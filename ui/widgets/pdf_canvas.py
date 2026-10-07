"""
PdfCanvas — a fast, annotation-capable PDF page view built on PyMuPDF.

* Continuous or single-page layout, zoom (custom / fit width / fit page)
* Lazy, visible-first rendering with an LRU pixmap cache; very high zoom levels
  render a sharp clip of the visible area on top of a lower-resolution base.
* Tools: hand, text select, highlight / underline / strikeout, sticky note,
  free-hand ink, eraser, text box. Every change is a standard PDF annotation.
"""
from __future__ import annotations

from collections import OrderedDict

import fitz
from PySide6.QtCore import QPoint, QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import (QColor, QCursor, QGuiApplication, QImage, QKeySequence,
                           QPainter, QPainterPath, QPen, QPixmap)
from PySide6.QtWidgets import (QAbstractScrollArea, QInputDialog, QMenu,
                               QMessageBox, QToolTip)

from core import pdf_annotations as pa
from core.utils.i18n import t

MARGIN = 16
SPACING = 14
MIN_ZOOM, MAX_ZOOM = 0.1, 8.0
BASE_MAX_PIXELS = 9_000_000        # above this a page gets a hi-res clip overlay
CACHE_MAX_PIXELS = 70_000_000      # ~280 MB of 32-bit pixmaps

BG_COLOR = QColor("#D9D2C5")
SELECTION_COLOR = QColor(51, 136, 255, 70)
SEARCH_COLOR = QColor(255, 214, 0, 90)
SEARCH_CURRENT_COLOR = QColor(255, 120, 0, 130)
FLASH_COLOR = QColor(201, 100, 66)

TOOLS = ("hand", "select", "highlight", "underline", "strikeout", "note", "text", "ink", "eraser")
MARKUP_TOOLS = ("highlight", "underline", "strikeout")
TEXT_TOOLS = ("select",) + MARKUP_TOOLS
EDITABLE_TYPES = {fitz.PDF_ANNOT_TEXT, fitz.PDF_ANNOT_FREE_TEXT} | pa.MARKUP_TYPES


def _qcolor(rgb) -> QColor:
    return QColor.fromRgbF(*rgb) if rgb else QColor(0, 0, 0)


class PdfCanvas(QAbstractScrollArea):
    currentPageChanged = Signal(int)
    zoomChanged = Signal(float)
    documentModified = Signal()          # an annotation was added/edited/removed
    selectionChanged = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PdfCanvas")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.viewport().setMouseTracking(True)
        self.verticalScrollBar().setSingleStep(48)
        self.horizontalScrollBar().setSingleStep(48)
        self.verticalScrollBar().valueChanged.connect(self._on_scrolled)
        self.horizontalScrollBar().valueChanged.connect(self._on_scrolled)

        self.doc: fitz.Document | None = None
        self._sizes: list[tuple[float, float]] = []      # display size in points
        self._rects: dict[int, QRectF] = {}              # page -> canvas rect
        self._content_w = self._content_h = 0.0
        self._zoom = 1.0
        self._fit_mode: str | None = "width"
        self._continuous = True
        self._current = 0
        self._dpi_scale = self.logicalDpiX() / 72.0

        # rendering
        self._cache: OrderedDict[int, tuple[float, QPixmap]] = OrderedDict()
        self._clips: dict[int, tuple[float, QRectF, QPixmap]] = {}
        self._pending: list[int] = []
        self._render_timer = QTimer(self, interval=0, singleShot=True)
        self._render_timer.timeout.connect(self._process_render_queue)
        self._clip_timer = QTimer(self, interval=120, singleShot=True)
        self._clip_timer.timeout.connect(self._schedule_render)
        self._relayout_timer = QTimer(self, interval=0, singleShot=True)
        self._relayout_timer.timeout.connect(self._apply_fit)

        # interaction
        self.tool = "hand"
        self.tool_colors = {
            "highlight": pa.COLORS["yellow"], "underline": pa.COLORS["blue"],
            "strikeout": pa.COLORS["red"], "note": pa.COLORS["yellow"],
            "text": pa.COLORS["black"], "ink": pa.COLORS["red"],
        }
        self.ink_width = 2.0
        self._words: dict[int, list[pa.Word]] = {}
        self._sel_page = -1
        self._sel_anchor: fitz.Point | None = None
        self._sel_words: list[pa.Word] = []
        self._drag_origin: QPoint | None = None
        self._drag_scroll = (0, 0)
        self._ink_page = -1
        self._ink_points: list[fitz.Point] = []
        self._pressed = False
        self._undo: list[tuple[int, int]] = []           # (page, xref)
        self._hover_xref = None

        # overlays
        self._search_hits: dict[int, list[fitz.Rect]] = {}
        self._search_current: tuple[int, int] | None = None
        self._flash: tuple[int, fitz.Rect] | None = None
        self._flash_timer = QTimer(self, interval=1400, singleShot=True)
        self._flash_timer.timeout.connect(self._clear_flash)
        self._update_cursor()

    # ================================================================ document
    def set_document(self, doc: fitz.Document | None, keep_view: bool = False):
        page, scroll = self._current, self.verticalScrollBar().value()
        self.doc = doc
        self._cache.clear(); self._clips.clear(); self._pending.clear()
        self._words.clear(); self._undo.clear()
        self.clear_selection()
        self._search_hits.clear(); self._search_current = None
        self._sizes = []
        if doc is not None:
            for i in range(doc.page_count):
                r = doc[i].rect
                self._sizes.append((max(r.width, 1.0), max(r.height, 1.0)))
        if not keep_view:
            self._current = 0
        else:
            self._current = min(page, max(0, self.page_count() - 1))
        self._apply_fit(force=True)
        if keep_view:
            self.verticalScrollBar().setValue(scroll)
        self.viewport().update()

    def page_count(self) -> int:
        return len(self._sizes)

    def current_page(self) -> int:
        return self._current

    def invalidate_page(self, page: int):
        self._cache.pop(page, None)
        self._clips.pop(page, None)
        self._schedule_render()
        self.viewport().update()

    def invalidate_all(self):
        self._cache.clear(); self._clips.clear()
        self._schedule_render(); self.viewport().update()

    # ================================================================== layout
    def scale(self) -> float:
        return self._zoom * self._dpi_scale

    def zoom(self) -> float:
        return self._zoom

    def fit_mode(self) -> str | None:
        return self._fit_mode

    def is_continuous(self) -> bool:
        return self._continuous

    def set_continuous(self, on: bool):
        if on == self._continuous:
            return
        page = self._current
        self._continuous = on
        self._relayout()
        self.go_to_page(page)

    def set_fit_mode(self, mode: str | None):
        self._fit_mode = mode
        self._apply_fit(force=True)

    def set_zoom(self, zoom: float, anchor: QPoint | None = None):
        zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom))
        self._fit_mode = None
        self._set_zoom_internal(zoom, anchor)

    def zoom_in(self):
        self.set_zoom(self._next_zoom(+1))

    def zoom_out(self):
        self.set_zoom(self._next_zoom(-1))

    _STEPS = [0.1, 0.25, 0.33, 0.5, 0.67, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75,
              2.0, 2.5, 3.0, 4.0, 5.0, 6.4, 8.0]

    def _next_zoom(self, direction: int) -> float:
        z = self._zoom
        if direction > 0:
            return next((s for s in self._STEPS if s > z + 1e-3), MAX_ZOOM)
        return next((s for s in reversed(self._STEPS) if s < z - 1e-3), MIN_ZOOM)

    def _set_zoom_internal(self, zoom: float, anchor: QPoint | None = None):
        if self.doc is None:
            self._zoom = zoom
            return
        if anchor is None:
            anchor = QPoint(self.viewport().width() // 2, self.viewport().height() // 3)
        hit = self._hit(anchor, clamp=True)
        self._zoom = zoom
        self._relayout()
        if hit is not None:
            page, pt = hit
            r = self._rects.get(page)
            if r is not None:
                s = self.scale()
                self.horizontalScrollBar().setValue(int(r.x() + pt.x * s - anchor.x()))
                self.verticalScrollBar().setValue(int(r.y() + pt.y * s - anchor.y()))
        self._clips.clear()
        self._schedule_render()
        self.viewport().update()
        self.zoomChanged.emit(self._zoom)

    def _apply_fit(self, force: bool = False):
        if self.doc is None or not self._sizes:
            self._relayout(); return
        if self._fit_mode:
            w, h = self._sizes[self._current]
            if self._continuous:
                w = max(sw for sw, _ in self._sizes[max(0, self._current - 3):self._current + 4])
            vw = max(50, self.viewport().width() - 2 * MARGIN)
            vh = max(50, self.viewport().height() - 2 * MARGIN)
            z = vw / (w * self._dpi_scale)
            if self._fit_mode == "page":
                z = min(z, vh / (h * self._dpi_scale))
            z = max(MIN_ZOOM, min(MAX_ZOOM, z))
            if force or abs(z - self._zoom) > 1e-3:
                page = self._current
                offset = self._page_offset_ratio()
                self._zoom = z
                self._relayout()
                self._restore_page_offset(page, offset)
                self._clips.clear()
                self.zoomChanged.emit(self._zoom)
                self._schedule_render()
                self.viewport().update()
                return
        self._relayout()

    def _page_offset_ratio(self) -> float:
        r = self._rects.get(self._current)
        if r is None or r.height() <= 0:
            return 0.0
        return (self.verticalScrollBar().value() - r.y()) / r.height()

    def _restore_page_offset(self, page: int, ratio: float):
        r = self._rects.get(page)
        if r is not None:
            self.verticalScrollBar().setValue(int(r.y() + ratio * r.height()))

    def _relayout(self):
        self._rects = {}
        if self.doc is None or not self._sizes:
            self._content_w = self._content_h = 0
            self._update_scrollbars()
            return
        s = self.scale()
        pages = range(len(self._sizes)) if self._continuous else [self._current]
        y = MARGIN
        maxw = 0.0
        tmp = []
        for p in pages:
            w, h = self._sizes[p]
            pw, ph = w * s, h * s
            tmp.append((p, y, pw, ph))
            y += ph + SPACING
            maxw = max(maxw, pw)
        self._content_w = maxw + 2 * MARGIN
        self._content_h = y - SPACING + MARGIN
        avail_w = max(self._content_w, self.viewport().width())
        for p, py, pw, ph in tmp:
            self._rects[p] = QRectF((avail_w - pw) / 2.0, py, pw, ph)
        self._update_scrollbars()

    def _update_scrollbars(self):
        vw, vh = self.viewport().width(), self.viewport().height()
        hb, vb = self.horizontalScrollBar(), self.verticalScrollBar()
        hb.setRange(0, max(0, int(self._content_w - vw)))
        hb.setPageStep(vw)
        vb.setRange(0, max(0, int(self._content_h - vh)))
        vb.setPageStep(vh)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._fit_mode:
            self._relayout_timer.start()
        else:
            self._relayout()
        self._schedule_render()

    # ============================================================== navigation
    def go_to_page(self, page: int, y_points: float | None = None):
        if not self._sizes:
            return
        page = max(0, min(page, len(self._sizes) - 1))
        if not self._continuous and page != self._current:
            self._current = page
            self._relayout()
        r = self._rects.get(page)
        if r is None:
            return
        y = r.y() - MARGIN / 2 if y_points is None else r.y() + y_points * self.scale() - 60
        self.verticalScrollBar().setValue(int(y))
        if y_points is None:
            self.horizontalScrollBar().setValue(int(r.x() - MARGIN))
        self._set_current(page)
        self._schedule_render()
        self.viewport().update()

    def next_page(self):
        self.go_to_page(self._current + 1)

    def prev_page(self):
        self.go_to_page(self._current - 1)

    def scroll_to_rect(self, page: int, rect: fitz.Rect):
        """Scrolls so that a page-space rectangle is visible."""
        if self.doc is None:
            return
        if not self._continuous and page != self._current:
            self._current = page
            self._relayout()
        r = self._canvas_rect(page, rect)
        if r is None:
            return
        vb, hb = self.verticalScrollBar(), self.horizontalScrollBar()
        vw, vh = self.viewport().width(), self.viewport().height()
        if r.top() < vb.value() + 40 or r.bottom() > vb.value() + vh - 40:
            vb.setValue(int(r.center().y() - vh / 3))
        if r.left() < hb.value() or r.right() > hb.value() + vw:
            hb.setValue(int(r.center().x() - vw / 2))
        self._set_current(page)
        self.viewport().update()

    def flash_rect(self, page: int, rect: fitz.Rect):
        self._flash = (page, fitz.Rect(rect))
        self.scroll_to_rect(page, rect)
        self._flash_timer.start()
        self.viewport().update()

    def _clear_flash(self):
        self._flash = None
        self.viewport().update()

    def _set_current(self, page: int):
        if page != self._current:
            self._current = page
            self.currentPageChanged.emit(page)

    def _on_scrolled(self, *_):
        if self._continuous and self._rects:
            vb = self.verticalScrollBar().value()
            probe = vb + self.viewport().height() * 0.35
            page = self._page_at_y(probe)
            if page is not None:
                self._set_current(page)
        self._schedule_render()
        if self._clips or self.scale() > 0:
            self._clip_timer.start()
        self.viewport().update()

    def _page_at_y(self, y: float):
        # binary search over continuous layout
        keys = list(self._rects.keys())
        lo, hi = 0, len(keys) - 1
        best = keys[0] if keys else None
        while lo <= hi:
            mid = (lo + hi) // 2
            r = self._rects[keys[mid]]
            if y < r.top():
                hi = mid - 1
            else:
                best = keys[mid]
                if y <= r.bottom() + SPACING:
                    return best
                lo = mid + 1
        return best

    def _visible_pages(self) -> list[int]:
        top = self.verticalScrollBar().value()
        bottom = top + self.viewport().height()
        if not self._continuous:
            return list(self._rects.keys())
        first = self._page_at_y(top)
        if first is None:
            return []
        result = []
        for p in range(first, len(self._sizes)):
            r = self._rects.get(p)
            if r is None or r.top() > bottom:
                break
            if r.bottom() >= top:
                result.append(p)
        return result

    # ============================================================== rendering
    def _schedule_render(self):
        if self.doc is not None and not self._render_timer.isActive():
            self._render_timer.start()

    def _process_render_queue(self):
        if self.doc is None:
            return
        s = self.scale()
        dpr = self.devicePixelRatioF()
        visible = self._visible_pages()
        # neighbours are pre-rendered so scrolling feels instant
        wanted = visible + [p for p in (visible[-1] + 1, visible[0] - 1) if 0 <= p < len(self._sizes)] \
            if visible else []
        for p in wanted:
            base_scale = self._base_scale(p, s, dpr)
            entry = self._cache.get(p)
            if entry is None or abs(entry[0] - base_scale) > 1e-4:
                self._render_base(p, base_scale, dpr)
                self.viewport().update()
                self._render_timer.start()
                return
        # hi-res clip overlays for very large zooms
        for p in visible:
            if self._base_scale(p, s, dpr) < s - 1e-4:
                if self._render_clip(p, s, dpr):
                    self.viewport().update()
                    self._render_timer.start()
                    return

    def _base_scale(self, page: int, s: float, dpr: float) -> float:
        w, h = self._sizes[page]
        px = w * h * (s * dpr) ** 2
        if px <= BASE_MAX_PIXELS:
            return s
        return s * (BASE_MAX_PIXELS / px) ** 0.5

    def _pix_to_qpixmap(self, pix: fitz.Pixmap, dpr: float) -> QPixmap:
        fmt = QImage.Format.Format_RGB888 if pix.n == 3 else QImage.Format.Format_RGBA8888
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt).copy()
        qpm = QPixmap.fromImage(img)
        qpm.setDevicePixelRatio(dpr)
        return qpm

    def _render_base(self, page: int, scale: float, dpr: float):
        try:
            f = scale * dpr
            pix = self.doc[page].get_pixmap(matrix=fitz.Matrix(f, f), annots=True, alpha=False)
            qpm = self._pix_to_qpixmap(pix, dpr)
        except Exception:
            qpm = QPixmap()
        self._cache[page] = (scale, qpm)
        self._cache.move_to_end(page)
        total = sum(pm.width() * pm.height() for _, pm in self._cache.values())
        visible = set(self._visible_pages())
        while total > CACHE_MAX_PIXELS and len(self._cache) > 1:
            victim = next((k for k in self._cache if k not in visible), None)
            if victim is None:
                break
            _, pm = self._cache.pop(victim)
            total -= pm.width() * pm.height()

    def _render_clip(self, page: int, s: float, dpr: float) -> bool:
        r = self._rects.get(page)
        if r is None:
            return False
        vis = QRectF(self.horizontalScrollBar().value(), self.verticalScrollBar().value(),
                     self.viewport().width(), self.viewport().height()).intersected(r)
        if vis.isEmpty():
            return False
        # region in display points, padded by half a viewport
        pad_w, pad_h = vis.width() * 0.5, vis.height() * 0.5
        want = vis.adjusted(-pad_w, -pad_h, pad_w, pad_h).intersected(r)
        existing = self._clips.get(page)
        if existing and abs(existing[0] - s) < 1e-4 and existing[1].contains(vis):
            return False
        local = want.translated(-r.x(), -r.y())
        clip = fitz.Rect(local.left() / s, local.top() / s, local.right() / s, local.bottom() / s)
        try:
            f = s * dpr
            pix = self.doc[page].get_pixmap(matrix=fitz.Matrix(f, f), clip=clip,
                                            annots=True, alpha=False)
            self._clips[page] = (s, want, self._pix_to_qpixmap(pix, dpr))
        except Exception:
            return False
        return True

    def render_thumbnail(self, page: int, width: int) -> QPixmap:
        dpr = self.devicePixelRatioF()
        w, _ = self._sizes[page]
        f = width / w * dpr
        pix = self.doc[page].get_pixmap(matrix=fitz.Matrix(f, f), annots=True, alpha=False)
        return self._pix_to_qpixmap(pix, dpr)

    # ================================================================ painting
    def _canvas_rect(self, page: int, rect: fitz.Rect) -> QRectF | None:
        """page-space rect -> canvas rect (content coordinates)."""
        r = self._rects.get(page)
        if r is None or self.doc is None:
            return None
        d = pa.to_display_space(self.doc[page], rect)
        s = self.scale()
        return QRectF(r.x() + d.x0 * s, r.y() + d.y0 * s, d.width * s, d.height * s)

    def paintEvent(self, event):
        p = QPainter(self.viewport())
        p.fillRect(self.viewport().rect(), BG_COLOR)
        if self.doc is None:
            return
        ox, oy = self.horizontalScrollBar().value(), self.verticalScrollBar().value()
        p.translate(-ox, -oy)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        needs_render = False
        s = self.scale()
        for page in self._visible_pages():
            r = self._rects[page]
            # shadow + paper
            p.fillRect(r.translated(2, 3), QColor(0, 0, 0, 40))
            p.fillRect(r, Qt.GlobalColor.white)
            entry = self._cache.get(page)
            if entry is not None and not entry[1].isNull():
                p.drawPixmap(r, entry[1], QRectF(entry[1].rect()))
                if abs(entry[0] - self._base_scale(page, s, self.devicePixelRatioF())) > 1e-4:
                    needs_render = True
            else:
                needs_render = True
            clip = self._clips.get(page)
            if clip is not None and abs(clip[0] - s) < 1e-4:
                p.drawPixmap(clip[1], clip[2], QRectF(clip[2].rect()))
            self._paint_overlays(p, page)
        if needs_render:
            self._schedule_render()

    def _paint_overlays(self, p: QPainter, page: int):
        p.setPen(Qt.PenStyle.NoPen)
        hits = self._search_hits.get(page)
        if hits:
            for i, rect in enumerate(hits):
                cr = self._canvas_rect(page, rect)
                cur = self._search_current == (page, i)
                p.fillRect(cr, SEARCH_CURRENT_COLOR if cur else SEARCH_COLOR)
        if page == self._sel_page and self._sel_words:
            color = SELECTION_COLOR
            if self.tool in MARKUP_TOOLS and self._pressed:
                color = _qcolor(self.tool_colors[self.tool]); color.setAlpha(110)
            for rect in pa.line_rects(self._sel_words):
                p.fillRect(self._canvas_rect(page, rect), color)
        if page == self._ink_page and len(self._ink_points) > 1:
            path = QPainterPath()
            for i, pt in enumerate(self._ink_points):
                d = pa.to_display_space(self.doc[page], pt)
                r = self._rects[page]
                q = QPointF(r.x() + d.x * self.scale(), r.y() + d.y * self.scale())
                path.moveTo(q) if i == 0 else path.lineTo(q)
            pen = QPen(_qcolor(self.tool_colors["ink"]), max(1.0, self.ink_width * self.scale()))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap); pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            p.strokePath(path, pen)
        if self._flash and self._flash[0] == page:
            cr = self._canvas_rect(page, self._flash[1])
            if cr is not None:
                pen = QPen(FLASH_COLOR, 3); p.setPen(pen)
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawRoundedRect(cr.adjusted(-4, -4, 4, 4), 4, 4)
                p.setPen(Qt.PenStyle.NoPen)

    # =========================================================== hit testing
    def _hit(self, pos: QPoint, clamp: bool = False, page_hint: int | None = None):
        """viewport pos -> (page, display-space point in points)."""
        if self.doc is None:
            return None
        cx = pos.x() + self.horizontalScrollBar().value()
        cy = pos.y() + self.verticalScrollBar().value()
        s = self.scale()
        candidates = [page_hint] if page_hint is not None else self._visible_pages()
        for page in candidates:
            r = self._rects.get(page)
            if r is None:
                continue
            inside = r.contains(QPointF(cx, cy))
            if inside or clamp or page_hint is not None:
                x = min(max(cx, r.left()), r.right())
                y = min(max(cy, r.top()), r.bottom())
                if inside or page_hint is not None or (clamp and r.top() - SPACING <= cy <= r.bottom() + SPACING):
                    return page, fitz.Point((x - r.x()) / s, (y - r.y()) / s)
        if clamp and candidates:
            page = candidates[0]
            r = self._rects[page]
            return page, fitz.Point(0, max(0.0, (cy - r.y()) / s))
        return None

    def _page_point(self, pos: QPoint, page_hint: int | None = None):
        """viewport pos -> (page, page-space point)."""
        hit = self._hit(pos, page_hint=page_hint)
        if hit is None:
            return None
        page, dpt = hit
        return page, pa.to_page_space(self.doc[page], dpt)

    def _annot_at(self, pos: QPoint):
        hit = self._page_point(pos)
        if hit is None:
            return None
        page, pt = hit
        annot = pa.annot_at(self.doc[page], pt)
        return (page, annot) if annot is not None else None

    # ================================================================== tools
    def set_tool(self, tool: str):
        if tool not in TOOLS:
            return
        self.tool = tool
        if tool not in TEXT_TOOLS:
            self.clear_selection()
        self._update_cursor()

    def set_tool_color(self, rgb):
        if self.tool in self.tool_colors:
            self.tool_colors[self.tool] = rgb

    def _update_cursor(self):
        shapes = {
            "hand": Qt.CursorShape.OpenHandCursor, "select": Qt.CursorShape.IBeamCursor,
            "highlight": Qt.CursorShape.IBeamCursor, "underline": Qt.CursorShape.IBeamCursor,
            "strikeout": Qt.CursorShape.IBeamCursor, "note": Qt.CursorShape.PointingHandCursor,
            "text": Qt.CursorShape.CrossCursor, "ink": Qt.CursorShape.CrossCursor,
            "eraser": Qt.CursorShape.ForbiddenCursor,
        }
        self.viewport().setCursor(QCursor(shapes.get(self.tool, Qt.CursorShape.ArrowCursor)))

    def _words_for(self, page: int) -> list[pa.Word]:
        if page not in self._words:
            self._words[page] = pa.page_words(self.doc[page])
        return self._words[page]

    def has_selection(self) -> bool:
        return bool(self._sel_words)

    def selected_text(self) -> str:
        return pa.words_text(self._sel_words)

    def clear_selection(self):
        had = bool(self._sel_words)
        self._sel_words = []
        self._sel_page = -1
        self._sel_anchor = None
        if had:
            self.selectionChanged.emit(False)
            self.viewport().update()

    def copy_selection(self) -> bool:
        text = self.selected_text()
        if text:
            QGuiApplication.clipboard().setText(text)
            return True
        return False

    def _mark(self, page: int, pt: fitz.Point):
        """Remember a newly created annotation for undo + notify."""
        self._undo.append((page, pt))
        self.invalidate_page(page)
        self.documentModified.emit()

    def markup_selection(self, kind: str):
        if not self._sel_words or self._sel_page < 0:
            return
        page = self._sel_page
        color = self.tool_colors.get(kind, pa.COLORS["yellow"])
        annot = pa.add_text_markup(self.doc[page], kind, pa.line_rects(self._sel_words), color)
        self.clear_selection()
        if annot is not None:
            self._mark(page, annot.xref)

    def undo(self) -> bool:
        while self._undo:
            page, xref = self._undo.pop()
            if pa.delete_annot(self.doc[page], xref):
                self.invalidate_page(page)
                self.documentModified.emit()
                return True
        return False

    def can_undo(self) -> bool:
        return bool(self._undo)

    # ------------------------------------------------------------- dialogs
    def _ask_text(self, title: str, label: str, text: str = "") -> str | None:
        value, ok = QInputDialog.getMultiLineText(self, title, label, text)
        if not ok:
            return None
        value = value.strip()
        return value or None

    def _add_note(self, page: int, pt: fitz.Point):
        text = self._ask_text(t("viewer_note_title"), t("viewer_note_prompt"))
        if text is None:
            return
        annot = pa.add_sticky_note(self.doc[page], pt, text, self.tool_colors["note"])
        self._mark(page, annot.xref)

    def _add_text_box(self, page: int, pt: fitz.Point):
        text = self._ask_text(t("viewer_textbox_title"), t("viewer_textbox_prompt"))
        if text is None:
            return
        annot = pa.add_text_box(self.doc[page], pt, text, 12, self.tool_colors["text"])
        self._mark(page, annot.xref)

    def edit_annotation(self, page: int, xref: int):
        annot = pa.find_annot(self.doc[page], xref)
        if annot is None:
            return
        current = (annot.info or {}).get("content", "") or ""
        text, ok = QInputDialog.getMultiLineText(self, t("viewer_edit_annot"),
                                                 t("viewer_note_prompt"), current)
        if not ok or text == current:
            return
        if annot.type[0] == fitz.PDF_ANNOT_FREE_TEXT and not text.strip():
            return
        pa.set_annot_content(self.doc[page], xref, text)
        self.invalidate_page(page)
        self.documentModified.emit()

    def delete_annotation(self, page: int, xref: int):
        if pa.delete_annot(self.doc[page], xref):
            self.invalidate_page(page)
            self.documentModified.emit()

    def recolor_annotation(self, page: int, xref: int, rgb):
        annot = pa.find_annot(self.doc[page], xref)
        if annot is None:
            return
        if annot.type[0] == fitz.PDF_ANNOT_FREE_TEXT:
            annot.update(fontname="helv", text_color=rgb)
        else:
            annot.set_colors(stroke=rgb)
            annot.update()
        self.invalidate_page(page)
        self.documentModified.emit()

    # ================================================================== mouse
    def mousePressEvent(self, ev):
        if self.doc is None:
            return
        self.setFocus()
        if ev.button() == Qt.MouseButton.MiddleButton or (
                ev.button() == Qt.MouseButton.LeftButton and self.tool == "hand"):
            self._start_drag(ev)
            return
        if ev.button() != Qt.MouseButton.LeftButton:
            return
        hit = self._page_point(ev.position().toPoint())
        if hit is None:
            self.clear_selection()
            return
        page, pt = hit
        self._pressed = True
        if self.tool in TEXT_TOOLS:
            self.clear_selection()
            self._sel_page = page
            self._sel_anchor = pt
        elif self.tool == "ink":
            self._ink_page = page
            self._ink_points = [pt]
        elif self.tool == "eraser":
            self._erase_at(ev.position().toPoint())
        elif self.tool == "note":
            self._pressed = False
            self._add_note(page, pt)
        elif self.tool == "text":
            self._pressed = False
            self._add_text_box(page, pt)

    def _start_drag(self, ev):
        self._drag_origin = ev.position().toPoint()
        self._drag_scroll = (self.horizontalScrollBar().value(), self.verticalScrollBar().value())
        self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, ev):
        pos = ev.position().toPoint()
        if self._drag_origin is not None:
            d = pos - self._drag_origin
            self.horizontalScrollBar().setValue(self._drag_scroll[0] - d.x())
            self.verticalScrollBar().setValue(self._drag_scroll[1] - d.y())
            return
        if self._pressed and self.tool in TEXT_TOOLS and self._sel_anchor is not None:
            self._autoscroll(pos)
            hit = self._page_point(pos, page_hint=self._sel_page)
            if hit:
                words = self._words_for(self._sel_page)
                self._sel_words = pa.select_words(words, self._sel_anchor, hit[1])
                self.viewport().update()
            return
        if self._pressed and self.tool == "ink" and self._ink_page >= 0:
            hit = self._page_point(pos, page_hint=self._ink_page)
            if hit:
                self._ink_points.append(hit[1])
                self.viewport().update()
            return
        if self._pressed and self.tool == "eraser":
            self._erase_at(pos)
            return
        self._update_hover(pos, ev.globalPosition().toPoint())

    def _autoscroll(self, pos: QPoint):
        vb = self.verticalScrollBar()
        if pos.y() < 10:
            vb.setValue(vb.value() - 20)
        elif pos.y() > self.viewport().height() - 10:
            vb.setValue(vb.value() + 20)

    def mouseReleaseEvent(self, ev):
        if self._drag_origin is not None:
            self._drag_origin = None
            self._update_cursor()
            return
        if not self._pressed:
            return
        self._pressed = False
        if self.tool in TEXT_TOOLS:
            if self._sel_words:
                if self.tool in MARKUP_TOOLS:
                    self.markup_selection(self.tool)
                else:
                    self.selectionChanged.emit(True)
            self.viewport().update()
        elif self.tool == "ink" and self._ink_page >= 0:
            page, pts = self._ink_page, self._ink_points
            self._ink_page, self._ink_points = -1, []
            if len(pts) >= 2:
                annot = pa.add_ink(self.doc[page], [pts], self.tool_colors["ink"], self.ink_width)
                if annot is not None:
                    self._mark(page, annot.xref)
            self.viewport().update()

    def mouseDoubleClickEvent(self, ev):
        if ev.button() != Qt.MouseButton.LeftButton or self.doc is None:
            return
        pos = ev.position().toPoint()
        found = self._annot_at(pos)
        if found and found[1].type[0] in EDITABLE_TYPES and self.tool not in ("ink", "eraser"):
            self.edit_annotation(found[0], found[1].xref)
            return
        if self.tool in TEXT_TOOLS:     # select a single word
            hit = self._page_point(pos)
            if hit:
                page, pt = hit
                words = pa.select_words(self._words_for(page), pt, pt)
                self._sel_page, self._sel_words = page, words
                self.selectionChanged.emit(bool(words))
                self.viewport().update()

    def _erase_at(self, pos: QPoint):
        found = self._annot_at(pos)
        if found:
            self.delete_annotation(found[0], found[1].xref)

    def _update_hover(self, pos: QPoint, global_pos: QPoint):
        if self.tool in ("ink",):
            return
        found = self._annot_at(pos)
        xref = found[1].xref if found else None
        if xref != self._hover_xref:
            self._hover_xref = xref
            if found:
                info = found[1].info or {}
                content = (info.get("content") or "").strip()
                author = (info.get("title") or "").strip()
                tip = content if not author else f"<b>{author}</b><br>{content}" if content else author
                if tip:
                    QToolTip.showText(global_pos, tip.replace("\n", "<br>"), self.viewport())
                if self.tool in ("hand", "select"):
                    self.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
            else:
                QToolTip.hideText()
                self._update_cursor()

    def wheelEvent(self, ev):
        if ev.modifiers() & Qt.KeyboardModifier.ControlModifier:
            dy = ev.angleDelta().y()
            if dy:
                factor = 1.15 if dy > 0 else 1 / 1.15
                self.set_zoom(self._zoom * factor, ev.position().toPoint())
            return
        if not self._continuous:
            vb = self.verticalScrollBar()
            dy = ev.angleDelta().y()
            if dy < 0 and vb.value() >= vb.maximum() and self._current < self.page_count() - 1:
                self.go_to_page(self._current + 1)
                return
            if dy > 0 and vb.value() <= vb.minimum() and self._current > 0:
                self.go_to_page(self._current - 1)
                vb.setValue(vb.maximum())
                return
        super().wheelEvent(ev)

    def contextMenuEvent(self, ev):
        if self.doc is None:
            return
        menu = QMenu(self)
        found = self._annot_at(ev.pos())
        if found:
            page, annot = found
            xref, tid = annot.xref, annot.type[0]
            if tid in EDITABLE_TYPES:
                menu.addAction(t("viewer_edit_annot"), lambda: self.edit_annotation(page, xref))
            colors = menu.addMenu(t("viewer_change_color"))
            for name, rgb in pa.COLORS.items():
                colors.addAction(self._swatch_icon(rgb), t(f"viewer_color_{name}"),
                                 lambda r=rgb: self.recolor_annotation(page, xref, r))
            menu.addSeparator()
            menu.addAction(t("viewer_delete_annot"), lambda: self.delete_annotation(page, xref))
        elif self._sel_words:
            menu.addAction(t("viewer_copy"), self.copy_selection)
            menu.addSeparator()
            menu.addAction(t("viewer_tool_highlight"), lambda: self.markup_selection("highlight"))
            menu.addAction(t("viewer_tool_underline"), lambda: self.markup_selection("underline"))
            menu.addAction(t("viewer_tool_strikeout"), lambda: self.markup_selection("strikeout"))
        else:
            hit = self._page_point(ev.pos())
            if hit is None:
                return
            page, pt = hit
            menu.addAction(t("viewer_tool_note"), lambda: self._add_note(page, pt))
            menu.addAction(t("viewer_tool_text"), lambda: self._add_text_box(page, pt))
        menu.exec(ev.globalPos())

    @staticmethod
    def _swatch_icon(rgb):
        from PySide6.QtGui import QIcon
        pm = QPixmap(14, 14)
        pm.fill(_qcolor(rgb))
        return QIcon(pm)

    # =============================================================== keyboard
    def keyPressEvent(self, ev):
        if ev.matches(QKeySequence.StandardKey.Copy):
            self.copy_selection()
            return
        key = ev.key()
        no_hscroll = self.horizontalScrollBar().maximum() == 0
        if key == Qt.Key.Key_Right and no_hscroll:
            self.next_page(); return
        if key == Qt.Key.Key_Left and no_hscroll:
            self.prev_page(); return
        if key == Qt.Key.Key_Home:
            self.go_to_page(0); return
        if key == Qt.Key.Key_End:
            self.go_to_page(self.page_count() - 1); return
        if not self._continuous and key in (Qt.Key.Key_PageDown, Qt.Key.Key_Space):
            vb = self.verticalScrollBar()
            if vb.value() >= vb.maximum():
                self.next_page(); return
        if not self._continuous and key == Qt.Key.Key_PageUp:
            vb = self.verticalScrollBar()
            if vb.value() <= vb.minimum():
                self.prev_page(); vb.setValue(vb.maximum()); return
        if key == Qt.Key.Key_Space and self._continuous:
            vb = self.verticalScrollBar(); vb.setValue(vb.value() + vb.pageStep() - 40); return
        super().keyPressEvent(ev)

    # ================================================================= search
    def set_search_results(self, hits: dict[int, list[fitz.Rect]], current=None):
        self._search_hits = hits
        self._search_current = current
        self.viewport().update()

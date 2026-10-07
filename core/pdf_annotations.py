"""
Annotation & text helpers for the built-in PDF viewer (pure PyMuPDF, no Qt).

Coordinate conventions
----------------------
* "page space"    : unrotated PDF coordinates (what get_text()/search_for() return
                    and what the add_*_annot() methods expect).
* "display space" : rotated, visible coordinates in points (what get_pixmap renders).

Use :func:`to_page_space` / :func:`to_display_space` to convert between them.
All annotations are written as *standard* PDF annotations, so they are visible
and editable in Acrobat, Edge, Chrome, Foxit, etc.
"""
from __future__ import annotations

import getpass
from dataclasses import dataclass

import fitz  # PyMuPDF

# Named colours (RGB 0..1) shared by the UI palette
COLORS: dict[str, tuple[float, float, float]] = {
    "yellow": (1.0, 0.89, 0.20),
    "green": (0.49, 0.87, 0.36),
    "pink": (1.0, 0.47, 0.71),
    "blue": (0.36, 0.71, 1.0),
    "red": (0.89, 0.18, 0.18),
    "black": (0.10, 0.10, 0.10),
}

MARKUP_TYPES = {
    fitz.PDF_ANNOT_HIGHLIGHT, fitz.PDF_ANNOT_UNDERLINE,
    fitz.PDF_ANNOT_STRIKE_OUT, fitz.PDF_ANNOT_SQUIGGLY,
}
# Annotation types we show in the side panel (skip links, widgets, popups...)
LISTED_TYPES = MARKUP_TYPES | {
    fitz.PDF_ANNOT_TEXT, fitz.PDF_ANNOT_FREE_TEXT, fitz.PDF_ANNOT_INK,
    fitz.PDF_ANNOT_SQUARE, fitz.PDF_ANNOT_CIRCLE, fitz.PDF_ANNOT_LINE,
    fitz.PDF_ANNOT_POLYGON, fitz.PDF_ANNOT_POLY_LINE, fitz.PDF_ANNOT_STAMP,
}


def author_name() -> str:
    try:
        return getpass.getuser()
    except Exception:
        return "Çevirgeç PDF"


# ----------------------------------------------------------------- coordinates
def to_page_space(page: fitz.Page, point: fitz.Point) -> fitz.Point:
    return fitz.Point(point) * page.derotation_matrix


def to_display_space(page: fitz.Page, obj):
    """Converts a Point/Rect from page space to display space."""
    if isinstance(obj, fitz.Rect):
        return fitz.Rect(obj) * page.rotation_matrix
    return fitz.Point(obj) * page.rotation_matrix


# ------------------------------------------------------------- text selection
@dataclass
class Word:
    rect: fitz.Rect
    text: str
    block: int
    line: int


def page_words(page: fitz.Page) -> list[Word]:
    """Words in natural reading order (page space)."""
    words = page.get_text("words", sort=False)
    return [Word(fitz.Rect(w[:4]), w[4], w[5], w[6]) for w in words]


def _nearest_word_index(words: list[Word], pt: fitz.Point) -> int:
    best, best_d = -1, None
    for i, w in enumerate(words):
        r = w.rect
        if r.contains(pt):
            return i
        dx = max(r.x0 - pt.x, 0, pt.x - r.x1)
        dy = max(r.y0 - pt.y, 0, pt.y - r.y1)
        d = dx * dx + (dy * 3) ** 2          # prefer same line
        if best_d is None or d < best_d:
            best, best_d = i, d
    return best


def select_words(words: list[Word], start: fitz.Point, end: fitz.Point) -> list[Word]:
    """Words between two page-space points, in reading order (like a text cursor)."""
    if not words:
        return []
    a = _nearest_word_index(words, start)
    b = _nearest_word_index(words, end)
    if a < 0 or b < 0:
        return []
    if a > b:
        a, b = b, a
    return words[a:b + 1]


def words_text(words: list[Word]) -> str:
    out, prev = [], None
    for w in words:
        key = (w.block, w.line)
        if prev is not None:
            out.append("\n" if key != prev else " ")
        out.append(w.text)
        prev = key
    return "".join(out)


def line_rects(words: list[Word]) -> list[fitz.Rect]:
    """Merges selected words into one rectangle per text line."""
    rects: list[fitz.Rect] = []
    prev = None
    for w in words:
        key = (w.block, w.line)
        if key == prev and rects:
            rects[-1] |= w.rect
        else:
            rects.append(fitz.Rect(w.rect))
        prev = key
    return rects


# --------------------------------------------------------------- annotations
def _finish(annot: fitz.Annot, color=None, content: str | None = None) -> fitz.Annot:
    info = {"title": author_name()}
    if content is not None:
        info["content"] = content
    annot.set_info(info)
    if color is not None:
        annot.set_colors(stroke=color)
    annot.update()
    return annot


def add_text_markup(page: fitz.Page, kind: str, rects: list[fitz.Rect],
                    color=COLORS["yellow"]) -> fitz.Annot | None:
    """kind: 'highlight' | 'underline' | 'strikeout'. rects in page space."""
    if not rects:
        return None
    quads = [fitz.Rect(r).quad for r in rects]
    if kind == "highlight":
        annot = page.add_highlight_annot(quads=quads)
    elif kind == "underline":
        annot = page.add_underline_annot(quads=quads)
    elif kind == "strikeout":
        annot = page.add_strikeout_annot(quads=quads)
    else:
        raise ValueError(kind)
    return _finish(annot, color)


def add_sticky_note(page: fitz.Page, point: fitz.Point, text: str,
                    color=COLORS["yellow"]) -> fitz.Annot:
    annot = page.add_text_annot(fitz.Point(point), text, icon="Comment")
    return _finish(annot, color, text)


def add_ink(page: fitz.Page, strokes: list[list[fitz.Point]], color=COLORS["red"],
            width: float = 2.0) -> fitz.Annot | None:
    strokes = [[(p.x, p.y) for p in s] for s in strokes if len(s) >= 2]
    if not strokes:
        return None
    annot = page.add_ink_annot(strokes)
    annot.set_border(width=width)
    return _finish(annot, color)


def add_text_box(page: fitz.Page, point: fitz.Point, text: str, fontsize: float = 12,
                 color=COLORS["black"]) -> fitz.Annot:
    """Free-text box whose size is estimated from the text (page space top-left)."""
    lines = text.splitlines() or [""]
    longest = max(fitz.get_text_length(l, fontname="helv", fontsize=fontsize) for l in lines)
    width = max(60.0, longest + fontsize)
    height = fontsize * 1.35 * len(lines) + fontsize * 0.8
    rect = fitz.Rect(point.x, point.y, point.x + width, point.y + height)
    annot = page.add_freetext_annot(rect, text, fontsize=fontsize, fontname="helv",
                                    text_color=color)
    annot.set_info({"title": author_name(), "content": text})
    annot.update(fontsize=fontsize, fontname="helv", text_color=color)
    return annot


def find_annot(page: fitz.Page, xref: int) -> fitz.Annot | None:
    for annot in page.annots() or []:
        if annot.xref == xref:
            return annot
    return None


def annot_at(page: fitz.Page, point: fitz.Point, tolerance: float = 3.0) -> fitz.Annot | None:
    """Top-most listed annotation under a page-space point."""
    hit = None
    for annot in page.annots() or []:
        if annot.type[0] not in LISTED_TYPES:
            continue
        r = fitz.Rect(annot.rect)
        r.x0 -= tolerance; r.y0 -= tolerance; r.x1 += tolerance; r.y1 += tolerance
        if not r.contains(point):
            continue
        if annot.type[0] in MARKUP_TYPES and annot.vertices:
            # Only count a hit when on one of the marked lines, not the gaps.
            v = annot.vertices
            quads = [fitz.Quad(v[i:i + 4]).rect for i in range(0, len(v) - 3, 4)]
            if quads and not any(q.contains(point) for q in quads):
                continue
        hit = annot  # later annotations are drawn on top
    return hit


def delete_annot(page: fitz.Page, xref: int) -> bool:
    annot = find_annot(page, xref)
    if annot is None:
        return False
    page.delete_annot(annot)
    return True


def set_annot_content(page: fitz.Page, xref: int, text: str) -> bool:
    annot = find_annot(page, xref)
    if annot is None:
        return False
    annot.set_info(content=text)
    if annot.type[0] == fitz.PDF_ANNOT_FREE_TEXT:
        annot.update(fontname="helv")
    else:
        annot.update()
    return True


@dataclass
class AnnotInfo:
    page: int
    xref: int
    type_id: int
    type_name: str
    content: str
    author: str
    rect: fitz.Rect          # page space
    color: tuple | None


def list_annotations(doc: fitz.Document) -> list[AnnotInfo]:
    result = []
    for pno in range(doc.page_count):
        page = doc[pno]
        for annot in page.annots() or []:
            tid, tname = annot.type[0], annot.type[1]
            if tid not in LISTED_TYPES:
                continue
            info = annot.info or {}
            content = info.get("content", "") or ""
            if tid in MARKUP_TYPES and not content:
                try:  # show the marked text itself
                    content = page.get_textbox(annot.rect).strip()
                except Exception:
                    content = ""
            stroke = (annot.colors or {}).get("stroke")
            result.append(AnnotInfo(pno, annot.xref, tid, tname, " ".join(content.split()),
                                    info.get("title", "") or "", fitz.Rect(annot.rect),
                                    tuple(stroke) if stroke else None))
    return result


# ---------------------------------------------------------------------- save
def save_document(doc: fitz.Document, target_path: str, password: str | None = None
                  ) -> tuple[fitz.Document, str]:
    """
    Saves *doc* to *target_path* and returns ``(document_to_keep_using, mode)``.

    * Same file + incremental possible -> ``saveIncr()`` (fast, keeps signatures
      and encryption intact); the same document object is returned.
    * Otherwise a full, compacted save is written (through a temp file when
      overwriting the original), the old document is closed and the saved file
      is reopened. NOTE: xrefs may change in that case.
    """
    import os
    target_path = os.path.abspath(target_path)
    same_file = bool(doc.name) and os.path.normcase(os.path.abspath(doc.name)) == \
        os.path.normcase(target_path)

    if same_file and doc.can_save_incrementally():
        doc.saveIncr()
        return doc, "incremental"

    kwargs = {"garbage": 3, "deflate": True}
    if (doc.metadata or {}).get("encryption"):
        kwargs["encryption"] = fitz.PDF_ENCRYPT_KEEP

    if same_file:
        tmp = target_path + ".cevirgec-tmp"
        doc.save(tmp, **kwargs)
        doc.close()
        os.replace(tmp, target_path)
    else:
        doc.save(target_path, **kwargs)
        doc.close()

    new_doc = fitz.open(target_path)
    if new_doc.needs_pass and password:
        new_doc.authenticate(password)
    return new_doc, "full"


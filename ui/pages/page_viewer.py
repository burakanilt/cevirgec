import os
import fitz
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QFileDialog, QMessageBox, QLabel, QSplitter,
                               QListWidget, QListWidgetItem, QToolBar, QToolButton, QInputDialog)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
import qtawesome as qta

from ui.widgets.pdf_canvas import PdfCanvas
from core import pdf_annotations as pa
from core.utils.i18n import t

class PageViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PageViewer")
        self.doc = None
        self.file_path = None
        self.password = None
        self.has_unsaved_changes = False

        self._setup_ui()
        self._setup_shortcuts()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toolbar
        self.toolbar = QToolBar(self)
        self.toolbar.setIconSize(QSize(20, 20))
        self.toolbar.setMovable(False)
        main_layout.addWidget(self.toolbar)

        # Build Toolbar Items
        self.btn_open = self._add_tool(self.toolbar, "fa5s.folder-open", "viewer_open_tip", self.open_file)
        self.btn_save = self._add_tool(self.toolbar, "fa5s.save", "viewer_save_tip", self.save_file)
        self.btn_save_as = self._add_tool(self.toolbar, "fa5s.file-download", "viewer_save_as_tip", self.save_file_as)
        self.toolbar.addSeparator()

        self.btn_zoom_out = self._add_tool(self.toolbar, "fa5s.search-minus", "viewer_zoom_out", lambda: self.canvas.zoom_out())
        self.lbl_zoom = QLabel(" 100% ")
        self.lbl_zoom.setMinimumWidth(50)
        self.lbl_zoom.setAlignment(Qt.AlignCenter)
        self.toolbar.addWidget(self.lbl_zoom)
        self.btn_zoom_in = self._add_tool(self.toolbar, "fa5s.search-plus", "viewer_zoom_in", lambda: self.canvas.zoom_in())
        self.btn_fit_width = self._add_tool(self.toolbar, "fa5s.arrows-alt-h", "viewer_zoom_fit_width", lambda: self.canvas.set_fit_mode("width"))
        self.btn_fit_page = self._add_tool(self.toolbar, "fa5s.expand", "viewer_zoom_fit_page", lambda: self.canvas.set_fit_mode("page"))
        self.toolbar.addSeparator()

        # Tools group
        self.tool_buttons = {}
        tools = [
            ("hand", "fa5s.hand-paper", "viewer_tool_select"),  # Using hand icon for select/hand combo or just hand
            ("select", "fa5s.i-cursor", "viewer_tool_select"),
            ("highlight", "fa5s.highlighter", "viewer_tool_highlight"),
            ("underline", "fa5s.underline", "viewer_tool_underline"),
            ("strikeout", "fa5s.strikethrough", "viewer_tool_strikeout"),
            ("ink", "fa5s.pen", "viewer_tool_ink"),
            ("text", "fa5s.font", "viewer_tool_freetext"),
            ("note", "fa5s.sticky-note", "viewer_tool_text_note"),
        ]

        for tool, icon, tooltip in tools:
            btn = QToolButton(self.toolbar)
            btn.setIcon(qta.icon(icon, color="#2D2A26", color_active="#C96442"))
            btn.setToolTip(t(tooltip))
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, t=tool: self.set_tool(t))
            self.toolbar.addWidget(btn)
            self.tool_buttons[tool] = btn

        self.toolbar.addSeparator()
        
        # Color pickers
        self.color_buttons = {}
        colors = [
            ("yellow", pa.COLORS["yellow"], "viewer_color_yellow"),
            ("green", pa.COLORS["green"], "viewer_color_green"),
            ("pink", pa.COLORS["pink"], "viewer_color_pink"),
            ("blue", pa.COLORS["blue"], "viewer_color_blue")
        ]
        
        for color_name, rgb, tooltip in colors:
            btn = QToolButton(self.toolbar)
            color_hex = f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
            btn.setStyleSheet(f"QToolButton {{ background-color: {color_hex}; border-radius: 4px; margin: 2px; width: 16px; height: 16px; }}")
            btn.setToolTip(t(tooltip))
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, c=color_name: self.set_color(c))
            self.toolbar.addWidget(btn)
            self.color_buttons[color_name] = btn

        # Main Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)

        # PDF Canvas
        self.canvas = PdfCanvas()
        self.canvas.zoomChanged.connect(self._on_zoom_changed)
        self.canvas.documentModified.connect(self._on_document_modified)
        self.canvas.selectionChanged.connect(self._on_selection_changed)
        self.splitter.addWidget(self.canvas)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setMaximumWidth(300)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        
        lbl_annot = QLabel(t("viewer_annotations"))
        lbl_annot.setStyleSheet("font-weight: bold;")
        sidebar_layout.addWidget(lbl_annot)
        
        self.annot_list = QListWidget()
        self.annot_list.setWordWrap(True)
        self.annot_list.itemClicked.connect(self._on_annot_clicked)
        sidebar_layout.addWidget(self.annot_list)
        
        self.splitter.addWidget(self.sidebar)
        self.splitter.setSizes([700, 200])

        self.set_tool("hand")
        self.set_color("yellow")
        self.retranslate_ui()

    def _add_tool(self, toolbar, icon_name, tooltip, callback):
        btn = QToolButton(toolbar)
        btn.setIcon(qta.icon(icon_name, color="#2D2A26", color_active="#C96442"))
        btn.setToolTip(t(tooltip))
        btn.clicked.connect(callback)
        toolbar.addWidget(btn)
        return btn

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.open_file)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_file)
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.canvas.undo)
        QShortcut(QKeySequence("V"), self).activated.connect(lambda: self.set_tool("select"))
        QShortcut(QKeySequence("H"), self).activated.connect(lambda: self.set_tool("hand"))

    def retranslate_ui(self):
        pass # The dynamic keys will be re-rendered

    def set_tool(self, tool):
        self.canvas.set_tool(tool)
        for t_name, btn in self.tool_buttons.items():
            btn.setChecked(t_name == tool)
            
        # If markup tool and selection exists, apply it immediately
        if tool in pa.MARKUP_TOOLS and self.canvas.has_selection():
            self.canvas.markup_selection(tool)
            self.set_tool("select")

    def set_color(self, color_name):
        rgb = pa.COLORS[color_name]
        for tool in pa.MARKUP_TOOLS + ("note",):
            self.canvas.tool_colors[tool] = rgb
        for c_name, btn in self.color_buttons.items():
            btn.setChecked(c_name == color_name)

    def open_file(self, file_path=None):
        if self.has_unsaved_changes:
            ans = QMessageBox.question(self, t("warning"), t("viewer_unsaved_changes"),
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if ans == QMessageBox.Yes:
                self.save_file()
            elif ans == QMessageBox.Cancel:
                return

        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(self, t("viewer_open"), "", "PDF Files (*.pdf)")
        if not file_path:
            return

        try:
            doc = fitz.open(file_path)
            if doc.needs_pass:
                pwd, ok = QInputDialog.getText(self, t("viewer_password_title"), t("viewer_password_prompt").format(file=os.path.basename(file_path)))
                if ok and pwd:
                    doc.authenticate(pwd)
                else:
                    doc.close()
                    return
            
            self.doc = doc
            self.file_path = file_path
            self.password = None
            self.canvas.set_document(doc)
            self.has_unsaved_changes = False
            self.refresh_annotations()
            self._update_title()
        except Exception as e:
            QMessageBox.critical(self, t("error"), t("viewer_load_error").format(file=file_path, error=str(e)))

    def save_file(self):
        if not self.doc or not self.file_path:
            return
        try:
            self.doc, _ = pa.save_document(self.doc, self.file_path, self.password)
            self.canvas.set_document(self.doc, keep_view=True)
            self.has_unsaved_changes = False
            self.refresh_annotations()
            self._update_title()
            QMessageBox.information(self, t("success"), t("viewer_saved"))
        except Exception as e:
            QMessageBox.critical(self, t("error"), f"Save error: {e}")

    def save_file_as(self):
        if not self.doc:
            return
        path, _ = QFileDialog.getSaveFileName(self, t("viewer_save_as"), self.file_path, "PDF Files (*.pdf)")
        if path:
            self.file_path = path
            self.save_file()

    def _on_zoom_changed(self, zoom):
        self.lbl_zoom.setText(f" {int(zoom * 100)}% ")

    def _on_document_modified(self):
        self.has_unsaved_changes = True
        self.refresh_annotations()
        self._update_title()

    def _on_selection_changed(self, has_sel):
        pass

    def _update_title(self):
        if self.file_path:
            base = os.path.basename(self.file_path)
            if self.has_unsaved_changes:
                base = "*" + base
            # If we wanted to update main window title, we could do it here
            
    def refresh_annotations(self):
        self.annot_list.clear()
        if not self.doc:
            return
        annots = pa.list_annotations(self.doc)
        if not annots:
            self.annot_list.addItem(t("viewer_no_annotations"))
            return
            
        for a in annots:
            item = QListWidgetItem(f"{a.type_name}: {a.content[:50]}..." if len(a.content) > 50 else f"{a.type_name}: {a.content}")
            item.setData(Qt.UserRole, (a.page, a.rect))
            self.annot_list.addItem(item)

    def _on_annot_clicked(self, item):
        data = item.data(Qt.UserRole)
        if data:
            page, rect = data
            self.canvas.flash_rect(page, rect)

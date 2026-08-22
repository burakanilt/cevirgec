import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QLineEdit, QGroupBox, 
                               QMessageBox, QListWidget, QSpinBox, QSplitter, QScrollArea)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
from core.pdf_ops import merge_pdfs, split_pdf, compress_pdf, extract_pdf_images, reorder_pdf_pages
from core.pdf_backend import open_document, render_page, page_count
from core.utils.i18n import t

class PagePdfTools(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.single_pdf_path = None
        self.pdf_doc = None
        self.current_page = 0
        self.total_pages = 0
        
        main_layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # --- SOL TARAF: Araçlar ---
        left_widget = QWidget()
        layout = QVBoxLayout(left_widget)
        
        # 1. Merge
        self.group_merge = QGroupBox(t("tab_merge"))
        merge_layout = QVBoxLayout()
        self.list_merge = QListWidget()
        self.btn_add = QPushButton(t("btn_add_pdf"))
        self.btn_add.clicked.connect(self.add_merge_file)
        self.btn_merge = QPushButton(t("btn_merge_pdfs"))
        self.btn_merge.clicked.connect(self.do_merge)
        merge_layout.addWidget(self.list_merge)
        merge_layout.addWidget(self.btn_add)
        merge_layout.addWidget(self.btn_merge)
        self.group_merge.setLayout(merge_layout)
        layout.addWidget(self.group_merge)
        
        # General Single PDF Tools
        self.group_single = QGroupBox(t("nav_pdf_tools"))
        single_layout = QVBoxLayout()
        
        self.lbl_single = QLabel(t("selected_file", file=t("none_selected")))
        self.btn_single = QPushButton(t("select_file"))
        self.btn_single.clicked.connect(self.select_single_pdf)
        single_layout.addWidget(self.lbl_single)
        single_layout.addWidget(self.btn_single)
        
        # Split
        split_layout = QHBoxLayout()
        self.lbl_start = QLabel("Başlangıç:")
        self.spin_start = QSpinBox(); self.spin_start.setMinimum(1); self.spin_start.setMaximum(9999)
        split_layout.addWidget(self.lbl_start)
        split_layout.addWidget(self.spin_start)
        self.lbl_end = QLabel("Bitiş:")
        self.spin_end = QSpinBox(); self.spin_end.setMinimum(1); self.spin_end.setMaximum(9999)
        split_layout.addWidget(self.lbl_end)
        split_layout.addWidget(self.spin_end)
        self.btn_split = QPushButton(t("tab_reorder"))
        self.btn_split.clicked.connect(self.do_split)
        split_layout.addWidget(self.btn_split)
        single_layout.addLayout(split_layout)
        
        # Reorder / Delete
        reorder_layout = QHBoxLayout()
        self.lbl_reorder = QLabel(t("lbl_page_order"))
        self.txt_pages = QLineEdit()
        self.btn_reorder = QPushButton(t("btn_reorder_save"))
        self.btn_reorder.clicked.connect(self.do_reorder)
        reorder_layout.addWidget(self.lbl_reorder)
        reorder_layout.addWidget(self.txt_pages)
        reorder_layout.addWidget(self.btn_reorder)
        single_layout.addLayout(reorder_layout)
        
        # Compress & Extract
        action_layout = QHBoxLayout()
        self.btn_compress = QPushButton(t("btn_compress_pdf"))
        self.btn_compress.clicked.connect(self.do_compress)
        self.btn_extract = QPushButton("Görselleri Çıkart")
        self.btn_extract.clicked.connect(self.do_extract)
        action_layout.addWidget(self.btn_compress)
        action_layout.addWidget(self.btn_extract)
        single_layout.addLayout(action_layout)
        
        self.group_single.setLayout(single_layout)
        layout.addWidget(self.group_single)
        
        layout.addStretch()
        
        # --- SAĞ TARAF: PDF Önizleme ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        viewer_controls = QHBoxLayout()
        self.btn_prev = QPushButton("<")
        self.btn_prev.clicked.connect(self.prev_page)
        self.lbl_page = QLabel("0 / 0")
        self.lbl_page.setAlignment(Qt.AlignCenter)
        self.btn_next = QPushButton(">")
        self.btn_next.clicked.connect(self.next_page)
        
        viewer_controls.addWidget(self.btn_prev)
        viewer_controls.addWidget(self.lbl_page)
        viewer_controls.addWidget(self.btn_next)
        right_layout.addLayout(viewer_controls)
        
        self.scroll_area = QScrollArea()
        self.lbl_viewer = QLabel(t("preview"))
        self.lbl_viewer.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.lbl_viewer)
        self.scroll_area.setWidgetResizable(True)
        right_layout.addWidget(self.scroll_area)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([450, 550])

    def retranslate_ui(self):
        self.group_merge.setTitle(t("tab_merge"))
        self.btn_add.setText(t("btn_add_pdf"))
        self.btn_merge.setText(t("btn_merge_pdfs"))
        self.group_single.setTitle(t("nav_pdf_tools"))
        
        if self.single_pdf_path:
            self.lbl_single.setText(t("selected_file", file=os.path.basename(self.single_pdf_path)))
        else:
            self.lbl_single.setText(t("selected_file", file=t("none_selected")))
            
        self.btn_single.setText(t("select_file"))
        self.lbl_reorder.setText(t("lbl_page_order"))
        self.btn_reorder.setText(t("btn_reorder_save"))
        self.btn_compress.setText(t("btn_compress_pdf"))

    def add_merge_file(self):
        paths, _ = QFileDialog.getOpenFileNames(self, t("select_file"), "", "PDF Files (*.pdf)")
        for p in paths:
            self.list_merge.addItem(p)

    def do_merge(self):
        if self.list_merge.count() < 2:
            QMessageBox.warning(self, t("warning"), t("please_select_file"))
            return
        
        paths = [self.list_merge.item(i).text() for i in range(self.list_merge.count())]
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
        if out_path:
            try:
                merge_pdfs(paths, out_path)
                QMessageBox.information(self, t("success"), t("msg_merge_success"))
            except Exception as e:
                QMessageBox.critical(self, t("error"), str(e))

    def select_single_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, t("select_file"), "", "PDF Files (*.pdf)")
        if path:
            self.single_pdf_path = path
            self.lbl_single.setText(t("selected_file", file=os.path.basename(path)))
            self.load_pdf_viewer(path)

    def load_pdf_viewer(self, path):
        if self.pdf_doc:
            self.pdf_doc.close()
        try:
            self.pdf_doc = open_document(path)
            self.total_pages = page_count(self.pdf_doc)
            self.current_page = 0
            self.render_current_page()
        except Exception as e:
            QMessageBox.critical(self, t("error"), f"{e}")

    def render_current_page(self):
        if not self.pdf_doc or self.total_pages == 0:
            return
            
        try:
            img_data = render_page(self.pdf_doc, self.current_page, dpi=150)
            img = QImage.fromData(img_data)
            pixmap = QPixmap.fromImage(img)
            self.lbl_viewer.setPixmap(pixmap)
            self.lbl_page.setText(f"{self.current_page + 1} / {self.total_pages}")
        except Exception as e:
            self.lbl_viewer.setText(f"{e}")

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.render_current_page()

    def next_page(self):
        if self.total_pages > 0 and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.render_current_page()

    def do_split(self):
        if not self.single_pdf_path: return
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
        if out_path:
            try:
                split_pdf(self.single_pdf_path, out_path, self.spin_start.value() - 1, self.spin_end.value() - 1)
                QMessageBox.information(self, t("success"), t("msg_reorder_success"))
            except Exception as e:
                QMessageBox.critical(self, t("error"), str(e))

    def parse_page_list(self, text: str) -> list[int]:
        pages = []
        parts = text.split(',')
        for p in parts:
            p = p.strip()
            if not p: continue
            if '-' in p:
                start, end = p.split('-')
                pages.extend(list(range(int(start) - 1, int(end))))
            else:
                pages.append(int(p) - 1)
        return pages

    def do_reorder(self):
        if not self.single_pdf_path: return
        text = self.txt_pages.text()
        if not text: return
        
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
        if out_path:
            try:
                pages = self.parse_page_list(text)
                reorder_pdf_pages(self.single_pdf_path, out_path, pages)
                QMessageBox.information(self, t("success"), t("msg_reorder_success"))
            except Exception as e:
                QMessageBox.critical(self, t("error"), str(e))

    def do_compress(self):
        if not self.single_pdf_path: return
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
        if out_path:
            try:
                original_size = os.path.getsize(self.single_pdf_path)
                compress_pdf(self.single_pdf_path, out_path)
                new_size = os.path.getsize(out_path)
                ratio = int((1 - (new_size / original_size)) * 100) if original_size > 0 else 0
                msg = t("msg_compress_success", 
                        old_size=f"{original_size/1024/1024:.2f} MB", 
                        new_size=f"{new_size/1024/1024:.2f} MB", 
                        ratio=ratio)
                QMessageBox.information(self, t("success"), msg)
            except Exception as e:
                QMessageBox.critical(self, t("error"), str(e))

    def do_extract(self):
        if not self.single_pdf_path: return
        out_dir = QFileDialog.getExistingDirectory(self, t("select_file"))
        if out_dir:
            try:
                saved = extract_pdf_images(self.single_pdf_path, out_dir)
                QMessageBox.information(self, t("success"), f"{len(saved)} images extracted.")
            except Exception as e:
                QMessageBox.critical(self, t("error"), str(e))

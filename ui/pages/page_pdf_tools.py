import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QLineEdit, QGroupBox, 
                               QMessageBox, QListWidget, QSpinBox, QSplitter, QScrollArea)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
from core.pdf_ops import merge_pdfs, split_pdf, compress_pdf, extract_pdf_images, reorder_pdf_pages
from core.pdf_backend import open_document, render_page, page_count

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
        group_merge = QGroupBox("PDF Birleştirme")
        merge_layout = QVBoxLayout()
        self.list_merge = QListWidget()
        btn_add = QPushButton("Dosya Ekle")
        btn_add.clicked.connect(self.add_merge_file)
        btn_merge = QPushButton("Listeyi Birleştir")
        btn_merge.clicked.connect(self.do_merge)
        merge_layout.addWidget(self.list_merge)
        merge_layout.addWidget(btn_add)
        merge_layout.addWidget(btn_merge)
        group_merge.setLayout(merge_layout)
        layout.addWidget(group_merge)
        
        # General Single PDF Tools
        group_single = QGroupBox("Diğer Araçlar (Böl, Seç, Sıkıştır, Görsel Çıkart)")
        single_layout = QVBoxLayout()
        
        self.lbl_single = QLabel("Seçilen PDF: Yok")
        btn_single = QPushButton("İşlem Yapılacak PDF'i Seç")
        btn_single.clicked.connect(self.select_single_pdf)
        single_layout.addWidget(self.lbl_single)
        single_layout.addWidget(btn_single)
        
        # Split
        split_layout = QHBoxLayout()
        split_layout.addWidget(QLabel("Başlangıç Sayfası:"))
        self.spin_start = QSpinBox(); self.spin_start.setMinimum(1); self.spin_start.setMaximum(9999)
        split_layout.addWidget(self.spin_start)
        split_layout.addWidget(QLabel("Bitiş Sayfası:"))
        self.spin_end = QSpinBox(); self.spin_end.setMinimum(1); self.spin_end.setMaximum(9999)
        split_layout.addWidget(self.spin_end)
        btn_split = QPushButton("PDF'i Böl")
        btn_split.clicked.connect(self.do_split)
        split_layout.addWidget(btn_split)
        single_layout.addLayout(split_layout)
        
        # Reorder / Delete
        reorder_layout = QHBoxLayout()
        reorder_layout.addWidget(QLabel("Kalan Sayfalar (Örn: 1,3,4-10):"))
        self.txt_pages = QLineEdit()
        btn_reorder = QPushButton("Sayfaları Ayıkla/Sırala")
        btn_reorder.clicked.connect(self.do_reorder)
        reorder_layout.addWidget(self.txt_pages)
        reorder_layout.addWidget(btn_reorder)
        single_layout.addLayout(reorder_layout)
        
        # Compress & Extract
        action_layout = QHBoxLayout()
        btn_compress = QPushButton("Sıkıştır")
        btn_compress.clicked.connect(self.do_compress)
        btn_extract = QPushButton("İçindeki Görselleri Çıkart")
        btn_extract.clicked.connect(self.do_extract)
        action_layout.addWidget(btn_compress)
        action_layout.addWidget(btn_extract)
        single_layout.addLayout(action_layout)
        
        group_single.setLayout(single_layout)
        layout.addWidget(group_single)
        
        layout.addStretch()
        
        # --- SAĞ TARAF: PDF Önizleme ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        viewer_controls = QHBoxLayout()
        self.btn_prev = QPushButton("<")
        self.btn_prev.clicked.connect(self.prev_page)
        self.lbl_page = QLabel("Sayfa: 0 / 0")
        self.lbl_page.setAlignment(Qt.AlignCenter)
        self.btn_next = QPushButton(">")
        self.btn_next.clicked.connect(self.next_page)
        
        viewer_controls.addWidget(self.btn_prev)
        viewer_controls.addWidget(self.lbl_page)
        viewer_controls.addWidget(self.btn_next)
        right_layout.addLayout(viewer_controls)
        
        self.scroll_area = QScrollArea()
        self.lbl_viewer = QLabel("PDF Önizleme Alanı")
        self.lbl_viewer.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.lbl_viewer)
        self.scroll_area.setWidgetResizable(True)
        right_layout.addWidget(self.scroll_area)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([450, 550])

    def add_merge_file(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "PDF Seç", "", "PDF Files (*.pdf)")
        for p in paths:
            self.list_merge.addItem(p)

    def do_merge(self):
        if self.list_merge.count() < 2:
            QMessageBox.warning(self, "Hata", "Birleştirme için en az 2 dosya gereklidir.")
            return
        
        paths = [self.list_merge.item(i).text() for i in range(self.list_merge.count())]
        out_path, _ = QFileDialog.getSaveFileName(self, "Birleştirilmiş PDF'i Kaydet", "", "PDF Files (*.pdf)")
        if out_path:
            try:
                merge_pdfs(paths, out_path)
                QMessageBox.information(self, "Başarılı", "PDF'ler birleştirildi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

    def select_single_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "PDF Seç", "", "PDF Files (*.pdf)")
        if path:
            self.single_pdf_path = path
            self.lbl_single.setText(f"Seçilen PDF: {os.path.basename(path)}")
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
            QMessageBox.critical(self, "Hata", f"PDF yüklenirken hata: {e}")

    def render_current_page(self):
        if not self.pdf_doc or self.total_pages == 0:
            return
            
        try:
            img_data = render_page(self.pdf_doc, self.current_page, dpi=150)
            img = QImage.fromData(img_data)
            pixmap = QPixmap.fromImage(img)
            self.lbl_viewer.setPixmap(pixmap)
            self.lbl_page.setText(f"Sayfa: {self.current_page + 1} / {self.total_pages}")
        except Exception as e:
            self.lbl_viewer.setText(f"Görüntüleme Hatası: {e}")

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
        out_path, _ = QFileDialog.getSaveFileName(self, "Farklı Kaydet", "", "PDF Files (*.pdf)")
        if out_path:
            try:
                split_pdf(self.single_pdf_path, out_path, self.spin_start.value() - 1, self.spin_end.value() - 1)
                QMessageBox.information(self, "Başarılı", "PDF bölündü.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

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
        
        out_path, _ = QFileDialog.getSaveFileName(self, "Farklı Kaydet", "", "PDF Files (*.pdf)")
        if out_path:
            try:
                pages = self.parse_page_list(text)
                reorder_pdf_pages(self.single_pdf_path, out_path, pages)
                QMessageBox.information(self, "Başarılı", "Sayfalar ayıklandı.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

    def do_compress(self):
        if not self.single_pdf_path: return
        out_path, _ = QFileDialog.getSaveFileName(self, "Farklı Kaydet", "", "PDF Files (*.pdf)")
        if out_path:
            try:
                original_size = os.path.getsize(self.single_pdf_path)
                compress_pdf(self.single_pdf_path, out_path)
                new_size = os.path.getsize(out_path)
                msg = f"Sıkıştırma tamamlandı.\nEski: {original_size/1024/1024:.2f} MB\nYeni: {new_size/1024/1024:.2f} MB"
                QMessageBox.information(self, "Başarılı", msg)
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

    def do_extract(self):
        if not self.single_pdf_path: return
        out_dir = QFileDialog.getExistingDirectory(self, "Görsellerin Kaydedileceği Klasörü Seçin")
        if out_dir:
            try:
                saved = extract_pdf_images(self.single_pdf_path, out_dir)
                QMessageBox.information(self, "Başarılı", f"{len(saved)} adet görsel çıkartıldı.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

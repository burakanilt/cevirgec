import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QRadioButton, QSpinBox, 
                               QGroupBox, QMessageBox)
from core.pdf_backend import open_document
from core.signature import add_signature_to_pdf

class PageSignature(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_path = None
        self.sig_path = None
        
        layout = QVBoxLayout(self)
        
        # File selections
        self.lbl_pdf = QLabel("Seçilen PDF: Yok")
        btn_pdf = QPushButton("PDF Seç")
        btn_pdf.clicked.connect(self.select_pdf)
        
        self.lbl_sig = QLabel("Seçilen İmza (Şeffaf PNG): Yok")
        btn_sig = QPushButton("İmza Seç")
        btn_sig.clicked.connect(self.select_sig)
        
        layout.addWidget(self.lbl_pdf)
        layout.addWidget(btn_pdf)
        layout.addWidget(self.lbl_sig)
        layout.addWidget(btn_sig)
        
        # Page Selection
        page_layout = QHBoxLayout()
        page_layout.addWidget(QLabel("Sayfa (1'den başlar):"))
        self.spin_page = QSpinBox()
        self.spin_page.setMinimum(1)
        self.spin_page.setMaximum(9999)
        page_layout.addWidget(self.spin_page)
        layout.addLayout(page_layout)
        
        # Position Selection
        group_pos = QGroupBox("İmza Konumu")
        pos_layout = QHBoxLayout()
        self.rb_br = QRadioButton("Sağ Alt")
        self.rb_bl = QRadioButton("Sol Alt")
        self.rb_tr = QRadioButton("Sağ Üst")
        self.rb_tl = QRadioButton("Sol Üst")
        self.rb_c = QRadioButton("Merkez")
        self.rb_br.setChecked(True) # Default
        
        pos_layout.addWidget(self.rb_br)
        pos_layout.addWidget(self.rb_bl)
        pos_layout.addWidget(self.rb_tr)
        pos_layout.addWidget(self.rb_tl)
        pos_layout.addWidget(self.rb_c)
        group_pos.setLayout(pos_layout)
        layout.addWidget(group_pos)
        
        # Action Button
        btn_apply = QPushButton("İmzayı Ekle ve Kaydet")
        btn_apply.clicked.connect(self.apply_signature)
        layout.addWidget(btn_apply)
        layout.addStretch()

    def select_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "PDF Seç", "", "PDF Files (*.pdf)")
        if path:
            self.pdf_path = path
            self.lbl_pdf.setText(f"Seçilen PDF: {os.path.basename(path)}")

    def select_sig(self):
        path, _ = QFileDialog.getOpenFileName(self, "İmza Seç", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.sig_path = path
            self.lbl_sig.setText(f"Seçilen İmza: {os.path.basename(path)}")

    def calculate_rect(self, doc_width, doc_height, sig_width=150, sig_height=50, margin=50):
        if self.rb_br.isChecked(): # Sağ Alt
            x0 = doc_width - margin - sig_width
            y1 = doc_height - margin
            x1 = x0 + sig_width
            y0 = y1 - sig_height
        elif self.rb_bl.isChecked(): # Sol Alt
            x0 = margin
            y1 = doc_height - margin
            x1 = x0 + sig_width
            y0 = y1 - sig_height
        elif self.rb_tr.isChecked(): # Sağ Üst
            x0 = doc_width - margin - sig_width
            y0 = margin
            x1 = x0 + sig_width
            y1 = y0 + sig_height
        elif self.rb_tl.isChecked(): # Sol Üst
            x0 = margin
            y0 = margin
            x1 = x0 + sig_width
            y1 = y0 + sig_height
        else: # Merkez
            x0 = (doc_width - sig_width) / 2
            y0 = (doc_height - sig_height) / 2
            x1 = x0 + sig_width
            y1 = y0 + sig_height
        
        return (x0, y0, x1, y1)

    def apply_signature(self):
        if not self.pdf_path or not self.sig_path:
            QMessageBox.warning(self, "Hata", "Lütfen PDF ve İmza dosyalarını seçin.")
            return
            
        out_path, _ = QFileDialog.getSaveFileName(self, "Farklı Kaydet", "", "PDF Files (*.pdf)")
        if not out_path:
            return
            
        try:
            doc = open_document(self.pdf_path)
            # PyMuPDF pages are 0-indexed
            page_index = self.spin_page.value() - 1
            if page_index >= len(doc):
                raise ValueError("Sayfa numarası PDF'in toplam sayfasından büyük.")
                
            page = doc[page_index]
            rect = self.calculate_rect(page.rect.width, page.rect.height)
            doc.close() # Close since add_signature_to_pdf opens it again
            
            add_signature_to_pdf(self.pdf_path, self.sig_path, page_index, rect, out_path)
            QMessageBox.information(self, "Başarılı", "İmza başarıyla eklendi.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

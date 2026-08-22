import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QLineEdit, QMessageBox,
                               QGroupBox, QSpinBox)
from core.watermark import add_watermark, remove_watermark

class PageWatermark(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_path = None
        
        layout = QVBoxLayout(self)
        
        # Seçim Grubu
        group_sel = QGroupBox("PDF Seçimi")
        sel_layout = QVBoxLayout()
        self.lbl_pdf = QLabel("Seçilen PDF: Yok")
        btn_pdf = QPushButton("İşlem Yapılacak PDF'i Seç")
        btn_pdf.clicked.connect(self.select_pdf)
        sel_layout.addWidget(self.lbl_pdf)
        sel_layout.addWidget(btn_pdf)
        group_sel.setLayout(sel_layout)
        layout.addWidget(group_sel)
        
        # Filigran Ekle
        group_add = QGroupBox("Filigran Ekle")
        add_layout = QVBoxLayout()
        self.txt_watermark = QLineEdit()
        self.txt_watermark.setPlaceholderText("Filigran Metni (Örn: GİZLİ)")
        self.txt_watermark.setText("GİZLİ")
        
        self.spin_fontsize = QSpinBox()
        self.spin_fontsize.setRange(10, 200)
        self.spin_fontsize.setValue(40)
        self.spin_fontsize.setPrefix("Boyut: ")
        
        font_layout = QHBoxLayout()
        font_layout.addWidget(self.txt_watermark)
        font_layout.addWidget(self.spin_fontsize)
        
        btn_add = QPushButton("Filigran Ekle ve Kaydet")
        btn_add.clicked.connect(self.do_add_watermark)
        
        add_layout.addLayout(font_layout)
        add_layout.addWidget(btn_add)
        group_add.setLayout(add_layout)
        layout.addWidget(group_add)
        
        # Filigran Kaldır
        group_rem = QGroupBox("Filigran Kaldır")
        rem_layout = QVBoxLayout()
        btn_rem = QPushButton("Uygulama Tarafından Eklenmiş Filigranı Temizle")
        btn_rem.clicked.connect(self.do_remove_watermark)
        rem_layout.addWidget(QLabel("Sadece bu uygulama ile OCG katmanı olarak eklenen filigranları kaldırır."))
        rem_layout.addWidget(btn_rem)
        group_rem.setLayout(rem_layout)
        layout.addWidget(group_rem)
        
        layout.addStretch()

    def select_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "PDF Seç", "", "PDF Files (*.pdf)")
        if path:
            self.pdf_path = path
            self.lbl_pdf.setText(f"Seçilen PDF: {os.path.basename(path)}")

    def do_add_watermark(self):
        if not self.pdf_path:
            QMessageBox.warning(self, "Hata", "Lütfen bir PDF seçin.")
            return
            
        text = self.txt_watermark.text()
        if not text:
            QMessageBox.warning(self, "Hata", "Lütfen bir filigran metni girin.")
            return
            
        out_path, _ = QFileDialog.getSaveFileName(self, "Farklı Kaydet", "", "PDF Files (*.pdf)")
        if out_path:
            try:
                fontsize = self.spin_fontsize.value()
                add_watermark(self.pdf_path, out_path, text=text, fontsize=fontsize)
                QMessageBox.information(self, "Başarılı", "Filigran başarıyla eklendi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

    def do_remove_watermark(self):
        if not self.pdf_path:
            QMessageBox.warning(self, "Hata", "Lütfen bir PDF seçin.")
            return
            
        out_path, _ = QFileDialog.getSaveFileName(self, "Farklı Kaydet", "", "PDF Files (*.pdf)")
        if out_path:
            try:
                remove_watermark(self.pdf_path, out_path)
                QMessageBox.information(self, "Başarılı", "Filigran başarıyla temizlendi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QLineEdit, QGroupBox, 
                               QMessageBox)
from core.pdf_ops import apply_encryption, apply_redaction, clear_pdf_metadata, revert_redactions
from PySide6.QtWidgets import QCheckBox

class PageSecurity(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_path = None
        
        layout = QVBoxLayout(self)
        
        # General File Selection
        self.lbl_pdf = QLabel("Seçilen PDF: Yok")
        btn_pdf = QPushButton("İşlem Yapılacak PDF'i Seç")
        btn_pdf.clicked.connect(self.select_pdf)
        
        layout.addWidget(self.lbl_pdf)
        layout.addWidget(btn_pdf)
        
        # 1. Encryption
        group_enc = QGroupBox("Şifreleme (AES-256)")
        enc_layout = QVBoxLayout()
        self.txt_pw = QLineEdit()
        self.txt_pw.setPlaceholderText("Parola girin...")
        self.txt_pw.setEchoMode(QLineEdit.EchoMode.Password)
        btn_enc = QPushButton("Şifrele / Şifre Kaldır (Farklı Kaydet)")
        btn_enc.clicked.connect(self.do_encryption)
        enc_layout.addWidget(self.txt_pw)
        enc_layout.addWidget(btn_enc)
        group_enc.setLayout(enc_layout)
        layout.addWidget(group_enc)
        
        # 2. Redaction (KVKK)
        group_redact = QGroupBox("Veri Karartma (Redaction / KVKK)")
        redact_layout = QVBoxLayout()
        self.txt_redact = QLineEdit()
        self.txt_redact.setPlaceholderText("Karartılacak Kelime / TCKN / IBAN...")
        
        self.chk_reversible = QCheckBox("Geri Döndürülebilir Karartma (Annotation Olarak Ekle)")
        btn_redact = QPushButton("Metni Karart")
        btn_redact.clicked.connect(self.do_redaction)
        
        btn_revert = QPushButton("Geri Döndürülebilir Karartmaları Kaldır")
        btn_revert.clicked.connect(self.do_revert_redaction)
        
        redact_layout.addWidget(self.txt_redact)
        redact_layout.addWidget(self.chk_reversible)
        redact_layout.addWidget(btn_redact)
        redact_layout.addWidget(btn_revert)
        group_redact.setLayout(redact_layout)
        layout.addWidget(group_redact)
        
        # 3. Metadata
        group_meta = QGroupBox("Üstveri (Metadata) Temizleyici")
        meta_layout = QVBoxLayout()
        btn_meta = QPushButton("Tüm Dijital Ayak İzlerini (Metadata) Temizle")
        btn_meta.clicked.connect(self.do_clear_metadata)
        meta_layout.addWidget(btn_meta)
        group_meta.setLayout(meta_layout)
        layout.addWidget(group_meta)
        
        layout.addStretch()

    def select_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "PDF Seç", "", "PDF Files (*.pdf)")
        if path:
            self.pdf_path = path
            self.lbl_pdf.setText(f"Seçilen PDF: {os.path.basename(path)}")

    def do_encryption(self):
        if not self.pdf_path:
            QMessageBox.warning(self, "Hata", "Lütfen bir PDF seçin.")
            return
        pw = self.txt_pw.text()
        out_path, _ = QFileDialog.getSaveFileName(self, "Farklı Kaydet", "", "PDF Files (*.pdf)")
        if out_path:
            try:
                apply_encryption(self.pdf_path, out_path, user_pw=pw if pw else None)
                QMessageBox.information(self, "Başarılı", "Şifreleme işlemi tamamlandı.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

    def do_redaction(self):
        if not self.pdf_path:
            QMessageBox.warning(self, "Hata", "Lütfen bir PDF seçin.")
            return
        text = self.txt_redact.text()
        if not text:
            QMessageBox.warning(self, "Hata", "Lütfen karartılacak bir metin girin.")
            return
            
        out_path, _ = QFileDialog.getSaveFileName(self, "Farklı Kaydet", "", "PDF Files (*.pdf)")
        if out_path:
            try:
                apply_redaction(self.pdf_path, out_path, text, reversible=self.chk_reversible.isChecked())
                QMessageBox.information(self, "Başarılı", "Karartma işlemi tamamlandı.\n\nUYARI: Bu, paylaşım amaçlı düzenlenmiş bir kopyadır; resmi doğrulama için orijinal belge kullanılmalıdır.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

    def do_revert_redaction(self):
        if not self.pdf_path:
            QMessageBox.warning(self, "Hata", "Lütfen bir PDF seçin.")
            return
            
        out_path, _ = QFileDialog.getSaveFileName(self, "Farklı Kaydet", "", "PDF Files (*.pdf)")
        if out_path:
            try:
                revert_redactions(self.pdf_path, out_path)
                QMessageBox.information(self, "Başarılı", "Geri döndürülebilir karartmalar temizlendi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

    def do_clear_metadata(self):
        if not self.pdf_path:
            QMessageBox.warning(self, "Hata", "Lütfen bir PDF seçin.")
            return
        out_path, _ = QFileDialog.getSaveFileName(self, "Farklı Kaydet", "", "PDF Files (*.pdf)")
        if out_path:
            try:
                clear_pdf_metadata(self.pdf_path, out_path)
                QMessageBox.information(self, "Başarılı", "Metadata temizlendi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

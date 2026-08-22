import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QLineEdit, QGroupBox, 
                               QMessageBox, QCheckBox)
from core.pdf_ops import apply_encryption, apply_redaction, clear_pdf_metadata, revert_redactions
from core.utils.i18n import t

class PageSecurity(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_path = None
        
        layout = QVBoxLayout(self)
        
        # General File Selection
        self.lbl_pdf = QLabel(t("selected_file", file=t("none_selected")))
        self.btn_pdf = QPushButton(t("select_file"))
        self.btn_pdf.clicked.connect(self.select_pdf)
        
        layout.addWidget(self.lbl_pdf)
        layout.addWidget(self.btn_pdf)
        
        # 1. Encryption
        self.group_enc = QGroupBox(t("tab_encrypt"))
        enc_layout = QVBoxLayout()
        self.txt_pw = QLineEdit()
        self.txt_pw.setPlaceholderText(t("lbl_password"))
        self.txt_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_enc = QPushButton(t("btn_encrypt_pdf"))
        self.btn_enc.clicked.connect(self.do_encryption)
        enc_layout.addWidget(self.txt_pw)
        enc_layout.addWidget(self.btn_enc)
        self.group_enc.setLayout(enc_layout)
        layout.addWidget(self.group_enc)
        
        # 2. Redaction (KVKK / GDPR)
        self.group_redact = QGroupBox(t("tab_redact"))
        redact_layout = QVBoxLayout()
        self.txt_redact = QLineEdit()
        self.txt_redact.setPlaceholderText(t("placeholder_redact"))
        
        self.chk_reversible = QCheckBox(t("chk_reversible"))
        self.btn_redact = QPushButton(t("btn_apply_redaction"))
        self.btn_redact.clicked.connect(self.do_redaction)
        
        self.btn_revert = QPushButton("Geri Döndürülebilir Karartmaları Kaldır")
        self.btn_revert.clicked.connect(self.do_revert_redaction)
        
        redact_layout.addWidget(self.txt_redact)
        redact_layout.addWidget(self.chk_reversible)
        redact_layout.addWidget(self.btn_redact)
        redact_layout.addWidget(self.btn_revert)
        self.group_redact.setLayout(redact_layout)
        layout.addWidget(self.group_redact)
        
        # 3. Metadata
        self.group_meta = QGroupBox(t("tab_metadata"))
        meta_layout = QVBoxLayout()
        self.btn_meta = QPushButton(t("btn_clean_metadata"))
        self.btn_meta.clicked.connect(self.do_clear_metadata)
        meta_layout.addWidget(self.btn_meta)
        self.group_meta.setLayout(meta_layout)
        layout.addWidget(self.group_meta)
        
        layout.addStretch()

    def retranslate_ui(self):
        if self.pdf_path:
            self.lbl_pdf.setText(t("selected_file", file=os.path.basename(self.pdf_path)))
        else:
            self.lbl_pdf.setText(t("selected_file", file=t("none_selected")))
            
        self.btn_pdf.setText(t("select_file"))
        self.group_enc.setTitle(t("tab_encrypt"))
        self.txt_pw.setPlaceholderText(t("lbl_password"))
        self.btn_enc.setText(t("btn_encrypt_pdf"))
        
        self.group_redact.setTitle(t("tab_redact"))
        self.txt_redact.setPlaceholderText(t("placeholder_redact"))
        self.chk_reversible.setText(t("chk_reversible"))
        self.btn_redact.setText(t("btn_apply_redaction"))
        
        self.group_meta.setTitle(t("tab_metadata"))
        self.btn_meta.setText(t("btn_clean_metadata"))

    def select_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, t("select_file"), "", "PDF Files (*.pdf)")
        if path:
            self.pdf_path = path
            self.lbl_pdf.setText(t("selected_file", file=os.path.basename(path)))

    def do_encryption(self):
        if not self.pdf_path:
            QMessageBox.warning(self, t("warning"), t("please_select_file"))
            return
        pw = self.txt_pw.text()
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
        if out_path:
            try:
                apply_encryption(self.pdf_path, out_path, user_pw=pw if pw else None)
                QMessageBox.information(self, t("success"), t("msg_encrypt_success"))
            except Exception as e:
                QMessageBox.critical(self, t("error"), str(e))

    def do_redaction(self):
        if not self.pdf_path:
            QMessageBox.warning(self, t("warning"), t("please_select_file"))
            return
        text = self.txt_redact.text()
        if not text:
            QMessageBox.warning(self, t("warning"), t("placeholder_redact"))
            return
            
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
        if out_path:
            try:
                apply_redaction(self.pdf_path, out_path, text, reversible=self.chk_reversible.isChecked())
                QMessageBox.information(self, t("success"), t("msg_redact_success"))
            except Exception as e:
                QMessageBox.critical(self, t("error"), str(e))

    def do_revert_redaction(self):
        if not self.pdf_path:
            QMessageBox.warning(self, t("warning"), t("please_select_file"))
            return
            
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
        if out_path:
            try:
                revert_redactions(self.pdf_path, out_path)
                QMessageBox.information(self, t("success"), "Reverted redactions.")
            except Exception as e:
                QMessageBox.critical(self, t("error"), str(e))

    def do_clear_metadata(self):
        if not self.pdf_path:
            QMessageBox.warning(self, t("warning"), t("please_select_file"))
            return
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
        if out_path:
            try:
                clear_pdf_metadata(self.pdf_path, out_path)
                QMessageBox.information(self, t("success"), t("msg_meta_success"))
            except Exception as e:
                QMessageBox.critical(self, t("error"), str(e))

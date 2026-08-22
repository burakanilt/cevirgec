import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QLineEdit, QMessageBox,
                               QGroupBox, QSpinBox)
from core.watermark import add_watermark, remove_watermark
from core.utils.i18n import t

class PageWatermark(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_path = None
        
        layout = QVBoxLayout(self)
        
        # Seçim Grubu
        self.group_sel = QGroupBox(t("tab_add_watermark"))
        sel_layout = QVBoxLayout()
        self.lbl_pdf = QLabel(t("selected_file", file=t("none_selected")))
        self.btn_pdf = QPushButton(t("select_file"))
        self.btn_pdf.clicked.connect(self.select_pdf)
        sel_layout.addWidget(self.lbl_pdf)
        sel_layout.addWidget(self.btn_pdf)
        self.group_sel.setLayout(sel_layout)
        layout.addWidget(self.group_sel)
        
        # Filigran Ekle
        self.group_add = QGroupBox(t("tab_add_watermark"))
        add_layout = QVBoxLayout()
        self.txt_watermark = QLineEdit()
        self.txt_watermark.setPlaceholderText(t("placeholder_watermark"))
        self.txt_watermark.setText("GİZLİ")
        
        self.spin_fontsize = QSpinBox()
        self.spin_fontsize.setRange(10, 200)
        self.spin_fontsize.setValue(40)
        self.spin_fontsize.setPrefix("Boyut: ")
        
        font_layout = QHBoxLayout()
        font_layout.addWidget(self.txt_watermark)
        font_layout.addWidget(self.spin_fontsize)
        
        self.btn_add = QPushButton(t("btn_apply_watermark"))
        self.btn_add.clicked.connect(self.do_add_watermark)
        
        add_layout.addLayout(font_layout)
        add_layout.addWidget(self.btn_add)
        self.group_add.setLayout(add_layout)
        layout.addWidget(self.group_add)
        
        # Filigran Kaldır
        self.group_rem = QGroupBox(t("tab_remove_watermark"))
        rem_layout = QVBoxLayout()
        self.btn_rem = QPushButton(t("btn_remove_watermark"))
        self.btn_rem.clicked.connect(self.do_remove_watermark)
        rem_layout.addWidget(self.btn_rem)
        self.group_rem.setLayout(rem_layout)
        layout.addWidget(self.group_rem)
        
        layout.addStretch()

    def retranslate_ui(self):
        if self.pdf_path:
            self.lbl_pdf.setText(t("selected_file", file=os.path.basename(self.pdf_path)))
        else:
            self.lbl_pdf.setText(t("selected_file", file=t("none_selected")))
            
        self.btn_pdf.setText(t("select_file"))
        self.group_add.setTitle(t("tab_add_watermark"))
        self.txt_watermark.setPlaceholderText(t("placeholder_watermark"))
        self.btn_add.setText(t("btn_apply_watermark"))
        self.group_rem.setTitle(t("tab_remove_watermark"))
        self.btn_rem.setText(t("btn_remove_watermark"))

    def select_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, t("select_file"), "", "PDF Files (*.pdf)")
        if path:
            self.pdf_path = path
            self.lbl_pdf.setText(t("selected_file", file=os.path.basename(path)))

    def do_add_watermark(self):
        if not self.pdf_path:
            QMessageBox.warning(self, t("warning"), t("please_select_file"))
            return
            
        text = self.txt_watermark.text()
        if not text:
            QMessageBox.warning(self, t("warning"), t("placeholder_watermark"))
            return
            
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
        if out_path:
            try:
                fontsize = self.spin_fontsize.value()
                add_watermark(self.pdf_path, out_path, text=text, fontsize=fontsize)
                QMessageBox.information(self, t("success"), t("msg_wm_add_success"))
            except Exception as e:
                QMessageBox.critical(self, t("error"), str(e))

    def do_remove_watermark(self):
        if not self.pdf_path:
            QMessageBox.warning(self, t("warning"), t("please_select_file"))
            return
            
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
        if out_path:
            try:
                remove_watermark(self.pdf_path, out_path)
                QMessageBox.information(self, t("success"), t("msg_wm_rem_success"))
            except Exception as e:
                QMessageBox.critical(self, t("error"), str(e))

import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QRadioButton, QSpinBox, 
                               QGroupBox, QMessageBox)
from core.pdf_backend import open_document
from core.signature import add_signature_to_pdf
from core.utils.i18n import t

class PageSignature(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_path = None
        self.sig_path = None
        
        layout = QVBoxLayout(self)
        
        # File selections
        self.lbl_pdf = QLabel(t("selected_file", file=t("none_selected")))
        self.btn_pdf = QPushButton(t("select_file"))
        self.btn_pdf.clicked.connect(self.select_pdf)
        
        self.lbl_sig = QLabel(t("lbl_sig_image") + " " + t("none_selected"))
        self.btn_sig = QPushButton(t("btn_select_sig"))
        self.btn_sig.clicked.connect(self.select_sig)
        
        layout.addWidget(self.lbl_pdf)
        layout.addWidget(self.btn_pdf)
        layout.addWidget(self.lbl_sig)
        layout.addWidget(self.btn_sig)
        
        # Page Selection
        page_layout = QHBoxLayout()
        self.lbl_page = QLabel(t("lbl_sig_page"))
        self.spin_page = QSpinBox()
        self.spin_page.setMinimum(1)
        self.spin_page.setMaximum(9999)
        page_layout.addWidget(self.lbl_page)
        page_layout.addWidget(self.spin_page)
        layout.addLayout(page_layout)
        
        # Position Selection
        self.group_pos = QGroupBox(t("lbl_sig_position"))
        pos_layout = QHBoxLayout()
        self.rb_br = QRadioButton(t("pos_bottom_right"))
        self.rb_bl = QRadioButton(t("pos_bottom_left"))
        self.rb_tr = QRadioButton(t("pos_top_right"))
        self.rb_tl = QRadioButton(t("pos_top_left"))
        self.rb_c = QRadioButton("Merkez / Center")
        self.rb_br.setChecked(True) # Default
        
        pos_layout.addWidget(self.rb_br)
        pos_layout.addWidget(self.rb_bl)
        pos_layout.addWidget(self.rb_tr)
        pos_layout.addWidget(self.rb_tl)
        pos_layout.addWidget(self.rb_c)
        self.group_pos.setLayout(pos_layout)
        layout.addWidget(self.group_pos)
        
        # Action Button
        self.btn_apply = QPushButton(t("btn_sign_pdf"))
        self.btn_apply.clicked.connect(self.apply_signature)
        layout.addWidget(self.btn_apply)
        layout.addStretch()

    def retranslate_ui(self):
        if self.pdf_path:
            self.lbl_pdf.setText(t("selected_file", file=os.path.basename(self.pdf_path)))
        else:
            self.lbl_pdf.setText(t("selected_file", file=t("none_selected")))
            
        self.btn_pdf.setText(t("select_file"))
        
        if self.sig_path:
            self.lbl_sig.setText(t("lbl_sig_image") + " " + os.path.basename(self.sig_path))
        else:
            self.lbl_sig.setText(t("lbl_sig_image") + " " + t("none_selected"))
            
        self.btn_sig.setText(t("btn_select_sig"))
        self.lbl_page.setText(t("lbl_sig_page"))
        self.group_pos.setTitle(t("lbl_sig_position"))
        self.rb_br.setText(t("pos_bottom_right"))
        self.rb_bl.setText(t("pos_bottom_left"))
        self.rb_tr.setText(t("pos_top_right"))
        self.rb_tl.setText(t("pos_top_left"))
        self.btn_apply.setText(t("btn_sign_pdf"))

    def select_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, t("select_file"), "", "PDF Files (*.pdf)")
        if path:
            self.pdf_path = path
            self.lbl_pdf.setText(t("selected_file", file=os.path.basename(path)))

    def select_sig(self):
        path, _ = QFileDialog.getOpenFileName(self, t("btn_select_sig"), "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.sig_path = path
            self.lbl_sig.setText(t("lbl_sig_image") + f" {os.path.basename(path)}")

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
            QMessageBox.warning(self, t("warning"), t("please_select_file"))
            return
            
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
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
            doc.close()
            
            add_signature_to_pdf(self.pdf_path, self.sig_path, page_index, rect, out_path)
            QMessageBox.information(self, t("success"), t("msg_sign_success"))
        except Exception as e:
            QMessageBox.critical(self, t("error"), str(e))

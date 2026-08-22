import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTabWidget, QFormLayout, QLineEdit,
                               QComboBox, QMessageBox, QFileDialog, QGroupBox,
                               QTextEdit, QScrollArea, QCheckBox, QProgressBar)
from PySide6.QtCore import Qt, QObject, Signal
import threading
from PIL import Image
from core.convert.to_pdf import convert_docx_to_pdf as docx_to_pdf

from core.etds_tools import generate_ek1_decision, generate_ek2_user_notice, extract_verification_code
from core.pdf_ops import apply_bottom_margin
from core.pdf_backend import render_page, open_document
from core.router import analyze_document
from core.convert.to_word import convert_digital_pdf_to_word, convert_scanned_pdf_to_word
from core.convert.router import route_to_excel
from core.utils.i18n import t

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)
    success = Signal(str)

class PageEtds(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        
        self.tab_generator = QWidget()
        self.tab_pdf_adjust = QWidget()
        self.tab_legacy_ocr = QWidget()
        
        self.setup_tab_generator()
        self.setup_tab_pdf_adjust()
        self.setup_tab_legacy_ocr()
        
        self.tabs.addTab(self.tab_generator, "Karar Üretici (EK-1 / EK-2)")
        self.tabs.addTab(self.tab_pdf_adjust, "PDF Uyumlulaştırıcı")
        self.tabs.addTab(self.tab_legacy_ocr, "Eski Defter Dijitalleştirme")
        
        main_layout.addWidget(self.tabs)
        
    def retranslate_ui(self):
        self.tabs.setTabText(0, "Karar / Decision (EK-1 / EK-2)")
        self.tabs.setTabText(1, "PDF Uyumlulaştırıcı / Adjuster")
        self.tabs.setTabText(2, "Eski Defter / Legacy OCR")
        
    def setup_tab_generator(self):
        layout = QVBoxLayout(self.tab_generator)
        
        # Sırket Türü Warning
        group_info = QGroupBox(t("info"))
        info_layout = QVBoxLayout()
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Anonim Şirket (A.Ş.)", "Limited Şirket (Ltd. Şti.)", "Kooperatif"])
        self.combo_type.currentIndexChanged.connect(self.update_warning)
        
        self.lbl_warning = QLabel()
        self.lbl_warning.setWordWrap(True)
        self.lbl_warning.setStyleSheet("color: #ffa500; font-weight: bold;")
        
        info_layout.addWidget(QLabel("Şirket Türü / Company Type:"))
        info_layout.addWidget(self.combo_type)
        info_layout.addWidget(self.lbl_warning)
        group_info.setLayout(info_layout)
        layout.addWidget(group_info)
        
        self.update_warning() # Initial warning
        
        # Form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        form_layout = QFormLayout(scroll_content)
        
        self.txt_unvan = QLineEdit()
        self.txt_tarih = QLineEdit()
        self.txt_karar_no = QLineEdit()
        self.txt_katilanlar = QLineEdit()
        
        self.txt_mersis_no = QLineEdit()
        self.txt_vergi_dairesi = QLineEdit()
        self.txt_vergi_no = QLineEdit()
        self.txt_ticaret_sicil_md = QLineEdit()
        self.txt_ticaret_sicil_no = QLineEdit()
        
        self.txt_defter_turu = QLineEdit()
        self.txt_defter_turu.setText("Yönetim Kurulu Karar Defteri")
        self.txt_hesap_donemi = QLineEdit()
        self.txt_onay_tarihi = QLineEdit()
        self.txt_onay_no = QLineEdit()
        self.txt_onay_makami = QLineEdit()
        
        self.txt_yetkili_ad = QLineEdit()
        self.txt_yetkili_tckn = QLineEdit()
        self.txt_yetkili_eposta = QLineEdit()
        self.txt_yetkili_tel = QLineEdit()
        
        form_layout.addRow("Şirket Ünvanı / Title:", self.txt_unvan)
        form_layout.addRow("MERSİS No:", self.txt_mersis_no)
        form_layout.addRow("Vergi Dairesi / Tax Office:", self.txt_vergi_dairesi)
        form_layout.addRow("Vergi No / Tax ID:", self.txt_vergi_no)
        form_layout.addRow("Ticaret Sicili Md.:", self.txt_ticaret_sicil_md)
        form_layout.addRow("Ticaret Sicil No:", self.txt_ticaret_sicil_no)
        
        form_layout.addRow("Karar Tarihi / Date:", self.txt_tarih)
        form_layout.addRow("Karar No / Decision No:", self.txt_karar_no)
        form_layout.addRow("Katılanlar / Attendees:", self.txt_katilanlar)
        
        form_layout.addRow("Defter Türü / Book Type:", self.txt_defter_turu)
        form_layout.addRow("Hesap Dönemi / Period:", self.txt_hesap_donemi)
        form_layout.addRow("Onay Tarihi / Approval Date:", self.txt_onay_tarihi)
        form_layout.addRow("Onay No:", self.txt_onay_no)
        form_layout.addRow("Onay Makamı:", self.txt_onay_makami)
        
        form_layout.addRow("Yetkili Ad Soyad / Officer Name:", self.txt_yetkili_ad)
        form_layout.addRow("Yetkili TCKN / ID:", self.txt_yetkili_tckn)
        form_layout.addRow("Yetkili E-posta / Email:", self.txt_yetkili_eposta)
        form_layout.addRow("Yetkili Telefon / Phone:", self.txt_yetkili_tel)
        
        self.chk_kaydetme = QCheckBox("Kaydetme / Save")
        self.chk_guncelleme = QCheckBox("Güncelleme / Update")
        self.chk_silme = QCheckBox("Silme / Delete")
        self.chk_goruntuleme = QCheckBox("Görüntüleme / View")
        yetki_layout = QHBoxLayout()
        yetki_layout.addWidget(self.chk_kaydetme)
        yetki_layout.addWidget(self.chk_guncelleme)
        yetki_layout.addWidget(self.chk_silme)
        yetki_layout.addWidget(self.chk_goruntuleme)
        form_layout.addRow("Yetki Kapsamı / Permissions:", yetki_layout)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        btn_layout = QHBoxLayout()
        btn_ek1 = QPushButton("EK-1 Üret / Generate EK-1")
        btn_ek1.clicked.connect(self.generate_ek1)
        
        btn_ek2 = QPushButton("EK-2 Üret / Generate EK-2")
        btn_ek2.clicked.connect(self.generate_ek2)
        
        btn_layout.addWidget(btn_ek1)
        btn_layout.addWidget(btn_ek2)
        
        layout.addLayout(btn_layout)
        
    def update_warning(self):
        ctype = self.combo_type.currentText()
        if "Anonim" in ctype:
            self.lbl_warning.setText("Uyarı: A.Ş.'ler için Yönetim Kurulu Karar Defteri, Pay Defteri ve Genel Kurul Toplantı ve Müzakere Defteri e-ortamda zorunludur.")
        elif "Limited" in ctype:
            self.lbl_warning.setText("Uyarı: Ltd. Şti.'ler için Pay Defteri ve Genel Kurul Toplantı Defteri zorunludur. Müdürler Kurulu Karar Defteri ihtiyari (isteğe bağlıdır).")
        else:
            self.lbl_warning.setText("Uyarı: İlgili mevzuat uyarınca defter zorunluluklarınızı kontrol ediniz.")

    def get_yetki_kapsami_str(self):
        y = []
        if self.chk_kaydetme.isChecked(): y.append("Kaydetme")
        if self.chk_guncelleme.isChecked(): y.append("Güncelleme")
        if self.chk_silme.isChecked(): y.append("Silme")
        if self.chk_goruntuleme.isChecked(): y.append("Görüntüleme")
        return ", ".join(y)

    def generate_ek1(self):
        data = {
            "sirket_unvani": self.txt_unvan.text(),
            "karar_tarihi": self.txt_tarih.text(),
            "karar_no": self.txt_karar_no.text(),
            "katilanlar": self.txt_katilanlar.text(),
            
            "mersis_no": self.txt_mersis_no.text(),
            "vergi_dairesi": self.txt_vergi_dairesi.text(),
            "vergi_no": self.txt_vergi_no.text(),
            "ticaret_sicil_md": self.txt_ticaret_sicil_md.text(),
            "ticaret_sicil_no": self.txt_ticaret_sicil_no.text(),
            
            "defter_turu": self.txt_defter_turu.text(),
            "hesap_donemi": self.txt_hesap_donemi.text(),
            "onay_tarihi": self.txt_onay_tarihi.text(),
            "onay_no": self.txt_onay_no.text(),
            "onay_makami": self.txt_onay_makami.text(),
            
            "yetkili_ad_soyad": self.txt_yetkili_ad.text(),
            "yetkili_tckn": self.txt_yetkili_tckn.text(),
            "yetkili_eposta": self.txt_yetkili_eposta.text(),
            "yetkili_telefon": self.txt_yetkili_tel.text(),
            
            "yetki_kaydetme": self.chk_kaydetme.isChecked(),
            "yetki_guncelleme": self.chk_guncelleme.isChecked(),
            "yetki_silme": self.chk_silme.isChecked(),
            "yetki_goruntuleme": self.chk_goruntuleme.isChecked()
        }
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "EK1_Karar.docx", "Word Documents (*.docx)")
        if out_path:
            try:
                generate_ek1_decision(data, out_path)
                QMessageBox.information(self, t("success"), t("msg_template_success"))
            except Exception as e:
                QMessageBox.critical(self, t("error"), str(e))

    def generate_ek2(self):
        data = {
            "sirket_unvani": self.txt_unvan.text(),
            "bildirim_tarihi": self.txt_tarih.text(),
            "yeni_kullanicilar": [
                {
                    "ad_soyad": self.txt_yetkili_ad.text(),
                    "tckn": self.txt_yetkili_tckn.text(),
                    "eposta": self.txt_yetkili_eposta.text(),
                    "telefon": self.txt_yetkili_tel.text(),
                    "defter_turu": self.txt_defter_turu.text(),
                    "yetki_kapsami": self.get_yetki_kapsami_str()
                }
            ] if self.txt_yetkili_ad.text() else [],
            "kaldırilan_kullanicilar": []
        }
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "EK2_Bildirim.docx", "Word Documents (*.docx)")
        if out_path:
            try:
                generate_ek2_user_notice(data, out_path)
                QMessageBox.information(self, t("success"), t("msg_template_success"))
            except Exception as e:
                QMessageBox.critical(self, t("error"), str(e))

    def setup_tab_pdf_adjust(self):
        layout = QVBoxLayout(self.tab_pdf_adjust)
        
        self.lbl_adjust_pdf = QLabel(t("selected_file", file=t("none_selected")))
        btn_select = QPushButton(t("select_file") + " (PDF / JPG / PNG / DOCX)")
        btn_select.clicked.connect(self.select_adjust_pdf)
        
        self.combo_defter_turu = QComboBox()
        self.combo_defter_turu.addItems(["Yönetim Kurulu Karar Defteri", "Genel Kurul Toplantı ve Müzakere Defteri", "Pay Defteri (Veri Girişi - Form)"])
        
        btn_margin = QPushButton("ETDS Alt Boşluk (Marj) Ekle / Add Margin")
        btn_margin.clicked.connect(self.apply_margin)
        
        # Doğrulama Kodu Bölümü
        group_verify = QGroupBox("Doğrulama Kodu / Verification Code")
        verify_layout = QVBoxLayout()
        btn_verify = QPushButton("Belgeden Kodu Çıkar / Extract Code")
        btn_verify.clicked.connect(self.extract_code)
        self.lbl_code = QLabel("Kod / Code: -")
        self.lbl_code.setTextInteractionFlags(Qt.TextSelectableByMouse)
        verify_layout.addWidget(btn_verify)
        verify_layout.addWidget(self.lbl_code)
        group_verify.setLayout(verify_layout)
        
        layout.addWidget(self.lbl_adjust_pdf)
        layout.addWidget(btn_select)
        layout.addWidget(QLabel("Defter Türü / Book Type:"))
        layout.addWidget(self.combo_defter_turu)
        layout.addWidget(btn_margin)
        layout.addSpacing(20)
        layout.addWidget(group_verify)
        layout.addStretch()
        
        self.adjust_pdf_path = None

    def select_adjust_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, t("select_file"), "", "Desteklenen Dosyalar (*.pdf *.jpg *.jpeg *.png *.docx)")
        if not path:
            return
            
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png']:
            try:
                temp_pdf = os.path.join(os.path.expanduser("~"), "temp_cevirgec_pdf_img.pdf")
                Image.open(path).convert('RGB').save(temp_pdf, "PDF")
                self.adjust_pdf_path = temp_pdf
                self.lbl_adjust_pdf.setText(f"PDF: {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.critical(self, t("error"), f"{e}")
                return
        elif ext == '.docx':
            try:
                temp_pdf = os.path.join(os.path.expanduser("~"), "temp_cevirgec_pdf_docx.pdf")
                docx_to_pdf(os.path.abspath(path), os.path.abspath(temp_pdf))
                self.adjust_pdf_path = temp_pdf
                self.lbl_adjust_pdf.setText(f"PDF: {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.critical(self, t("error"), f"{e}")
                return
        else:
            self.adjust_pdf_path = path
            self.lbl_adjust_pdf.setText(t("selected_file", file=os.path.basename(path)))

    def apply_margin(self):
        if not self.adjust_pdf_path:
            QMessageBox.warning(self, t("warning"), t("please_select_file"))
            return
            
        if "Pay Defteri" in self.combo_defter_turu.currentText():
            QMessageBox.warning(self, t("warning"), "Kapsam Sınırı: Pay Defteri veri girişi (form) ile çalışır.")
            return
            
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
        if out_path:
            try:
                apply_bottom_margin(self.adjust_pdf_path, out_path, margin_pts=115.0)
                QMessageBox.information(self, t("success"), "Marj başarıyla eklendi.")
            except Exception as e:
                QMessageBox.critical(self, t("error"), str(e))

    def extract_code(self):
        if not self.adjust_pdf_path:
            QMessageBox.warning(self, t("warning"), t("please_select_file"))
            return
            
        try:
            doc = open_document(self.adjust_pdf_path)
            try:
                img = render_page(doc, 0, dpi=150)
                code = extract_verification_code(img)
                if code:
                    self.lbl_code.setText(f"Kod: {code}")
                    QMessageBox.information(self, t("info"), f"Doğrulama kodu: {code}")
                else:
                    self.lbl_code.setText("Kod: -")
                    QMessageBox.warning(self, t("warning"), "Kod bulunamadı.")
            finally:
                doc.close()
        except Exception as e:
            QMessageBox.critical(self, t("error"), str(e))

    def setup_tab_legacy_ocr(self):
        layout = QVBoxLayout(self.tab_legacy_ocr)
        
        self.signals = WorkerSignals()
        self.signals.success.connect(lambda msg: QMessageBox.information(self, t("success"), msg))
        self.signals.error.connect(lambda err: QMessageBox.critical(self, t("error"), err))
        self.signals.finished.connect(lambda: self.progress_ocr.setVisible(False))
        
        lbl = QLabel("Eski Defter Dijitalleştirme / Legacy Book Digitization")
        lbl.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(lbl)
        
        self.lbl_legacy_pdf = QLabel(t("selected_file", file=t("none_selected")))
        btn_select = QPushButton(t("select_file"))
        btn_select.clicked.connect(self.select_legacy_pdf)
        
        layout.addWidget(self.lbl_legacy_pdf)
        layout.addWidget(btn_select)
        
        btn_layout = QHBoxLayout()
        btn_word = QPushButton("Akıllı Dönüştür / Convert (Word)")
        btn_word.clicked.connect(lambda: self.run_legacy_convert("word"))
        btn_excel = QPushButton("Akıllı Dönüştür / Convert (Excel)")
        btn_excel.clicked.connect(lambda: self.run_legacy_convert("excel"))
        
        btn_layout.addWidget(btn_word)
        btn_layout.addWidget(btn_excel)
        layout.addLayout(btn_layout)
        
        self.progress_ocr = QProgressBar()
        self.progress_ocr.setRange(0, 0)
        self.progress_ocr.setVisible(False)
        layout.addWidget(self.progress_ocr)
        
        layout.addStretch()
        self.legacy_pdf_path = None

    def select_legacy_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, t("select_file"), "", "PDF Files (*.pdf)")
        if path:
            self.legacy_pdf_path = path
            self.lbl_legacy_pdf.setText(t("selected_file", file=os.path.basename(path)))

    def run_legacy_convert(self, mode):
        if not self.legacy_pdf_path:
            QMessageBox.warning(self, t("warning"), t("please_select_file"))
            return
            
        ext_filter = "Excel Files (*.xlsx)" if mode == "excel" else "Word Documents (*.docx)"
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", ext_filter)
        if not out_path:
            return
            
        self.progress_ocr.setVisible(True)
        
        def task():
            try:
                decisions = analyze_document(self.legacy_pdf_path)
                pipeline = "DIGITAL" if decisions.count("DIGITAL") >= len(decisions) / 2 else "OCR"
                
                if mode == "excel":
                    try:
                        route_to_excel(self.legacy_pdf_path, out_path)
                    except Exception as e:
                        self.signals.error.emit(str(e))
                else:
                    if pipeline == "DIGITAL":
                        convert_digital_pdf_to_word(self.legacy_pdf_path, out_path)
                    else:
                        convert_scanned_pdf_to_word(self.legacy_pdf_path, out_path)
                        
                self.signals.success.emit(f"Dönüşüm tamamlandı! ({pipeline})")
            except Exception as e:
                self.signals.error.emit(str(e))
            finally:
                self.signals.finished.emit()
                
        threading.Thread(target=task, daemon=True).start()

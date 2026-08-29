import os
import threading
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QProgressBar, QMessageBox,
                               QGroupBox, QGridLayout, QFrame, QComboBox)
from PySide6.QtCore import Signal, QObject, Qt
import qtawesome as qta

from core.convert.router import route_to_excel
from core.convert.to_word import convert_digital_pdf_to_word, convert_scanned_pdf_to_word
from core.router import analyze_document
from core.utils.i18n import t

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)
    success = Signal(str)

class DropZone(QFrame):
    clicked = Signal()
    fileDropped = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("DropZone")
        self.setMinimumHeight(140)
        
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        
        self.lbl_icon = QLabel()
        self.lbl_icon.setPixmap(qta.icon("fa5s.cloud-upload-alt", color="#C96442").pixmap(44, 44))
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        
        self.lbl_text = QLabel(t("drop_zone_text"))
        self.lbl_text.setAlignment(Qt.AlignCenter)
        self.lbl_text.setStyleSheet("font-weight: bold; color: #2D2A26;")
        
        self.layout.addWidget(self.lbl_icon)
        self.layout.addWidget(self.lbl_text)
        
    def retranslate_ui(self):
        self.lbl_text.setText(t("drop_zone_text"))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("border: 2px dashed #C96442; background-color: #E2DCD0;")
            
    def dragLeaveEvent(self, event):
        self.setStyleSheet("")
        
    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.fileDropped.emit(file_path)
        self.setStyleSheet("")

class PageConvert(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file_path = None
        
        layout = QVBoxLayout(self)
        
        self.signals = WorkerSignals()
        self.signals.success.connect(self.on_success)
        self.signals.error.connect(self.on_error)
        self.signals.finished.connect(self.on_finished)
        
        # Drop Zone
        self.drop_zone = DropZone(self)
        self.drop_zone.clicked.connect(self.select_file)
        self.drop_zone.fileDropped.connect(self.set_selected_file)
        layout.addWidget(self.drop_zone)
        
        # Selected File Info
        self.lbl_selected = QLabel(t("selected_file", file=t("none_selected")))
        self.lbl_selected.setStyleSheet("font-weight: bold; color: #2D2A26; margin: 8px 0px;")
        layout.addWidget(self.lbl_selected)
        
        # OCR Language Setting Row
        self.row_ocr_lang = QHBoxLayout()
        self.lbl_ocr_lang = QLabel(t("ocr_lang_label"))
        self.lbl_ocr_lang.setStyleSheet("font-weight: bold; color: #5C564D;")
        self.combo_ocr_lang = QComboBox()
        self.combo_ocr_lang.addItem(t("ocr_lang_tr"), "tr")
        self.combo_ocr_lang.addItem(t("ocr_lang_en"), "en")
        self.combo_ocr_lang.addItem(t("ocr_lang_latin"), "latin")
        self.row_ocr_lang.addWidget(self.lbl_ocr_lang)
        self.row_ocr_lang.addWidget(self.combo_ocr_lang)
        self.row_ocr_lang.addStretch()
        layout.addLayout(self.row_ocr_lang)
        
        # --- PDF'den Dışa Aktar ---
        self.group_export = QGroupBox(t("grp_export_pdf"))
        self.grid_export = QGridLayout()
        
        self.btn_pdf_word = QPushButton(t("btn_pdf_to_word"))
        self.btn_pdf_word.clicked.connect(self.pdf_to_word)
        self.grid_export.addWidget(self.btn_pdf_word, 0, 0)
        
        self.btn_pdf_excel = QPushButton(t("btn_pdf_to_excel"))
        self.btn_pdf_excel.clicked.connect(self.pdf_to_excel)
        self.grid_export.addWidget(self.btn_pdf_excel, 0, 1)
        
        self.btn_pdf_md = QPushButton(t("btn_pdf_to_md"))
        self.btn_pdf_md.clicked.connect(lambda: QMessageBox.information(self, t("info"), t("md_info_msg")))
        self.grid_export.addWidget(self.btn_pdf_md, 1, 0)
        
        self.group_export.setLayout(self.grid_export)
        layout.addWidget(self.group_export)
        
        # --- PDF'e İçeri Aktar ---
        self.group_import = QGroupBox(t("grp_import_pdf"))
        self.grid_import = QGridLayout()
        
        self.btn_word_pdf = QPushButton(t("btn_word_to_pdf"))
        self.btn_word_pdf.clicked.connect(self.word_to_pdf)
        self.grid_import.addWidget(self.btn_word_pdf, 0, 0)
        
        self.btn_excel_pdf = QPushButton(t("btn_excel_to_pdf"))
        self.btn_excel_pdf.clicked.connect(self.excel_to_pdf)
        self.grid_import.addWidget(self.btn_excel_pdf, 0, 1)
        
        self.btn_md_pdf = QPushButton(t("btn_md_to_pdf"))
        self.btn_md_pdf.clicked.connect(self.md_to_pdf)
        self.grid_import.addWidget(self.btn_md_pdf, 1, 0)
        
        self.btn_image_pdf = QPushButton(t("btn_image_to_pdf"))
        self.btn_image_pdf.clicked.connect(self.image_to_pdf)
        self.grid_import.addWidget(self.btn_image_pdf, 1, 1)
        
        self.group_import.setLayout(self.grid_import)
        layout.addWidget(self.group_import)
        
        # İlerleme
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        layout.addStretch()
        
        # Hide action groups initially
        self.group_export.setVisible(False)
        self.group_import.setVisible(False)

    def retranslate_ui(self):
        self.drop_zone.retranslate_ui()
        if self.selected_file_path:
            self.lbl_selected.setText(t("selected_file", file=os.path.basename(self.selected_file_path)))
        else:
            self.lbl_selected.setText(t("selected_file", file=t("none_selected")))
            
        self.lbl_ocr_lang.setText(t("ocr_lang_label"))
        curr_ocr = self.combo_ocr_lang.currentData()
        self.combo_ocr_lang.clear()
        self.combo_ocr_lang.addItem(t("ocr_lang_tr"), "tr")
        self.combo_ocr_lang.addItem(t("ocr_lang_en"), "en")
        self.combo_ocr_lang.addItem(t("ocr_lang_latin"), "latin")
        idx = self.combo_ocr_lang.findData(curr_ocr)
        if idx >= 0:
            self.combo_ocr_lang.setCurrentIndex(idx)
            
        self.group_export.setTitle(t("grp_export_pdf"))
        self.btn_pdf_word.setText(t("btn_pdf_to_word"))
        self.btn_pdf_excel.setText(t("btn_pdf_to_excel"))
        self.btn_pdf_md.setText(t("btn_pdf_to_md"))
        
        self.group_import.setTitle(t("grp_import_pdf"))
        self.btn_word_pdf.setText(t("btn_word_to_pdf"))
        self.btn_excel_pdf.setText(t("btn_excel_to_pdf"))
        self.btn_md_pdf.setText(t("btn_md_to_pdf"))
        self.btn_image_pdf.setText(t("btn_image_to_pdf"))

    def get_selected_ocr_lang(self) -> str:
        return self.combo_ocr_lang.currentData() or "tr"

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 
            t("select_file"), 
            "", 
            "Supported Files (*.pdf *.docx *.xlsx *.xls *.md *.txt *.png *.jpg *.jpeg *.bmp *.webp *.tiff *.tif);;All Files (*.*)"
        )
        if path:
            self.set_selected_file(path)

    def set_selected_file(self, path):
        if not path or not os.path.exists(path):
            return
        self.selected_file_path = path
        self.lbl_selected.setText(t("selected_file", file=os.path.basename(path)))
        
        ext = os.path.splitext(path)[1].lower()
        image_exts = ['.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff', '.tif']
        if ext == '.pdf':
            self.group_export.setVisible(True)
            self.group_import.setVisible(False)
            self.btn_pdf_word.setVisible(True)
            self.btn_pdf_excel.setVisible(True)
            self.btn_pdf_md.setVisible(True)
        elif ext in ['.docx', '.doc']:
            self.group_export.setVisible(False)
            self.group_import.setVisible(True)
            self.btn_word_pdf.setVisible(True)
            self.btn_excel_pdf.setVisible(False)
            self.btn_md_pdf.setVisible(False)
            self.btn_image_pdf.setVisible(False)
        elif ext in ['.xlsx', '.xls']:
            self.group_export.setVisible(False)
            self.group_import.setVisible(True)
            self.btn_word_pdf.setVisible(False)
            self.btn_excel_pdf.setVisible(True)
            self.btn_md_pdf.setVisible(False)
            self.btn_image_pdf.setVisible(False)
        elif ext in ['.md', '.txt']:
            self.group_export.setVisible(False)
            self.group_import.setVisible(True)
            self.btn_word_pdf.setVisible(False)
            self.btn_excel_pdf.setVisible(False)
            self.btn_md_pdf.setVisible(True)
            self.btn_image_pdf.setVisible(False)
        elif ext in image_exts:
            self.group_export.setVisible(False)
            self.group_import.setVisible(True)
            self.btn_word_pdf.setVisible(False)
            self.btn_excel_pdf.setVisible(False)
            self.btn_md_pdf.setVisible(False)
            self.btn_image_pdf.setVisible(True)
        else:
            self.group_export.setVisible(False)
            self.group_import.setVisible(False)
            QMessageBox.warning(self, t("unsupported_file"), t("unsupported_file_msg"))
            self.lbl_selected.setText(t("selected_file", file=t("none_selected")))
            self.selected_file_path = None

    def run_in_background(self, task_func):
        self.progress.setVisible(True)
        self.setEnabled(False)
        
        def wrapper():
            try:
                task_func()
            except Exception as e:
                self.signals.error.emit(str(e))
            finally:
                self.signals.finished.emit()
                
        threading.Thread(target=wrapper, daemon=True).start()

    def on_success(self, msg):
        QMessageBox.information(self, t("success"), msg)
        
    def on_error(self, err):
        QMessageBox.critical(self, t("error"), err)
        
    def on_finished(self):
        self.progress.setVisible(False)
        self.setEnabled(True)

    # --- PDF'den ---
    def pdf_to_word(self):
        if not self.selected_file_path: return
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "Word Documents (*.docx)")
        if not out_path: return
        
        ocr_lang = self.get_selected_ocr_lang()
        def task():
            decisions = analyze_document(self.selected_file_path)
            mode = "DIGITAL" if decisions.count("DIGITAL") >= len(decisions) / 2 else "OCR"
            
            if mode == "DIGITAL":
                convert_digital_pdf_to_word(self.selected_file_path, out_path)
                self.signals.success.emit(t("msg_pdf_word_digital"))
            else:
                convert_scanned_pdf_to_word(self.selected_file_path, out_path, lang=ocr_lang)
                self.signals.success.emit(t("msg_pdf_word_ocr"))
            
        self.run_in_background(task)

    def pdf_to_excel(self):
        if not self.selected_file_path: return
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "Excel Files (*.xlsx)")
        if not out_path: return
        
        def task():
            layer_used = route_to_excel(self.selected_file_path, out_path)
            self.signals.success.emit(t("msg_pdf_excel_success", layer=layer_used))
            
        self.run_in_background(task)

    # --- PDF'e ---
    def word_to_pdf(self):
        if not self.selected_file_path: return
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
        if not out_path: return
        
        def task():
            from core.convert.to_pdf import convert_docx_to_pdf
            convert_docx_to_pdf(self.selected_file_path, out_path)
            self.signals.success.emit(t("msg_word_pdf_success"))
            
        self.run_in_background(task)

    def excel_to_pdf(self):
        if not self.selected_file_path: return
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
        if not out_path: return
        
        def task():
            import win32com.client
            import pythoncom
            pythoncom.CoInitialize()
            try:
                excel = win32com.client.Dispatch("Excel.Application")
                excel.Visible = False
                excel.DisplayAlerts = False
                
                wb = excel.Workbooks.Open(os.path.abspath(self.selected_file_path))
                wb.ExportAsFixedFormat(0, os.path.abspath(out_path))
                wb.Close(False)
                excel.Quit()
                self.signals.success.emit(t("msg_excel_pdf_success"))
            finally:
                pythoncom.CoUninitialize()
                
        self.run_in_background(task)

    def md_to_pdf(self):
        if not self.selected_file_path: return
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
        if not out_path: return
        
        def task():
            import markdown
            from PySide6.QtGui import QTextDocument
            from PySide6.QtPrintSupport import QPrinter
            
            with open(self.selected_file_path, 'r', encoding='utf-8') as f:
                md_text = f.read()
                
            html = markdown.markdown(md_text, extensions=['extra', 'tables'])
            
            doc = QTextDocument()
            doc.setHtml(html)
            
            printer = QPrinter()
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(out_path)
            
            doc.print_(printer)
            self.signals.success.emit(t("msg_md_pdf_success"))
            
        try:
            task()
        except Exception as e:
            self.on_error(str(e))

    def image_to_pdf(self):
        if not self.selected_file_path: return
        out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
        if not out_path: return
        
        def task():
            from core.convert.to_pdf import convert_image_to_pdf
            convert_image_to_pdf(self.selected_file_path, out_path)
            self.signals.success.emit(t("msg_image_pdf_success"))
            
        self.run_in_background(task)

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QStackedWidget, QPushButton, QFrame, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from ui.theme import GLOBAL_STYLESHEET
from core.utils.timing import time_it
from core.utils.resources import resource_path

from ui.pages.page_image import PageImage
from ui.pages.page_notepad import PageNotepad
from ui.pages.page_pdf_tools import PagePdfTools
from ui.pages.page_security import PageSecurity
from ui.pages.page_signature import PageSignature
from ui.pages.page_etds import PageEtds
from ui.pages.page_convert import PageConvert
from ui.pages.page_watermark import PageWatermark

import qtawesome as qta
import ctypes

try:
    myappid = 'cevirgecpdf.app.v2'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

class MainWindow(QMainWindow):
    @time_it("MainWindow Init")
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Çevirgeç PDF V.2.0")
        self.setWindowIcon(QIcon(resource_path("assets/icons/app_icon.png")))
        self.resize(1000, 700)
        self.setStyleSheet(GLOBAL_STYLESHEET)
        self.setAcceptDrops(True)
        
        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self._setup_sidebar()
        self._setup_pages()
        
        # Select first menu item
        self.menu_buttons[0].setChecked(True)
        self.stack.setCurrentIndex(0)

    def _setup_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("MenuFrame")
        self.sidebar.setFixedWidth(220)
        
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 20, 0, 0)
        self.sidebar_layout.setSpacing(5)
        
        # Logo + Title Area
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(20, 0, 10, 20)
        
        title_label = QLabel("ÇEVİRGEÇ PDF")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #C96442;")
        
        logo_layout.addWidget(title_label)
        logo_layout.addStretch()
        
        # Add a wrapper widget to apply margins
        logo_wrapper = QWidget()
        logo_wrapper.setLayout(logo_layout)
        self.sidebar_layout.addWidget(logo_wrapper)
        
        self.menu_buttons = []
        menus = [
            ("PDF Dönüştür", 0, "fa5s.sync"),
            ("PDF Araçları", 1, "fa5s.file-pdf"),
            ("Güvenlik & KVKK", 2, "fa5s.shield-alt"),
            ("ETDS Modülü", 3, "fa5s.book"),
            ("Filigran", 4, "fa5s.tint"),
            ("İmza", 5, "fa5s.signature"),
            ("Görsel İşlemleri", 6, "fa5s.image"),
            ("Not Defteri", 7, "fa5s.edit")
        ]
        
        for text, index, icon_name in menus:
            btn = QPushButton(text)
            btn.setObjectName("MenuButton")
            btn.setCheckable(True)
            # Apply icon using qtawesome (new palette)
            icon = qta.icon(icon_name, color="#2D2A26", color_active="#C96442")
            btn.setIcon(icon)
            btn.clicked.connect(lambda checked, idx=index: self._switch_page(idx))
            self.sidebar_layout.addWidget(btn)
            self.menu_buttons.append(btn)
            
        self.sidebar_layout.addStretch()
        
        footer_label = QLabel("© 2026 Burak Tekiner")
        footer_label.setStyleSheet("color: #888888; font-size: 11px;")
        footer_label.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(footer_label)
        
        self.main_layout.addWidget(self.sidebar)

    def _setup_pages(self):
        self.stack = QStackedWidget()
        
        # Add Pages (Indices match the menu)
        self.stack.addWidget(PageConvert())                                  # 0
        self.stack.addWidget(PagePdfTools())                                 # 1
        self.stack.addWidget(PageSecurity())                                 # 2
        self.stack.addWidget(PageEtds())                                     # 3
        self.stack.addWidget(PageWatermark())                                # 4
        self.stack.addWidget(PageSignature())                                # 5
        self.stack.addWidget(PageImage())                                    # 6
        self.stack.addWidget(PageNotepad())                                  # 7
        
        self.main_layout.addWidget(self.stack)

    def _switch_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.menu_buttons):
            btn.setChecked(i == index)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.handle_file(file_path)

    def handle_file(self, file_path):
        import os
        if not file_path or not os.path.exists(file_path):
            return
            
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.pdf', '.docx', '.doc', '.xlsx', '.xls']:
            self._switch_page(0)  # 0: PageConvert
            page_convert = self.stack.widget(0)
            page_convert.set_selected_file(file_path)
        elif ext in ['.md', '.txt']:
            self._switch_page(7)  # 7: PageNotepad
            page_notepad = self.stack.widget(7)
            page_notepad.load_file(file_path)

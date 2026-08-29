from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QStackedWidget, QPushButton, QFrame, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from ui.theme import GLOBAL_STYLESHEET
from core.utils.timing import time_it
from core.utils.resources import resource_path
from core.utils.i18n import t, get_language, toggle_language, add_language_listener

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
        self.setWindowTitle(t("app_title"))
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
        
        # Register for i18n language updates
        add_language_listener(self.on_language_changed)

    def _get_menu_defs(self):
        return [
            ("nav_convert", 0, "fa5s.sync"),
            ("nav_pdf_tools", 1, "fa5s.file-pdf"),
            ("nav_security", 2, "fa5s.shield-alt"),
            ("nav_etds", 3, "fa5s.book"),
            ("nav_watermark", 4, "fa5s.tint"),
            ("nav_signature", 5, "fa5s.signature"),
            ("nav_image", 6, "fa5s.image"),
            ("nav_notepad", 7, "fa5s.edit")
        ]

    def _setup_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("MenuFrame")
        self.sidebar.setFixedWidth(220)
        
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 20, 0, 10)
        self.sidebar_layout.setSpacing(5)
        
        # Logo + Title Area
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(20, 0, 10, 20)
        
        self.title_label = QLabel(t("app_brand"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #C96442;")
        
        logo_layout.addWidget(self.title_label)
        logo_layout.addStretch()
        
        # Add a wrapper widget to apply margins
        logo_wrapper = QWidget()
        logo_wrapper.setLayout(logo_layout)
        self.sidebar_layout.addWidget(logo_wrapper)
        
        self.menu_buttons = []
        menus = self._get_menu_defs()
        
        for key, index, icon_name in menus:
            btn = QPushButton(t(key))
            btn.setObjectName("MenuButton")
            btn.setCheckable(True)
            btn.setProperty("i18n_key", key)
            # Apply icon using qtawesome
            icon = qta.icon(icon_name, color="#2D2A26", color_active="#C96442")
            btn.setIcon(icon)
            btn.clicked.connect(lambda checked, idx=index: self._switch_page(idx))
            self.sidebar_layout.addWidget(btn)
            self.menu_buttons.append(btn)
            
        self.sidebar_layout.addStretch()
        
        # Language Switcher & Controls at bottom
        lang_layout = QHBoxLayout()
        lang_layout.setContentsMargins(15, 0, 15, 5)
        
        self.btn_lang = QPushButton(self._get_lang_btn_text())
        self.btn_lang.setObjectName("LangSwitchButton")
        self.btn_lang.setToolTip(t("lang_switch_tooltip"))
        self.btn_lang.setStyleSheet("""
            QPushButton#LangSwitchButton {
                background-color: #EDE9E0;
                color: #2D2A26;
                border: 1px solid #D6CEBE;
                border-radius: 6px;
                padding: 5px 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton#LangSwitchButton:hover {
                background-color: #DFD9CD;
                border-color: #C96442;
                color: #C96442;
            }
        """)
        self.btn_lang.clicked.connect(self._toggle_app_language)
        lang_layout.addWidget(self.btn_lang)
        self.sidebar_layout.addLayout(lang_layout)
        
        self.footer_label = QLabel(t("footer_credits"))
        self.footer_label.setStyleSheet("color: #888888; font-size: 11px;")
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(self.footer_label)
        
        self.main_layout.addWidget(self.sidebar)

    def _get_lang_btn_text(self) -> str:
        current = get_language()
        return "🌐 Dil: Türkçe" if current == "tr" else "🌐 Lang: English"

    def _toggle_app_language(self):
        toggle_language()

    def on_language_changed(self, lang: str):
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(t("app_title"))
        self.title_label.setText(t("app_brand"))
        self.btn_lang.setText(self._get_lang_btn_text())
        self.btn_lang.setToolTip(t("lang_switch_tooltip"))
        self.footer_label.setText(t("footer_credits"))
        
        # Retranslate menu buttons
        for btn in self.menu_buttons:
            key = btn.property("i18n_key")
            if key:
                btn.setText(t(key))
                
        # Retranslate stacked pages
        for i in range(self.stack.count()):
            widget = self.stack.widget(i)
            if hasattr(widget, "retranslate_ui"):
                try:
                    widget.retranslate_ui()
                except Exception:
                    pass

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
        if ext in ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff', '.tif']:
            self._switch_page(0)  # 0: PageConvert
            page_convert = self.stack.widget(0)
            page_convert.set_selected_file(file_path)
        elif ext in ['.md', '.txt']:
            self._switch_page(7)  # 7: PageNotepad
            page_notepad = self.stack.widget(7)
            page_notepad.load_file(file_path)

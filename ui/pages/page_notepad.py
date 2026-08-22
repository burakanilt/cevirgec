import os
import markdown
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, 
                               QTextBrowser, QSplitter, QPushButton, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt

class PageNotepad(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_file = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Üst Menü
        toolbar = QHBoxLayout()
        btn_new = QPushButton("Yeni")
        btn_new.clicked.connect(self.new_file)
        
        btn_open = QPushButton("Aç")
        btn_open.clicked.connect(self.open_file)
        
        btn_save = QPushButton("Kaydet")
        btn_save.clicked.connect(self.save_file)
        
        btn_export = QPushButton("MD Olarak Dışa Aktar")
        btn_export.clicked.connect(self.export_file)
        
        toolbar.addWidget(btn_new)
        toolbar.addWidget(btn_open)
        toolbar.addWidget(btn_save)
        toolbar.addWidget(btn_export)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Bölünmüş Ekran (Splitter)
        splitter = QSplitter(Qt.Horizontal)
        
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Markdown formatında yazmaya başlayın...")
        self.editor.textChanged.connect(self.update_preview)
        
        self.preview = QTextBrowser()
        self.preview.setOpenExternalLinks(True)
        
        splitter.addWidget(self.editor)
        splitter.addWidget(self.preview)
        splitter.setSizes([500, 500])
        
        layout.addWidget(splitter)
        
        # Otomatik kaydetme / kurtarma
        self.save_dir = os.path.expanduser("~/.cevirgec_pdf/notes")
        os.makedirs(self.save_dir, exist_ok=True)
        self.backup_path = os.path.join(self.save_dir, "notepad_backup.md")
        
        self.load_backup()

    def update_preview(self):
        text = self.editor.toPlainText()
        html = markdown.markdown(text, extensions=['extra', 'tables', 'fenced_code'])
        # Add basic styling to make it look nice
        styled_html = f"""
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; font-size: 14px; color: #2D2A26; }}
            h1, h2, h3 {{ color: #C96442; }}
            code {{ background-color: #EDE9E0; padding: 2px 4px; border-radius: 4px; }}
            pre {{ background-color: #EDE9E0; padding: 10px; border-radius: 6px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #D6CEBE; padding: 8px; text-align: left; }}
            th {{ background-color: #EDE9E0; }}
            blockquote {{ border-left: 4px solid #C96442; margin-left: 0; padding-left: 10px; color: #5C564D; }}
        </style>
        {html}
        """
        self.preview.setHtml(styled_html)
        
        # Backup automatically
        try:
            with open(self.backup_path, "w", encoding="utf-8") as f:
                f.write(text)
        except:
            pass

    def load_backup(self):
        if os.path.exists(self.backup_path):
            try:
                with open(self.backup_path, "r", encoding="utf-8") as f:
                    self.editor.setPlainText(f.read())
            except:
                pass

    def new_file(self):
        self.editor.clear()
        self.current_file = None

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Aç", "", "Markdown Files (*.md);;Text Files (*.txt);;All Files (*.*)")
        if path:
            self.load_file(path)

    def load_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.setPlainText(f.read())
            self.current_file = path
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(self.editor.toPlainText())
                QMessageBox.information(self, "Başarılı", "Kaydedildi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))
        else:
            self.save_file_as()

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Kaydet", "", "Text Files (*.txt);;All Files (*.*)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.editor.toPlainText())
                self.current_file = path
                QMessageBox.information(self, "Başarılı", "Dosya başarıyla kaydedildi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

    def export_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "MD Olarak Dışa Aktar", "", "Markdown Files (*.md)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.editor.toPlainText())
                QMessageBox.information(self, "Başarılı", "Dosya başarıyla Markdown olarak dışa aktarıldı.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

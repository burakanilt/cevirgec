from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent

class DropZone(QWidget):
    # Signal emitted when a valid PDF file is dropped
    file_dropped = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("PDF dosyasını buraya sürükleyin veya tıklayıp seçin", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 20px;
                background-color: #f9f9f9;
                color: #555;
            }
        """)
        layout.addWidget(self.label)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            # Check if any URL is a PDF
            for url in event.mimeData().urls():
                if url.isLocalFile() and url.toLocalFile().lower().endswith('.pdf'):
                    event.acceptProposedAction()
                    self.label.setStyleSheet("""
                        QLabel {
                            border: 2px dashed #4CAF50;
                            border-radius: 10px;
                            padding: 20px;
                            background-color: #e8f5e9;
                            color: #2E7D32;
                        }
                    """)
                    return
        event.ignore()
        
    def dragLeaveEvent(self, event):
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 20px;
                background-color: #f9f9f9;
                color: #555;
            }
        """)
        super().dragLeaveEvent(event)
        
    def dropEvent(self, event: QDropEvent):
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 20px;
                background-color: #f9f9f9;
                color: #555;
            }
        """)
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.pdf'):
                    self.file_dropped.emit(file_path)
                    break # Just process the first valid PDF for now

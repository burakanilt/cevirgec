from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
from PIL import Image

class PDFPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.preview_label = QLabel("PDF Önizlemesi Yok", self)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #e0e0e0; border: 1px solid #ccc;")
        layout.addWidget(self.preview_label)
        
        self.current_pdf_path = None
        self.current_page = 0
        
    def load_pdf(self, pdf_path: str, page_num: int = 0):
        """
        Renders the PDF page using core.pdf_backend and displays it.
        """
        from core.pdf_backend import open_document, render_page
        self.current_pdf_path = pdf_path
        self.current_page = page_num
        
        doc = open_document(pdf_path)
        try:
            # We use a lower DPI for preview to keep it fast
            img_pil = render_page(doc, page_num, dpi=72)
            
            # Convert PIL image to QPixmap
            # Ensure it's in a format QImage can understand
            if img_pil.mode != "RGBA":
                img_pil = img_pil.convert("RGBA")
                
            data = img_pil.tobytes("raw", "RGBA")
            qim = QImage(data, img_pil.width, img_pil.height, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qim)
            
            # Scale to fit while keeping aspect ratio
            # Actually, keeping it as is or letting the layout scale it
            self.preview_label.setPixmap(pixmap.scaled(
                self.preview_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))
        except Exception as e:
            self.preview_label.setText(f"Önizleme Yüklenemedi:\n{str(e)}")
        finally:
            doc.close()
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Re-render or just let it scale. Since we rendered to QPixmap, we might want to scale the original pixmap.
        # But this is just a skeleton for now.
        pass

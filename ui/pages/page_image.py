import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QSpinBox, QComboBox, 
                               QGroupBox, QMessageBox, QCheckBox)
from core.convert.image_ops import advanced_image_process

class PageImage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.img_path = None
        
        layout = QVBoxLayout(self)
        
        # File Selection
        self.lbl_img = QLabel("Seçilen Görsel: Yok")
        btn_img = QPushButton("Görsel Seç")
        btn_img.clicked.connect(self.select_img)
        
        layout.addWidget(self.lbl_img)
        layout.addWidget(btn_img)
        
        # Settings
        group = QGroupBox("Görsel Ayarları")
        g_layout = QVBoxLayout()
        
        # Resize
        row_size = QHBoxLayout()
        row_size.addWidget(QLabel("Genişlik (Boşsa oran korunur):"))
        self.spin_w = QSpinBox(); self.spin_w.setMaximum(99999); self.spin_w.setValue(0)
        row_size.addWidget(self.spin_w)
        row_size.addWidget(QLabel("Yükseklik:"))
        self.spin_h = QSpinBox(); self.spin_h.setMaximum(99999); self.spin_h.setValue(0)
        row_size.addWidget(self.spin_h)
        g_layout.addLayout(row_size)
        
        # Format
        row_fmt = QHBoxLayout()
        row_fmt.addWidget(QLabel("Çıktı Formatı:"))
        self.combo_fmt = QComboBox()
        self.combo_fmt.addItems(["PNG", "JPEG"])
        row_fmt.addWidget(self.combo_fmt)
        g_layout.addLayout(row_fmt)
        
        # Color Mode
        row_color = QHBoxLayout()
        row_color.addWidget(QLabel("Renk Uzayı:"))
        self.combo_color = QComboBox()
        self.combo_color.addItems(["RGB", "RGBA", "Grayscale"])
        row_color.addWidget(self.combo_color)
        g_layout.addLayout(row_color)
        
        # Padding Option
        self.chk_padding = QCheckBox("Oranı Koru ve Boşlukları Doldur (Padding)")
        self.chk_padding.setChecked(True)
        g_layout.addWidget(self.chk_padding)
        
        # Smart Scan Option
        self.chk_smart_scan = QCheckBox("Akıllı Tarama (Otomatik Yön Düzeltme)")
        self.chk_smart_scan.setChecked(False)
        g_layout.addWidget(self.chk_smart_scan)
        
        # DPI
        row_dpi = QHBoxLayout()
        row_dpi.addWidget(QLabel("DPI (Örn: 300, 72):"))
        self.spin_dpi = QSpinBox(); self.spin_dpi.setMinimum(10); self.spin_dpi.setMaximum(1200); self.spin_dpi.setValue(300)
        row_dpi.addWidget(self.spin_dpi)
        g_layout.addLayout(row_dpi)
        
        group.setLayout(g_layout)
        layout.addWidget(group)
        
        btn_apply = QPushButton("Uygula ve Kaydet")
        btn_apply.clicked.connect(self.do_apply)
        layout.addWidget(btn_apply)
        
        layout.addStretch()

    def select_img(self):
        path, _ = QFileDialog.getOpenFileName(self, "Görsel Seç", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.img_path = path
            self.lbl_img.setText(f"Seçilen Görsel: {os.path.basename(path)}")

    def do_apply(self):
        if not self.img_path:
            QMessageBox.warning(self, "Hata", "Lütfen bir görsel seçin.")
            return
            
        fmt = self.combo_fmt.currentText()
        out_path, _ = QFileDialog.getSaveFileName(self, "Farklı Kaydet", "", f"{fmt} Files (*.{fmt.lower()})")
        if not out_path:
            return
            
        try:
            w = self.spin_w.value()
            h = self.spin_h.value()
            dpi_val = self.spin_dpi.value()
            color_mode = self.combo_color.currentText()
            pad_image = self.chk_padding.isChecked()
            do_smart_scan = self.chk_smart_scan.isChecked()
            
            advanced_image_process(
                input_path=self.img_path,
                output_path=out_path,
                width=w,
                height=h,
                dpi=dpi_val,
                color_mode=color_mode,
                pad_image=pad_image,
                smart_scan=do_smart_scan
            )
            
            QMessageBox.information(self, "Başarılı", "Görsel başarıyla dönüştürüldü.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QSpinBox, QComboBox, 
                               QGroupBox, QMessageBox, QCheckBox)
from core.convert.image_ops import advanced_image_process
from core.utils.i18n import t

class PageImage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.img_path = None
        
        layout = QVBoxLayout(self)
        
        # File Selection
        self.lbl_img = QLabel(t("selected_file", file=t("none_selected")))
        self.btn_img = QPushButton(t("select_file"))
        self.btn_img.clicked.connect(self.select_img)
        
        layout.addWidget(self.lbl_img)
        layout.addWidget(self.btn_img)
        
        # Settings
        self.group = QGroupBox(t("grp_image_settings"))
        g_layout = QVBoxLayout()
        
        # Resize
        row_size = QHBoxLayout()
        self.lbl_w = QLabel(t("lbl_width"))
        self.spin_w = QSpinBox(); self.spin_w.setMaximum(99999); self.spin_w.setValue(0)
        row_size.addWidget(self.lbl_w)
        row_size.addWidget(self.spin_w)
        
        self.lbl_h = QLabel(t("lbl_height"))
        self.spin_h = QSpinBox(); self.spin_h.setMaximum(99999); self.spin_h.setValue(0)
        row_size.addWidget(self.lbl_h)
        row_size.addWidget(self.spin_h)
        g_layout.addLayout(row_size)
        
        # Format
        row_fmt = QHBoxLayout()
        self.lbl_fmt = QLabel(t("lbl_output_format"))
        self.combo_fmt = QComboBox()
        self.combo_fmt.addItems(["PNG", "JPEG", "PDF"])
        row_fmt.addWidget(self.lbl_fmt)
        row_fmt.addWidget(self.combo_fmt)
        g_layout.addLayout(row_fmt)
        
        # Color Mode
        row_color = QHBoxLayout()
        self.lbl_color = QLabel(t("lbl_color_mode"))
        self.combo_color = QComboBox()
        self.combo_color.addItems(["RGB", "RGBA", "Grayscale"])
        row_color.addWidget(self.lbl_color)
        row_color.addWidget(self.combo_color)
        g_layout.addLayout(row_color)
        
        # Padding Option
        self.chk_padding = QCheckBox(t("chk_pad_image"))
        self.chk_padding.setChecked(True)
        g_layout.addWidget(self.chk_padding)
        
        # Smart Scan Option
        self.chk_smart_scan = QCheckBox(t("chk_smart_scan"))
        self.chk_smart_scan.setChecked(False)
        g_layout.addWidget(self.chk_smart_scan)
        
        # DPI
        row_dpi = QHBoxLayout()
        self.lbl_dpi = QLabel(t("lbl_dpi"))
        self.spin_dpi = QSpinBox(); self.spin_dpi.setMinimum(10); self.spin_dpi.setMaximum(1200); self.spin_dpi.setValue(300)
        row_dpi.addWidget(self.lbl_dpi)
        row_dpi.addWidget(self.spin_dpi)
        g_layout.addLayout(row_dpi)
        
        self.group.setLayout(g_layout)
        layout.addWidget(self.group)
        
        self.btn_apply = QPushButton(t("btn_apply_image"))
        self.btn_apply.clicked.connect(self.do_apply)
        layout.addWidget(self.btn_apply)
        
        layout.addStretch()

    def retranslate_ui(self):
        if self.img_path:
            self.lbl_img.setText(t("selected_file", file=os.path.basename(self.img_path)))
        else:
            self.lbl_img.setText(t("selected_file", file=t("none_selected")))
            
        self.btn_img.setText(t("select_file"))
        self.group.setTitle(t("grp_image_settings"))
        self.lbl_w.setText(t("lbl_width"))
        self.lbl_h.setText(t("lbl_height"))
        self.lbl_fmt.setText(t("lbl_output_format"))
        self.lbl_color.setText(t("lbl_color_mode"))
        self.chk_padding.setText(t("chk_pad_image"))
        self.chk_smart_scan.setText(t("chk_smart_scan"))
        self.lbl_dpi.setText(t("lbl_dpi"))
        self.btn_apply.setText(t("btn_apply_image"))

    def select_img(self):
        path, _ = QFileDialog.getOpenFileName(self, t("select_file"), "", "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.tif);;All Files (*.*)")
        if path:
            self.img_path = path
            self.lbl_img.setText(t("selected_file", file=os.path.basename(path)))

    def do_apply(self):
        if not self.img_path:
            QMessageBox.warning(self, t("warning"), t("please_select_file"))
            return
            
        fmt = self.combo_fmt.currentText()
        if fmt.upper() == "PDF":
            out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", "PDF Files (*.pdf)")
        else:
            out_path, _ = QFileDialog.getSaveFileName(self, t("save_as"), "", f"{fmt} Files (*.{fmt.lower()})")
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
            
            QMessageBox.information(self, t("success"), t("msg_image_success"))
        except Exception as e:
            QMessageBox.critical(self, t("error"), str(e))

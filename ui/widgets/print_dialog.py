from PySide6.QtWidgets import (QDialog, QHBoxLayout, QVBoxLayout, QFormLayout, QComboBox,
                               QSpinBox, QRadioButton, QPushButton, QLabel, QWidget)
from PySide6.QtGui import QPageLayout
from PySide6.QtPrintSupport import QPrinter, QPrinterInfo, QPrintPreviewWidget


class PrintDialog(QDialog):
    """Yazdırma ayarları + canlı önizlemenin aynı kutuda olduğu yazdırma penceresi."""

    def __init__(self, page_count, paint_callback, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yazdır")
        self.resize(1000, 700)
        self.page_count = page_count
        self.paint_callback = paint_callback

        self.printer = QPrinter(QPrinter.HighResolution)

        root = QHBoxLayout(self)

        # --- Sol: ayarlar ---
        left = QWidget()
        left.setFixedWidth(280)
        lv = QVBoxLayout(left)
        form = QFormLayout()

        self.cmb_printer = QComboBox()
        names = QPrinterInfo.availablePrinterNames()
        self.cmb_printer.addItems(names)
        default = QPrinterInfo.defaultPrinterName()
        if default in names:
            self.cmb_printer.setCurrentText(default)
        form.addRow("Yazıcı:", self.cmb_printer)

        self.cmb_orient = QComboBox()
        self.cmb_orient.addItems(["Dikey", "Yatay"])
        form.addRow("Yönlendirme:", self.cmb_orient)

        self.spin_copies = QSpinBox()
        self.spin_copies.setRange(1, 99)
        form.addRow("Kopya:", self.spin_copies)
        lv.addLayout(form)

        lv.addWidget(QLabel("Sayfalar:"))
        self.rb_all = QRadioButton(f"Tümü ({page_count} sayfa)")
        self.rb_all.setChecked(True)
        self.rb_range = QRadioButton("Aralık:")
        lv.addWidget(self.rb_all)
        lv.addWidget(self.rb_range)
        rng = QHBoxLayout()
        self.spin_from = QSpinBox()
        self.spin_to = QSpinBox()
        for s in (self.spin_from, self.spin_to):
            s.setRange(1, page_count)
        self.spin_to.setValue(page_count)
        rng.addWidget(self.spin_from)
        rng.addWidget(QLabel("-"))
        rng.addWidget(self.spin_to)
        lv.addLayout(rng)
        lv.addStretch()

        btns = QHBoxLayout()
        self.btn_print = QPushButton("Yazdır")
        self.btn_print.setDefault(True)
        self.btn_cancel = QPushButton("İptal")
        btns.addWidget(self.btn_print)
        btns.addWidget(self.btn_cancel)
        lv.addLayout(btns)
        root.addWidget(left)

        # --- Sağ: önizleme ---
        self.preview = QPrintPreviewWidget(self.printer)
        self.preview.paintRequested.connect(self._paint_preview)
        root.addWidget(self.preview, 1)

        self.cmb_printer.currentTextChanged.connect(self._on_printer_changed)
        self.cmb_orient.currentIndexChanged.connect(self._on_orient_changed)
        self.rb_all.toggled.connect(self._refresh)
        self.rb_range.toggled.connect(self.spin_from.setEnabled)
        self.rb_range.toggled.connect(self.spin_to.setEnabled)
        self.spin_from.setEnabled(False)
        self.spin_to.setEnabled(False)
        self.spin_from.valueChanged.connect(self._refresh)
        self.spin_to.valueChanged.connect(self._refresh)
        self.btn_print.clicked.connect(self._do_print)
        self.btn_cancel.clicked.connect(self.reject)

        if names:
            self.printer.setPrinterName(self.cmb_printer.currentText())

    def _range(self):
        if self.rb_all.isChecked():
            return 1, self.page_count
        a, b = self.spin_from.value(), self.spin_to.value()
        return min(a, b), max(a, b)

    def _paint_preview(self, printer):
        first, last = self._range()
        last = min(last, first + 29)  # büyük belgelerde önizleme hızlı kalsın
        self.paint_callback(printer, first, last, 90)

    def _refresh(self, *_):
        self.preview.updatePreview()

    def _on_printer_changed(self, name):
        if name:
            self.printer.setPrinterName(name)
        self.preview.updatePreview()

    def _on_orient_changed(self, idx):
        orient = QPageLayout.Portrait if idx == 0 else QPageLayout.Landscape
        self.printer.setPageOrientation(orient)
        self.preview.updatePreview()

    def showEvent(self, e):
        super().showEvent(e)
        self.preview.fitToWidth()

    def _do_print(self):
        first, last = self._range()
        self.printer.setCopyCount(self.spin_copies.value())
        self.paint_callback(self.printer, first, last)
        self.accept()

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow
from core.utils.logging import logger
from core.utils.timing import time_it
from core.utils.resources import resource_path

@time_it("Uygulama Açılışı")
def main():
    app = QApplication(sys.argv)
    
    icon_path = resource_path("assets/icons/app_icon.png")
    app.setWindowIcon(QIcon(icon_path))
    
    # We can measure setup time
    window = MainWindow()
    window.setWindowIcon(QIcon(icon_path))
    window.show()
    
    logger.info("Uygulama başlatıldı.")
    return app, window

if __name__ == "__main__":
    if "--test-ocr" in sys.argv:
        try:
            # Format: app.py --test-ocr <pdf_path> <out_path>
            idx = sys.argv.index("--test-ocr")
            pdf_path = sys.argv[idx + 1]
            out_path = sys.argv[idx + 2]
            print(f"CLI OCR Test: Converting {pdf_path} -> {out_path}")
            from core.convert.to_word import convert_scanned_pdf_to_word
            convert_scanned_pdf_to_word(pdf_path, out_path)
            print("CLI OCR Test: Conversion successful!")
            sys.exit(0)
        except Exception as e:
            import traceback
            print(f"CLI OCR Test Error: {e}")
            traceback.print_exc()
            sys.exit(1)
            
    if "--test-excel" in sys.argv:
        try:
            idx = sys.argv.index("--test-excel")
            pdf_path = sys.argv[idx + 1]
            out_path = sys.argv[idx + 2]
            print(f"CLI Excel Test: Converting {pdf_path} -> {out_path}")
            from core.convert.router import route_to_excel
            layer = route_to_excel(pdf_path, out_path)
            print(f"CLI Excel Test: Conversion successful using {layer}")
            sys.exit(0)
        except Exception as e:
            import traceback
            print(f"CLI Excel Test Error: {e}")
            traceback.print_exc()
            sys.exit(1)
            
    original_argv = sys.argv.copy()
    app, window = main()
    
    import os
    logger.info(f"App started with args: {original_argv}")
    if len(original_argv) > 1:
        for arg in original_argv[1:]:
            logger.info(f"Checking argument: {arg}")
            if not arg.startswith("--"):
                if os.path.exists(arg) and os.path.isfile(arg):
                    logger.info(f"Valid file found, handling: {arg}")
                    window.handle_file(arg)
                    break
                else:
                    logger.warning(f"Argument is not a valid file: {arg}")
                
    sys.exit(app.exec())

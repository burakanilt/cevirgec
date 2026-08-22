import os
import time
from PySide6.QtWidgets import QApplication

from core.signature import extract_signature, add_signature_to_pdf
from core.watermark import add_watermark, remove_watermark
from ui.pages.page_notepad import PageNotepad
from PIL import Image, ImageDraw

OUTPUT_DIR = "tests/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test_signature():
    print("=== TEST 1: İmza Temizleme ve Ekleme ===")
    
    # 1. Create a dummy image with shadow (simulating phone photo)
    sig_photo = os.path.join(OUTPUT_DIR, "dummy_sig_photo.jpg")
    img = Image.new('L', (400, 200), color=220) # grayish background (shadow)
    draw = ImageDraw.Draw(img)
    # Draw some dark text/signature
    draw.text((150, 80), "Benim Imzam", fill=30, align="center")
    # Add some lighter shadow part to test Otsu
    draw.rectangle([0,0, 150, 200], fill=170)
    img.save(sig_photo)
    print("Oluşturuldu: Gölgeli imza fotoğrafı.")
    
    # 2. Extract signature
    clean_sig = os.path.join(OUTPUT_DIR, "temiz_imza.png")
    extract_signature(sig_photo, clean_sig)
    print("Otsu algoritması ile temiz şeffaf PNG çıkarıldı.")
    
    # 3. Add to a dummy PDF
    pdf_in = "tests/samples/dummy.pdf"
    if not os.path.exists(pdf_in):
        # Fallback to another small pdf
        pdf_in = "tests/samples/1_modern.pdf"
    
    pdf_out = os.path.join(OUTPUT_DIR, "imzali_sonuc.pdf")
    
    if os.path.exists(pdf_in):
        add_signature_to_pdf(pdf_in, clean_sig, page_num=0, rect=(100, 100, 300, 200), out_path=pdf_out)
        print(f"Başarılı! İmza dosyaya eklendi: {pdf_out}")
    else:
        print("HATA: Test için kullanılacak PDF bulunamadı!")


def test_watermark():
    print("\n=== TEST 2: Filigran Ekleme ve Kaldırma ===")
    
    pdf_in = "tests/samples/dummy.pdf"
    if not os.path.exists(pdf_in):
        pdf_in = "tests/samples/1_modern.pdf"
        
    if not os.path.exists(pdf_in):
        print("HATA: Test için kullanılacak PDF bulunamadı!")
        return
        
    pdf_with_wm = os.path.join(OUTPUT_DIR, "watermark_eklenmis.pdf")
    pdf_clean = os.path.join(OUTPUT_DIR, "watermark_temizlenmis.pdf")
    
    # 1. Add Watermark
    add_watermark(pdf_in, pdf_with_wm, text="GİZLİ")
    print(f"Filigran eklendi: {pdf_with_wm}")
    
    # 2. Remove Watermark
    remove_watermark(pdf_with_wm, pdf_clean)
    print(f"Filigran kaldırıldı: {pdf_clean}")
    
    # 3. Test exception on flattened watermark (or PDF without our OCG)
    print("Düzleştirilmiş (veya OCG olmayan) PDF üzerinde kaldırma testi:")
    try:
        remove_watermark(pdf_in, os.path.join(OUTPUT_DIR, "hata_testi.pdf"))
    except ValueError as e:
        print(f"Beklenen hata yakalandı: {e}")


def test_notepad():
    print("\n=== TEST 3: Not Defteri Kayıt Testi ===")
    
    # We need a QApplication instance to create QWidgets
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        
    notepad = PageNotepad()
    
    # Simulate user input
    test_text = f"Otomatik kayıt testi: {time.time()}"
    notepad.text_edit.setPlainText(test_text)
    
    print("Metin girildi. Otomatik kayıt (auto_save) tetikleniyor...")
    # Manually trigger the slot to avoid waiting 5 seconds in tests
    notepad.auto_save()
    
    # Verify file
    save_path = os.path.expanduser("~/.cevirgec2/notes/notepad_backup.txt")
    if os.path.exists(save_path):
        with open(save_path, "r", encoding="utf-8") as f:
            saved_content = f.read()
            if saved_content == test_text:
                print(f"Başarılı! Dosya diskte ( {save_path} ) doğru şekilde oluşturuldu.")
            else:
                print("HATA: İçerik eşleşmiyor!")
    else:
        print("HATA: Dosya oluşturulamadı!")

if __name__ == "__main__":
    test_signature()
    test_watermark()
    test_notepad()

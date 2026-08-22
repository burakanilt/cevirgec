import os
import fitz
import sys

from ui.pages.page_signature import PageSignature
from core.pdf_ops import apply_encryption, apply_redaction, clear_pdf_metadata, merge_pdfs, compress_pdf, reorder_pdf_pages, extract_pdf_images
from core.pdf_backend import open_document
from core.convert.image_ops import resize_image, change_dpi, convert_format
from PIL import Image, ImageDraw

OUTPUT_DIR = "tests/outputs/sprint35"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_test_data():
    # 5-page PDF
    pdf_5 = os.path.join(OUTPUT_DIR, "test_5_pages.pdf")
    doc = fitz.open()
    for i in range(5):
        page = doc.new_page()
        page.insert_text(fitz.Point(100, 100), f"Sayfa {i+1} - BURA GIZLI BURA", fontsize=20)
        
        # Insert an image on page 1 (index 0)
        if i == 0:
            img = Image.new('RGB', (100, 100), color='red')
            img_path = os.path.join(OUTPUT_DIR, "temp_red.jpg")
            img.save(img_path)
            page.insert_image(fitz.Rect(10, 10, 110, 110), filename=img_path)
            
    doc.save(pdf_5)
    doc.close()
    
    # Dummy signature
    sig_photo = os.path.join(OUTPUT_DIR, "dummy_sig_transparent.png")
    img = Image.new('RGBA', (150, 50), color=(0,0,0,255))
    img.save(sig_photo)
    
    return pdf_5, sig_photo

def test_signature(pdf_5, sig_photo):
    print("\n=== 1. İMZA TESTİ ===")
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    
    ps = PageSignature()
    ps.pdf_path = pdf_5
    ps.sig_path = sig_photo
    ps.spin_page.setValue(1) # Page 1
    
    # Calculate Right-Bottom (Sağ Alt)
    ps.rb_br.setChecked(True)
    doc = open_document(pdf_5)
    page = doc[0]
    rect_br = ps.calculate_rect(page.rect.width, page.rect.height)
    print(f"Sağ Alt Koordinatlar: {rect_br}")
    
    # Calculate Top-Left (Sol Üst)
    ps.rb_tl.setChecked(True)
    rect_tl = ps.calculate_rect(page.rect.width, page.rect.height)
    print(f"Sol Üst Koordinatlar: {rect_tl}")
    doc.close()
    print("İmza pozisyonlaması başarılı.")

def test_security(pdf_5):
    print("\n=== 2. GÜVENLİK TESTİ ===")
    
    # Encryption
    enc_pdf = os.path.join(OUTPUT_DIR, "encrypted.pdf")
    apply_encryption(pdf_5, enc_pdf, "1234")
    try:
        doc = open_document(enc_pdf) # should fail
        print("HATA: Şifresiz açılabildi!")
    except ValueError:
        print("Şifreleme BAŞARILI (Parolasız açılamadı).")
        doc2 = open_document(enc_pdf, "1234")
        print("Parola ile giriş BAŞARILI.")
        doc2.close()
        
    # Redaction (Irreversible)
    redact_pdf = os.path.join(OUTPUT_DIR, "redacted.pdf")
    apply_redaction(pdf_5, redact_pdf, "GIZLI", reversible=False)
    print("KVKK Fiziksel Karartma (Geri Döndürülemez) uygulandı.")
    
    # Redaction (Reversible)
    redact_rev_pdf = os.path.join(OUTPUT_DIR, "redacted_reversible.pdf")
    apply_redaction(pdf_5, redact_rev_pdf, "GIZLI", reversible=True)
    print("KVKK Geçici Karartma (Geri Döndürülebilir) uygulandı.")
    
    # Revert Redaction
    reverted_pdf = os.path.join(OUTPUT_DIR, "redacted_reverted.pdf")
    from core.pdf_ops import revert_redactions
    revert_redactions(redact_rev_pdf, reverted_pdf)
    print("Geçici Karartma başarıyla geri alındı.")
    
    # Metadata
    meta_pdf = os.path.join(OUTPUT_DIR, "no_meta.pdf")
    clear_pdf_metadata(pdf_5, meta_pdf)
    doc3 = open_document(meta_pdf)
    print(f"Metadata kontrolü (Temiz): {doc3.metadata}")
    doc3.close()

def test_pages_images(pdf_5):
    print("\n=== 3. SAYFA VE GÖRSEL TESTİ ===")
    # Remove pages 2 and 4 (indices 1 and 3)
    # Remaining should be 0, 2, 4 (Sayfa 1, 3, 5)
    pages_pdf = os.path.join(OUTPUT_DIR, "reordered.pdf")
    reorder_pdf_pages(pdf_5, pages_pdf, [0, 2, 4])
    doc = open_document(pages_pdf)
    print(f"Sayfa ayıklama başarılı. Kalan sayfa sayısı: {len(doc)}")
    doc.close()
    
    # Extract images
    img_dir = os.path.join(OUTPUT_DIR, "extracted_images")
    os.makedirs(img_dir, exist_ok=True)
    saved = extract_pdf_images(pdf_5, img_dir)
    print(f"Görsel çıkartma başarılı. Çıkartılan görsel sayısı: {len(saved)}")

def test_classic(pdf_5):
    print("\n=== 4. KLASİK ARAÇLAR TESTİ ===")
    # Image resize
    img_in = os.path.join(OUTPUT_DIR, "temp_red.jpg")
    img_out = os.path.join(OUTPUT_DIR, "temp_red_resized.png")
    convert_format(img_in, img_out, "PNG")
    resize_image(img_out, img_out, width=50, height=50)
    change_dpi(img_out, img_out, (150, 150))
    print(f"Görsel yeniden boyutlandırma ve format değişimi başarılı: {img_out}")
    
    # Compress
    comp_pdf = os.path.join(OUTPUT_DIR, "compressed.pdf")
    compress_pdf(pdf_5, comp_pdf)
    size_orig = os.path.getsize(pdf_5)
    size_comp = os.path.getsize(comp_pdf)
    print(f"PDF Sıkıştırma: {size_orig} byte -> {size_comp} byte")

if __name__ == "__main__":
    p5, sig = create_test_data()
    test_signature(p5, sig)
    test_security(p5)
    test_pages_images(p5)
    test_classic(p5)
    print("\n[OK] Sprint 3.5 Tüm Testler Tamamlandı.")

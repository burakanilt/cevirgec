import os
from core.router import analyze_document
from core.convert.to_word import convert_scanned_pdf_to_word
from core.convert.to_excel import convert_scanned_pdf_to_excel

OUTPUT_DIR = "tests/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test_sample_2_word():
    print("=== TEST: Sample 2 (Eski/Taranmış PDF -> Word) ===")
    pdf_path = "tests/samples/ENGİNLER ART GAZETE.pdf"
    
    # Check if Sample 2 exists
    if not os.path.exists(pdf_path):
        print(f"{pdf_path} bulunamadı!")
        return
        
    # Router test
    decisions = analyze_document(pdf_path)
    print(f"Router kararları: {decisions}")
    
    # We expect all pages to be OCR
    ocr_pages = [i for i, d in enumerate(decisions) if d == "OCR"]
    
    if ocr_pages:
        out_path = os.path.join(OUTPUT_DIR, "ENGINLER_ART_GAZETE_OCR_Cikti.docx")
        print(f"{len(ocr_pages)} sayfa OCR ile Word'e çevriliyor (sadece ilk sayfa test amaçlı)...")
        convert_scanned_pdf_to_word(pdf_path, out_path, pages=[ocr_pages[0]])
        print(f"Çeviri tamamlandı: {out_path}")
    else:
        print("HATA: Router sayfaları OCR olarak işaretlemedi!")

def test_sample_5_excel():
    print("\n=== TEST: Sample 5 (Taranmış Tablo -> Excel) ===")
    pdf_path = "tests/samples/masak excel.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"{pdf_path} bulunamadı!")
        return
        
    decisions = analyze_document(pdf_path)
    print(f"Router kararları: {decisions}")
    
    ocr_pages = [i for i, d in enumerate(decisions) if d == "OCR"]
    
    if ocr_pages:
        out_path = os.path.join(OUTPUT_DIR, "masak_excel_OCR_Cikti.xlsx")
        print(f"{len(ocr_pages)} sayfa OCR ile Excel'e çevriliyor (sadece ilk sayfa test amaçlı)...")
        convert_scanned_pdf_to_excel(pdf_path, out_path, pages=[ocr_pages[0]])
        print(f"Çeviri tamamlandı: {out_path}")
    else:
        print("HATA: Router sayfaları OCR olarak işaretlemedi!")

if __name__ == "__main__":
    test_sample_2_word()
    test_sample_5_excel()

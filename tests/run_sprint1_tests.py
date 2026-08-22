import os
from core.convert.to_word import convert_digital_pdf_to_word
from core.convert.to_excel import convert_digital_pdf_to_excel
from core.convert.to_md import convert_digital_pdf_to_md
from core.pdf_ops import merge_pdfs

SAMPLES_DIR = "tests/samples"
OUT_DIR = "tests/outputs"

os.makedirs(OUT_DIR, exist_ok=True)

def run_tests():
    print("--- SPRINT 1 GERÇEK DOSYA TESTLERİ BAŞLIYOR ---")
    
    # 1. Sample 1 (Modern Dijital) -> Word
    s1 = os.path.join(SAMPLES_DIR, "surucu-belgesi-gerekli-belgeler.pdf")
    o1 = os.path.join(OUT_DIR, "surucu-belgesi_out.docx")
    print(f"\n[Test 1] {s1} -> Word")
    convert_digital_pdf_to_word(s1, o1)
    print(f"Bitti. Dosya: {o1} (Exists: {os.path.exists(o1)})")
    
    # 2. Sample 3 (Çok Kolonlu / Dijital Doküman) -> Word
    s3 = os.path.join(SAMPLES_DIR, "document.pdf")
    o3 = os.path.join(OUT_DIR, "document_out.docx")
    print(f"\n[Test 2] {s3} -> Word")
    convert_digital_pdf_to_word(s3, o3)
    print(f"Bitti. Dosya: {o3} (Exists: {os.path.exists(o3)})")
    
    # 3. Sample 4 (Tablolu Dijital PDF) -> Excel
    s4 = os.path.join(SAMPLES_DIR, "Eimzali_Hesap_Hareketleri.pdf")
    o4 = os.path.join(OUT_DIR, "Eimzali_Hesap_Hareketleri_out.xlsx")
    print(f"\n[Test 3] {s4} -> Excel")
    convert_digital_pdf_to_excel(s4, o4)
    print(f"Bitti. Dosya: {o4} (Exists: {os.path.exists(o4)})")
    
    # 4. Sample 9 için 100+ sayfa oluşturma (0110 (1).pdf dosyasını 4 kez birleştirerek 108 sayfa yapıyoruz)
    s_base = os.path.join(SAMPLES_DIR, "0110 (1).pdf")
    s9 = os.path.join(OUT_DIR, "100plus_pages.pdf")
    print(f"\n[Hazırlık] 100+ Sayfalık PDF oluşturuluyor (4x {s_base})")
    merge_pdfs([s_base, s_base, s_base, s_base], s9)
    print(f"Oluşturuldu: {s9} (Size: {os.path.getsize(s9)} bytes)")
    
    # 100+ sayfa -> MD Dönüşümü (Timing testi)
    o9 = os.path.join(OUT_DIR, "100plus_out.md")
    print(f"\n[Test 4] {s9} -> Markdown (108 sayfa)")
    convert_digital_pdf_to_md(s9, o9)
    print(f"Bitti. Dosya: {o9} (Exists: {os.path.exists(o9)})")
    
    # 5. Merge Hız Testi (100+ sayfa PDF birleştirme)
    o_merged = os.path.join(OUT_DIR, "merged_200plus.pdf")
    print(f"\n[Test 5] 2x {s9} -> Birleştir (216 sayfa)")
    merge_pdfs([s9, s9], o_merged)
    print(f"Bitti. Dosya: {o_merged} (Exists: {os.path.exists(o_merged)})")
    
    print("\n--- TESTLER TAMAMLANDI ---")

if __name__ == "__main__":
    run_tests()

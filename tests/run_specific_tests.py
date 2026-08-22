import os
from core.convert.to_excel import convert_digital_pdf_to_excel
from core.convert.to_word import convert_digital_pdf_to_word

SAMPLES_DIR = "tests/samples"
OUT_DIR = "tests/outputs"

os.makedirs(OUT_DIR, exist_ok=True)

def run_specific_tests():
    # 1. Eimzali_Hesap_Hareketleri -> Excel (Refactored)
    s_excel = os.path.join(SAMPLES_DIR, "Eimzali_Hesap_Hareketleri.pdf")
    o_excel = os.path.join(OUT_DIR, "Eimzali_Hesap_Hareketleri_out_v2.xlsx")
    print(f"Converting {s_excel} to Excel...")
    convert_digital_pdf_to_excel(s_excel, o_excel)
    print(f"Done: {o_excel} (Exists: {os.path.exists(o_excel)}, Size: {os.path.getsize(o_excel)} bytes)")
    
    # 2. ENGİNLER ART GAZETE -> Word
    s_word = os.path.join(SAMPLES_DIR, "ENGİNLER ART GAZETE.pdf")
    o_word = os.path.join(OUT_DIR, "ENGINLER_ART_GAZETE_out.docx")
    print(f"Converting {s_word} to Word...")
    convert_digital_pdf_to_word(s_word, o_word)
    print(f"Done: {o_word} (Exists: {os.path.exists(o_word)}, Size: {os.path.getsize(o_word)} bytes)")

if __name__ == "__main__":
    run_specific_tests()

import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from PIL import Image

from core.pdf_backend import open_document, render_page
from core.ocr.engine import run_ocr

# 1. Create a PDF with Turkish text using a standard font that supports it
pdf_path = "tests/samples/Sample 8_turkish.pdf"

def create_turkish_pdf():
    # In Windows, we can use Arial or Calibri which supports Turkish
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
        font = 'Arial'
    except:
        font = 'Helvetica'
        
    c = canvas.Canvas(pdf_path)
    c.setFont(font, 24)
    # The text we want to test
    text = "Türkçe Test: ğ, ü, ş, ı, ö, ç, Ğ, Ü, Ş, İ, Ö, Ç"
    c.drawString(50, 700, text)
    c.drawString(50, 650, "Pijamalı hasta yağız şoföre çabucak güvendi.")
    c.save()

def test_ocr():
    print(f"--- SAMPLE 8: TÜRKÇE KARAKTER TESTİ ---")
    doc = open_document(pdf_path)
    img = render_page(doc, 0, dpi=300)
    
    print("OCR başlatılıyor...")
    result = run_ocr(img)
    
    with open('test_sample8_out.txt', 'w', encoding='utf-8') as f:
        if result:
            print("RapidOCR Çıktısı (dosyaya kaydedildi):")
            for line in result:
                bbox, text, confidence = line
                f.write(f"Metin: {text} (Güven: {confidence:.2f})\n")
                print(f"Metin kaydedildi: {text.encode('ascii', 'replace').decode()}")
        else:
            print("Herhangi bir metin bulunamadı!")
            f.write("Herhangi bir metin bulunamadı!\n")
        
    doc.close()

if __name__ == "__main__":
    create_turkish_pdf()
    test_ocr()

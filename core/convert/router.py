import os
from core.pdf_backend import open_document, extract_text, page_count
from core.convert.templates.manager import match_template
from core.convert.to_excel import convert_template_to_excel, convert_digital_pdf_to_excel, convert_scanned_pdf_to_excel

def route_to_excel(pdf_path: str, excel_path: str, pages: list[int] = None):
    """
    Karar zinciri (Router) for Table Extraction:
    1. Şablon Kontrolü (Katman A)
    2. Dijital Kontrolü (Katman B)
    3. Taranmış Kontrolü (Katman C)
    """
    doc = open_document(pdf_path)
    total_pages = page_count(doc)
    
    # Sadece ilk sayfayı kontrol etmek şablon ve dijital tespiti için genelde yeterlidir.
    first_page_text = extract_text(doc, 0)
    
    doc.close()
    
    # Katman A: Şablon eşleşmesi var mı?
    template = match_template(first_page_text)
    if template:
        print(f"Router: Katman A (Şablon) seçildi -> {template.get('name')}")
        convert_template_to_excel(pdf_path, excel_path, template, pages)
        return "Katman A"
        
    # Katman B vs Katman C Kararı
    # Eğer ilk sayfada belirgin bir metin varsa (ör. 50 karakterden fazla), dijital kabul edelim.
    # Tabi ekstrelerde ilk sayfa boş veya sadece logo olabilir, ama genelde hesap dökümü metin içerir.
    # İleri seviye: Sayfaların ortalama metin yoğunluğuna bakılabilir ama şimdilik ilk sayfa yeterli.
    
    text_len = len(first_page_text.strip())
    if text_len > 50:
        print("Router: Katman B (Dijital) seçildi")
        convert_digital_pdf_to_excel(pdf_path, excel_path, pages)
        return "Katman B"
    else:
        print("Router: Katman C (Taranmış / OCR) seçildi")
        convert_scanned_pdf_to_excel(pdf_path, excel_path, pages)
        return "Katman C"

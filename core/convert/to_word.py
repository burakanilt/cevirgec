from pdf2docx import Converter
from core.utils.timing import time_it

@time_it("PDF to Word (Digital)")
def convert_digital_pdf_to_word(pdf_path: str, docx_path: str, pages: list[int] = None):
    """
    Converts a digital PDF (or specific pages) to a Word document using pdf2docx.
    `pages` is a list of 0-indexed page numbers. If None, converts all pages.
    """
    cv = Converter(pdf_path)
    try:
        # pdf2docx uses 0-indexed page numbers
        if pages is not None:
            cv.convert(docx_path, pages=pages)
        else:
            cv.convert(docx_path)
    finally:
        cv.close()

@time_it("PDF to Word (OCR)")
def convert_scanned_pdf_to_word(pdf_path: str, docx_path: str, pages: list[int] = None):
    """
    Converts scanned PDF pages to a Word document using RapidOCR.
    """
    import docx
    from core.pdf_backend import open_document, render_page, page_count
    from core.ocr.engine import run_ocr
    
    doc = docx.Document()
    pdf_doc = open_document(pdf_path)
    
    try:
        total_pages = page_count(pdf_doc)
        if pages is None:
            pages = list(range(total_pages))
            
        for i, page_num in enumerate(pages):
            img = render_page(pdf_doc, page_num, dpi=300)
            result = run_ocr(img)
            
            if result:
                import numpy as np
                boxes = []
                for bbox, text, conf in result:
                    arr = np.array(bbox)
                    y_c = np.mean(arr[:, 1])
                    min_x = np.min(arr[:, 0])
                    boxes.append({'y_c': y_c, 'x': min_x, 'text': text})
                
                # Sort by center Y
                boxes.sort(key=lambda b: b['y_c'])
                
                lines = []
                current_line = []
                for b in boxes:
                    if not current_line:
                        current_line.append(b)
                    else:
                        # 15 pixels tolerance to group in the same line
                        avg_y = sum(cb['y_c'] for cb in current_line) / len(current_line)
                        if abs(b['y_c'] - avg_y) < 15:
                            current_line.append(b)
                        else:
                            lines.append(current_line)
                            current_line = [b]
                if current_line:
                    lines.append(current_line)
                
                for line_boxes in lines:
                    # Sort left-to-right
                    line_boxes.sort(key=lambda b: b['x'])
                    line_text = " ".join([b['text'] for b in line_boxes])
                    doc.add_paragraph(line_text)
                    
            if i < len(pages) - 1:
                doc.add_page_break()
                
        doc.save(docx_path)
    finally:
        pdf_doc.close()

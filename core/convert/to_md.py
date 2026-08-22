import pymupdf4llm
from core.utils.timing import time_it

@time_it("PDF to Markdown (Digital)")
def convert_digital_pdf_to_md(pdf_path: str, md_path: str, pages: list[int] = None):
    """
    Converts a digital PDF to Markdown using pymupdf4llm.
    """
    md_text = pymupdf4llm.to_markdown(pdf_path, pages=pages)
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)

@time_it("PDF to Markdown (OCR)")
def convert_scanned_pdf_to_md(pdf_path: str, md_path: str, pages: list[int] = None):
    """
    Converts scanned PDF pages to Markdown using RapidOCR.
    """
    from core.pdf_backend import open_document, render_page, page_count
    from core.ocr.engine import run_ocr
    
    pdf_doc = open_document(pdf_path)
    
    try:
        total_pages = page_count(pdf_doc)
        if pages is None:
            pages = list(range(total_pages))
            
        with open(md_path, "w", encoding="utf-8") as f:
            for i, page_num in enumerate(pages):
                img = render_page(pdf_doc, page_num, dpi=300)
                result = run_ocr(img)
                
                if result:
                    from core.ocr.engine import sort_ocr_results_by_columns
                    # result is list of (bbox, text, conf)
                    # Sort by columns and then y1 (top of bounding box)
                    result = sort_ocr_results_by_columns(result)
                    
                    for bbox, text, conf in result:
                        f.write(text + "\n\n")
                        
                if i < len(pages) - 1:
                    f.write("---\n\n")
    finally:
        pdf_doc.close()

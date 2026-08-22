from core import pdf_backend

def determine_page_pipeline(doc, page_no: int, threshold: int = 30) -> str:
    """
    Determines if a page should go through the digital pipeline or OCR pipeline.
    Uses core.pdf_backend to extract text to maintain the Fitz Wall.
    
    Returns:
        "DIGITAL" if text layer has >= `threshold` words.
        "OCR_PENDING" otherwise.
    """
    # Use extract_words from pdf_backend which returns a list of words
    words = pdf_backend.extract_words(doc, page_no)
    
    if len(words) >= threshold:
        return "DIGITAL"
    else:
        return "OCR"

def analyze_document(pdf_path: str, threshold: int = 30) -> list[str]:
    """
    Analyzes all pages in a document and returns a list of pipeline decisions.
    """
    doc = pdf_backend.open_document(pdf_path)
    try:
        total_pages = pdf_backend.page_count(doc)
        decisions = []
        for i in range(total_pages):
            decisions.append(determine_page_pipeline(doc, i, threshold))
        return decisions
    finally:
        doc.close()

def add_watermark(pdf_path: str, out_path: str, text: str = "GİZLİ", fontsize: int = 40):
    """
    Adds an OCG (layer) based watermark to the PDF.
    """
    from core.pdf_backend import open_document, save_document, add_watermark_ocg
    
    doc = open_document(pdf_path)
    try:
        add_watermark_ocg(doc, text, fontsize=fontsize)
        save_document(doc, out_path)
    finally:
        doc.close()

def remove_watermark(pdf_path: str, out_path: str):
    """
    Removes the OCG watermark from the PDF.
    """
    from core.pdf_backend import open_document, save_document, remove_watermark_ocg
    import logging
    
    doc = open_document(pdf_path)
    try:
        remove_watermark_ocg(doc)
        save_document(doc, out_path)
    except ValueError as e:
        # User requirement: Log or catch the specific ValueError for flattened watermarks
        logging.warning(str(e))
        raise
    finally:
        doc.close()

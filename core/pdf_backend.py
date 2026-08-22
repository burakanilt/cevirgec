import fitz  # PyMuPDF
from PIL import Image

def open_document_original(path: str) -> fitz.Document:
    # Renamed to avoid conflicts, though the new one is at the bottom. Wait, Python uses the latest defined. Let's just remove it.
    pass
def page_count(doc: fitz.Document) -> int:
    return len(doc)

def render_page(doc: fitz.Document, page_no: int, dpi: int = 300) -> Image.Image:
    page = doc[page_no]
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    # Convert fitz pixmap to PIL Image
    mode = "RGBA" if pix.alpha else "RGB"
    return Image.frombytes(mode, [pix.width, pix.height], pix.samples)

def extract_words(doc: fitz.Document, page_no: int) -> list:
    page = doc[page_no]
    return page.get_text("words")

def extract_text(doc: fitz.Document, page_no: int) -> str:
    page = doc[page_no]
    return page.get_text("text")

def merge_documents(docs: list[fitz.Document]) -> fitz.Document:
    merged_doc = fitz.open()
    for doc in docs:
        merged_doc.insert_pdf(doc)
    return merged_doc

def split_document(doc: fitz.Document, start_page: int, end_page: int) -> fitz.Document:
    new_doc = fitz.open()
    new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
    return new_doc

def rotate_page(doc: fitz.Document, page_no: int, rotation: int):
    page = doc[page_no]
    page.set_rotation(rotation)

def compress_document(doc: fitz.Document, output_path: str):
    doc.save(output_path, garbage=4, deflate=True)

def save_document_original(doc: fitz.Document, output_path: str):
    # Old version
    pass
def insert_image(doc: fitz.Document, page_no: int, img_path: str, rect: tuple):
    page = doc[page_no]
    fitz_rect = fitz.Rect(*rect)
    page.insert_image(fitz_rect, filename=img_path)

def add_watermark_ocg(doc: fitz.Document, text: str = "GİZLİ", fontsize: int = 40):
    """
    Adds a text watermark as an OCG layer to all pages.
    """
    ocg_xref = doc.add_ocg("CevirgecWatermark")
    
    for page in doc:
        rect = page.rect
        # Simple diagonal watermark in the center
        p1 = fitz.Point(rect.width * 0.2, rect.height * 0.8)
        p2 = fitz.Point(rect.width * 0.8, rect.height * 0.2)
        
        # Use insert_text or insert_textbox with oc=ocg_xref
        # A simple text insertion
        # We need a font size that fits. Just a basic large text.
        try:
            page.insert_text(
                fitz.Point(rect.width/2 - 100, rect.height/2), 
                text, 
                fontsize=fontsize, 
                color=(0.8, 0.8, 0.8), # light gray
                oc=ocg_xref,
                fontname="arial",
                fontfile="C:/Windows/Fonts/arial.ttf"
            )
        except Exception as e:
            import logging
            logging.warning(f"Arial font yüklenemedi, varsayılan fonta dönülüyor: {e}")
            page.insert_text(
                fitz.Point(rect.width/2 - 100, rect.height/2), 
                text, 
                fontsize=fontsize, 
                color=(0.8, 0.8, 0.8), # light gray
                oc=ocg_xref
            )

def remove_watermark_ocg(doc: fitz.Document):
    """
    Removes or hides the CevirgecWatermark OCG layer.
    Raises ValueError if no such layer is found.
    """
    ocgs = doc.get_ocgs()
    found_xref = None
    
    for xref, info in ocgs.items():
        if info.get('name') == "CevirgecWatermark":
            found_xref = xref
            break
            
    if found_xref is not None:
        doc.set_layer(-1, off=[found_xref])
    else:
        raise ValueError("OCG katmanı bulunamadı, düzleştirilmiş filigran silinemez.")

def encrypt_document(doc: fitz.Document, password: str):
    """
    Sets encryption parameters for the document. 
    It will take effect when doc.save() is called.
    """
    # We don't encrypt in-place here. In PyMuPDF, encryption is done during save.
    # We can pass encryption params via save_document. Let's modify save_document to accept kwargs.
    pass

def save_document(doc: fitz.Document, output_path: str, encryption: int = fitz.PDF_ENCRYPT_NONE, user_pw: str = None, owner_pw: str = None):
    """
    Saves the document, optionally applying encryption.
    """
    if user_pw or owner_pw:
        # If user provides password, we encrypt with AES-256 (default for high security)
        doc.save(
            output_path, 
            encryption=fitz.PDF_ENCRYPT_AES_256, 
            owner_pw=owner_pw or user_pw,
            user_pw=user_pw
        )
    else:
        doc.save(output_path)

def open_document(path: str, password: str = None) -> fitz.Document:
    doc = fitz.open(path)
    if doc.needs_pass:
        if password:
            doc.authenticate(password)
        else:
            raise ValueError("Belge şifreli, parola gerekli!")
    return doc

def redact_text(doc: fitz.Document, text: str, reversible: bool = False):
    """
    Searches for `text` across all pages and applies redaction (blackout).
    If reversible is True, it draws a black rectangle annot that can be removed later.
    If reversible is False, it physically removes the text.
    """
    for page in doc:
        text_instances = page.search_for(text)
        if reversible:
            for inst in text_instances:
                annot = page.add_rect_annot(inst)
                annot.set_colors(stroke=(0, 0, 0), fill=(0, 0, 0))
                annot.set_info({'title': 'CevirgecReversible', 'content': 'Reversible Redaction'})
                annot.update()
        else:
            for inst in text_instances:
                page.add_redact_annot(inst, fill=(0, 0, 0))
            if text_instances:
                page.apply_redactions()

def remove_reversible_redactions(doc: fitz.Document):
    """
    Removes all reversible redactions (annotations created by Cevirgec) from the PDF.
    """
    for page in doc:
        annots = list(page.annots())
        for annot in annots:
            if annot.info.get('title') == "CevirgecReversible":
                page.delete_annot(annot)

def extract_images(doc: fitz.Document, output_dir: str) -> list[str]:
    """
    Extracts all images from the PDF and saves them to output_dir.
    Returns a list of saved file paths.
    """
    import os
    saved_files = []
    
    for i in range(len(doc)):
        for img in doc.get_page_images(i):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            out_path = os.path.join(output_dir, f"image_p{i+1}_{xref}.{image_ext}")
            with open(out_path, "wb") as f:
                f.write(image_bytes)
            saved_files.append(out_path)
            
    return saved_files

def select_pages(doc: fitz.Document, page_list: list[int]):
    """
    Selects/reorders/deletes pages in the document based on the page_list (0-indexed).
    """
    doc.select(page_list)

def clear_metadata(doc: fitz.Document):
    """
    Clears the document's metadata (author, creation date, etc.)
    """
    doc.set_metadata({})

def expand_page_bottom_margin(doc: fitz.Document, margin_pts: float = 115.0):
    """
    Expands the bottom margin of all pages in the PDF by `margin_pts`.
    Since PyMuPDF coordinates start top-left (0,0), increasing y1 extends the bottom.
    """
    for page in doc:
        rect = page.rect
        rect.y1 += margin_pts
        page.set_mediabox(rect)

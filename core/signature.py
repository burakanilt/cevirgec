import os
import numpy as np
from PIL import Image

def extract_signature(img_path: str, out_path: str, custom_threshold: int = None):
    """
    Extracts a signature from an image by:
    1. Converting to grayscale.
    2. Using Otsu's thresholding (or a custom threshold) to find the signature pixels.
    3. Making the background transparent.
    4. Cropping to the signature bounding box.
    5. Saving as PNG.
    """
    # 1. Open and convert to grayscale
    img = Image.open(img_path).convert("L")
    arr = np.array(img)
    
    # 2. Otsu's thresholding (adaptive for shadows)
    if custom_threshold is None:
        hist, _ = np.histogram(arr.flatten(), 256, [0,256])
        hist_norm = hist.astype(float) / arr.size
        omega = np.cumsum(hist_norm)
        mu = np.cumsum(hist_norm * np.arange(256))
        mu_t = mu[-1]
        
        with np.errstate(divide='ignore', invalid='ignore'):
            sigma_b_squared = (mu_t * omega - mu)**2 / (omega * (1 - omega))
            
        threshold = np.nanargmax(sigma_b_squared)
    else:
        threshold = custom_threshold
        
    # We might want to slightly bias the threshold to be lower to remove light gray shadows better
    # In practice, Otsu works well, but if we need a tolerance, we could adjust it here.
    # threshold = int(threshold * 0.9)
    
    # 3. Apply threshold and make background transparent
    rgba = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
    
    # Signature pixels: make them black and opaque
    is_sig = arr < threshold
    rgba[is_sig, 0] = 0 # R
    rgba[is_sig, 1] = 0 # G
    rgba[is_sig, 2] = 0 # B
    rgba[is_sig, 3] = 255 # A
    
    # 4. Crop to bounding box
    coords = np.argwhere(is_sig)
    if coords.size > 0:
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0)
        
        # Add a small padding
        pad = 5
        y0 = max(0, y0 - pad)
        y1 = min(arr.shape[0] - 1, y1 + pad)
        x0 = max(0, x0 - pad)
        x1 = min(arr.shape[1] - 1, x1 + pad)
        
        rgba = rgba[y0:y1+1, x0:x1+1]
        
    # 5. Save as PNG
    out_img = Image.fromarray(rgba, 'RGBA')
    out_img.save(out_path, format="PNG")
    return out_path

def add_signature_to_pdf(pdf_path: str, sig_img_path: str, page_num: int, rect: tuple, out_path: str):
    """
    Adds a signature image to a specific page and rectangle in a PDF.
    Maintains the Fitz wall via pdf_backend.
    """
    from core.pdf_backend import open_document, insert_image, save_document
    
    doc = open_document(pdf_path)
    try:
        # insert_image expects rect as (x0, y0, x1, y1)
        insert_image(doc, page_num, sig_img_path, rect)
        save_document(doc, out_path)
    finally:
        doc.close()

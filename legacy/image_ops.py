from PIL import Image, ImageOps
import img2pdf
import os

import fitz  # PyMuPDF

def fix_image_orientation(image_path):
    """
    Opens an image, fixes its EXIF orientation, and returns the PIL Image object.
    Convert to RGB to ensure compatibility with PDF libraries (no Alpha).
    """
    try:
        img = Image.open(image_path)
        img = ImageOps.exif_transpose(img)
        
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        return img
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

def images_to_pdf(image_paths, output_pdf_path):
    """
    Converts a list of images to a single PDF, handling orientation and mode.
    """
    try:
        # img2pdf likes raw bytes or paths, but we need to pre-process (orientation/RGB)
        # So we save temp files or pass bytes.
        # Simplest consistent way: Save temp adjusted images if needed, or just specific paths.
        # But we already fix orientation in the UI flow usually.
        # Let's handle the list here more robustly.
        
        cleaned_images = []
        temp_files_to_remove = []
        
        for p in image_paths:
            img = fix_image_orientation(p)
            if img:
                # Save as temp JPG to ensure standard format
                temp_name = f"temp_{os.path.basename(p)}.jpg"
                img.save(temp_name, quality=90)
                cleaned_images.append(temp_name)
                temp_files_to_remove.append(temp_name)
        
        pdf_bytes = img2pdf.convert(cleaned_images)
        with open(output_pdf_path, "wb") as f:
            f.write(pdf_bytes)
            
        # Cleanup
        for t in temp_files_to_remove:
            if os.path.exists(t):
                os.remove(t)
                
        return True
    except Exception as e:
        raise e

def pdf_to_images(pdf_path, output_dir, fmt="png"):
    """
    Converts PDF pages to images.
    """
    try:
        doc = fitz.open(pdf_path)
        created_files = []
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=150)
            out_name = os.path.join(output_dir, f"{base_name}_page_{i+1}.{fmt}")
            pix.save(out_name)
            created_files.append(out_name)
            
        return created_files
    except Exception as e:
        raise e

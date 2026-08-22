from PIL import Image

def resize_image(img_path: str, out_path: str, width: int = None, height: int = None):
    """
    Resizes an image. If only width or height is provided, maintains aspect ratio.
    """
    img = Image.open(img_path)
    
    if width and not height:
        ratio = width / img.width
        height = int(img.height * ratio)
    elif height and not width:
        ratio = height / img.height
        width = int(img.width * ratio)
    elif not width and not height:
        width, height = img.width, img.height
        
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    img.save(out_path)
    return out_path

def change_dpi(img_path: str, out_path: str, dpi: tuple = (300, 300)):
    """
    Changes the DPI metadata of an image.
    """
    img = Image.open(img_path)
    img.save(out_path, dpi=dpi)
    return out_path

def convert_format(img_path: str, out_path: str, format: str = "PNG"):
    """
    Converts image format (e.g., to 'JPEG', 'PNG').
    """
    img = Image.open(img_path)
    if img.mode == 'RGBA' and format.upper() in ['JPEG', 'JPG']:
        img = img.convert('RGB')
    img.save(out_path, format=format)
    return out_path

from PIL import ImageOps

def advanced_image_process(input_path: str, output_path: str, width: int, height: int, dpi: int, color_mode: str, pad_image: bool, smart_scan: bool = False):
    """
    Advanced image processor: Handles RGB/RGBA/Grayscale conversion, padding, resizing, and DPI.
    Includes optional Smart Scan (EXIF orientation fix).
    """
    img = Image.open(input_path)
    
    if smart_scan:
        img = ImageOps.exif_transpose(img)
    
    # 1. Color mode conversion
    if color_mode == 'RGB':
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            # Convert transparent pixels to white background
            background = Image.new('RGBA', img.size, (255, 255, 255, 255))
            alpha_composite = Image.alpha_composite(background, img.convert('RGBA'))
            img = alpha_composite.convert('RGB')
        else:
            img = img.convert('RGB')
    elif color_mode == 'RGBA':
        img = img.convert('RGBA')
    elif color_mode == 'Grayscale':
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGBA', img.size, (255, 255, 255, 255))
            alpha_composite = Image.alpha_composite(background, img.convert('RGBA'))
            img = alpha_composite.convert('L')
        else:
            img = img.convert('L')
            
    # 2. Resizing & Padding
    if width > 0 and height > 0:
        if pad_image:
            # maintain aspect ratio, add white padding
            img = ImageOps.pad(img, (width, height), color=(255,255,255) if color_mode == 'RGB' else (255,255,255,0))
        else:
            # stretch or exact resize
            img = img.resize((width, height), Image.Resampling.LANCZOS)
    elif width > 0 and height == 0:
        ratio = width / img.width
        h = int(img.height * ratio)
        img = img.resize((width, h), Image.Resampling.LANCZOS)
    elif height > 0 and width == 0:
        ratio = height / img.height
        w = int(img.width * ratio)
        img = img.resize((w, height), Image.Resampling.LANCZOS)
        
    # 3. Save with DPI
    # Format determination based on output_path
    fmt = output_path.split('.')[-1].upper()
    if fmt == 'JPG': fmt = 'JPEG'
    
    if fmt == 'JPEG' and img.mode == 'RGBA':
        img = img.convert('RGB') # Safety fallback
        
    img.save(output_path, format=fmt, dpi=(dpi, dpi))
    return output_path

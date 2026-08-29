import os
import pytest
from PIL import Image, ImageDraw
import fitz

from core.convert.to_pdf import convert_image_to_pdf
from core.convert.image_ops import advanced_image_process

def test_convert_rgb_image_to_pdf(tmp_path):
    img_path = str(tmp_path / "test_rgb.png")
    pdf_path = str(tmp_path / "test_rgb.pdf")
    
    img = Image.new("RGB", (200, 100), color=(255, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((10, 10), "Test RGB", fill=(255, 255, 255))
    img.save(img_path)
    
    out = convert_image_to_pdf(img_path, pdf_path)
    assert os.path.exists(out)
    assert os.path.getsize(out) > 0
    
    doc = fitz.open(pdf_path)
    assert len(doc) == 1
    doc.close()

def test_convert_rgba_transparent_image_to_pdf(tmp_path):
    img_path = str(tmp_path / "test_rgba.png")
    pdf_path = str(tmp_path / "test_rgba.pdf")
    
    img = Image.new("RGBA", (150, 150), color=(0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([20, 20, 130, 130], fill=(0, 128, 255, 200))
    img.save(img_path)
    
    out = convert_image_to_pdf(img_path, pdf_path)
    assert os.path.exists(out)
    
    doc = fitz.open(pdf_path)
    assert len(doc) == 1
    doc.close()

def test_advanced_image_process_to_pdf(tmp_path):
    img_path = str(tmp_path / "test_process.jpg")
    pdf_path = str(tmp_path / "test_process.pdf")
    
    img = Image.new("RGB", (400, 300), color=(50, 150, 200))
    img.save(img_path, "JPEG")
    
    out = advanced_image_process(
        input_path=img_path,
        output_path=pdf_path,
        width=800,
        height=600,
        dpi=300,
        color_mode="RGB",
        pad_image=True,
        smart_scan=False
    )
    assert os.path.exists(out)
    
    doc = fitz.open(pdf_path)
    assert len(doc) == 1
    doc.close()

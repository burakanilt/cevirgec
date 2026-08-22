import os
import io
import pandas as pd
from PIL import Image

_img2table_engine = None

def get_table_engine():
    global _img2table_engine
    if _img2table_engine is None:
        from img2table.ocr._types import OCRData, OCRInstance
        from img2table.document._types import Document
        from core.ocr.engine import get_engine
        
        class CustomRapidOCR(OCRInstance):
            def of(self, document) -> OCRData | None:
                engine = get_engine()
                records = {}
                import numpy as np
                
                for page_idx, image in enumerate(document.images):
                    result, _ = engine(image)
                    if not result:
                        continue
                        
                    list_elements = []
                    for idx, (bbox, text, conf) in enumerate(result):
                        bbox_np = np.array(bbox)
                        
                        # Apply 10px snapping to y-coordinates to prevent row shifts
                        y1_raw = np.min(bbox_np[:, 1])
                        y2_raw = np.max(bbox_np[:, 1])
                        y1_snapped = int(round(y1_raw / 10.0) * 10)
                        y2_snapped = int(round(y2_raw / 10.0) * 10)
                        
                        if y2_snapped <= y1_snapped:
                            y2_snapped = y1_snapped + 10
                            
                        list_elements.append({
                            "id": f"word_{page_idx + 1}_{idx + 1}",
                            "parent": f"word_{page_idx + 1}_{idx + 1}",
                            "value": text,
                            "confidence": int(100 * conf),
                            "x1": int(np.min(bbox_np[:, 0])),
                            "y1": y1_snapped,
                            "x2": int(np.max(bbox_np[:, 0])),
                            "y2": y2_snapped,
                        })
                    
                    if list_elements:
                        records[page_idx] = list_elements
                        
                return OCRData(records=records) if records else None

        _img2table_engine = CustomRapidOCR()
    return _img2table_engine

def extract_tables_to_excel(image: Image.Image, output_path: str):
    """
    Extracts tables from a scanned PIL Image using img2table and writes directly to an xlsx file.
    """
    ocr_engine = get_table_engine()
    
    from img2table.document import Image as Img2TableImage
    
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    
    img2table_doc = Img2TableImage(src=img_bytes)
    
    # Extract tables and save directly to xlsx
    img2table_doc.to_xlsx(output_path, ocr=ocr_engine, implicit_rows=True, borderless_tables=False)

def extract_tables_from_image(image: Image.Image):
    """
    Extracts tables from a scanned PIL Image using img2table.
    Returns: list of ExtractedTable
    """
    ocr_engine = get_table_engine()
    from img2table.document import Image as Img2TableImage
    
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    
    img2table_doc = Img2TableImage(src=img_bytes)
    extracted_tables = img2table_doc.extract_tables(ocr=ocr_engine, implicit_rows=True, borderless_tables=False)
    
    return extracted_tables

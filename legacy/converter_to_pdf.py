import os
from docx2pdf import convert
import pandas as pd
from openpyxl import load_workbook
from docx import Document
from docx.shared import Inches

def convert_docx_to_pdf(docx_path, output_path=None):
    if output_path is None:
        output_path = docx_path.replace(".docx", ".pdf")
    
    # docx2pdf handles COM internally
    convert(docx_path, output_path)
    return output_path

def convert_image_to_docx(image_path, output_path=None):
    """
    Inserts an image into a new Word document.
    """
    if output_path is None:
        # crude extension replace
        base = os.path.splitext(image_path)[0]
        output_path = base + ".docx"
        
    doc = Document()
    # Add image, fitting to page width roughly (6 inches is safe standard)
    doc.add_picture(image_path, width=Inches(6.0))
    doc.save(output_path)
    return output_path

def convert_excel_to_pdf(xlsx_path, output_path=None):
    """
    Converts Excel to PDF. 
    NOTE: Detailed Excel->PDF formatting is complex without Excel installed.
    For this 'Master Prompt', we rely on COM automation similar to docx2pdf logic if available,
    or we can provide a Pandas->HTML->PDF fallback if requested, but let's stick to the prompt's context.
    The prompt said "Office -> PDF: docx2pdf ... pandas + openpyxl (Excel verisi için)".
    Passively, pandas/openpyxl reads data. To PRINT to PDF, we really want an Excel instance.
    """
    if output_path is None:
        output_path = xlsx_path.replace(".xlsx", ".pdf")

    # Simple approach using win32com if user has Excel installed (matches docx2pdf dependency style)
    try:
        import win32com.client
        import pythoncom
        
        pythoncom.CoInitialize()
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        
        wb = excel.Workbooks.Open(os.path.abspath(xlsx_path))
        wb.ExportAsFixedFormat(0, os.path.abspath(output_path))
        wb.Close()
        excel.Quit()
        return output_path
    except ImportError:
        # Fallback or Error
        raise ImportError("pywin32 not installed or Excel not found. Excel->PDF requires Microsoft Excel.")
    except Exception as e:
        raise e

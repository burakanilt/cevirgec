import pdfplumber
import pandas as pd
from pdf2docx import Converter

def convert_pdf_to_docx(pdf_path, output_path=None):
    if output_path is None:
        output_path = pdf_path.replace(".pdf", ".docx")
        
    cv = Converter(pdf_path)
    # Convert whole PDF
    cv.convert(output_path, start=0, end=None)
    cv.close()
    return output_path

import os
import pdfplumber
import pandas as pd
import xlwings as xw
try:
    import camelot
except ImportError:
    camelot = None

def convert_pdf_to_excel(pdf_path, output_path=None):
    """
    Extracts tables from PDF and saves them to an Excel file using Camelot (Lattice/Stream)
    with a fallback to pdfplumber. Uses xlwings for final formatting.
    """
    if output_path is None:
        output_path = pdf_path.replace(".pdf", ".xlsx")

    # 1. Try Camelot-py first (High Accuracy)
    tables_found = False
    
    if camelot:
        try:
            # Try Lattice (lines) approach first
            tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
            if len(tables) == 0:
                # Try Stream (whitespace) approach
                tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
            
            if len(tables) > 0:
                with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                    for i, table in enumerate(tables):
                        df = table.df
                        sheet_name = f"Table_{i+1}"
                        df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                tables_found = True
        except Exception as e:
            print(f"Camelot extraction failed: {e}. Falling back to pdfplumber.")
            tables_found = False

    # 2. Fallback to pdfplumber if Camelot failed or found nothing
    if not tables_found:
        print("Using pdfplumber fallback...")
        with pdfplumber.open(pdf_path) as pdf:
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                has_tables = False
                for i, page in enumerate(pdf.pages):
                     # Tuned settings for better table detection "Lines"
                    pk_table_settings = {
                        "vertical_strategy": "lines", 
                        "horizontal_strategy": "lines",
                        "snap_tolerance": 3,
                    }
                    tables = page.extract_tables(table_settings=pk_table_settings)
                    
                    if not tables:
                         # Fallback to "text" strategy
                        pk_table_settings_text = {
                            "vertical_strategy": "text", 
                            "horizontal_strategy": "text",
                            "snap_tolerance": 3,
                        }
                        tables = page.extract_tables(table_settings=pk_table_settings_text)
                    
                    if tables:
                        has_tables = True
                        for j, table in enumerate(tables):
                            # Clean cleanup
                            df = pd.DataFrame(table[1:], columns=table[0]) 
                            sheet_name = f"Page{i+1}_Table{j+1}"
                            # Sanitize sheet name len (max 31 chars)
                            sheet_name = sheet_name[:31] 
                            # Basic sanitization
                            df = df.applymap(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                if not has_tables:
                    pd.DataFrame(["No tables found."]).to_excel(writer, "Info")

    # 3. Post-Process with xlwings (Formatting)
    # Only if on Windows and generic Excel is available
    if os.name == 'nt':
        try:
            app = xw.App(visible=False)
            wb = app.books.open(output_path)
            for sheet in wb.sheets:
                sheet.autofit() # Autofit columns and rows
            wb.save()
            wb.close()
            app.quit()
        except Exception as e:
            print(f"xlwings formatting failed (Excel might not be installed): {e}")

    return output_path

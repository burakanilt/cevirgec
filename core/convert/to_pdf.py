import os
import sys
import io

def convert_docx_to_pdf(docx_path: str, output_path: str):
    """
    Word dosyasını PDF'e dönüştürür.
    Sistemde Microsoft Word (COM objesi) yüklü olmasını gerektirir.
    GUI / PyInstaller ortamında sys.stdout ve sys.stderr None olduğu için 'NoneType' object has no attribute 'write'
    hatasını engellemek üzere sys.stdout / sys.stderr güvenliği ve doğrudan win32com COM otomasyonu kullanılır.
    """
    # GUI veya konsol bulunmayan ortamlarda sys.stdout / sys.stderr None olabiliyor.
    # tqdm ve win32com çıktıları için bu yönlendirme şarttır.
    if sys.stdout is None:
        sys.stdout = io.StringIO()
    if sys.stderr is None:
        sys.stderr = io.StringIO()

    try:
        import pythoncom
        pythoncom.CoInitialize()
        
        # Öncelikli: win32com ile doğrudan Word COM motorunu çağır
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False
        
        abs_docx = os.path.abspath(docx_path)
        abs_pdf = os.path.abspath(output_path)
        
        doc = word.Documents.Open(abs_docx)
        # 17 = wdFormatPDF
        doc.SaveAs(abs_pdf, FileFormat=17)
        doc.Close(False)
        word.Quit()
    except Exception as win32_err:
        # İkincil deneme: docx2pdf kütüphanesi ile dene
        try:
            from docx2pdf import convert
            convert(os.path.abspath(docx_path), os.path.abspath(output_path))
        except Exception as e:
            raise Exception(f"Bu işlem için sistemde Microsoft Word kurulu olmalıdır. Detay: {win32_err}")
    finally:
        try:
            import pythoncom
            pythoncom.CoUninitialize()
        except:
            pass

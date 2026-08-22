import os
from core import pdf_backend
from core import router

SAMPLES_DIR = "tests/samples"
files = [f for f in os.listdir(SAMPLES_DIR) if f.endswith(".pdf")]

print("--- DOSYA INCELEME ---")
for f in files:
    path = os.path.join(SAMPLES_DIR, f)
    try:
        doc = pdf_backend.open_document(path)
        pages = pdf_backend.page_count(doc)
        
        # Check first page words to see if it's digital
        words = len(pdf_backend.extract_words(doc, 0)) if pages > 0 else 0
        decision = router.determine_page_pipeline(doc, 0) if pages > 0 else "N/A"
        
        print(f"Dosya: {f:60} | Sayfa: {pages:3} | Sayfa 1 Kelime: {words:4} | Karar: {decision}")
        doc.close()
    except Exception as e:
        print(f"Hata {f}: {e}")

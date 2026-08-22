from core import pdf_backend
from core.utils.timing import time_it
import os

@time_it("PDF Birleştirme")
def merge_pdfs(pdf_paths: list[str], output_path: str):
    """
    Merges multiple PDFs into a single PDF.
    """
    docs = [pdf_backend.open_document(p) for p in pdf_paths]
    try:
        merged = pdf_backend.merge_documents(docs)
        pdf_backend.save_document(merged, output_path)
    finally:
        for doc in docs:
            doc.close()

@time_it("PDF Bölme")
def split_pdf(pdf_path: str, output_path: str, start_page: int, end_page: int):
    """
    Splits a PDF by extracting pages from start_page to end_page (0-indexed, inclusive).
    """
    doc = pdf_backend.open_document(pdf_path)
    try:
        new_doc = pdf_backend.split_document(doc, start_page, end_page)
        pdf_backend.save_document(new_doc, output_path)
    finally:
        doc.close()

@time_it("PDF Sıkıştırma")
def compress_pdf(pdf_path: str, output_path: str):
    """
    Compresses a PDF file.
    """
    doc = pdf_backend.open_document(pdf_path)
    try:
        pdf_backend.compress_document(doc, output_path)
    finally:
        doc.close()

@time_it("PDF Sayfa Döndürme")
def rotate_pdf_page(pdf_path: str, output_path: str, page_no: int, rotation: int):
    """
    Rotates a specific page (0-indexed) by `rotation` degrees (e.g. 90, 180, 270) and saves.
    """
    doc = pdf_backend.open_document(pdf_path)
    try:
        pdf_backend.rotate_page(doc, page_no, rotation)
        pdf_backend.save_document(doc, output_path)
    finally:
        doc.close()

@time_it("PDF Şifreleme / Şifre Çözme")
def apply_encryption(pdf_path: str, output_path: str, user_pw: str, owner_pw: str = None):
    """
    Encrypts a PDF using AES-256.
    """
    doc = pdf_backend.open_document(pdf_path) # Assumes original is not encrypted or we don't need pw to open
    try:
        pdf_backend.save_document(doc, output_path, user_pw=user_pw, owner_pw=owner_pw)
    finally:
        doc.close()

@time_it("PDF KVKK Karartma")
def apply_redaction(pdf_path: str, output_path: str, text_to_redact: str, reversible: bool = False):
    """
    Finds and redacts text in a PDF.
    """
    doc = pdf_backend.open_document(pdf_path)
    try:
        pdf_backend.redact_text(doc, text_to_redact, reversible=reversible)
        pdf_backend.save_document(doc, output_path)
    finally:
        doc.close()

@time_it("PDF Geri Döndürülebilir Karartmaları Kaldır")
def revert_redactions(pdf_path: str, output_path: str):
    """
    Removes all reversible redactions in a PDF.
    """
    doc = pdf_backend.open_document(pdf_path)
    try:
        pdf_backend.remove_reversible_redactions(doc)
        pdf_backend.save_document(doc, output_path)
    finally:
        doc.close()

@time_it("PDF Görsel Çıkartma")
def extract_pdf_images(pdf_path: str, output_dir: str):
    """
    Extracts all embedded images in a PDF.
    """
    doc = pdf_backend.open_document(pdf_path)
    try:
        return pdf_backend.extract_images(doc, output_dir)
    finally:
        doc.close()

@time_it("PDF Sayfa Seçimi/Silme")
def reorder_pdf_pages(pdf_path: str, output_path: str, page_list: list[int]):
    """
    Reorders or deletes pages in a PDF based on the page_list (0-indexed).
    """
    doc = pdf_backend.open_document(pdf_path)
    try:
        pdf_backend.select_pages(doc, page_list)
        pdf_backend.save_document(doc, output_path)
    finally:
        doc.close()

@time_it("PDF Metadata Temizleme")
def clear_pdf_metadata(pdf_path: str, output_path: str):
    """
    Clears metadata (Author, CreationDate) from a PDF.
    """
    doc = pdf_backend.open_document(pdf_path)
    try:
        pdf_backend.clear_metadata(doc)
        pdf_backend.save_document(doc, output_path)
    finally:
        doc.close()

@time_it("PDF Alt Boşluk (Marj) Ekleme")
def apply_bottom_margin(pdf_path: str, output_path: str, margin_pts: float = 115.0):
    """
    Expands the bottom margin of a PDF by a specified amount (default 115 pts ~ 4 cm).
    """
    doc = pdf_backend.open_document(pdf_path)
    try:
        pdf_backend.expand_page_bottom_margin(doc, margin_pts)
        pdf_backend.save_document(doc, output_path)
    finally:
        doc.close()

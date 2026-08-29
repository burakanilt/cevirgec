import os
import json
from typing import Callable, List

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".cevirgec_pdf", "config.json")

TRANSLATIONS = {
    "tr": {
        # App Title & Navigation
        "app_title": "Çevirgeç PDF V.2.0",
        "app_brand": "ÇEVİRGEÇ PDF",
        "nav_convert": "PDF Dönüştür",
        "nav_pdf_tools": "PDF Araçları",
        "nav_security": "Güvenlik & KVKK",
        "nav_etds": "ETDS Modülü",
        "nav_watermark": "Filigran",
        "nav_signature": "İmza",
        "nav_image": "Görsel İşlemleri",
        "nav_notepad": "Not Defteri",
        "footer_credits": "© 2026 Burak Tekiner",
        "lang_switch_tooltip": "Dili Değiştir (TR / EN)",

        # Common Actions & Dialogs
        "select_file": "Dosya Seç",
        "save_as": "Farklı Kaydet",
        "selected_file": "Seçilen Dosya: {file}",
        "none_selected": "Yok",
        "success": "Başarılı",
        "error": "Hata",
        "info": "Bilgi",
        "warning": "Uyarı",
        "cancel": "İptal",
        "apply": "Uygula",
        "save": "Kaydet",
        "delete": "Sil",
        "clear": "Temizle",
        "preview": "Önizleme",
        "unsupported_file": "Desteklenmeyen Dosya",
        "unsupported_file_msg": "Seçilen dosya formatı desteklenmiyor (.pdf, .docx, .xlsx, .xls, .md, .txt, .png, .jpg, .jpeg, .bmp, .webp, .tiff).",
        "please_select_file": "Lütfen önce bir dosya seçin.",

        # Dropzone
        "drop_zone_text": "Dosyayı buraya sürükleyin veya seçmek için tıklayın",
        "drop_zone_active": "Dosyayı buraya bırakın",

        # Page: Convert
        "grp_export_pdf": "PDF'den Dönüştür",
        "grp_import_pdf": "PDF'e Dönüştür",
        "btn_pdf_to_word": "PDF -> Word (DOCX)",
        "btn_pdf_to_excel": "PDF -> Excel (XLSX)",
        "btn_pdf_to_md": "PDF -> Markdown (MD)",
        "btn_word_to_pdf": "Word -> PDF",
        "btn_excel_to_pdf": "Excel -> PDF",
        "btn_md_to_pdf": "Markdown -> PDF",
        "btn_image_to_pdf": "Görsel -> PDF",
        "ocr_lang_label": "OCR Tanıma Dili:",
        "ocr_lang_tr": "🇹🇷 Türkçe",
        "ocr_lang_en": "🇬🇧 English",
        "ocr_lang_latin": "🌐 Çok Dilli / Latin",
        "md_info_msg": "Markdown dönüştürme için sol menüden 'Görsel İşlemleri -> OCR' modülünü kullanabilirsiniz.",
        "msg_pdf_word_digital": "PDF (Dijital) başarıyla DOCX formatına dönüştürüldü.",
        "msg_pdf_word_ocr": "PDF (Taranmış/OCR) başarıyla DOCX formatına dönüştürüldü.",
        "msg_pdf_excel_success": "PDF başarıyla XLSX formatına dönüştürüldü ({layer}).",
        "msg_word_pdf_success": "Word dosyası başarıyla PDF'e dönüştürüldü.",
        "msg_excel_pdf_success": "Excel dosyası başarıyla PDF'e dönüştürüldü.",
        "msg_md_pdf_success": "Markdown dosyası başarıyla PDF'e dönüştürüldü.",
        "msg_image_pdf_success": "Görsel dosyası başarıyla PDF'e dönüştürüldü.",

        # Page: PDF Tools
        "tab_merge": "Birleştir",
        "tab_reorder": "Sırala / Sayfa Sil",
        "tab_compress": "Sıkıştır & Optimize Et",
        "tab_metadata": "Metadata Temizle",
        "btn_add_pdf": "PDF Ekle",
        "btn_merge_pdfs": "Seçilenleri Birleştir",
        "btn_reorder_save": "Yeni PDF Olarak Kaydet",
        "btn_compress_pdf": "PDF'i Sıkıştır",
        "btn_clean_metadata": "Metadata Temizle ve Kaydet",
        "lbl_page_order": "Sayfa Sırası (Örn: 1,3,5-8):",
        "lbl_compress_level": "Sıkıştırma Seviyesi:",
        "compress_standard": "Standart (Dengeli)",
        "compress_high": "Yüksek (Küçük Boyut)",
        "msg_merge_success": "PDF dosyaları başarıyla birleştirildi.",
        "msg_reorder_success": "Sayfalar başarıyla yeniden sıralandı.",
        "msg_compress_success": "PDF başarıyla sıkıştırıldı.\nEski Boyut: {old_size}\nYeni Boyut: {new_size} ({ratio}% tasarruf)",
        "msg_meta_success": "Metadata başarıyla temizlendi.",

        # Page: Security & KVKK
        "tab_redact": "KVKK & Metin Karartma",
        "tab_encrypt": "Şifreleme & İzinler",
        "lbl_search_redact": "Karartılacak Kelimeler / Kalıplar (Virgülle ayırın):",
        "placeholder_redact": "Örn: TC Kimlik, IBAN, İsim, Soyisim",
        "chk_reversible": "Geri Döndürülebilir Karartma (Şifreli Katman)",
        "btn_apply_redaction": "Karartmayı Uygula ve Kaydet",
        "lbl_password": "PDF Şifresi:",
        "btn_encrypt_pdf": "Şifrele ve Kaydet",
        "btn_decrypt_pdf": "Şifreyi Çöz ve Kaydet",
        "msg_redact_success": "KVKK metin karartma başarıyla tamamlandı.",
        "msg_encrypt_success": "PDF başarıyla şifrelendi.",
        "msg_decrypt_success": "PDF şifresi başarıyla kaldırıldı.",

        # Page: ETDS
        "etds_title": "Elektronik Tebligat & Şablon Doldurma Modülü",
        "etds_desc": "Resmi tebligat ekleri, karar örnekleri ve genel kurul tutanakları için şablon doldurucu.",
        "lbl_template": "Şablon Seçimi:",
        "btn_fill_template": "Şablonu Doldur ve Kaydet",
        "msg_template_success": "Şablon başarıyla dolduruldu ve kaydedildi.",

        # Page: Watermark
        "tab_add_watermark": "Filigran Ekle",
        "tab_remove_watermark": "Filigran Temizle",
        "lbl_watermark_text": "Filigran Metni:",
        "placeholder_watermark": "Örn: GİZLİDİR, TASLAK, KOPYA",
        "lbl_opacity": "Şeffaflık (Opaklık):",
        "lbl_font_size": "Yazı Boyutu:",
        "lbl_angle": "Açı (Derece):",
        "btn_apply_watermark": "Filigran Ekle ve Kaydet",
        "btn_remove_watermark": "Filigranı Kaldır ve Kaydet",
        "msg_wm_add_success": "Filigran başarıyla eklendi.",
        "msg_wm_rem_success": "Filigran temizleme işlemi tamamlandı.",

        # Page: Signature
        "lbl_sig_image": "İmza Görseli:",
        "btn_select_sig": "İmza Görseli Seç",
        "chk_transparent_sig": "İmza Arka Planını Şeffaflaştır",
        "lbl_sig_page": "İmza Basılacak Sayfa:",
        "lbl_sig_position": "İmza Konumu:",
        "pos_bottom_right": "Sağ Alt",
        "pos_bottom_left": "Sol Alt",
        "pos_top_right": "Sağ Üst",
        "pos_top_left": "Sol Üst",
        "btn_sign_pdf": "PDF'i İmzala ve Kaydet",
        "msg_sign_success": "İmza başarıyla PDF'e eklendi.",

        # Page: Image Tools
        "grp_image_settings": "Görsel Ayarları",
        "lbl_width": "Genişlik (0 ise oran korunur):",
        "lbl_height": "Yükseklik:",
        "lbl_output_format": "Çıktı Formatı:",
        "lbl_color_mode": "Renk Uzayı:",
        "chk_pad_image": "Oranı Koru ve Boşlukları Doldur (Padding)",
        "chk_smart_scan": "Akıllı Tarama (Otomatik Yön & Kontrast)",
        "lbl_dpi": "DPI:",
        "btn_apply_image": "Uygula ve Kaydet",
        "msg_image_success": "Görsel başarıyla dönüştürüldü.",

        # Page: Notepad
        "notepad_title": "Entegre Not Defteri",
        "btn_open_file": "Dosya Aç (.txt / .md)",
        "btn_save_file": "Kaydet",
        "btn_export_pdf": "PDF Olarak Dışa Aktar",
        "msg_note_saved": "Not başarıyla kaydedildi.",
        "msg_note_pdf_exported": "Not başarıyla PDF olarak dışa aktarıldı."
    },
    "en": {
        # App Title & Navigation
        "app_title": "Cevirgec PDF V.2.0",
        "app_brand": "CEVIRGEC PDF",
        "nav_convert": "Convert PDF",
        "nav_pdf_tools": "PDF Tools",
        "nav_security": "Security & GDPR",
        "nav_etds": "ETDS Module",
        "nav_watermark": "Watermark",
        "nav_signature": "Signature",
        "nav_image": "Image Tools",
        "nav_notepad": "Notepad",
        "footer_credits": "© 2026 Burak Tekiner",
        "lang_switch_tooltip": "Switch Language (TR / EN)",

        # Common Actions & Dialogs
        "select_file": "Select File",
        "save_as": "Save As",
        "selected_file": "Selected File: {file}",
        "none_selected": "None",
        "success": "Success",
        "error": "Error",
        "info": "Information",
        "warning": "Warning",
        "cancel": "Cancel",
        "apply": "Apply",
        "save": "Save",
        "delete": "Delete",
        "clear": "Clear",
        "preview": "Preview",
        "unsupported_file": "Unsupported File",
        "unsupported_file_msg": "Selected file format is not supported (.pdf, .docx, .xlsx, .xls, .md, .txt, .png, .jpg, .jpeg, .bmp, .webp, .tiff).",
        "please_select_file": "Please select a file first.",

        # Dropzone
        "drop_zone_text": "Drag and drop a file here or click to select",
        "drop_zone_active": "Drop file here",

        # Page: Convert
        "grp_export_pdf": "Convert from PDF",
        "grp_import_pdf": "Convert to PDF",
        "btn_pdf_to_word": "PDF -> Word (DOCX)",
        "btn_pdf_to_excel": "PDF -> Excel (XLSX)",
        "btn_pdf_to_md": "PDF -> Markdown (MD)",
        "btn_word_to_pdf": "Word -> PDF",
        "btn_excel_to_pdf": "Excel -> PDF",
        "btn_md_to_pdf": "Markdown -> PDF",
        "btn_image_to_pdf": "Image -> PDF",
        "ocr_lang_label": "OCR Language:",
        "ocr_lang_tr": "🇹🇷 Turkish",
        "ocr_lang_en": "🇬🇧 English",
        "ocr_lang_latin": "🌐 Multilingual / Latin",
        "md_info_msg": "For Markdown conversion, you can use the 'Image Tools -> OCR' module on the left menu.",
        "msg_pdf_word_digital": "PDF (Digital) was successfully converted to DOCX.",
        "msg_pdf_word_ocr": "PDF (Scanned/OCR) was successfully converted to DOCX.",
        "msg_pdf_excel_success": "PDF was successfully converted to XLSX ({layer}).",
        "msg_word_pdf_success": "Word document was successfully converted to PDF.",
        "msg_excel_pdf_success": "Excel spreadsheet was successfully converted to PDF.",
        "msg_md_pdf_success": "Markdown file was successfully converted to PDF.",
        "msg_image_pdf_success": "Image was successfully converted to PDF.",

        # Page: PDF Tools
        "tab_merge": "Merge",
        "tab_reorder": "Reorder / Delete Pages",
        "tab_compress": "Compress & Optimize",
        "tab_metadata": "Clean Metadata",
        "btn_add_pdf": "Add PDF",
        "btn_merge_pdfs": "Merge Selected",
        "btn_reorder_save": "Save as New PDF",
        "btn_compress_pdf": "Compress PDF",
        "btn_clean_metadata": "Clean Metadata & Save",
        "lbl_page_order": "Page Order (e.g. 1,3,5-8):",
        "lbl_compress_level": "Compression Level:",
        "compress_standard": "Standard (Balanced)",
        "compress_high": "High (Smallest Size)",
        "msg_merge_success": "PDF files were successfully merged.",
        "msg_reorder_success": "Pages were successfully reordered.",
        "msg_compress_success": "PDF was successfully compressed.\nOriginal Size: {old_size}\nNew Size: {new_size} ({ratio}% saved)",
        "msg_meta_success": "Metadata was successfully cleaned.",

        # Page: Security & KVKK
        "tab_redact": "GDPR & Text Redaction",
        "tab_encrypt": "Encryption & Permissions",
        "lbl_search_redact": "Words / Patterns to Redact (comma separated):",
        "placeholder_redact": "E.g. National ID, IBAN, Full Name",
        "chk_reversible": "Reversible Redaction (Encrypted Layer)",
        "btn_apply_redaction": "Apply Redaction & Save",
        "lbl_password": "PDF Password:",
        "btn_encrypt_pdf": "Encrypt & Save",
        "btn_decrypt_pdf": "Decrypt & Save",
        "msg_redact_success": "GDPR text redaction completed successfully.",
        "msg_encrypt_success": "PDF was successfully encrypted.",
        "msg_decrypt_success": "PDF password was successfully removed.",

        # Page: ETDS
        "etds_title": "Electronic Notification & Template Filler Module",
        "etds_desc": "Template filler for formal notification attachments, decision records, and general assembly minutes.",
        "lbl_template": "Select Template:",
        "btn_fill_template": "Fill Template & Save",
        "msg_template_success": "Template was successfully filled and saved.",

        # Page: Watermark
        "tab_add_watermark": "Add Watermark",
        "tab_remove_watermark": "Remove Watermark",
        "lbl_watermark_text": "Watermark Text:",
        "placeholder_watermark": "E.g. CONFIDENTIAL, DRAFT, COPY",
        "lbl_opacity": "Opacity (Transparency):",
        "lbl_font_size": "Font Size:",
        "lbl_angle": "Angle (Degrees):",
        "btn_apply_watermark": "Apply Watermark & Save",
        "btn_remove_watermark": "Remove Watermark & Save",
        "msg_wm_add_success": "Watermark was successfully added.",
        "msg_wm_rem_success": "Watermark removal process completed.",

        # Page: Signature
        "lbl_sig_image": "Signature Image:",
        "btn_select_sig": "Select Signature Image",
        "chk_transparent_sig": "Make Signature Background Transparent",
        "lbl_sig_page": "Page to Sign:",
        "lbl_sig_position": "Signature Position:",
        "pos_bottom_right": "Bottom Right",
        "pos_bottom_left": "Bottom Left",
        "pos_top_right": "Top Right",
        "pos_top_left": "Top Left",
        "btn_sign_pdf": "Sign PDF & Save",
        "msg_sign_success": "Signature was successfully added to PDF.",

        # Page: Image Tools
        "grp_image_settings": "Image Settings",
        "lbl_width": "Width (0 to preserve aspect ratio):",
        "lbl_height": "Height:",
        "lbl_output_format": "Output Format:",
        "lbl_color_mode": "Color Space:",
        "chk_pad_image": "Preserve Aspect Ratio with Padding",
        "chk_smart_scan": "Smart Scan (Auto-Orientation & Contrast)",
        "lbl_dpi": "DPI:",
        "btn_apply_image": "Apply & Save",
        "msg_image_success": "Image was successfully converted.",

        # Page: Notepad
        "notepad_title": "Integrated Notepad",
        "btn_open_file": "Open File (.txt / .md)",
        "btn_save_file": "Save",
        "btn_export_pdf": "Export as PDF",
        "msg_note_saved": "Note was successfully saved.",
        "msg_note_pdf_exported": "Note was successfully exported to PDF."
    }
}

_current_language = "tr"
_listeners: List[Callable[[str], None]] = []

def _load_config():
    global _current_language
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                _current_language = data.get("language", "tr")
    except Exception:
        _current_language = "tr"

def _save_config():
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        config = {}
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception:
                config = {}
        config["language"] = _current_language
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# Initialize config on module load
_load_config()

def get_language() -> str:
    return _current_language

def set_language(lang: str) -> None:
    global _current_language
    if lang not in TRANSLATIONS:
        lang = "tr"
    if _current_language != lang:
        _current_language = lang
        _save_config()
        for callback in _listeners:
            try:
                callback(_current_language)
            except Exception:
                pass

def toggle_language() -> str:
    new_lang = "en" if _current_language == "tr" else "tr"
    set_language(new_lang)
    return new_lang

def add_language_listener(callback: Callable[[str], None]) -> None:
    if callback not in _listeners:
        _listeners.append(callback)

def remove_language_listener(callback: Callable[[str], None]) -> None:
    if callback in _listeners:
        _listeners.remove(callback)

def t(key: str, **kwargs) -> str:
    """
    Get localized string for current language with optional format kwargs.
    Falls back to Turkish if key not found in selected language,
    or returns the key itself if not found anywhere.
    """
    lang_dict = TRANSLATIONS.get(_current_language, TRANSLATIONS["tr"])
    text = lang_dict.get(key)
    if text is None:
        text = TRANSLATIONS["tr"].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

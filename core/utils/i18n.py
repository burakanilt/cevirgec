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
        "nav_viewer": "PDF Görüntüleyici",
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
        "btn_export_md": "MD Olarak Dışa Aktar",
        "msg_note_saved": "Not başarıyla kaydedildi.",
        "msg_note_md_exported": "Not başarıyla MD olarak dışa aktarıldı.",

        # Page: PDF Viewer
        "viewer_title": "PDF Görüntüleyici",
        "viewer_subtitle": "PDF dosyalarınızı hızlıca açın, okuyun, arayın ve yazdırın — tamamen çevrimdışı.",
        "viewer_open": "PDF Aç",
        "viewer_open_tip": "PDF Aç (Ctrl+O)",
        "viewer_drop_hint": "veya PDF dosyalarını bu pencereye sürükleyip bırakın",
        "viewer_recent": "Son Açılanlar",
        "viewer_recent_empty": "Henüz açılmış bir dosya yok",
        "viewer_clear_recent": "Listeyi Temizle",
        "viewer_set_default": "Varsayılan PDF Uygulaması Yap",
        "viewer_default_done": "Çevirgeç PDF, Windows'a PDF görüntüleyici olarak kaydedildi.\n\nŞimdi açılacak Windows Ayarları'nda '.pdf' türü için 'Çevirgeç PDF'i seçerek işlemi tamamlayın.\n(Alternatif: bir PDF'e sağ tıklayın → Birlikte aç → Başka bir uygulama seç → Çevirgeç PDF → Her zaman.)",
        "viewer_default_unsupported": "Bu özellik yalnızca Windows'ta kullanılabilir.",
        "viewer_sidebar": "Kenar Çubuğu (F4)",
        "viewer_thumbnails": "Sayfalar",
        "viewer_bookmarks": "Yer İmleri",
        "viewer_no_bookmarks": "Bu belgede yer imi yok",
        "viewer_print": "Yazdır (Ctrl+P)",
        "viewer_first_page": "İlk Sayfa (Home)",
        "viewer_prev_page": "Önceki Sayfa (←)",
        "viewer_next_page": "Sonraki Sayfa (→)",
        "viewer_last_page": "Son Sayfa (End)",
        "viewer_goto_page": "Sayfaya Git (Ctrl+G)",
        "viewer_page_of": "/ {total}",
        "viewer_zoom_in": "Yakınlaştır (Ctrl++)",
        "viewer_zoom_out": "Uzaklaştır (Ctrl+-)",
        "viewer_fit_width": "Sayfa Genişliği (Ctrl+2)",
        "viewer_fit_page": "Tam Sayfa (Ctrl+0)",
        "viewer_zoom_fit_width": "Genişliğe Sığdır",
        "viewer_zoom_fit_page": "Sayfaya Sığdır",
        "viewer_continuous": "Sürekli Kaydırma / Tek Sayfa",
        "viewer_search": "Belgede Ara (Ctrl+F)",
        "viewer_search_placeholder": "Belgede ara...",
        "viewer_search_none": "Sonuç yok",
        "viewer_search_count": "{current} / {total}",
        "viewer_search_prev": "Önceki Sonuç (Shift+F3)",
        "viewer_search_next": "Sonraki Sonuç (F3 / Enter)",
        "viewer_search_close": "Kapat (Esc)",
        "viewer_fullscreen": "Okuma Modu / Tam Ekran (F11)",
        "viewer_more": "Diğer İşlemler",
        "viewer_properties": "Belge Özellikleri",
        "viewer_copy_page_text": "Bu Sayfanın Metnini Kopyala",
        "viewer_copied": "Sayfa {page} metni panoya kopyalandı.",
        "viewer_no_text": "Bu sayfada seçilebilir metin yok (taranmış bir belge olabilir).\nMetni çıkarmak için 'PDF Dönüştür' modülündeki OCR'ı kullanabilirsiniz.",
        "viewer_send_convert": "Dönüştürücüde Aç",
        "viewer_show_in_folder": "Klasörde Göster",
        "viewer_password_title": "Parola Gerekli",
        "viewer_password_prompt": "'{file}' parola korumalı.\nLütfen parolayı girin:",
        "viewer_password_wrong": "Parola yanlış. Lütfen tekrar deneyin:",
        "viewer_load_error": "'{file}' açılamadı:\n{error}",
        "viewer_err_not_found": "Dosya bulunamadı.",
        "viewer_err_invalid": "Geçersiz veya bozuk PDF dosyası.",
        "viewer_err_security": "Desteklenmeyen güvenlik/şifreleme yöntemi.",
        "viewer_err_unknown": "Bilinmeyen hata.",
        "viewer_printing": "Yazdırılıyor...",
        "viewer_print_error": "Yazıcı başlatılamadı.",
        "viewer_prop_file": "Dosya",
        "viewer_prop_path": "Konum",
        "viewer_prop_size": "Dosya Boyutu",
        "viewer_prop_pages": "Sayfa Sayısı",
        "viewer_prop_page_size": "Sayfa Boyutu",
        "viewer_prop_title": "Başlık",
        "viewer_prop_author": "Yazar",
        "viewer_prop_subject": "Konu",
        "viewer_prop_keywords": "Anahtar Kelimeler",
        "viewer_prop_creator": "Oluşturan Uygulama",
        "viewer_prop_producer": "PDF Üretici",
        "viewer_prop_created": "Oluşturulma",
        "viewer_prop_modified": "Değiştirilme",
        "viewer_close": "Kapat",
        
        # PDF Viewer Annotations & Tools
        "viewer_tool_select": "Seçim (V)",
        "viewer_tool_highlight": "Vurgula",
        "viewer_tool_underline": "Altını Çiz",
        "viewer_tool_strikeout": "Üstünü Çiz",
        "viewer_tool_ink": "Kalem",
        "viewer_tool_freetext": "Metin Kutusu",
        "viewer_tool_text_note": "Yapışkan Not",
        "viewer_save": "Kaydet",
        "viewer_save_tip": "Kaydet (Ctrl+S)",
        "viewer_save_as": "Farklı Kaydet",
        "viewer_save_as_tip": "Farklı Kaydet...",
        "viewer_print_tip": "Yazdır (Ctrl+P)",
        "viewer_annotations": "Notlar & İşaretler",
        "viewer_no_annotations": "Bu belgede henüz not/işaret yok.",
        "viewer_unsaved_changes": "Kaydedilmemiş değişiklikler var. Kapatmadan önce kaydetmek ister misiniz?",
        "viewer_color_yellow": "Sarı",
        "viewer_color_green": "Yeşil",
        "viewer_color_pink": "Pembe",
        "viewer_color_blue": "Mavi",
        "viewer_delete_annotation": "Notu/İşareti Sil",
        "viewer_saved": "Değişiklikler kaydedildi."
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
        "nav_viewer": "PDF Viewer",
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
        "btn_export_md": "Export as MD",
        "msg_note_saved": "Note was successfully saved.",
        "msg_note_md_exported": "Note was successfully exported to MD.",

        # Page: PDF Viewer
        "viewer_title": "PDF Viewer",
        "viewer_subtitle": "Open, read, search and print your PDFs quickly — fully offline.",
        "viewer_open": "Open PDF",
        "viewer_open_tip": "Open PDF (Ctrl+O)",
        "viewer_drop_hint": "or drag and drop PDF files onto this window",
        "viewer_recent": "Recent Files",
        "viewer_recent_empty": "No recently opened files yet",
        "viewer_clear_recent": "Clear List",
        "viewer_set_default": "Set as Default PDF App",
        "viewer_default_done": "Cevirgec PDF was registered with Windows as a PDF viewer.\n\nIn the Windows Settings page that opens now, choose 'Çevirgeç PDF' for the '.pdf' type to finish.\n(Alternative: right-click a PDF → Open with → Choose another app → Çevirgeç PDF → Always.)",
        "viewer_default_unsupported": "This feature is only available on Windows.",
        "viewer_sidebar": "Sidebar (F4)",
        "viewer_thumbnails": "Pages",
        "viewer_bookmarks": "Bookmarks",
        "viewer_no_bookmarks": "This document has no bookmarks",
        "viewer_print": "Print (Ctrl+P)",
        "viewer_first_page": "First Page (Home)",
        "viewer_prev_page": "Previous Page (←)",
        "viewer_next_page": "Next Page (→)",
        "viewer_last_page": "Last Page (End)",
        "viewer_goto_page": "Go to Page (Ctrl+G)",
        "viewer_page_of": "/ {total}",
        "viewer_zoom_in": "Zoom In (Ctrl++)",
        "viewer_zoom_out": "Zoom Out (Ctrl+-)",
        "viewer_fit_width": "Fit Width (Ctrl+2)",
        "viewer_fit_page": "Fit Page (Ctrl+0)",
        "viewer_zoom_fit_width": "Fit Width",
        "viewer_zoom_fit_page": "Fit Page",
        "viewer_continuous": "Continuous Scroll / Single Page",
        "viewer_search": "Find in Document (Ctrl+F)",
        "viewer_search_placeholder": "Find in document...",
        "viewer_search_none": "No results",
        "viewer_search_count": "{current} / {total}",
        "viewer_search_prev": "Previous Result (Shift+F3)",
        "viewer_search_next": "Next Result (F3 / Enter)",
        "viewer_search_close": "Close (Esc)",
        "viewer_fullscreen": "Reading Mode / Full Screen (F11)",
        "viewer_more": "More Actions",
        "viewer_properties": "Document Properties",
        "viewer_copy_page_text": "Copy Text of This Page",
        "viewer_copied": "Text of page {page} was copied to the clipboard.",
        "viewer_no_text": "This page has no selectable text (it may be a scanned document).\nUse the OCR in the 'Convert PDF' module to extract its text.",
        "viewer_send_convert": "Open in Converter",
        "viewer_show_in_folder": "Show in Folder",
        "viewer_password_title": "Password Required",
        "viewer_password_prompt": "'{file}' is password protected.\nPlease enter the password:",
        "viewer_password_wrong": "Wrong password. Please try again:",
        "viewer_load_error": "Could not open '{file}':\n{error}",
        "viewer_err_not_found": "File not found.",
        "viewer_err_invalid": "Invalid or corrupted PDF file.",
        "viewer_err_security": "Unsupported security/encryption scheme.",
        "viewer_err_unknown": "Unknown error.",
        "viewer_printing": "Printing...",
        "viewer_print_error": "Could not start the printer.",
        "viewer_prop_file": "File",
        "viewer_prop_path": "Location",
        "viewer_prop_size": "File Size",
        "viewer_prop_pages": "Page Count",
        "viewer_prop_page_size": "Page Size",
        "viewer_prop_title": "Title",
        "viewer_prop_author": "Author",
        "viewer_prop_subject": "Subject",
        "viewer_prop_keywords": "Keywords",
        "viewer_prop_creator": "Creator Application",
        "viewer_prop_producer": "PDF Producer",
        "viewer_prop_created": "Created",
        "viewer_prop_modified": "Modified",
        "viewer_close": "Close",

        # PDF Viewer Annotations & Tools
        "viewer_tool_select": "Select (V)",
        "viewer_tool_highlight": "Highlight",
        "viewer_tool_underline": "Underline",
        "viewer_tool_strikeout": "Strikethrough",
        "viewer_tool_ink": "Pen",
        "viewer_tool_freetext": "Text Box",
        "viewer_tool_text_note": "Sticky Note",
        "viewer_save": "Save",
        "viewer_save_tip": "Save (Ctrl+S)",
        "viewer_save_as": "Save As",
        "viewer_save_as_tip": "Save As...",
        "viewer_print_tip": "Print (Ctrl+P)",
        "viewer_annotations": "Notes & Markups",
        "viewer_no_annotations": "No annotations/markups in this document yet.",
        "viewer_unsaved_changes": "There are unsaved changes. Do you want to save before closing?",
        "viewer_color_yellow": "Yellow",
        "viewer_color_green": "Green",
        "viewer_color_pink": "Pink",
        "viewer_color_blue": "Blue",
        "viewer_delete_annotation": "Delete Annotation/Markup",
        "viewer_saved": "Changes saved."
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

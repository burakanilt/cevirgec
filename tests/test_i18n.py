import pytest
from core.utils.i18n import t, get_language, set_language, toggle_language, add_language_listener, remove_language_listener, TRANSLATIONS

def test_i18n_key_parity():
    """Ensure all translation keys exist in both Turkish and English."""
    tr_keys = set(TRANSLATIONS["tr"].keys())
    en_keys = set(TRANSLATIONS["en"].keys())
    
    missing_in_en = tr_keys - en_keys
    missing_in_tr = en_keys - tr_keys
    
    assert not missing_in_en, f"Keys missing in EN: {missing_in_en}"
    assert not missing_in_tr, f"Keys missing in TR: {missing_in_tr}"

def test_i18n_translation_and_formatting():
    """Test text retrieval and kwargs formatting in both languages."""
    set_language("tr")
    assert get_language() == "tr"
    assert t("nav_convert") == "PDF Dönüştür"
    assert t("selected_file", file="test.pdf") == "Seçilen Dosya: test.pdf"
    
    set_language("en")
    assert get_language() == "en"
    assert t("nav_convert") == "Convert PDF"
    assert t("selected_file", file="test.pdf") == "Selected File: test.pdf"

def test_i18n_toggle_and_listeners():
    """Test language toggling and listener callbacks."""
    set_language("tr")
    events = []
    
    def on_lang(lang):
        events.append(lang)
        
    add_language_listener(on_lang)
    
    new_lang = toggle_language()
    assert new_lang == "en"
    assert get_language() == "en"
    assert events == ["en"]
    
    new_lang = toggle_language()
    assert new_lang == "tr"
    assert get_language() == "tr"
    assert events == ["en", "tr"]
    
    remove_language_listener(on_lang)
    toggle_language()
    assert len(events) == 2 # No new events after removal
    
    # Reset to TR
    set_language("tr")

def test_ocr_engine_lang_support():
    """Test that core.ocr.engine.run_ocr accepts lang parameter without errors."""
    from PIL import Image
    from core.ocr.engine import run_ocr
    
    # Create small dummy blank image
    img = Image.new("RGB", (100, 40), color=(255, 255, 255))
    
    # Calling run_ocr with different languages
    res_tr = run_ocr(img, lang="tr")
    res_en = run_ocr(img, lang="en")
    res_latin = run_ocr(img, lang="latin")
    
    # Blank image returns None or empty list
    assert res_tr is None or isinstance(res_tr, list)
    assert res_en is None or isinstance(res_en, list)
    assert res_latin is None or isinstance(res_latin, list)

"""Tests for core.pdf_annotations (viewer annotation layer)."""
import os

import fitz
import pytest

from core import pdf_annotations as pa


@pytest.fixture
def sample_pdf(tmp_path):
    path = tmp_path / "sample.pdf"
    doc = fitz.open()
    for i in range(3):
        page = doc.new_page()
        page.insert_text((72, 100), f"Sayfa {i + 1} merhaba dunya", fontsize=14)
        page.insert_text((72, 130), "ikinci satir burada", fontsize=14)
    doc.save(str(path))
    doc.close()
    return str(path)


def test_select_words_and_text(sample_pdf):
    doc = fitz.open(sample_pdf)
    page = doc[0]
    words = pa.page_words(page)
    sel = pa.select_words(words, fitz.Point(75, 95), fitz.Point(200, 125))
    text = pa.words_text(sel)
    assert text.startswith("Sayfa 1")
    assert "\n" in text  # spans two lines
    assert len(pa.line_rects(sel)) == 2


def test_markup_note_ink_textbox_roundtrip(sample_pdf, tmp_path):
    doc = fitz.open(sample_pdf)
    page = doc[0]
    words = pa.page_words(page)
    sel = pa.select_words(words, fitz.Point(75, 95), fitz.Point(150, 95))
    for kind in ("highlight", "underline", "strikeout"):
        assert pa.add_text_markup(page, kind, pa.line_rects(sel), pa.COLORS["green"]) is not None
    pa.add_sticky_note(page, fitz.Point(300, 300), "Türkçe not: ğüşıöç")
    pa.add_ink(page, [[fitz.Point(100, 400), fitz.Point(150, 420), fitz.Point(200, 400)]])
    box = pa.add_text_box(doc[1], fitz.Point(72, 200), "Kutu ŞĞİ")

    infos = pa.list_annotations(doc)
    assert len(infos) == 6
    note = next(i for i in infos if i.type_id == fitz.PDF_ANNOT_TEXT)
    assert note.content == "Türkçe not: ğüşıöç"
    hl = next(i for i in infos if i.type_id == fitz.PDF_ANNOT_HIGHLIGHT)
    assert "merhaba" in hl.content or "Sayfa" in hl.content

    # edit + hit test + delete
    assert pa.set_annot_content(doc[1], box.xref, "Yeni metin")
    hit = pa.annot_at(page, fitz.Point(301, 301))
    assert hit is not None and hit.type[0] == fitz.PDF_ANNOT_TEXT
    assert pa.delete_annot(page, hit.xref)

    # Save incrementally onto the original, then Save As
    doc, mode = pa.save_document(doc, sample_pdf)
    assert mode == "incremental"
    other = str(tmp_path / "kopya.pdf")
    doc, mode = pa.save_document(doc, other)
    assert mode == "full" and os.path.normcase(doc.name) == os.path.normcase(other)
    infos = pa.list_annotations(doc)
    assert len(infos) == 5
    assert any(i.content == "Yeni metin" for i in infos)
    doc.close()


def test_rotation_mapping(sample_pdf):
    doc = fitz.open(sample_pdf)
    page = doc[0]
    page.set_rotation(90)
    p = fitz.Point(100, 50)
    back = pa.to_display_space(page, pa.to_page_space(page, p))
    assert abs(back.x - p.x) < 1e-6 and abs(back.y - p.y) < 1e-6


def test_recent_files_and_last_page(tmp_path, monkeypatch):
    from core.utils import app_config
    monkeypatch.setattr(app_config, "CONFIG_PATH", str(tmp_path / "config.json"))
    f1 = tmp_path / "a.pdf"; f1.write_bytes(b"%PDF")
    f2 = tmp_path / "b.pdf"; f2.write_bytes(b"%PDF")
    app_config.add_recent_file(str(f1))
    app_config.add_recent_file(str(f2))
    app_config.add_recent_file(str(f1))
    assert app_config.get_recent_files() == [str(f1), str(f2)]
    app_config.set_last_page(str(f1), 7)
    assert app_config.get_last_page(str(f1)) == 7
    assert app_config.get_last_page(str(f2)) == 0

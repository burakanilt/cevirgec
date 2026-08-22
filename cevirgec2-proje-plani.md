# ÇEVİRGEÇ2 — Yeniden Yapılanma Teknik Planı

Hedef: Hızlı, tamamen offline, Windows (.exe) + Linux (AppImage) çalışan belge dönüştürme ve PDF araç seti. V1'in hızını koruyup taranmış/eski PDF sorununu çözer.

---

## 1. ALTIN KURALLAR (mimari anayasa)

1. **torch / transformers / GLM-OCR YASAK.** Hantallığın kaynağı buydu. OCR tamamen ONNX runtime üzerinden.
2. **Lazy import:** OCR ve tablo motorları uygulama açılışında DEĞİL, ilk kullanımda yüklenir. Açılış hedefi < 2 saniye.
3. **UI asla kilitlenmez:** Tüm işler QThreadPool worker'larında, progress callback ile.
4. **core/ klasörü UI'dan %100 bağımsız:** Her fonksiyon `cli.py` üzerinden UI olmadan test edilebilir.
5. **Sayfa bazlı akıllı router:** Metin katmanı olan sayfa OCR'a asla girmez.
6. **Safe Append:** V1'den çalışan kod (PyMuPDF birleştirme/bölme, imza yerleştirme) aynen taşınır, yeniden yazılmaz.

---

## 2. TEKNOLOJİ YIĞINI

| Katman | Teknoloji | Neden |
|---|---|---|
| Dil | Python 3.12 | Mevcut kod tabanı + AI agent uyumu |
| UI | **PySide6 (Qt Widgets)** | CustomTkinter'dan hızlı, native görünüm, Win+Linux, olgun |
| PDF çekirdek | PyMuPDF (fitz) | Birleştir/böl/sıkıştır/filigran/imza — V1'den taşınır |
| PDF→Word | **pdf2docx** (metin katmanlı) + python-docx (OCR sonucu yeniden inşa) | pdf2docx layout'u çok iyi korur |
| PDF→Excel | pdfplumber (metin katmanlı tablo) + **img2table** (taranmış tablo) | |
| PDF→Markdown | **pymupdf4llm** | Tek satırda kaliteli MD çıktısı |
| OCR ana motor | **rapidocr_onnxruntime** | PaddleOCR kalitesi, torch YOK, CPU'da hızlı (~1-2 sn/sayfa), TR destekli, modeller offline paketlenir (~15 MB) |
| OCR yedek | pytesseract (opsiyonel, sistemde varsa) | Zorunlu bağımlılık değil |
| Görsel işlem | Pillow | Çözünürlük/DPI/piksel/format |
| Islak imza | Pillow (beyaz zemin temizleme) + PyMuPDF (yerleştirme) | |
| Not defteri | QPlainTextEdit + otomatik kayıt (QSettings + dosya) | |
| Build | **PyInstaller (onedir modu)** | onefile değil — onedir açılışta 5-10x hızlı |
| Linux paket | AppImage (appimagetool) | Tek dosya, kurulumsuz |
| Win installer | Inno Setup (opsiyonel) | |

**V2'nin asıl silahı RapidOCR:** GLM-OCR kalitesine yakın sonucu, 3 GB yerine 15 MB modelle, 6 dakika yerine saniyeler içinde, internet olmadan verir. docTR/img2table+docTR denemesindeki torch yükü tamamen ortadan kalkar.

---

## 3. DOSYA YAPISI

```
cevirgec2/
├── app.py                      # Giriş noktası (sadece QApplication başlatır)
├── cli.py                      # core/ fonksiyonlarını UI'sız test etme aracı
├── requirements.txt            # Çalışma bağımlılıkları
├── requirements-dev.txt        # pyinstaller, pytest
│
├── assets/
│   ├── icons/                  # .ico (Win) + .png (Linux)
│   ├── fonts/                  # PDF üretiminde TR karakter için (DejaVu vb.)
│   └── models/                 # RapidOCR .onnx modelleri (det+rec+cls, offline)
│
├── core/                       # === UI'DAN TAMAMEN BAĞIMSIZ ===
│   ├── __init__.py
│   ├── router.py               # Sayfa analizi: metin katmanı mı, tarama mı?
│   │                           #   kural: sayfa >= 30 kelime → dijital
│   │                           #          değilse → OCR hattı
│   ├── pdf_ops.py              # birleştir, böl, döndür, sıkıştır, sayfa sil/sırala
│   ├── watermark.py            # filigran ekle (metin/görsel) + kaldır
│   ├── signature.py            # imza fotoğrafı: zemin temizle → PNG → yerleştir
│   │
│   ├── convert/
│   │   ├── __init__.py
│   │   ├── to_word.py          # dijital: pdf2docx | taranmış: OCR → python-docx
│   │   ├── to_excel.py         # dijital: pdfplumber | taranmış: img2table
│   │   ├── to_md.py            # pymupdf4llm (dijital) | OCR → md (taranmış)
│   │   ├── to_pdf.py           # görsel(ler) → PDF, MD → PDF (reportlab)
│   │   └── image_ops.py        # çözünürlük (DPI), piksel boyut, format, kalite
│   │
│   ├── ocr/
│   │   ├── __init__.py         # LAZY yükleme burada: get_engine() singleton
│   │   ├── engine.py           # RapidOCR wrapper — sayfa görseli → metin+koordinat
│   │   ├── table.py            # img2table + RapidOCR backend → DataFrame
│   │   └── fallback.py         # pytesseract (sistemde kuruluysa)
│   │
│   └── utils/
│       ├── logging.py          # dosyaya log (hata analizi için)
│       ├── tempfiles.py        # geçici dosya yönetimi + temizlik
│       ├── progress.py         # callback protokolü: (yüzde, mesaj)
│       └── timing.py           # her adımın süresini logla (hantallık ölçümü!)
│
├── ui/
│   ├── main_window.py          # Sol menü + sayfa yığını (QStackedWidget)
│   ├── theme.py                # Renk/font sabitleri (koyu tema)
│   ├── workers.py              # QRunnable sarmalayıcı — core çağrıları buradan
│   ├── pages/
│   │   ├── page_convert.py     # PDF → Word/Excel/MD (tek ekran, format seçimi)
│   │   ├── page_pdf_tools.py   # birleştir / böl / sıkıştır / döndür
│   │   ├── page_watermark.py
│   │   ├── page_signature.py   # imza foto yükle → önizle → sayfaya sürükle
│   │   ├── page_image.py       # görsel çözünürlük/boyut/format
│   │   └── page_notepad.py     # not defteri (otomatik kayıt)
│   └── widgets/
│       ├── dropzone.py         # sürükle-bırak (V1'deki bug'lar için testli)
│       ├── file_list.py        # çoklu dosya + sıralama
│       ├── pdf_preview.py      # PyMuPDF render → QPixmap sayfa önizleme
│       └── busy_overlay.py     # progress bar + iptal butonu
│
├── tests/
│   ├── samples/                # 10 REFERANS DOSYA (aşağıda liste)
│   └── test_convert.py, test_pdf_ops.py, test_ocr.py ...
│
└── build/
    ├── cevirgec2-win.spec      # PyInstaller spec (Windows)
    ├── cevirgec2-linux.spec    # PyInstaller spec (Linux)
    ├── installer.iss           # Inno Setup (opsiyonel)
    └── BUILD.md                # adım adım build talimatı
```

---

## 4. KRİTİK AKIŞLAR

### 4.1 Dönüştürme router'ı (kalbi bu)

```
Girdi dosyası
├── PDF ise → her sayfa için:
│     ├── metin katmanı ≥ 30 kelime → DİJİTAL HAT
│     │     Word: pdf2docx | Excel: pdfplumber | MD: pymupdf4llm
│     └── değilse (taranmış/eski PDF) → OCR HATTI
│           sayfa → 300 DPI görsel (PyMuPDF)
│           → RapidOCR (metin+koordinat)
│           → tablo şüphesi varsa img2table
│           → python-docx / openpyxl / md ile yeniden inşa
└── Görsel ise (jpg/png/tiff) → doğrudan OCR HATTI
```

Karışık PDF'lerde (bazı sayfa dijital, bazısı tarama) sayfa sayfa karar verilir — V1'in "ya hep ya hiç" yaklaşımı gider.

### 4.2 Islak imza

1. Kullanıcı imza fotoğrafını yükler (telefonla çekilmiş olabilir).
2. Pillow: gri tonlama → eşikleme → beyaz zemini şeffaf yap → kırp → PNG.
3. PDF önizlemede kullanıcı imzayı sürükleyip boyutlandırır.
4. PyMuPDF `insert_image` ile kalıcı gömme.

### 4.3 Filigran kaldırma (dürüst sınırlar)

- Annotation / OCG (katman) filigranı → PyMuPDF ile temiz kaldırılır.
- İçeriğe gömülü filigran → tespit + redaction denemesi; her zaman mümkün değil, UI'da açıkça belirtilir. "Her filigranı kaldırırız" vaadi verme.

### 4.4 Not defteri

Basit tut: sekmeli QPlainTextEdit, 5 saniyede bir otomatik kayıt (`~/.cevirgec2/notes/`), .txt/.md dışa aktarma. Özellik şişirme yok.

---

## 5. PERFORMANS HEDEFLERİ (kabul kriterleri)

| İşlem | Hedef |
|---|---|
| Uygulama açılışı | < 2 sn |
| Dijital PDF → Word (10 sayfa) | < 5 sn |
| Taranmış PDF → Word (10 sayfa, RapidOCR) | < 30 sn |
| PDF birleştirme (100 sayfa) | < 3 sn |
| RAM (normal kullanım) | < 400 MB |
| RAM (OCR aktif) | < 1 GB |

`utils/timing.py` her işi loglar — "hantal" hissi bir daha sayısız kalmaz.

---

## 6. TEST SETİ (samples/ klasörüne başta koy)

1. Modern dijital PDF (metin katmanlı)
2. Eski taranmış PDF (1990'lar, düşük kalite)
3. Çok kolonlu dijital PDF
4. Tablolu dijital PDF (çizgili + çizgisiz)
5. Taranmış tablolu PDF (fatura/beyanname tarzı)
6. Karışık PDF (dijital + taranmış sayfalar)
7. Telefonla çekilmiş belge fotoğrafı (jpg)
8. Türkçe karakter yoğun belge (ğüşiöç testi)
9. 100+ sayfalık büyük PDF
10. Şifreli/kısıtlı PDF (hata mesajı testi)

Kural: **Her sprint sonunda 10 dosyanın 10'u da denenir.** Agent "bitti" derse bu setle doğrulanmadan kabul yok.

---

## 7. BUILD STRATEJİSİ

**PyInstaller onedir** (onefile DEĞİL — her açılışta temp'e açma yok, 5-10x hızlı açılış):

```bash
# Windows
pyinstaller build/cevirgec2-win.spec
# → dist/cevirgec2/ klasörü → Inno Setup ile tek installer.exe

# Linux
pyinstaller build/cevirgec2-linux.spec
# → dist/cevirgec2/ → appimagetool ile Cevirgec2.AppImage
```

Spec dosyalarında kritik noktalar:
- `assets/models/*.onnx` → `datas` içine (OCR offline çalışsın)
- `assets/fonts/` → `datas` içine (PDF üretiminde TR karakter)
- `onnxruntime` binary'leri → `--collect-all onnxruntime`
- Tesseract PAKETLENMEZ — opsiyonel sistem bağımlılığı, Ayarlar'da "kuruluysa yolunu göster"
- UPX kapalı (antivirüs yanlış alarmı + açılış yavaşlaması)

---

## 8. SPRINT PLANI (Antigravity/Claude Code'a sırayla)

**Sprint 0 — İskelet (1 akşam):** Klasör yapısı, PySide6 ana pencere + sol menü + boş sayfalar, workers.py, timing/logging. Kabul: uygulama < 2 sn açılıyor, menüler geziliyor.

**Sprint 1 — Dijital hat (2 akşam):** router.py + pdf2docx/pdfplumber/pymupdf4llm dönüşümleri + pdf_ops (birleştir/böl/sıkıştır/döndür — V1'den taşı). Kabul: samples 1,3,4,9 sorunsuz.

**Sprint 2 — OCR hattı (2-3 akşam):** RapidOCR entegrasyonu (lazy), taranmış→Word/MD, img2table→Excel, görsel→PDF/Word. Kabul: samples 2,5,6,7,8 sorunsuz, süreler hedef içinde.

**Sprint 3 — Araçlar (2 akşam):** İmza, filigran, image_ops, not defteri, pdf_preview + sürükle-bırak. Kabul: imza akışı uçtan uca çalışıyor.

**Sprint 4 — Build + cila (2 akşam):** İki platform build, 10 dosyalık tam test, hata mesajları Türkçe, ikon/tema. Kabul: temiz bir Windows makinede installer'dan kurulup çalışıyor.

Toplam gerçekçi süre: ~9-10 akşam.

---

## 9. V1'DEN NE TAŞINIR, NE ÇÖPE GİDER

**Taşınır:** PyMuPDF birleştirme/bölme/sıkıştırma kodu, imza yerleştirme mantığı, Türkçe hata mesajları, samples birikimi.

**Çöpe:** GLM-OCR ve tüm torch/transformers kodu, win32com/Word bağımlılığı kalıntıları, CustomTkinter UI, docTR denemesi.

**Bilinçli kapsam dışı (v2.1'e):** pyHanko dijital e-imza (PFX), toplu işlem (batch), redaction aracı, LibreOffice ile Word/Excel→PDF (v2'de sadece görsel/MD→PDF var; Office→PDF LibreOffice headless gerektirir, paketleme yükü büyük — sonraya).

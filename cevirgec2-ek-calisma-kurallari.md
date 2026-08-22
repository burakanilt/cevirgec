---

# EK: İLK KURULUM + AGENT ÇALIŞMA KURALLARI

> Bu ek, ana planın **nasıl** uygulanacağını ve agentin **nerede yalan söyleyemeyeceğini** tanımlar. Ana plan "ne yapılacağını" anlatır; bu ek onu bağlar. Sprint 0'a başlamadan önce **A bölümü** eksiksiz tamamlanır.

---

## A. İLK KURULUM (Sprint 0'dan önceki sıfırıncı adım)

Aşağıdaki 6 adım, tek satır dönüştürme kodu yazılmadan önce bitirilir. Amaç: v2 faciasının iki kaynağını (paketleme sürprizi + yol/asset sorunu) en sona değil, en başa çekmek.

**A.1 — Ortam.** Python 3.12 ile temiz bir `venv` kurulur. Sistem Python'ına global kurulum YAPILMAZ.

**A.2 — İskelet.** Ana plandaki (Bölüm 3) klasör yapısı birebir oluşturulur. Boş `__init__.py`'ler ve modül dosyaları yerine konur. Bu noktada dosyalar boş/stub olabilir, ama yapı tam olmalı.

**A.3 — requirements kilitleme.** Aşağıdaki paketler kurulur, ardından **çalışan kombinasyon `==` ile sabitlenir** ve `BUILD.md`'ye yazılır. "En son sürüm" kullanılmaz — özellikle `onnxruntime` + `rapidocr_onnxruntime` + `pymupdf` üçlüsünün uyumu kırılgandır.

```
# Çalışma bağımlılıkları (sürümler kurulumdan SONRA kilitlenecek)
PySide6
pymupdf
pymupdf4llm
pdf2docx
pdfplumber
img2table
rapidocr_onnxruntime
pillow
python-docx
openpyxl
reportlab
```
```
# requirements-dev.txt
pyinstaller
pytest
```

**A.4 — Fitz duvarı (`core/pdf_backend.py`).** PyMuPDF'e dokunan TÜM işlemler bu tek modülden geçer. Daha ilk kurulumda bu modül oluşturulur ve şu arayüzü sunar (faz 2'de içi pypdfium2/pdfplumber ile değiştirilecek, dışı sabit kalacak):

```
core/pdf_backend.py — tek fitz kapısı
  open_document(path) -> Doc
  page_count(doc) -> int
  render_page(doc, page_no, dpi=300) -> PIL.Image     # OCR + preview bunu kullanır
  extract_words(doc, page_no) -> list[(text, x0,y0,x1,y1)]
  extract_text(doc, page_no) -> str                   # router'ın kelime sayımı
  merge / split / rotate / compress                   # pdf_ops buradan çağırır
  insert_image(doc, page_no, img, rect)               # imza yerleştirme
```

Kural (aşağıda R1): UI ve diğer `core/` modülleri `import fitz` YAPMAZ; hepsi `pdf_backend`'i çağırır.

**A.5 — Yol çözücü (`utils/resources.py`).** Dev ve frozen (PyInstaller) ortamda model/font/asset yolunu doğru çözen tek `resource_path()` fonksiyonu yazılır (`sys._MEIPASS` durumu ele alınır). Kodun hiçbir yerinde `assets/...` göreli yolu elle yazılmaz — her zaman bu çağrılır.

**A.6 — Erken build kanıtı.** Boş uygulamanın PyInstaller **onedir** build'i daha ilk akşam alınır ve **temiz bir klasörde** açılır. Sahte bir `dummy.onnx` dosyası `datas`'a konur ve frozen exe içinden `resource_path()` ile okunabildiği kanıtlanır. Bu adım geçmeden Sprint 0 kapanmaz. (Sebep: onnxruntime + model paketleme sorununu Sprint 4'te değil, en başta yakala.)

---

## B. AGENT ÇALIŞMA KURALLARI (tüm sprintler boyunca geçerli)

**R1 — Fitz duvarı korunur.** PyMuPDF (fitz) yalnızca `core/pdf_backend.py` içinde import edilir. Başka hiçbir dosya fitz'i doğrudan çağırmaz. İhlal, o görevi otomatik "açık" sayar.

**R2 — "Bitti" kanıt ister.** Bir görev, agent "tamam" dediğinde değil, şu üç kanıt sunulduğunda biter:
(a) çalıştırılan komut + çıktısı,
(b) üretilen dosyanın kendisi (docx/xlsx/pdf açılıp gösterilir),
(c) `utils/timing.py` log'undan gerçek süre.
Kanıt yoksa görev açıktır. Ekran görüntüsü/log olmadan "çalışıyor" kabul edilmez.

**R3 — Kapsam kilidi.** Bu planda yazmayan hiçbir özellik eklenmez. Agent bir eksik veya "iyileştirme" görürse onu YAPMAZ — önce sorar. Faz 1'in tek hedefi: v1'in yaptığı işlevler + taranmış PDF çözümü, hızlı ve çalışır halde. Her türlü iyileştirme faz 2'ye saklıdır.

**R4 — Sprint sonu tam doğrulama.** Her sprintin sonunda, o sprintin kabul kriterindeki dosyalar gerçekten dönüştürülür ve çıktılar gösterilir. Bu yapılmadan bir sonraki sprinte geçilmez. ("10 dosyanın 10'u" kuralı sona bırakılamaz, sprint sprint uygulanır.)

**R5 — Erken gate'ler ertelenmez.**
- *Build gate:* A.6 (paketleme kanıtı) Sprint 0'da alınır.
- *Türkçe OCR gate:* Sprint 2'nin İLK işi, RapidOCR'ı **sample 8** (ğüşıöçİ yoğun belge) üzerinde test etmektir. Türkçe karakter tanıma zayıfsa, tüm OCR hattı kurulmadan önce raporlanır — dil/model ayarı gerekebilir.

**R6 — Sürümler sabit kalır.** `requirements.txt`'teki tüm sürümler `==` ile kilitlidir (A.3). Agent kendi kararıyla paket yükseltmez/değiştirmez; gerekiyorsa gerekçesiyle sorar. Çalışan kombinasyon `BUILD.md`'de kayıtlıdır.

**R7 — Router disiplini.** Metin katmanı olan sayfa OCR'a asla girmez (ana plan Kural 5). Karışık PDF'lerde karar sayfa sayfadır. Agent "kolay olsun diye" tüm PDF'i tek hatta zorlamaz.

---

## C. FAZ 2 NOTU (şimdi yapılmaz, sadece kayıt)

Faz 1 çalışır ve 10/10 test geçtikten sonra açılacak "geliştirme-iyileştirme" fazının başlangıç noktası: `core/pdf_backend.py`'nin içini PyMuPDF'ten pypdfium2 (render) + pypdf (birleştir/böl) + pikepdf (sıkıştır) + pdfplumber (metin/koordinat) ile değiştirmek; ardından pdf2docx'in (MIT) layout algoritmasını bu permissive tabana taşıyarak kendi Word assembler'ımızı yazmak. Fitz duvarı (R1) bu geçişi "tek dosya değişikliği" haline getirmek için vardır. **Faz 1 sırasında bu maddeye dokunulmaz.**

# Çevirgeç PDF v2.0 📑🚀

[🇹🇷 Türkçe](#türkçe) | [🇬🇧 English](#english)

---

<a name="türkçe"></a>
## 🇹🇷 Türkçe

**Çevirgeç PDF v2.0**, tamamen yerel (offline) çalışan, hızlı, modern ve gizlilik odaklı bir masaüstü PDF dönüştürme ve belge yönetim aracıdır. PySide6 (Qt6) ile geliştirilmiş modern arayüzü, PyMuPDF altyapısı ve hafif ONNX modelleriyle güçlendirilmiş çevrimdışı OCR yetenekleriyle tüm belge işlemlerinizi internete ihtiyaç duymadan, saniyeler içinde gerçekleştirir.

---

### 🌟 Öne Çıkan Özellikler

#### 📝 1. Not Defteri ve Canlı Markdown (.md) Görüntüleyici / Editör
* **Bölünmüş Ekran (Split-View)**: Sol panelde hızlıca Markdown notları yazıp düzenlerken, sağ panelde anlık olarak zengin biçimlendirilmiş HTML önizlemesini izleyin.
* **.md Dosya Görüntüleme & Düzenleme**: Mevcut Markdown (`.md`) veya düz metin (`.txt`) belgelerinizi açıp inceleyin, düzenleyin ve kaydedin.
* **Anında PDF Dışa Aktarma**: Yazdığınız veya görüntülediğiniz Markdown içeriklerini tek tıkla doğrudan profesyonelce biçimlendirilmiş PDF formatına dönüştürün.
* **Gelişmiş Yazı Tipi & Sözdizimi Desteği**: Başlıklar, listeler, kod blokları, tablolar, alıntılar ve Türkçe karakterleri kusursuz şekilde görselleştirin.
* **Otomatik Kayıt ve Oturum Belleği**: Notlarınızı kaybetmemeniz için son oturum durumunu hatırlar.

#### 🔄 2. Kapsamlı Belge Dönüştürücü (Import & Export)
* **PDF'ten Dönüştürme**:
  * **Word (.docx)**: Sayfa düzeni ve metin yapısı korunarak hızlı dönüştürme.
  * **Excel (.xlsx)**: Tablo tespiti ve çoklu sayfa desteğiyle elektronik tabloya dönüştürme.
  * **Markdown (.md)**: LLM (Yapay Zeka) modellerine uygun, temiz ve hiyerarşik Markdown formatına aktarım.
  * **Düz Metin (.txt)**: Hızlı metin katmanı çıkarımı.
* **PDF'e Dönüştürme**:
  * **Word (.docx, .doc)** $\rightarrow$ **PDF** (Microsoft Office COM veya yerel dönüştürücü ile).
  * **Excel (.xlsx, .xls)** $\rightarrow$ **PDF**.
  * **Markdown (.md)** ve **Metin (.txt)** $\rightarrow$ **PDF**.
  * **Görseller (.png, .jpg, .jpeg, .bmp, .webp, .tiff, .tif)** $\rightarrow$ **PDF**.

#### 🔍 3. Hızlı ve Çevrimdışı Türkçe / Latin OCR Motoru
* **İnternetsiz & Gizlilik Odaklı**: Belgeleriniz hiçbir sunucuya yüklenmez, tüm işlemler bilgisayarınızda ONNX Runtime üzerinde çalışır.
* **PP-OCRv5 & v3 Modelleri**: Türkçe karakterler (`ğ, ü, ş, ı, ö, ç, İ`) dahil yüksek doğruluklu metin ve taranmış belge tanıma.
* **Akıllı Sayfa Yönlendirici (Smart Router)**: Sayfa metin katmanına sahipse OCR'a girmeden anında dijitalleştirir; yalnızca taranmış/görsel sayfaları OCR işlemine alır.

#### 🏛️ 4. Resmi Belge & ETDS / EYP Araçları
* **Elektronik Belge Paketi (EYP/ETDS)**: Resmi kurumların elektronik yazışma paketlerini açma, üstveri (metadata) ve eklerini ayrıştırma ve görselleştirme.
* **Gelişmiş Önizleme**: Resmi ek belgeleri uygulama içinden doğrudan inceleme.

#### 🛠️ 5. PDF Araç Kutusu (PDF Toolbox)
* **Birleştirme (Merge)**: Çok sayıda PDF'i tek dosyada hızla birleştirme.
* **Sayfa Ayırma / Bölme (Split)**: Sayfa aralığına göre veya her sayfayı ayrı PDF olarak dışa aktarma.
* **Sayfa Silme (Delete Pages)**: İstenmeyen sayfaları tek işlemle çıkarma.
* **Sayfa Döndürme (Rotate)**: Sayfaları 90°, 180°, 270° döndürme.
* **Sıkıştırma (Compress)**: DPI ve görsel kalitesi optimize edilerek dosya boyutunu küçültme.
* **Sayfa / Bates Numaralandırma**: Belgelere alt/üst bilgi olarak sayfa numarası veya arşiv kodu ekleme.
* **Sayfa Önizleme**: Yüksek çözünürlüklü sayfa gezgini.

#### 🔒 6. Güvenlik, İmza ve Filigran
* **AES-256 Şifreleme**: PDF'lere güçlü kullanıcı şifresi ekleme.
* **Şifre Kaldırma**: Şifresi bilinen korumalı PDF'leri şifresiz hale getirme.
* **Islak İmza Yerleştirme**: İmza fotoğraflarındaki beyaz arka planı otomatik temizleyip (şeffaflaştırıp) PDF'in istenen sayfasına ve koordinatına konumlandırma.
* **Filigran (Watermark)**: Şeffaflık, açı ve konum ayarlarıyla metin veya logo/resim filigranı ekleme.

#### 🖼️ 7. Gelişmiş Görsel İşleme
* **Format Dönüştürme**: PNG, JPEG ve PDF arasında dönüştürme.
* **Akıllı Belge İyileştirme**: Belge fotoğraflarındaki gölgeleri temizleme, Otsu binarizasyon ile taranmış evrak netliği sağlama, DPI ayarlama ve orantılı doldurma.

---

### 💻 Kurulum ve Çalıştırma

#### Gereksinimler
* Python 3.10+ (Python 3.12 önerilir)
* Windows veya Linux

#### Adımlar
1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/burakanilt/cevirgec2.git
   cd cevirgec2
   ```

2. Sanal ortam oluşturup aktif edin:
   ```bash
   python -m venv .venv
   # Windows için:
   .venv\Scripts\activate
   # Linux/macOS için:
   source .venv/bin/activate
   ```

3. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. Uygulamayı başlatın:
   ```bash
   python app.py
   ```

5. Testleri çalıştırmak için:
   ```bash
   pytest
   ```

---

<a name="english"></a>
## 🇬🇧 English

**Çevirgeç PDF v2.0** is a fast, offline-first, modern, and privacy-focused desktop PDF converter and document management utility. Built with PySide6 (Qt6), PyMuPDF engine, and lightweight ONNX runtime models, it performs all document conversion, OCR, and editing tasks locally in seconds without requiring an internet connection.

---

### 🌟 Key Features

#### 📝 1. Notepad & Live Markdown (.md) Viewer / Editor
* **Live Split-View**: Write and edit Markdown notes on the left panel while instantly seeing the rendered HTML output on the right.
* **.md File Viewer & Editor**: Open, view, edit, and save your existing Markdown (`.md`) or plain text (`.txt`) files effortlessly.
* **Instant PDF Export**: Convert your notes or Markdown documentation into professionally styled PDF files with a single click.
* **Rich Typography & Formatting Support**: Full rendering for headings, lists, tables, code blocks, blockquotes, and special Unicode characters.
* **Auto-Save & Session Restore**: Retains your current editor session so you never lose your notes.

#### 🔄 2. Comprehensive Document Conversion (Import & Export)
* **From PDF**:
  * **To Word (.docx)**: Preserves layouts, paragraph flow, and styling.
  * **To Excel (.xlsx)**: Intelligent table detection and extraction.
  * **To Markdown (.md)**: Clean, structured Markdown optimized for LLMs and note-taking.
  * **To Plain Text (.txt)**: Rapid text extraction.
* **To PDF**:
  * **Word (.docx, .doc)** $\rightarrow$ **PDF** (via Microsoft Office COM or native engines).
  * **Excel (.xlsx, .xls)** $\rightarrow$ **PDF**.
  * **Markdown (.md)** & **Plain Text (.txt)** $\rightarrow$ **PDF**.
  * **Images (.png, .jpg, .jpeg, .bmp, .webp, .tiff, .tif)** $\rightarrow$ **PDF**.

#### 🔍 3. Fast & Offline Turkish / Latin OCR Engine
* **100% Privacy & Offline Execution**: No documents are sent to any remote servers. Powered by ONNX Runtime.
* **PP-OCRv5 & v3 Models**: High-accuracy recognition for Turkish special characters and multilingual text.
* **Smart Pipeline Router**: Digital pages with text layers bypass OCR instantly, whereas scanned pages are automatically routed through the OCR pipeline.

#### 🏛️ 4. Official Document & EYP / ETDS Tools
* **Electronic Correspondence Packages (EYP)**: Extract metadata, enclosures, attachments, and main documents from official Turkish government packages.
* **Built-in Document Inspector**: Preview and extract internal attachments directly.

#### 🛠️ 5. PDF Toolbox
* **Merge**: Combine multiple PDF documents in seconds.
* **Split**: Extract specific page ranges or burst all pages into individual files.
* **Delete Pages**: Remove unwanted pages effortlessly.
* **Rotate**: Rotate orientation (90°, 180°, 270°).
* **Compress**: Optimize file size with configurable DPI and image compression.
* **Bates & Page Numbering**: Add customized headers, footers, and page numbers.
* **High-Res Preview**: Visual page browser with zoom and navigation.

#### 🔒 6. Security, Signature & Watermarking
* **AES-256 Encryption**: Protect your PDF documents with passwords.
* **Password Removal**: Decrypt password-protected PDFs.
* **Signature Placement**: Automatically clean and make transparent handwritten signatures and stamp them onto any coordinate of a PDF page.
* **Watermark**: Stamp text or logo watermarks with opacity and angle controls.

#### 🖼️ 7. Advanced Image Processing
* **Format Conversion**: Convert between PNG, JPEG, and PDF.
* **Document Scanner Enhancements**: Shadow removal, Otsu thresholding, binarization, DPI adjustment, and aspect-ratio padding.

---

### 💻 Installation & Usage

#### Prerequisites
* Python 3.10+ (Python 3.12 recommended)
* Windows or Linux

#### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/burakanilt/cevirgec2.git
   cd cevirgec2
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Linux/macOS:
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Run unit tests:
   ```bash
   pytest
   ```

---

### 📜 License & Third-Party Credits
* **License**: GNU Affero General Public License v3.0 ([AGPL-3.0](LICENSE.txt))
* Third-party libraries and licenses are detailed in [CREDITS.txt](CREDITS.txt).

# 🐷 DompetVibe.ai — Sahabat Cerdas Pengatur Keuangan & Gaya Belanjamu ✨

> Platform *Behavioral Finance* cerdas yang membaca mutasi rekening bank dan e-wallet secara otomatis, mendeteksi bocor halus, mengelompokkan pos pengeluaran bulanan, dan memberikan simulasi penghematan nyata dengan bahasa yang santai, ramah, dan mudah dipahami.

---

## 🌟 Fitur Unggulan Platform

1. **📄 Ekstraksi Berkas Asli Multi-Bank Tanpa OCR:**
   Mendukung pembacaan berkas mutasi digital (`.pdf`, `.xlsx`, `.csv`) dari **m-BCA, KlikBCA, Bank Mandiri (Livin'), BRI (BRImo), BNI, Permata ME, GoPay, ShopeePay, OVO, dan DANA** dengan akurasi 100% tanpa risiko salah baca karakter OCR.

2. **📊 Analisis Multi-Bulan & Tren Arus Kas:**
   Dapat mengunggah beberapa berkas mutasi sekaligus. Sistem secara otomatis memilah data per bulan, melacak stabilitas arus kas, dan menyajikan narasi tren rata-rata pengeluaran bulanan.

3. **🏷️ Pemetaan Kategori Cerdas:**
   Mengelompokkan transaksi ke pos *Kebutuhan Pokok (Needs)*, *Belanja Keinginan (Wants)*, *Cicilan Pinjaman (Paylater/Kredit)*, *Biaya Administrasi Bank*, dan *Kuliner*.

4. **🛡️ Diagnosis Tingkat Kendali Belanja:**
   Mengukur seberapa kuat rem pengeluaranmu ke dalam 4 tingkatan: **Aman**, **Waspada**, **Impulsif**, atau **Kritis**.

5. **💡 4 Spending Personas (Karakter Finansial):**
   * 🌱 **Si Mindful Planner:** Disiplin tinggi, minim jajan, arus kas selalu surplus.
   * ☕ **Anak Kopi & Kafe:** Dominan nongkrong dan kulineran kekinian, waspada bocor halus.
   * ⚡ **Pemburu Promo:** Sensitif voucher cashback dan tanggal kembar (FOMO).
   * 💳 **Sahabat Paylater:** Pengguna cicilan digital dan belanja larut malam yang rawan defisit.

6. **🎯 Simulasi Cerdas & Rencana Penghematan Nyata (What-If):**
   * AI otomatis merekomendasikan pos terboros yang paling fleksibel untuk dipangkas.
   * Pilihan pos sasaran penghematan interaktif (*clickable chips*).
   * Preset pemangkasan 1-klik (10% Santai, 20% Rekomendasi, 35% Agresif, 50% Maksimal).
   * Menampilkan proyeksi arus kas baru dan ekuivalen nyata (*Dana Darurat*, *Emas Batangan*, *Cangkir Kopi / Belanja Online*).

7. **🔒 Jaminan Privasi 100% Aman:**
   Tidak pernah meminta PIN, password, nomor kartu ATM, atau CVV. Semua berkas diolah secara aman dan privat.

---

## 🎓 Panduan Cepat untuk Dosen / Penguji / Pengguna Baru

> **💡 Catatan Penting:** Proyek ini **100% Pure Python** dan **TIDAK memerlukan instalasi Tesseract OCR eksternal**. Sistem menggunakan parser digital vektor cerdas (`pdfplumber`) langsung dari struktur internal dokumen perbankan, sehingga siap dijalankan di sistem operasi mana pun tanpa instalasi software tambahan atau pengaturan PATH!

### Opsi 1: Jalankan Otomatis 1-Klik (Rekomendasi untuk Windows)
Cukup **klik ganda (double-click)** pada berkas:
👉 **`jalankan.bat`**

Skrip ini akan secara otomatis:
1. Memeriksa ketersediaan Python di komputer.
2. Memasang seluruh dependensi dari `requirements.txt`.
3. Menjalankan server aplikasi dan otomatis membuka halaman web di browser (`http://127.0.0.1:5000`).

---

### Opsi 2: Jalankan via Terminal / Command Prompt
Jika mengkloning dari GitHub atau menjalankan melalui terminal:
```powershell
# 1. Masuk ke folder proyek
cd websiteAIFinance

# 2. Pasang semua dependensi
pip install -r requirements.txt

# 3. Jalankan aplikasi
python app.py
```
Akses di browser: **`http://127.0.0.1:5000`**

---

## 🚀 Cara Menjalankan Kembali di PC Ini (Besok / Lain Waktu)

Jika kamu ingin menjalankan aplikasi ini lagi di PC yang sama, langkahnya sangat mudah:

1. **Buka Terminal / Command Prompt:**
   Buka **PowerShell**, **Command Prompt (CMD)**, atau terminal di **VS Code**.

2. **Masuk ke Folder Proyek:**
   ```powershell
   cd c:\Users\KazuhikoAji\OneDrive\Dokumen\websiteAIFinance
   ```

3. **Jalankan Aplikasi:**
   ```powershell
   python app.py
   ```

4. **Buka di Browser:**
   Buka browser (Chrome, Edge, Firefox, dll.) lalu akses alamat:
   👉 **`http://127.0.0.1:5000`**

5. **Untuk Menghentikan Server:**
   Tekan **`Ctrl + C`** pada jendela terminal.

---

## 💻 Panduan Instalasi di PC / Laptop Lain (Dari Awal)

Jika kamu ingin memindahkan atau menginstal aplikasi ini di laptop/PC lain, ikuti langkah-langkah berikut:

### 1. Prasyarat Sistem
* **Python 3.10 atau versi lebih baru** (disarankan Python 3.10, 3.11, atau 3.12).
  * Unduh dari [python.org](https://www.python.org/downloads/).
  * ⚠️ **PENTING saat instalasi Python di Windows:** Pastikan mencentang kotak **"Add python.exe to PATH"**.

---

### 2. Salin Folder Proyek
Salin seluruh folder `websiteAIFinance` ke PC baru (bisa menggunakan Flashdisk, Google Drive, OneDrive, atau Git).

---

### 3. Buka Terminal di PC Baru
Buka **PowerShell** atau **Command Prompt**, lalu arahkan ke lokasi folder proyek:
```powershell
cd C:\path\ke\folder\websiteAIFinance
```
*(Ganti `C:\path\ke\folder` dengan lokasi folder tempat kamu menyimpan proyek).*

---

### 4. Buat Virtual Environment (Sangat Disarankan)
Membuat lingkungan virtual agar library Python terisolasi rapi dan tidak bentrok dengan aplikasi lain:

* **Buat Virtual Environment:**
  ```powershell
  python -m venv venv
  ```

* **Aktifkan Virtual Environment:**
  * **Windows (PowerShell):**
    ```powershell
    .\venv\Scripts\Activate.ps1
    ```
    *(Jika muncul error script restriction di PowerShell, jalankan sekali: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` lalu aktifkan lagi).*
  * **Windows (CMD):**
    ```cmd
    venv\Scripts\activate.bat
    ```
  * **macOS / Linux:**
    ```bash
    source venv/bin/activate
    ```

---

### 5. Install Seluruh Dependensi (Requirements)
Jalankan perintah berikut untuk mengunduh semua library yang dibutuhkan otomatis:
```powershell
pip install -r requirements.txt
```

Library utama yang akan terpasang:
* `Flask` & `Flask-CORS` (Backend Web Server)
* `pandas`, `numpy`, `openpyxl` (Pengolahan Tabel Data & Excel)
* `pdfplumber` (Ekstraksi Berkas PDF m-Banking)
* `scikit-learn` & `xgboost` (Model Machine Learning)
* `shap` (Transparansi Model Explainable AI)
* `joblib` (Penyimpanan Model Serialisasi)

---

### 6. Jalankan Server Flask
Setelah instalasi selesai, jalankan:
```powershell
python app.py
```

Jika berhasil, akan muncul pesan:
```text
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

Buka browser dan buka:
👉 **`http://127.0.0.1:5000`**

---

## 📁 Struktur Direktori Proyek

```text
websiteAIFinance/
├── app.py                      # Server backend Flask & routing API
├── requirements.txt            # Daftar library Python yang dibutuhkan
├── README.md                   # Dokumentasi panduan instalasi & penggunaan
├── templates/
│   └── index.html              # Antarmuka web utama (Tailwind pastel & komponen interaktif)
├── static/
│   ├── css/
│   │   └── custom.css          # Styling pastel, animasi hover, gradasi, & floating icon
│   └── js/
│       └── app.js              # Logika frontend (Upload, Navigasi 5 Menu, Filter Bulan, Simulator)
├── ml/
│   ├── feature_mapper.py       # Ekstraksi transaksi bank & e-wallet multi-format
│   ├── prepare_and_train.py    # Skrip pelatihan model ML
│   └── generate_samples.py     # Generator data uji sintetis & sampel mutasi
├── models/
│   ├── xgboost_model.pkl       # Model XGBoost (Prediksi Kendali Belanja)
│   ├── kmeans_model.pkl        # Model K-Means (4 Spending Personas)
│   ├── rf_model.pkl            # Model Random Forest pembanding
│   ├── scaler.pkl              # Normalizer fitur input
│   └── evaluation_metrics.json # Data metrik performa model
├── sample_demo/                # Berkas mutasi contoh siap pakai (.pdf, .csv, .xlsx)
└── uploads/                    # Folder penampung sementara berkas yang diunggah
```

---

## ❓ Tanya Jawab & Solusi Kendala (Troubleshooting)

1. **Port 5000 Sudah Terpakai (`Address already in use`):**
   Jika port 5000 sedang digunakan proses lain di PC:
   * Buka file `app.py`.
   * Pada baris paling bawah, ubah baris `app.run(debug=True, port=5000)` menjadi port lain, misalnya `port=5050`.
   * Akses web melalui `http://127.0.0.1:5050`.

2. **Browser Menampilkan Tampilan Lama (Cache):**
   Jika setelah update tampilan terasa belum berubah, tekan **`Ctrl + F5`** (atau `Ctrl + Shift + R`) di browser untuk melakukan hard refresh cache.

3. **Format Berkas Mutasi yang Didukung:**
   * **PDF Asli:** e-Statement resmi dari m-BCA, Permata ME, Livin' Mandiri, BRImo, BNI.
   * **Excel / CSV:** Format ekspor transaksi e-Statement bank atau e-wallet (GoPay, ShopeePay, OVO).

---

<p align="center">
  Dibuat dengan ❤️ untuk Membantu Pengelolaan Finansial yang Lebih Sehat &amp; Menyenangkan.<br>
  <strong>DompetVibe.ai • 2026</strong>
</p>

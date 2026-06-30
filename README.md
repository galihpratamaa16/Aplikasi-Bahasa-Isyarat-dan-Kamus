# Sign Language Letter Detector

Program Python sederhana untuk membantu pembelajaran pengenalan huruf bahasa isyarat.

## Fitur
- Tangkap data landmark tangan dari webcam
- Latih model klasifikasi huruf dari data landmark
- Jalankan deteksi huruf secara real-time

## Setup
1. Buat virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instal dependensi:

```powershell
pip install -r requirements.txt
```

## Langkah penggunaan

### Opsi 1: GUI Desktop (tkinter)
1. Jalankan `main_menu.py`:

```powershell
python main_menu.py
```

2. Dari halaman utama, pilih:
   - **Mulai Belajar** — deteksi huruf secara real-time
   - **Kumpulkan Data** — kumpulkan dataset baru

### Opsi 2: Web Application (Flask)
1. Jalankan `web_app.py`:

```powershell
python web_app.py
```

2. Buka browser dan akses: `http://127.0.0.1:5000`

3. Dari halaman utama website, pilih:
   - **Mulai Belajar** — lihat deteksi huruf melalui streaming video
   - **Kumpulkan Data** — petunjuk untuk mengumpulkan data dari terminal

### Opsi 3: Command Line
- Kumpulkan data: `python capture_dataset.py`
- Latih model: `python train_model.py`
- Deteksi huruf real-time: `python app.py`

## Catatan
- Program ini menggunakan MediaPipe Tasks API untuk mendeteksi landmark tangan.
- Model MediaPipe akan diunduh otomatis ke folder `models/` saat pertama kali dijalankan.
- Dataset awal perlu dikumpulkan sendiri dengan berbagai posisi tangan untuk setiap huruf.
- Program ini cocok sebagai dasar dan dapat dikembangkan ke huruf Bahasa Isyarat Indonesia (BISINDO) atau American Sign Language (ASL).

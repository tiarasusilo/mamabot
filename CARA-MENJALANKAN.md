# Cara Menjalankan MamaBot

Panduan untuk pemula. Ikuti dari atas ke bawah; setiap perintah bisa disalin langsung.

## 1. Persiapan (sekali saja)

1. Pasang **Python 3.10 atau lebih baru** dari https://www.python.org/downloads/
   (Windows: centang **Add python.exe to PATH**).
2. Periksa di terminal: `python --version` (macOS/Linux: `python3 --version`).
3. Ekstrak proyek, lalu buka terminal di folder `mamabot-flask`.
   Di VS Code: **File › Open Folder…**, lalu buka terminal dengan **Ctrl + `**.
4. Buat dan aktifkan virtual environment:

```bash
python -m venv venv
```

| Sistem | Perintah aktivasi |
| --- | --- |
| Windows (Command Prompt) | `venv\Scripts\activate` |
| Windows (PowerShell) | `venv\Scripts\Activate.ps1` |
| macOS / Linux | `source venv/bin/activate` |

Awal baris terminal akan berubah menjadi `(venv)`. Aktifkan ulang setiap membuka terminal baru.

5. Pasang pustaka:

```bash
pip install -r requirements.txt
```

## 2. Menjalankan aplikasi web

```bash
python app.py
```

| Alamat | Isi |
| --- | --- |
| http://127.0.0.1:5000/ | Beranda MamaBot |
| http://127.0.0.1:5000/chat | Halaman chat |
| http://127.0.0.1:5000/chat?q=MPASI | Chat dengan saran pertanyaan topik MPASI |
| http://127.0.0.1:5000/admin | Statistik dan pertanyaan yang tidak dikenali |

Yang bisa dicoba:

- Klik tombol saran, atau ketik pertanyaan sendiri. Balasan muncul **tanpa memuat ulang halaman**.
- Muat ulang halaman (F5): riwayat tetap ada karena disimpan di `chat_history.db`.
- Klik **Hapus riwayat** untuk mengosongkan percakapan sesi Anda.
- Buka `/admin` untuk melihat pertanyaan yang belum dipahami bot, lalu tambahkan polanya ke `themes/mamabot.json`.

File `chat_history.db` dibuat otomatis. Hapus file ini bila ingin memulai dari nol.

## 3. Chat di terminal (tanpa browser)

```bash
python cli.py                  # chat biasa
python cli.py --debug          # tampilkan 3 kandidat intent dan skornya
python cli.py --ambang 0.6     # coba ambang batas lain
```

Ketik `keluar` untuk berhenti.

## 4. Menjalankan uji otomatis

```bash
pytest -v
```

Hasil yang diharapkan pada baris terakhir: **`45 passed`**. Uji memakai database sementara,
sehingga tidak mengubah `chat_history.db`.

## 5. Mengukur akurasi

`evaluate.py` menguji bot dengan kalimat di `evaluasi/mamabot.csv` yang **tidak** ada di file tema.

```bash
python evaluate.py             # akurasi, hasil per intent, daftar kesalahan
python evaluate.py --sweep     # bandingkan beberapa ambang batas
```

Hasil saat proyek ini dibuat: **70 kalimat uji, akurasi 92,9%** pada ambang 0,45.
Kesalahan yang tersisa sengaja dibiarkan karena memakai kata yang tidak ada di pola
(misalnya "gizi seimbang untuk bumil" atau "ciri-ciri mau melahirkan"). Ini batas pendekatan berbasis aturan.
Untuk memperbaikinya, tambahkan pola atau kata baku di `NORMALISASI` pada `chatbot/engine.py`.

Kolom `intent` di CSV diisi `fallback` untuk pertanyaan di luar tema (bot seharusnya menolak).

## 6. Pengaturan lewat variabel lingkungan

| Variabel | Bawaan | Fungsi |
| --- | --- | --- |
| `SECRET_KEY` | `ganti-dengan-kunci-rahasia` | Menandatangani cookie sesi. **Wajib diganti** di server sungguhan. |
| `THRESHOLD` | `0.45` | Ambang batas skor |
| `DATABASE` | `chat_history.db` | Lokasi file SQLite |
| `ADMIN_KEY` | (kosong) | Bila diisi, `/admin` hanya terbuka dengan `?key=<nilai>` |

```bash
# Linux / macOS
export ADMIN_KEY=rahasia123 THRESHOLD=0.4
python app.py
```

```powershell
# Windows PowerShell
$env:ADMIN_KEY="rahasia123"; $env:THRESHOLD="0.4"
python app.py
```

Lalu buka http://127.0.0.1:5000/admin?key=rahasia123

## 7. Masalah yang sering terjadi

| Gejala | Penyebab | Solusi |
| --- | --- | --- |
| `'python' is not recognized` | Python belum masuk PATH | Pasang ulang dan centang *Add python.exe to PATH*, atau pakai `py` |
| `ModuleNotFoundError: No module named 'flask'` | venv belum aktif | Aktifkan venv, lalu `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'chatbot'` | Dijalankan dari folder yang salah | `cd mamabot-flask` dulu |
| `Address already in use` | Port 5000 dipakai (di macOS bisa AirPlay Receiver) | Hentikan server lama, atau `flask --app app run --port 5001` |
| `File tema mamabot.json tidak valid` | Struktur JSON salah | Baca daftar masalah di pesan galat, perbaiki JSON |
| `json.decoder.JSONDecodeError` | Koma berlebih atau tanda kutip salah | `python -m json.tool themes/mamabot.json` |
| Tampilan tidak berubah setelah CSS/JS diedit | Cache browser | Tekan Ctrl + Shift + R |
| Foto latar beranda tidak muncul | Link foto mati atau diblokir | Ganti link di `templates/index.html`, atau pakai foto di `static/img/` |
| Bot sering menjawab "belum punya informasi" | Pola kurang bervariasi | Lihat `/admin`, tambahkan pola ke JSON |

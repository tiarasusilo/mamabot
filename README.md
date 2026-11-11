# MamaBot — Sahabat Bunda dan Si Kecil

Chatbot edukasi kesehatan ibu dan anak berbasis aturan (*rule-based*), dibuat dengan **Python + Flask**.
Topiknya: kehamilan, persalinan, menyusui, MPASI, dan perawatan bayi.
Strukturnya mengikuti `aplikasi-final` pada paket praktikum, tetapi dibuat untuk **satu bot** (MamaBot),
bukan tiga tema.

> Informasi MamaBot bersifat edukatif dan **bukan pengganti konsultasi tenaga kesehatan**.

## Mulai cepat

```bash
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # Linux / macOS
pip install -r requirements.txt
python app.py
```

Buka **http://127.0.0.1:5000**. Panduan lengkap ada di [CARA-MENJALANKAN.md](CARA-MENJALANKAN.md).

## Isi proyek

```
mamabot-flask/
├── app.py                  route halaman + REST API + halaman admin
├── cli.py                  chat di terminal  (python cli.py --debug)
├── evaluate.py             ukur akurasi dengan data uji
├── requirements.txt        Flask + pytest
├── pytest.ini
├── chatbot/
│   ├── engine.py           praproses teks, skor kemiripan, validasi tema
│   └── database.py         riwayat & statistik (SQLite)
├── themes/
│   └── mamabot.json        SEMUA isi bot: intent, pola, respons, fallback
├── evaluasi/
│   └── mamabot.csv         70 kalimat uji (di luar pola di JSON)
├── templates/
│   ├── index.html          beranda (hero + menu topik)
│   ├── chat.html           halaman chat
│   ├── admin.html          statistik & pertanyaan yang tidak dikenali
│   └── 404.html            halaman galat (404 / 403)
├── static/
│   ├── css/home.css        gaya beranda
│   ├── css/style.css       gaya chat, admin, dan galat
│   ├── js/chat.js          kirim pesan dengan fetch(), tanpa reload
│   └── img/mamabot-icon.svg
└── tests/                  45 uji pytest
```

## Cara kerja singkat

1. Pesan Bunda diproses: huruf kecil → tanda baca dibuang → kata tidak baku dinormalisasi
   (`gimana` → `bagaimana`, `bumil` → `ibu hamil`) → kata henti dibuang (`Bun`, `Bunda`, `ya`, ...).
2. Setiap pola di `themes/mamabot.json` diberi skor kemiripan (Jaccard + kemiripan karakter + cakupan).
3. Intent dengan skor tertinggi dipilih bila skornya ≥ **0,45**; jika tidak, bot memberi jawaban *fallback*.

## Endpoint

| Metode | URL | Keterangan |
| --- | --- | --- |
| GET | `/` | Beranda |
| GET | `/chat` | Halaman chat. `?q=Kehamilan` (atau Persalinan, Menyusui, MPASI, Perawatan Bayi) menampilkan saran pertanyaan topik itu |
| GET | `/admin` | Statistik & pertanyaan yang tidak dikenali |
| POST | `/api/chat` | `{"message": "..."}` → `{"reply", "intent", "score"}` |
| POST | `/api/explain` | Tiga kandidat intent teratas beserta skornya |
| GET | `/api/history` | Riwayat chat sesi ini |
| DELETE | `/api/history` | Hapus riwayat sesi ini |
| GET | `/api/stats` | Jumlah pertanyaan per intent |

## Mengubah isi bot

Cukup edit `themes/mamabot.json`, lalu jalankan ulang `python app.py`.
Aplikasi memeriksa file itu saat start dan berhenti dengan pesan jelas bila ada yang salah
(misalnya pola yang sama dipakai dua intent). Periksa JSON tanpa menjalankan aplikasi:

```bash
python -m json.tool themes/mamabot.json
```

## Catatan

- **Foto latar beranda** diatur di `templates/index.html` (variabel `--bg-image` pada `<section class="hero">`).
  Jika foto gagal dimuat, beranda memakai gradien mawar sebagai cadangan.
- Isi jawaban bersifat umum. Sebelum dipakai sungguhan, pastikan setiap jawaban sesuai
  pedoman terbaru (Buku KIA / Kemenkes / IDAI) dan ditinjau tenaga kesehatan.

"""Uji integrasi route Flask menggunakan test client."""
import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    # Database sementara agar pengujian tidak mengotori data asli
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()


def test_halaman_beranda(client):
    res = client.get("/")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "MamaBot" in html
    assert "/chat" in html                     # tombol mulai percakapan
    assert "static/css/home.css" in html


def test_halaman_chat(client):
    res = client.get("/chat")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Chat MamaBot" in html
    assert "static/js/chat.js" in html


def test_file_statis_tersedia(client):
    for path in ("css/home.css", "css/style.css", "js/chat.js", "img/mamabot-icon.svg"):
        assert client.get(f"/static/{path}").status_code == 200, path


def test_halaman_tidak_ada_404(client):
    res = client.get("/tidak-ada")
    assert res.status_code == 404
    assert "Halaman tidak ditemukan" in res.get_data(as_text=True)


def test_api_chat_berhasil(client):
    res = client.post("/api/chat", json={"message": "kapan bayi mulai mpasi"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["intent"] == "mulai_mpasi"
    assert data["reply"]


@pytest.mark.parametrize("payload", [
    {"message": ""},
    {"message": "   "},
    {"message": "a" * 501},
    {},
])
def test_api_chat_input_tidak_valid(client, payload):
    assert client.post("/api/chat", json=payload).status_code == 400


def test_riwayat_tersimpan_dan_bisa_dihapus(client):
    client.post("/api/chat", json={"message": "halo"})
    riwayat = client.get("/api/history").get_json()
    assert [r["sender"] for r in riwayat] == ["user", "bot"]

    client.delete("/api/history")
    assert client.get("/api/history").get_json() == []


def test_riwayat_terpisah_antar_pengunjung(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "t.db")})
    a, b = app.test_client(), app.test_client()
    a.post("/api/chat", json={"message": "halo"})
    assert len(a.get("/api/history").get_json()) == 2
    assert b.get("/api/history").get_json() == []


def test_statistik_intent(client):
    client.post("/api/chat", json={"message": "halo"})
    stats = client.get("/api/stats").get_json()
    assert stats[0]["intent"] == "salam"


def test_api_explain(client):
    data = client.post("/api/explain", json={"message": "bayi boleh makan madu"}).get_json()
    assert data["threshold"] == 0.45
    assert data["candidates"][0]["intent"] == "madu_bayi"


def test_halaman_admin_menampilkan_pertanyaan_tak_dikenali(client):
    client.post("/api/chat", json={"message": "harga bensin berapa"})
    html = client.get("/admin").get_data(as_text=True)
    assert "harga bensin berapa" in html
    assert "tidak dikenali" in html


def test_pesan_berisi_html_tidak_dieksekusi_di_admin(client):
    client.post("/api/chat", json={"message": "<script>alert(1)</script>"})
    html = client.get("/admin").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html      # Jinja2 meng-escape otomatis


def test_admin_key_melindungi_halaman_admin(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "t.db"), "ADMIN_KEY": "rahasia"})
    c = app.test_client()
    assert c.get("/admin").status_code == 403
    assert c.get("/api/stats").status_code == 403
    assert c.get("/admin?key=rahasia").status_code == 200

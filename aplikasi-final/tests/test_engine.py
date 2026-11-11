"""Uji unit untuk mesin chatbot MamaBot (tanpa Flask)."""
from pathlib import Path

import pytest

from chatbot.engine import ChatbotEngine, load_themes, preprocess, similarity, validate_theme

THEMES = load_themes(Path(__file__).resolve().parent.parent / "themes")
THEME = THEMES["mamabot"]


def test_preprocess_normalisasi_dan_stopword():
    # "Bun" dibuang, "gimana" -> "bagaimana", "ya" dan "apa" dibuang
    assert preprocess("Gimana cara menyusui, Bun, ya?") == ["bagaimana", "cara", "menyusui"]


def test_preprocess_singkatan_ibu_dan_bayi():
    assert preprocess("bumil ngopi") == ["ibu", "hamil", "kopi"]


def test_similarity_kalimat_sama_bernilai_satu():
    t = ["makanan", "ibu", "hamil"]
    assert similarity(t, t) == 1.0


def test_similarity_kalimat_berbeda_rendah():
    assert similarity(["bensin"], ["makanan", "ibu", "hamil"]) < 0.3


def test_tema_mamabot_termuat_dan_valid():
    assert "mamabot" in THEMES
    assert validate_theme(THEME) == []


def test_jumlah_intent_dan_pola_memenuhi_syarat():
    # Syarat template: minimal 10 intent, tiap intent >= 5 pola dan >= 2 respons
    assert len(THEME["intents"]) >= 10
    for intent in THEME["intents"]:
        assert len(intent["patterns"]) >= 5, intent["tag"]
        assert len(intent["responses"]) >= 2, intent["tag"]


@pytest.mark.parametrize("pesan, intent", [
    ("halo bunda", "salam"),
    ("Bun, makanan apa yang baik untuk ibu hamil?", "makanan_hamil"),
    ("ibu hamil boleh minum kopi ga", "kopi_hamil"),
    ("kenapa mual saat hamil", "mual_hamil"),
    ("Apa saja tanda-tanda mau melahirkan?", "tanda_melahirkan"),
    ("Bagaimana tanda-tanda persalinan?", "tanda_melahirkan"),
    ("Gimana cara menyusui yang benar, ya?", "posisi_menyusui"),
    ("Kapan bayi mulai diberikan MPASI?", "mulai_mpasi"),
    ("Bun, bayi umur 6 bulan sudah boleh makan apa?", "menu_mpasi"),
    ("bayi boleh makan madu ga", "madu_bayi"),
    ("cara memandikan bayi", "mandi_bayi"),
    ("makasih ya bun", "terima_kasih"),
])
def test_klasifikasi_intent(pesan, intent):
    tag, _ = ChatbotEngine(THEME).classify(pesan)
    assert tag == intent


@pytest.mark.parametrize("pesan", [
    "bayi saya kejang",
    "bayi sesak napas",
    "ibu mengalami perdarahan hebat",
])
def test_keadaan_darurat_dikenali(pesan):
    """Pesan gawat darurat tidak boleh jatuh ke fallback."""
    tag, _ = ChatbotEngine(THEME).classify(pesan)
    assert tag == "darurat_medis"


def test_salah_ketik_masih_dikenali():
    tag, _ = ChatbotEngine(THEME).classify("cara menyusi bayi dengan benar")
    assert tag == "posisi_menyusui"


def test_pertanyaan_di_luar_tema_memberi_fallback():
    hasil = ChatbotEngine(THEME).reply("siapa presiden indonesia")
    assert hasil["intent"] is None
    assert hasil["reply"] in THEME["fallback"]


def test_pesan_kosong_tidak_error():
    hasil = ChatbotEngine(THEME).reply("   ")
    assert hasil["intent"] is None


def test_perkenalan_menyebut_nama_bot():
    hasil = ChatbotEngine(THEME).reply("kamu siapa")
    assert "MamaBot" in hasil["reply"]


def test_explain_mengurutkan_kandidat_dari_skor_tertinggi():
    kandidat = ChatbotEngine(THEME).explain("bayi boleh makan madu ga")
    assert kandidat[0]["intent"] == "madu_bayi"
    skor = [k["score"] for k in kandidat]
    assert skor == sorted(skor, reverse=True)


def test_validate_theme_menemukan_kesalahan():
    rusak = {"id": "x", "name": "X", "bot_name": "B", "avatar": "*", "color": "#000",
             "description": "d", "greeting": "g", "suggestions": [], "fallback": ["f"],
             "intents": [{"tag": "a", "patterns": ["halo"], "responses": ["hai"]},
                         {"tag": "b", "patterns": ["halo"], "responses": []}]}
    masalah = validate_theme(rusak)
    assert any("responses kosong" in m for m in masalah)
    assert any("'a' dan 'b'" in m for m in masalah)


def test_semua_tombol_saran_dijawab_intent_yang_benar():
    """Tombol saran di chat.html dan di mamabot.json harus mengarah ke intent yang masuk akal."""
    engine = ChatbotEngine(THEME)
    harapan = {
        "Apa makanan yang baik untuk ibu hamil?": "makanan_hamil",
        "Bagaimana tanda-tanda persalinan?": "tanda_melahirkan",
        "Bagaimana cara menyusui yang benar?": "posisi_menyusui",
        "Kapan bayi mulai diberikan MPASI?": "mulai_mpasi",
    }
    for pesan, intent in harapan.items():
        assert engine.classify(pesan)[0] == intent, pesan
    for saran in THEME["suggestions"]:
        assert engine.classify(saran)[0] is not None, saran


def test_akurasi_data_uji_minimal_90_persen():
    from evaluate import baca_data, evaluasi
    akurasi, _ = evaluasi(THEME, baca_data("mamabot"), 0.45)
    assert akurasi >= 0.9

"""
MamaBot - chatbot kesehatan ibu dan anak (Flask, rule-based).

Jalankan:
    python app.py
lalu buka http://127.0.0.1:5000
"""
import os
import uuid
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request, session

from chatbot import ChatbotEngine, ChatHistory, load_themes

BASE_DIR = Path(__file__).resolve().parent
THEME_ID = "mamabot"          # nama file tema: themes/mamabot.json


def create_app(config: dict | None = None) -> Flask:
    """Application factory: memudahkan konfigurasi berbeda untuk pengujian."""
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "ganti-dengan-kunci-rahasia"),
        DATABASE=os.environ.get("DATABASE", str(BASE_DIR / "chat_history.db")),
        THEMES_DIR=str(BASE_DIR / "themes"),
        THRESHOLD=float(os.environ.get("THRESHOLD", "0.45")),
        ADMIN_KEY=os.environ.get("ADMIN_KEY", ""),   # kosong = halaman admin terbuka
        MAX_LEN=500,
    )
    if config:
        app.config.update(config)

    # Muat tema MamaBot dan buat satu engine untuknya
    themes = load_themes(app.config["THEMES_DIR"])
    if THEME_ID not in themes:
        raise RuntimeError(f"File themes/{THEME_ID}.json tidak ditemukan")
    theme = themes[THEME_ID]
    engine = ChatbotEngine(theme, app.config["THRESHOLD"])
    history = ChatHistory(app.config["DATABASE"])

    def get_session_id() -> str:
        """Setiap pengunjung mendapat ID sesi unik yang disimpan di cookie."""
        if "sid" not in session:
            session["sid"] = uuid.uuid4().hex
        return session["sid"]

    def check_admin():
        kunci = app.config["ADMIN_KEY"]
        if kunci and request.args.get("key") != kunci:
            abort(403, description="Kunci admin salah atau tidak ada")

    # ------------------------------------------------------------------ #
    # Halaman (mengembalikan HTML)
    # ------------------------------------------------------------------ #
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/chat")
    def chat():
        return render_template("chat.html")

    @app.route("/admin")
    def admin():
        check_admin()
        return render_template(
            "admin.html", theme=theme,
            summary=history.summary(THEME_ID),
            stats=history.stats(THEME_ID),
            unknown=history.unknown_questions(THEME_ID),
            threshold=app.config["THRESHOLD"],
        )

    # ------------------------------------------------------------------ #
    # REST API (mengembalikan JSON)
    # ------------------------------------------------------------------ #
    @app.post("/api/chat")
    def api_chat():
        data = request.get_json(silent=True) or {}
        message = str(data.get("message", "")).strip()

        if not message:
            return jsonify({"error": "Pesan tidak boleh kosong"}), 400
        if len(message) > app.config["MAX_LEN"]:
            return jsonify({"error": f"Pesan maksimal {app.config['MAX_LEN']} karakter"}), 400

        sid = get_session_id()
        result = engine.reply(message)

        history.add(sid, THEME_ID, "user", message, result["intent"], result["score"])
        history.add(sid, THEME_ID, "bot", result["reply"], result["intent"], result["score"])
        return jsonify(result)

    @app.post("/api/explain")
    def api_explain():
        """Tiga kandidat intent teratas: untuk melihat cara bot 'berpikir'."""
        data = request.get_json(silent=True) or {}
        message = str(data.get("message", ""))[: app.config["MAX_LEN"]]
        return jsonify({"threshold": app.config["THRESHOLD"],
                        "candidates": engine.explain(message)})

    @app.get("/api/history")
    def api_history():
        return jsonify(history.get(get_session_id(), THEME_ID))

    @app.delete("/api/history")
    def api_clear_history():
        history.clear(get_session_id(), THEME_ID)
        return jsonify({"status": "ok"})

    @app.get("/api/stats")
    def api_stats():
        check_admin()
        return jsonify(history.stats(THEME_ID))

    @app.errorhandler(403)
    @app.errorhandler(404)
    def error_page(err):
        if request.path.startswith("/api/"):
            return jsonify({"error": err.description}), err.code
        return render_template("404.html", message=err.description, code=err.code), err.code

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

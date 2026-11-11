"""
Chat dengan MamaBot langsung di terminal, tanpa browser.

Contoh:
    python cli.py
    python cli.py --debug          # tampilkan 3 kandidat intent teratas
Ketik 'keluar' untuk berhenti.
"""
import argparse
from pathlib import Path

from chatbot import ChatbotEngine, load_themes

BASE_DIR = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="MamaBot di terminal")
    parser.add_argument("--tema", default="mamabot", help="id tema (nama file JSON tanpa .json)")
    parser.add_argument("--ambang", type=float, default=0.45, help="ambang batas skor")
    parser.add_argument("--debug", action="store_true", help="tampilkan kandidat intent")
    args = parser.parse_args()

    themes = load_themes(BASE_DIR / "themes")
    if args.tema not in themes:
        print(f"Tema '{args.tema}' tidak ada. Pilihan: {', '.join(themes)}")
        return
    theme = themes[args.tema]
    bot = ChatbotEngine(theme, args.ambang)

    print(f"{theme['avatar']} {theme['bot_name']}: {theme['greeting']}")
    print("(ketik 'keluar' untuk berhenti)\n")
    while True:
        try:
            pesan = input("Anda: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if pesan.lower() in {"keluar", "exit", "quit"}:
            break
        hasil = bot.reply(pesan)
        print(f"{theme['bot_name']}: {hasil['reply']}")
        label = hasil["intent"] or "tidak dikenali"
        print(f"   [intent: {label} · skor {hasil['score']:.2f}]")
        if args.debug:
            for i, k in enumerate(bot.explain(pesan), 1):
                print(f"   {i}. {k['intent']:<18} {k['score']:.2f}  pola: \"{k['pattern']}\"")
        print()
    print("Sampai jumpa!")


if __name__ == "__main__":
    main()

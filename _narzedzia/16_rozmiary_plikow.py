# -*- coding: utf-8 -*-
"""Rozmiary prawdziwych plików do pobrania (25.11.2026) -> assets/rozmiary.js (SP.kb = {ścieżka względem assets: kB}).

Centrum plików i lista „Pliki” budują paczki ZIP w przeglądarce wyłącznie z plików, które są na serwerze —
ten spis daje im rzeczywiste rozmiary (licznik MB, kontrola przed pobraniem).
Uruchamiać po każdej zmianie w assets/img, assets/karty, assets/dokumenty, assets/cad (np. po 7_karty_pdf.py, 8_zasoby_kart.py, 10_modele_3d.py).
"""
import os, io, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets")
DIRS = ["img", "karty", "dokumenty", "cad", "akademia"]

kb = {}
for d in DIRS:
    for base, _, files in os.walk(os.path.join(A, d)):
        for f in files:
            if f.endswith((".tmp", ".db")) or f.startswith("."):
                continue
            p = os.path.join(base, f)
            rel = os.path.relpath(p, A).replace(os.sep, "/")
            kb[rel] = max(1, round(os.path.getsize(p) / 1024))

js = ("/* Wygenerowano (_narzedzia/16_rozmiary_plikow.py): rozmiary plików na serwerze w kB — do paczek ZIP w Centrum plików. */\n"
      "window.SP = window.SP || {};\nwindow.SP.kb = " + json.dumps(kb, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + ";\n")
io.open(os.path.join(A, "rozmiary.js"), "w", encoding="utf-8").write(js)
print("Plików: %d, razem %.1f MB, rozmiary.js %.0f kB" % (len(kb), sum(kb.values()) / 1024, len(js.encode("utf-8")) / 1024))

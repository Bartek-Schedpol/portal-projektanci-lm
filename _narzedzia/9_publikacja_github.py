# -*- coding: utf-8 -*-
"""Przygotowanie publicznej wersji makiety A „Biblioteka” do repozytorium GitHub (GitHub Pages).

Kopiuje z koncepcja-portalu do folderu repozytorium tylko to, co potrzebne makiecie A:
  a-biblioteka/, karta/, assets/ (dane, ikony, fonty, zdjęcia, rysunki, znaki, karty PDF), _narzedzia/ (bez tego skryptu nie zmienia się nic)
Pomija: opracowanie (index.html, PDF), koncepcje B i C, zrzuty ekranów.
W a-biblioteka/index.html włącza tryb SPP_SOLO (pasek prezentera bez linków do opracowania i koncepcji B/C).

Użycie:  python 9_publikacja_github.py  [folder_repo]
Domyślny folder repo: "18. Leroy Merlin - Portal\\github-portal-lm". Potem: git add -A, commit, push.
"""
import os, sys, io, re, shutil

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
DST = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(SRC), "github-portal-lm")

DIRS = ["v2", "en", "ro", "a-biblioteka", "karta", "assets/fonts", "assets/img", "assets/znaki", "assets/karty", "assets/dokumenty", "assets/akademia", "assets/cad", "_narzedzia"]
FILES = ["assets/data.js", "assets/bokmapa.js", "assets/filmy.js", "assets/modele3d.js", "assets/lm.js", "assets/packshoty.js", "assets/rysunki.js", "assets/dokumenty.js", "assets/icons.js", "assets/proto.js", "assets/staty.js", "assets/rozmiary.js", "assets/i18n.js", "assets/i18n-en.js", "assets/i18n-ro.js",
         "assets/logo.svg", "assets/logo-white.svg", "assets/img-manifest.json"]
SKIP = ("__pycache__", ".tmp", "Thumbs.db", "_audyt_odplyw")   # arkusze audytu tylko lokalnie

INDEX = """<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex,nofollow">
<title>Strefa projektanta Schedpol</title>
<script>/* wersja językowa (25.11.2026): zapamiętany wybór, inaczej język przeglądarki — pl → v2, ro → ro, pozostałe → en */
(function(){var k;try{k=localStorage.getItem('sp-lang')}catch(e){}
if(!k){var l=(navigator.language||'pl').toLowerCase();k=l.indexOf('pl')===0?'pl':(l.indexOf('ro')===0?'ro':'en')}
location.replace(({pl:'v2',en:'en',ro:'ro'}[k]||'v2')+'/index.html'+location.hash)})();</script>
<noscript><meta http-equiv="refresh" content="0; url=v2/index.html"></noscript>
</head>
<body><p><a href="v2/index.html">Polski</a> · <a href="en/index.html">English</a> · <a href="ro/index.html">Română</a></p></body>
</html>
"""

README = """# Strefa projektanta Schedpol × Leroy Merlin — makieta

Klikalna makieta portalu dla projektantów sieci Leroy Merlin (koncepcja A „Biblioteka”):
wyszukiwarka po numerze referencyjnym LM, katalog z filtrami, karta produktu z plikami do pobrania,
Centrum plików z paczkami serii, teczka plików oraz karty produktów PDF (A4) dla 371 indeksów.

**Podgląd:** https://bartek-schedpol.github.io/portal-lm-projektanci/

> Makieta poglądowa — nie jest działającym serwisem. Działa pobieranie kart produktów PDF, kart gwarancyjnych i instrukcji montażu; pozostałe pliki są symulowane.
> Ceny i dostępność produktów: w systemie sklepu Leroy Merlin. Zdjęcia aranżacyjne są wizualizacjami poglądowymi.

## Struktura

| Folder | Zawartość |
|---|---|
| `a-biblioteka/` | makieta portalu (HTML/CSS/JS bez frameworków, router na hashach) |
| `karta/` | szablon karty produktu A4 — podgląd: `karta/index.html?ref=<nr ref. LM>` |
| `assets/data.js` | 371 indeksów i 23 serie (generowane z materiałów Schedpol) |
| `assets/filmy.js` | filmy z kanału YouTube Schedpol (ID sprawdzone oEmbed) i materiały Akademii |
| `assets/bokmapa.js` | mapa regionów BOK (wektor z przeglądu oferty) |
| `assets/lm.js` | gama, EAN i kod dostawcy z eksportu referencji LM (26.03.2026) |
| `assets/packshoty.js` | packshot każdego indeksu wg serii, koloru i kształtu (paczka e-commerce), zdjęcia dodatkowe |
| `assets/rysunki.js`, `assets/img/rys/` | rysunki techniczne do kart |
| `assets/dokumenty.js`, `assets/dokumenty/` | karty gwarancyjne i instrukcje montażu przypisane do indeksów |
| `assets/karty/` | wygenerowane karty produktów PDF — **wersja robocza, do przebudowy** |
| `assets/fonts/` | Roboto (krój strony) i Roboto Condensed (Apache 2.0, karty PDF) |
| `assets/znaki/` | logo Schedpol, znak Leroy Merlin, logo Sensea, znaki gwarancji |
| `_narzedzia/` | skrypty Pythona do odświeżenia danych, zasobów i kart (wymagają materiałów źródłowych spoza repozytorium) |

## Uruchomienie lokalne

```
python -m http.server 8766
```
i otwórz http://localhost:8766/ (makieta działa też po otwarciu `a-biblioteka/index.html` z dysku).

Skrót klawiszowy `H` chowa pasek prezentera, strzałki ← → przełączają ekrany.

© SCHEDPOL Sp. z o.o. Materiały produktowe (zdjęcia, rysunki, opisy) są własnością Schedpol i nie podlegają licencji open source.
Znaki Sensea i Leroy Merlin należą do ich właścicieli i zostały użyte wyłącznie na potrzeby makiety.
"""


def ign(d, names):
    return [n for n in names if n in SKIP or n.endswith(SKIP)]


def main():
    os.makedirs(DST, exist_ok=True)
    for d in DIRS + ["assets"]:                          # wyczyść tylko to, czym zarządza skrypt (zostaje .git)
        p = os.path.join(DST, d)
        if d != "assets" and os.path.isdir(p):
            shutil.rmtree(p)
    for d in DIRS:
        shutil.copytree(os.path.join(SRC, d), os.path.join(DST, d), ignore=ign)
    for f in FILES:
        os.makedirs(os.path.dirname(os.path.join(DST, f)), exist_ok=True)
        shutil.copy2(os.path.join(SRC, f), os.path.join(DST, f))
    a = os.path.join(DST, "a-biblioteka", "v1.html")   # V1; a-biblioteka/index.html = przekierowanie na V2 (24.11.2026)
    s = io.open(a, encoding="utf-8").read()
    if "SPP_SOLO" not in s:
        s = re.sub(r'(<script src="\.\./assets/proto\.js[^"]*"></script>)', r'<script>window.SPP_SOLO = 1;</script>\n\1', s, count=1)
        if "SPP_SOLO" not in s:                         # odnośnik może mieć ?v=… — bez trybu SOLO nie publikujemy
            sys.exit("BŁĄD: nie znaleziono odnośnika do proto.js — tryb SOLO nie został włączony")
    io.open(a, "w", encoding="utf-8", newline="").write(s)
    io.open(os.path.join(DST, "index.html"), "w", encoding="utf-8", newline="\n").write(INDEX)
    io.open(os.path.join(DST, "README.md"), "w", encoding="utf-8", newline="\n").write(README)
    io.open(os.path.join(DST, ".nojekyll"), "w").write("")
    io.open(os.path.join(DST, ".gitignore"), "w", encoding="utf-8").write("__pycache__/\n*.tmp\nThumbs.db\n")
    size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(DST) if ".git" not in r for f in fs)
    print("Gotowe: %s  (%.1f MB)" % (DST, size / 1e6))


if __name__ == "__main__":
    main()

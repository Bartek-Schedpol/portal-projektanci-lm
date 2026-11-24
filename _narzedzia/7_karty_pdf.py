# -*- coding: utf-8 -*-
"""Karty produktów PDF (A4) dla wszystkich indeksów z assets/data.js.

Szablon: karta/index.html?ref=<nr>&druk=1  →  Edge bez okna (print-to-pdf)  →  assets/karty/Karta-produktu_LM<nr>.pdf
Ten sam szablon jest podglądem w portalu, więc karta i strona nie rozjadą się treściowo.

Wymaga działającego podglądu:  python -m http.server 8766 --directory "<...>\\koncepcja-portalu"
Użycie:
  python 7_karty_pdf.py                 -> wszystkie indeksy
  python 7_karty_pdf.py 89189409 9...   -> tylko wskazane
  python 7_karty_pdf.py --kontrola      -> tylko sprawdzenie gotowych plików (1 strona A4, fonty Roboto)
"""
import os, sys, io, json, subprocess, tempfile, shutil, time
from concurrent.futures import ThreadPoolExecutor

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "karty")
BASE = "http://localhost:8766/karta/index.html?druk=1&ref="
EDGE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"   # Chrome: Edge 157 bez okna nie drukuje PDF (11.2026)
if not os.path.exists(EDGE):
    EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
WORKERS = 6


def refs_all():
    s = io.open(os.path.join(ROOT, "assets", "data.js"), encoding="utf-8").read()
    j = s[s.index("window.SP = ") + 12: s.index(";\n\n/* ---- pomocnicze")]
    return [p["ref"] for p in json.loads(j)["products"]]


def pdf_path(ref):
    return os.path.join(OUT, "Karta-produktu_LM%s.pdf" % ref)


def one(ref):
    prof = tempfile.mkdtemp(prefix="edge-karta-")
    try:
        out = pdf_path(ref)
        if os.path.exists(out):
            os.remove(out)                                 # stary plik nie może „udawać” nowego, gdy serwer nie odpowiada
        cmd =[EDGE, "--headless=new", "--disable-gpu", "--no-first-run", "--disable-extensions", "--user-data-dir=" + prof,
               "--virtual-time-budget=15000", "--no-pdf-header-footer", "--print-to-pdf=" + out, BASE + ref]
        subprocess.run(cmd, capture_output=True, timeout=120)
        if not os.path.exists(out):
            return ref, False
        import fitz                                        # odchudzenie: zdjęcia do 180 dpi, podzbiór fontów
        d = fitz.open(out)
        d.set_metadata({"title": "Karta produktu LM %s" % ref, "author": "SCHEDPOL Sp. z o.o.", "subject": "Karta produktu dla projektantów Leroy Merlin"})
        d.rewrite_images(dpi_threshold=170, dpi_target=150, quality=78)
        d.subset_fonts()
        tmp = out + ".tmp"
        d.ez_save(tmp); d.close()
        os.replace(tmp, out)
        return ref, True
    finally:
        shutil.rmtree(prof, ignore_errors=True)


def kontrola(refs):
    import fitz
    bad = []
    total = 0
    for r in refs:
        p = pdf_path(r)
        if not os.path.exists(p):
            bad.append((r, "brak pliku")); continue
        total += os.path.getsize(p)
        d = fitz.open(p)
        w, h = d[0].rect.width / 72 * 25.4, d[0].rect.height / 72 * 25.4
        fonts = {f[3] for pg in d for f in pg.get_fonts()}
        txt = d[0].get_text()
        if d.page_count != 1: bad.append((r, "%d stron" % d.page_count))
        if abs(w - 210) > 1 or abs(h - 297) > 1: bad.append((r, "format %.0f×%.0f" % (w, h)))
        if not all("Roboto" in f for f in fonts): bad.append((r, "fonty: %s" % ", ".join(sorted(fonts))))
        if r not in txt: bad.append((r, "brak nr ref. w warstwie tekstowej"))
        # packshot (~94 mm przy 150 dpi ≈ 550 px) musi być w PDF; same ikonki (14–240 px) znaczą, że zdjęcia nie zdążyły się wczytać
        # (zdarza się przy generowaniu wielu kart naraz — 11.2026 na stronę trafiło 9 kart bez obrazków, a stara kontrola ich nie złapała)
        if max([im[2] for im in d[0].get_images(full=True)] or [0]) < 300: bad.append((r, "brak packshotu (zdjęcia nie zdążyły się wczytać)"))
        hit = d[0].search_for("charakter informacyjny")
        if not hit or hit[-1].y1 > d[0].rect.height - 5 * 72 / 25.4:
            bad.append((r, "stopka poza stroną — treść się nie mieści"))
        d.close()
    print("Sprawdzono: %d plików, razem %.1f MB, średnio %.0f kB" % (len(refs), total / 1e6, total / max(1, len(refs)) / 1e3))
    for b in bad:
        print("  PROBLEM", b[0], "—", b[1])
    print("OK" if not bad else "Problemów: %d" % len(bad))
    return sorted({b[0] for b in bad})


def main():
    args = sys.argv[1:]
    import urllib.request
    try:
        urllib.request.urlopen(BASE.split("karta/")[0] + "karta/index.html", timeout=5).read(1)
    except Exception as e:
        sys.exit("Serwer podglądu nie odpowiada (%s) — uruchom: python -m http.server 8766 w folderze koncepcja-portalu" % e)
    os.makedirs(OUT, exist_ok=True)
    refs = [a for a in args if a.isdigit()] or refs_all()
    if "--kontrola" not in args:
        t = time.time()
        with ThreadPoolExecutor(WORKERS) as ex:
            res = list(ex.map(one, refs))
        miss = [r for r, ok in res if not ok]
        print("Wygenerowano %d/%d w %.0f s" % (len(res) - len(miss), len(res), time.time() - t))
        if miss: print("Brak:", " ".join(miss))
    bad = kontrola(refs)
    if bad and "--kontrola" not in args:                 # druga próba pojedynczo (bez obciążenia serwera)
        print("Ponawiam pojedynczo:", len(bad))
        for r in bad: one(r)
        kontrola(refs)


if __name__ == "__main__":
    main()

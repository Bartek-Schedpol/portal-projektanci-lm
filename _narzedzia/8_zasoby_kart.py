# -*- coding: utf-8 -*-
"""Zasoby kart produktów: gama/EAN z eksportu LM, znaki marek i gwarancji, rysunki techniczne.

Wejście (folder "18. Leroy Merlin - Portal\\materiały"):
  - 2026-03-26T13-41-37-moje-referencje.xlsx      eksport referencji z systemu LM (gama, EAN, kod dostawcy)
  - Etykiety Frigo i Ipsilon\\*\\SNS*.pdf          etykiety Sensea: logo, znak „YEAR Guarantee”, rysunek z wymiarami danego rozmiaru
  - Przegląd oferty (Leroy Merlin) 2025.09a A4.pdf  znaki „LAT GWARANCJI” Schedpol
  - 2026 - Paczka Ecommerce LEROY MERLIN\\...      rysunki techniczne pozostałych serii
Wyjście:
  assets/lm.js        nadpisuje p.g (gama) i dopisuje p.ean, p.sup wg eksportu LM
  assets/znaki/*.png  logo Sensea, znaki gwarancji
  assets/img/rys/*    rysunki techniczne;  assets/rysunki.js  (SP.rys: nr ref. → plik)
Użycie: python 8_zasoby_kart.py
"""
import os, sys, io, json, glob, re, shutil
import fitz, openpyxl
from PIL import Image, ImageOps

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MAT = os.path.join(os.path.dirname(ROOT), "materiały")
ECOM = "\\\\?\\" + os.path.abspath(os.path.join(MAT, "2026 - Paczka Ecommerce LEROY MERLIN"))   # długie ścieżki Windows
ETYK = os.path.join(MAT, "Etykiety Frigo i Ipsilon")
PRZEGLAD = os.path.join(MAT, "Przegląd oferty (Leroy Merlin) 2025.09a A4.pdf")
XLSX = os.path.join(MAT, "2026-03-26T13-41-37-moje-referencje.xlsx")
OUT_Z = os.path.join(ROOT, "assets", "znaki")
OUT_R = os.path.join(ROOT, "assets", "img", "rys")


def products():
    s = io.open(os.path.join(ROOT, "assets", "data.js"), encoding="utf-8").read()
    return json.loads(s[s.index("window.SP = ") + 12: s.index(";\n\n/* ---- pomocnicze")])["products"]





# ---------- 1. eksport LM ----------
# Kształty, w których arkusz tytułów rozjeżdża się z nazwą w systemie LM, a LM ma rację (sprawdzone z etykietą/wymiarem).
# Uwaga: 95495956 („BALANS KW 120X90”) — błąd po stronie LM, w danych zostaje „prostokątny”.
SHAPE_FIX = {"45256512": "pięciokątny", "88758947": "pięciokątny", "82763748": "pięciokątny", "88758948": "pięciokątny",
             "82763752": "pięciokątny", "86448669": "prostokątny",
             "87098822": "półokrągły", "87098831": "półokrągły", "87098801": "półokrągły"}   # 25.11.2026: Magnetic 1/4K (audyt odpływu)
# Gama ustalona ręcznie dla indeksów spoza eksportu LM (decyzja Schedpol 23.11.2026).
GAMA_FIX = {"83648377": "X"}
def lm_export(P):
    ws = openpyxl.load_workbook(XLSX, data_only=True).active
    head = [str(c or "").strip() for c in next(ws.iter_rows(min_row=1, max_row=1, values_only=True))]
    ix = {k: head.index(k) for k in ("Referencja produktu", "GTIN (EAN)", "Referencja Dostawcy", "Nazwa produktu", "Gama")}
    L = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        ref = str(r[ix["Referencja produktu"]] or "").strip()
        if ref:
            L[ref] = {"g": str(r[ix["Gama"]] or "").strip(), "ean": str(r[ix["GTIN (EAN)"]] or "").strip(),
                      "sup": str(r[ix["Referencja Dostawcy"]] or "").strip(), "n": str(r[ix["Nazwa produktu"]] or "").strip()}
    refs = {p["ref"] for p in P}
    only_lm = {k: v["n"] for k, v in L.items() if k not in refs}
    only_data = sorted(refs - set(L))
    js = ("/* Wygenerowano z eksportu referencji LM (26.03.2026): gama, EAN, kod dostawcy. Ma pierwszeństwo przed przeglądem oferty. */\n"
          "(function (SP) {\n  var L = " + json.dumps({k: {x: v[x] for x in ("g", "ean", "sup")} for k, v in L.items() if k in refs}, ensure_ascii=False) + ";\n"
          "  SP.lmDate = '26.03.2026';\n  SP.lmOnly = " + json.dumps(only_lm, ensure_ascii=False) + ";\n"
          "  var SHAPE = " + json.dumps(SHAPE_FIX, ensure_ascii=False) + ";  /* kształt wg nazwy w systemie LM (arkusz tytułów był błędny) */\n"
          "  var GAMA = " + json.dumps(GAMA_FIX, ensure_ascii=False) + ";  /* gama ustalona ręcznie — indeksy spoza eksportu LM */\n"
          "  SP.products.forEach(function (p) { var x = L[p.ref]; if (x) { p.g = x.g; p.ean = x.ean; p.sup = x.sup; } else { p.g = GAMA[p.ref] || ''; p.lmMissing = true; }\n"
          "    if (SHAPE[p.ref]) p.shape = SHAPE[p.ref]; });\n"
          "})(window.SP);\n")
    io.open(os.path.join(ROOT, "assets", "lm.js"), "w", encoding="utf-8").write(js)
    print("Eksport LM: %d ref.; tylko w eksporcie: %s; brak w eksporcie: %s" % (len(L), only_lm, only_data))
    return L


# ---------- 2. znaki ----------
def png_clip(page, rect, out, dpi=600):
    pix = page.get_pixmap(dpi=dpi, clip=rect, alpha=True)
    pix.save(out)
    return pix.width, pix.height


def znaki():
    os.makedirs(OUT_Z, exist_ok=True)
    fr = fitz.open(os.path.join(ETYK, "FRIGO 20.01.2025", "SNS4630.pdf"))[0]
    ip = fitz.open(os.path.join(ETYK, "IPSILON 18.10.2024", "SNS2248.pdf"))[0]
    logo = fitz.Rect()
    for d in fr.get_drawings():
        r = d["rect"]
        if r.y0 > 15 and r.y1 < 95 and r.x0 > 90 and r.x1 < 420:
            logo.include_rect(r)
    out = {"sensea": png_clip(fr, logo, os.path.join(OUT_Z, "sensea.png"))}
    badge = fitz.Rect(529.3, 489.6, 578.6, 538.9)           # granatowy znak „YEAR Guarantee” z etykiet
    out["gw-sensea-10"] = png_clip(fr, badge, os.path.join(OUT_Z, "gw-sensea-10.png"))
    out["gw-sensea-7"] = png_clip(ip, badge, os.path.join(OUT_Z, "gw-sensea-7.png"))
    po = fitz.open(PRZEGLAD)
    for key, pg, rect in (("gw-10", 12, fitz.Rect(512.7, 34.2, 579.7, 101.2)), ("gw-31", 20, fitz.Rect(515.9, 34.2, 582.9, 101.2)),
                          ("gw-7", 2, fitz.Rect(755.7, 177.4, 803.5, 226.2))):
        out[key] = png_clip(po[pg], rect, os.path.join(OUT_Z, key + ".png"))
    print("Znaki:", out)


# ---------- 3. rysunki ----------
def label_bound(page):
    D = page.get_drawings()
    ne = [d["rect"].y0 for d in D if d["rect"].y0 > 760 and d["rect"].width > 250 and d["rect"].height < 10 and "f" in d["type"]]
    box = [d["rect"].y0 - 16 for d in D if 780 < d["rect"].y0 < 1000 and d["rect"].width > 100 and d["rect"].height > 25 and "f" in d["type"]]
    yne = min(ne + box + [905])                            # nad linią „Ne contient pas…” i szarym polem piktogramów
    A = [d for d in D if 680 < d["rect"].y0 and d["rect"].y1 < yne - 1 and d["rect"].x0 > 110 and d["rect"].x1 < 370]
    S = fitz.Rect()
    for d in A:
        if "s" in d["type"] and d["rect"].y0 > 700:
            S.include_rect(d["rect"])
    u = fitz.Rect(S)
    for d in A:
        r = d["rect"]
        if "s" in d["type"]:
            continue
        cy = (r.y0 + r.y1) / 2
        rot = r.height > r.width * 1.2 and r.height > 9
        if (S.y0 - 2 <= cy <= S.y1 + 10 and S.x0 - 30 <= r.x0 and r.x1 <= S.x1 + 30) or \
           (rot and S.y0 - 22 <= r.y0 and r.y1 <= S.y1 + 10 and S.x0 - 30 <= r.x0 <= S.x1 + 30):
            u.include_rect(r)
    return u + (-4, -4, 4, 4)


def trim_save(im, out, maxpx=1700):
    im = im.convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    diff = ImageOps.invert(ImageOps.grayscale(Image.composite(im, bg, Image.new("L", im.size, 255))))
    box = diff.point(lambda v: 255 if v > 18 else 0).getbbox()
    if box:
        pad = int(max(im.size) * 0.015)
        im = im.crop((max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad)))
    im.thumbnail((maxpx, maxpx), Image.LANCZOS)
    im.save(out, "PNG", optimize=True) if out.endswith(".png") else im.save(out, "JPEG", quality=86, optimize=True)
    return im.size


def open_src(path):
    if path.lower().endswith(".pdf"):
        pg = fitz.open(path)[0]
        pix = pg.get_pixmap(dpi=200)
        return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        im = bg
    return im.convert("RGB")


import unicodedata


def _n(s):
    return unicodedata.normalize("NFC", s).lower().strip()


def E(*parts):
    """Ścieżka w paczce e-commerce odporna na NFC/NFD i wielkość liter w nazwach folderów."""
    cur = ECOM
    for part in parts:
        try:
            hit = [x for x in os.listdir(cur) if _n(x) == _n(part)]
        except OSError:
            return os.path.join(cur, *parts[parts.index(part):])
        cur = os.path.join(cur, hit[0] if hit else part)
    return cur
SHAPE = {"kwadratowy": "kw", "prostokątny": "pr", "półokrągły": "po", "pięciokątny": "pi"}
ECOM_MAP = {
    ("Balans", "kw"): E("BALANS", "RYSUNEK TECHNICZNY - WSZYTSKIE BRODZIKI", "BALANS 35mm 2021 (M3) kwadrat.png"),
    ("Balans", "pr"): E("BALANS", "RYSUNEK TECHNICZNY - WSZYTSKIE BRODZIKI", "BALANS LM 2026 - prostokąt.png"),
    ("Comfo", "kw"): E("COMFO", "1. Kwadrat", "3. Rysunek techniczny", "Rysunek_techniczny_Comfo_2500x2500px-300dpi_kwadrat_JPG.jpg"),
    ("Comfo", "po"): E("COMFO", "2. Półokragły", "3. Rysunek techniczny", "Rysunek_techniczny_Comfo_2500x2500px_300dpi_półokrągły_JPG.jpg"),
    ("Comfo", "pr"): E("COMFO", "3.Prostokąt", "2022 Rys tech Eko prostokąt 80x100cm.pdf"),
    ("Consist", "kw"): E("CONSIST", "Kwadrat", "3. Rys. Techniczny", "Rysunek_techniczny_Consist_2500x2500px_300dpi_kwadrat_JPG.jpg"),
    ("Consist", "pr"): E("CONSIST", "Prosotkąt", "3.Rys Techniczny", "Rysunek_techniczny_Consist_2500x2500px_300dpi_prostokąt_PDF.jpg"),
    ("Corrina", "kw"): E("CORRINA", "Kwadrat", "3. Rys techniczny", "Rysunek_techniczny_Corrina_2500x2500px_300dpi_kwadrat_JPG.jpg"),
    ("Dafne", "po"): E("DAFNE", "Półokrągły", "3. Rys techniczny", "Rysunek_techniczny_Dafne_2500x2500px_300dpi_półokrągły_JPG.jpg"),
    ("Dante", "kw"): E("DANTE", "1. Kwadrat", "3. Rys techniczny", "Rysunek_techniczny_Dante_2500x2500px_300dpi_kwadrat-JPG.jpg"),
    ("Dante", "po"): E("DANTE", "2. Półokrągły", "3. Rys. Techniczny", "Rysunek_techniczny_Dante_2500x2500px-300dpi_półokrągły_JPG.jpg"),
    ("Go Baby", "po"): E("GO BABY", "Półokragły", "3. Rys techniczny", "Rysunek_techniczny_Go_Baby_2500x2500px-300dpi_półokrągły_JPG.jpg"),
    ("Grawello", "kw"): E("GRAWELLO", "1. Kwdrat", "3. Rys techniczny", "Rysunek_Techniczny_Grawello_2500x2500p_300dpi_kwadrat_JPG.jpg"),
    ("Grawello", "po"): E("GRAWELLO", "2. Półokrągły", "3. Rys techniczny", "Rysunek_techniczny_Grawello_2500x2500px_300dpi_półokragły_JPG.jpg"),
    ("Grawello", "pr"): E("GRAWELLO", "3. Prostokąt", "3. Rys techniczny", "Rysunek_techniczny_Grawello_2500x2500px_300dpi_prostokąt-JPG.jpg"),
    ("Integral", "kw"): E("INTEGRAL", "White Stone", "1. Kwdrat", "3. Rys techniczny", "Rysunek_techniczny_Integral_2500x2500px_300dpi_JPG.jpg"),
    ("Integral", "pr"): E("INTEGRAL", "White Stone", "2. Prostokąt", "3. Rys techniczny", "Rysunek_techniczny_Integral_2500x2500px_300dpi_prostokąt_JPG.jpg"),
    ("Magnetic", "kw"): E("MAGNETIC", "2. Biały gładki", "1. KWADRAT", "2. RYSUNEK TECHNICZNY", "Rysunek_techniczny_Magnetic_Smooth-White_2500x2500px_300dpi_kwadrat_JPG.jpg"),
    ("Magnetic", "po"): E("MAGNETIC", "2. Biały gładki", "2. PÓŁOKRĄGŁY", "2. RYSUNEK TECHNICZNY", "Rysunek_techniczny_Magnetic_Smooth_White_2500x2500px_300dpi_półokragły_JPG.jpg"),
    ("Magnetic", "pr"): E("MAGNETIC", "2. Biały gładki", "3. PROSTOKĄT", "2. RYSUNEK TECHNICZNY", "Rysunek_techniczny_Magnetic_2500x2500px_300dpi_prostokąt_JPG.jpg"),
    ("Sinergid", "kw"): E("SINEGRID", "Sinegrid biały gładki", "1. kwadrat", "2. rysunek techniczny", "Rysunek_techniczny_sinegrid_Smooth_White_2500x2500px_300dpi_kwadrat_JPG.jpg"),
    ("Sinergid", "po"): E("SINEGRID", "Sinegrid biały gładki", "2. półokrągły", "2. rysunek techniczny", "Rysunek_techniczny_sinegrid_Smooth_White_2500x2500px_300dpi_półokrągły_JPG.jpg"),
    ("Sinergid", "pr"): E("SINEGRID", "Sinegrid biały gładki", "3. prostokąt", "2. rysunek techniczny", "Rysunek_Techniczny_Sinegrid_2500x2500px-300dpi_prostokąt_JPG.jpg"),
    ("Tebe", "kw"): E("TEBE", "Czarny Mat", "1. Kwadrat", "3. Rys techniczny", "Caspar New kwadratowe srodek Syfon 2023.jpg"),
    ("Tebe", "po"): E("TEBE", "Czarny Mat", "2. Półokrągły", "3. Rys techniczny", "Rysunek_techniczny_Tebe_Black_Stone_2500x2500p;x_300dpi_JPG.jpg"),
    ("Torres", "pr"): E("TORRES", "TORRES BIAŁY MAT", "3. Rys techniczny", "Rysunek_techniczny_torres_White_Mat_2500x2500p;x_300dpi_JPG.jpg"),
    ("Frigo", "kw"): E("FRIGO - sensea", "FRIGO BIAŁY GŁADKI", "GOTOWE PACZKI - PLIKI 300 DPI", "FRIGO BIAŁY GŁADKI KWADRAT", "3. RYS. TECHNICZNY", "RYS TECH. FRIGO KWADRAT 2026.png"),
    ("Frigo", "pr"): E("FRIGO - sensea", "FRIGO BIAŁY GŁADKI", "GOTOWE PACZKI - PLIKI 300 DPI", "FRIGO BIAŁY GŁADKI PROSTOKĄT", "3. RYS. TECHNICZNY", "RYS TECH. FRIGO BIAŁY GŁADKI PROSTOKĄT 2026 jpg.jpg"),
    ("Frigo", "po"): E("FRIGO - sensea", "FRIGO BIAŁY GŁADKI", "GOTOWE PACZKI - PLIKI 300 DPI", "FRIGO BIAŁY GŁADKI PÓŁOKRĄGŁY", "3. RYS. TECHNICZNY", "RYS TECH. FRIGO PÓŁOKRĄGŁY 2026. JPG.jpg"),
}


def ecom_file(p):
    fam, sh = p["fam"], SHAPE.get(SHAPE_FIX.get(p["ref"]) or p.get("shape") or "", "")   # kształt wg nazwy LM ma pierwszeństwo
    if (fam, sh) in ECOM_MAP:
        return ECOM_MAP[(fam, sh)]
    if fam == "Ipsilon":
        f = {"kw": E("IPSILON", "IPSILON BIAŁY GŁADKI", "GOTOWE PACZKI - min. 2500x2500 300dpi", "IPSILON BIAŁY GŁADKI KWADRAT", "1. RYS. TECHNICZNY", "Rysunek techniczny ipsilon kwadrat JPG.jpg"),
             "po": E("IPSILON", "IPSILON Rysunki techniczne", "Ipsilon rys tech okragly 2020.png"),
             "pr": E("IPSILON", "IPSILON Rysunki techniczne", "IPSILON prostokąt 2022.png"),
             "pi": E("IPSILON", "IPSILON Rysunki techniczne", "Ipsilon %dx%d 2600px.png" % (p["a"], p["a"]))}
        return f.get(sh)
    if fam == "Frigo" and sh == "pi":
        return E("FRIGO - sensea", "FRIGO BIAŁY GŁADKI", "GOTOWE PACZKI - PLIKI 300 DPI", "FRIGO BIAŁY GŁADKI PIĘCIOKĄT", "3. RYS. TECHNICZNY",
                 "frigo pięciokąt %dx%d%s" % (p["a"], p["a"], ".jpg" if p["a"] == 80 else " jpg.jpg"))
    if fam == "Harmony":
        sub = "HARMONY PRIME" if "Prime" in p["s"] else "HARMONY"
        if "Black" in p["s"] or (p.get("c") == "czarny"):
            sub += " BLACK"
        f = glob.glob(E("ODPŁYWY LINIOWE", sub, "3. Rys techniczny", "*JPG.jpg"))
        return f[0] if f else None
    if fam == "Wall Comfort":
        thick = str(p.get("h")) == "6"
        d = E("ŚCIANKA", "2. Thick (6cm)", "1. Smooth White", "3. Rys techniczny") if thick else E("ŚCIANKA", "1. Thin (1cm)", "1. Smooth White Thin (1 cm)", "3. Rys techniczny")
        f = glob.glob(os.path.join(d, "*JPG.jpg"))
        return f[0] if f else None
    if fam == "Najazd":
        return E("NAJAZD DO BRODZIKÓW", "Najazd do brodzików - Smooth White", "3. rys. tech", "Rysunek_techniczny_najazd_podjazd_do_brodzików_2500x2500px_300dpi_JPG.jpg")
    if fam == "Maskownica Balans/Integral":
        return E("MASKOWNICE DO BRODZIKÓW BALANSINTEGRAL", "1.Maskownica złota", "3. Rys techniczny", "Rysunek_techniczny_Maskownica_Złota_2500x2500px_300dpi_JPG.jpg")
    if fam == "Nośnik":
        if p["ref"] in ("90151712", "90151713"):
            return E("NOŚNIK DO WANNY", "1.2 Nośnik do PROSTOKĄTNYCH wanien z podcięciem na stopy_led", "3. Rys techniczny",
                     "Rysunek_techniczny_nośnik_do_wanien_prostokątnych_z_podcięciem_na_stopy_led_2500x2500px_300dpi-JPG.jpg")
        if p["ref"] == "44054682":
            return E("NOŚNIK DO WANNY", "2. NOŚNIK DO WANIEN PÓŁOKRĄGŁYCH GAMA X", "3. Rys techniczny", "_Rysunek_techniczny_Elementy_nosnika_do_wanien_półokrągłych_2500x2500px_300dpi_JPG.jpg")
        return None                                         # 43732724: w paczce tylko „Nośniki Stabilsound – montaż” (inna technologia)
    return None


def rysunki(P, L):
    os.makedirs(OUT_R, exist_ok=True)
    R, cache, braki = {}, {}, []
    for p in P:
        sup = (L.get(p["ref"]) or {}).get("sup", "")
        lab = None
        if p["fam"] in ("Frigo", "Ipsilon") and sup:
            cand = glob.glob(os.path.join(ETYK, "*", sup.replace("/", "-") + ".pdf"))
            lab = cand[0] if cand else None
        if lab:
            key = "et-" + os.path.basename(lab)[:-4].lower()
            if key not in cache:
                pg = fitz.open(lab)[0]
                pix = pg.get_pixmap(dpi=300, clip=label_bound(pg))
                im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                cache[key] = trim_save(im, os.path.join(OUT_R, key + ".png"))
            R[p["ref"]] = {"f": key + ".png", "w": cache[key][0], "h": cache[key][1], "src": "etykieta " + os.path.basename(lab)}
            continue
        src = ecom_file(p)
        if not src or not os.path.exists(src):
            braki.append((p["ref"], p["fam"], p.get("shape"), src and os.path.basename(src)))
            continue
        key = "ec-" + re.sub(r"[^a-z0-9]+", "-", (p["fam"] + "-" + os.path.basename(src)).lower().encode("ascii", "ignore").decode())[:70].strip("-")
        if key not in cache:
            cache[key] = trim_save(open_src(src), os.path.join(OUT_R, key + ".png"))
        R[p["ref"]] = {"f": key + ".png", "w": cache[key][0], "h": cache[key][1], "src": "paczka e-commerce: " + os.path.relpath(src, ECOM)}
    js = "/* Wygenerowano: rysunki techniczne dla kart produktów (8_zasoby_kart.py). */\nwindow.SP.rys = " + json.dumps(R, ensure_ascii=False) + ";\n"
    io.open(os.path.join(ROOT, "assets", "rysunki.js"), "w", encoding="utf-8").write(js)
    n_et = sum(1 for v in R.values() if v["src"].startswith("etykieta"))
    print("Rysunki: %d indeksów (%d z etykiet, %d z paczki), plików: %d" % (len(R), n_et, len(R) - n_et, len(cache)))
    print("Bez rysunku (%d):" % len(braki))
    for b in braki:
        print("  ", b)


# ---------- 4. packshoty — poprawki do data.js ----------
# Frigo szary kamień miał w data.js packshot białego kamienia (plik „szary” z paczki był rysunkiem technicznym).
# Źródło: najpierw packshot konkretnego indeksu (folder PACKSHOTY, plik Product-<EAN>-P.png),
# potem packshot kształtu z GOTOWE PACZKI (szary kamień).
FRIGO_GS = E("FRIGO - sensea", "FRIGO SZARY KAMIEŃ")
GS_SHAPE = {"kwadratowy": "KWADRAT", "prostokątny": "PROSTOKĄT", "półokrągły": "PÓŁOKRĄGŁY", "pięciokątny": "PIĘCIOKĄT"}


def pack_save(src, key, out_dir, maxpx=760, crop=True):
    """Zapis do webp. Zwraca (w, h, tb) — tb = przezroczyste tło."""
    im = Image.open(src).convert("RGBA")
    a = im.getchannel("A")
    tb = a.getextrema()[0] < 250
    if crop:
        box = a.point(lambda v: 255 if v > 8 else 0).getbbox() if tb else \
            ImageOps.invert(im.convert("L")).point(lambda v: 255 if v > 12 else 0).getbbox()
        if box:
            pad = 0 if tb else int(max(im.size) * 0.03)
            im = im.crop((max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad)))
    im.thumbnail((maxpx, maxpx), Image.LANCZOS)
    if not tb:
        im = im.convert("RGB")
    im.save(os.path.join(out_dir, key + ".webp"), "WEBP", quality=86, method=6)
    return im.size[0], im.size[1], tb


# Balans: packshot wg koloru i kształtu + zdjęcia dodatkowe z paczki. Infografiki i przekrój pominięte celowo:
# zawierają Antibac, „50% CO₂” z liściem, „ekstremalną wytrzymałość”, ochronę przed pleśnią (czarna lista EmpCo).
BAL_COL = {"biały kamień": ("BIAŁY KAMIEŃ", "ws"), "czarny kamień": ("CZARNY KAMIEŃ", "bs"),
           "szary kamień": ("SZARY KAMIEŃ", "gs"), "kaszmirowy kamień": ("KASZMIROWY KAMIEŃ", "cas")}
BAL_SH = {"kwadratowy": ("KWADRAT", "kw"), "prostokątny": ("PROSTOKĄT", "pr")}
EXTRA_SKIP = re.compile(r"infografik|przekr|zalety", re.I)


def extra_cap(name):
    n = name.lower()
    if "zoom" in n: return "Zbliżenie powierzchni"
    if "tekstur" in n: return "Struktura powierzchni"
    if "balans 300 dpi" in n: return "Linie docinania · wizualizacja poglądowa"
    return None


def balans(P, out_dir, img, ref_im, extra, log):
    base = E("BALANS")
    groups = {}
    for p in P:
        if p["fam"] == "Balans" and p.get("c") in BAL_COL and p.get("shape") in BAL_SH:
            groups.setdefault((p["c"], p["shape"]), []).append(p["ref"])
    for (c, sh), refs in sorted(groups.items()):
        cname, ccode = BAL_COL[c]
        sname, scode = BAL_SH[sh]
        d = glob.glob(os.path.join(base, "BALANS " + cname, "GOTOWE PACZKI*", "BALANS %s %s" % (cname, sname)))
        if not d:
            log.append(("Balans", c, sh, "brak folderu")); continue
        d = d[0]
        packs = [f for f in glob.glob(os.path.join(d, "*PACKSHOT*", "*")) if f.lower().endswith((".png", ".jpg"))]
        pngs = sorted([f for f in packs if f.lower().endswith(".png")], key=lambda f: ("#" in os.path.basename(f), os.path.basename(f)))
        pngs = pngs or sorted(packs)
        # biały prostokąt: ujęcie #1 ma narysowane linie cięcia — główny packshot to #2, a #1 pomijamy (jest zdjęcie „Linie docinania”)
        if (ccode, scode) == ("ws", "pr"):
            pngs = [f for f in pngs if "#2" in f] + [f for f in pngs if "#2" not in f and "#1" not in f]
        main, alts = pngs[0], pngs[1:]
        key = "p-balans-%s-%s" % (ccode, scode)
        w, h, tb = pack_save(main, key, out_dir)
        img[key] = {"f": key + ".webp", "w": w, "h": h, "tb": tb, "k": "pack"}
        items, n = [], 2
        for f in alts:
            if n > 3:
                break
            k = "%s-%d" % (key, n)
            w, h, tb = pack_save(f, k, out_dir)
            if scode == "kw" and h > w * 1.1:              # w folderach KWADRAT są widoki z góry prostokąta — pomijamy
                os.remove(os.path.join(out_dir, k + ".webp"))
                log.append(("Balans", c, sh, "pominięto widok prostokąta: " + os.path.basename(f)))
                continue
            img[k] = {"f": k + ".webp", "w": w, "h": h, "tb": tb, "k": "pack"}
            items.append({"k": k, "kind": "pack", "cap": "Packshot · inne ujęcie"})
            n += 1
        exf = [f for f in glob.glob(os.path.join(d, "*odatkowe*", "*")) + glob.glob(os.path.join(d, "*ODATKOWE*", "*"))
               if f.lower().endswith((".png", ".jpg")) and not EXTRA_SKIP.search(os.path.basename(f))]
        for f in sorted(set(exf)):
            cap = extra_cap(os.path.basename(f))
            if not cap:
                log.append(("Balans", c, sh, "pominięto " + os.path.basename(f))); continue
            k = "x-balans-%s-%s-%s" % (ccode, scode, re.sub(r"[^a-z]+", "", cap.lower())[:10])
            w, h, tb = pack_save(f, k, out_dir, maxpx=1200, crop=False)
            img[k] = {"f": k + ".webp", "w": w, "h": h, "tb": tb, "k": "extra"}
            items.append({"k": k, "kind": "extra", "cap": cap})
        for r in refs:
            ref_im[r] = key
            extra[r] = items
        log.append(("Balans", c, sh, key, len(refs), [x["cap"] for x in items]))


# ---------- 4b. packshoty dla wszystkich serii ----------
# --- kolor i kształt wg nazwy w systemie LM (kody na końcu nazwy) ---
LM_COL = [(r"CZMAT$", "czarny mat"), (r"(?:BSTR|BST|BS)$", "biały kamień"), (r"(?:CSTR|CZST|CZS|CZA|CS)$", "czarny kamień"),
          (r"SZ$", "szary kamień"), (r"(?:CEM|CE)$", "cementowy kamień"), (r"(?:BIA|B)$", "biały gładki")]
LM_SHAPE = [(r"\b5K[AĄ]T\b", "pięciokątny"), (r"(?:\b1/4K\b|\b14K\b|\bPÓŁ\b|\bPOL\b)", "półokrągły"), (r"\bKW\b", "kwadratowy"), (r"\bPR\b", "prostokątny")]
LM_SHAPE_SKIP = {"95495956"}                                # „BALANS KW 120X90” — błąd w nazwie LM
COLOR_FAMS = {"Frigo", "Ipsilon", "Magnetic", "Sinergid", "Integral"}


def lm_color(name):
    last = (name or "").split()[-1] if name else ""
    last = re.sub(r"^.*?(\d)(?=[A-Z])", "", last)        # „80X80X5/3BIA” → „BIA”
    for rx, c in LM_COL:
        if re.search(rx, last):
            return c
    return None


def lm_shape(ref, name):
    if ref in LM_SHAPE_SKIP:
        return None
    for rx, s in LM_SHAPE:
        if re.search(rx, (name or "").upper()):
            return s
    return None


def _norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn").replace("ł", "l")


COL_TOK = {"biały gładki": ["bialy gladki", "smooth white"], "biały kamień": ["bialy kamien", "biala struktura", "white stone"],
           "czarny kamień": ["czarny kamien", "czarny strukturalny", "black stone"], "szary kamień": ["szary kamien", "4. szary", "grey stone", "greystone"],
           "czarny mat": ["czarny mat", "black mat"], "biały mat": ["bialy mat"], "kaszmirowy kamień": ["kaszmirowy"]}
SHP_TOK = {"kwadratowy": ["kwadrat", "kwdrat"], "prostokątny": ["prostokat", "prosotkat"], "półokrągły": ["polokragl", "polokrag"],
           "pięciokątny": ["pieciokat", "piecioka"]}
FAM_DIR = {"Sinergid": "SINEGRID", "Frigo": "FRIGO - sensea", "Wall Comfort": "ŚCIANKA", "Harmony": "ODPŁYWY LINIOWE"}


def pack_dirs():
    out = []
    for root, dirs, files in os.walk(ECOM):
        n = _norm(root)
        if "pack" in _norm(os.path.basename(root)) and "surow" not in n and "nie edyt" not in n and "frigo - sensea\\frigo\\" not in n:
            imgs = [os.path.join(root, f) for f in files if f.lower().endswith((".png", ".jpg"))]
            if imgs:
                out.append((n, root, imgs))
    return out


def pick_main(imgs):
    imgs = [f for f in imgs if not re.search(r"rys|tech|product-", _norm(os.path.basename(f)))]
    png = sorted([f for f in imgs if f.lower().endswith(".png")], key=lambda f: ("#" in os.path.basename(f), os.path.basename(f)))
    jpg = sorted([f for f in imgs if f.lower().endswith(".jpg")], key=lambda f: ("#" in os.path.basename(f), os.path.basename(f)))
    return (png + jpg)[:1]


def resolve_dir(p, color, shape, DIRS):
    fam = FAM_DIR.get(p["fam"], p["fam"].upper())
    cands = [d for d in DIRS if ("\\" + _norm(fam) + "\\") in d[0] + "\\"]
    if p["fam"] == "Wall Comfort":
        cands = [d for d in cands if ("thick" in d[0]) == (str(p.get("h")) == "6")]
    if p["fam"] == "Harmony":
        want = "harmony" + (" prime" if "Prime" in p["s"] else "") + (" black" if p.get("c") == "czarny" else "")
        cands = [d for d in cands if d[0].split("\\odplywy liniowe\\")[-1].split("\\")[0] == want]
    if p["fam"] == "Panele do brodzików":
        cands = [d for d in DIRS if "panele do brodzikow" in d[0] and _norm(p["s"].replace("Panel ", "")) in d[0]]
    if color and color in COL_TOK and p["fam"] not in ("Harmony",):
        c2 = [d for d in cands if any(t in d[0] for t in COL_TOK[color])]
        if c2 or p["fam"] in COLOR_FAMS or p["fam"] in ("Wall Comfort", "Torres", "Tebe"):
            cands = c2
    if shape and shape in SHP_TOK:
        s2 = [d for d in cands if any(t in d[0] for t in SHP_TOK[shape])]
        if s2 or any(any(t in d[0] for t in sum(SHP_TOK.values(), [])) for d in cands):
            cands = s2
    cands = [d for d in cands if "gotowe paczki" in d[0]] or cands  # Frigo: foldery GOTOWE PACZKI zamiast luźnych
    return cands[0] if len(cands) >= 1 else None


SKIP_FAMS = {"Balans", "Nośnik", "Obudowa uniwersalna", "Najazd", "Nogi Ipsilon", "Maskownica Balans/Integral"}  # Balans osobno; reszta bez zmian


def packshoty(P, L):
    out_dir = os.path.join(ROOT, "assets", "img")
    img, ref_im, extra, log, fix = {}, {}, {}, [], {}
    DIRS = pack_dirs()
    by_ean = {}
    for n, root, imgs in DIRS:
        for f in imgs:
            m = re.search(r"Product-(\d+)-P\.png$", f)
            if m:
                by_ean[m.group(1)] = f
    for root, _, files in os.walk(os.path.join(ECOM, "FRIGO - sensea")):
        for f in files:
            m = re.search(r"Product-(\d+)-P\.png$", f)
            if m and "surow" not in _norm(root):
                by_ean.setdefault(m.group(1), os.path.join(root, f))
    for p in P:
        x = L.get(p["ref"]) or {}
        name = x.get("n", "")
        color = (lm_color(name) if p["fam"] in COLOR_FAMS else None) or p.get("c")
        shape = lm_shape(p["ref"], name) or SHAPE_FIX.get(p["ref"], p.get("shape"))
        f = {}
        if p["fam"] in COLOR_FAMS and color and color != p.get("c"):
            f["c"] = color
        if shape and shape != p.get("shape") and p.get("shape"):
            f["shape"] = shape
        if f:
            fix[p["ref"]] = f
        if p["fam"] in SKIP_FAMS or (color or "").startswith("cementowy"):
            continue                                        # cementowy kamień: brak packshotu w paczce — zostaje dotychczasowy
        ean = x.get("ean", "")
        if ean in by_ean:
            src, key = by_ean[ean], "pk-" + ean
        else:
            d = resolve_dir(p, color, shape, DIRS)
            m = pick_main(d[2]) if d else []
            if not m:
                log.append((p["ref"], p["fam"], color, shape, "BRAK packshotu w paczce")); continue
            src = m[0]
            import hashlib                                  # skrót pełnej ścieżki: ta sama nazwa pliku bywa w kilku folderach
            key = "pk-" + re.sub(r"[^a-z0-9]+", "-", _norm(os.path.basename(src)))[:40].strip("-") + "-" + hashlib.md5(src.encode("utf-8")).hexdigest()[:6]
        if key not in img:
            w, h, tb = pack_save(src, key, out_dir)
            img[key] = {"f": key + ".webp", "w": w, "h": h, "tb": tb, "k": "pack", "src": os.path.relpath(src, ECOM)}
        ref_im[p["ref"]] = key
        log.append((p["ref"], p["fam"], color, shape, key))
    balans(P, out_dir, img, ref_im, extra, log)
    js = ("/* Wygenerowano (8_zasoby_kart.py): packshot każdego indeksu wg serii, koloru i kształtu z paczki e-commerce\n"
          "   (kolor i kształt wg nazwy w systemie LM), zdjęcia dodatkowe Balans (SP.extra: nr ref. → [{k, kind, cap}]). */\n"
          "(function (SP) {\n  var IMG = " + json.dumps(img, ensure_ascii=False) + ";\n  var IM = " + json.dumps(ref_im) + ";\n"
          "  var EX = " + json.dumps(extra, ensure_ascii=False) + ";\n"
          "  var FIX = " + json.dumps(fix, ensure_ascii=False) + ";\n"
          "  var SURF = {}; (SP.surfaces || []).forEach(function (x) { SURF[x.pl] = x; });\n"
          "  Object.keys(IMG).forEach(function (k) { SP.img[k] = IMG[k]; });\n"
          "  SP.extra = EX;\n"
          "  SP.products.forEach(function (p) {\n"
          "    if (IM[p.ref]) p.im = IM[p.ref];\n"
          "    var f = FIX[p.ref];\n"
          "    if (f) { if (f.shape) p.shape = f.shape; if (f.c) { p.c = f.c; var su = SURF[f.c]; if (su) { p.hx = su.hx; p.ral = su.ral; p.ce = su.n; } } }\n"
          "  });\n"
          "})(window.SP);\n")
    io.open(os.path.join(ROOT, "assets", "packshoty.js"), "w", encoding="utf-8").write(js)
    print("Poprawki packshotów: %d indeksów, %d nowych plików" % (len(ref_im), len(img)))
    for x in log:
        print("  ", x)


# ---------- 5. karty gwarancyjne i instrukcje montażu ----------
DOCS_DIR = os.path.join(MAT, "Instrukcje i Karty")
# klucz: (plik źródłowy, nazwa publikowana, tytuł, typ)
DOCS = {
    "gw-stabilsafe": ("00. Karta Gwarancyjna_Stabilsafe_v15.25 (8str A3) 16.06.2025.pdf", "Karta-gwarancyjna_Stabilsafe_v15.25.pdf", "Karta gwarancyjna Stabilsafe v15.25", "gw"),
    "no01": ("01. Brodziki_StabPlus_instr_mont_No01 v09.2024 A4.pdf", "Instrukcja-montazu_No01_brodziki-kompozytowe_v09.2024.pdf", "Instrukcja montażu No01 — brodziki kompozytowe", "in"),
    "no02": ("02. Brodziki_Stabilsound_instr_mont_No02_v06.2023 A4.pdf", "Instrukcja-montazu_No02_brodziki-zintegrowane_v06.2023.pdf", "Instrukcja montażu No02 — brodziki zintegrowane", "in"),
    "no03": ("03. Brodziki_standard_Instrukcja_No03 v06.2023 A4.pdf", "Instrukcja-montazu_No03_brodziki-standard_v06.2023.pdf", "Instrukcja montażu No03 — brodziki laminowane", "in"),
    "no04": ("04. Obudowy_podpłytkowe_Instrukcja_No4 v11.2023.pdf", "Instrukcja-montazu_No04_obudowy-podplytkowe_v11.2023.pdf", "Instrukcja montażu No04 — obudowy podpłytkowe", "in"),
    "no05": ("05.Odplywy_liniowe_instr_mont_No05_v07.2024.pdf", "Instrukcja-montazu_No05_odplywy-liniowe_v07.2024.pdf", "Instrukcja montażu No05 — odpływy liniowe", "in"),
    "no07": ("07. Schedpol_Wanny_instr_No07v12.2025.pdf", "Instrukcja-montazu_No07_wanny_v12.2025.pdf", "Instrukcja montażu No07 — wanny", "in"),
    "no08": ("08. Nośnik_do_wanien_No08 v14.2023.pdf", "Instrukcja-montazu_No08_nosnik-do-wanien_v14.2023.pdf", "Instrukcja montażu No08 — nośnik do wanien", "in"),
    "no12": ("12. Instrukcja montażu Wall_comfort No12 v11.2023.pdf", "Instrukcja-montazu_No12_Wall-Comfort_v11.2023.pdf", "Instrukcja montażu No12 — Wall Comfort", "in"),
    "no27": ("27. Instrukcja Najazd Schedpol No27v2025.pdf", "Instrukcja-montazu_No27_najazd_v2025.pdf", "Instrukcja montażu No27 — najazd do brodzików", "in"),
    "comfo": ("Brodziki_Comfo_2022.pdf", "Instrukcja-montazu_Comfo_2022.pdf", "Instrukcja montażu — brodziki Comfo", "in"),
    "frigo": ("FRIGO_Sensea_v3.2022.pdf", "Instrukcja-montazu_Frigo-Sensea_v3.2022.pdf", "Instrukcja montażu — Frigo Sensea", "in"),
    "ipsilon": ("Ipsilon_Sensea_2024_v5 - Druk A4.pdf", "Instrukcja-montazu_Ipsilon-Sensea_2024_v5.pdf", "Instrukcja montażu — Ipsilon Sensea", "in"),
    "ob1040": ("Obudowa podpłytkowa 1.040 (2018).pdf", "Instrukcja-montazu_obudowa-podplytkowa-1.040_2018.pdf", "Instrukcja montażu — obudowa podpłytkowa 1.040", "in"),
    "no03a": ("03A. Brodzik standard + nośnik No03A v02.2023 A4 DE.pdf", "Instrukcja-montazu_No03A_brodzik-standard-z-nosnikiem_v02.2023.pdf", "Instrukcja montażu No03A — brodzik standard z nośnikiem", "in"),
    "no05c": ("05C.Odplywy_liniowe_Winyl_instr_mont_No05A_v01.2026(1).pdf", "Instrukcja-montazu_No05C_odplywy-liniowe-posadzka-winylowa_v01.2026.pdf", "Instrukcja montażu No05C — odpływy liniowe, posadzka winylowa", "in"),
    "gw-stabilsound": ("00. Karta Gwarancyjna_Stabilsound_v14.2025_(8str A3)-all.pdf", "Karta-gwarancyjna_Stabilsound_v14.2025.pdf", "Karta gwarancyjna Stabilsound v14.2025 — marka katalogowa Schedpol, nie dotyczy indeksów LM", "gw"),
}
# instrukcje wg serii (pierwsza = podstawowa, kolejne = warianty montażu)
DOC_FAM = {"Balans": ["no01"], "Magnetic": ["no01"], "Sinergid": ["no02"], "Integral": ["no02"], "Consist": ["no02"], "Grawello": ["no02"],
           "Dante": ["no02"], "Go Baby": ["no02"], "Panele do brodzików": ["no02"], "Tebe": ["no03", "no03a"], "Corrina": ["no03", "no03a"],
           "Dafne": ["no03", "no03a"], "Comfo": ["comfo", "no03a"], "Frigo": ["frigo"], "Ipsilon": ["ipsilon"], "Nogi Ipsilon": ["ipsilon"],
           "Harmony": ["no05", "no05c"], "Torres": ["no07"], "Nośnik": ["no08"], "Wall Comfort": ["no12"], "Najazd": ["no27"]}
DOC_REF = {"90151710": ["no04"], "90151711": ["no04"], "43416086": ["ob1040"], "43732703": ["ob1040"]}   # obudowy LED vs 1040/1.041
DOC_NOT_LM = {"gw-stabilsound"}            # w bibliotece dokumentów, ale nie przypisywane do indeksów LM (kanał DIY = Stabilsafe)


def dokumenty(P):
    out = os.path.join(ROOT, "assets", "dokumenty")
    os.makedirs(out, exist_ok=True)
    D, M = {}, {}
    for k, (src, dst, title, typ) in DOCS.items():
        s = os.path.join(DOCS_DIR, src)
        shutil.copy2(s, os.path.join(out, dst))
        d = fitz.open(s)
        D[k] = {"f": dst, "t": title, "typ": typ, "mb": round(os.path.getsize(s) / 1048576, 1), "str": d.page_count}
    fams = {k: [] for k in D}
    for p in P:
        ins = DOC_REF.get(p["ref"]) or DOC_FAM.get(p["fam"]) or []
        M[p["ref"]] = list(ins) + ["gw-stabilsafe"]
        for k in M[p["ref"]]:
            if p["fam"] not in fams[k]:
                fams[k].append(p["fam"])
    for k in D:
        D[k]["fams"] = fams[k]
        D[k]["lm"] = k not in DOC_NOT_LM
    js = ("/* Wygenerowano (8_zasoby_kart.py): karty gwarancyjne i instrukcje montażu przypisane do indeksów.\n"
          "   Źródło: materiały/Instrukcje i Karty. SP.docs: klucz → plik (+ fams: serie, lm: czy dotyczy indeksów LM);\n"
          "   SP.docMap: nr ref. → [klucze]. */\n"
          "window.SP.docs = " + json.dumps(D, ensure_ascii=False) + ";\nwindow.SP.docMap = " + json.dumps(M) + ";\n")
    io.open(os.path.join(ROOT, "assets", "dokumenty.js"), "w", encoding="utf-8").write(js)
    bez = [p["ref"] + " " + p["fam"] for p in P if len(M[p["ref"]]) == 1]
    print("Dokumenty: %d plików, %.1f MB; indeksów z instrukcją: %d, bez instrukcji: %s" %
          (len(D), sum(v["mb"] for v in D.values()), len(P) - len(bez), bez))
    znane = {v[0] for v in DOCS.values()}
    nowe = [f for f in os.listdir(DOCS_DIR) if f.lower().endswith(".pdf") and f not in znane]
    print("UWAGA — pliki w folderze bez przypisania (dopisz do DOCS):" if nowe else "Wszystkie PDF z folderu są w bazie.", nowe or "")


if __name__ == "__main__":
    P = products()
    L = lm_export(P)
    znaki()
    rysunki(P, L)
    packshoty(P, L)
    dokumenty(P)

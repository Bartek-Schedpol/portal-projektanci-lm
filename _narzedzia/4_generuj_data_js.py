# -*- coding: utf-8 -*-
"""Generuje koncepcja-portalu/assets/data.js — wspólne dane dla trzech makiet."""
import os, sys, io, json, re, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
SP = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = ROOT + r"\koncepcja-portalu\assets"
prods = json.load(open(SP + "/data_products.json", encoding="utf-8"))
man = json.load(open(OUT + r"\img-manifest.json", encoding="utf-8"))

# ---------- obraz dla wariantu ----------
def has(o, *subs):
    return any(s in (o["c"] or "") for s in subs)

def img_for(o):
    s, sh = o["s"], o["shape"]
    if s == "Balans":
        if has(o, "czarny"): return "p-balans-bs"
        if has(o, "kaszmir"): return "p-balans-cas"
        if has(o, "szary"): return "p-balans-gs"
        return "p-balans-ws-rect" if sh == "prostokątny" else "p-balans-ws"
    if s == "Magnetic":
        if has(o, "czarny"): return "p-magnetic-bs"
        if has(o, "szary"): return "p-magnetic-gs"
        if has(o, "biały kamień"): return "p-magnetic-ws"
        return "p-magnetic-r55" if sh == "półokrągły" else "p-magnetic-sw"
    if s == "Ipsilon":
        if has(o, "czarny"): return "p-ipsilon-bs"
        if has(o, "szary", "cement"): return "p-ipsilon-gs"
        if has(o, "biały kamień"): return "p-ipsilon-ws"
        return {"półokrągły": "p-ipsilon-r55", "pięciokątny": "p-ipsilon-5", "prostokątny": "p-ipsilon-rect"}.get(sh, "p-ipsilon-sw")
    if s == "Frigo":
        if has(o, "czarny"): return "p-frigo-bs"
        if has(o, "biały kamień", "szary", "cement"): return "p-frigo-ws"
        return "p-frigo-sw"
    if s == "Sinergid":
        if has(o, "czarny"): return "p-sinegrid-bm"
        if has(o, "kamień"): return "p-sinegrid-ws"
        return "p-sinegrid-sw"
    if s == "Integral": return "p-integral-bs" if has(o, "czarny") else "p-integral-ws"
    if s == "Torres": return "p-torres-b" if has(o, "czarny") else "p-torres-w"
    if s == "Wall Comfort":
        if has(o, "czarny"): return "p-wall-bs"
        if has(o, "szary"): return "p-wall-gs"
        if has(o, "biały kamień"): return "p-wall-ws"
        return "p-wall6-sw" if str(o["h"]) == "6" else "p-wall-sw"
    if s == "Nośnik":                       # trzy różne produkty (paczka e-commerce: NOŚNIK DO WANNY 1.1 / 1.2 / 2.)
        t = (o.get("t") or "").lower()
        if "półokr" in t or "polokr" in t or "1/4" in t: return "p-nosnik-polokr"
        if "61/48" in t or "podcię" in t: return "p-nosnik-wanna"
        return "p-nosnik-prost"
    if s == "Obudowa uniwersalna":          # 4 indeksy: prostokątna/półokrągła × z podcięciem (LED, 2023) / bez podcięcia
        return {"90151710": "p-obudowa", "90151711": "p-obudowa-pol-led", "43416086": "p-obudowa-pol", "43732703": "p-obudowa-pr"}.get(o["ref"], "p-obudowa")
    if s == "Maskownica Balans/Integral":
        return "p-maskownica-szczot" if has(o, "szczotk") else "p-maskownica-miedz" if has(o, "miedz") else "p-maskownica-zlota"
    if s.startswith("Panel"): return "p-panel-dante" if s in ("Panel Dante", "Panel Grawello") else "p-panel-gobaby"
    m = {"Consist": "p-consist", "Comfo": "p-comfo", "Corrina": "p-corrina", "Dafne": "p-dafne", "Dante": "p-dante",
         "Go Baby": "p-gobaby", "Grawello": "p-grawello", "Tebe": "p-tebe", "Najazd": "p-najazd", "Nogi Ipsilon": "p-nogi",
         "Harmony": "p-harmony", "Harmony Black": "p-harmony-black", "Harmony Prime": "p-harmony-prime",
         "Harmony Prime Black": "p-harmony-prime-black"}
    return m.get(s, "p-balans-ws")

NEW = {"Consist", "Sinergid", "Tebe", "Harmony", "Harmony Black", "Harmony Prime", "Harmony Prime Black", "Najazd",
       "Maskownica Balans/Integral"}

P = []
for o in prods:
    fam = "Harmony" if o["s"].startswith("Harmony") else "Panele do brodzików" if o["s"].startswith("Panel") else o["s"]
    isnew = o["s"] in NEW or (o["s"] == "Balans" and has(o, "kaszmir"))
    hv = o["h"]
    P.append({"ref": o["ref"], "s": o["s"], "fam": fam, "cat": o["cat"], "tech": o["tech"], "tn": o["tn"], "brand": o["brand"],
              "shape": o["shape"], "a": o["a"], "b": o["b"], "h": hv, "c": o["c"], "ce": o["ce"], "ral": o["ral"], "hx": o["hx"],
              "g": o["g"], "new": isnew, "im": img_for(o), "t": o["t"]})
    if o["s"] == "Obudowa uniwersalna":         # wersja wg nazwy LM: „… LED” = z podcięciem na stopy; „ZABUDOWA ELAST” = bez
        P[-1]["ver"] = "z podcięciem na stopy (LED)" if o["ref"] in ("90151710", "90151711") else "bez podcięcia na stopy"
        if o["ref"] == "43732703": P[-1].update(a=170, b=90, h="58")   # tytuł LM: 170+90x58

# ---------- serie ----------
G10 = ("Gwarancja producenta: 10 lat na wytrzymałość na nacisk wg PN-EN 14527 oraz 5 lat na stałość barwy. "
       "Warunek: montaż zgodnie z instrukcją, przez osobę o odpowiednich kwalifikacjach. Zakres i terytorium — "
       "karta gwarancyjna Stabilsafe v15.25. Gwarancja nie ogranicza ustawowych praw kupującego.")
GSP = ("Gwarancja producenta wg karty gwarancyjnej Stabilsafe v15.25 (technologia Standard Plus). "
       "Warunek: montaż zgodnie z instrukcją, przez osobę o odpowiednich kwalifikacjach. "
       "Gwarancja nie ogranicza ustawowych praw kupującego.")
GEPS = ("Gwarancja producenta: 31 lat na trwałość materiału nośnika EPS. Zakres i warunki — karta gwarancyjna "
        "Stabilsafe v15.25. Gwarancja nie ogranicza ustawowych praw kupującego.")
GGEN = "Gwarancja producenta wg karty gwarancyjnej Stabilsafe v15.25. Gwarancja nie ogranicza ustawowych praw kupującego."

F_KOMP = ["Możliwy montaż na posadzce lub zlicowany z posadzką.",
          "Możliwość docięcia brodzika ułatwia dopasowanie do nietypowych wnęk.",
          "Hydroszczelna warstwa ogranicza przenikanie wilgoci do wnętrza konstrukcji.",
          "Właściwości powierzchni ograniczają przyleganie zabrudzeń — brodzik łatwo utrzymać w czystości."]
F_KOMP2 = ["Możliwy montaż na posadzce lub zlicowany z posadzką.",
           "Hydroszczelna warstwa ogranicza przenikanie wilgoci do wnętrza konstrukcji.",
           "Właściwości powierzchni ograniczają przyleganie zabrudzeń — brodzik łatwo utrzymać w czystości."]
F_ZINT = ["Podparcie na całej powierzchni brodzika zapewnia jego stabilność.",
          "Wielowarstwowa konstrukcja wspiera izolację termiczną i akustyczną.",
          "Syfon i podejście kanalizacyjne mieszczą się w konstrukcji brodzika.",
          "Właściwości powierzchni ograniczają przyleganie zabrudzeń — brodzik łatwo utrzymać w czystości."]
F_LAM = ["Wzmocnione dno zwiększa sztywność konstrukcji: 2 warstwy laminatu żywicznego i płyta drewnopochodna.",
         "Możliwy montaż na posadzce lub zlicowany z posadzką.",
         "Właściwości powierzchni ograniczają przyleganie zabrudzeń — brodzik łatwo utrzymać w czystości."]

SER = [
 # fam, kategoria, typ, lead, sceny, cechy, gwarancja
 ("Balans", "brodzik", "Brodzik kompozytowy · Stabilsafe®",
  "Płaski brodzik kompozytowy o strukturze kamienia. Wysokość 3,5–4 cm, do docięcia na wymiar wnęki.",
  ["balans-ws-a", "balans-bs-a", "balans-cas", "balans-gs", "balans-ws-b", "balans-zoom-ws", "balans-cut"], F_KOMP, G10),
 ("Magnetic", "brodzik", "Brodzik kompozytowy · Stabilsafe®",
  "Brodzik kompozytowy o wysokości 5 cm — w wersji gładkiej oraz o strukturze kamienia.", [], F_KOMP2, G10),
 ("Ipsilon", "brodzik", "Brodzik laminowany · Standard Plus",
  "Brodzik laminowany o wysokości 5 cm. Cztery kształty, w tym pięciokątny; powierzchnia gładka lub o strukturze kamienia.",
  ["ipsilon-sw", "ipsilon-bs"], F_LAM, GSP),
 ("Frigo", "brodzik", "Brodzik zintegrowany · Stabilsafe®",
  "Brodzik zintegrowany z nośnikiem, wysokość 12 cm. Cztery kształty i cztery wykończenia powierzchni.",
  ["frigo-sw", "frigo-bs"], F_ZINT, G10),
 ("Sinergid", "brodzik", "Brodzik zintegrowany · Stabilsafe®",
  "Brodzik zintegrowany o wysokości 16 cm, w trzech wykończeniach: biały gładki, biały kamień, czarny mat.", [], F_ZINT, G10),
 ("Integral", "brodzik", "Brodzik zintegrowany · Stabilsafe®",
  "Brodzik zintegrowany o strukturze kamienia, wysokość 12 cm. Biały lub czarny kamień.",
  ["integral-bs", "integral-ws"], F_ZINT, G10),
 ("Consist", "brodzik", "Brodzik zintegrowany · Stabilsafe®",
  "Brodzik zintegrowany w kolorze białym gładkim — kwadratowy 90 × 90 i prostokątny 80 × 100 cm.",
  ["consist", "consist-rect"], F_ZINT, G10),
 ("Tebe", "brodzik", "Brodzik laminowany · Standard Plus",
  "Brodzik w wykończeniu czarny mat, wysokość 4,5 cm. Kwadratowy i półokrągły, 80 i 90 cm.", ["tebe"], F_LAM, GSP),
 ("Corrina", "brodzik", "Brodzik laminowany · Standard Plus",
  "Brodzik laminowany kwadratowy 100 × 100 cm, wysokość 5,5 cm.", ["corrina"], F_LAM, GSP),
 ("Comfo", "brodzik", "Brodzik laminowany · Standard Plus",
  "Brodzik laminowany z ryflowanym dnem, wysokość 16 cm.", ["comfo"], F_LAM, GSP),
 ("Grawello", "brodzik", "Brodzik głęboki zintegrowany · Stabilsafe®",
  "Brodzik głęboki — kwadratowy, półokrągły i prostokątny. Do wersji półokrągłej dostępny panel.", ["grawello"], F_ZINT, G10),
 ("Dante", "brodzik", "Brodzik głęboki zintegrowany · Stabilsafe®",
  "Brodzik głęboki z siedziskiem, 80 i 90 cm. Do wersji półokrągłej dostępny panel.", ["dante"], F_ZINT, G10),
 ("Go Baby", "brodzik", "Brodzik głęboki zintegrowany · Stabilsafe®",
  "Brodzik głęboki półokrągły 80 i 90 cm, z dedykowanym panelem.", ["gobaby"], F_ZINT, G10),
 ("Dafne", "brodzik", "Brodzik głęboki laminowany · Standard Plus",
  "Brodzik głęboki półokrągły 80 i 90 cm, z dedykowanym panelem.", ["dafne"], F_LAM, GSP),
 ("Torres", "wanna", "Wanna laminowana · Standard Plus",
  "Wanna prostokątna 140–170 × 70 cm w wykończeniu biały mat lub czarny mat.", ["torres-w", "torres-b"],
  ["Wykończenie matowe: biały mat i czarny mat.", "Wąski rant o szerokości 2 cm.", "Wzmocnienia rantów."], GSP),
 ("Harmony", "odpływ liniowy", "Odpływ liniowy",
  "Odpływy liniowe 60–90 cm. Maskownica 2w1 (gładka lub do zabudowy płytkami) albo Steel Black.",
  ["odplyw-scena", "odplyw-detal", "odplyw-black", "odplyw-prime"],
  ["Długości 60, 70, 80 i 90 cm.", "Maskownica 2w1: gładka lub do zabudowy płytkami.",
   "Regulacja położenia w pionie i poziomie."], GGEN),
 ("Wall Comfort", "panel ścienny", "Dekoracyjny panel ścienny",
  "Wielkoformatowy panel 210 × 100 cm w grubości 1 lub 6 cm. Montaż na klej, bez skuwania płytek.",
  ["wc-po", "wc-przed"],
  ["Duży format 210 × 100 cm ogranicza liczbę łączeń.", "Dwie grubości: 1 cm oraz 6 cm — wariant 6 cm pozwala ukryć instalację.",
   "Panele można docinać i montować na klej.", "Cztery wykończenia, w tym o strukturze kamienia."], GGEN),
 ("Nośnik", "nośnik", "Nośnik EPS do wanien",
  "Nośnik do wanien prostokątnych 120–170 cm (także w wersji z podcięciem na stopy / LED) i półokrągłych.",
  ["nosnik"], ["Podparcie wanny na całej powierzchni.", "Możliwość bezpośredniego oklejenia płytkami.",
               "Łączone elementy pozwalają dopasować nośnik do rozmiaru wanny."], GEPS),
 ("Obudowa uniwersalna", "obudowa", "Obudowa do wanien",
  "Obudowa podpłytkowa do wanien prostokątnych i półokrągłych, do oklejenia płytkami. Dwie wersje: z podcięciem na stopy (wnęka przy posadzce, miejsce na taśmę LED) albo bez podcięcia — panele do samej posadzki.",
  ["obudowa-led", "obudowa-pol", "obudowa-pr", "obudowa-pol-bez"], ["Do wanien akrylowych i stalowych.", "Możliwość bezpośredniego oklejenia płytkami.",
                                    "Montaż z możliwością późniejszego demontażu."], GGEN),
 ("Maskownica Balans/Integral", "akcesoria", "Maskownica odpływu",
  "Maskownice do brodzików Balans i Integral: złota polerowana, złota szczotkowana i miedziana.", [], [], GGEN),
 ("Panele do brodzików", "akcesoria", "Panel do brodzika głębokiego",
  "Panele do brodzików półokrągłych Grawello, Dante, Go Baby i Dafne.", [], [], GGEN),
 ("Najazd", "akcesoria", "Najazd do brodzików",
  "Najazd 78 lub 104 cm ułatwia wejście do brodzika osobom o ograniczonej sprawności ruchowej.", ["najazd-b", "najazd-a"], [], GGEN),
 ("Nogi Ipsilon", "akcesoria", "Zestaw nóg",
  "Zestaw nóg do brodzików Ipsilon: 5 nóżek i 4 kotwy przyścienne.", [], [], GGEN),
]

# ---------- inwentaryzacja plików z folderu materiałów ----------
FOLD = {"BALANS": "Balans", "COMFO": "Comfo", "CONSIST": "Consist", "CORRINA": "Corrina", "DAFNE": "Dafne", "DANTE": "Dante",
        "FRIGO - sensea": "Frigo", "FRIGO": "Frigo", "GO BABY": "Go Baby", "GRAWELLO": "Grawello", "INTEGRAL": "Integral",
        "IPSILON": "Ipsilon", "MAGNETIC": "Magnetic", "MASKOWNICE DO BRODZIKÓW BALANSINTEGRAL": "Maskownica Balans/Integral",
        "NAJAZD DO BRODZIKÓW": "Najazd", "NOGI DO BRODZIKÓW IPSILON": "Nogi Ipsilon", "NOŚNIK DLA BRODZIKA": "Nośnik",
        "NOŚNIK DO WANNY": "Nośnik", "ODPŁYWY LINIOWE": "Harmony", "HARMONY": "Harmony", "PANELE DO BRODZIKÓW": "Panele do brodzików",
        "SINEGRID": "Sinergid", "TEBE": "Tebe", "TORRES": "Torres", "ZABUDOWA WANNY": "Obudowa uniwersalna", "ŚCIANKA": "Wall Comfort"}
inv = collections.defaultdict(lambda: collections.Counter())
size = collections.Counter()
for base, tag in ((ROOT + r"\materiały\2026 - Paczka Ecommerce LEROY MERLIN", "p"), (ROOT + r"\materiały\LEROY MERLIN - poprawki po Empco", "e")):
    lb = "\\\\?\\" + base
    for dp, dn, fn in os.walk(lb):
        rel = dp[len(lb) + 1:]
        if not rel: continue
        top = rel.split("\\")[0]
        fam = FOLD.get(top)
        if not fam: continue
        low = rel.lower()
        if "frigo - sensea\\frigo\\" in low + "\\": continue
        for f in fn:
            e = f.lower().rsplit(".", 1)[-1]
            if e in ("db", "tmp", "psd", "cdr"): continue
            if tag == "e": k = "infografika" if e == "png" else "inne"
            elif e == "pdf": k = "instrukcja" if "instrukcja" in f.lower() else "rysunek"
            elif e == "docx": k = "opis"
            elif e == "mp4": k = "film"
            elif "pack" in low: k = "packshot"
            elif "aran" in low: k = "aranżacja"
            elif "rys" in low: k = "rysunek"
            else: k = "zdjęcie dodatkowe"
            inv[fam][k] += 1
            size[fam] += os.path.getsize(os.path.join(dp, f))

series = []
for fam, cat, typ, lead, scenes, feats, gw in SER:
    items = [p for p in P if p["fam"] == fam]
    cols = []
    for p in items:
        if p["c"] and p["c"] not in [c["n"] for c in cols]:
            cols.append({"n": p["c"], "e": p["ce"], "ral": p["ral"], "hx": p["hx"]})
    hs = sorted({str(p["h"]) for p in items if p["h"]}, key=lambda v: float(re.split("[/]", v)[0]))
    series.append({"fam": fam, "cat": cat, "type": typ, "lead": lead, "scenes": scenes, "feats": feats, "gw": gw,
                   "n": len(items), "brand": collections.Counter(p["brand"] for p in items).most_common(1)[0][0] if items else "Schedpol",
                   "shapes": sorted({p["shape"] for p in items if p["shape"]}), "colors": cols, "heights": hs,
                   "pack": items[0]["im"] if items else "", "new": any(p["new"] for p in items),
                   "files": dict(inv[fam]), "mb": round(size[fam] / 1e6, 1)})

img = {k: {"f": v["file"], "w": v["w"], "h": v["h"], "tb": v.get("tb", False), "k": v["kind"]} for k, v in man.items()}

contacts = {
 "bok": [{"n": "BOK 1 · Zachód", "tel": "691 947 536", "mail": "bok1@schedpol.pl"},
         {"n": "BOK 2 · Wschód", "tel": "603 509 837", "mail": "bok2@schedpol.pl"},
         {"n": "BOK 3 · Południe", "tel": "601 424 132", "mail": "bok3@schedpol.pl"}],
 "hours": "pon.–pt. 8:00–16:00", "company": "SCHEDPOL Sp. z o.o., ul. Przemysłowa 2, 64-400 Bielsko (Międzychód)", "since": 1981,
}
surfaces = [
 {"n": "Smooth White", "pl": "biały gładki", "ral": "RAL 9003", "hx": "#F7F7F5", "tex": "wc-tex-sw"},
 {"n": "White Stone", "pl": "biały kamień", "ral": "RAL 9016", "hx": "#EDEDEA", "tex": "tex-white-stone"},
 {"n": "Cashmere Stone", "pl": "kaszmirowy kamień", "ral": "RAL 9001", "hx": "#E9E0D2", "tex": "tex-cashmere"},
 {"n": "Grey Stone", "pl": "szary kamień", "ral": "RAL 7012", "hx": "#575D5E", "tex": "tex-grey-stone"},
 {"n": "Black Stone", "pl": "czarny kamień", "ral": "RAL 9004", "hx": "#2A2A2B", "tex": "tex-black-stone"},
]
data = {"meta": {"generated": "2026-11-13", "products": len(P), "series": len(series),
                 "sources": ["Tytuły Produktów_ Leroy Merlin.xlsx", "Przegląd oferty (Leroy Merlin) 2025.09", "LEROY MERLIN - poprawki po Empco"]},
        "img": img, "series": series, "products": P, "contacts": contacts, "surfaces": surfaces}

HELP = r"""
/* ---- pomocnicze (wspólne dla makiet) ---- */
(function (SP) {
  SP.base = SP.base || ((window.SP_UP != null ? window.SP_UP : '../') + 'assets/img/');
  SP.src = function (k) { var i = SP.img[k]; return i ? SP.base + i.f : ''; };
  SP.isCutout = function (k) { var i = SP.img[k]; return !!(i && i.tb); };
  SP.dims = function (p) {            // "80 × 100 × 3,5 cm"
    var parts = [];
    if (p.a != null) parts.push(String(p.a));
    if (p.b != null) parts.push(String(p.b));
    if (p.h != null && p.h !== '') parts.push(String(p.h).replace('.', ','));
    return parts.length ? parts.join(' × ') + ' cm' : '';
  };
  SP.byFam = function (fam) { return SP.products.filter(function (p) { return p.fam === fam; }); };
  SP.serie = function (fam) { return SP.series.filter(function (s) { return s.fam === fam; })[0]; };
  SP.byRef = function (ref) { return SP.products.filter(function (p) { return p.ref === String(ref); })[0]; };
  SP.cats = [
    { id: 'brodzik', label: 'Brodziki' }, { id: 'wanna', label: 'Wanny' }, { id: 'odpływ liniowy', label: 'Odpływy liniowe' },
    { id: 'panel ścienny', label: 'Panele ścienne' }, { id: 'nośnik', label: 'Nośniki' }, { id: 'obudowa', label: 'Obudowy wanien' },
    { id: 'akcesoria', label: 'Akcesoria' }
  ];
  SP.catLabel = function (id) { var c = SP.cats.filter(function (c) { return c.id === id; })[0]; return c ? c.label : id; };
  SP.search = function (q) {          // szukanie po nr ref., serii, wymiarze, kolorze
    q = String(q || '').toLowerCase().replace(/×/g, 'x').replace(/\s+/g, ' ').trim();
    if (!q) return SP.products.slice();
    var terms = q.split(' ');
    return SP.products.filter(function (p) {
      var hay = (p.ref + ' ' + p.s + ' ' + p.fam + ' ' + p.cat + ' ' + p.shape + ' ' + p.c + ' ' + p.brand + ' ' +
        (p.a != null ? p.a + 'x' + p.b : '') + ' ' + (p.b != null ? p.b + 'x' + p.a : '') + ' ' + p.t + ' ' + (p.ean || '') + ' ' + (p.sup || '')).toLowerCase().replace(/×/g, 'x');   // 25.11: także EAN i kod dostawcy (lm.js)
      return terms.every(function (t) { return hay.indexOf(t) !== -1; });
    });
  };
})(window.SP);
"""
js = "/* Wygenerowano automatycznie z materiałów Schedpol dla LM — dane do makiet. */\nwindow.SP = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n" + HELP
open(OUT + r"\data.js", "w", encoding="utf-8").write(js)
print("data.js:", round(len(js.encode("utf-8")) / 1024), "KB | serie:", len(series), "| produkty:", len(P))
for s in series:
    print(f'  {s["fam"]:28s} n={s["n"]:3d} {s["brand"]:8s} kszt={len(s["shapes"])} kol={len(s["colors"])} h={s["heights"]} pliki={sum(s["files"].values())} ({s["mb"]} MB) {dict(s["files"])}')
print("nieprzypisane fam:", sorted({p["fam"] for p in P} - {s[0] for s in SER}))

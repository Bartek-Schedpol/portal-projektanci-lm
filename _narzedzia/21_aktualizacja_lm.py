# -*- coding: utf-8 -*-
"""Aktualizacja portalu wg eksportu referencji LM z 26.11.2026 (warstwa assets/aktualizacja-lm.js).

Warstwa nakłada się na data.js / lm.js / packshoty.js / rysunki.js / modele3d.js / dokumenty.js (ładowana po nich),
bez ponownego uruchamiania generatorów 4/8 (nadpisałyby ręczne korekty odcieni packshotów):
  - gama, EAN i kod dostawcy wg nowego eksportu (nowa gama „M”),
  - usunięcie indeksów, których nie ma w eksporcie (83648377 Frigo),
  - nowy indeks Ipsilon 160×90 biały kamień (92529792; bryła, rysunek i dokumenty jak 92530022 — ta sama geometria),
  - nowa seria UNITY — odpływ liniowy pod winyl (20 indeksów) z materiałów „2026.06.10 Unity Odpływ pod winyl LM”.
Treści UNITY wg arkusza partnera LM, bez twierdzeń niezgodnych z EmpCo (staż w latach, „miliony zadowolonych”, „bezpieczny dla rodziny”,
„idealne dopasowanie”, przewaga z atestu) i bez okresu gwarancji (brak karty gwarancyjnej dla UNITY w materiałach).
Uruchom: python 21_aktualizacja_lm.py <eksport.xlsx>
"""
import io, json, os, re, sys, glob
import openpyxl
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); A = os.path.join(ROOT, 'assets')
MAT = os.path.join(os.path.dirname(ROOT), 'materiały')
UN = os.path.join(MAT, '2026.06.10 Unity Odpływ pod winyl LM')
IMG = os.path.join(A, 'img'); RYS = os.path.join(IMG, 'rys')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

XLSX = sys.argv[1] if len(sys.argv) > 1 else os.path.join(MAT, '2026-11-26T08-30-15-moje-referencje-0fe4aff1-29b7-41a8-9dff-87d9ea0db037.xlsx')
rows = list(openpyxl.load_workbook(XLSX, read_only=True).worksheets[0].iter_rows(values_only=True))
H = [str(c or '').strip() for c in rows[0]]
LM = {}
for r in rows[1:]:
    d = {H[i]: (str(v).strip() if v is not None else '') for i, v in enumerate(r) if i < len(H)}
    if d.get('Referencja produktu'): LM[d['Referencja produktu']] = d

dj = io.open(os.path.join(A, 'data.js'), encoding='utf-8').read()
P = {p['ref']: p for p in json.loads(dj[dj.index('window.SP = ') + 12:dj.index(';\n\n/* ---- pomocnicze')])['products']}

REMOVE = sorted(r for r in P if r not in LM)
LMDATA = {r: {'g': d.get('Gama', ''), 'ean': d.get('GTIN (EAN)', ''), 'sup': d.get('Referencja Dostawcy', '')} for r, d in LM.items()}

# ---------- UNITY: obrazy ----------
COL = {  # folder koloru -> nazwa w portalu, hx, słowo w kluczu
    'Steel': ('stal', '#C9CCCF', 'steel'), 'Black': ('czarny', '#1B1B1C', 'black'), 'Gold Shine': ('złoty', '#C9A24B', 'gold'),
    'Copper Shine': ('miedziany', '#B8734F', 'copper'), 'Graphite Shine': ('grafitowy', '#4B4D52', 'graphite')}
NEWIMG = {}


def save(src, key, kind, maxw, alpha):
    im = Image.open(src)
    if im.mode == 'CMYK': im = im.convert('RGB')
    im = im.convert('RGBA' if alpha else 'RGB')
    if alpha:                                          # przytnij przezroczyste marginesy
        bb = im.getbbox()
        if bb: im = im.crop(bb)
    im.thumbnail((maxw, maxw), Image.LANCZOS)
    ext = 'webp' if alpha else 'jpg'
    fn = key + '.' + ext
    if alpha: im.save(os.path.join(IMG, fn), 'WEBP', quality=88, method=6)
    else: im.save(os.path.join(IMG, fn), 'JPEG', quality=82, optimize=True, progressive=True)
    NEWIMG[key] = {'f': fn, 'w': im.width, 'h': im.height, 'tb': bool(alpha), 'k': kind}
    return key


PHOTO = os.path.join(UN, 'odpływy pod winyl wysłane zdjęcia na portal')
folders = {f: os.path.join(PHOTO, f) for f in os.listdir(PHOTO) if os.path.isdir(os.path.join(PHOTO, f))}
ean_dir, colkey = {}, {}
for name, path in folders.items():
    c = next(k for k in COL if k in name)
    for f in os.listdir(path):
        m = re.search(r'PDT[-_](\d{13})-', f)
        if m: ean_dir[m.group(1)] = path; colkey[m.group(1)] = c


def pick(ean, tag):
    for ext in ('png', 'jpg'):
        g = glob.glob(os.path.join(ean_dir[ean], 'PDT[-_]%s-%s.%s' % (ean, tag, ext)))
        if g: return g[0]
    return None


any_ean = next(iter(ean_dir))
# 26.11: korpus (P-01) i widok z góry (P-02) nie są pokazywane przy UNITY — decyzja użytkownika
PACKF = {'Steel': 'Unity silver.png', 'Black': 'Unity pakszot.png', 'Gold Shine': 'unity gold.png', 'Copper Shine': 'unity copper.png', 'Graphite Shine': 'unity grafit.png'}   # packshoty główne (decyzja użytkownika 26.11)
per = {}
for c, (cn, hx, w) in COL.items():
    e = next(x for x in ean_dir if colkey[x] == c)
    per[c] = {'pack': save(os.path.join(UN, '1. Packshot', PACKF[c]), 'unity-' + w, 'pack', 900, True),
              'mask': save(pick(e, 'P-05'), 'unity-maskownica-' + w, 'pack', 900, True),
              'a3': save(pick(e, 'A-03'), 'unity-aranzacja-' + w, 'scene', 1200, False),
              'a4': save(pick(e, 'A-04'), 'unity-detal-' + w, 'scene', 1200, False)}
rim = Image.open(os.path.join(UN, '3. Rysunek Techniczny', 'Rys Techniczny.jpg')).convert('RGB')
bb = Image.eval(rim.convert('L'), lambda v: 255 - v).point(lambda v: 255 if v > 18 else 0).getbbox()
if bb: rim = rim.crop((max(0, bb[0] - 30), max(0, bb[1] - 30), min(rim.width, bb[2] + 30), min(rim.height, bb[3] + 30)))
rim.thumbnail((1700, 1700), Image.LANCZOS)
rim.info.pop('icc_profile', None); rim = rim.convert('L').point(lambda v: 255 if v > 232 else v).quantize(colors=16, dither=Image.Dither.NONE); rim.info = {}; rim.save(os.path.join(RYS, 'unity-rysunek-techniczny.png'), optimize=True)
RYSU = {'f': 'unity-rysunek-techniczny.png', 'w': rim.width, 'h': rim.height, 'src': 'materiały: 2026.06.10 Unity Odpływ pod winyl LM / 3. Rysunek Techniczny'}

# ---------- UNITY: produkty z arkusza partnera LM ----------
ws = openpyxl.load_workbook(os.path.join(UN, '10000748_extract_partner_data_20260703075928.xlsm'), read_only=True, data_only=True)['MOD_201131']
pr = list(ws.iter_rows(values_only=True)); PH = [str(x) for x in pr[2]]
NEWP, EXTRA = [], {}
for r in pr[6:]:
    d = dict(zip(PH, r))
    ref, ean = str(d.get('Referencja ADEO') or ''), str(d.get('Kod EAN (GTIN)') or '')
    if not re.fullmatch(r'\d{8}', ref): continue
    c = colkey[ean]; cn, hx, w = COL[c]
    L = int(float(d.get('Długość (w mm)*') or 0)) // 10
    NEWP.append({'ref': ref, 's': 'Unity', 'fam': 'Unity', 'cat': 'odpływ liniowy', 'tech': '', 'tn': '', 'brand': 'Schedpol', 'shape': '',
                 'a': L, 'b': None, 'h': None, 'c': cn, 'ce': '', 'ral': '', 'hx': hx, 'g': LMDATA.get(ref, {}).get('g', 'X'), 'new': True,
                 'im': per[c]['pack'], 't': str(d.get('Tytuł produktu') or ''), 'noCadDecor': True,   # zdjęcie główne: packshot w kolorze maskownicy
                 'ean': ean, 'sup': LMDATA.get(ref, {}).get('sup') or str(d.get('Artykuł u dostawcy handlowego') or '')})
    EXTRA[ref] = [{'k': per[c]['mask'], 'kind': 'pack', 'cap': 'Maskownica ' + cn},
                  {'k': per[c]['a3'], 'kind': 'photo', 'cap': 'Wizualizacja poglądowa'},
                  {'k': per[c]['a4'], 'kind': 'photo', 'cap': 'Wizualizacja poglądowa · zbliżenie'}]
NEWP.sort(key=lambda p: (list(COL).index(next(k for k, v in COL.items() if v[0] == p['c'])), p['a']))
SERIES = {'fam': 'Unity', 'cat': 'odpływ liniowy', 'type': 'Odpływ liniowy pod winyl',
          'lead': 'Odpływ liniowy do podłóg winylowych (wykładziny i panele o grubości 2–3 mm). Długości 60–90 cm, maskownica 2w1 w pięciu wykończeniach.',
          'scenes': [], 'feats': ['Do podłóg winylowych o grubości 2–3 mm — maskownica na poziomie posadzki, bez progu.',
                                  'Przepływ 42 l/min (dane producenta).',
                                  'Maskownica 2w1 w pięciu wykończeniach: stal, czarny, złoty, miedziany, grafitowy (PVD).',
                                  'Regulowane nóżki: wysokość montażu 70–85 mm. Syfon wyjmowany od góry haczykiem z zestawu.',
                                  'Korpus z aluminium. Długości 60, 70, 80 i 90 cm.'],
          'gw': '', 'n': len(NEWP), 'brand': 'Schedpol', 'shapes': [], 'colors': [{'n': v[0], 'e': '', 'ral': '', 'hx': v[1]} for v in COL.values()],
          'heights': [], 'pack': per['Graphite Shine']['pack'], 'new': True, 'files': {}, 'mb': 0}

# ---------- Ipsilon 160×90 biały kamień ----------
sib = P['92530022']; wsib = P['92529791']
ips = dict(sib); ips.update({'ref': '92529792', 'c': wsib['c'], 'ce': wsib.get('ce', ''), 'ral': wsib.get('ral', ''), 'hx': wsib.get('hx', ''),
                             'im': wsib['im'], 'g': LMDATA['92529792']['g'], 'new': False,
                             't': 'Brodzik Laminowany Prostokątny Sensea Ipsilon 160x90x5/3cm Biały Kamień'})
ips.update({'ean': LMDATA['92529792']['ean'], 'sup': LMDATA['92529792']['sup']})
NEWP.append(ips)
LMDATA_NEW = {p['ref']: {'g': p['g'], 'ean': p['ean'], 'sup': p['sup']} for p in NEWP}

js = '''/* Wygenerowano (_narzedzia/21_aktualizacja_lm.py) — aktualizacja wg eksportu referencji LM z 26.11.2026.
   Warstwa po data.js, lm.js, packshoty.js, rysunki.js, dokumenty.js, modele3d.js: gama/EAN/kod dostawcy wg eksportu (nowa gama „M”),
   usunięte indeksy spoza eksportu, nowy Ipsilon 160×90 biały kamień, nowa seria UNITY (odpływ liniowy pod winyl). */
(function (SP) {
  var REMOVE = %s, LMD = %s, NEWP = %s, IMG = %s, EXTRA = %s, SERIES = %s, RYSU = %s;
  SP.products = SP.products.filter(function (p) { return REMOVE.indexOf(p.ref) === -1; });
  Object.keys(IMG).forEach(function (k) { SP.img[k] = IMG[k]; });
  if (!SP.serie('Unity')) { var hi = SP.series.findIndex(function (s) { return s.fam === 'Harmony'; }); SP.series.splice(hi + 1, 0, SERIES); }
  NEWP.forEach(function (p) { if (!SP.byRef(p.ref)) SP.products.push(p); });
  SP.products.forEach(function (p) { var x = LMD[p.ref]; if (x) { p.g = x.g; if (x.ean) p.ean = x.ean; if (x.sup) p.sup = x.sup; p.lmMissing = false; } });
  SP.extra = SP.extra || {}; Object.keys(EXTRA).forEach(function (r) { SP.extra[r] = EXTRA[r]; });
  SP.rys = SP.rys || {};
  NEWP.forEach(function (p) { if (p.fam === 'Unity') SP.rys[p.ref] = RYSU; });
  if (SP.rys['92530022']) SP.rys['92529792'] = SP.rys['92530022'];
  if (SP.cad && SP.cad['92530022']) SP.cad['92529792'] = SP.cad['92530022'];
  if (SP.docMap && SP.docMap['92530022']) SP.docMap['92529792'] = SP.docMap['92530022'];
  SP.series.forEach(function (s) { s.n = SP.products.filter(function (p) { return p.fam === s.fam; }).length; });
})(window.SP);
''' % tuple(json.dumps(x, ensure_ascii=False) for x in (REMOVE, dict(LMDATA, **LMDATA_NEW), NEWP, NEWIMG, EXTRA, SERIES, RYSU))
io.open(os.path.join(A, 'aktualizacja-lm.js'), 'w', encoding='utf-8').write(js)
print('usunięte:', REMOVE, '| nowe:', len(NEWP), '| obrazy:', len(NEWIMG), '| gama M:', sum(1 for v in LMDATA.values() if v['g'] == 'M'))

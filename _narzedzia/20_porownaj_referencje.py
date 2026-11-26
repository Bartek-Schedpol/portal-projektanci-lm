# -*- coding: utf-8 -*-
"""Porównanie eksportu referencji LM z portalem (26.11.2026).
Użycie: python 20_porownaj_referencje.py <nowy.xlsx> [stary.xlsx]
Porównuje: indeksy nowe / usunięte względem portalu (assets/data.js), gama, EAN, kod dostawcy, nazwa w LM.
Wynik: tekst na ekran + _narzedzia/porownanie_referencji.json
"""
import io, json, os, re, sys
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(os.path.dirname(HERE), 'assets')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def load(path):
    rows = list(openpyxl.load_workbook(path, read_only=True).worksheets[0].iter_rows(values_only=True))
    h = [str(c or '').strip() for c in rows[0]]
    out = {}
    for r in rows[1:]:
        d = {h[i]: (str(v).strip() if v is not None else '') for i, v in enumerate(r) if i < len(h)}
        ref = d.get('Referencja produktu', '')
        if ref: out[ref] = d
    return out


def js_obj(text, name):
    i = text.index('var %s = ' % name) + len('var %s = ' % name)
    return json.JSONDecoder().raw_decode(text[i:])[0]


new = load(sys.argv[1]); old = load(sys.argv[2]) if len(sys.argv) > 2 else {}
d = io.open(os.path.join(A, 'data.js'), encoding='utf-8').read()
P = {p['ref']: p for p in json.loads(d[d.index('window.SP = ') + 12:d.index(';\n\n/* ---- pomocnicze')])['products']}
L = js_obj(io.open(os.path.join(A, 'lm.js'), encoding='utf-8').read(), 'L')

added = sorted(r for r in new if r not in P)
gone = sorted(r for r in P if r not in new)
chg = []
for r in sorted(set(new) & set(P)):
    n, l = new[r], L.get(r, {})
    c = {}
    if n.get('Gama', '') != l.get('g', P[r].get('g', '')): c['gama'] = [l.get('g', ''), n.get('Gama', '')]
    if n.get('GTIN (EAN)', '') and n.get('GTIN (EAN)', '') != l.get('ean', ''): c['ean'] = [l.get('ean', ''), n.get('GTIN (EAN)', '')]
    if n.get('Referencja Dostawcy', '') != l.get('sup', ''): c['kod_dostawcy'] = [l.get('sup', ''), n.get('Referencja Dostawcy', '')]
    if old.get(r) and old[r].get('Nazwa produktu') != n.get('Nazwa produktu'): c['nazwa_LM'] = [old[r].get('Nazwa produktu'), n.get('Nazwa produktu')]
    if c: chg.append((r, P[r]['fam'], P[r].get('s'), c))

print('Nowy eksport: %d indeksów | stary: %d | portal: %d' % (len(new), len(old), len(P)))
print('\n=== NOWE w eksporcie, brak w portalu (%d) ===' % len(added))
for r in added:
    n = new[r]
    print('%s | %s | gama %s | %s / %s | utw. %s | 1. dostawa %s | EAN %s | kod %s' % (r, n.get('Nazwa produktu'), n.get('Gama'), n.get('Nazwa podrejonu'), n.get('Typ artykułu'),
          n.get('Data utworzenia'), n.get('Data 1 dostawy'), n.get('GTIN (EAN)'), n.get('Referencja Dostawcy')))
print('\n=== W PORTALU, brak w nowym eksporcie (%d) ===' % len(gone))
for r in gone:
    print('%s | %s %s | %s %s | w starym eksporcie: %s' % (r, P[r]['fam'], P[r].get('s'), P[r].get('a'), P[r].get('b'), 'tak (gama %s)' % old[r].get('Gama') if r in old else 'nie'))
print('\n=== ZMIANY w istniejących indeksach (%d) ===' % len(chg))
for r, f, s, c in chg:
    print('%s | %s | %s' % (r, s, '; '.join('%s: %s → %s' % (k, v[0] or '—', v[1] or '—') for k, v in c.items())))
json.dump({'nowe': {r: new[r] for r in added}, 'usuniete': gone, 'zmiany': [{'ref': r, 'seria': s, 'zmiany': c} for r, f, s, c in chg]},
          open(os.path.join(HERE, 'porownanie_referencji.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

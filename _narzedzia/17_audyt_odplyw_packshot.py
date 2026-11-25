# -*- coding: utf-8 -*-
"""Audyt: położenie odpływu na packshocie vs rysunek techniczny (25.11.2026).

Każda unikalna para (packshot, kształt, wymiar) brodzika -> wiersz arkusza kontrolnego:
packshot | rysunek techniczny | opis (nr ref., seria, kształt, wymiar, kolor) — do oceny wzrokowej.
Wynik: _narzedzia/_audyt_odplyw/arkusz_XX.jpg + lista.json
"""
import io, json, os, re
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); A = os.path.join(ROOT, 'assets')
OUT = os.path.join(HERE, '_audyt_odplyw'); os.makedirs(OUT, exist_ok=True)


def js_obj(text, name):
    i = text.index('var %s = ' % name) + len('var %s = ' % name)
    dec = json.JSONDecoder()
    return dec.raw_decode(text[i:])[0]


d = io.open(os.path.join(A, 'data.js'), encoding='utf-8').read()
data = json.loads(d[d.index('window.SP = ') + 12:d.index(';\n\n/* ---- pomocnicze')])
pk = io.open(os.path.join(A, 'packshoty.js'), encoding='utf-8').read()
IMG, IM, FIX = js_obj(pk, 'IMG'), js_obj(pk, 'IM'), js_obj(pk, 'FIX')
img = dict(data['img']); img.update(IMG)
rys = json.loads(io.open(os.path.join(A, 'rysunki.js'), encoding='utf-8').read().split('window.SP.rys =', 1)[1].strip().rstrip(';').split(';\n')[0])

rows, seen = [], {}
for p in data['products']:
    if p['cat'] != 'brodzik': continue
    im = IM.get(p['ref'], p['im'])
    f = FIX.get(p['ref'], {})
    shape = f.get('shape', p.get('shape')); col = f.get('c', p.get('c'))
    r = rys.get(p['ref'], {}).get('f', '')
    key = (im, r)
    if key in seen:
        seen[key]['refs'].append(p['ref']); continue
    row = {'refs': [p['ref']], 'fam': p['fam'], 'shape': shape, 'dim': '%s×%s' % (p.get('a'), p.get('b')), 'c': col, 'im': im,
           'imf': img.get(im, {}).get('f', ''), 'rys': r}
    seen[key] = row; rows.append(row)
rows.sort(key=lambda x: (x['fam'], x['shape'] or '', x['dim']))
json.dump(rows, open(os.path.join(OUT, 'lista.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

try:
    F = ImageFont.truetype('arial.ttf', 15); FB = ImageFont.truetype('arialbd.ttf', 17)
except OSError:
    F = FB = ImageFont.load_default()
W, RH, PER = 1500, 330, 6


def thumb(path, box):
    if not path or not os.path.exists(path):
        t = Image.new('RGB', box, (240, 220, 220)); ImageDraw.Draw(t).text((10, 10), 'BRAK', fill=(160, 0, 0), font=FB); return t
    i = Image.open(path).convert('RGBA'); bg = Image.new('RGBA', i.size, (255, 255, 255, 255)); bg.alpha_composite(i)
    i = bg.convert('RGB'); i.thumbnail(box)
    t = Image.new('RGB', box, 'white'); t.paste(i, ((box[0] - i.width) // 2, (box[1] - i.height) // 2)); return t


for s in range(0, len(rows), PER):
    sheet = Image.new('RGB', (W, RH * min(PER, len(rows) - s)), 'white'); dr = ImageDraw.Draw(sheet)
    for k, row in enumerate(rows[s:s + PER]):
        y = k * RH
        sheet.paste(thumb(os.path.join(A, 'img', row['imf']), (560, 310)), (10, y + 10))
        sheet.paste(thumb(os.path.join(A, 'img', 'rys', row['rys']) if row['rys'] else '', (420, 310)), (590, y + 10))
        n = s + k + 1
        dr.text((1030, y + 20), '#%d  %s' % (n, row['fam']), fill='black', font=FB)
        txt = ['kształt: %s' % row['shape'], 'wymiar: %s' % row['dim'], 'kolor: %s' % row['c'], 'packshot: %s' % row['im'][:40],
               'indeksy (%d): %s' % (len(row['refs']), ' '.join(row['refs'][:6]) + (' …' if len(row['refs']) > 6 else ''))]
        for t_, line in enumerate(txt): dr.text((1030, y + 52 + t_ * 24), line, fill=(40, 40, 40), font=F)
        dr.line((0, y + RH - 1, W, y + RH - 1), fill=(200, 200, 200), width=2)
    sheet.save(os.path.join(OUT, 'arkusz_%02d.jpg' % (s // PER + 1)), quality=82)
print('par packshot/rysunek:', len(rows), ' arkuszy:', (len(rows) + PER - 1) // PER)

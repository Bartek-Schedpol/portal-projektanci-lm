# -*- coding: utf-8 -*-
"""Wersje językowe portalu (25.11.2026): en/ i ro/ powstają z plików V2 (v2/index.html, v2/podstrony.html).
Strony są identyczne jak polskie — teksty tłumaczy w przeglądarce assets/i18n.js słownikiem assets/i18n-<lang>.js
(18_slownik.py). Uruchamiać po każdej zmianie w v2/*.html (i po 18_slownik.py, jeśli zmienił się słownik — wtedy tylko podbić ?v=).
Polska wersja dostaje sam przełącznik języka (i18n.js bez słownika).
"""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
V = '20261126k'
PAGES = ['index.html', 'podstrony.html']
HIDE = '<style>.i18n-wait body{visibility:hidden}</style>'   # bez „mignięcia” polskiego tekstu przed tłumaczeniem


def pl_switcher(s):
    s = re.sub(r'\n?<script src="\.\./assets/i18n[^"]*"[^>]*></script>', '', s)
    return s.replace('</head>', '<script src="../assets/i18n.js?v=%s" defer></script>\n</head>' % V, 1)


for f in PAGES:
    p = os.path.join(ROOT, 'v2', f)
    s = io.open(p, encoding='utf-8').read()
    s2 = pl_switcher(s)
    if s2 != s: io.open(p, 'w', encoding='utf-8', newline='').write(s2)
    base = re.sub(r'\n?<script src="\.\./assets/i18n[^"]*"[^>]*></script>', '', s2)
    for lang in ('en', 'ro'):
        d = os.path.join(ROOT, lang); os.makedirs(d, exist_ok=True)
        t = base.replace('<html lang="pl">', '<html lang="%s" class="i18n-wait">' % lang, 1)
        t = t.replace('url(hero.jpg)', 'url(../v2/hero.jpg)').replace('src="hero.jpg"', 'src="../v2/hero.jpg"')
        # znak „30 lat” (SVG — tłumacz w i18n.js go pomija): napisy na wstędze i pod spodem
        Z30 = {'en': ('YEARS', 'OF PARTNERSHIP', '2'), 'ro': ('DE ANI', 'DE COLABORARE', '1.6')}[lang]
        t = t.replace('letter-spacing="4" fill="#fff">LAT</text>', 'letter-spacing="%s" fill="#fff">%s</text>' % (Z30[2], Z30[0])).replace('>WSPÓŁPRACY</text>', '>%s</text>' % Z30[1])
        t = t.replace('</head>', HIDE + '\n<script src="../assets/i18n-%s.js?v=%s"></script>\n<script src="../assets/i18n.js?v=%s"></script>\n</head>' % (lang, V, V), 1)
        t = t.replace('<!doctype html>', '<!doctype html>\n<!-- Wygenerowano z v2/%s (_narzedzia/19_wersje_jezykowe.py) — nie edytować ręcznie -->' % f, 1)
        io.open(os.path.join(d, f), 'w', encoding='utf-8', newline='').write(t)
print('OK: v2 (przełącznik), en/, ro/ —', ', '.join(PAGES))

# -*- coding: utf-8 -*-
"""Baza modeli 3D dla LM z paczki „materiały/008 Modele 3D” (katalog Schedpol 2021).

Serie LM mają w katalogu inne nazwy — rozpoznane po bryle (render vs packshot, wymiary, wysokość, odpływ):
  Balans→KALAIT, Integral→NEW HORIZONS, Magnetic→OMEGA (kamień: OMEGA STONE), Frigo→COMPETIA NEW,
  Ipsilon→CASPAR NEW (kamień: CASPAR NEW STONE), Comfo→GRANDO PLUS, Sinergid→EKO 2, Torres→FERRA;
  Grawello, Dante, Go Baby, Dafne i panele — te same nazwy.
Dopasowanie indeksu LM do pliku: po ZMIERZONYCH wymiarach głównej bryły (nazwy plików w paczce bywają błędne)
i kształcie (R55 = półokrągły, 5k = pięciokątny). Pliki wspólne dla wariantów kolorystycznych (ta sama bryła).

Uruchom:  python 10_modele_3d.py   -> assets/cad/*.dwg|obj|3ds|glb + assets/modele3d.js
"""
import json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(os.path.dirname(ROOT), 'materiały', '008 Modele 3D', '01. 3D_SCHEDPOL_2021')
OUT = os.path.join(ROOT, 'assets', 'cad')
BLENDER = r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'

SERIES = {  # seria LM -> foldery katalogu (drugi = wersja kamienna)
    'Balans': ['00. KALAIT'], 'Integral': ['09. NEW HORIZONS'], 'Magnetic': ['03. OMEGA', '04. OMEGA STONE'],
    'Frigo': ['11. COMPETIA NEW'], 'Ipsilon': ['17. CASPAR NEW', '18. CASPAR NEW STONE'], 'Comfo': ['12. GRANDO PLUS'],
    'Sinergid': ['19. EKO 2'], 'Torres': ['30. FERRA'],
    'Grawello': ['13. GRAWELLO'], 'Dante': ['15. DANTE'], 'Go Baby': ['14. GO BABY'], 'Dafne': ['21. DAFNE'],
}
PANELS = {'Panel Grawello': '24. PANEL GRAWELLO - ZEFIR', 'Panel Dante': '27. PANEL DANTE - DORIS',
          'Panel Go Baby': '25. PANEL GO BABY - BONA', 'Panel Dafne': '26. PANEL DAFNE'}
H_TOL = 2.0   # cm — tolerancja wysokości (np. Omega 5,5 vs Magnetic 5)


def shape_of_name(f):
    n = f.lower()
    if '5k' in n: return 'pięciokątny'
    if 'r55' in n or 'r90' in n: return 'półokrągły'
    return None


def main_dims(path):
    """Wymiary największej bryły w pliku OBJ (bez dołożonych obok kratek / akcesoriów), posortowane malejąco."""
    verts, faces, cur = [], {}, '_'
    with open(path, encoding='latin-1') as f:
        for l in f:
            if l.startswith('v '):
                verts.append([float(x) for x in l.split()[1:4]])
            elif l[:2] in ('o ', 'g '):
                cur = l.strip()
            elif l.startswith('f '):
                s = faces.setdefault(cur, set())
                for t in l.split()[1:]:
                    i = int(t.split('/')[0]); s.add(i - 1 if i > 0 else len(verts) + i)
    best = None
    for idx in faces.values():
        P = [verts[i] for i in idx]
        d = sorted(max(p[k] for p in P) - min(p[k] for p in P) for k in range(3))
        if best is None or d[1] * d[2] > best[1] * best[2]:
            best = d
    return [round(best[2], 1), round(best[1], 1), round(best[0], 1)] if best else None


def catalog(folder):
    out = []
    for dp, dn, fn in os.walk(os.path.join(SRC, folder)):
        for f in fn:
            if f.lower().endswith('.obj'):
                p = os.path.join(dp, f)
                out.append({'obj': p, 'stem': os.path.splitext(f)[0], 'dims': main_dims(p), 'shape': shape_of_name(f)})
    return out


def sibling(objpath, ext):
    stem = os.path.splitext(os.path.basename(objpath))[0].strip().lower()
    base = os.path.dirname(os.path.dirname(objpath))
    for dp, dn, fn in os.walk(base):
        for f in fn:
            n, e = os.path.splitext(f)
            if n.strip().lower() == stem and e.lower() == '.' + ext:
                return os.path.join(dp, f)
    return None


# Położenie odpływu wg rysunków technicznych produktów LM (odczyt 20.11.2026, assets/img/rys):
#   Frigo: prostokątne — środek krótszego boku, 15 cm od krawędzi; kwadratowe — narożnik 15 cm;
#          półokrągłe i pięciokątne — narożnik naprzeciw ściętego/łukowego.
#   Ipsilon: prostokątne — środek dłuższego boku, 14 cm od krawędzi (wyjątek 90×70: narożnik 15,2 cm);
#          kwadratowe — narożnik 15,2; półokrągłe — narożnik przy łuku 15,6; pięciokątne — narożnik naprzeciw ścięcia.
#   Magnetic: narożnik 12,8 cm (prostokątne w katalogu 2021 miały odpływ na środku dłuższego boku).
#   Sinergid: narożnik 15 cm. Balans, Integral: prostokątne — środek krótszego boku 33 cm (90×110, 90×120: 38 cm), kwadratowe — narożnik 21 cm.
def drain_rule(p):
    fam, shp = p['fam'], p.get('shape')
    rect = shp == 'prostokątny'
    if fam == 'Frigo':
        return ['short_mid', 15] if rect else (['corner_opp', 15] if shp in ('półokrągły', 'pięciokątny') else ['corner', 15])
    if fam == 'Ipsilon':
        if rect: return ['corner', 15.2] if sorted([float(p['a']), float(p['b'])]) == [70.0, 90.0] else ['long_mid', 14]
        return {'półokrągły': ['corner_adj', 15.6], 'pięciokątny': ['corner_opp', 15]}.get(shp, ['corner', 15.2])
    if fam == 'Magnetic':
        return ['corner_opp', 12.8] if shp == 'półokrągły' else ['corner', 12.8]
    if fam == 'Sinergid':
        return ['corner_opp', 15] if shp == 'półokrągły' else ['corner', 15]
    if fam in ('Balans', 'Integral'):        # rysunek LM: 330 mm (380 mm dla 900×1100 i 900×1200)
        if not rect: return ['corner', 21]
        return ['short_mid', 38] if sorted([float(p['a']), float(p['b'])]) in ([90.0, 110.0], [90.0, 120.0]) else ['short_mid', 33]
    return None


CONS = {'kompozytowy': 'kompozyt', 'zintegrowany': 'zintegr'}
RULE_TAG = {'corner': 'N', 'corner_opp': 'N', 'corner_adj': 'N', 'short_mid': 'K', 'long_mid': 'D'}


RF_OBJ = os.path.join(os.path.dirname(ROOT), 'materiały', '008 Modele 3D', 'Regular Flow 3D (Schedline 2025)', 'Regular Flow 3D.obj')


def harmony(prods, out):
    """Odpływy liniowe Harmony: bryła Schedline 2025 „Regular Flow” -> długość, syfon i wykończenie wg rysunków Harmony."""
    import zipfile
    hp = [p for p in prods if p['cat'] == 'odpływ liniowy' and p['fam'] == 'Harmony' and p.get('a')]
    if not hp or not os.path.exists(RF_OBJ):
        print('Harmony: brak produktów albo pliku Regular Flow'); return
    jobs, refs = {}, {}
    for p in hp:
        prime = 'Prime' in p['s']; black = (p.get('c') == 'czarny')
        L = int(round(float(p['a']) * 10))
        key = 'Schedpol_Harmony%s%s_%d' % ('-Prime' if prime else '', '-Black' if black else '', L)
        jobs[key] = {'obj': RF_OBJ, 'glb': os.path.join(OUT, key + '.glb'), 'objout': os.path.join(OUT, key + '.obj'),
                     'L': L, 'prime': prime, 'black': black}
        refs[p['ref']] = key
    jf = os.path.join(OUT, '_jobs_h.json'); rf = os.path.join(OUT, '_pomiar_h.json')
    json.dump(jobs, open(jf, 'w', encoding='utf-8'))
    subprocess.run([BLENDER, '-b', '--factory-startup', '--python', os.path.join(HERE, '10d_blender_odplyw.py'), '--', jf, rf], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    meas = json.load(open(rf, encoding='utf-8')); os.remove(jf)
    shutil.copy2(rf, os.path.join(HERE, 'harmony3d_log.json')); os.remove(rf)
    files = {}
    for key, J in jobs.items():
        if 'err' in meas.get(key, {'err': 1}) or not os.path.exists(J['glb']):
            print('  BŁĄD Harmony', key, meas.get(key)); continue
        zp = os.path.join(OUT, key + '.obj.zip')
        with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            z.write(J['objout'], key + '.obj')
        os.remove(J['objout'])
        files[key] = [{'ext': 'OBJ', 'f': key + '.obj.zip', 'kb': os.path.getsize(zp) // 1024, 'zip': 1},
                      {'ext': 'GLB', 'f': key + '.glb', 'kb': os.path.getsize(J['glb']) // 1024, 'view': 1}]
    for ref, key in refs.items():
        if key not in files: continue
        dm = meas[key]['dims_mm']
        out[ref] = {'src': 'Schedline 2025 · Regular Flow', 'dims': [round(dm[0] / 10, 1), round(dm[1] / 10, 1), round(dm[2] / 10, 1)],
                    'files': files[key],
                    'note': 'bryła Regular Flow (Schedline 2025): długość, położenie syfonu i wykończenie wg rysunku technicznego Harmony'}
    print('Harmony: modeli', len(files), 'indeksów', len([r for r in refs if refs[r] in files]))



def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):                     # czyść zawartość (katalog bywa zablokowany przez inny proces)
        os.remove(os.path.join(OUT, f))
    data = json.loads(open(os.path.join(ROOT, 'assets', 'data.js'), encoding='utf-8').read().split('=', 1)[1].split(';\n')[0])
    prods = data['products']
    cats = {}
    def cat(folder):
        if folder not in cats: cats[folder] = catalog(folder)
        return cats[folder]

    models, refs, miss, approx = {}, {}, [], {}
    for p in prods:
        size = None
        if p['fam'] in SERIES and p.get('a') and p.get('b'):
            folders = SERIES[p['fam']]
            stone = 'kamień' in (p.get('c') or '') or 'kamien' in (p.get('c') or '')
            folder = folders[1] if stone and len(folders) > 1 else folders[0]
            want = sorted([float(p['a']), float(p['b'])], reverse=True)
            shp = p.get('shape') if p.get('shape') in ('półokrągły', 'pięciokątny') else None
            try:
                h = float(str(p.get('h') or '0').split('/')[0].replace(',', '.'))
            except ValueError:
                h = 0
            cand = [m for m in cat(folder) if m['dims'] and abs(m['dims'][0] - want[0]) <= 0.6 and abs(m['dims'][1] - want[1]) <= 0.6 and m['shape'] == shp]
            if p['fam'] not in ('Grawello', 'Dante', 'Go Baby', 'Dafne') and h:
                cand = [m for m in cand if abs(m['dims'][2] - h) <= H_TOL]
            near = False
            if not cand:                       # brak wymiaru -> najbliższy wymiar, ten sam kształt, przeskalowany do wymiaru produktu
                pool = [m for f in ([folder] + [x for x in folders if x != folder]) for m in cat(f) if m['dims'] and m['shape'] == shp]
                if p['fam'] not in ('Grawello', 'Dante', 'Go Baby', 'Dafne') and h:
                    pool = [m for m in pool if abs(m['dims'][2] - h) <= H_TOL]
                if not pool:
                    miss.append('%s %s %s %s×%s×%s' % (p['ref'], p['fam'], p.get('shape'), p['a'], p['b'], p.get('h'))); continue
                # zamiennik o proporcjach boków jak najbliższych (skalowanie zachowa kształt rantu)
                cand = [min(pool, key=lambda m: ((m['dims'][0] - want[0]) ** 2 + (m['dims'][1] - want[1]) ** 2 +
                                                 400 * (m['dims'][0] / m['dims'][1] - want[0] / want[1]) ** 2,
                                                 folders.index(next(f for f in folders if m['obj'].startswith(os.path.join(SRC, f))))))]
                near = True
            m = sorted(cand, key=lambda m: abs(m['dims'][2] - h))[0]
            if near:
                approx[p['ref']] = m['dims']
                size = want
            rule = drain_rule(p) if p['cat'] == 'brodzik' else None
            cons = CONS.get(p.get('tech')) if p['cat'] == 'brodzik' else None
        elif p['s'] in PANELS:
            size_ = '90' if p['ref'] in ('42303401', '43217391', '44178281', '44516283') else '80'
            m = next((m for m in cat(PANELS[p['s']]) if m['stem'].startswith(size_)), None)
            if not m:
                miss.append(p['ref'] + ' ' + p['s']); continue
            rule = cons = None
        else:
            continue
        dims = list(size) + [m['dims'][2]] if size else m['dims']
        tag = '-R55' if m['shape'] == 'półokrągły' else ('-5k' if m['shape'] == 'pięciokątny' else '')
        if rule: tag += '-o' + RULE_TAG[rule[0]]
        key = '%s_%s_%gx%gx%g%s' % (p['brand'], (p['s'] if p['s'] in PANELS else p['fam']).replace(' ', '-'), dims[0], dims[1], dims[2], tag)
        key = key.replace('.', ',')
        models.setdefault(key, {'obj': m['obj'], 'src': os.path.relpath(m['obj'], SRC).split(os.sep)[0].split('. ', 1)[1] + ' · ' + m['stem'],
                                'dims': dims, 'refs': [], 'size': size, 'rule': rule, 'cons': cons})
        models[key]['refs'].append(p['ref'])
        refs[p['ref']] = key

    jobs = {}
    for key, m in models.items():
        jobs[key] = {'obj': m['obj'], 'glb': os.path.join(OUT, key + '.glb'), 'metal': key.split('_')[1] != 'Magnetic',
                     'size': m['size'], 'rule': m['rule'], 'cons': m['cons'], 'objout': os.path.join(OUT, key + '.obj'), 'fam': key.split('_')[1]}
    jf = os.path.join(OUT, '_jobs.json'); rf = os.path.join(OUT, '_pomiar.json')
    json.dump(jobs, open(jf, 'w', encoding='utf-8'))
    subprocess.run([BLENDER, '-b', '--factory-startup', '--python', os.path.join(HERE, '10b_blender_brodzik.py'), '--', jf, rf], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    meas = json.load(open(rf, encoding='utf-8')); os.remove(jf)
    shutil.copy2(rf, os.path.join(HERE, 'modele3d_log.json')); os.remove(rf)
    import zipfile
    for key, m in models.items():
        r = meas.get(key, {})
        files = []
        fixed = r.get('modified')
        if fixed:                       # poprawiona bryła -> tylko poprawiony OBJ (DWG/3DS z katalogu miałyby stary odpływ/wymiar)
            src = os.path.join(OUT, key + '.obj')
            zp = os.path.join(OUT, key + '.obj.zip')
            with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
                z.write(src, key + '.obj')
            os.remove(src)
            files.append({'ext': 'OBJ', 'f': key + '.obj.zip', 'kb': os.path.getsize(zp) // 1024, 'zip': 1})
        else:
            if os.path.exists(os.path.join(OUT, key + '.obj')): os.remove(os.path.join(OUT, key + '.obj'))
            for ext in ('dwg', 'obj', '3ds'):
                src = m['obj'] if ext == 'obj' else sibling(m['obj'], ext)
                if src and ext == 'obj':
                    zp = os.path.join(OUT, key + '.obj.zip')
                    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
                        z.write(src, key + '.obj')
                    files.append({'ext': 'OBJ', 'f': key + '.obj.zip', 'kb': os.path.getsize(zp) // 1024, 'zip': 1})
                elif src:
                    shutil.copy2(src, os.path.join(OUT, key + '.' + ext))
                    files.append({'ext': ext.upper(), 'f': key + '.' + ext, 'kb': os.path.getsize(src) // 1024})
        if os.path.exists(os.path.join(OUT, key + '.glb')):
            files.append({'ext': 'GLB', 'f': key + '.glb', 'kb': os.path.getsize(os.path.join(OUT, key + '.glb')) // 1024, 'view': 1})
        m['files'] = files; m['fixed'] = fixed
    out = {}
    for ref, key in refs.items():
        m = models[key]
        out[ref] = {'src': '2021 · ' + m['src'], 'dims': m['dims'], 'files': m['files']}
        if ref in approx:
            out[ref]['approx'] = 1; out[ref]['from'] = approx[ref]
        if m.get('fixed'):
            out[ref]['fix'] = 1
    harmony(prods, out)
    js = ('/* Modele 3D przypisane do indeksów LM — generuje _narzedzia/10_modele_3d.py (+10b_blender_brodzik.py) z paczki „008 Modele 3D”.\n'
          '   Bryły z katalogu Schedpol 2021, poprawione: wymiar produktu, położenie odpływu wg rysunku technicznego, spód wg konstrukcji. */\n'
          'window.SP = window.SP || {};\nwindow.SP.cad = ' + json.dumps(out, ensure_ascii=False) + ';\n')
    open(os.path.join(ROOT, 'assets', 'modele3d.js'), 'w', encoding='utf-8').write(js)
    errs = {k: v for k, v in meas.items() if 'err' in v}
    print('indeksów z modelem:', len(out), ' unikalnych brył:', len(models), ' poprawionych:', sum(1 for m in models.values() if m.get('fixed')),
          ' błędów:', len(errs))
    for k, v in errs.items(): print('  BŁĄD', k, v['err'], v.get('tb', '')[-300:])
    print('bez modelu w paczce (%d)' % len(miss))


if __name__ == '__main__':
    main()

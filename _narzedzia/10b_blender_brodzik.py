# -*- coding: utf-8 -*-
"""Część Blendera dla 10_modele_3d.py (tryb wsadowy): OBJ z katalogu -> GLB dla portalu (+ poprawiony OBJ).

Dla każdego zadania:
  1. import, rozdzielenie luźnych części, usunięcie kratek/akcesoriów leżących obok bryły;
  2. dopasowanie wymiaru (model zastępczy -> wymiar produktu; części odpływu przesuwane, nie rozciągane);
  3. odpływ w położeniu z rysunku technicznego produktu (zalepienie starego otworu + przeniesienie maskownicy);
  4. spód wg konstrukcji: kompozytowy = pełny, płaski, czarna mata + otwór odpływowy;
     zintegrowany = rama skorupy, nośnik EPS z wycięciem i kanałami, otwór odpływowy w skorupie;
  5. materiały (zmienia kolor tylko „akryl”), UV, skala cm -> m, eksport GLB (Draco) i OBJ (cm), jeśli zmieniony.
Uruchom: blender -b --factory-startup --python 10b_blender_brodzik.py -- zadania.json wynik.json
"""
import json, math, sys
import bpy, bmesh, mathutils
from mathutils import Vector
from mathutils.bvhtree import BVHTree

args = sys.argv[sys.argv.index('--') + 1:]
jobs = json.load(open(args[0], encoding='utf-8'))
res = {}


# ---------- geometria 2D ----------
def hull2d(pts):
    pts = sorted(set((round(x, 1), round(y, 1)) for x, y in pts))
    if len(pts) < 3: return pts
    def cr(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 1e-6: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 1e-6: up.pop()
        up.append(p)
    H = lo[:-1] + up[:-1]
    out = []
    for p in H:                                   # usuń punkty zbyt bliskie (< 0,8 cm)
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 0.8: out.append(p)
    if len(out) > 3 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) < 0.8: out.pop()
    return out                                    # CCW


def inside(p, H):
    for i in range(len(H)):
        a, b = H[i], H[(i + 1) % len(H)]
        if (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) < -1e-6: return False
    return True


def dist_hull(p, H):
    best = 1e9
    for i in range(len(H)):
        a, b = H[i], H[(i + 1) % len(H)]
        ax, ay = b[0] - a[0], b[1] - a[1]
        L = ax * ax + ay * ay or 1e-9
        t = max(0, min(1, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / L))
        best = min(best, math.hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay))
    return best


def inset(H, d):
    n = len(H); lines = []
    for i in range(n):
        a, b = H[i], H[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1e-9
        nx, ny = -dy / L, dx / L                      # normalna do środka (CCW)
        lines.append(((a[0] + nx * d, a[1] + ny * d), (dx / L, dy / L)))
    out = []
    for i in range(n):
        (p1, d1), (p2, d2) = lines[i - 1], lines[i]
        den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 1e-4:
            out.append(p2)
        else:
            t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
            out.append((p1[0] + d1[0] * t, p1[1] + d1[1] * t))
    return out


# ---------- materiały ----------
def material(name, rgb, rough, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    m.diffuse_color = (*rgb, 1)                         # kolor w podglądzie Workbench (rendery kontrolne 10c)
    return m


def new_obj(name, bm, mats):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    for m in mats: o.data.materials.append(m)
    return o


def disc(bm, cx, cy, z, r0, r1, mi, down=True, n=40):
    """Pierścień (r0 > 0) albo dysk (r0 = 0) w płaszczyźnie z; down=True -> normalna w dół."""
    out = [bm.verts.new((cx + r1 * math.cos(2 * math.pi * k / n), cy + r1 * math.sin(2 * math.pi * k / n), z)) for k in range(n)]
    if r0 <= 0:
        f = bm.faces.new(out[::-1] if down else out); f.material_index = mi; return
    inn = [bm.verts.new((cx + r0 * math.cos(2 * math.pi * k / n), cy + r0 * math.sin(2 * math.pi * k / n), z)) for k in range(n)]
    for k in range(n):
        q = [out[k], out[(k + 1) % n], inn[(k + 1) % n], inn[k]]
        f = bm.faces.new(q[::-1] if down else q); f.material_index = mi


def poly_face(bm, P, z, mi, down):
    vs = [bm.verts.new((x, y, z)) for x, y in P]
    f = bm.faces.new(vs[::-1] if down else vs); f.material_index = mi
    return vs


def strip(bm, A, B, mi, flip=False):
    """Pas czworokątów między dwiema pętlami wierzchołków o tej samej liczbie punktów."""
    n = len(A)
    for k in range(n):
        q = [A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]]
        f = bm.faces.new(q[::-1] if flip else q); f.material_index = mi


def bbox(objs):
    mn = Vector((1e9,) * 3); mx = -mn
    for o in objs:
        for v in o.data.vertices:
            mn = Vector(map(min, mn, v.co)); mx = Vector(map(max, mx, v.co))
    return mn, mx


for key, J in jobs.items():
    log = []
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.wm.obj_import(filepath=J['obj'])
        objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        bpy.ops.object.select_all(action='SELECT')
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        if len(objs[0].data.vertices) < 400000:
            bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.separate(type='LOOSE'); bpy.ops.object.mode_set(mode='OBJECT')
        objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']

        def area(o):
            a, b = bbox([o]); d = sorted(b - a); return d[1] * d[2]
        big = max(objs, key=area)
        bmn, bmx = bbox([big])
        for o in list(objs):
            a, b = bbox([o]); c = (a + b) / 2
            if any(c[i] < bmn[i] - 1 or c[i] > bmx[i] + 1 for i in range(3)):
                bpy.data.objects.remove(o, do_unlink=True); objs.remove(o)
        # środek obrysu w (0,0), spód z = 0
        mn, mx = bbox(objs); c = (mn + mx) / 2
        for o in objs:
            o.data.transform(mathutils.Matrix.Translation((-c.x, -c.y, -mn.z)))
        barea = area(big)
        smalls = [o for o in objs if o is not big and area(o) < barea * 0.06]
        mn, mx = bbox([big]); H0 = mx.z - mn.z
        modified = False

        # --- 2. wymiar produktu (model zastępczy) ---
        if J.get('size'):
            Lx, Ly = mx.x - mn.x, mx.y - mn.y
            A, B = sorted(J['size'], reverse=True)
            tx, ty = (A, B) if Lx >= Ly else (B, A)
            sx, sy = tx / Lx, ty / Ly
            if abs(sx - 1) > 0.01 or abs(sy - 1) > 0.01:
                big.data.transform(mathutils.Matrix.Diagonal((sx, sy, 1, 1)))
                for o in objs:
                    if o is big: continue
                    a, b = bbox([o]); cc = (a + b) / 2
                    o.data.transform(mathutils.Matrix.Translation((cc.x * (sx - 1), cc.y * (sy - 1), 0)))
                modified = True; log.append('wymiar %.0fx%.0f -> %.0fx%.0f' % (Lx, Ly, tx, ty))
        mn, mx = bbox([big])
        bm = bmesh.new(); bm.from_mesh(big.data)
        H = hull2d([(v.co.x, v.co.y) for v in bm.verts])

        # --- 3. odpływ ---
        drain = None
        if smalls:
            main = max(smalls, key=area)
            a, b = bbox([main]); drain = Vector(((a.x + b.x) / 2, (a.y + b.y) / 2))
            half = max(b.x - a.x, b.y - a.y) / 2
        rule = J.get('rule')
        if rule and drain is not None:
            kind, off = rule
            x0, y0, x1, y1 = mn.x, mn.y, mx.x, mx.y
            corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            cut = [i for i, p in enumerate(corners) if not inside((p[0] + (9 if p[0] < 0 else -9), p[1] + (9 if p[1] < 0 else -9)), H)]   # ścięty/łukowy narożnik (nie zaokrąglenie)
            def inner(i): p = corners[i]; return (p[0] + (off if p[0] < 0 else -off), p[1] + (off if p[1] < 0 else -off))
            if kind == 'corner':
                cand = [inner(i) for i in range(4) if i not in cut]
            elif kind == 'corner_opp':
                cand = [inner((cut[0] + 2) % 4)] if cut else [inner(i) for i in range(4)]
            elif kind == 'corner_adj':
                cand = [inner((cut[0] + 1) % 4), inner((cut[0] + 3) % 4)] if cut else [inner(i) for i in range(4)]
            else:
                longx = (x1 - x0) >= (y1 - y0)
                if (kind == 'short_mid') == longx:   # środek krótszego boku przy osi x / dłuższego przy osi y
                    cand = [(x0 + off, 0.0), (x1 - off, 0.0)]
                else:
                    cand = [(0.0, y0 + off), (0.0, y1 - off)]
            t = Vector(min(cand, key=lambda q: (q[0] - drain.x) ** 2 + (q[1] - drain.y) ** 2))
            if (t - drain).length > 3.5:
                tree = BVHTree.FromBMesh(bm)
                def zat(p):
                    hit = tree.ray_cast(Vector((p[0], p[1], mx.z + 20)), Vector((0, 0, -1)))
                    return hit[0].z if hit[0] else None
                R = max(4.0, min(11.0, max(half * 1.42 + 1.5, 0 if J.get('cons') == 'kompozyt' else 8.0)))   # z lejkiem wokół odpływu
                dirc = Vector((-drain.x, -drain.y)); dirc = dirc.normalized() if dirc.length > 0.1 else Vector((1, 0))
                zf = zat(drain + dirc * (R + 1.5))
                mv = [o for o in smalls if (lambda a, b: (Vector(((a.x + b.x) / 2, (a.y + b.y) / 2)) - drain).length)(*bbox([o])) < 12]
                zmv = min(bbox([o])[0].z for o in mv)
                kill = []
                for f in bm.faces:
                    cc = f.calc_center_median()
                    if (Vector((cc.x, cc.y)) - drain).length > R or cc.z < 0.6: continue
                    if cc.z < zf - 0.3 or (abs(f.normal.z) > 0.9 and abs(cc.z - zf) < 1.2):
                        kill.append(f)
                kv = set(v for f in kill for v in f.verts)
                bmesh.ops.delete(bm, geom=kill, context='FACES_ONLY')
                bm.verts.ensure_lookup_table()
                for v in [v for v in bm.verts if not v.link_faces]: bm.verts.remove(v)
                bnd = [e for e in bm.edges if len(e.link_faces) == 1 and e.verts[0] in kv and e.verts[1] in kv]
                r = bmesh.ops.holes_fill(bm, edges=bnd, sides=0)
                bmesh.ops.triangulate(bm, faces=r['faces'])
                for f in bm.faces: pass
                tree = BVHTree.FromBMesh(bm)
                znew = zat(t)
                ctop = max(bbox([o])[1].z for o in mv)          # wierzch maskownicy względem posadzki wokół starego odpływu
                dz = ((znew + max(ctop - zf, 0.05)) - ctop) if (znew is not None and zf is not None) else 0.0
                d = t - drain
                for o in mv:
                    o.data.transform(mathutils.Matrix.Translation((d.x, d.y, dz)))
                log.append('odpływ (%.1f, %.1f) -> (%.1f, %.1f)' % (drain.x, drain.y, t.x, t.y))
                drain = t; modified = True
        bm.normal_update()

        # --- 3b. Balans: maskownica od nowa (3 równe szczeliny), posadzka pod nią wyrównana, płytka ponad najwyższym punktem ---
        if J.get('fam') == 'Balans' and drain is not None and smalls:
            mv = [o for o in smalls if (lambda a, b: (Vector(((a.x + b.x) / 2, (a.y + b.y) / 2)) - drain).length)(*bbox([o])) < 12]
            a0, b0 = bbox([max(mv, key=area)])
            S = max(b0.x - a0.x, b0.y - a0.y)
            for o in mv:
                objs.remove(o); smalls.remove(o); bpy.data.objects.remove(o, do_unlink=True)
            tree = BVHTree.FromBMesh(bm)
            def zat2(x, y):
                hit = tree.ray_cast(Vector((x, y, mx.z + 20)), Vector((0, 0, -1))); return hit[0].z if hit[0] else None
            h2 = S / 2 + 1.2
            zf = max(z for z in [zat2(drain.x + dx, drain.y + dy) for dx, dy in ((h2 + 1.5, 0), (-h2 - 1.5, 0), (0, h2 + 1.5), (0, -h2 - 1.5))] if z is not None)
            kill = []
            for f in bm.faces:
                cc = f.calc_center_median()
                if max(abs(cc.x - drain.x), abs(cc.y - drain.y)) > h2 or cc.z < 0.6: continue
                if cc.z < zf - 0.25 or (abs(f.normal.z) > 0.9 and abs(cc.z - zf) < 1.2): kill.append(f)
            if kill:
                kv = set(v for f in kill for v in f.verts)
                bmesh.ops.delete(bm, geom=kill, context='FACES_ONLY')
                for v in [v for v in bm.verts if not v.link_faces]: bm.verts.remove(v)
                bnd = [e for e in bm.edges if len(e.link_faces) == 1 and e.verts[0] in kv and e.verts[1] in kv]
                r = bmesh.ops.holes_fill(bm, edges=bnd, sides=0)
                bmesh.ops.triangulate(bm, faces=r['faces'])
            tree = BVHTree.FromBMesh(bm)
            zs = [z for z in [zat2(drain.x + dx * S / 2, drain.y + dy * S / 2) for dx in (-1, 0, 1) for dy in (-1, 0, 1)] if z is not None]
            ztop = max(zs) + 0.12; zbot = min(zs) - 0.3
            cb = bmesh.new()
            bmesh.ops.create_cube(cb, size=1.0, matrix=mathutils.Matrix.Translation((drain.x, drain.y, (ztop + zbot) / 2)) @ mathutils.Matrix.Diagonal((S, S, ztop - zbot, 1)))
            cov = new_obj('maskownica', cb, [])
            sb = bmesh.new()
            L, Wd, gap = 0.62 * S, 0.42, 1.15                     # 3 równe szczeliny, równoległe do osi x
            for k in (-1, 0, 1):
                bmesh.ops.create_cube(sb, size=1.0, matrix=mathutils.Matrix.Translation((drain.x, drain.y + k * gap, ztop)) @ mathutils.Matrix.Diagonal((L, Wd, 0.7, 1)))
            cut = new_obj('szczeliny', sb, [])
            mats_tmp = material('otwor', (0.015, 0.015, 0.015), 0.6)
            cut.data.materials.append(mats_tmp)
            mod = cov.modifiers.new('slots', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = cut; mod.solver = 'EXACT'
            try: mod.material_mode = 'TRANSFER'
            except Exception: pass
            cov.data.materials.append(material('metal', (0.62, 0.64, 0.66), 0.28, 1.0))
            bpy.context.view_layer.objects.active = cov
            with bpy.context.temp_override(object=cov, active_object=cov):
                bpy.ops.object.modifier_apply(modifier='slots')
            bpy.data.objects.remove(cut, do_unlink=True)
            cov['keep_mat'] = 1
            log.append('maskownica Balans: 3 równe szczeliny, wierzch %.2f cm' % ztop)
            bm.normal_update()

        # --- 4. spód ---
        cons = J.get('cons')
        mats = {'akryl': material('akryl', (0.93, 0.93, 0.92), 0.45), 'metal': material('metal', (0.62, 0.64, 0.66), 0.28, 1.0),
                'mata': material('mata', (0.03, 0.03, 0.03), 0.85), 'otwor': material('otwor', (0.015, 0.015, 0.015), 0.6),
                'spod': material('spod', (0.78, 0.74, 0.56), 0.75), 'styropian': material('styropian', (0.95, 0.95, 0.93), 0.95),
                'plastik': material('plastik', (0.90, 0.90, 0.89), 0.4)}
        dpos = drain if drain is not None else Vector((0, 0))
        if cons == 'kompozyt':
            kill = [f for f in bm.faces if f.normal.z < -0.6 and f.calc_center_median().z < 0.8]
            bmesh.ops.delete(bm, geom=kill, context='FACES_ONLY')
            nb = bmesh.new()
            poly_face(nb, H, 0.0, 0, True)                                   # czarna mata — pełny, płaski spód
            disc(nb, dpos.x, dpos.y, -0.03, 3.4, 4.8, 1)                     # pierścień otworu odpływowego
            disc(nb, dpos.x, dpos.y, -0.02, 0, 3.4, 2)
            new_obj('spod_mata', nb, [mats['mata'], mats['metal'], mats['otwor']])
            if not J.get('metal') and smalls:          # maskownica w kolorze brodzika (Magnetic): widoczna szczelina wokół
                cm, cx = bbox([max(smalls, key=area)])
                g = bmesh.new(); zt = cx.z + 0.02; w = 0.3
                P = [(cm.x, cm.y), (cx.x, cm.y), (cx.x, cx.y), (cm.x, cx.y)]
                Q = [(cm.x - w, cm.y - w), (cx.x + w, cm.y - w), (cx.x + w, cx.y + w), (cm.x - w, cx.y + w)]
                strip(g, [g.verts.new((x, y, zt)) for x, y in Q], [g.verts.new((x, y, zt)) for x, y in P], 0)
                new_obj('szczelina', g, [mats['otwor']])
            log.append('spód kompozytowy')
        elif cons == 'zintegr':
            hc = min(max(0.5 * H0, 2.5), 7.0)
            kill = [f for f in bm.faces if f.calc_center_median().z < hc - 0.01 and dist_hull(tuple(f.calc_center_median())[:2], H) > 1.2]
            bmesh.ops.delete(bm, geom=kill, context='FACES_ONLY')
            for o in list(objs):
                if o is not big and bbox([o])[1].z < hc:
                    bpy.data.objects.remove(o, do_unlink=True); objs.remove(o)
            W = inset(H, 1.5)
            nb = bmesh.new()
            outer = [nb.verts.new((x, y, 0.0)) for x, y in H]
            in0 = [nb.verts.new((x, y, 0.0)) for x, y in W]
            inc = [nb.verts.new((x, y, hc)) for x, y in W]
            strip(nb, outer, in0, 0, flip=True)                               # rama skorupy (dół)
            strip(nb, in0, inc, 1, flip=True)                                 # ścianka wnęki
            f = nb.faces.new(inc[::-1]); f.material_index = 1                 # sufit wnęki (spód skorupy)
            disc(nb, dpos.x, dpos.y, hc - 0.06, 3.6, 4.9, 2)                  # króciec odpływu
            disc(nb, dpos.x, dpos.y, hc - 0.05, 0, 3.6, 3)
            o_sp = new_obj('spod_skorupa', nb, [mats['akryl'], mats['spod'], mats['plastik'], mats['otwor']])
            bmesh.ops.recalc_face_normals  # (normalne ustawione ręcznie)
            # nośnik EPS z wycięciem przy odpływie (kanał do krawędzi)
            E = inset(H, 6.0)
            eb = bmesh.new()
            lo = [eb.verts.new((x, y, 0.0)) for x, y in E]
            hi = [eb.verts.new((x, y, hc - 0.08)) for x, y in E]
            eb.faces.new(lo[::-1]); eb.faces.new(hi); strip(eb, lo, hi, 0)
            bmesh.ops.recalc_face_normals(eb, faces=eb.faces[:])
            o_eps = new_obj('nosnik_eps', eb, [mats['styropian']])
            cb = bmesh.new()
            bmesh.ops.create_cone(cb, cap_ends=True, segments=48, radius1=15, radius2=15, depth=40,
                                  matrix=mathutils.Matrix.Translation((dpos.x, dpos.y, hc / 2)))
            o_cut = new_obj('ciecie', cb, [])
            mod = o_eps.modifiers.new('cut', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = o_cut; mod.solver = 'EXACT'
            bpy.context.view_layer.objects.active = o_eps
            with bpy.context.temp_override(object=o_eps, active_object=o_eps):
                bpy.ops.object.modifier_apply(modifier='cut')
            bpy.data.objects.remove(o_cut, do_unlink=True)
            log.append('spód zintegrowany (nośnik %.1f cm)' % hc)
        elif cons == 'lamin':
            # 25.11.2026 — brodzik standardowy (laminowany), wg zdjęć spodu od użytkownika:
            #   płaski (Ipsilon, h < 8 cm): biała płyta wzmacniająca w ramce, otwór odpływu z kołnierzem;
            #   głęboki (Comfo, Dafne): laminat (beżowy, matowy), kołnierz wokół otworu, plastikowa stopka pośrodku.
            #   Kolory ścianek ustawia krok 5 (materiał „laminat”/„plyta” — kolor wariantu go nie zmienia).
            flat = H0 < 8
            tree = BVHTree.FromBMesh(bm)
            def zup(x, y):
                hit = tree.ray_cast(Vector((x, y, -5.0)), Vector((0, 0, 1)))
                return hit[0].z if hit[0] else None
            nb = bmesh.new()
            if flat:
                disc(nb, dpos.x, dpos.y, -0.03, 3.6, 5.4, 0)                      # kołnierz otworu (plastik)
                disc(nb, dpos.x, dpos.y, -0.02, 0, 3.6, 1)                        # otwór
                new_obj('spod_odplyw', nb, [mats['plastik'], mats['otwor']])
                log.append('spód standardowy płaski (płyta)')
            else:
                zr = [z for z in (zup(dpos.x + dx, dpos.y + dy) for dx, dy in ((7, 0), (-7, 0), (0, 7), (0, -7))) if z is not None and z > 1]
                if zr:
                    disc(nb, dpos.x, dpos.y, min(zr) - 0.05, 3.7, 5.6, 0)         # kołnierz otworu pod skorupą
                fam = J.get('fam')
                # środek ciężkości obrysu (dla brodzika półokrągłego środek bryły, nie prostokąta otaczającego)
                A2 = cx0 = cy0 = 0.0
                for i in range(len(H)):
                    (x1, y1), (x2, y2) = H[i], H[(i + 1) % len(H)]
                    cr_ = x1 * y2 - x2 * y1; A2 += cr_; cx0 += (x1 + x2) * cr_; cy0 += (y1 + y2) * cr_
                cx0, cy0 = cx0 / (3 * A2), cy0 / (3 * A2)
                if (Vector((cx0, cy0)) - dpos).length < 12:                      # podpora nie na odpływie
                    cx0, cy0 = cx0 - (dpos.x - cx0) * 0.5, cy0 - (dpos.y - cy0) * 0.5
                zc = zup(cx0, cy0)
                parts = []                                                       # (bmesh, nazwa, materiały)
                def cyl(b, x, y, z0, z1, r0, r1, seg=32):
                    bmesh.ops.create_cone(b, cap_ends=True, segments=seg, radius1=r0, radius2=r1, depth=z1 - z0,
                                          matrix=mathutils.Matrix.Translation((x, y, (z0 + z1) / 2)))
                if fam == 'Comfo' and zc is not None and zc > 3:
                    # 25.11.2026 (zdjęcie od użytkownika): jedna regulowana stopa pośrodku — talerz Ø10 cm z 4 wkrętami,
                    # korpus stożkowy z nakrętką regulacji, podstawa z kołnierzem; sięga od spodu skorupy do posadzki.
                    zt = zc - 0.12
                    lb, mb_ = bmesh.new(), bmesh.new()
                    cyl(lb, cx0, cy0, zt - 0.45, zt, 5.0, 5.0, 40)                   # talerz
                    cyl(lb, cx0, cy0, zt - 1.6, zt - 0.45, 2.0, 3.2)                 # stożek pod talerzem
                    cyl(lb, cx0, cy0, 0.55 * zt, zt - 1.6, 1.7, 1.7)                 # górna tuleja
                    cyl(lb, cx0, cy0, 1.3, 0.45 * zt, 2.1, 1.6)                      # korpus dolny (żebrowany na zdjęciu)
                    cyl(lb, cx0, cy0, 0.0, 1.3, 3.6, 3.6, 40)                        # podstawa z kołnierzem
                    cyl(mb_, cx0, cy0, 0.45 * zt, 0.55 * zt, 2.3, 2.3, 6)           # nakrętka regulacji (sześciokąt)
                    for k in range(4):                                             # wkręty w talerzu
                        a = math.pi / 4 + k * math.pi / 2
                        cyl(mb_, cx0 + 3.6 * math.cos(a), cy0 + 3.6 * math.sin(a), zt - 0.45 - 0.01, zt - 0.2, 0.35, 0.35, 12)
                    parts += [(lb, 'stopa_comfo', [mats['plastik']]), (mb_, 'stopa_comfo_metal', [mats['metal']])]
                    log.append('Comfo: stopa regulowana %.1f cm' % zt)
                elif fam == 'Dafne':
                    # 25.11.2026 — stelaż montażowy wg rysunku technicznego Dafne (wymiary w mm dla 800; 900 proporcjonalnie):
                    # dwie szyny równoległe, końce szyny 1: (460,73)→(678,458), szyny 2: (61,350)→(283,735) w układzie
                    # u = bok, przy którego końcu leży odpływ, v = drugi bok, początek w narożniku prostym; 4 nogi na końcach szyn,
                    # wysokość całkowita z nogami 350 mm (brodzik 230 + 35 rant) -> nogi ok. 12 cm pod spodem.
                    x0, y0, x1, y1 = mn.x, mn.y, mx.x, mx.y
                    C4 = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
                    cut = [i for i, p in enumerate(C4) if not inside((p[0] + (9 if p[0] < 0 else -9), p[1] + (9 if p[1] < 0 else -9)), H)]
                    qi = (cut[0] + 2) % 4 if cut else 0
                    Q = Vector(C4[qi]); A_ = Vector(C4[(qi + 1) % 4]) - Q; B_ = Vector(C4[(qi + 3) % 4]) - Q
                    eu, ev = A_.normalized(), B_.normalized()
                    if (dpos - Q).dot(ev) > (dpos - Q).dot(eu): eu, ev = ev, eu  # u = bok, wzdłuż którego odpływ jest dalej od narożnika
                    sc_ = (x1 - x0) / 80.0 / 10.0                                  # mm rysunku -> cm modelu
                    def P(u, v): return Q + eu * (u * sc_) + ev * (v * sc_)
                    rb, fb = bmesh.new(), bmesh.new()
                    for (u0, v0, u1, v1) in ((460, 73, 678, 458), (61, 350, 283, 735)):
                        a, b = P(u0, v0), P(u1, v1); d = b - a; L = d.length; ang = math.atan2(d.y, d.x); m_ = (a + b) / 2
                        bmesh.ops.create_cube(rb, size=1.0, matrix=mathutils.Matrix.Translation((m_.x, m_.y, -1.0)) @ mathutils.Matrix.Rotation(ang, 4, 'Z')
                                              @ mathutils.Matrix.Diagonal((L + 2.0, 3.0, 2.0, 1)))   # ceownik 30×20 mm
                        for t in (a + d.normalized() * 1.5, b - d.normalized() * 1.5):            # nogi przy końcach szyny
                            cyl(rb, t.x, t.y, -5.5, -2.0, 0.5, 0.5, 12)                        # pręt gwintowany
                            cyl(rb, t.x, t.y, -2.25, -1.95, 0.9, 0.9, 6)                       # nakrętka pod szyną
                            cyl(fb, t.x, t.y, -10.5, -5.5, 1.9, 1.3)                           # noga (stożek)
                            cyl(fb, t.x, t.y, -12.0, -10.5, 2.9, 2.9, 32)                      # stopka
                    parts += [(rb, 'stelaz_szyny', [mats['metal']]), (fb, 'stelaz_nogi', [mats['plastik']])]
                    log.append('Dafne: stelaż 2 szyny + 4 nogi (rysunek)')
                elif zc is not None and zc > 2:
                    hf = min(2.0, zc - 0.5)
                    bmesh.ops.create_cone(nb, cap_ends=True, segments=40, radius1=3.0, radius2=3.4, depth=hf,
                                          matrix=mathutils.Matrix.Translation((cx0, cy0, zc - hf / 2 - 0.12)))   # wierzch pod skorupą (nie przebija na wierzch)
                    disc(nb, cx0, cy0, zc - hf - 0.01, 0, 0.9, 1, n=24)               # gniazdo śruby stopki
                    log.append('stopka %.1f cm pod skorupą' % hf)
                for f in nb.faces:
                    if f.material_index not in (0, 1): f.material_index = 0
                o = new_obj('spod_stopka', nb, [mats['plastik'], mats['otwor']])
                o['keep_mat'] = 1
                for b_, nm, ms in parts:
                    po = new_obj(nm, b_, ms); po['keep_mat'] = 1
                if fam == 'Comfo':
                    # wypustki antypoślizgowe na dnie (rysunek i packshot Comfo): owalne, ok. 22×12 mm, siatka ukośna co ok. 11,6 cm
                    def zdn(x, y):
                        hit = tree.ray_cast(Vector((x, y, mx.z + 20)), Vector((0, 0, -1)))
                        return (hit[0].z, hit[1]) if hit[0] else (None, None)
                    zfl, _ = zdn(cx0, cy0)
                    wb = bmesh.new(); nw = 0
                    a1 = math.radians(-14); a2 = math.radians(76); pitch = 11.6
                    e1 = Vector((math.cos(a1), math.sin(a1))); e2 = Vector((math.cos(a2), math.sin(a2)))
                    rng = int((mx.x - mn.x) / pitch) + 3
                    for i in range(-rng, rng + 1):
                        for k in range(-rng, rng + 1):
                            q = Vector((cx0, cy0)) + e1 * (i * pitch) + e2 * (k * pitch) + e1 * (pitch / 2 if k % 2 else 0) * 0
                            if not inside((q.x, q.y), H) or dist_hull((q.x, q.y), H) < 12.5 or (q - dpos).length < 9: continue
                            z, nrm = zdn(q.x, q.y)
                            if z is None or zfl is None or abs(z - zfl) > 0.9: continue
                            g = bmesh.new()
                            bmesh.ops.create_uvsphere(g, u_segments=20, v_segments=8, radius=1.0)
                            for v in g.verts:
                                if v.co.z < 0: v.co.z = 0.0
                            bm_m = mathutils.Matrix.Translation((q.x, q.y, z - 0.02)) @ mathutils.Matrix.Rotation(math.radians(48), 4, 'Z') @ mathutils.Matrix.Diagonal((1.2, 0.65, 0.4, 1))
                            bmesh.ops.transform(g, matrix=bm_m, verts=g.verts)
                            me_ = bpy.data.meshes.new('w'); g.to_mesh(me_); g.free(); wb.from_mesh(me_); bpy.data.meshes.remove(me_)
                            nw += 1
                    if nw:
                        wo = new_obj('wypustki', wb, [mats['akryl']])
                        log.append('Comfo: wypustki antypoślizgowe %d szt.' % nw)
                log.append('spód standardowy głęboki (laminat)')
        bm.to_mesh(big.data); bm.free()
        # normalne: usuń zapisane w OBJ (dawały „ducha” starego odpływu), wygładzanie wg kąta
        for o in [o for o in bpy.context.scene.objects if o.type == 'MESH']:
            bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
            try:
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
            except Exception:
                pass
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))

        # --- 5. materiały, UV, eksport ---
        big.data.materials.clear(); big.data.materials.append(mats['akryl'])
        for p in big.data.polygons: p.material_index = 0
        if cons == 'lamin':                       # spód skorupy widoczny od dołu -> laminat / płyta
            flat = H0 < 8
            big.data.materials.append(material('plyta', (0.90, 0.90, 0.88), 0.92) if flat else material('laminat', (0.89, 0.86, 0.79), 0.93))
            bt = bmesh.new(); bt.from_mesh(big.data); bt.faces.ensure_lookup_table(); tr = BVHTree.FromBMesh(bt); bt.free()
            nlam, dup = 0, []
            UP, DN = Vector((0, 0, 1)), Vector((0, 0, -1))
            for p in big.data.polygons:                  # test niezależny od kierunku normalnych (w bryłach 2021 bywają odwrócone)
                n, c = p.normal, p.center
                if flat and dist_hull((c.x, c.y), H) < 1.2: continue             # ramka akrylowa wokół płyty
                if abs(n.z) > 0.5:                       # poziome: pierwsza ściana trafiona promieniem od dołu
                    hit = tr.ray_cast(Vector((c.x, c.y, -10.0)), UP)
                    under = hit[2] == p.index
                else:                                    # pionowe: po stronie środka brodzika otwarta przestrzeń aż do posadzki
                    r = Vector((c.x, c.y)); r = r.normalized() if r.length > 0.1 else Vector((1, 0))
                    q = Vector((c.x - r.x * 0.4, c.y - r.y * 0.4, c.z - 0.05))
                    under = c.z < H0 - 0.8 and tr.ray_cast(q, DN)[0] is None
                if not under: continue
                # skorupa z grubością -> przekoloruj; pojedyncza powierzchnia (ta sama ściana widoczna z wierzchu) -> osobna warstwa 1 mm pod spodem
                if abs(n.z) > 0.5:
                    h = tr.ray_cast(Vector((c.x, c.y, c.z + 0.02)), UP); thick = h[0] is not None and h[3] < 3.0
                    off = Vector((0, 0, -0.1))
                else:
                    h = tr.ray_cast(Vector((c.x + r.x * 0.02, c.y + r.y * 0.02, c.z)), Vector((r.x, r.y, 0))); thick = h[0] is not None and h[3] < 3.0
                    off = Vector((-r.x * 0.1, -r.y * 0.1, 0))
                if thick:
                    p.material_index = 1
                else:
                    dup.append(([big.data.vertices[i].co + off for i in p.vertices]))
                nlam += 1
            if dup:
                lb = bmesh.new()
                for P in dup:
                    try: lb.faces.new([lb.verts.new(v) for v in P])
                    except ValueError: pass
                lo = new_obj('spod_laminat', lb, [big.data.materials[1]]); lo['keep_mat'] = 1
            log.append('laminat/płyta: %d ścian (%d jako warstwa pod skorupą)' % (nlam, len(dup)))
        for o in objs:
            if o is big or o.get('keep_mat'): continue
            o.data.materials.clear()
            o.data.materials.append(mats['metal'] if (J.get('metal') and o in smalls) else mats['akryl'])
        allm = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        if modified and J.get('objout'):
            bpy.ops.object.select_all(action='SELECT')
            for o in allm:
                if o.name.startswith('spod_laminat'): o.select_set(False)   # warstwa koloru tylko dla podglądu GLB, nie do CAD
            bpy.ops.wm.obj_export(filepath=J['objout'], export_selected_objects=True, export_materials=False,
                                  export_uv=False, export_normals=True)
        for o in allm:
            o.data.transform(mathutils.Matrix.Diagonal((0.01, 0.01, 0.01, 1)))   # cm -> m (AR 1:1)
            bmu = bmesh.new(); bmu.from_mesh(o.data)
            uv = bmu.loops.layers.uv.verify()
            for f in bmu.faces:
                n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
                u, v = [i for i in range(3) if i != ax]
                for l in f.loops:
                    l[uv].uv = (l.vert.co[u] / 0.3, l.vert.co[v] / 0.3)
            bmu.to_mesh(o.data); bmu.free()
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.gltf(filepath=J['glb'], export_format='GLB', export_draco_mesh_compression_enable=True,
                                  export_yup=True, export_apply=True)
        mn, mx = bbox(allm)
        res[key] = {'dims': [round(x * 100, 1) for x in (mx - mn)], 'modified': modified, 'log': log,
                    'drain': [round(dpos.x, 1), round(dpos.y, 1)] if drain is not None else None}
        if J.get('png'):
            pass
    except Exception as e:
        import traceback
        res[key] = {'err': repr(e), 'tb': traceback.format_exc()[-600:], 'log': log}
json.dump(res, open(args[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

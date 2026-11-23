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
        for o in objs:
            if o is big or o.get('keep_mat'): continue
            o.data.materials.clear()
            o.data.materials.append(mats['metal'] if (J.get('metal') and o in smalls) else mats['akryl'])
        allm = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        if modified and J.get('objout'):
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.wm.obj_export(filepath=J['objout'], export_selected_objects=False, export_materials=False,
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

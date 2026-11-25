# -*- coding: utf-8 -*-
"""Rendery kontrolne GLB (widok z góry pod kątem i od spodu) — Blender, Workbench.
Uruchom: blender -b --factory-startup --python 10c_render_kontrola.py -- katalog_wyj plik1.glb [plik2.glb ...]"""
import math, os, sys
import bpy, mathutils
args = sys.argv[sys.argv.index('--') + 1:]
outd = args[0]; os.makedirs(outd, exist_ok=True)
for glb in args[1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb)
    for m in bpy.data.materials:                 # kolor podglądu = kolor bazowy materiału (laminat, mata, akryl…)
        bs = m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
        if bs: m.diffuse_color = tuple(bs.inputs['Base Color'].default_value)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'MATERIAL'
    sc.display.shading.show_cavity = True
    sc.render.resolution_x = 640; sc.render.resolution_y = 480
    ms = [o for o in sc.objects if o.type == 'MESH']
    mn = mathutils.Vector((1e9,) * 3); mx = -mn
    for o in ms:
        for c in o.bound_box:
            w = o.matrix_world @ mathutils.Vector(c); mn = mathutils.Vector(map(min, mn, w)); mx = mathutils.Vector(map(max, mx, w))
    ctr = (mn + mx) / 2; R = (mx - mn).length
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = R * 1.15
    for tag, d in (('gora', mathutils.Vector((0.55, -0.9, 1.1))), ('spod', mathutils.Vector((0.35, -0.6, -1.3))), ('plan', mathutils.Vector((0.0, -0.001, 1.0))), ('przod', mathutils.Vector((0.35, -1.0, 0.12)))):
        cam.location = ctr + d.normalized() * R * 2
        cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = os.path.join(outd, os.path.basename(glb)[:-4] + '_' + tag + '.png')
        bpy.ops.render.render(write_still=True)

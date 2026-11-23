"""
Big curved ultrawide monitor for the workstations (40"-class, 21:9, ~1500R curve), original
design: razor-thin bezels, a curved shell with a cyan light ring on the back, a slim arm on a
wide two-prong base, and a soft cyan light bar under the chin. No logos.

    build_dev_monitor(parent=None, name="DevMonitor", screen="code") -> root empty
        screen: "code" (editor + repo, textures/dev_screen_code.png)
                "repo" (repo page + editor, textures/dev_screen_repo.png)
    build_dev_monitor_preview(parent=None, name=...) -> the two variants side by side

Coordinates are three.js style (Y up, screen faces +Z, origin at the centre of the base on the
desk surface) - a drop-in for razer_monitor.build_razer_monitor. The screen mesh is named
"<name>Screen".
"""

import math
import os
import sys

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P  # noqa: E402
from loft_room import block, mat  # noqa: E402

TEX = {
    "code": os.path.join(HERE, "textures", "dev_screen_code.png"),
    "repo": os.path.join(HERE, "textures", "dev_screen_repo.png"),
}

PW, PH = 0.96, 0.41  # visible panel (21:9), 40"-class
RADIUS = 1.6  # ~1600R curve
PY, PZ = 0.315, -0.06  # panel centre height / depth: a short stand, bottom edge ~10 cm off the desk


def _root(name, parent):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    return root


def _screen_mat(kind):
    name = f"Loft_DevScreen_{kind}"
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(TEX[kind], check_existing=True)
    tex.image.pack()
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 1.5
    b.inputs["Roughness"].default_value = 0.25
    return m


def _curved(name, w, h, z_front, m, parent, segs=32, uv=False, depth=0.0, cy=PY):
    """A strip bent round a vertical axis (the 1500R curve), centred at (0, cy); its middle sits
    at z_front and the edges curve toward the viewer. depth > 0 makes it a closed slab."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap") if uv else None
    half = (w / 2) / RADIUS

    def ring(dz):
        top, bot = [], []
        for i in range(segs + 1):
            a = -half + 2 * half * i / segs
            x = RADIUS * math.sin(a)
            z = z_front + dz + RADIUS * (1 - math.cos(a))  # edges come forward
            bot.append(bm.verts.new(P(x, cy - h / 2, z)))
            top.append(bm.verts.new(P(x, cy + h / 2, z)))
        return bot, top

    fb, ft = ring(0.0)
    for i in range(segs):
        f = bm.faces.new((fb[i], fb[i + 1], ft[i + 1], ft[i]))
        if uv:
            u0, u1 = i / segs, (i + 1) / segs
            for loop, (u, v) in zip(f.loops, ((u0, 0), (u1, 0), (u1, 1), (u0, 1))):
                loop[uvl].uv = (u, v)
    if depth > 0:
        bb, bt = ring(-depth)
        for i in range(segs):
            bm.faces.new((bb[i + 1], bb[i], bt[i], bt[i + 1]))
            bm.faces.new((ft[i], ft[i + 1], bt[i + 1], bt[i]))  # top
            bm.faces.new((fb[i + 1], fb[i], bb[i], bb[i + 1]))  # bottom
        bm.faces.new((fb[0], ft[0], bt[0], bb[0]))
        bm.faces.new((ft[-1], fb[-1], bb[-1], bt[-1]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    me.materials.append(m)
    o.parent = parent
    return o


def build_dev_monitor(parent=None, name="DevMonitor", screen="code"):
    SHELL = mat("DevMonShell", "#121318", 0.4, metal=0.3)
    BEZEL = mat("DevMonBezel", "#050506", 0.25)
    METAL = mat("DevMonMetal", "#2a2c33", 0.3, metal=0.85)
    CYAN = mat("DevMonGlow", "#22e4ff", emit="#22e4ff", strength=6.0)
    SCREEN = _screen_mat(screen)

    root = _root(name, parent)

    # wide two-prong base + slim arm up the back
    for s in (-1, 1):
        f = block(f"{name}Prong{s}", (s * 0.13, 0.008, -0.04), (0.26, 0.014, 0.05), METAL, root, r=0.006)
        f.rotation_euler = (0, 0, math.radians(-s * 18))
    block(f"{name}Hub", (0, 0.012, -0.08), (0.09, 0.022, 0.09), METAL, root, r=0.01)
    block(f"{name}Arm", (0, PY / 2 + 0.01, -0.115), (0.06, PY, 0.025), METAL, root, r=0.01)
    block(f"{name}Hinge", (0, PY, -0.105), (0.11, 0.07, 0.05), SHELL, root, r=0.012)

    # curved panel: bezel slab, the screen just in front, the shell behind
    _curved(f"{name}Panel", PW + 0.012, PH + 0.02, PZ, BEZEL, root, depth=0.014, cy=PY)
    _curved(f"{name}Screen", PW - 0.006, PH - 0.006, PZ + 0.0012, SCREEN, root, uv=True, cy=PY + 0.002)
    _curved(f"{name}Shell", PW * 0.72, PH * 0.8, PZ - 0.014, SHELL, root, depth=0.028, cy=PY - 0.005)
    # cyan light ring on the back of the shell + a light bar under the chin
    _curved(f"{name}BackRing", PW * 0.5, 0.012, PZ - 0.0425, CYAN, root, depth=0.003, cy=PY + 0.08)
    _curved(f"{name}BackRing2", PW * 0.5, 0.012, PZ - 0.0425, CYAN, root, depth=0.003, cy=PY - 0.09)
    _curved(f"{name}ChinGlow", PW * 0.6, 0.004, PZ - 0.004, CYAN, root, depth=0.004, cy=PY - PH / 2 - 0.012)
    return root


def build_dev_monitor_preview(parent=None, name="DevMonitorPreview"):
    """Both screen variants side by side (as on the two desks), scaled 2x for the preview."""
    root = _root(name, parent)
    a = build_dev_monitor(root, name + "A", "code")
    a.location = P(-0.53, 0, 0)
    b = build_dev_monitor(root, name + "B", "repo")
    b.location = P(0.53, 0, 0)
    root.scale = (2, 2, 2)
    return root


def build_dev_monitor_single(parent=None, name="DevMonitorSingle"):
    """One monitor at 2x, for the 3/4 and back views."""
    root = _root(name, parent)
    build_dev_monitor(root, name + "M", "code")
    root.scale = (2, 2, 2)
    return root

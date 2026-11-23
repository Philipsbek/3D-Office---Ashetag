"""
Cyberpunk street tree (original design) for the city sidewalks: a slim dark trunk that forks
into three limbs, a low-poly faceted canopy of clustered leaf blobs in deep green / teal, a
string of tiny warm fairy lights wound through the leaves, and a square concrete planter with
a cyan neon lip and a dark grate on top.

Built light on purpose (the city repeats it many times): ~1.5k triangles, everything merged
into a handful of meshes (one per material).

    build_street_tree(parent=None, name="StreetTree", seed=1, height=5.2) -> root

Coordinates are three.js style (Y up, origin at the centre of the planter's base).
"""

import math
import os
import random
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P  # noqa: E402
from gaming_desk import tube  # noqa: E402
from loft_room import block, mat, slab  # noqa: E402
from bookshelf import _join  # noqa: E402

PLANTER = 1.1  # square planter side
PLANTER_H = 0.38


def _blob(name, c, r, m, parent, rng, squash=0.82):
    """A faceted leaf clump: a jittered low-res icosphere, flat shaded."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r)
    o = bpy.context.active_object
    for v in o.data.vertices:
        v.co *= 1 + rng.uniform(-0.16, 0.12)
    o.location = P(*c)
    o.scale = (1, 1, squash)
    o.rotation_euler = (rng.uniform(0, 6.28), rng.uniform(0, 6.28), rng.uniform(0, 6.28))
    o.name = name
    o.data.materials.append(m)
    o.parent = parent
    return o


def build_street_tree(parent=None, name="StreetTree", seed=1, height=5.2):
    rng = random.Random(seed)
    CONCRETE = mat("TreePlanter", "#1b1c20", 0.85)
    GRATE = mat("TreeGrate", "#0c0c0f", 0.4, metal=0.8)
    SOIL = mat("TreeSoil", "#120d0a", 0.95)
    CYAN = mat("TreeNeonCyan", "#22e4ff", emit="#22e4ff", strength=6.0)
    BARK = mat("TreeBark", "#1d1714", 0.9)
    LEAF = [
        mat("TreeLeafDeep", "#123a2a", 0.75),
        mat("TreeLeafMid", "#1c5236", 0.75),
        mat("TreeLeafTeal", "#145049", 0.75),
    ]
    FAIRY = [
        mat("TreeFairyWarm", "#ffcf7a", emit="#ffcf7a", strength=14.0),
        mat("TreeFairyPink", "#ff5fd8", emit="#ff5fd8", strength=14.0),
    ]

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---- planter: four concrete walls, soil, a dark grate and a cyan neon lip
    s, h, t = PLANTER, PLANTER_H, 0.09
    parts = [
        slab(f"{name}WallF", -s / 2, s / 2, 0, h, s / 2 - t, s / 2, CONCRETE, root),
        slab(f"{name}WallB", -s / 2, s / 2, 0, h, -s / 2, -s / 2 + t, CONCRETE, root),
        slab(f"{name}WallL", -s / 2, -s / 2 + t, 0, h, -s / 2 + t, s / 2 - t, CONCRETE, root),
        slab(f"{name}WallR", s / 2 - t, s / 2, 0, h, -s / 2 + t, s / 2 - t, CONCRETE, root),
    ]
    _join(parts, f"{name}Planter", root)
    slab(f"{name}Soil", -s / 2 + t, s / 2 - t, 0, h - 0.06, -s / 2 + t, s / 2 - t, SOIL, root)
    bars = [
        slab(f"{name}Bar{k}", -s / 2 + t + 0.02 + k * 0.1, -s / 2 + t + 0.05 + k * 0.1, h - 0.06, h - 0.04, -s / 2 + t, s / 2 - t, GRATE, root)
        for k in range(9)
    ]
    _join(bars, f"{name}Grate", root)
    lips = [
        slab(f"{name}LipF", -s / 2, s / 2, h, h + 0.015, s / 2 - 0.02, s / 2 + 0.005, CYAN, root),
        slab(f"{name}LipB", -s / 2, s / 2, h, h + 0.015, -s / 2 - 0.005, -s / 2 + 0.02, CYAN, root),
        slab(f"{name}LipL", -s / 2 - 0.005, -s / 2 + 0.02, h, h + 0.015, -s / 2, s / 2, CYAN, root),
        slab(f"{name}LipR", s / 2 - 0.02, s / 2 + 0.005, h, h + 0.015, -s / 2, s / 2, CYAN, root),
    ]
    _join(lips, f"{name}Neon", root)

    # ---- trunk: a slightly bent stem that forks into three limbs
    lean = rng.uniform(-0.12, 0.12)
    fork_y = height * 0.48
    fork = (lean, fork_y, rng.uniform(-0.08, 0.08))
    wood = [tube(f"{name}Trunk", [(0, h - 0.06, 0), (lean * 0.4, fork_y * 0.5, 0.02), fork], 0.09, BARK, root)]
    tips = []
    for k in range(3):
        a = k * 2.094 + rng.uniform(-0.4, 0.4)
        spread = rng.uniform(0.7, 1.0)
        mid = (fork[0] + math.cos(a) * spread * 0.45, fork_y + 0.7, fork[2] + math.sin(a) * spread * 0.45)
        tip = (fork[0] + math.cos(a) * spread, fork_y + 1.45 + rng.uniform(-0.15, 0.2), fork[2] + math.sin(a) * spread)
        wood.append(tube(f"{name}Limb{k}", [fork, mid, tip], 0.055, BARK, root))
        tips.append(tip)
    _join(wood, f"{name}Wood", root)

    # ---- canopy: leaf clumps around the limb tips and over the crown
    centres = []
    crown = (lean, height * 0.82, 0)
    centres.append((crown, 1.05))
    for tip in tips:
        centres.append(((tip[0], tip[1] + 0.25, tip[2]), rng.uniform(0.75, 0.9)))
    for k in range(4):
        a = k * 1.571 + rng.uniform(0, 1)
        c = (lean + math.cos(a) * 0.75, height * 0.74 + rng.uniform(-0.2, 0.25), math.sin(a) * 0.75)
        centres.append((c, rng.uniform(0.6, 0.78)))
    blobs = {i: [] for i in range(len(LEAF))}
    for i, (c, r) in enumerate(centres):
        k = rng.randrange(len(LEAF))
        blobs[k].append(_blob(f"{name}Leaf{i}", c, r, LEAF[k], root, rng))
    for k, objs in blobs.items():
        if objs:
            for o in objs:
                bpy.ops.object.select_all(action="DESELECT")
                o.select_set(True)
                bpy.context.view_layer.objects.active = o
                bpy.ops.object.shade_flat()
            _join(objs, f"{name}Canopy{k}", root)

    # ---- fairy lights: tiny glowing beads sitting just on the canopy surface
    beads = {0: [], 1: []}
    for i in range(34):
        c, r = centres[rng.randrange(len(centres))]
        d = Vector((rng.gauss(0, 1), rng.uniform(-0.6, 0.7), rng.gauss(0, 1))).normalized()
        p = (c[0] + d.x * r * 1.0, c[1] + d.y * r * 0.82, c[2] + d.z * r * 1.0)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.035, location=P(*p))
        o = bpy.context.active_object
        k = 0 if rng.random() < 0.75 else 1
        o.data.materials.append(FAIRY[k])
        o.parent = root
        o.name = f"{name}Bead{i}"
        beads[k].append(o)
    for k, objs in beads.items():
        if objs:
            _join(objs, f"{name}Fairy{k}", root)
    return root


def build_street_tree_trio(parent=None, name="StreetTreeTrio"):
    """Preview helper: three seeds side by side to show the variation."""
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    for i, sd in enumerate((1, 2, 3)):
        r = build_street_tree(root, f"{name}T{i}", seed=sd, height=5.0 + 0.3 * i)
        r.location = P((i - 1) * 2.6, 0, 0)
    return root

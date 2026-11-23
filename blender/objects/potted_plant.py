"""
Cyberpunk potted plant: a snake plant (tall, sword-shaped, gently twisting
leaves with lighter edges) in a tapered black concrete planter with a green
neon ring, dark soil with pebbles, and a small magenta grow-light on a stake.

    build_potted_plant(parent=None, name="PottedPlant", leaves=11, seed=2) -> root

Coordinates are three.js style (Y up, origin at the centre of the planter's
base on the floor). All leaves are merged into one mesh.
"""

import math
import os
import random
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P  # noqa: E402
from gaming_desk import disc, ring, tube  # noqa: E402
from loft_room import mat  # noqa: E402
from bookshelf import _join  # noqa: E402

POT_H = 0.34
POT_R_TOP, POT_R_BOT = 0.17, 0.13


def _leaf(name, base, height, width, angle, lean, twist, m, parent):
    """One sword leaf: a tapered blade rising from `base`, leaning outward and twisting."""
    seg = 10
    verts, faces = [], []
    for i in range(seg + 1):
        t = i / seg
        w = width * (math.sin(math.pi * min(0.98, t * 0.92 + 0.04)) ** 0.7) * (1 - 0.85 * t ** 3)
        r = lean * t ** 1.6  # outward lean grows with height
        a_twist = twist * t
        cx = base[0] + r * math.cos(angle)
        cz = base[2] + r * math.sin(angle)
        y = base[1] + height * t
        # blade direction: perpendicular to the lean, rotated by the twist
        bx = -math.sin(angle + a_twist)
        bz = math.cos(angle + a_twist)
        # three verts across: two edges + a raised midrib (a gentle V fold)
        nx, nz = math.cos(angle + a_twist), math.sin(angle + a_twist)
        for s in (-1, 0, 1):
            fold = 0.0 if s else w * 0.18
            verts.append(P(cx + s * bx * w / 2 + nx * fold, y, cz + s * bz * w / 2 + nz * fold))
    for i in range(seg):
        a = i * 3
        faces.append([a, a + 1, a + 4, a + 3])
        faces.append([a + 1, a + 2, a + 5, a + 4])
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    sol = o.modifiers.new("Thick", "SOLIDIFY")
    sol.thickness = 0.005
    for poly in o.data.polygons:
        poly.use_smooth = True
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def build_potted_plant(parent=None, name="PottedPlant", leaves=11, seed=2):
    POT = mat("PlanterConcrete", "#17181b", 0.85)
    RIM = mat("PlanterRim", "#25272b", 0.4, metal=0.6)
    SOIL = mat("PlanterSoil", "#120d0a", 0.95)
    PEBBLE = mat("PlanterPebble", "#3a3c40", 0.6)
    GREEN = mat("PlanterNeon", "#2bff7a", emit="#2bff7a", strength=7.0)
    LEAF_A = mat("LeafDark", "#1e4a2a", 0.55)
    LEAF_B = mat("LeafMid", "#2b6236", 0.55)
    LEAF_EDGE = mat("LeafVariegated", "#3d6e33", 0.5)
    STAKE = mat("GrowStake", "#1a1b1e", 0.4, metal=0.7)
    GROW = mat("GrowLight", "#ff2bd6", emit="#ff2bd6", strength=10.0)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---------- tapered planter, rim, neon ring, soil
    bpy.ops.mesh.primitive_cone_add(radius1=POT_R_BOT, radius2=POT_R_TOP, depth=POT_H, vertices=40)
    pot = bpy.context.active_object
    pot.name = f"{name}Planter"
    pot.location = P(0, POT_H / 2, 0)
    bev = pot.modifiers.new("Round", "BEVEL")
    bev.width = 0.01
    bev.segments = 2
    bpy.ops.object.shade_smooth()
    pot.data.materials.append(POT)
    pot.parent = root
    ring(f"{name}Rim", (0, POT_H, 0), POT_R_TOP - 0.008, 0.014, RIM, root)
    ring(f"{name}NeonRing", (0, 0.06, 0), POT_R_BOT + 0.008, 0.006, GREEN, root)
    disc(f"{name}Soil", (0, POT_H - 0.03, 0), POT_R_TOP - 0.015, 0.02, SOIL, root, verts=40)
    rng = random.Random(seed)
    for k in range(9):
        a, r = rng.uniform(0, 2 * math.pi), rng.uniform(0.05, POT_R_TOP - 0.04)
        bpy.ops.mesh.primitive_ico_sphere_add(radius=rng.uniform(0.012, 0.022), subdivisions=1)
        pb = bpy.context.active_object
        pb.name = f"{name}Pebble{k}"
        pb.location = P(r * math.cos(a), POT_H - 0.018, r * math.sin(a))
        pb.scale = (1, 1, 0.6)
        pb.data.materials.append(PEBBLE)
        pb.parent = root

    # ---------- sword leaves (merged), with a few lighter-edged ones
    blades = []
    for k in range(leaves):
        a = 2 * math.pi * k / leaves + rng.uniform(-0.25, 0.25)
        r0 = rng.uniform(0.0, 0.06)
        base = (r0 * math.cos(a), POT_H - 0.03, r0 * math.sin(a))
        h = rng.uniform(0.55, 0.95)
        m = LEAF_EDGE if k % 4 == 0 else (LEAF_A if k % 2 else LEAF_B)
        blades.append(_leaf(f"{name}Leaf{k}", base, h, rng.uniform(0.06, 0.09), a, rng.uniform(0.06, 0.2), rng.uniform(-0.8, 0.8), m, None))
    _join(blades, f"{name}Leaves", root)

    # ---------- magenta grow-light on a stake
    tube(f"{name}Stake", [(0.11, POT_H - 0.03, 0.05), (0.13, POT_H + 0.78, 0.06)], 0.006, STAKE, root)
    tube(f"{name}GrowBar", [(0.13, POT_H + 0.78, 0.06), (0.0, POT_H + 0.82, 0.01)], 0.012, STAKE, root)
    tube(f"{name}GrowLamp", [(0.11, POT_H + 0.805, 0.055), (0.01, POT_H + 0.83, 0.015)], 0.008, GROW, root)

    # preview-only lights: magenta from the grow lamp, green at the base (not exported)
    for k, (lx, ly, lz, col, w) in enumerate(((0.06, POT_H + 0.74, 0.04, (1.0, 0.17, 0.84), 8), (0, 0.06, POT_R_BOT + 0.12, (0.17, 1.0, 0.48), 3))):
        ld = bpy.data.lights.new(f"{name}GlowLight{k}", "POINT")
        ld.color = col
        ld.energy = w
        ld.shadow_soft_size = 0.15
        lo = bpy.data.objects.new(f"{name}GlowLight{k}", ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(lx, ly, lz)
        lo.parent = root
    return root

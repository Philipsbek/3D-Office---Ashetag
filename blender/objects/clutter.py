"""
Small lived-in props for the loft, each its own builder (origin on the floor
at the item's base unless noted; three.js coords, Y up, front faces +Z):

    build_skateboard(parent, name)       black deck with kicktails, magenta grip
                                          stripe, chrome trucks, glowing cyan wheels
                                          (built lying flat; lean it when placing)
    build_guitar_on_stand(parent, name)  black electric guitar with a cyan edge line
                                          and chrome hardware on an A-frame stand
    build_pizza_boxes(parent, name)      three stacked boxes, slightly askew
    build_can_cluster(parent, name)      five energy-drink cans, one crushed on its side
    build_headphone_stand(parent, name)  stand + over-ear headphones with magenta rings
    build_hanging_plant(parent, name)    pot on three cords with trailing vines;
                                          origin = the hanging point (hangs toward -Y)
    build_clutter_preview(parent, name)  everything in a row (hanging plant from a bar)
"""

import math
import os
import random
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P, rounded_box  # noqa: E402
from gaming_desk import disc, ring, tube  # noqa: E402
from loft_room import block, mat  # noqa: E402
from bookshelf import _join  # noqa: E402


def _root(name, parent):
    r = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(r)
    if parent:
        r.parent = parent
    return r


def _mats():
    return {
        "black": mat("ClutterBlack", "#0d0e11", 0.35, metal=0.3),
        "chrome": mat("ClutterChrome", "#a3a9b0", 0.12, metal=1.0),
        "steel": mat("ClutterSteel", "#25272c", 0.35, metal=0.85),
        "cyan": mat("ClutterCyan", "#22e4ff", emit="#22e4ff", strength=7.0),
        "mag": mat("ClutterMagenta", "#ff2bd6", emit="#ff2bd6", strength=7.0),
        "card": mat("PizzaCard", "#3a2e24", 0.85),
        "card_top": mat("PizzaCardTop", "#2e241c", 0.85),
        "label": mat("PizzaLabel", "#ff3a3a", 0.6),
    }


def build_skateboard(parent=None, name="Skateboard"):
    M = _mats()
    root = _root(name, parent)
    deck = rounded_box(f"{name}Deck", (0, 0.1, 0), (0.8, 0.014, 0.21), 0.006, M["black"], root)
    for v in deck.data.vertices:  # kick up both tails (Blender X = length, Z = up)
        t = abs(v.co.x) - 0.3
        if t > 0:
            v.co.z += t * 0.5
    block(f"{name}Grip", (0, 0.109, 0), (0.6, 0.002, 0.04), M["mag"], root)
    for s in (-1, 1):
        block(f"{name}Truck{s}", (s * 0.27, 0.07, 0), (0.05, 0.03, 0.17), M["chrome"], root)
        for w in (-1, 1):
            disc(f"{name}Wheel{s}_{w}", (s * 0.27, 0.03, w * 0.1), 0.03, 0.035, M["cyan"], root, axis="z")
    return root


def build_guitar_on_stand(parent=None, name="GuitarStand"):
    M = _mats()
    root = _root(name, parent)
    # A-frame stand
    for s in (-1, 1):
        tube(f"{name}StandLeg{s}", [(s * 0.15, 0.0, 0.12), (0, 0.32, -0.02)], 0.009, M["steel"], root)
        tube(f"{name}StandBack{s}", [(s * 0.12, 0.0, -0.18), (0, 0.32, -0.02)], 0.009, M["steel"], root)
    tube(f"{name}Neckrest", [(0, 0.32, -0.02), (0, 0.98, -0.1)], 0.009, M["steel"], root)
    block(f"{name}Cradle", (0, 0.24, 0.07), (0.3, 0.03, 0.06), M["steel"], root, r=0.008)
    # guitar leaning back slightly: body (two overlapping lobes) + neck + headstock
    g = _root(f"{name}Guitar", root)
    g.location = P(0, 0.26, 0.06)
    g.rotation_euler = (math.radians(-12), 0, 0)  # leans back onto the neck rest
    # one solid body with a real guitar outline: wide lower bout, narrow waist, smaller upper bout
    def half_width(y):
        lower = 0.19 * math.exp(-((y - 0.15) / 0.13) ** 2)
        upper = 0.15 * math.exp(-((y - 0.4) / 0.1) ** 2)
        return max(lower, upper, 0.11 * math.exp(-((y - 0.28) / 0.2) ** 2))
    ys = [0.5 * i / 30 for i in range(31)]
    outline = [(half_width(y) * math.sqrt(max(0.0, 1 - ((y - 0.25) / 0.255) ** 8)), y) for y in ys]
    pts = [(x, y) for x, y in outline] + [(-x, y) for x, y in reversed(outline)]
    verts = [P(x, y, z) for z in (-0.022, 0.022) for (x, y) in pts]
    n = len(pts)
    faces = [list(range(n)), list(range(2 * n - 1, n - 1, -1))]
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, n + j, n + i])
    me = bpy.data.meshes.new(f"{name}Body")
    me.from_pydata(verts, [], faces)
    me.update()
    body = bpy.data.objects.new(f"{name}Body", me)
    bpy.context.collection.objects.link(body)
    bev = body.modifiers.new("Round", "BEVEL")
    bev.width = 0.008
    bev.segments = 3
    body.data.materials.append(M["black"])
    body.parent = g
    # cyan line around the edge of the face
    tube(f"{name}BodyEdge", [(x * 0.97, y, 0.024) for x, y in pts] + [(pts[0][0] * 0.97, pts[0][1], 0.024)], 0.0035, M["cyan"], g)
    block(f"{name}Neck", (0, 0.78, 0.01), (0.05, 0.62, 0.025), M["black"], g)
    block(f"{name}Headstock", (0, 1.14, 0.005), (0.08, 0.15, 0.02), M["black"], g, r=0.008)
    for k in range(3):
        block(f"{name}Pickup{k}", (0, 0.22 + k * 0.07, 0.026), (0.08, 0.02, 0.006), M["chrome"], g)
    for k in range(6):
        x = -0.015 + k * 0.006
        tube(f"{name}String{k}", [(x, 0.14, 0.03), (x, 1.08, 0.025)], 0.0008, M["chrome"], g)
    for k, y in enumerate((0.1, 0.14)):
        disc(f"{name}Knob{k}", (0.08, y, 0.03), 0.012, 0.012, M["chrome"], g, axis="z")
    return root


def build_pizza_boxes(parent=None, name="PizzaBoxes"):
    M = _mats()
    root = _root(name, parent)
    for k, rot in enumerate((0, 9, -6)):
        b = block(f"{name}Box{k}", (0, 0.024 + k * 0.048, 0), (0.36, 0.045, 0.36), M["card"], root, r=0.004)
        b.rotation_euler = (0, 0, math.radians(rot))
        lb = block(f"{name}Label{k}", (0, 0.047 + k * 0.048, 0.0), (0.14, 0.002, 0.06), M["label"], root)
        lb.rotation_euler = (0, 0, math.radians(rot))
    return root


def build_can_cluster(parent=None, name="Cans", seed=3):
    M = _mats()
    CANS = [mat(f"ClutterCan_{c}", c, 0.25, metal=0.8, emit=c, strength=0.4) for c in ("#ff2bd6", "#22e4ff", "#2bff7a", "#ffb020")]
    rng = random.Random(seed)
    root = _root(name, parent)
    parts = []
    for k, (x, z) in enumerate(((0, 0), (0.08, 0.03), (-0.05, 0.08), (0.04, -0.07))):
        parts.append(disc(f"{name}Can{k}", (x, 0.062, z), 0.033, 0.124, rng.choice(CANS), None, verts=16))
    crushed = disc(f"{name}Crushed", (0.18, 0.025, 0.06), 0.033, 0.09, CANS[1], None, axis="x", verts=16)
    crushed.scale = (1, 1, 0.6)
    parts.append(crushed)
    _join(parts, f"{name}All", root)
    return root


def build_headphone_stand(parent=None, name="HeadphoneStand"):
    M = _mats()
    root = _root(name, parent)
    disc(f"{name}Base", (0, 0.01, 0), 0.08, 0.02, M["black"], root)
    ring(f"{name}BaseGlow", (0, 0.004, 0), 0.08, 0.004, M["cyan"], root)
    tube(f"{name}Pole", [(0, 0.02, 0), (0, 0.3, 0)], 0.01, M["steel"], root)
    block(f"{name}Hanger", (0, 0.31, 0), (0.1, 0.02, 0.03), M["steel"], root, r=0.006)
    # headphones: headband arc over the hanger + two ear cups
    arc = [(0.09 * math.cos(a), 0.33 + 0.05 * math.sin(a) - 0.05 + 0.05, 0) for a in [math.pi * i / 12 for i in range(13)]]
    tube(f"{name}Band", [(x, y, z) for x, y, z in arc], 0.012, M["black"], root)
    for s in (-1, 1):
        disc(f"{name}Cup{s}", (s * 0.095, 0.26, 0), 0.045, 0.035, M["black"], root, axis="x")
        ring(f"{name}CupGlow{s}", (s * 0.114, 0.26, 0), 0.035, 0.004, M["mag"], root, axis="x")
    return root


def build_hanging_plant(parent=None, name="HangingPlant", drop=0.7, seed=6):
    M = _mats()
    LEAF = mat("HangLeaf", "#2b6236", 0.6)
    LEAF2 = mat("HangLeafDark", "#1e4a2a", 0.6)
    POT = mat("HangPot", "#17181b", 0.8)
    rng = random.Random(seed)
    root = _root(name, parent)
    py = -drop
    bpy.ops.mesh.primitive_cone_add(radius1=0.09, radius2=0.13, depth=0.14, vertices=32)
    pot = bpy.context.active_object
    pot.name = f"{name}Pot"
    pot.location = P(0, py, 0)
    bpy.ops.object.shade_smooth()
    pot.data.materials.append(POT)
    pot.parent = root
    ring(f"{name}PotGlow", (0, py - 0.065, 0), 0.092, 0.004, M["cyan"], root)
    for k in range(3):
        a = 2 * math.pi * k / 3
        tube(f"{name}Cord{k}", [(0, 0, 0), (0.12 * math.cos(a), py + 0.07, 0.12 * math.sin(a))], 0.003, M["black"], root)
    disc(f"{name}Hook", (0, 0.0, 0), 0.015, 0.03, M["chrome"], root)
    leaves = []
    for k in range(7):  # trailing vines spilling over the rim
        a = 2 * math.pi * k / 7 + rng.uniform(-0.2, 0.2)
        r0 = 0.12
        pts = []
        for i in range(8):
            t = i / 7
            r = r0 + 0.06 * t
            pts.append((r * math.cos(a), py + 0.07 - t * rng.uniform(0.35, 0.6), r * math.sin(a)))
        tube(f"{name}Vine{k}", pts, 0.004, LEAF2, root)
        for i, (x, y, z) in enumerate(pts[1:], 1):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, segments=10, ring_count=6)
            lf = bpy.context.active_object
            lf.name = f"{name}Leaf{k}_{i}"
            lf.scale = (1.0, 1.0, 0.35)
            lf.location = P(x + rng.uniform(-0.02, 0.02), y, z + rng.uniform(-0.02, 0.02))
            lf.rotation_euler = (rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), rng.uniform(0, 3))
            lf.data.materials.append(LEAF if (i + k) % 2 else LEAF2)
            leaves.append(lf)
    _join(leaves, f"{name}Leaves", root)
    return root


def build_clutter_preview(parent=None, name="ClutterPreview"):
    root = _root(name, parent)
    sk = build_skateboard(root, f"{name}Skate")
    sk.location = P(-1.45, 0, 0.2)
    gt = build_guitar_on_stand(root, f"{name}Guitar")
    gt.location = P(-0.85, 0, 0)
    pz = build_pizza_boxes(root, f"{name}Pizza")
    pz.location = P(-0.1, 0, 0.1)
    cn = build_can_cluster(root, f"{name}Cans")
    cn.location = P(0.45, 0, 0.15)
    hp = build_headphone_stand(root, f"{name}Phones")
    hp.location = P(0.95, 0, 0.1)
    bar = mat("PreviewBar", "#25272c", 0.35, metal=0.85)
    tube(f"{name}Bar", [(1.25, 1.5, 0), (2.05, 1.5, 0)], 0.015, bar, root)
    pl = build_hanging_plant(root, f"{name}Plant")
    pl.location = P(1.65, 1.5, 0)
    ld = bpy.data.lights.new(f"{name}Glow", "POINT")
    ld.color = (0.6, 0.8, 1.0)
    ld.energy = 30
    lo = bpy.data.objects.new(f"{name}Glow", ld)
    bpy.context.collection.objects.link(lo)
    lo.location = P(0, 1.2, 1.0)
    lo.parent = root
    return root

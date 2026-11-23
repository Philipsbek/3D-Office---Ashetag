"""
Low vinyl-record cabinet for the boombox to sit on (original design): a dark wood-look box on
thin black metal legs, an open front shelf packed with record sleeves in neon colours, a
turntable-style slatted side, a cyan light strip under the top lip and a magenta glow beneath.

    build_boombox_stand(parent=None, name="BoomboxStand") -> root empty
    build_boombox_stand_preview(parent=None, name=...)   -> the stand with the boombox on top

Coordinates are three.js style (Y up, front faces +Z, origin at the centre of the footprint on
the floor). TOP_Y is the height of the top surface (where the boombox goes).
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
from loft_room import block, mat, slab  # noqa: E402

W, D = 0.86, 0.42  # footprint
LEG_H = 0.12
BOX_H = 0.44
TOP_Y = LEG_H + BOX_H + 0.03


def _root(name, parent):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    return root


def build_boombox_stand(parent=None, name="BoomboxStand"):
    WOOD = mat("StandWood", "#2a1f1c", 0.6)
    WOOD_DARK = mat("StandWoodDark", "#1a1414", 0.6)
    TOP = mat("StandTop", "#0d0c10", 0.25, metal=0.3)
    METAL = mat("StandMetal", "#0f0f12", 0.35, metal=0.85)
    CYAN = mat("StandNeonCyan", "#22e4ff", emit="#22e4ff", strength=6.0)
    PINK = mat("StandNeonPink", "#ff2bd6", emit="#ff2bd6", strength=6.0)
    SLEEVES = [mat(f"StandSleeve{c[1:]}", c, 0.7) for c in ("#22e4ff", "#ff4fd8", "#b6ff3b", "#ffb020", "#7a4dff", "#f2f0ea", "#d8283c", "#1b1b22")]

    root = _root(name, parent)
    rng = random.Random(4)

    # thin black legs, splayed a touch
    for sx in (-1, 1):
        for sz in (-1, 1):
            leg = block(f"{name}Leg{sx}{sz}", (sx * (W / 2 - 0.06), LEG_H / 2, sz * (D / 2 - 0.05)), (0.03, LEG_H, 0.03), METAL, root)
            leg.rotation_euler = (math.radians(-sz * 4), math.radians(0), math.radians(sx * 4))

    # the cabinet: sides, back, bottom, a middle divider; the front is open
    y0, y1 = LEG_H, LEG_H + BOX_H
    t = 0.025
    slab(f"{name}Bottom", -W / 2, W / 2, y0, y0 + t, -D / 2, D / 2, WOOD, root)
    slab(f"{name}Back", -W / 2, W / 2, y0, y1, -D / 2, -D / 2 + t, WOOD_DARK, root)
    for sx in (-1, 1):
        slab(f"{name}Side{sx}", sx * W / 2 - (t if sx > 0 else 0), sx * W / 2 + (0 if sx > 0 else t), y0, y1, -D / 2, D / 2, WOOD, root)
    slab(f"{name}Divider", -t / 2 + 0.12, t / 2 + 0.12, y0, y1, -D / 2, D / 2 - 0.02, WOOD, root)
    # top with a slight overhang + cyan strip under its front lip, magenta glow under the box
    block(f"{name}Top", (0, y1 + 0.015, 0.0), (W + 0.04, 0.03, D + 0.04), TOP, root, r=0.006)
    slab(f"{name}TopNeon", -W / 2, W / 2, y1 - 0.008, y1, D / 2 + 0.01, D / 2 + 0.018, CYAN, root)
    slab(f"{name}UnderGlow", -W / 2 + 0.04, W / 2 - 0.04, y0 - 0.006, y0, -D / 2 + 0.05, D / 2 - 0.05, PINK, root)

    # left bay: record sleeves standing in a row, a few leaning
    x = -W / 2 + t + 0.02
    while x < 0.12 - 0.03:
        th = 0.012 + rng.random() * 0.006
        s = block(f"{name}Sleeve{int(x * 1000)}", (x + th / 2, y0 + t + 0.155, 0.0), (th, 0.31, 0.31), rng.choice(SLEEVES), root)
        s.rotation_euler = (0, 0, math.radians(rng.uniform(-6, 6)))
        x += th + 0.003
    # right bay: a small stack of records lying flat + a little amp with a glowing dial
    for k in range(4):
        block(f"{name}Stack{k}", (0.28, y0 + t + 0.006 + k * 0.013, 0.02), (0.3, 0.012, 0.3), SLEEVES[(k * 3) % len(SLEEVES)], root)
    block(f"{name}Amp", (0.28, y0 + t + 0.06 + 0.1, 0.03), (0.3, 0.12, 0.26), METAL, root, r=0.01)
    for k, xx in enumerate((0.2, 0.28, 0.36)):
        block(f"{name}Knob{k}", (xx, y0 + t + 0.16, 0.165), (0.03, 0.03, 0.01), CYAN if k == 1 else PINK, root, r=0.004)
    return root


def build_boombox_stand_preview(parent=None, name="BoomboxStandPreview"):
    import boombox

    root = _root(name, parent)
    build_boombox_stand(root, name + "S")
    bb = boombox.build_boombox(root, name=name + "B")
    bb.location = P(0, TOP_Y, 0.0)
    bb.rotation_euler = (0, 0, math.radians(-8))
    return root

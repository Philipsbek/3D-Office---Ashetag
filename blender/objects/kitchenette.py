"""
Cyberpunk kitchenette for the loft's lower-left corner: gloss-black base
cabinets on a recessed plinth with pink neon underglow, a dark steel worktop
with a sink and an induction hob (glowing red rings), a built-in black
front-loading washing machine with a cyan-lit door, a dark tiled splashback,
and a floating black shelf with dishes and a pink light strip underneath.

    build_kitchenette(parent=None, name="Kitchenette") -> root empty

Coordinates are three.js style (Y up, the kitchen faces +Z). The origin is on
the floor at the centre of the back edge (against the wall).
"""

import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P  # noqa: E402
from gaming_desk import disc, ring, tube  # noqa: E402
from loft_room import block, mat  # noqa: E402

L = 2.6  # total length
D = 0.62  # depth
TOP = 0.92  # worktop height
WASH_W = 0.6  # washing machine width (right end)


def build_kitchenette(parent=None, name="Kitchenette"):
    GLOSS = mat("KitchenGloss", "#0d0e10", 0.18, metal=0.2)
    PLINTH = mat("KitchenPlinth", "#050506", 0.8)
    STEEL = mat("KitchenSteel", "#3a3d42", 0.3, metal=0.9)
    TOPM = mat("KitchenTop", "#1d1f23", 0.35, metal=0.6)
    SINK = mat("KitchenSink", "#121316", 0.25, metal=0.8)
    CHROME = mat("KitchenChrome", "#9aa0a6", 0.12, metal=1.0)
    HOB = mat("KitchenHob", "#050507", 0.05, metal=0.1)
    TILE = mat("KitchenTile", "#15232a", 0.35)
    GROUT = mat("KitchenGrout", "#07090b", 0.8)
    PINK = mat("KitchenPink", "#ff3fa6", emit="#ff3fa6", strength=8.0)
    CYAN = mat("KitchenCyan", "#22e4ff", emit="#22e4ff", strength=7.0)
    RED = mat("KitchenHobRed", "#ff2a1a", emit="#ff2a1a", strength=6.0)
    GLASS = mat("WasherGlass", "#0a1622", 0.05, metal=0.3, emit="#103048", strength=0.5)
    CERAMIC = mat("Ceramic", "#2a2c31", 0.3)
    MUG_A = mat("MugMagenta", "#8a1d5c", 0.4)
    MUG_B = mat("MugTeal", "#1d5c5a", 0.4)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    x0, x1 = -L / 2, L / 2
    xw = x1 - WASH_W  # washer starts here

    # ---------- plinth (recessed) with pink underglow along the toe kick
    block(f"{name}Plinth", ((x0 + xw) / 2, 0.05, D / 2 - 0.04), (xw - x0, 0.1, D - 0.08), PLINTH, root)
    block(f"{name}ToeGlow", ((x0 + xw) / 2, 0.012, D - 0.07), (xw - x0 - 0.06, 0.008, 0.01), PINK, root)

    # ---------- base cabinets: three gloss-black doors with steel bar handles
    n = 3
    dw = (xw - x0) / n
    for k in range(n):
        cx = x0 + dw * (k + 0.5)
        block(f"{name}Door{k}", (cx, 0.1 + (TOP - 0.14) / 2, D - 0.02), (dw - 0.012, TOP - 0.15, 0.04), GLOSS, root, r=0.004)
        block(f"{name}Handle{k}", (cx, TOP - 0.1, D + 0.006), (dw * 0.55, 0.012, 0.012), STEEL, root)
    block(f"{name}Carcass", ((x0 + xw) / 2, 0.1 + (TOP - 0.14) / 2, (D - 0.04) / 2), (xw - x0, TOP - 0.14, D - 0.04), PLINTH, root)

    # ---------- front-loading washing machine (right end)
    wx = (xw + x1) / 2
    wh = TOP - 0.04
    block(f"{name}Washer", (wx, wh / 2, D / 2), (WASH_W - 0.01, wh, D - 0.01), GLOSS, root, r=0.01)
    block(f"{name}WasherPanel", (wx, wh - 0.07, D + 0.002), (WASH_W - 0.06, 0.09, 0.01), HOB, root, r=0.003)
    block(f"{name}WasherDisplay", (wx + 0.08, wh - 0.07, D + 0.009), (0.12, 0.035, 0.004), CYAN, root)
    disc(f"{name}WasherKnob", (wx - 0.15, wh - 0.07, D + 0.012), 0.025, 0.02, CHROME, root, axis="z")
    door_y = 0.4
    ring(f"{name}WasherDoorRim", (wx, door_y, D + 0.015), 0.19, 0.03, CHROME, root, axis="z")
    disc(f"{name}WasherGlass", (wx, door_y, D + 0.012), 0.17, 0.02, GLASS, root, axis="z")
    ring(f"{name}WasherGlow", (wx, door_y, D + 0.004), 0.235, 0.006, CYAN, root, axis="z")
    block(f"{name}WasherDrawer", (wx - 0.16, wh - 0.16, D + 0.002), (0.18, 0.06, 0.01), GLOSS, root, r=0.003)

    # ---------- worktop with sink and hob
    block(f"{name}Worktop", (0, TOP - 0.02, D / 2 + 0.01), (L + 0.04, 0.04, D + 0.02), TOPM, root, r=0.004)
    sx = x0 + 0.65
    block(f"{name}SinkRim", (sx, TOP + 0.003, D / 2 + 0.03), (0.56, 0.006, 0.42), STEEL, root, r=0.004)
    block(f"{name}SinkBasin", (sx, TOP + 0.005, D / 2 + 0.03), (0.5, 0.006, 0.36), SINK, root)
    disc(f"{name}SinkDrain", (sx, TOP + 0.009, D / 2 + 0.03), 0.03, 0.004, CHROME, root)
    # arched chrome tap
    tube(f"{name}Tap", [(sx, TOP, 0.12), (sx, TOP + 0.3, 0.12), (sx, TOP + 0.36, 0.16), (sx, TOP + 0.34, 0.26), (sx, TOP + 0.28, 0.28)], 0.014, CHROME, root)
    disc(f"{name}TapLever", (sx + 0.05, TOP + 0.03, 0.12), 0.012, 0.06, CHROME, root, axis="x")
    hx = x0 + 1.5
    block(f"{name}Hob", (hx, TOP + 0.004, D / 2), (0.58, 0.008, 0.5), HOB, root, r=0.004)
    for k, (dx, dz, r) in enumerate(((-0.13, -0.1, 0.09), (0.14, 0.1, 0.07))):
        ring(f"{name}HobRing{k}", (hx + dx, TOP + 0.009, D / 2 + dz), r, 0.004, RED, root)

    # ---------- splashback: dark tiles with grout lines + a neon strip under the shelf
    sb_h = 0.62
    block(f"{name}Splashback", (0, TOP + sb_h / 2, 0.006), (L, sb_h, 0.012), TILE, root)
    for k in range(1, 4):
        block(f"{name}GroutH{k}", (0, TOP + k * sb_h / 4, 0.013), (L, 0.006, 0.002), GROUT, root)
    for k in range(1, 13):
        block(f"{name}GroutV{k}", (x0 + k * L / 13, TOP + sb_h / 2, 0.013), (0.006, sb_h, 0.002), GROUT, root)

    # ---------- floating shelf with dishes, pink strip underneath
    shy = TOP + sb_h + 0.1
    block(f"{name}Shelf", (-0.25, shy, 0.14), (1.7, 0.035, 0.28), GLOSS, root, r=0.004)
    block(f"{name}ShelfGlow", (-0.25, shy - 0.022, 0.25), (1.6, 0.006, 0.01), PINK, root)
    for k in range(5):  # stack of plates
        disc(f"{name}Plate{k}", (-0.85, shy + 0.025 + k * 0.016, 0.14), 0.12, 0.012, CERAMIC, root)
    for k, bx in enumerate((-0.48, -0.3)):  # bowls
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, segments=24, ring_count=12)
        b = bpy.context.active_object
        b.name = f"{name}Bowl{k}"
        b.scale = (1, 1, 0.55)
        b.location = P(bx, shy + 0.05, 0.14)
        bpy.ops.object.shade_smooth()
        b.data.materials.append(CERAMIC)
        b.parent = root
    for k, (jx, jh) in enumerate(((0.05, 0.16), (0.18, 0.12), (0.3, 0.2))):  # jars
        disc(f"{name}Jar{k}", (jx, shy + 0.018 + jh / 2, 0.14), 0.045, jh, GLASS, root)
        disc(f"{name}JarLid{k}", (jx, shy + 0.022 + jh, 0.14), 0.047, 0.012, STEEL, root)

    # ---------- bits on the worktop: kettle and two mugs
    kx = xw + WASH_W / 2  # on the worktop above the washer
    disc(f"{name}KettleBase", (kx, TOP + 0.01, 0.3), 0.08, 0.02, GLOSS, root)
    disc(f"{name}Kettle", (kx, TOP + 0.12, 0.3), 0.07, 0.2, STEEL, root)
    ring(f"{name}KettleGlow", (kx, TOP + 0.025, 0.3), 0.071, 0.004, CYAN, root)
    tube(f"{name}KettleSpout", [(kx + 0.06, TOP + 0.12, 0.3), (kx + 0.12, TOP + 0.2, 0.3)], 0.012, STEEL, root)
    tube(f"{name}KettleHandle", [(kx - 0.06, TOP + 0.06, 0.3), (kx - 0.11, TOP + 0.1, 0.3), (kx - 0.11, TOP + 0.18, 0.3), (kx - 0.06, TOP + 0.21, 0.3)], 0.01, GLOSS, root)
    for k, (mx, mz, m) in enumerate(((x0 + 1.05, 0.42, MUG_A), (x0 + 1.15, 0.5, MUG_B))):
        disc(f"{name}Mug{k}", (mx, TOP + 0.05, mz), 0.04, 0.1, m, root)
        ring(f"{name}MugHandle{k}", (mx + 0.045, TOP + 0.05, mz), 0.025, 0.007, m, root, axis="z")

    # preview-only lights so the pink strips visibly glow (lights aren't exported)
    for k, (lx, ly, lz, w) in enumerate(((-0.75, shy - 0.06, 0.25, 18), (0.25, shy - 0.06, 0.25, 18),
                                         (-0.9, 0.03, D + 0.02, 10), (0.0, 0.03, D + 0.02, 10))):
        ld = bpy.data.lights.new(f"{name}GlowLight{k}", "POINT")
        ld.color = (1.0, 0.25, 0.65)
        ld.energy = w
        ld.shadow_soft_size = 0.25
        lo = bpy.data.objects.new(f"{name}GlowLight{k}", ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(lx, ly, lz)
        lo.parent = root

    return root

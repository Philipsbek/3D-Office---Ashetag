"""
Cyberpunk mini drinks fridge: a compact black fridge with a glass door, cool
blue interior light, two wire shelves of glowing cans and bottles, a chrome
bar handle, a cyan glow strip at the base, and a few things on top (a box of
snacks and a can).

    build_mini_fridge(parent=None, name="MiniFridge", seed=2) -> root empty

Coordinates are three.js style (Y up, the door faces +Z, origin at the centre
of the base on the floor).
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
from gaming_desk import disc, tube  # noqa: E402
from loft_room import block, mat  # noqa: E402
from glass_room import glass_mat  # noqa: E402
from bookshelf import _join  # noqa: E402

W, H, D = 0.56, 0.86, 0.56


def build_mini_fridge(parent=None, name="MiniFridge", seed=2):
    BODY = mat("FridgeBody", "#0d0e11", 0.3, metal=0.5)
    INNER = mat("FridgeInner", "#0a1a2c", 0.4, emit="#1f5fb0", strength=0.9)
    WIRE = mat("FridgeWire", "#8a9096", 0.2, metal=1.0)
    CHROME = mat("FridgeChrome", "#a3a9b0", 0.12, metal=1.0)
    CYAN = mat("FridgeCyan", "#22e4ff", emit="#22e4ff", strength=8.0)
    BOX = mat("SnackBox", "#2a123a", 0.6)
    BOX_TXT = mat("SnackBoxStripe", "#ffd21a", emit="#ffd21a", strength=1.5)
    GLASS = glass_mat("FridgeDoor", "#7fb8e8", 0.18)
    cols = ["#ff2bd6", "#22e4ff", "#2bff7a", "#ffb020", "#ff3a3a"]
    CANS = [mat(f"FridgeCan_{c}", c, 0.25, metal=0.8, emit=c, strength=0.5) for c in cols]
    BOTTLE = mat("FridgeBottle", "#2a6a4a", 0.1, emit="#2bff7a", strength=0.3)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    rng = random.Random(seed)
    base = 0.05
    zf = D / 2

    # ---------- shell built around an open, lit interior
    block(f"{name}Back", (0, base + H / 2, -D / 2 + 0.03), (W, H, 0.06), BODY, root)
    for s in (-1, 1):
        block(f"{name}Side{s}", (s * (W / 2 - 0.025), base + H / 2, 0), (0.05, H, D), BODY, root, r=0.006)
    block(f"{name}Top", (0, base + H - 0.025, 0), (W, 0.05, D), BODY, root, r=0.006)
    block(f"{name}Floor", (0, base + 0.05, 0), (W, 0.1, D), BODY, root)
    block(f"{name}Plinth", (0, base / 2, 0.02), (W - 0.04, base, D - 0.04), BODY, root)
    block(f"{name}BaseGlow", (0, 0.012, zf - 0.03), (W - 0.1, 0.008, 0.01), CYAN, root)
    # lit interior walls
    iw, ih = W - 0.1, H - 0.15
    block(f"{name}InnerBack", (0, base + 0.1 + ih / 2, -D / 2 + 0.065), (iw, ih, 0.005), INNER, root)

    # ---------- two wire shelves with cans and bottles
    items = []
    for k, sy in enumerate((base + 0.12, base + 0.45)):
        block(f"{name}Shelf{k}", (0, sy, -0.02), (iw, 0.008, D - 0.16), WIRE, root)
        for c, x in enumerate((-0.16, -0.08, 0.0, 0.08, 0.16)):  # five evenly spaced columns
            if k == 1 and c in (0, 3):  # two bottles on the top shelf
                items.append(disc(f"{name}Bottle{k}_{c}", (x, sy + 0.12, 0.02), 0.03, 0.22, BOTTLE, None, verts=14))
                items.append(disc(f"{name}BottleNeck{k}_{c}", (x, sy + 0.26, 0.02), 0.012, 0.06, BOTTLE, None, verts=10))
            else:
                for zz in (-0.08, 0.06):  # two cans deep
                    items.append(disc(f"{name}Can{k}_{c}_{zz}", (x, sy + 0.066, zz), 0.033, 0.124, rng.choice(CANS), None, verts=14))
    if items:
        _join(items, f"{name}Drinks", root)

    # ---------- glass door in a black frame, chrome handle
    block(f"{name}DoorGlass", (0, base + H / 2, zf + 0.01), (W - 0.06, H - 0.06, 0.008), GLASS, root)
    for k, (x, y, w, h) in enumerate(((0, base + H - 0.025, W, 0.05), (0, base + 0.05, W, 0.1),
                                      (-W / 2 + 0.025, base + H / 2, 0.05, H), (W / 2 - 0.025, base + H / 2, 0.05, H))):
        block(f"{name}DoorFrame{k}", (x, y, zf + 0.012), (w, h, 0.03), BODY, root, r=0.004)
    tube(f"{name}Handle", [(W / 2 - 0.05, base + 0.25, zf + 0.045), (W / 2 - 0.05, base + 0.7, zf + 0.045)], 0.009, CHROME, root)
    for k, y in enumerate((0.25, 0.7)):
        block(f"{name}HandleMount{k}", (W / 2 - 0.05, base + y, zf + 0.033), (0.018, 0.018, 0.024), CHROME, root)
    block(f"{name}Badge", (-W / 2 + 0.07, base + H - 0.025, zf + 0.029), (0.06, 0.012, 0.004), CYAN, root)

    # ---------- on top: a snack box and a can
    bx = block(f"{name}SnackBox", (-0.1, base + H + 0.06, -0.02), (0.22, 0.12, 0.14), BOX, root, r=0.004)
    bx.rotation_euler = (0, 0, math.radians(-10))
    st = block(f"{name}SnackStripe", (-0.1, base + H + 0.07, 0.052), (0.2, 0.025, 0.002), BOX_TXT, root)
    st.rotation_euler = (0, 0, math.radians(-10))
    disc(f"{name}TopCan", (0.14, base + H + 0.062, 0.05), 0.033, 0.124, CANS[1], root)

    # preview-only glow (lights aren't exported)
    ld = bpy.data.lights.new(f"{name}GlowLight", "POINT")
    ld.color = (0.3, 0.6, 1.0)
    ld.energy = 10
    ld.shadow_soft_size = 0.3
    lo = bpy.data.objects.new(f"{name}GlowLight", ld)
    bpy.context.collection.objects.link(lo)
    lo.location = P(W * 0.8, base + 0.2, zf + 0.5)
    lo.parent = root
    return root

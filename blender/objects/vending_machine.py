"""
Cyberpunk drinks vending machine for the loft's blue alcove: a black cabinet
with a backlit display window full of glowing cans on five shelves, a lit
header with 3D text, a keypad column (screen, buttons, coin slot, card reader),
a pickup bin, and cyan neon strips down the front edges.

    build_vending_machine(parent=None, name="VendingMachine", header="DRINKS") -> root

Coordinates are three.js style (Y up, the machine faces +Z, origin at the
centre of its base on the floor). All cans are merged into one mesh.
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
from gaming_desk import disc  # noqa: E402
from loft_room import block, mat  # noqa: E402
from bookshelf import _join  # noqa: E402
from arcade_cabinet import _text  # noqa: E402

W, H, D = 1.0, 1.95, 0.8


def build_vending_machine(parent=None, name="VendingMachine", header="DRINKS"):
    BODY = mat("VendBody", "#0d0e11", 0.35, metal=0.4)
    TRIM = mat("VendTrim", "#202227", 0.3, metal=0.85)
    INTERIOR = mat("VendInterior", "#06070a", 0.6)
    BACKLIGHT = mat("VendBacklight", "#0c2a4a", emit="#1f6fd0", strength=1.4)  # deep blue glow
    SHELF = mat("VendShelf", "#2a2d33", 0.3, metal=0.9)
    CYAN = mat("VendCyan", "#22e4ff", emit="#22e4ff", strength=8.0)
    HEAD = mat("VendHeader", "#0a2a4a", emit="#1a7aff", strength=2.5)
    HEAD_TXT = mat("VendHeaderText", "#ffffff", emit="#ffffff", strength=6.0)
    SCREEN = mat("VendScreen", "#041014", emit="#22e4ff", strength=1.8)
    KEY = mat("VendKey", "#3a3d44", 0.3, metal=0.7)
    GREEN = mat("VendGreen", "#2bff7a", emit="#2bff7a", strength=6.0)
    SLOT = mat("VendSlot", "#ff7a14", emit="#ff7a14", strength=5.0)
    can_cols = ["#ff2bd6", "#22e4ff", "#ffd21a", "#ff3a3a", "#2bff7a", "#9a5bff"]
    CANS = [mat(f"VendCan_{c}", c, 0.25, metal=0.8, emit=c, strength=0.6) for c in can_cols]

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---------- cabinet, built from panels around a 0.3 m deep display recess
    wx0, wx1 = -W / 2 + 0.06, W / 2 - 0.3
    wy0, wy1 = 0.55, 1.68
    zf = D / 2
    rd = 0.3  # recess depth
    block(f"{name}Core", (0, H / 2, (-D / 2 + zf - rd) / 2), (W, H, D - rd), BODY, root, r=0.01)
    block(f"{name}RightColumn", ((wx1 + 0.04 + W / 2) / 2, H / 2, zf - rd / 2), (W / 2 - wx1 - 0.04, H, rd), BODY, root)
    block(f"{name}LeftStrip", ((-W / 2 + wx0 - 0.04) / 2, H / 2, zf - rd / 2), (wx0 - 0.04 + W / 2, H, rd), BODY, root)
    block(f"{name}TopBlock", (0, (wy1 + 0.04 + H) / 2, zf - rd / 2), (W, H - wy1 - 0.04, rd), BODY, root)
    block(f"{name}BottomBlock", (0, (wy0 - 0.04) / 2, zf - rd / 2), (W, wy0 - 0.04, rd), BODY, root)
    block(f"{name}Plinth", (0, 0.04, 0.02), (W - 0.04, 0.08, D - 0.02), TRIM, root)
    for s in (-1, 1):
        block(f"{name}EdgeNeon{s}", (s * (W / 2 + 0.002), H / 2, D / 2 - 0.01), (0.01, H - 0.1, 0.01), CYAN, root)

    # ---------- display window (left part of the front)
    wcx, wcy = (wx0 + wx1) / 2, (wy0 + wy1) / 2
    ww, wh = wx1 - wx0, wy1 - wy0
    block(f"{name}Backlight", (wcx, wcy, zf - 0.29), (ww - 0.02, wh - 0.02, 0.01), BACKLIGHT, root)
    for k, (x, y, w, h) in enumerate(((wcx, wy1 + 0.02, ww + 0.04, 0.04), (wcx, wy0 - 0.02, ww + 0.04, 0.04),
                                      (wx0 - 0.02, wcy, 0.04, wh + 0.08), (wx1 + 0.02, wcy, 0.04, wh + 0.08))):
        block(f"{name}WindowFrame{k}", (x, y, zf + 0.005), (w, h, 0.03), TRIM, root)
    # five shelves of cans
    rng = random.Random(11)
    rows, cols = 5, 6
    cans = []
    for r in range(rows):
        sy = wy0 + 0.04 + r * (wh - 0.04) / rows
        block(f"{name}Shelf{r}", (wcx, sy, zf - 0.13), (ww - 0.02, 0.012, 0.24), SHELF, root)
        block(f"{name}ShelfLip{r}", (wcx, sy + 0.015, zf - 0.015), (ww - 0.02, 0.03, 0.006), SHELF, root)
        col = rng.choice(CANS)
        for c in range(cols):
            cx = wx0 + 0.05 + c * (ww - 0.1) / (cols - 1)
            if rng.random() < 0.12:
                continue  # a sold-out gap here and there
            m = col if rng.random() < 0.75 else rng.choice(CANS)
            cans.append(disc(f"{name}Can{r}_{c}", (cx, sy + 0.068, zf - 0.07), 0.03, 0.12, m, None, verts=16))
    if cans:
        _join(cans, f"{name}Cans", root)

    # ---------- keypad column (right part of the front)
    kx = W / 2 - 0.15
    block(f"{name}KeyPanel", (kx, 1.15, zf + 0.004), (0.2, 0.95, 0.01), TRIM, root, r=0.004)
    block(f"{name}Screen", (kx, 1.5, zf + 0.011), (0.15, 0.09, 0.004), SCREEN, root)
    for r in range(4):
        for c in range(3):
            block(f"{name}Key{r}_{c}", (kx - 0.045 + c * 0.045, 1.37 - r * 0.045, zf + 0.013), (0.032, 0.032, 0.008), KEY, root, r=0.004)
    block(f"{name}CoinSlot", (kx, 1.12, zf + 0.012), (0.012, 0.06, 0.004), SLOT, root)
    block(f"{name}CardReader", (kx, 0.98, zf + 0.016), (0.11, 0.07, 0.02), BODY, root, r=0.004)
    block(f"{name}CardLED", (kx + 0.04, 0.995, zf + 0.028), (0.012, 0.012, 0.004), GREEN, root)
    block(f"{name}ChangeCup", (kx, 0.76, zf + 0.02), (0.1, 0.06, 0.03), INTERIOR, root, r=0.004)

    # ---------- pickup bin under the window
    flap = block(f"{name}BinFlap", (wcx, 0.33, zf + 0.004), (ww - 0.08, 0.15, 0.012), TRIM, root, r=0.004)
    flap.rotation_euler = (math.radians(-10), 0, 0)
    block(f"{name}BinLabel", (wcx, 0.44, zf + 0.004), (0.2, 0.012, 0.004), CYAN, root)

    # ---------- lit header with text
    block(f"{name}Header", (0, H - 0.12, zf + 0.004), (W - 0.04, 0.18, 0.012), HEAD, root)
    _text(f"{name}HeaderText", header, (0, H - 0.12, zf + 0.012), 0.1, HEAD_TXT, root, max_width=W - 0.3)

    # preview-only lights: the machine's glow on the floor and surroundings
    for k, (lx, ly, lz, col, w) in enumerate(((0, 1.1, D / 2 + 0.4, (0.62, 0.86, 1.0), 25), (0, 0.15, D / 2 + 0.2, (0.13, 0.89, 1.0), 8))):
        ld = bpy.data.lights.new(f"{name}GlowLight{k}", "POINT")
        ld.color = col
        ld.energy = w
        ld.shadow_soft_size = 0.4
        lo = bpy.data.objects.new(f"{name}GlowLight{k}", ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(lx, ly, lz)
        lo.parent = root

    return root

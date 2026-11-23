"""
Cyberpunk Services board for the loft's big yellow window: a large hanging
holographic display (the website draws the live Services list on it), with
neon corner brackets, a thin black bezel, two suspension cables, and glowing
note cards stuck to the window on either side, wired to the display with thin
neon lines.

    build_holo_board(parent=None, name="HoloBoard") -> root empty

Coordinates are three.js style (Y up, the display faces +Z). The origin is the
centre of the display. The screen is a plane named "TVScreen" with 0..1 UVs at
16:9, matching the site's 1024x576 Services canvas.
"""

import math
import os
import random
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P, _hex  # noqa: E402
from gaming_desk import tube  # noqa: E402
from loft_room import block, mat  # noqa: E402

SW, SH = 2.2, 2.2 * 9 / 16  # screen size (16:9)


def _services_preview_image():
    """Stand-in picture of the Services list (the site replaces it live)."""
    name = "HoloServicesPreview"
    img = bpy.data.images.get(name)
    if img:
        return img
    w, h = 256, 144
    img = bpy.data.images.new(name, w, h)
    px = [0.0] * (w * h * 4)

    def rect(x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(h, y1)):
            for x in range(max(0, x0), min(w, x1)):
                i = (y * w + x) * 4
                px[i:i + 4] = (*c, 1)

    rect(0, 0, w, h, (0.004, 0.02, 0.03))  # deep teal-black glass
    cyan, mag, dim = _hex("#22e4ff"), _hex("#ff2bd6"), (0.05, 0.25, 0.3)
    rect(16, 112, 120, 124, cyan)  # title bar
    for k in range(4):  # four list rows: number + label
        y = 88 - k * 20
        rect(16, y, 26, y + 8, mag if k == 0 else dim)
        rect(34, y, 34 + [120, 96, 80, 60][k], y + 8, cyan if k == 0 else dim)
    for x in range(0, w, 4):  # scanline + frame
        rect(x, 2, x + 2, 3, dim)
    rect(0, 0, w, 2, cyan)
    rect(0, h - 2, w, h, cyan)
    img.pixels = px
    img.pack()
    return img


def _screen_mat():
    m = bpy.data.materials.get("Holo_Screen")
    if m:
        return m
    m = bpy.data.materials.new("Holo_Screen")
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _services_preview_image()
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 2.0
    b.inputs["Roughness"].default_value = 0.1
    return m


def build_holo_board(parent=None, name="HoloBoard"):
    BEZEL = mat("HoloBezel", "#0b0c0e", 0.35, metal=0.6)
    CABLE = mat("HoloCable", "#1a1b1e", 0.5, metal=0.5)
    CYAN = mat("HoloCyan", "#22e4ff", emit="#22e4ff", strength=8.0)
    MAG = mat("HoloMagenta", "#ff2bd6", emit="#ff2bd6", strength=6.0)
    CARD = mat("HoloCard", "#121318", 0.6)
    CARD_TXT = mat("HoloCardText", "#7fe9ff", emit="#7fe9ff", strength=2.5)
    PIN = mat("HoloPin", "#ff2bd6", emit="#ff2bd6", strength=8.0)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---------- display: back panel, bezel bars, screen plane
    block(f"{name}Back", (0, 0, -0.025), (SW + 0.08, SH + 0.08, 0.03), BEZEL, root, r=0.006)
    for k, (x, y, w, h) in enumerate(((0, SH / 2 + 0.03, SW + 0.08, 0.025), (0, -SH / 2 - 0.03, SW + 0.08, 0.025),
                                      (-SW / 2 - 0.03, 0, 0.025, SH + 0.08), (SW / 2 + 0.03, 0, 0.025, SH + 0.08))):
        block(f"{name}Bezel{k}", (x, y, 0.0), (w, h, 0.02), BEZEL, root)
    bpy.ops.mesh.primitive_plane_add(size=1)
    scr = bpy.context.active_object
    scr.name = "TVScreen"
    scr.scale = (SW, SH, 1)
    scr.location = P(0, 0, 0.012)
    scr.rotation_euler = (math.pi / 2, 0, 0)
    scr.data.materials.append(_screen_mat())
    scr.parent = root

    # ---------- neon corner brackets (L shapes) + a magenta status bar
    L = 0.32
    for k, (sx, sy) in enumerate(((-1, 1), (1, 1), (-1, -1), (1, -1))):
        cx, cy = sx * (SW / 2 + 0.06), sy * (SH / 2 + 0.06)
        block(f"{name}BracketH{k}", (cx - sx * L / 2, cy, 0.02), (L, 0.014, 0.014), CYAN, root)
        block(f"{name}BracketV{k}", (cx, cy - sy * L / 2, 0.02), (0.014, L, 0.014), CYAN, root)
    block(f"{name}StatusBar", (SW / 2 - 0.25, -SH / 2 - 0.08, 0.02), (0.36, 0.012, 0.012), MAG, root)

    # ---------- two cables from the top corners up to the ceiling
    for k, x in enumerate((-SW / 2 + 0.2, SW / 2 - 0.2)):
        tube(f"{name}Cable{k}", [(x, SH / 2 + 0.04, -0.02), (x, SH / 2 + 1.1, -0.02)], 0.006, CABLE, root)
        block(f"{name}CableClamp{k}", (x, SH / 2 + 0.06, -0.02), (0.05, 0.04, 0.04), BEZEL, root)

    # ---------- glowing note cards on the window either side, wired to the display
    rng = random.Random(3)
    cards = [(-1.62, 0.42), (-1.85, -0.12), (-1.5, -0.55), (1.6, 0.48), (1.9, 0.0), (1.55, -0.5)]
    for k, (x, y) in enumerate(cards):
        w, h = rng.uniform(0.24, 0.32), rng.uniform(0.17, 0.24)
        c = block(f"{name}Card{k}", (x, y, -0.06), (w, h, 0.006), CARD, root)
        c.rotation_euler = (0, math.radians(rng.uniform(-8, 8)), 0)
        # "text" lines on the card
        for j in range(3):
            ln = block(f"{name}CardLine{k}_{j}", (x - w * 0.08, y + h * 0.22 - j * h * 0.22, -0.055), (w * rng.uniform(0.45, 0.7), 0.012, 0.002), CARD_TXT, root)
            ln.rotation_euler = c.rotation_euler
        block(f"{name}Pin{k}", (x, y + h / 2 - 0.03, -0.05), (0.022, 0.022, 0.012), PIN, root)
        # thin neon wire from the pin to the nearest display edge
        ex = math.copysign(SW / 2 + 0.03, x)
        ey = max(-SH / 2 + 0.1, min(SH / 2 - 0.1, y * 0.6))
        tube(f"{name}Wire{k}", [(x, y + h / 2 - 0.03, -0.045), (ex, ey, -0.035)], 0.0035, MAG, root)

    return root


def build_holo_board_preview(parent=None, name="HoloBoardPreview"):
    """Preview only: the board raised to eye level in front of a glowing yellow
    window panel, the way it will hang in the loft (the window is part of the room)."""
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    win = mat("PreviewWindowGlow", "#ffd21a", emit="#ffd21a", strength=3.0)
    block(f"{name}Window", (0, 1.7, -0.12), (4.6, 2.0, 0.02), win, root)
    board = build_holo_board(root, name=f"{name}Board")
    board.location = P(0, 1.65, 0.12)
    return root

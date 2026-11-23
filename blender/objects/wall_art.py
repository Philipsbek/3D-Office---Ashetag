"""
Cyberpunk wall art for the loft (original artwork, generated in code):

    build_led_mural(parent=None, name="LEDMural", w=4.0, h=2.2)
        a large wall-mounted LED screen showing a night city skyline (lit windows,
        neon moon ring, haze) in a slim black frame with mounting brackets and a
        cyan top light. The screen plane is "<name>Screen" with 0..1 UVs.
    build_poster(parent=None, name="Poster", art="circles", glow="#ff2bd6")
        a framed print with a glowing neon border. art: circles | stripes | wave
    build_wall_art_preview(parent, name) -> mural + three posters on a dark wall

Coordinates are three.js style (Y up, art faces +Z, origin on the wall at the
centre of the piece).
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
from loft_room import block, mat  # noqa: E402
from pinball import _image_emissive  # noqa: E402


def _px_image(name, w, h, fn):
    img = bpy.data.images.get(name)
    if img:
        return img
    img = bpy.data.images.new(name, w, h)
    px = [0.0] * (w * h * 4)
    for y in range(h):
        for x in range(w):
            r, g, b = fn(x / (w - 1), y / (h - 1))
            i = (y * w + x) * 4
            px[i:i + 4] = (r, g, b, 1.0)
    img.pixels = px
    img.pack()
    return img


def _skyline_image():
    """Night city skyline: purple-magenta sky, neon moon ring, dark towers with lit windows."""
    w, h = 400, 220
    rng = random.Random(9)
    mag, cyan, amber = _hex("#ff2bd6"), _hex("#22e4ff"), _hex("#ffb020")
    # tower layout: (x0, x1, top) in 0..1 units, back row then front row
    towers = []
    x = 0.0
    while x < 1.0:
        tw = rng.uniform(0.03, 0.08)
        towers.append((x, x + tw, rng.uniform(0.35, 0.75), 0))
        x += tw + rng.uniform(0.0, 0.01)
    x = 0.0
    while x < 1.0:
        tw = rng.uniform(0.04, 0.1)
        towers.append((x, x + tw, rng.uniform(0.18, 0.5), 1))
        x += tw + rng.uniform(0.01, 0.04)
    win_seed = {i: rng.random() for i in range(len(towers))}

    def fn(u, v):
        # sky gradient
        r, g, b = 0.05 + 0.25 * v ** 2, 0.01 + 0.02 * v, 0.1 + 0.12 * v
        # neon moon ring
        d = math.hypot((u - 0.72) * 1.8, v - 0.72)
        if abs(d - 0.12) < 0.008:
            r, g, b = mag
        elif d < 0.12:
            r, g, b = r + 0.08, g + 0.02, b + 0.1
        # horizon haze
        haze = math.exp(-((v - 0.3) / 0.12) ** 2) * 0.25
        r, g, b = r + haze * mag[0], g + haze * mag[1] * 0.4, b + haze * mag[2]
        # towers (front row drawn last = on top)
        for i, (x0, x1, top, row) in enumerate(towers):
            if x0 <= u <= x1 and v <= top:
                shade = 0.02 if row else 0.05
                r, g, b = shade, shade * 0.8, shade * 1.6
                # windows grid
                cu = int((u - x0) * 160)
                cv = int(v * 110)
                if cu % 3 == 1 and cv % 3 == 1 and v < top - 0.02:
                    hsh = (cu * 7 + cv * 13 + int(win_seed[i] * 97)) % 11
                    if hsh < 3:
                        r, g, b = amber if hsh else cyan
                # rooftop neon strip on some front towers
                if row and top - 0.012 < v <= top and win_seed[i] > 0.6:
                    r, g, b = cyan
        return r, g, b

    return _px_image("WallArtSkyline", w, h, fn)


def _poster_image(art):
    mag, cyan, yel = _hex("#ff2bd6"), _hex("#22e4ff"), _hex("#ffd21a")

    def circles(u, v):
        d = math.hypot(u - 0.5, (v - 0.55) * 1.3)
        ringn = int(d * 22)
        if ringn % 2 == 0 and d < 0.42:
            return mag if ringn % 4 == 0 else cyan
        return (0.03, 0.01, 0.06)

    def stripes(u, v):
        if abs((u + v * 0.6) % 0.18 - 0.09) < 0.03 and v < 0.75:
            return cyan
        if v > 0.72 and abs(u - 0.5) < (0.95 - v) * 1.2:
            return yel
        return (0.02, 0.02, 0.05)

    def wave(u, v):
        y = 0.5 + 0.15 * math.sin(u * 10)
        for k in range(6):
            if abs(v - (y - 0.06 * k + 0.12)) < 0.008:
                return mag if k % 2 else cyan
        if abs((u * 12) % 1 - 0.5) < 0.03 and v < 0.3:
            return (0.15, 0.05, 0.25)
        return (0.03, 0.0, 0.05)

    fn = {"circles": circles, "stripes": stripes, "wave": wave}[art]
    return _px_image(f"WallArtPoster_{art}", 96, 128, fn)


def _plane(name, c, w, h, m, parent):
    bpy.ops.mesh.primitive_plane_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.scale = (w, h, 1)
    o.location = P(*c)
    o.rotation_euler = (math.pi / 2, 0, 0)
    o.data.materials.append(m)
    o.parent = parent
    return o


def build_led_mural(parent=None, name="LEDMural", w=4.0, h=2.2):
    FRAME = mat("MuralFrame", "#0b0c0e", 0.35, metal=0.7)
    STEEL = mat("MuralSteel", "#2a2c31", 0.3, metal=0.9)
    CYAN = mat("MuralCyan", "#22e4ff", emit="#22e4ff", strength=8.0)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    block(f"{name}Body", (0, 0, 0.05), (w + 0.1, h + 0.1, 0.08), FRAME, root, r=0.01)
    _plane(f"{name}Screen", (0, 0, 0.092), w, h, _image_emissive("WallArt_Skyline", _skyline_image(), 1.5), root)
    block(f"{name}TopGlow", (0, h / 2 + 0.06, 0.08), (w - 0.2, 0.012, 0.012), CYAN, root)
    for s in (-1, 1):  # wall brackets
        block(f"{name}Bracket{s}", (s * (w / 2 - 0.3), h / 2 + 0.02, 0.02), (0.12, 0.16, 0.04), STEEL, root)
        block(f"{name}BracketLow{s}", (s * (w / 2 - 0.3), -h / 2 - 0.02, 0.02), (0.12, 0.16, 0.04), STEEL, root)
    return root


def build_poster(parent=None, name="Poster", art="circles", glow="#ff2bd6", w=0.6, h=0.8):
    FRAME = mat("PosterFrame", "#0b0c0e", 0.35, metal=0.6)
    NEON = mat(f"PosterNeon_{glow}", glow, emit=glow, strength=8.0)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    block(f"{name}Frame", (0, 0, 0.015), (w + 0.06, h + 0.06, 0.03), FRAME, root, r=0.004)
    _plane(f"{name}Art", (0, 0, 0.032), w, h, _image_emissive(f"WallArt_Poster_{art}", _poster_image(art), 1.2), root)
    for k, (x, y, sx, sy) in enumerate(((0, h / 2 + 0.03, w + 0.06, 0.01), (0, -h / 2 - 0.03, w + 0.06, 0.01),
                                        (-w / 2 - 0.03, 0, 0.01, h + 0.06), (w / 2 + 0.03, 0, 0.01, h + 0.06))):
        block(f"{name}Neon{k}", (x, y, 0.034), (sx, sy, 0.01), NEON, root)
    return root


def build_wall_art_preview(parent=None, name="WallArtPreview"):
    """Preview only: mural above three posters on a dark concrete wall."""
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    wall = mat("PreviewConcrete", "#1c1c1e", 0.9)
    block(f"{name}Wall", (0, 1.9, -0.06), (5.6, 3.8, 0.1), wall, root)
    m = build_led_mural(root, f"{name}Mural")
    m.location = P(0, 2.55, 0)
    for k, (x, art, col) in enumerate(((-1.1, "circles", "#ff2bd6"), (0.0, "stripes", "#22e4ff"), (1.1, "wave", "#ffd21a"))):
        p = build_poster(root, f"{name}Poster{k}", art=art, glow=col)
        p.location = P(x, 0.75, 0)
    return root

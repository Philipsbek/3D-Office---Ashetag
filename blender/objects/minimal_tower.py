"""
Minimalist tower for the ASHETAG office, replacing the condo box and the
loft's solid back/left walls (style ref: floor-to-ceiling corner glazing with
thin black frames meeting glass-to-glass, a thin white ceiling slab with
recessed lights). Kept cyberpunk with a few precise neon lines.

    build_minimal_tower(parent=None, name="MinimalTower")
        Same footprint as the condo under the office: x -7.3..8.8, z -6.3..4.3.
        Ground at y = 0; nine 4 m floors below; the office level sits on top at
        y = 36 (its floor = the site's y = 0), 6.8 m tall, then the roof slab.
        Every floor uses the office level's glazing: floor-to-ceiling glass, one
        slim mullion per wall, thin black sill and head, frameless glass corners.
        The office level has glass on the back (-Z) and left (-X) only; front and
        right stay open for the camera, like the current cutaway room.
    build_minimal_tower_preview(parent, name) -> tower + a glimpse of a lit interior

Coordinates are three.js style (Y up).
"""

import math
import os
import random  # preview city glow
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P  # noqa: E402
from glass_room import glass_mat  # noqa: E402
from loft_room import mat, slab  # noqa: E402

XA, XB = -7.3, 8.8
ZA, ZB = -6.3, 4.3
FLOORS, FH = 9, 4.0
OFFICE_Y = FLOORS * FH  # 36: the office floor
OFFICE_H = 6.8


def _dark_glass():
    """Near-black glazing: no interior shows, only a glossy sheen picking up the city."""
    m = mat("MinDarkGlass", "#05070c", 0.04)
    b = m.node_tree.nodes["Principled BSDF"]
    for name, val in (("Specular IOR Level", 0.9), ("IOR", 1.52)):
        if name in b.inputs:
            b.inputs[name].default_value = val
    return m


def _mats():
    return {
        "slab": mat("MinSlab", "#1a1b21", 0.5),
        "edge": mat("MinSlabEdge", "#d9dbe2", 0.35),  # crisp light slab edge, minimalist accent
        "ceiling": mat("MinCeiling", "#eceef2", 0.6),
        "frame": mat("MinFrame", "#2c2e36", 0.35, metal=0.6),
        "glass": glass_mat("MinGlass", "#8fa6c8", 0.18),
        # lower floors: dark, mirror-like glass that only picks up the city's light
        "darkGlass": _dark_glass(),
        "core": mat("MinCore", "#202128", 0.7),
        "downlight": mat("MinDownlight", "#ffffff", emit="#fff4e0", strength=10.0),
        "cyan": mat("MinNeonCyan", "#22e4ff", emit="#22e4ff", strength=9.0),
        "pink": mat("MinNeonPink", "#ff4fd8", emit="#ff4fd8", strength=9.0),
    }


def build_minimal_tower(parent=None, name="MinimalTower", seed=5, include_office=True):
    """include_office=False: just the floors under the office (the site builds the
    office level itself, as the open cutaway loft with the same glass corner)."""
    M = _mats()
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---- lower floors: dark reflective glass (no interiors shown), a slim slab between
    for f in range(FLOORS):
        y0 = f * FH
        # the glass skin (all four sides, glass-to-glass corners)
        for side, (x0, x1, z0, z1) in enumerate(((XA, XB, ZA - 0.01, ZA + 0.01), (XA, XB, ZB - 0.01, ZB + 0.01),
                                                  (XA - 0.01, XA + 0.01, ZA, ZB), (XB - 0.01, XB + 0.01, ZA, ZB))):
            slab(f"{name}Glass{f}_{side}", x0, x1, y0 + 0.15, y0 + FH - 0.15, z0, z1, M["darkGlass"], root)
        # floor slab: dark, with a thin light edge band (the minimalist line)
        # the top slab sits just under the site's own office floor (top at -0.13) so it never pokes through it
        dy = -0.28 if (f == FLOORS - 1 and not include_office) else 0.0
        slab(f"{name}Slab{f}", XA - 0.12, XB + 0.12, y0 + FH - 0.15 + dy, y0 + FH + 0.15 + dy, ZA - 0.12, ZB + 0.12, M["slab"], root)
        for k, (x0, x1, z0, z1) in enumerate(((XA - 0.13, XB + 0.13, ZA - 0.13, ZA - 0.11), (XA - 0.13, XB + 0.13, ZB + 0.11, ZB + 0.13),
                                               (XA - 0.13, XA - 0.11, ZA - 0.13, ZB + 0.13), (XB + 0.11, XB + 0.13, ZA - 0.13, ZB + 0.13))):
            slab(f"{name}SlabEdge{f}_{k}", x0, x1, y0 + FH - 0.05 + dy, y0 + FH + 0.05 + dy, z0, z1, M["edge"], root)
    # same glazing as the office level on every floor: two big panes per wall
    # (one slim mullion in the middle), thin black sill and head, glass-to-glass corners
    for f in range(FLOORS):
        y0, y1 = f * FH + 0.15, (f + 1) * FH - 0.15
        for k, (x0, x1, z0, z1) in enumerate(((XA, XB, ZA - 0.04, ZA + 0.04), (XA, XB, ZB - 0.04, ZB + 0.04),
                                               (XA - 0.04, XA + 0.04, ZA, ZB), (XB - 0.04, XB + 0.04, ZA, ZB))):
            slab(f"{name}FSill{f}_{k}", x0, x1, y0, y0 + 0.06, z0, z1, M["frame"], root)
            slab(f"{name}FHead{f}_{k}", x0, x1, y1 - 0.06, y1, z0, z1, M["frame"], root)
        xm, zm = (XA + XB) / 2, (ZA + ZB) / 2
        for k, z in enumerate((ZA, ZB)):
            slab(f"{name}FMullX{f}_{k}", xm - 0.03, xm + 0.03, y0, y1, z - 0.04, z + 0.04, M["frame"], root)
        for k, x in enumerate((XA, XB)):
            slab(f"{name}FMullZ{f}_{k}", x - 0.04, x + 0.04, y0, y1, zm - 0.03, zm + 0.03, M["frame"], root)
    # lobby: deep dark canopy over the entrance with a cyan line, plinth
    slab(f"{name}Canopy", XA + 2.0, XB - 2.0, FH - 0.2, FH + 0.05, ZB, ZB + 2.4, M["slab"], root)
    slab(f"{name}CanopyNeon", XA + 2.0, XB - 2.0, FH - 0.24, FH - 0.2, ZB + 2.34, ZB + 2.4, M["cyan"], root)
    slab(f"{name}Plinth", XA - 0.4, XB + 0.4, -0.05, 0.15, ZA - 0.4, ZB + 0.4, M["slab"], root)
    # (the pink corner neon line was removed at the user's request, 2026-11-22)
    if not include_office:
        return root

    # ---- office level: glass back + left walls, one slim mullion each, glass corner
    oy = OFFICE_Y
    slab(f"{name}OfficeFloor", XA, XB, oy - 0.15, oy, ZA, ZB, M["slab"], root)
    for k, (x0, x1, z0, z1) in enumerate(((XA, XB, ZA - 0.01, ZA + 0.01), (XA - 0.01, XA + 0.01, ZA, ZB))):
        slab(f"{name}OfficeGlass{k}", x0, x1, oy + 0.06, oy + OFFICE_H - 0.06, z0, z1, M["glass"], root)
    # thin black frame: sill and head on both glass walls, one mid mullion each
    for k, (x0, x1, z0, z1) in enumerate(((XA, XB, ZA - 0.04, ZA + 0.04), (XA - 0.04, XA + 0.04, ZA, ZB))):
        slab(f"{name}Sill{k}", x0, x1, oy, oy + 0.06, z0, z1, M["frame"], root)
        slab(f"{name}Head{k}", x0, x1, oy + OFFICE_H - 0.06, oy + OFFICE_H, z0, z1, M["frame"], root)
    slab(f"{name}MullBack", (XA + XB) / 2 - 0.03, (XA + XB) / 2 + 0.03, oy, oy + OFFICE_H, ZA - 0.04, ZA + 0.04, M["frame"], root)
    slab(f"{name}MullLeft", XA - 0.04, XA + 0.04, oy, oy + OFFICE_H, (ZA + ZB) / 2 - 0.03, (ZA + ZB) / 2 + 0.03, M["frame"], root)
    # roof: thin white ceiling slab with recessed downlights, dark top, neon crown line
    slab(f"{name}Ceiling", XA - 0.3, XB + 0.3, oy + OFFICE_H, oy + OFFICE_H + 0.12, ZA - 0.3, ZB + 0.3, M["ceiling"], root)
    slab(f"{name}Roof", XA - 0.3, XB + 0.3, oy + OFFICE_H + 0.12, oy + OFFICE_H + 0.45, ZA - 0.3, ZB + 0.3, M["slab"], root)
    for k, (x0, x1, z0, z1) in enumerate(((XA - 0.32, XB + 0.32, ZA - 0.32, ZA - 0.29), (XA - 0.32, XA - 0.29, ZA - 0.32, ZB + 0.32),
                                           (XA - 0.32, XB + 0.32, ZB + 0.29, ZB + 0.32), (XB + 0.29, XB + 0.32, ZA - 0.32, ZB + 0.32))):
        slab(f"{name}Crown{k}", x0, x1, oy + OFFICE_H + 0.2, oy + OFFICE_H + 0.27, z0, z1, M["cyan"], root)
    for i in range(4):
        for j in range(2):
            x = XA + 2.2 + i * 3.8
            z = ZA + 2.2 + j * 5.0
            slab(f"{name}Down{i}{j}", x - 0.18, x + 0.18, oy + OFFICE_H - 0.01, oy + OFFICE_H, z - 0.05, z + 0.05, M["downlight"], root)
    # rooftop: low plant box and a slim mast with a red beacon, kept minimal
    slab(f"{name}RoofBox", XA + 9.0, XB - 1.5, oy + OFFICE_H + 0.45, oy + OFFICE_H + 1.6, ZA + 1.5, ZA + 4.5, M["core"], root)
    slab(f"{name}Mast", XA + 1.4, XA + 1.5, oy + OFFICE_H + 0.45, oy + OFFICE_H + 5.0, ZA + 1.4, ZA + 1.5, M["frame"], root)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, segments=12, ring_count=8, location=P(XA + 1.45, oy + OFFICE_H + 5.15, ZA + 1.45))
    b = bpy.context.active_object
    b.name = f"{name}Beacon"
    b.data.materials.append(mat("MinBeacon", "#ff2020", emit="#ff2020", strength=14.0))
    b.parent = root
    return root


def build_minimal_tower_preview(parent=None, name="MinimalTowerPreview"):
    """Preview only: the tower plus a warm-lit office floor so the glass corner reads."""
    root = build_minimal_tower(parent, name)
    oy = OFFICE_Y
    warmfloor = mat("PreviewOfficeFloor", "#3a2c3a", 0.5, emit="#5a2a6a", strength=0.6)
    slab(f"{name}OfficeGlowFloor", XA + 0.2, XB - 0.2, oy, oy + 0.02, ZA + 0.2, ZB - 0.2, warmfloor, root)
    # a few furniture-ish silhouettes and neon accents inside
    dark = mat("PreviewFurniture", "#121217", 0.6)
    for k, (x, z, w, d, h) in enumerate(((-3.5, -4.5, 3.0, 1.0, 0.9), (2.5, -1.5, 3.4, 1.4, 0.8), (-5.5, 0.5, 1.2, 2.6, 2.0))):
        slab(f"{name}Furn{k}", x - w / 2, x + w / 2, oy, oy + h, z - d / 2, z + d / 2, dark, root)
    pinkglow = mat("MinNeonPink", "#ff4fd8", emit="#ff4fd8", strength=9.0)
    cyanglow = mat("MinNeonCyan", "#22e4ff", emit="#22e4ff", strength=9.0)
    slab(f"{name}SofaNeon", 0.8, 4.2, oy + 0.1, oy + 0.14, -0.8, -0.76, pinkglow, root)
    slab(f"{name}DeskNeon", -5.0, -2.0, oy + 0.88, oy + 0.92, -4.0, -3.96, cyanglow, root)
    # preview-only city round the tower so the dark glass has something to reflect
    rng = random.Random(3)
    for k in range(36):
        ang = k / 36 * 2 * math.pi + rng.uniform(-0.05, 0.05)
        rad = rng.uniform(110, 150)
        w, h = rng.uniform(8, 16), rng.uniform(20, 70)
        x, z = 0.75 + math.cos(ang) * rad, -1 + math.sin(ang) * rad
        slab(f"{name}CityBlock{k}", x - w / 2, x + w / 2, 0, h, z - w / 2, z + w / 2, mat("PreviewCityBlock", "#0c0b14", 0.8), root)
        col = rng.choice(("#22e4ff", "#ff4fd8", "#ffb82e", "#ffd9a8"))
        for j in range(rng.randint(3, 7)):
            yy = rng.uniform(4, h - 2)
            slab(f"{name}CityLit{k}_{j}", x - w / 2 - 0.05, x + w / 2 + 0.05, yy, yy + rng.uniform(0.4, 2.0), z - w / 2 - 0.05, z + w / 2 + 0.05,
                 mat(f"PreviewCityLit{col[1:]}", col, emit=col, strength=3.0), root)
    for n, pos, col, e, sz in (("Inside", (0.75, oy + 4.5, -1.0), (1.0, 0.6, 0.9), 1800, 3), ("Fill", (-40, 40, -40), (0.55, 0.5, 1.0), 25000, 12),
                               ("Street", (-20, 6, -25), (0.9, 0.5, 1.0), 20000, 6)):
        ld = bpy.data.lights.new(n, "POINT")
        ld.color = col
        ld.energy = e
        ld.shadow_soft_size = sz
        ld.specular_factor = 0.3
        lo = bpy.data.objects.new(n, ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(*pos)
    return root

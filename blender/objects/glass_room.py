"""
Cyberpunk glass room for the loft's lower-left front corner: a black steel
frame with tinted glass walls and a glass roof (so the lobby camera can see
in), a sliding glass door with a long handle, a frosted privacy band, neon
trim along the roof edge, and a raised floor with an edge light.

    build_glass_room(parent=None, name="GlassRoom", w=3.2, d=3.0, h=2.6) -> root

Coordinates are three.js style (Y up). Origin at the centre of the footprint on
the floor; the door is on the front (+Z) side. Glass uses alpha blending, which
the website shows as see-through.
"""

import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P, _hex  # noqa: E402
from gaming_desk import tube  # noqa: E402
from loft_room import block, mat  # noqa: E402

POST = 0.07  # frame profile thickness
PLAT = 0.12  # raised floor height


def glass_mat(name, color, alpha, rough=0.05):
    m = bpy.data.materials.get("Glass_" + name)
    if m:
        return m
    m = bpy.data.materials.new("Glass_" + name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*_hex(color), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Alpha"].default_value = alpha
    for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
        try:
            setattr(m, attr, val)
        except Exception:
            pass
    m.diffuse_color = (*_hex(color), alpha)
    return m


def build_glass_room(parent=None, name="GlassRoom", w=3.2, d=3.0, h=2.6):
    STEEL = mat("GlassRoomSteel", "#121316", 0.35, metal=0.85)
    FLOOR = mat("GlassRoomFloor", "#0d0e11", 0.3, metal=0.4)
    HANDLE = mat("GlassRoomHandle", "#9aa0a6", 0.15, metal=1.0)
    CYAN = mat("GlassRoomCyan", "#22e4ff", emit="#22e4ff", strength=8.0)
    MAG = mat("GlassRoomMagenta", "#ff2bd6", emit="#ff2bd6", strength=7.0)
    GLASS = glass_mat("Tint", "#7fc8ff", 0.16)
    FROST = glass_mat("Frost", "#d8ecff", 0.55, rough=0.6)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    x0, x1, z0, z1 = -w / 2, w / 2, -d / 2, d / 2
    top = PLAT + h

    # ---------- raised floor with a cyan edge light around the front and sides
    block(f"{name}Floor", (0, PLAT / 2, 0), (w, PLAT, d), FLOOR, root, r=0.01)
    block(f"{name}FloorGlowFront", (0, 0.03, z1 + 0.004), (w - 0.1, 0.012, 0.008), CYAN, root)
    for s in (-1, 1):
        block(f"{name}FloorGlowSide{s}", (s * (x1 + 0.004), 0.03, 0), (0.008, 0.012, d - 0.1), CYAN, root)

    # ---------- steel frame: corner posts, mid posts, top + bottom rails, roof beams
    posts = [(x0, z0), (x1, z0), (x0, z1), (x1, z1), (0, z0), (x0, 0), (x1, 0)]
    for k, (px, pz) in enumerate(posts):
        block(f"{name}Post{k}", (px, PLAT + h / 2, pz), (POST, h, POST), STEEL, root)
    for k, (cx, cz, sx, sz) in enumerate(((0, z0, w, POST), (0, z1, w, POST), (x0, 0, POST, d), (x1, 0, POST, d))):
        block(f"{name}TopRail{k}", (cx, top, cz), (sx + POST, POST, sz + POST), STEEL, root)
        block(f"{name}BottomRail{k}", (cx, PLAT + POST / 2, cz), (sx, POST, sz), STEEL, root)
    for k in range(1, 3):  # roof beams across the width
        block(f"{name}RoofBeam{k}", (0, top, z0 + k * d / 3), (w, POST * 0.8, POST * 0.8), STEEL, root)

    # ---------- glass: back, sides, fixed front panel, roof
    gt = 0.012
    gh = h - POST
    gy = PLAT + POST / 2 + gh / 2
    for k, (cx, cz, sx, sz) in enumerate(((-w / 4, z0, w / 2 - POST, gt), (w / 4, z0, w / 2 - POST, gt),
                                          (x0, -d / 4, gt, d / 2 - POST), (x0, d / 4, gt, d / 2 - POST),
                                          (x1, -d / 4, gt, d / 2 - POST), (x1, d / 4, gt, d / 2 - POST))):
        block(f"{name}Glass{k}", (cx, gy, cz), (sx, gh, sz), GLASS, root)
    # front: fixed panel on the left, sliding door on the right (slightly open)
    door_w = 1.05
    fixed_w = w - door_w - POST
    block(f"{name}GlassFront", (x0 + POST / 2 + fixed_w / 2, gy, z1), (fixed_w, gh, gt), GLASS, root)
    door_x = x1 - POST / 2 - door_w / 2 - 0.25  # slid 25 cm open
    block(f"{name}Door", (door_x, gy, z1 + 0.04), (door_w, gh, gt), GLASS, root)
    block(f"{name}DoorTrack", (x1 - door_w / 2 - 0.2, top - POST, z1 + 0.04), (door_w * 1.6, 0.04, 0.04), STEEL, root)
    for s in (-1, 1):  # thin steel edges on the door
        block(f"{name}DoorEdge{s}", (door_x + s * door_w / 2, gy, z1 + 0.04), (0.025, gh, 0.025), STEEL, root)
    tube(f"{name}DoorHandle", [(door_x - door_w / 2 + 0.12, 0.8, z1 + 0.075), (door_x - door_w / 2 + 0.12, 1.6, z1 + 0.075)], 0.014, HANDLE, root)
    for k, y in enumerate((0.8, 1.6)):
        block(f"{name}HandleMount{k}", (door_x - door_w / 2 + 0.12, y, z1 + 0.06), (0.02, 0.02, 0.04), HANDLE, root)
    # glass roof between the rails
    block(f"{name}GlassRoof", (0, top + POST / 2 - 0.004, 0), (w - POST, gt, d - POST), GLASS, root)

    # ---------- frosted privacy band around the walls (door included)
    by, bh = PLAT + 1.05, 0.32
    for k, (cx, cz, sx, sz) in enumerate(((0, z0 + 0.008, w - POST, 0.004), (x0 + 0.008, 0, 0.004, d - POST),
                                          (x1 - 0.008, 0, 0.004, d - POST), (x0 + POST / 2 + fixed_w / 2, z1 - 0.008, fixed_w, 0.004))):
        block(f"{name}Frost{k}", (cx, by, cz), (sx, bh, sz), FROST, root)
    block(f"{name}FrostDoor", (door_x, by, z1 + 0.032), (door_w - 0.04, bh, 0.004), FROST, root)

    # ---------- neon trim along the roof edge (cyan) + a magenta line on the door track
    for k, (cx, cz, sx, sz) in enumerate(((0, z1 + POST / 2 + 0.006, w + POST, 0.012), (x0 - POST / 2 - 0.006, 0, 0.012, d + POST),
                                          (x1 + POST / 2 + 0.006, 0, 0.012, d + POST))):
        block(f"{name}RoofNeon{k}", (cx, top - POST / 2 - 0.012, cz), (sx, 0.016, sz), CYAN, root)  # just under the top rail
    block(f"{name}DoorNeon", (x1 - door_w / 2 - 0.2, top - POST - 0.03, z1 + 0.065), (door_w * 1.5, 0.01, 0.01), MAG, root)

    # preview-only lights: soft cyan glow inside and around (lights aren't exported)
    for k, (lx, ly, lz, col, en) in enumerate(((0, top - 0.3, 0, (0.6, 0.9, 1.0), 60), (0, 0.2, z1 + 0.5, (0.13, 0.89, 1.0), 8))):
        ld = bpy.data.lights.new(f"{name}GlowLight{k}", "POINT")
        ld.color = col
        ld.energy = en
        ld.shadow_soft_size = 0.5
        lo = bpy.data.objects.new(f"{name}GlowLight{k}", ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(lx, ly, lz)
        lo.parent = root
    return root

"""
Cyberpunk lounge table + stools for the loft's lower-middle zone: a long black
slab table on two waterfall legs with a cyan light strip under its front edge,
a steel footrest bar, a cable tray, a few props, and round stools with black
leather seats, foot rings and a cyan glow ring under each seat.

The table is desk height (top 0.76 m) and the stool seats are 0.51 m, the
same as the gaming desk/chair, so the sleeping character can nap at it.

    build_lounge_stool(parent=None, name="LoungeStool") -> root empty
    build_lounge_table(parent=None, name="LoungeTable", stools=3) -> root empty

Coordinates are three.js style (Y up). The table's long side runs along X and
its front (where people sit) faces +Z; origin at the centre of the table on
the floor. Stools come with it on the +Z side (one pushed out at an angle).
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

TL, TD, TOP = 2.4, 0.7, 0.76  # table length, depth, top height
SEAT = 0.51


def build_lounge_stool(parent=None, name="LoungeStool"):
    LEATHER = mat("StoolLeather", "#111114", 0.55)
    STEEL = mat("StoolSteel", "#1c1d21", 0.35, metal=0.9)
    CHROME = mat("StoolChrome", "#8d9298", 0.15, metal=1.0)
    CYAN = mat("StoolCyan", "#22e4ff", emit="#22e4ff", strength=7.0)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # padded round seat with a stitched rim
    disc(f"{name}Seat", (0, SEAT - 0.04, 0), 0.19, 0.08, LEATHER, root, verts=40)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.19, segments=40, ring_count=12)
    cush = bpy.context.active_object
    cush.name = f"{name}Cushion"
    cush.scale = (1, 1, 0.16)
    cush.location = P(0, SEAT, 0)
    bpy.ops.object.shade_smooth()
    cush.data.materials.append(LEATHER)
    cush.parent = root
    ring(f"{name}SeatGlow", (0, SEAT - 0.085, 0), 0.15, 0.006, CYAN, root)
    disc(f"{name}SeatPlate", (0, SEAT - 0.09, 0), 0.1, 0.02, STEEL, root)
    # four splayed legs, a chrome foot ring and rubber feet
    for k in range(4):
        a = math.radians(45 + 90 * k)
        tx, tz = 0.08 * math.cos(a), 0.08 * math.sin(a)
        bx, bz = 0.2 * math.cos(a), 0.2 * math.sin(a)
        tube(f"{name}Leg{k}", [(tx, SEAT - 0.1, tz), (bx, 0.02, bz)], 0.014, STEEL, root)
        disc(f"{name}Foot{k}", (bx, 0.01, bz), 0.02, 0.02, STEEL, root)
    ring(f"{name}FootRing", (0, 0.2, 0), 0.165, 0.009, CHROME, root)
    return root


def build_lounge_table(parent=None, name="LoungeTable", stools=3):
    SLAB = mat("TableSlab", "#0e0f12", 0.3, metal=0.3)
    EDGE = mat("TableEdge", "#1f2126", 0.25, metal=0.85)
    STEEL = mat("TableSteel", "#26282d", 0.35, metal=0.9)
    CYAN = mat("TableCyan", "#22e4ff", emit="#22e4ff", strength=8.0)
    CAN = mat("TableCan", "#1a1a1d", 0.25, metal=0.9)
    CAN_BAND = mat("TableCanBand", "#ff2bd6", emit="#ff2bd6", strength=2.0)
    TABLET = mat("TableTablet", "#08090b", 0.15, emit="#1d6f8a", strength=0.5)
    PAPER = mat("TablePaper", "#2b2d33", 0.8)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---------- slab top + steel edge band
    block(f"{name}Top", (0, TOP - 0.03, 0), (TL, 0.06, TD), SLAB, root, r=0.006)
    block(f"{name}EdgeFront", (0, TOP - 0.03, TD / 2 + 0.004), (TL, 0.062, 0.008), EDGE, root)
    block(f"{name}EdgeBack", (0, TOP - 0.03, -TD / 2 - 0.004), (TL, 0.062, 0.008), EDGE, root)
    # cyan strip tucked under the front edge
    block(f"{name}UnderGlow", (0, TOP - 0.066, TD / 2 - 0.04), (TL - 0.2, 0.008, 0.012), CYAN, root)

    # ---------- waterfall legs, footrest bar, cable tray
    for k, sx in enumerate((-1, 1)):
        x = sx * (TL / 2 - 0.25)
        block(f"{name}Leg{k}", (x, (TOP - 0.06) / 2, 0), (0.06, TOP - 0.06, TD - 0.06), SLAB, root, r=0.006)
        block(f"{name}LegGlow{k}", (x + sx * 0.032, 0.35, TD / 2 - 0.06), (0.004, 0.5, 0.01), CYAN, root)
    tube(f"{name}Footrest", [(-TL / 2 + 0.25, 0.18, TD / 2 - 0.12), (TL / 2 - 0.25, 0.18, TD / 2 - 0.12)], 0.016, STEEL, root)
    block(f"{name}CableTray", (0, TOP - 0.16, -TD / 2 + 0.12), (TL - 0.7, 0.05, 0.14), STEEL, root)

    # ---------- props: two cans, a glowing tablet, a few papers
    for k, (cx, cz) in enumerate(((0.75, 0.05), (0.86, -0.06))):
        disc(f"{name}Can{k}", (cx, TOP + 0.062, cz), 0.033, 0.124, CAN, root)
        ring(f"{name}CanBand{k}", (cx, TOP + 0.07, cz), 0.034, 0.004, CAN_BAND, root)
    tb = block(f"{name}Tablet", (-0.75, TOP + 0.005, 0.02), (0.26, 0.01, 0.18), TABLET, root, r=0.004)
    tb.rotation_euler = (0, 0, math.radians(-12))
    for k, (px, pz, rot) in enumerate(((0.3, -0.1, 8), (0.38, -0.04, -14))):
        pa = block(f"{name}Paper{k}", (px, TOP + 0.001 + k * 0.001, pz), (0.21, 0.002, 0.297), PAPER, root)
        pa.rotation_euler = (0, 0, math.radians(rot))

    # ---------- stools on the front side (one pushed out at an angle)
    spots = [(-0.75, TD / 2 + 0.25, 0), (0.0, TD / 2 + 0.3, 0), (0.78, TD / 2 + 0.55, 25)][:stools]
    for k, (sx, sz, rot) in enumerate(spots):
        st = build_lounge_stool(root, name=f"{name}Stool{k}")
        st.location = P(sx, 0, sz)
        st.rotation_euler = (0, 0, math.radians(rot))

    # preview-only cyan lights so the glow strips visibly light things (not exported)
    glows = [(-0.6, TOP - 0.12, TD / 2 + 0.05, 14), (0.6, TOP - 0.12, TD / 2 + 0.05, 14)]
    glows += [(sx, SEAT - 0.14, sz, 6) for sx, sz, _ in spots]
    for k, (lx, ly, lz, w) in enumerate(glows):
        ld = bpy.data.lights.new(f"{name}GlowLight{k}", "POINT")
        ld.color = (0.13, 0.89, 1.0)
        ld.energy = w
        ld.shadow_soft_size = 0.2
        lo = bpy.data.objects.new(f"{name}GlowLight{k}", ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(lx, ly, lz)
        lo.parent = root

    return root

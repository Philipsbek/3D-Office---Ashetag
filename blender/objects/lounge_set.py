"""
Cyberpunk lounge set for the loft's open lower floor: a large dark rug with a
neon edge and faint stripes, a low black L-shaped sectional sofa (padded seat
and back cushions, magenta underglow, cyan/magenta throw pillows), and a low
coffee table with a cyan edge and a small hologram projector on top.

    build_lounge_set(parent=None, name="LoungeSet") -> root empty

Coordinates are three.js style (Y up). The sofa faces +Z; the chaise sticks
out toward +Z on the right (+X). Origin at the centre of the rug on the floor.
"""

import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P, rounded_box  # noqa: E402
from gaming_desk import disc, ring  # noqa: E402
from loft_room import block, mat  # noqa: E402
from glass_room import glass_mat  # noqa: E402

RUG_W, RUG_D = 3.4, 2.6
SEAT_Y = 0.42  # top of the seat cushions


def _sofa_section(name, cx, cz, w, d, back, M, root):
    """One sofa block: plinth with underglow, base, seat cushions, optional back cushions."""
    block(f"{name}Plinth", (cx, 0.04, cz), (w - 0.08, 0.08, d - 0.08), M["plinth"], root)
    block(f"{name}Base", (cx, 0.2, cz), (w, 0.24, d), M["frame"], root, r=0.02)
    # seat cushions (split into equal pads along the longer side)
    n = max(1, round(max(w, d) / 0.8))
    along_x = w >= d
    for k in range(n):
        if along_x:
            px = cx - w / 2 + (k + 0.5) * w / n
            rounded_box(f"{name}Seat{k}", (px, SEAT_Y - 0.06, cz + (0.08 if back else 0)), (w / n - 0.03, 0.14, d - (0.22 if back else 0.04)), 0.05, M["cushion"], root)
        else:
            pz = cz - d / 2 + (k + 0.5) * d / n
            rounded_box(f"{name}Seat{k}", (cx, SEAT_Y - 0.06, pz), (w - 0.04, 0.14, d / n - 0.03), 0.05, M["cushion"], root)
    if back:
        for k in range(n):
            px = cx - w / 2 + (k + 0.5) * w / n
            c = rounded_box(f"{name}Back{k}", (px, SEAT_Y + 0.2, cz - d / 2 + 0.12), (w / n - 0.04, 0.42, 0.2), 0.07, M["cushion"], root)
            c.rotation_euler = (math.radians(-8), 0, 0)  # leans back slightly
        block(f"{name}BackFrame", (cx, 0.4, cz - d / 2 + 0.04), (w, 0.56, 0.08), M["frame"], root, r=0.02)


def build_lounge_set(parent=None, name="LoungeSet"):
    M = {
        "rug": mat("RugDark", "#141419", 0.95),
        "stripe": mat("RugStripe", "#1f2029", 0.95),
        "frame": mat("SofaFrame", "#0d0d10", 0.5),
        "plinth": mat("SofaPlinth", "#050506", 0.8),
        "cushion": mat("SofaCushion", "#1c1d22", 0.75),
        "pillow_c": mat("PillowCyan", "#0f3a44", 0.8),
        "pillow_m": mat("PillowMagenta", "#4a1340", 0.8),
        "table": mat("CoffeeTable", "#0b0b0d", 0.15, metal=0.4),
        "steel": mat("CoffeeSteel", "#2a2c31", 0.3, metal=0.9),
        "cyan": mat("LoungeCyan", "#22e4ff", emit="#22e4ff", strength=8.0),
        "mag": mat("LoungeMagenta", "#ff2bd6", emit="#ff2bd6", strength=8.0),
        "holo": mat("HoloShape", "#7ff3ff", emit="#7ff3ff", strength=6.0),
    }
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---------- rug: dark base, faint stripes, neon edge
    block(f"{name}Rug", (0, 0.006, 0), (RUG_W, 0.012, RUG_D), M["rug"], root)
    for k in range(-3, 4):
        block(f"{name}RugStripe{k}", (k * 0.42, 0.0125, 0), (0.05, 0.002, RUG_D - 0.3), M["stripe"], root)
    for k, (cx, cz, sx, sz) in enumerate(((0, RUG_D / 2 - 0.08, RUG_W - 0.16, 0.012), (0, -RUG_D / 2 + 0.08, RUG_W - 0.16, 0.012),
                                          (RUG_W / 2 - 0.08, 0, 0.012, RUG_D - 0.16), (-RUG_W / 2 + 0.08, 0, 0.012, RUG_D - 0.16))):
        block(f"{name}RugNeon{k}", (cx, 0.013, cz), (sx, 0.004, sz), M["cyan"], root)

    # ---------- L-shaped sectional: long back section + chaise on the right
    sz0 = -RUG_D / 2 + 0.55  # back section centre (z)
    _sofa_section(f"{name}Main", -0.25, sz0, 2.4, 0.95, True, M, root)
    _sofa_section(f"{name}Chaise", 1.3, sz0 + 0.62, 0.9, 2.2, False, M, root)
    # chaise back + arm on the outer side
    block(f"{name}ChaiseArm", (1.73, 0.36, sz0 + 0.62), (0.12, 0.48, 2.2), M["frame"], root, r=0.03)
    block(f"{name}MainArm", (-1.47, 0.36, sz0), (0.12, 0.48, 0.95), M["frame"], root, r=0.03)
    # magenta underglow strips at the plinth
    block(f"{name}Glow0", (-0.25, 0.012, sz0 + 0.44), (2.2, 0.008, 0.01), M["mag"], root)
    block(f"{name}Glow1", (1.73, 0.012, sz0 + 0.62), (0.01, 0.008, 2.0), M["mag"], root)
    # throw pillows
    for k, (px, pz, rot, m) in enumerate(((-1.15, sz0 - 0.05, 12, "pillow_c"), (-0.65, sz0 - 0.02, -8, "pillow_m"), (1.45, sz0 - 0.05, -15, "pillow_c"))):
        p = rounded_box(f"{name}Pillow{k}", (px, SEAT_Y + 0.16, pz), (0.4, 0.38, 0.13), 0.06, M[m], root)
        p.rotation_euler = (math.radians(-14), 0, math.radians(rot))

    # ---------- coffee table with hologram projector
    tx, tz = -0.35, sz0 + 1.25
    block(f"{name}TableTop", (tx, 0.36, tz), (1.2, 0.05, 0.6), M["table"], root, r=0.01)
    block(f"{name}TableEdge", (tx, 0.36, tz + 0.304), (1.16, 0.012, 0.006), M["cyan"], root)
    block(f"{name}TableBase", (tx, 0.17, tz), (0.9, 0.34, 0.4), M["plinth"], root, r=0.01)
    disc(f"{name}HoloBase", (tx + 0.25, 0.4, tz), 0.07, 0.03, M["steel"], root)
    ring(f"{name}HoloRing", (tx + 0.25, 0.416, tz), 0.07, 0.006, M["cyan"], root)
    bpy.ops.mesh.primitive_cone_add(radius1=0.05, radius2=0.15, depth=0.3, vertices=24)
    beam = bpy.context.active_object
    beam.name = f"{name}HoloBeam"
    beam.location = P(tx + 0.25, 0.57, tz)
    beam.data.materials.append(glass_mat("HoloBeam", "#22e4ff", 0.12, rough=0.3))
    beam.parent = root
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.09, subdivisions=1)
    shape = bpy.context.active_object
    shape.name = f"{name}HoloShape"  # the site could spin this
    shape.location = P(tx + 0.25, 0.8, tz)
    wf = shape.modifiers.new("Wire", "WIREFRAME")
    wf.thickness = 0.006
    shape.data.materials.append(M["holo"])
    shape.parent = root
    # a couple of props: a can and a remote
    disc(f"{name}Can", (tx - 0.3, 0.445, tz + 0.08), 0.033, 0.124, M["steel"], root)
    rm = block(f"{name}Remote", (tx - 0.05, 0.39, tz - 0.1), (0.05, 0.02, 0.18), M["frame"], root, r=0.008)
    rm.rotation_euler = (0, 0, math.radians(20))

    # preview-only glow lights (lights aren't exported)
    for k, (lx, ly, lz, col, en) in enumerate(((-0.25, 0.05, sz0 + 0.6, (1.0, 0.17, 0.84), 10), (tx + 0.25, 0.8, tz, (0.13, 0.89, 1.0), 6))):
        ld = bpy.data.lights.new(f"{name}GlowLight{k}", "POINT")
        ld.color = col
        ld.energy = en
        ld.shadow_soft_size = 0.3
        lo = bpy.data.objects.new(f"{name}GlowLight{k}", ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(lx, ly, lz)
        lo.parent = root
    return root

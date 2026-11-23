"""
Cyberpunk electric moped for the loft's lower-right doorway zone: a matte-black
step-through scooter body, glowing orange wheel rims and underglow, a round
headlight with a light ring, a cyan dashboard, a red tail-light strip, a padded
seat and a centre stand.

    build_e_moped(parent=None, name="EMoped") -> root empty

Coordinates are three.js style (Y up). The moped points toward +X (seen side-on
from +Z); origin on the floor between the wheels.
"""

import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P, rounded_box  # noqa: E402
from gaming_desk import disc, ring, tube  # noqa: E402
from loft_room import block, mat  # noqa: E402

WR = 0.22  # wheel radius (tyre outer)
WX = 0.6  # wheel offset from the centre


def _blob(name, c, scale, m, parent, rot=(0, 0, 0)):
    """A smooth stretched sphere for curvy body panels."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=40, ring_count=20)
    o = bpy.context.active_object
    o.name = name
    o.location = P(*c)
    o.scale = (scale[0], scale[2], scale[1])
    o.rotation_euler = rot
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    o.parent = parent
    return o


def _wheel(name, x, root, M):
    y = WR
    ring(f"{name}Tyre", (x, y, 0), WR - 0.05, 0.05, M["tyre"], root, axis="z")
    disc(f"{name}Rim", (x, y, 0), WR - 0.07, 0.07, M["rim"], root, axis="z", verts=32)
    for s in (-1, 1):
        ring(f"{name}RimGlow{s}", (x, y, s * 0.037), WR - 0.085, 0.006, M["orange"], root, axis="z")
        disc(f"{name}Hub{s}", (x, y, s * 0.04), 0.045, 0.02, M["chrome"], root, axis="z")
    # five spokes on the outer face
    for k in range(5):
        a = 2 * math.pi * k / 5
        tube(f"{name}Spoke{k}", [(x + 0.05 * math.cos(a), y + 0.05 * math.sin(a), 0.036),
                                 (x + (WR - 0.09) * math.cos(a), y + (WR - 0.09) * math.sin(a), 0.036)], 0.01, M["chrome"], root)


def build_e_moped(parent=None, name="EMoped"):
    M = {
        "body": mat("MopedBody", "#101114", 0.35, metal=0.5),
        "trim": mat("MopedTrim", "#26282d", 0.3, metal=0.9),
        "tyre": mat("MopedTyre", "#0a0a0b", 0.85),
        "rim": mat("MopedRim", "#18191c", 0.3, metal=0.8),
        "chrome": mat("MopedChrome", "#9aa0a6", 0.15, metal=1.0),
        "seat": mat("MopedSeat", "#0c0c0e", 0.6),
        "orange": mat("MopedOrange", "#ff7a14", emit="#ff7a14", strength=8.0),
        "cyan": mat("MopedCyan", "#22e4ff", emit="#22e4ff", strength=5.0),
        "red": mat("MopedRed", "#ff1a2a", emit="#ff1a2a", strength=8.0),
        "lamp": mat("MopedLamp", "#fff1d6", emit="#fff1d6", strength=12.0),
    }
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    _wheel(f"{name}Front", WX, root, M)
    _wheel(f"{name}Rear", -WX, root, M)

    # ---------- floorboard + orange underglow
    block(f"{name}Floorboard", (0.0, 0.27, 0), (0.75, 0.06, 0.3), M["body"], root, r=0.02)
    block(f"{name}FloorMat", (0.0, 0.302, 0), (0.6, 0.006, 0.24), M["trim"], root)
    block(f"{name}Underglow", (0.0, 0.232, 0), (0.6, 0.006, 0.012), M["orange"], root)

    # ---------- rear body over the back wheel, seat, tail light
    # one sleek tapered rear panel: wide under the seat, narrowing and kicking up at the tail
    rb = rounded_box(f"{name}RearBody", (-0.43, 0.49, 0), (0.88, 0.3, 0.32), 0.1, M["body"], root)
    xs = [v.co.x for v in rb.data.vertices]
    x0, x1 = min(xs), max(xs)
    for v in rb.data.vertices:
        t = (v.co.x - x0) / (x1 - x0)  # 0 = tail, 1 = front
        v.co.y *= 0.62 + 0.38 * t  # narrower tail
        if v.co.z < 0:  # underside sweeps up toward the tail, clearing the wheel
            v.co.z *= 0.55 + 0.45 * t
        v.co.z += 0.05 * (1 - t)
    rounded_box(f"{name}Seat", (-0.33, 0.7, 0), (0.62, 0.09, 0.27), 0.04, M["seat"], root)
    block(f"{name}SeatPiping", (-0.33, 0.655, 0), (0.6, 0.01, 0.28), M["orange"], root)
    block(f"{name}TailLight", (-0.86, 0.52, 0), (0.02, 0.04, 0.2), M["red"], root, r=0.004)
    tube(f"{name}GrabRail", [(-0.62, 0.72, -0.13), (-0.72, 0.74, -0.1), (-0.72, 0.74, 0.1), (-0.62, 0.72, 0.13)], 0.012, M["chrome"], root)

    # ---------- front: leg shield, steering column, fender, handlebar, headlight
    shield = rounded_box(f"{name}LegShield", (0.41, 0.62, 0), (0.08, 0.7, 0.32), 0.035, M["body"], root)
    shield.rotation_euler = (0, math.radians(-14), 0)  # leans back toward the rider
    block(f"{name}ShieldGlow", (0.465, 0.62, 0), (0.006, 0.5, 0.012), M["orange"], root)
    tube(f"{name}Fork", [(0.5, 0.95, 0), (WX, WR, 0)], 0.028, M["trim"], root)
    _blob(f"{name}FrontFender", (WX + 0.02, WR + 0.12, 0), (0.2, 0.06, 0.08), M["body"], root)
    disc(f"{name}HeadsetCap", (0.5, 0.98, 0), 0.06, 0.08, M["body"], root)
    tube(f"{name}Handlebar", [(0.46, 1.06, -0.33), (0.5, 1.03, -0.12), (0.5, 1.03, 0.12), (0.46, 1.06, 0.33)], 0.016, M["trim"], root)
    for s in (-1, 1):
        tube(f"{name}Grip{s}", [(0.462, 1.058, s * 0.25), (0.455, 1.065, s * 0.35)], 0.022, M["seat"], root)
        tube(f"{name}Mirror{s}", [(0.5, 1.04, s * 0.2), (0.49, 1.16, s * 0.24)], 0.006, M["trim"], root)
        mh = block(f"{name}MirrorHead{s}", (0.49, 1.18, s * 0.25), (0.02, 0.05, 0.09), M["body"], root, r=0.01)
    _blob(f"{name}HeadCowl", (0.55, 1.03, 0), (0.1, 0.09, 0.11), M["body"], root)
    disc(f"{name}Headlight", (0.645, 1.03, 0), 0.06, 0.02, M["lamp"], root, axis="x")
    ring(f"{name}HeadlightRing", (0.65, 1.03, 0), 0.068, 0.007, M["cyan"], root, axis="x")
    dash = block(f"{name}Dash", (0.49, 1.11, 0), (0.08, 0.008, 0.14), M["cyan"], root)
    dash.rotation_euler = (0, math.radians(-30), 0)

    # ---------- centre stand, tucked under the floorboard
    for s in (-1, 1):
        tube(f"{name}Stand{s}", [(-0.1, 0.24, s * 0.09), (-0.13, 0.015, s * 0.1)], 0.011, M["trim"], root)
        disc(f"{name}StandFoot{s}", (-0.13, 0.008, s * 0.1), 0.02, 0.016, M["trim"], root)

    # preview-only orange glow under the moped (lights aren't exported)
    ld = bpy.data.lights.new(f"{name}GlowLight", "POINT")
    ld.color = (1.0, 0.48, 0.08)
    ld.energy = 12
    ld.shadow_soft_size = 0.3
    lo = bpy.data.objects.new(f"{name}GlowLight", ld)
    bpy.context.collection.objects.link(lo)
    lo.location = P(0, 0.12, 0.25)
    lo.parent = root

    return root

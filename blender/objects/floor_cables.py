"""
Cyberpunk floor cables: a black floor junction box with status LEDs and
several thick rubber cables snaking out of it across the floor, with glowing
cyan connector collars, short light segments along the runs, and a loose coil
at the end of one cable.

    build_floor_cables(parent=None, name="FloorCables", seed=5) -> root empty

Coordinates are three.js style (Y up, lying on the floor at y = 0, origin at
the junction box). Cables run roughly toward +X / +Z / -X so the set can be
rotated to fit where it's placed.
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
from gaming_desk import ring, tube  # noqa: E402
from loft_room import block, mat  # noqa: E402


def _catmull(points, steps=10):
    """Smooth curve through control points (Catmull-Rom), returned as a dense list."""
    pts = [points[0]] + points + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(steps):
            t = k / steps
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(3)))
    out.append(points[-1])
    return out


def _along(curve, t):
    """Point and direction at fraction t of a dense polyline."""
    i = min(len(curve) - 2, int(t * (len(curve) - 1)))
    a, b = curve[i], curve[i + 1]
    d = [b[j] - a[j] for j in range(3)]
    n = math.sqrt(sum(v * v for v in d)) or 1.0
    return a, [v / n for v in d]


def build_floor_cables(parent=None, name="FloorCables", seed=5):
    RUBBER = mat("CableRubber", "#0b0b0d", 0.75)
    BOX = mat("CableBox", "#17181b", 0.4, metal=0.7)
    STEEL = mat("CableSteel", "#5b5f65", 0.25, metal=0.95)
    CYAN = mat("CableCyan", "#22e4ff", emit="#22e4ff", strength=8.0)
    AMBER = mat("CableAmber", "#ffb020", emit="#ffb020", strength=6.0)
    GREEN = mat("CableGreen", "#2bff7a", emit="#2bff7a", strength=6.0)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    rng = random.Random(seed)

    # ---------- junction box
    block(f"{name}Box", (0, 0.06, 0), (0.34, 0.12, 0.26), BOX, root, r=0.012)
    block(f"{name}BoxLid", (0, 0.122, 0), (0.3, 0.008, 0.22), STEEL, root, r=0.004)
    for k, m in enumerate((GREEN, AMBER, CYAN)):
        block(f"{name}LED{k}", (-0.08 + k * 0.04, 0.09, 0.131), (0.016, 0.016, 0.004), m, root)
    for k, (bx, bz) in enumerate(((-0.14, -0.1), (0.14, -0.1), (-0.14, 0.1), (0.14, 0.1))):
        block(f"{name}Screw{k}", (bx, 0.127, bz), (0.012, 0.006, 0.012), STEEL, root)

    # ---------- cables: control points on the floor, smoothed, with glow details
    runs = [
        (0.04, [(0.17, 0.04, 0.0), (0.6, 0.04, 0.12), (1.1, 0.04, -0.15), (1.7, 0.04, 0.1), (2.3, 0.04, 0.0)]),
        (0.032, [(0.1, 0.032, 0.13), (0.4, 0.032, 0.6), (0.2, 0.032, 1.1), (0.6, 0.032, 1.6), (0.5, 0.032, 2.1)]),
        (0.036, [(-0.17, 0.036, 0.02), (-0.6, 0.036, -0.2), (-1.0, 0.036, 0.25), (-1.5, 0.036, 0.05)]),
        (0.026, [(0.05, 0.026, -0.13), (0.3, 0.026, -0.5), (0.9, 0.026, -0.6), (1.4, 0.026, -0.95)]),
    ]
    for c, (r, ctrl) in enumerate(runs):
        # a little wobble so they look dropped, not drawn with a ruler
        ctrl = [ctrl[0]] + [(x + rng.uniform(-0.05, 0.05), y, z + rng.uniform(-0.05, 0.05)) for x, y, z in ctrl[1:]]
        curve = _catmull(ctrl, steps=12)
        tube(f"{name}Cable{c}", curve, r, RUBBER, root)
        # connector collar where it leaves the box, and a plug at the far end
        for k, t in enumerate((0.02, 0.995)):
            p, d = _along(curve, t)
            ang = math.atan2(d[2], d[0])
            a = (p[0] - d[0] * 0.04, p[1], p[2] - d[2] * 0.04)
            b = (p[0] + d[0] * 0.04, p[1], p[2] + d[2] * 0.04)
            tube(f"{name}Collar{c}_{k}", [a, b], r * 1.45, STEEL, root)
            mid = ((a[0] + b[0]) / 2, p[1], (a[2] + b[2]) / 2)
            rg = ring(f"{name}CollarGlow{c}_{k}", mid, r * 1.5, 0.005, CYAN, root, axis="x")
            rg.rotation_euler = (0, 0, 0)
            rg.rotation_euler[2] = -ang  # face along the cable (Blender Z = vertical)
            rg.rotation_euler[1] = math.pi / 2
        # two short glowing segments along each cable
        for k, t in enumerate((0.35, 0.68)):
            p, d = _along(curve, t)
            a = (p[0] - d[0] * 0.06, p[1], p[2] - d[2] * 0.06)
            b = (p[0] + d[0] * 0.06, p[1], p[2] + d[2] * 0.06)
            tube(f"{name}GlowSeg{c}_{k}", [a, b], r * 1.08, CYAN if (c + k) % 2 == 0 else AMBER, root)

    # ---------- a loose coil at the end of the long cable
    cx, cz = 2.45, 0.0
    coil = []
    for k in range(64):
        a = 2 * math.pi * k / 22
        rr = 0.17 + 0.012 * k / 22
        coil.append((cx + rr * math.cos(a), 0.03 + 0.022 * (k / 64), cz + rr * math.sin(a)))
    tube(f"{name}Coil", coil, 0.024, RUBBER, root)

    # preview-only cyan glow light (lights aren't exported)
    ld = bpy.data.lights.new(f"{name}GlowLight", "POINT")
    ld.color = (0.13, 0.89, 1.0)
    ld.energy = 6
    ld.shadow_soft_size = 0.3
    lo = bpy.data.objects.new(f"{name}GlowLight", ld)
    bpy.context.collection.objects.link(lo)
    lo.location = P(0.6, 0.3, 0.3)
    lo.parent = root
    return root

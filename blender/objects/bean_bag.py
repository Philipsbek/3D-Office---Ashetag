"""
Cyberpunk bean bags: slouchy fabric bags with a raised back, a sitting dent,
soft wrinkles, a carry loop, and a thin glowing neon seam around the middle.

    build_bean_bag(parent=None, name="BeanBag", fabric="#1b1c22", seam="#22e4ff",
                   size=0.95, seed=1) -> root empty
    build_bean_bag_set(parent=None, name="BeanBagSet") -> three bags, different colours

Coordinates are three.js style (Y up). The seat faces +Z (the back is at -Z);
origin at the centre of the base on the floor.
"""

import math
import os
import random
import sys

import bpy
from mathutils import Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P  # noqa: E402
from gaming_desk import tube  # noqa: E402
from loft_room import mat  # noqa: E402


def _shape(x, y, z, size, rng_off):
    """Deform a unit-sphere point (three.js axes) into a slouched bean bag."""
    r = size / 2
    # base: wide and flat on the floor
    yy = y
    if yy < -0.2:
        yy = -0.2 + (yy + 0.2) * 0.25
    # back rises well above the seat, front stays low
    back = max(0.0, -z + 0.15)  # 0 at the front, ~1 at the back
    yy = yy + 0.25
    if yy > 0:
        yy *= 0.8 + 1.05 * back ** 1.3
        yy = 1.15 * math.tanh(yy / 1.15)  # round off the top instead of a peak
    # sitting dent: a deep dip in the top-front middle
    dent = math.exp(-((x / 0.5) ** 2 + ((z - 0.3) / 0.45) ** 2)) * max(0.0, y) * 0.7
    yy -= dent
    # sag outward at the bottom
    spread = 1.0 + 0.18 * max(0.0, -y)
    xx, zz = x * spread, z * spread * 0.95
    # wrinkles
    p = Vector((x * 2.2 + rng_off, y * 2.2, z * 2.2))
    w = 0.045 * noise.noise(p) + 0.02 * noise.noise(p * 2.7)
    return (xx * r * (1 + w), yy * r * (1 + w * 0.6), zz * r * (1 + w))


def build_bean_bag(parent=None, name="BeanBag", fabric="#1b1c22", seam="#22e4ff", size=0.95, seed=1):
    FABRIC = mat(f"BeanFabric_{fabric}", fabric, 0.85)
    SEAM = mat(f"BeanSeam_{seam}", seam, emit=seam, strength=7.0)
    LOOP = mat("BeanLoop", "#0c0c0e", 0.7)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    rng = random.Random(seed)
    off = rng.uniform(0, 50)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=48, ring_count=24)
    bag = bpy.context.active_object
    bag.name = f"{name}Bag"
    lift = 0.0
    for v in bag.data.vertices:
        x, y, z = v.co.x, v.co.z, -v.co.y  # Blender -> three.js
        sx, sy, sz = _shape(x, y, z, size, off)
        v.co = P(sx, sy, sz)
    lift = -min(v.co.z for v in bag.data.vertices)  # sit exactly on the floor
    for v in bag.data.vertices:
        v.co.z += lift
    sub = bag.modifiers.new("Smooth", "SUBSURF")
    sub.levels = 1
    bpy.ops.object.shade_smooth()
    bag.data.materials.append(FABRIC)
    bag.parent = root

    # neon seam: follow the bag's surface around its middle, just proud of it
    seam_y = None
    pts = []
    for k in range(73):
        a = 2 * math.pi * k / 72
        x, z = math.cos(a), math.sin(a)
        sx, sy, sz = _shape(x * 0.999, -0.05, z * 0.999, size, off)
        n = math.hypot(sx, sz) or 1.0
        pts.append((sx + sx / n * 0.012, sy + lift, sz + sz / n * 0.012))
    tube(f"{name}Seam", pts, 0.006, SEAM, root)

    # carry loop at the top of the back
    tx, ty, tz = _shape(0.0, 0.55, -0.83, size, off)
    tube(f"{name}Loop", [(tx - 0.05, ty + lift - 0.01, tz), (tx - 0.03, ty + lift + 0.05, tz), (tx + 0.03, ty + lift + 0.05, tz), (tx + 0.05, ty + lift - 0.01, tz)], 0.012, LOOP, root)

    # preview-only light from the seam (lights aren't exported)
    ld = bpy.data.lights.new(f"{name}GlowLight", "POINT")
    ld.color = tuple(int(seam.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    ld.energy = 5
    ld.shadow_soft_size = 0.3
    lo = bpy.data.objects.new(f"{name}GlowLight", ld)
    bpy.context.collection.objects.link(lo)
    lo.location = P(0, 0.15, size * 0.62)
    lo.parent = root
    return root


def build_bean_bag_set(parent=None, name="BeanBagSet"):
    """Three bags in different colours, casually angled toward each other."""
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    bags = [
        ("Charcoal", "#1b1c22", "#22e4ff", 1.0, (-1.05, 0.0), 20, 1),
        ("Plum", "#2b1630", "#ff2bd6", 0.9, (0.0, -0.25), 0, 4),
        ("Teal", "#10282a", "#2bff7a", 0.85, (1.0, 0.05), -25, 7),
    ]
    for label, fab, sm, sz, (x, z), yaw, sd in bags:
        b = build_bean_bag(root, f"{name}{label}", fabric=fab, seam=sm, size=sz, seed=sd)
        b.location = P(x, 0, z)
        b.rotation_euler = (0, 0, math.radians(yaw))
    return root

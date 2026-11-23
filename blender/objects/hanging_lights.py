"""
Cyberpunk hanging lights for under the loft's mezzanine. Three kinds, each
hanging from a ceiling plate at y = 0 down to `drop` metres below it:

    build_neon_bar_pendant(parent, name, drop=0.9, length=1.4, color="#22e4ff")
        a long neon tube in a black channel, on two thin cables
    build_bulb_cluster(parent, name, drops=(0.6, 0.85, 0.7, 1.0, 0.75))
        warm filament bulbs in black sockets, hanging at staggered heights
    build_ring_pendant(parent, name, drop=1.0, radius=0.35, color="#ff2bd6")
        a large neon ring on three cables
    build_hanging_lights_preview(parent, name) -> all three under a ceiling slab

Coordinates are three.js style (Y up). The origin of each light is its ceiling
mount point; lights hang down toward -Y.
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
from gaming_desk import disc, ring, tube  # noqa: E402
from loft_room import block, mat  # noqa: E402


def _root(name, parent):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    return root


def _preview_light(name, pos, color, watts, parent):
    """Light for Blender previews only (lights aren't exported)."""
    ld = bpy.data.lights.new(name, "POINT")
    ld.color = _hex(color)
    ld.energy = watts
    ld.shadow_soft_size = 0.2
    lo = bpy.data.objects.new(name, ld)
    bpy.context.collection.objects.link(lo)
    lo.location = P(*pos)
    lo.parent = parent


def build_neon_bar_pendant(parent=None, name="NeonBar", drop=0.9, length=1.4, color="#22e4ff"):
    BLACK = mat("PendantBlack", "#0d0e10", 0.4, metal=0.7)
    CABLE = mat("PendantCable", "#111114", 0.6)
    NEON = mat(f"PendantNeon_{color}", color, emit=color, strength=10.0)
    root = _root(name, parent)
    y = -drop
    block(f"{name}Channel", (0, y + 0.02, 0), (length, 0.04, 0.06), BLACK, root, r=0.006)
    block(f"{name}Tube", (0, y - 0.006, 0), (length - 0.06, 0.016, 0.03), NEON, root, r=0.004)
    for s in (-1, 1):
        x = s * (length / 2 - 0.12)
        tube(f"{name}Cable{s}", [(x, 0, 0), (x, y + 0.04, 0)], 0.003, CABLE, root)
        disc(f"{name}Canopy{s}", (x, -0.01, 0), 0.03, 0.02, BLACK, root)
    _preview_light(f"{name}Glow", (0, y - 0.15, 0), color, 30, root)
    return root


def build_bulb_cluster(parent=None, name="BulbCluster", drops=(0.6, 0.85, 0.7, 1.0, 0.75), seed=3):
    BLACK = mat("PendantBlack", "#0d0e10", 0.4, metal=0.7)
    CABLE = mat("PendantCable", "#111114", 0.6)
    GLASS = mat("BulbGlass", "#ff9a2a", 0.05, emit="#ff8a1a", strength=2.6)  # warm amber glass
    FIL = mat("BulbFilament", "#ffd08a", emit="#ffd08a", strength=14.0)
    root = _root(name, parent)
    rng = random.Random(seed)
    block(f"{name}Plate", (0, -0.015, 0), (0.5, 0.03, 0.5), BLACK, root, r=0.008)
    n = len(drops)
    for k, d in enumerate(drops):
        a = 2 * math.pi * k / n + rng.uniform(-0.3, 0.3)
        r = 0.15 if k else 0.0
        x, z = r * math.cos(a), r * math.sin(a)
        tube(f"{name}Cable{k}", [(x, -0.03, z), (x, -d + 0.07, z)], 0.003, CABLE, root)
        disc(f"{name}Socket{k}", (x, -d + 0.04, z), 0.016, 0.06, BLACK, root)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, segments=20, ring_count=12)
        b = bpy.context.active_object
        b.name = f"{name}Bulb{k}"
        b.scale = (1, 1, 1.35)  # Edison-style elongated bulb
        b.location = P(x, -d - 0.035, z)
        bpy.ops.object.shade_smooth()
        b.data.materials.append(GLASS)
        b.parent = root
        tube(f"{name}Filament{k}", [(x - 0.012, -d - 0.005, z), (x, -d - 0.045, z), (x + 0.012, -d - 0.005, z)], 0.0025, FIL, root)
    _preview_light(f"{name}Glow", (0, -0.85, 0), "#ffb35a", 40, root)
    return root


def build_ring_pendant(parent=None, name="RingPendant", drop=1.0, radius=0.35, color="#ff2bd6"):
    BLACK = mat("PendantBlack", "#0d0e10", 0.4, metal=0.7)
    CABLE = mat("PendantCable", "#111114", 0.6)
    NEON = mat(f"PendantNeon_{color}", color, emit=color, strength=10.0)
    root = _root(name, parent)
    y = -drop
    ring(f"{name}Housing", (0, y + 0.012, 0), radius, 0.022, BLACK, root)
    ring(f"{name}Neon", (0, y - 0.008, 0), radius, 0.012, NEON, root)
    disc(f"{name}Canopy", (0, -0.01, 0), 0.05, 0.02, BLACK, root)
    for k in range(3):
        a = 2 * math.pi * k / 3
        tube(f"{name}Cable{k}", [(0, -0.02, 0), (radius * math.cos(a), y + 0.03, radius * math.sin(a))], 0.003, CABLE, root)
    _preview_light(f"{name}Glow", (0, y - 0.2, 0), color, 30, root)
    return root


def build_hanging_lights_preview(parent=None, name="HangingLightsPreview"):
    """Preview only: the three kinds hanging under a dark ceiling slab at 2.4 m."""
    root = _root(name, parent)
    CEIL = mat("PreviewCeiling", "#141416", 0.8)
    H = 2.4
    block(f"{name}Ceiling", (0, H + 0.1, 0), (4.6, 0.2, 1.6), CEIL, root)
    a = build_neon_bar_pendant(root, f"{name}Bar", drop=0.9)
    a.location = P(-1.45, H, 0)
    b = build_bulb_cluster(root, f"{name}Bulbs")
    b.location = P(0.15, H, 0)
    c = build_ring_pendant(root, f"{name}Ring", drop=1.0)
    c.location = P(1.55, H, 0)
    return root

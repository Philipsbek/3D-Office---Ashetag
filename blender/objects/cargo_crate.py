"""
Cyberpunk cargo crates for the loft's lower floor: black hard-shell cases with
chamfered edges, a raised lid band, red light strips down the front corners,
steel latches and side handles, a small status panel, and rubber feet.

    build_cargo_crate(parent=None, name="Crate", size=(1.0, 0.6, 0.65)) -> root
    build_crate_set(parent=None, name="CrateSet") -> four crates (one stacked)

Coordinates are three.js style (Y up, the crate's front faces +Z, origin at
the centre of its base on the floor). size = (width x, height y, depth z).
"""

import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P  # noqa: E402
from gaming_desk import disc, tube  # noqa: E402
from loft_room import block, mat  # noqa: E402


def _chamfer_box(name, c, size, chamfer, m, parent):
    """Box with flat 45° chamfers on every edge (a hard-case look)."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.location = P(*c)
    o.scale = (size[0], size[2], size[1])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bev = o.modifiers.new("Chamfer", "BEVEL")
    bev.width = chamfer
    bev.segments = 1
    bev.limit_method = "NONE"
    o.data.materials.append(m)
    o.parent = parent
    return o


def build_cargo_crate(parent=None, name="Crate", size=(1.0, 0.6, 0.65)):
    SHELL = mat("CrateShell", "#121316", 0.45, metal=0.35)
    BAND = mat("CrateBand", "#1d1f23", 0.35, metal=0.7)
    STEEL = mat("CrateSteel", "#5b5f65", 0.25, metal=0.95)
    RUBBER = mat("CrateRubber", "#070708", 0.9)
    RED = mat("CrateRed", "#ff1a2a", emit="#ff1a2a", strength=9.0)
    PANEL = mat("CratePanel", "#08090a", 0.2, emit="#ff1a2a", strength=0.35)

    w, h, d = size
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    foot = 0.03
    _chamfer_box(f"{name}Shell", (0, foot + h / 2, 0), (w, h, d), 0.07, SHELL, root)
    # raised band where the lid meets the body
    _chamfer_box(f"{name}LidBand", (0, foot + h * 0.68, 0), (w + 0.02, 0.05, d + 0.02), 0.03, BAND, root)
    # red light strips down both front corners (on the chamfer faces)
    for s in (-1, 1):
        strip = block(f"{name}RedStrip{s}", (s * (w / 2 - 0.031), foot + h * 0.4, d / 2 - 0.031), (0.014, h * 0.5, 0.014), RED, root)
        strip.rotation_euler = (0, 0, 0)
    # latches on the front
    for s in (-1, 1):
        x = s * w * 0.28
        block(f"{name}Latch{s}", (x, foot + h * 0.68, d / 2 + 0.012), (0.09, 0.07, 0.02), STEEL, root, r=0.006)
        block(f"{name}LatchPin{s}", (x, foot + h * 0.63, d / 2 + 0.02), (0.05, 0.015, 0.012), BAND, root)
    # status panel between the latches
    block(f"{name}Panel", (0, foot + h * 0.4, d / 2 + 0.003), (w * 0.22, h * 0.16, 0.008), PANEL, root, r=0.004)
    block(f"{name}PanelLED", (w * 0.07, foot + h * 0.43, d / 2 + 0.008), (0.018, 0.018, 0.004), RED, root)
    # side handles
    for s in (-1, 1):
        tube(f"{name}Handle{s}", [(s * (w / 2 + 0.005), foot + h * 0.5, -0.12), (s * (w / 2 + 0.04), foot + h * 0.52, -0.1),
                                  (s * (w / 2 + 0.04), foot + h * 0.52, 0.1), (s * (w / 2 + 0.005), foot + h * 0.5, 0.12)], 0.012, STEEL, root)
    # rubber feet
    for k, (sx, sz) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        disc(f"{name}Foot{k}", (sx * (w / 2 - 0.1), foot / 2, sz * (d / 2 - 0.1)), 0.04, foot, RUBBER, root)
    return root


def build_crate_set(parent=None, name="CrateSet"):
    """Four crates as they'll be scattered on the lower floor: a big one with a
    small one stacked on it, a medium one, and one turned at an angle."""
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    big = build_cargo_crate(root, f"{name}Big", (1.15, 0.62, 0.7))
    big.location = P(-0.9, 0, 0)
    top = build_cargo_crate(root, f"{name}Small", (0.7, 0.4, 0.5))
    top.location = P(-0.95, 0.65, 0.02)
    top.rotation_euler = (0, 0, math.radians(8))
    med = build_cargo_crate(root, f"{name}Medium", (0.9, 0.5, 0.6))
    med.location = P(0.45, 0, 0.1)
    turned = build_cargo_crate(root, f"{name}Turned", (0.95, 0.55, 0.6))
    turned.location = P(1.55, 0, -0.35)
    turned.rotation_euler = (0, 0, math.radians(-32))
    # preview-only red glow lights at the crate fronts (lights aren't exported)
    for k, (lx, lz) in enumerate(((-0.9, 0.55), (0.45, 0.6), (1.75, 0.15))):
        ld = bpy.data.lights.new(f"{name}GlowLight{k}", "POINT")
        ld.color = (1.0, 0.1, 0.16)
        ld.energy = 10
        ld.shadow_soft_size = 0.2
        lo = bpy.data.objects.new(f"{name}GlowLight{k}", ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(lx, 0.25, lz)
        lo.parent = root
    return root

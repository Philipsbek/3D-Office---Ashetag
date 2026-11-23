"""
Cyberpunk telescope for the loft bedroom corner: a matte-black refractor on a
black steel tripod, with cyan light rings on the tube, a small finder scope,
an accessory tray, and a red status LED on the mount.

    build_telescope(parent=None, name="Telescope", tilt_deg=32) -> root empty

Coordinates are three.js style (Y up). The tube points toward +Z and tilts up
by `tilt_deg`; origin is the centre of the tripod on the floor. The tube sits
under an empty named "<name>Pivot" so the site could slowly sweep it.
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

HEAD_Y = 1.28  # height of the tube's pivot


def build_telescope(parent=None, name="Telescope", tilt_deg=32):
    BODY = mat("ScopeBody", "#141518", 0.55, metal=0.4)
    METAL = mat("ScopeMetal", "#2c2e33", 0.35, metal=0.9)
    CHROME = mat("ScopeChrome", "#8a8e94", 0.2, metal=1.0)
    GLASS = mat("ScopeGlass", "#0b1a2a", 0.05, metal=0.2, emit="#1a5a8a", strength=0.4)
    CYAN = mat("ScopeCyan", "#22e4ff", emit="#22e4ff", strength=8.0)
    RED = mat("ScopeLED", "#ff2a2a", emit="#ff2a2a", strength=8.0)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---------- tripod: three splayed legs, centre column, spreader + tray
    hub_y = HEAD_Y - 0.2
    disc(f"{name}Hub", (0, hub_y, 0), 0.07, 0.06, METAL, root)
    ring(f"{name}HubGlow", (0, hub_y - 0.035, 0), 0.07, 0.006, CYAN, root)
    tray_y = 0.5
    for k in range(3):
        a = math.radians(90 + 120 * k)
        fx, fz = 0.56 * math.cos(a), 0.56 * math.sin(a)
        hx, hz = 0.06 * math.cos(a), 0.06 * math.sin(a)
        tube(f"{name}Leg{k}", [(hx, hub_y, hz), (fx, 0.03, fz)], 0.019, BODY, root)
        # telescoping lower section in metal
        tube(f"{name}LegLower{k}", [(hx + (fx - hx) * 0.55, hub_y + (0.03 - hub_y) * 0.55, hz + (fz - hz) * 0.55), (fx, 0.03, fz)], 0.014, METAL, root)
        disc(f"{name}Foot{k}", (fx, 0.012, fz), 0.03, 0.024, METAL, root)
        # spreader arm from the column to the leg
        t = (hub_y - tray_y) / (hub_y - 0.03)
        lx, lz = hx + (fx - hx) * t, hz + (fz - hz) * t
        tube(f"{name}Spreader{k}", [(0, tray_y, 0), (lx, tray_y, lz)], 0.008, METAL, root)
    tube(f"{name}Column", [(0, tray_y, 0), (0, hub_y, 0)], 0.016, METAL, root)
    disc(f"{name}Tray", (0, tray_y + 0.01, 0), 0.14, 0.012, BODY, root, verts=3)  # triangular tray
    for k, (ex, ez) in enumerate(((0.05, 0.0), (-0.03, 0.04))):  # spare eyepieces in the tray
        disc(f"{name}SpareEyepiece{k}", (ex, tray_y + 0.04, ez), 0.016, 0.05, CHROME, root)

    # ---------- mount head with a red status LED
    disc(f"{name}MountBase", (0, hub_y + 0.06, 0), 0.05, 0.06, METAL, root)
    block(f"{name}MountHead", (0, HEAD_Y - 0.07, 0), (0.09, 0.12, 0.1), BODY, root, r=0.01)
    block(f"{name}LED", (0.046, HEAD_Y - 0.05, 0.02), (0.004, 0.012, 0.012), RED, root)
    disc(f"{name}SlowMotionKnob", (-0.07, HEAD_Y - 0.06, 0), 0.02, 0.04, CHROME, root, axis="x")

    # ---------- optical tube on a pivot, tilted up toward +Z
    pivot = bpy.data.objects.new(f"{name}Pivot", None)
    bpy.context.collection.objects.link(pivot)
    pivot.location = P(0, HEAD_Y, 0)
    pivot.rotation_euler = (-math.radians(tilt_deg), 0, 0)  # -X rotation lifts +Z upward
    pivot.parent = root

    block(f"{name}Dovetail", (0, -0.075, 0), (0.035, 0.02, 0.34), METAL, pivot)
    for k, z in enumerate((-0.12, 0.12)):  # tube rings
        ring(f"{name}TubeRing{k}", (0, 0, z), 0.07, 0.012, METAL, pivot, axis="z")
        block(f"{name}RingFoot{k}", (0, -0.062, z), (0.025, 0.03, 0.02), METAL, pivot)
    disc(f"{name}Tube", (0, 0, 0.02), 0.065, 0.85, BODY, pivot, axis="z")
    disc(f"{name}DewShield", (0, 0, 0.5), 0.078, 0.2, BODY, pivot, axis="z")
    disc(f"{name}Objective", (0, 0, 0.555), 0.071, 0.006, GLASS, pivot, axis="z")
    ring(f"{name}FrontGlow", (0, 0, 0.395), 0.079, 0.006, CYAN, pivot, axis="z")
    ring(f"{name}MidGlow", (0, 0, 0.2), 0.066, 0.005, CYAN, pivot, axis="z")
    ring(f"{name}RearGlow", (0, 0, -0.33), 0.066, 0.005, CYAN, pivot, axis="z")
    # back end: cap, focuser and an eyepiece pointing up
    disc(f"{name}RearCap", (0, 0, -0.42), 0.06, 0.05, METAL, pivot, axis="z")
    disc(f"{name}Focuser", (0, 0, -0.48), 0.035, 0.09, METAL, pivot, axis="z")
    disc(f"{name}FocusKnob", (0, -0.02, -0.47), 0.016, 0.1, CHROME, pivot, axis="x")
    disc(f"{name}Diagonal", (0, 0.03, -0.55), 0.028, 0.07, METAL, pivot)
    disc(f"{name}Eyepiece", (0, 0.09, -0.55), 0.02, 0.07, BODY, pivot)
    ring(f"{name}EyepieceGlow", (0, 0.125, -0.55), 0.02, 0.004, CYAN, pivot)
    # finder scope on a little bracket
    block(f"{name}FinderBracket", (0.045, 0.075, -0.08), (0.02, 0.04, 0.05), METAL, pivot)
    disc(f"{name}Finder", (0.06, 0.1, -0.06), 0.018, 0.24, BODY, pivot, axis="z")
    ring(f"{name}FinderGlow", (0.06, 0.1, 0.06), 0.019, 0.003, CYAN, pivot, axis="z")

    return root

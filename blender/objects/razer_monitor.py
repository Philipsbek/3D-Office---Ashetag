"""
Razer-style 27" gaming monitor (inspired by the Raptor): thin bezels, slim
CNC-aluminium-look L stand on a flat base, Razer-green cables routed up the
back of the stand, and a Chroma underglow strip on the base. No logos.

    build_razer_monitor(parent=None, name="RazerMonitor") -> root empty

Coordinates are three.js style (Y up, screen faces +Z, origin at the centre
of the base, on the desk surface). The screen mesh is named "MonitorScreen"
so the website can put live content on it.
"""

import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P, _hex, rounded_box  # noqa: E402
from gaming_desk import tube  # noqa: E402

RAZER_GREEN = "#44d62c"

_M = {}


def mat(name, color, rough=0.5, metal=0.0, emit=None, strength=1.0, image=None):
    key = "Razer_" + name
    if key in _M:
        return _M[key]
    m = bpy.data.materials.new(key)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*_hex(color), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*_hex(emit), 1)
        b.inputs["Emission Strength"].default_value = strength
    if image is not None:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = image
        nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
        nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = strength
    m.diffuse_color = (*_hex(color), 1)
    _M[key] = m
    return m


def wallpaper(w=640, h=360):
    """Placeholder screen image: dark scene with a green horizon grid (gets replaced live on the site)."""
    img = bpy.data.images.get("MonitorWallpaper")
    if img:  # one shared image for every monitor
        return img
    img = bpy.data.images.new("MonitorWallpaper", w, h)
    px = [0.0] * (w * h * 4)
    g = (0x44 / 255, 0xD6 / 255, 0x2C / 255)
    horizon = 0.42
    for y in range(h):
        v = y / (h - 1)  # 0 = bottom
        for x in range(w):
            u = x / (w - 1)
            r, gg, b = 0.01 + 0.03 * v, 0.015 + 0.04 * v, 0.03 + 0.06 * v  # night sky gradient
            # glowing sun on the horizon
            d = math.hypot((u - 0.5) * 1.8, (v - horizon - 0.08) * 1.0)
            if d < 0.13 and v > horizon:
                r, gg, b = g[0] * 0.9, g[1] * 0.9, g[2] * 0.9
            elif d < 0.25 and v > horizon:
                k = (0.25 - d) / 0.12 * 0.35
                r, gg, b = r + g[0] * k, gg + g[1] * k, b + g[2] * k
            # perspective grid floor
            if v < horizon:
                depth = (horizon - v) / horizon
                zline = abs(math.sin(1 / max(depth, 0.02) * 2.2)) < 0.12
                xline = abs(math.sin((u - 0.5) / max(depth, 0.05) * 9)) < 0.08
                if zline or xline:
                    k = 0.25 + 0.6 * depth
                    r, gg, b = g[0] * k, g[1] * k, g[2] * k
                else:
                    r, gg, b = 0.005, 0.01, 0.01
            i = (y * w + x) * 4
            px[i:i + 4] = (r, gg, b, 1.0)
    img.pixels = px
    img.pack()
    return img


def build_razer_monitor(parent=None, name="RazerMonitor"):
    ALU = mat("Aluminium", "#1c1c1f", 0.35, metal=0.8)
    BLACK = mat("Plastic", "#0b0b0c", 0.5)
    BEZEL = mat("Bezel", "#050505", 0.3)
    GREEN = mat("GreenCable", RAZER_GREEN, 0.6, emit=RAZER_GREEN, strength=0.6)
    GLOW = mat("Underglow", RAZER_GREEN, 0.4, emit=RAZER_GREEN, strength=5)
    LED = mat("PowerLED", RAZER_GREEN, 0.3, emit=RAZER_GREEN, strength=8)
    SCREEN = _M.get("Razer_Screen") or mat("Screen", "#000000", 0.2, image=wallpaper(), strength=1.6)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---------- flat base with Chroma underglow
    rounded_box("MonitorBase", (0, 0.008, -0.03), (0.32, 0.012, 0.22), 0.006, ALU, root)
    rounded_box("MonitorUnderglow", (0, 0.0015, -0.03), (0.3, 0.003, 0.2), 0.002, GLOW, root)

    # ---------- L stand: upright arm at the back of the base, hinge into the panel
    rounded_box("StandArm", (0, 0.2, -0.125), (0.065, 0.38, 0.022), 0.008, ALU, root)
    rounded_box("StandFoot", (0, 0.02, -0.1), (0.065, 0.02, 0.07), 0.006, ALU, root)
    rounded_box("StandHinge", (0, 0.36, -0.105), (0.09, 0.05, 0.04), 0.01, BLACK, root)

    # signature green cables routed up the back of the arm
    for i, x in enumerate((-0.014, 0.0, 0.014)):
        tube(f"GreenCable{i}", [
            (x, 0.012, -0.05), (x, 0.012, -0.12), (x, 0.03, -0.142),
            (x, 0.33, -0.142), (x, 0.36, -0.125),
        ], 0.0045, GREEN, root)

    # ---------- panel
    pw, ph, pd = 0.62, 0.365, 0.022
    py, pz = 0.43, -0.075
    rounded_box("MonitorPanel", (0, py, pz), (pw, ph, pd), 0.006, BEZEL, root)
    rounded_box("MonitorBack", (0, py - 0.01, pz - 0.022), (0.42, 0.25, 0.03), 0.02, BLACK, root)
    rounded_box("MonitorChin", (0, py - ph / 2 + 0.006, pz + 0.002), (pw, 0.014, pd + 0.004), 0.004, BEZEL, root)
    rounded_box("PowerLED", (0.26, py - ph / 2 + 0.006, pz + pd / 2 + 0.003), (0.006, 0.003, 0.002), 0.001, LED, root)

    # the screen: a plane just in front of the panel (UVs map the whole image)
    bpy.ops.mesh.primitive_plane_add(size=1)
    scr = bpy.context.active_object
    scr.name = "MonitorScreen"
    scr.location = P(0, py + 0.004, pz + pd / 2 + 0.0015)
    scr.scale = (pw - 0.016, ph - 0.03, 1)
    scr.rotation_euler = (math.pi / 2, 0, 0)
    scr.data.materials.append(SCREEN)
    scr.parent = root

    return root

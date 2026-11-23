"""
Cyberpunk sim-racing rig for the office's front-left corner (replaces the glass
room): black aluminium-profile cockpit on a mat with a cyan neon border,
magenta underglow along the frame, a bucket seat with neon piping and harness
slots, a wheel on a deck with LED rev lights, three pedals, a sequential
shifter, and three screens (centre + two angled wings) on a stand showing one
wide original night-race picture (textures/race_screens.png).

    build_sim_rig(parent=None, name="SimRig") -> root empty

Coordinates are three.js style (Y up). The driver faces -Z (the screens are at
-Z, facing +Z); origin at the centre of the mat on the floor.
"""

import math
import os
import sys

import bpy
import bmesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P  # noqa: E402
from gaming_desk import disc, ring, tube  # noqa: E402
from loft_room import block, mat, slab  # noqa: E402

TEX = os.path.join(HERE, "textures", "race_screens.png")


def _screen_mat():
    m = bpy.data.materials.get("Loft_SimRigScreen")
    if m:
        return m
    m = bpy.data.materials.new("Loft_SimRigScreen")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(TEX, check_existing=True)
    tex.image.pack()
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 1.6
    b.inputs["Roughness"].default_value = 0.3
    return m


def _pivot(name, pos, parent, rot=(0, 0, 0)):
    """Empty at a three.js position with a Blender-axis rotation (radians)."""
    e = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(e)
    e.location = P(*pos)
    e.rotation_euler = rot
    e.parent = parent
    return e


def _image_quad(name, x0, x1, y0, y1, z, u0, u1, m, parent):
    """Flat quad facing +Z showing the u0..u1 slice of the screen image."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")  # same name as the other parts, so it survives the join
    vs = [bm.verts.new(P(x, y, z)) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    f = bm.faces.new(vs)
    for loop, (u, v) in zip(f.loops, ((u0, 0), (u1, 0), (u1, 1), (u0, 1))):
        loop[uv].uv = (u, v)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    me.materials.append(m)
    o.parent = parent
    return o


def build_sim_rig(parent=None, name="SimRig"):
    FRAME = mat("SimFrame", "#16171c", 0.35, metal=0.8)
    MAT = mat("SimMat", "#0e0e13", 0.9)
    SEAT = mat("SimSeat", "#141419", 0.55)
    SEAT_SIDE = mat("SimSeatSide", "#23232b", 0.5)
    WHEEL = mat("SimWheel", "#0c0c10", 0.5)
    ALU = mat("SimAlu", "#8a9098", 0.25, metal=1.0)
    BEZEL = mat("SimBezel", "#08080b", 0.3)
    CYAN = mat("SimNeonCyan", "#22e4ff", emit="#22e4ff", strength=8.0)
    PINK = mat("SimNeonPink", "#ff4fd8", emit="#ff4fd8", strength=8.0)
    REV = mat("SimRevLed", "#ffd21a", emit="#ffb020", strength=6.0)
    SCREEN = _screen_mat()

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---------- mat with a cyan neon border
    x0, x1, z0, z1 = -0.85, 0.85, -1.45, 1.05
    slab(f"{name}Mat", x0, x1, 0.0, 0.015, z0, z1, MAT, root)
    e = 0.025
    for k, (a, b, c, d) in enumerate(((x0, x1, z0, z0 + e), (x0, x1, z1 - e, z1), (x0, x0 + e, z0, z1), (x1 - e, x1, z0, z1))):
        slab(f"{name}MatNeon{k}", a, b, 0.015, 0.022, c, d, CYAN, root)

    # ---------- aluminium-profile chassis, magenta underglow on the outer faces
    p = 0.08  # profile size
    for s in (-1, 1):
        x = s * 0.3
        slab(f"{name}Rail{s}", x - p / 2, x + p / 2, 0.02, 0.02 + p, -0.8, 0.8, FRAME, root, r=0.006)
        slab(f"{name}Glow{s}", x + s * p / 2 - 0.006, x + s * p / 2 + 0.006, 0.03, 0.045, -0.78, 0.78, PINK, root)
    for k, z in enumerate((-0.8 + p / 2, -0.25, 0.3, 0.8 - p / 2)):
        slab(f"{name}Cross{k}", -0.3, 0.3, 0.02, 0.02 + p, z - p / 2, z + p / 2, FRAME, root, r=0.006)

    # ---------- bucket seat on sliders; the back reclines ~18 degrees
    slab(f"{name}Slider", -0.2, 0.2, 0.1, 0.16, 0.2, 0.7, FRAME, root)
    block(f"{name}Cushion", (0, 0.24, 0.44), (0.46, 0.12, 0.5), SEAT, root, r=0.04)
    for s in (-1, 1):
        block(f"{name}Bolster{s}", (s * 0.25, 0.3, 0.44), (0.08, 0.18, 0.5), SEAT_SIDE, root, r=0.035)
        slab(f"{name}CushPipe{s}", s * 0.21 - 0.006, s * 0.21 + 0.006, 0.3, 0.305, 0.2, 0.68, PINK, root)
    back = _pivot(f"{name}BackPivot", (0, 0.26, 0.7), root, rot=(math.radians(18), 0, 0))
    block(f"{name}Back", (0, 0.42, 0), (0.48, 0.84, 0.1), SEAT, back, r=0.04)
    for s in (-1, 1):
        block(f"{name}Wing{s}", (s * 0.27, 0.32, -0.04), (0.08, 0.56, 0.16), SEAT_SIDE, back, r=0.035)
        slab(f"{name}BackPipe{s}", s * 0.2 - 0.007, s * 0.2 + 0.007, 0.06, 0.8, -0.056, -0.05, PINK, back)
        slab(f"{name}Harness{s}", s * 0.1 - 0.035, s * 0.1 + 0.035, 0.66, 0.74, -0.06, 0.06, BEZEL, back)
    block(f"{name}Head", (0, 0.88, 0), (0.36, 0.12, 0.1), SEAT, back, r=0.04)

    # ---------- wheel deck, wheel and rev lights
    for s in (-1, 1):
        slab(f"{name}DeckPost{s}", s * 0.3 - 0.03, s * 0.3 + 0.03, 0.1, 0.62, -0.42, -0.36, FRAME, root)
    slab(f"{name}DeckBar", -0.3, 0.3, 0.58, 0.64, -0.42, -0.36, FRAME, root)
    deck = _pivot(f"{name}DeckPivot", (0, 0.66, -0.36), root, rot=(math.radians(15), 0, 0))
    block(f"{name}Base", (0, 0.06, 0.02), (0.16, 0.12, 0.24), WHEEL, deck, r=0.02)
    block(f"{name}BaseLed", (0, 0.121, 0.0), (0.1, 0.004, 0.02), CYAN, deck)
    wheel = _pivot(f"{name}WheelPivot", (0, 0.1, 0.16), deck)
    ring(f"{name}Rim", (0, 0, 0), 0.15, 0.018, WHEEL, wheel, axis="z")
    disc(f"{name}Hub", (0, 0, -0.01), 0.05, 0.04, WHEEL, wheel, axis="z")
    block(f"{name}Spoke", (0, 0, 0.0), (0.28, 0.035, 0.02), WHEEL, wheel)
    block(f"{name}SpokeLow", (0, -0.07, 0.0), (0.035, 0.14, 0.02), WHEEL, wheel)
    for k in range(7):
        block(f"{name}Rev{k}", (-0.06 + k * 0.02, 0.05, 0.013), (0.012, 0.012, 0.004), CYAN if k < 3 else REV if k < 5 else PINK, wheel)
    for s in (-1, 1):  # paddles
        block(f"{name}Paddle{s}", (s * 0.1, 0.03, -0.03), (0.06, 0.08, 0.008), ALU, wheel)

    # ---------- pedals on an angled plate
    pedals = _pivot(f"{name}PedalPivot", (0, 0.1, -0.68), root, rot=(math.radians(35), 0, 0))
    block(f"{name}PedalPlate", (0, 0.0, 0), (0.42, 0.02, 0.28), FRAME, pedals)
    for k, x in enumerate((-0.12, 0.0, 0.12)):
        block(f"{name}Pedal{k}", (x, 0.04, -0.02), (0.06 if k else 0.08, 0.012, 0.13), ALU, pedals)
        block(f"{name}PedalArm{k}", (x, 0.02, 0.06), (0.015, 0.03, 0.06), ALU, pedals)

    # ---------- sequential shifter on the right
    slab(f"{name}ShiftMount", 0.3, 0.42, 0.1, 0.16, -0.18, -0.06, FRAME, root)
    tube(f"{name}ShiftPost", [(0.38, 0.16, -0.12), (0.38, 0.42, -0.12), (0.37, 0.5, -0.14)], 0.012, ALU, root)
    disc(f"{name}ShiftKnob", (0.37, 0.53, -0.14), 0.028, 0.06, WHEEL, root, verts=16)
    block(f"{name}ShiftLed", (0.37, 0.565, -0.14), (0.03, 0.004, 0.03), PINK, root)

    # ---------- triple screens on a stand: centre facing the driver, wings angled in 50 degrees
    sw, sh, sy, sz = 1.04, 0.6, 1.02, -1.2  # one 16:9 panel; centre height; plane
    for s in (-1, 1):
        slab(f"{name}StandPost{s}", s * 0.35 - 0.035, s * 0.35 + 0.035, 0.015, sy, sz - 0.16, sz - 0.09, FRAME, root)
        slab(f"{name}StandFoot{s}", s * 0.35 - 0.05, s * 0.35 + 0.05, 0.015, 0.05, sz - 0.4, sz + 0.2, FRAME, root)
    slab(f"{name}StandBar", -0.62, 0.62, sy - 0.04, sy + 0.04, sz - 0.16, sz - 0.09, FRAME, root)

    def panel(tag, piv, xa, xb, u0, u1):
        slab(f"{name}{tag}Bezel", xa - 0.015, xb + 0.015, -sh / 2 - 0.015, sh / 2 + 0.015, -0.05, 0.0, BEZEL, piv)
        _image_quad(f"{name}{tag}Screen", xa, xb, -sh / 2, sh / 2, 0.003, u0, u1, SCREEN, piv)
        slab(f"{name}{tag}Back", xa + 0.2, xb - 0.2, -0.15, 0.15, -0.09, -0.05, BEZEL, piv)

    mid = _pivot(f"{name}ScreenMid", (0, sy, sz), root)
    panel("Mid", mid, -sw / 2, sw / 2, 1 / 3, 2 / 3)
    slab(f"{name}MidGlow", -sw / 2, sw / 2, -sh / 2 - 0.03, -sh / 2 - 0.02, -0.04, -0.01, CYAN, mid)
    a = math.radians(50)
    left = _pivot(f"{name}ScreenLeftHinge", (-sw / 2 - 0.02, sy, sz), root, rot=(0, 0, a))
    panel("Left", left, -sw - 0.01, -0.01, 0.0, 1 / 3)
    right = _pivot(f"{name}ScreenRightHinge", (sw / 2 + 0.02, sy, sz), root, rot=(0, 0, -a))
    panel("Right", right, 0.01, sw + 0.01, 2 / 3, 1.0)
    return root


def build_sim_rig_preview(parent=None, name="SimRigPreview"):
    return build_sim_rig(parent, name)

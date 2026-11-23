"""
Loft bed for the upper-right corner under the big window, cyberpunk style:
a low black steel platform bed with magenta neon underglow, a cyan light line
on the headboard, a dark charcoal mattress and pillows, a rumpled rust-red
duvet that hangs over the sides and is folded back at the head, and a black
steel crate (cyan edge light) as a bedside table with a warm lamp and a phone.

    build_loft_bed(parent=None, name="LoftBed") -> root empty

Coordinates are three.js style (Y up). Head of the bed at -Z, foot at +Z,
origin at the centre of the bed on the floor (the bedside crate sits on +X).
"""

import math
import os
import sys

import bpy
from mathutils import noise, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P, rounded_box  # noqa: E402
from gaming_desk import disc, tube  # noqa: E402
from loft_room import block, mat  # noqa: E402

BW, BL = 1.6, 2.05  # mattress width (x) and length (z)
FRAME_H = 0.22  # top of the platform
MAT_H = 0.22  # mattress thickness
TOP = FRAME_H + MAT_H


def _duvet(name, m, parent):
    """A draped, wrinkled sheet: flat on top, hanging over the sides and foot."""
    nx, nz = 46, 50
    x0, x1 = -BW / 2 - 0.22, BW / 2 + 0.22
    z0, z1 = -BL / 2 + 0.55, BL / 2 + 0.24  # starts below the pillows
    verts, faces = [], []
    hang = 0.2  # how far it drops over the edges
    for j in range(nz + 1):
        for i in range(nx + 1):
            u, v = i / nx, j / nz
            x = x0 + (x1 - x0) * u
            z = z0 + (z1 - z0) * v
            y = TOP + 0.04
            # sides: fold down over the mattress edge
            over = max(0.0, abs(x) - BW / 2)
            if over > 0:
                y -= min(hang, over * 1.25)
                x = math.copysign(BW / 2 + 0.03 + max(0.0, over - hang / 1.25) * 0.15, x)
            over_f = max(0.0, z - BL / 2)
            if over_f > 0:
                y -= min(hang, over_f * 1.25)
                z = BL / 2 + 0.03
            # wrinkles: big soft lumps + finer creases
            p = Vector((x * 1.6, z * 1.6, 0.3))
            y += 0.07 * noise.noise(p) + 0.03 * noise.noise(p * 3.1)
            # long diagonal creases
            y += 0.014 * math.sin((x * 0.8 + z) * 9.0 + 2.0 * noise.noise(p * 0.7))
            # never dip into the mattress on the flat top
            if over == 0 and over_f == 0:
                y = max(y, TOP + 0.035)
            # a slight lump where a body would have been
            y += 0.035 * math.exp(-((x + 0.25) ** 2 / 0.12 + (z - 0.1) ** 2 / 0.5))
            verts.append(P(x, y, z))
    for j in range(nz):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append([a, a + 1, a + nx + 2, a + nx + 1])
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    sol = o.modifiers.new("Thick", "SOLIDIFY")
    sol.thickness = 0.035
    sol.offset = 0
    sub = o.modifiers.new("Smooth", "SUBSURF")
    sub.levels = 1
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    o.parent = parent
    return o


def build_loft_bed(parent=None, name="LoftBed"):
    STEEL = mat("BedSteel", "#141517", 0.45, metal=0.8)
    MATTRESS = mat("Mattress", "#1c1d20", 0.85)
    SHEET = mat("BedSheet", "#26282c", 0.9)
    DUVET = mat("Duvet", "#121215", 0.8)  # black
    PILLOW = mat("Pillow", "#2e3035", 0.9)
    PILLOW2 = mat("PillowDark", "#16171a", 0.6)
    CRATE = mat("CrateWood", "#1b1c1f", 0.5, metal=0.6)  # black steel crate
    LAMP = mat("LampGlow", "#ffb35a", emit="#ffb35a", strength=6.0)
    NEON_M = mat("BedNeonMagenta", "#ff2bd6", emit="#ff2bd6", strength=8.0)
    NEON_C = mat("BedNeonCyan", "#22e4ff", emit="#22e4ff", strength=8.0)
    LAMPBODY = mat("LampBody", "#2b2d30", 0.4, metal=0.7)
    PHONE = mat("PhoneScreen", "#0d0f12", 0.2, emit="#3a7bd5", strength=0.6)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---------- steel platform: low frame on legs, slatted base
    fw, fl = BW + 0.12, BL + 0.12
    block("BedFrameSideL", (-fw / 2 + 0.03, FRAME_H - 0.04, 0), (0.06, 0.18, fl), STEEL, root, r=0.004)
    block("BedFrameSideR", (fw / 2 - 0.03, FRAME_H - 0.04, 0), (0.06, 0.18, fl), STEEL, root, r=0.004)
    block("BedFrameFoot", (0, FRAME_H - 0.04, fl / 2 - 0.03), (fw, 0.18, 0.06), STEEL, root, r=0.004)
    block("BedFrameHead", (0, FRAME_H - 0.04, -fl / 2 + 0.03), (fw, 0.18, 0.06), STEEL, root, r=0.004)
    for k in range(9):
        z = -BL / 2 + 0.12 + k * (BL - 0.24) / 8
        block(f"BedSlat{k}", (0, FRAME_H - 0.03, z), (BW, 0.025, 0.08), STEEL, root)
    for k, (lx, lz) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0))):
        block(f"BedLeg{k}", (lx * (fw / 2 - 0.08), (FRAME_H - 0.13) / 2, lz * (fl / 2 - 0.08)), (0.06, FRAME_H - 0.13, 0.06), STEEL, root)
    # neon underglow: a magenta strip under each side rail and the foot (lights the floor)
    block("UnderglowL", (-fw / 2 + 0.06, FRAME_H - 0.135, 0), (0.012, 0.01, fl - 0.2), NEON_M, root)
    block("UnderglowR", (fw / 2 - 0.06, FRAME_H - 0.135, 0), (0.012, 0.01, fl - 0.2), NEON_M, root)
    block("UnderglowFoot", (0, FRAME_H - 0.135, fl / 2 - 0.06), (fw - 0.2, 0.01, 0.012), NEON_M, root)
    # a real light under the frame so previews show the floor glow
    # (lights are not exported; the website adds its own)
    for k, (lx, lz) in enumerate(((-fw / 2 - 0.02, -0.5), (-fw / 2 - 0.02, 0.5), (fw / 2 + 0.02, -0.5), (fw / 2 + 0.02, 0.5), (0, fl / 2 + 0.02))):
        ld = bpy.data.lights.new(f"{name}UnderglowLight{k}", "POINT")
        ld.color = (1.0, 0.17, 0.84)
        ld.energy = 25
        ld.shadow_soft_size = 0.3
        lo = bpy.data.objects.new(f"{name}UnderglowLight{k}", ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(lx, 0.04, lz)
        lo.parent = root
    # low headboard: a padded steel-edged panel
    block("Headboard", (0, FRAME_H + 0.3, -fl / 2 + 0.02), (fw, 0.6, 0.05), STEEL, root, r=0.006)
    rounded_box("HeadboardPad", (0, FRAME_H + 0.33, -fl / 2 + 0.06), (fw - 0.12, 0.46, 0.05), 0.02, PILLOW2, root)
    # cyan light line along the top edge of the headboard
    block("HeadboardNeon", (0, FRAME_H + 0.605, -fl / 2 + 0.05), (fw - 0.1, 0.012, 0.012), NEON_C, root)

    # ---------- mattress + fitted sheet
    rounded_box("Mattress", (0, FRAME_H + MAT_H / 2, 0), (BW, MAT_H, BL), 0.05, MATTRESS, root)
    rounded_box("FittedSheet", (0, TOP - 0.006, 0), (BW + 0.01, 0.02, BL + 0.01), 0.008, SHEET, root)

    # ---------- pillows (soft, slightly squashed and angled)
    for k, (px, rot) in enumerate(((-0.38, 6), (0.36, -9))):
        p = rounded_box(f"Pillow{k}", (px, TOP + 0.08, -BL / 2 + 0.3), (0.62, 0.14, 0.4), 0.06, PILLOW, root)
        p.rotation_euler = (math.radians(-12), 0, math.radians(rot))

    # ---------- duvet: draped and wrinkled, with a folded-back roll at the head
    _duvet("Duvet", DUVET, root)
    # folded-back top edge: a soft, slightly lumpy band lying across the bed
    fold = rounded_box("DuvetFold", (0, TOP + 0.075, -BL / 2 + 0.66), (BW + 0.38, 0.07, 0.34), 0.03, DUVET, root)
    for v in fold.data.vertices:
        v.co.z += 0.018 * noise.noise(Vector((v.co.x * 3.0, v.co.y * 3.0, 1.7)))
    fold.rotation_euler = (math.radians(-4), 0, math.radians(1.5))

    # ---------- bedside crate with a lamp and a phone (on +X, by the head)
    cx, cz = fw / 2 + 0.38, -BL / 2 + 0.35
    ch = 0.5
    block("BedsideCrate", (cx, ch / 2, cz), (0.5, ch, 0.45), CRATE, root, r=0.01)
    for k, y in enumerate((0.15, 0.35)):  # vent slots
        block(f"CrateGap{k}", (cx, y, cz + 0.226), (0.46, 0.015, 0.004), STEEL, root)
    # cyan edge light around the crate top
    for k, (dx, dz, sx, sz) in enumerate(((0, 0.225, 0.5, 0.01), (0, -0.225, 0.5, 0.01), (0.25, 0, 0.01, 0.45), (-0.25, 0, 0.01, 0.45))):
        block(f"CrateNeon{k}", (cx + dx, ch - 0.006, cz + dz), (sx, 0.01, sz), NEON_C, root)
    disc("LampBase", (cx - 0.1, ch + 0.012, cz - 0.05), 0.07, 0.024, LAMPBODY, root)
    tube("LampStem", [(cx - 0.1, ch + 0.02, cz - 0.05), (cx - 0.1, ch + 0.28, cz - 0.05)], 0.008, LAMPBODY, root)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, segments=24, ring_count=12)
    bulb = bpy.context.active_object
    bulb.name = "LampGlobe"
    bulb.location = P(cx - 0.1, ch + 0.34, cz - 0.05)
    bpy.ops.object.shade_smooth()
    bulb.data.materials.append(LAMP)
    bulb.parent = root
    ph = block("Phone", (cx + 0.1, ch + 0.006, cz + 0.06), (0.075, 0.01, 0.15), PHONE, root, r=0.003)
    ph.rotation_euler = (0, 0, math.radians(18))

    return root

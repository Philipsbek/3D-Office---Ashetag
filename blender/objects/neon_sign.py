"""
Neon wall sign for the loft's lower-level red zone: glowing tube lettering
(outline-style neon) on a black acrylic backplate held off the wall by steel
standoffs, a neon border with rounded corners, and a transformer box with its
cable running down the wall.

    build_neon_sign(parent=None, name="NeonSign", text="ASHETAG",
                    color="#ff2438", border="#ff2438") -> root empty

Coordinates are three.js style (Y up, the sign faces +Z). The origin is on
the wall (z = 0) at the centre of the sign.
"""

import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P, _hex  # noqa: E402
from gaming_desk import disc, tube  # noqa: E402
from loft_room import block, mat  # noqa: E402

PW, PH = 1.7, 0.62  # backplate size
OFF = 0.05  # backplate distance from the wall


def _neon_text(name, body, size, z, m, parent, max_width):
    """Outline-style neon tubes following the letter shapes."""
    bpy.ops.object.text_add()
    t = bpy.context.active_object
    t.data.body = body
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.size = size
    t.data.space_character = 1.12
    bpy.context.view_layer.update()
    if t.dimensions.x > max_width:
        t.data.size = size * max_width / t.dimensions.x
    t.data.fill_mode = "NONE"  # no faces: just the outlines...
    t.data.bevel_depth = 0.0065  # ...turned into round tubes
    t.data.bevel_resolution = 3
    t.rotation_euler = (math.pi / 2, 0, 0)
    t.location = P(0, 0, z)
    t.data.materials.append(m)
    bpy.ops.object.convert(target="MESH")
    t = bpy.context.active_object
    t.name = name
    t.parent = parent
    return t


def _rounded_rect_tube(name, w, h, r, z, radius, m, parent, seg=6):
    pts = []
    corners = ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270))
    for cx, cy, a0 in corners:
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    pts.append(pts[0])
    return tube(name, pts, radius, m, parent)


def build_neon_sign(parent=None, name="NeonSign", text="ASHETAG", color="#ff2438", border="#ff2438"):
    ACRYLIC = mat("SignAcrylic", "#060607", 0.5, metal=0.1)  # satin, no mirror blobs
    STEEL = mat("SignSteel", "#5a5e63", 0.25, metal=0.95)
    BOX = mat("SignBox", "#141518", 0.5, metal=0.5)
    CABLE = mat("SignCable", "#0c0c0d", 0.6)
    NEON = mat(f"SignNeon_{color}", color, emit=color, strength=12.0)
    NEON_B = mat(f"SignNeon_{border}", border, emit=border, strength=10.0)
    TUBE_DIM = mat(f"SignNeonDim_{color}", color, 0.3, emit=color, strength=1.5)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # backplate on four standoffs
    block(f"{name}Backplate", (0, 0, OFF), (PW, PH, 0.012), ACRYLIC, root, r=0.01)
    for k, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        disc(f"{name}Standoff{k}", (sx * (PW / 2 - 0.05), sy * (PH / 2 - 0.05), OFF / 2 + 0.006), 0.012, OFF + 0.012, STEEL, root, axis="z")

    zf = OFF + 0.03  # tubes float just in front of the plate
    _rounded_rect_tube(f"{name}Border", PW - 0.07, PH - 0.07, 0.07, zf, 0.008, NEON_B, root)
    _neon_text(f"{name}Text", text, 0.3, zf, NEON, root, max_width=PW - 0.28)
    # small tube clips holding the border
    for k, x in enumerate((-0.6, 0.0, 0.6)):
        for s in (-1, 1):
            block(f"{name}Clip{k}_{s}", (x, s * (PH / 2 - 0.035), OFF + 0.018), (0.012, 0.02, 0.02), STEEL, root)

    # transformer box under the sign + cable running down the wall
    block(f"{name}Transformer", (PW / 2 - 0.2, -PH / 2 - 0.16, 0.04), (0.2, 0.12, 0.07), BOX, root, r=0.006)
    block(f"{name}TransformerLED", (PW / 2 - 0.13, -PH / 2 - 0.14, 0.077), (0.012, 0.012, 0.004), TUBE_DIM, root)
    tube(f"{name}Cable", [(PW / 2 - 0.2, -PH / 2 - 0.1, 0.03), (PW / 2 - 0.2, -PH / 2 + 0.02, 0.03)], 0.006, CABLE, root)
    tube(f"{name}CableDown", [(PW / 2 - 0.25, -PH / 2 - 0.22, 0.02), (PW / 2 - 0.25, -PH / 2 - 1.2, 0.02)], 0.007, CABLE, root)

    return root


def build_neon_sign_preview(parent=None, name="NeonSignPreview", text="ASHETAG", color="#ff2438"):
    """Preview only: the sign at eye level on a dark concrete wall, with a red
    light in front so the wall picks up the glow (lights aren't exported)."""
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    wall = mat("PreviewConcrete", "#1c1c1e", 0.9)
    block(f"{name}Wall", (0, 1.4, -0.06), (3.6, 2.8, 0.1), wall, root)
    sign = build_neon_sign(root, name=f"{name}Sign", text=text, color=color, border=color)
    sign.location = P(0, 1.7, 0)
    for k, (x, w) in enumerate(((-1.3, 35), (1.3, 35))):
        ld = bpy.data.lights.new(f"{name}Glow{k}", "POINT")
        ld.color = _hex(color)
        ld.energy = w
        ld.shadow_soft_size = 0.4
        lo = bpy.data.objects.new(f"{name}Glow{k}", ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(x, 1.2, 0.45)
        lo.parent = root
    return root


def build_sha_area_sign_preview(parent=None, name="ShaAreaPreview"):
    """Preview of the "SHA AREA" sign (same design as the ASHETAG sign)."""
    return build_neon_sign_preview(parent, name, text="SHA AREA")

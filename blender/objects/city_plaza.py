"""
Plaza furniture for the open paved ground round the office, smooth neon-night
style. Every piece faces +Z with its origin on the ground at its centre.

    build_plaza_planter(parent, name, accent)  2.6 m rounded planter, neon rim, a tree, low shrubs
    build_plaza_bench(parent, name, accent)    2.2 m curved-edge bench on two slab legs, neon underglow
    build_plaza_kiosk(parent, name, accent)    noodle-stand kiosk: rounded cabin, lit serving hatch,
                                               awning with neon edge, glowing sign, two stools
    build_plaza_bollard(parent, name, accent)  0.9 m bollard with a glowing top ring
    build_plaza_floor_light(parent, name, accent)  flush round floor light
    build_plaza_kit_preview(parent, name)      all of it on a patch of paving (+ the approved vending machine)

Coordinates are three.js style (Y up).
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
from gaming_desk import disc  # noqa: E402
from loft_room import block, mat  # noqa: E402
from city_smooth import _tree, rounded_band, rounded_prism  # noqa: E402
from city_street import neon_text  # noqa: E402


def _root(name, parent):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    return root


def _mats(accent):
    return {
        "shell": mat("PlazaShell", "#2a2b36", 0.45, metal=0.15),
        "dark": mat("PlazaDark", "#15161c", 0.4, metal=0.5),
        "wood": mat("PlazaWood", "#3a2a22", 0.6),
        "soil": mat("PlazaSoil", "#1a1512", 0.9),
        "leaf": mat("SmoothLeaf", "#1c4a34", 0.7),
        "leafNeon": mat("SmoothLeafGlow", "#2a6a4a", 0.6, emit="#1e8a5a", strength=0.6),
        "trunk": mat("SmoothTrunk", "#2a1d18", 0.8),
        "neon": mat(f"PlazaNeon{accent[1:]}", accent, emit=accent, strength=8.0),
        "warm": mat("PlazaWarm", "#ffcf8a", emit="#ff9e48", strength=2.2),
        "red": mat("PlazaRed", "#8a1420", 0.55),
        "sign": mat("PlazaSignText", "#ffe6b0", emit="#ffcf7a", strength=9.0),
        "steel": mat("PlazaSteel", "#8a90a0", 0.3, metal=0.9),
    }


def build_plaza_planter(parent=None, name="Planter", accent="#2bff9a", seed=1):
    M = _mats(accent)
    root = _root(name, parent)
    rng = random.Random(seed)
    rounded_prism(f"{name}Body", (0, 0, 0), 2.6, 2.6, 1.0, 0.6, M["shell"], root, seg=8, cap_m=M["soil"])
    rounded_band(f"{name}Rim", (0, 0.6, 0), 2.62, 2.62, 1.01, 0.06, M["neon"], root, seg=8)
    rounded_band(f"{name}Foot", (0, 0.0, 0), 2.66, 2.66, 1.03, 0.08, M["dark"], root, seg=8)
    _tree(f"{name}Tree", (0, 0.6, 0), 1.3, {"trunk": M["trunk"], "leaf": M["leaf"], "leafNeon": M["leafNeon"]}, root, rng)
    for k in range(5):  # low shrubs round the trunk
        a = k * 2 * math.pi / 5 + 0.3
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.28, location=P(0.75 * math.cos(a), 0.72, 0.75 * math.sin(a)))
        b = bpy.context.active_object
        b.name = f"{name}Shrub{k}"
        b.scale = (1.0, 1.0, 0.7)
        bpy.ops.object.shade_smooth()
        b.data.materials.append(M["leaf"])
        b.parent = root
    return root


def build_plaza_bench(parent=None, name="Bench", accent="#22e4ff"):
    M = _mats(accent)
    root = _root(name, parent)
    rounded_prism(f"{name}Seat", (0, 0.42, 0), 2.2, 0.62, 0.25, 0.1, M["wood"], root, seg=6, cap_m=M["wood"])
    rounded_prism(f"{name}Back", (0, 0.55, -0.27), 2.2, 0.1, 0.05, 0.42, M["wood"], root, seg=3, cap_m=M["wood"])
    for k, x in enumerate((-0.8, 0.8)):
        rounded_prism(f"{name}Leg{k}", (x, 0, 0), 0.12, 0.58, 0.05, 0.42, M["dark"], root, seg=3, cap_m=M["dark"])
    rounded_band(f"{name}Glow", (0, 0.38, 0), 2.0, 0.5, 0.2, 0.025, M["neon"], root, seg=6)
    return root


def build_plaza_kiosk(parent=None, name="Kiosk", accent="#ff4fd8", text="NOODLES"):
    M = _mats(accent)
    root = _root(name, parent)
    W, D, H = 3.2, 2.2, 2.6
    rounded_prism(f"{name}Cabin", (0, 0, 0), W, D, 0.6, H, M["shell"], root, seg=6, cap_m=M["dark"])
    # lit serving hatch on the front with a counter
    block(f"{name}Hatch", (0, 1.45, D / 2 + 0.005), (2.3, 0.95, 0.02), M["warm"], root)
    block(f"{name}Counter", (0, 0.98, D / 2 + 0.22), (2.5, 0.07, 0.45), M["dark"], root, r=0.02)
    rounded_band(f"{name}HatchNeon", (0, 0.96, D / 2 + 0.22), 2.52, 0.47, 0.02, 0.03, M["neon"], root, seg=2)
    # awning with neon edge, then the sign box on the roof
    rounded_prism(f"{name}Awning", (0, H - 0.05, 0.35), W + 0.5, D + 1.0, 0.75, 0.14, M["red"], root, seg=6, cap_m=M["red"])
    rounded_band(f"{name}AwningNeon", (0, H - 0.07, 0.35), W + 0.52, D + 1.02, 0.76, 0.05, M["neon"], root, seg=6)
    rounded_prism(f"{name}SignBox", (0, H + 0.09, 0.4), 2.6, 0.3, 0.12, 0.62, M["dark"], root, seg=3, cap_m=M["dark"])
    neon_text(f"{name}SignText", text, (0, H + 0.4, 0.56), 0.38, M["sign"], root, 2.3, depth=0.03)
    # two stools at the counter
    for k, x in enumerate((-0.7, 0.7)):
        disc(f"{name}StoolTop{k}", (x, 0.72, D / 2 + 0.75), 0.2, 0.06, M["red"], root, verts=16)
        disc(f"{name}StoolLeg{k}", (x, 0.36, D / 2 + 0.75), 0.04, 0.7, M["steel"], root, verts=8)
        disc(f"{name}StoolFoot{k}", (x, 0.02, D / 2 + 0.75), 0.16, 0.04, M["dark"], root, verts=16)
    return root


def build_plaza_bollard(parent=None, name="Bollard", accent="#22e4ff"):
    M = _mats(accent)
    root = _root(name, parent)
    disc(f"{name}Post", (0, 0.42, 0), 0.12, 0.84, M["dark"], root, verts=16)
    disc(f"{name}Ring", (0, 0.8, 0), 0.125, 0.07, M["neon"], root, verts=16)
    disc(f"{name}Cap", (0, 0.86, 0), 0.11, 0.05, M["steel"], root, verts=16)
    return root


def build_plaza_floor_light(parent=None, name="FloorLight", accent="#22e4ff"):
    M = _mats(accent)
    root = _root(name, parent)
    disc(f"{name}Rim", (0, 0.01, 0), 0.32, 0.02, M["steel"], root, verts=24)
    disc(f"{name}Glow", (0, 0.022, 0), 0.24, 0.01, M["neon"], root, verts=24)
    return root


def build_plaza_kit_preview(parent=None, name="PlazaKitPreview"):
    import city_roads
    import vending_machine

    root = _root(name, parent)
    pave = city_roads.paving_mat()
    g = block(f"{name}Ground", (0, -0.05, 0), (26, 0.1, 16), pave, root)
    bpy.context.view_layer.update()
    city_roads._world_uv(g)
    build_plaza_planter(root, f"{name}Planter0").location = P(-8, 0, -3)
    build_plaza_planter(root, f"{name}Planter1", "#22e4ff", seed=2).location = P(7.5, 0, -4)
    for k, (x, z, rot) in enumerate(((-4.5, -3.6, 0), (3.6, -4.6, 0), (-8, 0.4, 180))):
        b = build_plaza_bench(root, f"{name}Bench{k}")
        b.location = P(x, 0, z)
        b.rotation_euler = (0, 0, math.radians(rot))
    build_plaza_kiosk(root, f"{name}Kiosk").location = P(0, 0, -2.5)
    vm = vending_machine.build_vending_machine(root, f"{name}Vending")
    vm.location = P(4.0, 0, -6.2)
    for k, x in enumerate(range(-10, 11, 4)):
        build_plaza_bollard(root, f"{name}Bollard{k}", "#22e4ff" if k % 2 else "#ff4fd8").location = P(x, 0, 6.5)
    for k, (x, z) in enumerate(((-5, 2.5), (-1, 3.5), (3, 2.5), (7, 3.5), (10, 0))):
        build_plaza_floor_light(root, f"{name}Floor{k}").location = P(x, 0, z)
    fill = bpy.data.lights.new(f"{name}Fill", "POINT")
    fill.color = (0.6, 0.5, 1.0)
    fill.energy = 12000
    fill.shadow_soft_size = 6
    fo = bpy.data.objects.new(f"{name}Fill", fill)
    bpy.context.collection.objects.link(fo)
    fo.location = P(0, 14, 10)
    warm = bpy.data.lights.new(f"{name}KioskLight", "POINT")
    warm.color = (1.0, 0.7, 0.45)
    warm.energy = 400
    wo = bpy.data.objects.new(f"{name}KioskLight", warm)
    bpy.context.collection.objects.link(wo)
    wo.location = P(0, 1.6, 0.2)
    return root

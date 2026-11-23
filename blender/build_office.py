"""
Builds the 3D office in Blender, saves office.blend, and exports
public/models/office.glb for the website.

Run it (no Blender window needed):
  "C:\\Program Files\\Blender Foundation\\Blender 5.3\\blender.exe" -b --python blender/build_office.py

Or just open blender/office.blend, edit it by hand, and export with
File > Export > glTF 2.0 (.glb) using the settings listed at the bottom.

HOW THE WEBSITE READS THIS FILE
- Any object (usually an Empty) with a custom property "link" becomes
  clickable. Clicking any mesh under it goes to that URL.
  "label" is the text shown on hover.
  (Object Properties > Custom Properties in Blender; exported as glTF "extras",
  which three.js puts in object.userData.)
- Objects named "ArcadeScreen" and "TVScreen" get live textures from code.
"""

import bpy
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import character  # noqa: E402  (blender/character.py)

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "objects"))
import gaming_chair  # noqa: E402
import gaming_desk  # noqa: E402
import razer_keyboard  # noqa: E402
import razer_monitor  # noqa: E402  (kept for reference; desks now use dev_monitor)
import dev_monitor  # noqa: E402
import razer_mouse  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_GLB = os.path.normpath(os.path.join(HERE, "..", "public", "models", "office.glb"))
OUT_BLEND = os.path.join(HERE, "office.blend")

bpy.ops.wm.read_factory_settings(use_empty=True)
COLL = bpy.context.collection


# ---------------------------------------------------------------- helpers
# The web scene uses three.js coordinates (Y up). Blender is Z up.
# P() and S() convert, so positions here match the old placeholder layout.
def P(x, y, z):
    return (x, -z, y)


def S(sx, sy, sz):
    return (sx, sz, sy)


def hexc(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


_mats = {}


def mat(name, color, rough=0.7, metal=0.0, emit=None, strength=1.0):
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*hexc(color), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*hexc(emit), 1)
        b.inputs["Emission Strength"].default_value = strength
    _mats[name] = m
    return m


def finish(o, name, m, parent, bevel):
    o.name = name
    if m:
        o.data.materials.append(m)
    if bevel > 0:
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        md = o.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = 2
        md.limit_method = "ANGLE"
    if parent:
        o.parent = parent
    return o


def box(name, pos, size, m, parent=None, rx=0.0, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.location = P(*pos)
    o.scale = S(*size)
    o.rotation_euler = (rx, 0, 0)
    return finish(o, name, m, parent, bevel)


def plane(name, pos, w, h, m, parent=None, facing="z"):
    """facing: 'z' = faces the viewer (+Z in three.js), 'x' = faces +X, 'up' = floor."""
    bpy.ops.mesh.primitive_plane_add(size=1)
    o = bpy.context.active_object
    o.location = P(*pos)
    o.scale = (w, h, 1)
    o.rotation_euler = {"z": (math.pi / 2, 0, 0), "x": (math.pi / 2, 0, math.pi / 2), "up": (0, 0, 0)}[facing]
    return finish(o, name, m, parent, 0)


def cylinder(name, pos, radius, height, m, parent=None, rx=0.0, verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, vertices=verts)
    o = bpy.context.active_object
    o.location = P(*pos)
    o.rotation_euler = (rx, 0, 0)
    bpy.ops.object.shade_smooth()
    return finish(o, name, m, parent, 0)


def sphere(name, pos, radius, m, parent=None, scale=(1, 1, 1), ico=False):
    if ico:
        bpy.ops.mesh.primitive_ico_sphere_add(radius=radius, subdivisions=2)
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=24, ring_count=12)
        bpy.ops.object.shade_smooth()
    o = bpy.context.active_object
    o.location = P(*pos)
    o.scale = S(*scale)
    return finish(o, name, m, parent, 0)


def group(name, pos=(0, 0, 0), link=None, label=None):
    e = bpy.data.objects.new(name, None)
    COLL.objects.link(e)
    e.location = P(*pos)
    if link:
        e["link"] = link
        e["label"] = label or name
    return e


# ---------------------------------------------------------------- materials
M_FLOOR = mat("Floor", "#151515", rough=0.55)
M_WALL = mat("Wall", "#1a1a1a", rough=0.9)
M_STEP = mat("Concrete", "#202020", rough=0.85)
M_DARK = mat("DarkPlastic", "#161616", rough=0.5)
M_METAL = mat("Metal", "#3a3a3a", rough=0.35, metal=0.9)
M_WOOD = mat("Wood", "#4a3424", rough=0.6)
M_FABRIC = mat("Fabric", "#202226", rough=0.95)
M_SKIN = mat("Skin", "#c99a7a", rough=0.6)
M_SHIRT = mat("Shirt", "#2c2c2c", rough=0.9)
M_STRIP = mat("LightStrip", "#ffffff", emit="#ffffff", strength=8)
M_NEON = mat("Neon", "#ffffff", emit="#ffffff", strength=6)
M_MARQUEE = mat("Marquee", "#ff7a1a", emit="#ff7a1a", strength=1.2)
M_BTN_BLUE = mat("ButtonBlue", "#2b6bff", emit="#2b6bff", strength=1.5)
M_BTN_RED = mat("ButtonRed", "#ff3344", emit="#ff3344", strength=1.5)
M_SCREEN = mat("ScreenPlaceholder", "#000000", emit="#222222", strength=1)
# A tiny 2x2 image on the screen material, so the optimiser keeps the screens' UVs
# (the website swaps in live canvas textures that need them). Not single-colour on
# purpose: a flat image would be folded into a plain colour and the UVs dropped.
_ph = bpy.data.images.new("ScreenPlaceholderTex", 2, 2)
_ph.pixels = [0.13, 0.13, 0.13, 1, 0.12, 0.12, 0.12, 1, 0.12, 0.12, 0.12, 1, 0.13, 0.13, 0.13, 1]
_ph.pack()
_tex = M_SCREEN.node_tree.nodes.new("ShaderNodeTexImage")
_tex.image = _ph
M_SCREEN.node_tree.links.new(_tex.outputs["Color"], M_SCREEN.node_tree.nodes["Principled BSDF"].inputs["Emission Color"])
M_POT = mat("Pot", "#2a2a2a", rough=0.8)
M_LEAF = mat("Leaf", "#2f5a32", rough=0.8)
SCREEN_COLORS = ["#2fd17a", "#4aa3ff", "#ff7a1a", "#c77dff", "#4aa3ff", "#2fd17a"]

# ---------------------------------------------------------------- the loft (approved revamp)
# Every piece below is an approved asset (blender/objects/APPROVED.md, L1-L16
# plus the Razer desk set 1-5). Rotations are three.js yaw: an object built
# facing +Z ends up facing (sin yaw, cos yaw).
import loft_room  # noqa: E402
import fan_unit  # noqa: E402
import bookshelf  # noqa: E402
import arcade_cabinet  # noqa: E402
import loft_bed  # noqa: E402
import telescope  # noqa: E402
import holo_board  # noqa: E402
import kitchenette  # noqa: E402
import neon_sign  # noqa: E402
import lounge_table  # noqa: E402
import e_moped  # noqa: E402
import cargo_crate  # noqa: E402
import vending_machine  # noqa: E402
import boombox  # noqa: E402
import potted_plant  # noqa: E402
import floor_cables  # noqa: E402
import glass_room  # noqa: E402
import sim_racing  # noqa: E402
import chill_area  # noqa: E402
import bar as bar_kit  # noqa: E402
import bean_bag  # noqa: E402
import lounge_set  # noqa: E402
import hanging_lights  # noqa: E402
import server_rack  # noqa: E402
import pinball  # noqa: E402
import wall_art  # noqa: E402
import mini_fridge  # noqa: E402
import meeting_set  # noqa: E402
import clutter  # noqa: E402

UP = loft_room.MEZ_Y  # upper floor height
Z_BACK = loft_room.Z0  # back wall


def place(name, pos, yaw_deg=0.0, parent=None, link=None, label=None):
    g = group(name, pos, link=link, label=label)
    g.rotation_euler = (0, 0, math.radians(yaw_deg))
    if parent:
        g.parent = parent
    return g



def merge_into(spot, name):
    """Join every mesh/curve/text under `spot` into one mesh (one primitive per material on
    export), parented back under `spot` in place. Static props with hundreds of tiny parts
    (bottles, snacks, rugs) become a handful of draw calls on the site."""
    def textured(o):  # image-textured parts (TV screen, rug top) stay separate so their maps survive
        return o.type == "MESH" and any(
            m and m.use_nodes and any(n.type == "TEX_IMAGE" for n in m.node_tree.nodes) for m in o.data.materials
        )

    keep = [o for o in spot.children_recursive if textured(o)]
    for o in keep:
        mw = o.matrix_world.copy()
        o.parent = spot
        o.matrix_world = mw
    parts = [o for o in spot.children_recursive if o.type in ("MESH", "CURVE", "FONT") and o not in keep]
    if not parts:
        return None
    bpy.ops.object.select_all(action="DESELECT")
    for o in parts:
        o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.convert(target="MESH")  # curves/text/bevels -> real geometry
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    bpy.ops.object.join()
    merged = bpy.context.active_object
    merged.name = name
    merged.data.name = name
    for e in [o for o in spot.children_recursive if o.type == "EMPTY"]:
        bpy.data.objects.remove(e, do_unlink=True)
    merged.parent = spot
    merged.matrix_parent_inverse = spot.matrix_world.inverted()
    return merged


room = group("Room")
loft_room.build_loft_room(room, name="Loft")

# ================================================================ UPPER FLOOR
# ---------- workstation (→ /people): two Razer desk setups, hero + typer, fan unit, bookshelf
work = place("Workstation", (0, 0, 0), link="/people", label="People")
DESK_W, DESK_D = 1.6, 0.75
for i, x in enumerate((-5.25, -3.6)):
    d = place(f"Desk{i}", (x, UP, Z_BACK + DESK_D / 2 + 0.06), 0, work)
    gaming_desk.build_gaming_desk(d, name=f"GamingDesk{i}", width=DESK_W, depth=DESK_D, mount="front")
    mon = place(f"MonitorSpot{i}", (0, 0.75, -0.17), 0, d)
    # 40"-class curved ultrawides: desk 0 shows the code editor, desk 1 the repo page (approved 2026-11-23)
    dev_monitor.build_dev_monitor(mon, name=f"DevMonitor{i}", screen="code" if i == 0 else "repo")
    kb = place(f"KeyboardSpot{i}", (0.07, 0.7555, 0.03), 0, d)
    razer_keyboard.build_razer_keyboard(kb, name=f"RazerKeyboard{i}")
    ms = place(f"MouseSpot{i}", (0.4, 0.7555, 0.1), 0, d)
    razer_mouse.build_razer_mouse(ms, name=f"RazerMouse{i}")
    if i == 0:
        # the hero, on a chair swivelled round toward the camera
        seat = place("HeroSeat", (0, 0, 0.78), 38, d)
        gaming_chair.build_gaming_chair(seat, name="HeroChair")
        character.build_character(seat, pose="sit", name="Character")
    else:
        seat = place("TyperSeat", (0, 0, 0.65), 180, d)
        gaming_chair.build_gaming_chair(seat, name="TyperChair")
        character.build_character(seat, pose="type", name="Typer")
fan = place("FanSpot", (-6.62, UP, -4.2), 90, work)
fan_unit.build_fan_unit(fan, name="FanUnit")
shelf = place("BookshelfSpot", (-4.42, UP + 1.5, Z_BACK), 0, work)
bookshelf.build_bookshelf(shelf, name="Bookshelf", length=3.2, shelves=2)

# ---------- arcades (→ /lab): playable blue cabinet + decorative red one
arc = place("Arcade", (-1.15, UP, Z_BACK + 0.47), 0, link="/lab", label="Lab")
arcade_cabinet.build_arcade_pair(arc, name="ArcadePair")

# ---------- bedroom corner: holo Services board (→ /services), bed, telescope
board = place("ServicesBoard", (4.1, 4.95, Z_BACK + 0.25), 0, link="/services", label="Services")
holo_board.build_holo_board(board, name="HoloBoard")
# three bean bags under the window (replaced the bed, 2026-11-21)
beans = place("BeanBagSpot", (3.7, UP, -4.45), 0)
bean_bag.build_bean_bag_set(beans, name="BeanBagSet")
scope = place("TelescopeSpot", (6.15, UP, -3.55), 200)
telescope.build_telescope(scope, name="Telescope", tilt_deg=28)

# ================================================================ LOWER FLOOR
kitchen = place("KitchenSpot", (-7.0, 0, -4.35), 90)
kitchenette.build_kitchenette(kitchen, name="Kitchenette")
sign = place("NeonSignSpot", (-4.55, 1.85, Z_BACK), 0)
neon_sign.build_neon_sign(sign, name="NeonSign", text="PHILIPS BEK")
vend = place("VendingSpot", (0.9, 0, Z_BACK + 0.45), 0)
vending_machine.build_vending_machine(vend, name="VendingMachine")
moped = place("MopedSpot", (5.25, 0, -3.7), 0)
e_moped.build_e_moped(moped, name="EMoped")

# lounge table out front; the sleeper naps at it on the first stool
table = place("LoungeSpot", (-2.25, 0, -1.25), 0)
lounge_table.build_lounge_table(table, name="LoungeTable", stools=3)
nap = place("SleeperSeat", (-0.75, 0, lounge_table.TD / 2 + 0.25), 180, table)
character.build_character(nap, pose="sleep", name="Sleeper")

# (glass room + SHA AREA sign in the front-left corner removed at the user's request, 2026-11-22)
# sim-racing rig in that corner: screens against the glass wall, the driver looking out at the city
rig = place("SimRigSpot", (-5.35, 0, 3.0), 90)  # tucked into the front-left corner (glass wall + open front)
sim_racing.build_sim_rig(rig, name="SimRig")
# chill (gaming) corner between the glass wall and Chengnan's table: rug, big TV against the
# glass facing into the room, console, two pads, three lounger bean bags (approved 2026-11-23)
chill = place("ChillSpot", (-5.25, 0, -0.375), 90)
chill_area.build_chill_area(chill, name="ChillArea")
merge_into(chill, "ChillAreaMerged")
# neon bar under the mezzanine behind Chengnan's table: back bar against the back wall, counter
# facing the room, drinks + snacks on it, the ring pendant hanging over it (approved 2026-11-23)
bar_spot = place("BarSpot", (-1.85, 0, -4.44), 0)
bar_kit.build_bar_area(bar_spot, name="Bar")
merge_into(bar_spot, "BarMerged")
crate2 = place("CrateSpot2", (6.2, 0, 0.9), -24)
cargo_crate.build_cargo_crate(crate2, name="CrateSolo", size=(0.95, 0.55, 0.6))
boom = place("BoomboxSpot", (-0.35, 0, -0.15), -22)
boombox.build_boombox(boom, name="Boombox")
plant = place("PlantSpot", (2.7, 0, -2.05), 0)
potted_plant.build_potted_plant(plant, name="PottedPlant")
# (floor cables removed from the loft at the user's request, 2026-11-21)

# ================================================================ FURNISHING ROUND (F1-F8, 2026-11-21)
# lounge: rug + L-sofa + hologram coffee table on the open front floor, sofa facing the camera
lounge = place("LoungeSetSpot", (0.6, 0, 1.6), 0)
lounge_set.build_lounge_set(lounge, name="LoungeSet")

# hanging lights under the mezzanine (its underside is at y = 3.0)
CEIL = loft_room.MEZ_Y - loft_room.MEZ_T
bulbs = place("BulbClusterSpot", (-5.7, CEIL, -4.0), 0)
hanging_lights.build_bulb_cluster(bulbs, name="KitchenBulbs")
nbar = place("NeonBarSpot", (0.9, CEIL, -4.25), 0)
hanging_lights.build_neon_bar_pendant(nbar, name="AlcoveNeonBar", drop=0.75, length=1.4)
ringp = place("RingPendantSpot", (-2.35, CEIL, -4.1), 0)
hanging_lights.build_ring_pendant(ringp, name="RingPendant", drop=0.9)

# server racks in the back-right corner (beside the pipes), doors facing out; pinball side-on by the stairs
racks = place("ServerRackSpot", (7.55, 0, Z_BACK + 0.53), 0)  # back-right corner, just past the riser pipes
server_rack.build_server_rack_pair(racks, name="ServerRacks")
pin = place("PinballSpot", (6.3, 0, 2.3), -90)
pinball.build_pinball(pin, name="Pinball")

# posters on the lower back wall (the LED mural on the left wall went when that wall turned to glass, 2026-11-22)
for k, (x, art, col) in enumerate(((-2.75, "circles", "#ff2bd6"), (-1.95, "stripes", "#22e4ff"), (-1.15, "wave", "#ffd21a"))):
    pst = place(f"PosterSpot{k}", (x, 1.65, Z_BACK), 0)
    wall_art.build_poster(pst, name=f"Poster{k}", art=art, glow=col)

# mini fridge upstairs between the arcades and the bean bags
fridge = place("FridgeSpot", (0.6, UP, Z_BACK + 0.33), 0)
mini_fridge.build_mini_fridge(fridge, name="MiniFridge")

# (glass room furniture - meeting table set + wall rack - removed with the glass room, 2026-11-22)

# small props
gtr = place("GuitarSpot", (1.3, UP, -5.45), -15)
clutter.build_guitar_on_stand(gtr, name="Guitar")
hp = place("HeadphoneSpot", (-5.92, UP + 0.75, -5.62), 20)
clutter.build_headphone_stand(hp, name="HeadphoneStand")
cans = place("CansSpot", (2.45, UP, -3.6), 0)
clutter.build_can_cluster(cans, name="Cans")
pizza = place("PizzaSpot", (-1.55, 0, 1.15), 18)
clutter.build_pizza_boxes(pizza, name="PizzaBoxes")
skate = place("SkateSpot", (2.95, 0, 3.35), 28)
clutter.build_skateboard(skate, name="Skateboard")
for k, x in enumerate((-1.6, 2.6)):  # hanging from the mezzanine railing, over the lower floor
    rail_y, rail_z, hook_z = loft_room.MEZ_Y + 1.0, loft_room.MEZ_Z - 0.12, loft_room.MEZ_Z + 0.2
    gaming_desk.tube(f"HangingPlantArm{k}", [(x, rail_y, rail_z), (x, rail_y + 0.06, hook_z)], 0.012, M_METAL, room)
    hpl = place(f"HangingPlantSpot{k}", (x, rail_y + 0.06, hook_z), 0)
    clutter.build_hanging_plant(hpl, name=f"HangingPlant{k}", drop=1.0, seed=6 + k)

# ---------------------------------------------------------------- save + export
# 1) Blender exports an uncompressed file to blender/out/office.raw.glb
# 2) glTF-Transform (npm dev dependency) shrinks it for the web:
#    dedup  - the six desk setups, chairs and characters are identical copies;
#             store each shape once and let every copy point at it
#    prune  - drop anything left unused (but keep empty markers)
#    draco  - compress the geometry (done once, so precision is only lost once)
# 3) the site's model URL version and expected size are updated automatically
import re
import subprocess

ROOT = os.path.normpath(os.path.join(HERE, ".."))
RAW_GLB = os.path.join(HERE, "out", "office.raw.glb")
os.makedirs(os.path.dirname(RAW_GLB), exist_ok=True)
os.makedirs(os.path.dirname(OUT_GLB), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
bpy.ops.export_scene.gltf(
    filepath=RAW_GLB,
    export_format="GLB",
    export_extras=True,                         # custom properties -> userData
    export_apply=True,                          # apply bevel modifiers
    export_draco_mesh_compression_enable=False, # compressed later, after dedup
    export_lights=False,                        # lights live in code
    export_cameras=False,
)
print("EXPORTED", RAW_GLB, os.path.getsize(RAW_GLB), "bytes")

TMP = os.path.join(HERE, "out", "office.dedup.glb")
for cmd in (
    f'npx gltf-transform dedup "{RAW_GLB}" "{TMP}"',
    # keep empty marker objects the site may look up by name
    f'npx gltf-transform prune "{TMP}" "{TMP}" --keep-leaves true',
    f'npx gltf-transform draco "{TMP}" "{OUT_GLB}"',
):
    subprocess.run(cmd, shell=True, check=True, cwd=ROOT)
os.remove(TMP)
size = os.path.getsize(OUT_GLB)
print("OPTIMIZED", OUT_GLB, size, "bytes")

scene_tsx = os.path.join(ROOT, "components", "Scene.tsx")
src = open(scene_tsx, encoding="utf-8").read()
src = re.sub(r"office\.glb\?v=(\d+)", lambda m: f"office.glb?v={int(m.group(1)) + 1}", src, count=1)
src = re.sub(r"const MODEL_BYTES = [\d_]+", f"const MODEL_BYTES = {size:_}", src, count=1)
open(scene_tsx, "w", encoding="utf-8").write(src)
print("UPDATED", scene_tsx)

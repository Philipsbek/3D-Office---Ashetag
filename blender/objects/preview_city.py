"""
Preview render for city-scale pieces (buildings, vehicles): purple night-sky
background, dark ground, no studio backdrop.

  blender -b --python blender/objects/preview_city.py -- <module> <function> <out.png> <cam_x> <cam_y> <cam_z> <tgt_x> <tgt_y> <tgt_z> [lens] [fog] [eevee|cycles]

Camera/target are three.js coordinates (Y up).
"""

import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
module_name, func_name, out = a[0], a[1], os.path.abspath(a[2])
cam = tuple(float(v) for v in a[3:6])
tgt = tuple(float(v) for v in a[6:9])
lens = float(a[9]) if len(a) > 9 else 35
fog = float(a[10]) if len(a) > 10 else 0.0
engine_name = a[11] if len(a) > 11 else "eevee"  # "cycles" for true reflections of off-screen things

bpy.ops.wm.read_factory_settings(use_empty=True)
from character import P  # noqa: E402

getattr(importlib.import_module(module_name), func_name)()
scene = bpy.context.scene

# dark ground
g = bpy.data.materials.new("PreviewGround")
g.use_nodes = True
gb = g.node_tree.nodes["Principled BSDF"]
gb.inputs["Base Color"].default_value = (0.012, 0.01, 0.02, 1)
gb.inputs["Roughness"].default_value = 0.18 if fog else 0.5  # wet street
bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 0, -0.02))
bpy.context.active_object.data.materials.append(g)

# purple night sky
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.11, 0.04, 0.15, 1)
bg.inputs["Strength"].default_value = 0.6
if fog:
    # purple volumetric haze
    vs = world.node_tree.nodes.new("ShaderNodeVolumeScatter")
    vs.inputs["Color"].default_value = (0.75, 0.55, 1.0, 1)
    vs.inputs["Density"].default_value = fog
    world.node_tree.links.new(vs.outputs[0], world.node_tree.nodes["World Output"].inputs["Volume"])

cd = bpy.data.cameras.new("Cam")
cd.lens = lens
cd.clip_end = 5000
c = bpy.data.objects.new("Cam", cd)
scene.collection.objects.link(c)
scene.camera = c
c.location = P(*cam)
c.rotation_euler = (Vector(P(*tgt)) - Vector(c.location)).to_track_quat("-Z", "Y").to_euler()

for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try:
        scene.render.engine = engine
        break
    except TypeError:
        continue
# ray-traced reflections so glass mirrors the lit city (EEVEE Next)
for attr in ("use_raytracing",):
    try:
        setattr(scene.eevee, attr, True)
    except Exception:
        pass
if engine_name == "cycles":
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 96
    scene.cycles.use_denoising = True
    try:
        scene.cycles.device = "GPU"
    except Exception:
        pass
scene.render.resolution_x = 1800
scene.render.resolution_y = 1000
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = 0.4
try:
    scene.view_settings.look = "AgX - Punchy"
except TypeError:
    pass
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("RENDERED", out)

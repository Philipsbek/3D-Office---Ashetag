"""
Product-shot preview for a single scripted asset: three views (3/4 front,
side, back) on a soft studio backdrop, rendered with EEVEE.

  blender -b --python blender/objects/preview_object.py -- <module> <function> <out.png>

e.g. -- gaming_chair build_gaming_chair previews/gaming_chair.png
"""

import importlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import bpy  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
module_name, func_name, out_path = args[0], args[1], os.path.abspath(args[2])
spacing = float(args[3]) if len(args) > 3 else 1.1
cam_dist = float(args[4]) if len(args) > 4 else 5.2
cam_height = float(args[5]) if len(args) > 5 else 1.15
views = [float(v) for v in args[6].split(",")] if len(args) > 6 else [30, 90, 180]
cam_pitch = float(args[7]) if len(args) > 7 else 84  # 90 = level, lower = looking down
dark = len(args) > 8 and args[8] == "dark"  # dim studio, so RGB lighting stands out

bpy.ops.wm.read_factory_settings(use_empty=True)
build = getattr(importlib.import_module(module_name), func_name)

# views side by side (yaw in degrees; objects face -Y in Blender = toward camera)
for i, yaw in enumerate(views):
    e = bpy.data.objects.new(f"View{i}", None)
    bpy.context.collection.objects.link(e)
    e.location = ((i - (len(views) - 1) / 2) * spacing, 0, 0)
    e.rotation_euler = (0, 0, math.radians(yaw))
    build(e, name=f"Asset{i}")

scene = bpy.context.scene

# backdrop: floor + curved-ish back wall
bd = bpy.data.materials.new("Backdrop")
try:
    bd.use_nodes = True
except Exception:
    pass
bd.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.03, 0.03, 0.035, 1) if dark else (0.82, 0.82, 0.83, 1)
bd.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
bpy.context.active_object.data.materials.append(bd)
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 6, 0), rotation=(math.pi / 2, 0, 0))
bpy.context.active_object.data.materials.append(bd)

# world + lights
world = bpy.data.worlds.new("World")
scene.world = world
try:
    world.use_nodes = True
except Exception:
    pass
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.8, 0.8, 0.82, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.04 if dark else 0.45


def area(name, loc, rot, energy, size):
    d = bpy.data.lights.new(name, "AREA")
    d.energy = energy * (0.12 if dark else 1.0)
    d.size = size
    o = bpy.data.objects.new(name, d)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    bpy.context.collection.objects.link(o)


area("Key", (-2.5, -3.5, 3.5), (50, 0, -35), 700, 3)
area("Fill", (3.5, -3, 2), (65, 0, 50), 220, 4)
area("Rim", (0, 3, 3.5), (-45, 0, 0), 500, 4)

# camera
cam_data = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam)
scene.camera = cam
cam.location = (0, -cam_dist, cam_height)
cam.rotation_euler = (math.radians(cam_pitch), 0, 0)
cam_data.lens = 50

# render settings
for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "CYCLES"):
    try:
        scene.render.engine = engine
        break
    except TypeError:
        continue
if scene.render.engine == "CYCLES":
    scene.cycles.samples = 64
scene.render.resolution_x = 1800
scene.render.resolution_y = 900
scene.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
scene.view_settings.exposure = 0.0 if dark else -0.4
if dark and hasattr(scene, "eevee") and hasattr(scene.eevee, "use_bloom"):
    scene.eevee.use_bloom = True
scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print("RENDERED", out_path, scene.render.engine)

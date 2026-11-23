"""
Glass-room meeting set: a round black pedestal table with a cyan glow ring
under the top, four black swivel chairs (shell seat + back, chrome gas lift,
5-star base, cyan accent line), and an open black shelving rack for the wall
with books, boxes, a speaker, a trophy, a small plant and cyan shelf lights.

    build_meeting_table_set(parent=None, name="MeetingSet") -> table + 4 chairs
    build_wall_rack(parent=None, name="WallRack", w=1.5, h=1.9, d=0.38) -> rack
        (origin on the floor at the middle of its back edge, faces +Z)
    build_meeting_room_preview(parent, name) -> both inside the glass room

Coordinates are three.js style (Y up). Table origin at its centre on the floor.
"""

import math
import os
import random
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P, rounded_box  # noqa: E402
from gaming_desk import disc, ring, tube  # noqa: E402
from loft_room import block, mat  # noqa: E402
from bookshelf import _join  # noqa: E402

TABLE_R, TABLE_Y = 0.62, 0.74
SEAT_Y = 0.47


def _mats():
    return {
        "black": mat("MeetBlack", "#0d0e11", 0.3, metal=0.4),
        "shell": mat("MeetShell", "#141519", 0.45),
        "pad": mat("MeetPad", "#1e1f25", 0.8),
        "chrome": mat("MeetChrome", "#a3a9b0", 0.12, metal=1.0),
        "steel": mat("MeetSteel", "#1b1c20", 0.35, metal=0.85),
        "cyan": mat("MeetCyan", "#22e4ff", emit="#22e4ff", strength=8.0),
    }


def _chair(name, M, parent):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    root.parent = parent
    # 5-star base with castors + chrome gas lift
    for k in range(5):
        a = 2 * math.pi * k / 5
        tube(f"{name}Leg{k}", [(0, 0.08, 0), (0.28 * math.cos(a), 0.05, 0.28 * math.sin(a))], 0.016, M["steel"], root)
        disc(f"{name}Castor{k}", (0.28 * math.cos(a), 0.03, 0.28 * math.sin(a)), 0.025, 0.025, M["black"], root, axis="x")
    disc(f"{name}Hub", (0, 0.08, 0), 0.04, 0.05, M["steel"], root)
    tube(f"{name}Lift", [(0, 0.08, 0), (0, SEAT_Y - 0.06, 0)], 0.02, M["chrome"], root)
    # shell seat with a pad, and a curved back
    rounded_box(f"{name}Seat", (0, SEAT_Y - 0.03, 0.02), (0.48, 0.06, 0.46), 0.03, M["shell"], root)
    rounded_box(f"{name}SeatPad", (0, SEAT_Y + 0.005, 0.03), (0.42, 0.03, 0.4), 0.015, M["pad"], root)
    back = rounded_box(f"{name}Back", (0, SEAT_Y + 0.3, -0.21), (0.46, 0.5, 0.05), 0.025, M["shell"], root)
    back.rotation_euler = (math.radians(-10), 0, 0)
    pad = rounded_box(f"{name}BackPad", (0, SEAT_Y + 0.3, -0.18), (0.4, 0.42, 0.025), 0.012, M["pad"], root)
    pad.rotation_euler = (math.radians(-10), 0, 0)
    tube(f"{name}BackArm", [(0, SEAT_Y - 0.04, -0.15), (0, SEAT_Y + 0.08, -0.22)], 0.018, M["steel"], root)
    # thin cyan accent along the top of the back
    acc = block(f"{name}Accent", (0, SEAT_Y + 0.555, -0.255), (0.38, 0.008, 0.008), M["cyan"], root)
    acc.rotation_euler = (math.radians(-10), 0, 0)
    return root


def build_meeting_table_set(parent=None, name="MeetingSet"):
    M = _mats()
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    # round pedestal table
    disc(f"{name}Top", (0, TABLE_Y - 0.02, 0), TABLE_R, 0.04, M["black"], root, verts=64)
    ring(f"{name}TopEdge", (0, TABLE_Y - 0.02, 0), TABLE_R, 0.02, M["steel"], root)
    ring(f"{name}Glow", (0, TABLE_Y - 0.06, 0), TABLE_R - 0.08, 0.008, M["cyan"], root)
    tube(f"{name}Column", [(0, 0.04, 0), (0, TABLE_Y - 0.04, 0)], 0.06, M["steel"], root)
    disc(f"{name}Foot", (0, 0.02, 0), 0.32, 0.04, M["steel"], root, verts=48)
    # four chairs facing the table, slightly pulled out at different angles
    for k in range(4):
        a = math.radians(45 + 90 * k)
        r = TABLE_R + 0.28 + (0.06 if k % 2 else 0.0)
        ch = _chair(f"{name}Chair{k}", M, root)
        ch.location = P(r * math.sin(a), 0, r * math.cos(a))
        ch.rotation_euler = (0, 0, a + math.pi + math.radians(8 if k % 2 else -6))
    return root


def build_wall_rack(parent=None, name="WallRack", w=1.5, h=1.9, d=0.38, seed=4):
    M = _mats()
    BOOKS = [mat(n, c, 0.75) for n, c in (("RackBookNavy", "#1b2a45"), ("RackBookTeal", "#1d5c58"),
                                         ("RackBookPurple", "#3f2a5a"), ("RackBookGrey", "#34383d"), ("RackBookRed", "#6a2024"))]
    BOX = mat("RackBox", "#202227", 0.7)
    GOLD = mat("RackTrophy", "#c9a14a", 0.25, metal=1.0)
    LEAF = mat("RackLeaf", "#2b6236", 0.6)
    POT = mat("RackPot", "#17181b", 0.8)
    rng = random.Random(seed)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    zc = d / 2
    # frame: four uprights + five shelves
    for k, (sx, sz) in enumerate(((-1, 0), (1, 0), (-1, 1), (1, 1))):
        block(f"{name}Post{k}", (sx * (w / 2 - 0.02), h / 2, 0.02 + sz * (d - 0.04)), (0.03, h, 0.03), M["steel"], root)
    shelves = [0.06, 0.5, 0.94, 1.38, 1.82]
    for k, y in enumerate(shelves):
        block(f"{name}Shelf{k}", (0, y, zc), (w, 0.025, d), M["black"], root)
        if 0 < k:
            block(f"{name}ShelfGlow{k}", (0, y - 0.018, d - 0.02), (w - 0.1, 0.006, 0.008), M["cyan"], root)
    # contents
    parts = []
    # shelf 1: storage boxes
    for k, x in enumerate((-0.45, 0.0, 0.45)):
        block(f"{name}Box{k}", (x, 0.06 + 0.15, zc), (0.38, 0.28, d - 0.06), BOX, root, r=0.01)
    # shelf 2: books + speaker
    x = -w / 2 + 0.08
    for i in range(14):
        t = rng.uniform(0.025, 0.05)
        hh = rng.uniform(0.2, 0.3)
        parts.append(block(f"{name}Book{i}", (x + t / 2, 0.5 + 0.0125 + hh / 2, zc), (t, hh, rng.uniform(0.2, 0.26)), rng.choice(BOOKS), None, r=0.003))
        x += t + 0.003
    block(f"{name}Speaker", (0.45, 0.5 + 0.17, zc), (0.2, 0.32, 0.22), M["black"], root, r=0.015)
    disc(f"{name}SpeakerCone", (0.45, 0.5 + 0.14, zc + 0.112), 0.07, 0.01, M["steel"], root, axis="z")
    ring(f"{name}SpeakerGlow", (0.45, 0.5 + 0.14, zc + 0.115), 0.075, 0.004, M["cyan"], root, axis="z")
    # shelf 3: trophy + plant + lying books
    disc(f"{name}TrophyBase", (-0.45, 0.94 + 0.03, zc), 0.05, 0.04, M["black"], root)
    tube(f"{name}TrophyStem", [(-0.45, 0.99, zc), (-0.45, 1.08, zc)], 0.012, GOLD, root)
    bpy.ops.mesh.primitive_cone_add(radius1=0.03, radius2=0.07, depth=0.1, vertices=24)
    cup = bpy.context.active_object
    cup.name = f"{name}TrophyCup"
    cup.location = P(-0.45, 1.13, zc)
    bpy.ops.object.shade_smooth()
    cup.data.materials.append(GOLD)
    cup.parent = root
    disc(f"{name}PlantPot", (0.4, 0.94 + 0.08, zc), 0.07, 0.14, POT, root)
    for i in range(6):
        a = 2 * math.pi * i / 6
        tube(f"{name}PlantLeaf{i}", [(0.4, 1.1, zc), (0.4 + 0.08 * math.cos(a), 1.26, zc + 0.08 * math.sin(a))], 0.012, LEAF, root)
    for i in range(3):
        parts.append(block(f"{name}FlatBook{i}", (0.0, 0.94 + 0.02 + i * 0.035, zc), (0.26, 0.032, 0.2), rng.choice(BOOKS), None, r=0.003))
    # shelf 4: binders
    for i in range(8):
        parts.append(block(f"{name}Binder{i}", (-0.6 + i * 0.07, 1.38 + 0.0125 + 0.15, zc), (0.06, 0.3, 0.26), rng.choice(BOOKS), None, r=0.004))
    if parts:
        _join(parts, f"{name}Books", root)

    # preview-only glow (lights aren't exported)
    ld = bpy.data.lights.new(f"{name}GlowLight", "POINT")
    ld.color = (0.2, 0.9, 1.0)
    ld.energy = 12
    ld.shadow_soft_size = 0.4
    lo = bpy.data.objects.new(f"{name}GlowLight", ld)
    bpy.context.collection.objects.link(lo)
    lo.location = P(0, 1.2, d + 0.5)
    lo.parent = root
    return root


def build_meeting_room_preview(parent=None, name="MeetingRoomPreview"):
    """Preview only: table set + wall rack inside the approved glass room."""
    import glass_room  # noqa: E402

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    glass_room.build_glass_room(root, f"{name}Glass")
    t = build_meeting_table_set(root, f"{name}Table")
    t.location = P(0.25, glass_room.PLAT, 0.1)
    rack = build_wall_rack(root, f"{name}Rack")
    rack.location = P(-1.55, glass_room.PLAT, 0.0)
    rack.rotation_euler = (0, 0, math.radians(90))  # back against the left side, facing +X
    lt = bpy.data.lights.new(f"{name}RoomLight", "POINT")
    lt.color = (0.75, 0.9, 1.0)
    lt.energy = 50
    lo = bpy.data.objects.new(f"{name}RoomLight", lt)
    bpy.context.collection.objects.link(lo)
    lo.location = P(0.2, 2.2, 0.2)
    lo.parent = root
    return root

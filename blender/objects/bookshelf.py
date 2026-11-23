"""
Wall bookshelf for the loft workstation: three long dark-wood shelves on black
steel brackets, packed with books (upright rows, leaning books, flat stacks),
a few bookends and boxes, and a teal LED strip under each shelf lip.

    build_bookshelf(parent=None, name="Bookshelf", length=3.2, shelves=3) -> root empty

Coordinates are three.js style (Y up, books face +Z). The origin is on the wall
(z = 0), centred, at the bottom of the lowest brackets (lowest shelf top = 0.23 m up). All books are merged
into one mesh per shelf so hundreds of books stay cheap to draw.
"""

import os
import random
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P  # noqa: E402
from loft_room import block, mat  # noqa: E402

SHELF_D = 0.26  # depth from the wall
SHELF_T = 0.04  # plank thickness
GAP = 0.42  # vertical spacing between shelves
LIFT = 0.23  # lowest shelf top sits this far above the origin

BOOK_COLORS = [
    ("BookNavy", "#1b2a45"), ("BookTeal", "#1d5c58"), ("BookPurple", "#3f2a5a"),
    ("BookRed", "#6a2024"), ("BookMustard", "#8c6a24"), ("BookGrey", "#34383d"),
    ("BookCream", "#a89d86"), ("BookBlue", "#284f8c"), ("BookBlack", "#141517"),
    ("BookOlive", "#3f4a2a"),
]


def _join(objs, name, parent):
    """Merge many small objects into one mesh (keeps their materials)."""
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.convert(target="MESH")  # apply bevels before joining
    bpy.ops.object.join()
    o = bpy.context.active_object
    o.name = name
    o.parent = parent
    return o


def _book(rng, name, x, y0, M, parent, tilt=0.0, flat=False):
    """One book standing on y0 with its spine at the front. Returns (object, thickness)."""
    t = rng.uniform(0.022, 0.06)
    h = rng.uniform(0.17, 0.3)
    d = rng.uniform(0.15, min(0.22, SHELF_D - 0.03))
    col = rng.choice(M["books"])
    z = d / 2 + 0.015
    if flat:
        o = block(name, (x, y0 + t / 2, z), (h, t, d), col, None, r=0.003)
    else:
        o = block(name, (x, y0 + h / 2, z), (t, h, d), col, None, r=0.003)
        if tilt:
            # lean sideways, pivoting on the bottom corner
            o.rotation_euler = (0, tilt, 0)
            o.location.z = P(0, y0 + h / 2 * 0.98, 0)[2]
    parts = [o]
    # a lighter title band on some spines
    if not flat and not tilt and rng.random() < 0.22:
        band = block(name + "Band", (x, y0 + h * rng.uniform(0.6, 0.8), z + d / 2 + 0.001), (t * 0.86, 0.022, 0.003), M["band"], None)
        parts.append(band)
    return parts, t, h  # t = thickness: how far to step along a row or up a stack


def build_bookshelf(parent=None, name="Bookshelf", length=3.2, shelves=3):
    M = {
        "wood": mat("ShelfWood", "#3b2a1e", 0.6),
        "steel": mat("ShelfSteel", "#141517", 0.45, metal=0.8),
        "strip": mat("ShelfStrip", "#3fe0c8", emit="#3fe0c8", strength=6.0),
        "band": mat("BookBand", "#b89a5a", 0.4, metal=0.6),  # gold foil
        "box": mat("ShelfBox", "#26282b", 0.7),
        "bookend": mat("Bookend", "#5a5d61", 0.3, metal=0.9),
        "books": [mat(n, c, rough=0.75) for n, c in BOOK_COLORS],
    }
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    # everything hangs off an inner empty raised so the brackets' bottoms sit at y = 0
    body = bpy.data.objects.new(name + "Body", None)
    bpy.context.collection.objects.link(body)
    body.location = P(0, LIFT, 0)
    body.parent = root

    rng = random.Random(7)
    half = length / 2
    for s in range(shelves):
        y = s * GAP
        # plank + front lip + LED strip tucked under the lip
        block(f"Shelf{s}", (0, y - SHELF_T / 2, SHELF_D / 2), (length, SHELF_T, SHELF_D), M["wood"], body, r=0.004)
        block(f"ShelfStrip{s}", (0, y - SHELF_T - 0.006, SHELF_D - 0.03), (length - 0.1, 0.008, 0.012), M["strip"], body)
        # L brackets
        for k, bx in enumerate((-half + 0.25, 0.0, half - 0.25)):
            block(f"ShelfBracketV{s}_{k}", (bx, y - SHELF_T - 0.09, 0.012), (0.03, 0.18, 0.024), M["steel"], body)
            block(f"ShelfBracketH{s}_{k}", (bx, y - SHELF_T - 0.012, SHELF_D * 0.42), (0.03, 0.024, SHELF_D * 0.8), M["steel"], body)

        # fill the shelf left to right with runs of books, stacks and objects
        parts = []
        x = -half + 0.06
        end = half - 0.06
        i = 0
        while x < end - 0.05:
            r = rng.random()
            if r < 0.08 and x < end - 0.3:  # flat stack
                sx = x + 0.15
                yy = y
                for k in range(rng.randint(2, 4)):
                    p, th, _ = _book(rng, f"Book{s}_{i}", sx, yy, M, None, flat=True)
                    parts += p
                    yy += th
                    i += 1
                x += 0.34
            elif r < 0.13 and x < end - 0.25:  # storage box
                block(f"ShelfBox{s}_{i}", (x + 0.11, y + 0.09, SHELF_D / 2), (0.2, 0.18, SHELF_D - 0.06), M["box"], body, r=0.01)
                x += 0.25
            elif r < 0.18:  # gap with a leaning book
                p, th, h = _book(rng, f"Book{s}_{i}", x + 0.09, y, M, None, tilt=0.32)
                parts += p
                i += 1
                x += 0.2
            else:  # an upright run of books, ended by a bookend sometimes
                for k in range(rng.randint(4, 11)):
                    if x > end - 0.07:
                        break
                    p, th, _ = _book(rng, f"Book{s}_{i}", x + 0.03, y, M, None)
                    # nudge to sit flush: books are centred on x, so advance by thickness
                    for o in p:
                        o.location.x += th / 2 - 0.03
                    parts += p
                    x += th + 0.002
                    i += 1
                if rng.random() < 0.35 and x < end - 0.05:
                    block(f"Bookend{s}_{i}", (x + 0.02, y + 0.08, 0.1), (0.012, 0.16, 0.12), M["bookend"], body)
                    x += 0.05
                x += rng.uniform(0.02, 0.08)
        if parts:
            _join(parts, f"Books{s}", body)

    return root

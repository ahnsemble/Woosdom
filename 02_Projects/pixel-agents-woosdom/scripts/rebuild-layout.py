#!/usr/bin/env python3
"""
Ultra-dense office layout — maximum furniture packing.
Target: 120+ furniture items, 280+ tiles, 55-70% floor coverage per room.

Key fixes from previous iterations:
- Red/brown/gray chairs (row 12) are fully opaque — NOT invisible chair_simple (1,17)
- Continuous wall furniture strips along every wall
- 5 desks per row in large rooms
- Rug overlays under meeting/lounge areas
- Plants at every corner and intersection
"""
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
OUTPUT = PROJECT / "config" / "layout.json"
TSMAP_PATH = PROJECT / "config" / "tileset-map.json"

COLS, ROWS = 30, 34
VOID, FLOOR, WALL = 0, 1, 2

with open(TSMAP_PATH) as f:
    TSMAP = json.load(f)
PRESETS = TSMAP["furniturePresets"]
SINGLES = TSMAP["singleTileItems"]

# Floor tiles (all trans=0.0)
FLOOR_A = (3, 5)   # dark blue-gray
FLOOR_B = (3, 4)   # light gray
# Warm wood rug
RUG_A = (0, 6)     # warm wood
RUG_B = (1, 6)     # warm wood variant
# Walls
WALL_A = (2, 8)
WALL_B = (3, 8)

tiles = [VOID] * (COLS * ROWS)
overrides = {}

def idx(c, r): return r * COLS + c

def set_tile(c, r, ttype, sx=None, sy=None):
    if 0 <= c < COLS and 0 <= r < ROWS:
        tiles[idx(c, r)] = ttype
        if sx is not None and sy is not None:
            overrides[f"{c},{r}"] = {"sx": sx, "sy": sy}

def fill_floor(c1, c2, r1, r2, a=FLOOR_A, b=FLOOR_B):
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            t = a if (c + r) % 2 == 0 else b
            set_tile(c, r, FLOOR, t[0], t[1])

def fill_rug(c1, c2, r1, r2):
    """Override floor tiles with warm wood rug pattern."""
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            t = RUG_A if (c + r) % 2 == 0 else RUG_B
            overrides[f"{c},{r}"] = {"sx": t[0], "sy": t[1]}

def draw_walls(c1, c2, r1, r2):
    for c in range(c1, c2 + 1):
        w = WALL_A if c % 2 == 0 else WALL_B
        set_tile(c, r1, WALL, w[0], w[1])
        set_tile(c, r2, WALL, w[0], w[1])
    for r in range(r1 + 1, r2):
        w = WALL_A if r % 2 == 0 else WALL_B
        set_tile(c1, r, WALL, w[0], w[1])
        set_tile(c2, r, WALL, w[0], w[1])

def door(c, r):
    t = FLOOR_A if (c + r) % 2 == 0 else FLOOR_B
    set_tile(c, r, FLOOR, t[0], t[1])

# ================================================================
# FURNITURE HELPERS
# ================================================================
furniture = []
fid = [1]

def T(sx, sy, oc=0, orow=0):
    return {"sx": sx, "sy": sy, "offsetCol": oc, "offsetRow": orow}

def place_preset(key, col, row):
    p = PRESETS[key]
    furniture.append({"uid": f"f_{fid[0]}", "type": key,
                      "col": col, "row": row,
                      "tiles": list(p["tiles"]),
                      "blockedOffsets": list(p["blockedOffsets"])})
    fid[0] += 1

def place_single(key, col, row):
    item = SINGLES[key]
    blocked = [[0, 0]] if item["blocked"] else []
    furniture.append({"uid": f"f_{fid[0]}", "type": key,
                      "col": col, "row": row,
                      "tiles": [{"sx": item["sx"], "sy": item["sy"],
                                 "offsetCol": 0, "offsetRow": 0}],
                      "blockedOffsets": blocked})
    fid[0] += 1

def place_custom(name, col, row, tile_list, blocked=None):
    furniture.append({"uid": f"f_{fid[0]}", "type": name,
                      "col": col, "row": row,
                      "tiles": tile_list,
                      "blockedOffsets": blocked or [[t["offsetCol"], t["offsetRow"]] for t in tile_list]})
    fid[0] += 1

# ================================================================
# CUSTOM FURNITURE — VISIBLE CHAIRS (row 12 = 0% transparent)
# ================================================================

def place_desk_wide_red(col, row):
    """2x3: monitor-desk-red_chair."""
    place_custom("desk_wide_red", col, row, [
        T(4, 20, 0, 0), T(4, 20, 1, 0),
        T(2, 0, 0, 1),  T(5, 0, 1, 1),
        T(0, 12, 0, 2), T(0, 12, 1, 2),
    ], [[0,0], [1,0], [0,1], [1,1]])

def place_desk_wide_brown(col, row):
    """2x3: monitor-desk-brown_chair."""
    place_custom("desk_wide_brown", col, row, [
        T(4, 20, 0, 0), T(4, 20, 1, 0),
        T(2, 0, 0, 1),  T(5, 0, 1, 1),
        T(4, 12, 0, 2), T(4, 12, 1, 2),
    ], [[0,0], [1,0], [0,1], [1,1]])

def place_desk_wide_gray(col, row):
    """2x3: monitor-desk-gray_chair."""
    place_custom("desk_wide_gray", col, row, [
        T(4, 20, 0, 0), T(4, 20, 1, 0),
        T(2, 0, 0, 1),  T(5, 0, 1, 1),
        T(2, 12, 0, 2), T(2, 12, 1, 2),
    ], [[0,0], [1,0], [0,1], [1,1]])

def place_desk_narrow_red(col, row):
    """1x3: monitor-desk-red_chair."""
    place_custom("desk_narrow_red", col, row, [
        T(4, 20, 0, 0),
        T(2, 0, 0, 1),
        T(0, 12, 0, 2),
    ], [[0,0], [0,1]])

def place_bookshelf_brown(col, row):
    """2x2 brown bookshelf with colorful books."""
    place_custom("bookshelf_brown", col, row, [
        T(8, 8, 0, 0),  T(9, 8, 1, 0),
        T(8, 9, 0, 1),  T(9, 9, 1, 1),
    ], [[0,0], [1,0], [0,1], [1,1]])

def place_bookshelf_gray(col, row):
    """2x2 gray bookshelf."""
    place_custom("bookshelf_gray", col, row, [
        T(11, 8, 0, 0), T(12, 8, 1, 0),
        T(11, 9, 0, 1), T(12, 9, 1, 1),
    ], [[0,0], [1,0], [0,1], [1,1]])

def place_filing_cabinet(col, row):
    """2x2 filing cabinet."""
    place_custom("filing_cabinet", col, row, [
        T(6, 10, 0, 0), T(7, 10, 1, 0),
        T(6, 11, 0, 1), T(7, 11, 1, 1),
    ], [[0,0], [1,0], [0,1], [1,1]])

def place_presentation_board(col, row):
    """2x2 presentation board / chart."""
    place_custom("presentation", col, row, [
        T(2, 26, 0, 0), T(3, 26, 1, 0),
        T(2, 27, 0, 1), T(3, 27, 1, 1),
    ], [[0,0], [1,0], [0,1], [1,1]])

def place_coffee_table(col, row):
    """2x1 small table."""
    place_custom("coffee_table", col, row, [
        T(2, 0, 0, 0), T(5, 0, 1, 0),
    ], [[0,0], [1,0]])

# ================================================================
# BUILD ROOMS (same structure, tighter furniture)
# ================================================================

# === BRAIN HQ (Meeting Room) — top center ===
draw_walls(7, 22, 1, 8)
fill_floor(8, 21, 2, 7)     # 14x6 inner
door(14, 8); door(15, 8)

# === HALLWAY A ===
fill_floor(1, 28, 9, 10)

# === CC ROOM ===
draw_walls(1, 18, 11, 22)
fill_floor(2, 17, 12, 21)   # 16x10 inner
door(9, 11); door(10, 11)

# === CODEX ROOM ===
draw_walls(20, 28, 11, 22)
fill_floor(21, 27, 12, 21)  # 7x10 inner
door(20, 16); door(20, 17)

# === VERTICAL HALLWAY ===
fill_floor(19, 19, 9, 24)

# === HALLWAY B ===
fill_floor(1, 28, 23, 24)

# === AG ROOM ===
draw_walls(1, 14, 25, 33)
fill_floor(2, 13, 26, 32)   # 12x7 inner
door(7, 25); door(8, 25)

# === BRAIN OFFICE ===
draw_walls(16, 28, 25, 33)
fill_floor(17, 27, 26, 32)  # 11x7 inner
door(16, 29); door(16, 30)

# === VERTICAL HALLWAY B ===
fill_floor(15, 15, 23, 33)

# ================================================================
# RUG OVERLAYS (warm wood under meeting/lounge areas)
# ================================================================
fill_rug(11, 15, 3, 6)    # Brain HQ meeting table area
fill_rug(22, 26, 18, 20)  # Codex lounge
fill_rug(17, 20, 31, 32)  # Brain Office sofa

# ================================================================
# FURNITURE — ULTRA DENSE PLACEMENT
# ================================================================

# ============================================================
# BRAIN HQ — Meeting Room (inner: cols 8-21, rows 2-7)
# 14x6 = 84 floor tiles, target ~60 tiles covered (71%)
# ============================================================

# North wall strip (rows 2-3) — CONTINUOUS furniture
place_bookshelf_brown(8, 2)            # (8-9, 2-3)
place_bookshelf_gray(10, 2)            # (10-11, 2-3)
place_single("clock_wall", 12, 2)
place_single("picture_small", 13, 2)
place_preset("whiteboard", 14, 2)      # (14, 2-3)
place_single("picture_small", 15, 2)
place_single("picture_small", 16, 2)
place_presentation_board(17, 2)        # (17-18, 2-3)
place_single("plant_small", 19, 2)
place_bookshelf_brown(20, 2)           # (20-21, 2-3)

# Row 3: chairs below single items + plant
place_single("chair_red", 12, 3)      # north of table
place_single("chair_red", 13, 3)
place_single("chair_red", 15, 3)
place_single("chair_red", 16, 3)
place_single("plant_fern", 19, 3)

# West side equipment (rows 4-5)
place_filing_cabinet(8, 4)             # (8-9, 4-5)
place_single("plant_potted", 10, 4)
place_single("plant_large", 10, 5)

# Meeting table center
place_preset("meeting_table_3x2", 12, 4)  # (12-14, 4-5)

# Chairs flanking table
place_single("chair_red", 11, 4)      # west
place_single("chair_red", 11, 5)
place_single("chair_red", 15, 4)      # east
place_single("chair_red", 15, 5)

# East side equipment (rows 4-5)
place_preset("copier", 16, 4)         # (16-17, 4-5)
place_single("plant_potted", 18, 4)
place_single("box_single", 18, 5)
place_preset("bookshelf_tall", 21, 4) # (21, 4-5)

# Row 6: south chairs
place_single("chair_red", 12, 6)
place_single("chair_red", 13, 6)
place_single("chair_red", 14, 6)

# Row 7: bottom decorations
place_single("plant_large", 8, 7)
place_single("box_single", 9, 7)
place_single("plant_fern", 18, 7)
place_single("box_stack", 20, 7)
place_single("plant_potted", 21, 7)

# ============================================================
# CC ROOM — Main Workspace (inner: cols 2-17, rows 12-21)
# 16x10 = 160 floor tiles, target ~115 tiles covered (72%)
# ============================================================

# North wall strip (rows 12-13) — CONTINUOUS 2x2 units
place_bookshelf_brown(2, 12)           # (2-3, 12-13)
place_bookshelf_gray(4, 12)            # (4-5, 12-13)
place_filing_cabinet(6, 12)            # (6-7, 12-13)
place_bookshelf_brown(8, 12)           # (8-9, 12-13)
place_preset("copier", 10, 12)        # (10-11, 12-13)
place_filing_cabinet(12, 12)           # (12-13, 12-13)
place_bookshelf_gray(14, 12)           # (14-15, 12-13)
place_single("plant_potted", 16, 12)
place_single("plant_fern", 17, 12)
# Fill row 13 under single-tile items
place_single("clock_wall", 16, 13)
place_single("picture_small", 17, 13)

# West wall equipment (col 2, rows 14-20)
place_preset("vending_machine", 2, 14)  # (2, 14-15)
place_single("plant_potted", 2, 16)
place_preset("water_cooler", 2, 18)    # (2, 18-19)
place_single("plant_large", 2, 20)

# East wall equipment (col 17, rows 14-20)
place_preset("water_cooler", 17, 14)   # (17, 14-15)
place_single("clock_wall", 17, 16)
place_preset("whiteboard", 17, 18)     # (17, 18-19)
place_single("plant_fern", 17, 20)

# DESK ROW 1 (rows 14-16) — 5 wide desks
place_desk_wide_red(3, 14)             # (3-4, 14-16)
place_desk_wide_red(6, 14)             # (6-7, 14-16)
place_desk_wide_red(9, 14)             # (9-10, 14-16)
place_desk_wide_red(12, 14)            # (12-13, 14-16)
place_desk_wide_gray(15, 14)           # (15-16, 14-16)

# Row 17: walking path (sparse items)
place_single("chair_brown", 5, 17)
place_single("chair_brown", 11, 17)

# DESK ROW 2 (rows 18-20) — 5 wide desks
place_desk_wide_brown(3, 18)           # (3-4, 18-20)
place_desk_wide_brown(6, 18)           # (6-7, 18-20)
place_desk_wide_brown(9, 18)           # (9-10, 18-20)
place_desk_wide_brown(12, 18)          # (12-13, 18-20)
place_desk_wide_gray(15, 18)           # (15-16, 18-20)

# Row 21: south wall items
place_single("plant_large", 2, 21)
place_single("box_single", 3, 21)
place_single("box_stack", 4, 21)
place_single("plant_fern", 7, 21)
place_single("box_single", 10, 21)
place_single("plant_small", 13, 21)
place_single("picture_small", 15, 21)
place_single("plant_potted", 17, 21)

# ============================================================
# CODEX ROOM — Server/Dev Room (inner: cols 21-27, rows 12-21)
# 7x10 = 70 floor tiles, target ~42 tiles covered (60%)
# ============================================================

# North wall strip (rows 12-13)
place_preset("server_rack", 21, 12)    # (21, 12-13)
place_preset("server_rack", 22, 12)    # (22, 12-13)
place_single("picture_small", 23, 12)
place_single("clock_wall", 24, 12)
place_bookshelf_brown(25, 12)          # (25-26, 12-13)
place_single("plant_potted", 27, 12)
# Row 13 extras
place_single("plant_small", 23, 13)
place_single("box_single", 24, 13)
place_single("plant_fern", 27, 13)

# West wall items (col 21)
place_preset("bookshelf_tall", 21, 14) # (21, 14-15)
place_single("plant_small", 21, 16)

# East wall equipment (col 27, rows 14-20)
place_preset("bookshelf_tall", 27, 14) # (27, 14-15)
place_preset("vending_machine", 27, 16)# (27, 16-17)
place_preset("vending_machine", 27, 18)# (27, 18-19)
place_preset("water_cooler", 27, 20)   # (27, 20-21)

# DESK ROW (rows 14-16) — 2 wide desks
place_desk_wide_brown(22, 14)          # (22-23, 14-16)
place_desk_wide_brown(25, 14)          # (25-26, 14-16)

# Row 17: walking
place_single("chair_brown", 24, 17)

# Lounge area (rows 18-20) — rug underneath
place_single("plant_large", 21, 18)
place_preset("sofa_2seat", 22, 18)     # (22-23, 18-19)
place_single("chair_brown", 24, 19)    # lounge seat
place_coffee_table(25, 18)             # (25-26, 18)
place_single("chair_brown", 24, 20)    # lounge seat

# South wall (row 21)
place_single("plant_fern", 21, 21)
place_single("box_single", 22, 21)
place_single("box_stack", 24, 21)
place_single("plant_potted", 26, 21)

# ============================================================
# AG ROOM — Scout/Research (inner: cols 2-13, rows 26-32)
# 12x7 = 84 floor tiles, target ~55 tiles covered (65%)
# ============================================================

# North wall strip (rows 26-27) — CONTINUOUS
place_bookshelf_brown(2, 26)           # (2-3, 26-27)
place_preset("large_landscape", 4, 26) # (4-6, 26-27)
place_single("clock_wall", 7, 26)
place_single("picture_small", 8, 26)
place_preset("whiteboard", 9, 26)      # (9, 26-27)
place_presentation_board(10, 26)       # (10-11, 26-27)
place_single("plant_potted", 12, 26)
place_single("plant_fern", 13, 26)
# Row 27 extras (below single items)
place_single("box_single", 7, 27)
place_single("picture_small", 8, 27)
place_single("box_stack", 12, 27)
place_single("plant_small", 13, 27)

# West wall items (col 2, rows 28-31)
place_preset("bookshelf_tall", 2, 28)  # (2, 28-29)
place_single("plant_potted", 2, 30)
place_single("plant_small", 2, 31)

# East wall items (col 13, rows 28-31)
place_filing_cabinet(12, 28)           # (12-13, 28-29)
place_single("box_single", 12, 30)
place_single("plant_large", 13, 30)

# DESK ROW (rows 28-30) — 3 wide desks
place_desk_wide_red(3, 28)             # (3-4, 28-30)
place_desk_wide_red(6, 28)             # (6-7, 28-30)
place_desk_wide_red(9, 28)             # (9-10, 28-30)

# Row 31: walking + extras
place_single("chair_red", 5, 31)
place_single("chair_red", 8, 31)

# Row 32: south wall items
place_single("plant_fern", 3, 32)
place_single("box_stack", 5, 32)
place_single("box_single", 7, 32)
place_single("plant_potted", 9, 32)
place_single("plant_small", 11, 32)
place_single("plant_large", 13, 32)

# ============================================================
# BRAIN OFFICE — Command Center (inner: cols 17-27, rows 26-32)
# 11x7 = 77 floor tiles, target ~55 tiles covered (71%)
# ============================================================

# North wall strip (rows 26-27) — CONTINUOUS
place_single("plant_potted", 17, 26)
place_preset("whiteboard", 18, 26)     # (18, 26-27)
place_preset("large_landscape", 19, 26)# (19-21, 26-27)
place_single("clock_wall", 22, 26)
place_single("picture_small", 23, 26)
place_bookshelf_brown(24, 26)          # (24-25, 26-27)
place_single("plant_fern", 26, 26)
place_preset("bookshelf_tall", 27, 26) # (27, 26-27)
# Row 27 extras
place_single("plant_small", 17, 27)
place_single("box_single", 22, 27)
place_single("picture_small", 23, 27)
place_single("plant_small", 26, 27)

# DESK ROW (rows 28-30) — 2 wide desks
place_desk_wide_brown(18, 28)          # (18-19, 28-30)
place_desk_wide_brown(21, 28)          # (21-22, 28-30)

# Equipment block (cols 24-27, rows 28-30)
place_preset("copier", 24, 28)        # (24-25, 28-29)
place_preset("server_rack", 26, 28)   # (26, 28-29)
place_preset("vending_machine", 27, 28)# (27, 28-29)
place_filing_cabinet(24, 30)           # (24-25, 30-31)
place_preset("water_cooler", 26, 30)  # (26, 30-31)
place_single("plant_large", 27, 30)

# Left side items (col 17, rows 28-30)
place_preset("bookshelf_tall", 17, 28) # (17, 28-29)
place_single("plant_potted", 17, 30)

# Walkway col 20 and 23 are free for agents

# Sofa area (rows 31-32) — rug underneath
place_preset("sofa_2seat", 17, 31)     # (17-18, 31-32)
place_single("plant_large", 19, 32)
place_coffee_table(20, 32)             # (20-21, 32)
place_single("box_single", 22, 32)
place_single("box_stack", 23, 32)
place_single("plant_potted", 27, 32)

# ============================================================
# HALLWAY DECORATIONS — Plants everywhere
# ============================================================

# Hallway A (rows 9-10)
place_single("plant_potted", 1, 9)
place_single("plant_large", 5, 9)
place_single("plant_fern", 10, 9)
place_single("plant_small", 15, 9)
place_single("plant_potted", 24, 9)
place_single("plant_large", 28, 9)
place_single("plant_fern", 3, 10)
place_single("box_single", 8, 10)
place_single("plant_potted", 13, 10)
place_single("plant_small", 18, 10)
place_single("box_stack", 22, 10)
place_single("plant_fern", 26, 10)

# Hallway B (rows 23-24)
place_single("plant_potted", 1, 23)
place_single("plant_large", 6, 23)
place_single("plant_fern", 12, 23)
place_single("plant_small", 18, 23)
place_single("plant_potted", 25, 23)
place_single("plant_large", 28, 24)
place_single("box_single", 3, 24)
place_single("plant_fern", 9, 24)
place_single("plant_small", 16, 24)
place_single("box_stack", 21, 24)
place_single("plant_potted", 27, 24)

# Vertical hallway (col 19)
place_single("plant_potted", 19, 11)
place_single("plant_fern", 19, 22)

# Vertical hallway B (col 15)
place_single("plant_potted", 15, 25)
place_single("plant_fern", 15, 33)

# ================================================================
# ROOMS, HALLWAY, SEATS, AGENTS
# ================================================================

rooms = [
    {"id": "brain", "label": "Brain HQ", "team": "brain",
     "minCol": 8, "maxCol": 21, "minRow": 2, "maxRow": 7,
     "floorColor": "#8ca0b0",
     "floorPattern": [{"sx": 3, "sy": 5}, {"sx": 3, "sy": 4}]},
    {"id": "cc", "label": "CC Room", "team": "cc",
     "minCol": 2, "maxCol": 17, "minRow": 12, "maxRow": 21,
     "floorColor": "#8ca0b0",
     "floorPattern": [{"sx": 3, "sy": 5}, {"sx": 3, "sy": 4}]},
    {"id": "codex", "label": "Codex Room", "team": "codex",
     "minCol": 21, "maxCol": 27, "minRow": 12, "maxRow": 21,
     "floorColor": "#8ca0b0",
     "floorPattern": [{"sx": 3, "sy": 5}, {"sx": 3, "sy": 4}]},
    {"id": "ag", "label": "AG Room", "team": "ag",
     "minCol": 2, "maxCol": 13, "minRow": 26, "maxRow": 32,
     "floorColor": "#8ca0b0",
     "floorPattern": [{"sx": 3, "sy": 5}, {"sx": 3, "sy": 4}]},
]

hallway = {
    "minCol": 1, "maxCol": 28, "minRow": 9, "maxRow": 24,
    "floorColor": "#8ca0b0",
    "floorPattern": [{"sx": 3, "sy": 5}, {"sx": 3, "sy": 4}],
}

# Seats — chair row = desk.row + 2 (opaque chairs, NOT blocked)
seats = [
    # CC: 5 desks row1 (chair at 14+2=16), 5 desks row2 (chair at 18+2=20)
    {"id": "cc-seat-0", "seatCol": 3,  "seatRow": 16, "facingDir": 1},
    {"id": "cc-seat-1", "seatCol": 6,  "seatRow": 16, "facingDir": 1},
    {"id": "cc-seat-2", "seatCol": 9,  "seatRow": 16, "facingDir": 1},
    {"id": "cc-seat-3", "seatCol": 3,  "seatRow": 20, "facingDir": 1},
    {"id": "cc-seat-4", "seatCol": 6,  "seatRow": 20, "facingDir": 1},

    # Codex: 2 desks (chair at 14+2=16), 2 lounge chairs
    {"id": "codex-seat-0", "seatCol": 22, "seatRow": 16, "facingDir": 1},
    {"id": "codex-seat-1", "seatCol": 25, "seatRow": 16, "facingDir": 1},
    {"id": "codex-seat-2", "seatCol": 24, "seatRow": 19, "facingDir": 3},
    {"id": "codex-seat-3", "seatCol": 24, "seatRow": 20, "facingDir": 3},

    # AG: 3 desks (chair at 28+2=30), 1 standing
    {"id": "ag-seat-0", "seatCol": 3,  "seatRow": 30, "facingDir": 1},
    {"id": "ag-seat-1", "seatCol": 6,  "seatRow": 30, "facingDir": 1},
    {"id": "ag-seat-2", "seatCol": 9,  "seatRow": 30, "facingDir": 1},
    {"id": "ag-seat-3", "seatCol": 5,  "seatRow": 31, "facingDir": 0},

    # Brain: at meeting table
    {"id": "brain-seat-0", "seatCol": 14, "seatRow": 6, "facingDir": 1},
]

agents = [
    # sprites.png = 384x256px → 4x2 blocks (96x128px each) = 8 sprite slots
    # spriteRow must be 0-1 only. Agents 8-13 reuse row 0-1 (distinguished by name label)
    {"id": 0,  "role": "foreman",      "displayName": "Foreman",      "team": "cc",    "room": "cc",    "seatId": "cc-seat-0",    "spriteRow": 0, "spriteCol": 0},
    {"id": 1,  "role": "engineer",     "displayName": "Engineer",     "team": "cc",    "room": "cc",    "seatId": "cc-seat-1",    "spriteRow": 0, "spriteCol": 1},
    {"id": 2,  "role": "critic",       "displayName": "Critic",       "team": "cc",    "room": "cc",    "seatId": "cc-seat-2",    "spriteRow": 0, "spriteCol": 2},
    {"id": 3,  "role": "gitops",       "displayName": "GitOps",       "team": "cc",    "room": "cc",    "seatId": "cc-seat-3",    "spriteRow": 0, "spriteCol": 3},
    {"id": 4,  "role": "vault_keeper", "displayName": "VaultKeeper",  "team": "cc",    "room": "cc",    "seatId": "cc-seat-4",    "spriteRow": 1, "spriteCol": 0},
    {"id": 5,  "role": "compute_lead", "displayName": "Compute Lead", "team": "codex", "room": "codex", "seatId": "codex-seat-0", "spriteRow": 1, "spriteCol": 1},
    {"id": 6,  "role": "quant",        "displayName": "Quant",        "team": "codex", "room": "codex", "seatId": "codex-seat-1", "spriteRow": 1, "spriteCol": 2},
    {"id": 7,  "role": "backtester",   "displayName": "Backtester",   "team": "codex", "room": "codex", "seatId": "codex-seat-2", "spriteRow": 1, "spriteCol": 3},
    {"id": 8,  "role": "builder",      "displayName": "Builder",      "team": "codex", "room": "codex", "seatId": "codex-seat-3", "spriteRow": 0, "spriteCol": 0},
    {"id": 9,  "role": "scout_lead",   "displayName": "Scout Lead",   "team": "ag",    "room": "ag",    "seatId": "ag-seat-0",    "spriteRow": 0, "spriteCol": 1},
    {"id": 10, "role": "web_scout",    "displayName": "Web Scout",    "team": "ag",    "room": "ag",    "seatId": "ag-seat-1",    "spriteRow": 0, "spriteCol": 2},
    {"id": 11, "role": "architect",    "displayName": "Architect",    "team": "ag",    "room": "ag",    "seatId": "ag-seat-2",    "spriteRow": 0, "spriteCol": 3},
    {"id": 12, "role": "experiment",   "displayName": "Experiment",   "team": "ag",    "room": "ag",    "seatId": "ag-seat-3",    "spriteRow": 1, "spriteCol": 0},
    {"id": 13, "role": "brain",        "displayName": "Brain",        "team": "brain", "room": "brain", "seatId": "brain-seat-0", "spriteRow": 1, "spriteCol": 1},
]

# ================================================================
# OUTPUT
# ================================================================
layout = {
    "version": 2,
    "cols": COLS, "rows": ROWS,
    "tiles": tiles,
    "tileOverrides": overrides,
    "rooms": rooms,
    "hallway": hallway,
    "wallTiles": {"tiles": [{"sx": 2, "sy": 8}, {"sx": 3, "sy": 8}]},
    "furniture": furniture,
    "seats": seats,
    "agents": agents,
}

with open(OUTPUT, "w") as f:
    json.dump(layout, f, indent=2)

# Stats
from collections import Counter
tc = Counter(tiles)
total_floor = tc[FLOOR]
total_furn_tiles = sum(len(f["tiles"]) for f in furniture)

print(f"Layout: {COLS}x{ROWS}")
print(f"Tiles: {tc[VOID]} void, {tc[FLOOR]} floor, {tc[WALL]} wall")
print(f"Furniture: {len(furniture)} items, {total_furn_tiles} tiles")
print(f"Coverage: {total_furn_tiles}/{total_floor} = {total_furn_tiles/total_floor*100:.0f}%")
print(f"Overrides: {len(overrides)} (incl. {sum(1 for k in overrides if RUG_A[0] <= overrides[k].get('sx', -1) <= RUG_B[0])} rug tiles)")
print(f"Seats: {len(seats)}, Agents: {len(agents)}")
print(f"Unique furniture types: {len(set(f['type'] for f in furniture))}")
print(f"Written to {OUTPUT}")

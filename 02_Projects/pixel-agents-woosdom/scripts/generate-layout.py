#!/usr/bin/env python3
"""
layout.json 생성 스크립트.
2x2 균등 그리드 레이아웃 + 다중 타일 가구 + 14 에이전트.

그리드: 52 cols x 35 rows
┌───────────────┬───────────────┐
│ CC Room       │ Codex Room    │ row 0: wall
│ (cols 1-23,   │ (cols 27-50,  │ rows 1-14: rooms
│  rows 1-14)   │  rows 1-14)   │
├───────────────┼───────────────┤ rows 15-17: hallway
│   Hallway + cross corridor    │
├───────────────┼───────────────┤
│ AG Room       │ Brain HQ      │ rows 18-31: rooms
│ (cols 1-23,   │ (cols 27-50,  │ row 32: wall
│  rows 18-31)  │  rows 18-31)  │
└───────────────┴───────────────┘
"""

import json
import os

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config", "layout.json"
)

COLS = 52
ROWS = 35

# Tile types
VOID = 0
FLOOR = 1
WALL = 2

# Direction
DOWN = 0
UP = 1
RIGHT = 2
LEFT = 3


def build_tile_grid():
    """Build flat tile array."""
    grid = [VOID] * (COLS * ROWS)

    def set_tile(c, r, t):
        if 0 <= c < COLS and 0 <= r < ROWS:
            grid[r * COLS + c] = t

    def fill_rect(c1, r1, c2, r2, t):
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                set_tile(c, r, t)

    # Rooms (floor)
    rooms = [
        (1, 1, 23, 14),    # CC
        (27, 1, 50, 14),   # Codex
        (1, 18, 23, 31),   # AG
        (27, 18, 50, 31),  # Brain HQ
    ]
    for c1, r1, c2, r2 in rooms:
        fill_rect(c1, r1, c2, r2, FLOOR)

    # Hallways
    fill_rect(1, 15, 50, 17, FLOOR)    # horizontal hallway
    fill_rect(24, 1, 26, 31, FLOOR)    # vertical corridor (connects all rooms)

    # Walls — outer border
    # Top wall (row 0)
    fill_rect(0, 0, 51, 0, WALL)
    # Bottom wall (row 32+)
    fill_rect(0, 32, 51, 34, WALL)
    # Left wall (col 0)
    for r in range(ROWS):
        set_tile(0, r, WALL)
    # Right wall (col 51)
    for r in range(ROWS):
        set_tile(51, r, WALL)

    # Inner walls between CC and Codex (but corridor passes through)
    # No wall between rooms and corridor (open sides)

    return grid


def build_rooms():
    return [
        {
            "id": "cc",
            "label": "CC Room",
            "team": "cc",
            "minCol": 1, "maxCol": 23,
            "minRow": 1, "maxRow": 14,
            "floorColor": "#c4a96a",
            "floorPattern": [{"sx": 0, "sy": 4}, {"sx": 1, "sy": 4}],
        },
        {
            "id": "codex",
            "label": "Codex Room",
            "team": "codex",
            "minCol": 27, "maxCol": 50,
            "minRow": 1, "maxRow": 14,
            "floorColor": "#8fa4b5",
            "floorPattern": [{"sx": 8, "sy": 3}, {"sx": 9, "sy": 3}],
        },
        {
            "id": "ag",
            "label": "AG Room",
            "team": "ag",
            "minCol": 1, "maxCol": 23,
            "minRow": 18, "maxRow": 31,
            "floorColor": "#9aab8e",
            "floorPattern": [{"sx": 3, "sy": 5}, {"sx": 6, "sy": 5}],
        },
        {
            "id": "brain",
            "label": "Brain HQ",
            "team": "brain",
            "minCol": 27, "maxCol": 50,
            "minRow": 18, "maxRow": 31,
            "floorColor": "#a0abb8",
            "floorPattern": [{"sx": 3, "sy": 4}, {"sx": 6, "sy": 4}],
        },
    ]


def build_hallway():
    return {
        "minCol": 1, "maxCol": 50,
        "minRow": 15, "maxRow": 17,
        "floorColor": "#b3b3a8",
        "floorPattern": [{"sx": 5, "sy": 5}, {"sx": 6, "sy": 5}],
    }


# UID counter
_uid_counter = 0
def next_uid(prefix="f"):
    global _uid_counter
    _uid_counter += 1
    return f"{prefix}_{_uid_counter}"


def desk_with_monitor(col, row):
    """모니터+책상+의자 세트 (1x3). row 0=monitor, 1=desk, 2=chair"""
    uid = next_uid("desk")
    return {
        "uid": uid,
        "type": "desk_with_monitor",
        "col": col,
        "row": row,
        "tiles": [
            {"sx": 4, "sy": 20, "offsetCol": 0, "offsetRow": 0},  # monitor
            {"sx": 2, "sy": 0,  "offsetCol": 0, "offsetRow": 1},  # desk
            {"sx": 1, "sy": 17, "offsetCol": 0, "offsetRow": 2},  # chair
        ],
        "blockedOffsets": [[0, 0], [0, 1]],
    }


def wide_desk(col, row):
    """2칸 넓은 책상 + 모니터 2개 + 의자 2개 (2x3)"""
    uid = next_uid("wdesk")
    return {
        "uid": uid,
        "type": "wide_desk_with_monitor",
        "col": col,
        "row": row,
        "tiles": [
            {"sx": 4, "sy": 20, "offsetCol": 0, "offsetRow": 0},
            {"sx": 4, "sy": 20, "offsetCol": 1, "offsetRow": 0},
            {"sx": 2, "sy": 0,  "offsetCol": 0, "offsetRow": 1},
            {"sx": 5, "sy": 0,  "offsetCol": 1, "offsetRow": 1},
            {"sx": 1, "sy": 17, "offsetCol": 0, "offsetRow": 2},
            {"sx": 1, "sy": 17, "offsetCol": 1, "offsetRow": 2},
        ],
        "blockedOffsets": [[0, 0], [1, 0], [0, 1], [1, 1]],
    }


def bookshelf_tall(col, row):
    uid = next_uid("bshelf")
    return {
        "uid": uid,
        "type": "bookshelf_tall",
        "col": col,
        "row": row,
        "tiles": [
            {"sx": 10, "sy": 8, "offsetCol": 0, "offsetRow": 0},
            {"sx": 10, "sy": 9, "offsetCol": 0, "offsetRow": 1},
        ],
        "blockedOffsets": [[0, 0], [0, 1]],
    }


def whiteboard(col, row):
    uid = next_uid("wb")
    return {
        "uid": uid,
        "type": "whiteboard",
        "col": col,
        "row": row,
        "tiles": [
            {"sx": 2, "sy": 18, "offsetCol": 0, "offsetRow": 0},
            {"sx": 2, "sy": 19, "offsetCol": 0, "offsetRow": 1},
        ],
        "blockedOffsets": [[0, 0], [0, 1]],
    }


def server_rack(col, row):
    uid = next_uid("srv")
    return {
        "uid": uid,
        "type": "server_rack",
        "col": col,
        "row": row,
        "tiles": [
            {"sx": 14, "sy": 10, "offsetCol": 0, "offsetRow": 0},
            {"sx": 14, "sy": 11, "offsetCol": 0, "offsetRow": 1},
        ],
        "blockedOffsets": [[0, 0], [0, 1]],
    }


def meeting_table(col, row):
    uid = next_uid("mtg")
    return {
        "uid": uid,
        "type": "meeting_table_3x2",
        "col": col,
        "row": row,
        "tiles": [
            {"sx": 2, "sy": 0, "offsetCol": 0, "offsetRow": 0},
            {"sx": 5, "sy": 0, "offsetCol": 1, "offsetRow": 0},
            {"sx": 2, "sy": 0, "offsetCol": 2, "offsetRow": 0},
            {"sx": 2, "sy": 0, "offsetCol": 0, "offsetRow": 1},
            {"sx": 5, "sy": 0, "offsetCol": 1, "offsetRow": 1},
            {"sx": 2, "sy": 0, "offsetCol": 2, "offsetRow": 1},
        ],
        "blockedOffsets": [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1]],
    }


def single_tile(col, row, sx, sy, ftype, blocked=True):
    uid = next_uid(ftype)
    return {
        "uid": uid,
        "type": ftype,
        "col": col,
        "row": row,
        "tiles": [{"sx": sx, "sy": sy, "offsetCol": 0, "offsetRow": 0}],
        "blockedOffsets": [[0, 0]] if blocked else [],
    }


def build_furniture():
    furniture = []

    # === CC Room (cols 1-23, rows 1-14) — 5 desks ===
    # Row of 4 desks (monitor at row 2, desk at row 3, chair at row 4)
    furniture.append(desk_with_monitor(3, 2))
    furniture.append(desk_with_monitor(6, 2))
    furniture.append(desk_with_monitor(9, 2))
    furniture.append(desk_with_monitor(12, 2))
    # 5th desk (second row)
    furniture.append(desk_with_monitor(7, 8))
    # Decorations
    furniture.append(bookshelf_tall(1, 1))
    furniture.append(whiteboard(15, 1))
    furniture.append(single_tile(22, 1, 0, 22, "clock"))     # clock
    furniture.append(single_tile(20, 13, 5, 28, "plant"))    # plant
    furniture.append(single_tile(22, 13, 5, 28, "plant"))    # plant

    # === Codex Room (cols 27-50, rows 1-14) — 4 desks ===
    furniture.append(desk_with_monitor(29, 2))
    furniture.append(desk_with_monitor(32, 2))
    furniture.append(desk_with_monitor(35, 2))
    furniture.append(desk_with_monitor(32, 8))
    # Servers
    furniture.append(server_rack(27, 1))
    furniture.append(server_rack(28, 1))
    furniture.append(server_rack(49, 1))
    furniture.append(server_rack(50, 1))
    # Decorations
    furniture.append(single_tile(40, 1, 4, 20, "monitor"))   # extra monitor
    furniture.append(single_tile(41, 1, 4, 20, "monitor"))

    # === AG Room (cols 1-23, rows 18-31) — 4 desks ===
    furniture.append(desk_with_monitor(3, 19))
    furniture.append(desk_with_monitor(6, 19))
    furniture.append(desk_with_monitor(9, 19))
    furniture.append(desk_with_monitor(7, 25))
    # Decorations
    furniture.append(bookshelf_tall(1, 18))
    furniture.append(bookshelf_tall(22, 18))
    furniture.append(single_tile(15, 30, 5, 28, "plant"))
    furniture.append(single_tile(1, 30, 1, 18, "picture"))   # picture

    # === Brain HQ (cols 27-50, rows 18-31) — executive desk + meeting table ===
    # Executive desk (center)
    furniture.append(wide_desk(37, 19))
    # Meeting table (large, 3x2)
    furniture.append(meeting_table(35, 25))
    # Decorations
    furniture.append(single_tile(28, 18, 0, 22, "clock"))    # clock
    furniture.append(single_tile(49, 18, 5, 28, "plant"))    # plant
    furniture.append(single_tile(28, 30, 5, 28, "plant"))    # plant
    furniture.append(single_tile(49, 30, 5, 28, "plant"))    # plant
    # Wall monitors (for Brain HQ big screen)
    furniture.append(single_tile(38, 18, 4, 20, "monitor"))
    furniture.append(single_tile(39, 18, 4, 20, "monitor"))
    furniture.append(single_tile(40, 18, 4, 20, "monitor"))
    furniture.append(single_tile(34, 18, 1, 18, "picture"))  # picture
    furniture.append(bookshelf_tall(27, 28))

    return furniture


def build_seats():
    return [
        # CC Room (5 seats — chair row = desk row + 2)
        {"id": "cc-seat-0", "seatCol": 3,  "seatRow": 4,  "facingDir": UP},
        {"id": "cc-seat-1", "seatCol": 6,  "seatRow": 4,  "facingDir": UP},
        {"id": "cc-seat-2", "seatCol": 9,  "seatRow": 4,  "facingDir": UP},
        {"id": "cc-seat-3", "seatCol": 12, "seatRow": 4,  "facingDir": UP},
        {"id": "cc-seat-4", "seatCol": 7,  "seatRow": 10, "facingDir": UP},

        # Codex Room (4 seats)
        {"id": "codex-seat-0", "seatCol": 29, "seatRow": 4,  "facingDir": UP},
        {"id": "codex-seat-1", "seatCol": 32, "seatRow": 4,  "facingDir": UP},
        {"id": "codex-seat-2", "seatCol": 35, "seatRow": 4,  "facingDir": UP},
        {"id": "codex-seat-3", "seatCol": 32, "seatRow": 10, "facingDir": UP},

        # AG Room (4 seats)
        {"id": "ag-seat-0", "seatCol": 3,  "seatRow": 21, "facingDir": UP},
        {"id": "ag-seat-1", "seatCol": 6,  "seatRow": 21, "facingDir": UP},
        {"id": "ag-seat-2", "seatCol": 9,  "seatRow": 21, "facingDir": UP},
        {"id": "ag-seat-3", "seatCol": 7,  "seatRow": 27, "facingDir": UP},

        # Brain HQ (1 executive seat)
        {"id": "brain-seat-0", "seatCol": 37, "seatRow": 21, "facingDir": UP},
    ]


def build_agents():
    return [
        # CC Team (5)
        {"id": 1,  "role": "foreman",      "displayName": "Foreman",      "team": "cc",    "room": "cc",    "seatId": "cc-seat-0",    "spriteRow": 0, "spriteCol": 0},
        {"id": 2,  "role": "engineer",     "displayName": "Engineer",     "team": "cc",    "room": "cc",    "seatId": "cc-seat-1",    "spriteRow": 0, "spriteCol": 1},
        {"id": 3,  "role": "critic",       "displayName": "Critic",       "team": "cc",    "room": "cc",    "seatId": "cc-seat-2",    "spriteRow": 0, "spriteCol": 2},
        {"id": 4,  "role": "gitops",       "displayName": "GitOps",       "team": "cc",    "room": "cc",    "seatId": "cc-seat-3",    "spriteRow": 0, "spriteCol": 3},
        {"id": 5,  "role": "vault_keeper", "displayName": "VaultKeeper",  "team": "cc",    "room": "cc",    "seatId": "cc-seat-4",    "spriteRow": 0, "spriteCol": 0},

        # Codex Team (4)
        {"id": 6,  "role": "compute_lead", "displayName": "Compute Lead", "team": "codex", "room": "codex", "seatId": "codex-seat-0", "spriteRow": 1, "spriteCol": 0},
        {"id": 7,  "role": "quant",        "displayName": "Quant",        "team": "codex", "room": "codex", "seatId": "codex-seat-1", "spriteRow": 1, "spriteCol": 1},
        {"id": 8,  "role": "backtester",   "displayName": "Backtester",   "team": "codex", "room": "codex", "seatId": "codex-seat-2", "spriteRow": 1, "spriteCol": 2},
        {"id": 9,  "role": "builder",      "displayName": "Builder",      "team": "codex", "room": "codex", "seatId": "codex-seat-3", "spriteRow": 1, "spriteCol": 3},

        # AG Team (4)
        {"id": 10, "role": "scout_lead",   "displayName": "Scout Lead",   "team": "ag",    "room": "ag",    "seatId": "ag-seat-0",    "spriteRow": 1, "spriteCol": 0},
        {"id": 11, "role": "web_scout",    "displayName": "Web Scout",    "team": "ag",    "room": "ag",    "seatId": "ag-seat-1",    "spriteRow": 1, "spriteCol": 1},
        {"id": 12, "role": "architect",    "displayName": "Architect",    "team": "ag",    "room": "ag",    "seatId": "ag-seat-2",    "spriteRow": 1, "spriteCol": 2},
        {"id": 13, "role": "experiment",   "displayName": "Experiment",   "team": "ag",    "room": "ag",    "seatId": "ag-seat-3",    "spriteRow": 1, "spriteCol": 3},

        # Brain (1)
        {"id": 14, "role": "brain",        "displayName": "Brain",        "team": "brain", "room": "brain", "seatId": "brain-seat-0", "spriteRow": 0, "spriteCol": 3},
    ]


def main():
    layout = {
        "version": 1,
        "cols": COLS,
        "rows": ROWS,
        "tiles": build_tile_grid(),
        "rooms": build_rooms(),
        "hallway": build_hallway(),
        "wallTiles": {
            "tiles": [{"sx": 2, "sy": 8}, {"sx": 3, "sy": 8}]
        },
        "furniture": build_furniture(),
        "seats": build_seats(),
        "agents": build_agents(),
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(layout, f, indent=2, ensure_ascii=False)

    print(f"Generated: {OUTPUT_PATH}")
    print(f"Grid: {COLS}x{ROWS} = {COLS * ROWS} tiles")
    print(f"Rooms: {len(layout['rooms'])}")
    print(f"Furniture: {len(layout['furniture'])} items")
    print(f"Seats: {len(layout['seats'])}")
    print(f"Agents: {len(layout['agents'])}")


if __name__ == "__main__":
    main()

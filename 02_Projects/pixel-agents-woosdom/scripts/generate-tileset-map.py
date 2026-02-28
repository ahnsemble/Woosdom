#!/usr/bin/env python3
"""
Tileset 분석 + tileset-map.json 생성 스크립트.
Office Tileset All 16x16.png를 PIL로 분석하고, 타일을 카테고리별로 분류한다.

사용법: python3 scripts/generate-tileset-map.py
출력: config/tileset-map.json
"""

from PIL import Image
import json
import os

TILESET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "src", "assets", "tileset.png"
)
OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config", "tileset-map.json"
)

TILE_SIZE = 16


def analyze_tile(img, col, row):
    """단일 타일 분석: 평균 색상, 투명도."""
    x0 = col * TILE_SIZE
    y0 = row * TILE_SIZE
    tile = img.crop((x0, y0, x0 + TILE_SIZE, y0 + TILE_SIZE))
    pixels = list(tile.getdata())

    if img.mode == "RGBA":
        non_transparent = [(r, g, b) for r, g, b, a in pixels if a > 128]
        transparent_count = sum(1 for _, _, _, a in pixels if a <= 128)
        transparent_ratio = transparent_count / len(pixels) if pixels else 1.0
    else:
        non_transparent = [(p[0], p[1], p[2]) for p in pixels]
        transparent_ratio = 0.0

    if non_transparent:
        avg_r = sum(p[0] for p in non_transparent) // len(non_transparent)
        avg_g = sum(p[1] for p in non_transparent) // len(non_transparent)
        avg_b = sum(p[2] for p in non_transparent) // len(non_transparent)
    else:
        avg_r = avg_g = avg_b = 0

    return {
        "col": col,
        "row": row,
        "avgColor": [avg_r, avg_g, avg_b],
        "transparency": round(transparent_ratio, 2),
        "isEmpty": transparent_ratio > 0.95,
    }


def categorize_tiles(tiles_data, grid_cols, grid_rows):
    """
    타일을 카테고리별로 분류.
    시각적 분석 결과 기반 수동 매핑 (tileset.png = Donarg Office Interior 16x16).
    """
    categories = {
        "floor": [],
        "wall": [],
        "desk": [],
        "chair": [],
        "bookshelf": [],
        "monitor": [],
        "computer": [],
        "plant": [],
        "sofa": [],
        "appliance": [],
        "decoration": [],
        "window": [],
        "door": [],
        "box": [],
        "rug": [],
        "misc": [],
    }

    # --- 수동 카테고리 매핑 (tileset 시각적 분석 결과) ---
    # 형식: (col, row) -> category

    manual_map = {}

    # Row 0: 책상 상단 (나무색 + 회색 변형)
    for c in range(1, 7):
        manual_map[(c, 0)] = "desk"
    manual_map[(7, 0)] = "desk"  # 회색 책상
    for c in range(8, 14):
        manual_map[(c, 0)] = "desk"
    manual_map[(14, 0)] = "desk"
    manual_map[(15, 0)] = "desk"

    # Row 1: 책상 하단 / 서랍
    for c in range(1, 7):
        manual_map[(c, 1)] = "desk"
    manual_map[(7, 1)] = "desk"
    for c in range(8, 14):
        manual_map[(c, 1)] = "desk"
    manual_map[(14, 1)] = "desk"
    manual_map[(15, 1)] = "desk"

    # Row 2-3: 소파/벤치/선반 상단+하단
    for c in range(0, 8):
        manual_map[(c, 2)] = "sofa"  # 소파/벤치
        manual_map[(c, 3)] = "sofa"
    for c in range(8, 14):
        manual_map[(c, 2)] = "bookshelf"  # 선반
        manual_map[(c, 3)] = "bookshelf"
    for c in range(14, 16):
        manual_map[(c, 2)] = "wall"  # 벽 변형
        manual_map[(c, 3)] = "wall"

    # Row 4-5: 바닥 타일 (나무, 타일 패턴)
    for c in range(0, 2):
        manual_map[(c, 4)] = "floor"  # 나무 바닥
    for c in range(2, 8):
        manual_map[(c, 4)] = "floor"  # 회색/타일 바닥
    for c in range(8, 11):
        manual_map[(c, 4)] = "floor"
    for c in range(11, 16):
        manual_map[(c, 4)] = "floor"
    for c in range(0, 2):
        manual_map[(c, 5)] = "floor"
    for c in range(2, 8):
        manual_map[(c, 5)] = "floor"
    for c in range(8, 11):
        manual_map[(c, 5)] = "floor"
    for c in range(11, 16):
        manual_map[(c, 5)] = "floor"

    # Row 6-7: 추가 바닥 타일 / 벽 타일
    for c in range(0, 16):
        manual_map[(c, 6)] = "floor"
        manual_map[(c, 7)] = "floor"

    # Row 8-9: 벽 타일, 책장
    for c in range(0, 4):
        manual_map[(c, 8)] = "wall"
    for c in range(4, 8):
        manual_map[(c, 8)] = "wall"
    for c in range(8, 12):
        manual_map[(c, 8)] = "bookshelf"
    for c in range(12, 16):
        manual_map[(c, 8)] = "bookshelf"
    for c in range(0, 4):
        manual_map[(c, 9)] = "wall"
    for c in range(4, 8):
        manual_map[(c, 9)] = "wall"
    for c in range(8, 12):
        manual_map[(c, 9)] = "bookshelf"
    for c in range(12, 16):
        manual_map[(c, 9)] = "bookshelf"

    # Row 10-11: 대형 기기 (음료자판기, 복사기, 서버 등)
    for c in range(0, 16):
        manual_map[(c, 10)] = "appliance"
        manual_map[(c, 11)] = "appliance"

    # Row 12-13: 의자, 소파 단일, 화분, 컵 등 소품
    for c in range(0, 4):
        manual_map[(c, 12)] = "chair"
    for c in range(4, 8):
        manual_map[(c, 12)] = "chair"
    for c in range(8, 16):
        manual_map[(c, 12)] = "misc"
    for c in range(0, 4):
        manual_map[(c, 13)] = "chair"
    for c in range(4, 8):
        manual_map[(c, 13)] = "chair"
    for c in range(8, 16):
        manual_map[(c, 13)] = "misc"

    # Row 14-15: 소형 가전/소품 (모니터 소형, 전화기, 키보드, 마우스 등)
    for c in range(0, 16):
        manual_map[(c, 14)] = "misc"
        manual_map[(c, 15)] = "misc"

    # Row 16-17: 의자, 간판, 소품
    for c in range(0, 4):
        manual_map[(c, 16)] = "misc"
    for c in range(0, 4):
        manual_map[(c, 17)] = "chair"
    for c in range(4, 16):
        manual_map[(c, 16)] = "misc"
        manual_map[(c, 17)] = "misc"

    # Row 18-19: 벽 장식 (화이트보드, 그림, 액자)
    for c in range(0, 16):
        manual_map[(c, 18)] = "decoration"
        manual_map[(c, 19)] = "decoration"

    # Row 20-21: 컴퓨터, 모니터, 키보드 세트
    for c in range(0, 16):
        manual_map[(c, 20)] = "computer"
        manual_map[(c, 21)] = "computer"

    # Row 22-23: 시계, 액자, 전구, 스위치
    for c in range(0, 16):
        manual_map[(c, 22)] = "decoration"
        manual_map[(c, 23)] = "decoration"

    # Row 24-25: 더 많은 컴퓨터/모니터
    for c in range(0, 16):
        manual_map[(c, 24)] = "computer"
        manual_map[(c, 25)] = "computer"

    # Row 26-27: 풍경화, 벽장식
    for c in range(0, 16):
        manual_map[(c, 26)] = "decoration"
        manual_map[(c, 27)] = "decoration"

    # Row 28-29: 식물(화분), 박스
    for c in range(0, 8):
        manual_map[(c, 28)] = "plant"
        manual_map[(c, 29)] = "plant"
    for c in range(8, 16):
        manual_map[(c, 28)] = "box"
        manual_map[(c, 29)] = "box"

    # Row 30-31: 바닥 매트, 카펫, 문매트
    for c in range(0, 16):
        manual_map[(c, 30)] = "rug"
        manual_map[(c, 31)] = "rug"

    # 분류 실행
    for t in tiles_data:
        if t["isEmpty"]:
            continue
        key = (t["col"], t["row"])
        cat = manual_map.get(key, "misc")
        categories[cat].append({
            "col": t["col"],
            "row": t["row"],
            "avgColor": t["avgColor"],
            "transparency": t["transparency"],
        })

    return categories


def build_furniture_presets():
    """
    다중 타일 가구 프리셋 정의.
    레퍼런스 이미지 (Office Level 1-4) 기반.
    """
    return {
        "desk_with_monitor": {
            "label": "Monitor Desk",
            "description": "모니터 + 책상 + 의자 (1x3)",
            "tiles": [
                {"sx": 4, "sy": 20, "offsetCol": 0, "offsetRow": 0, "name": "monitor"},
                {"sx": 2, "sy": 0, "offsetCol": 0, "offsetRow": 1, "name": "desk"},
                {"sx": 1, "sy": 17, "offsetCol": 0, "offsetRow": 2, "name": "chair"},
            ],
            "footprint": [1, 3],
            "blockedOffsets": [[0, 0], [0, 1]],
            "seatOffset": {"col": 0, "row": 2, "facingDir": 1},
        },
        "wide_desk_with_monitor": {
            "label": "Wide Desk (2x3)",
            "description": "2칸 책상 + 모니터 + 의자 2개",
            "tiles": [
                {"sx": 4, "sy": 20, "offsetCol": 0, "offsetRow": 0, "name": "monitor_l"},
                {"sx": 4, "sy": 20, "offsetCol": 1, "offsetRow": 0, "name": "monitor_r"},
                {"sx": 2, "sy": 0, "offsetCol": 0, "offsetRow": 1, "name": "desk_l"},
                {"sx": 5, "sy": 0, "offsetCol": 1, "offsetRow": 1, "name": "desk_r"},
                {"sx": 1, "sy": 17, "offsetCol": 0, "offsetRow": 2, "name": "chair_l"},
                {"sx": 1, "sy": 17, "offsetCol": 1, "offsetRow": 2, "name": "chair_r"},
            ],
            "footprint": [2, 3],
            "blockedOffsets": [[0, 0], [1, 0], [0, 1], [1, 1]],
            "seatOffset": {"col": 0, "row": 2, "facingDir": 1},
        },
        "bookshelf_tall": {
            "label": "Bookshelf (1x2)",
            "description": "2칸 높이 책장",
            "tiles": [
                {"sx": 10, "sy": 8, "offsetCol": 0, "offsetRow": 0, "name": "top"},
                {"sx": 10, "sy": 9, "offsetCol": 0, "offsetRow": 1, "name": "bottom"},
            ],
            "footprint": [1, 2],
            "blockedOffsets": [[0, 0], [0, 1]],
        },
        "bookshelf_wide": {
            "label": "Wide Bookshelf (2x2)",
            "description": "2칸 폭 책장",
            "tiles": [
                {"sx": 10, "sy": 8, "offsetCol": 0, "offsetRow": 0, "name": "top_l"},
                {"sx": 11, "sy": 8, "offsetCol": 1, "offsetRow": 0, "name": "top_r"},
                {"sx": 10, "sy": 9, "offsetCol": 0, "offsetRow": 1, "name": "bot_l"},
                {"sx": 11, "sy": 9, "offsetCol": 1, "offsetRow": 1, "name": "bot_r"},
            ],
            "footprint": [2, 2],
            "blockedOffsets": [[0, 0], [1, 0], [0, 1], [1, 1]],
        },
        "meeting_table_3x2": {
            "label": "Meeting Table (3x2)",
            "description": "3x2 회의 테이블",
            "tiles": [
                {"sx": 2, "sy": 0, "offsetCol": 0, "offsetRow": 0, "name": "desk_tl"},
                {"sx": 5, "sy": 0, "offsetCol": 1, "offsetRow": 0, "name": "desk_tc"},
                {"sx": 2, "sy": 0, "offsetCol": 2, "offsetRow": 0, "name": "desk_tr"},
                {"sx": 2, "sy": 0, "offsetCol": 0, "offsetRow": 1, "name": "desk_bl"},
                {"sx": 5, "sy": 0, "offsetCol": 1, "offsetRow": 1, "name": "desk_bc"},
                {"sx": 2, "sy": 0, "offsetCol": 2, "offsetRow": 1, "name": "desk_br"},
            ],
            "footprint": [3, 2],
            "blockedOffsets": [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1]],
        },
        "whiteboard": {
            "label": "Whiteboard (1x2)",
            "description": "벽걸이 화이트보드",
            "tiles": [
                {"sx": 2, "sy": 18, "offsetCol": 0, "offsetRow": 0, "name": "top"},
                {"sx": 2, "sy": 19, "offsetCol": 0, "offsetRow": 1, "name": "bottom"},
            ],
            "footprint": [1, 2],
            "blockedOffsets": [[0, 0], [0, 1]],
        },
        "server_rack": {
            "label": "Server Rack (1x2)",
            "description": "서버 랙",
            "tiles": [
                {"sx": 14, "sy": 10, "offsetCol": 0, "offsetRow": 0, "name": "top"},
                {"sx": 14, "sy": 11, "offsetCol": 0, "offsetRow": 1, "name": "bottom"},
            ],
            "footprint": [1, 2],
            "blockedOffsets": [[0, 0], [0, 1]],
        },
        "vending_machine": {
            "label": "Vending Machine (1x2)",
            "description": "자판기",
            "tiles": [
                {"sx": 0, "sy": 10, "offsetCol": 0, "offsetRow": 0, "name": "top"},
                {"sx": 0, "sy": 11, "offsetCol": 0, "offsetRow": 1, "name": "bottom"},
            ],
            "footprint": [1, 2],
            "blockedOffsets": [[0, 0], [0, 1]],
        },
        "water_cooler": {
            "label": "Water Cooler (1x2)",
            "description": "정수기",
            "tiles": [
                {"sx": 2, "sy": 10, "offsetCol": 0, "offsetRow": 0, "name": "top"},
                {"sx": 2, "sy": 11, "offsetCol": 0, "offsetRow": 1, "name": "bottom"},
            ],
            "footprint": [1, 2],
            "blockedOffsets": [[0, 0], [0, 1]],
        },
        "copier": {
            "label": "Copier (2x2)",
            "description": "복사기",
            "tiles": [
                {"sx": 4, "sy": 10, "offsetCol": 0, "offsetRow": 0, "name": "top_l"},
                {"sx": 5, "sy": 10, "offsetCol": 1, "offsetRow": 0, "name": "top_r"},
                {"sx": 4, "sy": 11, "offsetCol": 0, "offsetRow": 1, "name": "bot_l"},
                {"sx": 5, "sy": 11, "offsetCol": 1, "offsetRow": 1, "name": "bot_r"},
            ],
            "footprint": [2, 2],
            "blockedOffsets": [[0, 0], [1, 0], [0, 1], [1, 1]],
        },
        "sofa_2seat": {
            "label": "2-Seat Sofa (2x2)",
            "description": "2인 소파",
            "tiles": [
                {"sx": 0, "sy": 2, "offsetCol": 0, "offsetRow": 0, "name": "back_l"},
                {"sx": 1, "sy": 2, "offsetCol": 1, "offsetRow": 0, "name": "back_r"},
                {"sx": 0, "sy": 3, "offsetCol": 0, "offsetRow": 1, "name": "seat_l"},
                {"sx": 1, "sy": 3, "offsetCol": 1, "offsetRow": 1, "name": "seat_r"},
            ],
            "footprint": [2, 2],
            "blockedOffsets": [[0, 0], [1, 0], [0, 1], [1, 1]],
        },
        "large_landscape": {
            "label": "Landscape Painting (3x2)",
            "description": "벽걸이 풍경화",
            "tiles": [
                {"sx": 0, "sy": 26, "offsetCol": 0, "offsetRow": 0, "name": "tl"},
                {"sx": 1, "sy": 26, "offsetCol": 1, "offsetRow": 0, "name": "tc"},
                {"sx": 2, "sy": 26, "offsetCol": 2, "offsetRow": 0, "name": "tr"},
                {"sx": 0, "sy": 27, "offsetCol": 0, "offsetRow": 1, "name": "bl"},
                {"sx": 1, "sy": 27, "offsetCol": 1, "offsetRow": 1, "name": "bc"},
                {"sx": 2, "sy": 27, "offsetCol": 2, "offsetRow": 1, "name": "br"},
            ],
            "footprint": [3, 2],
            "blockedOffsets": [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1]],
        },
    }


def build_single_tile_items():
    """단일 타일 아이템 정의."""
    return {
        "plant_potted": {"sx": 5, "sy": 28, "category": "plant", "label": "Potted Plant", "blocked": True},
        "plant_small": {"sx": 4, "sy": 28, "category": "plant", "label": "Small Plant", "blocked": True},
        "plant_large": {"sx": 6, "sy": 28, "category": "plant", "label": "Large Plant", "blocked": True},
        "plant_fern": {"sx": 7, "sy": 28, "category": "plant", "label": "Fern", "blocked": True},
        "clock_wall": {"sx": 0, "sy": 22, "category": "decoration", "label": "Wall Clock", "blocked": True},
        "picture_small": {"sx": 1, "sy": 18, "category": "decoration", "label": "Small Picture", "blocked": True},
        "box_single": {"sx": 8, "sy": 28, "category": "box", "label": "Box", "blocked": True},
        "box_stack": {"sx": 9, "sy": 28, "category": "box", "label": "Stacked Boxes", "blocked": True},
        "chair_simple": {"sx": 1, "sy": 17, "category": "chair", "label": "Office Chair", "blocked": False},
        "chair_red": {"sx": 0, "sy": 12, "category": "chair", "label": "Red Chair", "blocked": False},
        "chair_brown": {"sx": 4, "sy": 12, "category": "chair", "label": "Brown Chair", "blocked": False},
        "monitor_single": {"sx": 4, "sy": 20, "category": "computer", "label": "Monitor", "blocked": True},
        "desk_single": {"sx": 2, "sy": 0, "category": "desk", "label": "Desk Tile", "blocked": True},
        "rug_tile": {"sx": 0, "sy": 30, "category": "rug", "label": "Rug", "blocked": False},
    }


def main():
    img = Image.open(TILESET_PATH)
    width, height = img.size
    grid_cols = width // TILE_SIZE
    grid_rows = height // TILE_SIZE

    print(f"Tileset: {width}x{height} px, {grid_cols} cols x {grid_rows} rows = {grid_cols * grid_rows} tiles")

    # 전체 타일 분석
    tiles_data = []
    for row in range(grid_rows):
        for col in range(grid_cols):
            tiles_data.append(analyze_tile(img, col, row))

    non_empty = [t for t in tiles_data if not t["isEmpty"]]
    print(f"Non-empty tiles: {len(non_empty)} / {len(tiles_data)}")

    # 카테고리 분류
    categories = categorize_tiles(tiles_data, grid_cols, grid_rows)

    # JSON 빌드
    result = {
        "tileset": "tileset.png",
        "tileSize": TILE_SIZE,
        "gridCols": grid_cols,
        "gridRows": grid_rows,
        "totalTiles": grid_cols * grid_rows,
        "nonEmptyTiles": len(non_empty),
        "categories": categories,
        "furniturePresets": build_furniture_presets(),
        "singleTileItems": build_single_tile_items(),
    }

    # 출력
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nOutput: {OUTPUT_PATH}")
    print("\nCategories:")
    for cat, tiles in categories.items():
        print(f"  {cat}: {len(tiles)} tiles")


if __name__ == "__main__":
    main()

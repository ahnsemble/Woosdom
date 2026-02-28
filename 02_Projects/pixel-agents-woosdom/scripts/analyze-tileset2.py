#!/usr/bin/env python3
"""Analyze tileset2.png (B-C-D-E Office 2) and generate tileset2-map.json.
Tileset: 512×512, 16px tiles → 32×32 grid.
"""

import json
import os
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

INPUT_PATH = os.path.join(PROJECT_ROOT, "src", "assets", "tileset2.png")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "config", "tileset2-map.json")

TILE_SIZE = 16
OPACITY_THRESHOLD = 0.05  # at least 5% opaque pixels to be considered non-empty


def analyze():
    img = Image.open(INPUT_PATH).convert("RGBA")
    width, height = img.size

    grid_cols = width // TILE_SIZE
    grid_rows = height // TILE_SIZE

    pixels = list(img.getdata())

    tiles = []
    for row in range(grid_rows):
        for col in range(grid_cols):
            opaque_count = 0
            r_sum = g_sum = b_sum = 0

            for ty in range(TILE_SIZE):
                for tx in range(TILE_SIZE):
                    px = (row * TILE_SIZE + ty) * width + (col * TILE_SIZE + tx)
                    r, g, b, a = pixels[px]
                    if a > 10:
                        opaque_count += 1
                        r_sum += r
                        g_sum += g
                        b_sum += b

            total = TILE_SIZE * TILE_SIZE
            opacity = opaque_count / total

            if opacity > OPACITY_THRESHOLD:
                avg_r = r_sum // opaque_count if opaque_count else 0
                avg_g = g_sum // opaque_count if opaque_count else 0
                avg_b = b_sum // opaque_count if opaque_count else 0
                tiles.append({
                    "col": col,
                    "row": row,
                    "label": f"Pack2 ({col},{row})",
                    "transparency": round(1 - opacity, 2),
                    "avgColor": [avg_r, avg_g, avg_b],
                })

    result = {
        "tileSize": TILE_SIZE,
        "gridCols": grid_cols,
        "gridRows": grid_rows,
        "tiles": tiles,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    print(f"tileset2: {grid_cols}×{grid_rows} grid, {len(tiles)} non-empty tiles")
    print(f"Written → {OUTPUT_PATH}")


if __name__ == "__main__":
    analyze()

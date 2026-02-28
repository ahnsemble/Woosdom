#!/usr/bin/env python3
"""
Donarg Office Interior 16x16 타일셋 분석 스크립트.
PIL로 이미지를 열어 각 16x16 타일의 위치와 평균 색상을 추출한다.
결과를 src/assets/tileset-map.txt에 기록한다.
"""

from PIL import Image
import os

TILESET_PATH = "/Users/woosung/Desktop/Dev/Woosdom_Brain/02_Projects/woosdom_app/assets/Office Tileset/Office Tileset All 16x16.png"
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "assets", "tileset-map.txt")

def analyze_tile(img, col, row, tile_size=16):
    """Analyze a single tile and return its average color and transparency."""
    x0 = col * tile_size
    y0 = row * tile_size
    tile = img.crop((x0, y0, x0 + tile_size, y0 + tile_size))
    pixels = list(tile.getdata())

    if img.mode == "RGBA":
        non_transparent = [(r, g, b) for r, g, b, a in pixels if a > 128]
        transparent_ratio = 1.0 - len(non_transparent) / len(pixels) if pixels else 1.0
    else:
        non_transparent = pixels
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
        "avg_color": (avg_r, avg_g, avg_b),
        "transparent_ratio": transparent_ratio,
        "is_empty": transparent_ratio > 0.95,
    }


def main():
    img = Image.open(TILESET_PATH)
    width, height = img.size
    tile_size = 16
    cols = width // tile_size
    rows = height // tile_size

    print(f"Image size: {width}x{height} pixels")
    print(f"Grid: {cols} columns x {rows} rows = {cols * rows} tiles")
    print(f"Mode: {img.mode}")
    print()

    tiles = []
    for row in range(rows):
        for col in range(cols):
            info = analyze_tile(img, col, row, tile_size)
            tiles.append(info)

    # Write output
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        f.write(f"# Donarg Office Interior 16x16 Tileset Analysis\n")
        f.write(f"# Image: {width}x{height} pixels\n")
        f.write(f"# Grid: {cols} cols x {rows} rows = {cols * rows} tiles\n")
        f.write(f"# Tile size: {tile_size}x{tile_size}\n\n")

        f.write("## Tile Map (col, row) -> avg_color, transparency\n\n")

        non_empty_count = 0
        for row_idx in range(rows):
            f.write(f"### Row {row_idx} (y={row_idx * tile_size}-{(row_idx + 1) * tile_size - 1})\n")
            row_tiles = [t for t in tiles if t["row"] == row_idx]
            for t in row_tiles:
                if not t["is_empty"]:
                    non_empty_count += 1
                    r, g, b = t["avg_color"]
                    tr = t["transparent_ratio"]
                    marker = " (partial)" if 0.1 < tr <= 0.95 else ""
                    f.write(f"  [{t['col']:2d},{t['row']:2d}] rgb({r:3d},{g:3d},{b:3d}) trans={tr:.0%}{marker}\n")
            empty_in_row = sum(1 for t in row_tiles if t["is_empty"])
            if empty_in_row > 0:
                f.write(f"  ({empty_in_row} empty tiles)\n")
            f.write("\n")

        f.write(f"\n## Summary\n")
        f.write(f"Total tiles: {len(tiles)}\n")
        f.write(f"Non-empty tiles: {non_empty_count}\n")
        f.write(f"Empty tiles: {len(tiles) - non_empty_count}\n")

    print(f"Analysis written to: {OUTPUT_PATH}")
    print(f"Non-empty tiles: {non_empty_count} / {len(tiles)}")


if __name__ == "__main__":
    main()

import json
import os
import hashlib
from PIL import Image

ASSETS_DIR = "src/assets/tilesets/vx_ace"
OUT_FILE = "config/tileset-vx-map.json"
TILE_SIZE = 16

files = [
    {"file": "A2 Office Floors.png", "idx": 2, "category": "floor"},
    {"file": "A4 Office Walls.png", "idx": 3, "category": "wall"},
    {"file": "A5 Office Floors & Walls.png", "idx": 4, "category": "wall"},
    {"file": "B-C-D-E Office 1 No Shadows.png", "idx": 5, "category": "furniture"},
    {"file": "B-C-D-E Office 2 No Shadows.png", "idx": 6, "category": "furniture"}
]

images_data = []

def get_tile_hash(img, col, row, span=1):
    box = (col * TILE_SIZE, row * TILE_SIZE, (col + span) * TILE_SIZE, (row + span) * TILE_SIZE)
    tile = img.crop(box)
    
    # Check if fully transparent
    transparent = True
    pixels = list(tile.getdata())
    for p in pixels:
        if len(p) == 4 and p[3] == 0:
            continue
        transparent = False
        break
        
    if transparent:
        return "transparent"
        
    return hashlib.md5(tile.tobytes()).hexdigest()

for f in files:
    path = os.path.join(ASSETS_DIR, f['file'])
    if not os.path.exists(path):
        continue
        
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    
    span = 2 if f['category'] == 'furniture' else 1
    
    cols = w // TILE_SIZE
    rows = h // TILE_SIZE
    
    seen_hashes = set()
    tiles = []
    
    for r in range(0, rows, span):
        for c in range(0, cols, span):
            thash = get_tile_hash(img, c, r, span)
            if thash == "transparent":
                continue
            if thash not in seen_hashes:
                seen_hashes.add(thash)
                tiles.append({
                    "col": c,
                    "row": r,
                    "sw": span,
                    "sh": span,
                    "tilesetIdx": f['idx']
                })
                
    images_data.append({
        "file": f['file'],
        "tilesetIdx": f['idx'],
        "category": f['category'],
        "cols": cols,
        "rows": rows,
        "tiles": tiles
    })

with open(OUT_FILE, 'w') as out:
    json.dump({
        "tileSize": TILE_SIZE,
        "images": images_data
    }, out, indent=2)

print(f"VX Map generated: {OUT_FILE}")

import type { LayoutConfig, FurnitureConfig } from '../config/LayoutTypes.ts'

// Tile types
const VOID = 0
const FLOOR = 1
const WALL = 2

let uidCounter = 1000

function nextUid(): string {
  return `edit_${uidCounter++}`
}

/** Paint a floor tile at (col, row) with a specific sprite */
export function paintFloor(
  layout: LayoutConfig,
  col: number,
  row: number,
  tileSx: number,
  tileSy: number,
  tilesetIdx?: number,
): LayoutConfig {
  const tiles = [...layout.tiles]
  const idx = row * layout.cols + col
  if (idx < 0 || idx >= tiles.length) return layout
  tiles[idx] = FLOOR

  // Store per-tile sprite override so the selected tile actually appears
  const tileOverrides = { ...(layout.tileOverrides ?? {}) }
  tileOverrides[`${col},${row}`] = { sx: tileSx, sy: tileSy, tilesetIdx }

  return { ...layout, tiles, tileOverrides }
}

/** Paint a wall tile at (col, row) with optional sprite override */
export function paintWall(
  layout: LayoutConfig,
  col: number,
  row: number,
  tileSx?: number,
  tileSy?: number,
  tilesetIdx?: number,
): LayoutConfig {
  const tiles = [...layout.tiles]
  const idx = row * layout.cols + col
  if (idx < 0 || idx >= tiles.length) return layout
  tiles[idx] = WALL

  if (tileSx !== undefined && tileSy !== undefined) {
    const tileOverrides = { ...(layout.tileOverrides ?? {}) }
    tileOverrides[`${col},${row}`] = { sx: tileSx, sy: tileSy, tilesetIdx }
    return { ...layout, tiles, tileOverrides }
  }

  return { ...layout, tiles }
}

/** Erase a tile (set to VOID) and remove any furniture at that position */
export function eraseTile(
  layout: LayoutConfig,
  col: number,
  row: number,
): LayoutConfig {
  const tiles = [...layout.tiles]
  const idx = row * layout.cols + col
  if (idx < 0 || idx >= tiles.length) return layout
  tiles[idx] = VOID

  // Remove any furniture that overlaps with this tile
  const furniture = layout.furniture.filter(f => {
    for (const t of f.tiles) {
      if (f.col + t.offsetCol === col && f.row + t.offsetRow === row) {
        return false
      }
    }
    return true
  })

  // Clean up tile override
  const tileOverrides = { ...(layout.tileOverrides ?? {}) }
  delete tileOverrides[`${col},${row}`]

  return { ...layout, tiles, furniture, tileOverrides }
}

/** Place a furniture preset at (col, row) */
export function placeFurniture(
  layout: LayoutConfig,
  presetType: string,
  col: number,
  row: number,
  presetTiles: Array<{ sx: number; sy: number; offsetCol: number; offsetRow: number; tilesetIdx?: number; sw?: number; sh?: number }>,
  blockedOffsets: [number, number][],
): LayoutConfig {
  const newFurniture: FurnitureConfig = {
    uid: nextUid(),
    type: presetType,
    col,
    row,
    tiles: presetTiles,
    blockedOffsets,
  }

  return {
    ...layout,
    furniture: [...layout.furniture, newFurniture],
  }
}

/** Remove furniture by uid */
export function removeFurniture(
  layout: LayoutConfig,
  uid: string,
): LayoutConfig {
  return {
    ...layout,
    furniture: layout.furniture.filter(f => f.uid !== uid),
  }
}

/** Find furniture at (col, row) */
export function findFurnitureAt(
  layout: LayoutConfig,
  col: number,
  row: number,
): FurnitureConfig | null {
  for (const f of layout.furniture) {
    for (const t of f.tiles) {
      if (f.col + t.offsetCol === col && f.row + t.offsetRow === row) {
        return f
      }
    }
  }
  return null
}

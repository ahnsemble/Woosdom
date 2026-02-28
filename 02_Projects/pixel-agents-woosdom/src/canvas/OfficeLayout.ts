import { TILE_SIZE } from '../constants.ts'
import { TileType, Direction } from './types.ts'
import type { RoomDef, Seat, FurniturePlacement, TileRef } from './types.ts'
import { getLayoutSync, getRoomAt as layoutGetRoomAt, getFloorColor as layoutGetFloorColor, getFloorTileRef as layoutGetFloorTileRef } from '../config/LayoutLoader.ts'
import type { RoomConfig } from '../config/LayoutTypes.ts'

// ---- Config-driven room accessors ----

function toRoomDef(rc: RoomConfig): RoomDef {
  const teamMap: Record<string, string> = { cc: 'cc', codex: 'codex', ag: 'ag', brain: 'brain' }
  return {
    id: rc.id,
    label: rc.label,
    team: (teamMap[rc.team] ?? rc.team) as RoomDef['team'],
    minCol: rc.minCol,
    maxCol: rc.maxCol,
    minRow: rc.minRow,
    maxRow: rc.maxRow,
    floorColor: rc.floorColor,
  }
}

/** Get all rooms from layout config */
export function getRooms(): RoomDef[] {
  const layout = getLayoutSync()
  return layout.rooms.map(toRoomDef)
}

/** Legacy ROOMS export — reads from config */
export const ROOMS: RoomDef[] = []

/** Initialize ROOMS array after layout is loaded */
export function initRooms(): void {
  ROOMS.length = 0
  ROOMS.push(...getRooms())
}

/** Get hallway bounds from config */
export function getHallway() {
  const layout = getLayoutSync()
  return {
    minCol: layout.hallway.minCol,
    maxCol: layout.hallway.maxCol,
    minRow: layout.hallway.minRow,
    maxRow: layout.hallway.maxRow,
    floorColor: layout.hallway.floorColor,
  }
}

/** Get floor tile ref for a grid coordinate (checkerboard pattern) */
export function getFloorTileRef(col: number, row: number): TileRef {
  const ref = layoutGetFloorTileRef(col, row)
  return { sx: ref.sx, sy: ref.sy, tilesetIdx: ref.tilesetIdx }
}

// ---- Tile grid generation ----

export function createTileGrid(): TileType[][] {
  const layout = getLayoutSync()
  const grid: TileType[][] = []
  for (let r = 0; r < layout.rows; r++) {
    grid[r] = []
    for (let c = 0; c < layout.cols; c++) {
      const v = layout.tiles[r * layout.cols + c]
      grid[r][c] = v as TileType
    }
  }
  return grid
}

// ---- Furniture placements ----

export function createFurniturePlacements(): FurniturePlacement[] {
  const layout = getLayoutSync()
  const furniture: FurniturePlacement[] = []

  for (const f of layout.furniture) {
    for (const t of f.tiles) {
      const col = f.col + t.offsetCol
      const row = f.row + t.offsetRow
      // Check if this sub-tile is blocked
      const isBlocked = f.blockedOffsets.some(
        ([bc, br]) => bc === t.offsetCol && br === t.offsetRow
      )
      furniture.push({
        tile: { sx: t.sx, sy: t.sy, sw: t.sw ?? 1, sh: t.sh ?? 1, tilesetIdx: t.tilesetIdx },
        col,
        row,
        blocked: isBlocked,
      })
    }
  }

  return furniture
}

// ---- Seats (one per agent, next to desk) ----

export function createSeats(): Seat[] {
  const layout = getLayoutSync()
  const dirMap: Record<number, Direction> = {
    0: Direction.DOWN,
    1: Direction.UP,
    2: Direction.RIGHT,
    3: Direction.LEFT,
  }
  return layout.seats.map(s => ({
    id: s.id,
    seatCol: s.seatCol,
    seatRow: s.seatRow,
    facingDir: dirMap[s.facingDir] ?? Direction.UP,
  }))
}

// ---- Blocked tiles (from furniture) ----

export function getBlockedTiles(furniture: FurniturePlacement[]): Set<string> {
  const blocked = new Set<string>()
  for (const f of furniture) {
    if (f.blocked) {
      const w = f.tile.sw ?? 1
      const h = f.tile.sh ?? 1
      for (let dr = 0; dr < h; dr++) {
        for (let dc = 0; dc < w; dc++) {
          blocked.add(`${f.col + dc},${f.row + dr}`)
        }
      }
    }
  }
  return blocked
}

// ---- Room lookup ----

export function getRoomAt(col: number, row: number): RoomDef | null {
  const rc = layoutGetRoomAt(col, row)
  if (!rc) return null
  return toRoomDef(rc)
}

export function getFloorColor(col: number, row: number): string {
  return layoutGetFloorColor(col, row)
}

// Helper: pixel size of office (dynamic from layout)
export function getOfficeDimensions(): { cols: number; rows: number; widthPx: number; heightPx: number } {
  const layout = getLayoutSync()
  return {
    cols: layout.cols,
    rows: layout.rows,
    widthPx: layout.cols * TILE_SIZE,
    heightPx: layout.rows * TILE_SIZE,
  }
}

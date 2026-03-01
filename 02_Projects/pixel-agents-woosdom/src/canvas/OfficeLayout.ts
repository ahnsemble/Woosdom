import { TILE_SIZE } from '../constants.ts'
import { Direction, TileType } from './types.ts'
import type { RoomDef, Seat, FurniturePlacement } from './types.ts'
import { getLayoutSync } from '../config/LayoutLoader.ts'
import type { RoomConfig } from '../config/LayoutTypes.ts'

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

export function getRooms(): RoomDef[] {
  const layout = getLayoutSync()
  return layout.rooms.map(toRoomDef)
}

export function createTileGrid(): TileType[][] {
  const layout = getLayoutSync()
  const grid: TileType[][] = []
  for (let r = 0; r < layout.rows; r++) {
    grid[r] = []
    for (let c = 0; c < layout.cols; c++) {
      grid[r][c] = layout.tiles[r * layout.cols + c] as TileType
    }
  }
  return grid
}

export function createFurniturePlacements(): FurniturePlacement[] {
  const layout = getLayoutSync()
  const furniture: FurniturePlacement[] = []

  for (const f of layout.furniture) {
    for (const t of f.tiles) {
      const col = f.col + t.offsetCol
      const row = f.row + t.offsetRow
      const isBlocked = f.blockedOffsets.some(([bc, br]) => bc === t.offsetCol && br === t.offsetRow)
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

export function getBlockedTiles(furniture: FurniturePlacement[]): Set<string> {
  const blocked = new Set<string>()
  for (const f of furniture) {
    if (!f.blocked) continue
    const w = f.tile.sw ?? 1
    const h = f.tile.sh ?? 1
    for (let dr = 0; dr < h; dr++) {
      for (let dc = 0; dc < w; dc++) {
        blocked.add(`${f.col + dc},${f.row + dr}`)
      }
    }
  }
  return blocked
}

export function getOfficeDimensions(): { cols: number; rows: number; widthPx: number; heightPx: number } {
  const layout = getLayoutSync()
  return {
    cols: layout.cols,
    rows: layout.rows,
    widthPx: layout.cols * TILE_SIZE,
    heightPx: layout.rows * TILE_SIZE,
  }
}

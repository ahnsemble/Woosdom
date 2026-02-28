import type { TileType as TileTypeVal } from './types.ts'
import { TileType } from './types.ts'

/** BFS pathfinding on a 4-connected grid */
export function findPath(
  startCol: number, startRow: number,
  endCol: number, endRow: number,
  tileMap: TileTypeVal[][],
  blockedTiles: Set<string>,
): Array<{ col: number; row: number }> {
  if (startCol === endCol && startRow === endRow) return []

  const rows = tileMap.length
  const cols = tileMap[0]?.length ?? 0
  const dirs = [
    { dc: 0, dr: -1 },
    { dc: 0, dr: 1 },
    { dc: -1, dr: 0 },
    { dc: 1, dr: 0 },
  ]

  const visited = new Set<string>()
  const parent = new Map<string, string>()
  const queue: Array<{ col: number; row: number }> = []

  const startKey = `${startCol},${startRow}`
  const endKey = `${endCol},${endRow}`
  visited.add(startKey)
  queue.push({ col: startCol, row: startRow })

  while (queue.length > 0) {
    const current = queue.shift()!
    const currentKey = `${current.col},${current.row}`

    if (currentKey === endKey) {
      // Reconstruct path (excluding start, including end)
      const path: Array<{ col: number; row: number }> = []
      let key = endKey
      while (key !== startKey) {
        const [c, r] = key.split(',').map(Number)
        path.unshift({ col: c, row: r })
        key = parent.get(key)!
      }
      return path
    }

    for (const { dc, dr } of dirs) {
      const nc = current.col + dc
      const nr = current.row + dr
      const nKey = `${nc},${nr}`

      if (nc < 0 || nc >= cols || nr < 0 || nr >= rows) continue
      if (visited.has(nKey)) continue

      // Allow entering the final destination tile even if it's technically "blocked" by furniture (like a chair)
      const isTarget = (nc === endCol && nr === endRow)
      if (!isTarget && !isWalkable(nc, nr, tileMap, blockedTiles)) continue

      visited.add(nKey)
      parent.set(nKey, currentKey)
      queue.push({ col: nc, row: nr })
    }
  }

  return [] // No path found
}

function isWalkable(
  col: number, row: number,
  tileMap: TileTypeVal[][],
  blockedTiles: Set<string>,
): boolean {
  const tile = tileMap[row]?.[col]
  if (tile === undefined) return false
  if (tile === TileType.WALL || tile === TileType.VOID) return false
  if (blockedTiles.has(`${col},${row}`)) return false
  return true
}

/** Get all walkable tiles within a rectangular region */
export function getWalkableTilesInRegion(
  minCol: number, maxCol: number,
  minRow: number, maxRow: number,
  tileMap: TileTypeVal[][],
  blockedTiles: Set<string>,
): Array<{ col: number; row: number }> {
  const tiles: Array<{ col: number; row: number }> = []
  for (let r = minRow; r <= maxRow; r++) {
    for (let c = minCol; c <= maxCol; c++) {
      if (isWalkable(c, r, tileMap, blockedTiles)) {
        tiles.push({ col: c, row: r })
      }
    }
  }
  return tiles
}

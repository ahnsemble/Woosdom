import type { LayoutConfig, RoomConfig } from './LayoutTypes.ts'
import { VOID_TILE_COLOR } from '../constants.ts'

let layoutConfig: LayoutConfig | null = null

// Dev-only fallback: used when electronAPI is not available (browser preview).
const LAYOUT_FALLBACK_PATH = new URL('../../config/layout.json', import.meta.url).href

export async function loadLayout(): Promise<LayoutConfig> {
  if (layoutConfig) return layoutConfig

  const api = window.electronAPI
  if (api?.readLayout) {
    layoutConfig = await api.readLayout()
  } else {
    const resp = await fetch(LAYOUT_FALLBACK_PATH)
    layoutConfig = await resp.json()
  }
  return layoutConfig!
}

export function getLayoutSync(): LayoutConfig {
  if (!layoutConfig) throw new Error('Layout not loaded — call loadLayout() first')
  return layoutConfig
}

export function setLayout(config: LayoutConfig): void {
  layoutConfig = config
}

export function getRoomAt(col: number, row: number): RoomConfig | null {
  if (!layoutConfig) return null
  for (const room of layoutConfig.rooms) {
    if (col >= room.minCol && col <= room.maxCol && row >= room.minRow && row <= room.maxRow) {
      return room
    }
  }
  return null
}

export function getFloorColor(col: number, row: number): string {
  if (!layoutConfig) return VOID_TILE_COLOR
  const room = getRoomAt(col, row)
  if (room) return room.floorColor

  const h = layoutConfig.hallway
  if (row >= h.minRow && row <= h.maxRow && col >= h.minCol && col <= h.maxCol) {
    return h.floorColor
  }
  return VOID_TILE_COLOR
}

export function getFloorTileRef(col: number, row: number): { sx: number; sy: number; tilesetIdx?: number } {
  if (!layoutConfig) return { sx: 0, sy: 4 }

  const override = layoutConfig.tileOverrides?.[`${col},${row}`]
  if (override) return override

  const room = getRoomAt(col, row)
  let pattern: { sx: number; sy: number }[] | undefined

  if (room) {
    pattern = room.floorPattern
  } else {
    const h = layoutConfig.hallway
    if (row >= h.minRow && row <= h.maxRow && col >= h.minCol && col <= h.maxCol) {
      pattern = h.floorPattern
    }
  }

  if (!pattern || pattern.length === 0) return { sx: 0, sy: 4 }
  return pattern[(col + row) % pattern.length]
}

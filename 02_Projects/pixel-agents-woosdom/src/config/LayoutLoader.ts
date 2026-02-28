/**
 * layout.json 로딩 및 캐싱.
 * 렌더러 프로세스에서 사용.
 */
import type { LayoutConfig, RoomConfig } from './LayoutTypes.ts'

let layoutConfig: LayoutConfig | null = null

/** layout.json을 비동기 로드 (최초 1회) */
export async function loadLayout(): Promise<LayoutConfig> {
  if (layoutConfig) return layoutConfig

  // Electron IPC 사용 가능하면 파일시스템에서 읽기
  const api = (window as unknown as Record<string, unknown>).electronAPI as
    | { readLayout?: () => Promise<LayoutConfig> }
    | undefined
  if (api?.readLayout) {
    layoutConfig = await api.readLayout()
  } else {
    // fallback: Vite static import
    const resp = await fetch(new URL('../../config/layout.json', import.meta.url).href)
    layoutConfig = await resp.json()
  }
  return layoutConfig!
}

/** 동기 접근 (loadLayout 이후에만 사용) */
export function getLayoutSync(): LayoutConfig {
  if (!layoutConfig) throw new Error('Layout not loaded — call loadLayout() first')
  return layoutConfig
}

/** 레이아웃 핫 리로드 (커스터마이즈 모드에서 사용) */
export function setLayout(config: LayoutConfig): void {
  layoutConfig = config
}

/** 좌표가 속한 방 찾기 */
export function getRoomAt(col: number, row: number): RoomConfig | null {
  if (!layoutConfig) return null
  for (const room of layoutConfig.rooms) {
    if (col >= room.minCol && col <= room.maxCol &&
      row >= room.minRow && row <= room.maxRow) {
      return room
    }
  }
  return null
}

/** 좌표의 바닥 색상 반환 */
export function getFloorColor(col: number, row: number): string {
  if (!layoutConfig) return '#333'
  const room = getRoomAt(col, row)
  if (room) return room.floorColor

  const h = layoutConfig.hallway
  if (row >= h.minRow && row <= h.maxRow && col >= h.minCol && col <= h.maxCol) {
    return h.floorColor
  }
  return '#333'
}

/** 좌표의 바닥 타일 참조 반환 (per-tile override 우선, fallback: 체커보드) */
export function getFloorTileRef(col: number, row: number): { sx: number; sy: number; tilesetIdx?: number } {
  if (!layoutConfig) return { sx: 0, sy: 4 }

  // Per-tile sprite override (set by customize editor)
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

/** layout.json 스키마 타입 정의 */

export interface TileRef {
  sx: number  // tileset column (0-indexed)
  sy: number  // tileset row (0-indexed)
  tilesetIdx?: number
}

export interface RoomConfig {
  id: string
  label: string
  team: string
  minCol: number
  maxCol: number
  minRow: number
  maxRow: number
  floorColor: string
  floorPattern: TileRef[]  // 체커보드 패턴용 2+ 타일
}

export interface HallwayConfig {
  minCol: number
  maxCol: number
  minRow: number
  maxRow: number
  floorColor: string
  floorPattern: TileRef[]
}

export interface FurnitureTile {
  sx: number
  sy: number
  offsetCol: number
  offsetRow: number
  tilesetIdx?: number  // 0=tileset.png, 1=tileset2.png, 2+=vx_ace options
  sw?: number
  sh?: number
}

export interface FurnitureConfig {
  uid: string
  type: string
  col: number
  row: number
  tiles: FurnitureTile[]
  blockedOffsets: [number, number][]
}

export interface SeatConfig {
  id: string
  seatCol: number
  seatRow: number
  facingDir: number  // 0=DOWN, 1=UP, 2=RIGHT, 3=LEFT
}

export interface AgentConfig {
  id: number
  role: string
  displayName: string
  team: string
  room: string
  seatId: string
  spriteRow: number
  spriteCol: number
}

export interface WallTileConfig {
  tiles: TileRef[]
}

export interface LayoutConfig {
  version: number
  cols: number
  rows: number
  tiles: number[]            // flat array (cols*rows), 0=VOID, 1=FLOOR, 2=WALL
  rooms: RoomConfig[]
  hallway: HallwayConfig
  wallTiles: WallTileConfig
  furniture: FurnitureConfig[]
  seats: SeatConfig[]
  agents: AgentConfig[]
  tileOverrides?: Record<string, TileRef>  // "col,row" → sprite override
}

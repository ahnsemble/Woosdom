/** Tile types for the office grid */
export const TileType = {
  VOID: 0,
  FLOOR: 1,
  WALL: 2,
} as const
export type TileType = (typeof TileType)[keyof typeof TileType]

/** Character direction */
export const Direction = {
  DOWN: 0,
  UP: 1,
  RIGHT: 2,
  LEFT: 3,
} as const
export type Direction = (typeof Direction)[keyof typeof Direction]

/** Character FSM state */
export const CharacterState = {
  TYPE: 0,
  WALK: 1,
  IDLE: 2,
} as const
export type CharacterState = (typeof CharacterState)[keyof typeof CharacterState]

/** Agent team */
export const AgentTeam = {
  CC: 'cc',
  CODEX: 'codex',
  AG: 'ag',
  BRAIN: 'brain',
} as const
export type AgentTeam = (typeof AgentTeam)[keyof typeof AgentTeam]

/** Room definition with grid boundaries */
export interface RoomDef {
  id: string
  label: string
  team: AgentTeam
  minCol: number
  maxCol: number
  minRow: number
  maxRow: number
  floorColor: string
}

/** A tile coordinate reference into the tileset PNG */
export interface TileRef {
  /** Column in the tileset (0-indexed) */
  sx: number
  /** Row in the tileset (0-indexed) */
  sy: number
  /** Width in tiles (default 1) */
  sw?: number
  /** Height in tiles (default 1) */
  sh?: number
  /** Which tileset image to use: 0=tileset.png (default), 1=tileset2.png */
  tilesetIdx?: number
}

/** Furniture placed in the office */
export interface FurniturePlacement {
  tile: TileRef
  col: number
  row: number
  blocked?: boolean  // blocks pathfinding
}

/** Seat for an agent */
export interface Seat {
  id: string
  seatCol: number
  seatRow: number
  facingDir: Direction
}

/** Map Direction enum → RPG Maker sprite row within a character block */
export const DIRECTION_TO_SPRITE_ROW: Record<Direction, number> = {
  [Direction.DOWN]: 0,
  [Direction.LEFT]: 1,
  [Direction.RIGHT]: 2,
  [Direction.UP]: 3,
} as const

/** Walk animation frame cycle: stand → left-step → stand → right-step */
export const WALK_FRAME_SEQUENCE = [0, 1, 0, 2] as const

/** Bubble state text mapping */
export const BUBBLE_TEXT: Record<string, string> = {
  typing: '\uCF54\uB529 \uC911...',
  reading: '\uC77D\uB294 \uC911...',
  done: '\u2705',
  error: '\u274C',
  communicating: '\uD83D\uDCE1 \uBCF4\uACE0 \uC911...',
  meeting: '\uD83E\uDD1D \uD68C\uC758 \uC911...',
} as const

/** Bubble fade-out duration in seconds */
export const BUBBLE_FADE_SEC = 0.5

/** Character runtime state */
export interface Character {
  id: number
  role: string
  displayName: string
  team: AgentTeam
  room: string
  state: CharacterState
  dir: Direction
  x: number
  y: number
  tileCol: number
  tileRow: number
  path: Array<{ col: number; row: number }>
  moveProgress: number
  currentTool: string | null
  frame: number
  frameTimer: number
  wanderTimer: number
  wanderCount: number
  wanderLimit: number
  isActive: boolean
  seatId: string | null
  seatTimer: number
  bubbleType: 'typing' | 'reading' | 'done' | 'error' | 'communicating' | 'meeting' | null
  bubbleTimer: number
  spriteRow: number  // row in 32x32folk sprite sheet
  spriteCol: number  // column in 32x32folk sprite sheet
}

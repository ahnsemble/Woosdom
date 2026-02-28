/** Tile size in pixels (Donarg 16x16) */
export const TILE_SIZE = 16

/** Canvas zoom level (integer for pixel-perfect rendering) */
export const DEFAULT_ZOOM = 3

/** Max delta time to prevent physics jumps */
export const MAX_DELTA_TIME_SEC = 0.1

/** Character movement */
export const WALK_SPEED_PX_PER_SEC = 48
export const WALK_FRAME_DURATION_SEC = 0.15
export const TYPE_FRAME_DURATION_SEC = 0.3

/** Sitting Y offset in pixels (character shifts down when seated at desk) */
export const SITTING_OFFSET_PX = 6

/** Wandering behavior */
export const WANDER_PAUSE_MIN_SEC = 1.5
export const WANDER_PAUSE_MAX_SEC = 3.0
export const WANDER_MOVES_BEFORE_REST_MIN = 2
export const WANDER_MOVES_BEFORE_REST_MAX = 5
export const SEAT_REST_MIN_SEC = 0.5
export const SEAT_REST_MAX_SEC = 2.0

/** Office grid dimensions (legacy — prefer getOfficeDimensions() from OfficeLayout.ts) */
export const OFFICE_COLS = 52
export const OFFICE_ROWS = 35

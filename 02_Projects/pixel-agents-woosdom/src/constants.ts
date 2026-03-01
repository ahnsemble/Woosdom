/** Tile size in pixels (Donarg 16x16) */
export const TILE_SIZE = 16

/** Canvas zoom level (integer for pixel-perfect rendering) */
export const DEFAULT_ZOOM = 3

/** Max delta time to prevent physics jumps */
export const MAX_DELTA_TIME_SEC = 0.1

/** Event log dedup window in milliseconds */
export const EVENT_DEDUP_WINDOW_MS = 10_000

/** Base color for tiles outside rooms/hallways */
export const VOID_TILE_COLOR = '#2a2a3e'

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

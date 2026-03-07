extends Node

# Global Constants
const TILE_SIZE: float = 1.0
const CHUNK_WIDTH: int = 9 # -4 to +4
const FORWARD_DIRECTION: Vector3 = Vector3(0, 0, -1)
const BACKWARD_DIRECTION: Vector3 = Vector3(0, 0, 1)
const LEFT_DIRECTION: Vector3 = Vector3(-1, 0, 0)
const RIGHT_DIRECTION: Vector3 = Vector3(1, 0, 0)

# Layers (Collision)
const LAYER_PLAYER: int = 1
const LAYER_OBSTACLE: int = 2 # Cars, Trains, Trees
const LAYER_LOG: int = 4
const LAYER_WATER: int = 8
const LAYER_COIN: int = 16
const LAYER_XP: int = 32
const LAYER_ICE: int = 64
const LAYER_CONVEYOR: int = 128

const XP_PER_LEVEL: Array[int] = [10, 15, 20, 30, 40, 50, 60, 80, 100, 130]

# Enums
enum LaneType {
	GRASS,
	ROAD,
	RIVER,
	TRAIN,
	ICE,
	CONVEYOR
}

enum GameState {
	MENU,
	PLAYING,
	GAME_OVER
}

static func get_difficulty_multiplier(score: int) -> float:
	# S-Curve: 0~200 완만, 200~500 급등, 500+ 수렴 (max 1.35)
	var t := clampf(float(score) / 500.0, 0.0, 1.0)
	return 1.0 + 0.35 * (3.0 * t * t - 2.0 * t * t * t)

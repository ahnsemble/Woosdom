extends Node3D
class_name ChunkBase

@export var type: Global.LaneType = Global.LaneType.GRASS
@export var coin_scene: PackedScene = preload("res://scenes/objects/coin.tscn")
@export var xp_orb_scene: PackedScene = preload("res://scenes/objects/xp_orb.tscn")

const COIN_SPAWN_CHANCE: float = 0.3
const XP_ORB_CHANCE_MIN: float = 0.3
const XP_ORB_CHANCE_MAX: float = 0.5

func setup(z_index: int) -> void:
	position.z = z_index * -Global.TILE_SIZE
	name = "Chunk_" + str(z_index)
	_try_spawn_coin()
	_try_spawn_xp_orb()

	# Apply Difficulty
	for child in get_children():
		if child.has_method("apply_difficulty"):
			child.call("apply_difficulty", GameManager.current_score)

func _can_spawn_pickups() -> bool:
	return type == Global.LaneType.GRASS or type == Global.LaneType.ROAD or type == Global.LaneType.ICE or type == Global.LaneType.CONVEYOR

func _try_spawn_coin() -> void:
	if not _can_spawn_pickups():
		return
	if not coin_scene:
		return
	if randf() > COIN_SPAWN_CHANCE:
		return

	var coin = coin_scene.instantiate()
	add_child(coin)
	coin.position = Vector3(randi_range(-3, 3), 0.5, 0)

func _try_spawn_xp_orb() -> void:
	if not _can_spawn_pickups():
		return
	if not xp_orb_scene:
		return

	var spawn_chance := randf_range(XP_ORB_CHANCE_MIN, XP_ORB_CHANCE_MAX)
	if randf() > spawn_chance:
		return

	var xp_orb = xp_orb_scene.instantiate()
	add_child(xp_orb)
	xp_orb.position = Vector3(randi_range(-3, 3), 0.45, 0)

func _on_screen_exited() -> void:
	# Called when chunk goes behind the camera
	pass

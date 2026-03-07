extends Node
class_name ChunkManager

@export var player_path: NodePath
@export var chunk_holder_path: NodePath

@export var chunk_grass_scene: PackedScene = preload("res://scenes/chunks/chunk_grass.tscn")
@export var chunk_road_scene: PackedScene = preload("res://scenes/chunks/chunk_road.tscn")
@export var chunk_river_scene: PackedScene = preload("res://scenes/chunks/chunk_river.tscn")
@export var chunk_train_scene: PackedScene = preload("res://scenes/chunks/chunk_train.tscn")
@export var chunk_ice_scene: PackedScene = preload("res://scenes/chunks/chunk_ice.tscn")
@export var chunk_conveyor_scene: PackedScene = preload("res://scenes/chunks/chunk_conveyor.tscn")

var player: Node3D
var chunk_holder: Node3D

var current_z_index: int = 0
var active_chunks: Array[ChunkBase] = []
var chunk_history: Array[int] = [] # For avoiding repetition

const VIEW_DISTANCE: int = 20
const BACK_REMOVE_DISTANCE: int = 10

func _ready() -> void:
	# 직접 경로 참조 (export NodePath 로딩 불안정 우회)
	player = get_node_or_null("../Player")
	chunk_holder = get_node_or_null("../ChunkHolder")
	if not chunk_holder:
		push_error("ChunkHolder not found!")
		return

	GameManager.connect("game_restarted", _on_game_restarted)
	_spawn_initial_chunks()

func _spawn_initial_chunks() -> void:
	for chunk in active_chunks:
		if is_instance_valid(chunk):
			chunk.queue_free()

	active_chunks.clear()
	chunk_history.clear()
	current_z_index = 0

	for i in range(-5, VIEW_DISTANCE):
		spawn_chunk(i)
	current_z_index = VIEW_DISTANCE

func _process(_delta: float) -> void:
	if not is_instance_valid(player):
		return

	var player_z_index = int(round(abs(player.position.z) / Global.TILE_SIZE))

	# Spawn ahead
	while current_z_index < player_z_index + VIEW_DISTANCE:
		spawn_chunk(current_z_index)
		current_z_index += 1

	# Despawn behind
	while active_chunks.size() > 0:
		var first_chunk = active_chunks[0]
		if abs(first_chunk.position.z) < float(player_z_index - BACK_REMOVE_DISTANCE) * Global.TILE_SIZE:
			active_chunks.pop_front().queue_free()
		else:
			break

func _on_game_restarted() -> void:
	_spawn_initial_chunks()

func spawn_chunk(z_index: int) -> void:
	var type = _pick_next_chunk_type()
	var scene = _get_scene_for_type(type)

	if scene:
		var chunk = scene.instantiate() as ChunkBase
		chunk_holder.add_child(chunk)
		chunk.setup(z_index)
		active_chunks.append(chunk)

func _pick_next_chunk_type() -> Global.LaneType:
	# Avoid 3 same in a row
	var last_type = -1
	var last_count = 0

	if chunk_history.size() > 0:
		last_type = chunk_history.back()
		for i in range(chunk_history.size() - 1, -1, -1):
			if chunk_history[i] == last_type:
				last_count += 1
			else:
				break

	var weights = {
		Global.LaneType.GRASS: 30,
		Global.LaneType.ROAD: 25,
		Global.LaneType.RIVER: 20,
		Global.LaneType.TRAIN: 10,
		Global.LaneType.ICE: 15,
		Global.LaneType.CONVEYOR: 10
	}

	# Adjust weights based on history
	if last_count >= 3 and weights.has(last_type):
		weights[last_type] = 0

	# Safe start
	if current_z_index < 5:
		return Global.LaneType.GRASS

	return _weighted_random(weights)

func _weighted_random(weights: Dictionary) -> Global.LaneType:
	var total_weight := 0
	for w in weights.values():
		total_weight += int(w)

	if total_weight <= 0:
		return Global.LaneType.GRASS

	var roll = randi() % total_weight
	var current = 0
	for type in weights.keys():
		current += int(weights[type])
		if roll < current:
			chunk_history.append(int(type))
			if chunk_history.size() > 10:
				chunk_history.pop_front()
			return type

	return Global.LaneType.GRASS

func _get_scene_for_type(type: Global.LaneType) -> PackedScene:
	match type:
		Global.LaneType.GRASS:
			return chunk_grass_scene
		Global.LaneType.ROAD:
			return chunk_road_scene
		Global.LaneType.RIVER:
			return chunk_river_scene
		Global.LaneType.TRAIN:
			return chunk_train_scene
		Global.LaneType.ICE:
			return chunk_ice_scene
		Global.LaneType.CONVEYOR:
			return chunk_conveyor_scene
	return chunk_grass_scene

extends Node3D
class_name LaneMover

enum Direction { LEFT, RIGHT }

@export var direction: Direction = Direction.RIGHT
@export var speed: float = 2.0
@export var spawn_rate: float = 2.0
@export var object_scene: PackedScene

var timer: float = 0.0
var spawn_x: float = 10.0
var despawn_x: float = -10.0
var move_dir: Vector3

var base_speed: float = 2.0
var base_spawn_rate: float = 2.0

var pool: ObjectPool

func _ready() -> void:
	base_speed = speed
	base_spawn_rate = spawn_rate
	_sync_direction()
	pool = ObjectPool.new(self)

func _sync_direction() -> void:
	if direction == Direction.RIGHT:
		move_dir = Vector3(1, 0, 0)
		spawn_x = -6.0
		despawn_x = 6.0
	else:
		move_dir = Vector3(-1, 0, 0)
		spawn_x = 6.0
		despawn_x = -6.0

func set_direction(new_direction: Direction) -> void:
	direction = new_direction
	_sync_direction()

func apply_difficulty(player_score: int) -> void:
	var multiplier := Global.get_difficulty_multiplier(player_score)
	speed = base_speed * multiplier
	spawn_rate = max(0.4, base_spawn_rate / multiplier)

func _process(delta: float) -> void:
	# Move children
	for child in get_children():
		if child is Area3D: # Assuming cars/logs are Area3D
			child.position += move_dir * speed * delta

			if (direction == Direction.RIGHT and child.position.x > despawn_x) or 			   (direction == Direction.LEFT and child.position.x < despawn_x):
				pool.return_object(child, object_scene.resource_path)

	# Spawn
	timer -= delta
	if timer <= 0:
		spawn_object()
		timer = max(0.25, spawn_rate + randf_range(-0.35, 0.35))

func spawn_object() -> void:
	if not object_scene:
		return

	var obj = pool.get_object(object_scene.resource_path)
	obj.position = Vector3(spawn_x, 0.5, 0)

	# Rotate if needed
	if direction == Direction.LEFT:
		obj.rotation_degrees.y = 180
	else:
		obj.rotation_degrees.y = 0

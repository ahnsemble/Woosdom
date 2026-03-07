extends Area3D
class_name XPOrb

@export var value: int = 1
var is_collected: bool = false

func _ready() -> void:
	add_to_group("magnet_collectible")

func _process(delta: float) -> void:
	rotation.y += 2.0 * delta

func magnet_to(target_position: Vector3, delta: float) -> void:
	global_position = global_position.move_toward(target_position, 8.0 * delta)

func collect() -> void:
	if is_collected:
		return
	is_collected = true
	GameManager.add_xp(value)
	queue_free()

func reset() -> void:
	visible = true
	set_process(true)
	is_collected = false

extends ChunkBase
class_name ChunkConveyor

@export var belt_speed: float = 1.25
@export var move_right: bool = true

@onready var conveyor_area: Area3D = $ConveyorArea
var player: PlayerController

func _ready() -> void:
	player = get_tree().get_root().get_node_or_null("Main/Player") as PlayerController

func setup(z_index: int) -> void:
	move_right = randf() >= 0.5
	super.setup(z_index)
	var mover := get_node_or_null("LaneMover") as LaneMover
	if mover:
		mover.set_direction(LaneMover.Direction.RIGHT if move_right else LaneMover.Direction.LEFT)

func _process(delta: float) -> void:
	if GameManager.current_state != Global.GameState.PLAYING:
		return
	if not is_instance_valid(player) or player.is_dead:
		return
	if not conveyor_area:
		return

	if conveyor_area.overlaps_area(player):
		var dir := 1.0 if move_right else -1.0
		var next_pos := player.global_position
		next_pos.x = clampf(next_pos.x + dir * belt_speed * delta, -4.0, 4.0)
		player.global_position = next_pos

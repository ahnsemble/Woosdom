extends Node3D

@export var train_scene: PackedScene
@export var warning_light: Node3D
@export var base_warning_duration: float = 1.5

var timer: float = 0.0
var is_active: bool = false
var has_spawned_train: bool = false

func _ready() -> void:
	if warning_light:
		warning_light.visible = false
	GameManager.connect("game_restarted", _on_game_restarted)
	_start_cycle()

func _start_cycle() -> void:
	var difficulty := Global.get_difficulty_multiplier(GameManager.current_score)
	timer = randf_range(2.0, 5.0) / difficulty
	is_active = false
	has_spawned_train = false

func _get_warning_duration() -> float:
	var duration := base_warning_duration
	if SkillManager.has_skill("eagle_eye"):
		duration += 1.0
	return duration

func _process(delta: float) -> void:
	if GameManager.current_state != Global.GameState.PLAYING:
		return

	timer -= delta

	if not is_active:
		if timer <= 0:
			# Start Warning
			is_active = true
			if warning_light:
				warning_light.visible = true
			timer = _get_warning_duration()
	else:
		if timer <= 0 and not has_spawned_train:
			_spawn_train()
			has_spawned_train = true
			timer = 0.6
		elif has_spawned_train and timer <= 0:
			# Reset
			if warning_light:
				warning_light.visible = false
			_start_cycle()

func _spawn_train() -> void:
	if not train_scene:
		return

	var train = train_scene.instantiate()
	add_child(train)
	train.position = Vector3(-10, 0.5, 0)

	var run_duration: float = max(0.9, 1.5 / Global.get_difficulty_multiplier(GameManager.current_score))
	var tween = create_tween()
	tween.tween_property(train, "position:x", 10.0, run_duration)
	tween.tween_callback(train.queue_free)

func _on_game_restarted() -> void:
	for child in get_children():
		if child is Area3D:
			child.queue_free()
	if warning_light:
		warning_light.visible = false
	_start_cycle()

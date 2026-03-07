extends Area3D
class_name PlayerController

signal player_moved(new_pos: Vector3)
signal player_died(reason: String)

# Movement Settings
@export var move_speed: float = 0.1 # Seconds per tile
@export var jump_height: float = 0.5
@export var dash_cooldown: float = 3.0
@export var magnet_range: float = 3.0
@export var magnet_pull_speed: float = 8.0

# Components
@onready var visual: Node3D = $Visual
@onready var ray_front: RayCast3D = $RayFront
@onready var ray_back: RayCast3D = $RayBack
@onready var ray_left: RayCast3D = $RayLeft
@onready var ray_right: RayCast3D = $RayRight

# State
var is_moving: bool = false
var can_dash: bool = true
var dash_timer: float = 0.0
var is_dead: bool = false
var bulldozer_step_counter: int = 0
var queued_slide_direction: Vector3 = Vector3.ZERO
var slide_queued: bool = false

# Input
var touch_start_pos: Vector2
var touch_time: float = 0.0
const SWIPE_THRESHOLD: float = 50.0
const TAP_THRESHOLD_TIME: float = 0.2

var last_tap_time: float = 0.0
const DOUBLE_TAP_TIME: float = 0.25

func _ready() -> void:
	# Snap to grid
	position = position.round()
	GameManager.connect("game_restarted", _on_game_restarted)

	var callback := Callable(self, "_on_area_entered")
	if not area_entered.is_connected(callback):
		area_entered.connect(callback)

func _process(delta: float) -> void:
	if not can_dash:
		dash_timer -= delta
		if dash_timer <= 0:
			can_dash = true

	if GameManager.current_state == Global.GameState.PLAYING and SkillManager.has_skill("coin_magnet"):
		_apply_coin_magnet(delta)

func _unhandled_input(event: InputEvent) -> void:
	if GameManager.current_state == Global.GameState.GAME_OVER:
		return

	if is_moving or is_dead:
		return

	# First input starts the game (Crossy Road style)
	if GameManager.current_state == Global.GameState.MENU:
		GameManager.start_game()

	# Keyboard input (desktop)
	if event is InputEventKey and event.pressed and not event.echo:
		if Input.is_action_just_pressed("move_forward"):
			move(Global.FORWARD_DIRECTION)
			return
		elif Input.is_action_just_pressed("move_backward"):
			move(Global.BACKWARD_DIRECTION)
			return
		elif Input.is_action_just_pressed("move_left"):
			move(Global.LEFT_DIRECTION)
			return
		elif Input.is_action_just_pressed("move_right"):
			move(Global.RIGHT_DIRECTION)
			return
		elif Input.is_action_just_pressed("dash") and can_dash:
			move(Global.FORWARD_DIRECTION, 2)
			can_dash = false
			dash_timer = dash_cooldown
			return

	# Touch input (mobile)
	if event is InputEventScreenTouch:
		if event.pressed:
			touch_start_pos = event.position
			touch_time = Time.get_ticks_msec() / 1000.0
		else:
			var touch_end_pos = event.position
			var touch_duration = (Time.get_ticks_msec() / 1000.0) - touch_time
			var drag_vector = touch_end_pos - touch_start_pos

			if drag_vector.length() < SWIPE_THRESHOLD and touch_duration < TAP_THRESHOLD_TIME:
				# TAP
				_handle_tap()
			else:
				# SWIPE
				_handle_swipe(drag_vector)

func _handle_tap() -> void:
	var current_time = Time.get_ticks_msec() / 1000.0
	if current_time - last_tap_time < DOUBLE_TAP_TIME and can_dash:
		# Double Tap -> Dash
		move(Global.FORWARD_DIRECTION, 2)
		can_dash = false
		dash_timer = dash_cooldown
	else:
		# Single Tap -> Hop Forward
		move(Global.FORWARD_DIRECTION)

	last_tap_time = current_time

func _handle_swipe(vector: Vector2) -> void:
	if abs(vector.x) > abs(vector.y):
		if vector.x > 0:
			move(Global.RIGHT_DIRECTION)
		else:
			move(Global.LEFT_DIRECTION)
	else:
		if vector.y > 0:
			move(Global.BACKWARD_DIRECTION)
		else:
			move(Global.FORWARD_DIRECTION)

func move(direction: Vector3, steps: int = 1, from_ice_slide: bool = false) -> void:
	if is_moving or is_dead:
		return

	# Raycast check for blocking obstacles
	var target_pos = position + direction * steps * Global.TILE_SIZE
	var ray = _get_ray_for_direction(direction)
	if ray:
		ray.force_raycast_update()
		if ray.is_colliding():
			var collider = ray.get_collider()
			if collider is CollisionObject3D:
				var obstacle := collider as CollisionObject3D
				if (obstacle.collision_layer & Global.LAYER_OBSTACLE) != 0:
					return

	is_moving = true

	# Tween Movement
	var tween = create_tween()
	tween.set_trans(Tween.TRANS_SINE)
	tween.set_ease(Tween.EASE_OUT)

	# Jump arc
	tween.tween_property(visual, "position:y", jump_height, move_speed * 0.5)
	tween.parallel().tween_property(self, "position", target_pos, move_speed)
	tween.tween_property(visual, "position:y", 0.0, move_speed * 0.5)

	# Squash/Stretch
	tween.parallel().tween_property(visual, "scale", Vector3(1.2, 0.8, 1.2), move_speed * 0.5)
	tween.tween_property(visual, "scale", Vector3(1.0, 1.0, 1.0), move_speed * 0.5)

	await tween.finished
	is_moving = false

	GameManager.update_score(int(round(position.z)))
	emit_signal("player_moved", position)

	var landing := _check_landing()
	if is_dead:
		return

	if SkillManager.has_skill("bulldozer"):
		bulldozer_step_counter += steps
		if bulldozer_step_counter >= 10:
			bulldozer_step_counter = 0
			_try_bulldoze()

	if bool(landing.get("on_ice", false)) and not from_ice_slide:
		queued_slide_direction = direction
		slide_queued = true
		call_deferred("_execute_ice_slide")

func _execute_ice_slide() -> void:
	if not slide_queued:
		return
	if is_dead or is_moving:
		return
	slide_queued = false
	move(queued_slide_direction, 1, true)

func _get_ray_for_direction(dir: Vector3) -> RayCast3D:
	if dir == Global.FORWARD_DIRECTION:
		return ray_front
	if dir == Global.BACKWARD_DIRECTION:
		return ray_back
	if dir == Global.LEFT_DIRECTION:
		return ray_left
	if dir == Global.RIGHT_DIRECTION:
		return ray_right
	return null

func _check_landing() -> Dictionary:
	var areas = get_overlapping_areas()
	var on_log = false
	var in_water = false
	var on_ice = false

	for area in areas:
		if (area.collision_layer & Global.LAYER_LOG) != 0:
			on_log = true
		elif (area.collision_layer & Global.LAYER_WATER) != 0:
			in_water = true
		elif (area.collision_layer & Global.LAYER_COIN) != 0:
			if area.has_method("collect"):
				area.call("collect")
		elif (area.collision_layer & Global.LAYER_XP) != 0:
			if area.has_method("collect"):
				area.call("collect")
		elif (area.collision_layer & Global.LAYER_ICE) != 0:
			on_ice = true

	if in_water and not on_log:
		die("river")

	return {
		"on_log": on_log,
		"in_water": in_water,
		"on_ice": on_ice
	}

func _on_area_entered(area: Area3D) -> void:
	if is_dead:
		return

	if (area.collision_layer & Global.LAYER_OBSTACLE) != 0:
		die("hit")
		return

	if (area.collision_layer & Global.LAYER_COIN) != 0 or (area.collision_layer & Global.LAYER_XP) != 0:
		if area.has_method("collect"):
			area.call("collect")

func _apply_coin_magnet(delta: float) -> void:
	for item in get_tree().get_nodes_in_group("magnet_collectible"):
		if not (item is Area3D):
			continue

		var area := item as Area3D
		if not is_instance_valid(area):
			continue

		var distance := global_position.distance_to(area.global_position)
		if distance > magnet_range:
			continue

		if area.has_method("magnet_to"):
			area.call("magnet_to", global_position, delta)
		else:
			area.global_position = area.global_position.move_toward(global_position, magnet_pull_speed * delta)

		if distance < 0.45 and area.has_method("collect"):
			area.call("collect")

func _try_bulldoze() -> void:
	if not ray_front:
		return

	ray_front.force_raycast_update()
	if not ray_front.is_colliding():
		return

	var collider = ray_front.get_collider()
	if collider is CollisionObject3D:
		var obstacle := collider as CollisionObject3D
		if (obstacle.collision_layer & Global.LAYER_OBSTACLE) != 0:
			obstacle.queue_free()

func die(reason: String) -> void:
	if is_dead:
		return

	if reason == "hit" and SkillManager.consume_shield():
		return

	is_dead = true
	is_moving = false
	emit_signal("player_died", reason)
	GameManager._on_player_died(reason)

	# Hide instead of queue_free — we need this node for restart
	visual.visible = false
	set_process(false)
	set_physics_process(false)

func reset() -> void:
	# Called on game restart to reset player state.
	position = Vector3(0, 0, 0)
	is_moving = false
	is_dead = false
	can_dash = true
	dash_timer = 0.0
	bulldozer_step_counter = 0
	slide_queued = false
	queued_slide_direction = Vector3.ZERO
	visual.visible = true
	visual.position = Vector3.ZERO
	visual.scale = Vector3.ONE
	set_process(true)
	set_physics_process(true)

func _on_game_restarted() -> void:
	reset()

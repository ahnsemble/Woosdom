extends Camera3D

@export var target_path: NodePath
@export var follow_speed: float = 2.0
@export var offset: Vector3 = Vector3(0, 10, 10) # Isometic view offset
@export var min_scroll_speed: float = 0.3  # 최소 전진 속도 (독수리 대체)
@export var death_distance: float = 8.0    # 카메라 뒤 이 거리 이상이면 사망

var target: Node3D
var furthest_z: float = 0.0  # 카메라가 도달한 가장 앞쪽 Z

func _ready() -> void:
	target = get_node_or_null("../Player")
	if target:
		position = target.position + offset
		look_at(target.position, Vector3.UP)
	GameManager.connect("game_restarted", _on_game_restarted)

func _process(delta: float) -> void:
	if GameManager.current_state != Global.GameState.PLAYING:
		return
	
	# 최소 전진 속도 적용 (독수리 역할)
	furthest_z -= min_scroll_speed * delta
	
	# 플레이어가 더 앞에 있으면 카메라도 따라감
	if is_instance_valid(target):
		if target.position.z < furthest_z:
			furthest_z = target.position.z
	
	# 카메라 위치 보간
	var target_x = 0.0
	if is_instance_valid(target):
		target_x = target.position.x
	
	var new_x = lerp(position.x - offset.x, target_x, follow_speed * delta)
	var new_z = lerp(position.z - offset.z, furthest_z, follow_speed * delta)
	
	position.x = new_x + offset.x
	position.z = new_z + offset.z
	
	# 스크롤 아웃 사망 체크: 플레이어가 카메라 기준점보다 너무 뒤에 있으면 사망
	if is_instance_valid(target):
		var distance_behind = target.position.z - furthest_z  # 양수면 뒤처짐
		if distance_behind > death_distance:
			target.call("die", "scroll")


func _on_game_restarted() -> void:
	target = get_node_or_null("../Player")
	furthest_z = 0.0
	if target:
		position = target.position + offset

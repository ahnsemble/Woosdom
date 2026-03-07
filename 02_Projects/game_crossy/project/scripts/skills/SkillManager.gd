extends Node

signal skills_changed(active_skills: Array[String])
signal skill_applied(skill_id: String)

var active_skills: Array[String] = []
var skill_pool: Array[Dictionary] = [
	{
		"id": "shield",
		"name": "Shield",
		"category": "Defense",
		"description": "1회 피격 무효화"
	},
	{
		"id": "coin_magnet",
		"name": "Coin Magnet",
		"category": "Economy",
		"description": "3타일 내 코인/XP 자동 수집"
	},
	{
		"id": "bulldozer",
		"name": "Bulldozer",
		"category": "Attack",
		"description": "10칸마다 전방 장애물 1개 파괴"
	},
	{
		"id": "eagle_eye",
		"name": "Eagle Eye",
		"category": "Defense",
		"description": "기차 경고 시간 +1.0초"
	}
]

func _ready() -> void:
	randomize()
	emit_signal("skills_changed", active_skills.duplicate())

func get_random_choices(count: int = 3) -> Array[Dictionary]:
	var available: Array[Dictionary] = []
	for skill in skill_pool:
		if not active_skills.has(skill["id"]):
			available.append(skill)

	available.shuffle()
	return available.slice(0, min(count, available.size()))

func apply_skill(skill_id: String) -> void:
	if active_skills.has(skill_id):
		return

	var skill_data := get_skill_data(skill_id)
	if skill_data.is_empty():
		return

	active_skills.append(skill_id)
	emit_signal("skill_applied", skill_id)
	emit_signal("skills_changed", active_skills.duplicate())

func has_skill(skill_id: String) -> bool:
	return active_skills.has(skill_id)

func consume_shield() -> bool:
	if not active_skills.has("shield"):
		return false

	active_skills.erase("shield")
	emit_signal("skills_changed", active_skills.duplicate())
	return true

func clear_skills() -> void:
	active_skills.clear()
	emit_signal("skills_changed", active_skills.duplicate())

func get_skill_data(skill_id: String) -> Dictionary:
	for skill in skill_pool:
		if skill["id"] == skill_id:
			return skill
	return {}

func get_active_skill_names() -> Array[String]:
	var names: Array[String] = []
	for skill_id in active_skills:
		var data := get_skill_data(skill_id)
		if data.has("name"):
			names.append(str(data["name"]))
		else:
			names.append(skill_id)
	return names

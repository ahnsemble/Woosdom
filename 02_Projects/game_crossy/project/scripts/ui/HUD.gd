extends CanvasLayer

@onready var score_label: Label = $Control/ScoreLabel
@onready var coin_label: Label = $Control/CoinLabel
@onready var level_label: Label = $Control/LevelLabel
@onready var xp_bar: ProgressBar = $Control/XPBar
@onready var xp_label: Label = $Control/XPLabel
@onready var skills_bar: HBoxContainer = $Control/SkillsBar

func _ready() -> void:
	GameManager.connect("score_updated", _on_score_updated)
	GameManager.connect("coins_updated", _on_coins_updated)
	GameManager.connect("xp_updated", _on_xp_updated)
	SkillManager.connect("skills_changed", _on_skills_changed)

	_on_score_updated(GameManager.current_score)
	_on_coins_updated(GameManager.total_coins)
	_on_xp_updated(GameManager.current_xp, _get_xp_to_next_level(), GameManager.current_level)
	_on_skills_changed(SkillManager.active_skills)

func _get_xp_to_next_level() -> int:
	if GameManager.current_level >= Global.XP_PER_LEVEL.size():
		return Global.XP_PER_LEVEL[Global.XP_PER_LEVEL.size() - 1]
	return Global.XP_PER_LEVEL[GameManager.current_level]

func _on_score_updated(new_score: int) -> void:
	score_label.text = str(new_score)

func _on_coins_updated(new_total: int) -> void:
	coin_label.text = "🪙 " + str(new_total)

func _on_xp_updated(current_xp: int, xp_to_next: int, current_level: int) -> void:
	level_label.text = "Lv." + str(current_level)
	xp_bar.max_value = max(1, xp_to_next)
	xp_bar.value = min(current_xp, xp_to_next)
	xp_label.text = str(current_xp) + "/" + str(xp_to_next) + " XP"

func _on_skills_changed(active_skill_ids: Array[String]) -> void:
	for child in skills_bar.get_children():
		child.queue_free()

	if active_skill_ids.is_empty():
		var empty_label := Label.new()
		empty_label.text = "No Skills"
		empty_label.modulate = Color(0.85, 0.85, 0.85, 1.0)
		skills_bar.add_child(empty_label)
		return

	for skill_id in active_skill_ids:
		var skill_data := SkillManager.get_skill_data(skill_id)
		var tag := Label.new()
		tag.text = str(skill_data.get("name", skill_id))
		tag.modulate = Color(0.95, 0.95, 1.0, 1.0)
		skills_bar.add_child(tag)

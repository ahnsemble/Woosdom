extends CanvasLayer

@onready var panel: PanelContainer = $Root/Panel
@onready var score_label: Label = $Root/Panel/VBox/ScoreLabel
@onready var best_label: Label = $Root/Panel/VBox/BestLabel
@onready var level_label: Label = $Root/Panel/VBox/LevelLabel
@onready var skills_label: Label = $Root/Panel/VBox/SkillsLabel
@onready var retry_button: Button = $Root/Panel/VBox/RetryButton

func _ready() -> void:
	panel.visible = false
	process_mode = Node.PROCESS_MODE_ALWAYS
	GameManager.connect("game_over", _on_game_over)
	GameManager.connect("game_restarted", _on_game_restarted)
	retry_button.pressed.connect(_on_retry_pressed)

func _on_game_over(final_score: int, high_score: int) -> void:
	panel.visible = true
	score_label.text = "Score: " + str(final_score)
	best_label.text = "Best: " + str(high_score)
	level_label.text = "Level: " + str(GameManager.current_level)

	var names := SkillManager.get_active_skill_names()
	if names.is_empty():
		skills_label.text = "Skills: -"
	else:
		var merged := ""
		for i in range(names.size()):
			if i > 0:
				merged += ", "
			merged += names[i]
		skills_label.text = "Skills: " + merged

func _on_retry_pressed() -> void:
	panel.visible = false
	get_tree().paused = false
	SkillManager.clear_skills()
	GameManager.start_game()

func _on_game_restarted() -> void:
	panel.visible = false

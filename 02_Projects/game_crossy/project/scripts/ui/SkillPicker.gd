extends CanvasLayer

@onready var cards: Array[VBoxContainer] = [
	$Root/Panel/VBox/Choices/Card1,
	$Root/Panel/VBox/Choices/Card2,
	$Root/Panel/VBox/Choices/Card3
]

func _ready() -> void:
	visible = false
	process_mode = Node.PROCESS_MODE_ALWAYS
	GameManager.connect("level_up", _on_level_up)

	for card in cards:
		var button := card.get_node("PickButton") as Button
		button.pressed.connect(_on_pick_pressed.bind(button))

func _on_level_up(_new_level: int) -> void:
	var choices := SkillManager.get_random_choices(3)
	if choices.is_empty():
		return
	show_choices(choices)

func show_choices(choices: Array[Dictionary]) -> void:
	visible = true
	get_tree().paused = true

	for i in range(cards.size()):
		var card = cards[i]
		if i >= choices.size():
			card.visible = false
			continue

		card.visible = true
		var choice: Dictionary = choices[i]
		var name_label := card.get_node("Name") as Label
		var desc_label := card.get_node("Desc") as Label
		var pick_button := card.get_node("PickButton") as Button

		name_label.text = str(choice.get("name", "Unknown"))
		desc_label.text = str(choice.get("description", ""))
		pick_button.set_meta("skill_id", str(choice.get("id", "")))
		pick_button.text = "Select"

func _on_pick_pressed(button: Button) -> void:
	if not button.has_meta("skill_id"):
		return

	var skill_id := str(button.get_meta("skill_id"))
	if skill_id == "":
		return

	SkillManager.apply_skill(skill_id)
	hide_picker()

func hide_picker() -> void:
	get_tree().paused = false
	visible = false

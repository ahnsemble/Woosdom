extends Node

signal score_updated(new_score: int)
signal game_over(final_score: int, high_score: int)
signal game_restarted
signal coins_updated(new_total: int)
signal level_up(new_level: int)
signal xp_updated(current_xp: int, xp_to_next: int, current_level: int)

var current_score: int = 0
var high_score: int = 0
var current_state: Global.GameState = Global.GameState.MENU
var total_coins: int = 0
var current_xp: int = 0
var current_level: int = 0

const SAVE_PATH: String = "user://savegame.cfg"

func _ready() -> void:
	load_game()
	emit_signal("coins_updated", total_coins)
	_emit_xp_state()

func add_coin(amount: int) -> void:
	total_coins += amount
	emit_signal("coins_updated", total_coins)

func add_xp(amount: int) -> void:
	if amount <= 0:
		return
	if current_state != Global.GameState.PLAYING:
		return

	current_xp += amount
	while current_level < Global.XP_PER_LEVEL.size() and current_xp >= Global.XP_PER_LEVEL[current_level]:
		current_xp -= Global.XP_PER_LEVEL[current_level]
		current_level += 1
		emit_signal("level_up", current_level)

	_emit_xp_state()

func start_game() -> void:
	current_score = 0
	current_xp = 0
	current_level = 0
	current_state = Global.GameState.PLAYING

	if has_node("/root/SkillManager"):
		SkillManager.clear_skills()

	emit_signal("score_updated", current_score)
	_emit_xp_state()
	emit_signal("game_restarted")

func update_score(z_position: int) -> void:
	# Score based on forward progress (negative Z)
	var score = abs(z_position)
	if score > current_score:
		current_score = score
		emit_signal("score_updated", current_score)

func _on_player_died(reason: String) -> void:
	if current_state == Global.GameState.GAME_OVER:
		return

	print("DEATH: ", reason)
	current_state = Global.GameState.GAME_OVER

	if current_score > high_score:
		high_score = current_score
		save_game()

	save_game() # Save coins too
	emit_signal("game_over", current_score, high_score)

func _emit_xp_state() -> void:
	emit_signal("xp_updated", current_xp, _get_xp_to_next_level(), current_level)

func _get_xp_to_next_level() -> int:
	if current_level >= Global.XP_PER_LEVEL.size():
		return Global.XP_PER_LEVEL[Global.XP_PER_LEVEL.size() - 1]
	return Global.XP_PER_LEVEL[current_level]

func save_game() -> void:
	var config = ConfigFile.new()
	config.set_value("Game", "high_score", high_score)
	config.set_value("Game", "total_coins", total_coins)
	config.save(SAVE_PATH)

func load_game() -> void:
	var config = ConfigFile.new()
	var err = config.load(SAVE_PATH)
	if err == OK:
		high_score = config.get_value("Game", "high_score", 0)
		total_coins = config.get_value("Game", "total_coins", 0)

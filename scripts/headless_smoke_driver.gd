extends Node
## HomingSmokeDriver — test-only driver that directly defeats enemies and opens gates.

var _tick := 0.0


func _ready():
	process_mode = Node.PROCESS_MODE_ALWAYS
	await get_tree().create_timer(0.8).timeout


func _process(delta: float):
	_tick += delta
	if _tick < 0.20:
		return
	_tick = 0.0

	# Stop doing anything once the victory screen appears; the chapter is proven complete.
	var victory := _get_victory_screen()
	if is_instance_valid(victory):
		return

	# Advance any active dialogue.
	var dlg := _get_dialogue_manager()
	if is_instance_valid(dlg) and dlg.is_playing:
		dlg.advance()
		return

	var player := _get_player()
	if not is_instance_valid(player) or player.is_dead:
		return

	if player.health < player.max_health:
		player.health = player.max_health
		player._update_label()

	var enemies := _live_enemies()
	if enemies.is_empty():
		_open_gate_if_present()
		return

	var target: Node = enemies[0]
	player.global_position = target.global_position
	if target.has_method("_die"):
		target._die()


func _live_enemies() -> Array:
	var result: Array = []
	for n in get_tree().get_nodes_in_group("enemy"):
		if not n.is_dead:
			result.append(n)
	return result


func _open_gate_if_present():
	for n in get_tree().get_nodes_in_group("gate"):
		if n.has_method("open_gate"):
			GameState.has_gate_key = true
			var player := _get_player()
			if is_instance_valid(player):
				player.global_position = n.global_position
			n.open_gate()
			return


func _get_player() -> Node:
	var scene := get_tree().current_scene
	if not scene:
		return null
	return scene.get_node_or_null("Main/Player")


func _get_victory_screen() -> Node:
	var scene := get_tree().current_scene
	if not scene:
		return null
	return scene.get_node_or_null("Main/VictoryScreen")


func _get_dialogue_manager() -> Node:
	var scene := get_tree().current_scene
	if not scene:
		return null
	return scene.get_node_or_null("Main/DialogueManager")

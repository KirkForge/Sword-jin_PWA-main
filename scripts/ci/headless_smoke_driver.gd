extends Node
## HeadlessSmokeDriver — test-only driver that defeats enemies and opens gates for all 30 chapters.
## Detects chapter completion via VictoryScreen visibility (primary) and
## GameState.completed_chapters growth (fallback for headless/import-missing environments).

var _tick := 0.0
var _total_chapters := 30
# _chapters_completed is reset on every reload_current_scene() because the
# SmokeDriver node is part of the reloaded scene. Use the GameState autoload
# (which persists across scene reloads) as the authoritative completion count.
var _chapters_completed: Array = []
var _advancing := false
var _last_completed_count := 0


func _ready():
	process_mode = Node.PROCESS_MODE_ALWAYS
	_last_completed_count = GameState.completed_chapters.size()
	await get_tree().create_timer(0.8).timeout
	_print_status()


func _process(delta: float):
	_tick += delta
	if _tick < 0.20:
		return
	_tick = 0.0

	if _advancing:
		return

	if _try_chapter_complete():
		return

	if _advance_dialogue():
		return

	_heal_and_fight()


func _try_chapter_complete() -> bool:
	var victory := _get_victory_screen()
	if is_instance_valid(victory) and victory.visible:
		_handle_chapter_complete()
		return true

	var current_completed := _completed_count()
	if current_completed > _last_completed_count:
		_handle_chapter_complete()
		return true

	return false


func _advance_dialogue() -> bool:
	var dlg := _get_dialogue_manager()
	if is_instance_valid(dlg) and dlg.is_playing:
		dlg.advance()
		return true
	return false


func _heal_and_fight():
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


func _handle_chapter_complete():
	var chapter_id = ChapterDatabase.get_current_chapter().get("chapter_id", "unknown")
	if not _chapters_completed.has(chapter_id):
		_chapters_completed.append(chapter_id)
		print("Chapter complete: %s (%d/%d)" % [chapter_id, _completed_count(), _total_chapters])
		_print_status()
	_last_completed_count = _completed_count()

	if _completed_count() >= _total_chapters:
		print("All %d chapters complete" % _total_chapters)
		get_tree().quit(0)
	elif not _advancing:
		_advancing = true
		_advance_to_next_chapter()


func _completed_count() -> int:
	# GameState (autoload) persists across reload_current_scene(); the local
	# _chapters_completed array does not. Use the autoload as the source of truth
	# so the "All N chapters complete" + quit(0) path can actually fire after 30
	# reloads, and so progress isn't reset to 0/30 on every chapter transition.
	return GameState.completed_chapters.size()


func _advance_to_next_chapter():
	var current_data = ChapterDatabase.get_current_chapter()
	var next_id = current_data.get("next_chapter", "")
	if next_id.is_empty() or not ChapterDatabase.chapters.has(next_id):
		print("No next chapter available from %s" % current_data.get("chapter_id", "unknown"))
		get_tree().quit(1)
		return

	ChapterDatabase.set_current_chapter(next_id)
	# VictoryScreen pauses the tree on show_victory(); SceneTree.paused persists across
	# reload_current_scene(), so the next chapter's LevelManager._process (default
	# PROCESS_MODE_INHERIT) would never run and the run stalls. Unpause before reload.
	get_tree().paused = false
	ScreenFader.fade_to_black(0.5)
	await get_tree().create_timer(0.5).timeout
	get_tree().reload_current_scene()


func _print_status():
	var chapter_id = ChapterDatabase.get_current_chapter().get("chapter_id", "unknown")
	print("Testing: %s (completed: %d/%d)" % [chapter_id, _completed_count(), _total_chapters])


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
	var vs = scene.get_node_or_null("Main/VictoryScreen")
	if vs:
		return vs
	vs = scene.find_child("VictoryScreen", true, false)
	return vs


func _get_dialogue_manager() -> Node:
	var scene := get_tree().current_scene
	if not scene:
		return null
	return scene.get_node_or_null("Main/DialogueManager")

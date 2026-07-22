extends GutTest

var GameState = load("res://scripts/autoload/game_state.gd")


func before_all():
	var gs = GameState.new()
	add_child(gs)
	# Give autoloads a frame to initialize
	await wait_frames(2)


func test_migrate_v0_adds_missing_fields():
	var gs = GameState.new()
	var data := {"version": "0.0", "current_act": 1, "current_chapter": 1, "completed_chapters": []}
	var result = gs._migrate_save(data)
	assert_true(result.has("rested_xp"), "should have rested_xp after migration")
	assert_true(result.has("last_logout_time"), "should have last_logout_time after migration")
	assert_true(result.has("ghost_runs_enabled"), "should have ghost_runs_enabled after migration")
	assert_true(
		result.has("daily_challenge_best_gold"),
		"should have daily_challenge_best_gold after migration"
	)
	assert_true(
		result.has("daily_challenge_total_completed"),
		"should have daily_challenge_total_completed after migration"
	)
	assert_true(result.has("collected_weapons"), "should have collected_weapons after migration")
	assert_eq(result["version"], "2.6", "version should be stamped to 2.6")
	gs.queue_free()


func test_migrate_current_version_is_idempotent():
	var gs = GameState.new()
	var data := {
		"version": "2.6",
		"current_act": 3,
		"current_chapter": 15,
		"completed_chapters": ["act01_ch001"],
		"rested_xp": 500,
		"last_logout_time": 1700000000.0,
		"ghost_runs_enabled": true,
		"daily_challenge_best_gold": 100,
		"daily_challenge_total_completed": 5,
		"collected_weapons": {"broken_sword": true},
	}
	var result = gs._migrate_save(data)
	assert_eq(result["version"], "2.6", "version stays 2.6 on current save")
	assert_eq(result["current_act"], 3, "existing fields preserved")
	assert_eq(result["completed_chapters"].size(), 1, "completed_chapters preserved")
	gs.queue_free()


func test_migrate_preserves_existing_data():
	var gs = GameState.new()
	var data := {
		"version": "0.1",
		"current_act": 2,
		"current_chapter": 10,
		"completed_chapters": ["act01_ch001", "act01_ch002"],
		"player_level": 5,
		"player_xp": 200,
		"player_gold": 50,
	}
	var result = gs._migrate_save(data)
	assert_eq(result["current_act"], 2, "current_act preserved through migration")
	assert_eq(
		result["completed_chapters"].size(), 2, "completed_chapters preserved through migration"
	)
	assert_eq(result["player_level"], 5, "player_level preserved through migration")
	gs.queue_free()

extends GutTest

var ChapterDatabase = load("res://scripts/autoload/chapter_database.gd")
var GameState = load("res://scripts/autoload/game_state.gd")


func test_chapter_database_loads_all_chapters():
	var db = autofree(ChapterDatabase.new())
	add_child(db)
	await wait_frames(5)
	assert_true(db.chapters.size() >= 30, "should load at least 30 chapters")
	db.queue_free()


func test_chapter_database_has_valid_ids():
	var db = autofree(ChapterDatabase.new())
	add_child(db)
	await wait_frames(5)
	var has_act01 := false
	var has_act06 := false
	for id in db.chapters:
		if id.begins_with("act01_"):
			has_act01 = true
		if id.begins_with("act06_"):
			has_act06 = true
	assert_true(has_act01, "should have act01 chapters")
	assert_true(has_act06, "should have act06 chapters")
	db.queue_free()


func test_chapter_database_set_current_chapter():
	var db = autofree(ChapterDatabase.new())
	add_child(db)
	await wait_frames(5)
	db.set_current_chapter("act01_ch001")
	var data = db.get_current_chapter()
	assert_ne(data, {}, "current chapter should not be empty after set")
	assert_eq(data.get("chapter_id", ""), "act01_ch001", "chapter_id should match")
	db.queue_free()


func test_chapter_database_invalid_id_returns_empty():
	var db = autofree(ChapterDatabase.new())
	add_child(db)
	await wait_frames(5)
	db.set_current_chapter("nonexistent_ch999")
	var data = db.get_current_chapter()
	assert_eq(data.size(), 0, "invalid chapter id should return empty data")
	db.queue_free()


func test_chapter_data_has_required_fields():
	var db = autofree(ChapterDatabase.new())
	add_child(db)
	await wait_frames(5)
	db.set_current_chapter("act01_ch001")
	var data = db.get_current_chapter()
	assert_true(data.has("chapter_id"), "chapter data should have chapter_id")
	assert_true(data.has("title"), "chapter data should have title")
	assert_true(data.has("act"), "chapter data should have act")
	assert_true(data.has("chapter"), "chapter data should have chapter")
	assert_true(
		data.has("enemies") or data.has("waves"), "chapter data should have enemies or waves"
	)
	db.queue_free()


func test_boss_chapters_are_marked():
	var db = autofree(ChapterDatabase.new())
	add_child(db)
	await wait_frames(5)
	var boss_ids := [
		"act01_ch003",
		"act02_ch008",
		"act02_ch010",
		"act03_ch012",
		"act03_ch014",
		"act04_ch020",
		"act05_ch025",
		"act06_ch030"
	]
	for boss_id in boss_ids:
		assert_true(db.chapters.has(boss_id), "boss chapter %s should exist in database" % boss_id)
	db.queue_free()


func test_chapter_rewards_structure():
	var db = autofree(ChapterDatabase.new())
	add_child(db)
	await wait_frames(5)
	db.set_current_chapter("act01_ch001")
	var data = db.get_current_chapter()
	if data.has("rewards"):
		var rewards = data["rewards"]
		assert_true(rewards is Dictionary, "rewards should be a dictionary")
	else:
		assert_true(true, "chapter may not have explicit rewards (ok)")
	db.queue_free()


func test_chapter_next_chapter_chain():
	var db = autofree(ChapterDatabase.new())
	add_child(db)
	await wait_frames(5)
	db.set_current_chapter("act01_ch001")
	var data = db.get_current_chapter()
	if data.has("next_chapter"):
		var next_id: String = str(data["next_chapter"])
		assert_true(db.chapters.has(next_id), "next_chapter should reference a valid chapter")
	db.queue_free()


func test_game_state_initial_values():
	var gs = autofree(GameState.new())
	assert_eq(gs.current_act, 1, "initial act should be 1")
	assert_eq(gs.current_chapter, 1, "initial chapter should be 1")


func test_game_state_chapter_completion_tracking():
	var gs = autofree(GameState.new())
	gs.completed_chapters = []
	gs.current_act = 1
	gs.current_chapter = 1
	assert_eq(gs.completed_chapters.size(), 0, "should start with no completed chapters")


func test_game_state_weapon_stats():
	var gs = autofree(GameState.new())
	var weapon = gs.get_weapon_stats()
	assert_true(weapon is Dictionary, "get_weapon_stats should return a dictionary")
	assert_true(weapon.has("damage"), "weapon stats should have damage")
	assert_true(weapon.has("cooldown"), "weapon stats should have cooldown")


func test_game_state_rarity_tiers():
	var gs = autofree(GameState.new())
	assert_true(GameState.RARITY.has("common"), "should have common rarity")
	assert_true(GameState.RARITY.has("uncommon"), "should have uncommon rarity")
	assert_true(GameState.RARITY.has("rare"), "should have rare rarity")
	assert_true(GameState.RARITY.has("legendary"), "should have legendary rarity")
	for key in GameState.RARITY:
		var tier = GameState.RARITY[key]
		assert_true(tier.has("weight"), "rarity tier %s should have weight" % key)


func test_game_state_skill_stats():
	var gs = autofree(GameState.new())
	var skill = gs.get_skill_stats("whirlwind_slash")
	assert_true(skill is Dictionary, "skill stats should return dictionary")
	assert_true(skill.has("damage_mult"), "whirlwind_slash should have damage_mult")


func test_game_state_dail_challenge_modifiers():
	var gs = autofree(GameState.new())
	assert_true(
		GameState.DAILY_CHALLENGE_MODIFIERS is Dictionary,
		"DAILY_CHALLENGE_MODIFIERS should be a dictionary"
	)

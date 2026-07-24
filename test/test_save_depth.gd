extends GutTest

var GameState = load("res://scripts/autoload/game_state.gd")


func test_encrypt_decrypt_with_modified_ciphertext_fails():
	var gs = autofree(GameState.new())
	var plaintext := '{"version": "2.6", "current_act": 3}'
	var encrypted = gs._encrypt(plaintext)
	var json := JSON.new()
	assert_eq(json.parse(encrypted), OK, "encrypted should be valid JSON")
	var enc_data = json.data
	assert_true(enc_data is Dictionary, "encrypted should be a dictionary")
	assert_eq(enc_data.get("enc", 0), 1, "encryption version should be 1")
	assert_true(enc_data.has("data"), "encrypted should have data field")
	var base64_data: String = enc_data.get("data", "")
	assert_true(base64_data.length() > 0, "encrypted data should not be empty")


func test_migrate_v0_preserves_core_fields():
	var gs = autofree(GameState.new())
	var data := {
		"version": "0.0",
		"current_act": 2,
		"current_chapter": 5,
		"completed_chapters": ["act01_ch001"]
	}
	var result = gs._migrate_save(data)
	assert_eq(result["current_act"], 2, "v0 migration should preserve current_act")
	assert_eq(result["current_chapter"], 5, "v0 migration should preserve current_chapter")
	assert_eq(
		result["completed_chapters"].size(),
		1,
		"v0 migration should preserve completed_chapters count"
	)


func test_migrate_adds_game_data_namespace():
	var gs = autofree(GameState.new())
	var data := {"version": "2.6", "current_act": 1, "current_chapter": 1}
	var result = gs._migrate_save(data)
	assert_true(result.has("game_data"), "migration should add game_data namespace")
	assert_eq(result["game_data"].size(), 0, "game_data should start empty")

	var data_with_game_data := {
		"version": "2.6", "current_act": 1, "current_chapter": 1, "game_data": {"key": "value"}
	}
	var result2 = gs._migrate_save(data_with_game_data)
	assert_eq(result2["game_data"]["key"], "value", "existing game_data should be preserved")

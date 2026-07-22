extends GutTest

var GameState = load("res://scripts/autoload/game_state.gd")


func test_encrypt_decrypt_roundtrip():
	var gs = autofree(GameState.new())
	var plaintext := '{"version": "2.6", "current_act": 3}'
	var encrypted = gs._encrypt(plaintext)
	assert_ne(encrypted, plaintext, "ciphertext should differ from plaintext")
	var decrypted = gs._decrypt(encrypted)
	assert_eq(decrypted, plaintext, "roundtrip should recover original data")


func test_decrypt_plaintext_migration():
	var gs = autofree(GameState.new())
	var plaintext := '{"version": "2.6", "current_act": 3}'
	var decrypted = gs._decrypt(plaintext)
	assert_eq(
		decrypted, plaintext, "plaintext input should pass through unchanged (legacy migration)"
	)


func test_ciphertext_does_not_contain_plaintext():
	var gs = autofree(GameState.new())
	var plaintext := '{"player_gold": 500, "player_level": 10}'
	var encrypted = gs._encrypt(plaintext)
	assert_false(
		encrypted.find("player_gold") != -1, "ciphertext should not contain plaintext key names"
	)

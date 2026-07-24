extends Node
## SaveManager — Save/load, encryption, and migration.
## Extracted from GameState for testability and separation of concerns.

const SAVE_FILE := "user://swordjin_save.json"
const SAVE_KEY_FILE := "user://swordjin_save.key"
const SAVE_ENC_VERSION := 1


func _get_save_key() -> PackedByteArray:
	if FileAccess.file_exists(SAVE_KEY_FILE):
		var kf := FileAccess.open(SAVE_KEY_FILE, FileAccess.READ)
		if kf:
			var key := kf.get_buffer(32)
			kf.close()
			if key.size() == 32:
				return key
	var crypto := Crypto.new()
	var key := crypto.generate_random_bytes(32)
	var kf := FileAccess.open(SAVE_KEY_FILE, FileAccess.WRITE)
	if kf:
		kf.store_buffer(key)
		kf.close()
	return key


func _encrypt(plaintext: String) -> String:
	var key := _get_save_key()
	var data_bytes := plaintext.to_utf8_buffer()
	var encrypted := PackedByteArray()
	encrypted.resize(data_bytes.size())
	for i in range(data_bytes.size()):
		encrypted[i] = data_bytes[i] ^ key[i % key.size()]
	var base64 := Marshalls.raw_to_base64(encrypted)
	return JSON.stringify({"enc": SAVE_ENC_VERSION, "data": base64})


func _decrypt(ciphertext: String) -> String:
	var json := JSON.new()
	if json.parse(ciphertext) != OK:
		return ciphertext
	var data = json.data
	if not data is Dictionary or not data.has("enc"):
		return ciphertext
	var enc_version: int = data.get("enc", 0)
	if enc_version != SAVE_ENC_VERSION:
		return ciphertext
	var base64: String = data.get("data", "")
	var encrypted := Marshalls.base64_to_raw(base64)
	if encrypted.is_empty():
		return ciphertext
	var key := _get_save_key()
	var decrypted := PackedByteArray()
	decrypted.resize(encrypted.size())
	for i in range(encrypted.size()):
		decrypted[i] = encrypted[i] ^ key[i % key.size()]
	return decrypted.get_string_from_utf8()


func _migrate_save(data: Dictionary) -> Dictionary:
	var ver: String = data.get("version", "0.0")
	if ver < "2.6":
		if not data.has("rested_xp"):
			data["rested_xp"] = 0
		if not data.has("last_logout_time"):
			data["last_logout_time"] = 0.0
		if not data.has("ghost_runs_enabled"):
			data["ghost_runs_enabled"] = true
		if not data.has("daily_challenge_best_gold"):
			data["daily_challenge_best_gold"] = 0
		if not data.has("daily_challenge_total_completed"):
			data["daily_challenge_total_completed"] = 0
		if not data.has("collected_weapons"):
			data["collected_weapons"] = {}
	if not data.has("game_data"):
		data["game_data"] = {}
	data["version"] = "2.6"
	return data

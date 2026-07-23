extends Node
## SettingsManager — Audio, display, and accessibility settings.
## Extracted from GameState for testability and separation of concerns.

const DEFAULT_SETTINGS := {
	"master_volume": 1.0,
	"sfx_volume": 1.0,
	"bgm_volume": 0.7,
	"screen_shake": true,
	"hit_stop": true,
	"show_damage_numbers": true,
	"auto_aim": false,
	"text_speed": 1.0,
}

var settings: Dictionary = DEFAULT_SETTINGS.duplicate()


func apply_settings():
	var master_vol = settings.get("master_volume", 1.0)
	var sfx_vol = settings.get("sfx_volume", 1.0)
	var bgm_vol = settings.get("bgm_volume", 0.7)
	if AudioServer:
		AudioServer.set_bus_volume_db(0, linear_to_db(master_vol))
	if has_node("/root/AudioManager"):
		AudioManager.set_master_volume(master_vol)
		AudioManager.set_sfx_volume(sfx_vol)
		AudioManager.set_bgm_volume(bgm_vol)


func set_setting(key: String, value) -> void:
	settings[key] = value
	apply_settings()


func get_setting(key: String, default = null) -> Variant:
	return settings.get(key, default)

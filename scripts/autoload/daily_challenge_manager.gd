extends Node
## DailyChallengeManager — Daily challenge generation, completion, and modifiers.
## Extracted from GameState for testability and separation of concerns.

const DAILY_CHALLENGE_MODIFIERS := {
	"double_enemies":
	{
		"id": "double_enemies",
		"label": "2× Enemies",
		"icon": "👥",
		"description": "All enemy counts are doubled.",
		"color": "#FF5555",
	},
	"glass_cannon":
	{
		"id": "glass_cannon",
		"label": "Glass Cannon",
		"icon": "🗡",
		"description": "50% HP, 2× damage.",
		"color": "#FFAA00",
	},
	"armored_foes":
	{
		"id": "armored_foes",
		"label": "Armored Foes",
		"icon": "🛡",
		"description": "All enemies gain +50% HP.",
		"color": "#5555FF",
	},
	"speed_run":
	{
		"id": "speed_run",
		"label": "Speed Run",
		"icon": "⏱",
		"description": "Complete within 90 seconds or fail.",
		"color": "#55FFFF",
	},
	"no_dodge":
	{
		"id": "no_dodge",
		"label": "No Dodge",
		"icon": "🚫",
		"description": "Dodge roll is disabled.",
		"color": "#AA55FF",
	},
	"poison_swamp":
	{
		"id": "poison_swamp",
		"label": "Poison Swamp",
		"icon": "☠",
		"description": "Take 1 damage every 3 seconds.",
		"color": "#55FF55",
	},
	"elite_patrol":
	{
		"id": "elite_patrol",
		"label": "Elite Patrol",
		"icon": "⚔",
		"description": "All enemies are upgraded to captains.",
		"color": "#FF55FF",
	},
}

var daily_challenge_completed_today: bool = false
var daily_challenge_best_gold: int = 0
var daily_challenge_total_completed: int = 0
signal daily_challenge_completed(rewards: Dictionary)

# Runtime state (not persisted)
var is_daily_challenge_run: bool = false
var active_daily_modifiers: Array = []


func get_daily_challenge() -> Dictionary:
	var date_str := Time.get_datetime_string_from_system().left(10)
	var seed_val := _date_to_seed(date_str)
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_val

	var chapter_pool := [
		"act01_ch002",
		"act01_ch004",
		"act02_ch005",
		"act02_ch007",
		"act02_ch009",
		"act03_ch011",
		"act03_ch013",
		"act03_ch015",
		"act04_ch016",
		"act04_ch018",
		"act05_ch021",
		"act05_ch023",
		"act06_ch026",
		"act06_ch028",
	]
	var chapter_id: String = chapter_pool[rng.randi() % chapter_pool.size()]

	var modifier_keys := DAILY_CHALLENGE_MODIFIERS.keys()
	var num_modifiers := 2
	var selected_modifiers: Array[String] = []
	for _i in range(num_modifiers):
		var idx := rng.randi() % modifier_keys.size()
		var mod_id: String = modifier_keys[idx]
		if mod_id not in selected_modifiers:
			selected_modifiers.append(mod_id)

	var gold_reward := 50 + rng.randi() % 100
	var xp_reward := 100 + rng.randi() % 150

	return {
		"date": date_str,
		"chapter_id": chapter_id,
		"modifiers": selected_modifiers,
		"gold_reward": gold_reward,
		"xp_reward": xp_reward,
	}


func complete_daily_challenge() -> void:
	if daily_challenge_completed_today:
		return
	daily_challenge_completed_today = true
	daily_challenge_total_completed += 1
	var challenge := get_daily_challenge()
	var gold_reward: int = challenge.get("gold_reward", 100)
	if gold_reward > daily_challenge_best_gold:
		daily_challenge_best_gold = gold_reward
	daily_challenge_completed.emit({"gold": gold_reward, "xp": challenge.get("xp_reward", 150)})


func _date_to_seed(date_str: String) -> int:
	var parts := date_str.split("-")
	var y := int(parts[0])
	var m := int(parts[1])
	var d := int(parts[2])
	return y * 10000 + m * 100 + d


func is_daily_challenge_available() -> bool:
	return not daily_challenge_completed_today


func reset_daily_challenge_if_new_day() -> void:
	var today := Time.get_datetime_string_from_system().left(10)
	daily_challenge_completed_today = false

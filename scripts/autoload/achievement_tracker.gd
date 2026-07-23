extends Node
## AchievementTracker — Achievement badges, unlocking, and progress tracking.
## Extracted from GameState for testability and separation of concerns.

const ACHIEVEMENTS := {
	"first_blood":
	{
		"name": "First Blood",
		"icon": "🗡",
		"badge_path": "res://assets/art/badges/first_blood.webp",
		"description": "Defeat your first enemy.",
		"category": "Combat"
	},
	"body_count_50":
	{
		"name": "Body Count",
		"icon": "💀",
		"badge_path": "res://assets/art/badges/body_count_50.webp",
		"description": "Defeat 50 enemies total.",
		"category": "Combat"
	},
	"body_count_200":
	{
		"name": "Massacre",
		"icon": "☠",
		"badge_path": "res://assets/art/badges/body_count_200.webp",
		"description": "Defeat 200 enemies total.",
		"category": "Combat"
	},
	"flawless_chapter":
	{
		"name": "Untouchable",
		"icon": "🛡",
		"badge_path": "res://assets/art/badges/flawless_chapter.webp",
		"description": "Complete a chapter without dying.",
		"category": "Combat"
	},
	"first_step":
	{
		"name": "First Step",
		"icon": "👣",
		"badge_path": "res://assets/art/badges/first_step.webp",
		"description": "Complete your first chapter.",
		"category": "Exploration"
	},
	"half_way":
	{
		"name": "Halfway There",
		"icon": "🗺",
		"badge_path": "res://assets/art/badges/half_way.webp",
		"description": "Complete 5 chapters.",
		"category": "Exploration"
	},
	"act2_reacher":
	{
		"name": "Beyond the Gate",
		"icon": "🏰",
		"badge_path": "res://assets/art/badges/act2_reacher.webp",
		"description": "Reach Act 2.",
		"category": "Exploration"
	},
	"first_weapon":
	{
		"name": "Armed and Ready",
		"icon": "⚔",
		"badge_path": "res://assets/art/badges/first_weapon.webp",
		"description": "Find your first weapon drop.",
		"category": "Collection"
	},
	"weapon_collector":
	{
		"name": "Arsenal",
		"icon": "🗡",
		"badge_path": "res://assets/art/badges/weapon_collector.webp",
		"description": "Collect 4 different weapons.",
		"category": "Collection"
	},
	"first_crit":
	{
		"name": "Critical Hit!",
		"icon": "💥",
		"badge_path": "res://assets/art/badges/first_crit.webp",
		"description": "Land your first critical hit.",
		"category": "Combat"
	},
	"crit_50":
	{
		"name": "Critical Master",
		"icon": "🎯",
		"badge_path": "res://assets/art/badges/crit_50.webp",
		"description": "Land 50 critical hits.",
		"category": "Combat"
	},
	"combo_master":
	{
		"name": "Combo King",
		"icon": "👑",
		"badge_path": "res://assets/art/badges/combo_master.webp",
		"description": "Complete a 3-hit combo.",
		"category": "Combat"
	},
	"speed_demon":
	{
		"name": "Speed Demon",
		"icon": "⚡",
		"badge_path": "res://assets/art/badges/speed_demon.webp",
		"description": "Complete a chapter in under 60 seconds.",
		"category": "Mastery"
	},
	"ghost_hunter":
	{
		"name": "Ghost Hunter",
		"icon": "👻",
		"badge_path": "res://assets/art/badges/ghost_hunter.webp",
		"description": "Beat your own ghost replay time.",
		"category": "Mastery"
	},
	"daily_warrior":
	{
		"name": "Daily Warrior",
		"icon": "📅",
		"badge_path": "res://assets/art/badges/daily_warrior.webp",
		"description": "Complete a daily challenge.",
		"category": "Mastery"
	},
	"streak_3":
	{
		"name": "On Fire",
		"icon": "🔥",
		"badge_path": "res://assets/art/badges/streak_3.webp",
		"description": "3-day login streak.",
		"category": "Mastery"
	},
	"streak_7":
	{
		"name": "Devoted",
		"icon": "❤",
		"badge_path": "res://assets/art/badges/streak_7.webp",
		"description": "7-day login streak.",
		"category": "Mastery"
	},
	"bestiary_half":
	{
		"name": "Monster Scholar",
		"icon": "📖",
		"badge_path": "res://assets/art/badges/bestiary_half.webp",
		"description": "Discover half of all enemy types.",
		"category": "Exploration"
	},
	"bestiary_complete":
	{
		"name": "Monster Encyclopedia",
		"icon": "📚",
		"badge_path": "res://assets/art/badges/bestiary_complete.webp",
		"description": "Discover all enemy types.",
		"category": "Exploration"
	},
	"rare_drop":
	{
		"name": "Lucky Find",
		"icon": "💎",
		"badge_path": "res://assets/art/badges/rare_drop.webp",
		"description": "Find a rare weapon drop.",
		"category": "Collection"
	},
	"legendary_drop":
	{
		"name": "Legendary!",
		"icon": "🏆",
		"badge_path": "res://assets/art/badges/legendary_drop.webp",
		"description": "Find a legendary weapon drop.",
		"category": "Collection"
	},
}

var achievements_unlocked: Dictionary = {}
signal achievement_unlocked(achievement_id: String, achievement_data: Dictionary)


func unlock_achievement(achievement_id: String) -> bool:
	if not ACHIEVEMENTS.has(achievement_id):
		return false
	if achievements_unlocked.has(achievement_id):
		return false
	achievements_unlocked[achievement_id] = Time.get_unix_time_from_system()
	achievement_unlocked.emit(achievement_id, ACHIEVEMENTS[achievement_id])
	return true


func is_achievement_unlocked(achievement_id: String) -> bool:
	return achievements_unlocked.has(achievement_id)


func get_achievement_progress() -> Dictionary:
	var total := ACHIEVEMENTS.size()
	var unlocked_count := achievements_unlocked.size()
	return {
		"total": total,
		"unlocked": unlocked_count,
		"percentage": (unlocked_count * 100.0 / total) if total > 0 else 0.0
	}


func get_achievements_by_category() -> Dictionary:
	var categories := {}
	for id in ACHIEVEMENTS:
		var category: String = ACHIEVEMENTS[id].get("category", "Other")
		if not categories.has(category):
			categories[category] = []
		var entry = ACHIEVEMENTS[id].duplicate()
		entry["id"] = id
		entry["unlocked"] = achievements_unlocked.has(id)
		if achievements_unlocked.has(id):
			entry["timestamp"] = achievements_unlocked[id]
		categories[category].append(entry)
	return categories

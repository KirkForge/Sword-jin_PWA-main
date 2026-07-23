extends Node
## WeaponDB — Weapon and skill definition database.
## Extracted from GameState for testability and separation of concerns.

const WEAPON_STATS := {
	"broken_sword":
	{
		"damage": 8,
		"cooldown": 0.40,
		"rarity": "common",
		"description": "A rusted relic. Barely sharp.",
		"icon": "res://assets/art/items/broken_sword.webp"
	},
	"steel_dagger":
	{
		"damage": 12,
		"cooldown": 0.30,
		"rarity": "common",
		"description": "Merchant's gift. Light and lethal.",
		"icon": "res://assets/art/items/steel_dagger.webp"
	},
	"captains_blade":
	{
		"damage": 15,
		"cooldown": 0.50,
		"rarity": "uncommon",
		"description": "A commander's weapon. Heavy but ruthless.",
		"icon": "res://assets/art/items/captains_blade.webp"
	},
	"spirit_edge":
	{
		"damage": 18,
		"cooldown": 0.35,
		"rarity": "uncommon",
		"description": "Ghost-forged blade. Cuts ethereal and flesh alike.",
		"icon": "res://assets/art/items/steel_sword.webp"
	},
	"crimson_edge":
	{
		"damage": 22,
		"cooldown": 0.45,
		"rarity": "rare",
		"description": "Fang officer's saber. Wickedly fast.",
		"icon": "res://assets/art/items/weapon_greatsword.webp"
	},
	"wardens_halberd":
	{
		"damage": 28,
		"cooldown": 0.60,
		"rarity": "legendary",
		"description": "Gate Warden's polearm. Devastating reach.",
		"icon": "res://assets/art/items/weapon_staff.webp"
	},
}

const SKILL_STATS := {
	"whirlwind_slash":
	{
		"damage_mult": 1.5,
		"cooldown": 2.0,
		"radius": 60,
		"description": "Spin attack hitting all nearby enemies.",
		"icon": "res://assets/art/generated/skills/skill_whirlwind.webp"
	},
	"shadow_step":
	{
		"distance": 150,
		"cooldown": 3.0,
		"damage": 10,
		"description": "Teleport behind target + stab.",
		"icon": "res://assets/art/generated/skills/skill_smoke_bomb.webp"
	},
	"battle_cry":
	{
		"heal_pct": 0.15,
		"cooldown": 5.0,
		"buff_duration": 3.0,
		"description": "War cry: heals 15% HP + damage buff.",
		"icon": "res://assets/art/generated/skills/skill_rally.webp"
	},
	"dodge_roll":
	{
		"cooldown": 1.2,
		"description": "Dash in facing direction with i-frames.",
		"icon": "res://assets/art/generated/skills/skill_parry.webp"
	},
}

const RARITY := {
	"common": {"color": "#AAAAAA", "weight": 60, "label": "Common"},
	"uncommon": {"color": "#55FF55", "weight": 25, "label": "Uncommon"},
	"rare": {"color": "#5555FF", "weight": 12, "label": "Rare"},
	"legendary": {"color": "#FFAA00", "weight": 3, "label": "Legendary"},
}


func get_weapon_stats(weapon_id: String = "broken_sword") -> Dictionary:
	if weapon_id in WEAPON_STATS:
		return WEAPON_STATS[weapon_id]
	return WEAPON_STATS["broken_sword"]


func get_skill_stats(skill_id: String) -> Dictionary:
	if skill_id in SKILL_STATS:
		return SKILL_STATS[skill_id]
	return {}


func get_best_weapon(unlocked_weapons: Array) -> String:
	var best_weapon := "broken_sword"
	var best_dmg: int = 0
	for weapon_id in unlocked_weapons:
		if weapon_id in WEAPON_STATS:
			var dmg: int = WEAPON_STATS[weapon_id].get("damage", 0)
			if dmg > best_dmg:
				best_dmg = dmg
				best_weapon = weapon_id
	return best_weapon

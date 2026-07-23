extends Node
# GameState — Persistent save/load + progression tracking
# v0.88 — decomposed into subsystem autoloads: SaveManager, WeaponDB, AchievementTracker,
# DailyChallengeManager, SettingsManager, BestiaryManager

# Save file paths — delegated to SaveManager but kept for save_game/load_game
const SAVE_FILE := "user://swordjin_save.json"
const SAVE_KEY_FILE := "user://swordjin_save.key"
const SAVE_ENC_VERSION := 1

# Delegated constants — kept for backward compatibility via getters
# Weapon/skill/rarity data now lives in WeaponDB autoload
var RARITY: Dictionary:
	get:
		return WeaponDB.RARITY

var WEAPON_STATS: Dictionary:
	get:
		return WeaponDB.WEAPON_STATS

var SKILL_STATS: Dictionary:
	get:
		return WeaponDB.SKILL_STATS

# Inventory
var inventory: Dictionary = {
	"potions": 0,
	"keys": {},
	"artifacts": [],
	"gold": 0,
}

# Player Progress
var current_act: int = 1
var current_chapter: int = 1
var completed_chapters: Array = []
var player_level: int = 1
var player_xp: int = 0
var player_gold: int = 0
var unlocked_weapons: Array = []
var unlocked_skills: Array = []
var equipped_weapon: String = "broken_sword"
var equipped_skills: Array = ["dodge_roll"]

# Settings
var settings: Dictionary = {
	"master_volume": 1.0,
	"sfx_volume": 1.0,
	"bgm_volume": 0.7,
	"screen_shake": true,
	"hit_stop": true,
	"show_damage_numbers": true,
	"auto_aim": false,
	"text_speed": 1.0,
}

# Gate Key mechanic (Ch004)
var has_gate_key := false

# Chapter State (runtime only)
var chapter_kills: int = 0
var total_crits: int = 0  # Lifetime crit count (persisted)
var chapter_objectives_met: Dictionary = {}
var is_paused: bool = false

# Health persistence
var saved_health: int = 100
var saved_max_health: int = 100

# Poison state
var poison_timer: float = 0.0
var poison_damage: int = 0
var poison_tick_rate: float = 1.0

# Battle cry buff
var damage_buff_mult: float = 1.0
var damage_buff_timer: float = 0.0

# Chapter Stars (chapter_id → 1-3 stars)
# ⭐ = complete the chapter
# ⭐⭐ = complete without dying
# ⭐⭐⭐ = complete under par time
var chapter_stars: Dictionary = {}

# Bestiary — delegated to BestiaryManager autoload
# Use BestiaryManager.BESTIARY for data, GameState.BESTIARY for backward compat
var BESTIARY: Dictionary:
	get:
		return BestiaryManager.BESTIARY

# Kill tracking: enemy_type → total kill count (persisted)
var bestiary: Dictionary = {}  # enemy_type → {"kills": int, "lore_unlocked": [int]}

# ─── Achievement Badges ──────────────────────────────────────────────────────
# Delegated to AchievementTracker autoload
var ACHIEVEMENTS: Dictionary:
	get:
		return AchievementTracker.ACHIEVEMENTS

var achievements_unlocked: Dictionary = {}  # achievement_id → timestamp
signal achievement_unlocked(achievement_id: String, achievement_data: Dictionary)
# ─── Daily Login Streak ───────────────────────────────────────────────────────
# Consecutive days played → escalating gold + potion rewards
# Streak breaks if >24h since last login
# Streak caps at 7 days, then cycles (day 8 = day 1 rewards again, streak counter keeps going)

# Streak rewards — delegated to GameState logic, data kept inline
const STREAK_REWARDS := {
	1: {"gold": 10, "potions": 0, "label": "Day 1 — 10g"},
	2: {"gold": 20, "potions": 1, "label": "Day 2 — 20g + 1🧪"},
	3: {"gold": 30, "potions": 1, "label": "Day 3 — 30g + 1🧪"},
	4: {"gold": 50, "potions": 2, "label": "Day 4 — 50g + 2🧪"},
	5: {"gold": 75, "potions": 2, "label": "Day 5 — 75g + 2🧪"},
	6: {"gold": 100, "potions": 3, "label": "Day 6 — 100g + 3🧪"},
	7: {"gold": 150, "potions": 3, "label": "Day 7 — 150g + 3🧪 🔥"},
}

var daily_streak: int = 0
var last_login_date: String = ""
var streak_claimed_today: bool = false
signal streak_claimed(streak_day: int, rewards: Dictionary)

# Daily challenge modifiers — delegated to DailyChallengeManager autoload
var DAILY_CHALLENGE_MODIFIERS: Dictionary:
	get:
		return DailyChallengeManager.DAILY_CHALLENGE_MODIFIERS

# Daily challenge state
var daily_challenge_completed_today: bool = false
var daily_challenge_best_gold: int = 0  # Lifetime best gold from daily challenges
var daily_challenge_total_completed: int = 0  # Lifetime total completions
signal daily_challenge_completed(rewards: Dictionary)

# Daily challenge runtime state (not persisted, set when starting a challenge)
var is_daily_challenge_run: bool = false
var active_daily_modifiers: Array = []  # Array of modifier IDs active this run

# Loot tracking
var chapter_loot: Array = []  # Runtime: items dropped this chapter run
var collected_weapons: Dictionary = {}  # weapon_id → {"count": int, "best_rarity": String}

# Chapter performance tracking (runtime, reset per chapter)
var chapter_start_time: float = 0.0
var chapter_deaths: int = 0

# Ghost run settings (persisted)
var ghost_runs_enabled: bool = true  # Whether to show ghost replays

# ─── Rested XP System ──────────────────────────────────────────────────────
# Offline time accumulates bonus XP: 1 rested XP per 2 minutes offline
# Max cap: 1000 rested XP (≈33 hours offline)
# On next chapter completion, rested XP is added as bonus XP (2× multiplier)
const RESTED_XP_RATE := 0.5  # rested XP per minute offline
const RESTED_XP_CAP := 1000
var rested_xp: int = 0  # Accumulated rested bonus XP
var last_logout_time: float = 0.0  # Unix timestamp of last save/close


func _ready():
	load_game()
	_check_daily_streak()
	_calculate_rested_xp()
	if OS.has_feature("web"):
		_start_autosave()
	print(
		(
			"GameState loaded — Act %d, Ch %d, Level %d, Weapon: %s, Skills: %s, Streak: %d, Rested XP: %d"
			% [
				current_act,
				current_chapter,
				player_level,
				equipped_weapon,
				str(equipped_skills),
				daily_streak,
				rested_xp
			]
		)
	)


func _notification(what):
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		save_game()


func _migrate_save(data: Dictionary) -> Dictionary:
	return SaveManager._migrate_save(data)


func _get_save_key() -> PackedByteArray:
	return SaveManager._get_save_key()


func _encrypt(plaintext: String) -> String:
	return SaveManager._encrypt(plaintext)


func _decrypt(ciphertext: String) -> String:
	return SaveManager._decrypt(ciphertext)


func save_game():
	var data := {
		"version": "2.6",
		"current_act": current_act,
		"current_chapter": current_chapter,
		"completed_chapters": completed_chapters,
		"player_level": player_level,
		"player_xp": player_xp,
		"player_gold": player_gold,
		"unlocked_weapons": unlocked_weapons,
		"unlocked_skills": unlocked_skills,
		"equipped_weapon": equipped_weapon,
		"equipped_skills": equipped_skills,
		"saved_health": saved_health,
		"saved_max_health": saved_max_health,
		"has_gate_key": has_gate_key,
		"inventory": inventory,
		"settings": settings,
		"chapter_stars": chapter_stars,
		"collected_weapons": collected_weapons,
		"bestiary": bestiary,
		"total_crits": total_crits,
		"achievements_unlocked": achievements_unlocked,
		"daily_streak": daily_streak,
		"last_login_date": last_login_date,
		"streak_claimed_today": streak_claimed_today,
		"daily_challenge_completed_today": daily_challenge_completed_today,
		"daily_challenge_best_gold": daily_challenge_best_gold,
		"daily_challenge_total_completed": daily_challenge_total_completed,
		"ghost_runs_enabled": ghost_runs_enabled,
		"rested_xp": rested_xp,
		"last_logout_time": Time.get_unix_time_from_system(),
	}

	var file := FileAccess.open(SAVE_FILE, FileAccess.WRITE)
	if file:
		file.store_string(_encrypt(JSON.stringify(data, "\t")))
		file.close()
		_save_indexeddb()
		print("Game saved")
	else:
		push_error("Failed to save game")


func load_game():
	if not FileAccess.file_exists(SAVE_FILE):
		print("No save file — starting fresh")
		return

	var file := FileAccess.open(SAVE_FILE, FileAccess.READ)
	if file == null:
		push_error("Cannot read save file")
		return

	var text := _decrypt(file.get_as_text())
	file.close()

	var json = JSON.new()
	var err := json.parse(text)
	if err != OK:
		push_error("Save file corrupt — starting fresh")
		return

	var data = json.data
	if data is Dictionary:
		data = _migrate_save(data)
		current_act = data.get("current_act", 1)
		current_chapter = data.get("current_chapter", 1)
		completed_chapters = data.get("completed_chapters", [])
		player_level = data.get("player_level", 1)
		player_xp = data.get("player_xp", 0)
		player_gold = data.get("player_gold", 0)
		unlocked_weapons = data.get("unlocked_weapons", [])
		unlocked_skills = data.get("unlocked_skills", [])
		equipped_weapon = data.get("equipped_weapon", "broken_sword")
		equipped_skills = data.get("equipped_skills", ["dodge_roll"])
		saved_health = data.get("saved_health", 100)
		saved_max_health = data.get("saved_max_health", 100)
		has_gate_key = data.get("has_gate_key", false)
		inventory = data.get("inventory", {"potions": 0, "keys": {}, "artifacts": [], "gold": 0})
		chapter_stars = data.get("chapter_stars", {})
		collected_weapons = data.get("collected_weapons", {})
		bestiary = data.get("bestiary", {})
		total_crits = data.get("total_crits", 0)
		achievements_unlocked = data.get("achievements_unlocked", {})
		daily_streak = data.get("daily_streak", 0)
		last_login_date = data.get("last_login_date", "")
		streak_claimed_today = data.get("streak_claimed_today", false)
		daily_challenge_completed_today = data.get("daily_challenge_completed_today", false)
		daily_challenge_best_gold = data.get("daily_challenge_best_gold", 0)
		daily_challenge_total_completed = data.get("daily_challenge_total_completed", 0)
		ghost_runs_enabled = data.get("ghost_runs_enabled", true)
		rested_xp = data.get("rested_xp", 0)
		last_logout_time = data.get("last_logout_time", 0.0)
		settings = (
			data
			. get(
				"settings",
				{
					"master_volume": 1.0,
					"sfx_volume": 1.0,
					"bgm_volume": 0.7,
					"screen_shake": true,
					"hit_stop": true,
					"show_damage_numbers": true,
					"auto_aim": false,
					"text_speed": 1.0,
				}
			)
		)
		print(
			(
				"Save loaded — HP %d/%d, weapon: %s, skills: %s"
				% [saved_health, saved_max_health, equipped_weapon, str(equipped_skills)]
			)
		)


func apply_settings():
	SettingsManager.settings = settings
	SettingsManager.apply_settings()


func complete_current_chapter():
	var chapter_id := "act%02d_ch%03d" % [current_act, current_chapter]
	if not completed_chapters.has(chapter_id):
		completed_chapters.append(chapter_id)

	# Calculate stars based on performance
	var elapsed := (Time.get_ticks_msec() / 1000.0) - chapter_start_time
	var stars := calculate_stars(chapter_id, chapter_deaths, elapsed)
	print(
		(
			"Chapter %s complete — %d stars (deaths: %d, time: %.1fs)"
			% [chapter_id, stars, chapter_deaths, elapsed]
		)
	)

	var next_chapter_id_raw = ChapterDatabase.get_current_chapter().get("next_chapter", "")
	var next_chapter_id: String = "" if next_chapter_id_raw == null else str(next_chapter_id_raw)
	if next_chapter_id != "" and ChapterDatabase.chapters.has(next_chapter_id):
		ChapterDatabase.chapters[next_chapter_id]["is_unlocked"] = true

	var rewards = ChapterDatabase.get_current_chapter().get("rewards", {})
	player_xp += rewards.get("xp", 0)
	player_gold += rewards.get("gold", 0)
	inventory["gold"] = player_gold

	if rewards.has("unlock_weapon"):
		var w = rewards.unlock_weapon
		if w not in unlocked_weapons:
			unlocked_weapons.append(w)
		_auto_equip_best_weapon()
	if rewards.has("unlock_skill"):
		var s = rewards.unlock_skill
		if s not in unlocked_skills:
			unlocked_skills.append(s)
		if equipped_skills.size() < 3:
			equipped_skills.append(s)

	saved_health = mini(saved_health + 25, saved_max_health)

	# Check chapter-based achievements
	check_chapter_achievements(chapter_deaths, stars)

	save_game()


func calculate_stars(chapter_id: String, deaths: int, elapsed_time: float) -> int:
	# ⭐ = complete (always at least 1)
	# ⭐⭐ = no deaths
	# ⭐⭐⭐ = no deaths + under par time
	var stars := 1
	if deaths == 0:
		stars = 2
	# Par time per chapter (seconds) — generous targets
	var par_times := {
		"act01_ch001": 60,
		"act01_ch002": 75,
		"act01_ch003": 90,
		"act01_ch004": 120,
		"act02_ch005": 75,
		"act02_ch006": 90,
		"act02_ch007": 90,
		"act02_ch008": 120,
		"act02_ch009": 120,
		"act02_ch010": 150,
		"act03_ch011": 90,
		"act03_ch012": 150,
		"act03_ch013": 120,
		"act03_ch014": 180,
		"act03_ch015": 150,
		"act04_ch016": 120,
		"act04_ch017": 150,
		"act04_ch018": 120,
		"act04_ch019": 180,
		"act04_ch020": 240,
		"act05_ch021": 150,
		"act05_ch022": 180,
		"act05_ch023": 200,
		"act05_ch024": 240,
		"act05_ch025": 360,
		"act06_ch026": 180,
		"act06_ch027": 200,
		"act06_ch028": 220,
		"act06_ch029": 260,
		"act06_ch030": 360,
	}
	var par_time: float = par_times.get(chapter_id, 120.0)
	if deaths == 0 and elapsed_time <= par_time:
		stars = 3
	# Only upgrade, never downgrade
	if chapter_stars.get(chapter_id, 0) < stars:
		chapter_stars[chapter_id] = stars
	return stars


func get_stars(chapter_id: String) -> int:
	return chapter_stars.get(chapter_id, 0)


func get_total_stars() -> int:
	var total := 0
	for stars in chapter_stars.values():
		total += stars
	return total


func get_max_possible_stars() -> int:
	return ChapterDatabase.chapters.size() * 3


func get_level_xp_requirement(level: int) -> int:
	return level * level * 100


func add_xp(amount: int):
	var actual_xp := amount
	# Consume rested XP bonus: double the base XP up to rested XP cap
	if rested_xp > 0:
		var bonus := mini(rested_xp, amount)  # Match 1:1 with base XP
		actual_xp += bonus
		rested_xp -= bonus
		print("RESTED XP BONUS: +%d XP (rested remaining: %d)" % [bonus, rested_xp])

	player_xp += actual_xp
	var required := get_level_xp_requirement(player_level)
	while player_xp >= required:
		player_xp -= required
		player_level += 1
		saved_max_health += 10
		saved_health = saved_max_health
		print("LEVEL UP! Now level %d — HP %d" % [player_level, saved_max_health])
		if AudioManager.voice_cache.has("level_up"):
			AudioManager.play_voice("level_up")
		required = get_level_xp_requirement(player_level)


func is_chapter_unlocked(act: int, chapter: int) -> bool:
	var id := "act%02d_ch%03d" % [act, chapter]
	if ChapterDatabase.chapters.has(id):
		return ChapterDatabase.chapters[id].get("is_unlocked", false)
	return false


func reset_chapter_state():
	chapter_kills = 0
	chapter_objectives_met.clear()
	poison_timer = 0
	poison_damage = 0
	damage_buff_mult = 1.0
	damage_buff_timer = 0.0
	chapter_start_time = Time.get_ticks_msec() / 1000.0
	chapter_deaths = 0
	chapter_loot.clear()


var _autosave_timer: Timer = null


func _start_autosave():
	_autosave_timer = Timer.new()
	_autosave_timer.wait_time = 60.0
	_autosave_timer.autostart = true
	_autosave_timer.timeout.connect(_on_autosave_timeout)
	add_child(_autosave_timer)


func _on_autosave_timeout():
	save_game()


func _save_indexeddb():
	if OS.has_feature("web"):
		(
			JavaScriptBridge
			. eval(
				"""
			if (typeof Module !== 'undefined' && Module.FS && Module.FS.syncfs) {
				Module.FS.syncfs(false, function(err) {
					if (err) console.error('GameState: syncfs error:', err);
				});
			}
		"""
			)
		)


func add_potion(count: int = 1):
	inventory["potions"] += count
	print("Potions: %d" % inventory["potions"])


func use_potion() -> bool:
	if inventory["potions"] <= 0:
		return false
	inventory["potions"] -= 1
	saved_health = mini(saved_health + 30, saved_max_health)
	print(
		"Used potion! HP: %d/%d (%d left)" % [saved_health, saved_max_health, inventory["potions"]]
	)
	return true


func _auto_equip_best_weapon():
	var best_weapon := "broken_sword"
	var best_dmg: int = 0
	for weapon_id in unlocked_weapons:
		if weapon_id in WEAPON_STATS:
			var dmg: int = WEAPON_STATS[weapon_id].get("damage", 0)
			if dmg > best_dmg:
				best_dmg = dmg
				best_weapon = weapon_id
	if best_weapon != equipped_weapon:
		equipped_weapon = best_weapon
		print(
			(
				"Auto-equipped: %s (DMG %d, CD %.2fs)"
				% [
					equipped_weapon,
					WEAPON_STATS[equipped_weapon].damage,
					WEAPON_STATS[equipped_weapon].cooldown
				]
			)
		)


func get_weapon_stats(weapon_id: String = equipped_weapon) -> Dictionary:
	return WeaponDB.get_weapon_stats(weapon_id)


func get_skill_stats(skill_id: String) -> Dictionary:
	return WeaponDB.get_skill_stats(skill_id)


func equip_weapon(weapon_id: String) -> bool:
	if weapon_id in unlocked_weapons:
		equipped_weapon = weapon_id
		save_game()
		return true
	return false


func equip_skill(skill_id: String, slot: int) -> bool:
	if skill_id not in unlocked_skills:
		return false
	while equipped_skills.size() <= slot:
		equipped_skills.append("")
	equipped_skills[slot] = skill_id
	save_game()
	return true


class ChapterProgress:
	var chapter_id: String
	var best_time: float
	var stars: int = 0
	var completed: bool = false


# ─── Loot Drop System ───────────────────────────────────
# Variable ratio reinforcement: enemies drop loot on death
# Boss/champion kills = guaranteed drop + rare chance
# Trash mob kills = 5% uncommon drop chance


func roll_loot_drop(enemy_type: String, is_boss: bool = false) -> Dictionary:
	"""Roll for a loot drop when an enemy dies. Returns {} if no drop."""
	var rng := RandomNumberGenerator.new()
	rng.randomize()

	# Drop chance: trash 15%, boss/champion 100%
	var drop_chance := 1.0 if is_boss else 0.15
	if rng.randf() > drop_chance:
		return {}

	# Roll rarity: weighted random from RARITY
	var rarity := _roll_rarity(is_boss)

	# Pick a weapon of that rarity (or nearest lower)
	var weapon_id := _pick_weapon_by_rarity(rarity)
	if weapon_id.is_empty():
		return {}

	var loot := {
		"weapon_id": weapon_id,
		"rarity": rarity,
		"gold_value": _gold_value_for_rarity(rarity),
	}

	# Track in chapter loot
	chapter_loot.append(loot)

	# If weapon not yet owned, unlock it
	if weapon_id not in unlocked_weapons:
		unlocked_weapons.append(weapon_id)
		_auto_equip_best_weapon()
		loot["is_new"] = true
		if AudioManager.voice_cache.has("weapon_unlocked"):
			AudioManager.play_voice("weapon_unlocked")
	else:
		loot["is_new"] = false

	# Update collection tracking
	if not collected_weapons.has(weapon_id):
		collected_weapons[weapon_id] = {"count": 0, "best_rarity": rarity}
	collected_weapons[weapon_id]["count"] += 1
	var rarity_order := ["common", "uncommon", "rare", "legendary"]
	var current_rank := rarity_order.find(collected_weapons[weapon_id]["best_rarity"])
	var new_rank := rarity_order.find(rarity)
	if new_rank > current_rank:
		collected_weapons[weapon_id]["best_rarity"] = rarity

	# Add gold value
	player_gold += loot.gold_value
	inventory["gold"] = player_gold

	print(
		(
			"LOOT DROP: %s [%s] (gold: %d)%s"
			% [weapon_id, rarity, loot.gold_value, " NEW!" if loot.get("is_new") else " dup"]
		)
	)

	# Check loot achievements
	check_loot_achievements(rarity)

	save_game()
	return loot


func _roll_rarity(is_boss: bool) -> String:
	"""Weighted random rarity roll. Bosses get +15% to rare/legendary."""
	var rng := RandomNumberGenerator.new()
	rng.randomize()

	var weights := {}
	for r in RARITY.keys():
		weights[r] = RARITY[r].weight

	# Boss bonus: shift weight from common up to rare/legendary
	if is_boss:
		weights["common"] = max(10, weights["common"] - 30)
		weights["uncommon"] += 10
		weights["rare"] += 12
		weights["legendary"] += 8

	var total := 0.0
	for w in weights.values():
		total += w

	var roll := rng.randf() * total
	var cumulative := 0.0
	for r in ["legendary", "rare", "uncommon", "common"]:
		cumulative += weights[r]
		if roll <= cumulative:
			return r
	return "common"


func _pick_weapon_by_rarity(rarity: String) -> String:
	"""Pick a weapon matching the rolled rarity. Falls back to lower rarity."""
	var rarity_order := ["legendary", "rare", "uncommon", "common"]
	var target_idx := rarity_order.find(rarity)

	# Try exact rarity first, then fall back to lower
	for i in range(target_idx, rarity_order.size()):
		var r: String = rarity_order[i]
		var candidates: Array = []
		for wid in WEAPON_STATS.keys():
			if WEAPON_STATS[wid].get("rarity", "common") == r:
				candidates.append(wid)
		if not candidates.is_empty():
			candidates.sort()
			var rng := RandomNumberGenerator.new()
			rng.randomize()
			return candidates[rng.randi() % candidates.size()]
	return ""


func _gold_value_for_rarity(rarity: String) -> int:
	match rarity:
		"common":
			return 5
		"uncommon":
			return 15
		"rare":
			return 40
		"legendary":
			return 100
		_:
			return 5


func get_loot_summary() -> Dictionary:
	"""Get summary of chapter loot for victory screen."""
	var by_rarity := {}
	for loot in chapter_loot:
		var r: String = loot.get("rarity", "common")
		if not by_rarity.has(r):
			by_rarity[r] = {"count": 0, "items": [], "gold": 0}
		by_rarity[r].count += 1
		by_rarity[r].items.append(loot.weapon_id)
		by_rarity[r].gold += loot.get("gold_value", 0)
	return {
		"total_drops": chapter_loot.size(),
		"total_gold": chapter_loot.reduce(func(acc, l): return acc + l.get("gold_value", 0), 0),
		"new_weapons": chapter_loot.filter(func(l): return l.get("is_new", false)).size(),
		"by_rarity": by_rarity,
	}


func get_collection_progress() -> Dictionary:
	"""Get weapon collection stats for UI."""
	var total_weapons := WEAPON_STATS.size()
	var collected := collected_weapons.size()
	return {
		"total": total_weapons,
		"collected": collected,
		"percentage": (collected * 100.0 / total_weapons) if total_weapons > 0 else 0.0,
	}


# ─── Bestiary ─────────────────────────────────────────────────────────────────


func record_kill(enemy_type: String) -> void:
	"""Record a kill in the bestiary. Delegates to BestiaryManager."""
	BestiaryManager.record_kill(enemy_type)
	bestiary = BestiaryManager.bestiary
	chapter_kills += 1

	# Check for lore unlock milestones (logging)
	if BestiaryManager.BESTIARY.has(enemy_type):
		var entry: Dictionary = BestiaryManager.BESTIARY[enemy_type]
		var kills: int = BestiaryManager.bestiary.get(enemy_type, {}).get("kills", 0)
		var lore_milestones: Array = entry.get("lore", {}).keys()
		lore_milestones.sort()
		for milestone in lore_milestones:
			if kills >= milestone:
				print("BESTIARY LORE UNLOCK: %s at %d kills" % [entry.name, milestone])


func record_crit() -> void:
	"""Record a critical hit. Call from player on crit."""
	total_crits += 1
	if total_crits >= 50:
		unlock_achievement("crit_50")

	# Check kill-based achievements
	check_achievements()
	save_game()


func get_bestiary_entry(enemy_type: String) -> Dictionary:
	return BestiaryManager.get_bestiary_entry(enemy_type)


func get_bestiary_progress() -> Dictionary:
	return BestiaryManager.get_bestiary_progress()


# ─── Achievement System ─────────────────────────────────────────────────────


func unlock_achievement(achievement_id: String) -> bool:
	var result := AchievementTracker.unlock_achievement(achievement_id)
	if result:
		achievements_unlocked = AchievementTracker.achievements_unlocked
		achievement_unlocked.emit(
			achievement_id, AchievementTracker.ACHIEVEMENTS.get(achievement_id, {})
		)
		save_game()
	return result


func is_achievement_unlocked(achievement_id: String) -> bool:
	return AchievementTracker.is_achievement_unlocked(achievement_id)


func check_achievements() -> void:
	"""Check all achievement conditions and unlock any that are met. Call at key moments."""
	var total_kills := 0
	for enemy_type in bestiary:
		total_kills += bestiary[enemy_type].get("kills", 0)

	var completed_count := completed_chapters.size()
	var weapons_count := collected_weapons.size()
	var discovered_enemies := 0
	for enemy_type in BESTIARY:
		if bestiary.get(enemy_type, {}).get("kills", 0) > 0:
			discovered_enemies += 1

	var three_star_count := 0
	for stars in chapter_stars.values():
		if stars >= 3:
			three_star_count += 1

	# Combat
	if total_kills >= 1:
		unlock_achievement("first_blood")
	if total_kills >= 50:
		unlock_achievement("body_count_50")
	if total_kills >= 200:
		unlock_achievement("body_count_200")

	# Exploration
	if completed_count >= 1:
		unlock_achievement("first_step")
	if completed_count >= 5:
		unlock_achievement("half_way")
	if current_act >= 2 or completed_count >= 4:
		unlock_achievement("act2_reacher")
	if current_act >= 3 or completed_count >= 10:
		unlock_achievement("act3_reacher")
	if completed_count >= 15:
		unlock_achievement("act3_complete")
	if current_act >= 4 or completed_count >= 16:
		unlock_achievement("act4_reacher")
	if completed_count >= 20:
		unlock_achievement("act4_complete")
	if current_act >= 5 or completed_count >= 21:
		unlock_achievement("act5_reacher")
	if completed_count >= 25:
		unlock_achievement("act5_complete")
	if current_act >= 6 or completed_count >= 26:
		unlock_achievement("act6_reacher")
	if completed_count >= 30:
		unlock_achievement("act6_complete")

	# Collection
	if weapons_count >= 3:
		unlock_achievement("armory_3")
	if weapons_count >= WEAPON_STATS.size():
		unlock_achievement("armory_all")
	if discovered_enemies >= 4:
		unlock_achievement("bestiary_half")
	if discovered_enemies >= BESTIARY.size():
		unlock_achievement("bestiary_all")

	# Mastery
	if three_star_count >= 1:
		unlock_achievement("speed_demon")
	if three_star_count >= 5:
		unlock_achievement("perfectionist")


func check_chapter_achievements(deaths: int, stars: int) -> void:
	"""Check achievements that depend on chapter performance. Call after chapter completion."""
	if deaths == 0:
		unlock_achievement("flawless_chapter")
	if stars >= 3:
		unlock_achievement("speed_demon")

	# Speed Demon: 3-star 5 different chapters
	var three_star_count := 0
	for chapter_id in chapter_stars:
		if chapter_stars[chapter_id] >= 3:
			three_star_count += 1
	if three_star_count >= 5:
		unlock_achievement("speed_demon_5")

	# Re-check general achievements too
	check_achievements()


func check_ghost_achievement(chapter_id: String, completion_time: float) -> void:
	"""Check if player beat their ghost. Called after chapter completion if ghost was active."""
	var best_time := GhostRecorder.get_best_time(chapter_id)
	if best_time > 0 and completion_time < best_time:
		unlock_achievement("ghost_hunter")


func check_loot_achievements(rarity: String) -> void:
	"""Check achievements that depend on loot drops. Call after loot roll."""
	if rarity == "legendary":
		unlock_achievement("legendary_find")
	check_achievements()


func get_achievement_progress() -> Dictionary:
	return AchievementTracker.get_achievement_progress()


func get_achievements_by_category() -> Dictionary:
	return AchievementTracker.get_achievements_by_category()


# ─── Daily Login Streak System ──────────────────────────────────────────────


func _check_daily_streak() -> void:
	"""Check and update daily login streak. Call on game startup."""
	var today := Time.get_datetime_string_from_system().split(" ")[0]  # YYYY-MM-DD

	# Guard against malformed/empty saved dates
	if last_login_date.is_empty() or not _is_valid_date_string(last_login_date):
		# First ever login (or corrupted save)
		daily_streak = 1
		last_login_date = today
		streak_claimed_today = false
		daily_challenge_completed_today = false  # New day = fresh challenge
		print("STREAK: First login! Day 1")
		return

	if last_login_date == today:
		# Same day — already logged in today
		print("STREAK: Already logged in today (day %d)" % daily_streak)
		return

	# New day — reset daily challenge
	daily_challenge_completed_today = false

	# Check if yesterday was the last login (consecutive)
	var yesterday := _get_yesterday_date(last_login_date)
	if today == yesterday or _is_next_day(last_login_date, today):
		# Consecutive day
		daily_streak += 1
		last_login_date = today
		streak_claimed_today = false
		print("STREAK: Consecutive! Day %d" % daily_streak)
	else:
		# Streak broken — missed a day
		daily_streak = 1
		last_login_date = today
		streak_claimed_today = false
		print("STREAK: Broken! Reset to day 1")


func claim_daily_streak() -> Dictionary:
	"""Claim today's streak reward. Returns reward dict or empty if already claimed."""
	if streak_claimed_today:
		return {}

	var reward_day := ((daily_streak - 1) % 7) + 1  # Cycle 1-7
	var rewards: Dictionary = STREAK_REWARDS.get(reward_day, STREAK_REWARDS[1]).duplicate()

	# Apply rewards
	player_gold += rewards.get("gold", 0)
	inventory["gold"] = player_gold
	add_potion(rewards.get("potions", 0))

	streak_claimed_today = true
	print("STREAK CLAIMED: Day %d → %s" % [daily_streak, rewards.get("label", "")])
	AudioManager.play_sfx("streak_claim")
	streak_claimed.emit(daily_streak, rewards)

	# Check streak achievements
	_check_streak_achievements()

	save_game()
	return rewards


func get_streak_info() -> Dictionary:
	"""Get streak status for UI display."""
	var reward_day := ((daily_streak - 1) % 7) + 1
	var next_reward: Dictionary = STREAK_REWARDS.get(reward_day, STREAK_REWARDS[1])
	return {
		"streak": daily_streak,
		"reward_day": reward_day,
		"claimed_today": streak_claimed_today,
		"next_reward": next_reward,
		"days_to_cycle": 7 - reward_day,
	}


func _check_streak_achievements() -> void:
	"""Check streak-related achievements."""
	if daily_streak >= 3:
		unlock_achievement("streak_3")
	if daily_streak >= 7:
		unlock_achievement("streak_7")


func _is_valid_date_string(date_str: String) -> bool:
	"""Validate YYYY-MM-DD format and sane values."""
	var parts := date_str.split("-")
	if parts.size() != 3:
		return false
	var year := int(parts[0])
	var month := int(parts[1])
	var day := int(parts[2])
	if year < 2020 or year > 2100 or month < 1 or month > 12 or day < 1 or day > 31:
		return false
	return true


func _get_yesterday_date(date_str: String) -> String:
	"""Get the date string for the day before the given date."""
	if not _is_valid_date_string(date_str):
		return ""
	var parts := date_str.split("-")
	var year := int(parts[0])
	var month := int(parts[1])
	var day := int(parts[2])

	# Convert to unix timestamp and subtract 86400
	var epoch := Time.get_unix_time_from_datetime_dict(
		{"year": year, "month": month, "day": day, "hour": 12, "minute": 0, "second": 0}
	)
	var yesterday_epoch := epoch - 86400
	var yesterday_dict := Time.get_datetime_dict_from_unix_time(yesterday_epoch)
	return (
		"%04d-%02d-%02d" % [yesterday_dict["year"], yesterday_dict["month"], yesterday_dict["day"]]
	)


func _is_next_day(date1: String, date2: String) -> bool:
	"""Check if date2 is the day after date1."""
	var parts1 := date1.split("-")
	var parts2 := date2.split("-")
	var epoch1 := Time.get_unix_time_from_datetime_dict(
		{
			"year": int(parts1[0]),
			"month": int(parts1[1]),
			"day": int(parts1[2]),
			"hour": 12,
			"minute": 0,
			"second": 0
		}
	)
	var epoch2 := Time.get_unix_time_from_datetime_dict(
		{
			"year": int(parts2[0]),
			"month": int(parts2[1]),
			"day": int(parts2[2]),
			"hour": 12,
			"minute": 0,
			"second": 0
		}
	)
	return (epoch2 - epoch1) <= 86400 and epoch2 > epoch1


# ─── Rested XP System ───────────────────────────────────────────────────────


func _calculate_rested_xp() -> void:
	"""Calculate rested XP accumulated since last logout."""
	if last_logout_time <= 0:
		# First time or no prior logout — no rested XP
		last_logout_time = Time.get_unix_time_from_system()
		return

	var now := Time.get_unix_time_from_system()
	var offline_minutes := (now - last_logout_time) / 60.0

	if offline_minutes < 1.0:
		return  # Less than 1 minute offline — no bonus

	var earned := int(offline_minutes * RESTED_XP_RATE)
	rested_xp = mini(rested_xp + earned, RESTED_XP_CAP)
	last_logout_time = now

	if earned > 0:
		var hours := offline_minutes / 60.0
		print(
			(
				"RESTED XP: Away %.1fh → +%d rested XP (total: %d/%d)"
				% [hours, earned, rested_xp, RESTED_XP_CAP]
			)
		)


func get_rested_xp_info() -> Dictionary:
	"""Get rested XP status for UI display."""
	var is_capped := rested_xp >= RESTED_XP_CAP
	var pct := (rested_xp * 100.0 / RESTED_XP_CAP) if RESTED_XP_CAP > 0 else 0.0
	return {
		"rested_xp": rested_xp,
		"cap": RESTED_XP_CAP,
		"percentage": pct,
		"is_capped": is_capped,
		"has_bonus": rested_xp > 0,
	}


# ─── Daily Challenge System ───────────────────────────────────────────────────


func get_daily_challenge() -> Dictionary:
	return DailyChallengeManager.get_daily_challenge()


func complete_daily_challenge() -> void:
	DailyChallengeManager.complete_daily_challenge()
	daily_challenge_completed_today = DailyChallengeManager.daily_challenge_completed_today
	daily_challenge_best_gold = DailyChallengeManager.daily_challenge_best_gold
	daily_challenge_total_completed = DailyChallengeManager.daily_challenge_total_completed
	var challenge := DailyChallengeManager.get_daily_challenge()
	var bonus_gold: int = (
		challenge.get("bonus_gold", 50)
		if challenge.has("bonus_gold")
		else challenge.get("gold_reward", 50)
	)
	player_gold += bonus_gold
	AudioManager.play_sfx("daily_challenge")
	save_game()


func _check_daily_challenge_achievements() -> void:
	if daily_challenge_total_completed >= 1:
		unlock_achievement("daily_challenger")
	if daily_challenge_total_completed >= 7:
		unlock_achievement("daily_veteran")


func is_daily_challenge_available() -> bool:
	return DailyChallengeManager.is_daily_challenge_available()


func reset_daily_challenge_if_new_day() -> void:
	DailyChallengeManager.reset_daily_challenge_if_new_day()
	daily_challenge_completed_today = DailyChallengeManager.daily_challenge_completed_today


func get_leaderboard_data() -> Array:
	"""Get leaderboard data for all chapters: chapter_id, title, best_time, stars, has_ghost."""
	var result := []
	var sorted_ids := ChapterDatabase.chapters.keys()
	sorted_ids.sort()
	for chapter_id in sorted_ids:
		var ch = ChapterDatabase.chapters[chapter_id]
		if not ch.get("is_unlocked", false):
			continue
		var entry := {
			"chapter_id": chapter_id,
			"title": ch.get("title", chapter_id),
			"best_time": GhostRecorder.get_best_time(chapter_id),
			"stars": get_stars(chapter_id),
			"has_ghost": GhostRecorder.has_ghost(chapter_id),
		}
		result.append(entry)
	return result

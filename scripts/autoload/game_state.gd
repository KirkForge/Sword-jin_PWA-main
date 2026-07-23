extends Node
# gdlint:ignore=max-public-methods,max-file-lines
# GameState — Persistent save/load + progression tracking
# v0.89 — decomposed into subsystem autoloads: SaveManager, WeaponDB, AchievementTracker,
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
var settings: Dictionary = SettingsManager.DEFAULT_SETTINGS.duplicate()

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

# Delegated to AchievementTracker autoload
var ACHIEVEMENTS: Dictionary:
	get:
		return AchievementTracker.ACHIEVEMENTS

var achievements_unlocked: Dictionary = {}  # achievement_id → timestamp
signal achievement_unlocked(achievement_id: String, achievement_data: Dictionary)

var STREAK_REWARDS: Dictionary:
	get:
		return StreakManager.STREAK_REWARDS

var daily_streak: int:
	get:
		return StreakManager.daily_streak
	set(v):
		StreakManager.daily_streak = v

var last_login_date: String:
	get:
		return StreakManager.last_login_date
	set(v):
		StreakManager.last_login_date = v

var streak_claimed_today: bool:
	get:
		return StreakManager.streak_claimed_today
	set(v):
		StreakManager.streak_claimed_today = v

signal streak_claimed(streak_day: int, rewards: Dictionary)

# Daily challenge modifiers — delegated to DailyChallengeManager autoload
var DAILY_CHALLENGE_MODIFIERS: Dictionary:
	get:
		return DailyChallengeManager.DAILY_CHALLENGE_MODIFIERS

# Daily challenge state
var daily_challenge_completed_today: bool = false
var daily_challenge_best_gold: int = 0
var daily_challenge_total_completed: int = 0
signal daily_challenge_completed(rewards: Dictionary)

# Daily challenge runtime state (not persisted, set when starting a challenge)
var is_daily_challenge_run: bool = false
var active_daily_modifiers: Array = []

# Loot tracking
var chapter_loot: Array = []
var collected_weapons: Dictionary = {}

# Chapter performance tracking (runtime, reset per chapter)
var chapter_start_time: float = 0.0
var chapter_deaths: int = 0

# Ghost run settings (persisted)
var ghost_runs_enabled: bool = true

var RESTED_XP_RATE: float:
	get:
		return StreakManager.RESTED_XP_RATE

var RESTED_XP_CAP: int:
	get:
		return StreakManager.RESTED_XP_CAP

var rested_xp: int:
	get:
		return StreakManager.rested_xp
	set(v):
		StreakManager.rested_xp = v

var last_logout_time: float:
	get:
		return StreakManager.last_logout_time
	set(v):
		StreakManager.last_logout_time = v


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
		settings = data.get("settings", SettingsManager.DEFAULT_SETTINGS.duplicate())
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


func roll_loot_drop(enemy_type: String, is_boss: bool = false) -> Dictionary:
	var rng := RandomNumberGenerator.new()
	rng.randomize()

	var drop_chance := 1.0 if is_boss else 0.15
	if rng.randf() > drop_chance:
		return {}

	var rarity := WeaponDB.roll_rarity(is_boss)
	var weapon_id := WeaponDB.pick_weapon_by_rarity(rarity)
	if weapon_id.is_empty():
		return {}

	var loot := {
		"weapon_id": weapon_id,
		"rarity": rarity,
		"gold_value": WeaponDB.gold_value_for_rarity(rarity),
	}

	chapter_loot.append(loot)

	if weapon_id not in unlocked_weapons:
		unlocked_weapons.append(weapon_id)
		_auto_equip_best_weapon()
		loot["is_new"] = true
		if AudioManager.voice_cache.has("weapon_unlocked"):
			AudioManager.play_voice("weapon_unlocked")
	else:
		loot["is_new"] = false

	if not collected_weapons.has(weapon_id):
		collected_weapons[weapon_id] = {"count": 0, "best_rarity": rarity}
	collected_weapons[weapon_id]["count"] += 1
	var rarity_order := ["common", "uncommon", "rare", "legendary"]
	var current_rank := rarity_order.find(collected_weapons[weapon_id]["best_rarity"])
	var new_rank := rarity_order.find(rarity)
	if new_rank > current_rank:
		collected_weapons[weapon_id]["best_rarity"] = rarity

	player_gold += loot.gold_value
	inventory["gold"] = player_gold

	print(
		(
			"LOOT DROP: %s [%s] (gold: %d)%s"
			% [weapon_id, rarity, loot.gold_value, " NEW!" if loot.get("is_new") else " dup"]
		)
	)

	AchievementTracker.check_loot_achievements(rarity)

	save_game()
	return loot


func get_loot_summary() -> Dictionary:
	return WeaponDB.get_loot_summary(chapter_loot)


func get_collection_progress() -> Dictionary:
	return WeaponDB.get_collection_progress(collected_weapons)


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

	AchievementTracker.check_achievements(
		total_kills,
		completed_count,
		weapons_count,
		discovered_enemies,
		BESTIARY.size(),
		three_star_count,
		current_act
	)
	sync_achievements()


func check_chapter_achievements(deaths: int, stars: int) -> void:
	AchievementTracker.check_chapter_achievements(deaths, stars, chapter_stars)
	sync_achievements()
	check_achievements()


func check_ghost_achievement(chapter_id: String, completion_time: float) -> void:
	AchievementTracker.check_ghost_achievement(chapter_id, completion_time)
	sync_achievements()


func check_loot_achievements(rarity: String) -> void:
	AchievementTracker.check_loot_achievements(rarity)
	sync_achievements()
	check_achievements()


func get_achievement_progress() -> Dictionary:
	return AchievementTracker.get_achievement_progress()


func get_achievements_by_category() -> Dictionary:
	return AchievementTracker.get_achievements_by_category()


func _check_daily_streak() -> void:
	StreakManager.check_daily_streak()
	daily_streak = StreakManager.daily_streak
	last_login_date = StreakManager.last_login_date
	streak_claimed_today = StreakManager.streak_claimed_today


func claim_daily_streak() -> Dictionary:
	var rewards := StreakManager.claim_daily_streak(self)
	daily_streak = StreakManager.daily_streak
	streak_claimed_today = StreakManager.streak_claimed_today
	return rewards


func get_streak_info() -> Dictionary:
	return StreakManager.get_streak_info()


func sync_achievements() -> void:
	achievements_unlocked = AchievementTracker.achievements_unlocked


func _calculate_rested_xp() -> void:
	StreakManager.calculate_rested_xp()
	rested_xp = StreakManager.rested_xp
	last_logout_time = StreakManager.last_logout_time


func get_rested_xp_info() -> Dictionary:
	return StreakManager.get_rested_xp_info()


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
	AchievementTracker.check_daily_challenge_achievements(daily_challenge_total_completed)
	sync_achievements()
	AudioManager.play_sfx("daily_challenge")
	save_game()


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

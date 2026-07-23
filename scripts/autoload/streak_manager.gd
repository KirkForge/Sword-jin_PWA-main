extends Node
## StreakManager — Daily login streak and rested XP subsystem.
## Extracted from GameState for testability and separation of concerns.

const STREAK_REWARDS := {
	1: {"gold": 10, "potions": 0, "label": "Day 1 — 10g"},
	2: {"gold": 20, "potions": 1, "label": "Day 2 — 20g + 1🧪"},
	3: {"gold": 30, "potions": 1, "label": "Day 3 — 30g + 1🧪"},
	4: {"gold": 50, "potions": 2, "label": "Day 4 — 50g + 2🧪"},
	5: {"gold": 75, "potions": 2, "label": "Day 5 — 75g + 2🧪"},
	6: {"gold": 100, "potions": 3, "label": "Day 6 — 100g + 3🧪"},
	7: {"gold": 150, "potions": 3, "label": "Day 7 — 150g + 3🧪 🔥"},
}

const RESTED_XP_RATE := 0.5
const RESTED_XP_CAP := 1000

var daily_streak: int = 0
var last_login_date: String = ""
var streak_claimed_today: bool = false
var rested_xp: int = 0
var last_logout_time: float = 0.0

signal streak_claimed(streak_day: int, rewards: Dictionary)


func check_daily_streak() -> void:
	var today := Time.get_datetime_string_from_system().split(" ")[0]

	if last_login_date.is_empty() or not is_valid_date_string(last_login_date):
		daily_streak = 1
		last_login_date = today
		streak_claimed_today = false
		print("STREAK: First login! Day 1")
		return

	if last_login_date == today:
		print("STREAK: Already logged in today (day %d)" % daily_streak)
		return

	if today == get_yesterday_date(last_login_date) or is_next_day(last_login_date, today):
		daily_streak += 1
		last_login_date = today
		streak_claimed_today = false
		print("STREAK: Consecutive! Day %d" % daily_streak)
	else:
		daily_streak = 1
		last_login_date = today
		streak_claimed_today = false
		print("STREAK: Broken! Reset to day 1")


func claim_daily_streak(gs) -> Dictionary:
	if streak_claimed_today:
		return {}

	var reward_day := ((daily_streak - 1) % 7) + 1
	var rewards: Dictionary = STREAK_REWARDS.get(reward_day, STREAK_REWARDS[1]).duplicate()

	gs.player_gold += rewards.get("gold", 0)
	gs.inventory["gold"] = gs.player_gold
	gs.add_potion(rewards.get("potions", 0))

	streak_claimed_today = true
	print("STREAK CLAIMED: Day %d → %s" % [daily_streak, rewards.get("label", "")])
	AudioManager.play_sfx("streak_claim")
	streak_claimed.emit(daily_streak, rewards)

	if daily_streak >= 3:
		gs.unlock_achievement("streak_3")
	if daily_streak >= 7:
		gs.unlock_achievement("streak_7")

	gs.save_game()
	return rewards


func get_streak_info() -> Dictionary:
	var reward_day := ((daily_streak - 1) % 7) + 1
	var next_reward: Dictionary = STREAK_REWARDS.get(reward_day, STREAK_REWARDS[1])
	return {
		"streak": daily_streak,
		"reward_day": reward_day,
		"claimed_today": streak_claimed_today,
		"next_reward": next_reward,
		"days_to_cycle": 7 - reward_day,
	}


func calculate_rested_xp() -> void:
	if last_logout_time <= 0:
		last_logout_time = Time.get_unix_time_from_system()
		return

	var now := Time.get_unix_time_from_system()
	var offline_minutes := (now - last_logout_time) / 60.0

	if offline_minutes < 1.0:
		return

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
	var is_capped := rested_xp >= RESTED_XP_CAP
	var pct := (rested_xp * 100.0 / RESTED_XP_CAP) if RESTED_XP_CAP > 0 else 0.0
	return {
		"rested_xp": rested_xp,
		"cap": RESTED_XP_CAP,
		"percentage": pct,
		"is_capped": is_capped,
		"has_bonus": rested_xp > 0,
	}


func is_valid_date_string(date_str: String) -> bool:
	var parts := date_str.split("-")
	if parts.size() != 3:
		return false
	var year := int(parts[0])
	var month := int(parts[1])
	var day := int(parts[2])
	if year < 2020 or year > 2100 or month < 1 or month > 12 or day < 1 or day > 31:
		return false
	return true


func get_yesterday_date(date_str: String) -> String:
	if not is_valid_date_string(date_str):
		return ""
	var parts := date_str.split("-")
	var year := int(parts[0])
	var month := int(parts[1])
	var day := int(parts[2])

	var epoch := Time.get_unix_time_from_datetime_dict(
		{"year": year, "month": month, "day": day, "hour": 12, "minute": 0, "second": 0}
	)
	var yesterday_epoch := epoch - 86400
	var yesterday_dict := Time.get_datetime_dict_from_unix_time(yesterday_epoch)
	return (
		"%04d-%02d-%02d" % [yesterday_dict["year"], yesterday_dict["month"], yesterday_dict["day"]]
	)


func is_next_day(date1: String, date2: String) -> bool:
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

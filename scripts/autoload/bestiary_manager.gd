extends Node
## BestiaryManager — Enemy type catalog, kill tracking, and lore unlocks.
## Extracted from GameState for testability and separation of concerns.

# Bestiary definitions — enemy type catalog with lore unlocks at kill milestones
const BESTIARY := {
	"skeleton":
	{
		"name": "Skeleton",
		"description": "Reanimated bones of fallen soldiers. Shambling but relentless.",
		"lore":
		{
			10: "Skeletons are the weakest of the undead, animated by residual battlefield malice.",
			50:
			"A skeleton's bones rattle with ancient war memories. Some still clutch rusted weapons.",
			100:
			"The oldest skeletons can reform after destruction — only fire or holy blades end them permanently.",
		},
		"stats": {"hp": 30, "damage": 8, "speed": 80, "type": "Undead"},
	},
	"skeleton_archer":
	{
		"name": "Skeleton Archer",
		"description": "Bone archers that keep their distance and rain arrows from afar.",
		"lore":
		{
			10:
			"Skeleton archers retain enough muscle memory to aim, but their arrows fly erratically.",
			50:
			"Some archer skeletons still carry quivers from their living days — arrows marked with regiment sigils.",
			100:
			"The finest skeleton archers were once imperial marksmen. Their undead accuracy is terrifying.",
		},
		"stats": {"hp": 25, "damage": 7, "speed": 70, "type": "Undead"},
	},
	"skeleton_captain":
	{
		"name": "Skeleton Captain",
		"description":
		"Armored commander of the undead. Shield blocks attacks. Charges when enraged.",
		"lore":
		{
			5:
			"Captains were military officers in life. Death hasn't diminished their tactical instinct.",
			25: "The captain's shield bears the crest of a kingdom that no longer exists.",
			50:
			"Skeleton captains can command lesser undead. Destroying one often causes nearby skeletons to falter.",
		},
		"stats": {"hp": 80, "damage": 15, "speed": 65, "type": "Undead • Boss"},
	},
	"ghost":
	{
		"name": "Ghost",
		"description":
		"Spectral entity that phases between tangible and intangible. Attacks pierce armor.",
		"lore":
		{
			10:
			"Ghosts are souls trapped between worlds. They flicker when they phase, briefly vulnerable.",
			50:
			"The ghost's wail isn't just eerie — it's a resonance attack that weakens the living's will to fight.",
			100:
			"Ancient ghosts can possess the living. The spectral blade 'Spirit Edge' is forged from their essence.",
		},
		"stats": {"hp": 35, "damage": 18, "speed": 60, "type": "Spectral"},
	},
	"bandit":
	{
		"name": "Bandit",
		"description": "Fast flanking fighter. Circles behind targets and strikes quickly.",
		"lore":
		{
			10: "Bandits are deserters and outlaws who prey on travelers along the Iron Road.",
			50:
			"The Crimson Fang recruits bandits with promises of gold and power. Most don't live to collect.",
			100:
			"Some bandits were once imperial soldiers — their military training makes them dangerous even without armor.",
		},
		"stats": {"hp": 50, "damage": 12, "speed": 90, "type": "Human"},
	},
	"assassin":
	{
		"name": "Assassin",
		"description":
		"Crimson Fang elite. Vanishes and reappears behind targets. Poisoned blades.",
		"lore":
		{
			5: "Assassins are Crimson Fang operatives trained in shadow techniques and venomcraft.",
			25:
			"An assassin's poison slows the heart and clouds the mind. Without an antidote, death follows within hours.",
			50:
			"The Crimson Fang's assassination order has toppled three kingdoms. Their symbol: a red fang in shadow.",
		},
		"stats": {"hp": 45, "damage": 20, "speed": 140, "type": "Human • Elite"},
	},
	"golem":
	{
		"name": "Golem",
		"description":
		"Massive stone construct. Armor absorbs damage. Devastating but slow attacks.",
		"lore":
		{
			5:
			"Golems are ancient constructs built to guard fortresses. Their stone skin deflects most blades.",
			25:
			"A golem's core is a geode of compressed earth magic. Destroying it is the only way to stop one.",
			50:
			"The Gate Warden golem has stood for a thousand years. Its halberd is the legendary Wardens_halberd.",
		},
		"stats": {"hp": 180, "damage": 30, "speed": 40, "type": "Construct"},
	},
	"necromancer":
	{
		"name": "Necromancer",
		"description":
		"Dark caster that raises skeleton minions. Stays at range — priority kill target.",
		"lore":
		{
			5:
			"Necromancers bind residual battlefield malice into new skeletons. Kill the caster and the summons fall.",
			25:
			"The most powerful necromancers can raise entire graveyards. The Siege of Ashmont saw 10,000 undead.",
			50:
			"Necromancy was once a sacred art — preserving heroes to fight again. The Crimson Fang corrupted it.",
		},
		"stats": {"hp": 60, "damage": 10, "speed": 50, "type": "Undead • Caster"},
	},
	"berserker":
	{
		"name": "Berserker",
		"description":
		"Dual-wielding brute that gets faster and stronger as HP drops. Enrages at 50% health.",
		"lore":
		{
			5:
			"Berserkers fight with reckless fury. As wounds accumulate, their rage amplifies rather than weakens them.",
			25:
			"Crimson Fang berserkers drink a battle elixir before combat — it removes pain but shortens their lives.",
			50:
			"The berserker's red fury is a blood magic technique. At full enrage, they can shatter stone with bare fists.",
		},
		"stats": {"hp": 90, "damage": 18, "speed": 75, "type": "Human • Brute"},
	},
	"shaman":
	{
		"name": "Shaman",
		"description":
		"Support caster that buffs nearby allies with damage and speed aura. Kill first.",
		"lore":
		{
			5:
			"Shamans channel elemental spirits to empower their allies. Their aura makes every nearby enemy deadlier.",
			25:
			"A shaman's totem is the source of their power. Breaking it dispels all active buffs instantly.",
			50:
			"The greatest shaman could empower an entire army. The Battle of Red Plains was won by three shamans.",
		},
		"stats": {"hp": 55, "damage": 8, "speed": 55, "type": "Human • Support"},
	},
	"wraith":
	{
		"name": "Wraith",
		"description":
		"Elite spectral entity. Teleports short distances, life drain AoE. Intangible during phase.",
		"lore":
		{
			5:
			"Wraiths are ascended ghosts — souls that consumed others to gain power. Their life drain is insatiable.",
			25:
			"A wraith's teleport is a short leap through the spirit realm. They're vulnerable for a moment after reappearing.",
			50:
			"The Wraith King beneath the capital commands thousands. His crown is forged from consumed souls.",
		},
		"stats": {"hp": 70, "damage": 15, "speed": 65, "type": "Spectral • Elite"},
	},
}

# Kill tracking: enemy_type → {"kills": int, "lore_unlocked": [int]}
var bestiary: Dictionary = {}

signal bestiary_updated(enemy_type: String, kills: int)


func record_kill(enemy_type: String) -> void:
	if not BESTIARY.has(enemy_type):
		return

	if not bestiary.has(enemy_type):
		bestiary[enemy_type] = {"kills": 0, "lore_unlocked": []}

	bestiary[enemy_type]["kills"] += 1

	var entry: Dictionary = BESTIARY[enemy_type]
	var lore_milestones: Array = entry.get("lore", {}).keys()
	lore_milestones.sort()

	for milestone in lore_milestones:
		if (
			bestiary[enemy_type]["kills"] >= milestone
			and milestone not in bestiary[enemy_type]["lore_unlocked"]
		):
			bestiary[enemy_type]["lore_unlocked"].append(milestone)

	bestiary_updated.emit(enemy_type, bestiary[enemy_type]["kills"])


func get_bestiary_entry(enemy_type: String) -> Dictionary:
	var entry: Dictionary = BESTIARY.get(enemy_type, {}).duplicate()
	var kills: int = bestiary.get(enemy_type, {}).get("kills", 0)
	var unlocked: Array = bestiary.get(enemy_type, {}).get("lore_unlocked", [])
	entry["kill_count"] = kills
	entry["lore_unlocked"] = unlocked
	entry["discovered"] = kills > 0
	return entry


func get_bestiary_progress() -> Dictionary:
	var total_types := BESTIARY.size()
	var discovered := 0
	var total_kills := 0
	var lore_unlocked_count := 0
	var total_lore := 0

	for enemy_type in BESTIARY:
		var kills: int = bestiary.get(enemy_type, {}).get("kills", 0)
		if kills > 0:
			discovered += 1
		total_kills += kills
		var lore: Dictionary = BESTIARY[enemy_type].get("lore", {})
		total_lore += lore.size()
		var unlocked: Array = bestiary.get(enemy_type, {}).get("lore_unlocked", [])
		lore_unlocked_count += unlocked.size()

	return {
		"total_types": total_types,
		"discovered": discovered,
		"percentage": (discovered * 100.0 / total_types) if total_types > 0 else 0.0,
		"total_kills": total_kills,
		"lore_unlocked": lore_unlocked_count,
		"total_lore": total_lore,
	}

extends Node
# AudioManager — v0.82 — SFX pool + BGM crossfade + ghost/achievement/streak sounds + volume controls
# Preloads all SFX; plays via AudioStreamPlayer pool
# BGM layers via dedicated AudioStreamPlayers with crossfade

const SFX_DIR := "res://assets/sfx/"
const BGM_DIR := "res://assets/bgm/"
const VOICE_DIR := "res://assets/sfx/voice/"
const POOL_SIZE := 8

var sfx_pool: Array[AudioStreamPlayer] = []
var pool_index := 0

var sfx_cache: Dictionary = {}
var bgm_cache: Dictionary = {}

var bgm_player_a := AudioStreamPlayer.new()
var bgm_player_b := AudioStreamPlayer.new()
var current_bgm_player: AudioStreamPlayer
var bgm_tween: Tween

var voice_player := AudioStreamPlayer.new()
var voice_cache: Dictionary = {}

@export var master_volume: float = 0.8
@export var sfx_volume: float = 0.7
@export var bgm_volume: float = 0.5


func _ready():
	_create_pool()
	_create_bgm_players()
	_create_voice_player()
	_load_all_sfx()
	_load_all_bgm()
	_load_all_voice()
	print(
		(
			"AudioManager ready — %d SFX, %d BGM, %d voice clips"
			% [sfx_cache.size(), bgm_cache.size(), voice_cache.size()]
		)
	)


func _create_pool():
	for i in range(POOL_SIZE):
		var player = AudioStreamPlayer.new()
		player.bus = "Master"
		player.volume_db = linear_to_db(sfx_volume * master_volume)
		add_child(player)
		player.finished.connect(_on_player_finished.bind(player))
		sfx_pool.append(player)


func _create_bgm_players():
	for p in [bgm_player_a, bgm_player_b]:
		p.bus = "Master"
		p.volume_db = linear_to_db(0.0)
		p.stream_paused = true
		add_child(p)
	current_bgm_player = bgm_player_a


func _load_all_sfx():
	var files := [
		"sword_swing",
		"sword_hit",
		"skeleton_death",
		"player_hurt",
		"shield_block",
		"captain_charge",
		"level_complete",
		"ui_click",
		"bow_fire",
		"arrow_hit",
		"arrow_impact",
		"dodge_roll",
		"ghost_start",
		"ghost_finish",
		"daily_challenge",
		"achievement_unlock",
		"streak_claim",
		"crit_hit"
	]
	for name in files:
		var path = SFX_DIR + name + ".wav"
		var stream = load(path)
		if stream:
			sfx_cache[name] = stream
		else:
			push_warning("Failed to load SFX: " + path)


func _load_all_bgm():
	var files := [
		"bgm_title",
		"bgm_battle",
		"bgm_boss",
		"bgm_act3",
		"bgm_act4",
		"bgm_act5",
		"bgm_act6",
		"bgm_victory",
		"bgm_daily",
		"bgm_gameover",
		"bgm_ambient_ruins",
		"bgm_ambient_foreboding",
		"bgm_exploration",
		"bgm_siege",
		"bgm_void",
		"bgm_final_confrontation",
		"bgm_triumphant",
	]
	for name in files:
		var loaded := false
		for ext in [".ogg", ".wav"]:
			var path = BGM_DIR + name + ext
			var stream = load(path)
			if stream:
				if stream is AudioStreamOggVorbis:
					stream.loop = true
				elif stream is AudioStreamWAV:
					stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
				bgm_cache[name] = stream
				loaded = true
				break
		if not loaded:
			push_warning("Failed to load BGM: " + name)


func _create_voice_player():
	voice_player.bus = "Master"
	voice_player.volume_db = linear_to_db(0.9)
	add_child(voice_player)


func _load_all_voice():
	var dir := DirAccess.open(VOICE_DIR)
	if dir == null:
		return
	dir.list_dir_begin()
	var file := dir.get_next()
	while file != "":
		if not dir.current_is_dir() and (file.ends_with(".ogg") or file.ends_with(".wav")):
			var name := file.get_basename()
			var stream = load(VOICE_DIR + file)
			if stream:
				voice_cache[name] = stream
			else:
				push_warning("Failed to load voice clip: " + file)
		file = dir.get_next()
	dir.list_dir_end()


func play_voice(name: String):
	if not voice_cache.has(name):
		push_warning("Voice clip not found: " + name)
		return
	voice_player.stop()
	voice_player.stream = voice_cache[name]
	voice_player.play()


# --- SFX ---


func play_sfx(name: String):
	if not sfx_cache.has(name):
		push_warning("SFX not found: " + name)
		return

	# Find next available player
	var attempts := 0
	var start := pool_index
	while attempts < POOL_SIZE:
		var p = sfx_pool[pool_index]
		pool_index = (pool_index + 1) % POOL_SIZE
		if not p.playing:
			p.stream = sfx_cache[name]
			p.play()
			return
		attempts += 1

	# Fallback: stop oldest and reuse
	var oldest = sfx_pool[start]
	oldest.stop()
	oldest.stream = sfx_cache[name]
	oldest.play()


func play_random_pitch(name: String, min_pitch: float = 0.9, max_pitch: float = 1.1):
	if not sfx_cache.has(name):
		return

	for i in range(POOL_SIZE):
		var idx = (pool_index + i) % POOL_SIZE
		var p = sfx_pool[idx]
		if not p.playing:
			pool_index = (idx + 1) % POOL_SIZE
			p.stream = sfx_cache[name]
			p.pitch_scale = randf_range(min_pitch, max_pitch)
			p.play()
			return


func stop_all():
	for p in sfx_pool:
		p.stop()


# --- BGM ---


func play_bgm(name: String, fade_duration: float = 1.0, loop: bool = true):
	if not bgm_cache.has(name):
		push_warning("BGM not found: " + name)
		return

	var target_db = linear_to_db(bgm_volume * master_volume)
	var next_player := bgm_player_b if current_bgm_player == bgm_player_a else bgm_player_a

	# Stop any existing crossfade
	if bgm_tween:
		bgm_tween.kill()

	bgm_tween = create_tween().set_trans(Tween.TRANS_LINEAR).set_ease(Tween.EASE_IN_OUT)

	# Fade out current
	if current_bgm_player.playing:
		bgm_tween.tween_property(
			current_bgm_player, "volume_db", linear_to_db(0.001), fade_duration
		)
		bgm_tween.tween_callback(current_bgm_player.stop)

	# Prepare next
	next_player.stream = bgm_cache[name]
	if next_player.stream is AudioStreamWAV:
		next_player.stream.loop_mode = (
			AudioStreamWAV.LOOP_FORWARD if loop else AudioStreamWAV.LOOP_DISABLED
		)
	elif next_player.stream is AudioStreamOggVorbis:
		next_player.stream.loop = loop
	next_player.volume_db = linear_to_db(0.001)
	next_player.stream_paused = false
	next_player.play()

	# Fade in next
	bgm_tween.tween_property(next_player, "volume_db", target_db, fade_duration)

	current_bgm_player = next_player


func stop_bgm(fade_duration: float = 1.0):
	if bgm_tween:
		bgm_tween.kill()

	bgm_tween = create_tween().set_trans(Tween.TRANS_LINEAR).set_ease(Tween.EASE_IN_OUT)
	bgm_tween.tween_property(current_bgm_player, "volume_db", linear_to_db(0.001), fade_duration)
	bgm_tween.tween_callback(current_bgm_player.stop)


func _on_player_finished(player: AudioStreamPlayer):
	player.pitch_scale = 1.0  # Reset pitch


func set_volume(vol: float):
	master_volume = clamp(vol, 0.0, 1.0)
	var sfx_db = linear_to_db(sfx_volume * master_volume)
	for p in sfx_pool:
		p.volume_db = sfx_db
	var bgm_db = linear_to_db(bgm_volume * master_volume)
	for p in [bgm_player_a, bgm_player_b]:
		if p.playing:
			p.volume_db = bgm_db


func set_master_volume(vol: float):
	master_volume = clamp(vol, 0.0, 1.0)
	_apply_volumes()


func set_sfx_volume(vol: float):
	sfx_volume = clamp(vol, 0.0, 1.0)
	_apply_volumes()


func set_bgm_volume(vol: float):
	bgm_volume = clamp(vol, 0.0, 1.0)
	_apply_volumes()


func _apply_volumes():
	var sfx_db = linear_to_db(sfx_volume * master_volume)
	for p in sfx_pool:
		p.volume_db = sfx_db
	var bgm_db = linear_to_db(bgm_volume * master_volume)
	for p in [bgm_player_a, bgm_player_b]:
		if p.playing:
			p.volume_db = bgm_db

extends GutTest

var Player = load("res://scripts/player.gd")


func test_player_initial_health():
	var player = autofree(Player.new())
	player.max_health = 100
	player.is_dead = false
	player.is_dodging = false
	add_child(player)
	await wait_frames(2)
	player.health = 100
	assert_eq(player.health, 100, "player should start with full health")


func test_player_velocity_zero_by_default():
	var player = autofree(Player.new())
	player.max_health = 100
	player.is_dead = false
	player.is_dodging = false
	add_child(player)
	await wait_frames(2)
	assert_eq(player.velocity, Vector2.ZERO, "player velocity should be zero when no input")


func test_player_dodge_cooldown_constant():
	assert_eq(Player.DODGE_COOLDOWN, 1.2, "dodge cooldown should be 1.2 seconds")
	assert_eq(Player.DODGE_DURATION, 0.25, "dodge duration should be 0.25 seconds")
	assert_eq(Player.DODGE_SPEED_MULT, 3.0, "dodge speed multiplier should be 3.0")


func test_player_stunned_cannot_move():
	var player = autofree(Player.new())
	player.max_health = 100
	player.health = 100
	player.is_dead = false
	player.is_dodging = false
	add_child(player)
	await wait_frames(2)
	player.is_attacking = true
	player.attack_timer = 0.5
	var vel_before = player.velocity
	player._physics_process(0.016)
	assert_eq(
		player.velocity.length(), vel_before.length(), "velocity should not change while attacking"
	)


func test_player_speed_constant():
	assert_eq(Player.DODGE_SPEED_MULT, 3.0, "dodge speed multiplier constant should be 3.0")


func test_player_dodge_enabled_default():
	var player = autofree(Player.new())
	player.max_health = 100
	player.is_dead = false
	add_child(player)
	await wait_frames(2)
	assert_true(player.dodge_enabled, "dodge should be enabled by default")


func test_player_set_dodge_enabled():
	var player = autofree(Player.new())
	player.max_health = 100
	player.is_dead = false
	add_child(player)
	await wait_frames(2)
	player.set_dodge_enabled(false)
	assert_false(player.dodge_enabled, "dodge should be disabled after set_dodge_enabled(false)")
	player.set_dodge_enabled(true)
	assert_true(player.dodge_enabled, "dodge should be re-enabled after set_dodge_enabled(true)")


func test_player_take_damage_reduces_health():
	var player = autofree(Player.new())
	player.max_health = 100
	player.health = 100
	player.is_dead = false
	player.is_dodging = false
	add_child(player)
	await wait_frames(2)
	player.take_damage(25)
	await wait_frames(15)
	assert_eq(player.health, 75, "health should be 75 after 25 damage from 100")


func test_player_heal_does_not_exceed_max():
	var player = autofree(Player.new())
	player.max_health = 100
	player.health = 90
	player.is_dead = false
	player.is_dodging = false
	add_child(player)
	await wait_frames(2)
	player.heal(30)
	await wait_frames(5)
	assert_eq(player.health, 100, "heal should cap at max_health")


func test_player_heal_does_nothing_when_dead():
	var player = autofree(Player.new())
	player.max_health = 100
	player.health = 100
	player.is_dead = false
	player.is_dodging = false
	add_child(player)
	await wait_frames(2)
	player.is_dead = true
	player.health = 50
	player.heal(30)
	assert_eq(player.health, 50, "heal should not change health when dead")


func test_player_dodge_ignores_damage():
	var player = autofree(Player.new())
	player.max_health = 100
	player.health = 100
	player.is_dead = false
	player.is_dodging = true
	add_child(player)
	await wait_frames(2)
	player.take_damage(50)
	await wait_frames(15)
	assert_eq(player.health, 100, "player should take no damage while dodging")


func test_player_overkill_damage_marks_dead():
	var player = autofree(Player.new())
	player.max_health = 100
	player.health = 100
	player.is_dead = false
	player.is_dodging = false
	add_child(player)
	await wait_frames(2)
	player.take_damage(999)
	await wait_frames(15)
	assert_true(player.is_dead, "player should be dead after overkill damage")
	assert_true(player.health <= 0, "health should be zero or below after overkill")


func test_player_combo_constants():
	assert_eq(Player.COMBO_MAX, 3, "max combo hits should be 3")
	assert_eq(Player.COMBO_WINDOW, 0.5, "combo window should be 0.5 seconds")
	assert_eq(Player.COMBO_DAMAGE_MULT.size(), 3, "should have 3 combo damage multipliers")
	assert_eq(Player.COMBO_DAMAGE_MULT[0], 1.0, "first combo hit multiplier should be 1.0")


func test_player_crit_constants():
	assert_eq(Player.CRIT_BASE_CHANCE, 0.10, "base crit chance should be 10%")
	assert_eq(Player.CRIT_DAMAGE_MULT, 2.0, "crit damage multiplier should be 2.0")
	assert_eq(Player.CRIT_COMBO_BONUS.size(), 3, "should have 3 combo crit bonuses")


func test_player_weapon_constants():
	var gs = autofree(load("res://scripts/autoload/game_state.gd").new())
	assert_true(GameState.WEAPON_STATS is Dictionary, "WEAPON_STATS should be a dictionary")
	assert_true(GameState.WEAPON_STATS.has("broken_sword"), "should have broken_sword weapon")
	assert_true(GameState.WEAPON_STATS.has("wardens_halberd"), "should have wardens_halberd weapon")


func test_player_speed_default():
	var player = autofree(Player.new())
	player.max_health = 100
	player.is_dead = false
	add_child(player)
	await wait_frames(2)
	assert_eq(player.speed, 200.0, "player default speed should be 200")

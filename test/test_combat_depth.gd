extends GutTest

var Player = load("res://scripts/player.gd")
var Skeleton = load("res://scripts/skeleton.gd")
var Golem = load("res://scripts/golem.gd")


func test_overkill_damage_clamps_health_to_zero():
	var player = autofree(Player.new())
	player.max_health = 50
	player.is_dead = false
	player.is_dodging = false
	add_child(player)
	await wait_frames(2)
	player.health = 50
	player.take_damage(999)
	await wait_frames(15)
	assert_true(player.health <= 0, "overkill damage should bring HP to 0 or below")
	assert_true(player.is_dead, "player should be dead after overkill damage")


func test_zero_damage_leaves_health_unchanged():
	var player = autofree(Player.new())
	player.is_dead = false
	player.is_dodging = false
	add_child(player)
	await wait_frames(2)
	player.health = 80
	player.max_health = 100
	player.take_damage(0)
	await wait_frames(15)
	assert_eq(player.health, 80, "zero damage should not change HP")


func test_multiple_enemies_each_take_damage():
	var skel1 = autofree(Skeleton.new())
	skel1.max_health = 30
	skel1.health = 30
	skel1.is_dead = false
	add_child(skel1)
	await wait_frames(2)
	skel1.take_damage(10)
	await wait_frames(10)
	assert_eq(skel1.health, 20, "first skeleton should take 10 damage")

	var skel2 = autofree(Skeleton.new())
	skel2.max_health = 30
	skel2.health = 30
	skel2.is_dead = false
	add_child(skel2)
	await wait_frames(2)
	skel2.take_damage(5)
	await wait_frames(10)
	assert_eq(skel2.health, 25, "second skeleton should take 5 damage")


func test_player_heal_restores_health():
	var player = autofree(Player.new())
	player.is_dead = false
	player.is_dodging = false
	add_child(player)
	await wait_frames(2)
	player.max_health = 100
	player.health = 50
	player.heal(30)
	await wait_frames(5)
	assert_eq(player.health, 80, "heal should restore 30 HP from 50 to 80")


func test_enemy_armor_reduces_damage():
	var golem = autofree(Golem.new())
	golem.max_health = 180
	golem.health = 180
	golem.is_dead = false
	golem.armor = 10
	add_child(golem)
	await wait_frames(2)
	golem.take_damage(25)
	await wait_frames(10)
	var expected_damage = max(1, 25 - 10)
	assert_eq(
		golem.health, 180 - expected_damage, "golem armor should reduce incoming damage by 10"
	)

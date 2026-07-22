extends GutTest

var Player = load("res://scripts/player.gd")


func test_take_damage_reduces_health():
	var player = autofree(Player.new())
	player.max_health = 100
	player.health = 100
	player.is_dead = false
	player.is_dodging = false
	add_child(player)
	await wait_frames(2)
	player.take_damage(10)
	await wait_frames(15)
	assert_eq(player.health, 90, "health should drop by damage amount")


func test_take_damage_lethal_health_below_zero():
	var player = autofree(Player.new())
	player.max_health = 100
	player.health = 100
	player.is_dead = false
	player.is_dodging = false
	add_child(player)
	await wait_frames(2)
	player.take_damage(999)
	await wait_frames(15)
	assert_lt(player.health, 1, "health should be 0 or below after overkill damage")


func test_take_damage_ignored_when_dodging():
	var player = autofree(Player.new())
	player.max_health = 100
	player.health = 100
	player.is_dead = false
	player.is_dodging = true
	add_child(player)
	await wait_frames(2)
	player.take_damage(50)
	await wait_frames(15)
	assert_eq(player.health, 100, "health should not change when dodging")

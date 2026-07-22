extends GutTest

var Skeleton = load("res://scripts/skeleton.gd")
var Golem = load("res://scripts/golem.gd")


func test_skeleton_take_damage_reduces_health():
	var skeleton = autofree(Skeleton.new())
	skeleton.max_health = 30
	skeleton.health = 30
	skeleton.is_dead = false
	add_child(skeleton)
	await wait_frames(2)
	skeleton.take_damage(10)
	await wait_frames(10)
	assert_eq(skeleton.health, 20, "skeleton health should drop by damage amount")


func test_skeleton_take_damage_lethal():
	var skeleton = autofree(Skeleton.new())
	skeleton.max_health = 30
	skeleton.health = 30
	skeleton.is_dead = false
	add_child(skeleton)
	await wait_frames(2)
	skeleton.take_damage(30)
	await wait_frames(10)
	assert_true(skeleton.is_dead, "skeleton should be dead after lethal damage")


func test_golem_take_damage_armor_reduces():
	var golem = autofree(Golem.new())
	golem.max_health = 180
	golem.health = 180
	golem.is_dead = false
	golem.armor = 5
	add_child(golem)
	await wait_frames(2)
	golem.take_damage(15)
	await wait_frames(10)
	var expected_damage = max(1, 15 - 5)
	assert_eq(golem.health, 180 - expected_damage, "golem should take reduced damage due to armor")


func test_golem_take_damage_armor_minimum_1():
	var golem = autofree(Golem.new())
	golem.max_health = 180
	golem.health = 180
	golem.is_dead = false
	golem.armor = 50
	add_child(golem)
	await wait_frames(2)
	golem.take_damage(5)
	await wait_frames(10)
	assert_eq(golem.health, 179, "golem should take minimum 1 damage when armor exceeds attack")

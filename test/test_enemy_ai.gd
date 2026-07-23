extends GutTest

var Skeleton = load("res://scripts/skeleton.gd")
var SkeletonCaptain = load("res://scripts/skeleton_captain.gd")
var Golem = load("res://scripts/golem.gd")


func test_skeleton_default_stats():
	var skeleton = autofree(Skeleton.new())
	skeleton.max_health = 30
	skeleton.health = 30
	skeleton.is_dead = false
	add_child(skeleton)
	await wait_frames(2)
	assert_eq(skeleton.speed, 80.0, "skeleton speed should be 80")
	assert_eq(skeleton.detection_range, 250.0, "skeleton detection range should be 250")
	assert_eq(skeleton.attack_range, 32.0, "skeleton attack range should be 32")
	assert_eq(skeleton.attack_damage, 8, "skeleton attack damage should be 8")


func test_skeleton_detection_range():
	var skeleton = autofree(Skeleton.new())
	skeleton.max_health = 30
	skeleton.health = 30
	skeleton.is_dead = false
	add_child(skeleton)
	await wait_frames(2)
	assert_true(skeleton.detection_range > 0, "detection range should be positive")
	assert_true(
		skeleton.detection_range >= skeleton.attack_range,
		"detection range should be >= attack range"
	)


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
	assert_true(skeleton.is_dead, "skeleton should die from lethal damage")


func test_skeleton_no_damage_when_dead():
	var skeleton = autofree(Skeleton.new())
	skeleton.max_health = 30
	skeleton.health = 30
	skeleton.is_dead = false
	add_child(skeleton)
	await wait_frames(2)
	skeleton.is_dead = true
	skeleton.health = 30
	skeleton.take_damage(10)
	await wait_frames(5)
	assert_eq(skeleton.health, 30, "dead skeleton should not take more damage")


func test_skeleton_knockback_applies():
	var skeleton = autofree(Skeleton.new())
	skeleton.max_health = 30
	skeleton.health = 30
	skeleton.is_dead = false
	add_child(skeleton)
	await wait_frames(2)
	skeleton.apply_knockback(Vector2.RIGHT, 200.0)
	await wait_frames(5)
	assert_true(
		skeleton.knockback_velocity.length() > 0,
		"knockback velocity should be non-zero after apply_knockback"
	)


func test_captain_default_stats():
	var captain = autofree(SkeletonCaptain.new())
	captain.max_health = 80
	captain.health = 80
	captain.is_dead = false
	add_child(captain)
	await wait_frames(2)
	assert_eq(captain.speed, 65.0, "captain speed should be 65")
	assert_eq(captain.detection_range, 280.0, "captain detection range should be 280")
	assert_eq(captain.attack_damage, 15, "captain attack damage should be 15")


func test_captain_shield_mechanic():
	var captain = autofree(SkeletonCaptain.new())
	captain.max_health = 80
	captain.health = 80
	captain.is_dead = false
	add_child(captain)
	await wait_frames(2)
	assert_eq(captain.shield_max, 3, "captain should have shield_max of 3")
	assert_true(captain.shield_max > 0, "captain should have positive shield_max")


func test_captain_shield_blocks_damage():
	var captain = autofree(SkeletonCaptain.new())
	captain.max_health = 80
	captain.health = 80
	captain.is_dead = false
	add_child(captain)
	await wait_frames(2)
	captain.shield_charges = 2
	var health_before = captain.health
	captain.take_damage(10)
	await wait_frames(10)
	assert_eq(captain.health, health_before, "captain should take no damage when shield is up")
	assert_eq(captain.shield_charges, 1, "captain should lose one shield charge on block")


func test_captain_shield_regen_timer():
	var captain = autofree(SkeletonCaptain.new())
	captain.max_health = 80
	captain.health = 80
	captain.is_dead = false
	add_child(captain)
	await wait_frames(2)
	assert_eq(captain.SHIELD_REGEN_DELAY, 2.0, "shield regen delay should be 2.0 seconds")


func test_golem_armor_reduces_damage():
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
	assert_eq(golem.health, 180 - expected_damage, "golem should take reduced damage due to armor")


func test_golem_armor_minimum_one_damage():
	var golem = autofree(Golem.new())
	golem.max_health = 180
	golem.health = 180
	golem.is_dead = false
	golem.armor = 50
	add_child(golem)
	await wait_frames(2)
	golem.take_damage(5)
	await wait_frames(10)
	assert_eq(golem.health, 179, "golem should take minimum 1 damage even with high armor")


func test_enemy_death_flag():
	var skeleton = autofree(Skeleton.new())
	skeleton.max_health = 30
	skeleton.health = 30
	skeleton.is_dead = false
	add_child(skeleton)
	await wait_frames(2)
	assert_false(skeleton.is_dead, "skeleton should not be dead initially")
	skeleton.take_damage(30)
	await wait_frames(10)
	assert_true(skeleton.is_dead, "skeleton should be dead after lethal damage")


func test_captain_takes_damage_after_shield_empty():
	var captain = autofree(SkeletonCaptain.new())
	captain.max_health = 80
	captain.health = 80
	captain.is_dead = false
	add_child(captain)
	await wait_frames(2)
	captain.shield_charges = 0
	captain.take_damage(20)
	await wait_frames(10)
	assert_eq(captain.health, 60, "captain should take damage when shield is empty")


func test_captain_knockback_reduced():
	var captain = autofree(SkeletonCaptain.new())
	captain.max_health = 80
	captain.health = 80
	captain.is_dead = false
	add_child(captain)
	await wait_frames(2)
	captain.apply_knockback(Vector2.RIGHT, 200.0)
	await wait_frames(5)
	assert_true(captain.knockback_velocity.length() > 0, "captain should receive knockback")


func test_skeleton_attack_cooldown():
	var skeleton = autofree(Skeleton.new())
	skeleton.max_health = 30
	skeleton.health = 30
	skeleton.is_dead = false
	add_child(skeleton)
	await wait_frames(2)
	assert_eq(skeleton.attack_cooldown, 1.2, "skeleton attack cooldown should be 1.2s")
	assert_eq(skeleton.attack_duration, 0.4, "skeleton attack duration should be 0.4s")

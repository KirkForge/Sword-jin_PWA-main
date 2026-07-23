extends GutTest


func test_audio_manager_sfx_cache_loaded():
	assert_true(AudioManager.sfx_cache is Dictionary, "sfx_cache should be a dictionary")
	assert_true(AudioManager.sfx_cache.size() > 0, "sfx_cache should not be empty after _ready")


func test_audio_manager_bgm_cache_loaded():
	assert_true(AudioManager.bgm_cache is Dictionary, "bgm_cache should be a dictionary")
	assert_true(AudioManager.bgm_cache.size() > 0, "bgm_cache should not be empty after _ready")


func test_audio_manager_pool_size():
	assert_eq(AudioManager.POOL_SIZE, 8, "SFX pool size should be 8")
	assert_eq(AudioManager.sfx_pool.size(), AudioManager.POOL_SIZE, "pool should match POOL_SIZE")


func test_audio_manager_master_volume_range():
	AudioManager.set_master_volume(0.5)
	assert_eq(AudioManager.master_volume, 0.5, "master volume should be 0.5")
	AudioManager.set_master_volume(-0.5)
	assert_eq(AudioManager.master_volume, 0.0, "master volume should clamp to 0.0 on negative")
	AudioManager.set_master_volume(1.5)
	assert_eq(AudioManager.master_volume, 1.0, "master volume should clamp to 1.0 on overflow")


func test_audio_manager_sfx_volume_range():
	AudioManager.set_sfx_volume(0.3)
	assert_eq(AudioManager.sfx_volume, 0.3, "sfx volume should be 0.3")
	AudioManager.set_sfx_volume(-1.0)
	assert_eq(AudioManager.sfx_volume, 0.0, "sfx volume should clamp to 0.0 on negative")
	AudioManager.set_sfx_volume(2.0)
	assert_eq(AudioManager.sfx_volume, 1.0, "sfx volume should clamp to 1.0 on overflow")


func test_audio_manager_bgm_volume_range():
	AudioManager.set_bgm_volume(0.4)
	assert_eq(AudioManager.bgm_volume, 0.4, "bgm volume should be 0.4")
	AudioManager.set_bgm_volume(-0.5)
	assert_eq(AudioManager.bgm_volume, 0.0, "bgm volume should clamp to 0.0 on negative")
	AudioManager.set_bgm_volume(3.0)
	assert_eq(AudioManager.bgm_volume, 1.0, "bgm volume should clamp to 1.0 on overflow")


func test_audio_manager_set_volume_convenience():
	AudioManager.set_volume(0.0)
	assert_eq(AudioManager.master_volume, 0.0, "set_volume(0) should mute master")
	AudioManager.set_volume(0.8)
	assert_eq(AudioManager.master_volume, 0.8, "set_volume(0.8) should set master to 0.8")


func test_audio_manager_play_sfx_unknown_no_crash():
	AudioManager.play_sfx("nonexistent_sfx_name")
	await wait_frames(5)
	assert_true(true, "playing nonexistent SFX should not crash")


func test_audio_manager_play_bgm_unknown_no_crash():
	AudioManager.play_bgm("nonexistent_bgm_name")
	await wait_frames(5)
	assert_true(true, "playing nonexistent BGM should not crash")


func test_audio_manager_stop_all_sfx():
	AudioManager.stop_all()
	for p in AudioManager.sfx_pool:
		assert_false(p.playing, "all SFX players should be stopped after stop_all")

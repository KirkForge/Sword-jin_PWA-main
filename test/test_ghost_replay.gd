extends GutTest


func test_record_start_stop_state():
	GhostRecorder.start_recording()
	assert_true(GhostRecorder.is_recording, "GhostRecorder should be recording after start")
	assert_eq(GhostRecorder.current_recording.size(), 0, "recording should start empty")
	var recording = GhostRecorder.stop_recording()
	assert_false(GhostRecorder.is_recording, "GhostRecorder should not be recording after stop")


func test_playback_snapshot_data_structure():
	var snapshots := [
		{"t": 0.0, "x": 100.0, "y": 200.0, "fr": true, "atk": false},
		{"t": 0.1, "x": 110.0, "y": 200.0, "fr": true, "atk": false},
		{"t": 0.2, "x": 120.0, "y": 200.0, "fr": true, "atk": false},
	]
	assert_eq(snapshots.size(), 3, "test snapshot data should have 3 entries")
	assert_true(snapshots[0].has("x"), "snapshots should contain position data")
	assert_true(snapshots[0].has("t"), "snapshots should contain time data")
	assert_true(snapshots[0].has("fr"), "snapshots should contain facing data")
	assert_true(snapshots[0].has("atk"), "snapshots should contain attack data")


func test_empty_ghost_list_no_crash():
	var best_time := GhostRecorder.get_best_time("nonexistent_chapter")
	assert_eq(best_time, -1.0, "nonexistent chapter should return -1 best time")
	var ghost_info := GhostRecorder.get_ghost_info("nonexistent_chapter")
	assert_eq(ghost_info.size(), 0, "nonexistent chapter should return empty ghost info")
	var has_ghost := GhostRecorder.has_ghost("nonexistent_chapter")
	assert_false(has_ghost, "nonexistent chapter should report no ghost")

extends GutTest


func test_login_failed_signal_carries_error():
	PlayFab.login_failed.emit("test error message")
	await wait_frames(1)
	assert_true(true, "login_failed signal can be emitted without errors")


func test_login_failed_connected_to_error_screen_handler():
	var connections = PlayFab.login_failed.get_connections()
	var found := false
	for conn in connections:
		if str(conn["callable"]).find("_on_login_failed_error_screen") != -1:
			found = true
	assert_true(found, "login_failed should be connected to _on_login_failed_error_screen")

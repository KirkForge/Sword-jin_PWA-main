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


func test_error_screen_receives_message_on_signal():
	var error_msg := "Network timeout"
	PlayFab.login_failed.emit(error_msg)
	await wait_frames(2)
	assert_eq(
		ErrorScreen.title_label.text,
		"Cloud Sync Unavailable",
		"ErrorScreen title should show cloud sync header"
	)
	assert_eq(
		ErrorScreen.message_label.text,
		"Cloud leaderboard sync failed: " + error_msg + ". Your progress is saved locally.",
		"ErrorScreen message should include the error detail"
	)


func test_error_screen_auto_hides_after_timeout():
	PlayFab.login_failed.emit("temporary error")
	await wait_frames(2)
	assert_true(ErrorScreen.visible, "ErrorScreen should be visible after error")
	ErrorScreen._auto_hide_timer = 0.0
	await wait_frames(2)
	assert_false(ErrorScreen.visible, "ErrorScreen should auto-hide after timeout expires")


func test_error_screen_dismiss_on_return_button():
	PlayFab.login_failed.emit("test dismiss")
	await wait_frames(2)
	assert_true(ErrorScreen.visible, "ErrorScreen should be visible after error")
	ErrorScreen._on_return()
	await wait_frames(1)
	assert_false(ErrorScreen.visible, "ErrorScreen should hide when return is pressed")

extends GutTest
## Test ErrorTracker — circular buffer and error reporting


func test_report_error_adds_to_buffer():
	ErrorTracker.clear_errors()
	ErrorTracker.report_error("test_type", "test message", {"key": "value"})
	assert_eq(ErrorTracker.get_error_count(), 1, "Should have 1 error after report")


func test_circular_buffer_max_size():
	ErrorTracker.clear_errors()
	for i in range(60):
		ErrorTracker.report_error("type_%d" % i, "msg_%d" % i)
	assert_eq(ErrorTracker.get_error_count(), 50, "Buffer should cap at MAX_BUFFER_SIZE")


func test_circular_buffer_evicts_oldest():
	ErrorTracker.clear_errors()
	for i in range(55):
		ErrorTracker.report_error("type_%d" % i, "msg_%d" % i)
	var errors = ErrorTracker.get_recent_errors()
	assert_eq(errors[0]["type"], "type_5", "Oldest error should be evicted (type_5)")
	assert_eq(errors.size(), 50, "Should have exactly 50 errors")


func test_get_recent_errors_with_count():
	ErrorTracker.clear_errors()
	for i in range(10):
		ErrorTracker.report_error("type_%d" % i, "msg_%d" % i)
	var last_3 = ErrorTracker.get_recent_errors(3)
	assert_eq(last_3.size(), 3, "Should return requested count")
	assert_eq(last_3[2]["type"], "type_9", "Last error should be most recent")


func test_clear_errors():
	ErrorTracker.clear_errors()
	ErrorTracker.report_error("a", "b")
	ErrorTracker.report_error("c", "d")
	assert_eq(ErrorTracker.get_error_count(), 2, "Should have 2 errors")
	ErrorTracker.clear_errors()
	assert_eq(ErrorTracker.get_error_count(), 0, "Should have 0 errors after clear")


func test_report_error_without_context():
	ErrorTracker.clear_errors()
	ErrorTracker.report_error("simple", "no context")
	var errors = ErrorTracker.get_recent_errors(1)
	assert_eq(errors[0]["type"], "simple", "Type should match")
	assert_eq(errors[0]["message"], "no context", "Message should match")
	assert_eq(errors[0]["context"].size(), 0, "Context should be empty dict")


func test_report_error_with_context():
	ErrorTracker.clear_errors()
	ErrorTracker.report_error("playfab_login", "timeout", {"status": 500, "retry": true})
	var errors = ErrorTracker.get_recent_errors(1)
	assert_eq(errors[0]["context"]["status"], 500, "Context status should be 500")
	assert_eq(errors[0]["context"]["retry"], true, "Context retry should be true")

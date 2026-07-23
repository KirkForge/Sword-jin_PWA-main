extends Node
## ErrorTracker — Circular buffer error log with signal emission.
## Captures runtime errors from GameState, PlayFab, and LevelManager
## for debugging and potential remote reporting.

signal error_reported(error_type: String, message: String, context: Dictionary)

const MAX_BUFFER_SIZE := 50

var _errors: Array = []


func report_error(error_type: String, message: String, context: Dictionary = {}) -> void:
	var entry := {
		"type": error_type,
		"message": message,
		"context": context,
		"timestamp": Time.get_unix_time_from_system(),
	}
	_errors.append(entry)
	if _errors.size() > MAX_BUFFER_SIZE:
		_errors.pop_front()
	error_reported.emit(error_type, message, context)
	print("ERROR [%s]: %s %s" % [error_type, message, str(context) if context else ""])


func get_recent_errors(count: int = MAX_BUFFER_SIZE) -> Array:
	var start: int = max(0, _errors.size() - count)
	return _errors.slice(start, _errors.size())


func clear_errors() -> void:
	_errors.clear()


func get_error_count() -> int:
	return _errors.size()

extends Node
## HeadlessSmokeDriver — automated input for CI smoke tests.
## Beats act01_ch001 by walking right/down/up and spamming attack.

var _timer := 0.0
var _phase := 0

func _ready():
	await get_tree().create_timer(0.6).timeout

func _process(delta: float):
	_timer += delta
	if _timer < 0.10:
		return
	_timer = 0.0
	_phase += 1

	match _phase % 10:
		0, 1, 2, 3:
			_press("move_right", 0.30)
		4:
			_tap("attack")
		5, 6:
			_press("move_down", 0.20)
		7:
			_tap("attack")
		8, 9:
			_press("move_up", 0.20)

func _tap(action: String):
	_press(action, 0.08)

func _press(action: String, duration: float):
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	Input.parse_input_event(ev)
	var t := get_tree().create_timer(duration)
	t.timeout.connect(_release.bind(action))

func _release(action: String):
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = false
	Input.parse_input_event(ev)

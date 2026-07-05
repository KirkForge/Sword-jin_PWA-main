extends CanvasLayer
# ErrorScreen — Global singleton for user-facing error display
# Call from anywhere: ErrorScreen.show_error("Title", "Message")

signal return_pressed

@onready var overlay = $ColorRect
@onready var title_label = $VBoxContainer/TitleLabel
@onready var message_label = $VBoxContainer/MessageLabel
@onready var return_btn = $VBoxContainer/ReturnButton

var _auto_hide_timer: float = 0.0
const AUTO_HIDE_SECONDS := 15.0

func _ready():
	visible = false
	process_mode = PROCESS_MODE_ALWAYS
	return_btn.pressed.connect(_on_return)

func show_error(title: String, message: String, show_return: bool = true):
	title_label.text = title
	message_label.text = message
	return_btn.visible = show_return
	visible = true
	overlay.modulate = Color(0, 0, 0, 0)
	var tween := create_tween()
	tween.tween_property(overlay, "modulate", Color(0, 0, 0, 0.75), 0.3)
	_auto_hide_timer = AUTO_HIDE_SECONDS

func _process(delta):
	if not visible:
		return
	_auto_hide_timer -= delta
	if _auto_hide_timer <= 0:
		visible = false

func _on_return():
	visible = false
	return_pressed.emit()
	get_tree().paused = false
	get_tree().change_scene_to_file("res://scenes/title_screen.tscn")

extends GutTest

var ArenaBuilder = load("res://scripts/arena_builder.gd")


func test_arena_dimensions_within_bounds():
	var arena = autofree(ArenaBuilder.new())
	assert_eq(ArenaBuilder.ARENA_W, 40, "ARENA_W should be 40 tiles")
	assert_eq(ArenaBuilder.ARENA_H, 22, "ARENA_H should be 22 tiles")
	assert_eq(ArenaBuilder.TILE_SIZE, 16, "TILE_SIZE should be 16px")


func test_arena_pixel_dimensions():
	var pixel_w = ArenaBuilder.ARENA_W * ArenaBuilder.TILE_SIZE
	var pixel_h = ArenaBuilder.ARENA_H * ArenaBuilder.TILE_SIZE
	assert_eq(pixel_w, 640, "arena pixel width should be 640")
	assert_eq(pixel_h, 352, "arena pixel height should be 352")


func test_arena_theme_mapping_exists():
	var themes = ArenaBuilder.CHAPTER_THEMES
	assert_true(themes is Dictionary, "CHAPTER_THEMES should be a dictionary")
	assert_true(themes.size() >= 30, "should have themes for all 30 chapters")


func test_arena_theme_valid_values():
	var themes = ArenaBuilder.CHAPTER_THEMES
	var valid_themes := ["field", "forest", "fortress", "dark_fortress"]
	for chapter_id in themes:
		var theme: String = themes[chapter_id]
		assert_true(theme in valid_themes, "chapter %s has invalid theme: %s" % [chapter_id, theme])


func test_arena_boss_chapters_use_fortress_variant():
	var themes = ArenaBuilder.CHAPTER_THEMES
	var boss_ids := [
		"act01_ch003",
		"act02_ch008",
		"act02_ch010",
		"act03_ch012",
		"act03_ch014",
		"act04_ch020",
		"act05_ch025",
		"act06_ch030"
	]
	for boss_id in boss_ids:
		if themes.has(boss_id):
			var theme: String = themes[boss_id]
			assert_true(
				theme == "fortress" or theme == "dark_fortress",
				"boss chapter %s should use fortress variant, got: %s" % [boss_id, theme]
			)


func test_arena_backgrounds_mapped():
	var bgs = ArenaBuilder.CHAPTER_BACKGROUNDS
	assert_true(bgs is Dictionary, "CHAPTER_BACKGROUNDS should be a dictionary")
	assert_true(bgs.size() >= 30, "should have backgrounds for all 30 chapters")


func test_arena_atmosphere_overlays():
	var overlays = ArenaBuilder.ATMOSPHERE_OVERLAYS
	assert_true(overlays.has("field"), "should have field overlay")
	assert_true(overlays.has("forest"), "should have forest overlay")
	assert_true(overlays.has("fortress"), "should have fortress overlay")
	assert_true(overlays.has("dark_fortress"), "should have dark_fortress overlay")


func test_arena_tile_types_defined():
	assert_eq(ArenaBuilder.ARENA_W, 40, "ARENA_W constant")
	assert_eq(ArenaBuilder.ARENA_H, 22, "ARENA_H constant")
	assert_eq(ArenaBuilder.TILE_SIZE, 16, "TILE_SIZE constant")


func test_arena_layout_generation_field():
	var arena = autofree(ArenaBuilder.new())
	var layout = arena._generate_layout("field", "act01_ch001")
	assert_eq(layout.size(), ArenaBuilder.ARENA_H, "layout should have ARENA_H rows")
	for row in layout:
		assert_eq(row.size(), ArenaBuilder.ARENA_W, "each row should have ARENA_W columns")


func test_arena_layout_border_walls():
	var arena = autofree(ArenaBuilder.new())
	var layout = arena._generate_layout("field", "act01_ch001")
	for y in range(layout.size()):
		for x in range(layout[y].size()):
			if y < 2 or y >= ArenaBuilder.ARENA_H - 2:
				assert_eq(
					layout[y][x], 2, "border row should be wall (type 2) at y=%d x=%d" % [y, x]
				)


func test_arena_layout_ground_tiles_valid():
	var arena = autofree(ArenaBuilder.new())
	var layout = arena._generate_layout("field", "act01_ch001")
	var valid_types := [0, 1, 2, 3, 4, 5, 6]
	for y in range(layout.size()):
		for x in range(layout[y].size()):
			assert_true(
				layout[y][x] in valid_types,
				"tile at (%d,%d) should be valid type, got %d" % [y, x, layout[y][x]]
			)


func test_arena_walkable_positions_empty_before_setup():
	var arena = autofree(ArenaBuilder.new())
	var positions = arena.get_walkable_positions()
	assert_eq(positions.size(), 0, "walkable positions should be empty before setup")


func test_arena_hazard_tiles_in_dark_fortress():
	var arena = autofree(ArenaBuilder.new())
	var layout = arena._generate_layout("dark_fortress", "act01_ch003")
	var has_hazard := false
	for row in layout:
		for tile in row:
			if tile == 6:
				has_hazard = true
				break
		if has_hazard:
			break
	assert_true(has_hazard, "dark_fortress layout should contain hazard tiles (type 6)")

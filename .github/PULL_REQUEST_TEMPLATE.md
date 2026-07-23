## Summary
[Brief description of what this PR does]

## Related Issues
[Closes #XXX or relates to #YYY]

## Changes
- [List key changes]

## Testing
- [ ] All GUT tests pass (`godot --headless --path . -s addons/gut/gut_cmdln.gd -gdir=res://test -gexit`)
- [ ] Lint clean (`gdformat --check . && gdlint .`)
- [ ] Manual testing notes: [describe what you tested manually]

## Checklist
- [ ] No `print()` statements in committed code (use `ErrorTracker.report_error()` for runtime errors)
- [ ] No secrets or credentials committed
- [ ] `project.godot` updated if new autoloads/scripts were added
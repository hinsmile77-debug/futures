# Codex Session 2026-05-09 - Chart Toggle And Shutdown Guard

## Summary

- Added same-day guard so that after end-of-day auto shutdown has actually run once, a manual restart later on the same trading day will not trigger `daily_close()` and auto shutdown again.
- Strengthened the minute chart dialog shortcut workflow so `Ctrl+Shift+X` both opens and closes the chart, even when the chart dialog itself has focus.

## Code Changes

### `main.py`

- Added `_restore_auto_shutdown_state()` to restore whether today's auto shutdown already happened from `data/session_state.json`.
- Added runtime flags:
  - `_auto_shutdown_done_today`
  - `_skip_post_close_cycle_today`
- Updated `_increment_session()` rollover state so `auto_shutdown_done_date` is reset when the stored date changes.
- Updated `_scheduler_tick()` so a same-day manual restart after 15:40 skips duplicate `daily_close()` execution.
- Updated `daily_close()` so it does not schedule auto shutdown again when today's auto shutdown already ran.
- Updated `_auto_shutdown()` so it persists `auto_shutdown_done_date = today` before quitting.

### `dashboard/main_dashboard.py`

- Minute chart shortcut changed to `Ctrl+Shift+X`.
- Added a dialog-local `QShortcut` bound to the same key so pressing `Ctrl+Shift+X` while the chart dialog has focus immediately closes the dialog.

## Expected Behavior

1. End-of-day auto shutdown runs once and stores today's shutdown date.
2. User manually restarts the app later on the same date.
3. The app remains open:
   - no duplicate auto shutdown notice
   - no duplicate `_auto_shutdown()`
   - no duplicate `daily_close()` cycle after restart
4. Minute chart opens with `Ctrl+Shift+X`.
5. Pressing `Ctrl+Shift+X` again closes the chart regardless of whether focus is on the main window or the chart dialog.

## Validation To Run Next

- Restart manually after an actual end-of-day auto shutdown and confirm the program stays open.
- Confirm `data/session_state.json` keeps `auto_shutdown_done_date` for the day.
- Repeatedly test `Ctrl+Shift+X` as:
  - open from main window
  - close from chart dialog focus
  - reopen from main window
  - repeat while crosshair/drag interactions are active


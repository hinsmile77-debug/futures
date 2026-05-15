"""Runtime health policy hot-reload and degraded auto/manual gate validation.

This script is a focused harness and does not connect broker/UI.
"""

import os
import re
import sys
import time
import importlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import main  # noqa: E402


class _DummyCB:
    @staticmethod
    def is_entry_allowed():
        return True


class _Collector:
    def __init__(self):
        self.rows = []

    def system(self, msg, level="INFO"):
        self.rows.append(("SYSTEM", level, str(msg)))

    def signal(self, msg):
        self.rows.append(("SIGNAL", "INFO", str(msg)))


def _replace_setting(text, key, value_literal):
    pattern = r"^(\s*%s\s*=\s*).*$" % re.escape(key)
    repl = r"\g<1>%s" % value_literal
    return re.sub(pattern, repl, text, flags=re.MULTILINE)


def main_run():
    collector = _Collector()

    # Build minimal TradingSystem instance without heavy __init__ side effects.
    ts = main.TradingSystem.__new__(main.TradingSystem)
    ts._health_degraded_mode = True
    ts._health_warn_streak = 0
    ts._health_info_streak = 0
    ts._health_policy = main.TradingSystem._build_health_policy()
    ts._health_settings_path = os.path.join(BASE_DIR, "config", "settings.py")
    ts._health_settings_mtime = float(os.path.getmtime(ts._health_settings_path))
    ts._health_policy_last_reload_check = 0.0

    original_system = main.log_manager.system
    original_signal = main.log_manager.signal
    main.log_manager.system = collector.system
    main.log_manager.signal = collector.signal

    settings_path = ts._health_settings_path
    with open(settings_path, "r", encoding="utf-8") as f:
        original_settings = f.read()

    changed = False
    try:
        # 1) Baseline gate behavior before settings change
        auto_block_before = ts._is_degraded_entry_blocked(confidence=0.58, is_manual=False)
        manual_block_before = ts._is_degraded_entry_blocked(confidence=0.58, is_manual=True)

        # 2) Change settings to force manual block and new threshold/hotreload interval
        modified = original_settings
        modified = _replace_setting(modified, "HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY", "True")
        modified = _replace_setting(modified, "HEALTH_DEGRADED_MIN_CONF", "0.60")
        modified = _replace_setting(modified, "HEALTH_POLICY_HOT_RELOAD_INTERVAL_SEC", "1")

        if modified != original_settings:
            with open(settings_path, "w", encoding="utf-8", newline="") as f:
                f.write(modified)
            changed = True

        time.sleep(1.2)
        ts._maybe_reload_health_policy()

        # 3) Re-check gate behavior after hot-reload
        auto_block_after = ts._is_degraded_entry_blocked(confidence=0.58, is_manual=False)
        manual_block_after = ts._is_degraded_entry_blocked(confidence=0.58, is_manual=True)

        # 4) 45분(틱) 시뮬레이션: confidence 시계열에서 자동/수동 차단 카운트
        auto_block_count = 0
        manual_block_count = 0
        total_ticks = 45
        for i in range(total_ticks):
            conf = 0.56 + ((i % 9) * 0.01)  # 0.56 ~ 0.64
            if ts._is_degraded_entry_blocked(confidence=conf, is_manual=False)[0]:
                auto_block_count += 1
            if ts._is_degraded_entry_blocked(confidence=conf, is_manual=True)[0]:
                manual_block_count += 1

        hotreload_logs = [r for r in collector.rows if "핫리로드 반영" in r[2]]

        print("=== Health Policy Hot-Reload Validation ===")
        print("hotreload_log_count:", len(hotreload_logs))
        if hotreload_logs:
            print("hotreload_log_last:", hotreload_logs[-1][2])

        print("auto_block_before:", auto_block_before)
        print("manual_block_before:", manual_block_before)
        print("auto_block_after:", auto_block_after)
        print("manual_block_after:", manual_block_after)
        print("sim_ticks:", total_ticks)
        print("sim_auto_block_count:", auto_block_count)
        print("sim_manual_block_count:", manual_block_count)

        expected_ok = (
            (auto_block_before[0] is True)
            and (manual_block_before[0] is False)
            and (auto_block_after[0] is True)
            and (manual_block_after[0] is True)
            and (len(hotreload_logs) >= 1)
            and (auto_block_count > 0)
            and (manual_block_count > 0)
        )

        print("RESULT:", "PASS" if expected_ok else "FAIL")

    finally:
        if changed:
            with open(settings_path, "w", encoding="utf-8", newline="") as f:
                f.write(original_settings)
            importlib.reload(main.runtime_settings)
        main.log_manager.system = original_system
        main.log_manager.signal = original_signal


if __name__ == "__main__":
    main_run()

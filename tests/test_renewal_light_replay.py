"""[MW0602 신동 주체 리뉴얼] scripts/light_pass_replay.py — 장후 재생 리허설 회귀.

  R1 미륵 피처 ATR 이 경량 ATR 과 같은 정의면 PASS(12부품 · ATR · CB④ · 시간)
  R2 미륵 피처 ATR 이 다르면 FAIL(② ATR) — 판정 기준이 실제로 작동한다
  R3 raw_features 가 없으면 ATR·CB④ 는 「미측정」이고 판정은 나머지로만(PASS 도 FAIL 도 아님 ≠ 0)
  R4 신동 보유 구간이 없으면 P8 은 「미발동」(누락으로 세지 않는다)
  R5 그날 봉이 없으면 NO_DATA · 종료코드 2
"""
import datetime
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402
from features.technical.atr import ATRCalculator  # noqa: E402
from scripts import light_pass_replay as LR  # noqa: E402

D = "2026-10-26"


def _mk(tmp, feats="same", trade=True):
    raw = os.path.join(str(tmp), "raw.db")
    sd = os.path.join(str(tmp), "sd.db")
    con = sqlite3.connect(raw)
    con.execute("CREATE TABLE raw_candles (ts TEXT, open REAL, high REAL, low REAL, close REAL, volume INT)")
    con.execute("CREATE TABLE raw_features (ts TEXT, features TEXT)")
    calc = ATRCalculator()
    t = datetime.datetime(2026, 10, 26, 8, 45)
    px = 1000.0
    i = 0
    while t.strftime("%H:%M") <= "15:12":
        px += (1 if i % 3 else -1) * 0.7
        h, l = px + 0.8 + (i % 5) * 0.1, px - 0.6
        ts = t.strftime("%Y-%m-%d %H:%M:%S")
        con.execute("INSERT INTO raw_candles VALUES (?,?,?,?,?,?)", (ts, px, h, l, px, 100))
        r = calc.update(h, l, px)
        if feats != "none" and t.strftime("%H:%M") >= "09:00":
            atr = r["atr"] * (1.5 if feats == "diff" else 1.0)
            con.execute("INSERT INTO raw_features VALUES (?,?)",
                        (ts, json.dumps({"atr": atr, "atr_ratio": r["atr_ratio"]})))
        t += datetime.timedelta(minutes=1)
        i += 1
    con.commit()
    con.close()
    s = sqlite3.connect(sd)
    s.execute("CREATE TABLE shindong_trades (trade_date TEXT, variant TEXT, entry_ts TEXT, leg1_exit_ts TEXT,"
              " leg2_exit_ts TEXT, status TEXT)")
    if trade:
        s.execute("INSERT INTO shindong_trades VALUES (?,?,?,?,?,?)",
                  (D, "MAIN", D + " 10:00:00", D + " 10:40:00", D + " 10:40:00", "CLOSED"))
    s.commit()
    s.close()
    return raw, sd


def test_R1_same_definition_passes(tmp_path):
    raw, sd = _mk(tmp_path)
    r = LR.replay(D, raw, sd, main_mod=main)
    assert r["verdict"] == "PASS", r["lines"]
    st = r["stats"]
    assert st["missing_parts"] == [] and st["hold_bars"] == 40
    assert st["atr_cmp"] > 300 and st["atr_max_rel"] < 1e-6
    assert st["bars"] == 370                       # 09:00 ~ 15:09
    assert r["exit_code"] == 0


def test_R2_atr_mismatch_fails(tmp_path):
    raw, sd = _mk(tmp_path, feats="diff")
    r = LR.replay(D, raw, sd, main_mod=main)
    assert r["verdict"] == "FAIL" and r["exit_code"] == 1
    assert any("② ATR" in ln and "FAIL" in ln for ln in r["lines"])


def test_R3_no_features_is_unmeasured_not_fail(tmp_path):
    raw, sd = _mk(tmp_path, feats="none")
    r = LR.replay(D, raw, sd, main_mod=main)
    assert r["verdict"] == "PASS"
    assert any("② ATR    : 미측정" in ln for ln in r["lines"])
    assert any("③ CB④    : 미측정" in ln for ln in r["lines"])


def test_R4_no_holding_means_p8_not_required(tmp_path):
    raw, sd = _mk(tmp_path, trade=False)
    r = LR.replay(D, raw, sd, main_mod=main)
    assert r["verdict"] == "PASS" and r["stats"]["hold_bars"] == 0
    assert any("P8 미발동" in ln for ln in r["lines"])


def test_R5_no_bars(tmp_path):
    r = LR.replay("2026-10-27", os.path.join(str(tmp_path), "none.db"), None, main_mod=main)
    assert r["verdict"] == "NO_DATA" and r["exit_code"] == 2


def test_R6_patches_are_restored(tmp_path):
    raw, sd = _mk(tmp_path)
    keep = (main._ts_vbook_on_bar, main.log_manager, main.fetch_recent_raw_candles, main.save_candle)
    LR.replay(D, raw, sd, main_mod=main)
    assert keep == (main._ts_vbook_on_bar, main.log_manager, main.fetch_recent_raw_candles, main.save_candle)

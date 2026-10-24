# -*- coding: utf-8 -*-
"""[MW0602 신동 주체 리뉴얼] 장후 재생 리허설 — 그날 실제 1분봉을 미륵 휴면 경량 분봉 패스에 흘린다.

실거래를 멈추지 않는 전환 검증의 두 번째 겹이다(계획서 Phase 6-B). 첫 겹은 장중 병행 건식 실행
(`LIGHT_PASS_DRY_RUN`)이고, 이 스크립트는 장후에 하루치를 한 번에 본다.

무엇을 하나
-----------
`main.TradingSystem._light_minute_pass` **실제 코드**를 대역 객체(브로커·Qt·DB 쓰기 없음)에 붙여
그날 `raw_candles` 를 분 순서대로 넣는다. 신동 MAIN 거래(`shindong.db`)의 진입~청산 구간에는 포지션을
보유 중으로 두어 청산 감시(P8)가 실제로 불리는지도 본다. 08:45~08:59 봉은 프리장 경로처럼 ATR 만 먹인다.

판정 (결과를 보기 전에 고정 — 바꾸려면 이 주석·상수·회귀 테스트를 함께 고칠 것)
-----------------------------------------------------------------------------
  ① 부품   : 12부품이 전부 불렸다(P8 은 그날 신동 보유 구간이 있을 때만 요구 — 없으면 「미발동」)
  ② ATR    : 09:15 이후 비교 가능한 봉의 95% 이상에서 경량 ATR 과 미륵 피처 ATR 의 상대오차 ≤ 10%
             (`raw_features` 가 없으면 미측정 — PASS 도 FAIL 도 아니다. 계측 4원칙 ②)
  ③ CB④    : 경량 ATR 비율 ≥ CB_ATR_MULT_LIMIT 인 봉 수 == 미륵 피처 기준 봉 수(미측정이면 생략)
  ④ 시간   : 봉당 경량 패스 최대 < 1,000ms
  종료코드  0 = PASS · 1 = FAIL · 2 = 데이터 없음(그날 봉 0)

읽기 전용이다 — DB 에 쓰지 않는다(`save_candle` 은 대역이 센다). 장중에는 돌리지 않는다(456차).

실행:
    python scripts/light_pass_replay.py --date 2026-10-26
    python scripts/light_pass_replay.py --date 2026-10-26 --out docs/.../replay_20261026.md
"""
import argparse
import datetime
import io
import json
import os
import queue
import sqlite3
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402

ensure_conda_dll_path()

ATR_REL_TOL = 0.10
ATR_PASS_SHARE = 0.95
ATR_COMPARE_FROM = "09:15"
MAX_MS = 1000.0


def _ro(path):
    if not path or not os.path.exists(path):
        return None
    con = sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True, timeout=5.0)
    con.row_factory = sqlite3.Row
    return con


def load_day(date_str, raw_db, sd_db):
    """→ (bars[dict], feats{ts: {atr, atr_ratio}} 또는 None, holds[(entry_ts, exit_ts)] 또는 None)."""
    nxt = (datetime.date.fromisoformat(date_str) + datetime.timedelta(days=1)).isoformat()
    bars, feats, holds = [], None, None
    con = _ro(raw_db)
    if con is not None:
        try:
            for r in con.execute("SELECT ts, open, high, low, close, volume FROM raw_candles "
                                 "WHERE ts>=? AND ts<? ORDER BY ts", (date_str, nxt)):
                bars.append({"ts": datetime.datetime.strptime(str(r["ts"])[:19], "%Y-%m-%d %H:%M:%S"),
                             "open": r["open"], "high": r["high"], "low": r["low"],
                             "close": r["close"], "volume": r["volume"]})
            try:
                rows = con.execute("SELECT ts, features FROM raw_features WHERE ts>=? AND ts<?",
                                   (date_str, nxt)).fetchall()
                feats = {}
                for r in rows:
                    try:
                        f = json.loads(r["features"])
                        feats[str(r["ts"])[:19]] = {"atr": f.get("atr"), "atr_ratio": f.get("atr_ratio")}
                    except (TypeError, ValueError):
                        continue
                if not feats:
                    feats = None
            except sqlite3.OperationalError:
                feats = None
        finally:
            con.close()
    sc = _ro(sd_db)
    if sc is not None:
        try:
            holds = []
            for r in sc.execute("SELECT entry_ts, leg1_exit_ts, leg2_exit_ts, status FROM shindong_trades "
                                "WHERE trade_date=? AND variant='MAIN' AND status!='RETRACTED' ORDER BY entry_ts",
                                (date_str,)):
                ex = max([x for x in (r["leg1_exit_ts"], r["leg2_exit_ts"]) if x] or ["%s 15:05:00" % date_str])
                holds.append((str(r["entry_ts"])[:16], str(ex)[:16]))
        except sqlite3.OperationalError:
            holds = None
        finally:
            sc.close()
    return bars, feats, holds


def _harness(main):
    TS = main.TradingSystem
    from features.technical.atr import ATRCalculator

    class _Pos(object):
        status = "FLAT"

    class _Dash(object):
        def __init__(self, calls):
            self.calls = calls

        def notify_pipeline_ran(self):
            self.calls.append("notify")

        def update_price(self, **k):
            pass

        def update_system_status(self, **k):
            pass

        def update_profit_guard_badge(self, st):
            pass

    class _CB(object):
        state = "NORMAL"

        def __init__(self, h):
            self.h = h

        def record_atr(self, r):
            self.h.calls.append("P10_cb4_record_atr")
            self.h.last_ratio = r

        def record_pipe_latency(self, ms):
            self.h.calls.append("P11_cb5_record_latency")

    class _PG(object):
        def guard_status(self, pnl, size_mult, dt):
            return {}

    class H(object):
        LIGHT_PASS_PARTS = TS.LIGHT_PASS_PARTS
        _light_minute_pass = TS._light_minute_pass
        _bar_price_guard = TS._bar_price_guard
        _light_atr_prime = TS._light_atr_prime
        _light_atr_update = TS._light_atr_update
        _light_push_profit_guard_badge = TS._light_push_profit_guard_badge

        def __init__(self):
            self.calls = []
            self.last_ratio = None
            self.position = _Pos()
            self.dashboard = _Dash(self.calls)
            self.circuit_breaker = _CB(self)
            self.profit_guard = _PG()
            self.realtime_data = None
            self._db_write_queue = queue.Queue()
            self._light_atr = ATRCalculator()
            self._light_atr_dry = ATRCalculator()
            self._light_atr_day = None
            self._light_atr_dry_day = None
            self._light_last_ts = None
            self._sys_daily_net_krw = 0.0
            self._sys_daily_legs = 0
            self._sys_daily_other_krw = 0.0
            self._sys_daily_other_legs = 0
            self._pg_badge_err_logged = False
            self._manual_entry_ctx = {}
            self._maint_ctx = None
            self._last_real_pipeline_dt = None
            self._sigma_prev_price = 0.0
            self._last_pipe_ms = 0.0

        def _maybe_compute_levels_0930(self, ts_raw):
            self.calls.append("P3_levels_0930")

        def _process_tick_stop(self):
            self.calls.append("P7_tick_stop")

        def _check_pending_order_timeout(self):
            self.calls.append("P6_pending_timeout")

        def _check_exit_triggers(self, price, features, decision, bar=None):
            self.calls.append("P8_exit_triggers")

        def _push_position_panels(self, close, atr, bar, atr_ok=None, open_gap_ok=None):
            self.calls.append("P12_panels")

    return H


def replay(date_str, raw_db, sd_db, atr_limit=3.0, main_mod=None):
    """→ dict(verdict, exit_code, lines[...], stats{...})."""
    if main_mod is None:
        import main as main_mod
    bars, feats, holds = load_day(date_str, raw_db, sd_db)
    out = {"date": date_str, "lines": [], "stats": {}}
    say = out["lines"].append
    if not bars:
        out.update(verdict="NO_DATA", exit_code=2)
        say("[LightReplay] %s raw_candles 0봉 — 판정 불가(데이터 없음)" % date_str)
        return out

    H = _harness(main_mod)
    h = H()
    rec = {"vbook": 0}
    saved = []

    class _LM(object):
        def system(self, msg, level="INFO"):
            pass

        def trade(self, *a, **k):
            pass

        def signal(self, *a, **k):
            pass

    def _vb(self, bar, atr):
        self.calls.append("P10_vbook_on_bar")
        rec["vbook"] += 1

    prior = []

    def _recent(limit=60):
        return prior[-limit:]

    patches = {"_ts_vbook_on_bar": _vb, "log_manager": _LM(), "fetch_recent_raw_candles": _recent,
               "save_candle": lambda b: saved.append(b)}
    orig = {k: getattr(main_mod, k) for k in patches}
    for k, v in patches.items():
        setattr(main_mod, k, v)
    seen = set()
    ms = []
    cmp_n = cmp_ok = 0
    max_rel = 0.0
    cb4_light = cb4_mireuk = 0
    hold_bars = 0
    try:
        for b in bars:
            hm = b["ts"].strftime("%H:%M")
            ts = b["ts"].strftime("%Y-%m-%d %H:%M:%S")
            if hm < "09:00":
                h._light_atr_update(False, b["high"], b["low"], b["close"], ts)   # 프리장 경로와 같다
                prior.append(dict(b, ts=ts))
                continue
            if hm >= "15:10":
                break                                   # 15:10 이후는 청산 전용 패스(경량 패스 밖)
            ym = b["ts"].strftime("%Y-%m-%d %H:%M")
            holding = bool(holds) and any(e <= ym < x for e, x in holds)
            h.position.status = "LONG" if holding else "FLAT"
            hold_bars += int(holding)
            n0 = len(h.calls)
            t0 = time.perf_counter()
            h._light_minute_pass(b)
            ms.append((time.perf_counter() - t0) * 1000.0)
            for c in h.calls[n0:]:
                if isinstance(c, str) and c.startswith("P"):
                    seen.add(c)
            while not h._db_write_queue.empty():
                it = h._db_write_queue.get_nowait()
                if it and it[0] == "candle":
                    seen.add("P1_save_candle")
            if h._light_last_ts == ts:
                seen.update(("P5_dup_guard", "P5_bar_guard"))
            if h._manual_entry_ctx.get("atr"):
                seen.add("P10_atr")
            r_light = h.last_ratio
            if r_light is not None and r_light >= atr_limit:
                cb4_light += 1
            mf = (feats or {}).get(ts)
            if mf:
                if mf.get("atr_ratio") is not None and float(mf["atr_ratio"]) >= atr_limit:
                    cb4_mireuk += 1
                if hm >= ATR_COMPARE_FROM and mf.get("atr") not in (None, 0):
                    rel = abs(float(h._manual_entry_ctx["atr"]) - float(mf["atr"])) / abs(float(mf["atr"]))
                    cmp_n += 1
                    cmp_ok += int(rel <= ATR_REL_TOL)
                    max_rel = max(max_rel, rel)
            prior.append(dict(b, ts=ts))
    finally:
        for k, v in orig.items():
            setattr(main_mod, k, v)

    need = set(H.LIGHT_PASS_PARTS)
    if not hold_bars:
        need.discard("P8_exit_triggers")
    missing = sorted(need - seen)
    ok_parts = not missing
    if feats is None:
        ok_atr = None
    else:
        ok_atr = (cmp_n > 0 and cmp_ok / float(cmp_n) >= ATR_PASS_SHARE)
    ok_cb4 = None if feats is None else (cb4_light == cb4_mireuk)
    ms_max = max(ms) if ms else 0.0
    ok_ms = ms_max < MAX_MS
    checks = [ok_parts, ok_ms] + [x for x in (ok_atr, ok_cb4) if x is not None]
    verdict = "PASS" if all(checks) else "FAIL"
    ms_sorted = sorted(ms)
    p95 = ms_sorted[int(0.95 * (len(ms_sorted) - 1))] if ms_sorted else 0.0
    out["stats"] = {"bars": len(ms), "hold_bars": hold_bars, "missing_parts": missing,
                    "atr_cmp": cmp_n, "atr_ok": cmp_ok, "atr_max_rel": max_rel,
                    "cb4_light": cb4_light, "cb4_mireuk": cb4_mireuk, "ms_p95": p95, "ms_max": ms_max,
                    "saved_sync": len(saved)}
    say("[LightReplay] %s 경량 패스 %d봉(09:00~15:09) · 신동 보유 %s분" % (
        date_str, len(ms), hold_bars if holds is not None else "미측정(shindong.db 없음)"))
    say("  ① 부품   : %s" % ("12/12 호출" if ok_parts and hold_bars else
                              ("11/12 호출 · P8 미발동(보유 구간 없음)" if ok_parts else
                               "누락 %s" % ", ".join(missing))))
    if ok_atr is None:
        say("  ② ATR    : 미측정(raw_features 없음 — 미륵 휴면일이면 정상)")
    else:
        say("  ② ATR    : %d/%d봉 상대오차 ≤ %.0f%% (%.1f%% · 기준 %.0f%%) · 최대 %.1f%% — %s" % (
            cmp_ok, cmp_n, ATR_REL_TOL * 100, (100.0 * cmp_ok / cmp_n) if cmp_n else 0.0,
            ATR_PASS_SHARE * 100, max_rel * 100, "OK" if ok_atr else "FAIL"))
    if ok_cb4 is None:
        say("  ③ CB④    : 미측정(raw_features 없음)")
    else:
        say("  ③ CB④    : 경량 %d봉 vs 미륵 %d봉 (비율 ≥ %.1f) — %s" % (
            cb4_light, cb4_mireuk, atr_limit, "OK" if ok_cb4 else "FAIL"))
    say("  ④ 시간   : 봉당 p95 %.1fms · 최대 %.1fms (기준 < %.0fms) — %s" % (
        p95, ms_max, MAX_MS, "OK" if ok_ms else "FAIL"))
    say("  판정     : %s" % verdict)
    out.update(verdict=verdict, exit_code=0 if verdict == "PASS" else 1)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="미륵 휴면 경량 분봉 패스 장후 재생 리허설")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--raw-db", default=None)
    ap.add_argument("--sd-db", default=None)
    ap.add_argument("--out", default=None, help="결과를 md 로도 저장")
    a = ap.parse_args(argv)
    now = datetime.datetime.now()
    if a.date == now.date().isoformat() and datetime.time(8, 40) <= now.time() < datetime.time(15, 40):
        print("[LightReplay] 장중 실행 금지(15:40 이후) — 대형 DB 장중 스캔 규약(456차)")
        return 2
    from config import settings as S
    r = replay(a.date, a.raw_db or S.RAW_DATA_DB, a.sd_db or S.SHINDONG_DB,
               atr_limit=float(getattr(S, "CB_ATR_MULT_LIMIT", 3.0)))
    txt = "\n".join(r["lines"])
    # 파일을 먼저 쓴다 — Windows 콘솔(cp949)은 '—' 등을 못 찍어 print 가 판정 뒤에 죽었다(2026-10-25 실측).
    if a.out:
        with io.open(a.out, "w", encoding="utf-8") as f:
            f.write("```\n" + txt + "\n```\n")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    print(txt)
    return r["exit_code"]


if __name__ == "__main__":
    sys.exit(main())

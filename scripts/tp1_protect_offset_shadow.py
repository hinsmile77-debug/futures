# scripts/tp1_protect_offset_shadow.py
"""[404차 후속3, 캠페인 25] TP1 보호전환 offset 폭 A/B 카운터팩추얼 — 읽기 전용.

무엇을 묻는가
--------------
qty=1 포지션은 TP1에서 물리적 분할청산이 불가능해 "보호스톱 전환"만 일어난다
(position_tracker.arm_tp1_single_contract_with_mode). 보호스톱은 **진입가 기준**으로

    protected_stop = entry_price ± protect_offset_pts
      breakeven       : offset = 0
      breakeven_plus  : offset = alpha_pts (0.20)
      atr_profit      : offset = ATR × TP1_PROTECT_ATR_LOCK_MULT (0.25)   ← 현행

이 offset이 "TP1을 찍은 뒤 얼마를 지키느냐"를 결정한다. 0731 케이스①은 TP1 도달
5초 만에 이 보호스톱에 걸려 +1.46pt 장부이익이 +0.58pt로 끝났고, 그 직후 가격은
+6.58pt까지 갔다. 이 채널은 "offset이 달랐다면 어땠을까"를 실제 분봉으로 재생한다.

왜 라이브 코드를 안 건드리는가
------------------------------
필요한 입력이 전부 이미 저장돼 있다 — synthetic_partial_exits(진입가·TP1 도달가·
보호스톱·모드, TP1 전환 시점마다 1행) + raw_candles(고저가). tp1_geometry_shadow
(403차 P1-6)와 동일한 설계이며, 진입 경로에 섀도 INSERT를 심지 않는 만큼 라이브
회귀 위험이 0이고 **과거 표본에 소급 적용된다**(신설 즉시 판정 가능).

무엇을 결론으로 삼을 수 있나 / 없나
-----------------------------------
- 사전등록 기준은 config/settings.py VALIDATION_CAMPAIGN["tp1_protect_offset_shadow"]에
  고정돼 있다. 관측 후 기준을 바꾸지 말 것(§9).
- ⚠ **사전등록 원칙상 반드시 밝힐 것**: `breakeven` 변형의 결과는 이 채널을 만들기
  전(404차 후속3 조사)에 이미 1회 측정됐다(23건, 22/23 현행 우세). 따라서 breakeven
  항목은 **재확인용이지 사전등록된 검증이 아니다.** 이 채널의 사전등록 가치는
  아직 측정된 적 없는 `atr_lock_0.50` / `atr_lock_0.75` / `bar_range` 세 변형에 있다.
- 313차 원칙: min_days 미달이면 판정하지 않는다.
- [12] tp1_trail_shadow가 이미 기각한 "TP1 이후 더 느슨한 트레일링"과는 **다른
  질문**이다 — 그건 TP1 이후 트레일 폭, 이건 TP1 시점의 초기 보호 offset이다.

한계 (반드시 함께 읽을 것)
--------------------------
- 1분봉 고저가 기준이라 봉 내 도달 순서를 알 수 없다. 보호스톱·TP2가 같은 봉에서
  모두 닿으면 보수적으로 **스톱을 먼저** 적용한다(캠페인 다른 채널과 동일 관례).
- TP3·4단계 트레일링·신호소멸청산은 모델링하지 않고 TP2/스톱/15:10만 본다. 이
  요소들은 모든 변형에 동일하게 빠지므로 **변형 간 상대비교는 유효**하지만,
  절대값을 실현손익으로 인용하면 안 된다.
- ATR은 저장된 offset에서 역산한다(offset = ATR × 0.25). 현행이 atr_profit이 아닌
  행(breakeven 등)은 ATR 역산이 불가능해 제외된다.

실행:
    py310_64\python.exe scripts/tp1_protect_offset_shadow.py [--since 2026-06-01]
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config.settings import (  # noqa: E402
    TRADES_DB, RAW_DATA_DB, VALIDATION_CAMPAIGN, ATR_TP2_MULT,
    FUTURES_COMMISSION_RATE, TICK_SIZE,
)
from config.constants import MINI_FUTURES_PT_VALUE  # noqa: E402

_CR = VALIDATION_CAMPAIGN.get("tp1_protect_offset_shadow", {})
_LOCK_MULT_CURRENT = 0.25          # main.py:TP1_PROTECT_ATR_LOCK_MULT
_BAR_RANGE_LOOKBACK = 3            # bar_range 변형: 직전 N봉
_MAX_MIN = 360                     # 재생 상한(분) — 15:10 컷이 먼저 걸리는 게 정상


def _conn(p):
    c = sqlite3.connect(p, timeout=15)
    c.row_factory = sqlite3.Row
    return c


def _cost_pts(px: float) -> float:
    slip = float(VALIDATION_CAMPAIGN.get("slippage_ticks_per_side", 1.0))
    return 2.0 * px * FUTURES_COMMISSION_RATE + 2.0 * slip * TICK_SIZE


def _load_hooks(since: str):
    """TP1 보호전환 시점 **전량** — 모드 분류·ATR 확보는 compute()가 한다.

    [MW0601 406차 / C] 예전에는 여기서 `AND protect_mode = 'atr_profit'`으로 걸렀다.
    거르는 것 자체는 옳다(`current` 변형이 "실제 일어난 일"이어야 판정식이 성립한다)
    — 다만 **몇 건이 왜 빠졌는지가 어디에도 남지 않아** MW0601의 n=0이 "표본이 아직
    안 쌓였다"로 오독됐다. 전량을 읽어 와서 compute()가 사유별로 세고 리포트가
    "해당 없음(모드 breakeven) N건"까지 표기한다. **판정 모집단은 그대로다.**

    atr / protect_offset_pts는 406차 B에서 신설된 컬럼이라, 아직 마이그레이션이
    적용되지 않은 DB(예: 코드만 먼저 pull한 PC)에서도 죽지 않도록 PRAGMA로 확인한다.
    """
    with _conn(TRADES_DB) as c:
        cols = {r[1] for r in c.execute(
            "PRAGMA table_info(synthetic_partial_exits)").fetchall()}
        extra = ", atr, protect_offset_pts" if "atr" in cols else ""
        return [dict(r) for r in c.execute(
            """SELECT ts, entry_ts, direction, entry_price, synthetic_price,
                      synthetic_pnl_pts, protect_mode, stop_after%s
                 FROM synthetic_partial_exits
                WHERE ts >= ? ORDER BY ts""" % extra, (since,))]


def _load_candles(since: str):
    with _conn(RAW_DATA_DB) as c:
        rows = c.execute(
            "SELECT ts, high, low FROM raw_candles WHERE ts >= ? ORDER BY ts",
            (since,)).fetchall()
    return [(r["ts"], float(r["high"]), float(r["low"])) for r in rows]


def _offset_for(name: str, atr: float, bar_rng: float) -> float:
    if name == "current":
        return atr * _LOCK_MULT_CURRENT
    if name == "breakeven":
        return 0.0
    if name == "breakeven_plus":
        return 0.20
    if name == "atr_lock_0.50":
        return atr * 0.50
    if name == "atr_lock_0.75":
        return atr * 0.75
    if name == "bar_range":
        return max(atr * _LOCK_MULT_CURRENT, bar_rng * 0.5)
    raise ValueError("unknown variant: %s" % name)


def _simulate(bars, i0, is_long, entry_px, stop_px, tp2_px):
    """보호전환 시점 이후 재생 — STOP/TP2/시간만료 중 먼저. 동시 도달은 STOP 우선."""
    sgn = 1 if is_long else -1
    day = bars[i0][0][:10]
    for j in range(i0 + 1, min(i0 + 1 + _MAX_MIN, len(bars))):
        ts, hi, lo = bars[j]
        if ts[:10] != day or ts[11:16] > "15:10":
            break
        hit_stop = (lo <= stop_px) if is_long else (hi >= stop_px)
        hit_tp2 = (hi >= tp2_px) if is_long else (lo <= tp2_px)
        if hit_stop:
            return "STOP", sgn * (stop_px - entry_px)
        if hit_tp2:
            return "TP2", sgn * (tp2_px - entry_px)
    # 15:10 강제청산 — 마지막 관측봉 중간값
    j = min(i0 + _MAX_MIN, len(bars) - 1)
    px = (bars[j][1] + bars[j][2]) / 2.0
    return "FORCED", sgn * (px - entry_px)


def compute(since: str = "2026-06-01") -> dict:
    hooks = _load_hooks(since)
    bars = _load_candles(since)
    idx = {t: i for i, (t, _, _) in enumerate(bars)}
    variants = list(_CR.get("variants", ["current"]))
    res = {v: [] for v in variants}
    days, skipped = set(), 0

    # [MW0601 406차 / C] 제외 사유별 카운터 — 예전에는 전부 skipped 하나로 뭉뚱그려져
    # "왜 표본이 없는지"를 리포트가 말해줄 수 없었다.
    n_other_mode: dict = {}     # atr_profit이 아니라 판정 모집단에서 빠진 건수(모드별)
    n_backout_legacy = 0        # atr 컬럼 이전 행 — 역산 폴백을 쓴 건수
    n_excluded_override = 0     # prev_stop 오버라이드가 확인돼 제외한 건수

    for h in hooks:
        # 판정 모집단은 atr_profit 행만이다 — `current` 변형(ATR×0.25)이 "실제로
        # 일어난 일"과 일치해야 delta_vs_current가 의미를 갖는다. 다른 모드 행은
        # 세어만 두고 리포트가 사유로 표기한다(판정 기준 무변경).
        mode = str(h.get("protect_mode") or "").strip().lower()
        if mode != "atr_profit":
            n_other_mode[mode or "(미기록)"] = n_other_mode.get(mode or "(미기록)", 0) + 1
            continue
        ts = h["ts"]
        i0 = idx.get(ts)
        if i0 is None:
            skipped += 1
            continue
        ep = float(h["entry_price"])
        off_from_entry = abs(float(h["stop_after"]) - ep)
        _stored_atr = h.get("atr")
        _stored_off = h.get("protect_offset_pts")
        if _stored_atr is not None and float(_stored_atr) > 0:
            # [406차 B] 보호전환 시점의 ATR 원본. 역산이 필요 없다.
            atr = float(_stored_atr)
        else:
            # 레거시 행(atr 컬럼 이전) — |stop_after-entry|/0.25 역산 폴백.
            # ⚠ position_tracker:749-751의 prev_stop 오버라이드가 걸린 행에서는 이
            # 값이 ATR이 아니라 트레일링 스톱이다. protect_offset_pts가 있으면
            # 대조해서 걸러내고, 없으면(진짜 레거시) 걸러낼 방법이 없어 그대로 쓴다
            # — 그 건수를 n_backout_legacy로 노출해 해석 시 감안하게 한다.
            if (_stored_off is not None
                    and abs(float(_stored_off) - off_from_entry) > 1e-6):
                n_excluded_override += 1
                skipped += 1
                continue
            atr = off_from_entry / _LOCK_MULT_CURRENT if off_from_entry > 0 else 0.0
            if atr <= 0:
                skipped += 1
                continue
            n_backout_legacy += 1
        is_long = str(h["direction"]).upper() == "LONG"
        sgn = 1 if is_long else -1
        # 직전 N봉 평균 레인지
        lo_i = max(0, i0 - _BAR_RANGE_LOOKBACK)
        rngs = [hi - lo for _, hi, lo in bars[lo_i:i0]] or [atr]
        bar_rng = sum(rngs) / len(rngs)
        tp2 = ep + sgn * atr * ATR_TP2_MULT
        cost = _cost_pts(ep)
        days.add(ts[:10])
        for v in variants:
            off = _offset_for(v, atr, bar_rng)
            stop = ep + sgn * off
            outcome, pts = _simulate(bars, i0, is_long, ep, stop, tp2)
            res[v].append((outcome, pts - cost))

    return {"variants": variants, "rows": res,
            "n_hooks": len(hooks) - skipped - sum(n_other_mode.values()),
            "n_skipped": skipped, "n_days": len(days), "since": since,
            # [MW0601 406차 / C]
            "n_other_mode": n_other_mode,
            "n_backout_legacy": n_backout_legacy,
            "n_excluded_override": n_excluded_override}


def summarize(out: dict) -> dict:
    res = out["rows"]
    base = res.get("current", [])
    base_total = sum(p for _, p in base) if base else None
    per = {}
    for v in out["variants"]:
        rows = res.get(v, [])
        if not rows:
            continue
        pts = [p for _, p in rows]
        per[v] = {
            "n": len(pts),
            "total_pt": round(sum(pts), 4),
            "median_pt": round(sorted(pts)[len(pts) // 2], 4),
            "win_rate": round(sum(1 for p in pts if p > 0) / len(pts), 4),
            "max_loss_pt": round(min(pts), 4),
            "n_stop": sum(1 for o, _ in rows if o == "STOP"),
            "n_tp2": sum(1 for o, _ in rows if o == "TP2"),
            "n_forced": sum(1 for o, _ in rows if o == "FORCED"),
            "delta_vs_current": (round(sum(pts) - base_total, 4)
                                 if base_total is not None else None),
            "beats_current_n": (sum(1 for (_, p), (_, q) in zip(rows, base) if p > q)
                                if base and len(rows) == len(base) else None),
        }
    min_n = int(_CR.get("min_samples", 20))
    min_d = int(_CR.get("min_days", 3))
    n_cur = len(base)
    if n_cur < min_n or out["n_days"] < min_d:
        verdict, reason = "INSUFFICIENT", ("표본 부족 (n=%d<%d 또는 거래일=%d<%d)"
                                           % (n_cur, min_n, out["n_days"], min_d))
        # [MW0601 406차 / E] "곧 표본이 찬다"와 "이 PC에서는 영원히 안 찬다"를 구분한다.
        # 판정 모집단은 atr_profit 행뿐인데, 라이브 모드가 breakeven이면 아무리
        # 기다려도 이 채널은 채워지지 않는다 — 그 사실을 사유에 명시한다.
        _other = out.get("n_other_mode") or {}
        if _other and n_cur == 0:
            _desc = (list(_other)[0] if len(_other) == 1
                     else "/".join("%s %d건" % kv for kv in sorted(_other.items())))
            reason = ("해당 없음 — 보호전환 %d건이 전부 `%s` 모드다. 판정 모집단은 "
                      "atr_profit 행이므로 라이브 모드를 atr_profit으로 두기 전에는 "
                      "표본이 쌓이지 않는다(대기해도 무의미)"
                      % (sum(_other.values()), _desc))
        elif _other:
            reason += " · 모드 불일치 제외 %d건(%s)" % (
                sum(_other.values()),
                "/".join("%s %d" % kv for kv in sorted(_other.items())))
    else:
        beat = [k for k, v in per.items()
                if k != "current" and (v["delta_vs_current"] or 0) > 0]
        verdict = "FAIL" if beat else "PASS"
        reason = ("현행 초과 대안: %s" % ", ".join(beat)) if beat else "모든 대안이 현행 이하"
    return {"verdict": verdict, "reason": reason, "per_variant": per,
            "n_hooks": out["n_hooks"], "n_days": out["n_days"],
            "n_skipped": out["n_skipped"], "min_samples": min_n, "min_days": min_d,
            # [MW0601 406차 / C·E] 제외 사유 노출 — 해석에 필요하다.
            # n_backout_legacy가 크면 그만큼 ATR이 검증 불가한 역산값이라는 뜻이다.
            "n_other_mode": out.get("n_other_mode") or {},
            "n_backout_legacy": out.get("n_backout_legacy", 0),
            "n_excluded_override": out.get("n_excluded_override", 0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-06-01")
    args = ap.parse_args()
    out = compute(args.since)
    s = summarize(out)

    print("=" * 92)
    print("TP1 보호전환 offset A/B 카운터팩추얼   기간 %s~" % args.since)
    print("사전등록 기준: config/settings.py VALIDATION_CAMPAIGN['tp1_protect_offset_shadow']")
    print("=" * 92)
    print("보호전환 %d건 (제외 %d건) / 거래일 %d일"
          % (out["n_hooks"], out["n_skipped"], out["n_days"]))
    print()
    print("%-16s %5s %7s %7s %7s %9s %9s %9s"
          % ("변형", "n", "STOP", "TP2", "강제", "승률", "누적pt", "중앙값"))
    for v in out["variants"]:
        d = s["per_variant"].get(v)
        if not d:
            print("%-16s (표본 없음)" % v)
            continue
        print("%-16s %5d %7d %7d %7d %8.1f%% %+9.2f %+9.3f"
              % (v, d["n"], d["n_stop"], d["n_tp2"], d["n_forced"],
                 d["win_rate"] * 100, d["total_pt"], d["median_pt"]))
    print()
    print("현행 대비 차이 (pt / 1계약 환산 원 / 건별 우세):")
    for v in out["variants"]:
        d = s["per_variant"].get(v)
        if not d or v == "current":
            continue
        print("  %-16s %+8.2f pt   %+12s 원   우세 %s/%d건"
              % (v, d["delta_vs_current"],
                 format(int((d["delta_vs_current"] or 0) * MINI_FUTURES_PT_VALUE), ","),
                 d["beats_current_n"], d["n"]))
    print()
    print("판정: %s — %s" % (s["verdict"], s["reason"]))
    print("§9: 이 스크립트는 판정을 자동 적용하지 않는다. 적용은 주간회의 수동 결정.")
    print("⚠ breakeven 변형은 404차 후속3 조사에서 이미 1회 측정됨 — 사전등록 검증이")
    print("  아니라 재확인용이다. 사전등록 가치는 atr_lock_0.50/0.75·bar_range에 있다.")
    print("⚠ 절대값은 실현손익이 아니다(TP3·트레일링·신호소멸 미모델링). 상대비교 전용.")


if __name__ == "__main__":
    main()

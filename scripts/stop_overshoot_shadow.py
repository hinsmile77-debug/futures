# -*- coding: utf-8 -*-
"""scripts/stop_overshoot_shadow.py — [MW0602 470차 D2'] 손절 오버슛(shakeout) 섀도 계측

════════════════════════════════════════════════════════════════════════════
왜 이 축이 필요한가
════════════════════════════════════════════════════════════════════════════
417차 재분해는 진입수량 vs 계약당손익이 **무관**(rho=+0.004, p=0.96)이고, 유일하게
유의한 관계가 진입수량 vs **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5,
rho=+0.318 p=0.015)임을 밝혔다. 그래서 지금 계측 채널은 전부 "손실이 의도한
손절폭을 **초과**했는가" 쪽만 본다.

**그 반대편에는 채널이 없다 — 손절이 너무 타이트해 노이즈에 걸리는 경우다.**

2026-08-14 CASE-04 가 정확히 그 사례다:
    14:40:00 LONG 진입 1096.46 · 손절 1094.40 (의도 손절폭 1.851pt)
    14:41 저점 1093.88 — 손절가를 **0.52pt 오버슛**
    14:41:43 손절 체결 1094.20
      ↓ 이후
    14:51 1096.38 → 14:54 **1098.60** — 진입가를 넘어 +2.14pt
그날 1분 레인지 최대가 1.84pt 였으니 손절폭 1.851pt 는 노이즈 폭과 거의 같았다.

**"손절은 손절이고, 되돌아온 것은 사후에만 안다."** 이 스크립트는 그 사후 사실을
기록만 한다 — 집행에는 아무 영향도 주지 않는다.

════════════════════════════════════════════════════════════════════════════
대조군(control) — **이것이 없으면 회복률은 해석 불가다** [470차 후속3 추가]
════════════════════════════════════════════════════════════════════════════
최초 실행에서 15분 회복률 **80.2%** 가 나왔다. 큰 숫자로 보이지만 **그 자체로는
아무 뜻도 없다** — KOSPI200 선물 1분봉은 되돌림이 잦아, 손절과 무관하게 아무 시각을
잡아도 15분 안에 특정 가격을 다시 스칠 확률이 원래 높을 수 있기 때문이다.
371차 PSI(계측 결함)·372차 임계 재보정(이상치 2건의 착시)이 "숫자는 커 보였지만
아니었다"로 끝난 전례가 둘 있다.

그래서 **매칭 대조군**을 둔다. 무작위 시각을 그냥 뽑으면 안 된다 — 손절 건은
진입가까지 **특정 거리 D**만큼 되돌아와야 회복인데, 대조군의 거리가 다르면 비교가
성립하지 않는다(D 가 작으면 회복은 당연히 쉽다).

    처치(treatment): 손절 체결 시각 T, 체결가 P_x, 진입가 P_e.
                     D = |P_e − P_x| (역행 거리 = 대략 손절폭)
                     → T 이후 N분 안에 가격이 D 만큼 **되돌아오는가**

    대조(control)  : **같은 거래일**의 무작위 분봉 t (T 로부터 ±N분은 제외),
                     그 시점 종가 C_t 를 기준으로 **같은 방향 · 같은 거리 D**
                     → t 이후 N분 안에 가격이 D 만큼 움직이는가

이 설계가 통제하는 것: 거리 D · 방향 · 거래일(변동성 체제) · 창 길이 N.
**통제하지 않는 것(=측정하려는 효과): "그 시점이 역행 직후였다"는 사실 하나.**
따라서 손절이 국소 극단(shakeout)에 몰려 있다면 처치 > 대조가 나와야 한다.

판정은 **일자단위 부호검정**이 주판정이다(313차 ① — 신호단위 n 은 독립관측치가 아니다).
신호단위 차이는 참고로만 병기하고, 드롭-워스트(313차 ③)도 함께 낸다.

════════════════════════════════════════════════════════════════════════════
설계 원칙
════════════════════════════════════════════════════════════════════════════
① **읽기 전용.** 모든 DB 를 `mode=ro` URI 로만 연다. 라이브 배선이 아니다.
② **포지션 단위.** `trades` 한 행은 **청산 레그**다(417차 단위 혼동).
③ **진짜 손절만.** `tp1_reached=1` 하드스톱은 TP1 도달 후 **보호 트레일 이익 청산**이다
   (465차 P4 / 468차 G-3). 추가로 **포지션 합손익이 음수**인 것만 센다(아래 주 참조).
④ **재현 가능.** 대조군 표본은 `--seed` 고정 난수다. 같은 인자면 같은 결과가 나온다.
⑤ **판정하되 임계는 사전등록 없이 만들지 않는다.** p-value 와 효과크기를 내되
   "몇 %p 이상이면 조치"라는 합격선은 **여기서 만들지 않는다**(313차 ④).

사용:
    python scripts/stop_overshoot_shadow.py --days 20
    python scripts/stop_overshoot_shadow.py --days 20 --controls 50
    python scripts/stop_overshoot_shadow.py --json out.json --out report.md
"""
from __future__ import print_function

import argparse
import bisect
import datetime as dt
import io
import json
import os
import random
import sqlite3
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRADES_DB = os.path.join(ROOT, "data", "db", "trades.db")
RAW_DB = os.path.join(ROOT, "data", "db", "raw_data.db")

WINDOWS = (5, 10, 15)          # 청산 후 관측 분(minute)
PRIMARY_WINDOW = 15            # 주판정 창
DEFAULT_CONTROLS = 20          # 손절 1건당 대조 표본 수
DEFAULT_SEED = 470             # 재현용 고정 시드 (470차)

# 대조 표본을 뽑을 시간대 — 매분 루프가 도는 구간으로 제한한다.
CONTROL_TIME_LO = "09:00:00"
CONTROL_TIME_HI = "15:10:00"

# 진짜 손절로 볼 exit_reason 조각. `하드스톱`은 tp1_reached 로 한 번 더 거른다.
_STOP_TOKENS = ("하드스톱", "손절")
# 손절 계열이라도 이것들은 제외 — 손절이 아니다.
_NOT_STOP = ("TP1", "TP2", "TP3", "강제청산", "시간마감", "신호소멸")


def _ro(path):
    if not os.path.exists(path):
        raise SystemExit("[stop_overshoot] DB 없음: %s" % path)
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)


def _is_real_stop(reason, tp1_reached):
    """청산 사유가 손절 계열인가 — 보호 트레일 이익 청산과 가른다."""
    r = str(reason or "")
    if any(x in r for x in _NOT_STOP):
        return False
    if not any(x in r for x in _STOP_TOKENS):
        return False
    # 465차 P4: tp1_reached=1 인 하드스톱은 **이익 청산**이다.
    if tp1_reached:
        return False
    return True


# ────────────────────────────────────────────────────────────── 데이터 로드
def load_positions(days=None):
    """청산 레그를 진입 시각으로 묶어 포지션 단위로 되돌린다."""
    con = _ro(TRADES_DB)
    rows = list(con.execute(
        "select entry_ts, exit_ts, direction, entry_price, exit_price, quantity,"
        "       pnl_pts, exit_reason, tp1_reached, grade, entry_horizon, entry_source"
        "  from trades where entry_ts is not null and exit_ts is not null"
        " order by entry_ts, exit_ts"))
    con.close()

    pos = OrderedDict()
    for r in rows:
        (ets, xts, d, ep, xp, q, pt, reason, tp1, grade, hz, src) = r
        p = pos.setdefault(ets, {
            "entry_ts": ets, "direction": d, "entry_price": ep,
            "grade": grade, "horizon": hz, "source": src, "legs": [],
        })
        p["legs"].append({
            "exit_ts": xts, "exit_price": xp, "qty": q, "pnl_pts": pt or 0.0,
            "reason": reason, "tp1_reached": tp1,
        })

    out = []
    for p in pos.values():
        last = p["legs"][-1]                      # 최종 청산 레그
        p["exit_ts"] = last["exit_ts"]
        p["exit_price"] = last["exit_price"]
        p["exit_reason"] = last["reason"]
        p["tp1_reached"] = last["tp1_reached"]
        p["pnl_pts"] = sum(l["pnl_pts"] for l in p["legs"])
        p["n_legs"] = len(p["legs"])
        out.append(p)

    if days:
        dates = sorted({x["entry_ts"][:10] for x in out})[-int(days):]
        out = [x for x in out if x["entry_ts"][:10] in dates]
    return out


def load_bars_by_day():
    """분봉 OHLC 를 거래일별 인덱스로 적재한다.

    종전에는 전체 리스트를 매 창마다 선형 스캔했다. 대조군이 붙으면 호출이
    수천 배로 늘어 그 구조로는 못 돌린다 — 날짜별로 나눈 뒤 bisect 로 자른다.
    """
    con = _ro(RAW_DB)
    rows = con.execute(
        "select ts, high, low, close from raw_candles"
        " where high is not null and low is not null and close is not null"
        " order by ts")
    by_day = {}
    for ts, hi, lo, cl in rows:
        by_day.setdefault(ts[:10], []).append((ts[:19], float(hi), float(lo), float(cl)))
    con.close()
    for d in by_day:
        by_day[d].sort(key=lambda b: b[0])
    return by_day


# ────────────────────────────────────────────────────────────── 창 계산
def _add_minutes(ts19, minutes):
    return (dt.datetime.strptime(ts19, "%Y-%m-%d %H:%M:%S")
            + dt.timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")


def _slice_after(day_bars, start_ts19, minutes):
    """`start_ts19` **초과** ~ +minutes 이내 분봉. 없으면 빈 리스트."""
    keys = [b[0] for b in day_bars]
    i = bisect.bisect_right(keys, start_ts19)
    end = _add_minutes(start_ts19, minutes)
    j = bisect.bisect_right(keys, end)
    return day_bars[i:j]


def _favorable_excursion(seg, is_long, ref_price):
    """창 안에서 원하는 방향의 최대 도달치와 `ref_price` 도달 여부.

    반환: (reached: bool, mfe_pt: float)  — mfe 는 ref 기준 초과분(음수면 미달)
    """
    if not seg:
        return None, None
    if is_long:
        best = max(b[1] for b in seg)          # high
        return bool(best >= ref_price), round(best - ref_price, 4)
    best = min(b[2] for b in seg)              # low
    return bool(best <= ref_price), round(ref_price - best, 4)


class DayIndex(object):
    """한 거래일의 분봉 + 대조 표본 후보 인덱스."""

    def __init__(self, bars):
        self.bars = bars
        self.keys = [b[0] for b in bars]

    def slice_after(self, ts19, minutes):
        i = bisect.bisect_right(self.keys, ts19)
        j = bisect.bisect_right(self.keys, _add_minutes(ts19, minutes))
        return self.bars[i:j]

    def control_candidates(self, minutes):
        """N분 창이 온전히 남아 있는 장중 분봉 인덱스 목록."""
        out = []
        for i, b in enumerate(self.bars):
            hhmmss = b[0][11:19]
            if not (CONTROL_TIME_LO <= hhmmss <= CONTROL_TIME_HI):
                continue
            # 창이 온전한가 — 마지막 분봉이 t+minutes 에 도달하는가
            if self.keys[-1] < _add_minutes(b[0], minutes):
                continue
            out.append(i)
        return out


# ────────────────────────────────────────────────────────────── 통계
def _binom_two_sided_p(k, n, p=0.5):
    """정확 이항검정 양측 p-value. scipy 없이 정수 연산으로 계산한다.

    (py37_32 런타임에는 scipy 1.5.4 가 있으나, 이 스크립트는 표준 라이브러리만으로
     어느 환경에서든 돌게 둔다 — 점검 도구가 환경에 묶이면 안 된다.)
    """
    if n <= 0:
        return 1.0

    def _comb(nn, kk):
        if kk < 0 or kk > nn:
            return 0
        kk = min(kk, nn - kk)
        num, den = 1, 1
        for i in range(kk):
            num *= (nn - i)
            den *= (i + 1)
        return num // den

    def _pmf(i):
        return _comb(n, i) * (p ** i) * ((1.0 - p) ** (n - i))

    obs = _pmf(k)
    tol = obs * (1 + 1e-9)
    return min(1.0, sum(_pmf(i) for i in range(n + 1) if _pmf(i) <= tol))


def _rate(num, den):
    return (float(num) / den) if den else None


# ────────────────────────────────────────────────────────────── 본 분석
def analyze(days=None, n_controls=DEFAULT_CONTROLS, seed=DEFAULT_SEED,
            strict_loss=True):
    positions = load_positions(days=days)
    by_day = load_bars_by_day()
    idx = {d: DayIndex(b) for d, b in by_day.items()}

    # ③ 진짜 손절 — 사유 필터 + (기본) 포지션 합손익 음수
    #
    # [470차 후속3] `strict_loss` 를 기본 True 로 켠다. **`tp1_reached` 필터가 과거
    # 구간에서 작동하지 않기 때문이다.**
    #
    #   실측(최근 20거래일 손절 라벨 131건): `tp1_reached` 값 분포 = {None: 129, 0: 2}
    #   → 이 컬럼은 **2026-08-13부터 적재**됐고 그 이전 행은 전부 NULL 이다.
    #     `if tp1_reached: return False` 는 NULL 에 대해 아무 일도 하지 않으므로,
    #     **보호 트레일 이익 청산이 그대로 "진짜 손절"로 통과했다.**
    #   실제로 131건 중 **79건이 포지션 합손익 ≥ 0**(대부분 1레그, `하드스톱(틱)` 라벨)이었다.
    #   최초 실행의 회복률 80.2% 는 그 79건을 포함한 값이다.
    #
    # 합손익 음수 조건은 그 결측을 대신하는 **직접 판정**이다 — 손해를 본 건만 센다.
    # ⚠ 정의를 조용히 바꾸지 않는다 — 리포트가 두 모집단 수를 모두 표시하고,
    #   `--include-profit-stops` 로 최초 실행과 같은 모집단을 재현할 수 있다.
    loose = [p for p in positions if _is_real_stop(p["exit_reason"], p["tp1_reached"])]
    stops = [p for p in loose if p["pnl_pts"] < 0] if strict_loss else loose

    rng = random.Random(seed)
    recs = []
    skipped_no_window = 0

    for p in stops:
        day = p["exit_ts"][:10]
        di = idx.get(day)
        if di is None:
            continue
        is_long = str(p["direction"]).upper() == "LONG"
        ep = float(p["entry_price"] or 0.0)
        xp = float(p["exit_price"] or 0.0)
        dist = abs(ep - xp)                      # 되돌아와야 하는 거리 D
        if dist <= 0:
            continue

        rec = {
            "entry_ts": p["entry_ts"], "exit_ts": p["exit_ts"], "day": day,
            "direction": p["direction"], "grade": p["grade"], "horizon": p["horizon"],
            "entry_price": ep, "exit_price": xp, "dist_pt": round(dist, 3),
            "pnl_pts": round(p["pnl_pts"], 3), "exit_reason": p["exit_reason"],
            "n_legs": p["n_legs"],
        }

        for w in WINDOWS:
            seg = di.slice_after(p["exit_ts"][:19], w)
            reached, mfe = _favorable_excursion(seg, is_long, ep)
            rec["recovered_%dm" % w] = reached
            rec["mfe_%dm" % w] = mfe

            # ── 매칭 대조군 ──────────────────────────────────────────
            cands = di.control_candidates(w)
            # 처치 시점 ±w분은 제외 — 그 구간은 처치 창 자체라 결과가 강하게 얽힌다.
            lo_ex = _add_minutes(p["exit_ts"][:19], -w)
            hi_ex = _add_minutes(p["exit_ts"][:19], w)
            cands = [i for i in cands if not (lo_ex <= di.keys[i] <= hi_ex)]
            if not cands:
                rec["control_rate_%dm" % w] = None
                rec["control_mfe_%dm" % w] = None
                if w == PRIMARY_WINDOW:
                    skipped_no_window += 1
                continue

            picks = ([rng.choice(cands) for _ in range(n_controls)]
                     if len(cands) > n_controls
                     else cands)
            hits, mfes = 0, []
            for i in picks:
                c_close = di.bars[i][3]
                # **같은 방향 · 같은 거리 D** 를 요구한다 — 이것이 매칭의 핵심이다.
                c_ref = c_close + dist if is_long else c_close - dist
                c_seg = di.slice_after(di.keys[i], w)
                c_reached, c_mfe = _favorable_excursion(c_seg, is_long, c_ref)
                if c_reached:
                    hits += 1
                if c_mfe is not None:
                    mfes.append(c_mfe)
            rec["control_n_%dm" % w] = len(picks)
            rec["control_rate_%dm" % w] = _rate(hits, len(picks))
            rec["control_mfe_%dm" % w] = (round(sum(mfes) / len(mfes), 4) if mfes else None)

        recs.append(rec)

    return {
        "records": recs,
        "n_positions": len(positions),
        "n_loose": len(loose),
        "n_strict": len(stops),
        "strict_loss": strict_loss,
        "n_controls": n_controls,
        "seed": seed,
        "skipped_no_window": skipped_no_window,
    }


def day_level(recs, w=PRIMARY_WINDOW):
    """일자단위 집계 — 처치 회복률 vs 대조 회복률 (313차 ① 주판정 단위)."""
    days = OrderedDict()
    for r in recs:
        if r.get("recovered_%dm" % w) is None or r.get("control_rate_%dm" % w) is None:
            continue
        d = days.setdefault(r["day"], {"n": 0, "t_hit": 0, "c_sum": 0.0})
        d["n"] += 1
        d["t_hit"] += 1 if r["recovered_%dm" % w] else 0
        d["c_sum"] += r["control_rate_%dm" % w]
    out = []
    for day, d in days.items():
        out.append({
            "day": day, "n": d["n"],
            "t_rate": d["t_hit"] / float(d["n"]),
            "c_rate": d["c_sum"] / float(d["n"]),
            "delta": d["t_hit"] / float(d["n"]) - d["c_sum"] / float(d["n"]),
        })
    return out


def sign_test(day_rows):
    """일자단위 부호검정 — 처치 > 대조인 날이 우연 이상으로 많은가."""
    pos = sum(1 for r in day_rows if r["delta"] > 0)
    neg = sum(1 for r in day_rows if r["delta"] < 0)
    ties = sum(1 for r in day_rows if r["delta"] == 0)
    n = pos + neg
    return {"pos": pos, "neg": neg, "ties": ties, "n": n,
            "p": _binom_two_sided_p(pos, n) if n else 1.0}


# ────────────────────────────────────────────────────────────── 리포트
def _pct(x):
    return "—" if x is None else "%.1f%%" % (100.0 * x)


def report(res, days=None):
    recs = res["records"]
    L = []
    A = L.append
    A("# 손절 오버슛(shakeout) 섀도 — [MW0602 470차 D2' + 후속3 대조군]")
    A("")
    A("- 대상: 포지션 **%d건** 중 손절 계열 %d건 → **진짜 손절(합손익 음수) %d건**%s" % (
        res["n_positions"], res["n_loose"], res["n_strict"],
        (" (최근 %s거래일)" % days) if days else " (전 기간)"))
    A("  - `tp1_reached=1` 하드스톱(보호 트레일 **이익** 청산)은 제외 — 465차 P4 / 468차 G-3")
    A("  - 추가로 **포지션 합손익이 음수**인 것만 센다. 최초 실행(80.2%)에는 트레일이")
    A("    이익 구간까지 올라간 뒤 걸린 건이 %d건 섞여 있었다." % (res["n_loose"] - res["n_strict"]))
    A("- 대조 표본: 손절 1건당 **%d개**, 시드 `%d` (재현 가능)" % (res["n_controls"], res["seed"]))
    A("")
    if not recs:
        A("_진짜 손절 표본이 없다._")
        return "\n".join(L)

    A("## 대조군 설계 — 무엇과 비교하는가")
    A("")
    A("```")
    A("처치  손절 체결 시각 T, 체결가 P_x, 진입가 P_e,  D = |P_e − P_x|")
    A("      → T 이후 N분 안에 가격이 D 만큼 되돌아오는가")
    A("")
    A("대조  같은 거래일의 무작위 분봉 t (T ± N분 제외), 그 시점 종가 C_t")
    A("      → t 이후 N분 안에 **같은 방향으로 같은 거리 D** 만큼 움직이는가")
    A("```")
    A("")
    A("통제한 것: **거리 D · 방향 · 거래일 · 창 길이**.")
    A("통제하지 않은 것 = **측정 대상**: *\"그 시점이 역행 직후였다\"* 는 사실 하나.")
    A("→ 손절이 국소 극단(shakeout)에 몰려 있다면 **처치 > 대조**가 나와야 한다.")
    A("")

    A("## 1. 처치 vs 대조 (신호단위 — 참고용)")
    A("")
    A("| 창 | 표본 | 처치 회복률 | 대조 회복률 | **차이** |")
    A("|---|---|---|---|---|")
    for w in WINDOWS:
        vals = [r for r in recs
                if r.get("recovered_%dm" % w) is not None
                and r.get("control_rate_%dm" % w) is not None]
        if not vals:
            A("| %d분 | 0 | — | — | — |" % w)
            continue
        t = sum(1 for r in vals if r["recovered_%dm" % w]) / float(len(vals))
        c = sum(r["control_rate_%dm" % w] for r in vals) / float(len(vals))
        A("| %d분 | %d | %s | %s | **%+.1f%%p** |" % (
            w, len(vals), _pct(t), _pct(c), 100.0 * (t - c)))
    A("")
    A("> ⚠ 신호단위 n 은 **독립관측치가 아니다**(313차 ①). 같은 날 손절은 같은 장세를")
    A("> 공유한다. 아래 **일자단위**가 주판정이다.")
    A("")

    rows = day_level(recs, PRIMARY_WINDOW)
    st = sign_test(rows)
    A("## 2. 일자단위 부호검정 — **주판정** (%d분 창)" % PRIMARY_WINDOW)
    A("")
    A("| 날짜 | 손절 | 처치 | 대조 | 차이 |")
    A("|---|---|---|---|---|")
    for r in rows:
        A("| %s | %d | %s | %s | %+.1f%%p |" % (
            r["day"], r["n"], _pct(r["t_rate"]), _pct(r["c_rate"]), 100.0 * r["delta"]))
    A("")
    A("**처치 우세 %d일 / 대조 우세 %d일 / 동률 %d일 · 부호검정 p = %.4f**" % (
        st["pos"], st["neg"], st["ties"], st["p"]))
    A("")
    if rows:
        mean_delta = sum(r["delta"] for r in rows) / float(len(rows))
        A("일자단위 평균 차이 **%+.1f%%p** (관측 %d일)" % (100.0 * mean_delta, len(rows)))
        A("")
        # 313차 ③ — 드롭-워스트
        if len(rows) > 2:
            worst = max(rows, key=lambda r: abs(r["delta"]))
            rest = [r for r in rows if r is not worst]
            md2 = sum(r["delta"] for r in rest) / float(len(rest))
            st2 = sign_test(rest)
            A("**드롭-워스트(313차 ③)** — 영향 최대일 `%s`(%+.1f%%p) 제외 시 "
              "평균 **%+.1f%%p**, p = %.4f · 부호 %s" % (
                  worst["day"], 100.0 * worst["delta"], 100.0 * md2, st2["p"],
                  "유지" if (md2 > 0) == (mean_delta > 0) else "**반전**"))
            A("")

    A("## 3. 해석")
    A("")
    if not rows:
        A("_일자단위 표본이 없다._")
    elif st["n"] < 5:
        A("- **판정 보류** — 유효 관측일이 %d일뿐이다. 표본을 더 볼 것." % st["n"])
    elif st["p"] < 0.05 and st["pos"] > st["neg"]:
        A("- 처치 회복률이 대조보다 **유의하게 높다**(p=%.4f). 손절 지점이 국소 극단에" % st["p"])
        A("  몰려 있다는 방향의 증거다 — 다만 **이것은 '손절폭을 넓혀라'가 아니다.**")
        A("  손절의 목적은 꼬리 자르기이고, 회복하지 않은 나머지가 얼마나 큰 손실을")
        A("  막았는지는 이 표에 없다. **주간회의 안건으로만 올린다.**")
    elif st["p"] < 0.05 and st["neg"] > st["pos"]:
        A("- 처치 회복률이 대조보다 **유의하게 낮다**(p=%.4f). 손절 지점은 오히려" % st["p"])
        A("  되돌림이 덜한 자리였다는 뜻 — **손절폭 확대 논의의 근거가 되지 못한다.**")
    else:
        A("- **차이가 유의하지 않다**(p=%.4f)." % st["p"])
        A("  즉 최초 실행의 회복률 80.2%는 **손절 지점의 특성이 아니라 이 시장의 기본 성질**로")
        A("  대부분 설명된다 — 아무 시각을 잡아도 비슷한 비율로 되돌아온다.")
        A("  **\"손절이 타이트하다\"는 결론의 근거로 쓸 수 없다.**")
    A("")
    A("> ⚠ **합격선을 여기서 만들지 않는다**(313차 ④ 사전등록 — 관측 후 기준 수립 금지).")
    A("> 이 스크립트는 p-value 와 효과크기를 낼 뿐, \"몇 %p 이상이면 조치\"를 정의하지 않는다.")
    A("> 손절폭 재설계는 주간회의 결정 사항이다.")
    A("")
    A("> ⚠ 회복은 **사후에만 안다.** MFE 는 창 안의 *가장 좋았던 순간*이라 실전에서")
    A("> 그 지점을 집을 수 있었다는 뜻이 아니다.")
    A("")

    A("## 4. 개별 손절 (최근 12건)")
    A("")
    A("| 진입 | 방향 | 등급 | 손익(pt) | D(pt) | 5분 | 10분 | 15분 | 대조15 |")
    A("|---|---|---|---|---|---|---|---|---|")
    for r in recs[-12:]:
        def _m(w):
            v = r.get("recovered_%dm" % w)
            return "—" if v is None else ("✅" if v else "·")
        A("| %s | %s | %s | %+.2f | %.2f | %s | %s | %s | %s |" % (
            r["entry_ts"][5:16], r["direction"], r["grade"] or "?", r["pnl_pts"],
            r["dist_pt"], _m(5), _m(10), _m(15), _pct(r.get("control_rate_15m"))))
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description="손절 오버슛(shakeout) 섀도 계측 — 읽기 전용")
    ap.add_argument("--days", type=int, default=None, help="최근 N거래일만")
    ap.add_argument("--controls", type=int, default=DEFAULT_CONTROLS,
                    help="손절 1건당 대조 표본 수 (기본 %d)" % DEFAULT_CONTROLS)
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED,
                    help="대조 표본 난수 시드 (기본 %d — 재현용)" % DEFAULT_SEED)
    ap.add_argument("--include-profit-stops", action="store_true",
                    help="합손익이 양수인 손절 라벨 건도 포함 (최초 실행과 같은 모집단)")
    ap.add_argument("--json", default=None, help="레코드를 JSON으로 저장")
    ap.add_argument("--out", default=None, help="리포트를 md 파일로 저장 (기본 stdout)")
    args = ap.parse_args(argv)

    res = analyze(days=args.days, n_controls=args.controls, seed=args.seed,
                  strict_loss=not args.include_profit_stops)
    text = report(res, days=args.days)

    if args.json:
        with io.open(args.json, "w", encoding="utf-8") as f:
            f.write(json.dumps(res, ensure_ascii=False, indent=2))
        sys.stderr.write("[stop_overshoot] JSON 저장: %s\n" % args.json)
    if args.out:
        with io.open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        sys.stderr.write("[stop_overshoot] 저장: %s\n" % args.out)
        print(args.out)
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

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

[25-B] TP2 거리 축 (MW0601 432차 추가)
--------------------------------------
같은 훅 모집단·같은 `_simulate()`를 쓰되 **보호 offset을 현행(ATR×0.25)으로 고정하고
TP2만** 바꾸는 평행 축이다. 계기는 0805 일일점검 — 진입 19건 전부에서 TP2 거리 ÷ 손절
거리 = 1.00이었고(ATR_STOP_MULT = ATR_TP2_MULT = 1.5), qty=1은 TP1에서 돈이 들어오지
않으므로 실질 페이오프가 "손절폭만큼 완주해야 손절 1건을 상쇄"하는 구조가 된다.

왜 [23] tp1_geometry_shadow가 아니라 여기인가: [23]의 시뮬레이터는 TP1 도달 시
전량청산으로 종료해 TP2가 아예 등장하지 않는다. 더 중요한 것은 **조건부 추정이 정확히
valid**하다는 점 — TP2를 바꿔도 stop·TP1은 불변이므로 "TP1 도달 사건 집합"이 전 변형에서
동일하고, 따라서 TP1 도달 건만 보는 것은 선택편향이 아니라 교란이 제거된 설계다.

판정은 `tp2_*` 키로 **본채널과 완전히 분리**돼 계산된다(본채널 합격선 무변경, §9-4).
사전등록 기준·판정보조 3종·한계는 config/settings.py의 [25-B] 주석에 관측 전 고정.

[MW0601 443차] 정본 재생기 이관
--------------------------------
441차 [47] 엔진 커버리지 가드가 이 채널을 SUSPENDED로 잡아 두었다 — 자체
`_simulate()`가 **TP2에서 종료**하고 트레일링을 모델링하지 않아, 게이트의 PASS가
이 채널의 계측을 검증하지 못했기 때문이다. 443차가 `exit_replay`로 이관했다.

**무엇이 달라지나** — v1은 *보호전환 시점부터* 스톱/TP2만 봤다. v2는 *진입부터*
라이브 청산 사다리를 그대로 돌리고 offset을 `lock_offset_pts`로 주입한다. 따라서
v1이 못 보던 **4단계 트레일링이 보호스톱을 더 끌어올리는 효과**가 반영된다.
조건부 타당성은 그대로다 — offset은 TP1 도달 여부에 영향을 주지 않으므로 arm
사건 집합이 전 변형에서 동일하다(§25-B 주석의 논리와 같다).

**결과: 판정 방향은 유지되고 크기가 바뀌었다**([3-B]가 뒤집힌 것과 대조적).
`atr_lock_0.75` Δ현행 +6.86 → **+12.62pt**로 오히려 강해졌고, `breakeven`은
−10.22 → **−0.08pt**로 사실상 현행과 동률이 됐다(트레일링이 초기 lock의 차이를
흡수한다 — v1에는 없던 효과). **[25-B]는 최선 변형이 바뀌었다**: `tp2_2.00`
(v1 최선) → **`tp2_1.25`**(v2 최선, +44.06 vs 현행 +37.95).
⚠ **이관 전 수치를 인용하지 말 것.** v1은 `engine="v1"`로 재현 가능하다.

**v2 전용 제외 2종**(v1에는 없던 개념):
  - 원 진입수량 ≠ 1 — 실측 36건 중 **2건**. tier1 축소/TP1 부분청산으로 잔여
    1계약이 arm된 케이스인데, 정본 재생기는 `stage==1 and qty==1`로 **원 진입
    수량**을 보므로 같은 상황을 만들지 못한다(부분청산으로 모델링된다).
  - 재생기 arm 미도달 — 실측 **1건**. 라이브는 틱으로 TP1을 쳤는데 봉 기준
    재생에서는 못 친 경우. 그 훅은 전 변형이 동일해져 delta를 희석하므로 제외한다.

한계 (반드시 함께 읽을 것)
--------------------------
- 1분봉 고저가 기준이라 봉 내 도달 순서를 알 수 없다. 보호스톱·TP2가 같은 봉에서
  모두 닿으면 보수적으로 **스톱을 먼저** 적용한다(캠페인 다른 채널과 동일 관례).
- (v1 한정) TP3·4단계 트레일링을 모델링하지 않고 TP2/스톱/15:10만 본다.
  **v2에서는 해소됐다** — 443차 이관 참조.
- ATR은 저장된 offset에서 역산한다(offset = ATR × 0.25). 현행이 atr_profit이 아닌
  행(breakeven 등)은 ATR 역산이 불가능해 제외된다.
- **[MW0602 432차] 체결가능성 클램프** — offset이 보호전환 시점의 실제 유리이동을
  넘으면 그 시점 가격으로 자른다. 이 클램프가 없던 시기(404차 후속3 ~ 431차)의
  `atr_lock_0.50/0.75`·`bar_range` 수치는 **시장이 제시한 적 없는 가격에 체결된
  것으로 계상**돼 부풀려져 있었다. 그 수치를 인용하지 말 것:

      atr_lock_0.75  Δ현행 +18.75pt → 클램프 후 **+8.04pt** (허수 기여 57%)
      bar_range      Δ현행  +8.50pt → 클램프 후   +4.96pt (42%)
      atr_lock_0.50  Δ현행  +3.81pt → 클램프 후   +2.23pt (42%)
      current/breakeven/breakeven_plus — 클램프 0건, 영향 없음

  변형별 클램프 발동 건수는 `n_clamped`로 노출되며 CLI·리포트가 함께 찍는다.
  클램프 비율이 높다 = 그 변형이 기하학적으로 무리한 요구를 했다는 뜻이다.

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
    # [432차] 라이브와 같은 상수를 쓴다 — 예전에는 여기 리터럴 사본이 있어
    # 라이브가 바뀌면 `current` 기준선이 조용히 어긋날 수 있었다.
    TP1_PROTECT_ATR_LOCK_MULT, TP1_PROTECT_PLUS_ALPHA_PTS,
    # [440차] 호라이즌 비례 lock(§25-C) — TP1 거리를 라이브와 같은 산식으로 구한다.
    ATR_TP1_MULT, ATR_HORIZON_TP1_MULT,
    HURST_REGIME_ATR_MULT, HURST_REGIME_ATR_MULT_ENABLED,
)
from config.constants import MINI_FUTURES_PT_VALUE  # noqa: E402

_CR = VALIDATION_CAMPAIGN.get("tp1_protect_offset_shadow", {})
_LOCK_MULT_CURRENT = TP1_PROTECT_ATR_LOCK_MULT   # 라이브 정본(config/settings.py)
_BAR_RANGE_LOOKBACK = 3            # bar_range 변형: 직전 N봉
_MAX_MIN = 360                     # 재생 상한(분) — 15:10 컷이 먼저 걸리는 게 정상
# [MW0602 432차] 체결가능성 클램프. 기본 True — 끄면 결함 상태(체결 불가 가격을
# 체결로 계상)가 재현된다. 과거 수치 재현 목적으로만 False로 둘 것.
_CLAMP_ON = bool(_CR.get("feasibility_clamp", True))
# [MW0601 443차] 재생기 엔진 — [23-B]/[3-B]와 **같은 스위치를 공유**한다.
# 근거·되돌리는 법은 config/settings.py sim_fidelity_gate["engine"] 주석 참조.
_ENGINE = str((VALIDATION_CAMPAIGN.get("sim_fidelity_gate", {}) or {})
              .get("engine", "v1")).lower()


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


def _load_hz(since: str):
    """[MW0601 440차 / 25-C] entry_ts → (entry_horizon, hurst_bucket).

    `synthetic_partial_exits`에는 호라이즌 컬럼이 없다. 비례 lock 변형이 TP1 거리를
    알아야 하므로 `trades`에서 조인해 온다. 조인 실패는 그 변형에서만 제외된다.
    """
    with _conn(TRADES_DB) as c:
        return {r["entry_ts"]: (r["entry_horizon"], r["hurst_bucket"])
                for r in c.execute(
                    "SELECT entry_ts, entry_horizon, hurst_bucket FROM trades "
                    "WHERE entry_ts >= ? GROUP BY entry_ts", (since,))}


def _load_candles(since: str):
    with _conn(RAW_DATA_DB) as c:
        rows = c.execute(
            "SELECT ts, high, low FROM raw_candles WHERE ts >= ? ORDER BY ts",
            (since,)).fetchall()
    return [(r["ts"], float(r["high"]), float(r["low"])) for r in rows]


def _tp2_mult_for(name: str) -> float:
    """[MW0601 432차 / 25-B] TP2 거리 변형 → ATR 배수.

    `current`는 라이브 상수 ATR_TP2_MULT(1.5)를 그대로 쓴다 — 하드코딩하지 않는 이유는
    라이브 값이 바뀌면 이 채널의 기준선도 함께 따라가야 delta_vs_current가 의미를
    유지하기 때문이다(offset 축의 `_offset_for("current")`가 _LOCK_MULT_CURRENT를
    쓰는 것과 같은 관례).
    """
    if name == "current":
        return float(ATR_TP2_MULT)
    if name.startswith("tp2_"):
        try:
            return float(name[4:])
        except ValueError:
            pass
    raise ValueError("unknown tp2 variant: %s" % name)


def _tp1_dist(atr: float, horizon, hurst_bucket) -> float:
    """[MW0601 440차] 그 진입의 **TP1 거리(pt)** — 라이브 `_recalculate_levels()` 산식.

    호라이즌 비례 lock(`lock_prop_*`)의 기준선이다. hurst 레짐 배수까지 곱해야
    라이브 TP1과 같은 값이 된다.
    """
    base = ATR_HORIZON_TP1_MULT.get(horizon, ATR_TP1_MULT)
    m = (HURST_REGIME_ATR_MULT.get(hurst_bucket or "", {})
         if HURST_REGIME_ATR_MULT_ENABLED else {})
    return float(atr) * float(base) * float(m.get("tp1", 1.0))


def _offset_for(name: str, atr: float, bar_rng: float, tp1_dist: float = None) -> float:
    """변형 이름 → 보호전환 offset(pt).

    `lock_prop_*`는 TP1 거리에 비례한다 — 그 변형만 `tp1_dist`를 요구하며,
    구할 수 없으면 ValueError를 던져 호출측이 그 행을 **비례 변형에서만** 제외한다
    (기존 변형의 모집단은 무변경 — settings §25-C 주석 참조).
    """
    if name == "current":
        return atr * _LOCK_MULT_CURRENT
    if name == "breakeven":
        return 0.0
    if name == "breakeven_plus":
        return TP1_PROTECT_PLUS_ALPHA_PTS
    if name == "atr_lock_0.50":
        return atr * 0.50
    if name == "atr_lock_0.75":
        return atr * 0.75
    if name == "bar_range":
        return max(atr * _LOCK_MULT_CURRENT, bar_rng * 0.5)
    if name.startswith("lock_prop_"):
        if not tp1_dist or tp1_dist <= 0:
            raise ValueError("lock_prop needs tp1_dist: %s" % name)
        return float(tp1_dist) * float(name[len("lock_prop_"):])
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


def _load_qty(since: str):
    """[MW0601 443차] entry_ts → 진입 계약수. v2 재생은 진입부터 돌리므로 필요하다.

    ⚠ 훅 전량이 qty=1인 것은 **아니다** — 443차 실측 36건 중 2건이 qty≥2였다
    (tier1 축소/TP1 부분청산으로 **잔여 1계약**이 된 뒤 arm된 케이스). 정본
    재생기는 `stage == 1 and qty == 1`로 **원 진입수량**을 보므로 그 2건에서는
    보호전환이 아니라 부분청산을 모델링한다 — 같은 상황이 아니다.
    → v2 경로는 qty=1만 판정하고 나머지는 사유를 붙여 제외한다(`n_qty_gt1`).
    """
    with _conn(TRADES_DB) as c:
        return {r["entry_ts"]: (int(r["eq"] or 0) or int(r["lq"] or 0) or 1)
                for r in c.execute(
                    "SELECT entry_ts, MAX(COALESCE(entry_qty,0)) eq, SUM(quantity) lq "
                    "FROM trades WHERE entry_ts >= ? GROUP BY entry_ts", (since,))}


def _load_bars_map(since: str):
    """{ts: (high, low, close)} — v2 재생기 입력 형태."""
    with _conn(RAW_DATA_DB) as c:
        return {r["ts"]: (float(r["high"]), float(r["low"]), float(r["close"]))
                for r in c.execute(
                    "SELECT ts, high, low, close FROM raw_candles WHERE ts >= ?",
                    (since,))}


def compute(since: str = "2026-06-01", engine=None) -> dict:
    """[MW0601 443차] engine="v1"/"v2" — 기본은 사전등록된 현행 엔진
    (`sim_fidelity_gate["engine"]`). [23-B]/[3-B]와 같은 스위치를 공유하며
    v1 코드는 보존한다(되돌리면 이관 전 수치가 재현된다)."""
    hooks = _load_hooks(since)
    bars = _load_candles(since)
    idx = {t: i for i, (t, _, _) in enumerate(bars)}
    variants = list(_CR.get("variants", ["current"]))
    _eng = str(engine or _ENGINE).lower()
    _replay = _regime_for = None
    bars_map, qty_map = None, {}
    if _eng == "v2":
        from scripts.exit_replay import replay as _replay, regime_for as _regime_for
        bars_map = _load_bars_map(since)
        qty_map = _load_qty(since)
    res = {v: [] for v in variants}
    # [MW0601 440차 / 25-C] 훅 ts 평행 리스트 — 비례 변형이 호라이즌 미상 행을
    # 건너뛰면 변형마다 모집단이 달라진다. delta는 **짝지은 부분집합**으로 내야
    # 공정하다(summarize 참조). 기존 변형끼리는 전건 일치하므로 영향 없음.
    res_ts = {v: [] for v in variants}
    days, skipped = set(), 0

    # [MW0601 432차 / 25-B] TP2 거리 축 — offset 축과 **완전히 평행한 별도 집계**다.
    # 같은 훅 모집단·같은 _simulate()를 쓰되 offset은 현행(ATR×0.25)으로 고정하고
    # TP2만 바꾼다. res와 섞지 않는 이유는 본채널 verdict가 오염되면 안 되기 때문
    # (§9-4 — 본채널 합격선 무변경). 판정도 summarize()에서 별도 키로 낸다.
    tp2_variants = list(_CR.get("tp2_variants", []))
    res_tp2 = {v: [] for v in tp2_variants}

    # [MW0601 406차 / C] 제외 사유별 카운터 — 예전에는 전부 skipped 하나로 뭉뚱그려져
    # "왜 표본이 없는지"를 리포트가 말해줄 수 없었다.
    n_other_mode: dict = {}     # atr_profit이 아니라 판정 모집단에서 빠진 건수(모드별)
    n_backout_legacy = 0        # atr 컬럼 이전 행 — 역산 폴백을 쓴 건수
    n_excluded_override = 0     # prev_stop 오버라이드가 확인돼 제외한 건수
    # [MW0602 432차] 변형별 체결가능성 클램프 발동 건수·초과폭 — 아래 클램프 참조.
    n_clamped: dict = {v: 0 for v in variants}
    clamp_excess: dict = {v: [] for v in variants}
    # [MW0601 440차 / 25-C] 비례 변형에서만 호라이즌 미상으로 빠진 건수.
    n_no_horizon: dict = {}
    hz_map = _load_hz(since)
    # [MW0601 443차 / v2] 정본 재생기 경로에서만 생기는 제외 사유 2종.
    n_qty_gt1 = 0     # 잔여 1계약 arm 케이스 — 원 진입수량이 1이 아니라 모집단이 다르다
    n_no_arm = 0      # 재생기가 TP1 arm에 도달하지 못한 훅(반사실을 만들 수 없다)

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
        # [MW0602 432차] 보호전환 **시점에 실제로 도달했던** 유리이동. 클램프 상한.
        excursion = abs(float(h["synthetic_price"]) - ep)
        # [MW0601 440차 / 25-C] 호라이즌 비례 lock용 TP1 거리. hooks 테이블에
        # entry_horizon이 없어 trades를 entry_ts로 조인해 얻는다(_load_hz 참조).
        _hz, _hb = hz_map.get(h.get("entry_ts") or "", (None, None))
        tp1_dist = _tp1_dist(atr, _hz, _hb) if _hz else None

        # ── [MW0601 443차] 정본 재생기 경로 ─────────────────────────────────────
        # v1은 **보호전환 시점(i0)부터** 스톱/TP2만 보고 끝냈다. v2는 **진입부터**
        # 라이브 청산 사다리를 그대로 돌리고, 보호전환 offset은 `lock_offset_pts`로
        # 주입한다(이미 있던 절대-pt 오버라이드). 그래야 v1이 못 보던 것 —
        # 4단계 트레일링이 보호스톱을 **더 끌어올리는 것** — 이 반영된다.
        # 조건부 타당성은 그대로다: offset은 TP1 도달 여부에 영향을 주지 않으므로
        # arm 사건 집합이 전 변형에서 동일하다(사전등록 §25-B 주석의 논리).
        if _eng == "v2":
            _ets = h.get("entry_ts") or ""
            if int(qty_map.get(_ets, 1)) != 1:
                n_qty_gt1 += 1
                continue
            rg = _regime_for(_ets)
            staged, armed_ok = [], True
            for v in variants:
                try:
                    off_raw = _offset_for(v, atr, bar_rng, tp1_dist)
                except ValueError:
                    n_no_horizon[v] = n_no_horizon.get(v, 0) + 1
                    continue
                r = _replay(
                    bars_map, _ets, h["direction"], ep, 1, atr, _hz, _hb,
                    lock_offset_pts=off_raw,
                    # 클램프는 재생기가 arm 봉의 유리 극값을 알고 있으므로 거기서
                    # 건다(432차가 v1에서 밖에서 걸던 것을 정본 안으로 옮긴 것).
                    lock_clamp_to_bar=_CLAMP_ON,
                    tp_trigger=rg["tp_trigger"], protect_mode=rg["protect_mode"])
                if r is None:
                    armed_ok = False
                    break
                if not r.get("tp1_armed"):
                    # 재생기가 arm에 도달하지 못했다 — 이 훅은 offset 반사실을
                    # 만들 수 없다(전 변형이 동일해져 delta가 0으로 희석된다).
                    armed_ok = False
                    break
                if r.get("n_lock_clamped"):
                    n_clamped[v] += 1
                    clamp_excess[v].append(float(r.get("lock_clamp_excess_pts") or 0.0))
                staged.append((v, r["outcome"], r["pts_per_contract"] - cost))
            if not armed_ok:
                n_no_arm += 1
                continue
            for v, outcome, net in staged:
                res[v].append((outcome, net))
                res_ts[v].append(ts)
            # [25-B] TP2 축 — offset은 현행 고정, TP2만 변형.
            for v in tp2_variants:
                r = _replay(
                    bars_map, _ets, h["direction"], ep, 1, atr, _hz, _hb,
                    tp2_mult=_tp2_mult_for(v),
                    lock_offset_pts=_offset_for("current", atr, bar_rng),
                    lock_clamp_to_bar=_CLAMP_ON,
                    tp_trigger=rg["tp_trigger"], protect_mode=rg["protect_mode"])
                if r is not None:
                    res_tp2[v].append((r["outcome"], r["pts_per_contract"] - cost))
            continue

        for v in variants:
            try:
                off_raw = _offset_for(v, atr, bar_rng, tp1_dist)
            except ValueError:
                # 비례 변형인데 호라이즌을 못 구한 행 — **그 변형에서만** 제외한다.
                # 기존 변형의 모집단은 무변경(사전등록 §25-C).
                n_no_horizon[v] = n_no_horizon.get(v, 0) + 1
                continue
            # ── 체결가능성 클램프 ────────────────────────────────────────────
            # offset은 진입가에서 **이익 방향으로** 띄우는 거리다. 이것이 그 시점의
            # 실제 유리이동보다 크면 보호스톱이 당시 가격보다 더 이익 쪽에 놓인다.
            # _simulate()는 다음 봉에서 hit_stop을 무조건 True로 읽으므로,
            # **시장이 한 번도 제시하지 않은 가격에 체결된 것으로 계상**된다.
            #
            # 실측(432차, 판정모집단 49건): 시점 유리이동 중앙 0.552×ATR
            #   atr_lock_0.75 → 28건(57%)이 체결 불가, 초과폭 중앙 0.52pt
            #   bar_range     → 14건(29%),  atr_lock_0.50 → 5건(10%)
            #   current/breakeven/breakeven_plus → 0건 (영향 없음)
            # 클램프 전후 Δ현행: atr_lock_0.75 +18.75 → **+8.04pt** (57%가 허수였다)
            #
            # 상한을 excursion으로 두면 "그 순간 가격에 스톱" = 사실상 즉시 익절이며,
            # 이는 실제로 체결 가능한 최선이다.
            off = min(off_raw, excursion) if _CLAMP_ON else off_raw
            if off_raw > excursion + 1e-9:
                n_clamped[v] += 1
                clamp_excess[v].append(off_raw - excursion)
            stop = ep + sgn * off
            outcome, pts = _simulate(bars, i0, is_long, ep, stop, tp2)
            res[v].append((outcome, pts - cost))
            res_ts[v].append(ts)

        # [MW0601 432차 / 25-B] TP2 축 — 보호 offset은 현행 고정, TP2만 변형.
        # `current`는 위 offset 축의 `current`와 수치가 동일해야 정상이다
        # (같은 stop·같은 tp2·같은 시뮬). 어긋나면 배선 오류다 — summarize()가 검산한다.
        stop_cur = ep + sgn * _offset_for("current", atr, bar_rng)
        for v in tp2_variants:
            tp2_v = ep + sgn * atr * _tp2_mult_for(v)
            outcome, pts = _simulate(bars, i0, is_long, ep, stop_cur, tp2_v)
            res_tp2[v].append((outcome, pts - cost))

    return {"variants": variants, "rows": res, "rows_ts": res_ts,
            "n_hooks": len(hooks) - skipped - sum(n_other_mode.values()),
            "n_skipped": skipped, "n_days": len(days), "since": since,
            # [MW0601 406차 / C]
            "n_other_mode": n_other_mode,
            "n_backout_legacy": n_backout_legacy,
            "n_excluded_override": n_excluded_override,
            # [MW0601 432차 / 25-B]
            "tp2_variants": tp2_variants, "rows_tp2": res_tp2,
            # [MW0602 432차]
            "n_clamped": n_clamped,
            "clamp_excess": clamp_excess,
            # [MW0601 440차 / 25-C]
            "n_no_horizon": n_no_horizon,
            # [MW0601 443차 / v2 이관]
            "engine": _eng,
            "n_qty_gt1": n_qty_gt1,
            "n_no_arm": n_no_arm}


def summarize(out: dict) -> dict:
    res = out["rows"]
    base = res.get("current", [])
    base_total = sum(p for _, p in base) if base else None
    # [MW0601 440차 / 25-C] 짝지은 delta용 — 훅 ts → current의 pt.
    _rts = out.get("rows_ts") or {}
    _base_by_ts = dict(zip(_rts.get("current") or [], [p for _, p in base]))
    per = {}
    for v in out["variants"]:
        rows = res.get(v, [])
        if not rows:
            continue
        pts = [p for _, p in rows]
        # 변형이 일부 행을 건너뛰었으면(비례 lock의 호라이즌 미상) 전체합끼리
        # 빼는 것은 **모집단이 다른 두 수의 차**라 무의미하다. 공통 행만으로
        # 짝지어 계산한다. 전건 일치면 결과가 종전과 동일하다(회귀 없음).
        _delta_paired = None
        _vts = _rts.get(v) or []
        if _base_by_ts and len(_vts) == len(pts):
            _common = [(p, _base_by_ts[t]) for p, t in zip(pts, _vts)
                       if t in _base_by_ts]
            if _common:
                _delta_paired = round(sum(a - b for a, b in _common), 4)
        per[v] = {
            "n": len(pts),
            "total_pt": round(sum(pts), 4),
            "median_pt": round(sorted(pts)[len(pts) // 2], 4),
            "win_rate": round(sum(1 for p in pts if p > 0) / len(pts), 4),
            "max_loss_pt": round(min(pts), 4),
            "n_stop": sum(1 for o, _ in rows if o == "STOP"),
            "n_tp2": sum(1 for o, _ in rows if o == "TP2"),
            "n_forced": sum(1 for o, _ in rows if o == "FORCED"),
            # [MW0601 443차] 결말 분포 전체 — v2는 라벨 집합이 다르다.
            # 보호전환 뒤 되돌려 털린 건은 "STOP"이 아니라 **TP1_ARM_STOP**이라
            # 위 n_stop이 v2에서 항상 0이다(결함이 아니다). 이 분포를 함께 내지
            # 않으면 "스톱 0건"이 "한 번도 안 털렸다"로 오독된다.
            "outcomes": {o: sum(1 for oo, _ in rows if oo == o)
                         for o in sorted({oo for oo, _ in rows})},
            # 짝지은 값이 있으면 그것을 쓴다 — 전건 일치면 총합차와 같다(회귀 없음).
            "delta_vs_current": (
                _delta_paired if _delta_paired is not None
                else (round(sum(pts) - base_total, 4)
                      if base_total is not None else None)),
            "delta_paired": _delta_paired,
            "n_missing_vs_current": (len(base) - len(pts)) if base else None,
            "beats_current_n": (sum(1 for (_, p), (_, q) in zip(rows, base) if p > q)
                                if base and len(rows) == len(base) else None),
            # [MW0602 432차] 체결가능성 클램프가 걸린 건수 — 클수록 그 변형은
            # "그 시점에 존재하지 않던 가격"을 요구한 것이므로 원안 자체가 기하학적
            # 으로 무리다. 해석 시 반드시 병기할 것.
            "n_clamped": (out.get("n_clamped") or {}).get(v, 0),
            "clamp_excess_med": (
                round(sorted((out.get("clamp_excess") or {}).get(v) or [0])[
                    len((out.get("clamp_excess") or {}).get(v) or [0]) // 2], 4)
                if ((out.get("clamp_excess") or {}).get(v)) else 0.0),
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
            "n_excluded_override": out.get("n_excluded_override", 0),
            # [MW0601 432차 / 25-B] TP2 축 — 본채널 verdict와 분리된 별도 판정.
            "tp2": _summarize_tp2(out, base),
            # [MW0602 432차] 클램프 총계 — 리포트 생성기가 경고문에 쓴다.
            "n_clamped": out.get("n_clamped") or {}}


def _summarize_tp2(out: dict, offset_base: list) -> dict:
    """[MW0601 432차 / 25-B] TP2 거리 축 요약 — 본채널과 독립 판정.

    사전등록 기준은 VALIDATION_CAMPAIGN['tp1_protect_offset_shadow']의 tp2_* 키에
    관측 전 고정돼 있다. 여기서 기준을 바꾸지 말 것(§9).

    `offset_base`는 offset 축의 current 행 — 배선 검산에만 쓴다(판정 무관).
    """
    res = out.get("rows_tp2") or {}
    variants = out.get("tp2_variants") or []
    if not variants:
        return {"verdict": "DISABLED", "reason": "tp2_variants 미설정", "per_variant": {}}

    base = res.get("current", [])
    base_pts = [p for _, p in base]
    base_total = sum(base_pts) if base_pts else None

    per = {}
    for name in variants:
        rows = res.get(name, [])
        if not rows:
            continue
        pts = [p for _, p in rows]
        d = {
            "n": len(pts),
            "total_pt": round(sum(pts), 4),
            "avg_pt": round(sum(pts) / len(pts), 4),
            "median_pt": round(sorted(pts)[len(pts) // 2], 4),
            "win_rate": round(sum(1 for p in pts if p > 0) / len(pts), 4),
            "max_loss_pt": round(min(pts), 4),
            "std_pt": round((sum((p - sum(pts) / len(pts)) ** 2 for p in pts)
                             / max(len(pts) - 1, 1)) ** 0.5, 4),
            "n_stop": sum(1 for o, _ in rows if o == "STOP"),
            "n_tp2": sum(1 for o, _ in rows if o == "TP2"),
            "n_forced": sum(1 for o, _ in rows if o == "FORCED"),
            # [MW0601 443차] 결말 분포 전체 — v2는 라벨 집합이 다르다.
            # 보호전환 뒤 되돌려 털린 건은 "STOP"이 아니라 **TP1_ARM_STOP**이라
            # 위 n_stop이 v2에서 항상 0이다(결함이 아니다). 이 분포를 함께 내지
            # 않으면 "스톱 0건"이 "한 번도 안 털렸다"로 오독된다.
            "outcomes": {o: sum(1 for oo, _ in rows if oo == o)
                         for o in sorted({oo for oo, _ in rows})},
        }
        if base_total is not None and len(pts) == len(base_pts):
            deltas = [p - q for p, q in zip(pts, base_pts)]
            d["delta_vs_current"] = round(sum(deltas), 4)
            d["beats_current_n"] = sum(1 for x in deltas if x > 0)
            # 사전등록 판정보조 ① 이상치 분해(drop-max) — 최대 기여 1건을 뺀 delta.
            # [25] 본채널이 이 검사에서 무너진 전례가 있어 처음부터 계산해 노출한다.
            d["delta_drop_max"] = (round(sum(deltas) - max(deltas), 4)
                                   if deltas else None)
        else:
            d["delta_vs_current"] = None
            d["beats_current_n"] = None
            d["delta_drop_max"] = None
        per[name] = d

    min_n = int(_CR.get("tp2_min_samples", 20))
    min_d = int(_CR.get("tp2_min_days", 3))
    n_cur = len(base)
    if n_cur < min_n or out["n_days"] < min_d:
        verdict = "INSUFFICIENT"
        reason = ("표본 부족 (n=%d<%d 또는 거래일=%d<%d)"
                  % (n_cur, min_n, out["n_days"], min_d))
    else:
        beat = [k for k, v in per.items()
                if k != "current" and (v.get("delta_vs_current") or 0) > 0]
        verdict = "FAIL" if beat else "PASS"
        reason = ("현행 초과 대안: %s" % ", ".join(beat)) if beat else "모든 대안이 현행 이하"

    # 배선 검산 — TP2축 current와 offset축 current는 stop·tp2·시뮬이 전부 같으므로
    # 수치가 일치해야 한다. 어긋나면 축 하나가 잘못 배선된 것이므로 판정을 신뢰할 수
    # 없다. verdict는 건드리지 않고 사실만 노출한다(조용한 오염 방지).
    _ob = sum(p for _, p in offset_base) if offset_base else None
    consistent = (base_total is not None and _ob is not None
                  and abs(base_total - _ob) < 1e-9)
    return {
        "verdict": verdict, "reason": reason, "per_variant": per,
        "min_samples": min_n, "min_days": min_d,
        "n_hooks": out["n_hooks"], "n_days": out["n_days"],
        "baseline_consistent": consistent,
        "baseline_note": (None if consistent else
                          "⚠ 배선 검산 실패 — TP2축 current(%s) ≠ offset축 current(%s). "
                          "판정을 신뢰하지 말 것." % (base_total, _ob)),
    }


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
    # [MW0601 444차] v2 이관 후 STOP/강제 고정 컬럼은 항상 0을 찍는다 — 보호전환 뒤
    # 털린 건이 TP1_ARM_STOP으로 라벨링되기 때문이다(결함 아님). 리포트는 443차에
    # 결말 분포로 바꿨는데 CLI만 남아 있었다. 같은 표기로 통일한다.
    print("%-16s %5s %9s %9s %9s  %s"
          % ("변형", "n", "승률", "누적pt", "중앙값", "결말 분포"))
    for v in out["variants"]:
        d = s["per_variant"].get(v)
        if not d:
            print("%-16s (표본 없음)" % v)
            continue
        _oc = d.get("outcomes") or {}
        _oc_txt = (" ".join("%s=%d" % (o, c) for o, c in _oc.items())
                   if _oc else "STOP=%d TP2=%d" % (d["n_stop"], d["n_tp2"]))
        print("%-16s %5d %8.1f%% %+9.2f %+9.3f  %s"
              % (v, d["n"], d["win_rate"] * 100, d["total_pt"], d["median_pt"],
                 _oc_txt))
    print()
    print("현행 대비 차이 (pt / 1계약 환산 원 / 건별 우세 / 체결가능성 클램프):")
    for v in out["variants"]:
        d = s["per_variant"].get(v)
        if not d or v == "current":
            continue
        _cl = d.get("n_clamped", 0)
        _cltxt = ("클램프 %d/%d건(%.0f%%, 초과 중앙 %.2fpt)"
                  % (_cl, d["n"], 100.0 * _cl / d["n"], d.get("clamp_excess_med", 0.0))
                  ) if _cl else "클램프 없음"
        print("  %-16s %+8.2f pt   %+12s 원   우세 %s/%d건   %s"
              % (v, d["delta_vs_current"],
                 format(int((d["delta_vs_current"] or 0) * MINI_FUTURES_PT_VALUE), ","),
                 d["beats_current_n"], d["n"], _cltxt))
    print()
    print("판정: %s — %s" % (s["verdict"], s["reason"]))
    print("§9: 이 스크립트는 판정을 자동 적용하지 않는다. 적용은 주간회의 수동 결정.")
    print("⚠ breakeven 변형은 404차 후속3 조사에서 이미 1회 측정됨 — 사전등록 검증이")
    print("  아니라 재확인용이다. 사전등록 가치는 atr_lock_0.50/0.75·bar_range에 있다.")
    print("⚠ 절대값은 실현손익이 아니다(TP3·트레일링·신호소멸 미모델링). 상대비교 전용.")
    _tot_cl = sum((s.get("n_clamped") or {}).values())
    if _tot_cl:
        print("⚠ [432차] 체결가능성 클램프가 적용됐다 — offset이 보호전환 시점의 실제")
        print("  유리이동을 넘는 건은 그 시점 가격으로 잘랐다. 클램프 비율이 높은 변형은")
        print("  '그 순간 존재하지 않던 가격'을 요구한 것이므로 원안 자체가 기하학적 무리다.")
        print("  (클램프 도입 전 atr_lock_0.75는 +18.75pt였고 그 중 57%가 허수였다.)")

    # ── [MW0601 432차 / 25-B] TP2 거리 축 ─────────────────────────────────────
    t = s.get("tp2") or {}
    if t.get("per_variant"):
        print()
        print("=" * 92)
        print("[25-B] TP2 거리 A/B — 보호 offset은 현행(ATR×0.25) 고정, TP2만 변형")
        print("=" * 92)
        if not t.get("baseline_consistent"):
            print(t.get("baseline_note") or "⚠ 배선 검산 실패")
            print()
        print("%-12s %5s %7s %7s %7s %9s %9s %9s %9s"
              % ("변형", "n", "STOP", "TP2", "강제", "승률", "누적pt", "중앙값", "최대손실"))
        for v in out.get("tp2_variants", []):
            d = t["per_variant"].get(v)
            if not d:
                print("%-12s (표본 없음)" % v)
                continue
            print("%-12s %5d %7d %7d %7d %8.1f%% %+9.2f %+9.3f %+9.2f"
                  % (v, d["n"], d["n_stop"], d["n_tp2"], d["n_forced"],
                     d["win_rate"] * 100, d["total_pt"], d["median_pt"],
                     d["max_loss_pt"]))
        print()
        print("현행 대비 (pt / 1계약 환산 원 / 건별우세 / drop-max 후 delta):")
        for v in out.get("tp2_variants", []):
            d = t["per_variant"].get(v)
            if not d or v == "current" or d.get("delta_vs_current") is None:
                continue
            print("  %-12s %+8.2f pt  %+12s 원   우세 %s/%d건   drop-max %+8.2f pt"
                  % (v, d["delta_vs_current"],
                     format(int(d["delta_vs_current"] * MINI_FUTURES_PT_VALUE), ","),
                     d["beats_current_n"], d["n"], d["delta_drop_max"]))
        print()
        print("판정: %s — %s" % (t.get("verdict"), t.get("reason")))
        print("⚠ TP2 단축은 완주율↑ / 완주 1건당 이익↓의 교환이다. 누적pt만 보지 말고")
        print("  승률·최대손실·drop-max를 반드시 함께 읽을 것(사전등록 판정보조 ①②③).")
        print("⚠ 이 판정은 위 offset 축 판정과 **무관**하다 — 본채널 합격선 무변경(§9-4).")


if __name__ == "__main__":
    main()

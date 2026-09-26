# -*- coding: utf-8 -*-
"""strategy/stack_gate_shadow.py — 「기계적 매수 / 쌓는 매수」 진입 게이트 **섀도 계측**

출처: `Sindong\\peterlee\\매도매수_성격판별_지표검증_20260913.md` §4-9, §7
      (피터리 역설계에서 나온 "기계적 매도/매수 vs 쌓는 매도/매수" 4상태)

⛔ **이 모듈은 실거래 의사결정에 관여하지 않는다.** `trend_efficiency_gate_shadow`와
   같은 계측 전용이다 — 진입한 분봉 **전량**을 기록하고 `would_block`으로 가른다.
   라이브 편입은 표본 120거래일 + 사전등록 합격선 통과 뒤에만 검토한다.

━━ 상태 정의 (W=30분 관측창) ━━
    aggr_imb = (매수공격체결 − 매도공격체결)/거래량 의 30분합 **− 당일 중앙값**
               ⚠ 디바이어스 필수. 원시 buy_vol:sell_vol 이 전 구간 1.70:1 로
                 매수 편향돼 있어(분봉 98.9%) 빼지 않으면 매도 상태가 0개가 된다.
    oi_delta = OI(t) − OI(t−30), 일중 한정 (전일 이월분 섞지 않는다)
    active   = |aggr_imb| ≥ 당일 q분위 ∧ |oi_delta| ≥ 당일 q분위   (기본 q=0.5)

    aggr_imb>0 ∧ oi_delta≤0 → BUY_MECH   기계적 매수  ← 롱 차단 후보
        ⚠ "숏 환매"로 단정하지 말 것. OI 감소는 **매수자와 매도자가 모두 청산**일 때만
          일어난다. 실측(수급 유효 42일, 30분 증분 중앙값)이 말하는 구성은:
            외국인 선물 -128계약 / 기관 선물 +102계약 / 차익프로그램 -2,445백만
          → 사는 쪽은 **기관**이고, 차익 프로그램이 줄며(주식 매도) 선물을 되사는
            **매수차익 청산**이다. 그 반대편에서 외국인이 롱을 정리한다.
          즉 숏 환매는 맞되 **차익 환매**이지 방향성 숏의 손절이 아니다.
    aggr_imb>0 ∧ oi_delta>0 → BUY_STACK  상방을 쌓는 매수
        거울상: 외국인 선물 +325계약 / 기관 -382계약 / 차익 +18,856백만 → 외국인이
        신규 롱, 기관이 차익으로 신규 숏. 새 포지션 둘이 맞붙어 OI가 는다.
    aggr_imb<0 ∧ oi_delta>0 → SELL_STACK 하방을 쌓는 매도
    aggr_imb<0 ∧ oi_delta≤0 → SELL_MECH  기계적 매도

━━ 검증 근거와 한계 (2026-09-13 기준) ━━
    표본밖(앞40일 학습/뒤 검증) 기계적 매수 구간 **롱** 기댓값:
        W30/h60  −10.91bp [−14.38, −7.41] P(<0)=1.000  (검증 22일)
        W30/h20   −9.13bp [−12.95, −5.43] P(<0)=1.000
        W30/h5    −3.03bp [ −7.53, +1.13] P(<0)=0.921   ← 미륵이 실보유(중앙 2.8분) 척도
    · 효과는 **W=30분 관측창에서만** 존재한다. W=5/10/15 에서는 사라진다.
    · 미륵이 실제 보유시간 척도(5분)에서는 부호만 맞고 **유의하지 않다.**
    · 실매매 로그 대조: LONG∧BUY_MECH n=12 평균 −2.77pt / SHORT∧BUY_MECH n=29
      평균 +1.29pt·승률 79% — 방향은 일관하나 표본이 작다.
    · 롤 회피 교란 통제 완료: BUY_MECH의 52.6%가 "일중 OI 급감일"에 몰려 있어
      만기 회피 드리프트가 의심됐으나, 일별 드리프트를 뺀 뒤에도 라벨의 80.2%가
      유지되고(반대 상태로 넘어간 건 0건) 표본밖 기댓값도 −14.31bp [−13.43, −7.21]
      P(<0)=1.000 (검증 27일)로 살아남는다.
    → **지금은 기록만 한다.**
"""
from __future__ import annotations

import datetime
import logging
from collections import deque
from typing import Deque, Dict, List, Optional

logger = logging.getLogger(__name__)

WINDOW_MIN = 30          # 관측창 — 검증에서 이 값에서만 효과가 존재했다
ACTIVE_Q = 0.5           # 활성 임계(당일 분위). 낮추면 커버리지↑ 효과↓ (§4-9 표)
STATE_BUY_MECH = "BUY_MECH"
STATE_BUY_STACK = "BUY_STACK"
STATE_SELL_MECH = "SELL_MECH"
STATE_SELL_STACK = "SELL_STACK"
STATE_NA = "NA"


def _quantile(vals: List[float], q: float) -> Optional[float]:
    v = sorted(x for x in vals if x is not None)
    if not v:
        return None
    if q <= 0:
        return v[0]
    i = min(int(q * (len(v) - 1)), len(v) - 1)
    return v[i]


class StackGateShadow:
    """일 단위로 리셋되는 롤링 상태기. main.py 분봉 루프에서 update() 한 번 호출."""

    def __init__(self, window_min: int = WINDOW_MIN, active_q: float = ACTIVE_Q):
        self.W = int(window_min)
        self.q = float(active_q)
        self._bars: Deque[dict] = deque(maxlen=self.W + 1)
        self._ar_hist: List[float] = []      # 당일 aggr_imb_raw 이력 (중앙값 산출용)
        self._abs_ar: List[float] = []       # 당일 |디바이어스 aggr_imb|
        self._abs_oi: List[float] = []       # 당일 |oi_delta|
        self._day: Optional[str] = None

    def reset_daily(self) -> None:
        self._bars.clear(); self._ar_hist.clear()
        self._abs_ar.clear(); self._abs_oi.clear()

    def update(self, ts: str, buy_vol, sell_vol, volume, oi) -> Dict:
        """분봉 1개 투입 → 현재 상태 dict 반환.

        Args:
            ts: "%Y-%m-%d %H:%M:%S" 또는 "%Y-%m-%d %H:%M:00"
            buy_vol/sell_vol/volume: 해당 분봉 (raw_candles 동일 컬럼)
            oi: 해당 분봉 미결제약정
        """
        day = ts[:10]
        if self._day != day:
            self._day = day
            self.reset_daily()
        self._bars.append({
            "ts": ts,
            "bv": float(buy_vol or 0.0), "sv": float(sell_vol or 0.0),
            "vol": float(volume or 0.0), "oi": (None if oi in (None, 0) else float(oi)),
        })
        out = {"state": STATE_NA, "aggr_imb": None, "oi_delta": None,
               "ready": False, "reason": ""}
        if len(self._bars) <= self.W:
            out["reason"] = "warmup(%d/%d)" % (len(self._bars), self.W + 1)
            return out
        win = list(self._bars)[-self.W:]
        bv = sum(b["bv"] for b in win); sv = sum(b["sv"] for b in win)
        vol = sum(b["vol"] for b in win)
        if vol <= 0 or (bv + sv) <= 0:
            out["reason"] = "no_aggressor_data"       # 2026-06-08 이전 구간이 여기
            return out
        ar_raw = (bv - sv) / vol
        self._ar_hist.append(ar_raw)
        med = _quantile(self._ar_hist, 0.5) or 0.0
        aggr = ar_raw - med                            # ⚠ 디바이어스
        oi_now = self._bars[-1]["oi"]; oi_then = self._bars[-(self.W + 1)]["oi"]
        if oi_now is None or oi_then is None:
            out["reason"] = "no_oi"
            return out
        doi = oi_now - oi_then
        self._abs_ar.append(abs(aggr)); self._abs_oi.append(abs(doi))
        out.update({"aggr_imb": aggr, "oi_delta": doi, "ready": True})
        ta = _quantile(self._abs_ar, self.q); to = _quantile(self._abs_oi, self.q)
        if ta is None or to is None or abs(aggr) < ta or abs(doi) < to:
            out["reason"] = "inactive"
            return out
        if aggr > 0:
            out["state"] = STATE_BUY_STACK if doi > 0 else STATE_BUY_MECH
        else:
            out["state"] = STATE_SELL_STACK if doi > 0 else STATE_SELL_MECH
        return out

    @staticmethod
    def would_block(state: str, direction: str) -> bool:
        """라이브 편입 시 차단 조건 — 지금은 기록용 플래그일 뿐이다."""
        return state == STATE_BUY_MECH and direction == "LONG"


# ── DDL — utils/db_utils.init_db() 에 옮겨 붙이거나 아래 ensure_table()을 쓴다 ──
DDL = """
CREATE TABLE IF NOT EXISTS stack_gate_shadow (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ts            TEXT NOT NULL,      -- 진입 분봉 시각
    direction     TEXT NOT NULL,      -- LONG/SHORT (실제 진입 방향)
    grade         TEXT,
    state         TEXT,               -- BUY_MECH / BUY_STACK / SELL_MECH / SELL_STACK / NA
    aggr_imb      REAL,               -- 디바이어스 공격자 불균형 (30분)
    oi_delta      REAL,               -- OI 30분 증분
    state_ready   INTEGER,            -- 0=워밍업·데이터없음 1=실측 (미측정과 폴백을 뭉개지 않는다)
    would_block   INTEGER,            -- 1 = 게이트가 켜졌다면 차단됐을 진입
    conf          REAL,
    atr           REAL,
    entry_horizon TEXT,
    entry_qty     INTEGER,
    entry_price   REAL NOT NULL,      -- 섀도 관례 — 분봉 종가(실체결가 아님)
    stop_price    REAL,
    tp1_price     REAL,
    resolved      INTEGER DEFAULT 0,
    cf_outcome    TEXT,               -- STOP / TP1 / NEITHER
    cf_exit_price REAL,
    hyp_pnl_pts   REAL,               -- (+)=진입이 옳았음, (-)=차단이 옳았음
    mfe5_atr      REAL,               -- 고정 5분 창 (미륵이 실보유 중앙 2.8분에 맞춘 계측)
    mae5_atr      REAL,
    mfe30_atr     REAL,               -- 고정 30분 창
    mae30_atr     REAL,
    created_at    TEXT DEFAULT (datetime('now', 'localtime'))
)
"""
DDL_IDX = "CREATE INDEX IF NOT EXISTS idx_sgs_ts ON stack_gate_shadow(ts)"

INSERT_SQL = """INSERT INTO stack_gate_shadow
 (ts, direction, grade, state, aggr_imb, oi_delta, state_ready, would_block,
  conf, atr, entry_horizon, entry_qty, entry_price, stop_price, tp1_price)
 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""


def ensure_table(db_path: str) -> None:
    import sqlite3
    con = sqlite3.connect(db_path)
    try:
        con.execute(DDL); con.execute(DDL_IDX); con.commit()
    finally:
        con.close()


def resolve_rows(bar_map: Dict[str, dict], rows: List[dict]) -> List[tuple]:
    """미결 행의 반사실 판정 — 진입 분봉 이후 STOP/TP1 중 먼저 닿는 쪽.

    `trend_efficiency_gate_shadow` 판정 관례와 동일하게 **분봉 격자**를 걷는다.
    동일봉 동시터치는 보수적으로 STOP 우선 (model/triple_barrier_label.py 규약).
    """
    out = []
    for r in rows:
        t0 = datetime.datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S")
        lng = r["direction"] == "LONG"
        stop, tp1, ep = r["stop_price"], r["tp1_price"], r["entry_price"]
        atr = r.get("atr") or 0.0
        outcome, px = "NEITHER", None
        mfe = {5: 0.0, 30: 0.0}; mae = {5: 0.0, 30: 0.0}
        for m in range(1, 31):
            b = bar_map.get((t0 + datetime.timedelta(minutes=m)).strftime("%Y-%m-%d %H:%M:00"))
            if not b:
                continue
            for w in (5, 30):
                if m <= w:
                    up, dn = b["high"] - ep, b["low"] - ep
                    mfe[w] = max(mfe[w], up if lng else -dn)
                    mae[w] = min(mae[w], dn if lng else -up)
            if outcome == "NEITHER":
                hit_s = (b["low"] <= stop) if lng else (b["high"] >= stop)
                hit_t = (b["high"] >= tp1) if lng else (b["low"] <= tp1)
                if hit_s:
                    outcome, px = "STOP", stop
                elif hit_t:
                    outcome, px = "TP1", tp1
        if outcome == "NEITHER":
            b = bar_map.get((t0 + datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:00"))
            px = b["close"] if b else None
        if px is None:
            continue
        pnl = (px - ep) if lng else (ep - px)
        a = atr if atr else 1.0
        out.append((1, outcome, float(px), float(pnl),
                    mfe[5] / a, mae[5] / a, mfe[30] / a, mae[30] / a, r["id"]))
    return out


UPDATE_SQL = """UPDATE stack_gate_shadow SET resolved=?, cf_outcome=?, cf_exit_price=?,
 hyp_pnl_pts=?, mfe5_atr=?, mae5_atr=?, mfe30_atr=?, mae30_atr=? WHERE id=?"""

# collection/cybos/futures_flow_series.py
"""선물 수급 4종 — 시초 대비 증감 시계열 (613차).

「선물 투자자 수급」 6카드(현재값 하나만 보여주던 것)를 걷어내고, 그중 4종을
개인 옵션 6종과 **같은 형식**의 시계열로 옮긴다(사용자 지시 2026-09-21).

    · 미결제약정 (계약)          ← `raw_candles.oi` + `raw_investor_futures`
    · 외인 선물 순매수 (계약)    ← `raw_investor_futures`      [613차 신설]
    · 프로그램 차익 (백만원)     ← `raw_program_trade` idx19   [451차 신설]
    · 프로그램 비차익 (백만원)   ← `raw_program_trade` idx37

반환 스키마는 `WeeklyOptionFlow.get_individual_session_delta()` 와 **일부러 같다** —
차트 위젯이 두 payload 를 같은 코드로 그린다.

설계 메모
---------
· **네 행 모두 「당일 첫 바를 0 으로 놓은 차분」이다.** 앞의 셋은 원천이
  *일중 누계*라 차분해야 흐름이 보이고(451차 주석이 같은 지적을 한다),
  미결제약정은 레벨이지만 시초 대비 증감이 곧 신규 진입·청산 흐름이다.
· **누계도 함께 싣는다**(`value`). 걷어낸 카드가 보여주던 값이 그것이라,
  증감만 남기면 미결제 62,767 같은 절대 수준이 화면에서 사라진다.
· **기준 시각이 행마다 다르다.** 실측 첫 바 — 캔들 08:45 · 프로그램 09:02 ·
  7221 수급 09:02(09:00~09:02 는 서버 피크라 의도적으로 스킵한다).
  그래서 `baseline_time` 을 행마다 따로 싣는다. 하나로 뭉뚱그리면 안 된다.
· **결측 분을 0 으로 잇지 않는다.** 없는 분은 점을 찍지 않는다(계측 4원칙 ②).
· **미수집 상품은 키 자체를 만들지 않는다.** 빈 dict 와 0 을 구분한다.
"""
from __future__ import annotations

import datetime
import json
import logging
import sqlite3
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("SYSTEM")

# (키, 라벨, 단위) — 사용자 지정 순서 그대로.
DASHBOARD_PRODUCTS: Tuple[Tuple[str, str, str], ...] = (
    ("open_int",    "미결제약정",       "계약"),
    ("fut_fi",      "외인 선물 순매수", "계약"),
    ("prog_arb",    "프로그램 차익",    "백만원"),
    ("prog_nonarb", "프로그램 비차익",  "백만원"),
)

SESSION_START = "08:45"
SESSION_END   = "15:35"

# `raw_program_trade.fields` 의 열 인덱스 — 문자열 키다(JSON).
# ⚠ idx17(차익순매수 위탁금액)은 서버측 결함으로 idx19 를 중복 반환한다(451차 주석).
_ARB_IDX    = "19"
_NONARB_IDX = "37"


def _hhmm(ts: str) -> Optional[str]:
    """'YYYY-MM-DD HH:MM:SS' → 'HH:MM'."""
    try:
        return ts[11:16]
    except Exception:                                           # noqa: BLE001
        return None


def _pack(label: str, unit: str, pts: List[Tuple[str, int]],
          src: str) -> Optional[Dict[str, Any]]:
    """관측점 리스트를 payload 한 칸으로. 비었으면 None(키를 만들지 않는다)."""
    if not pts:
        return None
    base_t, base_v = pts[0]
    last_t, last_v = pts[-1]
    return {
        "label":         label,
        "unit":          unit,
        "baseline":      base_v,
        "baseline_time": base_t,
        "value":         last_v,              # 현재 **누계/레벨** (걷어낸 카드의 값)
        "delta":         last_v - base_v,     # 시초 대비 증감 (막대가 그리는 값)
        "last_time":     last_t,
        "n":             len(pts),
        "src":           src,                 # live | derived | mixed
        "series":        [(t, v - base_v) for t, v in pts],
    }


def _src_of(seen: Set[str]) -> str:
    if not seen:
        return "live"
    if len(seen) == 1:
        for s in seen:
            return s
    return "mixed"


def get_futures_session_delta(
    trade_date: Optional[str] = None,
    raw_db_path: str = "data/db/raw_data.db",
) -> Dict[str, Any]:
    """선물 수급 4종의 **시초 대비 증감** 시계열.

    호출은 수급 QTimer 경로에서 분당 1회 — **GUI 스레드에서 DB 를 열지 않는다.**
    조회 3건 전부 PK(ts) 범위 스캔이며 하루치는 약 390행씩이다.

    Returns:
        {"trade_date", "last_time", "products": {key: {...}}}
        수집 전이면 `products` 가 비어 있다 — 빈 dict 와 0 을 구분한다.
    """
    today = trade_date or datetime.date.today().isoformat()
    lo = "%s %s:00" % (today, SESSION_START)
    hi = "%s %s:59" % (today, SESSION_END)
    out = {"trade_date": today, "last_time": None, "products": {}}   # type: Dict[str, Any]

    try:
        con = sqlite3.connect("file:%s?mode=ro" % raw_db_path, uri=True, timeout=3.0)
    except Exception as exc:                                    # noqa: BLE001
        logger.warning("[FuturesFlow] DB 열기 실패: %s", exc)
        return out

    fi_pts = []     # type: List[Tuple[str, int]]
    oi_pts = []     # type: List[Tuple[str, int]]
    arb_pts = []    # type: List[Tuple[str, int]]
    non_pts = []    # type: List[Tuple[str, int]]
    fi_src = set()  # type: Set[str]
    oi_src = set()  # type: Set[str]

    try:
        # ── ① 미결제약정 — 캔들이 1차 원천 ────────────────────────────
        # `raw_candles.oi` 는 08:45 부터 있고 과거 전 구간에 존재한다(백필 불필요).
        # 다만 **15:08 에서 끊긴다** — 분봉 파이프라인이 15:09 에 정상 종료하기
        # 때문이다. 그 뒤는 아래 ②의 수급 테이블이 이어받는다.
        try:
            for ts, oi in con.execute(
                "SELECT ts, oi FROM raw_candles WHERE ts>=? AND ts<=? ORDER BY ts",
                (lo, hi),
            ):
                t = _hhmm(ts)
                if t is None or oi is None or int(oi) <= 0:
                    continue        # 0 은 미수신이다 — 실측 0계약이 아니다
                oi_pts.append((t, int(oi)))
                oi_src.add("live")
        except sqlite3.Error as exc:
            logger.debug("[FuturesFlow] raw_candles 조회 스킵: %s", exc)

        # ── ② 외인 선물 순매수 + 미결제약정 꼬리 ──────────────────────
        try:
            rows = con.execute(
                "SELECT ts, fields, src FROM raw_investor_futures "
                "WHERE ts>=? AND ts<=? ORDER BY ts",
                (lo, hi),
            ).fetchall()
        except sqlite3.Error as exc:
            # 613차 배포 전 날짜이거나 테이블 미생성. 행이 없는 것과 같다.
            logger.debug("[FuturesFlow] raw_investor_futures 조회 스킵: %s", exc)
            rows = []

        last_candle_t = oi_pts[-1][0] if oi_pts else None
        for ts, fields_json, src in rows:
            t = _hhmm(ts)
            if t is None:
                continue
            try:
                f = json.loads(fields_json)
            except Exception:                                   # noqa: BLE001
                continue
            v = f.get("foreign_net_qty")
            if v is not None:
                fi_pts.append((t, int(v)))
                fi_src.add(str(src or "live"))
            # 캔들이 끊긴 뒤 구간만 이어붙인다 — 같은 분을 두 원천으로 두 번
            # 찍으면 축이 섞인다(둘 다 계약이지만 관측 시점이 다르다).
            oi_v = f.get("open_interest")
            if oi_v and (last_candle_t is None or t > last_candle_t):
                oi_pts.append((t, int(oi_v)))
                oi_src.add(str(src or "live"))

        # ── ③ 프로그램 차익·비차익 ────────────────────────────────────
        try:
            for ts, fields_json in con.execute(
                "SELECT ts, fields FROM raw_program_trade "
                "WHERE ts>=? AND ts<=? AND market='1' ORDER BY ts",
                (lo, hi),
            ):
                t = _hhmm(ts)
                if t is None:
                    continue
                try:
                    f = json.loads(fields_json)
                except Exception:                               # noqa: BLE001
                    continue
                if _ARB_IDX in f:
                    arb_pts.append((t, int(f[_ARB_IDX])))
                if _NONARB_IDX in f:
                    non_pts.append((t, int(f[_NONARB_IDX])))
        except sqlite3.Error as exc:
            logger.debug("[FuturesFlow] raw_program_trade 조회 스킵: %s", exc)
    except Exception as exc:                                    # noqa: BLE001
        logger.warning("[FuturesFlow] 조회 실패: %s", exc)
        return out
    finally:
        try:
            con.close()
        except Exception:                                       # noqa: BLE001
            pass

    meta = dict((k, (lab, unit)) for k, lab, unit in DASHBOARD_PRODUCTS)
    packed = {
        "open_int":    _pack(meta["open_int"][0], meta["open_int"][1],
                             oi_pts, _src_of(oi_src)),
        "fut_fi":      _pack(meta["fut_fi"][0], meta["fut_fi"][1],
                             fi_pts, _src_of(fi_src)),
        "prog_arb":    _pack(meta["prog_arb"][0], meta["prog_arb"][1],
                             arb_pts, "live"),
        "prog_nonarb": _pack(meta["prog_nonarb"][0], meta["prog_nonarb"][1],
                             non_pts, "live"),
    }
    last_times = []
    for key, _lab, _unit in DASHBOARD_PRODUCTS:
        d = packed.get(key)
        if d is None:
            continue            # 아직 안 옴 — 항목 자체를 만들지 않는다
        out["products"][key] = d
        last_times.append(d["last_time"])
    out["last_time"] = max(last_times) if last_times else None
    return out

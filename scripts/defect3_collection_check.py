# -*- coding: utf-8 -*-
"""[MW0601 559차] 데이터 결함 3건 — **수집 정상성** 일일 점검기.

무엇을 재는가
-------------
559차가 손댄 세 결함의 수집이 다음 거래일에도 **끊기지 않고 들어오는가**.
계측을 새로 붙였는지가 아니라, 원래 재던 것까지 **여전히 정상인가**를 본다.

  ① 체결 방향  — 앵커·섀도·미분류 적재율, 항등식 I4, 3축 매수비중
  ② 외국인 수급 — 그날 값이 상수가 아닌가, 단위가 압축값인가, 측정 플래그가 도는가
  ③ 호가잔량    — book_* 적재율, 스냅샷 수, 5단이 1단보다 두꺼운가, 적립 진척

왜 스크립트인가
---------------
이 프로젝트가 반복해서 밟은 함정이 **「만들어 놓고 안 돌린 계측」**이다
(FP-CRITICAL 죽은 게이트 2개월 · TOX 죽은 섀도 1개월 · 552차 결함1 하루).
손으로 쿼리하면 항목을 빠뜨리므로, 다음 거래일 장후에 **이것 하나만** 돌린다.

🔴 이것은 알파 판정기가 아니다. 손익도 IC 도 보지 않는다.

판정 기준은 상단에 **사전등록**돼 있다. 결과를 보고 임계를 고치지 말 것(458차 D6).

실행
----
    python scripts/defect3_collection_check.py                 # 최근 거래일
    python scripts/defect3_collection_check.py --date 2026-09-16
    python scripts/defect3_collection_check.py --json

⚠ 장 마감 후 전용(456차 — 장중 라이브 DB 전수 스캔이 CB⑤를 자가유발했다).
종료코드: 0 = 전부 통과(또는 경고만) · 1 = FAIL 1건 이상 · 2 = 장중 차단.
"""
from __future__ import print_function

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402

ensure_conda_dll_path()

import argparse  # noqa: E402
import json as _json  # noqa: E402
from collections import OrderedDict  # noqa: E402

from utils.analysis_db import guard_intraday, connect_ro  # noqa: E402

CHANNEL = "defect3_collection_check"
RAW_DB = os.path.join(_ROOT, "data", "db", "raw_data.db")

# ── 사전등록 임계 ────────────────────────────────────────────────────────────
FILL_MIN = 0.98            # 앵커·섀도·미분류·호가 적재율 하한
ANCHOR_SHARE_BAND = (0.45, 0.55)   # 앵커 매수비중 정상대 — 벗어나면 원천을 의심
LEGACY_SHARE_MIN = 0.55    # legacy 는 아직 편향돼 있어야 정상(전환 전이므로)
SHADOW_ANCHOR_GAP_MAX = 0.02       # 섀도 vs 앵커 괴리 상한(452차 반증 조건)
INV_ABS_MAX = 10.0         # 수급 압축값 정상 상한 — 넘으면 단위 불일치
BOOK_DEPTH_RATIO_MIN = 1.05        # 5단 총잔량 ÷ 1단 잔량. 1.0 이면 2~5단이 비었다
BOOK_TARGET_DAYS = 60      # Phase 3-0/3 판정에 필요한 적립 거래일

# 559차 배포일. 이 날 **이전** 거래일에는 `unk_vol`·`*_measured` 가 존재하지 않는다 —
# 그 날을 점검하면 FAIL 이 아니라 **미측정(n/a)** 이다(계측 4원칙 ②).
# 배포일이 밀리면 여기만 고친다.
DEPLOY_DATE = "2026-09-13"

_OK, _WARN, _FAIL, _NA = "PASS", "WARN", "FAIL", "n/a"


def _add(rows, defect, name, verdict, detail):
    rows.append({"defect": defect, "name": name, "verdict": verdict, "detail": detail})


def _latest_day(con):
    r = con.execute("SELECT MAX(substr(ts,1,10)) FROM raw_candles").fetchone()
    return r[0] if r else None


def check_flow(con, day, rows):
    """① 체결 방향 — 앵커·섀도·미분류가 계속 들어오는가."""
    q = con.execute(
        "SELECT COUNT(*), SUM(anchor_buy IS NOT NULL), SUM(buy_vol_flag IS NOT NULL),"
        " SUM(unk_vol IS NOT NULL), SUM(COALESCE(buy_vol,0)), SUM(COALESCE(sell_vol,0)),"
        " SUM(COALESCE(buy_vol_flag,0)), SUM(COALESCE(sell_vol_flag,0)),"
        " SUM(COALESCE(anchor_buy,0)), SUM(COALESCE(anchor_sell,0)),"
        " SUM(COALESCE(unk_vol,0))"
        " FROM raw_candles WHERE substr(ts,1,10)=?", (day,)).fetchone()
    n = q[0] or 0
    if not n:
        _add(rows, "①", "봉 수집", _FAIL, "%s 봉이 0개다 — 수집 자체가 안 됐다" % day)
        return
    _add(rows, "①", "봉 수집", _OK, "%d봉" % n)

    post = day >= DEPLOY_DATE
    for label, idx in (("앵커 적재율", 1), ("섀도 적재율", 2), ("미분류 적재율", 3)):
        r = (q[idx] or 0) / float(n)
        if label == "미분류 적재율" and not post:
            _add(rows, "①", label, _NA,
                 "%s 는 559차 배포(%s) 이전이라 `unk_vol` 이 없다 — 결함이 아니다"
                 % (day, DEPLOY_DATE))
            continue
        v = _OK if r >= FILL_MIN else _FAIL
        note = ""
        if label == "미분류 적재율" and v == _FAIL and (q[idx] or 0) == 0:
            note = " — 559차 P1-4 배선이 안 돌았다"
        _add(rows, "①", label, v, "%d/%d (%.1f%%)%s" % (q[idx] or 0, n, r * 100, note))

    legacy = (q[4] or 0) / float((q[4] or 0) + (q[5] or 0) or 1)
    shadow = (q[6] or 0) / float((q[6] or 0) + (q[7] or 0) or 1)
    anchor = (q[8] or 0) / float((q[8] or 0) + (q[9] or 0) or 1)
    _add(rows, "①", "legacy 매수비중", _OK if legacy >= LEGACY_SHARE_MIN else _WARN,
         "%.2f%% — 전환 전이므로 편향(>=%.0f%%)이 정상이다"
         % (legacy * 100, LEGACY_SHARE_MIN * 100))
    _add(rows, "①", "앵커 매수비중",
         _OK if ANCHOR_SHARE_BAND[0] <= anchor <= ANCHOR_SHARE_BAND[1] else _FAIL,
         "%.2f%% (정상대 %.0f~%.0f%%)"
         % (anchor * 100, ANCHOR_SHARE_BAND[0] * 100, ANCHOR_SHARE_BAND[1] * 100))
    gap = abs(shadow - anchor)
    _add(rows, "①", "섀도 vs 앵커 괴리", _OK if gap <= SHADOW_ANCHOR_GAP_MAX else _FAIL,
         "%.2f%%p (상한 %.0f%%p) — 넘으면 Phase 3 을 앵커 직접 사용으로 재설계"
         % (gap * 100, SHADOW_ANCHOR_GAP_MAX * 100))

    bad = con.execute(
        "SELECT COUNT(*) FROM raw_candles WHERE substr(ts,1,10)=?"
        " AND buy_vol_flag IS NOT NULL AND unk_vol IS NOT NULL"
        " AND buy_vol_flag + sell_vol_flag + unk_vol <> volume", (day,)).fetchone()[0]
    have = con.execute(
        "SELECT COUNT(*) FROM raw_candles WHERE substr(ts,1,10)=?"
        " AND buy_vol_flag IS NOT NULL AND unk_vol IS NOT NULL", (day,)).fetchone()[0]
    if not have:
        _add(rows, "①", "항등식 I4", _NA, "unk_vol 계측 봉이 없다")
    else:
        _add(rows, "①", "항등식 I4", _OK if bad == 0 else _FAIL,
             "위반 %d/%d봉 · 미분류 누계 %d계약" % (bad, have, q[10] or 0))


def check_investor(con, day, rows):
    """② 외국인 수급 — 상수가 아닌가, 단위가 맞는가, 측정 플래그가 도는가."""
    import json
    vals, meas_pre, meas_reg, sup_reg, n = [], [], [], [], 0
    absmax = 0.0
    flag_absent = 0
    for ts, feat in con.execute(
            "SELECT ts, features FROM raw_features WHERE substr(ts,1,10)=? ORDER BY ts",
            (day,)):
        try:
            f = json.loads(feat)
        except Exception:
            continue
        n += 1
        v = f.get("foreign_futures_net")
        if v is not None:
            vals.append(float(v))
            absmax = max(absmax, abs(float(v)))
        m = f.get("foreign_futures_net_measured")
        if m is None:
            flag_absent += 1
        elif ts[11:16] < "09:00":
            meas_pre.append(float(m))
        else:
            meas_reg.append(float(m))
        s = f.get("quality_investor_supported")
        if s is not None and ts[11:16] >= "09:00":
            sup_reg.append(float(s))

    if not n:
        _add(rows, "②", "피처 행", _FAIL, "%s 행이 0개다" % day)
        return
    _add(rows, "②", "피처 행", _OK, "%d행" % n)

    distinct = len(set(vals))
    _add(rows, "②", "값이 상수가 아닌가", _OK if distinct > 1 else _FAIL,
         "distinct %d — 1 이면 07-13 이전처럼 하루 종일 상수다" % distinct)
    _add(rows, "②", "단위 정상(압축값)", _OK if absmax <= INV_ABS_MAX else _FAIL,
         "|max| %.4g (상한 %.0f) — 넘으면 압축 이전 원단위가 섞였다" % (absmax, INV_ABS_MAX))

    if flag_absent == n and day < DEPLOY_DATE:
        _add(rows, "②", "측정 플래그", _NA,
             "%s 는 559차 배포(%s) 이전이라 `*_measured` 가 없다 — 결함이 아니다"
             % (day, DEPLOY_DATE))
    elif flag_absent == n:
        _add(rows, "②", "측정 플래그", _FAIL,
             "`*_measured` 키가 한 행도 없다 — 559차 P1'-1 배선이 안 돌았다")
    else:
        pre_ok = (not meas_pre) or max(meas_pre) == 0.0
        reg_ok = bool(meas_reg) and (sum(meas_reg) / len(meas_reg)) > 0.5
        _add(rows, "②", "측정 플래그 프리장", _OK if pre_ok else _WARN,
             "프리장 %d행 중 측정=1 이 %d행 (0 이어야 정상)"
             % (len(meas_pre), sum(1 for x in meas_pre if x)))
        _add(rows, "②", "측정 플래그 정규장", _OK if reg_ok else _FAIL,
             "정규장 %d행 중 측정=1 이 %d행"
             % (len(meas_reg), sum(1 for x in meas_reg if x)))
    if sup_reg:
        r = sum(sup_reg) / len(sup_reg)
        _add(rows, "②", "TR 지원율(정규장)", _OK if r > 0.5 else _FAIL,
             "%.1f%% — 0 이면 CpSvrNew7221 이 안 붙었다" % (r * 100))


def check_book(con, day, rows):
    """③ 호가잔량 — 적재가 이어지는가, 5단이 실제로 차 있는가, 적립은 몇 일인가."""
    q = con.execute(
        "SELECT COUNT(*), SUM(book_bid_tot IS NOT NULL), SUM(COALESCE(book_snaps,0)>0),"
        " AVG(book_snaps) FROM raw_candles WHERE substr(ts,1,10)=?", (day,)).fetchone()
    n = q[0] or 0
    if not n:
        _add(rows, "③", "봉 수집", _FAIL, "%s 봉이 0개다" % day)
        return
    r = (q[1] or 0) / float(n)
    _add(rows, "③", "book_* 적재율", _OK if r >= FILL_MIN else _FAIL,
         "%d/%d (%.1f%%)" % (q[1] or 0, n, r * 100))
    _add(rows, "③", "스냅샷 수신 봉", _OK if (q[2] or 0) / float(n) >= FILL_MIN else _WARN,
         "%d/%d · 봉당 평균 %.0f회" % (q[2] or 0, n, q[3] or 0))

    sb = con.execute(
        "SELECT COUNT(*), SUM(book_bid_tot IS NOT NULL),"
        " AVG(CASE WHEN bid_qty>0 AND book_bid_tot IS NOT NULL"
        "      THEN 1.0*book_bid_tot/bid_qty END),"
        " SUM(CASE WHEN bid_qty>0 AND book_bid_tot IS NOT NULL"
        "      AND book_bid_tot<=bid_qty THEN 1 ELSE 0 END)"
        " FROM session_bars WHERE substr(ts,1,10)=?", (day,)).fetchone()
    if not (sb and sb[0]):
        _add(rows, "③", "session_bars 적재", _WARN, "%s 세션봉이 없다" % day)
    else:
        _add(rows, "③", "session_bars 적재율",
             _OK if (sb[1] or 0) / float(sb[0]) >= FILL_MIN else _FAIL,
             "%d/%d" % (sb[1] or 0, sb[0]))
        ratio = sb[2] or 0.0
        _add(rows, "③", "5단 ÷ 1단 잔량비",
             _OK if ratio >= BOOK_DEPTH_RATIO_MIN else _FAIL,
             "평균 %.2f (하한 %.2f) · 비<=1.0 인 봉 %d — 1.0 이면 2~5단이 비었거나 파싱 어긋남"
             % (ratio, BOOK_DEPTH_RATIO_MIN, sb[3] or 0))

    days = con.execute(
        "SELECT COUNT(DISTINCT substr(ts,1,10)) FROM raw_candles"
        " WHERE book_bid_tot IS NOT NULL").fetchone()[0]
    _add(rows, "③", "적립 진척", _OK,
         "%d/%d 거래일 (Phase 3-0 판정 %d일)" % (days, BOOK_TARGET_DAYS, 20))


def main():
    ap = argparse.ArgumentParser(description="데이터 결함 3건 수집 정상성 점검 (559차)")
    ap.add_argument("--date", default=None, help="점검 거래일 (기본: 최근일)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    guard_intraday(CHANNEL)
    if not os.path.exists(RAW_DB):
        print("[%s] raw_data.db 없음" % CHANNEL)
        return 0

    con = connect_ro(RAW_DB)
    day = args.date or _latest_day(con)
    rows = []
    check_flow(con, day, rows)
    check_investor(con, day, rows)
    check_book(con, day, rows)

    n_fail = sum(1 for r in rows if r["verdict"] == _FAIL)
    n_warn = sum(1 for r in rows if r["verdict"] == _WARN)

    if args.json:
        print(_json.dumps({"channel": CHANNEL, "date": day, "fail": n_fail,
                           "warn": n_warn, "rows": rows}, ensure_ascii=False, indent=2))
        return 1 if n_fail else 0

    print("=" * 78)
    print("[%s] 데이터 결함 3건 수집 정상성 — %s" % (CHANNEL, day))
    print("=" * 78)
    cur = None
    titles = {"①": "체결 방향 (buy_vol/sell_vol)", "②": "외국인 수급 (foreign_futures_net)",
              "③": "호가잔량 (book_*)"}
    for r in rows:
        if r["defect"] != cur:
            cur = r["defect"]
            print("-" * 78)
            print("%s %s" % (cur, titles.get(cur, "")))
        print("  %-4s %-22s %s" % (r["verdict"], r["name"], r["detail"]))
    print("-" * 78)
    if n_fail:
        print("종합: 🔴 FAIL %d건 · WARN %d건 — 위 FAIL 항목의 수집 경로부터 볼 것" % (n_fail, n_warn))
    elif n_warn:
        print("종합: ⚠ WARN %d건 (FAIL 0) — 경고는 판정이 아니다. 추세로 볼 것" % n_warn)
    else:
        print("종합: ✅ 전부 통과 — 세 결함의 수집이 정상이다")
    if day < DEPLOY_DATE:
        print("ℹ %s 는 559차 배포(%s) 이전이다 — `unk_vol`·`*_measured` 는 n/a 가 정상이다."
              % (day, DEPLOY_DATE))
    print("⚠ 임계는 상단 사전등록값이다. 결과를 보고 고치지 말 것(458차 D6).")
    print("=" * 78)
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())

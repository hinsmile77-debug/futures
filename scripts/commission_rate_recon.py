# scripts/commission_rate_recon.py
# -*- coding: utf-8 -*-
"""[MW0601 493차 / F-1·F-2] 수수료율 실측 재검증 · 브로커 net 백필 · 영향 리포트.

**왜 이 스크립트가 존재하는가.**
2026-05-11 브로커를 키움 → Cybos로 바꾸면서 `FUTURES_COMMISSION_RATE`가 키움
값(편도 0.0015%)으로 남았다. 실제는 0.00981% — **6.54배**다. 그 결과 엔진 net
손익이 6개월간 낙관 편향됐고(6거래일 실측 −20만원 vs 실제 −70만원), 아무 계측도
그것을 짚지 못했다. 477차 EOD 대사가 `gross vs gross`만 비교했기 때문이다.

**핵심 관찰 — 정답지는 처음부터 로그에 있었다.**
CpTd6197 헤더의 `예탁현금`(idx=1)과 `익일가예탁현금`(idx=2)이 매분 수신·기록되고
있었고, 그 차이가 곧 **브로커 실현 순손익**이다. 없던 데이터가 아니라 아무도 안 본
데이터였다. 그래서 과거 24거래일을 로그만으로 소급 복원할 수 있다.

  브로커 실제 수수료 = gross(CpTd6197 실현손익) − (익일가예탁현금 − 예탁현금)
  약정대금          = Σ(entry_price + exit_price) × quantity × pt_value

서브커맨드
  --verify         요율 회귀·재검증 (26주 WFA 주기 항목). 기본 동작.
  --backfill       과거 SYSTEM 로그 → daily_broker_pnl 브로커 net 축 소급 적재.
  --impact         [F-3] 비용모델 요율 해제 시 왕복 비용 변화 규모.
  --rewrite-trades [명시 실행 전용] 과거 trades 행의 수수료/net을 실측 요율로 정정.
                   기동 시 자동으로는 절대 하지 않는다 — 과거 손익 재작성은
                   부수효과가 아니라 결정이어야 한다.

주의: 장중 실행 금지(CLAUDE.md 456차) — guard_intraday가 막는다.
"""
from __future__ import print_function

import argparse
import ast
import glob
import io
import os
import re
import sqlite3
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_utils import _get_pt_value_from_prefs                 # noqa: E402
from config.settings import (                                       # noqa: E402
    TRADES_DB, FUTURES_COMMISSION_RATE,
    COST_MODEL_COMMISSION_RATE, COST_MODEL_COMMISSION_RATE_PINNED,
    TICK_SIZE, VALIDATION_CAMPAIGN, ATR_HORIZON_TP1_MULT,
)
from utils.analysis_db import guard_intraday                        # noqa: E402

LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
_SUMMARY_RE = re.compile(r"summary=(\{.*\})\s*$")


def _scan_lines(lines):
    """한 날의 로그 줄들에서 (gross, 예탁현금, 익일가예탁현금)을 뽑는다.

    같은 날 여러 번 찍히므로 **마지막 값**을 쓴다 — 장중 값은 아직 체결이 안
    끝났을 수 있고, 마지막 것이 그날 확정치에 가장 가깝다.
    """
    dep = nxt = gross = None
    for line in lines:
        if "[CybosDailyPnl] account" not in line or "summary=" not in line:
            continue
        m = _SUMMARY_RE.search(line.strip())
        if not m:
            continue
        try:
            d = ast.literal_eval(m.group(1))
            dep = float(d.get("총매매", 0) or 0)
            nxt = float(d.get("총평가수익률", 0) or 0)   # 익일가예탁현금
            gross = float(d.get("실현손익", 0) or 0)
        except Exception:
            continue
    return gross, dep, nxt


def _iter_log_sources():
    """(날짜, 줄 이터러블) — **원본 로그 + 월 zip 압축본**을 모두 훑는다.

    🔴 **압축본을 반드시 읽어야 한다.** `SYSTEM`은 Tier B(압축) 채널이라
    `scripts/monthly_cleanup.py`가 30일 뒤 `YYYYMM_SYSTEM.zip`으로 묶고 원본을
    지운다(멤버명은 원본 파일명 그대로). 이 스크립트는 **26주 주기 재검증** 도구라
    소비 창이 30일을 반드시 넘으므로, `*_SYSTEM.log`만 glob하면 오래된 날이
    **조용히 사라진다** — 표본이 준 줄도 모르고 요율을 재보정하게 된다.
    (`tests/test_479_log_retention_tiers.py`가 이 실수를 자동 검출한다.)

    같은 날이 원본과 zip 양쪽에 있으면(압축 직후·삭제 전) **원본을 우선**한다.
    """
    seen = set()
    for path in sorted(glob.glob(os.path.join(LOG_DIR, "*_SYSTEM.log"))):
        base = os.path.basename(path)
        if not re.match(r"^\d{8}_SYSTEM\.log$", base):
            continue
        seen.add(base)
        with open(path, encoding="utf-8", errors="ignore") as fh:
            yield base[:8], fh

    for zpath in sorted(glob.glob(os.path.join(LOG_DIR, "*_SYSTEM.zip"))):
        try:
            with zipfile.ZipFile(zpath) as zf:
                for name in sorted(zf.namelist()):
                    base = os.path.basename(name)
                    if not re.match(r"^\d{8}_SYSTEM\.log$", base) or base in seen:
                        continue
                    seen.add(base)
                    with zf.open(name) as raw:
                        yield base[:8], io.TextIOWrapper(
                            raw, encoding="utf-8", errors="ignore")
        except (zipfile.BadZipFile, OSError) as exc:
            # 손상 아카이브를 조용히 건너뛰면 표본 손실이 은닉된다(계측 4원칙 ③).
            print("  [경고] 압축본 읽기 실패 — 그 달 표본이 빠진다: %s (%s)"
                  % (os.path.basename(zpath), exc), file=sys.stderr)


def _iter_broker_days():
    """날짜별 (gross, 예탁현금, 익일가예탁현금). 원본·압축본 모두 대상."""
    for stamp, lines in _iter_log_sources():
        date = "%s-%s-%s" % (stamp[:4], stamp[4:6], stamp[6:8])
        gross, dep, nxt = _scan_lines(lines)
        if dep:
            yield date, gross, dep, nxt


def _pt_value():
    """계약 승수 — **시스템과 같은 원천**(ui_prefs.json의 symbol_code)에서 얻는다.

    여기 상수를 박으면 안 된다. `config.constants.FUTURES_PT_VALUE`는 정규선물
    250,000이고 이 계좌가 쓰는 미니선물은 50,000이라, 잘못 쓰면 약정대금이 정확히
    5배가 되어 요율이 1/5로 나온다(개발 중 실제로 한 번 밟았다). 계측 4원칙 ①의
    단위 문제다 — 승수는 종목이 정한다.
    """
    return _get_pt_value_from_prefs()


def _notional_by_day():
    """trades.db 일자별 약정대금(편도 합)·레그수·계약수·엔진수수료."""
    pt = _pt_value()
    con = sqlite3.connect(TRADES_DB)
    con.row_factory = sqlite3.Row
    out = {}
    for r in con.execute(
            """SELECT date(entry_ts) d,
                      SUM((entry_price + exit_price) * quantity) px_sum,
                      COUNT(*) legs, SUM(quantity) contracts,
                      SUM(COALESCE(commission_krw, 0)) eng_comm
                 FROM trades
                WHERE entry_price IS NOT NULL AND exit_price IS NOT NULL
             GROUP BY 1"""):
        out[r["d"]] = {
            "notional": float(r["px_sum"] or 0.0) * pt,
            "legs": int(r["legs"] or 0),
            "contracts": int(r["contracts"] or 0),
            "engine_commission": float(r["eng_comm"] or 0.0),
        }
    con.close()
    return out


def _joined():
    nt = _notional_by_day()
    rows = []
    for date, gross, dep, nxt in _iter_broker_days():
        t = nt.get(date)
        if not t or t["notional"] <= 0:
            continue
        net = nxt - dep
        row = {"date": date, "gross": gross, "net": net,
               "actual_commission": gross - net,
               "deposit": dep, "next_deposit": nxt}
        row.update(t)
        rows.append(row)
    return rows


# 일자 요율이 중앙값에서 이 비율 이상 벗어나면 **오염일**로 보고 추정에서 뺀다.
# 5%는 요율 세대 오차(이번 건 554%)와 정상 잔차(반올림 ≤0.01%)를 가르는 폭이며,
# 실측 오염일들은 −194%~+257%로 이 문턱과 겹치지 않는다.
CONTAMINATED_DEVIATION = 0.05


def _split_clean(rows):
    """일자별 요율의 중앙값을 기준으로 정상일/오염일을 가른다.

    **왜 중앙값인가.** `예탁현금`(CpTd6197 idx=1)은 **당일 시가 고정**이라
    장중 입출금·미기록 체결이 있으면 `익일가 − 예탁` 차이에 수수료 아닌 금액이
    섞인다(실측: 2026-06-22는 음수 수수료 −0.0092%가 나왔다 — 수수료로는 불가능).
    그런 날을 합산에 넣으면 총합 방식이 통째로 끌려간다(전체 R² 0.56, 요율 +6.7%).
    중앙값은 소수 오염일에 흔들리지 않는다.

    ⚠ **오염일을 조용히 버리지 않는다** — 호출부가 목록·사유를 인쇄한다
    (계측 4원칙 ③ 탈락 가시화).
    """
    rated = [(r, r["actual_commission"] / r["notional"]) for r in rows if r["notional"] > 0]
    if not rated:
        return [], [], 0.0
    vals = sorted(v for _, v in rated)
    n = len(vals)
    med = vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2.0
    clean, dirty = [], []
    for r, v in rated:
        r["eff_rate"] = v
        (clean if med and abs(v / med - 1.0) <= CONTAMINATED_DEVIATION else dirty).append(r)
    return clean, dirty, med


# ---------------------------------------------------------------------------
def cmd_verify(args):
    rows = _joined()
    if not rows:
        print("표본 없음 — logs/ 의 SYSTEM 로그(원본+월 zip)와 trades.db 를 확인할 것")
        return 1
    clean, dirty, med = _split_clean(rows)
    if not clean:
        print("정상 표본 없음 — 전 일자가 중앙값에서 벗어난다. 원천을 먼저 점검할 것")
        return 1

    print("date        브로커gross  브로커net   실제수수료   약정대금(백만)  legs  ct   엔진수수료  실효요율%")
    tot_c = tot_n = 0.0
    for r in sorted(clean, key=lambda x: x["date"]):
        tot_c += r["actual_commission"]
        tot_n += r["notional"]
        print("%s %11.0f %10.0f %11.0f %14.1f %5d %4d %11.0f   %.6f"
              % (r["date"], r["gross"], r["net"], r["actual_commission"],
                 r["notional"] / 1e6, r["legs"], r["contracts"],
                 r["engine_commission"], r["eff_rate"] * 100.0))

    # ── 탈락 가시화 (계측 4원칙 ③) — 개수만 세지 말고 전부 인쇄한다 ──────────
    if dirty:
        print("")
        print("제외 %d일 / 전체 %d일 — 요율 중앙값에서 %.0f%% 초과 이탈:"
              % (len(dirty), len(rows), CONTAMINATED_DEVIATION * 100))
        for r in sorted(dirty, key=lambda x: x["date"]):
            print("  {}  실효 {:.6f}% (중앙값의 {:+.0f}%)  gross {:+,.0f}  net {:+,.0f}  "
                  "약정 {:,.0f}백만  legs {}  ct {}".format(
                      r["date"], r["eff_rate"] * 100.0,
                      (r["eff_rate"] / med - 1.0) * 100.0 if med else 0.0,
                      r["gross"], r["net"], r["notional"] / 1e6,
                      r["legs"], r["contracts"]))
        print("  추정 원인: `예탁현금`은 **당일 시가 고정**이라 (a) 장중 입출금,")
        print("             (b) trades.db 미기록 체결(수동·복구 진입 → 약정대금 과소),")
        print("             (c) 마지막 TR 판독이 최종 정산 전 — 중 하나가 섞인 날이다.")
        print("             수수료로는 불가능한 **음수**가 나오면 (a)가 거의 확실하다.")
        print("  ⚠ 이 날들은 요율 추정에서만 뺀다 — 손익 집계에서 뺀다는 뜻이 아니다.")

    eff_rate = tot_c / tot_n if tot_n else 0.0
    print("")
    print("정상 %d일 / 전체 %d일  ·  총 실제수수료 %.0f원 / 총 약정대금 %.0f원"
          % (len(clean), len(rows), tot_c, tot_n))
    print("→ 실효 편도 요율 = %.9f  (%.6f%%)   [중앙값 %.6f%%]"
          % (eff_rate, eff_rate * 100.0, med * 100.0))
    print("→ 현행 라이브 상수 %.7f 대비 배수 = %.4f"
          % (FUTURES_COMMISSION_RATE, eff_rate / FUTURES_COMMISSION_RATE))

    # 고정비 성분 검정 — 순수 비례인지, 레그당 고정비가 있는지.
    # 있으면 요율 하나로는 못 맞으므로 상수 재보정만으로 끝나지 않는다.
    # ⚠ 정상일만 넣는다 — 오염일을 넣으면 그 잡음이 고정비 성분으로 잘못 잡힌다
    #   (실측: 전체 투입 시 레그당 +362원이라는 허위 고정비가 나왔다).
    try:
        import numpy as np
        y = np.array([r["actual_commission"] for r in clean], float)
        A2 = np.array([[r["notional"], r["legs"]] for r in clean], float)
        c2 = np.linalg.lstsq(A2, y, rcond=None)[0]
        A1 = np.array([[r["notional"]] for r in clean], float)
        c1 = np.linalg.lstsq(A1, y, rcond=None)[0]
        p1 = A1.dot(c1)
        ss = ((y - y.mean()) ** 2).sum()
        r2 = 1.0 - ((y - p1) ** 2).sum() / ss if ss else float("nan")
        print("")
        print("[1변수] comm = %.9f x 약정대금            R2=%.6f  최대잔차 %.1f원"
              % (c1[0], r2, abs(y - p1).max()))
        print("[2변수] comm = %.9f x 약정대금 + %.2f x 레그수   (고정비 성분)"
              % (c2[0], c2[1]))
        if abs(c2[1]) > 50.0:
            print("  경고: 레그당 고정비 성분이 유의하다 — 요율 상수 하나로는 재현 불가.")
    except ImportError:
        print("(numpy 없음 — 회귀 생략)")

    drift = abs(eff_rate / FUTURES_COMMISSION_RATE - 1.0)
    print("")
    if drift <= 0.02:
        print("판정: PASS — 라이브 상수가 실측 대비 ±2%% 이내 (편차 %.2f%%, 정상 %d일)"
              % (drift * 100, len(clean)))
        return 0
    print("판정: FAIL — 라이브 상수가 실측과 %.1f%% 어긋난다. "
          "FUTURES_COMMISSION_RATE 재보정 필요." % (drift * 100))
    print("      재보정 시 불연속 마커(strategy_events METRIC_REDEFINITION)를 함께 남길 것.")
    return 2


def cmd_backfill(args):
    """과거 로그 → daily_broker_pnl 브로커 net 축 소급 적재."""
    from utils.db_utils import (init_daily_broker_pnl_db, upsert_broker_net,
                                fetch_broker_net)
    init_daily_broker_pnl_db()
    n_new = n_skip = 0
    for date, gross, dep, nxt in _iter_broker_days():
        if fetch_broker_net(date) is not None and not args.force:
            n_skip += 1
            continue
        upsert_broker_net(date, dep, nxt)
        got = fetch_broker_net(date)
        if got is None:
            # is_krx_trading_date 가드에 걸린 날(비거래일) — 정상 스킵
            n_skip += 1
            continue
        n_new += 1
        eng = got["engine_commission_krw"]
        print("%s  gross %+10.0f  net %+10.0f  실제수수료 %9.0f  (엔진 %s)"
              % (date, got["gross_krw"], got["net_krw"], got["commission_krw"],
                 ("%.0f" % eng) if eng is not None else "미기입"))
    print("")
    print("적재 %d일 / 스킵 %d일" % (n_new, n_skip))
    return 0


def _round_trip_cost_pt(price, rate, slip_ticks):
    return 2.0 * price * rate + 2.0 * slip_ticks * TICK_SIZE


def cmd_impact(args):
    """[F-3] 비용모델 요율 핀 해제 시 무엇이 얼마나 움직이는가."""
    slip = float(VALIDATION_CAMPAIGN.get("slippage_ticks_per_side", 1.0))
    price = args.price
    pinned = _round_trip_cost_pt(price, COST_MODEL_COMMISSION_RATE, slip)
    live = _round_trip_cost_pt(price, FUTURES_COMMISSION_RATE, slip)
    print("비용모델 요율 상태: %s"
          % ("핀(PINNED)" if COST_MODEL_COMMISSION_RATE_PINNED else "해제(라이브와 동기)"))
    print("  COST_MODEL_COMMISSION_RATE = %.7f (%.5f%%)"
          % (COST_MODEL_COMMISSION_RATE, COST_MODEL_COMMISSION_RATE * 100))
    print("  FUTURES_COMMISSION_RATE    = %.7f (%.5f%%)"
          % (FUTURES_COMMISSION_RATE, FUTURES_COMMISSION_RATE * 100))
    print("")
    print("왕복 비용(pt) @ price=%.0f, 슬리피지 %.1f틱/편도" % (price, slip))
    print("  현행(핀)  = 2x%.0fx%.7f + 2x%.1fx%.2f = %.4f pt"
          % (price, COST_MODEL_COMMISSION_RATE, slip, TICK_SIZE, pinned))
    print("  해제 후   = 2x%.0fx%.7f + 2x%.1fx%.2f = %.4f pt"
          % (price, FUTURES_COMMISSION_RATE, slip, TICK_SIZE, live))
    print("  → %.2f배 (%+.4f pt)"
          % (live / pinned if pinned else float("nan"), live - pinned))
    print("")
    print("TP1 목표 대비 비용 잠식률 (호라이즌별 ATR x 배수, ATR 중앙값 %.3fpt 가정)" % args.atr)
    for hz, mult in sorted(ATR_HORIZON_TP1_MULT.items(), key=lambda kv: kv[1]):
        tp1 = args.atr * mult
        print("  %-4s TP1=%.3fpt  현행 %5.1f%%  →  해제 후 %5.1f%%"
              % (hz, tp1, pinned / tp1 * 100 if tp1 else 0,
                 live / tp1 * 100 if tp1 else 0))
    print("")
    print("해제는 주간회의 승인 사항이다. 사전등록 합격선은 무변경이지만")
    print("측정값이 바뀌어 채널 verdict가 일괄 이동한다(461차 mdd_pct 유형).")
    return 0


def cmd_rewrite_trades(args):
    """[명시 실행 전용] 과거 trades 행의 수수료/net을 실측 요율로 정정."""
    from utils.db_utils import normalize_trade_pnl
    con = sqlite3.connect(TRADES_DB)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """SELECT id, entry_price, quantity, pnl_pts, forward_pnl_pts,
                  commission_krw, net_pnl_krw, commission_rate_used
             FROM trades
            WHERE pnl_pts IS NOT NULL
              AND (commission_rate_used IS NULL OR commission_rate_used <> ?)""",
        (FUTURES_COMMISSION_RATE,)).fetchall()
    if not rows:
        print("정정 대상 없음 — 모든 행이 이미 %.7f 요율이다." % FUTURES_COMMISSION_RATE)
        con.close()
        return 0
    d_comm = d_net = 0.0
    for r in rows:
        m = normalize_trade_pnl(entry_price=r["entry_price"], quantity=r["quantity"],
                                pnl_pts=r["pnl_pts"], pt_value=_pt_value(),
                                commission_rate=FUTURES_COMMISSION_RATE)
        d_comm += m["commission_krw"] - float(r["commission_krw"] or 0.0)
        d_net += m["net_pnl_krw"] - float(r["net_pnl_krw"] or 0.0)
    # ⚠ `%` 연산자는 콤마 플래그를 지원하지 않는다 — `format()`으로 먼저 문자열을
    #   만든다. 종전 `%+,.0f`는 실행 즉시 ValueError로 죽었다(F-Y와 같은 결함;
    #   `tests/test_493_percent_format_comma.py`가 이 커밋에서 잡아냈다).
    print("대상 {}행 — 수수료 {}원 / net {}원 변동 예정".format(
        len(rows), format(d_comm, "+,.0f"), format(d_net, "+,.0f")))
    if not args.yes:
        print("")
        print("실제로 쓰려면 --yes 를 붙일 것. (백업 권장: data/db/trades.db 복사)")
        con.close()
        return 0
    for r in rows:
        m = normalize_trade_pnl(entry_price=r["entry_price"], quantity=r["quantity"],
                                pnl_pts=r["pnl_pts"], pt_value=_pt_value(),
                                commission_rate=FUTURES_COMMISSION_RATE)
        fwd_pts = r["forward_pnl_pts"] if r["forward_pnl_pts"] is not None else r["pnl_pts"]
        f = normalize_trade_pnl(entry_price=r["entry_price"], quantity=r["quantity"],
                                pnl_pts=fwd_pts, pt_value=_pt_value(),
                                commission_rate=FUTURES_COMMISSION_RATE)
        con.execute(
            """UPDATE trades
                  SET commission_krw = ?, net_pnl_krw = ?, pnl_krw = ?,
                      forward_commission_krw = ?, forward_net_pnl_krw = ?,
                      forward_pnl_krw = ?, commission_rate_used = ?
                WHERE id = ?""",
            (m["commission_krw"], m["net_pnl_krw"], m["net_pnl_krw"],
             f["commission_krw"], f["net_pnl_krw"], f["net_pnl_krw"],
             FUTURES_COMMISSION_RATE, r["id"]))
    con.commit()
    con.close()
    print("정정 완료 %d행. strategy_events 마커와 DECISION_LOG 기록을 남길 것." % len(rows))
    return 0


def main():
    ap = argparse.ArgumentParser(description="수수료율 실측 재검증 · 브로커 net 백필")
    ap.add_argument("--verify", action="store_true", help="요율 회귀·재검증 (기본)")
    ap.add_argument("--backfill", action="store_true", help="과거 로그 → 브로커 net 적재")
    ap.add_argument("--impact", action="store_true", help="[F-3] 비용모델 해제 영향")
    ap.add_argument("--rewrite-trades", action="store_true", dest="rewrite",
                    help="[명시] 과거 trades 수수료/net 소급 정정")
    ap.add_argument("--yes", action="store_true", help="--rewrite-trades 실제 반영")
    ap.add_argument("--force", action="store_true", help="--backfill 시 기존 값도 덮어씀")
    ap.add_argument("--price", type=float, default=1040.0, help="--impact 기준가")
    ap.add_argument("--atr", type=float, default=3.371, help="--impact ATR 중앙값(pt)")
    args = ap.parse_args()

    guard_intraday("commission_rate_recon")

    if args.backfill:
        return cmd_backfill(args)
    if args.impact:
        return cmd_impact(args)
    if args.rewrite:
        return cmd_rewrite_trades(args)
    return cmd_verify(args)


if __name__ == "__main__":
    sys.exit(main())

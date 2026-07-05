# scripts/analyze_mae_mfe.py
"""
[260704 감사 P1] MAE/MFE 기반 배리어(손절/TP) 재산정 진단.

trades.db 전 체결 이력의 실제 가격 경로(raw_candles high/low)를 복원해:
  - MAE(Maximum Adverse Excursion): 보유 중 가장 불리했던 역행폭
  - MFE(Maximum Favorable Excursion): 보유 중 가장 유리했던 순행폭
를 계산하고, 현재 ATR_STOP_MULT·ATR_HORIZON_TP1_MULT 배수가 실측 분포에 비해
과소/과대한지 진단한다. 승리 거래의 MFE 중앙값(TP 근거), 패배 거래의 MAE 분포
(스톱 근거) — 감사 §3-3 P1 항목.

추가로 청산 이후(사후) 가격 경로를 봐서:
  - 손절 거래: 손절 이후 가격이 진입가를 회복했는지 (스톱이 너무 타이트했는가)
  - TP 거래: TP 이후 추가로 얼마나 더 유리하게 갔는지 (TP가 너무 보수적인가)
를 함께 보고한다.

이 스크립트는 읽기 전용 진단이다 — 배리어 값을 자동으로 바꾸지 않는다.
결과를 보고 사용자가 직접 config/settings.py 값을 조정할 것.

실행:
    python scripts/analyze_mae_mfe.py [--days 90] [--lookforward 15]
"""
import argparse
import datetime
import sqlite3
import sys
from pathlib import Path
from typing import List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Windows 콘솔 cp949 코드페이지에서 한글 출력 시 UnicodeEncodeError 방지
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config.settings import (
    TRADES_DB, RAW_DATA_DB, ATR_STOP_MULT, ATR_HORIZON_TP1_MULT, ATR_TP1_MULT, DATA_DIR,
)

_REPORT_LINES: List[str] = []


def out(msg: str = "") -> None:
    """콘솔 출력 + 리포트 라인 누적(파일 저장용). 콘솔 인코딩 실패는 무시."""
    _REPORT_LINES.append(msg)
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("utf-8", errors="replace").decode("ascii", errors="replace"))

LOOKFORWARD_MIN_DEFAULT = 15
_STOP_KEYWORDS = ("손절", "하드스톱", "트레일링스톱")
_TP_KEYWORDS = ("TP",)


def _fmt_ts(dt: datetime.datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _parse_ts(ts: str) -> datetime.datetime:
    return datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")


def load_trades(days_back: Optional[int] = None) -> List[sqlite3.Row]:
    conn = sqlite3.connect(TRADES_DB, timeout=10)
    conn.row_factory = sqlite3.Row
    q = """SELECT entry_ts, exit_ts, direction, entry_price, exit_price, quantity,
                  exit_reason, grade, entry_horizon, COALESCE(net_pnl_krw, pnl_krw) AS net_pnl_krw
           FROM trades
           WHERE exit_ts IS NOT NULL AND entry_price IS NOT NULL AND exit_price IS NOT NULL"""
    params: Tuple = ()
    if days_back:
        cutoff = (datetime.date.today() - datetime.timedelta(days=days_back)).isoformat()
        q += " AND entry_ts >= ?"
        params = (cutoff + " 00:00:00",)
    q += " ORDER BY entry_ts"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return rows


def load_candle_path(conn, start_ts: str, end_ts: str) -> List[Tuple[float, float]]:
    """[(high, low), ...] — start_ts < ts <= end_ts (진입봉 자체는 진입가 기준이므로 제외)."""
    rows = conn.execute(
        "SELECT high, low FROM raw_candles WHERE ts > ? AND ts <= ? ORDER BY ts",
        (start_ts, end_ts),
    ).fetchall()
    return [(float(r[0]), float(r[1])) for r in rows]


def load_entry_atr(conn, entry_ts: str) -> float:
    import json
    row = conn.execute(
        "SELECT features FROM raw_features WHERE ts = ?", (entry_ts,)
    ).fetchone()
    if not row or not row[0]:
        return 0.0
    try:
        fd = json.loads(row[0])
    except (ValueError, TypeError):
        return 0.0
    return float(fd.get("atr", 0.0) or 0.0)


def compute_mae_mfe(direction: str, entry_price: float, path: List[Tuple[float, float]]) -> Tuple[float, float]:
    mfe = 0.0
    mae = 0.0
    for hi, lo in path:
        if direction == "LONG":
            mfe = max(mfe, hi - entry_price)
            mae = max(mae, entry_price - lo)
        else:
            mfe = max(mfe, entry_price - lo)
            mae = max(mae, hi - entry_price)
    return mfe, mae


def percentile(values: List[float], p: float) -> float:
    if not values:
        return float("nan")
    import numpy as np
    return float(np.percentile(values, p))


def classify_exit(reason: str) -> str:
    if any(k in reason for k in _STOP_KEYWORDS):
        return "stop"
    if any(k in reason for k in _TP_KEYWORDS):
        return "tp"
    return "other"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=None, help="최근 N일만 분석 (기본: 전체)")
    parser.add_argument("--lookforward", type=int, default=LOOKFORWARD_MIN_DEFAULT,
                         help="청산 이후 사후분석 분 (기본 15)")
    args = parser.parse_args()

    trades = load_trades(args.days)
    if not trades:
        print("분석할 체결 이력이 없습니다.")
        return

    raw_conn = sqlite3.connect(RAW_DATA_DB, timeout=10)

    win_mfe, lose_mae = [], []
    stop_recovery_pts = []   # 손절 이후 사후 회복폭 (진입가 대비, +면 회복)
    tp_extra_pts = []        # TP 이후 사후 추가 유리폭
    n_skipped = 0

    for t in trades:
        direction = t["direction"]
        entry_price = float(t["entry_price"])
        exit_ts = t["exit_ts"]
        entry_ts = t["entry_ts"]
        pnl = float(t["net_pnl_krw"] or 0.0)
        reason = t["exit_reason"] or ""

        path_held = load_candle_path(raw_conn, entry_ts, exit_ts)
        if not path_held:
            n_skipped += 1
            continue
        mfe, mae = compute_mae_mfe(direction, entry_price, path_held)

        if pnl > 0:
            win_mfe.append(mfe)
        elif pnl < 0:
            lose_mae.append(mae)

        kind = classify_exit(reason)
        if kind == "stop":
            try:
                fwd_end = _fmt_ts(_parse_ts(exit_ts) + datetime.timedelta(minutes=args.lookforward))
                path_after = load_candle_path(raw_conn, exit_ts, fwd_end)
                if path_after:
                    # LONG: 이후 최고가가 진입가를 얼마나 넘었는가 (+면 회복/재상승)
                    if direction == "LONG":
                        best = max(hi for hi, _ in path_after)
                        stop_recovery_pts.append(best - entry_price)
                    else:
                        best = min(lo for _, lo in path_after)
                        stop_recovery_pts.append(entry_price - best)
            except Exception:
                pass
        elif kind == "tp":
            try:
                fwd_end = _fmt_ts(_parse_ts(exit_ts) + datetime.timedelta(minutes=args.lookforward))
                path_after = load_candle_path(raw_conn, exit_ts, fwd_end)
                if path_after:
                    exit_price = float(t["exit_price"])
                    if direction == "LONG":
                        best = max(hi for hi, _ in path_after)
                        tp_extra_pts.append(best - exit_price)
                    else:
                        best = min(lo for _, lo in path_after)
                        tp_extra_pts.append(exit_price - best)
            except Exception:
                pass

    raw_conn.close()

    out("=" * 64)
    out(f"  MAE/MFE 분석 — 체결 {len(trades)}건 (경로 결측 {n_skipped}건 제외)")
    out("=" * 64)

    out(f"\n[승리 거래 MFE 분포] n={len(win_mfe)}")
    if win_mfe:
        for p in (25, 50, 75, 90):
            out(f"  P{p}: {percentile(win_mfe, p):.2f}pt")
        out(f"  → 참고: 현재 TP1 배수 = ATR × {ATR_TP1_MULT} (entry_horizon 미지정 시)")
        for hz, mult in ATR_HORIZON_TP1_MULT.items():
            out(f"    {hz}: ATR × {mult}")
    else:
        out("  데이터 부족")

    out(f"\n[패배 거래 MAE 분포] n={len(lose_mae)}")
    if lose_mae:
        for p in (25, 50, 75, 90):
            out(f"  P{p}: {percentile(lose_mae, p):.2f}pt")
        out(f"  → 참고: 현재 하드스톱 배수 = ATR × {ATR_STOP_MULT}")
    else:
        out("  데이터 부족")

    out(f"\n[손절 이후 {args.lookforward}분 사후 회복폭] n={len(stop_recovery_pts)}")
    if stop_recovery_pts:
        recovered = sum(1 for v in stop_recovery_pts if v > 0)
        out(f"  회복(진입가 재돌파) 비율: {recovered}/{len(stop_recovery_pts)} "
            f"({100.0 * recovered / len(stop_recovery_pts):.1f}%)")
        for p in (50, 75, 90):
            out(f"  P{p}: {percentile(stop_recovery_pts, p):+.2f}pt")
        out("  → 비율이 높으면 하드스톱이 과소(too tight) — 배수 상향 검토")
    else:
        out("  손절 거래 없음 또는 사후 데이터 없음")

    out(f"\n[TP 이후 {args.lookforward}분 사후 추가 유리폭] n={len(tp_extra_pts)}")
    if tp_extra_pts:
        left_on_table = sum(1 for v in tp_extra_pts if v > 0)
        out(f"  추가 유리 비율: {left_on_table}/{len(tp_extra_pts)} "
            f"({100.0 * left_on_table / len(tp_extra_pts):.1f}%)")
        for p in (50, 75, 90):
            out(f"  P{p}: {percentile(tp_extra_pts, p):+.2f}pt")
        out("  → 비율/폭이 크면 TP가 과소(조기 익절) — 배수 상향 검토")
    else:
        out("  TP 거래 없음 또는 사후 데이터 없음")

    out("\n" + "=" * 64)
    out("  이 진단은 배리어 값을 자동으로 바꾸지 않습니다.")
    out("  분기 1회 재실행 권장 — config/settings.py 조정은 사용자 판단으로 수동 반영.")
    out("=" * 64)

    report_path = Path(DATA_DIR) / "mae_mfe_report.txt"
    try:
        report_path.write_text("\n".join(_REPORT_LINES), encoding="utf-8")
        out(f"\n리포트 저장: {report_path}")
    except Exception as e:
        out(f"리포트 저장 실패: {e}")


if __name__ == "__main__":
    main()

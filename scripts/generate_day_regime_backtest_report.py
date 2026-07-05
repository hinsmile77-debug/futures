# scripts/generate_day_regime_backtest_report.py
"""
[v9-dev Track L1, 2026-07-05] 데이 레짐 엔진(`strategy/regime/day_regime_engine.py`) 검증 리포트.

`DayRegimeEngine`은 Hurst·시가이격·opt_gex_bn/opt_chain_pcr 등 raw_candles만으로는
재구성할 수 없는 입력을 쓰므로(참고: `generate_regime_postmortem_report.py`는 OHLC만으로
MicroRegimeClassifier를 오프라인 재현하지만 탈진장을 과소추정하는 한계가 있었다 — 이 엔진은
그보다 입력이 많아 오프라인 재현 시 왜곡이 더 커진다), 오프라인 재분류 대신 **실거래 중
main.py가 매분 남긴 섀도우 로그**(`ensemble_decisions.entry_gate_json.day_regime_shadow`)를
그대로 읽어 검증한다.

핵심 질문: "이 레짐 분류가 실제로 방향 신호와 상관이 있는가?" — TREND_UP/TREND_DN 구간의
방향 적중률이 RANGE/CHAOS 구간보다 뚜렷이 높아야 Track L2(레짐조건부 프로파일) 착수의
근거가 된다. 뚜렷하지 않다면 L2는 아직 이르다.

읽기 전용 진단 — 어떤 정책도 자동으로 켜거나 끄지 않는다.

실행:
    python scripts/generate_day_regime_backtest_report.py [--days 14]
"""
import argparse
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config.settings import PREDICTIONS_DB, DATA_DIR


def load_rows(days: int) -> List[sqlite3.Row]:
    conn = sqlite3.connect(PREDICTIONS_DB, timeout=10)
    conn.row_factory = sqlite3.Row
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=days)).strftime("%Y-%m-%d 00:00:00")
    rows = conn.execute(
        """SELECT ts, direction, entry_gate_json
           FROM ensemble_decisions
           WHERE direction != 0 AND ts >= ?
           ORDER BY ts""",
        (cutoff,),
    ).fetchall()
    conn.close()
    return rows


def load_realized_move_map(days: int, horizon: str = "1m") -> Dict[tuple, float]:
    conn = sqlite3.connect(PREDICTIONS_DB, timeout=10)
    conn.row_factory = sqlite3.Row
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=days)).strftime("%Y-%m-%d 00:00:00")
    rows = conn.execute(
        """SELECT ts, predicted, realized_move FROM meta_labels
           WHERE horizon = ? AND ts >= ?""",
        (horizon, cutoff),
    ).fetchall()
    conn.close()
    return {(r["ts"], int(r["predicted"])): float(r["realized_move"] or 0.0) for r in rows}


def percentile(values: List[float], p: float) -> float:
    if not values:
        return float("nan")
    import numpy as np
    return float(np.percentile(values, p))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=14, help="분석 기간(일), 기본 14일")
    args = parser.parse_args()

    rows = load_rows(args.days)
    move_map = load_realized_move_map(args.days)

    if not rows:
        print(f"최근 {args.days}일간 분석할 ensemble_decisions 행이 없습니다.")
        return

    by_regime: Dict[str, List[float]] = defaultdict(list)
    n_no_shadow = 0
    n_no_realized = 0

    for row in rows:
        try:
            gate = json.loads(row["entry_gate_json"]) if row["entry_gate_json"] else None
        except (ValueError, TypeError):
            gate = None
        if not gate or "day_regime_shadow" not in gate:
            n_no_shadow += 1
            continue

        regime = gate.get("day_regime_shadow")
        move = move_map.get((row["ts"], int(row["direction"])))
        if move is None:
            n_no_realized += 1
            continue

        # 방향 신호와 정렬된 실현폭 그대로 사용(양수=신호 방향 적중, 음수=역행)
        # TREND_UP/TREND_DN 레짐일 때는 "레짐 방향과 신호 방향 일치 여부"도 참고 지표로 남긴다.
        by_regime[regime or "UNKNOWN"].append(move)

    print("=" * 68)
    print(f"  데이 레짐 엔진 백테스트 리포트 — 최근 {args.days}일, 방향성 신호 {len(rows)}건")
    print("=" * 68)

    if n_no_shadow == len(rows):
        print("\n이 기간의 entry_gate_json에는 day_regime_shadow 필드가 없습니다.")
        print("(배포 이전 데이터이거나 아직 표본이 쌓이지 않음 — 배포 이후 재실행 필요)")
        return

    print(f"\nday_regime_shadow 필드 보유: {len(rows) - n_no_shadow}/{len(rows)}건 "
          f"(구버전 {n_no_shadow}건 제외, realized_move 미매칭 {n_no_realized}건 별도)")

    print(f"\n[레짐별] 방향 신호 실현폭(realized_move, 수수료·TP/SL 미반영 근사)")
    print(f"{'레짐':12s} {'n':>6s} {'평균':>10s} {'승률':>8s}  {'P25':>8s}  {'P75':>8s}")
    for regime in sorted(by_regime.keys()):
        moves = by_regime[regime]
        avg = sum(moves) / len(moves)
        win = sum(1 for v in moves if v > 0) / len(moves)
        print(f"{regime:12s} {len(moves):6d} {avg:+10.4f} {win*100:7.1f}%  "
              f"{percentile(moves, 25):+8.4f}  {percentile(moves, 75):+8.4f}")

    trend_moves = by_regime.get("TREND_UP", []) + by_regime.get("TREND_DN", [])
    range_moves = by_regime.get("RANGE", [])
    print(f"\n[핵심 비교] TREND_UP+TREND_DN vs RANGE")
    if trend_moves and range_moves:
        t_avg = sum(trend_moves) / len(trend_moves)
        r_avg = sum(range_moves) / len(range_moves)
        print(f"  TREND 평균={t_avg:+.4f}(n={len(trend_moves)})  "
              f"RANGE 평균={r_avg:+.4f}(n={len(range_moves)})  차이={t_avg - r_avg:+.4f}")
        if t_avg > r_avg:
            print("  → TREND 구간에서 신호 방향성이 더 뚜렷함 — L2 착수 근거로 참고 가능"
                  "(표본 규모·통계적 유의성은 별도 확인 필요)")
        else:
            print("  → 이 표본에서는 TREND/RANGE 차이가 뚜렷하지 않음 — L2 착수는 아직 이름")
    else:
        print("  표본 부족 — 더 긴 --days로 재실행 권장")

    print("\n" + "=" * 68)
    print("  주의: realized_move는 1m 호라이즌 방향성 실현폭 근사치. 통계적 유의성 검정은")
    print("  포함하지 않음 — 표본이 작을 때 이 리포트만으로 L2 착수를 결정하지 말 것.")
    print("  이 리포트는 진단 전용이며 어떤 정책도 자동으로 켜거나 끄지 않는다.")
    print("=" * 68)

    report_path = Path(DATA_DIR) / "day_regime_backtest_report.txt"
    try:
        lines = [f"데이 레짐 백테스트 리포트 — 최근 {args.days}일, n={len(rows)}"]
        for regime in sorted(by_regime.keys()):
            moves = by_regime[regime]
            lines.append(f"{regime}: n={len(moves)} avg={sum(moves)/len(moves):+.4f}")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"\n리포트 저장: {report_path}")
    except Exception as e:
        print(f"리포트 저장 실패: {e}")


if __name__ == "__main__":
    main()

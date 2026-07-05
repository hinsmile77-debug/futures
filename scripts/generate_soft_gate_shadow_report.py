# scripts/generate_soft_gate_shadow_report.py
"""
[v9-dev Track L3, 2026-07-05] 소프트게이트 점수화 섀도우 리포트.

`strategy/entry/soft_gate_scorer.py`(SoftGateScorer)가 매분 실거래 판정과 병렬로 남긴
`entry_gate_json.soft_gate_shadow_*` 필드를 읽어, "체크리스트+4종 오버라이드 직렬 AND"
대신 점수합산이었다면 무엇이 달라졌을지 집계한다.

핵심 질문: qty_ok=False(직렬 AND가 실제로 차단)인데 soft_gate_shadow_grade가 X가 아닌
(=점수합산이었다면 통과했을) 신호가 실제로 방향성이 있었는가? — 이 표가 쌓여야
Track L3의 승격 여부(합격선은 아직 미확정, mireuki_v9_구현계획_v3_2026-07-05.md §2 참고)를
판단할 수 있다.

이 스크립트는 읽기 전용 진단이며, 어떤 게이트도 자동으로 켜거나 끄지 않는다.

실행:
    python scripts/generate_soft_gate_shadow_report.py [--days 7]
"""
import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional

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
        """SELECT ts, direction, entry_gate_json, entry_final_ok, entry_qty
           FROM ensemble_decisions
           WHERE direction != 0 AND ts >= ?
           ORDER BY ts""",
        (cutoff,),
    ).fetchall()
    conn.close()
    return rows


def load_realized_move_map(days: int, horizon: str = "1m") -> Dict[tuple, float]:
    """{(ts, predicted): realized_move} — meta_labels 기준(learning/meta_labeling.py 산출)."""
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


def parse_gate(row: sqlite3.Row) -> Optional[Dict]:
    try:
        return json.loads(row["entry_gate_json"]) if row["entry_gate_json"] else None
    except (ValueError, TypeError):
        return None


def percentile(values: List[float], p: float) -> float:
    if not values:
        return float("nan")
    import numpy as np
    return float(np.percentile(values, p))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=7, help="분석 기간(일), 기본 7일(주간)")
    args = parser.parse_args()

    rows = load_rows(args.days)
    move_map = load_realized_move_map(args.days)

    if not rows:
        print(f"최근 {args.days}일간 분석할 ensemble_decisions 행이 없습니다.")
        return

    n_no_shadow = 0        # soft_gate_shadow 필드 자체가 없는 구버전 행(배포 이전)
    n_blocked_now = 0      # 직렬 AND가 실제로 차단(qty_ok=False)한 행
    n_would_pass = 0       # 그 중 soft_gate_shadow_grade가 X가 아니었던 행(점수합산이면 통과)
    would_pass_moves: List[float] = []
    n_no_realized = 0

    # 참고 대조군: 직렬 AND도 통과 + 소프트게이트도 A/B/C였던 행(둘이 일치하는 정상 케이스)
    both_pass_moves: List[float] = []

    for row in rows:
        gate = parse_gate(row)
        if not gate or "soft_gate_shadow_grade" not in gate:
            n_no_shadow += 1
            continue

        qty_ok = bool(gate.get("qty_ok", False))
        soft_grade = gate.get("soft_gate_shadow_grade")
        move = move_map.get((row["ts"], int(row["direction"])))

        if not qty_ok:
            n_blocked_now += 1
            if soft_grade and soft_grade != "X":
                n_would_pass += 1
                if move is not None:
                    would_pass_moves.append(move)
                else:
                    n_no_realized += 1
        else:
            if soft_grade and soft_grade != "X" and move is not None:
                both_pass_moves.append(move)

    print("=" * 68)
    print(f"  소프트게이트 점수화 섀도우 리포트 — 최근 {args.days}일, 방향성 신호 {len(rows)}건")
    print("=" * 68)

    if n_no_shadow == len(rows):
        print("\n이 기간의 entry_gate_json에는 soft_gate_shadow 필드가 없습니다.")
        print("(배포 이전 데이터이거나 아직 표본이 쌓이지 않음 — 배포 이후 재실행 필요)")
        return

    print(f"\nsoft_gate_shadow 필드 보유: {len(rows) - n_no_shadow}/{len(rows)}건 "
          f"(구버전 {n_no_shadow}건 제외)")
    print(f"직렬 AND 실제 차단(qty_ok=False): {n_blocked_now}건")
    print(f"  ↳ 소프트게이트였다면 통과(soft_grade != X): {n_would_pass}건 "
          f"({n_would_pass / n_blocked_now * 100:.1f}%)" if n_blocked_now else "")

    print(f"\n[핵심 지표] 직렬 AND가 막았지만 소프트게이트라면 통과했을 신호의 실현 방향성")
    if would_pass_moves:
        avg = sum(would_pass_moves) / len(would_pass_moves)
        win = sum(1 for v in would_pass_moves if v > 0) / len(would_pass_moves)
        print(f"  n={len(would_pass_moves)}  평균={avg:+.4f}  승률={win*100:.1f}%  "
              f"P25={percentile(would_pass_moves, 25):+.4f}  "
              f"P75={percentile(would_pass_moves, 75):+.4f}")
        print(f"  (realized_move 미매칭 {n_no_realized}건 별도)")
    else:
        print(f"  표본 없음 (realized_move 미매칭 {n_no_realized}건)")

    print(f"\n[대조군] 직렬 AND·소프트게이트 둘 다 통과한 정상 케이스")
    if both_pass_moves:
        avg2 = sum(both_pass_moves) / len(both_pass_moves)
        win2 = sum(1 for v in both_pass_moves if v > 0) / len(both_pass_moves)
        print(f"  n={len(both_pass_moves)}  평균={avg2:+.4f}  승률={win2*100:.1f}%")
    else:
        print("  표본 없음")

    print("\n" + "=" * 68)
    print("  주의: realized_move는 1m 호라이즌 방향성 실현폭(수수료·TP/SL 미반영) 근사치.")
    print("  이 리포트는 진단 전용 — Track L3 승격 합격선은 아직 사전등록되지 않았음")
    print("  (mireuki_v9_구현계획_v3_2026-07-05.md §2, dev VALIDATION_CAMPAIGN 원칙과 동일).")
    print("  표본이 더 쌓인 뒤 별도 세션에서 합격선을 확정할 것 — 이 스크립트가 자동으로")
    print("  게이트를 켜거나 끄지 않는다.")
    print("=" * 68)

    report_path = Path(DATA_DIR) / "soft_gate_shadow_report.txt"
    try:
        lines = [
            f"소프트게이트 섀도우 리포트 — 최근 {args.days}일, n={len(rows)}",
            f"직렬AND 차단 {n_blocked_now}건 중 소프트게이트 통과 {n_would_pass}건",
        ]
        if would_pass_moves:
            lines.append(
                f"would_pass: n={len(would_pass_moves)} "
                f"avg={sum(would_pass_moves)/len(would_pass_moves):+.4f}"
            )
        report_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"\n리포트 저장: {report_path}")
    except Exception as e:
        print(f"리포트 저장 실패: {e}")


if __name__ == "__main__":
    main()

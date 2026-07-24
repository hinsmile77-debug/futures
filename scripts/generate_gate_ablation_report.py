# scripts/generate_gate_ablation_report.py
"""
[260704 감사 P1] 게이트/레이어 ablation 주간 리포트.

"이 게이트만 없었으면 진입했을 거래"의 가상 손익(방향성 실현폭, 수수료 미반영)을
집계해 신호품질 게이트별 기여도를 진단한다. 감사 근거:
docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md §2-3 P1, §7-3.

"게이트 과잉... 각각은 사고의 사후 대응으로 정당하나, 총합의 한계 기여를 아무도
모른다." → 이 스크립트는 매주(또는 필요 시) 실행해 각 게이트가 실제로 막은 신호가
그 이후 어느 쪽으로 움직였는지 집계한다. 읽기 전용 진단 — 게이트를 자동으로
끄거나 제거하지 않는다.

데이터 출처: predictions.db의 ensemble_decisions.entry_gate_json(STEP7 마스터 게이트
개별 결과) + meta_labels.realized_move(방향성 실현폭, learning/meta_labeling.py 산출).

방법: STEP7 게이트 딕셔너리에서 "이 게이트 하나만" False였던(다른 모든 게이트는 통과)
분봉을 골라, 같은 시각 1m 호라이즌의 realized_move를 이어붙인다 — "이 게이트가 없었으면
그 방향으로 진입했을 때의 가상 실현폭"의 근사치다. 실제 수수료·슬리피지·TP/SL 경로는
반영하지 않은 방향성 근사이므로 참고용으로만 쓸 것.

안전/운영 게이트(kill_switch·circuit breaker·broker_sync 등)는 분석 대상에서 제외한다
— 이들은 "기여가 없으면 제거"의 대상이 아니라 사고 대응으로 반드시 존치해야 하는
안전장치다. 신호품질 게이트(Hurst·ATR 범위·시가이격·거래량, MetaGate, ToxicityGate)만
분석한다.

실행:
    python scripts/generate_gate_ablation_report.py [--days 7]
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
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from config.settings import PREDICTIONS_DB, DATA_DIR

# entry_gate_json의 불리언 키 중 "안전/운영" 게이트 — ablation 랭킹에서 제외.
# 사고 대응으로 반드시 존치해야 하는 것들(감사 §7-8: 안전장치는 이 시스템의 자산).
_SAFETY_OPERATIONAL_GATES = {
    "cb_normal", "hc_ok", "broker_sync_ok", "integrity_ok", "kill_switch_ok",
    "cooldown_ok", "exit_cooldown_ok", "new_entry_time", "reverse_clamp_ok",
    "mode_filter_ok", "qty_ok", "intraday_ok", "armistice_ok", "ecb_observe_ok",
}

# 신호품질 게이트 — entry_gate_json 안에서 ablation 분석 대상.
# [297차] hurst_ok(횡보장 진입 차단)와 meta_gate(구형 하드차단, main.py의
# MetaGate.evaluate action=="skip" → X등급 강제)는 260705 검증 캠페인 문서
# §3-2b·§4-2에서 "매주 반드시 판독"으로 지정된 우선 순위 게이트 — 아래
# solo_blocked 집계에 이미 포함되어 있으므로 리포트 실행 후 이 둘부터 확인할 것.
_SIGNAL_QUALITY_GATES = {"hurst_ok", "atr_ok", "open_gap_ok", "bar_volume_ok"}


def load_rows(days: int) -> List[sqlite3.Row]:
    conn = sqlite3.connect(PREDICTIONS_DB, timeout=10)
    conn.row_factory = sqlite3.Row
    import datetime as _dt
    cutoff = (_dt.date.today() - _dt.timedelta(days=days)).strftime("%Y-%m-%d 00:00:00")
    rows = conn.execute(
        """SELECT ts, direction, entry_gate_json, meta_action, toxicity_action, entry_final_ok
           FROM ensemble_decisions
           WHERE direction != 0 AND ts >= ?
           ORDER BY ts""",
        (cutoff,),
    ).fetchall()
    conn.close()
    return rows


def load_realized_move_map(days: int, horizon: str = "1m") -> Dict[tuple, float]:
    """{(ts, predicted): realized_move} — meta_labels 기준 (learning/meta_labeling.py 산출)."""
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


def build_blockers(row: sqlite3.Row) -> Dict[str, bool]:
    """행 하나의 게이트별 차단 여부. True=이 게이트가 차단함."""
    blockers = {}
    try:
        gate_dict = json.loads(row["entry_gate_json"]) if row["entry_gate_json"] else {}
    except (ValueError, TypeError):
        gate_dict = {}
    for k, v in gate_dict.items():
        blockers[k] = (v is False)
    blockers["meta_gate"] = (str(row["meta_action"] or "") == "skip")
    blockers["toxicity_gate"] = (str(row["toxicity_action"] or "pass") not in ("pass", ""))
    return blockers


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

    # 게이트별: 이 게이트만 단독으로 차단한 케이스의 realized_move 목록
    solo_blocked: Dict[str, List[float]] = {}
    passed_moves: List[float] = []   # 비교 기준선 — 모든 게이트 통과(entry_final_ok=True) 신호
    n_no_realized = 0

    for row in rows:
        blockers = build_blockers(row)
        blocking_keys = [k for k, v in blockers.items() if v]
        move = move_map.get((row["ts"], int(row["direction"])))

        if not blocking_keys:
            if move is not None:
                passed_moves.append(move)
            else:
                n_no_realized += 1
            continue

        if len(blocking_keys) == 1:
            sole = blocking_keys[0]
            if sole in _SAFETY_OPERATIONAL_GATES:
                continue  # 안전/운영 게이트는 ablation 대상 아님
            if move is None:
                continue
            solo_blocked.setdefault(sole, []).append(move)

    print("=" * 64)
    print(f"  게이트 Ablation 리포트 — 최근 {args.days}일, 방향성 신호 {len(rows)}건")
    print("=" * 64)

    print(f"\n[기준선] 모든 게이트 통과 신호 realized_move — n={len(passed_moves)}")
    if passed_moves:
        avg_base = sum(passed_moves) / len(passed_moves)
        win_base = sum(1 for v in passed_moves if v > 0) / len(passed_moves)
        print(f"  평균={avg_base:+.4f}  승률={win_base * 100:.1f}%  "
              f"P25={percentile(passed_moves, 25):+.4f}  P75={percentile(passed_moves, 75):+.4f}")
    else:
        print("  데이터 없음")

    print(f"\n[신호품질 게이트별] 단독 차단 신호의 가상 realized_move")
    print(f"{'게이트':16s} {'n':>6s} {'평균':>10s} {'승률':>8s}  {'합계':>10s}  진단")
    if not solo_blocked:
        print("  단독 차단 사례가 이 기간에는 없습니다 (더 긴 --days로 재실행 권장)")
    for gate in sorted(_SIGNAL_QUALITY_GATES | {"meta_gate", "toxicity_gate"}):
        moves = solo_blocked.get(gate, [])
        if not moves:
            print(f"{gate:16s} {'0':>6s}  (단독 차단 사례 없음)")
            continue
        avg = sum(moves) / len(moves)
        win = sum(1 for v in moves if v > 0) / len(moves)
        total = sum(moves)
        verdict = (
            "차단 신호 평균 방향성 양호 — 이 게이트가 없었으면 이득이었을 가능성"
            if avg > 0 else
            "차단 신호 평균 방향성 불량 — 게이트가 실제로 나쁜 신호를 걸러냄"
        )
        print(f"{gate:16s} {len(moves):6d} {avg:+10.4f} {win * 100:7.1f}%  {total:+10.2f}  {verdict}")

    print("\n" + "=" * 64)
    print("  주의: realized_move는 1m 호라이즌 방향성 실현폭(수수료·TP/SL 미반영) 근사치.")
    print("  안전/운영 게이트(kill_switch·CB·broker_sync 등)는 분석 대상에서 제외했습니다.")
    print("  이 리포트는 게이트를 자동으로 끄거나 제거하지 않습니다 — 사용자 검토 후 결정.")
    print("=" * 64)

    report_path = Path(DATA_DIR) / "gate_ablation_report.txt"
    try:
        lines = []
        lines.append(f"게이트 Ablation 리포트 — 최근 {args.days}일, n={len(rows)}")
        for gate in sorted(_SIGNAL_QUALITY_GATES | {"meta_gate", "toxicity_gate"}):
            moves = solo_blocked.get(gate, [])
            if moves:
                lines.append(f"{gate}: n={len(moves)} avg={sum(moves)/len(moves):+.4f}")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"\n리포트 저장: {report_path}")
    except Exception as e:
        print(f"리포트 저장 실패: {e}")


if __name__ == "__main__":
    main()

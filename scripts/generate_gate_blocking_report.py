# scripts/generate_gate_blocking_report.py — W1 Phase 0: 게이트 차단 로그 30일 전수 집계
"""
mireuki_v9_최종설계안_2026-07-03.md §Part3 진단(문답 13번): "EntryChecklist·CoherenceGate·
TrendGate·MetaGate·BiasReset·Hurst필터·ATR상한·시가이격필터 등 6~8겹 게이트가 AND 직렬로
붙어 있어 결합 통과율이 곱셈으로 붕괴한다"는 가설을, 실제 ensemble_decisions DB 30일치로
검증한다.

- 겹별(마지널) 통과율: entry_gate_json(18개 bool 키, main.py:6199-6218 _gate_checks)
- 결합 통과율 vs 이론적 곱셈값: 게이트가 독립이라는 가정 하의 기대 통과율과 실측 비교
- 최종 차단 원인 1위 집계: entry_block_reason(우선순위 체인, main.py:6220-6307)을
  코드에 실제 기록된 한국어 문구로 분류 — 실행 순서를 재현하지 않고 기록된 결과만 집계하므로
  main.py의 우선순위 로직을 다시 구현할 필요가 없다.
- 체크리스트 등급 X 세부 원인: checklist_reason (main.py:5087-5641 단축 코드)

출력: gate_blocking_report.md, gate_blocking_metrics.json (ROOT)
"""
import json
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import PREDICTIONS_DB

REPORT_PATH = ROOT / "gate_blocking_report.md"
METRICS_PATH = ROOT / "gate_blocking_metrics.json"

LOOKBACK_DAYS = 30

# main.py `_entry_block_reason` elif 체인이 실제로 남기는 한국어 문구 그대로 매칭 —
# 실행 순서를 재추정하지 않고, 저장된 결과 문자열만 분류한다.
# [402차] 라인번호 주석(구 "6220-6307")은 이미 어긋나 있어 제거 — 코드가 옮겨다녀도
# 썩지 않도록 변수명으로만 가리킨다. 위→아래 첫 매치 사용이므로 순서가 곧 우선순위.
BLOCK_REASON_TAGS = [
    # [402차] JointGateBlock은 체크리스트 통과 *이후* 2차 실행단계 차단이라 일반 needle
    # 보다 먼저 와야 한다(utils/db_utils.py의 305차 주석과 동일 원칙). 이 표에만 항목이
    # 빠져 있어 지금까지 통째로 "미분류"로 집계됐다 — 402차 검증에서 발견.
    ("JointGateBlock", "JointGateBlock"),
    ("거래소CB_관망", "거래소 CB 해제 후 관망"),
    ("CircuitBreaker", "Circuit Breaker"),
    ("고신뢰연속오답(HC)", "고신뢰 연속오답"),
    ("브로커sync미검증", "브로커 sync 미검증"),
    ("RestartArmistice", "Restart Armistice"),
    ("포지션무결성실패", "포지션 무결성 실패"),
    ("ENTRY쿨다운", "ENTRY 타임아웃 쿨다운"),
    ("청산후쿨다운", "청산 후 쿨다운"),
    ("ReverseClamp", "Reverse Clamp"),
    ("IntradayRegime", "IntradayRegime"),
    ("Hurst횡보차단", "Hurst"),
    ("ATR변동성부족", "변동성 부족"),
    ("ATR고변동성과대", "고변동성 진입 차단"),
    ("시가이격과다", "시가이격 과다"),
    ("Degraded최소신뢰도", "Degraded 최소신뢰도"),
    ("모드필터", "모드필터"),
    ("점심휴식구간(8_time)", "점심 휴식 구간"),
    ("진입금지시간대(8_time)", "진입 금지 시간대"),
    # [402차] "15:00 이후"는 NEW_ENTRY_CUTOFF=14:50 변경 후 사문화된 needle이었다
    # (utils/db_utils.py 동일 수정 참조). 시각 비의존 문구로 교체.
    ("마감전신규진입금지", "신규 진입 금지"),
    # [402차] 아래 4종 신설 — 401차까지 "등급X" 사유가 전부 `_qty_display <= 0`
    # 분기에 가로채여 "사이저 산출 수량 0"으로 저장됐고, 그 문구는 이 표에 항목이
    # 없어 통째로 "미분류"로 빠졌다(2026-07-29 실측 50건). main.py 402차 수정으로
    # 등급X가 "체크리스트 미통과"와 "게이트 강등"으로 갈라져 저장된다.
    ("게이트강등_Toxicity", "게이트 강등 X — ToxicityGate"),
    ("게이트강등_Meta", "게이트 강등 X — MetaGate"),
    ("게이트강등_Exec", "게이트 강등 X — ExecutionGovernor"),
    ("게이트강등_기타", "게이트 강등 X"),
    ("사이저수량0", "사이저 산출 수량 0"),
    ("등급X_기타", "등급X"),
    # [402차] 347차 신설 문구 2종도 표에 없어 "미분류"로 빠지고 있었다.
    ("conf_floor미달", "conf_floor 미달"),
    ("자동진입토글OFF", "자동진입 비활성화"),
    # [402차] 401차가 신설한 [정보] 문구 — 차단이 아니라 "포지션 보유중이라 평가 생략"
    # 이지만, 버킷이 없어 "미분류"로 섞여 들어가고 있었다.
    ("포지션보유중(평가생략)", "포지션 보유중"),
]


def _classify_block_reason(reason: str) -> str:
    if not reason:
        return "차단없음"
    for tag, pattern in BLOCK_REASON_TAGS:
        if pattern in reason:
            return tag
    return "미분류"


def _fetch(since_ts: str):
    with sqlite3.connect(PREDICTIONS_DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT ts, grade, auto_entry, entry_final_ok, entry_executed,
                   entry_gate_json, entry_block_reason, checklist_reason
            FROM ensemble_decisions
            WHERE ts >= ?
            ORDER BY ts
            """,
            (since_ts,),
        ).fetchall()
    return rows


def _analyze(rows):
    grade_counter = Counter()
    auto_entry_count = 0
    entry_final_ok_count = 0
    entry_executed_count = 0
    block_reason_counter = Counter()
    checklist_reason_counter = Counter()

    gate_true = Counter()
    gate_total = Counter()
    gate_snapshot_rows = 0
    combined_all_true = 0

    for row in rows:
        grade_counter[row["grade"] or ""] += 1
        auto_entry_count += int(row["auto_entry"] or 0)
        entry_final_ok_count += int(row["entry_final_ok"] or 0)
        entry_executed_count += int(row["entry_executed"] or 0)
        block_reason_counter[_classify_block_reason(row["entry_block_reason"] or "")] += 1
        if row["checklist_reason"]:
            checklist_reason_counter[row["checklist_reason"]] += 1

        try:
            gate_checks = json.loads(row["entry_gate_json"] or "{}")
        except (TypeError, ValueError):
            gate_checks = {}
        if not gate_checks:
            continue
        gate_snapshot_rows += 1
        all_true = True
        for key, val in gate_checks.items():
            gate_total[key] += 1
            if val:
                gate_true[key] += 1
            else:
                all_true = False
        if all_true:
            combined_all_true += 1

    n = len(rows)
    marginal_rate = {
        k: round(gate_true[k] / gate_total[k], 4) if gate_total[k] else None
        for k in gate_total
    }
    theoretical_product = 1.0
    for rate in marginal_rate.values():
        if rate is not None:
            theoretical_product *= rate
    combined_actual_rate = (
        round(combined_all_true / gate_snapshot_rows, 4) if gate_snapshot_rows else None
    )

    return {
        "n": n,
        "gate_snapshot_rows": gate_snapshot_rows,
        "grade_dist": dict(grade_counter),
        "auto_entry_count": auto_entry_count,
        "entry_final_ok_count": entry_final_ok_count,
        "entry_executed_count": entry_executed_count,
        "block_reason_dist": dict(block_reason_counter.most_common()),
        "checklist_reason_dist": dict(checklist_reason_counter.most_common()),
        "gate_marginal_pass_rate": dict(sorted(marginal_rate.items(), key=lambda x: (x[1] is None, x[1]))),
        "gate_count": len(marginal_rate),
        "theoretical_combined_pass_rate": round(theoretical_product, 6) if marginal_rate else None,
        "actual_combined_pass_rate": combined_actual_rate,
        "collapse_ratio": (
            round(combined_actual_rate / theoretical_product, 4)
            if combined_actual_rate is not None and theoretical_product > 0
            else None
        ),
    }


def build_report(metrics: dict) -> str:
    a = metrics["analysis"]
    lines = [
        "# Gate Blocking Report — 30일 게이트 차단 전수 집계 (v9 Phase 0)",
        "",
        f"- Generated at: {metrics['generated_at']}",
        f"- 조회 구간: 최근 {metrics['lookback_days']}일 ({metrics['since_ts']} ~)",
        f"- 전체 분봉 판정 수: {a['n']}건 (게이트 스냅샷 보유: {a['gate_snapshot_rows']}건)",
        f"- 등급 분포: {a['grade_dist']}",
        f"- auto_entry={a['auto_entry_count']}건, entry_final_ok={a['entry_final_ok_count']}건, "
        f"entry_executed={a['entry_executed_count']}건",
        "",
        "## 겹별(마지널) 게이트 통과율 — 낮은 순",
        "",
    ]
    for k, v in a["gate_marginal_pass_rate"].items():
        lines.append(f"- `{k}`: {v if v is not None else 'N/A'}")
    lines += [
        "",
        "## 결합 통과율 vs 이론적 곱셈값 (AND 직렬 붕괴 검증)",
        "",
        f"- 게이트 {a['gate_count']}겹, 이론적 곱셈 통과율(독립 가정): "
        f"{a['theoretical_combined_pass_rate']}",
        f"- 실측 결합 통과율(전 게이트 True): {a['actual_combined_pass_rate']}",
        f"- collapse_ratio(실측/이론): {a['collapse_ratio']} "
        "(1에 가까울수록 게이트 간 독립에 가까움 — 1보다 많이 낮으면 서로 다른 시점에 "
        "번갈아 차단해 결합 통과율이 이론보다도 더 붕괴한다는 뜻)",
        "",
        "## 최종 차단 원인 분류 (entry_block_reason 실측 문구 기준)",
        "",
    ]
    for k, v in a["block_reason_dist"].items():
        lines.append(f"- {k}: {v}건")
    lines += [
        "",
        "## 체크리스트 등급 X 세부 원인 (checklist_reason)",
        "",
    ]
    for k, v in a["checklist_reason_dist"].items():
        lines.append(f"- {k}: {v}건")
    lines += [
        "",
        "---",
        "",
        "## 해석 가이드",
        "",
        "- `gate_marginal_pass_rate` 하위 항목이 실제 병목 게이트 후보.",
        "- `collapse_ratio` < 1이면 \"각 게이트는 그럭저럭 통과하는데 서로 다른 시점에 번갈아 차단해 "
        "결합 통과율이 곱셈보다도 낮다\" — L3 소프트 게이트(점수 합산) 전환의 정량적 근거.",
        "- `block_reason_dist`의 최빈 항목이 §5(구현계획) 우선 개선 대상.",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    since_ts = (datetime.now() - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d %H:%M:%S")
    rows = _fetch(since_ts)
    if not rows:
        print("validation=FAIL (no ensemble_decisions rows in lookback window)")
        return 1

    analysis = _analyze(rows)
    metrics = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "lookback_days": LOOKBACK_DAYS,
        "since_ts": since_ts,
        "analysis": analysis,
    }

    REPORT_PATH.write_text(build_report(metrics), encoding="utf-8")
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"saved_report={REPORT_PATH}")
    print(f"saved_metrics={METRICS_PATH}")
    print(f"n={analysis['n']} gate_snapshot_rows={analysis['gate_snapshot_rows']}")
    print(f"theoretical_combined={analysis['theoretical_combined_pass_rate']} "
          f"actual_combined={analysis['actual_combined_pass_rate']} "
          f"collapse_ratio={analysis['collapse_ratio']}")
    print(f"top_block_reasons={dict(list(analysis['block_reason_dist'].items())[:5])}")
    print("validation=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

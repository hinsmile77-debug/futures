"""[399차] HurstGate 소프트 사이징(×0.5) no-op 비율/손익 분석.

배경: 333차 후속이 하드차단 대신 사이징 축소(hurst<0.45 시 size_mult=0.50)로
전환했고(hurst_gate_shadow counterfactual n=111로 검증됨), 396차 후속이
`hurst_soft_block_applied`/`hurst_soft_block_noop`을 entry_gate_json에 남기기
시작했다. 398차 정기점검 딥다이브에서 "mean-revert hurst_bucket 진입이 다른
버킷보다 손익이 나쁘다"는 관찰(2주 풀링 n=32, 통계적으로 유의하지 않음, p=0.18)이
나왔는데, 이 스크립트는 그 원인이 "사이징 축소가 이미 1계약 바닥이라 no-op되어
완화 효과가 없었기 때문"인지를 entry_gate_json의 no-op 플래그로 직접 갈라서
확인한다. 313차 원칙(소표본 결론 금지)에 따라 판단이 아니라 실측 분해만 제공.

읽기 전용 분석 스크립트 — 실거래 로직에 영향 없음.
"""
import json
import sqlite3
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import PREDICTIONS_DB, TRADES_DB


def _fetch_hurst_softblock_events(since_date):
    with sqlite3.connect(PREDICTIONS_DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT ts, grade, entry_qty, entry_gate_json
            FROM ensemble_decisions
            WHERE entry_executed = 1
              AND date(ts) >= date(?)
              AND entry_gate_json IS NOT NULL
            ORDER BY ts
            """,
            (since_date,),
        ).fetchall()

    events = []
    for row in rows:
        try:
            gate = json.loads(row["entry_gate_json"] or "{}")
        except (TypeError, ValueError):
            continue
        if not gate.get("hurst_soft_block_applied"):
            continue
        events.append({
            "ts": row["ts"],
            "grade": row["grade"],
            "entry_qty": row["entry_qty"],
            "noop": bool(gate.get("hurst_soft_block_noop")),
        })
    return events


def _fetch_trade_pnl(entry_ts_minute):
    # trades.entry_ts는 초 단위까지 있어 분 단위(HH:MM)까지만 맞춰 매칭한다.
    with sqlite3.connect(TRADES_DB) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT net_pnl_krw, exit_reason
            FROM trades
            WHERE strftime('%Y-%m-%d %H:%M', entry_ts) = ?
            ORDER BY id LIMIT 1
            """,
            (entry_ts_minute,),
        ).fetchone()
    return dict(row) if row else None


def main() -> int:
    since_date = sys.argv[1] if len(sys.argv) >= 2 else "2026-07-14"
    events = _fetch_hurst_softblock_events(since_date)
    print(f"since_date={since_date}")
    print(f"hurst_soft_block_applied 이벤트 수={len(events)}")
    if not events:
        print("validation=FAIL (해당 기간 HurstGate 소프트 발동 이벤트 없음)")
        return 1

    noop_pnls, real_pnls = [], []
    noop_wins, real_wins = 0, 0
    matched, unmatched = 0, 0

    for ev in events:
        ts_minute = ev["ts"][:16]  # "YYYY-MM-DD HH:MM"
        trade = _fetch_trade_pnl(ts_minute)
        if trade is None:
            unmatched += 1
            continue
        matched += 1
        pnl = float(trade["net_pnl_krw"] or 0.0)
        if ev["noop"]:
            noop_pnls.append(pnl)
            noop_wins += int(pnl > 0)
        else:
            real_pnls.append(pnl)
            real_wins += int(pnl > 0)

    print(f"체결 매칭={matched}  미매칭(체결 안 됐거나 조인 실패)={unmatched}")
    print()
    print("== no-op (이미 1계약 바닥이라 사이징 축소 무의미) ==")
    if noop_pnls:
        print(f"  n={len(noop_pnls)}  승률={noop_wins/len(noop_pnls):.1%}  "
              f"평균손익={mean(noop_pnls):,.0f}원  합계={sum(noop_pnls):,.0f}원")
    else:
        print("  n=0")
    print("== 실제 사이징 축소 적용됨 (qty가 실제로 줄어듦) ==")
    if real_pnls:
        print(f"  n={len(real_pnls)}  승률={real_wins/len(real_pnls):.1%}  "
              f"평균손익={mean(real_pnls):,.0f}원  합계={sum(real_pnls):,.0f}원")
    else:
        print("  n=0")

    if noop_pnls:
        noop_rate = len(noop_pnls) / (len(noop_pnls) + len(real_pnls)) if (noop_pnls or real_pnls) else 0.0
        print()
        print(f"no-op 비율={noop_rate:.1%} — 이 비율이 높을수록 333차 사이징 완화가 "
              f"1계약 바닥 문제로 무력화되는 빈도가 높다는 뜻(0715진입청산검토.md의 "
              f"'사이징이 항상 1계약으로 바닥나 분할청산이 무력화' 문제와 동일 원인).")

    print()
    print("주의: 표본이 작으면(수십 건 미만) 여기서 나온 승률/손익 차이를 "
          "곧바로 정책 판단 근거로 쓰지 말 것(313차 원칙) — 방향성 참고만.")
    print("validation=PASS (분석 완료, 정책 결론은 아님)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

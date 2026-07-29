"""[399차] P4(CVD+OFI 동시 역방향 강등) 발동분 승률/손익 집계.

배경: 398차 정기점검 딥다이브에서 "[P4] CVD+OFI 동시 역방향 → 등급 A→C 강등" 신호가
손실로 이어지는지 의심됐고, 제안 2(가설 수준)로 "P4 강등 신호는 완전차단 대신 사이징
축소를 검토하되, 먼저 [P4] 발동분만 골라 승률/손익을 집계한 뒤 판단할 것"을 등록했다.

[400차 주의] 이 스크립트는 실행한 PC의 로컬 `trades.db`/`logs/`만 본다 — MW0601/MW0602
두 PC가 각자 독립 계좌로 실거래하므로 같은 스크립트를 다른 PC에서 실행하면 표본·수치가
당연히 달라진다(399차는 MW0602 기준, 400차 MW0601 재실행은 MW0601 기준 — 서로 다른
결과가 나온 것은 오류가 아니라 PC 차이). dev_memory에 이 스크립트의 출력을 인용할 때는
반드시 출처 PC명을 함께 적을 것(`feedback_devmemory_pc_provenance` 메모리 참조).

또한 아래 `_fetch_c_grade_trades`의 `grade = 'C'` 필터는 `ensemble_decisions.grade`
(모델 원등급)가 아니라 `trades.grade`(체크리스트 최종등급, `main.py:6263 _final_grade =
_cr["grade"]`)를 본다는 점을 유념할 것 — 원등급이 C였던 신호도 체크리스트 통과 후 A로
승격되면 이 스크립트의 표본에서 빠진다(그 PC에서 그날 체결된 신호가 전부 A로 승격됐다면
해당 날짜 기여분은 0건이 된다).

`entry_gate_json`에는 이 세션(399차) 이전 시점 데이터에 P4 강등 플래그가 없어(오늘
`main.py`에 `p4_cvd_ofi_demoted` 필드를 신규 추가함, 내일부터 DB로 직접 조회 가능),
과거분은 `logs/YYYYMMDD_SIGNAL.log`의 "[P4] CVD+OFI 동시 역방향" 텍스트를 파싱해
분(minute) 단위로 `trades.entry_ts`와 매칭한다. 라인 포맷:
    2026-07-28 14:00:47 [INFO] SIGNAL: [P4] CVD+OFI 동시 역방향 → 등급 A→C 강등 ...

비교군: 같은 기간 C등급 실체결 거래 중 P4로 강등되지 않은 건("organic C")과
대조해, P4 강등분이 organic C보다 특별히 나쁜지를 실측한다(313차 원칙 — 표본이
작으면 유의성 판정 없이 방향성만 보고).

읽기 전용 분석 스크립트 — 실거래 로직에 영향 없음.
"""
import re
import sqlite3
import sys
import datetime
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import TRADES_DB, LOG_DIR

_P4_LINE_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2} .*\[P4\] CVD\+OFI 동시 역방향"
)


def _p4_demotion_minutes(dates):
    minutes = set()
    for d in dates:
        log_path = Path(LOG_DIR) / f"{d}_SIGNAL.log"
        if not log_path.exists():
            continue
        with open(log_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                m = _P4_LINE_RE.match(line)
                if m:
                    minutes.add(m.group(1))
    return minutes


def _fetch_c_grade_trades(since_date):
    with sqlite3.connect(TRADES_DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT entry_ts, net_pnl_krw, exit_reason
            FROM trades
            WHERE grade = 'C' AND date(entry_ts) >= date(?)
            ORDER BY entry_ts
            """,
            (since_date,),
        ).fetchall()
    return rows


def _date_range(since_date):
    start = datetime.datetime.strptime(since_date, "%Y-%m-%d").date()
    today = datetime.date.today()
    d = start
    out = []
    while d <= today:
        out.append(d.strftime("%Y%m%d"))
        d += datetime.timedelta(days=1)
    return out


def main() -> int:
    since_date = sys.argv[1] if len(sys.argv) >= 2 else "2026-07-14"
    dates = _date_range(since_date)
    p4_minutes = _p4_demotion_minutes(dates)
    print(f"since_date={since_date}  P4 강등 로그 발동 이벤트(분 단위, 체결 무관)={len(p4_minutes)}")

    c_trades = _fetch_c_grade_trades(since_date)
    print(f"기간 내 C등급 실체결 거래={len(c_trades)}")

    p4_pnls, organic_pnls = [], []
    p4_wins, organic_wins = 0, 0
    for t in c_trades:
        minute_key = t["entry_ts"][:16]  # "YYYY-MM-DD HH:MM"
        pnl = float(t["net_pnl_krw"] or 0.0)
        if minute_key in p4_minutes:
            p4_pnls.append(pnl)
            p4_wins += int(pnl > 0)
        else:
            organic_pnls.append(pnl)
            organic_wins += int(pnl > 0)

    print()
    print("== P4(CVD+OFI 동시역행) 강등분 C등급 체결 ==")
    if p4_pnls:
        print(f"  n={len(p4_pnls)}  승률={p4_wins/len(p4_pnls):.1%}  "
              f"평균손익={mean(p4_pnls):,.0f}원  합계={sum(p4_pnls):,.0f}원")
    else:
        print("  n=0 (기간 내 P4 강등분이 실제 체결까지 간 사례 없음)")

    print("== organic C등급(강등 아닌 원래 C) 체결 ==")
    if organic_pnls:
        print(f"  n={len(organic_pnls)}  승률={organic_wins/len(organic_pnls):.1%}  "
              f"평균손익={mean(organic_pnls):,.0f}원  합계={sum(organic_pnls):,.0f}원")
    else:
        print("  n=0")

    print()
    print("주의: n이 한 자릿수~십여 건이면 유의성 판정 불가(313차 원칙) — "
          "방향성 참고만 하고 사이징/차단 정책을 이 결과만으로 바꾸지 말 것.")
    print("참고: 2026-07-29부터는 ensemble_decisions.entry_gate_json의 "
          "'p4_cvd_ofi_demoted' 필드로 로그 파싱 없이 직접 조회 가능(399차 신설).")
    print("validation=PASS (분석 완료, 정책 결론은 아님)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

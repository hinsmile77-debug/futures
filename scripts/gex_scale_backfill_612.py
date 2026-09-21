# scripts/gex_scale_backfill_612.py
"""[MW0601 612차] `opt_gex_bn` 100배 오류 소급 정정.

## 무엇을 고치나

`Dscbo1.OptionMst`의 Greeks 는 **백분율**로 온다. `_HV_GAMMA = 110` 주석은 249차
도입 당시부터 "(백분율, ÷100)"이라 적혀 있었는데 `_compute_gex()`가 그 ÷100 을
적용하지 않았다(`git log -S "gamma / 100"` = 0건). 그래서 `opt_gex_bn`이
**2026-05 이래 줄곧 100배** 부풀려진 채 DB 에 쌓였다.

근거 — `data/option_metrics.json`(2026-05-14, 48종목 실수집):
  · `delta` 필드 범위 −52.63 ~ +59.43  → 0~1 이 아니라 0~100. Greeks 는 백분율.
  · ATM(strike 1220.0) `gamma` 0.2100 vs BS 이론 1/(S·σ·√(2πT)) = 0.002018
    (S=1220.17, σ=56.51%, T=30/365)   → **비율 104.1**

## 무엇은 안 바뀌나 — 오해 방지

⚠ **IC·Spearman 은 불변이다.** ÷100 은 순수 양의 선형 변환이라 순위상관을 바꾸지
   않는다. 「GEX IC 0.198 → 0.013 재현 실패(F4)」의 원인이 이 버그라고 쓰면 **틀린다.**
⚠ **학습 영향 없음.** `model/horizons/feature_names.pkl`(97키 동결 슈퍼셋)과
   호라이즌별 6개 피처셋 전수 확인에서 옵션 체인 키는 하나도 포함돼 있지 않다.
   train/serve skew 우려 없음(317차 원칙).
⇒ 실제로 바뀌는 것은 **저장된 숫자의 스케일**뿐이다. 그래서 되돌릴 수 있고,
   그래서 소급 정정이 안전하다(501차 broker_net 정정과 같은 성격).

## 어디를 고치나

`raw_features.features` / `raw_features_horizon.features` 는 **JSON TEXT 블롭**이다
(컬럼이 아니다). 행마다 파싱해 `opt_gex_bn` 키만 ÷100 하고 되쓴다.
`opt_gex_sign` 은 부호라 **건드리지 않는다**. `opt_chain_pcr`·`opt_atm_*` 도 무관하다.

## 사용법

    python scripts/gex_scale_backfill_612.py --dry-run     # 건수만 센다(쓰기 없음)
    python scripts/gex_scale_backfill_612.py --apply       # 백업 후 정정
    python scripts/gex_scale_backfill_612.py --verify      # 정정 후 분포 확인

🔴 **장 마감 후에만 돈다** — `guard_intraday()`가 08:45~15:35 를 차단한다(456차).
   전수 스캔이라 장중에 돌리면 CB⑤(파이프라인 지연 5초)를 자가유발한다.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dll_bootstrap import ensure_conda_dll_path   # noqa: E402
ensure_conda_dll_path()

from utils.analysis_db import guard_intraday            # noqa: E402

RAW_DB = os.path.join("data", "db", "raw_data.db")
REG_DB = os.path.join("data", "db", "strategy_registry.db")
KEY = "opt_gex_bn"
FACTOR = 100.0
CHUNK = 2000

# 이 시각 이후에 쓰인 행은 이미 정정된 코드의 산물이므로 건드리지 않는다.
# (612차 배포 시각을 여기 박는다 — 배포 후 첫 실행 전에 실제 값으로 갱신할 것)
FIX_DEPLOYED_AT = "2026-09-21 15:35:00"


def _tables(con):
    out = []
    for t in ("raw_features", "raw_features_horizon"):
        try:
            con.execute("SELECT 1 FROM %s LIMIT 1" % t).fetchone()
            out.append(t)
        except sqlite3.Error:
            pass
    return out


def scan(con, table, cutoff):
    """정정 대상 행 수와 값 범위를 센다. 쓰기 없음."""
    n_rows = n_hit = 0
    lo = hi = None
    cur = con.execute(
        "SELECT rowid, features FROM %s WHERE ts < ?" % table, (cutoff,))
    while True:
        batch = cur.fetchmany(CHUNK)
        if not batch:
            break
        for _rid, blob in batch:
            n_rows += 1
            try:
                d = json.loads(blob)
            except Exception:
                continue
            v = d.get(KEY)
            if v is None:
                continue
            try:
                v = float(v)
            except Exception:
                continue
            n_hit += 1
            lo = v if lo is None else min(lo, v)
            hi = v if hi is None else max(hi, v)
    return n_rows, n_hit, lo, hi


def apply_fix(con, table, cutoff):
    """`opt_gex_bn` 만 ÷100 하고 되쓴다. 다른 키는 손대지 않는다."""
    changed = 0
    pending = []
    cur = con.execute(
        "SELECT rowid, features FROM %s WHERE ts < ?" % table, (cutoff,))
    while True:
        batch = cur.fetchmany(CHUNK)
        if not batch:
            break
        for rid, blob in batch:
            try:
                d = json.loads(blob)
            except Exception:
                continue
            if KEY not in d:
                continue
            try:
                d[KEY] = round(float(d[KEY]) / FACTOR, 6)
            except Exception:
                continue
            pending.append((json.dumps(d, ensure_ascii=False), rid))
            if len(pending) >= CHUNK:
                con.executemany(
                    "UPDATE %s SET features=? WHERE rowid=?" % table, pending)
                changed += len(pending)
                pending = []
    if pending:
        con.executemany(
            "UPDATE %s SET features=? WHERE rowid=?" % table, pending)
        changed += len(pending)
    return changed


def mark_discontinuity(n_raw, n_hz):
    """`strategy_events` 에 METRIC_REDEFINITION 마커. 461차·501차 관례."""
    note = (
        "[612차] opt_gex_bn 100배 정정 — OptionMst Greeks 는 백분율인데 "
        "_compute_gex 가 ÷100 을 적용하지 않았다(249차 도입 이래). "
        "근거: data/option_metrics.json delta 범위 -52.63~+59.43(백분율), "
        "ATM gamma 0.2100 vs BS 이론 0.002018 = 비율 104.1. "
        "소급 정정: raw_features %d행 / raw_features_horizon %d행. "
        "opt_gex_sign 은 무변경. IC/Spearman 은 선형변환이라 불변이며 "
        "학습 피처셋에 미포함이라 train/serve skew 없음. "
        "⚠ 2026-09-21 이전 opt_gex_bn 시계열과 직접 비교 금지." % (n_raw, n_hz)
    )
    try:
        con = sqlite3.connect(REG_DB)
        con.execute("""
            CREATE TABLE IF NOT EXISTS strategy_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT, event_type TEXT, detail TEXT
            )""")
        cur = con.execute(
            "INSERT INTO strategy_events(ts, event_type, detail) VALUES (?,?,?)",
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "METRIC_REDEFINITION", note),
        )
        con.commit()
        eid = cur.lastrowid
        con.close()
        return eid
    except Exception as exc:
        print("  [WARN] strategy_events 마커 기록 실패: %s" % exc)
        print("         → 수동으로 남길 것. 마커 없는 불연속은 461차가 겪은 사고다.")
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true", help="건수만 센다 (쓰기 없음)")
    g.add_argument("--apply", action="store_true", help="백업 후 정정")
    g.add_argument("--verify", action="store_true", help="정정 후 분포 확인")
    ap.add_argument("--cutoff", default=FIX_DEPLOYED_AT,
                    help="이 ts 이전 행만 대상 (기본: 612차 배포 시각)")
    args = ap.parse_args()

    guard_intraday("gex_scale_backfill_612")   # 장중이면 rc=2 로 종료

    if not os.path.exists(RAW_DB):
        print("[ERR] %s 없음" % RAW_DB)
        return 1

    if args.apply:
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = "%s.bak_%s_pre_gex_612" % (RAW_DB, stamp)
        print("[1/4] 백업 → %s" % bak)
        shutil.copy2(RAW_DB, bak)

    con = sqlite3.connect(RAW_DB)
    con.execute("PRAGMA journal_mode=wal")
    tables = _tables(con)
    print("[i] 대상 테이블: %s | cutoff ts < %s" % (tables, args.cutoff))

    if args.dry_run or args.verify:
        for t in tables:
            n_rows, n_hit, lo, hi = scan(con, t, args.cutoff
                                         if args.dry_run else "9999-12-31")
            rng = ("%.4f ~ %.4f" % (lo, hi)) if lo is not None else "—"
            print("  %-22s 행 %7d | %s 보유 %7d | 범위 %s"
                  % (t, n_rows, KEY, n_hit, rng))
        if args.verify:
            print("\n[i] --verify 는 전 구간 분포다. 정정이 끝났다면 |값| 최대가")
            print("    정정 전의 1/100 스케일이어야 한다(실측 참고: 정정 전 max 38.2e2 B).")
        con.close()
        return 0

    totals = {}
    for t in tables:
        print("[2/4] %s 정정 중…" % t)
        totals[t] = apply_fix(con, t, args.cutoff)
        print("       %d 행 갱신" % totals[t])
    con.commit()
    con.close()

    print("[3/4] 불연속 마커 기록")
    eid = mark_discontinuity(totals.get("raw_features", 0),
                             totals.get("raw_features_horizon", 0))
    print("       strategy_events id=%s" % eid)

    print("[4/4] 완료. 검증: python scripts/gex_scale_backfill_612.py --verify")
    print("\n⚠ CLAUDE.md 「주기적 재검증 항목」과 dev_memory/DECISION_LOG.md 에")
    print("  이 불연속(전환 마커 id=%s)을 기록할 것." % eid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

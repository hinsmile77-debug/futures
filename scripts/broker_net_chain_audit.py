# -*- coding: utf-8 -*-
"""[MW0602 501차] 브로커 net 예탁금 체인 무결성 진단 — **읽기 전용**.

`daily_broker_pnl.broker_net_krw`는 실전 전환 기준 ①의 판정 원천이다(493차 F-1).
그 값이 조용히 틀어지는 경로가 셋 있고, 이 스크립트는 셋을 한 번에 잰다.

## 무엇을 재는가

**D1 — 롤오버(장후 정산) 판독 오염.**
`CpTd6197`의 두 필드는 정산 전후로 **의미가 바뀐다**:

    장중     예탁현금 = 당일 시가(고정) · 익일가 = 시가 + gross − 수수료
             → `익일가 − 예탁` = 그날 net              ✅
    장후정산 예탁현금 = (시가 + gross)로 롤오버 · 익일가 = 거기서 수수료만 차감
             → `익일가 − 예탁` = −수수료               ❌

거래일 저녁에 세션이 살아 있으면 뒤쪽 판독이 남는다. 그걸 그날 net으로 채택하면
손익이 통째로 사라진다(MW0602 실측 4일: 2026-06-30·07-01·07-14·08-06.
08-06은 −360,142가 −43,142로 기록돼 8월 손실 6위가 순위에서 사라졌다).

판별은 **「예탁현금은 당일 시가 고정」 불변식**으로 한다 — 그날 첫 판독과
달라지면 롤오버. MW0602 전 로그(49거래일·2,164줄)에서 오탐 0·미탐 0.

⚠ 「실현손익 0 && 예탁≠익일가」로는 안 된다 — 미실현이 익일가를 움직이는 장중
초반 줄이 걸려 33일이 오탐된다(설계 중 실제로 밟은 실패).

**D2 — 체인 불연속.** 입출금이 없다면 `전일 익일가 == 당일 예탁`이어야 한다.
어긋나면 (a) 롤오버 오염 (b) 실제 입출금 (c) 결측 중 하나다.

**D3 — 거래일 판정 음성 캐싱으로 라이브 저장이 통째로 죽는 증상.**
`is_krx_trading_date()`가 음성을 영구 캐시하면, 장전 08:41 첫 호출(당일
`predictions` 첫 행은 09:00)이 `False`를 굳혀 그날 `upsert_broker_net`이 종일
스킵된다. 로그의 `[BrokerNet] state=SKIP_NON_TRADING`이 지문이다.
⚠ 이 로그는 500차 F-5가 넣은 것이라 그 이전 세대에는 없다 — 그때는 "로그 없음"이
"정상"이 아니라 **"판정 불가"** 다(계측 4원칙 ②).

## 사용

    python scripts/broker_net_chain_audit.py               # 전체 진단
    python scripts/broker_net_chain_audit.py --since 2026-07-01
    python scripts/broker_net_chain_audit.py --json        # 기계 판독용

종료코드: 0 = 이상 없음 / 1 = 오염·불연속 발견 / 2 = 표본 없음.

**이 스크립트는 아무것도 쓰지 않는다.** 정정은
`python scripts/commission_rate_recon.py --backfill --force`가 한다
(그 스크립트의 `_scan_lines`에 D1 가드가 들어 있어야 한다 — §D1 결과가
「가드 미적용」이면 먼저 그쪽을 고칠 것).

근거: `docs/정기점검/브로커net_예탁금체인결함_규명및MW0601점검가이드_20260830.md`,
      `dev_memory/DECISION_LOG.md` 2026-08-30(MW0602 501차 후속).
"""
import argparse
import ast
import glob
import io
import json
import os
import re
import sqlite3
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(ROOT, "logs")
TRADES_DB = os.path.join(ROOT, "data", "db", "trades.db")
_SUMMARY_RE = re.compile(r"summary=(\{.*\})")
_DEP_EPS = 1.0          # 예탁현금 동일 판정 허용오차(원)
_CHAIN_EPS = 1000.0     # 체인 불연속 경보 임계(원) — 반올림 수십원은 무시


def _iter_log_days():
    """(YYYYMMDD, 줄 리스트) — 원본 로그 + 월 zip 압축본 모두.

    압축본을 빠뜨리면 오래된 날이 **조용히** 사라진다(Tier B 30일 압축).
    """
    seen = set()
    for path in sorted(glob.glob(os.path.join(LOG_DIR, "*_SYSTEM.log"))):
        base = os.path.basename(path)
        if not re.match(r"^\d{8}_SYSTEM\.log$", base):
            continue
        seen.add(base)
        with open(path, encoding="utf-8", errors="ignore") as fh:
            yield base[:8], list(fh)
    for zpath in sorted(glob.glob(os.path.join(LOG_DIR, "*_SYSTEM.zip"))):
        try:
            with zipfile.ZipFile(zpath) as zf:
                for name in sorted(zf.namelist()):
                    base = os.path.basename(name)
                    if not re.match(r"^\d{8}_SYSTEM\.log$", base) or base in seen:
                        continue
                    seen.add(base)
                    with zf.open(name) as raw:
                        yield base[:8], list(io.TextIOWrapper(
                            raw, encoding="utf-8", errors="ignore"))
        except (zipfile.BadZipFile, OSError) as exc:
            print("  [경고] 압축본 읽기 실패 — 그 달 표본이 빠진다: %s (%s)"
                  % (os.path.basename(zpath), exc), file=sys.stderr)


def _parse_day(lines):
    """그날의 CpTd6197 판독들 → (rows, skip_non_trading_count).

    rows = [(hhmmss, gross, dep, nxt), ...]  예탁현금 0(빈 TR)은 제외.
    """
    rows, skips = [], 0
    for line in lines:
        if "[BrokerNet] state=SKIP_NON_TRADING" in line:
            skips += 1
        if "[CybosDailyPnl] account" not in line or "summary=" not in line:
            continue
        m = _SUMMARY_RE.search(line.strip())
        if not m:
            continue
        try:
            d = ast.literal_eval(m.group(1))
            dep = float(d.get("총매매", 0) or 0)
            nxt = float(d.get("총평가수익률", 0) or 0)
            gross = float(d.get("실현손익", 0) or 0)
        except Exception:
            continue
        if not dep:
            continue
        rows.append((line[11:19], gross, dep, nxt))
    return rows, skips


def _split_rollover(rows):
    """(장중 판독, 롤오버 판독) — 「예탁현금 당일 시가 고정」 불변식 기준."""
    if not rows:
        return [], []
    base = rows[0][2]
    keep = [r for r in rows if abs(r[2] - base) <= _DEP_EPS]
    drop = [r for r in rows if abs(r[2] - base) > _DEP_EPS]
    return keep, drop


def _db_rows():
    if not os.path.exists(TRADES_DB):
        return {}
    con = sqlite3.connect(TRADES_DB)
    try:
        return {r[0]: r[1:] for r in con.execute(
            "SELECT date, deposit_cash_krw, next_day_deposit_cash_krw, "
            "broker_net_krw, pnl_krw FROM daily_broker_pnl")}
    finally:
        con.close()


def _traded_dates():
    """실제 거래일 집합 — 로그에 CpTd6197 판독이 있어도 휴장일일 수 있다.

    ⚠ 이 구분이 없으면 **주말·휴장일 세션의 정상 스킵이 D3 결함으로 오탐된다**
    (설계 중 2026-08-30 일요일이 그렇게 잡혔다). 판정 원천은
    `is_krx_trading_date()`와 같은 것을 쓴다 — predictions 또는 trades.
    """
    out = set()
    preds = os.path.join(ROOT, "data", "db", "predictions.db")
    if os.path.exists(preds):
        con = sqlite3.connect(preds)
        try:
            out |= {r[0] for r in con.execute(
                "SELECT DISTINCT date(ts) FROM predictions")}
        except sqlite3.Error:
            pass
        finally:
            con.close()
    if os.path.exists(TRADES_DB):
        con = sqlite3.connect(TRADES_DB)
        try:
            out |= {r[0] for r in con.execute(
                "SELECT DISTINCT date(entry_ts) FROM trades")}
        except sqlite3.Error:
            pass
        finally:
            con.close()
    return out


def _guard_present():
    """`commission_rate_recon._scan_lines`에 D1 가드가 들어 있는가."""
    p = os.path.join(ROOT, "scripts", "commission_rate_recon.py")
    if not os.path.exists(p):
        return None
    src = open(p, encoding="utf-8", errors="ignore").read()
    return "base_dep" in src and "롤오버" in src


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="", help="YYYY-MM-DD 이후만")
    ap.add_argument("--json", action="store_true", help="기계 판독용 JSON")
    args = ap.parse_args()

    db = _db_rows()
    traded = _traded_dates()
    days, contaminated, chain_breaks, skip_days = {}, [], [], []
    for stamp, lines in _iter_log_days():
        date = "%s-%s-%s" % (stamp[:4], stamp[4:6], stamp[6:8])
        if args.since and date < args.since:
            continue
        rows, skips = _parse_day(lines)
        if skips and date in traded:
            # 휴장일의 SKIP_NON_TRADING 은 정상 동작이다 — 거래일만 결함으로 센다.
            skip_days.append((date, skips))
        if not rows:
            continue
        keep, drop = _split_rollover(rows)
        intra_net = (keep[-1][3] - keep[-1][2]) if keep else None
        rec = db.get(date)
        rec_net = rec[2] if rec else None
        days[date] = {
            "lines": len(rows), "last": rows[-1][0],
            "intraday_net": intra_net, "recorded_net": rec_net,
            "rollover_lines": len(drop),
            "gross": (rec[3] if rec else None),
        }
        if drop and rec_net is not None and intra_net is not None \
                and abs(rec_net - intra_net) > _CHAIN_EPS:
            contaminated.append((date, intra_net, rec_net, drop[-1][0]))

    # 체인 연속성 — 전일 익일가 vs 당일 예탁
    prev_date = prev_next = None
    for date in sorted(db):
        dep, nxt = db[date][0], db[date][1]
        if dep is None or nxt is None:
            continue
        if args.since and date < args.since:
            prev_date, prev_next = date, nxt
            continue
        if prev_next is not None and abs(dep - prev_next) > _CHAIN_EPS:
            chain_breaks.append((prev_date, prev_next, date, dep, dep - prev_next))
        prev_date, prev_next = date, nxt

    guard = _guard_present()
    result = {
        "days_scanned": len(days),
        "contaminated": [{"date": d, "intraday_net": a, "recorded_net": b,
                          "last_rollover_line": t} for d, a, b, t in contaminated],
        "chain_breaks": [{"prev_date": a, "prev_next_deposit": b, "date": c,
                          "deposit": d, "gap": g} for a, b, c, d, g in chain_breaks],
        "skip_non_trading_days": [{"date": d, "count": n} for d, n in skip_days],
        "d1_guard_present": guard,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if (contaminated or chain_breaks or skip_days) else 0

    W = lambda v: "{:+,.0f}".format(v) if v is not None else "-"
    print("브로커 net 예탁금 체인 진단 — 로그 %d일 / DB %d행" % (len(days), len(db)))
    print("")

    print("── D1. 롤오버(장후 정산) 판독 오염 ──")
    if not days:
        print("  표본 없음 — logs/ 의 SYSTEM 로그(원본+월 zip)를 확인할 것")
        return 2
    if contaminated:
        print("  🔴 %d일 오염" % len(contaminated))
        for d, a, b, t in contaminated:
            print("     %s  장중 %14s  vs  기록 %14s   (마지막 롤오버줄 %s)"
                  % (d, W(a), W(b), t))
        print("     정정식: true_net = gross + 기록net  (검산 후 사용할 것)")
        print("     정정:   python scripts/commission_rate_recon.py --backfill --force")
    else:
        roll = [d for d, v in days.items() if v["rollover_lines"]]
        print("  ✅ 오염 없음" + ("  (롤오버 줄 자체는 %d일에 있으나 채택되지 않았다)"
                                  % len(roll) if roll else ""))

    print("")
    print("── D2. 체인 연속성 (전일 익일가 == 당일 예탁) ──")
    if chain_breaks:
        print("  🔴 불연속 %d건" % len(chain_breaks))
        for a, b, c, d, g in chain_breaks:
            print("     %s 익일가 %14s  vs  %s 예탁 %14s   차 %14s"
                  % (a, W(b), c, W(d), W(g)))
        print("     원인 후보: (a) 롤오버 오염 → D1 참조  (b) 실제 입출금  (c) 결측")
    else:
        print("  ✅ 불연속 없음")

    print("")
    print("── D3. 거래일 판정 음성 캐싱 (라이브 저장 무동작) ──")
    if skip_days:
        unfixed = [(d, n) for d, n in skip_days
                   if db.get(d, (None,) * 4)[2] is None]
        print("  🔴 **거래일인데** `[BrokerNet] state=SKIP_NON_TRADING` 발생: %d일"
              % len(skip_days))
        for d, n in skip_days[-10:]:
            print("     %s  %d건%s" % (d, n,
                  "   ← 그날 broker_net 미기록(미해소)"
                  if db.get(d, (None,) * 4)[2] is None else "   (이후 소급 적재됨)"))
        print("     원인: is_krx_trading_date() 가 음성을 영구 캐시 → 장전 08:41 호출이")
        print("           False 를 굳혀 그날 upsert_broker_net 이 종일 스킵된다")
        print("           (당일 predictions 첫 행은 09:00 이라 그 시점엔 근거가 없다).")
        print("     수정: True 만 영구 캐시, False 는 **지난 날짜만** 캐시.")
        if not unfixed:
            print("     ℹ 위 날짜들은 broker_net 이 이미 채워져 있다 — **과거 로그의 흔적**")
            print("       이며 코드가 고쳐졌다면 다음 거래일부터 사라진다. 라이브 확인 필요.")
    else:
        print("  ✅ SKIP_NON_TRADING 없음")
        print("     ⚠ 단, 이 로그는 500차 F-5 이후 세대에만 있다 — 그 이전 구간은")
        print("       「로그 없음」이 「정상」이 아니라 **판정 불가**다(계측 4원칙 ②).")
        print("       그 구간은 아래 대체 지표로 볼 것: broker_net 이 NULL 인 거래일.")
        miss = [d for d, v in db.items()
                if v[2] is None and (not args.since or d >= args.since)]
        if miss:
            print("       broker_net NULL 인 날: %d일  %s"
                  % (len(miss), " ".join(sorted(miss)[-8:])))

    print("")
    print("── 부가. D1 가드 배선 여부 ──")
    if guard is None:
        print("  ? commission_rate_recon.py 없음")
    elif guard:
        print("  ✅ `_scan_lines` 에 롤오버 가드 있음")
    else:
        print("  🔴 `_scan_lines` 에 롤오버 가드 **없음** — 정정해도 다음 적재에서 재오염된다.")
        print("     먼저 파서를 고칠 것(MW0602 501차 후속 참조).")

    return 1 if (contaminated or chain_breaks or skip_days or guard is False) else 0


if __name__ == "__main__":
    sys.exit(main())

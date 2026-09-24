# -*- coding: utf-8 -*-
"""[MW0601 626차] 신동 사전등록 채점 — R2 · R3 · 섀도(E2+F2)를 **나눠서** 센다.

사전등록: `docs/신동거래/신동_사전등록_20260924.md` §4.

무엇을 내나
-----------
1. 변형(MAIN / SHADOW_E2F2) × 규칙(R2 / R3)별 거래 수 · 승 · 순손익 · 거래당
2. 규칙가 vs **실현가능가** — 라이브 행은 처음 알아챈 시각의 최신 종가(`detect_px`)로
   진입했다고 보고 같은 청산가로 다시 잰다. 09:00·09:01 흐름은 09:02 수집(PEAK_SKIP)에서야
   들어오므로 R2 는 구조적으로 늦게 탐지된다 — 그 비용이 여기서 드러난다.
3. R3 중단 판정 — 채점 시작 후 `R3_KILL_AFTER_DAYS` 거래일이 차면
   MAIN R3 누적 순손익 < 0 **이고** 승률 < 35% 이면 「중단」.
   🔴 판정 기준은 `strategy/shindong/spec.py` 에서 읽는다 — 여기서 값을 바꾸지 말 것.

⚠ 채점 시작일(9/28) 이전 행(9/21–9/23 백필 등)은 **표본에 넣지 않는다** — 규칙을 만든 날이다.
⚠ `RETRACTED`(재계산에서 사라진 신호)는 표본에서 빼되 건수는 따로 적는다(탈락 가시화, 계측 4원칙 ③).

사용:
    python scripts/shindong_scorecard.py                 # 표준출력
    python scripts/shindong_scorecard.py --out docs/신동거래/채점_YYYYMMDD.md
"""
import argparse
import datetime as _dt
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.settings import SHINDONG_DB  # noqa: E402
from strategy.shindong import spec  # noqa: E402
from strategy.shindong.engine import leg_net  # noqa: E402


def _fmt(v):
    return format(float(v), "+,.0f")


def _load(db, since):
    con = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True)
    con.row_factory = sqlite3.Row
    try:
        trades = [dict(r) for r in con.execute(
            "SELECT * FROM shindong_trades WHERE trade_date>=? ORDER BY trade_date, entry_ts",
            (since,))]
        days = [dict(r) for r in con.execute(
            "SELECT * FROM shindong_day WHERE trade_date>=? ORDER BY trade_date", (since,))]
    finally:
        con.close()
    return trades, days


def _realizable_net(t):
    """처음 알아챈 시각의 종가로 들어갔다면. 라이브 행이 아니면 None(미측정)."""
    if t.get("source") != "live" or t.get("detect_px") is None:
        return None
    e = float(t["detect_px"])
    tot = 0.0
    for n in (1, 2):
        if not t.get("leg%d_exit_ts" % n):
            return None                       # 보유 중 — 아직 못 잰다
        x = float(t["leg%d_exit_px" % n])
        mkt = (t.get("leg%d_reason" % n) or "") in ("SL", "BE", "TIME")
        tot += leg_net(int(t["side"]), e, x, mkt)[1]
    return tot


def build(db=SHINDONG_DB, since=spec.SCORING_START):
    lines = []
    w = lines.append
    w("# 신동 채점표 (%s 기준)" % _dt.date.today().isoformat())
    w("")
    w("- 규격: `%s` · 채점 시작 %s · DB `%s`" % (spec.SPEC_VERSION, since, db))
    if not os.path.exists(db):
        w("- **미배선** — DB 가 없다(0건이 아니다)")
        return "\n".join(lines)
    trades, days = _load(db, since)
    main_days = sorted({d["trade_date"] for d in days if d["variant"] == "MAIN"})
    w("- 판정 기록 거래일: **%d일**" % len(main_days))
    retr = [t for t in trades if t["status"] == "RETRACTED"]
    live = [t for t in trades if t["status"] != "RETRACTED"]
    if retr:
        w("- ⚠ 재계산에서 사라진 신호(RETRACTED) **%d건** — 표본 제외" % len(retr))
    openn = [t for t in live if t["status"] == "OPEN"]
    if openn:
        w("- 보유 중(OPEN) %d건 — 순손익은 닫힌 다리만" % len(openn))
    w("")
    w("## 1. 변형 × 규칙")
    w("")
    w("| 변형 | 규칙 | 거래 | 승 | 승률 | 순손익(원) | 거래당 | 실현가능가 순손익* |")
    w("|---|---|---|---|---|---|---|---|")
    for v in spec.VARIANTS:
        for rule in ("R2", "R3", "합계"):
            xs = [t for t in live if t["variant"] == v and (rule == "합계" or t["rule"] == rule)]
            n = len(xs)
            win = sum(1 for t in xs if float(t.get("net_krw") or 0) > 0)
            net = sum(float(t.get("net_krw") or 0) for t in xs)
            rz = [_realizable_net(t) for t in xs]
            rz_ok = [x for x in rz if x is not None]
            rz_txt = ("%s (%d/%d건)" % (_fmt(sum(rz_ok)), len(rz_ok), n)) if rz_ok else "미측정"
            w("| %s | %s | %d | %d | %s | %s | %s | %s |" % (
                v, rule, n, win, ("%.0f%%" % (100.0 * win / n)) if n else "-",
                _fmt(net), _fmt(net / n) if n else "-", rz_txt))
    w("")
    w("\\* 실현가능가 = 처음 알아챈 시각(`detected_at`)의 최신 종가로 진입했다고 보고 같은 청산가로 다시 잰 값."
      " 백필·보유 중 행은 재지 못한다(미측정 ≠ 0).")
    w("")
    w("## 2. 일별 (MAIN)")
    w("")
    w("| 날짜 | 상품 | 장전 콜−풋 | 방향 | R2 | 거래 | 순손익(원) |")
    w("|---|---|---|---|---|---|---|")
    for d in [d for d in days if d["variant"] == "MAIN"]:
        xs = [t for t in live if t["variant"] == "MAIN" and t["trade_date"] == d["trade_date"]]
        w("| %s | %s | %s | %s | %s | %d | %s |" % (
            d["trade_date"], d.get("product") or "-",
            ("%+.0f" % d["pm_sp"]) if d.get("pm_sp") is not None else "미수집",
            {-1: "하방", 0: "보류", 1: "상방"}.get(d.get("bias"), "-"),
            (d.get("r2_status") or "-") + ((" " + d["r2_ts"]) if d.get("r2_ts") else ""),
            len(xs), _fmt(sum(float(t.get("net_krw") or 0) for t in xs))))
    w("")
    w("## 3. R3 중단 판정 (사전등록 §3)")
    w("")
    r3 = [t for t in live if t["variant"] == "MAIN" and t["rule"] == "R3" and t["status"] == "CLOSED"]
    n3 = len(r3)
    net3 = sum(float(t.get("net_krw") or 0) for t in r3)
    wr3 = (sum(1 for t in r3 if float(t.get("net_krw") or 0) > 0) / n3) if n3 else None
    w("- MAIN R3 닫힌 거래 %d건 · 순손익 %s원 · 승률 %s" % (
        n3, _fmt(net3), ("%.0f%%" % (100 * wr3)) if wr3 is not None else "-"))
    if len(main_days) < spec.R3_KILL_AFTER_DAYS:
        w("- 판정: **대기** — %d/%d 거래일" % (len(main_days), spec.R3_KILL_AFTER_DAYS))
    elif n3 == 0:
        w("- 판정: **판정불가** — %d거래일 동안 R3 거래 0건(표본 없음 ≠ 통과)" % len(main_days))
    else:
        kill = net3 < spec.R3_KILL_NET_MAX and wr3 < spec.R3_KILL_WINRATE_MAX
        w("- 판정: **%s** (기준: 순손익 < %s **그리고** 승률 < %.0f%%)" % (
            "R3 중단" if kill else "R3 유지", spec.R3_KILL_NET_MAX, 100 * spec.R3_KILL_WINRATE_MAX))
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=spec.SCORING_START)
    ap.add_argument("--db", default=SHINDONG_DB)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    txt = build(a.db, a.since)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(txt + "\n")
        print("저장: %s" % a.out)
    else:
        print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())

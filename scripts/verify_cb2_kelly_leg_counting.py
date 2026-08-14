# -*- coding: utf-8 -*-
"""scripts/verify_cb2_kelly_leg_counting.py — [MW0602 470차 C2] CB②·Kelly 레그 이중계상 검증

════════════════════════════════════════════════════════════════════════════
무엇을 확인하는가 — **읽기 전용. 아무것도 고치지 않는다.**
════════════════════════════════════════════════════════════════════════════
2026-08-14 라이브에서 실제 손실 **포지션 2건**에 CB 연속손절 카운터가 **3**까지 올라갔다:

    13:07:27 [Position] 체결부분청산 … 손절1차 조기축소   → [CB] 연속 손절 1회
    13:07:31 [Position] 체결청산 … 하드스톱(틱)           → [CB] 연속 손절 2회   ← 같은 포지션
    14:41:43                                              → [CB] 연속 손절 3회

360차가 예견했던 이중계상의 **라이브 최초 실측**이다. 지금은 무해하다
(`CB_CONSEC_STOP_LIMIT=9999`). 위험은 **복원 시점**이다 — 임계를 2로 되돌리면
그날 13:07:31에 HALT 가 걸리고 `_trigger_halt()` 가 emergency_exit 까지 부른다.
실제 손실 포지션은 그 시점 1건뿐이었는데도.

360차 기록은 "`record_stop_loss()` 와 `kelly.record(win=False)` 가 같은 경로에서
호출되므로 Kelly 승률도 같은 왜곡을 받았을 가능성"을 남겼다. **이 스크립트가 그
가능성을 수치로 확정한다.**

코드 실측(2026-08-14, main.py) — 두 호출은 **4개 지점에서 항상 짝으로** 일어난다:
    :9680/:9681   _post_partial_exit()        TP 부분청산
    :9761/:9762   _post_loss_tier1_exit()     손절1차 조기축소
    :10090/:10091 _post_exit()                최종 청산
    :13658/:13659 _ts_record_nonfinal_exit()  체결청산-부분
즉 **CB②가 레그를 세면 Kelly 도 레그를 센다.** 가설이 아니라 코드 사실이다.

다만 두 축의 의미는 다르다:
  · CB② — "연속 손절 **횟수**"로 당일 정지를 건다. 레그를 세면 임계가 실질 절반이 된다.
  · Kelly — 승/패 **표본**으로 사이즈를 정한다. 레그를 세면 다중레그 포지션이
            두 번 반영돼 포지션 단위 승률과 갈린다.
그래서 이 스크립트는 **레그 기준 vs 포지션 기준**을 나란히 낸다.

사용:
    python scripts/verify_cb2_kelly_leg_counting.py
    python scripts/verify_cb2_kelly_leg_counting.py --days 20
"""
from __future__ import print_function

import argparse
import io
import os
import sqlite3
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRADES_DB = os.path.join(ROOT, "data", "db", "trades.db")

# CB②/Kelly 는 `pnl_pts > 0` 이면 승, 아니면 패로 센다(main.py 4개 지점 공통).
# 그 규칙을 **그대로** 재현한다 — 여기서 규칙을 '개선'하면 검증이 아니라 다른 계산이 된다.


def _ro(path):
    if not os.path.exists(path):
        raise SystemExit("[verify_cb2] DB 없음: %s" % path)
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)


def load(days=None):
    con = _ro(TRADES_DB)
    rows = list(con.execute(
        "select entry_ts, exit_ts, direction, quantity, pnl_pts, exit_reason,"
        "       tp1_reached, grade, entry_source"
        "  from trades where entry_ts is not null and exit_ts is not null"
        " order by entry_ts, exit_ts"))
    con.close()

    pos = OrderedDict()
    for (ets, xts, d, q, pt, reason, tp1, grade, src) in rows:
        pos.setdefault(ets, {"entry_ts": ets, "direction": d, "grade": grade,
                             "source": src, "legs": []})
        pos[ets]["legs"].append(
            {"exit_ts": xts, "qty": q, "pnl_pts": pt or 0.0,
             "reason": reason, "tp1_reached": tp1})
    out = list(pos.values())
    if days:
        dates = sorted({p["entry_ts"][:10] for p in out})[-int(days):]
        out = [p for p in out if p["entry_ts"][:10] in dates]
    return out


def analyze(positions):
    leg_win = leg_loss = 0
    pos_win = pos_loss = 0
    multi_leg_loss = []          # 레그를 2회 이상 손실로 센 포지션
    multi_leg_win = []
    max_streak_leg = max_streak_pos = 0
    cur_leg = cur_pos = 0

    for p in positions:
        legs = p["legs"]
        tot = sum(l["pnl_pts"] for l in legs)
        n_leg_loss = sum(1 for l in legs if l["pnl_pts"] <= 0)
        n_leg_win = len(legs) - n_leg_loss
        leg_loss += n_leg_loss
        leg_win += n_leg_win

        # CB②는 승 레그가 하나라도 나오면 record_win() 으로 카운터를 0으로 만든다.
        # 레그 순서대로 그 규칙을 그대로 돌려 최대 연속 손절을 잰다.
        for l in legs:
            if l["pnl_pts"] > 0:
                cur_leg = 0
            else:
                cur_leg += 1
                max_streak_leg = max(max_streak_leg, cur_leg)

        if tot > 0:
            pos_win += 1
            cur_pos = 0
            if n_leg_win > 1:
                multi_leg_win.append((p["entry_ts"], n_leg_win, round(tot, 2)))
        else:
            pos_loss += 1
            cur_pos += 1
            max_streak_pos = max(max_streak_pos, cur_pos)
            if n_leg_loss > 1:
                multi_leg_loss.append((p["entry_ts"], n_leg_loss, round(tot, 2)))

    return {
        "n_positions": len(positions),
        "n_legs": sum(len(p["legs"]) for p in positions),
        "leg_win": leg_win, "leg_loss": leg_loss,
        "pos_win": pos_win, "pos_loss": pos_loss,
        "leg_win_rate": (leg_win / float(leg_win + leg_loss)) if (leg_win + leg_loss) else 0.0,
        "pos_win_rate": (pos_win / float(pos_win + pos_loss)) if (pos_win + pos_loss) else 0.0,
        "max_streak_leg": max_streak_leg,
        "max_streak_pos": max_streak_pos,
        "multi_leg_loss": multi_leg_loss,
        "multi_leg_win": multi_leg_win,
    }


def report(r, positions, days=None):
    L = []
    A = L.append
    A("# CB②·Kelly 레그 이중계상 검증 — [MW0602 470차 C2]")
    A("")
    A("- 대상: **포지션 %d건 / 청산 레그 %d건**%s" % (
        r["n_positions"], r["n_legs"], (" (최근 %s거래일)" % days) if days else " (전 기간)"))
    A("- 읽기 전용. 이 스크립트는 아무것도 고치지 않는다.")
    A("")
    A("## 1. 승패 집계 — 레그 기준 vs 포지션 기준")
    A("")
    A("| 기준 | 승 | 패 | 승률 |")
    A("|---|---|---|---|")
    A("| **레그**(현행 CB②·Kelly 가 세는 방식) | %d | %d | **%.1f%%** |" % (
        r["leg_win"], r["leg_loss"], 100.0 * r["leg_win_rate"]))
    A("| **포지션**(사후검증·§5 가 세는 방식) | %d | %d | **%.1f%%** |" % (
        r["pos_win"], r["pos_loss"], 100.0 * r["pos_win_rate"]))
    A("")
    _gap = 100.0 * (r["leg_win_rate"] - r["pos_win_rate"])
    A("→ 두 승률이 **%+.1f%%p** 갈린다. Kelly 는 이 중 **레그 기준**을 쓴다." % _gap)
    A("")
    A("## 2. CB② 최대 연속 손절 — 임계 복원 시 무엇이 달라지나")
    A("")
    A("| 세는 단위 | 최대 연속 손절 |")
    A("|---|---|")
    A("| **레그**(현행) | **%d** |" % r["max_streak_leg"])
    A("| **포지션**(360차가 의도한 단위) | **%d** |" % r["max_streak_pos"])
    A("")
    if r["max_streak_leg"] > r["max_streak_pos"]:
        A("> 🔴 **레그 기준이 포지션 기준보다 %d 크다.** `CB_CONSEC_STOP_LIMIT` 를 2~3으로"
          % (r["max_streak_leg"] - r["max_streak_pos"]))
        A("> 복원하면 **보정 전 숫자로 정한 임계의 실질값은 그보다 작다.**")
        A("> 08-29 재검토 안건을 `9999→2~3` 이 아니라 **`C1(포지션 단위 집계) 적용 후 9999→2~3`**")
        A("> 으로 재기술해야 하는 이유가 이 표다.")
    else:
        A("> 이 표본에서는 두 값이 같다 — 다중레그 손실 포지션이 없었다는 뜻이다.")
        A("> **표본이 작아 그런 것일 수 있다.** 결론을 내지 말고 표본을 더 볼 것.")
    A("")
    A("## 3. 한 포지션이 손실 이벤트를 2회 이상 만든 사례")
    A("")
    if r["multi_leg_loss"]:
        A("| 진입 | 손실 레그 수 | 포지션 합(pt) |")
        A("|---|---|---|")
        for ets, n, tot in r["multi_leg_loss"][-15:]:
            A("| %s | **%d** | %+.2f |" % (ets[:16], n, tot))
        A("")
        A("총 **%d 포지션**이 손실 레그를 2회 이상 만들었다 — "
          "CB② 카운터가 그만큼 부풀려졌다." % len(r["multi_leg_loss"]))
    else:
        A("_해당 없음._")
    A("")
    A("## 4. 결론")
    A("")
    A("- `record_stop_loss()` 와 `kelly.record(win=False)` 는 main.py 4개 지점")
    A("  (`_post_partial_exit` · `_post_loss_tier1_exit` · `_post_exit` ·")
    A("  `_ts_record_nonfinal_exit`)에서 **항상 짝으로** 호출된다. 코드 사실이다.")
    A("- 따라서 **CB②가 레그를 세면 Kelly 도 레그를 센다.** 360차가 남긴 가능성은 확정이다.")
    A("- 다만 두 축의 처방은 다르다:")
    A("  · **CB②** — 레그 계상이 곧 임계 왜곡이다. C1 에서 포지션 단위로 고친다.")
    A("  · **Kelly** — 레그도 각각 실현된 결과라 계상 자체가 틀렸다고 단정할 수 없다.")
    A("    문제는 **사후검증(포지션)과 다른 단위를 쓴다**는 것이고, 승률이 %+.1f%%p 갈린다."
      % _gap)
    A("    Kelly 변경은 사이징에 직접 영향을 주므로 **이 점검의 범위가 아니다** —")
    A("    표본과 함께 주간회의로 올린다(313차 ④ 사전등록: 관측 후 기준 수립 금지).")
    A("")
    A("> ⚠ 이 스크립트는 **판정하지 않는다.** 합격선도 verdict 도 만들지 않는다.")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description="CB②·Kelly 레그 이중계상 검증 — 읽기 전용")
    ap.add_argument("--days", type=int, default=None, help="최근 N거래일만")
    ap.add_argument("--out", default=None, help="md 파일로 저장 (기본 stdout)")
    args = ap.parse_args(argv)

    positions = load(days=args.days)
    r = analyze(positions)
    text = report(r, positions, days=args.days)

    if args.out:
        with io.open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        sys.stderr.write("[verify_cb2] 저장: %s\n" % args.out)
        print(args.out)
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

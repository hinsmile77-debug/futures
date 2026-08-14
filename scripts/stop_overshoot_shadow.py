# -*- coding: utf-8 -*-
"""scripts/stop_overshoot_shadow.py — [MW0602 470차 D2'] 손절 오버슛(shakeout) 섀도 계측

════════════════════════════════════════════════════════════════════════════
왜 이 축이 필요한가
════════════════════════════════════════════════════════════════════════════
417차 재분해는 진입수량 vs 계약당손익이 **무관**(rho=+0.004, p=0.96)이고, 유일하게
유의한 관계가 진입수량 vs **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5,
rho=+0.318 p=0.015)임을 밝혔다. 그래서 지금 계측 채널은 전부 "손실이 의도한
손절폭을 **초과**했는가" 쪽만 본다.

**그 반대편에는 채널이 없다 — 손절이 너무 타이트해 노이즈에 걸리는 경우다.**

2026-08-14 CASE-04 가 정확히 그 사례다:
    14:40:00 LONG 진입 1096.46 · 손절 1094.40 (의도 손절폭 1.851pt)
    14:41 저점 1093.88 — 손절가를 **0.52pt 오버슛**
    14:41:43 손절 체결 1094.20
      ↓ 이후
    14:43 저점 1094.20 (손절가 재테스트) → 14:51 1096.38 → 14:54 **1098.60**
    보유했다면 14:54 에 +2.14pt(+107,000원 상당) 이익이었다.
그날 1분 레인지 최대가 1.84pt 였으니 손절폭 2.06pt 는 노이즈를 겨우 넘는 수준이었다.

**"손절은 손절이고, 되돌아온 것은 사후에만 안다."** 이 스크립트는 그 사후 사실을
기록만 한다 — 집행에는 아무 영향도 주지 않는다.

════════════════════════════════════════════════════════════════════════════
설계 원칙
════════════════════════════════════════════════════════════════════════════
① **읽기 전용.** 모든 DB 를 `mode=ro` URI 로만 연다. 라이브 배선이 아니다.
   (라이브 훅을 신설하면 집행 경로에 위험을 얹는데, 같은 통계를 사후에 정확히
    계산할 수 있으므로 그럴 이유가 없다 — 계측 먼저, 배선은 나중.)
② **포지션 단위.** `trades` 한 행은 **청산 레그**다(417차 단위 혼동). 진입 시각으로
   묶어 마지막 레그의 청산 시각·가격을 그 포지션의 손절로 본다.
③ **진짜 손절만.** `tp1_reached=1` 인 `하드스톱` 은 TP1 도달 후 **보호 트레일 이익
   청산**이다(465차 P4 / 468차 G-3). 손절로 세면 없는 사실을 만든다.
④ **판정하지 않는다.** 합격선도 verdict 도 만들지 않는다(313차 ④ 사전등록 원칙 —
   관측 후 기준 수립 금지). 회복률이 쌓인 뒤 주간회의가 판단한다.
⑤ **일자단위 분해를 항상 병기.** 313차 ①: 신호단위 n 은 독립관측치가 아니다.

════════════════════════════════════════════════════════════════════════════
무엇을 세는가
════════════════════════════════════════════════════════════════════════════
진짜 손절 포지션마다 청산 후 N분(기본 5·10·15) 안에

  · `recovered`   : 가격이 **진입가**로 되돌아왔는가 (LONG 이면 high >= entry,
                    SHORT 이면 low <= entry) — "손절이 없었다면 본전 이상이었다"
  · `mfe_pt`      : 그 창에서 원래 방향으로 최대 유리 이동 (pt)
  · `overshoot_pt`: 청산가가 손절가를 얼마나 지나쳤나(체결 슬리피지 축과 구분)

사용:
    python scripts/stop_overshoot_shadow.py                # 전체
    python scripts/stop_overshoot_shadow.py --days 20      # 최근 20거래일
    python scripts/stop_overshoot_shadow.py --json out.json
"""
from __future__ import print_function

import argparse
import io
import json
import os
import sqlite3
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRADES_DB = os.path.join(ROOT, "data", "db", "trades.db")
RAW_DB = os.path.join(ROOT, "data", "db", "raw_data.db")

WINDOWS = (5, 10, 15)          # 청산 후 관측 분(minute)

# 진짜 손절로 볼 exit_reason 조각. `하드스톱`은 tp1_reached 로 한 번 더 거른다.
_STOP_TOKENS = ("하드스톱", "손절")
# 손절 계열이라도 이것들은 제외 — 손절이 아니다.
_NOT_STOP = ("TP1", "TP2", "TP3", "강제청산", "시간마감", "신호소멸")


def _ro(path):
    if not os.path.exists(path):
        raise SystemExit("[stop_overshoot] DB 없음: %s" % path)
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)


def _is_real_stop(reason, tp1_reached):
    """진짜 손절인가 — 보호 트레일 이익 청산과 가른다."""
    r = str(reason or "")
    if any(x in r for x in _NOT_STOP):
        return False
    if not any(x in r for x in _STOP_TOKENS):
        return False
    # 465차 P4: tp1_reached=1 인 하드스톱은 **이익 청산**이다.
    if tp1_reached:
        return False
    return True


def load_positions(days=None):
    """청산 레그를 진입 시각으로 묶어 포지션 단위로 되돌린다."""
    con = _ro(TRADES_DB)
    rows = list(con.execute(
        "select entry_ts, exit_ts, direction, entry_price, exit_price, quantity,"
        "       pnl_pts, exit_reason, tp1_reached, grade, entry_horizon, entry_source"
        "  from trades where entry_ts is not null and exit_ts is not null"
        " order by entry_ts, exit_ts"))
    con.close()

    pos = OrderedDict()
    for r in rows:
        (ets, xts, d, ep, xp, q, pt, reason, tp1, grade, hz, src) = r
        p = pos.setdefault(ets, {
            "entry_ts": ets, "direction": d, "entry_price": ep,
            "grade": grade, "horizon": hz, "source": src, "legs": [],
        })
        p["legs"].append({
            "exit_ts": xts, "exit_price": xp, "qty": q, "pnl_pts": pt,
            "reason": reason, "tp1_reached": tp1,
        })

    out = []
    for p in pos.values():
        last = p["legs"][-1]                      # 최종 청산 레그
        p["exit_ts"] = last["exit_ts"]
        p["exit_price"] = last["exit_price"]
        p["exit_reason"] = last["reason"]
        p["tp1_reached"] = last["tp1_reached"]
        p["pnl_pts"] = sum((l["pnl_pts"] or 0.0) for l in p["legs"])
        p["n_legs"] = len(p["legs"])
        out.append(p)

    if days:
        dates = sorted({x["entry_ts"][:10] for x in out})[-int(days):]
        out = [x for x in out if x["entry_ts"][:10] in dates]
    return out


def load_bars():
    """분봉 OHLC — ts 오름차순 리스트."""
    con = _ro(RAW_DB)
    bars = list(con.execute(
        "select ts, high, low, close from raw_candles"
        " where high is not null and low is not null order by ts"))
    con.close()
    return bars


def _window_slice(bars, start_ts, minutes):
    """`start_ts` 초과 ~ +minutes 이내 분봉만. 문자열 비교로 충분(ISO 포맷)."""
    import datetime as dt
    try:
        t0 = dt.datetime.strptime(start_ts[:19], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return []
    t1 = t0 + dt.timedelta(minutes=minutes)
    s0, s1 = start_ts[:19], t1.strftime("%Y-%m-%d %H:%M:%S")
    # 같은 거래일 안으로 제한 — 오버나이트 금지 시스템이라 다음날 가격은 무의미하다.
    day = start_ts[:10]
    return [b for b in bars if s0 < b[0][:19] <= s1 and b[0][:10] == day]


def analyze(days=None):
    positions = load_positions(days=days)
    bars = load_bars()
    stops = [p for p in positions if _is_real_stop(p["exit_reason"], p["tp1_reached"])]

    recs = []
    for p in stops:
        d_long = str(p["direction"]).upper() == "LONG"
        ep = float(p["entry_price"] or 0.0)
        xp = float(p["exit_price"] or 0.0)
        rec = {
            "entry_ts": p["entry_ts"], "exit_ts": p["exit_ts"],
            "direction": p["direction"], "grade": p["grade"],
            "horizon": p["horizon"], "source": p["source"],
            "entry_price": ep, "exit_price": xp, "pnl_pts": round(p["pnl_pts"], 3),
            "exit_reason": p["exit_reason"], "n_legs": p["n_legs"],
        }
        for w in WINDOWS:
            seg = _window_slice(bars, p["exit_ts"], w)
            if not seg:
                rec["recovered_%dm" % w] = None
                rec["mfe_%dm" % w] = None
                continue
            if d_long:
                best = max(b[1] for b in seg)          # high
                rec["recovered_%dm" % w] = bool(best >= ep)
                rec["mfe_%dm" % w] = round(best - ep, 3)
            else:
                best = min(b[2] for b in seg)          # low
                rec["recovered_%dm" % w] = bool(best <= ep)
                rec["mfe_%dm" % w] = round(ep - best, 3)
        recs.append(rec)
    return recs, len(positions), len(stops)


def _fmt_pct(n, d):
    return "—" if not d else "%.1f%%" % (100.0 * n / d)


def report(recs, n_pos, n_stop, days=None):
    L = []
    A = L.append
    A("# 손절 오버슛(shakeout) 섀도 — [MW0602 470차 D2']")
    A("")
    A("- 대상: 포지션 %d건 중 **진짜 손절 %d건**%s" % (
        n_pos, n_stop, (" (최근 %s거래일)" % days) if days else " (전 기간)"))
    A("- `tp1_reached=1` 하드스톱(보호 트레일 이익 청산)은 **제외**했다 — 465차 P4 / 468차 G-3")
    A("")
    if not recs:
        A("_진짜 손절 표본이 없다._")
        return "\n".join(L)

    days_obs = sorted({r["entry_ts"][:10] for r in recs})
    A("## 회복률 — 손절 직후 가격이 진입가로 되돌아왔는가")
    A("")
    A("| 창 | 표본 | 회복 | 회복률 | 평균 MFE(pt) | 최대 MFE(pt) |")
    A("|---|---|---|---|---|---|")
    for w in WINDOWS:
        vals = [r for r in recs if r.get("recovered_%dm" % w) is not None]
        rec_n = sum(1 for r in vals if r["recovered_%dm" % w])
        mfes = [r["mfe_%dm" % w] for r in vals if r["mfe_%dm" % w] is not None]
        A("| %d분 | %d | %d | %s | %s | %s |" % (
            w, len(vals), rec_n, _fmt_pct(rec_n, len(vals)),
            ("%+.2f" % (sum(mfes) / len(mfes))) if mfes else "—",
            ("%+.2f" % max(mfes)) if mfes else "—"))
    A("")

    # 313차 ① — 일자단위 분해를 반드시 병기한다.
    A("## 일자단위 분해 (313차 ① — 신호단위 n은 독립관측치가 아니다)")
    A("")
    A("- 관측 거래일 **%d일** (%s ~ %s)" % (len(days_obs), days_obs[0], days_obs[-1]))
    A("")
    A("| 날짜 | 손절 | 15분 내 회복 | 회복률 |")
    A("|---|---|---|---|")
    for d in days_obs:
        day_recs = [r for r in recs if r["entry_ts"][:10] == d]
        vals = [r for r in day_recs if r.get("recovered_15m") is not None]
        rec_n = sum(1 for r in vals if r["recovered_15m"])
        A("| %s | %d | %d | %s |" % (d, len(day_recs), rec_n, _fmt_pct(rec_n, len(vals))))
    A("")

    A("## 개별 손절 (최근 15건)")
    A("")
    A("| 진입 | 방향 | 등급 | 손익(pt) | 5분 | 10분 | 15분 | MFE15(pt) |")
    A("|---|---|---|---|---|---|---|---|")
    for r in recs[-15:]:
        def _m(w):
            v = r.get("recovered_%dm" % w)
            return "—" if v is None else ("✅회복" if v else "·")
        A("| %s | %s | %s | %+.2f | %s | %s | %s | %s |" % (
            r["entry_ts"][5:16], r["direction"], r["grade"] or "?", r["pnl_pts"],
            _m(5), _m(10), _m(15),
            ("%+.2f" % r["mfe_15m"]) if r.get("mfe_15m") is not None else "—"))
    A("")
    A("> ⚠ **판정하지 않는다.** 이 스크립트는 합격선도 verdict 도 만들지 않는다")
    A("> (313차 ④ 사전등록 — 관측 후 기준 수립 금지). 회복률이 높게 누적되면 **그때**")
    A("> 손절폭 재설계를 주간회의 안건으로 올린다. 오늘 1~2건으로는 논하지 않는다.")
    A("> 또한 회복은 **사후에만 안다** — '손절하지 말았어야 했다'는 결론으로 직행 금지.")
    A("")
    A("> 🔴 **회복률 숫자를 단독으로 읽지 마라 — 기준선이 아직 없다.**")
    A("> KOSPI200 선물 1분봉은 되돌림이 잦아, **아무 시각에나 기준가를 잡아도** 15분 안에")
    A("> 그 가격을 다시 스치는 비율이 상당히 높을 수 있다. 즉 위 %s 가 '손절이 타이트하다'는"
      % _fmt_pct(sum(1 for r in recs if r.get("recovered_15m")),
                 sum(1 for r in recs if r.get("recovered_15m") is not None)))
    A("> 증거가 되려면 **대조군**이 필요하다 — 같은 거래일·같은 시간대에서 무작위로 뽑은")
    A("> 시각을 기준가로 삼았을 때의 회복률과 비교해야 한다.")
    A("> 그 대조군을 만들기 전까지 이 표는 **추세 관측용**이다(날짜별 편차·MFE 크기 변화).")
    A("> 371차 PSI·372차 임계 재보정이 '숫자가 커 보였지만 계측 결함/이상치였다'로 끝난")
    A("> 전례가 둘 있다 — 같은 실수를 반복하지 않는다.")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description="손절 오버슛(shakeout) 섀도 계측 — 읽기 전용")
    ap.add_argument("--days", type=int, default=None, help="최근 N거래일만")
    ap.add_argument("--json", default=None, help="레코드를 JSON으로 저장")
    ap.add_argument("--out", default=None, help="리포트를 md 파일로 저장 (기본 stdout)")
    args = ap.parse_args(argv)

    recs, n_pos, n_stop = analyze(days=args.days)
    text = report(recs, n_pos, n_stop, days=args.days)

    if args.json:
        with io.open(args.json, "w", encoding="utf-8") as f:
            f.write(json.dumps({"n_positions": n_pos, "n_stops": n_stop,
                                "windows": list(WINDOWS), "records": recs},
                               ensure_ascii=False, indent=2))
        sys.stderr.write("[stop_overshoot] JSON 저장: %s\n" % args.json)
    if args.out:
        with io.open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        sys.stderr.write("[stop_overshoot] 저장: %s\n" % args.out)
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

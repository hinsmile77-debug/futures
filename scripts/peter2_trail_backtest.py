"""[MW0601 690차 후속] 피터2 이익보호 트레일 탐색 — 읽기전용(regular_candles.db만 연다).

피터 실거래 내역(_tr.txt)을 정규선물 1분봉으로 재생해 이익보호(손절 끌어올리기) 규칙을 비교한다.

규칙은 피터의 실제 청산 *이전*에만 개입할 수 있다(더 일찍 나가게만 함) — 피터 경로를 보존한 반사실.
보수 가정:
  - 진입 분봉은 버린다(진입 전 고가로 트레일이 무장되는 look-ahead 방지)
  - 한 분봉 안에서는 '직전까지의 손절선으로 저가 먼저 검사 → 그다음 고가로 손절선 갱신'
  - 시가가 손절선을 이미 넘어 갭이면 시가 체결, 아니면 손절선 - 슬리피지
"""
import glob, os, re, sqlite3, sys, itertools, random, statistics as st

ROOT = r"C:\Users\82108\PycharmProjects\futures"
SLIP = 0.10
LINE = re.compile(r"(\d{1,2}):(\d{2})\s+([LS])\s+([\d.]+)\s*/\s*(\d{1,2}):(\d{2})\s+X\s+([\d.]+)\s*(\S*)")

def load_trades():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "peter_feed", "*_tr.txt"))):
        d = os.path.basename(f)[:10]
        for ln in open(f, encoding="utf-8", errors="replace"):
            m = LINE.search(ln)
            if not m:
                continue
            eh, em, side, ep, xh, xm, xp, why = m.groups()
            out.append(dict(date=d, et="%02d:%s" % (int(eh), em), side=side, ep=float(ep),
                            xt="%02d:%s" % (int(xh), xm), xp=float(xp), why=why))
    return out

def load_bars(con, t):
    rows = con.execute(
        "select substr(ts,12,5),open,high,low,close from regular_candles "
        "where code='10100' and trade_date=? and substr(ts,12,5)>? and substr(ts,12,5)<? order by ts",
        (t["date"], t["et"], t["xt"])).fetchall()
    return rows

def atr_at(con, t, n=14):
    rows = con.execute(
        "select high,low,close from regular_candles where code='10100' and trade_date=? "
        "and substr(ts,12,5)<=? order by ts desc limit ?", (t["date"], t["et"], n + 1)).fetchall()[::-1]
    if len(rows) < 3:
        return None
    trs = [max(h - l, abs(h - rows[i - 1][2]), abs(l - rows[i - 1][2])) for i, (h, l, c) in enumerate(rows) if i]
    return sum(trs) / len(trs)

def simulate(t, bars, rule):
    """rule(entry, peak_fav, atr) -> 보호 손절가(진입 방향 기준 pt, entry 대비 오프셋) 또는 None"""
    sgn = 1 if t["side"] == "L" else -1
    ep = t["ep"]
    peak = 0.0          # 최대 유리 이동(pt)
    prot = None         # 보호선(오프셋 pt, entry 기준 유리 방향 +)
    for hm, o, h, l, c in bars:
        fav_open = (o - ep) * sgn
        adverse = (l - ep) * sgn if sgn == 1 else (h - ep) * sgn   # 이 분봉 최악 지점
        if prot is not None and adverse <= prot:
            fill = fav_open if fav_open < prot else prot - SLIP
            return fill, hm, True, peak
        best = (h - ep) * sgn if sgn == 1 else (l - ep) * sgn
        peak = max(peak, best)
        p = rule(peak, t["atr"])
        if p is not None and (prot is None or p > prot):
            prot = p
    return (t["xp"] - ep) * sgn, t["xt"], False, peak

def R_none(peak, atr): return None
def R_trail(arm, back):
    return lambda peak, atr: (peak - back) if peak >= arm else None
def R_be(arm, lock):
    return lambda peak, atr: lock if peak >= arm else None
def R_pct(arm, keep):
    return lambda peak, atr: keep * peak if peak >= arm else None
def R_atr(arm_m, back_m):
    return lambda peak, atr: (peak - back_m * atr) if (atr and peak >= arm_m * atr) else None
def R_step(arm, lock, arm2, back2):
    def f(peak, atr):
        if peak >= arm2: return max(lock, peak - back2)
        if peak >= arm: return lock
        return None
    return f

def evaluate(trades, rule):
    res = []
    for t in trades:
        pnl, _, hit, _ = simulate(t, t["bars"], rule)
        res.append(pnl)
    return res

def main():
    con = sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "data", "db", "regular_candles.db"), uri=True)
    trades = load_trades()
    for t in trades:
        t["bars"] = load_bars(con, t)
        t["atr"] = atr_at(con, t)
    trades = [t for t in trades if t["bars"] is not None]
    base = evaluate(trades, R_none)
    # 데이터 점검: 베이스라인(=피터 실제) 대비 경로 MFE
    print("거래 %d건 · %d거래일 · 승 %d · 합계 %+.2fpt · 평균 ATR14 %.2f" % (
        len(trades), len({t['date'] for t in trades}), sum(p > 0 for p in base), sum(base),
        st.mean([t['atr'] for t in trades if t['atr']])))
    print("\n# 거래별 경로")
    for t, b in zip(trades, base):
        _, _, _, pk = simulate(t, t["bars"], R_none)
        print("%s %s %s %7.2f -> %s %7.2f  실현 %+6.2f  MFE %+6.2f  ATR %.2f  봉%d" % (
            t["date"], t["et"], t["side"], t["ep"], t["xt"], t["xp"], b, pk, t["atr"] or 0, len(t["bars"])))

    grid = []
    for arm in (3, 4, 5, 6, 7, 8, 10, 12):
        for back in (2, 3, 4, 5, 6, 8, 10):
            if back > arm + 4: continue
            grid.append(("trail arm%d back%d" % (arm, back), R_trail(arm, back)))
    for arm in (3, 4, 5, 6, 8, 10):
        for lock in (0, 1, 2, 3):
            if lock >= arm: continue
            grid.append(("BE arm%d lock%+d" % (arm, lock), R_be(arm, lock)))
    for arm in (4, 5, 6, 8, 10):
        for keep in (0.3, 0.4, 0.5, 0.6, 0.7):
            grid.append(("pct arm%d keep%.1f" % (arm, keep), R_pct(arm, keep)))
    for am in (2, 3, 4, 5, 6):
        for bm in (1.5, 2, 3, 4, 5):
            grid.append(("atr arm%.0fx back%.1fx" % (am, bm), R_atr(am, bm)))
    for arm, lock, arm2, back2 in itertools.product((4, 5, 6), (0, 1, 2), (8, 10, 12, 15), (4, 5, 6, 8)):
        if arm2 <= arm or lock >= arm: continue
        grid.append(("step %d→%+d, %d→peak-%d" % (arm, lock, arm2, back2), R_step(arm, lock, arm2, back2)))

    n = len(trades)
    half = sorted(range(n), key=lambda i: (trades[i]["date"], trades[i]["et"]))
    first, second = set(half[:n // 2]), set(half[n // 2:])
    rows = []
    for name, rule in grid:
        r = evaluate(trades, rule)
        d = [a - b for a, b in zip(r, base)]
        rows.append(dict(name=name, tot=sum(r), dlt=sum(d), d1=sum(d[i] for i in first),
                         d2=sum(d[i] for i in second), helped=sum(x > 0.05 for x in d),
                         hurt=sum(x < -0.05 for x in d), worst=min(d), wins=sum(p > 0 for p in r), r=r, d=d))
    rows.sort(key=lambda x: -x["dlt"])
    print("\n# 베이스라인(피터 실제) %+.2fpt\n# 상위 25 (Δ=규칙-피터, 전반/후반 = 시간순 반분)" % sum(base))
    for x in rows[:25]:
        print("%-34s 합계%+8.2f Δ%+7.2f 전반%+6.2f 후반%+6.2f 개선%2d 악화%2d 최악%+6.2f 승%2d" % (
            x["name"], x["tot"], x["dlt"], x["d1"], x["d2"], x["helped"], x["hurt"], x["worst"], x["wins"]))
    print("\n# 하위 5")
    for x in rows[-5:]:
        print("%-34s Δ%+7.2f 개선%2d 악화%2d" % (x["name"], x["dlt"], x["helped"], x["hurt"]))

    # 계열별 최선 + 부트스트랩 Δ>0 확률
    random.seed(7)
    print("\n# 계열별 최선 · 부트스트랩(2000회) Δ>0 확률 · Δ 95% 구간")
    fams = {}
    for x in rows:
        fams.setdefault(x["name"].split()[0], x)
    for k, x in fams.items():
        bs = []
        for _ in range(2000):
            idx = [random.randrange(n) for _ in range(n)]
            bs.append(sum(x["d"][i] for i in idx))
        bs.sort()
        print("%-6s %-34s Δ%+7.2f  P(Δ>0)=%.2f  95%%[%+.1f, %+.1f]" % (
            k, x["name"], x["dlt"], sum(b > 0 for b in bs) / len(bs), bs[50], bs[1949]))

    # 고원 확인: trail 계열 arm×back 격자 Δ 표
    print("\n# trail 격자 Δ (행 arm, 열 back)")
    backs = (2, 3, 4, 5, 6, 8, 10)
    print("arm\\back " + " ".join("%7d" % b for b in backs))
    lut = {x["name"]: x["dlt"] for x in rows}
    for arm in (3, 4, 5, 6, 7, 8, 10, 12):
        print("%8d " % arm + " ".join(
            ("%+7.1f" % lut["trail arm%d back%d" % (arm, b)]) if ("trail arm%d back%d" % (arm, b)) in lut else "      -"
            for b in backs))
    return trades, rows, base

def _unused():
    pass


def atr_surface_and_oos(trades, base):
    """ATR 비례 계열의 고원(plateau)과 시간 분할 표본외 검증 — 제안 규칙 근거."""
    arms = (2, 3, 3.5, 4, 4.5, 5, 5.5, 6, 7)
    backs = (2, 2.5, 3, 3.5, 4, 4.5, 5, 6)
    D = {(a, b): [x - y for x, y in zip(evaluate(trades, R_atr(a, b)), base)] for a in arms for b in backs}
    print("\n# ATR 계열 Δ (행 arm×ATR, 열 back×ATR)")
    print("arm\back " + " ".join("%7s" % b for b in backs))
    for a in arms:
        print("%8s " % a + " ".join("%+7.1f" % sum(D[(a, b)]) for b in backs))
    n = len(trades)
    order = sorted(range(n), key=lambda i: (trades[i]["date"], trades[i]["et"]))
    for cut in (0.4, 0.5, 0.6):
        k = int(n * cut)
        A, B = set(order[:k]), set(order[k:])
        g = max(D, key=lambda g: sum(D[g][i] for i in A))
        print("분할 %.0f%%: 앞(~%s)에서 고른 %s → 앞Δ%+.1f 뒤Δ%+.1f" % (
            cut * 100, trades[order[k - 1]]["date"], g, sum(D[g][i] for i in A), sum(D[g][i] for i in B)))
    days = sorted({t["date"] for t in trades})
    byday = {d: [i for i, t in enumerate(trades) if t["date"] == d] for d in days}
    random.seed(11)
    for g in ((4.5, 3.5), (4, 3.5), (5, 3.5), (7, 3)):
        bs = sorted(sum(sum(D[g][i] for i in byday[random.choice(days)]) for _ in days) for _ in range(4000))
        print("ATR arm%.1fx back%.1fx Δ%+.1f 일자부트스트랩 P(Δ>0)=%.2f" % (
            g[0], g[1], sum(D[g]), sum(b > 0 for b in bs) / len(bs)))


if __name__ == "__main__":
    _t, _rows, _base = main()
    atr_surface_and_oos(_t, _base)

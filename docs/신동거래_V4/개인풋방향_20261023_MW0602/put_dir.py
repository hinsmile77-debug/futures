# -*- coding: utf-8 -*-
"""개인 풋 단독 방향안 — 콜−풋 대신 개인 위클리 풋 순매수(백만원)의 변화로 방향. 읽기 전용(DB 미기록).

방향: 풋 변화 ≥ +K → 매수 · ≤ −K → 매도 (콜−풋 ↓ → 매수 인 현행 역추종과 같은 쪽).
변형:  A = 첫 거래(FLOWC 누적, 09:00 대비)만 풋 · B = 2·3번째(R60, 최근 60분)만 풋 · C = 둘 다 풋.
나머지(재난손절 0.6×ATR · 트레일 6/4 · 익절 12 · 15:05 · 하루 3건 · 손절 방향 누적 금지)는 v3 그대로.
엔진 `families.run_family_day("hybr60")` 를 쓰고 신호 함수 2개만 런타임에 바꿔 끼운다(원본 무수정 · 복원).

문턱 선택: ① 격자 전체 면 ② 워크포워드 — 평가일 t 마다 t 이전 날만으로 문턱을 골라 t 에 적용
(최소 학습 5일 · 기준 = 학습 순손익 최대, 동률이면 학습 최악일이 나은 쪽).
"""
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.isdir(os.path.join(ROOT, "strategy")):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(HERE, "..", "신동v3_꼬리위험_20261023_MW0602"))
os.chdir(ROOT)
import sim                                                     # noqa: E402
from strategy.shindong import engine as E, families as F, spec as S   # noqa: E402

OF, OR = F._flow_signal, F._roll_signal
KC_GRID = (50, 75, 100, 150, 200, 300, 400)       # 풋 누적(09:00 대비)
KR_GRID = (25, 50, 75, 100, 150, 200, 300)        # 풋 최근 60분
A_END, B_START, OOS, MIN_TRAIN = "2026-10-08", "2026-10-12", "2026-10-19", 5


def day_net(day, kc=None, kr=None):
    """kc: 첫 거래를 풋 누적 문턱 kc 로(None = 콜−풋 300) · kr: R60 을 풋 60분 문턱 kr 로(None = 콜−풋 150)."""
    d, L = sim.frame(day)
    put = d.put

    def fs(dd, series, k, sign):
        return OF(dd, put, kc, +1) if (kc is not None and series is dd.sp) else OF(dd, series, k, sign)

    def rsig(series, win, k, sign):
        return OR(put, win, kr, +1) if (kr is not None and series is d.sp) else OR(series, win, k, sign)
    F._flow_signal, F._roll_signal = fs, rsig
    try:
        r = F.run_family_day(d, L, "hybr60")
    finally:
        F._flow_signal, F._roll_signal = OF, OR
    trs = [t for t in r["trades"] if t["status"] == "CLOSED"]
    return sum(E.trade_net(t) for t in trs) / 2 / S.PT_VALUE_KRW, len(trs)


DAYS = sim.days()
CACHE = {}


def series(kc, kr):
    key = (kc, kr)
    if key not in CACHE:
        CACHE[key] = {d: day_net(d, kc, kr) for d in DAYS}
    return CACHE[key]


def summ(s):
    v = {d: x[0] for d, x in s.items()}
    return dict(tot=sum(v.values()), a=sum(x for d, x in v.items() if d <= A_END), b=sum(x for d, x in v.items() if d >= B_START),
                oos=sum(x for d, x in v.items() if d >= OOS), worst=min(v.values()), n=sum(x[1] for x in s.values()),
                pos=sum(1 for x in v.values() if x > 0))


BASE = series(None, None)
B0 = summ(BASE)
print("일수 %d (%s~%s) · 기준 v3: 합계 %+.1f · 전반 %+.1f · 후반 %+.1f · 10/19~ %+.1f · 최악일 %.1f · 거래 %d" % (
    len(DAYS), DAYS[0], DAYS[-1], B0["tot"], B0["a"], B0["b"], B0["oos"], B0["worst"], B0["n"]))

VARS = {"A 첫거래=풋": [(kc, None) for kc in KC_GRID],
        "B R60=풋": [(None, kr) for kr in KR_GRID],
        "C 둘다=풋": list(itertools.product(KC_GRID, KR_GRID))}

for name, cands in VARS.items():
    print("\n## %s — 격자 (합계 / 전반 / 후반 / 10/19~ / 최악일 / 거래)" % name)
    for kc, kr in cands:
        s = summ(series(kc, kr))
        print("  kc=%-4s kr=%-4s %+7.1f (Δ%+6.1f) | %+6.1f %+6.1f | %+6.1f | %6.1f | %3d | 이익일 %d" % (
            kc, kr, s["tot"], s["tot"] - B0["tot"], s["a"], s["b"], s["oos"], s["worst"], s["n"], s["pos"]))
    # 워크포워드
    wf, picks = {}, []
    for i, day in enumerate(DAYS):
        if i < MIN_TRAIN:
            continue
        tr = DAYS[:i]

        def score(c):
            s = series(*c)
            return (sum(s[d][0] for d in tr), min(s[d][0] for d in tr))
        best = max(cands, key=score)
        picks.append((day[5:], best))
        wf[day] = series(*best)[day][0]
    ev = list(wf)
    base_ev = {d: BASE[d][0] for d in ev}
    print("  ▶ 워크포워드 %d일(%s~): %+.1f vs 기준 %+.1f (Δ%+.1f) · 최악일 %.1f vs %.1f · 10/19~ %+.1f vs %+.1f" % (
        len(ev), ev[0][5:], sum(wf.values()), sum(base_ev.values()), sum(wf.values()) - sum(base_ev.values()),
        min(wf.values()), min(base_ev.values()),
        sum(v for d, v in wf.items() if d >= OOS), sum(v for d, v in base_ev.items() if d >= OOS)))
    print("    선택 문턱:", " ".join("%s:%s" % (d, "/".join(str(x) for x in c if x is not None)) for d, c in picks))

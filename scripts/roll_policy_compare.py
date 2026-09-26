# -*- coding: utf-8 -*-
# scripts/roll_policy_compare.py — 롤 정책 3안 워크포워드 대조 (읽기 전용)
"""`ROLL_POLICY` = off / exclude / adjust 를 같은 데이터·같은 함수로 돌려 비교한다.

무엇을 재는가
-------------
09:30 거리 모델(`fit_stage2_at` + `distance_stage2`)의 **표본외 예측오차**다.
각 세션 i 에 대해 직전 60세션으로 적합하고, 세션 i 의 실제 (고가−시가)/ATR,
(시가−저가)/ATR 을 맞히게 해 절대오차 중앙값을 본다. 적합·예측 모두
**프로덕션과 같은 함수**를 쓴다 — 다른 코드로 재현하면 무엇을 잰 건지 알 수 없다.

  off      기존 동작 (롤 오염 그대로)
  exclude  롤 당일을 이력에서 제외 (표본 9%% 손실)
  adjust   갭에 롤 점프를 더해 상쇄 (표본 유지)

⚠ 어떤 DB 에도 쓰지 않는다. `raw_data.db`·`regular_candles.db` 를 읽기 전용으로만 연다.

실행:  python scripts/roll_policy_compare.py [--since 2025-08-01]
"""
from __future__ import print_function
import argparse, os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from features.levels import levels_store as LS
from features.levels import premarket_levels as PL

OUT = []
def P(s=""):
    print(s); OUT.append(str(s))


def build(sessions, policy, labels):
    """정책에 맞는 요약 리스트를 만든다."""
    if policy == "exclude":
        sessions = [(d, b) for d, b in sessions if d not in labels]
    ss = [PL.summarize_session(d, b) for d, b in sessions]
    if policy == "adjust":
        for s in ss:
            s.roll_adj = labels.get(s.d, 0.0)
    PL.fill_derived(ss)
    return ss


def walk(ss, labels):
    """워크포워드: 직전 60세션 적합 → 당일 예측 → 절대오차."""
    rows = []
    for i in range(PL.TRAIN_SESSIONS, len(ss)):
        s, prev = ss[i], ss[i - 1]
        if not s.atr or s.atr <= 0 or s.u_t is None or (prev.h - prev.l) <= 0:
            continue
        p2 = PL.fit_stage2_at(ss[:i], i, None)
        if not p2:
            continue
        path = (s.u_t, s.d_t, s.ret_t)
        # R̂ 스케일 경로 — `_x_fixed` 가 갭을 2개 항(부호·절대값)으로 쓴다
        rh2 = PL.fit_rhat(ss[:i], i, True, None)
        xf = PL._x_fixed(s, prev, PL.atr_of(ss, i, 5))
        x2 = (xf + [__import__("math").log(max(path[0] + path[1], 1e-3)), abs(path[2])]) if xf else None
        sc = PL.rhat_scale(rh2, x2)
        dist = PL.distance_stage2(p2, s.o, s.atr, PL._gap_pt(s, prev), prev.h - prev.l, path, sc)
        eu = abs((dist["high"] - s.o) / s.atr - (s.h - s.o) / s.atr)
        ed = abs((s.o - dist["low"]) / s.atr - (s.o - s.l) / s.atr)
        hit = (dist["low"] <= s.l and dist["high"] >= s.h)
        # _band 는 (하한, 상한) 짝 — 밴드의 바깥쪽 끝으로 포함 여부를 본다
        c50 = (dist["low50"][0] <= s.l and dist["high50"][1] >= s.h)
        c80 = (dist["low80"][0] <= s.l and dist["high80"][1] >= s.h)
        w80 = (dist["high80"][1] - dist["low80"][0]) / s.atr
        rows.append((s.d, eu, ed, hit, s.d in labels, s.atr, c50, c80, w80))
    return rows


def stat(rows, pick=None):
    r = [x for x in rows if pick is None or pick(x)]
    if not r:
        return None
    eu = np.array([x[1] for x in r]); ed = np.array([x[2] for x in r])
    both = np.concatenate([eu, ed])
    return dict(n=len(r), mae=float(both.mean()), med=float(np.median(both)),
                p90=float(np.percentile(both, 90)),
                cover=float(np.mean([x[3] for x in r])),
                c50=float(np.mean([x[6] for x in r])), c80=float(np.mean([x[7] for x in r])),
                w80=float(np.median([x[8] for x in r])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=LS.HISTORY_SINCE)
    a = ap.parse_args()

    P("[데이터] raw_candles 이력 로드 (since=%s)" % a.since)
    sessions, excluded = LS.load_sessions(since=a.since)      # 정책 off 기준 원본
    labels = LS.roll_labels()
    P("  세션 %d개 / 품질 제외 %d개 / 롤 라벨 %d개" % (len(sessions), len(excluded), len(labels)))
    hit = [d for d, _ in sessions if d in labels]
    P("  이력에 남아 있는 롤 당일: %d개" % len(hit))

    res = {}
    for pol in ("off", "exclude", "adjust"):
        ss = build(sessions, pol, labels)
        rows = walk(ss, labels)
        res[pol] = rows
        P("  [%s] 평가 세션 %d개" % (pol, len(rows)))

    P("\n=== 표본외 예측오차 (ATR 단위, 낮을수록 좋다) ===")
    P("  정책      n    MAE     중앙   p90    구간적중률")
    for pol in ("off", "exclude", "adjust"):
        st = stat(res[pol])
        P("  %-8s %4d  %.4f  %.4f  %.4f   %5.1f%%"
          % (pol, st["n"], st["mae"], st["med"], st["p90"], 100 * st["cover"]))

    P("\n=== 롤 당일만 (오염이 직접 작용하는 표본) ===")
    P("  정책      n    MAE     중앙   p90    구간적중률")
    for pol in ("off", "adjust"):
        st = stat(res[pol], pick=lambda x: x[4])
        if st:
            P("  %-8s %4d  %.4f  %.4f  %.4f   %5.1f%%"
              % (pol, st["n"], st["mae"], st["med"], st["p90"], 100 * st["cover"]))

    P("\n=== 저변동 국면(ATR<20) — 오염 비중이 가장 컸던 구간 ===")
    P("  정책      n    MAE     중앙   p90    구간적중률")
    for pol in ("off", "exclude", "adjust"):
        st = stat(res[pol], pick=lambda x: x[5] < 20)
        if st:
            P("  %-8s %4d  %.4f  %.4f  %.4f   %5.1f%%"
              % (pol, st["n"], st["mae"], st["med"], st["p90"], 100 * st["cover"]))

    base = stat(res["off"])
    P("\n=== R̂ 스케일 밴드 적중률 (명목 50%% / 80%%) + 80%% 밴드 폭(ATR 단위) ===")
    P("  정책      n    50%%밴드  80%%밴드  밴드폭")
    for pol in ("off", "exclude", "adjust"):
        st = stat(res[pol])
        P("  %-8s %4d  %5.1f%%  %5.1f%%  %.3f" % (pol, st["n"], 100*st["c50"], 100*st["c80"], st["w80"]))
    P("  롤 당일만:")
    for pol in ("off", "adjust"):
        st = stat(res[pol], pick=lambda x: x[4])
        if st: P("    %-8s %4d  %5.1f%%  %5.1f%%  %.3f" % (pol, st["n"], 100*st["c50"], 100*st["c80"], st["w80"]))

    P("\n=== off 대비 ===")
    for pol in ("exclude", "adjust"):
        st = stat(res[pol])
        P("  %-8s MAE %+.2f%%  중앙 %+.2f%%  적중률 %+.1f%%p"
          % (pol, 100 * (st["mae"] / base["mae"] - 1), 100 * (st["med"] / base["med"] - 1),
             100 * (st["cover"] - base["cover"])))
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "logs", "roll_policy_compare.txt")
    try:
        open(path, "w").write("\n".join(OUT) + "\n")
        print("[저장] %s" % path)
    except Exception as e:
        print("[저장 실패] %r" % e)


if __name__ == "__main__":
    sys.exit(main())

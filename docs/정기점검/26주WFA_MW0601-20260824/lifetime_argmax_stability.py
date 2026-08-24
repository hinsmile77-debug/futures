# -*- coding: utf-8 -*-
"""[MW0601] "IC 최강 h" 배정의 시간 안정성 — 사용자 제안의 **전제 조건** 검정.

사용자 제안(2026-08-24): "발굴 25개를 IC 최강 h에 배치한 대로 배정하고 방향모델을
학습하면 더 나은 방향 정보원이 되지 않는가."

그 제안이 성립하려면 **배정이 안정적**이어야 한다. 전반기에 h=5가 최강이던 피처가
후반기엔 h=30이 최강이라면, 그 배정은 신호가 아니라 노이즈를 고정하는 것이다.
학습에 쓰면 과거의 표본변동을 미래 구조로 착각해 굳히게 된다.

## 전반기/후반기 구분 기준 (사전 고정)

  ① 대상은 IC 유효일 31거래일(2026-06-02 ~ 2026-08-24).
  ② **날짜순으로 정렬한 뒤 앞 15일 / 뒤 16일.**
     `scripts/core_feature_discovery.py:290`의 `half = len(day_tag) // 2` 관례 그대로다.
     이 배터리가 이미 쓰는 분할이므로 새 기준을 만들지 않는다.
  ③ **무작위 분할이 아니라 시간순 분할이다.** 시계열에서 날짜를 섞어 나누면
     같은 국면의 이웃 날짜가 양쪽에 흩어져 "안정적"으로 보이는 착시가 생긴다.

## 분할점 자의성 — 두 가지 통제

  통제 A  분할점을 10~21일 사이에서 옮기며 일치율을 다시 잰다.
          한 지점(15일)에서만 성립/불성립하는 결론을 막는다.
  통제 B  **홀수일 vs 짝수일** 분할을 대조군으로 둔다.
          시간순 분할은 '시장 국면 변화 + 표본변동'을 함께 담지만,
          홀짝 분할은 국면 변화를 양쪽에 고르게 섞어 **표본변동만** 남긴다.
            · 시간순 낮음 ∧ 홀짝 높음 -> 배정이 시기에 따라 바뀐다(국면 의존)
            · 둘 다 낮음               -> argmax 자체가 표본 노이즈다
"""
from __future__ import print_function

import io
import json
import math
import os
import sys

import numpy as np

_ROOT = r"C:\Users\82108\PycharmProjects\futures"
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from utils.dll_bootstrap import ensure_conda_dll_path

ensure_conda_dll_path()
from scripts.core_feature_discovery import build_matrix, analyze

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live_only import load_live

IC_HZ = [1, 3, 5, 10, 15, 30]


def subset(X, ts_list, keep_days):
    idx = [i for i, t in enumerate(ts_list) if t[:10] in keep_days]
    return X[idx, :], [ts_list[i] for i in idx]


def argmax_map(names, X, ts_list, closes, targets):
    """피처별 argmax_h와 IC t 프로파일."""
    prof = {n: [] for n in targets}
    for h in IC_HZ:
        res, _nd = analyze(names, X, ts_list, closes, h)
        d = {r["name"]: r["ic_t"] for r in res}
        for n in targets:
            prof[n].append(d.get(n, float("nan")))
    out = {}
    for n in targets:
        ts = prof[n]
        if any(not np.isfinite(t) for t in ts):
            continue
        a = [abs(t) for t in ts]
        i = int(np.argmax(a))
        srt = sorted(a, reverse=True)
        out[n] = dict(best_h=IC_HZ[i], best_abs=srt[0],
                      margin=(srt[0] - srt[1]) / max(1e-9, srt[0]), prof=ts)
    return out


def agree(m1, m2):
    common = [n for n in m1 if n in m2]
    hit = [n for n in common if m1[n]["best_h"] == m2[n]["best_h"]]
    return len(hit), len(common), hit


def perm_p(m1, m2, obs, n_common, seed=20260824, N=20000):
    """두 분할의 argmax 짝을 섞었을 때 obs 이상 일치할 확률."""
    common = [n for n in m1 if n in m2]
    a = [m1[n]["best_h"] for n in common]
    b = [m2[n]["best_h"] for n in common]
    rng = np.random.RandomState(seed)
    cnt = 0
    for _ in range(N):
        if sum(1 for x, y in zip(a, rng.permutation(b)) if x == y) >= obs:
            cnt += 1
    return (cnt + 1.0) / (N + 1.0)


def main():
    L = io.StringIO()

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        L.write(s + "\n")

    fin = json.load(open("lifetime_tau_final.json", encoding="utf-8"))
    targets = [d["nm"] for d in fin["discovered"]]

    feats, closes, dates = load_live()
    names, X, ts_list = build_matrix(feats, verbose=False)
    days = sorted({t[:10] for t in ts_list})
    nd = len(days)
    half = nd // 2

    P("=" * 110)
    P("[MW0601] 'IC 최강 h' 배정의 시간 안정성 — 발굴 %d개 대상" % len(targets))
    P("=" * 110)
    P("관찰창 %s ~ %s · %d거래일" % (days[0], days[-1], nd))
    P("")
    P("[전반기/후반기 구분 기준]")
    P("  · 날짜순 정렬 후 앞 %d일 / 뒤 %d일 (core_feature_discovery.py:290 관례)"
      % (half, nd - half))
    P("  · 전반기: %s ~ %s" % (days[0], days[half - 1]))
    P("  · 후반기: %s ~ %s" % (days[half], days[-1]))
    P("  · 무작위가 아니라 **시간순** 분할 — 날짜를 섞으면 같은 국면이 양쪽에 흩어져")
    P("    안정적으로 보이는 착시가 생긴다.")

    # ── 주 분할 ────────────────────────────────────────────────────
    d1, d2 = set(days[:half]), set(days[half:])
    X1, t1 = subset(X, ts_list, d1)
    X2, t2 = subset(X, ts_list, d2)
    m1 = argmax_map(names, X1, t1, closes, targets)
    m2 = argmax_map(names, X2, t2, closes, targets)
    full = argmax_map(names, X, ts_list, closes, targets)

    hit, n_common, hit_names = agree(m1, m2)
    p = perm_p(m1, m2, hit, n_common)

    P("\n" + "=" * 110)
    P("[1] 전반기 vs 후반기 — 같은 피처가 같은 h에서 최강인가")
    P("=" * 110)
    P("%-30s %10s %10s %10s %9s %8s"
      % ("피처", "전체창", "전반기", "후반기", "일치", "여유*"))
    P("-" * 110)
    for n in targets:
        if n not in m1 or n not in m2:
            P("%-30s %10s %10s %10s %9s" % (n[:30], "-", "-", "-", "산출불가"))
            continue
        ok = m1[n]["best_h"] == m2[n]["best_h"]
        P("%-30s %10s %10s %10s %9s %7.0f%%"
          % (n[:30],
             "h=%d" % full[n]["best_h"] if n in full else "-",
             "h=%d" % m1[n]["best_h"], "h=%d" % m2[n]["best_h"],
             "**O**" if ok else "X", full[n]["margin"] * 100 if n in full else 0))
    P("\n  * 여유 = (최강|t| - 차순위|t|) / 최강|t|. 작을수록 argmax가 표본변동에 흔들린다.")
    P("\n   일치 **%d / %d** (%.1f%%) · 순열 p = %.4f"
      % (hit, n_common, 100.0 * hit / max(1, n_common), p))
    P("   우연 기대치 ≈ %.1f개 (6개 중 하나를 맞히는 셈)" % (n_common / 6.0))

    # ── 통제 A: 분할점 이동 ────────────────────────────────────────
    P("\n" + "=" * 110)
    P("[2] 통제 A — 분할점을 옮겨도 같은가 (10~21일)")
    P("=" * 110)
    P("%8s  %-24s %9s %9s" % ("분할점", "경계", "일치", "비율"))
    P("-" * 110)
    rates = []
    for cut in range(10, min(22, nd - 9)):
        a, b = set(days[:cut]), set(days[cut:])
        Xa, ta = subset(X, ts_list, a)
        Xb, tb = subset(X, ts_list, b)
        ma = argmax_map(names, Xa, ta, closes, targets)
        mb = argmax_map(names, Xb, tb, closes, targets)
        h, c, _ = agree(ma, mb)
        if c:
            rates.append(h / float(c))
            P("%8d  %-24s %9s %8.1f%%"
              % (cut, "%s | %s" % (days[cut - 1], days[cut]), "%d/%d" % (h, c),
                 100.0 * h / c))
    if rates:
        P("\n   분할점 %d개에서 일치율 평균 %.1f%% · 범위 %.1f~%.1f%%"
          % (len(rates), 100 * np.mean(rates), 100 * min(rates), 100 * max(rates)))
        P("   -> 특정 분할점에서만 나온 결론이 아니다." if np.std(rates) < 0.15
          else "   -> 분할점에 따라 흔들린다 — 해석 주의.")

    # ── 통제 B: 홀짝 분할 ──────────────────────────────────────────
    P("\n" + "=" * 110)
    P("[3] 통제 B — 홀수일 vs 짝수일 (시장 국면 변화를 양쪽에 고르게 섞은 대조군)")
    P("=" * 110)
    od, ev = set(days[0::2]), set(days[1::2])
    Xo, to = subset(X, ts_list, od)
    Xe, te = subset(X, ts_list, ev)
    mo = argmax_map(names, Xo, to, closes, targets)
    me = argmax_map(names, Xe, te, closes, targets)
    h3, c3, _ = agree(mo, me)
    p3 = perm_p(mo, me, h3, c3)
    P("   홀수일 %d개 vs 짝수일 %d개" % (len(od), len(ev)))
    P("   일치 **%d / %d** (%.1f%%) · 순열 p = %.4f"
      % (h3, c3, 100.0 * h3 / max(1, c3), p3))
    P("")
    P("   [대조] 시간순 %.1f%%  vs  홀짝 %.1f%%"
      % (100.0 * hit / max(1, n_common), 100.0 * h3 / max(1, c3)))
    if c3 and n_common:
        r_time, r_oe = hit / float(n_common), h3 / float(c3)
        if r_oe - r_time > 0.15:
            P("   -> 홀짝이 뚜렷이 높다 = 배정이 **시기에 따라 바뀐다**(국면 의존).")
        elif max(r_time, r_oe) < 0.35:
            P("   -> **둘 다 낮다 = argmax 자체가 표본 노이즈다.**")
        else:
            P("   -> 둘 다 어느 정도 재현된다.")

    # ── 여유 분포 ──────────────────────────────────────────────────
    P("\n" + "=" * 110)
    P("[4] argmax의 '여유' — 최강과 차순위가 얼마나 벌어져 있나")
    P("=" * 110)
    mg = [full[n]["margin"] for n in targets if n in full]
    if mg:
        mg = np.array(mg)
        P("   여유 중앙값 %.1f%% · 25%%=%.1f%% · 75%%=%.1f%%"
          % (100 * np.median(mg), 100 * np.percentile(mg, 25), 100 * np.percentile(mg, 75)))
        P("   여유 < 10%% 인 피처 %d/%d — 이들은 최강과 차순위가 사실상 동률이라"
          % (int((mg < 0.10).sum()), mg.size))
        P("   배정이 표본을 조금만 바꿔도 뒤집힌다.")

    json.dump(dict(days=[days[0], days[-1]], n_days=nd, half=half,
                   boundary=[days[half - 1], days[half]],
                   time_split=dict(hit=hit, n=n_common, p=p, hits=hit_names),
                   cut_rates=rates,
                   odd_even=dict(hit=h3, n=c3, p=p3),
                   margins={n: full[n]["margin"] for n in full},
                   best_full={n: full[n]["best_h"] for n in full},
                   best_h1={n: m1[n]["best_h"] for n in m1},
                   best_h2={n: m2[n]["best_h"] for n in m2}),
              open("lifetime_argmax_stability.json", "w", encoding="utf-8"),
              ensure_ascii=False, default=float)
    with open("lifetime_argmax_stability.txt", "w", encoding="utf-8") as f:
        f.write(L.getvalue())
    P("\n저장 -> lifetime_argmax_stability.txt / .json")


if __name__ == "__main__":
    main()

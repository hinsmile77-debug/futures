# -*- coding: utf-8 -*-
"""[MW0601] 중복 피처 점검 — tau/IC/분포가 완전히 같은 쌍이 있다.

tau 검정에서 두 쌍이 소수점까지 동일하게 나왔다:
   opt_pcr_extreme_signed / opt_pcr_norm      tau 39.5 · rank 35.5 · t 7.96 · 동률 74%
   queue_depletion_speed  / queue_refill_rate tau 1.5  · 첨도 8682/8679 · 점질량 41.7%

우연이 아니라 **같은 값을 두 이름으로 저장**하고 있을 가능성이 높다. 그렇다면
학습 X에 중복 열이 들어가고, L1·L2 검정 수가 부풀려지며(다중비교 보정이 과해진다),
SHAP 기여가 둘로 쪼개진다. 전수로 확인한다.
"""
from __future__ import print_function

import io
import json
import os
import sys

import numpy as np

_ROOT = r"C:\Users\82108\PycharmProjects\futures"
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from utils.dll_bootstrap import ensure_conda_dll_path

ensure_conda_dll_path()
from scripts.core_feature_discovery import build_matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live_only import load_live


def main():
    L = io.StringIO()

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s)
        L.write(s + "\n")

    feats, closes, dates = load_live()
    names, X, ts_list = build_matrix(feats, verbose=False)
    n = len(names)

    P("=" * 104)
    P("[MW0601] 중복 피처 전수 점검 — 순수 라이브 %d거래일 · %d피처" % (len(dates), n))
    P("=" * 104)

    exact, near, prop = [], [], []
    for i in range(n):
        a = X[:, i].astype(np.float64)
        for j in range(i + 1, n):
            b = X[:, j].astype(np.float64)
            m = np.isfinite(a) & np.isfinite(b)
            if m.sum() < 200:
                continue
            aa, bb = a[m], b[m]
            if np.array_equal(aa, bb):
                exact.append((names[i], names[j], int(m.sum())))
                continue
            sa, sb = aa.std(), bb.std()
            if sa <= 0 or sb <= 0:
                continue
            r = float(np.corrcoef(aa, bb)[0, 1])
            if abs(r) >= 0.9999:
                # 완전 선형 종속 — 배율/부호만 다른가
                k = float(np.dot(aa, bb) / np.dot(aa, aa))
                prop.append((names[i], names[j], r, k, int(m.sum())))
            elif abs(r) >= 0.99:
                near.append((names[i], names[j], r, int(m.sum())))

    P("\n[1] **값이 완전히 동일** — %d쌍" % len(exact))
    if exact:
        for a, b, k in exact:
            P("   %-34s == %-34s (겹치는 관측 %d)" % (a, b, k))
    else:
        P("   없음")

    P("\n[2] **선형 종속** (|r| >= 0.9999, 배율·부호만 차이) — %d쌍" % len(prop))
    for a, b, r, k, m in prop:
        P("   %-32s ~ %-32s r=%+.6f  b≈%.4f×a  (n=%d)" % (a, b, r, k, m))

    P("\n[3] 매우 높은 상관 (0.99 <= |r| < 0.9999) — %d쌍" % len(near))
    for a, b, r, m in sorted(near, key=lambda z: -abs(z[2]))[:20]:
        P("   %-32s ~ %-32s r=%+.5f (n=%d)" % (a, b, r, m))

    P("\n" + "=" * 104)
    P("[영향]")
    P("  · 중복 열은 L1·L2 **검정 수를 부풀린다** -> Bonferroni 임계가 필요 이상으로 높아져")
    P("    실제 신호를 더 많이 탈락시킨다(이번 창 임계 |t|>=6.44).")
    P("  · 학습 X에 같은 정보가 두 번 들어가면 트리 모델의 분기 선택과 SHAP 기여가")
    P("    두 이름으로 쪼개진다 — 중요도 해석이 왜곡된다.")
    P("  · 판정·설정 변경은 하지 않는다(절대원칙 §6). 이 표는 기록이다.")
    P("=" * 104)

    json.dump(dict(exact=[dict(a=a, b=b, n=k) for a, b, k in exact],
                   proportional=[dict(a=a, b=b, r=r, k=k, n=m) for a, b, r, k, m in prop],
                   near=[dict(a=a, b=b, r=r, n=m) for a, b, r, m in near]),
              open("lifetime_dup_check.json", "w", encoding="utf-8"), ensure_ascii=False)
    with open("lifetime_dup_check.txt", "w", encoding="utf-8") as f:
        f.write(L.getvalue())
    P("\n저장 -> lifetime_dup_check.txt / .json")


if __name__ == "__main__":
    main()

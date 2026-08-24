# -*- coding: utf-8 -*-
import json, io, os, sys
sys.path.insert(0, os.path.normpath("C:/Users/82108/PycharmProjects/futures"))
from utils.dll_bootstrap import ensure_conda_dll_path
ensure_conda_dll_path()
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
B = r"C:\Users\82108\AppData\Local\Temp\claude\c--Users-82108-PycharmProjects-futures\3da3ba26-bb1e-4099-afe8-f02e11a996bd\scratchpad\wfa"
live = json.load(io.open(B + r"\live_only.json", encoding="utf-8"))
cells = live["cells"]; D = float(live["days"])

def rank(a):
    a = np.asarray(a, dtype=float)
    o = np.argsort(a, kind="mergesort"); r = np.empty(a.size, float); r[o] = np.arange(1, a.size + 1)
    s = a[o]; i = 0
    while i < s.size:
        j = i
        while j + 1 < s.size and s[j + 1] == s[i]: j += 1
        if j > i: r[o[i:j + 1]] = (i + 1 + j + 1) / 2.0
        i = j + 1
    return r

tr = np.array([c["ntr"] / D for c in cells]); net = np.array([c["net"] for c in cells])
rho = float(np.corrcoef(rank(tr), rank(net))[0, 1])
print("전체 %d셀 — 거래수/일 vs net/일 순위상관 rho = %+.4f" % (len(cells), rho))
P = [c for c in cells if c["net"] > 0 and abs(c["t"]) >= 2 and c["h1"] is not None and c["h1"] > 0 and c["h2"] > 0]
mp = float(np.median([c["ntr"] / D for c in P])); ma = float(np.median(tr))
print()
print("합격 9셀 거래/일 중앙값 %.1f  vs  전체 중앙값 %.1f  →  **%.1f배 적게 거래**" % (mp, ma, ma / mp))
print()
for h in [1, 3, 5, 10, 15, 30]:
    g = [c for c in cells if c["h"] == h]
    print("  h=%-3d 거래/일 중앙 %6.1f | net/일 중앙 %8.3f" % (
        h, np.median([c["ntr"] / D for c in g]), np.median([c["net"] for c in g])))
print()
jack = {"toxicity_flow_stress": True, "toxicity_queue_stress": True, "imbalance_slope": True,
        "ofi_norm": False, "microprice_slope": False, "quality_investor_age_sec": True,
        "va_bandwidth": False, "cvd": False, "macro_nasdaq_chg": False}
NZ_T, NZ_NET = 2.92, 18.5277
print("=== 3중 통제 생존표 ===")
print("%-26s %8s %8s %10s %10s %10s" % ("feature", "t", "거래/일", "노이즈하한", "잭나이프", "최종"))
n = 0
for c in sorted(P, key=lambda c: -c["net"]):
    nz = (abs(c["t"]) > NZ_T and c["net"] > NZ_NET)
    jk = jack.get(c["nm"], False)
    fin = nz and jk; n += fin
    print("%-26s %8.2f %8.1f %10s %10s %10s" % (
        c["nm"], c["t"], c["ntr"] / D, "통과" if nz else "미달", "유지" if jk else "탈락", "O" if fin else "**X**"))
print("→ 세 통제를 모두 통과한 셀: **%d / 9**" % n)

# -*- coding: utf-8 -*-
"""R1 수집일(9/21)부터 제안 루프를 그대로 돌렸다면 — 6일 전진 검증.
매일: 그날 이전 흐름일로만 조합을 고르고(훈련 최소 1일) 그날 적용. 9/21 은 훈련 데이터가 없어 거래 없음(미측정).
python loop_flow6.py <grid_all.json>"""
import json, sys, collections, statistics as stt
G = json.load(open(sys.argv[1], encoding="utf-8"))
M = 1e4
FD = ["2026-09-21", "2026-09-22", "2026-09-23", "2026-09-28", "2026-09-29", "2026-09-30"]
MAIN = {"2026-09-21": -617000, "2026-09-22": 1630000, "2026-09-23": 1824000, "2026-09-28": 330000, "2026-09-29": -1038000, "2026-09-30": -512000}
FAMS = [("A", None), ("B", "r1"), ("B", "none"), ("C", None), ("D", "r1"), ("D", "none"), ("E", "r1"), ("E", "none")]


def table(fam, filt):
    t = collections.defaultdict(dict)
    for d in FD:
        for p, net, n in G[d]["fam"].get(fam, []):
            if filt and json.loads(p).get("filt") != filt:
                continue
            t[p][d] = (net, n)
    return t


def wf(t, pol):
    """day -> (net, n, params) ; 방향일에만 값이 있는 계열(A·r1)은 그날이 보류면 0 거래."""
    out = {}
    cur = None
    for i, d in enumerate(FD):
        tr = [x for x in FD[:i] if any(x in t[p] for p in t)]
        if not tr:
            out[d] = None
            continue
        cand = [p for p in t if all(x in t[p] for x in tr)]
        if pol == "rank":
            sc = collections.defaultdict(float)
            for dd in tr:
                for r, p in enumerate(sorted(cand, key=lambda p: t[p][dd][0])):
                    sc[p] += r / len(cand)
        else:
            sc = {p: sum(t[p][dd][0] for dd in tr) for p in cand}
        best = max(cand, key=lambda p: sc[p])
        if pol == "hyst" and cur in cand and sc[best] <= max(sc[cur], 0) * 1.10:
            best = cur
        cur = best
        v = t[best].get(d)
        out[d] = (v[0], v[1], best) if v else (0.0, 0, best)
    return out


print("정책별 6일 합(만원) · 9/21 은 훈련 없음 → 거래 없음.  괄호 = 거래 수")
hdr = "%-9s " % "" + " ".join("%10s" % d[5:] for d in FD) + "        합"
res = {}
for fam, filt in FAMS:
    t = table(fam, filt)
    if not t:
        continue
    name = fam + ("(" + filt + ")" if filt else "")
    print("\n== 계열 %s  조합 %d" % (name, len(t)))
    print(hdr)
    for pol in ("daily", "hyst", "rank"):
        o = wf(t, pol)
        res[(name, pol)] = o
        tot = sum(v[0] for v in o.values() if v)
        print("%-9s " % pol + " ".join(("%+7.1f(%d)" % (v[0] / M, v[1])) if v else "      미측정" for v in (o[d] for d in FD)) + " %+9.1f" % (tot / M))
    # 마지막 날 선택된 파라미터
    print("   9/30 에 들고 있던 조합(daily):", res[(name, "daily")][FD[-1]][2])
    print("   9/30 에 들고 있던 조합(rank): ", res[(name, "rank")][FD[-1]][2])

print("\n== 현행 MAIN")
print("%-9s " % "MAIN" + " ".join("%10.1f" % (MAIN[d] / M) for d in FD) + " %+9.1f" % (sum(MAIN.values()) / M))

# 메타: 계열까지 전진 선택 — 그날 이전 흐름일의 전진 성과 합이 가장 큰 계열
print("\n== 메타(계열도 전진 선택)")
for pol in ("daily", "rank"):
    seq = []
    for i, d in enumerate(FD):
        if i < 2:
            seq.append(None); continue
        best = max([k for k in res if k[1] == pol],
                   key=lambda k: sum(res[k][x][0] for x in FD[1:i] if res[k][x]))
        v = res[best][d]
        seq.append((v[0] if v else 0.0, best[0]))
    print("%-9s " % pol + " ".join(("%+7.1f %-6s" % (v[0] / M, v[1])) if v else "     미측정   " for v in seq) + " %+9.1f" % (sum(v[0] for v in seq if v) / M))

# 참고: 9/30 문서의 고정 후보(표본 안 — 사후 선택)
print("\n== 참고(표본 안 · 사후 선택): 고정 규칙 6일")
fixed = {"BRK(D r1 9/30최적)": ("D", {"b": 2, "filt": "r1", "max_trades": 5, "tp": 8, "trail": [4, 3]}),
         "FLOWC(C 6일최적)": ("C", {"K": 300, "flip_exit": False, "max_trades": 3, "stop": None, "tp": 12, "trail": [6, 4]})}
for name, (fam, p) in fixed.items():
    k = json.dumps(p, sort_keys=True)
    t = table(fam, None)
    v = [t[k].get(d) for d in FD]
    print("%-22s " % name + " ".join(("%+7.1f(%d)" % (x[0] / M, x[1])) if x else "        -" for x in v) + " %+9.1f" % (sum(x[0] for x in v if x) / M))

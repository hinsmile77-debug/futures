# ②SHADOW_F2X 수량 규칙 격자 — f2_final.json 거래(l1·l2·stop) 재가중. 손익 = l1 + (q-1)*l2
import json, sys, statistics as st
src, out = sys.argv[1], sys.argv[2]
o = json.load(open(src, encoding="utf-8")); D = o["days"]; T = o["trades"]["②SHADOW_F2X"]
CAP, PV = 3e7, 5e4
def q_risk(X, buf, floor=0.0, cap=3):
    return lambda t: min(cap, max(1, int(CAP * X // ((max(t["stop"], floor) + buf) * PV))))
RULES = {
    "고정2": lambda t: 2,
    "711차 1.5%(버퍼1)": q_risk(.015, 1.0),
    "권고 X2.0·버퍼0.5·하한4": q_risk(.02, 0.5, 4.0),
    "손익최대 X2.0·버퍼0.5·하한3.5": q_risk(.02, 0.5, 3.5),
}
res = {"days": D, "rules": {}}
for nm, qf in RULES.items():
    day = [round(sum(t["l1"] + (qf(t) - 1) * t["l2"] for t in T[d]) / 1e4, 1) for d in D]
    res["rules"][nm] = {"daily": day, "qmix": [sum(1 for d in D for t in T[d] if qf(t) == k) for k in (1, 2, 3)]}
json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("날짜 | " + " | ".join(RULES))
for i, d in enumerate(D):
    print(d[5:], " | ".join("%+.1f" % res["rules"][n]["daily"][i] for n in RULES))
for n in RULES: print(n, res["rules"][n]["qmix"], "이긴날", sum(x > 0 for x in res["rules"][n]["daily"]))

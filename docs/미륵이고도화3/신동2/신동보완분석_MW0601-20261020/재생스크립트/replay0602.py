# [보관용] 2026-10-20 세션 재생 스크립트 — 인자: <origin/dev 워크트리 경로> <날짜(콤마)> <출력 json>.
# 정식 도구는 scripts/shindong_complement_mw0602.py (워크트리 자동 생성·삭제).
import sys, json, os
WT = sys.argv[1]; DB = r"C:\Users\82108\PycharmProjects\futures\data\db"
sys.path.insert(0, WT)
from strategy.shindong import runner, spec
dates = sys.argv[2].split(",")
out = {}
for d in dates:
    r = runner.compute(d, os.path.join(DB,"raw_data.db"), os.path.join(DB,"option_flow.db"), os.path.join(DB,"premarket_levels.db"), live=False)
    row = {}
    for v, res in r["results"].items():
        tr = [dict(t, net_krw=sum(g.get("net",0.0) for g in t["legs"] if not g.get("open",True))) for t in res.get("trades", [])]
        row[v] = {"n": len(tr), "w": sum(1 for t in tr if (t.get("net_krw") or 0) > 0),
                  "net": sum(float(t.get("net_krw") or 0) for t in tr),
                  "worst": min([float(t.get("net_krw") or 0) for t in tr], default=0.0),
                  "notes": res.get("decision", {}).get("notes")}
    out[d] = {"product": r["product"], "v": row, "bias": r["results"]["MAIN"].get("decision",{}).get("bias")}
    print(d, r["product"], {v: round(x["net"]/1e4,1) for v,x in row.items()}, flush=True)
print("VARIANTS", spec.VARIANTS, spec.SPEC_VERSION)
json.dump(out, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)

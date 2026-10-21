"""regime_history vs ensemble_decisions.micro_regime 커버리지 대조 — 장외 전용, 읽기전용."""
import csv
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import _paths  # 저장소 경로·PC별 출력 폴더 (README.md)
from utils.analysis_db import guard_intraday, connect_ro
guard_intraday("regime_coverage")
OUT = _paths.out("regime_coverage.csv")

p = connect_ro(_paths.db("predictions.db"))
ed = p.execute("""select substr(ts,1,10) d, count(*),
                  sum(case when micro_regime is not null and micro_regime<>'' then 1 else 0 end),
                  sum(case when micro_regime_source is not null then 1 else 0 end),
                  sum(case when micro_regime_legacy is not null then 1 else 0 end)
                  from ensemble_decisions group by d order by d""").fetchall()
r = connect_ro(_paths.db("raw_data.db"))
rh = dict(r.execute("select substr(ts,1,10) d, count(*) from regime_history group by d").fetchall())
# 겹치는 날: 분 단위 라벨 일치율
agree = {}
for d in sorted(rh):
    a = dict(r.execute("select ts, regime from regime_history where ts like ?", (d + "%",)).fetchall())
    b = dict(p.execute("select ts, micro_regime from ensemble_decisions where ts like ?", (d + "%",)).fetchall())
    common = [k for k in a if k in b]
    agree[d] = (len(common), sum(1 for k in common if a[k] == b[k]))
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["date", "ed_rows", "ed_micro", "ed_source", "ed_legacy", "rh_rows", "common", "same"])
    for d, n, m, s, l in ed:
        c = agree.get(d, (0, 0)); w.writerow([d, n, m, s, l, rh.get(d, 0), c[0], c[1]])
with_mr = [x for x in ed if x[2]]
print("ensemble_decisions days", len(ed), ed[0][0], "->", ed[-1][0])
print("micro_regime days", len(with_mr), with_mr[0][0] if with_mr else None, "->", with_mr[-1][0] if with_mr else None,
      "rows", sum(x[2] for x in ed))
print("micro_regime_source days", sum(1 for x in ed if x[3]))
print("regime_history days", len(rh), "overlap agree", sum(v[1] for v in agree.values()), "/", sum(v[0] for v in agree.values()))
print("disagree days", [(d, v) for d, v in agree.items() if v[0] != v[1]][:10])

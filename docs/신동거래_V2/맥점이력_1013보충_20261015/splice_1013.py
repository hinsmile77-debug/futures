# -*- coding: utf-8 -*-
"""이력 캐시에 2026-10-13 세션 하나만 접합한다(전량 재생성 금지 — raw_candles 보존 범위 밖 세션 소실).
refresh_history_cache() 의 증분 경로와 같은 함수(summarize_session · fill_derived)를 쓴다."""
import os, sys, json, io, datetime
ROOT = sys.argv[1]
sys.path.insert(0, ROOT); os.chdir(ROOT)
from utils.dll_bootstrap import ensure_conda_dll_path
ensure_conda_dll_path()
from features.levels import levels_store as LS
from features.levels import premarket_levels as PL

DAY = "2026-10-13"
APPLY = "--apply" in sys.argv
cache = LS.load_history_cache()
old_dump = dict((s["d"], json.dumps(s, sort_keys=True)) for s in cache["summaries"])
summaries = [PL.summary_from_dict(s) for s in cache["summaries"]]
bars_by_day = dict((d, [PL.bar_from_dict(b) for b in bs]) for d, bs in (cache.get("bars") or {}).items())
assert DAY not in [s.d for s in summaries], "이미 있다"
prev = [s for s in summaries if s.d < DAY][-1]
sessions, excluded = LS.load_sessions(since=DAY, until="2026-10-14", prev_close=prev.c)
print("load_sessions:", [(d, len(b)) for d, b in sessions], "excluded:", excluded)
assert len(sessions) == 1 and sessions[0][0] == DAY and not excluded
d, bars = sessions[0]
summaries.append(PL.summarize_session(d, bars))
bars_by_day[d] = bars
summaries.sort(key=lambda x: x.d)
PL.fill_derived(summaries)
keep = set(x.d for x in summaries[-(PL.LOOKBACK + 1):])
bars_by_day = dict((k, v) for k, v in bars_by_day.items() if k in keep)
exc = dict(cache.get("excluded", {}))
exc.pop(DAY, None)
payload = dict(
    updated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    path_grid=cache.get("path_grid"),
    last_date=summaries[-1].d,
    summaries=[PL.summary_to_dict(s) for s in summaries],
    bars=dict((k, [PL.bar_to_dict(b) for b in bs]) for k, bs in bars_by_day.items()),
    excluded=exc,
)
new_dump = dict((s["d"], json.dumps(s, sort_keys=True)) for s in payload["summaries"])
changed = [k for k in old_dump if new_dump.get(k) != old_dump[k]]
print("summaries %d -> %d | added %s | changed %s" % (len(old_dump), len(new_dump),
      sorted(set(new_dump) - set(old_dump)), changed))
s13 = [s for s in payload["summaries"] if s["d"] == DAY][0]
s14 = [s for s in payload["summaries"] if s["d"] == "2026-10-14"][0]
o14 = json.loads(old_dump["2026-10-14"])
print("10-13:", {k: s13.get(k) for k in ("o", "h", "l", "c", "atr")})
print("10-14 atr: %s -> %s" % (o14.get("atr"), s14.get("atr")))
print("bars days:", sorted(payload["bars"]), "| excluded:", sorted(payload["excluded"]))
if APPLY:
    LS.save_history_cache(payload)
    print("SAVED", LS.HISTORY_CACHE_PATH)
    s2, b2 = LS.history_from_cache()
    p = LS.prepare_params(s2, b2, "2026-10-15")
    print("10/15 prev:", p["prev"].d, "h/l/c", p["prev"].h, p["prev"].l, p["prev"].c, "| atr", p["atr"], "| warnings", p["warnings"],
          "| history_sessions", p.get("history_sessions"))
    c = p["candidates"]
    print("10/15 candidates 900~1000:", [(k, c[k]) for k in sorted(c) if 900 <= k <= 1000])

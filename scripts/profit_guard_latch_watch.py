# scripts/profit_guard_latch_watch.py
"""[MW0601 477차 후속6 / GR-1] ProfitGuard L1 래치 기회비용 — 읽기 전용 소급.

무엇을 묻는가
--------------
L1-Trail이 발동하면 `_TrailingGuard.update()`의 첫 줄
(`if self.is_halted: return True`)이 **당일 내내 진입을 막는다** — 손익이 보호선
위로 돌아와도 재평가하지 않고, `reset()`은 일일 마감에만 불린다. 2026-08-18에는
13:19:59 래치 이후 15:09까지 110분이 그 상태였다.

"세션의 30%가 무거래였다"는 서술은 쉽게 나오지만, **래치가 실제로 막은 기회**는
그보다 훨씬 작다. 다른 게이트(등급 X · 14:50 이후 금지 · 청산 쿨다운 · Degraded)가
이미 막고 있던 분은 래치를 풀어도 진입이 없기 때문이다. 이 스크립트는 그 차이를
**깔때기**로 분리하고, 남은 분(binding)에만 반사실을 계산한다.

왜 라이브 코드를 안 건드리는가
------------------------------
필요한 입력이 전부 이미 있다 — SIGNAL/TRADE 로그 + `ensemble_decisions`
(grade·confidence·min_conf·direction·entry_block_reason·entry_mode·features.atr) +
`raw_candles`. [25]·G-1(`position_mfe_shadow`)과 같은 설계이며 **과거 발동일에
소급 적용**된다(2026-06-19 이래 4회를 즉시 계산).

⚠ 왜 로그가 1차 원천인가
------------------------
`ensemble_decisions.entry_block_reason`은 STEP7 elif 체인의 **1등 사유 하나**만
남긴다. 2026-08-18 실측에서 ProfitGuard가 로그상 105분 차단인데 DB에는 20분만
ProfitGuard로 기록됐다 — 나머지는 다른 사유가 선행했다. 471차 F-4의
`entry_block_axes`가 이 문제의 답이지만 **2026-08-14 이후 행에만 있어**
6월 발동일 3회는 축 복원이 불가능하다. 그래서 차단 사실 자체는 로그에서 읽고,
DB는 "그 분에 진입 자격이 살아 있었는가"를 판정하는 데 쓴다.

무엇을 결론으로 삼을 수 있나 / 없나
-----------------------------------
- 🔴 **이 스크립트는 verdict를 내지 않는다.** 판정문 재등록(대상을 A/B → 자동진입
  자격으로, min_days를 거래일 → **L1 발동일**로)은 2026-08-29 주간회의 승인
  사항이다(GR-2). 그 전까지는 관측치만 출력한다 — §9 사전등록 원칙.
- ⚠ **binding 분은 독립 표본이 아니다.** 연속된 분은 사실상 같은 자리이고 실제로는
  그중 한 번만 진입한다. `overlap_clusters`(기본 30분)를 반드시 함께 읽을 것
  (313차 ②).
- ⚠ 반사실은 "그 분에 진입했다면"이지 "그만큼 벌었다"가 아니다.

실행:
    python scripts/profit_guard_latch_watch.py [--since 2026-06-01] [--json] [--write]
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import re
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config.settings import (  # noqa: E402
    TRADES_DB, RAW_DATA_DB, PREDICTIONS_DB, VALIDATION_CAMPAIGN,
    FUTURES_COMMISSION_RATE, TICK_SIZE,
)

LOG_DIR = os.path.join(ROOT, "logs")
# 진입 모드별 자동진입 허용 등급 — main.py:8396 `allowed_grades`와 같은 표.
# ⚠ 하드코딩 사본이다. main.py가 바뀌면 여기도 바꿔야 한다(리터럴 사본 경고).
ALLOWED_GRADES = {"auto": ("A",), "hybrid": ("A", "B"), "manual": ("A", "B", "C")}
OVERLAP_WINDOW_MIN = 30     # 같은 자리로 볼 시간 폭 — 313차 ② overlap 보정
DEFAULT_QTY = 2             # 반사실 진입 수량. 431차 이후 실측 최빈값

_RE_LATCH = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?\[ProfitGuard-L1\] 트레일링 발동.*?"
    r"피크 ([+-][\d,]+)원 대비 (\d+)% 하락.*?현재 ([+-][\d,]+)원 < 보호선 ([+-][\d,]+)원")
_RE_BLOCK = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.*?\[ProfitGuard\] 진입 차단[:\s]*\[(L\d[^\]]*)\]")
# [477차 후속7 / GR-3] 차단 줄 끝의 손익 원천 토큰 — `| src=broker(gross)` 형태.
# 2026-08-18 이전 로그에는 없다(→ "미측정"으로 남기고 0/임의값으로 채우지 않는다).
_RE_SRC = re.compile(r"\| src=(\S+)")


def _conn(p):
    c = sqlite3.connect("file:%s?mode=ro" % p.replace("\\", "/"), uri=True, timeout=15)
    c.row_factory = sqlite3.Row
    return c


def _cost_pts(px: float) -> float:
    slip = float(VALIDATION_CAMPAIGN.get("slippage_ticks_per_side", 1.0))
    return 2.0 * px * FUTURES_COMMISSION_RATE + 2.0 * slip * TICK_SIZE


def _read_log(path):
    for enc in ("utf-8", "cp949"):
        try:
            with open(path, "r", encoding=enc, errors="replace") as f:
                return f.readlines()
        except IOError:
            return []
    return []


def scan_logs(since: str):
    """로그에서 (래치 이벤트, 일자별 차단 분) 추출.

    Returns: ({date: {ts, peak, ratio_pct, current, floor}},
              {date: {minute_str: set(layer)}},
              {date: {src_label: count}})   # GR-3 토큰 — 없는 날은 빈 dict(미측정)
    """
    latches, blocks, srcs = {}, {}, {}
    for path in sorted(glob.glob(os.path.join(LOG_DIR, "*_TRADE.log"))
                       + glob.glob(os.path.join(LOG_DIR, "*_SIGNAL.log"))):
        base = os.path.basename(path)
        day = base[:8]
        if len(day) != 8 or not day.isdigit():
            continue
        d = "%s-%s-%s" % (day[:4], day[4:6], day[6:8])
        if d < since:
            continue
        for line in _read_log(path):
            m = _RE_LATCH.match(line)
            if m and d not in latches:
                latches[d] = {
                    "ts": m.group(1),
                    "peak_krw": float(m.group(2).replace(",", "")),
                    "ratio_pct": int(m.group(3)),
                    "current_krw": float(m.group(4).replace(",", "")),
                    "floor_krw": float(m.group(5).replace(",", "")),
                }
                continue
            b = _RE_BLOCK.match(line)
            if b:
                blocks.setdefault(d, {}).setdefault(b.group(1), set()).add(b.group(2))
                sm = _RE_SRC.search(line)
                if sm:
                    srcs.setdefault(d, {})[sm.group(1)] = (
                        srcs.setdefault(d, {}).get(sm.group(1), 0) + 1)
    return latches, blocks, srcs


def _load_day_rows(day: str):
    with _conn(PREDICTIONS_DB) as c:
        return {r["ts"][:16]: dict(r) for r in c.execute(
            """SELECT ts, direction, grade, confidence, min_conf, entry_mode,
                      entry_block_reason, entry_block_axes, entry_executed, features
                 FROM ensemble_decisions WHERE date(ts) = ? ORDER BY ts""", (day,))}


def _load_bars(day: str):
    with _conn(RAW_DATA_DB) as c:
        return {r["ts"]: (float(r["high"]), float(r["low"]), float(r["close"]))
                for r in c.execute(
                    "SELECT ts, high, low, close FROM raw_candles WHERE date(ts) = ?",
                    (day,))}


def _atr_of(row, fallback):
    try:
        f = json.loads(row.get("features") or "{}")
        v = f.get("atr")
        return float(v) if v else fallback
    except (ValueError, TypeError):
        return fallback


def _cluster_rows(rows):
    """연속·근접(OVERLAP_WINDOW_MIN 이내) binding 분을 **한 자리**로 묶는다.

    실제로는 한 클러스터에서 한 번만 진입한다 — 분 단위 합계는 같은 기회를 여러 번
    세므로 클러스터 단위가 정직한 읽기 단위다(313차 ②).
    """
    if not rows:
        return []
    def _key(ts):
        return int(ts[11:13]) * 60 + int(ts[14:16])
    rs = sorted(rows, key=lambda r: r["ts"])
    out, cur = [], [rs[0]]
    for r in rs[1:]:
        if _key(r["ts"]) - _key(cur[0]["ts"]) > OVERLAP_WINDOW_MIN:
            out.append(cur)
            cur = [r]
        else:
            cur.append(r)
    out.append(cur)
    return [{
        "start": c[0]["ts"][11:16],
        "end": c[-1]["ts"][11:16],
        "n_minutes": len(c),
        "net_pts_sum": round(sum(x["net_pts"] for x in c), 4),
        "net_pts_first": c[0]["net_pts"],   # 그 자리에서 첫 분에 진입했다면
    } for c in out]


def analyze_day(day: str, latch: dict, block_minutes: dict,
                src_counts: dict = None) -> dict:
    """하루치 깔때기 + binding 반사실."""
    from scripts.exit_replay import replay, regime_for

    rows = _load_day_rows(day)
    bars = _load_bars(day)
    rg = regime_for(day)

    latch_hm = latch["ts"][11:16]
    after = {m: lays for m, lays in block_minutes.items() if m[11:16] > latch_hm}

    # 대표 ATR — 분별 features.atr이 없을 때만 쓰는 폴백(당일 중앙값)
    atrs = sorted(_atr_of(r, 0.0) for r in rows.values() if _atr_of(r, 0.0) > 0)
    atr_fallback = atrs[len(atrs) // 2] if atrs else 3.0

    n_db = n_qual = 0
    binding, grade_dist = [], {}
    for m in sorted(after):
        r = rows.get(m)
        if r is None:
            continue
        n_db += 1
        mode = str(r.get("entry_mode") or "manual").strip().lower()
        allowed = ALLOWED_GRADES.get(mode, ALLOWED_GRADES["manual"])
        conf, mc = r.get("confidence") or 0.0, r.get("min_conf")
        if r.get("grade") not in allowed or mc is None or conf < mc:
            continue
        n_qual += 1
        grade_dist[r["grade"]] = grade_dist.get(r["grade"], 0) + 1
        # binding = 이 분의 1등 차단사유가 ProfitGuard (다른 축이 선행하지 않음)
        if "ProfitGuard" not in (r.get("entry_block_reason") or ""):
            continue
        d = {1: "LONG", -1: "SHORT"}.get(int(r.get("direction") or 0))
        if d is None:
            continue
        px = (bars.get(m + ":00") or (None, None, None))[2]
        if px is None:
            continue
        out = replay(bars, r["ts"], d, px, DEFAULT_QTY, _atr_of(r, atr_fallback),
                     tp_trigger=rg["tp_trigger"], protect_mode=rg["protect_mode"])
        if not out:
            continue
        net = out["pts_per_contract"] - _cost_pts(px)
        binding.append({
            "ts": r["ts"], "direction": d, "grade": r["grade"],
            "conf": round(float(conf), 4), "min_conf": round(float(mc), 4),
            "atr": round(_atr_of(r, atr_fallback), 4),
            "pts_per_contract": round(out["pts_per_contract"], 4),
            "net_pts": round(net, 4), "outcome": out["outcome"],
        })

    tot = sum(b["net_pts"] for b in binding)
    wins = sum(1 for b in binding if b["net_pts"] > 0)
    return {
        "date": day,
        "latch": latch,
        "regime": rg,
        "funnel": {
            "log_block_minutes": len(block_minutes),
            "after_latch_minutes": len(after),
            "db_rows": n_db,
            "entry_qualified": n_qual,
            "binding": len(binding),
        },
        "grade_dist_qualified": grade_dist,
        # [477차 후속7 / GR-3] 그날 차단 줄이 어느 손익 원천으로 판정됐는가.
        # 빈 dict = 토큰 이전 로그(**미측정** — "engine이었다"가 아니다).
        "pnl_source_counts": dict(src_counts or {}),
        "overlap_clusters": len(_cluster_rows(binding)),
        "clusters": _cluster_rows(binding),
        "cf_total_net_pts_per_ct": round(tot, 4),
        "cf_wins": wins,
        "cf_losses": len(binding) - wins,
        "binding_rows": binding,
    }


def compute(since: str = "2026-06-01") -> dict:
    latches, blocks, srcs = scan_logs(since)
    days = []
    for d in sorted(latches):
        # 로그 콜은 SIGNAL, 래치는 TRADE — 둘 중 하나만 있는 날은 계측 불완전
        if d not in blocks:
            days.append({"date": d, "error": "차단 로그 없음(SIGNAL 로그 부재)"})
            continue
        try:
            days.append(analyze_day(d, latches[d], blocks[d], srcs.get(d)))
        except Exception as e:  # noqa: BLE001 — 하루 실패가 전체를 막지 않는다
            days.append({"date": d, "error": "%s: %s" % (type(e).__name__, e)})
    ok = [d for d in days if "error" not in d]
    return {
        "since": since,
        "n_latch_days": len(latches),
        "n_analyzed": len(ok),
        "total_binding_minutes": sum(d["funnel"]["binding"] for d in ok),
        "total_binding_clusters": sum(d["overlap_clusters"] for d in ok),
        "total_cf_net_pts_per_ct": round(
            sum(d["cf_total_net_pts_per_ct"] for d in ok), 4),
        # 클러스터당 1회 진입 가정 — 분 단위 합계보다 이쪽이 정직한 단위다(313차 ②)
        "total_cf_net_pts_per_ct_by_cluster": round(
            sum(c["net_pts_first"] for d in ok for c in d.get("clusters", [])), 4),
        "days": days,
        # 🔴 판정문 미승인 — GR-2(2026-08-29 주간회의)까지 관측 전용
        "verdict": "NOT_JUDGED",
        "verdict_note": (
            "판정문 재등록 미승인 — 대상(A/B → 자동진입 자격)·min_days(거래일 → "
            "L1 발동일) 변경은 2026-08-29 주간회의 승인 사항이다(GR-2, §9 사전등록). "
            "이 출력은 관측치이며 어떤 임계와도 비교하지 않는다."),
    }


def _first_gap(res):
    """민감도 예시용 — 첫 클러스터의 (첫 분 진입, 분 단위 합)."""
    for d in res.get("days", []):
        for c in d.get("clusters", []) or []:
            return c["net_pts_first"], c["net_pts_sum"]
    return 0.0, 0.0


def render_md(res: dict) -> str:
    L = ["# ProfitGuard L1 래치 기회비용 관측 (GR-1, 읽기 전용 소급)", ""]
    L.append("- 대상 구간: `%s` 이후 · L1 발동일 **%d일** (분석 성공 %d일)"
             % (res["since"], res["n_latch_days"], res["n_analyzed"]))
    L.append("- **binding 분 합계 %d분** (overlap 보정 클러스터 **%d개**)"
             % (res["total_binding_minutes"], res["total_binding_clusters"]))
    L.append("- 반사실 **분 단위** 합계 %+.2f pt/계약 (비용 차감 후, %d계약 가정)"
             % (res["total_cf_net_pts_per_ct"], DEFAULT_QTY))
    L.append("- 반사실 **클러스터 단위**(자리당 1회 진입) 합계 **%+.2f pt/계약** ← 정직한 단위"
             % res["total_cf_net_pts_per_ct_by_cluster"])
    L.append("- ⚠ 두 값의 격차가 방법 민감도다 — 자리 안에서 **어느 분에 진입하느냐**로")
    L.append("  결과가 뒤집힌다(2026-08-18 첫 자리: 첫 분 %+.2f vs 8분 합 %+.2f). 표본이"
             % (_first_gap(res)[0], _first_gap(res)[1]))
    L.append("  1거래일뿐이라 **어느 쪽도 손익 추정으로 쓸 수 없다**.")
    L.append("- 판정: **%s** — %s" % (res["verdict"], res["verdict_note"]))
    L.append("")
    L.append("## 깔때기 (계측 4원칙 ③ 탈락 가시화)")
    L.append("")
    L.append("| 발동일 | 래치 | 로그 차단분 | 래치 이후 | 진입자격 | **binding** | 클러스터 | 반사실 pt/ct |")
    L.append("|---|---|---|---|---|---|---|---|")
    for d in res["days"]:
        if "error" in d:
            L.append("| %s | — | — | — | — | — | — | ⚠ %s |" % (d["date"], d["error"]))
            continue
        f = d["funnel"]
        L.append("| %s | %s | %d | %d | %d | **%d** | %d | %+.2f |" % (
            d["date"], d["latch"]["ts"][11:16], f["log_block_minutes"],
            f["after_latch_minutes"], f["entry_qualified"], f["binding"],
            d["overlap_clusters"], d["cf_total_net_pts_per_ct"]))
    L.append("")
    L.append("> **binding** = 그 분에 ProfitGuard가 차단했고 · 진입 자격(등급 ∈ entry_mode")
    L.append("> 허용 & conf ≥ min_conf)이 살아 있었고 · `entry_block_reason`이 ProfitGuard인 분.")
    L.append("> 나머지는 다른 게이트가 이미 막고 있어 **래치를 풀어도 진입이 없다**.")
    L.append("> ⚠ binding 분은 독립 표본이 아니다 — 연속된 분은 같은 자리이고 실제로는 그중")
    L.append("> 한 번만 진입한다. **클러스터 수를 함께 읽을 것**(313차 ②).")
    L.append("")
    for d in res["days"]:
        if "error" in d or not d["binding_rows"]:
            continue
        lt = d["latch"]
        L.append("## {} — 래치 {} (피크 {:+,.0f}원 → 현재 {:+,.0f}원, 보호선 {:+,.0f}원)".format(
            d["date"], lt["ts"][11:19], lt["peak_krw"], lt["current_krw"], lt["floor_krw"]))
        L.append("")
        _sc = d.get("pnl_source_counts") or {}
        L.append("- 손익 원천(GR-3 토큰): %s" % (
            ", ".join("%s×%d" % kv for kv in sorted(_sc.items())) if _sc
            else "**미측정** — 토큰 도입(2026-08-18) 이전 로그"))
        L.append("- 재생 체제: `%s` / `%s` · 자격 분 등급 분포: %s" % (
            d["regime"]["tp_trigger"], d["regime"]["protect_mode"],
            ", ".join("%s=%d" % kv for kv in sorted(d["grade_dist_qualified"].items())) or "—"))
        L.append("- 반사실 **%+.2f pt/계약** (승 %d / 패 %d)" % (
            d["cf_total_net_pts_per_ct"], d["cf_wins"], d["cf_losses"]))
        L.append("")
        if d.get("clusters"):
            L.append("**자리(클러스터) 단위** — 실제로는 각 자리에서 한 번만 진입한다")
            L.append("")
            L.append("| 자리 | 분 수 | 첫 분 진입 시 | (참고) 분 단위 합 |")
            L.append("|---|---|---|---|")
            for c in d["clusters"]:
                L.append("| %s~%s | %d | **%+.2f** | %+.2f |" % (
                    c["start"], c["end"], c["n_minutes"],
                    c["net_pts_first"], c["net_pts_sum"]))
            L.append("")
        L.append("| 시각 | 방향 | 등급 | conf/min | ATR | 결말 | net pt/ct |")
        L.append("|---|---|---|---|---|---|---|")
        for b in d["binding_rows"]:
            L.append("| %s | %s | %s | %.3f/%.3f | %.2f | %s | %+.2f |" % (
                b["ts"][11:16], b["direction"], b["grade"], b["conf"], b["min_conf"],
                b["atr"], b["outcome"], b["net_pts"]))
        L.append("")
    L.append("---")
    L.append("")
    L.append("생성: `scripts/profit_guard_latch_watch.py` — 읽기 전용, 집행·라이브 코드 무변경.")
    L.append("차단 사실은 **로그가 1차 원천**이다(`entry_block_reason`은 1등 사유 1건만 남기고,")
    L.append("`entry_block_axes`는 2026-08-14 이후 행에만 있어 그 이전 발동일은 축 복원 불가).")
    return "\n".join(L)


def _out_dir():
    from utils.db_utils import pc_id
    d = os.path.join(ROOT, "docs", "정기점검", "금요일점검", pc_id())
    if not os.path.isdir(d):
        os.makedirs(d)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-06-01")
    ap.add_argument("--json", action="store_true", help="JSON을 stdout으로")
    ap.add_argument("--write", action="store_true",
                    help="금요일점검 PC 폴더에 md/json 날짜본 저장")
    a = ap.parse_args()

    # 장중 DB 분석 금지 (CLAUDE.md 456차) — 로그·DB 전수 스캔이라 해당된다
    try:
        from utils.analysis_db import guard_intraday
        guard_intraday("profit_guard_latch_watch")
    except ImportError:
        pass

    res = compute(a.since)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print(render_md(res))
    if a.write:
        stamp = datetime.date.today().strftime("%Y%m%d")
        d = _out_dir()
        with open(os.path.join(d, "profit_guard_latch_%s.md" % stamp),
                  "w", encoding="utf-8") as f:
            f.write(render_md(res))
        with open(os.path.join(d, "profit_guard_latch_%s.json" % stamp),
                  "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        print("\n저장: %s/profit_guard_latch_%s.{md,json}" % (d, stamp))


if __name__ == "__main__":
    main()

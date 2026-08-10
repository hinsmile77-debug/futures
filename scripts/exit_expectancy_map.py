# -*- coding: utf-8 -*-
"""[MW0602 458차 / 3-C] 청산 기하 기대값 지도 — 축별 A/B의 상호작용 사각 보완.

무엇인가
--------
[23-B]/[25]/[25-B]는 기하 축을 **하나씩** 바꾼다. 그러나 스톱 폭·TP1 거리·TP2
거리는 상호작용한다(스톱이 넓으면 TP1 의미가 변한다). 정본 재생기
(`scripts/exit_replay.py`, 440차 — 라이브 트레일링 함수를 import)로
(stop_mult × tp1_mult × tp2_mult) 그리드 전 셀을 같은 포지션 집합에 재생해
**기대값 표면**을 그린다. 현행 파라미터가 능선인지 골짜기인지 보는 지도다.

판정 채널이 아니다
------------------
어떤 셀도 이 지도만으로 안건이 되지 않는다(0808 D2: 표본이 쌓여도 수렴하지
않을 수 있고 PC간 부호 역전 전례가 있다). **MW0601 대조 + 별도 사전등록** 없이는
적용 논의 금지. 월간 수동 실행, 날짜본 md 산출(덮어쓰기 없음 — 407차 규약).

축의 한계 (정직 고지)
---------------------
· 트레일 발동 지연·TP1 비율(33%)은 재생기가 파라미터화하지 않아 **이 지도에 없다**.
  그 축이 필요해지면 exit_replay 확장이 선행돼야 한다(별건).
· 창은 기본 2026-08-03~ — 코드 세대 경계(440차: TickTP1/atr_profit 전환)를 넘어
  섞으면 과거를 다른 시스템의 규칙으로 재생하게 된다. 세대 고정: envelope+atr_profit.
· 절대 pt를 실현손익으로 인용하지 말 것 — 재생기의 상대비교만 유효([23-B] 관례).

사용
----
    python scripts/exit_expectancy_map.py                    # 08-03~ 기본 창
    python scripts/exit_expectancy_map.py --since 2026-08-03 --stdout

읽기 전용(DB) + md 날짜본 1개 생성. py310_64 권장.
"""
import argparse
import collections
import datetime
import glob
import io
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("MIREUK_TEST_MODE", "1")

from config.settings import TRADES_DB, RAW_DATA_DB, PREDICTIONS_DB  # noqa: E402
from scripts.exit_replay import replay  # noqa: E402  — 정본 재생기 (440차)
from utils.db_utils import pc_id  # noqa: E402

_TS = "%Y-%m-%d %H:%M:%S"
_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
_OUT_DIR_TPL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "정기점검", "금요일점검", "%s")

# 그리드 — 현행(스톱 1.5 / TP1 hz별 / TP2 1.5)을 반드시 포함한다.
STOP_GRID = (1.2, 1.5, 1.8)
TP1_GRID = (None, 0.3, 0.5, 0.7)      # None = 호라이즌별 라이브 현행
TP2_GRID = (1.2, 1.5, 2.0)

_ENTRY_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*\[Position\] 진입 (LONG|SHORT) (\d+)계약 @ ([\d.]+) \|"
    r".*horizon=(\S+) hurst=(\S+)", re.MULTILINE)


def _conn(path):
    c = sqlite3.connect("file:%s?mode=ro" % str(path).replace("\\", "/"), uri=True)
    c.row_factory = sqlite3.Row
    return c


def load_positions(since):
    """진입 로그에서 (ts, dir, qty, px, horizon, hurst)를 얻는다 — 재생 입력."""
    pos = []
    for f in sorted(glob.glob(os.path.join(_LOG_DIR, "2026*_TRADE.log"))):
        day = os.path.basename(f)[:8]
        if "%s-%s-%s" % (day[:4], day[4:6], day[6:8]) < since[:10]:
            continue
        try:
            text = io.open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for m in _ENTRY_RE.finditer(text.replace("\r", "")):
            ts, dirn, qty, px, hz, hurst = m.groups()
            pos.append({"entry_ts": ts[:17] + "00", "direction": dirn,
                        "qty": int(qty), "entry_px": float(px),
                        "horizon": hz, "hurst": hurst})
    return pos


def load_atr(since):
    import json as _json
    atr = {}
    with _conn(PREDICTIONS_DB) as c:
        for r in c.execute("SELECT ts, features FROM ensemble_decisions WHERE ts >= ?",
                           (since,)):
            try:
                a = float((_json.loads(r["features"]) or {}).get("atr") or 0.0)
            except (ValueError, TypeError):
                a = 0.0
            if a > 0:
                atr[str(r["ts"])[:16]] = a
    return atr


def load_bars(since):
    bars = {}
    with _conn(RAW_DATA_DB) as c:
        for r in c.execute("SELECT ts, high, low, close FROM raw_candles WHERE ts >= ?",
                           (since,)):
            bars[str(r["ts"])] = (float(r["high"]), float(r["low"]), float(r["close"]))
    return bars


def _atr_for(ets, atr):
    k = ets[:16]
    if k in atr:
        return atr[k]
    prev = (datetime.datetime.strptime(ets, _TS) - datetime.timedelta(minutes=1))
    return atr.get(prev.strftime(_TS)[:16])


def build_map(since):
    positions = load_positions(since)
    atr = load_atr(since)
    bars = load_bars(since)
    usable = []
    for p in positions:
        a = _atr_for(p["entry_ts"], atr)
        if a:
            usable.append((p, a))
    cells = {}
    for sm in STOP_GRID:
        for t1 in TP1_GRID:
            for t2 in TP2_GRID:
                tot, n = 0.0, 0
                for p, a in usable:
                    r = replay(bars, p["entry_ts"], p["direction"], p["entry_px"],
                               p["qty"], a, horizon=p["horizon"],
                               hurst_bucket=p["hurst"],
                               stop_mult=sm, tp1_mult=t1, tp2_mult=t2,
                               tp_trigger="envelope", protect_mode="atr_profit")
                    if r is None:
                        continue
                    tot += r["pts_per_contract"]
                    n += 1
                cells[(sm, t1, t2)] = (tot, n)
    return cells, len(usable), len({p["entry_ts"][:10] for p, _ in usable})


def render(cells, n_pos, n_days, since):
    today = datetime.date.today().strftime("%Y-%m-%d")
    L = []
    L.append("# 청산 기하 기대값 지도 — %s · %s" % (pc_id(), today))
    L.append("")
    L.append("> 생성: `scripts/exit_expectancy_map.py` (읽기 전용) · 창 %s~ · "
             "포지션 %d건/%d일" % (since[:10], n_pos, n_days))
    L.append("> 재생: 정본 `exit_replay.replay()` · 세대 고정 envelope+atr_profit")
    L.append(">")
    L.append("> ⚠ **지도이지 판정이 아니다.** 어떤 셀도 MW0601 대조 + 별도 사전등록")
    L.append("> 없이 안건이 되지 않는다(0808 D2). 절대 pt 인용 금지 — 상대비교만 유효.")
    L.append("> 트레일 지연·TP1 비율 축은 재생기 미지원으로 **이 지도에 없다.**")
    L.append("")
    cur_key = (1.5, None, 1.5)
    cur = cells.get(cur_key)
    if cur and cur[1]:
        L.append("**현행 셀** (stop 1.5 × tp1 hz현행 × tp2 1.5): 합계 %+.2fpt · "
                 "건당 %+.4fpt (n=%d)" % (cur[0], cur[0] / cur[1], cur[1]))
        L.append("")
    for sm in STOP_GRID:
        L.append("## stop_mult = %.1f" % sm)
        L.append("")
        hdr = "| tp1 \\ tp2 |" + "".join(" %.1f |" % t2 for t2 in TP2_GRID)
        L.append(hdr)
        L.append("|---|" + "---|" * len(TP2_GRID))
        for t1 in TP1_GRID:
            row = "| %s |" % ("hz현행" if t1 is None else "%.1f" % t1)
            for t2 in TP2_GRID:
                tot, n = cells.get((sm, t1, t2), (0.0, 0))
                mark = " **←현행**" if (sm, t1, t2) == cur_key else ""
                row += (" %+.2f (%+.3f/건)%s |" % (tot, tot / n, mark)) if n else " — |"
            L.append(row)
        L.append("")
    best = max((k for k in cells if cells[k][1]), key=lambda k: cells[k][0])
    L.append("최대 셀: stop %.1f × tp1 %s × tp2 %.1f = %+.2fpt — **인용 전 D2 재독**"
             % (best[0], "hz현행" if best[1] is None else best[1], best[2],
                cells[best][0]))
    L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    # 기본 2026-08-03 — 코드 세대 경계(440차). 이전으로 넓히면 체제가 섞인다.
    ap.add_argument("--since", default="2026-08-03")
    ap.add_argument("--stdout", action="store_true")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    since = a.since if len(a.since) > 10 else a.since + " 00:00:00"
    cells, n_pos, n_days, = build_map(since)
    md = render(cells, n_pos, n_days, since)
    if a.stdout:
        print(md)
    out_dir = _OUT_DIR_TPL % pc_id()
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "exit_expectancy_map_%s.md"
                       % datetime.date.today().strftime("%Y%m%d"))
    io.open(out, "w", encoding="utf-8").write(md)
    print("저장: %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

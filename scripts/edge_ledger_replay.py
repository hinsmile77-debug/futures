# -*- coding: utf-8 -*-
"""EdgeScore(등급 재설계) 소급 재생 검증 — Phase 0 사전검증 도구.

■■ 검증 결과: 이 척도는 **기각됐다**. 라이브에 배선하지 말 것. ■■
  2026-07-27(394차) 이 스크립트 자신의 출력으로 기각. 척도의 전제인 "셀의 과거 실적이
  미래 실적을 예측한다"가 반증됨 — 상위 25% 셀 과거 0.577 → 미래 0.512(거의 완전한
  평균회귀), 일자단위 상관은 그룹별 부호가 엇갈림. 파라미터 36조합(--sweep) + 재설계안
  2종으로도 구제 불가. B등급은 전 조합에서 C보다 낮은 역전(임계밴드가 평균회귀 정점을
  선별하기 때문), A등급은 11거래일 클러스터 아티팩트(일자단위 t=0.58).
  상세: docs/미륵이고도화2/Phase0_검증결과_2026-07-27.md §1
  이 파일은 그 판정의 재현 가능한 증거로 보존한다 — 등급을 롤링 실적으로 만들자는
  제안이 다시 나오면 먼저 이 스크립트를 돌려볼 것.


`docs/미륵이고도화2/등급AB_신뢰도고도화_제안_2026-07-27.md` §2-1의 EdgeLedger 척도를
과거 predictions.db에 소급 적용해, 라이브 배선 전에 다음 3가지 보장(G1~G3)이 실제로
성립하는지 확인한다.

  G1 도달가능성 — 엣지가 있는 구간에서 A/B가 실제로 점등되는가
  G2 정직성     — 무엣지/과신 구간(2026-05-19 이전)에서 A/B가 남발되지 않는가
  G3 단조성     — 부여된 등급별 실측 부호적중·EV가 A≥B≥C≥X 로 단조인가

**엄격한 walk-forward**: 시각 t의 신호를 등급판정할 때 원장에는 t 이전에 이미
"결과가 확정된"(ts + horizon <= t) 관측치만 들어있다. 미래참조 없음.

읽기 전용 — DB에 아무것도 쓰지 않는다.

실행:
  python scripts/edge_ledger_replay.py                 # 기본(운영 후보 파라미터)
  python scripts/edge_ledger_replay.py --sweep         # 파라미터 스윕
  python scripts/edge_ledger_replay.py --cell-detail   # 셀별 상세
"""
from __future__ import print_function

import argparse
import math
import os
import sqlite3
import sys
from collections import defaultdict, deque

DEFAULT_DB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "db", "predictions.db",
)

# ── 척도 파라미터 (제안서 §2-1 후보값) ──────────────────────────────
WINDOW_DEFAULT = 300

GRADE_CUTS_DEFAULT = {
    # grade: (wilson_lower_min, min_n, require_positive_ev)
    "A": (0.55, 150, True),
    "B": (0.52, 100, True),
}
C_PHAT_MIN_DEFAULT = 0.50
C_MIN_N_DEFAULT = 60

# 호라이즌 그룹 (CLAUDE.md 절대원칙 §3 HORIZON_CORE_GROUP과 동일 분류)
HZ_GROUP = {
    "1m": "SHORT", "3m": "SHORT", "5m": "SHORT",
    "10m": "MID", "15m": "MID",
    "30m": "LONG",
}
HZ_MINUTES = {"1m": 1, "3m": 3, "5m": 5, "10m": 10, "15m": 15, "30m": 30}

# 왕복 비용(pt): 수수료 2×price×FUTURES_COMMISSION_RATE + 슬리피지 2×틱
#   config/settings.py: FUTURES_COMMISSION_RATE=0.000015, slippage_ticks_per_side=1.0
#   KOSPI200 선물 틱=0.05pt, 기준가 ~1100pt
ROUND_TRIP_COST_PT = 2 * 1100.0 * 0.000015 + 2 * 0.05   # ≈ 0.133pt

Z95 = 1.959963985


def wilson_lower(hits, n, z=Z95):
    """이항비율의 Wilson 하한 (95%). n=0이면 0.0."""
    if n <= 0:
        return 0.0
    p = float(hits) / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    margin = (z / denom) * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    return max(0.0, center - margin)


def zone_of(ts):
    """시간대 구획: AM(09~11) / MID(12) / PM(13~15)."""
    hh = ts[11:13]
    if hh in ("08", "09", "10", "11"):
        return "AM"
    if hh == "12":
        return "MID"
    return "PM"


class EdgeLedger(object):
    """셀별 rolling 부호적중·EV 원장 + Wilson 하한 기반 등급 판정."""

    def __init__(self, window=WINDOW_DEFAULT, cuts=None,
                 c_phat_min=C_PHAT_MIN_DEFAULT, c_min_n=C_MIN_N_DEFAULT,
                 cost_pt=ROUND_TRIP_COST_PT):
        self.window = int(window)
        self.cuts = dict(cuts or GRADE_CUTS_DEFAULT)
        self.c_phat_min = float(c_phat_min)
        self.c_min_n = int(c_min_n)
        self.cost_pt = float(cost_pt)
        # cell -> deque[(hit or None, ev_pt or None)]
        self._buf = defaultdict(lambda: deque(maxlen=self.window))

    def stats(self, cell):
        buf = self._buf.get(cell)
        if not buf:
            return 0, 0.0, 0.0, 0, 0.0
        hits = [h for h, _ in buf if h is not None]
        evs = [e for _, e in buf if e is not None]
        n = len(hits)
        n_hit = sum(hits)
        phat = (float(n_hit) / n) if n else 0.0
        low = wilson_lower(n_hit, n)
        ev = (sum(evs) / len(evs)) if evs else 0.0
        return n, phat, low, len(evs), ev

    def grade(self, cell):
        n, phat, low, n_ev, ev = self.stats(cell)
        for g in ("A", "B"):
            low_min, min_n, need_ev = self.cuts[g]
            if n >= min_n and low >= low_min and (not need_ev or ev > 0.0):
                return g, n, phat, low, ev
        if n >= self.c_min_n and phat >= self.c_phat_min:
            return "C", n, phat, low, ev
        return "X", n, phat, low, ev

    def record(self, cell, hit, ev_pt):
        self._buf[cell].append((hit, ev_pt))

    def cells(self):
        return list(self._buf.keys())


def load_events(db_path, since="2026-05-08"):
    """(ts, horizon, direction, actual, realized_move, regime, legacy_grade) 시계열 로드."""
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # 레짐: ensemble_decisions에서 ts별 1건
    cur.execute(
        "SELECT ts, regime, grade FROM ensemble_decisions WHERE ts >= ?", (since,)
    )
    ens = {}
    for ts, regime, grade in cur.fetchall():
        ens[ts] = (regime or "UNKNOWN", grade or "?")

    # 실현 이동폭: meta_labels (ts, horizon)
    cur.execute(
        "SELECT ts, horizon, realized_move FROM meta_labels "
        "WHERE ts >= ? AND realized_move IS NOT NULL", (since,)
    )
    moves = {}
    for ts, hz, mv in cur.fetchall():
        moves[(ts, hz)] = float(mv)

    cur.execute(
        "SELECT ts, horizon, direction, actual FROM predictions "
        "WHERE ts >= ? AND actual IS NOT NULL AND horizon IN ('1m','3m','5m','10m','15m','30m') "
        "ORDER BY ts, horizon", (since,)
    )
    events = []
    for ts, hz, d, a in cur.fetchall():
        regime, legacy = ens.get(ts, ("UNKNOWN", "?"))
        events.append({
            "ts": ts, "hz": hz, "dir": int(d), "actual": int(a),
            "move": moves.get((ts, hz)),
            "regime": regime, "legacy": legacy,
        })
    con.close()
    return events


def ts_to_minutes(ts):
    """'YYYY-MM-DD HH:MM:SS' → 정렬·경과 비교용 절대 분. 날짜 경계는 큰 갭으로 취급."""
    y, mo, d = int(ts[0:4]), int(ts[5:7]), int(ts[8:10])
    hh, mi = int(ts[11:13]), int(ts[14:16])
    return ((y * 12 + mo) * 31 + d) * 1440 + hh * 60 + mi


def replay(events, ledger, verbose=False):
    """엄격 walk-forward 재생. 각 신호에 등급을 부여하고 실제 결과와 함께 반환."""
    pending = deque()   # (resolve_minute, cell, hit, ev)
    graded = []

    for ev in events:
        now = ts_to_minutes(ev["ts"])

        # 1) 결과가 확정된 과거 관측치만 원장에 반영 (미래참조 차단)
        while pending and pending[0][0] <= now:
            _, cell, hit, ev_pt = pending.popleft()
            ledger.record(cell, hit, ev_pt)

        cell = (HZ_GROUP[ev["hz"]], zone_of(ev["ts"]), ev["regime"])

        # 2) 방향성 신호에만 등급 부여 (FLAT 예측은 진입 대상 아님)
        if ev["dir"] != 0:
            g, n, phat, low, cell_ev = ledger.grade(cell)
            hit = None if ev["actual"] == 0 else (1 if ev["actual"] == ev["dir"] else 0)
            realized_ev = None
            if ev["move"] is not None:
                realized_ev = ev["move"] * ev["dir"] - ledger.cost_pt
            graded.append({
                "ts": ev["ts"], "hz": ev["hz"], "cell": cell, "grade": g,
                "n": n, "phat": phat, "low": low, "cell_ev": cell_ev,
                "hit": hit, "ev": realized_ev, "legacy": ev["legacy"],
            })

        # 3) 이 신호의 결과는 horizon 경과 후 확정 → 대기열에 적재
        hit = None if ev["actual"] == 0 else (1 if ev["actual"] == ev["dir"] else 0)
        ev_pt = None
        if ev["move"] is not None and ev["dir"] != 0:
            ev_pt = ev["move"] * ev["dir"] - ledger.cost_pt
        if ev["dir"] != 0:
            pending.append((now + HZ_MINUTES[ev["hz"]], cell, hit, ev_pt))

    return graded


def summarize(graded, title, since=None, until=None):
    sel = [g for g in graded
           if (since is None or g["ts"] >= since) and (until is None or g["ts"] < until)]
    print("\n" + "=" * 78)
    print(title + "  (n=%d)" % len(sel))
    print("=" * 78)
    if not sel:
        print("  (표본 없음)")
        return {}

    out = {}
    print("  %-6s %8s %8s %10s %10s %10s" % ("grade", "n", "share", "sign_acc", "n_hit", "EV(pt)"))
    for g in ("A", "B", "C", "X"):
        rows = [r for r in sel if r["grade"] == g]
        if not rows:
            print("  %-6s %8d %7.1f%%          -          -          -" % (g, 0, 0.0))
            out[g] = None
            continue
        hits = [r["hit"] for r in rows if r["hit"] is not None]
        evs = [r["ev"] for r in rows if r["ev"] is not None]
        acc = (sum(hits) / float(len(hits))) if hits else float("nan")
        ev = (sum(evs) / float(len(evs))) if evs else float("nan")
        print("  %-6s %8d %7.1f%% %10.4f %10d %10.4f" % (
            g, len(rows), 100.0 * len(rows) / len(sel), acc, len(hits), ev))
        out[g] = (len(rows), acc, ev, len(hits))
    return out


def check_guarantees(graded):
    """G1/G2/G3 판정."""
    print("\n" + "#" * 78)
    print("# 보장 판정 (G1 도달가능성 / G2 정직성 / G3 단조성)")
    print("#" * 78)

    # ── G2: 과신 구간(05-08~05-19)에서 A/B 남발 없어야 함
    early = [g for g in graded if g["ts"] < "2026-05-20"]
    early_ab = [g for g in early if g["grade"] in ("A", "B")]
    print("\n[G2 정직성] 2026-05-08~05-19 과신구간")
    print("  구 등급 실적(참고): A=474건 B=310건 (ensemble_decisions 전수)")
    print("  EdgeScore: 신호 %d건 중 A/B = %d건 (%.2f%%)" % (
        len(early), len(early_ab), 100.0 * len(early_ab) / max(1, len(early))))
    if early_ab:
        hits = [g["hit"] for g in early_ab if g["hit"] is not None]
        if hits:
            print("    → 그 A/B의 실측 부호적중 = %.4f (n=%d)" % (
                sum(hits) / float(len(hits)), len(hits)))
    g2 = len(early_ab) == 0 or (
        len(early_ab) / float(max(1, len(early))) < 0.02)
    print("  판정: %s" % ("PASS — 과신구간 A/B 억제됨" if g2 else "FAIL — 과신구간 A/B 남발"))

    # ── G1: 전 기간에서 A/B가 도달 가능한가
    ab = [g for g in graded if g["grade"] in ("A", "B")]
    print("\n[G1 도달가능성] 전 기간")
    print("  A/B 부여 = %d건 / 전체 %d건 (%.2f%%)" % (
        len(ab), len(graded), 100.0 * len(ab) / max(1, len(graded))))
    if ab:
        by_cell = defaultdict(int)
        by_month = defaultdict(int)
        for g in ab:
            by_cell[g["cell"]] += 1
            by_month[g["ts"][:7]] += 1
        print("  점등 셀 상위:")
        for cell, n in sorted(by_cell.items(), key=lambda x: -x[1])[:8]:
            print("    %-28s %d건" % (str(cell), n))
        print("  월별: %s" % dict(by_month))
    g1 = len(ab) > 0
    print("  판정: %s" % ("PASS — 엣지 구간에서 점등됨" if g1 else
                          "FAIL — 전 기간 A/B 0건 (컷이 도달불가)"))

    # ── G3: 등급별 단조성
    print("\n[G3 단조성] 등급별 실측 부호적중 (전 기간)")
    order = []
    for g in ("A", "B", "C", "X"):
        rows = [r for r in graded if r["grade"] == g]
        hits = [r["hit"] for r in rows if r["hit"] is not None]
        if len(hits) >= 30:
            acc = sum(hits) / float(len(hits))
            order.append((g, acc, len(hits)))
            print("    %s acc=%.4f (n=%d)" % (g, acc, len(hits)))
        else:
            print("    %s 표본부족(n=%d) — 단조성 판정 제외" % (g, len(hits)))
    mono = all(order[i][1] >= order[i + 1][1] - 1e-9 for i in range(len(order) - 1))
    print("  판정: %s" % ("PASS — 단조" if mono and len(order) >= 2 else
                          ("FAIL — 역전 존재" if len(order) >= 2 else "판정불가(표본부족)")))

    return {"G1": g1, "G2": g2, "G3": mono and len(order) >= 2}


def sweep(events):
    print("\n" + "#" * 78)
    print("# 파라미터 스윕 — (window, A컷, B컷) 조합별 G1/G2/G3")
    print("#" * 78)
    print("  %-24s %6s %6s %8s %8s %8s %8s" % (
        "params", "A건", "B건", "A_acc", "B_acc", "C_acc", "X_acc"))
    combos = []
    for window in (300, 500, 800):
        for a_low, b_low in ((0.55, 0.52), (0.55, 0.53), (0.54, 0.52)):
            for min_n_a, min_n_b in ((150, 150), (200, 200), (300, 300), (150, 100)):
                combos.append((window, a_low, b_low, min_n_a, min_n_b))
    best = []
    for window, a_low, b_low, min_n_a, min_n_b in combos:
        if min_n_a > window or min_n_b > window:
            continue
        cuts = {"A": (a_low, min_n_a, True), "B": (b_low, min_n_b, True)}
        led = EdgeLedger(window=window, cuts=cuts)
        gr = replay(events, led)
        res = {}
        for g in ("A", "B", "C", "X"):
            rows = [r for r in gr if r["grade"] == g]
            hits = [r["hit"] for r in rows if r["hit"] is not None]
            res[g] = (len(rows), (sum(hits) / float(len(hits))) if hits else float("nan"))
        early_ab = sum(1 for r in gr if r["ts"] < "2026-05-20" and r["grade"] in ("A", "B"))
        # 단조성: 표본 30건 이상인 등급만으로 A≥B≥C≥X 확인
        seq = [(g, res[g][1]) for g in ("A", "B", "C", "X") if res[g][0] >= 30
               and not math.isnan(res[g][1])]
        mono = all(seq[i][1] >= seq[i + 1][1] for i in range(len(seq) - 1)) and len(seq) >= 3
        has_ab = (res["A"][0] + res["B"][0]) > 0
        tag = "w%d A%.2f/%d B%.2f/%d" % (window, a_low, min_n_a, b_low, min_n_b)
        flag = "OK " if (mono and has_ab and early_ab < 0.02 * 6674) else "   "
        print("  %s%-22s %6d %6d %8.4f %8.4f %8.4f %8.4f  early_AB=%-4d %s" % (
            flag, tag, res["A"][0], res["B"][0], res["A"][1], res["B"][1],
            res["C"][1], res["X"][1], early_ab, "MONO" if mono else "inv"))
        if mono and has_ab:
            best.append((tag, res["A"][0] + res["B"][0], res))
    print("\n  단조성 PASS 조합: %d개" % len(best))
    for tag, n_ab, res in sorted(best, key=lambda x: -x[1])[:5]:
        print("    %-24s A/B계=%d (A_acc=%.4f B_acc=%.4f)" % (
            tag, n_ab, res["A"][1], res["B"][1]))


def cell_detail(graded):
    print("\n" + "#" * 78)
    print("# 셀별 상세 (부여등급 분포 + 실측 부호적중)")
    print("#" * 78)
    by_cell = defaultdict(list)
    for g in graded:
        by_cell[g["cell"]].append(g)
    print("  %-30s %7s %8s %s" % ("cell", "n", "acc", "등급분포"))
    for cell, rows in sorted(by_cell.items(), key=lambda x: -len(x[1])):
        hits = [r["hit"] for r in rows if r["hit"] is not None]
        acc = (sum(hits) / float(len(hits))) if hits else float("nan")
        dist = defaultdict(int)
        for r in rows:
            dist[r["grade"]] += 1
        dist_s = " ".join("%s=%d" % (g, dist[g]) for g in ("A", "B", "C", "X") if dist[g])
        print("  %-30s %7d %8.4f %s" % (str(cell), len(rows), acc, dist_s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--since", default="2026-05-08")
    ap.add_argument("--window", type=int, default=WINDOW_DEFAULT)
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--cell-detail", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.db):
        print("DB 없음: %s" % args.db)
        return 1

    print("EdgeScore 소급 재생 — DB=%s since=%s" % (args.db, args.since))
    print("왕복비용 가정 = %.4f pt (수수료 2×1100×0.000015 + 슬리피지 2×0.05)" % ROUND_TRIP_COST_PT)
    events = load_events(args.db, args.since)
    print("이벤트 로드: %d건 (predictions, actual 확정분)" % len(events))

    ledger = EdgeLedger(window=args.window)
    graded = replay(events, ledger)
    print("등급부여 신호: %d건 (방향성 예측만)" % len(graded))

    summarize(graded, "[전 기간] EdgeScore 등급별 실측")
    summarize(graded, "[과신구간] 2026-05-08 ~ 05-19", until="2026-05-20")
    summarize(graded, "[현재구간] 2026-05-20 ~ ", since="2026-05-20")

    check_guarantees(graded)

    if args.cell_detail:
        cell_detail(graded)
    if args.sweep:
        sweep(events)
    return 0


if __name__ == "__main__":
    sys.exit(main())

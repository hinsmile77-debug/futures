# -*- coding: utf-8 -*-
"""[MW0601 626차] 신동 사전등록 채점 — R2 · R3 · 섀도(E2+F2)를 **나눠서** 센다.

사전등록: `docs/신동거래/신동_사전등록_20260924.md` §4.

무엇을 내나
-----------
0. [MW0602 604차] v2 — MAIN = FLOWC. 채점 창은 `spec.SCORING_START`(v2) 부터. v1 창(R3 중단 판정)은 SHADOW_V1 +
   v2 이전 MAIN(v1 spec_version) 행으로 **따로** 센다. 종료된 섀도(E2F2·X4NF·TR44·X4NFA)는 「종료」 한 줄.
1. 변형(spec.VARIANTS) × 규칙(R2 / R3 / FLOW / BRK)별 거래 수 · 승 · 순손익 · 거래당
2. 규칙가 vs **실현가능가** — 라이브 행은 처음 알아챈 시각의 최신 종가(`detect_px`)로
   진입했다고 보고 같은 청산가로 다시 잰다. 09:00·09:01 흐름은 09:02 수집(PEAK_SKIP)에서야
   들어오므로 R2 는 구조적으로 늦게 탐지된다 — 그 비용이 여기서 드러난다.
3. R3 중단 판정 — 채점 시작 후 `R3_KILL_AFTER_DAYS` 거래일이 차면
   MAIN R3 누적 순손익 < 0 **이고** 승률 < 35% 이면 「중단」.
   🔴 판정 기준은 `strategy/shindong/spec.py` 에서 읽는다 — 여기서 값을 바꾸지 말 것.

4. [MW0602 598차] **표시만**(판정 아님) — R3 분리(깨진 맥점 · R1 정렬 · [603차] 저변동 진입), R1·R2 경제성(보류일·R2 확정률),
   「보이는 대로」 손익(철회된 라이브 신호를 철회 시점 시장가로 청산했다고 본 값).

⚠ 채점 시작일(9/28) 이전 행(9/21–9/23 백필 등)은 **표본에 넣지 않는다** — 규칙을 만든 날이다.
⚠ `RETRACTED`(재계산에서 사라진 신호)는 표본에서 빼되 건수는 따로 적는다(탈락 가시화, 계측 4원칙 ③).

사용:
    python scripts/shindong_scorecard.py                 # 표준출력
    python scripts/shindong_scorecard.py --out docs/신동거래/채점_YYYYMMDD.md
"""
import argparse
import datetime as _dt
import json
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.settings import (PREMARKET_LEVELS_DB, RAW_DATA_DB, SHINDONG_DB,  # noqa: E402
                             WEEKLY_OPTION_FLOW_DB)
FLOW_DB = WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) else os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)
from strategy.shindong import spec  # noqa: E402
from strategy.shindong.engine import leg_net  # noqa: E402


def _fmt(v):
    return format(float(v), "+,.0f")


def _load(db, since):
    con = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True)
    con.row_factory = sqlite3.Row
    try:
        trades = [dict(r) for r in con.execute(
            "SELECT * FROM shindong_trades WHERE trade_date>=? ORDER BY trade_date, entry_ts",
            (since,))]
        days = [dict(r) for r in con.execute(
            "SELECT * FROM shindong_day WHERE trade_date>=? ORDER BY trade_date", (since,))]
    finally:
        con.close()
    return trades, days


def _realizable_net(t):
    """처음 알아챈 시각의 종가로 들어갔다면. 라이브 행이 아니면 None(미측정)."""
    if t.get("source") != "live" or t.get("detect_px") is None:
        return None
    e = float(t["detect_px"])
    tot = 0.0
    for n in (1, 2):
        if not t.get("leg%d_exit_ts" % n):
            return None                       # 보유 중 — 아직 못 잰다
        x = float(t["leg%d_exit_px" % n])
        mkt = (t.get("leg%d_reason" % n) or "") in ("SL", "BE", "TIME", "TR")
        tot += leg_net(int(t["side"]), e, x, mkt)[1]
    return tot


def _is_broken(t):
    """[598차] R3 진입가가 터치 맥점을 이미 반대로 넘어가 있는가 — SHADOW_X4NFA 가 막는 진입."""
    if t.get("rule") != "R3" or t.get("touch_level") is None:
        return None
    return int(t["side"]) * (float(t["entry_px"]) - float(t["touch_level"])) <= 0


def _lowvol_ctx(raw_db, levels_db):
    """[603차] 저변동 판별에 쓰는 읽기 전용 연결 2개. 없으면 None(미측정)."""
    def _ro(p):
        return sqlite3.connect("file:%s?mode=ro" % p.replace("\\", "/"), uri=True) if p and os.path.exists(p) else None
    return _ro(raw_db), _ro(levels_db)


def _is_lowvol(t, ctx):
    """[603차] R3 진입 분이 「저변동(횡보 예보)」이었나 — 채점표 기록 축(판정 아님).

    True  = 진입 분 `realized_vol_ann` ≤ LOWVOL_RV_MAX **또는** 직전 60봉 고저 범위 ≤ 0.30×ATR14.
    False = 둘 다 측정됐고 둘 다 아님(한쪽만 측정되면 그 한쪽으로 판정).
    None  = 어느 쪽도 못 쟀다(미측정 ≠ 정상 변동 — 계측 4원칙 ②).
    두 조건은 76일 사전 감지 실측에서 앞 60분 횡보를 71~80% 맞힌 축이다(spec 주석·딥다이브 §3).
    """
    if t.get("rule") != "R3" or not t.get("entry_ts"):
        return None
    raw_con, lv_con = ctx if ctx else (None, None)
    if raw_con is None:
        return None
    day, ent = str(t["trade_date"]), str(t["entry_ts"])[:16]
    rv = None
    r = raw_con.execute("SELECT features FROM raw_features WHERE ts>=? AND ts<=? ORDER BY ts DESC LIMIT 1",
                        (ent + ":00", ent + ":59")).fetchone()
    if r:
        try:
            v = json.loads(r[0]).get("realized_vol_ann")
            rv = float(v) if isinstance(v, (int, float)) else None
        except (TypeError, ValueError):
            rv = None
    rng = None
    bars = raw_con.execute("SELECT high, low FROM raw_candles WHERE ts>=? AND ts<=? ORDER BY ts DESC LIMIT ?",
                           (day + " 00:00", ent + ":59", spec.LOWVOL_RANGE_BARS)).fetchall()
    atr14 = None
    if lv_con is not None:
        try:
            a = lv_con.execute("SELECT atr14 FROM premarket_levels WHERE date=? AND stage='0850'", (day,)).fetchone()
        except sqlite3.OperationalError:       # 컬럼·테이블 없음(옛 DB) → 범위 축 미측정
            a = None
        atr14 = float(a[0]) if a and a[0] is not None else None
    if bars and atr14:
        rng = max(b[0] for b in bars) - min(b[1] for b in bars)
    c1 = None if rv is None else (rv <= spec.LOWVOL_RV_MAX)
    c2 = None if rng is None else (rng <= spec.LOWVOL_RANGE60_ATR_MULT * atr14)
    if c1 is None and c2 is None:
        return None
    return bool(c1) or bool(c2)


def _retract_px(con, t):
    """철회를 알아챈 벽시계(`updated_at`) 직전에 **완성된** 1분봉 종가. 못 구하면 None(미측정)."""
    if con is None or not t.get("updated_at"):
        return None
    ts = _dt.datetime.strptime(str(t["updated_at"])[:19], "%Y-%m-%d %H:%M:%S")
    bar = (ts.replace(second=0) - _dt.timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:59")
    r = con.execute("SELECT close FROM raw_candles WHERE ts>=? AND ts<=? ORDER BY ts DESC LIMIT 1",
                    (t["trade_date"] + " 00:00", bar)).fetchone()
    return float(r[0]) if r else None


def _as_seen_net(t, con):
    """[598차] 철회된 라이브 신호를 화면에서 보고 따랐다면 — 실현가능가(`detect_px`) 진입,
    철회 전에 닫힌 다리는 그 청산가, 남은 다리는 철회 시점 종가에 시장가 청산.
    백필 행 · 원천 없음은 None(미측정 ≠ 0)."""
    if t.get("source") != "live" or t.get("status") != "RETRACTED":
        return None
    e = float(t["detect_px"] if t.get("detect_px") is not None else t["entry_px"])
    side = int(t["side"])
    rpx = None
    tot = 0.0
    for n in (1, 2):
        if t.get("leg%d_exit_ts" % n):
            x = float(t["leg%d_exit_px" % n])
            mkt = (t.get("leg%d_reason" % n) or "") in ("SL", "BE", "TIME", "TR")
        else:
            if rpx is None:
                rpx = _retract_px(con, t)
                if rpx is None:
                    return None
            x, mkt = rpx, True
        tot += leg_net(side, e, x, mkt)[1]
    return tot


def _r1_hits(days, raw_db):
    """[632차 후속] R1 방향 적중 — 방향대로 09:00 종가 → 15:05 종가가 움직였나.

    반환 [(날짜, bias, 09:00 종가, 15:05 종가, 적중 True/False/None)]. None = 봉 결측(미측정 ≠ 불적중).
    """
    rows = [d for d in days if d["variant"] == "MAIN" and d.get("bias")]
    out = []
    con = None
    if raw_db and os.path.exists(raw_db):
        con = sqlite3.connect("file:%s?mode=ro" % raw_db.replace("\\", "/"), uri=True)
    try:
        for d in rows:
            a = b = None
            if con is not None:
                day = d["trade_date"]
                r = con.execute("SELECT close FROM raw_candles WHERE ts>=? AND ts<=? ORDER BY ts DESC LIMIT 1",
                                (day + " 00:00", "%s %s:59" % (day, spec.R1_HIT_FROM))).fetchone()
                a = r[0] if r else None
                r = con.execute("SELECT close, ts FROM raw_candles WHERE ts>=? AND ts<=? ORDER BY ts DESC LIMIT 1",
                                ("%s %s" % (day, spec.R1_HIT_FROM), "%s %s:59" % (day, spec.R1_HIT_TO))).fetchone()
                # 15:05 봉이 아직 없으면(장중) 미측정
                b = r[0] if (r and str(r[1])[11:16] >= spec.R1_HIT_TO) else None
            hit = None if (a is None or b is None or b == a) else (int(d["bias"]) * (b - a) > 0)
            out.append((d["trade_date"], int(d["bias"]), a, b, hit))
    finally:
        if con is not None:
            con.close()
    return out


def build(db=SHINDONG_DB, since=spec.SCORING_START, raw_db=RAW_DATA_DB, levels_db=PREMARKET_LEVELS_DB,
          flow_db=None):
    flow_db = FLOW_DB if flow_db is None else flow_db
    lines = []
    w = lines.append
    w("# 신동 채점표 (%s 기준)" % _dt.date.today().isoformat())
    w("")
    w("- 규격: `%s`(MAIN = %s) · v2 채점 시작 %s · v1 창(SHADOW_V1 · R3 중단 판정) %s 부터 · DB `%s`" % (
        spec.SPEC_VERSION, spec.MAIN_FAMILY.upper(), since, spec.V1_SCORING_START, db))
    if not os.path.exists(db):
        w("- **미배선** — DB 가 없다(0건이 아니다)")
        return "\n".join(lines)
    trades_all, days_all = _load(db, min(since, spec.V1_SCORING_START))
    trades = [t for t in trades_all if t["trade_date"] >= since]
    days = [d for d in days_all if d["trade_date"] >= since]
    main_days = sorted({d["trade_date"] for d in days if d["variant"] == "MAIN"})
    w("- v2 판정 기록 거래일: **%d일**" % len(main_days))
    for v, st in sorted(spec.LATE_SHADOW_START.items()):
        pre = [t for t in trades if t["variant"] == v and t["trade_date"] < st]
        if pre:
            trades = [t for t in trades if t not in pre]
            w("- %s 채점 시작(%s) 전 행 **%d건** — 표본 제외" % (v, st, len(pre)))
    retr = [t for t in trades if t["status"] == "RETRACTED"]
    live = [t for t in trades if t["status"] != "RETRACTED"]
    if retr:
        w("- ⚠ 재계산에서 사라진 신호(RETRACTED) **%d건** — 표본 제외" % len(retr))
    openn = [t for t in live if t["status"] == "OPEN"]
    if openn:
        w("- 보유 중(OPEN) %d건 — 순손익은 닫힌 다리만" % len(openn))
    retired = {v: sum(1 for t in trades_all if t["variant"] == v) for v in spec.RETIRED_SHADOWS}
    if any(retired.values()):
        w("- 종료된 섀도(DB 행 보존 · 판정 없음): " + " · ".join(
            "%s %d행(%s)" % (v, n, spec.RETIRED_SHADOWS[v]) for v, n in sorted(retired.items()) if n))
    w("")
    w("## 1. 변형 × 규칙 (v2 창)")
    w("")
    w("| 변형 | 규칙 | 거래 | 승 | 승률 | 순손익(원) | 거래당 | 실현가능가 순손익* |")
    w("|---|---|---|---|---|---|---|---|")
    for v in spec.VARIANTS:
        rules = sorted({t["rule"] for t in live if t["variant"] == v}) + ["합계"]
        for rule in rules:
            xs = [t for t in live if t["variant"] == v and (rule == "합계" or t["rule"] == rule)]
            closed = [t for t in xs if t["status"] == "CLOSED"]
            n = len(closed)
            win = sum(1 for t in closed if _net(t) > 0)
            tot = sum(_net(t) for t in closed)
            rz = [_realizable_net(t) for t in closed]
            rz_ok = [x for x in rz if x is not None]
            w("| %s | %s | %d | %d | %s | %s | %s | %s |" % (
                v, rule, n, win, ("%.0f%%" % (100.0 * win / n)) if n else "-", _fmt(tot),
                _fmt(tot / n) if n else "-",
                ("%s (%d/%d건)" % (_fmt(sum(rz_ok)), len(rz_ok), n)) if rz_ok else ("-" if n else "-")))
    w("")
    w("\\* 실현가능가 = 처음 알아챈 시각(`detected_at`)의 최신 종가로 진입했다고 보고 같은 청산가로 다시 잰 값. "
      "백필·보유 중 행은 재지 못한다(미측정 ≠ 0).")
    w("")
    w("## 2. 일별 (MAIN v2)")
    w("")
    ctxs = {}                                      # [605차] 날짜 → (DayFrame, 맥점) — 일별 계측·재난 손절 반사실이 같이 쓴다
    w("\n".join(_daily_section(live, days, raw_db, flow_db, levels_db, ctxs)))
    w("")
    sec = 3
    w("## %d. v2 vs V1 되돌림 판정 (사전등록 V2 §4)" % sec)
    w("")
    w("\n".join(_rollback_judge(live, days)))
    w("")
    sec += 1
    for v, m in spec.SHADOW_META:
        if v == "SHADOW_V1":
            continue
        w("## %d. %s 판정 (%s 사전등록)" % (sec, v, m.get("origin", "")))
        w("")
        w("\n".join(_late_judge(live, days, v)))
        w("")
        sec += 1
    w("## %d. V1 레거시 — R3 중단 판정 (v1 사전등록 §3 · %s 부터 · 표본 = v2 이전 MAIN + SHADOW_V1)" % (
        sec, spec.V1_SCORING_START))
    w("")
    w("\n".join(_v1_r3_kill_section(trades_all, days_all)))
    w("")
    sec += 1
    w("## %d. R1 방향 적중률 (표시 — 판정 아님 · %s 부터)" % (sec, spec.V1_SCORING_START))
    w("")
    w("\n".join(_r1_section(_r1_hits(days_all, raw_db))))
    w("")
    sec += 1
    w("## %d. R1·R2 경제성 (표시 — 판정 아님 · v1 행 · %s 부터)" % (sec, spec.V1_SCORING_START))
    w("")
    v1_live = [t for t in trades_all if _is_v1(t) and t["status"] != "RETRACTED"]
    w("\n".join(_r2_econ_section(v1_live, days_all)))
    w("")
    sec += 1
    w("## %d. R3 분리 — 깨진 맥점 · R1 정렬 · 저변동 진입 (v1 행, 표시 — 판정 아님)" % sec)
    w("")
    ctx = _lowvol_ctx(raw_db, levels_db)          # [603차] 저변동 축 — raw_features · raw_candles · ATR14
    try:
        w("\n".join(_r3_split_section(v1_live, days_all, ctx)))
    finally:
        for _con in ctx:
            if _con is not None:
                _con.close()
    w("")
    sec += 1
    w("## %d. FLOWC ↔ FLOWF 대조 — 같은 규칙 · 다른 원천 (표시 — 판정 아님)" % sec)
    w("")
    w("\n".join(_flow_pair_section(live, days)))
    w("")
    sec += 1
    w("## %d. 재난 손절 발동일 — 실제 vs 반사실 (MAIN, 표시 — 판정 아님)" % sec)
    w("")
    w("\n".join(_cat_stop_section(live, days, raw_db, flow_db, levels_db, ctxs)))
    w("")
    sec += 1
    w("## %d. 보이는 대로 손익 — 철회된 라이브 신호 포함 (표시 — 판정 아님)" % sec)
    w("")
    w("\n".join(_as_seen_section(live, retr, raw_db)))
    return "\n".join(lines)


def _net(t):
    return float(t.get("net_krw") or 0)


def _day_ctx(day, raw_db, flow_db, levels_db, cache):
    """[605차] 그날의 (DayFrame, 맥점) — 하루치만 읽는다. 원천이 없으면 None(미측정)."""
    if day in cache:
        return cache[day]
    out = None
    try:
        from strategy.shindong import engine as _E, runner as _RN
        from strategy.shindong.calendar import select_flow_product
        if raw_db and os.path.exists(raw_db) and levels_db and os.path.exists(levels_db):
            prod = select_flow_product(_dt.date.fromisoformat(day))[0]
            c, f, lv = _RN.load_inputs(day, prod, raw_db, flow_db or "", levels_db)
            if c and "0850" in lv:
                out = (_E.DayFrame(c, f), _E.prepare_levels(lv))
    except Exception:                               # 원천 스키마가 다르면 미측정으로 둔다(채점표가 죽지 않게)
        out = None
    cache[day] = out
    return out


def _daily_section(live, days, raw_db, flow_db, levels_db, ctxs):
    """[605차] 일별 표 + 계측 4열(판정 아님): 만기일 · 당일 콜−풋 진폭 · R1 적중 · 첫 진입 시각(10:00 전/후)."""
    from strategy.shindong.calendar import select_flow_product
    hits = {h[0]: h[4] for h in _r1_hits(days, raw_db)}
    out = ["| 날짜 | 상품 | 만기일 | 장전 콜−풋 | 방향 | R1 적중 | 콜−풋 진폭 | R2(V1) | 첫 진입 | 거래 | 순손익(원) |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    early = {"전": [], "후": [], "없음": []}
    for d in [x for x in days if x["variant"] == "MAIN"]:
        day = d["trade_date"]
        xs = [t for t in live if t["variant"] == "MAIN" and t["trade_date"] == day]
        closed = [t for t in xs if t["status"] == "CLOSED"]
        net = sum(_net(t) for t in closed)
        try:
            exp = select_flow_product(_dt.date.fromisoformat(day))[1]
            is_exp = "만기" if exp.isoformat() == day else "-"
        except Exception:
            is_exp = "미측정"
        ctx = _day_ctx(day, raw_db, flow_db, levels_db, ctxs)
        amp = "미측정"
        if ctx is not None:
            sp = [v for k, v in ctx[0].sp.items() if "09:00" <= k <= spec.TIME_EXIT]
            if sp:
                amp = "%.0f" % (max(sp) - min(sp))
        first = min((str(t["entry_ts"])[11:16] for t in xs), default=None)
        if first is None:
            fe = "-"
            early["없음"].append(net)
        else:
            lab = "전" if first < "10:00" else "후"
            fe = "%s (10:00 %s)" % (first, lab)
            early[lab].append(net)
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %d | %s |" % (
            day, d.get("product") or "-", is_exp,
            ("%+.0f" % d["pm_sp"]) if d.get("pm_sp") is not None else "미수집",
            {-1: "하방", 0: "보류", 1: "상방", None: "-"}.get(d.get("bias"), "?"),
            {True: "적중", False: "불적중", None: "-"}[hits.get(day)], amp,
            (d.get("r2_status") or "-") + ((" " + str(d["r2_ts"])) if d.get("r2_ts") else ""),
            fe, len(closed), _fmt(net)))
    out.append("")
    out.append("- 첫 진입 시각별 MAIN 손익: 10:00 이전 %d일 %s원 · 이후 %d일 %s원 · 진입 없음 %d일. "
               "콜−풋 진폭 = 그날 09:00~15:05 개인 콜−풋의 고저 폭(백만원) — 문턱 %d 이 진폭에 비해 작은 날을 가려 보려는 계측이다(판정 아님)."
               % (len(early["전"]), _fmt(sum(early["전"])), len(early["후"]), _fmt(sum(early["후"])), len(early["없음"]), spec.FLOWC_K))
    return out


def _cat_stop_section(live, days, raw_db, flow_db, levels_db, ctxs):
    """[605차] 재난 손절이 발동한 날 — 실제 손익과 반사실 둘(손절이 없었다면 · 같은 방향만 중단했다면).
    반사실 ②가 「동방향만 중단」 변형의 증거를 섀도 슬롯 없이 쌓는다. 원천이 없으면 미측정(0 으로 메우지 않는다)."""
    from strategy.shindong import engine as _E, families as _F
    mdays = sorted({d["trade_date"] for d in days if d["variant"] == "MAIN"})
    hit = {}
    for t in live:
        if t["variant"] == "MAIN" and t.get("rule") == "FLOW" and (t.get("leg1_reason") or "") == "SL":
            hit.setdefault(t["trade_date"], str(t.get("leg1_exit_ts") or "")[11:16])
    if not hit:
        return ["- 발동 없음 — 0 / %d 거래일" % len(mdays)]
    out = ["| 날짜 | 발동 시각 | 실제(v2.1) | 손절이 없었다면 | 같은 방향만 중단했다면 |", "|---|---|---|---|---|"]
    tot = {"act": 0.0, "nostop": [], "same": []}
    for day in sorted(hit):
        act = sum(_net(t) for t in live if t["variant"] == "MAIN" and t["trade_date"] == day and t["status"] == "CLOSED")
        tot["act"] += act
        ctx = _day_ctx(day, raw_db, flow_db, levels_db, ctxs)
        cells = []
        for key, kw in (("nostop", dict(cat_atr=None, halt_mode=None)),
                        ("same", dict(cat_atr=spec.FLOW_CAT_STOP_ATR, halt_mode="same"))):
            trs = _F.flowc_counterfactual(ctx[0], ctx[1], **kw) if ctx is not None else None
            if trs is None:
                cells.append("미측정")
            else:
                v = sum(_E.trade_net(t) for t in trs if t["status"] == "CLOSED")
                tot[key].append(v)
                cells.append("%s (%d거래)" % (_fmt(v), len(trs)))
        out.append("| %s | %s | %s | %s | %s |" % (day, hit[day] or "-", _fmt(act), cells[0], cells[1]))
    out.append("")
    out.append("- 발동 **%d / %d 거래일** · 실제 합 %s원 · 손절이 없었다면 %s · 같은 방향만 중단했다면 %s" % (
        len(hit), len(mdays), _fmt(tot["act"]),
        (_fmt(sum(tot["nostop"])) + "원") if len(tot["nostop"]) == len(hit) else "일부 미측정",
        (_fmt(sum(tot["same"])) + "원") if len(tot["same"]) == len(hit) else "일부 미측정"))
    out.append("- 반사실은 그날 봉·흐름·맥점으로 다시 계산한 값이다(장후 원천 기준 — 라이브 철회와 무관). "
               "재난 손절 폭(0.6×ATR14)과 중단 방식의 재검토 근거로만 쓴다 — 20거래일 전 규격 변경 금지.")
    return out


def _is_v1(t):
    """[604차] v1(R1/R2/R3) 규칙으로 난 행인가 — SHADOW_V1, 또는 v2 이전 MAIN(spec_version v1 · 미기록은 v1 로 본다)."""
    v = t.get("variant")
    if v == "SHADOW_V1":
        return True
    if v == "MAIN":
        return (t.get("spec_version") or spec.V1_SPEC_VERSION) == spec.V1_SPEC_VERSION
    return False


def _grp_row(label, xs):
    n = len(xs)
    win = sum(1 for t in xs if _net(t) > 0)
    tot = sum(_net(t) for t in xs)
    return "| %s | %d | %d | %s | %s | %s |" % (
        label, n, win, ("%.0f%%" % (100.0 * win / n)) if n else "-", _fmt(tot), _fmt(tot / n) if n else "-")


def _r2_econ_section(live, days):
    """[598차] R3 중단 판정 뒤 「R2 만 남으면」을 결과 보기 전에 보이게 둔다."""
    md = [d for d in days if d["variant"] == "MAIN"]
    if not md:
        return ["- 판정 기록 없음"]
    dirs = [d for d in md if d.get("bias")]
    hold = [d for d in md if not d.get("bias")]
    conf = [d for d in dirs if d.get("r2_status") == "CONFIRMED"]
    r2 = [t for t in live if _is_v1(t) and t["rule"] == "R2" and t["status"] == "CLOSED"]   # [604차] v1 행
    out = ["| 항목 | 값 |", "|---|---|",
           "| 판정 거래일 | %d |" % len(md),
           "| R1 보류일(콜−풋 절댓값 < %d 또는 미수집) | %d (%.0f%%) |" % (
               spec.BIAS_MIN, len(hold), 100.0 * len(hold) / len(md)),
           "| R1 방향일 | %d |" % len(dirs),
           "| R2 확정 / 방향일 | %d / %d%s |" % (
               len(conf), len(dirs), (" = %.0f%%" % (100.0 * len(conf) / len(dirs))) if dirs else ""),
           "| R2 닫힌 거래 · 승 · 순손익 | %d · %d · %s원 |" % (
               len(r2), sum(1 for t in r2 if _net(t) > 0), _fmt(sum(_net(t) for t in r2)))]
    out.append("")
    out.append("- 보류일에는 R2 가 없다 — R3 가 중단되면 그날 신동은 거래하지 않는다. 판정 전에 이 비율을 본다.")
    return out


def _r3_split_section(live, days, lowvol_ctx=None):
    bias = {d["trade_date"]: d.get("bias") for d in days if d["variant"] == "MAIN"}
    r3 = [t for t in live if _is_v1(t) and t["rule"] == "R3" and t["status"] == "CLOSED"]   # [604차] v1 행
    if not r3:
        return ["- v1 R3 닫힌 거래 없음"]
    out = ["| 구분 | 거래 | 승 | 승률 | 순손익(원) | 거래당 |", "|---|---|---|---|---|---|"]
    out.append(_grp_row("정상 진입(맥점 이쪽 편)", [t for t in r3 if _is_broken(t) is False]))
    out.append(_grp_row("**깨진 맥점 진입** (X4NFA 차단 대상)", [t for t in r3 if _is_broken(t)]))
    miss = [t for t in r3 if _is_broken(t) is None]
    if miss:
        out.append("| 맥점 미기록(미측정) | %d | | | | |" % len(miss))

    def al(t):
        b = bias.get(t["trade_date"])
        return None if not b else (int(t["side"]) == int(b))
    out.append(_grp_row("R1 방향과 같음", [t for t in r3 if al(t) is True]))
    out.append(_grp_row("R1 방향과 반대", [t for t in r3 if al(t) is False]))
    out.append(_grp_row("R1 보류일", [t for t in r3 if al(t) is None]))
    # [603차] 저변동(횡보 예보) 진입 — 진입 분 realized_vol 하위 1/3 또는 직전 60분 범위 ≤ 0.30×ATR14
    lv = {id(t): _is_lowvol(t, lowvol_ctx) for t in r3}
    out.append(_grp_row("**저변동 진입**(횡보 예보 — rv≤%.2f 또는 60분범위≤%.2f×ATR14)" % (
        spec.LOWVOL_RV_MAX, spec.LOWVOL_RANGE60_ATR_MULT), [t for t in r3 if lv[id(t)] is True]))
    out.append(_grp_row("정상 변동 진입", [t for t in r3 if lv[id(t)] is False]))
    miss_lv = [t for t in r3 if lv[id(t)] is None]
    if miss_lv:
        out.append("| 변동성 미측정(피처·봉·ATR14 없음) | %d | | | | |" % len(miss_lv))
    out.append("")
    out.append("- 기록만 한다 — 이 표로 규격을 바꾸지 않는다(사전등록 §6). R1 정렬은 조건으로 올리지 않는다(다중비교).")
    out.append("- 저변동 축도 게이트가 아니다 — 횡보에서 R3 를 막는 방어는 6일·76일 대리 모두 효과가 없었다"
               "(`신동_횡보구간_방어전략_딥다이브_MW0602-20260930.md` §4). 표본이 쌓이면 X4NF 판정 옆에 둔다.")
    return out


def _as_seen_section(live, retr, raw_db):
    con = None
    if raw_db and os.path.exists(raw_db):
        con = sqlite3.connect("file:%s?mode=ro" % raw_db.replace("\\", "/"), uri=True)
    out = ["| 변형 | 채점 순손익(닫힌 거래) | 철회 신호(라이브) | 철회분 보이는 대로 | **보이는 대로 합** |",
           "|---|---|---|---|---|"]
    try:
        for v in spec.VARIANTS:
            closed = sum(_net(t) for t in live if t["variant"] == v and t["status"] == "CLOSED")
            rv = [t for t in retr if t["variant"] == v and t.get("source") == "live"]
            vals = [_as_seen_net(t, con) for t in rv]
            ok = [x for x in vals if x is not None]
            miss = len(vals) - len(ok)
            out.append("| %s | %s | %d%s | %s | **%s** |" % (
                v, _fmt(closed), len(rv), (" (미측정 %d)" % miss) if miss else "",
                _fmt(sum(ok)) if rv else "-", _fmt(closed + sum(ok))))
    finally:
        if con is not None:
            con.close()
    out.append("")
    out.append("- 철회 신호 = 화면에 진입으로 떴다가 원천 흐름 재수신으로 사라진 거래. 채점은 이것을 뺀다(사전등록 §4).")
    out.append("- 보이는 대로 = 그 신호를 따라 탐지 시각 종가에 들어가, 철회를 알아챈 직전 완성봉 종가에 "
               "시장가로 나왔다고 본 값. 원천 봉이 없으면 미측정.")
    return out


def _r1_section(hits):
    out = ["적중 = R1 방향으로 %s 종가 → %s 종가가 움직였는가. 보류일(방향 없음)은 대상이 아니다." % (
        spec.R1_HIT_FROM, spec.R1_HIT_TO), ""]
    if not hits:
        return out + ["- 방향 판정일 없음"]
    out += ["| 날짜 | R1 | %s | %s | 적중 |" % (spec.R1_HIT_FROM, spec.R1_HIT_TO), "|---|---|---|---|---|"]
    for day, b, a, c, hit in hits:
        out.append("| %s | %s | %s | %s | %s |" % (
            day, "하방" if b < 0 else "상방", ("%.2f" % a) if a is not None else "-",
            ("%.2f" % c) if c is not None else "-", {True: "적중", False: "불적중", None: "미측정"}[hit]))
    meas = [h[4] for h in hits if h[4] is not None]
    miss = len(hits) - len(meas)
    rate = (sum(meas) / float(len(meas))) if meas else None
    out.append("")
    out.append("- 적중 **%d / %d**%s%s" % (
        sum(meas), len(meas), (" = **%.0f%%**" % (100 * rate)) if rate is not None else "",
        (" · 미측정 %d일 제외" % miss) if miss else ""))
    out.append("- 읽는 기준(R2 단독 연구 · 74일 대리 대략값): < %.0f%% 이면 R2 현행 구조는 적자 · "
               "68–76%% 는 +20pt 익절 우위 · ≥ 76%% 는 현행 우위. **표본이 작을 때 이 기준으로 청산을 바꾸지 말 것.**"
               % (100 * spec.R1_BREAKEVEN_HINT))
    return out


def _by_day(live, xdays, v):
    m = {d: 0.0 for d in xdays}
    for t in live:
        if t["variant"] == v and t["trade_date"] in m and t["status"] == "CLOSED":
            m[t["trade_date"]] += float(t.get("net_krw") or 0)
    return m


def _rollback_judge(live, days):
    """[604차] v2 되돌림 — SHADOW_V1 이 MAIN(v2)보다 순손익이 크고 **그리고** 최악일도 덜 나쁘면 v1 복귀."""
    xdays = sorted({d["trade_date"] for d in days if d["variant"] == "MAIN"})
    if not xdays:
        return ["- 기록 없음 — v2 채점 시작 %s 이후 MAIN 판정 행이 없다(미측정 ≠ 0)" % spec.SCORING_START]
    mm, vv = _by_day(live, xdays, "MAIN"), _by_day(live, xdays, "SHADOW_V1")
    out = ["| 변형 | 거래일 | 순손익(원) | 최악일(원) |", "|---|---|---|---|"]
    for v, m in (("MAIN(v2)", mm), ("SHADOW_V1", vv)):
        out.append("| %s | %d | %s | %s |" % (v, len(m), _fmt(sum(m.values())), _fmt(min(m.values()))))
    if len(xdays) < spec.JUDGE_AFTER_DAYS:
        out.append("- 판정: **대기** — %d/%d 거래일" % (len(xdays), spec.JUDGE_AFTER_DAYS))
    else:
        back = sum(vv.values()) > sum(mm.values()) and min(vv.values()) > min(mm.values())
        out.append("- 판정: **%s** (기준: V1 이 순손익 우위 **그리고** 최악일 개선이면 복귀)" % (
            "v1 복귀 — v3 로 재사전등록" if back else "v2 유지"))
    return out


def _flow_pair_section(live, days):
    """[604차] MAIN(콜−풋) vs SHADOW_FLOWF(외국인 선물) — 같은 날 첫 진입 방향 일치 · 일별 손익. 표시만."""
    xdays = sorted({d["trade_date"] for d in days if d["variant"] == "MAIN"})
    if not xdays:
        return ["- 기록 없음"]
    out = ["| 날짜 | MAIN 첫 진입 | FLOWF 첫 진입 | 방향 | MAIN 순손익 | FLOWF 순손익 |", "|---|---|---|---|---|---|"]
    agree = n = 0
    mm, ff = _by_day(live, xdays, "MAIN"), _by_day(live, xdays, "SHADOW_FLOWF")
    for day in xdays:
        def first(v):
            xs = sorted([t for t in live if t["variant"] == v and t["trade_date"] == day], key=lambda t: t["entry_ts"])
            return xs[0] if xs else None
        a, b = first("MAIN"), first("SHADOW_FLOWF")
        same = None if (a is None or b is None) else (int(a["side"]) == int(b["side"]))
        if same is not None:
            n += 1
            agree += int(same)
        lab = lambda t: ("%s %s" % (str(t["entry_ts"])[11:16], "매수" if int(t["side"]) > 0 else "매도")) if t else "-"
        out.append("| %s | %s | %s | %s | %s | %s |" % (
            day, lab(a), lab(b), {True: "같음", False: "반대", None: "-"}[same], _fmt(mm[day]), _fmt(ff[day])))
    out.append("")
    out.append("- 첫 진입 방향 일치 **%d / %d** · 둘 다 거래한 날만 센다. 기록만 한다(판정 아님)." % (agree, n))
    return out


def _v1_r3_kill_section(trades_all, days_all):
    """v1 사전등록 §3 그대로 — 표본은 v1 행(v2 이전 MAIN + SHADOW_V1), R3 만."""
    v1 = [t for t in trades_all if _is_v1(t) and t["status"] != "RETRACTED"]
    v1days = sorted({d["trade_date"] for d in days_all
                     if (d["variant"] == "SHADOW_V1") or
                     (d["variant"] == "MAIN" and (d.get("spec_version") or spec.V1_SPEC_VERSION) == spec.V1_SPEC_VERSION)})
    r3 = [t for t in v1 if t["rule"] == "R3" and t["status"] == "CLOSED"]
    n = len(r3)
    win = sum(1 for t in r3 if _net(t) > 0)
    tot = sum(_net(t) for t in r3)
    out = ["- v1 R3 닫힌 거래 %d건 · 순손익 %s원 · 승률 %s" % (n, _fmt(tot), ("%.0f%%" % (100.0 * win / n)) if n else "-"),
           "- v1 거래일 %d일 (%s 부터)" % (len(v1days), spec.V1_SCORING_START)]
    if len(v1days) < spec.R3_KILL_AFTER_DAYS:
        out.append("- 판정: **대기** — %d/%d 거래일" % (len(v1days), spec.R3_KILL_AFTER_DAYS))
    elif n and tot < spec.R3_KILL_NET_MAX and (win / float(n)) < spec.R3_KILL_WINRATE_MAX:
        out.append("- 판정: **R3 중단** (순손익 < %d 그리고 승률 < %.0f%%) — v1 은 SHADOW_V1 로 기록만 계속한다"
                   % (spec.R3_KILL_NET_MAX, 100 * spec.R3_KILL_WINRATE_MAX))
    else:
        out.append("- 판정: **R3 유지** (중단 조건 미충족)")
    out.append("- 이 판정은 v1 사전등록 창의 기록이다 — MAIN 이 v2 로 바뀐 것과 무관하게 남긴다.")
    return out


def _late_judge(live, days, variant):
    """같은 거래일 집합에서 MAIN vs 섀도 — 순손익 **그리고** 최악일 둘 다 나아야 「채택 후보」."""
    out = []
    start = spec.LATE_SHADOW_START[variant]
    xdays = sorted({d["trade_date"] for d in days
                    if d["variant"] == variant and d["trade_date"] >= start})
    if not xdays:
        return ["- 기록 없음 — 채점 시작 %s 이후 %s 판정 행이 없다(미측정 ≠ 0)" % (start, variant)]

    def by_day(v):
        m = {d: 0.0 for d in xdays}
        for t in live:
            if t["variant"] == v and t["trade_date"] in m and t["status"] == "CLOSED":
                m[t["trade_date"]] += float(t.get("net_krw") or 0)
        return m
    mm, xx = by_day("MAIN"), by_day(variant)
    out.append("| 변형 | 거래일 | 순손익(원) | 최악일(원) |")
    out.append("|---|---|---|---|")
    for v, m in (("MAIN", mm), (variant, xx)):
        out.append("| %s | %d | %s | %s |" % (v, len(m), _fmt(sum(m.values())), _fmt(min(m.values()))))
    if len(xdays) < spec.JUDGE_AFTER_DAYS:
        out.append("- 판정: **대기** — %d/%d 거래일" % (len(xdays), spec.JUDGE_AFTER_DAYS))
    else:
        ok = sum(xx.values()) > sum(mm.values()) and min(xx.values()) > min(mm.values())
        out.append("- 판정: **%s** (기준: 순손익 우위 **그리고** 최악일 개선)" % (
            "채택 후보 — 새 SPEC_VERSION 개정 뒤 재채점" if ok else "폐기"))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=spec.SCORING_START)
    ap.add_argument("--db", default=SHINDONG_DB)
    ap.add_argument("--raw-db", dest="raw_db", default=RAW_DATA_DB)
    ap.add_argument("--levels-db", dest="levels_db", default=PREMARKET_LEVELS_DB)
    ap.add_argument("--flow-db", dest="flow_db", default=None)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    txt = build(a.db, a.since, a.raw_db, a.levels_db, a.flow_db)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(txt + "\n")
        print("저장: %s" % a.out)
    else:
        print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())

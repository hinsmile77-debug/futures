# -*- coding: utf-8 -*-
"""[MW0602 640차] 신동2 AI 의 「상대의 수」 — 신동 v3 MAIN · 섀도 5종을 읽고, AI 와 같은 단위로 나란히 세운다.

사용자 정의(2026-10-20): 신동2 AI 의 최고의 경쟁자는 신동 v3 MAIN 과 그 섀도다. MAIN·섀도의 행위는 「상대의 수」로 읽는다 —
따라 할 신호가 아니라 *오늘 상대가 어디서 들어가 어디서 나갔고 어디서 틀렸나* 다. 이 모듈은 그 상대를 읽는 유일한 통로이며
사다리(`tools/maekjeom_ladder/ladder_data.py`)·snapshot(`scripts/shindong2_live.py`)·학습(`scripts/shindong2_learn.py`)이 공유한다.

원천: `data/db/shindong.db` — `main.py` 가 매분 `strategy.shindong.runner.run_and_store` 로 쓴다(라이브). 여기서는 **읽기만** 한다.
단위: **pt/계약 · 수수료 포함**. 신동은 2계약 일괄(`spec.LEGS`)이라 `net_krw ÷ PT_VALUE_KRW ÷ LEGS`.
AI 는 1계약 pt 에 수수료가 없으므로(`simulate_ai`) 비교 때 왕복 비용 `AI_RT_COST_PT` 를 AI 쪽에서 뺀다 — 사전등록 §2.
사전등록: `docs/맥점x옵션사다리개선/02_사전등록_AI대MAIN_판정_MW0602-20261020.md` (값은 아래 PREREG 한 곳).

🔴 456차 — 장중에도 하루치 PK 조회 두 개뿐이다(`trade_date=?`). 전수 스캔 없음.
🔴 미측정 ≠ 0 — DB 가 없거나 그날 행이 없으면 `present=False` 와 사유를 돌려준다. 0 으로 채우지 않는다.
"""
from __future__ import annotations

import datetime as _dt
import os
import sqlite3
import sys
from typing import Any, Dict, List, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from strategy.shindong import spec as S  # noqa: E402  (상수만 — config 를 끌어오지 않는다)

SD_DB = os.environ.get("SHINDONG2_SD_DB") or os.path.join(ROOT, "data", "db", "shindong.db")
PT_DIV = float(S.PT_VALUE_KRW * S.LEGS)          # 원 → pt/계약 (2계약 일괄)
AI_RT_COST_PT = 0.20                             # 사전등록 §2 — AI 1거래 왕복 비용(수수료 ≈ 0.17 + 슬리피지 2틱 0.04 → 둥근 값)
PREREG = dict(
    version="SD2AI-2026-10-20-v1",
    scoring_start="2026-10-21",     # 첫 창 시작(배포 다음 거래일). 그 이전은 「개시 전 참고」
    window=20,                      # 거래일
    min_days=15,                    # 창 안 AI·MAIN 둘 다 측정된 날 최소
    copy_agree=0.80,                # 동의율 > 이 값 → INVALID_COPY
    copy_min_n=10,                  # 동의율을 판정에 쓰는 최소 n
    disagree_min=5,                 # 반대일 코호트 최소 n
    divergence_pt=1.0,              # 「갈린 섀도」 = |섀도 − MAIN| ≥ 이 값
)
REASON = {"TP1": "1차", "TP2": "최종", "SL": "손절", "BE": "본전", "TIME": "시간", "TR": "트레일"}
VARIANTS = tuple(S.VARIANTS)
SHORT = {v: v.replace("SHADOW_", "") for v in VARIANTS}
# [640차 이식] 규격 자동 감지 — dev(MW0602) = 신동 v3 「계열」(families · SHADOW_META · MAIN_FAMILY),
#   v9-dev(MW0601) = 신동 v2 R1/R2/R3 엔진(engine.run_day · 섀도 E2F2·X4NF·TR44·X4NFA). 같은 파일이 두 브랜치에서 돈다.
RULESET = "family" if hasattr(S, "SHADOW_META") and hasattr(S, "MAIN_FAMILY") else "v1"
LABEL = {"MAIN": ("MAIN(v3 %s)" % S.MAIN_FAMILY.upper()) if RULESET == "family" else ("MAIN(%s R1/R2/R3)" % S.SPEC_VERSION)}
LABEL.update({k: m["label"] for k, m in getattr(S, "SHADOW_META", ())})
SIDE_KO = {1: "매수", -1: "매도"}


def to_pt(net_krw: Optional[float]) -> Optional[float]:
    return None if net_krw is None else round(float(net_krw) / PT_DIV, 2)


def _ro(path: str) -> sqlite3.Connection:
    con = sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True, timeout=5.0)
    con.row_factory = sqlite3.Row
    return con


def _hm(ts: Optional[str]) -> Optional[str]:
    return str(ts)[11:16] if ts else None


def _trade(r: Dict[str, Any], last_close: Optional[float]) -> Dict[str, Any]:
    side = int(r["side"])
    legs = [(r.get("leg1_exit_ts"), r.get("leg1_exit_px"), r.get("leg1_reason")),
            (r.get("leg2_exit_ts"), r.get("leg2_exit_px"), r.get("leg2_reason"))]
    closed = [g for g in legs if g[0]]
    exit_t = max((g[0] for g in closed), default=None)
    exit_px = None
    if closed:
        last = [g for g in closed if g[0] == exit_t]
        exit_px = last[-1][1]
    reasons = [g[2] for g in closed if g[2]]
    t = dict(rule=r["rule"], side=side, side_ko=SIDE_KO.get(side, "?"), entry_t=_hm(r["entry_ts"]), entry_px=r["entry_px"],
             stop_init=r.get("stop_init"), stop_now=r.get("stop_now"), t1=r.get("t1"), t2=r.get("t2"),
             status=r["status"], exit_t=_hm(exit_t), exit_px=exit_px, reasons=reasons,
             reason_ko="/".join(REASON.get(x, x) for x in reasons) if reasons else None,
             net_pt=to_pt(r.get("net_krw")) if r["status"] == "CLOSED" else None, eval_pt=None,
             detected_at=_hm(r.get("detected_at")), detect_px=r.get("detect_px"), key=r["trade_key"])
    if r["status"] == "OPEN" and last_close is not None:
        t["eval_pt"] = round((float(last_close) - float(r["entry_px"])) * side, 2)   # 수수료 없는 평가값
    return t


def read_day(day: str, db: Optional[str] = None, last_close: Optional[float] = None,
             live: bool = False) -> Dict[str, Any]:
    """그날 변형별 거래·손익·방향. DB/행이 없으면 present=False(미측정)."""
    db = db or SD_DB
    out: Dict[str, Any] = dict(date=day, db=db, live=live, present=False, why=None, variants={}, divergent=[],
                               prereg=PREREG, unit="pt/계약 · 수수료 포함")
    if not os.path.exists(db):
        out["why"] = "shindong.db 없음 — 미륵이 미실행이거나 경로 다름(미측정 ≠ 0)"
        return out
    try:
        con = _ro(db)
        try:
            trows = [dict(r) for r in con.execute(
                "SELECT * FROM shindong_trades WHERE trade_date=? AND status!='RETRACTED' ORDER BY variant, entry_ts", (day,))]
            drows = {r["variant"]: dict(r) for r in con.execute("SELECT * FROM shindong_day WHERE trade_date=?", (day,))}
        finally:
            con.close()
    except sqlite3.Error as e:
        out["why"] = "shindong.db 읽기 실패: %s" % e
        return out
    if not trows and not drows:
        out["why"] = "이 날 신동 기록 없음(미실행·휴장·수집 전)"
        return out
    out["present"] = True
    for v in VARIANTS:
        ts = [_trade(r, last_close) for r in trows if r["variant"] == v]
        d = drows.get(v)
        closed = [t for t in ts if t["net_pt"] is not None]
        op = [t for t in ts if t["status"] == "OPEN"]
        vd = dict(variant=v, short=SHORT[v], label=LABEL.get(v, v), present=bool(ts or d), trades=ts, n=len(ts),
                  n_closed=len(closed), pnl_pt=round(sum(t["net_pt"] for t in closed), 2) if closed else (0.0 if d else None),
                  worst_trade_pt=min((t["net_pt"] for t in closed), default=None),
                  open=op[0] if op else None,
                  first_side=ts[0]["side_ko"] if ts else None, last_side=ts[-1]["side_ko"] if ts else None,
                  bias=(d or {}).get("bias"), pm_sp=(d or {}).get("pm_sp"), notes=(d or {}).get("notes"),
                  horizon=(d or {}).get("horizon"), spec_version=(d or {}).get("spec_version"),
                  updated_at=(d or {}).get("updated_at"))
        out["variants"][v] = vd
    m = out["variants"]["MAIN"]
    out["main"] = m
    if m["pnl_pt"] is not None:
        for v in VARIANTS[1:]:
            sv = out["variants"][v]
            if sv["pnl_pt"] is not None and abs(sv["pnl_pt"] - m["pnl_pt"]) >= PREREG["divergence_pt"]:
                out["divergent"].append(dict(short=sv["short"], pnl_pt=sv["pnl_pt"], diff=round(sv["pnl_pt"] - m["pnl_pt"], 2),
                                             first_side=sv["first_side"], n=sv["n"]))
    return out


def direction_of(vd: Optional[Dict[str, Any]]) -> Optional[str]:
    """변형의 그날 방향 = 첫 거래 방향. 거래 없음 → None(관망이지 0 이 아니다)."""
    return (vd or {}).get("first_side")


def ai_cost_pt(ai_sim: Optional[Dict[str, Any]]) -> Optional[float]:
    """AI 재량 실현에서 왕복 비용을 뺀 값(사전등록 §2). 시뮬이 없으면 None. 거래 0 → 0.0(참여하지 않은 것도 선택이다)."""
    if not ai_sim:
        return None
    closed = [t for t in ai_sim.get("trades", []) if not t.get("open")]
    return round(float(ai_sim.get("pnl") or 0.0) - AI_RT_COST_PT * len(closed), 2)


def agreement(ai_dir: Optional[str], main_dir: Optional[str]) -> Optional[str]:
    """기계 동의 판정 — 둘 다 방향이 있을 때만. 한쪽이라도 관망이면 None(미측정)."""
    if ai_dir in ("매수", "매도") and main_dir in ("매수", "매도"):
        return "agree" if ai_dir == main_dir else "disagree"
    return None


def judge_window(rows: List[Dict[str, Any]], prereg: Optional[Dict[str, Any]] = None,
                 window: Optional[int] = None, since: Optional[str] = None) -> Dict[str, Any]:
    """사전등록 §3~§5 판정. rows: 날짜순 [{date, ai_pt, main_pt, ai_dir, main_dir, vs_main, vs_src}].

    반환: verdict ∈ BEATS | TRAILS | INVALID_COPY | UNMEASURED, 창 집계, 동의율, 반대일 코호트.
    """
    P = dict(PREREG, **(prereg or {}))
    w = window or P["window"]
    since = P["scoring_start"] if since is None else since
    sub = [r for r in rows if (not since or r["date"] >= since)][-w:]
    both = [r for r in sub if r.get("ai_pt") is not None and r.get("main_pt") is not None]
    out: Dict[str, Any] = dict(version=P["version"], window=w, since=since or None, n_rows=len(sub), n_both=len(both),
                               first=sub[0]["date"] if sub else None, last=sub[-1]["date"] if sub else None,
                               ai_net=None, main_net=None, ai_worst=None, main_worst=None, diff=None,
                               agree_rate=None, n_dir=0, verdict="UNMEASURED", why="",
                               cohort=dict(n=0, wins=0, win_rate=None, sum_diff=None, verdict="UNMEASURED"))
    if both:
        out["ai_net"] = round(sum(r["ai_pt"] for r in both), 2)
        out["main_net"] = round(sum(r["main_pt"] for r in both), 2)
        out["ai_worst"] = round(min(r["ai_pt"] for r in both), 2)
        out["main_worst"] = round(min(r["main_pt"] for r in both), 2)
        out["diff"] = round(out["ai_net"] - out["main_net"], 2)
    # 동의율 — 기록값(vs_main) 우선, 없으면 기계 계산
    dirs = []
    for r in both:
        vm = r.get("vs_main")
        if vm == "abstain":                      # 기권은 기록값이다 — 기계 판정으로 대체하지 않고 분모에서 뺀다(§5)
            continue
        if vm not in ("agree", "disagree"):
            vm = agreement(r.get("ai_dir"), r.get("main_dir"))
        if vm:
            dirs.append((r, vm))
    out["n_dir"] = len(dirs)
    if dirs:
        out["agree_rate"] = round(sum(1 for _, vm in dirs if vm == "agree") / len(dirs), 2)
    dis = [r for r, vm in dirs if vm == "disagree"]
    c = out["cohort"]
    c["n"] = len(dis)
    if dis:
        c["wins"] = sum(1 for r in dis if r["ai_pt"] > r["main_pt"])
        c["win_rate"] = round(c["wins"] / len(dis), 2)
        c["sum_diff"] = round(sum(r["ai_pt"] - r["main_pt"] for r in dis), 2)
        if len(dis) >= P["disagree_min"]:
            c["verdict"] = "AI_WINS" if c["sum_diff"] > 0 and c["win_rate"] >= 0.5 else "MAIN_WINS"
        else:
            c["verdict"] = "UNMEASURED"
    if len(both) < P["min_days"]:
        out["why"] = "둘 다 측정된 날 %d < %d — 판정 보류(미측정)" % (len(both), P["min_days"])
        return out
    if out["n_dir"] >= P["copy_min_n"] and out["agree_rate"] is not None and out["agree_rate"] > P["copy_agree"]:
        out["verdict"] = "INVALID_COPY"
        out["why"] = "동의율 %.0f%% > %.0f%% — AI 가 MAIN 의 복사본이다. 능가 판정 무효" % (out["agree_rate"] * 100, P["copy_agree"] * 100)
        return out
    beats = out["ai_net"] > out["main_net"] and out["ai_worst"] > out["main_worst"]
    out["verdict"] = "BEATS" if beats else "TRAILS"
    out["why"] = "AI %+.2f vs MAIN %+.2f (최악일 %+.2f vs %+.2f)" % (out["ai_net"], out["main_net"], out["ai_worst"], out["main_worst"])
    if beats and c["verdict"] != "AI_WINS":
        out["why"] += " — ⚠ 반대일 코호트가 AI 우위를 뒷받침하지 않는다(동의일 덕일 수 있다)"
    return out


VERDICT_KO = {"BEATS": "능가", "TRAILS": "미달", "INVALID_COPY": "무효(복사본)", "UNMEASURED": "미측정",
              "AI_WINS": "AI 우위", "MAIN_WINS": "MAIN 우위"}


# ── ②단계: 상대가 지금 무엇을 보고 있나 — 신호원 값 ────────────────────────
def _db_paths():
    db = os.path.join(ROOT, "data", "db")
    return dict(raw=os.path.join(db, "raw_data.db"), flow=os.path.join(db, "option_flow.db"),
                levels=os.path.join(db, "premarket_levels.db"))


def signal_from_frame(d, upto: Optional[str] = None, L=None) -> Dict[str, Any]:
    """DayFrame 에서 MAIN·섀도의 신호원 값을 읽는다(미래 참조 없음 — upto 이하 분만).

    FLOWC   : 개인 위클리 콜−풋(백만원) 09:00 대비 변화 dv. dv ≥ +K → 매도 / dv ≤ −K → 매수 (역추종, K=FLOWC_K)
    FLOWR60 : 최근 60분 변화. 같은 부호 규약, K=FLOWR_K. 첫 신호 10:00
    FX60    : 외국인 선물 순매수 누적 최근 60분 변화(계약) — HYBL 의 FX 축(K=LEAD_K_FX, 순추종)
    HYBL    : 가격이 따라가는 지표(CP/FX) — families._lead_signal
    R1      : 08:59 콜−풋 편향(BRKC 의 방향일 판정)
    v1 규격(MW0601 v9)이면 `signal_from_frame_v1` 로 넘긴다 — L(맥점)이 필요하다.
    """
    if RULESET != "family":
        return signal_from_frame_v1(d, L, upto)
    from strategy.shindong import families as F
    keys = [k for k in d.idx if k in d.c and (upto is None or k <= upto)]
    out: Dict[str, Any] = dict(upto=keys[-1] if keys else None, present=bool(keys))
    if not keys:
        out["why"] = "봉 없음"
        return out
    k = keys[-1]
    sp = d.sp.get(k)
    out["cp_now"] = None if sp is None else round(sp, 1)
    # FLOWC — 09:00 기준점(없으면 그 이후 첫 값)
    base_k = S.FLOW_BASE if S.FLOW_BASE in d.sp else next((x for x in sorted(d.sp) if x > S.FLOW_BASE), None)
    if base_k is not None and sp is not None and base_k <= k:
        dv = sp - d.sp[base_k]
        out["flowc"] = dict(base_t=base_k, dv=round(dv, 1), k=S.FLOWC_K, side=("매도" if dv >= S.FLOWC_K else "매수" if dv <= -S.FLOWC_K else None),
                            dist=round(S.FLOWC_K - abs(dv), 1))
    else:
        out["flowc"] = None
    # FLOWR60 — 최근 60분
    rk = F._minus_min(k, S.FLOWR_WIN_MIN)
    if rk >= S.FLOW_BASE and d.sp.get(rk) is not None and sp is not None:
        dv = sp - d.sp[rk]
        out["flowr60"] = dict(from_t=rk, dv=round(dv, 1), k=S.FLOWR_K, side=("매도" if dv >= S.FLOWR_K else "매수" if dv <= -S.FLOWR_K else None),
                              dist=round(S.FLOWR_K - abs(dv), 1))
    else:
        out["flowr60"] = None
    # FX60 — 외국인 선물 최근 60분
    if d.fx and rk >= S.FLOW_BASE and d.fx.get(rk) is not None and d.fx.get(k) is not None:
        dv = d.fx[k] - d.fx[rk]
        kf = S.LEAD_K_FX
        out["fx60"] = dict(from_t=rk, dv=round(dv, 0), k=round(kf, 0), side=("매수" if dv >= kf else "매도" if dv <= -kf else None))
    else:
        out["fx60"] = None
    # HYBL 주도 지표
    try:
        lsig, lst = F._lead_signal(d)
        side = lsig(k)
        out["lead"] = dict(side=SIDE_KO.get(side) if side else None, lead=lst.get("lead"))
    except Exception as e:
        out["lead"] = dict(side=None, lead=None, why=str(e)[:80])
    pm_sp, bias = F._r1_bias(d)
    out["r1"] = dict(pm_sp=None if pm_sp is None else round(pm_sp, 1), bias=bias, side=SIDE_KO.get(bias) if bias else None)
    return out


def signal_from_frame_v1(d, L, upto: Optional[str] = None) -> Dict[str, Any]:
    """[640차 이식] v1 규격(MW0601 v9 MAIN = R1/R2/R3) — 상대가 지금 보는 것. `engine.run_day` 와 같은 식·같은 상수.

    R1 : 08:59 개인 위클리 콜−풋 → |값| ≥ BIAS_MIN 이면 편향(콜 우위 → 하방 = 매도)
    R2 : 편향일, 09:01–09:10 에 09:00 대비 (콜 Δ, 풋 Δ, 콜−풋 Δ ≥ CONF_MIN) 가 편향 방향으로 확인되면 개장 진입
    R3 : 09:30–14:30, 구조맥점 터치(이쪽 TOUCH_NEAR · 건너편 TOUCH_FAR) 뒤 REV_WIN_MIN 분 안 콜−풋 반전 ≥ REV_MIN 이면 반전 진입
    """
    from strategy.shindong import engine as E
    keys = [k for k in d.idx if k in d.c and (upto is None or k <= upto)]
    out: Dict[str, Any] = dict(ruleset="v1", upto=keys[-1] if keys else None, present=bool(keys))
    if not keys:
        out["why"] = "봉 없음"
        return out
    k = keys[-1]
    sp = d.sp.get(k)
    out["cp_now"] = None if sp is None else round(sp, 1)
    pm = [x for x in d.idx if x <= S.PREMARKET_LAST and x in d.sp]
    pm_sp = d.sp[pm[-1]] if pm else None
    bias = 0 if pm_sp is None or abs(pm_sp) < S.BIAS_MIN else (-1 if pm_sp > 0 else 1)
    out["r1"] = dict(pm_sp=None if pm_sp is None else round(pm_sp, 1), bias=bias, side=SIDE_KO.get(bias) if bias else None,
                     k=S.BIAS_MIN)
    r2 = dict(status=None, ts=None, ds=None, need=S.CONF_MIN)
    if L is None:
        r2["status"] = "맥점 없음"
    elif bias:
        dec = E.run_day(d, L, "MAIN")["decision"]
        r2.update(status=dec.get("r2"), ts=dec.get("r2_ts"))
        if S.CONF_BASE in d.sp and sp is not None:
            r2["ds"] = round(sp - d.sp[S.CONF_BASE], 1)
    else:
        r2["status"] = "편향 없음(R2 없음)"
    out["r2"] = r2
    r3 = dict(active=k >= S.R3_START and k <= S.NEW_ENTRY_END, above=None, below=None, rev_min=S.REV_MIN,
              band=(S.TOUCH_NEAR, S.TOUCH_FAR))
    if L is not None:
        _, lv = E.levels_at(L, k)
        px = d.c[k]
        up = sorted(x for x in lv if x > px)
        dn = sorted((x for x in lv if x < px), reverse=True)
        r3["above"] = round(up[0], 2) if up else None
        r3["below"] = round(dn[0], 2) if dn else None
    out["r3"] = r3
    return out



def signal_state(day: str, upto: Optional[str] = None) -> Dict[str, Any]:
    """그날 신호원 값(장중이면 upto=완결 봉). 원천을 못 읽으면 present=False + 사유. 456차 — 하루치 조회만(runner 와 같은 경로)."""
    try:
        from strategy.shindong import runner, engine
        from strategy.shindong.calendar import select_flow_product
        P = _db_paths()
        product, _exp, note = select_flow_product(_dt.date.fromisoformat(day))
        candles, flow, lvrows = runner.load_inputs(day, product, P["raw"], P["flow"], P["levels"])
        fx = runner.load_fx(day, P["raw"]) if hasattr(runner, "load_fx") else {}     # v9 runner 에는 load_fx 가 없다
        if not candles:
            return dict(present=False, why="봉 없음", product=product)
        try:
            d = engine.DayFrame(candles, flow, horizon=upto, fx=fx)
        except TypeError:                                                              # v9 DayFrame 은 fx 인자가 없다
            d = engine.DayFrame(candles, flow, horizon=upto)
        L = engine.prepare_levels(lvrows) if lvrows and "0850" in lvrows else None
        out = signal_from_frame(d, upto, L=L)
        out.update(product=product, product_note=note, flow_n=len(flow), fx_n=len(fx))
        return out
    except Exception as e:
        return dict(present=False, why="신호원 읽기 실패: %s" % e)


def signal_lines(sg: Optional[Dict[str, Any]]) -> List[str]:
    """snapshot 용 — 상대가 지금 무엇을 보고 있고 다음에 무엇을 하려는가."""
    if not sg:
        return []
    if not sg.get("present"):
        return ["상대의 눈(신호원): 미측정 — %s" % sg.get("why")]
    if sg.get("ruleset") == "v1":
        return _signal_lines_v1(sg)
    L = ["상대의 눈(신호원, ~%s · 위클리 %s):" % (sg.get("upto"), sg.get("product"))]
    fc = sg.get("flowc")
    if fc:
        L.append("  · 개인 위클리 콜−풋 %s백만 · %s 대비 %+.0f (FLOWC K=%d → %s%s)" % (
            sg.get("cp_now"), fc["base_t"], fc["dv"], fc["k"], fc["side"] or "신호 없음", "" if fc["side"] else " · 문턱까지 %.0f" % fc["dist"]))
    else:
        L.append("  · 개인 위클리 콜−풋: 09:00 기준점 없음(미측정)")
    fr = sg.get("flowr60")
    if fr:
        L.append("  · 최근 60분 변화 %+.0f (FLOWR60 K=%d → %s%s)" % (fr["dv"], fr["k"], fr["side"] or "신호 없음", "" if fr["side"] else " · 문턱까지 %.0f" % fr["dist"]))
    else:
        L.append("  · 최근 60분 변화: 아직 10:00 전(미측정)")
    fx = sg.get("fx60")
    if fx:
        L.append("  · 외인 선물 최근 60분 %+.0f계약 (HYBL FX축 K=%.0f → %s)" % (fx["dv"], fx["k"], fx["side"] or "신호 없음"))
    ld = sg.get("lead") or {}
    L.append("  · HYBL 주도 지표: %s%s" % (ld.get("lead") or "없음(상관 < 0.3)", (" → " + ld["side"]) if ld.get("side") else ""))
    r1 = sg.get("r1") or {}
    L.append("  · R1(08:59 콜−풋 %s): %s" % (r1.get("pm_sp"), r1.get("side") or "보류"))
    L.append("  ※ MAIN 의 첫 거래는 FLOWC, 2·3번째는 FLOWR60. 손절 난 방향은 당일 재진입 금지. 신호는 종가로 확정 → 다음 봉부터 청산 검사.")
    return L


def _fp(x: Optional[float]) -> str:
    return "—" if x is None else "%+.2f" % x


def summary_lines(r: Dict[str, Any]) -> List[str]:
    """snapshot 용 「상대의 수」 요약. 변형별 한 줄 + MAIN 거래 상세."""
    L = ["### 상대의 수 — 신동 v3 MAIN · 섀도 (%s)" % r.get("unit", "pt/계약")]
    if not r.get("present"):
        L.append("미측정 — %s" % (r.get("why") or "기록 없음"))
        return L
    for v in VARIANTS:
        vd = r["variants"][v]
        if not vd["present"]:
            L.append("- %s: 미측정(이 날 행 없음)" % vd["short"])
            continue
        op = vd["open"]
        st = ("보유 %s @%.2f 평가 %s · 손절 %s" % (op["side_ko"], op["entry_px"], _fp(op["eval_pt"]),
                                                op["stop_now"] if op["stop_now"] is not None else "—")) if op else "무포지션"
        L.append("- %s: %s · 거래 %d · 당일 %s · %s" % (vd["short"], vd["first_side"] or "관망", vd["n"], _fp(vd["pnl_pt"]), st))
    m = r["main"]
    for t in m["trades"]:
        L.append("  MAIN %s %s %s @%.2f → %s %s %s" % (t["rule"], t["entry_t"], t["side_ko"], t["entry_px"],
                                                      t["exit_t"] or "보유", t["reason_ko"] or "평가", _fp(t["net_pt"] if t["net_pt"] is not None else t["eval_pt"])))
    if r.get("divergent"):
        L.append("갈린 섀도(|차| ≥ %.1fpt): " % PREREG["divergence_pt"] +
                 " · ".join("%s %s(%s)" % (d["short"], _fp(d["pnl_pt"]), _fp(d["diff"])) for d in r["divergent"]))
    nt = m.get("notes")
    if nt:
        L.append("MAIN 메모: " + str(nt)[:200])
    return L


def _signal_lines_v1(sg: Dict[str, Any]) -> List[str]:
    """v1 규격(MW0601 v9) 의 「상대의 눈」."""
    L = ["상대의 눈(신호원, ~%s · 위클리 %s · 규격 R1/R2/R3):" % (sg.get("upto"), sg.get("product"))]
    r1 = sg.get("r1") or {}
    L.append("  · R1 08:59 개인 위클리 콜−풋 %s백만 (|값| ≥ %d → %s)" % (r1.get("pm_sp"), r1.get("k", 0), r1.get("side") or "편향 없음 — 오늘 R2 없음"))
    r2 = sg.get("r2") or {}
    L.append("  · R2 개장 확정: %s%s%s" % (r2.get("status") or "—", (" " + r2["ts"]) if r2.get("ts") else "",
                                      (" · 09:00 대비 콜−풋 %+.0f (문턱 %d)" % (r2["ds"], r2["need"])) if r2.get("ds") is not None else ""))
    r3 = sg.get("r3") or {}
    L.append("  · R3 맥점 반전(%s): 위 구조맥점 %s · 아래 %s · 터치 폭 이쪽 %.1f/건너편 %.1f · 반전 문턱 콜−풋 %d" % (
        "작동 시간" if r3.get("active") else "09:30–14:30 밖", r3.get("above"), r3.get("below"),
        (r3.get("band") or (0, 0))[0], (r3.get("band") or (0, 0))[1], r3.get("rev_min") or 0))
    L.append("  ※ MAIN 은 2계약 — 1차 목표에서 절반, 나머지는 최종 목표·손절·15:05. 신호는 종가로 확정 → 다음 봉부터 청산 검사.")
    return L

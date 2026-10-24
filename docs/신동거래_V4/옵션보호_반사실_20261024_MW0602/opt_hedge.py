# -*- coding: utf-8 -*-
"""옵션 보호(매수 → 풋 · 매도 → 콜) 반사실 — V4 21일 재생 위. 읽기 전용(DB 미기록).

V4 재생 = sim6.run({"stopx": ("mkt", "stop")}) (v4_compare 와 동일). 레그(계약)마다 진입 분에 보호옵션 1개를
사고, 그 레그가 청산되는 분에 판다. 미니선물 1계약(5만/pt)에 대응하는 것은 미니옵션 1계약(5만/pt)이다.

옵션 시세 원천이 DB 에 없다(option_book 감마는 행사가 무관 상수라 IV 역산 불가) → 모형가:
  Black-76(r=0) · 기초 = 그 분의 선물가 · IV = 그 분의 VKOSPI(0·결측은 직전값) × 스큐 배수
  잔존기간 = 영업시간 기준(장중 405분 = 1영업일, /252) — 장중 세타를 최대로 잡는 보수 가정
  비용 = 매수·매도 각 반호가(half) + 수수료 0.15%(프리미엄 대금, 가정)

보호 구성(K = 재난손절가 = 진입가 ∓ 0.6×ATR14, 2.5pt 격자 반올림)
  M_K    월물(미니) · K=재난손절
  M_K2   월물(미니) · K=재난손절 ∓ 0.3×ATR (더 먼 외가)
  M_SP   월물(미니) · 풋(콜) 스프레드: K 매수 · K ∓ 0.6×ATR 매도
  W_K    위클리(정규, 승수 25만 = 미니 5계약분) · K=재난손절 — 1~2계약 규모에서는 **집행 불가**, 계약당 환산 참고치
"""
import os, sys, io, json, math, sqlite3, contextlib, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.isdir(os.path.join(ROOT, "strategy")):
    ROOT = os.path.dirname(ROOT)
DD = os.path.join(HERE, "..", "수익최대화_딥다이브_20261023_MW0602")
sys.path.insert(0, ROOT); sys.path.insert(0, DD)
os.chdir(ROOT)
import sim6                                                   # noqa: E402
from strategy.shindong import engine as E, spec as S          # noqa: E402

PTV = 50_000
OPT_COMM = 0.0015

# ── 레그 캡처: sim6.make_pos 를 감싸 반환 포지션을 기록 ─────────────
CAP = []
_orig_mp = sim6.make_pos


def _wrap_mp(d, cfg, day):
    f = _orig_mp(d, cfg, day)

    def pos(dd, side, t0, stop, trail, tp):
        p = f(dd, side, t0, stop, trail, tp)
        if p.get("legs") and p.get("status") == "CLOSED" and p["legs"][0].get("ts"):
            CAP.append(dict(day=day, atr=cfg["_atr"], p=p))
        return p
    return pos


sim6.make_pos = _wrap_mp
v4 = sim6.run({"stopx": ("mkt", "stop")})
sim6.make_pos = _orig_mp
# run_family_day 는 포지션을 여러 번 평가할 수 있다 → 실제 채택된 거래(v4)와 진입시각·방향으로 맞춘다
adopted = {(d, t["t"], t["side"]) for d in v4 for t in v4[d]}
seen, trades = set(), []
for x in CAP:
    p = x["p"]; key = (x["day"], p["entry_ts"], p["side"])
    if key in adopted and key not in seen and p["legs"][0]["ts"] != p["entry_ts"]:
        seen.add(key); trades.append(x)
skipped = [k for k in adopted if k not in seen]

# ── 입력: VKOSPI · 분봉 ────────────────────────────────────────────
rc = sqlite3.connect("file:data/db/raw_data.db?mode=ro", uri=True)
VK = {}
for ts, v in rc.execute("select ts, json_extract(features,'$.vkospi') from raw_features "
                        "where ts>='2026-09-21' and ts<'2026-10-24' order by ts"):
    VK.setdefault(ts[:10], {})[ts[11:16]] = v


def vk_at(day, hm):
    m = VK.get(day, {})
    ks = [k for k in sorted(m) if k <= hm and m[k]]
    if ks:
        return m[ks[-1]] / 100.0
    ks = [k for k in sorted(m) if m[k]]
    return m[ks[0]] / 100.0


TRADING = sorted({d for d in VK})


def is_td(d):
    s = d.isoformat()
    if TRADING[0] <= s <= TRADING[-1]:
        return s in TRADING
    return d.weekday() < 5


def second_thu(y, m):
    d = dt.date(y, m, 1)
    d += dt.timedelta(days=(3 - d.weekday()) % 7)
    return d + dt.timedelta(days=7)


def monthly_exp(day):
    d = dt.date.fromisoformat(day)
    y, m = d.year, d.month
    for _ in range(3):
        e = second_thu(y, m)
        while not is_td(e):
            e -= dt.timedelta(days=1)
        if (e - d).days >= 3:          # 만기 3일 미만이면 다음 월물로 롤
            return e
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def weekly_exp(day):
    d = dt.date.fromisoformat(day) + dt.timedelta(days=1)
    while not (d.weekday() in (0, 3) and is_td(d)):
        d += dt.timedelta(days=1)
    return d


def t_years(day, hm, exp):
    """영업시간 기준 잔존(년). 장 09:00~15:45 = 405분 = 1영업일, 만기일은 15:20 까지."""
    d0 = dt.date.fromisoformat(day)
    mins_today = max(0, (15 * 60 + 45) - (int(hm[:2]) * 60 + int(hm[3:])))
    days = 0.0
    d = d0 + dt.timedelta(days=1)
    while d < exp:
        if is_td(d):
            days += 1
        d += dt.timedelta(days=1)
    last = (15 * 60 + 20 - 9 * 60) / 405.0
    return (mins_today / 405.0 + days + (last if exp > d0 else 0)) / 252.0


def N(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def b76(F, K, s, T, cp):
    if T <= 0 or s <= 0:
        return max(0.0, (F - K) if cp == "C" else (K - F))
    sd = s * math.sqrt(T)
    d1 = (math.log(F / K) + 0.5 * sd * sd) / sd
    d2 = d1 - sd
    return F * N(d1) - K * N(d2) if cp == "C" else K * N(-d2) - F * N(-d1)


def delta(F, K, s, T, cp):
    sd = s * math.sqrt(T); d1 = (math.log(F / K) + 0.5 * sd * sd) / sd
    return N(d1) if cp == "C" else N(d1) - 1


def grid(x):
    return round(x / 2.5) * 2.5


# ── 구성 · 시나리오 ────────────────────────────────────────────────
def legs_for(cfg, side, e, atr):
    cat = e - side * 0.6 * atr
    cp = "P" if side > 0 else "C"
    if cfg == "M_K":
        return [(cp, grid(cat), +1)]
    if cfg == "M_K2":
        return [(cp, grid(cat - side * 0.3 * atr), +1)]
    if cfg == "M_SP":
        return [(cp, grid(cat), +1), (cp, grid(cat - side * 0.6 * atr), -1)]
    if cfg == "W_K":
        return [(cp, grid(cat), +1)]


SKEW = {"base": {"P": 1.00, "C": 0.95}, "low": {"P": 0.90, "C": 0.85}, "high": {"P": 1.15, "C": 1.05}}
HALF = {"M": 0.15, "W": 0.05}          # 반호가(pt) 기본값 — 미니월물은 얇다, 위클리 정규는 두껍다


def opt_value(cfg, legs, F, day, hm, exp, skew):
    v = 0.0
    T = t_years(day, hm, exp)
    s0 = vk_at(day, hm)
    for cp, K, q in legs:
        v += q * b76(F, K, s0 * SKEW[skew][cp], T, cp)
    return v


def hedge_trade(x, cfg, skew="base", half=None, hold_to=None):
    """한 거래(2레그) — 레그별 옵션 손익(pt/계약) 리스트."""
    p, day, atr = x["p"], x["day"], x["atr"]
    side, e, t0 = p["side"], p["entry_px"], p["entry_ts"]
    exp = weekly_exp(day) if cfg.startswith("W") else monthly_exp(day)
    h = HALF["W" if cfg.startswith("W") else "M"] if half is None else half
    legs = legs_for(cfg, side, e, atr)
    nlegs = len(legs)
    D, _ = sim6.sim4.sim.frame(day)
    out = []
    for lg in p["legs"]:
        tx = hold_to or lg["ts"]
        tx = D.last_at_or_before(tx)
        Fx = lg["px"] if hold_to is None else D.c[tx]
        v0 = opt_value(cfg, legs, e, day, t0, exp, skew)
        v1 = opt_value(cfg, legs, Fx, day, tx, exp, skew)
        gross0 = sum(abs(q) * b76(e, K, vk_at(day, t0) * SKEW[skew][cp], t_years(day, t0, exp), cp) for cp, K, q in legs)
        gross1 = sum(abs(q) * b76(Fx, K, vk_at(day, tx) * SKEW[skew][cp], t_years(day, tx, exp), cp) for cp, K, q in legs)
        cost = 2 * h * nlegs + OPT_COMM * (gross0 + gross1)
        out.append(dict(v0=v0, v1=v1, pnl=v1 - v0 - cost, cost=cost, T0=t_years(day, t0, exp) * 252,
                        fut=side * (Fx - e), K=legs[0][1], exp=exp.isoformat(),
                        d0=sum(q * delta(e, K, vk_at(day, t0) * SKEW[skew][cp], t_years(day, t0, exp), cp) for cp, K, q in legs)))
    return out


def worst_mark(x, cfg, skew="base"):
    """동결 시나리오: 진입 뒤 15:05 까지 손대지 못함 — 분별 평가손의 최악(선물 단독 vs 선물+옵션), pt/계약."""
    p, day, atr = x["p"], x["day"], x["atr"]
    side, e, t0 = p["side"], p["entry_px"], p["entry_ts"]
    exp = weekly_exp(day) if cfg.startswith("W") else monthly_exp(day)
    legs = legs_for(cfg, side, e, atr)
    D, _ = sim6.sim4.sim.frame(day)
    v0 = opt_value(cfg, legs, e, day, t0, exp, skew)
    wf = wh = 0.0; wt = None
    for k in D.idx:
        if not (t0 < k <= S.TIME_EXIT) or k not in D.h:
            continue
        adv = D.l[k] if side > 0 else D.h[k]
        f = side * (adv - e)
        hdg = f + opt_value(cfg, legs, adv, day, k, exp, skew) - v0
        if f < wf:
            wf, wt = f, k
        wh = min(wh, hdg)
    tx = D.last_at_or_before(S.TIME_EXIT)
    end_f = side * (D.c[tx] - e)
    end_h = end_f + opt_value(cfg, legs, D.c[tx], day, tx, exp, skew) - v0
    return dict(wf=wf, wh=wh, wt=wt, end_f=end_f, end_h=end_h)


def fmt(x):
    return "%+.2f" % x


lines = []
P = lines.append
CFGS = ("M_K", "M_K2", "M_SP", "W_K")
LAB = {"M_K": "월물 K=재난손절", "M_K2": "월물 K=재난손절∓0.3ATR", "M_SP": "월물 스프레드 K / K∓0.6ATR", "W_K": "위클리 K=재난손절(참고·집행불가)"}

fut_tot = sum(t["pt"] for d in v4 for t in v4[d])
n_tr = sum(len(v4[d]) for d in v4)
P("# 옵션 보호 반사실 — V4 21일 (%s ~ %s)" % (min(v4), max(v4)))
P("V4 거래 %d건 · 캡처 %d건 · 미캡처 %d건 · V4 합계 %+.1f pt/계약 (2계약 %+.1f만)" % (n_tr, len(trades), len(skipped), fut_tot, fut_tot * 2 * PTV / 1e4))
cap_tot = sum(sum(E.leg_net(t["p"]["side"], t["p"]["entry_px"], lg["px"], lg["mkt"])[1] for lg in t["p"]["legs"]) / 2 / PTV for t in trades)
P("캡처 거래 선물 순손익 합 %+.1f pt/계약 (V4 합계와 대조)" % cap_tot)

# 1) 정상 운영 비용 — 구성별
P("\n## 1. 정상 운영(재난손절 정상 집행) — 옵션 손익 합 (pt/계약, 2레그 평균)")
P("| 구성 | 옵션 손익 합 | 그중 집행비용(호가·수수료) | 진입 프리미엄 중앙 | 진입 |델타| 중앙 | 잔존 영업일 중앙 | V4 대비 | 선물+옵션 합 | 이익일 |")
P("|---|---|---|---|---|---|---|---|---|")
RES = {}
for cfg in CFGS:
    rows = []
    for x in trades:
        hs = hedge_trade(x, cfg)
        net_f = sum(E.leg_net(x["p"]["side"], x["p"]["entry_px"], lg["px"], lg["mkt"])[1] for lg in x["p"]["legs"]) / 2 / PTV
        rows.append(dict(x=x, opt=sum(h["pnl"] for h in hs) / 2, cost=sum(h["cost"] for h in hs) / 2,
                         v0=hs[0]["v0"], d0=hs[0]["d0"], T0=hs[0]["T0"], K=hs[0]["K"], exp=hs[0]["exp"], fut=net_f))
    RES[cfg] = rows
    ot = sum(r["opt"] for r in rows); ct = sum(r["cost"] for r in rows)
    srt = lambda a: sorted(a)[len(a) // 2]
    byday = {}
    for r in rows:
        byday.setdefault(r["x"]["day"], 0.0); byday[r["x"]["day"]] += r["fut"] + r["opt"]
    P("| %s | %+.1f | −%.1f | %.2f | %+.2f | %.1f | %+.1f%% | %+.1f | %d/%d |" % (
        LAB[cfg], ot, ct, srt([r["v0"] for r in rows]), srt([abs(r["d0"]) for r in rows]), srt([r["T0"] for r in rows]),
        100 * ot / cap_tot, cap_tot + ot, sum(v > 0 for v in byday.values()), len(byday)))

# 1-b) 민감도
P("\n## 1-b. 민감도 — M_K 옵션 손익 합 (pt/계약)")
P("| 스큐 \\ 반호가 | 0.05 | 0.15 | 0.30 |")
P("|---|---|---|---|")
for sk in ("low", "base", "high"):
    vals = []
    for hf in (0.05, 0.15, 0.30):
        vals.append(sum(sum(h["pnl"] for h in hedge_trade(x, "M_K", sk, hf)) / 2 for x in trades))
    P("| %s | %s |" % (sk, " | ".join("%+.1f" % v for v in vals)))

# 1-c) 손익 분해: 델타 끌림 vs 시간가치·IV
P("\n## 1-c. M_K 옵션 손익 — 승자/패자 분리 (pt/계약)")
for lab, sel in (("선물 이익 거래", lambda r: r["fut"] > 0), ("선물 손실 거래", lambda r: r["fut"] <= 0)):
    rs = [r for r in RES["M_K"] if sel(r)]
    P("- %s %d건: 선물 %+.1f · 옵션 %+.1f (집행비용 −%.1f)" % (lab, len(rs), sum(r["fut"] for r in rs), sum(r["opt"] for r in rs), sum(r["cost"] for r in rs)))

# 2) 거래별 표 (M_K)
P("\n## 2. 거래별 — M_K (pt/계약)")
P("| 날짜 | 진입 | 방향 | 사유 | 진입가 | ATR | K | 만기 | 잔존(영업일) | IV | 프리미엄 | 델타 | 선물 순 | 옵션 | 합 |")
P("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in RES["M_K"]:
    x = r["x"]; p = x["p"]
    why = "/".join(sorted({lg["reason"] for lg in p["legs"]}))
    P("| %s | %s | %s | %s | %.2f | %.1f | %.1f | %s | %.1f | %.1f | %.2f | %+.2f | %+.2f | %+.2f | %+.2f |" % (
        x["day"][5:], p["entry_ts"], "매수" if p["side"] > 0 else "매도", why, p["entry_px"], x["atr"], r["K"], r["exp"][5:], r["T0"],
        vk_at(x["day"], p["entry_ts"]) * 100, r["v0"], r["d0"], r["fut"], r["opt"], r["fut"] + r["opt"]))

# 3) 동결 스트레스 — 진입 직후 동결, 15:05 까지 무청산
P("\n## 3. 동결 스트레스 — 진입 직후 동결 · 15:05 까지 무청산 (pt/계약, 집행비용 제외 평가손)")
P("| 구성 | 최악 평가손(선물 단독) | 최악 평가손(보호) | 15:05 결과 최악(단독 → 보호) | 15:05 결과 합(단독 → 보호) | 평가손이 0.6ATR 넘은 거래 |")
P("|---|---|---|---|---|---|")
for cfg in ("M_K", "M_K2", "M_SP", "W_K"):
    ws = [(x, worst_mark(x, cfg)) for x in trades]
    over = [(x, w) for x, w in ws if -w["wf"] > 0.6 * x["atr"]]
    P("| %s | %.2f | %.2f | %.2f → %.2f | %+.1f → %+.1f | %d건 (단독 최악 %.1f → 보호 %.1f) |" % (
        LAB[cfg], min(w["wf"] for _, w in ws), min(w["wh"] for _, w in ws),
        min(w["end_f"] for _, w in ws), min(w["end_h"] for _, w in ws),
        sum(w["end_f"] for _, w in ws), sum(w["end_h"] for _, w in ws),
        len(over), min([w["wf"] for _, w in over] or [0]), min([w["wh"] for _, w in over] or [0])))
P("\n### 3-b. 평가손이 0.6×ATR 를 넘은 거래 (M_K)")
for x in trades:
    w = worst_mark(x, "M_K")
    if -w["wf"] > 0.6 * x["atr"]:
        p = x["p"]
        P("- %s %s %s ATR %.1f: 최악 %s(%.2f×ATR, %s) → 보호 %s · 15:05 %s → %s" % (
            x["day"][5:], p["entry_ts"], "매수" if p["side"] > 0 else "매도", x["atr"], fmt(w["wf"]), -w["wf"] / x["atr"], w["wt"],
            fmt(w["wh"]), fmt(w["end_f"]), fmt(w["end_h"])))

# 4) 같은 델타의 수량 축소와 비교
P("\n## 4. 같은 델타만큼 수량을 줄인 것과 비교 (pt/계약)")
P("옵션 보호의 선형 부분(델타)은 수량 축소와 같다. 남는 것(볼록성 − 시간가치 − 호가)만이 옵션 고유의 값이다.")
P("| 구성 | 정상 운영: 보호 합 | 정상 운영: 수량 (1−|δ|) 합 | 옵션 고유 손익 | 동결 최악: 보호 | 동결 최악: 수량 (1−|δ|) |")
P("|---|---|---|---|---|---|")
for cfg in CFGS:
    rows = RES[cfg]
    hed = sum(r["fut"] + r["opt"] for r in rows)
    cut = sum(r["fut"] * (1 - abs(r["d0"])) for r in rows)
    wm = [(r, worst_mark(r["x"], cfg)) for r in rows]
    P("| %s | %+.1f | %+.1f | %+.1f | %.2f | %.2f |" % (LAB[cfg], hed, cut, hed - cut,
      min(w["wh"] for _, w in wm), min(w["wf"] * (1 - abs(r["d0"])) for r, w in wm)))

json.dump({cfg: [dict(day=r["x"]["day"], t=r["x"]["p"]["entry_ts"], side=r["x"]["p"]["side"], fut=r["fut"], opt=r["opt"],
                      cost=r["cost"], v0=r["v0"], d0=r["d0"], K=r["K"], exp=r["exp"]) for r in RES[cfg]] for cfg in RES},
          open(os.path.join(HERE, "opt_hedge.json"), "w"), indent=1)
open(os.path.join(HERE, "out_opt_hedge.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))

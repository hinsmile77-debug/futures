"""[MW0601 2026-10-26] 신동2 메인·섀도 손익 × 갭·나스닥 연관분석 (읽기 전용, 장후 전용). py310_64.
결과: docs/미륵이고도화3/신동2/신동2_메인섀도_손익×갭·나스닥_연관분석_MW0601-20261026.md
"""
import sys, json, sqlite3, datetime as dt
sys.path.insert(0, r"C:\Users\82108\PycharmProjects\futures")
from utils.dll_bootstrap import ensure_conda_dll_path
ensure_conda_dll_path()
import numpy as np, pandas as pd
from scipy import stats

D = r"C:\Users\82108\PycharmProjects\futures\docs\미륵이고도화3\신동2\신동보완분석_MW0601-20261020\데이터"
SP = D + r"\웹원자료_yahoo_20261026"
KST = dt.timedelta(hours=9)

# ---------- 손익 ----------
a = json.load(open(D + r"\인과엔진_메인섀도_일별_22일.json", encoding="utf-8"))
b = json.load(open(D + r"\F2_F2X_전후_거래_22일.json", encoding="utf-8"))
days = a["days"]
pnl = pd.DataFrame(index=days)
pnl["재생MAIN"] = pd.Series(a["current_main"])
names = {"MAIN": "인과MAIN", "MAIN_F2": "F2(V2+F2)", "SHADOW_V2": "V2", "SHADOW_E2F2": "E2F2",
         "SHADOW_X4NF": "X4NF", "SHADOW_X4NFA": "X4NFA", "SHADOW_ATRS": "ATRS"}
for k, n in names.items():
    pnl[n] = pd.Series(a["causal"][k])
tr = b["trades"]
keyF2X = [k for k in tr if "F2X" in k][0]
def daysum(t): return pd.Series({d: sum(x["l1"] + x["l2"] for x in t.get(d, [])) / 1e4 for d in days})
pnl["F2X"] = daysum(tr[keyF2X])
pnl = pnl.astype(float)
pnl["Δ재생−인과"] = pnl["재생MAIN"] - pnl["인과MAIN"]
pnl["ΔF2−인과"] = pnl["F2(V2+F2)"] - pnl["인과MAIN"]
pnl["ΔF2X−인과"] = pnl["F2X"] - pnl["인과MAIN"]

# 방향별 손익(인과 MAIN·F2·F2X) — 갭 방향과 같은 쪽/반대쪽
keyC = [k for k in tr if k.startswith("인과")][0]
keyF2 = [k for k in tr if "SHADOW_F2" in k and "F2X" not in k][0]
side = {}
for lab, key in (("인과MAIN", keyC), ("F2", keyF2), ("F2X", keyF2X)):
    for d in days:
        for x in tr[key].get(d, []):
            side.setdefault((lab, d), {1: 0.0, -1: 0.0, "n1": 0, "n-1": 0})
            s = side[(lab, d)]
            s[x["side"]] += (x["l1"] + x["l2"]) / 1e4
            s["n%d" % x["side"]] += 1

# ---------- 미륵이 DB: 갭·장중 ----------
con = sqlite3.connect("file:" + r"C:\Users\82108\PycharmProjects\futures\data\db\regular_candles.db" + "?mode=ro", uri=True)
c = pd.read_sql("select ts,trade_date,open,high,low,close from regular_candles where code='10100' and trade_date>='2026-09-15'", con)
c["ts"] = pd.to_datetime(c.ts)
mk = {}
dl = sorted(c.trade_date.unique())
for i, d in enumerate(dl):
    if d not in days: continue
    g = c[c.trade_date == d].sort_values("ts"); p = c[c.trade_date == dl[i - 1]].sort_values("ts")
    pc = p.close.iloc[-1]; o = g.open.iloc[0]
    g9 = g[g.ts >= pd.Timestamp(d + " 09:00")]
    hi, lo, cl = g.high.max(), g.low.min(), g.close.iloc[-1]
    filled = (lo <= pc) if o > pc else (hi >= pc)
    mk[d] = dict(prev_close=pc, open=o, gap=o - pc, gap_pct=(o / pc - 1) * 100,
                 range_pt=hi - lo, range_pct=(hi - lo) / o * 100, oc=cl - o, oc_pct=(cl / o - 1) * 100,
                 trend=abs(cl - o) / (hi - lo), gap_filled=bool(filled),
                 first15=g[g.ts <= pd.Timestamp(d + " 09:00")].close.iloc[-1] - o,
                 prev_close_t=p.ts.iloc[-1])
mk = pd.DataFrame(mk).T

# ---------- 웹: 야후 ----------
def yh(fn):
    j = json.load(open(SP + "\\" + fn))["chart"]["result"][0]
    q = j["indicators"]["quote"][0]
    df = pd.DataFrame({"t": pd.to_datetime(j["timestamp"], unit="s") + KST, "o": q["open"], "h": q["high"], "l": q["low"], "c": q["close"]}).dropna()
    return df
nqh, esh, ewy = yh("h_NQ_F.json"), yh("h_ES_F.json"), yh("h_EWY.json")
ixic = yh("IXIC.json")
ixic["d"] = ixic.t.dt.date  # 일봉 타임스탬프는 미국 개장(KST 22:30)
ixic["ret"] = ixic.c.pct_change() * 100
ixic["rng"] = (ixic.h - ixic.l) / ixic.c.shift() * 100
ewyd = yh("h_EWY.json")

def window(df, t0, t1):
    w = df[(df.t > t0) & (df.t <= t1)]
    return w
rows = {}
for d in mk.index:
    t1 = pd.Timestamp(d + " 08:45"); t0 = mk.loc[d, "prev_close_t"] + pd.Timedelta(minutes=1)
    r = {}
    for lab, df in (("NQ", nqh), ("ES", esh)):
        w = window(df, t0, t1)
        base = df[df.t <= t0].c.iloc[-1]
        r[lab + "_on_pct"] = (w.c.iloc[-1] / base - 1) * 100
        r[lab + "_onrng_pct"] = (w.h.max() - w.l.min()) / base * 100
    # 나스닥 지수: KR 개장 직전에 끝난 미국 정규장
    prior = ixic[ixic.t < t1].iloc[-1]
    r["IXIC_ret"] = prior.ret; r["IXIC_rng"] = prior.rng; r["IXIC_date"] = str(prior.t.date())
    # EWY: 직전 KR 종가 이후 미국 정규장 수익(야간 한국 프록시)
    w = window(ewy, t0, t1)
    base = ewy[ewy.t <= t0].c.iloc[-1]
    r["EWY_on_pct"] = (w.c.iloc[-1] / base - 1) * 100 if len(w) else np.nan
    rows[d] = r
ext = pd.DataFrame(rows).T
X = pd.concat([mk, ext], axis=1)
num = ["gap_pct", "range_pct", "oc_pct", "trend", "NQ_on_pct", "NQ_onrng_pct", "ES_on_pct", "IXIC_ret", "IXIC_rng", "EWY_on_pct"]
for k in num: X[k] = X[k].astype(float)
X["abs_gap"] = X.gap_pct.abs(); X["abs_NQ"] = X.NQ_on_pct.abs(); X["abs_IXIC"] = X.IXIC_ret.abs()

# ---------- 상관 ----------
targets = ["재생MAIN", "인과MAIN", "F2(V2+F2)", "F2X", "V2", "E2F2", "X4NF", "X4NFA", "ATRS", "Δ재생−인과", "ΔF2−인과", "ΔF2X−인과"]
feats = ["gap_pct", "abs_gap", "NQ_on_pct", "abs_NQ", "NQ_onrng_pct", "IXIC_ret", "abs_IXIC", "IXIC_rng", "EWY_on_pct", "range_pct", "trend"]
M = X.join(pnl)
M = M[M.index != "2026-10-13"]  # 거래 0건일 제외
out = []
for t in targets:
    row = {"var": t}
    for f in feats:
        rho, p = stats.spearmanr(M[f].astype(float), M[t].astype(float))
        row[f] = "%+.2f%s" % (rho, "**" if p < 0.01 else ("*" if p < 0.05 else ""))
    out.append(row)
corr = pd.DataFrame(out).set_index("var")

# 갭 버킷
def bucket(g):
    if g >= 0.5: return "갭상승≥+0.5%"
    if g <= -0.5: return "갭하락≤−0.5%"
    return "보합 |갭|<0.5%"
M["gapb"] = M.gap_pct.apply(bucket)
bk = M.groupby("gapb")[targets[:9]].agg(["mean", "count"])

# 갭 방향 일치 거래 손익
al = []
for d in M.index:
    sg = np.sign(M.loc[d, "gap_pct"])
    for lab in ("인과MAIN", "F2", "F2X"):
        s = side.get((lab, d))
        if not s or not sg: continue
        al.append(dict(d=d, lab=lab, with_gap=s[int(sg)] if sg else np.nan, against=s[-int(sg)] if sg else np.nan,
                       n_with=s["n%d" % int(sg)], n_ag=s["n%d" % -int(sg)]))
al = pd.DataFrame(al)
alS = al.groupby("lab")[["with_gap", "against", "n_with", "n_ag"]].sum()

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
print(X[["prev_close", "open", "gap", "gap_pct", "gap_filled", "first15", "range_pct", "oc_pct", "trend", "NQ_on_pct", "NQ_onrng_pct", "ES_on_pct", "IXIC_date", "IXIC_ret", "IXIC_rng", "EWY_on_pct"]].round(2).to_string())
print(pnl.round(1).to_string())
print(corr.to_string())
print(bk.round(1).to_string())
print(alS.round(1).to_string())
print(al[al.d == "2026-10-26"].round(1).to_string())
# 갭 ↔ 나스닥 야간
for f in ("NQ_on_pct", "ES_on_pct", "IXIC_ret", "EWY_on_pct"):
    print(f, "vs gap_pct spearman %.2f pearson %.2f" % (stats.spearmanr(X[f], X.gap_pct)[0], stats.pearsonr(X[f], X.gap_pct)[0]))
X.join(pnl).to_csv(D + "\갭·나스닥_일별결합_22일.csv", encoding="utf-8-sig")
for lab in ("인과MAIN", "F2", "F2X"):
    for d in ["2026-10-26"]:
        pass

# ===== 추가: NQ 구간 분해 + 당일 KR 방향 =====
print("\n=== IXIC 일봉 타임스탬프 샘플 ===")
print(ixic[["t","c","ret"]].tail(6).to_string())
seg = {}
for i, d in enumerate(mk.index):
    pd_ = dl[dl.index(d) - 1]
    k0 = pd.Timestamp(pd_ + " 09:00"); k1 = mk.loc[d, "prev_close_t"] + pd.Timedelta(minutes=1)
    t1 = pd.Timestamp(d + " 08:45")
    def px(t): return nqh[nqh.t <= t].c.iloc[-1]
    # 미국 정규장 종가 시각 = t1 직전 05:00/06:00 KST 근처 — NQ 1h에서 05:00 KST 이전 마지막
    us_close = pd.Timestamp(d + " 06:00") if True else None
    seg[d] = dict(NQ_krsess=(px(k1)/px(k0)-1)*100, NQ_eve_to_usclose=(px(us_close)/px(k1)-1)*100,
                  NQ_usclose_to_open=(px(t1)/px(us_close)-1)*100)
seg = pd.DataFrame(seg).T.astype(float)
M2 = M.join(seg)
M2["prev_oc"] = [mk.oc_pct.get(dl[dl.index(d)-1], np.nan) if dl[dl.index(d)-1] in mk.index else np.nan for d in M2.index]
for f in ["NQ_krsess","NQ_eve_to_usclose","NQ_usclose_to_open","IXIC_ret","oc_pct","prev_oc"]:
    s = []
    for t in ["재생MAIN","인과MAIN","F2(V2+F2)","F2X","ΔF2−인과","ΔF2X−인과"]:
        r, p = stats.spearmanr(M2[f], M2[t], nan_policy="omit"); s.append("%s %+.2f(p%.3f)" % (t, r, p))
    print(f, " | ".join(s))
print("IXIC_ret vs oc_pct", stats.spearmanr(M2.IXIC_ret, M2.oc_pct))
print("IXIC_ret vs range_pct", stats.spearmanr(M2.IXIC_ret, M2.range_pct))
# 순열 검정 (인과MAIN ~ IXIC_ret)
rng = np.random.default_rng(0); obs = stats.spearmanr(M2.IXIC_ret, M2["인과MAIN"])[0]
perm = [stats.spearmanr(rng.permutation(M2.IXIC_ret.values), M2["인과MAIN"])[0] for _ in range(20000)]
print("perm p", np.mean(np.abs(perm) >= abs(obs)))
# 나스닥 부호 버킷
M2["nqb"] = np.where(M2.IXIC_ret >= 0.5, "나스닥≥+0.5%", np.where(M2.IXIC_ret <= -0.5, "나스닥≤−0.5%", "나스닥 보합"))
print(M2.groupby("nqb")[["재생MAIN","인과MAIN","F2(V2+F2)","F2X","V2","ATRS","oc_pct","range_pct"]].agg(["mean","count"]).round(1).to_string())
# 갭 방향 일치 거래 — 버킷별
al2 = al.merge(M2[["gapb"]], left_on="d", right_index=True)
print(al2.groupby(["lab","gapb"])[["with_gap","against","n_with","n_ag"]].sum().round(1).to_string())
print(M2[["gap_pct","IXIC_ret","NQ_on_pct","oc_pct","NQ_krsess","NQ_eve_to_usclose","NQ_usclose_to_open"]].round(2).to_string())

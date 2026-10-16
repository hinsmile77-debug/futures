"""[MW0601 2026-10-02] 나스닥 선물(키움 영웅문Global 1분봉) ↔ 미니 KOSPI200 1분봉 리드-래그·괴리 탐색 (읽기 전용).

입력 디렉터리 <dir>:
  nq/*.csv  — scripts/nasdaq_leadlag_xls2csv.py 로 변환한 키움 차트 내보내기(일자,시간,시,고,저,종,…).
              키움 시각 = 봉 시작 → +1분 해 봉 종료로 맞춘다(교차상관 피크 L=0 으로 실측 확인).
  mnq.csv   — 추가 내보내기(선택, 없으면 이 줄을 지울 것)
  k200_all.csv — CpSysDib.FutOptChart 1분봉(date,time,…,close; 시각 = 봉 종료)
사용(py310_64): python scripts/nasdaq_leadlag_probe.py <dir>
근거·결과: docs/미륵이고도화3/나스닥선물_1분봉_수집방안_및_Cybos거울상_검토_MW0601-20261002.md §8
"""
import sys, glob, os
sys.path.insert(0, r"C:\Users\82108\PycharmProjects\futures")
from utils.dll_bootstrap import ensure_conda_dll_path
ensure_conda_dll_path()
import numpy as np, pandas as pd
S = sys.argv[1]
def load_nq(p):
    n = pd.read_csv(p, encoding="utf-8").iloc[:, :6]; n.columns = ["d", "t", "o", "h", "l", "c"]
    n = n[pd.to_numeric(n.c, errors="coerce").notna()].copy(); n["c"] = n.c.astype(float)
    n["ts"] = pd.to_datetime(n.d + " " + n.t) + pd.Timedelta(minutes=1)   # 봉 시작 → 봉 종료
    n["src"] = os.path.basename(p); return n[["ts", "c", "src"]]
parts = [load_nq(p) for p in sorted(glob.glob(S + r"\nq\*.csv"))] + [load_nq(S + r"\mnq.csv")]
allnq = pd.concat(parts)
# 같은 시각이 여러 파일에 있으면 값이 일치하는지(내보내기 정합성) 확인
g = allnq.groupby("ts").c.agg(["min", "max", "count"]); multi = g[g["count"] > 1]
print("NQ 중복시각 %d개, 그중 값 불일치 %d개 (최대차 %.2f)" % (len(multi), (multi["max"] - multi["min"] > 0).sum(), (multi["max"] - multi["min"]).max() if len(multi) else 0))
N = allnq.groupby("ts").c.first().sort_index()
k = pd.read_csv(S + r"\k200_all.csv")
k["ts"] = pd.to_datetime(k.date.astype(str) + k.time.astype(str).str.zfill(4), format="%Y%m%d%H%M")
K = k.set_index("ts").close.sort_index()
df = pd.concat({"n": N, "k": K}, axis=1)
tt = df.index.time
df = df[(tt >= pd.Timestamp("09:01").time()) & (tt <= pd.Timestamp("15:20").time())].copy()
df["day"] = df.index.date
df = df.dropna(subset=["k"])
# 1분 수익률 — 직전 분이 연속 존재할 때만
def r1(s):
    return np.log(s).groupby(df.day).diff()
df["rn"], df["rk"] = r1(df.n), r1(df.k)
both = df.dropna(subset=["rn", "rk"])
print("\n[커버리지] 일자별 겹치는 1분 수익률 수")
cov = both.groupby("day").size(); print(cov.to_string())
print("합계 %d (본장 전체 일: %s)" % (len(both), [str(d) for d, c in cov.items() if c > 300]))
def xc(d, L):
    x = d.groupby("day").rn.shift(L); m = pd.concat([x, d.rk], axis=1).dropna(); return m.corr().iloc[0, 1], len(m)
for label, d in (("전 구간", df), ("14:00–15:20 (13일 동일 창)", df[df.index.time >= pd.Timestamp("14:01").time()])):
    print("\n[1분 교차상관 — %s] L>0 = 나스닥 선행" % label)
    for L in range(-5, 6):
        r, n = xc(d, L); print("  L=%+d r=%+.3f n=%d ±2SE=%.3f" % (L, r, n, 2/np.sqrt(n)))
print("\n[일자별] L=0, L=+1, L=+2  /  1분 std NQ·K200(bp)  /  동시 β")
rows = []
for day, g in df.groupby("day"):
    m0 = g[["rn", "rk"]].dropna()
    if len(m0) < 30: continue
    out = []
    for L in (0, 1, 2):
        m = pd.concat([g.rn.shift(L), g.rk], axis=1).dropna(); out.append(m.corr().iloc[0, 1])
    b = np.polyfit(m0.rn, m0.rk, 1)[0]
    rows.append((day, len(m0), *out, m0.rn.std()*1e4, m0.rk.std()*1e4, b))
    print("  %s n=%3d  L0=%+.3f L1=%+.3f L2=%+.3f  std %.2f/%.2f  β=%.2f" % rows[-1])
R = pd.DataFrame(rows, columns=["day", "n", "L0", "L1", "L2", "sn", "sk", "beta"])
print("  L1>0인 날 %d/%d · L2>0인 날 %d/%d · L0 범위 %.2f–%.2f" % ((R.L1 > 0).sum(), len(R), (R.L2 > 0).sum(), len(R), R.L0.min(), R.L0.max()))
beta = np.polyfit(both.rn, both.rk, 1)[0]
print("\n[누적 시계 · 비중첩] β(전체)=%.2f" % beta)
print("  h   n  NQ과거→K200미래   괴리→K200미래   K200자기되돌림   OLS: 미래~자기과거+괴리 (괴리 t)   괴리<0인 날")
for h in (1, 3, 5, 10, 15):
    rows = []
    for day, g in df.groupby("day"):
        g = g.dropna(subset=["n", "k"])
        # 연속 분만 쓰기 위해 시각 간격 검사
        idx = g.index; ln, lk = np.log(g.n.values), np.log(g.k.values)
        for i in range(h, len(g) - h, h):
            if (idx[i] - idx[i-h]) != pd.Timedelta(minutes=h) or (idx[i+h] - idx[i]) != pd.Timedelta(minutes=h): continue
            pn, pk, fk = ln[i]-ln[i-h], lk[i]-lk[i-h], lk[i+h]-lk[i]
            rows.append((day, pn, pk, pk - beta*pn, fk))
    a = pd.DataFrame(rows, columns=["day", "pn", "pk", "e", "fk"])
    c = lambda x: np.corrcoef(a[x], a.fk)[0, 1]
    X = np.column_stack([np.ones(len(a)), a.pk, a.e]); y = a.fk.values
    coef, *_ = np.linalg.lstsq(X, y, rcond=None); res = y - X @ coef
    s2 = res @ res / (len(y) - 3); se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    perday = a.groupby("day")[["e", "fk"]].apply(lambda g: np.corrcoef(g.e, g.fk)[0, 1] if len(g) > 5 else np.nan).dropna()
    print("  %2d %4d   %+.3f            %+.3f           %+.3f            t=%+.2f                 %d/%d" % (h, len(a), c("pn"), c("e"), c("pk"), coef[2]/se[2], (perday < 0).sum(), len(perday)))

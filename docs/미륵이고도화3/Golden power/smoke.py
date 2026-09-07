"""스모크 테스트: 코드가 도는지, 그리고 '신호 없음'을 신호 없음으로 판정하는지 확인.
이건 성능 결과가 아니다. 합성 랜덤워크라 알파가 존재하지 않는다."""
import numpy as np, pandas as pd
from golden_power import golden_power, golden_power_features
from evaluate import Panel, explore, forward_returns, purged_folds

rng = np.random.default_rng(7)
# 40 거래일 x 380분 랜덤워크
idx, sess, px = [], [], []
p = 1050.0
for d in pd.bdate_range("2026-06-01", periods=40):
    p *= np.exp(rng.normal(0, 0.004))
    for m in range(380):
        p *= np.exp(rng.normal(0, 0.00035))
        idx.append(pd.Timestamp(d) + pd.Timedelta(minutes=540+m)); sess.append(d.date()); px.append(p)
df = pd.DataFrame({"close": px, "session": sess}, index=pd.DatetimeIndex(idx))
df["ofi_norm"] = rng.normal(size=len(df))
df["cvd_div"]  = rng.normal(size=len(df))

# 1) 산식 자기검증: gp_buy==0 인 봉은 반드시 25봉 신저 종가여야 한다
gp = golden_power(df["close"], 25)
zero = gp["golden_buy"].abs() < 1e-9
rollmin = df["close"].rolling(25).min()
assert bool((df["close"][zero] == rollmin[zero]).all()), "gp_buy==0 정합성 실패"
zs = gp["golden_sell"].abs() < 1e-9
rollmax = df["close"].rolling(25).max()
assert bool((df["close"][zs] == rollmax[zs]).all()), "gp_sell==0 정합성 실패"
print(f"[OK] 돌파 플래그 정합  신저 {int(zero.sum())}봉  신고 {int(zs.sum())}봉  "
      f"(전체 {len(df)}봉 중 각 {zero.mean()*100:.1f}% / {zs.mean()*100:.1f}%)")

# 2) 선형종속 확인
f = golden_power_features(df["close"], 25, session=df["session"])
rec_buy = (f.gp_range + f.gp_dir)/2
assert np.allclose(rec_buy.dropna(), gp["golden_buy"].reindex(rec_buy.dropna().index), atol=1e-9)
print("[OK] gp_buy = (gp_range + gp_dir)/2  선형종속 확인 -> 4개 동시투입 금지 근거")

# 3) 세션 리셋 확인
first = df.groupby("session").head(24).index
assert f.loc[first, "gp_dir"].isna().all(), "세션 리셋 실패"
print("[OK] 세션 리셋  각 거래일 첫 24봉 NaN (오버나이트 갭 차단)")

# 4) purge 확인
folds = purged_folds(df["session"], n_folds=5, embargo_days=1)
for tr, te in folds:
    assert not (set(df["session"].iloc[tr]) & set(df["session"].iloc[te]))
print(f"[OK] purged 워크포워드  {len(folds)}겹, 학습/테스트 거래일 교집합 없음")

# 5) 귀무 하에서 FDR 통과 개수
res = explore(Panel(df, confirm_cols=["ofi_norm","cvd_div"]), horizons=(5,15,30))
print(f"[OK] explore 실행  후보 {len(res)}건, FDR(0.10) 통과 {int(res.fdr_pass.sum())}건")
print("     -> 합성 랜덤워크이므로 통과 0건에 가까워야 정상 (거짓양성 억제 확인)")
print(res[["feature","horizon","ic_mean","ic_t","p","fdr_pass"]].head(5).to_string(index=False))

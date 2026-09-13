# -*- coding: utf-8 -*-
"""[MW0601 559차 / P0-2] 수급 피처 로그압축 **역변환 가드**.

무엇을 막는가
-------------
`raw_features` 의 수급 8키는 `features/feature_builder.py:856-882`(124차, 2026-06-08)
에서 **부호보존 log1p 압축**돼 저장된다.

    stored = sign(raw) * log1p(|raw| / 1000)

분석 스크립트는 이걸 되돌려 계약수로 읽는다.

    raw ~= sign(v) * expm1(|v|) * 1000

그런데 **압축 이전 단위로 저장된 4거래일**(2026-06-02 · 06-04 · 06-05 · 06-08)이
DB 에 남아 있다. 418차 사고 복구 때 압축 도입 이전 백업
(`raw_data.db.bak_20260608_151648`)에서 되살린 행들이다. 거기에 역변환을 걸면:

  · 클립이 있는 구현(`np.clip(|v|, 0, 30)`) → `expm1(30) * 1000 = 1.0686e+16` **포화 상수**
  · 클립이 없는 구현                          → `inf`

🔴 **이 값을 「센티널」이라 부르지 말 것.** DB 안에 그런 값은 **0건**이다
(`raw_features` · `raw_features_horizon` · `raw_program_trade` · `predictions.db`
전 JSON 컬럼에서 `|v| > 1e12` 스캔 결과 0). 저건 **단위 불일치 + 클립**이 만든
분석측 산물이다.

왜 크기 임계만으로는 못 거르는가
--------------------------------
2026-06-08 은 331행 중 `|v| >= 30` 이 **70행뿐**이다. 나머지는 「12계약」처럼 작은
원단위 값이라 압축값과 크기로 구분되지 않는다. 그래서 **1차 규칙은 날짜**다.

  · `ts < INVESTOR_LOG1P_EPOCH` 이고 supported 인 행 → 단위 미상 → NaN
  · 그 뒤 구간에서 `|v| >= UNIT_MISMATCH_ABS` → 안전망(라이브 최대가 2.6 수준이라
    30 은 도달 불가한 값이다)

계측 4원칙 ③ — 제외한 행 수와 사유를 **반드시 남긴다**. 조용히 지우면
「수급이 원래 그 날 없었다」로 오독된다.
"""
from __future__ import print_function

import numpy as np

# ── 사전등록 상수 ────────────────────────────────────────────────────────────
INVESTOR_LOG1P_EPOCH = "2026-06-09"   # 이 날부터 전 행이 압축 단위(첫 완전 압축일)
UNIT_MISMATCH_ABS = 30.0              # 안전망. 라이브 실측 최대 |v| ~= 2.6
_EXPM1_SATURATION = float(np.expm1(30.0) * 1000.0)   # 1.0686e+16 — 이 값이 나오면 버그다

INVESTOR_LOG1P_KEYS = (
    "foreign_futures_net", "retail_futures_net", "institution_futures_net",
    "foreign_call_net", "foreign_put_net",
    "program_arb_net", "program_non_arb_net", "foreign_retail_divergence",
)


def invert_investor_log1p(values, supported=None, dates=None, name="", verbose=True):
    """압축된 수급값을 계약수로 되돌린다. 단위 불일치 행은 NaN 으로 빼고 개수를 남긴다.

    Args:
        values:    저장값(압축 단위) 1차원 배열/시리즈.
        supported: `quality_investor_supported`(또는 `_futures_supported`). 1 이 아닌
                   행은 애초에 미측정이라 NaN. None 이면 전부 측정된 것으로 본다.
        dates:     각 행의 날짜 문자열('YYYY-MM-DD' 로 시작하면 된다). None 이면
                   날짜 규칙을 건너뛰고 크기 안전망만 적용한다.
        name:      로그에 찍을 컬럼명.
        verbose:   제외 집계를 출력할지.

    Returns:
        np.ndarray(float) — 역변환 결과. 제외된 자리는 NaN.
    """
    v = np.asarray(values, dtype=float)
    keep = np.isfinite(v)

    n_unsup = 0
    if supported is not None:
        sup = np.asarray(supported, dtype=float)
        bad = ~(sup == 1.0)
        n_unsup = int(np.sum(bad & keep))
        keep &= ~bad

    n_epoch = 0
    if dates is not None:
        ds = np.asarray([str(x)[:10] for x in dates])
        pre = ds < INVESTOR_LOG1P_EPOCH
        n_epoch = int(np.sum(pre & keep))
        keep &= ~pre

    with np.errstate(invalid="ignore"):
        over = keep & (np.abs(v) >= UNIT_MISMATCH_ABS)
    n_over = int(np.sum(over))
    keep &= ~over

    out = np.full(v.shape, np.nan, dtype=float)
    with np.errstate(over="ignore"):
        out[keep] = np.sign(v[keep]) * np.expm1(np.abs(v[keep])) * 1000.0
    out[~np.isfinite(out)] = np.nan

    if verbose:
        print("[inv_guard] %-28s 유효 %6d행 | 제외: 미측정 %5d · 압축이전(%s 이전) %4d"
              " · 크기>=%g %3d"
              % (name or "(unnamed)", int(np.sum(np.isfinite(out))), n_unsup,
                 INVESTOR_LOG1P_EPOCH, n_epoch, UNIT_MISMATCH_ABS, n_over))
        if n_epoch or n_over:
            print("            ↑ 418차 복구분(2026-06-02·04·05·08)은 압축 이전 **계약수 원단위**다."
                  " 역변환 대상이 아니다 — 「센티널」이 아니라 단위 불일치.")
    return out


def add_inverted_columns(df, keys=None, supported_col="quality_investor_supported",
                         suffix="_raw", date_index=True, verbose=True):
    """DataFrame 에 `<key>_raw` 열을 가드 적용해 붙인다.

    `date_index=True` 면 인덱스를 날짜 원천으로 쓴다(분봉 인덱스가 DatetimeIndex 인
    패널 스크립트용). 아니면 `ts` 열을 쓴다.
    """
    keys = [k for k in (keys or INVESTOR_LOG1P_KEYS) if k in df.columns]
    sup = df[supported_col] if supported_col in df.columns else None
    if date_index:
        dates = df.index.astype(str)
    else:
        dates = df["ts"].astype(str) if "ts" in df.columns else None
    for k in keys:
        df[k + suffix] = invert_investor_log1p(
            df[k].values, None if sup is None else sup.values,
            dates, name=k, verbose=verbose)
    return df

# -*- coding: utf-8 -*-
"""[MW0601 455차 / N3] 노이즈 벤치마크 피처 생성 — IC 스크리닝의 실용적 하한선.

원리(검토보고 §3-N3): 실제 피처와 통계적 성질이 유사한 가짜 피처를 같은 검정에 태워,
최종 랭킹에서 가짜보다 아래인 실피처는 후보 자격을 잃는다. 통계 이론 없이 작동하는
가장 실용적인 다중검정 방어선이다(basis_pt형 우연 유의 재발 방지).

두 유형:
  · shuffle  — 행 순서 무작위 재배열: 주변 분포는 완전 보존, 시계열 구조 파괴.
  · phase    — 위상 무작위화(FFT 진폭 보존·위상 셔플): 자기상관 구조까지 보존한
               "그럴듯한" 노이즈. 자기상관이 강한 피처의 우연 IC가 얼마나 나오는지 잰다.

규약:
  · **raw_features에 절대 쓰지 않는다** — 스크리닝 시점 메모리 생성만
    (수집 계층 오염 금지, feedback_no_schema_fallback_in_collection 취지).
  · 시드는 관찰창 마지막 날짜(YYYYMMDD 정수) — 같은 창이면 완전 재현.
  · 노이즈가 Bonferroni 유의로 뜨면 그 회차 스크리닝 전체를 의심할 것(자동 경보).
  · 하한선 규칙(사전등록): 노이즈 최고 |IC_t| 아래의 실피처는 ADD 후보 자격 상실 "제안"
    — 자동 조치 없음(§6 자동 통합 금지).

py37_32 호환, numpy 전용.
"""
from __future__ import print_function

from collections import OrderedDict

import numpy as np

DEFAULT_N_SHUFFLE = 3
DEFAULT_N_PHASE = 2


def shuffle_column(values, rng):
    """비-NaN 값들을 무작위 재배열 (NaN 위치는 보존)."""
    v = np.array(values, dtype=np.float64, copy=True)
    ok = ~np.isnan(v)
    vals = v[ok]
    rng.shuffle(vals)
    v[ok] = vals
    return v


def phase_randomize(values, rng):
    """위상 무작위화 — FFT 진폭 보존, 위상만 무작위 (NaN은 중앙값 대체 후 위치 복원)."""
    v = np.array(values, dtype=np.float64, copy=True)
    ok = ~np.isnan(v)
    if ok.sum() < 8:
        return shuffle_column(values, rng)  # 표본 미달 — 셔플 폴백
    med = float(np.median(v[ok]))
    filled = np.where(ok, v, med)
    spec = np.fft.rfft(filled - filled.mean())
    mag = np.abs(spec)
    phases = rng.uniform(0.0, 2.0 * np.pi, size=spec.shape)
    phases[0] = 0.0  # DC 성분 위상 고정
    if filled.size % 2 == 0:
        phases[-1] = 0.0  # Nyquist 성분 실수 유지
    synth = np.fft.irfft(mag * np.exp(1j * phases), n=filled.size) + filled.mean()
    out = np.full_like(v, np.nan)
    out[ok] = synth[ok]
    return out


def make_noise_features(cols, seed, n_shuffle=DEFAULT_N_SHUFFLE, n_phase=DEFAULT_N_PHASE):
    """노이즈 피처 dict 생성.

    Args:
        cols: OrderedDict/dict {실피처명: np.ndarray} — 템플릿(값 분포·자기상관의 원천).
        seed: int — 관찰창 마지막 날짜 YYYYMMDD 권장.
    Returns:
        OrderedDict {노이즈명: np.ndarray}. 이름에 템플릿 출처를 남긴다
        (noise_shuf1_ofi_norm 형식 — 어떤 실피처를 흉내냈는지 추적 가능).
    """
    rng = np.random.RandomState(int(seed) % (2 ** 31 - 1))
    names = [k for k, v in cols.items()
             if isinstance(v, np.ndarray) and np.isfinite(v).sum() >= 30]
    out = OrderedDict()
    if not names:
        return out
    for i in range(n_shuffle):
        src = names[i % len(names)]
        out["noise_shuf%d_%s" % (i + 1, src)] = shuffle_column(cols[src], rng)
    for i in range(n_phase):
        src = names[(i + n_shuffle) % len(names)]
        out["noise_phase%d_%s" % (i + 1, src)] = phase_randomize(cols[src], rng)
    return out


def is_noise_name(name):
    return str(name).startswith("noise_shuf") or str(name).startswith("noise_phase")


def noise_floor(rows, name_key="name", stat_key="ic_t"):
    """결과 행 목록에서 노이즈 하한선(max |stat|)과 그 이름을 반환. 없으면 (nan, None)."""
    best, best_name = float("nan"), None
    for r in rows:
        if not is_noise_name(r.get(name_key, "")):
            continue
        s = r.get(stat_key)
        if s is None:
            continue
        try:
            a = abs(float(s))
        except (TypeError, ValueError):
            continue
        if not np.isfinite(a):
            continue
        if best_name is None or a > best:
            best, best_name = a, r[name_key]
    return best, best_name

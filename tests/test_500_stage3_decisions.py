# -*- coding: utf-8 -*-
"""[MW0601 500차 3단계] 주간회의 결정 1·2·3 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
결정 1 — CVD 편향·시계 제거는 **섀도 우선**
────────────────────────────────────────────────────────────────────────────
`delta = buy_vol - sell_vol` 의 Cybos buy_vol 편향(98.6%)으로 누적 CVD 가
단조증가하고, 파생 정규화가 전부 붕괴한다(500-A). 교정은 두 축을 **함께** 고쳐야
한다 — 정규화만으로는 안 된다(98.6% 가 여전히 양수라 단조증가 유지):
  ① delta 를 당일 러닝 평균으로 중심화 (편향 제거, 미래참조 없음)
  ② slope 분모를 누적 max → 롤링 변동성 (시계 제거)
즉시 live 로 켜지 않는 이유: cvd_divergence 는 3m·15m, cvd_slope 는 5m 배포
pkl 에 있고(앙상블 가중 합 0.71) 그 모델들은 **구 분포로** 학습돼 있다.

결정 2 — "CORE" 정의가 세 곳에서 달랐다. 단일 출처로 통합한다.
결정 3 — 97 슈퍼셋은 컬럼을 **삭제하지 않는다**(shape mismatch). 등록만 한다.

  S1  debias 가 편향을 실제로 제거한다 (단조증가 입력에서 부호가 양쪽 다 나온다)
  S2  debias 가 시계를 제거한다 (구 경로는 시간에 따라 감쇠, 신 경로는 아니다)
  S3  워밍업 구간이 debias_measured=False 로 구분된다 (계측 4원칙 ②)
  S4  기본 모드가 shadow — 라이브 키가 바뀌지 않는다
  S5  CORE 정의 3곳이 같은 집합을 가리킨다                    ← 결정 2 핵심
  S6  폐기 예정 등록이 실측과 일치하고, 배포 중인 것은 in_gbm 으로 표시된다
  S7  `ofi_pressure` 는 폐기 목록에 없다 (CORE 실집행 키다)

실행: python tests/test_500_stage3_decisions.py   (COM/브로커·DB 불필요)
"""

import io
import os
import pickle
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

from utils.analysis_db import utf8_console  # noqa: E402

utf8_console()

from features.technical.cvd import CVDCalculator  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("OK" if cond else "FAIL", name,
                         ("\n         → %s" % detail) if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)
    return cond


# ══════════════════════════════════════════════════════════════
# S1~S4 — 결정 1 (debias 섀도)
# ══════════════════════════════════════════════════════════════
# 실제 편향을 재현한다: buy > sell 이 98.6% — 라이브와 같은 형태의 입력.
import random  # noqa: E402

random.seed(500)
cvd = CVDCalculator(window=10)
rows = []
price = 390.0
for i in range(120):
    biased = random.random() < 0.986          # 매수 우세가 98.6%
    buy = 100 + random.gauss(0, 8)
    sell = buy - abs(random.gauss(12, 5)) if biased else buy + abs(random.gauss(12, 5))
    price += random.gauss(0, 0.15)
    rows.append(cvd.update_from_bar(close=price, buy_vol=buy, sell_vol=max(sell, 1.0)))

live_slopes = [r["cvd_slope_norm"] for r in rows if r.get("measured")]
deb_slopes = [r["cvd_slope_debias"] for r in rows if r.get("debias_measured")]

check("S1a 구 경로는 편향 그대로 — cvd_slope_norm 음수 0건 (결함 재현)",
      sum(1 for x in live_slopes if x < 0) == 0,
      "재현 실패: 음수 %d건. 입력 편향 시나리오를 확인할 것"
      % sum(1 for x in live_slopes if x < 0))
_neg = sum(1 for x in deb_slopes if x < 0)
check("S1b debias 는 양방향이 나온다 (음수 %d/%d, 20~80%% 기대)"
      % (_neg, len(deb_slopes)),
      len(deb_slopes) > 20 and 0.20 <= _neg / float(len(deb_slopes)) <= 0.80,
      "중심화가 듣지 않으면 여기서 걸린다 — 편향이 남았다는 뜻")

# S2 — 시계(감쇠) 제거. 구 경로는 분모가 하루 종일 커져 |값| 이 단조감소한다.
def _decay(v):
    """전반부 평균 대비 후반부 평균 비율 — 1.0 이면 감쇠 없음."""
    h = len(v) // 2
    a = sum(abs(x) for x in v[:h]) / max(h, 1)
    b = sum(abs(x) for x in v[h:]) / max(len(v) - h, 1)
    return b / a if a > 1e-12 else float("nan")


d_live, d_deb = _decay(live_slopes), _decay(deb_slopes)
check("S2a 구 경로는 시간에 따라 감쇠한다 (후/전 = %.3f < 0.7, 결함 재현)"
      % d_live, d_live < 0.7)
check("S2b debias 는 감쇠하지 않는다 (후/전 = %.3f, 0.5~2.0 기대)" % d_deb,
      0.5 <= d_deb <= 2.0,
      "분모를 롤링 변동성으로 바꿨는데도 감쇠가 남으면 시계 성분이 안 빠진 것")

# S3 — 워밍업 구분
warm = [r for r in rows if not r.get("debias_measured")]
check("S3 워밍업 구간이 debias_measured=False 로 구분된다 (%d봉)" % len(warm),
      len(warm) > 0 and all(r["cvd_slope_debias"] == 0.0 for r in warm),
      "미측정과 '값이 0' 이 구분되지 않으면 계측 4원칙 ② 위반")

# S4 — 기본 shadow: 라이브 키가 debias 로 대체되지 않는다
from config.settings import CVD_DEBIAS_MODE  # noqa: E402

check("S4a 기본 모드가 shadow", str(CVD_DEBIAS_MODE).lower() == "shadow",
      "live 로 켜려면 사전등록 조건 ⓐ~ⓓ 를 먼저 충족할 것 (settings 주석)")
fb_src = io.open(os.path.join(ROOT, "features", "feature_builder.py"),
                 encoding="utf-8").read()
check("S4b 섀도 키가 raw_features 에 항상 기록된다",
      'features["cvd_slope_debias"]' in fb_src
      and 'features["cvd_debias_measured"]' in fb_src,
      "계산만 하고 기록하지 않으면 TOX 죽은 섀도(한 달 무배선)와 같은 상태가 된다")
check("S4c live 전환 시에도 섀도 키를 남긴다 (전환 전후 대조 보존)",
      '_CVD_DEBIAS_LIVE' in fb_src
      and fb_src.index('features["cvd_slope_debias"]')
          < fb_src.index("_CVD_DEBIAS_LIVE and"),
      "섀도 기록보다 덮어쓰기가 먼저면 전환 후 원값이 사라진다(461차 교훈)")

# ══════════════════════════════════════════════════════════════
# S5 — 결정 2 (CORE 정의 통합)
# ══════════════════════════════════════════════════════════════
from config.constants import CORE_FEATURES  # noqa: E402
from config.settings import CORE_FEATURES_BY_GROUP  # noqa: E402
from strategy.regime_fingerprint import _CORE_FEATURES as PSI_CORE  # noqa: E402

want = sorted(set(v for v in CORE_FEATURES_BY_GROUP["short"].values()
                  if isinstance(v, str)))
check("S5a constants.CORE_FEATURES == CORE_FEATURES_BY_GROUP['short'] (%s)"
      % want, sorted(CORE_FEATURES) == want,
      "실제: %s" % sorted(CORE_FEATURES))
check("S5b regime_fingerprint(PSI) 도 같은 집합을 쓴다",
      sorted(PSI_CORE) == want,
      "PSI 가 진입 판단에 안 쓰이는 피처의 분포를 재고 있다. 실제: %s"
      % sorted(PSI_CORE))
check("S5c cvd_divergence 가 CORE 에서 빠졌다",
      "cvd_divergence" not in CORE_FEATURES and "cvd_divergence" not in PSI_CORE,
      "부호가 -sign(price_slope_10m)(99.92%) 이고 크기가 시각 함수라 "
      "CORE 로서 재는 것이 이름과 다르다(500-B)")

# ══════════════════════════════════════════════════════════════
# S6·S7 — 결정 3 (97 슈퍼셋)
# ══════════════════════════════════════════════════════════════
from config.settings import FEATURE_SUPERSET_DEPRECATED as DEPR  # noqa: E402

sup_path = os.path.join(ROOT, "model", "horizons", "feature_names.pkl")
if os.path.exists(sup_path):
    with open(sup_path, "rb") as f:
        superset = set(pickle.load(f))
    missing = [n for n in DEPR if n not in superset]
    check("S6a 등록된 폐기 예정 컬럼이 실제 슈퍼셋에 있다 (%d개)" % len(DEPR),
          not missing,
          "슈퍼셋에 없는 것을 등록했다 — 이미 빠졌으면 등록을 지울 것: %s"
          % ", ".join(missing))
    # in_gbm 표기가 실제 배포 pkl 과 맞는가 — 여기가 틀리면 "지워도 되는 줄 알고"
    # 지우는 사고가 난다.
    bad = []
    for name, meta in DEPR.items():
        actual = []
        for hz in ("1m", "3m", "5m", "10m", "15m", "30m"):
            p = os.path.join(ROOT, "model", "horizons",
                             "feature_names_%s.pkl" % hz)
            if os.path.exists(p):
                with open(p, "rb") as f:
                    if name in set(pickle.load(f)):
                        actual.append(hz)
        if sorted(actual) != sorted(meta.get("in_gbm") or []):
            bad.append("%s: 등록 %s vs 실제 %s"
                       % (name, meta.get("in_gbm"), actual))
    check("S6b in_gbm 표기가 배포 pkl 실제와 일치한다", not bad,
          "; ".join(bad) + "  ← 배포 중인 컬럼을 '미배포'로 적으면 제거 사고가 난다")
else:
    check("S6 슈퍼셋 pkl 존재", False, "%s 없음" % sup_path)

check("S7 `ofi_pressure` 는 폐기 목록에 없다",
      "ofi_pressure" not in DEPR,
      "sign(ofi_norm) 항등식이지만 단기 CORE 체크리스트 실집행 키다 — "
      "중복이라고 지우면 진입 게이트가 깨진다")
check("S7b 삭제가 아니라 등록임이 코드로 강제된다 (경고만, 차단 없음)",
      "폐기 예정 컬럼" in io.open(
          os.path.join(ROOT, "learning", "batch_retrainer.py"),
          encoding="utf-8").read(),
      "batch_retrainer 에 감시 로그가 없으면 다음 세션이 왜 남아 있는지 재조사한다")

print()
if FAILURES:
    print("❌ 실패 %d건:" % len(FAILURES))
    for f in FAILURES:
        print("   - %s" % f)
    sys.exit(1)
print("✅ 전부 통과")
sys.exit(0)

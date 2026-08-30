# -*- coding: utf-8 -*-
"""[MW0601 500차 2단계] 워밍업 폴백 가시화 회귀 테스트 — 계측 4원칙 ②·④.

────────────────────────────────────────────────────────────────────────────
막으려는 것
────────────────────────────────────────────────────────────────────────────
CVD 와 VPIN 은 버퍼가 차기 전까지 **0.0 을 내보낸다**. 그 0.0 은 바깥에서
"측정했더니 0"과 구분되지 않았다:

  · CVD  `compute()` n<3      → cvd/cvd_norm/cvd_slope/direction 전부 0
    실측 cvd 계열 zero 0.5%(n=7,527)가 정확히 이 구간(매 거래일 개장 직후 2분)
  · VPIN `_complete_bucket()` 버킷<10 → vpin=0.0
    실측 zero 6.3%. `vpin` 의 시간축 비율 0.479(개장 워밍업 성분)도 여기서 온다

CLAUDE.md 계측 4원칙 ②: **"측정하지 않았다"와 "측정했더니 0이다"를 같은 값으로
표현하지 마라.** 같은 계열의 과거 사고 — `recent_accuracy()` 가 빈 버퍼에서
조용히 0.5 를 반환해 `daily_stats` 에 8거래일 연속 기록된 건(457차),
`program_*` 3종이 `.get(key, 0)` 으로 상수 0 을 "정상 수집"으로 위장한 건(451차).

소비처가 숫자를 요구하므로 **값은 0.0 을 유지**하고 `*_measured` 동반 플래그로
구분한다(원칙 ②가 제시한 두 선택지 중 후자).

  W1  CVD 워밍업(n<3) 반환에 measured=False 가 동반된다
  W2  CVD 정상 구간 반환에 measured=True 가 동반된다
  W3  VPIN 워밍업(<10버킷) 이 measured=False, 이후 True 로 바뀐다
  W4  VPIN `_measured` 가 __init__ 에서 명시 초기화된다 (getattr 폴백 금지)
  W5  reset_daily() 가 measured 를 되돌린다 (다음 날 워밍업이 다시 잡힌다)
  W6  feature_builder 가 cvd_measured · vpin_measured 를 기록한다
  W7  `*_measured` 가 L0 상태플래그로 분류된다
        ← 안 하면 폴백을 드러내려고 만든 플래그가 **신설 즉시 CRITICAL** 로 떠서
          경보 피로를 만든다(0802 계획 Phase A 확정사항 4번이 지적한 그 실패).

실행: python tests/test_500_warmup_measured.py   (COM/브로커·DB 불필요)
"""

import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

from utils.analysis_db import utf8_console  # noqa: E402

utf8_console()

from features.technical.cvd import CVDCalculator  # noqa: E402
from features.supply_demand.vpin import VPINCalculator  # noqa: E402
from scripts.feature_health_report import is_benign_flag  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("OK" if cond else "FAIL", name,
                         ("\n         → %s" % detail) if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)
    return cond


# ── W1·W2 — CVD ────────────────────────────────────────────────
cvd = CVDCalculator(window=10)
warm = [cvd.update_from_bar(close=390.0 + i, buy_vol=10, sell_vol=8)
        for i in range(2)]
check("W1 CVD 워밍업(n<3) 이 measured=False 를 동반한다",
      all(r.get("measured") is False for r in warm),
      "반환값: %s" % [r.get("measured") for r in warm])
check("W1b 워밍업 반환의 값은 0.0 을 유지한다 (소비처 호환)",
      all(r["cvd_norm"] == 0.0 and r["cvd_slope"] == 0.0 for r in warm))
r3 = cvd.update_from_bar(close=393.0, buy_vol=10, sell_vol=8)
check("W2 CVD 정상 구간이 measured=True 를 동반한다",
      r3.get("measured") is True, "반환: %r" % r3.get("measured"))
check("W2b warmup_bars 가 함께 나온다 (몇 봉째인지 남긴다)",
      warm[0].get("warmup_bars") == 1 and r3.get("warmup_bars") == 3,
      "%r / %r" % (warm[0].get("warmup_bars"), r3.get("warmup_bars")))

# ── W3·W5 — VPIN ───────────────────────────────────────────────
vp = VPINCalculator(bucket_size=100)
check("W3a 초기 상태는 measured=False", vp.is_measured() is False)
done, price = 0, 390.0
while done < 12:
    price += 0.05
    if vp.update_tick(price=price, volume=60):
        done += 1
        if done == 5:
            check("W3b 5버킷(<10) 시점에 measured=False", vp.is_measured() is False)
check("W3c 10버킷 이상에서 measured=True", vp.is_measured() is True)
check("W3d vpin 값이 실제로 산출된다", vp.get_current_vpin() > 0.0,
      "vpin=%r" % vp.get_current_vpin())
vp.reset_daily()
check("W5 reset_daily() 가 measured 를 False 로 되돌린다",
      vp.is_measured() is False,
      "다음 거래일 워밍업이 다시 잡히지 않으면 개장 구간 0.0 이 또 위장된다")

# ── W4 — getattr 폴백 금지 (계측 4원칙 ④) ──────────────────────
vpin_src = io.open(os.path.join(ROOT, "features", "supply_demand", "vpin.py"),
                   encoding="utf-8").read()
check("W4a `_measured` 가 __init__ 에서 명시 초기화된다",
      re.search(r"def __init__.*?self\._measured\s*:\s*bool\s*=", vpin_src, re.S)
      is not None,
      "__init__ 초기화가 없으면 tests/test_457_fallback_visibility.py 계열의 "
      "'읽기만 있고 할당 없는 속성' 사고가 재발한다")
check("W4b `getattr(self, \"_measured\", ...)` 폴백 읽기가 없다",
      'getattr(self, "_measured"' not in vpin_src
      and "getattr(self, '_measured'" not in vpin_src,
      "CLAUDE.md 계측 4원칙 ④ — 런타임 상태를 getattr 폴백으로 읽지 마라")

# ── W6 — feature_builder 배선 ──────────────────────────────────
fb_src = io.open(os.path.join(ROOT, "features", "feature_builder.py"),
                 encoding="utf-8").read()
for key in ("cvd_measured", "vpin_measured"):
    check("W6[%s] feature_builder 가 기록한다" % key,
          'features["%s"]' % key in fb_src,
          "계산만 하고 아무도 소비하지 않으면 TOX 죽은 섀도와 같은 상태가 된다")
check("W6c CVD 예외 폴백 경로도 cvd_measured 를 0 으로 남긴다",
      re.search(r'"cvd_slope":\s*0\.0,\s*\n\s*"cvd_measured":\s*0\.0', fb_src)
      is not None,
      "예외 경로에서 키가 빠지면 그 분봉만 컬럼이 사라져 '미측정'이 또 안 보인다")

# ── W7 — L0 상태플래그 분류 ────────────────────────────────────
for key in ("cvd_measured", "vpin_measured"):
    check("W7[%s] L0 상태플래그로 분류된다" % key, is_benign_flag(key),
          "정상 운영에서 거의 항상 1 이라 분류하지 않으면 신설 즉시 CRITICAL 로 뜬다 "
          "— 폴백을 드러내려는 장치가 경보 피로를 만들어 진짜 이상을 묻는다")
check("W7c 진짜 피처는 상태플래그로 오분류되지 않는다",
      not is_benign_flag("cvd_delta_norm") and not is_benign_flag("ofi_norm"),
      "접미사 규칙이 너무 넓으면 실제 이상을 조용히 삼킨다")

print()
if FAILURES:
    print("❌ 실패 %d건:" % len(FAILURES))
    for f in FAILURES:
        print("   - %s" % f)
    sys.exit(1)
print("✅ 전부 통과")
sys.exit(0)

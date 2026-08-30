# -*- coding: utf-8 -*-
"""[MW0601 500차 1단계] CVD·OFI 라이브 결함 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
T1 이 이 파일의 존재 이유다 — **임계와 그 임계가 재는 피처의 범위를 묶는다**
────────────────────────────────────────────────────────────────────────────
TrendGate 의 CVD 급반전 하드브레이크는 배포 이래 **한 번도 발동할 수 없었다**:

    _CVD_SLOPE_HARD_BREAK_DN = -300   vs  실측 cvd_slope 범위 [0.0000, 0.9743]
    _CVD_SLOPE_HARD_BREAK_UP = +200

Phase 3-A 가 `cvd_slope` 를 계약수 → 정규화값[-1,1] 으로 바꾸면서
(`feature_builder.py:208`) 임계를 함께 옮기지 않았다. **단위 300배 불일치**이고,
에러도 경보도 없이 조용히 죽었다(계측 4원칙 ① 위반).

그 하드브레이크는 진입 min_conf 를 0.44(부스트 시 0.38)까지 **완화**하는 streak 의
**즉시 취소 장치**다. 완화는 살고 취소만 죽어 있었다. 3분 리셋
(`_STREAK_FAIL_RESET`)은 살아 있으므로 최악 노출은 3분이지만, 설계자가
"숏스퀴즈는 3분을 기다릴 수 없다"고 판단해 **추가로** 단 장치다.
471차 F-1(15:10 1차 경로) · 474차(중기·장기 CORE 그룹)와 같은 도달불가 유형이며,
6개월간 어떤 계측에도 걸리지 않은 것까지 같다.

⇒ **임계를 -0.3 으로 고치는 것만으로는 재발을 못 막는다.** 정규화가 또 바뀌면
   같은 일이 또 난다. 그래서 T1 은 임계값이 아니라 **"임계가 그 피처의 실측
   관측 범위 안에 있는가 + 발화율이 상식 범위인가"** 를 잠근다.

  T1  하드브레이크 임계가 대상 피처의 실측 범위 안 + 발화율 0.1~10%   ← 핵심
  T2  TrendGate 가 죽은 키(cvd_slope · cvd_direction)를 읽지 않는다
  T3  int() 절단 금지 — 값이 {0.0, 0.5} 인 피처에 int() 를 씌우면 영구 0 이 된다
  T4  앙상블 숏서킷이 방향 대칭이다 (구조적 LONG 편향 제거)
  T5  Guard-F1 이 지키는 키 == 체크리스트가 실제로 쓰는 키
  T6  항등식 고정 — ofi_imbalance·ofi_pressure 는 ofi_norm 의 결정론적 파생

T1·T6 은 `raw_data.db` 가 필요하다. 없으면 ⏳ 로 **명시**하고 넘어간다.

실행: python tests/test_500_cvd_ofi_live_defects.py   (COM/브로커 불필요)
"""

import io
import json
import os
import re
import sqlite3
import sys
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

# cp949 콘솔에서 ⏳·✅ 같은 문자가 UnicodeEncodeError 로 테스트를 죽인다
# (455차 전례). 판정 로직과 무관한 사고이므로 출력 스트림을 먼저 고정한다.
from utils.analysis_db import utf8_console  # noqa: E402

utf8_console()

RAW_DB = os.path.join(ROOT, "data", "db", "raw_data.db")
FAILURES = []
SKIPPED = []


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("OK" if cond else "FAIL", name,
                         ("\n         → %s" % detail) if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)
    return cond


def skip(name, why):
    print("[ ⏳ ] %s — %s (통과가 아니라 미실행)" % (name, why))
    SKIPPED.append(name)


def src_of(relpath):
    return io.open(os.path.join(ROOT, relpath), encoding="utf-8").read()


def load_rows(days_from="2026-07-31"):
    """raw_features (ts, dict) — 읽기 전용."""
    con = sqlite3.connect("file:%s?mode=ro" % RAW_DB.replace("\\", "/"), uri=True)
    out = []
    for ts, f in con.execute(
            "select ts, features from raw_features where ts >= ? order by ts",
            (days_from,)):
        try:
            out.append((ts, json.loads(f)))
        except Exception:
            continue
    con.close()
    return out


# ══════════════════════════════════════════════════════════════
# T1 — 임계·범위 묶음  (이 파일의 핵심)
# ══════════════════════════════════════════════════════════════
import strategy.entry.trend_persistence as TP  # noqa: E402

spec = getattr(TP, "HARD_BREAK_SPEC", None)
if not check("T1a TrendGate 가 HARD_BREAK_SPEC 을 기계판독 형태로 선언한다",
             isinstance(spec, dict) and bool(spec),
             "임계와 대상 피처를 코드가 스스로 밝히지 않으면 범위 검증을 자동화할 수 없다. "
             "`HARD_BREAK_SPEC = {키: {feature, window, op, threshold}}` 를 선언할 것"):
    skip("T1b 임계가 실측 범위 안 + 발화율 정상", "HARD_BREAK_SPEC 미선언")
elif not os.path.exists(RAW_DB):
    skip("T1b 임계가 실측 범위 안 + 발화율 정상", "raw_data.db 없음")
else:
    rows = load_rows()
    for key, s in sorted(spec.items()):
        feat, win = s["feature"], int(s.get("window", 1) or 1)
        thr, op = float(s["threshold"]), s["op"]
        series, buf, day = [], deque(maxlen=win), None
        for ts, d in rows:
            if ts[:10] != day:
                day = ts[:10]
                buf.clear()
            buf.append(float(d.get(feat, 0.0) or 0.0))
            if len(buf) == win:
                series.append(sum(buf) / float(win))
        if not series:
            skip("T1b[%s]" % key, "%s 표본 없음" % feat)
            continue
        lo, hi = min(series), max(series)
        fired = sum(1 for x in series
                    if (x <= thr if op == "<=" else x >= thr))
        rate = 100.0 * fired / len(series)
        check("T1b[%s] 임계 %+.3f 가 %s(w=%d) 실측 범위 [%+.3f, %+.3f] 안에 있다"
              % (key, thr, feat, win, lo, hi),
              lo <= thr <= hi,
              "임계가 범위 밖 = 구조적 발동 불가. 단위가 바뀌었는지 먼저 의심할 것")
        check("T1c[%s] 발화율 %.2f%% 가 상식 범위(0.1~10%%)" % (key, rate),
              0.1 <= rate <= 10.0,
              "0 에 가까우면 죽은 장치, 10%% 초과면 streak 자체를 무력화한다 "
              "(단일 바 cvd_delta_norm 은 |0.90| 에서도 8%% 발화 — 그래서 롤링을 쓴다)")


# ══════════════════════════════════════════════════════════════
# T2·T3 — 죽은 키 / int() 절단
# ══════════════════════════════════════════════════════════════
tp_src = src_of("strategy/entry/trend_persistence.py")

check("T2a TrendGate 가 죽은 키 `cvd_slope` 를 읽지 않는다",
      'features.get("cvd_slope"' not in tp_src,
      "cvd_slope 는 buy_vol 편향으로 음수 0건 + 시각 함수다(500차)")
check("T2b TrendGate 가 죽은 키 `cvd_direction` 을 읽지 않는다",
      'features.get("cvd_direction"' not in tp_src,
      "cvd_direction 은 {0.0, 0.5} 2값 고착이다(최빈 99.5%)")

# int() 절단 — 값이 0.5 인 피처에 int() 를 씌우면 영구 0. 표시 경로도 포함한다.
_INT_TRUNC = re.compile(r'int\(\s*(?:float\()?features(?:\s*or\s*\{\})?\.get\(\s*[\'"]'
                        r'(cvd_direction|cvd_delta_norm|cvd_divergence|cvd_slope|'
                        r'ofi_norm|ofi_imbalance)[\'"]')
for rel in ("strategy/entry/trend_persistence.py", "main.py",
            "model/ensemble_decision.py"):
    hits = _INT_TRUNC.findall(src_of(rel))
    check("T3[%s] 연속형 피처에 int() 절단이 없다" % rel,
          not hits,
          "int(0.5) == 0 — 값이 있는데 영구 0 이 된다. 발견: %s" % ", ".join(sorted(set(hits))))


# ══════════════════════════════════════════════════════════════
# T4 — 앙상블 숏서킷 방향 대칭
# ══════════════════════════════════════════════════════════════
ed_src = src_of("model/ensemble_decision.py")
check("T4a 숏서킷이 고착 키 `cvd_direction` 을 확증에 쓰지 않는다",
      'get("cvd_direction"' not in ed_src,
      "0.5 고착이라 `_cvd > 0` 이 99.5% True / `_cvd < 0` 이 0건 "
      "→ UP 은 무조건 통과, DOWN 만 OFI 를 요구하는 구조적 LONG 편향")
# UP 분기와 DOWN 분기가 같은 피처쌍을 쓰는가 (부호만 반대)
_m = re.search(r"_feat_agree\s*=\s*\((.*?)\n\s*\)", ed_src, re.S)
_blk = _m.group(1) if _m else ""
_up = re.findall(r"_(\w+)\s*>\s*0", _blk)
_dn = re.findall(r"_(\w+)\s*<\s*0", _blk)
check("T4b UP·DOWN 확증이 같은 피처 집합을 쓴다 (대칭)",
      bool(_blk) and sorted(set(_up)) == sorted(set(_dn)),
      "UP=%s vs DOWN=%s" % (sorted(set(_up)), sorted(set(_dn))))


# ══════════════════════════════════════════════════════════════
# T5 — Guard-F1 이 지키는 키 == 체크리스트 실소비 키
# ══════════════════════════════════════════════════════════════
from config.settings import CORE_FEATURES_BY_GROUP  # noqa: E402

main_src = src_of("main.py")
_g = re.search(r"Guard-F1.*?", main_src)
_gm = re.search(r"for\s+_fk\s+in\s+\(([^)]*)\)\s*:\s*\n\s*_fv\s*=\s*features\.get",
                main_src)
if _gm is None:
    check("T5 Guard-F1 대상 키가 하드코딩돼 있지 않다 (CORE 정의에서 읽는다)",
          "CORE_FEATURES_BY_GROUP" in main_src and "Guard-F1" in main_src,
          "하드코딩 루프도 못 찾고 CORE 정의 참조도 없다 — 가드가 사라졌는지 확인할 것")
else:
    hard = set(re.findall(r'"([a-z_]+)"', _gm.group(1)))
    want = set(v for k, v in CORE_FEATURES_BY_GROUP["short"].items()
               if isinstance(v, str))
    check("T5 Guard-F1 하드코딩 키 %s 가 실소비 키 %s 와 일치"
          % (sorted(hard), sorted(want)),
          hard == want,
          "가드가 안 쓰는 값을 지키고, 실제 쓰는 값(cvd_delta_norm)은 무방비다. "
          "CORE_FEATURES_BY_GROUP 에서 읽도록 바꿀 것")


# ══════════════════════════════════════════════════════════════
# T6 — 항등식 고정 (구성적 중복)
# ══════════════════════════════════════════════════════════════
if not os.path.exists(RAW_DB):
    skip("T6 OFI 항등식 고정", "raw_data.db 없음")
else:
    rows = load_rows()
    n = len(rows)
    bad_i = bad_p = round_edge = 0
    neg_slope = 0
    for _, d in rows:
        if "ofi_norm" in d and "ofi_imbalance" in d:
            if abs(round(d["ofi_norm"] / 3.0, 3) - d["ofi_imbalance"]) > 0.0011:
                bad_i += 1
        if "ofi_norm" in d and "ofi_pressure" in d:
            s = 1.0 if d["ofi_norm"] > 0 else (-1.0 if d["ofi_norm"] < 0 else 0.0)
            if abs(s - d["ofi_pressure"]) > 1e-9:
                # 반올림 경계 — pressure = sign(ofi_raw) 인데 ofi_norm 은 4자리
                # 반올림이라 |ofi_norm| < 5e-5 이면 ±0.0 이 된다(부호 소실).
                # 항등식 자체는 살아 있으므로 별도로 센다.
                if d["ofi_norm"] == 0.0:
                    round_edge += 1
                else:
                    bad_p += 1
        if float(d.get("cvd_slope", 0.0) or 0.0) < 0:
            neg_slope += 1
    check("T6a ofi_imbalance ≡ round(ofi_norm/3, 3)  (n=%d, 불일치 %d)" % (n, bad_i),
          bad_i == 0,
          "항등식이 깨졌다면 ofi.py 가 바뀐 것이다 — 중복 해소인지 결함인지 확인할 것")
    check("T6b ofi_pressure ≡ sign(ofi_norm)  (n=%d, 불일치 %d, 반올림경계 %d)"
          % (n, bad_p, round_edge),
          bad_p == 0)
    check("T6c 반올림 경계가 0.5%% 미만 (%.2f%%)" % (100.0 * round_edge / max(n, 1)),
          round_edge <= 0.005 * n,
          "|ofi_norm| < 5e-5 인 행이 급증했다면 avg_vol 스케일이 바뀐 것이다")
    print("     ℹ cvd_slope 음수 %d/%d — 0 이면 buy_vol 편향이 아직 살아 있다는 뜻"
          % (neg_slope, n))

print()
if SKIPPED:
    print("⏳ 미실행 %d건: %s" % (len(SKIPPED), ", ".join(SKIPPED)))
if FAILURES:
    print("❌ 실패 %d건:" % len(FAILURES))
    for f in FAILURES:
        print("   - %s" % f)
    sys.exit(1)
print("✅ 전부 통과")
sys.exit(0)

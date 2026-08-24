# -*- coding: utf-8 -*-
"""[MW0602 491차 F-4] 장중 자동 재학습(STEP 3) 조건의 도달 가능성 계측 — 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
배경 (상세: dev_memory/DECISION_LOG.md 2026-08-24 491차 · 0824 리포트 1-7)
────────────────────────────────────────────────────────────────────────────
DriftRetrain 조건A는 `5m 정확도 < 25%` **and** `n >= 20` 이다. 그런데 그 `n` 은
`online_learner._acc_buf["5m"]`(100 슬롯 롤링)의 길이이고, 학습은 5m 봉단위로
dedup 되므로 창 안에 들어올 수 있는 5m 표본의 **이론 상한도 20**이다.
즉 조건A는 "창 전체가 빈틈없이 conf>=0.52 를 통과" 라는 사실상 도달 불가 조건을
요구한다. 조건B(n>=15)도 같은 상한 아래 있다.

🔴 이 Fix 는 **계측만** 붙인다. 임계도 조건식도 무변경 — 표본 게이트 완화는
   학습 위생 정책 변경이고 490차 P0 와 얽힌다(주간회의 소관).

지키는 불변식:
  T1  `[DriftRetrain]` 상태 샘플에 `n_cap=` · `conf_pass_rate=` 가 있다.
  T2  `n_cap == ACCURACY_WINDOW // HORIZONS["5m"]` (= 100 // 5 = 20).
      🔴 이 값이 조건A의 `n>=20` 과 같다는 사실 자체가 1-7 이다.
  T3  임계·조건식 무변경 — 0.25 / 20 / 0.15 / 15 / 0.52 가 그대로 있다.
  T4  `conf_pass_rate` 는 표본 0 일 때 **NA**(미측정)다. 0.000 이 아니다
      (계측 4원칙 ② — 0824 G-5 가 말한 「미측정 0.0% vs 진짜 0.0%」).
  T5  통과율 누계가 **날짜가 바뀌면 리셋**된다(당일 누계 규약).
  T6  수집기 §12b 에 임계쌍 `DriftRetrain조건B(n≥15)` 가 있고, 로그 원천
      스캐너가 그 쌍을 실제로 렌더한다.

실행: python tests/test_491_driftretrain_reachability.py   (COM/브로커 불필요)
"""

import datetime
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

FAILURES = []
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


_MAIN = io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()


def test_t1_fields_in_state_sample():
    m = re.search(r'"\[DriftRetrain\] state=%s[^"]*"\s*\n\s*"([^"]*)"\s*\n\s*"([^"]*)"',
                  _MAIN)
    check("T1: 상태 샘플 포맷 문자열 발견", m is not None)
    blob = _MAIN[_MAIN.find('"[DriftRetrain] state=%s'):][:400]
    check("T1: n_cap= 존재", "n_cap=%d" in blob)
    check("T1: conf_pass_rate= 존재", "conf_pass_rate=%s" in blob)
    check("T1: 종전 필드 보존(파서 호환)",
          "acc5m=%.1f%%" in blob and "cond_a=%s" in blob and "cond_b=%s" in blob)


def test_t2_n_cap_invariant():
    from config.settings import HORIZONS
    # ⚠ `learning.online_learner` 를 import 하지 않는다 — numpy/sklearn 이 필요해
    #   COM 없는 테스트 환경(PATH 기본 python)에서 죽는다. 상수만 원문에서 읽는다.
    src = io.open(os.path.join(ROOT, "learning", "online_learner.py"),
                  encoding="utf-8").read()
    m = re.search(r"ACCURACY_WINDOW\s*=\s*(\d+)", src)
    check("T2: ACCURACY_WINDOW 상수 발견", m is not None)
    want = int(int(m.group(1)) // HORIZONS["5m"])
    check("T2: 이론 상한 = %d (100 // 5)" % want, want == 20)
    # main.py 가 같은 두 원천에서 계산하는지 — 하드코딩 20 이면 안 된다
    check("T2: ACCURACY_WINDOW 에서 계산", 'ACCURACY_WINDOW", 100)' in _MAIN)
    check("T2: HORIZONS['5m'] 에서 계산", 'HORIZONS.get("5m", 5)' in _MAIN)
    # 🔴 상한이 조건A 표본 게이트와 같다 = 1-7 의 실체
    check("T2: 상한이 조건A n>=20 과 같다(= 1-7)",
          want == 20 and "_dr_acc5m_n >= 20" in _MAIN)


def test_t3_thresholds_unchanged():
    for frag in ("_dr_acc5m < 0.25", "_dr_acc5m_n >= 20",
                 "_dr_acc5m < 0.15", "_dr_acc5m_n >= 15",
                 "_min_conf_sgd  = 0.52"):
        check("T3: 무변경 — %s" % frag, frag in _MAIN)


def test_t4_unmeasured_is_na():
    check("T4: 표본 0 → NA", '_dr_cpr   = ("NA" if _dr_seen <= 0' in _MAIN)
    # 0.000 폴백이 들어오지 않았는지
    check("T4: 0.0 폴백 없음",
          '_dr_cpr = "%.3f" % 0' not in _MAIN and 'conf_pass_rate=0.000' not in _MAIN)


def test_t5_daily_reset():
    check("T5: 날짜 키 비교로 리셋",
          '_cst.get("date") != _day_dv' in _MAIN)
    check("T5: 리셋 시 seen/pass 동시 초기화",
          '{"date": _day_dv, "seen": {}, "pass": {}}' in _MAIN)
    check("T5: __init__ 기본값 None(미측정)", "self._sgd_conf_stat = None" in _MAIN)


def test_t6_collector_pair():
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills",
                                    "mireuk-daily-check", "scripts"))
    import collect_evidence as CE
    cfg = json.loads(json.dumps(CE.DEFAULT_CONFIG))
    pairs = cfg["threshold_reachability"]["pairs"]
    name = "DriftRetrain조건B(n≥15)"
    check("T6: 임계쌍 등록", name in pairs)
    check("T6: 임계 15", float(pairs[name]["threshold"]) == 15.0)
    check("T6: 로그 원천 스펙", "log" in pairs[name] and "db" not in pairs[name])
    rows = CE.scan_threshold_reachability(ROOT, cfg, datetime.date.today())
    got = [r for r in rows if r["name"] == name]
    check("T6: 스캐너가 행을 낸다", len(got) == 1)
    if got:
        check("T6: 판정 문자열 존재(예외로 죽지 않는다)", bool(got[0]["verdict"]))
    # 기존 3쌍이 그대로 렌더되는지 — 로그 원천 추가가 DB 경로를 깨지 않았다
    check("T6: 기존 DB 원천 쌍 보존", len(rows) == len(pairs))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for fn in (test_t1_fields_in_state_sample, test_t2_n_cap_invariant,
               test_t3_thresholds_unchanged, test_t4_unmeasured_is_na,
               test_t5_daily_reset, test_t6_collector_pair):
        try:
            fn()
        except Exception as e:
            print("[FAIL] %s: %r" % (fn.__name__, e))
            FAILURES.append(fn.__name__)
    print("-" * 60)
    print("전부 통과" if not FAILURES else "실패 %d건: %s" % (len(FAILURES), FAILURES))
    sys.exit(1 if FAILURES else 0)

# -*- coding: utf-8 -*-
"""[MW0602 494차] F-1 회귀 — CORE 축퇴의 원인 축(`frac_zero`) 계측.

**무엇을 고정하는가.**

① 🔴 **기존 문구가 한 글자도 바뀌지 않았다.** 이 로그는 §12 가 정규식으로 읽는다 —
   앞부분을 건드리면 계측이 조용히 끊긴다(468차 G-2 가 경고한 형태). 새 필드는
   **꼬리에만** 붙는다.
② 새 필드 4종이 실제로 붙는다.
③ 수집기 §12 의 버킷 매핑이 연속값을 3버킷으로 접는다 — 접지 않으면 전부 `변동`이
   되어 고착 감시가 무의미해진다.
④ 판정 기준은 **관측값 역산이 아니다**(313차 ④) — 0.90/0.50 이라는 산술 경계다.

실행:
    python tests/test_494_core_degen_cause_axis.py
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILURES = []

_COLLECTOR = os.path.join(".claude", "skills", "mireuk-daily-check", "scripts",
                          "collect_evidence.py")


def _read(rel):
    with io.open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def test_existing_log_prefix_is_byte_identical():
    """🔴 §12 가 읽는 앞부분 무변경 — 확장은 꼬리에서만."""
    src = _read(os.path.join("model", "multi_horizon_model.py"))
    assert ("\"[ScalerRefresh] %s CORE '%s' raw_std≈0(%.4f)\"\n"
            "                                \" → identity(0,1) 강제 (FLAT 100%% 방지)%s\""
            in src), "기존 문구 앞부분이 바뀌었거나 꼬리 확장(%s)이 없다"


def test_new_fields_are_appended():
    src = _read(os.path.join("model", "multi_horizon_model.py"))
    for field in ("n_nonzero=%d/%d", "frac_zero=%.3f", "raw_range=%.4f"):
        assert field in src, field
    # 요약 실패가 축퇴 방어 자체를 막지 않는다
    assert 'n_nonzero=?/? frac_zero=? raw_range=?' in src


def test_regex_matches_extended_line_only():
    old = ("[ScalerRefresh] 1m CORE 'ofi_norm' raw_std≈0(0.0278)"
           " → identity(0,1) 강제 (FLAT 100% 방지)")
    new = old + " n_nonzero=3/30 frac_zero=0.900 raw_range=0.0912"
    rx = re.compile(r"\[ScalerRefresh\][^\n]*frac_zero=(?P<v>[0-9.?]+)")
    assert rx.search(old) is None, "배포 전 줄은 잡히면 안 된다(measured_since 취지)"
    m = rx.search(new)
    assert m and m.group("v") == "0.900"


def test_collector_buckets_fold_continuous_values():
    """연속값 → 3버킷. 접지 않으면 전부 `변동`이 되어 고착 감시가 죽는다."""
    src = _read(_COLLECTOR)
    i = src.find('"CORE축퇴_원인축"')
    assert i > 0, "수집기 §12 에 CORE축퇴_원인축 이 없다"
    block = src[i:i + 2000]
    assert '"measured_since": "2026-08-26"' in block, "배포일 마커가 없다"
    assert "benign" not in block.split('"why"')[0], \
        "🔴 benign 으로 등록하면 안 된다 — 점질량 고착이 정상이라는 판단은 아직 없다"

    vm = [(r"1\.000|0\.9\d+", "≥0.90(점질량)"),
          (r"0\.[5-8]\d+", "0.50~0.89"),
          (r"0\.[0-4]\d+", "<0.50(진짜 저변동)"),
          (r"\?", "요약실패")]
    # 설정에 적힌 매핑과 위 기대치가 같은지 대조 (설정만 바뀌면 여기서 깨진다)
    for pat, label in vm:
        assert pat.replace("\\", "\\\\") in block or pat in block, pat
        assert label in block, label
    for value, expect in (("0.900", "≥0.90(점질량)"), ("1.000", "≥0.90(점질량)"),
                          ("0.667", "0.50~0.89"), ("0.100", "<0.50(진짜 저변동)"),
                          ("?", "요약실패")):
        got = next((l for p, l in vm if re.fullmatch(p, value)), None)
        assert got == expect, (value, got, expect)


def test_thresholds_are_arithmetic_not_backfitted():
    """판정 임계 0.90/0.50 이 관측값 역산이 아님을 문서로 고정(313차 ④)."""
    src = _read(os.path.join("model", "multi_horizon_model.py"))
    i = src.find("[MW0602 494차 / F-1]")
    assert i > 0
    block = src[i:i + 2500]
    assert "관측값에서 역산하지 않았다" in block
    assert "frac_zero >= 0.90" in block and "frac_zero < 0.5" in block


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for fn in (test_existing_log_prefix_is_byte_identical,
               test_new_fields_are_appended,
               test_regex_matches_extended_line_only,
               test_collector_buckets_fold_continuous_values,
               test_thresholds_are_arithmetic_not_backfitted):
        try:
            fn()
            print("[ok]   %s" % fn.__name__)
        except Exception as e:
            print("[FAIL] %s: %r" % (fn.__name__, e))
            FAILURES.append(fn.__name__)
    print("-" * 60)
    print("전부 통과" if not FAILURES else "실패 %d건: %s" % (len(FAILURES), FAILURES))
    sys.exit(1 if FAILURES else 0)

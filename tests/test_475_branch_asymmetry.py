# -*- coding: utf-8 -*-
"""tests/test_475_branch_asymmetry.py
    — [MW0602 475차 후속] 수집기 §12 분기편향 탐지 회귀

────────────────────────────────────────────────────────────────────────────
무엇을 지키는가
────────────────────────────────────────────────────────────────────────────
고착·무기록 말고 **세 번째 죽음**이 있다 — 계측이 *한쪽 분기에서만* 돈다.

2026-08-18 `[ConfFloorGuard] state=` 80샘플이 전부 `ZONE_BLACKOUT` 이었고, 그 80이
진입 금지 존 체류 **80분과 정확히 일치**했다(진입 허용 290분 0건). 값 분포만 보면
"한 값 고착"이지만 진짜 문제는 **분포가 그 분기의 것**이라는 데 있다.
그것을 발견한 방법이 사람이 우연히 한 산술 일치였으므로 계측으로 바꿨다.

⚠ 이 탐지기는 **옵트인**(`sample_axis: "minute"`)이다. 화이트리스트였으면 설계상
  매분이 아닌 지표가 즉시 오탐이 됐다 — 0818 실측 관측률:
    CB_state 1.01(진짜 매분) · ConfFloor 0.22(편향) · degraded 0.07 · CORE준비도 0.12

불변식:
  (1) 매분 샘플러가 한쪽 분기에서만 찍히면 `분기편향`
  (2) 진짜 매분 샘플러(관측률 ≈ 1.0)는 통과 — 값이 한 종류라도 `분기편향` 아님
  (3) `sample_axis` 없는 지표는 관측률을 아예 재지 않는다 (오탐 차단)
  (4) 표본 0은 `무기록`이지 `분기편향`이 아니다 — 배포 첫날 이전이 전부 여기 걸린다
      (0814 ConfFloor 0건의 원인은 편향이 아니라 미배포였다)
  (5) 표본이 없는 날은 분모에서 뺀다 — 안 그러면 배포 첫날 지표가 무조건 편향으로 뜬다
      (0818 ConfFloor: 10일 분모면 0.03, 관측일 분모면 0.22)
"""
from __future__ import print_function

import io
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".claude", "skills", "mireuk-daily-check", "scripts"))

import collect_evidence as ce                                        # noqa: E402

_fails = []


def check(label, cond):
    print("%s %s" % ("[OK]  " if cond else "[FAIL]", label))
    if not cond:
        _fails.append(label)


def _write_log(root, ymd, suffix, lines):
    d = os.path.join(root, "logs")
    if not os.path.isdir(d):
        os.makedirs(d)
    p = os.path.join(d, "%s%s.log" % (ymd, suffix))
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(u"\n".join(lines) + u"\n")
    return p


def _minute_lines(ymd, n_minutes, sampler=None, start_min=9 * 60):
    """09:00 부터 n_minutes 분 동안 매분 한 줄. sampler(i) 가 문자열이면 그 줄을 덧붙인다."""
    y = "%s-%s-%s" % (ymd[:4], ymd[4:6], ymd[6:])
    out = []
    for i in range(n_minutes):
        t = start_min + i
        stamp = u"%s %02d:%02d:30" % (y, t // 60, t % 60)
        out.append(u"%s [INFO] SIGNAL: [Ensemble] dir=UP conf=0.42" % stamp)
        extra = sampler(i) if sampler else None
        if extra:
            out.append(u"%s [INFO] SIGNAL: %s" % (stamp, extra))
    return out


def _cfg(patterns):
    cfg = ce.load_config(".")
    cfg["scan_dirs"] = ["logs"]
    cfg["stuck_indicators"] = dict(cfg["stuck_indicators"])
    cfg["stuck_indicators"]["patterns"] = patterns
    return cfg


_PAT_OPTIN = {
    "샘플러": {"re": r"\[Probe\] state=(?P<v>\w+)", "files": ["_SIGNAL"],
               "sample_axis": "minute", "why": "테스트"},
}
_PAT_NO_AXIS = {
    "샘플러": {"re": r"\[Probe\] state=(?P<v>\w+)", "files": ["_SIGNAL"], "why": "테스트"},
}


def _run(patterns, sampler, n_minutes=300, ymd="20260818"):
    root = tempfile.mkdtemp(prefix="mireuk_test_")
    try:
        _write_log(root, ymd, "_SIGNAL", _minute_lines(ymd, n_minutes, sampler))
        import datetime
        day = datetime.date(int(ymd[:4]), int(ymd[4:6]), int(ymd[6:]))
        rows = ce.scan_stuck_indicators(root, _cfg(patterns), day)
        return rows[0] if rows else None
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ══════════════════════════════════════════════════════════════════
def test_branch_bias_detected():
    # 0818 ConfFloor 재현 — 300분 중 앞 66분(22%)에만 찍힌다.
    r = _run(_PAT_OPTIN, lambda i: "[Probe] state=ZONE_BLACKOUT" if i < 66 else None)
    check("(1) 한쪽 분기에서만 찍히면 분기편향 — %s (관측률 %.2f)"
          % (r["verdict"], r["ratio"] or 0),
          r["verdict"] == "분기편향")
    check("(1) 관측률이 0.22 근방", 0.18 <= (r["ratio"] or 0) <= 0.26)
    check("(1) 표본부족보다 먼저 판정한다 (1일·66건인데 보류되지 않는다)",
          r["verdict"] != "표본부족")


def test_true_per_minute_sampler_passes():
    """CB_state(0818 실측 관측률 1.01) 재현 — 값이 한 종류여도 편향이 아니다."""
    root = tempfile.mkdtemp(prefix="mireuk_test_")
    try:
        import datetime
        for ymd in ("20260812", "20260813", "20260818"):
            _write_log(root, ymd, "_SIGNAL",
                       _minute_lines(ymd, 300, lambda i: "[Probe] state=NORMAL"))
        rows = ce.scan_stuck_indicators(root, _cfg(_PAT_OPTIN),
                                        datetime.date(2026, 8, 18))
        r = rows[0]
    finally:
        shutil.rmtree(root, ignore_errors=True)
    check("(2) 진짜 매분 샘플러는 분기편향 아님 — %s (관측률 %.2f)"
          % (r["verdict"], r["ratio"] or 0),
          r["verdict"] != "분기편향")
    check("(2) 값이 한 종류면 고착으로 간다 — 관측률 축이 고착 판정을 가리지 않는다",
          r["verdict"] == "고착" and (r["ratio"] or 0) >= 0.95)


def test_no_axis_means_no_ratio():
    # degraded(0.07)·CORE준비도(0.12) 처럼 설계상 매분이 아닌 지표 — 옵트인 안 하면 안 잰다.
    r = _run(_PAT_NO_AXIS, lambda i: "[Probe] state=OFF" if i % 15 == 0 else None)
    check("(3) sample_axis 없으면 관측률을 재지 않는다", r.get("ratio") is None)
    check("(3) 따라서 분기편향으로 오탐하지 않는다 — %s" % r["verdict"],
          r["verdict"] != "분기편향")


def test_zero_sample_is_unrecorded_not_bias():
    r = _run(_PAT_OPTIN, lambda i: None)
    check("(4) 표본 0은 무기록이지 분기편향이 아니다 — %s" % r["verdict"],
          r["verdict"] == "무기록")


def test_days_without_samples_excluded_from_denominator():
    """배포 첫날 함정 — 0818 ConfFloor 가 10일 분모면 0.03, 관측일 분모면 0.22."""
    root = tempfile.mkdtemp(prefix="mireuk_test_")
    try:
        import datetime
        # 앞선 4거래일: 로그는 있으나 지표는 아직 없다(미배포)
        for ymd in ("20260811", "20260812", "20260813", "20260814"):
            _write_log(root, ymd, "_SIGNAL", _minute_lines(ymd, 300, None))
        # 배포 첫날: 300분 중 150분에 찍힌다 (0.50 경계 위)
        _write_log(root, "20260818", "_SIGNAL",
                   _minute_lines("20260818", 300,
                                 lambda i: "[Probe] state=OK" if i < 150 else None))
        rows = ce.scan_stuck_indicators(root, _cfg(_PAT_OPTIN),
                                        datetime.date(2026, 8, 18))
        r = rows[0]
        check("(5) 표본 없는 날은 분모에서 빠진다 (exp=300, 1500 아님) — exp=%s"
              % r.get("expected"), r.get("expected") == 300)
        check("(5) 관측률 0.50 — 10일 분모였다면 0.10 이었다",
              0.48 <= (r["ratio"] or 0) <= 0.52)
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    for fn in sorted(
        [v for k, v in list(globals().items()) if k.startswith("test_")],
        key=lambda f: f.__code__.co_firstlineno,
    ):
        print("\n── %s" % fn.__name__)
        fn()
    print("\n" + "=" * 60)
    if _fails:
        print("분기편향 탐지 회귀 실패 %d건" % len(_fails))
        for f in _fails:
            print("  - %s" % f)
        sys.exit(1)
    print("분기편향 탐지 회귀 전부 통과")

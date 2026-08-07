"""[MW0602 439차 P3] [48] 봉중 하드스톱 채널의 **가드 경계 pre/post 분해** 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
무엇이 문제였나
────────────────────────────────────────────────────────────────────────────
[48]은 스스로 이렇게 적어 두고 있다(`bar_stop_path_watch.py` 모듈 docstring):

    "이 채널의 사전등록 가치는 **424차 억제 배포 후의 회복 판정**에 있다"

그런데 `summarize()`는 `start_date`(2026-07-05) 이후 표본을 **통째로 풀링**해서
판정한다. 실측하면 봉중 13건 중 **8건(61.5%)이 가드 배포 이전**이다:

    08-03 : 8건 — 423차 가드는 그날 **장 마감 후** 커밋(c64efd6)됐다.
                  그 세션은 가드 없이 돌았고 진입 21건이 전부 qty=1이었다.
    08-04 : 4건 — qty=1 가드 가동. qty>=2 우회는 424차가 일부러 열어 뒀다.
    08-05 : 1건 — would_suppress=0, 즉 유령이 아니라 **정상 봉중**이다.
    08-06~: 0건 — 431차(MAX_CONTRACTS 10→3)로 qty>=2 급감 + 틱 경로가 선점.

즉 n이 min_samples(25)에 도달하더라도 그 판정은 "억제 후 회복"이 아니라
**pre/post 혼합**이다. 채널이 존재 이유로 내건 질문에 답할 수 없는 상태다.

────────────────────────────────────────────────────────────────────────────
439차 P3가 검증하는 불변식
────────────────────────────────────────────────────────────────────────────
    (1) 봉중 표본이 `guard_live_date` 기준으로 pre/post 분리된다
    (2) pre 비중이 임계 초과면 `prereg_contaminated`가 선다
    (3) 임계 이하면 서지 않는다 (상시 경보 방지)
    (4) **verdict 계산식은 무변경** — 분해는 판정에 관여하지 않는다 (§9, 313차)
    (5) 발생 추이는 **일자별 시퀀스**로 낸다 — 합계 하나로 내면 가드 이전 날이
        섞여 오독된다(최근 5일 합 13건인데 그중 8건이 08-03 = 가드 이전)
    (6) `bar_dry_days`는 마지막 발생 이후 무발생 거래일 수를 정확히 센다

(4)가 깨지면 사후 데이터로 합격선을 움직인 것이 되어 313차 위반이다.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

from scripts.bar_stop_path_watch import (  # noqa: E402
    BAR, TICK, TARGET, _bar_guard_split, summarize,
)

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _mkout(bar_by_day, tick_by_day=None):
    """{날짜: 봉중건수} → compute() 출력 형태로 조립."""
    tick_by_day = tick_by_day or {}
    days = sorted(set(bar_by_day) | set(tick_by_day))
    by_day, groups = {}, {}
    for d in days:
        by_day[d] = {}
        if bar_by_day.get(d):
            by_day[d][BAR] = [-1.0] * bar_by_day[d]
            groups.setdefault(BAR, []).extend([-1.0] * bar_by_day[d])
        if tick_by_day.get(d):
            by_day[d][TICK] = [0.05] * tick_by_day[d]
            groups.setdefault(TICK, []).extend([0.05] * tick_by_day[d])
    return {"since": "2026-07-05", "groups": groups, "n_reclassified": 0,
            "days": {k: len({d for d in days if by_day[d].get(k)})
                     for k in (BAR, TICK)},
            "by_day": by_day, "all_days": days,
            "n_total": sum(len(v) for v in groups.values()), "error": None}


def test_pre_post_split():
    """(1) 실 데이터 형태 — 08-03(가드 이전) 8건 / 08-04~ 5건으로 갈린다."""
    out = _mkout({"2026-08-03": 8, "2026-08-04": 4, "2026-08-05": 1,
                  "2026-08-06": 0, "2026-08-07": 0})
    s = _bar_guard_split(out)
    check("(1) 가드 경계 = 2026-08-04", s["guard_live_date"] == "2026-08-04")
    check("(1) pre n=8 / 1거래일", s["pre_guard"]["n"] == 8 and s["pre_guard"]["days"] == 1)
    check("(1) post n=5 / 2거래일", s["post_guard"]["n"] == 5 and s["post_guard"]["days"] == 2)
    # `pre_guard_share`는 소수 4자리 반올림 저장이다(round(8/13,4)=0.6154).
    check("(1) pre 비중 61.5%", s["pre_guard_share"] == round(8 / 13, 4))


def test_contamination_flag_raised():
    """(2) pre 과반 → 오염 플래그 + 사유 문구."""
    out = _mkout({"2026-08-03": 8, "2026-08-04": 4, "2026-08-05": 1})
    s = _bar_guard_split(out)
    check("(2) prereg_contaminated True", s["prereg_contaminated"] is True)
    check("(2) 사유 문구 존재", bool(s.get("contamination_reason")))
    check("(2) 사유에 '혼합 판정' 명시", "혼합 판정" in s.get("contamination_reason", ""))


def test_contamination_flag_not_raised():
    """(3) pre 소수면 플래그가 서면 안 된다 — 상시 경보 방지."""
    out = _mkout({"2026-08-03": 1, "2026-08-04": 5, "2026-08-05": 5})
    s = _bar_guard_split(out)
    check("(3) pre 비중 1/11 → 플래그 False", s["prereg_contaminated"] is False)
    check("(3) 사유 문구 없음", not s.get("contamination_reason"))


def test_no_bar_samples():
    """(3') 봉중 표본이 아예 없으면 0으로 나누지 않고 플래그도 서지 않는다."""
    out = _mkout({}, {"2026-08-06": 20, "2026-08-07": 15})
    s = _bar_guard_split(out)
    check("(3') pre/post 모두 0", s["pre_guard"]["n"] == 0 and s["post_guard"]["n"] == 0)
    check("(3') 비중 0.0 (ZeroDivision 없음)", s["pre_guard_share"] == 0.0)
    check("(3') 플래그 False", s["prereg_contaminated"] is False)


def test_verdict_unchanged_by_split():
    """(4) 🔴 핵심 — 분해가 verdict를 바꾸면 안 된다 (§9, 313차).

    pre/post 구성이 정반대인 두 표본에서 봉중 총계·유리비율이 같으면
    verdict와 reason이 동일해야 한다.
    """
    a = summarize(_mkout({"2026-08-03": 9, "2026-08-04": 1}))   # pre 지배
    b = summarize(_mkout({"2026-08-03": 1, "2026-08-04": 9}))   # post 지배
    check("(4) verdict 동일", a["verdict"] == b["verdict"])
    check("(4) reason 동일", a["reason"] == b["reason"])
    check("(4) 봉중 통계 동일", a["per_path"][BAR] == b["per_path"][BAR])
    check("(4) 그러나 오염 플래그는 갈린다",
          a["prereg_contaminated"] is True and b["prereg_contaminated"] is False)


def test_recent_sequence_not_pooled():
    """(5) 최근 발생은 합계가 아니라 **일자별 시퀀스**로 나와야 한다."""
    out = _mkout({"2026-08-03": 8, "2026-08-04": 4, "2026-08-05": 1,
                  "2026-08-06": 0, "2026-08-07": 0})
    s = _bar_guard_split(out)
    check("(5) 시퀀스 = [8,4,1,0,0]", s["bar_recent_seq"] == [8, 4, 1, 0, 0])
    check("(5) 합계 키를 노출하지 않는다(오독 방지)", "bar_recent_n" not in s)


def test_dry_days():
    """(6) 마지막 발생 이후 무발생 거래일 수."""
    s = _bar_guard_split(_mkout({"2026-08-03": 8, "2026-08-05": 1,
                                 "2026-08-06": 0, "2026-08-07": 0}))
    check("(6) 무발생 2거래일", s["bar_dry_days"] == 2)
    s2 = _bar_guard_split(_mkout({"2026-08-06": 3, "2026-08-07": 2}))
    check("(6') 마지막 날에도 발생 → 0", s2["bar_dry_days"] == 0)
    s3 = _bar_guard_split(_mkout({}, {"2026-08-06": 5, "2026-08-07": 5}))
    check("(6'') 전 구간 무발생 → 전체 거래일 수", s3["bar_dry_days"] == 2)


def test_live_channel_shape():
    """실 DB — 키가 실제로 채워지는지(스모크)."""
    from scripts.bar_stop_path_watch import compute
    s = summarize(compute("2026-07-05"))
    if s.get("no_data"):
        check("실 DB 없음 — 스킵", True)
        return
    for k in ("guard_live_date", "pre_guard", "post_guard", "pre_guard_share",
              "prereg_contaminated", "bar_by_day", "path_by_day",
              "bar_recent_seq", "bar_dry_days"):
        check("실 DB: %s 존재" % k, k in s)
    check("실 DB: verdict는 사전등록 어휘 유지",
          s.get("verdict") in ("PASS", "FAIL", "INSUFFICIENT"))


if __name__ == "__main__":
    print("=" * 72)
    print("[MW0602 439차 P3] [48] 가드 경계 pre/post 분해 회귀 테스트")
    print("=" * 72)
    for fn in (
        test_pre_post_split,
        test_contamination_flag_raised,
        test_contamination_flag_not_raised,
        test_no_bar_samples,
        test_verdict_unchanged_by_split,
        test_recent_sequence_not_pooled,
        test_dry_days,
        test_live_channel_shape,
    ):
        print("\n-- %s" % fn.__name__)
        fn()
    print("\n" + "=" * 72)
    if FAILURES:
        print("실패 %d건: %s" % (len(FAILURES), FAILURES))
        sys.exit(1)
    print("전부 통과")

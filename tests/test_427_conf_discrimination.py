"""[MW0602 427차] [39] confidence 판별력 감시 채널 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
왜 이 채널인가 — 0804 §P2의 방향을 뒤집었다
────────────────────────────────────────────────────────────────────────────
0804 점검 §P2는 "동적 min_conf가 랜덤 기준선(0.33)까지 내려앉아 사실상 무력화됐다"를
**고쳐야 할 문제**로 적었다. 조사 결과 방향이 틀렸다:

  · 모델축 n=14,770(30m 제외) — 하위절반 33.4% vs 상위절반 33.6% (격차 +0.15%p)
  · 앙상블축 — 승 63건 vs 패 37건, **격차 -0.0008** (Cohen d=-0.015)
  · min_conf 상향 스윕은 전 구간 손익 악화 (0.40→-407,558원 / 0.45→-749,942원)
  · 잘려나간 진입의 승률 62~63%가 전체 승률 63.0%와 **같다**
    → 게이트가 품질 필터가 아니라 **무작위 샘플러**로 작동한다는 직접 증거
  · 설계값 0.54 복원 시 진입이 거의 전멸 (실제 진입 conf 최댓값 0.579)

⚠ 초판은 앙상블축을 **81/100건**으로 보고했다(승 51/패 30, 격차 -0.0015).
  분 단위 정확 조인이 체결 분 경계를 넘은 19건을 잃은 것이며 427차 후속에서
  고쳤다 — 아래 `test_entry_decision_join` 참조. **판정은 바뀌지 않았다.**

**게이트는 정보 없는 신호를 걸러낼 수 없다.** 그래서 이 채널은 min_conf가 아니라
그 **선행조건**을 잰다 — "conf가 정보를 갖기 시작하는 순간". 그때가 min_conf를
다시 논할 시점이고, 그전에는 논할 필요가 없다.

────────────────────────────────────────────────────────────────────────────
지키려는 불변식
────────────────────────────────────────────────────────────────────────────
(A) **퇴역 호라이즌 30m을 제외한다.** 296차가 앙상블·게이트에서 퇴역시켰는데
    `predictions`에는 계속 쌓인다. 실측으로 `conf>=0.60` 구간의 88%가 30m이라,
    포함하면 퇴역 모델이 판정을 끌고 간다.

(B) **효과크기 AND 일자단위를 함께 요구한다.** 둘 중 하나만으로 SUPPORTS_HYP가
    되면 안 된다. 0804에 pooled z=-4.95가 일자단위로는 p=0.42였던(표본 56%가
    하루) 전례를 그대로 겪었다.

(C) **채널이 REJECTS_HYP에 영구히 갇히면 안 된다.** 판별력이 실제로 나타났을 때
    반드시 반응해야 한다 — 그러지 못하면 이 채널은 있으나 마나다. 아래
    `test_gate_can_actually_fire`가 합성 데이터로 두 게이트 성분이 모두 발화
    가능함을 확인한다(**위음성 방지**).

(D) **임계는 검출력에서 유도된 값이어야 한다.** 임의 상수면 나중에 아무나 바꾼다.

실행: python tests/test_427_conf_discrimination.py   (COM/브로커 불필요)
"""
import io
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _mod():
    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    import importlib
    return importlib.import_module("generate_validation_campaign_report")


# ══════════════ 사전등록 ══════════════

def test_channel_registered():
    from config.settings import VALIDATION_CAMPAIGN as VC
    cr = VC.get("conf_discrimination_watch")
    check("[39] 채널이 사전등록돼 있다", isinstance(cr, dict))
    if not isinstance(cr, dict):
        return
    need = ("alpha", "min_positions", "min_days", "ens_gap_min",
            "min_predictions", "model_gap_min_pp", "exclude_horizons")
    miss = [k for k in need if k not in cr]
    check("필수 키 전부 존재 (%s)" % (miss or "없음"), not miss)
    check("(A) 30m이 제외 목록에 있다", "30m" in cr.get("exclude_horizons", []))
    check("(D) min_days >= 6 (425차와 동일 수학 - n=5는 최소 p=0.0625)",
          int(cr.get("min_days", 0)) >= 6)


def test_thresholds_derive_from_power():
    """(D) 임계가 검출력에서 유도된 값인가 - 임의 상수 금지."""
    from config.settings import VALIDATION_CAMPAIGN as VC
    cr = VC["conf_discrimination_watch"]
    # 모델축: n=14,770 절반분할 격차 SE = sqrt(2*p*(1-p)/half), p=1/3
    half = 14770 // 2
    se_pp = math.sqrt(2 * (1 / 3.0) * (2 / 3.0) / half) * 100
    floor_pp = 1.96 * se_pp
    check("(D) 모델축 검출하한 ~1.52%%p 재현 (계산 %.2f)" % floor_pp,
          abs(floor_pp - 1.52) < 0.05)
    check("(D) model_gap_min_pp가 검출하한의 2배 이상 (%.1f >= %.2f)" % (
              float(cr["model_gap_min_pp"]), 2 * floor_pp),
          float(cr["model_gap_min_pp"]) >= 2 * floor_pp)
    # 앙상블축: 진입 conf sd=0.0556 기준 Cohen d
    d = float(cr["ens_gap_min"]) / 0.0556
    check("(D) ens_gap_min이 Cohen d 0.4~0.6 구간 (d=%.2f)" % d, 0.4 <= d <= 0.6)


# ══════════════ _split_half_gap 역학 ══════════════

def test_split_half_gap():
    m = _mod()
    check("표본 4건 미만이면 None", m._split_half_gap([(0.4, 1), (0.5, 0)]) is None)
    # 완전 판별: 낮은 conf 전부 오답, 높은 conf 전부 정답
    perfect = [(0.1, 0), (0.2, 0), (0.8, 1), (0.9, 1)]
    g = m._split_half_gap(perfect)
    check("완전 판별 시 격차 +100%p", g and abs(g["gap_pp"] - 100.0) < 1e-6)
    # 무판별
    flat = [(0.1, 1), (0.2, 0), (0.8, 1), (0.9, 0)]
    g2 = m._split_half_gap(flat)
    check("무판별 시 격차 0%p", g2 and abs(g2["gap_pp"]) < 1e-6)
    # 역판별(높은 conf가 더 나쁨)
    inv = [(0.1, 1), (0.2, 1), (0.8, 0), (0.9, 0)]
    g3 = m._split_half_gap(inv)
    check("역판별은 음수 격차", g3 and g3["gap_pp"] < 0)
    # 홀수 표본
    g4 = m._split_half_gap([(0.1, 0), (0.2, 0), (0.5, 1), (0.8, 1), (0.9, 1)])
    check("홀수 표본에서도 죽지 않는다", g4 is not None and g4["n"] == 5)


# ══════════════ (C) 위음성 방지 — 게이트가 발화 가능한가 ══════════════

def test_gate_can_actually_fire():
    """판별력이 **실제로 나타났을 때** 두 게이트 성분이 다 발화하는가.

    이 테스트가 없으면 채널이 버그로 영구 REJECTS_HYP에 갇혀도 알 수 없다 —
    "판별력 없음"과 "탐지 불능"이 같은 출력을 내기 때문이다.
    """
    m = _mod()
    from config.settings import VALIDATION_CAMPAIGN as VC
    cr = VC["conf_discrimination_watch"]

    # 성분1: 효과크기 — 상위절반이 하위절반보다 임계 이상 잘 맞히는 합성 표본
    #        하위 200건 25% 적중 / 상위 200건 45% 적중 → 격차 20%p
    synth = [(0.30, 1 if i < 50 else 0) for i in range(200)]
    synth += [(0.60, 1 if i < 90 else 0) for i in range(200)]
    g = m._split_half_gap(synth)
    check("(C) 합성 판별표본에서 격차가 임계를 넘는다 (%.1f%%p >= %.1f)" % (
              g["gap_pp"], float(cr["model_gap_min_pp"])),
          g and g["gap_pp"] >= float(cr["model_gap_min_pp"]))

    # 성분2: 일자단위 — 전 거래일 양수면 유의해져야 한다
    day_gaps = [5.0, 8.0, 3.5, 6.2, 4.1, 7.7, 2.9]   # 7일 전부 양수
    s = m._paired_day_summary(day_gaps, float(cr["alpha"]))
    check("(C) 7일 전부 양수면 일자단위가 유의해진다 (p=%s)" % s.get("sign_p"),
          s.get("significant") is True)

    # 두 성분이 다 참이면 model_hit이 True가 되는 구조여야 한다
    model_hit = (g["gap_pp"] >= float(cr["model_gap_min_pp"])) and s["significant"]
    check("(C) 두 성분이 다 참 → SUPPORTS_HYP 조건 성립", model_hit is True)

    # (B) 한쪽만으로는 안 된다 — 효과크기는 크지만 일자단위가 흩어진 경우
    mixed = m._paired_day_summary([9.0, -8.0, 7.0, -6.0, 5.0, -4.0, 3.0],
                                  float(cr["alpha"]))
    check("(B) 효과크기만 크고 일자가 흩어지면 유의하지 않다",
          mixed.get("significant") is False)


# ══════════════ 실 DB 판정 ══════════════

def test_eval_current_state():
    m = _mod()
    out = m.eval_conf_discrimination_watch()
    check("판정이 dict를 반환한다", isinstance(out, dict) and "verdict" in out)
    check("두 축이 모두 보고된다",
          set(("model", "ensemble")) <= set((out.get("axes") or {}).keys()))
    mb = (out.get("axes") or {}).get("model") or {}
    eb = (out.get("axes") or {}).get("ensemble") or {}
    check("(A) 30m 제외가 실제로 걸렸다 (%s건)" % out.get("n_pred_excluded"),
          int(out.get("n_pred_excluded", 0)) > 0)
    check("(A) 제외 목록이 metrics에 남는다",
          "30m" in (out.get("excluded_horizons") or []))
    # [MW0601 488차 재설계] 종전은 427차 실측값 5개(격차 +0.15%p·-0.0008·n=100·
    # 승63/패37)와 `verdict == REJECTS_HYP`·`hit == False`를 그대로 핀했다.
    # 캠페인 시작 고정(2026-07-05) 누적이라 표본이 늘면 판정식이 멀쩡해도 깨졌고
    # (08-23 실측 n=166·승104/패62), 무엇보다 판별력이 **실제로 나타나는 날** —
    # 이 채널의 존재 이유가 실현되는 바로 그 순간 — 테스트가 FAIL을 낸다.
    # (C) 위음성 방지와 같은 취지로, 핀 대신 ② 정합·③ 단조·④ 매핑을 건다.
    from config.settings import VALIDATION_CAMPAIGN as _VC
    cr = _VC["conf_discrimination_watch"]
    check("(②) 승 + 패 == 앙상블축 n (%s+%s==%s)"
          % (eb.get("n_win"), eb.get("n_loss"), eb.get("n")),
          int(eb.get("n_win") or 0) + int(eb.get("n_loss") or 0)
          == int(eb.get("n") or -1))
    check("(③) 모델축 표본이 427차 하한(14,770) 이상 (%s) - 줄면 predictions "
          "보존정책이 캠페인 창을 침범한 것" % mb.get("n"),
          int(mb.get("n") or 0) >= 14770)
    check("(③) 앙상블축 표본이 427차 하한(100) 이상 (%s)" % eb.get("n"),
          int(eb.get("n") or 0) >= 100)
    check("(③) 승/패가 427차 하한(63/37) 이상 (%s/%s)"
          % (eb.get("n_win"), eb.get("n_loss")),
          int(eb.get("n_win") or 0) >= 63 and int(eb.get("n_loss") or 0) >= 37)
    check("앙상블축 Cohen d가 보고된다", "cohen_d" in eb)
    check("두 축 다 일자 층화 결과를 갖는다",
          (mb.get("stratified") or {}).get("sign_p") is not None
          and (eb.get("stratified") or {}).get("sign_p") is not None)
    # (④) hit 성분과 verdict를 사전등록 임계로 재계산해 대조한다 — 판정식 표류 감지.
    _model_ready = int(mb.get("n") or 0) >= int(cr["min_predictions"])
    _ens_ready = (int(eb.get("n") or 0) >= int(cr["min_positions"])
                  and (eb.get("stratified") or {}).get("paired_days", 0)
                  >= int(cr["min_days"]))
    _exp_mh = bool(_model_ready
                   and float(mb.get("gap_pp") or 0.0) >= float(cr["model_gap_min_pp"])
                   and (mb.get("stratified") or {}).get("significant"))
    _exp_eh = bool(_ens_ready
                   and float(eb.get("gap") or 0.0) >= float(cr["ens_gap_min"])
                   and (eb.get("stratified") or {}).get("significant"))
    check("(④) model_hit이 재계산과 일치 (%s)" % out.get("model_hit"),
          bool(out.get("model_hit")) == _exp_mh)
    check("(④) ens_hit이 재계산과 일치 (%s)" % out.get("ens_hit"),
          bool(out.get("ens_hit")) == _exp_eh)
    if not _model_ready and not _ens_ready:
        check("(④) 두 축 다 미성숙 → INSUFFICIENT",
              out.get("verdict") == "INSUFFICIENT")
    else:
        check("(④) verdict 매핑 - SUPPORTS ↔ (model_hit OR ens_hit)",
              out.get("verdict") ==
              ("SUPPORTS_HYP" if (_exp_mh or _exp_eh) else "REJECTS_HYP"))


def test_entry_decision_join():
    """[427차 후속] 진입↔결정 조인 — 분 단위 정확 조인은 19%를 잃는다.

    체결 확인이 `T+1:00~:09`에 도착하면 `trades.entry_ts`가 결정 분보다 1분 뒤가
    된다. 초판은 `entry_ts[:16] == ts[:16]`이라 그 19건을 통째로 잃고 매칭률
    81%로 보고했다 — 데이터가 없는 게 아니라 **키가 어긋난 것**이었다.
    """
    m = _mod()
    pairs, unmatched = m._entry_decision_pairs("2026-07-05 00:00:00")
    check("매칭 쌍이 반환된다", len(pairs) > 0)
    offs = {}
    for _e, _d, o in pairs:
        offs[o] = offs.get(o, 0) + 1
    # [488차 재설계] 절대 건수 핀(0분 81 / -1분 19, 427차 실측)은 고정 시작 누적이라
    # 표본이 늘면 깨진다(08-23 실측 81/85 — -1분이 신규 증가분을 전부 흡수했다).
    # 단조 하한으로 교체 — 내려가면 조인 키가 바뀐 것이다.
    check("(③) 오프셋 0분이 427차 하한(81건) 이상 (%s건)" % offs.get(0, 0),
          offs.get(0, 0) >= 81)
    check("(③) 오프셋 -1분이 427차 하한(19건) 이상 (%s건) - 분 경계를 넘은 체결"
          % offs.get(-1, 0), offs.get(-1, 0) >= 19)
    check("오프셋은 0 / -1 두 종류뿐", set(offs.keys()) <= set((0, -1)))
    check("미매칭 0건 - 전수 매칭된다", len(unmatched) == 0)
    check("결정행에 direction이 실려 있다 (방향 일치 검사의 전제)",
          all(d["direction"] is not None for _e, d, _o in pairs))


def test_integrity_surfaced():
    """무결성 지표를 숨기지 않는가 — 매칭률·오프셋 분포."""
    m = _mod()
    out = m.eval_conf_discrimination_watch()
    for k in ("n_positions_total", "n_matched", "n_unmatched",
              "match_rate", "unmatched_days", "join_offset_min"):
        if k not in out:
            check("무결성 지표 %s가 보고된다" % k, False)
            return
    check("무결성 지표 6종이 전부 보고된다", True)
    # [488차 재설계] "매칭률 100%"는 현재 실측이지 설계 보장이 아니다 — 미래에
    # 정당하게 100% 아래로 내려갈 수 있고(결정행 유실 등), 그때는 eval이 지표로
    # 보고하는 것이 옳지 테스트가 죽는 것이 옳지 않다. 정의 정합만 건다.
    _tot = int(out.get("n_positions_total") or 0)
    _mat = int(out.get("n_matched") or 0)
    check("(②) match_rate == n_matched / n_positions_total (%.4f)"
          % float(out.get("match_rate") or 0),
          _tot > 0 and abs(float(out["match_rate"])
                           - round(_mat / float(_tot), 4)) < 1e-9)
    check("(②) 매칭 + 미매칭이 전체를 넘지 않는다",
          _mat + int(out.get("n_unmatched") or 0) <= _tot)
    check("오프셋 분포가 남는다 (-1분 비중이 곧 체결지연 신호)",
          "-1" in (out.get("join_offset_min") or {}))


def test_recommendation_names_the_blocker():
    """권고가 '왜 지금 min_conf를 만지면 안 되는가'를 말하는가."""
    m = _mod()
    rec = m.eval_conf_discrimination_watch().get("recommendation") or ""
    check("권고에 'min_conf 조정은 무의미' 취지가 있다", "무의미" in rec)
    check("권고가 선행조건(§P1)을 지목한다", "P1" in rec)
    check("권고가 0804 스윕 실측을 근거로 든다", "62~63" in rec or "63.0" in rec)


def test_renders_in_report():
    m = _mod()
    md, metrics = m.build_report(28)
    check("metrics에 채널이 실린다", "conf_discrimination_watch" in metrics)
    check("요약표에 [39] 행이 있다", "| [39] confidence 판별력" in md)
    check("상세섹션이 있다", "## [39] confidence 판별력" in md)
    check("0804 스윕 실측표가 렌더된다", "407,558" in md)
    check("30m 제외 경고가 렌더된다", "88%가 30m" in md)
    check("무결성 경고가 렌더된다", "매칭률" in md or "매칭되지 않는다" in md)


if __name__ == "__main__":
    print("=" * 72)
    print("[MW0602 427차] [39] confidence 판별력 감시 채널 회귀 테스트")
    print("=" * 72)
    for fn in (
        test_channel_registered,
        test_thresholds_derive_from_power,
        test_split_half_gap,
        test_gate_can_actually_fire,
        test_eval_current_state,
        test_entry_decision_join,
        test_integrity_surfaced,
        test_recommendation_names_the_blocker,
        test_renders_in_report,
    ):
        print("\n-- %s" % fn.__name__)
        fn()
    print("\n" + "=" * 72)
    if FAILURES:
        print("실패 %d건:" % len(FAILURES))
        for f in FAILURES:
            print("  - %s" % f)
        sys.exit(1)
    print("전부 통과")

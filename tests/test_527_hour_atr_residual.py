# -*- coding: utf-8 -*-
"""[MW0602 526차 후속6] P-1 [51-R] 시간대×ATR 층 잔여 · [58] 13:00~13:30 섀도 회귀 고정.

배경 — O-69(13시대 진입 손실 집중) 조기 판정(2026-09-03, 사용자 지시)
--------------------------------------------------------------------
20거래일 실측에서 13시대 44포지션 −1,298,472원 · 12거래일 중 11일 음수
(일자 부호검정 p=0.0063)였는데, **ATR 층화 후 그 열위가 사라졌다**
(층 내 일자내 순열 p=0.57). 13시는 진입시점 ATR 최저(평균 1.44)이고
`ATR<1.5` 진입 비중이 최고(27/44=61%, 09~10h는 0/48)여서 **"13시"가
"저변동 진입"의 대리변수**였다. 모델 적중률·시장 효율에는 시간대 차이가 없었다.

이 파일이 고정하는 불변식
------------------------
1. 층화 잔여 검정이 **교락을 실제로 흡수한다** — 시간대 효과가 전부 ATR로 설명되면
   `p_withinday`는 작아도 `p_withinday_atr`은 유의하지 않아야 한다. 이 성질이 깨지면
   O-69류 관찰이 매주 "시간대 고유 효과"로 오독된다.
2. 반대로 **층 안에 진짜 시간대 효과가 있으면 잡아낸다** — 그러지 못하면 계측이
   죽은 채널이 된다(FP-CRITICAL 2개월 PSI=0.0 계열).
3. 얇은 셀은 `INSUFFICIENT`다. **0이 아니다**(계측 4원칙 ② 미측정≠0).
4. 탈락 건수가 보인다(계측 4원칙 ③ 탈락 가시화).
5. [58] FAIL 조건에서 **ATR 층화 잔여(cond4)가 빠지지 않는다** — 빠지면 이 채널은
   O-69가 기각한 바로 그 근거로 진입 금지를 정당화하게 된다.
6. **라이브가 무변경이다** — `ZONE_ENTRY_BAN_ENFORCE=False` 유지 · `TIME_ZONES`에
   승격용 존(`LUNCH_RECOVERY_EARLY`)이 아직 없다. 섀도는 섀도여야 한다.
7. [51] 본판정은 손대지 않았다 — `eval_profit_geometry_lowvol_watch` 안에
   `hour_residual`이 등장하면 판정식에 섞인 것이다(§9-4 검증 시계).
8. 사전등록 상수 고정 — 창 `13:00~13:30` · 판정창 `2026-09-04` · 층 경계
   `(1.25,1.5,2.0,2.6)`. **관측에서 역산하지 않았다**는 근거는 settings 주석에 있다.
9. 순열검정이 재현된다(같은 seed → 같은 p).

실행:
    "C:\\Users\\pc1\\anaconda3\\envs\\py37_32\\python.exe" tests/test_527_hour_atr_residual.py
    (pytest는 두 conda env 모두에 없다 — 파일 하단 러너로 돌린다)
"""
import inspect
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GEN = os.path.join(_ROOT, "scripts", "generate_validation_campaign_report.py")


def _R():
    import scripts.generate_validation_campaign_report as R
    return R


def _src():
    with io.open(_GEN, encoding="utf-8") as f:
        return f.read()


_CFG = {"strata_edges": (1.5,), "alpha": 0.05, "min_positions_per_cell": 10,
        "min_days_per_cell": 5, "permutations": 300, "seed": 462}


def _rows_absorbed():
    """시간대 효과가 **전부 ATR로 설명되는** 합성 표본.

    층 안에서는 손익이 상수라 시간대 차이가 정확히 0이다. 그런데 13시에는 저변동
    (나쁜) 포지션이 몰려 있어 층을 무시하면 13시가 열위로 보인다 — 0903 실측의
    구조를 그대로 축소한 것이다.
    """
    rows = []
    for i in range(12):
        day = "2026-08-%02d" % (i + 3)
        for _ in range(3):                       # 13시 · 저변동 · 나쁘다
            rows.append({"day": day, "hm": "13:10", "hour": "13",
                         "atr": 1.1, "pnl": -30000.0, "pts_per_ct": -1.0})
        rows.append({"day": day, "hm": "13:40", "hour": "13",              # 13시 · 고변동
                     "atr": 2.2, "pnl": 10000.0, "pts_per_ct": 0.4})
        rows.append({"day": day, "hm": "11:10", "hour": "11",              # 11시 · 저변동
                     "atr": 1.1, "pnl": -30000.0, "pts_per_ct": -1.0})
        for _ in range(3):                       # 11시 · 고변동 · 좋다
            rows.append({"day": day, "hm": "11:40", "hour": "11",
                         "atr": 2.2, "pnl": 10000.0, "pts_per_ct": 0.4})
    return rows


def _rows_true_effect():
    """층 **안에서도** 13시가 열위인 합성 표본 — 진짜 시간대 효과."""
    rows = []
    for i in range(12):
        day = "2026-08-%02d" % (i + 3)
        for atr, bad, good in ((1.1, -30000.0, -10000.0), (2.2, -5000.0, 15000.0)):
            for _ in range(2):
                rows.append({"day": day, "hm": "13:10", "hour": "13",
                             "atr": atr, "pnl": bad, "pts_per_ct": -1.0})
            for _ in range(2):
                rows.append({"day": day, "hm": "11:10", "hour": "11",
                             "atr": atr, "pnl": good, "pts_per_ct": 0.4})
    return rows


# ── 1. 교락 흡수 ─────────────────────────────────────────────────────────────

def test_1_hour_effect_absorbed_by_atr():
    """시간대 효과가 ATR로 설명되면 `p_withinday`는 작고 `p_withinday_atr`은 크다.

    이 대비가 [51-R]의 존재 이유다 — 0903 실측 13시대가 0.091 → 0.57이었다.
    """
    out = _R()._hour_atr_residual(_rows_absorbed(), _CFG)
    e = out["by_hour"]["13"]
    assert e["p_withinday"] is not None and e["p_withinday"] < 0.05, (
        "층을 무시하면 13시가 열위로 보여야 한다 (실측 구조 재현): %s" % e["p_withinday"])
    assert e["p_withinday_atr"] >= 0.05, (
        "ATR 층화 후에는 유의하지 않아야 한다 — 교락 흡수 실패: %s" % e["p_withinday_atr"])
    assert e["escalate_candidate"] is False, "흡수된 효과를 승격 후보로 올리면 안 된다"


# ── 2. 진짜 효과 탐지 ────────────────────────────────────────────────────────

def test_2_true_within_stratum_effect_detected():
    """층 안에 진짜 시간대 효과가 있으면 잡아낸다 (죽은 계측 방지)."""
    out = _R()._hour_atr_residual(_rows_true_effect(), _CFG)
    e = out["by_hour"]["13"]
    assert e["p_withinday_atr"] < 0.05, (
        "층 내 진짜 열위를 못 잡았다 — 계측이 죽었다: %s" % e["p_withinday_atr"])
    assert e["sign_p"] < 0.05, "일별 순손익 부호검정도 유의해야 한다: %s" % e["sign_p"]


# ── 3. 얇은 셀 = INSUFFICIENT (계측 4원칙 ②) ────────────────────────────────

def test_3_thin_cells_marked_insufficient_not_zero():
    """미달 셀은 `INSUFFICIENT`로 표기된다 — 0으로 찍으면 '측정했더니 0'과 섞인다."""
    rows = _rows_absorbed()[:6]          # 2일치 미만 · 셀 n<10
    out = _R()._hour_atr_residual(rows, _CFG)
    assert out["cells"], "셀이 하나도 안 나왔다"
    assert all(c["status"] == "INSUFFICIENT" for c in out["cells"]), (
        "얇은 셀이 OK로 찍혔다: %s" % out["cells"])
    for c in out["cells"]:
        assert c["n"] > 0, "INSUFFICIENT 셀도 n을 보여야 한다(미측정≠0)"


# ── 4. 탈락 가시화 (계측 4원칙 ③) ───────────────────────────────────────────

def test_4_dropped_counts_visible():
    """`_entry_atr_rows`가 탈락 사유별 건수를 돌려준다."""
    rows, dropped = _R()._entry_atr_rows()
    for k in ("total_positions", "no_atr", "bad_ts"):
        assert k in dropped, "탈락 카운터 누락: %s (계측 4원칙 ③)" % k
    assert dropped["total_positions"] >= len(rows), (
        "총 포지션 수가 산출 행보다 작다 — 카운터가 틀렸다")
    if dropped["total_positions"] == 0:
        print("    (SKIP 상세검증: trades.db 표본 0 — CI/신규 PC)")
    else:
        assert len(rows) + dropped["no_atr"] + dropped["bad_ts"] == \
            dropped["total_positions"], "탈락 합이 총계와 안 맞는다"


# ── 5. [58] FAIL 조건에 ATR 잔여가 남아 있다 ────────────────────────────────

def test_5_channel58_fail_requires_atr_residual():
    """FAIL 4조건에서 cond4(ATR 층화 잔여)가 빠지면 O-69가 기각한 근거로 금지하게 된다."""
    src = inspect.getsource(_R().eval_lunch_early_entry_ban_shadow)
    assert "cond2 and cond3 and cond4" in src, (
        "[58] FAIL 조건 결합이 바뀌었다 — 4조건 전부 필요하다")
    assert "require_atr_residual" in src, "ATR 잔여 조건 키가 사라졌다"
    assert 'p_withinday_atr' in src, "층화 잔여 p를 읽지 않는다 — 층 무시 판정으로 퇴화"


# ── 6. 라이브 무변경 (섀도는 섀도다) ────────────────────────────────────────

def test_6_live_wiring_untouched():
    """집행 플래그와 존 정의가 그대로다 — 이 커밋은 매매 정책을 바꾸지 않았다."""
    from config.settings import ZONE_ENTRY_BAN_ENFORCE, TIME_ZONES
    assert ZONE_ENTRY_BAN_ENFORCE is False, (
        "[58]은 섀도다 — ZONE_ENTRY_BAN_ENFORCE를 켜면 이 테스트가 막는다")
    assert "LUNCH_RECOVERY_EARLY" not in TIME_ZONES, (
        "승격용 존이 라우터에 들어왔다 — 승격은 [58] 판정 후 주간회의 소관이며 "
        "ZONE_MIN_CONF·C_AUTO_EXP_ZONES·main.py:_trend_mc_zones 세 표 동반 추가가 조건이다")
    assert TIME_ZONES.get("LUNCH_RECOVERY") == ("13:00", "14:00"), (
        "LUNCH_RECOVERY 정의가 바뀌었다 — [58] 코호트 해석이 달라진다")


# ── 7. [51] 본판정 불변 ─────────────────────────────────────────────────────

def test_7_channel51_judgment_untouched():
    """[51] 판정식에 `hour_residual`이 섞이면 안 된다 — 부속 관측은 별 함수다."""
    src = inspect.getsource(_R().eval_profit_geometry_lowvol_watch)
    assert "hour_residual" not in src, (
        "[51] 본판정 함수가 부속 관측을 참조한다 — 판정 무영향 원칙 위반")
    from config.settings import VALIDATION_CAMPAIGN as V
    cr = V["profit_geometry_lowvol_watch"]
    assert cr["atr_split_pt"] == 2.6, "[51] 분할선이 바뀌었다(§9-4 검증 시계 리셋)"
    assert cr["profit_atr_ratio_gap_min"] == 0.25, "[51] 합격선이 바뀌었다"
    assert cr["min_samples_per_bucket"] == 25 and cr["min_days"] == 10


# ── 8. 사전등록 상수 고정 ───────────────────────────────────────────────────

def test_8_preregistered_constants_frozen():
    """창·판정창·층 경계는 사후 변경 금지 대상이다."""
    from config.settings import VALIDATION_CAMPAIGN as V
    c58 = V["lunch_early_entry_ban_shadow"]
    assert tuple(c58["window"]) == ("13:00", "13:30"), "창이 바뀌었다(사후탐색 창 — 고정)"
    assert c58["start_date"] == "2026-09-04", (
        "판정 창 시작일이 바뀌었다 — 그 이전은 가설 생성 구간이다")
    assert c58["min_samples"] == 20 and c58["min_days"] == 10 and c58["alpha"] == 0.05
    assert c58["require_atr_residual"] is True
    hr = V["profit_geometry_lowvol_watch"]["hour_residual"]
    assert tuple(hr["strata_edges"]) == (1.25, 1.5, 2.0, 2.6), (
        "층 경계가 바뀌었다 — 1.25/1.5/2.0은 ATR_MIN_ENTRY 배수, 2.6은 [51] 분할선이다")
    assert hr["consecutive_weeks_required"] == 2, "단주 관측으로 승격하게 된다"
    from config.settings import ATR_MIN_ENTRY
    assert ATR_MIN_ENTRY == 1.0, (
        "ATR 진입 하한이 바뀌었다 — 층 경계의 앵커이므로 주석을 함께 갱신할 것")


# ── 9. 재현성 · 요약행 유일성 ───────────────────────────────────────────────

def test_9_permutation_deterministic_and_row_unique():
    """같은 seed → 같은 p. 그리고 [58] 요약행 번호가 중복되지 않는다(487차 불변식)."""
    rows = _rows_true_effect()
    a = _R()._hour_atr_residual(rows, _CFG)["by_hour"]["13"]["p_withinday_atr"]
    b = _R()._hour_atr_residual(_rows_true_effect(), _CFG)["by_hour"]["13"]["p_withinday_atr"]
    assert a == b, "순열검정이 재현되지 않는다 — seed 고정이 풀렸다"
    src = _src()
    nums = re.findall(r'L\.append\("\| \[(\d+)\]', src)
    nums += re.findall(r"_row_462\((\d+),", src)
    dupes = sorted({n for n in nums if nums.count(n) > 1})
    assert not dupes, "요약표 채널 번호 중복: %s" % dupes
    assert "_row_462(58," in src, "[58] 요약행이 없다"


if __name__ == "__main__":
    fns = [(n, f) for n, f in sorted(globals().items())
           if n.startswith("test_") and callable(f)]
    ok = fail = 0
    for name, fn in fns:
        try:
            fn()
            print("  PASS %s" % name)
            ok += 1
        except Exception as e:
            print("  FAIL %s -> %s: %s" % (name, type(e).__name__, e))
            fail += 1
    print("\n%d passed, %d failed (of %d)" % (ok, fail, len(fns)))
    sys.exit(1 if fail else 0)

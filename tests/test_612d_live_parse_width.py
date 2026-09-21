# tests/test_612d_live_parse_width.py
"""[MW0601 612차 후속4] 라이브 파싱 폭과 소비 열의 어긋남 회귀 가드.

## 무슨 일이 있었나

612차 후속2 가 `CpSvrNew7221` 열 30/31/32(선물 순매수 **금액**)를 쓰기 시작했다.
그런데 `_probe_investor_tr` 의 **상시(라이브) 파싱 폭은 15열**이었다 —
전 64열은 세션당 progid별 **첫 호출(RAW 덤프)** 에서만 읽는다(메인 스레드
점유 때문에 일부러 좁혀 둔 것).

결과: 라이브에서 `r.get(30, 0)` 이 **0 을 만들어냈고**, 대시보드
「선물 순매수 (억원)」 3칸이 하루 종일 `0` 으로 떴다(2026-09-21 15:03 실측
`[CybosInvestorRaw] … amt_mn={}`).

🔴 **오프라인 검증은 통과했다.** RAW 덤프는 64열을 읽으므로 PROBE 로그 기반
분석에서는 값이 멀쩡히 보였다 — "덤프에는 있는데 라이브만 빈다"는 형태라
배선 테스트로도 안 잡혔다.

🔴 **`*_measured` 플래그도 못 막았다.** `net_amounts` 를 `r.get(col, 0)` 으로
무조건 채웠기 때문에 키는 항상 존재했고, 하류가 "키가 왔다 = 측정됐다"로 읽었다.
451차가 폐기한 「스키마 폴백으로 상수 0 을 정상 수집처럼 위장」과 같은 형태다.

## 이 파일이 고정하는 것

  1. 소비하는 열이 **상시 파싱 폭 안에** 있다
  2. 열이 없으면 **키를 만들지 않는다**(0 을 지어내지 않는다)
  3. 라이브 폭이 전 64열로 넓어지지 않았다(메인 스레드 점유 회귀 방지)
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 🔴 CLAUDE.md 537차 — **numpy import 보다 먼저** PATH 를 세운다.
#   늦게 부르면 소용없다(실측: 함수 안에서 부르면 여전히 프로세스가 즉사한다).
from utils.dll_bootstrap import ensure_conda_dll_path   # noqa: E402

ensure_conda_dll_path()

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_API = os.path.join(_ROOT, "collection", "cybos", "api_connector.py")


def _src():
    with open(_API, "r", encoding="utf-8") as f:
        return f.read()


def _live_fields(progid="CpSysDib.CpSvrNew7221"):
    from collection.cybos.api_connector import CybosAPI

    extra = CybosAPI._LIVE_EXTRA_FIELDS.get(progid, ())
    return set(range(15)) | set(extra)


def test_1_consumed_columns_are_inside_live_parse_width():
    """소비하는 열이 상시 파싱 폭 안에 있어야 한다 — 이게 이번 사고의 본체다."""
    fields = _live_fields()
    for col, what in ((2, "개인 순매수 계약"), (5, "외인 순매수 계약"),
                      (8, "기관 순매수 계약"), (30, "개인 순매수 금액"),
                      (31, "외인 순매수 금액"), (32, "기관 순매수 금액")):
        assert col in fields, (
            "열 %d(%s)를 소비하는데 라이브 파싱 폭 밖이다 — 라이브에서 0 이 된다. "
            "`CybosAPI._LIVE_EXTRA_FIELDS` 에 등록할 것" % (col, what)
        )


def test_2_columns_referenced_in_code_are_registered():
    """`r.get(N)` / `r[N]` 로 읽는 열이 전부 폭 안에 있는지 소스에서 역추적한다.

    사람이 등록을 잊는 것이 이번 결함이었으므로, **코드가 실제로 읽는 열**을
    기준으로 검사한다.
    """
    src = _src()
    body = src.split('if progid == "CpSysDib.CpSvrNew7221":', 1)[1]
    body = body.split("            else:", 1)[0]
    used = set()
    for m in re.finditer(r"r\.get\((\d+)\s*,|r\[(\d+)\]|\(\"[a-z]+\",\s*(\d+)\)", body):
        for g in m.groups():
            if g is not None:
                used.add(int(g))
    assert used, "7221 파싱부에서 읽는 열을 찾지 못했다 — 패턴이 바뀌었으면 이 테스트를 갱신할 것"
    missing = sorted(c for c in used if c not in _live_fields())
    assert not missing, (
        "코드가 읽지만 라이브 파싱 폭 밖인 열: %s — 라이브에서 조용히 0 이 된다" % missing
    )


def test_3_absent_column_yields_no_key_not_zero():
    """열이 없으면 키를 만들지 않는다 (계측 4원칙 ② · 451차)."""
    # 주석 속 언급은 설명이므로 코드 줄만 본다.
    code_only = "\n".join(
        ln for ln in _src().splitlines() if not ln.lstrip().startswith("#"))
    assert "r.get(30, 0)" not in code_only, (
        "`r.get(30, 0)` 이 되살아났다 — 열이 없을 때 0 을 지어내 "
        "`*_measured` 플래그가 True 로 위장된다"
    )
    assert "if _col in r:" in code_only, "열 존재 확인 분기가 사라졌다"


def test_4_absent_column_semantics():
    """파싱 규칙 자체를 재현해 고정한다."""
    def build(row):
        out = {}
        for k, col in (("individual", 30), ("foreign", 31), ("institution", 32)):
            if col in row:
                out[k] = int(row[col])
        return out

    assert build({30: "-51528", 31: "1294497", 32: "-1260062"}) == {
        "individual": -51528, "foreign": 1294497, "institution": -1260062}
    assert build({2: "-185", 5: "4654"}) == {}, "없는 열이 0 으로 만들어졌다"
    # 값이 진짜 0 인 것과 열이 없는 것은 달라야 한다
    assert build({30: "0"}) == {"individual": 0}


def test_5_live_width_did_not_widen_to_all_64():
    """전 64열을 매분 읽으면 메인 스레드를 점유한다 — 그래서 좁혀 둔 것이다."""
    fields = _live_fields()
    assert len(fields) <= 24, (
        "라이브 파싱 폭이 %d열로 넓어졌다. `_fetch_investor_data` 는 메인 스레드를 "
        "점유하며 500ms 초과 시 경고가 찍힌다 — 필요한 열만 등록할 것" % len(fields)
    )
    src = _src()
    assert "field_idx = tuple(range(64))" in src, "RAW 덤프 경로가 사라졌다"
    assert "field_limit = 64 if is_dump_call else 15" not in src, (
        "고정 폭 15 로 되돌아갔다"
    )


def test_6_dashboard_shows_wait_when_amount_unmeasured():
    """금액이 미측정이면 화면은 0 이 아니라 「대기」여야 한다."""
    dash = os.path.join(_ROOT, "dashboard", "main_dashboard.py")
    with open(dash, "r", encoding="utf-8") as f:
        src = f.read()
    assert '_fmt_eok(fi_amt) if _measured("foreign_futures_amt") else "대기"' in src


# ── [612차 후속5] 첫 호출(RAW 덤프) 경로는 세션당 1회라 테스트를 빠져나간다 ──

def test_7_probe_runs_on_both_dump_and_live_paths():
    """🔴 이 테스트가 있었다면 `field_limit` NameError 를 잡았다.

    612차 후속4 가 `field_limit` → `field_idx` 로 바꾸면서 RAW 덤프 **로그 줄**의
    참조 한 곳을 놓쳤다. 그 경로는 **세션당 progid별 첫 호출에서만** 타므로
    py_compile 도, 기존 어떤 테스트도 건드리지 않았다. 라이브에서는 재기동 직후
    첫 수급 호출이 통째로 실패하고(`futures investor TR 후보 없음`) 다음 60초
    틱까지 화면이 비었다.

    ⇒ 가짜 COM 객체로 **덤프 경로와 상시 경로를 모두** 실행한다.
    """
    import collection.cybos.api_connector as A

    class _Fake(object):
        def __init__(self):
            self.reads = 0

        def SetInputValue(self, *a):
            pass

        def BlockRequest(self):
            return 0

        def GetDibStatus(self):
            return 0

        def GetDibMsg1(self):
            return ""

        def GetHeaderValue(self, i):
            return "28" if i < 3 else ""

        def GetDataValue(self, fi, ri):
            self.reads += 1
            if ri > 4 or fi > 51:
                raise Exception("out of range")
            if ri == 2 and fi in (2, 5, 8):
                return {2: "-185", 5: "4654", 8: "-4531"}[fi]
            if ri == 2 and fi in (30, 31, 32):
                return {30: "-51528", 31: "1294497", 32: "-1260062"}[fi]
            return "0"

    fake = _Fake()
    orig_dispatch = A.Dispatch
    orig_done = A.CybosAPI._probe_dump_done
    A.Dispatch = lambda progid: fake
    A.CybosAPI._probe_dump_done = set()
    try:
        api = A.CybosAPI.__new__(A.CybosAPI)

        dump = api._probe_investor_tr("CpSysDib.CpSvrNew7221", [(0, 49)])
        assert dump is not None, "덤프 경로가 실패했다 — 첫 호출이 죽으면 재기동 직후가 빈다"
        assert dump["rows"][2].get(30) == "-51528"

        reads_dump = fake.reads
        fake.reads = 0
        live = api._probe_investor_tr("CpSysDib.CpSvrNew7221", [(0, 49)])
        assert live is not None, "상시 경로가 실패했다"
        assert live["rows"][2].get(31) == "1294497", (
            "상시 경로에서 금액 열이 안 읽힌다 — 612차 후속4 의 그 결함이다"
        )
        assert set(live["rows"][2]) == set(range(15)) | {30, 31, 32}
        assert fake.reads < reads_dump, (
            "상시 경로가 덤프만큼 읽는다 — 메인 스레드 점유가 늘어난다"
        )
    finally:
        A.Dispatch = orig_dispatch
        A.CybosAPI._probe_dump_done = orig_done


def test_8_code_error_is_not_labelled_as_api_failure():
    """코드 버그를 「dispatch/request failed」로 찍으면 브로커 탓으로 오진한다."""
    # `_probe_investor_tr` 의 핸들러만 본다 (파일 전체의 첫 except 가 아니다).
    src = _src()
    fn = src.split("def _probe_investor_tr", 1)[1]
    fn = fn.split("\n    def ", 1)[0]
    tail = fn.split("except Exception as exc:", 1)[1]
    assert "코드 오류" in tail, (
        "NameError 같은 파이썬 오류가 COM 실패와 같은 문구로 찍힌다 — "
        "612차 후속4 진단이 그것 때문에 한 번 우회했다"
    )
    assert "probe_log.error" in tail


def test_9_program_cards_wait_when_unsupported():
    """`arb` 는 0 으로 초기화돼 절대 None 이 아니다 — 그 조건으로는 「대기」가 안 뜬다."""
    dash = os.path.join(_ROOT, "dashboard", "main_dashboard.py")
    with open(dash, "r", encoding="utf-8") as f:
        src = f.read()
    assert "if prog_supported or arb is not None:" not in src, (
        "수집 실패 중에도 프로그램 카드에 0 이 뜬다(계측 4원칙 ②)"
    )
    assert "prog_supported = bool(div.get(\"program_supported\", False))" in src


def test_10_restart_holes_are_shortened():
    """재기동 직후 빈 구간을 줄이는 배선이 살아 있는가."""
    main = os.path.join(_ROOT, "main.py")
    with open(main, "r", encoding="utf-8") as f:
        src = f.read()
    assert "QTimer.singleShot(20_000, self._poll_option_chain)" in src, (
        "옵션 체인이 재기동 후 최대 5분간 「미수집」으로 남는다"
    )
    assert "QTimer.singleShot(8_000, self._poll_kospi200_index)" in src, (
        "VKOSPI·현물지수가 재기동 후 60초간 빈다"
    )
    assert "self._investor_retry_done" in src, "수급 첫 호출 실패 재시도가 없다"
    assert "self._investor_retry_done = False" in src, (
        "명시 초기화가 없다 — getattr 폴백은 계측 4원칙 ④ 위반"
    )


def test_11_panel_has_a_second_update_path():
    """🔴 분봉 파이프라인은 **15:09 에 정상 종료**한다 — 갱신 경로가 하나면 언다.

    실측(09-17 15:09:02 · 09-18 15:09:00 · 09-21 15:09:01) — 매일 같다.
    2026-09-21 에는 하필 그 직전 틱이 수집 실패 상태였고, 그 뒤 15:09:45 부터
    데이터가 정상이었는데도 화면은 하루 종일 「대기 / 0」으로 남았다.
    """
    main = os.path.join(_ROOT, "main.py")
    with open(main, "r", encoding="utf-8") as f:
        src = f.read()
    body = src.split("def _fetch_investor_data", 1)[1].split("\n    def ", 1)[0]
    assert "self.dashboard.update_divergence(" in body, (
        "수급 타이머가 패널을 갱신하지 않는다 — 15:09 이후 화면이 언다"
    )


def test_12_freshness_chip_ages_by_itself():
    """신선도 칩이 push 에 매달리면, 멈춘 순간의 「15초 전」이 영원히 남는다."""
    dash = os.path.join(_ROOT, "dashboard", "main_dashboard.py")
    with open(dash, "r", encoding="utf-8") as f:
        src = f.read()
    assert "def _render_age_chip" in src
    assert "_fut_fetch_epoch" in src, "절대시각 원점이 없다 — 나이를 다시 못 잰다"
    assert "self._age_timer.timeout.connect(self._render_age_chip)" in src, (
        "칩 자가 갱신 타이머가 없다"
    )
    inv = os.path.join(_ROOT, "collection", "cybos", "investor_data.py")
    with open(inv, "r", encoding="utf-8") as f:
        assert '"last_fetch_epoch"' in f.read(), (
            "get_panel_data 가 절대시각을 안 준다"
        )


def test_13_age_chip_thresholds():
    """칩 문구·임계 — **위젯 없이** 산식만 고정한다.

    ⚠ 원래는 `DivergencePanel` 을 실제로 띄워 검증하려 했는데, 이 환경의
      pytest 프로세스에서 그 위젯 구성이 **stderr 없이 프로세스를 죽인다**
      (실측 exit=127, `ensure_conda_dll_path()` 로도 안 잡힘). 죽는 테스트를
      스위트에 남기면 스위트 전체가 무력해진다(O-77 전례) — 그래서 산식만
      떼어 고정하고, 위젯 렌더는 별도 스모크로 확인했다.
      스모크 실측(2026-09-21): 15초 → "수급 15초 전" / 200초 → "수급 3분 20초 전"
      (주황) / 1800초 → "수급 30분 00초 전" (빨강) / 원점 None → "수급 ——",
      타이머 10000ms 가동.
    """
    def chip(age):
        if age is None:
            return "수급 ——", "muted"
        if age < 60:
            txt = "수급 %d초 전" % int(age)
        else:
            txt = "수급 %d분 %02d초 전" % (int(age // 60), int(age % 60))
        col = "red" if age > 600 else ("orange" if age > 180.0 else "muted")
        return txt, col

    assert chip(15) == ("수급 15초 전", "muted")
    assert chip(200) == ("수급 3분 20초 전", "orange")
    assert chip(1800) == ("수급 30분 00초 전", "red")
    assert chip(None)[0] == "수급 ——"
    # 경계
    assert chip(180)[1] == "muted" and chip(181)[1] == "orange"
    assert chip(600)[1] == "orange" and chip(601)[1] == "red"


def test_14_chip_render_matches_the_formula():
    """패널 구현이 위 산식과 같은 임계를 쓰는지 소스로 확인한다."""
    dash = os.path.join(_ROOT, "dashboard", "main_dashboard.py")
    with open(dash, "r", encoding="utf-8") as f:
        body = f.read().split("def _render_age_chip", 1)[1]
    body = body.split("\n    def ", 1)[0]
    assert "age > 180.0" in body, "stale 임계가 바뀌었다"
    assert "age > 600" in body, "「멈춤」 임계가 바뀌었다"
    assert '"수급 %d초 전"' in body and '"수급 %d분 %02d초 전"' in body

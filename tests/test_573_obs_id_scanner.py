# -*- coding: utf-8 -*-
"""[MW0602 573차] 관측 ID 채번 스캐너 — 「발급」과 「언급」을 가른다.

무엇을 막는 장치인가
--------------------
증거 수집기 §11 은 *"다음 `O-*` 는 이 번호부터 발급하라"* 를 매일 자동으로 알려
준다(494차 F-7). 그런데 그 최댓값을 `_obs_ids`(본문 전수 `\\bO-(\\d+)\\b`)로 세고
있었다. `dev_memory/NEXT_TODO.md` 에는 발급 항목만 있는 게 아니라

    - **다음 관측 ID는 `O-82`부터** (아직 발급 안 됨 — 예고)

같은 **예고 문구**가 매 세션 실린다. 예고를 발급으로 오인하면 다음 세션이 실제로는
비어 있는 번호를 건너뛴다.

🔴 **자기증폭한다.** 2026-09-16 장후 실측 — 실제 발급 최댓값은 `O-81` 인데 스캐너는
`O-83` 을 냈다. 전날 오탐(`O-82`)을 적은 리포트 문장이 그대로 `NEXT_TODO.md` 에
실려 **다음 날 최댓값을 한 칸 더 밀어 올렸기** 때문이다. 고치지 않으면 번호가 매일
하나씩 비어 간다.

⚠ 고칠 도구는 처음부터 있었다 — `_OBS_DEF_RE`(정의성 라벨 정규식)는 494차부터 이
  파일에 있었으나 **아무도 쓰지 않았다.** 493차 §⑤(*"이미 받고 있는데 안 보고 있는
  것"*) 계열이다.

이 파일이 하는 일
-----------------
1. 예고 문구를 **발급으로 세지 않는다**
2. 체크박스 머리의 정의성 라벨은 **표기 변형과 무관하게 센다**
3. 세지 않은 번호를 **밝힌다**(계측 4원칙 ③ 탈락 가시화)
4. 라벨 형식이 바뀌면 **조용히 물러서지 않는다**(계측 4원칙 ④ 폴백 가시화)
5. 이 절의 규약인 **오탐 금지**를 깨지 않는다

실행:
    pytest tests/test_573_obs_id_scanner.py
"""
import io
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS = os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check", "scripts")
for _p in (_ROOT, _SCRIPTS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import collect_evidence as CE  # noqa: E402

_COLLECTOR = os.path.join(_SCRIPTS, "collect_evidence.py")
_NEXT_TODO = os.path.join(_ROOT, "dev_memory", "NEXT_TODO.md")

#: 실제 `NEXT_TODO.md` 의 축약 재현 — 발급 2건 + 예고 문구 2줄.
#: 0916 장후가 마주친 바로 그 형태다.
_FIXTURE = u"""## 2026-09-16 (MW0602 573차 - 장후 일일 점검)

### 관측 예정
- [ ] **`O-80`** 프로세스 무응답 재발 여부 - 판정 2026-09-17
- [ ] **`O-81`** LONG/SHORT 방향별 승률 격차 표본 축적

### 갱신
- `O-81`(방향별 승률) - 오늘 데이터 1건 추가. 다음 관측 ID는 여전히 `O-82`부터.
- **다음 관측 ID는 `O-82`부터** (§11 스캐너가 낸 `O-83`은 오탐, 실제 최댓값 `O-81`)
"""


def _read(path):
    with io.open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _independent_issued_max(text):
    """테스트 자신의 오라클 — 구현을 구현으로 검사하지 않기 위해 따로 센다.

    체크박스 항목의 **첫 번째** `O-NN` 만 발급으로 본다.
    """
    best = None
    for line in text.splitlines():
        m = re.match(r"^\s*-\s*\[[ xX]\]\s*(?P<head>.*)$", line)
        if not m:
            continue
        m2 = re.search(r"O-(\d+)", m.group("head"))
        if not m2:
            continue
        n = int(m2.group(1))
        if best is None or n > best:
            best = n
    return best


# ── ① 예고 문구는 발급이 아니다 ──────────────────────────────────────────

def test_1_forecast_sentence_is_not_an_issuance():
    """`O-82`·`O-83` 은 「부터」라고 예고만 됐다. 세면 안 된다."""
    got = CE._obs_def_ids(_FIXTURE)
    assert got == set([80, 81]), got
    assert 82 not in got, "예고 문구(`O-82`부터)를 발급으로 셌다 - 573차 회귀"
    assert 83 not in got, "오탐을 적은 문장(`O-83`)을 발급으로 셌다 - 573차 회귀"


def test_2_checkbox_heads_are_counted_in_every_written_form():
    """표기가 흔들려도 발급은 발급이다(볼드/백틱/평문/체크됨/접미)."""
    text = u"\n".join([
        u"- [ ] **`O-90`** 백틱+볼드",
        u"- [x] **O-91** 볼드만",
        u"- [ ] `O-92` 백틱만",
        u"- [ ] O-93 평문",
        u"- [ ] **`O-94`** (0916) 접미 달림",
    ])
    got = CE._obs_def_ids(text)
    assert got == set([90, 91, 92, 93, 94]), got


def test_3_mention_only_numbers_are_disclosed(tmpdir):
    """탈락 가시화(계측 4원칙 ③) - 안 센 번호를 밝힌다.

    이 줄이 없으면 다음 세션이 *"왜 O-83 이 아니라 O-82 인가"* 를 매번 다시
    조사한다. 0916 장후가 실제로 그 조사에 한 절을 썼다.
    """
    root = str(tmpdir)
    os.makedirs(os.path.join(root, "dev_memory"))
    with io.open(os.path.join(root, "dev_memory", "NEXT_TODO.md"),
                 "w", encoding="utf-8") as f:
        f.write(_FIXTURE)

    r = CE.scan_obs_labels(root)
    assert r["basis"] == "def", r
    assert r["max"] == 81 and r["next"] == 82, r
    assert r["mentioned_only"] == [82, 83], r
    for n in r["mentioned_only"]:
        assert n > r["max"], "발급 최댓값 아래 번호를 탈락으로 보고했다"


def test_4_fallback_is_visible_when_label_format_changes(tmpdir):
    """폴백 가시화(계측 4원칙 ④) - 라벨 형식이 바뀌면 **말하고** 물러선다.

    정의성 라벨이 0건이면 `_OBS_DEF_RE` 가 낡은 것이다. 조용히 `next=None` 을
    내면 채번 안내가 사라진 줄도 모른다.
    """
    root = str(tmpdir)
    os.makedirs(os.path.join(root, "dev_memory"))
    with io.open(os.path.join(root, "dev_memory", "NEXT_TODO.md"),
                 "w", encoding="utf-8") as f:
        f.write(u"| ID | 대상 |\n|---|---|\n| O-70 | 표 형식으로 바뀌었다 |\n")

    r = CE.scan_obs_labels(root)
    assert r["basis"] == "mention-fallback", r
    assert r.get("fallback_reason"), "폴백 사유가 비었다 - 계측 4원칙 ④ 위반"
    assert r["max"] == 70 and r["next"] == 71, r


# ── ② 이 절의 규약: 오탐 금지 ────────────────────────────────────────────

def test_5_new_issuance_is_judged_against_prev_mentions_not_prev_labels():
    """🔴 오탐 금지 - 「신규 발급」은 직전 커밋에 **언급조차 없던** 번호뿐이다.

    예고로만 있던 `O-82` 가 오늘 체크박스로 정리되는 것은 **정상 발급**이지
    충돌이 아니다. 좁은 축끼리 빼면 그것까지 「이미 쓰인 번호로 발급」으로
    잡혀 늑대소년이 된다 - 이 절이 초안을 폐기하며 세운 규약을 정면으로
    어기게 된다.
    """
    src = _read(_COLLECTOR)
    assert 'out["new"] = sorted(now_ids - prev_any)' in src, (
        "신규 발급 판정이 넓은 축(prev_any)에서 떨어져 나갔다 - 오탐이 돌아온다")
    assert 'prev_any = _obs_ids(prev)' in src, (
        "넓은 축 자체가 사라졌다 - 오탐 방지의 기준선이 없어진다")


def test_6_max_is_no_longer_taken_from_the_broad_scan():
    """채번 최댓값이 다시 본문 전수로 돌아가지 않았는가."""
    src = _read(_COLLECTOR)
    assert 'now_def = _obs_def_ids(cur)' in src
    assert 'out["max"] = max(now_ids)' in src
    # 종전의 결함 형태가 그대로 살아 있으면 안 된다.
    # (`io.open(..., "r")` 는 개행을 `\n` 으로 정규화하므로 `\r` 을 쓰지 말 것 -
    #  CRLF 파일에서 조용히 통과하는 공허한 검사가 된다.)
    assert "    now_ids = _obs_ids(cur)\n    if now_ids:" not in src, (
        "573차 이전 코드가 되살아났다")


# ── ③ 라이브 회귀 + 비공허성 ────────────────────────────────────────────

def test_7_live_next_todo_is_scanned_on_the_issued_axis():
    """실제 `NEXT_TODO.md` - 독립 오라클과 발급 최댓값이 일치하는가."""
    if not os.path.exists(_NEXT_TODO):
        return
    r = CE.scan_obs_labels(_ROOT)
    oracle = _independent_issued_max(_read(_NEXT_TODO))
    assert r["basis"] == "def", r
    assert r["max"] == oracle, (r["max"], oracle)
    assert r["next"] == oracle + 1


def test_8_the_two_axes_actually_differ_here():
    """음성 대조 - 이 검사가 **헛돌지 않는다**는 증거.

    두 축이 늘 같은 값이면 위 테스트들은 아무것도 지키지 않는 셈이다.
    픽스처에서는 반드시 갈려야 한다(발급 81 vs 언급 83).
    """
    assert max(CE._obs_ids(_FIXTURE)) == 83
    assert max(CE._obs_def_ids(_FIXTURE)) == 81


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    import tempfile
    import shutil

    _fails = 0
    for _name, _fn in sorted(globals().items()):
        if not _name.startswith("test_") or not callable(_fn):
            continue
        _tmp = None
        try:
            if "tmpdir" in _fn.__code__.co_varnames[:_fn.__code__.co_argcount]:
                _tmp = tempfile.mkdtemp()
                _fn(_tmp)
            else:
                _fn()
            print("PASS %s" % _name)
        except Exception as e:
            _fails += 1
            print("FAIL %s: %s" % (_name, e))
        finally:
            if _tmp:
                shutil.rmtree(_tmp, ignore_errors=True)
    sys.exit(1 if _fails else 0)

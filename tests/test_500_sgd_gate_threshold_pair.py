# -*- coding: utf-8 -*-
"""[MW0602 500차] G-5 회귀 — 「임계 좌초」 다섯 번째 감시쌍(SGD 표본 게이트).

**무엇이 문제였나.** 임계 좌초 — *상수 임계가 실측 분포 위에 있어 그 아래 분기가
통째로 도달 불가가 되는 것* — 이 0826 에 **세 번째 사례**로 확인됐다(이상점 `1-13`).
앞의 둘은 각각 다른 세션이 **우연히** 발견했고 그 사이 걸린 시간이 3개월·6개월이다.

여기서 배선하는 것은 그 계통을 매일 자동으로 보이게 하는 다섯 번째 임계쌍이다.
`main.py` 의 `_min_conf_sgd = 0.52` 는 SGD 온라인 학습의 고신뢰 레이블 필터이며,
STEP 3 장중 재학습 조건 A(n≥20)·B(n≥15) 가 세는 표본 `n` 의 **유일한 입력 경로**다.
여기서 좌초하면 그 아래 두 분기가 함께 죽는다. 2026-08-26 실측 5m `max(conf)=0.4580`.

🔴 **임계를 바꾸지 않는다.** 완화는 학습 위생 정책이라 주간회의 소관이고
(`main.py:5849` 주석 · 490차 P0), 관측값에서 문턱을 역산하면 458차 D6 과 같은
사전등록 위반이다. 이 쌍이 하는 일은 *"매일 보이게 한다"* 까지다.

고정하는 불변식:

① 쌍이 등록돼 있고 **임계가 코드의 상수와 같다**(0.52). 문서만 고치면 죽은 계측이 된다.
② SQL 이 실제 DB 에서 돌고, 5m·방향성 예측만 센다.
③ **판정 무영향** — 어떤 캠페인 합격선·판정식도 건드리지 않는다.
④ `known` 이 붙어 있다 — 규명된 미도달을 매일 §11 적신호로 울리면 늑대소년이 된다.
⑤ 원인 축(conf)과 결과 축(n)이 **둘 다** 등록돼 있다.

실행:
    py37_32\\python.exe tests/test_500_sgd_gate_threshold_pair.py
"""
import datetime
import io
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_COLLECTOR = os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check",
                          "scripts", "collect_evidence.py")
FAILURES = []

PAIR = "SGD표본게이트(5m conf≥0.52)"
THRESHOLD = 0.52


def _collector():
    """수집기를 모듈로 로드한다 — 패키지가 아니라 스크립트라 경로 로드가 필요하다."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("_ce500", _COLLECTOR)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except ImportError:                                   # py2 계열 방어(미사용 경로)
        import imp
        return imp.load_source("_ce500", _COLLECTOR)


def _pairs():
    m = _collector()
    cfg = m.load_config(_ROOT)
    return m, cfg, (cfg.get("threshold_reachability") or {}).get("pairs") or {}


# ── ① 등록 + 임계가 코드 상수와 일치 ─────────────────────────────────────────
def test_pair_is_registered():
    _m, _cfg, pairs = _pairs()
    assert PAIR in pairs, "다섯 번째 임계쌍이 없다 — 등록된 것: %s" % list(pairs)
    assert abs(float(pairs[PAIR]["threshold"]) - THRESHOLD) < 1e-9, pairs[PAIR]["threshold"]


def test_threshold_matches_the_live_constant():
    """문서 임계가 코드 임계와 갈리면 계측이 조용히 엉뚱한 것을 잰다."""
    with io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8") as f:
        src = f.read()
    assert "_min_conf_sgd  = 0.52" in src or "_min_conf_sgd = 0.52" in src, \
        "main.py 의 SGD conf 게이트 상수를 못 찾았다 — 임계쌍을 재확인하라"


# ── ② SQL 이 실제 DB 에서 돈다 ────────────────────────────────────────────────
def test_sql_runs_and_filters_5m_directional():
    _m, _cfg, pairs = _pairs()
    spec = pairs[PAIR]
    assert spec.get("db") == "data/db/predictions.db", spec.get("db")
    sql = spec["sql"]
    assert "horizon = '5m'" in sql, sql
    assert "direction != 0" in sql, sql
    db = os.path.join(_ROOT, "data", "db", "predictions.db")
    if not os.path.exists(db):                            # 새 PC — 스키마만 검증
        return
    conn = sqlite3.connect(db)
    try:
        rows = conn.execute(sql, ("2026-08-12", "2026-08-26")).fetchall()
    finally:
        conn.close()
    assert isinstance(rows, list), rows
    for d, v in rows:
        assert len(str(d)) == 10, d
        assert 0.0 <= float(v) <= 1.0, (d, v)


def test_scanner_returns_a_verdict_for_the_pair():
    m, cfg, _pairs_ = _pairs()
    rows = m.scan_threshold_reachability(_ROOT, cfg, datetime.date(2026, 8, 26))
    hit = [r for r in rows if r["name"] == PAIR]
    assert len(hit) == 1, [r["name"] for r in rows]
    r = hit[0]
    assert r["verdict"] not in (None, ""), r
    # 판정 어휘는 기존 네 쌍과 같은 집합이어야 한다 — 새 어휘를 만들면 렌더가 깨진다.
    assert ("도달" in r["verdict"] or "표본없음" in r["verdict"]
            or "DB미접속" in r["verdict"] or "무기록" in r["verdict"]), r["verdict"]


# ── ③ 판정 무영향 ─────────────────────────────────────────────────────────────
def test_pair_does_not_touch_any_campaign_gate():
    _m, _cfg, pairs = _pairs()
    spec = pairs[PAIR]
    blob = "%s %s" % (spec.get("why", ""), spec.get("known", ""))
    assert "판정 기준 무변경" in blob or "관측 전용" in blob, blob
    # 캠페인 합격선 레지스트리를 참조하거나 쓰지 않는다.
    for forbidden in ("VALIDATION_CAMPAIGN", "min_samples", "verdict ="):
        assert forbidden not in spec.get("sql", ""), forbidden


def test_settings_threshold_untouched():
    """G-5 는 임계를 건드리지 않는다 — settings 에 새 상수를 만들지 않았는지."""
    with io.open(os.path.join(_ROOT, "config", "settings.py"), encoding="utf-8") as f:
        src = f.read()
    assert "SGD_CONF_GATE" not in src, "임계를 설정으로 승격했다 — G-5 범위를 벗어난다"


# ── ④ known 이 붙어 있다 ──────────────────────────────────────────────────────
def test_pair_is_known_so_it_does_not_cry_wolf():
    _m, _cfg, pairs = _pairs()
    known = pairs[PAIR].get("known") or ""
    assert known.strip(), "known 이 없으면 §11 적신호로 매일 올라온다(늑대소년)"
    assert "1-13" in known, known


# ── ⑤ 원인 축과 결과 축이 둘 다 있다 ─────────────────────────────────────────
def test_cause_and_effect_axes_are_both_registered():
    _m, _cfg, pairs = _pairs()
    assert "DriftRetrain조건B(n≥15)" in pairs, \
        "결과 축(n)이 사라졌다 — 원인 축만 남으면 '왜 안 쌓이나'만 보이고 '안 쌓인다'가 사라진다"
    assert PAIR in pairs
    assert len(pairs) >= 5, list(pairs)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for fn in (test_pair_is_registered,
               test_threshold_matches_the_live_constant,
               test_sql_runs_and_filters_5m_directional,
               test_scanner_returns_a_verdict_for_the_pair,
               test_pair_does_not_touch_any_campaign_gate,
               test_settings_threshold_untouched,
               test_pair_is_known_so_it_does_not_cry_wolf,
               test_cause_and_effect_axes_are_both_registered):
        try:
            fn()
            print("[ok]   %s" % fn.__name__)
        except Exception as e:
            print("[FAIL] %s: %r" % (fn.__name__, e))
            FAILURES.append(fn.__name__)
    print("-" * 60)
    print("전부 통과" if not FAILURES else "실패 %d건: %s" % (len(FAILURES), FAILURES))
    sys.exit(1 if FAILURES else 0)

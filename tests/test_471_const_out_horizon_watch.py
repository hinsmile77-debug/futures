"""[MW0601 471차 후속7 / G-2] ConstOut 호라이즌 건강도 채널 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
배경 (상세: docs/정기점검/매일점검/MW0601-20260814-점검리포트-post.md §3 G-2)
────────────────────────────────────────────────────────────────────────────
2026-08-14에 3m이 하루 4회 ConstOut으로 앙상블에서 빠졌다 돌아왔고, 그 연쇄가
재학습 4회 → S0 스파이크 → Degraded 선제차단 4회를 만들었다. **그날 유일한 진입의
호라이즌도 3m이었다.** "그런 날의 그 호라이즌 진입은 성적이 다른가"를 묻는 축이 없었다.

🔵 함정 ① 확인: **일별 영속화는 457차 G5가 이미 구현했다**(`scaler_daily.
   const_out_by_horizon`, 2026-08-12부터 실데이터). 리포트 G-2의 "영속화하자"는
   이미 반영된 사안이며, 이 채널은 남은 절반(진입 성적 결합)만 만든다.

지키는 불변식:
  T1  🔴 `const_out_by_horizon`이 NULL인 날의 진입은 **양 버킷 어디에도 안 들어간다**.
      미측정을 clean으로 세면 버킷이 오염된다(계측 4원칙 ②). 캠페인 구간 대부분이
      그 구간이므로 이 오염은 조용하고 크다.
  T2  `{}`(빈 dict)는 **측정했고 ConstOut이 없었다** — NULL과 다르다. clean으로 센다.
  T3  버킷 분리는 그날 **그 호라이즌**의 events 기준이다(다른 호라이즌 값에 오염 안 됨).
  T4  표본 미달이면 INSUFFICIENT + 제외 건수를 사유에 명시한다(계측 4원칙 ③).
  T5  판정 임계는 사전등록에서 읽는다. FLAG_DRAG는 렌더러에 등록돼 있다
      (미등록이면 조용히 INSUFFICIENT로 표시된다).

실행: python tests/test_471_const_out_horizon_watch.py   (COM/브로커 불필요)
"""

import json
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import scripts.const_out_horizon_watch as W  # noqa: E402

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _make_scaler_db(path, rows):
    """rows: [(date, const_out_by_horizon_json_or_None)]"""
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE scaler_daily (date TEXT PRIMARY KEY, "
                "const_out_by_horizon TEXT)")
    con.executemany("INSERT INTO scaler_daily (date, const_out_by_horizon) "
                    "VALUES (?,?)", rows)
    con.commit()
    con.close()


_POSITIONS = [
    # 측정일(08-12) — 3m events=3 → heavy / 5m events=0 → clean
    {"entry_ts": "2026-08-12 10:00:00", "entry_horizon": "3m", "pnl": -100000.0},
    {"entry_ts": "2026-08-12 11:00:00", "entry_horizon": "5m", "pnl": +50000.0},
    # 측정일(08-13) — 빈 dict = 측정했고 ConstOut 없음 → 전부 clean
    {"entry_ts": "2026-08-13 10:00:00", "entry_horizon": "3m", "pnl": +30000.0},
    # 🔴 미측정일(08-11, NULL) — 양쪽 어디에도 안 들어가야 한다
    {"entry_ts": "2026-08-11 10:00:00", "entry_horizon": "3m", "pnl": -900000.0},
    # 측정 이전(캠페인 초기) — 역시 제외
    {"entry_ts": "2026-07-20 10:00:00", "entry_horizon": "1m", "pnl": -800000.0},
]


def _with_stub_env(fn):
    tmp = tempfile.mkdtemp(prefix="qdq_471g2_")
    db = os.path.join(tmp, "scaler_monitor.db")
    _make_scaler_db(db, [
        ("2026-08-11", None),                                    # 미측정
        ("2026-08-12", json.dumps({"3m": {"events": 3, "minutes": 5},
                                   "5m": {"events": 0, "minutes": 0}})),
        ("2026-08-13", json.dumps({})),                          # 측정·무발생
    ])
    _o_db, _o_pos = W.SCALER_MONITOR_DB, W._load_positions
    W.SCALER_MONITOR_DB = db
    W._load_positions = lambda: list(_POSITIONS)
    try:
        fn()
    finally:
        W.SCALER_MONITOR_DB, W._load_positions = _o_db, _o_pos


def test_bucketing_excludes_unmeasured():
    def body():
        out = W.compute(since="2026-07-05")
        check("T1: 측정 3거래일 중 NULL 제외 → 2일", out.get("measured_days") == 2)
        check("T1: 미측정일 진입 2건 제외", out.get("n_positions_excluded_unmeasured") == 2)
        check("T1: 버킷에 들어간 포지션은 3건", out.get("n_positions_measured") == 3)
        h, c = out.get("heavy"), out.get("clean")
        check("T3: heavy = 08-12 3m 1건", h and h["n"] == 1)
        check("T2: clean = 08-12 5m + 08-13 3m 2건 (빈 dict는 측정·무발생)",
              c and c["n"] == 2)
        # 🔴 미측정 -900,000원이 clean에 섞였다면 평균이 음수로 무너진다
        check("T1: clean 평균이 미측정 손실에 오염되지 않았다",
              c and c["avg_pnl_krw"] == 40000.0)
        check("T3: 호라이즌별 분해 — 3m은 heavy·clean 양쪽",
              (out.get("by_horizon") or {}).get("3m", {}).get("heavy", {})["n"] == 1
              and (out["by_horizon"]["3m"].get("clean") or {})["n"] == 1)
        check("T3: 5m은 clean만", (out["by_horizon"]["5m"].get("heavy")) is None)
        tot = out.get("const_out_by_horizon_totals") or {}
        check("T3: ConstOut 총계는 측정일만 합산 (3m events=3)",
              tot.get("3m", {}).get("events") == 3)
    _with_stub_env(body)


def test_summarize_insufficient_is_explicit():
    def body():
        s = W.summarize(W.compute(since="2026-07-05"))
        check("T4: 표본 미달 → INSUFFICIENT", s.get("verdict") == "INSUFFICIENT")
        check("T4: 사유에 제외 건수 명시(계측 4원칙 ③)",
              "미측정 제외 2포지션" in s.get("reason", ""))
        check("T4: 사유에 측정 구간 명시",
              "2026-08-12~2026-08-13" in s.get("reason", ""))
        check("T4: 표본 미달이어도 관측치는 실린다(호라이즌 총계)",
              bool(s.get("const_out_by_horizon_totals")))
    _with_stub_env(body)


def test_verdict_thresholds_come_from_prereg():
    from config.settings import VALIDATION_CAMPAIGN
    cfg = VALIDATION_CAMPAIGN.get("const_out_horizon_watch") or {}
    check("T5: 사전등록 존재", bool(cfg))
    check("T5: heavy 임계는 O-3 관측기준과 같은 3", cfg.get("heavy_events_min") == 3)
    check("T5: 표본 하한은 [28]·[29]와 동일 20/5",
          cfg.get("min_samples_per_bucket") == 20 and cfg.get("min_days") == 5)
    check("T5: data_start = 457차 G5 배포일", cfg.get("data_start") == "2026-08-12")
    check("T5: 모듈이 사전등록 값을 그대로 읽는다",
          W.HEAVY_MIN == cfg["heavy_events_min"] and W.MIN_N == cfg["min_samples_per_bucket"])


def test_flag_drag_is_rendered_and_is_not_a_block():
    import scripts.generate_validation_campaign_report as rep
    # 🔴 미등록 verdict는 조용히 INSUFFICIENT로 표시된다 — 판정이 사라진 것처럼 보인다
    check("T5: FLAG_DRAG가 렌더러에 등록됨",
          "FLAG_DRAG" in rep._fmt_verdict("FLAG_DRAG"))
    check("T5: 채널이 리포트에 배선됨",
          'scripts.const_out_horizon_watch' in open(
              rep.__file__.replace(".pyc", ".py"), encoding="utf-8").read())
    src = open(os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "scripts", "const_out_horizon_watch.py"),
        encoding="utf-8").read()
    check("T5: FLAG_DRAG 판정문이 '차단 처방이 아니다'를 명시",
          "차단 처방이 아니다" in src)


def test_flag_drag_fires_when_gap_exceeds():
    """임계 초과 시 실제로 FLAG_DRAG가 나오는가 (판정 경로 자체의 생존 확인)."""
    def body():
        out = W.compute(since="2026-07-05")
        # 표본 하한만 우회해 판정 분기를 태운다 — 임계값은 건드리지 않는다.
        out["n_days_measured_with_entries"] = W.MIN_DAYS
        out["heavy"] = {"n": W.MIN_N, "avg_pnl_krw": -300000.0,
                        "total_pnl_krw": -300000.0 * W.MIN_N, "win_rate": 0.2}
        out["clean"] = {"n": W.MIN_N, "avg_pnl_krw": +100000.0,
                        "total_pnl_krw": 100000.0 * W.MIN_N, "win_rate": 0.6}
        s = W.summarize(out)
        check("T5: 격차 400,000원 ≥ 200,000원 → FLAG_DRAG",
              s.get("verdict") == "FLAG_DRAG" and s.get("gap_krw") == 400000.0)
        out["heavy"]["avg_pnl_krw"] = +50000.0      # 격차 50,000원
        s2 = W.summarize(out)
        check("T5: 격차 미달 → PASS", s2.get("verdict") == "PASS")
    _with_stub_env(body)


if __name__ == "__main__":
    _fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in _fns:
        try:
            fn()
        except Exception as e:
            FAILURES.append("%s: %r" % (fn.__name__, e))
            print("[FAIL] %s: %r" % (fn.__name__, e))
    print("-" * 60)
    if FAILURES:
        print("실패 %d건: %s" % (len(FAILURES), FAILURES))
        sys.exit(1)
    print("전부 통과")

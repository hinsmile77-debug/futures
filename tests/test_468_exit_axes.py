# -*- coding: utf-8 -*-
"""[MW0602 468차 G-3] 청산 라벨 2축 스키마 회귀 테스트.

지키려는 불변식:
  1. `exit_reason` 문자열은 **바꾸지 않는다**. 사전등록 채널 [15]·[26]·[48]과
     `bar_stop_path_watch.py`·`test_439`가 `'%하드스톱%'`로 필터한다(465차 P4 결정).
  2. `classify_exit()`이 트리거/결과의 **유일한 생성자**다 — 기록 경로와 분석이
     같은 함수를 쓴다.
  3. 하드스톱 vs 보호트레일은 **`tp1_reached`로만** 가른다. `pnl_pts>0` 추정 금지 —
     그러면 트리거 축이 결과 축과 상관돼 2축으로 나눈 의미가 사라진다.
     `tp1_reached`가 None(구버전 행)이면 `하드스톱?`(모른다)이다.
  4. INSERT 컬럼수 · 플레이스홀더 수 · 값 튜플 길이가 일치한다.
  5. 리포트 쪽에도 멱등 ALTER가 있다(420차 joint_gate_shadow 사고 형태 방지).

실행: python tests/test_468_exit_axes.py   (COM/브로커 불필요, DB는 있으면 검사)
"""
from __future__ import print_function

import ast
import io
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

_FAILS = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        _FAILS.append(name)


def read(rel):
    with io.open(os.path.join(BASE, rel), encoding="utf-8") as f:
        return f.read()


# ══════════════════════════════════════════════════════════════════
# 1. classify_exit 매핑
# ══════════════════════════════════════════════════════════════════
def test_classify():
    from utils.db_utils import classify_exit

    print("\n-- test_classify")
    cases = [
        # (reason, tp1_reached, pnl, 기대 trigger, 기대 outcome)
        ("하드스톱", 1, 1.41, "보호트레일", "이익"),
        ("하드스톱(틱)", 0, -1.48, "하드스톱", "손실"),
        ("하드스톱", None, 1.41, "하드스톱?", "이익"),      # 구버전 행 = 모른다
        ("하드스톱(틱)_유실복구", 0, -0.5, "하드스톱", "손실"),
        ("손절1차 조기축소", 0, -1.48, "손절1차", "손실"),
        ("손절1차 전량청산(qty1)", 0, -0.9, "손절1차", "손실"),
        ("TP1 부분청산 33%", 1, 0.8, "TP1", "이익"),
        ("TP2(전량)", 1, 2.62, "TP2", "이익"),
        ("15:10 강제청산", 0, 0.0, "시간마감", "본전"),
        ("15:18 안전망", 0, -0.2, "안전망", "손실"),
        ("수동 부분청산 50%", 1, 0.3, "수동", "이익"),
        ("stuck_exit_flat", None, None, "복구", ""),
    ]
    for reason, tp1, pnl, want_t, want_o in cases:
        got_t, got_o = classify_exit(reason, tp1, pnl)
        check("`%s` (tp1=%s) → %s/%s" % (reason, tp1, want_t, want_o or "—"),
              got_t == want_t and got_o == want_o)

    # 3번 불변식: 같은 reason·같은 손익이어도 tp1_reached가 트리거를 가른다
    a, _ = classify_exit("하드스톱", 1, -0.5)   # 이익이 아니어도 TP1 도달이면 보호트레일
    b, _ = classify_exit("하드스톱", 0, 5.0)    # 이익이어도 TP1 미도달이면 하드스톱
    check("트리거는 손익이 아니라 tp1_reached로 갈린다", a == "보호트레일" and b == "하드스톱")

    # 결과 축: 동률은 `본전` — 승패 집계의 `>0` 규약(패로 셈)과 다른 축이다
    _, o = classify_exit("TP2(전량)", 1, 0.0)
    check("동률은 `본전` (승패 집계 규약과 분리)", o == "본전")


# ══════════════════════════════════════════════════════════════════
# 2. exit_reason 문자열 불변 (465차 P4 결정 보존)
# ══════════════════════════════════════════════════════════════════
def test_reason_untouched():
    print("\n-- test_reason_untouched")
    src = read("main.py")
    check("`reason=\"하드스톱\"` 그대로", 'reason="하드스톱"' in src)
    check("`reason=\"하드스톱(틱)\"` 그대로", 'reason="하드스톱(틱)"' in src)
    check("`보호트레일` 라벨을 exit_reason 에 쓰지 않는다",
          'reason="보호트레일"' not in src)


# ══════════════════════════════════════════════════════════════════
# 3. INSERT 컬럼수 = 플레이스홀더 = 값 개수
# ══════════════════════════════════════════════════════════════════
def test_insert_arity():
    print("\n-- test_insert_arity")
    src = read("main.py")
    i = src.find("INSERT INTO trades")
    check("INSERT INTO trades 존재", i > 0)
    if i < 0:
        return
    head = src[i:i + 2000]
    cols_part = head[head.find("(") + 1:head.find(")")]
    n_cols = len([c for c in cols_part.replace("\n", " ").split(",") if c.strip()])
    vals_i = head.find("VALUES")
    vals_part = head[vals_i:head.find(")", vals_i)]
    n_ph = vals_part.count("?")
    check("컬럼 %d개 = 플레이스홀더 %d개" % (n_cols, n_ph), n_cols == n_ph)
    check("exit_trigger/exit_outcome 이 컬럼 목록에 있다",
          "exit_trigger" in cols_part and "exit_outcome" in cols_part)

    # 값 튜플 길이는 AST로 센다 (문자열 파싱으로는 중첩 괄호를 못 센다)
    tree = ast.parse(src)
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name = getattr(f, "id", None) or getattr(f, "attr", None)
        if name != "execute" or len(node.args) < 3:
            continue
        sql = node.args[1]
        s = sql.s if isinstance(sql, ast.Str) else (
            sql.value if isinstance(sql, ast.Constant) and isinstance(sql.value, str) else "")
        if "INSERT INTO trades" not in s:
            continue
        if isinstance(node.args[2], ast.Tuple):
            found.append(len(node.args[2].elts))
    check("값 튜플을 찾았다", len(found) == 1)
    if found:
        check("값 %d개 = 컬럼 %d개" % (found[0], n_cols), found[0] == n_cols)


# ══════════════════════════════════════════════════════════════════
# 4. 멱등 ALTER 2중화 (db_utils + 리포트)
# ══════════════════════════════════════════════════════════════════
def test_migration_double_guard():
    print("\n-- test_migration_double_guard")
    du = read("utils/db_utils.py")
    check("db_utils additions 에 exit_trigger", '"exit_trigger": "TEXT"' in du)
    check("db_utils additions 에 exit_outcome", '"exit_outcome": "TEXT"' in du)
    rep = read("scripts/generate_validation_campaign_report.py")
    check("리포트에도 멱등 ALTER 함수", "_ensure_trades_exit_axis_columns" in rep)
    check("리포트가 그 함수를 실제로 호출한다",
          rep.count("_ensure_trades_exit_axis_columns") >= 2)


# ══════════════════════════════════════════════════════════════════
# 5. 라이브 DB (있을 때만)
# ══════════════════════════════════════════════════════════════════
def test_live_db():
    print("\n-- test_live_db")
    import sqlite3
    p = os.path.join(BASE, "data", "db", "trades.db")
    if not os.path.exists(p):
        print("[SKIP] trades.db 없음")
        return
    conn = sqlite3.connect(p)
    try:
        from utils.db_utils import init_trades_db  # noqa: F401  (마이그레이션 존재 확인용)
    except ImportError:
        pass
    try:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(trades)")}
        if "exit_trigger" not in cols:
            print("[SKIP] 아직 마이그레이션 전 — 앱 기동 또는 리포트 1회 실행 후 재검사")
            return
        n_old = conn.execute(
            "select count(*) from trades where exit_trigger is not null and exit_ts < ?",
            ("2026-08-14",)).fetchone()[0]
        check("소급 백필 없음 (배포 이전 행은 NULL)", n_old == 0)
    finally:
        conn.close()


if __name__ == "__main__":
    test_classify()
    test_reason_untouched()
    test_insert_arity()
    test_migration_double_guard()
    test_live_db()
    print("\n" + "=" * 60)
    if _FAILS:
        print("실패 %d건:" % len(_FAILS))
        for f in _FAILS:
            print("  - %s" % f)
        sys.exit(1)
    print("468차 G-3 청산 2축 회귀 테스트 전부 통과")

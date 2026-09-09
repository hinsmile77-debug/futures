# -*- coding: utf-8 -*-
"""[MW0602 554차 / 1-6 단계 1] 비용모델 요율 **핀 해제 사전 관측** — 읽기 전용.

`--impact`(commission_rate_recon)는 *"왕복 비용이 얼마나 오르나"* 만 답한다.
정작 주간회의가 물어야 하는 것은 ***"어느 채널의 verdict 가 뒤집히나"*** 인데,
그 답이 지금까지 없었다. 461차 `mdd_pct` 사고의 교훈이 정확히 그것이다 —
**측정값이 재정의되면서 판정이 뒤집혔는데 아무도 몰랐다.**

이 스크립트는 비용 의존 채널을 **핀 요율과 라이브 요율로 각각 한 번씩** 평가해
verdict 를 나란히 놓는다. 판정에는 **아무 영향이 없다**(별도 스크립트이며 리포트
생성 경로를 건드리지 않는다).

무엇을 조심했는가
-----------------
🔴 **리포트는 DB에 쓴다.** `resolve_and_eval_*` 10개가 섀도 테이블
   (`hurst_gate_shadow`·`joint_gate_shadow`·`tp2_hold_shadow` 등)을 `UPDATE` 한다
   — 카운터팩추얼 해소다. 그냥 두 번 부르면 **이중 적용**된다.
   ⇒ `trades.db` **복사본 2벌**(핀용·라이브용)을 떠서 각 패스가 동일한 시작
     상태에서 출발하게 한다. 라이브 `trades.db` 는 **열지도 않는다**.
   ⚠ `predictions.db`·`raw_data.db` 는 읽기 전용으로만 쓰이므로 복사하지 않는다
     (530MB 를 뜨지 않기 위해서다). 쓰기 구문이 생기면 이 전제가 깨진다 —
     아래 `_assert_no_unexpected_writes()` 가 매 실행 때 되묻는다.

🔴 **대상 함수를 손으로 적지 않는다.** `_roundtrip_cost_pt()` 호출을 AST 로 훑어
   그 줄을 감싸는 최상위 함수를 자동 식별한다. 손 목록은 낡는다 —
   `test_493` 의 `_COST_CONSUMERS`(파일 목록)가 541차 이식에 그대로 뚫린 것이
   바로 그 사고이며, 이 스크립트는 그 사고의 산물이다.

⚠ **핀 해제는 이 스크립트로 결정하지 않는다.** 여기 나오는 「해제 시 verdict」는
  주간회의 입력 자료이지 승인이 아니다. 사전등록 합격선은 무변경이다(§9-4).

실행 (py310_64 — 리포트 생성기와 같은 환경):
    python scripts/cost_pin_release_preview.py [--days 28] [--json]
"""
from __future__ import print_function

import argparse
import ast
import io
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import traceback

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_REPORT_REL = "scripts/generate_validation_campaign_report.py"

#: 이 두 테이블 접두는 리포트가 **쓰는** 것으로 이미 알려져 있다(2026-09-09 실측).
#: 여기 없는 곳에 새 쓰기가 생기면 복사본 전략의 전제가 깨지므로 실행을 멈춘다.
_KNOWN_WRITE_DBS = ("TRADES_DB",)


def _load_report_module():
    """리포트를 모듈로 적재한다 (scripts/ 는 패키지가 아니다)."""
    import importlib.util
    path = os.path.join(_ROOT, _REPORT_REL)
    spec = importlib.util.spec_from_file_location("_vcr_preview", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def discover_cost_dependent_funcs():
    """`_roundtrip_cost_pt()` 를 부르는 **최상위 함수 이름** 집합 — AST 자동 식별.

    손 목록을 두지 않는 이유는 모듈 docstring 참조.
    """
    path = os.path.join(_ROOT, _REPORT_REL)
    src = io.open(path, encoding="utf-8").read()
    tree = ast.parse(src, filename=path)
    lines = [ln.split("#", 1)[0] for ln in src.splitlines()]
    owner = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        end = max((getattr(n, "lineno", node.lineno) for n in ast.walk(node)),
                  default=node.lineno)
        for ln in range(node.lineno, end + 1):
            owner[ln] = node.name
    found = {}
    for i, ln in enumerate(lines, 1):
        if "_roundtrip_cost_pt(" in ln and "def _roundtrip_cost_pt" not in ln:
            fn = owner.get(i)
            if fn and not fn.startswith("_"):
                found.setdefault(fn, []).append(i)
    return found


def _assert_no_unexpected_writes():
    """리포트의 SQL 쓰기가 여전히 **`TRADES_DB` 로만** 나가는가.

    이 전제가 깨지면(예: `predictions.db` 에 `UPDATE` 가 생기면) 복사본 2벌
    전략이 라이브를 보호하지 못한다. **조용히 틀리느니 멈춘다.**

    🔴 판정 대상은 「함수 이름 규약」이 아니라 **실제 쓰기 대상 DB** 다.
       초안은 `resolve_and_eval_*` 이름으로 갈랐는데 두 가지를 잘못 잡았다:
         · `_conn()` — `UPDATE` 가 **독스트링 안**에 있었다(오탐).
           그래서 여기서는 `#` 주석만이 아니라 **`.execute()` 인자로 넘어가는
           문자열**만 SQL 로 본다 — 독스트링·설명문은 애초에 후보가 아니다.
         · `_backfill_shadow_mfe()` — 이름 규약 밖이지만 `_conn(TRADES_DB)` 로
           쓴다. 즉 **안전한데 이름 때문에 걸렸다**(미탐이 아니라 과탐).
       이름은 규약이고 DB 는 사실이다. 사실을 본다.

    반환: (쓰기 함수 목록, 규약 위반 목록)
    """
    import re
    path = os.path.join(_ROOT, _REPORT_REL)
    src = io.open(path, encoding="utf-8").read()
    tree = ast.parse(src, filename=path)

    def _str_val(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.JoinedStr):       # f-string
            return " ".join(_str_val(v) or "" for v in node.values)
        # ⚠ 이 저장소는 `"UPDATE %s SET ..." % table` 로 테이블명을 끼워 넣는다
        #   (`_backfill_shadow_mfe`). Constant 만 보면 그런 쓰기를 **놓친다** —
        #   미탐은 오탐보다 위험하다(가드가 조용히 통과한다).
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
            return _str_val(node.left)
        # `"UPDATE " + tbl` 이나 `sql.format(...)` 형태도 왼쪽/수신자를 본다
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return " ".join(x for x in (_str_val(node.left),
                                        _str_val(node.right)) if x)
        if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "format":
            return _str_val(getattr(node.func, "value", None))
        return None

    # 🔴 이 정규식으로 두 번 미탐했다. 둘 다 **테이블명을 보려 한 것**이 원인이다:
    #   ① `UPDATE\s+\w` + `\b` → 한 글자 테이블명만 매치. `UPDATE signal_decay_exits`
    #      가 안 걸려 「쓰기 함수 0건」이 나왔고 가드가 **공허하게 통과**했다.
    #   ② `UPDATE\s+\w+`      → `"UPDATE %s SET ..." % table`(`_backfill_shadow_mfe`)
    #      의 `%s` 가 `\w` 가 아니라 또 놓쳤다.
    #   ⇒ 애초에 **`.execute()` 인자만** 보고 있으므로 테이블명을 확인할 이유가
    #     없다. 키워드만 본다. 미탐은 오탐보다 위험하다 — 오탐은 시끄럽고,
    #     미탐은 조용히 라이브를 위험에 둔다.
    _WRITE = re.compile(r"\b(INSERT\s+INTO|UPDATE|DELETE\s+FROM|REPLACE\s+INTO)\b",
                        re.I)
    writers, db_targets = {}, {}
    for top in tree.body:
        if not isinstance(top, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        wrote, dbs = False, set()
        for n in ast.walk(top):
            if not isinstance(n, ast.Call):
                continue
            fname = getattr(n.func, "attr", None) or getattr(n.func, "id", None)
            # ① 실제로 실행되는 SQL 만 본다 (독스트링·주석 제외)
            if fname in ("execute", "executemany", "executescript"):
                for a in n.args:
                    s = _str_val(a)
                    if s and _WRITE.search(s):
                        wrote = True
            # ② 이 함수가 어느 DB 에 붙는가
            if fname in ("_conn", "connect"):
                for a in n.args:
                    nm = getattr(a, "id", None)
                    if nm:
                        dbs.add(nm)
                    else:
                        s = _str_val(a)
                        if s:
                            dbs.add("<literal>")
        if wrote:
            writers[top.name] = dbs
            db_targets[top.name] = dbs
    # 쓰기 함수가 붙은 DB 가 전부 허용 목록 안인가.
    # (DB 식별자를 못 잡은 경우 = 알 수 없음 → 안전하게 위반으로 본다)
    bad = {fn: dbs for fn, dbs in writers.items()
           if (not dbs) or not dbs.issubset(set(_KNOWN_WRITE_DBS))}
    return sorted(writers), bad


def _copy_trades_db(dst_dir, tag):
    """sqlite backup API 로 일관 스냅샷. 단순 파일복사가 아니다(WAL 중간상태 회피)."""
    from config.settings import TRADES_DB
    dst = os.path.join(dst_dir, "trades_%s.db" % tag)
    src = sqlite3.connect("file:%s?mode=ro" % TRADES_DB.replace("\\", "/"), uri=True)
    out = sqlite3.connect(dst)
    with out:
        src.backup(out)
    out.close()
    src.close()
    return dst


def _run_pass(mod, funcs, rate, trades_db, days):
    """요율·DB를 갈아끼운 채 대상 함수를 한 번씩 돌리고 verdict 를 거둔다."""
    prev_rate, prev_db = mod.COST_MODEL_COMMISSION_RATE, mod.TRADES_DB
    mod.COST_MODEL_COMMISSION_RATE = rate
    mod.TRADES_DB = trades_db
    got = {}
    try:
        for fn in sorted(funcs):
            f = getattr(mod, fn, None)
            if f is None:
                got[fn] = {"verdict": None, "error": "함수 없음"}
                continue
            try:
                import inspect
                kw = {}
                try:
                    if "days" in inspect.signature(f).parameters:
                        kw["days"] = days
                except (TypeError, ValueError):
                    pass
                r = f(**kw)
            except Exception as e:
                got[fn] = {"verdict": None,
                           "error": "%s: %s" % (type(e).__name__, e)}
                continue
            if isinstance(r, dict):
                # ⚠ 일부 평가자는 **한 함수가 채널 여럿**을 낸다 — verdict 가
                #   `out["tight"]["verdict"]` 처럼 한 겹 아래 있다
                #   (`eval_gp_cross_channels` 가 그렇고, 하필 1-6 의 당사자다).
                #   최상위만 보면 그 행이 `-` 로 비어 결정표에 구멍이 생긴다.
                if r.get("verdict") is not None:
                    got[fn] = {"verdict": r.get("verdict"), "error": None}
                    continue
                subs = {k: v.get("verdict") for k, v in r.items()
                        if isinstance(v, dict) and "verdict" in v}
                if subs:
                    for k, v in subs.items():
                        got["%s[%s]" % (fn, k)] = {"verdict": v, "error": None}
                else:
                    got[fn] = {"verdict": None,
                               "error": r.get("error") or "verdict 키 없음"}
            else:
                got[fn] = {"verdict": None, "error": "dict 아님(%s)" % type(r).__name__}
    finally:
        mod.COST_MODEL_COMMISSION_RATE = prev_rate
        mod.TRADES_DB = prev_db
    return got


def main(argv=None):
    ap = argparse.ArgumentParser(description="비용모델 핀 해제 사전 관측 (읽기 전용)")
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    from config.settings import (COST_MODEL_COMMISSION_RATE,
                                 FUTURES_COMMISSION_RATE, TICK_SIZE,
                                 VALIDATION_CAMPAIGN)

    pinned, live = COST_MODEL_COMMISSION_RATE, FUTURES_COMMISSION_RATE
    if abs(pinned - live) < 1e-12:
        print("핀과 라이브 요율이 이미 같다 (%.7f) — 비교할 것이 없다." % pinned)
        return 0

    offenders, bad = _assert_no_unexpected_writes()
    if bad:
        print("🔴 중단 — `TRADES_DB` 밖으로 나가는 SQL 쓰기가 있다:")
        for fn, dbs in sorted(bad.items()):
            print("     %-44s → %s" % (fn, ", ".join(sorted(dbs)) or "대상 불명"))
        print("   복사본 2벌(trades.db) 전략이 라이브를 보호한다는 전제가 깨졌다.")
        print("   해당 DB도 복사 대상에 넣고 이 스크립트를 갱신할 것.")
        return 2

    funcs = discover_cost_dependent_funcs()
    if not funcs:
        print("🔴 비용 의존 함수를 하나도 찾지 못했다 — `_roundtrip_cost_pt` 이름이 "
              "바뀌었는지 확인할 것(계측이 조용히 죽는 형태).")
        return 2

    slip = float(VALIDATION_CAMPAIGN.get("slippage_ticks_per_side", 1.0))
    px = 1040.0
    c_pin = 2 * px * pinned + 2 * slip * TICK_SIZE
    c_live = 2 * px * live + 2 * slip * TICK_SIZE

    print("비용모델 핀 해제 사전 관측 — 판정 무영향(관측 전용)")
    print("")
    print("  요율        핀 %.7f  →  라이브 %.7f   (요율 배수 %.3f)"
          % (pinned, live, live / pinned))
    print("  왕복비용    %.4f pt  →  %.4f pt        (**비용 배수 %.3f**)"
          % (c_pin, c_live, c_live / c_pin))
    print("  ⚠ 요율 배수와 비용 배수는 다르다 — 슬리피지 %.2fpt 가 양쪽 동일해 "
          "배수를 희석한다(계측 4원칙 ①)." % (2 * slip * TICK_SIZE))
    print("")
    print("  비용 의존 함수 %d개 (AST 자동 식별) · 쓰기 함수 %d개는 복사본에서 실행"
          % (len(funcs), len(offenders)))
    print("")

    tmp = tempfile.mkdtemp(prefix="costpin_")
    try:
        mod = _load_report_module()
        db_a = _copy_trades_db(tmp, "pinned")
        db_b = _copy_trades_db(tmp, "live")
        res_a = _run_pass(mod, funcs, pinned, db_a, args.days)
        res_b = _run_pass(mod, funcs, live, db_b, args.days)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rows, flipped, errored = [], 0, 0
    # ⚠ 키는 `funcs` 가 아니라 **두 패스 결과의 합집합**으로 돈다 — 한 함수가
    #   채널 여럿을 내면 `fn[sub]` 라벨이 생기고, 한쪽 패스에만 있는 키도
    #   조용히 사라지면 안 된다(계측 4원칙 ③).
    for fn in sorted(set(res_a) | set(res_b)):
        a, b = res_a.get(fn, {}), res_b.get(fn, {})
        if fn not in res_a or fn not in res_b:
            a = a or {"verdict": None, "error": "이 패스에서 산출되지 않음"}
            b = b or {"verdict": None, "error": "이 패스에서 산출되지 않음"}
        va, vb = a.get("verdict"), b.get("verdict")
        err = a.get("error") or b.get("error")
        if err:
            errored += 1
            mark = "⚠미측정"
        elif va != vb:
            flipped += 1
            mark = "🔴뒤집힘"
        else:
            mark = "  동일"
        rows.append({"func": fn, "pinned": va, "live": vb,
                     "flip": (va != vb and not err), "error": err, "mark": mark})

    if args.json:
        print(json.dumps({"pinned_rate": pinned, "live_rate": live,
                          "cost_pin_pt": c_pin, "cost_live_pt": c_live,
                          "rows": rows}, ensure_ascii=False, indent=2))
        return 1 if flipped else 0

    print("%-46s %-14s %-14s %s" % ("채널 평가 함수", "핀(현행)", "해제 시", ""))
    print("-" * 92)
    for r in rows:
        print("%-46s %-14s %-14s %s"
              % (r["func"], r["pinned"] or "-", r["live"] or "-", r["mark"]))
        if r["error"]:
            print("%-46s   └ %s" % ("", r["error"][:110]))
    print("-" * 92)
    print("뒤집힘 %d건 / 동일 %d건 / 미측정 %d건 (전체 %d)"
          % (flipped, len(rows) - flipped - errored, errored, len(rows)))
    print("")
    print("⚠ 미측정은 **동일이 아니다** — 실행이 실패한 것이다(계측 4원칙 ②).")
    print("⚠ 이 표는 주간회의 입력 자료다. 사전등록 합격선은 무변경이며,")
    print("  해제 여부는 여기서 결정하지 않는다.")
    return 1 if flipped else 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""[MW0601 480차 / F-3] `ofi_norm` 원값 분포 프로브 — CORE 피처 identity 강제의 인과 판정.

## 왜 필요한가

2026-08-19 장후 점검 §1-4: 스케일러 재적합 39회 **전부**(6개 호라이즌 234행)에서
CORE 피처 `ofi_norm`이 `raw_std≈0` 판정을 받아 identity(0,1)로 강제됐다.
추이는 08-17 이전 0~6회 → 08-18 94% → 08-19 **100%** 다.

그런데 **인과 방향을 모른다**(313차 원칙: n이 작을 때 확정 금지):

  후보 ① 데이터 원천 문제 — `ofi_norm` 원값의 분산 자체가 줄었다(수집·계산 축)
  후보 ② 판정 임계 문제 — 원값은 그대로인데 `raw_std < 0.05` 컷이 과민하다(스케일러 축)

둘은 조치가 정반대다. ①이면 OFI 계산·틱 수집을 봐야 하고, ②면 임계를 재보정한다.
`raw_features`의 원값 분포를 보면 갈린다 — 이 스크립트가 그것만 한다.

## 사전등록 판정문 (2026-08-19 리포트 §2 F-3 · 데이터를 보기 전에 고정)

> *"08-17 이전 대비 std가 한 자릿수 배율로 줄었으면 데이터 원천 문제(수집),
> std는 그대로인데 identity 강제만 늘었으면 판정 임계 문제(스케일러).
> **5거래일 관측으로 확정**하며 그 전에는 CORE 지정을 건드리지 않는다."*

⚠ 임계·판정문을 사후에 움직이지 말 것(458차 D6과 같은 사전등록 위반).
⚠ 이 스크립트는 **조사만** 한다. CLAUDE.md §3의 CORE 지정은 여기서 바뀌지 않는다.

## 무엇을 재는가

라이브 스케일러(`model/multi_horizon_model.py:_refresh_scalers`)는 최근 N봉의
`np.std()`를 그대로 보고 `< 0.05`면 identity를 강제한다. 그래서 일자별 std만이 아니라
**그 판정이 실제로 도는 창 크기(30봉=A_WARMUP / 500봉=장중 트리거)의 롤링 std**를
같이 낸다 — 일자 전체 std가 0.05를 넘어도 500봉 창이 넘지 못하면 identity가 걸린다.

    python scripts/ofi_norm_distribution_probe.py                 # 최근 15거래일
    python scripts/ofi_norm_distribution_probe.py --from 2026-08-01 --feature ofi_norm
    python scripts/ofi_norm_distribution_probe.py --json data/ofi_norm_probe.json

읽기 전용이며 장중에는 `guard_intraday()`가 막는다(2026-08-10 CB⑤ 자가유발 전례).
"""
from __future__ import print_function

import argparse
import datetime
import json
import math
import os
import sys
from collections import OrderedDict

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.analysis_db import connect_ro, guard_intraday, utf8_console  # noqa: E402

RAW_DB = os.path.join(_ROOT, "data", "db", "raw_data.db")

#: 라이브가 identity를 강제하는 임계 — model/multi_horizon_model.py 와 같은 값.
#: ⚠ 하드코딩이 아니라 "그 코드가 쓰는 값"을 옮겨 적은 것이다. 코드가 바뀌면 여기도
#:   바꿔야 하므로, 아래 `_assert_threshold_matches_live()`가 소스에서 재확인한다.
IDENTITY_STD_THRESHOLD = 0.05

#: 라이브 재적합 창 — [ScalerRefresh] 로그의 `n=... bars` 실측값.
WINDOWS = (30, 500)


def _std(xs):
    n = len(xs)
    if n < 2:
        return 0.0
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / n)


def _assert_threshold_matches_live():
    """상수가 라이브 코드와 갈라지면 이 프로브의 결론이 통째로 틀린다."""
    path = os.path.join(_ROOT, "model", "multi_horizon_model.py")
    try:
        with open(path, encoding="utf-8") as f:
            src = f.read()
    except Exception:
        return "확인 불가(%s 읽기 실패)" % path
    return ("일치" if "_raw_std < %s" % IDENTITY_STD_THRESHOLD in src
            else "⚠ 불일치 — model/multi_horizon_model.py 의 컷을 확인하라")


def load_series(db_path, feature, since):
    """raw_features(JSON 페이로드)에서 일자별 시계열을 뽑는다."""
    con = connect_ro(db_path)
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT ts, features FROM raw_features WHERE ts >= ? ORDER BY ts",
            (since,),
        )
        byday = OrderedDict()
        missing = 0
        for ts, payload in cur.fetchall():
            try:
                v = json.loads(payload).get(feature)
            except Exception:
                v = None
            if v is None:
                missing += 1
                continue
            byday.setdefault(ts[:10], []).append(float(v))
        return byday, missing
    finally:
        con.close()


def summarize(byday, feature):
    """일자별 요약 + 라이브와 같은 창의 롤링 std.

    ⚠ 롤링 창은 **일자 경계를 넘어 연속**으로 잡는다. 라이브 재적합은 "최근 500봉"을
    쓰지 하루치를 쓰지 않기 때문이다 — 하루 385봉이므로 500봉 창은 항상 전일을 걸친다.
    창을 하루 안에 가두면 500봉 컬럼이 통째로 "미측정"이 되어(첫 구현이 그랬다)
    정작 장중 트리거의 판정 조건을 못 본다.
    각 창은 **마지막 봉의 일자**에 귀속시킨다(그 시점에 재적합이 돌기 때문).
    """
    days = sorted(byday)
    flat, owner = [], []
    for day in days:
        for x in byday[day]:
            flat.append(x)
            owner.append(day)

    roll = {w: {} for w in WINDOWS}
    for w in WINDOWS:
        for i in range(0, len(flat) - w + 1):
            roll[w].setdefault(owner[i + w - 1], []).append(_std(flat[i:i + w]))

    rows = []
    for day in days:
        xs = byday[day]
        n = len(xs)
        row = {
            "date": day,
            "n": n,
            "std": _std(xs),
            "min": min(xs),
            "max": max(xs),
            "zero_pct": 100.0 * sum(1 for x in xs if abs(x) < 1e-12) / n,
            "uniq": len(set(xs)),
        }
        for w in WINDOWS:
            stds = roll[w].get(day) or []
            if stds:
                row["below_%d" % w] = 100.0 * sum(
                    1 for v in stds if v < IDENTITY_STD_THRESHOLD) / len(stds)
                row["medstd_%d" % w] = sorted(stds)[len(stds) // 2]
            else:
                # ⚠ 미측정 ≠ 0 (계측 4원칙 ②) — 창을 채울 선행 표본이 없던 것이다.
                row["below_%d" % w] = None
                row["medstd_%d" % w] = None
        rows.append(row)
    return rows


def render(rows, feature, missing, days_window):
    out = []
    A = out.append
    A("# `%s` 원값 분포 프로브 (F-3)" % feature)
    A("")
    A("- 생성: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    A("- identity 강제 임계: raw_std < %.2f (라이브 코드 대조: %s)"
      % (IDENTITY_STD_THRESHOLD, _assert_threshold_matches_live()))
    A("- 라이브 재적합 창: %s봉 ([ScalerRefresh] `n=` 실측)"
      % "·".join(str(w) for w in WINDOWS))
    if missing:
        A("- ⚠ 피처 키가 없던 행 %d개 — 이 값들은 집계에서 **제외**했다(0으로 세지 않았다)"
          % missing)
    A("")
    A("| 일자 | n | 일std | 30봉창 <임계 | 500봉창 <임계 | 500봉 중앙std | min | max | 0% | uniq |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        def _p(v):
            return "—(미측정)" if v is None else "%.0f%%" % v

        def _f(v):
            return "—" if v is None else "%.4f" % v

        A("| %s | %d | **%.4f** | %s | %s | %s | %.3f | %.3f | %.1f%% | %d |" % (
            r["date"], r["n"], r["std"], _p(r.get("below_30")), _p(r.get("below_500")),
            _f(r.get("medstd_500")), r["min"], r["max"], r["zero_pct"], r["uniq"]))
    A("")

    # ── 사전등록 판정문 대입 ──
    if len(rows) >= 4:
        recent = rows[-days_window:] if days_window else rows[-5:]
        base = rows[:-len(recent)] or rows[:1]
        r_std = sum(x["std"] for x in recent) / len(recent)
        b_std = sum(x["std"] for x in base) / len(base)
        ratio = (b_std / r_std) if r_std > 0 else float("inf")
        A("## 판정 (사전등록 문구 대입)")
        A("")
        A("- 기준구간 %s~%s 평균 일std = **%.4f**" % (base[0]["date"], base[-1]["date"], b_std))
        A("- 최근 %d거래일 평균 일std = **%.4f**" % (len(recent), r_std))
        A("- 축소 배율 = **×%.2f**" % ratio)
        A("")
        if ratio >= 2.0:
            A("→ **후보 ① 데이터 원천 문제 쪽**. 원값 분산 자체가 줄었으므로 identity 강제는 "
              "결과이지 원인이 아니다. 다음 조사축은 OFI 계산 입력(틱·호가 수집량)이다.")
        elif ratio <= 1.2:
            A("→ **후보 ② 판정 임계 문제 쪽**. 원값 분산은 유지되는데 identity만 늘었다면 "
              "`raw_std < %.2f` 컷의 과민성을 본다." % IDENTITY_STD_THRESHOLD)
        else:
            A("→ **판정 보류**(축소 배율 1.2~2.0 사이). 표본을 더 쌓는다.")
        A("")
        A("⚠ **5거래일 관측 전에는 확정하지 않는다**(사전등록). CORE 지정 변경은 이 조사 "
          "단독으로 하지 않는다 — CLAUDE.md 절대원칙 §3.")
        A("")
    else:
        A("_표본 일수가 4일 미만이라 판정문을 대입하지 않는다._")
        A("")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ofi_norm 원값 분포 프로브 (F-3)")
    ap.add_argument("--feature", default="ofi_norm")
    ap.add_argument("--from", dest="since", default=None,
                    help="시작일 YYYY-MM-DD (기본: 15거래일 전 근사 = 21일 전)")
    ap.add_argument("--recent-days", type=int, default=5,
                    help="'최근' 구간 일수 (사전등록 5거래일)")
    ap.add_argument("--json", default=None, help="원자료 JSON 저장 경로")
    ap.add_argument("--db", default=RAW_DB)
    args = ap.parse_args(argv)

    utf8_console()
    guard_intraday("ofi_norm_distribution_probe")

    since = args.since or (datetime.date.today() - datetime.timedelta(days=21)).isoformat()
    byday, missing = load_series(args.db, args.feature, since)
    if not byday:
        print("표본 없음 — %s 이후 raw_features에 %s 키가 없다" % (since, args.feature))
        return 1
    rows = summarize(byday, args.feature)
    text = render(rows, args.feature, missing, args.recent_days)
    print(text)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"feature": args.feature, "since": since,
                       "threshold": IDENTITY_STD_THRESHOLD,
                       "windows": list(WINDOWS), "rows": rows}, f,
                      ensure_ascii=False, indent=2)
        print("JSON 저장: %s" % args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())

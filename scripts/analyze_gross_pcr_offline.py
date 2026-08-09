# -*- coding: utf-8 -*-
"""[MW0601 451차 Phase 0-3] gross PCR 오프라인 분석 — `[CybosProbe][RAW]` 덤프 기반.

## 왜 이 스크립트가 성립하는가

450차 TODO는 "gross는 로그에 기록된 적이 없어 오프라인 검증이 불가"라며 라이브 프로브를
선행조건으로 걸어놨다. **그 판단은 틀렸다**(451차 후속3). `api_connector._probe_investor_tr`가
**세션당 progid별 1회** `CpSysDib.CpSvrNew7221`의 행×열 격자를 통째로
`logs/YYYYMMDD_PROBE.log`에 남기고 있었고, 수십 거래일치가 이미 쌓여 있다.

7221 격자(우리 코드 주석 기준, 열 0~14 구간):
    행 2=선물, 3=옵션콜, 4=옵션풋
    열 0·1·2 = 개인 매도·매수·순매수
    열 3·4·5 = 외인 매도·매수·순매수   ← **열3·열4가 gross다**
    열 6·7·8 = 기관 매도·매수·순매수

현재 `PCRStore`는 **순매수(열5)** 만 쓴다. 순매수는 매수·매도가 상쇄된 잔차라 스케일이
요동하고(450차가 실측), 그래서 절대 임계 가드가 원리적으로 맞을 수 없었다.

## 이 스크립트가 답하는 것

1. gross(열3·열4)와 net(열5)의 **스케일 차이** — 가드 통과율이 실제로 갈리는가
2. gross PCR(put_gross/call_gross)과 net PCR의 **분포·안정성** 차이
3. net PCR의 알려진 두 병리(캡 고착, 중앙값 편향)가 gross에서 완화되는가

## 🔴 한계 — 결론을 넘겨짚지 말 것

- 덤프는 **하루 1건(장 시작 직후 09:02 스냅샷)** 이다. **일중 분포는 볼 수 없다.**
  → 일간 스케일 판정에는 충분하지만 **가드 임계 재설정의 근거로는 부족**하다.
    임계 재보정은 병행 기록으로 일중 표본을 쌓은 뒤에 할 것.
- 2026-08-09 이전 덤프는 **열 15에서 절단**돼 있다(451차 후속4에서 폭을 넓혔다).
  열3·열4는 절단 범위 안이라 이 분석에는 영향이 없다.
- 7221 입력이 `ord('1')`(옵션금액/선물계약)이므로 옵션 값의 단위는 **금액**이다.

실행:
    python scripts/analyze_gross_pcr_offline.py
    python scripts/analyze_gross_pcr_offline.py --json out.json
"""
from __future__ import print_function

import argparse
import ast
import glob
import io
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_GLOB = os.path.join(_ROOT, "logs", "2026*_PROBE.log")

ROW_CALL, ROW_PUT = 3, 4
COL_FI_SELL, COL_FI_BUY, COL_FI_NET = 3, 4, 5

# 450차가 교체하기 전의 구 가드. "만약 그대로였다면" 통과율 비교용 기준선이다.
LEGACY_MIN_CALL_ABS = 1000
# 450차가 배포한 현행 가드(`collection/options/pcr_store.py:PCR_MIN_ACTIVITY_ABS`).
CURRENT_MIN_ACTIVITY = 100
PCR_MAX = 5.0


def _to_int(v, default=0):
    try:
        return int(float(str(v).replace(",", "").strip()))
    except Exception:
        return default


def load_dumps():
    """PROBE 로그에서 날짜별 7221 격자를 뽑는다."""
    out = []
    for path in sorted(glob.glob(LOG_GLOB)):
        date = os.path.basename(path)[:8]
        line = None
        for enc in ("utf-8", "cp949"):
            try:
                with io.open(path, encoding=enc, errors="replace") as fp:
                    for l in fp:
                        if "CpSvrNew7221" in l and "rows_sample=" in l:
                            line = l
                            break
                break
            except Exception:
                continue
        if not line:
            continue
        m = re.search(r"rows_sample=(\[.*\])", line.strip())
        if not m:
            continue
        try:
            rows = ast.literal_eval(m.group(1))
        except Exception:
            continue
        if len(rows) <= ROW_PUT:
            continue
        c, p = rows[ROW_CALL], rows[ROW_PUT]
        out.append({
            "date": date,
            "call_sell": _to_int(c.get(COL_FI_SELL)), "call_buy": _to_int(c.get(COL_FI_BUY)),
            "call_net": _to_int(c.get(COL_FI_NET)),
            "put_sell":  _to_int(p.get(COL_FI_SELL)), "put_buy":  _to_int(p.get(COL_FI_BUY)),
            "put_net":   _to_int(p.get(COL_FI_NET)),
        })
    return out


def _pct(hits, n):
    return 100.0 * hits / float(n) if n else 0.0


def _median(xs):
    s = sorted(xs)
    n = len(s)
    if not n:
        return 0.0
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def analyze(rows):
    res = {"n_days": len(rows), "days": []}
    net_pcrs, gross_pcrs = [], []
    legacy_pass = cur_pass_net = cur_pass_gross = 0
    net_capped = gross_capped = 0

    for r in rows:
        call_g = r["call_sell"] + r["call_buy"]       # gross 활동량
        put_g = r["put_sell"] + r["put_buy"]
        call_n, put_n = abs(r["call_net"]), abs(r["put_net"])

        # 현행 PCRStore 산식을 그대로 재현(net 기반, 캡 적용)
        pcr_n = min(put_n / float(call_n), PCR_MAX) if call_n > 0 else None
        pcr_g = min(put_g / float(call_g), PCR_MAX) if call_g > 0 else None

        if call_n >= LEGACY_MIN_CALL_ABS:
            legacy_pass += 1
        if max(call_n, put_n) >= CURRENT_MIN_ACTIVITY:
            cur_pass_net += 1
        if max(call_g, put_g) >= CURRENT_MIN_ACTIVITY:
            cur_pass_gross += 1
        if pcr_n is not None:
            net_pcrs.append(pcr_n)
            if pcr_n >= PCR_MAX:
                net_capped += 1
        if pcr_g is not None:
            gross_pcrs.append(pcr_g)
            if pcr_g >= PCR_MAX:
                gross_capped += 1

        res["days"].append({
            "date": r["date"], "call_gross": call_g, "put_gross": put_g,
            "call_net_abs": call_n, "put_net_abs": put_n,
            "pcr_net": pcr_n, "pcr_gross": pcr_g,
        })

    n = len(rows)
    res["summary"] = {
        "legacy_guard_pass_pct": _pct(legacy_pass, n),
        "current_guard_pass_net_pct": _pct(cur_pass_net, n),
        "current_guard_pass_gross_pct": _pct(cur_pass_gross, n),
        "call_gross_min": min((d["call_gross"] for d in res["days"]), default=0),
        "call_gross_max": max((d["call_gross"] for d in res["days"]), default=0),
        "call_net_abs_min": min((d["call_net_abs"] for d in res["days"]), default=0),
        "call_net_abs_max": max((d["call_net_abs"] for d in res["days"]), default=0),
        "pcr_net_median": _median(net_pcrs),
        "pcr_gross_median": _median(gross_pcrs),
        "pcr_net_capped_pct": _pct(net_capped, len(net_pcrs)),
        "pcr_gross_capped_pct": _pct(gross_capped, len(gross_pcrs)),
    }
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="", help="결과 JSON 저장 경로")
    ap.add_argument("--all", action="store_true", help="일자별 표 전부 출력")
    args = ap.parse_args()

    rows = load_dumps()
    if not rows:
        print("PROBE 로그에서 CpSvrNew7221 덤프를 찾지 못했습니다: %s" % LOG_GLOB)
        return 1

    res = analyze(rows)
    s = res["summary"]

    print("gross PCR 오프라인 분석 — %d거래일 (%s ~ %s)"
          % (res["n_days"], rows[0]["date"], rows[-1]["date"]))
    print("출처: [CybosProbe][RAW] 세션당 1회 덤프 (장 시작 직후 스냅샷 — 일중 분포 아님)")
    print()

    print("[1] 외인 콜 스케일 — gross vs net")
    print("    gross(매도+매수) : %8d ~ %8d" % (s["call_gross_min"], s["call_gross_max"]))
    print("    net(|순매수|)    : %8d ~ %8d" % (s["call_net_abs_min"], s["call_net_abs_max"]))
    print()

    print("[2] 가드 통과율")
    print("    구 가드 net |call| >= %-5d : %5.1f%%   (450차가 교체한 그 가드)"
          % (LEGACY_MIN_CALL_ABS, s["legacy_guard_pass_pct"]))
    print("    현행 net   max(|c|,|p|) >= %-3d : %5.1f%%" % (CURRENT_MIN_ACTIVITY, s["current_guard_pass_net_pct"]))
    print("    현행 gross max( c , p ) >= %-3d : %5.1f%%" % (CURRENT_MIN_ACTIVITY, s["current_guard_pass_gross_pct"]))
    print()

    print("[3] PCR 분포 — net의 알려진 두 병리가 gross에서 완화되는가")
    print("    중앙값   net %.3f  /  gross %.3f   (1.0=중립)"
          % (s["pcr_net_median"], s["pcr_gross_median"]))
    print("    캡(%.1f) 고착률  net %5.1f%%  /  gross %5.1f%%"
          % (PCR_MAX, s["pcr_net_capped_pct"], s["pcr_gross_capped_pct"]))
    print()

    if args.all:
        print("%-9s %10s %10s %10s %10s %8s %8s"
              % ("date", "call_gross", "put_gross", "|call_net|", "|put_net|", "pcr_net", "pcr_gr"))
        for d in res["days"]:
            print("%-9s %10d %10d %10d %10d %8s %8s"
                  % (d["date"], d["call_gross"], d["put_gross"], d["call_net_abs"],
                     d["put_net_abs"],
                     "%.3f" % d["pcr_net"] if d["pcr_net"] is not None else "-",
                     "%.3f" % d["pcr_gross"] if d["pcr_gross"] is not None else "-"))
        print()

    print("⚠ 한계: 하루 1건(장 시작 직후) 스냅샷이다. 일중 분포는 이 데이터로 알 수 없으므로")
    print("  **가드 임계 재설정의 근거로 쓰지 말 것** — 병행 기록으로 일중 표본을 쌓은 뒤 판단.")

    if args.json:
        with io.open(args.json, "w", encoding="utf-8") as fp:
            fp.write(json.dumps(res, ensure_ascii=False, indent=2))
        print("JSON 저장: %s" % args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())

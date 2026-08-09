# -*- coding: utf-8 -*-
"""[MW0601 453차 / QDQ Phase 2] CVD 앵커 대조 리포트 — 읽기 전용.

근거: `docs/Spec for feature/Validation for feature/QDQ_Phase2_구현계획_2026-08-09.md`
상위: 같은 폴더 `QDQ_도입_손익분석_및_구현계획_2026-08-09.md` §2(발견 A)·§5 Phase 2

**이 리포트가 답하는 단 하나의 질문**

    anchor_buy_share가 0.50 근방인가, 0.63 근방인가?

    0.50 근방 → 발견 A(체결구분 파싱 결함) 라이브 확정 → Phase 3 착수 가능
    0.63 근방 → 매수 편향이 시장 실체 → 진단이 틀렸다 → Phase 3 취소

Phase 0(앵커·섀도 계측 적재)과 Phase 1(복구 경로 파괴 차단)은 이 판정을 내리기
위한 배선이었다. 나머지 지표는 전부 이 판정의 신뢰도를 재는 보조다.

**무엇을 대조하나 — 두 쌍**

    legacy vs anchor   buy_vol      vs anchor_buy   지금 라이브가 얼마나 틀렸나
    shadow vs anchor   buy_vol_flag vs anchor_buy   Phase 3 수정안이 정답지와 맞나

두 번째가 핵심이다. 0에 수렴해야 "올바른 체결구분 파싱 = 서버 정답지"가 증명된다.
크면 분류 방식 자체의 한계이므로 Phase 3을 앵커 직접 사용으로 재설계해야 한다.

**설계상 반드시 지킨 것 3가지**

  1) **읽기 전용.** raw_data.db를 SELECT하고 md/json을 쓰는 것 외에 아무것도 하지
     않는다. 게이팅·종료코드 신호 없음(항상 0, 생성 실패만 1) — CB②·CB③-P4·
     FP-CRITICAL이 "계측이 덜 익은 상태에서 차단부터 켰다가 상시 발동으로 껐다"는
     같은 실패를 겪었다(CLAUDE.md §2). 네 번째를 만들지 않는다.
  2) **못 재면 못 잰다고 말한다.** 계측 0행에서 0%를 계산해 통과시키지 않는다
     (`toxicity_block_shadow`가 자기모순 조건으로 3개월간 0건인 채 방치된
     402차 후속3의 교훈).
  3) **크기 축을 순/절대로 분리한다.** 봉끼리 상쇄되는 순 오차만 보면 오전 +100 /
     오후 −100이 0으로 보인다(QDQ 보고서 §1.3 `anchor_diff` 경고의 집계판).
     판정은 절대 오차로 한다.

실행:
  python scripts/generate_cvd_anchor_report.py                # 최근 5거래일
  python scripts/generate_cvd_anchor_report.py --days 1 --stdout   # 배포 첫날 판정
  python scripts/generate_cvd_anchor_report.py --out-dir /tmp/x --no-prune
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sqlite3
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

RAW_DB = os.path.join(ROOT, "data", "db", "raw_data.db")
REPORT_STEM = "cvd_anchor"

# ── 판정 임계 ────────────────────────────────────────────────────────────────
# ⚠ 전부 **지금 정한 판단 기준**이며 캘리브레이션된 값이 아니다. QDQ 보고서 §6의
#   3단계(관측 2~4주 → p99를 warn, 그 1.5~2배를 fail → 운영)를 아직 안 거쳤다.
#   임계를 바꾸면 반드시 커밋 이력으로 남길 것 — "조용히 완화된 임계치가 가장 위험하다".
MIN_BARS = 300                  # 판정 가능 최소 계측 봉수 (약 1거래일)
BALANCED_LO, BALANCED_HI = 0.45, 0.55   # anchor_buy_share "균형" 구간
BIASED_MIN = 0.58               # legacy가 기존 편향(실측 0.631)을 재현하는지
IDENTITY_MAX_VIOLATION = 0.01   # I1 위반율 상한 — 넘으면 앵커 자체를 못 믿는다
SHADOW_MATCH_MAX = 0.02         # shadow vs anchor 절대괴리 허용 (거래량 대비)

# 판정 코드
V_NO_DATA = "⏳ 계측 미개시/부족"
V_ANCHOR_BAD = "⚠ 앵커 신뢰 불가"
V_CONFIRMED = "✅ 발견 A 확정"
V_REFUTED = "❌ 진단 오류 — Phase 3 취소"
V_AMBIGUOUS = "⚠ 판정 애매 — 표본 확대 필요"


def git_hash():
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
            stderr=subprocess.STDOUT, timeout=10)
        return out.decode("utf-8", "replace").strip()
    except Exception:
        return None


def _pc_dir_name():
    """산출물 폴더로 쓸 PC 이름 — 405차 P0-5/408차 규약과 동일(경고 포함)."""
    try:
        from utils.db_utils import pc_id
        raw = pc_id()
    except Exception:
        try:
            import platform as _pf
            host = _pf.node() or ""
            m = re.search(r"(MW\d{4})", host, re.IGNORECASE)
            raw = m.group(1).upper() if m else (host[:32] or "UNKNOWN")
        except Exception:
            raw = "UNKNOWN"
    safe = re.sub(r'[\\/:*?"<>|\s]+', "_", raw).strip("._") or "UNKNOWN"
    if not re.match(r"^MW\d{4}$", safe):
        print("[경고] PC 식별자가 MW#### 형식이 아니다: %r → 산출물 폴더 '%s' 사용. "
              "새 PC라면 호스트명을 확인할 것." % (raw, safe), file=sys.stderr)
    return safe


def _pct(x):
    return "—" if x is None else "%.2f%%" % (100.0 * x)


def _share(a, b):
    """a / (a+b) — 분모 0이면 None(계산 불가). 0.0으로 뭉개지 않는다."""
    tot = a + b
    return (float(a) / tot) if tot else None


# ── 수집 ────────────────────────────────────────────────────────────────────

def load_bars(db_path, days):
    """최근 `days` 거래일의 raw_candles 행. 없으면 빈 리스트."""
    if not os.path.exists(db_path):
        return [], []
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        dates = [r[0] for r in con.execute(
            "SELECT DISTINCT substr(ts,1,10) d FROM raw_candles ORDER BY d DESC "
            "LIMIT ?", (days,)).fetchall()]
        if not dates:
            return [], []
        cutoff = min(dates)
        rows = con.execute(
            "SELECT ts, volume, buy_vol, sell_vol, anchor_buy, anchor_sell,"
            "       buy_vol_flag, sell_vol_flag, bar_recovered "
            "FROM raw_candles WHERE substr(ts,1,10) >= ? ORDER BY ts",
            (cutoff,)).fetchall()
        return [dict(r) for r in rows], sorted(dates)
    finally:
        con.close()


# ── 3축 대조 ────────────────────────────────────────────────────────────────

def three_axis(bars, own_key):
    """`own_key`(자체 매수량) vs `anchor_buy`(서버 정답지) 3축 대조.

    반환 dict — 계측 봉이 없으면 n=0에 나머지 None.

      n            대조 가능 봉수 (양쪽 다 계측된 봉)
      volume       그 봉들의 거래량 합
      mag_net      ①-순  |Σd| / Σvolume       ← 봉끼리 상쇄된다
      mag_abs      ①-절대 Σ|d| / Σvolume      ← 판정은 이쪽
      sign_bias    ② 불일치 봉 중 '자체 < 앵커' 비율 (1.0=자체가 계속 과소)
      concentration ③ 불일치 봉 비율
      max_abs_bar  최대 단일봉 절대 괴리(계약)
      worst_ts     그 봉의 ts

    `mag_net`과 `mag_abs`가 크게 벌어지면 그 자체가 "오차가 방향을 바꿔가며 났다"는
    정보다 — 순 오차만 보면 0으로 보이는 사고를 §2-1에서 명시적으로 갈라놓았다.
    """
    diffs = []
    vol = 0
    for b in bars:
        own, anc = b.get(own_key), b.get("anchor_buy")
        if own is None or anc is None:
            continue
        diffs.append((b["ts"], float(own) - float(anc)))
        vol += int(b.get("volume") or 0)
    n = len(diffs)
    if n == 0 or vol <= 0:
        return {"n": n, "volume": vol, "mag_net": None, "mag_abs": None,
                "sign_bias": None, "concentration": None,
                "max_abs_bar": None, "worst_ts": None}
    net = sum(d for _, d in diffs)
    absum = sum(abs(d) for _, d in diffs)
    mism = [(t, d) for t, d in diffs if d != 0]
    under = sum(1 for _, d in mism if d < 0)
    worst_ts, worst = max(diffs, key=lambda x: abs(x[1]))
    return {
        "n": n, "volume": vol,
        "mag_net": abs(net) / vol,
        "mag_abs": absum / vol,
        "sign_bias": (float(under) / len(mism)) if mism else None,
        "concentration": float(len(mism)) / n,
        "max_abs_bar": abs(worst), "worst_ts": worst_ts,
    }


def identities(bars):
    """항등식 3종 위반 집계. I2 잔차는 부호를 나눠 센다(음수 = 이중 집계 버그)."""
    out = {"i1_n": 0, "i1_bad": 0, "i1_max": 0.0,
           "i2_n": 0, "i2_unclassified": 0, "i2_negative_bars": 0,
           "i3_n": 0, "i3_bad": 0, "i3_bad_legacy_era": 0, "i3_bad_dates": []}
    for b in bars:
        v = int(b.get("volume") or 0)
        ab, as_ = b.get("anchor_buy"), b.get("anchor_sell")
        if ab is not None and as_ is not None:
            out["i1_n"] += 1
            d = (int(ab) + int(as_)) - v
            if d != 0:
                out["i1_bad"] += 1
                out["i1_max"] = max(out["i1_max"], abs(d))
        fb, fs = b.get("buy_vol_flag"), b.get("sell_vol_flag")
        if fb is not None and fs is not None:
            out["i2_n"] += 1
            resid = v - (int(fb) + int(fs))   # 양수 = 미분류 틱 물량(정상)
            if resid > 0:
                out["i2_unclassified"] += resid
            elif resid < 0:
                out["i2_negative_bars"] += 1   # 음수 = 이중 집계 (버그)
        bv, sv = b.get("buy_vol"), b.get("sell_vol")
        if bv is not None and sv is not None:
            out["i3_n"] += 1
            if (int(bv) + int(sv)) != v:
                out["i3_bad"] += 1
                # [453차] 452차 Phase 1 이전에 생성된 행인지 구분한다.
                # `bar_recovered`가 NULL이면 그 열이 없던 시절(=452차 이전)의 행이고,
                # 08-04처럼 구 복구 경로가 buy/sell을 0으로 파괴한 봉(실측 55봉)이
                # 관찰창에 들어온 것이다. 이걸 구분하지 않으면 "수집기 회귀"를
                # 의심하게 만들어 없는 버그를 쫓게 된다.
                if b.get("bar_recovered") is None:
                    out["i3_bad_legacy_era"] += 1
                d = str(b["ts"])[:10]
                if d not in out["i3_bad_dates"]:
                    out["i3_bad_dates"].append(d)
    return out


def daily_shares(bars):
    """일자별 매수비중 3종 — legacy / shadow / anchor."""
    agg = {}
    for b in bars:
        d = str(b["ts"])[:10]
        a = agg.setdefault(d, dict.fromkeys(
            ["lb", "ls", "fb", "fs", "ab", "as_", "n", "meas"], 0))
        a["n"] += 1
        a["lb"] += int(b.get("buy_vol") or 0)
        a["ls"] += int(b.get("sell_vol") or 0)
        if b.get("buy_vol_flag") is not None:
            a["fb"] += int(b["buy_vol_flag"]); a["fs"] += int(b.get("sell_vol_flag") or 0)
        if b.get("anchor_buy") is not None:
            a["meas"] += 1
            a["ab"] += int(b["anchor_buy"]); a["as_"] += int(b.get("anchor_sell") or 0)
    rows = []
    for d in sorted(agg):
        a = agg[d]
        rows.append({
            "date": d, "bars": a["n"], "anchor_bars": a["meas"],
            "legacy": _share(a["lb"], a["ls"]),
            "shadow": _share(a["fb"], a["fs"]),
            "anchor": _share(a["ab"], a["as_"]),
        })
    return rows


def decide(cov, ident, legacy_share, anchor_share, shadow_vs_anchor):
    """히어로 판정 + 사유. (verdict, reason, next_action)"""
    n = cov["anchor_bars"]
    if n < MIN_BARS:
        if n == 0:
            return (V_NO_DATA,
                    "앵커 계측 행이 0이다. Phase 0 배포 후 거래일이 아직 지나지 않았거나, "
                    "원천이 22/23 필드를 주지 않는다.",
                    "다음 거래일 장 마감 후 재실행. 그래도 0이면 SYSTEM 로그에서 "
                    "`[CVD-ANCHOR][UNAVAIL]`을 확인할 것 — 그 경고가 있으면 필드 가용성 "
                    "가설이 반증된 것이고 Phase 3·4를 재설계해야 한다.")
        return (V_NO_DATA,
                "앵커 계측 %d봉 — 판정 최소치 %d봉 미달." % (n, MIN_BARS),
                "거래일을 더 쌓은 뒤 재실행.")

    i1_rate = (float(ident["i1_bad"]) / ident["i1_n"]) if ident["i1_n"] else None
    if i1_rate is not None and i1_rate > IDENTITY_MAX_VIOLATION:
        return (V_ANCHOR_BAD,
                "항등식 I1(anchor_buy+anchor_sell==volume) 위반율 %s > %s. "
                "서버 정답지가 우리 거래량과 맞지 않으므로 아래 비중 대조를 신뢰할 수 없다."
                % (_pct(i1_rate), _pct(IDENTITY_MAX_VIOLATION)),
                "필드 인덱스(22=누적체결매도 / 23=누적체결매수) 재확인. "
                "공식 캡처본에서는 13=22+23이 정확히 성립한다.")

    if anchor_share is None:
        return (V_ANCHOR_BAD, "앵커 매수비중을 계산할 수 없다(분모 0).",
                "앵커 열이 전부 0인지 확인.")

    if BALANCED_LO <= anchor_share <= BALANCED_HI and (
            legacy_share is not None and legacy_share >= BIASED_MIN):
        extra = ""
        if shadow_vs_anchor is not None and shadow_vs_anchor > SHADOW_MATCH_MAX:
            extra = (" 다만 shadow vs anchor 절대괴리 %s > %s — 올바른 체결구분 파싱만으로는 "
                     "정답지에 도달하지 못한다. Phase 3은 **앵커 직접 사용**으로 설계할 것."
                     % (_pct(shadow_vs_anchor), _pct(SHADOW_MATCH_MAX)))
        return (V_CONFIRMED,
                "앵커 매수비중 %s(균형)인데 라이브 legacy는 %s(편향) — 발견 A가 "
                "라이브에서 재현됐다.%s" % (_pct(anchor_share), _pct(legacy_share), extra),
                "Phase 3 착수 가능. 단 섀도 20거래일 누적 후, 정규화 포화"
                "(features/technical/cvd.py:104)를 **동시에** 고칠 것. "
                "틱 원본이 없어 2026-06-08~전환일 구간은 영구 편향(백필 불가)이므로 "
                "학습 창 분리가 필요하다.")

    if anchor_share >= BIASED_MIN:
        return (V_REFUTED,
                "앵커 매수비중이 %s로 legacy(%s)와 동급이다. 매수 편향은 계측 결함이 "
                "아니라 시장 실체이거나, 두 계열이 같은 결함을 공유한다."
                % (_pct(anchor_share), _pct(legacy_share)),
                "🔴 Phase 3(CVD 전환) 취소. 발견 A의 근거를 재검토하고 "
                "DECISION_LOG 452차 항목을 정정할 것.")

    return (V_AMBIGUOUS,
            "앵커 %s / legacy %s — 균형(%.2f~%.2f)에도 편향(≥%.2f)에도 명확히 들지 않는다."
            % (_pct(anchor_share), _pct(legacy_share),
               BALANCED_LO, BALANCED_HI, BIASED_MIN),
            "표본을 더 쌓고 재판정. 일자별 표(§4)에서 특정일 쏠림 여부를 먼저 볼 것.")


# ── 리포트 ──────────────────────────────────────────────────────────────────

def build_report(days):
    today = datetime.date.today()
    pc = _pc_dir_name()
    bars, dates = load_bars(RAW_DB, days)

    cov = {
        "bars": len(bars),
        "dates": dates,
        "anchor_bars": sum(1 for b in bars if b.get("anchor_buy") is not None),
        "shadow_bars": sum(1 for b in bars if b.get("buy_vol_flag") is not None),
        "recovered_bars": sum(1 for b in bars if b.get("bar_recovered") == 1),
    }
    ident = identities(bars)
    ax_legacy = three_axis(bars, "buy_vol")
    ax_shadow = three_axis(bars, "buy_vol_flag")
    daily = daily_shares(bars)

    tot = {"lb": 0, "ls": 0, "fb": 0, "fs": 0, "ab": 0, "as_": 0}
    for b in bars:
        tot["lb"] += int(b.get("buy_vol") or 0); tot["ls"] += int(b.get("sell_vol") or 0)
        if b.get("buy_vol_flag") is not None:
            tot["fb"] += int(b["buy_vol_flag"]); tot["fs"] += int(b.get("sell_vol_flag") or 0)
        if b.get("anchor_buy") is not None:
            tot["ab"] += int(b["anchor_buy"]); tot["as_"] += int(b.get("anchor_sell") or 0)
    legacy_share = _share(tot["lb"], tot["ls"])
    shadow_share = _share(tot["fb"], tot["fs"])
    anchor_share = _share(tot["ab"], tot["as_"])

    verdict, reason, action = decide(
        cov, ident, legacy_share, anchor_share, ax_shadow["mag_abs"])

    metrics = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "pc": pc, "git": git_hash(), "days_requested": days,
        "coverage": cov, "identities": ident,
        "axis_legacy_vs_anchor": ax_legacy, "axis_shadow_vs_anchor": ax_shadow,
        "shares": {"legacy": legacy_share, "shadow": shadow_share,
                   "anchor": anchor_share},
        "daily": daily,
        "verdict": verdict, "reason": reason, "next_action": action,
        "thresholds": {
            "MIN_BARS": MIN_BARS, "BALANCED": [BALANCED_LO, BALANCED_HI],
            "BIASED_MIN": BIASED_MIN,
            "IDENTITY_MAX_VIOLATION": IDENTITY_MAX_VIOLATION,
            "SHADOW_MATCH_MAX": SHADOW_MATCH_MAX,
            "calibrated": False,
        },
    }

    L = []
    L.append("# CVD 앵커 대조 리포트 — %s · %s" % (pc, today.strftime("%Y-%m-%d")))
    L.append("")
    L.append("> 생성: `scripts/generate_cvd_anchor_report.py` (읽기 전용) · "
             "git `%s` · 관찰창 최근 %d거래일" % (metrics["git"] or "?", days))
    L.append("> 근거: `docs/Spec for feature/Validation for feature/"
             "QDQ_Phase2_구현계획_2026-08-09.md`")
    L.append("")

    # ── 히어로 ──
    L.append("## 판정")
    L.append("")
    L.append("### %s" % verdict)
    L.append("")
    L.append("%s" % reason)
    L.append("")
    L.append("**다음 조치**: %s" % action)
    L.append("")
    L.append("| 매수비중 | 값 | 의미 |")
    L.append("|---|---|---|")
    L.append("| **앵커**(서버 정답지) | **%s** | 이 값이 판정을 가른다 — 0.50 근방이면 발견 A 확정 |"
             % _pct(anchor_share))
    L.append("| 섀도(올바른 체결구분) | %s | Phase 3 전환 대상의 값 |" % _pct(shadow_share))
    L.append("| 라이브 legacy(현행) | %s | 44거래일 실측 63.08%%를 재현하는지 |" % _pct(legacy_share))
    L.append("")

    # ── §1 커버리지 ──
    L.append("## §1 계측 커버리지")
    L.append("")
    L.append("| 항목 | 값 |")
    L.append("|---|---|")
    L.append("| 관찰창 봉수 | %d (거래일 %d개: %s) |"
             % (cov["bars"], len(dates),
                ", ".join(dates) if len(dates) <= 6 else
                "%s ~ %s" % (dates[0], dates[-1])))
    L.append("| 앵커 계측 봉 | %d (%s) |"
             % (cov["anchor_bars"],
                _pct(float(cov["anchor_bars"]) / cov["bars"]) if cov["bars"] else "—"))
    L.append("| 섀도 계측 봉 | %d (%s) |"
             % (cov["shadow_bars"],
                _pct(float(cov["shadow_bars"]) / cov["bars"]) if cov["bars"] else "—"))
    L.append("| 복구 재처리 봉(`bar_recovered=1`) | %d |" % cov["recovered_bars"])
    L.append("")
    if cov["anchor_bars"] == 0:
        L.append("> ⏳ **앵커 계측 0행.** Phase 0(2026-08-09 배포) 이후 거래일이 지나지 "
                 "않았으면 정상이다. 거래일이 지났는데도 0이면 SYSTEM 로그의 "
                 "`[CVD-ANCHOR][UNAVAIL]`을 확인할 것 — 원천이 22/23을 주지 않는다는 뜻이며 "
                 "필드 가용성 가설(공식 xls 캡처본 기준)이 반증된 것이다.")
        L.append("")
    if cov["recovered_bars"] > 0:
        L.append("> 🔴 **453차 D1 회귀 의심**: 복구 재처리 봉이 %d개 있다. D1 배포 후로는 "
                 "`bar_recovered=1`이 **새로 생기지 않아야** 한다(복구가 파이프라인을 "
                 "재실행하지 않으므로). 관찰창에 453차 이전 봉이 섞였는지 먼저 확인하고, "
                 "아니면 `_try_pipeline_recovery` 경로를 점검할 것."
                 % cov["recovered_bars"])
        L.append("")

    # ── §2 항등식 ──
    L.append("## §2 항등식")
    L.append("")
    L.append("부등식(`|CVD| <= volume`)은 약하다 — 매수 60/매도 30/총 100이면 10이 "
             "증발해도 통과한다. 항등식만이 분류 로직 버그를 잡는다(QDQ 보고서 §2.3).")
    L.append("")
    L.append("| # | 항등식 | 대상 | 위반 | 비고 |")
    L.append("|---|---|---|---|---|")
    _i1r = (float(ident["i1_bad"]) / ident["i1_n"]) if ident["i1_n"] else None
    L.append("| I1 | `anchor_buy + anchor_sell == volume` | %d봉 | %d (%s) | 최대 잔차 %g계약 |"
             % (ident["i1_n"], ident["i1_bad"], _pct(_i1r), ident["i1_max"]))
    L.append("| I2 | `buy_vol_flag + sell_vol_flag == volume` | %d봉 | 잔차 %d계약 | "
             "양수=미분류 틱(정상) · **음수 봉 %d개** |"
             % (ident["i2_n"], ident["i2_unclassified"], ident["i2_negative_bars"]))
    L.append("| I3 | `buy_vol + sell_vol == volume` | %d봉 | %d | 라이브 경로는 구조상 항상 성립 |"
             % (ident["i3_n"], ident["i3_bad"]))
    L.append("")
    if ident["i2_negative_bars"] > 0:
        L.append("> 🔴 **I2 음수 잔차 %d봉** — 섀도 합이 거래량을 초과했다. 미분류가 아니라 "
                 "**이중 집계 버그**다. `collection/cybos/realtime_data.py`의 섀도 누적 경로를 "
                 "점검할 것." % ident["i2_negative_bars"])
        L.append("")
    if ident["i3_bad"] > 0:
        _legacy = ident["i3_bad_legacy_era"]
        _new = ident["i3_bad"] - _legacy
        L.append("> **I3 위반 %d봉** (%s) — 라이브 수집 경로에서는 `buy_v`/`sell_v`가 같은 "
                 "`volume`에서 갈라지므로 구조상 깨질 수 없다."
                 % (ident["i3_bad"], ", ".join(ident["i3_bad_dates"])))
        if _legacy:
            L.append("> ")
            L.append("> - **452차 이전 생성 %d봉** (`bar_recovered` IS NULL): 구 복구 경로가 "
                     "`buy_vol: 0`을 하드코딩해 원본을 파괴한 봉이다(발견 C, 전체 실측 55봉). "
                     "**이미 규명·수정된 사안이며 원본 소실로 복구 불가** — 새 버그가 아니다. "
                     "관찰창이 452차 배포일 이후로 넘어가면 자연히 사라진다." % _legacy)
        if _new:
            L.append("> ")
            L.append("> - 🔴 **452차 이후 생성 %d봉**: 이건 **새 결함이다.** Phase 1이 막았어야 할 "
                     "경로가 뚫렸거나 다른 쓰기 경로가 있다. `utils/db_utils.py:save_candle*`와 "
                     "`main.py:_bar_from_raw_candle_row` 경로를 점검할 것." % _new)
        L.append("")

    # ── §3 3축 ──
    L.append("## §3 3축 대조")
    L.append("")
    L.append("**크기 축을 순/절대로 나눈 이유**: 순 오차는 봉끼리 상쇄된다 — 오전 +100, "
             "오후 −100이면 0으로 보인다(QDQ 보고서 §1.3 `anchor_diff` 경고의 집계판). "
             "**판정은 절대 오차로 한다.** 두 값이 벌어지면 그 자체가 '오차가 방향을 "
             "바꿔가며 났다'는 정보다.")
    L.append("")
    L.append("| 축 | legacy vs 앵커 | 섀도 vs 앵커 | 읽는 법 |")
    L.append("|---|---|---|---|")
    L.append("| 대조 봉수 | %d | %d | 양쪽 다 계측된 봉 |"
             % (ax_legacy["n"], ax_shadow["n"]))
    L.append("| ①-순 `\\|Σd\\|/Σvol` | %s | %s | 상쇄 있음 — 참고용 |"
             % (_pct(ax_legacy["mag_net"]), _pct(ax_shadow["mag_net"])))
    L.append("| **①-절대 `Σ\\|d\\|/Σvol`** | **%s** | **%s** | **판정 지표** |"
             % (_pct(ax_legacy["mag_abs"]), _pct(ax_shadow["mag_abs"])))
    L.append("| ② 부호편향 | %s | %s | 1.0=자체가 계속 과소, 0=계속 과대 |"
             % (_pct(ax_legacy["sign_bias"]), _pct(ax_shadow["sign_bias"])))
    L.append("| ③ 집중도 | %s | %s | 불일치 봉 비율 — 낮으면 소수 봉에 몰림 |"
             % (_pct(ax_legacy["concentration"]), _pct(ax_shadow["concentration"])))
    L.append("| 최대 단일봉 괴리 | %s | %s | |"
             % ("—" if ax_legacy["max_abs_bar"] is None
                else "%g계약 (%s)" % (ax_legacy["max_abs_bar"], ax_legacy["worst_ts"]),
                "—" if ax_shadow["max_abs_bar"] is None
                else "%g계약 (%s)" % (ax_shadow["max_abs_bar"], ax_shadow["worst_ts"])))
    L.append("")
    L.append("- **legacy vs 앵커**가 커야 정상이다 — 지금 라이브가 틀렸다는 증거다.")
    L.append("- **섀도 vs 앵커**는 0에 수렴해야 한다. 크면 올바른 체결구분 파싱만으로는 "
             "정답지에 도달하지 못한다는 뜻이고, Phase 3을 **앵커 직접 사용**으로 "
             "재설계해야 한다(허용 상한 %s)." % _pct(SHADOW_MATCH_MAX))
    L.append("")

    # ── §4 일자별 ──
    L.append("## §4 일자별 매수비중")
    L.append("")
    L.append("| 날짜 | 봉수 | 앵커계측 | legacy | 섀도 | **앵커** |")
    L.append("|---|---|---|---|---|---|")
    for r in daily:
        L.append("| %s | %d | %d | %s | %s | **%s** |"
                 % (r["date"], r["bars"], r["anchor_bars"],
                    _pct(r["legacy"]), _pct(r["shadow"]), _pct(r["anchor"])))
    L.append("")
    L.append("> 특정일만 튀면 그날의 시장 사건·재기동을 먼저 의심할 것. 전 거래일이 "
             "고르게 한쪽이면 구조적 결함이다(발견 A의 근거가 정확히 그 형태였다 — "
             "44거래일 **전부** 매수 50% 초과).")
    L.append("")

    # ── §5 임계 ──
    L.append("## §5 판정 임계 (미캘리브레이션)")
    L.append("")
    L.append("| 이름 | 값 | 용도 |")
    L.append("|---|---|---|")
    L.append("| `MIN_BARS` | %d | 판정 가능 최소 계측 봉수 |" % MIN_BARS)
    L.append("| `BALANCED` | %.2f ~ %.2f | 앵커 비중 '균형' 구간 |" % (BALANCED_LO, BALANCED_HI))
    L.append("| `BIASED_MIN` | %.2f | legacy가 기존 편향을 재현하는 하한 |" % BIASED_MIN)
    L.append("| `IDENTITY_MAX_VIOLATION` | %s | I1 위반 허용률 |" % _pct(IDENTITY_MAX_VIOLATION))
    L.append("| `SHADOW_MATCH_MAX` | %s | 섀도-앵커 절대괴리 허용 |" % _pct(SHADOW_MATCH_MAX))
    L.append("")
    L.append("⚠ **전부 지금 정한 판단 기준이며 캘리브레이션된 값이 아니다.** QDQ 보고서 §6의 "
             "3단계(관측 2~4주 → p99를 warn·1.5~2배를 fail → 운영)를 아직 안 거쳤다. "
             "임계를 바꾸면 반드시 커밋 이력으로 남길 것 — 조용히 완화된 임계치가 가장 위험하다.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("> 이 리포트는 **관측이다.** 게이팅하지 않고 종료코드로 후속 잡을 막지 않는다"
             "(항상 0). CB②·CB③-P4·FP-CRITICAL이 계측이 덜 익은 상태에서 차단부터 켰다가 "
             "상시 발동으로 꺼진 전례가 있어(CLAUDE.md §2), 네 번째를 만들지 않는다. "
             "Phase 3 전환은 이 판정 + 섀도 20거래일 + 사용자 승인을 거친다.")

    return "\n".join(L), metrics


def main():
    ap = argparse.ArgumentParser(description="CVD 앵커 대조 리포트 (읽기 전용)")
    ap.add_argument("--days", type=int, default=5,
                    help="관찰창(거래일). 기본 5 — 주간 체인 기준")
    ap.add_argument("--out-dir", default=None,
                    help="출력 폴더 오버라이드. 기본 docs/정기점검/금요일점검/<PC명>/ "
                         "— 지정 시 FIFO 보관정리는 하지 않는다")
    ap.add_argument("--keep", type=int, default=None,
                    help="FIFO 보관 주차 수. 기본 config/settings.py:"
                         "VALIDATION_REPORT_KEEP_WEEKS")
    ap.add_argument("--no-prune", action="store_true", help="이번 실행만 보관정리 생략")
    ap.add_argument("--stdout", action="store_true", help="리포트 본문을 콘솔에도 출력")
    args = ap.parse_args()

    if not os.path.exists(RAW_DB):
        print("raw_data.db 없음: %s" % RAW_DB, file=sys.stderr)
        return 1

    keep = args.keep
    if keep is None:
        try:
            from config.settings import VALIDATION_REPORT_KEEP_WEEKS
            keep = VALIDATION_REPORT_KEEP_WEEKS
        except Exception:
            keep = 4

    report_md, metrics = build_report(args.days)

    pc_name = metrics["pc"]
    out_dir = (os.path.abspath(args.out_dir) if args.out_dir else
               os.path.join(ROOT, "docs", "정기점검", "금요일점검", pc_name))
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.date.today().strftime("%Y%m%d")
    md_path = os.path.join(out_dir, "%s_report_%s.md" % (REPORT_STEM, stamp))
    json_path = os.path.join(out_dir, "%s_metrics_%s.json" % (REPORT_STEM, stamp))
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2, default=str)

    if args.stdout:
        print(report_md)
    print("저장: %s / %s" % (md_path, json_path))
    print("판정: %s | 앵커비중 %s / legacy %s | 앵커계측 %d봉"
          % (metrics["verdict"], _pct(metrics["shares"]["anchor"]),
             _pct(metrics["shares"]["legacy"]), metrics["coverage"]["anchor_bars"]))

    # 쓰기가 끝난 뒤에만 FIFO — 중간에 죽어도 이번 주 파일은 이미 디스크에 있다.
    if args.out_dir:
        print("보관정리: --out-dir 사용 중이라 건너뜀")
    elif args.no_prune:
        print("보관정리: --no-prune")
    else:
        try:
            from scripts.campaign_report_paths import prune
            removed = prune(pc_name, keep, stem=REPORT_STEM)
            if removed:
                print("보관정리: %d주 초과분 %d개 삭제 — %s"
                      % (keep, len(removed),
                         ", ".join(os.path.basename(p) for p in removed)))
            elif keep and keep > 0:
                print("보관정리: 삭제 대상 없음 (보관 %d주)" % keep)
        except Exception as e:
            print("[경고] 보관정리 실패(무해, 다음 주 재시도): %s" % e, file=sys.stderr)

    # 게이팅하지 않는다 — 판정 결과와 무관하게 항상 0 (§2-5).
    return 0


if __name__ == "__main__":
    sys.exit(main())

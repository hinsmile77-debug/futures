# scripts/checklist_ev_regression.py
"""
[368차 신설] 체크리스트 11개 항목·조합별 순EV 기여도 회귀분석.

배경: 366차가 "pass_count 단순합산(몇 개 통과했는지 개수만 봄)이 실현 엣지와
반비례하는 구조적 문제"를 진단했고, 368차가 그 개별 사례(10_chase+6_foreign
동시실패, 0722 MW0601 실측)를 섀도 채널 [16]으로 등록했다. 이 스크립트는
그 다음 단계 — "몇 개 조합을 손으로 골라 검증"하는 대신, 11개 항목 전체를
회귀 피처로 구성해 어떤 항목(및 2-way 조합)이 순EV와 가장 강하게 연관되는지
데이터 기반으로 스캔한다.

방법:
  1. logs/*_TRADE.log의 [진입체크] 라인을 정규식으로 파싱해 11개 항목의
     ✅/❌를 이진 피처로 만든다.
  2. trades.db 체결 결과(entry_ts)와 매칭한다 — [진입체크] 로그와 실제
     체결([Position] 진입) 사이 0~5초 지연이 있어(§ eval_chase_foreign_combo_watch
     와 동일 이슈) 가장 가까운 직전 [진입체크] 라인을 채택한다.
  3. 컬럼분산이 0인 항목(해당 호라이즌 그룹에서 항상 면제=True인 CORE 대체
     항목 등)은 회귀에서 제외한다.
  4. Ridge 회귀(표준화된 피처, 작은 alpha)로 개별 항목 계수를 추정하고,
     보조지표로 항목별 단순 평균EV 차이(pass 평균 - fail 평균)를 함께 보고한다.
  5. 동시실패 빈도가 min_pair_n 이상인 모든 2-way 조합에 대해 "두 항목이
     함께 실패했을 때"의 표본 평균EV·승률을 스캔해 순위를 매긴다.

주의 — 이 스크립트는 오프라인 읽기전용 진단이다. 실거래 경로에 전혀
연결되지 않으며, 결과를 즉시 정책화하지 않는다(§9 사전등록 원칙). 로그
보존기간(~20일 안팎)에 묶여 있어 표본이 작다 — 계수 부호·크기는 "다음에
어떤 조합을 좁혀서 섀도 채널로 검증할지" 우선순위를 정하는 용도로만 쓸 것,
바로 강등 규칙화하지 말 것.

실행:
    python scripts/checklist_ev_regression.py [--days 60] [--min-pair-n 6]

출력: 콘솔 + data/checklist_ev_regression_report.md
(gitignore 대상 PC별 산출물 — 재생성 가능)
"""
import argparse
import datetime
import glob
import os
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config.settings import TRADES_DB, DATA_DIR
import sqlite3

_TS_FMT = "%Y-%m-%d %H:%M:%S"

# [진입체크] 라인 예:
# "2026-07-22 09:32:57 [INFO] TRADE: [진입체크] SHORT→SHORT 1계약 A급 | sign✅ conf✅
#  vwap✅ cvd✅ ofi✅ fore❌ prev✅ time✅ risk✅ chas❌ coun✅ | conf=36.4%"
_LINE_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*\[진입체크\]\s+\S+→\S+\s+\d+계약\s+"
    r"(?P<grade>[ABCX])급\s*\|\s*(?P<checks>.+?)\s*\|\s*conf=(?P<conf>[\d.]+)%"
)
_CHECK_RE = re.compile(r"(sign|conf|vwap|cvd|ofi|fore|prev|time|risk|chas|coun)([✅❌])")

_ITEM_LABELS = {
    "sign": "1_signal", "conf": "2_confidence", "vwap": "3_vwap", "cvd": "4_cvd",
    "ofi": "5_ofi", "fore": "6_foreign", "prev": "7_prev_bar", "time": "8_time",
    "risk": "9_risk", "chas": "10_chase", "coun": "11_countertrend",
}
_ITEM_KEYS = list(_ITEM_LABELS.keys())  # 회귀 피처 순서 고정


def _krw(x: float) -> str:
    return "{:+,.0f}원".format(x)


def _parse_trade_logs(log_dir: str, cutoff: datetime.datetime):
    """logs/*_TRADE.log를 스캔해 {ts_str: {item: 0/1, grade, conf}} 리스트로 반환."""
    entries = []
    for path in sorted(glob.glob(os.path.join(log_dir, "*_TRADE.log"))):
        fname = os.path.basename(path)
        m = re.match(r"(\d{8})_TRADE\.log", fname)
        if not m:
            continue
        try:
            file_date = datetime.datetime.strptime(m.group(1), "%Y%m%d")
        except ValueError:
            continue
        if file_date < cutoff - datetime.timedelta(days=1):
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
        except OSError:
            continue
        for ln in lines:
            m2 = _LINE_RE.match(ln)
            if not m2:
                continue
            items = dict(_CHECK_RE.findall(m2.group("checks")))
            if len(items) != len(_ITEM_KEYS):
                continue  # 파싱 불완전 — 스킵(방어적)
            row = {k: (1 if items.get(k) == "✅" else 0) for k in _ITEM_KEYS}
            row["ts"] = m2.group("ts")
            row["grade_logged"] = m2.group("grade")
            row["conf_pct"] = float(m2.group("conf"))  # "conf" 키는 2_confidence 체크 불리언용
            entries.append(row)
    return entries


def _match_trades(days: int, log_dir: str):
    cutoff_dt = datetime.datetime.now() - datetime.timedelta(days=days)
    cutoff_ts = cutoff_dt.strftime(_TS_FMT)

    con = sqlite3.connect(TRADES_DB)
    con.row_factory = sqlite3.Row
    trades = con.execute(
        """SELECT entry_ts, exit_ts, direction, grade, quantity, net_pnl_krw, pnl_krw
           FROM trades WHERE entry_ts >= ? AND exit_ts IS NOT NULL""",
        (cutoff_ts,),
    ).fetchall()
    con.close()

    checklist_entries = _parse_trade_logs(log_dir, cutoff_dt)
    # ts -> datetime 캐시 (반복 파싱 비용 절감)
    for e in checklist_entries:
        e["_dt"] = datetime.datetime.strptime(e["ts"], _TS_FMT)

    matched = []
    for r in trades:
        try:
            r_dt = datetime.datetime.strptime(r["entry_ts"][:19], _TS_FMT)
        except (TypeError, ValueError):
            continue
        best, best_diff = None, None
        for e in checklist_entries:
            diff = (r_dt - e["_dt"]).total_seconds()
            if 0 <= diff <= 5 and (best_diff is None or diff < best_diff):
                best, best_diff = e, diff
        if best is None:
            continue
        pnl = r["net_pnl_krw"] if r["net_pnl_krw"] is not None else r["pnl_krw"]
        matched.append({**{k: best[k] for k in _ITEM_KEYS}, "grade": r["grade"] or "?",
                         "net_pnl_krw": float(pnl or 0.0), "entry_ts": r["entry_ts"]})
    return matched


def _ridge_coefs(X: np.ndarray, y: np.ndarray, alpha: float = 1.0):
    """표준화된 피처에 대한 Ridge 계수 — sklearn 의존(1.0.2, 프로젝트 고정버전)."""
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    model = Ridge(alpha=alpha)
    model.fit(Xs, y)
    return model.coef_, model.intercept_, model.score(Xs, y)


def analyze(days: int, min_pair_n: int):
    log_dir = os.path.join(ROOT, "logs")
    matched = _match_trades(days, log_dir)

    lines = []
    lines.append("# 체크리스트 항목·조합 순EV 회귀분석 (368차)")
    lines.append("")
    lines.append("- 생성: %s (분석 창 %d일)" % (
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), days))
    lines.append("- 로그-DB 매칭 표본: **%d건**" % len(matched))
    lines.append("")

    if len(matched) < 20:
        lines.append("> ⚠ 표본이 20건 미만 — 회귀 계수는 참고용으로만 사용할 것"
                      "(로그 보존기간 제약).")

    if not matched:
        lines.append("매칭 표본 0건 — 분석 불가.")
        report = "\n".join(lines)
        print(report)
        return report

    y = np.array([m["net_pnl_krw"] for m in matched], dtype=float)

    # 컬럼분산 0인 항목 제외 (해당 기간 항상 면제=True 등)
    active_keys = [
        k for k in _ITEM_KEYS
        if len(set(m[k] for m in matched)) > 1
    ]
    dropped_keys = [k for k in _ITEM_KEYS if k not in active_keys]

    lines.append("- 회귀 피처: %d개 (%s)" % (
        len(active_keys), ", ".join(_ITEM_LABELS[k] for k in active_keys)))
    if dropped_keys:
        lines.append("- 분산 0으로 제외: %s (기간 내 항상 통과 — 면제 항목일 가능성)" % (
            ", ".join(_ITEM_LABELS[k] for k in dropped_keys)))
    lines.append("")

    # ── 1) 항목별 단순 평균EV 차이 (pass - fail) ────────────────────────
    lines.append("## 항목별 단순 평균EV 비교 (통과 시 평균 - 실패 시 평균)")
    lines.append("")
    lines.append("| 항목 | n통과 | 평균EV(통과) | n실패 | 평균EV(실패) | 차이 |")
    lines.append("|---|---|---|---|---|---|")
    univariate = []
    for k in active_keys:
        pass_vals = [m["net_pnl_krw"] for m in matched if m[k] == 1]
        fail_vals = [m["net_pnl_krw"] for m in matched if m[k] == 0]
        avg_p = float(np.mean(pass_vals)) if pass_vals else 0.0
        avg_f = float(np.mean(fail_vals)) if fail_vals else 0.0
        diff = avg_p - avg_f
        univariate.append((k, len(pass_vals), avg_p, len(fail_vals), avg_f, diff))
    for k, np_, avg_p, nf, avg_f, diff in sorted(univariate, key=lambda t: t[5]):
        lines.append("| %s | %d | %s | %d | %s | %s |" % (
            _ITEM_LABELS[k], np_, _krw(avg_p), nf, _krw(avg_f), _krw(diff)))
    lines.append("")

    # ── 2) Ridge 다변량 회귀 (다른 항목 통제 후 개별 기여도) ────────────
    lines.append("## Ridge 다변량 회귀 계수 (표준화 피처, alpha=1.0)")
    lines.append("")
    lines.append("- 다른 10개 항목을 통제한 뒤 이 항목이 통과↔실패일 때 순EV에 미치는")
    lines.append("  한계 기여도(방향·상대크기만 참고 — 표본이 작아 절대값 과신 금지).")
    lines.append("")
    try:
        X = np.array([[m[k] for k in active_keys] for m in matched], dtype=float)
        coefs, intercept, r2 = _ridge_coefs(X, y, alpha=1.0)
        lines.append("- R² = %.3f (표본 %d건 — 낮아도 정상, 설명력보다 부호/순위 참고용)" % (
            r2, len(matched)))
        lines.append("")
        lines.append("| 항목 | Ridge 계수 |")
        lines.append("|---|---|")
        ranked = sorted(zip(active_keys, coefs), key=lambda t: t[1])
        for k, c in ranked:
            lines.append("| %s | %+.0f |" % (_ITEM_LABELS[k], c))
    except Exception as e:
        lines.append("- ⚠ Ridge 회귀 실패: %s" % e)
    lines.append("")

    # ── 3) 2-way 조합(동시 실패) 스캔 ────────────────────────────────
    lines.append("## 2-way 조합(동시 실패) 스캔 (n≥%d)" % min_pair_n)
    lines.append("")
    lines.append("- 두 항목이 함께 실패했을 때(나머지 항목 무관)의 표본 — 순위는 평균EV 오름차순")
    lines.append("")
    pair_rows = []
    for i, k1 in enumerate(active_keys):
        for k2 in active_keys[i + 1:]:
            vals = [m["net_pnl_krw"] for m in matched if m[k1] == 0 and m[k2] == 0]
            if len(vals) < min_pair_n:
                continue
            avg = float(np.mean(vals))
            win_rate = float(np.mean([1.0 if v > 0 else 0.0 for v in vals]))
            pair_rows.append((k1, k2, len(vals), avg, win_rate, sum(vals)))
    if pair_rows:
        lines.append("| 조합(동시 실패) | n | 평균EV | 승률 | 합계 |")
        lines.append("|---|---|---|---|---|")
        for k1, k2, n, avg, wr, total in sorted(pair_rows, key=lambda t: t[3]):
            lines.append("| %s + %s | %d | %s | %.0f%% | %s |" % (
                _ITEM_LABELS[k1], _ITEM_LABELS[k2], n, _krw(avg), wr * 100, _krw(total)))
    else:
        lines.append("- 표본 기준(n≥%d)을 만족하는 조합 없음 — min_pair_n을 낮춰 재실행 검토" %
                      min_pair_n)
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("> **읽는 법**: 단순 평균EV 비교와 Ridge 계수의 부호가 일치하는 항목일수록")
    lines.append("> 신뢰도가 높다(항목 간 상관에 덜 휘둘림). 부호가 갈리면 다른 항목과의")
    lines.append("> 공선성 때문일 가능성이 커 추가 표본 없이는 해석하지 말 것.")
    lines.append("> 2-way 조합 표는 368차 [16](chase+foreign)처럼 다음 섀도 관찰 채널 후보를")
    lines.append("> 고르는 용도 — 이 리포트 자체가 정책 결정 근거가 되지 않는다(§9 원칙).")

    report = "\n".join(lines)
    print(report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=60,
                        help="분석 창(일) — 로그 보존기간(~20일 안팎)에 자연히 캡됨")
    parser.add_argument("--min-pair-n", type=int, default=6,
                        help="2-way 조합 스캔 최소 표본 수")
    args = parser.parse_args()

    report = analyze(args.days, args.min_pair_n)

    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, "checklist_ev_regression_report.md")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(report)
    print("\n저장: %s" % out_path)


if __name__ == "__main__":
    main()

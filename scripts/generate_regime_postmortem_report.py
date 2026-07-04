# scripts/generate_regime_postmortem_report.py — W1 Phase 0: 일별 레짐 사후 라벨링
"""
mireuki_v9_최종설계안_2026-07-03.md §4 L1 "데이 레짐 엔진" 착수 전, 최근 30일을
사후적으로 레짐 라벨링해 "TREND일과 RANGE일에 기존 시스템 PnL이 실제로 갈리는가"를
raw_candles + daily_stats(trades.db)만으로 먼저 검증한다.

레짐 분류는 신규 로직을 만들지 않고 기존 `collection/macro/micro_regime.py::
MicroRegimeClassifier`를 그대로 재사용한다(문답 14번: "이미 있는 신호를 통합하는 것이
먼저" 원칙). 단, 이 분류기는 원래 bear/bull_exhaustion·vwap_position·z_warn_count도
입력받는데 raw_candles에는 OHLC만 있어 이 3개는 기본값(0)으로 넣는다 — 따라서
**탈진장(EXHAUSTION) 레짐은 이 사후분석에서 과소 추정된다**는 한계가 있음을
report에 명시한다. TREND/RANGE/VOLATILE/MIXED 판정(ADX+ATR 기반)은 OHLC만으로도
정상 작동한다.

**2026-07-03 왜곡 회피 보강**: 사용자가 조사한 2026-06~07 실제 거래소 서킷브레이커
발동일지(06-08, 06-23, 06-26, 07-02 — 국내 증시 역사상 이례적으로 잦은 발동)와
raw_candles를 대조한 결과, 06-08은 첫 봉이 09:44(정규 개장 09:00보다 44분 늦음)부터
시작해 실제 급락 구간이 데이터에서 통째로 빠져 있었고, 이 때문에 `day_ret_pct`가
09:44 시점 가격을 기준으로 계산돼 실제 낙폭을 크게 과소평가 — 하필 이 날이 22일
표본 중 유일한 '횡보장' 판정일이었다(레짐 오분류의 핵심 원인). 06-23/06-26은 장중
18~31분짜리 데이터 공백(거래정지로 추정)이 확인됐다. 이런 날을 TREND/RANGE 일반
버킷에 그대로 섞으면 레짐별 PnL 비교 자체가 왜곡되므로, 장중 10분 이상 공백 또는
09:10 이후 첫 봉 시작(개장 초반 결측)이 감지된 날은 **별도 버킷으로 분리**하고
TREND/RANGE/VOLATILE/MIXED 정규 집계에서 제외한다.

출력: regime_postmortem_report.md, regime_postmortem_metrics.json (ROOT)
"""
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import RAW_DATA_DB, TRADES_DB
from collection.macro.micro_regime import MicroRegimeClassifier, REGIMES

REPORT_PATH = ROOT / "regime_postmortem_report.md"
METRICS_PATH = ROOT / "regime_postmortem_metrics.json"

LOOKBACK_DAYS = 30

# 왜곡 회피 판정 기준 (2026-07-03 보강)
GAP_THRESHOLD_MIN = 10        # 이보다 긴 봉 공백 → 거래정지 의심
LATE_OPEN_THRESHOLD = "09:10"  # 첫 봉이 이 시각 이후 시작 → 개장 초반 결측 의심
EXCLUDED_BUCKET_NAME = "위기장/데이터결측(제외)"


def _load_candles(since_ts: str):
    with sqlite3.connect(RAW_DATA_DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT ts, high, low, close FROM raw_candles WHERE ts >= ? ORDER BY ts",
            (since_ts,),
        ).fetchall()
    return [dict(r) for r in rows]


def _load_daily_stats(since_date: str):
    with sqlite3.connect(TRADES_DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT date, trades, wins, pnl_pts, pnl_krw FROM daily_stats WHERE date >= ? ORDER BY date",
            (since_date,),
        ).fetchall()
    return {r["date"]: dict(r) for r in rows}


def _group_by_date(candles):
    by_date = defaultdict(list)
    for c in candles:
        by_date[c["ts"][:10]].append(c)
    return dict(sorted(by_date.items()))


def _detect_gaps(day_candles, threshold_min: int = GAP_THRESHOLD_MIN):
    """봉 간 시간 공백이 threshold_min 초과인 구간 탐지 — 거래정지(CB) 의심 신호."""
    gaps = []
    prev_ts = None
    for c in day_candles:
        ts = datetime.strptime(c["ts"], "%Y-%m-%d %H:%M:%S")
        if prev_ts is not None:
            delta_min = (ts - prev_ts).total_seconds() / 60
            if delta_min > threshold_min:
                gaps.append({
                    "from": prev_ts.strftime("%H:%M"),
                    "to": ts.strftime("%H:%M"),
                    "minutes": round(delta_min, 1),
                })
        prev_ts = ts
    return gaps


def _assess_data_quality(day_candles):
    """왜곡 회피 판정: 장중 공백 또는 개장 초반 결측이 있으면 'EXCLUDED'."""
    gaps = _detect_gaps(day_candles)
    first_time = day_candles[0]["ts"][11:16]  # "HH:MM"
    late_open = first_time > LATE_OPEN_THRESHOLD
    if gaps or late_open:
        reasons = [f"공백 {g['from']}~{g['to']}({g['minutes']}분)" for g in gaps]
        if late_open:
            reasons.append(f"개장결측(첫봉 {first_time})")
        return "EXCLUDED", "; ".join(reasons)
    return "OK", ""


def _label_day(day_candles):
    clf = MicroRegimeClassifier()
    regime_counter = Counter()
    for c in day_candles:
        res = clf.push_1m_candle(c["high"], c["low"], c["close"])
        regime_counter[res["regime"]] += 1

    dominant, dominant_n = regime_counter.most_common(1)[0]
    total = sum(regime_counter.values())
    first_close = day_candles[0]["close"]
    last_close = day_candles[-1]["close"]
    day_high = max(c["high"] for c in day_candles)
    day_low = min(c["low"] for c in day_candles)

    return {
        "dominant_regime": dominant,
        "dominant_share": round(dominant_n / total, 3) if total else None,
        "regime_dist": {r: round(regime_counter.get(r, 0) / total, 3) for r in REGIMES} if total else {},
        "day_ret_pct": round((last_close - first_close) / first_close * 100, 3),
        "day_range_pct": round((day_high - day_low) / first_close * 100, 3),
        "bar_count": total,
    }


def build_report(metrics: dict) -> str:
    lines = [
        "# Regime Postmortem Report — 일별 레짐 사후 라벨링 (v9 Phase 0)",
        "",
        f"- Generated at: {metrics['generated_at']}",
        f"- 조회 구간: 최근 {metrics['lookback_days']}일 ({metrics['since_ts'][:10]} ~)",
        "- ⚠️ 한계: bear/bull_exhaustion·vwap_position을 raw_candles에서 재구성하지 않고 "
        "기본값(0)으로 넣었음 — **탈진장(EXHAUSTION) 레짐은 과소 추정됨.** "
        "TREND/RANGE/VOLATILE/MIXED(ADX+ATR 기반)는 OHLC만으로 정상 판정됨.",
        f"- ⚠️ 왜곡 회피: 장중 {GAP_THRESHOLD_MIN}분 초과 공백 또는 {LATE_OPEN_THRESHOLD} 이후 "
        "첫 봉 시작(개장 초반 결측)이 감지된 날은 `data_quality=EXCLUDED`로 표시하고 "
        f"`{EXCLUDED_BUCKET_NAME}` 버킷으로 분리 — 아래 레짐별 PnL 집계에서 제외됨.",
        "",
        "## 일별 상세",
        "",
        "| 날짜 | 지배 레짐 | 지배 비중 | 일중수익률% | 일중레인지% | 거래수 | 승수 | pnl_krw | 데이터품질 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for d in metrics["daily"]:
        quality_cell = d["data_quality"]
        if d.get("quality_reason"):
            quality_cell += f" ({d['quality_reason']})"
        lines.append(
            f"| {d['date']} | {d['dominant_regime']} | {d['dominant_share']} | "
            f"{d['day_ret_pct']:+.2f} | {d['day_range_pct']:.2f} | "
            f"{d['trades'] if d['trades'] is not None else '—'} | "
            f"{d['wins'] if d['wins'] is not None else '—'} | "
            f"{d['pnl_krw'] if d['pnl_krw'] is not None else '—'} | "
            f"{quality_cell} |"
        )
    lines += [
        "",
        f"## 레짐 버킷별 PnL 집계 (dominant_regime 기준, `{EXCLUDED_BUCKET_NAME}`은 정규 비교에서 제외)",
        "",
        "| 레짐 | 일수 | 합계pnl_krw | 평균pnl_krw | 평균일중수익률% | 총거래 | 총승수 |",
        "|---|---|---|---|---|---|---|",
    ]
    for regime, agg in metrics["by_regime"].items():
        lines.append(
            f"| {regime} | {agg['days']} | {agg['sum_pnl_krw']:.0f} | "
            f"{agg['mean_pnl_krw']:.0f} | {agg['mean_day_ret_pct']:+.2f} | "
            f"{agg['total_trades']} | {agg['total_wins']} |"
        )
    lines += [
        "",
        "---",
        "",
        "## 해석 가이드",
        "",
        "- TREND 버킷의 평균pnl_krw가 RANGE 버킷보다 뚜렷이 높다면 경로 B(추세일 대형 홀딩) "
        "전제가 데이터로 뒷받침됨 — §4 L1 데이 레짐 엔진 설계를 그대로 진행.",
        "- 차이가 뚜렷하지 않다면 현재 시스템이 TREND일에도 추세를 제대로 못 타고 있다는 뜻 "
        "— L2 청산 재설계(트레일링 확폭+러너)의 우선순위를 높여야 함.",
        "- `daily_stats`에 없는 날짜(trades=—)는 미체결일 또는 daily_close 미실행일.",
        f"- `{EXCLUDED_BUCKET_NAME}`에 잡힌 날은 2026-06~07 실제 거래소 서킷브레이커 발동일"
        "(06-08·06-23·06-26·07-02)과 상당 부분 겹친다 — 이 날들을 일반 레짐 버킷에 그대로 "
        "섞으면 레짐 오분류(예: 급락 구간이 통째로 빠져 '횡보장'으로 오판정)가 발생하므로 "
        "분리했다. 표본이 쌓일수록(NEXT_TODO 290차) 이 버킷 자체를 '위기장' 레짐으로 "
        "정식 편입할지 별도 검토 필요.",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    since_ts = (datetime.now() - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d 00:00:00")
    candles = _load_candles(since_ts)
    if not candles:
        print("validation=FAIL (no raw_candles rows in lookback window)")
        return 1

    by_date = _group_by_date(candles)
    daily_stats = _load_daily_stats(since_ts[:10])

    daily = []
    regime_bucket = defaultdict(lambda: {
        "days": 0, "sum_pnl_krw": 0.0, "total_trades": 0, "total_wins": 0,
        "sum_day_ret_pct": 0.0,
    })

    for date, day_candles in by_date.items():
        if len(day_candles) < 5:
            continue  # ATRCalculator 최소 워밍업 미달 — 조기장 반토막 등 제외
        label = _label_day(day_candles)
        quality, quality_reason = _assess_data_quality(day_candles)
        ds = daily_stats.get(date, {})
        row = {
            "date": date,
            "dominant_regime": label["dominant_regime"],
            "dominant_share": label["dominant_share"],
            "day_ret_pct": label["day_ret_pct"],
            "day_range_pct": label["day_range_pct"],
            "bar_count": label["bar_count"],
            "trades": ds.get("trades"),
            "wins": ds.get("wins"),
            "pnl_krw": ds.get("pnl_krw"),
            "data_quality": quality,
            "quality_reason": quality_reason,
        }
        daily.append(row)

        # 왜곡 회피: 공백/개장결측일은 TREND/RANGE/... 정규 버킷에서 제외하고
        # 별도 버킷(EXCLUDED_BUCKET_NAME)으로 분리 집계
        bucket_key = label["dominant_regime"] if quality == "OK" else EXCLUDED_BUCKET_NAME
        bucket = regime_bucket[bucket_key]
        bucket["days"] += 1
        bucket["sum_pnl_krw"] += float(ds.get("pnl_krw") or 0.0)
        bucket["total_trades"] += int(ds.get("trades") or 0)
        bucket["total_wins"] += int(ds.get("wins") or 0)
        bucket["sum_day_ret_pct"] += label["day_ret_pct"]

    by_regime = {}
    for regime, b in regime_bucket.items():
        by_regime[regime] = {
            "days": b["days"],
            "sum_pnl_krw": round(b["sum_pnl_krw"], 0),
            "mean_pnl_krw": round(b["sum_pnl_krw"] / b["days"], 0) if b["days"] else 0.0,
            "mean_day_ret_pct": round(b["sum_day_ret_pct"] / b["days"], 3) if b["days"] else 0.0,
            "total_trades": b["total_trades"],
            "total_wins": b["total_wins"],
        }

    metrics = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "lookback_days": LOOKBACK_DAYS,
        "since_ts": since_ts,
        "daily": daily,
        "by_regime": dict(sorted(by_regime.items(), key=lambda x: -x[1]["mean_pnl_krw"])),
    }

    REPORT_PATH.write_text(build_report(metrics), encoding="utf-8")
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"saved_report={REPORT_PATH}")
    print(f"saved_metrics={METRICS_PATH}")
    print(f"day_count={len(daily)}")
    print(f"by_regime={metrics['by_regime']}")
    print("validation=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

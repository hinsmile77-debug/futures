# -*- coding: utf-8 -*-
"""[MW0601 456차 / Wave 4] 사전등록 하위 축 3종 — 판정 전용, 읽기 전용.

⚠ **새 채널이 아니라 기존 채널의 하위 축**이다.

설계 중 조사에서 세 제안이 전부 기존 채널과 실질 중복임이 드러났다(등록 채널 54개):

| 제안 | 기존 채널 | 이미 하는 것 | 여기서 더하는 것 |
|---|---|---|---|
| F4-A | `tp1_arm_latency_watch` / `mfe_capture_watch` | arm 지연 vs TP2 완주, 캡처율 | **보호전환 이후 포기한 MFE** |
| G2-B | `exit_fill_slippage_watch` [17] | 슬리피지 일자단위 부호검정 | **청산수량 분해** |
| F10-B | `grade_x_promotion` [36] | 승격 **경로**(X→A/C→A/C→C) 우열 | **C→A 내부 pass_count 축** |

중복 채널을 만드는 대신 빠진 축 하나씩만 붙인다 — 이 프로젝트는 정의가 갈라져
표류한 전례가 반복됐다(419차 "죽은 상수", 432차 "3중 정의", 333차 후속4 동기화 드리프트).

합격선은 `config/settings.py:VALIDATION_CAMPAIGN`에 사전등록돼 있다(456차 승인).
**여기서 기준을 바꾸지 말 것** — 사후 조작이 된다(캠페인 §9).
"""
from __future__ import print_function

import datetime
import math
import random

_TS_FMT = "%Y-%m-%d %H:%M:%S"


# ── 공용 통계 헬퍼 ────────────────────────────────────────────────────────────

def daily_t(day_vals):
    """일자단위 평균과 t. Returns (mean, t, n_days).

    신호단위 풀링을 쓰지 않는 이유(372차): 하루 수백 개의 상관된 분봉을 독립
    관측으로 세면 표본수가 부풀려져 t가 과대평가된다.
    """
    v = [x for x in day_vals if x is not None and not math.isnan(x)]
    n = len(v)
    if n < 3:
        return (float("nan"), float("nan"), n)
    m = sum(v) / n
    var = sum((x - m) ** 2 for x in v) / (n - 1)
    if var <= 0:
        return (m, float("nan"), n)
    return (m, m / math.sqrt(var / n), n)


def half_sign_agree(day_pairs):
    """전·후반 부호 일치 — 우연한 구간 적합을 거른다. day_pairs=[(date, value)]"""
    vs = [v for _, v in sorted(day_pairs) if v is not None and not math.isnan(v)]
    if len(vs) < 4:
        return False
    h = len(vs) // 2
    a = sum(vs[:h]) / max(h, 1)
    b = sum(vs[h:]) / max(len(vs) - h, 1)
    return (a > 0) == (b > 0)


# ── [17-Q] 손절 체결 슬리피지 × 청산수량 ─────────────────────────────────────

def eval_exit_fill_slippage_qty(conn_factory, trades_db, campaign_start,
                                spearman, campaign_cfg):
    """417차가 열어두고 **미검증**으로 남긴 가설을 검정한다.

    *"미니선물 호가 깊이를 여러 계약이 한 번에 훑어, 계약수가 클수록 손절 체결이
    의도가보다 나빠진다."* 417차는 '손절폭 초과 비율' vs 진입수량(rho=+0.318)만
    봤고 **체결 슬리피지 자체는 재지 않았다.**

    🔴 **사전등록 정직성 고지** — 첫 관측치를 등록 **전에 이미 봤다**
    (08-03~08-10 하드스톱 74건: qty=1 n=66 평균 −0.3162pt / qty=2 n=8 −0.6875pt).
    따라서 최초 판정은 사전등록 검증이 아니라 **"이미 본 결과의 코드화"** 이며
    [47]·[48]의 고지와 같은 취급이다. 이 축의 가치는 앞으로의 재현에 있다.
    """
    cr = campaign_cfg.get("exit_fill_slippage_qty", {})
    out = {"verdict": "INSUFFICIENT", "pre_observed": bool(cr.get("pre_observed"))}
    if not cr.get("enabled", True):
        out["verdict"] = "DISABLED"
        return out
    min_n = int(cr.get("min_samples", 60))
    min_q2 = int(cr.get("min_samples_qty2p", 20))
    min_d = int(cr.get("min_days", 10))
    drop_top = int(cr.get("outlier_drop_top", 2))

    try:
        with conn_factory(trades_db) as conn:
            # `quantity`는 456차 신설 — 이전 행은 trades 조인으로 폴백한다.
            rows = conn.execute(
                """SELECT s.ts, s.slippage_pts,
                          COALESCE(s.quantity, t.quantity) AS qty
                     FROM exit_fill_slippage s
                     LEFT JOIN trades t
                            ON t.entry_ts = s.entry_ts
                           AND ABS(strftime('%s', t.exit_ts)
                                   - strftime('%s', s.ts)) <= 3
                    WHERE s.ts >= ?
                      AND s.reason LIKE '%하드스톱%'
                      AND s.slippage_pts IS NOT NULL
                    ORDER BY s.ts""",
                (campaign_start,),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    data = [(str(r["ts"])[:10], int(r["qty"]), abs(float(r["slippage_pts"])))
            for r in rows if r["qty"]]
    out["n"] = len(data)
    out["n_days"] = len({d for d, _, _ in data})
    out["n_qty2p"] = sum(1 for _, q, _ in data if q >= 2)
    if not data:
        out["reason"] = "표본 없음"
        return out

    by_qty = {}
    for _, q, s in data:
        by_qty.setdefault(q, []).append(s)
    out["by_qty"] = {q: {"n": len(v), "mean_abs_slip": sum(v) / len(v)}
                     for q, v in sorted(by_qty.items())}

    if out["n"] < min_n or out["n_qty2p"] < min_q2 or out["n_days"] < min_d:
        out["reason"] = ("표본 미달 — 전체 %d/%d · qty>=2 %d/%d · %d/%d일"
                         % (out["n"], min_n, out["n_qty2p"], min_q2,
                            out["n_days"], min_d))
        return out

    out["rho"] = spearman([q for _, q, _ in data], [s for _, _, s in data])

    # 이상치 제거 후 부호 유지 (372차 — 손실 91%가 단 2건에서 나온 착시 방지)
    trimmed = sorted(data, key=lambda x: -x[2])[drop_top:]
    out["rho_trimmed"] = spearman([q for _, q, _ in trimmed],
                                  [s for _, _, s in trimmed])
    out["outlier_dropped"] = drop_top

    # 일자단위 부트스트랩 95% CI — 일자를 통째로 리샘플해 일내 상관을 보존한다
    days = sorted({d for d, _, _ in data})
    by_day = {d: [(q, s) for dd, q, s in data if dd == d] for d in days}
    rnd = random.Random(20260810)          # 재현성 고정
    boots = []
    for _ in range(1000):
        samp = [qs for d in (rnd.choice(days) for _ in days) for qs in by_day[d]]
        if len({q for q, _ in samp}) < 2:
            continue
        b = spearman([q for q, _ in samp], [s for _, s in samp])
        if not math.isnan(b):
            boots.append(b)
    if len(boots) < 100:
        out["reason"] = "부트스트랩 실패 (수량 분산 부족)"
        return out
    boots.sort()
    lo, hi = boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots))]
    out["ci95"] = [lo, hi]

    out["half_sign_agree"] = half_sign_agree([
        (d, spearman([q for q, _ in by_day[d]], [s for _, s in by_day[d]]))
        for d in days if len({q for q, _ in by_day[d]}) >= 2
    ])

    if out["rho"] > 0 and lo > 0 and out["half_sign_agree"] and out["rho_trimmed"] > 0:
        out["verdict"] = "SUPPORTS_HYP"
        out["note"] = ("계약수가 클수록 손절 체결이 나쁘다 — 417차 가설 지지. "
                       "집행 축 개선을 주간회의 안건으로.")
    elif out["rho"] < 0 and hi < 0:
        out["verdict"] = "REJECTS_HYP"
    else:
        out["verdict"] = "PASS"
        out["note"] = "구분 안 됨 — 현행 유지. 표본이 적으면 당연히 PASS다(오독 금지)."
    return out


# ── [36-P] C→A 승격 내부의 pass_count 축 ─────────────────────────────────────

def eval_grade_promotion_passcount(merged_positions, has_column, spearman,
                                   campaign_cfg):
    """승격에 정렬강도 하한이 필요한가.

    ⚠ **원안 폐기 기록** — 311차 방법론(`pass=6` vs `pass>=7`)을 그대로 옮기려
    했으나 실측 6거래일 42건이 **전부 pass>=7**이었다. 처리군이 영원히 비어
    판정 불가 채널이 된다([8] KellySkip 함정). 그래서 **연속형 rho**가 주지표다.

    연속형은 임의 분할점을 만들지 않는다. 정책 질문("하한을 둘 것인가")은
    *"pass_count가 정보를 담는가"* 로 먼저 답해야 하며, rho ≈ 0이면
    **어떤 하한도 정당화되지 않는다.**
    """
    cr = campaign_cfg.get("grade_promotion_passcount", {})
    out = {"verdict": "INSUFFICIENT"}
    if not cr.get("enabled", True):
        out["verdict"] = "DISABLED"
        return out
    min_n = int(cr.get("min_samples", 40))
    min_d = int(cr.get("min_days", 10))
    min_b = int(cr.get("min_samples_per_bucket", 20))
    split = int(cr.get("bucket_split", 9))
    t_thr = float(cr.get("t_threshold", 2.26))

    if not has_column("checklist_pass_count"):
        out["no_data"] = True
        out["reason"] = "`trades.checklist_pass_count` 컬럼 없음 — 마이그레이션 전 DB"
        return out

    pos = merged_positions(extra_cols="raw_grade, grade, checklist_pass_count")
    ca = [p for p in pos
          if p.get("raw_grade") == "C" and p.get("grade") == "A"
          and p.get("checklist_pass_count") is not None]
    out["n"] = len(ca)
    out["n_days"] = len({p["entry_ts"][:10] for p in ca})
    if not ca:
        out["reason"] = ("C→A 승격 중 pass_count 기록 표본 없음 (기록 개시 %s)"
                         % cr.get("data_start", "?"))
        return out

    dist = {}
    for p in ca:
        k = int(p["checklist_pass_count"])
        dist[k] = dist.get(k, 0) + 1
    out["passcount_dist"] = dict(sorted(dist.items()))

    if out["n"] < min_n or out["n_days"] < min_d:
        out["reason"] = ("표본 미달 — %d/%d건 · %d/%d일"
                         % (out["n"], min_n, out["n_days"], min_d))
        return out

    by_day = {}
    for p in ca:
        by_day.setdefault(p["entry_ts"][:10], []).append(
            (int(p["checklist_pass_count"]), float(p.get("pnl") or 0.0)))
    day_rho = [(d, spearman([q for q, _ in v], [r for _, r in v]))
               for d, v in sorted(by_day.items())
               if len(v) >= 3 and len({q for q, _ in v}) >= 2]
    mean_rho, t, nd = daily_t([r for _, r in day_rho])
    out["mean_daily_rho"] = mean_rho
    out["t"] = t
    out["n_rho_days"] = nd
    out["half_sign_agree"] = half_sign_agree(day_rho)

    lo = [p for p in ca if int(p["checklist_pass_count"]) < split]
    hi = [p for p in ca if int(p["checklist_pass_count"]) >= split]
    out["buckets"] = {}
    for lab, v in (("pass<%d" % split, lo), ("pass>=%d" % split, hi)):
        if v:
            out["buckets"][lab] = {
                "n": len(v),
                "avg_pnl_krw": sum(float(p.get("pnl") or 0.0) for p in v) / len(v),
                "win_rate": sum(1 for p in v if (p.get("pnl") or 0) > 0) / len(v),
            }
    out["bucket_judgeable"] = (len(lo) >= min_b and len(hi) >= min_b)

    if math.isnan(t):
        out["reason"] = "일자단위 rho 산출 불가 (일별 pass_count 분산 부족)"
        return out
    if mean_rho > 0 and t > t_thr and out["half_sign_agree"]:
        out["verdict"] = "SUPPORTS_HYP"
        out["note"] = "pass_count가 높을수록 성과가 좋다 — 승격 하한 설계를 안건으로."
    elif mean_rho < 0 and t < -t_thr:
        out["verdict"] = "REJECTS_HYP"
        out["note"] = "하한이 오히려 해롭다."
    else:
        out["verdict"] = "PASS"
        out["note"] = ("pass_count가 정보를 담지 않는다 — "
                       "311차 가드를 C 경로로 확장하지 않는다.")
    return out


# ── [TP1-M] TP1 보호전환 이후 포기한 MFE ─────────────────────────────────────

def eval_tp1_protect_forgone_mfe(conn_factory, trades_db, campaign_start,
                                 load_candle_maps, campaign_cfg):
    """보호전환이 이익을 조기 절단하는지 **관측만으로** 탐지한다.

    ⚠ **청산정책을 모델링하지 않는다** — `raw_candles`의 H/L만 쓴다.
    [47] 게이트가 밝힌 재생기 결함(TP3·4단계 트레일링 미모델링 → 러너를 건당
    2.61pt 과소평가)은 **청산정책 모델링** 경로의 문제다. 이 축은 그 경로를 타지
    않으므로 **[47] SUSPEND 대상이 아니다.** 리포트에서 [25]/[25-B]와 같은 처리를
    받지 않도록 주의할 것.

    ⚠ **MFE는 상한이다.** SUPPORTS_HYP가 *"그만큼 벌 수 있었다"* 는 뜻이 **아니라**
    *"포착할 여지가 있었다"* 는 탐지 신호다. **기회 크기 추정에 쓰지 말 것** —
    실제 회수 가능액은 Phase B의 A/B에서만 답할 수 있다.

    모집단: `synthetic_partial_exits`(arm_ts, 436차 이후) ⋈ `trades`
    = **1계약 보호전환 경로**. 다계약 TP1 부분청산은 [12] tp1_trail_shadow 담당이며
    여기서 다루지 않는다(범위를 명시해 중복을 피한다).
    """
    cr = campaign_cfg.get("tp1_protect_forgone_mfe", {})
    out = {"verdict": "INSUFFICIENT"}
    if not cr.get("enabled", True):
        out["verdict"] = "DISABLED"
        return out
    min_n = int(cr.get("min_samples", 40))
    min_d = int(cr.get("min_days", 10))
    thr = float(cr.get("forgone_pt_threshold", 0.5))
    t_thr = float(cr.get("t_threshold", 2.26))
    start = max(str(cr.get("data_start", "")), str(campaign_start)[:10])

    try:
        with conn_factory(trades_db) as conn:
            rows = conn.execute(
                """SELECT s.entry_ts, s.arm_ts, s.direction,
                          t.exit_ts, t.exit_price
                     FROM synthetic_partial_exits s
                     JOIN trades t ON t.entry_ts = s.entry_ts
                    WHERE s.arm_ts IS NOT NULL
                      AND substr(s.arm_ts,1,10) >= ?
                      AND t.exit_ts IS NOT NULL
                    ORDER BY s.arm_ts""",
                (start,),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out
    if not rows:
        out["reason"] = "표본 없음 (arm_ts 기록 %s 이후)" % start
        return out

    _, high_map, low_map = load_candle_maps(start + " 00:00:00",
                                            exclude_untradeable=True)
    recs = []
    for r in rows:
        try:
            is_long = str(r["direction"]).upper() == "LONG"
            ex_ts = str(r["exit_ts"])[:19]
            exit_px = float(r["exit_price"])
            t0 = datetime.datetime.strptime(ex_ts, _TS_FMT).replace(second=0)
        except Exception:
            continue
        end = t0.replace(hour=15, minute=10, second=0)
        best, cur = None, t0 + datetime.timedelta(minutes=1)
        while cur <= end:
            k = cur.strftime(_TS_FMT)
            px = high_map.get(k) if is_long else low_map.get(k)
            if px is not None:
                v = (px - exit_px) if is_long else (exit_px - px)
                best = v if best is None else max(best, v)
            cur += datetime.timedelta(minutes=1)
        if best is not None:
            recs.append((ex_ts[:10], max(0.0, best)))

    out["n"] = len(recs)
    out["n_days"] = len({d for d, _ in recs})
    if out["n"] < min_n or out["n_days"] < min_d:
        out["reason"] = ("표본 미달 — %d/%d건 · %d/%d일"
                         % (out["n"], min_n, out["n_days"], min_d))
        return out

    by_day = {}
    for d, v in recs:
        by_day.setdefault(d, []).append(v)
    day_means = [(d, sum(v) / len(v)) for d, v in sorted(by_day.items())]
    mean, t, _ = daily_t([v for _, v in day_means])
    out["mean_forgone_pts"] = mean
    out["t"] = t
    out["half_sign_agree"] = half_sign_agree(day_means)
    out["threshold_pt"] = thr

    if mean > thr and t > t_thr and out["half_sign_agree"]:
        out["verdict"] = "SUPPORTS_HYP"
        out["note"] = ("보호전환 이후 평균 %.2fpt의 유리 이동을 포기했다 — "
                       "offset 재설계를 주간회의 안건으로. "
                       "⚠ MFE는 상한이며 회수 가능액이 아니다." % mean)
    else:
        out["verdict"] = "PASS"
        out["note"] = ("현행 유지 — 포기폭이 문턱(%.2fpt) 미만이거나 불안정" % thr)
    return out

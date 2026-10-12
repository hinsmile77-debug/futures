# -*- coding: utf-8 -*-
"""[MW0602 615차 후속2] 피터2 오프셋 장중 자동 실측 — 순수 함수(입출력 없음).

오프셋 = 「내 미니 근월물 − 정규 10100(코스피200 연결 근월물)」. 피터는 일반선물 가격으로
말하므로 미니가 = 피터가 + 오프셋이다(596차 F4).

왜 장중에 재나
    종전에는 장후 정규 10100 수집 뒤에야 잴 수 있어 **직전 실측일** 값을 썼다. 만기 다음 날은
    미니 월물이 바뀌어 약 2pt 점프하므로 그 값이 `safe=False` 가 되고 하루 종일 진입이 막혔다.
    2026-10-12 실측: 사용값 −4.88(10-08) vs 그날 실제 −2.0~−2.3(08:50부터 ±0.15 안정).
    평일에도 하루 안에서 0.3~0.6pt 움직인다(596차) — 당일 실측이 직전일 값보다 낫다
    (사용자 결정 2026-10-12: 평일에도 우선).

입력은 `CpSysDib.FutOptChart` 행(라벨 = 봉 **종료** 시각 HHMM). 두 계약을 **같은 TR** 로 받아
라벨 규약 차이 없이 분끼리 짝짓는다 — raw_candles(시작 시각)와 섞지 않는다.
"""
import statistics

MIN_N = 8            # 짝지어진 분 수 하한
MAX_SPREAD = 0.30    # 5분 슬롯 중앙값의 최고−최저 상한(pt)
LOOKBACK_MIN = 30    # 최근 N개 분으로 잰다 — 일중 드리프트를 따라간다
FIRST_LABEL = 846    # 08:45 봉(종료 라벨 0846)부터


def _by_label(rows, ymd):
    out = {}
    for r in rows or ():
        try:
            if int(r.get('date')) != ymd:
                continue
            c = r.get('close')
            if c is None:
                continue
            out[int(r.get('time'))] = float(c)
        except (TypeError, ValueError):
            continue
    return out


def _hm(label):
    return '%02d:%02d' % (label // 100, label % 100)


def measure(mini_rows, reg_rows, ymd, now_hhmm, lookback=LOOKBACK_MIN,
            min_n=MIN_N, max_spread=MAX_SPREAD):
    """→ dict(value, n, spread, safe, reason, first, last, full, n_full).

    `ymd` = 오늘(int YYYYMMDD), `now_hhmm` = 지금(int HHMM). 라벨이 `now_hhmm` 을 넘는 봉은
    아직 형성 중이라 버린다. `value is None` 이면 못 잰 것이고 `reason` 이 이유다(계측 4원칙 ②).
    `safe` 는 표본(`n ≥ min_n`)과 안정성(`spread ≤ max_spread`)을 둘 다 통과해야 True.
    """
    out = {'value': None, 'n': 0, 'spread': None, 'safe': False, 'reason': '',
           'first': None, 'last': None, 'full': None, 'n_full': 0}
    mini = _by_label(mini_rows, ymd)
    reg = _by_label(reg_rows, ymd)
    if not mini:
        out['reason'] = '미니 분봉 없음'
        return out
    if not reg:
        out['reason'] = '정규 10100 분봉 없음'
        return out
    labels = sorted(l for l in set(mini) & set(reg) if FIRST_LABEL <= l <= now_hhmm)
    if not labels:
        out['reason'] = '짝지어진 완성봉 없음'
        return out
    diffs = [(l, round(mini[l] - reg[l], 2)) for l in labels]
    out['full'] = round(statistics.median(d for _, d in diffs), 2)
    out['n_full'] = len(diffs)
    win = diffs[-lookback:]
    vals = [d for _, d in win]
    out['value'] = round(statistics.median(vals), 2)
    out['n'] = len(win)
    out['first'], out['last'] = _hm(win[0][0]), _hm(win[-1][0])
    slots = {}
    for l, d in win:
        mins = (l // 100) * 60 + (l % 100)
        slots.setdefault(mins // 5, []).append(d)
    meds = [statistics.median(v) for v in slots.values()]
    out['spread'] = round(max(meds) - min(meds), 2)
    if out['n'] < min_n:
        out['reason'] = '표본 부족 n=%d<%d' % (out['n'], min_n)
    elif out['spread'] > max_spread:
        out['reason'] = '불안정 spread=%.2f>%.2f' % (out['spread'], max_spread)
    else:
        out['safe'] = True
        out['reason'] = 'ok'
    return out

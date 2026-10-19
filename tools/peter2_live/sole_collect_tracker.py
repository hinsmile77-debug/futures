# -*- coding: utf-8 -*-
"""[MW0601 698차] 피터2 X 수집 — MW0601 단독 수집 전환 효과 추적. 읽기 전용.

배경
    2026-10-19 장후 697-2 판정 FAIL(트윗 지연 p90 237.2초 > 90초, 429 23건).
    한도 창마다 남은 예산(rem)이 **우리 요청 수보다 훨씬 많이** 줄었다 — 80초 주기 우리 요청
    2회 사이에 rem 이 5~6씩 빠졌다(창당 외부 소진 중앙값 약 27회). 같은 X 로그인을 쓰는
    MW0602 수집기가 한도를 나눠 쓰고 있었다는 뜻이다.
    → 2026-10-20 사용자 결정: 새 계정 없이 **MW0602 수집기를 끈다**(03 판정절차 §4 ②안).

사전등록 판정 기준 (2026-10-20 07:50 KST, 결과를 보기 전에 고정 — 보고 나서 바꾸지 말 것)
    평가 창: 2026-10-20 부터 **수신기 로그가 있는 평일 5거래일**.
    ① 단독 확인  — 그날 09:00–15:20 한도 창(관측 ≥ 5줄)의 **외부 소진 중앙값 ≤ 3**.
                   외부 소진 = (창 안 rem 최대 − 최소) − (우리 관측 줄 수 − 1).
                   ※ 우리 요청은 줄마다 rem 이 1씩 줄어드는 것으로 1:1 대응한다(10-19 로그 실측).
    ② 한도 초과 소멸 — 그날 09:00–15:20 의 429 ≤ 1건.
    ③ 지연 개선(주 판정) — 평가 창 전체 트윗 지연 **통합 p90 ≤ 90초**, 통합 n ≥ 30
                   (합격선은 latency_report.P90_LIMIT_SEC 그대로 — 615차 사전등록).
    최종(5거래일 후):
      ①이 5일 중 4일 이상 PASS 且 ③ PASS → IMPROVED   : 종결, F-4(프로필 폴백) 불필요.
      ①이 4일 이상 PASS 且 ③ FAIL         → NOT_LIMIT   : 한도는 풀렸는데 지연이 남음 →
                                             03 §2 「혼자 소진」 가지(RELOAD_SEC 역산·F-4).
      ①이 4일 미만                          → STILL_SHARED: MW0602 중지 미반영 또는 다른 소비자
                                             (같은 계정으로 사람이 X 검색) → 사용자 확인.
      통합 n < 30                           → INSUFFICIENT: 평가 창 연장(기준은 그대로).

실행
    python tools/peter2_live/sole_collect_tracker.py              # 오늘까지
    python tools/peter2_live/sole_collect_tracker.py --upto 2026-10-24
    python tools/peter2_live/sole_collect_tracker.py --json
"""
from __future__ import print_function

import argparse
import datetime as D
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import latency_report as LR   # noqa: E402

BASELINE_DATE = '2026-10-19'
START_DATE = '2026-10-20'
EVAL_DAYS = 5
EXTERNAL_MEDIAN_MAX = 3
N429_MAX = 1
MIN_LINES_PER_WINDOW = 5
POOLED_MIN_N = 30
DAYS_PASS_MIN = 4
SESSION = ('09:00:00', '15:20:00')


def _median(vals):
    if not vals:
        return None
    s = sorted(vals)
    m = len(s) // 2
    return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2.0


def window_external(rates):
    """RATE 줄 → 한도 창별 외부 소진. 정규장(09:00–15:20)에 첫 관측이 있는 창만."""
    wins = {}
    for x in rates:
        wins.setdefault((x['op'], x['reset']), []).append(x)
    out = []
    for (op, reset), v in sorted(wins.items(), key=lambda kv: kv[1][0]['t']):
        if not (SESSION[0] <= v[0]['t'] <= SESSION[1]):
            continue
        rems = [int(x['rem']) for x in v if x['rem'].isdigit()]
        if len(rems) < 2:
            continue
        ext = (max(rems) - min(rems)) - (len(rems) - 1)
        out.append({'op': op, 'reset': reset, 'first': v[0]['t'], 'lines': len(rems),
                    'drop': max(rems) - min(rems), 'external': ext,
                    'counted': len(rems) >= MIN_LINES_PER_WINDOW})
    return out


def day_stats(date):
    """하루 지표. RATE·트윗이 없으면 `measured=False`(미측정 ≠ 0 — 계측 4원칙 ②)."""
    lat = LR.build(date)
    tweets = LR.load_tweets(date)
    rates = LR.load_rates(date)
    wins = window_external(rates)
    counted = [w['external'] for w in wins if w['counted']]
    n429 = sum(1 for x in rates if x['st'] == '429' and SESSION[0] <= x['t'] <= SESSION[1])
    med = _median(counted)
    if med is None:
        sole = None
    else:
        sole = med <= EXTERNAL_MEDIAN_MAX
    return {'date': date, 'measured': bool(rates) or bool(tweets),
            'rate_measured': bool(rates), 'receiver_log': lat['receiver_log'],
            'n': lat['n'], 'p50': lat['p50'], 'p90': lat['p90'], 'max': lat['max'],
            'day_verdict': lat['verdict'], 'page_errors': lat['page_errors'],
            'error_minutes': lat['error_minutes'], 'n429_session': n429,
            'windows': len(counted), 'external_median': med,
            'external_max': max(counted) if counted else None,
            'sole_pass': sole, 'n429_pass': (n429 <= N429_MAX) if rates else None,
            'lats': [t['lat'] for t in tweets]}


def eval_dates(upto):
    """START_DATE..upto 의 평일 중 수신기 로그가 있는 날(앞에서부터 EVAL_DAYS 개)과,
    로그가 없는 평일(휴장·미기동 — 미측정) 목록."""
    d = D.date.fromisoformat(START_DATE)
    end = D.date.fromisoformat(upto)
    got, missing = [], []
    while d <= end and len(got) < EVAL_DAYS:
        if d.weekday() < 5:
            p = os.path.join(LR.ROOT, 'logs', 'peter2_receiver_%s.log' % d.strftime('%Y%m%d'))
            (got if os.path.exists(p) else missing).append(d.isoformat())
        d += D.timedelta(days=1)
    return got, missing


def build(upto=None):
    upto = upto or D.date.today().isoformat()
    dates, missing = eval_dates(upto)
    base = day_stats(BASELINE_DATE)
    days = [day_stats(x) for x in dates]
    pooled = [v for s in days for v in s['lats']]
    p90 = LR._pct(pooled, 0.9)
    sole_days = sum(1 for s in days if s['sole_pass'])
    if len(days) < EVAL_DAYS:
        final = 'IN_PROGRESS'
    elif len(pooled) < POOLED_MIN_N:
        final = 'INSUFFICIENT'
    elif sole_days < DAYS_PASS_MIN:
        final = 'STILL_SHARED'
    elif p90 is not None and p90 <= LR.P90_LIMIT_SEC:
        final = 'IMPROVED'
    else:
        final = 'NOT_LIMIT'
    for s in [base] + days:
        s.pop('lats', None)
    return {'baseline': base, 'days': days, 'missing_weekdays': missing,
            'pooled_n': len(pooled), 'pooled_p90': p90, 'sole_days': sole_days,
            'eval_days': EVAL_DAYS, 'final': final, 'upto': upto}


_FINAL_TXT = {
    'IN_PROGRESS': '진행 중 — 평가 창 5거래일 미도달(중간값은 참고만)',
    'INSUFFICIENT': '판정 불가 — 트윗 표본 부족, 평가 창 연장(기준 그대로)',
    'STILL_SHARED': '아직 공유 소비 — MW0602 중지 미반영 또는 다른 소비자, 사용자 확인',
    'IMPROVED': '개선 확인 — 단독 수집으로 한도·지연 모두 해소, F-4 불필요',
    'NOT_LIMIT': '한도는 풀렸으나 지연 잔존 — 03 §2 「혼자 소진」 가지(RELOAD_SEC·F-4)',
}


def _mark(v):
    return {True: 'PASS', False: '**FAIL**', None: '미측정'}[v]


def render(r):
    L = ['# 피터2 단독 수집 추적 (MW0602 수집기 중지 · 2026-10-20~)', '',
         '- 최종: **%s** — %s' % (r['final'], _FINAL_TXT[r['final']]),
         '- 평가 창 %d/%d거래일 · ① 단독 PASS %d일(필요 %d) · 통합 트윗 n=%d · 통합 p90=%s초(합격 ≤ %d)'
         % (len(r['days']), r['eval_days'], r['sole_days'], DAYS_PASS_MIN, r['pooled_n'],
            r['pooled_p90'], LR.P90_LIMIT_SEC), '']
    if r['missing_weekdays']:
        L += ['- 수신기 로그 없는 평일(휴장·미기동 — 미측정, 평가 창에서 제외): %s'
              % ', '.join(r['missing_weekdays']), '']
    L += ['| 날짜 | 트윗 n | p50/p90/max(초) | 일 판정 | 외부소진 중앙/최대(창 수) | ① 단독 | 429(정규장) | ② | PAGE_ERROR | 오류 분 |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for tag, s in [('기준선 ', r['baseline'])] + [('', s) for s in r['days']]:
        L.append('| %s%s | %d | %s/%s/%s | %s | %s/%s (%d) | %s | %d | %s | %d | %d/380 |' % (
            tag, s['date'], s['n'], s['p50'], s['p90'], s['max'], s['day_verdict'],
            s['external_median'], s['external_max'], s['windows'], _mark(s['sole_pass']),
            s['n429_session'], _mark(s['n429_pass']), s['page_errors'], s['error_minutes']))
    L += ['', '외부 소진 = 한도 창 안 rem 감소폭 − (우리 관측 줄 − 1). 0 근처면 우리만 쓰고 있다.',
          '기준선(10-19)은 MW0602 가 함께 돌던 날이다 — 판정에 들어가지 않는다.']
    return '\n'.join(L)


def evidence_lines(day_iso):
    """collect_evidence.py §9-e 용 짧은 요약(마크다운 줄 목록)."""
    r = build(day_iso)
    today = [s for s in r['days'] if s['date'] == day_iso]
    out = ['- 최종: **%s** — %s (평가 %d/%d거래일)' % (r['final'], _FINAL_TXT[r['final']],
                                                    len(r['days']), r['eval_days'])]
    if today:
        s = today[0]
        out.append('- 오늘: 트윗 n=%d · p90=%s초 · 외부소진 중앙 %s(기준선 %s) · 429(정규장) %d건 · ① %s · ② %s'
                   % (s['n'], s['p90'], s['external_median'],
                      r['baseline']['external_median'], s['n429_session'],
                      _mark(s['sole_pass']), _mark(s['n429_pass'])))
    else:
        out.append('- 오늘은 평가 창 밖이거나 수신기 로그 없음 — 미측정')
    out.append('- 전체 표: `python tools/peter2_live/sole_collect_tracker.py --upto %s`' % day_iso)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--upto', default=None)
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    r = build(a.upto)
    txt = json.dumps(r, ensure_ascii=False, indent=1) if a.json else render(r)
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    print(txt)
    return {'STILL_SHARED': 2, 'NOT_LIMIT': 2}.get(r['final'], 0)


if __name__ == '__main__':
    sys.exit(main())

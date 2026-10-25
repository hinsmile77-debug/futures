# -*- coding: utf-8 -*-
"""base_shift.json 의 기준점별 일손익을 09:00 대비 일별 우열로 비교한다(만원, ±0.5만 이내 = 동일)."""
import json
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
r = json.load(open('base_shift.json', encoding='utf-8'))
for mode in 'AB':
    b0 = r[mode + '_09:00']['days']
    print('mode', mode)
    for m in range(1, 11):
        d = r['%s_09:%02d' % (mode, m)]['days']
        s = sorted((d[x] - b0[x]) / 1e4 for x in b0)
        print('09:%02d up %2d down %2d same %2d  sum %+7.1f  best %+6.1f worst %+6.1f  drop-best %+7.1f' % (
            m, sum(v > 0.5 for v in s), sum(v < -0.5 for v in s), sum(abs(v) <= 0.5 for v in s),
            sum(s), s[-1], s[0], sum(s[:-1])))

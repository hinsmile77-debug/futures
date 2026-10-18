# -*- coding: utf-8 -*-
"""보조 집계 — 재진입 거래 단독 손익 · 보류 구간 · 가드 민감도. stop_reentry_cf.py 를 import 한다."""
import sys, io
sys.argv = [sys.argv[0]]
import stop_reentry_cf as M
ev, ho = M.load(M.EVAL), M.load(M.HOLD)
for gm in ("rec", "all"):
    R, H = M.sweep(ev, gm), M.sweep(ho, gm)
    print("\n===== 가드 %s =====" % gm)
    print("손절/재진입/상한 :  10일 총 | 최악일 | PF | 재진입거래 n·합 | 보류5일 총 | 보류 최악일")
    for sn in ("0.6ATR(현행)", "0.4ATR", "0.3ATR", "12pt", "8pt", "3pt"):
        for rm in ("halt", "same", "sig", "rearm", "stoplvl", "half", "entrylvl", "cool10"):
            for cap in (3, 6):
                st, dl, tr = R[(sn, rm, cap)]
                re = [t["net"] for t in tr if t["re"]]
                hs = H[(sn, rm, cap)][0]
                print("  %-12s %-8s %d : %7.1f | %6.1f | %4.2f | %2d %7.1f | %6.1f | %6.1f" % (
                    sn, rm, cap, st["tot"] / 1e4, st["worst"] / 1e4, st["pf"], len(re), sum(re) / 1e4,
                    hs["tot"] / 1e4, hs["worst"] / 1e4))

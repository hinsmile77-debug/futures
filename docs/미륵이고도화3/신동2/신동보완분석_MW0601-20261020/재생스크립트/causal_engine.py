# -*- coding: utf-8 -*-
"""인과 엔진(확인 시각 우선 R3) + 실험 변형 MAIN_F2(트레일+F2) · V2_F2(F2만). 모든 소스 치환은 정확히 1회인지 검사한다."""
import sys, os, re, inspect, datetime as dt
ROOT=r"C:\Users\82108\PycharmProjects\futures"; sys.path.insert(0, ROOT)
from strategy.shindong import engine as E, runner, spec as S
from strategy.shindong.calendar import select_flow_product
_r3=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"causal_r3.py"),encoding="utf-8").read()
R3_CAUSAL=_r3.split("R3_CAUSAL='''",1)[1].split("'''",1)[0]
src=inspect.getsource(E.run_day)
a=src.index("    # R3\n"); b=src.index('    return {"decision": dec, "trades": trades}')
src=src[:a]+R3_CAUSAL+src[b:]
def sub1(s, old, new):
    assert s.count(old)==1, ("치환 실패", old, s.count(old)); return s.replace(old,new)
src=sub1(src,"def run_day(","def run_day_c(")
src=sub1(src,'e2 = f2 = variant == "SHADOW_E2F2"','e2 = variant == "SHADOW_E2F2"; f2 = variant in ("SHADOW_E2F2", "MAIN_F2", "V2_F2")')
m=re.search(r'elif variant in \(("MAIN"[^)]*)\):', src); assert m, "트레일 분기 없음"
src=sub1(src,m.group(0),'elif variant in (%s, "MAIN_F2"):'%m.group(1))
ns=E.__dict__; exec(src, ns); run_day_c=ns["run_day_c"]
DB=os.path.join(ROOT,"data","db"); P=[os.path.join(DB,x) for x in ("raw_data.db","option_flow.db","premarket_levels.db")]
def inputs(d0):
    prod=select_flow_product(dt.date.fromisoformat(d0))[0]; return runner.load_inputs(d0,prod,*P)

# -*- coding: utf-8 -*-
"""[MW0601 2026-10-27] 신동2AI 「피터의 방법」 — 시가 범위 상자(B0·B1·B2) · 채점 · P맥점 반발 판정. **순수 함수**.

피터 실례: 10-22 10:00 「875 895 싸움」(OR 873.85–895.20 → 875 이탈 뒤 −23pt 가속) ·
           10-26 09:09 「870 850 싸움」(OR 854.0–868.3, 하단 850 = 먼스리 풋벽·삼중 바닥 → 종일 안에서 놀다 850.00 마감).
정의·문턱 = `docs/미륵이고도화3/피터2/피터방법_사전등록_MW0601.json` 의 box · hypotheses (코드에 복제하지 않는다).

봉 = [hm, o, h, l, c]. 미래 참조 금지: `make_boxes(bars, T)` 는 hm < T 인 봉만 읽는다.
"""
import math


def _hm(t):
    return int(t[:2]) * 60 + int(t[3:5])


def opening_range(bars, T, start="08:45"):
    pre = [b for b in bars if _hm(start) <= _hm(b[0]) < _hm(T)]
    if not pre:
        return None
    return dict(lo=min(b[3] for b in pre), hi=max(b[2] for b in pre), last=pre[-1][4], n=len(pre))


def _snap(edge, side, anchors, max_d):
    """OR 변에서 바깥쪽 max_d 안의 앵커 중 변에 가장 가까운 값. 없으면 None."""
    if side == "lo":
        c = [a for a in anchors if edge - max_d <= a <= edge]
        return max(c) if c else None
    c = [a for a in anchors if edge <= a <= edge + max_d]
    return min(c) if c else None


def make_boxes(bars, T, anchors, cfg):
    """T 시점 상자 3종. OR 이 없으면 None(미측정)."""
    bx = cfg["box"]
    orr = opening_range(bars, T, bx.get("or_start", "08:45"))
    if not orr:
        return None
    r = bx["round_pt"]
    b1 = [math.floor(orr["lo"] / r) * r, math.ceil(orr["hi"] / r) * r]
    slo = _snap(orr["lo"], "lo", anchors or [], bx["snap_max_pt"])
    shi = _snap(orr["hi"], "hi", anchors or [], bx["snap_max_pt"])
    b2 = [slo if slo is not None else b1[0], shi if shi is not None else b1[1]]
    w = b2[1] - b2[0]
    b0 = [round(orr["last"] - w / 2, 2), round(orr["last"] + w / 2, 2)]
    return dict(T=T, or_lo=orr["lo"], or_hi=orr["hi"], last=orr["last"],
                B0=b0, B1=b1, B2=b2, snapped=dict(lo=slo is not None, hi=shi is not None))


def score_box(bars, box, T, cfg, end=None):
    """T 이후 end(기본 15:10)까지: held · 첫 이탈(1분 종가 ≥ break_close) · 이탈 뒤 60분 MFE/MAE."""
    bx = cfg["box"]
    end = end or bx.get("session_end", "15:10")
    tol, brk, win = bx["hold_tol_pt"], bx["break_close_pt"], bx["ext_window_min"]
    post = [b for b in bars if _hm(T) <= _hm(b[0]) <= _hm(end)]
    if not post:
        return None
    lo, hi = box
    held = all(b[2] <= hi + tol and b[3] >= lo - tol for b in post)
    out = dict(held=held, n_bars=len(post), break_side=None, break_t=None, ext=None, mae=None)
    for i, b in enumerate(post):
        side = "up" if b[4] >= hi + brk else "dn" if b[4] <= lo - brk else None
        if not side:
            continue
        fut = [x for x in post[i + 1:] if _hm(x[0]) <= _hm(b[0]) + win]
        out.update(break_side=side, break_t=b[0], break_px=b[4])
        if fut:
            if side == "up":
                out["ext"] = round(max(x[2] for x in fut) - b[4], 2)
                out["mae"] = round(b[4] - min(x[3] for x in fut), 2)
            else:
                out["ext"] = round(b[4] - min(x[3] for x in fut), 2)
                out["mae"] = round(max(x[2] for x in fut) - b[4], 2)
        break
    return out


def box_position(px, box):
    """상자 안 위치 0(하단)–1(상단). 밖이면 <0 또는 >1."""
    if px is None or not box or box[1] <= box[0]:
        return None
    return round((px - box[0]) / (box[1] - box[0]), 3)


def level_reaction(bars, level, cfg, start="09:00", end="15:10"):
    """레벨 첫 터치(±touch) 뒤 window 분 안에 되돌림(revert)이 관통(pierce)보다 먼저 오는가.

    접근 방향은 터치 직전 봉 종가로 정한다(위에서 내려와 닿으면 지지 시험, 아래에서 올라와 닿으면 저항 시험).
    반환 None = 터치 없음 / 접근 방향을 모름. 같은 봉에 둘 다 걸리면 관통(보수적)."""
    h = cfg["hypotheses"]["H-P1"]
    tp, win, rv, pc = h["touch_pt"], h["window_min"], h["revert_pt"], h["pierce_pt"]
    seq = [b for b in bars if _hm(start) <= _hm(b[0]) <= _hm(end)]
    for i, b in enumerate(seq):
        if b[3] - tp <= level <= b[2] + tp:
            if i == 0:
                return None
            prev = seq[i - 1][4]
            if abs(prev - level) <= tp:
                return None
            from_above = prev > level
            for x in seq[i:]:
                if _hm(x[0]) > _hm(b[0]) + win:
                    break
                pierce = (x[3] <= level - pc) if from_above else (x[2] >= level + pc)
                revert = (x[2] >= level + rv) if from_above else (x[3] <= level - rv)
                if pierce:
                    return dict(t=b[0], side="지지" if from_above else "저항", ok=False)
                if revert:
                    return dict(t=b[0], side="지지" if from_above else "저항", ok=True)
            return dict(t=b[0], side="지지" if from_above else "저항", ok=None)   # 창 안 결말 없음
    return None

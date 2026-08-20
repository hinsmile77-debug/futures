#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""미륵이(futures) 일일 점검 — 증거 수집기.

표준 라이브러리만 쓴다. **Python 3.7 호환** (py37_32 런타임에서도 돈다).

메시아용 수집기와 달리 로그 파일명을 미리 알지 못해도 동작한다.
날짜 토큰(20260812 / 2026-08-12 / 260812)을 파일명에 가진 것을 스스로 찾아
분류·요약한다. 사냥개가 냄새로 찾는 방식이고, 목줄(config)을 채우면
정해진 곳만 뒤진다.

사용:
    python scripts/collect_evidence.py --discover          # 무엇이 있는지 먼저 본다
    python scripts/collect_evidence.py --phase pre
    python scripts/collect_evidence.py --phase post --date 2026-08-11 --out docs/정기점검/매일점검/evidence.md

설정 고정(선택): config/dailycheck_targets.json
    {"scan_dirs": ["logs", "data/logs"], "process_map": {"main": "trader_", "eod": "eod_"}}
"""

from __future__ import annotations

import argparse
import io
import json
import os
import platform
import re
import subprocess
import sys
from datetime import date as _date
from datetime import datetime, timedelta

# ------------------------------------------------------------------ 시간대
# py3.7 에는 zoneinfo 가 없다. KST 는 고정 오프셋이라 직접 만든다.
try:
    from datetime import timezone

    KST = timezone(timedelta(hours=9))
except Exception:  # pragma: no cover
    KST = None


def now_kst():
    if KST is None:
        return datetime.now()
    return datetime.now(KST)


def ts_kst(epoch):
    if KST is None:
        return datetime.fromtimestamp(epoch)
    return datetime.fromtimestamp(epoch, KST)


# ------------------------------------------------------------------ 기본 설정
DEFAULT_CONFIG = {
    # 로그가 있을 만한 곳. 없으면 무시한다.
    "scan_dirs": ["logs", "log", "data", "data/logs", "output/logs", "."],
    "scan_depth": 2,
    # 파일명에 이 문자열이 있으면 아예 무시한다 (호가처럼 수십 MB짜리, 모델 백업 등)
    "exclude_patterns": [".bak_", "__pycache__", ".pkl", ".joblib", ".parquet", ".csv"],
    # 로그 다이제스트 순서. 크기가 아니라 중요도로 고른다 —
    # TRADE 는 15KB지만 강제청산이 거기 있고, HOGA 는 51MB지만 원시 호가일 뿐이다.
    "priority_logs": [
        "_TRADE", "_WARN", "_SYSTEM", "_SIGNAL", "_LEARNING", "_HEALTH",
        "retrain_eod", "retrain_intraday", "_MICRO", "_DATA", "_PROBE",
        "launcher_", "_DEBUG", "_BACKFILL",
    ],
    # 인벤토리에는 남기되 본문은 훑지 않는다.
    # 호가 원본처럼 수십 MB짜리는 "존재와 크기"가 증거이지 내용은 읽을 것이 아니다.
    "never_digest_patterns": ["_HOGA"],
    "max_logs_digested": 8,
    # 이보다 작은 .txt 는 로그가 아니라 마커·리포트로 보고 전문을 싣는다
    "marker_max_bytes": 8192,
    # 그 국면까지 왔으면 있어야 하는 완료 마커
    "expected_markers": [
        {"contains": "daily_close_done", "phase": "post",
         "why": "15:40 일일 마감 완료 마커"},
        {"contains": "eod_retrain_done", "phase": "post",
         "why": "EOD 재학습 완료 마커 — 없으면 모델 미교체 → 다음날 CB③ HALT 위험"},
        {"contains": "strategy_report", "phase": "post",
         "why": "일일 전략 리포트"},
    ],
    # 하루의 뼈대 — CLAUDE.md "매분 실행 파이프라인 9단계" 기준
    "anchors": [
        {"at": "08:40", "label": "런처 기동 (Mireuk_batch)", "phase": "pre"},
        {"at": "08:55", "label": "매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작", "phase": "pre"},
        {"at": "09:00", "label": "정규장 개장 · 매분 루프 시작", "phase": "pre"},
        {"at": "10:00", "label": "장중 초반", "phase": "intra"},
        {"at": "12:00", "label": "장중 중간점", "phase": "intra"},
        {"at": "14:00", "label": "장중 후반 · 장중 재학습", "phase": "intra"},
        {"at": "15:10", "label": "**오버나이트 금지 — 강제 청산** (절대원칙 1)", "phase": "post"},
        {"at": "15:18", "label": "안전망 청산 (STEP 8 5단계 마지막)", "phase": "post"},
        {"at": "15:40", "label": "자가학습 일일 마감 + SHAP 피처 심사", "phase": "post"},
        {"at": "15:47", "label": "EOD 재학습(py310_64) 완료", "phase": "post"},
    ],
    "anchor_window_minutes": 6,
    "gap_scan_window": ["08:55", "15:12"],
    "gap_threshold_minutes": 10,
    # 매분 루프이므로 정상이면 1분 간격 기록이 있어야 한다
    "minute_loop_window": ["09:00", "15:10"],
    # 이 정도 분(minute)을 덮는 로그만 "매분 루프 로그"로 보고 커버리지를 잰다.
    # EOD 재학습 로그처럼 몇 줄뿐인 파일에 커버리지 0%를 들이대면 경보만 시끄러워진다.
    "main_loop_min_minutes": 60,
    # 비우면 "분 커버리지가 충분한 모든 로그"가 대상. 채널별로 나뉜 구조에서는
    # 매분 도는 본체 채널만 지정하는 편이 낫다. 예: ["_SYSTEM"]
    "main_loop_log_patterns": [],
    # 이 토큰이 보이면 무조건 인용한다 (대소문자 무시, 부분일치, 한 줄당 첫 매치만)
    # 2026-08-12 MW0601 실측 로그에서 뽑았다 — 추상적 키워드가 아니라 실제로 찍히는 문자열이다.
    "always_quote_patterns": [
        "[CB]", "연속 손절", "HALT", "CIRCUIT",
        "강제청산",
        # [MW0601 471차 F-1·F-2] 15:10 청산 1차 경로(분봉 구동)와 2차 안전망(30s 틱)의
        # 태그. **"안전망"보다 앞에 둬야 한다** — 한 줄당 첫 매치만 채택(break)하므로
        # 뒤에 두면 D2 발동 로그가 "안전망" 버킷으로 들어가 §11 적신호 6번 판정이
        # 이 태그를 못 본다.
        "[ForceExitPass]", "[SchedForceExit]",
        "[ExitCooldown]", "안전망", "FORCED",
        "0xC0000409", "STACK_BUFFER", "Traceback", "MemoryError", "OutOfMemory", "메모리 부족",
        "메인 스레드 블로킹", "[Brier] 과신", "[SHAP] 슬로우",
        "degraded=ON", "level=CRITICAL",
        "축퇴", "WeightCollapse", "ConstOut", "ConfFloorGuard",
        "전략 상태 경보", "판정  :",
        "[Shutdown]", "자동 종료", "기동 복원",
        "PSI",
    ],
    # 거래일 요약 — 이름있는 그룹으로 뽑는다. 로그 문구가 바뀌면 여기만 고치면 된다.
    "day_summary_patterns": {
        "entry_check": r"\[진입체크\]\s*(?P<dir>\S+)\s+(?P<qty>\d+)계약\s+(?P<grade>[A-Z]급(?:\(원시[A-Z]\))?)\s*\|\s*(?P<checks>[^|]+?)\s*\|\s*conf=(?P<conf>[\d.]+)%",
        "entry": r"\[Position\] 진입 (?P<dir>\w+) (?P<qty>\d+)계약 @ (?P<px>[\d.]+).*?horizon=(?P<hz>\w+)\s+hurst=(?P<hurst>\S+)",
        "fill_entry": r"\[체결진입\]\s*(?P<dir>\w+)\s+(?P<qty>\d+)계약.*?보유=(?P<held>\d+)계약",
        "exit": r"\[Position\] 체결청산 (?P<dir>\w+) @ (?P<px>[\d.]+)\s*\|\s*PnL=(?P<pt>[+-][\d.]+)pt\s*\((?P<won>[+-][\d,]+)원\)\s*\|\s*(?P<reason>.+?)\s*$",
        # [MW0601 482차 / F-4] 부분청산 레그 — 계측 4원칙 ①(포지션 단위가 기본).
        # `체결청산`만 세면 TP1 부분청산·손절1차 조기축소로 빠져나간 레그가 통째로
        # 사라진다. 2026-08-20 실측: 레그 7 중 3레그(-118,014원)가 은닉돼 당일 순손실이
        # 34% 과소, 승률이 25%p 과소 보고됐다.
        # ⚠ **체결 단위**(`[Position] 체결부분청산`)를 쓴다. 요약 라인
        #   (`[TP1 부분청산]`·`[손절1차 조기축소]`)은 이 체결들의 합이라 둘 다 세면
        #   이중계상이다(10:55:17 실측: -61,628 + -60,628 = -122,256 = 요약 라인).
        "partial_exit": r"\[Position\] 체결부분청산 (?P<qty>\d+)계약 @ (?P<px>[\d.]+)\s*\|\s*잔여=(?P<rem>\d+)계약\s*\|\s*PnL=(?P<pt>[+-][\d.]+)pt\s*\((?P<won>[+-][\d,]+)원\)\s*\|\s*(?P<reason>.+?)\s*$",
        # 포지션 종료 표식 — 조립된 포지션 수와 대조하는 정합성 축
        "pos_done": r"\[청산 완료\] PnL=(?P<pt>[+-][\d.]+)pt\s*\((?P<won>[+-][\d,]+)원\)",
        "block": r"\[차단\]\s*(?P<reason>.+?)\s*$",
        "sizer": r"\[Sizer\].*?신뢰도배수=(?P<conf_mult>[\d.]+)\s+레짐배수=(?P<regime_mult>[\d.]+)\s+안전배수=(?P<safe_mult>[\d.]+).*?→\s*(?P<qty>\d+)계약",
        "cb": r"\[CB\]\s*(?P<msg>.+?)\s*$",
        "block_ms": r"메인 스레드 블로킹.*?간격 (?P<ms>\d+)ms|간격 (?P<ms2>\d+)ms — 메인 스레드 블로킹",
    },
    "banner_start": "전략 상태 경보",
    "banner_lines": 8,
    # config/settings.py 에서 값을 확인할 상수 — CLAUDE.md 절대원칙·한시예외 대응
    "invariants": [
        {"name": "CB_CONSEC_STOP_LIMIT", "expect": "9999",
         "why": "모의투자 한정 예외(CB② 사실상 비활성). 실투 전환 전 2~3 복원 필수. 재검토 기한 2026-08-29"},
        {"name": "CB3_P4_GRADE_BLOCK_ENABLED", "expect": "False",
         "why": "30m 퇴역으로 CB③-P4 상시 RESTRICTED 고착 → 차단만 비활성 (296·297차)"},
        {"name": "FP_CRITICAL_GRADE_BLOCK_ENABLED", "expect": "False",
         "why": "PSI 계측 결함으로 차단만 비활성. 371차 분위수 재설계 후 라이브 관찰 중"},
        {"name": "MAX_CONTRACTS", "expect": "3",
         "why": "431차 10→3 인하. 실전 자본 확정 시 재산출 대상"},
        {"name": "SIZING_TARGET_CAPITAL_ENABLED", "expect": "True",
         "why": "모의투자 한정. False 전환은 단독 지시로 읽지 말 것 (손실 구간 복원 위험)"},
        {"name": "SIZING_TARGET_CAPITAL_KRW", "expect": None,
         "why": "현행 5천만원. 실전 전환 기준 ⑧의 남은 해제 조건"},
        {"name": "HURST_WINDOW_N", "expect": "90", "why": "317차 재보정. 26주 WFA마다 재검증"},
        {"name": "HURST_MAX_LAG", "expect": "9", "why": "317차 재보정. 26주 WFA마다 재검증"},
        {"name": "VALIDATION_REPORT_KEEP_WEEKS", "expect": "4", "why": "주간 리포트 FIFO 보관"},
        # --- 2026-08-12 실측으로 추가된 감시 대상 ---
        {"name": "CB_ACCURACY_MIN_30M", "expect": "0.28",
         "why": "CB③ 임계. 98차(2026-06-02) FLAT 예측 제외 + 0.35→0.28. CLAUDE.md 문구 정정 완료(461차 F-3)"},
        {"name": "CB_ACC_RESTRICTED_MIN", "expect": "0.30",
         "why": "WATCH→RESTRICTED 경계. 30m 구조적 성능(0.3052)과 거의 같아 CB③-P4 비활성의 직접 원인"},
        {"name": "CB_ACCURACY_MIN_30M_STRICT", "expect": "0.42",
         "why": "과신 연속 시 강화 임계 (0.50→0.42 완화)"},
        {"name": "TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED", "expect": "False",
         "why": "311차 후속4가 처음부터 False로 신설(섀도). CLAUDE.md 한시예외 4번째 + 실전 전환 기준 ⑨ 등재(461차 F-4). ⚠ 복원 선행조건: spread_extreme_shadow 계측 배선(NEXT_TODO F-8)"},
        {"name": "LIMIT_PIN_ENTRY_BLOCK_ENABLED", "expect": "True",
         "why": "호가 상하한 핀 진입 차단 — 켜져 있어야 정상"},
        {"name": "HURST_SOFT_BLOCK_ENABLED", "expect": "True",
         "why": "Hurst 소프트 차단(사이즈 0.5배). 316~318차 재보정 계열"},
        {"name": "HEALTH_DEGRADED_BLOCK_AUTO_ENTRY", "expect": "True",
         "why": "Degraded 상태 자동진입 차단 — 켜져 있어야 정상"},
        {"name": "CB_PIPE_PAUSE_MS", "expect": "5_000",
         "why": "CB⑤ 실질 구현. `CB_API_LATENCY_LIMIT` 은 Kiwoom 레거시로 Cybos에서 미사용"},
        {"name": "ENTRY_HORIZON_B1", "expect": "3.2", "why": "1m/3m 경계 [374차 1.5→3.5, 387차 3.5→3.2] — 드리프트 항목"},
        {"name": "ENTRY_HORIZON_B2", "expect": "4.4", "why": "3m/5m 경계 [374차 2.5→4.0, 387차 4.0→4.4] — 드리프트 항목"},
        {"name": "CB_DAILY_HALT_FULL_BLOCK", "expect": "3", "why": "HALT 3회 → 완전 관망"},
        # --- 462·468차 배포분 (2026-08-14 추가). 전부 라이브 검증 대기 상태다 ---
        # ⚠ [MW0601 482차 / F-2] 아래 5건은 `origin/dev`(MW0602 운영 브랜치) **전용**이다.
        #   v9-dev 에는 상수뿐 아니라 **기능 코드 자체가 없다**(2026-08-20 전수검색: 5개 이름
        #   모두 리포 안에서 수집기 기대표에만 존재). 브랜치를 구분하지 않던 종전 기대표는
        #   MW0601 리포트에서 8거래일 연속 `미발견 ⚠` 5행을 만들었고, §11 자동 적신호
        #   15칸 중 5칸을 상시 점유해 진짜 적신호를 가렸다. `branches` 키로 범위를 좁힌다.
        {"name": "MODEL_LABEL_STATE_UNLOCK_ENABLED", "expect": "True", "branches": ["dev"],
         "why": "468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지"},
        {"name": "PRE_RETRAIN_DONE_BY_EOD_ENABLED", "expect": "True", "branches": ["dev"],
         "why": "468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치"},
        {"name": "ZONE_ENTRY_BAN_ENFORCE", "expect": "False", "branches": ["dev"],
         "why": "462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지"},
        {"name": "ZONE_ENTRY_BAN_SHADOW_ENABLED", "expect": "True", "branches": ["dev"],
         "why": "462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다"},
        {"name": "PIPE_LATENCY_EXCLUDE_MODEL_SWAP", "expect": "True", "branches": ["dev"],
         "why": "462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치)"},
    ],
    # 차단 게이트 자동 인벤토리 — 이름에 이 패턴이 있고 값이 True/False 인 상수
    "gate_flag_pattern": "BLOCK|ENABLED|DISABLE",
    # CLAUDE.md·DECISION_LOG 에 근거가 기록된 "일부러 꺼둔" 게이트.
    # 여기 없는 False 게이트는 §10에서 적신호로 올린다 — 조용히 잠든 게이트를 막기 위함.
    "documented_disabled_flags": [
        "CB3_P4_GRADE_BLOCK_ENABLED",
        "FP_CRITICAL_GRADE_BLOCK_ENABLED",
    ],
    # 텍스트로 훑을 기준 문서
    "design_docs": [
        "CLAUDE.md", "CORE.md", "ROADMAP.md",
        "_archive/plans/PROJECT_DESIGN.md",
    ],
    "devmemory_files": [
        "dev_memory/DECISION_LOG.md",
        "dev_memory/NEXT_TODO.md",
        "dev_memory/CURRENT_STATE.md",
        "dev_memory/SESSION_LOG.md",
    ],
    # 날짜 토큰이 없어 인벤토리에 안 잡히는 상태 파일 — 존재와 mtime 만 본다
    "state_files": [
        {"path": "data/_exit_normally", "why": "정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라"},
    ],
    "report_dirs": ["docs/정기점검/매일점검", "docs/정기점검/금요일점검"],
    # --out-auto 가 쓰는 출력 폴더. 파일명에 PC명이 들어가 두 PC가 서로를 덮지 않는다.
    "evidence_dir": "docs/정기점검/매일점검",
    "max_error_samples_per_tag": 2,
    "max_warn_tags": 12,
    "msg_truncate": 240,
    "max_files_per_group": 6,
    "max_log_bytes": 40 * 1024 * 1024,
}

LEVEL_RE = re.compile(r"\b(CRITICAL|FATAL|ERROR|WARNING|WARN|INFO|DEBUG)\b")
LEVEL_ORDER = ["CRITICAL", "FATAL", "ERROR", "WARNING", "WARN", "INFO", "DEBUG"]
# 2026-08-12 09:00:01,123  /  2026-08-12T09:00:01  /  [09:00:01]  /  09:00:01
TIME_RE = re.compile(r"(?:(\d{4})[-/](\d{2})[-/](\d{2})[T ])?(\d{2}):(\d{2}):(\d{2})")
# 미륵이 표준 라인:
#   2026-08-12 08:40:48 [INFO] SYSTEM: [FaultHandler] 활성화 | file=... PID=17492
#   └ 날짜/시각      └ 레벨   └ 채널  └ 컴포넌트
# 첫 대괄호는 **레벨**이므로 태그로 잡으면 안 된다. 컴포넌트는 채널 뒤 대괄호다.
MIREUK_LINE_RE = re.compile(
    r"^\S+\s+\S+\s+\[(?P<level>[A-Z]+)\]\s+(?P<channel>[A-Z_]+):\s*(?:\[(?P<comp>[^\]]{1,50})\]\s*)?(?P<msg>.*)$"
)
# 그 밖의 포맷용 폴백
TAG_BRACKET_RE = re.compile(r"\[([A-Za-z가-힣_][\w가-힣.\-]{1,40})\]")
TAG_LOGGER_RE = re.compile(r"\s([A-Za-z_][\w.]{2,50})\s+[-|:]\s")
LEVEL_NAMES = frozenset(LEVEL_ORDER)
DATE_TOKEN_KEYS = ("ymd", "y_m_d", "ymd2", "md")


# ---------------------------------------------------- [480차 G-2] 로그 종료시각 기준선
_TS_RE = re.compile(r"(\d{2}):(\d{2}):(\d{2})")


def log_end_minute(path):
    """로그 파일의 **마지막 기록 시각**(분)을 꼬리에서 읽는다.

    전문을 파싱하지 않는다 — 12거래일치를 매 점검마다 훑으면 그 자체가 IO 부하다
    (2026-08-10 CB⑤ 자가유발 전례). 꼬리 8KB만 읽고 마지막 `HH:MM:SS`를 취한다.
    실패 시 mtime으로 떨어지되 **그 사실을 함께 반환**한다(계측 4원칙 ④).

    반환: (분, 출처) 또는 (None, 사유)
    """
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            f.seek(max(0, size - 8192))
            tail = f.read().decode("utf-8", "replace")
    except Exception as exc:
        return None, "읽기 실패(%s)" % exc
    hits = _TS_RE.findall(tail)
    if hits:
        h, m, _s = hits[-1]
        return int(h) * 60 + int(m), "로그 본문"
    try:
        mt = ts_kst(os.stat(path).st_mtime)
        return mt.hour * 60 + mt.minute, "mtime 폴백(본문에 시각 없음)"
    except Exception as exc:
        return None, "mtime 실패(%s)" % exc


def prior_log_end_baseline(root, day, suffix="_SYSTEM.log", n=5):
    """직전 n거래일의 같은 채널 로그 종료시각 — 오늘을 재는 자.

    왜 필요한가: 2026-08-19 동결일, 수집기 §11은 공백을 정확히 짚었지만 *"정상일에는
    15:40까지 로그가 있다"* 는 **비교 기준선이 표에 없어서**, 사람이 직전 12일 로그를
    직접 열어 확인해야 했다. 그 확인을 기계가 한다.

    파일명 규약 `YYYYMMDD_SYSTEM.log`만 본다. 주말·휴장일은 파일 자체가 없으므로
    자동으로 빠진다(거래일 캘린더를 따로 들이지 않는 이유).
    """
    logs_dir = os.path.join(root, "logs")
    if not os.path.isdir(logs_dir):
        return []
    today_tok = day.strftime("%Y%m%d")
    cands = []
    for name in os.listdir(logs_dir):
        if not name.endswith(suffix):
            continue
        tok = name[: len(today_tok)]
        if not tok.isdigit() or tok >= today_tok:
            continue
        cands.append((tok, os.path.join(logs_dir, name)))
    cands.sort(reverse=True)
    out = []
    for tok, path in cands[:n]:
        mnt, src = log_end_minute(path)
        if mnt is not None:
            out.append({"date": tok, "minute": mnt, "source": src})
    return out


def median_minute(rows):
    vals = sorted(r["minute"] for r in rows)
    if not vals:
        return None
    return vals[len(vals) // 2]


def eprint(*a):
    sys.stderr.write(" ".join(str(x) for x in a) + "\n")


# ------------------------------------------------------------------ 유틸
def find_repo_root(start):
    cur = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(cur, "CLAUDE.md")) and os.path.isdir(os.path.join(cur, "dev_memory")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    cur = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(cur, ".git")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return os.path.abspath(start)
        cur = parent


def parse_date(s):
    if not s:
        return now_kst().date()
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%Y%m%d", "%y%m%d", "%m/%d", "%m-%d"):
        try:
            d = datetime.strptime(s, fmt)
        except ValueError:
            continue
        if fmt in ("%m/%d", "%m-%d"):
            d = d.replace(year=now_kst().year)
        return d.date()
    raise SystemExit("날짜 형식을 못 읽었다: %r (예: 2026-08-12 / 20260812 / 8/11)" % s)


def date_tokens(day):
    return {
        "ymd": day.strftime("%Y%m%d"),
        "y_m_d": day.strftime("%Y-%m-%d"),
        "ymd2": day.strftime("%y%m%d"),
        "md": day.strftime("%m%d"),
    }


def hhmm_to_min(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def m2hhmm(m):
    return "%02d:%02d" % (m // 60, m % 60)


def fmt_bytes(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return ("%.0f%s" % (n, unit)) if unit == "B" else ("%.1f%s" % (n, unit))
        n = n / 1024.0
    return "%sB" % n


def truncate(s, n):
    s = str(s).replace("\n", " ⏎ ").replace("\r", "").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def read_text(path, limit=None):
    for enc in ("utf-8-sig", "cp949", "latin-1"):
        try:
            with io.open(path, "r", encoding=enc, errors="strict") as f:
                return f.read() if limit is None else f.read(limit)
        except (UnicodeDecodeError, LookupError):
            continue
        except Exception as e:
            return "(읽기 실패) %s" % e
    try:
        with io.open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read() if limit is None else f.read(limit)
    except Exception as e:
        return "(읽기 실패) %s" % e


def open_text(path):
    """인코딩을 순서대로 시도해 라인 이터레이터를 준다."""
    for enc in ("utf-8-sig", "cp949"):
        try:
            f = io.open(path, "r", encoding=enc, errors="strict")
            f.readline()
            f.seek(0)
            return f
        except (UnicodeDecodeError, LookupError):
            try:
                f.close()
            except Exception:
                pass
            continue
        except Exception:
            break
    return io.open(path, "r", encoding="utf-8", errors="replace")


def run_git(root, args, timeout=25):
    try:
        p = subprocess.Popen(["git"] + list(args), cwd=root,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate(timeout=timeout)
        dec = lambda b: b.decode("utf-8", "replace").strip()
        return dec(out) if p.returncode == 0 else "(git 실패 rc=%s) %s" % (p.returncode, dec(err)[:300])
    except Exception as e:
        return "(git 실행 불가) %s" % e


# [MW0601 476차] PC 식별자 오버라이드 — 인자 > 환경변수 > 호스트명.
# 프로세스 전역으로 한 번만 정한다(build()와 --out-auto가 반드시 같은 값을 써야
# 한다 — 다르면 머리말의 PC와 파일명의 PC가 어긋난 다이제스트가 나온다).
_PC_OVERRIDE = None


def set_pc_override(pc):
    """`--pc` / `MIREUK_PC_ID` 로 PC 식별자를 강제한다. None이면 자동탐지."""
    global _PC_OVERRIDE
    _PC_OVERRIDE = (pc or "").strip().upper() or None
    return _PC_OVERRIDE


def pc_id():
    """CLAUDE.md 규약: 호스트명에서 MW#### 를 뽑는다 (utils/db_utils.py:pc_id() 와 동일 취지).

    [476차] 우선순위는 **`--pc` 인자 > `MIREUK_PC_ID` 환경변수 > 호스트명 자동탐지**다.

    왜 필요한가: 코웍/컨테이너 등 **리눅스 샌드박스에서 돌리면 호스트명이 `claude`**
    라 `MW####`를 못 뽑고 `evidence_UNKNOWN-….md` 가 조용히 생긴다. 그 상태로
    커밋하면 어느 PC의 관찰인지 영영 모른다(멀티PC — CLAUDE.md 함정③).
    실제로 2026-08-18 장후 점검이 이 경로를 밟아 `platform.node()`를 임시 주입해
    우회해야 했다. 스킬 문서(SKILL.md·RUN_ON_MW0602.md)는 `--pc MW0602`를 **필수**로
    적고 있었는데 코드에는 그 인자가 없었다 — 문서와 코드의 불일치를 코드 쪽으로 맞춘다.

    반환: (PC명, 호스트명). 오버라이드가 걸리면 호스트명은 `"<host> (override)"`.
    """
    host = platform.node() or ""
    if _PC_OVERRIDE:
        return _PC_OVERRIDE, "%s (override)" % (host or "?")
    env = (os.environ.get("MIREUK_PC_ID") or "").strip().upper()
    if env:
        return env, "%s (env MIREUK_PC_ID)" % (host or "?")
    m = re.search(r"(MW\d{4})", host, re.IGNORECASE)
    return (m.group(1).upper() if m else "UNKNOWN"), host


# ------------------------------------------------------- 증거 다이제스트 보관정책
#
# [MW0601 476차 / 지침 §2·§3] **기본값은 「지우지 않음」이다.** 2026-08-18 실측:
#
#   · `docs/정기점검` 전체 = 100파일 **3.4MB** → 용량이 삭제 사유가 될 수 없다
#   · 전부 **git 추적** 대상 → 지워도 용량이 안 줄고 grep 대상만 잃는다
#   · 일일 점검 문서의 소급 인용 꼬리 = **182일**(= 26주 WFA 주기)
#   · 증거 다이제스트 인용 26회 중 과거분 **1회** — 마흐디의 0건과 다르다
#   · 증거는 원본 로그가 있어야 재생성된다. 로그는 현재 87일치 보유
#     → **로그 보관(monthly_cleanup.py LOG_KEEP_DAYS)이 증거의 재생성 가능성을
#       결정한다.** 둘을 따로 정할 수 없다.
#
# 그래서 `--prune-days`는 **기본 끔**이다. 수단은 두되 켜는 것은 사람이 정한다.
# 켤 때도 아래가 강제된다:
#   · `keep_days < 1` 이면 아무것도 지우지 않는다(0을 "전부"로 읽지 않는다)
#   · **자기 PC 산출물만** 대상이다 — 정규식에 PC명을 박는다(멀티PC 교차삭제 방지)
#   · **mtime이 아니라 파일명의 날짜**로 판정한다
#   · 지운 파일명을 전부 인쇄한다 / 개별 실패는 경고만 낸다
#   · 보고서(`<PC>-<날짜>-점검리포트*.md`)와 접미사 스냅샷은 정규식에 **안 걸린다**
_EVIDENCE_PRUNE_MIN_KEEP = 1


def _evidence_strict_re(pcid):
    """자동 생성된 증거 다이제스트 **정확히 그 형태만**.

    `evidence_<PC>-<YYYYMMDD>_<phase>.md` 와 461차 F-6 의 비덮어쓰기 변형
    `..._<phase>_<HHMM>.md` / `..._<phase>_<HHMM>-<n>.md` 까지만 매칭한다.
    보고서·검토보고·딥다이브 md 는 `evidence_` 로 시작하지 않아 구조적으로 제외된다.
    다른 PC의 파일은 PC명이 정규식에 박혀 있어 **매칭 자체가 안 된다.**
    """
    return re.compile(
        r"^evidence_%s-(\d{8})_(pre|intra|post|all)(_\d{4}(-\d+)?)?\.md$"
        % re.escape(pcid))


def prune_evidence(root, cfg, pcid, keep_days, today, dry_run=False):
    """증거 다이제스트 FIFO 정리. 반환: (지운/지울 경로 리스트, 사유 문자열)."""
    if keep_days is None or keep_days < _EVIDENCE_PRUNE_MIN_KEEP:
        return [], "keep_days<%d — 킬스위치(아무것도 지우지 않는다)" % _EVIDENCE_PRUNE_MIN_KEEP
    if pcid == "UNKNOWN":
        # PC를 모르면 무엇이 내 것인지도 모른다. 남의 것을 지울 위험이 있으므로 멈춘다.
        return [], "PC 식별자가 UNKNOWN — 자기 PC 산출물을 특정할 수 없어 중단(--pc 를 줄 것)"
    d = os.path.join(root, cfg["evidence_dir"])
    if not os.path.isdir(d):
        return [], "증거 디렉터리 없음: %s" % d
    strict = _evidence_strict_re(pcid)
    cut = today - timedelta(days=keep_days)
    doomed = []
    for name in sorted(os.listdir(d)):
        m = strict.match(name)
        if not m:
            continue
        try:
            fd = datetime.strptime(m.group(1), "%Y%m%d").date()
        except ValueError:
            continue                      # 날짜를 못 읽으면 지우지 않는다
        if fd < cut:
            doomed.append(os.path.join(d, name))
    if dry_run:
        return doomed, "dry-run (컷오프 %s 이전)" % cut.strftime("%Y-%m-%d")
    deleted = []
    for p in doomed:
        try:
            os.remove(p)
            deleted.append(p)
        except OSError as e:
            eprint("[collect_evidence] 보관정리 실패(무해, 다음에 재시도): %s — %s"
                   % (os.path.basename(p), e))
    return deleted, "컷오프 %s 이전" % cut.strftime("%Y-%m-%d")


# ------------------------------------------------------------------ 파일 탐색
def discover_files(root, cfg, day):
    """날짜 토큰을 파일명에 가진 파일을 찾아 그룹으로 묶는다."""
    toks = date_tokens(day)
    found = []
    seen = set()
    for rel in cfg["scan_dirs"]:
        base = os.path.normpath(os.path.join(root, rel))
        if not os.path.isdir(base):
            continue
        base_depth = base.rstrip(os.sep).count(os.sep)
        for dirpath, dirnames, filenames in os.walk(base):
            if dirpath.count(os.sep) - base_depth >= cfg["scan_depth"]:
                dirnames[:] = []
            dirnames[:] = [d for d in dirnames
                           if d not in (".git", ".venv", "__pycache__", "node_modules", ".idea")]
            for fn in filenames:
                full = os.path.normpath(os.path.join(dirpath, fn))
                if full in seen:
                    continue
                if any(x.lower() in fn.lower() for x in cfg.get("exclude_patterns", [])):
                    continue
                hit = None
                for key in DATE_TOKEN_KEYS:
                    if toks[key] in fn:
                        hit = key
                        break
                if hit is None:
                    continue
                seen.add(full)
                try:
                    st = os.stat(full)
                except OSError:
                    continue
                # 파일명에서 날짜 토큰을 지운 나머지를 그룹키로 쓴다
                stem = fn
                for key in DATE_TOKEN_KEYS:
                    stem = stem.replace(toks[key], "{DATE}")
                found.append({
                    "path": full,
                    "rel": os.path.relpath(full, root).replace(os.sep, "/"),
                    "name": fn,
                    "group": stem,
                    "token": hit,
                    "size": st.st_size,
                    "mtime": st.st_mtime,
                    "ext": os.path.splitext(fn)[1].lower(),
                })
    found.sort(key=lambda x: (x["group"], x["rel"]))
    return found


def is_logish(entry):
    return entry["ext"] in (".log", ".txt", ".out", ".err", "") or "log" in entry["name"].lower()


def is_jsonish(entry):
    return entry["ext"] in (".json", ".jsonl")


# ------------------------------------------------------------------ 로그 파싱
class LogDigest(object):
    """JSON 로그와 평문 로그를 모두 받는다 — 미륵이는 평문 logging 포맷일 가능성이 높다."""

    def __init__(self, entry, cfg, day):
        self.entry = entry
        self.rel = entry["rel"]
        self.cfg = cfg
        self.day = day
        self.size = entry["size"]
        self.mtime = ts_kst(entry["mtime"])
        self.total_lines = 0
        self.json_lines = 0
        self.timed = 0
        self.records = []
        self.level_counts = {}
        self.tag_counts = {}
        self.channel_counts = {}
        self.by_level_tag = {}
        self.quoted = {}
        self.first_lines = []
        self.last_lines = []
        self.truncated = False
        # 거래일 요약용 — config 의 정규식에 걸린 것만 모은다
        self.hits = {}
        self.banner = []
        self._banner_left = 0
        self._day_re = {}
        for key, pat in (cfg.get("day_summary_patterns") or {}).items():
            try:
                self._day_re[key] = re.compile(pat)
            except re.error as e:
                eprint("[collect_evidence] day_summary_patterns['%s'] 정규식 오류: %s" % (key, e))

    def scan(self):
        if self.size > self.cfg["max_log_bytes"]:
            self.truncated = True
            return self
        tail = []
        try:
            f = open_text(self.entry["path"])
        except Exception as e:
            self.first_lines = ["(열기 실패) %s" % e]
            return self
        with f:
            for line in f:
                line = line.rstrip("\r\n")
                if not line.strip():
                    continue
                self.total_lines += 1
                if len(self.first_lines) < 5:
                    self.first_lines.append(truncate(line, 300))
                tail.append(line)
                if len(tail) > 5:
                    tail.pop(0)
                # 결산 배너는 여러 줄에 걸쳐 있어 한 줄씩 보면 뜻이 없다 — 창을 열어 통째로 담는다
                if self._banner_left > 0:
                    self.banner.append(truncate(line, 200))
                    self._banner_left -= 1
                elif self.cfg.get("banner_start") and self.cfg["banner_start"] in line:
                    self.banner.append(truncate(line, 200))
                    self._banner_left = int(self.cfg.get("banner_lines", 8))
                self._ingest(line)
        self.last_lines = [truncate(x, 300) for x in tail]
        return self

    def _ingest(self, line):
        stripped = line.lstrip()
        level = None
        tag = None
        msg = line
        rec = None
        if stripped.startswith("{"):
            try:
                rec = json.loads(stripped)
            except Exception:
                rec = None
        if isinstance(rec, dict):
            self.json_lines += 1
            level = str(rec.get("level") or rec.get("levelname") or "?").upper()
            tag = str(rec.get("tag") or rec.get("name") or rec.get("logger") or "?")
            msg = str(rec.get("msg") or rec.get("message") or "")
            tsrc = str(rec.get("ts") or rec.get("timestamp") or rec.get("asctime") or "")
        else:
            mm = MIREUK_LINE_RE.match(line)
            if mm:
                # 미륵이 표준 포맷 — 채널과 컴포넌트를 정확히 가른다
                level = mm.group("level")
                comp = mm.group("comp")
                tag = comp if comp else mm.group("channel")
                msg = mm.group("msg")
                self.channel_counts[mm.group("channel")] = \
                    self.channel_counts.get(mm.group("channel"), 0) + 1
            else:
                m = LEVEL_RE.search(line)
                level = m.group(1) if m else "PLAIN"
                tag = None
                for bm in TAG_BRACKET_RE.finditer(line):
                    if bm.group(1) not in LEVEL_NAMES:   # [INFO] 같은 레벨 대괄호는 건너뛴다
                        tag = bm.group(1)
                        break
                if tag is None:
                    ml = TAG_LOGGER_RE.search(line)
                    tag = ml.group(1) if ml else "-"
                msg = line[m.end():] if m else line
                msg = re.sub(r"^[\s\-|:]+", "", msg)
                if tag and tag != "-" and msg.startswith(tag):
                    msg = re.sub(r"^%s[\s\-|:]+" % re.escape(tag), "", msg)
            tsrc = line

        minutes = None
        hhmm = "??:??:??"
        mt = TIME_RE.search(tsrc)
        if mt:
            hhmm = "%s:%s:%s" % (mt.group(4), mt.group(5), mt.group(6))
            minutes = int(mt.group(4)) * 60 + int(mt.group(5))
            self.timed += 1

        level = level if level in LEVEL_ORDER or level == "PLAIN" else "PLAIN"
        self.level_counts[level] = self.level_counts.get(level, 0) + 1
        self.tag_counts[tag] = self.tag_counts.get(tag, 0) + 1
        entry = {"hhmm": hhmm, "minutes": minutes, "level": level, "tag": tag,
                 "msg": truncate(msg if msg else line, 600), "raw": truncate(line, 600)}
        if minutes is not None:
            self.records.append(entry)
        if level in ("ERROR", "CRITICAL", "FATAL", "WARNING", "WARN"):
            self.by_level_tag.setdefault((level, tag), []).append(entry)

        up = line.upper()
        for pat in self.cfg["always_quote_patterns"]:
            if pat.upper() in up:
                bucket = self.quoted.setdefault(pat, [])
                if len(bucket) < 8:
                    bucket.append(entry)
                break

        for key, rx in self._day_re.items():
            mh = rx.search(line)
            if mh:
                d = dict(mh.groupdict())
                d["hhmm"] = hhmm
                d["_raw"] = truncate(line, 400)
                self.hits.setdefault(key, []).append(d)

    # --- 파생 --------------------------------------------------------
    def gaps(self):
        lo = hhmm_to_min(self.cfg["gap_scan_window"][0])
        hi = hhmm_to_min(self.cfg["gap_scan_window"][1])
        thr = self.cfg["gap_threshold_minutes"]
        pts = sorted(set(e["minutes"] for e in self.records
                         if e["minutes"] is not None and lo <= e["minutes"] <= hi))
        out = []
        for a, b in zip(pts, pts[1:]):
            if b - a >= thr:
                out.append((a, b, b - a))
        return out

    def minute_coverage(self):
        """매분 루프가 정말 매분 돌았는지 — 분 단위 커버리지."""
        lo = hhmm_to_min(self.cfg["minute_loop_window"][0])
        hi = hhmm_to_min(self.cfg["minute_loop_window"][1])
        have = set(e["minutes"] for e in self.records
                   if e["minutes"] is not None and lo <= e["minutes"] <= hi)
        total = hi - lo + 1
        missing = sorted(set(range(lo, hi + 1)) - have)
        return len(have), total, missing

    def is_main_loop(self):
        """매분 루프를 도는 본체 로그인가 — 커버리지 판정 대상 여부.

        패턴이 지정돼 있으면 그 파일만 대상이다. 채널별로 로그가 갈린 구조에서는
        예측 채널이 매분 기록하지 않는 것이 정상일 수 있어, 아무 로그나 붙잡고
        "커버리지 54%"라고 하면 경보만 시끄러워진다.
        """
        pats = self.cfg.get("main_loop_log_patterns") or []
        if pats and not any(p.lower() in self.entry["name"].lower() for p in pats):
            return False
        have, _total, _missing = self.minute_coverage()
        return have >= self.cfg["main_loop_min_minutes"]

    def anchor_slices(self, anchors, phases):
        w = self.cfg["anchor_window_minutes"]
        out = []
        for a in anchors:
            if a["phase"] not in phases:
                continue
            at = hhmm_to_min(a["at"])
            hits = [e for e in self.records
                    if e["minutes"] is not None and at - w <= e["minutes"] <= at + w]
            out.append((a, hits))
        return out


# ------------------------------------------------------------------ JSON 요약
def summarize_json(path, max_chars=1800):
    raw = read_text(path)
    if raw.startswith("(읽기 실패)"):
        return raw
    stripped = raw.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            obj = json.loads(stripped)
        except Exception:
            # jsonl 일 수 있다
            lines = [l for l in stripped.splitlines() if l.strip()]
            head = lines[:3]
            tail = lines[-3:] if len(lines) > 3 else []
            return truncate("JSONL %d행\n첫: %s\n끝: %s" % (len(lines), " | ".join(head), " | ".join(tail)), max_chars)
        dumped = json.dumps(obj, ensure_ascii=False, indent=1)
        if len(dumped) <= max_chars:
            return dumped

        def fold(o, depth=0):
            if depth >= 2:
                if isinstance(o, dict):
                    return "<dict %d키: %s…>" % (len(o), ", ".join(list(o)[:8]))
                if isinstance(o, list):
                    return "<list %d건>" % len(o)
                return o
            if isinstance(o, dict):
                return dict((k, fold(v, depth + 1)) for k, v in o.items())
            if isinstance(o, list):
                head = [fold(v, depth + 1) for v in o[:3]]
                return head + (["…외 %d건" % (len(o) - 3)] if len(o) > 3 else [])
            return o
        return truncate(json.dumps(fold(obj), ensure_ascii=False, indent=1), max_chars)
    lines = [l for l in stripped.splitlines() if l.strip()]
    return truncate("JSONL %d행\n첫: %s\n끝: %s" % (
        len(lines), " | ".join(lines[:2]), " | ".join(lines[-2:])), max_chars)


# ------------------------------------------------------------------ 불변식 검사
def current_branch(root):
    """[MW0601 482차 / F-2] 현재 체크아웃된 브랜치명. 못 읽으면 None."""
    out = run_git(root, ["branch", "--show-current"])
    if not out:
        return None
    b = out.strip().splitlines()[0].strip() if out.strip() else ""
    return b or None


def check_invariants(root, cfg):
    """config/settings.py 를 import 하지 않고 정규식으로만 읽는다.

    import 하면 py37_32 전용 모듈이 딸려 들어와 터진다. 여기서는 '값이 무엇인가'만
    알면 되므로 텍스트로 읽는 편이 안전하고 빠르다.

    [MW0601 482차 / F-2] 브랜치 스코프 — 항목에 `branches` 키가 있고 현재 브랜치가
    거기 없으면 표에서 빼고 **개수와 이름을 따로 남긴다**(계측 4원칙 ③ 탈락 가시화).
    키가 없는 항목은 종전과 동일하게 전 브랜치 대상이므로 MW0602(`dev`)의 표는
    바뀌지 않는다. 브랜치를 못 읽으면(detached HEAD 등) **아무것도 빼지 않는다** —
    감시 누락보다 오탐이 낫다.

    반환: (path, rows, out_of_scope)
    """
    path = os.path.join(root, "config", "settings.py")
    if not os.path.exists(path):
        return None, [], []
    text = read_text(path)
    branch = current_branch(root)
    rows = []
    out_of_scope = []
    for inv in cfg["invariants"]:
        name = inv["name"]
        _scope = inv.get("branches")
        if _scope and branch and branch not in _scope:
            out_of_scope.append({"name": name, "branches": _scope, "why": inv.get("why", "")})
            continue
        # `NAME = 3` 뿐 아니라 `NAME: bool = True` 형태(어노테이션 대입)도 잡는다.
        # 468차 F-1/G-1 스위치가 어노테이션으로 선언돼 있어, 이걸 안 보면 실재하는
        # 상수가 `미발견 ⚠` 으로 뜬다 — 오탐이 아니라 **감시 누락**이다.
        m = re.search(r"(?m)^\s*%s\s*(?::[^=\n]+)?=\s*([^\n#]+)" % re.escape(name), text)
        actual = m.group(1).strip().rstrip(",") if m else None
        exp = inv["expect"]
        if actual is None:
            verdict = "**미발견 ⚠**"
        elif exp is None:
            verdict = "값 확인"
        elif actual == exp or actual.rstrip("_0123456789") == exp:
            verdict = "일치"
        else:
            verdict = "**불일치 ⚠**"
        rows.append({"name": name, "actual": actual, "expect": exp,
                     "verdict": verdict, "why": inv["why"]})
    # VALIDATION_CAMPAIGN mode 는 dict 안에 있어 따로 본다
    m = re.search(r"VALIDATION_CAMPAIGN\s*=\s*\{.*?[\"']mode[\"']\s*:\s*[\"'](\w+)[\"']",
                  text, re.S)
    if m:
        rows.append({"name": 'VALIDATION_CAMPAIGN["mode"]', "actual": m.group(1),
                     "expect": "standing", "why": "2026-08-01 상시 운영 전환",
                     "verdict": "일치" if m.group(1) == "standing" else "**불일치 ⚠**"})
    return path, rows, out_of_scope


# ------------------------------------------------- [MW0601 482차 / F-4] 포지션 조립기
_HHMMSS_RE = re.compile(r"(\d{2}):(\d{2}):(\d{2})")


def _rec_seconds(rec):
    """레코드의 초 단위 시각. `_raw` 앞머리의 로그 타임스탬프를 쓴다.

    `hhmm` 은 분 해상도라 같은 분 안에서 벌어지는 진입→부분청산→청산의 순서를
    복원할 수 없다(2026-08-20 10:55:00 진입 → 10:55:17 조기축소가 같은 분이다).
    """
    m = _HHMMSS_RE.search(rec.get("_raw") or "")
    if not m:
        h, mi = (rec.get("hhmm") or "00:00").split(":")[:2]
        return int(h) * 3600 + int(mi) * 60
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))


def _won(rec):
    try:
        return int((rec.get("won") or "0").replace(",", ""))
    except (TypeError, ValueError):
        return 0


def _pt(rec):
    try:
        return float(rec.get("pt"))
    except (TypeError, ValueError):
        return 0.0


def assemble_positions(merged):
    """청산 **레그**를 **포지션**으로 조립한다 — CLAUDE.md 계측 4원칙 ①.

    왜 필요한가: `trades.quantity` 와 마찬가지로 로그의 청산도 레그 단위다.
    이익 포지션은 TP1/TP2/TP3 로 쪼개져 작은 레그 여러 개가 되고, 손실 포지션은
    하드스톱 전량청산이라 큰 레그 하나가 된다. 레그로 승패를 세면 "부분청산으로
    손실을 턴 포지션이 승" 이 되고(417차가 사이징 통계 4종을 무효화한 그 오류),
    `체결청산` 만 세면 부분청산 레그의 손익이 통째로 사라진다.

    2026-08-20 실측 — 레그 7 / 포지션 4:
        수집기 §5 종전: 청산 4건 · 승 1 (25%) · -230,004원
        DB 포지션 단위: 4포지션 2승 2패(50.0%) · -348,018원
        차이 -118,014원 = 은닉된 3레그(손절1차 조기축소 2 + TP1 부분청산 1)

    조립 규칙:
      · `[Position] 진입` 이 포지션을 연다.
      · `체결부분청산` / `체결청산` 레그를 열린 포지션에 붙인다.
      · `체결청산`(전량) 이 포지션을 닫는다.
      · 포지션 pt 는 **계약 가중합** Σ(pt_i × qty_i) 이다. 레그 수량이 다르면
        비가중 합은 부호까지 뒤집힌다(utils/db_utils.py `_trend_sql` 과 동일 규약).
      · 전량청산 레그에는 수량이 안 찍히므로 직전 레그의 `잔여=` 로 역산한다.

    반환: (positions, orphans)
      positions: [{"open_hhmm","dir","entry_qty","hz","legs":[...],
                   "net_won","net_pt","closed","exit_reason"}]
      orphans:   포지션에 귀속되지 않은 레그(진입 로그가 없는 이월 포지션 등)
    """
    ev = []
    for rec in merged.get("entry", []):
        ev.append((_rec_seconds(rec), 0, "entry", rec))
    for rec in merged.get("partial_exit", []):
        ev.append((_rec_seconds(rec), 1, "partial", rec))
    for rec in merged.get("exit", []):
        ev.append((_rec_seconds(rec), 2, "full", rec))
    ev.sort(key=lambda t: (t[0], t[1]))

    positions, orphans, cur = [], [], None
    for _sec, _ord, kind, rec in ev:
        if kind == "entry":
            if cur is not None:              # 직전 포지션이 안 닫혔다 — 그대로 보존
                positions.append(cur)
            try:
                _eq = int(rec.get("qty") or 0)
            except (TypeError, ValueError):
                _eq = 0
            cur = {"open_hhmm": rec.get("hhmm"), "dir": rec.get("dir"),
                   "entry_qty": _eq, "hz": rec.get("hz"), "grade": None,
                   "legs": [], "net_won": 0, "net_pt": 0.0,
                   "closed": False, "exit_reason": None, "_rem": _eq}
            continue
        if cur is None:
            orphans.append(rec)
            continue
        if kind == "partial":
            try:
                _q = int(rec.get("qty") or 1)
            except (TypeError, ValueError):
                _q = 1
            try:
                cur["_rem"] = int(rec.get("rem"))
            except (TypeError, ValueError):
                cur["_rem"] = max(0, cur["_rem"] - _q)
        else:
            # 전량청산 — 수량 미기재. 직전 레그의 잔여로 역산(최소 1)
            _q = max(1, int(cur["_rem"] or 1))
            cur["_rem"] = 0
        cur["legs"].append({"hhmm": rec.get("hhmm"), "qty": _q,
                            "pt": _pt(rec), "won": _won(rec),
                            "reason": (rec.get("reason") or "?").strip(),
                            "kind": kind})
        cur["net_won"] += _won(rec)
        cur["net_pt"] += _pt(rec) * _q
        if kind == "full":
            cur["closed"] = True
            cur["exit_reason"] = (rec.get("reason") or "?").strip()
            positions.append(cur)
            cur = None
    if cur is not None:
        positions.append(cur)
    return positions, orphans


def day_summary(digests, cfg, out):
    """거래일 요약 — 로그 요약이 아니라 '오늘 무엇을 했는가'.

    로그 레벨 집계만으로는 이 시스템을 읽을 수 없다. 미륵이는 ERROR 를 거의 안 남기고
    (2026-08-12 하루 종일 0건) 정작 중요한 것은 INFO 로 찍히는 진입·청산·차단이다.
    """
    A = out.append
    merged = {}
    banner = []
    for dg in digests:
        for k, v in dg.hits.items():
            merged.setdefault(k, []).extend(v)
        if dg.banner and not banner:
            banner = dg.banner
    for k in merged:
        merged[k].sort(key=lambda d: d.get("hhmm") or "")

    A("## 5. 거래일 요약 — 오늘 무엇을 했는가")
    A("")
    if not merged and not banner:
        A("_거래일 패턴이 하나도 안 잡혔다. 로그 문구가 바뀌었을 수 있다 — "
          "`config/dailycheck_targets.json` 의 `day_summary_patterns` 를 확인하라._")
        A("")
        return

    # --- 전략 상태 경보 배너 (그날의 판정) ---
    if banner:
        A("### 전략 상태 경보 — 그날의 판정")
        A("")
        A("```")
        out.extend(banner)
        A("```")
        A("")

    ec = merged.get("entry_check", [])
    en = merged.get("entry", [])
    fi = merged.get("fill_entry", [])
    ex = merged.get("exit", [])
    bl = merged.get("block", [])
    sz = merged.get("sizer", [])

    A("| 항목 | 건수 |")
    A("|---|---|")
    A("| 진입체크 통과(`[진입체크]`) | %d |" % len(ec))
    A("| 진입 등록(`[Position] 진입`) | %d |" % len(en))
    A("| 체결(`[체결진입]`) | %d |" % len(fi))
    A("| 청산(`체결청산`) | %d |" % len(ex))
    A("| 차단(`[차단]`) | %d |" % len(bl))
    A("| 사이저 호출(`[Sizer]`) | %d |" % len(sz))
    A("")

    # --- 손익 — **포지션 단위가 기본**(계측 4원칙 ①) [MW0601 482차 / F-4] ---
    pe = merged.get("partial_exit", [])
    pd = merged.get("pos_done", [])
    if ex or pe:
        positions, orphans = assemble_positions(merged)
        closed = [q for q in positions if q["closed"]]
        wins = sum(1 for q in closed if q["net_won"] > 0)
        tot_won = sum(q["net_won"] for q in closed)
        tot_pt = sum(q["net_pt"] for q in closed)
        n_legs = sum(len(q["legs"]) for q in closed)

        A("### 포지션 %d건 · 승 %d (%s) · 합계 %+.2fpt (%s원)  ※ 레그 %d행"
          % (len(closed), wins,
             ("%.0f%%" % (100.0 * wins / len(closed))) if closed else "—",
             tot_pt, format(tot_won, "+,d"), n_legs))
        A("")
        A("> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식)"
          " 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준"
          " 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** —"
          " 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).")
        A("")
        A("| 진입 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |")
        A("|---|---|---|---|---|---|---|---|")
        for q in positions:
            A("| %s | %s | %s | %s | %d | %+.2f | %s | %s |" % (
                q["open_hhmm"], q.get("dir"), q.get("entry_qty"), q.get("hz") or "—",
                len(q["legs"]), q["net_pt"], format(q["net_won"], "+,d"),
                q["exit_reason"] if q["closed"] else "**미청산(보유 중)**"))
        A("")

        # 레그 상세 — 은닉되던 부분청산을 눈에 보이게 (계측 4원칙 ③ 탈락 가시화)
        A("**청산 레그 %d행** (부분청산 %d · 전량청산 %d)" % (n_legs, len(pe), len(ex)))
        A("")
        A("> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을"
          " 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다"
          "(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** —"
          " 아래 정합성 줄이 그것을 본다.")
        A("")
        A("| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |")
        A("|---|---|---|---|---|---|")
        for q in positions:
            for lg in q["legs"]:
                A("| %s | %s | %d | %+.2f | %s | %s |" % (
                    lg["hhmm"], "부분" if lg["kind"] == "partial" else "전량",
                    lg["qty"], lg["pt"], format(lg["won"], "+,d"), lg["reason"]))
        A("")

        reasons = {}
        for q in positions:
            for lg in q["legs"]:
                reasons[lg["reason"]] = reasons.get(lg["reason"], 0) + 1
        A("**청산 사유 분포(레그 단위)** — " + ", ".join(
            "`%s`×%d" % (k, v) for k, v in sorted(reasons.items(), key=lambda kv: -kv[1])))
        A("")

        # 손절 준수율 적신호는 **포지션의 최종 청산사유** 기준 — 부분청산 레그가
        # 분모를 부풀려 비율을 왜곡하지 않게 한다.
        stop_pos = sum(1 for q in closed
                       if "스톱" in (q["exit_reason"] or "") or "손절" in (q["exit_reason"] or ""))
        if stop_pos:
            A("> 최종 청산이 하드스톱·손절 계열인 포지션 %d/%d건. **손절 준수율**"
              "(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 "
              "— 진입 로그의 `손절=` 값과 대조하라." % (stop_pos, len(closed)))
            A("")

        # --- 정합성 등식 (482차 F-4) ---
        # 은닉 레그를 다시 놓치면 이 등식이 깨진다 — 회귀 자동 검출.
        leg_sum = sum(_won(e) for e in ex) + sum(_won(e) for e in pe)
        ok_sum = (leg_sum == tot_won)
        ok_cnt = (len(pd) == len(closed)) if pd else None
        _bits = ["레그합 %s = 포지션합 %s → %s" % (
            format(leg_sum, "+,d"), format(tot_won, "+,d"), "OK" if ok_sum else "**불일치 ⚠**")]
        if ok_cnt is not None:
            _bits.append("`[청산 완료]` %d건 = 조립 포지션 %d건 → %s" % (
                len(pd), len(closed), "OK" if ok_cnt else "**불일치 ⚠**"))
        if orphans:
            _bits.append("**귀속 실패 레그 %d행 ⚠**(진입 로그 없는 이월 포지션 가능)" % len(orphans))
        A("**정합성**: " + " · ".join(_bits))
        A("")

    # --- 진입 상세 ---
    if en:
        A("### 진입 %d건" % len(en))
        A("")
        A("| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |")
        A("|---|---|---|---|---|---|")
        for e in en:
            A("| %s | %s | %s | %s | %s | %s |" % (
                e["hhmm"], e.get("dir"), e.get("qty"), e.get("px"), e.get("hz"), e.get("hurst")))
        A("")
        qd = {}
        for e in en:
            qd[e.get("qty")] = qd.get(e.get("qty"), 0) + 1
        A("계약수 분포 — " + ", ".join("%s계약×%d" % (k, v) for k, v in sorted(qd.items())))
        A("")
    if ec:
        gd = {}
        fail = {}
        for e in ec:
            gd[e.get("grade")] = gd.get(e.get("grade"), 0) + 1
            for name, mark in re.findall(r"(\w+)\s*([✅❌])", e.get("checks") or ""):
                if mark == "❌":
                    fail[name] = fail.get(name, 0) + 1
        A("등급 분포 — " + ", ".join("`%s`×%d" % (k, v) for k, v in sorted(gd.items())))
        A("")
        if fail:
            A("**진입한 건들의 체크리스트 미통과 항목** — " + ", ".join(
                "`%s`×%d" % (k, v) for k, v in sorted(fail.items(), key=lambda kv: -kv[1])))
            A("")
            if any(k.startswith("vwap") for k in fail):
                A("> ⚠ **`vwap` 미통과 상태로 진입한 건이 %d건 있다.** 절대원칙 3에서 VWAP 위치는 "
                  "단기·중기 그룹 모두 미통과 시 **강제 X** 다 — 등급 상향 경로가 이를 우회했는지 확인하라."
                  % sum(v for k, v in fail.items() if k.startswith("vwap")))
                A("")

    # --- 사이저 vs 실제 ---
    if sz:
        sq = {}
        for s in sz:
            sq[s.get("qty")] = sq.get(s.get("qty"), 0) + 1
        A("### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가")
        A("")
        A("사이저 출력 계약수 — " + ", ".join("**%s계약**×%d" % (k, v) for k, v in sorted(sq.items())))
        if en:
            eq = {}
            for e in en:
                eq[e.get("qty")] = eq.get(e.get("qty"), 0) + 1
            A("")
            A("실제 진입 계약수 — " + ", ".join("**%s계약**×%d" % (k, v) for k, v in sorted(eq.items())))
            try:
                smax = max(int(k) for k in sq)
                emax = max(int(k) for k in eq)
                if smax > emax:
                    A("")
                    A("> ⚠ 사이저는 최대 **%d계약**을 냈는데 실제 진입 최대는 **%d계약**이다. "
                      "게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — "
                      "실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다." % (smax, emax))
            except (TypeError, ValueError):
                pass
        A("")
        mults = {}
        for s in sz:
            key = "conf=%s regime=%s safe=%s" % (
                s.get("conf_mult"), s.get("regime_mult"), s.get("safe_mult"))
            mults[key] = mults.get(key, 0) + 1
        A("배수 조합 상위 — " + ", ".join(
            "`%s`×%d" % (k, v) for k, v in sorted(mults.items(), key=lambda kv: -kv[1])[:5]))
        A("")

    # --- 차단 사유 ---
    if bl:
        bd = {}
        for b in bl:
            r = truncate(b.get("reason") or "?", 90)
            bd[r] = bd.get(r, 0) + 1
        A("### 차단 사유 %d건 · %d종" % (len(bl), len(bd)))
        A("")
        A("| 건수 | 사유 |")
        A("|---|---|")
        for k, v in sorted(bd.items(), key=lambda kv: -kv[1])[:20]:
            A("| %d | %s |" % (v, k))
        A("")
        items = {}
        for b in bl:
            m = re.search(r"미통과 항목:\s*(.+)$", b.get("reason") or "")
            if m:
                for it in m.group(1).split(","):
                    it = it.strip()
                    if it:
                        items[it] = items.get(it, 0) + 1
        if items:
            A("**체크리스트 미통과 항목 누적** — " + ", ".join(
                "`%s`×%d" % (k, v) for k, v in sorted(items.items(), key=lambda kv: -kv[1])))
            A("")
            A("> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 "
              "그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.")
            A("")

    # --- CB ---
    cb = merged.get("cb", [])
    if cb:
        cd = {}
        for c in cb:
            k = truncate(c.get("msg") or "?", 60)
            cd[k] = cd.get(k, 0) + 1
        A("### Circuit Breaker 이벤트 %d건" % len(cb))
        A("")
        for k, v in sorted(cd.items(), key=lambda kv: -kv[1]):
            A("- `%s` ×%d" % (k, v))
        A("")
        A("> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** "
          "카운터 로그가 보이는 것은 정상이다.")
        A("")

    # --- 메인 스레드 블로킹 ---
    bms = merged.get("block_ms", [])
    if bms:
        vals = []
        for b in bms:
            v = b.get("ms") or b.get("ms2")
            if v:
                try:
                    vals.append(int(v))
                except ValueError:
                    pass
        if vals:
            vals.sort(reverse=True)
            over = [v for v in vals if v >= 5000]
            A("### 메인 스레드 블로킹 %d건 · 최대 %dms · 5초 초과 %d건"
              % (len(vals), vals[0], len(over)))
            A("")
            A("상위 — " + ", ".join("%dms" % v for v in vals[:8]))
            A("")
            if over:
                A("> ⚠ `CB_PIPE_PAUSE_MS = 5_000`(CB⑤ 실질 구현) 이상이 **%d건**이다. "
                  "CB⑤가 실제로 발동했는지, 아니면 계측만 되고 지나갔는지 확인하라." % len(over))
                A("")


def scan_gate_flags(root, cfg):
    """`*_BLOCK_ENABLED` 류 불리언 플래그를 전수 조사한다.

    한시예외를 하나하나 손으로 적어두면 새로 생긴 것을 놓친다. 이름 규칙으로 훑으면
    "꺼져 있는데 아무도 기록해두지 않은 게이트"가 저절로 드러난다.
    """
    path = os.path.join(root, "config", "settings.py")
    if not os.path.exists(path):
        return []
    text = read_text(path)
    pat = re.compile(cfg.get("gate_flag_pattern", "BLOCK|ENABLED|DISABLE"))
    out = []
    for m in re.finditer(r"(?m)^([A-Z][A-Z0-9_]*)\s*=\s*(True|False)\b", text):
        name, val = m.group(1), m.group(2)
        if not pat.search(name):
            continue
        out.append({"name": name, "value": val,
                    "documented": name in cfg.get("documented_disabled_flags", [])})
    out.sort(key=lambda r: (r["value"] == "True", r["name"]))
    return out


# ------------------------------------------------------------------ dev_memory
def devmemory_section(root, cfg, day, out):
    A = out.append
    A("")
    A("## 8. dev_memory")
    A("")
    for rel in cfg["devmemory_files"]:
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            A("- **%s**: 없음 ⚠" % rel)
            continue
        st = os.stat(p)
        mt = ts_kst(st.st_mtime)
        fresh = "**오늘 갱신됨**" if mt.date() == day else "마지막 갱신 %s" % mt.strftime("%Y-%m-%d %H:%M")
        A("### %s — %s · %s" % (rel, fmt_bytes(st.st_size), fresh))
        # 전부 훑으면 이 절만 25KB가 된다. 꼬리 열람은 두 파일로 한정한다.
        detailed = ("DECISION_LOG" in rel) or ("NEXT_TODO" in rel)
        text = read_text(p)
        heads = [l.strip() for l in text.splitlines() if re.match(r"^#{1,3} ", l)]
        if heads:
            A("")
            A("최근 헤딩 %d개:" % min(8, len(heads)))
            A("```")
            out.extend(heads[-8:])
            A("```")
        if not detailed:
            A("")
            A("_(참고용 — 필요하면 직접 열 것)_")
            A("")
            continue
        if "NEXT_TODO" in rel:
            openitems = [l.strip() for l in text.splitlines() if re.match(r"^\s*[-*]\s*\[ \]", l)]
            A("")
            A("미완료 체크박스 **%d건** (끝에서 30건)" % len(openitems))
            if openitems:
                A("```")
                out.extend(truncate(x, 200) for x in openitems[-30:])
                A("```")
        A("")
        A("<details><summary>%s 꼬리 2.5KB</summary>" % rel)
        A("")
        A("```")
        A(text[-2500:])
        A("```")
        A("")
        A("</details>")
        A("")


# ------------------------------------------------------------------ 본문
def build(root, day, phase, cfg, discover_only=False):
    toks = date_tokens(day)
    D = toks["y_m_d"]
    phases = {"pre": ["pre"], "intra": ["pre", "intra"],
              "post": ["pre", "intra", "post"], "all": ["pre", "intra", "post"]}[phase]
    pcid, host = pc_id()
    L = []
    A = L.append

    A("# 미륵이 증거 다이제스트 — %s / %s" % (D, phase.upper()))
    A("")
    A("- 생성 %s KST · PC **%s** (`%s`)" % (now_kst().strftime("%Y-%m-%d %H:%M:%S"), pcid, host))
    A("- 리포 `%s`" % root)
    A("- 점검 범위: %s (장전=pre / 장중=intra / 장후=post)" % ", ".join(phases))
    A("- 날짜 토큰: %s" % " · ".join("`%s`" % toks[k] for k in DATE_TOKEN_KEYS))
    if pcid == "UNKNOWN":
        A("- 🔴 호스트명에서 `MW####` 를 못 뽑았다 — **이 파일은 어느 PC의 관찰인지 알 수 없다.**")
        A("  `--pc MW0601` 처럼 인자로 강제하거나 `MIREUK_PC_ID` 환경변수를 줄 것 "
          "(리눅스 샌드박스에서 돌리면 호스트명이 `claude`다). "
          "커밋/DECISION_LOG 태그도 수동 확인할 것")
    # [476차] 보관정책을 산출물 자신에 새긴다 — 파일만 보고도 "지워도 되는가"를 알 수 있게.
    A("- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, "
      "소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). "
      "정리 수단은 `--prune-days`이며 **기본 꺼져 있다**")
    A("")

    # ---- 1. 파일 인벤토리 ----
    files = discover_files(root, cfg, day)
    A("## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)")
    A("")
    if not files:
        A("**해당 날짜 토큰을 가진 파일을 하나도 못 찾았다 ⚠**")
        A("")
        A("가능성: (a) 그날 프로그램이 안 돌았다 (b) 로그가 다른 폴더에 있다 "
          "(c) 파일명에 날짜를 안 쓴다 (d) `scan_dirs` 설정이 좁다.")
        A("")
        A("현재 스캔 대상: %s (깊이 %d)" % (", ".join("`%s`" % d for d in cfg["scan_dirs"]), cfg["scan_depth"]))
        A("")
        A("`config/dailycheck_targets.json` 에 `scan_dirs` 를 지정하면 그곳만 뒤진다.")
        A("")
    else:
        groups = {}
        for e in files:
            groups.setdefault(e["group"], []).append(e)
        A("총 **%d개** 파일 · %d개 그룹" % (len(files), len(groups)))
        A("")
        A("| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |")
        A("|---|---|---|---|---|")
        for g in sorted(groups):
            items = groups[g]
            for e in items[: cfg["max_files_per_group"]]:
                A("| `%s` | %d | `%s` | %s | %s |" % (
                    g, len(items), e["rel"], fmt_bytes(e["size"]),
                    ts_kst(e["mtime"]).strftime("%m-%d %H:%M")))
            if len(items) > cfg["max_files_per_group"]:
                A("| `%s` | | … 외 %d개 | | |" % (g, len(items) - cfg["max_files_per_group"]))
        A("")

    if discover_only:
        A("---")
        A("")
        A("*`--discover` 모드다. 위 인벤토리를 보고 `config/dailycheck_targets.json` 의 "
          "`scan_dirs` 를 좁힌 뒤 `--phase` 로 다시 돌려라.*")
        return "\n".join(L)

    # ---- 2. 코드·커밋 상태 ----
    A("## 2. 코드·커밋 상태")
    A("")
    head = run_git(root, ["rev-parse", "--short", "HEAD"])
    branch = run_git(root, ["rev-parse", "--abbrev-ref", "HEAD"])
    status = run_git(root, ["status", "--porcelain"])
    dirty = [l for l in status.splitlines() if l.strip()]
    A("- HEAD `%s` · 브랜치 `%s` · 미커밋 %d건" % (head, branch, len(dirty)))
    if dirty:
        A("```")
        L.extend(dirty[:40])
        if len(dirty) > 40:
            A("… 외 %d건" % (len(dirty) - 40))
        A("```")
    nxt = (day + timedelta(days=1)).strftime("%Y-%m-%d")
    todays = run_git(root, ["log", "--oneline", "--no-decorate",
                            "--since=%s 00:00" % D, "--until=%s 00:00" % nxt])
    A("")
    A("**당일(%s) 커밋**" % D)
    A("```")
    A(todays if todays.strip() else "(당일 커밋 없음)")
    A("```")
    recent = run_git(root, ["log", "--oneline", "--no-decorate", "-12"])
    A("")
    A("**최근 커밋 12건**")
    A("```")
    A(recent)
    A("```")
    # PC 태그 규약 점검
    bad_tag = [l for l in recent.splitlines()
               if l.strip() and not re.search(r"\[MW\d{4}\]", l)]
    A("")
    if bad_tag:
        A("⚠ **PC명 태그 누락 커밋 %d건** (CLAUDE.md 멀티PC 컨벤션 위반):" % len(bad_tag))
        A("```")
        L.extend(bad_tag[:8])
        A("```")
    else:
        A("PC명 태그 규약: 최근 12건 모두 `[MW####]` 접두 확인")
    A("")

    # ---- 3. 절대원칙 불변식 ----
    A("## 3. 설정 불변식 — 절대원칙·한시예외 (config/settings.py)")
    A("")
    spath, rows, inv_oos = check_invariants(root, cfg)
    if spath is None:
        A("`config/settings.py` 를 못 찾았다 ⚠ — 경로가 바뀌었는지 확인할 것")
    else:
        A("| 상수 | 현재값 | 기대값 | 판정 | 왜 보는가 |")
        A("|---|---|---|---|---|")
        for r in rows:
            A("| `%s` | `%s` | %s | %s | %s |" % (
                r["name"], r["actual"] if r["actual"] is not None else "—",
                ("`%s`" % r["expect"]) if r["expect"] else "—",
                r["verdict"], truncate(r["why"], 90)))
        A("")
        A("> 이 표는 **의도한 예외가 여전히 의도대로인지** 보는 것이다. "
          "`불일치`는 누군가 바꿨다는 뜻이고, 바꿨다면 `dev_memory/DECISION_LOG.md` 에 근거가 있어야 한다.")
        if inv_oos:
            A("")
            A("_이 브랜치(`%s`) 범위 밖 **%d건** — 표에서 제외했다(계측 4원칙 ③): %s._" % (
                current_branch(root) or "?", len(inv_oos),
                ", ".join("`%s`(→%s)" % (r["name"], "/".join(r["branches"])) for r in inv_oos)))
            A("> 제외는 \"없어도 된다\"가 아니라 \"이 브랜치에는 기능 자체가 없다\"는 뜻이다. "
              "이식 여부는 별개 안건이며 주간회의에서 정한다.")
    A("")

    gates = scan_gate_flags(root, cfg)
    if gates:
        only_rx = re.compile(cfg.get("gate_flag_alert_pattern", "BLOCK"))
        off = [g for g in gates if g["value"] == "False"]
        undoc = [g for g in off if not g["documented"] and only_rx.search(g["name"])]
        A("### 차단 게이트 전수 인벤토리 — %d개 중 **%d개 꺼짐**" % (len(gates), len(off)))
        A("")
        A("| 플래그 | 값 | 기록됨 |")
        A("|---|---|---|")
        for g in gates:
            if g["value"] == "False":
                if g["documented"]:
                    doc = "기록됨"
                elif only_rx.search(g["name"]):
                    doc = "**미기록 ⚠**"
                else:
                    doc = "기능토글"
            else:
                doc = "—"
            A("| `%s` | %s | %s |" % (g["name"], g["value"], doc))
        A("")
        if undoc:
            A("> ⚠ **꺼져 있는데 근거가 기록되지 않은 차단 게이트 %d개**: %s" % (
                len(undoc), ", ".join("`%s`" % g["name"] for g in undoc)))
            A("> 의도한 것이면 `dev_memory/DECISION_LOG.md` 에 사유·복원조건을 적고 "
              "`config/dailycheck_targets.json` 의 `documented_disabled_flags` 에 추가하라. "
              "의도한 것이 아니면 그 자체가 P0다.")
            A("")

    # ---- 4. 로그 다이제스트 ----
    A("## 4. 마커·리포트 · 로그 다이제스트")
    A("")
    markers = [e for e in files if e["ext"] == ".txt" and 0 < e["size"] <= cfg["marker_max_bytes"]]
    marker_paths = set(e["path"] for e in markers)
    nodig = cfg.get("never_digest_patterns", [])
    logs = [e for e in files
            if is_logish(e) and e["size"] > 0 and e["path"] not in marker_paths
            and not any(x.lower() in e["name"].lower() for x in nodig)]
    skipped = [e for e in files
               if is_logish(e) and any(x.lower() in e["name"].lower() for x in nodig)]
    if skipped:
        A("_본문 미열람(설정): %s — 존재와 크기만 증거로 본다_" % ", ".join(
            "`%s` %s" % (e["name"], fmt_bytes(e["size"])) for e in skipped[:6]))
        A("")

    if markers:
        A("### 당일 마커·리포트 파일 (전문)")
        A("")
        A("완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나"
          " 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.")
        A("")
        for e in sorted(markers, key=lambda x: x["rel"]):
            A("**`%s`** — %s · %s" % (e["rel"], fmt_bytes(e["size"]),
                                      ts_kst(e["mtime"]).strftime("%m-%d %H:%M:%S")))
            A("```")
            A(read_text(e["path"], 6000).rstrip())
            A("```")
            A("")

    prio = cfg.get("priority_logs", [])

    def rank(e):
        low = e["name"].lower()
        for i, pat in enumerate(prio):
            if pat.lower() in low:
                return i
        return len(prio)

    logs.sort(key=lambda e: (rank(e), -e["size"]))
    picked = logs[: cfg["max_logs_digested"]]
    if len(logs) > len(picked):
        A("_다이제스트 대상 %d/%d개 (중요도순). 제외: %s_" % (
            len(picked), len(logs),
            ", ".join("`%s`" % e["name"] for e in logs[len(picked):][:8])))
        A("")
    digests = []
    if not logs:
        A("당일 로그 파일을 못 찾았다 ⚠")
        A("")
    for e in picked:
        dg = LogDigest(e, cfg, day).scan()
        digests.append(dg)
        A("### `%s` — %s · %d행 · 최종 %s" % (
            dg.rel, fmt_bytes(dg.size), dg.total_lines, dg.mtime.strftime("%H:%M:%S")))
        if dg.truncated:
            A("")
            A("⚠ 파일이 너무 커서(%s) 건너뛰었다. `--max-log-mb` 로 올릴 수 있다." % fmt_bytes(dg.size))
            A("")
            continue
        kind = "JSON %d행" % dg.json_lines if dg.json_lines else "평문"
        lv = ", ".join("%s=%d" % (k, v) for k, v in sorted(
            dg.level_counts.items(),
            key=lambda kv: LEVEL_ORDER.index(kv[0]) if kv[0] in LEVEL_ORDER else 99))
        A("")
        A("- 형식 %s · 시각 인식 %d행 · %s" % (kind, dg.timed, lv))
        A("")
        A("<details><summary>첫 5행 / 끝 5행</summary>")
        A("")
        A("```")
        L.extend(dg.first_lines)
        A("  …")
        L.extend(dg.last_lines)
        A("```")
        A("")
        A("</details>")
        A("")
        sev = [(k, v) for k, v in dg.by_level_tag.items() if k[0] in ("CRITICAL", "FATAL", "ERROR")]
        if sev:
            sev.sort(key=lambda kv: -len(kv[1]))
            A("**ERROR 이상**")
            A("")
            A("| level | tag | 건수 | 최초 | 최종 | 대표 |")
            A("|---|---|---|---|---|---|")
            for (level, tag), items in sev:
                A("| %s | `%s` | %d | %s | %s | %s |" % (
                    level, tag, len(items), items[0]["hhmm"], items[-1]["hhmm"],
                    truncate(items[0]["msg"], cfg["msg_truncate"])))
            A("")
            for (level, tag), items in sev[:4]:
                n = cfg["max_error_samples_per_tag"]
                A("<details><summary>%s/%s 원문 %d건</summary>" % (level, tag, min(n, len(items))))
                A("")
                A("```")
                for it in items[:n]:
                    A(it["raw"])
                A("```")
                A("")
                A("</details>")
                A("")
        warn = [(k, v) for k, v in dg.by_level_tag.items() if k[0] in ("WARNING", "WARN")]
        if warn:
            warn.sort(key=lambda kv: -len(kv[1]))
            A("**WARNING — 태그 %d종 (상위 %d)**" % (len(warn), min(len(warn), cfg["max_warn_tags"])))
            A("")
            A("| tag | 건수 | 최초 | 최종 | 대표 |")
            A("|---|---|---|---|---|")
            for (level, tag), items in warn[: cfg["max_warn_tags"]]:
                A("| `%s` | %d | %s | %s | %s |" % (
                    tag, len(items), items[0]["hhmm"], items[-1]["hhmm"],
                    truncate(items[0]["msg"], cfg["msg_truncate"])))
            A("")
        if dg.channel_counts:
            ch = sorted(dg.channel_counts.items(), key=lambda kv: -kv[1])
            A("**채널** — " + ", ".join("`%s`×%d" % (t, c) for t, c in ch[:8]))
            A("")
        top = sorted(dg.tag_counts.items(), key=lambda kv: -kv[1])[:15]
        if top:
            A("**컴포넌트 상위 15** — " + ", ".join("`%s`×%d" % (t, c) for t, c in top))
            A("")

    # ---- 5. 거래일 요약 ----
    day_summary(digests, cfg, L)

    # ---- 6. 항상 인용하는 패턴 ----
    A("## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)")
    A("")
    any_q = False
    for dg in digests:
        if not dg.quoted:
            continue
        any_q = True
        A("### `%s`" % dg.rel)
        A("```")
        for pat, items in sorted(dg.quoted.items()):
            A("--- %s ×%d(표본)" % (pat, len(items)))
            for it in items[:4]:
                A("%s %s" % (it["hhmm"], truncate(it["raw"], 220)))
        A("```")
        A("")
    if not any_q:
        A("(해당 패턴 없음 — 안전장치가 조용했거나, 계측이 없거나. 어느 쪽인지 원본으로 구분할 것)")
        A("")

    # ---- 7. 타임라인 앵커 · 매분 루프 커버리지 ----
    A("## 7. 타임라인 앵커 · 매분 루프 커버리지")
    A("")
    for dg in digests[:4]:
        if not dg.records:
            continue
        main = dg.is_main_loop()
        A("### `%s`%s" % (dg.rel, "" if main else " _(보조 로그 — 매분 루프 대상 아님)_"))
        A("")
        A("| 시각 | 앵커 | 창 내 | 대표 |")
        A("|---|---|---|---|")
        # 그 로그가 살아 있던 시간대 밖의 앵커는 "없어서 이상"이 아니라 "해당 없음"이다.
        mins = [e["minutes"] for e in dg.records if e["minutes"] is not None]
        alive = (min(mins), max(mins)) if mins else (0, 0)
        for a, hits in dg.anchor_slices(cfg["anchors"], phases):
            if not main and not hits:
                continue          # 보조 로그에 없는 앵커는 이상이 아니다
            rep = "—"
            if hits:
                sev_hit = [h for h in hits if h["level"] in ("ERROR", "CRITICAL", "FATAL", "WARNING", "WARN")]
                pick = sev_hit[0] if sev_hit else hits[0]
                rep = "%s [%s] %s" % (pick["hhmm"], pick["level"], truncate(pick["msg"], 110))
            at = hhmm_to_min(a["at"])
            in_range = alive[0] - cfg["anchor_window_minutes"] <= at <= alive[1] + cfg["anchor_window_minutes"]
            if hits:
                label = a["label"]
            elif not in_range:
                label = "_%s (이 로그 생존구간 밖)_" % a["label"]
            else:
                label = a["label"] + " ⚠"
            A("| %s | %s | %d | %s |" % (a["at"], label, len(hits), rep))
        A("")
        A("- 이 로그 생존구간: %s ~ %s" % (m2hhmm(alive[0]), m2hhmm(alive[1])))
        A("")
        if not main:
            A("_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._")
            A("")
            continue
        have, total, missing = dg.minute_coverage()
        pct = (100.0 * have / total) if total else 0.0
        A("**매분 루프 커버리지 %s~%s: %d/%d분 (%.1f%%)**" % (
            cfg["minute_loop_window"][0], cfg["minute_loop_window"][1], have, total, pct))
        if missing:
            runs = []
            s = prev = missing[0]
            for m in missing[1:]:
                if m == prev + 1:
                    prev = m
                    continue
                runs.append((s, prev))
                s = prev = m
            runs.append((s, prev))
            runs = [r for r in runs if r[1] - r[0] >= 2]
            if runs:
                A("")
                A("연속 3분 이상 기록 없는 구간 %d개:" % len(runs))
                A("")
                A("| 시작 | 끝 | 분 |")
                A("|---|---|---|")
                for a, b in runs[:15]:
                    A("| %s | %s | %d |" % (m2hhmm(a), m2hhmm(b), b - a + 1))
        A("")
        gaps = dg.gaps()
        A("**%s~%s 구간 %d분 이상 공백: %d건**" % (
            cfg["gap_scan_window"][0], cfg["gap_scan_window"][1],
            cfg["gap_threshold_minutes"], len(gaps)))
        if gaps:
            A("")
            A("| 시작 | 재개 | 공백(분) |")
            A("|---|---|---|")
            for a, b, g in gaps[:15]:
                A("| %s | %s | %d |" % (m2hhmm(a), m2hhmm(b), g))
        A("")

    # ---- [480차 G-2] 로그 종료시각 vs 직전 5거래일 ----
    # 2026-08-19 동결은 "로그가 15:40이 아니라 13:51에 끝났다"가 유일하게 눈에 띄는
    # 신호였는데, 그 판단에 필요한 기준선이 리포트에 없어 사람이 직전 12일 로그를
    # 직접 열어야 했다. 기준선을 표에 박아 그 수작업을 없앤다.
    A("### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)")
    A("")
    _base = prior_log_end_baseline(root, day)
    _today_end, _today_src = (None, "오늘 SYSTEM 로그 없음")
    _tp = os.path.join(root, "logs", "%s_SYSTEM.log" % toks["ymd"])
    if os.path.exists(_tp):
        _today_end, _today_src = log_end_minute(_tp)
    if not _base:
        A("_직전 거래일 SYSTEM 로그가 없어 기준선을 만들 수 없다 (보관정책·신규 PC 확인)._")
    else:
        A("| 일자 | 종료시각 | 출처 |")
        A("|---|---|---|")
        for r in _base:
            A("| %s | %s | %s |" % (r["date"], m2hhmm(r["minute"]), r["source"]))
        _med = median_minute(_base)
        A("| **중앙값** | **%s** | 기준선 |" % m2hhmm(_med))
        A("| **오늘 %s** | **%s** | %s |" % (
            toks["ymd"],
            "—(미측정)" if _today_end is None else m2hhmm(_today_end),
            _today_src))
        A("")
        if _today_end is None:
            A("- ⚠ 오늘 종료시각 미측정 — **0으로 읽지 말 것**(계측 4원칙 ②).")
        else:
            _delta = _today_end - _med
            A("- 델타 **%+d분** (음수 = 기준선보다 이르게 끝났다)" % _delta)
            if phase in ("post", "all") and _delta <= -30:
                A("- 🔴 30분 이상 조기 종료 — §11 적신호 참조")
    A("")

    # ---- 8. dev_memory ----
    devmemory_section(root, cfg, day, L)

    # ---- 9. 산출물 JSON ----
    jsons = [e for e in files if is_jsonish(e)]
    A("## 9. 당일 JSON/JSONL 산출물")
    A("")
    if not jsons:
        A("(없음)")
        A("")
    for e in sorted(jsons, key=lambda x: x["rel"])[:12]:
        A("### `%s` — %s · %s" % (e["rel"], fmt_bytes(e["size"]),
                                  ts_kst(e["mtime"]).strftime("%m-%d %H:%M:%S")))
        A("```json")
        A(summarize_json(e["path"]))
        A("```")
        A("")

    # ---- 10. 정기점검 리포트 폴더 ----
    A("## 10. 정기점검 리포트 현황")
    A("")
    for rel in cfg["report_dirs"]:
        base = os.path.join(root, rel)
        if not os.path.isdir(base):
            A("- `%s` 없음" % rel)
            continue
        rep_rows = []
        for dirpath, dirnames, filenames in os.walk(base):
            for fn in filenames:
                full = os.path.join(dirpath, fn)
                try:
                    st = os.stat(full)
                except OSError:
                    continue
                rep_rows.append((st.st_mtime, os.path.relpath(full, root).replace(os.sep, "/"), st.st_size))
        rep_rows.sort(reverse=True)
        A("### `%s` — %d개 (최근 8개)" % (rel, len(rep_rows)))
        A("")
        A("| 파일 | 크기 | 최종 |")
        A("|---|---|---|")
        for mt, r, szb in rep_rows[:8]:
            A("| `%s` | %s | %s |" % (r, fmt_bytes(szb), ts_kst(mt).strftime("%m-%d %H:%M")))
        A("")

    # ---- 11. 자동 적신호 ----
    A("## 11. 자동 적신호 (출발점이지 결론이 아니다)")
    A("")
    flags = []
    if not files:
        flags.append("당일 날짜 토큰 파일 0개 — 프로그램이 안 돌았거나 탐색 경로가 틀렸다")
    if spath and rows:
        for r in rows:
            if "불일치" in r["verdict"] or "미발견" in r["verdict"]:
                flags.append("설정 불변식 `%s` = `%s` (기대 `%s`) — %s" % (
                    r["name"], r["actual"], r["expect"], truncate(r["why"], 90)))
    # 전수 표에는 `*_ENABLED` 전부를 싣되, 적신호로는 **차단 게이트**(이름에 BLOCK)만 올린다.
    # 기능 토글이 꺼진 것과 차단 장치가 꺼진 것은 무게가 다르다.
    only = re.compile(cfg.get("gate_flag_alert_pattern", "BLOCK"))
    for g in scan_gate_flags(root, cfg):
        if g["value"] == "False" and not g["documented"] and only.search(g["name"]):
            flags.append("차단 게이트 `%s` = False 인데 **근거 미기록** — "
                         "의도한 예외인지 확인하고 DECISION_LOG에 남길 것" % g["name"])
    for dg in digests:
        n_err = sum(v for k, v in dg.level_counts.items() if k in ("ERROR", "CRITICAL", "FATAL"))
        if n_err:
            flags.append("`%s`: ERROR 이상 %d건" % (dg.rel, n_err))
        if dg.records and dg.is_main_loop():
            have, total, missing = dg.minute_coverage()
            if total and have < total * 0.98:
                flags.append("`%s`: 매분 루프 커버리지 %d/%d분 (%.1f%%) — 루프가 빠진 구간이 있다" % (
                    dg.rel, have, total, 100.0 * have / total))
            # 연속 3분 이상 비면 매분 루프에서는 그 자체가 사건이다
            runs, s, prev = [], None, None
            for mnt in missing:
                if prev is not None and mnt == prev + 1:
                    prev = mnt
                    continue
                if s is not None and prev - s >= 2:
                    runs.append((s, prev))
                s = prev = mnt
            if s is not None and prev - s >= 2:
                runs.append((s, prev))
            for a, b in runs[:6]:
                flags.append("`%s`: %s~%s **연속 %d분 매분 루프 기록 없음**" % (
                    dg.rel, m2hhmm(a), m2hhmm(b), b - a + 1))
            for a, b, g in dg.gaps():
                if g >= cfg["gap_threshold_minutes"] * 2:
                    flags.append("`%s`: %s~%s %d분 로그 공백" % (dg.rel, m2hhmm(a), m2hhmm(b), g))
        for pat in ("0xC0000409", "STACK_BUFFER", "Traceback", "OOM", "MemoryError"):
            if pat in dg.quoted:
                flags.append("`%s`: **%s** 출현 %d건 — 크래시/메모리 계열" % (dg.rel, pat, len(dg.quoted[pat])))
    if phase in ("post", "all"):
        # [MW0601 471차 F-2] 판정 기준 교체: "강제청산 문자열이 있는가"가 아니라
        # **하트비트 또는 실집행 로그 중 하나가 있는가**로 본다.
        # 종전 기준은 "대상 없음(포지션 FLAT)"과 "코드 사망"을 구분하지 못해
        # 0812·0813·0814 3일 연속으로 적신호를 띄웠고 매번 사람이 원본으로 수동
        # 판별했다. 이제 15:10 이후 안전망 경로는 FLAT이어도 당일 1회
        # `[SchedForceExit] … 청산 대상 없음(정상) bar_pass=N회`를 남긴다.
        # ⚠ "FLAT"을 근거로 치던 종전 needle은 뺐다 — 포지션 상태 로그 어디에나
        #   등장하는 문자열이라 사실상 상시 통과였다(적신호가 죽어 있었다).
        hit_exec = any(("강제청산" in dg.quoted or "FORCED" in dg.quoted)
                       for dg in digests)
        hit_beat = any(("[SchedForceExit]" in dg.quoted or "[ForceExitPass]" in dg.quoted)
                       for dg in digests)
        if not (hit_exec or hit_beat):
            flags.append("장후인데 **15:10 청산 경로가 아무 흔적도 남기지 않았다** — "
                         "실집행(`강제청산`)도 하트비트(`[SchedForceExit]`)도 없다. "
                         "절대원칙 1 확인 필요 (471차 F-2 배포 이후라면 하트비트 부재 자체가 이상)")
    all_names = " ".join(e["name"] for e in files).lower()
    for em in cfg.get("expected_markers", []):
        if em["phase"] in phases and em["contains"].lower() not in all_names:
            flags.append("완료 마커 **`%s`** 없음 — %s" % (em["contains"], em["why"]))
    # --- 미륵이 특화 적신호 ---
    # 이 시스템은 ERROR 를 거의 안 남긴다(2026-08-12 하루 0건). 레벨만 보면 아무 일도
    # 없었던 것처럼 보이므로, 실제로 의미 있는 신호를 따로 잡는다.
    merged = {}
    banner_all = []
    for dg in digests:
        for k, v in dg.hits.items():
            merged.setdefault(k, []).extend(v)
        if dg.banner:
            banner_all.extend(dg.banner)

    for line in banner_all:
        m = re.search(r"판정\s*:\s*(\S+)", line)
        if m and m.group(1) not in ("OK", "NORMAL", "GOOD", "PASS"):
            flags.append("전략 상태 경보 **판정 = %s** — 배너 전문을 §5에서 확인하라" % m.group(1))
            break

    ex = merged.get("exit", [])
    en = merged.get("entry", [])
    bl = merged.get("block", [])
    sz = merged.get("sizer", [])
    if phase in ("post", "all"):
        if not en and not ex:
            top_bl = ""
            if bl:
                bd = {}
                for b in bl:
                    r = truncate(b.get("reason") or "?", 60)
                    bd[r] = bd.get(r, 0) + 1
                top_bl = " 최다 차단 사유: `%s`" % sorted(bd.items(), key=lambda kv: -kv[1])[0][0]
            flags.append("**진입 0건** — 차단 %d건.%s (진입0 딥다이브 절차를 따르라)" % (len(bl), top_bl))
        # [MW0601 482차 / F-4] 포지션 단위로 센다. 종전은 `체결청산` 레그만 세어
        # 2026-08-20에 "4건 100% 하드스톱"이라 찍었으나 실제는 하드스톱 4 ·
        # 손절1차 조기축소 2 · TP1 부분청산 1(레그 7 / 포지션 4)이었다.
        _pos_all, _ = assemble_positions(merged)
        _pos = [q for q in _pos_all if q["closed"]]
        if _pos:
            stops = sum(1 for q in _pos
                        if "스톱" in (q["exit_reason"] or "") or "손절" in (q["exit_reason"] or ""))
            if stops * 2 >= len(_pos):
                flags.append("포지션 %d건 중 최종청산이 하드스톱·손절 계열 **%d건(%.0f%%)** "
                             "— 손절 준수율 확인 필요 (레그 %d행)"
                             % (len(_pos), stops, 100.0 * stops / len(_pos),
                                sum(len(q["legs"]) for q in _pos)))
            _hidden = sum(1 for q in _pos if len(q["legs"]) > 1)
            if _hidden:
                flags.append("다레그 포지션 **%d건** — 레그 단위 집계는 손익·승률을 왜곡한다"
                             "(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라"
                             % _hidden)
    try:
        if sz and en:
            smax = max(int(s["qty"]) for s in sz if s.get("qty"))
            emax = max(int(e["qty"]) for e in en if e.get("qty"))
            if smax > emax:
                flags.append("사이저 최대 %d계약 → 실제 진입 최대 %d계약 — 게이트 배수에 눌림 "
                             "(sizing_inversion_watch 대상)" % (smax, emax))
    except (ValueError, KeyError, TypeError):
        pass

    # [MW0601 478차 후속 / FZ-6] 장중 로그 침묵 — 메인 이벤트 루프 동결 조기 감지.
    #
    # 2026-08-19 13:41:21에 메인(Qt) 스레드가 네이티브 스핀에 빠져 틱·분봉·QTimer가
    # 전부 멈췄다. 그런데 **프로세스는 살아 있고 ERROR도 0건**이라 레벨 집계로는
    # 아무 일도 없어 보인다(함정 ④). 유일하게 눈에 띄는 신호는 "로그가 그냥 끊긴다"
    # 는 것이었고, 그날 장중 점검(12:35 수집)은 동결 이전이라 잡지 못했다.
    # 동결 이후 아무 때나 수집기를 돌렸다면 즉시 드러났을 신호이므로 여기에 넣는다.
    #
    # 판정: 장중(pre/intra) 수집이고 오늘 로그일 때, 최신 로그 기록이 **5분 이상**
    # 낡았으면 적신호. 매분 파이프라인이 도는 한 SYSTEM/SIGNAL 로그는 60초 안에
    # 반드시 갱신되므로 5분은 충분한 여유다(정상 최장 블로킹 실측 9.5초의 30배).
    # ⚠ 이것은 **동결 확정이 아니라 확인 지시**다 — 장 시작 전·점심 저활동·수집 시점
    #   우연도 가능하다. 원본 로그 꼬리와 프로세스 CPU를 직접 볼 것.
    try:
        if phase in ("pre", "intra") and day == now_kst().date():
            _live = [e for e in files
                     if e["name"].lower().endswith(".log") and toks["ymd"] in e["name"]]
            if _live:
                _newest = max(ts_kst(e["mtime"]) for e in _live)
                _age_min = (now_kst() - _newest).total_seconds() / 60.0
                if _age_min >= 5.0:
                    flags.append(
                        "**장중 로그 침묵 %.0f분** (최신 기록 %s) — 매분 파이프라인이 돌면 "
                        "60초 안에 갱신된다. 메인 이벤트 루프 동결 가능성: 프로세스 CPU가 "
                        "1코어 100%%에 붙어 있고 `Responding=False`면 확정 "
                        "(2026-08-19 13:41 동일 사고). `logs/crash_fault.log` 꼬리에서 "
                        "메인 스레드 스택이 `exec_()` 단독인지 확인하라"
                        % (_age_min, _newest.strftime("%H:%M:%S"))
                    )
    except (KeyError, TypeError, ValueError):
        pass

    # [MW0601 480차 / G-2] 장후 조기종료 — FZ-6(장중 침묵)과 잡는 구간이 다르다.
    # FZ-6은 "지금 이 순간 로그가 멎었다"를, 이쪽은 "오늘 하루가 평소보다 일찍
    # 끝났다"를 본다. 08-19는 13:51에 끝났고(직전 12거래일은 전부 15:40대),
    # 장후 점검이 아니었으면 다음 거래일까지 몰랐을 사고다.
    try:
        if phase in ("post", "all"):
            _b = prior_log_end_baseline(root, day)
            _tp2 = os.path.join(root, "logs", "%s_SYSTEM.log" % toks["ymd"])
            _te = log_end_minute(_tp2)[0] if os.path.exists(_tp2) else None
            _md = median_minute(_b)
            if _b and _md is not None and _te is not None and _te - _md <= -30:
                flags.append(
                    "**SYSTEM 로그가 직전 %d거래일 중앙값(%s)보다 %d분 이르게 끝났다** "
                    "(오늘 %s) — 15:40 daily_close까지 살아 있었는지 확인하라. "
                    "프로세스 동결이면 15:10 강제청산·15:40 마감이 통째로 미실행이다 "
                    "(2026-08-19 13:41 사고)"
                    % (len(_b), m2hhmm(_md), _md - _te, m2hhmm(_te))
                )
            elif phase in ("post", "all") and _b and _te is None:
                flags.append("오늘 SYSTEM 로그 종료시각을 못 읽었다 — 파일 부재/손상 확인 "
                             "(미측정이지 정상이 아니다)")
    except (OSError, ValueError, TypeError):
        pass

    bms = merged.get("block_ms", [])
    over = []
    for b in bms:
        v = b.get("ms") or b.get("ms2")
        try:
            if v and int(v) >= 5000:
                over.append(int(v))
        except ValueError:
            pass
    if over:
        flags.append("메인 스레드 블로킹 5초 초과 **%d건** (최대 %dms) — "
                     "`CB_PIPE_PAUSE_MS=5_000` 기준 초과. CB⑤ 발동 여부 확인" % (len(over), max(over)))

    for dg in digests:
        for pat in ("[Brier] 과신", "degraded=ON", "level=CRITICAL", "축퇴",
                    "WeightCollapse", "ConstOut"):
            if pat in dg.quoted:
                flags.append("`%s`: **%s** %d건(표본)" % (dg.rel, pat, len(dg.quoted[pat])))

    if bad_tag:
        flags.append("PC명 태그 누락 커밋 %d건 — 멀티PC 컨벤션 위반" % len(bad_tag))
    if dirty:
        flags.append("미커밋 변경 %d건" % len(dirty))
    for rel in ("dev_memory/DECISION_LOG.md", "dev_memory/NEXT_TODO.md"):
        p = os.path.join(root, rel)
        if os.path.exists(p) and ts_kst(os.stat(p).st_mtime).date() != day and phase in ("post", "all"):
            flags.append("`%s` 가 오늘 갱신되지 않았다 — 세션 기록 의무 확인" % rel)

    for sf in cfg.get("state_files", []):
        p = os.path.join(root, sf["path"])
        if not os.path.exists(p):
            if phase in ("post", "all"):
                flags.append("상태 파일 `%s` 없음 — %s" % (sf["path"], sf["why"]))
        else:
            mt = ts_kst(os.stat(p).st_mtime)
            if mt.date() != day and phase in ("post", "all"):
                flags.append("상태 파일 `%s` 가 오늘 것이 아니다 (%s) — %s"
                             % (sf["path"], mt.strftime("%m-%d %H:%M"), sf["why"]))

    if flags:
        seen = set()
        i = 0
        for f in flags:
            if f in seen:
                continue
            seen.add(f)
            i += 1
            A("%d. %s" % (i, f))
    else:
        A("자동 탐지 적신호 없음. 그래도 §4~§6을 직접 읽고 판단할 것.")
    A("")
    A("---")
    A("")
    A("*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — "
      "예: `findstr /C:\"강제청산\" logs\\*%s*.log` (Windows) / `grep 강제청산 logs/*%s*.log`*"
      % (toks["ymd"], toks["ymd"]))
    return "\n".join(L)


# ------------------------------------------------------------------ 설정 로드
def load_config(root):
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    for rel in ("config/dailycheck_targets.json", "configs/dailycheck_targets.json"):
        p = os.path.join(root, rel)
        if os.path.exists(p):
            try:
                user = json.loads(read_text(p))
                cfg.update(user)
                eprint("[collect_evidence] 설정 덮어씀: %s" % p)
            except Exception as e:
                eprint("[collect_evidence] 설정 무시(파싱 실패): %s" % e)
            break
    return cfg


def _nonclobber_path(root, base_rel, ext):
    """[461차, F-6] `base_rel + ext`가 이미 있으면 시각 접미사로 비켜간다.

    반환은 `base_rel`과 같은 형식(리포 루트 기준 상대경로)이라 호출부의 절대경로
    변환 로직을 그대로 탄다. 덮어쓰기를 하지 않는 것이 목적이므로, 시각 접미사까지
    충돌하면(같은 분 재실행) `-2`, `-3` … 을 더 붙여 반드시 새 파일을 만든다.
    """
    if not os.path.exists(os.path.join(root, base_rel + ext)):
        return base_rel + ext
    stamp = now_kst().strftime("%H%M")
    cand = "%s_%s%s" % (base_rel, stamp, ext)
    n = 2
    while os.path.exists(os.path.join(root, cand)) and n < 100:
        cand = "%s_%s-%d%s" % (base_rel, stamp, n, ext)
        n += 1
    return cand


def main(argv=None):
    ap = argparse.ArgumentParser(description="미륵이 일일 점검 증거 수집기")
    ap.add_argument("--phase", choices=["pre", "intra", "post", "all"], default="post")
    ap.add_argument("--date", default=None, help="YYYY-MM-DD / YYYYMMDD (기본 오늘 KST)")
    ap.add_argument("--root", default=None, help="리포 루트 (기본 자동탐지)")
    ap.add_argument("--out", default=None, help="파일로 저장 (기본 stdout)")
    ap.add_argument("--out-auto", action="store_true",
                    help="evidence_<PC명>-<YYYYMMDD>_<국면>.md 로 자동 저장 "
                         "(두 PC가 서로 덮어쓰지 않는다. 셸 날짜 확장에 의존하지 않아 "
                         "PowerShell/bash 어디서든 같다. [461차] 같은 이름이 이미 있으면 "
                         "_<HHMM>을 붙여 회피 — 기존 파일을 덮지 않는다)")
    ap.add_argument("--discover", action="store_true",
                    help="파일 인벤토리만 출력 — 처음 한 번 돌려 경로를 확인한다")
    ap.add_argument("--max-log-mb", type=int, default=None, help="이보다 큰 로그는 건너뛴다")
    ap.add_argument("--pc", default=None,
                    help="PC 식별자를 강제한다 (예: MW0601). 우선순위는 "
                         "--pc > MIREUK_PC_ID 환경변수 > 호스트명 자동탐지. "
                         "리눅스 샌드박스처럼 호스트명에 MW####가 없는 환경에서 "
                         "evidence_UNKNOWN-… 이 생기는 것을 막는다")
    ap.add_argument("--prune-days", type=int, default=None,
                    help="[476차] 자기 PC의 증거 다이제스트를 N일치만 남긴다. "
                         "**기본 끔** — 인자를 줘야만 지운다. 1 미만이면 아무것도 "
                         "지우지 않는다. 보고서·다른 PC 파일은 대상이 아니다. "
                         "삭제 전 --prune-dry-run 으로 목록을 먼저 볼 것")
    ap.add_argument("--prune-dry-run", action="store_true",
                    help="--prune-days 대상만 인쇄하고 지우지 않는다")
    args = ap.parse_args(argv)

    set_pc_override(args.pc)

    start = args.root if args.root else os.path.dirname(os.path.abspath(__file__))
    root = find_repo_root(start)
    day = parse_date(args.date)
    cfg = load_config(root)
    if args.max_log_mb:
        cfg["max_log_bytes"] = args.max_log_mb * 1024 * 1024

    text = build(root, day, args.phase, cfg, discover_only=args.discover)

    out = args.out
    if args.out_auto and not out:
        pcid, _host = pc_id()
        base = os.path.join(cfg["evidence_dir"],
                            "evidence_%s-%s_%s" % (pcid, day.strftime("%Y%m%d"), args.phase))
        # [461차, F-6] 같은 국면이 하루 두 번 돌 수 있다 — 2026-08-13에 예약작업이
        # 13:13에 오발해 phase=post 로 돌았고, 16:22 진짜 장후 수집이 그 파일을 덮었다.
        # 리포트에는 덮어쓰기 방어가 있는데 다이제스트에는 없었다. 존재하면 시각
        # 접미사로 회피한다(같은 분 재실행까지 대비해 -2, -3 … 을 더 붙인다).
        out = _nonclobber_path(root, base, ".md")

    if out:
        outp = out if os.path.isabs(out) else os.path.join(root, out)
        d = os.path.dirname(outp)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        with io.open(outp, "w", encoding="utf-8") as f:
            f.write(text)
        eprint("[collect_evidence] 저장: %s (%s)" % (outp, fmt_bytes(len(text.encode("utf-8")))))
        print(outp)
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
        try:
            print(text)
        except UnicodeEncodeError:
            sys.stdout.write(text.encode("utf-8", "replace").decode("ascii", "replace"))

    # [MW0601 476차] 보관정리 — **기본 끔.** 인자를 줘야만 돈다.
    # 다이제스트를 먼저 쓰고 나서 돈다: 정리가 실패해도 오늘 증거는 이미 남는다.
    if args.prune_days is not None or args.prune_dry_run:
        pcid, _h = pc_id()
        removed, why = prune_evidence(
            root, cfg, pcid, args.prune_days, now_kst().date(),
            dry_run=args.prune_dry_run)
        eprint("[collect_evidence] 보관정리(%s · PC=%s): %s — %d건"
               % ("dry-run" if args.prune_dry_run else "apply", pcid, why, len(removed)))
        for p in removed:                     # 지운 것은 반드시 인쇄한다
            eprint("    - %s" % os.path.basename(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())

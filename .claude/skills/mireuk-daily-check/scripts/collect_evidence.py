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
    python scripts/collect_evidence.py --phase post --pc MW0602 --out-auto   # 호스트명이 그 PC의 것이 아닐 때

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
import sqlite3
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
        # [MW0602 470차 S3] 부분청산 — 이것을 안 세면 §5 손익이 배너와 어긋난다.
        # 2026-08-14 실측: §5 -82,547원 vs 배너 -93,450원, 차이 10,902원이 정확히 부분청산 3레그였다.
        "partial_exit": r"\[Position\] 체결부분청산 (?P<qty>\d+)계약 @ (?P<px>[\d.]+)\s*\|\s*잔여=(?P<rem>\d+)계약\s*\|\s*PnL=(?P<pt>[+-][\d.]+)pt\s*\((?P<won>[+-][\d,]+)원\)\s*\|\s*(?P<reason>.+?)\s*$",
        "block": r"\[차단\]\s*(?P<reason>.+?)\s*$",
        "sizer": r"\[Sizer\].*?신뢰도배수=(?P<conf_mult>[\d.]+)\s+레짐배수=(?P<regime_mult>[\d.]+)\s+안전배수=(?P<safe_mult>[\d.]+).*?→\s*(?P<qty>\d+)계약",
        # [MW0602 470차 S3] 사이즈 축소 사유 — **이미 존재하는 로그**다(main.py:8833).
        # 470차 장후 1차가 TRADE.log 만 보고 "사유 로그가 없다"고 오보했다. 실제로는 SIGNAL.log 에
        # 있었다. 수집기가 이 채널을 읽지 않은 것이 오보의 원인이므로 §5의 시야에 넣는다.
        "sizer_match": r"\[SizerMatch\] sizer=(?P<sizer_qty>\d+)계약 → actual=(?P<actual_qty>\d+)계약\s*\(gap=(?P<gap>\d+)\)\s*\|\s*(?P<mults>.+?)\s*$",
        # [MW0602 470차 S3/B3] 증거금 상한 — MAX_CONTRACTS 보다 먼저 구속하는 실효 상한.
        # [MW0602 485차 F-5] 신·구 양식 택일 — 477차 후속 G-2가 무조건 상태 샘플
        # `[MarginCap] state=OK|CAP|BLOCK LONG 산출=N 상한=M`(main.py:16266)을 신설했는데
        # 이 정규식이 구 축소 로그만 알아봐 §5(구만 계수)와 §12(신만 계수)가 같은
        # 다이제스트 안에서 어긋났다(0821 리포트 1-11: §5 `3` vs §12 `27`).
        # ⚠ CAP 발생 시 신·구 두 줄이 **같은 사건에 대해 함께** 찍힌다 — 소비부는
        #   state 유무로 나눠 세야 하며 매치 수를 그대로 합산하면 CAP이 중복 계수된다.
        "margin_cap": r"\[MarginCap\]\s*(?:state=(?P<state>OK|CAP|BLOCK)\s+)?(?P<dir>\w+)\s+산출=(?P<calc>\d+)(?:계약\s*→\s*증거금상한=(?P<cap>\d+)계약으로 축소|\s+상한=(?P<cap_new>\d+))",
        # [MW0602 470차 B2] 시간대 존 전환 — 진입 가능 시간 예산을 재구성한다.
        # 추가 계측이 필요 없다. 이 로그를 구간으로 접으면 존별 체류 분수가 그대로 나온다.
        "time_zone": r"\[TimeRouter\] 시간대 전환 → (?P<zone>[A-Z_]+)\s*[:：]\s*(?P<desc>.+?)\s*$",
        "cb": r"\[CB\]\s*(?P<msg>.+?)\s*$",
        "block_ms": r"메인 스레드 블로킹.*?간격 (?P<ms>\d+)ms|간격 (?P<ms2>\d+)ms — 메인 스레드 블로킹",
        # [MW0602 476차 F-7] 일일 마감 줄 — §5 손익 검산의 2차 원천.
        # `오늘 PnL` 이 든 전략경보 배너는 뜨지 않는 날이 있는데(0819 실측: 배너 자체
        # 미출력 → 검산 축이 매일 비었다), 이 줄은 15:40 daily_close 마다 무조건 찍힌다.
        "daily_close": r"일일 마감\s*\|\s*승=(?P<w>\d+)\s*패=(?P<l>\d+)\s*PnL=(?P<won>[+-]?[\d,]+)원",
    },
    "banner_start": "전략 상태 경보",
    "banner_lines": 8,
    # config/settings.py 에서 값을 확인할 상수 — CLAUDE.md 절대원칙·한시예외 대응
    "invariants": [
        {"name": "CB_CONSEC_STOP_LIMIT", "expect": "9999",
         # [MW0602 491차 F-1] 489차 D2가 기한을 **날짜 → 사건**으로 바꿨는데 이 사본만
         # 남아 죽은 날짜를 매일 인쇄했다(정본 `invariants.md`는 489차에 갱신됨).
         # ⚠ 값(`9999`)은 손대지 않는다 — 이 fix는 기한 문구만 고친다.
         "why": "모의투자 한정 예외(CB② 사실상 비활성). 실투 전환 전 2~3 복원 필수. "
                "🔴 [489차 D2] 기한은 날짜가 아니라 **사건** — 복원 = 전환기준 ⑧ 해제와 "
                "동일 커밋. 종전 '2026-08-29'는 효력 종료(재인용 금지). "
                "그 사이 캠페인 [56] cb2_restore_shadow가 매주 반사실 재계산"},
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
         "why": "CB③ 임계(0.35→0.28 완화). CLAUDE.md 절대원칙 §2 본문 '35%' 옆에 실값 병기 완료(468차) — 문서-코드 괴리 해소됨"},
        {"name": "CB_ACC_RESTRICTED_MIN", "expect": "0.30",
         "why": "WATCH→RESTRICTED 경계. 30m 구조적 성능(0.3052)과 거의 같아 CB③-P4 비활성의 직접 원인"},
        {"name": "CB_ACCURACY_MIN_30M_STRICT", "expect": "0.42",
         "why": "과신 연속 시 강화 임계 (0.50→0.42 완화)"},
        {"name": "TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED", "expect": "False",
         "why": "극단 스프레드(20틱) block — 311차 섀도우 검증 대기. 근거·활성화 조건은 config/settings.py:4770-4781"},
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
        {"name": "MODEL_LABEL_STATE_UNLOCK_ENABLED", "expect": "True",
         "why": "468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지"},
        {"name": "PRE_RETRAIN_DONE_BY_EOD_ENABLED", "expect": "True",
         "why": "468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치"},
        {"name": "ZONE_ENTRY_BAN_ENFORCE", "expect": "False",
         "why": "462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지"},
        {"name": "ZONE_ENTRY_BAN_SHADOW_ENABLED", "expect": "True",
         "why": "462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다"},
        {"name": "PIPE_LATENCY_EXCLUDE_MODEL_SWAP", "expect": "True",
         "why": "462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치)"},
    ],
    # 차단 게이트 자동 인벤토리 — 이름에 이 패턴이 있고 값이 True/False 인 상수
    "gate_flag_pattern": "BLOCK|ENABLED|DISABLE",
    # CLAUDE.md·DECISION_LOG·settings.py 주석에 근거가 기록된 "일부러 꺼둔" 게이트.
    # 여기 없는 False 게이트는 §10에서 적신호로 올린다 — 조용히 잠든 게이트를 막기 위함.
    # ⚠ config/dailycheck_targets.json 의 같은 키가 이 목록을 **통째로 대체**한다
    #   (load_config 는 cfg.update(user)). 한쪽만 고치면 JSON 없는 PC에서만 오탐이 난다.
    "documented_disabled_flags": [
        "CB3_P4_GRADE_BLOCK_ENABLED",           # CLAUDE.md 절대원칙 §2 한시예외 (297차)
        "FP_CRITICAL_GRADE_BLOCK_ENABLED",      # CLAUDE.md 절대원칙 §2 한시예외 (303·371차)
        "HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY",   # 설계 선택 — 수동진입은 막지 않는다
        "TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED",  # config/settings.py:4770-4781 (311차)
    ],
    # ── [MW0602 468차 G-2] 고착 지표 자동 탐지 ────────────────────────────────
    # 미륵이가 **반복적으로 밟아온 실패 형태**: 안전장치·계측이 한쪽 값에 붙박여
    # 사실상 죽어 있는데 아무도 모른다. FP-CRITICAL 상시 CRITICAL(303차),
    # CB③-P4 상시 RESTRICTED(292차), PSI 메가빈(371차), `CORE안전=⚠️` 6거래일
    # 100%(468차) — 매번 사람이 뒤늦게 발견했다.
    #
    # 여기서는 **두 가지**를 잡는다:
    #   ① 한 값이 관측의 100%  → 고착(발동하지 않는 안전장치 / 죽은 판정)
    #   ② 표본 0             → 아예 기록이 끊겼거나 로그 문구가 바뀌어 패턴이 안 맞음.
    #      **이것도 죽은 지표다.** 조용히 넘어가면 "경고가 없다 = 정상"으로 읽힌다.
    "stuck_indicators": {
        "lookback_days": 10,      # 최근 몇 거래일치 로그를 볼 것인가
        "min_days": 3,            # 이보다 적은 날에서만 관측되면 판정 보류
        "min_samples": 20,        # 이보다 표본이 적으면 판정 보류
        "max_file_mb": 8,         # 이보다 큰 파일은 건너뛴다(HOGA 등)
        #
        # ⚠ **조건부 로그를 넣지 말 것.** 임계를 넘을 때만 찍는 줄(예:
        #   `[RegimeFingerprint] PSI=… CRITICAL`은 PSI>0.20에서만 출력)을 표본으로 삼으면
        #   100% 고착이 **구조적으로 보장**된다 — 지표가 죽은 게 아니라 표본이 편향된 것이다.
        #   실제로 이 절을 만들면서 그 패턴을 넣었다가 "PSI 100% CRITICAL 고착"이라는
        #   가짜 적신호를 만들어 봤다(2026-08-05 이후엔 CLEAR라 아예 안 찍힌다).
        #   **매 주기 무조건 찍히는 상태 샘플만** 넣는다.
        #
        # [MW0602 475차 후속 / 장후 G-3 = 장전 G-1] **분기편향 자동 탐지.**
        #
        # 고착·무기록 말고 세 번째 죽음이 있다 — 지표가 **특정 분기에서만 돈다.**
        # 2026-08-18 `ConfFloor` 가 그것이었다: 80샘플이 전부 `ZONE_BLACKOUT` 이고
        # 그 80이 **진입 금지 존 체류 80분과 정확히 일치**했다(진입 허용 290분 0건).
        # 즉 "매분 무조건 상태 샘플"이라 주장하는 계측이 실제로는 한쪽 분기에서만 찍혔다.
        # 그것을 발견한 방법이 사람이 우연히 한 산술 일치였으므로 계측으로 바꾼다.
        #
        # ⚠ **옵트인이다**(`sample_axis: "minute"`). 화이트리스트 방식으로 만들면
        #   설계상 매분이 아닌 지표가 즉시 오탐이 된다 — 0818 실측 비율:
        #     CB_state 1.01(진짜 매분)  ConfFloor 0.22(편향)
        #     degraded 0.07 · CORE준비도 0.12  ← 둘 다 설계상 매분 아님(오탐이 될 뻔했다)
        # ⚠ `n == 0` 은 분기편향으로 세지 않는다 — 그건 기존 `무기록`이며, 배포 첫날
        #   이전 날짜가 전부 여기 걸린다(0814 ConfFloor 0건은 미배포가 원인이다).
        #
        # name: {re: 값 캡처 정규식(그룹 v), files: 파일명 부분일치, why: 왜 보는가,
        #        benign: 이 값 하나로 100%인 것이 정상인 경우(경고 대신 정보로 표시),
        #        min_samples/min_days: 전역 기준 덮어쓰기(선택),
        #        sample_axis: "minute" 이면 "그 지표가 사는 로그가 살아 있던 분" 대비
        #                     관측률을 재고 branch_ratio_min 미만이면 `분기편향`.
        #                     "ensemble_minute" 이면 분모를 `[Ensemble] dir=` 출현 분으로
        #                     좁힌다(476차 F-8 — 앙상블이 계산된 분에만 사는 지표용.
        #                     ConfFloor 를 "minute" 축으로 재면 포지션 보유 등으로 앙상블을
        #                     건너뛴 분이 분모에 들어가 관측률이 구조적으로 과소평가된다:
        #                     0819 실측 원시 0.88 vs 앙상블 축 1.00),
        #        value_map: [[정규식, 라벨], …] — 캡처값을 라벨로 정규화(476차 G-6.
        #                   예: bar_pass 1,2,3… 을 "≥1(생존)" 하나로 접어 고착 오탐 방지),
        #        measured_since: "YYYY-MM-DD" — **계측 배포일 마커**(477차 후속 G-1).
        #                   그 이전 일자는 분모·분자·무기록 판정에서 제외한다.
        #                   배포 전 날짜는 **미측정**이지 "관측률 낮음"이 아니다(계측 4원칙 ②)
        #                   — 0820 실측: ConfFloor 합산 0.72 는 08-18(배포 전)이 창에 섞인
        #                   값이었고 당일값은 1.00 이었다. ⚠ 낡으면 반대 방향으로 속인다 —
        #                   26주 WFA 목록(invariants.md §5)에서 갱신을 강제한다}
        # 관측률이 이 값 미만이면 분기편향. 0.5 는 "절반의 분에서 안 찍혔다"는 뜻이라
        # 주기 로그(2분·5분 간격)와 진짜 편향을 가르는 자리다. 0818 실측 0.22 는 통과 못 하고
        # 진짜 매분 샘플러 CB_state 1.01 은 여유 있게 통과한다.
        "branch_ratio_min": 0.5,
        # 분모가 이보다 작은 날은 관측률을 재지 않는다(반나절만 돈 날에 판정하지 않는다).
        "branch_min_expected": 60,
        "patterns": {
            "CORE안전": {
                "re": r"CORE안전=(?P<v>\S+)",
                "files": ["_LEARNING"],
                "why": "SHAP CORE 감시. 468차 F-3 이전 6거래일 100% ⚠️ 고착 실적",
            },
            "degraded": {
                "re": r"\[Health\][^|]*degraded=(?P<v>\w+)",
                "files": ["_HEALTH"],
                "benign": ["OFF"],
                "why": "시스템 헬스 강등. OFF 고착은 정상(사고 없음)",
            },
            "CB_state": {
                "re": r"\[DBG-CB\] state=(?P<v>\w+)",
                "files": ["_DEBUG"],
                "benign": ["NORMAL"],
                "sample_axis": "minute",   # 0818 실측 관측률 1.01 — 진짜 매분 샘플러
                "why": "CB 전체 상태(매분 샘플). NORMAL 고착은 정상 — 단 Phase 5 조건 ②"
                       "(CB 실발동 확인)가 여전히 미충족이라는 뜻이기도 하다",
            },
            "GuardFair_유효": {
                "re": r"\[GuardFair\][^\n]*\|\s*(?P<v>무효|ok)\s*\(",
                "files": ["retrain_eod"],
                "why": "457차 fair_valid. 무효 100%면 GuardFair 비교가 죽어 있다",
            },
            # ── [MW0602 494차 F-8] 그 무효가 **얼마나** 어긋났는가 ────────────
            # 위 `GuardFair_유효` 는 8거래일 내내 `무효` 100% 였다(0825 이상점 1-11).
            # 그런데 그 값 하나로는 **표본 문제인지 산술적 불가인지** 구분되지 않는다 —
            # 그래서 "20거래일 누적 후 판정" 이라는 계획이 세워졌고, 그 계획은
            # 표본을 더 모아도 닫히지 않는다(`holdout_bars=1850`≈5거래일인데 현행
            # 모델은 매일 재학습된다 → `train_end < holdout_start` 가 참이 될 수 없다).
            # `gap_bars` 는 홀드아웃 중 현행이 **이미 학습한 봉 수**다.
            # 성립에 필요한 최대 홀드아웃 = `holdout_bars - gap_bars`.
            #
            # ⚠ **판정 무영향(섀도)** — 캠페인 [23] 합격선을 건드리지 않는다.
            # 🔴 `benign` 아님. `1850` 100% 고착이면 홀드아웃 전체가 오염된 것이고,
            #    그 값이 2026-08-28 주간회의 안건 ⑦(홀드아웃을 줄일 것인가 vs
            #    `fair_valid` 필터를 폐기할 것인가)의 직접 입력이다.
            # ⚠ 지금 이 값으로 `holdout_bars` 를 고르지 말 것 — 관측 후 기준 수립은
            #    313차 ④ 위반이다. 2주치를 모은 뒤 주간회의에서 정한다.
            "GuardFair_gap_bars": {
                "re": r"\[GuardFair\][^\n]*gap_bars=(?P<v>\d+|\?)",
                "files": ["retrain_eod"],
                "min_samples": 6,   # EOD 6호라이즌 = 하루 6줄. 전역 20이면 4일 걸린다
                "measured_since": "2026-08-26",   # 494차 F-8 배포 다음 EOD
                "why": "GuardFair 홀드아웃 중 현행이 이미 학습한 봉 수(494차 F-8). "
                       "`fair_valid` 는 '성립했는가'만 말하고 '얼마나 어긋났는가'를 "
                       "말하지 않는다. 성립에 필요한 최대 홀드아웃 = 1850 - 이 값. "
                       "🔴 benign 아님 — 1850 고착이면 홀드아웃 전체 오염. "
                       "⚠ 판정 무영향(섀도), 주간회의 2026-08-28 안건 ⑦의 입력",
            },
            "전략판정": {
                "re": r"판정\s*:\s*(?P<v>\S+)",
                # [MW0602 475차 후속] 원천을 로그 → **일일 전략 리포트 파일**로 교체.
                # 로그 배너(`_WARN`/`_SYSTEM`)는 main.py 가
                # `if _action in (ROLLBACK_REVIEW, REPLACE_CANDIDATE)` 일 때만 찍는
                # **조건부 로그**라, 표본이 UNDERPERFORM 으로 100% 고착되는 것이
                # 구조적으로 보장된다 — 바로 이 절 머리말이 금지한 패턴이다.
                # 2026-08-18 실측: 로그 원천 `UNDERPERFORM×7`(🔴 고착) vs 그날 실제 판정
                # `INSUFFICIENT`. 게다가 470차 R1(seed 기준선 차단) 이후 verdict 가
                # 영구 INSUFFICIENT 라 이 배너는 **앞으로 영영 안 찍힌다** → 방치하면
                # 고착이 아니라 `무기록` 으로 굳는다.
                # `data/daily_reports/strategy_report_YYYYMMDD_*.txt` 는 EOD 마다
                # **무조건** 생성되고 날짜 토큰도 있어 이 스캐너가 이미 훑고 있다.
                "files": ["strategy_report"],
                "min_samples": 5,   # 리포트는 하루 1회라 전역 20건 기준이면 영영 판정 불가
                "why": "일일 전략 리포트의 판정(매 EOD 무조건 생성). 한 값 고착이면 "
                       "판정식이 무의미해진 것. ⚠ 로그 배너는 경보일 때만 나가는 "
                       "조건부라 원천으로 쓰지 말 것(475차 실측)",
            },
            # ── [MW0602 470차] 470차 L2·B4 가 신설한 무조건 상태 샘플 2종 ──
            # 둘 다 "엣지 트리거라 마지막 상태가 열린 채 끝나던" 지표를 상태 샘플로 바꾼 것이다.
            # 배포 이전 날짜를 조회하면 `무기록`으로 뜨는 것이 정상 — 그때는 로그가 없었다.
            "ConfFloor": {
                "re": r"\[ConfFloorGuard\] state=(?P<v>\w+)",
                "files": ["_SIGNAL"],
                "benign": ["OK"],
                # 470차 L2 가 "매분 무조건"을 표방하며 신설했다 — 그 주장을 매일 검증한다.
                # [476차 F-8] 실제 호출 지점은 EnsembleDecision.compute() 내부라
                # **앙상블이 계산된 분에만** 남는다(0819 실측: [Ensemble] 출현 306분과
                # 교집합 306 · 차집합 0). 분모를 앙상블 축으로 좁혀 오탐을 없앤다.
                "sample_axis": "ensemble_minute",
                # [477차 후속 G-1] 08-18 은 F-8(상시 상태 샘플) 배포 전 = 미측정.
                "measured_since": "2026-08-19",
                "why": "자동진입 하한 도달 가능 여부(매분 샘플, 470차 L2). OK 고착은 정상. "
                       "BLOCKED 고착이면 어떤 신호도 자동진입 하한을 못 넘는 상태가 "
                       "종일 지속된 것이다 — 2026-08-11 오전 88신호 전부 grade=X 가 그 사례",
            },
            "CORE준비도": {
                "re": r"\[CORE준비도\][^\n]*축퇴 (?P<v>\d+)/\d+",
                "files": ["_LEARNING", "_SYSTEM", "_SIGNAL"],
                "benign": ["0"],
                "measured_since": "2026-08-14",   # 470차 B4 배포일 (477차 후속 G-1)
                "why": "장전/장중 스케일러 refit 시 CORE 축퇴 개수(470차 B4). 0 고착이 정상. "
                       "0이 아닌 값에 고착하면 절대원칙 ③의 CORE가 상시 무력화된 것 — "
                       "2026-08-14 장전 above_vwap 6호라이즌 identity 강제가 그 사례. "
                       "⚠ 섀도 계측이다. 차단으로 승격하려면 20거래일 축적 후 "
                       "'축퇴일의 09:00~09:30 정확도'를 일자단위로 비교할 것(317차 교훈)",
            },
            # ── [MW0602 476차 G-2 / 488차 계획 D] CORE 축퇴 **피처명** 축 ──
            # 위 `CORE준비도` 는 **개수만** 센다(`1`×35). 어느 피처가 축퇴했는지는
            # 값에 안 실려서, 470차가 사전등록한 20거래일 판정 때 로그를 **다시 파싱**해야
            # 한다. 개수 축을 대체하지 않고 **병렬로** 둔다 — 개수는 심각도, 피처명은 원인이라
            # 묻는 것이 다르고, 개수 축의 시계열(measured_since 2026-08-14)을 끊지 않기 위해서다.
            # 로그 원본: `model/multi_horizon_model.py:1281` (축퇴 시 WARNING) /
            #            `:1286` (축퇴 0 이어도 INFO 1줄 — 조건부 로그가 아니다).
            "CORE축퇴_피처": {
                "re": r"\[CORE준비도\][^\n]*축퇴 \d+/\d+ — (?P<v>[^|\n]+)",
                "files": ["_LEARNING", "_SYSTEM", "_SIGNAL"],
                # 축퇴 0 줄의 꼬리는 "CORE 스케일 정상" 이다 — `없음` 으로 정규화해
                # 피처명 값들과 같은 분포에 놓는다. 축퇴 줄은 `above_vwap×6hz` 형태.
                "value_map": [[r"CORE 스케일 정상\s*", "없음"]],
                "benign": ["없음"],
                # 축 신설일(08-24)이 아니라 **로그 배포일**이다 — 같은 표의 개수 축
                # `CORE준비도` 와 동일 기준(470차 B4). 이 축은 이미 있는 로그를 다르게
                # 읽을 뿐이라 소급 관측이 유효하다. 축 신설일로 잡으면 창이 비어
                # 08-14~08-21 실측(`cvd_divergence×6hz` 등)을 통째로 못 본다.
                "measured_since": "2026-08-14",
                "why": "축퇴한 CORE 피처의 **이름 집합**(476차 G-2). `없음` 고착이 정상. "
                       "특정 피처명에 고착하면 그 피처가 상시 identity 강제 상태다 — "
                       "2026-08-14 `above_vwap×6hz` 가 그 사례이며 그때는 이름을 알려고 "
                       "로그를 재파싱해야 했다. ⚠ 개수 축 `CORE준비도` 와 병렬(대체 아님). "
                       "⚠ 섀도 관측 축 추가일 뿐 **차단 승격이 아니다**",
            },
            # ── [MW0602 494차 F-1] CORE 축퇴의 **원인 축** ────────────────────
            # 위 두 축은 *몇 개가*(`CORE준비도`) *무엇이*(`CORE축퇴_피처`) 축퇴했는지를
            # 센다. 세 번째 질문 — **왜** — 이 남아 있었다. `raw_std≈0` 은
            #   (a) 그 구간에 그 피처가 실제로 거의 안 움직였다 (정상)
            #   (b) 계산부가 유효 입력을 못 받아 상수를 낸다 (결함)
            # 둘 중 하나인데 로그가 둘을 구분하지 못했다(0825 이상점 1-1).
            # 494차 F-1 이 `[ScalerRefresh]` 축퇴 줄 **꼬리에** frac_zero 등을 병기한다.
            #
            # ⚠ **이 축은 사건 속성이지 상태 샘플이 아니다** — 축퇴가 일어난 줄에만 있다.
            #   그래서 이 절 머리말의 "조건부 로그 금지"에 걸리는 것처럼 보이지만
            #   성격이 다르다: 금지 대상은 *한쪽 분기만 기록되는 임계 초과 로그*(PSI
            #   CRITICAL 처럼 100% 고착이 **구조적으로 보장**되는 것)다. 여기서는
            #   같은 줄에서 세 버킷이 모두 나올 수 있으므로 고착은 구조가 아니라 **사실**이다.
            #   분모(축퇴가 몇 번 있었나)는 `CORE준비도` 가 이미 잡는다 — 병렬로 읽을 것.
            #
            # 판정(사전등록, 313차 ④): `≥0.90(점질량)` 3거래일 연속 → (b) 결함 쪽으로
            # 기울어 CORE 피처 계산부 조사를 안건화. `<0.50` 인데 축퇴면 (a) 정상.
            "CORE축퇴_원인축": {
                "re": r"\[ScalerRefresh\][^\n]*frac_zero=(?P<v>[0-9.?]+)",
                "files": ["_LEARNING", "_SYSTEM", "_SIGNAL"],
                # 연속값을 그대로 세면 전부 "변동"이 되어 아무것도 못 본다 — 버킷으로 접는다.
                "value_map": [
                    [r"1\.000|0\.9\d+", "≥0.90(점질량)"],
                    [r"0\.[5-8]\d+",    "0.50~0.89"],
                    [r"0\.[0-4]\d+",    "<0.50(진짜 저변동)"],
                    [r"\?",             "요약실패"],
                ],
                "measured_since": "2026-08-26",   # 494차 F-1 배포 다음 거래일
                "why": "CORE 축퇴가 (a)진짜 저변동인가 (b)입력 부재인가(494차 F-1). "
                       "`≥0.90(점질량)` 고착이면 (b) 쪽 — 0825 `ofi_norm` 이 §12 "
                       "`CORE축퇴_피처` 210표본 중 137건(65.2%)을 차지하던 만성 상태의 "
                       "원인을 가른다. 🔴 benign 아님. ⚠ 사건 속성 축이다 — 분모는 "
                       "`CORE준비도`(무조건 상태 샘플)가 잡는다. 병렬로 읽을 것",
            },
            # ── [MW0602 476차 G-6] 15:10 강제청산 1차 경로 하트비트 ──
            # 471차 F-2 가 배선한 `[SchedForceExit] … bar_pass=N회` 는 15:11 에 매일
            # **무조건** 1줄 찍힌다(FLAT 이어도) — §5 규약(조건부 로그 금지) 준수.
            # 그런데 어디에도 집계되지 않아 "1차 경로가 살아 있었는가"를 알려면 매번
            # 원본을 grep 해야 했다. 470차 C2'가 `신뢰도배수`를 benign 으로 등록한 것과
            # 같은 취지 — *목적은 발견이 아니라 규명된 것도 계속 보이게 두는 것*이다.
            "강제청산_경로": {
                "re": r"\[SchedForceExit\][^\n]*bar_pass=(?P<v>\d+)회",
                "files": ["_SYSTEM"],
                # bar_pass 원값(1,2,3…)은 관심사가 아니다 — 15:10 창을 1차 경로(STEP 8)가
                # **지나갔는가(≥1)** 만 본다. 원값 그대로 세면 "2 100%"가 🔴 고착으로
                # 오탐된다. 0 = 471차 F-1 복구가 다시 죽은 것(P-9).
                "value_map": [[r"0", "0(경로사망)"], [r"[1-9]\d*", "≥1(생존)"]],
                "benign": ["≥1(생존)"],
                "min_samples": 3,   # 하루 1줄이라 전역 20건 기준이면 영영 판정 불가
                "measured_since": "2026-08-14",   # 471차 F-2 배포일 (477차 후속 G-1)
                "why": "15:10 강제청산 1차 경로 생존(471차 F-2 하트비트, 매일 15:11 무조건 1줄). "
                       "'≥1(생존)' 고착이 정상. '0(경로사망)' 출현 = 1차 경로 재사망. "
                       "F-1R 리허설(실집행 확인) 전까지의 공백을 매일 관측으로 메운다(G-6)",
            },
            # ── [MW0602 477차 후속 G-2] 증거금 상한 상태 — 470차 C2'가 예고한 그 항목 ──
            # 종전 `[MarginCap] … 축소` 는 **축소가 일어날 때만** 찍히는 조건부 로그라
            # §5 규약 위반이었고, 그 조건부성이 0820 이상점 1-1(entry_qty 오귀속)을 낳았다.
            # main.py `_ts_margin_capped_qty()` 가 조회 성공 매 사이클에
            # `[MarginCap] state=OK|CAP|BLOCK 산출=N 상한=M` 상태 샘플을 남긴다(무조건).
            # ⚠ 사이클 자체는 진입 후보 분(auto_entry & grade≠X)에만 돈다 — 매분 샘플러가
            #   아니므로 sample_axis 를 켜지 말 것(즉시 오탐이 된다).
            # 전환기준 ⑧의 직접 입력 — "증거금이 언제부터 binding constraint 였나"가
            # 부재가 아니라 값으로 남는다(470차 사슬의 첫 칸).
            "MarginCap_state": {
                "re": r"\[MarginCap\] state=(?P<v>\w+)",
                "files": ["_TRADE"],
                "benign": ["OK"],
                "measured_since": "2026-08-21",   # 배포 다음 거래일부터 로그 존재
                "why": "증거금 상한 상태(477차 후속 G-2, 조회 성공 사이클마다 무조건 1줄). "
                       "OK 고착이 정상. CAP 고착이면 증거금이 사이저보다 항상 먼저 자르는 "
                       "상태(470차 실측: 목표자본 5천만 > 실잔고 2.9천만에서 5/5 축소) — "
                       "⑧ 재설계 논의의 직접 입력. BLOCK 출현 = 증거금 부족 진입 차단",
            },
            # ── [MW0602 492차 F-7 ⑤] 학습률 조절기 2축 ─────────────────────
            # 0824 1-13: `DRIFT_UP` 이 최근 9일 중 6일 찍혔는데 alpha 는 열흘째
            # `0.01000`(=ALPHA_MAX) 로 붙박여 있었다. **매일 대응한 기록만 남고
            # 아무것도 바뀌지 않은** 형태다 — §12 가 정확히 잡아야 할 것이다.
            # 🔴 `sgd_alpha` 는 **benign 이 아니다.** 상한 고착이 정상이라는 판단이
            #    아직 없다(있었다면 그것부터 사전등록됐어야 한다).
            # ⚠ 임계(`ALPHA_MAX` 등)는 무변경 — 이 두 행은 관측일 뿐이다.
            "sgd_alpha": {
                "re": r"\[DriftAdjuster\] acc=.*?→ alpha=(?P<v>[0-9.]+)",
                "files": ["_learning"],
                "min_samples": 3,   # EOD 1줄/일 — 전역 20건이면 영영 판정 불가
                "why": "SGD 학습률 실값(drift_adjuster). `0.01000` 단일값 고착 = "
                       "ALPHA_MAX 포화 — 상향 지시가 무연산이라는 뜻(0824 1-13). "
                       "🔴 benign 아님. 하향 경로(RECOVERY_THRESHOLD=0.58)는 최근 "
                       "10일 acc 최댓값 0.4048 이라 **도달 불가**다",
            },
            "drift_action": {
                "re": r"\[DriftAdjuster\] acc=.*?→ alpha=[0-9.]+ \((?P<v>[A-Z_]+)\)",
                "files": ["_learning"],
                "min_samples": 3,
                "measured_since": "2026-08-25",   # 492차 F-7 액션 분리 배포 다음 거래일
                "why": "학습률 조절기 판정 액션. 492차 F-7 이 `DRIFT_UP`(진짜 상향)과 "
                       "`DRIFT_UP_SATURATED`(상한 포화·무연산)를 갈랐다 — 배포 전 행은 "
                       "둘이 섞여 있어 **미측정**으로 뺀다(계측 4원칙 ②). "
                       "`DRIFT_UP_SATURATED` 100% 고착 = 조절기가 손잡이를 잃은 상태",
            },
        },
    },
    # ── [MW0602 475차 후속 / 장후 G-2] DB 원천 지표 ────────────────────────────
    # 로그에 없는 상태를 §12 시야에 넣는다. 판정 규칙은 로그 지표와 같다(stuck_verdict).
    # ⚠ `ensemble_decisions` 는 `predictions.db` 에 있다 — 같은 이름의
    #   `data/db/ensemble_decisions.db` 는 0바이트 유령 파일이다.
    "db_indicators": {
        "lookback_days": 14,
        "min_samples": 20,
        "min_days": 3,
        "sources": {
            "binding_gate": {
                "db": "data/db/predictions.db",
                "sql": "select substr(ts,1,10) d, sizing_trace from ensemble_decisions "
                       " where ts >= ? and ts <= ? || ' 23:59:59' and sizing_trace is not null",
                "json_key": "binding_gate",
                "measured_since": "2026-08-14",   # 471차 후속6 sizing_trace 배포일 (G-1)
                "why": "무엇이 실제로 사이즈를 구속했는가(471차 후속6 sizing_trace). "
                       "한 게이트 100% 고착이면 316차 HurstGate(63% 차단)와 같은 상태다. "
                       "⚠ 2026-08-14 이후 행에만 있다 — 그 이전은 미측정이지 압력 0이 아니다. "
                       "🔴 [491차 F-5] `margin` 출현은 **증거금이 구속한 것** — ⑧ 해제 "
                       "논의의 직접 입력이다. 그 이전 행의 품질 게이트 이름 일부는 "
                       "오귀속이며 **소급 재라벨하지 않았다**(계측 4원칙 ②)",
            },
        },
    },
    # ── [MW0602 485차 G-1 / 488차 계획 D] 스냅샷 정체 (snapshot identity) ──────
    # §12 가 못 잡는 **네 번째 형태**다. 정리하면 죽음의 형태는 넷이다:
    #   ① 고착(§12)        — 값이 한쪽에 붙박였다
    #   ② 무기록(§12)      — 로그 문구가 바뀌어 정규식이 아무것도 못 잡는다
    #   ③ 분기편향(475 G-1)— 계측이 한쪽 분기에서만 돈다
    #   ④ **스냅샷 정체**  — 로그는 매일 정상 출력되고 값도 "정상"인데 **어제와 똑같다**
    # ④의 실사례: `data/ensemble_calibrator.pkl` 이 2026-08-11~08-21 **7거래일** 갱신되지
    # 않았다(0821 이상점 1-1). 매 기동 `[Calibration] … 복원 완료 n=…` 은 정상적으로 찍혔고
    # n 값도 정상 범위였다 — **다만 매일 같은 수였다.** ①~③ 어디에도 안 걸린다.
    #
    # 여러 필드를 튜플로 묶어 **일자 간 동일성**을 보고, 연속 동일일수 ≥ N 이면 정체로 본다.
    # ⚠ `N` 은 실측 갱신 주기의 2배로 **사전등록**한다(313차 ④ — 결과를 보고 조정 금지).
    # ⚠ 값이 원래 잘 안 변하는 지표는 `benign: true` 로 등록해 표시만 하고 적신호에서 뺀다.
    #
    # 🔴 **등록은 로그 실측으로만 한다.** 0821 등록문은 초기 3종(`앙상블보정기` ·
    #    `MetaConf` · `앙상블가중`)을 제안했으나, 488차 구현 시 실측한 결과
    #    **나머지 둘은 캡처할 로그가 없다** — `MetaConf` 는 복원 **실패** 시에만 찍고
    #    (`main.py:4660-4662` — 성공 경로 무로그), 호라이즌 가중은 로그 자체가 없다.
    #    없는 로그를 등록하면 매일 `무기록` 이 떠 늑대소년이 된다(§12 규약과 같은 취지).
    #    → **두 축은 로그 신설이 선행조건**이며 별건으로 남긴다(NEXT_TODO 488차 항목).
    "snapshot_identity": {
        "lookback_days": 14,
        "patterns": {
            "앙상블보정기_스냅샷": {
                "re": r"\[Calibration\] 앙상블 보정기 복원 완료 "
                      r"n=(?P<n>\d+) fitted=(?P<fitted>\S+)[^\n]*?out_max=(?P<out_max>\S+)",
                "files": ["_SYSTEM"],
                "fields": ["n", "fitted", "out_max"],
                # 실측 갱신 주기 = 매 거래일(EOD 15:40 저장) → 정체 허용 상한을 넉넉히
                # 잡아도 4거래일이면 이상. 0821 사고는 7거래일이었다. **N=8 사전등록**
                # (0821 G-1 등록문 그대로 — 구현 시점에 결과를 보고 바꾸지 않았다).
                "n_warn": 8,
                # 여기서는 배포일이 아니라 **로그 형식이 존재하는 최초일**이다.
                # 477차 G-1 의 measured_since 는 *로그 자체가 신설된* 축을 위한 것인데
                # 이 로그는 최소 2026-07-31 부터 같은 형식으로 있었다(실측). 배포일로
                # 잡으면 소급 창이 통째로 비어 **이미 일어난 정체를 못 본다** — 그러면
                # 이 축을 만든 이유가 사라진다.
                "measured_since": "2026-07-31",
                "why": "앙상블 Platt 보정기 스냅샷(n·fitted·out_max). 매 거래일 EOD 에 "
                       "갱신되는 것이 정상. 같은 튜플이 N거래일 연속이면 저장 경로가 "
                       "끊긴 것이다 — 2026-08-12~21 `n=1183` 10일 연속이 그 사례이며"
                       "(실측) 그때는 사람이 pkl mtime 을 직접 열어보고서야 알았다"
                       "(0821 이상점 1-1). 원인은 **485차 F-1 로 08-23 수정 완료** — "
                       "따라서 08-24 이후 갱신으로 바뀌는 것이 기대값이고, 그 전환 "
                       "자체가 F-1 의 라이브 검증(P-1·P-2)이 된다. 계속 정체면 "
                       "수정이 듣지 않은 것이다",
            },
        },
    },
    # ── [MW0602 476차 G-4] 임계-분포 대조 (threshold reachability) ─────────────
    # §12 고착 검사가 못 잡는 네 번째 죽음: **로그는 정상 출력되는데 그 로그가 지키려던
    # 분기가 죽어 있다.** 0819 리포트 1-9(`[EntryGate] 조건부 구간` 54회 정상 출력 —
    # 죽은 것은 로그가 아니라 "A등급이면 통과"라는 분기 자체)가 그것이고,
    # 471차 F-1(6개월)·474차(6개월)·1-9(약 3개월) 모두 사람이 우연히 발견했다.
    # 여기서는 판정식의 **상수 임계**와 그 임계를 받는 **DB 컬럼의 실측 분포**를 짝지어
    # `max(관측) < 임계` 가 N거래일 연속이면 §12b 에 표시한다.
    #  · known: 이미 규명·등록된 미도달(안건 참조 문자열). §11 적신호로는 **known 이
    #    없는 항목만** 올린다 — 규명된 사실을 매일 경보로 울리면 늑대소년이 된다.
    #  · ⚠ 조건부로만 발생하는 임계(예: CRASH 레짐 전용)는 미도달이 정상이다 —
    #    그런 쌍은 등록하지 말거나 known 으로 등록할 것(§12 benign 과 같은 취지).
    #  · ⚠ 판정 기준 변경이 아니다 — 관측 전용이며 어떤 캠페인 합격선도 건드리지 않는다.
    "threshold_reachability": {
        "lookback_days": 14,
        "consec_days_warn": 3,
        "pairs": {
            "앙상블A(conf≥0.70)": {
                "db": "data/db/predictions.db",
                "sql": "select substr(ts,1,10) d, max(confidence) from ensemble_decisions "
                       " where direction != 0 and ts >= ? and ts <= ? || ' 23:59:59' group by 1",
                "threshold": 0.70,
                "known": "1-9 등록(0819) — 주간회의 2026-08-22 안건. 2026-06 이후 도달 0건",
                "why": "앙상블 등급 A 임계(ensemble_decision.py). 미도달이면 09:20~09:29 "
                       "'A등급만 허용' 게이트가 전면 금지로 동작하고 HCGuard·CRASH A숏 예외도 "
                       "발동 불가(tests/test_476_grade_reachability.py 가 정의를 고정)",
            },
            "앙상블B(conf≥0.60)": {
                "db": "data/db/predictions.db",
                "sql": "select substr(ts,1,10) d, max(confidence) from ensemble_decisions "
                       " where direction != 0 and ts >= ? and ts <= ? || ' 23:59:59' group by 1",
                "threshold": 0.60,
                "known": "1-9 등록(0819) — 주간회의 2026-08-22 안건",
                "why": "앙상블 등급 B 임계. A와 같은 뿌리(2026-05→06 conf 분포 급변에 임계만 고정)",
            },
            # ── [MW0602 491차 F-4] 세 번째 항목 ─────────────────────────────
            # 🔴 임계를 바꾸자는 것이 아니다. "임계에 닿지 않는다"를 매일 자동으로
            #    보이게 하고 처분은 주간회의로 올린다 — 앞 두 쌍과 같은 취급이다.
            # ⚠ 이 쌍의 원천은 **DB가 아니라 로그**다(`n` 은 online_learner 의 롤링
            #   버퍼 길이라 DB 컬럼이 없다). `log` 스펙을 쓰는 첫 쌍이다.
            "DriftRetrain조건B(n≥15)": {
                "log": {"files": ["_system"],
                        "re": r"\[DriftRetrain\] state=\S+ acc5m=\S+ n=(?P<v>\d+)"},
                "threshold": 15.0,
                "known": "1-7 등록(0824) — 20거래일 누적 후 2026-09-26 주간회의 안건. "
                         "🔴 그 전에 임계·표본 게이트 완화 금지(490차 P0 학습 위생과 얽힘)",
                "why": "장중 자동 재학습(STEP 3) 조건B의 표본 게이트(main.py `_drift_trigger_b`). "
                       "조건A는 n≥20 인데 100분 창의 5m dedup 이론 상한도 20이라 "
                       "「창 전체가 빈틈없이 conf≥0.52 통과」를 요구한다. 조건B(15)가 "
                       "미도달이면 두 분기 모두 사실상 도달 불가다. "
                       "⚠ 판정 기준 무변경(사전등록 458차 D6 교훈)",
            },
            "TOX스프레드(진입≥20틱)": {
                "db": "data/db/predictions.db",
                "sql": "select substr(ts,1,10) d, max(spread_ticks) from ensemble_decisions "
                       " where entry_executed=1 and spread_ticks is not null "
                       "   and ts >= ? and ts <= ? || ' 23:59:59' group by 1",
                "threshold": 20.0,
                "known": "473차 F-8 — 진입 표본 도달 ETA 약 7.1개월(INSUFFICIENT). 전환기준 ⑨ "
                         "처분(선행조건 유지 vs 26주 WFA 이관)은 주간회의 안건",
                "why": "TOXICITY_SEVERE_SPREAD_BLOCK_TICKS(전환기준 ⑨). '표본이 오지 않는다'가 "
                       "매일 자동으로 보인다. ⚠ 판정 기준 무변경(사전등록 458차 D6 교훈)",
            },
        },
    },
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


# ------------------------------------------------------------------ 거래일 판정
# [MW0602 486차 F-1 + G-1 / 488차 계획 B] 수집기가 휴장일을 인지한다.
#
# **왜.** 0823(일요일)에 `--phase post` 를 돌리자 §11 에 적신호 7건이 올라왔고
# **전부 "오늘이 휴장일"이라는 한 가지 사실의 파생**이었다(실제 결함 0건). 그중 하나는
# *"15:10 청산 경로가 아무 흔적도 남기지 않았다 — 절대원칙 1 확인 필요"* 였다.
# 반대편 사고도 있다 — 484차가 `logs/20260817_SYSTEM.log`(공휴일 기동)를 근거로
# 08-17을 거래일로 세어 "8거래일"이라 썼다. **파일의 존재/부재를 곧바로 원인으로 읽은**
# 같은 형태이고, 그 교훈은 문서(DECISION_LOG)에만 있고 도구에는 없었다.
#
# 🔴 **새 판정식을 만들지 않는다.** `config/krx_holidays.py:is_krx_holiday()` 를 쓰고
#    식은 `scripts/campaign_steps.py:40-41` 과 동일하게 `weekday()>=5 or is_krx_holiday(d)`.
#    판정식이 둘이 되면 어느 쪽이 옳은지 다투게 된다.
def is_trading_day(root, d):
    """거래일이면 (True, "거래일"), 아니면 (False, 사유).

    반환 사유: "주말(토)" / "주말(일)" / "공휴일(KRX)" / "거래일"
               / "거래일(추정 — 공휴일표 미적재)"

    ⚠ 수집기는 **표준 라이브러리만** 쓰는 것이 원칙이라, repo 모듈 임포트가 실패하면
      `weekday()>=5` 만으로 폴백하고 **그 사실을 사유에 남긴다.** 공휴일은 못 거르되
      주말은 걸러진다 — 부분 성립이 무성립보다 낫다.
    """
    wd = d.weekday()
    if wd >= 5:
        return False, "주말(%s)" % ("토" if wd == 5 else "일")
    added = False
    try:
        if root and root not in sys.path:
            sys.path.insert(0, root)
            added = True
        from config.krx_holidays import is_krx_holiday
        return (False, "공휴일(KRX)") if is_krx_holiday(d) else (True, "거래일")
    except Exception:
        return True, "거래일(추정 — 공휴일표 미적재)"
    finally:
        if added:
            try:
                sys.path.remove(root)
            except ValueError:
                pass


def prev_trading_day(root, d, max_back=14):
    """`d` 직전 거래일. 못 찾으면 None(연휴가 14일을 넘는 일은 없다)."""
    cur = d
    for _ in range(max_back):
        cur = cur - timedelta(days=1)
        ok, _why = is_trading_day(root, cur)
        if ok:
            return cur
    return None


# [486차 F-1] 휴장일에 **강등할 적신호**를 명시 열거한다.
#
# 🔴 **전부 끄지 않는다.** 미커밋 변경·PC명 태그 위반·설정 불변식 `불일치`는 휴장일에도
#    유효한 사실이므로 그대로 올린다. 억제는 **당일 데이터 부재에서 파생되는 것만**이다.
# 🔴 **과잉 억제가 이 기능의 최대 위험**이다 — 휴장 플래그가 잘못 서면 진짜 결함이 있는
#    거래일에 적신호가 통째로 사라진다. 그래서 목록을 여기 고정하고
#    `tests/test_486_collector_holiday.py` 가 **6개임을 불변식으로 단언**한다.
#    목록이 늘면 테스트가 깨져 재검토를 강제한다.
HOLIDAY_SUPPRESS = (
    "당일 날짜 토큰 파일 0개",           # ① 프로그램이 안 돌았다 — 휴장이면 정상
    "15:10 청산 경로가 아무 흔적도",      # ② 절대원칙 1 거짓 경보
    "완료 마커 **`daily_close_done`**",  # ③ 15:40 마감
    "완료 마커 **`eod_retrain_done`**",  # ④ ⚠ "다음날 CB③ HALT 위험" 인과는 휴장일엔 불성립
    "완료 마커 **`strategy_report`**",   # ⑤ 일일 전략 리포트
    "**진입 0건**",                      # ⑥ 거래가 없는 날의 진입 0은 결함이 아니다
)


def split_holiday_flags(flags):
    """휴장일 적신호를 (남길 것, 강등할 것)으로 가른다. 순수 함수 — 테스트 대상."""
    keep, sup = [], []
    for f in flags:
        (sup if any(k in f for k in HOLIDAY_SUPPRESS) else keep).append(f)
    return keep, sup


# ------------------------------------------------------------------ 장전 발화 마진
# [MW0602 488차 계획 A] 485차 G-2 + 476차 G-3 병합.
#
# **왜 재는가.** 0821 O-10 이 "예약 발화가 09:00 전인가"를 3거래일 관측으로 판정하려
# 했는데, 마진이 **예측 47초 vs 실측 12초** 로 4배 차이가 났다. 아무도 그 값을 매일
# 보고 있지 않아서 단발 관측으로 판정할 뻔했다. 그리고 반대편에서는 0819 장전 점검이
# **09:07**(개장 7분 후)에 돌아 장전/장중 표본이 한 파일에 섞였다 — 같은 축의 반대편이다.
#
# 🔴 **마진이 작다고 cron 을 08:58:30 이전으로 앞당기지 말 것.**
#    `phases.md` A-2(08:55 매크로 → 레짐 확정) 증거를 잃는다. 0821 실측 레짐 확정은
#    **08:58:19** 였다. 이 경고는 렌더에도 매번 동봉한다.
MARGIN_ANCHOR = "09:00:00"          # 개장 — 마진의 기준점
MARGIN_WARN_SEC = 30                # 이보다 작으면 경고 (사전등록 — 사후 조정 금지)
MARGIN_WARN_STREAK = 2              # 연속 N거래일이면 §11 적신호로 승격
MARGIN_TREND_DAYS = 5               # 추이 표에 싣는 과거 다이제스트 수


def _fire_margin(day, now):
    """발화 마진(초) = 09:00:00 − 생성시각. 순수 함수 — 시각 조작 없이 테스트한다.

    Args:
        day: 점검 대상일(`date`).
        now: 수집기 실행 시각(`datetime`, KST).

    Returns:
        (margin_sec, kind)
          kind == "live"      — 대상일 == 실행일. margin_sec 유효(음수면 개장 후 실행).
          kind == "backfill"  — 대상일 ≠ 실행일(소급/재실행). margin_sec 는 None.

    ⚠ **소급 실행에 마진을 계산하지 않는다.** 0823 이상점 1-2(예약작업 재실행으로
      일요일에 08-21분 점검이 다시 돈 건)에서 보듯, 그때 나오는 "마진"은 발화 품질이
      아니라 재실행 시각일 뿐이다. 그 값을 추이에 섞으면 판정이 오염된다.
    """
    if day is None or now is None:
        return None, "backfill"
    if day.strftime("%Y-%m-%d") != now.strftime("%Y-%m-%d"):
        return None, "backfill"
    h, m, s = [int(x) for x in MARGIN_ANCHOR.split(":")]
    anchor = now.replace(hour=h, minute=m, second=s, microsecond=0)
    return int(round((anchor - now).total_seconds())), "live"


def fmt_margin(sec):
    """마진 초를 사람이 읽는 문자열로. 음수는 개장 **후** 실행이라는 뜻이다."""
    if sec is None:
        return "—"
    if sec >= 0:
        return "+%d초 (개장 %d분 %d초 전)" % (sec, sec // 60, sec % 60)
    a = -sec
    return "−%d초 (**개장 %d분 %d초 후**)" % (a, a // 60, a % 60)


_EVIDENCE_GEN_RE = re.compile(
    r"^- 생성 (\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2}):(\d{2}) KST")
_EVIDENCE_NAME_RE = re.compile(r"^evidence_(.+)-(\d{8})_pre\.md$")


def read_margin_history(out_dir, pcid, day, limit=MARGIN_TREND_DAYS):
    """과거 장전 다이제스트에서 발화 마진 추이를 되읽는다.

    같은 폴더의 `evidence_<PC>-YYYYMMDD_pre.md` 파일에서 생성 줄(고정 형식)을 파싱한다.
    ⚠ evidence 는 `.gitignore` 대상이라 **이 이력은 로컬 전용**이다 — 다른 PC 나
      새 클론에는 없다. 표에 그 사실을 명시한다(없는 이력을 "마진 양호"로 읽지 않게).

    반환: [(ymd, margin_sec 또는 None)] — 날짜 내림차순, 대상일 제외.
    """
    out = []
    try:
        names = sorted(os.listdir(out_dir), reverse=True)
    except OSError:
        return out
    today_tok = day.strftime("%Y%m%d")
    for fn in names:
        m = _EVIDENCE_NAME_RE.match(fn)
        if not m or m.group(1) != pcid or m.group(2) >= today_tok:
            continue
        try:
            with io.open(os.path.join(out_dir, fn), encoding="utf-8",
                         errors="replace") as f:
                for _ in range(40):          # 생성 줄은 머리 몇 줄 안에 있다
                    ln = f.readline()
                    if not ln:
                        break
                    g = _EVIDENCE_GEN_RE.match(ln)
                    if not g:
                        continue
                    # 그 다이제스트의 대상일 == 파일명 날짜. 생성일이 다르면 소급본이다.
                    if g.group(1).replace("-", "") != m.group(2):
                        out.append((m.group(2), None))
                        break
                    sec = (hhmm_to_min(MARGIN_ANCHOR[:5]) * 60
                           - (int(g.group(2)) * 3600 + int(g.group(3)) * 60
                              + int(g.group(4))))
                    out.append((m.group(2), sec))
                    break
        except OSError:
            continue
        if len(out) >= limit:
            break
    return out


def _is_tight(sec):
    """**정시 발화인데 여유가 없는** 날인가 — 연속 판정이 세는 것은 이것뿐이다.

    🔴 개장 **후** 실행(`sec < 0`)을 여기 넣지 않는다. 그것은 "마진이 빠듯하다"가
    아니라 **"장전 점검이 아예 늦었다"** 는 다른 사건이고, 이미 별도 적신호
    (`장전 점검이 개장 후 N분에 실행됨`)로 올라간다. 섞으면 두 가지가 뭉개진다 —
    실측이 그걸 보여줬다: 08-18·08-14 다이제스트는 각각 개장 **452분·635분 후**에
    생성된 수동 실행분인데, 부호만 보고 세면 "마진 빠듯함 4일 연속"이 된다.

    ⚠ 이 구분은 **결과를 보고 만든 문턱이 아니다**(313차 ④). 새 상수를 도입하지
      않았고, 기존 경계(0 = 개장)를 쓴다.
    """
    return sec is not None and 0 <= sec < MARGIN_WARN_SEC


def margin_streak_flag(cur_sec, history):
    """`0 ≤ 마진 < MARGIN_WARN_SEC` 가 연속 `MARGIN_WARN_STREAK` 거래일이면 적신호.

    ⚠ 임계·연속일은 **0821 G-2 등록문 그대로의 사전등록 값**이다(313차 ④ — 결과를
      보고 조정하지 않는다). 소급본(None)과 지각본(음수)은 판정에서 제외하되 연속을
      끊지도 않는다 — "관측 못 함"·"다른 사건"을 "정상"으로도 "위반"으로도 세지 않는다.
    """
    if not _is_tight(cur_sec):
        return None
    streak, seen = 1, []
    for _ymd, sec in history:
        if sec is None or sec < 0:      # 소급본·지각본 — 중립(건너뛴다)
            continue
        if _is_tight(sec):
            streak += 1
            seen.append(_ymd)
            if streak >= MARGIN_WARN_STREAK:
                break
        else:
            break
    if streak < MARGIN_WARN_STREAK:
        return None
    return ("장전 발화 마진 **%d초** — `<%d초` 가 %d거래일 연속(%s). "
            "예약 발화가 개장에 너무 붙었다. 🔴 **cron 을 08:58:30 이전으로 앞당기지 말 것** — "
            "A-2(08:55 매크로→레짐, 실측 확정 08:58:19) 증거를 잃는다"
            % (cur_sec, MARGIN_WARN_SEC, streak,
               ", ".join(seen) if seen else "이전 관측"))


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
    # [MW0602 476차 F-5] `--no-optional-locks` — status 계열이 .git/index.lock 을
    # 만들지 않게 한다. 0819 장전에 스테일 index.lock 이 커밋을 막았고, 샌드박스
    # 마운트는 unlink 불가라 세션이 스스로 지울 수도 없었다. 읽기 전용 수집기가
    # 락을 남길 이유가 없다.
    try:
        p = subprocess.Popen(["git", "--no-optional-locks"] + list(args), cwd=root,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate(timeout=timeout)
        dec = lambda b: b.decode("utf-8", "replace").strip()
        return dec(out) if p.returncode == 0 else "(git 실패 rc=%s) %s" % (p.returncode, dec(err)[:300])
    except Exception as e:
        return "(git 실행 불가) %s" % e


# --pc 인자 / MIREUK_PC_ID 환경변수로 들어온 PC명 override. main() 이 채운다.
_PC_OVERRIDE = None


def _norm_pc(value):
    """'MW0602' . 'mw0602' . 'DeskTop-MW0602' 어느 형태로 줘도 MW#### 를 뽑는다."""
    if not value:
        return None
    m = re.search(r"(MW\d{4})", value, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    v = value.strip().upper()
    return v or None


def pc_id():
    """CLAUDE.md 규약: 호스트명에서 MW#### 를 뽑는다 (utils/db_utils.py:pc_id() 와 동일 취지).

    우선순위: `--pc` 인자 > `MIREUK_PC_ID` 환경변수 > 호스트명 자동탐지.
    아무것도 주지 않으면 종전과 **완전히 같게** 동작한다 (MW0601 기존 사용 무영향).

    override 가 필요한 이유: 예약작업.컨테이너처럼 **호스트명이 그 PC의 것이 아닌
    환경**에서 돌면 자동탐지가 UNKNOWN 이 되고, 그대로 커밋하면 어느 PC의 관찰인지
    영영 모르게 된다 (2026-08-13 MW0602 코웍 예약작업에서 실측 - 샌드박스
    호스트명이 `claude` 로 나온다).
    """
    host = platform.node() or ""
    forced = _PC_OVERRIDE or _norm_pc(os.environ.get("MIREUK_PC_ID"))
    if forced:
        return forced, "%s (override . host=%s)" % (forced, host or "?")
    m = re.search(r"(MW\d{4})", host, re.IGNORECASE)
    return (m.group(1).upper() if m else "UNKNOWN"), host


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
def check_invariants(root, cfg):
    """config/settings.py 를 import 하지 않고 정규식으로만 읽는다.

    import 하면 py37_32 전용 모듈이 딸려 들어와 터진다. 여기서는 '값이 무엇인가'만
    알면 되므로 텍스트로 읽는 편이 안전하고 빠르다.
    """
    path = os.path.join(root, "config", "settings.py")
    if not os.path.exists(path):
        return None, []
    text = read_text(path)
    rows = []
    for inv in cfg["invariants"]:
        name = inv["name"]
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
    return path, rows


# ------------------------------------------------------------------ 확정 결정 레지스트리
# [MW0602 475차 후속3] 왜 일일 다이제스트에 주간회의 결정이 필요한가.
#
# 2026-08-18 장후 리포트 §5 R-1 이 "TP1 보호트레일 protect_offset 감도 섀도 계측"을
# **신규 제안**했다. 그런데 그 질문은 캠페인 [25] `tp1_protect_offset_shadow`(404차
# 후속3, 443차 정본 재생기 이관)가 이미 더 강한 형태(소급 counterfactual, 95훅/16일)로
# 측정했고, 판정(FAIL)을 지나 **주간회의 확정 결정(2026-08-08 "미적용 유지")**까지
# 끝나 있었다. R-1 의 방향 직관(보호를 느슨하게)조차 실측이 반박한다(v2: breakeven
# Δ−0.08pt ≈ 현행 동률, 우세 변형은 오히려 타이트한 atr_lock_0.75 +12.62pt).
#
# CLAUDE.md 캠페인 절이 경고한 바로 그 사고다 — *"일부러 적용하지 않기로 한 FAIL 을
# 다음 세션이 보고 적용을 재시도할 위험"*. 레지스트리는 있었지만 주간 리포트(docs/)에만
# 렌더되고 이 수집기의 scan_dirs(logs·data)에는 안 잡혀 **일일 세션의 시야에 없었다.**
# 그래서 최신 주간 리포트에서 결정 헤딩만 뽑아 §13 으로 노출한다.
def scan_campaign_decisions(root, pcid):
    """최신 주간 캠페인 리포트의 "확정 결정 레지스트리" 헤딩을 추출한다.

    반환: {"file": 상대경로, "mtime": "MM-DD HH:MM", "entries": [(key, decision, date)]}
          리포트가 없으면 None — **미측정이지 "결정 없음"이 아니다**(계측 4원칙 ②).
    """
    base = os.path.join(root, "docs", "정기점검", "금요일점검", pcid or "")
    if not os.path.isdir(base):
        return None
    cands = sorted(
        f for f in os.listdir(base)
        if re.match(r"^validation_campaign_report_\d{8}\.md$", f))
    if not cands:
        return None
    latest = os.path.join(base, cands[-1])
    entries = []
    in_reg = False
    # 형식(주간 리포트가 렌더): `### \`key\` — 결정문 *(YYYY-MM-DD)*`
    # 결정문 안에도 — 가 있을 수 있으므로 첫 — 만 구분자로 쓴다.
    h_re = re.compile(r"^###\s+`(?P<key>[^`]+)`\s*—\s*(?P<rest>.+?)\s*$")
    d_re = re.compile(r"\*\((?P<d>\d{4}-\d{2}-\d{2})\)\*\s*$")
    try:
        with io.open(latest, encoding="utf-8", errors="replace") as f:
            for ln in f:
                if ln.startswith("## "):
                    in_reg = ln.startswith("## 확정 결정 레지스트리")
                    continue
                if not in_reg:
                    continue
                m = h_re.match(ln.strip())
                if not m:
                    continue
                rest = m.group("rest")
                dm = d_re.search(rest)
                date = dm.group("d") if dm else ""
                if dm:
                    rest = rest[:dm.start()].strip()
                entries.append((m.group("key"), rest, date))
    except (IOError, OSError):
        return None
    return {
        "file": os.path.relpath(latest, root),
        "mtime": ts_kst(os.stat(latest).st_mtime).strftime("%m-%d %H:%M"),
        "entries": entries,
    }


# ------------------------------------------------------------------ DB (읽기 전용)
# [MW0602 475차 후속] 이 수집기가 DB 를 읽는 **첫 경로**다.
#
# 왜 필요한가: 로그에는 없는 사실이 있다. 수수료가 그렇다 — 청산 줄
# `PnL=+0.34pt (+15,301원)` 의 pt 는 gross 이고 원은 **net** 이라, 로그만 보면
# "방향은 맞혔는데 비용에 졌다" 와 "방향을 틀렸다" 가 같은 숫자로 보인다.
# 2026-08-18 실측: gross +8,000원인데 수수료 33,084원이라 net -25,084원.
#
# 규율
#  · **읽기 전용**(`mode=ro`)이고 타임아웃을 둔다. 장중 점검이 본체와 겹쳐도 안전하다.
#  · 실패는 **조용히 0을 만들지 않는다** — stderr 경고 + 호출부가 "(DB 없음 — 미측정)"
#    으로 렌더한다. 계측 4원칙 ②: 미측정과 0은 다르다.
#  · 표준 라이브러리만(`sqlite3` 는 stdlib) — 이 수집기의 이식성 규약을 지킨다.
#
# ⚠ **`ensemble_decisions` 는 `predictions.db` 에 있다.** 같은 이름의
#   `data/db/ensemble_decisions.db` 가 있지만 **0바이트·테이블 0개짜리 유령**이다
#   (2026-08-18 실측). 이름만 보고 열면 조용히 빈 결과가 나온다.
# [MW0602 476차 F-2'] 3단 폴백의 접근 기록. 렌더가 `db_access_notes()` 로 읽는다.
#   rel -> 사용된 모드 집합 {"ro", "snapshot", "immutable", "실패", "없음"}
_DB_ACCESS = {}
_DB_SNAPSHOT = {}      # abs db 경로 -> 스냅샷 경로 (실패는 None) — 세션당 1회만 복사
_DB_TMPDIR = [None]


def _db_snapshot(p):
    """[MW0602 476차 F-2'] ①(`mode=ro`) 실패 시에만 — db + `-wal` + `-shm` 을 tempdir 로
    복사해 일반 open 한다. WAL 포함이라 값이 정확하다.

    ⚠ `predictions.db` 는 929MB — **세션당 1회만** 복사하고 결과(실패 포함)를 캐시한다.
    디스크 여유가 사본 크기의 1.2배 미만이면 복사하지 않는다(③ immutable 로 넘어간다).
    """
    import atexit
    import shutil
    import tempfile
    if p in _DB_SNAPSHOT:
        return _DB_SNAPSHOT[p]
    try:
        need = os.path.getsize(p)
        for suf in ("-wal", "-shm"):
            if os.path.exists(p + suf):
                need += os.path.getsize(p + suf)
        free = shutil.disk_usage(tempfile.gettempdir()).free
        if free < need * 1.2:
            eprint("[collect_evidence] DB 스냅샷 생략(디스크 여유 부족): %s" % p)
            _DB_SNAPSHOT[p] = None
            return None
        if _DB_TMPDIR[0] is None:
            _DB_TMPDIR[0] = tempfile.mkdtemp(prefix="mireuk_dbsnap_")
            atexit.register(shutil.rmtree, _DB_TMPDIR[0], True)
        dst = os.path.join(_DB_TMPDIR[0], os.path.basename(p))
        shutil.copy2(p, dst)
        for suf in ("-wal", "-shm"):
            if os.path.exists(p + suf):
                shutil.copy2(p + suf, dst + suf)
        _DB_SNAPSHOT[p] = dst
    except Exception as e:
        eprint("[collect_evidence] DB 스냅샷 실패(%s): %s" % (p, e))
        _DB_SNAPSHOT[p] = None
    return _DB_SNAPSHOT[p]


def db_rows(root, rel, sql, params=(), timeout=3.0):
    """읽기 전용 SQLite 질의. 실패하면 `None`(빈 리스트 아님 — 0과 구분한다).

    [MW0602 476차 F-2'] 3단 폴백:
      ① `file:…?mode=ro`               — 윈도우 네이티브에서 최선 (WAL 포함)
      ② 스냅샷 복사(db+`-wal`+`-shm`)   — 코웍 샌드박스가 `-shm` 매핑을 못 할 때. 값 정확
      ③ `mode=ro&immutable=1`          — 최후. **WAL 미반영**(최신 수 분 누락 가능, 경고 동반)
    실패 원인은 마운트 자체가 아니라 **라이브 프로세스가 WAL 을 쥐고 있는 동안의 경합**
    이었다(0819 장후 실측: 장전·장중 ① 실패, 장후 ① 성공). 어느 단계를 썼는지는
    `_DB_ACCESS` 에 남겨 다이제스트가 한 줄 주석으로 보여준다.
    """
    p = os.path.normpath(os.path.join(root, rel))
    if not os.path.exists(p):
        eprint("[collect_evidence] DB 없음: %s" % rel)
        _DB_ACCESS.setdefault(rel, set()).add("없음")
        return None
    esc = p.replace("\\", "/").replace("?", "%3f").replace("#", "%23")

    def _run(target, uri):
        con = sqlite3.connect(target, uri=uri, timeout=timeout)
        try:
            return con.execute(sql, tuple(params)).fetchall()
        finally:
            con.close()

    try:                                        # ① mode=ro
        out = _run("file:%s?mode=ro" % esc, True)
        _DB_ACCESS.setdefault(rel, set()).add("ro")
        return out
    except Exception as e1:
        err1 = e1
    snap = _db_snapshot(p)                      # ② 스냅샷 (세션 1회 복사)
    if snap:
        try:
            out = _run(snap, False)
            _DB_ACCESS.setdefault(rel, set()).add("snapshot")
            return out
        except Exception as e2:
            eprint("[collect_evidence] DB 스냅샷 질의 실패(%s): %s" % (rel, e2))
    try:                                        # ③ immutable=1 (WAL 누락 감수)
        out = _run("file:%s?mode=ro&immutable=1" % esc, True)
        _DB_ACCESS.setdefault(rel, set()).add("immutable")
        return out
    except Exception as e3:
        eprint("[collect_evidence] DB 질의 실패(%s): ①%s / ③%s" % (rel, err1, e3))
        _DB_ACCESS.setdefault(rel, set()).add("실패")
        return None


def db_access_notes():
    """[MW0602 476차 F-2'] ①이 아닌 경로로 읽은 DB 가 있으면 다이제스트용 주석을 낸다."""
    lines = []
    for rel in sorted(_DB_ACCESS):
        modes = _DB_ACCESS[rel]
        if "snapshot" in modes:
            lines.append("> ℹ️ `%s` — `mode=ro` 실패로 **스냅샷 사본**에서 읽었다"
                         "(WAL 포함, 값 정확. 원인: 라이브 프로세스 WAL 경합 — F-2')." % rel)
        elif "immutable" in modes:
            lines.append("> ⚠ `%s` — **`immutable=1` 폴백**으로 읽었다. WAL 미반영이라 "
                         "**최신 수 분이 누락**될 수 있다(0818 실측 8행 차이)." % rel)
        elif "실패" in modes or "없음" in modes:
            lines.append("> ⬛ `%s` — 3단 폴백 전부 실패. 이 DB 원천 지표는 "
                         "**미측정**이다(0이 아니다 — 계측 4원칙 ②)." % rel)
    return lines


def trade_costs(root, day):
    """그날 청산된 거래의 gross / 수수료 / net. 실패하면 None.

    포지션 귀속은 **진입 시각(HH:MM)** 으로 한다 — §5 포지션표가 진입 시각으로
    묶기 때문이다(470차 S3 집계 단위 규약).
    """
    d = day.isoformat()
    rows = db_rows(root, os.path.join("data", "db", "trades.db"),
                   "select substr(entry_ts,12,5) hm, count(*), "
                   "       sum(gross_pnl_krw), sum(commission_krw), sum(net_pnl_krw) "
                   "  from trades where date(exit_ts)=? group by entry_ts",
                   (d,))
    if rows is None:
        return None
    by_min, tot = {}, [0, 0.0, 0.0, 0.0]
    for hm, n, g, c, net in rows:
        g, c, net = float(g or 0), float(c or 0), float(net or 0)
        prev = by_min.get(hm)
        by_min[hm] = (n + prev[0], g + prev[1], c + prev[2], net + prev[3]) if prev \
            else (n, g, c, net)
        tot[0] += n; tot[1] += g; tot[2] += c; tot[3] += net
    return {"legs": tot[0], "gross": tot[1], "comm": tot[2], "net": tot[3],
            "by_min": by_min}


# ------------------------------------------------------------------ 고착 지표
def stuck_verdict(dist, n, hit_days, scanned_days, min_n, min_d, benign,
                  ratio=None, expected=0, ratio_min=0.5, exp_min=60):
    """값 분포 → (판정, 사유). 로그 지표와 DB 지표가 **같은 규칙**을 쓴다.

    판정 순서에 뜻이 있다:
      무기록 → 분기편향 → 표본부족 → (정상)고착 → 변동
    분기편향이 표본부족보다 앞이다 — 통계가 아니라 구조 문제라 표본이 쌓여도
    저절로 해소되지 않는다(0818 ConfFloor 는 1일차에 이미 확정적이었다).
    """
    if n == 0:
        return "무기록", "%d거래일 전체에서 0건 — 로그 문구 변경 또는 계측 중단" % scanned_days
    # [MW0602 477차 후속 F-2] ratio 는 **당일값**(가장 최근 유효 일자)이다 — 합산값은
    # 계측 배포 경계를 넘으면 미측정일을 섞으므로 판정에 쓰지 않는다(참고 표시만).
    if ratio is not None and expected >= exp_min and ratio < ratio_min:
        return "분기편향", (
            "당일 관측률 %.2f (합산 %d건 / 관측일 %d일 / 분모 %d분) — 매분 샘플러를 "
            "표방하는데 일부 분기에서만 찍힌다" % (ratio, n, len(hit_days), expected))
    if len(hit_days) < min_d or n < min_n:
        return "표본부족", "관측 %d일 · %d건 (기준 %d일 · %d건)" % (
            len(hit_days), n, min_d, min_n)
    if len(dist) == 1:
        # 한 값 100%가 **정상인** 지표가 있다(사고 없는 날의 degraded=OFF 등).
        # 그것까지 적신호로 올리면 §12 전체가 늑대소년이 된다 — 표에는 남기되
        # 경고로는 올리지 않는다.
        if dist[0][0] in benign:
            return "정상고착", "`%s` 100%% (%d건 / %d일) — 기대값" % (
                dist[0][0], n, len(hit_days))
        return "고착", "`%s` 100%% (%d건 / %d일)" % (dist[0][0], n, len(hit_days))
    return "변동", "%d개 값" % len(dist)


def scan_db_indicators(root, cfg, day):
    """[MW0602 475차 후속 / 장후 G-2] DB 원천 고착 지표.

    §12 는 로그 정규식만 봤다. 그런데 **로그에 없는 상태**가 있다 —
    471차 후속6이 신설한 `ensemble_decisions.sizing_trace.binding_gate`
    ("무엇이 실제로 사이즈를 구속했는가")가 그렇다. 431차가 곱셈 체인을 min() 합성으로
    바꾼 뒤 이 축이 생겼지만 감시 목록에 없어, 한 게이트가 상시 binding 으로 굳어도
    아무도 모른다(316차 HurstGate 63% 차단과 같은 형태).

    ⚠ `sizing_trace` 는 **2026-08-14 이후 행에만** 있다. 그 이전은 NULL 이며
      **미측정이지 "압력 0"이 아니다**(계측 4원칙 ②).
    """
    conf = cfg.get("db_indicators") or {}
    srcs = conf.get("sources") or {}
    if not srcs:
        return []
    look = int(conf.get("lookback_days", 14))
    since = (day - timedelta(days=look)).isoformat()
    rows = []
    for name, spec in srcs.items():
        # [MW0602 477차 후속 G-1] measured_since — 계측 배포일 이전 행은 미측정.
        # 창 하한을 배포일로 끌어올려 배포 전 구간이 표본에 섞이지 않게 한다.
        _ms = str(spec.get("measured_since") or "")
        _since = max(since, _ms) if _ms else since
        raw = db_rows(root, spec["db"], spec["sql"], (_since, day.isoformat()))
        if raw is None:
            # [MW0602 476차 F-2'] 접근 실패는 `무기록`(계측 중단 의심)과 다르다 —
            # 수집기 환경 문제이며 **미측정**이다. 판정을 분리해 오독을 막는다.
            rows.append({"name": name, "why": spec.get("why", ""), "days": 0, "n": 0,
                         "dist": [], "verdict": "DB미접속", "ratio": None, "expected": None,
                         "note": "DB 접근 실패(3단 폴백 전부) — **미측정**이지 0이 아니다",
                         "scanned_days": 0, "source": "DB"})
            continue
        counts, hit_days = {}, set()
        for r in raw:
            d, payload = r[0], r[1]
            v = payload
            if spec.get("json_key"):
                try:
                    v = json.loads(payload).get(spec["json_key"])
                except (ValueError, TypeError):
                    continue
            v = str(v)
            counts[v] = counts.get(v, 0) + 1
            hit_days.add(d)
        dist = sorted(counts.items(), key=lambda kv: -kv[1])
        n = sum(counts.values())
        verdict, note = stuck_verdict(
            dist, n, hit_days, look,
            int(spec.get("min_samples", conf.get("min_samples", 20))),
            int(spec.get("min_days", conf.get("min_days", 3))),
            [str(b) for b in (spec.get("benign") or [])])
        rows.append({"name": name, "why": spec.get("why", ""), "days": len(hit_days),
                     "n": n, "dist": dist, "verdict": verdict, "note": note,
                     "ratio": None, "expected": None, "scanned_days": look,
                     "measured_since": spec.get("measured_since"),
                     "source": "DB"})
    return rows


def _threshold_days_from_log(root, cfg, day, look, spec):
    """[MW0602 491차 F-4] 로그 원천 임계쌍 — 일자별 `max(캡처 수치)`.

    반환: [(YYYYMMDD, float)] 오름차순 / 정규식이 깨졌으면 None.
    ⚠ 관측 전용. §12 의 `stuck_indicators` 와 같은 파일 집합을 본다
      (`collect_files_by_day`) — 한쪽만 스캔 범위가 갈리지 않게 하기 위해서다.
    """
    try:
        rx = re.compile(spec["re"])
    except (re.error, KeyError, TypeError):
        return None
    want = [f.lower() for f in (spec.get("files") or [])]
    max_bytes = int((cfg.get("stuck_indicators") or {}).get("max_file_mb", 8)) * 1024 * 1024
    by_day = collect_files_by_day(root, cfg, day)
    out = {}
    for d in sorted(by_day)[-look:]:
        for full in by_day[d]:
            fn = os.path.basename(full).lower()
            if want and not any(w in fn for w in want):
                continue
            try:
                if os.stat(full).st_size > max_bytes:
                    continue
                with io.open(full, encoding="utf-8", errors="replace") as f:
                    for ln in f:
                        m = rx.search(ln)
                        if not m:
                            continue
                        try:
                            v = float(m.group("v"))
                        except (TypeError, ValueError, IndexError):
                            continue
                        if d not in out or v > out[d]:
                            out[d] = v
            except (IOError, OSError):
                continue
    return sorted(out.items())


def scan_threshold_reachability(root, cfg, day):
    """[MW0602 476차 G-4] 임계-분포 대조 — "로그는 정상인데 분기가 죽은" 형태 탐지.

    반환: [{name, threshold, days, overall_max, consec, verdict, known, why}]
      verdict — "도달" / "미도달(N일 연속)" / "표본없음" / "DB미접속"
    consec 는 **말미 연속** 미도달 거래일 수다(중간에 도달한 날이 있으면 거기서 끊는다).
    ⚠ 관측 전용 — 어떤 판정 기준·합격선도 건드리지 않는다.
    """
    conf = cfg.get("threshold_reachability") or {}
    pairs = conf.get("pairs") or {}
    if not pairs:
        return []
    look = int(conf.get("lookback_days", 14))
    warn_d = int(conf.get("consec_days_warn", 3))
    since = (day - timedelta(days=look)).isoformat()
    rows = []
    for name, spec in pairs.items():
        base = {"name": name, "threshold": float(spec["threshold"]),
                "known": spec.get("known"), "why": spec.get("why", ""),
                "scanned_days": look}
        # [MW0602 491차 F-4] 원천이 둘이다 — DB 컬럼(기존) 또는 **로그 캡처**.
        # 로그 원천이 필요한 이유: 임계가 지키는 값이 DB에 없는 경우가 있다
        # (`_drift_trigger_b` 의 n 은 online_learner 롤링 버퍼 길이다).
        # 그런 쌍을 등록 못 하면 §12b 는 "DB에 있는 임계만" 보는 반쪽이 된다.
        if spec.get("log"):
            day_max = _threshold_days_from_log(root, cfg, day, look, spec["log"])
            if day_max is None:
                base.update({"days": 0, "overall_max": None, "consec": None,
                             "verdict": "무기록"})
                rows.append(base)
                continue
        else:
            raw = db_rows(root, spec["db"], spec["sql"], (since, day.isoformat()))
            if raw is None:
                base.update({"days": 0, "overall_max": None, "consec": None,
                             "verdict": "DB미접속"})
                rows.append(base)
                continue
            day_max = sorted((str(d), float(v)) for d, v in raw if v is not None)
        if not day_max:
            base.update({"days": 0, "overall_max": None, "consec": None,
                         "verdict": "표본없음"})
            rows.append(base)
            continue
        thr = float(spec["threshold"])
        consec = 0
        for _d, v in reversed(day_max):
            if v < thr:
                consec += 1
            else:
                break
        overall = max(v for _d, v in day_max)
        if consec >= warn_d:
            verdict = "미도달(%d일 연속%s)" % (
                consec, " — 전 관측일" if consec == len(day_max) else "")
        elif consec == 0:
            verdict = "도달(최근일)"
        else:
            verdict = "최근 %d일 미도달" % consec
        base.update({"days": len(day_max), "overall_max": overall,
                     "consec": consec, "verdict": verdict})
        rows.append(base)
    return rows


def collect_files_by_day(root, cfg, day):
    """스캔 대상 폴더의 파일을 `YYYYMMDD` 토큰별로 묶는다. (대상일 이후는 제외)

    [MW0602 488차 계획 D] `scan_stuck_indicators` 안에 있던 것을 그대로 떼어냈다 —
    스냅샷 정체 스캐너(§12c)가 **같은 일자 집합**을 봐야 하기 때문이다. 복제하면
    한쪽만 `exclude_patterns` 가 바뀌는 식으로 조용히 갈라진다.
    ⚠ 동작 무변경 — 로직을 옮기기만 했다.
    """
    ymd_re = re.compile(r"(20\d{6})")
    today_tok = date_tokens(day)["ymd"]
    by_day = {}
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
                if any(x.lower() in fn.lower() for x in cfg.get("exclude_patterns", [])):
                    continue
                if any(x.lower() in fn.lower() for x in cfg.get("never_digest_patterns", [])):
                    continue
                m = ymd_re.search(fn)
                if not m or m.group(1) > today_tok:
                    continue
                by_day.setdefault(m.group(1), []).append(
                    os.path.normpath(os.path.join(dirpath, fn)))
    return by_day


def snapshot_verdict(seq, n_warn):
    """일자별 스냅샷 튜플 열에서 **말단 연속 동일일수**를 세어 판정한다.

    Args:
        seq: [(ymd, 튜플문자열)] — 날짜 오름차순. 그날 관측이 없으면 아예 없는 항목.
        n_warn: 연속 동일일수가 이 값 이상이면 정체.

    Returns:
        (verdict, streak) — verdict ∈ {"정체", "갱신", "표본부족"}

    ⚠ **말단(최근)부터 센다.** 과거에 정체가 있었어도 이후 갱신됐으면 지금은 정상이다 —
      485차 F-1(저장 게이트 제거) 배포 후 회복을 정체로 계속 부르면 안 된다.
    """
    if len(seq) < 2:
        return "표본부족", len(seq)
    last = seq[-1][1]
    streak = 1
    for _ymd, val in reversed(seq[:-1]):
        if val == last:
            streak += 1
        else:
            break
    return ("정체" if streak >= n_warn else "갱신"), streak


def scan_snapshot_identity(root, cfg, day):
    """[MW0602 485차 G-1 / 488차 계획 D] 값이 정상인데 **어제와 똑같은** 지표를 찾는다.

    반환: [{name, why, verdict, streak, n_warn, days, series, measured_since, benign}]
      verdict — "정체" / "갱신" / "표본부족" / "무기록"

    §12(고착·무기록)·475차 G-1(분기편향)이 못 잡는 네 번째 형태다. 설정부 주석 참조.
    """
    conf = cfg.get("snapshot_identity") or {}
    pats = conf.get("patterns") or {}
    if not pats:
        return []
    look = int(conf.get("lookback_days", 14))
    max_bytes = int((cfg.get("stuck_indicators") or {}).get("max_file_mb", 8)) * 1024 * 1024
    by_day = collect_files_by_day(root, cfg, day)
    days = sorted(by_day)[-look:]
    if not days:
        return []

    rows = []
    for name, spec in pats.items():
        base = {"name": name, "why": spec.get("why", ""),
                "n_warn": int(spec.get("n_warn", 8)),
                "measured_since": spec.get("measured_since"),
                "benign": bool(spec.get("benign")), "series": [], "streak": 0,
                "days": 0}
        try:
            rx = re.compile(spec["re"])
        except re.error as e:
            base.update({"verdict": "무기록", "note": "정규식 오류: %s" % e})
            rows.append(base)
            continue
        # [477차 후속 G-1과 같은 규약] 계측 배포일 이전은 **미측정**이지 "정체"가 아니다.
        _ms = str(spec.get("measured_since") or "").replace("-", "")
        p_days = [d for d in days if not _ms or d >= _ms]
        want = [f.lower() for f in (spec.get("files") or [])]
        fields = list(spec.get("fields") or [])
        series = []
        for d in p_days:
            got = None
            for full in by_day[d]:
                fn = os.path.basename(full).lower()
                if want and not any(w in fn for w in want):
                    continue
                try:
                    if os.stat(full).st_size > max_bytes:
                        continue
                    with io.open(full, encoding="utf-8", errors="replace") as f:
                        for ln in f:
                            m = rx.search(ln)
                            if m:
                                # 그날 **마지막** 관측을 쓴다 — 재기동이 여러 번이면
                                # 최신 상태가 그날의 스냅샷이다.
                                got = " · ".join(
                                    "%s=%s" % (k, (m.group(k) or "").strip())
                                    for k in fields)
                except (OSError, IOError):
                    continue
            if got is not None:
                series.append((d, got))
        base["series"] = series
        base["days"] = len(series)
        if not series:
            if _ms and not p_days:
                base.update({"verdict": "표본부족",
                             "note": "계측 시작 전 (measured_since %s)"
                                     % spec.get("measured_since")})
            else:
                base.update({"verdict": "무기록",
                             "note": "최근 %d거래일 기록 0건 — 로그 문구 변경 의심"
                                     % len(p_days)})
            rows.append(base)
            continue
        v, streak = snapshot_verdict(series, base["n_warn"])
        base.update({"verdict": v, "streak": streak})
        rows.append(base)
    return rows


def scan_stuck_indicators(root, cfg, day):
    """[MW0602 468차 G-2] 최근 N거래일 상태 지표의 값 분포를 센다.

    반환: [{name, why, days, n, dist:[(값, 건수)], verdict, note}]
      verdict — "고착"(한 값 100%) / "변동" / "표본부족" / "무기록"

    **왜 표본 0을 따로 세는가.** 로그 문구가 바뀌면 정규식이 조용히 아무것도 안 잡는데,
    그 상태는 "경고 없음 = 정상"으로 읽힌다. 고착과 무기록은 증상이 다를 뿐 둘 다
    "지표가 죽었다"이므로 같은 표에서 함께 보고한다.
    """
    conf = cfg.get("stuck_indicators") or {}
    pats = conf.get("patterns") or {}
    if not pats:
        return []
    look = int(conf.get("lookback_days", 10))
    max_bytes = int(conf.get("max_file_mb", 8)) * 1024 * 1024

    # 최근 N거래일 = 스캔 대상 폴더에서 발견되는 YYYYMMDD 토큰 중 오늘 이하 상위 N개.
    # 별도 캘린더가 필요 없다 — 파일이 있는 날이 곧 돌아간 날이다.
    by_day = collect_files_by_day(root, cfg, day)
    days = sorted(by_day)[-look:]
    if not days:
        return []

    # [MW0602 475차 후속] `sample_axis: "minute"` 지표의 분모 — **그 지표가 사는 로그가
    # 그날 살아 있던 분(分)**. 매분 루프 창(09:00~15:10)으로 자른다.
    # 왜 파일별인가: 채널마다 기록 주기가 달라 한 분모를 공유하면 주기 차이가 편향으로
    # 오독된다. "이 파일이 그 분에 살아 있었는데 이 지표는 안 찍혔다" 가 물어야 할 것이다.
    _ts_min_re = re.compile(r"^\d{4}-\d{2}-\d{2} (\d{2}):(\d{2})")
    _loop_lo = hhmm_to_min(cfg.get("minute_loop_window", ["09:00", "15:10"])[0])
    _loop_hi = hhmm_to_min(cfg.get("minute_loop_window", ["09:00", "15:10"])[1])
    file_minutes = {}          # full path -> 살아 있던 분 수 (같은 파일 재계산 방지)

    rows = []
    for name, spec in pats.items():
        try:
            rx = re.compile(spec["re"])
        except re.error as e:
            rows.append({"name": name, "why": spec.get("why", ""), "days": 0, "n": 0,
                         "dist": [], "verdict": "무기록",
                         "note": "정규식 오류: %s" % e})
            continue
        want = [f.lower() for f in (spec.get("files") or [])]
        # [MW0602 476차 F-8] "ensemble_minute" 축 — 분모를 로그 생존 분이 아니라
        # `[Ensemble] dir=` 출현 분으로 좁힌다. compute() 안에서만 사는 지표용.
        axis = str(spec.get("sample_axis") or "")
        per_minute = axis in ("minute", "ensemble_minute")
        axis_rx = re.compile(r"\[Ensemble\] dir=") if axis == "ensemble_minute" else None
        # [MW0602 476차 G-6] value_map — 캡처값 정규화 (예: bar_pass N → "≥1(생존)")
        vmap = []
        for _vm in (spec.get("value_map") or []):
            try:
                vmap.append((re.compile(_vm[0]), str(_vm[1])))
            except (re.error, IndexError, TypeError):
                continue
        # [MW0602 477차 후속 G-1] measured_since — 계측 배포일 이전 일자는 통째로 제외.
        # 배포 전 날짜는 **미측정**이지 "관측 0"이 아니다(계측 4원칙 ②). 합산에 섞으면
        # 이미 고쳐진 계측이 며칠간 "안 고쳐진 것"처럼 보인다(0820 이상점 1-2:
        # ConfFloor 합산 0.72 vs 당일 1.00 — 08-18 배포 전 하루가 분모에 섞였다).
        _ms = str(spec.get("measured_since") or "").replace("-", "")
        p_days = [d for d in days if not _ms or d >= _ms]
        if _ms and not p_days:
            # 계측 시작 전 — `무기록`(계측 중단 의심, §11 적신호)으로 올리면 배포
            # 당일마다 늑대소년이 된다. 표본부족(판정 보류)으로 명시한다.
            rows.append({"name": name, "why": spec.get("why", ""), "days": 0, "n": 0,
                         "dist": [], "verdict": "표본부족",
                         "note": "계측 시작 전 (measured_since %s — 창 내 해당 거래일 없음)"
                                 % spec.get("measured_since"),
                         "scanned_days": 0, "measured_since": spec.get("measured_since"),
                         "ratio": None, "ratio_today": None, "ratio_min_day": None,
                         "expected": None})
            continue
        counts, hit_days = {}, set()
        expected = 0            # 분모 합 (per_minute 일 때만 의미 있다)
        day_stats = []          # [MW0602 477차 후속 F-2] (일자, 분자, 분모) — 일자별 관측률용
        for d in p_days:
            day_expected = 0
            _n_before = sum(counts.values())
            for full in by_day[d]:
                fn = os.path.basename(full).lower()
                if want and not any(w in fn for w in want):
                    continue
                try:
                    if os.stat(full).st_size > max_bytes:
                        continue
                    # 분모는 같은 스트림에서 센다 — 파일을 두 번 읽지 않는다.
                    # 캐시 키에 축을 넣는다 — 같은 파일이라도 "minute"(생존 분)와
                    # "ensemble_minute"([Ensemble] 출현 분)의 분모는 다르다(476차 F-8).
                    track = per_minute and (full, axis) not in file_minutes
                    mins = set() if track else None
                    with io.open(full, encoding="utf-8", errors="replace") as f:
                        for ln in f:
                            if track and (axis_rx is None or axis_rx.search(ln)):
                                tm = _ts_min_re.match(ln)
                                if tm:
                                    _t = int(tm.group(1)) * 60 + int(tm.group(2))
                                    if _loop_lo <= _t <= _loop_hi:
                                        mins.add(_t)
                            m = rx.search(ln)
                            if m:
                                v = (m.group("v") or "").strip()
                                for _vrx, _lbl in vmap:
                                    if _vrx.fullmatch(v):
                                        v = _lbl
                                        break
                                counts[v] = counts.get(v, 0) + 1
                                hit_days.add(d)
                    if track:
                        file_minutes[(full, axis)] = len(mins)
                except (IOError, OSError):
                    continue
                if per_minute:
                    # 여러 파일에 걸치면 **최댓값**을 쓴다. 합치면 같은 분을 두 번 세서
                    # 분모가 부풀고 멀쩡한 지표가 편향으로 보인다.
                    day_expected = max(day_expected, file_minutes.get((full, axis), 0))
            # 표본이 하나도 없는 날은 분모에서 뺀다 — 그 날은 "편향"이 아니라 **미배포**이거나
            # 계측 중단이며, 그것은 `무기록`이 말할 몫이다. 빼지 않으면 배포 첫날 지표가
            # 무조건 분기편향으로 뜬다(0818 ConfFloor: 80/2918=0.03 vs 80/365=0.22).
            _day_n = sum(counts.values()) - _n_before
            if _day_n > 0:
                expected += day_expected
                day_stats.append((d, _day_n, day_expected))
        n = sum(counts.values())
        dist = sorted(counts.items(), key=lambda kv: -kv[1])
        _min_n = int(spec.get("min_samples", conf.get("min_samples", 20)))
        _min_d = int(spec.get("min_days", conf.get("min_days", 3)))
        _benign = [str(b) for b in (spec.get("benign") or [])]
        _exp_min = int(conf.get("branch_min_expected", 60))
        _ratio = (float(n) / expected) if (per_minute and expected) else None
        # [MW0602 477차 후속 F-2] 일자별 관측률 — 합산은 계측 배포 경계·과거 결함일을
        # 창이 빠져나갈 때까지 끌고 다닌다(0820 실측: 합산 0.72 vs 당일 1.00).
        # 판정은 **당일값**(가장 최근 유효 일자)으로 한다. 분모가 exp_min 미만인 날은
        # 재지 않는다(반나절만 돈 날에 판정하지 않는다 — 기존 규약 유지).
        _day_ratios = [(d, float(dn) / de) for d, dn, de in day_stats
                       if de >= _exp_min] if per_minute else []
        _ratio_today = _day_ratios[-1][1] if _day_ratios else None
        _ratio_min_day = min(r for _, r in _day_ratios) if _day_ratios else None
        verdict, note = stuck_verdict(
            dist, n, hit_days, len(p_days), _min_n, _min_d, _benign,
            ratio=_ratio_today, expected=expected,
            ratio_min=float(conf.get("branch_ratio_min", 0.5)),
            exp_min=_exp_min)
        rows.append({"name": name, "why": spec.get("why", ""), "days": len(hit_days),
                     "n": n, "dist": dist, "verdict": verdict, "note": note,
                     "scanned_days": len(p_days),
                     "measured_since": spec.get("measured_since"),
                     "ratio": _ratio, "ratio_today": _ratio_today,
                     "ratio_min_day": _ratio_min_day,
                     "expected": expected if per_minute else None})
    return rows


def exit_stop_kind(reason):
    """[MW0602 468차 F-2/A안] 청산 사유 한 줄을 손절/보호/불명으로 가른다.

    `하드스톱` 라벨 하나에 **정반대 두 사건**이 들어 있다 — 진짜 손절과 TP1 도달 후
    보호 스톱(이익 청산). 465차 P4가 라벨 교체 대신 `trades.tp1_reached` 컬럼을 택했고
    (LIKE '%하드스톱%'가 사전등록 채널의 필터라 문자열을 못 바꾼다), 468차가 같은 값을
    청산 로그 줄에 `[TP1보호]`/`[TP1미도달]` 태그로 덧붙였다.

    반환: "stop"(진짜 손절) / "protect"(보호트레일) / "unknown"(태그 없는 구버전 로그)
          / None(손절 계열이 아님 — TP·시간마감 등)

    ⚠ 태그가 없으면 **불명으로 둔다.** 손절로 세면 없는 사실을 만들고, 보호로 세면
    진짜 손절을 숨긴다 — 둘 다 이 수집기가 실제로 저지른 오독의 형태다.
    """
    r = str(reason or "")
    if not ("스톱" in r or "손절" in r):
        return None
    if "TP1보호" in r:
        return "protect"
    if "TP1미도달" in r:
        return "stop"
    return "unknown"


def exit_stop_counts(exits):
    """청산 목록 → (진짜손절, 보호트레일, 태그없음) 건수."""
    kinds = [exit_stop_kind(e.get("reason")) for e in exits]
    return kinds.count("stop"), kinds.count("protect"), kinds.count("unknown")


def _won_to_int(s):
    """`+24,863` → 24863. 파싱 실패는 None — 0으로 떨어뜨리면 손익이 조용히 사라진다."""
    try:
        return int(str(s).replace(",", "").replace("+", ""))
    except (TypeError, ValueError):
        return None


def group_positions(entries, partials, finals):
    """진입·부분청산·최종청산 이벤트를 **포지션 단위**로 묶는다.

    [MW0602 470차 S3] 417차(2026-08-02)가 정정한 단위 혼동 — 청산 레그를 포지션으로 세는 것 —
    이 2026-08-14 리포트에서 그대로 재발했다("최대 손실 14:40" ← 실제는 13:05, 포지션으로
    묶으면 -163,268원). **원인은 사람이 아니라 이 도구다**: §5가 레그 단위로 렌더링했고
    리포트가 그것을 옮겨 적었다. 그래서 집계 단위를 도구 쪽에서 고정한다.

    미륵이는 동시에 한 포지션만 보유한다(FLAT↔보유 교대). 따라서 시각순으로 훑으며
    진입이 포지션을 열고 최종청산이 닫는 방식으로 정확히 묶인다.

    반환: (positions, orphans)
      positions — [{"entry":…, "legs":[…], "pt":float|None, "won":int|None, "closed":bool}]
      orphans   — 진입 없이 나타난 청산 레그(전일 이월·로그 절단·수집 시점 절단).
                  ⚠ **버리지 않는다.** 버리면 손익이 조용히 사라지고 검산이 통과해버린다.
    """
    ev = []
    for e in entries or []:
        ev.append((e.get("hhmm") or "", 0, "entry", e))
    for e in partials or []:
        ev.append((e.get("hhmm") or "", 1, "partial", e))
    for e in finals or []:
        ev.append((e.get("hhmm") or "", 2, "final", e))
    # 같은 초에 진입과 청산이 겹치면 진입(0) → 부분(1) → 최종(2) 순으로 정렬해야
    # 포지션이 열리기 전에 닫히는 역전이 생기지 않는다.
    ev.sort(key=lambda t: (t[0], t[1]))

    positions = []
    orphans = []
    cur = None
    for _hhmm, _ord, kind, rec in ev:
        if kind == "entry":
            cur = {"entry": rec, "legs": [], "closed": False}
            positions.append(cur)
        elif cur is not None and not cur["closed"]:
            cur["legs"].append((kind, rec))
            if kind == "final":
                cur["closed"] = True
                cur = None
        else:
            orphans.append((kind, rec))

    for p in positions:
        pts = [_pt_to_float(r.get("pt")) for _k, r in p["legs"]]
        wons = [_won_to_int(r.get("won")) for _k, r in p["legs"]]
        p["pt"] = sum(v for v in pts if v is not None) if any(v is not None for v in pts) else None
        p["won"] = sum(v for v in wons if v is not None) if any(v is not None for v in wons) else None
    return positions, orphans


def _pt_to_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def day_summary(digests, cfg, out, root=None, day=None):
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

    ds_flags = []

    A("## 5. 거래일 요약 — 오늘 무엇을 했는가")
    A("")
    if not merged and not banner:
        A("_거래일 패턴이 하나도 안 잡혔다. 로그 문구가 바뀌었을 수 있다 — "
          "`config/dailycheck_targets.json` 의 `day_summary_patterns` 를 확인하라._")
        A("")
        return ds_flags

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
    pex = merged.get("partial_exit", [])
    bl = merged.get("block", [])
    sz = merged.get("sizer", [])
    sm = merged.get("sizer_match", [])
    mc = merged.get("margin_cap", [])

    positions, orphans = group_positions(en, pex, ex)

    A("| 항목 | 건수 |")
    A("|---|---|")
    A("| 진입체크 통과(`[진입체크]`) | %d |" % len(ec))
    A("| 진입 등록(`[Position] 진입`) | %d |" % len(en))
    A("| 체결(`[체결진입]`) | %d |" % len(fi))
    A("| **포지션**(진입~최종청산) | **%d** |" % len(positions))
    A("| 청산 레그 — 최종(`체결청산`) | %d |" % len(ex))
    A("| 청산 레그 — 부분(`체결부분청산`) | %d |" % len(pex))
    A("| 차단(`[차단]`) | %d |" % len(bl))
    A("| 사이저 호출(`[Sizer]`) | %d |" % len(sz))
    A("| 사이즈 축소(`[SizerMatch]`) | %d |" % len(sm))
    # [MW0602 485차 F-5] 「조회 N · 축소 M」 2축 병기 — 신형식(state=)은 조회 성공
    # 사이클마다 무조건 찍히는 상태 샘플이라, 종전처럼 "축소만 세는 칸"에 그대로
    # 흘리면 전 건이 축소로 오독된다. CAP 사건은 신·구 두 줄이 함께 찍히므로
    # 축소는 state=CAP만 센다. 신형식이 하나도 없으면(08-20 이전 로그) 구형식
    # 축소 줄만 있던 시절이라 종전 의미(조회 미상 · 축소 N)로 폴백한다.
    _mc_state = [r for r in mc if r.get("state")]
    _mc_old = [r for r in mc if not r.get("state")]
    if _mc_state:
        A("| 증거금 상한(`[MarginCap]`) | 조회 %d · 축소 %d |"
          % (len(_mc_state), sum(1 for r in _mc_state if r.get("state") == "CAP")))
    else:
        A("| 증거금 상한(`[MarginCap]`) | 조회 — · 축소 %d (구형식만) |" % len(_mc_old))
    A("")
    A("> **집계 단위 — 승패·손익은 `포지션`으로 센다. `레그`가 아니다.**")
    A("> 이익 포지션은 TP1/TP2/TP3로 쪼개져 여러 레그가 되고 손실 포지션은 전량청산 한 레그가 된다 — "
      "레그로 세면 **없는 인과가 만들어진다**(417차가 정확히 그 사고였고, 470차 리포트에서 재발했다).")
    A("")

    # [MW0602 475차 후속 / 장후 G-1] 비용 축 — 로그에는 수수료가 없다.
    # 청산 줄의 원화는 **net** 이고 pt 는 gross 라, 순액만 보면
    # "방향은 맞혔는데 비용에 졌다"와 "방향을 틀렸다"가 같은 숫자로 보인다.
    costs = trade_costs(root, day) if (root and day) else None

    # --- 손익 (포지션 단위) ---
    if positions or orphans:
        wins = sum(1 for p in positions if (p.get("pt") or 0) > 0 and p["closed"])
        closed = [p for p in positions if p["closed"]]
        tot_pt = sum(p["pt"] for p in positions if p.get("pt") is not None)
        tot_won = sum(p["won"] for p in positions if p.get("won") is not None)
        for _k, r in orphans:
            _w = _won_to_int(r.get("won"))
            _p = _pt_to_float(r.get("pt"))
            if _w is not None:
                tot_won += _w
            if _p is not None:
                tot_pt += _p
        n_leg = len(ex) + len(pex)
        A("### 포지션 %d건 (레그 %d) · 승 %d / 종료 %d (%s) · 합계 %+.2fpt (%s원)"
          % (len(positions), n_leg, wins, len(closed),
             ("%.0f%%" % (100.0 * wins / len(closed))) if closed else "—",
             tot_pt, format(tot_won, "+,d")))
        A("")
        # 비용 축 — 하루 합계. 승률이 높은데 적자인 날을 그 자리에서 가른다.
        if costs is None:
            A("> ⚠ **비용 축 미측정** — `data/db/trades.db` 를 읽지 못했다. "
              "아래 `합계원`은 수수료 차감 **후**(net)이며 gross 는 알 수 없다. "
              "**미측정이지 수수료 0이 아니다.**")
            A("")
        else:
            _g, _c, _net = costs["gross"], costs["comm"], costs["net"]
            _ratio = ("%.0f%%" % (100.0 * _c / abs(_g))) if _g else "n/a"
            A("### 비용 축 — gross %s원 · 수수료 %s원 · net %s원 (수수료/|gross| = %s)"
              % (format(int(_g), "+,d"), format(int(_c), ",d"),
                 format(int(_net), "+,d"), _ratio))
            A("")
            if _g > 0 > _net:
                A("> 🔴 **수수료가 손익의 부호를 뒤집었다** — 방향은 맞혔고 비용에 졌다. "
                  "gross `%s원` → net `%s원`." % (format(int(_g), "+,d"), format(int(_net), "+,d")))
                A("")
            elif _g < 0 and _c > abs(_g):
                A("> ⚠ **수수료가 원손실보다 크다** — 손실의 절반 이상이 비용이다.")
                A("")
            A("> 원천은 `trades` 의 `gross_pnl_krw`·`commission_krw`·`net_pnl_krw` 다. "
              "로그의 원화는 **net**, pt 는 **gross** 라 둘을 그냥 나누면 안 된다.")
            A("")
        A("**포지션 단위** — 진입 시각으로 묶었다.")
        A("")
        A("| 진입 | 방향 | 계약 | 레그 | 합계pt | gross원 | 수수료 | 합계원(net) | 청산 사유 체인 |")
        A("|---|---|---|---|---|---|---|---|---|")
        for p in positions:
            e = p["entry"]
            chain = " → ".join(
                "%s(%s)" % ((r.get("reason") or "?").strip(), r.get("pt")) for _k, r in p["legs"]
            ) or "_미청산_"
            _cm = (costs or {}).get("by_min", {}).get((e.get("hhmm") or "")[:5])
            A("| %s | %s | %s | %d | %s | %s | %s | %s | %s |" % (
                e.get("hhmm"), e.get("dir"), e.get("qty"), len(p["legs"]),
                ("%+.2f" % p["pt"]) if p.get("pt") is not None else "?",
                format(int(_cm[1]), "+,d") if _cm else "—",
                format(int(_cm[2]), ",d") if _cm else "—",
                format(p["won"], "+,d") if p.get("won") is not None else "?",
                truncate(chain, 110)))
        A("")
        if any(not p["closed"] for p in positions):
            n_open = sum(1 for p in positions if not p["closed"])
            A("> ⚠ **미청산 포지션 %d건** — 수집 시점에 아직 열려 있거나 청산 로그를 못 찾았다. "
              "장후 국면이면 절대원칙 ①(15:10 강제청산) 확인 대상이다." % n_open)
            A("")
            ds_flags.append("**미청산 포지션 %d건** — 청산 로그 미발견. 절대원칙 ① 확인" % n_open)
        if orphans:
            A("> 🔴 **진입 없이 나타난 청산 레그 %d건** — 전일 이월이거나 로그가 잘렸다. "
              "손익에는 포함했으나 포지션으로 묶지 못했다." % len(orphans))
            for _k, r in orphans:
                A(">   - %s %s %s (%s)" % (r.get("hhmm"), r.get("pt"), r.get("won"),
                                           truncate((r.get("reason") or "?").strip(), 40)))
            A("")
            ds_flags.append("진입 없는 청산 레그 **%d건** — 이월 포지션 또는 로그 절단" % len(orphans))

        # --- 자동 검산: 전략 상태 경보 배너의 '오늘 PnL' 과 대조 ---
        # 2026-08-14: §5가 -82,547원(레그·부분청산 누락), 배너가 -93,450원이었는데
        # 둘이 같은 절에 나란히 찍혀 읽는 사람이 매번 손으로 검산해야 했다.
        banner_won, banner_src = None, None
        for bline in banner or []:
            bm = re.search(r"오늘\s*PnL\s*[:：]\s*([+-]?[\d,]+)\s*원", bline)
            if bm:
                banner_won, banner_src = _won_to_int(bm.group(1)), "전략경보 배너"
                break
        if banner_won is None:
            # [MW0602 476차 F-7] 전략경보 배너가 없는 날(0819 실측)의 폴백 —
            # `일일 마감 | 승=… 패=… PnL=…` 줄은 15:40 마다 무조건 발행된다.
            _dc = merged.get("daily_close") or []
            if _dc:
                banner_won = _won_to_int(_dc[-1].get("won"))
                banner_src = "`일일 마감` 배너"
        if banner_won is not None:
            diff = tot_won - banner_won
            if abs(diff) <= 2:      # 반올림 1원 차는 정상
                A("> ✅ **검산 일치** — §5 합계 `%s원` ≒ %s `%s원` (차 %d원)"
                  % (format(tot_won, "+,d"), banner_src, format(banner_won, "+,d"), diff))
            else:
                A("> 🔴 **검산 불일치** — §5 합계 `%s원` vs %s `%s원` (**차 %s원**). "
                  "어느 한쪽이 레그를 빠뜨렸다는 뜻이다. 리포트에 손익을 옮겨 적기 전에 원인을 찾아라."
                  % (format(tot_won, "+,d"), banner_src, format(banner_won, "+,d"), format(diff, "+,d")))
                ds_flags.append(
                    "§5 손익 `%s원` ≠ %s `%s원` (차 %s원) — 집계 누락 의심"
                    % (format(tot_won, "+,d"), banner_src, format(banner_won, "+,d"), format(diff, "+,d")))
            A("")
        else:
            A("> ⚠ 전략경보 배너(`오늘 PnL`)도 `일일 마감 | … PnL=` 줄도 못 찾아 **검산하지 못했다.** "
              "장중이면 정상(둘 다 15:40 마감 시 발행). 장후면 배너 문구 변경을 의심하라.")
            A("")

        # --- 레그 상세 (접어둔다 — 단위 혼동 방지) ---
        if ex or pex:
            reasons = {}
            for e in ex:
                r = (e.get("reason") or "?").strip()
                reasons[r] = reasons.get(r, 0) + 1
            A("<details><summary>청산 레그 상세 %d건 (부분 %d + 최종 %d) — "
              "⚠ 이 표로 승패를 세지 말 것</summary>" % (n_leg, len(pex), len(ex)))
            A("")
            A("| 시각 | 종류 | 방향/계약 | PnL(pt) | PnL(원) | 사유 |")
            A("|---|---|---|---|---|---|")
            for p in positions:
                for k, r in p["legs"]:
                    A("| %s | %s | %s | %s | %s | %s |" % (
                        r.get("hhmm"), "부분" if k == "partial" else "**최종**",
                        r.get("dir") or ("%s계약" % r.get("qty")),
                        r.get("pt"), r.get("won"), (r.get("reason") or "?").strip()))
            for k, r in orphans:
                A("| %s | %s(고아) | %s | %s | %s | %s |" % (
                    r.get("hhmm"), "부분" if k == "partial" else "최종",
                    r.get("dir") or ("%s계약" % r.get("qty")),
                    r.get("pt"), r.get("won"), (r.get("reason") or "?").strip()))
            A("")
            A("</details>")
            A("")
            if reasons:
                A("**최종청산 사유 분포** — " + ", ".join(
                    "`%s`×%d" % (k, v) for k, v in sorted(reasons.items(), key=lambda kv: -kv[1])))
                A("")
            if pex:
                pr = {}
                pwon = 0
                for e in pex:
                    r = (e.get("reason") or "?").strip()
                    pr[r] = pr.get(r, 0) + 1
                    _w = _won_to_int(e.get("won"))
                    if _w is not None:
                        pwon += _w
                A("**부분청산 %d건 · 합계 %s원** — " % (len(pex), format(pwon, "+,d")) + ", ".join(
                    "`%s`×%d" % (k, v) for k, v in sorted(pr.items(), key=lambda kv: -kv[1])))
                A("")
                A("> 부분청산은 **포지션 손익의 일부**다. 최종청산만 더하면 배너와 어긋난다"
                  "(2026-08-14 실측 차 10,902원).")
                A("")
        n_stop, n_prot, n_unk = exit_stop_counts(ex)
        if n_stop or n_prot or n_unk:
            A("> **손절 계열 분해** — 진짜 손절 %d건 · TP1 보호트레일 %d건 · 태그없음 %d건 "
              "(청산 %d건 중)" % (n_stop, n_prot, n_unk, len(ex)))
            if n_prot:
                A("> `하드스톱` 라벨이지만 **TP1 도달 후 보호 스톱 = 이익 청산**인 건이 "
                  "%d건이다. 손절로 세지 말 것 — 라벨 하나에 정반대 두 사건이 들어 있다"
                  "(465차 `tp1_reached`, 468차 로그 태그)." % n_prot)
            if n_unk:
                A("> 태그 없는 %d건은 **468차 이전 로그**다. 손절로도 보호로도 세지 않는다 — "
                  "`trades.tp1_reached`(08-13 이후 적재)로 직접 확인하라." % n_unk)
            if n_stop:
                A("> 진짜 손절 %d건의 **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 "
                  "417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라."
                  % n_stop)
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

    # --- 실효 상한 분해 (SizerMatch / MarginCap) ---
    # [MW0602 470차 S3+B3] 사이저 출력이 그대로 체결되지 않는 경로는 두 개다 —
    #   (1) 품질게이트 min() 합성(431차)   (2) 브로커 증거금 상한(get_order_available_qty)
    # 이 둘은 성격이 정반대다: 증거금은 **자본이 늘면 사라지고**, 게이트 배수는 안 사라진다.
    # ⑧ 해제 판단에서 절대 같이 세면 안 되므로 사유별로 갈라 보여준다.
    if sm or mc:
        A("### 실효 상한 분해 — 무엇이 그날의 binding constraint였나")
        A("")
        A("| 경로 | 건수 | 내용 |")
        A("|---|---|---|")
        if sm:
            gaps = {}
            for s in sm:
                gaps["%s→%s" % (s.get("sizer_qty"), s.get("actual_qty"))] = \
                    gaps.get("%s→%s" % (s.get("sizer_qty"), s.get("actual_qty")), 0) + 1
            A("| 품질게이트 `[SizerMatch]` | %d | %s |" % (
                len(sm), ", ".join("`%s계약`×%d" % (k, v)
                                   for k, v in sorted(gaps.items(), key=lambda kv: -kv[1]))))
        # [MW0602 485차 F-5] 신형식(state=) 도입 후 mc에는 무조건 상태 샘플(OK 포함)이
        # 섞인다. binding 판정은 축소 사건(state=CAP, 구형식 축소 줄)만으로 한다 —
        # CAP 사건은 신·구 두 줄이 함께 찍히므로 신형식이 있으면 신형식만 센다.
        _mc_state = [m_ for m_ in mc if m_.get("state")]
        _mc_bind = ([m_ for m_ in _mc_state if m_.get("state") == "CAP"]
                    if _mc_state else [m_ for m_ in mc if not m_.get("state")])
        if mc:
            caps = {}
            for m_ in _mc_bind:
                _ck = "%s→%s" % (m_.get("calc"), m_.get("cap") or m_.get("cap_new"))
                caps[_ck] = caps.get(_ck, 0) + 1
            A("| 증거금 `[MarginCap]` | 조회 %s · 축소 %d | %s |" % (
                ("%d" % len(_mc_state)) if _mc_state else "—", len(_mc_bind),
                ", ".join("`%s계약`×%d" % (k, v)
                          for k, v in sorted(caps.items(), key=lambda kv: -kv[1])) or "—"))
        A("")
        if sm:
            mult_mix = {}
            for s in sm:
                mult_mix[(s.get("mults") or "?").strip()] = \
                    mult_mix.get((s.get("mults") or "?").strip(), 0) + 1
            A("게이트 배수 조합 — " + ", ".join(
                "`%s`×%d" % (truncate(k, 60), v)
                for k, v in sorted(mult_mix.items(), key=lambda kv: -kv[1])[:5]))
            A("")
        # [MW0602 485차 F-5] mc 비어있지 않음 ≠ 발동 — 신형식은 OK만 있는 날도
        # 상태 샘플이 쌓인다. 경고는 실제 축소(_mc_bind)가 있을 때만 낸다.
        if _mc_bind:
            A("> ⚠ **증거금 상한이 발동한 날이다.** `MAX_CONTRACTS` 보다 증거금이 먼저 구속하면 "
              "실전 전환 기준 ⑧의 `[28] sizing_inversion_watch` 는 **구조적으로 표본을 못 쌓는다** "
              "(431차 이후 74포지션 qty≥3 0건). 이것은 '표본이 천천히 쌓이는 중'이 아니라 "
              "'⑧ 해제 전까지 켜지지 않는 상태'다.")
            A("")
        A("> 이 절은 신설 로그가 아니라 **이미 있던 `[SizerMatch]`(main.py:8833)를 §5 시야에 넣은 것**이다. "
          "470차 장후 1차가 `TRADE.log` 만 보고 \"축소 사유 로그가 없다\"고 오보한 원인이 여기였다.")
        A("")

    # --- 진입 가능 시간 예산 (B2) ---
    # [MW0602 470차 B2] "진입 0건"을 볼 때 **분모를 알 수 있게** 한다.
    # 2026-08-14: 11:50:27~13:00 의 70분이 TimeRouter OTHER(진입 금지)였는데, 그 사실을
    # 알려주는 것은 전환 로그 단 1줄뿐이었다. 대시보드·수집기·리포트 어디에도
    # "오늘 진입 가능 시간이 몇 분이었는가"가 없었다.
    # STABLE_TREND 80분에 진입 1건 vs OTHER 55분에 0건은 전혀 다른 정보다.
    tzs = merged.get("time_zone", [])
    if tzs:
        # 진입금지 존 — settings.py `_ZONE_PARAMS[*]["allow_new_entry"]` 및
        # main.py `is_entry_zone()` 과 같은 집합. 바뀌면 여기도 갱신할 것.
        _NO_ENTRY = {"OTHER", "EXIT_ONLY", "PRE_MARKET"}
        segs = []
        for i, t in enumerate(tzs):
            start = hhmm_to_min((t.get("hhmm") or "00:00:00")[:5])
            if i + 1 < len(tzs):
                end = hhmm_to_min((tzs[i + 1].get("hhmm") or "00:00:00")[:5])
            else:
                # 마지막 구간은 로그가 끝난 시각까지. 장중 점검이면 "진행 중"이다.
                end = max(start, hhmm_to_min(cfg["minute_loop_window"][1]))
            segs.append((t.get("zone") or "?", start, max(end, start)))

        # 매분 루프 창(09:00~15:10, 장중이면 잘린 창)과 교집합만 센다 —
        # 08:40 기동 직후의 OTHER 는 "진입 기회를 잃은 시간"이 아니다.
        _lo = hhmm_to_min(cfg["minute_loop_window"][0])
        _hi = hhmm_to_min(cfg["minute_loop_window"][1])
        budget = {}
        for zone, s, e in segs:
            s2, e2 = max(s, _lo), min(e, _hi)
            if e2 > s2:
                budget[zone] = budget.get(zone, 0) + (e2 - s2)
        total_min = sum(budget.values())

        # 존별 진입 건수 — 진입 시각이 어느 구간에 들어가는지로 귀속
        ent_by_zone = {}
        for e in en:
            m = hhmm_to_min((e.get("hhmm") or "00:00:00")[:5])
            for zone, s, ee in segs:
                if s <= m < ee:
                    ent_by_zone[zone] = ent_by_zone.get(zone, 0) + 1
                    break

        A("### 진입 가능 시간 예산 — 오늘 진입 기회가 몇 분이었나")
        A("")
        A("| 존 | 진입 | 체류(분) | 비중 | 진입 건수 |")
        A("|---|---|---|---|---|")
        for zone, mins in sorted(budget.items(), key=lambda kv: -kv[1]):
            allow = "🚫 금지" if zone in _NO_ENTRY else "✅ 허용"
            A("| `%s` | %s | %d | %.0f%% | %d |" % (
                zone, allow, mins, (100.0 * mins / total_min) if total_min else 0.0,
                ent_by_zone.get(zone, 0)))
        ban_min = sum(m for z, m in budget.items() if z in _NO_ENTRY)
        A("")
        A("**진입 가능 %d분 / 금지 %d분** (매분 루프 창 %s~%s 기준 총 %d분)" % (
            total_min - ban_min, ban_min,
            cfg["minute_loop_window"][0], cfg["minute_loop_window"][1], total_min))
        A("")
        if ban_min:
            A("> **진입 0건을 볼 때 이 분모를 먼저 보라.** 금지 구간의 0건은 이상이 아니다. "
              "매일 11:50~13:00 **70분**이 구조적으로 `OTHER`(TIME_ZONES 정의 공백)이며 "
              "462차 P1-a로 등록·채널 [53] 판정 대기 중이다(`settings.py:5184`).")
            A("")
        if any(z in _NO_ENTRY and n_ent for z, n_ent in ent_by_zone.items()):
            _viol = {z: n for z, n in ent_by_zone.items() if z in _NO_ENTRY and n}
            A("> ⚠ **진입금지 존에서 진입 %d건** — `ZONE_ENTRY_BAN_ENFORCE=False`(의도된 상태)라 "
              "집행되지 않는다. 채널 [53] `zone_ban_breach_watch` 의 표본이다. "
              "**집행을 켜자는 신호로 읽지 말 것** — 위반 코호트가 흑자였다(462차)." % sum(_viol.values()))
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
        # [MW0602 470차 L1] 시간대 존 차단을 별도 행으로 분리한다.
        # 존은 min_conf 를 올리는 간접 경로로만 작동해 `conf미달`과 구분되지 않았다.
        # 2026-08-14: OTHER 존 55분이 `2_confidence`(33건/58%)에 통째로 오귀속됐다.
        n_zone = sum(1 for b in bl if "존금지" in (b.get("reason") or ""))
        if n_zone:
            A("**시간대 존 차단(`존금지`) %d건** — 위 `2_confidence` 계열과 **겹쳐 세지 말 것**. "
              "존은 `min_conf`를 올리는 간접 경로라 470차 L1 이전에는 `conf미달`로만 찍혔다."
              % n_zone)
            A("")
            A("> 매일 11:50~13:00 **70분**이 구조적으로 이 상태다(`settings.py:5184` TIME_ZONES "
              "정의 공백, 462차 P1-a 등록·채널 [53] 판정 대기). 그 구간의 진입 0건은 "
              "**분모를 보고 읽어야 한다.**")
            A("")
        elif bl:
            A("> `존금지` 라벨 0건 — 470차 L1 배포 이전 로그이거나 존 차단이 실제로 없었던 날이다. "
              "구분하려면 `[TimeRouter] 시간대 전환` 로그를 직접 볼 것.")
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

    return ds_flags


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
def clamp_windows_to_now(cfg, day, phase):
    """[MW0602 470차 S2] 아직 오지 않은 시간을 분모·공백으로 세지 않는다.

    2026-08-14 장중 점검(12:41)에서 수집기가
      적신호 ① "매분 루프 커버리지 222/371분 (59.8%)"
      적신호 ② "12:42~15:10 **연속 149분 기록 없음**"
    을 최상단에 올렸다. 실측은 **09:00~12:41 222/222분, 누락 0분**이었다 — 두 적신호 다
    미래 시각을 센 결과다. 이런 가짜 적신호가 매번 최상단에 뜨면 적신호 전체가 무시된다
    (468차 G-2가 막으려던 실패 유형과 같은 늑대소년 효과).

    ⚠ **과거일 재실행(`--date`)에는 적용하지 않는다.** 그날은 15:10까지 다 지났으므로
    창을 자르면 진짜 공백을 숨긴다. "오늘"인지 반드시 확인한다.
    ⚠ `pre`/`post` 국면도 자르지 않는다 — pre 는 창 자체가 개장 전이라 무의미하고,
    post 는 15:10 이 이미 지난 뒤라 자를 것이 없다.

    반환: 잘렸으면 "HH:MM", 아니면 None (렌더링에 쓴다)
    """
    if phase != "intra":
        return None
    now = now_kst()
    if day.strftime("%Y-%m-%d") != now.strftime("%Y-%m-%d"):
        return None                      # 과거일 재실행 — 자르지 않는다
    now_min = now.hour * 60 + now.minute
    cut = None
    for key in ("minute_loop_window", "gap_scan_window"):
        win = cfg.get(key)
        if not win:
            continue
        lo, hi = hhmm_to_min(win[0]), hhmm_to_min(win[1])
        if now_min < hi:
            new_hi = max(lo, now_min)
            cfg[key] = [win[0], m2hhmm(new_hi)]
            if key == "minute_loop_window":
                cut = m2hhmm(new_hi)
    return cut


def build(root, day, phase, cfg, discover_only=False):
    toks = date_tokens(day)
    D = toks["y_m_d"]
    phases = {"pre": ["pre"], "intra": ["pre", "intra"],
              "post": ["pre", "intra", "post"], "all": ["pre", "intra", "post"]}[phase]
    pcid, host = pc_id()
    # [470차 S2] 국면 인지 — 진행 중인 장중이면 창을 수집 시각까지 자른다.
    # cfg 를 얕은 복사해 호출자 설정을 오염시키지 않는다(digest 는 이 복사본을 받는다).
    cfg = dict(cfg)
    window_cut = clamp_windows_to_now(cfg, day, phase)
    L = []
    A = L.append

    A("# 미륵이 증거 다이제스트 — %s / %s" % (D, phase.upper()))
    A("")
    A("- 생성 %s KST · PC **%s** (`%s`)" % (now_kst().strftime("%Y-%m-%d %H:%M:%S"), pcid, host))
    A("- 리포 `%s`" % root)
    A("- 점검 범위: %s (장전=pre / 장중=intra / 장후=post)" % ", ".join(phases))
    if window_cut:
        A("- ⏳ **진행 중인 장중** — 커버리지·공백 창을 `%s` 까지 잘랐다(미래 시각을 공백으로 세지 않는다). "
          "15:10 까지의 판정은 장후 점검에서 한다." % window_cut)
    A("- 날짜 토큰: %s" % " · ".join("`%s`" % toks[k] for k in DATE_TOKEN_KEYS))
    if pcid == "UNKNOWN":
        A("- ⚠ 호스트명에서 `MW####` 를 못 뽑았다 — 커밋/DECISION_LOG 태그를 수동 확인할 것")
    A("")

    # [MW0602 486차 G-1 / 488차 계획 B] 거래일 문맥 — **3줄 고정 블록.**
    # 484차(파일 있음 → 거래일로 오계수)와 0823 1-1(파일 없음 → 결함 7건)이 같은 축의
    # 양쪽 끝이다. 둘 다 "거래일이 무엇인가"를 도구가 답하지 않아서 생겼다.
    # ⚠ **1단계는 표시까지다.** §12(10거래일)·§12b(14거래일)의 계수 정의 통합은
    #   26주 WFA 경계로 분리한다 — 지금 바꾸면 관측일 수가 달라져 시계열이 끊긴다
    #   (461차 `mdd_pct` 유형).
    is_td, td_why = is_trading_day(root, day)
    prev_td = prev_trading_day(root, day)
    prev_has_log = None
    if prev_td is not None:
        _ptok = prev_td.strftime("%Y%m%d")
        prev_has_log = any(
            _ptok in e["name"] for e in discover_files(root, cfg, prev_td))
    A("### 🗓 거래일 문맥")
    A("")
    A("- **대상일**: `%s` (%s요일)" % (D, "월화수목금토일"[day.weekday()]))
    A("- **거래일 여부**: %s" % (
        "**거래일** ✅" if is_td else "🚫 **거래일이 아니다** — %s" % td_why))
    if prev_td is None:
        A("- **직전 거래일**: 못 찾음(14일 역탐색 실패) ⚠")
    else:
        A("- **직전 거래일**: `%s` — 그날 로그 %s" % (
            prev_td.strftime("%Y-%m-%d"),
            "**있음**" if prev_has_log else "**없음** ⚠ (그날도 안 돌았는지 확인할 것)"))
    if not is_td:
        A("")
        A("> 🗓 **%s은 거래일이 아니다(%s). 아래의 0건들은 결함이 아니다.**" % (D, td_why))
        A("> 프로그램 미기동·완료 마커 부재·진입 0건은 전부 이 한 가지 사실의 파생이다. "
          "§11 에서 해당 적신호를 `휴장(정상)` 으로 강등하고 **건수를 명시**한다 — "
          "은폐가 아니라 이동이다.")
    if "추정" in td_why:
        A("")
        A("> ⚠ `config/krx_holidays.py` 임포트 실패 — **주말만 판정했다(공휴일 미판정).** "
          "공휴일에 이 다이제스트를 보면 거래일로 표시되니 수동 확인할 것.")
    A("")

    # [MW0602 488차 계획 A] 장전 발화 마진 + 지각 배너 (485차 G-2 + 476차 G-3)
    if phase == "pre":
        _margin, _kind = _fire_margin(day, now_kst())
        _hist = read_margin_history(
            os.path.join(root, "docs", "정기점검", "매일점검"), pcid, day)
        A("### ⏱ 장전 발화 마진")
        A("")
        if _kind == "backfill":
            A("- **소급 실행 — 발화 마진 무의미.** 대상일(`%s`)과 실행일(`%s`)이 다르다. "
              "여기서 나오는 값은 발화 품질이 아니라 재실행 시각일 뿐이라 재지 않는다"
              " (0823 이상점 1-2 계열)." % (D, now_kst().strftime("%Y-%m-%d")))
        else:
            A("- **마진 = %s − 생성시각 = %s**" % (MARGIN_ANCHOR, fmt_margin(_margin)))
            if _margin is not None and _margin < 0:
                A("- ⚠ **개장 후 실행이다** — 장전/장중 표본이 한 파일에 섞인다(§5 진입 건수 참조).")
        if _hist:
            A("")
            A("| 과거 장전 다이제스트 | 발화 마진 |")
            A("|---|---|")
            for _ymd, _sec in _hist:
                A("| `%s` | %s |" % (_ymd, "소급본(미측정)" if _sec is None else fmt_margin(_sec)))
            A("")
            A("> ⚠ 이 이력은 `evidence_*.md` 에서 되읽은 것이라 **로컬 전용**이다"
              "(`.gitignore` 대상). 다른 PC·새 클론에는 없다 — **행이 없는 것을 "
              "「마진 양호」로 읽지 말 것**(계측 4원칙 ② 미측정 ≠ 0).")
        else:
            A("- 과거 장전 다이제스트 없음 — 추이는 다음 거래일부터 쌓인다(로컬 전용 이력).")
        A("")
        A("> 🔴 **마진이 작아도 cron 을 08:58:30 이전으로 앞당기지 말 것** — "
          "`phases.md` A-2(08:55 매크로 → 레짐 확정) 증거를 잃는다. "
          "0821 실측 레짐 확정 시각은 **08:58:19** 였다. "
          "판정: `<%d초` 가 %d거래일 연속이면 §11 에 P2 로 자동 등록(사전등록 임계)."
          % (MARGIN_WARN_SEC, MARGIN_WARN_STREAK))
        A("")

    # ---- 1. 파일 인벤토리 ----
    files = discover_files(root, cfg, day)
    A("## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)")
    A("")
    if not files:
        A("**해당 날짜 토큰을 가진 파일을 하나도 못 찾았다 ⚠**")
        A("")
        A("가능성: (a) 그날 프로그램이 안 돌았다 (b) 로그가 다른 폴더에 있다 "
          "(c) 파일명에 날짜를 안 쓴다 (d) `scan_dirs` 설정이 좁다"
          "%s." % (" **(e) 오늘이 거래일이 아니다 — 위 「거래일 문맥」 참조. "
                   "이 경우 (a)~(d)를 의심할 이유가 없다**" if not is_td else ""))
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
    # [MW0602 470차 S1] `-c core.autocrlf=true` 를 **강제**한다 — 환경 중립화.
    # 이 점검은 두 곳에서 돈다: 사용자의 Windows(Git for Windows 기본 autocrlf=true)와
    # 예약작업의 리눅스 샌드박스(autocrlf 미설정). Windows 워킹트리는 CRLF, HEAD는 LF이므로
    # autocrlf 없이 세면 **같은 바이트가 "전 파일 수정됨"으로 읽힌다** —
    # 2026-08-13 517건 / 08-14 520·522·529·530건이 전부 그 오탐이었고(실제 7건),
    # 진짜 미커밋 7건이 그 노이즈에 묻혀 점검의 눈이 멀었다.
    # ⚠ `-c` 는 읽기 전용 오버라이드다. 워킹트리도 리포지터리 설정도 건드리지 않는다.
    #   ⛔ `.gitattributes` + `git add --renormalize` 는 **하지 않는다** — 리포지터리는 정상이고
    #      518파일을 건드리면 Windows 쪽 정상 동작을 깨뜨린다(470차 초안 권고를 철회한 이유).
    status = run_git(root, ["-c", "core.autocrlf=true", "status", "--porcelain"])
    dirty = [l for l in status.splitlines() if l.strip()]
    A("- HEAD `%s` · 브랜치 `%s` · 미커밋 %d건" % (head, branch, len(dirty)))
    A("- 측정: `git -c core.autocrlf=true status --porcelain` (개행 차이 제외 — 환경 중립)")
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
    spath, rows = check_invariants(root, cfg)
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
    # [MW0602 470차 S3] §5가 스스로 발견한 것(손익 검산 불일치·미청산·고아 레그)을
    # §11 적신호로 올린다. 예전에는 §5 안에만 찍혀 읽는 사람이 놓칠 수 있었다.
    day_summary_flags = day_summary(digests, cfg, L, root, day)

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
        A("**매분 루프 커버리지 %s~%s%s: %d/%d분 (%.1f%%)**" % (
            cfg["minute_loop_window"][0], cfg["minute_loop_window"][1],
            " _(진행 중 — 창을 수집 시각까지 자름)_" if window_cut else "",
            have, total, pct))
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
    # [468차 G-2] §12 표를 먼저 계산한다 — 아래 적신호 목록이 그 결과를 인용한다.
    stuck_rows = scan_stuck_indicators(root, cfg, day)
    # [MW0602 475차 후속 / G-2] DB 원천 지표를 같은 표에 합류시킨다 —
    # 판정 규칙(stuck_verdict)이 같으므로 렌더·적신호가 그대로 재사용된다.
    stuck_rows += scan_db_indicators(root, cfg, day)
    # [MW0602 476차 G-4] 임계-분포 대조 — §12b 에 렌더하고, known 없는 미도달만 적신호.
    reach_rows = scan_threshold_reachability(root, cfg, day)
    # [MW0602 485차 G-1 / 488차 계획 D] 스냅샷 정체 — §12c 에 렌더.
    snap_rows = scan_snapshot_identity(root, cfg, day)

    A("## 11. 자동 적신호 (출발점이지 결론이 아니다)")
    A("")
    flags = []
    # [MW0602 470차 S3] §5 자체 검산 결과를 최우선으로 올린다 — 손익이 배너와 다르면
    # 그 아래 모든 손익 서술이 오염된다.
    flags.extend(day_summary_flags or [])
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
        if ex:
            # [468차 F-2/A안] 보호트레일(TP1 도달 후 이익 청산)을 손절로 세지 않는다.
            # 태그 없는 구버전 로그는 '모른다'이므로 손절 쪽에 함께 넣되 적신호 문구에
            # 그 사실을 적는다 — 조용히 빼면 진짜 손절 급증을 놓친다.
            n_stop, n_prot, n_unk = exit_stop_counts(ex)
            _susp = n_stop + n_unk
            if _susp and _susp * 2 >= len(ex):
                _det = "진짜 손절 %d" % n_stop
                if n_unk:
                    _det += " · 태그없음(468차 이전 로그) %d" % n_unk
                if n_prot:
                    _det += " · 보호트레일 %d건은 제외" % n_prot
                flags.append("청산 %d건 중 손절 계열 **%d건(%.0f%%)** [%s] — 손절 준수율 확인 필요"
                             % (len(ex), _susp, 100.0 * _susp / len(ex), _det))
    try:
        if sz and en:
            smax = max(int(s["qty"]) for s in sz if s.get("qty"))
            emax = max(int(e["qty"]) for e in en if e.get("qty"))
            if smax > emax:
                flags.append("사이저 최대 %d계약 → 실제 진입 최대 %d계약 — 게이트 배수에 눌림 "
                             "(sizing_inversion_watch 대상)" % (smax, emax))
    except (ValueError, KeyError, TypeError):
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

    # [468차 G-2] 고착·무기록은 그날의 이벤트가 아니라 **누적 상태**라서 다른 적신호와
    # 성격이 다르다. 그래도 여기 올린다 — §12를 안 읽으면 영영 안 보이기 때문이다.
    for r in stuck_rows:
        if r["verdict"] == "고착":
            flags.append("고착 지표 **`%s`** — %s. 안전장치가 '켜져 있다'와 '작동한다'는 "
                         "다르다 (§12)" % (r["name"], r["note"]))
        elif r["verdict"] == "분기편향":
            flags.append("지표 **`%s`** %s — 계측이 **한쪽 분기에서만** 돈다. "
                         "값 분포가 정상으로 보여도 그 분포는 그 분기의 것이다 (§12)"
                         % (r["name"], r["note"]))
        elif r["verdict"] == "무기록":
            flags.append("지표 **`%s`** 최근 %d거래일 **기록 0건** — 계측 중단 또는 로그 문구 "
                         "변경 의심 (§12)" % (r["name"], r.get("scanned_days", 0)))
        elif r["verdict"] == "DB미접속":
            # [MW0602 476차 F-2'] 계측 중단 의심이 아니라 **수집기 환경 문제**다.
            flags.append("지표 **`%s`** — DB 접근 실패로 **미측정** (계측 중단이 아니라 "
                         "수집기 환경 문제. 라이브 프로세스 WAL 경합 가능성 — §12)" % r["name"])
    # [MW0602 476차 G-4] 임계 미도달 — **규명 안 된 것만** 올린다(known 은 §12b 표시로 충분).
    for r in reach_rows:
        if r["verdict"].startswith("미도달") and not r.get("known"):
            flags.append("임계 미도달 **`%s`** — %s, max(관측)=%s < 임계 %s (§12b). "
                         "로그가 정상이어도 이 임계를 지키는 분기는 죽어 있을 수 있다"
                         % (r["name"], r["verdict"], r["overall_max"], r["threshold"]))

    # [MW0602 485차 G-1 / 488차 계획 D] 스냅샷 정체 — **benign 이 아닌 것만** 올린다.
    # ⚠ `무기록`도 올린다(§12 규약과 동일) — 로그 문구가 바뀌면 조용히 죽기 때문이다.
    for r in snap_rows:
        if r["verdict"] == "정체" and not r.get("benign"):
            flags.append("스냅샷 정체 **`%s`** — 최근 **%d거래일 연속 같은 값**"
                         "(임계 %d, 사전등록). 로그는 매일 정상 출력되고 값도 정상 범위지만 "
                         "갱신 경로가 끊겼을 수 있다 (§12c). 마지막 관측: `%s`"
                         % (r["name"], r["streak"], r["n_warn"],
                            r["series"][-1][1] if r.get("series") else "—"))
        elif r["verdict"] == "무기록":
            flags.append("스냅샷 지표 **`%s`** 최근 창 **기록 0건** — 계측 중단 또는 "
                         "로그 문구 변경 의심 (§12c)" % r["name"])

    # [MW0602 488차 계획 A] 발화 마진 연속 미달 — 사전등록 임계로 P2 자동 등록.
    if phase == "pre":
        _m, _k = _fire_margin(day, now_kst())
        if _k == "live":
            _mf = margin_streak_flag(
                _m, read_margin_history(
                    os.path.join(root, "docs", "정기점검", "매일점검"), pcid, day))
            if _mf:
                flags.append(_mf)
            if _m is not None and _m < 0:
                flags.append("장전 점검이 **개장 후 %d분**에 실행됨 — 장전/장중 표본 혼입 "
                             "가능. §5 진입 건수로 이 시점까지의 거래를 확인할 것"
                             % ((-_m + 59) // 60))

    # [MW0602 486차 F-1] 휴장일 강등 — 은폐가 아니라 이동이다. 건수를 반드시 낸다.
    suppressed = []
    if not is_td:
        flags, suppressed = split_holiday_flags(flags)

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
    if suppressed:
        A("")
        A("**🗓 휴장(정상)으로 강등된 적신호 %d건** — %s(%s)이라 당일 데이터가 없는 것이 "
          "정상이다. 아래는 **삭제가 아니라 이동**이며, 거래일에는 그대로 적신호로 올라온다."
          % (len(suppressed), D, td_why))
        A("")
        for j, f in enumerate(suppressed, 1):
            A("- ~~%d. %s~~" % (j, f))
        A("")
        A("> ⚠ **강등 목록은 코드에 고정돼 있다**(`HOLIDAY_SUPPRESS`, 6종). "
          "미커밋 변경·PC명 태그 위반·설정 불변식 `불일치`는 휴장일에도 **강등하지 않는다** — "
          "위 본 목록에 그대로 남는다. 과잉 억제가 이 기능의 최대 위험이라 "
          "`tests/test_486_collector_holiday.py` 가 목록 크기를 불변식으로 잠근다.")
    A("")

    # ---- 12. 고착 지표 ----
    A("## 12. 고착 지표 (최근 %d거래일 상태값 분포)" % (cfg.get("stuck_indicators", {}) or {})
      .get("lookback_days", 10))
    A("")
    if not stuck_rows:
        A("`stuck_indicators` 설정이 비어 있다 — 탐지를 수행하지 않았다.")
        A("")
    else:
        A("> **왜 보는가.** 292차(CB③-P4 상시 RESTRICTED)·303차(FP-CRITICAL 상시 CRITICAL)·")
        A("> 371차(PSI 메가빈)·468차(`CORE안전` 6거래일 100% ⚠️)는 전부 **같은 실패**였다 — ")
        A("> 지표가 한쪽 값에 붙박여 죽어 있는데 매번 사람이 뒤늦게 발견했다.")
        A("> `무기록`은 그 반대 형태다: 문구가 바뀌어 계측이 조용히 끊긴 상태.")
        A("")
        A("> **세 번째 죽음 — 분기편향.** 고착·무기록 말고 *한쪽 분기에서만 도는* 계측이 있다.")
        A("> 2026-08-18 `ConfFloor` 80샘플이 전부 `ZONE_BLACKOUT` 이었고 그 80이 진입 금지 존")
        A("> 체류 **80분과 정확히 일치**했다(허용 290분 0건). `관측률` 열이 그것을 잰다 — ")
        A("> `sample_axis: \"minute\"` 지표만 대상이며, **그 지표가 사는 로그가 살아 있던 분**이 분모다.")
        A("> `\"ensemble_minute\"` 축(476차 F-8)은 분모를 `[Ensemble] dir=` 출현 분으로 좁힌다 — ")
        A("> `compute()` 안에서만 사는 지표(ConfFloor)를 로그 생존 분으로 재면 관측률이 구조적으로 낮게 나온다.")
        A("")
        A("> **관측률은 `합산 / 당일 / 최소일` 3값이다(477차 후속 F-2). 판정은 당일값으로 한다** — ")
        A("> 합산값은 계측 배포 경계를 넘으면 미측정일을 섞는다(0820 실측: ConfFloor 합산 0.72 vs")
        A("> 당일 1.00 — 08-18 배포 전 하루가 분모에 남아 있었다). `(계측 MM-DD~)` 표시는")
        A("> `measured_since` 마커(G-1) — 그 이전 일자는 분모·분자·무기록 판정에서 제외됐다.")
        A("")
        A("| 지표 | 원천 | 판정 | 관측일 | 표본 | 관측률(합산/당일/최소일) | 값 분포 | 왜 보는가 |")
        A("|---|---|---|---|---|---|---|---|")
        # [MW0602 476차 F-2'] ①(`mode=ro`)이 아닌 경로로 읽은 DB 가 있으면 명시한다.
        for _ln in db_access_notes():
            A(_ln)
        if db_access_notes():
            A("")
        for r in stuck_rows:
            mark = {"고착": "🔴 고착", "무기록": "🔴 무기록", "정상고착": "⚪ 정상고착",
                    "표본부족": "⚪ 표본부족", "변동": "✅ 변동",
                    "분기편향": "🟠 분기편향",
                    "DB미접속": "⬛ DB미접속(미측정)"}[r["verdict"]]
            dist = ", ".join("`%s`×%d" % (v, c) for v, c in r["dist"][:6]) or "—"
            if r.get("ratio") is not None:
                # [477차 후속 F-2] 합산 / **당일** / 최소일 — 판정은 당일값이 했다.
                _f = lambda v: ("%.2f" % v) if v is not None else "—"
                _rt = "%s / **%s** / %s" % (
                    _f(r["ratio"]), _f(r.get("ratio_today")), _f(r.get("ratio_min_day")))
            else:
                _rt = "—"
            _nm = "`%s`" % r["name"]
            if r.get("measured_since"):
                _nm += " (계측 %s~)" % r["measured_since"][5:]
            A("| %s | %s | %s | %d | %d | %s | %s | %s |" % (
                _nm, r.get("source") or "로그", mark, r["days"], r["n"],
                _rt, dist, r["why"]))
        A("")
        A("*판정 기준: 한 값이 100%면 `고착`, 표본 0이면 `무기록`, "
          "**당일** 관측률이 기준(0.5) 미만이면 `분기편향`(표본부족보다 **먼저** — 구조 문제라 "
          "표본이 쌓여도 해소되지 않는다. 합산·최소일 값은 참고 표시 — 배포 경계를 넘으면 "
          "미측정일이 섞인다), "
          "관측일·표본이 기준 미달이면 `표본부족`(판정 보류). "
          "**출발점이지 결론이 아니다** — 고착이 정상인 지표도 있다(예: 사고 없는 날의 CB 상태).*")
        A("")

    # ---- 12b. 임계-분포 대조 (476차 G-4) ----
    if reach_rows:
        A("### 12b. 임계-분포 대조 (threshold reachability — 최근 %d거래일)"
          % (cfg.get("threshold_reachability", {}) or {}).get("lookback_days", 14))
        A("")
        A("> **왜 보는가.** 로그가 정상 출력돼도 **그 로그가 지키려던 분기**는 죽어 있을 수")
        A("> 있다 — 1-9(앙상블 A/B, 약 3개월) · 471차 F-1(15:10 경로, 6개월) · 474차(CORE")
        A("> 그룹, 6개월)가 전부 사람이 우연히 발견했다. 판정식의 상수 임계 vs 그 임계를")
        A("> 받는 DB 컬럼의 실측 분포를 매일 대조한다. `📌` = 이미 규명·등록된 안건")
        A("> (적신호로 안 올린다 — 표시로 충분). ⚠ 관측 전용, 판정 기준 무변경.")
        A("")
        A("| 임계쌍 | 관측일 | max(관측) | 임계 | 판정 | 안건 | 왜 보는가 |")
        A("|---|---|---|---|---|---|---|")
        for r in reach_rows:
            if r["verdict"] == "DB미접속":
                mark = "⬛ DB미접속(미측정)"
            elif r["verdict"] == "표본없음":
                mark = "⚪ 표본없음"
            elif r["verdict"].startswith("미도달"):
                mark = ("📌 %s" % r["verdict"]) if r.get("known") else ("⚠️ %s" % r["verdict"])
            else:
                mark = "✅ %s" % r["verdict"]
            A("| `%s` | %s | %s | %s | %s | %s | %s |" % (
                r["name"], r["days"],
                ("%.4g" % r["overall_max"]) if r.get("overall_max") is not None else "—",
                "%.4g" % r["threshold"], mark,
                truncate(r.get("known") or "—", 60), truncate(r["why"], 90)))
        A("")

    # ---- 12c. 스냅샷 정체 (485차 G-1 / 488차 계획 D) ----
    if snap_rows:
        A("### 12c. 스냅샷 정체 (snapshot identity — 최근 %d거래일)"
          % (cfg.get("snapshot_identity", {}) or {}).get("lookback_days", 14))
        A("")
        A("> **왜 보는가 — 죽음의 네 번째 형태다.** §12 는 *한 값 고착*, §12 `무기록`은")
        A("> *계측 중단*, 475차 G-1 은 *분기편향*을 잡는다. 여기서 잡는 것은 **로그가 매일**")
        A("> **정상 출력되고 값도 정상인데 어제와 똑같은** 경우다. 실사례:")
        A("> `ensemble_calibrator.pkl` 이 2026-08-11~21 **7거래일** 갱신되지 않았고")
        A("> `[Calibration] … 복원 완료 n=…` 은 매일 정상이었다 — 사람이 pkl mtime 을")
        A("> 직접 열어보고서야 알았다(0821 이상점 1-1). ⚠ 임계 `N`은 **사전등록**이며")
        A("> 결과를 보고 조정하지 않는다(313차 ④).")
        A("")
        A("| 지표 | 관측일 | 판정 | 연속 동일 | 임계N | 마지막 관측값 | 왜 보는가 |")
        A("|---|---|---|---|---|---|---|")
        for r in snap_rows:
            if r["verdict"] == "정체":
                mark = "⚪ 정체(정상)" if r.get("benign") else "🟠 **정체**"
            elif r["verdict"] == "무기록":
                mark = "🔴 무기록"
            elif r["verdict"] == "표본부족":
                mark = "⚫ 표본부족"
            else:
                mark = "✅ 갱신"
            A("| `%s` | %d | %s | %s | %d | `%s` | %s |" % (
                r["name"], r.get("days", 0), mark,
                ("%d일" % r["streak"]) if r.get("streak") else (r.get("note") or "—"),
                r.get("n_warn", 0),
                truncate(r["series"][-1][1], 60) if r.get("series") else "—",
                truncate(r["why"], 90)))
        A("")
        _ms_snap = [r for r in snap_rows if r.get("measured_since")]
        if _ms_snap:
            A("> ⚠ **계측 시작일 이전은 미측정이지 「갱신」이 아니다**(계측 4원칙 ②): %s"
              % " · ".join("`%s` %s~" % (r["name"], r["measured_since"]) for r in _ms_snap))
            A("")

    # ---- 13. 확정 결정 레지스트리 ----
    # [475차 후속3] §5 수익률 향상방안(R-*)·§3 고도화를 쓰기 전에 반드시 볼 것 —
    # 같은 질문의 결정이 이미 있으면 신규 계측 제안이 아니라 그 채널의 판정·결정 인용이다.
    A("## 13. 확정 결정 레지스트리 (주간회의 결정 — 재론 주의)")
    A("")
    dec = scan_campaign_decisions(root, pcid)
    if dec is None:
        A("> ⚠ **미측정** — `docs/정기점검/금요일점검/%s/validation_campaign_report_*.md` 를 "
          "찾지 못했다. **\"결정이 없다\"는 뜻이 아니다** — 레지스트리 원본은 "
          "`config/settings.py:VALIDATION_CAMPAIGN_DECISIONS` 다. 그쪽을 직접 확인할 것."
          % (pcid or "?"))
        A("")
    else:
        A("> **왜 여기 있는가.** 2026-08-18 §5 R-1 이 캠페인 [25]의 확정 결정(미적용 유지, "
          "2026-08-08)을 모른 채 같은 질문의 섀도 계측을 신규 제안했다 — CLAUDE.md 가 경고한 "
          "*\"일부러 적용하지 않기로 한 FAIL 을 다음 세션이 재시도\"* 사고다. "
          "**§5 R-* · §3 고도화를 쓰기 전에 이 표와 대조하라.** 아래 키와 같은 질문이면 "
          "신규 계측 제안 금지 — 해당 채널의 판정·결정을 인용한다. "
          "결정을 바꾸는 것은 주간회의 소관이다(§9).")
        A("")
        A("- 원천: `%s` (mtime %s) — 판정(verdict)은 매주 재계산되지만 아래 **결정(decision)은 "
          "수동 확정 이력**이다. 둘을 혼동하지 말 것." % (dec["file"], dec["mtime"]))
        A("")
        if not dec["entries"]:
            A("_레지스트리 섹션은 있으나 항목이 0건 — 리포트 포맷 변경 의심. 원본을 열어 볼 것._")
        else:
            A("| 채널 키 | 결정 | 확정일 |")
            A("|---|---|---|")
            for key, decision, date in dec["entries"]:
                A("| `%s` | %s | %s |" % (key, truncate(decision, 140), date or "—"))
        A("")
    A("---")
    A("")
    A("*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — "
      "예: `findstr /C:\"강제청산\" logs\\*%s*.log` (Windows) / `grep 강제청산 logs/*%s*.log`*"
      % (toks["ymd"], toks["ymd"]))
    return "\n".join(L)


# 같은 날 같은 국면의 보존본 개수 (주간 리포트 VALIDATION_REPORT_KEEP_WEEKS 와 같은 사상)
EVIDENCE_KEEP_PER_PHASE = 3


def preserve_existing_digest(outp, keep=EVIDENCE_KEEP_PER_PHASE):
    """[MW0602 470차 S4] 같은 국면 재수집이 직전본을 **경고 없이** 덮는 것을 막는다.

    2026-08-14 실제 발생: 장후 2차 수집(16:22)이 1차본(15:53)을 덮었다(70.6KB → 71.1KB).
    그날은 차이가 EOD 로그 후반부뿐이라 손실이 작았지만, 위험한 경우는 **재기동 전후로
    두 번 수집할 때**다 — 첫 수집만 담고 있던 로그 구간이 영영 사라진다.

    CLAUDE.md "주간 산출물 위치 규약"이 기록한 사고
    (*"고정 파일명이 매주 덮어써서 2026-07-31분이 08-01 재생성에 덮였다"*)와 **같은 형태**다.
    주간 리포트는 날짜본으로 고쳤는데 일일 다이제스트는 안 고쳐져 있었다.

    동작: 기존본을 `<이름>_<mtime HHMM>.md` 로 rename 하고 stderr 에 경고.
          같은 날 같은 국면의 보존본이 `keep` 를 넘으면 오래된 것부터 지운다.
    """
    if not os.path.exists(outp):
        return
    base, ext = os.path.splitext(outp)
    try:
        stamp = datetime.fromtimestamp(os.path.getmtime(outp)).strftime("%H%M")
    except Exception:
        stamp = "prev"
    bak = "%s_%s%s" % (base, stamp, ext)
    n = 1
    while os.path.exists(bak):          # 같은 분에 두 번 돌린 경우
        bak = "%s_%s-%d%s" % (base, stamp, n, ext)
        n += 1
    try:
        os.rename(outp, bak)
        eprint("[collect_evidence] 기존본 보존: %s (덮어쓰지 않았다)" % os.path.basename(bak))
    except Exception as e:
        eprint("[collect_evidence] ⚠ 기존본 보존 실패 — 덮어쓴다: %s" % e)
        return
    # FIFO — 자동 생성물만 대상. 접미사가 시각(4자리 숫자)인 것만 센다.
    try:
        d = os.path.dirname(outp) or "."
        stem = os.path.basename(base)
        rx = re.compile(r"^%s_(\d{4})(-\d+)?%s$" % (re.escape(stem), re.escape(ext)))
        olds = sorted(f for f in os.listdir(d) if rx.match(f))
        for f in olds[:-keep] if len(olds) > keep else []:
            os.remove(os.path.join(d, f))
            eprint("[collect_evidence] 보존본 FIFO 삭제: %s" % f)
    except Exception as e:
        eprint("[collect_evidence] 보존본 정리 실패(무해): %s" % e)


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


def main(argv=None):
    ap = argparse.ArgumentParser(description="미륵이 일일 점검 증거 수집기")
    ap.add_argument("--phase", choices=["pre", "intra", "post", "all"], default="post")
    ap.add_argument("--date", default=None, help="YYYY-MM-DD / YYYYMMDD (기본 오늘 KST)")
    ap.add_argument("--root", default=None, help="리포 루트 (기본 자동탐지)")
    ap.add_argument("--out", default=None, help="파일로 저장 (기본 stdout)")
    ap.add_argument("--out-auto", action="store_true",
                    help="evidence_<PC명>-<YYYYMMDD>_<국면>.md 로 자동 저장 "
                         "(두 PC가 서로 덮어쓰지 않는다. 셸 날짜 확장에 의존하지 않아 "
                         "PowerShell/bash 어디서든 같다)")
    ap.add_argument("--discover", action="store_true",
                    help="파일 인벤토리만 출력 — 처음 한 번 돌려 경로를 확인한다")
    ap.add_argument("--max-log-mb", type=int, default=None, help="이보다 큰 로그는 건너뛴다")
    ap.add_argument("--pc", default=None,
                    help="PC명을 직접 지정한다 (예: MW0602). 환경변수 MIREUK_PC_ID 로도 같다. "
                         "생략하면 호스트명에서 자동탐지 - 예약작업.컨테이너처럼 호스트명이 "
                         "그 PC의 것이 아닐 때만 쓴다")
    args = ap.parse_args(argv)

    global _PC_OVERRIDE
    _PC_OVERRIDE = _norm_pc(args.pc)

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
        out = os.path.join(cfg["evidence_dir"],
                           "evidence_%s-%s_%s.md" % (pcid, day.strftime("%Y%m%d"), args.phase))

    if out:
        outp = out if os.path.isabs(out) else os.path.join(root, out)
        d = os.path.dirname(outp)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        preserve_existing_digest(outp, keep=EVIDENCE_KEEP_PER_PHASE)
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
    return 0


if __name__ == "__main__":
    sys.exit(main())

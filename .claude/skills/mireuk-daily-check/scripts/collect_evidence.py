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
        "강제청산", "[ExitCooldown]", "안전망", "FORCED",
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
        "margin_cap": r"\[MarginCap\]\s*(?P<dir>\w+)\s*산출=(?P<calc>\d+)계약 → 증거금상한=(?P<cap>\d+)계약으로 축소",
        # [MW0602 470차 B2] 시간대 존 전환 — 진입 가능 시간 예산을 재구성한다.
        # 추가 계측이 필요 없다. 이 로그를 구간으로 접으면 존별 체류 분수가 그대로 나온다.
        "time_zone": r"\[TimeRouter\] 시간대 전환 → (?P<zone>[A-Z_]+)\s*[:：]\s*(?P<desc>.+?)\s*$",
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
        # name: {re: 값 캡처 정규식(그룹 v), files: 파일명 부분일치, why: 왜 보는가,
        #        benign: 이 값 하나로 100%인 것이 정상인 경우(경고 대신 정보로 표시),
        #        min_samples/min_days: 전역 기준 덮어쓰기(선택)}
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
                "why": "CB 전체 상태(매분 샘플). NORMAL 고착은 정상 — 단 Phase 5 조건 ②"
                       "(CB 실발동 확인)가 여전히 미충족이라는 뜻이기도 하다",
            },
            "GuardFair_유효": {
                "re": r"\[GuardFair\][^\n]*\|\s*(?P<v>무효|ok)\s*\(",
                "files": ["retrain_eod"],
                "why": "457차 fair_valid. 무효 100%면 GuardFair 비교가 죽어 있다",
            },
            "전략판정": {
                "re": r"판정\s*:\s*(?P<v>\S+)",
                "files": ["_WARN", "_SYSTEM"],
                "min_samples": 5,   # 배너는 하루 1~2회라 전역 20건 기준이면 영영 판정 불가
                "why": "전략 상태 경보 판정. 한 값 고착이면 판정식이 무의미해진 것",
            },
            # ── [MW0602 470차] 470차 L2·B4 가 신설한 무조건 상태 샘플 2종 ──
            # 둘 다 "엣지 트리거라 마지막 상태가 열린 채 끝나던" 지표를 상태 샘플로 바꾼 것이다.
            # 배포 이전 날짜를 조회하면 `무기록`으로 뜨는 것이 정상 — 그때는 로그가 없었다.
            "ConfFloor": {
                "re": r"\[ConfFloorGuard\] state=(?P<v>\w+)",
                "files": ["_SIGNAL"],
                "benign": ["OK"],
                "why": "자동진입 하한 도달 가능 여부(매분 샘플, 470차 L2). OK 고착은 정상. "
                       "BLOCKED 고착이면 어떤 신호도 자동진입 하한을 못 넘는 상태가 "
                       "종일 지속된 것이다 — 2026-08-11 오전 88신호 전부 grade=X 가 그 사례",
            },
            "CORE준비도": {
                "re": r"\[CORE준비도\][^\n]*축퇴 (?P<v>\d+)/\d+",
                "files": ["_LEARNING", "_SYSTEM", "_SIGNAL"],
                "benign": ["0"],
                "why": "장전/장중 스케일러 refit 시 CORE 축퇴 개수(470차 B4). 0 고착이 정상. "
                       "0이 아닌 값에 고착하면 절대원칙 ③의 CORE가 상시 무력화된 것 — "
                       "2026-08-14 장전 above_vwap 6호라이즌 identity 강제가 그 사례. "
                       "⚠ 섀도 계측이다. 차단으로 승격하려면 20거래일 축적 후 "
                       "'축퇴일의 09:00~09:30 정확도'를 일자단위로 비교할 것(317차 교훈)",
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


# ------------------------------------------------------------------ 고착 지표
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
    days = sorted(by_day)[-look:]
    if not days:
        return []

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
        counts, hit_days = {}, set()
        for d in days:
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
                                v = (m.group("v") or "").strip()
                                counts[v] = counts.get(v, 0) + 1
                                hit_days.add(d)
                except (IOError, OSError):
                    continue
        n = sum(counts.values())
        dist = sorted(counts.items(), key=lambda kv: -kv[1])
        _min_n = int(spec.get("min_samples", conf.get("min_samples", 20)))
        _min_d = int(spec.get("min_days", conf.get("min_days", 3)))
        _benign = [str(b) for b in (spec.get("benign") or [])]
        if n == 0:
            verdict, note = "무기록", "%d거래일 전체에서 0건 — 로그 문구 변경 또는 계측 중단" % len(days)
        elif len(hit_days) < _min_d or n < _min_n:
            verdict, note = "표본부족", "관측 %d일 · %d건 (기준 %d일 · %d건)" % (
                len(hit_days), n, _min_d, _min_n)
        elif len(dist) == 1:
            # 한 값 100%가 **정상인** 지표가 있다(사고 없는 날의 degraded=OFF 등).
            # 그것까지 적신호로 올리면 §12 전체가 늑대소년이 된다 — 표에는 남기되
            # 경고로는 올리지 않는다.
            if dist[0][0] in _benign:
                verdict = "정상고착"
                note = "`%s` 100%% (%d건 / %d일) — 기대값" % (dist[0][0], n, len(hit_days))
            else:
                verdict = "고착"
                note = "`%s` 100%% (%d건 / %d일)" % (dist[0][0], n, len(hit_days))
        else:
            verdict, note = "변동", "%d개 값" % len(dist)
        rows.append({"name": name, "why": spec.get("why", ""), "days": len(hit_days),
                     "n": n, "dist": dist, "verdict": verdict, "note": note,
                     "scanned_days": len(days)})
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
    A("| 증거금 상한(`[MarginCap]`) | %d |" % len(mc))
    A("")
    A("> **집계 단위 — 승패·손익은 `포지션`으로 센다. `레그`가 아니다.**")
    A("> 이익 포지션은 TP1/TP2/TP3로 쪼개져 여러 레그가 되고 손실 포지션은 전량청산 한 레그가 된다 — "
      "레그로 세면 **없는 인과가 만들어진다**(417차가 정확히 그 사고였고, 470차 리포트에서 재발했다).")
    A("")

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
        A("**포지션 단위** — 진입 시각으로 묶었다.")
        A("")
        A("| 진입 | 방향 | 계약 | 레그 | 합계pt | 합계원 | 청산 사유 체인 |")
        A("|---|---|---|---|---|---|---|")
        for p in positions:
            e = p["entry"]
            chain = " → ".join(
                "%s(%s)" % ((r.get("reason") or "?").strip(), r.get("pt")) for _k, r in p["legs"]
            ) or "_미청산_"
            A("| %s | %s | %s | %d | %s | %s | %s |" % (
                e.get("hhmm"), e.get("dir"), e.get("qty"), len(p["legs"]),
                ("%+.2f" % p["pt"]) if p.get("pt") is not None else "?",
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
        banner_won = None
        for bline in banner or []:
            bm = re.search(r"오늘\s*PnL\s*[:：]\s*([+-]?[\d,]+)\s*원", bline)
            if bm:
                banner_won = _won_to_int(bm.group(1))
                break
        if banner_won is not None:
            diff = tot_won - banner_won
            if abs(diff) <= 2:      # 반올림 1원 차는 정상
                A("> ✅ **검산 일치** — §5 합계 `%s원` ≒ 전략경보 배너 `%s원` (차 %d원)"
                  % (format(tot_won, "+,d"), format(banner_won, "+,d"), diff))
            else:
                A("> 🔴 **검산 불일치** — §5 합계 `%s원` vs 전략경보 배너 `%s원` (**차 %s원**). "
                  "어느 한쪽이 레그를 빠뜨렸다는 뜻이다. 리포트에 손익을 옮겨 적기 전에 원인을 찾아라."
                  % (format(tot_won, "+,d"), format(banner_won, "+,d"), format(diff, "+,d")))
                ds_flags.append(
                    "§5 손익 `%s원` ≠ 전략경보 배너 `%s원` (차 %s원) — 집계 누락 의심"
                    % (format(tot_won, "+,d"), format(banner_won, "+,d"), format(diff, "+,d")))
            A("")
        else:
            A("> ⚠ 전략경보 배너에서 `오늘 PnL` 을 못 찾아 **검산하지 못했다.** "
              "장중이면 정상(배너는 15:40 마감 시 발행). 장후면 배너 문구 변경을 의심하라.")
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
        if mc:
            caps = {}
            for m_ in mc:
                caps["%s→%s" % (m_.get("calc"), m_.get("cap"))] = \
                    caps.get("%s→%s" % (m_.get("calc"), m_.get("cap")), 0) + 1
            A("| 증거금 `[MarginCap]` | %d | %s |" % (
                len(mc), ", ".join("`%s계약`×%d" % (k, v)
                                   for k, v in sorted(caps.items(), key=lambda kv: -kv[1]))))
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
        if mc:
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
    day_summary_flags = day_summary(digests, cfg, L)

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
        hit_flat = any(("강제청산" in dg.quoted or "FORCED" in dg.quoted or "FLAT" in dg.quoted)
                       for dg in digests)
        if not hit_flat:
            flags.append("장후인데 **강제청산(15:10) 흔적을 못 찾았다** — 절대원칙 1 확인 필요 "
                         "(포지션이 없었을 수도 있다. 원본으로 구분할 것)")
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
        elif r["verdict"] == "무기록":
            flags.append("지표 **`%s`** 최근 %d거래일 **기록 0건** — 계측 중단 또는 로그 문구 "
                         "변경 의심 (§12)" % (r["name"], r.get("scanned_days", 0)))

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
        A("| 지표 | 판정 | 관측일 | 표본 | 값 분포 | 왜 보는가 |")
        A("|---|---|---|---|---|---|")
        for r in stuck_rows:
            mark = {"고착": "🔴 고착", "무기록": "🔴 무기록", "정상고착": "⚪ 정상고착",
                    "표본부족": "⚪ 표본부족", "변동": "✅ 변동"}[r["verdict"]]
            dist = ", ".join("`%s`×%d" % (v, c) for v, c in r["dist"][:6]) or "—"
            A("| `%s` | %s | %d | %d | %s | %s |" % (
                r["name"], mark, r["days"], r["n"], dist, r["why"]))
        A("")
        A("*판정 기준: 한 값이 100%면 `고착`, 표본 0이면 `무기록`, "
          "관측일·표본이 기준 미달이면 `표본부족`(판정 보류). "
          "**출발점이지 결론이 아니다** — 고착이 정상인 지표도 있다(예: 사고 없는 날의 CB 상태).*")
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

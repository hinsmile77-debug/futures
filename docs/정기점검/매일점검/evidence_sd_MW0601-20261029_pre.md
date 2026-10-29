# 신동 일일 점검 증거 — MW0601 / 2026-10-29 / pre

- 수집 시각: 2026-10-29 08:53:22 · PC: claude (override) · 거래일: 예 (평일) · 직전 거래일: 2026-10-28
- 브랜치: `Sindong2-V4` · HEAD: 25d2a916 2026-10-28 18:39:18 +0900 [MW0601] 727차 후속2-보정: F-SD-5 테스트 — events_since_record 없는 갈래(Sindong-V4)에서도 통과
- `.git/index.lock`: 없음
- 당일 로그 파일: 10개
- 현재 거래주체 파일: SHINDONG (set_at 2026-10-21T09:05:30 · dashboard)

## 0. 자동 적신호 (출발점이지 결론이 아니다)

- 없음

## 1. 설정 (config/settings.py — 엔진·주체는 기동 시 1회 읽힌다)

| 키 | 값 |
|---|---|
| `MIREUK_ENGINE` | `"off"` |
| `PRINCIPAL_ALLOWED` | `("SHINDONG", "PETER")` |
| `PRINCIPAL_DEFAULT` | `"SHINDONG"` |
| `LIGHT_PASS_DRY_RUN` | `False` |
| `PRINCIPAL_SHINDONG_ENABLED` | `True` |
| `SHINDONG_LIVE_QTY` | `3` |
| `SHINDONG_STOP_RISK_QTY_ENABLED` | `True` |
| `SHINDONG_STOP_RISK_PCT` | `0.020` |
| `SHINDONG_STOP_RISK_BUF_PTS` | `0.5` |
| `SHINDONG_STOP_RISK_FLOOR_PTS` | `4.0` |
| `MAX_CONTRACTS` | `3` |
| `LIVE_OPERATING_CAPITAL_KRW` | `30_000_000` |
| `CB_CONSEC_STOP_LIMIT` | `3` |
| `PETER2_FOLLOW_MODE` | `"live"` |
| `SHINDONG_REPORT_MAIL_ENABLED` | `False` |
| `SHINDONG_DAILY_MAIL_ENABLED` | `True` |

## 2. 로그 계수 (당일 · 중복 기록은 1회로)

| 항목 | 건수 | 기대 | 판정 | 첫 줄 |
|---|---|---|---|---|
| 기동 — 신동 주체 초기화(미륵 엔진 off) | 2 | 1+ | 정상 | 08:40:45 [INFO] SYSTEM: [System] 신동 주체 초기화 (미륵 엔진 off) |
| `[Engine] 미륵 엔진=off` | 1 | 1+ | 정상 | 08:40:45 [WARNING] SYSTEM: [Engine] 미륵 엔진=off — 예측·학습·재학습·미륵 진입·미륵 장후 항목 생략, 경량 분봉 패스 사용 (거래주체=신동) |
| **미륵 진입 거부 `[MireukOff]`** (1건이라도 = 도달 경로 결함) | 0 | 0 | 정상 |  |
| 08:45 휴면 분기 `[EarlyWarmup] 미륵 휴면` | 1 | 1+ | 정상 | 08:45:23 [INFO] SYSTEM: [EarlyWarmup] 미륵 휴면 — 스케일러 재적합 생략(미륵 상태 파일 보존) |
| 08:45 실시간 선행 구독 | 1 | 1+ | 정상 | 08:45:23 [INFO] SYSTEM: [EarlyWarmup] Cybos RT 08:45 선행 구독 시작 (프리장 봉 15봉 확보) — 개장 대비 +23.2s |
| 재학습 생략 `[GBM-64] 미륵 휴면`(있으면 정상) | 0 | - | 관찰 |  |
| 주체 전환·거부 `[Principal]` | 0 | - | 관찰 |  |
| 긴급 알림 메일 발송 | 0 | - | 관찰 |  |
| 재기동(세션) | 1 | - | 관찰 | 08:40:53 [INFO] SYSTEM: [Session] 재기동 #1 \| cause=STARTUP |
| Traceback | 0 | 0 | 정상 |  |
| 런처 입구 점검 `[SindongCheck] result=` (logs/Mireuk_batch) | 1 | 1+ | 정상 | [SindongCheck] result=pass |

- ERROR/CRITICAL: 전체 0줄 · 확정된 고정 경고 0줄 · HealthPolicy CRITICAL 0줄 · **그 밖 0줄**

## 3. 장전 준비 (전일 신동 EOD · 맥점 · 자본 · 동기화 · 예약작업)

- 전일(2026-10-28) 신동 EOD 마커: `completed: 2026-10-28T15:55:01 exit=0`
- 맥점 이력 캐시 `last_date`: `2026-10-28`
- 08:50 맥점: `08:50:23 [INFO] SYSTEM: [LEVELS 08:50] ref=940.00 ATR=49.8 \| 구조 상방 943(1) 946(1) 951(1) \| 하방 938(1) 934(1) 902(1) [후보 18개 · 위 3 / 아래 15]  ※참고용 — 검증상 무작위와 구분 안 됨`
- 09:30 맥점: 없음
- 자본(기준자본·실운영금): `08:40:53 [INFO] SYSTEM: [Capital] 기준자본=50,000,000원(target) \| 실운영금=30,000,000원 \| 실제잔고=30,626,731원 \| 괴리=-38.7% \| base_risk=1,500,000원(3.0%) \| 일일한도=600,000원(2.0%) \| MA…`
- ProfitGuard 원화 임계: `08:45:53 [INFO] TRADE: [ProfitGuard] 원화 임계 배율 ×1.50 → ×1.00 (신동 2계약) — L1 발동 2,000,000원 · L2 중단 4,000,000원 · L3 1,000,000원 · L4 1,500,000원`
- 브로커 동기화: `08:40:53 [INFO] SYSTEM: [BrokerSync] startup sync 무포지션 확인(blank rows): FLAT -> FLAT (armistice cleared)`
- 피터2 모드: `08:40:59 [INFO] SYSTEM: [Peter2] 모드=shadow (거래주체=신동)`
- 예약작업 상태: 미측정(Windows 가 아님 — Cowork 샌드박스)

### 3-b. 단일 인스턴스 (main.py 1벌 · 미륵 런처 휴면)

- 실행 중 main.py: 미측정(Windows 가 아님)
- 미륵 런처 예약작업(start_mireuk.bat): 미측정
- 당일 런처 로그: launcher_20261029_084000_770.log=Sindong
- `[SingleInstance] 중복 기동 거부`: 0건

### 3-c. 피터2 수집기 (하트비트 · X 탭 · 장후 사료)

- 하트비트: last_post=`2026-10-29T08:53:08` · last_ok=`2026-10-29T08:53:08` · articles=1 · off_search=False · error=None
- X 탭 계수: 미측정(확장 1.2.0 이전이거나 수신기 미갱신)
- 수신기 로그: NEW 1 · PAGE_ERROR 0 · OFF_SEARCH 진입 0 · TABS 중복 0
- 장후 사료 확정 `peter_paste` 최근일: `2026-10-28`
- 직전 거래일 삭제 탐지 `2026-10-28.eod_ids.json`: 있음

## 6. 미결 관측 · 장중 확인 항목 (NEXT_TODO 상단)

- NEXT_TODO 끝 400줄의 열린 항목 184건 · 태그 `[로그]` 5 · `[경보]` 0 · `[화면]` 3 · **태그 없는 「장중」 항목 20건**
  - - [ ] `docs/정기점검/매일점검/_wrongdate_evidence_sd_MW0601-20261025_pre.md` — 10-26 장전 날짜 오류 보존본(리포트 2-1 인용). 수집기 KST 수정(e71b4e27) 뒤 재발 없으면 보존·삭제 결정 `[로그]`.
  - - [ ] O-699 `[로그]` 10-27 장전: `[CybosMarginQty] 조회 성공(당일 첫 회)` 원값(매도·매수 신규가능)이 예탁금 대비 상식적인가 · `[Capital]` 「장시작 가능」 숫자 전환 · `판독 의심` 0건 · `조회 실패 … 11298` 0건
  - - [ ] O-700 `[로그]` 다음 신동 보유일: 대체 대조 WARNING 꼬리 「수급 타이머 다음 발화까지」가 수 초 이내 + `[ShindongPerf]` 정규 대조 간격 59–62초 몰림 → 경합 확정 시 문턱 60→90초 수정안 상정(신동 보유관리 경로 — 별도 승인)
  - - [ ] **(관찰)** 수집기 §0 「수동 개입」 적신호가 다음 거래일 장후 증거에서 0건/1건+를 올바로 내는지 — O-702 와 같은 축. `[로그]`
  - - [ ] **(관찰)** 10-28 15:55 장후 snapshot 머리가 `확정 (완결 봉 15:44)` 이고 외인 경로 끝이 15:34 인지. 만기일(11-12)은 15:19 봉으로 확정되는지. `[로그]`
  - - [ ] **(관찰)** 사다리 서버 화면이 15:52 적재 직후 정규봉으로 바뀌어도 이상 없는지(15:08 → 15:44 봉 확장). `[화면]`
  - - [ ] **(이월) 726차 — §3-V V-1028-7** 724차 후속2 사다리 해설 패널([화면]) — 사용자 확인 대상.
  - - [ ] **(이월) 727차 — §3-V V-1028-7 / O-707** `[화면]` 724차 후속2 사다리 해설 패널 — 소스는 확인됐으나(shindong.db 기준·v3 미표기) 실제 화면 렌더링 미확인. 급하지 않음.
  - - [ ] **O-p1 (신규, 확인 필요)** 피터2 오프셋 보정값(A056B) 08:58:09 spread=0.31>0.30 "불안정"(표본 13개) — 09:30 전후 재측정에서 0.30 이하로 복귀하는지 장중 점검이 판정.
  - - [ ] **O-p2 (신규, 확인 필요)** 캐너리 z-경고 피처 수 08:59:09 10개로 재상승(08:55 임계접촉→재적합→08:59 8개 이후) — 09:10~09:15 재측정값이 8개 이하로 복귀하는지 장중 점검이 판정.
  - - [ ] **O-p3 (신규, 확인 필요)** 옵션체인 재수집이 09:01:26(개장 1분 후)에 완료 — 과거 타이밍 기준 판정 기록 부재. 다른 평일과 비교해 정상 범위인지 장중/다음 점검이 확인.
  - - [ ] **1-3 (P2, 장후 판정 대기)** 피터2 오프셋 보정값(`PETER2_OFFSET_TOL_PT`) spread가 08:58~11:23 구간 n=30까지 쌓여도 0.31~0.40 사이로 전혀 0.30 이하로 내려오지 않음 — 장후 점검이 하루 전체 추이로 "안정화됐는지/계속 불안정했는지"…
  - - [ ] **O-p2 (판정보류 → 장후)** 캐너리 z경고 재상승 — 09:00~12:26 구간 재측정 로그 0건. 장후 점검이 `grep -c "Canary" logs/20261019_*.log`로 하루 전체 측정 횟수 재확인하고, 장중 미측정이 설계상 정상(1회성 장전 체크)인지 `main.py`…
  - - [ ] **698-1 (10-20 장중·장후)** RATE 우리 요청 사이 rem 감소가 1로 떨어졌는가(① 외부 소진 중앙 ≤ 3). 아니면 MW0602 중지 미반영 → 사용자 확인.
  - - [ ] **698-1 장중 중간 관측(보강)** 08:30~12:45 15분 창 17개 중 16개 외부소진 0회(1개 창만 1회) — 전일 중앙값 27회 대비 뚜렷한 개선 지속. 최종 판정은 10-26 장후까지 유지.

## 7. 오늘 커밋

- 없음

## 8. 변경 반영 검증 — 대장 후보 (스킬 §3-V)

- 창: 직전 거래일 2026-10-28 15:40 KST 이후 — 어제 장후 자동조치(17:23)·저녁·밤·오늘 커밋을 모두 덮는다
- 커밋 13건 · 검증 대상(코드·도구 포함) **10건** · 문서·산출물만 3건(대장 제외 — 점검 산출물 커밋 등)

| 커밋 | 시각 | 구분 | 제목 | 바꾼 파일(코드) |
|---|---|---|---|---|
| f872026b | 10-28 16:24 | 도구·화면·점검 | [MW0601] 725차 후속6: 신동2 poll 라우팅 — 무보유 position 헛호출·같은 이벤트 재발화 차단 | `.claude/skills/shindong2/SKILL.md`, `scripts/shindong2_live.py`, `scripts/shindong2_run.ps1` … 외 1개 |
| 82c583b2 | 10-28 16:30 | 도구·화면·점검 | [MW0601] 725차 후속7: 신동2 이벤트 — MAIN 진입·1차 청산·청산을 「상대의 수」 이벤트로 생성 | `.claude/skills/shindong2/SKILL.md`, `scripts/shindong2_live.py`, `tests/test_725f_shindong2_poll_routing.py` |
| e432cd27 | 10-28 16:59 | 실행경로·도구·화면·점검·문서·산출물 | [MW0602] F3 이식: 현물 외인 방향 = 금액(백만원) → Sindong2-V4 (원 Sindong-V4 5c396b4) + 이식메모 | `.claude/skills/shindong2/SKILL.md`, `scripts/foreign_flow_pit_review.py`, `scripts/shindong2_live.py` … 외 6개 |
| 3b4dd482 | 10-28 17:01 | 도구·화면·점검 | [MW0601] 725차 후속8: 신동2 poll — 장중 슬롯(:00·:30)에서 intraday 에 양보 · 잠금 대기 제거 | `.claude/skills/shindong2/SKILL.md`, `scripts/shindong2_run.ps1`, `tests/test_725f_shindong2_poll_routing.py` |
| 7d79e35b | 10-28 17:02 |  | [MW0601] Merge origin/Sindong2-V4 — MW0602 F3 이식(e432cd27, 현물 외인 방향 = 금액) 동기화 | — |
| c019c457 | 10-28 17:22 | 도구·화면·점검 | [MW0601] 725차 후속10: 신동2 10-28 검토 3건 — 장중 08:45 시가 보정 · manage 대상 기록 · 헤드리스 고지·마감 검사 | `.claude/skills/shindong2/SKILL.md`, `scripts/shindong2_live.py`, `scripts/shindong2_run.ps1` … 외 3개 |
| 7e43748c | 10-28 17:26 | 도구·화면·점검 | [MW0601] 725차 후속11: 08:45 시가 보정 — open_bar_ts 열이 없는 premarket_levels 폴백(Sindong-V4 이식 대비) | `tests/test_725g_shindong2_open_manage_headless.py`, `tools/maekjeom_ladder/ladder_data.py` |
| d8a77fba | 10-28 17:28 | 도구·화면·점검 | [MW0601] 727차 후속: 장후 자동조치 — G-10(피터2 확장 판 로그) | `tests/test_725_peter2_restored_pinned_tab.py`, `tests/test_727_peter2_ext_version_log.py`, `tools/peter2_live/extension/background.js` … 외 2개 |
| 577ef3d4 | 10-28 18:31 | 도구·화면·점검 | [MW0601] 727차 후속2: F-SD-5 [ForeignCutCheck] — 외인 선물 마감 누계 반영 여부를 장후 매 회 1줄 | `scripts/shindong2_live.py`, `tests/test_640_plain_and_warnings.py`, `tests/test_fsd5_foreign_cut_check.py` |
| 25d2a916 | 10-28 18:39 | 도구·화면·점검 | [MW0601] 727차 후속2-보정: F-SD-5 테스트 — events_since_record 없는 갈래(Sindong-V4)에서도 통과 | `tests/test_fsd5_foreign_cut_check.py` |

- 직전 거래일(2026-10-28) 「변경 반영 검증」 열린 행 0건
- 오늘 앞 국면(2026-10-29) 리포트 없음 — 이월 미결 미측정


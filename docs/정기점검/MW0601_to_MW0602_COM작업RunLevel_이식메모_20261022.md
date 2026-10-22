# COM 예약작업 RunLevel 공용 판정기 — MW0601 → MW0602 이식 메모 (2026-10-22)

> 원 작업: v9-dev(MW0601) 705차 후속 `689d1956`
> dev 반영: 이 메모와 같은 커밋(선별 이식). **매매 코드 무변경 · 등록된 예약작업 무변경.**

## 1. 한 줄 요약

COM을 여는 예약작업 설치 스크립트가 RunLevel을 **각자 다른 고정값**으로 들고 있던 것을
공용 판정기 `scripts/lib/ComTaskRunLevel.ps1` 하나로 모았다. **MW0602에서는 판정 결과가
Highest라 종전과 같다** — 지금 돌고 있는 작업은 그대로 두면 된다.

## 2. 왜

RunLevel이 API 세션(CpStart/DibServer)과 다르면 COM이 로그인 안 된 DibServer를 새로 띄워
`IsConnect=0`으로 **크래시 없이 매일** 실패한다(MW0602 2026-09-17 정규수집 · MW0601
2026-09-21 – 10-02 백필 8거래일). 그런데 그 수준을 정하는 것은 BROKER가 아니라
**① UAC(EnableLUA) ② 세션을 띄운 방식**이었다.

| PC | UAC | 세션 | 필요한 RunLevel | 판정기 결과 |
|---|---|---|---|---|
| MW0602 | 켜짐 | CREON 런처 자기승격 | **Highest** (647차 실측) | Highest |
| MW0601 | **꺼짐**(EnableLUA=0) | — | 무관(두 레벨이 같은 토큰) | Highest(UAC 재활성 대비) |

MW0601이 BROKER=creon인데 Limited 작업이 정상 동작해 「규칙이 틀렸다」로 보였던 것(704-6)은
UAC가 꺼져 있었기 때문이다.

## 3. 판정 순서

1. UAC 꺼짐 → 오늘은 동치. UAC를 다시 켜도 맞는 쪽(아래 3)
2. `CpStart.exe` 실행 중 → 그 프로세스 토큰의 **실측 승격 여부**
3. BROKER=creon → Highest / cybos → `'Cybos Plus'` 기동 작업의 RunLevel(없으면 Limited)
4. 판정 불가 → **등록 거부**(추측 금지)

`-RunLevel`을 직접 주면 그 값이 이기고, 판정과 다르면 WARN을 찍는다.
Highest 판정인데 비관리자 셸이면 등록 전에 멈춘다(종전 사전점검과 같은 역할).

## 4. dev에 들어온 것

| 파일 | 변경 |
|---|---|
| `scripts/lib/ComTaskRunLevel.ps1` | 신설 — 판정기(순수 ASCII) |
| `scripts/audit_com_task_runlevel.ps1` | 신설 — 읽기 전용 전수 대조. OK / EQUIV(UAC 꺼짐이라 영향 없음) / MISMATCH. exit 0/1/2 |
| `scripts/option_flow_backfill_task.ps1` | BROKER 규칙 → 판정기 |
| `scripts/regular_collect_task.ps1` | 기본 Highest 고정 → 판정기 (MW0602 2026-09-17 주석은 보존) |
| `scripts/strike_investor_snapshot_task.ps1` | 기본 Limited → 판정기 (647차가 `-RunLevel Highest`로 등록한 것과 같은 값이 이제 기본) |
| `scripts/backfill_option_flow.py` | 미접속 메시지에 UAC 상태 병기 |
| `TASK_OPTION_BACKFILL_INSTALL.bat` | 주석 |
| `tests/test_705_com_task_runlevel.py` | 신설 6건 — 설치기 전수 배선 · 판정 순서 · 거부 · ASCII |
| `tests/test_595_*` · `test_655_*` | 사전점검 위치 단언을 판정기 함수명으로 / BROKER 단언을 판정기로 |

**v9-dev에만 있고 dev에는 안 들어온 것**: `eod_session_cleanup.ps1`(MW0601 전용 장후 세션
정리) · `broker_switch/switch_broker.ps1`(감사 5단계 자동 실행). dev에 그 파일들이 없다.

검증(dev 워크트리): 705·655·595·704 **55 passed · 1 skip**(MW0601 전용 정리 스크립트 검사).

## 5. MW0602에서 할 일

**필수 아님.** 등록된 작업은 바꾸지 않았다. 확인만 원하면:

```
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\audit_com_task_runlevel.ps1
```

기대: `UAC(EnableLUA)=on` · `resolved: Highest` · `\Mireuk\` COM 작업 전부 `OK`.
`MISMATCH`가 나오면 그 작업은 지금도 매일 실패하고 있다는 뜻이다 — `LastTaskResult`로
교차 확인 후 해당 `*_task.ps1`로 재등록(관리자 PowerShell).
`resolved`가 Highest가 아니면 판정 근거(`basis=`)를 보고 **재등록하지 말고** MW0601에 알릴 것.

# 신동 주체 전환 — 이 PC 검증 기록 (MW0602 · 2026-10-25 휴무일 장전 · 661차)

- 브랜치: `Sindong-V4` · 전환 대상 코드 `7be11df`(660차 + 브랜치 역할 문서)
- 결과: **전환 완료** — `MIREUK_ENGINE="off"` · `PRINCIPAL_LOCK="SHINDONG"` · `LIGHT_PASS_DRY_RUN=False`
- 다음 기동(2026-10-26 장전)부터 적용된다(설정은 기동 때 한 번만 읽는다).

## 단계별 결과

| 단계 | 결과 | 근거 |
|---|---|---|
| 1. 재기동 확인 | 🟡 **대체 검증** — 휴무일이라 실제 Cybos 기동은 못 했다. 격리 사본(저장소+data 4GB)에서 py37_32·offscreen·가짜 브로커로 실제 `TradingSystem` 을 띄우고 10/23 실분봉 30개를 넣었다 | `스모크_off_py37_32.txt` |
| 2. 신동 장후 작업 | ✅ `\Mireuk\Shindong_EOD_1555` 등록(평일 15:55) · 수동 실행 exit=0 · **예약작업 경로 실행 LastTaskResult=0**(인자에 `--date 2026-10-23 --no-wait` 를 잠시 붙였다가 원복) | `logs\shindong_eod_20261025.log` · `data\shindong_eod_done_20261023.txt` |
| 3. 병행 건식 대조 | ⛔ **미실시** — 장이 열린 날에만 가능. 가짜 브로커로는 미륵 파이프라인이 로그인 후 객체(`investor_data`·`macro_fetcher`) 부재로 완주하지 못해, 건식 대조가 30/30 「파이프라인 미완주」 불일치로 정확히 잡아냈을 뿐 비교값이 없다 | `스모크_full_dry_py37_32.txt` |
| 4. 장후 재생 | ✅ **8거래일 전부 PASS**(10/14~10/23) — 12/12 부품 · ATR 상대오차 ≤10% 98.8~100% · CB④ 일치(전부 0 vs 0) · 봉당 최대 0.3ms | `replay_YYYYMMDD.md` |
| 전환 | ✅ 설정 3종 · `strategy_events` id=128 `METRIC_REDEFINITION` · ✅ 미륵 재학습 예약작업 `\Maitreya_EODretrain` **Disabled**(사용자 관리자 실행) |

### 스모크(off) 요약 — 클라우드 결과와 동일

init 16.0s · 파이프라인 0회 · 봉당 최대 55ms · 경량 ATR 2.8486 · `grab()`+paint 정상 · **ERROR 0** ·
`[MireukOff]` 미륵 진입 거부 · 주체 전환 거부(PRINCIPAL_LOCK) · 재학습 spawn 거부.

### 전체 테스트(Windows · base anaconda pytest)
전환 전(격리 사본, full) **17 failed / 2867 passed** vs 전환 후 **19 failed / 2865 passed**. 새 실패 2건은
`test_616_trade_principal.py` 의 파일 기본값 테스트가 `PRINCIPAL_LOCK` 에 가려진 것 — 픽스처에서 고정을 풀어 해소(26 passed).
남은 17건은 전환 전과 **동일 목록**이다. 신규·관련 테스트 61건은 전부 통과.

### 재생 판정 ③ 의 한계
8일 모두 CB④ 발동 봉이 경량·미륵 **둘 다 0** 이라 「발동 수 일치」는 발동일 표본이 없다. 고변동일에 다시 볼 것.

## 이 PC에서 드러난 결함 3건(수정 완료)

| # | 결함 | 수정 |
|---|---|---|
| W1 | `light_pass_replay.py` 가 결과를 콘솔에 찍는 줄에서 `—` 를 cp949 로 못 써 **판정 직후 exit=1 로 죽음**(`--out` 파일도 미기록). Linux(UTF-8)에선 안 보였다 | 파일 먼저 기록 + stdout UTF-8 재설정 |
| W2 | `shindong_eod.py` 콘솔 로그 핸들러가 같은 이유로 logging 오류 출력(실행은 계속) | stdout UTF-8 재설정 |
| W3 | 🔴 `-DisableMireukRetrain` 이 `MireukiEODRetrain` 이름만 찾음 — **이 PC 작업명은 `\Maitreya_EODretrain`** 이라 전환일에 아무것도 끄지 못하고 지나갔을 것 | 두 이름 모두 매칭 · 권한 거부 시 관리자 재실행 안내 후 exit 1 |

## ✅ (완료 2026-10-25) 미륵 재학습 예약작업 비활성 — 관리자 권한이 필요했던 조치

`\Maitreya_EODretrain` 은 `RunLevel=Highest` 로 등록돼 있어 일반 권한으로는 끌 수 없다(Access denied).
**관리자 권한 명령 프롬프트**에서:

```
# 관리자 PowerShell — 현재 폴더 실행은 & + 전체 경로
& "C:\Users\pc1\PycharmProjects\futures\TASK_SHINDONG_EOD_INSTALL.bat" -DisableMireukRetrain
```

`[OK] disabled: \Maitreya_EODretrain` 이 나와야 한다. 끄지 않으면 월요일 15:50 에 미륵 재학습이 돌아
휴면 중 미륵 모델 파일을 덮어쓴다(「되살림 = 마지막 실가동 상태」 원칙 위반). 맥점 캐시는 신동 EOD 가 맡으므로 끄는 쪽이 안전하다.

## 전환 첫날(10/26) 확인 — `dev_memory/NEXT_TODO.md` 660 의 6번

`[Engine] 미륵 엔진=off` · `[LightPass] 경량 ATR … 시작` · `raw_candles` 380봉 전후 · 08:50/09:30 맥점 ·
`[MireukOff]` ERROR 0건 · CB 진입 정지 사유에 파이프 지연 없음 · 15:10 `[ForceExitPass]`(보유 시) ·
장후 `[DailyClose] 미륵 휴면 …` 1줄 · 15:55 `shindong_eod_done_20261026.txt` exit=0.

⚠ 문서는 「첫날 1계약」을 권장하지만 `SHINDONG_LIVE_QTY` 등 수량 설정은 **바꾸지 않았다**(사용자 결정 사항).

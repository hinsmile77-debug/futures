# EOD 리포트 "1일차" 고정 버그 딥다이브 + 수정

작성일: 2026-07-06
관련: 사용자 요청 "EOD 리포터 무작위 샘플 딥다이브" 후속 (v9-dev 브랜치 작업 —
[[project_v9_dev_branch_split]] 규칙에 따라 dev_memory 4개 파일은 건드리지 않고 여기에 기록)

배경: `data/daily_reports/*.txt` 무작위 7건(05-07~07-06)을 읽어보니 6건이 전부
`(1일차)` / `데이터 부족(1일)` / `롤링20일: 누적 +0원`으로 찍혀 있었다. 실제로는
2026-05-07부터 07-06까지 두 달째 매일 자동매매(모의투자)가 돌고 있었는데도 리포트
상단 요약이 하루도 안 지난 것처럼 고정되어 있어 딥다이브했다.

---

## 1. 근본원인 — "현재 버전" 포인터가 두 곳에 따로 존재

```
strategy_versions.is_current = 'v1.2'   (scripts/qa_strategy_seeder.py가 2026-05-07
                                          18:37에 더미 3버전을 등록하며 남긴 값 —
                                          실제 배포가 아니라 QA 테스트 데이터)
config/strategy_params.py: PARAM_HISTORY[-1]["version"] = 'v1.0'  (05-07 이후
                                          한 번도 append된 적 없이 고정)
```

`main.py:8429`(라이브 스냅샷 기록 시 사용하는 활성 버전)는 `PARAM_HISTORY[-1]`을 읽어
매일 `v1.0` 태그로 스냅샷을 저장했고, `daily_exporter.py`/`get_current_version()`은
`strategy_versions.is_current`(=`v1.2`)를 기준으로 조회했다. 즉 실거래 데이터는
`v1.0`에 33일치가 쌓였는데, 리포트는 `v1.2`(QA 더미 스냅샷 1건, 05-07)만 보고 있었다.

DB 실측:
```
strategy_versions:  v1.0(비활성) / v1.1(비활성) / v1.2(is_current=1, QA 더미)
strategy_live_snapshots:
  v1.0 → 33일치, 2026-05-07~07-06 (실제 손익 등락 존재: 06-26 +562만, 07-01 -776만 등)
  v1.1 → 1건 (QA 더미, 05-07)
  v1.2 → 1건 (QA 더미, 05-07)
```

`get_rolling_metrics('v1.2')`는 스냅샷이 1건뿐이라 `len(pnls)<2`로 조기 반환 →
`cum_pnl` 키 자체가 없어 `daily_exporter`가 `0`으로 채움 → "누적 +0원"이 영원히 출력.
`_get_live_days('v1.2')`도 distinct snapshot_date=1이라 "1일차" 고정.

CUSUM 값(예: 07-01 `CRITICAL 7764009.50`)은 실제 v1.0 거래 데이터와 정확히 일치 —
CUSUM 자체는 정상 동작 중이었고, 문제는 같은 리포트 안에서 고장난 "롤링20일" 줄과
나란히 찍혀 모순처럼 보였다는 점.

**영향**: `CLAUDE.md` 실전 전환 기준 `① 모의투자 4주 통산 수익률 양수` 판정이
구조적으로 산출 불가능한 상태로 2개월이 그냥 지나갔다.

---

## 2. 수정 — "활성 버전"을 registry(`strategy_versions.is_current`) 하나로 통일

1. **DB 정정** (`data/db/strategy_registry.db`, 커밋 대상 아님): `is_current`를
   `v1.2` → `v1.0`으로 되돌림(실제 운영 버전). `v1.1`/`v1.2`는 `is_current=0`으로
   비활성화(기록은 보존).
2. **`main.py:8425-8438`**: 라이브 스냅샷 기록 시 `PARAM_HISTORY[-1]` 대신
   `get_registry().get_current_version()`을 읽도록 변경.
3. **`strategy/ops/hotswap_gate.py:143-190`**: 다음 버전 번호를 매길 때도
   `PARAM_HISTORY[-1]` 대신 registry 기준으로 변경(실제 Hot-Swap 발동 시 같은
   드리프트 재발 방지). `param_optimizer.apply_best()`와 동일하게 `PARAM_HISTORY`에도
   문서화용 항목을 append하도록 추가 — registry가 유일한 "활성 버전" 소스이고
   PARAM_HISTORY는 참고용 변경이력.

검증(`DailyExporter.build_report()` 직접 호출):
```
버전    : v1.0  (33일차)
판정    : UNDERPERFORM
Live    : Sh=-0.69  MDD=137.4%  WR=0.0%  PF=1.00
롤링20일: 누적 -2112475원  Sh=-0.69  MDD=137.4%
```
`(1일차)`/`누적 +0원` 고정이 사라지고 실제 33일치 데이터가 반영됨.
(`판정: UNDERPERFORM`은 리포트 버그가 아니라 진짜 실측 — WFA 대비 Live 성과 하회.)

---

## 3. 부수 발견 — `coherence_blocked` 컬럼 에러는 버그가 아니라 미적용 마이그레이션

검증 중 `진입 퍼널 : [계산 실패: no such column: coherence_blocked]` 에러가 나서
추가로 딥다이브함.

- `297차`(`2a2d6c7`, 2026-07-06 21:28:53 커밋)가 `ensemble_decisions`에
  `coherence_blocked` 컬럼을 새로 추가하는 코드(`utils/db_utils.py`
  `_migrate_ensemble_decisions_db()` additions + `fetch_daily_entry_funnel()` 쿼리)를
  넣음.
- 그날 15:40 리포트는 이 커밋보다 **먼저** 생성돼 해당 컬럼 참조 자체가 없었음(에러
  없음). 커밋 이후 앱이 재시작되지 않아 `init_all_dbs() → init_predictions_db() →
  _migrate_ensemble_decisions_db()`가 다시 돌지 않았고, 그 사이 검증 스크립트가 새
  코드로 옛 스키마를 조회해 에러가 난 것.
- `init_all_dbs()`를 수동 실행해 즉시 마이그레이션 적용(nullable 컬럼 추가라
  안전/멱등). 원래는 다음 앱 재시작(08:55 기동) 때 자동으로 적용됐을 부분.
- 재검증 결과 정상 출력 확인:
  ```
  진입 퍼널(2026-07-06, 총 369분):
    FLAT 74 → conf미달 235 → CoherenceGate 0 → 게이트차단 60 → 후보 0 → 진입 0
    게이트별: Hurst(횡보차단)=55  마감시간(15:00+)=2  콜드스타트/기타(σ미수집)=1
              Degraded신뢰도=1  모드필터=1
  ```

---

## 4. 남은 관찰 항목 (액션 없음, 참고용)

- **등급 "?" 버킷** (07-06 리포트: `-1,275,689원(5건,승60%)`) — 이미
  `dev_memory` 285차/286차에 "미조치"로 등록된 `stuck_exit_flat`/`stuck_exit_remainder`
  청산 경로가 `grade`를 기록하지 않는 문제. 새로 발견된 게 아니라 기존 추적 항목이
  리포트 숫자로 실측된 것.
- **호라이즌 "?" 버킷** — `entry_horizon`은 2026-07-05부터 기록 시작이라 그 이전
  거래는 전부 "?"로 집계되는 게 설계상 정상. 07-06 기준 132건 전부가 여전히 "?"라
  며칠 더 지나도 비율이 안 줄면 기록 경로 자체를 재확인 필요.

## 변경 파일

`main.py`, `strategy/ops/hotswap_gate.py`, `data/db/strategy_registry.db`(직접 UPDATE,
커밋 제외), `data/db/predictions.db`(스키마 마이그레이션, 커밋 제외).

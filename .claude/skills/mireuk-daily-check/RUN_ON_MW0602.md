# MW0602에서 실행할 지시서

> **STEP 1·2는 2026-08-14에 완료됐다** (MW0602 `dev`). 아래 §0에 결과를 적어 둔다.
> **지금부터 이 문서는 STEP 0·3~6만 쓰는 실행 지시서다.**

## 0. 완료 기록 — STEP 1·2 (2026-08-14)

| STEP | 결과 |
|---|---|
| 1. 스킬 패치 | `SKILL_PATCH.md` 6곳 전부 `SKILL.md` 에 삽입 후 **패치 파일 삭제**. 기존 문장 무수정 |
| 2-1. `predictions.db` | `data/db/predictions.db` — 3테이블 확정. 손익은 `data/db/trades.db` 에 있다. **전체 기록 → `references/evidence_map.md` §8**(신설) |
| 2-2. 수집기 DB 조회 | **읽지 않는다**(`sqlite3` 0건). 제4부는 직접 조회 — SKILL.md §2·postmortem §0에 명시 |
| 2-3. P8 정의 | `retrain_eod.py:p8_scaler_refit()` = **EOD 스케일러 재적합**(15:45~, py310_64). CLAUDE.md·ROADMAP.md에는 약칭이 없다 |
| 2-4. **313차 판정** | **동일하지 않다 — 포함관계.** 방법론=`predictions.db` 카운터팩추얼 절차 / 원칙=결론 인정 규율. → **`postmortem.md` §4-2를 다섯 갈래로 다시 씀**, `invariants.md` §4에 정본 기록 |
| 2-5. 중복 | 중복 없음. 역할 분담 확정(스키마=evidence_map §8 / 국면관문=phases C-6 / 절차=postmortem) |
| 2-6. 청산 사유 | 7종 확정. ⚠ `하드스톱`에 **TP1 보호 이익 청산이 섞여 있다**. `15:10 강제청산`은 0건 |

**함께 반영한 것** — 수집기 불변식 정규식이 `NAME: bool = True`(어노테이션 대입)를 못 읽어
468차 스위치가 감시에서 빠져 있던 것을 수정하고, 462·468차 스위치 5종을 감시 대상에 추가했다.

---

## 1. 아래 전문을 Claude Code에 그대로 붙여넣는다

리포 루트(`C:\Users\pc1\PycharmProjects\futures`)에서 `claude` 실행 후:

---

미륵이 점검 — 장후(post) 국면. 오늘 날짜 기준으로 수행한다.

**STEP 0. 환경 확인**
- `git branch --show-current` 가 `dev` 인지 확인한다. 아니면 즉시 중단하고 보고한다 (함정③).
- `.claude/skills/mireuk-daily-check/references/postmortem.md` 가 있는지 확인한다.

**STEP 1·2는 완료됐다** (위 §0). 바로 STEP 3으로 간다.

**STEP 3. 증거 수집**
```
python .claude/skills/mireuk-daily-check/scripts/collect_evidence.py --phase post --pc MW0602 --out-auto
```
실패하면 조용히 넘어가지 말고 보고서 최상단에 실패 사실과 stderr를 적는다.

**STEP 4. 점검 리포트 작성 — 5부 구성**
`docs/정기점검/매일점검/MW0602-<YYYYMMDD>-점검리포트.md` (기존 날짜본을 덮어쓰지 않는다)

양식은 `references/report_template.md` 를 그대로 따른다(§4·§5가 사후검증·향상방안이다).

- 제1부 이상점 정리보고 (SKILL.md §5 4단 형식: 증상→근거→기준위반→영향)
- 제2부 Fix 작업 구현계획 (P0/P1/P2, 파일:함수 수준)
- 제3부 고도화 방안
- **제4부 진입 승패 사후검증** — `references/postmortem.md` §1~§4 절차대로
  - §1 오늘 할일 4분류 표 (NEXT_TODO 미완료 × 당일 커밋 대조)
  - §2 3원 대사 — **포지션 단위**로 로그 / `ensemble_decisions.entry_executed=1` /
    `COUNT(DISTINCT trades.entry_ts)` 세 값 (`trades` 행수는 청산 레그라 더 많다)
  - §3 케이스 카드 — **포지션** 1건당 1장, 요인 태그 A~F
  - §4 요인 집계 + 313차 다섯 갈래
- **제5부 수익률 향상방안** — postmortem.md §5 의 6칸 양식

**반드시 지킬 것**
- 함정① — 제안이 이미 코드에 있는지 `config/settings.py: VALIDATION_CAMPAIGN_DECISIONS` 와 `DECISION_LOG.md` 로 먼저 확인
- 함정② — 재인용 금지 수치(2026-06-25 SHAP=0, 2026-08-01 §9-3 사이징 통계 4종) 인용 금지
- 함정④ — ERROR 를 찾지 마라. 진입·청산·차단·사이징은 INFO 다
- 313차 — **판정 단위는 건수가 아니라 거래일**이다. 다섯 갈래를 다 적용한다(`postmortem.md` §4-2)
- **승패를 `exit_reason` 만으로 세지 마라** — `하드스톱`에 TP1 보호 이익 청산이 섞여 있다
- 요인 태그는 로그 인용과 시각 없이 붙이지 않는다. 없으면 `?`
- 절대원칙 6종 저촉 제안 금지
- **DB는 읽기 전용으로만** 만진다 — 라이브 프로세스가 같은 파일을 쓴다

**STEP 5. dev_memory 갱신 (생략 금지)**
- `dev_memory/DECISION_LOG.md` 에 append. 헤더: `## <날짜> (MW0602 NNN차 — 일일 점검 + 승패 사후검증)`
  - 세션 차수는 **원격(git) 기준**으로 맞춘다 (392차 관행)
  - 항목 구성: 증상 → 원인 → 결정 → Why → How to apply → 검증
- `dev_memory/NEXT_TODO.md` 에 새 fix/고도화를 체크박스로 추가
- 두 파일 다 덮어쓰지 않는다

**STEP 6. 커밋**
- 커밋 메시지 첫 단어는 `[MW0602]`

---

## 2. 참고

- 장중(09:00~15:10)에는 이 지시서를 돌리지 않는다. 라이브 프로세스가 돈다.
- STEP 2 #4(313차 판정)는 완료됐다 — **포함관계**로 확정하고 `postmortem.md` §4-2 를 다시 썼다.
- 이 지시서 대신 **`/dailycheck post`** 로 스킬을 직접 불러도 같은 절차가 돈다.
  지시서는 "스킬을 못 쓰는 환경(예약작업 등)"에서 붙여넣기용으로 남긴다.

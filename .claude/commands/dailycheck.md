---
description: 미륵이 장전/장중/장후 일일 운영 점검 — 이상점·Fix계획·고도화방안 보고서
argument-hint: "[pre|intra|post] [YYYY-MM-DD]"
---

`mireuk-daily-check` 스킬을 사용해 미륵이 일일 운영 점검을 수행하라.

인자: $ARGUMENTS
- 첫 인자가 `pre`/`intra`/`post` 중 하나면 그것을 국면으로 쓴다. 없으면 현재 KST 시각으로 추론한다(~09:00 pre / 09:00~15:10 intra / 15:10~ post).
- 두 번째 인자가 날짜면 그 날을 대상으로 한다. 없으면 오늘.

절차는 스킬 문서를 그대로 따른다. 요약:

1. `python scripts/collect_evidence.py --phase <국면> --date <날짜> --out-auto`
   (`--out-auto` 는 `docs/정기점검/매일점검/evidence_<PC명>-<날짜>_<국면>.md` 로 저장한다.)
   (처음 쓰는 PC라면 `--discover` 를 먼저 돌려 로그 인벤토리를 확인한다.)
2. 걸린 지점만 원본 로그를 좁게 되짚는다.
3. `CLAUDE.md`(절대원칙 6종·9단계) · `CORE.md` · `ROADMAP.md` · `dev_memory/` · 커밋 이력과 대조한다.
   `references/phases.md` 체크리스트와 `references/invariants.md` 를 빠짐없이 통과시킨다.
4. `references/report_template.md` 형식으로 **① 이상점 정리보고 ② Fix 작업 구현계획 ③ 고도화 방안**
   보고서를 `docs/정기점검/매일점검/<PC명>-<YYYYMMDD>-점검리포트.md` 에 쓴다. 날짜본을 덮어쓰지 않는다.
5. **장후(`post`)면 여기서 끝내지 않는다** — `references/postmortem.md` 절차로
   **④ 진입 승패 사후검증 ⑤ 수익률 향상방안**까지 이어 붙인다(EOD+P8 완료 확인 → 오늘 할일
   4분류 → 3원 대사 → 케이스 카드 → 313차 다섯 갈래). 수집기는 DB를 읽지 않으므로
   `predictions.db`·`trades.db` 는 직접 조회한다(`references/evidence_map.md` §8, 읽기 전용).
6. `dev_memory/DECISION_LOG.md` append + `NEXT_TODO.md` 갱신. 세션 헤더와 커밋에 PC명 병기.

세 가지 함정을 잊지 마라:
- **판정 ≠ 결정** — 리포트 FAIL이 반복되는 것은 미조치의 증거가 아니다. 코드를 먼저 확인하라.
- **재인용 금지 수치** — `references/invariants.md` §3.
- **멀티PC** — `[MW0601]`/`[MW0602]` 태그, 세션 차수는 원격 기준.

장중(`intra`)에는 코드 변경·재기동을 **실행하지 않는다.** 라이브 프로세스가 돌고 있다.

# Codex Session Start for Mireuk

## What Codex Should Assume

- When a session starts inside this `futures` project, Codex should treat Mireuk as an actively operated trading system.
- The default intent is:
  - monitor runtime behavior
  - inspect anomalies
  - trace root causes
  - make verifiable fixes
  - continue hardening and upgrades

## Re-entry Read Order

1. `dev_memory/CODEX_COLLAB_INTENT.md`
2. `dev_memory/CODEX_STARTUP_ROUTINE.md`
3. `dev_memory/CURRENT_STATE.md`
4. `dev_memory/NEXT_TODO.md`
5. `dev_memory/DECISION_LOG.md`
6. `dev_memory/SESSION_LOG.md`
7. latest files under `logs/`

## Good User Opening Comments

- `미륵이 세션 시작. 루틴대로 현재 상태와 최신 로그부터 점검해`
- `미륵이 모니터링 시작. dev_memory와 최신 로그를 읽고 이상점부터 찾아줘`
- `미륵이 이어서 작업하자. 실행 상태 복원하고 할 일 우선순위 정리해줘`
- `미륵이 점검 모드로 시작해. 최근 변경사항, 미검증 항목, 리스크를 먼저 요약해줘`

## Expected First Actions

1. Reconstruct project and runtime context.
2. Read the newest logs and detect obvious anomalies.
3. Summarize active issues, pending checks, and likely next actions.
4. Move into diagnosis, fixes, or upgrades based on evidence.

## Session Operating Rule

- Prefer one focused topic per chat.
- When the topic changes materially, start a new chat instead of carrying unrelated history forward.
- Use a short start comment at the beginning and a short close comment at the end.
- Leave important conclusions, verifications, bugs, and TODOs in `dev_memory` so the next session can stay short and efficient.
- Even within the same topic, if the session becomes long or shifts from one work mode to another, close with a summary and restart in a fresh chat.

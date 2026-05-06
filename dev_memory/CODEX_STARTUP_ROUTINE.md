# Codex Startup Routine for Mireuk

## Goal

- When Codex is opened inside the `futures` project, quickly reconstruct Mireuk's current context, operating status, recent changes, and pending work with minimal user prompting.
- See `CODEX_SESSION_START.md` for the short session-start guide and recommended user opening comments.

## Read Order

1. `dev_memory/CODEX_COLLAB_INTENT.md`
2. `dev_memory/CURRENT_STATE.md`
3. `dev_memory/NEXT_TODO.md`
4. `dev_memory/DECISION_LOG.md`
5. `dev_memory/SESSION_LOG.md`
6. Root docs: `CLAUDE.md`, `CORE.md`, `PROJECT_DESIGN.md`, `ROADMAP.md`

## First Runtime Checks

1. Check the latest log files in `logs/` and identify the newest `SYSTEM`, `WARN`, `DATA`, and trading-related logs.
2. Look for fresh errors, warnings, stalled pipeline signs, repeated recovery attempts, missing fills, or suspicious zero/empty values.
3. Confirm whether the current concern is runtime monitoring, anomaly diagnosis, bug fixing, or feature/system upgrade work.

## Default Operating Assumptions

- Mireuk is an actively operated trading system.
- Monitoring and anomaly diagnosis take priority over speculative refactors.
- Safety-sensitive paths include Kiwoom connection, realtime data flow, minute pipeline, entry/exit orders, partial exits, and emergency exit behavior.
- Prefer evidence from logs, DB state, and code paths over guesswork.

## Default Response Pattern

1. Reconstruct current status from docs and logs.
2. Summarize the most important active issues or recent changes.
3. Identify what looks abnormal, risky, incomplete, or unverified.
4. Make or suggest the smallest verifiable next action.
5. After stabilization, move into hardening or upgrade work.

## Important Pending Focus Areas

- Verify actual Kiwoom order/fill behavior end-to-end.
- Verify TP1/TP2 partial exit behavior end-to-end.
- Watch for pipeline stalls, watchdog recoveries, and realtime feed mismatches.
- Keep checking whether dashboard metrics match runtime reality.

## Session Handoff Rule

- If Codex discovers a new bug, decision, verification result, or operating caveat, record it back into `dev_memory` before finishing when appropriate.

## Session Efficiency Rule

- Prefer one main topic per chat session.
- If the work shifts to a new topic, open a new chat and restart with the short Mireuk start comment.
- Close each topic with the short Mireuk end comment and preserve key outcomes in `dev_memory`.
- Even within the same topic, if the session gets long or changes work mode significantly, end it cleanly and restart from a fresh session.

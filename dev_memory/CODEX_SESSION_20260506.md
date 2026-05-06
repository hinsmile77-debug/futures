# Codex Session Note - 2026-05-06

## Session scope

- Date: `2026-05-06`
- Session focus:
  - restore Mireuk runtime state
  - fix Kiwoom order submission path
  - stop `predictions.confidence` DB failures
  - expose actual `ACCNO` accounts in UI and persist selected account number
  - verify post-restart behavior from logs

## Code changes applied

- `collection/kiwoom/api_connector.py`
  - fixed `SendOrder` `dynamicCall(...)` invocation to pass a single argument list
- `learning/prediction_buffer.py`
  - sanitize `confidence`
  - fallback to `1/3` when missing, invalid, or non-finite before DB insert
- `main.py`
  - abort internal entry open when Kiwoom `SendOrder` returns non-zero
  - log raw `ACCNO` and parsed account list after login
  - add account save flow:
    - read selected account from dashboard
    - validate 10-digit numeric account
    - write `ACCOUNT_NO` into `config/secrets.py`
    - update in-memory `_secrets.ACCOUNT_NO`
    - rebind emergency order adapter
- `dashboard/main_dashboard.py`
  - added top-right account UI:
    - `계좌번호:` label
    - combo box
    - save button
  - added adapter methods to populate/select account list

## Verification completed

- `py_compile` passed for:
  - `collection/kiwoom/api_connector.py`
  - `learning/prediction_buffer.py`
  - `main.py`
  - `dashboard/main_dashboard.py`

## Runtime timeline

### 1. Initial failures before patch validation

- `2026-05-06 09:38~09:43`
  - entry path failed with `TypeError` in `api_connector.send_order()`
  - root cause: wrong `dynamicCall(...)` argument shape
- `2026-05-06 09:44~10:26`
  - repeated warnings:
    - `NOT NULL constraint failed: predictions.confidence`
- `2026-05-06 09:45`
  - Circuit Breaker halt triggered:
    - `30m accuracy 33.3% < 35%`

### 2. After code fixes, before correct account save

- `TypeError` disappeared after order-call patch
- entry failures changed to Kiwoom return code `ret=-302`
- `WARN.log` shows `ret=-302` at:
  - `10:30:34`
  - `10:31:03`
  - `10:32:03`
  - `10:45:16`
  - `10:45:20`
  - `10:45:22`
  - `10:48:19`
- interpretation:
  - order call shape was fixed
  - remaining failure was account-number validity / order acceptance path

### 3. Account discovery and save flow

- login log after UI/account work:
  - `2026-05-06 10:45:47`
  - `ACCNO raw=7034610331;8123417111;`
  - `parsed accounts=['7034610331', '8123417111']`
- user selected real 10-digit account and saved it
- save confirmation:
  - `2026-05-06 10:47:47`
  - `[Account] 주문 계좌번호 저장 완료: 7034610331`
- persisted config:
  - `config/secrets.py`
  - `ACCOUNT_NO = "7034610331"`

### 4. After final restart with saved 10-digit account

- restart/account reflection confirmed at:
  - `2026-05-06 10:48:37`
  - `ACCNO raw=7034610331;8123417111;`
  - `parsed accounts=['7034610331', '8123417111']`
- last observed `ret=-302`:
  - `2026-05-06 10:48:19`
- no further `ret=-302` observed after restart at `10:48:31~10:48:37`
- no further `predictions.confidence` warnings after restart
- realtime feed and 1-minute bars continued normally through at least `11:06`

## Post-restart observed trading behavior

- `TRADE.log` after final restart shows internal trading lifecycle activity:
  - `10:49:01` close LONG, `+0.95pt`, TP1(full)
  - `10:50:00` enter LONG `@1124.8`
  - `10:52:00` close LONG, `+1.10pt`, TP1(full)
  - `10:53:00` enter LONG `@1126.3`
  - `10:56:00` close LONG, `-1.99pt`, hard stop
  - `10:58:00` enter LONG `@1126.6`

## Important anomalies still open

### 1. Possible local state mismatch around `10:48:19`

- `WARN.log`:
  - `2026-05-06 10:48:19`
  - `[Entry] SendOrder ... ret=-302`
- `TRADE.log` at the same timestamp:
  - `2026-05-06 10:48:19`
  - internal LONG position open logged
- after restart:
  - `2026-05-06 10:48:31`
  - restored LONG position warning appears
- this suggests at least one local/broker state inconsistency window around the account-fix boundary

### 2. No explicit broker fill confirmation yet

- we confirmed:
  - `dynamicCall` crash resolved
  - `ret=-302` disappeared after valid account save + restart
  - internal trade flow continued
- we have not confirmed:
  - explicit Kiwoom order acceptance/fill via `OnReceiveChejanData`
  - exact broker-side fill status matching internal `TRADE.log`

### 3. Circuit Breaker still active as strategy risk

- `2026-05-06 11:00:00`
  - Circuit Breaker halt triggered again:
    - `30m accuracy 33.3% < 35%`
- operationally, infrastructure improved, but model/runtime performance risk remains

## Current end-of-session status

- account selection/save UI: working
- `ACCNO` logging after login: working
- `config/secrets.py` account persistence: working
- `SendOrder` argument-shape crash: fixed
- `predictions.confidence` DB warning: no recurrence after fix/restart
- `ret=-302` invalid-account failure: no recurrence after saving valid 10-digit account and restarting
- realtime feed / bar close flow: active
- remaining uncertainty:
  - broker fill confirmation path
  - local restore/state mismatch near `10:48:19`
  - CB halt due to low recent accuracy

## Recommended next step

1. implement and log `OnReceiveChejanData`
2. record explicit states for:
   - order request
   - order accepted/rejected
   - partial fill
   - full fill
   - cancel/reject
3. reconcile local `PositionTracker` updates against actual Chejan events
4. re-check why a local LONG was logged at `10:48:19` while `ret=-302` also existed in the same window

## Follow-up update

- `OnReceiveChejanData` callback is now wired into `KiwoomAPI`
- explicit runtime logging added for:
  - order request
  - order accept/confirm
  - fill events
  - reject/error messages from `OnReceiveMsg`
- `TradingSystem` now treats Chejan fill as the source of truth for:
  - entry open
  - partial exit
  - full exit
- `PositionTracker` now has fill-based sync helpers:
  - `apply_entry_fill(...)`
  - `apply_exit_fill(...)`
- important remaining caveat:
  - multi-contract full-exit orders split across multiple fill events still need an end-to-end live verification pass to confirm DB row semantics are exactly what we want

## Close-out update

- Date:
  - `2026-05-06`
- This close-out focused on:
  - broker sync startup block diagnosis
  - reconstructing the `10:48:19` local/broker mismatch window
  - strengthening order / message / chejan / balance diagnostics for the next run

### What we concluded

- `BrokerSync` block at `2026-05-06 12:23:50` likely came from an **empty placeholder `OPW20006` response being treated as a hard mismatch**, not necessarily from a true broker-side inconsistency.
- `OPW20006` balance requests were also being sent with an empty password field, which reduced confidence in the startup-balance interpretation path.
- The exact root cause of the `2026-05-06 10:48:19` mismatch is still not fully proven from historical logs alone, but the main observability gap was clear:
  - we could not tell from the restored state file whether the restored LONG came from
    - a true Chejan fill
    - a broker sync write
    - or a local-only state save path

### Code/debug changes added this session

- `collection/kiwoom/api_connector.py`
  - added `OrderDiag` logging right before `SendOrder`
  - added `ChejanDiag` logging with expanded raw chejan payload context
  - added `OrderMsgDiag` logging for `OnReceiveMsg`
  - `request_futures_balance()` now injects `ACCOUNT_PWD`
  - `OPW20006` response is now classified into:
    - `nonempty_rows`
    - `blank_row_count`
    - `all_blank_rows`
  - diagnostic logs added:
    - `OPW20006-REQ`
    - `OPW20006-RESP`
    - `OPW20006-DIAG`

- `main.py`
  - added pending-order lifecycle diagnostics:
    - `PendingOrder set`
    - `PendingOrder clear`
  - added structured diagnostics:
    - `EntryAttempt`
    - `EntrySendOrderResult`
    - `EntryPendingCreated`
    - `PartialExitAttempt`
    - `PartialExitSendOrderResult`
    - `OrderMsgFlow`
    - `ChejanFlow`
    - `ChejanMatch`
    - `ChejanDedup`
    - `EntryFillFlow`
    - `ExitFillFlow`
    - `BalanceChejanFlow`
    - `BrokerSyncFlatPlaceholder`
  - startup broker sync now treats a row set with only blank placeholder rows as:
    - effectively `FLAT`
    - not a hard mismatch
    - and should release `block_new_entries`

- `strategy/position/position_tracker.py`
  - state file now carries:
    - `last_update_reason`
    - `last_update_ts`
  - restore path now emits `PositionDiag`
  - this should let us identify whether a restored position came from:
    - `apply_entry_fill:*`
    - `sync_from_broker:*`
    - `sync_flat_from_broker`
    - `partial_close:*`
    - other local state paths

### Verification done

- `py_compile` passed for:
  - `main.py`
  - `collection/kiwoom/api_connector.py`
  - `strategy/position/position_tracker.py`

### First things to check next session

1. `OPW20006-REQ / RESP / DIAG`
   - verify whether startup rows are truly blank placeholders or populated balance rows
2. `BrokerSyncFlatPlaceholder` or `BrokerSync status`
   - verify whether startup no longer leaves `block_new_entries=True` in the blank-row case
3. `EntryAttempt` -> `EntrySendOrderResult` -> `PendingOrder` -> `OrderMsgDiag` -> `ChejanFlow`
   - verify complete causal chain for one entry order
4. `PositionDiag`
   - verify restored position source on restart
5. if a mismatch happens again:
   - compare `PositionDiag`
   - `PendingOrder`
   - `ChejanDiag`
   - `BalanceChejanFlow`
   - and `OrderMsgDiag`
   together before changing logic again

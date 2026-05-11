# Cybos Daily PnL Source Of Truth

Date: 2026-05-11

## Rule

For futures daily pnl and account summary fields, the source of truth is the
raw `CpTd6197` response captured in `SYSTEM.log`.

HTS is reference-only. If HTS and raw Cybos payload appear different, keep the
implementation aligned with the logged `CpTd6197` headers unless a later broker
payload proves otherwise.

## Validated Mapping

Validated from:
- `[CybosDailyPnl] ... validate=... summary=...`
- `[CybosDailyPnlHeaders] ... headers=...`

Current mapping:
- `header 1` = `예탁현금`
- `header 2` = `익일가예탁현금`
- `header 5` = `전일손익`
- `header 6` = `금일손익`
- `header 9` = `청산후총평가금액`

## Current Observations

Observed on the 2026-05-11 mock trading session:
- `header 9 == header 2`
- `header 5 == 0`

Implications:
- `청산후총평가금액` and `익일가예탁현금` can legitimately be identical in the
  current Cybos environment.
- `전일손익` being `0` is currently a broker payload fact, not a parser failure.

## Where To Update

If this mapping changes in a future session, update both:
- `collection/cybos/api_connector.py`
- this memo

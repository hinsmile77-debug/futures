# Broker Capability Matrix

Last updated: 2026-05-15

## Purpose

This document separates capability support from runtime verification.

- Supported: feature exists in broker abstraction or runtime path.
- Verified: feature was confirmed in runtime/log/real session.

## Matrix

| Capability | kiwoom | cybos | simulation mode |
|---|---|---|---|
| connect | supported, verified(legacy path) | supported, verified(startup) | supported (same broker connect path) |
| account list | supported | supported | supported |
| nearest futures code | supported | supported | supported |
| market order | supported | supported | supported (broker-dependent) |
| fill callback | supported | supported | supported (event path same) |
| realtime tick | supported | supported | supported (requires market/open feed) |
| realtime hoga | supported | supported | supported (requires market/open feed) |
| investor TR/data | supported | supported (runtime quality varies) | supported (broker-dependent) |
| balance sync | supported | supported | supported |
| server label resolution | supported (GetServerGubun) | supported (Cybos label path) | supported |

## Runtime verification source

At startup, main runtime logs capability summary as a single line:

- prefix: [Capability]
- output fields:
  - connect
  - balance
  - order
  - fill
  - tick (event count)
  - hoga (event count)
  - investor (fetch count, runtime_supported)
  - server

Reference implementation: main.py (TradingSystem._collect_broker_capability_summary, TradingSystem._log_broker_capability_summary).

## Notes

- Runtime verification is session-specific and may remain N before market events occur.
- order/fill verification typically becomes Y only after real order flow or simulated fill events.
- investor runtime_supported can be broker/data-source dependent and should be interpreted together with fetch_count.

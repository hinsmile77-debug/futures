# Cybos Option Probe Summary

Date: 2026-05-13
Scope: Verify which Cybos COM/TR candidates can actually provide option-related data for Mireuk feature expansion.

## Goal

Before building any Cybos version of `option_data.py`, verify:

- which option COM objects are actually registered
- which objects return usable payloads
- which objects are option snapshot only vs chain/statistics style
- whether any candidate can realistically support PCR / ATM OI / GEX style features

## Real HTS Option Codes Used

- `B0165A01`
- `B0165A07`

These codes came from HTS and replaced earlier guessed synthetic codes.

## Confirmed Working Candidates

### `Dscbo1.OptionMst`

- registered
- `Dispatch()` works
- `BlockRequest()` works
- returns useful payload for real option codes
- useful values are in `GetHeaderValue()`
- `GetDataValue()` rows are effectively empty

Interpretation:
- single-option snapshot object
- not a chain row object

### `Dscbo1.SoptionMst`

- registered
- works for real option codes
- same family as `OptionMst`
- appears to use integer-like scaling compared with `OptionMst`

Interpretation:
- single-option snapshot object
- keep as a live comparison candidate

## Rejected Or Downgraded Candidates

### `Dscbo1.OptionCurrentRq`

- COM ProgID not registered in current environment

### `CpSysDib.CpSvrNew5000`

- COM ProgID not registered in current environment

### `Dscbo1.FutureOptionStat`

- registered
- `Dispatch()` works
- `BlockRequest()` works
- returns `dib_status=-1`
- message: `00103 해당 업무가 중지중입니다.(open.rq)`

Interpretation:
- service exists but is not usable now

### `Dscbo1.FutureOptionStatPB`

- registered
- `Dispatch()` works
- `BlockRequest()` is not supported

Interpretation:
- not a normal request-style TR

### `CpSysDib.CpSvrNew7215A`

- integer-input TR
- valid combinations found
- detailed payload is not option chain data

Observed valid family:
- `input0=0`
- `input1=49 or 50`
- `input2=1/2/49/50` and some nearby values

Observed rows:
- stock/ETF code and name pairs
- ranking-like structure
- no strike
- no call/put split
- no option OI chain shape

Interpretation:
- not a useful option chain/OI source

### `CpSysDib.CpSvrNew7215B`

- integer-input TR
- string input rejected
- tested integer values still return input error

Interpretation:
- unresolved, but lower priority than fresher families

### `CpSysDib.CpSvrNew7221`

- integer-input TR
- string input rejected
- int inputs complete normally
- message: `stock.total.invest`

Interpretation:
- stock total investor summary family
- not option chain/OI

## Current Best Interpretation

As of 2026-05-13:

- the only clearly usable option-related Cybos objects found so far are `OptionMst` / `SoptionMst`
- these appear to be single-option snapshot objects
- no verified Cybos object has yet been found that clearly provides strike-by-strike option OI chain data
- no verified path to true PCR / ATM OI / GEX exists yet

## Practical Decision

- do not start `collection/cybos/option_data.py` yet
- continue probing only for true option chain / OI candidates
- treat `OptionMst/SoptionMst` as snapshot research sources only

## Scripts Added In This Session

- `scripts/ensure_cybos_login.py`
- `scripts/probe_cp_option_mst.py`
- `scripts/probe_option_current_rq.py`
- `scripts/probe_cp_svr_new5000.py`
- `scripts/probe_future_option_stat.py`
- `scripts/probe_future_option_stat_pb.py`
- `scripts/probe_cp_svr_new7215a.py`
- `scripts/probe_cp_svr_new7215a_inputs.py`
- `scripts/probe_cp_svr_new7215a_multi_inputs.py`
- `scripts/probe_cp_svr_new7215a_detail.py`
- `scripts/probe_cp_svr_new7215b.py`
- `scripts/probe_cp_svr_new7215b_inputs.py`
- `scripts/probe_cp_svr_new7221.py`
- `scripts/probe_cp_svr_new7221_inputs.py`

## Next TODO

1. Probe `CpSysDib.CpSvrNew7222`.
2. Probe `CpSysDib.CpSvrNew7224`.
3. If both are non-option families, stop broad random probing.
4. Build an `OptionMst/SoptionMst` field-mapping helper:
   - compare multiple option codes side by side
   - identify strike / last / open / high / low / volume / OI / theoretical / IV candidates
5. Decide whether Mireuk phase-1 can use snapshot-only option features before chain/OI is solved.

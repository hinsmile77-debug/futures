# stack_gate_shadow — main.py 훅 (⚠ 아직 적용 안 함)

**출처** `Sindong\peterlee\매도매수_성격판별_지표검증_20260913.md` §4-9·§7
**상태** 모듈·백필·리포트는 완성. **main.py 는 건드리지 않았다** — 라이브 진입 경로라 승인 후 적용.

## 지금 상태로 이미 되는 것

```
python scripts\backfill_stack_gate_shadow.py
```
`raw_candles` 에 상태기를 재생해 과거 진입 전량에 상태를 붙이고 반사실까지 판정한다.
결과는 `data\db\stack_gate_shadow.db` (신규 파일, trades.db 무변경).
**main.py 훅 없이도 매일 EOD 후 이 한 줄만 돌리면 표본이 계속 쌓인다.** 훅은 선택이다.

## 훅이 주는 것

백필은 분봉 격자(`raw_candles`)에서 재생하므로 진입 시점의 **실시간** 공격자·OI 스냅숏과
미세하게 다를 수 있다. 훅은 그 차이를 없앤다. 그뿐이다 — 라이브 동작은 바뀌지 않는다.

## 훅 위치 — `trend_efficiency_gate_shadow` 블록 바로 아래

`main.py` 의 `if _entry_executed_this_cycle and direction != 0:` 블록(현재 약 11037행)
끝에 이어 붙인다. 같은 조건·같은 관례를 쓰므로 기존 블록 안에 넣어도 된다.

### ① 초기화 (봇 기동부, `self.` 컨텍스트)

```python
from strategy.stack_gate_shadow import StackGateShadow, ensure_table, INSERT_SQL
self._stack_gate = StackGateShadow()          # W=30, q=0.5
ensure_table(TRADES_DB)                        # 또는 db_utils.init_db() 에 DDL 이관
```

### ② 분봉 루프 — 진입 여부와 무관하게 **매 분** 호출 (창이 끊기면 안 된다)

```python
_sg = self._stack_gate.update(
    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00"),
    bar.get("buy_vol"), bar.get("sell_vol"), bar.get("volume"), bar.get("oi"),
)
```

### ③ 진입 직후 기록 (`_entry_executed_this_cycle` 블록 안)

```python
try:
    _sg_dir = "LONG" if direction == 1 else "SHORT"
    _sg_dm = 1 if direction == 1 else -1
    execute(TRADES_DB, INSERT_SQL, (
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00"),
        _sg_dir, _final_grade, _sg["state"],
        _sg["aggr_imb"], _sg["oi_delta"], int(_sg["ready"]),
        int(StackGateShadow.would_block(_sg["state"], _sg_dir)),
        float(confidence), float(atr), _entry_horizon, int(_qty_auto),
        float(close),
        float(close - _sg_dm * atr * ATR_STOP_MULT),
        float(close + _sg_dm * atr * ATR_TP1_MULT),
    ))
except Exception as _sg_e:
    logger.warning("[StackGateShadow] 기록 실패 (무해): %s", _sg_e)
```

### ④ 반사실 판정 — EOD 배치에서

`resolve_rows(bar_map, pending)` → `UPDATE_SQL`. 백필 스크립트 §2~3이 그대로 예시다.

## 🔴 라이브 편입 금지 조건 (해제 전까지 `would_block` 은 기록용 플래그일 뿐이다)

1. 표본 **120거래일** 도달 (현재 57일)
2. 앵커드 워크포워드에서 `BUY_MECH ∧ LONG` 표본밖 기댓값 95%CI 상한 < 0
   — **미륵이 실보유 척도(h=5분)에서**. 현재 h=5 표본밖은 −3.03bp [−7.53, +1.13] 으로 **미달**
3. 기존 게이트(hurst / toxicity / trend_efficiency / joint)와의 **중복 차단률** 확인 —
   이미 다른 게이트가 막던 진입을 다시 막는 것이면 추가 가치가 0이다. 미측정 항목
4. 절제(ablation) — `ofi_pressure`·`cvd_*` 위에 추가 설명력이 있는지

## 알려진 제약

- **공격자 데이터는 2026-06-08 부터다.** 그 이전은 `state='NA', reason='no_aggressor_data'`.
- 원시 `buy_vol:sell_vol` 은 전 구간 **1.70:1 매수 편향**(분봉 98.9%). 모듈이 당일 중앙값을
  빼서 처리한다. **다른 코드가 이 컬럼을 방향 지표로 직접 쓰면 조용히 틀린다.**
- 효과는 **W=30분 관측창에서만** 존재한다(W=5/10/15 에서 소멸). 보유시간이 짧다고 창을
  줄이면 안 된다 — 창은 30분, 내다보는 지평만 짧게.

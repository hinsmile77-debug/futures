# Calibration Report

- Generated at: 2026-07-01 14:18:16
- Platt 보정기 도입 이후(since 2026-06-04) 검증 예측: 31106건
- 전체 누적 검증 예측: 62520건

## 최근 (Platt 보정 이후) — 현재 모델 성능 기준

- Accuracy: 32.69%
- Brier score: 0.238665
- Log-loss: 1.197790
- ECE: 0.122563

### 호라이즌별 (최근)

#### 10m
- Count: 4824  Accuracy: 31.57%  Brier: 0.242563  ECE: 0.143644

#### 15m
- Count: 4722  Accuracy: 31.85%  Brier: 0.251624  ECE: 0.178277

#### 1m
- Count: 6110  Accuracy: 34.84%  Brier: 0.224040  ECE: 0.066284

#### 30m
- Count: 5609  Accuracy: 32.25%  Brier: 0.242206  ECE: 0.135999

#### 3m
- Count: 5055  Accuracy: 31.97%  Brier: 0.236065  ECE: 0.108577

#### 5m
- Count: 4786  Accuracy: 33.18%  Brier: 0.239214  ECE: 0.117218

### Worst Confidence Bins (최근)

- 0.8~0.9: n=220 avg_conf=0.8465 acc=0.3136 gap=0.5328
- 0.7~0.8: n=320 avg_conf=0.7344 acc=0.2938 gap=0.4406
- 0.6~0.7: n=1658 avg_conf=0.6394 acc=0.3034 gap=0.3360
- 0.5~0.6: n=4657 avg_conf=0.5416 acc=0.3197 gap=0.2219
- 0.4~0.5: n=13975 avg_conf=0.4422 acc=0.3262 gap=0.1160
- 0.3~0.4: n=10276 avg_conf=0.3696 acc=0.3362 gap=0.0333

---

## 전체 누적 (참고용 — Platt 보정 이전 raw conf 포함)

- Accuracy: 34.70%
- Brier score: 0.239505
- Log-loss: 1.199273
- ECE: 0.130414

### Worst Confidence Bins (전체)

- 0.8~0.9: n=1291 avg_conf=0.8393 acc=0.3261 gap=0.5132
- 0.7~0.8: n=1928 avg_conf=0.7419 acc=0.3657 gap=0.3763
- 0.6~0.7: n=4725 avg_conf=0.6453 acc=0.3308 gap=0.3145
- 0.5~0.6: n=13859 avg_conf=0.5313 acc=0.3602 gap=0.1711
- 0.4~0.5: n=24882 avg_conf=0.4461 acc=0.3435 gap=0.1026
- 0.3~0.4: n=15835 avg_conf=0.3677 acc=0.3454 gap=0.0224

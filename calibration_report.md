# Calibration Report

- Generated at: 2026-07-01 14:01:16
- Platt 보정기 도입 이후(since 2026-06-04) 검증 예측: 31059건
- 전체 누적 검증 예측: 62473건

## 최근 (Platt 보정 이후) — 현재 모델 성능 기준

- Accuracy: 32.67%
- Brier score: 0.238704
- Log-loss: 1.197985
- ECE: 0.122831

### 호라이즌별 (최근)

#### 10m
- Count: 4822  Accuracy: 31.58%  Brier: 0.242510  ECE: 0.143518

#### 15m
- Count: 4720  Accuracy: 31.82%  Brier: 0.251701  ECE: 0.178509

#### 1m
- Count: 6093  Accuracy: 34.81%  Brier: 0.224055  ECE: 0.066680

#### 30m
- Count: 5592  Accuracy: 32.17%  Brier: 0.242341  ECE: 0.136911

#### 3m
- Count: 5049  Accuracy: 31.97%  Brier: 0.236077  ECE: 0.108649

#### 5m
- Count: 4783  Accuracy: 33.20%  Brier: 0.239219  ECE: 0.117067

### Worst Confidence Bins (최근)

- 0.8~0.9: n=220 avg_conf=0.8465 acc=0.3136 gap=0.5328
- 0.7~0.8: n=320 avg_conf=0.7344 acc=0.2938 gap=0.4406
- 0.6~0.7: n=1656 avg_conf=0.6394 acc=0.3025 gap=0.3368
- 0.5~0.6: n=4657 avg_conf=0.5416 acc=0.3197 gap=0.2219
- 0.4~0.5: n=13947 avg_conf=0.4423 acc=0.3258 gap=0.1165
- 0.3~0.4: n=10259 avg_conf=0.3696 acc=0.3363 gap=0.0333

---

## 전체 누적 (참고용 — Platt 보정 이전 raw conf 포함)

- Accuracy: 34.69%
- Brier score: 0.239525
- Log-loss: 1.199371
- ECE: 0.130553

### Worst Confidence Bins (전체)

- 0.8~0.9: n=1291 avg_conf=0.8393 acc=0.3261 gap=0.5132
- 0.7~0.8: n=1928 avg_conf=0.7419 acc=0.3657 gap=0.3763
- 0.6~0.7: n=4723 avg_conf=0.6453 acc=0.3305 gap=0.3148
- 0.5~0.6: n=13859 avg_conf=0.5313 acc=0.3602 gap=0.1711
- 0.4~0.5: n=24854 avg_conf=0.4462 acc=0.3433 gap=0.1029
- 0.3~0.4: n=15818 avg_conf=0.3677 acc=0.3454 gap=0.0223

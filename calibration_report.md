# Calibration Report

- Generated at: 2026-07-02 15:25:33
- Platt 보정기 도입 이후(since 2026-06-04) 검증 예측: 32223건
- 전체 누적 검증 예측: 63637건

## 최근 (Platt 보정 이후) — 현재 모델 성능 기준

- Accuracy: 32.79%
- Brier score: 0.238380
- Log-loss: 1.195884
- ECE: 0.121370

### 호라이즌별 (최근)

#### 10m
- Count: 4903  Accuracy: 31.65%  Brier: 0.242489  ECE: 0.143676

#### 15m
- Count: 4773  Accuracy: 31.80%  Brier: 0.251675  ECE: 0.179471

#### 1m
- Count: 6512  Accuracy: 34.58%  Brier: 0.224190  ECE: 0.068868

#### 30m
- Count: 5982  Accuracy: 32.92%  Brier: 0.241639  ECE: 0.130334

#### 3m
- Count: 5188  Accuracy: 32.09%  Brier: 0.235714  ECE: 0.106452

#### 5m
- Count: 4865  Accuracy: 33.09%  Brier: 0.239029  ECE: 0.117051

### Worst Confidence Bins (최근)

- 0.8~0.9: n=220 avg_conf=0.8465 acc=0.3136 gap=0.5328
- 0.7~0.8: n=322 avg_conf=0.7344 acc=0.2950 gap=0.4394
- 0.6~0.7: n=1674 avg_conf=0.6395 acc=0.3035 gap=0.3360
- 0.5~0.6: n=4869 avg_conf=0.5413 acc=0.3212 gap=0.2201
- 0.4~0.5: n=14515 avg_conf=0.4425 acc=0.3279 gap=0.1145
- 0.3~0.4: n=10623 avg_conf=0.3696 acc=0.3361 gap=0.0335

---

## 전체 누적 (참고용 — Platt 보정 이전 raw conf 포함)

- Accuracy: 34.72%
- Brier score: 0.239346
- Log-loss: 1.198282
- ECE: 0.129672

### Worst Confidence Bins (전체)

- 0.8~0.9: n=1291 avg_conf=0.8393 acc=0.3261 gap=0.5132
- 0.7~0.8: n=1930 avg_conf=0.7419 acc=0.3658 gap=0.3761
- 0.6~0.7: n=4741 avg_conf=0.6453 acc=0.3307 gap=0.3146
- 0.5~0.6: n=14071 avg_conf=0.5313 acc=0.3601 gap=0.1712
- 0.4~0.5: n=25422 avg_conf=0.4462 acc=0.3441 gap=0.1021
- 0.3~0.4: n=16182 avg_conf=0.3678 acc=0.3451 gap=0.0227

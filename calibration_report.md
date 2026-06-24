# Calibration Report

- Generated at: 2026-06-24 10:34:06
- Platt 보정기 도입 이후(since 2026-06-04) 검증 예측: 25086건
- 전체 누적 검증 예측: 56500건

## 최근 (Platt 보정 이후) — 현재 모델 성능 기준

- Accuracy: 32.31%
- Brier score: 0.240607
- Log-loss: 1.211022
- ECE: 0.131023

### 호라이즌별 (최근)

#### 10m
- Count: 4278  Accuracy: 31.14%  Brier: 0.243707  ECE: 0.152423

#### 15m
- Count: 4288  Accuracy: 32.09%  Brier: 0.250345  ECE: 0.175515

#### 1m
- Count: 4170  Accuracy: 35.40%  Brier: 0.222666  ECE: 0.062438

#### 30m
- Count: 3864  Accuracy: 30.75%  Brier: 0.249221  ECE: 0.158668

#### 3m
- Count: 4261  Accuracy: 31.00%  Brier: 0.238560  ECE: 0.122087

#### 5m
- Count: 4225  Accuracy: 33.42%  Brier: 0.239479  ECE: 0.115620

### Worst Confidence Bins (최근)

- 0.8~0.9: n=220 avg_conf=0.8465 acc=0.3136 gap=0.5328
- 0.7~0.8: n=285 avg_conf=0.7347 acc=0.2702 gap=0.4645
- 0.6~0.7: n=1461 avg_conf=0.6390 acc=0.2950 gap=0.3440
- 0.5~0.6: n=4064 avg_conf=0.5420 acc=0.3243 gap=0.2177
- 0.4~0.5: n=11161 avg_conf=0.4430 acc=0.3214 gap=0.1216
- 0.3~0.4: n=7895 avg_conf=0.3694 acc=0.3322 gap=0.0371

---

## 전체 누적 (참고용 — Platt 보정 이전 raw conf 포함)

- Accuracy: 34.75%
- Brier score: 0.240457
- Log-loss: 1.205307
- ECE: 0.135007

### Worst Confidence Bins (전체)

- 0.8~0.9: n=1291 avg_conf=0.8393 acc=0.3261 gap=0.5132
- 0.7~0.8: n=1893 avg_conf=0.7421 acc=0.3634 gap=0.3787
- 0.6~0.7: n=4528 avg_conf=0.6455 acc=0.3293 gap=0.3162
- 0.5~0.6: n=13266 avg_conf=0.5309 acc=0.3634 gap=0.1675
- 0.4~0.5: n=22068 avg_conf=0.4470 acc=0.3433 gap=0.1038
- 0.3~0.4: n=13454 avg_conf=0.3673 acc=0.3447 gap=0.0226

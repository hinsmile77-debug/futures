# Calibration Report

- Generated at: 2026-06-26 15:24:26
- Platt 보정기 도입 이후(since 2026-06-04) 검증 예측: 28162건
- 전체 누적 검증 예측: 59576건

## 최근 (Platt 보정 이후) — 현재 모델 성능 기준

- Accuracy: 32.30%
- Brier score: 0.239969
- Log-loss: 1.205848
- ECE: 0.130434

### 호라이즌별 (최근)

#### 10m
- Count: 4611  Accuracy: 31.42%  Brier: 0.243124  ECE: 0.147052

#### 15m
- Count: 4577  Accuracy: 31.68%  Brier: 0.251918  ECE: 0.181142

#### 1m
- Count: 5059  Accuracy: 35.17%  Brier: 0.223661  ECE: 0.066729

#### 30m
- Count: 4643  Accuracy: 30.63%  Brier: 0.246293  ECE: 0.158548

#### 3m
- Count: 4701  Accuracy: 31.46%  Brier: 0.236993  ECE: 0.116682

#### 5m
- Count: 4571  Accuracy: 33.17%  Brier: 0.239508  ECE: 0.118989

### Worst Confidence Bins (최근)

- 0.8~0.9: n=220 avg_conf=0.8465 acc=0.3136 gap=0.5328
- 0.7~0.8: n=319 avg_conf=0.7344 acc=0.2947 gap=0.4397
- 0.6~0.7: n=1601 avg_conf=0.6392 acc=0.2917 gap=0.3475
- 0.5~0.6: n=4504 avg_conf=0.5416 acc=0.3217 gap=0.2199
- 0.4~0.5: n=12678 avg_conf=0.4430 acc=0.3228 gap=0.1202
- 0.3~0.4: n=8840 avg_conf=0.3697 acc=0.3307 gap=0.0391

---

## 전체 누적 (참고용 — Platt 보정 이전 raw conf 포함)

- Accuracy: 34.62%
- Brier score: 0.240163
- Log-loss: 1.203156
- ECE: 0.134523

### Worst Confidence Bins (전체)

- 0.8~0.9: n=1291 avg_conf=0.8393 acc=0.3261 gap=0.5132
- 0.7~0.8: n=1927 avg_conf=0.7419 acc=0.3659 gap=0.3761
- 0.6~0.7: n=4668 avg_conf=0.6454 acc=0.3271 gap=0.3182
- 0.5~0.6: n=13706 avg_conf=0.5312 acc=0.3613 gap=0.1699
- 0.4~0.5: n=23585 avg_conf=0.4468 acc=0.3426 gap=0.1042
- 0.3~0.4: n=14399 avg_conf=0.3676 acc=0.3429 gap=0.0248

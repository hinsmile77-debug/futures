# Calibration Report

- Generated at: 2026-07-01 12:57:16
- Platt 보정기 도입 이후(since 2026-06-04) 검증 예측: 30873건
- 전체 누적 검증 예측: 62287건

## 최근 (Platt 보정 이후) — 현재 모델 성능 기준

- Accuracy: 32.65%
- Brier score: 0.238789
- Log-loss: 1.198513
- ECE: 0.123255

### 호라이즌별 (최근)

#### 10m
- Count: 4808  Accuracy: 31.57%  Brier: 0.242589  ECE: 0.143839

#### 15m
- Count: 4710  Accuracy: 31.83%  Brier: 0.251684  ECE: 0.178499

#### 1m
- Count: 6029  Accuracy: 34.88%  Brier: 0.224000  ECE: 0.066166

#### 30m
- Count: 5528  Accuracy: 32.05%  Brier: 0.242618  ECE: 0.138402

#### 3m
- Count: 5028  Accuracy: 31.88%  Brier: 0.236174  ECE: 0.109728

#### 5m
- Count: 4770  Accuracy: 33.25%  Brier: 0.239238  ECE: 0.116819

### Worst Confidence Bins (최근)

- 0.8~0.9: n=220 avg_conf=0.8465 acc=0.3136 gap=0.5328
- 0.7~0.8: n=320 avg_conf=0.7344 acc=0.2938 gap=0.4406
- 0.6~0.7: n=1654 avg_conf=0.6394 acc=0.3023 gap=0.3371
- 0.5~0.6: n=4655 avg_conf=0.5416 acc=0.3199 gap=0.2218
- 0.4~0.5: n=13852 avg_conf=0.4423 acc=0.3258 gap=0.1165
- 0.3~0.4: n=10172 avg_conf=0.3695 acc=0.3358 gap=0.0337

---

## 전체 누적 (참고용 — Platt 보정 이전 raw conf 포함)

- Accuracy: 34.69%
- Brier score: 0.239570
- Log-loss: 1.199637
- ECE: 0.130786

### Worst Confidence Bins (전체)

- 0.8~0.9: n=1291 avg_conf=0.8393 acc=0.3261 gap=0.5132
- 0.7~0.8: n=1928 avg_conf=0.7419 acc=0.3657 gap=0.3763
- 0.6~0.7: n=4721 avg_conf=0.6453 acc=0.3304 gap=0.3149
- 0.5~0.6: n=13857 avg_conf=0.5313 acc=0.3603 gap=0.1710
- 0.4~0.5: n=24759 avg_conf=0.4462 acc=0.3433 gap=0.1029
- 0.3~0.4: n=15731 avg_conf=0.3677 acc=0.3452 gap=0.0225

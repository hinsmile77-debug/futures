# Calibration Report

- Generated at: 2026-06-09 14:47:04
- Platt 보정기 도입 이후(since 2026-06-04) 검증 예측: 7250건
- 전체 누적 검증 예측: 49658건

## 최근 (Platt 보정 이후) — 현재 모델 성능 기준

- Accuracy: 30.83%
- Brier score: 0.242951
- Log-loss: 1.205972
- ECE: 0.146800

### 호라이즌별 (최근)

#### 10m
- Count: 1207  Accuracy: 29.49%  Brier: 0.247009  ECE: 0.170181

#### 15m
- Count: 1218  Accuracy: 31.94%  Brier: 0.248766  ECE: 0.170285

#### 1m
- Count: 1215  Accuracy: 37.12%  Brier: 0.219803  ECE: 0.053879

#### 30m
- Count: 1175  Accuracy: 27.49%  Brier: 0.254389  ECE: 0.190755

#### 3m
- Count: 1206  Accuracy: 29.93%  Brier: 0.241816  ECE: 0.139762

#### 5m
- Count: 1229  Accuracy: 28.89%  Brier: 0.246264  ECE: 0.163109

### Worst Confidence Bins (최근)

- 0.7~0.8: n=5 avg_conf=0.7113 acc=0.2000 gap=0.5113
- 0.6~0.7: n=331 avg_conf=0.6318 acc=0.2628 gap=0.3689
- 0.5~0.6: n=1325 avg_conf=0.5362 acc=0.2891 gap=0.2471
- 0.4~0.5: n=3962 avg_conf=0.4462 acc=0.3087 gap=0.1375
- 0.3~0.4: n=1627 avg_conf=0.3739 acc=0.3325 gap=0.0413

---

## 전체 누적 (참고용 — Platt 보정 이전 raw conf 포함)

- Accuracy: 36.30%
- Brier score: 0.276686
- Log-loss: 3.496718
- ECE: 0.242563

### Worst Confidence Bins (전체)

- 0.9~1.0: n=10263 avg_conf=0.9994 acc=0.3941 gap=0.6053
- 0.8~0.9: n=1802 avg_conf=0.8570 acc=0.3169 gap=0.5402
- 0.7~0.8: n=1613 avg_conf=0.7433 acc=0.3794 gap=0.3639
- 0.6~0.7: n=3398 avg_conf=0.6469 acc=0.3376 gap=0.3094
- 0.5~0.6: n=10527 avg_conf=0.5273 acc=0.3691 gap=0.1582
- 0.4~0.5: n=14869 avg_conf=0.4499 acc=0.3505 gap=0.0994
- 0.3~0.4: n=7186 avg_conf=0.3665 acc=0.3556 gap=0.0109

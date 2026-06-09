# Rollout Readiness Report

- Generated at: 2026-06-09 14:47:05
- Recommended stage: small_size
- Reason: A/B 개선 확인 + calibration 양호 + meta 표본 충분

## Metrics

- Verified predictions: 49658
- Ensemble decisions: 7366
- Meta labels: 41162
- Overall ECE: 0.146800
- Enhanced vs baseline total PnL delta: +13.8200 pt

## Checklist

- Shadow telemetry present: yes
- Meta-label dataset ready: yes
- Calibration report generated: yes
- Meta tuning report generated: yes

## Stage Criteria

- `shadow`: telemetry/labels insufficient or calibration weak
- `alert_only`: A/B improvement exists but execution evidence still limited
- `small_size`: A/B positive, calibration acceptable, meta labels sufficiently accumulated
- `full`: only after repeated `small_size` validation and stable drawdown control

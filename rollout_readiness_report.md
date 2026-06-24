# Rollout Readiness Report

- Generated at: 2026-06-24 10:34:08
- Recommended stage: small_size
- Reason: A/B 개선 확인 + calibration 양호 + meta 표본 충분

## Metrics

- Verified predictions: 56500
- Ensemble decisions: 10953
- Meta labels: 59100
- Overall ECE: 0.131023
- Enhanced vs baseline total PnL delta: +125.8900 pt

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

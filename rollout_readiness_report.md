# Rollout Readiness Report

- Generated at: 2026-06-26 15:24:29
- Recommended stage: small_size
- Reason: A/B 개선 확인 + calibration 양호 + meta 표본 충분

## Metrics

- Verified predictions: 59576
- Ensemble decisions: 11879
- Meta labels: 62176
- Overall ECE: 0.130434
- Enhanced vs baseline total PnL delta: +240.0900 pt

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

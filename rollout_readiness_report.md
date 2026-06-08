# Rollout Readiness Report

- Generated at: 2026-06-08 10:17:32
- Recommended stage: alert_only
- Reason: A/B 개선 확인, 다만 calibration 또는 meta 표본 추가 필요

## Metrics

- Verified predictions: 46660
- Ensemble decisions: 6733
- Meta labels: 38164
- Overall ECE: 0.247990
- Enhanced vs baseline total PnL delta: +160.2500 pt

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

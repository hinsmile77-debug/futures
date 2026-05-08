# Rollout Readiness Report

- Generated at: 2026-05-08 14:33:46
- Recommended stage: shadow
- Reason: 실거래 확대 전 shadow/alert 단계 유지 권장

## Metrics

- Verified predictions: 8524
- Ensemble decisions: 21
- Meta labels: 18
- Overall ECE: 0.397556
- Enhanced vs baseline total PnL delta: +0.0000 pt

## Checklist

- Shadow telemetry present: yes
- Meta-label dataset ready: not yet
- Calibration report generated: yes
- Meta tuning report generated: yes

## Stage Criteria

- `shadow`: telemetry/labels insufficient or calibration weak
- `alert_only`: A/B improvement exists but execution evidence still limited
- `small_size`: A/B positive, calibration acceptable, meta labels sufficiently accumulated
- `full`: only after repeated `small_size` validation and stable drawdown control

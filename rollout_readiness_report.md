# Rollout Readiness Report

- Generated at: 2026-05-12 12:53:59
- Recommended stage: shadow
- Reason: 실거래 확대 전 shadow/alert 단계 유지 권장

## Metrics

- Verified predictions: 11975
- Ensemble decisions: 653
- Meta labels: 3469
- Overall ECE: 0.404116
- Enhanced vs baseline total PnL delta: -7.8000 pt

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

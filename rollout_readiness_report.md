# Rollout Readiness Report

- Generated at: 2026-07-02 15:25:35
- Recommended stage: small_size
- Reason: A/B 개선 확인 + calibration 양호 + meta 표본 충분

## Metrics

- Verified predictions: 63637
- Ensemble decisions: 13340
- Meta labels: 66237
- Overall ECE: 0.121370
- Enhanced vs baseline total PnL delta: +252.2700 pt

## Checklist

- Shadow telemetry present: yes
- Meta-label dataset ready: yes
- Calibration report generated: yes
- Meta tuning report generated: yes
- Confidence inversion: none

## Stage Criteria

- `shadow`: telemetry/labels insufficient or calibration weak
- `alert_only`: A/B improvement exists but execution evidence still limited
- `small_size`: A/B positive, calibration acceptable, meta labels sufficiently accumulated
- `full`: only after repeated `small_size` validation and stable drawdown control

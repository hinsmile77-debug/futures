# Meta Gate Tuning Report

- Generated at: 2026-05-08 14:34:00
- Horizon: 5m
- Source: meta_labels
- Samples: 3

## Distribution

- Realized actions: {'skip': 3}
- Avg meta confidence: 0.6667

## Threshold Grid

- take>=0.65, reduce>=0.54: match=66.67%, take=1, reduce=0, skip=2
- take>=0.67, reduce>=0.56: match=66.67%, take=1, reduce=0, skip=2
- take>=0.69, reduce>=0.58: match=66.67%, take=1, reduce=0, skip=2
- take>=0.71, reduce>=0.60: match=66.67%, take=1, reduce=0, skip=2

## Recommendation

- Best grid: take>=0.65, reduce>=0.54
- Best match rate: 66.67%

## Latest Samples

- 2026-05-08 14:25:00: meta_conf=1.0000 realized=skip correct=0 mlofi=-0.0299 mp_bias=-0.0031 queue=0.0436 cancel_add=0.0094
- 2026-05-08 14:26:00: meta_conf=0.5000 realized=skip correct=0 mlofi=-0.0234 mp_bias=0.0004 queue=-0.0376 cancel_add=0.0096
- 2026-05-08 14:27:00: meta_conf=0.5000 realized=skip correct=0 mlofi=-0.0467 mp_bias=-0.0001 queue=-0.0176 cancel_add=0.0139

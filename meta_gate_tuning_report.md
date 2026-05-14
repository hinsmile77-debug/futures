# Meta Gate Tuning Report

- Generated at: 2026-05-14 14:10:02
- Horizon: 5m
- Source: meta_labels
- Samples: 1343

## Distribution

- Realized actions: {'skip': 825, 'reduce': 20, 'take': 498}
- Avg meta confidence: 0.8447

## Threshold Grid

- take>=0.65, reduce>=0.54: match=42.74%, take=994, reduce=1, skip=348
- take>=0.67, reduce>=0.56: match=42.74%, take=994, reduce=1, skip=348
- take>=0.69, reduce>=0.58: match=41.62%, take=955, reduce=39, skip=349
- take>=0.71, reduce>=0.60: match=41.62%, take=955, reduce=39, skip=349

## Recommendation

- Best grid: take>=0.65, reduce>=0.54
- Best match rate: 42.74%

## Latest Samples

- 2026-05-14 13:34:00: meta_conf=1.0000 realized=skip correct=0 mlofi=0.0620 mp_bias=0.0462 queue=-0.0796 cancel_add=-0.0005
- 2026-05-14 13:35:00: meta_conf=1.0000 realized=skip correct=0 mlofi=-0.0718 mp_bias=0.0308 queue=0.0055 cancel_add=-0.0051
- 2026-05-14 13:36:00: meta_conf=1.0000 realized=skip correct=0 mlofi=-0.0099 mp_bias=-0.0335 queue=0.0412 cancel_add=-0.0005
- 2026-05-14 13:37:00: meta_conf=1.0000 realized=skip correct=0 mlofi=0.0014 mp_bias=0.0243 queue=-0.0415 cancel_add=-0.0006
- 2026-05-14 13:38:00: meta_conf=1.0000 realized=skip correct=0 mlofi=0.1577 mp_bias=0.0562 queue=-0.0795 cancel_add=-0.0096
- 2026-05-14 13:39:00: meta_conf=1.0000 realized=skip correct=0 mlofi=-0.0140 mp_bias=-0.0005 queue=-0.0262 cancel_add=0.0094
- 2026-05-14 13:40:00: meta_conf=1.0000 realized=skip correct=0 mlofi=-0.0532 mp_bias=-0.0037 queue=-0.0575 cancel_add=0.0153
- 2026-05-14 13:41:00: meta_conf=1.0000 realized=skip correct=0 mlofi=0.0069 mp_bias=-0.0545 queue=-0.0528 cancel_add=-0.0028
- 2026-05-14 13:42:00: meta_conf=0.3334 realized=skip correct=0 mlofi=-0.0668 mp_bias=0.0150 queue=0.0530 cancel_add=0.0147
- 2026-05-14 14:04:00: meta_conf=0.3334 realized=take correct=1 mlofi=0.0194 mp_bias=0.0054 queue=0.0579 cancel_add=-0.0029

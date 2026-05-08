# Meta Gate Tuning Report

- Generated at: 2026-05-08 15:33:01
- Horizon: 5m
- Source: meta_labels
- Samples: 57

## Distribution

- Realized actions: {'skip': 46, 'reduce': 4, 'take': 7}
- Avg meta confidence: 0.8325

## Threshold Grid

- take>=0.65, reduce>=0.54: match=29.82%, take=41, reduce=0, skip=16
- take>=0.67, reduce>=0.56: match=29.82%, take=41, reduce=0, skip=16
- take>=0.69, reduce>=0.58: match=29.82%, take=41, reduce=0, skip=16
- take>=0.71, reduce>=0.60: match=29.82%, take=41, reduce=0, skip=16

## Recommendation

- Best grid: take>=0.65, reduce>=0.54
- Best match rate: 29.82%

## Latest Samples

- 2026-05-08 15:12:00: meta_conf=1.0000 realized=skip correct=0 mlofi=0.0523 mp_bias=-0.0011 queue=0.0596 cancel_add=0.0362
- 2026-05-08 15:13:00: meta_conf=1.0000 realized=skip correct=0 mlofi=-0.0179 mp_bias=0.0005 queue=0.0331 cancel_add=0.0184
- 2026-05-08 15:14:00: meta_conf=1.0000 realized=skip correct=0 mlofi=0.0414 mp_bias=-0.0012 queue=0.0129 cancel_add=0.0244
- 2026-05-08 15:15:00: meta_conf=1.0000 realized=skip correct=0 mlofi=0.0337 mp_bias=-0.0026 queue=0.0208 cancel_add=0.0172
- 2026-05-08 15:16:00: meta_conf=1.0000 realized=skip correct=0 mlofi=0.0093 mp_bias=-0.0004 queue=-0.0195 cancel_add=0.0137
- 2026-05-08 15:17:00: meta_conf=0.3334 realized=reduce correct=1 mlofi=0.0028 mp_bias=-0.0013 queue=-0.0417 cancel_add=0.0176
- 2026-05-08 15:18:00: meta_conf=1.0000 realized=skip correct=0 mlofi=0.0258 mp_bias=-0.0037 queue=0.0506 cancel_add=0.0419
- 2026-05-08 15:19:00: meta_conf=1.0000 realized=skip correct=0 mlofi=0.0029 mp_bias=-0.0006 queue=0.0140 cancel_add=0.0056
- 2026-05-08 15:21:00: meta_conf=1.0000 realized=skip correct=0 mlofi=-0.0620 mp_bias=-0.0035 queue=0.0359 cancel_add=0.0223
- 2026-05-08 15:22:00: meta_conf=1.0000 realized=skip correct=0 mlofi=0.0140 mp_bias=-0.0031 queue=0.0664 cancel_add=0.0125

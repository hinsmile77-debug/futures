# Meta Gate Tuning Report

- Generated at: 2026-05-14 12:31:02
- Horizon: 5m
- Source: meta_labels
- Samples: 1271

## Distribution

- Realized actions: {'skip': 771, 'reduce': 19, 'take': 481}
- Avg meta confidence: 0.8439

## Threshold Grid

- take>=0.65, reduce>=0.54: match=43.12%, take=940, reduce=1, skip=330
- take>=0.67, reduce>=0.56: match=43.12%, take=940, reduce=1, skip=330
- take>=0.69, reduce>=0.58: match=41.94%, take=901, reduce=39, skip=331
- take>=0.71, reduce>=0.60: match=41.94%, take=901, reduce=39, skip=331

## Recommendation

- Best grid: take>=0.65, reduce>=0.54
- Best match rate: 43.12%

## Latest Samples

- 2026-05-14 12:16:00: meta_conf=0.5000 realized=skip correct=0 mlofi=-0.0631 mp_bias=-0.0119 queue=0.0550 cancel_add=-0.0017
- 2026-05-14 12:17:00: meta_conf=0.5000 realized=skip correct=0 mlofi=-0.0631 mp_bias=-0.0030 queue=0.0274 cancel_add=-0.0004
- 2026-05-14 12:18:00: meta_conf=0.5000 realized=skip correct=0 mlofi=-0.0300 mp_bias=0.0013 queue=0.0036 cancel_add=-0.0007
- 2026-05-14 12:19:00: meta_conf=0.5000 realized=take correct=1 mlofi=-0.1157 mp_bias=-0.0025 queue=0.0069 cancel_add=0.0007
- 2026-05-14 12:20:00: meta_conf=0.5000 realized=take correct=1 mlofi=0.0475 mp_bias=-0.0130 queue=-0.0164 cancel_add=0.0013
- 2026-05-14 12:21:00: meta_conf=0.5000 realized=take correct=1 mlofi=0.1055 mp_bias=0.0081 queue=-0.0534 cancel_add=0.0003
- 2026-05-14 12:22:00: meta_conf=0.5000 realized=take correct=1 mlofi=-0.0420 mp_bias=0.0000 queue=-0.0027 cancel_add=0.0011
- 2026-05-14 12:23:00: meta_conf=0.5000 realized=take correct=1 mlofi=0.0318 mp_bias=0.0015 queue=0.0025 cancel_add=-0.0003
- 2026-05-14 12:24:00: meta_conf=0.5000 realized=take correct=1 mlofi=-0.0130 mp_bias=0.0016 queue=0.0366 cancel_add=-0.0026
- 2026-05-14 12:25:00: meta_conf=0.5000 realized=skip correct=0 mlofi=0.1314 mp_bias=0.0104 queue=-0.1456 cancel_add=-0.0005

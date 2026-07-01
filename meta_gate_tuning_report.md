# Meta Gate Tuning Report

- Generated at: 2026-07-01 14:18:17
- Horizon: 5m
- Source: meta_labels
- Samples: 9420

## Distribution

- Realized actions: {'skip': 7360, 'reduce': 622, 'take': 1438}
- Avg meta confidence: 0.4616

## Threshold Grid

- take>=0.65, reduce>=0.54: match=67.46%, take=405, reduce=1048, skip=7967
- take>=0.67, reduce>=0.56: match=69.81%, take=310, reduce=849, skip=8261
- take>=0.69, reduce>=0.58: match=71.77%, take=187, reduce=701, skip=8532
- take>=0.71, reduce>=0.60: match=73.50%, take=153, reduce=524, skip=8743

## Recommendation

- Best grid: take>=0.71, reduce>=0.60
- Best match rate: 73.50%

## Latest Samples

- 2026-07-01 13:23:00: meta_conf=0.4054 realized=skip correct=0 mlofi=0.0619 mp_bias=-0.0029 queue=0.0436 cancel_add=0.0006
- 2026-07-01 13:28:00: meta_conf=0.3550 realized=skip correct=0 mlofi=-0.0087 mp_bias=0.0016 queue=-0.0353 cancel_add=0.0032
- 2026-07-01 13:33:00: meta_conf=0.3550 realized=skip correct=1 mlofi=-0.0627 mp_bias=0.0013 queue=-0.0229 cancel_add=-0.0014
- 2026-07-01 13:38:00: meta_conf=0.3550 realized=skip correct=0 mlofi=0.0626 mp_bias=-0.0033 queue=0.0272 cancel_add=-0.0008
- 2026-07-01 13:43:00: meta_conf=0.3550 realized=skip correct=0 mlofi=-0.0347 mp_bias=-0.0031 queue=0.0628 cancel_add=0.0005
- 2026-07-01 13:48:00: meta_conf=0.3646 realized=skip correct=0 mlofi=0.0805 mp_bias=0.0008 queue=0.0491 cancel_add=0.0079
- 2026-07-01 13:53:00: meta_conf=0.3550 realized=take correct=1 mlofi=0.0285 mp_bias=-0.0010 queue=0.0072 cancel_add=0.0019
- 2026-07-01 13:58:00: meta_conf=0.3550 realized=skip correct=0 mlofi=0.0438 mp_bias=0.0025 queue=-0.0639 cancel_add=0.0072
- 2026-07-01 14:03:00: meta_conf=0.3600 realized=skip correct=0 mlofi=0.0340 mp_bias=-0.0023 queue=0.0218 cancel_add=0.0018
- 2026-07-01 14:08:00: meta_conf=0.3600 realized=skip correct=0 mlofi=0.0411 mp_bias=-0.0011 queue=0.0484 cancel_add=0.0009

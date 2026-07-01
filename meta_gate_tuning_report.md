# Meta Gate Tuning Report

- Generated at: 2026-07-01 14:01:17
- Horizon: 5m
- Source: meta_labels
- Samples: 9417

## Distribution

- Realized actions: {'skip': 7357, 'reduce': 622, 'take': 1438}
- Avg meta confidence: 0.4617

## Threshold Grid

- take>=0.65, reduce>=0.54: match=67.45%, take=405, reduce=1048, skip=7964
- take>=0.67, reduce>=0.56: match=69.80%, take=310, reduce=849, skip=8258
- take>=0.69, reduce>=0.58: match=71.76%, take=187, reduce=701, skip=8529
- take>=0.71, reduce>=0.60: match=73.49%, take=153, reduce=524, skip=8740

## Recommendation

- Best grid: take>=0.71, reduce>=0.60
- Best match rate: 73.49%

## Latest Samples

- 2026-07-01 13:08:00: meta_conf=0.3551 realized=skip correct=0 mlofi=-0.0060 mp_bias=-0.0049 queue=0.0660 cancel_add=0.0085
- 2026-07-01 13:13:00: meta_conf=0.3872 realized=skip correct=0 mlofi=0.0150 mp_bias=-0.0012 queue=0.0063 cancel_add=-0.0008
- 2026-07-01 13:18:00: meta_conf=0.3550 realized=skip correct=0 mlofi=0.0144 mp_bias=0.0013 queue=0.0000 cancel_add=0.0001
- 2026-07-01 13:23:00: meta_conf=0.4054 realized=skip correct=0 mlofi=0.0619 mp_bias=-0.0029 queue=0.0436 cancel_add=0.0006
- 2026-07-01 13:28:00: meta_conf=0.3550 realized=skip correct=0 mlofi=-0.0087 mp_bias=0.0016 queue=-0.0353 cancel_add=0.0032
- 2026-07-01 13:33:00: meta_conf=0.3550 realized=skip correct=1 mlofi=-0.0627 mp_bias=0.0013 queue=-0.0229 cancel_add=-0.0014
- 2026-07-01 13:38:00: meta_conf=0.3550 realized=skip correct=0 mlofi=0.0626 mp_bias=-0.0033 queue=0.0272 cancel_add=-0.0008
- 2026-07-01 13:43:00: meta_conf=0.3550 realized=skip correct=0 mlofi=-0.0347 mp_bias=-0.0031 queue=0.0628 cancel_add=0.0005
- 2026-07-01 13:48:00: meta_conf=0.3646 realized=skip correct=0 mlofi=0.0805 mp_bias=0.0008 queue=0.0491 cancel_add=0.0079
- 2026-07-01 13:53:00: meta_conf=0.3550 realized=take correct=1 mlofi=0.0285 mp_bias=-0.0010 queue=0.0072 cancel_add=0.0019

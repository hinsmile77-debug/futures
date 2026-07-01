# Meta Gate Tuning Report

- Generated at: 2026-07-01 12:57:17
- Horizon: 5m
- Source: meta_labels
- Samples: 9404

## Distribution

- Realized actions: {'skip': 7345, 'reduce': 622, 'take': 1437}
- Avg meta confidence: 0.4618

## Threshold Grid

- take>=0.65, reduce>=0.54: match=67.42%, take=405, reduce=1048, skip=7951
- take>=0.67, reduce>=0.56: match=69.77%, take=310, reduce=849, skip=8245
- take>=0.69, reduce>=0.58: match=71.74%, take=187, reduce=701, skip=8516
- take>=0.71, reduce>=0.60: match=73.47%, take=153, reduce=524, skip=8727

## Recommendation

- Best grid: take>=0.71, reduce>=0.60
- Best match rate: 73.47%

## Latest Samples

- 2026-07-01 12:03:00: meta_conf=0.4508 realized=skip correct=0 mlofi=0.0146 mp_bias=-0.0025 queue=0.0654 cancel_add=-0.0010
- 2026-07-01 12:08:00: meta_conf=0.3699 realized=skip correct=1 mlofi=-0.0013 mp_bias=-0.0028 queue=0.0329 cancel_add=-0.0010
- 2026-07-01 12:13:00: meta_conf=0.3699 realized=skip correct=0 mlofi=0.0352 mp_bias=-0.0036 queue=0.0644 cancel_add=-0.0009
- 2026-07-01 12:18:00: meta_conf=0.3701 realized=skip correct=0 mlofi=0.0484 mp_bias=-0.0012 queue=0.0017 cancel_add=-0.0015
- 2026-07-01 12:23:00: meta_conf=0.3701 realized=skip correct=0 mlofi=-0.0311 mp_bias=0.0012 queue=-0.0036 cancel_add=0.0009
- 2026-07-01 12:28:00: meta_conf=0.3700 realized=skip correct=0 mlofi=-0.0427 mp_bias=0.0003 queue=0.0062 cancel_add=0.0011
- 2026-07-01 12:33:00: meta_conf=0.3781 realized=take correct=1 mlofi=0.0497 mp_bias=-0.0041 queue=0.0726 cancel_add=0.0022
- 2026-07-01 12:38:00: meta_conf=0.3742 realized=skip correct=0 mlofi=0.1142 mp_bias=0.0018 queue=0.0077 cancel_add=0.0296
- 2026-07-01 12:43:00: meta_conf=0.5207 realized=skip correct=0 mlofi=0.0334 mp_bias=0.0048 queue=-0.0436 cancel_add=0.0069
- 2026-07-01 12:48:00: meta_conf=0.3550 realized=take correct=1 mlofi=-0.0143 mp_bias=-0.0043 queue=0.0534 cancel_add=0.0042

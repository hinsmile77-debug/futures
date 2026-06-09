# Meta Gate Tuning Report

- Generated at: 2026-06-09 14:47:05
- Horizon: 5m
- Source: meta_labels
- Samples: 6986

## Distribution

- Realized actions: {'skip': 5238, 'reduce': 370, 'take': 1378}
- Avg meta confidence: 0.5620

## Threshold Grid

- take>=0.65, reduce>=0.54: match=61.88%, take=1497, reduce=617, skip=4872
- take>=0.67, reduce>=0.56: match=64.09%, take=1437, reduce=479, skip=5070
- take>=0.69, reduce>=0.58: match=65.66%, take=1363, reduce=396, skip=5227
- take>=0.71, reduce>=0.60: match=67.03%, take=1342, reduce=303, skip=5341

## Recommendation

- Best grid: take>=0.71, reduce>=0.60
- Best match rate: 67.03%

## Latest Samples

- 2026-06-09 13:18:00: meta_conf=0.4902 realized=skip correct=1 mlofi=0.0585 mp_bias=-0.0001 queue=0.0121 cancel_add=0.0176
- 2026-06-09 13:19:00: meta_conf=0.4883 realized=skip correct=1 mlofi=-0.0025 mp_bias=0.0040 queue=-0.1227 cancel_add=0.0089
- 2026-06-09 13:20:00: meta_conf=0.5134 realized=skip correct=0 mlofi=0.0067 mp_bias=-0.0006 queue=-0.0724 cancel_add=-0.0044
- 2026-06-09 13:22:00: meta_conf=0.5344 realized=skip correct=0 mlofi=0.0109 mp_bias=-0.0008 queue=-0.0606 cancel_add=0.0123
- 2026-06-09 13:31:00: meta_conf=0.4980 realized=skip correct=0 mlofi=-0.0743 mp_bias=-0.0001 queue=0.0014 cancel_add=0.0016
- 2026-06-09 13:32:00: meta_conf=0.4797 realized=skip correct=0 mlofi=0.0351 mp_bias=-0.0022 queue=0.0357 cancel_add=0.0037
- 2026-06-09 13:33:00: meta_conf=0.5382 realized=skip correct=0 mlofi=0.0525 mp_bias=-0.0032 queue=0.0669 cancel_add=0.0033
- 2026-06-09 14:27:00: meta_conf=0.3484 realized=skip correct=0 mlofi=-0.0743 mp_bias=0.0029 queue=-0.0340 cancel_add=-0.0028
- 2026-06-09 14:28:00: meta_conf=0.3448 realized=skip correct=0 mlofi=-0.0671 mp_bias=-0.0011 queue=-0.0092 cancel_add=0.0049
- 2026-06-09 14:31:00: meta_conf=0.3985 realized=skip correct=0 mlofi=0.1340 mp_bias=0.0101 queue=0.0136 cancel_add=0.0048

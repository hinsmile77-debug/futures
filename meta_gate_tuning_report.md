# Meta Gate Tuning Report

- Generated at: 2026-06-26 15:24:28
- Horizon: 5m
- Source: meta_labels
- Samples: 9205

## Distribution

- Realized actions: {'skip': 7191, 'reduce': 608, 'take': 1406}
- Avg meta confidence: 0.4627

## Threshold Grid

- take>=0.65, reduce>=0.54: match=67.33%, take=405, reduce=1034, skip=7766
- take>=0.67, reduce>=0.56: match=69.69%, take=310, reduce=840, skip=8055
- take>=0.69, reduce>=0.58: match=71.69%, take=187, reduce=694, skip=8324
- take>=0.71, reduce>=0.60: match=73.44%, take=153, reduce=519, skip=8533

## Recommendation

- Best grid: take>=0.71, reduce>=0.60
- Best match rate: 73.44%

## Latest Samples

- 2026-06-26 14:11:00: meta_conf=0.3934 realized=skip correct=0 mlofi=0.0335 mp_bias=-0.0029 queue=-0.0081 cancel_add=0.0096
- 2026-06-26 14:16:00: meta_conf=0.4264 realized=skip correct=1 mlofi=-0.0083 mp_bias=0.0020 queue=-0.0448 cancel_add=0.0177
- 2026-06-26 14:21:00: meta_conf=0.4185 realized=skip correct=0 mlofi=-0.0015 mp_bias=-0.0072 queue=0.0501 cancel_add=0.0068
- 2026-06-26 14:26:00: meta_conf=0.4312 realized=skip correct=0 mlofi=0.1209 mp_bias=-0.0022 queue=-0.0226 cancel_add=0.0121
- 2026-06-26 14:31:00: meta_conf=0.4110 realized=skip correct=0 mlofi=0.0801 mp_bias=0.0012 queue=-0.0104 cancel_add=0.0006
- 2026-06-26 14:36:00: meta_conf=0.4993 realized=take correct=1 mlofi=0.0092 mp_bias=0.0040 queue=-0.0148 cancel_add=0.0022
- 2026-06-26 14:41:00: meta_conf=0.4532 realized=take correct=1 mlofi=-0.0201 mp_bias=0.0042 queue=-0.0123 cancel_add=-0.0004
- 2026-06-26 14:51:00: meta_conf=0.3799 realized=skip correct=1 mlofi=0.0052 mp_bias=0.0030 queue=0.0167 cancel_add=-0.0007
- 2026-06-26 14:56:00: meta_conf=0.4762 realized=skip correct=0 mlofi=0.0546 mp_bias=0.0046 queue=-0.0197 cancel_add=0.0057
- 2026-06-26 15:01:00: meta_conf=0.3788 realized=reduce correct=1 mlofi=0.0024 mp_bias=-0.0028 queue=0.0240 cancel_add=0.0035

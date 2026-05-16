# Meta Gate Tuning Report

- Generated at: 2026-05-15 15:24:02
- Horizon: 5m
- Source: meta_labels
- Samples: 1683

## Distribution

- Realized actions: {'skip': 1003, 'reduce': 31, 'take': 649}
- Avg meta confidence: 0.8061

## Threshold Grid

- take>=0.65, reduce>=0.54: match=43.85%, take=1112, reduce=1, skip=570
- take>=0.67, reduce>=0.56: match=43.85%, take=1112, reduce=1, skip=570
- take>=0.69, reduce>=0.58: match=42.96%, take=1073, reduce=39, skip=571
- take>=0.71, reduce>=0.60: match=42.96%, take=1073, reduce=39, skip=571

## Recommendation

- Best grid: take>=0.65, reduce>=0.54
- Best match rate: 43.85%

## Latest Samples

- 2026-05-15 15:09:00: meta_conf=0.4802 realized=skip correct=0 mlofi=0.0130 mp_bias=-0.0012 queue=0.0322 cancel_add=0.0077
- 2026-05-15 15:10:00: meta_conf=0.4802 realized=take correct=1 mlofi=-0.0599 mp_bias=-0.0005 queue=0.0220 cancel_add=0.0081
- 2026-05-15 15:11:00: meta_conf=0.4802 realized=skip correct=0 mlofi=-0.0645 mp_bias=-0.0034 queue=0.0696 cancel_add=0.0091
- 2026-05-15 15:12:00: meta_conf=0.4802 realized=skip correct=0 mlofi=-0.0257 mp_bias=-0.0009 queue=0.0387 cancel_add=0.0045
- 2026-05-15 15:13:00: meta_conf=0.4802 realized=skip correct=0 mlofi=0.0455 mp_bias=-0.0013 queue=0.0309 cancel_add=0.0025
- 2026-05-15 15:14:00: meta_conf=0.4802 realized=skip correct=0 mlofi=0.0432 mp_bias=0.0009 queue=0.0349 cancel_add=0.0027
- 2026-05-15 15:15:00: meta_conf=0.4802 realized=take correct=1 mlofi=0.0553 mp_bias=-0.0005 queue=0.0332 cancel_add=0.0060
- 2026-05-15 15:16:00: meta_conf=0.4802 realized=take correct=1 mlofi=0.1334 mp_bias=0.0011 queue=0.0142 cancel_add=0.0218
- 2026-05-15 15:17:00: meta_conf=0.4802 realized=skip correct=0 mlofi=0.0794 mp_bias=0.0067 queue=-0.0729 cancel_add=0.0033
- 2026-05-15 15:18:00: meta_conf=0.4802 realized=skip correct=0 mlofi=0.0204 mp_bias=0.0030 queue=-0.0089 cancel_add=0.0172

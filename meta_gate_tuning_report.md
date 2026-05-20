# Meta Gate Tuning Report

- Generated at: 2026-05-20 15:33:02
- Horizon: 5m
- Source: meta_labels
- Samples: 2751

## Distribution

- Realized actions: {'skip': 1754, 'reduce': 96, 'take': 901}
- Avg meta confidence: 0.7242

## Threshold Grid

- take>=0.65, reduce>=0.54: match=46.09%, take=1423, reduce=180, skip=1148
- take>=0.67, reduce>=0.56: match=47.07%, take=1408, reduce=148, skip=1195
- take>=0.69, reduce>=0.58: match=47.84%, take=1347, reduce=158, skip=1246
- take>=0.71, reduce>=0.60: match=48.38%, take=1333, reduce=148, skip=1270

## Recommendation

- Best grid: take>=0.71, reduce>=0.60
- Best match rate: 48.38%

## Latest Samples

- 2026-05-20 15:14:00: meta_conf=0.5677 realized=skip correct=0 mlofi=0.0492 mp_bias=0.0032 queue=-0.0013 cancel_add=0.0023
- 2026-05-20 15:15:00: meta_conf=0.5169 realized=skip correct=0 mlofi=0.0067 mp_bias=0.0004 queue=0.0267 cancel_add=0.0045
- 2026-05-20 15:16:00: meta_conf=0.4854 realized=reduce correct=1 mlofi=0.0186 mp_bias=0.0001 queue=-0.0058 cancel_add=0.0024
- 2026-05-20 15:17:00: meta_conf=0.5450 realized=take correct=1 mlofi=0.0179 mp_bias=0.0009 queue=-0.0135 cancel_add=0.0024
- 2026-05-20 15:18:00: meta_conf=0.4549 realized=reduce correct=1 mlofi=-0.0436 mp_bias=0.0013 queue=-0.0163 cancel_add=0.0125
- 2026-05-20 15:19:00: meta_conf=0.5602 realized=take correct=1 mlofi=-0.0050 mp_bias=-0.0006 queue=0.0153 cancel_add=0.0010
- 2026-05-20 15:20:00: meta_conf=0.5242 realized=take correct=1 mlofi=-0.0276 mp_bias=-0.0034 queue=0.0321 cancel_add=0.0027
- 2026-05-20 15:21:00: meta_conf=0.4910 realized=reduce correct=1 mlofi=-0.0207 mp_bias=-0.0091 queue=0.0966 cancel_add=0.0091
- 2026-05-20 15:22:00: meta_conf=0.5418 realized=reduce correct=1 mlofi=-0.0133 mp_bias=0.0026 queue=-0.0154 cancel_add=0.0011
- 2026-05-20 15:23:00: meta_conf=0.5159 realized=skip correct=0 mlofi=-0.0072 mp_bias=0.0001 queue=-0.0064 cancel_add=0.0000

# Meta Gate Tuning Report

- Generated at: 2026-05-12 12:53:59
- Horizon: 5m
- Source: meta_labels
- Samples: 601

## Distribution

- Realized actions: {'skip': 380, 'reduce': 12, 'take': 209}
- Avg meta confidence: 0.8229

## Threshold Grid

- take>=0.65, reduce>=0.54: match=45.92%, take=433, reduce=1, skip=167
- take>=0.67, reduce>=0.56: match=45.92%, take=433, reduce=1, skip=167
- take>=0.69, reduce>=0.58: match=43.43%, take=394, reduce=39, skip=168
- take>=0.71, reduce>=0.60: match=43.43%, take=394, reduce=39, skip=168

## Recommendation

- Best grid: take>=0.65, reduce>=0.54
- Best match rate: 45.92%

## Latest Samples

- 2026-05-12 12:39:00: meta_conf=1.0000 realized=skip correct=0 mlofi=-0.0539 mp_bias=0.0006 queue=-0.0241 cancel_add=0.0037
- 2026-05-12 12:40:00: meta_conf=1.0000 realized=skip correct=0 mlofi=0.0280 mp_bias=-0.0010 queue=-0.0138 cancel_add=-0.0024
- 2026-05-12 12:41:00: meta_conf=1.0000 realized=skip correct=0 mlofi=0.0173 mp_bias=-0.0024 queue=0.0167 cancel_add=-0.0015
- 2026-05-12 12:42:00: meta_conf=1.0000 realized=skip correct=0 mlofi=0.0098 mp_bias=-0.0069 queue=0.0332 cancel_add=-0.0063
- 2026-05-12 12:43:00: meta_conf=1.0000 realized=skip correct=0 mlofi=-0.0255 mp_bias=-0.0020 queue=-0.0048 cancel_add=0.0094
- 2026-05-12 12:44:00: meta_conf=1.0000 realized=skip correct=0 mlofi=-0.0214 mp_bias=-0.0049 queue=0.0435 cancel_add=-0.0016
- 2026-05-12 12:45:00: meta_conf=1.0000 realized=skip correct=0 mlofi=-0.0194 mp_bias=0.0055 queue=0.0092 cancel_add=-0.0012
- 2026-05-12 12:46:00: meta_conf=1.0000 realized=take correct=1 mlofi=-0.1296 mp_bias=-0.0038 queue=0.0097 cancel_add=0.0007
- 2026-05-12 12:47:00: meta_conf=1.0000 realized=skip correct=0 mlofi=-0.0063 mp_bias=0.0024 queue=0.0108 cancel_add=-0.0025
- 2026-05-12 12:48:00: meta_conf=1.0000 realized=skip correct=0 mlofi=0.0068 mp_bias=-0.0106 queue=0.0022 cancel_add=-0.0054

# Meta Gate Tuning Report

- Generated at: 2026-06-24 10:34:08
- Horizon: 5m
- Source: meta_labels
- Samples: 8859

## Distribution

- Realized actions: {'skip': 6895, 'reduce': 593, 'take': 1371}
- Avg meta confidence: 0.4628

## Threshold Grid

- take>=0.65, reduce>=0.54: match=67.23%, take=394, reduce=985, skip=7480
- take>=0.67, reduce>=0.56: match=69.50%, take=301, reduce=808, skip=7750
- take>=0.69, reduce>=0.58: match=71.44%, take=180, reduce=672, skip=8007
- take>=0.71, reduce>=0.60: match=73.16%, take=147, reduce=505, skip=8207

## Recommendation

- Best grid: take>=0.71, reduce>=0.60
- Best match rate: 73.16%

## Latest Samples

- 2026-06-24 10:19:00: meta_conf=0.4502 realized=skip correct=0 mlofi=0.0048 mp_bias=-0.0008 queue=-0.0168 cancel_add=-0.0001
- 2026-06-24 10:20:00: meta_conf=0.4580 realized=skip correct=0 mlofi=0.0174 mp_bias=0.0041 queue=-0.0535 cancel_add=0.0110
- 2026-06-24 10:21:00: meta_conf=0.4353 realized=skip correct=0 mlofi=0.0146 mp_bias=0.0155 queue=-0.0594 cancel_add=0.0222
- 2026-06-24 10:22:00: meta_conf=0.4515 realized=skip correct=0 mlofi=0.0133 mp_bias=0.0035 queue=-0.0139 cancel_add=0.0129
- 2026-06-24 10:23:00: meta_conf=0.4942 realized=skip correct=0 mlofi=0.0943 mp_bias=-0.0110 queue=0.0304 cancel_add=0.0050
- 2026-06-24 10:24:00: meta_conf=0.3501 realized=skip correct=1 mlofi=0.0667 mp_bias=-0.0015 queue=0.0115 cancel_add=0.0027
- 2026-06-24 10:25:00: meta_conf=0.4536 realized=reduce correct=1 mlofi=0.0147 mp_bias=0.0002 queue=-0.0229 cancel_add=0.0129
- 2026-06-24 10:26:00: meta_conf=0.4981 realized=skip correct=0 mlofi=-0.0569 mp_bias=0.0015 queue=-0.0077 cancel_add=0.0008
- 2026-06-24 10:27:00: meta_conf=0.4498 realized=skip correct=0 mlofi=-0.0272 mp_bias=0.0087 queue=-0.0134 cancel_add=0.0081
- 2026-06-24 10:28:00: meta_conf=0.4844 realized=skip correct=0 mlofi=-0.0370 mp_bias=0.0008 queue=0.0117 cancel_add=0.0053

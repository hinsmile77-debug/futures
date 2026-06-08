# Meta Gate Tuning Report

- Generated at: 2026-06-08 10:17:32
- Horizon: 5m
- Source: meta_labels
- Samples: 6499

## Distribution

- Realized actions: {'skip': 4833, 'reduce': 352, 'take': 1314}
- Avg meta confidence: 0.5702

## Threshold Grid

- take>=0.65, reduce>=0.54: match=60.36%, take=1497, reduce=611, skip=4391
- take>=0.67, reduce>=0.56: match=62.66%, take=1437, reduce=479, skip=4583
- take>=0.69, reduce>=0.58: match=64.35%, take=1363, reduce=396, skip=4740
- take>=0.71, reduce>=0.60: match=65.83%, take=1342, reduce=303, skip=4854

## Recommendation

- Best grid: take>=0.71, reduce>=0.60
- Best match rate: 65.83%

## Latest Samples

- 2026-06-08 10:02:00: meta_conf=0.5266 realized=skip correct=0 mlofi=0.0257 mp_bias=0.0044 queue=-0.0012 cancel_add=0.0118
- 2026-06-08 10:03:00: meta_conf=0.5260 realized=skip correct=0 mlofi=-0.0466 mp_bias=0.0043 queue=-0.0138 cancel_add=0.0055
- 2026-06-08 10:04:00: meta_conf=0.4935 realized=skip correct=1 mlofi=-0.0303 mp_bias=-0.0020 queue=-0.0019 cancel_add=0.0070
- 2026-06-08 10:05:00: meta_conf=0.4947 realized=skip correct=0 mlofi=-0.0516 mp_bias=0.0005 queue=0.0010 cancel_add=0.0076
- 2026-06-08 10:06:00: meta_conf=0.4963 realized=skip correct=0 mlofi=-0.0313 mp_bias=-0.0010 queue=-0.0112 cancel_add=0.0115
- 2026-06-08 10:07:00: meta_conf=0.4967 realized=skip correct=0 mlofi=0.0017 mp_bias=-0.0017 queue=0.0226 cancel_add=0.0181
- 2026-06-08 10:08:00: meta_conf=0.4862 realized=skip correct=0 mlofi=-0.0082 mp_bias=-0.0021 queue=-0.0078 cancel_add=0.0185
- 2026-06-08 10:09:00: meta_conf=0.4860 realized=take correct=1 mlofi=-0.0271 mp_bias=-0.0041 queue=0.0090 cancel_add=0.0042
- 2026-06-08 10:10:00: meta_conf=0.4878 realized=skip correct=0 mlofi=-0.0651 mp_bias=-0.0013 queue=-0.0430 cancel_add=0.0241
- 2026-06-08 10:11:00: meta_conf=0.4906 realized=take correct=1 mlofi=-0.0529 mp_bias=-0.0082 queue=0.0312 cancel_add=0.0035

# Meta Gate Tuning Report

- Generated at: 2026-05-20 10:50:02
- Horizon: 5m
- Source: meta_labels
- Samples: 2504

## Distribution

- Realized actions: {'skip': 1597, 'reduce': 74, 'take': 833}
- Avg meta confidence: 0.7464

## Threshold Grid

- take>=0.65, reduce>=0.54: match=45.53%, take=1411, reduce=121, skip=972
- take>=0.67, reduce>=0.56: match=46.33%, take=1399, reduce=103, skip=1002
- take>=0.69, reduce>=0.58: match=46.96%, take=1343, reduce=123, skip=1038
- take>=0.71, reduce>=0.60: match=47.60%, take=1332, reduce=114, skip=1058

## Recommendation

- Best grid: take>=0.71, reduce>=0.60
- Best match rate: 47.60%

## Latest Samples

- 2026-05-20 10:35:00: meta_conf=0.6868 realized=take correct=1 mlofi=0.0480 mp_bias=0.0005 queue=-0.0180 cancel_add=0.0042
- 2026-05-20 10:36:00: meta_conf=0.6484 realized=reduce correct=1 mlofi=0.0349 mp_bias=0.0043 queue=-0.0438 cancel_add=0.0021
- 2026-05-20 10:37:00: meta_conf=0.7521 realized=skip correct=0 mlofi=0.0076 mp_bias=0.0003 queue=0.0110 cancel_add=0.0017
- 2026-05-20 10:38:00: meta_conf=0.8052 realized=skip correct=0 mlofi=0.0176 mp_bias=-0.0005 queue=-0.0009 cancel_add=0.0040
- 2026-05-20 10:39:00: meta_conf=0.7946 realized=skip correct=0 mlofi=-0.0014 mp_bias=0.0024 queue=-0.0130 cancel_add=0.0007
- 2026-05-20 10:40:00: meta_conf=0.5942 realized=skip correct=0 mlofi=-0.0325 mp_bias=-0.0074 queue=0.0687 cancel_add=0.0015
- 2026-05-20 10:41:00: meta_conf=0.7185 realized=skip correct=0 mlofi=0.0219 mp_bias=0.0020 queue=-0.0218 cancel_add=0.0012
- 2026-05-20 10:42:00: meta_conf=0.5683 realized=skip correct=1 mlofi=0.0357 mp_bias=0.0020 queue=-0.0011 cancel_add=0.0022
- 2026-05-20 10:43:00: meta_conf=0.4369 realized=skip correct=0 mlofi=-0.0435 mp_bias=-0.0052 queue=0.0323 cancel_add=0.0009
- 2026-05-20 10:44:00: meta_conf=0.4174 realized=take correct=1 mlofi=-0.0057 mp_bias=-0.0032 queue=0.0174 cancel_add=0.0007

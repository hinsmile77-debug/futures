# Meta Gate Tuning Report

- Generated at: 2026-07-02 15:25:34
- Horizon: 5m
- Source: meta_labels
- Samples: 9499

## Distribution

- Realized actions: {'skip': 7427, 'reduce': 626, 'take': 1446}
- Avg meta confidence: 0.2172

## Threshold Grid

- take>=0.65, reduce>=0.54: match=75.02%, take=109, reduce=425, skip=8965
- take>=0.67, reduce>=0.56: match=75.66%, take=81, reduce=364, skip=9054
- take>=0.69, reduce>=0.58: match=75.89%, take=52, reduce=318, skip=9129
- take>=0.71, reduce>=0.60: match=76.40%, take=33, reduce=244, skip=9222

## Recommendation

- Best grid: take>=0.71, reduce>=0.60
- Best match rate: 76.40%

## Latest Samples

- 2026-07-02 14:13:00: meta_conf=0.3699 realized=skip correct=0 mlofi=-0.0250 mp_bias=-0.0007 queue=0.0251 cancel_add=0.0017
- 2026-07-02 14:18:00: meta_conf=0.0000 realized=skip correct=0 mlofi=0.0215 mp_bias=0.0028 queue=-0.0441 cancel_add=0.0030
- 2026-07-02 14:23:00: meta_conf=0.3677 realized=skip correct=0 mlofi=-0.0744 mp_bias=-0.0032 queue=0.0401 cancel_add=0.0008
- 2026-07-02 14:28:00: meta_conf=0.3025 realized=skip correct=0 mlofi=0.0019 mp_bias=0.0036 queue=-0.0613 cancel_add=-0.0015
- 2026-07-02 14:33:00: meta_conf=0.3950 realized=skip correct=0 mlofi=0.0123 mp_bias=0.0031 queue=-0.0695 cancel_add=-0.0017
- 2026-07-02 14:38:00: meta_conf=0.4185 realized=skip correct=0 mlofi=-0.0205 mp_bias=-0.0065 queue=0.0431 cancel_add=0.0129
- 2026-07-02 14:43:00: meta_conf=0.3560 realized=skip correct=0 mlofi=0.0432 mp_bias=0.0032 queue=-0.0380 cancel_add=0.0063
- 2026-07-02 14:48:00: meta_conf=0.3391 realized=skip correct=0 mlofi=-0.0099 mp_bias=0.0023 queue=-0.0540 cancel_add=0.0081
- 2026-07-02 14:53:00: meta_conf=0.3709 realized=reduce correct=1 mlofi=-0.0458 mp_bias=-0.0083 queue=0.0809 cancel_add=0.0043
- 2026-07-02 14:58:00: meta_conf=0.0000 realized=take correct=1 mlofi=-0.0702 mp_bias=0.0021 queue=-0.0032 cancel_add=0.0132

# scripts/train_quantile_regressor.py
"""
[260704 감사 P2] 분위 회귀(q10/q50/q90) 채널 학습 — 수동/스케줄 실행 전용.

호라이즌별 N분 후 가격변동(포인트)의 q10/q50/q90을 추정하는 회귀 모델을 학습해
model/horizons/quantile/에 저장한다. 실거래 사이징/TP 거리 산정에는 아직
연결되지 않음 — ensemble_decisions에 섀도우 신호로만 로깅한다.

실행 (py310_64 환경 — batch_retrainer와 동일 재학습 환경):
    conda activate py310_64
    python scripts/train_quantile_regressor.py [--weeks 26]
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from learning.quantile_regressor import train_quantile_models


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weeks", type=int, default=26, help="학습 기간 (주)")
    args = parser.parse_args()

    result = train_quantile_models(weeks_back=args.weeks)
    if not result.get("ok"):
        print("실패:", result.get("error"))
        sys.exit(1)

    print(f"모델 저장 위치: {result['model_dir']}")
    print(f"{'호라이즌':6s} {'상태':6s} {'n':>8s} {'pinball':>8s} {'커버리지<q10':>12s} {'커버리지>q90':>12s}")
    for hz, r in result["horizons"].items():
        if not r.get("ok"):
            print(f"{hz:6s} {'실패':6s}  {r.get('error', '')}")
            continue
        print(
            f"{hz:6s} {'성공':6s} {r['n_samples']:8d} {r['pinball']:8.4f} "
            f"{r['coverage_below_q10']:12.3f} {r['coverage_above_q90']:12.3f}"
        )
    print("\n참고: 커버리지<q10은 이상적으로 ~0.10, 커버리지>q90은 ~0.10 근처여야 함")
    print("(실측이 크게 벗어나면 분위 추정이 편향됐다는 뜻 — GBR_PARAMS 조정 검토)")


if __name__ == "__main__":
    main()

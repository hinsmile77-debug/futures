# scripts/run_shadow_triple_barrier_retrain.py
"""
[260704 감사 P1] Triple-barrier 레이블 섀도우 병행 학습 — 수동/스케줄 실행 전용.

기존 3클래스(path-conditioned) 프로덕션 모델(model/horizon/gbm_{hz}.pkl)은
전혀 건드리지 않는다. 결과는 model/horizon/shadow_triple_barrier/ 에 저장되며
실거래 의사결정에는 사용되지 않는다 — 순수 병행(shadow) 검증용.

실행 (py310_64 환경 — batch_retrainer와 동일 재학습 환경):
    conda activate py310_64
    python scripts/run_shadow_triple_barrier_retrain.py [--weeks 26]

2~4주 매일(또는 EOD 후) 반복 실행 후, 섀도우 예측과 실제 거래 손익의 상관을
별도로 분석해 승격 여부를 판정한다 (ROADMAP.md Phase 5 이후 항목 참조).
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

from config.settings import RETRAIN_WEEKS_BACK
from learning.batch_retrainer import BatchRetrainer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weeks", type=int, default=RETRAIN_WEEKS_BACK,
                         help="학습 기간 (주, 기본 RETRAIN_WEEKS_BACK)")
    args = parser.parse_args()

    retrainer = BatchRetrainer()
    result = retrainer.retrain_shadow_triple_barrier(weeks_back=args.weeks)

    if not result.get("ok"):
        print("실패:", result.get("error"))
        sys.exit(1)

    print(f"섀도우 모델 저장 위치: {result['shadow_dir']}")
    print(f"{'호라이즌':6s} {'상태':6s} {'cv_acc':>8s} {'champion':>8s} {'n':>8s}  {'출처':22s}  레이블분포")
    for hz, r in result["horizons"].items():
        if not r.get("ok"):
            print(f"{hz:6s} {'실패':6s}  {r.get('error', '')}")
            continue
        print(
            f"{hz:6s} {'성공':6s} "
            f"{r['cv_acc'] if r['cv_acc'] is not None else float('nan'):8.4f} "
            f"{r['champion_cv_acc']:8.4f} "
            f"{r['n_samples']:8d}  {r['source']:22s}  {r['label_dist']}"
        )


if __name__ == "__main__":
    main()

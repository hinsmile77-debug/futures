# scripts/train_meta_label_classifier.py
"""
[260704 감사 P1] Meta-labeling 진입품질 분류기 학습 — 수동/스케줄 실행 전용.

meta_labels 테이블(65,000+건 축적, 그동안 학습에 쓰이지 않던 데이터)로 호라이즌별
이진 분류기("이 신호로 진입하면 실이익이 나는가")를 학습해 model/horizons/meta_gate/에
저장한다. strategy/entry/meta_gate.py가 섀도우 신호(entry_quality_prob)로 로드해 로깅만
하며, 실거래 진입 결정에는 아직 영향을 주지 않는다.

실행 (py310_64 환경 — batch_retrainer와 동일 재학습 환경):
    conda activate py310_64
    python scripts/train_meta_label_classifier.py [--min-rows 2000]
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

from learning.meta_label_classifier import train_entry_quality_models, MIN_ROWS_PER_HORIZON


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-rows", type=int, default=MIN_ROWS_PER_HORIZON,
                         help="호라이즌별 최소 학습 행 수")
    args = parser.parse_args()

    result = train_entry_quality_models(min_rows=args.min_rows)
    if not result.get("ok"):
        print("실패:", result.get("error"))
        sys.exit(1)

    print(f"모델 저장 위치: {result['model_dir']}")
    print(f"{'호라이즌':6s} {'상태':6s} {'AUC':>8s} {'n':>8s} {'양성비율':>8s}")
    for hz, r in result["horizons"].items():
        if not r.get("ok"):
            print(f"{hz:6s} {'실패':6s}  {r.get('error', '')}")
            continue
        print(
            f"{hz:6s} {'성공':6s} "
            f"{r['auc'] if r['auc'] is not None else float('nan'):8.4f} "
            f"{r['n_samples']:8d} {r['pos_rate']:8.4f}"
        )


if __name__ == "__main__":
    main()

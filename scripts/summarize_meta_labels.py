import sys

from config.settings import PREDICTIONS_DB
from utils.db_utils import fetchall


def main(limit: int = 20) -> None:
    rows = fetchall(
        PREDICTIONS_DB,
        """
        SELECT horizon, meta_action, COUNT(*) AS cnt, ROUND(AVG(meta_score), 4) AS avg_score
        FROM meta_labels
        GROUP BY horizon, meta_action
        ORDER BY horizon, meta_action
        """,
    )
    print(f"groups={len(rows)}")
    for row in rows:
        print(
            f"{row['horizon']:>4} | {row['meta_action']:<6} | "
            f"cnt={row['cnt']:<4} avg_score={row['avg_score']}"
        )

    latest = fetchall(
        PREDICTIONS_DB,
        """
        SELECT ts, horizon, predicted, actual, confidence, realized_move, threshold_move, meta_action
        FROM meta_labels
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    print(f"latest={len(latest)}")
    for row in latest:
        print(
            f"{row['ts']} {row['horizon']} pred={row['predicted']} actual={row['actual']} "
            f"conf={row['confidence']:.4f} move={row['realized_move']:.4f} "
            f"th={row['threshold_move']:.4f} action={row['meta_action']}"
        )


if __name__ == "__main__":
    arg = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    main(arg)

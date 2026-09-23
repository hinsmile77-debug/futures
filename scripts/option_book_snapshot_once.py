"""
[MW0601 623차] 옵션 만기북(먼스리·목위클리·월위클리) 스냅샷 1회 — 라이브 워커와 **같은 코드 경로**.

`OptionChainWorker.run()` 을 스레드 없이 동기로 부른다. 결과는 `OPTION_BOOK_DB` 에 쌓인다
(라이브와 같은 테이블 — 같은 원천·같은 계산이므로 섞여도 된다).

쓰임: 라이브 재기동 전 실측 · 장후 수동 확인. 조회 수는 먼스리 ≈48 + 위클리 ≈96.
한도(15초당 60건)를 라이브와 공유하므로 `OPTION_BOOK_QUOTA_RESERVE` 를 지켜 천천히 돈다.

    python scripts/option_book_snapshot_once.py [--spot 1118.4]
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def _kospi200_spot() -> float:
    """OptionCallput 헤더 3 = KOSPI200 현재가 (1요청)."""
    from win32com.client import Dispatch
    from collection.options.option_chain_worker import _filter_front_month
    with open("data/option_chain.json", encoding="utf-8") as f:
        chain = json.load(f)["chain"]
    ym = _filter_front_month(chain)[0]["ym"]
    o = Dispatch("Dscbo1.OptionCallput")
    o.SetInputValue(0, ym)
    o.BlockRequest()
    return float(o.GetHeaderValue(3))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spot", type=float, default=0.0)
    args = ap.parse_args()
    if struct.calcsize("P") != 4:
        print("32-bit Python 필요 (py37_32)")
        return 2
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s: %(message)s")

    import pythoncom
    pythoncom.CoInitialize()
    from win32com.client import Dispatch
    if not int(Dispatch("CpUtil.CpCybos").IsConnect):
        print("Cybos 미연결")
        return 2
    spot = args.spot or _kospi200_spot()
    print("spot=%.2f" % spot)

    import config.settings as S
    from collection.options.option_chain_worker import OptionChainWorker
    with open("data/option_chain.json", encoding="utf-8") as f:
        chain = json.load(f)["chain"]
    out = {}
    w = OptionChainWorker(
        chain_raw=chain, spot=spot, cache_path="data/option_chain.json",
        atm_window_pt=30.0, pause_ms=50,
        book_cfg={"db_path": S.OPTION_BOOK_DB, "master_dir": S.OPTION_BOOK_MASTER_DIR,
                  "fallbacks": S.OPTION_BOOK_MASTER_FALLBACKS,
                  "window": S.OPTION_BOOK_ATM_WINDOW_PT,
                  "reserve": S.OPTION_BOOK_QUOTA_RESERVE,
                  "budget_sec": S.OPTION_BOOK_BUDGET_SEC})
    w.result_ready.connect(lambda feats, _c: out.__setitem__("feats", feats))
    w.book_ready.connect(lambda s: out.__setitem__("books", s))
    w.run()                                   # 동기 — 스레드 시작 안 함
    print("먼스리 피처:", json.dumps(out.get("feats"), ensure_ascii=False))
    print(json.dumps(out.get("books"), ensure_ascii=False, indent=1, default=str))
    return 0 if out.get("books") else 1


if __name__ == "__main__":
    sys.exit(main())

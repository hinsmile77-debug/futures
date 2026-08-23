# scripts/generate_validation_campaign_report.py
"""
[260705 검증 캠페인] 섀도우 채널 주간 판정 리포트.

docs/260705_OFFENSE_READINESS_AUDIT_AND_NEXT_PHASE.md §3의 사전 등록 합격선
(config.settings.VALIDATION_CAMPAIGN — 변경 금지)에 대해 5개 채널의 KPI를
계산하고 PASS / FAIL / INSUFFICIENT를 판정한다.

  [1] Triple-Barrier: 섀도우 TB 모델 OOS 재생(replay) IC vs 프로덕션 3클래스 IC
  [2] Meta-Gate:      entry_quality_prob 3분위별 실현 순EV 분리도
  [3] 분위 회귀:       [q10,q90] 커버리지 + 불확실성-실현폭 상관
  [4] 신호소멸청산:    counterfactual 판정(resolve) + "아낀 pt − 놓친 pt" 누적
  [5] 레짐 ATR 배수:   hurst_bucket별 실거래 순EV

읽기 전용 진단 + signal_decay_exits.resolved 갱신만 수행 — 어떤 정책도
자동으로 켜거나 끄지 않는다. 판정 결과는 권고이며 적용은 수동(주간 회의)이다.

실행 (py310_64 — EOD 체인 scripts/eod_retrain.py가 금요일마다 자동 호출):
    python scripts/generate_validation_campaign_report.py [--days 28]

출력: 콘솔 + docs/정기점검/금요일점검/<PC명>/validation_campaign_report_YYYYMMDD.md
                                        + validation_campaign_metrics_YYYYMMDD.json

[MW0601 407차] 예전에는 data/에 고정 파일명으로 썼다. 두 가지가 문제였다 —
(1) data/는 gitignore라 **다른 PC에서 볼 수 없어** PC간 대조가 수동 복사에 의존했고,
(2) 고정 파일명이 매주 덮어써서 **지난주 리포트가 남지 않았다**(2026-07-31분이 실제로
덮였다). PC 폴더 + 날짜본으로 둘 다 해소했다. PC명은 _pc_id()가 호스트명에서 뽑는다.
--out-dir로 출력 폴더를 덮어쓸 수 있으나 재현·검증용이며 주간 산출물은 기본 경로를 쓸 것.
"""
import argparse
import contextlib
import datetime
import json
import os
import pickle
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── [MW0601 448차] BLAS DLL 경로 보장 — **반드시 `import numpy` 앞** ───────────
# 이 스크립트가 0xC06D007F로 즉사한 당사자다(08-01·08-07 주간 리포트 2회 결번).
# EOD 체인에서는 campaign_steps가 자식으로 띄우고, 사람이 단독 실행하기도 한다 —
# 후자를 위해 여기서도 직접 보장한다(부모가 이미 했으면 no-op).
# ⚠ **numpy import 순서를 바꿨다** — 원래 이 import가 sys.path 설정보다 위에 있어
#   부트스트랩을 끼울 자리가 없었다. numpy는 import 자체는 성공하고 첫 BLAS 호출에서
#   죽으므로, 늦게 부르면 "임포트는 됐는데 나중에 죽는" 형태가 된다.
# 상세·실측은 utils/dll_bootstrap.py 참조.
from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402
ensure_conda_dll_path()

import numpy as np  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from config.settings import (
    BASE_DIR,
    PREDICTIONS_DB, TRADES_DB, RAW_DATA_DB, DATA_DIR, MODEL_DIR,
    HORIZONS, VALIDATION_CAMPAIGN, FUTURES_COMMISSION_RATE, TICK_SIZE,
    ENTRY_STARVATION_WEEKLY_MIN, ENTRY_STARVATION_MITIGATION_LADDER,
    HURST_RANGE_THRESHOLD, REGIME_EXHAUSTION_EXT_ATR_THRESHOLD,
    VALIDATION_CAMPAIGN_DECISIONS, VALIDATION_REPORT_KEEP_WEEKS,
    ATR_STOP_MULT, ATR_TP1_MULT,   # [426차] [38] 차단신호 가상 스톱/TP1 재구성
    CONF_SCALE_BREAKS,             # [430차] conf 스케일 불연속 레지스트리
    MC_PERCENTILE, MC_ABS_FLOOR, MC_ABS_CEIL,  # [430차] [44] DynMC 재현
    ZONE_ENTRY_BAN_ENFORCE,        # [462차] [53] 집행 플래그 현황 표기용
    META_SCORING_HORIZON_BREAKS,   # [463차] [2] 스코어링 호라이즌 불연속 고지
)
from config.constants import DIRECTION_UP, DIRECTION_DOWN, MINI_FUTURES_PT_VALUE
from strategy.position.position_tracker import compute_trailing_stop_tier  # [361차]
from utils.db_utils import (  # [384차] TB 채널 판정 유지(carry-forward)
    save_tb_verdict, fetch_latest_tb_verdicts,
)
from utils.market_state import (  # [404차 후속5] 거래불능(가격상한 고착) 구간
    detect_limit_pin_bars, LIMIT_PIN_LIQUID_VOL_MIN, SESSION_OPEN_HHMM,
)

SHADOW_TB_DIR = os.path.join(MODEL_DIR, "horizons", "shadow_triple_barrier")
_TS_FMT = "%Y-%m-%d %H:%M:%S"

# 호라이즌당 replay 상한 — 모델 mtime이 오래됐을 때 메모리/시간 폭주 방지
_MAX_REPLAY_ROWS = 12000


# ──────────────────────────────────────────────────────────────
# 공통 유틸
# ──────────────────────────────────────────────────────────────

def _rankdata(a):
    """평균순위(동률 처리) — `scripts/core_feature_discovery.rankdata`와 동일 정의.

    scipy 의존 없이, 합/비교만 쓴다(`_pearson_r` docstring의 BLAS 회피 제약과 동일 취지).
    """
    a = np.asarray(a, dtype=np.float64)
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(a.size, dtype=np.float64)
    ranks[order] = np.arange(1, a.size + 1, dtype=np.float64)
    sa = a[order]
    i = 0
    while i < sa.size:
        j = i
        while j + 1 < sa.size and sa[j + 1] == sa[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = (i + 1 + j + 1) / 2.0
        i = j + 1
    return ranks


def _spearman(x, y) -> float:
    """numpy 전용 스피어만 상관 (scipy 의존 회피). 동률은 **평균순위**로 처리한다.

    [MW0602 460차] 종전 구현은 `np.argsort(np.argsort(x))`로 **서수순위**를 만들어
    동률을 배열 위치 순서로 임의 분리했다. 두 축의 행 순서가 같으므로(같은 쿼리 결과)
    동률군 내부 순위가 양쪽 다 "시간 순서"를 대리하게 되고, 그 공유된 위치 성분이
    상관으로 읽히는 계통편향(부호는 항상 +)이 있었다. y가 전부 같은 값이면 y 순위가
    정확히 0..n-1이 되어 분산이 0이 아니게 되므로 아래 `sy` 가드도 무력했다
    (`_spearman([1,2,1,2,1,2], [0.3]*6)` → 구 +0.7143 / 정정 nan).

    ⚠ **계측 불연속 경계 2026-08-10.** 이 헬퍼를 쓰는 채널의 rho가 정정 방향으로 바뀐다.
    동률 없는 연속형 축은 사실상 무변화이고, **양쪽 축에 동시에 동률군이 있고 그 동률군이
    시간에 뭉쳐 있을수록** 크게 바뀐다(수량·pass_count·플래그 축). 독립 데이터 몬테카를로
    (참값 rho=0): 연속×연속 편향 -0.003 → 정정 후 동일 / 수량×승패플래그 n=60 +0.023 →
    +0.001 / 수량군이 시간에 뭉친 경우 n=60 **+0.110 → -0.001**.
    이 PC의 2026-08-10 시점 호출부 4곳은 실측 |Δ| ≤ 0.0045로 판정 무변화였다
    ([1] ic_3class 전 호라이즌 ≤0.0004, [3] unc_corr -0.0001, [12] edge_corr -0.0045).
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if len(x) < 3 or len(x) != len(y):
        return float("nan")
    rx = _rankdata(x)
    ry = _rankdata(y)
    sx = rx.std()
    sy = ry.std()
    if sx < 1e-12 or sy < 1e-12:
        return float("nan")
    return float(((rx - rx.mean()) * (ry - ry.mean())).mean() / (sx * sy))


@contextlib.contextmanager
def _conn(db_path):
    """DB 연결 — **반드시 닫는다.** 호출부는 종전 그대로 `with _conn(x) as conn:`.

    [MW0602 488차 후속2] 종전에는 raw `sqlite3.Connection` 을 돌려줬는데,
    `with conn:` 은 sqlite3 에서 **트랜잭션** 컨텍스트일 뿐 `close()` 가 아니다.
    그래서 리포트 1회 생성마다 **90곳에서 연결이 샜다**(이 파일의 `with _conn(` 수).

    증상은 두 갈래로 나타났다:
      · 운영 — 프로세스가 끝날 때까지 핸들 90개가 남는다. EOD 1회성이라 실피해는
        작지만, WAL 경합 진단을 어렵게 만든다(0819 §12 `DB미접속` 계열의 배경 소음).
      · 테스트 — **Windows 는 열린 파일을 지울 수 없다.** 임시 DB 를 만들어 판정을
        돌리고 `os.unlink()` 하는 테스트 8개가 전부 `PermissionError [WinError 32]`
        로 실패했다(`tests/test_439_p2_slippage_judgment.py`). 원인이 테스트가 아니라
        **프로덕션 코드의 누수**라, 테스트를 고치는 것은 증상 억제였을 것이다.

    ⚠ **트랜잭션 의미를 바꾸지 않는다.** 안쪽 `with conn:` 을 그대로 유지해
    성공 시 commit / 예외 시 rollback 이 종전과 같다 — 이 파일에는 섀도 테이블
    `UPDATE` 가 여러 곳 있어(예: `tp1_trail_shadow`) 자동 commit 이 사라지면
    **조용히 기록이 사라진다.**
    """
    conn = sqlite3.connect(db_path, timeout=15)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def _roundtrip_cost_pt(avg_price: float) -> float:
    """왕복 비용(pt) = 수수료 2×price×rate + 슬리피지 2×틱 (캠페인 공통 가정)."""
    slip = float(VALIDATION_CAMPAIGN.get("slippage_ticks_per_side", 1.0))
    return 2.0 * avg_price * FUTURES_COMMISSION_RATE + 2.0 * slip * TICK_SIZE


def _pc_id() -> str:
    """[MW0601 405차 / P0-5] 이 PC 식별자. utils.db_utils.pc_id()와 동일 규약."""
    try:
        from utils.db_utils import pc_id as _p
        return _p()
    except Exception:
        try:
            import platform as _pf
            import re as _re
            host = _pf.node() or ""
            m = _re.search(r"(MW\d{4})", host, _re.IGNORECASE)
            return m.group(1).upper() if m else (host[:32] or "UNKNOWN")
        except Exception:
            return "UNKNOWN"


# [MW0601 409차 / R3] A/B 채널 3종과 그 기준선 지표.
# 이 채널들의 FAIL 판정은 전부 `delta_vs_current`(대안 − 현행)로 내리므로,
# **기준선(current) 자체의 부호가 PC간 반대면 "현행 초과 대안" 목록이 구조적으로 갈린다.**
_AB_BASELINE_CHANNELS = (
    ("[3-B]", "quantile_tp_shadow", "분위회귀 TP1 거리 A/B"),
    ("[23-B]", "tp1_geometry_shadow", "TP1/손절 초기 기하 A/B"),
    ("[25]", "tp1_protect_offset_shadow", "TP1 보호전환 offset A/B"),
)


def _peer_ab_baselines(me: str) -> dict:
    """[MW0601 409차 / R3] 다른 PC 리포트의 A/B 기준선(current.total_pt)을 읽는다.

    왜 필요한가: 0802 31채널 대조에서 `tp1_geometry_shadow.per_variant.current.total_pt`가
    MW0601 −17.18 vs MW0602 +3.64로 **부호가 반대**임이 드러났다(quantile_tp_shadow도
    −16.94 vs +6.03). 같은 대안이 한 PC에서는 "현행 초과", 다른 PC에서는 "현행 미달"로
    갈릴 수밖에 없고, 실제로 tp1_x2(+32.78 vs −19.04)·q_x0.7·q_blend가 그렇게 갈렸다.
    교차검토 §2-4는 그걸 tp1_x2 1건의 문제로 봤지만 전수로는 A/B 채널 3개 전체의 문제다.

    407차가 리포트를 PC별 폴더의 날짜본으로 옮긴 덕에 상대 PC 파일을 읽을 수 있게 됐다.
    **판정에는 일절 반영하지 않는다** — 표시 전용이다. 상대 파일이 없거나 오래됐어도
    리포트 생성을 막지 않는다(없는 것이 정상인 상황이 많다: 새 PC, pull 전, 단일 PC 운용).

    반환: {pc: {"date": "YYYYMMDD", "vals": {channel_key: total_pt or None}}}
    """
    out = {}
    try:
        from scripts.campaign_report_paths import WEEKLY_DIR, latest
        if not os.path.isdir(WEEKLY_DIR):
            return out
        for name in sorted(os.listdir(WEEKLY_DIR)):
            if name == me or not os.path.isdir(os.path.join(WEEKLY_DIR, name)):
                continue
            try:
                p = latest(name, "metrics")
            except Exception:
                continue        # 그 폴더엔 리포트가 없다(검토보고만 있는 폴더 등)
            try:
                with open(p, encoding="utf-8") as f:
                    m = json.load(f)
            except Exception:
                continue
            vals = {}
            for _, key, _ in _AB_BASELINE_CHANNELS:
                try:
                    vals[key] = ((m.get(key) or {}).get("per_variant") or {}) \
                        .get("current", {}).get("total_pt")
                except Exception:
                    vals[key] = None
            if any(v is not None for v in vals.values()):
                _m = re.search(r"(\d{8})", os.path.basename(p))
                out[name] = {"date": _m.group(1) if _m else "?", "vals": vals}
    except Exception:
        pass                    # R3는 부가 정보다 — 실패가 리포트를 막으면 안 된다
    return out


def _prune(pc_name: str, keep: int) -> list:
    """[MW0601 408차] FIFO 보관정리 — 실패해도 리포트 생성을 막지 않는다."""
    try:
        from scripts.campaign_report_paths import prune as _p
        return _p(pc_name, keep)
    except Exception as e:
        print("[경고] 보관정리 실패(무해, 다음 주 재시도): %s" % e, file=sys.stderr)
        return []


def _pc_dir_name() -> str:
    """[MW0601 408차] 산출물 폴더로 쓸 PC 이름 — 새 PC에서도 안전하게.

    `_pc_id()`는 호스트명에서 `MW####`를 못 찾으면 호스트명 원문을, 그것도 실패하면
    "UNKNOWN"을 돌려준다. 그대로 폴더 이름으로 쓰면 새 PC에서 `금요일점검/UNKNOWN/`
    같은 폴더가 **조용히** 생겨 다음 주에야 발견된다 — 경고를 찍어 즉시 알린다.
    경로에 못 쓰는 문자는 방어적으로 치환한다(윈도우 호스트명엔 원래 없지만,
    환경변수 오버라이드 등으로 들어올 여지를 남기지 않는다).
    """
    raw = _pc_id()
    safe = re.sub(r'[\\/:*?"<>|\s]+', "_", raw).strip("._") or "UNKNOWN"
    if not re.match(r"^MW\d{4}$", safe):
        print("[경고] PC 식별자가 MW#### 형식이 아니다: %r → 산출물 폴더 '%s' 사용. "
              "새 PC라면 호스트명을 확인하거나 폴더를 수동으로 정리할 것 "
              "(대조 스크립트는 --pc1/--pc2로 폴더명을 지정할 수 있다)."
              % (raw, safe), file=sys.stderr)
    return safe


def _pearson_r(a, b):
    """BLAS를 타지 않는 피어슨 상관계수 — `np.corrcoef` 대체.

    **`np.corrcoef`/`np.cov`를 이 스크립트에서 쓰지 말 것.** 이 스크립트는 EOD 체인에서
    py310_64로 실행되는데, MW0601의 py310_64에서 `np.cov` 내부 matmul이 네이티브
    크래시한다(`0xc06d007f` DELAYLOAD_FAILURE — 프로세스가 traceback 없이 즉사하므로
    try/except로도 못 잡는다). 317차 Phase 1에서 이미 확인된 환경 제약이며
    `scripts/hurst_*.py` 3종이 docstring에 "py37_32에서 실행" 경고를 달아둔 그 이슈다.

    404차 후속3이 [24] 채널에 `np.corrcoef`를 넣으면서 이 제약이 리포트 생성 경로로
    유입됐다 — MW0602에서는 재현되지 않아 발견될 수 없었던 PC 환경차다. 여기서는
    합/평균만 쓰는 정의식으로 직접 계산한다(py37_32 `np.corrcoef`와 값 일치 확인:
    0.9933992677987828). 표준편차가 0이거나 표본이 2 미만이면 None.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.size < 2 or a.size != b.size:
        return None
    am = a - a.mean()
    bm = b - b.mean()
    denom = float(np.sqrt(float((am * am).sum()) * float((bm * bm).sum())))
    if denom <= 0.0:
        return None
    return float((am * bm).sum() / denom)


def _shadow_qty_profile(table: str) -> dict:
    """[MW0601 405차 / P0-3] 섀도 채널의 진입시점 계약수 분포 + qty 가중 hyp 합계.

    `hyp_pnl_pts`는 1계약 기준이라 실현 기여도를 과대/과소 표시할 수 있다. 여기서
    `ensemble_decisions.entry_qty`(사이저가 그 시점에 제안한 계약수)를 ts로 붙여
    "만약 제안 수량대로 진입했다면"의 가중 합계를 **참고값으로만** 계산한다.

    **판정에 쓰지 않는다.** 합격선을 qty 가중으로 바꾸면 §9-4 검증 시계가 리셋되고,
    무엇보다 섀도의 질문("차단 안 했으면 얼마였나")은 게이트 성능을 재는 것이라
    사이저 성능을 섞으면 두 개가 뒤엉킨다. 표시 전용이다.

    MW0601 실측: [6] hurst_gate_shadow는 비가중 +37.72 → 가중 +26.27pt(0.70배)로
    30% 희석되고, [7] joint_gate_shadow는 entry_qty가 전부 1이라 차이가 없다.
    """
    out = {"table": table}
    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                'SELECT ts, hyp_pnl_pts FROM "%s" WHERE resolved=1 AND ts >= ?' % table,
                (_campaign_start(),),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out
    if not rows:
        out["n"] = 0
        return out
    try:
        with _conn(PREDICTIONS_DB) as pconn:
            qmap = {r["ts"]: int(r["entry_qty"] or 1) for r in pconn.execute(
                "SELECT ts, entry_qty FROM ensemble_decisions "
                "WHERE entry_qty IS NOT NULL AND ts >= ?", (_campaign_start(),))}
    except Exception as e:
        out["error"] = str(e)
        return out

    dist, unw, wtd, matched = {}, 0.0, 0.0, 0
    for r in rows:
        h = float(r["hyp_pnl_pts"] or 0.0)
        q = qmap.get(r["ts"])
        if q is None:
            continue
        matched += 1
        dist[q] = dist.get(q, 0) + 1
        unw += h
        wtd += h * q
    out["n"] = len(rows)
    out["n_qty_matched"] = matched
    out["qty_dist"] = dict(sorted(dist.items()))
    out["unweighted_hyp_pt"] = round(unw, 4)
    out["qty_weighted_hyp_pt"] = round(wtd, 4)
    if abs(unw) > 1e-9:
        out["weight_ratio"] = round(wtd / unw, 4)
    return out


def _render_joint_mfe(jg: dict) -> list:
    """[404차 후속9 / P1-D] [7] JointGateBlock의 MFE 병기 절 (표시 전용).

    [MW0601 420차] 원래 이 코드는 `[29] mean-revert 상세` 뒤에 인라인으로 있었다.
    `jg`(=[7]) 데이터인데 렌더 위치가 두 섹션 뒤라, 출력물에서 [29] 아래 붙은 H3처럼
    보이고 [7]을 읽는 사람은 자기 채널의 자기편향 계측을 찾지 못했다. 함수로 떼어
    [7] 본문 바로 아래에서 호출한다 — **순수 이동이며 계산·문구 로직은 그대로다**
    (단 아래 MFE/MAE 대소 문단만 420차에서 조건부로 고쳤다, 사유는 해당 위치 주석).
    """
    L = []
    if not jg.get("n_with_mfe"):
        return L
    L.append("")
    L.append("### MFE 병기 — counterfactual이 얼마나 과소평가하는가 (P1-D)")
    L.append("")
    L.append("- 30분 창 MFE 평균 **%s pt**(중앙값 %s) · MAE 평균 **%s pt** (n=%s%s)"
             % (jg.get("avg_mfe_30m", "—"), jg.get("median_mfe_30m", "—"),
                jg.get("avg_mae_30m", "—"), jg.get("n_with_mfe", 0),
                (", 소급 %d건" % jg["mfe_backfilled"]) if jg.get("mfe_backfilled") else ""))
    L.append("- **MFE>MAE %s건 vs MAE≥MFE %s건** (ΣMFE %s / ΣMAE %s pt)"
             % (jg.get("n_mfe_gt_mae", "—"), jg.get("n_mae_ge_mfe", "—"),
                jg.get("total_mfe_30m", "—"), jg.get("total_mae_30m", "—")))
    if jg.get("cf_capture_of_mfe") is not None:
        L.append("- counterfactual 포착률 Σhyp/ΣMFE = %.1f%% "
                 "(음수 = TP1 가정의 순손익이 마이너스라는 뜻이지 '비율'로 읽지 말 것)"
                 % (jg["cf_capture_of_mfe"] * 100))
    L.append("- 추세형 과소평가 건수(MFE≥5pt 이면서 hyp<MFE의 30%%): **%s건**"
             % jg.get("n_trend_underestimated", 0))
    if jg.get("trend_underestimated_top5"):
        L.append("")
        L.append("| 시각 | 방향 | MFE(30분) | MAE(30분) | TP1 기준 hyp | cf |")
        L.append("|---|---|---|---|---|---|")
        for r in jg["trend_underestimated_top5"]:
            L.append("| %s | %s | **+%s** | −%s | %s | %s |" % (
                str(r["ts"])[5:16], r["dir"], r["mfe"], r["mae"], r["hyp"], r["cf"]))
    L.append("")
    L.append("> **계측이지 처방이 아니다.** `hyp_pnl_pts`는 차단 신호를 현행 TP1")
    L.append("> (ATR×0.3~0.5)로 청산했다고 가정하는데, 그 TP1이 너무 좁다는 것이 0731")
    L.append("> 리포트 §2-C의 결론이다 — 즉 counterfactual이 자기 편향적이라 추세일의")
    L.append("> 차단 비용을 구조적으로 과소평가한다. 포착률이 낮을수록 위 \"차단이")
    L.append("> 이득\" 판정이 TP1 가정에 크게 기대고 있다는 뜻이다.")
    L.append(">")
    L.append("> ⚠ 이 수치로 **TP를 넓히자는 결론을 내면 안 된다** — §2-E가 차단 19건에")
    L.append("> 대칭 TP(1:1)를 직접 적용해 −9.87pt(현행 +4.92pt)로 **이미 기각**했다.")
    L.append("> 이기는 거래가 더 버는 만큼 지는 거래도 커진다. MFE는 \"차단 판정이")
    L.append("> 어떤 가정 위에 서 있는지\"를 드러낼 뿐이다.")
    L.append(">")
    # [MW0601 420차] 아래 문단은 원래 "MAE 평균이 MFE 평균보다 **크다**. …그건 차단이
    # 옳았던 쪽 증거다"를 **무조건** 출력했다. MW0602 실측(MFE 6.63 < MAE 8.96)에서는
    # 참이지만 MW0601 실측(MFE 11.73 > MAE 6.68, MFE>MAE 74건 vs 42건)에서는 **거짓**이라,
    # 바로 위에 인쇄된 자기 숫자와 정면으로 모순되는 결론이 실려 있었다. 실측으로 분기한다.
    _mfe_gt = (float(jg.get("avg_mfe_30m", 0.0) or 0.0)
               > float(jg.get("avg_mae_30m", 0.0) or 0.0))
    L.append("> ⚠ **MFE만 보면 정반대로 읽힌다 — MAE를 반드시 함께 볼 것.**")
    if not _mfe_gt:
        L.append("> 이 표본에서 MAE 평균이 MFE 평균보다 **크다**. 차단된 신호들은 유리하게")
        L.append("> 간 폭보다 불리하게 간 폭이 더 컸다는 뜻이고, 그건 차단이 옳았던 쪽")
        L.append("> 증거다. \"추세일 차단 비용 과소평가\"는 개별 추세 건에서는 사실이지만")
        L.append("> 표본 전체로는 반대 방향 증거가 더 크다.")
    else:
        L.append("> 다만 **이 표본은 MFE 평균이 MAE 평균보다 크다**(%s vs %s, MFE>MAE"
                 % (jg.get("avg_mfe_30m", "—"), jg.get("avg_mae_30m", "—")))
        L.append("> %s건 vs %s건). 즉 **\"차단이 옳았다\"는 MAE 근거가 이 표본에는 없다.**"
                 % (jg.get("n_mfe_gt_mae", "—"), jg.get("n_mae_ge_mfe", "—")))
        L.append("> 그렇다고 반대 결론(차단이 비쌌다)이 서지도 않는다 — MFE는 아래")
        L.append("> \"순서를 모른다\" 한계 때문에 실현 가능한 값이 아니다. 판정은")
        L.append("> hyp_pnl_pts와 증거강도(t)로 하고 여기는 참고로만 볼 것.")
    L.append(">")
    L.append("> ⚠ **MFE/MAE는 순서를 모른다.** 위 07-27 09:49 SHORT처럼 MFE +23.96인데")
    L.append("> cf=STOP인 건은, 스톱이 먼저 맞은 뒤에 유리하게 갔다는 뜻일 수 있다.")
    L.append("> \"이만큼 벌 수 있었다\"의 상한이지 실현 가능한 값이 아니다.")
    return L


def _render_qty_profile(table: str) -> list:
    """[MW0601 405차 / P0-3] 섀도 채널 상세절에 붙일 계약수 프로파일 줄 (표시 전용)."""
    p = _shadow_qty_profile(table)
    if p.get("error") or not p.get("n_qty_matched"):
        return []
    lines = ["- 진입시점 계약수 분포: %s (매칭 %d/%d건)" % (
        ", ".join("%d계약×%d" % (q, c) for q, c in p["qty_dist"].items()),
        p["n_qty_matched"], p["n"])]
    if p.get("weight_ratio") is not None:
        lines.append(
            "  - **참고(판정 미반영)**: 비가중 %s pt → 사이저 제안 수량 가중 %s pt "
            "(%.2f배). 판정은 비가중 1계약 기준을 그대로 쓴다 — 게이트 성능에 "
            "사이저 성능을 섞지 않기 위해서다(§9-4 합격선 무변경)." % (
                p["unweighted_hyp_pt"], p["qty_weighted_hyp_pt"], p["weight_ratio"]))
    return lines


def _campaign_start() -> str:
    return VALIDATION_CAMPAIGN.get("start_date", "2026-07-05") + " 00:00:00"


# ── [MW0602 430차 / P0-1] conf 스케일 불연속 ────────────────────────────────
def _conf_scale_breaks_in(window_start: str, window_end: str = None) -> list:
    """분석 창이 걸치는 conf 스케일 불연속 목록.

    `config.settings.CONF_SCALE_BREAKS`를 읽어, 창 안에 들어오는 경계만 돌려준다.
    창의 시작보다 앞선 경계는 무해하다 — 창 전체가 같은 체제이기 때문이다.
    걸치는 경우에만 경고를 띄워야 "경고가 늘 떠 있어서 안 읽는" 상태를 피한다.

    Args:
        window_start: "YYYY-MM-DD" 또는 "YYYY-MM-DD HH:MM:SS"
        window_end:   같은 형식. None이면 상한 없음(오늘까지).
    """
    s = (window_start or "")[:10]
    e = (window_end or "9999-12-31")[:10]
    hits = []
    for b in (CONF_SCALE_BREAKS or ()):
        d = str(b.get("date", ""))[:10]
        if d and s < d <= e:
            hits.append(b)
    return hits


def _conf_scale_break_lines(window_start: str, window_end: str = None,
                            prefix: str = "> ") -> list:
    """불연속 경고 마크다운 줄. 걸치는 경계가 없으면 빈 리스트."""
    out = []
    for b in _conf_scale_breaks_in(window_start, window_end):
        out.append("%s⚠ **conf 스케일 불연속 — %s (%s)**" % (
            prefix, b.get("date"), b.get("label")))
        out.append("%s이 창은 경계를 걸친다. `ensemble_decisions.confidence`의 "
                   "**산출 경로가 달라졌으므로 경계를 넘는 수준 비교는 무효**다." % prefix)
        out.append("%s원인: %s" % (prefix, b.get("cause")))
        out.append("%s실측: %s" % (prefix, b.get("evidence")))
        if b.get("caveat"):
            out.append("%s%s" % (prefix, b["caveat"]))
        out.append("%s일자단위·층화 지표는 이 수준 이동에 면역이다 — **그쪽을 보라.**"
                   % prefix)
    return out


def _load_candle_maps(cutoff_ts: str, exclude_untradeable: bool = False):
    """분봉 맵 3종. `exclude_untradeable=True`면 거래불능(가격상한 고착) 분봉을 뺀다.

    [404차 후속5 / P0-B(a)]

    ## 왜 기본값이 False이고 호출부마다 켜야 하는가

    처음에는 이 함수 안에서 무조건 제외하도록 짰다가 **레이블이 망가지는 것을
    실측으로 잡았다.** [1] Triple-Barrier 채널은 이 맵을 청산 시뮬이 아니라
    **레이블 생성**(N분 뒤 가격이 얼마였나)에 쓴다. 고착 분봉이라도 그 시각의
    가격은 진짜 1036.28이므로, 빼면 정답을 지우는 셈이고 실제로 OOS 표본이
    3m 584→572 / 5m 346→339 / 10m 170→166 / 15m 107→104 / 30m 50→48로 깎였다.

    구분 기준은 **그 분봉을 무엇에 쓰는가**다:
      - 체결 시뮬(스톱/TP 도달 판정, MFE) → 제외 O. 체결 불가한 분에 청산했다고
        가정하면 안 된다.
      - 가격 조회·레이블(그 시각 가격이 얼마였나) → 제외 X. 가격은 실재했다.

    제외 semantics는 **결측 분봉과 동일**이라 소비처를 고칠 필요가 없다. 소비처는
    전부 `high_map.get(ts)` 가 None이면 `continue` 하도록 이미 작성돼 있다(원본
    DB에 실제 결측 분봉이 있기 때문). 시뮬 루프에서 건너뛰면 "그 분에는 청산하지
    못했다 = 포지션 유지"가 되어 의도와 일치한다.

    ⚠ 켠 상태에서도 실측 효과는 **현재 표본에서 0**이다(리포트 전문 diff 확인).
    가격이 상한에 붙으려면 먼저 유동적으로 그 가격에 도달해야 하므로 고착 분봉은
    새로운 극단을 만들지 못하고, 07-31의 두 거래도 고착 시작(14:21) 전에 청산됐다.
    그럼에도 유지하는 이유는 갭 상한가 직행처럼 **유동 분봉 없이 극단이 생기는
    경우**에 대한 구조적 보험이기 때문이다. 효과가 0이라는 사실 자체를 기록해 둔다
    — 나중에 이 필터가 뭔가를 바꾸면 그건 새로운 시장 상황이라는 신호다.
    """
    with _conn(RAW_DATA_DB) as conn:
        rows = [dict(r) for r in conn.execute(
            "SELECT ts, high, low, close, volume FROM raw_candles "
            "WHERE ts >= ? ORDER BY ts",
            (cutoff_ts,),
        )]
    if exclude_untradeable:
        pinned = detect_limit_pin_bars(rows)
        rows = [r for r in rows if r["ts"] not in pinned]
    close_map = {r["ts"]: float(r["close"]) for r in rows}
    high_map = {r["ts"]: float(r["high"]) for r in rows}
    low_map = {r["ts"]: float(r["low"]) for r in rows}
    return close_map, high_map, low_map


def _ts_plus_min(ts: str, minutes: int) -> str:
    return (
        datetime.datetime.strptime(ts, _TS_FMT) + datetime.timedelta(minutes=minutes)
    ).strftime(_TS_FMT)


# ──────────────────────────────────────────────────────────────
# [0] 캠페인 표본 기아 조기경보 + 완화 사다리 (§3-8, P1-7, 297차)
# ──────────────────────────────────────────────────────────────

def eval_sample_starvation() -> dict:
    """주간 진입 체결 건수를 §3-8 사전등록 하한과 비교하고, 완화 사다리의
    현재 단계를 판단한다. 자동으로 아무것도 변경하지 않는다 — 사다리 적용은
    항상 사용자 수동 결정 + DECISION_LOG 기록."""
    out = {"verdict": "OK", "floor": ENTRY_STARVATION_WEEKLY_MIN}
    try:
        with _conn(TRADES_DB) as conn:
            cutoff = (
                datetime.datetime.now() - datetime.timedelta(days=7)
            ).strftime(_TS_FMT)
            n_weekly = conn.execute(
                "SELECT COUNT(*) AS n FROM trades WHERE exit_ts IS NOT NULL AND exit_ts >= ?",
                (cutoff,),
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    n_weekly = int(n_weekly or 0)
    starved = n_weekly < ENTRY_STARVATION_WEEKLY_MIN
    projected_28d = n_weekly * 4
    out.update({
        "n_weekly_entries": n_weekly,
        "starved": starved,
        "projected_28d_entries": projected_28d,
    })

    at_risk = []
    _mg = VALIDATION_CAMPAIGN["meta_gate"]
    if projected_28d < _mg["min_per_tercile"] * 3:
        at_risk.append("Meta-Gate(§3-2, 분위당 %d건×3 필요)" % _mg["min_per_tercile"])
    _hr = VALIDATION_CAMPAIGN["hurst_regime"]
    if projected_28d < _hr["min_per_bucket"] * 2:
        at_risk.append("레짐 ATR 배수(§3-5②, 버킷당 %d건×2 필요)" % _hr["min_per_bucket"])
    out["kpis_at_risk"] = at_risk

    ladder = ENTRY_STARVATION_MITIGATION_LADDER
    step3 = next(s for s in ladder if s["step"] == 3)
    step3_applied = abs(HURST_RANGE_THRESHOLD - step3["mitigated_value"]) < 1e-6

    if step3_applied:
        out["ladder_status"] = "3단계(Hurst 완화) 적용됨 — 사다리 소진, 추가 완화 여지 없음"
        out["current_step"] = 3
    elif not starved:
        out["ladder_status"] = "정상 — 사다리 미적용 상태 유지"
        out["current_step"] = 0
    else:
        step1 = next(s for s in ladder if s["step"] == 1)
        deployed = datetime.datetime.strptime(step1["deployed_date"], "%Y-%m-%d")
        days_since = (datetime.datetime.now() - deployed).days
        if days_since < 5:
            out["ladder_status"] = (
                "1단계 관찰 중 (FQAdj 수정 후 %d거래일 경과, 5일 채울 때까지 대기)" % days_since
            )
            out["current_step"] = 1
        else:
            out["ladder_status"] = (
                "1단계 관찰 기간(5거래일) 경과 후에도 기아 지속 — "
                "2단계(MetaGate take_ceil 0.570→0.52) 검토 권고 (사용자 결정 필요)"
            )
            out["current_step"] = 2

    out["verdict"] = "STARVED" if starved else "OK"
    return out


# ──────────────────────────────────────────────────────────────
# [1] Triple-Barrier 채널 — OOS replay IC vs 3클래스 IC
# ──────────────────────────────────────────────────────────────

def _tb_apply_carried(res: dict, cv, n: int, min_n: int) -> None:
    """[439차] tb_verdict_log의 최근 판정을 이월 적용 — 표본 부족/0 공통 경로.

    384차의 carry-forward를 `eval_tb_channel()` 두 자리에서 함께 쓰도록 뽑아냈다.
    `cv`가 없으면(=첫 판정 전) 아무것도 이월하지 않고 이유만 남긴다.
    호출자가 이미 `res["reason"]`을 채웠으면 그 문구를 앞에 보존한다 —
    "왜 표본이 없는가"(모델 mtime 대기 등)가 이월 사실보다 진단에 중요하기 때문.
    """
    if cv is None:
        if not res.get("reason"):
            res["reason"] = "OOS 표본 부족 (%d < %d) — 첫 판정 대기" % (n, min_n)
        return
    res["status"] = cv["verdict"]
    res["carried"] = True
    res["judged_at"] = cv["judged_at"]
    res["ic_tb"] = cv["ic_tb"]
    res["ic_3class"] = cv["ic_3class"]
    _base = "누적중 (%d/%d)" % (n, min_n) if n else (res.get("reason") or "표본 0건")
    res["reason"] = ("%s — 최근 판정 유지: %s (%s 판정, n=%d)"
                     % (_base, cv["verdict"], cv["judged_at"][:10], cv["n_samples"]))


def eval_tb_channel(days: int) -> dict:
    """[384차] 383차가 규명한 구조결함(평가창이 매주 재학습으로 리셋돼 5m~30m이
    min_samples_hz 영구 미달) 해법: 호라이즌별로 실제 OOS n이 min_samples_hz에
    도달한 주에만 신선하게 판정하고 tb_verdict_log에 기록한다. 그 아래 주는 그
    "최근 판정"을 그대로 이어받아(carry-forward) 채널 집계에 반영 — n_pass/verdict
    계산 로직 자체는 res["status"]만 보므로 변경 불요.

    [439차] 이월 적용을 `_tb_apply_carried()`로 단일화했다. 이전에는 `n <
    min_samples_hz` 분기 안에만 있어서 **OOS 행이 정확히 0일 때** 그보다 앞선
    `if not rows: continue`가 먼저 걸려 이월이 통째로 건너뛰어졌다(경계값만 뚫린
    가드). 상세 실증은 그 `continue` 자리의 주석 참조.
    """
    cr = VALIDATION_CAMPAIGN["tb"]
    out = {"horizons": {}, "verdict": "INSUFFICIENT", "n_pass": 0}

    if not os.path.isdir(SHADOW_TB_DIR):
        out["error"] = "섀도우 TB 모델 디렉토리 없음 — 첫 주간 재학습 대기"
        return out

    try:
        from model.multi_horizon_model import apply_robust_preprocess
    except Exception as e:
        out["error"] = "apply_robust_preprocess 임포트 실패: %s" % e
        return out

    try:
        carried_verdicts = fetch_latest_tb_verdicts()
    except Exception as e:
        carried_verdicts = {}
        print("[TB채널] tb_verdict_log 조회 실패: %s" % e)

    now_dt = datetime.datetime.now()

    for hz, h_min in HORIZONS.items():
        res = {"status": "INSUFFICIENT"}
        out["horizons"][hz] = res
        model_p = os.path.join(SHADOW_TB_DIR, "gbm_%s_shadow_tb.pkl" % hz)
        scaler_p = os.path.join(SHADOW_TB_DIR, "scaler_%s_shadow_tb.pkl" % hz)
        fn_p = os.path.join(SHADOW_TB_DIR, "feature_names_%s_shadow_tb.pkl" % hz)
        if not all(os.path.exists(p) for p in (model_p, scaler_p, fn_p)):
            res["reason"] = "모델 파일 없음"
            continue

        # OOS 보장: 모델 파일 mtime 이후 데이터만 평가 (학습 표본과 완전 분리)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(model_p))
        eval_start = max(
            mtime.strftime(_TS_FMT),
            _campaign_start(),
            (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(_TS_FMT),
        )
        res["eval_start"] = eval_start

        try:
            with open(model_p, "rb") as f:
                model = pickle.load(f)
            with open(scaler_p, "rb") as f:
                scaler = pickle.load(f)
            with open(fn_p, "rb") as f:
                feat_names = pickle.load(f)
        except Exception as e:
            res["reason"] = "모델 로드 실패: %s" % e
            continue

        # 피처 행 로드 — batch_retrainer.retrain_shadow_triple_barrier와 동일 경로
        # (1m은 설계상 raw_features, 그 외는 raw_features_horizon → 부족 시 폴백)
        try:
            with _conn(RAW_DATA_DB) as conn:
                if hz == "1m":
                    rows = conn.execute(
                        "SELECT ts, features FROM raw_features WHERE ts > ? ORDER BY ts",
                        (eval_start,),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT ts, features FROM raw_features_horizon "
                        "WHERE horizon=? AND ts > ? ORDER BY ts",
                        (hz, eval_start),
                    ).fetchall()
                    if not rows:
                        rows = conn.execute(
                            "SELECT ts, features FROM raw_features WHERE ts > ? ORDER BY ts",
                            (eval_start,),
                        ).fetchall()
        except Exception as e:
            res["reason"] = "피처 조회 실패: %s" % e
            continue

        rows = rows[-_MAX_REPLAY_ROWS:]
        if not rows:
            # [439차] **여기서도 carry-forward를 태운다.** 384차가 심은 이월은
            # `n < min_samples_hz` 분기에만 있었는데, OOS 행이 **정확히 0**이면
            # 그보다 앞선 이 `continue`가 먼저 걸려 이월이 통째로 건너뛰어졌다 —
            # "표본이 적다"는 살리고 "표본이 없다"는 죽이는, 경계값만 뚫린 가드였다.
            # 실증(0807): EOD 체인은 리포트(15:47:41) → 섀도우 TB 재학습(15:48:57)
            # 순서라 리포트 시점엔 지난주 모델 mtime이 보여 1m n=1844 / 3m n=1194로
            # 정상 판정(FAIL)이 났다. 그런데 체인이 끝난 뒤 리포트를 **재생성하면**
            # 모델 mtime이 15:48:57로 밀려 OOS가 0이 되고, [1]이 FAIL → INSUFFICIENT로
            # 조용히 강등됐다. tb_verdict_log(id 48·49)에는 그날의 FAIL이 멀쩡히
            # 남아 있는데도 리포트만 판정을 잃는다.
            res["n_samples"] = 0
            res["reason"] = "OOS 표본 0건 (모델 mtime 이후 데이터 대기)"
            _tb_apply_carried(res, carried_verdicts.get(hz), 0,
                              int(cr["min_samples_hz"]))
            continue

        # [404차 후속5 / P0-B(a)] 여기는 **레이블 생성**(N분 뒤 실현 가격)이라
        # 거래불능 분봉을 빼면 안 된다 — 체결 가능 여부와 무관하게 그 시각 가격은
        # 실재했다. 실제로 켜봤더니 OOS 표본이 3m 584→572 등으로 깎였다.
        close_map, _hi, _lo = _load_candle_maps(eval_start)

        ts_list, X_list, y_list = [], [], []
        for r in rows:
            try:
                fd = json.loads(r["features"])
            except (ValueError, TypeError):
                continue
            if not isinstance(fd, dict):
                continue
            c0 = close_map.get(r["ts"])
            c1 = close_map.get(_ts_plus_min(r["ts"], h_min))
            if c0 is None or c1 is None:
                continue
            ts_list.append(r["ts"])
            X_list.append([float(fd.get(f, 0.0) or 0.0) for f in feat_names])
            y_list.append(c1 - c0)  # 실현 변동 (pt, 부호 포함)

        n = len(X_list)
        res["n_samples"] = n
        if n < int(cr["min_samples_hz"]):
            _tb_apply_carried(res, carried_verdicts.get(hz), n,
                              int(cr["min_samples_hz"]))
            continue

        try:
            X = np.array(X_list, dtype=np.float32)
            X = apply_robust_preprocess(X, list(feat_names))
            X_s = scaler.transform(X)
            proba = model.predict_proba(X_s)
            cls = list(getattr(model, "classes_", []))
            i_up = cls.index(DIRECTION_UP) if DIRECTION_UP in cls else None
            i_dn = cls.index(DIRECTION_DOWN) if DIRECTION_DOWN in cls else None
            p_up = proba[:, i_up] if i_up is not None else np.zeros(n)
            p_dn = proba[:, i_dn] if i_dn is not None else np.zeros(n)
            tb_score = p_up - p_dn
        except Exception as e:
            res["reason"] = "replay 실패: %s" % e
            continue

        ic_tb = _spearman(tb_score, y_list)

        # 3클래스 baseline: 같은 기간·같은 호라이즌 meta_labels의 up/down_prob
        try:
            with _conn(PREDICTIONS_DB) as conn:
                mrows = conn.execute(
                    """SELECT up_prob, down_prob, target_close, future_close
                       FROM meta_labels
                       WHERE horizon=? AND ts > ?
                         AND up_prob IS NOT NULL AND down_prob IS NOT NULL
                         AND target_close IS NOT NULL AND future_close IS NOT NULL""",
                    (hz, eval_start),
                ).fetchall()
        except Exception as e:
            res["reason"] = "meta_labels 조회 실패: %s" % e
            continue

        base_score = [float(m["up_prob"]) - float(m["down_prob"]) for m in mrows]
        base_move = [float(m["future_close"]) - float(m["target_close"]) for m in mrows]
        ic_3c = _spearman(base_score, base_move) if len(base_score) >= 3 else float("nan")

        res.update({
            "ic_tb": None if np.isnan(ic_tb) else round(ic_tb, 4),
            "ic_3class": None if np.isnan(ic_3c) else round(ic_3c, 4),
            "n_baseline": len(base_score),
        })
        if np.isnan(ic_tb) or np.isnan(ic_3c):
            res["reason"] = "IC 계산 불가 (분산 0 또는 표본 부족)"
            continue

        passed = (ic_tb > ic_3c + cr["ic_delta_min"]) and (ic_tb > cr["ic_abs_min"])
        res["status"] = "PASS" if passed else "FAIL"
        res["carried"] = False
        res["judged_at"] = now_dt.strftime(_TS_FMT)
        try:
            save_tb_verdict(
                horizon=hz, judged_at=res["judged_at"], eval_start=eval_start,
                model_mtime=mtime.strftime(_TS_FMT), n_samples=n,
                ic_tb=res["ic_tb"], ic_3class=res["ic_3class"], verdict=res["status"],
            )
        except Exception as e:
            res["reason"] = (res.get("reason", "") + " (판정 기록 실패: %s)" % e).strip()

    n_pass = sum(1 for r in out["horizons"].values() if r.get("status") == "PASS")
    n_judged = sum(1 for r in out["horizons"].values() if r.get("status") in ("PASS", "FAIL"))
    out["n_pass"] = n_pass
    if n_judged == 0:
        out["verdict"] = "INSUFFICIENT"
    elif n_pass >= int(cr["min_horizons_pass"]):
        out["verdict"] = "PASS"
    else:
        out["verdict"] = "FAIL"
    return out


# ──────────────────────────────────────────────────────────────
# [2] Meta-Gate 채널 — entry_quality_prob 3분위별 실현 순EV
# ──────────────────────────────────────────────────────────────

def eval_meta_gate_channel(days: int) -> dict:
    cr = VALIDATION_CAMPAIGN["meta_gate"]
    out = {"verdict": "INSUFFICIENT"}
    cutoff = max(
        _campaign_start(),
        (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(_TS_FMT),
    )

    try:
        with _conn(PREDICTIONS_DB) as conn:
            cols = {r["name"] for r in conn.execute(
                "PRAGMA table_info(ensemble_decisions)").fetchall()}
            hz_col = "meta_gate_horizon" if "meta_gate_horizon" in cols else None
            rows = conn.execute(
                """SELECT ts, direction, meta_entry_quality_prob AS prob%s
                   FROM ensemble_decisions
                   WHERE meta_entry_quality_prob IS NOT NULL
                     AND direction != 0 AND ts >= ?
                   ORDER BY ts""" % (
                    (", %s AS hz" % hz_col) if hz_col else ""),
                (cutoff,),
            ).fetchall()
            mrows = conn.execute(
                """SELECT ts, horizon, target_close, future_close FROM meta_labels
                   WHERE ts >= ? AND target_close IS NOT NULL AND future_close IS NOT NULL""",
                (cutoff,),
            ).fetchall()
            # [357차] 계측 생존 점검 — 최근 7일 소스 컬럼 적재량(방향 무관).
            # 0이면 "표본 대기"가 아니라 스코어러 사망(모델 로드 실패 등) 의심.
            _7d = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(_TS_FMT)
            src_7d = conn.execute(
                """SELECT COUNT(*) AS n FROM ensemble_decisions
                   WHERE meta_entry_quality_prob IS NOT NULL AND ts >= ?""",
                (_7d,),
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    out["src_nonnull_7d"] = int(src_7d)
    if src_7d == 0:
        out["no_data"] = True

    move_map = {(m["ts"], m["horizon"]): float(m["future_close"]) - float(m["target_close"])
                for m in mrows}

    samples = []  # (prob, direction_conditioned_move_pt)
    prices = []
    for r in rows:
        hz = (r["hz"] if ("hz" in r.keys()) else "") or "1m"
        key = (r["ts"], hz)
        if key not in move_map:
            key = (r["ts"], "1m")  # 구버전 행 fallback
            if key not in move_map:
                continue
        samples.append((float(r["prob"]), move_map[key] * int(r["direction"]),
                        str(r["ts"])[:10]))
    # 평균 가격 → 왕복 비용 산정
    avg_price = float(np.mean([float(m["target_close"]) for m in mrows])) if mrows else 1300.0
    cost_pt = _roundtrip_cost_pt(avg_price)

    out["n_samples"] = len(samples)
    out["cost_pt"] = round(cost_pt, 4)

    # [MW0602 463차 C3] 스코어링 호라이즌 불연속 고지 — **표시만, 판정 무관여**.
    # 이 채널의 입력 `meta_entry_quality_prob`은 2026-08-12 이전에는 전부 1m
    # 스코어러 산출값이었다(`_entry_horizon_pre` 미할당, read 2 / write 0).
    # 같은 기간 체결 진입의 88.9%가 3m·5m이었으므로 경계 이전 표본은
    # "3m·5m 진입을 1m 모델로 잰 값"이다. 405차 P0-3 pt배지와 같은 규율 —
    # 판정식·합격선·verdict에는 일절 관여하지 않고 혼용 사실만 드러낸다.
    try:
        _brk = (META_SCORING_HORIZON_BREAKS or ({},))[0].get("date")
    except Exception:
        _brk = None
    if _brk:
        _pre = sum(1 for s in samples if s[2] < _brk)
        _post = len(samples) - _pre
        out["scoring_break_date"] = _brk
        out["n_pre_break"] = _pre
        out["n_post_break"] = _post
        if _pre and _post:
            out["scoring_break_caveat"] = (
                "⚠ 표본이 스코어링 호라이즌 경계(%s)를 걸친다 — 이전 %d건은 1m 고정 "
                "스코어러, 이후 %d건은 실제 진입 호라이즌 산출값이다. 두 모집단을 합친 "
                "분위 판정은 해석 불가. 재측정은 경계 이후 표본만으로 할 것 "
                "(VALIDATION_CAMPAIGN_DECISIONS['meta_gate'] 재개 조건)." % (_brk, _pre, _post))
        elif _pre and not _post:
            out["scoring_break_caveat"] = (
                "⚠ 표본 전부가 경계(%s) **이전** — 1m 고정 스코어러 산출값이다. "
                "2026-08-01 '탈락 확정'과 같은 근거이며 재측정 표본이 아직 없다." % _brk)
    if len(samples) < 3 * int(cr["min_per_tercile"]):
        out["reason"] = "표본 부족 (%d < %d)" % (len(samples), 3 * cr["min_per_tercile"])
        if out.get("no_data"):
            out["reason"] += (" — **최근 7일 소스(meta_entry_quality_prob) 적재 0건**: "
                              "스코어러 모델 로드 실패 등 계측 사망 의심, 표본 대기가 아님 (357차)")
        return out

    samples.sort(key=lambda s: s[0])
    n = len(samples)
    k = n // 3
    bottom = [s[1] - cost_pt for s in samples[:k]]
    top = [s[1] - cost_pt for s in samples[-k:]]
    mid = [s[1] - cost_pt for s in samples[k:n - k]]
    # ⚠ 위 분위 분할은 경계(scoring_break_date)를 구분하지 않는다 — 의도적이다.
    # 판정식을 바꾸면 합격선 변경이 되어 §9-4 검증시계 리셋에 걸린다.
    # 혼용 사실은 scoring_break_caveat으로만 드러낸다(463차).

    top_ev = float(np.mean(top))
    bot_ev = float(np.mean(bottom))
    out.update({
        "tercile_n": k,
        "top_ev_pt": round(top_ev, 4),
        "mid_ev_pt": round(float(np.mean(mid)), 4) if mid else None,
        "bottom_ev_pt": round(bot_ev, 4),
        "separation_pt": round(top_ev - bot_ev, 4),
        "required_sep_pt": round(cr["sep_cost_mult"] * cost_pt, 4),
    })
    if k < int(cr["min_per_tercile"]):
        out["reason"] = "분위별 표본 부족 (%d < %d)" % (k, cr["min_per_tercile"])
        return out

    passed = (top_ev > cr["top_ev_min_pt"]) and \
             ((top_ev - bot_ev) > cr["sep_cost_mult"] * cost_pt)
    out["verdict"] = "PASS" if passed else "FAIL"
    return out


# ──────────────────────────────────────────────────────────────
# [MW0602 490차 / P1] [2] 재개 게이트 — 스코어러 AUC 기반
# ──────────────────────────────────────────────────────────────
def _meta_reopen_gate() -> dict:
    """489차 D1(최종 탈락)이 소진시킨 재개 조건을 대신하는 **새 사전등록 관문**.

    묻는 것: *"언제 [2] 계열 재설계에 자원을 다시 쓸 것인가."*
    게이트가 닫혀 있는 동안은 **아무것도 안 하는 것이 결정**이다.

    판정 지표는 `auc_net_directional` — 배포 모델 점수가 **순이익 라벨**(방향성 행만)을
    얼마나 잘 줄 세우는가다. [2]의 질문("순EV를 분리하는가")을 AUC 한 값으로 옮긴 것.

    ⚠ 게이트 통과는 "[2]가 통과한다"가 **아니다**. 성립하는 함의는 한 방향뿐 —
      **AUC≈0.5면 [2]가 통과할 리 없다.** 값싼 필터를 앞에 두는 것이다.
    ⚠ 문턱은 490차 실험 수치에서 역산하지 않았다(313차 ④). 앵커는
      `learning/calibration.py:PredictionCalibrator.DEGENERATE_AUC_MIN`이다.
    """
    cfg = (VALIDATION_CAMPAIGN.get("meta_gate") or {}).get("reopen_gate") or {}
    out = {"enabled": bool(cfg.get("enabled")), "metric": cfg.get("metric"),
           "need_weeks": int(cfg.get("consecutive_weeks", 4) or 4),
           "start_date": cfg.get("start_date")}
    if not out["enabled"]:
        out["state"] = "DISABLED"
        return out

    # 문턱 — 앵커 상수를 **런타임에 읽는다**(하드코딩 금지: 앵커가 바뀌면 함께 움직여야).
    try:
        from learning.calibration import PredictionCalibrator as _AC
        out["threshold"] = float(_AC.DEGENERATE_AUC_MIN)
        out["threshold_ok"] = True
    except Exception as e:
        out["threshold"] = None
        out["threshold_ok"] = False
        out["state"] = "UNKNOWN"
        out["reason"] = "앵커 상수 로드 실패: %s" % e
        return out

    try:
        from learning.meta_label_classifier import load_training_metrics
        metrics = load_training_metrics()
    except Exception as e:
        out["state"] = "UNKNOWN"
        out["reason"] = "학습 지표 사이드카 판독 실패: %s" % e
        return out

    hist = [h for h in (metrics.get("history") or [])
            if str(h.get("trained_at", ""))[:10] >= str(out["start_date"] or "")]
    out["n_runs"] = len(hist)
    if not hist:
        out["state"] = "INSUFFICIENT"
        out["reason"] = ("판정 창(%s~) 학습 기록 없음 — 사이드카가 쌓이기 전이다"
                         % out["start_date"])
        return out

    key = str(out["metric"])

    def _worst(entry):
        """호라이즌 중 **최솟값**으로 본다 — 하나라도 무정보면 통과로 치지 않는다."""
        vals = [v.get(key) for v in (entry.get("horizons") or {}).values()
                if isinstance(v.get(key), (int, float))]
        return (min(vals) if vals else None), (max(vals) if vals else None)

    latest_min, latest_max = _worst(hist[-1])
    out["latest_min"] = latest_min
    out["latest_max"] = latest_max
    out["latest_trained_at"] = hist[-1].get("trained_at")

    streak = 0
    for entry in reversed(hist):
        mn, _mx = _worst(entry)
        if mn is not None and mn >= out["threshold"]:
            streak += 1
        else:
            break
    out["streak_weeks"] = streak

    if streak >= out["need_weeks"]:
        out["state"] = "OPEN"
        out["reason"] = ("%s 최솟값이 %d회 연속 %.2f 이상 — [2] 재설계 자원 투입 검토 가능"
                         % (key, streak, out["threshold"]))
    else:
        out["state"] = "CLOSED"
        out["reason"] = (
            "%s 최솟값 %s < %.2f (연속 %d/%d회) — **재설계에 자원을 쓰지 않는다**"
            % (key, ("%.4f" % latest_min) if latest_min is not None else "N/A",
               out["threshold"], streak, out["need_weeks"]))
    return out


# ──────────────────────────────────────────────────────────────
# [3] 분위 회귀 채널 — 커버리지 + 불확실성 상관
# ──────────────────────────────────────────────────────────────

def _quantile_direction_stats(pairs) -> dict:
    """[3-A, 404차 후속10] q50 부호의 방향 적중률 — **관찰 전용, 판정 미반영**.

    감사 §3-3은 분위회귀 KPI를 3종으로 정의했다 — ① q50 부호의 방향 적중률,
    ② 폭-실현 상관, ③ 커버리지. 그런데 **합격선은 ②③만** 채택돼 ①은 사전등록만 되고
    한 번도 렌더링되지 않았다. 그 결과 [3] PASS가 "방향을 맞춘다"로 오독될 여지가
    있었다 — 실제로는 "불확실성 폭을 잘 맞춘다"는 뜻뿐이다.

    따라서 이 함수는 §3-3에 이미 등록돼 있던 KPI ①을 **표시만** 복원한다. 합격선
    (coverage_lo/hi·unc_corr_min)은 무변경이므로 §9-4가 금지하는 "판정 기준 사후 변경"이
    아니다. eval_quantile_channel()의 verdict 계산에 이 결과를 절대 넣지 말 것.

    conf_top30은 "모델이 강하게 말할 때는 맞는가"를 본다 — |q50| 상위 30% 부분집합의
    적중률이 전체와 같으면 q50의 크기에 정보가 없다는 뜻이다.
    """
    n = len(pairs)
    out = {"n": n}
    if n == 0:
        return out
    hits = [1.0 if (q > 0) == (m > 0) else 0.0 for q, m in pairs]
    out["hit_rate"] = round(float(np.mean(hits)), 4)
    out["q50_pos_share"] = round(sum(1 for q, _ in pairs if q > 0) / float(n), 4)
    k = max(1, int(n * 0.30))
    top = sorted(pairs, key=lambda x: -abs(x[0]))[:k]
    out["conf_top30_n"] = len(top)
    out["conf_top30_hit"] = round(
        float(np.mean([1.0 if (q > 0) == (m > 0) else 0.0 for q, m in top])), 4)
    return out


def eval_quantile_channel(days: int) -> dict:
    cr = VALIDATION_CAMPAIGN["quantile"]
    out = {"verdict": "INSUFFICIENT"}
    cutoff = max(
        _campaign_start(),
        (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(_TS_FMT),
    )

    try:
        with _conn(PREDICTIONS_DB) as conn:
            cols = {r["name"] for r in conn.execute(
                "PRAGMA table_info(ensemble_decisions)").fetchall()}
            if "quantile_q10_pt" not in cols:
                out["reason"] = "quantile_q10_pt 컬럼 없음 — 마이그레이션 전 데이터"
                return out
            rows = conn.execute(
                """SELECT ts, quantile_q10_pt AS q10, quantile_q90_pt AS q90,
                          quantile_expected_pt AS q50,
                          COALESCE(NULLIF(meta_gate_horizon, ''), '1m') AS hz
                   FROM ensemble_decisions
                   WHERE quantile_q10_pt IS NOT NULL AND quantile_q90_pt IS NOT NULL
                     AND ts >= ?""",
                (cutoff,),
            ).fetchall()
            mrows = conn.execute(
                """SELECT ts, horizon, target_close, future_close FROM meta_labels
                   WHERE ts >= ? AND target_close IS NOT NULL AND future_close IS NOT NULL""",
                (cutoff,),
            ).fetchall()
            # [357차] 계측 생존 점검 — [2]와 동일 취지 (분위 스코어러 사망 감지)
            _7d = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(_TS_FMT)
            src_7d = conn.execute(
                """SELECT COUNT(*) AS n FROM ensemble_decisions
                   WHERE quantile_q10_pt IS NOT NULL AND ts >= ?""",
                (_7d,),
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    out["src_nonnull_7d"] = int(src_7d)
    if src_7d == 0:
        out["no_data"] = True

    move_map = {(m["ts"], m["horizon"]): float(m["future_close"]) - float(m["target_close"])
                for m in mrows}

    covered, widths, abs_moves = [], [], []
    dir_pairs = []   # [3-A] (q50, 실현변동) — 방향 적중률 관찰용 (판정 미반영)
    for r in rows:
        mv = move_map.get((r["ts"], r["hz"]))
        if mv is None:
            continue
        q10, q90 = float(r["q10"]), float(r["q90"])
        covered.append(1.0 if (q10 <= mv <= q90) else 0.0)
        widths.append(q90 - q10)
        abs_moves.append(abs(mv))
        if r["q50"] is not None and float(r["q50"]) != 0.0 and mv != 0.0:
            dir_pairs.append((float(r["q50"]), mv))

    out["dir"] = _quantile_direction_stats(dir_pairs)

    n = len(covered)
    out["n_samples"] = n
    if n < int(cr["min_samples"]):
        out["reason"] = "표본 부족 (%d < %d)" % (n, cr["min_samples"])
        if out.get("no_data"):
            out["reason"] += (" — **최근 7일 소스(quantile_q10_pt) 적재 0건**: "
                              "스코어러 모델 로드 실패 등 계측 사망 의심, 표본 대기가 아님 (357차)")
        return out

    coverage = float(np.mean(covered))
    unc_corr = _spearman(widths, abs_moves)
    out.update({
        "coverage": round(coverage, 4),
        "coverage_band": [cr["coverage_lo"], cr["coverage_hi"]],
        "unc_corr": None if np.isnan(unc_corr) else round(unc_corr, 4),
    })
    if np.isnan(unc_corr):
        out["reason"] = "상관 계산 불가"
        return out
    passed = (cr["coverage_lo"] <= coverage <= cr["coverage_hi"]) and \
             (unc_corr > cr["unc_corr_min"])
    out["verdict"] = "PASS" if passed else "FAIL"
    return out


# ──────────────────────────────────────────────────────────────
# [4] 신호소멸청산 counterfactual — resolve + 누적 판정
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_signal_decay() -> dict:
    cr = VALIDATION_CAMPAIGN["signal_decay"]
    window_min = int(cr.get("cf_window_min", 30))
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM signal_decay_exits WHERE resolved = 0 ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    if unresolved:
        earliest = min(r["ts"] for r in unresolved)
        # 체결 시뮬 경로 — 거래불능 분봉 제외 [404차 후속5 / P0-B(a)]
        close_map, high_map, low_map = _load_candle_maps(
            earliest, exclude_untradeable=True)
        now = datetime.datetime.now()
        updates = []
        for r in unresolved:
            base = datetime.datetime.strptime(r["ts"], _TS_FMT)
            # 관찰 창이 아직 안 끝났으면(미래 데이터 부족) 다음 실행으로 미룸
            if now < base + datetime.timedelta(minutes=window_min + 2):
                continue
            is_long = str(r["direction"]) == "LONG"
            stop_p = float(r["stop_price"] or 0.0)
            tp1_p = float(r["tp1_price"] or 0.0)
            cf_outcome, cf_price = "NEITHER", None
            last_close = None
            # 창 종료 or 15:10 중 이른 쪽까지 분봉 스캔
            for m in range(1, window_min + 1):
                mid = base + datetime.timedelta(minutes=m)
                if mid.time() > datetime.time(15, 10):
                    break
                mid_ts = mid.strftime(_TS_FMT)
                hi = high_map.get(mid_ts)
                lo = low_map.get(mid_ts)
                if hi is None or lo is None:
                    continue
                last_close = close_map.get(mid_ts, last_close)
                if is_long:
                    hit_stop = stop_p > 0 and lo <= stop_p
                    hit_tp = tp1_p > 0 and hi >= tp1_p
                else:
                    hit_stop = stop_p > 0 and hi >= stop_p
                    hit_tp = tp1_p > 0 and lo <= tp1_p
                # 동시 터치 → 보수적으로 STOP 우선 (target_builder TB 레이블과 동일 관례)
                if hit_stop:
                    cf_outcome, cf_price = "STOP", stop_p
                    break
                if hit_tp:
                    cf_outcome, cf_price = "TP1", tp1_p
                    break
            if cf_price is None:
                if last_close is None:
                    continue  # 분봉 데이터 자체가 없음 — 다음 실행에서 재시도
                cf_price = last_close
            exit_p = float(r["exit_price"])
            # saved_pts: (+) = 조기청산이 더 나은 가격이었다 (아낀 pt)
            saved = (exit_p - cf_price) if is_long else (cf_price - exit_p)
            updates.append((cf_outcome, cf_price, round(saved, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE signal_decay_exits
                       SET resolved=1, cf_outcome=?, cf_exit_price=?, saved_pts=?
                       WHERE id=?""",
                    updates,
                )
                conn.commit()
            out["resolved_now"] = len(updates)

    # 누적 집계 (캠페인 시작 이후 전체)
    try:
        with _conn(TRADES_DB) as conn:
            agg = conn.execute(
                """SELECT COUNT(*) AS n, SUM(saved_pts) AS total_saved,
                          SUM(CASE WHEN cf_outcome='STOP' THEN 1 ELSE 0 END) AS n_stop,
                          SUM(CASE WHEN cf_outcome='TP1' THEN 1 ELSE 0 END) AS n_tp1,
                          SUM(CASE WHEN cf_outcome='NEITHER' THEN 1 ELSE 0 END) AS n_neither
                   FROM signal_decay_exits WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM signal_decay_exits WHERE resolved=0"
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_saved = float(agg["total_saved"] or 0.0)
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_saved_pts": round(total_saved, 4),
        "cf_stop": int(agg["n_stop"] or 0),
        "cf_tp1": int(agg["n_tp1"] or 0),
        "cf_neither": int(agg["n_neither"] or 0),
    })
    if n < int(cr["min_samples"]):
        out["reason"] = "발동 표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out
    # PASS = 유지, FAIL = 롤백 권고 (§3-5: conf 임계 강화 → 그래도 음수면 OFF)
    out["verdict"] = "PASS" if total_saved >= 0 else "FAIL"
    if out["verdict"] == "FAIL":
        out["recommendation"] = "conf 임계를 zone_mc+0.05로 강화 후 2주 재관찰, 재음수 시 OFF"
    return out


# ──────────────────────────────────────────────────────────────
# [6] Hurst 게이트 counterfactual — resolve + 누적 판정 (§3-6, P1-4, 297차)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_hurst_gate() -> dict:
    """hurst_gate_shadow(main.py에서 기록) resolve + PASS/FAIL 판정.

    PASS = 게이트 존치 (차단된 신호가 실제로 손실 방향이었거나 완화 기준 미충족).
    FAIL = 사이징 완화 권고 (하드차단→×0.5로 먼저 완화, 즉시 언블록 아님 — §3-6).
    """
    cr = VALIDATION_CAMPAIGN["hurst_gate_shadow"]
    window_min = int(cr.get("cf_window_min", 30))
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM hurst_gate_shadow WHERE resolved = 0 ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    if unresolved:
        earliest = min(r["ts"] for r in unresolved)
        # 체결 시뮬 경로 — 거래불능 분봉 제외 [404차 후속5 / P0-B(a)]
        close_map, high_map, low_map = _load_candle_maps(
            earliest, exclude_untradeable=True)
        now = datetime.datetime.now()
        updates = []
        for r in unresolved:
            base = datetime.datetime.strptime(r["ts"], _TS_FMT)
            if now < base + datetime.timedelta(minutes=window_min + 2):
                continue
            is_long = str(r["direction"]) == "LONG"
            stop_p = float(r["stop_price"] or 0.0)
            tp1_p = float(r["tp1_price"] or 0.0)
            cf_outcome, cf_price = "NEITHER", None
            last_close = None
            for m in range(1, window_min + 1):
                mid = base + datetime.timedelta(minutes=m)
                if mid.time() > datetime.time(15, 10):
                    break
                mid_ts = mid.strftime(_TS_FMT)
                hi = high_map.get(mid_ts)
                lo = low_map.get(mid_ts)
                if hi is None or lo is None:
                    continue
                last_close = close_map.get(mid_ts, last_close)
                if is_long:
                    hit_stop = stop_p > 0 and lo <= stop_p
                    hit_tp = tp1_p > 0 and hi >= tp1_p
                else:
                    hit_stop = stop_p > 0 and hi >= stop_p
                    hit_tp = tp1_p > 0 and lo <= tp1_p
                # 동시 터치 → 보수적으로 STOP 우선 (signal_decay·TB 레이블과 동일 관례)
                if hit_stop:
                    cf_outcome, cf_price = "STOP", stop_p
                    break
                if hit_tp:
                    cf_outcome, cf_price = "TP1", tp1_p
                    break
            if cf_price is None:
                if last_close is None:
                    continue  # 분봉 데이터 자체가 없음 — 다음 실행에서 재시도
                cf_price = last_close
            entry_p = float(r["entry_price"])
            # hyp_pnl_pts: (+) = 차단 안 했으면 이득이었다(완화 근거), (-) = 차단이 손실 회피
            hyp = (cf_price - entry_p) if is_long else (entry_p - cf_price)
            updates.append((cf_outcome, cf_price, round(hyp, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE hurst_gate_shadow
                       SET resolved=1, cf_outcome=?, cf_exit_price=?, hyp_pnl_pts=?
                       WHERE id=?""",
                    updates,
                )
                conn.commit()
            out["resolved_now"] = len(updates)

    try:
        with _conn(TRADES_DB) as conn:
            agg = conn.execute(
                """SELECT COUNT(*) AS n, SUM(hyp_pnl_pts) AS total_hyp,
                          AVG(entry_price) AS avg_price,
                          SUM(CASE WHEN hyp_pnl_pts > 0 THEN 1 ELSE 0 END) AS n_win,
                          SUM(CASE WHEN cf_outcome='STOP' THEN 1 ELSE 0 END) AS n_stop,
                          SUM(CASE WHEN cf_outcome='TP1' THEN 1 ELSE 0 END) AS n_tp1,
                          SUM(CASE WHEN cf_outcome='NEITHER' THEN 1 ELSE 0 END) AS n_neither
                   FROM hurst_gate_shadow WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM hurst_gate_shadow WHERE resolved=0"
            ).fetchone()["n"]
            baseline = conn.execute(
                """SELECT AVG(CASE WHEN COALESCE(net_pnl_krw, pnl_krw) > 0
                                   THEN 1.0 ELSE 0.0 END) AS wr
                   FROM trades WHERE exit_ts IS NOT NULL AND exit_ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_hyp = float(agg["total_hyp"] or 0.0)
    avg_price = float(agg["avg_price"] or 0.0) or 300.0
    win_rate = (int(agg["n_win"] or 0) / n) if n else 0.0
    baseline_wr = (
        float(baseline["wr"]) if baseline and baseline["wr"] is not None else None
    )
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_hyp_pnl_pts": round(total_hyp, 4),
        "win_rate": round(win_rate, 4),
        "baseline_win_rate": round(baseline_wr, 4) if baseline_wr is not None else None,
        "cf_stop": int(agg["n_stop"] or 0),
        "cf_tp1": int(agg["n_tp1"] or 0),
        "cf_neither": int(agg["n_neither"] or 0),
    })
    if n < int(cr["min_samples"]):
        out["reason"] = "차단 표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out

    cost_pt = _roundtrip_cost_pt(avg_price)
    out["cost_pt"] = round(cost_pt, 4)
    mitigate = (
        total_hyp > cost_pt * 2.0
        and baseline_wr is not None
        and win_rate > baseline_wr
    )
    out["verdict"] = "FAIL" if mitigate else "PASS"
    if mitigate:
        out["recommendation"] = (
            "Hurst 하드차단 → 사이징 ×0.5로 완화 권고 (즉시 언블록 금지, §3-6)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# [7] JointGateBlock counterfactual — resolve + 누적 판정 (§3-7, 327차)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_joint_gate() -> dict:
    """joint_gate_shadow(main.py에서 기록) resolve + PASS/FAIL 판정.
    hurst_gate_shadow와 완전히 동일한 판정 로직 — 대상 테이블만 다르다.

    PASS = 게이트 존치 (차단된 신호가 실제로 손실 방향이었거나 완화 기준 미충족).
    FAIL = 완화 권고 (하드차단→임계값 0.50 완화부터 검토, 즉시 언블록 아님 — §3-7).

    추가로 meta_size 구간별(< 0.55 / ≥ 0.55) 승률·hyp_pnl_pts를 함께 집계한다 —
    ToxicityGate reduce의 size_multiplier가 상수 0.7이라 joint_mult이 사실상
    meta_size 단일 임계와 동치라는 구조적 의문(07-14 실측 분석,
    docs/Ref/jointfateBlock.txt)을 표본이 쌓이면 검증할 수 있게 하기 위함.
    """
    cr = VALIDATION_CAMPAIGN["joint_gate_shadow"]
    window_min = int(cr.get("cf_window_min", 30))
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM joint_gate_shadow WHERE resolved = 0 ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    if unresolved:
        earliest = min(r["ts"] for r in unresolved)
        # 체결 시뮬 경로 — 거래불능 분봉 제외 [404차 후속5 / P0-B(a)]
        close_map, high_map, low_map = _load_candle_maps(
            earliest, exclude_untradeable=True)
        now = datetime.datetime.now()
        updates = []
        for r in unresolved:
            base = datetime.datetime.strptime(r["ts"], _TS_FMT)
            if now < base + datetime.timedelta(minutes=window_min + 2):
                continue
            is_long = str(r["direction"]) == "LONG"
            stop_p = float(r["stop_price"] or 0.0)
            tp1_p = float(r["tp1_price"] or 0.0)
            cf_outcome, cf_price = "NEITHER", None
            last_close = None
            for m in range(1, window_min + 1):
                mid = base + datetime.timedelta(minutes=m)
                if mid.time() > datetime.time(15, 10):
                    break
                mid_ts = mid.strftime(_TS_FMT)
                hi = high_map.get(mid_ts)
                lo = low_map.get(mid_ts)
                if hi is None or lo is None:
                    continue
                last_close = close_map.get(mid_ts, last_close)
                if is_long:
                    hit_stop = stop_p > 0 and lo <= stop_p
                    hit_tp = tp1_p > 0 and hi >= tp1_p
                else:
                    hit_stop = stop_p > 0 and hi >= stop_p
                    hit_tp = tp1_p > 0 and lo <= tp1_p
                # 동시 터치 → 보수적으로 STOP 우선 (signal_decay·hurst_gate와 동일 관례)
                if hit_stop:
                    cf_outcome, cf_price = "STOP", stop_p
                    break
                if hit_tp:
                    cf_outcome, cf_price = "TP1", tp1_p
                    break
            if cf_price is None:
                if last_close is None:
                    continue  # 분봉 데이터 자체가 없음 — 다음 실행에서 재시도
                cf_price = last_close
            entry_p = float(r["entry_price"])
            # hyp_pnl_pts: (+) = 차단 안 했으면 이득이었다(완화 근거), (-) = 차단이 손실 회피
            hyp = (cf_price - entry_p) if is_long else (entry_p - cf_price)
            # [404차 후속9 / P1-D] 창 전체 MFE/MAE 병기 — 위 루프는 스톱/TP에서 break
            # 하므로 "얼마나 갈 수 있었나"는 따로 걸어야 한다(§2-E 자기편향 계측).
            _mfe, _mae = _mfe_mae(r["ts"], entry_p, is_long, window_min,
                                  high_map, low_map)
            updates.append((cf_outcome, cf_price, round(hyp, 4), _mfe, _mae, r["id"]))

        if updates:
            _ensure_shadow_mfe_columns("joint_gate_shadow")
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE joint_gate_shadow
                       SET resolved=1, cf_outcome=?, cf_exit_price=?, hyp_pnl_pts=?,
                           mfe_30m=?, mae_30m=?
                       WHERE id=?""",
                    updates,
                )
                conn.commit()
            out["resolved_now"] = len(updates)

    # [404차 후속9 / P1-D] 컬럼 신설 이전에 확정된 과거 행 소급 계산 (멱등)
    out["mfe_backfilled"] = _backfill_shadow_mfe("joint_gate_shadow", window_min)

    # [MW0601 420차] 419차 계측 컬럼 보강 — main.py 기동 마이그레이션의 백스톱.
    # (리포트를 라이브가 안 돈 PC/백업 DB에 대고 돌리는 경우가 있다)
    _ensure_joint_gate_columns()

    try:
        with _conn(TRADES_DB) as conn:
            # [420차] 집계를 SQL 한 방에서 파이썬으로 옮긴다 — 체제 분리·에피소드
            # 병합·jackknife는 전부 행 단위 재그룹이라 GROUP BY로 표현할 수 없다.
            all_rows = conn.execute(
                """SELECT * FROM joint_gate_shadow
                   WHERE resolved=1 AND ts >= ? ORDER BY ts""",
                (_campaign_start(),),
            ).fetchall()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM joint_gate_shadow WHERE resolved=0"
            ).fetchone()["n"]
            baseline = conn.execute(
                """SELECT AVG(CASE WHEN COALESCE(net_pnl_krw, pnl_krw) > 0
                                   THEN 1.0 ELSE 0.0 END) AS wr
                   FROM trades WHERE exit_ts IS NOT NULL AND exit_ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
    except Exception as e:
        out["error"] = str(e)
        return out

    # ── [420차] tox 체제 분리 ─────────────────────────────────────────────
    # 419차 P0(TOXICITY_CANCEL_CHURN_CEILING 0.08→0.42)이 tox 밴드 분포를 이동시켜
    # JointGateBlock의 **모집단 자체**가 바뀐다(발동 전제가 tox_action=="reduce").
    # 구·신 체제를 한 풀로 합산하면 서로 다른 두 분포의 평균을 판정하게 되므로,
    # 판정은 **항상 한 체제 안에서만** 낸다.
    _regime_date = str(cr.get("tox_regime_date", "") or "")
    # [30] toxicity_recalib_watch와 같은 배포일을 가리켜야 한다. 어긋나면 한쪽만
    # 갱신된 것이고, 그 상태로는 두 채널이 서로 다른 "재보정 시점"을 전제하게 된다.
    _recal_date = str((VALIDATION_CAMPAIGN.get("toxicity_recalib_watch") or {})
                      .get("effective_date", "") or "")
    if _regime_date and _recal_date and _regime_date != _recal_date:
        out["regime_date_mismatch"] = (
            "joint_gate_shadow.tox_regime_date=%s ≠ toxicity_recalib_watch."
            "effective_date=%s — 한쪽만 갱신됐다" % (_regime_date, _recal_date))
    _pre = [r for r in all_rows
            if not _regime_date or str(r["ts"])[:10] < _regime_date]
    _post = [r for r in all_rows
             if _regime_date and str(r["ts"])[:10] >= _regime_date]

    def _pack(rows):
        _h = [float(r["hyp_pnl_pts"] or 0.0) for r in rows]
        return {
            "n": len(rows),
            "total_hyp_pnl_pts": round(sum(_h), 4),
            "win_rate": round(sum(1 for x in _h if x > 0) / len(rows), 4) if rows else 0.0,
        }

    out["regime_split"] = {
        "boundary": _regime_date or None,
        "pre": _pack(_pre),
        "post": _pack(_post),
    }
    # 행에 새겨진 tox_ceiling과 config 날짜 경계가 어긋나면 경계가 낡은 것이다
    # (ceiling이 또 바뀌었는데 tox_regime_date를 안 고친 경우). 판정을 막지는 않되
    # 리포트에 띄운다 — 침묵하면 다음 세션이 섞인 표본을 그대로 믿는다.
    _ceil_pre = {round(float(r["tox_ceiling"]), 4) for r in _pre
                 if r["tox_ceiling"] is not None}
    _ceil_post = {round(float(r["tox_ceiling"]), 4) for r in _post
                  if r["tox_ceiling"] is not None}
    out["tox_ceiling_observed"] = {
        "pre": sorted(_ceil_pre), "post": sorted(_ceil_post)}
    if len(_ceil_pre | _ceil_post) > 1 and (_ceil_pre & _ceil_post):
        out["regime_boundary_warning"] = (
            "tox_ceiling이 경계 양쪽에 걸쳐 있다 — tox_regime_date(%s)가 실제 "
            "재보정 시점과 다를 수 있음" % (_regime_date or "미설정"))

    # 판정 대상 체제 선택: 신 체제가 min_samples에 닿으면 그것으로 갈아탄다.
    # 닿기 전에는 구 체제로 판정하되 "구 체제 기준"임을 반드시 표기한다
    # (신 체제 표본이 0인데 판정을 못 낸다고 하면 채널이 몇 주간 침묵한다).
    _min_n = int(cr["min_samples"])
    if len(_post) >= _min_n:
        rows, judged = _post, "post"
    elif _post and len(_pre) < _min_n:
        rows, judged = _post, "post"   # 양쪽 다 미달이면 최신 체제를 보여준다
    else:
        rows, judged = _pre, "pre"
    out["judged_regime"] = judged
    out["judged_regime_note"] = (
        "419차 P0 재보정 **이후**(%s~) 표본으로 판정" % _regime_date
        if judged == "post" else
        "419차 P0 재보정 **이전**(~%s) 구 체제 표본으로 판정 — 신 체제 표본 %d건 "
        "(min_samples %d 미달)" % (_regime_date, len(_post), _min_n))

    # ── MFE/MAE는 판정 대상 체제 안에서만 본다(구·신 혼합 방지) ──────────
    mfe_rows = sorted(
        [r for r in rows if r["mfe_30m"] is not None],
        key=lambda r: float(r["mfe_30m"] or 0.0), reverse=True)

    # ── MFE 대비 counterfactual 포착률 ────────────────────────────────────
    # 핵심 지표는 `cf_capture_of_mfe` = Σhyp / ΣMFE 다. TP1 가정이 "갈 수 있었던 폭"의
    # 몇 %를 잡아냈는지 보여준다 — 이 값이 낮을수록 §2-E가 지적한 과소평가가 크다.
    # 비율의 평균이 아니라 **풀링**으로 낸다(402차 후속5 원칙 — 분모가 0에 가까운 건이
    # 개별 비율을 폭발시킨다).
    if mfe_rows:
        _mf = [float(r["mfe_30m"] or 0.0) for r in mfe_rows]
        _ma = [float(r["mae_30m"] or 0.0) for r in mfe_rows]
        _hy = [float(r["hyp_pnl_pts"] or 0.0) for r in mfe_rows]
        _sum_mfe = sum(_mf)
        out["n_with_mfe"] = len(mfe_rows)
        out["avg_mfe_30m"] = round(float(np.mean(_mf)), 4)
        out["median_mfe_30m"] = round(float(np.median(_mf)), 4)
        out["avg_mae_30m"] = round(float(np.mean(_ma)), 4)
        out["total_mfe_30m"] = round(_sum_mfe, 4)
        out["total_mae_30m"] = round(sum(_ma), 4)
        if _sum_mfe > 0:
            out["cf_capture_of_mfe"] = round(sum(_hy) / _sum_mfe, 4)
        # MFE만 보면 "차단이 비쌌다"로 읽히지만 MAE를 함께 봐야 판정이 선다.
        # 차단 신호가 유리하게 간 폭보다 불리하게 간 폭이 크면 차단은 옳았던 쪽이다.
        out["n_mfe_gt_mae"] = int(sum(1 for f, a in zip(_mf, _ma) if f > a))
        out["n_mae_ge_mfe"] = int(sum(1 for f, a in zip(_mf, _ma) if a >= f))
        # MFE가 크게 났는데(추세) TP1 가정이 1pt 남짓으로 눌러버린 건 — §2-E 표의 패턴
        _big = [r for r in mfe_rows
                if float(r["mfe_30m"] or 0.0) >= 5.0
                and float(r["hyp_pnl_pts"] or 0.0) < float(r["mfe_30m"] or 0.0) * 0.3]
        out["n_trend_underestimated"] = len(_big)
        out["trend_underestimated_top5"] = [
            {"ts": r["ts"], "dir": r["direction"],
             "mfe": round(float(r["mfe_30m"] or 0.0), 2),
             "mae": round(float(r["mae_30m"] or 0.0), 2),
             "hyp": round(float(r["hyp_pnl_pts"] or 0.0), 2),
             "cf": r["cf_outcome"]}
            for r in _big[:5]]

    n = len(rows)
    _hyp = [float(r["hyp_pnl_pts"] or 0.0) for r in rows]
    total_hyp = sum(_hyp)
    _prices = [float(r["entry_price"] or 0.0) for r in rows]
    avg_price = (sum(_prices) / len(_prices)) if _prices else 0.0
    avg_price = avg_price or 300.0
    win_rate = (sum(1 for x in _hyp if x > 0) / n) if n else 0.0
    baseline_wr = (
        float(baseline["wr"]) if baseline and baseline["wr"] is not None else None
    )

    def _bucket_pack(subset):
        _s = [float(r["hyp_pnl_pts"] or 0.0) for r in subset]
        return {
            "n": len(subset),
            "total_hyp_pnl_pts": round(sum(_s), 4),
            "win_rate": round(sum(1 for x in _s if x > 0) / len(subset), 4) if subset else 0.0,
        }

    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_hyp_pnl_pts": round(total_hyp, 4),
        "win_rate": round(win_rate, 4),
        "baseline_win_rate": round(baseline_wr, 4) if baseline_wr is not None else None,
        "cf_stop": sum(1 for r in rows if r["cf_outcome"] == "STOP"),
        "cf_tp1": sum(1 for r in rows if r["cf_outcome"] == "TP1"),
        "cf_neither": sum(1 for r in rows if r["cf_outcome"] == "NEITHER"),
        "meta_size_split": {
            "high": _bucket_pack([r for r in rows
                                  if float(r["meta_size"] or 0.0) >= 0.55]),
            "low": _bucket_pack([r for r in rows
                                 if float(r["meta_size"] or 0.0) < 0.55]),
        },
    })

    # ── [420차 ①] meta falsy 폴백 분리 ───────────────────────────────────
    # 419차 발견 ④: meta_size가 정확히 0.500인 행이 73/116(62.9%)인데, 그건
    # `learned["size_multiplier"] or 0.5`가 **0.0을 falsy로 잡아 0.5로 승격**시킨
    # 결과다(모델은 "사이즈 주지 마라"고 했다). 위 high/low(0.55) 분할은 low 버킷의
    # 78%가 이 폴백이라 해석이 서지 않는다 — 그래서 별도 축으로 가른다.
    # meta_size_fallback 컬럼은 420차부터 채워지므로 그 이전 행은 NULL이다.
    # NULL을 0으로 뭉개면 폴백 건이 학습값처럼 보이므로 **미계측으로 따로 센다**.
    _fb_known = [r for r in rows if r["meta_size_fallback"] is not None]
    if _fb_known:
        out["meta_fallback_split"] = {
            "fallback": _bucket_pack([r for r in _fb_known
                                      if int(r["meta_size_fallback"] or 0) == 1]),
            "learned": _bucket_pack([r for r in _fb_known
                                     if int(r["meta_size_fallback"] or 0) == 0]),
            "unmeasured_n": n - len(_fb_known),
        }
    else:
        out["meta_fallback_split"] = {"unmeasured_n": n}

    # ── [420차 ③] 419차 P1 실적용 시 차단 유지율 (차단 축 반사실) ────────
    # [31] toxicity_reduce_mult_shadow는 **체결된** 진입만 본다 — 차단된 신호는
    # 그 채널에 없다. 여기가 그 사각지대다. 판정하지 않고 세기만 한다.
    _wb = [r for r in rows if r["would_block_shadow"] is not None]
    if _wb:
        _kept = [r for r in _wb if int(r["would_block_shadow"] or 0) == 1]
        _freed = [r for r in _wb if int(r["would_block_shadow"] or 0) == 0]
        out["p1_shadow_block"] = {
            "n": len(_wb),
            "kept_n": len(_kept),
            "freed_n": len(_freed),
            "kept_share": round(len(_kept) / len(_wb), 4),
            # 해제됐을 신호들의 실제 counterfactual 손익 — P1 실적용의 차단 축 비용/이득
            "freed": _bucket_pack(_freed),
            "shadow_mult_mean": round(
                float(np.mean([float(r["tox_size_shadow"] or 0.0) for r in _wb])), 4),
        }

    if n < _min_n:
        out["reason"] = ("차단 표본 부족 (%s 체제 %d < %d) — 판정 보류"
                         % (judged, n, _min_n))
        return out

    cost_pt = _roundtrip_cost_pt(avg_price)
    out["cost_pt"] = round(cost_pt, 4)
    mitigate = (
        total_hyp > cost_pt * 2.0
        and baseline_wr is not None
        and win_rate > baseline_wr
    )
    out["verdict"] = "FAIL" if mitigate else "PASS"
    if mitigate:
        out["recommendation"] = (
            "JointGateBlock 임계값 0.50 → 완화 검토 (즉시 언블록 금지, §3-7)"
        )

    # ── [420차 ②] 증거강도 — verdict와 별개 축 ───────────────────────────
    # 현행 verdict는 `누적 hyp ≤ 0` 이분법이라 -13pt와 -0.01pt가 같은 PASS다.
    # "FAIL이 아니다"와 "차단이 옳다"는 다른 말이므로 분리해 표기한다.
    # 통계 단위는 **에피소드 첫 신호** — JointGateBlock은 조건이 유지되는 동안 매
    # 분봉 재차단하므로 원본 행은 독립 관측치가 아니다(116신호 = 59에피소드).
    # 차단이 없었다면 그 에피소드에서 진입은 한 번 일어났을 것이므로 첫 신호가
    # 자연스러운 사건 단위다.
    _eps = _episode_reduce(rows, int(cr.get("episode_gap_min", 5)))
    _ep_first = [float(e[0]["hyp_pnl_pts"] or 0.0) for e in _eps]
    _ep_total = sum(_ep_first)
    out["episode"] = {
        "n": len(_eps),
        "signals_per_episode": round(n / len(_eps), 2) if _eps else 0.0,
        "total_hyp_pnl_pts": round(_ep_total, 4),
        "win_rate": round(sum(1 for x in _ep_first if x > 0) / len(_ep_first), 4)
                    if _ep_first else 0.0,
        "max_run": max((len(e) for e in _eps), default=0),
    }
    _t_abs = float(cr.get("evidence_t_abs", 2.0))
    if len(_ep_first) >= 2:
        _sd = float(np.std(_ep_first, ddof=1))
        _tstat = ((_ep_total / len(_ep_first)) / (_sd / len(_ep_first) ** 0.5)
                  if _sd > 0 else 0.0)
        out["episode"]["mean"] = round(_ep_total / len(_ep_first), 4)
        out["episode"]["sd"] = round(_sd, 4)
        out["episode"]["t_stat"] = round(_tstat, 3)
        # SUPPORTS_GATE = 유의하게 음수(차단이 실제로 손실을 회피).
        # REJECTS_GATE  = 유의하게 양수(차단이 비쌌다) — verdict FAIL과 같은 방향이나
        #                 FAIL은 비용×2 + 승률 조건이라 둘이 항상 일치하지는 않는다.
        # NO_EVIDENCE   = 0과 구분 불가. PASS의 대부분이 여기 해당할 수 있다.
        if abs(_tstat) < _t_abs:
            out["evidence"] = "NO_EVIDENCE"
        else:
            out["evidence"] = "SUPPORTS_GATE" if _tstat < 0 else "REJECTS_GATE"

    # ── [420차 ②-b] 단일일 민감도(jackknife) ─────────────────────────────
    # 실측(구 체제)에서 07-28 하루가 37건(32%)·-19.66pt를 차지해 그 하루를 빼면
    # 누적이 +6.49pt로 **부호가 뒤집힌다**. 판정 전체가 한 거래일에 걸려 있다는
    # 사실은 요약표만 보면 절대 드러나지 않으므로 자동 병기한다.
    if cr.get("jackknife_enabled", True) and _eps:
        _by_day = {}
        for e in _eps:
            _d = str(e[0]["ts"])[:10]
            _by_day[_d] = _by_day.get(_d, 0.0) + float(e[0]["hyp_pnl_pts"] or 0.0)
        _flips = [(d, round(c, 4), round(_ep_total - c, 4))
                  for d, c in _by_day.items()
                  if (_ep_total - c) * _ep_total < 0]
        _worst = max(_by_day.items(), key=lambda kv: abs(kv[1])) if _by_day else None
        out["jackknife"] = {
            "n_days": len(_by_day),
            "sign_flip_days": sorted(_flips, key=lambda x: abs(x[1]), reverse=True),
            "fragile": bool(_flips),
            "largest_day": ({"date": _worst[0], "contrib": round(_worst[1], 4)}
                            if _worst else None),
        }
    return out


# ──────────────────────────────────────────────────────────────
# [9] OPEN_VOLATILE 시가이격 필터 counterfactual — resolve + 누적 판정 (§14, 354차)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_open_gap() -> dict:
    """open_gap_shadow(main.py에서 기록) resolve + PASS/FAIL 판정.
    hurst_gate_shadow와 완전히 동일한 판정 로직 — 대상 테이블만 다르다.

    PASS = 게이트 존치 (차단된 신호가 실제로 손실 방향이었거나 완화 기준 미충족).
    FAIL = 재설계 검토 권고 (2026-07-16 정기점검 P2-d — 세션 시가 고정 기준점 +
    ATR 압축으로 임계가 좁아지는 구조적 결함이 실제로 피해를 낸다는 실측 근거가
    이번에 처음 확보됐다는 뜻. 즉시 언블록이 아니라 그때의 실측 gap_pt/atr_at_block
    값을 근거로 기준점(예: 최근 N분 VWAP)·임계 재설계 착수).
    """
    cr = VALIDATION_CAMPAIGN["open_gap_shadow"]
    window_min = int(cr.get("cf_window_min", 30))
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM open_gap_shadow WHERE resolved = 0 ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    if unresolved:
        earliest = min(r["ts"] for r in unresolved)
        # 체결 시뮬 경로 — 거래불능 분봉 제외 [404차 후속5 / P0-B(a)]
        close_map, high_map, low_map = _load_candle_maps(
            earliest, exclude_untradeable=True)
        now = datetime.datetime.now()
        updates = []
        for r in unresolved:
            base = datetime.datetime.strptime(r["ts"], _TS_FMT)
            if now < base + datetime.timedelta(minutes=window_min + 2):
                continue
            is_long = str(r["direction"]) == "LONG"
            stop_p = float(r["stop_price"] or 0.0)
            tp1_p = float(r["tp1_price"] or 0.0)
            cf_outcome, cf_price = "NEITHER", None
            last_close = None
            for m in range(1, window_min + 1):
                mid = base + datetime.timedelta(minutes=m)
                if mid.time() > datetime.time(15, 10):
                    break
                mid_ts = mid.strftime(_TS_FMT)
                hi = high_map.get(mid_ts)
                lo = low_map.get(mid_ts)
                if hi is None or lo is None:
                    continue
                last_close = close_map.get(mid_ts, last_close)
                if is_long:
                    hit_stop = stop_p > 0 and lo <= stop_p
                    hit_tp = tp1_p > 0 and hi >= tp1_p
                else:
                    hit_stop = stop_p > 0 and hi >= stop_p
                    hit_tp = tp1_p > 0 and lo <= tp1_p
                # 동시 터치 → 보수적으로 STOP 우선 (signal_decay·hurst_gate와 동일 관례)
                if hit_stop:
                    cf_outcome, cf_price = "STOP", stop_p
                    break
                if hit_tp:
                    cf_outcome, cf_price = "TP1", tp1_p
                    break
            if cf_price is None:
                if last_close is None:
                    continue  # 분봉 데이터 자체가 없음 — 다음 실행에서 재시도
                cf_price = last_close
            entry_p = float(r["entry_price"])
            # hyp_pnl_pts: (+) = 차단 안 했으면 이득이었다(재설계 근거), (-) = 차단이 손실 회피
            hyp = (cf_price - entry_p) if is_long else (entry_p - cf_price)
            updates.append((cf_outcome, cf_price, round(hyp, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE open_gap_shadow
                       SET resolved=1, cf_outcome=?, cf_exit_price=?, hyp_pnl_pts=?
                       WHERE id=?""",
                    updates,
                )
                conn.commit()
            out["resolved_now"] = len(updates)

    try:
        with _conn(TRADES_DB) as conn:
            agg = conn.execute(
                """SELECT COUNT(*) AS n, SUM(hyp_pnl_pts) AS total_hyp,
                          AVG(entry_price) AS avg_price,
                          SUM(CASE WHEN hyp_pnl_pts > 0 THEN 1 ELSE 0 END) AS n_win,
                          SUM(CASE WHEN cf_outcome='STOP' THEN 1 ELSE 0 END) AS n_stop,
                          SUM(CASE WHEN cf_outcome='TP1' THEN 1 ELSE 0 END) AS n_tp1,
                          SUM(CASE WHEN cf_outcome='NEITHER' THEN 1 ELSE 0 END) AS n_neither,
                          AVG(gap_pt) AS avg_gap_pt, AVG(atr_at_block) AS avg_atr
                   FROM open_gap_shadow WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM open_gap_shadow WHERE resolved=0"
            ).fetchone()["n"]
            baseline = conn.execute(
                """SELECT AVG(CASE WHEN COALESCE(net_pnl_krw, pnl_krw) > 0
                                   THEN 1.0 ELSE 0.0 END) AS wr
                   FROM trades WHERE exit_ts IS NOT NULL AND exit_ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_hyp = float(agg["total_hyp"] or 0.0)
    avg_price = float(agg["avg_price"] or 0.0) or 300.0
    win_rate = (int(agg["n_win"] or 0) / n) if n else 0.0
    baseline_wr = (
        float(baseline["wr"]) if baseline and baseline["wr"] is not None else None
    )
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_hyp_pnl_pts": round(total_hyp, 4),
        "win_rate": round(win_rate, 4),
        "baseline_win_rate": round(baseline_wr, 4) if baseline_wr is not None else None,
        "cf_stop": int(agg["n_stop"] or 0),
        "cf_tp1": int(agg["n_tp1"] or 0),
        "cf_neither": int(agg["n_neither"] or 0),
        "avg_gap_pt": round(float(agg["avg_gap_pt"] or 0.0), 2),
        "avg_atr_at_block": round(float(agg["avg_atr"] or 0.0), 2),
    })
    if n < int(cr["min_samples"]):
        out["reason"] = "차단 표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out

    cost_pt = _roundtrip_cost_pt(avg_price)
    out["cost_pt"] = round(cost_pt, 4)
    mitigate = (
        total_hyp > cost_pt * 2.0
        and baseline_wr is not None
        and win_rate > baseline_wr
    )
    out["verdict"] = "FAIL" if mitigate else "PASS"
    if mitigate:
        out["recommendation"] = (
            "OPEN_VOLATILE 시가이격 필터 재설계 검토 권고 — 실측 gap_pt/atr_at_block "
            "근거로 기준점(예: 최근 N분 VWAP)·임계 재설계 착수 (즉시 언블록 금지, P2-d)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# [21] 방향별 순EV 감시 (402차 후속5) — [13] grade_ev_inversion의 미러
# ──────────────────────────────────────────────────────────────

def eval_direction_ev_watch() -> dict:
    """LONG/SHORT 방향별 실현 순EV를 캠페인 시작일 이후 누적 판정한다.

    [13] grade_ev_inversion과 동일 구조(축만 등급→방향). 실제 체결의 net_pnl_krw를
    그대로 집계하므로 counterfactual 시뮬레이션 불필요.

    **[13]과 필터가 다르다(의도적)**: [13]은 `grade IN ('A','B','C')`이라
    구버전 entry_source=NULL·OPERATOR_MANUAL 행이 포함되지만, 이 채널은
    `entry_source='SYSTEM_AUTO'` 한정이다 — 방향 편향은 시스템 판단의 문제이므로
    수동·레거시 진입을 섞으면 안 된다. 두 채널의 표본 수가 다른 것은 결함이 아니다
    (config/settings.py:VALIDATION_CAMPAIGN['direction_ev_watch'] 주석 참조).

    또한 trades는 부분청산을 같은 entry_ts로 여러 행에 나눠 기록하므로 그대로 세면
    TP1/TP2 부분청산이 각각 '승리'로 집계돼 승률이 부풀려진다(402차가 실제로 이
    함정에 걸렸다). 여기서는 **진입 1건 단위**로 묶어 집계한다.

    PASS = 두 방향 모두 평균 순EV ≥ 0, 또는 두 방향 모두 < 0(방향이 아니라 전반 문제).
    FAIL = 한 방향만 평균 순EV < 0 이고 양쪽 표본 충분 → 그 방향 min_conf 상향/사이징
    축소를 **섀도로** 먼저 검증할지 주간회의에서 결정(§9 — 즉시 적용 아님).
    """
    cr = VALIDATION_CAMPAIGN.get("direction_ev_watch", {})
    src = cr.get("entry_source", "SYSTEM_AUTO")
    min_n = int(cr.get("min_samples_per_direction", 20))
    out = {"verdict": "INSUFFICIENT", "entry_source_filter": src}

    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT entry_ts, direction,
                          COALESCE(net_pnl_krw, pnl_krw) AS pnl
                     FROM trades
                    WHERE exit_ts IS NOT NULL AND exit_ts >= ?
                      AND COALESCE(entry_source,'') = ?
                      AND direction IN ('LONG','SHORT')""",
                (_campaign_start(), src),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    # 진입 1건 단위로 병합 — 부분청산 행 중복 제거(합산이 그 진입의 실현 손익)
    from collections import defaultdict
    merged = defaultdict(lambda: {"dir": None, "pnl": 0.0})
    for r in rows:
        k = (r["entry_ts"], r["direction"])
        merged[k]["dir"] = r["direction"]
        merged[k]["pnl"] += float(r["pnl"] or 0.0)

    by_dir = defaultdict(list)
    for v in merged.values():
        by_dir[v["dir"]].append(v["pnl"])

    stats = {}
    for d, pnls in by_dir.items():
        arr = np.array(pnls, dtype=float)
        stats[d] = {
            "n": len(pnls),
            "avg_pnl_krw": round(float(arr.mean()), 0),
            "total_pnl_krw": round(float(arr.sum()), 0),
            "win_rate": round(float((arr > 0).mean()), 4),
            "min_pnl_krw": round(float(arr.min()), 0),
            "stdev_pnl_krw": round(float(arr.std(ddof=1)) if len(pnls) > 1 else 0.0, 0),
        }
    out["by_direction"] = stats
    out["n_entries_merged"] = len(merged)
    out["n_rows_raw"] = len(rows)

    lo = stats.get("LONG")
    sh = stats.get("SHORT")
    if not lo or not sh or lo["n"] < min_n or sh["n"] < min_n:
        out["reason"] = ("방향별 표본 부족 (LONG %d / SHORT %d, 각 %d 필요) — 판정 보류"
                         % (lo["n"] if lo else 0, sh["n"] if sh else 0, min_n))
        return out

    neg = [d for d in ("LONG", "SHORT") if stats[d]["avg_pnl_krw"] < 0]
    if len(neg) == 1:
        d = neg[0]
        out["verdict"] = "FAIL"
        out["recommendation"] = (
            "%s 방향만 평균 순EV 음수(%s원, n=%d, 최대손실 %s원, 표준편차 %s원) — "
            "해당 방향 min_conf 상향/사이징 축소를 섀도로 먼저 검증할지 주간회의에서 "
            "결정(즉시 적용 아님). 최대손실·표준편차로 단일건 지배 여부를 먼저 확인할 것."
            % (d, format(stats[d]["avg_pnl_krw"], ",.0f"), stats[d]["n"],
               format(stats[d]["min_pnl_krw"], ",.0f"),
               format(stats[d]["stdev_pnl_krw"], ",.0f"))
        )
    else:
        out["verdict"] = "PASS"
        if len(neg) == 2:
            out["reason"] = "두 방향 모두 평균 순EV 음수 — 방향 편향이 아니라 전반 성능 문제"
    return out


# ──────────────────────────────────────────────────────────────
# [22] MFE 캡처율 관찰 (402차 후속5) — verdict 항상 OBSERVE
# ──────────────────────────────────────────────────────────────

def eval_mfe_capture_watch() -> dict:
    """캡처율 = 실현 pt / 진입 후 최대 유리폭(MFE) pt 를 누적 관찰한다.

    fast_reversal_watch·exit_fill_slippage_watch와 동일한 관찰 계열 — verdict는 항상
    OBSERVE 고정이며 이 수치로 정책을 바꾸지 않는다. 이 지표로 내릴 결정
    ("청산을 더 늦춰라")은 이미 [12] tp1_trail_shadow가 판정 중이므로, 이 채널은
    그 판정을 해석할 맥락("캡처율이 이렇게 낮은데도 트레일링이 안 낫다")만 제공한다.

    두 가지를 함께 낸다:
      capture_in_hold  실현 / 보유구간(진입~청산) MFE — "고점에서 나왔나"
      capture_to_close 실현 / 진입~15:10 MFE        — "더 들고 갈 수 있었나"

    집계 단위는 진입 1건(부분청산 행 병합, 수량가중 평균 실현 pt).
    """
    cr = VALIDATION_CAMPAIGN.get("mfe_capture_watch", {})
    src = cr.get("entry_source", "SYSTEM_AUTO")
    min_note = int(cr.get("min_samples_for_note", 20))
    out = {"verdict": "OBSERVE", "entry_source_filter": src}

    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT entry_ts, exit_ts, direction, entry_price,
                          pnl_pts, quantity
                     FROM trades
                    WHERE exit_ts IS NOT NULL AND exit_ts >= ?
                      AND COALESCE(entry_source,'') = ?
                      AND direction IN ('LONG','SHORT')
                    ORDER BY entry_ts""",
                (_campaign_start(), src),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out
    if not rows:
        out["reason"] = "표본 없음"
        return out

    from collections import defaultdict
    merged = {}
    for r in rows:
        k = (r["entry_ts"], r["direction"], round(float(r["entry_price"] or 0.0), 2))
        m = merged.setdefault(k, {"pts_w": 0.0, "qty": 0, "exit_ts": r["exit_ts"]})
        q = int(r["quantity"] or 1)
        m["pts_w"] += float(r["pnl_pts"] or 0.0) * q
        m["qty"] += q
        if (r["exit_ts"] or "") > (m["exit_ts"] or ""):
            m["exit_ts"] = r["exit_ts"]

    earliest = min(k[0] for k in merged)[:10] + " 00:00:00"
    # MFE 계산 — 체결 가능했던 분봉만 [404차 후속5 / P0-B(a)]
    _, high_map, low_map = _load_candle_maps(earliest, exclude_untradeable=True)

    def mfe(entry_ts, until_ts, ep, is_long):
        t = datetime.datetime.strptime(entry_ts[:19], _TS_FMT).replace(second=0)
        end = datetime.datetime.strptime(until_ts[:19], _TS_FMT).replace(second=0)
        best = 0.0
        seen = False
        while t <= end:
            t += datetime.timedelta(minutes=1)
            key = t.strftime(_TS_FMT)
            hi = high_map.get(key)
            lo = low_map.get(key)
            if hi is None or lo is None:
                continue
            seen = True
            fav = (hi - ep) if is_long else (ep - lo)
            if fav > best:
                best = fav
        return best if seen else None

    samples = []
    for (ets, d, ep), m in sorted(merged.items()):
        if not m["qty"]:
            continue
        realized = m["pts_w"] / m["qty"]
        is_long = d == "LONG"
        cutoff = ets[:10] + " 15:10:00"
        mfe_hold = mfe(ets, m["exit_ts"], ep, is_long)
        mfe_close = mfe(ets, cutoff, ep, is_long)
        samples.append({"ts": ets, "dir": d, "realized_pt": round(realized, 3),
                        "mfe_hold_pt": round(mfe_hold, 3) if mfe_hold is not None else None,
                        "mfe_close_pt": round(mfe_close, 3) if mfe_close is not None else None})

    out["n_entries"] = len(merged)
    out["n_rows_raw"] = len(rows)

    # [402차 후속5] 캡처율은 **비율의 평균이 아니라 풀링 비율**로 낸다.
    # 손실 거래는 분자가 음수인데 분모(MFE)가 0에 가까워 개별 비율이 폭발한다
    # (초안이 실제로 -672.9%를 출력했다). ΣRealized/ΣMFE는 그 특이점이 없다.
    # 아울러 pt 단위 "미실현 잔여(MFE-실현)"를 함께 낸다 — 비율보다 해석이 직관적이고
    # 합산이 되며, 애초에 F 제안이 물었던 "얼마나 흘렸나"에 직접 답한다.
    def pooled(key):
        pair = [(s["realized_pt"], s[key]) for s in samples
                if s[key] is not None and s[key] > 0]
        if not pair:
            return None, None, 0
        num = sum(p[0] for p in pair)
        den = sum(p[1] for p in pair)
        left = [p[1] - p[0] for p in pair]
        return (round(num / den, 4) if den else None,
                round(float(np.mean(left)), 3), len(pair))

    ch, lh, nh = pooled("mfe_hold_pt")
    cc, lc, nc = pooled("mfe_close_pt")
    out["capture_in_hold_pooled"] = ch
    out["avg_left_in_hold_pt"] = lh
    out["n_hold"] = nh
    out["capture_to_close_pooled"] = cc
    out["avg_left_to_close_pt"] = lc
    out["n_close"] = nc

    # 승리 거래만의 캡처율 — "이겼을 때 고점 대비 얼마나 챙겼나".
    # 손실 거래의 캡처율은 의미가 없으므로(음수/양수 비율) 분리해서 본다.
    win = [s for s in samples if s["realized_pt"] > 0 and s["mfe_close_pt"]]
    if win:
        out["capture_to_close_pooled_winners"] = round(
            sum(s["realized_pt"] for s in win) / sum(s["mfe_close_pt"] for s in win), 4)
        out["n_winners"] = len(win)

    _mh = [s["mfe_hold_pt"] for s in samples if s["mfe_hold_pt"] is not None]
    _mc = [s["mfe_close_pt"] for s in samples if s["mfe_close_pt"] is not None]
    if _mh:
        out["avg_mfe_hold_pt"] = round(float(np.mean(_mh)), 3)
    if _mc:
        out["avg_mfe_close_pt"] = round(float(np.mean(_mc)), 3)
    out["avg_realized_pt"] = (round(float(np.mean([s["realized_pt"] for s in samples])), 3)
                              if samples else None)
    # 상위 5건은 비율이 아니라 **잔여 pt**로 정렬 — 가장 많이 흘린 순
    out["most_left5"] = sorted(
        [s for s in samples if s["mfe_close_pt"] is not None],
        key=lambda s: -(s["mfe_close_pt"] - s["realized_pt"]))[:5]
    if nc < min_note:
        out["reason"] = ("표본 %d < %d — 참고 수치만 (관찰 채널이라 판정은 없음)"
                         % (nc, min_note))
    return out


# ──────────────────────────────────────────────────────────────
# [23] EOD 모델가드 판정 괴리 감시 (404차 신설)
# ──────────────────────────────────────────────────────────────

def _ensure_guard_shadow_columns() -> None:
    """[MW0602 457차] guard_shadow_log의 457차 컬럼을 보장한다(멱등).

    `_ensure_joint_gate_columns`와 완전히 같은 사정 — 스키마 원본은
    `utils/db_utils.py`지만 두 PC가 각자 로컬 trades.db를 갖고 있고, 리포트가
    앱 재기동보다 먼저 돌 수 있다. 컬럼이 없으면 아래 SELECT가 예외를 내고
    `out["error"]`로 삼켜져 **채널이 조용히 죽는다**(420차 joint_gate_shadow와
    동일한 사고 형태). 여기가 2차 방어선이다.
    """
    try:
        with _conn(TRADES_DB) as conn:
            have = {r[1] for r in conn.execute(
                "PRAGMA table_info(guard_shadow_log)").fetchall()}
            if "fair_valid" not in have:
                conn.execute(
                    "ALTER TABLE guard_shadow_log ADD COLUMN fair_valid INTEGER")
    except Exception as e:
        print("[WARN] guard_shadow_log 컬럼 보장 실패: %s" % e, file=sys.stderr)


def eval_guard_shadow_channel(days: int) -> dict:
    """가드가 실제 판정에 쓰는 acc.txt 기준 결과(actual_verdict)와, old_acc_live
    (동일폴드 재측정) vs new(cv)의 공정비교 결과(fair_verdict)가 얼마나 자주
    어긋나는지 누적 판정한다(guard_shadow_log 테이블).

    missed_upgrade = fair_verdict가 REPLACE인데 actual_verdict가 HOLD인 행 —
    "공정비교로는 신모델이 나은데 acc.txt 때문에 가드가 구모델을 유지시킨" 경우.
    07-31 최초 라이브 관측(6개 호라이즌 중 3개, dev_memory/DECISION_LOG.md
    404차 항목)이 이 채널을 만든 계기이지만, PASS/FAIL 임계값은 그 단일일
    관측치에 맞추지 않고 독립적으로 고정했다(313차 원칙).

    [MW0601 405차 / P0-5] **PC별로 분리 판정한다.** 이 채널은 두 PC에서 정반대로
    나온다 — 07-31 실측 기준 MW0601은 6개 호라이즌 전부 공정비교로도 HOLD여서
    missed_upgrade_rate=0%인데, MW0602는 3개(3m/5m/10m)가 신모델 우세라 50%다.
    합산하면 상반된 신호가 상쇄돼 무의미한 값이 되므로, verdict는 **이 PC의 행만으로**
    계산하고 다른 PC 행은 참고용으로만 표시한다([23-B] tp1_x2 +32.78 vs -19.04에
    이은 두 번째 PC간 부호 역전 — 313차 원칙상 한 표본으로 합칠 수 없다).
    현재 두 머신은 각자 로컬 trades.db를 쓰므로 실질 필터링은 no-op이지만,
    DB를 합치거나 옮기는 순간 조용히 오염되는 것을 막는 방어선이다.
    """
    cr = VALIDATION_CAMPAIGN["guard_shadow"]
    out = {"verdict": "INSUFFICIENT", "n_samples": 0, "n_days": 0}
    cutoff = max(
        (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(_TS_FMT),
        _campaign_start(),
    )
    _ensure_guard_shadow_columns()
    try:
        with _conn(TRADES_DB) as conn:
            all_rows = conn.execute(
                """SELECT ts, horizon, acc_txt, old_acc_live, new_cv, live_note,
                          distortion, actual_verdict, fair_verdict, pc,
                          fair_new, fair_old, fair_hold_bars, fair_valid
                     FROM guard_shadow_log
                    WHERE ts >= ? AND source = 'eod'
                    ORDER BY ts""",
                (cutoff,),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    # pc=NULL은 405차 이전 기록 — 로컬 DB이므로 이 PC 것으로 간주(하위호환).
    _me = _pc_id()
    out["pc"] = _me
    rows = [r for r in all_rows if (r["pc"] or _me) == _me]
    _other = {}
    for r in all_rows:
        _p = r["pc"] or _me
        if _p != _me:
            _other[_p] = _other.get(_p, 0) + 1
    if _other:
        out["other_pc_rows_excluded"] = _other

    out["n_samples"] = len(rows)
    out["n_days"] = len({r["ts"][:10] for r in rows})
    _live_fail = [r for r in rows if r["fair_verdict"] is None]
    out["n_live_measure_failed"] = len(_live_fail)

    # [MW0601 405차 / P1-1] 공정 홀드아웃 섀도 요약 — **판정 미반영, 표시 전용**.
    # 위 fair_verdict은 "현행이 이미 학습한 폴드"로 잰 값이라 현행에 유리하다.
    # fair_new/fair_old는 최신 구간을 학습에서 완전히 뺀 도전자와 현행을 같은
    # 구간으로 채점한 값이다(현행 pkl은 intraday가 덮어써 여전히 유리할 수 있어
    # 격차는 하한이다 — batch_retrainer._measure_fair_holdout 주석 참조).
    #
    # 🔴 [MW0602 457차] **fair_valid=1 행만 요약한다.** 405차가 한계로 적어둔
    # "현행 pkl은 intraday가 덮어써 여전히 유리할 수 있다"가 관측이 아니라 **상시
    # 상태**였음이 457차에 확인됐다. 2026-07-31~08-10 실측 36행 중 **35행(97%)**
    # 도전자 열위, 평균 격차 -0.1161, 그리고 fair_note의 구모델 mtime이 전부 당일
    # 장중 재학습(예: 08-10 14:16)이라 홀드아웃 1850봉을 통째로 학습한 모델과 비교
    # 중이었다. 그 표본으로 "도전자가 나쁘다"를 읽으면 모든 모델이 영구 동결된다.
    # 이제 사이드카 메타(gbm_{h}_meta.json)의 train_end_ts로 오염을 직접 판정한다.
    # fair_valid IS NULL = 457차 이전 행 → 오염 여부 불명 → 요약에서 제외.
    _fair_all = [r for r in rows
                 if r["fair_new"] is not None and r["fair_old"] is not None]
    _fair = [r for r in _fair_all if r["fair_valid"] == 1]
    _fair_invalid = len(_fair_all) - len(_fair)
    if _fair_all:
        out["fair_holdout_invalid_n"] = _fair_invalid
        out["fair_holdout_invalid_rate"] = round(_fair_invalid / len(_fair_all), 4)
    if _fair:
        _gaps = [float(r["fair_new"]) - float(r["fair_old"]) for r in _fair]
        out["fair_holdout"] = {
            "n": len(_fair),
            "n_excluded_invalid": _fair_invalid,
            "n_new_better": sum(1 for g in _gaps if g > 0),
            "mean_gap": round(float(np.mean(_gaps)), 4),
            "hold_bars": int(_fair[-1]["fair_hold_bars"] or 0),
            "note": "판정 미반영 — 유효표본 누적 후 old_acc 인자 교체 여부를 주간회의 결정(§9)",
        }
    elif _fair_all:
        out["fair_holdout"] = {
            "n": 0,
            "n_excluded_invalid": _fair_invalid,
            "note": ("⚠ 유효 표본 0 — 측정된 %d행 전부 현행이 홀드아웃을 학습한 상태다"
                     "(457차). 이 채널의 fair_* 수치를 성능차로 인용하지 말 것."
                     % _fair_invalid),
        }

    fair_rows = [r for r in rows if r["fair_verdict"] is not None]
    if len(rows) < cr["min_samples"] or out["n_days"] < cr["min_days"]:
        out["reason"] = "표본 부족 (%d건/%d일 < %d건/%d일)" % (
            len(rows), out["n_days"], cr["min_samples"], cr["min_days"])
        return out
    if not fair_rows:
        out["reason"] = "공정비교 가능 표본 없음 (동일폴드 재측정 전부 실패)"
        return out

    missed = [r for r in fair_rows
              if r["fair_verdict"] == "REPLACE" and r["actual_verdict"] == "HOLD"]
    out["n_fair"] = len(fair_rows)
    out["missed_upgrade_n"] = len(missed)
    out["missed_upgrade_rate"] = round(len(missed) / len(fair_rows), 4)
    _dist = [r["distortion"] for r in fair_rows if r["distortion"] is not None]
    if _dist:
        out["mean_distortion"] = round(float(np.mean(_dist)), 4)

    by_hz = {}
    for r in fair_rows:
        b = by_hz.setdefault(r["horizon"], {"n": 0, "missed": 0})
        b["n"] += 1
        if r["fair_verdict"] == "REPLACE" and r["actual_verdict"] == "HOLD":
            b["missed"] += 1
    out["by_horizon"] = by_hz

    out["verdict"] = (
        "FAIL" if out["missed_upgrade_rate"] >= cr["missed_upgrade_rate_max"] else "PASS"
    )
    return out


# ──────────────────────────────────────────────────────────────
# [28]/[29] 사이징 역예측 · mean-revert 사이즈 (MW0601 405차) — 사전등록
# ──────────────────────────────────────────────────────────────

# `entry_source` 컬럼이 신설된 커밋(311차 후속4 `cf2d1b4`, 2026-07-12). 이보다 앞선
# 행은 값이 NULL이며 "출처 미상"이 아니라 **라벨 도입 이전**이라는 뜻이다 — 아래
# `_SYSTEM_AUTO_SQL` 주석 참조.
_ENTRY_SOURCE_COLUMN_ADDED = "2026-07-12"

# [MW0601 417차 / ③-1] "시스템 자동진입" 술어 — 하위호환 포함.
#
# **왜 `entry_source='SYSTEM_AUTO'` 단독으로는 안 되나.** 그 필터는 문자 그대로는
# 진입 출처를 거르지만, 컬럼이 2026-07-12에야 신설돼 그 이전 행이 전부 NULL이라
# **실제로는 "07-14 이후만"이라는 날짜 필터로 작동**했다. 그 결과 3계약+ 진입이
# 존재하던 유일한 구간(06-10~07-10, 129행)이 통째로 빠져 [28]의 qty≥3 버킷이
# 표본 0건이 됐다 — 채널이 감시하라고 만들어진 바로 그 현상을 못 보는 상태.
#
# **NULL을 시스템으로 봐도 안전한 근거(실측).** NULL 129행의 grade 분포는
# A=109 / B=8 / C=7 / 공백=5이고 **MANUAL이 0건**이다. 반대로 grade='MANUAL' 행은
# 전부 `entry_source='GHOST_PENDING_MISS'`로 라벨돼 있다. 즉 NULL 구간에 수동·유령
# 진입이 섞여 들어올 경로가 없다. 그래도 `grade <> 'MANUAL'`을 함께 걸어 이중으로
# 막는다(향후 백필로 NULL이 다시 생겨도 안전하도록).
#
# 판정식·합격선 무변경 — 모집단 정정은 계측 버그 수정이지 기준 완화가 아니다
# (409차 `ef3ee59`가 [13] 집계단위 정정에 적용한 것과 동일 논리, §9-4 리셋 대상 아님).
_SYSTEM_AUTO_SQL = (
    "(COALESCE(entry_source,'') = 'SYSTEM_AUTO' "
    " OR (entry_source IS NULL AND COALESCE(grade,'') <> 'MANUAL'))"
)


def _trades_has_column(name):
    """trades 테이블에 해당 컬럼이 있는지. 마이그레이션 이전 DB에서도 죽지 않게."""
    try:
        with _conn(TRADES_DB) as conn:
            return name in {r["name"] for r in
                            conn.execute("PRAGMA table_info(trades)").fetchall()}
    except Exception:
        return False


def _merged_positions(extra_cols=""):
    """진입 1건(entry_ts) 단위로 병합한 시스템 자동진입 포지션 목록.

    [21]·[13]과 동일 관례 — trades는 부분청산을 같은 entry_ts로 여러 행에 나눠
    기록하므로 그대로 세면 승률이 부풀려진다(402차가 실제로 걸린 함정).

    **수량은 `sum`이다** — [MW0601 417차 / ①] 정정.
      `trades.quantity`는 **청산 행별 계약수**이지 포지션 크기가 아니다. 405차가 이
      헬퍼를 만들 때는 `max`를 썼고 근거를 "부분청산으로 줄어들기 전 원래 진입
      규모"라 적었으나, 409차 `ef3ee59`가 실측으로 반증했다 —
      `2026-07-10 11:37:04`은 TP1 부분청산 2 + 하드스톱 3 = **5계약**인데 max로 세면
      3계약으로 잡힌다. 같은 커밋이 [13]을 sum으로 고쳤고 여기만 max로 남아 있어
      **한 파일 안에서 규칙이 엇갈리던 것**을 정합화한다.

      `max`의 편향 방향이 특히 나쁘다: 이익 포지션은 TP1/TP2/TP3로 쪼개져 나가
      최대 레그가 진입 규모보다 작게 잡히고, 손실 포지션은 하드스톱 전량청산이라
      max = 진입 규모다. 즉 **큰 계약수 구간에 손실만 남기는 방향으로 편향**돼
      [28]이 탐지하려는 역전을 스스로 만들어낸다(실측: 캠페인 구간 qty≥3 격차가
      max 1,313,295원 → sum 700,485원으로 87% 부풀려져 있었다).

    `entry_qty`(417차 ②)가 있으면 그것을 우선 쓴다 — 진입 시점에 기록된 값이라
    병합 추정이 필요 없다. 컬럼이 없거나 구버전 행이면 sum으로 폴백한다.
    """
    use_entry_qty = _trades_has_column("entry_qty")
    cols = "entry_ts, quantity, COALESCE(net_pnl_krw, pnl_krw) AS pnl"
    if use_entry_qty:
        cols += ", entry_qty"
    if extra_cols:
        cols += ", " + extra_cols
    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                "SELECT %s FROM trades WHERE exit_ts IS NOT NULL AND exit_ts >= ? "
                "AND %s" % (cols, _SYSTEM_AUTO_SQL),
                (_campaign_start(),),
            ).fetchall()
    except Exception:
        return []
    merged = {}
    for r in rows:
        k = r["entry_ts"]
        m = merged.setdefault(k, {"entry_ts": k, "pnl": 0.0, "qty": 0,
                                  "qty_recorded": None, "legs": 0})
        m["pnl"] += float(r["pnl"] or 0.0)
        m["qty"] += int(r["quantity"] or 1)
        m["legs"] += 1
        if use_entry_qty and m["qty_recorded"] is None:
            try:
                _eq = int(r["entry_qty"] or 0)
            except (TypeError, ValueError):
                _eq = 0
            if _eq > 0:
                m["qty_recorded"] = _eq
        for c in [c.strip() for c in extra_cols.split(",") if c.strip()]:
            if c not in m:
                m[c] = r[c]
    out = []
    for m in merged.values():
        # 기록값이 있으면 그것이 진실이다. 없으면 레그 합(417차 ①).
        m["qty_sum"] = m["qty"]
        if m.get("qty_recorded"):
            m["qty"] = m["qty_recorded"]
        out.append(m)
    return out


def _bucket_stats(pnls):
    arr = np.array(pnls, dtype=float)
    return {
        "n": int(arr.size),
        "avg_pnl_krw": round(float(arr.mean()), 0),
        "total_pnl_krw": round(float(arr.sum()), 0),
        "win_rate": round(float((arr > 0).mean()), 4),
        "min_pnl_krw": round(float(arr.min()), 0),
    }


def _sizer_pressure_from_trace(since: str = None) -> dict:
    """[MW0601 471차 후속6 / G-1] 사이저 압력 실측 — `sizing_trace`(JSON) 집계.

    무엇을 재나: **사이저가 내놓은 수량**과 **게이트 통과 후 최종 수량**의 분포 차이.
    [28]이 판정하려는 "계약수 역예측"은 표본이 qty≥3에 안 쌓여 구조적으로 막혀 있는데,
    그 원인이 (a) 진입이 적어서인지 (b) 사이저 뒤 게이트 체인에 눌려서인지를
    가르는 것이 이 지표다. 417차가 TRADE 로그로 한 번 손으로 셌고(379건 중 86건이
    3계약 이상), 그 값이 DB에 없어 매주 그대로 재인용돼 왔다.

    ⚠ **판정에 관여하지 않는다.** 관측치만 돌려준다 — 합격선 변경 금지(§9).
    ⚠ `sizing_trace`는 471차 후속6(2026-08-14) 이후 행에만 있다. 그 이전은 NULL이며
      **미측정**이지 "압력 0"이 아니다(계측 4원칙 ②). `since_effective`로 표기한다.
    """
    out = {"available": False}
    since = since or _campaign_start()
    try:
        with _conn(PREDICTIONS_DB) as conn:
            cols = {r[1] for r in conn.execute(
                "PRAGMA table_info(ensemble_decisions)").fetchall()}
            if "sizing_trace" not in cols:
                out["reason"] = ("`sizing_trace` 컬럼 없음 — 471차 후속6 미배포 PC "
                                 "(구 하드코딩 수치를 그대로 읽지 말 것)")
                return out
            rows = conn.execute(
                "SELECT ts, sizing_trace FROM ensemble_decisions "
                " WHERE ts >= ? AND sizing_trace IS NOT NULL ORDER BY ts",
                (since,),
            ).fetchall()
    except Exception as e:
        out["reason"] = "조회 실패 — %s: %s" % (type(e).__name__, e)
        return out

    if not rows:
        out["reason"] = ("`sizing_trace` 표본 0 — 배포 직후이거나 사이저가 돈 분이 없다 "
                         "(NULL은 미측정이지 0이 아니다)")
        return out

    n_ge3 = n_entered = 0
    entered_qty = []
    raw_hist, final_hist, binding = {}, {}, {}
    for r in rows:
        try:
            t = json.loads(r["sizing_trace"])
        except Exception:
            continue
        _raw = int(t.get("qty_sizer_raw") or 0)
        _fin = int(t.get("qty_auto") or 0)
        raw_hist[_raw] = raw_hist.get(_raw, 0) + 1
        final_hist[_fin] = final_hist.get(_fin, 0) + 1
        if _raw >= 3:
            n_ge3 += 1
        _bg = t.get("binding_gate")
        binding[_bg or "(없음)"] = binding.get(_bg or "(없음)", 0) + 1
        if int(t.get("entry_executed") or 0):
            n_entered += 1
            entered_qty.append(_fin)

    n = len(rows)
    out.update({
        "available": True,
        "since_effective": rows[0]["ts"][:10],
        "n_sizer_runs": n,
        "n_days": len({r["ts"][:10] for r in rows}),
        "n_sizer_ge3": n_ge3,
        "pct_sizer_ge3": round(100.0 * n_ge3 / n, 1),
        "qty_sizer_raw_hist": dict(sorted(raw_hist.items())),
        "qty_final_hist": dict(sorted(final_hist.items())),
        "binding_gate_hist": dict(sorted(binding.items(), key=lambda kv: -kv[1])),
        "n_entered": n_entered,
        "entered_qty_ge3": int(sum(1 for q in entered_qty if q >= 3)),
    })
    out["reason"] = (
        "사이저 %d회/%d일 중 3계약+ 출력 %d회(%.1f%%) → 실제 3계약+ 체결 %d건. "
        "최빈 binding=%s (실측 기준일 %s~)"
        % (n, out["n_days"], n_ge3, out["pct_sizer_ge3"], out["entered_qty_ge3"],
           (list(out["binding_gate_hist"]) or ["—"])[0], out["since_effective"])
    )
    return out


def eval_sizing_inversion_watch() -> dict:
    """[28] 사이징 역예측 감시 (MW0601 405차 / P1-2) — 사전등록.

    계약수 구간별 실현 순EV가 역전(사이즈를 키울수록 나빠짐)돼 있는지 누적 판정한다.
    상세 근거·판정 규약은 config.settings:VALIDATION_CAMPAIGN["sizing_inversion_watch"]
    주석 참조. **자동 조치 없음** — MAX_CONTRACTS 인하는 주간회의 수동 결정(§9).
    """
    cr = VALIDATION_CAMPAIGN.get("sizing_inversion_watch", {})
    min_n = int(cr.get("min_samples_per_bucket", 20))
    min_d = int(cr.get("min_days", 5))
    gap = float(cr.get("inversion_gap_krw", 200000))
    out = {"verdict": "INSUFFICIENT", "entry_source_filter": cr.get("entry_source", "SYSTEM_AUTO")}

    pos = _merged_positions()
    if not pos:
        out["reason"] = "표본 없음"
        return out
    out["n_positions"] = len(pos)
    out["n_days"] = len({p["entry_ts"][:10] for p in pos})
    # [417차 ①/②] 수량이 어디서 왔는지 남긴다 — 이 채널은 계약수가 판정의 축이라
    # 집계 출처가 바뀌면 과거 리포트와 숫자가 달라진다. 그 이유를 설명 없이 두면
    # 405차→409차→417차처럼 같은 혼란이 반복된다.
    out["qty_source"] = {
        "entry_qty_recorded": sum(1 for p in pos if p.get("qty_recorded")),
        "leg_sum_fallback": sum(1 for p in pos if not p.get("qty_recorded")),
        "note": "entry_qty(진입시 기록)가 있으면 우선, 없으면 청산레그 합(sum). "
                "405차의 max 집계는 409차 실측 반증으로 폐기(417차 ①).",
    }

    buckets = {"qty1": [], "qty2": [], "qty3plus": []}
    for p in pos:
        key = "qty1" if p["qty"] <= 1 else ("qty2" if p["qty"] == 2 else "qty3plus")
        buckets[key].append(p["pnl"])
    out["by_bucket"] = {k: _bucket_stats(v) for k, v in buckets.items() if v}

    # 계약수 상한 카운터팩추얼 — "상한 N이었다면 얼마였나"는 계산할 수 없다
    # (사이즈가 달랐으면 체결·청산 경로도 달랐을 것). 대신 상한 초과분을 제외한
    # 부분합만 제시한다 — 해석은 "그 거래들을 아예 안 했다면"이다.
    out["excl_above_cap_krw"] = {
        str(cap): round(sum(p["pnl"] for p in pos if p["qty"] <= cap), 0)
        for cap in (1, 2, 3)
    }
    out["all_krw"] = round(sum(p["pnl"] for p in pos), 0)

    b1, b3 = out["by_bucket"].get("qty1"), out["by_bucket"].get("qty3plus")

    # [MW0601 417차 / ③-2] 표본 정체 진단 — **게이트 체인에 눌린 상태**.
    #
    # **왜 필요한가.** 이 채널은 CLAUDE.md 실전전환기준 ⑧이 "MAX_CONTRACTS 인하 판단의
    # 근거"로 명시 지정한 곳인데, qty≥3 버킷이 안 채워지는 이유가 두 가지로 전혀 다른데
    # 둘 다 똑같이 `INSUFFICIENT`로만 보인다:
    #   (a) 진입이 적어 아직 모이는 중 — 기다리면 판정된다
    #   (b) 3계약+ 진입 자체가 계통적으로 발생하지 않음 — 기다려도 안 채워진다
    # 실제 상태는 (b)다.
    #
    # **원인은 사이징 자본이 아니라 사이저 뒤의 곱셈 게이트 체인이다** (417차 로그 실측,
    # 2026-07-14~07-31): `[Sizer]` 호출 379건 중 **86건(22.7%)이 3계약 이상을 출력**했고
    # 최대 6계약까지 나왔다. 그중 실제 진입까지 간 69건이 전부 meta·tox·hurst·L2 배수
    # (`main.py`의 `_qty_display = max(1, int(round(qty × mult)))` 연쇄)에 눌려 1~2계약으로
    # 체결됐다 — **qty≥3 체결 0건**. 대표적으로 `meta≈0.50 × tox=0.70 ≈ 0.35`가 최빈
    # 조합이라 사이저 3계약이 1계약이 된다.
    #
    # 따라서 이 채널은 **죽은 게 아니라 눌려 잠든 상태**이며, 깨어나는 조건이 실재한다:
    # ⑧ 해제로 base_risk가 오르거나(사이저 출력 상승) MetaGate/ToxicityGate 배수가
    # 완화되면 즉시 표본이 생긴다. 그때가 바로 이 채널이 필요한 시점이므로 **삭제하면
    # 안 된다** — 417차 조사 결론(확정 결정 레지스트리 9건 중 채널 삭제 선례 0건,
    # 전부 "부결/판정보류"로 기록하고 채널은 계속 운영).
    #
    # 판정(verdict)은 INSUFFICIENT 그대로 둔다 — **합격선을 낮추지 않는다**(313차:
    # 사후 데이터로 기준을 움직이는 것 금지). 바꾸는 것은 "왜 판정 못 하는가"의 가시성뿐.
    #
    # ⚠ 위 사이저 출력 통계는 TRADE 로그에서만 얻을 수 있어(DB에 원시 사이저 출력
    # 컬럼이 없다) 여기서 매주 재계산하지 않는다. 수치가 낡았는지 의심되면
    # `logs/*_TRADE.log`의 `[Sizer] ... → N계약`과 `[SizerMatch]`를 재집계할 것.
    recent_days = sorted({p["entry_ts"][:10] for p in pos})[-int(cr.get("min_days", 5)):]
    n3_recent = sum(1 for p in pos if p["qty"] >= 3 and p["entry_ts"][:10] in recent_days)
    n3_total = len(buckets["qty3plus"])
    out["n_qty3plus_recent"] = n3_recent
    out["structural_block"] = bool(n3_total == 0 or n3_recent == 0)
    if out["structural_block"]:
        out["structural_reason"] = (
            "최근 %d거래일 qty≥3 **체결** %d건 (누적 %d건). 원인은 사이징 자본이 아니라 "
            "**사이저 뒤의 곱셈 게이트 체인**이다 — 417차 로그 실측(2026-07-14~07-31)에서 "
            "`[Sizer]`는 379건 중 86건(22.7%%)이 3계약 이상을 출력했고 최대 6계약까지 "
            "나왔으나, 진입까지 간 69건이 전부 meta·tox 등 배수에 눌려 1~2계약으로 "
            "체결됐다(qty≥3 체결 0건, 최빈 조합 meta≈0.50 × tox=0.70 ≈ 0.35). "
            "따라서 이 버킷은 **기다린다고 채워지지 않지만**, ⑧ 해제로 base_risk가 오르거나 "
            "게이트 배수가 완화되면 즉시 표본이 생긴다 — 죽은 채널이 아니라 **눌려 잠든** "
            "채널이다. CLAUDE.md ⑧이 이 채널의 누적 판정을 MAX_CONTRACTS 인하 근거로 "
            "지정하고 있으므로, 지금 판정이 필요하다면 과거 3계약+ 구간"
            "(2026-06-10~07-10) 포지션 단위 재분석을 별도 근거로 쓸 것. "
            "\n\n"
            "> **[2026-08-14 MW0602 470차 원인 갱신] 병목은 게이트 배수가 아니라 "
            "브로커 증거금 상한이다.** 431차 배포(08-05) 이후 8거래일 74포지션 전부 qty≤2, "
            "qty≥3 **0건**(마지막은 431차 이전 2026-07-31). 08-14 실측에서 사이저 산출 "
            "3계약이 진입까지 간 5건은 **5/5 전부 `[MarginCap]`으로 2계약에 잘렸다** "
            "(`main.py:15741 get_order_available_qty()` → `:15757`). 목표자본 5천만원 vs "
            "실제 모의잔고 2,972만원의 괴리가 그 상한을 만든다. "
            "**즉 이 채널은 '표본이 천천히 쌓이는 중'이 아니라 ⑧이 해제되기 전에는 "
            "켜지지 않는다** — 해제 순서는 `실전 자본 재설정 → 증거금 상한 상승 → "
            "qty≥3 발생 → 표본 축적 → 판정`이다. 부수적으로 `MAX_CONTRACTS=3`은 현재 "
            "한 번도 구속하지 않는 죽은 파라미터다(값은 타당하니 되돌리지 말 것). "
            "⚠ MarginCap이 유일 원인이라는 단정은 아직 못 한다(인과 관측 5건·1거래일)."
            % (len(recent_days), n3_recent, n3_total)
        )

    # [MW0601 471차 후속6 / G-1] 사이저 압력 실측 — 위 structural_reason이 인용하는
    # "379건 중 86건이 3계약 이상" 수치는 **417차에 TRADE 로그로 한 번 센 값**이고
    # 그 뒤로 매주 그대로 재인용돼 왔다(DB에 사이저 원본 출력이 없었기 때문).
    # 471차 후속6이 `ensemble_decisions.sizing_trace`를 만들었으므로 이제 매주
    # 실측으로 갱신한다. **판정에는 관여하지 않는다** — 합격선은 사전등록 그대로다(§9).
    out["sizer_pressure"] = _sizer_pressure_from_trace()

    if out["n_days"] < min_d:
        out["reason"] = "관측일 부족 (%d일 < %d일)" % (out["n_days"], min_d)
        return out
    if not b1 or not b3 or b1["n"] < min_n or b3["n"] < min_n:
        out["reason"] = "구간 표본 부족 (qty1=%d, qty3+=%d, 각각 %d 필요) — 판정 보류%s" % (
            (b1 or {}).get("n", 0), (b3 or {}).get("n", 0), min_n,
            " ⚠ **구조적 판정불가**" if out.get("structural_block") else "")
        return out

    out["gap_krw"] = round(b1["avg_pnl_krw"] - b3["avg_pnl_krw"], 0)
    out["verdict"] = "FAIL" if out["gap_krw"] >= gap else "PASS"
    if out["verdict"] == "FAIL":
        out["recommendation"] = (
            "계약수 역예측 확정 (qty=1 평균 %s원 vs qty≥3 평균 %s원, 격차 %s원) — "
            "MAX_CONTRACTS 인하를 주간회의에서 검토 (즉시 변경 금지, §9)" % (
                format(b1["avg_pnl_krw"], ",.0f"), format(b3["avg_pnl_krw"], ",.0f"),
                format(out["gap_krw"], ",.0f")))
    return out


def eval_mean_revert_size_watch() -> dict:
    """[29] mean-revert 레짐 사이즈 축소 감시 (MW0601 405차 / P1-3) — 사전등록.

    hurst_bucket='mean-revert' 진입의 승률·순EV가 나머지 버킷보다 유의하게 낮은지
    누적 판정한다. 상세 근거는 config.settings의 채널 주석 참조.
    **"진입 차단"이 아니라 사이즈/등급 축 처방 가설이다**(317차 FalseBlock 교훈).
    """
    cr = VALIDATION_CAMPAIGN.get("mean_revert_size_watch", {})
    min_n = int(cr.get("min_samples_per_bucket", 20))
    min_d = int(cr.get("min_days", 5))
    gap_max = float(cr.get("win_rate_gap_max", 0.15))
    out = {"verdict": "INSUFFICIENT", "entry_source_filter": cr.get("entry_source", "SYSTEM_AUTO")}

    pos = _merged_positions(extra_cols="hurst_bucket")
    if not pos:
        out["reason"] = "표본 없음"
        return out
    out["n_positions"] = len(pos)
    out["n_days"] = len({p["entry_ts"][:10] for p in pos})

    mr = [p["pnl"] for p in pos if p.get("hurst_bucket") == "mean-revert"]
    oth = [p["pnl"] for p in pos if p.get("hurst_bucket") in ("neutral", "trend")]
    out["by_bucket"] = {}
    if mr:
        out["by_bucket"]["mean_revert"] = _bucket_stats(mr)
    if oth:
        out["by_bucket"]["neutral_trend"] = _bucket_stats(oth)

    if out["n_days"] < min_d:
        out["reason"] = "관측일 부족 (%d일 < %d일)" % (out["n_days"], min_d)
        return out
    if len(mr) < min_n or len(oth) < min_n:
        out["reason"] = "버킷 표본 부족 (mean-revert=%d, 그 외=%d, 각각 %d 필요) — 판정 보류" % (
            len(mr), len(oth), min_n)
        return out

    a, b = out["by_bucket"]["mean_revert"], out["by_bucket"]["neutral_trend"]
    out["win_rate_gap"] = round(b["win_rate"] - a["win_rate"], 4)
    out["avg_gap_krw"] = round(b["avg_pnl_krw"] - a["avg_pnl_krw"], 0)
    out["verdict"] = "FAIL" if out["win_rate_gap"] >= gap_max else "PASS"
    if out["verdict"] == "FAIL":
        out["recommendation"] = (
            "mean-revert 열위 확정 (승률 %.1f%% vs %.1f%%, 격차 %.1f%%p) — 처방은 "
            "사이즈 축소가 아니라 **등급 강등/임계값 이동** 축으로 설계할 것 "
            "(qty=1에서 사이즈 축소는 no-op, sizing_prescription_axis 결정 참조)" % (
                a["win_rate"] * 100, b["win_rate"] * 100, out["win_rate_gap"] * 100))
    return out


# ══════════════════════════════════════════════════════════════
# [35]~[37] MW0602 424차 후속 — 0804 일일점검 4-2 신설 3채널
#
# 셋 다 **표본·유의성 미달 상태로 등록**됐다. 등록 자체가 조치가 아니라,
# "지금 움직이면 313차 위반"이라는 판단을 코드에 남기는 장치다.
# 근거·판독 규칙·판정 어휘는 config.settings:VALIDATION_CAMPAIGN 각 채널 주석 참조.
# ══════════════════════════════════════════════════════════════

def _fmt_krw(v) -> str:
    """부호 포함 천단위 구분 원화 문자열.

    ⚠ `%+,.0f`는 **%-포매팅에서 지원되지 않는다**(콤마 플래그는 `format()`/f-string
    전용). 실제로 이 파일에서 ValueError로 리포트 생성이 죽었다 — 같은 실수가
    반복되지 않게 헬퍼로 고정한다.
    """
    try:
        return format(int(round(float(v))), "+,d")
    except (TypeError, ValueError):
        return "—"


def _sign_test_p(k: int, n: int) -> float:
    """양측 이항 부호검정 p (귀무 p0=0.5).

    313차 일자단위 검정의 공통 도구다. 포지션 단위 z검정을 쓰지 않는 이유:
    같은 날 진입들은 같은 레짐·같은 모델 스냅샷을 공유해 **독립 관측치가 아니다**.
    372차가 PSI 재보정에서 신호단위(n=29,089) 유의성이 일자단위(n=58)로 가면
    사라지는 것을 실측했다 — 여기서도 같은 규율을 적용한다.
    """
    if n <= 0:
        return 1.0
    from math import factorial as _f
    _c = lambda a, b: _f(a) // (_f(b) * _f(a - b))
    tail = sum(_c(n, i) for i in range(0, min(k, n - k) + 1)) / float(2 ** n)
    return min(1.0, 2.0 * tail)


def _paired_day_summary(day_diffs, alpha):
    """일자별 차이값 리스트 → 짝지은 검정 요약(평균차·t·부호검정 p)."""
    n = len(day_diffs)
    out = {"paired_days": n}
    if n == 0:
        return out
    arr = np.array(day_diffs, dtype=float)
    out["mean_diff"] = round(float(arr.mean()), 4)
    out["days_positive"] = int((arr > 0).sum())
    out["sign_p"] = round(_sign_test_p(out["days_positive"], n), 4)
    if n >= 2 and float(arr.std(ddof=1)) > 0:
        out["t_stat"] = round(float(arr.mean() / (arr.std(ddof=1) / np.sqrt(n))), 3)
    out["significant"] = bool(out["sign_p"] < alpha)
    return out


def _phantom_mirror_subsample(conn, eff: str, alpha: float) -> dict:
    """[439차] [35] 미러 서브표본 — **억제된 쪽**에서 같은 Δ를 반대 방향으로 잰다.

    왜 필요한가: [35] 주판정은 `live_suppressed=0`(가드가 못 막아 유령 청산이 실제로
    난 건)만 센다. 그런데 431차 이후 그 모집단이 사라져 주판정 표본이 영구 0이 됐다
    (`eval_phantom_stop_edge` 안 `structural_reason` 참조). 같은 질문 —

        Δ = (유령 청산했을 때의 손익) − (버텼을 때의 손익),  (+)면 유령이 유리

    — 은 `live_suppressed=1`(가드가 억제해서 버틴 건)에서도 **부호만 뒤집어** 잴 수 있다.
    주판정: 실제=유령청산, 반사실=버팀.  미러: 실제=버팀, 반사실=유령청산.
    ⚠ 반환하는 `delta_pt`는 **주판정과 부호 규약이 같다**((+)=유령 유리). 미러의
    원자료에서 보면 "억제이득"의 부호가 반대라는 뜻이므로 읽을 때 주의할 것.

    반사실(관측 전 고정): 유령 청산이 났다면 **시장가**로 나가므로 판정 시점의
    `cur_price`에 체결된 것으로 본다.

    ⚠ 이 서브표본은 주판정과 **합치지 않는다**. 세 가지가 다르다 —
      ① 반사실 비대칭: 주판정의 반사실은 "`stop_eval`로 계속"이라는 단일 규칙이지만,
         미러의 실제값은 억제 이후 **모든 청산 로직**(TP2·트레일·15:10 강제청산)의
         합이라 그것들과 교락돼 있다. "억제의 순수 효과"가 아니다.
      ② 시점 교락: 두 부분표본은 처치 시점이 갈린다(유령 발생기 vs 억제기). 436차가
         `827bd04` 교락 때문에 [50]을 PRE/POST 비교로 등록하지 **않은** 것과 같은 함정.
      ③ `cur_price` 근사 편향: 실측 유령 청산의 체결 슬리피지는 평균 -2.708pt(유리)
         였으므로 `cur_price` 근사는 유령을 **과소평가**한다 — 보수적 방향이다.
    그래서 verdict를 내지 않는다. 관찰 병기이며, 판정 승격은 §9 주간회의 안건이다.
    """
    out = {"n": 0}
    rs = conn.execute(
        """SELECT ts, entry_ts, direction, entry_price, stop_eval, cur_price,
                  quantity, tighten_path
             FROM phantom_stop_shadow
            WHERE ts >= ? AND would_suppress = 1 AND live_suppressed = 1
            ORDER BY ts""", (eff,)).fetchall()
    out["n_rows_total"] = int(conn.execute(
        "SELECT COUNT(*) FROM phantom_stop_shadow WHERE ts >= ?", (eff,)).fetchone()[0])
    recs, n_multi = [], 0
    for h in rs:
        ep = float(h["entry_price"] or 0.0)
        cp = float(h["cur_price"] or 0.0)
        if ep <= 0 or cp <= 0:
            continue
        is_short = (h["direction"] == "SHORT")
        ghost_pt = (ep - cp) if is_short else (cp - ep)
        # 버틴 결과: 그 판정 이후 닫힌 **모든** 레그의 합. 주판정의 LIMIT 1과 달리
        # 합을 쓰는 이유는 억제 후 포지션이 TP1 부분청산 → TP2로 쪼개질 수 있기
        # 때문이다. 다중레그면 1계약 기준 해석이 깨지므로 건수를 따로 노출한다.
        legs = conn.execute(
            """SELECT pnl_pts FROM trades
                WHERE entry_ts = ? AND exit_ts IS NOT NULL AND exit_ts >= ?
                ORDER BY exit_ts""", (h["entry_ts"], h["ts"])).fetchall()
        if not legs:
            continue
        if len(legs) > 1:
            n_multi += 1
        held_pt = sum(float(l["pnl_pts"] or 0.0) for l in legs)
        recs.append({
            "ts": h["ts"], "direction": h["direction"],
            "tighten_path": h["tighten_path"] or "—",
            "ghost_pt": ghost_pt, "held_pt": held_pt,
            "delta_pt": ghost_pt - held_pt,   # (+)=유령 유리 — 주판정과 동일 규약
        })
    if not recs:
        return out
    days = sorted({r["ts"][:10] for r in recs})
    deltas = [r["delta_pt"] for r in recs]
    out.update({
        "n": len(recs), "n_days": len(days), "n_multi_leg": n_multi,
        "ghost_pt_sum": round(sum(r["ghost_pt"] for r in recs), 3),
        "held_pt_sum": round(sum(r["held_pt"] for r in recs), 3),
        "delta_pt_sum": round(sum(deltas), 3),
        "delta_pt_avg": round(sum(deltas) / len(deltas), 4),
        "delta_pt_median": round(float(np.median(deltas)), 4),
        "favorable_n": sum(1 for d in deltas if d > 0),
        "ghost_positive_n": sum(1 for r in recs if r["ghost_pt"] > 0),
    })
    _bp = {}
    for r in recs:
        _bp.setdefault(r["tighten_path"], []).append(r["delta_pt"])
    out["by_path"] = {k: {"n": len(v), "delta_pt_sum": round(sum(v), 3)}
                      for k, v in sorted(_bp.items())}
    day_means = [float(np.mean([r["delta_pt"] for r in recs if r["ts"][:10] == d]))
                 for d in days]
    out.update(_paired_day_summary(day_means, alpha))
    # 평균과 중앙값이 갈리면 소수 관측이 끌고 있다는 뜻이다(313차) — 판독자가
    # 평균만 보고 결론 내지 않도록 플래그로 노출한다.
    out["mean_median_split"] = bool(
        out["delta_pt_avg"] * out["delta_pt_median"] < 0)
    return out


def eval_phantom_stop_edge() -> dict:
    """[35] 유령 하드스톱은 결함인가 알파인가 (MW0602 424차 후속) — 사전등록.

    424차가 `phantom_stop_shadow`에 심은 계측을 소비한다. 대상은 **유령 청산**뿐이다
    (`would_suppress=1` & `live_suppressed=0` & `exited=1`) — 즉 "전 경로를 덮은
    가드였다면 억제했을 텐데 실제로는 청산으로 나간" 건.

    반사실(관측 전 고정): 억제했다면 포지션은 유지되고 **판정에 실제로 쓰인 스톱**
    (`stop_eval`)으로 계속 간다 → 이후 분봉에서 닿으면 그 가격, 15:10까지 안 닿으면
    그날 마지막 종가. `delta_pt = 실현 − 반사실`, (+)면 유령이 유리.

    ⚠ 판정 전에 가드를 켜면 이 표본이 더 안 쌓인다. 라이브는 계측만 하도록 배선돼
    있다(main.py `mark_stop_tightened_shadow`).

    [439차] 그런데 그 모집단이 **가드를 켜지 않았는데도** 사라졌다 — 431차의
    MAX_CONTRACTS 10→3으로 qty>=2 진입 자체가 없어졌기 때문이다. 주판정 표본이
    영구 0이 되므로 (a) 0건의 원인을 "적재 0(=🔴 배선 점검)"과 "모집단 소멸
    (=⚠구조적판정불가)"로 구분하고, (b) `_phantom_mirror_subsample()`이 억제된 쪽에서
    같은 Δ를 재도록 병기한다. **주판정의 합격선·반사실 정의·verdict 어휘는 무변경**이다.
    """
    cr = VALIDATION_CAMPAIGN.get("phantom_stop_edge", {})
    min_n = int(cr.get("min_samples", 20))
    min_d = int(cr.get("min_days", 5))
    alpha = float(cr.get("alpha", 0.05))
    eff = str(cr.get("effective_date", "2026-08-05")) + " 00:00:00"
    out = {"verdict": "INSUFFICIENT", "effective_date": cr.get("effective_date")}

    try:
        with _conn(TRADES_DB) as conn:
            ph = conn.execute(
                """SELECT ts, entry_ts, direction, entry_price, stop_eval,
                          bar_high, bar_low, cur_price, quantity, tighten_path
                     FROM phantom_stop_shadow
                    WHERE ts >= ? AND would_suppress = 1
                      AND live_suppressed = 0 AND exited = 1
                    ORDER BY ts""", (eff,)).fetchall()
            rows = []
            for h in ph:
                # 실현: 그 판정 이후 최초로 닫힌 레그 (판정 → EXIT_FULL 주문)
                leg = conn.execute(
                    """SELECT pnl_pts, exit_price, exit_reason FROM trades
                        WHERE entry_ts = ? AND exit_ts IS NOT NULL AND exit_ts >= ?
                        ORDER BY exit_ts LIMIT 1""",
                    (h["entry_ts"], h["ts"])).fetchone()
                if leg is None:
                    continue
                rows.append({
                    "ts": h["ts"], "entry_ts": h["entry_ts"],
                    "direction": h["direction"],
                    "entry_price": float(h["entry_price"] or 0.0),
                    "stop_eval": float(h["stop_eval"] or 0.0),
                    "cur_price": float(h["cur_price"] or 0.0),
                    "tighten_path": h["tighten_path"],
                    "realized_pt": float(leg["pnl_pts"] or 0.0),
                })
            out["mirror"] = _phantom_mirror_subsample(conn, eff, alpha)
    except Exception as e:
        out["error"] = str(e)
        out["no_data"] = True
        return out

    if not rows:
        # [439차] 주판정 표본 0건의 원인이 두 가지로 갈린다 — 구분하지 않으면 오진한다.
        #   ① 적재 자체가 0  → 계측 사망 의심. 🔴 빨간불이 맞다(357차).
        #   ② 적재는 되는데 `live_suppressed=0`이 0  → **모집단 소멸**. 배선은 멀쩡하다.
        # ②가 실제로 일어났다: 431차가 MAX_CONTRACTS를 10→3으로 내리고 게이트 체인을
        # 재구성하면서 qty>=2 진입이 사라졌고, 유령 청산은 사실상 그 경로에서만 났다
        # (423차 가드가 qty=1 경로에는 정상 배선돼 있다). 그래서 남은 행은 전부
        # live_suppressed=1이고 주판정 필터를 통과하는 행이 영구히 0이다.
        # → [28] sizing_inversion_watch와 같은 **구조적 판정불가**로 표기한다.
        _mir = out.get("mirror") or {}
        if _mir.get("n"):
            out["structural_block"] = True
            out["structural_reason"] = (
                "유령 청산(`live_suppressed=0`) 0건 — 그러나 적재는 정상이다"
                "(계측 시작 이후 %d행, 그중 억제 %d행 / %d거래일). 원인은 배선이 아니라 "
                "**모집단 소멸**이다: **423차 가드 배포 후** 억제되지 않고 남은 경로는 "
                "424차가 일부러 열어 둔 qty>=2의 TP1 손익분기 우회뿐인데"
                "(main.py `tp1_breakeven` — 섀도만 기록), 431차의 MAX_CONTRACTS 10→3 + "
                "게이트 체인 재구성으로 qty>=2 진입이 급감했다(08-06 0건 / 08-07 1건). "
                "남은 행은 전부 `arm_tp1_qty1_mode`(가드가 정상 배선된 경로)라 주판정 "
                "필터를 통과하는 행이 **기다린다고 생기지 않는다**. "
                "→ 아래 **미러 서브표본**(억제된 쪽)이 같은 Δ를 반대 방향에서 재는 "
                "유일한 경로다." % (_mir.get("n_rows_total", 0), _mir.get("n", 0),
                                    _mir.get("n_days", 0)))
            out["reason"] = ("유령 청산 표본 0건 — ⚠ **구조적 판정불가** "
                             "(적재 정상, 미러 %d건/%d일 병기)"
                             % (_mir.get("n", 0), _mir.get("n_days", 0)))
            return out
        out["reason"] = ("표본 없음 — `phantom_stop_shadow` 적재 대기 "
                         "(계측 시작 %s, 그 이전은 소스가 없어 소급 판정 불가)"
                         % cr.get("effective_date"))
        # `no_data`는 🔴 "계측 점검 필요"로 렌더된다(357차). **계측 시작 전에는
        # 붙이지 않는다** — 정상인데 빨간불이 켜지면 그 신호를 무시하게 되고,
        # 정작 계측이 죽었을 때 357차가 막으려던 2주 방치가 그대로 재발한다.
        if datetime.date.today().isoformat() > str(cr.get("effective_date", "")):
            out["no_data"] = True
            out["reason"] += " ⚠ 계측 시작일이 지났는데 0건 — 배선 확인 필요"
        return out

    # 반사실: stop_eval 재히트까지 보유
    try:
        with _conn(RAW_DATA_DB) as rc:
            for r in rows:
                day = r["ts"][:10]
                bars = rc.execute(
                    "SELECT ts, high, low, close FROM raw_candles "
                    "WHERE ts > ? AND ts <= ? ORDER BY ts",
                    (r["ts"], day + " 15:10:00")).fetchall()
                if not bars:
                    r["cf_pt"] = None
                    continue
                se, is_short = r["stop_eval"], (r["direction"] == "SHORT")
                cf_exit = None
                for b in bars:
                    if (is_short and float(b["high"]) >= se) or \
                       ((not is_short) and float(b["low"]) <= se):
                        cf_exit = se
                        r["cf_hit_ts"] = b["ts"]
                        break
                if cf_exit is None:
                    cf_exit = float(bars[-1]["close"])
                    r["cf_hit_ts"] = None
                r["cf_pt"] = ((r["entry_price"] - cf_exit) if is_short
                              else (cf_exit - r["entry_price"]))
    except Exception as e:
        out["error"] = "반사실 계산 실패: %s" % e
        return out

    usable = [r for r in rows if r.get("cf_pt") is not None]
    for r in usable:
        r["delta_pt"] = r["realized_pt"] - r["cf_pt"]
    out["n"] = len(usable)
    out["n_unresolved"] = len(rows) - len(usable)
    days = sorted({r["ts"][:10] for r in usable})
    out["n_days"] = len(days)
    if usable:
        out["realized_pt_sum"] = round(sum(r["realized_pt"] for r in usable), 3)
        out["cf_pt_sum"] = round(sum(r["cf_pt"] for r in usable), 3)
        out["delta_pt_sum"] = round(sum(r["delta_pt"] for r in usable), 3)
        out["delta_pt_avg"] = round(out["delta_pt_sum"] / len(usable), 4)
        out["favorable_n"] = sum(1 for r in usable if r["delta_pt"] > 0)
        _bp = {}
        for r in usable:
            _bp.setdefault(r["tighten_path"] or "—", []).append(r["delta_pt"])
        out["by_path"] = {k: {"n": len(v), "delta_pt_sum": round(sum(v), 3)}
                          for k, v in sorted(_bp.items())}
        # 일자단위(313차) — 하루 평균 delta의 부호를 센다
        day_means = [float(np.mean([r["delta_pt"] for r in usable
                                    if r["ts"][:10] == d])) for d in days]
        out.update(_paired_day_summary(day_means, alpha))

    if out["n"] < min_n or out["n_days"] < min_d:
        out["reason"] = ("표본 축적 중 — %d건 / %d거래일 (필요 %d건 / %d일). "
                         "누적 delta %+.2fpt" % (
                             out["n"], out["n_days"], min_n, min_d,
                             out.get("delta_pt_sum", 0.0)))
        return out

    if not out.get("significant"):
        out["verdict"] = "PASS"
        out["recommendation"] = (
            "유령 청산과 반사실이 통계적으로 구분되지 않는다 (일자 부호검정 p=%.4f) — "
            "손익 중립이면 **정확성이 우선**이므로 가드를 qty>=2까지 활성화하는 것이 "
            "안전하다 (main.py tp1_breakeven의 mark_stop_tightened_shadow → "
            "_mark_stop_tightened)" % out.get("sign_p", 1.0))
    elif out["delta_pt_avg"] > 0:
        out["verdict"] = "SUPPORTS_HYP"
        out["recommendation"] = (
            "유령 청산이 반사실보다 유리 (평균 %+.3fpt, %d/%d일 우세, p=%.4f) — "
            "**버그로 고치지 말 것.** \"스파이크가 스톱을 스쳤으나 현재가가 유리하면 "
            "시장가 익절\"을 명시적 청산 정책으로 승격시키는 안건(§9 주간회의)" % (
                out["delta_pt_avg"], out.get("days_positive", 0),
                out.get("paired_days", 0), out.get("sign_p", 1.0)))
    else:
        out["verdict"] = "REJECTS_HYP"
        out["recommendation"] = (
            "유령 청산이 반사실보다 열위 (평균 %+.3fpt, p=%.4f) — 가드를 qty>=2까지 "
            "활성화할 것 (main.py tp1_breakeven에서 mark_stop_tightened_shadow를 "
            "_mark_stop_tightened로 교체)" % (
                out["delta_pt_avg"], out.get("sign_p", 1.0)))
    return out


def eval_grade_x_promotion() -> dict:
    """[36] 체크리스트 승격 경로별 우열 (MW0602 424차 후속) — 사전등록.

    0803 정기점검 P2의 "앙상블 X를 A로 올리는 경로에 하한 조건 추가" 제안을
    검정한다. 0804 실측은 정반대였다(X→A 6건 5승1패 +587,344원 vs C→A 14건
    -377,207원) — 다만 X 경로는 2거래일에만 존재해 확정 불가.
    """
    cr = VALIDATION_CAMPAIGN.get("grade_x_promotion", {})
    min_n = int(cr.get("min_samples_per_bucket", 20))
    min_d = int(cr.get("min_days", 5))
    alpha = float(cr.get("alpha", 0.05))
    out = {"verdict": "INSUFFICIENT",
           "entry_source_filter": cr.get("entry_source", "SYSTEM_AUTO")}

    if not _trades_has_column("raw_grade"):
        out["no_data"] = True
        out["reason"] = "`trades.raw_grade` 컬럼 없음 — 마이그레이션 전 DB"
        return out

    pos = _merged_positions(extra_cols="raw_grade, grade")
    pos = [p for p in pos if p.get("raw_grade")]   # 구버전 행(NULL)은 경로 미상
    if not pos:
        out["no_data"] = True
        out["reason"] = "raw_grade 기록 표본 없음 (구버전 행은 경로 판별 불가)"
        return out
    out["n_positions"] = len(pos)
    out["n_days"] = len({p["entry_ts"][:10] for p in pos})

    def _sel(raw, grade):
        return [p for p in pos
                if p.get("raw_grade") == raw and p.get("grade") == grade]

    xa, ca, cc = _sel("X", "A"), _sel("C", "A"), _sel("C", "C")
    out["by_path"] = {}
    for _lab, _v in (("X→A", xa), ("C→A", ca), ("C→C", cc)):
        if _v:
            _s = _bucket_stats([p["pnl"] for p in _v])
            _s["days"] = len({p["entry_ts"][:10] for p in _v})
            out["by_path"][_lab] = _s

    # ── [MW0602 462차] C→C 대조군 분해 — "승격 효과"와 "원시등급 효과"의 분리 ──
    # 이 채널의 판정축(X→A vs C→A)은 **원시등급도 승격여부도 함께** 다르다.
    # 즉 격차가 나와도 "승격 경로가 나쁜 것"인지 "원시 C가 나쁜 것"인지 구분되지
    # 않는다. C→C(원시 C · 승격 없음)가 그 교락을 푸는 대조군이다.
    #
    #   promotion_effect = C→A − C→C   (원시등급 고정 → 순수 승격 효과)
    #   raw_grade_effect = C→C − X→A   (…의 잔차 — 원시등급 축)
    #
    # 0811 점검 실측(n=96, 07-30~08-11): C→A 계약당 EV -0.433pt vs C→C -0.438pt로
    # 사실상 동일했고 X→A만 +1.119pt였다. 승격이 성과를 바꾸지 않았다는 뜻이라,
    # 이 값이 계속 0 근방이면 처방 축을 "승격 조이기"가 아니라 **원시등급 C 취급**
    # 으로 옮겨야 한다. ⚠ 그 실측의 일자단위 검정은 3/6·순열 p=0.285로 **비유의**다.
    #
    # ⚠ **판정 게이트보다 앞에 둔다** — 이 분해는 verdict가 INSUFFICIENT인 동안에도
    #   읽을 값이다. 게이트 뒤에 두면 X→A가 min_samples(20)에 도달할 때까지
    #   영영 계산되지 않는다(462차 초안이 실제로 그 실수를 했고 리포트에
    #   promotion_effect=None으로 찍혀 발견됐다). 판정에는 일절 관여하지 않는다.
    _cc, _ca, _xa = (out["by_path"].get("C→C"), out["by_path"].get("C→A"),
                     out["by_path"].get("X→A"))
    if _cc and _ca:
        out["promotion_effect_krw"] = round(_ca["avg_pnl_krw"] - _cc["avg_pnl_krw"], 0)
        out["n_cc"] = _cc.get("n")
        if _xa:
            out["raw_grade_effect_krw"] = round(_cc["avg_pnl_krw"] - _xa["avg_pnl_krw"], 0)
            _p, _r = (abs(out["promotion_effect_krw"]),
                      abs(out["raw_grade_effect_krw"]))
            if _p + _r > 0:
                out["dominant_axis"] = "원시등급" if _r > _p else "승격경로"
                out["axis_share"] = round(max(_p, _r) / (_p + _r), 3)
    else:
        out["promotion_effect_krw"] = None   # C→C 표본 없음 — 교락 미해소
        out["raw_grade_effect_krw"] = None
        out["dominant_axis"] = None

    if out["n_days"] < min_d:
        out["reason"] = "관측일 부족 (%d일 < %d일)" % (out["n_days"], min_d)
        return out
    if len(xa) < min_n or len(ca) < min_n:
        out["reason"] = ("경로 표본 부족 (X→A=%d, C→A=%d, 각각 %d 필요) — 판정 보류. "
                         "0803 P2 \"X 승격 조이기\" 제안은 그때까지 보류다" % (
                             len(xa), len(ca), min_n))
        return out

    a, b = out["by_path"]["X→A"], out["by_path"]["C→A"]
    out["avg_gap_krw"] = round(a["avg_pnl_krw"] - b["avg_pnl_krw"], 0)
    out["win_rate_gap"] = round(a["win_rate"] - b["win_rate"], 4)
    # 일자단위 — 두 경로가 다 있는 날만
    days = sorted({p["entry_ts"][:10] for p in xa} &
                  {p["entry_ts"][:10] for p in ca})
    diffs = [float(np.mean([p["pnl"] for p in xa if p["entry_ts"][:10] == d])
                   - np.mean([p["pnl"] for p in ca if p["entry_ts"][:10] == d]))
             for d in days]
    out.update(_paired_day_summary(diffs, alpha))

    if out.get("paired_days", 0) < min_d:
        out["reason"] = ("짝지은 거래일 부족 (%d일 < %d일) — 두 경로가 같은 날 함께 "
                         "나와야 일자단위 비교가 성립한다" % (
                             out.get("paired_days", 0), min_d))
        return out
    if not out.get("significant"):
        out["verdict"] = "PASS"
        out["recommendation"] = (
            "두 승격 경로가 구분되지 않는다 (p=%.4f) — 현행 유지. 0803 P2의 "
            "\"X 승격 조이기\"는 **근거 없음으로 종결**" % out.get("sign_p", 1.0))
    elif out["mean_diff"] > 0:
        out["verdict"] = "SUPPORTS_HYP"
        out["recommendation"] = (
            "X→A가 C→A보다 우월 (일평균 격차 %s원, p=%.4f) — 0803 P2 **기각**. "
            "조일 대상이 있다면 X가 아니라 **C→A 경로**다" % (
                _fmt_krw(out["mean_diff"]), out.get("sign_p", 1.0)))
    else:
        out["verdict"] = "REJECTS_HYP"
        out["recommendation"] = (
            "X→A가 C→A보다 열위 (일평균 격차 %s원, p=%.4f) — 0803 P2 지지. "
            "앙상블 X 승격에 하한 조건 설계를 주간회의 안건으로" % (
                _fmt_krw(out["mean_diff"]), out.get("sign_p", 1.0)))
    return out


def _atr14_at(conn, ts: str, lookback: int = 60):
    """진입 시각 직전 14봉 ATR(14). 봉이 모자라면 None.

    같은 날 봉만 쓴다 — 전일 종가 대비 TR은 오버나이트 갭을 섞는데,
    절대원칙 §1(15:10 강제청산)상 이 시스템에 오버나이트 포지션은 없다.
    """
    try:
        rows = conn.execute(
            "SELECT high, low, close FROM raw_candles "
            "WHERE ts <= ? AND substr(ts,1,10) = ? ORDER BY ts DESC LIMIT ?",
            (ts, ts[:10], lookback)).fetchall()
    except Exception:
        return None
    if len(rows) < 15:
        return None
    rows = list(reversed(rows))[-15:]      # 오래된 → 최신, TR 14개 확보
    trs, prev = [], float(rows[0]["close"])
    for b in rows[1:]:
        h, l = float(b["high"]), float(b["low"])
        trs.append(max(h - l, abs(h - prev), abs(l - prev)))
        prev = float(b["close"])
    return sum(trs) / len(trs) if trs else None


def eval_profit_geometry_lowvol_watch() -> dict:
    """[51] 저변동성 국면 이익기하 붕괴 (MW0602 462차) — 사전등록.

    진입시점 ATR(14)로 저·고변동 층을 갈라, 층별 **계약당 실현손익 / ATR** 을
    비교한다. 0811 점검 §4-1의 관찰(승률은 불변인데 계약당 실현이익만 -52%,
    MFE/ATR은 -9%뿐)을 검정 가능한 형태로 등록한 것이다.

    ⚠ 그 관찰은 **일자단위 순열검정 p=0.156으로 비유의**였다(거래일 12+7일).
    그래서 지금 처방하지 않는다 — min_days=10을 둔 이유가 그것이다.
    상세 근거는 config.settings:VALIDATION_CAMPAIGN["profit_geometry_lowvol_watch"].
    """
    cr = VALIDATION_CAMPAIGN.get("profit_geometry_lowvol_watch", {})
    min_n = int(cr.get("min_samples_per_bucket", 25))
    min_d = int(cr.get("min_days", 10))
    split = float(cr.get("atr_split_pt", 2.6))
    gap_min = float(cr.get("profit_atr_ratio_gap_min", 0.25))
    alpha = float(cr.get("alpha", 0.05))
    out = {"verdict": "INSUFFICIENT",
           "entry_source_filter": cr.get("entry_source", "SYSTEM_AUTO"),
           "atr_split_pt": split}

    pos = _merged_positions(extra_cols="pnl_pts")
    if not pos:
        out["reason"] = "표본 없음"
        return out

    # 계약당 pt로 정규화 — 원화·계약수 교란 제거(417차 레그/포지션 규율과 같은 취지)
    rows = []
    try:
        with _conn(RAW_DATA_DB) as conn:
            for p in pos:
                qty = float(p.get("entry_qty") or p.get("quantity") or 1) or 1.0
                pts = p.get("pnl_pts")
                if pts is None:
                    continue
                atr = _atr14_at(conn, p["entry_ts"])
                if not atr or atr <= 0:
                    continue
                rows.append({"day": p["entry_ts"][:10], "atr": atr,
                             "ratio": (float(pts) / qty) / atr,
                             "pnl": p["pnl"]})
    except Exception as e:
        out["error"] = "%s: %s" % (type(e).__name__, e)
        return out

    if not rows:
        out["reason"] = "ATR 산출 가능한 표본 없음 (raw_candles 부족)"
        return out
    out["n_positions"] = len(rows)
    out["n_days"] = len({r["day"] for r in rows})

    lo = [r for r in rows if r["atr"] < split]
    hi = [r for r in rows if r["atr"] >= split]
    out["by_stratum"] = {}
    for lab, v in (("low_vol", lo), ("high_vol", hi)):
        if v:
            out["by_stratum"][lab] = {
                "n": len(v),
                "avg_profit_atr_ratio": round(float(np.mean([x["ratio"] for x in v])), 4),
                "avg_pnl_krw": round(float(np.mean([x["pnl"] for x in v])), 0),
                "win_rate": round(float(np.mean([1.0 if x["pnl"] > 0 else 0.0 for x in v])), 4),
                "days": len({x["day"] for x in v}),
            }

    if out["n_days"] < min_d:
        out["reason"] = "관측일 부족 (%d일 < %d일)" % (out["n_days"], min_d)
        return out
    if len(lo) < min_n or len(hi) < min_n:
        out["reason"] = ("층 표본 부족 (저변동=%d, 고변동=%d, 각각 %d 필요) — 판정 보류"
                         % (len(lo), len(hi), min_n))
        return out

    a, b = out["by_stratum"]["low_vol"], out["by_stratum"]["high_vol"]
    out["ratio_gap"] = round(b["avg_profit_atr_ratio"] - a["avg_profit_atr_ratio"], 4)
    # 일자단위 — 두 층이 같은 날 함께 나온 날만(313차: 일자가 독립관측치)
    days = sorted({r["day"] for r in lo} & {r["day"] for r in hi})
    diffs = [float(np.mean([r["ratio"] for r in hi if r["day"] == d])
                   - np.mean([r["ratio"] for r in lo if r["day"] == d]))
             for d in days]
    out.update(_paired_day_summary(diffs, alpha))

    if out.get("paired_days", 0) < min_d:
        out["reason"] = ("짝지은 거래일 부족 (%d일 < %d일) — 두 층이 같은 날 함께 "
                         "나와야 일자단위 비교가 성립한다"
                         % (out.get("paired_days", 0), min_d))
        return out
    if out.get("significant") and out["ratio_gap"] >= gap_min:
        out["verdict"] = "FAIL"
        out["recommendation"] = (
            "저변동 층에서 이익기하가 열위 (실현/ATR %.3f vs %.3f, 격차 %.3f, p=%.4f) — "
            "처방 축은 둘이다: ① 저변동 국면 TP 기하 재설계([12]/[25]와 함께 볼 것) "
            "② 저변동 국면 진입 자체를 줄이기. **어느 쪽인지는 이 채널만으로 정해지지 "
            "않는다** — 주간회의 안건으로 올릴 것" % (
                a["avg_profit_atr_ratio"], b["avg_profit_atr_ratio"],
                out["ratio_gap"], out.get("sign_p", 1.0)))
    else:
        out["verdict"] = "PASS"
        out["recommendation"] = (
            "ATR 정규화 후 두 층이 구분되지 않는다 (격차 %.3f, p=%.4f) — 0811 §4-1의 "
            "\"저변동에서 이익기하 붕괴\" 가설은 **근거 없음**. 8월 적자는 다른 축에서 "
            "찾을 것" % (out.get("ratio_gap", 0.0), out.get("sign_p", 1.0)))
    return out


def eval_effective_weight_watch() -> dict:
    """[52] 준(準)붕괴 — 유효 가중합이 0은 아니나 극단적으로 낮은 진입 (462차) — 사전등록.

    `weight_collapsed`(가중합 == 0)는 기존 weight_collapse_watch가 잡지만,
    0 < w < 0.30 구간은 어느 그물에도 걸리지 않는다. 0811 유일 진입이 정확히
    그 구간(w=0.243, 방향은 3m 단독)이었고 패했다.
    459차 F2·461차 P-A와 같은 계열 — "약한 근거"와 "강한 근거"가 같은 conf
    스케일에 섞이는 문제다. 상세는 config.settings의 채널 주석 참조.
    """
    cr = VALIDATION_CAMPAIGN.get("effective_weight_watch", {})
    min_n = int(cr.get("min_samples_per_bucket", 25))
    min_d = int(cr.get("min_days", 10))
    w_low = float(cr.get("weight_sum_low", 0.30))
    alpha = float(cr.get("alpha", 0.05))
    out = {"verdict": "INSUFFICIENT",
           "entry_source_filter": cr.get("entry_source", "SYSTEM_AUTO"),
           "weight_sum_low": w_low}

    # 진입 성사 분의 앙상블 detail에서 유효 가중합을 복원
    try:
        with _conn(PREDICTIONS_DB) as conn:
            drows = conn.execute(
                "SELECT ts, detail, weight_collapsed FROM ensemble_decisions "
                "WHERE ts >= ? AND entry_executed = 1", (_campaign_start(),)).fetchall()
    except Exception as e:
        out["error"] = "%s: %s" % (type(e).__name__, e)
        return out
    wmap = {}
    for r in drows:
        try:
            det = json.loads(r["detail"] or "{}")
            wmap[str(r["ts"])[:16]] = (
                sum(float(h.get("weight", 0) or 0) for h in det.values()),
                int(r["weight_collapsed"] or 0),
            )
        except Exception:
            continue
    if not wmap:
        out["no_data"] = True
        out["reason"] = "entry_executed=1 행에 detail 없음"
        return out

    pos = _merged_positions(extra_cols="pnl_pts")
    rows = []
    for p in pos:
        k = p["entry_ts"][:16]
        hit = wmap.get(k)
        if hit is None:                      # 결정 ts와 체결 ts가 1~2분 어긋나는 경우
            for back in (1, 2):
                try:
                    alt = (datetime.datetime.strptime(k, "%Y-%m-%d %H:%M")
                           - datetime.timedelta(minutes=back)).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    break
                hit = wmap.get(alt)
                if hit is not None:
                    break
        if hit is None:
            continue
        wsum, collapsed = hit
        if collapsed:                        # 완전붕괴는 weight_collapse_watch 관할
            continue
        qty = float(p.get("entry_qty") or p.get("quantity") or 1) or 1.0
        pts = p.get("pnl_pts")
        rows.append({"day": p["entry_ts"][:10], "wsum": wsum, "pnl": p["pnl"],
                     "ppt": (float(pts) / qty) if pts is not None else None})
    if not rows:
        out["no_data"] = True
        out["reason"] = "가중합 복원 가능한 포지션 없음"
        return out
    out["n_positions"] = len(rows)
    out["n_days"] = len({r["day"] for r in rows})

    low = [r for r in rows if r["wsum"] < w_low]
    norm = [r for r in rows if r["wsum"] >= w_low]
    out["by_bucket"] = {}
    for lab, v in (("low_weight", low), ("normal_weight", norm)):
        if v:
            s = _bucket_stats([r["pnl"] for r in v])
            s["days"] = len({r["day"] for r in v})
            s["avg_wsum"] = round(float(np.mean([r["wsum"] for r in v])), 4)
            out["by_bucket"][lab] = s

    if out["n_days"] < min_d:
        out["reason"] = "관측일 부족 (%d일 < %d일)" % (out["n_days"], min_d)
        return out
    if len(low) < min_n or len(norm) < min_n:
        out["reason"] = ("버킷 표본 부족 (저가중=%d, 정상=%d, 각각 %d 필요) — 판정 보류"
                         % (len(low), len(norm), min_n))
        return out

    a, b = out["by_bucket"]["low_weight"], out["by_bucket"]["normal_weight"]
    out["avg_gap_krw"] = round(b["avg_pnl_krw"] - a["avg_pnl_krw"], 0)
    days = sorted({r["day"] for r in low} & {r["day"] for r in norm})
    diffs = [float(np.mean([r["pnl"] for r in norm if r["day"] == d])
                   - np.mean([r["pnl"] for r in low if r["day"] == d]))
             for d in days]
    out.update(_paired_day_summary(diffs, alpha))
    if out.get("paired_days", 0) < min_d:
        out["reason"] = ("짝지은 거래일 부족 (%d일 < %d일)"
                         % (out.get("paired_days", 0), min_d))
        return out
    if out.get("significant") and out.get("mean_diff", 0) > 0:
        out["verdict"] = "FAIL"
        out["recommendation"] = (
            "유효 가중합 <%.2f 진입이 열위 (일평균 격차 %s원, p=%.4f) — WeightCollapse "
            "안전망의 문턱을 0에서 이 값 근방으로 올리는 안을 검토. ⚠ 차단이 아니라 "
            "**등급 강등/사이즈 축소** 축으로 설계할 것(317차 하드차단 교훈)" % (
                w_low, _fmt_krw(out.get("mean_diff", 0)), out.get("sign_p", 1.0)))
    else:
        out["verdict"] = "PASS"
        out["recommendation"] = (
            "준붕괴 구간이 정상 구간과 구분되지 않는다 (p=%.4f) — 현행 문턱(가중합 0) 유지"
            % out.get("sign_p", 1.0))
    return out


def eval_zone_ban_breach_watch() -> dict:
    """[53] 시간대 진입금지 존 위반 코호트 (MW0602 462차 P1-a) — 사전등록.

    `ZONE_ENTRY_BAN_ENFORCE`를 켤지 말지를 정하는 **의사결정 도구**다.
    `allow_new_entry=False`가 진입 차단에 배선된 적이 없어(462차 P1-a) 금지 존에
    진입이 성사돼 왔다 — 그 코호트가 나머지보다 열위여야 집행이 정당화된다.

    ⚠ 등록 시점 실측은 **반대 방향**이다(7포지션 +596,858원 vs 나머지 146건
    -302,986원). n=7이라 확정 불가이며, 표본이 차서도 우위가 유지되면 처방은
    "집행"이 아니라 OTHER 존 정의(11:50~13:00 공백) 재검토다.
    """
    cr = VALIDATION_CAMPAIGN.get("zone_ban_breach_watch", {})
    min_n = int(cr.get("min_samples", 20))
    min_d = int(cr.get("min_days", 10))
    alpha = float(cr.get("alpha", 0.05))
    out = {"verdict": "INSUFFICIENT",
           "entry_source_filter": cr.get("entry_source", "SYSTEM_AUTO"),
           "enforce_flag": bool(ZONE_ENTRY_BAN_ENFORCE)}

    try:
        from strategy.entry.time_strategy_router import TimeStrategyRouter, is_entry_zone
    except Exception as e:
        out["error"] = "router import 실패: %s" % e
        return out

    router = TimeStrategyRouter()
    pos = _merged_positions()
    if not pos:
        out["reason"] = "표본 없음"
        return out
    rows = []
    for p in pos:
        try:
            dt = datetime.datetime.strptime(p["entry_ts"][:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
        zone = router.get_zone(dt)
        rows.append({"day": p["entry_ts"][:10], "zone": zone,
                     "banned": (not is_entry_zone(zone)), "pnl": p["pnl"]})
    if not rows:
        out["reason"] = "존 판별 가능한 표본 없음"
        return out
    out["n_positions"] = len(rows)
    out["n_days"] = len({r["day"] for r in rows})

    breach = [r for r in rows if r["banned"]]
    allowed = [r for r in rows if not r["banned"]]
    out["by_bucket"] = {}
    for lab, v in (("banned_zone", breach), ("allowed_zone", allowed)):
        if v:
            s = _bucket_stats([r["pnl"] for r in v])
            s["days"] = len({r["day"] for r in v})
            out["by_bucket"][lab] = s
    out["breach_zones"] = sorted({r["zone"] for r in breach})

    if len(breach) < min_n:
        out["reason"] = ("위반 코호트 표본 부족 (%d건 < %d건) — 판정 보류. "
                         "표본이 찰 때까지 ZONE_ENTRY_BAN_ENFORCE는 False 유지"
                         % (len(breach), min_n))
        return out
    if out["n_days"] < min_d:
        out["reason"] = "관측일 부족 (%d일 < %d일)" % (out["n_days"], min_d)
        return out

    a, b = out["by_bucket"]["banned_zone"], out["by_bucket"]["allowed_zone"]
    out["avg_gap_krw"] = round(b["avg_pnl_krw"] - a["avg_pnl_krw"], 0)
    days = sorted({r["day"] for r in breach} & {r["day"] for r in allowed})
    diffs = [float(np.mean([r["pnl"] for r in allowed if r["day"] == d])
                   - np.mean([r["pnl"] for r in breach if r["day"] == d]))
             for d in days]
    out.update(_paired_day_summary(diffs, alpha))
    if out.get("significant") and out.get("mean_diff", 0) > 0:
        out["verdict"] = "FAIL"
        out["recommendation"] = (
            "금지 존 위반 진입이 열위 (일평균 격차 %s원, p=%.4f) — "
            "`ZONE_ENTRY_BAN_ENFORCE = True` 승격을 주간회의 안건으로" % (
                _fmt_krw(out.get("mean_diff", 0)), out.get("sign_p", 1.0)))
    else:
        out["verdict"] = "PASS"
        out["recommendation"] = (
            "위반 코호트가 열위가 아니다 (p=%.4f) — 집행하지 말 것. 처방 방향은 "
            "**OTHER 존 정의 재검토**다: TIME_ZONES에 11:50~13:00이 정의되지 않아 "
            "매일 70분이 기본 금지로 떨어지는 것이 의도인지 확인할 것" % out.get("sign_p", 1.0))
    return out


def eval_hurst_meanrevert_drag() -> dict:
    """[37] mean-revert 적자의 **일자단위** 재검정 (MW0602 424차 후속) — 사전등록.

    ⚠ **[29] mean_revert_size_watch와 모집단이 같다. 중복이 아니라 브레이크다.**
    [29]는 포지션 단위 승률 격차로 판정하는데, 0804 실측에서 두 축이 갈렸다 —
    포지션 누적 -1,455,546원인데 짝지은 7거래일 검정은 p=0.4531로 미유의.
    누적 수치만으로 조치하는 것을 막는 것이 이 채널의 존재 이유다(313차).

    판독 규칙은 관측 전에 고정돼 있다 — config.settings 채널 주석 참조.
    """
    cr = VALIDATION_CAMPAIGN.get("hurst_meanrevert_drag", {})
    min_n = int(cr.get("min_samples", 20))
    min_pd = int(cr.get("min_paired_days", 5))
    alpha = float(cr.get("alpha", 0.05))
    out = {"verdict": "INSUFFICIENT",
           "entry_source_filter": cr.get("entry_source", "SYSTEM_AUTO"),
           "shares_population_with": "[29] mean_revert_size_watch"}

    # ⚠ `_merged_positions(extra_cols=...)`를 쓰지 않는다 — 그 헬퍼는 extra_cols를
    #   **첫 레그 값**으로만 담는다(`if c not in m: m[c] = r[c]`). `pnl_pts`는
    #   부분청산으로 여러 행에 쪼개지므로 그렇게 담으면 TP1 레그 하나만 세어진다.
    #   `pnl`(원)은 헬퍼가 정확히 합산하지만, 이 채널은 **pt 단위**로 봐야 한다 —
    #   417차 교훈대로 원 단위 격차는 계약수 효과와 뒤엉킨다(A/C 등급 차이가
    #   Mann-Whitney p=0.80으로 사라졌던 것과 같은 함정).
    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                "SELECT entry_ts, hurst_bucket, "
                "       SUM(pnl_pts) AS pts, SUM(COALESCE(net_pnl_krw, pnl_krw)) AS pnl "
                "  FROM trades "
                " WHERE exit_ts IS NOT NULL AND exit_ts >= ? AND %s "
                " GROUP BY entry_ts" % _SYSTEM_AUTO_SQL,
                (_campaign_start(),)).fetchall()
        pos = [{"entry_ts": r["entry_ts"], "hurst_bucket": r["hurst_bucket"],
                "pnl_pts": float(r["pts"] or 0.0), "pnl": float(r["pnl"] or 0.0)}
               for r in rows]
    except Exception as e:
        out["error"] = str(e)
        out["no_data"] = True
        return out
    if not pos:
        out["no_data"] = True
        out["reason"] = "표본 없음"
        return out
    out["n_positions"] = len(pos)
    out["n_days"] = len({p["entry_ts"][:10] for p in pos})

    mr = [p for p in pos if p.get("hurst_bucket") == "mean-revert"]
    oth = [p for p in pos if p.get("hurst_bucket") in ("neutral", "trend")]
    out["n_mean_revert"] = len(mr)
    out["n_other"] = len(oth)
    out["cum_krw"] = {
        "mean_revert": round(sum(p["pnl"] for p in mr), 0),
        "other": round(sum(p["pnl"] for p in oth), 0),
    }

    # 일자단위 — 양쪽 버킷이 **모두 있는** 날만이 실질 표본이다.
    # [33] faststop_rerun_watch가 "유효 거래일"을 병목으로 지목한 것과 같은 사정:
    # 한쪽만 있는 날은 그날의 레짐·변동성을 통제하지 못해 비교가 성립하지 않는다.
    days = sorted({p["entry_ts"][:10] for p in mr} &
                  {p["entry_ts"][:10] for p in oth})
    diffs = [float(np.mean([p["pnl_pts"] for p in mr if p["entry_ts"][:10] == d])
                   - np.mean([p["pnl_pts"] for p in oth if p["entry_ts"][:10] == d]))
             for d in days]
    out.update(_paired_day_summary(diffs, alpha))
    out["unpaired_days"] = out["n_days"] - out.get("paired_days", 0)

    if len(mr) < min_n:
        out["reason"] = "mean-revert 표본 부족 (%d < %d)" % (len(mr), min_n)
        return out
    if out.get("paired_days", 0) < min_pd:
        out["reason"] = ("짝지은 거래일 부족 (%d일 < %d일, 단일버킷일 %d일 제외) — "
                         "누적 %s원은 **판정 근거가 아니다**" % (
                             out.get("paired_days", 0), min_pd,
                             out.get("unpaired_days", 0),
                             _fmt_krw(out["cum_krw"]["mean_revert"])))
        return out

    if out.get("significant") and out.get("mean_diff", 0) < 0:
        out["verdict"] = "SUPPORTS_HYP"
        out["recommendation"] = (
            "mean-revert 열위가 일자단위로도 유의 (평균차 %+.2fpt, %d/%d일, p=%.4f) — "
            "[29]와 두 축 합치. 처방은 사이즈 축소가 아니라 **등급 강등/임계값 이동** "
            "축으로 설계할 것(qty=1에서 사이즈 축소는 no-op)" % (
                out["mean_diff"], out.get("days_positive", 0),
                out.get("paired_days", 0), out.get("sign_p", 1.0)))
    else:
        out["verdict"] = "PASS"
        out["recommendation"] = (
            "일자단위로는 유의하지 않다 (평균차 %+.2fpt, p=%.4f) — 누적 %s원이 "
            "커 보여도 **조치 금지**. [29]가 FAIL을 내더라도 이 채널이 PASS인 동안은 "
            "보류가 사전등록된 판독 규칙이다" % (
                out.get("mean_diff", 0.0), out.get("sign_p", 1.0),
                _fmt_krw(out["cum_krw"]["mean_revert"])))
    return out


# ══════════════════════════════════════════════════════════════
# [42] 타점의 가치 · [43] 변동성 추정량 (MW0602 429차)
# ══════════════════════════════════════════════════════════════

def eval_entry_timing_value_watch() -> dict:
    """[42] 타점(진입 시각)의 가치 (MW0602 429차) — 사전등록.

    [40]이 방향 축만 격리했다면 여기는 **타점 축**이다. `B − C`가 체크리스트/
    게이트가 고른 분(minute)의 기여분이다. 상세는 settings 채널 주석 참조.
    """
    cr = VALIDATION_CAMPAIGN.get("entry_timing_value_watch", {})
    out = {"verdict": "INSUFFICIENT"}
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from random_entry_control import run_three_arm
    except Exception as e:
        out["error"] = "random_entry_control 로드 실패: %s" % e
        out["no_data"] = True
        return out
    try:
        res = run_three_arm(_campaign_start(), int(cr.get("trials", 400)),
                            int(cr.get("seed", 429)),
                            tuple(cr.get("entry_window", ("09:05", "14:49"))))
    except Exception as e:
        out["error"] = "시뮬 실패: %s" % e
        out["no_data"] = True
        return out
    out.update(res)
    if res.get("error"):
        out["no_data"] = True
        return out

    if (res.get("n_usable", 0) < int(cr.get("min_entries", 40))
            or res.get("n_days", 0) < int(cr.get("min_days", 6))):
        out["reason"] = ("표본 부족 — 진입 %s건 / %s거래일 (필요 %s / %s)"
                         % (res.get("n_usable"), res.get("n_days"),
                            cr.get("min_entries"), cr.get("min_days")))
        return out

    _sig = float(res.get("sign_p", 1.0)) < float(cr.get("alpha", 0.05))
    if _sig and float(res.get("timing_gain_pt", 0.0)) > 0:
        out["verdict"] = "SUPPORTS_HYP"
        out["recommendation"] = (
            "**타점 선택에 가치가 있다** (기여 %+.2fpt, B>C %.1f%%, p=%.4f) — "
            "체크리스트/게이트가 고른 분이 무작위보다 낫다. 진입 축 개선의 "
            "근거가 생겼고, 그 위에 변동성·미시구조 피처를 얹는 것이 정당해진다"
            % (res.get("timing_gain_pt"), float(res.get("b_over_c_share", 0)) * 100,
               res.get("sign_p")))
    elif _sig:
        out["verdict"] = "REJECTS_HYP"
        out["recommendation"] = (
            "**타점 선택이 오히려 열위다** (기여 %+.2fpt, p=%.4f) — 체크리스트가 "
            "고르는 분이 무작위보다 나쁘다는 뜻이므로 원인 조사가 필요하다"
            % (res.get("timing_gain_pt"), res.get("sign_p")))
    else:
        out["verdict"] = "REJECTS_HYP"
        out["recommendation"] = (
            "타점 선택이 무작위와 구분되지 않는다 (기여 %+.2fpt, B>C %.1f%%, p=%.4f). "
            "**체크리스트가 가치를 더한다는 전제 위에 새 피처를 얹지 말 것** — "
            "가치가 검증되지 않은 필터에 검증되지 않은 피처를 더하는 일이 된다. "
            "[40]과 함께 읽으면 진입 축(방향·타점)이 **둘 다** 무작위와 구분되지 "
            "않는다는 뜻이다"
            % (res.get("timing_gain_pt"), float(res.get("b_over_c_share", 0)) * 100,
               res.get("sign_p")))
    return out


def eval_vol_estimator_watch() -> dict:
    """[43] 변동성 추정량 교체 가치 (MW0602 429차) — 사전등록.

    **사이저는 이미 ATR로 변동성 스케일링을 한다.** 그러니 질문은 "변동성을
    넣자"가 아니라 "분위 불확실성(선행 예측)이 ATR(후행 실현) 위에 **추가 정보**를
    갖는가"다. 판정은 **ATR 통제 후 부분상관**으로 한다.
    """
    cr = VALIDATION_CAMPAIGN.get("vol_estimator_watch", {})
    out = {"verdict": "INSUFFICIENT"}
    win = int(cr.get("horizon_min", 30))
    try:
        with _conn(PREDICTIONS_DB) as conn:
            rows = conn.execute(
                "SELECT ts, quantile_uncertainty_pt AS u, features "
                "  FROM ensemble_decisions "
                " WHERE ts >= ? AND entry_executed = 1 "
                "   AND quantile_uncertainty_pt IS NOT NULL", (_campaign_start(),)
            ).fetchall()
        with _conn(RAW_DATA_DB) as conn:
            bars = {}
            for r in conn.execute(
                    "SELECT ts, high, low FROM raw_candles WHERE ts >= ?",
                    (_campaign_start(),)):
                bars.setdefault(str(r["ts"])[:10], []).append(
                    (str(r["ts"]), float(r["high"]), float(r["low"])))
        for d in bars:
            bars[d].sort()
    except Exception as e:
        out["error"] = str(e)
        out["no_data"] = True
        return out

    A, U, R, D = [], [], [], []
    for r in rows:
        try:
            atr = float((json.loads(r["features"]) or {}).get("atr") or 0.0)
        except (ValueError, TypeError):
            atr = 0.0
        if atr <= 0:
            continue
        ts = str(r["ts"])
        end = (datetime.datetime.strptime(ts, _TS_FMT)
               + datetime.timedelta(minutes=win)).strftime(_TS_FMT)
        fut = [b for b in bars.get(ts[:10], ()) if ts < b[0] <= end]
        if len(fut) < 5:
            continue
        A.append(atr * ATR_STOP_MULT)
        U.append(float(r["u"]))
        R.append(max(b[1] for b in fut) - min(b[2] for b in fut))
        D.append(ts[:10])

    out["n"] = len(A)
    out["n_days"] = len(set(D))
    if out["n"] < int(cr.get("min_samples", 40)) or out["n_days"] < int(cr.get("min_days", 6)):
        out["reason"] = ("표본 부족 — %d건 / %d거래일 (필요 %s / %s). "
                         "`quantile_uncertainty_pt`가 있는 진입만 대상이다"
                         % (out["n"], out["n_days"],
                            cr.get("min_samples"), cr.get("min_days")))
        return out

    _A, _U, _R = np.array(A), np.array(U), np.array(R)
    out["corr_atr_realized"] = round(float(np.corrcoef(_A, _R)[0, 1]), 4)
    out["corr_qunc_realized"] = round(float(np.corrcoef(_U, _R)[0, 1]), 4)
    out["collinearity"] = round(float(np.corrcoef(_A, _U)[0, 1]), 4)
    # ATR을 통제한 뒤 잔차끼리의 상관 = 증분정보
    _bR = np.polyfit(_A, _R, 1)
    _bU = np.polyfit(_A, _U, 1)
    resR = _R - np.polyval(_bR, _A)
    resU = _U - np.polyval(_bU, _A)
    rp = float(np.corrcoef(resU, resR)[0, 1])
    out["partial_corr"] = round(rp, 4)
    n = out["n"]
    out["partial_t"] = round(
        rp * np.sqrt((n - 3) / max(1e-12, 1 - rp ** 2)), 3) if n > 3 else None

    # qty 경계 통과 — 상관이 높아도 클램프 때문에 계약수가 갈릴 수 있다.
    if cr.get("report_qty_boundary"):
        try:
            # ⚠ MINI_FUTURES_PT_VALUE는 config.constants에 있다(settings 아님).
            #   초판이 settings에서 import해 ImportError로 조용히 건너뛰었다.
            # [2026-08-06] 기준자본 판정을 config/capital.py 단일 출처로 이관.
            # 오프라인 재생이라 실제 잔고가 없으므로 balance=0 을 넘긴다 —
            # ENABLED=True 면 목표자본, False 면 0(= base_risk 0, 아래 분모 가드로
            # 경계 계산이 자동 생략)이 되어 구 동작과 동일하다.
            from config.capital import base_risk_krw
            from config.constants import MINI_FUTURES_PT_VALUE
            _base = base_risk_krw(0.0)
            # 전역 정규화 계수 — 수준 차이가 효과로 오인되지 않게 중앙값을 맞춘다.
            k = float(np.median(_A) / np.median(_U)) if np.median(_U) > 0 else 1.0
            out["norm_k"] = round(k, 4)
            cross = 0
            for i in range(n):
                q_atr = int(_base / max(1e-9, _A[i] * MINI_FUTURES_PT_VALUE))
                q_unc = int(_base / max(1e-9, _U[i] * k * MINI_FUTURES_PT_VALUE))
                if q_atr != q_unc:
                    cross += 1
            out["qty_boundary_cross"] = cross
            out["qty_boundary_share"] = round(cross / float(n), 4)
        except Exception as e:
            out["qty_boundary_error"] = str(e)

    _min_t = float(cr.get("min_partial_t", 2.0))
    if abs(out.get("partial_t") or 0.0) >= _min_t:
        out["verdict"] = "SUPPORTS_HYP"
        out["recommendation"] = (
            "분위 불확실성이 ATR 위에 **추가 정보를 갖는다** (부분상관 %+.4f, "
            "t=%+.2f) — 사이징 섀도 착수를 주간회의 안건으로. 다만 교체가 아니라 "
            "**잔차를 더하는 형태**로 설계할 것(두 추정량 상관 %.3f)"
            % (out["partial_corr"], out["partial_t"], out["collinearity"]))
    else:
        out["verdict"] = "REJECTS_HYP"
        _qb = out.get("qty_boundary_share")
        _qb_txt = ""
        if _qb is not None:
            # ⚠ "아무것도 안 바뀐다"가 아니다 — 이산화 때문에 많이 바뀌는데
            #    그 변화에 정보가 없다. 그건 무해가 아니라 **유해**다.
            _qb_txt = (" 그리고 교체하면 **아무것도 안 바뀌는 것이 아니라** "
                       "`int()` 절단 때문에 계약수가 **%.0f%%(%s/%s건)에서 갈린다** — "
                       "근거 없는 사이즈 변동을 그만큼 주입한다는 뜻이라 무해가 아니라 "
                       "유해다(CLAUDE.md ⑧·425차의 qty 1↔2 경계 참조)."
                       % (float(_qb) * 100, out.get("qty_boundary_cross"), out.get("n")))
        out["recommendation"] = (
            "ATR 위에 추가 정보가 없다 (부분상관 %+.4f, t=%+.2f < %.1f, 공선성 %.3f). "
            "**사이징 추정량 교체는 무의미하다** — 사이저는 이미 ATR로 변동성 "
            "스케일링을 하고 있고(`stop_risk = atr × %.1f × pt_value`), ATR 자체가 "
            "실현 레인지와 r=%+.3f로 이미 좋은 예측자다.%s"
            % (out["partial_corr"], out["partial_t"] or 0.0, _min_t,
               out["collinearity"], ATR_STOP_MULT, out["corr_atr_realized"], _qb_txt))
    return out


# ══════════════════════════════════════════════════════════════
# [44] DynMC 붕괴행 잠식 · [45] 축퇴 가드 플래핑 (MW0602 430차)
# ══════════════════════════════════════════════════════════════

def _load_conf_rows(start_date: str) -> list:
    """[430차 공통] ensemble_decisions에서 conf 축 원자료를 읽는다.

    두 채널([44]·[45])이 같은 표를 쓰므로 한 번만 읽는다. `confidence_raw`는
    2026-07-29부터 기록되므로 그 이전 구간은 보정 적용여부를 판정할 수 없다 —
    두 채널 모두 `start_date`가 07-31이라 문제되지 않지만, 호출부가 앞당기면
    `raw`가 None인 행이 섞이므로 소비처에서 걸러야 한다.

    Returns: [(date, ts, conf, raw, collapsed)] — raw는 None일 수 있다.
    """
    try:
        with _conn(PREDICTIONS_DB) as conn:
            rows = conn.execute(
                "SELECT substr(ts,1,10) AS d, ts, confidence AS c, "
                "       confidence_raw AS r, COALESCE(weight_collapsed,0) AS wc "
                "  FROM ensemble_decisions "
                " WHERE ts >= ? AND confidence IS NOT NULL "
                " ORDER BY ts", (start_date + " 00:00:00",)).fetchall()
    except Exception:
        return []
    return [(r["d"], r["ts"], float(r["c"]),
             (float(r["r"]) if r["r"] is not None else None), int(r["wc"]))
            for r in rows]


def _entry_collapse_lift(start_date: str) -> dict:
    """[44] 보조지표 (MW0602 436차) — 붕괴행이 **실제 진입까지 갔는가**.

    왜 별도 로더인가: `_load_conf_rows`는 [45]와 공유하는 5-튜플이라 원소를 추가하면
    양쪽의 언팩(`for d, _, c, _, wc in rows`)이 전부 깨진다. 이 지표는 [44]에서만
    쓰므로 독립 쿼리로 분리한다(회귀 위험 0).

    무엇을 재는가:
        lift = P(붕괴 | 진입) / P(붕괴 | 전체)
        lift ≈ 1  → 붕괴행이 진입에 비례해 들어간다
        lift ≪ 1  → 붕괴행은 하류 게이트에서 이미 걸러진다
        lift ≫ 1  → 붕괴행이 진입을 만들고 있다 (430차가 우려한 방향)

    왜 필요한가 — 430차 §5는 "붕괴행이 분포 최상단을 점유해 **진입 예산을 잠식**"한다고
    했다. 그 서술은 base_mc 축에서는 맞지만, "그래서 붕괴행이 실제로 진입하는가"는
    한 번도 측정된 적이 없었다. 0806(436차) 실측은 **반대**였다:
        08-03~08-06 진입 72건 중 붕괴행 **1건(1.4%)**, 전체 붕괴율 21.2% → **lift 0.07**
    즉 붕괴행은 하류에서 강하게 배제되고 있다. 이 관측이 맞다면 붕괴행을 피드에서
    빼는 조치(22.6%→35.2%)는 "판단 불가 행에게 진입을 준다"가 아니라 "정상 행의
    통과율을 복원한다"로 읽어야 한다 — 판정 시 해석이 달라지는 지점이다.

    ⚠ 이것은 **판정이 아니라 관측 기록**이다. 430차 §7이 08-11 이전 수치로 판정하지
      말라고 못박았고 [44]의 min_days=10이 그 방어선이다. 이 값도 같은 창을 따른다.

    함께 싣는 진입률(entry_rate)의 이유: 430차 §5는 진입 급증이 base_mc 수렴과 함께
    **자기소멸**한다고 투영했다(~08-11). 0806 실측은 base_mc가 투영대로 올랐는데
    (0.3971→0.4151, 투영 0.418) 진입률은 되돌지 않고 **신고점(6.2%)**이었다. 게이트
    수렴과 진입률을 **같은 표에서** 봐야 그 괴리가 판정 때 눈에 띈다.
    """
    out = {}
    try:
        with _conn(PREDICTIONS_DB) as conn:
            rows = conn.execute(
                "SELECT substr(ts,1,10) AS d, "
                "       COALESCE(weight_collapsed,0) AS wc, "
                "       COALESCE(entry_executed,0)   AS ex "
                "  FROM ensemble_decisions "
                " WHERE ts >= ? AND confidence IS NOT NULL",
                (start_date + " 00:00:00",)).fetchall()
    except Exception as e:
        return {"error": str(e)}
    if not rows:
        return {}
    n = len(rows)
    n_col = sum(1 for r in rows if int(r["wc"]))
    n_ex = sum(1 for r in rows if int(r["ex"]))
    n_ex_col = sum(1 for r in rows if int(r["ex"]) and int(r["wc"]))
    out["n_rows"] = n
    out["n_entries"] = n_ex
    out["entry_rate"] = round(n_ex / float(n), 4)
    out["collapsed_share"] = round(n_col / float(n), 4)
    out["entry_collapsed_n"] = n_ex_col
    if n_ex and n_col:
        out["entry_collapsed_share"] = round(n_ex_col / float(n_ex), 4)
        out["lift"] = round((n_ex_col / float(n_ex)) / (n_col / float(n)), 3)
    # 일자단위 진입률 — 430차 §5의 "자기소멸" 투영이 실제로 일어나는지 추적
    byday = {}
    for r in rows:
        d = r["d"]
        a = byday.setdefault(d, [0, 0])
        a[0] += 1
        a[1] += int(r["ex"])
    out["by_day"] = [{"date": d, "n": v[0], "entries": v[1],
                      "entry_rate": round(v[1] / float(v[0]), 4)}
                     for d, v in sorted(byday.items())]
    return out


def _base_mc_from(confs: list) -> float:
    """DynMC의 base_mc 산출을 그대로 재현.

    `strategy/entry/time_strategy_router.update_dynamic_mc()`와 **같은 식**이어야
    한다 — 다르면 이 채널이 재는 것이 라이브와 무관해진다. 그래서 인덱스 계산까지
    복제한다(`min(int(n*MC_PERCENTILE), n-1)`). STEP_LIMIT 클램프는 재현하지
    않는다: 그것은 수렴 속도만 늦추는 과도항이고, 이 채널이 묻는 것은 **수렴점**이다.
    """
    if not confs:
        return float("nan")
    s = sorted(confs)
    p = s[min(int(len(s) * MC_PERCENTILE), len(s) - 1)]
    return max(MC_ABS_FLOOR, min(MC_ABS_CEIL, p))


def eval_dynmc_collapse_feed_watch() -> dict:
    """[44] 붕괴행이 DynMC 진입 예산을 잠식하는가 (MW0602 430차) — 사전등록.

    `weight_collapsed=1`은 **실질 가중합 0 = 판단 불가**다. 그런데 07-31 보정
    미적용 전환 이후 이 행들의 conf가 0.85(클리핑 상한)로 나가 분포 최상단을
    점유하고, DynMC가 그 분포의 p65를 min_conf로 쓰기 때문에 **정상 신호 행의
    통과율이 설계 의도(1-p65≈35%)보다 낮아진다.**

    판정은 "현행 피드 vs 붕괴행 제외 피드" 두 base_mc를 각각 계산하고, **같은
    비붕괴 행 집합**에 적용해 통과율 차이를 본다 — 분모를 고정해야 base_mc
    이동분만 분리된다.

    상세 근거·임계 유도는 config.settings의 채널 주석 참조.
    """
    cr = VALIDATION_CAMPAIGN.get("dynmc_collapse_feed_watch", {}) or {}
    start = str(cr.get("start_date", "2026-07-31"))
    out = {"verdict": "INSUFFICIENT", "start_date": start}

    rows = [x for x in _load_conf_rows(start)]
    if not rows:
        out["no_data"] = True
        out["reason"] = "표본 없음 (%s 이후 ensemble_decisions 행 없음)" % start
        return out

    days = sorted({d for d, _, _, _, _ in rows})
    out["n_rows"] = len(rows)
    out["n_days"] = len(days)
    n_col = sum(1 for _, _, _, _, wc in rows if wc)
    out["n_collapsed"] = n_col
    out["collapsed_share"] = round(n_col / float(len(rows)), 4)

    all_conf = [c for _, _, c, _, _ in rows]
    non_conf = [c for _, _, c, _, wc in rows if not wc]
    out["n_non_collapsed"] = len(non_conf)
    if not non_conf:
        out["reason"] = "비붕괴 행이 없어 통과율을 낼 수 없다"
        return out

    mc_cur = _base_mc_from(all_conf)          # 현행 — 붕괴행 포함
    mc_alt = _base_mc_from(non_conf)          # 대안 — 붕괴행 제외
    out["base_mc_current"] = round(mc_cur, 4)
    out["base_mc_excl_collapsed"] = round(mc_alt, 4)
    out["base_mc_shift"] = round(mc_cur - mc_alt, 4)

    # 분모 고정 — 둘 다 **비붕괴 행**에만 적용한다.
    pass_cur = sum(1 for c in non_conf if c >= mc_cur) / float(len(non_conf))
    pass_alt = sum(1 for c in non_conf if c >= mc_alt) / float(len(non_conf))
    design = 1.0 - float(MC_PERCENTILE)
    out["pass_rate_current"] = round(pass_cur, 4)
    out["pass_rate_excl_collapsed"] = round(pass_alt, 4)
    out["pass_rate_design"] = round(design, 4)
    out["gap_pp"] = round((design - pass_cur) * 100.0, 2)

    # ── ConstOut 필터 여유폭 — main.py:_recalibrate_mc의 15% 임계에 얼마나 붙었나 ──
    # 넘으면 그 값이 통째로 제외돼 base_mc가 불연속으로 튄다. 그 순간을 놓치면
    # "왜 갑자기 min_conf가 내려갔지"를 사후에 설명할 수 없다.
    _freq = {}
    for c in all_conf:
        k = round(c, 2)
        _freq[k] = _freq.get(k, 0) + 1
    if _freq:
        _top_v, _top_n = max(_freq.items(), key=lambda kv: kv[1])
        out["top_conf_value"] = _top_v
        out["top_conf_share"] = round(_top_n / float(len(all_conf)), 4)
        _thr = float(cr.get("constout_threshold", 0.15))
        out["constout_threshold"] = _thr
        out["constout_margin_pp"] = round((_thr - out["top_conf_share"]) * 100.0, 2)
        out["constout_would_fire"] = bool(out["top_conf_share"] > _thr)

    # ── 일자단위(313차) — 붕괴율이 높은 하루가 통째로 만드는 것을 막는다 ──
    _byday = {}
    for d, _, c, _, wc in rows:
        _byday.setdefault(d, []).append((c, wc))
    day_gaps, day_rows = [], []
    for d in days:
        v = _byday[d]
        _a = [c for c, _ in v]
        _n = [c for c, wc in v if not wc]
        if not _n:
            continue
        _mc_c, _mc_a = _base_mc_from(_a), _base_mc_from(_n)
        _pc = sum(1 for c in _n if c >= _mc_c) / float(len(_n))
        _pa = sum(1 for c in _n if c >= _mc_a) / float(len(_n))
        day_gaps.append((_pa - _pc) * 100.0)
        day_rows.append({
            "date": d, "n": len(v),
            "collapsed_share": round(sum(1 for _, wc in v if wc) / float(len(v)), 4),
            "base_mc_current": round(_mc_c, 4), "base_mc_excl": round(_mc_a, 4),
            "pass_current": round(_pc, 4), "pass_excl": round(_pa, 4),
        })
    out["by_day"] = day_rows
    out["stratified"] = _paired_day_summary(day_gaps, float(cr.get("alpha", 0.05)))
    # [436차] 보조지표 — 붕괴행이 실제 진입까지 갔는가 + 진입률 추이(자기소멸 검증).
    # 판정에는 관여하지 않는다(verdict 산식 무변경) — 해석용 병기다.
    out["entry_lift"] = _entry_collapse_lift(start)

    # ── 판정 ─────────────────────────────────────────────────
    _min_d, _min_r = int(cr.get("min_days", 10)), int(cr.get("min_rows", 2000))
    if out["n_days"] < _min_d or out["n_rows"] < _min_r:
        out["reason"] = (
            "표본 부족 — %d거래일(필요 %d) / %d행(필요 %d). "
            "⚠ base_mc는 10일 롤링이라 07-31 전환분이 다 채워지기 전 수치로 "
            "판정하면 과도구간을 정상으로 오인한다."
            % (out["n_days"], _min_d, out["n_rows"], _min_r))
        return out

    _gap_min = float(cr.get("pass_rate_gap_min_pp", 5.0))
    _share_min = float(cr.get("min_day_share", 0.70))
    _st = out["stratified"] or {}
    _day_share = ((_st.get("days_positive", 0) / float(_st["paired_days"]))
                  if _st.get("paired_days") else 0.0)
    out["day_share"] = round(_day_share, 4)
    _eff_ok = out["gap_pp"] >= _gap_min
    _day_ok = _day_share >= _share_min
    if _eff_ok and _day_ok:
        out["verdict"] = "SUPPORTS_HYP"
        out["reason"] = (
            "설계 통과율 %.1f%% 대비 현행 %.1f%% — **이탈 %.2f%%p**(임계 %.1f), "
            "일자단위 %d/%d일(%.0f%%). 붕괴행 %.1f%%가 분포 상단을 점유해 base_mc를 "
            "%.4f→%.4f로 밀어올린다."
            % (design * 100, pass_cur * 100, out["gap_pp"], _gap_min,
               _st.get("days_positive", 0), _st.get("paired_days", 0),
               _day_share * 100, out["collapsed_share"] * 100, mc_alt, mc_cur))
        out["recommendation"] = (
            "DynMC 피드에서 `weight_collapsed=1` 행 제외를 **주간회의 안건으로** 올릴 것. "
            "⚠ 자동 배선 금지 — 제외하면 진입이 %.1f%%→%.1f%%로 늘고, 427차 [39]가 "
            "확정한 대로 min_conf는 무작위 샘플러이므로 **기대값의 부호가 보장되지 "
            "않는다.** CLAUDE.md ⑧(사이징·MAX_CONTRACTS) 미해제 상태에서는 진입 증가가 "
            "곧 노출 증가다."
            % (pass_cur * 100, pass_alt * 100))
    else:
        out["verdict"] = "REJECTS_HYP"
        out["reason"] = (
            "이탈 %.2f%%p(임계 %.1f, %s) · 일자단위 %.0f%%(임계 %.0f%%, %s) — "
            "현행 피드 유지."
            % (out["gap_pp"], _gap_min, "통과" if _eff_ok else "미달",
               _day_share * 100, _share_min * 100, "통과" if _day_ok else "미달"))
    return out


def eval_cal_guard_flap_watch() -> dict:
    """[45] 축퇴 가드 플래핑 게이지 (MW0602 430차) — 사전등록.

    **게이지다. 판정하지 않는다**(verdict=OBSERVE 고정) — [33]·[41]과 같은 부류.

    보정 적용/미적용은 DB에 직접 기록되지 않으므로 **행 단위로 복원**한다:
    `confidence == min(confidence_raw, 0.85)` 이면 미적용(raw 통과)이다.
    `calibrate()`가 미적합 시 raw를 그대로 돌려주고([calibration.py]), 적용
    경로는 Platt 출력이라 raw와 우연히 일치할 확률이 사실상 0이기 때문이다.

    ⚠ 허용오차 6e-4는 **DB 저장이 round(x,4)이기 때문**이다(424차가 float32
    허용오차로 같은 함정을 밟았다). 더 좁히면 반올림만으로 오분류가 생긴다.
    """
    cr = VALIDATION_CAMPAIGN.get("cal_guard_flap_watch", {}) or {}
    start = str(cr.get("start_date", "2026-07-31"))
    out = {"verdict": "OBSERVE", "start_date": start}

    rows = [x for x in _load_conf_rows(start) if x[3] is not None]
    if not rows:
        out["no_data"] = True
        out["reason"] = ("표본 없음 — `confidence_raw`는 2026-07-29부터 기록된다")
        return out

    _TOL = 6e-4          # round(x,4) 저장 오차의 여유분
    _CLIP = 0.85         # ensemble_decision.py의 보정 출력 클리핑 상한

    by_day, jumps, flips_by_day = {}, [], {}
    for d, ts, c, r, wc in rows:
        passthru = abs(c - min(r, _CLIP)) < _TOL
        by_day.setdefault(d, []).append((ts, passthru, c))

    n_pass = 0
    day_rows = []
    for d in sorted(by_day):
        seq = by_day[d]
        _p = sum(1 for _, p, _ in seq if p)
        n_pass += _p
        flips = 0
        for i in range(1, len(seq)):
            if seq[i][1] != seq[i - 1][1]:
                flips += 1
                jumps.append(abs(seq[i][2] - seq[i - 1][2]))
        flips_by_day[d] = flips
        day_rows.append({
            "date": d, "n": len(seq),
            "passthru_share": round(_p / float(len(seq)), 4),
            "flips": flips,
        })
    out["by_day"] = day_rows
    out["n_rows"] = len(rows)
    out["n_days"] = len(by_day)
    out["passthru_share"] = round(n_pass / float(len(rows)), 4)
    out["flips_total"] = int(sum(flips_by_day.values()))
    out["flips_per_day"] = round(out["flips_total"] / float(len(by_day)), 2)
    if jumps:
        out["conf_jump_median"] = round(float(np.median(jumps)), 4)
        out["conf_jump_max"] = round(float(np.max(jumps)), 4)

    _min_d = int(cr.get("min_days", 6))
    if out["n_days"] < _min_d:
        out["reason"] = "표본 %d거래일 (게이지 표시 하한 %d일)" % (out["n_days"], _min_d)
        return out

    _fw = float(cr.get("flip_per_day_warn", 4.0))
    _jw = float(cr.get("conf_jump_warn", 0.10))
    out["flap_warn"] = bool(out["flips_per_day"] >= _fw)
    out["jump_warn"] = bool((out.get("conf_jump_median") or 0.0) >= _jw)
    out["reason"] = (
        "보정 미적용 %.1f%% · 전환 %.2f회/일(경보 %.1f) · 전환 시 conf 점프 중앙값 "
        "%s(경보 %.2f)"
        % (out["passthru_share"] * 100, out["flips_per_day"], _fw,
           out.get("conf_jump_median", "—"), _jw))
    if out["flap_warn"] or out["jump_warn"]:
        out["recommendation"] = (
            "히스테리시스(또는 EOD 1회 고정) 도입을 주간회의 안건으로. "
            "⚠ **AUC 임계·보정 함수형은 건드리지 말 것** — 근본 문제는 임계가 아니라 "
            "정보 부재이고(raw conf 순위 AUC 0.489 < 0.5, 427차 [39]와 일치), "
            "임계를 손대면 conf 스케일에 세 번째 불연속이 생긴다."
        )
    return out


# ══════════════════════════════════════════════════════════════
# [41] 청산 측 학습기 게이지 (MW0602 428차) — 판정 채널 아님
# ══════════════════════════════════════════════════════════════

def eval_exit_model_watch() -> dict:
    """[41] 청산 측 학습기 게이지 (MW0602 428차) — 사전등록.

    [33] faststop_rerun_watch와 같은 **게이지**다. "언제 학습을 시작할 수 있는가"를
    매주 찍고, 요건에 닿으면 배너를 띄운다. verdict는 그때까지 OBSERVE.

    ⚠ 라이브 청산 무관여 — `exit_model_shadow`에 기록만 한다.
    """
    cr = VALIDATION_CAMPAIGN.get("exit_model_watch", {})
    out = {"verdict": "OBSERVE"}
    try:
        from learning.exit_outcome_labeler import (
            build_labels, summary as _lbl_summary, FEATURE_NAMES,
        )
        from learning.exit_classifier import (
            train_or_defer, MIN_EVENTS_PER_VARIABLE, MIN_DAYS as _EC_MIN_DAYS,
        )
        from config.settings import ATR_STOP_MULT, ATR_TP1_MULT
    except Exception as e:
        out["error"] = "청산 학습 모듈 로드 실패: %s" % e
        out["no_data"] = True
        return out

    # 설정 표류 감지 — settings와 코드 상수가 갈리면 게이지가 거짓말을 한다.
    _drift = []
    if abs(float(cr.get("min_events_per_variable", MIN_EVENTS_PER_VARIABLE))
           - float(MIN_EVENTS_PER_VARIABLE)) > 1e-9:
        _drift.append("min_events_per_variable")
    if int(cr.get("min_days", _EC_MIN_DAYS)) != int(_EC_MIN_DAYS):
        _drift.append("min_days")
    if _drift:
        out["config_drift"] = _drift

    try:
        rows = build_labels(TRADES_DB, PREDICTIONS_DB, RAW_DATA_DB,
                            _campaign_start(), ATR_STOP_MULT, ATR_TP1_MULT)
        smry = _lbl_summary(rows)
        res = train_or_defer(rows, smry, FEATURE_NAMES, TRADES_DB,
                             persist=False, label=str(cr.get("label", "y_hold_better")))
    except Exception as e:
        out["error"] = "라벨/학습 실패: %s" % e
        return out

    out["labels"] = smry
    out["readiness"] = res.get("readiness") or {}
    out["trained"] = bool(res.get("trained"))
    rd = out["readiness"]

    if not out["trained"]:
        _short = int(rd.get("positions_short") or 0)
        # 실측 진입속도로 남은 기간을 추정한다 — [33]과 같은 방식.
        _days = int(smry.get("n_days") or 0)
        _pos = int(smry.get("n_positions") or 0)
        _rate = (_pos / float(_days)) if _days else 0.0
        out["positions_per_day"] = round(_rate, 2)
        if _rate > 0 and _short > 0:
            out["eta_trading_days"] = int(round(_short / _rate))
        out["reason"] = rd.get("reason")
        return out

    out["oof_auc"] = res.get("oof_auc")
    out["oof_acc"] = res.get("oof_acc")
    out["baseline_acc"] = res.get("baseline_acc")
    _min_auc = float(cr.get("min_oof_auc", 0.55))
    if (res.get("oof_auc") or 0.0) >= _min_auc:
        out["verdict"] = "SUPPORTS_HYP"
        out["recommendation"] = (
            "청산 학습기가 정보를 갖는다 (OOF AUC %.4f >= %.2f, 기준선 정확도 %.4f) — "
            "**라이브 배선을 주간회의 안건으로.** 단 회전율은 안 늘지만 조기 청산은 "
            "이익도 자른다([11] 채널과 함께 읽을 것). D-day 스냅샷 이후에 배선할 것"
            % (res["oof_auc"], _min_auc, res.get("baseline_acc", 0)))
    else:
        out["verdict"] = "REJECTS_HYP"
        out["recommendation"] = (
            "학습은 열렸으나 정보가 없다 (OOF AUC %s < %.2f) — 청산 축도 현행 규칙 "
            "이상을 못 낸다는 뜻이다. 피처 재설계 또는 라벨 재정의 없이 재시도 금지"
            % (res.get("oof_auc"), _min_auc))
    return out


# ══════════════════════════════════════════════════════════════
# [40] 방향 선택의 가치 (MW0602 428차) — 연구 우선순위의 축
# ══════════════════════════════════════════════════════════════

def eval_direction_value_watch() -> dict:
    """[40] 방향 선택의 가치 (MW0602 428차) — 사전등록.

    같은 진입 시각·같은 청산 기하에서 실제 방향과 동전던지기를 비교한다.
    구현은 `scripts/random_entry_control.py`(오프라인·읽기 전용)에 있고 여기서는
    그것을 호출해 판정만 붙인다 — 시뮬 로직을 두 곳에 복붙하지 않기 위함이다
    ([11] resolver가 `_ts_execute_loss_tier1_exit`를 재사용한 것과 같은 취지).

    ⚠ 이 채널은 **"시스템 전체의 엣지"를 재지 않는다.** 방향 축 하나만 잰다.
       시뮬이 단순화돼 실제 손익을 재현하지 못하므로 절대 수준은 인용 금지.
    """
    cr = VALIDATION_CAMPAIGN.get("direction_value_watch", {})
    out = {"verdict": "INSUFFICIENT"}
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from random_entry_control import run as _rec_run
    except Exception as e:
        out["error"] = "random_entry_control 로드 실패: %s" % e
        out["no_data"] = True
        return out

    try:
        res = _rec_run(_campaign_start(), int(cr.get("trials", 400)),
                       int(cr.get("seed", 428)))
    except Exception as e:
        out["error"] = "시뮬 실패: %s" % e
        out["no_data"] = True
        return out
    out.update(res)
    if res.get("error"):
        out["no_data"] = True
        return out

    _min_n = int(cr.get("min_entries", 40))
    _min_d = int(cr.get("min_days", 6))
    _alpha = float(cr.get("alpha", 0.05))
    _min_share = float(cr.get("min_day_win_share", 0.70))

    if res.get("n_usable", 0) < _min_n or res.get("n_days", 0) < _min_d:
        out["reason"] = ("표본 부족 — 진입 %s건 / %s거래일 (필요 %d건 / %d일)"
                         % (res.get("n_usable"), res.get("n_days"), _min_n, _min_d))
        return out

    _days = int(res.get("days_evaluated") or 0)
    _share = (int(res.get("days_beating_random") or 0) / float(_days)) if _days else 0.0
    out["day_win_share"] = round(_share, 4)
    # 판정 2겹 — 전체 순열 p AND 일자단위 비율. 전체 합계 하나로 판정하면 큰 하루가
    # 통째로 만들 수 있다(0804에 같은 함정에 세 번 걸렸다).
    _perm_ok = float(res.get("p_one_sided", 1.0)) < _alpha
    _day_ok = _share >= _min_share
    out["perm_ok"], out["day_ok"] = _perm_ok, _day_ok

    if _perm_ok and _day_ok:
        out["verdict"] = "SUPPORTS_HYP"
        out["recommendation"] = (
            "**방향 선택이 무작위보다 우월하다** (단측 p=%.4f, 일자 %d/%d일=%.0f%%) — "
            "정보원 도입/피처 개선이 실제로 성과를 냈다는 첫 신호다. "
            "`docs/미륵이고도화3` 이월 D·E·G에 자원을 넣을 근거가 이제 생겼고, "
            "`FEATURE_SET_DECISIONS`의 `opt_trade_flow_realtime` 재검토 트리거 (2)도 "
            "충족된다" % (res.get("p_one_sided"), res.get("days_beating_random"),
                          _days, _share * 100))
    else:
        out["verdict"] = "REJECTS_HYP"
        out["recommendation"] = (
            "방향 선택이 동전던지기와 구분되지 않는다 (단측 p=%.4f, 일자 %d/%d일=%.0f%%). "
            "**방향 피처 재배치(이월 D·E·G)보다 청산 축([41])과 새 정보원 도입이 "
            "우선이다** — `FEATURE_SET_DECISIONS`의 `opt_trade_flow_realtime` "
            "재검토 트리거 (3)이 이 상태의 지속을 조건으로 걸려 있다"
            % (res.get("p_one_sided"), res.get("days_beating_random"),
               _days, _share * 100))
    return out


# ══════════════════════════════════════════════════════════════
# [39] confidence 판별력 감시 (MW0602 427차) — min_conf의 선행조건
# ══════════════════════════════════════════════════════════════

def _entry_decision_pairs(since, executed_only=True):
    """진입 체결(`trades.entry_ts`) ↔ 진입 결정(`ensemble_decisions`) 매핑.

    ⚠ **분 단위 정확 조인은 표본의 19%를 잃는다.** 캠페인 100포지션 전수 실측
    (MW0602 427차 후속):

        오프셋  0분 : 81건 — 체결 초 `:40~:59`
        오프셋 -1분 : 19건 — 체결 초 `:00~:09`
        방향 일치   : 100/100

    파이프라인이 `T:52` 근방에 주문을 내고 **체결 확인이 `T+1:00~:09`에 도착**하면
    `trades.entry_ts`(체결 시각)가 결정 분보다 1분 뒤가 된다. `ts[:16]`로 맞추면
    그 19건이 통째로 사라진다 — 데이터가 없는 게 아니라 **키가 어긋난 것**이다.
    (실제로 [39] 초판이 앙상블축 표본을 81/100으로 잃었고, [34]는 같은 결함을
     잠재 상태로 갖고 있었다 — effective_date 이후 아직 경계를 넘은 체결이 없어
     발현만 안 했다.)

    T → T-1 순으로 찾되 **방향 일치를 요구**한다. 방향까지 맞는 결정이 없으면
    매칭하지 않는다 — 인접 분에 반대 방향 결정이 있을 때 엉뚱하게 붙는 것을 막는다.

    Returns:
        (pairs, unmatched)
        pairs    = [(entry_ts, decision_row, offset_min), ...]
        unmatched = [entry_ts, ...]
    """
    _dirmap = {"LONG": 1, "SHORT": -1}
    try:
        with _conn(TRADES_DB) as conn:
            trows = conn.execute(
                "SELECT entry_ts, MIN(direction) AS direction "
                "  FROM trades WHERE entry_ts >= ? AND exit_ts IS NOT NULL AND %s "
                " GROUP BY entry_ts ORDER BY entry_ts" % _SYSTEM_AUTO_SQL,
                (since,)).fetchall()
        with _conn(PREDICTIONS_DB) as conn:
            erows = conn.execute(
                "SELECT * FROM ensemble_decisions WHERE ts >= ?%s"
                % (" AND entry_executed = 1" if executed_only else ""),
                (since,)).fetchall()
    except Exception:
        return [], []

    by_ts = {str(r["ts"]): r for r in erows}
    pairs, unmatched = [], []
    for t in trows:
        ets = str(t["entry_ts"])
        want = _dirmap.get(str(t["direction"]), 0)
        try:
            base = datetime.datetime.strptime(ets, _TS_FMT).replace(second=0)
        except ValueError:
            unmatched.append(ets)
            continue
        hit = None
        for off in (0, -1):
            k = (base + datetime.timedelta(minutes=off)).strftime(_TS_FMT)
            d = by_ts.get(k)
            if d is None:
                continue
            try:
                if int(d["direction"] or 0) != want:
                    continue
            except (TypeError, ValueError):
                continue
            hit = (ets, d, off)
            break
        if hit:
            pairs.append(hit)
        else:
            unmatched.append(ets)
    return pairs, unmatched


def _split_half_gap(pairs):
    """(conf, correct) 목록 → 상위절반 − 하위절반 적중률 격차.

    중앙값 기준 이분이 아니라 **정렬 후 절반**이다 — conf가 이산적으로 뭉쳐 있으면
    (실측: 0.35~0.40 구간에 44%가 몰린다) 중앙값 분할이 한쪽으로 쏠린다.
    """
    n = len(pairs)
    if n < 4:
        return None
    srt = sorted(pairs, key=lambda x: x[0])
    h = n // 2
    lo = sum(x[1] for x in srt[:h]) / float(h)
    hi = sum(x[1] for x in srt[h:]) / float(n - h)
    return {"n": n, "lo_acc": round(lo, 4), "hi_acc": round(hi, 4),
            "gap_pp": round((hi - lo) * 100.0, 3)}


def eval_conf_discrimination_watch() -> dict:
    """[39] confidence 판별력 감시 (MW0602 427차) — 사전등록.

    **min_conf 자체가 아니라 그 선행조건을 잰다.** 0804 조사에서 confidence가
    승/패를 전혀 가르지 못함이 확인됐고(앙상블 격차 -0.0015, 모델축 +0.4%p),
    그 상태에서 min_conf를 조이면 **무작위로 덜어낼 뿐**임이 스윕으로 확증됐다
    (잘려나간 진입 승률 62~63% = 전체 승률 63.0%).

    그래서 이 채널의 질문은 "min_conf를 얼마로 할까"가 아니라
    **"conf가 정보를 갖기 시작했는가"** 다. 그 순간이 오면 그때 min_conf를 논한다.

    상세 근거·임계 유도는 config.settings의 채널 주석 참조.
    """
    cr = VALIDATION_CAMPAIGN.get("conf_discrimination_watch", {})
    alpha = float(cr.get("alpha", 0.05))
    out = {"verdict": "INSUFFICIENT", "axes": {}}

    # ── (B) 모델축 — predictions.confidence vs correct ──────────
    _excl = set(cr.get("exclude_horizons", []) or [])
    try:
        with _conn(PREDICTIONS_DB) as conn:
            prows = conn.execute(
                "SELECT substr(ts,1,10) AS d, horizon, confidence AS c, correct AS k "
                "  FROM predictions "
                " WHERE ts >= ? AND correct IS NOT NULL AND confidence IS NOT NULL",
                (_campaign_start(),)).fetchall()
    except Exception as e:
        out["error"] = str(e)
        out["no_data"] = True
        return out

    kept = [(r["d"], float(r["c"]), int(r["k"])) for r in prows
            if r["horizon"] not in _excl]
    out["excluded_horizons"] = sorted(_excl)
    out["n_pred_excluded"] = len(prows) - len(kept)

    mb = {"n": len(kept), "n_days": len({d for d, _, _ in kept})}
    agg = _split_half_gap([(c, k) for _, c, k in kept])
    if agg:
        mb.update(agg)
        # 일자 층화 — **같은 날 안에서** 상/하위 절반을 가른다. 날짜 수준 교란
        # (그날은 변동성이 컸다)이 판별력으로 위장하는 것을 막는다(421차 Phase A 방식).
        day_gaps = []
        _byday = {}
        for d, c, k in kept:
            _byday.setdefault(d, []).append((c, k))
        for d, v in sorted(_byday.items()):
            g = _split_half_gap(v)
            if g:
                day_gaps.append(g["gap_pp"])
        mb["stratified"] = _paired_day_summary(day_gaps, alpha)
    out["axes"]["model"] = mb

    # ── (A) 앙상블축 — 진입한 포지션의 승/패 conf 격차 ───────────
    # [MW0602 427차 후속] 분 단위 정확 조인을 **공유 헬퍼로 교체**했다.
    # 초판은 `entry_ts[:16] == ts[:16]`이라 체결이 분 경계를 넘은 19건(체결 초
    # `:00~:09`)을 통째로 잃었다 — 데이터가 없는 게 아니라 키가 어긋난 것이었다.
    try:
        with _conn(TRADES_DB) as conn:
            _pnl = {str(r["entry_ts"]): float(r["k"] or 0.0) for r in conn.execute(
                "SELECT entry_ts, SUM(COALESCE(net_pnl_krw, pnl_krw)) AS k "
                "  FROM trades WHERE entry_ts >= ? AND exit_ts IS NOT NULL AND %s "
                " GROUP BY entry_ts" % _SYSTEM_AUTO_SQL, (_campaign_start(),))}
    except Exception as e:
        out["error"] = str(e)
        return out

    pairs, unmatched = _entry_decision_pairs(_campaign_start())
    rec, _off = [], {}
    for ets, d, off in pairs:
        _off[off] = _off.get(off, 0) + 1
        if d["confidence"] is None or ets not in _pnl:
            continue
        rec.append((ets[:10], float(d["confidence"]), _pnl[ets]))
    # 데이터 무결성 — 이 축의 표본을 직접 깎는다. 오프셋 분포도 함께 남긴다:
    # -1분 비중이 갑자기 늘면 체결 확인 지연이 커진 것이다(집행 품질 신호).
    _total = len(pairs) + len(unmatched)
    out["n_positions_total"] = _total
    out["n_matched"] = len(rec)
    out["n_unmatched"] = len(unmatched)
    out["unmatched_days"] = sorted({x[:10] for x in unmatched})
    out["match_rate"] = round(len(rec) / float(_total), 4) if _total else 0.0
    out["join_offset_min"] = {str(k): v for k, v in sorted(_off.items())}

    eb = {"n": len(rec), "n_days": len({d for d, _, _ in rec})}
    win = [c for _, c, k in rec if k > 0]
    los = [c for _, c, k in rec if k <= 0]
    eb["n_win"], eb["n_loss"] = len(win), len(los)
    if win and los:
        eb["win_conf"] = round(float(np.mean(win)), 4)
        eb["loss_conf"] = round(float(np.mean(los)), 4)
        eb["gap"] = round(eb["win_conf"] - eb["loss_conf"], 4)
        eb["conf_sd"] = round(float(np.std([c for _, c, _ in rec], ddof=1)), 4)
        if eb["conf_sd"] > 0:
            eb["cohen_d"] = round(eb["gap"] / eb["conf_sd"], 3)
        # 일자단위 — 승·패가 **둘 다 있는 날**만이 실질 표본이다
        _dg = []
        _bd = {}
        for d, c, k in rec:
            _bd.setdefault(d, []).append((c, k))
        for d, v in sorted(_bd.items()):
            w = [c for c, k in v if k > 0]
            l = [c for c, k in v if k <= 0]
            if w and l:
                _dg.append(float(np.mean(w) - np.mean(l)))
        eb["stratified"] = _paired_day_summary(_dg, alpha)
    out["axes"]["ensemble"] = eb

    # ── 판정 — 효과크기 AND 일자단위, 두 축 중 하나라도 통과하면 지지 ──
    _minp = int(cr.get("min_predictions", 2000))
    _minpos = int(cr.get("min_positions", 40))
    _mind = int(cr.get("min_days", 6))
    _gap_pp = float(cr.get("model_gap_min_pp", 3.0))
    _gap_ens = float(cr.get("ens_gap_min", 0.025))

    model_ready = mb.get("n", 0) >= _minp
    ens_ready = (eb.get("n", 0) >= _minpos
                 and (eb.get("stratified") or {}).get("paired_days", 0) >= _mind)
    if not model_ready and not ens_ready:
        out["reason"] = ("표본 부족 — 모델축 %d건(필요 %d) / 앙상블축 %d건·짝지은 %d일"
                         "(필요 %d건·%d일)" % (
                             mb.get("n", 0), _minp, eb.get("n", 0),
                             (eb.get("stratified") or {}).get("paired_days", 0),
                             _minpos, _mind))
        return out

    model_hit = bool(
        model_ready
        and mb.get("gap_pp", 0.0) >= _gap_pp
        and (mb.get("stratified") or {}).get("significant"))
    ens_hit = bool(
        ens_ready
        and eb.get("gap", 0.0) >= _gap_ens
        and (eb.get("stratified") or {}).get("significant"))
    out["model_hit"], out["ens_hit"] = model_hit, ens_hit

    if model_hit or ens_hit:
        out["verdict"] = "SUPPORTS_HYP"
        out["recommendation"] = (
            "confidence 판별력 출현 — %s축이 효과크기·일자단위 검정을 동시 통과했다. "
            "**min_conf 재검토를 주간회의 안건으로 올릴 시점이다**(0804 §P2가 보류한 "
            "바로 그 안건). 임계는 이 시점의 conf 분포로 새로 잡을 것 — 설계값 "
            "0.54~0.67은 구 분포 기준이라 그대로 쓰면 진입이 사라진다"
            % ("모델" if model_hit else "앙상블"))
    else:
        out["verdict"] = "REJECTS_HYP"
        out["recommendation"] = (
            "판별력 없음 — 모델축 격차 %+.2f%%p(임계 %.1f) / 앙상블축 %+.4f(임계 %.3f). "
            "**min_conf 조정은 무의미하다**: 정보 없는 신호를 조이면 무작위로 덜어낼 "
            "뿐이다(0804 스윕 실측 — 잘려나간 진입 승률 62~63%% = 전체 63.0%%). "
            "선행조건은 §P1(방향모델 랜덤) 해소이며, 새 정보원이 들어오면 이 채널이 "
            "먼저 반응한다" % (mb.get("gap_pp", 0.0), _gap_pp,
                              eb.get("gap", 0.0), _gap_ens))
    return out


# ══════════════════════════════════════════════════════════════
# [38] ProfitGuard-L1 피크 트레일링 (MW0602 426차) — 희귀사건 채널
# ══════════════════════════════════════════════════════════════

def _pg_live_config() -> dict:
    """라이브 ProfitGuard 파라미터의 **실제 출처**를 읽는다.

    ⚠ 이 채널의 기준선은 코드에 없다 — `data/profit_guard_prefs.json`이며
    대시보드에서 **장중 변경이 가능**하다. 코드 기본값(`ProfitGuardConfig`)만
    보고 판정하면 전혀 다른 임계를 재게 된다(419·420차 `tox_regime_date`
    교훈의 더 나쁜 버전 — 그쪽은 최소한 코드 안에 있었다).
    """
    cr = VALIDATION_CAMPAIGN.get("profit_guard_l1_watch", {})
    rel = str(cr.get("live_prefs_path", "data/profit_guard_prefs.json"))
    out = {"prefs_path": rel, "source": "code_default"}
    try:
        from strategy.profit_guard import ProfitGuardConfig
        _d = ProfitGuardConfig()
        out["code_activation_krw"] = float(_d.trail_activation_krw)
        out["code_ratio"] = float(_d.trail_ratio)
        out["activation_krw"] = out["code_activation_krw"]
        out["ratio"] = out["code_ratio"]
    except Exception as e:
        out["error"] = "코드 기본값 로드 실패: %s" % e
        return out
    path = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), rel.replace("/", os.sep))
    out["prefs_exists"] = os.path.exists(path)
    if out["prefs_exists"]:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                cfg = (json.load(fh) or {}).get("config") or {}
            if "trail_activation_krw" in cfg:
                out["activation_krw"] = float(cfg["trail_activation_krw"])
            if "trail_ratio" in cfg:
                out["ratio"] = float(cfg["trail_ratio"])
            out["source"] = "prefs_json"
            out["prefs_mtime"] = datetime.datetime.fromtimestamp(
                os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            out["error"] = "prefs 파싱 실패: %s" % e
    out["diverged"] = (
        abs(out["activation_krw"] - out["code_activation_krw"]) > 1e-9
        or abs(out["ratio"] - out["code_ratio"]) > 1e-9
    )
    return out


def _pg_replay(activation, ratio, days, legs_by_day, pos_by_day):
    """(발동금액, 비율) 격자 하나를 전 거래일에 소급 재현한다.

    실현손익 경로를 청산 레그 순서로 누적해 피크·보호선을 따라간다 — 라이브
    `_TrailingGuard.update()`와 같은 식이다(`peak >= activation` 이후
    `current < peak*(1-ratio)`).

    **발동했다고 다 같은 발동이 아니다.** 07-20은 14:56에 발동했는데 그날
    마지막 진입이 14:33이고 14:50부터 신규금지 구간이라 아무것도 막지 못했다.
    그래서 `binding`(발동 후 실제 진입 기회가 있었는가)을 따로 센다 — 이것이
    이 채널의 표본 단위다.
    """
    fires = []
    for d in days:
        run = peak = 0.0
        halt = None
        for lg in legs_by_day.get(d, []):
            run += lg["k"]
            if run > peak:
                peak = run
            if halt is None and peak >= activation and run < peak * (1.0 - ratio):
                halt = lg["exit_ts"]
                break
        if halt is None:
            continue
        after = [p for p in pos_by_day.get(d, []) if p["entry_ts"] > halt]
        fires.append({
            "day": d, "halt_ts": halt, "peak_krw": round(peak, 0),
            "n_after": len(after),
            "after_pnl_krw": round(sum(p["k"] for p in after), 0),
            "binding": bool(after),
        })
    return fires


def eval_profit_guard_l1_watch() -> dict:
    """[38] ProfitGuard-L1 피크 트레일링 감시 (MW0602 426차) — 사전등록.

    0804 점검이 L1을 "오늘 최대 공로자"로 적었으나 검증에서 **과장으로 확인**됐다.
    상세 근거·판정 축은 config.settings의 채널 주석 참조.

    verdict는 표본이 찰 때까지 OBSERVE다 — 실측 발동빈도(16거래일에 구속 1회)로는
    min_activations=5가 약 4개월 스케일이라, 그 사이에 판정을 흉내내면 단일일
    관측이 정책이 된다(0804에서 실제로 그럴 뻔했다).
    """
    cr = VALIDATION_CAMPAIGN.get("profit_guard_l1_watch", {})
    out = {"verdict": "OBSERVE", "live_config": _pg_live_config()}
    win = int(cr.get("cf_window_min", 30))

    # ── 실현손익 경로 (소급 재현용) ──────────────────────────────
    try:
        with _conn(TRADES_DB) as conn:
            legs = conn.execute(
                "SELECT entry_ts, exit_ts, COALESCE(net_pnl_krw, pnl_krw) AS k "
                "  FROM trades WHERE entry_ts >= ? AND exit_ts IS NOT NULL AND %s "
                " ORDER BY exit_ts" % _SYSTEM_AUTO_SQL, (_campaign_start(),)).fetchall()
            poss = conn.execute(
                "SELECT entry_ts, SUM(COALESCE(net_pnl_krw, pnl_krw)) AS k "
                "  FROM trades WHERE entry_ts >= ? AND exit_ts IS NOT NULL AND %s "
                " GROUP BY entry_ts" % _SYSTEM_AUTO_SQL, (_campaign_start(),)).fetchall()
    except Exception as e:
        out["error"] = str(e)
        out["no_data"] = True
        return out

    legs_by_day, pos_by_day = {}, {}
    for r in legs:
        legs_by_day.setdefault(r["exit_ts"][:10], []).append(
            {"exit_ts": r["exit_ts"], "k": float(r["k"] or 0.0)})
    for r in poss:
        pos_by_day.setdefault(r["entry_ts"][:10], []).append(
            {"entry_ts": r["entry_ts"], "k": float(r["k"] or 0.0)})
    days = sorted(pos_by_day)
    out["n_days_total"] = len(days)

    # ── (c) 임계 스윕 — 전 거래일 소급 재현 ─────────────────────
    sweep = []
    for act in cr.get("sweep_activation_krw", [1_000_000]):
        for ratio in cr.get("sweep_ratio", [0.20]):
            f = _pg_replay(float(act), float(ratio), days, legs_by_day, pos_by_day)
            bind = [x for x in f if x["binding"]]
            sweep.append({
                "activation_krw": float(act), "ratio": float(ratio),
                "n_fire": len(f), "n_binding": len(bind),
                "n_blocked_pos": sum(x["n_after"] for x in bind),
                # (+)면 차단해서 **지킨** 금액(막은 손실), (-)면 놓친 이익
                "saved_krw": round(-sum(x["after_pnl_krw"] for x in bind), 0),
            })
    out["sweep"] = sweep

    # ── (b)(d) 차단분 반사실 + 재개 지연 — 라이브에서 실제로 차단된 신호 ──
    try:
        with _conn(PREDICTIONS_DB) as conn:
            blocked = conn.execute(
                "SELECT ts, direction, grade, features FROM ensemble_decisions "
                " WHERE ts >= ? AND entry_block_reason LIKE '%ProfitGuard%' "
                " ORDER BY ts", (_campaign_start(),)).fetchall()
    except Exception as e:
        out["cf_error"] = str(e)
        blocked = []
    out["n_blocked_signals"] = len(blocked)
    out["blocked_days"] = sorted({r["ts"][:10] for r in blocked})
    _blk_by_day = {}
    for r in blocked:
        _blk_by_day.setdefault(r["ts"][:10], []).append(r["ts"])

    # 현행 운영값 행을 따로 뽑아 둔다 — 판정과 표기의 기준선이다.
    _lc = out["live_config"]
    cur = _pg_replay(float(_lc.get("activation_krw", 1_000_000)),
                     float(_lc.get("ratio", 0.20)), days, legs_by_day, pos_by_day)
    # ⚠ **순환논리 교정.** `_pg_replay`의 binding은 "발동 후 실제 진입이 있었는가"인데,
    #   가드가 **라이브로 실제 발동한 날**은 그 진입이 애초에 없다 — 가드가 막았기
    #   때문이다. 그 날을 "구속 아님"으로 세면 유일한 진짜 구속 사건이 사라진다
    #   (08-04이 정확히 그랬다). 라이브 차단 기록이 있으면 구속으로 인정한다.
    for f in cur:
        _lb = [t for t in _blk_by_day.get(f["day"], []) if t >= f["halt_ts"]]
        if _lb:
            f["binding"] = True
            f["n_live_blocked"] = len(_lb)
        else:
            f["n_live_blocked"] = 0
    out["fires"] = cur
    out["n_fire"] = len(cur)
    binding = [x for x in cur if x["binding"]]
    out["n_binding"] = len(binding)
    out["n_binding_days"] = len({x["day"] for x in binding})

    if blocked:
        _lo = min(r["ts"] for r in blocked)
        _hi = max(r["ts"] for r in blocked)
        try:
            with _conn(RAW_DATA_DB) as rc:
                bars = {r["ts"]: dict(r) for r in rc.execute(
                    "SELECT ts, high, low, close FROM raw_candles "
                    " WHERE ts >= ? AND ts <= datetime(?, '+%d minutes') ORDER BY ts"
                    % win, (_lo, _hi))}
        except Exception as e:
            out["cf_error"] = str(e)
            bars = {}
        seq = sorted(bars)
        # 그날 최초 차단 시각 = 발동 시각 근사 (재개 지연 축의 기준점)
        first_block = {}
        for r in blocked:
            first_block.setdefault(r["ts"][:10], r["ts"])

        rows, res = [], {"TP1": 0, "STOP": 0, "NEITHER": 0}
        for r in blocked:
            b = bars.get(r["ts"])
            if not b or not r["direction"]:
                continue
            try:
                atr = float((json.loads(r["features"]) or {}).get("atr") or 0.0)
            except (ValueError, TypeError):
                atr = 0.0
            if atr <= 0:
                continue
            m = 1 if int(r["direction"]) == 1 else -1
            e = float(b["close"])
            stop = e - m * atr * ATR_STOP_MULT
            tp1 = e + m * atr * ATR_TP1_MULT
            end = (datetime.datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S")
                   + datetime.timedelta(minutes=win)).strftime("%Y-%m-%d %H:%M:%S")
            out_kind, px = "NEITHER", None
            for ts in seq:
                if ts <= r["ts"]:
                    continue
                if ts > end:
                    break
                bb = bars[ts]
                if (bb["low"] <= stop) if m > 0 else (bb["high"] >= stop):
                    out_kind, px = "STOP", stop
                    break
                if (bb["high"] >= tp1) if m > 0 else (bb["low"] <= tp1):
                    out_kind, px = "TP1", tp1
                    break
            if px is None:
                px = float(bars[seq[-1]]["close"]) if seq else e
            res[out_kind] += 1
            _delay = (datetime.datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S")
                      - datetime.datetime.strptime(first_block[r["ts"][:10]],
                                                   "%Y-%m-%d %H:%M:%S")).total_seconds() / 60.0
            rows.append({"day": r["ts"][:10], "pt": (px - e) * m, "delay_min": _delay})

        out["cf_n"] = len(rows)
        out["cf_outcome"] = res
        if rows:
            out["cf_total_pt"] = round(sum(x["pt"] for x in rows), 4)
            out["cf_avg_pt"] = round(out["cf_total_pt"] / len(rows), 4)
            # (d) 재개 지연 구간별 — 두 조각을 **함께** 낸다. 한쪽만 보면 오독한다.
            #   kept_pt   : 재개 전까지 계속 차단한 구간의 신호 손익
            #               → (-)면 그 구간 차단이 이득(손실을 막았다)
            #   resumed_pt: 재개 후 신호 손익 → (+)면 재개가 이득(이익을 되찾았다)
            #   net_pt    : 재개 정책의 순효과 = resumed_pt (차단 유지분은 어느
            #               지연을 고르든 그대로 회피되므로 비교에서 상쇄된다)
            resume = {}
            for dly in cr.get("resume_delay_min", [0, 15, 30, 60]):
                _d = float(dly)
                after = [x for x in rows if x["delay_min"] >= _d]
                before = [x for x in rows if x["delay_min"] < _d]
                resume[str(dly)] = {
                    "n": len(after),
                    "pt": round(sum(x["pt"] for x in after), 4),
                    "n_kept": len(before),
                    "kept_pt": round(sum(x["pt"] for x in before), 4),
                }
            out["resume_delay"] = resume
            # 일자단위(313차) — 차단일이 여러 날 쌓이면 부호검정이 가능해진다
            _dm = {}
            for x in rows:
                _dm.setdefault(x["day"], []).append(x["pt"])
            out.update(_paired_day_summary(
                [float(np.mean(v)) for _, v in sorted(_dm.items())],
                float(cr.get("alpha", 0.05))))

    # ── 판정 — 표본이 찰 때까지 OBSERVE ─────────────────────────
    _min_a = int(cr.get("min_activations", 5))
    _min_d = int(cr.get("min_days", 5))
    if out["n_binding"] < _min_a or out["n_binding_days"] < _min_d:
        out["reason"] = (
            "구속 발동 %d건 / %d거래일 (필요 %d건 / %d일) — 관찰 단계. "
            "실측 발동빈도로는 약 4개월 스케일이다"
            % (out["n_binding"], out["n_binding_days"], _min_a, _min_d))
    return out


# ──────────────────────────────────────────────────────────────
# [24] TP1 보호전환 반납 관찰 (404차 후속3) — verdict 항상 OBSERVE
# ──────────────────────────────────────────────────────────────

def eval_tp1_protect_giveback_watch() -> dict:
    """qty=1 TP1 보호전환에서 "장부이익 대비 실제로 얼마를 지켰는가"를 관찰한다.

    소스는 synthetic_partial_exits — 보호전환 시점의 TP1 장부이익(synthetic_pnl_pts)과
    보호스톱(stop_after)이 기록돼 있는데 **캠페인 소비처가 하나도 없어 방치돼 있었다**
    (402차 후속3 toxicity_block_shadow와 같은 계열의 사각지대).

    청산 기하 10개 차원 중 "보호전환 offset 폭"(차원 D)이 통째로 미계측이었고,
    이 채널이 그 눈을 뜬다. 처방(offset을 얼마로 할지) 검증은 [25]가 맡는다 —
    여기서는 판정하지 않는다(verdict 항상 OBSERVE).

    평균이 아니라 **중앙값**을 주 지표로 낸다: 0729 폭락일 2건이 평균을 5배 끌어올려
    "평균 반납 0.21pt(8%)"와 "중앙값 반납 1.00pt"가 정반대 인상을 준다(372차 원칙).
    """
    out = {"verdict": "OBSERVE"}
    try:
        with _conn(TRADES_DB) as conn:
            hooks = conn.execute(
                """SELECT ts, entry_ts, direction, entry_price, synthetic_price,
                          synthetic_pnl_pts, protect_mode, stop_after
                     FROM synthetic_partial_exits
                    WHERE ts >= ? ORDER BY ts""", (_campaign_start(),)).fetchall()
            rows = []
            for h in hooks:
                real = conn.execute(
                    """SELECT sum(pnl_pts*quantity)/sum(quantity) FROM trades
                        WHERE entry_ts = ? AND exit_ts IS NOT NULL""",
                    (h["entry_ts"],)).fetchone()[0]
                if real is None:
                    continue
                paper = float(h["synthetic_pnl_pts"] or 0.0)
                rows.append({
                    "ts": h["ts"], "mode": h["protect_mode"], "paper": paper,
                    "real": float(real), "give": paper - float(real),
                    "offset": abs(float(h["stop_after"]) - float(h["entry_price"])),
                })
    except Exception as e:
        out["error"] = str(e)
        return out

    out["n"] = len(rows)
    out["n_days"] = len({r["ts"][:10] for r in rows})
    if not rows:
        out["reason"] = "표본 없음"
        return out

    # [MW0601 406차 / D] 모드별 분리 집계.
    # 보호스톱을 거는 자리가 모드마다 다르다(breakeven=진입가 / breakeven_plus=+0.20pt /
    # atr_profit=ATR×0.25). 그래서 "반납"이라는 말의 기준선 자체가 모드마다 다르고,
    # 섞어서 평균·중앙값·상관을 내면 두 자를 섞어 재는 것과 같다. 실측으로도 부호가
    # 반대로 나온다 — 0802 대조에서 중앙값 반납이 MW0601(breakeven) −0.1pt vs
    # MW0602(atr_profit) +1.0pt였다. 이 채널의 수치는 MW0602 검토보고 §1-4에서
    # "더 들고 있어라"의 근거로 인용됐으므로 라벨 없이 두면 안 된다.
    #
    # 지금은 각 PC 안에서 우연히 단일 모드지만 한 PC가 모드를 바꾸면 그 PC의 DB
    # 안에서 섞인다(MW0601은 406차 A로 breakeven→atr_profit 전환했다 — 08-03부터
    # 실제로 섞이기 시작한다).
    #
    # 최상위 키는 하위호환을 위해 **풀링 값 그대로** 둔다(기존 소비처·metrics 스키마
    # 무변경). 모드별 값은 by_mode_stats에 병기하고, 혼재 시 modes_mixed로 알린다.
    # [24]는 verdict가 항상 OBSERVE이므로 판정에는 아무 영향이 없다.
    def _give_stats(subset: list) -> dict:
        g = np.array([r["give"] for r in subset])
        o = np.array([r["offset"] for r in subset])
        p = np.array([r["paper"] for r in subset])
        st = {
            "n": len(subset),
            "n_days": len({r["ts"][:10] for r in subset}),
            "n_gaveback": int((g > 0).sum()),
            "n_ranfurther": int((g < 0).sum()),
            "mean_give_pt": round(float(g.mean()), 4),
            "median_give_pt": round(float(np.median(g)), 4),
            "mean_paper_pt": round(float(p.mean()), 4),
            "median_paper_pt": round(float(np.median(p)), 4),
            "mean_offset_pt": round(float(o.mean()), 4),
        }
        if np.median(p) > 0:
            st["median_giveback_rate"] = round(float(np.median(g) / np.median(p)), 4)
        if len(subset) > 2 and o.std() > 0 and g.std() > 0:
            # [MW0601 405차] np.corrcoef → _pearson_r (py310_64 네이티브 크래시 회피)
            _r = _pearson_r(o, g)
            if _r is not None:
                st["offset_vs_give_corr"] = round(_r, 4)
        return st

    out.update(_give_stats(rows))
    out["n"] = len(rows)          # _give_stats의 n과 동일하지만 명시적으로 되돌린다
    out["n_days"] = len({r["ts"][:10] for r in rows})

    modes = {}
    by_mode_rows = {}
    for r in rows:
        _m = r["mode"] or "(미기록)"
        modes[_m] = modes.get(_m, 0) + 1
        by_mode_rows.setdefault(_m, []).append(r)
    out["by_mode"] = modes
    out["by_mode_stats"] = {m: _give_stats(rs) for m, rs in sorted(by_mode_rows.items())}
    out["modes_mixed"] = len(by_mode_rows) > 1
    return out


# ──────────────────────────────────────────────────────────────
# [26] 거래불능(가격상한 고착) 구간 관찰 (404차 후속5) — verdict 항상 OBSERVE
# ──────────────────────────────────────────────────────────────

def eval_limit_pin_watch() -> dict:
    """가격이 일중 극단에 붙은 채 거래량이 붕괴한 구간을 계측한다.

    계기: 0731 정기점검 §1-C 이상점 3이 "14:20~15:06 가격 고착 46분 → MFE·캡처율·
    PSI 계측이 오염된다"고 지적했다. 그 가설을 검증하려면 먼저 구간을 기계적으로
    특정해야 한다(`utils/market_state.detect_limit_pin_bars`).

    ## 이 채널이 내는 핵심 수치는 "고착 분봉 수"가 아니라 `extreme_liquid_touches`다

    고착 분봉의 high/low가 MFE를 오염시키려면 **그 극단을 고착 분봉만이 만들었어야**
    한다. 그런데 가격이 상한에 붙으려면 먼저 유동적으로 그 가격에 도달해야 하므로,
    보통은 유동 분봉이 이미 같은 극단을 만들어 둔다 — 그러면 고착 분봉을 전부
    지워도 MFE는 한 틱도 안 변한다(max 연산이라 중복은 무해).

    2026-07-31 실측: 고착 29분봉, 그러나 1036.28을 유동 분봉 13개(최대 vol 642)가
    이미 터치 → **MFE 오염 0**. 리포트가 지목한 오염은 실측으로 기각된다.
    `extreme_liquid_touches == 0`인 날이 나오면 그때는 진짜 오염이므로 경고한다
    (갭 상한가 직행 등 — 현 표본엔 없음).

    실제 오염은 counterfactual의 진입가·목표가 쪽이며 [27]이 계측한다.
    """
    out = {"verdict": "OBSERVE"}
    try:
        with _conn(RAW_DATA_DB) as conn:
            bars = [dict(r) for r in conn.execute(
                "SELECT ts, high, low, volume FROM raw_candles WHERE ts >= ? ORDER BY ts",
                (_campaign_start(),))]
    except Exception as e:
        out["error"] = str(e)
        return out
    if not bars:
        out["reason"] = "분봉 없음"
        return out

    flagged = detect_limit_pin_bars(bars)
    out["n_session_bars"] = sum(1 for b in bars if b["ts"][11:16] >= SESSION_OPEN_HHMM)
    out["n_pinned_bars"] = len(flagged)
    if not flagged:
        out["reason"] = "캠페인 기간 중 가격상한 고착 구간 없음"
        return out

    by_day = {}
    for ts, side in flagged.items():
        by_day.setdefault((ts[:10], side), []).append(ts)

    days, contaminated = [], []
    for (day, side), tss in sorted(by_day.items()):
        tss.sort()
        sess = [b for b in bars if b["ts"][:10] == day
                and b["ts"][11:16] >= SESSION_OPEN_HHMM]
        field = "high" if side == "UP" else "low"
        extreme = (max(b["high"] for b in sess) if side == "UP"
                   else min(b["low"] for b in sess))
        # 그 극단을 '유동' 분봉이 터치했는가 — 오염 실재 여부의 직접 지표
        liquid = [b for b in sess if float(b[field]) == float(extreme)
                  and int(b["volume"] or 0) >= LIMIT_PIN_LIQUID_VOL_MIN]
        # 구간 내 결측 분봉 수 (거래 자체가 없던 분)
        t0 = datetime.datetime.strptime(tss[0], _TS_FMT)
        t1 = datetime.datetime.strptime(tss[-1], _TS_FMT)
        span = int((t1 - t0).total_seconds() // 60) + 1
        rec = {
            "date": day, "side": side, "price": round(float(extreme), 2),
            "n_bars": len(tss), "from": tss[0][11:16], "to": tss[-1][11:16],
            "span_min": span, "n_missing_bars": span - len(tss),
            "extreme_liquid_touches": len(liquid),
            "max_liquid_vol": max((int(b["volume"] or 0) for b in liquid), default=0),
        }
        days.append(rec)
        if not liquid:
            contaminated.append(rec)

    out["days"] = days
    out["n_days"] = len(days)
    out["mfe_contaminated_days"] = contaminated
    out["mfe_contamination"] = bool(contaminated)
    return out


# 가격상한 고착이 있었던 날의 (일자 → 상한가격) 맵. [27]과 counterfactual 제외에서 공용.
_LIMIT_DAYS_CACHE = None


def _limit_price_by_day() -> dict:
    global _LIMIT_DAYS_CACHE
    if _LIMIT_DAYS_CACHE is not None:
        return _LIMIT_DAYS_CACHE
    _LIMIT_DAYS_CACHE = _limit_price_by_day_uncached()
    return _LIMIT_DAYS_CACHE


def _limit_price_by_day_uncached() -> dict:
    try:
        with _conn(RAW_DATA_DB) as conn:
            bars = [dict(r) for r in conn.execute(
                "SELECT ts, high, low, volume FROM raw_candles WHERE ts >= ? ORDER BY ts",
                (_campaign_start(),))]
    except Exception:
        return {}
    flagged = detect_limit_pin_bars(bars)
    out = {}
    for ts, side in flagged.items():
        day = ts[:10]
        bar = next((b for b in bars if b["ts"] == ts), None)
        if bar is None:
            continue
        out.setdefault(day, {})[side] = float(bar["high"])
    return out


# ──────────────────────────────────────────────────────────────
# [27] counterfactual 도달불가 목표가 감시 (404차 후속5) — verdict 항상 OBSERVE
# ──────────────────────────────────────────────────────────────

def eval_unreachable_cf_watch() -> dict:
    """목표가가 그날 가격상한 밖이었던 counterfactual 행을 세고 **민감도만** 낸다.

    ## 이 채널은 판정을 바꾸지 않는다 — 그 이유가 핵심이다

    초안에서는 이런 행을 "이길 수 있는 경우의 수가 0인 가상거래"로 보고 판정에서
    자동 제외(resolved 1→2)하도록 짰다가 **되돌렸다.** 전제가 틀렸기 때문이다:

      2026-07-31 14:17 시점 시장은 유동적이었고(분봉 vol 109), 그때 실제로 LONG
      진입했다면 체결됐을 것이다. 그리고 TP1 1037.07은 상한(1036.28) 밖이라
      **정말로 안 채워지고** 스톱만 맞았을 것이다. 즉 counterfactual은 모델링
      결함이 아니라 **나쁜 거래를 충실히 시뮬레이션**한 것이고, 게이트가 막은 것은
      실제 손실 회피가 맞다. 이런 행을 빼면 게이트의 정당한 공로를 지우게 된다.

    남는 진짜 질문은 측정 오류가 아니라 **공로의 출처**다: 게이트가 자기 로직
    (meta·tox 점수)으로 막은 게 아니라, 신호가 우연히 가격상한에서 발생해 구조적으로
    질 수밖에 없었던 케이스라면, 그 이득은 게이트 알파가 아니라 시장 구조에서 온다.
    "옳았지만 이유는 달랐다"는 판정 오류가 아니라 **해석의 문제**이므로, 판정을
    조용히 바꾸지 않고 민감도만 병기해 주간회의에 올린다(§9 사전등록 원칙).

    실제로 이 5건을 빼면 [18] RegimeExhaustionGate 판정이 SUPPORTS_GATE →
    REJECTS_GATE로 **뒤집힌다**(누적 hyp −1.75 → +6.85, n 28 → 25). 표본 3건이
    권고를 뒤집는다는 사실 자체가 그 채널의 결론이 얼마나 얇은 근거 위에 있는지를
    보여주는 소득이다 — 372차 이상치 분해와 같은 교훈.

    verdict는 항상 OBSERVE. DB를 쓰지 않는 읽기 전용 분석이다.
    """
    out = {"verdict": "OBSERVE"}
    limits = _limit_price_by_day()
    out["limit_days"] = {d: v for d, v in limits.items()}
    if not limits:
        out["reason"] = "가격상한 고착일 없음 — 도달불가 목표가 발생 여지 없음"
        return out

    tables = ["hurst_gate_shadow", "joint_gate_shadow", "open_gap_shadow",
              "regime_exhaustion_shadow", "toxicity_block_shadow"]
    hits, by_table, sens = [], {}, {}
    try:
        with _conn(TRADES_DB) as conn:
            for t in tables:
                try:
                    rows = conn.execute(
                        "SELECT ts, direction, entry_price, tp1_price, cf_outcome, "
                        "hyp_pnl_pts FROM %s WHERE resolved=1 AND ts >= ?" % t,
                        (_campaign_start(),)).fetchall()
                except Exception:
                    continue
                bad = []
                for r in rows:
                    lim = limits.get(str(r["ts"])[:10])
                    if lim and _cf_target_unreachable(r["direction"], r["tp1_price"], lim):
                        bad.append(r)
                        hits.append({
                            "table": t, "ts": r["ts"], "dir": r["direction"],
                            "entry": r["entry_price"], "tp1": r["tp1_price"],
                            "limit": lim.get("UP") or lim.get("DOWN"),
                            "cf_outcome": r["cf_outcome"],
                            "hyp_pnl_pts": r["hyp_pnl_pts"],
                        })
                if not bad:
                    continue
                by_table[t] = len(bad)
                tot = sum(float(r["hyp_pnl_pts"] or 0.0) for r in rows)
                rm = sum(float(r["hyp_pnl_pts"] or 0.0) for r in bad)
                sens[t] = {
                    "n": len(rows), "n_excluded": len(bad),
                    "total_hyp_pnl_pts": round(tot, 4),
                    "total_if_excluded": round(tot - rm, 4),
                    "delta": round(-rm, 4),
                }
    except Exception as e:
        out["error"] = str(e)
        return out

    out["n_unreachable"] = len(hits)
    out["by_table"] = by_table
    out["rows"] = hits
    out["sensitivity"] = sens
    out["excluded_hyp_pnl_pts"] = round(
        sum(float(h["hyp_pnl_pts"] or 0.0) for h in hits), 4)
    if not hits:
        out["reason"] = "도달불가 목표가 행 없음"
    return out


def _ensure_shadow_mfe_columns(table: str) -> bool:
    """[404차 후속9 / P1-D] 섀도 테이블에 `mfe_30m`/`mae_30m` 컬럼을 보장한다(멱등).

    스키마 원본은 `utils/db_utils.py`지만 거기서 바꾸면 **기존 DB가 자동으로 갱신되지
    않는다**(CREATE TABLE IF NOT EXISTS라 이미 있는 테이블은 건드리지 않는다). 두 PC가
    각자 로컬 DB를 갖고 있으므로 ALTER를 여기서 멱등 실행한다.
    """
    try:
        with _conn(TRADES_DB) as conn:
            cols = {r[1] for r in conn.execute("PRAGMA table_info(%s)" % table)}
            for c in ("mfe_30m", "mae_30m"):
                if c not in cols:
                    conn.execute("ALTER TABLE %s ADD COLUMN %s REAL" % (table, c))
            conn.commit()
        return True
    except Exception:
        return False


_JGS_EXTRA_COLS = (
    ("meta_conf", "REAL"), ("meta_conf_raw", "REAL"), ("meta_size_raw", "REAL"),
    ("meta_size_fallback", "INTEGER"), ("tox_score", "REAL"),
    ("tox_score_ma", "REAL"), ("tox_ceiling", "REAL"),
    ("tox_size_shadow", "REAL"), ("joint_mult_shadow", "REAL"),
    ("would_block_shadow", "INTEGER"),
    # [MW0602 456차] 폴백 중립화 반사실. 주간 리포트가 아직 소비하지 않는다 —
    # 표본이 쌓이면 [7] 채널에 절을 추가할 것(NEXT_TODO 456차 항목).
    ("meta_neutral_pass", "INTEGER"),
)


def _ensure_trades_exit_axis_columns() -> bool:
    """[MW0602 468차 G-3] trades의 청산 2축 컬럼을 보장한다(멱등).

    `_ensure_guard_shadow_columns`·`_ensure_joint_gate_columns`와 완전히 같은 사정 —
    스키마 원본은 `utils/db_utils.py`지만 두 PC가 각자 로컬 trades.db를 갖고 있고,
    **리포트가 앱 재기동보다 먼저 돌 수 있다.** 컬럼이 없으면 이 축을 쓰는 SELECT가
    예외를 내고 `out["error"]`로 삼켜져 채널이 조용히 죽는다(420차 joint_gate_shadow와
    같은 사고 형태). 여기가 2차 방어선이다.

    기존 행은 NULL로 남는다 — **소급 계산하지 않는다.** `exit_trigger`의
    하드스톱/보호트레일 구분은 `tp1_reached`(2026-08-13부터 적재)에 의존하는데,
    그 이전 행은 그 값 자체가 없다. `pnl_pts>0`으로 추정하면 트리거 축이 결과 축과
    상관돼 2축으로 나눈 의미가 사라진다.
    """
    try:
        with _conn(TRADES_DB) as conn:
            cols = {r[1] for r in conn.execute("PRAGMA table_info(trades)")}
            for c in ("exit_trigger", "exit_outcome"):
                if c not in cols:
                    conn.execute("ALTER TABLE trades ADD COLUMN %s TEXT" % c)
            conn.commit()
        return True
    except Exception as e:
        print("[WARN] trades 청산 2축 컬럼 보장 실패: %s" % e, file=sys.stderr)
        return False


def _ensure_joint_gate_columns() -> bool:
    """[MW0601 420차] joint_gate_shadow의 419차 반영 계측 컬럼을 보장한다(멱등).

    _ensure_shadow_mfe_columns와 완전히 같은 사정 — 스키마 원본은
    `utils/db_utils.py`지만 CREATE TABLE IF NOT EXISTS는 **이미 있는 테이블을
    갱신하지 않는다**. 두 PC가 각자 로컬 DB를 갖고 있으므로 ALTER를 여기서 돌린다.

    기존 행은 NULL로 남는다 — 소급 계산하지 않는다. meta 폴백 여부·tox 원점수는
    차단 시점에만 알 수 있는 값이라 사후 복원이 불가능하고, 억지로 채우면 구
    체제 표본을 신 체제처럼 보이게 만든다. NULL은 "그때는 안 쟀다"는 정직한 표기다.
    """
    try:
        with _conn(TRADES_DB) as conn:
            cols = {r[1] for r in conn.execute(
                "PRAGMA table_info(joint_gate_shadow)")}
            for c, typ in _JGS_EXTRA_COLS:
                if c not in cols:
                    conn.execute(
                        "ALTER TABLE joint_gate_shadow ADD COLUMN %s %s" % (c, typ))
            conn.commit()
        return True
    except Exception:
        return False


def _episode_reduce(rows, gap_min: int):
    """같은 방향 신호가 `gap_min`분 이내로 연속되면 1 에피소드로 병합한다.

    JointGateBlock은 조건이 유지되는 동안 **매 분봉 재차단**하므로 원본 행 수는
    독립 관측치 수가 아니다(실측 2026-07-15~31: 116신호 = 59에피소드, 최대 6연속).
    신호 단위로 t검정을 하면 같은 사건을 여러 번 센 만큼 유의성이 부풀려진다.

    반환: [[row, ...], ...] — 각 에피소드의 행 리스트(시간순).
    """
    eps, cur = [], []
    for r in sorted(rows, key=lambda x: str(x["ts"])):
        if cur:
            try:
                t = datetime.datetime.strptime(str(r["ts"]), _TS_FMT)
                pt = datetime.datetime.strptime(str(cur[-1]["ts"]), _TS_FMT)
                same = (str(r["direction"]) == str(cur[-1]["direction"])
                        and (t - pt).total_seconds() <= gap_min * 60)
            except Exception:
                same = False
            if same:
                cur.append(r)
                continue
            eps.append(cur)
            cur = []
        cur.append(r)
    if cur:
        eps.append(cur)
    return eps


def _mfe_mae(base_ts: str, entry_p: float, is_long: bool, window_min: int,
             high_map: dict, low_map: dict):
    """진입 후 `window_min`분간 최대 유리폭(MFE)·최대 불리폭(MAE)을 pt로 반환.

    ## 왜 counterfactual 루프와 따로 도는가

    resolve 루프는 스톱/TP에 닿으면 `break`로 조기 종료한다. 그런데 이 채널이 답해야
    할 질문은 "그 가상거래가 **얼마나 갈 수 있었나**"이므로 청산 시점과 무관하게
    **창 전체**를 걸어야 한다. 그래서 별도 walk다.

    ## 무엇을 교정하는가 (0731 리포트 §2-E)

    `hyp_pnl_pts`는 차단 신호를 현행 TP1(ATR×0.3~0.5)로 청산했다고 가정해 계산한다.
    그 TP1이 너무 좁다는 것이 같은 리포트 §2-C의 결론이므로, counterfactual이
    **자기 편향적**이다 — 추세일의 차단 비용을 구조적으로 과소평가한다. 실측 예:

        13:16 신호  MFE +17.72 / MAE −0.12  인데  TP1 기준 hyp = +1.01

    MFE를 병기하면 "차단이 이득이었다"는 판정이 TP1 가정에 얼마나 기대고 있는지가
    드러난다. **처방이 아니라 계측**이다 — "TP만 넓히면 된다"는 처방은 §2-E가 이미
    직접 재계산으로 기각했다(대칭 TP 적용 시 −9.87pt로 현행 +4.92pt보다 나쁨).

    거래불능 분봉은 호출부가 `exclude_untradeable=True`로 이미 제외한 맵을 넘긴다
    (체결 불가한 분의 고저로 "갈 수 있었다"를 주장하면 안 된다 — 404차 후속5).

    Returns:
        (mfe, mae) — 둘 다 0 이상의 pt. 분봉이 하나도 없으면 (None, None).
    """
    try:
        base = datetime.datetime.strptime(str(base_ts)[:19], _TS_FMT)
    except (TypeError, ValueError):
        return None, None
    mfe = mae = 0.0
    seen = False
    for m in range(1, int(window_min) + 1):
        mid = base + datetime.timedelta(minutes=m)
        if mid.time() > datetime.time(15, 10):
            break
        key = mid.strftime(_TS_FMT)
        hi, lo = high_map.get(key), low_map.get(key)
        if hi is None or lo is None:
            continue
        seen = True
        fav = (hi - entry_p) if is_long else (entry_p - lo)
        adv = (entry_p - lo) if is_long else (hi - entry_p)
        if fav > mfe:
            mfe = fav
        if adv > mae:
            mae = adv
    if not seen:
        return None, None
    return round(mfe, 4), round(mae, 4)


def _backfill_shadow_mfe(table: str, window_min: int) -> int:
    """이미 resolved=1로 확정된 과거 행의 MFE/MAE를 소급 계산한다. 반환: 채운 행 수.

    resolve 루프는 `resolved=0`만 처리하므로, 컬럼 신설 이전에 확정된 행들은 영원히
    비어 있게 된다. 캠페인 표본 대부분이 그쪽이라 소급이 필수다. 멱등(NULL만 채움).
    """
    if not _ensure_shadow_mfe_columns(table):
        return 0
    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                "SELECT id, ts, direction, entry_price FROM %s "
                "WHERE resolved=1 AND mfe_30m IS NULL AND ts >= ? ORDER BY ts" % table,
                (_campaign_start(),)).fetchall()
    except Exception:
        return 0
    if not rows:
        return 0
    earliest = min(str(r["ts"]) for r in rows)
    _c, high_map, low_map = _load_candle_maps(earliest, exclude_untradeable=True)
    ups = []
    for r in rows:
        mfe, mae = _mfe_mae(r["ts"], float(r["entry_price"] or 0.0),
                            str(r["direction"]) == "LONG", window_min, high_map, low_map)
        if mfe is None:
            continue
        ups.append((mfe, mae, r["id"]))
    if not ups:
        return 0
    try:
        with _conn(TRADES_DB) as conn:
            conn.executemany(
                "UPDATE %s SET mfe_30m=?, mae_30m=? WHERE id=?" % table, ups)
            conn.commit()
    except Exception:
        return 0
    return len(ups)


def _cf_target_unreachable(direction, tp1_price, limits: dict) -> bool:
    """counterfactual 목표가가 그날 가격상한 밖인가 (도달 불가).

    limits: {'UP': 상한가} / {'DOWN': 하한가} — 그날 고착이 확인된 쪽만 들어온다.
    상한 고착일의 LONG TP가 상한 초과, 하한 고착일의 SHORT TP가 하한 미만이면 True.
    """
    try:
        tp = float(tp1_price)
    except (TypeError, ValueError):
        return False
    d = str(direction or "").upper()
    up, dn = limits.get("UP"), limits.get("DOWN")
    if d == "LONG" and up is not None and tp > float(up):
        return True
    if d == "SHORT" and dn is not None and tp < float(dn):
        return True
    return False


# ──────────────────────────────────────────────────────────────
# [25] TP1 보호전환 offset A/B (404차 후속3) — 오프라인 스크립트 위임
# [23] TP1/손절 초기 기하 A/B (403차 P1-6) — 오프라인 스크립트 위임
# ──────────────────────────────────────────────────────────────

def check_replay_regime_fit() -> dict:
    """[MW0601 447차] 사전등록 `replay_regime`이 **이 PC 실측과 맞는가** 자동 점검.

    왜 필요한가 — `tick_era_start`(2026-08-03)와 `pre.protect_mode`(breakeven)는
    **MW0601 TRADE 로그로 캘리브레이션**된 값인데 config는 **단일 값**이라 두 PC가
    공유한다. settings 주석이 "MW0602에서 판정할 때 재확인 필요"라고 이미 경고했지만
    **재확인을 사람이 기억해야 하는 구조**였고, 실제로 두 달 가까이 아무도 안 했다.

    MW0602가 0808 교차검토에서 수동으로 재도출해 **경계가 다르다**는 것을 확인했다
    (`tick_era_start` 07-31 vs 08-03, `pre.protect_mode` atr_profit vs breakeven).
    그 PC는 07-20부터 전 구간 `atr_profit`이라 **pre 구간 자체가 없다.**
    이 함수는 그 수동 작업을 **매주 자동으로** 수행해 불일치를 리포트에 띄운다 —
    새 PC가 붙어도 자동으로 걸린다.

    무엇을 보나 — `protect_mode` 축만 DB로 판정 가능하다(틱 TP 축은 TRADE 로그
    파싱이 필요해 범위 밖). `synthetic_partial_exits`를 경계 전후로 갈라 각 구간의
    **최빈 모드**를 config와 대조한다.

    ⚠ **경계를 자동으로 고치지 않는다.** `replay_regime`은 사전등록 블록이고,
      settings가 "재현이 잘 되는 쪽으로 옮기지 말 것 — 옮기는 순간 [47]은 검증이
      아니라 곡선맞춤이 된다(§9)"고 못 박았다. 이 함수는 **경보만** 낸다.
    ⚠ 소수 예외는 무시한다 — MW0601·MW0602 **양쪽 모두** 2026-08-03 13:25/13:38에
      `breakeven` 2건이 있는데, 같은 시각·같은 방향이라 PC 결함이 아니라 **운영자가
      양 PC 대시보드에서 모드를 장중 변경**한 흔적이다(421차 후속6 "장중변경 로그부재"
      가 등록한 사건). 최빈값 기준이라 이런 소수 예외에 흔들리지 않는다.
    """
    rg = (VALIDATION_CAMPAIGN.get("sim_fidelity_gate", {}) or {}).get("replay_regime") \
        or VALIDATION_CAMPAIGN.get("replay_regime") or {}
    start = str(rg.get("tick_era_start") or "")
    out = {"tick_era_start": start,
           "cfg_pre": (rg.get("pre") or {}).get("protect_mode"),
           "cfg_post": (rg.get("post") or {}).get("protect_mode")}
    if not start:
        out["error"] = "replay_regime 미등록"
        return out
    try:
        with _conn(TRADES_DB) as c:
            rows = c.execute(
                "SELECT substr(ts,1,10) AS d, protect_mode AS m, COUNT(*) AS n "
                "FROM synthetic_partial_exits GROUP BY d, m").fetchall()
    except Exception as e:
        out["error"] = "%s: %s" % (type(e).__name__, e)
        return out

    pre, post = {}, {}
    for r in rows:
        tgt = pre if str(r["d"]) < start else post
        k = str(r["m"] or "(미기록)")
        tgt[k] = tgt.get(k, 0) + int(r["n"] or 0)
    out["obs_pre"], out["obs_post"] = pre, post

    def _dom(d):
        return max(d.items(), key=lambda kv: kv[1])[0] if d else None

    out["dom_pre"], out["dom_post"] = _dom(pre), _dom(post)
    # pre 표본이 아예 없으면 "이 PC엔 pre 구간이 없다" — 불일치가 아니라 정보 부족.
    out["pre_empty"] = not pre
    out["mismatch_pre"] = bool(pre and out["dom_pre"] != out["cfg_pre"])
    out["mismatch_post"] = bool(post and out["dom_post"] != out["cfg_post"])
    out["ok"] = not (out["mismatch_pre"] or out["mismatch_post"])
    return out


def eval_offline_geometry_channels() -> dict:
    """[404차 후속3, 23-B/25] 오프라인 A/B 스크립트 2종을 리포트에 편입한다.

    두 스크립트 모두 라이브 계측이 아니라 저장된 데이터 재생이라 리포트 생성
    시점에 그대로 호출하면 된다. 종전에는 별도 실행해야만 결과가 보여 주간회의
    에서 사실상 아무도 보지 않았다(§23은 403차 신설 이후 리포트 미노출).

    스크립트 실패가 리포트 전체를 죽이면 안 되므로 각각 격리한다.
    """
    out = {}
    for key, mod in (("tp1_geometry_shadow", "scripts.tp1_geometry_shadow"),
                     ("tp1_protect_offset_shadow", "scripts.tp1_protect_offset_shadow"),
                     # [404차 후속10, 3-B] 분위회귀 기반 TP1 거리 A/B. 위 둘과 동일 설계
                     # (오프라인 재생·compute()/summarize() 규약)이라 같은 배관을 쓴다.
                     # ⚠ 이 채널의 verdict는 [3] 본채널 verdict와 무관하다(§9-4).
                     ("quantile_tp_shadow", "scripts.quantile_tp_shadow"),
                     # [MW0601 434차, 46] HurstGate 임계 위치 A/B. 동일 규약
                     # (compute()/summarize(), 오프라인 재생, 라이브 무변경).
                     # ⚠ 이 채널의 verdict는 [3-6] hurst_gate_shadow와 무관하다 —
                     #   그건 "차단된 신호가 벌었을까"(모집단: 차단분), 이건 "임계가
                     #   좋은/나쁜 신호를 가르는가"(모집단: 실제 진입분)로 질문이 다르다.
                     ("hurst_threshold_shadow", "scripts.hurst_threshold_shadow"),
                     # [MW0601 441차, 47-B] TP 체결 오버슈트 감시. 관찰 전용(OBSERVE).
                     # ⚠ [47] 게이트의 targets에 **넣지 않는다** — 이 채널은 게이트가
                     #   쓰는 재생기의 체결 모델 자체를 감시하므로, 게이트가 이것을
                     #   정지시키면 순환 논증이 된다(settings 주석 참조).
                     ("tp_fill_overshoot_watch", "scripts.tp_fill_overshoot_watch")):
        try:
            import importlib
            m = importlib.import_module(mod)
            out[key] = m.summarize(m.compute(_campaign_start()[:10]))
        except Exception as e:
            out[key] = {"verdict": "INSUFFICIENT", "error": "%s: %s" % (type(e).__name__, e)}

    # ── [MW0602 435차, 47] 시뮬레이터 재현충실도 게이트 ─────────────────────────
    # 위 채널들은 전부 같은 재생기 가정(1분봉 / TP2 종료 / TP3·트레일링 미모델링)을
    # 공유한다. 그 가정이 실제를 재현하지 못하면 delta의 **부호까지 뒤집힌다**
    # (432차 후속2 실측: 러너 보정만으로 [25-B] tp2_2.00이 +14.76 → −12.13).
    # 게이트가 SUSPEND면 verdict를 덮어 리포트가 FAIL을 찍지 않게 한다.
    #
    # ⚠ **데이터·사전등록은 그대로 보존한다** — 원 verdict는 `verdict_raw`로 남기고
    #   per_variant 등 수치도 전부 유지한다. 삭제가 아니라 정지다(§9).
    # ⚠ 게이트가 INSUFFICIENT(표본 미달)면 **열어 둔다** — 근거 없이 막지 않는다(313차).
    try:
        import importlib
        _g = importlib.import_module("scripts.sim_fidelity_gate")
        gate = _g.summarize(_g.compute(_campaign_start()[:10]))
    except Exception as e:
        gate = {"verdict": "INSUFFICIENT", "gate": "OPEN",
                "reason": "게이트 실행 실패(미적용): %s: %s" % (type(e).__name__, e)}
    out["_sim_fidelity_gate"] = gate

    # [MW0601 440차] v1/v2 엔진 대조 — **표기 전용**이며 위 gate 판정에 관여하지 않는다.
    # "재생기를 고쳤다"는 주장은 개선폭이 리포트에 남아야 검증 가능하다.
    # 계산이 두 배 드므로 사전등록 스위치로 끌 수 있다(report_both_engines).
    if (VALIDATION_CAMPAIGN.get("sim_fidelity_gate", {}) or {}).get("report_both_engines"):
        try:
            out["_sim_fidelity_engines"] = _g.compare_engines(_campaign_start()[:10])
        except Exception as e:
            out["_sim_fidelity_engines"] = {
                "v1": {"verdict": "ERROR", "reason": "%s: %s" % (type(e).__name__, e)},
                "v2": {"verdict": "ERROR", "reason": "%s: %s" % (type(e).__name__, e)}}

    _cr_gate = VALIDATION_CAMPAIGN.get("sim_fidelity_gate", {}) or {}

    # [MW0601 441차] 중첩 축 — 같은 스크립트 안의 **평행 판정**이라 함께 정지해야 한다.
    # 🔴 기존 결함 수정: settings의 targets 주석은 "[25-B]는 [25] 스크립트 안의 평행
    #    축이라 **같은 키로 함께 정지된다**"고 사전등록해 뒀는데, 실제 코드는 최상위
    #    `verdict`만 덮어써서 [25-B]가 정지를 새어나갔다(0807 리포트에서 [25]는
    #    SUSPENDED인데 [25-B]만 FAIL로 찍힌 것이 그 증거다). 사전등록과 코드를
    #    일치시키는 수정이지 기준 변경이 아니다.
    #    [25-B]는 축이 **TP2 거리** 자체라 "TP2에서 종료" 인공물의 직격 대상이다.
    _SUB_AXES = {"tp1_protect_offset_shadow": ["tp2"]}

    def _suspend(ch, by, reason_text, gate_reason):
        ch["verdict_raw"] = ch.get("verdict")
        ch["verdict"] = "SUSPENDED"
        ch["suspended_by"] = by
        ch["suspend_reason"] = gate_reason
        ch["reason"] = reason_text % (ch.get("verdict_raw"), ch.get("reason", ""))

    def _suspend_channel(key, by, reason_text, gate_reason):
        ch = out.get(key)
        if not isinstance(ch, dict):
            return
        _suspend(ch, by, reason_text, gate_reason)
        for sub in _SUB_AXES.get(key, []):
            sub_ch = ch.get(sub)
            if isinstance(sub_ch, dict) and sub_ch.get("verdict"):
                _suspend(sub_ch, by, reason_text, gate_reason)

    if gate.get("gate") == "SUSPEND":
        for key in (gate.get("targets") or []):
            _suspend_channel(
                key, "sim_fidelity_gate",
                "판정 정지 — 재생기가 실제를 재현하지 못한다(§47). 원 판정 `%s`: %s",
                gate.get("reason", ""))
    elif gate.get("verdict") == "PASS":
        # ── [MW0601 441차] 엔진 커버리지 가드 — PASS의 효력 범위를 제한한다 ──────
        # 435차의 간접 추론("정본이 실패하면 그들도 실패")은 **제한 방향으로만**
        # 타당하다. 역방향은 성립하지 않는다 — 미이관 채널은 정본과 **코드를
        # 공유하지 않기 때문이다**(440차가 고친 것은 exit_replay.py인데 그들은 자체
        # `_simulate`를 쓴다). 근거·분류는 settings의 `replay_engine_targets` 주석 참조.
        # ⚠ 이 가드가 없으면 441차의 게이트 개통이 **검증된 적 없는 계측을 통과시킨다**
        #   — [47]이 막으려던 바로 그 사고를 반대 방향으로 재현하는 셈이다.
        _verified = (set(_cr_gate.get("replay_engine_targets") or [])
                     | set(_cr_gate.get("no_replay_targets") or []))
        for key in (gate.get("targets") or []):
            if key in _verified:
                continue
            _suspend_channel(
                key, "engine_coverage",
                "판정 정지 — **정본 재생기 미이관**(§47 엔진 커버리지, 441차). "
                "[47] 자체는 PASS지만 이 채널은 자체 시뮬(TP1/TP2에서 종료)을 쓰므로 "
                "그 PASS가 여기까지 미치지 않는다. 해제 조건은 재생기 수리가 아니라 "
                "**이 채널을 `exit_replay`로 이관**하는 것이다. 원 판정 `%s`: %s",
                "[47]은 PASS이지만 이 채널은 정본 재생기(`exit_replay`)를 쓰지 않는다 "
                "— 게이트의 PASS가 이 채널의 계측을 검증하지 않는다(441차).")
    return out


def eval_intraday_cv_watch(days: int) -> dict:
    """[404차 후속] intraday 계측 CV(source='intraday') 관찰 — 판정 없음.

    mfe_capture_watch·exit_fill_slippage_watch와 동일한 순수 관찰 채널이다.
    실측(dev_memory/DECISION_LOG.md 404차 후속 §1): 동일 데이터·시드만 다른
    재현 분산이 5m 기준 8.83%p로 EOD 가드 허용폭(2.5%p)의 3.5배 — 이 채널의
    수치로 자동 게이트를 걸면 신호가 아니라 모델 재현 잡음을 판정하게 된다.
    지금은 "intraday cv_acc가 실제로 하락 추세인가"를 판단할 표본을 쌓는
    용도로만 쓴다. 다음 결정(게이트 도입 여부)은 이 관찰이 최소 수 주 쌓인
    뒤 사람이 내린다(§9).
    """
    out = {"verdict": "OBSERVE", "n_samples": 0, "n_days": 0}
    cutoff = max(
        (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(_TS_FMT),
        _campaign_start(),
    )
    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT ts, horizon, old_acc_live, new_cv, distortion, fair_verdict
                     FROM guard_shadow_log
                    WHERE ts >= ? AND source = 'intraday'
                    ORDER BY ts""",
                (cutoff,),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    out["n_samples"] = len(rows)
    out["n_days"] = len({r["ts"][:10] for r in rows})
    if not rows:
        out["reason"] = "표본 없음"
        return out

    by_hz = {}
    for r in rows:
        b = by_hz.setdefault(r["horizon"], {"cv": [], "dist": [], "hold_n": 0})
        b["cv"].append(r["new_cv"])
        if r["distortion"] is not None:
            b["dist"].append(r["distortion"])
        if r["fair_verdict"] == "HOLD":
            b["hold_n"] += 1

    out["by_horizon"] = {
        hz: {
            "n": len(v["cv"]),
            "mean_cv": round(float(np.mean(v["cv"])), 4),
            "std_cv": round(float(np.std(v["cv"])), 4) if len(v["cv"]) > 1 else None,
            "mean_distortion": round(float(np.mean(v["dist"])), 4) if v["dist"] else None,
            # fair_would_hold: "EOD처럼 가드를 걸었다면 통과 못 했을" 비율 — 참고용,
            # 판정 아님(§1 실측: 이 신호 자체가 시드 재현 잡음에 파묻혀 있음).
            "fair_would_hold_rate": round(v["hold_n"] / len(v["cv"]), 4),
        }
        for hz, v in by_hz.items()
    }
    return out


# ──────────────────────────────────────────────────────────────
# [20] BAR_ONLY_RELAX 수용/롤백 감시 (402차 후속)
# ──────────────────────────────────────────────────────────────

# 401차 커밋(2026-07-29 16:26)이 장 마감 후라 발효는 다음 세션부터.
BAR_ONLY_RELAX_EFFECTIVE_DATE = "2026-07-30"


def eval_weight_collapse_watch(days: int) -> dict:
    """BAR_ONLY_RELAX 활성화(401차)의 효과·부작용을 일자 단위로 감시한다.

    fast_reversal_watch·exit_fill_slippage_watch와 동일한 관찰 계열 —
    자동으로 롤백하지 않고 판정 문구만 노출한다(§9 사전등록 원칙).

    효과 지표는 `ensemble_decisions.weight_collapsed` 일별 비율,
    부작용 지표는 완화 대상 호라이즌(3m/5m)의 일별 방향 적중률이다.
    Q3(2026-06-25)가 bar_only로 막으려던 "학습/추론 분포 불일치"가 실제로
    해를 끼치면 그 두 호라이즌 적중률에 먼저 나타난다.

    주의: `weight_collapsed`는 398차(2026-07-28 저녁) 배포분부터 기록되므로,
    그 이전 일자는 컬럼이 NULL이다 — "collapse 0건"이 아니라 "미계측"이라
    집계에서 제외한다. 완화 전 기준선이 단일일(2026-07-29)뿐이라는 뜻이므로
    판정에 min_days를 둔다(313차 원칙).
    """
    cfg = VALIDATION_CAMPAIGN.get("weight_collapse_watch", {})
    out = {"verdict": "OBSERVE", "effective_date": BAR_ONLY_RELAX_EFFECTIVE_DATE}
    min_days = int(cfg.get("min_days", 3))
    target = float(cfg.get("target_ratio", 0.20))
    tol = float(cfg.get("target_tolerance", 0.07))
    ineff = float(cfg.get("ineffective_ratio_min", 0.40))
    over = float(cfg.get("overrelax_ratio_max", 0.05))
    floors = dict(cfg.get("hz_acc_floor", {}))
    streak_need = int(cfg.get("regression_streak_days", 3))
    since = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")

    daily = {}
    try:
        with _conn(PREDICTIONS_DB) as conn:
            for r in conn.execute(
                """SELECT substr(ts,1,10) d, COUNT(*) n,
                          SUM(CASE WHEN weight_collapsed IS NULL THEN 1 ELSE 0 END) n_null,
                          SUM(COALESCE(weight_collapsed,0)) n_wc
                     FROM ensemble_decisions
                    WHERE substr(ts,1,10) >= ?
                    GROUP BY d ORDER BY d""", (since,)
            ):
                n_meas = int(r["n"]) - int(r["n_null"])
                if n_meas <= 0:
                    continue          # 미계측일 — 집계 제외
                daily[r["d"]] = {"n": n_meas, "wc": int(r["n_wc"]),
                                 "ratio": float(r["n_wc"]) / n_meas, "acc": {}}
            for r in conn.execute(
                """SELECT substr(ts,1,10) d, horizon, AVG(CAST(correct AS FLOAT)) acc,
                          COUNT(*) n
                     FROM predictions
                    WHERE substr(ts,1,10) >= ? AND correct IS NOT NULL
                      AND horizon IN ('3m','5m')
                    GROUP BY d, horizon""", (since,)
            ):
                if r["d"] in daily:
                    daily[r["d"]]["acc"][r["horizon"]] = round(float(r["acc"]), 4)
    except Exception as e:
        out["error"] = str(e)
        return out

    pre = {d: v for d, v in daily.items() if d < BAR_ONLY_RELAX_EFFECTIVE_DATE}
    post = {d: v for d, v in daily.items() if d >= BAR_ONLY_RELAX_EFFECTIVE_DATE}
    out["n_days_pre"] = len(pre)
    out["n_days_post"] = len(post)
    out["baseline_ratio"] = (round(sum(v["ratio"] for v in pre.values()) / len(pre), 4)
                             if pre else None)
    out["daily"] = {d: {"ratio": round(v["ratio"], 4), "n": v["n"], "acc": v["acc"]}
                    for d, v in sorted(daily.items())}

    if len(post) < min_days:
        out["reason"] = ("완화 후 계측일 %d일 < 최소 %d일 — 판정 보류 (발효 %s)"
                         % (len(post), min_days, BAR_ONLY_RELAX_EFFECTIVE_DATE))
        out["verdict"] = "INSUFFICIENT"
        return out

    mean_post = sum(v["ratio"] for v in post.values()) / len(post)
    out["post_ratio"] = round(mean_post, 4)

    if mean_post >= ineff:
        effect = "INEFFECTIVE"
    elif mean_post <= over:
        effect = "OVER_RELAXED"
    elif abs(mean_post - target) <= tol:
        effect = "ON_TARGET"
    else:
        effect = "OFF_TARGET"
    out["effect"] = effect

    regressed = []
    for hz, floor in sorted(floors.items()):
        streak = worst = 0
        for d in sorted(post):
            a = post[d]["acc"].get(hz)
            if a is None:
                streak = 0
                continue
            if a < float(floor):
                streak += 1
                worst = max(worst, streak)
            else:
                streak = 0
        if worst >= streak_need:
            regressed.append("%s %d일연속<%.0f%%" % (hz, worst, float(floor) * 100))
    out["regressed"] = regressed

    if regressed:
        out["verdict"] = "ROLLBACK_REVIEW"
        out["recommendation"] = (
            "Q3 분포 불일치 부작용 의심(%s) — `BAR_ONLY_RELAX_ENABLED=False` 롤백을 "
            "주간회의에서 검토(즉시 자동 롤백 아님)" % " / ".join(regressed))
    elif effect == "ON_TARGET":
        out["verdict"] = "ACCEPT"
        out["recommendation"] = "효과 목표 구간·부작용 없음 — 완화 존치 수용"
    elif effect == "INEFFECTIVE":
        out["verdict"] = "INVESTIGATE"
        out["recommendation"] = (
            "완화가 듣지 않음(%.1f%% ≥ %.1f%%) — 원인이 bar age가 아닐 가능성. "
            "롤백보다 원인 재조사 우선" % (mean_post * 100, ineff * 100))
    return out


# ──────────────────────────────────────────────────────────────
# [19] ToxicityGate action="block" counterfactual — resolve + 누적 판정 (신설)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_toxicity_block() -> dict:
    """toxicity_block_shadow(main.py에서 기록) resolve + PASS/FAIL 판정.
    resolve_and_eval_open_gap()과 완전히 동일한 로직 — 대상 테이블만 다르다.

    PASS = 게이트 존치 (차단된 신호가 실제로 손실 방향이었거나 완화 기준 미충족).
    FAIL = 재설계 검토 권고 — block_threshold(0.45)가 그때의 실측 toxicity_score
    분포와 맞는지 재검토 착수(즉시 완화 금지, §9 사전등록 원칙).
    """
    cr = VALIDATION_CAMPAIGN["toxicity_block_shadow"]
    window_min = int(cr.get("cf_window_min", 30))
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM toxicity_block_shadow WHERE resolved = 0 ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    if unresolved:
        earliest = min(r["ts"] for r in unresolved)
        # 체결 시뮬 경로 — 거래불능 분봉 제외 [404차 후속5 / P0-B(a)]
        close_map, high_map, low_map = _load_candle_maps(
            earliest, exclude_untradeable=True)
        now = datetime.datetime.now()
        updates = []
        for r in unresolved:
            base = datetime.datetime.strptime(r["ts"], _TS_FMT)
            if now < base + datetime.timedelta(minutes=window_min + 2):
                continue
            is_long = str(r["direction"]) == "LONG"
            stop_p = float(r["stop_price"] or 0.0)
            tp1_p = float(r["tp1_price"] or 0.0)
            cf_outcome, cf_price = "NEITHER", None
            last_close = None
            for m in range(1, window_min + 1):
                mid = base + datetime.timedelta(minutes=m)
                if mid.time() > datetime.time(15, 10):
                    break
                mid_ts = mid.strftime(_TS_FMT)
                hi = high_map.get(mid_ts)
                lo = low_map.get(mid_ts)
                if hi is None or lo is None:
                    continue
                last_close = close_map.get(mid_ts, last_close)
                if is_long:
                    hit_stop = stop_p > 0 and lo <= stop_p
                    hit_tp = tp1_p > 0 and hi >= tp1_p
                else:
                    hit_stop = stop_p > 0 and hi >= stop_p
                    hit_tp = tp1_p > 0 and lo <= tp1_p
                # 동시 터치 → 보수적으로 STOP 우선 (open_gap_shadow와 동일 관례)
                if hit_stop:
                    cf_outcome, cf_price = "STOP", stop_p
                    break
                if hit_tp:
                    cf_outcome, cf_price = "TP1", tp1_p
                    break
            if cf_price is None:
                if last_close is None:
                    continue  # 분봉 데이터 자체가 없음 — 다음 실행에서 재시도
                cf_price = last_close
            entry_p = float(r["entry_price"])
            # hyp_pnl_pts: (+) = 차단 안 했으면 이득이었다(재설계 근거), (-) = 차단이 손실 회피
            hyp = (cf_price - entry_p) if is_long else (entry_p - cf_price)
            updates.append((cf_outcome, cf_price, round(hyp, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE toxicity_block_shadow
                       SET resolved=1, cf_outcome=?, cf_exit_price=?, hyp_pnl_pts=?
                       WHERE id=?""",
                    updates,
                )
                conn.commit()
            out["resolved_now"] = len(updates)

    try:
        with _conn(TRADES_DB) as conn:
            agg = conn.execute(
                """SELECT COUNT(*) AS n, SUM(hyp_pnl_pts) AS total_hyp,
                          AVG(entry_price) AS avg_price,
                          SUM(CASE WHEN hyp_pnl_pts > 0 THEN 1 ELSE 0 END) AS n_win,
                          SUM(CASE WHEN cf_outcome='STOP' THEN 1 ELSE 0 END) AS n_stop,
                          SUM(CASE WHEN cf_outcome='TP1' THEN 1 ELSE 0 END) AS n_tp1,
                          SUM(CASE WHEN cf_outcome='NEITHER' THEN 1 ELSE 0 END) AS n_neither,
                          AVG(toxicity_score) AS avg_score, AVG(toxicity_score_ma) AS avg_score_ma
                   FROM toxicity_block_shadow WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM toxicity_block_shadow WHERE resolved=0"
            ).fetchone()["n"]
            baseline = conn.execute(
                """SELECT AVG(CASE WHEN COALESCE(net_pnl_krw, pnl_krw) > 0
                                   THEN 1.0 ELSE 0.0 END) AS wr
                   FROM trades WHERE exit_ts IS NOT NULL AND exit_ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_hyp = float(agg["total_hyp"] or 0.0)
    avg_price = float(agg["avg_price"] or 0.0) or 300.0
    win_rate = (int(agg["n_win"] or 0) / n) if n else 0.0
    baseline_wr = (
        float(baseline["wr"]) if baseline and baseline["wr"] is not None else None
    )
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_hyp_pnl_pts": round(total_hyp, 4),
        "win_rate": round(win_rate, 4),
        "baseline_win_rate": round(baseline_wr, 4) if baseline_wr is not None else None,
        "cf_stop": int(agg["n_stop"] or 0),
        "cf_tp1": int(agg["n_tp1"] or 0),
        "cf_neither": int(agg["n_neither"] or 0),
        "avg_toxicity_score": round(float(agg["avg_score"] or 0.0), 4),
        "avg_toxicity_score_ma": round(float(agg["avg_score_ma"] or 0.0), 4),
    })
    if n < int(cr["min_samples"]):
        out["reason"] = "차단 표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out

    cost_pt = _roundtrip_cost_pt(avg_price)
    out["cost_pt"] = round(cost_pt, 4)
    mitigate = (
        total_hyp > cost_pt * 2.0
        and baseline_wr is not None
        and win_rate > baseline_wr
    )
    out["verdict"] = "FAIL" if mitigate else "PASS"
    if mitigate:
        out["recommendation"] = (
            "ToxicityGate block_threshold(0.45) 재검토 권고 — 실측 toxicity_score "
            "분포 근거로 임계값 재보정 착수 (즉시 완화 금지, §9 사전등록 원칙)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# [30]/[31] toxicity 재보정 계열 공통 (MW0601 419차)
# ──────────────────────────────────────────────────────────────

_TOX_RECALIB_GRACE_DAYS = 5  # 배선 직후 "표본 0"을 계측사망으로 오탐하지 않을 유예(달력일)


def _tox_recalib_grace_active() -> bool:
    """배선일로부터 유예기간 안이면 True.

    [357차]가 도입한 no_data(🔴 NO-DATA "계측 점검 필요")는 **소스 적재 자체가
    0인 계측 사망 의심**을 뜻한다. 그런데 신설 채널은 배선 당일에는 정의상 표본이
    0이라, 그대로 두면 첫 주 리포트가 매번 빨간 오탐을 띄운다. 유예기간 안에서는
    verdict를 INSUFFICIENT로만 두고 no_data 플래그를 세우지 않는다 —
    유예가 지나도 0건이면 그때는 **진짜** 배선 문제이므로 no_data가 맞다.
    """
    eff = str(VALIDATION_CAMPAIGN.get(
        "toxicity_recalib_watch", {}).get("effective_date", ""))
    if not eff:
        return False
    try:
        eff_d = datetime.datetime.strptime(eff, "%Y-%m-%d").date()
    except ValueError:
        return False
    return (datetime.date.today() - eff_d).days < _TOX_RECALIB_GRACE_DAYS


# ──────────────────────────────────────────────────────────────
# [30] toxicity_score 재보정(P0) 후 밴드 분포 관찰 (MW0601 419차)
# ──────────────────────────────────────────────────────────────

# [MW0602 424차 후속] **미정의 헬퍼 복구 — 리포트 생성 전체가 죽어 있었다.**
# 419차(`2050437`)가 [30] 채널을 추가하면서 아래 `_row_is_live()`를 호출만 하고
# 정의하지 않았다. `eval_toxicity_recalib_watch()`의 try/except는 DB 조회만 감싸고
# 행 순회는 밖이라, 첫 행에서 NameError가 나면 `build_report()`가 통째로 죽는다.
# 08-03부터 이 상태였으나 `campaign_due()`가 금요일에만 돌아 발현되지 않았다 —
# 422차 후속이 잡은 `[33]` `10%` 미이스케이프와 **같은 주에 생긴 같은 계열의
# 잠복 크래시**이고, 그쪽만 고쳐서는 08-07 리포트가 여전히 안 나온다.
#
# 원 의도는 채널 독스트링에 있다 — "백필 생성 행은 제외한다(418차) — 호가가 전부
# 0이라 spread/cancel 성분이 죽어 밴드 분포를 인위적으로 pass 쪽으로 끌어당긴다."
# 판별자는 `scripts/backfill_features.py:341`이 박는 마커 `feature_quality_score == 0.3`.
#
# ⚠ 허용오차 주의: 여기 입력은 **JSON dict(float64)** 라 0.3이 정확히 일치하지만,
#   같은 마커를 float32 행렬에서 비교하면 틀린다(424차 P0-A — `retrain_eod.py`가
#   `1e-9` 때문에 백필을 한 행도 못 걸렀다). 관례를 하나로 맞춰 1e-6을 쓴다.
_BACKFILL_QUALITY_MARKER = 0.3
_BACKFILL_MARKER_TOL = 1e-6


def _row_is_live(features_json) -> bool:
    """raw_features 한 행이 **라이브 수집분**인가(= 백필 소급 생성이 아닌가)."""
    try:
        d = (json.loads(features_json) if isinstance(features_json, str)
             else features_json)
    except (ValueError, TypeError):
        return False
    if not isinstance(d, dict):
        return False
    q = d.get("feature_quality_score")
    if q is None:
        # 마커 키 자체가 없으면 백필 도입 이전 스키마다 — 라이브로 본다.
        return True
    try:
        return abs(float(q) - _BACKFILL_QUALITY_MARKER) > _BACKFILL_MARKER_TOL
    except (TypeError, ValueError):
        return True


def eval_toxicity_recalib_watch() -> dict:
    """cancel_stress ceiling 재보정 후 toxicity 밴드 분포가 정상 구간으로
    돌아왔는지 raw_features 실측으로 확인한다.

    계기: 380차가 cancel_churn_ratio ceiling을 0.08로 잠정 설정하고 코드 주석에
    "라이브 섀도 관찰 후 재보정 필요"라고 예고했으나 실행되지 않았다. 라이브
    실측(2026-07-24~07-31, n=2,229)에서 cancel_churn_ratio p50=0.2649로 ceiling의
    3.3배 — **초과율 100%** 라 toxicity_cancel_stress가 전 분봉 1.0으로 포화했고,
    가중 0.20짜리 성분이 score에 상수 +0.20을 더하는 죽은 항이 돼 있었다
    (중앙값 score 0.3475의 58%). 그 오프셋 때문에 밴드 분포가 380차 설계목표에서
    완전히 이탈 — block 23.3% / reduce 76.4% / **pass 0.27%**.

    419차가 ceiling을 실측 p99인 0.42로 재보정했고, 이 채널이 그 결과를 매주 잰다.
    밴드 판정식은 ToxicityGate.evaluate()·ToxicityCalculator.update()와 동일하게
    재현한다(score/score_ma/spread_ticks OR 조건).

    백필 생성 행은 제외한다(418차) — 호가가 전부 0이라 spread/cancel 성분이 죽어
    밴드 분포를 인위적으로 pass 쪽으로 끌어당긴다.
    """
    cr = VALIDATION_CAMPAIGN.get("toxicity_recalib_watch", {})
    eff = str(cr.get("effective_date", ""))
    out = {"verdict": "INSUFFICIENT", "effective_date": eff,
           "cancel_churn_ceiling": None}
    try:
        from config.settings import TOXICITY_CANCEL_CHURN_CEILING as _ceil
        out["cancel_churn_ceiling"] = float(_ceil)
    except Exception:
        pass

    try:
        with _conn(RAW_DATA_DB) as conn:
            rows = conn.execute(
                "SELECT ts, features FROM raw_features WHERE ts >= ? ORDER BY ts",
                (eff,),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        # reason을 함께 세팅해야 요약표가 빈 수치를 0%로 렌더링하지 않는다.
        out["reason"] = "raw_features 조회 실패: %s" % e
        out["no_data"] = True
        return out

    n_block = n_reduce = n_pass = 0
    n_cancel_sat = 0
    scores, ratios = [], []
    for r in rows:
        if not _row_is_live(r["features"]):
            continue
        try:
            d = json.loads(r["features"])
        except (ValueError, TypeError):
            continue
        s = d.get("toxicity_score")
        if s is None:
            continue
        s = float(s)
        ma = float(d.get("toxicity_score_ma") or 0.0)
        spt = float(d.get("spread_ticks") or 0.0)
        cs = d.get("toxicity_cancel_stress")
        if cs is not None:
            if float(cs) >= 0.999:
                n_cancel_sat += 1
        cr_ratio = d.get("cancel_churn_ratio")
        if cr_ratio is not None:
            ratios.append(float(cr_ratio))
        scores.append(s)
        # ToxicityGate.evaluate()와 동일 판정식
        if s >= 0.45 or ma >= 0.40:
            n_block += 1
        elif s >= 0.28 or ma >= 0.25 or spt >= 8.0:
            n_reduce += 1
        else:
            n_pass += 1

    n = n_block + n_reduce + n_pass
    out["n_bars"] = n
    if n == 0:
        _grace = _tox_recalib_grace_active()
        out["no_data"] = not _grace
        out["reason"] = "재보정일(%s) 이후 라이브 분봉 0건%s" % (
            eff or "—",
            " — 배선 직후 유예 중(정상)" if _grace else " — 유예 경과, 배선 점검 필요")
        return out

    out.update({
        "block_share": round(n_block / n, 4),
        "reduce_share": round(n_reduce / n, 4),
        "pass_share": round(n_pass / n, 4),
        "cancel_sat_share": round(n_cancel_sat / n, 4),
        "score_p50": round(float(np.percentile(scores, 50)), 4),
        "score_p90": round(float(np.percentile(scores, 90)), 4),
    })
    if ratios:
        out["churn_p50"] = round(float(np.percentile(ratios, 50)), 4)
        out["churn_p99"] = round(float(np.percentile(ratios, 99)), 4)

    min_bars = int(cr.get("min_bars", 1500))
    if n < min_bars:
        out["reason"] = "재보정 후 분봉 부족 (%d < %d) — 판정 보류" % (n, min_bars)
        return out

    lo = float(cr.get("pass_share_lo", 0.15))
    hi = float(cr.get("pass_share_hi", 0.92))
    bmax = float(cr.get("block_share_max", 0.12))
    smax = float(cr.get("cancel_sat_max", 0.30))
    fails = []
    if not (lo <= out["pass_share"] <= hi):
        fails.append("pass %.1f%% ∉ [%.0f%%, %.0f%%]" % (
            out["pass_share"] * 100, lo * 100, hi * 100))
    if out["block_share"] > bmax:
        fails.append("block %.1f%% > %.0f%%" % (out["block_share"] * 100, bmax * 100))
    if out["cancel_sat_share"] > smax:
        fails.append("cancel포화 %.1f%% > %.0f%%" % (
            out["cancel_sat_share"] * 100, smax * 100))

    out["verdict"] = "FAIL" if fails else "PASS"
    if fails:
        out["reason"] = " / ".join(fails)
        out["recommendation"] = (
            "ToxicityGate 임계값(block 0.45 / reduce 0.28) 재선정을 주간회의 안건으로 "
            "올릴 것 — **자동 변경 금지**(임계값은 전 채널 판정에 영향, §3 원칙대로 "
            "사유를 DECISION_LOG.md에 기록해야 함)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# [31] ToxicityGate reduce 밴드 연속 배수 섀도 (MW0601 419차)
# ──────────────────────────────────────────────────────────────

def eval_toxicity_reduce_mult_shadow() -> dict:
    """상수 0.7 대신 연속 배수를 썼다면 수량이 달라졌을지를 실체결 진입에서 잰다.

    exec_1m_shadow와 동일 계열 — 실제 체결된 진입에 태그만 붙이므로 counterfactual
    가격 시뮬레이션이 불필요하다(toxicity_reduce_shadow 테이블, ts로 trades 조인).

    이 채널의 1차 질문은 손익이 아니라 **실효성**이다. reduce 밴드에서
    toxicity_score는 단조 등급성을 갖는데(라이브 n=1,614에서 향후 스프레드
    Spearman rho=+0.319, t=13.48) 상수 0.7이 그걸 전량 폐기한다. 다만 main.py의
    사이징 체인이 매 단계 max(1, round())로 양자화하고 실체결 수량이 1~2계약에
    묶여 있어, 연속화해도 수량이 실제로 바뀌지 않을 가능성이 크다 — 그렇다면
    코드 복잡도만 늘리는 변경이므로 하지 않는 것이 옳다.

    PASS = 현행 상수 유지(수량 상이 비율이 임계 미만 — 실적용 실익 없음)
    FAIL = 실적용 검토(앵커 재도출 + 양자화 체인 단일화를 함께 안건화)
    """
    cr = VALIDATION_CAMPAIGN.get("toxicity_reduce_mult_shadow", {})
    out = {"verdict": "INSUFFICIENT"}

    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                "SELECT * FROM toxicity_reduce_shadow ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        # 테이블 미생성(배선 후 첫 기동 전)도 여기로 온다 — reason을 세팅해야
        # 요약표가 빈 수치를 "수량상이 0.0%"로 잘못 렌더링하지 않는다.
        out["reason"] = "toxicity_reduce_shadow 조회 실패: %s" % e
        out["no_data"] = not _tox_recalib_grace_active()
        return out

    n = len(rows)
    out["n_samples"] = n
    if n == 0:
        _grace = _tox_recalib_grace_active()
        out["no_data"] = not _grace
        out["reason"] = "reduce 밴드 체결 진입 0건 — %s" % (
            "계측 배선 후 첫 거래 대기(유예 중, 정상)" if _grace
            else "유예 경과, 배선 점검 필요")
        return out

    n_div = sum(1 for r in rows
                if float(r["qty_after_shadow"] or 0) != float(r["qty_after_applied"] or 0))
    shadows = [float(r["tox_size_shadow"] or 0.0) for r in rows]
    out.update({
        "divergent_qty_n": n_div,
        "divergent_qty_share": round(n_div / n, 4),
        "shadow_mult_min": round(min(shadows), 4),
        "shadow_mult_p50": round(float(np.percentile(shadows, 50)), 4),
        "shadow_mult_max": round(max(shadows), 4),
        # 노출 중립성 점검 — 설계상 평균이 0.70 근처여야 한다(설계 근거는 settings 주석).
        "shadow_mult_mean": round(sum(shadows) / n, 4),
        "applied_mult_const": 0.7,
    })

    # [MW0601 421차] 앵커 신선도 — 앵커를 도출한 ceiling과 현행 ceiling이 다르면
    # 밴드 분포가 또 이동했다는 뜻이라 shadow_mult_mean 해석이 무의미해진다.
    # 420차 tox_regime_date 불일치 감지와 동일 취지 — **자동 수정은 하지 않는다**.
    from config.settings import TOXICITY_CANCEL_CHURN_CEILING as _cur_ceil
    _cfg = VALIDATION_CAMPAIGN.get("toxicity_reduce_mult_shadow", {}) or {}
    _anchor_ceil = _cfg.get("anchor_ceiling")
    if _anchor_ceil is not None and abs(
            float(_anchor_ceil) - float(_cur_ceil)) > 1e-9:
        out["anchor_stale"] = (
            "⚠ 앵커 낡음 — anchor_ceiling=%s 로 도출했으나 현행 "
            "TOXICITY_CANCEL_CHURN_CEILING=%s. scripts/"
            "toxicity_reduce_mult_anchor_rederive.py 재실행 후 HI/LO와 "
            "anchor_ceiling/anchor_date를 함께 갱신할 것."
            % (_anchor_ceil, _cur_ceil))
    out["anchor_date"] = _cfg.get("anchor_date", "—")

    # 실현 손익 병기 — trades와 entry_ts 조인(판정에는 쓰지 않는다, 참고용).
    # 이 테이블은 상한 없이 누적되므로 IN 절을 청크로 쪼갠다 — SQLite 기본
    # SQLITE_MAX_VARIABLE_NUMBER(999)를 넘으면 "too many SQL variables"로 죽는다.
    try:
        ts_list = [str(r["ts"]) for r in rows]
        pnl_map = {}
        with _conn(TRADES_DB) as conn:
            for i in range(0, len(ts_list), 500):
                chunk = ts_list[i:i + 500]
                qmarks = ",".join("?" * len(chunk))
                for t in conn.execute(
                    "SELECT entry_ts, SUM(COALESCE(net_pnl_krw,0)) AS pnl "
                    "FROM trades WHERE entry_ts IN (%s) AND %s GROUP BY entry_ts"
                    % (qmarks, _NOT_GHOST_SQL),
                    chunk,
                ).fetchall():
                    pnl_map[str(t["entry_ts"])] = float(t["pnl"] or 0.0)
        matched = [pnl_map[str(r["ts"])] for r in rows if str(r["ts"]) in pnl_map]
        if matched:
            out["matched_trades"] = len(matched)
            out["total_pnl_krw"] = round(sum(matched), 0)
    except Exception as e:
        out["pnl_join_error"] = str(e)

    min_n = int(cr.get("min_samples", 20))
    if n < min_n:
        out["reason"] = "표본 부족 (%d < %d) — 판정 보류" % (n, min_n)
        return out

    thr = float(cr.get("divergence_min_share", 0.20))
    diverges = out["divergent_qty_share"] >= thr
    out["verdict"] = "FAIL" if diverges else "PASS"
    if diverges:
        out["recommendation"] = (
            "연속 배수 실적용 검토 — 단 즉시 전환 금지. (a) 앵커를 재보정 후 분포로 "
            "재도출하고([30] 채널) (b) 사이징 체인의 8단 max(1,round()) 양자화 단일화를 "
            "함께 안건화할 것 (§9 사전등록 원칙)"
        )
    else:
        out["reason"] = (
            "수량 상이 %.1f%% < %.0f%% — 양자화에 흡수돼 실적용 실익 없음(현행 상수 유지)"
            % (out["divergent_qty_share"] * 100, thr * 100)
        )
    return out


# ──────────────────────────────────────────────────────────────
# [34] meta "size 0" 무시 관찰 (MW0601 422차 후속)
# ──────────────────────────────────────────────────────────────

def eval_meta_size_zero_shadow() -> dict:
    """메타 모델이 size 0("베팅하지 마라")을 냈는데 진입까지 간 신호의 손익.

    `_make_result()`는 `conf < 0.5`에서 size_multiplier를 0.0으로 낸다. conf는
    4급 품질레이블의 기대값이고 a=0.5에서 정확히 0.5가 되므로(고신뢰비중 h와 무관),
    size 0은 "이 맥락에서 호라이즌 예측기 풀이 동전던지기보다 못하다"는 뜻이다.

    그런데 액션 밴드가 그 0을 덮는다 — reduce는 `or 0.5`, take는 `max(0.9, ...)`.
    take 쪽 왜곡(0.0→0.9)이 reduce(0.0→0.5)보다 크므로 **밴드별로 분리 집계**한다.
    합산하면 take의 큰 왜곡이 reduce에 희석된다.

    PASS = 현행 유지(클램프·폴백이 해롭지 않음)
    FAIL = "안 B"(raw==0 → action skip 강등)를 주간회의 안건화 — 자동 전환 금지
    """
    cr = VALIDATION_CAMPAIGN.get("meta_size_zero_shadow", {})
    out = {"verdict": "INSUFFICIENT", "bands": {}}
    eff = str(cr.get("effective_date", "") or "")

    try:
        with _conn(PREDICTIONS_DB) as conn:
            rows = conn.execute(
                """SELECT ts, meta_action, meta_size_mult, meta_size_raw,
                          toxicity_action, entry_qty
                     FROM ensemble_decisions
                    WHERE entry_executed = 1
                      AND meta_action IS NOT NULL AND meta_action != 'skip'
                      AND ts >= ?
                    ORDER BY ts""",
                (eff,),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        # 컬럼 미생성(422차 후속 배선 전 기동) / 테이블 없음도 여기로 온다.
        out["reason"] = "ensemble_decisions.meta_size_raw 조회 실패: %s" % e
        out["no_data"] = True
        return out

    # 계측 이전 행은 raw가 NULL — 판정 모집단에서 제외하되 건수는 정직하게 표기한다.
    unmeasured = [r for r in rows if r["meta_size_raw"] is None]
    measured = [r for r in rows if r["meta_size_raw"] is not None]
    out["unmeasured"] = len(unmeasured)
    out["measured"] = len(measured)

    zero = [r for r in measured if abs(float(r["meta_size_raw"])) < 1e-9]
    out["n"] = len(zero)
    if not measured:
        out["reason"] = (
            "계측 표본 0건 — meta_size_raw 배선(%s) 이후 진입이 아직 없다" % eff
        )
        out["no_data"] = True
        return out

    out["zero_share"] = round(len(zero) / float(len(measured)), 4)

    # trades 조인 — 포지션 단위(진입은 중복 발화가 없어 에피소드 병합 불필요)
    # [MW0602 427차 후속] 종전 `substr(entry_ts,1,16)` 분 단위 정확 조인은
    # **체결이 분 경계를 넘으면 그 건을 통째로 잃는다**(캠페인 전수 실측 19/100건,
    # 체결 초 `:00~:09`). 이 채널은 effective_date가 늦어 아직 발현만 안 했을 뿐
    # 같은 결함이었다 — [39]가 실제로 그것에 걸려 발견됐다.
    # 공유 헬퍼가 결정 ts → 체결 entry_ts를 T/T-1 + 방향 일치로 풀어 준다.
    pnl_map = {}
    try:
        with _conn(TRADES_DB) as tconn:
            _by_entry = {str(t["entry_ts"]): float(t["pnl"] or 0.0) for t in tconn.execute(
                """SELECT entry_ts, SUM(net_pnl_krw) pnl
                     FROM trades WHERE entry_ts >= ? GROUP BY entry_ts""", (eff,))}
        for _ets, _d, _off in _entry_decision_pairs(eff)[0]:
            if _ets in _by_entry:
                pnl_map[str(_d["ts"])] = _by_entry[_ets]
    except Exception as e:
        out["pnl_join_error"] = str(e)

    def _band(rs):
        m = [(r, pnl_map[str(r["ts"])]) for r in rs if str(r["ts"]) in pnl_map]
        if not m:
            return {"n": len(rs), "matched": 0}
        v = [p for _, p in m]
        days = sorted({str(r["ts"])[:10] for r, _ in m})
        by_day = {}
        for r, p in m:
            by_day[str(r["ts"])[:10]] = by_day.get(str(r["ts"])[:10], 0.0) + p
        return {
            "n": len(rs), "matched": len(m),
            "total_pnl_krw": round(sum(v), 0),
            "avg_pnl_krw": round(sum(v) / len(v), 0),
            "win_rate": round(sum(1 for x in v if x > 0) / float(len(v)), 4),
            "days": len(days),
            "neg_days": sum(1 for x in by_day.values() if x < 0),
        }

    for band in ("reduce", "take"):
        out["bands"][band] = _band([r for r in zero if str(r["meta_action"]) == band])
    out["bands"]["_합계"] = _band(zero)

    agg = out["bands"]["_합계"]
    n_matched = int(agg.get("matched", 0) or 0)
    n_days = int(agg.get("days", 0) or 0)
    min_n = int(cr.get("min_samples", 20))
    min_d = int(cr.get("min_days", 5))
    if n_matched < min_n or n_days < min_d:
        out["reason"] = (
            "표본 부족 (매칭 %d/%d건, 거래일 %d/%d) — 판정 보류%s"
            % (n_matched, min_n, n_days, min_d,
               ("  ※ 미계측 %d건 제외" % out["unmeasured"]) if out["unmeasured"] else "")
        )
        return out

    # FAIL 2조건: 누적 손익이 왕복비용×2를 넘는 손실 AND 승률이 기준선 미만
    avg_price = 0.0
    try:
        with _conn(TRADES_DB) as tconn:
            r = tconn.execute(
                "SELECT AVG(entry_price) p FROM trades WHERE entry_ts >= ?", (eff,)
            ).fetchone()
            avg_price = float((r["p"] if r else 0.0) or 0.0)
    except Exception:
        pass
    cost_pt = _roundtrip_cost_pt(avg_price) if avg_price > 0 else 0.0
    # 미니선물(A05) 기준 — 이 시스템의 거래 대상. 왕복비용×2를 손실 문턱으로 쓴다
    # (다른 채널이 pt로 쓰는 `왕복비용×2` 규약을 원 단위로 옮긴 것).
    cost_krw = cost_pt * 2.0 * MINI_FUTURES_PT_VALUE * n_matched
    out["fail_threshold_krw"] = round(-cost_krw, 0)

    total = float(agg.get("total_pnl_krw", 0.0) or 0.0)
    wr = float(agg.get("win_rate", 0.0) or 0.0)
    base_wr = float(cr.get("baseline_win_rate", 0.50))
    if total < -cost_krw and wr < base_wr:
        out["verdict"] = "FAIL"
        out["recommendation"] = (
            "\"안 B\"(meta_size_raw==0 → action을 skip으로 강등)를 주간회의 안건화 — "
            "**자동 전환 금지**. 액션 축 변경이라 라이브 진입 동작이 바뀐다. "
            "상정 시 교란 (a)recent_accuracy 자기상관 (b)퇴역 30m·FLAT 혼입 "
            "(c)class_weight='balanced' 를 함께 볼 것 (settings [34] 주석)"
        )
    else:
        out["verdict"] = "PASS"
        out["reason"] = (
            "누적 %s원 / 승률 %.1f%% — FAIL 2조건(손익 < %s원 AND 승률 < %.0f%%) 미충족, 현행 유지"
            % (format(int(total), ","), wr * 100,
               format(int(-cost_krw), ","), base_wr * 100)
        )
    return out


# ──────────────────────────────────────────────────────────────
# [18] RegimeExhaustionGate counterfactual — resolve + 판정 (379차)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_regime_exhaustion() -> dict:
    """regime_exhaustion_shadow(main.py에서 기록) resolve + 판정.

    hurst_gate_shadow·open_gap_shadow와 resolve 메커니즘은 동일(발동 시점의
    가상 진입가·스톱·TP1이 cf_window_min 이내에 무엇에 먼저 닿았는지)이나,
    이 채널은 "게이트가 이미 차단 중인데 그게 옳았나"가 아니라 "탈진 반전
    가설 자체가 유효한가"를 묻는 것이라 PASS/FAIL 의미가 반대로 뒤집힌다:

    hyp_pnl_pts = 신호 방향(연장·추격 방향)으로 갔을 때의 결과.
      (+) = 신호 방향이 맞았음(탈진이 아니라 진짜 추세 지속) → 가설 반증 쪽.
      (-) = 신호 방향이 반전(스톱)에 먼저 닿음 → "탈진 반전" 가설 지지.

    SUPPORTS_GATE = 누적 hyp_pnl_pts가 유의하게 음수(왕복비용의 2배 이상 손실)
      — 이 방향으로 계속 갔으면 평균적으로 손해였다는 뜻. REGIME_EXHAUSTION_
      GATE_ENABLED 전환(등급 강등) 또는 3-2 제안(반대방향 신규 시그널)의 근거로
      쌓인다. 단 이 리포트는 권고만 — 즉시 자동 전환 없음(§9 사전등록 원칙).
    REJECTS_GATE = 누적 hyp_pnl_pts가 유의하게 양수 — 신호가 오히려 방향을
      맞췄다는 뜻. 가설 기각, 게이트 개발 중단 권고.
    OBSERVE = 표본은 충분하나 방향이 애매(왕복비용 2배 미만) — 계속 관찰.
    """
    cr = VALIDATION_CAMPAIGN["regime_exhaustion_watch"]
    window_min = int(cr.get("cf_window_min", 30))
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM regime_exhaustion_shadow WHERE resolved = 0 ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    if unresolved:
        earliest = min(r["ts"] for r in unresolved)
        # 체결 시뮬 경로 — 거래불능 분봉 제외 [404차 후속5 / P0-B(a)]
        close_map, high_map, low_map = _load_candle_maps(
            earliest, exclude_untradeable=True)
        now = datetime.datetime.now()
        updates = []
        for r in unresolved:
            base = datetime.datetime.strptime(r["ts"], _TS_FMT)
            if now < base + datetime.timedelta(minutes=window_min + 2):
                continue
            is_long = str(r["direction"]) == "LONG"
            stop_p = float(r["stop_price"] or 0.0)
            tp1_p = float(r["tp1_price"] or 0.0)
            cf_outcome, cf_price = "NEITHER", None
            last_close = None
            for m in range(1, window_min + 1):
                mid = base + datetime.timedelta(minutes=m)
                if mid.time() > datetime.time(15, 10):
                    break
                mid_ts = mid.strftime(_TS_FMT)
                hi = high_map.get(mid_ts)
                lo = low_map.get(mid_ts)
                if hi is None or lo is None:
                    continue
                last_close = close_map.get(mid_ts, last_close)
                if is_long:
                    hit_stop = stop_p > 0 and lo <= stop_p
                    hit_tp = tp1_p > 0 and hi >= tp1_p
                else:
                    hit_stop = stop_p > 0 and hi >= stop_p
                    hit_tp = tp1_p > 0 and lo <= tp1_p
                if hit_stop:
                    cf_outcome, cf_price = "STOP", stop_p
                    break
                if hit_tp:
                    cf_outcome, cf_price = "TP1", tp1_p
                    break
            if cf_price is None:
                if last_close is None:
                    continue
                cf_price = last_close
            entry_p = float(r["entry_price"])
            hyp = (cf_price - entry_p) if is_long else (entry_p - cf_price)
            updates.append((cf_outcome, cf_price, round(hyp, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE regime_exhaustion_shadow
                       SET resolved=1, cf_outcome=?, cf_exit_price=?, hyp_pnl_pts=?
                       WHERE id=?""",
                    updates,
                )
                conn.commit()
            out["resolved_now"] = len(updates)

    try:
        with _conn(TRADES_DB) as conn:
            agg = conn.execute(
                """SELECT COUNT(*) AS n, SUM(hyp_pnl_pts) AS total_hyp,
                          AVG(entry_price) AS avg_price,
                          SUM(CASE WHEN cf_outcome='STOP' THEN 1 ELSE 0 END) AS n_stop,
                          SUM(CASE WHEN cf_outcome='TP1' THEN 1 ELSE 0 END) AS n_tp1,
                          SUM(CASE WHEN cf_outcome='NEITHER' THEN 1 ELSE 0 END) AS n_neither,
                          AVG(ext_atr_60m) AS avg_ext60m, AVG(hurst) AS avg_hurst,
                          SUM(chase_failed) AS n_chase_failed,
                          SUM(countertrend_failed) AS n_ctr_failed
                   FROM regime_exhaustion_shadow WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM regime_exhaustion_shadow WHERE resolved=0"
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_hyp = float(agg["total_hyp"] or 0.0)
    avg_price = float(agg["avg_price"] or 0.0) or 300.0
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_hyp_pnl_pts": round(total_hyp, 4),
        "cf_stop": int(agg["n_stop"] or 0),
        "cf_tp1": int(agg["n_tp1"] or 0),
        "cf_neither": int(agg["n_neither"] or 0),
        "avg_ext_atr_60m": round(float(agg["avg_ext60m"] or 0.0), 3),
        "avg_hurst": round(float(agg["avg_hurst"] or 0.0), 3),
        "n_chase_failed": int(agg["n_chase_failed"] or 0),
        "n_countertrend_failed": int(agg["n_ctr_failed"] or 0),
    })
    if n < int(cr["min_samples"]):
        out["verdict"] = "INSUFFICIENT"
        out["reason"] = "표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out

    cost_pt = _roundtrip_cost_pt(avg_price)
    out["cost_pt"] = round(cost_pt, 4)
    if total_hyp < -cost_pt * 2.0:
        out["verdict"] = "SUPPORTS_GATE"
        out["recommendation"] = (
            "탈진 반전 가설 지지 — REGIME_EXHAUSTION_GATE_ENABLED 전환(등급 강등) 또는 "
            "반대방향 신규 진입 시그널(3-2 제안) 개발을 주간회의에서 검토 (§9 사전등록 원칙 — "
            "즉시 자동 전환 금지)"
        )
    elif total_hyp > cost_pt * 2.0:
        out["verdict"] = "REJECTS_GATE"
        out["recommendation"] = "가설 기각 — 신호 방향이 오히려 우세, 게이트 개발 중단 권고"
    else:
        out["verdict"] = "OBSERVE"
    return out


# ──────────────────────────────────────────────────────────────
# [10] TP2 홀드 A/B counterfactual — resolve + 누적 판정 (361차)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_tp2_hold() -> dict:
    """tp2_hold_shadow(main.py에서 기록) resolve + PASS/FAIL 판정.

    0720 정기점검 "TP3 도달 0건" 딥다이브 결과: 원인은 트레일링 폭이 아니라
    qty=2 스테이지 배분(TP2에서 잔량 1계약 전량 종료, TP3 몫이 항상 0)이었음.
    이 채널은 그 순간 "홀드했다면 TP3/트레일링까지 갔을 때 어땠을지"를 당일
    15:10까지 분봉으로 사후 시뮬레이션한다. 트레일링 티어는
    strategy.position.position_tracker.compute_trailing_stop_tier()를 그대로
    재사용(라이브 로직과 동일 소스, 드리프트 방지). ATR은 훅 시점 값을 고정
    사용(단순화 — 봉별 ATR 재계산은 하지 않음), 가상 트레일링 anchor는 TP1 이후
    상태를 정확히 재현하지 않고 TP2 시점부터 entry_price 기준으로 새로 시작한다
    (둘 다 §3-5류 채널들의 "고정 스톱/TP 기준" 단순화와 동일 원칙).

    PASS = 현행(TP2 전량종료) 유지 — 홀드가 평균적으로 손해.
    FAIL = 재배분(TP1만 정리 후 TP3/트레일링까지 보유) 채택 검토 권고
           (즉시 코드 변경 아님 — 주간회의 수동 결정, §9 사전등록 원칙).
    """
    cr = VALIDATION_CAMPAIGN["tp2_hold_shadow"]
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM tp2_hold_shadow WHERE resolved = 0 ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    if unresolved:
        earliest = min(r["ts"] for r in unresolved)
        # 체결 시뮬 경로 — 거래불능 분봉 제외 [404차 후속5 / P0-B(a)]
        close_map, high_map, low_map = _load_candle_maps(
            earliest, exclude_untradeable=True)
        now = datetime.datetime.now()
        updates = []
        for r in unresolved:
            base = datetime.datetime.strptime(r["ts"], _TS_FMT)
            day_end = base.replace(hour=15, minute=10, second=0, microsecond=0)
            if now < day_end + datetime.timedelta(minutes=2):
                continue  # 당일 장 마감까지 아직 안 지남 — 다음 실행에서 재시도
            is_long = str(r["direction"]) == "LONG"
            direction = "LONG" if is_long else "SHORT"
            entry_p = float(r["entry_price"])
            tp3_p = float(r["tp3_price"] or 0.0)
            atr = float(r["atr_at_hook"] or 0.0)

            anchor = entry_p
            stop = float(r["stop_price_at_hook"] or entry_p)
            cf_outcome, cf_price, cf_minutes = None, None, 0
            last_close, last_m = None, 0
            m = 0
            while True:
                m += 1
                mid = base + datetime.timedelta(minutes=m)
                if mid.time() > datetime.time(15, 10):
                    break
                mid_ts = mid.strftime(_TS_FMT)
                hi = high_map.get(mid_ts)
                lo = low_map.get(mid_ts)
                cl = close_map.get(mid_ts)
                if hi is None or lo is None or cl is None:
                    continue
                last_close, last_m = cl, m
                # 라이브와 동일하게 매분 종가로만 트레일링 1회 갱신
                anchor, stop = compute_trailing_stop_tier(
                    entry_p, direction, atr, cl, anchor, stop
                )
                hit_tp3 = tp3_p > 0 and (hi >= tp3_p if is_long else lo <= tp3_p)
                hit_stop = lo <= stop if is_long else hi >= stop
                # 동시 터치 → 보수적으로 STOP 우선 (기존 섀도 채널들과 동일 관례)
                if hit_stop:
                    cf_outcome, cf_price, cf_minutes = "TRAIL_STOP", stop, m
                    break
                if hit_tp3:
                    cf_outcome, cf_price, cf_minutes = "TP3", tp3_p, m
                    break
            if cf_price is None:
                if last_close is None:
                    continue  # 분봉 데이터 자체가 없음 — 다음 실행에서 재시도
                cf_outcome, cf_price, cf_minutes = "FORCE_EXIT", last_close, last_m
            tp2_p = float(r["tp2_price"])
            # hyp_pnl_pts: (+) = 홀드가 이득(재배분 근거), (-) = TP2 조기청산이 나았음
            hyp = (cf_price - tp2_p) if is_long else (tp2_p - cf_price)
            updates.append((cf_outcome, cf_price, cf_minutes, round(hyp, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE tp2_hold_shadow
                       SET resolved=1, cf_outcome=?, cf_exit_price=?,
                           cf_hold_minutes=?, hyp_pnl_pts=?
                       WHERE id=?""",
                    updates,
                )
                conn.commit()
            out["resolved_now"] = len(updates)

    try:
        with _conn(TRADES_DB) as conn:
            agg = conn.execute(
                """SELECT COUNT(*) AS n, SUM(hyp_pnl_pts) AS total_hyp,
                          AVG(entry_price) AS avg_price,
                          SUM(CASE WHEN hyp_pnl_pts > 0 THEN 1 ELSE 0 END) AS n_win,
                          SUM(CASE WHEN cf_outcome='TP3' THEN 1 ELSE 0 END) AS n_tp3,
                          SUM(CASE WHEN cf_outcome='TRAIL_STOP' THEN 1 ELSE 0 END) AS n_stop,
                          SUM(CASE WHEN cf_outcome='FORCE_EXIT' THEN 1 ELSE 0 END) AS n_force
                   FROM tp2_hold_shadow WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM tp2_hold_shadow WHERE resolved=0"
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_hyp = float(agg["total_hyp"] or 0.0)
    avg_price = float(agg["avg_price"] or 0.0) or 300.0
    win_rate = (int(agg["n_win"] or 0) / n) if n else 0.0
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_hyp_pnl_pts": round(total_hyp, 4),
        "win_rate": round(win_rate, 4),
        "cf_tp3": int(agg["n_tp3"] or 0),
        "cf_trail_stop": int(agg["n_stop"] or 0),
        "cf_force_exit": int(agg["n_force"] or 0),
    })
    if n < int(cr["min_samples"]):
        out["reason"] = "TP2 전량종료 표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out

    cost_pt = _roundtrip_cost_pt(avg_price)
    out["cost_pt"] = round(cost_pt, 4)
    adopt = total_hyp > cost_pt * 2.0
    out["verdict"] = "FAIL" if adopt else "PASS"
    if adopt:
        out["recommendation"] = (
            "qty=2 스테이지 재배분(TP1만 정리 후 TP3/트레일링까지 보유) 채택 검토 "
            "— 주간회의 수동 결정 (§9 사전등록 원칙)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# [11] qty=1 손실1차(Loss Tier1) 조기청산 counterfactual — resolve + 누적 판정 (363차)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_loss_tier1_qty1_shadow() -> dict:
    """loss_tier1_qty1_shadow(main.py에서 기록) resolve + PASS/FAIL 판정.

    0721 정기점검 딥다이브: is_loss_tier1_hit()가 qty<=1을 물리적 분할 불가로 원천
    제외해, qty=1 손실 포지션은 entry~stop 절반 지점을 지나도 아무 조치 없이 최종
    손절가까지 그대로 노출된다. tp2_hold_shadow와 달리 이 채널은 실제 포지션이
    그대로 진행되므로 candle 시뮬레이션이 필요 없다 — 실거래(trades 테이블)가
    최종적으로 낸 pnl_pts를 entry_ts 근사 조인(±10초, 체결보정 타이밍 오차 흡수)으로
    가져와 "그 시점에 tier1가에서 전량 조기청산했다면"과 그대로 대조한다.

    hyp_pnl_pts = tier1 조기청산 pt − 실제 실현 pt (양수 = 조기청산이 유리했음).
    PASS = 현행(qty=1 조기청산 없음) 유지 — 조기청산이 평균적으로 이득 아님.
    FAIL = qty=1 조기청산 정책 채택 검토 권고 (즉시 코드 변경 아님 — 주간회의 수동
           결정, §9 사전등록 원칙 — hurst_gate_shadow·open_gap_shadow와 동일 순서).

    [363차 후속, 0721 딥다이브 제안3 편입] 진입 시점 quantile 기대엣지/불확실성
    (main.py:_ts_execute_entry가 캡처)도 함께 저장돼, edge_ratio(=|expected_pt|/
    uncertainty_pt)와 실현 pnl_pts의 스피어만 상관을 보조 지표로 보고한다 — 이
    상관 자체는 PASS/FAIL 게이트가 아니라 참고용(§9와 동일 원칙, 표본이 쌓인 뒤
    등급/사이징 강화 여부는 사람이 별도 판단).
    """
    cr = VALIDATION_CAMPAIGN["loss_tier1_qty1_shadow"]
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM loss_tier1_qty1_shadow WHERE resolved = 0 ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    if unresolved:
        updates = []
        with _conn(TRADES_DB) as conn:
            for r in unresolved:
                # entry_ts 근사 조인(±10초) — position.entry_time(섀도 기록 시각 기준)과
                # trades.entry_ts(체결보정 후 확정)가 완전히 동일하지 않을 수 있음.
                match = conn.execute(
                    """SELECT pnl_pts FROM trades
                       WHERE direction = ?
                         AND ABS((julianday(entry_ts) - julianday(?)) * 86400) <= 10
                         AND exit_ts IS NOT NULL
                       ORDER BY ABS((julianday(entry_ts) - julianday(?)) * 86400)
                       LIMIT 1""",
                    (r["direction"], r["entry_ts"], r["entry_ts"]),
                ).fetchone()
                if match is None:
                    continue  # 실거래가 아직 청산 전 — 다음 실행에서 재시도
                actual_pnl = float(match["pnl_pts"] or 0.0)
                is_long = str(r["direction"]) == "LONG"
                entry_p = float(r["entry_price"])
                tier1_p = float(r["loss_tier1_price"])
                tier1_cut_pts = (tier1_p - entry_p) if is_long else (entry_p - tier1_p)
                hyp = tier1_cut_pts - actual_pnl
                updates.append((round(actual_pnl, 4), round(hyp, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE loss_tier1_qty1_shadow
                       SET resolved=1, actual_pnl_pts=?, hyp_pnl_pts=?
                       WHERE id=?""",
                    updates,
                )
                conn.commit()
            out["resolved_now"] = len(updates)

    # ── [MW0602 425차] 판정 모집단 정제 — 두 가지를 제외한다 ────────────────────
    # (1) `live_active=1` — LOSS_TIER1_QTY1_ENABLED 전환 이후의 기록. 그때는 실제로
    #     tier1에서 잘랐으므로 "잘랐다면"이라는 반사실이 실제와 같아져 hyp≈0으로
    #     수렴한다. 섞으면 판정이 0 쪽으로 희석된다.
    # (2) `from_tier1_remainder=1` — qty=2가 tier1으로 1계약을 자른 **잔여 1계약**.
    #     이 채널의 모집단은 "계단화가 원천 배제된 진짜 qty=1"인데 잔여계약은 이미
    #     한 번 보호받은 다른 모집단이다(그쪽은 [14]가 맡는다).
    #     ⚠ 구버전 행은 이 컬럼이 없거나 0이므로 **trades의 '손절1차 조기축소' 레그
    #       유무로 소급 보정**한다 — 실측 혼입이 있었다(08-04 12:21, entry_qty=2가
    #       12:22:18 tier1 체결로 qty 2→1이 된 뒤 이 표에 들어왔다).
    try:
        with _conn(TRADES_DB) as conn:
            _cols = {r[1] for r in conn.execute(
                "PRAGMA table_info(loss_tier1_qty1_shadow)").fetchall()}
            _has_live = "live_active" in _cols
            _has_rem = "from_tier1_remainder" in _cols
            if _has_rem:
                # 소급 보정 — 조인 관례는 위 resolve와 동일(±10초 근사).
                _fix = conn.execute(
                    """SELECT s.id FROM loss_tier1_qty1_shadow s
                        WHERE COALESCE(s.from_tier1_remainder,0) = 0
                          AND EXISTS (SELECT 1 FROM trades t
                                       WHERE t.exit_reason = '손절1차 조기축소'
                                         AND t.direction = s.direction
                                         AND ABS((julianday(t.entry_ts)
                                                  - julianday(s.entry_ts)) * 86400) <= 10)"""
                ).fetchall()
                if _fix:
                    conn.executemany(
                        "UPDATE loss_tier1_qty1_shadow SET from_tier1_remainder=1 WHERE id=?",
                        [(r["id"],) for r in _fix])
                    conn.commit()
                    out["remainder_backfilled"] = len(_fix)
    except Exception as e:
        out["error"] = "모집단 정제 실패: %s" % e
        return out

    _excl = ["resolved=1", "ts >= ?"]
    if _has_live:
        _excl.append("COALESCE(live_active,0) = 0")
    if _has_rem:
        _excl.append("COALESCE(from_tier1_remainder,0) = 0")
    _where = " AND ".join(_excl)

    try:
        with _conn(TRADES_DB) as conn:
            agg = conn.execute(
                """SELECT COUNT(*) AS n, SUM(hyp_pnl_pts) AS total_hyp,
                          AVG(entry_price) AS avg_price,
                          SUM(CASE WHEN hyp_pnl_pts > 0 THEN 1 ELSE 0 END) AS n_win
                   FROM loss_tier1_qty1_shadow WHERE """ + _where,
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM loss_tier1_qty1_shadow WHERE resolved=0"
            ).fetchone()["n"]
            _day_rows = conn.execute(
                "SELECT substr(ts,1,10) AS d, hyp_pnl_pts AS h "
                "  FROM loss_tier1_qty1_shadow WHERE " + _where,
                (_campaign_start(),),
            ).fetchall()
            if _has_live:
                out["n_live_excluded"] = conn.execute(
                    "SELECT COUNT(*) AS n FROM loss_tier1_qty1_shadow "
                    " WHERE resolved=1 AND COALESCE(live_active,0)=1"
                ).fetchone()["n"]
            if _has_rem:
                out["n_remainder_excluded"] = conn.execute(
                    "SELECT COUNT(*) AS n FROM loss_tier1_qty1_shadow "
                    " WHERE resolved=1 AND COALESCE(from_tier1_remainder,0)=1"
                ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_hyp = float(agg["total_hyp"] or 0.0)
    avg_price = float(agg["avg_price"] or 0.0) or 300.0
    win_rate = (int(agg["n_win"] or 0) / n) if n else 0.0
    # [425차] 일자단위 검정(313차) — 12/14 표본이 3거래일에 몰려 있어 건수만으로는
    # 하루가 표본의 40%를 공급해도 판정이 난다. 일자별 평균 hyp의 부호를 센다.
    _by_day = {}
    for _r in _day_rows:
        _by_day.setdefault(_r["d"], []).append(float(_r["h"] or 0.0))
    _day_means = [float(np.mean(v)) for _, v in sorted(_by_day.items())]
    out.update(_paired_day_summary(_day_means, float(cr.get("alpha", 0.05))))
    out["days"] = len(_day_means)
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_hyp_pnl_pts": round(total_hyp, 4),
        "win_rate": round(win_rate, 4),
    })

    # [363차 후속, §11-보조] quantile 기대엣지/불확실성 비율 vs 실현 pnl 상관 —
    # 정책 게이트 아님, 참고용 상관관계만 보고한다. "체크리스트/메타 등급과 무관하게
    # edge_ratio가 낮았던 진입이 실제로도 더 나쁜 결과를 냈는가"(0721 딥다이브 관찰)를
    # 표본이 쌓이는 대로 실측 확인 — 등급/사이징 강화 여부는 이 상관이 충분히 쌓인
    # 뒤 별도로 사람이 판단(§9와 동일 원칙, 이 값 자체가 자동으로 아무것도 바꾸지 않음).
    try:
        with _conn(TRADES_DB) as conn:
            edge_rows = conn.execute(
                """SELECT quantile_expected_pt AS exp_pt, quantile_uncertainty_pt AS unc_pt,
                          actual_pnl_pts AS pnl
                   FROM loss_tier1_qty1_shadow
                   WHERE resolved=1 AND ts >= ?
                     AND quantile_expected_pt IS NOT NULL
                     AND quantile_uncertainty_pt IS NOT NULL
                     AND quantile_uncertainty_pt > 0""",
                (_campaign_start(),),
            ).fetchall()
    except Exception:
        edge_rows = []
    edge_ratios = [abs(float(r["exp_pt"])) / float(r["unc_pt"]) for r in edge_rows]
    edge_pnls = [float(r["pnl"]) for r in edge_rows]
    out["n_edge_samples"] = len(edge_ratios)
    if len(edge_ratios) >= 10:
        _ec = _spearman(edge_ratios, edge_pnls)
        out["edge_uncertainty_corr"] = None if np.isnan(_ec) else round(_ec, 4)
        out["edge_ratio_mean"] = round(float(np.mean(edge_ratios)), 4)

    _min_d = int(cr.get("min_days", 0))
    if n < int(cr["min_samples"]):
        out["reason"] = ("tier1 터치 표본 부족 (%d < %d, %d거래일) — 판정 보류"
                         % (n, cr["min_samples"], out["days"]))
        return out
    if out["days"] < _min_d:
        # [425차] 건수는 찼는데 거래일이 모자란 경우. n=5에서는 양측 부호검정 최소
        # p가 0.0625라 α=0.05를 **원리적으로** 통과할 수 없다 — 건수만 보고 판정하면
        # 하루가 표본의 절반을 공급해도 통과한다.
        out["reason"] = ("거래일 부족 (%d일 < %d일, 표본 %d건) — 판정 보류. "
                         "누적 %+.2fpt는 아직 근거가 아니다"
                         % (out["days"], _min_d, n, total_hyp))
        return out

    cost_pt = _roundtrip_cost_pt(avg_price)
    out["cost_pt"] = round(cost_pt, 4)
    # [425차] 채택 조건을 **두 겹**으로 한다 — 종전은 누적 pt가 왕복비용의 2배를
    # 넘는지만 봤는데, 그 지표는 큰 하루가 통째로 만들 수 있다(372차 이상치 착시).
    #   ① 누적 hyp > 왕복비용 × 2   (경제적 유의미)
    #   ② 일자단위 부호검정 p < α    (재현성, 313차)
    _econ = total_hyp > cost_pt * 2.0
    _repro = bool(out.get("significant"))
    adopt = _econ and _repro
    out["econ_ok"] = _econ
    out["repro_ok"] = _repro
    out["verdict"] = "FAIL" if adopt else "PASS"
    if adopt:
        out["recommendation"] = (
            "qty=1 손실1차 **전량** 조기청산 채택 검토 — 누적 %+.2fpt(비용 %.3fpt×2 초과) "
            "이고 일자단위로도 재현된다(%d/%d일, p=%.4f). 적용은 "
            "`config/settings.py:LOSS_TIER1_QTY1_ENABLED = True` + "
            "`LOSS_TIER1_QTY1_EFFECTIVE_DATE` 기입 — 주간회의 수동 결정(§9). "
            "전환 후 이 채널은 live_active 행을 판정에서 제외하므로 판정이 얼어붙는다"
            % (total_hyp, cost_pt, out.get("days_positive", 0),
               out.get("paired_days", 0), out.get("sign_p", 1.0)))
    elif _econ and not _repro:
        out["recommendation"] = (
            "누적 %+.2fpt는 비용 기준을 넘지만 **일자단위로 재현되지 않는다** "
            "(%d/%d일, p=%.4f) — 채택 보류. 누적 수치만으로 움직이지 말 것(313차)"
            % (total_hyp, out.get("days_positive", 0),
               out.get("paired_days", 0), out.get("sign_p", 1.0)))
    return out


# ──────────────────────────────────────────────────────────────
# [14] Tier1 발동 후 잔여계약 2단계 조기청산 counterfactual — resolve + 누적 판정 (367차)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_loss_tier2_remainder_shadow() -> dict:
    """loss_tier2_remainder_shadow(main.py에서 기록) resolve + PASS/FAIL 판정.

    loss_tier1_qty1_shadow와 동일한 패턴이나, 조인 대상이 "원 포지션 전체"가 아니라
    "Tier1 이후 남은 잔여계약의 최종 청산 레그"다 — Tier1 체결 시 trades 테이블에
    별도 행(exit_reason='손절1차 조기축소')이 하나 생기고, 잔여계약은 그 뒤 별도
    행으로 최종 청산되므로 그 행만 골라 조인한다(direction+entry_ts+quantity로
    특정, tier1 레그 자체는 exit_reason으로 제외).

    hyp_pnl_pts = tier2가 조기청산 pt − 실제(잔여계약) 실현 pt (양수=조기청산 유리).
    PASS = 현행(잔여계약 추가조치 없음) 유지 — 조기청산이 평균적으로 이득 아님.
    FAIL = 잔여계약 2단계 조기청산 정책 채택 검토 권고 (즉시 코드 변경 아님 —
           주간회의 수동 결정, §9 사전등록 원칙 — loss_tier1_qty1_shadow와 동일 순서).
    """
    cr = VALIDATION_CAMPAIGN["loss_tier2_remainder_shadow"]
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM loss_tier2_remainder_shadow WHERE resolved = 0 ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    if unresolved:
        updates = []
        with _conn(TRADES_DB) as conn:
            for r in unresolved:
                match = conn.execute(
                    """SELECT pnl_pts FROM trades
                       WHERE direction = ? AND quantity = ?
                             AND exit_reason != '손절1차 조기축소'
                             AND ABS((julianday(entry_ts) - julianday(?)) * 86400) <= 10
                             AND exit_ts IS NOT NULL
                       ORDER BY ABS((julianday(entry_ts) - julianday(?)) * 86400)
                       LIMIT 1""",
                    (r["direction"], r["remaining_qty"], r["entry_ts"], r["entry_ts"]),
                ).fetchone()
                if match is None:
                    continue  # 잔여계약이 아직 청산 전 — 다음 실행에서 재시도
                actual_pnl = float(match["pnl_pts"] or 0.0)
                is_long = str(r["direction"]) == "LONG"
                entry_p = float(r["entry_price"])
                tier2_p = float(r["loss_tier2_price"])
                # entry_price는 원 포지션 진입가 — tier2_cut_pts는 "그 진입가 기준"
                # 실현 pt와 같은 기준(entry_price 대비)으로 맞춰야 actual_pnl(마찬가지로
                # trades.pnl_pts, entry_price 기준)과 동일 척도로 비교 가능.
                tier2_cut_pts = (tier2_p - entry_p) if is_long else (entry_p - tier2_p)
                hyp = tier2_cut_pts - actual_pnl
                updates.append((round(actual_pnl, 4), round(hyp, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE loss_tier2_remainder_shadow
                       SET resolved=1, actual_pnl_pts=?, hyp_pnl_pts=?
                       WHERE id=?""",
                    updates,
                )
                conn.commit()
            out["resolved_now"] = len(updates)

    try:
        with _conn(TRADES_DB) as conn:
            agg = conn.execute(
                """SELECT COUNT(*) AS n, SUM(hyp_pnl_pts) AS total_hyp,
                          AVG(entry_price) AS avg_price,
                          SUM(CASE WHEN hyp_pnl_pts > 0 THEN 1 ELSE 0 END) AS n_win
                   FROM loss_tier2_remainder_shadow WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM loss_tier2_remainder_shadow WHERE resolved=0"
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_hyp = float(agg["total_hyp"] or 0.0)
    avg_price = float(agg["avg_price"] or 0.0) or 300.0
    win_rate = (int(agg["n_win"] or 0) / n) if n else 0.0
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_hyp_pnl_pts": round(total_hyp, 4),
        "win_rate": round(win_rate, 4),
    })

    if n < int(cr["min_samples"]):
        out["reason"] = "tier2 터치 표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out

    cost_pt = _roundtrip_cost_pt(avg_price)
    out["cost_pt"] = round(cost_pt, 4)
    adopt = total_hyp > cost_pt * 2.0
    out["verdict"] = "FAIL" if adopt else "PASS"
    if adopt:
        out["recommendation"] = (
            "잔여계약 2단계 조기청산 정책 채택 검토 — 주간회의 수동 결정 (§9 사전등록 원칙)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# [15] 급행 풀스톱(TP1 미도달) 관찰 채널 (367차, 관찰 전용 — PASS/FAIL 판정 없음)
# ──────────────────────────────────────────────────────────────

def eval_fast_reversal_watch(days: int) -> dict:
    """하드스톱 청산 중 (a) 보유시간이 짧고(fast_exit_max_sec 이내) (b) TP1 보호전환이
    한 번도 발동하지 않은 포지션의 등급별 발생률·손익을 집계한다.

    0722 정기점검 딥다이브(4주 9건 사례, -2,161,020원 — A등급 4주 누적손실의 84%)에서
    발견한 패턴을 지속 관찰하기 위한 채널. GradeEVGuard·loss_tier1_qty1_shadow처럼
    거래가 완결돼야 표본이 쌓이는 채널과 달리, "TP1 도달 여부"는 로그에서 직접 읽을
    수 있어 정책 게이트 없이도 등급별 추세를 빠르게 볼 수 있다.

    PASS/FAIL 판정을 내리지 않는다 — 이 패턴 자체를 "차단"할 기존 메커니즘이 없어
    (즉 완화 정책이 아직 없어) 판정이 의미가 없기 때문. 순수 관찰용 — kelly_skip·
    grade_ev_inversion과 달리 verdict는 항상 "OBSERVE"로 고정.
    """
    fast_max_sec = int(VALIDATION_CAMPAIGN["fast_reversal_watch"]["fast_exit_max_sec"])
    out = {"verdict": "OBSERVE", "fast_exit_max_sec": fast_max_sec}
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(_TS_FMT)

    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT entry_ts, exit_ts, direction, grade, quantity,
                          pnl_pts, net_pnl_krw
                   FROM trades
                   WHERE entry_ts >= ? AND exit_ts IS NOT NULL
                         AND exit_reason LIKE '%하드스톱%'""",
                (cutoff,),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    candidates = []
    for r in rows:
        try:
            t0 = datetime.datetime.strptime(r["entry_ts"], _TS_FMT)
            t1 = datetime.datetime.strptime(r["exit_ts"], _TS_FMT)
        except (TypeError, ValueError):
            continue
        hold_sec = (t1 - t0).total_seconds()
        if hold_sec <= fast_max_sec:
            candidates.append((r, hold_sec))

    out["n_fast_hardstop"] = len(candidates)
    if not candidates:
        out["reason"] = "관찰 대상(급행 하드스톱) 0건"
        return out

    # TP1 도달 여부 — 같은 날짜의 TRADE.log에서 entry_ts~exit_ts 구간에 "TP1"
    # 문자열이 등장하는지 확인(main.py가 TP1 보호전환/부분청산 시 항상 이 문자열을
    # 남김 — synthetic_tp1(qty=1)·실제 부분청산(qty>=2) 모두 커버).
    by_date = {}
    for r, hold_sec in candidates:
        date_key = r["entry_ts"][:10].replace("-", "")
        by_date.setdefault(date_key, []).append((r, hold_sec))

    log_dir = os.path.join(ROOT, "logs")
    by_grade = {}
    for date_key, items in by_date.items():
        log_path = os.path.join(log_dir, f"{date_key}_TRADE.log")
        try:
            with open(log_path, encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
        except OSError:
            lines = None  # 로그 유실 — TP1 판정 불가로 보수적으로 "도달함" 취급(과다경보 방지)
        for r, hold_sec in items:
            reached_tp1 = True
            if lines is not None:
                reached_tp1 = any(
                    r["entry_ts"] <= ln[:19] <= r["exit_ts"] and "TP1" in ln
                    for ln in lines
                )
            if reached_tp1:
                continue  # TP1 도달 후 짧게 청산된 건 이 채널의 관심사가 아님(정상 동작)
            g = (r["grade"] or "?") or "?"
            slot = by_grade.setdefault(g, {"n": 0, "total_pnl_krw": 0.0, "n_loss": 0})
            slot["n"] += 1
            slot["total_pnl_krw"] += float(r["net_pnl_krw"] or 0.0)
            if float(r["net_pnl_krw"] or 0.0) < 0:
                slot["n_loss"] += 1

    out["by_grade"] = {
        g: {
            "n": v["n"],
            "total_pnl_krw": round(v["total_pnl_krw"], 0),
            "n_loss": v["n_loss"],
        }
        for g, v in by_grade.items()
    }
    out["n_no_tp1"] = sum(v["n"] for v in by_grade.values())
    return out


# [16] chase+foreign 조합 관찰 채널 (368차, 관찰 전용 — PASS/FAIL 판정 없음)
def eval_chase_foreign_combo_watch() -> dict:
    """10_chase(연장추격)와 6_foreign(외인 옵션 수급) 두 체크리스트 항목이 동시에
    실패(나머지 항목 무관)한 진입의 등급별 발생률·손익을 집계한다.

    0722 정기점검 딥다이브(MW0601 실측): 09:32~09:53 21분 사이 이 조합(나머지 9개
    항목 전부 통과)이 3회 발화해 3회 전부 하드스톱(-536,097원, 그날 최대
    손실뭉치 -742,800원의 72%). trades.db에 체크리스트 개별 항목이 저장되지
    않아 fast_reversal_watch(367차)와 동일 방식으로 entry_ts를 키 삼아
    TRADE.log의 [진입체크] 라인과 매칭한다.

    CHASE_FOREIGN_COMBO_GUARD_ENABLED(섀도) 판정 근거 표본 축적용 — 아직
    이 조합을 강등할 정책이 섀도 단계라 PASS/FAIL 판정은 하지 않는다
    (fast_reversal_watch와 동일 원칙). verdict는 항상 OBSERVE로 고정.
    """
    days = int(VALIDATION_CAMPAIGN["chase_foreign_combo_watch"]["lookback_days"])
    out = {"verdict": "OBSERVE", "lookback_days": days}
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(_TS_FMT)

    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT entry_ts, exit_ts, direction, grade, quantity,
                          pnl_pts, net_pnl_krw
                   FROM trades
                   WHERE entry_ts >= ? AND exit_ts IS NOT NULL""",
                (cutoff,),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    by_date = {}
    for r in rows:
        date_key = r["entry_ts"][:10].replace("-", "")
        by_date.setdefault(date_key, []).append(r)

    log_dir = os.path.join(ROOT, "logs")
    by_grade = {}
    n_matched = 0
    for date_key, items in by_date.items():
        log_path = os.path.join(log_dir, f"{date_key}_TRADE.log")
        try:
            with open(log_path, encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
        except OSError:
            continue  # 로그 유실 — 이 채널은 관찰용이라 보수적 취급 없이 스킵

        entry_lines = [ln for ln in lines if "[진입체크]" in ln]
        for r in items:
            # entry_ts는 [Position]체결 시각(초 단위로 [진입체크]보다 0~수초 늦음) —
            # 정확히 같은 초가 아닐 수 있어 직전 5초 이내 가장 가까운 [진입체크] 채택.
            try:
                r_dt = datetime.datetime.strptime(r["entry_ts"][:19], _TS_FMT)
            except (TypeError, ValueError):
                continue
            match, best_diff = None, None
            for ln in entry_lines:
                try:
                    ln_dt = datetime.datetime.strptime(ln[:19], _TS_FMT)
                except ValueError:
                    continue
                diff = (r_dt - ln_dt).total_seconds()
                if 0 <= diff <= 5 and (best_diff is None or diff < best_diff):
                    match, best_diff = ln, diff
            if match is None:
                continue
            n_matched += 1
            if "chas❌" in match and "fore❌" in match:
                g = (r["grade"] or "?") or "?"
                slot = by_grade.setdefault(g, {"n": 0, "total_pnl_krw": 0.0, "n_loss": 0})
                slot["n"] += 1
                slot["total_pnl_krw"] += float(r["net_pnl_krw"] or 0.0)
                if float(r["net_pnl_krw"] or 0.0) < 0:
                    slot["n_loss"] += 1

    out["n_matched"] = n_matched
    out["by_grade"] = {
        g: {"n": v["n"], "total_pnl_krw": round(v["total_pnl_krw"], 0), "n_loss": v["n_loss"]}
        for g, v in by_grade.items()
    }
    out["n_combo"] = sum(v["n"] for v in by_grade.values())
    out["total_pnl_krw"] = round(sum(v["total_pnl_krw"] for v in by_grade.values()), 0)
    if out["n_combo"] == 0:
        out["reason"] = "관찰 대상(chase+foreign 동시 실패) 0건"
    return out


# [17] 청산 주문 체결 슬리피지 관찰 채널 (369차, 관찰 전용 — PASS/FAIL 판정 없음)
def eval_exit_fill_slippage_watch(days: int) -> dict:
    """청산 주문의 의도가(price_hint)와 실체결가(fill_price) 괴리를 청산 사유별로
    집계한다(exit_fill_slippage 테이블, main.py::_ts_record_exit_fill_slippage()).

    0723 정기점검 딥다이브 계기: TP1 ATR보호전환(+0.35pt 확정 예정)이 하드스톱(틱)
    체결 슬리피지(주문가 1122.49 → 체결가 1122.12, 0.37pt≈18틱 불리)로 순손실
    (-0.02pt)로 뒤집힌 사례를 발견했으나, VALIDATION_CAMPAIGN 전 채널의 왕복비용
    계산이 가정하는 slippage_ticks_per_side(=1.0, 0.02pt)이 실측과 맞는지 검증할
    데이터가 그때까지 전혀 없었다.

    [439차 P2] 관찰 → **판정**으로 승격하면서 오염을 걷어냈다.

    🔴 이 채널은 자기 경보를 스스로 억제하고 있었다 — note 조건이 `풀링 평균 >
    가정`인데 풀링 평균이 **봉중(stop_intrabar) 경로에 오염**돼 음수로 끌려가
    조건이 성립할 수 없었다(풀링 -0.1816 / 봉중 -1.8854 / 유효 +0.0492).
    봉중은 `price_hint`가 봉 고저가에서 유도한 **허구의 스톱가**라 주문(시장가)과
    무관하다 — 슬리피지 추정에서 제외한다(P3 [48-T]에서 확정).

    경로 분류는 `scripts/bar_stop_path_watch.py:_path_of()` **단일 소스**를 쓴다.
    판정 기준·정직성 고지는 config/settings.py `exit_fill_slippage_watch` 참조.
    ⚠ FAIL이어도 `slippage_ticks_per_side`를 **자동으로 바꾸지 않는다**(§3).
    """
    days_cfg = VALIDATION_CAMPAIGN.get("exit_fill_slippage_watch", {})
    min_note = int(days_cfg.get("min_samples_for_note", 20))
    min_n = int(days_cfg.get("min_samples", 60))
    min_d = int(days_cfg.get("min_days", 8))
    alpha = float(days_cfg.get("alpha", 0.05))
    out = {"verdict": "INSUFFICIENT", "assumed_ticks_per_side": float(
        VALIDATION_CAMPAIGN.get("slippage_ticks_per_side", 1.0))}
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(_TS_FMT)

    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT ts, reason, hint_source, slippage_pts FROM exit_fill_slippage
                   WHERE ts >= ?""",
                (cutoff,),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    out["n"] = len(rows)
    if not rows:
        out["reason"] = "체결 슬리피지 기록 0건"
        return out

    vals = [float(r["slippage_pts"]) for r in rows]
    # ⚠ `avg_slippage_pts`는 **풀링값 그대로 둔다**(의미 변경 금지 — metrics json
    #   소비처와 과거 주차 대조가 이 키를 읽는다). 판정은 아래 유효-hint로 한다.
    out["avg_slippage_pts"] = round(sum(vals) / len(vals), 4)
    out["max_slippage_pts"] = round(max(vals), 4)
    out["assumed_slippage_pts_per_side"] = round(
        out["assumed_ticks_per_side"] * TICK_SIZE, 4)
    assumed = out["assumed_slippage_pts_per_side"]

    by_reason = {}
    for r in rows:
        reason = str(r["reason"] or "?") or "?"
        slot = by_reason.setdefault(reason, {"n": 0, "sum_pts": 0.0})
        slot["n"] += 1
        slot["sum_pts"] += float(r["slippage_pts"])
    out["by_reason"] = {
        k: {"n": v["n"], "avg_pts": round(v["sum_pts"] / v["n"], 4)}
        for k, v in by_reason.items()
    }

    # ── 유효-hint 부분표본 분리 ([48]과 단일 소스) ──────────────────────────
    try:
        from scripts.bar_stop_path_watch import _path_of as _bsp_path_of, BAR as _BAR
    except Exception as e:
        out["error"] = "경로 분류 임포트 실패: %s" % e
        return out

    valid, bar_vals = [], []
    for r in rows:
        v = float(r["slippage_pts"])
        if _bsp_path_of(r["hint_source"], r["reason"])[0] == _BAR:
            bar_vals.append(v)
        else:
            valid.append((str(r["ts"])[:10], v))
    out["n_bar_excluded"] = len(bar_vals)
    out["avg_bar_pts"] = round(sum(bar_vals) / len(bar_vals), 4) if bar_vals else None
    out["n_valid"] = len(valid)
    if not valid:
        out["reason"] = "유효-hint 표본 0건 (전부 봉중 경로 — hint가 허구라 제외)"
        return out

    vv = [x for _, x in valid]
    out["avg_valid_pts"] = round(sum(vv) / len(vv), 4)
    out["valid_over_assumed_mult"] = (round(out["avg_valid_pts"] / assumed, 2)
                                      if assumed else None)
    day_map = {}
    for d, x in valid:
        day_map.setdefault(d, []).append(x)
    days_sorted = sorted(day_map)
    out["n_valid_days"] = len(days_sorted)
    # 일자단위 = 판정 단위(313차). "가정 초과"를 부호로 삼아 부호검정한다.
    day_means = [float(np.mean(day_map[d])) for d in days_sorted]
    out["day_means"] = {d: round(m, 4) for d, m in zip(days_sorted, day_means)}
    out["avg_valid_day_pts"] = round(float(np.mean(day_means)), 4)
    out["median_valid_day_pts"] = round(float(np.median(day_means)), 4)
    out.update(_paired_day_summary([m - assumed for m in day_means], alpha))
    out["days_over_assumed"] = int(sum(1 for m in day_means if m > assumed))
    out["days_majority_over"] = bool(out["days_over_assumed"] * 2 > out["n_valid_days"])
    # 세 지표가 만장일치가 아니면 소표본 일자·이상치가 끌고 있다는 뜻이다(313차).
    _sig = (out["avg_valid_pts"] > assumed,          # 이벤트 평균
            out["avg_valid_day_pts"] > assumed,      # 일자 평균(이상치 민감)
            out["days_majority_over"])               # 일자 과반(이상치 강건)
    out["event_day_split"] = not (all(_sig) or not any(_sig))

    if out["n"] >= min_note and out["avg_valid_pts"] > assumed:
        out["note"] = (
            "유효-hint 실측 평균(%.4fpt)이 캠페인 가정(%.4fpt)의 %.1f배 — "
            "slippage_ticks_per_side 재보정 여부를 주간회의에서 검토할 가치 있음"
            "(§3 사전등록 원칙 — 즉시 자동 변경 금지). ⚠ 풀링 평균(%.4fpt)은 봉중 "
            "경로 %d건에 오염돼 이 경보를 억제하고 있었다(439차 P2)."
            % (out["avg_valid_pts"], assumed, out["avg_valid_pts"] / assumed,
               out["avg_slippage_pts"], out["n_bar_excluded"])
        )

    if out["n_valid"] < min_n or out["n_valid_days"] < min_d:
        out["reason"] = ("유효-hint 표본 부족 (%d건<%d 또는 거래일 %d<%d) — 판정 보류"
                         % (out["n_valid"], min_n, out["n_valid_days"], min_d))
        return out

    # 🔴 방향은 **일자 과반**으로 잡는다 — 일자 평균이 아니다.
    #   부호검정은 양측이라 "9일이 가정 **미만**이고 1일만 폭등"해도 유의가 뜨고,
    #   그 1일이 평균을 끌어올려 `avg_valid_day_pts > assumed`까지 참이 된다.
    #   그러면 일자단위로 내려온 이유(이상치 강건성) 자체가 무너진다.
    #   과반을 쓰면 부호검정이 세는 것(초과일 수)과 방향 판정이 같은 통계량이 된다.
    if out.get("significant") and out["days_majority_over"]:
        out["verdict"] = "FAIL"
        out["reason"] = (
            "초과일이 과반이고(일자 평균 %+.4fpt vs 가정 %.4fpt) 부호검정 p=%.4f < %.2f "
            "(초과일 %d/%d) — 왕복비용 가정이 실측을 못 따라간다. "
            "`slippage_ticks_per_side` 재보정을 **주간회의 안건으로** 올릴 것"
            "(⚠ 자동 변경 금지 — 바꾸면 §3에 따라 검증 시계 리셋)"
            % (out["avg_valid_day_pts"], assumed, out.get("sign_p", 1.0), alpha,
               out["days_over_assumed"], out["n_valid_days"]))
    else:
        out["verdict"] = "PASS"
        out["reason"] = (
            "일자단위 평균 %+.4fpt vs 가정 %.4fpt, 초과일 %d/%d, 부호검정 p=%.4f — "
            "**가정과 구분되지 않는다**(가정이 옳다고 증명된 것이 아니다). "
            "이벤트단위는 %+.4fpt(가정의 %.1f배)지만 313차상 판정 단위는 일자다"
            % (out["avg_valid_day_pts"], assumed, out["days_over_assumed"],
               out["n_valid_days"], out.get("sign_p", 1.0),
               out["avg_valid_pts"], (out["avg_valid_pts"] / assumed) if assumed else 0))
    return out


# ──────────────────────────────────────────────────────────────
# [12] qty=1 TP1 이후 트레일 폭 counterfactual — resolve + 누적 판정 (363차 후속)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_tp1_trail_shadow() -> dict:
    """tp1_trail_shadow(main.py에서 기록) resolve + PASS/FAIL 판정.

    0721 정기점검 딥다이브 제안4 편입 — 361차 tp2_hold_shadow와 동일한 패턴·판정
    로직이며 트레일링 시뮬레이션도 같은 순수함수(compute_trailing_stop_tier)를
    재사용한다(단일 소스 유지, 라이브 로직과 계측 시뮬레이션 드리프트 방지).
    qty=1은 TP1 이후 update_trailing_stop() 4단계 트레일링 대신 static ATR-lock
    1회 보호전환만 받는데, "그때부터 qty=2와 동일한 4단계 트레일링을 계속 적용
    했다면" 당일 15:10까지 분봉으로 사후 시뮬레이션하고, 실거래(trades 테이블)가
    최종적으로 낸 pnl_pts를 entry_ts 근사 조인(±10초, loss_tier1_qty1_shadow와
    동일 방식)으로 가져와 그대로 대조한다 — anchor 시작값은 tp2_hold_shadow의
    "entry_price로 단순화"와 달리 훅 시점에 이미 도달이 확인된 tp1_price를 사용
    (아는 값을 굳이 버릴 이유가 없음, stop 시작값은 실제 적용된 static lock).

    hyp_pnl_pts = (4단계 트레일링 지속 시뮬레이션 pt) − (실제 실현 pt).
    PASS = 현행(static lock) 유지 — 트레일링 지속이 평균적으로 이득 아님.
    FAIL = qty=1도 4단계 트레일링 적용 채택 검토 권고 (즉시 코드 변경 아님 —
           주간회의 수동 결정, §9 사전등록 원칙 — tp2_hold_shadow와 동일 순서).
    """
    cr = VALIDATION_CAMPAIGN["tp1_trail_shadow"]
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM tp1_trail_shadow WHERE resolved = 0 ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    if unresolved:
        earliest = min(r["ts"] for r in unresolved)
        # 체결 시뮬 경로 — 거래불능 분봉 제외 [404차 후속5 / P0-B(a)]
        close_map, high_map, low_map = _load_candle_maps(
            earliest, exclude_untradeable=True)
        now = datetime.datetime.now()
        updates = []
        with _conn(TRADES_DB) as conn:
            for r in unresolved:
                base = datetime.datetime.strptime(r["ts"], _TS_FMT)
                day_end = base.replace(hour=15, minute=10, second=0, microsecond=0)
                if now < day_end + datetime.timedelta(minutes=2):
                    continue  # 당일 장 마감까지 아직 안 지남 — 다음 실행에서 재시도
                # 실거래 실현 pnl 먼저 확인 — entry_ts 근사 조인(±10초)
                match = conn.execute(
                    """SELECT pnl_pts FROM trades
                       WHERE direction = ?
                         AND ABS((julianday(entry_ts) - julianday(?)) * 86400) <= 10
                         AND exit_ts IS NOT NULL
                       ORDER BY ABS((julianday(entry_ts) - julianday(?)) * 86400)
                       LIMIT 1""",
                    (r["direction"], r["entry_ts"], r["entry_ts"]),
                ).fetchone()
                if match is None:
                    continue  # 실거래가 아직 청산 전 — 다음 실행에서 재시도
                actual_pnl = float(match["pnl_pts"] or 0.0)

                is_long = str(r["direction"]) == "LONG"
                direction = "LONG" if is_long else "SHORT"
                entry_p = float(r["entry_price"])
                atr = float(r["atr_at_hook"] or 0.0)
                anchor = float(r["tp1_price"])
                stop = float(r["protect_stop_at_hook"])
                cf_outcome, cf_price, cf_minutes = None, None, 0
                last_close, last_m = None, 0
                m = 0
                while True:
                    m += 1
                    mid = base + datetime.timedelta(minutes=m)
                    if mid.time() > datetime.time(15, 10):
                        break
                    mid_ts = mid.strftime(_TS_FMT)
                    hi = high_map.get(mid_ts)
                    lo = low_map.get(mid_ts)
                    cl = close_map.get(mid_ts)
                    if hi is None or lo is None or cl is None:
                        continue
                    last_close, last_m = cl, m
                    anchor, stop = compute_trailing_stop_tier(
                        entry_p, direction, atr, cl, anchor, stop
                    )
                    hit_stop = lo <= stop if is_long else hi >= stop
                    if hit_stop:
                        cf_outcome, cf_price, cf_minutes = "TRAIL_STOP", stop, m
                        break
                if cf_price is None:
                    if last_close is None:
                        continue  # 분봉 데이터 자체가 없음 — 다음 실행에서 재시도
                    cf_outcome, cf_price, cf_minutes = "FORCE_EXIT", last_close, last_m
                cf_pnl = (cf_price - entry_p) if is_long else (entry_p - cf_price)
                hyp = cf_pnl - actual_pnl
                updates.append((
                    round(actual_pnl, 4), cf_outcome, round(cf_price, 4),
                    cf_minutes, round(hyp, 4), r["id"],
                ))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE tp1_trail_shadow
                       SET resolved=1, actual_pnl_pts=?, cf_outcome=?, cf_exit_price=?,
                           cf_hold_minutes=?, hyp_pnl_pts=?
                       WHERE id=?""",
                    updates,
                )
                conn.commit()
            out["resolved_now"] = len(updates)

    try:
        with _conn(TRADES_DB) as conn:
            agg = conn.execute(
                """SELECT COUNT(*) AS n, SUM(hyp_pnl_pts) AS total_hyp,
                          AVG(entry_price) AS avg_price,
                          SUM(CASE WHEN hyp_pnl_pts > 0 THEN 1 ELSE 0 END) AS n_win,
                          SUM(CASE WHEN cf_outcome='TRAIL_STOP' THEN 1 ELSE 0 END) AS n_stop,
                          SUM(CASE WHEN cf_outcome='FORCE_EXIT' THEN 1 ELSE 0 END) AS n_force
                   FROM tp1_trail_shadow WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM tp1_trail_shadow WHERE resolved=0"
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_hyp = float(agg["total_hyp"] or 0.0)
    avg_price = float(agg["avg_price"] or 0.0) or 300.0
    win_rate = (int(agg["n_win"] or 0) / n) if n else 0.0
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_hyp_pnl_pts": round(total_hyp, 4),
        "win_rate": round(win_rate, 4),
        "cf_trail_stop": int(agg["n_stop"] or 0),
        "cf_force_exit": int(agg["n_force"] or 0),
    })
    if n < int(cr["min_samples"]):
        out["reason"] = "TP1 보호전환 표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out

    cost_pt = _roundtrip_cost_pt(avg_price)
    out["cost_pt"] = round(cost_pt, 4)
    adopt = total_hyp > cost_pt * 2.0
    out["verdict"] = "FAIL" if adopt else "PASS"
    if adopt:
        out["recommendation"] = (
            "qty=1도 4단계 트레일링(update_trailing_stop) 적용 채택 검토 "
            "— 주간회의 수동 결정 (§9 사전등록 원칙)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# [5] 레짐 조건부 ATR 배수 — hurst_bucket별 순EV
# ──────────────────────────────────────────────────────────────

def eval_hurst_regime() -> dict:
    cr = VALIDATION_CAMPAIGN["hurst_regime"]
    out = {"verdict": "INSUFFICIENT", "buckets": {}}
    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT COALESCE(NULLIF(hurst_bucket,''),'?') AS bucket,
                          COUNT(*) AS n,
                          AVG(net_pnl_krw) AS avg_ev,
                          SUM(net_pnl_krw) AS total_ev,
                          AVG(CASE WHEN net_pnl_krw > 0 THEN 1.0 ELSE 0.0 END) AS wr
                   FROM trades
                   WHERE exit_ts >= ? AND net_pnl_krw IS NOT NULL
                   GROUP BY bucket""",
                (_campaign_start(),),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    for r in rows:
        out["buckets"][r["bucket"]] = {
            "n": int(r["n"]),
            "avg_ev_krw": round(float(r["avg_ev"] or 0.0), 0),
            "total_ev_krw": round(float(r["total_ev"] or 0.0), 0),
            "win_rate": round(float(r["wr"] or 0.0), 3),
        }

    trend = out["buckets"].get("trend")
    neutral = out["buckets"].get("neutral")
    min_n = int(cr["min_per_bucket"])
    if not trend or trend["n"] < min_n or not neutral or neutral["n"] < min_n:
        out["reason"] = "버킷별 표본 부족 (trend/neutral 각 %d건 필요)" % min_n
        return out
    # FAIL = trend 배수 1.20→1.10 후퇴 권고
    bad = trend["avg_ev_krw"] < 0 and trend["avg_ev_krw"] < neutral["avg_ev_krw"]
    out["verdict"] = "FAIL" if bad else "PASS"
    if bad:
        out["recommendation"] = "HURST_REGIME_ATR_MULT trend 1.20 → 1.10 후퇴 권고"
    return out


# ──────────────────────────────────────────────────────────────
# [8] KellyAdvisedSkip × C등급 누적 성과 — 게이트 승격 검토 (341차 신설)
# ──────────────────────────────────────────────────────────────

def eval_kelly_skip_grade_c() -> dict:
    """켈리(PositionSizer)가 "자본 대비 1계약도 부적절"이라 판단했는데
    (kelly_advised_skip=1) MINI_MIN_CONTRACTS 최소수량 강제로 그대로 체결된
    C등급 트레이드의 누적 성과를 4주 단위로 판정한다.

    signal_decay·hurst_gate_shadow·joint_gate_shadow와 달리 실제로 체결된
    진입(exec_1m_shadow·synthetic_partial_exits와 동일 계열)이므로
    counterfactual 시뮬레이션이 불필요 — trades 테이블의 실현 net_pnl_krw를
    그대로 집계하면 된다.

    PASS = 현행 유지 (C+KellySkip 조합이 특별히 나쁘지 않음, 또는 표본 부족).
    FAIL = 4주 누적 순손실 확정 → C등급+KellySkip 조합 진입 차단(사이징 0 또는
    등급 강등)을 단계 도입 검토 — 즉시 자동 차단이 아니라 권고만 출력(§9 원칙).
    """
    cr = VALIDATION_CAMPAIGN["kelly_skip"]
    out = {"verdict": "INSUFFICIENT"}
    try:
        with _conn(TRADES_DB) as conn:
            target = conn.execute(
                """SELECT COUNT(*) AS n,
                          SUM(net_pnl_krw) AS total_pnl,
                          AVG(net_pnl_krw) AS avg_pnl,
                          AVG(CASE WHEN net_pnl_krw > 0 THEN 1.0 ELSE 0.0 END) AS wr
                   FROM trades
                   WHERE exit_ts >= ? AND net_pnl_krw IS NOT NULL
                         AND grade = 'C' AND kelly_advised_skip = 1""",
                (_campaign_start(),),
            ).fetchone()
            baseline = conn.execute(
                """SELECT COUNT(*) AS n,
                          AVG(net_pnl_krw) AS avg_pnl,
                          AVG(CASE WHEN net_pnl_krw > 0 THEN 1.0 ELSE 0.0 END) AS wr
                   FROM trades
                   WHERE exit_ts >= ? AND net_pnl_krw IS NOT NULL
                         AND grade = 'C' AND COALESCE(kelly_advised_skip, 0) = 0""",
                (_campaign_start(),),
            ).fetchone()
            grade_split = conn.execute(
                """SELECT COALESCE(NULLIF(grade,''),'?') AS grade, COUNT(*) AS n,
                          SUM(net_pnl_krw) AS total_pnl,
                          AVG(CASE WHEN net_pnl_krw > 0 THEN 1.0 ELSE 0.0 END) AS wr
                   FROM trades
                   WHERE exit_ts >= ? AND net_pnl_krw IS NOT NULL
                         AND kelly_advised_skip = 1
                   GROUP BY grade""",
                (_campaign_start(),),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(target["n"] or 0)
    total_pnl = float(target["total_pnl"] or 0.0)
    base_n = int(baseline["n"] or 0)
    base_avg = float(baseline["avg_pnl"] or 0.0) if base_n else None
    base_wr = float(baseline["wr"] or 0.0) if base_n else None

    out.update({
        "n": n,
        "total_pnl_krw": round(total_pnl, 0),
        "avg_pnl_krw": round(float(target["avg_pnl"] or 0.0), 0),
        "win_rate": round(float(target["wr"] or 0.0), 4),
        "baseline_n": base_n,
        "baseline_avg_pnl_krw": round(base_avg, 0) if base_avg is not None else None,
        "baseline_win_rate": round(base_wr, 4) if base_wr is not None else None,
        "grade_split": {
            row["grade"]: {
                "n": int(row["n"] or 0),
                "total_pnl_krw": round(float(row["total_pnl"] or 0.0), 0),
                "win_rate": round((int(row["n"] or 0) and float(row["wr"] or 0.0)), 4),
            }
            for row in grade_split
        },
    })

    if n < int(cr["min_samples"]):
        out["reason"] = "C등급+KellySkip 표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out

    out["verdict"] = "FAIL" if total_pnl < 0 else "PASS"
    if out["verdict"] == "FAIL":
        out["recommendation"] = (
            "C등급+KellySkip 조합 누적 순손실 확정 — 진입 차단(사이징 0 또는 등급 "
            "강등) 단계 도입 검토 (§9 사전등록 원칙에 따라 적용은 수동 결정)"
        )
    return out


def eval_grade_ev_inversion() -> dict:
    """[366차 신설] §13 등급별 순EV 역전 감시 — A등급(체크리스트 pass_count≥6)의
    누적 순EV가 C등급보다 낮은 "역전" 현상을 캠페인 시작일 이후 누적 판정한다.

    kelly_skip과 동일 계열 — 실제로 체결된 진입(trades 테이블)이므로
    counterfactual 시뮬레이션이 불필요. 0722 정기점검 딥다이브에서 A등급 평균
    신뢰도(37.4%)가 C등급(35.9%)과 거의 동일한데도 순EV는 정반대(A 음수·C
    양수)임을 확인 — 신뢰도가 아니라 체크리스트 pass_count(등급) 자체가
    실현 엣지와 반비례하는 구조적 문제로 진단.

    PASS = A등급 평균 순EV ≥ 0 (역전 해소 또는 애초에 미발생).
    FAIL = A등급 평균 순EV < 0 이고 A/C 모두 표본 충분 → GradeEVGuard
    (config.settings.GRADE_EV_GUARD_ENABLED) 활성화를 주간회의에서 검토
    (§9 사전등록 원칙 — 즉시 자동 적용 아님).
    """
    cr = VALIDATION_CAMPAIGN["grade_ev_inversion"]
    out = {"verdict": "INSUFFICIENT"}
    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT entry_ts,
                          COALESCE(NULLIF(grade,''),'?') AS grade,
                          COALESCE(net_pnl_krw, pnl_krw) AS pnl,
                          COALESCE(quantity, 0) AS qty
                   FROM trades
                   WHERE exit_ts >= ? AND grade IN ('A','B','C')""",
                (_campaign_start(),),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    # [367차, 제안4 편입] min(최대손실)·표준편차 보강 — 평균만으로는 "고르게 나쁨"과
    # "소수 초대형 손실이 평균을 끌어내리는 fat-tail"을 구분할 수 없다(0722 딥다이브:
    # A등급 4주 손실의 84%가 급행 풀스톱 9건에 집중). SQLite에 STDEV가 없어 Python에서
    # 계산 — numpy(이미 상단에서 import).
    #
    # [MW0601 405차 / P0-4] **진입 1건 단위로 병합.** trades는 부분청산을 같은 entry_ts로
    # 여러 행에 나눠 기록하므로 그대로 세면 TP1/TP2 부분청산이 각각 '승리' 표본으로 잡혀
    # 승률이 부풀려진다 — [21] direction_ev_watch가 이미 같은 이유로 병합하며 docstring에
    # "402차가 실제로 이 함정에 걸렸다"까지 적어뒀는데, 그 미러인 이 채널에는 적용이
    # 누락돼 있었다. 편향은 랜덤이 아니라 **한 방향**이다: 부분청산은 TP1에 닿은 포지션에서만
    # 생기므로(손실은 하드스톱 한 번으로 끝나 항상 1행) 잉여 표본이 승자 쪽에 쏠린다.
    # MW0601 실측(캠페인 구간): C등급 승률 47.1%→42.9%, 표본 A 56→52 / C 17→14.
    # **판정식(A 평균 순EV < 0 → FAIL)은 무변경** — 집계 단위 정정은 계측 버그 수정이지
    # 합격선 변경이 아니므로 §9-4 검증 시계 리셋 대상이 아니다(404차 후속11의 캠페인
    # 상시 전환이 같은 논리로 처리된 전례). 표본 축소로 min_samples 미달이 나면 그것이
    # 정상이며 되돌리지 말 것 — 원래 판정할 표본이 없었던 것이다.
    # 근거: docs/정기점검/매일점검/MW0601-20260731-점검리포트.md §9-2.
    # [MW0601 409차 / R5] 계약수도 함께 병합한다. **`quantity`는 청산 행별 계약수이지
    # 포지션 크기가 아니다** — 부분청산 포지션은 여러 행에 나뉘어 있으므로 포지션
    # 크기는 `sum`이다(실측: `2026-07-10 11:37:04` → TP1 부분청산 2 + 하드스톱 3 = 5계약).
    # max로 세면 5계약 포지션이 3계약으로 잡힌다.
    from collections import defaultdict
    _merged = defaultdict(lambda: {"grade": None, "pnl": 0.0, "qty": 0})
    for row in rows:
        k = (row["entry_ts"], row["grade"])
        _merged[k]["grade"] = row["grade"]
        _merged[k]["pnl"] += float(row["pnl"] or 0.0)
        _merged[k]["qty"] += int(row["qty"] or 0)

    pnl_by_grade = defaultdict(list)
    qty_by_grade = defaultdict(list)
    for v in _merged.values():
        pnl_by_grade[v["grade"]].append(v["pnl"])
        qty_by_grade[v["grade"]].append((v["qty"], v["pnl"]))
    out["n_entries_merged"] = len(_merged)
    out["n_exit_events"] = len(rows)

    by_grade = {}
    for g, pnls in pnl_by_grade.items():
        arr = np.array(pnls, dtype=float)
        by_grade[g] = {
            "n": len(pnls),
            "avg_pnl_krw": round(float(arr.mean()), 0),
            "total_pnl_krw": round(float(arr.sum()), 0),
            "win_rate": round(float((arr > 0).mean()), 4),
            "min_pnl_krw": round(float(arr.min()), 0),
            "stdev_pnl_krw": round(float(arr.std(ddof=1)) if len(pnls) > 1 else 0.0, 0),
        }
    out["by_grade"] = by_grade

    # [MW0601 409차 / R5] 등급 × 계약수 교차 분해 — **표시 전용, 판정 미반영**.
    #
    # 0802 PC 대조에서 A등급 총손실이 MW0601 −3,986,335원 vs MW0602 −488,009원으로
    # 8.2배 갈렸다. 원인을 캠페인 구간 실측으로 분해한 결과, 이 채널이 "등급별" EV
    # 역전으로 부르는 현상이 **계약수 축으로 더 잘 설명된다**:
    #   A: qty≤2 48건 +1,311,796원(평균 +27,329)  /  qty≥3 4건 −5,298,131원(4전 1승)
    #   C: qty≤2 11건   −352,072원(평균 −32,007)  /  qty≥3 3건   +603,890원(3전 2승)
    # 즉 **qty≤2로 한정하면 A(+27,329) > C(−32,007)로 역전이 사라진다.**
    # A가 적자인 이유는 A등급이 큰 계약수를 더 많이 받았기 때문이지 등급 자체가
    # 역예측이기 때문이 아닐 수 있다 — 그렇다면 GradeEVGuard(등급 강등)는 잘못된
    # 처방이고, 0801 결정 "부결 — GradeEVGuard 활성화하지 않음"이 옳다.
    #
    # ⚠ 그러나 qty≥3 표본이 A 4건 / C 3건으로 **극히 얇다**(313차: 이걸로 확정 결론
    # 금지). C의 qty≥3이 흑자인 것은 CLAUDE.md 전환기준 ⑧이 인용하는 §9-3
    # "3계약 이상 16전 1승"과 방향이 다른데, 그쪽은 전체 기간이고 이쪽은 캠페인
    # 구간(_campaign_start 이후)이라 모집단이 다르다. **판정식은 건드리지 않는다**
    # (A 평균 순EV < 0 → FAIL 그대로) — 이 분해는 그 FAIL을 어떻게 읽을지에 대한
    # 맥락일 뿐이다. 계약수 축 판정은 [28] sizing_inversion_watch가 맡는다.
    def _qty_stats(pairs: list) -> dict:
        if not pairs:
            return {}
        arr = np.array([p for _, p in pairs], dtype=float)
        return {
            "n": len(pairs),
            "n_win": int((arr > 0).sum()),
            "total_pnl_krw": round(float(arr.sum()), 0),
            "avg_pnl_krw": round(float(arr.mean()), 0),
        }

    by_grade_qty, qty_split = {}, {}
    for g, pairs in qty_by_grade.items():
        _buckets = defaultdict(list)
        for q, p in pairs:
            _buckets[q].append((q, p))
        by_grade_qty[g] = {str(q): _qty_stats(v) for q, v in sorted(_buckets.items())}
        qty_split[g] = {
            "le2": _qty_stats([(q, p) for q, p in pairs if q <= 2]),
            "ge3": _qty_stats([(q, p) for q, p in pairs if q >= 3]),
        }
    out["by_grade_qty"] = by_grade_qty
    out["qty_split"] = qty_split
    # qty≤2 한정으로 A/C 역전이 유지되는지 — 리포트가 한 줄로 답하게 한다.
    _a2 = (qty_split.get("A") or {}).get("le2") or {}
    _c2 = (qty_split.get("C") or {}).get("le2") or {}
    if _a2.get("n") and _c2.get("n"):
        out["inversion_persists_qty_le2"] = bool(
            _a2["avg_pnl_krw"] < _c2["avg_pnl_krw"])

    min_n = int(cr["min_samples_per_grade"])
    a = by_grade.get("A")
    c = by_grade.get("C")
    if not a or a["n"] < min_n or not c or c["n"] < min_n:
        _a_n = a["n"] if a else 0
        _c_n = c["n"] if c else 0
        out["reason"] = (
            "등급별 표본 부족 (A=%d, C=%d, 각각 %d 필요) — 판정 보류" %
            (_a_n, _c_n, min_n)
        )
        return out

    out["verdict"] = "FAIL" if a["avg_pnl_krw"] < 0 else "PASS"
    if out["verdict"] == "FAIL":
        out["recommendation"] = (
            "A등급 누적 순EV 음수 확정(C등급은 양수) — GradeEVGuard "
            "(config.settings.GRADE_EV_GUARD_ENABLED) 활성화를 주간회의에서 검토"
            " (§9 사전등록 원칙에 따라 적용은 수동 결정)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# 리포트 생성
# ──────────────────────────────────────────────────────────────

def _fmt_verdict(v: str) -> str:
    return {
        "PASS": "✅ PASS", "FAIL": "❌ FAIL",
        "OK": "✅ OK", "STARVED": "🚨 STARVED",
        "OBSERVE": "👁 OBSERVE",  # [367차] 순수 관찰 채널(정책 게이트 없음) — PASS/FAIL 미판정
        # [379차] RegimeExhaustionGate 전용 — 하드 차단이 없어 PASS/FAIL 대신 가설
        # 지지/기각으로 표기(resolve_and_eval_regime_exhaustion() 참조)
        "SUPPORTS_GATE": "🔶 SUPPORTS_GATE",
        "REJECTS_GATE": "🔷 REJECTS_GATE",
        # [MW0602 424차 후속] [35]~[37] 전용 — PASS/FAIL로 표기할 수 없는 채널들.
        # 이 셋은 "조치가 필요한가"가 아니라 **어느 방향으로 필요한가**가 결론이다.
        #   [35] 유령 청산이 결함인가 알파인가 — 방향에 따라 처방이 정반대다
        #        (SUPPORTS=정책 승격 / REJECTS=가드 활성화).
        #   [36] 0803 P2의 "X 승격 조이기" 제안을 지지하는가 기각하는가.
        #   [37] [29]의 포지션단위 FAIL을 일자단위가 뒷받침하는가.
        # PASS/FAIL 어휘를 쓰면 "FAIL이니 조여라"로 자동 오독된다 — 실제로 [6]
        # Hurst 완화 권고가 그렇게 3주간 오독됐다(404차 후속11).
        "SUPPORTS_HYP": "🔶 SUPPORTS_HYP",
        "REJECTS_HYP": "🔷 REJECTS_HYP",
        # [MW0602 435차, 47] 재현충실도 게이트가 정지시킨 채널. FAIL/PASS 어느 쪽으로도
        # 읽으면 안 된다 — "판정 재료가 유효하지 않다"는 뜻이다. 데이터·사전등록은 보존.
        "SUSPENDED": "⏸ SUSPENDED(계측 무효)",
        # [MW0602 435차, 47] 게이트 자신의 판정
        "SUSPEND": "⏸ SUSPEND(하위 정지)",
        # [MW0601 457차 / G4·A3] 방향 편향·비용 엣지 전용.
        #   ALERT_BIAS는 **"뒤집어라"가 아니다.** 판정문에 역방향 적중률이 함께
        #   실려 있고 A1 실측은 반전 시 적중률이 **떨어짐**을 보였다(3m 0.347→0.337).
        #   조치 축은 방향 반전이 아니라 **절편 보정**이다. 위 [35]~[37] 주석이
        #   경고한 "FAIL이니 조여라" 자동 오독과 같은 함정을 피하려고 별도 어휘를 쓴다.
        "ALERT_BIAS": "🟠 ALERT_BIAS(절편 편향)",
        #   소급 구간을 포함한 실행 — 사전등록 판정으로 승격하지 않는다.
        "BACKFILL_ADVISORY": "🔎 BACKFILL_ADVISORY(소급·참고용)",
        # [MW0601 471차 후속7 / G-2, 54(구 51 — 487차 F-9 재배정)] ConstOut 빈발일의
        #   동일 호라이즌 진입 열위.
        #   **"그 호라이즌을 막아라"가 아니다** — 처방 축은 라우터 선택 억제·재학습
        #   스케줄·피처셋 조사다. 위 ALERT_BIAS와 같은 이유로 별도 어휘를 쓴다
        #   (FAIL 어휘를 쓰면 316~318차 HurstGate FalseBlock을 반복한다).
        # ⚠ 이 표에 없는 verdict는 조용히 "INSUFFICIENT"로 표시된다 — 새 채널을
        #   추가할 때 여기 등록을 빠뜨리면 판정이 사라진 것처럼 보인다.
        "FLAG_DRAG": "🟠 FLAG_DRAG(호라이즌 열위)",
        # [MW0602 486차 / 1-9, 55] 차단 게이트의 **정당성** 어휘.
        #   묻는 것이 "성능이 기준을 넘었는가"가 아니라 "차단이 정당한가"라
        #   PASS/FAIL을 쓰지 않는다(spread_extreme_watch와 같은 근거).
        #   ⚠ BLOCK_UNJUSTIFIED 는 **"즉시 제거하라"가 아니다** — 주간회의 상정
        #     자격일 뿐이고 집행은 §9 소관이다. 위 ALERT_BIAS·FLAG_DRAG와 같은
        #     이유로 별도 어휘를 둔다(FAIL 어휘를 쓰면 316~318차 HurstGate
        #     FalseBlock을 반복한다).
        "BLOCK_JUSTIFIED": "🛡 BLOCK_JUSTIFIED(차단 정당)",
        "BLOCK_UNJUSTIFIED": "🟠 BLOCK_UNJUSTIFIED(차단 근거 없음·상정 자격)",
        # [MW0602 489차 / D2, 56] CB② 복원 **방향** 어휘.
        #   묻는 것이 "성능이 기준을 넘었는가"가 아니라 "복원이 어느 방향인가"라
        #   PASS/FAIL을 쓰지 않는다(위 BLOCK_* 와 같은 근거).
        #   ⚠ RESTORE_COSTS 는 **"복원하지 말라"가 아니다** — CB②는 손익 장치가
        #     아니라 실전 자본의 꼬리위험 장치다. 이 채널은 그 대가를 계량할 뿐이고,
        #     복원 시점은 실전 전환 기준 ⑧에 사건으로 묶여 있다(절대원칙 §2).
        #   ⚠ SPLIT_BY_LIMIT 는 복원값 2와 3이 **서로 반대 방향**이라는 뜻이다.
        #     절대원칙 §2가 "2~3"이라 적어둔 범위 안에서 결론이 갈리므로,
        #     이 판정이 뜨면 **값을 먼저 정하지 말고 그 사실을 안건으로 올릴 것.**
        "RESTORE_FAVORS_CB2": "🛡 RESTORE_FAVORS_CB2(복원이 손실을 막는다)",
        "RESTORE_COSTS": "🟠 RESTORE_COSTS(복원이 수익을 막는다)",
        "SPLIT_BY_LIMIT": "🔀 SPLIT_BY_LIMIT(복원값 2·3이 반대 방향)",
        "NO_EVIDENCE": "➖ NO_EVIDENCE(표본은 찼으나 관문 미충족)",
        # [MW0602 487차 / F-8(B)] 생산부가 이 브랜치에 없는 채널 전용 —
        #   INSUFFICIENT("표본이 쌓이는 중")로 읽으면 안 된다. **표본은 오지 않는다.**
        #   0821 이상점 1-17: [50]/[54] 생산부 커밋(080c982)이 v9-dev 전용인데
        #   소비부만 dev에 들어와 매주 INSUFFICIENT 오독이 재생산되던 것을 끊는다.
        "NOT_AVAILABLE_ON_THIS_BRANCH": "🚫 NOT_AVAILABLE(브랜치 생산부 없음)",
    }.get(v, "⏳ INSUFFICIENT")


def _dm(key: str) -> str:
    """[404차 후속11] 확정 결정 인라인 마커 — 요약표 '핵심 수치' 끝에 덧붙인다.

    왜 필요한가: 캠페인 리포트의 권고·판정은 **조치 여부와 무관하게 매주 재출력**된다.
    [6] hurst_gate_shadow는 2026-07-15에 완화가 배포돼 라이브 중인데도 3주째 "완화
    권고"가 그대로 찍혔고, 0801 결산 초안이 그걸 신규 안건으로 잘못 올렸다. 반대로
    "FAIL이지만 일부러 적용하지 않기로 했다"는 결정은 아무 데도 남지 않아 다음 세션이
    같은 FAIL을 보고 적용을 재시도할 위험이 있었다.

    판정 로직에는 관여하지 않는다 — verdict는 사전등록 기준으로만 계산되고, 이 마커는
    "그래서 사람이 무엇을 결정했나"만 덧붙인다. 출처는 config.settings의
    VALIDATION_CAMPAIGN_DECISIONS이며 결정이 바뀌면 그쪽을 갱신할 것(§9).
    """
    d = VALIDATION_CAMPAIGN_DECISIONS.get(key)
    if not d:
        return ""
    return "  📌 **%s** (%s)" % (d["decision"], d["date"])


def _fmt_channel_verdict(out: dict) -> str:
    """[357차] INSUFFICIENT(표본 축적 대기)와 NO-DATA(소스 적재 자체가 0 — 계측
    사망 의심)를 구분 표기. [2]/[3] 채널이 스코어러 로드 실패로 캠페인 전 기간
    표본 0이었는데 '표본 부족'으로만 표시돼 2주간 발견되지 못한 재발 방지.
    판정값(metrics json의 verdict)은 사전등록 어휘 그대로 유지 — 표시만 구분."""
    if out.get("no_data"):
        return "🔴 NO-DATA(계측 점검 필요)"
    return _fmt_verdict(out.get("verdict", ""))


def build_report(days: int) -> tuple:
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # [MW0602 468차 G-3] 청산 2축 컬럼 보강 — main.py 기동 마이그레이션의 백스톱.
    # 리포트가 앱 재기동보다 먼저 도는 PC/백업 DB에서 채널이 조용히 죽는 것을 막는다.
    _ensure_trades_exit_axis_columns()
    ss = eval_sample_starvation()
    tb = eval_tb_channel(days)
    mg = eval_meta_gate_channel(days)
    qt = eval_quantile_channel(days)
    sd = resolve_and_eval_signal_decay()
    hr = eval_hurst_regime()
    hg = resolve_and_eval_hurst_gate()
    jg = resolve_and_eval_joint_gate()
    ks = eval_kelly_skip_grade_c()
    og = resolve_and_eval_open_gap()
    txb = resolve_and_eval_toxicity_block()
    t2 = resolve_and_eval_tp2_hold()
    lt1 = resolve_and_eval_loss_tier1_qty1_shadow()
    t1t = resolve_and_eval_tp1_trail_shadow()
    gei = eval_grade_ev_inversion()
    lt2 = resolve_and_eval_loss_tier2_remainder_shadow()
    frw = eval_fast_reversal_watch(days)
    cfc = eval_chase_foreign_combo_watch()
    efs = eval_exit_fill_slippage_watch(days)
    reg = resolve_and_eval_regime_exhaustion()
    wcw = eval_weight_collapse_watch(days)
    msz = eval_meta_size_zero_shadow()        # [34] MW0601 422차 후속
    dev = eval_direction_ev_watch()
    mcw = eval_mfe_capture_watch()
    gsc = eval_guard_shadow_channel(days)
    icw = eval_intraday_cv_watch(days)
    tpg = eval_tp1_protect_giveback_watch()
    lpw = eval_limit_pin_watch()
    ucw = eval_unreachable_cf_watch()
    siw = eval_sizing_inversion_watch()      # [28] MW0601 405차 P1-2
    mrs = eval_mean_revert_size_watch()      # [29] MW0601 405차 P1-3
    trw = eval_toxicity_recalib_watch()      # [30] MW0601 419차 P0
    trm = eval_toxicity_reduce_mult_shadow()  # [31] MW0601 419차 P1
    pse = eval_phantom_stop_edge()           # [35] MW0602 424차 후속
    gxp = eval_grade_x_promotion()           # [36] MW0602 424차 후속
    hmd = eval_hurst_meanrevert_drag()       # [37] MW0602 424차 후속
    pgl = eval_profit_guard_l1_watch()       # [38] MW0602 426차
    cdw = eval_conf_discrimination_watch()   # [39] MW0602 427차
    dvw = eval_direction_value_watch()       # [40] MW0602 428차
    emw = eval_exit_model_watch()            # [41] MW0602 428차
    etv = eval_entry_timing_value_watch()    # [42] MW0602 429차
    vew = eval_vol_estimator_watch()         # [43] MW0602 429차
    dcf = eval_dynmc_collapse_feed_watch()   # [44] MW0602 430차
    cgf = eval_cal_guard_flap_watch()        # [45] MW0602 430차
    # [51]~[53] MW0602 462차 — 0811 점검 P4 신설. 셋 다 표본 미달 등록 상태다.
    # 개별 격리: 신설 채널의 예외가 리포트 전체를 죽이면 안 된다(기존 관례).
    def _safe_eval(fn, label):
        try:
            return fn()
        except Exception as e:
            return {"verdict": "INSUFFICIENT",
                    "error": "%s: %s" % (type(e).__name__, e),
                    "reason": "%s 평가 실패" % label}
    pgv = _safe_eval(eval_profit_geometry_lowvol_watch, "[51]")
    efw = _safe_eval(eval_effective_weight_watch, "[52]")
    zbb = _safe_eval(eval_zone_ban_breach_watch, "[53]")
    off = eval_offline_geometry_channels()
    # [MW0602 435차] [48]/[49] — 둘 다 **시뮬레이터를 쓰지 않는다**(trades /
    # exit_fill_slippage 실측). 그래서 §47 게이트가 SUSPEND여도 계속 판정한다.
    # 스크립트 실패가 리포트를 죽이면 안 되므로 각각 격리한다(기존 관례와 동일).
    def _safe_channel(mod, label):
        try:
            import importlib
            m = importlib.import_module(mod)
            return m.summarize(m.compute(_campaign_start()[:10]))
        except Exception as e:
            return {"verdict": "INSUFFICIENT",
                    "error": "%s: %s" % (type(e).__name__, e),
                    "reason": "%s 실행 실패" % label}
    bsp = _safe_channel("scripts.bar_stop_path_watch", "[48]")
    pgw = _safe_channel("scripts.payoff_geometry_watch", "[49]")
    # [MW0602 487차 / F-8(B)] 채널 [50]·[54]는 **생산부가 v9-dev에만 있다**
    # (0821 이상점 1-17: 생산부 커밋 080c982 미이식 — [50]은
    # scripts/direction_bias_watch.py 파일 자체가 없고, [54]는
    # scaler_daily.const_out_by_horizon 컬럼이 없어 전 구간 미측정이다).
    # 2026-08-23 멀티PC 정책 폐기(487차)로 체리픽 경로가 닫혔으므로 INSUFFICIENT
    # ("표본이 쌓이는 중") 오독이 나지 않게 NOT_AVAILABLE_ON_THIS_BRANCH 로 분리
    # 표기한다. 생산부가 이 브랜치에 생기면(자체 재구현 — P3 백로그) 아래 감지가
    # 저절로 참이 되어 채널이 되살아난다 — 이 코드를 다시 손볼 필요가 없다.
    def _branch_unavailable(label, missing):
        return {"verdict": "NOT_AVAILABLE_ON_THIS_BRANCH",
                "reason": "%s 생산부가 이 브랜치에 없음 — %s. "
                          "체리픽 안 함(487차 결정) · 자체 재구현은 P3 백로그" % (label, missing)}

    def _has_module(name):
        try:
            import importlib.util
            return importlib.util.find_spec(name) is not None
        except Exception:
            return False

    def _has_const_out_column():
        try:
            import sqlite3
            from config.settings import SCALER_MONITOR_DB
            with sqlite3.connect(SCALER_MONITOR_DB) as _c:
                _cols = [r[1] for r in _c.execute("PRAGMA table_info(scaler_daily)")]
            return "const_out_by_horizon" in _cols
        except Exception:
            return False

    # [MW0601 457차 / G4] 방향 편향 상시 감시. predictions.db만 읽고 시뮬레이터를
    # 쓰지 않으므로 §47 게이트가 SUSPEND여도 계속 판정한다([48]/[49]와 같은 이유).
    dbw = (_safe_channel("scripts.direction_bias_watch", "[50]")
           if _has_module("scripts.direction_bias_watch")
           else _branch_unavailable(
               "[50]", "scripts/direction_bias_watch.py (080c982, v9-dev 전용)"))
    # [MW0601 471차 후속7 / G-2] ConstOut 호라이즌 건강도. scaler_monitor.db(457차 G5가
    # 이미 쌓고 있던 집계)와 trades만 읽고 시뮬레이터를 쓰지 않으므로 §47 게이트가
    # SUSPEND여도 계속 판정한다([48]/[49]/[50]과 같은 이유).
    # 채널 번호 [54] — 구 [51]이 462차 저변동성 채널과 충돌해 재배정(487차 F-9,
    # 선착 우선). 채널 키 문자열(`const_out_horizon_watch`)은 불변 — 이력 식별자다.
    cow = (_safe_channel("scripts.const_out_horizon_watch", "[54]")
           if _has_const_out_column()
           else _branch_unavailable(
               "[54]", "scaler_daily.const_out_by_horizon 컬럼 (457차 G5, v9-dev 전용)"))
    # [MW0602 486차 / 1-9] 09:20~09:29 "앙상블 A등급만 허용" 게이트 소급 판정.
    # predictions.db + raw_candles 만 읽고 라이브 배선이 없다 — 노출을 늘리지 않는
    # 순수 관찰 채널이라 §47 게이트가 SUSPEND여도 계속 판정한다([48]~[54]와 같은 이유).
    ewg = _safe_channel("scripts.early_window_gate_shadow", "[55]")
    # [MW0602 489차 / 0823 주간회의 D2] CB② 복원 반사실. trades.db만 읽고 라이브
    # 배선이 없다 — 노출을 늘리지 않는 순수 관찰 채널이라 §47 게이트가 SUSPEND여도
    # 계속 판정한다([48]~[55]와 같은 이유).
    # ⚠ 이 채널은 **로그가 아니라 DB에서 현행 규칙(포지션 단위, 470차 C1)으로
    #   재구성**한다. `[CB] 연속 손절 N회` 로그는 2026-08-14 이전이 레그 단위라
    #   과대계상된다 — 스크립트 docstring의 대조표 참조.
    cb2 = _safe_channel("scripts.cb2_restore_shadow", "[56]")

    metrics = {
        "generated_at": now_str,
        "days": days,
        "criteria": VALIDATION_CAMPAIGN,
        "sample_starvation": ss,
        "tb": tb, "meta_gate": mg, "quantile": qt,
        "signal_decay": sd, "hurst_regime": hr, "hurst_gate_shadow": hg,
        "joint_gate_shadow": jg, "kelly_skip": ks, "open_gap_shadow": og,
        "tp2_hold_shadow": t2, "loss_tier1_qty1_shadow": lt1,
        "tp1_trail_shadow": t1t, "grade_ev_inversion": gei,
        "loss_tier2_remainder_shadow": lt2, "fast_reversal_watch": frw,
        "chase_foreign_combo_watch": cfc, "exit_fill_slippage_watch": efs,
        "regime_exhaustion_watch": reg, "toxicity_block_shadow": txb,
        "weight_collapse_watch": wcw,
        "direction_ev_watch": dev, "mfe_capture_watch": mcw,
        "guard_shadow": gsc, "intraday_cv_watch": icw,
        "tp1_protect_giveback_watch": tpg,
        "limit_pin_watch": lpw, "unreachable_cf_watch": ucw,
        "sizing_inversion_watch": siw, "mean_revert_size_watch": mrs,
        "toxicity_recalib_watch": trw, "toxicity_reduce_mult_shadow": trm,
        "phantom_stop_edge": pse, "grade_x_promotion": gxp,
        "hurst_meanrevert_drag": hmd, "profit_guard_l1_watch": pgl,
        "conf_discrimination_watch": cdw, "direction_value_watch": dvw,
        "exit_model_watch": emw,
        "entry_timing_value_watch": etv, "vol_estimator_watch": vew,
        "dynmc_collapse_feed_watch": dcf, "cal_guard_flap_watch": cgf,
        # [MW0602 462차] 0811 점검 P4 신설 3채널
        "profit_geometry_lowvol_watch": pgv,
        "effective_weight_watch": efw,
        "zone_ban_breach_watch": zbb,
        # [430차] conf 스케일 불연속 — 분석 창이 걸치는 경계를 metrics에도 남긴다.
        # PC간 대조 스크립트(cmp_metrics.py)가 "코드 세대 차이"와 같은 이유로
        # "체제 차이"도 구분할 수 있어야 한다.
        "conf_scale_breaks_in_window": [
            {k: b.get(k) for k in ("date", "label")}
            for b in _conf_scale_breaks_in(VALIDATION_CAMPAIGN.get("start_date", ""))
        ],
        "tp1_geometry_shadow": off.get("tp1_geometry_shadow"),
        "tp1_protect_offset_shadow": off.get("tp1_protect_offset_shadow"),
        "quantile_tp_shadow": off.get("quantile_tp_shadow"),
        # [MW0602 435차] 신규 3채널. [47]은 게이트, [48]/[49]는 **시뮬 무관**이라
        # 게이트가 SUSPEND여도 계속 판정한다.
        "sim_fidelity_gate": off.get("_sim_fidelity_gate"),
        "bar_stop_path_watch": bsp,
        "payoff_geometry_watch": pgw,
        "direction_bias_watch": dbw,   # [MW0601 457차 / G4]
        "const_out_horizon_watch": cow,  # [MW0601 471차 후속7 / G-2]
        "early_window_gate_shadow": ewg,  # [MW0602 486차 / 1-9] — 채널 [55]
        "cb2_restore_shadow": cb2,        # [MW0602 489차 / D2]  — 채널 [56]
    }

    L = []
    L.append("# 검증 캠페인 주간 판정 리포트")
    L.append("")
    L.append("- 생성: %s  (분석 창 %d일, 캠페인 시작 %s)" % (
        now_str, days, VALIDATION_CAMPAIGN.get("start_date")))
    L.append("- 합격선: `config/settings.py:VALIDATION_CAMPAIGN` (사전 등록 — 변경 금지)")
    L.append("- 근거: `docs/260705_OFFENSE_READINESS_AUDIT_AND_NEXT_PHASE.md` §3")
    if VALIDATION_CAMPAIGN.get("mode") == "standing":
        L.append("- **운영 모드: 상시(standing)** — %s 전환. 4주 기한 없이 계속 생성하며, "
                 "채널별로 min_samples 도달 시점에 개별 판정한다. **합격선·판정문은 무변경**"
                 "(§9-4 — 상시 전환은 거버넌스 결정이지 판정 기준 변경이 아니다)."
                 % VALIDATION_CAMPAIGN.get("mode_changed_on", "—"))
    L.append("- 📌 표시가 붙은 채널은 **주간회의에서 확정된 결정이 있다** — 하단 "
             "\"확정 결정 레지스트리\" 참조. 판정(verdict)과 결정은 별개다.")
    L.append("")
    # [MW0602 430차 / P0-1] conf 스케일 불연속 경고 — 창이 경계를 걸칠 때만 뜬다.
    # 캠페인 창(start_date~)을 기준으로 판단한다: 대부분의 채널이 그 창을 쓴다.
    _csb = _conf_scale_break_lines(VALIDATION_CAMPAIGN.get("start_date", ""))
    if _csb:
        L.extend(_csb)
        L.append("")
    L.append("| 채널 | 판정 | 핵심 수치 |")
    L.append("|---|---|---|")
    L.append("| [0] 표본 기아 경보 | %s | 주간진입=%s건(하한 %s) 4주투영=%s건 |" % (
        _fmt_verdict(ss["verdict"]), ss.get("n_weekly_entries", "—"),
        ss.get("floor", "—"), ss.get("projected_28d_entries", "—")))
    L.append("| [1] Triple-Barrier | %s | 합격 호라이즌 %d개 (기준 %d개) |" % (
        _fmt_verdict(tb["verdict"]), tb.get("n_pass", 0),
        VALIDATION_CAMPAIGN["tb"]["min_horizons_pass"]))
    # [463차] 스코어링 호라이즌 경계 배지 — 표시 전용, 판정 무관여.
    _mg_brk = ""
    if mg.get("scoring_break_caveat"):
        _mg_brk = " 🔴 `[스코어러 경계 %s: 이전 %s건 / 이후 %s건]`" % (
            mg.get("scoring_break_date", "—"),
            mg.get("n_pre_break", "—"), mg.get("n_post_break", "—"))
    L.append("| [2] Meta-Gate | %s | 상위EV=%s 분리도=%s (필요 %s)%s%s |" % (
        _fmt_channel_verdict(mg), mg.get("top_ev_pt", "—"),
        mg.get("separation_pt", "—"), mg.get("required_sep_pt", "—"),
        _mg_brk, _dm("meta_gate")))
    L.append("| [3] 분위 회귀 | %s | 커버리지=%s (밴드 %s) 상관=%s |" % (
        _fmt_channel_verdict(qt), qt.get("coverage", "—"),
        qt.get("coverage_band", "—"), qt.get("unc_corr", "—")))
    _qd = qt.get("dir") or {}
    _g3b = off.get("quantile_tp_shadow") or {}
    L.append("| [3-A] q50 방향 적중률 (관찰) | %s | 적중=%s (n=%s) 상위30%%=%s q50양수비율=%s |" % (
        _fmt_verdict("OBSERVE"),
        ("%.1f%%" % (_qd["hit_rate"] * 100)) if _qd.get("hit_rate") is not None else "—",
        _qd.get("n", 0),
        ("%.1f%%" % (_qd["conf_top30_hit"] * 100)) if _qd.get("conf_top30_hit") is not None else "—",
        ("%.1f%%" % (_qd["q50_pos_share"] * 100)) if _qd.get("q50_pos_share") is not None else "—"))
    L.append("| [3-B] 분위회귀 TP1 거리 A/B | %s | %s (진입 %s건/%s일)%s |" % (
        _fmt_verdict(_g3b.get("verdict", "")), _g3b.get("reason", _g3b.get("error", "—")),
        _g3b.get("n_trades", "—"), _g3b.get("n_days", "—"), _dm("quantile_tp_shadow")))
    # [MW0601 409차 / R2] 마커 배선 — 이 행은 404차 후속11 당시 _dm()이 빠져 있었다.
    L.append("| [4] 신호소멸청산 | %s | 누적 saved=%spt (n=%s, 보류 %s)%s |" % (
        _fmt_verdict(sd["verdict"]), sd.get("total_saved_pts", "—"),
        sd.get("n_resolved", 0), sd.get("n_pending", 0), _dm("signal_decay")))
    L.append("| [5] 레짐 ATR 배수 | %s | %s%s |" % (
        _fmt_verdict(hr["verdict"]),
        " / ".join("%s: n=%d EV=%s원" % (b, v["n"], format(v["avg_ev_krw"], ",.0f"))
                   for b, v in sorted(hr.get("buckets", {}).items())) or "거래 없음",
        _dm("hurst_regime")))
    L.append("| [6] Hurst 게이트 counterfactual | %s | 누적 hyp=%spt 승률=%s (n=%s, 보류 %s)%s |" % (
        _fmt_verdict(hg["verdict"]), hg.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (hg["win_rate"] * 100)) if "win_rate" in hg else "—",
        hg.get("n_resolved", 0), hg.get("n_pending", 0), _dm("hurst_gate_shadow")))
    # [MW0601 420차] verdict 옆에 증거강도·체제·취약성을 같이 띄운다 — 요약표만 보고
    # "PASS = 차단이 옳다"로 읽히는 것이 이 채널의 실제 오독 경로였다.
    _jg_tags = []
    if jg.get("evidence") == "NO_EVIDENCE":
        _jg_tags.append("⚠증거없음(t=%s)" % jg.get("episode", {}).get("t_stat", "—"))
    elif jg.get("evidence"):
        _jg_tags.append("%s(t=%s)" % (jg["evidence"],
                                      jg.get("episode", {}).get("t_stat", "—")))
    if jg.get("judged_regime") == "pre":
        _jg_tags.append("구tox체제")
    if jg.get("jackknife", {}).get("fragile"):
        _jg_tags.append("단일일취약")
    L.append("| [7] JointGateBlock counterfactual | %s | 누적 hyp=%spt 승률=%s (n=%s, 보류 %s)%s |" % (
        _fmt_verdict(jg["verdict"]), jg.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (jg["win_rate"] * 100)) if "win_rate" in jg else "—",
        jg.get("n_resolved", 0), jg.get("n_pending", 0),
        (" · " + " · ".join(_jg_tags)) if _jg_tags else ""))
    L.append("| [8] KellyAdvisedSkip×C등급 | %s | 누적 순PnL=%s원 승률=%s (n=%s)%s |" % (
        _fmt_verdict(ks["verdict"]),
        format(ks["total_pnl_krw"], ",.0f") if "total_pnl_krw" in ks else "—",
        ("%.1f%%" % (ks["win_rate"] * 100)) if "win_rate" in ks else "—",
        ks.get("n", 0), _dm("kelly_skip")))
    L.append("| [9] OPEN_VOLATILE 시가이격 counterfactual | %s | 누적 hyp=%spt 승률=%s (n=%s, 보류 %s) |" % (
        _fmt_verdict(og["verdict"]), og.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (og["win_rate"] * 100)) if "win_rate" in og else "—",
        og.get("n_resolved", 0), og.get("n_pending", 0)))
    L.append("| [10] TP2 홀드 counterfactual (qty=2 재배분 A/B) | %s | 누적 hyp=%spt 승률=%s "
              "(n=%s, 보류 %s) TP3=%s건 트레일=%s건 강제청산=%s건 |" % (
        _fmt_verdict(t2["verdict"]), t2.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (t2["win_rate"] * 100)) if "win_rate" in t2 else "—",
        t2.get("n_resolved", 0), t2.get("n_pending", 0),
        t2.get("cf_tp3", "—"), t2.get("cf_trail_stop", "—"), t2.get("cf_force_exit", "—")))
    L.append("| [11] qty=1 손실1차 조기청산 counterfactual | %s | 누적 hyp=%spt 승률=%s "
             "(n=%s/%s일, 보류 %s) 일자 p=%s |" % (
        _fmt_verdict(lt1["verdict"]), lt1.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (lt1["win_rate"] * 100)) if "win_rate" in lt1 else "—",
        lt1.get("n_resolved", 0), lt1.get("days", "—"), lt1.get("n_pending", 0),
        lt1.get("sign_p", "—")))
    L.append("| [12] qty=1 TP1 이후 트레일 폭 counterfactual | %s | 누적 hyp=%spt 승률=%s "
              "(n=%s, 보류 %s) 트레일스톱=%s건 강제청산=%s건 |" % (
        _fmt_verdict(t1t["verdict"]), t1t.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (t1t["win_rate"] * 100)) if "win_rate" in t1t else "—",
        t1t.get("n_resolved", 0), t1t.get("n_pending", 0),
        t1t.get("cf_trail_stop", "—"), t1t.get("cf_force_exit", "—")))
    _gei_a = gei.get("by_grade", {}).get("A", {})
    _gei_c = gei.get("by_grade", {}).get("C", {})
    L.append("| [13] 등급별 순EV 역전 감시 | %s | A=%s원(n=%s, 최대손실=%s원) C=%s원(n=%s)%s |" % (
        _fmt_verdict(gei["verdict"]),
        format(_gei_a["avg_pnl_krw"], ",.0f") if _gei_a else "—", _gei_a.get("n", 0),
        format(_gei_a["min_pnl_krw"], ",.0f") if _gei_a else "—",
        format(_gei_c["avg_pnl_krw"], ",.0f") if _gei_c else "—", _gei_c.get("n", 0),
        _dm("grade_ev_inversion")))
    L.append("| [14] Tier1 잔여계약 2단계 조기청산 counterfactual | %s | 누적 hyp=%spt 승률=%s (n=%s, 보류 %s) |" % (
        _fmt_verdict(lt2["verdict"]), lt2.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (lt2["win_rate"] * 100)) if "win_rate" in lt2 else "—",
        lt2.get("n_resolved", 0), lt2.get("n_pending", 0)))
    _frw_a = frw.get("by_grade", {}).get("A", {})
    L.append("| [15] 급행 풀스톱(TP1 미도달) 관찰 | %s | 급행하드스톱=%s건 중 TP1미도달=%s건"
              " (A: n=%s 누적=%s원) |" % (
        _fmt_verdict(frw["verdict"]),
        frw.get("n_fast_hardstop", 0), frw.get("n_no_tp1", 0),
        _frw_a.get("n", 0),
        format(_frw_a["total_pnl_krw"], ",.0f") if _frw_a else "—"))
    L.append("| [16] chase+foreign 조합 관찰 | %s | 동시실패=%s건 누적=%s원 (매칭=%s건)%s |" % (
        _fmt_verdict(cfc["verdict"]),
        cfc.get("n_combo", 0),
        format(cfc["total_pnl_krw"], ",.0f") if cfc.get("n_combo") else "—",
        cfc.get("n_matched", 0), _dm("chase_foreign_combo_watch")))
    # [439차 P2] 헤드라인을 **유효-hint 기준**으로 바꾼다 — 풀링 평균은 봉중 경로
    # (hint가 허구)에 오염돼 음수로 끌려가 이 채널의 경보를 억제하고 있었다.
    L.append("| [17] 청산 체결 슬리피지 | %s | 유효-hint n=%s 일자평균=%spt / 이벤트 %spt "
             "(가정 %spt) · 봉중 %s건 제외 · 일자 p=%s |" % (
        _fmt_channel_verdict(efs),
        efs.get("n_valid", "—"), efs.get("avg_valid_day_pts", "—"),
        efs.get("avg_valid_pts", "—"), efs.get("assumed_slippage_pts_per_side", "—"),
        efs.get("n_bar_excluded", 0), efs.get("sign_p", "—")))
    L.append("| [18] RegimeExhaustionGate(탈진반전) | %s | 발동=%s건 누적hyp=%spt "
              "(STOP=%s/TP1=%s/NEITHER=%s)%s |" % (
        _fmt_verdict(reg["verdict"]),
        reg.get("n_resolved", 0),
        reg.get("total_hyp_pnl_pts", "—"),
        reg.get("cf_stop", 0), reg.get("cf_tp1", 0), reg.get("cf_neither", 0),
        _dm("regime_exhaustion_shadow")))
    L.append("| [19] ToxicityGate block counterfactual | %s | 누적 hyp=%spt 승률=%s (n=%s, 보류 %s) |" % (
        _fmt_verdict(txb["verdict"]), txb.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (txb["win_rate"] * 100)) if "win_rate" in txb else "—",
        txb.get("n_resolved", 0), txb.get("n_pending", 0)))
    L.append("| [20] BAR_ONLY_RELAX 수용/롤백 | %s | 완화후 collapse=%s (기준선 %s, 목표 %.0f%%±%.0f%%p) 계측일 전%s/후%s |" % (
        _fmt_verdict(wcw["verdict"]),
        ("%.1f%%" % (wcw["post_ratio"] * 100)) if wcw.get("post_ratio") is not None else "—",
        ("%.1f%%" % (wcw["baseline_ratio"] * 100)) if wcw.get("baseline_ratio") is not None else "—",
        float(VALIDATION_CAMPAIGN.get("weight_collapse_watch", {}).get("target_ratio", 0.20)) * 100,
        float(VALIDATION_CAMPAIGN.get("weight_collapse_watch", {}).get("target_tolerance", 0.07)) * 100,
        wcw.get("n_days_pre", 0), wcw.get("n_days_post", 0)))
    _dv = dev.get("by_direction", {})
    # [MW0601 409차 / R2] 마커 배선 — 위 [4]와 같은 이유.
    L.append("| [21] 방향별 순EV (SYSTEM_AUTO) | %s | %s%s |" % (
        _fmt_verdict(dev["verdict"]),
        " / ".join("%s: n=%d 평균=%s원 최대손실=%s원" % (
            d, _dv[d]["n"], format(_dv[d]["avg_pnl_krw"], ",.0f"),
            format(_dv[d]["min_pnl_krw"], ",.0f"))
            for d in ("LONG", "SHORT") if d in _dv) or "표본 없음",
        _dm("direction_ev_watch")))
    L.append("| [22] MFE 캡처율 관찰 | %s | 풀링캡처 보유내=%s 종가까지=%s / 평균잔여 %s pt (진입 %s건) |" % (
        _fmt_verdict(mcw["verdict"]),
        ("%.1f%%" % (mcw["capture_in_hold_pooled"] * 100)) if mcw.get("capture_in_hold_pooled") is not None else "—",
        ("%.1f%%" % (mcw["capture_to_close_pooled"] * 100)) if mcw.get("capture_to_close_pooled") is not None else "—",
        mcw.get("avg_left_to_close_pt", "—"), mcw.get("n_entries", 0)))
    L.append("| [23] EOD 모델가드 판정 괴리 | %s | missed_upgrade=%s (n=%s/%s, %d일) |" % (
        _fmt_channel_verdict(gsc),
        ("%.1f%%" % (gsc["missed_upgrade_rate"] * 100)) if gsc.get("missed_upgrade_rate") is not None else "—",
        gsc.get("missed_upgrade_n", "—"), gsc.get("n_fair", "—"), gsc.get("n_days", 0)))
    _g23 = off.get("tp1_geometry_shadow") or {}
    _g25 = off.get("tp1_protect_offset_shadow") or {}
    # ── [MW0602 435차] 신규 3채널 요약행. [47]을 **기하 채널들보다 먼저** 찍는다 —
    # 아래 [23-B]/[25]가 SUSPENDED로 보일 때 그 이유를 바로 위에서 읽게 하기 위함이다.
    _gate = off.get("_sim_fidelity_gate") or {}
    _gate_note = ""
    # [MW0601 441차] 조건부 부호경로가 판정을 바꾼 주에는 **표에서 바로 보이게** 한다.
    # 구 기준 그대로의 판정(verdict_strict_sign)과 갈리면 그 사실이 감사 대상이다(§9).
    if (_gate.get("verdict_strict_sign")
            and _gate.get("verdict_strict_sign") != _gate.get("verdict")):
        _gate_note = ("  ⚠ **구 기준(sign_match 무조건)으로는 `%s`** — 조건부 경로가 "
                      "판정을 바꿨다(441차)" % _gate["verdict_strict_sign"])
    L.append("| **[47] 시뮬 재현충실도 게이트** | %s | %s%s |" % (
        _fmt_verdict(_gate.get("verdict", "")), _gate.get("reason", "—"), _gate_note))
    _ovs = off.get("tp_fill_overshoot_watch") or {}
    L.append("| [47-B] TP 체결 오버슈트 (관찰) | %s | %s |" % (
        _fmt_verdict(_ovs.get("verdict", "")), _ovs.get("reason", "—")))
    L.append("| [48] 봉중 하드스톱 경로 건전성%s | %s | %s%s |" % (
        " ⚠사전등록오염" if bsp.get("prereg_contaminated") else "",
        _fmt_channel_verdict(bsp), bsp.get("reason", bsp.get("error", "—")),
        (" · 가드이전 %d / 이후 %d건 · 무발생 %d거래일" % (
            (bsp.get("pre_guard") or {}).get("n", 0),
            (bsp.get("post_guard") or {}).get("n", 0),
            bsp.get("bar_dry_days", 0))) if bsp.get("prereg_contaminated") else ""))
    _pk, _pr = (pgw.get("krw") or {}), (pgw.get("risk") or {})
    L.append("| [49] 페이오프 기하 상시 감시 | %s | %s%s |" % (
        _fmt_verdict(pgw.get("verdict", "")), pgw.get("reason", pgw.get("error", "—")),
        (" · 포지션 %s건/%s일 (레그 %s건)" % (pgw.get("n"), pgw.get("n_days"),
                                            pgw.get("n_legs"))) if pgw.get("n") else ""))
    # [MW0601 457차 / G4] 방향 편향 상시 감시. ALERT_BIAS는 "반전하라"가 아니다 —
    # 판정문에 역방향 적중률이 함께 실려 있으니 반드시 같이 읽을 것(A1 실측: 반전 시 하락).
    L.append("| [50] 방향 편향 상시 감시 | %s | %s |" % (
        _fmt_verdict(dbw.get("verdict", "")), dbw.get("reason", dbw.get("error", "—"))))
    # [MW0601 471차 후속7 / G-2] FLAG_DRAG는 "그 호라이즌을 막자"가 아니다 —
    # 판정문이 처방 축(라우터 억제·재학습 스케줄·피처셋 조사)을 함께 싣는다.
    # [MW0602 487차 / F-9] 구 [51] → [54] 재배정(462차 저변동성 채널이 선착).
    L.append("| [54] ConstOut 호라이즌 건강도 (구 [51]) | %s | %s |" % (
        _fmt_verdict(cow.get("verdict", "")), cow.get("reason", cow.get("error", "—"))))
    # [MW0602 486차 / 1-9] 09:20~09:29 게이트 소급 판정. 어휘가 PASS/FAIL이 아니라
    # BLOCK_JUSTIFIED / BLOCK_UNJUSTIFIED 다 — 묻는 것이 "성능"이 아니라 "차단의
    # 정당성"이기 때문(spread_extreme_watch와 같은 이유, HurstGate FalseBlock 전례).
    L.append("| [55] 09:20~09:29 A등급게이트 counterfactual | %s | %s `[1계약·TP1상한·미실현 시뮬]` |" % (
        _fmt_verdict(ewg.get("verdict", "")),
        ewg.get("headline") or ewg.get("reason", ewg.get("error", "—"))))
    # [MW0602 489차 / D2] CB② 복원 반사실. 단위는 **원(₩)** 이다 — pt 배지 채널과
    # 더하지 말 것. 어휘가 PASS/FAIL이 아닌 이유는 _fmt_verdict 주석 참조.
    L.append("| [56] CB② 복원 반사실 | %s | %s%s |" % (
        _fmt_verdict(cb2.get("verdict", "")),
        cb2.get("headline") or cb2.get("reason", cb2.get("error", "—")),
        _dm("cb2_restore_shadow")))
    L.append("| [23-B] TP1/손절 초기 기하 A/B | %s | %s (진입 %s건/%s일)%s |" % (
        _fmt_verdict(_g23.get("verdict", "")), _g23.get("reason", _g23.get("error", "—")),
        _g23.get("n_trades", "—"), _g23.get("n_days", "—"), _dm("tp1_geometry_shadow")))
    # [MW0601 406차 / D] 모드 라벨 필수 — 모드마다 보호스톱 기준선이 달라 수치를
    # 라벨 없이 인용하면 안 된다(0802 대조 §2-B: 부호가 반대로 나온다).
    _tpg_modes = tpg.get("by_mode") or {}
    if tpg.get("modes_mixed"):
        _tpg_tag = " ⚠ **모드 혼재**: " + "/".join(
            "%s %d" % kv for kv in sorted(_tpg_modes.items())) + " — 모드별 값은 상세 참조"
    elif _tpg_modes:
        _tpg_tag = " (mode=`%s`)" % list(_tpg_modes)[0]
    else:
        _tpg_tag = ""
    L.append("| [24] TP1 보호전환 반납 관찰 | %s | 중앙값 반납=%s pt (반납 %s / 달림 %s, n=%s)%s |" % (
        _fmt_verdict(tpg.get("verdict", "OBSERVE")),
        tpg.get("median_give_pt", "—"), tpg.get("n_gaveback", "—"),
        tpg.get("n_ranfurther", "—"), tpg.get("n", 0), _tpg_tag))
    # [MW0602 432차] 클램프 발동 건수를 요약행에 노출한다. 요약표만 보고 회의에
    # 올리는 경로가 실제로 있어서, "그 변형은 체결 불가능한 가격을 요구했다"는
    # 사실이 상세 섹션에만 있으면 놓친다.
    _cl25 = _g25.get("n_clamped") or {}
    _cl25_hot = sorted(((v, k) for k, v in _cl25.items() if v), reverse=True)
    _cl25_tag = (" ⚠클램프 " + ", ".join("%s %d건" % (k, v) for v, k in _cl25_hot)
                 if _cl25_hot else "")
    L.append("| [25] TP1 보호전환 offset A/B | %s | %s (전환 %s건/%s일)%s%s |" % (
        _fmt_verdict(_g25.get("verdict", "")), _g25.get("reason", _g25.get("error", "—")),
        _g25.get("n_hooks", "—"), _g25.get("n_days", "—"), _cl25_tag,
        _dm("tp1_protect_offset_shadow")))
    # [MW0601 432차] [25-B] TP2 거리 축 — [25]와 같은 훅 모집단·같은 시뮬을 쓰지만
    # **판정은 완전히 독립**이다(본채널 합격선 무변경, §9-4). 요약표에서도 별 행으로 낸다.
    _g25b = _g25.get("tp2") or {}
    if _g25b:
        # [2026-08-08 주간회의] [25-B]는 판정이 [25]와 완전히 분리돼 있어(§9-4) 결정도
        # 별도 키(`..._tp2`)로 기록한다 — 그 키를 여기 배선하지 않으면 확정 결정이 요약표에
        # 안 뜬다(실제로 D4 등록 직후 이 행만 마커가 비어 있었다).
        L.append("| [25-B] TP2 거리 A/B | %s | %s (전환 %s건/%s일)%s |" % (
            _fmt_verdict(_g25b.get("verdict", "")), _g25b.get("reason", "—"),
            _g25b.get("n_hooks", "—"), _g25b.get("n_days", "—"),
            _dm("tp1_protect_offset_shadow_tp2")))
    L.append("| [26] 거래불능(가격상한 고착) 구간 | %s | %s |" % (
        _fmt_verdict(lpw.get("verdict", "OBSERVE")),
        (lpw.get("reason") or "고착 %s분봉 / %s일  · MFE오염 %s"
         % (lpw.get("n_pinned_bars", 0), lpw.get("n_days", 0),
            "있음 ⚠" if lpw.get("mfe_contamination") else "없음"))))
    L.append("| [27] counterfactual 도달불가 목표가 | %s | %s |" % (
        _fmt_verdict(ucw.get("verdict", "OBSERVE")),
        (ucw.get("reason") or "해당 %s건 (%s) · hyp합 %s pt — 판정 미반영, 민감도만"
         % (ucw.get("n_unreachable", 0),
            ", ".join("%s=%d" % kv for kv in (ucw.get("by_table") or {}).items()) or "—",
            ucw.get("excluded_hyp_pnl_pts", "—")))))
    _sb = siw.get("by_bucket") or {}
    L.append("| [28] 사이징 역예측 감시%s | %s | %s |" % (
        " ⚠구조적판정불가" if siw.get("structural_block") else "",
        _fmt_verdict(siw["verdict"]),
        siw.get("reason") or (" / ".join(
            "%s: n=%d 승률=%.1f%% 평균=%s원" % (
                k, v["n"], v["win_rate"] * 100, format(v["avg_pnl_krw"], ",.0f"))
            for k, v in sorted(_sb.items())) or "표본 없음")))
    _mb = mrs.get("by_bucket") or {}
    L.append("| [29] mean-revert 레짐 사이즈 | %s | %s |" % (
        _fmt_verdict(mrs["verdict"]),
        mrs.get("reason") or (" / ".join(
            "%s: n=%d 승률=%.1f%% 평균=%s원" % (
                k, v["n"], v["win_rate"] * 100, format(v["avg_pnl_krw"], ",.0f"))
            for k, v in sorted(_mb.items())) or "표본 없음")))
    L.append("| [30] toxicity 재보정 밴드분포 | %s | %s |" % (
        _fmt_channel_verdict(trw),
        trw.get("reason") or (
            "pass=%.1f%% reduce=%.1f%% block=%.1f%% · cancel포화=%.1f%% (n=%s분봉)" % (
                trw.get("pass_share", 0) * 100, trw.get("reduce_share", 0) * 100,
                trw.get("block_share", 0) * 100, trw.get("cancel_sat_share", 0) * 100,
                trw.get("n_bars", "—")))))
    L.append("| [31] tox reduce 연속배수 섀도 | %s | %s |" % (
        _fmt_channel_verdict(trm),
        trm.get("reason") or (
            "수량상이 %s/%s (%.1f%%) · 섀도배수 %s~%s (평균 %s vs 실적용 0.70)" % (
                trm.get("divergent_qty_n", "—"), trm.get("n_samples", "—"),
                trm.get("divergent_qty_share", 0) * 100,
                trm.get("shadow_mult_min", "—"), trm.get("shadow_mult_max", "—"),
                trm.get("shadow_mult_mean", "—")))))
    _mz = msz.get("bands") or {}
    _mzt = _mz.get("_합계") or {}
    L.append("| [34] meta size0 무시 | %s | %s |" % (
        _fmt_channel_verdict(msz),
        msz.get("reason") or (
            "raw0 진입 %s건(매칭 %s) · 누적 %s원 승률 %.1f%% · %s"
            % (msz.get("n", "—"), _mzt.get("matched", "—"),
               format(int(_mzt.get("total_pnl_krw", 0) or 0), ","),
               float(_mzt.get("win_rate", 0) or 0) * 100,
               " / ".join(
                   "%s n=%s" % (b, (_mz.get(b) or {}).get("matched", 0))
                   for b in ("reduce", "take"))))))
    # [MW0602 424차 후속] [35]~[37] — 셋 다 등록 시점에 표본·유의성 미달이다.
    L.append("| [35] 유령 하드스톱 결함/알파%s | %s | %s |" % (
        " ⚠구조적판정불가" if pse.get("structural_block") else "",
        _fmt_channel_verdict(pse),
        pse.get("reason") or (
            "유령 %s건 / %s거래일 · 실현 %+.2fpt vs 반사실 %+.2fpt · "
            "delta %+.2fpt (유리 %s건) · 일자 부호검정 p=%s" % (
                pse.get("n", "—"), pse.get("n_days", "—"),
                pse.get("realized_pt_sum", 0.0), pse.get("cf_pt_sum", 0.0),
                pse.get("delta_pt_sum", 0.0), pse.get("favorable_n", "—"),
                pse.get("sign_p", "—")))))
    _gx = gxp.get("by_path") or {}
    L.append("| [36] 체크리스트 승격 경로 | %s | %s |" % (
        _fmt_channel_verdict(gxp),
        gxp.get("reason") or (" / ".join(
            "%s: n=%d(%d일) 승률=%.1f%% 평균=%s원" % (
                k, v["n"], v.get("days", 0), v["win_rate"] * 100,
                format(v["avg_pnl_krw"], ",.0f"))
            for k, v in sorted(_gx.items())) or "표본 없음")))
    L.append("| [37] mean-revert 일자단위 재검정 | %s | %s |" % (
        _fmt_channel_verdict(hmd),
        hmd.get("reason") or (
            "MR %s건 누적 %s원 · 짝지은 %s일 평균차 %+.2fpt · p=%s "
            "(⚠ [29]와 모집단 동일 — 판독규칙 상세 참조)" % (
                hmd.get("n_mean_revert", "—"),
                format(int((hmd.get("cum_krw") or {}).get("mean_revert", 0) or 0), ","),
                hmd.get("paired_days", "—"), hmd.get("mean_diff", 0.0),
                hmd.get("sign_p", "—")))))
    _pgc = pgl.get("live_config") or {}
    L.append("| [38] ProfitGuard-L1 피크 트레일링 | %s | %s |" % (
        _fmt_channel_verdict(pgl),
        pgl.get("reason") or (
            "구속발동 %s건/%s일 · 차단신호 %s건 반사실 %+.2fpt · 운영 %s원/%.0f%%%s" % (
                pgl.get("n_binding", "—"), pgl.get("n_binding_days", "—"),
                pgl.get("n_blocked_signals", 0), pgl.get("cf_total_pt", 0.0),
                format(int(_pgc.get("activation_krw", 0) or 0), ","),
                float(_pgc.get("ratio", 0) or 0) * 100,
                " ⚠설정출처=prefs" if _pgc.get("diverged") else ""))))
    _cdm = (cdw.get("axes") or {}).get("model") or {}
    _cde = (cdw.get("axes") or {}).get("ensemble") or {}
    L.append("| [39] confidence 판별력 | %s | %s |" % (
        _fmt_channel_verdict(cdw),
        cdw.get("reason") or (
            "모델축 %+.2f%%p(n=%s, 일자 p=%s) · 앙상블축 %+.4f(d=%s, 승%s/패%s) "
            "· 매칭 %s/%s" % (
                _cdm.get("gap_pp", 0.0), _cdm.get("n", "—"),
                (_cdm.get("stratified") or {}).get("sign_p", "—"),
                _cde.get("gap", 0.0), _cde.get("cohen_d", "—"),
                _cde.get("n_win", "—"), _cde.get("n_loss", "—"),
                cdw.get("n_matched", "—"), cdw.get("n_positions_total", "—")))))
    L.append("| [40] 방향 선택의 가치 | %s | %s |" % (
        _fmt_channel_verdict(dvw),
        dvw.get("reason") or (
            "실제 %+.2fpt vs 무작위중앙 %+.2fpt (n=%s/%s일) · 단측 p=%s · 일자 %s/%s일" % (
                dvw.get("actual_pt", 0.0), dvw.get("random_median_pt", 0.0),
                dvw.get("n_usable", "—"), dvw.get("n_days", "—"),
                dvw.get("p_one_sided", "—"),
                dvw.get("days_beating_random", "—"), dvw.get("days_evaluated", "—")))))
    _emr = emw.get("readiness") or {}
    L.append("| [41] 청산 측 학습기 게이지 | %s | %s |" % (
        _fmt_channel_verdict(emw),
        emw.get("reason") or (
            "OOF AUC=%s (기준선 %s) · 포지션 %s / EPV %s" % (
                emw.get("oof_auc", "—"), emw.get("baseline_acc", "—"),
                _emr.get("n_positions", "—"), _emr.get("epv", "—")))))
    L.append("| [42] 타점의 가치 | %s | %s%s |" % (
        _fmt_channel_verdict(etv),
        etv.get("reason") or (
            "타점 기여(B-C) %+.2fpt · B>C %.1f%% · 짝지은 p=%s "
            "(A %+.2f / B %+.2f / C %+.2f)" % (
                etv.get("timing_gain_pt", 0.0),
                float(etv.get("b_over_c_share", 0)) * 100, etv.get("sign_p", "—"),
                etv.get("arm_a_pt", 0.0), etv.get("arm_b_median_pt", 0.0),
                etv.get("arm_c_median_pt", 0.0))),
        _dm("entry_timing_value_watch")))
    L.append("| [43] 변동성 추정량 교체 | %s | %s |" % (
        _fmt_channel_verdict(vew),
        vew.get("reason") or (
            "ATR 통제 후 부분상관 %+.4f (t=%s) · 공선성 %.3f · "
            "실현레인지 상관 ATR %+.3f / q90-q10 %+.3f · qty경계통과 %s건" % (
                vew.get("partial_corr", 0.0), vew.get("partial_t", "—"),
                vew.get("collinearity", 0.0), vew.get("corr_atr_realized", 0.0),
                vew.get("corr_qunc_realized", 0.0),
                vew.get("qty_boundary_cross", "—")))))
    # [MW0602 489차 / D5] 결정 마커 필수 — 이 채널은 **보류 사유가 교체**된 이력이 있다
    # (0816 "MW0601 판정 대기" → 487차 정책 폐기로 소멸 → 0823 "손익 축 근거 없음").
    # 마커가 없으면 다음 세션이 SUPPORTS_HYP만 보고 "미조치"로 오독한다.
    L.append("| [44] DynMC 붕괴행 잠식 | %s | %s%s |" % (
        _fmt_channel_verdict(dcf),
        dcf.get("reason") or (
            "설계 %.1f%% vs 현행 %.1f%% (이탈 %.2f%%p) · base_mc %.4f→%.4f · "
            "붕괴 %.1f%%" % (
                float(dcf.get("pass_rate_design", 0)) * 100,
                float(dcf.get("pass_rate_current", 0)) * 100,
                dcf.get("gap_pp", 0.0),
                dcf.get("base_mc_excl_collapsed", 0.0),
                dcf.get("base_mc_current", 0.0),
                float(dcf.get("collapsed_share", 0)) * 100)),
        _dm("dynmc_collapse_feed_watch")))
    L.append("| [45] 축퇴 가드 플래핑 (게이지) | %s | %s%s |" % (
        _fmt_verdict("OBSERVE"), cgf.get("reason", "—"),
        _dm("cal_guard_flap_watch")))
    # [MW0601 434차] [46] HurstGate 임계 위치 A/B — OOS 기준 판정(전체표본은 in-sample).
    _g46 = off.get("hurst_threshold_shadow") or {}
    if _g46:
        # [MW0602 489차 / D3] 결정 마커 필수 — 0823 주간회의가 "미적용 · 감시 승격"으로
        # 닫았다. 마커가 없으면 매주 재출력되는 FAIL을 다음 세션이 신규 승격 안건으로
        # 오독한다([6] Hurst 완화가 3주째 같은 권고를 찍어 0801 초안이 잘못 올렸던 것과
        # 같은 사고 — 이 레지스트리가 존재하는 이유다).
        L.append("| [46] Hurst 임계 위치 A/B | %s | %s (OOS %s건/%s일, 전체 %s건/%s일)%s |" % (
            _fmt_verdict(_g46.get("verdict", "")),
            _g46.get("reason", _g46.get("error", "—")),
            _g46.get("n_oos", "—"), _g46.get("n_days_oos", "—"),
            _g46.get("n_matched", "—"), _g46.get("n_days", "—"),
            _dm("hurst_threshold_shadow")))

    # [MW0602 462차] [51]~[53] — 0811 점검 P4 신설. 전부 사전등록·표본 미달 상태.
    def _row_462(num, title, d, key):
        _why = d.get("reason") or d.get("recommendation") or d.get("error") or "—"
        L.append("| [%d] %s | %s | %s%s |" % (
            num, title, _fmt_verdict(d.get("verdict", "")), _why, _dm(key)))
    _row_462(51, "저변동성 이익기하 붕괴", pgv, "profit_geometry_lowvol_watch")
    _row_462(52, "준붕괴(유효가중합 저) 진입", efw, "effective_weight_watch")
    _row_462(53, "진입금지 존 위반 코호트%s" % (
        " **[집행 ON]**" if zbb.get("enforce_flag") else ""),
        zbb, "zone_ban_breach_watch")

    # [MW0601 405차 / P0-3] pt 채널 단위 배지 — 요약표에 단위가 다른 두 계열이 섞여 있다.
    # 실현손익 채널([13]·[21]·[5]·[8])은 trades.net_pnl_krw라 계약수가 반영된 "원"이고,
    # counterfactual 채널은 hyp_pnl_pts — **1계약 기준·TP1 상한·미실현 시뮬레이션**이다.
    # 이 사실이 어디에도 표기돼 있지 않아 `+32.78pt`가 실현손익과 같은 단위로 읽혔다.
    #
    # 계측은 결함이 아니다 — "차단 안 했으면 얼마였나"는 1계약 기준으로 재는 것이 맞고,
    # 사이저 출력을 섞으면 게이트 성능과 사이징 성능이 뒤엉킨다. 문제는 라벨이었다.
    # 실측 근거(MW0601): [6] Hurst는 1계약 기준 +37.72pt인데 진입시점 entry_qty로
    # 가중하면 +26.27pt(0.70배)다 — 고계약수 신호를 차단한 공로가 1계약 표기에서
    # 30% 희석된다. [7] JointGate는 entry_qty가 전부 1이라 차이가 없다(채널마다 다르다).
    # TP1 상한도 같은 방향의 계통 편향이다 — 하방은 stop까지 온전히 세면서 상방은
    # TP1에서 자른다(실거래 TP2 평균 +5.85pt / TP3 +8.00pt). 404차 후속9가 [7]에
    # MFE/MAE를 병기해 이 편향이 결론을 뒤집지는 않음을 확인했으나 [7]에서만 확인됐다.
    #
    # **표시만 바꾼다 — 판정식·합격선·verdict에 일절 관여하지 않는다.**
    _PT_BADGE = " `[1계약·TP1상한·미실현 시뮬]`"
    for _i in range(len(L) - 1, -1, -1):
        _row = L[_i]
        if not _row.startswith("| ["):
            if _row.startswith("| 채널 |"):
                break
            continue
        if "hyp=" in _row and _PT_BADGE not in _row:
            L[_i] = _row.rstrip()[:-1].rstrip() + _PT_BADGE + " |"
    L.append("")
    L.append("> `[1계약·TP1상한·미실현 시뮬]` 배지가 붙은 채널의 `hyp=…pt`는 **실현손익이 아니다** — "
             "계약수를 곱하지 않은 1계약 기준이고, TP1에서 끊는 가상 청산이며, 실제로는 "
             "일어나지 않은 거래다. 배지 없는 원(₩) 단위 채널([13]·[21]·[5]·[8])과 "
             "직접 더하거나 비교하지 말 것. 채널별 진입시점 계약수 분포는 각 채널 상세 절 참조.")

    # [0] 표본 기아 경보 상세
    L.append("## [0] 캠페인 표본 기아 경보 + 완화 사다리 (§3-8)")
    L.append("")
    if ss.get("error"):
        L.append("> ⚠ %s" % ss["error"])
    else:
        L.append("- 주간(7일) 진입 체결: **%d건** (하한 %d건) → 4주 투영 %d건" % (
            ss["n_weekly_entries"], ss["floor"], ss["projected_28d_entries"]))
        if ss.get("kpis_at_risk"):
            L.append("- **표본 미달 위험 KPI**: " + " / ".join(ss["kpis_at_risk"]))
        L.append("- **완화 사다리 상태**: %s" % ss.get("ladder_status", "—"))
        L.append("")
        L.append("| 단계 | 조치 | 상태 |")
        L.append("|---|---|---|")
        for s in ENTRY_STARVATION_MITIGATION_LADDER:
            _mark = "**← 현재**" if s["step"] == ss.get("current_step") else ""
            L.append("| %d | %s | %s |" % (s["step"], s["action"], _mark))
        L.append("")
        L.append("> 사다리 적용은 항상 사용자 수동 결정 — 자동 변경 없음. 적용 시"
                  " `dev_memory/DECISION_LOG.md`에 기록할 것.")
    L.append("")

    # [1] TB 상세
    L.append("## [1] Triple-Barrier — OOS replay IC vs 3클래스 IC")
    L.append("")
    L.append("| 호라이즌 | 판정 | IC_TB | IC_3class | OOS n | 비고 |")
    L.append("|---|---|---|---|---|---|")
    for hz in HORIZONS:
        r = tb["horizons"].get(hz, {})
        _status = r.get("status", "—")
        if r.get("carried"):
            _status = "%s (유지, %s 판정)" % (_status, str(r.get("judged_at", ""))[:10])
        L.append("| %s | %s | %s | %s | %s | %s |" % (
            hz, _status, r.get("ic_tb", "—"), r.get("ic_3class", "—"),
            r.get("n_samples", "—"), r.get("reason", "")))
    if tb.get("error"):
        L.append("")
        L.append("> ⚠ %s" % tb["error"])
    L.append("")
    L.append("> [357차 해석 확정] 1m은 앙상블 가중치 영구 0 퇴역(331차 후속2) 상태 —")
    L.append("> 1m이 IC 기준을 합격해도 \"1m 앙상블 복귀\"가 아니라 1m 활용방안 A·C")
    L.append("> (331차 후속3, 섀도우 경로)의 근거로만 사용한다. **실질 승격 검토 대상은")
    L.append("> 3m/5m로 한정** (30m은 296차 퇴역). 합격선 자체는 불변 — 해석만 확정")
    L.append("> (시계 리셋 불요).")
    L.append("> [384차] 383차가 규명한 구조결함(평가창이 매주 재학습으로 리셋돼 5m~30m이")
    L.append("> min_samples_hz 영구 미달) 해법 적용 — 이제 호라이즌별 실제 OOS n이")
    L.append("> min_samples_hz에 도달한 주에만 신선하게 판정하고, 그 아래 주는 `tb_verdict_log`의")
    L.append("> 최근 판정을 그대로 유지(위 표의 \"(유지, YYYY-MM-DD 판정)\")한다. 10m/15m/30m은")
    L.append("> 판정 주기 자체가 몇 주~십수 주 단위로 길 뿐 표본은 끊기지 않고 계속 누적된다.")
    L.append("")

    # [2] Meta-Gate 상세
    L.append("## [2] Meta-Gate — entry_quality_prob 3분위 순EV (왕복비용 %s pt 차감)" %
             mg.get("cost_pt", "—"))
    L.append("")
    if "top_ev_pt" in mg:
        L.append("| 분위 | 순EV(pt) | n |")
        L.append("|---|---|---|")
        L.append("| 상위 33%% | %s | %s |" % (mg["top_ev_pt"], mg.get("tercile_n")))
        L.append("| 중위 33%% | %s | — |" % mg.get("mid_ev_pt"))
        L.append("| 하위 33%% | %s | %s |" % (mg["bottom_ev_pt"], mg.get("tercile_n")))
    else:
        L.append("- %s" % mg.get("reason", mg.get("error", "데이터 없음")))
    L.append("")

    # ── [MW0602 490차 / P0-①·P1] 스코어러 학습 지표 + 재개 게이트 ───────────────
    # 종전에는 AUC가 EOD 로그에만 찍혀 **아무도 읽지 않았다**(292·303·371·468차 계열).
    try:
        from learning.meta_label_classifier import load_training_metrics as _ltm
        _tm = _ltm()
    except Exception:
        _tm = {}
    _tm_latest = (_tm.get("latest") or {}).get("horizons") or {}
    if _tm_latest:
        L.append("### [2-A] 스코어러 학습 지표 (490차 P0 — 관찰 전용, 판정 미반영)")
        L.append("")
        L.append("| 호라이즌 | 혼합 AUC | **방향성 AUC** | **순이익 AUC** | 강한추종 AUC | 방향성 n | 피처 |")
        L.append("|---|---|---|---|---|---|---|")
        for _hz in ("1m", "3m", "5m", "10m", "15m", "30m"):
            _r = _tm_latest.get(_hz)
            if not _r:
                continue

            def _f(key, row=_r):
                v = row.get(key)
                return ("%.4f" % v) if isinstance(v, (int, float)) else "—"

            L.append("| %s | %s | **%s** | **%s** | %s | %s | %s |" % (
                _hz, _f("auc_mixed"), _f("auc_directional"), _f("auc_net_directional"),
                _f("auc_strong_directional"), _r.get("n_oof_directional", "—"),
                _r.get("n_features", "—")))
        L.append("")
        L.append("- 학습 시각: %s · 스키마 기준일: %s" % (
            (_tm.get("latest") or {}).get("trained_at", "—"),
            (_tm_latest.get("1m") or {}).get("schema_day", "—")))
        L.append("")
        L.append("> 🔴 **`혼합 AUC`를 개선 근거로 쓰지 말 것** — FLAT 예측 행(22.7~46.2%)은")
        L.append("> 피처와 무관하게 라벨이 무조건 `skip`이라, 분류기가 \"조용한 장 = skip\"만")
        L.append("> 배워도 값이 올라간다. **[2]가 평가하는 모집단은 방향성 행뿐**이므로")
        L.append("> `방향성 AUC`가 이 채널과 정합하는 값이다(490차 실험 발견 ①).")
        L.append("> ")
        L.append("> **`순이익 AUC`** = 배포 모델 점수 vs `realized_move ≥ 왕복비용`(방향성 행).")
        L.append("> **[2]의 질문을 AUC 한 값으로 옮긴 것**이며 아래 재개 게이트의 판정 지표다.")
        L.append("> ")
        L.append("> **`강한추종 AUC`**(P2 섀도 게이지) = 점수 vs `realized_move ≥ max(2×임계, 0.05)`.")
        L.append("> **판정에 관여하지 않는다** — \"이 피처셋이 방향·수익이 아니라 **크기**를")
        L.append("> 잡는가\"를 묻는 관찰값이고, 청산 축 재활용 가능성의 입력이다.")
        L.append("> ⚠ 재활용하려면 **새 채널 사전등록이 필요**하다(주간회의 소관).")
    _gate = _meta_reopen_gate()
    if _gate.get("enabled"):
        _icon = {"OPEN": "🟢 OPEN", "CLOSED": "🔒 CLOSED",
                 "INSUFFICIENT": "⏳ INSUFFICIENT", "UNKNOWN": "⚠ UNKNOWN"}.get(
                     _gate.get("state"), _gate.get("state", "—"))
        L.append("")
        L.append("### [2-B] 재개 게이트 (490차 P1 — 사전등록)")
        L.append("")
        L.append("- 상태: **%s** — %s" % (_icon, _gate.get("reason", "—")))
        L.append("- 지표 `%s` · 문턱 **%s**(앵커 `PredictionCalibrator.DEGENERATE_AUC_MIN`) "
                 "· 필요 연속 %s회 · 판정창 %s~" % (
                     _gate.get("metric"),
                     ("%.2f" % _gate["threshold"]) if _gate.get("threshold") else "—",
                     _gate.get("need_weeks"), _gate.get("start_date")))
        if _gate.get("latest_min") is not None:
            L.append("- 최근 학습(%s): 호라이즌 최솟값 **%.4f** / 최댓값 %.4f · 연속 %s회" % (
                _gate.get("latest_trained_at", "—"), _gate["latest_min"],
                _gate.get("latest_max") or float("nan"), _gate.get("streak_weeks", 0)))
        L.append("")
        L.append("> **왜 이 게이트가 있나.** 489차 D1이 [2]를 최종 탈락시키며 재개 조건을")
        L.append("> **소진**시켰다. \"소진\"은 영원한 금지가 아니라 **\"새 사전등록 없이는")
        L.append("> 재개 불가\"**이고, 이 블록이 그 새 사전등록이다. 닫혀 있는 동안은")
        L.append("> **아무것도 안 하는 것이 결정**이며, 매주 자동 재계산되므로 사람이")
        L.append("> 기억할 필요가 없다(489차 D2가 CB②에 적용한 규율과 같다).")
        L.append("> ")
        L.append("> ⚠ **통과가 \"[2] 합격\"을 뜻하지 않는다.** AUC는 라벨 순위, [2]는 손익")
        L.append("> 분리다. 성립하는 함의는 한 방향뿐 — **AUC≈0.5면 [2]가 통과할 리 없다.**")
        L.append("> ⚠ 호라이즌 **최솟값**으로 본다 — 하나라도 무정보면 통과로 치지 않는다.")
        L.append("> ⚠ 403차의 *\"0.53은 변별력이 없다\"* 를 여기 옮기지 말 것 — 그것은")
        L.append("> **n=200**(보정기 버퍼, SE≈0.047) 기준이다. 이 채널은 방향성 n≈4천~1.4만이라")
        L.append("> 명목 SE≈0.005 수준이다. **같은 숫자라도 표본이 다르면 의미가 다르다.**")
    L.append("")

    # [3] 분위 회귀 상세
    L.append("## [3] 분위 회귀 — 캘리브레이션")
    L.append("")
    L.append("- 표본: %s건 / 커버리지 %s (합격 밴드 %s~%s) / 불확실성-실현폭 상관 %s (하한 %s)" % (
        qt.get("n_samples", 0), qt.get("coverage", "—"),
        VALIDATION_CAMPAIGN["quantile"]["coverage_lo"],
        VALIDATION_CAMPAIGN["quantile"]["coverage_hi"],
        qt.get("unc_corr", "—"), VALIDATION_CAMPAIGN["quantile"]["unc_corr_min"]))
    if qt.get("reason"):
        L.append("- %s" % qt["reason"])
    L.append("")

    # [3-A] q50 방향 적중률 (404차 후속10) — 관찰 전용, [3] 판정 미반영
    L.append("### [3-A] q50 방향 적중률 (404차 후속10, 관찰 전용 — 판정 없음)")
    L.append("")
    if not _qd or not _qd.get("n"):
        L.append("- 표본 없음 (q50 또는 실현 레이블 결측)")
    else:
        L.append("| 구분 | n | 방향 적중률 |")
        L.append("|---|---|---|")
        L.append("| 전체 | %d | %.1f%% |" % (_qd["n"], _qd["hit_rate"] * 100))
        L.append("| \\|q50\\| 상위 30%% | %d | %.1f%% |" % (
            _qd.get("conf_top30_n", 0), (_qd.get("conf_top30_hit") or 0) * 100))
        L.append("")
        L.append("- q50 > 0 비율: **%.1f%%** (50%%에서 크게 벗어나면 방향 편향)"
                 % (_qd["q50_pos_share"] * 100))
    L.append("")
    L.append("> **판정하지 않는다**(§3 합격선 무변경). 감사 §3-3은 분위회귀 KPI를 **3종**으로")
    L.append("> 정의했으나(① q50 방향 적중률 ② 폭-실현 상관 ③ 커버리지) 합격선은 ②③만")
    L.append("> 채택했다 — ①은 **사전등록돼 있었는데 한 번도 렌더링되지 않았다**. 그 탓에")
    L.append("> [3] PASS가 \"방향을 맞춘다\"로 오독될 여지가 있었다. 실제 의미는")
    L.append("> \"**불확실성 폭**을 잘 맞춘다\"뿐이다.")
    L.append("> 이 표의 목적은 승격 근거가 아니라 그 오독을 차단하는 것이다 — 적중률이")
    L.append("> 50% 근처면 **q50을 방향·사이징에 쓰지 말라**는 뜻이고, [2] Meta-Gate가")
    L.append("> 확신도-성과 역상관으로 탈락한 것과 같은 실패를 예방한다.")
    L.append("> `|q50| 상위 30%` 적중률이 전체와 비슷하면 q50의 **크기**에도 정보가 없다는 뜻.")
    L.append("")

    # [3-B] 분위회귀 기반 TP1 거리 A/B (404차 후속10)
    L.append("## [3-B] 분위회귀 기반 TP1 거리 A/B (404차 후속10 신설)")
    L.append("")
    if _g3b.get("error"):
        L.append("> ⚠ 스크립트 실행 실패: %s" % _g3b["error"])
    else:
        _sk = _g3b.get("skip") or {}
        L.append("- 진입 후보 %s건 → 시뮬 %s건 / 거래일 %s일"
                 % (_g3b.get("n_candidates", "—"), _g3b.get("n_trades", "—"),
                    _g3b.get("n_days", "—")))
        L.append("- 제외: 분위결측 %s건(2026-07-20 이전 미적재) / ATR결측 %s / 이익방향분위 부호반대 %s / TP과협 %s / 기하역전(TP1≥TP2) %s / 시뮬불가 %s"
                 % (_sk.get("quantile", 0), _sk.get("atr", 0), _sk.get("unfavorable", 0),
                    _sk.get("tp_too_tight", 0), _sk.get("tp_inverted", 0), _sk.get("sim", 0)))
        if _g3b.get("engine"):
            L.append("- 재생기 엔진: **%s** (442차 이관 — `sim_fidelity_gate[\"engine\"]` 공유)"
                     % _g3b["engine"])
        pv = _g3b.get("per_variant") or {}
        if pv:
            L.append("")
            L.append("| 변형 | n | 승률 | 누적pt | 현행 대비 | drop-max | 건별 우세 | 결말 분포 |")
            L.append("|---|---|---|---|---|---|---|---|")
            for k, v in pv.items():
                _oc = v.get("outcomes") or {}
                _oc_txt = (" · ".join("%s %d" % (o, c) for o, c in _oc.items())
                           if _oc else "TP1 %d / STOP %d" % (v["n_tp1"], v["n_stop"]))
                L.append("| %s | %d | %.1f%% | %+.2f | %s | %s | %s | %s |" % (
                    k, v["n"], v["win_rate"] * 100, v["total_pt"],
                    ("%+.2f" % v["delta_vs_current"]) if v.get("delta_vs_current") is not None else "—",
                    ("%+.2f" % v["delta_drop_max"]) if v.get("delta_drop_max") is not None else "—",
                    ("%s/%d" % (v["beats_current_n"], v["n"])) if v.get("beats_current_n") is not None else "—",
                    _oc_txt))
        L.append("")
        L.append("- **판정: %s** — %s" % (_g3b.get("verdict"), _g3b.get("reason")))
    L.append("")
    L.append("> **이 채널의 판정은 [3] 본채널 verdict에 반영하지 않는다**(§9-4 판정기준 사후")
    L.append("> 변경 금지). [3]의 합격선은 커버리지·불확실성상관 두 개 그대로다.")
    L.append("> 묻는 것: 현행 TP1은 `ATR × 배수`로 **신호 내용과 무관**한데, 분위회귀가 매 분봉")
    L.append("> 계산해 두고도 쓰지 않는 \"이익 방향 꼬리까지의 거리\"를 쓰면 나은가.")
    L.append("> LONG은 q90, SHORT는 |q10| — 방향별 favorable quantile을 쓴다(SHORT에 q90을")
    L.append("> 쓰면 손실 방향 꼬리를 TP로 삼는 꼴).")
    L.append("> **스톱은 전 변형 고정**(현행 ATR×1.5×hurst) — [23-B] `sym_1.0_1.0`이 TP·스톱을")
    L.append("> 동시에 바꿔 기여 분해가 불가능했던 교란을 제거했다. TP2/TP3도 현행 고정이다")
    L.append("> (**TP1 축만** 바꾼다는 사전등록 취지 — 442차 실측 110건에서 기하역전 0건).")
    L.append("> ")
    L.append("> ### 🔴 442차 정본 재생기 이관 — **이관 전 수치는 인공물이었다**")
    L.append("> ")
    L.append("> 441차까지 이 채널은 자체 시뮬을 썼고 규칙이 하나였다 — **\"TP1선에 닿으면")
    L.append("> 그 거리만큼 전부 벌고 즉시 종료\"**. 실제로는 TP1 도달이 청산이 아니다")
    L.append("> (1계약이면 **보호스톱 전환**이고 포지션은 살아 있다; 2계약 이상이면 33%만")
    L.append("> 나간다). 즉 구 시뮬은 \"TP1 찍고 반납한 거래\"와 \"TP2까지 완주한 거래\"를")
    L.append("> **둘 다 만점 처리**했고, 그 오차는 **TP1 거리에 정비례**한다 —")
    L.append("> **TP1을 넓히는 변형일수록 공짜로 점수가 오르는** 구조였다.")
    L.append("> ")
    L.append("> 442차 실측(110건)에서 그 지문이 완벽하게 단조로 드러났다:")
    L.append("> ")
    L.append("> | 변형 | TP1 폭(현행 대비) | 구 시뮬 개선폭 | **정본 이관 후** |")
    L.append("> |---|---|---|---|")
    L.append("> | q_x0.7 | +11.8% | +0.56pt | **−14.73pt** |")
    L.append("> | q_blend | +29.8% | +6.42pt | **−10.99pt** |")
    L.append("> | q_raw | +59.7% | **+20.22pt** | **−9.59pt** |")
    L.append("> ")
    L.append("> 순위가 \"분위회귀가 맞았는가\"가 아니라 **\"얼마나 넓혔는가\"** 로 전부")
    L.append("> 설명됐다. 이관 후 **판정이 FAIL → PASS로 뒤집혔다**(모든 대안이 현행 이하).")
    L.append("> 440차가 [23-B]에서 실증한 것과 같은 인공물이다(`tp1_x2` v1 최고 +37.96 →")
    L.append("> v2 최악 −30.68).")
    L.append("> ")
    L.append("> ⚠ **이관 전 수치(특히 `q_raw` +20.22pt)를 인용하지 말 것.** 0801 결산이")
    L.append("> \"감사 §5 승격 후보 4개 중 유일한 생존자\"로 올린 근거가 그 숫자였다.")
    L.append("> ⚠ v1 롤백 회귀는 4/4 비트 단위 재현됨(`engine=\"v1\"`).")
    L.append("> ")
    L.append("> ⚠ 결말 분포에 `TP1`이 안 보이는 것은 정상이다 — v2에서 TP1은 **청산이 아니라**")
    L.append("> **보호전환**이라 결말이 될 수 없다(`TP1_ARM_STOP`이 \"보호전환 후 되돌림\"이다).")
    L.append("> ⚠ 절대값은 실현손익이 아니다(1계약 기준·왕복비용 가정). **변형 간 상대비교 전용.**")
    L.append("> ⚠ FAIL이 떠도 즉시 적용 금지 — `drop-max`(최대기여 1건 제거 후 델타)와")
    L.append("> `건별 우세`를 함께 볼 것. [25]는 drop-max에서 부호가 역전돼 무너졌다(372차).")
    L.append("> ⚠ **MW0601 교차확인 필수** — [23-B]가 같은 코드·같은 기간에도 PC간 부호")
    L.append("> 역전을 냈다(tp1_x2: +32.78 vs −19.04). n≈40으로는 기하를 확정할 수 없다(313차).")
    L.append("")

    # [4] 신호소멸청산 상세
    L.append("## [4] 신호소멸청산 counterfactual (§3-5 롤백 기준 ①)")
    L.append("")
    L.append("- 이번 실행 resolve: %d건 / 누적 판정 %s건 (미판정 %s건)" % (
        sd.get("resolved_now", 0), sd.get("n_resolved", 0), sd.get("n_pending", 0)))
    L.append("- counterfactual 분포: STOP %s / TP1 %s / NEITHER %s" % (
        sd.get("cf_stop", 0), sd.get("cf_tp1", 0), sd.get("cf_neither", 0)))
    L.append("- 누적 saved_pts(아낀 pt − 놓친 pt): **%s pt**" % sd.get("total_saved_pts", "—"))
    if sd.get("recommendation"):
        L.append("- **권고**: %s" % sd["recommendation"])
    if sd.get("reason"):
        L.append("- %s" % sd["reason"])
    L.append("")

    # [5] 레짐 배수 상세
    L.append("## [5] 레짐 조건부 ATR 배수 (§3-5 롤백 기준 ②)")
    L.append("")
    if hr.get("buckets"):
        L.append("| 버킷 | n | 평균 순EV(원) | 누적(원) | 승률 |")
        L.append("|---|---|---|---|---|")
        for b, v in sorted(hr["buckets"].items()):
            L.append("| %s | %d | %s | %s | %.1f%% |" % (
                b, v["n"], format(v["avg_ev_krw"], ",.0f"),
                format(v["total_ev_krw"], ",.0f"), v["win_rate"] * 100))
    if hr.get("recommendation"):
        L.append("")
        L.append("- **권고**: %s" % hr["recommendation"])
    if hr.get("reason"):
        L.append("")
        L.append("- %s" % hr["reason"])
    L.append("")

    # [6] Hurst 게이트 counterfactual 상세
    L.append("## [6] Hurst 게이트 counterfactual (§3-6, P1-4)")
    L.append("")
    L.append("- 이번 실행 resolve: %d건 / 누적 판정 %s건 (미판정 %s건)" % (
        hg.get("resolved_now", 0), hg.get("n_resolved", 0), hg.get("n_pending", 0)))
    L.append("- counterfactual 분포: STOP %s / TP1 %s / NEITHER %s" % (
        hg.get("cf_stop", 0), hg.get("cf_tp1", 0), hg.get("cf_neither", 0)))
    L.append("- 누적 hyp_pnl_pts(차단 안 했으면 얻었을 pt): **%s pt** / 승률 %s (기준선 %s)" % (
        hg.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (hg["win_rate"] * 100)) if "win_rate" in hg else "—",
        ("%.1f%%" % (hg["baseline_win_rate"] * 100)) if hg.get("baseline_win_rate") is not None else "—",
    ))
    L.extend(_render_qty_profile("hurst_gate_shadow"))
    if hg.get("recommendation"):
        L.append("- **권고**: %s" % hg["recommendation"])
    if hg.get("reason"):
        L.append("- %s" % hg["reason"])
    L.append("")

    # [7] JointGateBlock counterfactual 상세
    L.append("## [7] JointGateBlock counterfactual (§3-7, 327차)")
    L.append("")
    L.append("- 이번 실행 resolve: %d건 / 누적 판정 %s건 (미판정 %s건)" % (
        jg.get("resolved_now", 0), jg.get("n_resolved", 0), jg.get("n_pending", 0)))
    L.append("- counterfactual 분포: STOP %s / TP1 %s / NEITHER %s" % (
        jg.get("cf_stop", 0), jg.get("cf_tp1", 0), jg.get("cf_neither", 0)))
    L.append("- 누적 hyp_pnl_pts(차단 안 했으면 얻었을 pt): **%s pt** / 승률 %s (기준선 %s)" % (
        jg.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (jg["win_rate"] * 100)) if "win_rate" in jg else "—",
        ("%.1f%%" % (jg["baseline_win_rate"] * 100)) if jg.get("baseline_win_rate") is not None else "—",
    ))
    if jg.get("meta_size_split"):
        L.append("- meta_size 구간별(tox_size 상수 구조 검증용):")
        for bucket, v in sorted(jg["meta_size_split"].items()):
            L.append("  - %s(meta%s0.55): n=%d hyp=%spt 승률=%.1f%%" % (
                bucket, "≥" if bucket == "high" else "<",
                v["n"], v["total_hyp_pnl_pts"], v["win_rate"] * 100))

    # ── [MW0601 420차] 419차 반영 4블록 ──────────────────────────────────
    _rs = jg.get("regime_split") or {}
    if _rs.get("boundary"):
        L.append("")
        L.append("### tox 체제 분리 (419차 P0 반영)")
        L.append("")
        L.append("- 경계: **%s** (`TOXICITY_CANCEL_CHURN_CEILING` 0.08→0.42 배포일)"
                 % _rs["boundary"])
        for _k, _lbl in (("pre", "구 체제(~경계 전)"), ("post", "신 체제(경계 이후)")):
            _v = _rs.get(_k) or {}
            L.append("- %s: n=%s 누적 hyp=%spt 승률=%.1f%%" % (
                _lbl, _v.get("n", 0), _v.get("total_hyp_pnl_pts", "—"),
                float(_v.get("win_rate", 0.0)) * 100))
        L.append("- **판정 대상**: %s" % jg.get("judged_regime_note", "—"))
        if jg.get("tox_ceiling_observed"):
            L.append("- 행에 기록된 tox_ceiling: 구=%s / 신=%s" % (
                jg["tox_ceiling_observed"].get("pre") or "미계측",
                jg["tox_ceiling_observed"].get("post") or "미계측"))
        if jg.get("regime_boundary_warning"):
            L.append("- ⚠ %s" % jg["regime_boundary_warning"])
        if jg.get("regime_date_mismatch"):
            L.append("- ⚠ **설정 불일치**: %s" % jg["regime_date_mismatch"])
        L.append("")
        L.append("> **구·신 체제를 합산하지 않는다.** JointGateBlock의 발동 전제가")
        L.append("> `tox_action==\"reduce\"`인데 419차 P0이 그 밴드 분포를 이동시켰다")
        L.append("> (block 23.3→8.6% / reduce 76.4→73.7% / pass 0.27→17.7%). 두 구간은")
        L.append("> 모집단이 달라 합치면 서로 다른 분포의 평균을 판정하게 된다.")

    _ep = jg.get("episode") or {}
    if _ep.get("n"):
        L.append("")
        L.append("### 에피소드 단위 재집계 + 증거강도")
        L.append("")
        L.append("- 신호 %s건 = **에피소드 %s건** (평균 %s신호/에피소드, 최대 연속 %s분)" % (
            jg.get("n_resolved", 0), _ep["n"], _ep.get("signals_per_episode", "—"),
            _ep.get("max_run", "—")))
        L.append("- 에피소드 첫신호 기준: 누적 hyp=**%spt** 승률=%.1f%%" % (
            _ep.get("total_hyp_pnl_pts", "—"), float(_ep.get("win_rate", 0.0)) * 100))
        if "t_stat" in _ep:
            L.append("- 건당 평균=%s sd=%s → **t=%s** (임계 |t|≥%.1f)" % (
                _ep.get("mean", "—"), _ep.get("sd", "—"), _ep["t_stat"],
                float(VALIDATION_CAMPAIGN["joint_gate_shadow"].get("evidence_t_abs", 2.0))))
        if jg.get("evidence"):
            L.append("- **증거강도: %s**" % jg["evidence"])
        L.append("")
        L.append("> **verdict와 증거강도는 다른 축이다.** verdict PASS는 `누적 hyp ≤ 0`")
        L.append("> 이분법이라 -13pt와 -0.01pt가 같은 판정을 받는다 — \"FAIL이 아니다\"와")
        L.append("> \"차단이 옳다\"는 다른 말이다. 통계 단위를 에피소드로 잡는 이유는")
        L.append("> JointGateBlock이 조건 지속 중 **매 분봉 재차단**하기 때문이다")
        L.append("> (같은 사건을 여러 번 세면 유의성이 부풀려진다).")

    _jk = jg.get("jackknife") or {}
    if _jk.get("n_days"):
        L.append("")
        L.append("### 단일일 민감도 (jackknife)")
        L.append("")
        L.append("- 거래일 %s일 · 최대 기여일: %s" % (
            _jk["n_days"],
            ("%s (%spt)" % (_jk["largest_day"]["date"], _jk["largest_day"]["contrib"]))
            if _jk.get("largest_day") else "—"))
        if _jk.get("sign_flip_days"):
            L.append("- ⚠ **이 날 하루를 빼면 누적 부호가 뒤집힌다**:")
            for _d, _c, _rest in _jk["sign_flip_days"]:
                L.append("  - %s 제거 → 누적 %spt → **%spt**" % (_d, _ep.get(
                    "total_hyp_pnl_pts", "—"), _rest))
            L.append("- → 판정이 단일 거래일에 걸려 있다. 조치 근거로 쓰지 말 것.")
        else:
            L.append("- 어느 거래일을 빼도 누적 부호 유지 — 단일일 의존 없음")

    _p1 = jg.get("p1_shadow_block") or {}
    if _p1.get("n"):
        L.append("")
        L.append("### 419차 P1(연속 배수) 실적용 시 차단 축 반사실")
        L.append("")
        L.append("- 계측 n=%s · 평균 tox 섀도배수=%s (현행 상수 0.70)" % (
            _p1["n"], _p1.get("shadow_mult_mean", "—")))
        L.append("- 차단 **유지** %s건 (%.1f%%) / **해제** %s건" % (
            _p1["kept_n"], _p1["kept_share"] * 100, _p1["freed_n"]))
        if _p1.get("freed", {}).get("n"):
            L.append("- 해제됐을 신호의 counterfactual: 누적 hyp=%spt 승률=%.1f%%" % (
                _p1["freed"]["total_hyp_pnl_pts"], _p1["freed"]["win_rate"] * 100))
        L.append("")
        L.append("> **판정하지 않는다 — 세기만 한다.** `[31] toxicity_reduce_mult_shadow`는")
        L.append("> 실제로 **체결된** reduce 밴드 진입만 보므로 JointGateBlock으로 차단된")
        L.append("> 신호는 그 채널에 들어가지 않는다. 여기가 그 사각지대다. 연속 배수가")
        L.append("> 실적용되면 `joint_mult`이 바뀌어 차단 여부 자체가 뒤집힐 수 있으므로")
        L.append("> ([31] FAIL 시 함께 읽을 것), 차단 축 비용을 미리 계측해 둔다.")
        L.append(">")
        L.append("> ⚠ **한 방향만 본다.** 이 표는 \"지금 차단된 신호\"만 담는다")
        L.append("> (joint_gate_shadow는 차단 시점에만 기록된다). 연속 배수는 반대")
        L.append("> 방향으로도 판정을 뒤집는다 — 예: meta=0.75 × tox_shadow=0.36이면")
        L.append("> 현행 0.525로 통과하지만 섀도로는 0.357이라 **차단**이다. 그런 건은")
        L.append("> 실제로 체결됐으므로 여기 없고 `trades`에 있다. 따라서 위 \"해제")
        L.append("> %s건\"을 P1의 순 노출 증가로 읽으면 안 된다 — 반대편이 빠져 있다."
                 % _p1["freed_n"])

    _fb = jg.get("meta_fallback_split") or {}
    if _fb.get("fallback") or _fb.get("learned"):
        L.append("")
        L.append("### meta falsy 폴백 분리 (419차 발견 ④)")
        L.append("")
        for _k, _lbl in (("fallback", "폴백(`or 0.5` 발동 — 모델은 size 0을 지시)"),
                         ("learned", "실학습값")):
            _v = _fb.get(_k) or {}
            if _v.get("n"):
                L.append("- %s: n=%s hyp=%spt 승률=%.1f%%" % (
                    _lbl, _v["n"], _v["total_hyp_pnl_pts"], _v["win_rate"] * 100))
        if _fb.get("unmeasured_n"):
            L.append("- 미계측(420차 이전 행): %s건 — 소급 복원 불가" % _fb["unmeasured_n"])
        L.append("")
        L.append("> 위 `meta_size 구간별(0.55)` 분할은 이 축과 섞여 있어 단독으로는")
        L.append("> 해석되지 않는다 — 구 체제 실측에서 low 버킷 94건 중 73건(78%)이")
        L.append("> 폴백이었다. **폴백은 모델이 \"사이즈를 주지 말라\"(size_mult=0.0)고")
        L.append("> 한 상태를 `or 0.5`가 밴드 중간값으로 승격시킨 것**이라 의미가 반대다.")
    elif _fb.get("unmeasured_n"):
        L.append("")
        L.append("- meta 폴백 분리: 미계측 %s건 (420차 계측 배선 이전 행)" % _fb["unmeasured_n"])

    # [MW0601 420차] [7] 자기편향 계측 — 원래 [29] 뒤에서 렌더링돼 [7]에서 보이지
    # 않던 것을 제자리로 옮겼다(_render_joint_mfe 도크스트링 참조).
    L.extend(_render_joint_mfe(jg))
    L.append("")
    L.extend(_render_qty_profile("joint_gate_shadow"))
    if jg.get("recommendation"):
        L.append("- **권고**: %s" % jg["recommendation"])
    if jg.get("reason"):
        L.append("- %s" % jg["reason"])
    L.append("")

    # [28]/[29] MW0601 405차 신설 채널 상세
    L.append("## [28] 사이징 역예측 감시 (MW0601 405차, P1-2)")
    L.append("")
    L.append("> 계약수를 키울수록 실현 순EV가 나빠지는가. 0801 점검 §9-3에서 3계약 이상 "
             "16전 1승 -2,642만원(이항검정 p=5.07e-07)이 확인됐으나 이를 보는 채널이 "
             "하나도 없었다. **자동 조치 없음** — MAX_CONTRACTS 인하는 주간회의 수동 결정(§9).")
    L.append("")
    L.append("- 포지션 %s건 / %s일 (부분청산 병합, 시스템 자동진입 — "
             "`entry_source=SYSTEM_AUTO` ∪ 컬럼 신설 이전 NULL행)" % (
                 siw.get("n_positions", "—"), siw.get("n_days", "—")))
    _qs = siw.get("qty_source") or {}
    if _qs:
        L.append("  - 계약수 출처: `entry_qty` 기록값 %s건 / 청산레그 합 폴백 %s건 "
                 "— 405차 `max` 집계는 409차 실측 반증으로 폐기(417차 ①)" % (
                     _qs.get("entry_qty_recorded", 0), _qs.get("leg_sum_fallback", 0)))
    for k, v in sorted((siw.get("by_bucket") or {}).items()):
        L.append("  - **%s**: n=%d 승률 %.1f%% 평균 %s원 누적 %s원 (최대손실 %s원)" % (
            k, v["n"], v["win_rate"] * 100, format(v["avg_pnl_krw"], ",.0f"),
            format(v["total_pnl_krw"], ",.0f"), format(v["min_pnl_krw"], ",.0f")))
    if siw.get("structural_block"):
        L.append("")
        L.append("- ⚠ **구조적 판정불가** — %s" % siw.get("structural_reason", ""))
        L.append("  - 이것은 \"표본이 모이는 중\"이 **아니다**. 표시를 분리한 이유는 "
                 "`toxicity_block_shadow`가 자기모순 조건으로 3개월간 0건인 채 "
                 "방치됐던 402차 후속3과 같은 유형이기 때문이다.")
    # [MW0601 471차 후속6 / G-1] 사이저 압력 **실측**. 바로 위 structural_reason이
    # 인용하는 "379건 중 86건(22.7%)"은 417차에 TRADE 로그로 한 번 센 값이고 그 뒤로
    # 매주 그대로 재인용돼 왔다 — 이 줄이 그것을 매주 갱신되는 실측으로 대체한다.
    # 판정에는 관여하지 않는다(§9 합격선 불변).
    _sp = siw.get("sizer_pressure") or {}
    L.append("")
    if _sp.get("available"):
        L.append("- **사이저 압력(실측, 471차 후속6 `sizing_trace`)**: %s"
                 % _sp.get("reason", "—"))
        L.append("  - 사이저 원본 수량 분포: %s / 최종 수량 분포: %s" % (
            _sp.get("qty_sizer_raw_hist"), _sp.get("qty_final_hist")))
        L.append("  - binding 게이트 빈도: %s" % _sp.get("binding_gate_hist"))
        L.append("  - ⚠ `sizing_trace`는 2026-08-14(471차 후속6) 이후 행에만 있다. "
                 "그 이전 구간은 **미측정**이지 압력 0이 아니다 — 위 417차 수치와 "
                 "직접 비교하지 말 것(집계 원천이 다르다).")
    else:
        L.append("- 사이저 압력(실측): 미가용 — %s" % _sp.get("reason", "이유 미상"))
    if siw.get("excl_above_cap_krw"):
        L.append("- 계약수 상한별 부분합(그 초과 거래를 **아예 안 했다면**): %s / 전체 %s원" % (
            " / ".join("상한%s=%s원" % (c, format(v, ",.0f"))
                       for c, v in sorted(siw["excl_above_cap_krw"].items())),
            format(siw.get("all_krw", 0), ",.0f")))
        L.append("  - ⚠ 진짜 counterfactual이 아니다 — 사이즈가 달랐으면 체결·청산 경로도 "
                 "달랐을 것이므로 \"상한 N이었다면\"이 아니라 \"그 거래들을 제외하면\"으로 읽을 것.")
    if siw.get("recommendation"):
        L.append("- **권고**: %s" % siw["recommendation"])
    if siw.get("reason"):
        L.append("- %s" % siw["reason"])
    L.append("")

    L.append("## [29] mean-revert 레짐 사이즈 (MW0601 405차, P1-3)")
    L.append("")
    L.append("> 0801 점검 §6-3의 313차 z검정 5개 세그먼트 중 **유일하게 Bonferroni 생존**한 축 "
             "(mean-revert 승률 45.7% vs 69.1%, z=-2.61 p=0.00911, n=35/152, 일자 분산 9일). "
             "n=35·최다일 40%로 경계선이라 누적 확인이 필요하다. "
             "**\"진입 차단\"이 아니라 사이즈/등급 축 처방 가설**이다(317차 FalseBlock 교훈).")
    L.append("")
    L.append("- 포지션 %s건 / %s일 (부분청산 병합, 시스템 자동진입 — "
             "`entry_source=SYSTEM_AUTO` ∪ 컬럼 신설 이전 NULL행)" % (
                 mrs.get("n_positions", "—"), mrs.get("n_days", "—")))
    for k, v in sorted((mrs.get("by_bucket") or {}).items()):
        L.append("  - **%s**: n=%d 승률 %.1f%% 평균 %s원 누적 %s원" % (
            k, v["n"], v["win_rate"] * 100, format(v["avg_pnl_krw"], ",.0f"),
            format(v["total_pnl_krw"], ",.0f")))
    if mrs.get("recommendation"):
        L.append("- **권고**: %s" % mrs["recommendation"])
    if mrs.get("reason"):
        L.append("- %s" % mrs["reason"])

    # [MW0601 420차] [7]의 MFE 병기 절은 여기서 _render_joint_mfe()로 분리해 [7] 본문
    # 바로 아래로 옮겼다. 원래 이 자리(= [29] mean-revert 상세 뒤)에서 렌더링돼
    # `jg` 데이터인데도 [29] 아래 붙은 H3처럼 보였다 — [7]을 읽는 사람이 자기 채널의
    # 자기편향 계측을 두 섹션 건너에서 찾아야 했다. 순수 이동(로직 무변경).
    L.append("")

    # [8] KellyAdvisedSkip × C등급 상세
    L.append("## [8] KellyAdvisedSkip × C등급 누적 성과 (341차 신설)")
    L.append("")
    L.append("- C등급+KellySkip 체결 n=%s | 누적 순PnL=%s원 | 평균=%s원 | 승률=%s" % (
        ks.get("n", 0),
        format(ks["total_pnl_krw"], ",.0f") if "total_pnl_krw" in ks else "—",
        format(ks["avg_pnl_krw"], ",.0f") if "avg_pnl_krw" in ks else "—",
        ("%.1f%%" % (ks["win_rate"] * 100)) if "win_rate" in ks else "—",
    ))
    if ks.get("baseline_n"):
        L.append("- 비교(C등급, KellySkip 아님) n=%s | 평균=%s원 | 승률=%s" % (
            ks["baseline_n"],
            format(ks["baseline_avg_pnl_krw"], ",.0f") if ks.get("baseline_avg_pnl_krw") is not None else "—",
            ("%.1f%%" % (ks["baseline_win_rate"] * 100)) if ks.get("baseline_win_rate") is not None else "—",
        ))
    if ks.get("grade_split"):
        L.append("- 등급별(KellySkip=1 전체, 참고용):")
        for grade, v in sorted(ks["grade_split"].items()):
            L.append("  - %s급: n=%d 누적PnL=%s원 승률=%.1f%%" % (
                grade, v["n"], format(v["total_pnl_krw"], ",.0f"), v["win_rate"] * 100))
    if ks.get("recommendation"):
        L.append("- **권고**: %s" % ks["recommendation"])
    if ks.get("reason"):
        L.append("- %s" % ks["reason"])
    L.append("")

    # [9] OPEN_VOLATILE 시가이격 counterfactual 상세
    L.append("## [9] OPEN_VOLATILE 시가이격 counterfactual (§14, 354차)")
    L.append("")
    L.append("- 이번 실행 resolve: %d건 / 누적 판정 %s건 (미판정 %s건)" % (
        og.get("resolved_now", 0), og.get("n_resolved", 0), og.get("n_pending", 0)))
    L.append("- counterfactual 분포: STOP %s / TP1 %s / NEITHER %s" % (
        og.get("cf_stop", 0), og.get("cf_tp1", 0), og.get("cf_neither", 0)))
    L.append("- 누적 hyp_pnl_pts(차단 안 했으면 얻었을 pt): **%s pt** / 승률 %s (기준선 %s)" % (
        og.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (og["win_rate"] * 100)) if "win_rate" in og else "—",
        ("%.1f%%" % (og["baseline_win_rate"] * 100)) if og.get("baseline_win_rate") is not None else "—",
    ))
    if "avg_gap_pt" in og:
        L.append("- 평균 gap_pt=%s / 평균 atr_at_block=%s (기준점 재설계 시 캘리브레이션 근거)" % (
            og["avg_gap_pt"], og["avg_atr_at_block"]))
    if og.get("recommendation"):
        L.append("- **권고**: %s" % og["recommendation"])
    if og.get("reason"):
        L.append("- %s" % og["reason"])
    L.append("")

    # [11] qty=1 손실1차 조기청산 counterfactual 상세
    L.append("## [11] qty=1 손실1차(Loss Tier1) 조기청산 counterfactual (363차 / 425차 개정)")
    L.append("")
    L.append("**0804 4-3 딥다이브에서 집행 축의 유일한 생존 처방으로 확정된 채널이다.**")
    L.append("급행 풀스톱 16건 중 **13건(-2,319,612원, 81%)이 qty=1**이고, qty=1은")
    L.append("`is_loss_tier1_hit()`가 \"물리적 분할 불가\"로 원천 제외해 전액이 풀스톱까지")
    L.append("노출된다. 같은 딥다이브에서 다른 후보는 전부 떨어졌다 —")
    L.append("손절 유예·스톱 확대는 **반증**(급행 16건 중 14건이 청산 후 더 나빠짐),")
    L.append("체결 슬리피지는 **대상 아님**(FAST 평균 -0.0157pt), 지정가 진입은 **미지지**")
    L.append("(최선 변형도 일자단위 p=0.45·델타의 59%가 단일일), 진입 판별자는 421차")
    L.append("Phase A가 245피처 **BH FDR 통과 0개**. \"스톱이 옳았다\"면 남는 레버는")
    L.append("**더 일찍 끊는 것**이고 그게 이 채널이다.")
    L.append("")
    L.append("- 이번 실행 resolve: %d건 / 누적 판정 %s건 (미판정 %s건)" % (
        lt1.get("resolved_now", 0), lt1.get("n_resolved", 0), lt1.get("n_pending", 0)))
    L.append("- 누적 hyp_pnl_pts(tier1가 조기청산 vs 실제 실현 pt 차이): **%s pt** / 승률 %s" % (
        lt1.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (lt1["win_rate"] * 100)) if "win_rate" in lt1 else "—",
    ))
    # [425차] 판정 2겹 — 경제성(누적 pt)과 재현성(일자단위)을 분리 표기한다.
    L.append("- 판정 조건 **2겹**: ① 누적 hyp > 왕복비용×2 → **%s** / "
             "② 일자단위 부호검정 p<%.2f → **%s** (%s/%s일, p=%s)" % (
        ("충족" if lt1.get("econ_ok") else "미충족" if "econ_ok" in lt1 else "—"),
        float((VALIDATION_CAMPAIGN.get("loss_tier1_qty1_shadow") or {}).get("alpha", 0.05)),
        ("충족" if lt1.get("repro_ok") else "미충족" if "repro_ok" in lt1 else "—"),
        lt1.get("days_positive", "—"), lt1.get("paired_days", "—"),
        lt1.get("sign_p", "—")))
    if lt1.get("n_live_excluded") or lt1.get("n_remainder_excluded"):
        L.append("- 판정 제외: 실적용 이후 %s건 · tier1 잔여계약 %s건 "
                 "(전자는 반사실이 실제와 같아지고, 후자는 이미 한 번 보호받은 다른 "
                 "모집단이라 [14]가 맡는다)" % (
                     lt1.get("n_live_excluded", 0), lt1.get("n_remainder_excluded", 0)))
    if lt1.get("remainder_backfilled"):
        L.append("- ⚠ 구버전 행 %s건을 `from_tier1_remainder`로 소급 보정했다 "
                 "(trades의 '손절1차 조기축소' 레그 유무 기준)" % lt1["remainder_backfilled"])
    if lt1.get("recommendation"):
        L.append("- **권고**: %s" % lt1["recommendation"])
    if lt1.get("reason"):
        L.append("- %s" % lt1["reason"])
    if "edge_uncertainty_corr" in lt1:
        L.append("- [제안3 편입, 참고용] edge_ratio(=|기대엣지|/불확실성, n=%s, 평균=%s) vs "
                  "실현 pt 스피어만 상관: **%s** (게이트 아님 — 등급/사이징 강화 여부는 "
                  "표본이 더 쌓인 뒤 별도 검토)" % (
            lt1.get("n_edge_samples", "—"), lt1.get("edge_ratio_mean", "—"),
            lt1.get("edge_uncertainty_corr", "—")))
    elif lt1.get("n_edge_samples", 0) > 0:
        L.append("- [제안3 편입] edge_ratio 표본 %s건 — 상관 계산 최소치(10건) 미달, 축적 대기" %
                  lt1.get("n_edge_samples", 0))
    L.append("")
    L.append("> **거래일이 병목이지 건수가 아니다.** 일자단위 양측 부호검정에서 얻을 수")
    L.append("> 있는 최소 p는 n=5일 때 0.0625로, α=0.05를 **원리적으로** 통과할 수 없다")
    L.append("> (n=6부터 0.03125로 기각 가능). 그래서 `min_days=6`을 걸었다 —")
    L.append("> 425차 등록 시점에 이미 5거래일 전부 양수였고 그 바닥에 닿아 있었다.")
    L.append("> ")
    L.append("> **FAIL이어도 자동 전환 금지.** 적용은 `LOSS_TIER1_QTY1_ENABLED = True` +")
    L.append("> `LOSS_TIER1_QTY1_EFFECTIVE_DATE` 기입이고 주간회의 수동 결정이다(§9).")
    L.append("> qty=1은 쪼갤 수 없으므로 이 정책은 부분 축소가 아니라 **qty=1 한정")
    L.append("> 손절폭 절반**이다 — 회복했을 포지션을 조기 손절하는 비용이 따르며,")
    L.append("> 그 비용은 위 hyp_pnl_pts에 이미 차감돼 있다(음수 표본이 그것이다).")
    L.append("> ")
    L.append("> ⚠ **전환하면 이 채널의 판정은 얼어붙는다** — 실제로 자르게 되므로")
    L.append("> 반사실이 실제와 같아진다. 그래서 전환 후 기록은 `live_active=1`로")
    L.append("> 태깅해 판정에서 빼고, 회귀 감시는 [15]·[13]이 맡는다.")
    L.append("")

    # [12] qty=1 TP1 이후 트레일 폭 counterfactual 상세
    L.append("## [12] qty=1 TP1 이후 트레일 폭 counterfactual (363차 후속, 0721 제안4 편입)")
    L.append("")
    L.append("- 이번 실행 resolve: %d건 / 누적 판정 %s건 (미판정 %s건)" % (
        t1t.get("resolved_now", 0), t1t.get("n_resolved", 0), t1t.get("n_pending", 0)))
    L.append("- counterfactual 분포: TRAIL_STOP %s / FORCE_EXIT %s" % (
        t1t.get("cf_trail_stop", 0), t1t.get("cf_force_exit", 0)))
    L.append("- 누적 hyp_pnl_pts(4단계 트레일링 지속 vs 실제 static lock 실현 pt 차이): "
              "**%s pt** / 승률 %s" % (
        t1t.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (t1t["win_rate"] * 100)) if "win_rate" in t1t else "—",
    ))
    if t1t.get("recommendation"):
        L.append("- **권고**: %s" % t1t["recommendation"])
    if t1t.get("reason"):
        L.append("- %s" % t1t["reason"])
    L.append("")

    # [13] 등급별 순EV 역전 감시 상세
    L.append("## [13] 등급별 순EV 역전 감시 (366차, 0722 정기점검 딥다이브)")
    L.append("")
    if gei.get("by_grade"):
        L.append("| 등급 | n | 평균 순EV(원) | 누적(원) | 승률 | 최대손실(원) | 표준편차(원) |")
        L.append("|---|---|---|---|---|---|---|")
        for g in ("A", "B", "C"):
            v = gei["by_grade"].get(g)
            if not v:
                continue
            L.append("| %s | %d | %s | %s | %.1f%% | %s | %s |" % (
                g, v["n"], format(v["avg_pnl_krw"], ",.0f"),
                format(v["total_pnl_krw"], ",.0f"), v["win_rate"] * 100,
                format(v["min_pnl_krw"], ",.0f"), format(v["stdev_pnl_krw"], ",.0f")))
        L.append("")
        L.append("> [367차, 제안4 편입] 최대손실·표준편차 보강 — 평균만으로는 \"등급 전체가")
        L.append("> 고르게 나쁨\"과 \"소수 초대형 손실(fat-tail)이 평균을 끌어내림\"을 구분할")
        L.append("> 수 없다. 0722 딥다이브: A등급 4주 누적손실의 84%가 [15]에서 관찰하는")
        L.append("> \"TP1 도달 전 급행 풀스톱\" 9건에 집중돼 있었음 — 표준편차가 크고")
        L.append("> 최대손실이 평균의 여러 배면 이 fat-tail 구조를 의심할 것.")
    # [MW0601 409차 / R5] 등급 × 계약수 교차 분해 — 표시 전용, 판정 미반영
    _qs = gei.get("qty_split") or {}
    if _qs:
        L.append("")
        L.append("**등급 × 계약수 분해** — 이 채널이 \"등급별\" 역전으로 부르는 현상이")
        L.append("계약수 축으로 더 잘 설명되는지 본다:")
        L.append("")
        L.append("| 등급 | qty≤2 n / 누적(원) / 평균(원) | qty≥3 n(승) / 누적(원) / 평균(원) |")
        L.append("|---|---|---|")
        for g in ("A", "B", "C"):
            v = _qs.get(g)
            if not v:
                continue

            def _f(s):
                if not s:
                    return "—"
                return "%d / %s / %s" % (s["n"], format(s["total_pnl_krw"], ",.0f"),
                                         format(s["avg_pnl_krw"], ",.0f"))
            _ge3 = v.get("ge3")
            _ge3s = ("%d(승%d) / %s / %s" % (
                _ge3["n"], _ge3["n_win"], format(_ge3["total_pnl_krw"], ",.0f"),
                format(_ge3["avg_pnl_krw"], ",.0f"))) if _ge3 else "—"
            L.append("| %s | %s | %s |" % (g, _f(v.get("le2")), _ge3s))
        L.append("")
        _persist = gei.get("inversion_persists_qty_le2")
        if _persist is False:
            L.append("> ⚠ **qty≤2로 한정하면 A/C 역전이 사라진다.** A가 적자인 것은 등급 자체가")
            L.append("> 역예측이어서가 아니라 **A등급이 큰 계약수를 더 많이 받았기 때문**일 수")
            L.append("> 있다. 그렇다면 GradeEVGuard(등급 강등)는 잘못된 처방이다 — 등급을")
            L.append("> 낮춰도 계약수 배분이 그대로면 문제가 남는다.")
        elif _persist is True:
            L.append("> qty≤2로 한정해도 A/C 역전이 유지된다 — 계약수만으로는 설명되지 않는다.")
        L.append("> ⚠ **qty≥3 표본이 얇다**(313차: 이걸로 확정 결론 금지). 또 이 표는 캠페인")
        L.append("> 구간 한정이라, 전체 기간을 본 `CLAUDE.md` 전환기준 ⑧의 §9-3")
        L.append("> \"3계약 이상 16전 1승\"과 모집단이 다르다 — 두 수치를 같은 것으로 읽지 말 것.")
        L.append("> **판정식은 무변경**(A 평균 순EV < 0 → FAIL). 계약수 축 판정은")
        L.append("> [28] `sizing_inversion_watch`가 맡는다 — 함께 볼 것.")
    if gei.get("recommendation"):
        L.append("- **권고**: %s" % gei["recommendation"])
    if gei.get("reason"):
        L.append("- %s" % gei["reason"])
    if gei.get("error"):
        L.append("- ⚠ %s" % gei["error"])
    L.append("")

    # [14] Tier1 잔여계약 2단계 조기청산 counterfactual 상세
    L.append("## [14] Tier1 잔여계약 2단계 조기청산 counterfactual (367차)")
    L.append("")
    L.append("- 이번 실행 resolve: %d건 / 누적 판정 %s건 (미판정 %s건)" % (
        lt2.get("resolved_now", 0), lt2.get("n_resolved", 0), lt2.get("n_pending", 0)))
    L.append("- 누적 hyp_pnl_pts(tier2가 조기청산 vs 실제 잔여계약 실현 pt 차이): **%s pt** / 승률 %s" % (
        lt2.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (lt2["win_rate"] * 100)) if "win_rate" in lt2 else "—",
    ))
    if lt2.get("recommendation"):
        L.append("- **권고**: %s" % lt2["recommendation"])
    if lt2.get("reason"):
        L.append("- %s" % lt2["reason"])
    if lt2.get("error"):
        L.append("- ⚠ %s" % lt2["error"])
    L.append("")

    # [15] 급행 풀스톱(TP1 미도달) 관찰 상세
    L.append("## [15] 급행 풀스톱(TP1 미도달) 관찰 (367차, 관찰 전용 — 정책 게이트 아님)")
    L.append("")
    L.append("- 관찰 기준: 하드스톱 청산 + 보유시간 ≤ %s초 + 진입~청산 구간에 TP1 관련 로그"
              " 없음" % frw.get("fast_exit_max_sec", "—"))
    L.append("- 급행 하드스톱 %s건 중 TP1 미도달 %s건" % (
        frw.get("n_fast_hardstop", 0), frw.get("n_no_tp1", 0)))
    if frw.get("by_grade"):
        L.append("")
        L.append("| 등급 | n | 누적 순PnL(원) | 손실건수 |")
        L.append("|---|---|---|---|")
        for g, v in sorted(frw["by_grade"].items()):
            L.append("| %s | %d | %s | %d |" % (
                g, v["n"], format(v["total_pnl_krw"], ",.0f"), v["n_loss"]))
    if frw.get("reason"):
        L.append("- %s" % frw["reason"])
    if frw.get("error"):
        L.append("- ⚠ %s" % frw["error"])
    L.append("- 이 채널은 PASS/FAIL을 판정하지 않는다 — 이 패턴 자체를 차단할 정책이")
    L.append("  아직 없어 판정이 무의미하다. GradeEVGuard·loss_tier1_qty1_shadow·")
    L.append("  loss_tier2_remainder_shadow가 다루는 문제의 선행지표로만 참고할 것.")
    L.append("")

    # [16] chase+foreign 조합 관찰 상세
    L.append("## [16] chase+foreign 조합 관찰 (368차, 관찰 전용 — 정책 게이트 아님)")
    L.append("")
    L.append("- 관찰 기준: [진입체크] 로그에서 `10_chase`·`6_foreign` 두 항목만 동시 실패"
              " (나머지 항목 무관)")
    L.append("- 로그-DB 매칭 %s건 중 동시실패 %s건" % (
        cfc.get("n_matched", 0), cfc.get("n_combo", 0)))
    if cfc.get("by_grade"):
        L.append("")
        L.append("| 등급 | n | 누적 순PnL(원) | 손실건수 |")
        L.append("|---|---|---|---|")
        for g, v in sorted(cfc["by_grade"].items()):
            L.append("| %s | %d | %s | %d |" % (
                g, v["n"], format(v["total_pnl_krw"], ",.0f"), v["n_loss"]))
    if cfc.get("reason"):
        L.append("- %s" % cfc["reason"])
    if cfc.get("error"):
        L.append("- ⚠ %s" % cfc["error"])
    L.append("- CHASE_FOREIGN_COMBO_GUARD_ENABLED(config/settings.py, 섀도) 활성화 여부")
    L.append("  판단 근거 표본 축적용. P4(CVD+OFI, 268차)와 동일 계열 논리이나 표본이")
    L.append("  작아(368차 등록 시점 n=5) 즉시 정책화하지 않는다 — §9 사전등록 원칙.")
    L.append("")

    # [17] 청산 체결 슬리피지 관찰 상세
    L.append("## [17] 청산 체결 슬리피지 (369차 · 439차 P2로 관찰→판정 승격)")
    L.append("")
    L.append("- 관찰 대상: 모든 청산 주문의 의도가(price_hint) vs 실체결가(fill_price)")
    L.append("  (exit_fill_slippage 테이블, main.py::_ts_record_exit_fill_slippage())")
    L.append("- 판정: **%s** — %s" % (_fmt_channel_verdict(efs),
                                     efs.get("reason", efs.get("error", "—"))))
    L.append("")
    L.append("### [17-V] 유효-hint 부분표본 — 판정 근거 (439차 P2)")
    L.append("")
    L.append("> 🔴 **이 채널은 자기 경보를 스스로 억제하고 있었다.** note 조건이")
    L.append("> `풀링 평균 > 가정`인데, 풀링 평균이 **봉중 경로에 오염**돼 음수로 끌려가")
    L.append("> 조건이 성립할 수 없었다. 봉중은 `price_hint`가 봉 고저가에서 유도한")
    L.append("> **허구의 스톱가**라 주문(시장가)과 무관하다 — 제외가 옳다([48-T]에서 확정).")
    L.append("> 경로 분류는 `bar_stop_path_watch._path_of()` **단일 소스**를 재사용한다.")
    L.append("")
    L.append("| 구분 | n | 평균(pt) | 가정 대비 | 경보 조건 성립 |")
    L.append("|---|---|---|---|---|")
    _asm = efs.get("assumed_slippage_pts_per_side") or 0.0
    for _nm, _n, _av in (
            ("풀링(구 헤드라인)", efs.get("n"), efs.get("avg_slippage_pts")),
            ("봉중 — hint 허구, **제외**", efs.get("n_bar_excluded"), efs.get("avg_bar_pts")),
            ("**유효-hint(틱/종가/목표)**", efs.get("n_valid"), efs.get("avg_valid_pts"))):
        if _n is None or _av is None:
            continue
        L.append("| %s | %s | %+.4f | %s | %s |" % (
            _nm, _n, _av,
            ("%.1f배" % (_av / _asm)) if _asm else "—",
            "✅ 예" if _av > _asm else "❌ 아니오"))
    L.append("")
    L.append("- 일자단위(313차 — **판정 단위**): 평균 %s pt · 중앙값 %s pt · "
             "초과일 **%s/%s**(과반 %s) · 부호검정 **p=%s**" % (
                 efs.get("avg_valid_day_pts", "—"), efs.get("median_valid_day_pts", "—"),
                 efs.get("days_over_assumed", "—"), efs.get("n_valid_days", "—"),
                 "예" if efs.get("days_majority_over") else "아니오",
                 efs.get("sign_p", "—")))
    L.append("  - 🔴 방향 판정은 **일자 과반**이 기준이다 — 일자 *평균*이 아니다.")
    L.append("    부호검정은 양측이라 \"9일이 가정 미만이고 1일만 폭등\"해도 유의가 뜨고,")
    L.append("    그 1일이 평균을 끌어올려 평균 기준이면 FAIL이 나버린다 — 일자단위로")
    L.append("    내려온 이유(이상치 강건성)가 무너진다. 과반을 쓰면 부호검정이 세는")
    L.append("    통계량과 방향 판정이 **같은 것**이 된다(439차 P2, 회귀 테스트 (4)).")
    if efs.get("day_means"):
        L.append("- 일자별 유효-hint 평균: %s" % " / ".join(
            "%s %+.3f" % (d[5:], v) for d, v in sorted(efs["day_means"].items())))
    if efs.get("event_day_split"):
        L.append("- 🔴 **이벤트단위와 일자단위의 부호가 갈린다** — 소표본 일자가 동일")
        L.append("  가중을 받아 끌고 있다는 뜻이다. 313차상 **일자단위가 판정 단위**이며,")
        L.append("  이벤트 수치만 보고 상수를 바꾸면 372차가 이상치로 PSI 임계를 바꿀 뻔한")
        L.append("  것과 같은 함정이다.")
    L.append("")
    L.append("> ⚠ **사전등록 정직성 고지** — 첫 관측치는 이 승격 **전에 이미 봤다**")
    L.append("> ([48]의 고지와 같은 취급). 다만 비교 임계 **0.02pt는 사후에 고른 값이")
    L.append("> 아니다** — 369차에 고정된 모델 가정(`slippage_ticks_per_side=1.0`)을")
    L.append("> 그대로 쓴다. 움직인 것은 임계가 아니라 **오염 제거와 검정 단위**다.")
    L.append("> ⚠ **PASS는 \"가정이 옳다고 증명됐다\"가 아니라 \"구분되지 않는다\"**이다.")
    L.append("> ⚠ FAIL이어도 `slippage_ticks_per_side`를 **자동으로 바꾸지 않는다** —")
    L.append("> 캠페인 전 채널의 왕복비용에 쓰이므로 §3에 따라 검증 시계 리셋이 필요하다.")
    L.append("")
    if efs.get("by_reason"):
        L.append("")
        L.append("| 청산사유 | n | 평균 슬리피지(pt) |")
        L.append("|---|---|---|")
        for reason, v in sorted(efs["by_reason"].items(), key=lambda kv: -kv[1]["n"]):
            L.append("| %s | %d | %s |" % (reason, v["n"], v["avg_pts"]))
    if efs.get("note"):
        L.append("- ⚠ **%s**" % efs["note"])
    if efs.get("reason"):
        L.append("- %s" % efs["reason"])
    if efs.get("error"):
        L.append("- ⚠ %s" % efs["error"])
    L.append("- 계기: 0723 유일 거래에서 TP1 ATR보호전환(+0.35pt 확정 예정)이 체결")
    L.append("  슬리피지로 순손실(-0.02pt)로 뒤집힘. slippage_ticks_per_side(현재 1.0,")
    L.append("  0.02pt)는 캠페인 전 채널의 왕복비용 계산에 쓰이는 공통 가정이므로,")
    L.append("  이 채널의 실측치가 그 가정과 다르더라도 즉시 자동 재보정하지 않는다")
    L.append("  — 바꾸려면 §3 사전등록 원칙에 따라 검증 시계를 리셋해야 한다.")
    L.append("")

    # [18] RegimeExhaustionGate 상세
    L.append("## [18] RegimeExhaustionGate 탈진 반전 counterfactual (379차, 관찰 전용 — 정책 게이트 아님)")
    L.append("")
    L.append("- 발동 조건: hurst<%.2f(평균회귀) AND 60분 느린 연장폭(price_extension_atr_60m)"
              " |값|>%.1fATR AND (10_chase 또는 11_countertrend 소프트 실패)" % (
        HURST_RANGE_THRESHOLD, REGIME_EXHAUSTION_EXT_ATR_THRESHOLD))
    L.append("- 계기: 0723 정기점검 딥다이브 — 진입 직후 반복 반전 패턴 3항. 10_chase"
              "(10분 룩백)는 여러 다리에 걸친 느린 탈진을 놓친다는 게 핵심 발견"
              "(0723 11:41 SHORT — 직전 10분은 안정, 이전 90분간 -35pt).")
    L.append("- 해석: hyp_pnl_pts는 **신호 방향(추격 방향)대로 갔을 때의 결과** — "
              "다른 섀도 채널과 부호 해석이 반대다. 음수 우세면 탈진 반전 가설 지지.")
    L.append("- 표본: 해결=%s건 대기중=%s건, 누적 hyp_pnl_pts=%spt "
              "(STOP=%s / TP1=%s / NEITHER=%s)" % (
        reg.get("n_resolved", 0), reg.get("n_pending", 0),
        reg.get("total_hyp_pnl_pts", "—"),
        reg.get("cf_stop", 0), reg.get("cf_tp1", 0), reg.get("cf_neither", 0)))
    if "avg_ext_atr_60m" in reg:
        L.append("- 평균 60분 연장폭=%spt(ATR배수) 평균 hurst=%s "
                  "(chase실패=%s건 / countertrend실패=%s건)" % (
            reg.get("avg_ext_atr_60m"), reg.get("avg_hurst"),
            reg.get("n_chase_failed", 0), reg.get("n_countertrend_failed", 0)))
    if reg.get("recommendation"):
        L.append("- **%s**" % reg["recommendation"])
    if reg.get("reason"):
        L.append("- %s" % reg["reason"])
    if reg.get("error"):
        L.append("- ⚠ %s" % reg["error"])
    L.append("- REGIME_EXHAUSTION_GATE_ENABLED(config/settings.py, 섀도) 활성화 여부")
    L.append("  판단 근거 표본 축적용(목표 min_samples=%d, hurst_gate_shadow·"
              "open_gap_shadow와 동일 기준) — §9 사전등록 원칙, 즉시 자동 전환 없음." % (
        VALIDATION_CAMPAIGN["regime_exhaustion_watch"]["min_samples"]))
    L.append("")

    # [19] ToxicityGate block counterfactual 상세
    L.append("## [19] ToxicityGate block counterfactual (신설)")
    L.append("")
    L.append("- 이번 실행 resolve: %d건 / 누적 판정 %s건 (미판정 %s건)" % (
        txb.get("resolved_now", 0), txb.get("n_resolved", 0), txb.get("n_pending", 0)))
    L.append("- counterfactual 분포: STOP %s / TP1 %s / NEITHER %s" % (
        txb.get("cf_stop", 0), txb.get("cf_tp1", 0), txb.get("cf_neither", 0)))
    L.append("- 누적 hyp_pnl_pts(차단 안 했으면 얻었을 pt): **%s pt** / 승률 %s (기준선 %s)" % (
        txb.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (txb["win_rate"] * 100)) if "win_rate" in txb else "—",
        ("%.1f%%" % (txb["baseline_win_rate"] * 100)) if txb.get("baseline_win_rate") is not None else "—",
    ))
    if "avg_toxicity_score" in txb:
        L.append("- 평균 toxicity_score=%s / 평균 toxicity_score_ma=%s (block_threshold 재검토 시 캘리브레이션 근거)" % (
            txb["avg_toxicity_score"], txb["avg_toxicity_score_ma"]))
    if txb.get("recommendation"):
        L.append("- **권고**: %s" % txb["recommendation"])
    if txb.get("reason"):
        L.append("- %s" % txb["reason"])
    L.append("- action=\"reduce\"는 실제 축소 체결로 trades에 남으므로 이 채널 대상 아님 —"
              " action=\"block\"만 계측(open_gap_shadow와 동일 원칙).")
    L.append("")

    # [20] BAR_ONLY_RELAX 수용/롤백 상세
    L.append("## [20] BAR_ONLY_RELAX 수용/롤백 감시 (402차 후속, 관찰 전용 — 자동 롤백 아님)")
    L.append("")
    if wcw.get("error"):
        L.append("> ⚠ %s" % wcw["error"])
    else:
        L.append("- 발효일 **%s** (401차 커밋이 2026-07-29 장 마감 후라 다음 세션부터 적용)"
                  % wcw.get("effective_date", "—"))
        L.append("- 계측일: 완화 전 %s일 / 완화 후 %s일"
                  % (wcw.get("n_days_pre", 0), wcw.get("n_days_post", 0)))
        L.append("- collapse 비율: 기준선 %s → 완화 후 %s (목표 %s±%s)" % (
            ("%.1f%%" % (wcw["baseline_ratio"] * 100)) if wcw.get("baseline_ratio") is not None else "—",
            ("%.1f%%" % (wcw["post_ratio"] * 100)) if wcw.get("post_ratio") is not None else "—",
            "%.0f%%" % (float(VALIDATION_CAMPAIGN.get("weight_collapse_watch", {}).get("target_ratio", 0.20)) * 100),
            "%.0f%%p" % (float(VALIDATION_CAMPAIGN.get("weight_collapse_watch", {}).get("target_tolerance", 0.07)) * 100),
        ))
        if wcw.get("effect"):
            L.append("- 효과 판정: **%s**" % wcw["effect"])
        if wcw.get("regressed"):
            L.append("- **회귀 감지(Q3 분포 불일치 부작용 의심)**: %s" % " / ".join(wcw["regressed"]))
        if wcw.get("daily"):
            L.append("")
            L.append("| 일자 | 계측 분봉 | collapse% | 3m 적중 | 5m 적중 | 구분 |")
            L.append("|---|---|---|---|---|---|")
            for d, v in sorted(wcw["daily"].items()):
                _a3 = v["acc"].get("3m")
                _a5 = v["acc"].get("5m")
                L.append("| %s | %d | %.1f%% | %s | %s | %s |" % (
                    d, v["n"], v["ratio"] * 100,
                    ("%.1f%%" % (_a3 * 100)) if _a3 is not None else "—",
                    ("%.1f%%" % (_a5 * 100)) if _a5 is not None else "—",
                    "완화후" if d >= wcw.get("effective_date", "") else "완화전"))
        if wcw.get("recommendation"):
            L.append("")
            L.append("- **권고**: %s" % wcw["recommendation"])
        if wcw.get("reason"):
            L.append("")   # 표 직후 리스트가 붙으면 Markdown 표 렌더링이 깨진다
            L.append("- %s" % wcw["reason"])
    L.append("")
    L.append("> `weight_collapsed`는 398차(2026-07-28 저녁) 배포분부터 기록된다 — 그 이전")
    L.append("> 일자는 컬럼이 NULL이라 \"collapse 0건\"이 아니라 \"미계측\"이므로 집계에서")
    L.append("> 제외한다. 완화 전 기준선이 사실상 2026-07-29 단일일이라는 뜻이므로,")
    L.append("> min_days(기본 3거래일) 미만에서는 판정을 보류한다(313차 원칙).")
    L.append("> 롤백은 `config/settings.py:BAR_ONLY_RELAX_ENABLED = False` 1줄로 즉시 가역.")
    L.append("> 일 단위 확인은 `scripts/weight_collapse_monitor.py`.")
    L.append("")

    # [21] 방향별 순EV 상세
    L.append("## [21] 방향별 순EV 감시 (402차 후속5, [13]의 방향 축 미러)")
    L.append("")
    if dev.get("error"):
        L.append("> ⚠ %s" % dev["error"])
    else:
        L.append("- 필터: `entry_source='%s'` — 진입 %s건(원본 %s행, 부분청산 병합)"
                  % (dev.get("entry_source_filter", "?"),
                     dev.get("n_entries_merged", 0), dev.get("n_rows_raw", 0)))
        L.append("")
        L.append("| 방향 | n | 평균 순EV(원) | 누적(원) | 승률 | 최대손실(원) | 표준편차(원) |")
        L.append("|---|---|---|---|---|---|---|")
        for d in ("LONG", "SHORT"):
            v = _dv.get(d)
            if not v:
                continue
            L.append("| %s | %d | %s | %s | %.1f%% | %s | %s |" % (
                d, v["n"], format(v["avg_pnl_krw"], ",.0f"),
                format(v["total_pnl_krw"], ",.0f"), v["win_rate"] * 100,
                format(v["min_pnl_krw"], ",.0f"), format(v["stdev_pnl_krw"], ",.0f")))
        if dev.get("recommendation"):
            L.append("")
            L.append("- **권고**: %s" % dev["recommendation"])
        if dev.get("reason"):
            L.append("")
            L.append("- %s" % dev["reason"])
    L.append("")
    L.append("> **[13]과 필터가 다르다(의도적)**. [13]은 `grade IN ('A','B','C')`이라")
    L.append("> 구버전 `entry_source=NULL`·`OPERATOR_MANUAL` 행이 포함되지만, 이 채널은")
    L.append("> `SYSTEM_AUTO` 한정이다 — 방향 편향은 시스템 판단의 문제이므로 수동·레거시")
    L.append("> 진입을 섞으면 안 된다. 두 채널의 표본 수가 다른 것은 결함이 아니다.")
    L.append("> 또한 부분청산 행 중복을 진입 1건 단위로 병합한다 — 그대로 세면 TP1/TP2")
    L.append("> 부분청산이 각각 '승리'로 집계돼 승률이 부풀려진다(402차 실제 오류 사례).")
    L.append("")

    # [22] MFE 캡처율 상세
    L.append("## [22] MFE 캡처율 관찰 (402차 후속5, 관찰 전용 — 판정 없음)")
    L.append("")
    if mcw.get("error"):
        L.append("> ⚠ %s" % mcw["error"])
    else:
        L.append("- 필터: `entry_source='%s'` — 진입 %s건(원본 %s행 병합)"
                  % (mcw.get("entry_source_filter", "?"),
                     mcw.get("n_entries", 0), mcw.get("n_rows_raw", 0)))
        L.append("- 평균 실현 %s pt / 보유구간 MFE %s pt / 15:10까지 MFE %s pt" % (
            mcw.get("avg_realized_pt", "—"), mcw.get("avg_mfe_hold_pt", "—"),
            mcw.get("avg_mfe_close_pt", "—")))
        L.append("- **풀링 캡처율**(ΣRealized/ΣMFE) 보유구간 %s (n=%s) / 15:10까지 %s (n=%s)" % (
            ("%.1f%%" % (mcw["capture_in_hold_pooled"] * 100)) if mcw.get("capture_in_hold_pooled") is not None else "—",
            mcw.get("n_hold", 0),
            ("%.1f%%" % (mcw["capture_to_close_pooled"] * 100)) if mcw.get("capture_to_close_pooled") is not None else "—",
            mcw.get("n_close", 0)))
        L.append("- **승리 거래만** 15:10까지 풀링 캡처율 %s (n=%s)" % (
            ("%.1f%%" % (mcw["capture_to_close_pooled_winners"] * 100))
            if mcw.get("capture_to_close_pooled_winners") is not None else "—",
            mcw.get("n_winners", 0)))
        L.append("- **평균 미실현 잔여**(MFE−실현) 보유구간 %s pt / 15:10까지 %s pt" % (
            mcw.get("avg_left_in_hold_pt", "—"), mcw.get("avg_left_to_close_pt", "—")))
        if mcw.get("most_left5"):
            L.append("")
            L.append("가장 많이 흘린 5건 (15:10 MFE − 실현):")
            L.append("")
            L.append("| 진입 | 방향 | 실현pt | 보유MFE | 15:10MFE | 잔여pt |")
            L.append("|---|---|---|---|---|---|")
            for s in mcw["most_left5"]:
                L.append("| %s | %s | %s | %s | %s | %.2f |" % (
                    s["ts"], s["dir"], s["realized_pt"],
                    s["mfe_hold_pt"] if s["mfe_hold_pt"] is not None else "—",
                    s["mfe_close_pt"] if s["mfe_close_pt"] is not None else "—",
                    s["mfe_close_pt"] - s["realized_pt"]))
        if mcw.get("reason"):
            L.append("")
            L.append("- %s" % mcw["reason"])
    L.append("")
    L.append("> 이 채널은 **판정하지 않는다**(verdict 항상 OBSERVE). 여기서 나올 결정")
    L.append("> (\"청산을 더 늦춰라\")은 이미 [12] tp1_trail_shadow가 판정 중이므로, 이")
    L.append("> 수치는 그 판정을 해석할 맥락(\"캡처율이 이렇게 낮은데도 트레일링이 안")
    L.append("> 낫다\"가 성립하는지)만 제공한다. 단일일 극단 사례로 결론 내지 말 것")
    L.append("> (2026-07-29 캡처율 7.7%는 -15.6% 폭락일 1건이다 — 313차 원칙).")
    L.append("")

    # [23] EOD 모델가드 판정 괴리 상세
    L.append("## [23] EOD 모델가드 판정 괴리 감시 (404차 신설)")
    L.append("")
    if gsc.get("error"):
        L.append("> ⚠ %s" % gsc["error"])
    elif gsc.get("reason"):
        L.append("- %s" % gsc["reason"])
    else:
        L.append("- 표본 %s건 / %s거래일 (재측정 실패 %s건 별도 제외)" % (
            gsc.get("n_samples", 0), gsc.get("n_days", 0),
            gsc.get("n_live_measure_failed", 0)))
        L.append("- **missed_upgrade_rate** (공정비교=REPLACE인데 acc.txt 기준=HOLD였던 비율): "
                  "**%s** (n=%s/%s)" % (
                      ("%.1f%%" % (gsc["missed_upgrade_rate"] * 100))
                      if gsc.get("missed_upgrade_rate") is not None else "—",
                      gsc.get("missed_upgrade_n", "—"), gsc.get("n_fair", "—")))
        if gsc.get("mean_distortion") is not None:
            L.append("- 평균 왜곡(acc.txt − 동일폴드 재측정) = %+.4f" % gsc["mean_distortion"])
        if gsc.get("by_horizon"):
            L.append("")
            L.append("| 호라이즌 | n | missed_upgrade |")
            L.append("|---|---|---|")
            for hz, v in sorted(gsc["by_horizon"].items()):
                L.append("| %s | %d | %d |" % (hz, v["n"], v["missed"]))
    L.append("")
    L.append("> **판정 기준**(관측 전 고정, §9): missed_upgrade_rate ≥ %.0f%% → FAIL"
              "(판정기준을 old_acc_live로 교체할지 주간회의 검토), 미만 → PASS(acc.txt 유지)."
              % (VALIDATION_CAMPAIGN["guard_shadow"]["missed_upgrade_rate_max"] * 100))
    L.append("> 07-31 최초 라이브 관측(6개 호라이즌 중 3개 불일치)이 이 채널을 만든 계기이나,")
    L.append("> 임계값은 그 단일일 관측치에 맞추지 않고 독립적으로 고정했다 — 이 리포트가")
    L.append("> 그 계기가 된 날의 데이터를 포함하더라도 임계값 자체는 사후 조정이 아니다.")
    L.append("> (근거: `dev_memory/DECISION_LOG.md` 404차 항목, 313차·§9 원칙)")
    L.append("")

    # [23-부속] intraday 계측 CV 관찰 (판정 없음)
    L.append("### [23-부속] intraday 계측 CV 관찰 (404차 후속, 관찰 전용 — 판정 없음)")
    L.append("")
    if icw.get("error"):
        L.append("> ⚠ %s" % icw["error"])
    elif icw.get("reason"):
        L.append("- %s" % icw["reason"])
    elif icw.get("by_horizon"):
        L.append("- 표본 %s건 / %s거래일" % (icw.get("n_samples", 0), icw.get("n_days", 0)))
        L.append("")
        L.append("| 호라이즌 | n | 평균 cv_acc | σ(cv_acc) | 평균 왜곡 | fair_would_hold |")
        L.append("|---|---|---|---|---|---|")
        for hz, v in sorted(icw["by_horizon"].items()):
            L.append("| %s | %d | %.4f | %s | %s | %s |" % (
                hz, v["n"], v["mean_cv"],
                ("%.4f" % v["std_cv"]) if v["std_cv"] is not None else "—",
                ("%+.4f" % v["mean_distortion"]) if v["mean_distortion"] is not None else "—",
                ("%.0f%%" % (v["fair_would_hold_rate"] * 100))))
    L.append("")
    L.append("> **판정하지 않는다**(verdict 항상 OBSERVE). 실측(404차 후속 §1): 동일 데이터·")
    L.append("> 시드만 다른 재현 분산이 5m 기준 8.83%p로 EOD 가드 허용폭(2.5%p)의 3.5배 —")
    L.append("> 이 표의 σ(cv_acc)가 크게 나오는 것은 결함이 아니라 그 잡음이 실측되는 것이다.")
    L.append("> `fair_would_hold`가 높다고 즉시 intraday 가드를 도입하지 말 것 — 표본이")
    L.append("> 충분히(수 주) 쌓여 잡음이 아닌 추세인지 확인한 뒤 사람이 판단한다(§9).")
    L.append("")

    # [23-B] TP1/손절 초기 기하 A/B 상세 (403차 P1-6 — 404차 후속3에서 리포트 편입)
    L.append("## [23-B] TP1/손절 초기 기하 A/B (403차 P1-6, 404차 후속3 리포트 편입)")
    L.append("")
    if _g23.get("error"):
        L.append("> ⚠ 스크립트 실행 실패: %s" % _g23["error"])
    else:
        L.append("- 진입 %s건 (ATR 결측 제외 %s건) / 거래일 %s일"
                  % (_g23.get("n_trades", "—"), _g23.get("n_skipped", "—"),
                     _g23.get("n_days", "—")))
        pv = _g23.get("per_variant") or {}
        if pv:
            L.append("")
            L.append("| 변형 | n | TP1 | STOP | 승률 | 누적pt | 현행 대비 |")
            L.append("|---|---|---|---|---|---|---|")
            for k, v in pv.items():
                L.append("| %s | %d | %d | %d | %.1f%% | %+.2f | %s |" % (
                    k, v["n"], v["n_tp1"], v["n_stop"], v["win_rate"] * 100,
                    v["total_pt"],
                    ("%+.2f" % v["delta_vs_current"]) if v["delta_vs_current"] is not None else "—"))
        L.append("")
        L.append("- **판정: %s** — %s" % (_g23.get("verdict"), _g23.get("reason")))
        # [MW0601 405차 / P1-4] OOS 부분집계 — 표시 전용, 판정 미반영
        _oos = _g23.get("oos") or {}
        if _oos:
            L.append("")
            L.append("### [23-B-OOS] 가설 수립 이후 신규분만 (%s~) — **판정 미반영**"
                     % _oos.get("oos_start", "—"))
            L.append("")
            _opv = _oos.get("per_variant") or {}
            if not _opv:
                L.append("- %s" % _oos.get("note", "표본 없음"))
            else:
                L.append("| 변형 | n | 승률 | 누적pt | 현행 대비 |")
                L.append("|---|---|---|---|---|")
                for k, v in _opv.items():
                    L.append("| %s | %d | %.1f%% | %+.2f | %s |" % (
                        k, v["n"], v["win_rate"] * 100, v["total_pt"],
                        ("%+.2f" % v["delta_vs_current"])
                        if v.get("delta_vs_current") is not None else "—"))
                L.append("")
                L.append("> %s" % _oos.get("note", ""))
                L.append("> 누적 표(위)는 **가설을 세운 그 기간을 포함**한다(403차 P1-6이 55건/11일로")
                L.append("> 처음 실행하며 이 대안들을 정의했다). 이 절은 그 이후 신규분만 세어 같은")
                L.append("> 방향이 유지되는지를 본다 — 표본이 쌓이기 전에는 해석하지 말 것(313차).")
    L.append("")
    L.append("> 종전에는 `scripts/tp1_geometry_shadow.py`를 따로 실행해야만 보여 주간회의에")
    L.append("> 노출되지 않았다(403차 신설 이후). 404차 후속3에서 계산부를 `compute()`/")
    L.append("> `summarize()`로 추출해 이 리포트가 직접 호출한다 — 판정 기준·로직 무변경.")
    L.append("> ⚠ `current`의 절대값은 실현손익이 아니다(qty=1 보호전환을 'TP1 전량청산'으로")
    L.append("> 단순화). **변형 간 상대비교 전용.**")
    L.append("> ⚠ 이 채널은 MW0601에서 `tp1_x2` **+32.78pt**(현행 초과=FAIL 방향)가 나왔으나")
    L.append("> MW0602에서는 **−19.04pt**(PASS 방향)로 **부호가 뒤집힌다.** 두 PC의 거래집합이")
    L.append("> 달라서이며(protect mode 무관 — 이 시뮬은 protect mode를 쓰지 않는다), n≈60·12일")
    L.append("> 로는 기하를 결정할 수 없다는 뜻이다(313차).")
    L.append("")

    # [24] TP1 보호전환 반납 관찰
    L.append("## [24] TP1 보호전환 반납 관찰 (404차 후속3, 관찰 전용 — 판정 없음)")
    L.append("")
    if tpg.get("error"):
        L.append("> ⚠ %s" % tpg["error"])
    elif tpg.get("reason"):
        L.append("- %s" % tpg["reason"])
    else:
        L.append("- 보호전환 %s건 / %s거래일 (모드 분포: %s)"
                  % (tpg.get("n", 0), tpg.get("n_days", 0),
                     ", ".join("%s=%d" % kv for kv in (tpg.get("by_mode") or {}).items()) or "—"))
        L.append("- **반납 %s건 / 더 달림 %s건**"
                  % (tpg.get("n_gaveback", "—"), tpg.get("n_ranfurther", "—")))
        L.append("- TP1 장부이익 평균 %s pt / 중앙값 %s pt   |   평균 보호폭 %s pt"
                  % (tpg.get("mean_paper_pt", "—"), tpg.get("median_paper_pt", "—"),
                     tpg.get("mean_offset_pt", "—")))
        L.append("- **반납 중앙값 %s pt** (평균 %s pt) → 중앙값 기준 반납률 %s"
                  % (tpg.get("median_give_pt", "—"), tpg.get("mean_give_pt", "—"),
                     ("%.0f%%" % (tpg["median_giveback_rate"] * 100))
                     if tpg.get("median_giveback_rate") is not None else "—"))
        if tpg.get("offset_vs_give_corr") is not None:
            L.append("- 보호폭 vs 반납 상관계수 **%.3f** (음수 = 좁은 보호폭일수록 더 반납)"
                      % tpg["offset_vs_give_corr"])
        # [MW0601 406차 / D] 모드별 분리표 — 위 풀링 수치는 하위호환용이며,
        # 모드가 섞이면 해석 근거로 쓸 수 없다.
        _bms = tpg.get("by_mode_stats") or {}
        if _bms:
            L.append("")
            L.append("**모드별 분리** (보호스톱 기준선이 모드마다 달라 섞어 읽으면 안 된다):")
            L.append("")
            L.append("| 모드 | n | 거래일 | 반납/달림 | 반납 중앙값 | 반납 평균 | 평균 보호폭 | 보호폭↔반납 상관 |")
            L.append("|---|---|---|---|---|---|---|---|")
            for _m, _s in _bms.items():
                L.append("| `%s` | %s | %s | %s / %s | **%s** pt | %s pt | %s pt | %s |" % (
                    _m, _s.get("n", 0), _s.get("n_days", 0),
                    _s.get("n_gaveback", "—"), _s.get("n_ranfurther", "—"),
                    _s.get("median_give_pt", "—"), _s.get("mean_give_pt", "—"),
                    _s.get("mean_offset_pt", "—"),
                    ("%.3f" % _s["offset_vs_give_corr"])
                    if _s.get("offset_vs_give_corr") is not None else "—"))
            if tpg.get("modes_mixed"):
                L.append("")
                L.append("> ⚠ **모드가 혼재한다 — 위 풀링 수치를 인용하지 말 것.** 모드별 행만 쓸 것.")
    L.append("")
    L.append("> **판정하지 않는다**(verdict 항상 OBSERVE). 처방(offset을 얼마로 할지)은 [25]가 맡는다.")
    L.append("> [MW0601 406차] **모드 라벨 없이 이 수치를 인용하지 말 것** — 보호스톱을 거는")
    L.append("> 자리가 모드마다 다르므로(breakeven=진입가 / atr_profit=ATR×0.25) \"반납\"의")
    L.append("> 기준선 자체가 다르다. 0802 PC간 대조에서 중앙값 반납이 breakeven −0.1pt vs")
    L.append("> atr_profit +1.0pt로 **부호가 반대**였다 — 섞으면 결론이 상쇄된다.")
    L.append("> **평균이 아니라 중앙값을 볼 것** — 0729 폭락일 2건이 평균을 5배 끌어올려")
    L.append("> 평균 반납은 무해해 보이는데 중앙값은 그 몇 배다. 두 수치가 정반대 인상을")
    L.append("> 주는 전형적 사례이므로 평균만 인용하지 말 것(372차 원칙).")
    L.append("> 소스(`synthetic_partial_exits`)는 339차부터 쌓였으나 404차 후속3까지 **캠페인")
    L.append("> 소비처가 없어 방치**돼 있었다 — 402차 후속3 `toxicity_block_shadow`와 같은 계열.")
    L.append("")

    # [26] 거래불능(가격상한 고착) 구간
    L.append("## [26] 거래불능(가격상한 고착) 구간 (404차 후속5, 관찰 전용 — 판정 없음)")
    L.append("")
    if lpw.get("error"):
        L.append("> ⚠ %s" % lpw["error"])
    elif lpw.get("reason"):
        L.append("- %s" % lpw["reason"])
    else:
        L.append("- 고착 **%s분봉** / %s일 (세션 분봉 %s개 중)"
                 % (lpw.get("n_pinned_bars", 0), lpw.get("n_days", 0),
                    lpw.get("n_session_bars", 0)))
        L.append("")
        L.append("| 일자 | 방향 | 가격 | 고착분봉 | 구간 | 결측분봉 | 극단 유동터치 | 최대 유동vol |")
        L.append("|---|---|---|---|---|---|---|---|")
        for d in lpw.get("days", []):
            L.append("| %s | %s | %s | %d | %s~%s | %d | **%d** | %d |" % (
                d["date"], d["side"], d["price"], d["n_bars"], d["from"], d["to"],
                d["n_missing_bars"], d["extreme_liquid_touches"], d["max_liquid_vol"]))
    L.append("")
    L.append("> **핵심 열은 '극단 유동터치'다.** 이 값이 0보다 크면 그 극단을 유동 분봉이")
    L.append("> 이미 만들었다는 뜻이고, 고착 분봉을 전부 지워도 **MFE는 변하지 않는다**")
    L.append("> (max 연산이라 중복 무해). 0731 리포트 §1-C 이상점 3이 제기한 \"MFE·캡처율")
    L.append("> 오염\" 가설은 이 지표로 **기각**된다 — 07-31 고착 29분봉이 있었지만 1036.28을")
    L.append("> 유동 분봉 13개(최대 vol 642)가 이미 터치했고, 리포트 전문 before/after diff에서")
    L.append("> 실제로 단 한 글자도 바뀌지 않았다.")
    L.append(">")
    L.append("> 이 값이 **0인 날이 나오면 그때는 진짜 오염**이다(갭 상한가 직행 등).")
    L.append("> 진짜 오염은 목표가 쪽이며 [27]이 계측한다.")
    L.append("")

    # [27] counterfactual 도달불가 목표가
    L.append("## [27] counterfactual 도달불가 목표가 (404차 후속5, 관찰 전용 — 판정 없음)")
    L.append("")
    if ucw.get("error"):
        L.append("> ⚠ %s" % ucw["error"])
    elif ucw.get("reason"):
        L.append("- %s" % ucw["reason"])
    else:
        L.append("- 해당 행 **%s건** (%s) · 합계 %s pt"
                 % (ucw.get("n_unreachable", 0),
                    ", ".join("%s=%d" % kv for kv in (ucw.get("by_table") or {}).items()) or "—",
                    ucw.get("excluded_hyp_pnl_pts", "—")))
        L.append("")
        L.append("| 테이블 | 시각 | 방향 | 진입가 | 목표가 | 그날 상한 | 결과 | hyp pnl |")
        L.append("|---|---|---|---|---|---|---|---|")
        for h in ucw.get("rows", [])[:12]:
            L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                h["table"], str(h["ts"])[11:16], h["dir"], h["entry"], h["tp1"],
                h["limit"], h["cf_outcome"], h["hyp_pnl_pts"]))
        L.append("")
        L.append("**민감도 — 이 행들을 뺐다면 (참고용, 실제 판정에는 미반영):**")
        L.append("")
        L.append("| 채널 | n | 제외 | 현행 누적 hyp | 제외 시 | 차이 |")
        L.append("|---|---|---|---|---|---|")
        for t, v in sorted((ucw.get("sensitivity") or {}).items()):
            L.append("| %s | %d | %d | %s | %s | %+.4f |" % (
                t, v["n"], v["n_excluded"], v["total_hyp_pnl_pts"],
                v["total_if_excluded"], v["delta"]))
    L.append("")
    L.append("> **이 채널은 판정을 바꾸지 않는다.** 초안에서는 \"이길 수 없는 가상거래\"로 보고")
    L.append("> 자동 제외하도록 짰다가 되돌렸다 — 전제가 틀렸다. 07-31 14:17 시장은 유동적이었고")
    L.append("> (vol 109) 실제로 진입했다면 체결됐을 것이며, TP1이 상한 밖이라 정말로 스톱만")
    L.append("> 맞았을 것이다. counterfactual은 모델링 결함이 아니라 **나쁜 거래를 충실히")
    L.append("> 시뮬레이션**한 것이고, 게이트의 손실 회피는 진짜다.")
    L.append(">")
    L.append("> 남는 질문은 측정 오류가 아니라 **공로의 출처**다 — 게이트가 자기 로직으로 막은")
    L.append("> 것인지, 신호가 우연히 가격상한에서 나와 구조적으로 질 수밖에 없었던 것인지.")
    L.append("> \"옳았지만 이유는 달랐다\"는 해석 문제라 판정을 조용히 바꾸지 않고 민감도만")
    L.append("> 병기해 주간회의에 올린다(§9).")
    L.append(">")
    L.append("> ⚠ **[18] RegimeExhaustionGate는 3건에 판정이 뒤집힌다**(SUPPORTS→REJECTS,")
    L.append("> 누적 hyp −1.75 → +6.85). 표본 3건이 권고를 뒤집는다는 사실 자체가 그 채널")
    L.append("> 결론의 근거가 얼마나 얇은지를 보여준다(372차 이상치 분해와 같은 교훈).")
    L.append("")

    # [25] TP1 보호전환 offset A/B
    L.append("## [25] TP1 보호전환 offset A/B (404차 후속3 신설)")
    L.append("")
    if _g25.get("error"):
        L.append("> ⚠ 스크립트 실행 실패: %s" % _g25["error"])
    else:
        L.append("- 보호전환 %s건 (제외 %s건) / 거래일 %s일"
                  % (_g25.get("n_hooks", "—"), _g25.get("n_skipped", "—"),
                     _g25.get("n_days", "—")))
        if _g25.get("engine"):
            L.append("- 재생기 엔진: **%s** (443차 이관 — `sim_fidelity_gate[\"engine\"]` 공유)"
                     % _g25["engine"])
        if _g25.get("n_qty_gt1") or _g25.get("n_no_arm"):
            L.append("- v2 전용 제외: 원 진입수량≠1 **%s건**(잔여 1계약 arm — 모집단이 다르다) "
                     "/ 재생기 arm 미도달 **%s건**"
                     % (_g25.get("n_qty_gt1", 0), _g25.get("n_no_arm", 0)))
        pv = _g25.get("per_variant") or {}
        if pv:
            L.append("")
            L.append("| 변형 | n | 승률 | 누적pt | 중앙값 | 현행 대비 | 건별 우세 | 결말 분포 |")
            L.append("|---|---|---|---|---|---|---|---|")
            for k, v in pv.items():
                _oc = v.get("outcomes") or {}
                _oc_txt = (" · ".join("%s %d" % (o, c) for o, c in _oc.items())
                           if _oc else "STOP %d / TP2 %d" % (v["n_stop"], v["n_tp2"]))
                L.append("| %s | %d | %.1f%% | %+.2f | %+.3f | %s | %s | %s |" % (
                    k, v["n"], v["win_rate"] * 100,
                    v["total_pt"], v["median_pt"],
                    ("%+.2f" % v["delta_vs_current"]) if v["delta_vs_current"] is not None else "—",
                    ("%s/%d" % (v["beats_current_n"], v["n"])) if v.get("beats_current_n") is not None else "—",
                    _oc_txt))
        L.append("")
        L.append("- **판정: %s** — %s" % (_g25.get("verdict"), _g25.get("reason")))
    L.append("")
    L.append("> ⚠ **사전등록 정직성 고지**: `breakeven` 변형은 이 채널 신설 **전에** 404차")
    L.append("> 후속3 조사에서 이미 1회 측정됐다(현행이 22/23 우세) — 재확인용이지 사전등록된")
    L.append("> 검증이 아니다. 사전등록 가치는 `atr_lock_0.50/0.75`·`bar_range`에 있다.")
    # ── [MW0601 440차] §25-C 호라이즌 비례 lock 축 신설 고지 ──────────────────
    _lp = [v for v in (_g25.get("per_variant") or {}) if str(v).startswith("lock_prop_")]
    if _lp:
        L.append("> ")
        L.append("> 🆕 **[MW0601 440차] §25-C 호라이즌 비례 lock 3변형 사전등록** — `%s`."
                 % "`, `".join(sorted(_lp)))
        L.append("> offset = **TP1거리 × k** (현행은 ATR×0.25 **고정**). 계기: TP1은 374/387차에")
        L.append("> 호라이즌별로 분화됐는데(`1m .3 / 3m .5 / 5m .7`) lock만 339차 상수라,")
        L.append("> \"TP1 이익 중 얼마를 확보하는가\"가 호라이즌에 **반비례**한다 —")
        L.append("> **1m 83% / 3m 50% / 5m 36%** ([49]가 실측으로 같은 것을 지적).")
        L.append("> 설계 의도라는 근거가 없고 두 축을 각각 고친 **부작용**으로 보인다.")
        L.append("> ")
        L.append("> ⚠ **관측 전 확정된 그리드다** — 0.35(느슨)·0.50·0.75(타이트) 양방향으로")
        L.append("> 넣어 **단조성**을 본다. 단조가 아니면 특정 값의 표본 우연이다.")
        L.append("> ⚠ 이 변형은 `entry_horizon`이 필요해 `trades` 조인에 실패한 행이 빠진다 —")
        L.append("> 그래서 `현행 대비`는 **짝지은 부분집합**으로 계산한다(기존 변형은 전건")
        L.append("> 일치라 종전 값과 동일). 각 행의 누락 건수는 위 표의 n으로 확인할 것.")
        L.append("> ⚠ **라이브는 무변경이다** — `TP1_PROTECT_ATR_LOCK_MULT`(0.25) 그대로다.")
    # [MW0602 432차] 이 자리에 있던 0801 경고문("최대 기여 1건만 빼면 부호 역전,
    # 건별 우세 8/23·7/23")은 **더 이상 참이 아니다** — 08-05 기준 표본 49건/11일에서
    # drop-max +16.50 유지, LOO일 최악 +10.00, 건별 우세 28/49로 전부 소멸했다.
    # 그 경고문을 그대로 두면 리포트가 매주 거짓을 찍는다. 새 제동으로 교체한다.
    L.append("> ⚠ **FAIL이 떠도 즉시 적용 금지** — 단, **이유가 2026-08-05에 바뀌었다.**")
    L.append("> 0801의 제동(drop-max 부호역전·건별 우세 소수)은 표본이 23건/8일 →")
    L.append("> 49건/11일로 늘며 **전부 소멸했다**(drop-max +16.50 유지, 우세 28/49).")
    L.append("> 지금의 제동은 두 가지다 — ① **일자단위 t검정 p=0.255로 미유의**(313차),")
    L.append("> ② 판독규칙 (3): MW0601 표본이 아직 08-03 시작분뿐이라 단독 확정 불가.")
    L.append("> ⚠ **[432차] 2026-08-05 이전의 이 채널 수치는 전부 무효다** — offset이")
    L.append("> 보호전환 시점의 실제 유리이동을 넘어도 체결로 계상되던 결함이 있었다")
    # ⚠ 이 줄에는 `%` 연산자를 적용하지 않는다 → 리터럴 퍼센트는 `%` 하나로 쓴다.
    #   (422차 후속의 `%%` 규칙은 `%` 포매팅을 **쓰는** 줄에만 해당한다. 431차 후속2가
    #    그 반대 방향으로 터진 사고다 — 포매팅 유무를 매번 확인할 것.)
    L.append("> (atr_lock_0.75는 **57%가 체결 불가**). 클램프 후 Δ현행 +18.75 → **+8.04pt**.")
    L.append("> 이 채널에서 **일자단위로 유의한 것은 `breakeven`(p=0.021) 하나뿐이고**")
    L.append("> **방향은 음(−9.23pt)** 이다 — 즉 '본전 보호는 현행보다 나쁘다'만 확립됐다.")
    L.append("> ⚠ [12] tp1_trail_shadow가 기각한 \"TP1 **이후** 트레일 폭\"과 다른 질문이다")
    L.append("> — 이건 TP1 **시점**의 초기 보호 offset이다.")
    L.append("> ⚠ **TP2 거리 축은 아래 [25-B]에 따로 있다** — 위 표의 변형들은 전부 TP2를")
    L.append("> 현행(ATR×1.5)으로 고정한 상태에서 보호 offset만 바꾼 것이다.")
    # [MW0601 421차 후속2] PC 출처 + 두 PC 불일치 판독 규칙 — 사전등록분을 그대로 노출한다.
    # 0803 점검에서 위 "8/23·7/23"의 PC 출처가 없어 "MW0601 breakeven 표본이라 406차로
    # 무효화됐다"는 오독이 실제로 발생했다. 그 재발을 막는 것이 목적이다.
    _c25 = VALIDATION_CAMPAIGN.get("tp1_protect_offset_shadow", {}) or {}
    # [432차] 예전에는 "위 8/23·7/23은 MW0602 표본"이라 적었는데, 그 숫자를 담던
    # 경고문을 교체하면서 **가리킬 대상이 사라졌다**. 자체 완결형으로 바꾼다.
    L.append("> ⚠ **위 표는 MW0602 표본**이다(404차 후속3). MW0601은 당시")
    L.append("> `breakeven`이라 유효표본 0이었고, 406차 통일로 **MW0601 표본은 %s부터**"
             % _c25.get("mw0601_sample_start", "—"))
    L.append("> 시작한다. 406차는 0801 결정을 무효화하지 않는다 — MW0601 독립 확인이")
    L.append("> 아직 없을 뿐이다. \"모드 불일치 제외 N건\"은 406차 투명성 기능이며 결함이 아니다.")
    L.append(">")
    L.append("> **두 PC 불일치 판독 규칙(사전등록, 관측 전 확정)**: (1) 같은 방향 + 둘 다")
    L.append("> drop-max 생존 → 승격 후보. (2) **부호 반대 → 기각 아닌 보류**, 두 값을 항상")
    L.append("> 병기(유리한 쪽만 인용 금지). (3) 한쪽만 표본 충족 → 단독 판정을 확정으로")
    L.append("> 쓰지 않고 \"단일 PC 표본\" 명시. (4) 어느 경우도 자동 적용 없음(§9).")
    L.append("> 근거: [23] tp1_geometry_shadow에서 이미 PC간 부호 역전 전례가 있다.")
    L.append("")

    # [25-B] TP2 거리 A/B (MW0601 432차 신설)
    L.append("## [25-B] TP2 거리 A/B (MW0601 432차 신설)")
    L.append("")
    if not _g25b:
        L.append("> ⚠ 미산출 — `tp2_variants` 미설정이거나 [25] 스크립트 실행 실패.")
    else:
        if not _g25b.get("baseline_consistent", True):
            L.append("> 🔴 %s" % (_g25b.get("baseline_note") or "배선 검산 실패"))
            L.append("")
        L.append("- 보호전환 %s건 / 거래일 %s일 · 보호 offset은 현행(ATR×0.25) **고정**, "
                 "TP2만 변형" % (_g25b.get("n_hooks", "—"), _g25b.get("n_days", "—")))
        pv2 = _g25b.get("per_variant") or {}
        if pv2:
            L.append("")
            L.append("| 변형 | n | TP2완주 | 승률 | 누적pt | 중앙값 | 최대손실 | 표준편차 | 현행 대비 | 건별 우세 | drop-max |")
            L.append("|---|---|---|---|---|---|---|---|---|---|---|")
            for k, v in pv2.items():
                L.append("| %s | %d | %d | %.1f%% | %+.2f | %+.3f | %+.2f | %.2f | %s | %s | %s |" % (
                    k, v["n"], v["n_tp2"], v["win_rate"] * 100,
                    v["total_pt"], v["median_pt"], v["max_loss_pt"], v["std_pt"],
                    ("%+.2f" % v["delta_vs_current"]) if v.get("delta_vs_current") is not None else "—",
                    ("%s/%d" % (v["beats_current_n"], v["n"])) if v.get("beats_current_n") is not None else "—",
                    ("%+.2f" % v["delta_drop_max"]) if v.get("delta_drop_max") is not None else "—"))
        L.append("")
        L.append("- **판정: %s** — %s" % (_g25b.get("verdict"), _g25b.get("reason")))
    L.append("")
    L.append("> **왜 [23]이 아니라 여기인가**: [23]의 시뮬레이터는 TP1 도달 시 전량청산으로")
    L.append("> 종료해 TP2가 등장하지 않는다. 반면 이 채널은 이미 `보호스톱 vs TP2`를 재생한다.")
    L.append("> 더 중요한 건 **조건부 추정이 정확히 valid**하다는 점 — TP2를 바꿔도 stop·TP1은")
    L.append("> 불변이라 \"TP1 도달 사건 집합\"이 전 변형에서 동일하다. TP1 도달 건만 보는 것은")
    L.append("> 선택편향이 아니라 교란이 제거된 설계다.")
    L.append(">")
    L.append("> ⚠ **TP2 단축은 완주율↑ / 완주 1건당 이익↓의 교환이다.** 누적pt만 보고 판단하지")
    L.append("> 말 것 — `TP2완주` 건수와 `중앙값`·`표준편차`가 함께 움직이는지 확인해야 한다.")
    L.append("> ⚠ `tp2_2.00`은 **대조군**(넓히는 방향)이다. 결과가 거리에 대해 단조라면 진짜")
    L.append("> 거리 효과이고, 특정 값에서만 튀면 표본 우연이다 — 단조성을 먼저 볼 것.")
    L.append("> ⚠ **FAIL이 떠도 즉시 적용 금지**(§9). 사전등록 판정보조 ①drop-max ②건별우세")
    L.append("> ③MW0601×MW0602 교차를 전부 통과해야 주간회의 승격 후보다. [25] 본채널이")
    L.append("> 바로 ①에서 무너진 전례가 있다(atr_lock_0.75 +0.92→−1.33pt).")
    L.append("> ⚠ 이 판정은 [25] 본채널(offset 축) 판정과 **무관**하다 — 본채널 합격선 무변경(§9-4).")
    L.append("")

    # ── [MW0602 435차] [47]/[48]/[49] 상세 ────────────────────────────────────
    L.append("## [47] 시뮬레이터 재현충실도 게이트 (435차 신설 · 메타 채널)")
    L.append("")
    _gate = off.get("_sim_fidelity_gate") or {}
    L.append("- 판정: **%s** — %s" % (_fmt_verdict(_gate.get("verdict", "")),
                                     _gate.get("reason", "—")))
    if _gate.get("repro_bias_R") is not None:
        L.append("- 재현 편향(중앙) **%+.3fR** / 평균 %+.3fR · 총합 시뮬 %+.2f pt vs 실제 %+.2f pt · 부호일치=%s"
                 % (_gate["repro_bias_R"], _gate.get("repro_bias_R_mean", 0),
                    _gate.get("sim_total_pt", 0), _gate.get("actual_total_pt", 0),
                    _gate.get("sign_match")))
    # ── [MW0601 441차] 4기준 판정 내역 — 어느 기준으로 통과/탈락했는지 감사 가능하게 ──
    if _gate.get("repro_gap_sd") is not None:
        _cr47 = VALIDATION_CAMPAIGN.get("sim_fidelity_gate", {}) or {}
        L.append("- 판정 기준별 (441차 4기준 AND):")
        L.append("  - ① 편향(중앙) `%+.3fR` ≤ `%.2fR`" % (
            _gate.get("repro_bias_R", 0), _cr47.get("repro_bias_R_max", 0.10)))
        L.append("  - ② **수준 — 재현 격차 `%.2f SE` ≤ `%.1f SE`** (격차 %.2f pt) ← 실질 판별자"
                 % (_gate["repro_gap_sd"], _cr47.get("repro_gap_sd_max", 1.0),
                    _gate.get("repro_gap_pt", 0)))
        L.append("  - ③ 일자단위 추적 — 상관 `%s` ≥ `%.2f` · 부호일치 `%s` ≥ `%.0f%%` (%s일)"
                 % (("%+.3f" % _gate["day_corr"]) if _gate.get("day_corr") is not None else "—",
                    _cr47.get("day_corr_min", 0.60),
                    ("%.0f%%" % (100 * _gate["day_sign_agree"]))
                    if _gate.get("day_sign_agree") is not None else "—",
                    100 * _cr47.get("day_sign_agree_min", 0.70),
                    _gate.get("n_day_points", "—")))
        L.append("  - ④ 부호검정 — 구속력 **%s** (|Σ실제|=%.2f SE, 기준 %.1f SE)"
                 % ("있음" if _gate.get("sign_binding") else "없음(무정보 → ②가 대체)",
                    _gate.get("sign_margin_sd") or 0.0,
                    _cr47.get("sign_match_min_sd", 2.0)))
        if _gate.get("verdict_strict_sign"):
            _same = _gate["verdict_strict_sign"] == _gate.get("verdict")
            L.append("- 구 기준(sign_match 무조건) 판정: **%s** — %s"
                     % (_gate["verdict_strict_sign"],
                        "현행과 동일(조건부 경로가 판정을 바꾸지 않았다)" if _same
                        else "⚠ **현행과 다르다** — 조건부 경로가 판정을 바꿨다. §9 감사 대상."))
    if _gate.get("sim_total_pt_legacy") is not None:
        L.append("- 참고 — 440차까지의 구 판정식 입력: 시뮬 %+.2f vs 실제 %+.2f pt "
                 "(레그 무가중합 vs 비용차감 시뮬). **441차가 단위를 통일**해 "
                 "양변을 `gross·1계약`으로 맞췄다 — 수치가 달라진 이유다."
                 % (_gate["sim_total_pt_legacy"], _gate["actual_total_pt_legacy"]))
    if _gate.get("engine"):
        L.append("- 재생기 엔진: **%s** (`config/settings.py sim_fidelity_gate[\"engine\"]`)"
                 % _gate["engine"])
    # ── [MW0601 447차] replay_regime 적합성 자동 점검 ──────────────────────────
    try:
        _rf = check_replay_regime_fit()
    except Exception as _e:
        _rf = {"error": "%s: %s" % (type(_e).__name__, _e)}
    if _rf.get("error"):
        L.append("- 체제 경계 점검: ⚠ 미산출 (%s)" % _rf["error"])
    else:
        _fmt_d = (lambda d: ", ".join("%s %d" % kv for kv in sorted(d.items())) or "없음")
        L.append("- **체제 경계 적합성** (`tick_era_start=%s`): %s"
                 % (_rf["tick_era_start"], "✅ 이 PC 실측과 일치" if _rf.get("ok")
                    else "🔴 **이 PC 실측과 불일치**"))
        L.append("  - pre 실측 `%s` vs config `%s` / post 실측 `%s` vs config `%s`"
                 % (_fmt_d(_rf.get("obs_pre") or {}), _rf.get("cfg_pre"),
                    _fmt_d(_rf.get("obs_post") or {}), _rf.get("cfg_post")))
        if not _rf.get("ok"):
            L.append("  - 🔴 **이 PC의 재생 체제가 틀렸을 수 있다** — `replay_regime`은 "
                     "**MW0601 TRADE 로그로 캘리브레이션**된 단일 값이라 두 PC가 공유한다. "
                     "MW0602 0808 교차검토가 실측으로 `tick_era_start` **07-31**(vs 08-03)·"
                     "`pre.protect_mode` **atr_profit**(vs breakeven)을 재도출했다. "
                     "**A/B 채널 수치를 PC간 비교하기 전에 이 불일치부터 해소할 것.**")
            L.append("  - ⚠ **경계를 임의로 옮기지 말 것** — settings가 \"재현이 잘 되는 "
                     "쪽으로 옮기는 순간 [47]은 검증이 아니라 곡선맞춤이 된다(§9)\"고 "
                     "못 박았다. PC별 분기 도입은 **주간회의 소관**이다.")
        elif _rf.get("pre_empty"):
            L.append("  - ℹ pre 구간 표본이 없다 — 이 PC는 경계 이전 보호전환 기록이 "
                     "없어 `pre` 설정이 사실상 미사용이다.")
    L.append("")

    # ── [MW0601 440차] v1/v2 엔진 대조 — "고쳤다"는 주장의 감사 근거 ────────────
    _eng = off.get("_sim_fidelity_engines") or {}
    if _eng:
        L.append("### 재생기 엔진 대조 (439차 — [47] 해제작업)")
        L.append("")
        L.append("| 엔진 | 판정 | MAE(개별정확도) | 편향(중앙) | 총합 시뮬 | 총합 실제 | 부호 |")
        L.append("|---|---|---|---|---|---|---|")
        for k, lbl in (("v1", "v1 (435차까지)"), ("v2", "v2 (사다리 편입)")):
            s = _eng.get(k) or {}
            if s.get("repro_bias_R") is None:
                L.append("| %s | %s | — | — | — | — | — |" % (lbl, s.get("verdict", "—")))
                continue
            L.append("| %s | %s | **%.4fR** | %+.4fR | %+.2f | %+.2f | %s |"
                     % (lbl, s.get("verdict", "—"), s.get("mae_R", 0),
                        s["repro_bias_R"], s.get("sim_total_pt", 0),
                        s.get("actual_total_pt", 0), s.get("sign_match")))
        L.append("")
        _v1, _v2 = _eng.get("v1") or {}, _eng.get("v2") or {}
        if _v1.get("mae_R") and _v2.get("mae_R"):
            L.append("- **개별 포지션 정확도(MAE)는 %.4fR → %.4fR (%+.0f%%)로 개선됐다.**"
                     % (_v1["mae_R"], _v2["mae_R"],
                        100.0 * (_v2["mae_R"] - _v1["mae_R"]) / _v1["mae_R"]))
        if _v2.get("sign_margin_sd") is not None:
            L.append("- ⚠ **부호 판정 안정성: |Σ실제| = %.2f SD.** 실제 총합이 분산 대비 "
                     "0 근처면 `sign_match`는 아주 작은 편향으로도 뒤집힌다 — "
                     "\"부호 불일치\"가 재현 실패인지 **기준의 불안정**인지 구분해서 읽을 것."
                     % _v2["sign_margin_sd"])
        L.append("")
        L.append("> **440차가 한 일**: `scripts/exit_replay.py`가 라이브 청산 사다리를")
        L.append("> 미러링한다 — 4단계 트레일링(`compute_trailing_stop_tier` **라이브 함수를**")
        L.append("> **import**) + 손절1차 + TP1/TP2/TP3 분할 + qty=1 보호전환 + 15:10 강제청산.")
        L.append("> 추가로 **코드 세대(체제)를 인식**한다 — 2026-08-03 이전은 TP 트리거가")
        L.append("> 종가뿐이고 보호전환이 `breakeven`이었다(TRADE 로그 전수 집계로 확정).")
        L.append("> 과거를 지금의 규칙으로 재생하면 그 자체가 오차원이 된다.")
        L.append("> ")
        L.append("> **441차가 한 일 — 남은 격차는 재생기 능력이 아니라 계측 결함이었다.**")
        L.append("> 440차는 잔여 격차를 \"틱 경로(오차원 ①)\"로 귀속했으나, 441차가 실제")
        L.append("> 청산 경로별로 분해하니 **틱스톱 76포지션의 오차는 +0.05pt(사실상 0)**")
        L.append("> 였다 — 틱 재현은 이미 정확했다. 격차는 두 계측 결함이었다:")
        L.append("> ")
        L.append("> - **ⓐ 판정식 단위 3중 불일치 (-16.15pt)** — `SUM(pnl_pts)`는 레그별")
        L.append(">   계약당 pt의 **무가중 합**인데 시뮬은 1계약 기준이었고, 게다가 시뮬만")
        L.append(">   왕복비용을 뺐다(실제는 gross). 왜곡이 **결과에 비대칭**이라 더 나쁘다 —")
        L.append(">   이긴 포지션은 TP 분할로 레그가 여러 개(부풀려짐), 진 포지션은 하드스톱")
        L.append(">   전량이라 하나다(417차와 같은 메커니즘). 실측: post 세대 TP도달 오차")
        L.append(">   −18.65pt가 단위 통일 후 **0.00pt** — 전부 이 인공물이었다.")
        L.append("> - **ⓑ 재생기 TP 체결가 (-21.56pt)** — `close` 세대는 트리거가 종가인데")
        L.append(">   체결을 목표가로 계상해 이익 오버슈트가 사라졌다. TP2 완주 22건이")
        L.append(">   목표거리를 **전건 초과**(합 +18.19pt)한 것이 그 증거다. → [47-B] 신설.")
        L.append("> ")
        L.append("> **합격선을 완화해서 통과한 것이 아니다** — 위 둘을 고친 뒤 **구 기준")
        L.append("> (sign_match 무조건) 그대로 PASS**했고(리포트 상단 ④ 항목 확인), 같은")
        L.append("> 수정을 받은 **v1은 여전히 SUSPEND**다(수준 기준 1.25SE > 1.0SE).")
        L.append("> 기준이 판별력을 잃지 않았다는 대조 증거다(§9).")
        L.append("> ")
        L.append("> ⚠ **v1이 만들던 인공물의 크기**: [23-B]에서 v1은 `tp1_x2`를 최선")
        L.append("> (**+37.96pt**)으로 봤는데 v2에서는 최악(**−30.68pt**)이다. TP1에서 종료하며")
        L.append("> `tp1_pts`를 확정이익으로 계상하면 **TP1을 넓히는 것만으로 장부가 좋아지는**")
        L.append("> 순수 인공물이 생긴다. 이 축의 과거 결론을 인용하지 말 것.")
        L.append("")
    L.append("> 기하 A/B 채널들은 전부 같은 재생기 가정을 공유한다 — ① 1분봉 고저가만 본다")
    L.append("> ② TP2에서 종료한다 ③ TP3·4단계 트레일링·신호소멸청산을 모델링하지 않는다.")
    L.append("> 그 가정이 실제를 재현하지 못하면 `delta_vs_current`의 **부호까지 뒤집힌다**")
    L.append("> — 432차 후속2 실측: 러너 프리미엄 보정만으로 [25-B] `tp2_2.00`이")
    L.append("> **+14.76 → −12.13pt**(−61만원)로 역전됐고, 4채널 결론 격차 합계는")
    L.append("> **61.51pt = 307만원**이다.")
    if _gate.get("gate") == "SUSPEND":
        L.append("> ")
        L.append("> ⏸ **아래 채널의 판정을 정지했다** — %s"
                 % ", ".join("`%s`" % t for t in (_gate.get("targets") or [])))
        L.append("> **삭제가 아니라 정지다**: 원 판정은 `verdict_raw`로, 수치는 그대로 보존된다.")
        L.append("> 소스 데이터도 `main.py`가 계속 기록하므로 소급 재실행이 가능하다.")
        L.append("> **해제 조건**: 재생기에 TP3·트레일링을 편입해 재현이 회복되면 **자동 PASS**")
        L.append("> — 사람이 \"재검토하기로 했는데 안 함\"으로 방치할 여지가 없다.")
    elif _gate.get("verdict") == "PASS":
        _crg = VALIDATION_CAMPAIGN.get("sim_fidelity_gate", {}) or {}
        _ver = (set(_crg.get("replay_engine_targets") or [])
                | set(_crg.get("no_replay_targets") or []))
        _unver = [t for t in (_gate.get("targets") or []) if t not in _ver]
        L.append("> ")
        L.append("> ### ⚠ 엔진 커버리지 — **이 PASS가 어디까지 미치는가** (441차 신설)")
        L.append("> ")
        L.append("> 435차는 \"정본([23-B])이 실패하면 같은 가정을 공유하는 그들도 실패한다\"는")
        L.append("> **간접 추론**으로 대상을 정했다. 그 추론은 **제한 방향으로만 타당하다** —")
        L.append("> 역방향(\"정본이 통과하면 그들도 통과\")은 성립하지 않는다. **그들은 정본과**")
        L.append("> **코드를 공유하지 않기 때문이다**: 440차가 고친 것은 `exit_replay.py`인데,")
        L.append("> 미이관 채널은 자체 `_simulate`를 그대로 쓴다(441차 코드 확인).")
        L.append("> ")
        L.append("> | 채널 | 재생 방식 | 이 PASS가 검증하나 |")
        L.append("> |---|---|---|")
        L.append("> | `tp1_geometry_shadow` [23-B] | **정본** `exit_replay` | ✅ 직접 검증 |")
        L.append("> | `hurst_threshold_shadow` [46] | **재생 없음**(실제 손익 슬라이스) | ➖ 무관 |")
        L.append("> | `quantile_tp_shadow` [3-B] | 자체 `_simulate` — **TP1에서 종료** | ❌ 미검증 |")
        L.append("> | `tp1_protect_offset_shadow` [25]/[25-B] | 자체 `_simulate` — **TP2에서 종료** | ❌ 미검증 |")
        L.append("> ")
        if _unver:
            L.append("> ⏸ 그래서 **다음 채널은 PASS에도 불구하고 정지를 유지한다** — %s"
                     % ", ".join("`%s`" % t for t in _unver))
            L.append("> 사유가 다르므로 표기도 다르다: \"재현 실패\"가 아니라 **\"정본 재생기**")
            L.append("> **미이관\"**이다. 원인이 다르면 처방도 다르다 — 전자는 재생기를 고치는")
            L.append("> 것이고, **후자는 그 채널을 `exit_replay`로 이관하는 것**이다.")
            L.append("> ")
        L.append("> 🔴 **[3-B]는 특히 위험하다.** 그 채널의 자체 시뮬은 TP1에서 종료하며 TP1")
        L.append("> 목표가를 확정이익으로 계상하는데, 440차가 [23-B]에서 **\"TP1을 넓히는")
        L.append("> 것만으로 장부가 좋아지는 순수 인공물\"**로 지목한 바로 그 구조다(v1에서")
        L.append("> `tp1_x2` 최선 +37.96 → v2에서 최악 −30.68). 그런데 [3-B]의 질문 자체가")
        L.append("> **\"TP1 거리를 무엇으로 정하나\"** 라서 이 인공물이 답을 직접 오염시킨다 —")
        L.append("> `q_raw`의 우위를 이관 전 수치로 인용하지 말 것.")
    L.append("> ⚠ **사전등록 정직성**: 최초 SUSPEND는 432차 후속2에서 **이미 본 결과**의")
    L.append("> 코드화다([25]의 `breakeven`과 같은 취급). 사전등록 가치는 **회복 판정**에 있다.")
    L.append("> ⚠ 정본 재생기로 [23-B]를 쓴다(포지션 단위 조인이 되는 유일한 채널). 다른")
    L.append("> 채널은 같은 세 가정을 공유하므로 **간접 추론**이다.")
    L.append("")

    # ── [MW0601 441차] [47-B] TP 체결 오버슈트 감시 ────────────────────────────
    L.append("## [47-B] TP 체결 오버슈트 감시 (441차 신설 · 관찰 전용)")
    L.append("")
    _ovs = off.get("tp_fill_overshoot_watch") or {}
    if _ovs.get("error"):
        L.append("> ⚠ 미산출 — %s" % _ovs["error"])
    else:
        L.append("- 판정: **%s** — %s" % (_fmt_verdict(_ovs.get("verdict", "")),
                                         _ovs.get("reason", "—")))
        L.append("- TP 레그 %s건 / %s거래일 (ATR 결측 제외 %s건)"
                 % (_ovs.get("n", "—"), _ovs.get("n_days", "—"),
                    _ovs.get("n_skipped_atr", 0)))
        _blocks = []
        if _ovs.get("overall"):
            _blocks.append(("전체", _ovs["overall"]))
        for k, v in (_ovs.get("by_era") or {}).items():
            _blocks.append(("세대 `%s`" % k, v))
        for k, v in (_ovs.get("by_stage") or {}).items():
            _blocks.append((k, v))
        if _blocks:
            L.append("")
            L.append("| 구분 | n | 일수 | 중앙(pt) | 평균(pt) | 중앙(ATR배) | 양수비율 | 최대 |")
            L.append("|---|---|---|---|---|---|---|---|")
            for label, a in _blocks:
                if not a:
                    continue
                L.append("| %s | %d | %d | %+.3f | %+.3f | %+.3f | %.0f%% | %+.2f |"
                         % (label, a["n"], a["n_days"], a["median_pt"], a["mean_pt"],
                            a["median_atr"], 100 * a["pos_share"], a["max_pt"]))
        L.append("")
    L.append("> **무엇을 재나**: 오버슈트 = (실제 TP 체결거리) − (재생기 목표거리).")
    L.append("> `envelope` 세대(틱 TP)는 틱이 목표가를 스치는 즉시 나가므로 **0 근처**가")
    L.append("> 정상이고, `close` 세대는 종가까지 간 만큼 **양수**가 정상이다 — 그래서")
    L.append("> 세대별로 갈라 본다(경계는 사전등록된 `replay_regime`).")
    L.append("> ")
    L.append("> **왜 생겼나**: 441차가 [47] 딥다이브에서 재생기가 `close` 세대의 TP를")
    L.append("> **목표가로 체결 계상**하던 결함을 찾았다(트리거는 종가인데). TP2 완주")
    L.append("> 22건이 목표거리를 전건 초과했고 그것이 재현 격차 **-21.56pt**였다.")
    L.append("> 결함은 고쳤고, 이 채널은 **같은 종류의 재발을 상시 감시**한다 —")
    L.append("> 체결 모델은 코드 세대가 바뀔 때 조용히 어긋나고, 441차 이전에는 그걸")
    L.append("> 볼 계기가 게이트 SUSPEND 딥다이브밖에 없었다(약 2개월간 미발견).")
    L.append("> ")
    L.append("> ⚠ **판정하지 않는다(OBSERVE).** 정상 오버슈트 크기의 기준을 지금 만들면")
    L.append("> **관측을 본 뒤 기준을 세우는 것**(313차 위반)이 된다. 표본이 쌓여 분포가")
    L.append("> 드러나면 §9 주간회의에서 사전등록할 것.")
    L.append("> ⚠ 오버슈트는 **이미 실현된 실제 손익의 일부**다 — \"더 벌 수 있었다\"가")
    L.append("> 아니다. `[1계약·미실현 시뮬]` 배지 채널들과 성격이 다르다.")
    L.append("> ⚠ [47] 게이트의 `targets`에 **넣지 않았다** — 게이트가 쓰는 재생기 자체를")
    L.append("> 감시하므로 게이트가 이것을 정지시키면 순환 논증이 된다.")
    L.append("")

    L.append("## [48] 봉중 하드스톱 경로 건전성 (435차 신설 · 시뮬 무관)")
    L.append("")
    if bsp.get("per_path"):
        L.append("| 경로 | n | 합계pt | 평균 | 유리비율 | 부호검정 p | 거래일 |")
        L.append("|---|---|---|---|---|---|---|")
        for k in ("봉중 하드스톱", "종가 하드스톱", "틱 하드스톱", "목표(TP1/TP2/기타)"):
            d = bsp["per_path"].get(k)
            if not d:
                continue
            L.append("| %s | %d | %+.2f | %+.3f | %d/%d (%.0f%%) | %.5f | %d |"
                     % (k, d["n"], d["total"], d["mean"], d["fav"], d["n"],
                        100 * d["fav_rate"], d["sign_p"], d["days"]))
        L.append("")
    L.append("- 판정: **%s** — %s" % (_fmt_channel_verdict(bsp),
                                     bsp.get("reason", bsp.get("error", "—"))))
    L.append("- (음수 = 유리) 미태깅 재분류 %s건 — `hint_source`는 423차부터 기록된다"
             % bsp.get("n_reclassified", 0))
    L.append("")
    L.append("> **틱 경로는 대칭이고(정직) 봉중 경로만 편향된다.** 메커니즘은 두 겹이다 —")
    L.append("> ① `price_hint`가 `min(_prev_stop_price, bar_high)`라 **허구의 스톱가**이고")
    L.append("> (주문은 시장가라 손익은 무관, 슬리피지 지표만 오염) ② 유령 하드스톱은")
    L.append("> \"봉의 극값이 스톱 조임보다 먼저 발생\"할 때만 생기고 스톱 조임은 TP1이")
    L.append("> 전제라 **이익 중인 포지션에서만 발동**한다 — 편향이 결정론적이다.")
    L.append("> ⚠ 사전등록 정직성: 첫 관측(13/13, p=0.00024)은 신설 전에 이미 봤다 —")
    L.append("> 재확인용이며, 가치는 **억제 후 회복 판정**에 있다.")
    L.append("")

    # ── [439차 P3] 발생 추이 + 가드 경계 분해 + 손익 오독 차단 ────────────────
    if bsp.get("path_by_day"):
        L.append("### [48-T] 발생 추이와 가드 경계 (439차 P3, 관찰 전용)")
        L.append("")
        L.append("| 날짜 | 봉중 | 틱 | 목표 | |")
        L.append("|---|---|---|---|---|")
        for _d in sorted(bsp["path_by_day"]):
            _p = bsp["path_by_day"][_d]
            _mk = "**← 423차 가드 배포**" if _d == bsp.get("guard_live_date") else ""
            L.append("| %s | %d | %d | %d | %s |" % (
                _d, _p.get("봉중 하드스톱", 0), _p.get("틱 하드스톱", 0),
                _p.get("목표(TP1/TP2/기타)", 0), _mk))
        L.append("")
        _pre, _post = (bsp.get("pre_guard") or {}), (bsp.get("post_guard") or {})
        L.append("- 가드 이전 **%d건 / %d거래일** (%+.2fpt) · 가드 이후 **%d건 / %d거래일** (%+.2fpt)"
                 % (_pre.get("n", 0), _pre.get("days", 0), _pre.get("total", 0.0),
                    _post.get("n", 0), _post.get("days", 0), _post.get("total", 0.0)))
        L.append("- 최근 %d거래일 봉중 발생: **%s** — 마지막 발생 이후 **무발생 %d거래일**"
                 % (len(bsp.get("recent_days", [])),
                    " / ".join(str(x) for x in bsp.get("bar_recent_seq", [])),
                    bsp.get("bar_dry_days", 0)))
        L.append("")
    if bsp.get("prereg_contaminated"):
        L.append("- 🔴 **사전등록 오염** — %s" % bsp.get("contamination_reason", ""))
        L.append("  - **위 verdict는 풀링값이다.** 판정 시 pre/post를 분리해 읽을 것.")
        L.append("  - 판정식·`fav_rate_band`·`min_samples`는 **무변경**이다(§9, 313차 —")
        L.append("    사후 데이터로 합격선을 움직이지 않는다). 바뀐 것은 가시성뿐이다.")
        L.append("")
    L.append("> 🔴 **`합계pt`는 손익이 아니다 — 원화로 환산하지 말 것.** `price_hint`가")
    L.append("> 봉 고저가에서 유도한 **허구의 스톱가**라 주문(시장가)과 무관하고, 슬리피지")
    L.append("> 지표만 오염시킨다. 봉중 −24.51pt를 \"122만원 유리했다\"로 읽으면 틀린다.")
    L.append("> 실제 손익 기여 추정은 두 개가 있고 **서로 3배 이상 어긋난 채 미해결**이다:")
    L.append("> ① 424차 — 08-04 qty≥2 3건 실현 +8.76pt(+433,609원) vs 반사실 0pt")
    L.append("> ② 435차 — 1분봉 반사실 재생 9건 통산 **≈+3.0pt**, 08-05 억제 5건은")
    L.append("> **억제가 오히려 +0.38pt 유리**")
    L.append("> 둘 다 이 채널의 사전등록 판정이 **아니다**. 라이브 재판정 경로는")
    L.append("> **[35-M] 미러 서브표본**(440차)뿐이다 — 그쪽을 볼 것.")
    L.append("")

    L.append("## [49] 페이오프 기하 상시 감시 (435차 신설 · 시뮬 무관)")
    L.append("")
    if pgw.get("krw"):
        L.append("| 기준 | n | 승률 | 평균승 | 평균패 | 손익비 | 손익분기승률 | edge_gap |")
        L.append("|---|---|---|---|---|---|---|---|")
        for nm, d in (("원화(pt)", pgw.get("krw")), ("위험조정(R)", pgw.get("risk"))):
            if not d:
                continue
            L.append("| %s | %d | %.1f%% | %+.3f | %+.3f | %.3f | %.1f%% | **%+.2f%%p** |"
                     % (nm, d["n"], 100 * d["win_rate"], d["avg_win"], d["avg_loss"],
                        d["payoff"], 100 * d["breakeven_wr"], 100 * d["edge_gap"]))
        L.append("")
    L.append("- 판정: **%s** — %s" % (_fmt_verdict(pgw.get("verdict", "")),
                                     pgw.get("reason", pgw.get("error", "—"))))
    L.append("- 포지션 %s건 / 레그 %s건 (다중레그 포지션 %s건) — ⚠ **417차: 포지션 단위로 병합**"
             % (pgw.get("n"), pgw.get("n_legs"), pgw.get("n_multileg")))
    L.append("")
    L.append("> **현행 기하가 애초에 이길 수 있는 구조인가**를 묻는 유일한 채널이다")
    L.append("> ([24]는 반납만, [25]는 offset만, [23-B]는 대안 기하만 본다).")
    L.append("> 설정 직독: 하드스톱 `ATR×1.50` / 보호스톱(qty=1) `ATR×0.25`(호라이즌 무관 상수)")
    L.append("> → 보호전환에 걸린 승리만 놓고 보면 **손익분기 승률 85.7%**. 러너가 그 격차를 메운다.")
    L.append("> TP1은 374/387차에 호라이즌별로 분화됐는데(0.3/0.5/0.7) lock은 339차 상수라")
    L.append("> **유지율이 호라이즌에 반비례**한다(1m 83% / 3m 50% / 5m 36%).")
    L.append("> ⚠ 두 기준이 갈리면 **결과가 소수 고변동일에 집중**됐다는 신호다 — 그래서 둘 다 찍는다.")
    L.append("")

    # [54] ConstOut 호라이즌 건강도 (MW0601 471차 후속7 / G-2 · 487차 F-9로 구 [51]에서 재배정)
    L.append("## [54] ConstOut 호라이즌 건강도 (471차 후속7 신설 · 시뮬 무관 · 구 [51])")
    L.append("")
    L.append("- 판정: **%s** — %s" % (_fmt_verdict(cow.get("verdict", "")),
                                     cow.get("reason", cow.get("error", "—"))))
    if cow.get("verdict") == "NOT_AVAILABLE_ON_THIS_BRANCH":
        # [MW0602 487차 / F-8(B)] 생산부가 이 브랜치에 없으면 아래 본문(457차 G5
        # 집계 전제)은 전부 거짓 전제가 된다 — 표를 비워 두는 대신 이유를 적는다.
        L.append("")
        L.append("> 생산부(`scaler_daily.const_out_by_horizon` 컬럼, 457차 G5)가 이 브랜치에 없다.")
        L.append("> 2026-08-23 멀티PC 정책 폐기로 체리픽 경로가 닫혔다 — 자체 재구현(P3 백로그)")
        L.append("> 전까지 이 표기가 정상이며, **INSUFFICIENT(표본 축적 중)로 읽으면 안 된다.**")
        L.append("")
    else:
        _co_tot = cow.get("const_out_by_horizon_totals") or {}
        if _co_tot:
            L.append("")
            L.append("| 호라이즌 | ConstOut 사건 | 제외 분 | 발생 거래일 |")
            L.append("|---|---|---|---|")
            for _hz, _v in _co_tot.items():
                L.append("| %s | %d | %d | %d |" % (
                    _hz, _v.get("events", 0), _v.get("minutes", 0), _v.get("days", 0)))
        _co_hz = cow.get("by_horizon") or {}
        if _co_hz:
            def _co_cell(d):
                return ("%d / %s원" % (d["n"], format(d["avg_pnl_krw"], ",.0f"))
                        if d else "—")
            L.append("")
            L.append("| 호라이즌 | heavy n / 평균 | clean n / 평균 |")
            L.append("|---|---|---|")
            for _hz, _v in sorted(_co_hz.items()):
                L.append("| %s | %s | %s |" % (
                    _hz, _co_cell(_v.get("heavy")), _co_cell(_v.get("clean"))))
        L.append("")
        L.append("> **일별 영속화는 457차 G5가 이미 하고 있다**(`scaler_daily.const_out_by_horizon`).")
        L.append("> 이 채널은 그 집계를 **진입 성적과 결합**하는 부분만 담당한다.")
        L.append("> 🔴 `const_out_by_horizon`이 NULL인 날(457차 G5 배포 이전)의 진입은 **양 버킷")
        L.append("> 어디에도 넣지 않는다** — 미측정을 clean으로 세면 버킷이 오염된다(계측 4원칙 ②).")
        L.append("> 이번 주 제외 포지션 **%s건**. 그래서 당분간 INSUFFICIENT가 정상이다."
                 % cow.get("n_excluded_unmeasured", "—"))
        L.append("> ⚠ FLAG_DRAG는 **차단 처방이 아니다** — 라우터 선택 억제·재학습 스케줄·")
        L.append("> 피처셋 조사 축이다(316~318차 HurstGate FalseBlock 교훈).")
        L.append("")

    # [33] 급행풀스톱 발굴 재실행 게이지 (MW0601 421차 후속10)
    # 판정 채널이 아니다 — Phase A를 언제 다시 돌릴지 사람이 기억하지 않아도 되게 하는
    # 알림이다. 별도 캘린더 신설 금지 규약(CLAUDE.md 주기적 재검증 절)에 따라 여기 얹는다.
    L.append("## [33] 급행풀스톱 판별자 발굴 — 재실행 게이지 (421차 후속10, 알림 전용)")
    L.append("")
    try:
        from scripts.faststop_discovery import readiness as _fs_ready
        _fs = _fs_ready()
    except Exception as _e:
        _fs = {"error": "게이지 계산 실패: %s" % _e}
    if _fs.get("error"):
        L.append("> ⚠ %s" % _fs["error"])
    else:
        # [MW0601 422차 후속] `10%`가 이스케이프되지 않아 `%s`와 함께 변환지정자 2개로
        # 해석돼 TypeError로 **리포트 생성 전체가 죽었다**(421차 후속10 도입 이래).
        # 문자열 그대로의 퍼센트는 `%%`여야 한다.
        L.append("- 마지막 Phase A 실행: **%s** (결과: BH FDR 10%% 통과 0개)"
                 % _fs.get("last_run", "—"))
        L.append("- 현재 표본: 포지션 %d / FAST **%d** / 거래일 %d (그중 **유효 %d일**)"
                 % (_fs["n_positions"], _fs["n_fast"], _fs["n_days"], _fs["n_useful_days"]))
        L.append("")
        L.append("| 트리거 | FAST | 유효 거래일 | 도달 |")
        L.append("|---|---|---|---|")
        for _tag, _lbl in (("interim", "중간(재실행 검토)"), ("full", "본(재실행 권고)")):
            _t = _fs.get(_tag) or {}
            L.append("| %s | %d / %d %s | %d / %d %s | %s |" % (
                _lbl, _fs["n_fast"], _t.get("min_fast", 0), "✅" if _t.get("fast_ok") else "…",
                _fs["n_useful_days"], _t.get("min_useful_days", 0),
                "✅" if _t.get("days_ok") else "…",
                "🔔 **도달**" if _t.get("reached") else "—"))
        L.append("")
        if (_fs.get("full") or {}).get("reached"):
            L.append("> 🔔 **본 트리거 도달 — `python scripts/faststop_discovery.py --perm 20000`")
            L.append("> 재실행 후 `faststop_rerun_watch.last_run_date`를 갱신할 것.**")
        elif (_fs.get("interim") or {}).get("reached"):
            L.append("> 🔔 **중간 트리거 도달 — 재실행 검토 시점이다.** 본 트리거까지")
            L.append("> 기다릴지 지금 한 번 돌려볼지 주간회의에서 판단할 것.")
        else:
            L.append("> 아직 두 트리거 모두 미도달 — 표본 축적 중. **조치 불필요.**")
    L.append("")
    L.append("> **유효 거래일**이 병목이다 — 일자 내 순열검정은 FAST와 OK가 **둘 다 있는")
    L.append("> 날**만 정보를 내므로 전체 거래일이 아니라 그 교집합이 실질 표본이다")
    L.append("> (초판 12일 중 7일). 실측 속도도 FAST 7.0건/주 vs 유효거래일 2.4일/주였다.")
    L.append("> 판정 채널이 아니므로 verdict를 내지 않는다.")
    L.append("")

    # [30] toxicity 재보정 밴드분포 상세 (MW0601 419차)
    L.append("## [30] toxicity_score 재보정 후 밴드 분포 (MW0601 419차, P0)")
    L.append("")
    if trw.get("error"):
        L.append("> ⚠ %s" % trw["error"])
    else:
        L.append("- 재보정 배포일: **%s** / cancel_churn ceiling: **%s** (구값 0.08)"
                 % (trw.get("effective_date", "—"), trw.get("cancel_churn_ceiling", "—")))
        L.append("- 집계 분봉: %s (백필 생성 행 제외 — 418차)" % trw.get("n_bars", "—"))
        L.append("")
        L.append("| 구간 | block | reduce | pass | cancel_stress 포화 | score p50 |")
        L.append("|---|---|---|---|---|---|")
        L.append("| 재보정 **전** 실측 (07-24~07-31, n=2,229) | 23.3% | 76.4% | **0.27%** | **100.0%** | 0.3475 |")
        L.append("| 380차 설계목표 | 0.7% | 11.8% | 87.5% | — | — |")
        L.append("| **이번 주 실측** | %s | %s | %s | %s | %s |" % (
            ("%.1f%%" % (trw["block_share"] * 100)) if "block_share" in trw else "—",
            ("%.1f%%" % (trw["reduce_share"] * 100)) if "reduce_share" in trw else "—",
            ("%.1f%%" % (trw["pass_share"] * 100)) if "pass_share" in trw else "—",
            ("%.1f%%" % (trw["cancel_sat_share"] * 100)) if "cancel_sat_share" in trw else "—",
            trw.get("score_p50", "—")))
        L.append("")
        if "churn_p50" in trw:
            L.append("- cancel_churn_ratio 실측: p50=%s / p99=%s (ceiling %s)"
                     % (trw["churn_p50"], trw["churn_p99"],
                        trw.get("cancel_churn_ceiling", "—")))
        L.append("- **판정: %s**%s" % (
            trw.get("verdict", "—"),
            (" — %s" % trw["reason"]) if trw.get("reason") else ""))
        if trw.get("recommendation"):
            L.append("- 권고: %s" % trw["recommendation"])
    L.append("")
    L.append("> **왜 이 채널이 생겼나**: 380차가 `cancel_churn_ratio` ceiling을 0.08로")
    L.append("> 잠정 설정하며 코드 주석에 \"라이브 섀도 관찰 후 재보정 필요\"라고 **스스로**")
    L.append("> **예고**했으나 실행되지 않았다. 라이브 실측 p50=0.2649로 ceiling의 3.3배 —")
    L.append("> **초과율 100%** 라 가중 0.20짜리 성분이 전 분봉에서 1.0으로 포화해 score에")
    L.append("> 상수 +0.20을 더하는 죽은 항이 됐다(중앙값 score 0.3475의 58%).")
    L.append("> 그 오프셋 때문에 게이트가 사실상 상시 발동(pass 0.27%) 상태였다.")
    L.append("> ⚠ **FAIL이어도 임계값을 자동으로 바꾸지 말 것** — block 0.45 / reduce 0.28은")
    L.append("> 전 채널 판정에 영향을 주므로 §3 원칙대로 주간회의 결정 + DECISION_LOG 기록이")
    L.append("> 선행돼야 한다. 또한 이 재보정은 **진입을 늘리는 방향**이라(시뮬레이션 기준")
    L.append("> block 23.3%→8.6%) CLAUDE.md 실전전환기준 ⑧과 함께 읽어야 한다.")
    L.append("")

    # [31] tox reduce 연속배수 섀도 상세 (MW0601 419차)
    L.append("## [31] ToxicityGate reduce 연속 배수 섀도 (MW0601 419차, P1)")
    L.append("")
    if trm.get("error"):
        L.append("> ⚠ %s" % trm["error"])
    else:
        L.append("- reduce 밴드 체결 진입: **%s건**%s" % (
            trm.get("n_samples", "—"),
            (" (trades 조인 %s건, 실현손익 합 %s원)" % (
                trm["matched_trades"], format(trm.get("total_pnl_krw", 0), ",.0f")))
            if trm.get("matched_trades") else ""))
        if trm.get("anchor_stale"):
            L.append("- %s" % trm["anchor_stale"])
        if "shadow_mult_mean" in trm:
            L.append("- 섀도 배수 분포: min=%s / p50=%s / max=%s, **평균=%s** (실적용 상수 0.70)"
                     % (trm["shadow_mult_min"], trm["shadow_mult_p50"],
                        trm["shadow_mult_max"], trm["shadow_mult_mean"]))
            L.append("  - 평균이 0.70에서 크게 벗어나면 **노출 중립 설계가 깨진 것**이다 —")
            L.append("    앵커(`TOXICITY_REDUCE_MULT_SHADOW_HI/LO`) 재도출 필요.")
            L.append("  - 현행 앵커 도출일: **%s** (421차 재도출, HI=0.81/LO=0.36)."
                     " 이 날짜 이전 표본은 구 앵커(0.90/0.45)로 계산된 값이라 섞어"
                     " 읽지 말 것." % trm.get("anchor_date", "—"))
            L.append("  - ⚠ 이 평균은 **게이트 이벤트** 모집단이다. 앵커 도출에 쓴")
            L.append("    **봉** 모집단과 값이 다르다(08-03 실측 0.8205 vs 0.7894) —")
            L.append("    절대값 판정이 아니라 추세 감시용으로 읽을 것.")
        if "divergent_qty_share" in trm:
            L.append("- tox 스테이지에서 수량이 달라진 진입: **%s/%s (%.1f%%)** (기준 %.0f%%)"
                     % (trm["divergent_qty_n"], trm["n_samples"],
                        trm["divergent_qty_share"] * 100,
                        float(VALIDATION_CAMPAIGN.get(
                            "toxicity_reduce_mult_shadow", {}).get(
                            "divergence_min_share", 0.20)) * 100))
        L.append("- **판정: %s**%s" % (
            trm.get("verdict", "—"),
            (" — %s" % trm["reason"]) if trm.get("reason") else ""))
        if trm.get("recommendation"):
            L.append("- 권고: %s" % trm["recommendation"])
    L.append("")
    L.append("> **PASS가 \"좋다\"는 뜻이 아니다** — 이 채널의 PASS는 \"연속화해도 수량이")
    L.append("> 안 바뀌니 현행 상수를 유지하라\"는 뜻이다. 상수 0.7이 정보를 폐기하는 것은")
    L.append("> 실측으로 확정돼 있다(reduce 밴드 n=1,614에서 향후 15m 평균스프레드가 5분위")
    L.append("> 2.8→3.8틱 단조 증가, Spearman rho=+0.319 t=13.48). 다만 사이징 체인이 8단")
    L.append("> `max(1, round())`로 양자화하고 실체결이 1~2계약에 묶여 있어 그 정보를 살릴")
    L.append("> 여지 자체가 없을 수 있고, 그렇다면 복잡도만 늘리는 변경이므로 하지 않는 것이 맞다.")
    L.append("> ⚠ `qty_after_*`는 **tox 스테이지 국소값**이다 — 하류(L2·Hurst·Degraded·상한)를")
    L.append("> 재시뮬레이션하지 않는다. 두 값이 같으면 최종 수량도 같지만(입력 동일), 다르다고")
    L.append("> 최종 수량이 반드시 달라지는 것은 아니다.")
    L.append("> ⚠ 현행 앵커는 **재보정 전** 분포로 도출됐다 — [30]이 새 분포를 확정하면")
    L.append("> 재도출할 것. 그전 판정은 잠정이다.")
    L.append("")
    L.append("---")
    L.append("")

    # [34] meta "size 0" 무시 상세 (MW0601 422차 후속)
    L.append("## [34] meta \"size 0\" 무시 (MW0601 422차 후속)")
    L.append("")
    L.append("**모델이 \"베팅하지 마라\"고 한 신호로 실제 진입한 건**의 손익이다.")
    L.append("`_make_result()`는 `conf < 0.5`에서 size를 **0.0**으로 내는데, 액션 밴드가 덮는다 —")
    L.append("`reduce`는 `or 0.5`(→0.5), `take`는 `max(0.9, …)`(→**0.9**, 거의 풀사이즈).")
    L.append("")
    L.append("> **임계 0.5는 임의 상수가 아니다.** `conf`는 4급 품질레이블(Q0~Q3, 가중치 0/⅓/⅔/1)의")
    L.append("> 기대값이고 `conf = ⅓(1−a)(1−h) + ⅔a(1−h) + a·h` 이다. **a=0.5를 넣으면 고신뢰비중**")
    L.append("> **h와 무관하게 정확히 0.5** — 즉 `conf<0.5 ⟺ 적중률<50% 추정`이다.")
    L.append("")
    if msz.get("error"):
        L.append("- ⚠ 조회 실패: `%s`" % msz.get("error"))
        L.append("  (`ensemble_decisions.meta_size_raw` 미생성 — 422차 후속 배선 후 첫 기동 전이면 정상)")
    else:
        L.append("- 계측 시작: `%s` 이후 결정만 (그 이전은 raw 복원 불가 → NULL)"
                 % (VALIDATION_CAMPAIGN.get("meta_size_zero_shadow", {}).get("effective_date", "—")))
        L.append("- 미계측 %s건 / 계측 %s건 · 그중 raw==0 **%s건** (%.1f%%)"
                 % (msz.get("unmeasured", 0), msz.get("measured", 0), msz.get("n", 0),
                    float(msz.get("zero_share", 0) or 0) * 100))
        L.append("")
        L.append("| 밴드 | 왜곡 | raw0 진입 | 매칭 | 누적손익 | 평균 | 승률 | 거래일 | 음수일 |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for _b, _dist in (("reduce", "0.0→0.5"), ("take", "0.0→**0.9**"), ("_합계", "—")):
            _v = (msz.get("bands") or {}).get(_b) or {}
            L.append("| %s | %s | %s | %s | %s원 | %s원 | %.1f%% | %s | %s |" % (
                _b, _dist, _v.get("n", 0), _v.get("matched", 0),
                format(int(_v.get("total_pnl_krw", 0) or 0), ","),
                format(int(_v.get("avg_pnl_krw", 0) or 0), ","),
                float(_v.get("win_rate", 0) or 0) * 100,
                _v.get("days", 0), _v.get("neg_days", 0)))
        L.append("")
    L.append("> **밴드를 합산해 읽지 말 것.** `take`의 왜곡(0.0→0.9)이 `reduce`(0.0→0.5)보다")
    L.append("> 크다 — 한 숫자로 합치면 큰 왜곡이 작은 쪽에 희석된다. 합계 행은 판정용이지")
    L.append("> 해석용이 아니다.")
    L.append("> ")
    L.append("> **판정 시 교란 3종을 반드시 함께 읽을 것** (settings `[34]` 주석):")
    L.append("> (a) `recent_accuracy`가 meta 입력이라 conf는 **자기상관**을 갖는다 — \"size 0")
    L.append("> 구간이 나빴다\"가 사전 판별력인지 나쁜 구간의 뭉침인지 구분되지 않는다.")
    L.append("> (b) meta 학습 스트림에 **퇴역한 30m(20.8%)과 FLAT 예측(20~45%)이 혼입**된다")
    L.append("> — conf 기준선이 그날 검증된 호라이즌 구성에 따라 흔들린다.")
    L.append("> (c) LR이 `class_weight='balanced'`라 conf가 실제보다 **높게** 나올 수 있다")
    L.append("> — `conf<0.5`는 오히려 보수적 추정일 수 있다.")
    L.append("> ")
    L.append("> FAIL이어도 **자동 전환 금지** — \"안 B\"(raw==0 → action skip 강등)는 액션 축")
    L.append("> 변경이라 라이브 진입 동작이 바뀐다. §9 사전등록 원칙대로 주간회의 안건이다.")
    L.append("")
    L.append("---")
    L.append("")

    # ── [35]~[37] MW0602 424차 후속 신설 3채널 상세 ─────────────────────────
    L.append("## [35] 유령 하드스톱 — 결함인가 알파인가 (MW0602 424차 후속)")
    L.append("")
    L.append("423차 가드가 `qty>=2`의 TP1 손익분기 경로를 우회해 유령 청산이 났다.")
    L.append("**일부러 고치지 않고 재고 있다** — 손익 부호가 예상과 반대이기 때문이다.")
    L.append("")
    L.append("> **[439차 정정] \"계속 난다\"는 더 이상 사실이 아니다.** 431차의 MAX_CONTRACTS")
    L.append("> 10→3 + 게이트 체인 재구성으로 `qty>=2` 진입이 사라져 유령 청산 모집단이")
    L.append("> 소멸했다(2026-08-05 이후 `live_suppressed=0` **0건**). 아래 근거표는")
    L.append("> **그 시절의 기록**이며 현행 상태가 아니다 — 현행은 [35-M] 미러를 볼 것.")
    L.append("")
    L.append("| 근거일 | 건수 | 실현 | 반사실(정상 가드) |")
    L.append("|---|---|---|---|")
    L.append("| 2026-08-03 (423차 실측) | 8 | +1.42pt | 5건 유리 / 3건 불리 |")
    L.append("| 2026-08-04 (qty≥2) | 3 | **+8.76pt (+433,609원)** | **0pt** |")
    L.append("")
    L.append("> 08-04의 +433,609원은 그날 순익 +752,561원의 **57.6%**다. 정상 동작이었다면")
    L.append("> 약 +316,000원이었다. 유령 판정은 *\"봉 고가가 스톱을 스쳤으나 현재가는 유리하게")
    L.append("> 되돌아왔다\"*에서만 성립해 **시장가가 스톱보다 좋은 국면만 고른다** — 스파이크-")
    L.append("> 되돌림 익절을 우연히 구현하고 있을 수 있다.")
    L.append("")
    L.append("반사실 정의(관측 전 고정): 억제했다면 포지션은 유지되고 **판정에 실제로 쓰인**")
    L.append("**스톱(`stop_eval`)** 으로 계속 간다 → 이후 분봉에서 닿으면 그 가격, 15:10까지")
    L.append("안 닿으면 그날 마지막 종가. `delta_pt = 실현 − 반사실`, (+)면 유령이 유리.")
    L.append("")
    if pse.get("error"):
        L.append("- ⚠ 조회 실패: `%s`" % pse.get("error"))
    elif not pse.get("n") and pse.get("structural_block"):
        L.append("- ⚠ **구조적 판정불가** — %s" % pse.get("structural_reason", ""))
        L.append("  - 이것은 \"표본이 모이는 중\"이 **아니다**. 🔴 NO-DATA(배선 점검)와도 "
                 "다르다 — 적재는 정상이고 주판정 **필터를 통과하는 모집단이 사라졌다**. "
                 "[28] `sizing_inversion_watch`와 같은 유형이다(440차).")
        L.append("  - ⚠ **[439차 P3 자체 정정]** 위 문구의 초판은 \"유령 청산은 qty≥2 "
                 "경로에서**만** 났다\"·\"qty≥2 진입 **자체가 사라졌다**\"였는데 둘 다 "
                 "과했다. 실측: **08-03에 봉중 유령 8건이 전부 qty=1에서 났다**"
                 "(423차 가드가 그날 장 마감 후 커밋 `c64efd6` — 그 세션은 가드 없이 "
                 "돌았고 진입 21건이 전부 qty=1이었다). qty≥2 한정은 **가드 배포 이후**에만 "
                 "성립한다. 또 qty≥2는 사라진 게 아니라 급감이다(08-07 1건). "
                 "경로별 일자 추이는 **[48-T]** 참조.")
    elif not pse.get("n"):
        L.append("- 표본 없음 — `phantom_stop_shadow` 적재 대기 (계측 시작 **%s**)."
                 % pse.get("effective_date"))
        L.append("  그 이전 판정은 소스가 없어 **소급 재구성이 불가능**하다.")
    else:
        L.append("- 유령 청산 **%s건 / %s거래일** (반사실 산출 실패 %s건 제외)"
                 % (pse.get("n"), pse.get("n_days"), pse.get("n_unresolved", 0)))
        L.append("- 실현 %+.2fpt vs 반사실 %+.2fpt → **delta %+.2fpt** (평균 %+.3fpt/건, 유리 %s건)"
                 % (pse.get("realized_pt_sum", 0.0), pse.get("cf_pt_sum", 0.0),
                    pse.get("delta_pt_sum", 0.0), pse.get("delta_pt_avg", 0.0),
                    pse.get("favorable_n", 0)))
        if pse.get("paired_days"):
            L.append("- 일자단위(313차): %s/%s일 유리, 평균 %+.3fpt, **부호검정 p=%s**"
                     % (pse.get("days_positive"), pse.get("paired_days"),
                        pse.get("mean_diff", 0.0), pse.get("sign_p")))
        if pse.get("by_path"):
            L.append("")
            L.append("| 조이기 경로 | 건수 | delta 합 |")
            L.append("|---|---|---|")
            for _k, _v in sorted((pse.get("by_path") or {}).items()):
                L.append("| `%s` | %s | %+.2fpt |" % (_k, _v["n"], _v["delta_pt_sum"]))
    L.append("")
    _mir = pse.get("mirror") or {}
    if _mir.get("n"):
        L.append("### [35-M] 미러 서브표본 — 억제된 쪽 (439차 신설, 관찰 병기)")
        L.append("")
        L.append("주판정이 보는 `live_suppressed=0`(유령 청산 발생)이 431차 이후 사라졌으므로,")
        L.append("**같은 Δ를 `live_suppressed=1`(가드가 억제해 버틴 건)에서 반대 방향으로** 잰다.")
        L.append("반사실(관측 전 고정): 유령 청산은 시장가이므로 판정 시점 `cur_price` 체결로 본다.")
        L.append("**부호 규약은 주판정과 같다 — (+)면 유령이 유리.**")
        L.append("")
        L.append("- 억제 **%d건 / %d거래일** (계측 시작 이후 적재 %d행, 다중레그 %d건)"
                 % (_mir["n"], _mir.get("n_days", 0),
                    _mir.get("n_rows_total", 0), _mir.get("n_multi_leg", 0)))
        L.append("- 유령청산했다면 %+.2fpt vs 버틴 실제 %+.2fpt → **delta %+.2fpt** "
                 "(평균 %+.3f / 중앙값 %+.3f, 유령 유리 %d/%d건)"
                 % (_mir.get("ghost_pt_sum", 0.0), _mir.get("held_pt_sum", 0.0),
                    _mir.get("delta_pt_sum", 0.0), _mir.get("delta_pt_avg", 0.0),
                    _mir.get("delta_pt_median", 0.0),
                    _mir.get("favorable_n", 0), _mir["n"]))
        L.append("- 유령청산 손익이 양수인 건: **%d/%d** — 스파이크-되돌림 익절 가설의 직접 지표"
                 % (_mir.get("ghost_positive_n", 0), _mir["n"]))
        if _mir.get("paired_days"):
            L.append("- 일자단위(313차): %s/%s일 유령 우세, 평균 %+.3fpt, **부호검정 p=%s**"
                     % (_mir.get("days_positive"), _mir.get("paired_days"),
                        _mir.get("mean_diff", 0.0), _mir.get("sign_p")))
        if _mir.get("mean_median_split"):
            L.append("- 🔴 **평균과 중앙값의 부호가 다르다** (%+.3f vs %+.3f) — 소수 관측이 "
                     "평균을 끌고 있다는 뜻이다. **평균만 보고 결론 내지 말 것**(313차)."
                     % (_mir.get("delta_pt_avg", 0.0), _mir.get("delta_pt_median", 0.0)))
        if _mir.get("by_path"):
            L.append("")
            L.append("| 조이기 경로 | 건수 | delta 합 |")
            L.append("|---|---|---|")
            for _k, _v in sorted((_mir.get("by_path") or {}).items()):
                L.append("| `%s` | %s | %+.2fpt |" % (_k, _v["n"], _v["delta_pt_sum"]))
        L.append("")
        L.append("> ⚠ **주판정과 합치지 않는다 — verdict도 내지 않는다.** 세 가지가 다르다:")
        L.append("> ① **반사실 비대칭** — 주판정의 반사실은 \"`stop_eval`로 계속\"이라는 단일")
        L.append("> 규칙이지만, 미러의 실제값은 억제 이후 **모든 청산 로직**(TP2·트레일·15:10")
        L.append("> 강제청산)의 합이라 그것들과 교락돼 있다. \"억제의 순수 효과\"가 아니다.")
        L.append("> ② **시점 교락** — 두 부분표본은 처치 시점이 갈린다(유령 발생기 vs 억제기).")
        L.append("> 436차가 `827bd04` 교락 때문에 [50]을 PRE/POST 비교로 등록하지 **않은** 것과")
        L.append("> 같은 함정이다.")
        L.append("> ③ **`cur_price` 근사 편향** — 실측 유령 청산의 체결 슬리피지는 평균")
        L.append("> −2.708pt(유리)였으므로 이 근사는 유령을 **과소평가**한다(보수적 방향).")
        L.append("")
        L.append("> 판정으로의 승격은 §9 주간회의 안건이다 — 합격선을 여기서 만들지 않는다(313차).")
        L.append("")
    if pse.get("recommendation"):
        L.append("- **권고**: %s" % pse["recommendation"])
        L.append("")
    L.append("> **판정 전에 가드를 켜지 말 것** — 켜는 순간 이 표본이 더 안 쌓인다.")
    L.append("> 라이브는 계측만 하도록 배선돼 있다(`main.py` tp1_breakeven →")
    L.append("> `mark_stop_tightened_shadow`). 전환은 그 한 줄을 `_mark_stop_tightened`로")
    L.append("> 바꾸는 것이고, **SUPPORTS_HYP면 전환이 아니라 정책 승격**이 처방이다.")
    L.append("")
    L.append("---")
    L.append("")

    L.append("## [36] 체크리스트 승격 경로별 우열 (MW0602 424차 후속)")
    L.append("")
    L.append("0803 정기점검 P2의 *\"앙상블 X를 A로 올리는 경로에 하한 조건 추가\"* 제안을")
    L.append("검정한다. **0804 실측은 정반대였다** — 그래서 그 제안은 이 채널 판정까지 보류다.")
    L.append("")
    if gxp.get("by_path"):
        L.append("| 경로 | 포지션 | 거래일 | 승률 | 평균 | 누적 |")
        L.append("|---|---|---|---|---|---|")
        for _k in ("X→A", "C→A", "C→C"):
            _v = (gxp.get("by_path") or {}).get(_k)
            if not _v:
                continue
            L.append("| **%s** | %d | %d | %.1f%% | %s원 | %s원 |" % (
                _k, _v["n"], _v.get("days", 0), _v["win_rate"] * 100,
                format(int(_v["avg_pnl_krw"]), ","),
                format(int(_v["total_pnl_krw"]), ",")))
        L.append("")
    else:
        L.append("- %s" % (gxp.get("reason") or "표본 없음"))
        L.append("")
    if gxp.get("paired_days"):
        L.append("- 일자단위(313차): 짝지은 %s일, 평균 격차 %s원, **부호검정 p=%s**"
                 % (gxp.get("paired_days"), _fmt_krw(gxp.get("mean_diff", 0.0)), gxp.get("sign_p")))
        L.append("")
    if gxp.get("recommendation"):
        L.append("- **권고**: %s" % gxp["recommendation"])
        L.append("")
    L.append("> `raw_grade`가 NULL인 구버전 행은 경로 판별이 불가능해 **전량 제외**한다 —")
    L.append("> 승격/미승격을 섞으면 이 채널이 재려는 값을 못 잰다.")
    L.append("")
    L.append("---")
    L.append("")

    L.append("## [37] mean-revert 적자 — 일자단위 재검정 (MW0602 424차 후속)")
    L.append("")
    L.append("⚠ **[29] mean_revert_size_watch와 모집단이 같다. 중복이 아니라 브레이크다.**")
    L.append("[29]는 포지션 단위 승률 격차로 판정하는데, 0804 실측에서 두 축이 갈렸다:")
    L.append("")
    L.append("| 축 | 결과 |")
    L.append("|---|---|")
    L.append("| 포지션 누적 | mean-revert 54건 **-1,455,546원** (neutral +2,303,166 / trend +778,965) |")
    L.append("| 일자단위 짝지은 검정 | 7거래일, 평균차 -1.63pt, t=-1.13, 부호 2/7, **p=0.4531 (미유의)** |")
    L.append("")
    L.append("누적 -145만원은 극적으로 보이지만 일자단위로는 재현되지 않는다 — 313차가")
    L.append("막으려던 바로 그 패턴이다(372차 PSI 재보정의 이상치 착시와 동형).")
    L.append("")
    if hmd.get("n_mean_revert"):
        L.append("- mean-revert **%s건** 누적 %s원 / 그 외 %s건 누적 %s원" % (
            hmd.get("n_mean_revert"),
            format(int((hmd.get("cum_krw") or {}).get("mean_revert", 0) or 0), ","),
            hmd.get("n_other"),
            format(int((hmd.get("cum_krw") or {}).get("other", 0) or 0), ",")))
        L.append("- 짝지은 거래일 **%s일** (단일버킷일 %s일 제외 — 그날은 레짐 통제가 안 된다)"
                 % (hmd.get("paired_days", 0), hmd.get("unpaired_days", 0)))
        if hmd.get("paired_days"):
            L.append("- 평균차 %+.2fpt · MR 우세 %s/%s일 · **부호검정 p=%s**%s" % (
                hmd.get("mean_diff", 0.0), hmd.get("days_positive", 0),
                hmd.get("paired_days"), hmd.get("sign_p"),
                (" · t=%s" % hmd["t_stat"]) if hmd.get("t_stat") is not None else ""))
    else:
        L.append("- %s" % (hmd.get("reason") or "표본 없음"))
    L.append("")
    if hmd.get("recommendation"):
        L.append("- **권고**: %s" % hmd["recommendation"])
        L.append("")
    L.append("> **판독 규칙 (관측 전 고정 — settings 채널 주석과 동일)**")
    L.append("> ")
    L.append("> | [29] | [37] | 조치 |")
    L.append("> |---|---|---|")
    L.append("> | FAIL | PASS | **보류.** 누적 수치만으로 움직이지 말 것 |")
    L.append("> | FAIL | SUPPORTS_HYP | 두 축 합치 — 주간회의 안건 승격 가능 |")
    L.append("> | PASS | SUPPORTS_HYP | 승률은 같은데 손익 크기가 갈림 — 재조사 |")
    L.append("> ")
    L.append("> 처방 축은 [29]와 동일하다 — qty=1에서 사이즈 축소는 no-op이므로")
    L.append("> **등급 강등/임계값 이동** 축으로 설계할 것(`sizing_prescription_axis` 참조).")
    L.append("")
    L.append("---")
    L.append("")

    L.append("## [38] ProfitGuard-L1 피크 트레일링 (MW0602 426차)")
    L.append("")
    L.append("**희귀사건 채널이다.** 0804 점검이 L1을 \"오늘 최대 공로자\"로 적었으나")
    L.append("검증에서 **과장으로 확인**됐다 — 캠페인 전체에서 구속력 있는 발동은 1회뿐이고,")
    L.append("그 하루의 차단 40건 반사실은 TP1 24 / STOP 16, 누적 **-1.87pt(-93,492원)** 로")
    L.append("박빙이었다. 판정을 서두르지 않도록 min_activations를 걸어 둔다.")
    L.append("")
    if _pgc.get("diverged"):
        L.append("> 🔴 **운영 파라미터가 코드에 없다.** 라이브 값은 `%s`에서 오며")
        L[-1] = L[-1] % _pgc.get("prefs_path", "—")
        L.append("> 대시보드에서 **장중 변경이 가능**하다 — 판정 기준선이 코드 리뷰로")
        L.append("> 보이지 않고 세션 중에 바뀔 수도 있다는 뜻이다.")
        L.append("> ")
        L.append("> | | 발동금액 | 비율 |")
        L.append("> |---|---|---|")
        L.append("> | **운영(prefs)** | **%s원** | **%.0f%%** |" % (
            format(int(_pgc.get("activation_krw", 0)), ","),
            float(_pgc.get("ratio", 0)) * 100))
        L.append("> | 코드 기본값 | %s원 | %.0f%% |" % (
            format(int(_pgc.get("code_activation_krw", 0)), ","),
            float(_pgc.get("code_ratio", 0)) * 100))
        L.append("> ")
        L.append("> prefs 최종수정: %s · **아래 수치는 전부 운영값 기준**이다."
                 % _pgc.get("prefs_mtime", "—"))
        L.append("")
    L.append("- 발동 %s회 (그중 **구속 %s회 / %s거래일**) · 전체 %s거래일" % (
        pgl.get("n_fire", "—"), pgl.get("n_binding", "—"),
        pgl.get("n_binding_days", "—"), pgl.get("n_days_total", "—")))
    if pgl.get("fires"):
        L.append("")
        L.append("| 거래일 | 피크 | 발동 | 발동후 진입 | 그 손익 | 구속? |")
        L.append("|---|---|---|---|---|---|")
        for f in pgl["fires"]:
            L.append("| %s | %s원 | %s | %s건 | %s원 | %s |" % (
                f["day"], format(int(f["peak_krw"]), ","), f["halt_ts"][11:16],
                f["n_after"], format(int(f["after_pnl_krw"]), ","),
                "**예**" if f["binding"] else "아니오"))
        L.append("")
        L.append("> **발동했다고 다 같은 발동이 아니다.** 발동 시각 뒤에 진입 기회가")
        L.append("> 없었으면(장 마감·14:50 신규금지) 무해무익이다 — 실제로 07-20이 그랬다")
        L.append("> (14:56 발동, 마지막 진입 14:33). 그래서 표본 단위는 **구속 발동**이다.")
        L.append("")
    if pgl.get("cf_n"):
        _o = pgl.get("cf_outcome") or {}
        L.append("- 차단 신호 반사실(%s분 창): **%s건** · TP1 %s / STOP %s / 무결정 %s" % (
            (VALIDATION_CAMPAIGN.get("profit_guard_l1_watch") or {}).get("cf_window_min", 30),
            pgl.get("cf_n"), _o.get("TP1", 0), _o.get("STOP", 0), _o.get("NEITHER", 0)))
        L.append("- 누적 **%+.2fpt** (건당 %+.3fpt) — **(+)면 차단이 손해, (-)면 이득**" % (
            pgl.get("cf_total_pt", 0.0), pgl.get("cf_avg_pt", 0.0)))
        if pgl.get("paired_days"):
            L.append("- 일자단위(313차): %s/%s일, p=%s" % (
                pgl.get("days_positive"), pgl.get("paired_days"), pgl.get("sign_p")))
        L.append("")
    if pgl.get("resume_delay"):
        L.append("**(d) 재개 조건 — 현재는 재개가 없다.** `_TrailingGuard.is_halted`가")
        L.append("`reset_daily()`까지 유지돼 발동일은 장 마감까지 신규진입이 막힌다.")
        L.append("아래는 \"발동 N분 뒤 재개했다면 그 뒤 차단분이 얼마였나\"이다.")
        L.append("")
        L.append("| 재개 지연 | 차단 유지분 | 그 손익 | 재개 후 진입분 | 그 손익 |")
        L.append("|---|---|---|---|---|")
        for _k in sorted(pgl["resume_delay"], key=lambda x: int(x)):
            _v = pgl["resume_delay"][_k]
            L.append("| **%s분**%s | %s건 | %+.2fpt | %s건 | %+.2fpt |" % (
                _k, " (현행)" if _k == "0" else "",
                _v.get("n_kept", 0), _v.get("kept_pt", 0.0), _v["n"], _v["pt"]))
        L.append("")
        L.append("> **두 열을 함께 읽어야 한다.** \"차단 유지분 손익\"이 (-)면 그 구간을")
        L.append("> 막은 것이 이득이고, \"재개 후 진입분 손익\"이 (+)면 재개가 이득이다.")
        L.append("> 즉 **(-, +) 조합이 나오는 지연이 최적**이다 — 나쁜 구간은 막고 좋은")
        L.append("> 구간은 되찾는다.")
        L.append("> ")
        L.append("> ⚠ **신호 수 ≠ 진입 수다.** 연속 분봉의 같은 방향 신호가 그대로 세어져")
        L.append("> 있고, 실제로는 포지션 보유·쿨다운·14:50 신규금지가 걸린다. 그래서 위")
        L.append("> pt 합계는 **상한**이지 기대손익이 아니다([6]·[7]과 같은 한계).")
        L.append("> 반사실 자체도 상방은 TP1에서 자르고 하방은 스톱까지 세는 비대칭이 있다.")
        L.append("")
    if pgl.get("sweep"):
        L.append("**(c) 임계 스윕 — 전 거래일 소급 재현.** 이 축은 반사실이 아니다:")
        L.append("발동하지 않았던 날은 그 뒤 진입이 실제로 체결돼 **실현손익이 남아 있다.**")
        L.append("")
        L.append("| 발동금액 | 비율 | 발동 | 구속 | 차단될 포지션 | 지킨 금액 |")
        L.append("|---|---|---|---|---|---|")
        for s in pgl["sweep"]:
            _cur = (abs(s["activation_krw"] - float(_pgc.get("activation_krw", -1))) < 1e-9
                    and abs(s["ratio"] - float(_pgc.get("ratio", -1))) < 1e-9)
            L.append("| %s%s | %.0f%% | %s | %s | %s | %s원 |" % (
                format(int(s["activation_krw"]), ","), " **(운영)**" if _cur else "",
                s["ratio"] * 100, s["n_fire"], s["n_binding"],
                s["n_blocked_pos"], format(int(s["saved_krw"]), ",")))
        L.append("")
        L.append("> \"지킨 금액\"이 (+)면 차단이 손실을 막은 것, (-)면 이익을 놓친 것이다.")
        L.append("> **전 격자에서 0이면 L1은 사실상 무발동**이라는 뜻이다 — 임계를 조이는")
        L.append("> 논의보다 \"이 레이어가 지금 무엇을 하고 있는가\"가 먼저다.")
        L.append("")
    if pgl.get("reason"):
        L.append("- %s" % pgl["reason"])
        L.append("")
    L.append("> **판정을 서두르지 말 것.** 실측 발동빈도(16거래일에 구속 1회)로는")
    L.append("> `min_activations=5`가 약 **4개월** 스케일이다([8] KellySkip과 같은 계열).")
    L.append("> 그 사이에 판정을 흉내내면 단일일 관측이 정책이 된다 — 0804에 실제로")
    L.append("> 그럴 뻔했고, 이 채널은 그 재발을 막으려고 만들었다.")
    L.append("")
    L.append("---")
    L.append("")

    L.append("## [39] confidence 판별력 (MW0602 427차)")
    L.append("")
    L.append("**min_conf 자체가 아니라 그 선행조건을 잰다.** 0804 §P2는 \"동적 min_conf가")
    L.append("랜덤 기준선(0.33)까지 내려앉아 무력화됐다\"를 문제로 제기했는데, 조사 결과")
    L.append("**문제 제기의 방향이 틀렸다** — 게이트는 정보 없는 신호를 걸러낼 수 없다.")
    L.append("")
    L.append("| 0804 조사 실측 | 결과 |")
    L.append("|---|---|")
    L.append("| min_conf 0.40 상향 | 손익 **−407,558원** |")
    L.append("| min_conf 0.45 상향 | 손익 **−749,942원** |")
    L.append("| 잘려나간 진입 승률 | **62~63%** = 전체 승률 **63.0%** |")
    L.append("| 설계값 0.54 복원 시 | 진입 81건 → **1건** (진입 conf 최댓값 0.579) |")
    L.append("")
    L.append("> 잘려나가는 진입의 승률이 전체와 같다는 것이 직접 증거다 — 게이트가 품질")
    L.append("> 필터가 아니라 **무작위 샘플러**로 작동한다. 그래서 질문을 바꿨다:")
    L.append("> \"min_conf를 얼마로 할까\"가 아니라 **\"conf가 정보를 갖기 시작했는가\"**.")
    L.append("")
    _cr39 = VALIDATION_CAMPAIGN.get("conf_discrimination_watch") or {}
    L.append("**(B) 모델축** — `predictions.confidence` vs `correct` (두꺼운 축)")
    L.append("")
    if _cdm.get("n"):
        L.append("- n=**%s**건 / %s거래일 · 퇴역 호라이즌 %s 제외 %s건" % (
            format(_cdm["n"], ","), _cdm.get("n_days", "—"),
            cdw.get("excluded_horizons") or "—",
            format(cdw.get("n_pred_excluded", 0), ",")))
        L.append("- 하위절반 %.1f%% vs 상위절반 %.1f%% → **격차 %+.2f%%p** (임계 %.1f%%p)" % (
            float(_cdm.get("lo_acc", 0)) * 100, float(_cdm.get("hi_acc", 0)) * 100,
            _cdm.get("gap_pp", 0.0), float(_cr39.get("model_gap_min_pp", 3.0))))
        _s = _cdm.get("stratified") or {}
        if _s.get("paired_days"):
            L.append("- 일자 층화(같은 날 안에서 상/하위 분할): %s/%s일 양수, "
                     "**부호검정 p=%s**" % (
                         _s.get("days_positive"), _s.get("paired_days"), _s.get("sign_p")))
    else:
        L.append("- 표본 없음")
    L.append("")
    L.append("> ⚠ **30m을 제외한다.** 296차가 앙상블·게이트에서 퇴역시킨 호라이즌인데")
    L.append("> `predictions`에는 계속 쌓인다. 실측으로 `conf≥0.60` 구간의 **88%가 30m**")
    L.append("> 이라, 포함하면 퇴역 모델이 판정을 끌고 간다.")
    L.append("")
    L.append("**(A) 앙상블축** — min_conf가 **실제로 게이트하는 값** (얇은 축)")
    L.append("")
    if _cde.get("n_win") and _cde.get("n_loss"):
        L.append("- 승 %s건 평균 conf **%.4f** / 패 %s건 **%.4f** → **격차 %+.4f** "
                 "(임계 %.3f · Cohen d=%s)" % (
                     _cde["n_win"], _cde.get("win_conf", 0), _cde["n_loss"],
                     _cde.get("loss_conf", 0), _cde.get("gap", 0),
                     float(_cr39.get("ens_gap_min", 0.025)), _cde.get("cohen_d", "—")))
        L.append("- 진입 conf 표준편차 %s — 임계 %.3f은 약 %.2f sd에 해당한다" % (
            _cde.get("conf_sd", "—"), float(_cr39.get("ens_gap_min", 0.025)),
            float(_cr39.get("ens_gap_min", 0.025)) / float(_cde.get("conf_sd") or 1)))
        _s2 = _cde.get("stratified") or {}
        if _s2.get("paired_days"):
            L.append("- 일자단위(승·패가 둘 다 있는 날): %s/%s일, **p=%s**" % (
                _s2.get("days_positive"), _s2.get("paired_days"), _s2.get("sign_p")))
    else:
        L.append("- 승 또는 패 표본이 없어 격차를 낼 수 없다")
    # [MW0602 430차 / P0-1] 이 축은 ensemble_decisions.confidence를 쓰므로
    # conf 스케일 불연속의 직접 영향권이다. 다만 **무엇이 오염되고 무엇이 면역인지**를
    # 명시해야 한다 — 안 그러면 다음 세션이 채널 전체를 불신하거나(과잉) 아무것도
    # 조정하지 않거나(과소) 둘 중 하나로 흐른다.
    if _conf_scale_breaks_in(VALIDATION_CAMPAIGN.get("start_date", "")):
        L.append("")
        L.extend(_conf_scale_break_lines(VALIDATION_CAMPAIGN.get("start_date", "")))
        L.append("> **이 채널에 미치는 영향**: 위 `격차`·`표준편차`는 경계 양쪽의 서로")
        L.append("> 다른 스케일을 한 통에 넣은 값이라 **수준·분산이 오염**된다. 반면")
        L.append("> 바로 아래 **일자단위(같은 날 안에서 승/패 비교)는 면역**이다 —")
        L.append("> 하루 안에서는 스케일이 하나이기 때문이다. **판정은 일자단위를 볼 것.**")
        L.append("> ")
        L.append("> **모델축(`predictions.confidence`)은 이 경계에서 계단 변화가 없다**")
        L.append("> — 430차 실측 1m/3m/5m 07-27~08-04 전 구간 0.36~0.41로 연속.")
        L.append("> 호라이즌 보정기도 **같은 축퇴 가드를 쓰지만**(같은 클래스다) 영향이")
        L.append("> 작은 이유는 입력 분포가 다르기 때문이다: 앙상블축에는 가중치 붕괴가")
        L.append("> 만드는 인위적 `raw≈1.0` 행이 21%나 있어 적용/미적용 차이가 0.33↔0.85로")
        L.append("> 벌어지지만, 호라이즌 raw는 기저율 근처(~0.33~0.40)라 보정을 걸든 말든")
        L.append("> 출력이 비슷하다. **\"가드를 안 쓴다\"가 아니라 \"입력이 극단이 아니다\"** —")
        L.append("> 붕괴 구조가 바뀌면 모델축도 영향권에 들어올 수 있으므로 재확인할 것.")
    _jo = cdw.get("join_offset_min") or {}
    L.append("- 진입↔결정 매칭 **%s/%s (%.1f%%)** · 오프셋 분포 %s" % (
        cdw.get("n_matched"), cdw.get("n_positions_total"),
        float(cdw.get("match_rate", 0)) * 100,
        " / ".join("%s분 %s건" % (k, v) for k, v in sorted(_jo.items())) or "—"))
    if cdw.get("n_unmatched"):
        L.append("- 🟡 **미매칭 %s건** — T/T-1 두 분과 방향 일치를 다 봐도 결정행을 "
                 "찾지 못했다. 발생일: %s" % (
                     cdw.get("n_unmatched"),
                     ", ".join(cdw.get("unmatched_days") or []) or "—"))
    L.append("")
    L.append("> **`-1분` 오프셋은 결함이 아니라 정상이다.** 파이프라인이 `T:52` 근방에")
    L.append("> 주문을 내고 체결 확인이 `T+1:00~:09`에 도착하면 `trades.entry_ts`(체결")
    L.append("> 시각)가 결정 분보다 1분 뒤가 된다. 427차 초판은 분 단위 정확 조인이라")
    L.append("> **이 19건을 통째로 잃고 매칭률 81%로 보고했다** — 데이터가 없는 게")
    L.append("> 아니라 키가 어긋난 것이었다(방향은 100/100 일치).")
    L.append("> ")
    L.append("> **`-1분` 비중이 갑자기 늘면 체결 확인 지연이 커진 것이다** — 집행 품질")
    L.append("> 신호로 함께 볼 것.")
    L.append("")
    if cdw.get("recommendation"):
        L.append("- **권고**: %s" % cdw["recommendation"])
        L.append("")
    # 임계는 settings에서 읽는다 — 본문에 상수를 복붙하면 값과 설명이 갈라진다.
    _mg = float(_cr39.get("model_gap_min_pp", 3.1))
    _eg = float(_cr39.get("ens_gap_min", 0.025))
    L.append("> **임계는 검출력에서 유도했다**(관측 전 고정). 모델축은 n≈14,770 절반분할의")
    L.append("> 격차 SE가 0.78%%p라 검출하한(1.96SE)이 1.52%%p이고, 임계 %.1f%%p는 그 "
             "**2배(3.04%%p) 이상**이다 —" % _mg)
    L.append("> 매주 들여다보는 채널이라 경계선 값이 우연히 넘는 것을 막을 여유가 필요하다.")
    L.append("> 앙상블축 %.3f은 진입 conf sd 0.0556 기준 **Cohen d≈%.2f**로, 이보다 작으면"
             % (_eg, _eg / 0.0556))
    L.append("> 승/패 conf 분포가 거의 완전히 겹쳐 어떤 임계도 둘을 가르지 못한다.")
    L.append("> ")
    L.append("> **두 축 모두 효과크기 AND 일자단위 검정을 함께 요구한다.** 0804에")
    L.append("> pooled z=−4.95가 일자단위로는 p=0.42였던 전례를 그대로 겪었다")
    L.append("> (표본의 56%가 하루, 88%가 퇴역 30m).")
    L.append("> ")
    L.append("> **SUPPORTS_HYP로 바뀌는 날이 min_conf를 다시 논할 시점이다.** 그때도")
    L.append("> 설계값 0.54~0.67을 그대로 쓰면 안 된다 — 구 conf 분포 기준이라 진입이")
    L.append("> 사라진다. 그 시점의 분포로 새로 잡을 것.")
    L.append("")
    L.append("---")
    L.append("")

    L.append("## [40] 방향 선택의 가치 (MW0602 428차)")
    L.append("")
    L.append("**같은 진입 시각·같은 청산 기하**에서 시스템의 실제 방향과 **동전던지기**를")
    L.append("비교한다. 두 팔이 같은 시뮬을 통과하므로 차이는 오직 **방향 선택의 기여분**이다.")
    L.append("구현: `scripts/random_entry_control.py` (오프라인·읽기 전용).")
    L.append("")
    if dvw.get("error"):
        L.append("- ⚠ 실행 실패: `%s`" % dvw.get("error"))
    elif dvw.get("n_usable"):
        L.append("- 표본: 진입 **%s건** 중 %s건 시뮬 가능 / **%s거래일**" % (
            dvw.get("n_entries"), dvw.get("n_usable"), dvw.get("n_days")))
        L.append("")
        L.append("| | 손익 | 승률 |")
        L.append("|---|---|---|")
        L.append("| **실제 방향** | **%+.2fpt** | %.1f%% |" % (
            dvw.get("actual_pt", 0.0), float(dvw.get("actual_win_rate", 0)) * 100))
        L.append("| 무작위 %s회 (중앙) | %+.2fpt | %.1f%% |" % (
            dvw.get("trials"), dvw.get("random_median_pt", 0.0),
            float(dvw.get("random_mean_win_rate", 0)) * 100))
        L.append("| 무작위 5~95%% 구간 | %+.2f ~ %+.2fpt | — |" % (
            dvw.get("random_p05_pt", 0.0), dvw.get("random_p95_pt", 0.0)))
        L.append("")
        L.append("- 실제가 무작위를 상회한 비율 **%.1f%%** → **단측 p = %s**" % (
            float(dvw.get("beats_random_share", 0)) * 100, dvw.get("p_one_sided")))
        L.append("- 일자단위(313차): **%s/%s일**에서 그날 무작위 중앙값 상회 (임계 %.0f%%)" % (
            dvw.get("days_beating_random"), dvw.get("days_evaluated"),
            float((VALIDATION_CAMPAIGN.get("direction_value_watch") or {})
                  .get("min_day_win_share", 0.70)) * 100))
    else:
        L.append("- %s" % (dvw.get("reason") or "표본 없음"))
    L.append("")
    if dvw.get("recommendation"):
        L.append("- **권고**: %s" % dvw["recommendation"])
        L.append("")
    L.append("> ⚠ **절대 수준 인용 금지.** 시뮬은 단순화돼 있다 — TP1(33% 부분익절) +")
    L.append("> 본전이동 + TP2 + 하드스톱 + 종가청산이 전부이고, **트레일링 계단·틱 청산·")
    L.append("> 손절계단화·ProfitGuard·수수료/슬리피지가 없다.** 실제 손익을 재현하지")
    L.append("> 못하며 **유효한 것은 두 팔의 비교뿐**이다(같은 시뮬이라 그 비교는 공정).")
    L.append("> 비용을 빼지 않은 것도 의도적이다 — 양쪽에 동일해 비교에서 상쇄된다.")
    L.append("> ")
    L.append("> **따라서 이 채널은 \"시스템 전체의 엣지\"를 재지 않는다. 방향 축 하나만**")
    L.append("> **잰다.** 실제 손익이 양수인데 여기서 음수가 나오는 것은 모순이 아니다 —")
    L.append("> 라이브 기하가 이 시뮬보다 정교하기 때문이다.")
    L.append("> ")
    L.append("> **이 채널이 연구 우선순위를 좌우한다.** `docs/미륵이고도화3` 로드맵의")
    L.append("> 이월 D·E·G는 전부 **방향 피처 재배치**이고, [40]이 REJECTS로 굳어 있는")
    L.append("> 동안 그것들은 소수점 싸움이다. 계획서 §5-1이 지적한 *\"3단계에서 성공의")
    L.append("> 정의가 비어 있다\"* 는 공백을 이 채널이 메운다 — **[40]의 전환이 곧**")
    L.append("> **성공의 정의다.**")
    L.append("")
    L.append("---")
    L.append("")

    L.append("## [41] 청산 측 학습기 게이지 (MW0602 428차)")
    L.append("")
    L.append("**판정 채널이 아니라 게이지다** ([33]과 같은 부류). \"언제 학습을 시작할 수")
    L.append("있는가\"를 매주 찍는다. 학습기가 **전부 진입 측**이라는 것이 계기다 —")
    L.append("GBM/RF·SGD·`meta_confidence`·`meta_labeling`이 모두 **방향 적중**을 학습하고,")
    L.append("**청산은 전부 규칙**(ATR 고정배수·트레일링·손절계단화)이다. 그런데 425차는")
    L.append("스톱이 16건 중 14건 옳았음을, [40]은 방향이 동전던지기와 구분되지 않음을")
    L.append("보였다 — **돈은 청산에서 온다.**")
    L.append("")
    _lb = emw.get("labels") or {}
    _rd = emw.get("readiness") or {}
    if emw.get("error"):
        L.append("- ⚠ 실행 실패: `%s`" % emw.get("error"))
    else:
        L.append("- 라벨 표본: **%s행** / %s포지션 / %s거래일 (포지션당 %s행)" % (
            _lb.get("n_rows", "—"), _lb.get("n_positions", "—"),
            _lb.get("n_days", "—"), _lb.get("rows_per_position", "—")))
        L.append("- 양성률: `y_hold_better` %.1f%% · `y_tp1_first` %.1f%%" % (
            float(_lb.get("y_hold_better_rate", 0)) * 100,
            float(_lb.get("y_tp1_first_rate", 0)) * 100))
        L.append("")
        L.append("| 게이지 | 현재 | 요건 |")
        L.append("|---|---|---|")
        L.append("| EPV (events per variable) | **%s** | ≥ %s |" % (
            _rd.get("epv", "—"), _rd.get("min_events_per_variable", "—")))
        L.append("| 포지션 | **%s** | ≥ %s (**%s건 부족**) |" % (
            _rd.get("n_positions", "—"), _rd.get("positions_required", "—"),
            _rd.get("positions_short", "—")))
        L.append("| 거래일 | %s | ≥ %s |" % (
            _rd.get("n_days", "—"), _rd.get("min_days", "—")))
        L.append("| 피처 수 | %s | — |" % _rd.get("n_features", "—"))
        L.append("")
        if emw.get("eta_trading_days"):
            L.append("- 실측 진입속도 **%s건/거래일** 기준 잔여 약 **%s거래일**" % (
                emw.get("positions_per_day"), emw.get("eta_trading_days")))
        L.append("")
        L.append("> 🔧 **[MW0601 440차] 라벨 기하 결함 수정 — 이전 주 수치와 비교 금지.**")
        L.append("> 라벨러가 TP1을 `ATR × ATR_TP1_MULT`(=**1.0**, \"entry_horizon 미지정 시")
        L.append("> fallback\")로 잡고 있었다. 라이브 TP1은 374/387차부터 호라이즌별")
        L.append("> (`1m .3 / 3m .5 / 5m .7`)이고 hurst 레짐 배수까지 곱하므로 라벨러의 TP1")
        L.append("> 거리는 **1.4~3.3배 과대**였다(표본 호라이즌: 3m 57 / 5m 49 / 1m 11건 —")
        L.append("> **전건 영향권**). 스톱에도 hurst 배수가 빠져 있었다.")
        L.append("> ")
        L.append("> 오염 범위: `dist_tp1_atr`·`tp1_done` 피처와 `y_tp1_first` 라벨.")
        L.append("> 수정 후 `y_tp1_first` 양성률 **42.4% → 53.8%**로 올랐고,")
        L.append("> `y_hold_better`(주 라벨)는 TP1 기하와 무관해 **36.6% 불변**이다 —")
        L.append("> 이 불변이 수정이 의도한 범위에만 닿았다는 검산이다.")
        L.append("> ")
        L.append("> **왜 표본을 더 기다리기 전에 고쳤나**: 267포지션을 더 모아도 잘못")
        L.append("> 라벨된 표본이 늘 뿐이다. 기하는 이제 `scripts/exit_replay.geometry()`")
        L.append("> 단일 소스에서 온다 — 재생기와 라벨러가 다른 기하를 쓰면 같은 표류가")
        L.append("> 반복된다(432차 \"3중 정의\" 교훈).")
        if emw.get("trained"):
            L.append("- 🔶 **학습이 열렸다** — OOF AUC **%s** (정확도 %s / 기준선 %s)" % (
                emw.get("oof_auc"), emw.get("oof_acc"), emw.get("baseline_acc")))
    if emw.get("config_drift"):
        L.append("- 🔴 **설정 표류**: `%s`가 settings와 `exit_classifier.py` 사이에서 "
                 "다르다. 게이지가 거짓말을 한다 — 둘을 맞출 것"
                 % ", ".join(emw["config_drift"]))
    L.append("")
    if emw.get("recommendation"):
        L.append("- **권고**: %s" % emw["recommendation"])
        L.append("")
    L.append("> **왜 스스로 학습을 거부하는가.** 395행처럼 보이지만 행은 같은 포지션 안에서")
    L.append("> 강하게 상관돼 있어(포지션당 4.03행) **유효표본은 포지션 수**다. 피처 14개·")
    L.append("> 양성률 32%에서 EPV는 2.25로 통상 기준 10의 **1/5**이다. 이 상태로 학습하면")
    L.append("> 학습이 아니라 암기다 — 그래서 `exit_classifier`가 **학습 자체를 거부**하고")
    L.append("> 얼마나 더 필요한지만 돌려준다.")
    L.append("> ")
    L.append("> 학습이 열리면 **`GroupKFold(groups=entry_ts)`** 를 쓴다. 같은 포지션의 행이")
    L.append("> 학습/검증에 갈라져 들어가면 누출이라 행 단위 KFold는 쓰지 않는다.")
    L.append("> ")
    L.append("> **이 축의 구조적 이점**: 회전율을 **늘리지 않는다**(진입 수 그대로, 청산")
    L.append("> 시점만 변경) → 189회 검정을 전멸시킨 왕복비용 0.133pt를 추가 지불하지")
    L.append("> 않는다. 그리고 **방향 예측이 필요 없다**(이미 진입한 포지션의 조건부 문제).")
    L.append("> ")
    L.append("> ⚠ **라이브 청산에 배선하지 않는다.** `exit_model_shadow`에 기록만 한다.")
    L.append("> 배선은 판정 후 주간회의 결정이며(§9), 계획서 2장이 경고한 \"기준선을")
    L.append("> 흔드는 변경\"이므로 **D-day(08-14) 스냅샷 이후**에 논의할 것.")
    L.append("")
    L.append("---")
    L.append("")

    L.append("## [42] 타점(진입 시각)의 가치 (MW0602 429차)")
    L.append("")
    L.append("**[40]의 빠진 축이다.** [40]은 진입 시각을 고정한 채 방향만 뒤집어")
    L.append("방향 축만 격리했다. 여기는 **타점 축**을 격리한다 — 3팔 비교에서")
    L.append("**`B − C`가 체크리스트/게이트가 고른 분(minute)의 기여분**이다.")
    L.append("")
    if etv.get("error"):
        L.append("- ⚠ 실행 실패: `%s`" % etv.get("error"))
    elif etv.get("arm_b_median_pt") is not None:
        L.append("| 팔 | 손익 | 5~95% |")
        L.append("|---|---|---|")
        L.append("| A) 실제시각 + **실제방향** | %+.2fpt | — |" % etv.get("arm_a_pt", 0.0))
        L.append("| B) 실제시각 + 무작위방향 | %+.2fpt | %+.2f ~ %+.2f |" % (
            etv.get("arm_b_median_pt", 0.0), etv.get("arm_b_p05_pt", 0.0),
            etv.get("arm_b_p95_pt", 0.0)))
        L.append("| C) **무작위시각** + 무작위방향 | %+.2fpt | %+.2f ~ %+.2f |" % (
            etv.get("arm_c_median_pt", 0.0), etv.get("arm_c_p05_pt", 0.0),
            etv.get("arm_c_p95_pt", 0.0)))
        L.append("")
        L.append("- **타점 기여 (B−C) = %+.2fpt** · B가 C를 이긴 시행 %s/%s (**%.1f%%**)"
                 % (etv.get("timing_gain_pt", 0.0), etv.get("trials_b_over_c"),
                    etv.get("trials"), float(etv.get("b_over_c_share", 0)) * 100))
        L.append("- **짝지은 부호검정 p = %s** (타점에 정보가 없으면 50%%)"
                 % etv.get("sign_p"))
        L.append("- 후보 분봉 %s개 (%s~%s, 거래일별 건수는 실제와 일치)" % (
            etv.get("n_candidate_bars"),
            (etv.get("entry_window") or ["—", "—"])[0],
            (etv.get("entry_window") or ["—", "—"])[1]))
    else:
        L.append("- %s" % (etv.get("reason") or "표본 없음"))
    L.append("")
    if etv.get("recommendation"):
        L.append("- **권고**: %s" % etv["recommendation"])
        L.append("")
    L.append("> **짝지은 검정을 쓴다.** 같은 시행에서 B·C를 뽑아 부호를 센다 — 두 팔이")
    L.append("> 같은 시장 데이터를 공유해 양의 상관을 가지므로, 독립 표본으로 다루면")
    L.append("> p가 낙관적으로 나온다.")
    L.append("> ")
    L.append("> C의 후보 분봉은 **09:05~14:49**로 제한한다 — 라이브도 14:50부터 신규진입")
    L.append("> 금지(345차)라 그 밖은 애초에 진입할 수 없다. 거래일별 건수도 실제와 맞춰")
    L.append("> 일중 진입 빈도를 보존한다.")
    L.append("> ")
    L.append("> ⚠ [40]과 **같은 시뮬 한계**를 그대로 물려받는다 — 절대 수준 인용 금지,")
    L.append("> 유효한 것은 팔 사이의 비교뿐이다.")
    L.append("> ")
    L.append("> **[40]과 함께 읽을 것.** 둘 다 REJECTS면 진입 축(방향·타점)이 **둘 다**")
    L.append("> 무작위와 구분되지 않는다는 뜻이고, 그 위에 새 진입 피처를 얹는 것은")
    L.append("> *가치가 검증되지 않은 필터에 검증되지 않은 피처를 더하는* 일이 된다.")
    L.append("")
    L.append("---")
    L.append("")

    L.append("## [43] 변동성 추정량 교체 가치 (MW0602 429차)")
    L.append("")
    L.append("**사이저는 이미 ATR로 변동성 스케일링을 하고 있다**")
    L.append("(`stop_risk = atr × %.1f × pt_value`). 그러니 질문은 \"변동성을 넣자\"가"
             % ATR_STOP_MULT)
    L.append("아니라 **\"분위 불확실성(선행 예측)이 ATR(후행 실현) 위에 추가 정보를")
    L.append("갖는가\"** 다. 판정은 **ATR을 통제한 뒤의 부분상관**으로 한다.")
    L.append("")
    if vew.get("error"):
        L.append("- ⚠ 조회 실패: `%s`" % vew.get("error"))
    elif vew.get("partial_corr") is not None:
        L.append("| 지표 | 값 |")
        L.append("|---|---|")
        L.append("| 표본 | %s건 / %s거래일 |" % (vew.get("n"), vew.get("n_days")))
        L.append("| corr(ATR×%.1f, %s분 실현레인지) | **%+.4f** |" % (
            ATR_STOP_MULT, vew.get("horizon_min", 30) if vew.get("horizon_min")
            else (VALIDATION_CAMPAIGN.get("vol_estimator_watch") or {}).get("horizon_min", 30),
            vew.get("corr_atr_realized", 0.0)))
        L.append("| corr(q90−q10, 실현레인지) | %+.4f |" % vew.get("corr_qunc_realized", 0.0))
        L.append("| 두 추정량 공선성 | **%.4f** |" % vew.get("collinearity", 0.0))
        L.append("| **부분상관** (ATR 통제 후) | **%+.4f (t=%s)** |" % (
            vew.get("partial_corr", 0.0), vew.get("partial_t", "—")))
        if vew.get("qty_boundary_cross") is not None:
            L.append("| qty 경계 통과 | %s건 / %s (%.1f%%) |" % (
                vew.get("qty_boundary_cross"), vew.get("n"),
                float(vew.get("qty_boundary_share", 0)) * 100))
        L.append("")
        _cw = float((VALIDATION_CAMPAIGN.get("vol_estimator_watch") or {})
                    .get("collinearity_warn", 0.90))
        if abs(float(vew.get("collinearity", 0))) >= _cw:
            L.append("> 🟡 **공선성 %.3f ≥ %.2f — 두 추정량이 사실상 같은 변수다.**"
                     % (vew.get("collinearity"), _cw))
            L.append("> 그래도 판정은 부분상관으로 한다(잔차에 정보가 있을 수 있으므로).")
            L.append("")
    else:
        L.append("- %s" % (vew.get("reason") or "표본 없음"))
    L.append("")
    if vew.get("recommendation"):
        L.append("- **권고**: %s" % vew["recommendation"])
        L.append("")
    L.append("> **왜 사이징 섀도를 돌리지 않는가.** 측정할 것이 없는 섀도는 잡음만")
    L.append("> 만든다 — [41]이 EPV 미달에서 학습을 거부하는 것과 같은 취지다.")
    L.append("> 이 채널이 SUPPORTS로 바뀌면 그때 섀도를 연다.")
    L.append("> ")
    L.append("> **SUPPORTS일 때도 \"교체\"가 아니라 \"잔차를 더하는\" 형태로 설계할 것** —")
    L.append("> 공선성이 높은 두 변수를 맞바꾸면 얻는 것 없이 기준선만 흔든다.")
    L.append("> ")
    L.append("> qty 경계 통과 건수를 함께 재는 이유: 상관이 높아도 `int()`·`min_qty`·")
    L.append("> `MAX_CONTRACTS` 클램프 때문에 경계에서 계약수가 갈릴 수 있다. 그 수가")
    L.append("> 0이면 **교체가 실무적으로도 무효**라는 뜻이다(CLAUDE.md ⑧·425차가")
    L.append("> qty 1↔2 경계의 중요성을 문서화했다).")
    L.append("")
    L.append("---")
    L.append("")

    # ── [MW0602 430차] [44] DynMC 붕괴행 잠식 ──────────────────────────
    L.append("## [44] DynMC 붕괴행 잠식 (MW0602 430차)")
    L.append("")
    L.append("`weight_collapsed=1`은 **실질 가중합 0 = 판단 불가**다. 07-31 보정 미적용")
    L.append("전환 이후 이 행들의 conf가 클리핑 상한 0.85로 나가 **분포 최상단을 점유**하고,")
    L.append("DynMC가 그 분포의 p%.0f를 `min_conf`로 쓰기 때문에 정상 신호 행의 통과율이"
             % (MC_PERCENTILE * 100))
    L.append("설계 의도(1−p%.0f≈%.0f%%)보다 낮아진다." % (
        MC_PERCENTILE * 100, (1 - MC_PERCENTILE) * 100))
    L.append("")
    if dcf.get("no_data") or dcf.get("n_rows") is None:
        L.append("- %s" % (dcf.get("reason") or "표본 없음"))
    else:
        L.append("| 지표 | 값 |")
        L.append("|---|---|")
        L.append("| 표본 | %s행 / %s거래일 (%s 이후) |" % (
            format(dcf.get("n_rows", 0), ","), dcf.get("n_days", "—"),
            dcf.get("start_date", "—")))
        L.append("| 붕괴행 비중 | **%.1f%%** (%s행) |" % (
            float(dcf.get("collapsed_share", 0)) * 100,
            format(dcf.get("n_collapsed", 0), ",")))
        L.append("| base_mc — 현행(붕괴 포함) | **%.4f** |" % dcf.get("base_mc_current", 0))
        L.append("| base_mc — 붕괴 제외 | %.4f (차 %+.4f) |" % (
            dcf.get("base_mc_excl_collapsed", 0), dcf.get("base_mc_shift", 0)))
        L.append("| 비붕괴 통과율 — 현행 | **%.1f%%** |" % (
            float(dcf.get("pass_rate_current", 0)) * 100))
        L.append("| 비붕괴 통과율 — 붕괴 제외 | %.1f%% |" % (
            float(dcf.get("pass_rate_excl_collapsed", 0)) * 100))
        L.append("| 설계 의도 통과율 | %.1f%% → **이탈 %+.2f%%p** |" % (
            float(dcf.get("pass_rate_design", 0)) * 100, dcf.get("gap_pp", 0.0)))
        if dcf.get("top_conf_share") is not None:
            L.append("| ConstOut 필터 여유 | 최빈값 %.2f가 %.1f%% "
                     "(임계 %.0f%% · 여유 **%+.2f%%p**)%s |" % (
                         dcf.get("top_conf_value", 0),
                         float(dcf.get("top_conf_share", 0)) * 100,
                         float(dcf.get("constout_threshold", 0.15)) * 100,
                         dcf.get("constout_margin_pp", 0.0),
                         " 🔴 **발동**" if dcf.get("constout_would_fire") else ""))
        _s44 = dcf.get("stratified") or {}
        if _s44.get("paired_days"):
            L.append("| 일자단위 | %s/%s일 양수, 부호검정 p=%s |" % (
                _s44.get("days_positive"), _s44.get("paired_days"), _s44.get("sign_p")))
        # [436차] 붕괴행이 실제 진입까지 갔는가 — 판정 무관여, 해석용 병기
        _el = dcf.get("entry_lift") or {}
        if _el.get("lift") is not None:
            L.append("| 붕괴행 진입 리프트 | **%.2fx** (진입 %d건 중 붕괴 %d건 = %.1f%% "
                     "vs 전체 붕괴율 %.1f%%) |" % (
                         _el["lift"], _el.get("n_entries", 0),
                         _el.get("entry_collapsed_n", 0),
                         float(_el.get("entry_collapsed_share", 0)) * 100,
                         float(_el.get("collapsed_share", 0)) * 100))
        if _el.get("by_day"):
            _bd = _el["by_day"]
            L.append("| 진입률 추이 | %s |" % " → ".join(
                "%s %.1f%%" % (r["date"][5:], r["entry_rate"] * 100) for r in _bd[-6:]))
        L.append("")
        if dcf.get("recommendation"):
            L.append("- **권고**: %s" % dcf["recommendation"])
            L.append("")
    L.append("> **⚠ 판정 = 조치가 아니다.** 붕괴행을 피드에서 빼면 진입이 늘어나는데,")
    L.append("> 427차 [39]가 확정한 대로 `min_conf`는 품질 필터가 아니라 **무작위**")
    L.append("> **샘플러**다 — 늘어난 진입은 무작위 표본 확대이고 기대값의 부호가")
    L.append("> 보장되지 않는다. CLAUDE.md ⑧(사이징·`MAX_CONTRACTS`) 미해제 상태에서는")
    L.append("> **진입 증가 = 노출 증가**이므로, 배선 변경은 주간회의 결정 사항이다.")
    L.append("> ")
    L.append("> **⚠ 판정 창.** `base_mc`는 10일 롤링이라 07-31 전환분이 다 채워지기")
    L.append("> 전(2026-08-11경) 수치로 판정하면 **과도구간을 정상으로 오인한다.**")
    L.append("> `min_days`가 그 방어선이다.")
    L.append("> ")
    L.append("> **[436차] 판정 시 반드시 함께 읽을 것 — 두 관측이 430차 §5와 어긋난다.**")
    L.append("> ① **붕괴행 진입 리프트가 1보다 한참 작다**(위 표의 실측값 — 436차")
    L.append("> 최초 관측 시 채널창 0.06x / 08-03~08-06만 보면 0.07x). 430차 §5는")
    L.append("> 붕괴행이 \"진입 예산을 잠식\"한다고 했으나, base_mc를 밀어올리는 것과")
    L.append("> 붕괴행이 **실제로 진입하는 것**은 다른 이야기다. 리프트가 계속 1을 크게")
    L.append("> 밑돌면 붕괴행 제외는 \"판단 불가 행에 진입을 준다\"가 아니라 **\"정상 행의")
    L.append("> 통과율을 복원한다\"**로 읽어야 하며, 그러면 위 ⚠(노출 증가)의 무게가 달라진다.")
    L.append("> ② **자기소멸이 아직 관측되지 않았다.** 430차 §5는 base_mc 수렴과 함께")
    L.append("> 진입 급증이 되돌아간다고 투영했는데(~08-11), 0806까지 base_mc는 투영대로")
    L.append("> 올랐고(0.3971→0.4151, 투영 0.418) **진입률은 되돌기는커녕 신고점**이었다")
    L.append("> (5.7%→3.0%→4.6%→**6.2%**). 위 \"진입률 추이\" 행이 그 후속이다 —")
    L.append("> 판정 시점에도 되돌지 않았으면 **투영 자체를 안건화할 것**.")
    L.append("> ")
    L.append("> **ConstOut 여유폭을 왜 같이 재는가.** `main.py:_recalibrate_mc`에")
    L.append("> \"동일 반올림값 15% 초과 시 제외\" 필터가 있다. 430차 실측에서 0.85가")
    L.append("> **12.6%**로 2.4%p 차이로 빠져나갔다 — 붕괴율이 오르는 날(07-29는 45%)엔")
    L.append("> 필터가 걸리고 안 걸리고가 뒤바뀌어 `base_mc`가 불연속으로 튄다.")
    L.append("> 임계는 손대지 않는다(낮추면 정상 conf 최빈값까지 걸린다) — **여유폭만**")
    L.append("> **노출**해 그 순간을 사후에 설명할 수 있게 한다.")
    L.append("")
    L.append("---")
    L.append("")

    # ── [MW0602 430차] [45] 축퇴 가드 플래핑 (게이지) ──────────────────
    L.append("## [45] 축퇴 가드 플래핑 (MW0602 430차 · 게이지)")
    L.append("")
    L.append("**판정 채널이 아니다**([33]·[41]과 같은 게이지). 앙상블 보정기의")
    L.append("적용/미적용이 하루 중 몇 번 뒤집히는지, 그 전환이 conf에 만드는 점프폭이")
    L.append("얼마인지만 잰다. 행 단위 복원 규칙: `confidence == min(confidence_raw, 0.85)`")
    L.append("이면 **미적용**(raw 통과)이다.")
    L.append("")
    if cgf.get("no_data"):
        L.append("- %s" % (cgf.get("reason") or "표본 없음"))
    else:
        L.append("| 지표 | 값 |")
        L.append("|---|---|")
        L.append("| 표본 | %s행 / %s거래일 |" % (
            format(cgf.get("n_rows", 0), ","), cgf.get("n_days", "—")))
        L.append("| 보정 미적용 비율 | **%.1f%%** |" % (
            float(cgf.get("passthru_share", 0)) * 100))
        L.append("| 전환 횟수 | 총 %s회 · **%.2f회/일**%s |" % (
            cgf.get("flips_total", "—"), cgf.get("flips_per_day", 0.0),
            " 🟡" if cgf.get("flap_warn") else ""))
        if cgf.get("conf_jump_median") is not None:
            L.append("| 전환 시 conf 점프 | 중앙값 **%.4f** / 최대 %.4f%s |" % (
                cgf.get("conf_jump_median", 0), cgf.get("conf_jump_max", 0),
                " 🟡" if cgf.get("jump_warn") else ""))
        _bd45 = cgf.get("by_day") or []
        if _bd45:
            L.append("")
            L.append("| 일자 | 행 | 미적용% | 전환 |")
            L.append("|---|---|---|---|")
            for r in _bd45[-10:]:
                L.append("| %s | %s | %.1f%% | %s |" % (
                    r["date"], r["n"], r["passthru_share"] * 100, r["flips"]))
        L.append("")
        if cgf.get("recommendation"):
            L.append("- **권고**: %s" % cgf["recommendation"])
            L.append("")
    L.append("> **왜 게이지인가.** 축퇴 판정은 `auc < 0.53` **단독**으로 내려진다 —")
    L.append("> AND의 span 조건은 사문이다(로그 845건 전수 최대 0.01321, 임계 0.02")
    L.append("> 도달 0건. `learning/calibration.py` 430차 정정 주석 참조). n=200에서")
    L.append("> AUC의 SE≈0.041이라 이 통계량이 0.53을 수시로 넘나든다.")
    L.append("> ")
    L.append("> **⚠ 이 채널은 임계 튜닝을 정당화하지 않는다.** 근본 문제는 임계가 아니라")
    L.append("> **정보 부재**다 — raw conf의 1m 적중 순위 AUC=**0.489**(<0.5, 역방향)로")
    L.append("> 어떤 단조 보정도 붙일 신호가 없다(427차 [39] REJECTS_HYP와 일치).")
    L.append("> 개선 여지는 \"정보 없음을 **안정적으로 표시**하는 것\"(히스테리시스 또는")
    L.append("> EOD 1회 고정)뿐이고, **AUC 임계·보정 함수형은 건드리지 않는다** —")
    L.append("> 건드리면 conf 스케일에 **세 번째 불연속**이 생긴다.")
    L.append("")
    L.append("---")
    L.append("")

    # ── [MW0601 434차] [46] HurstGate 임계 위치 A/B ──────────────────────
    L.append("## [46] HurstGate 임계 위치 A/B (MW0601 434차 신설)")
    L.append("")
    if not _g46:
        L.append("> ⚠ 미산출 — 스크립트 실행 실패 또는 사전등록 누락.")
    elif _g46.get("error"):
        L.append("> ⚠ 스크립트 실행 실패: %s" % _g46["error"])
    else:
        _live_th = float(_g46.get("live_threshold", 0.45))
        # ⚠ 431차 후속2 교훈 — 여러 줄에 걸친 문자열에 % 포매팅을 걸지 말 것.
        #   한 줄씩 독립적으로 포매팅한다(리터럴 %가 섞여도 안전).
        L.append("현행 임계 `HURST_RANGE_THRESHOLD = %.2f`가 이 추정량의 **판별 경계로**" % _live_th)
        L.append("**적절한 위치인가**를 묻는다. 지표는 **계약당 pt의 분리도**")
        L.append("(= 통과구간 평균 − 차단구간 평균)로, 계약당 정규화라 **사이징과 무관**하다.")
        L.append("")
        L.append("- 진입 %s건 중 hurst 매칭 %s건 / %s거래일 · 분위 룩백 %s거래일(당일 제외)"
                 % (_g46.get("n_positions", "—"), _g46.get("n_matched", "—"),
                    _g46.get("n_days", "—"), _g46.get("quantile_lookback_days", "—")))

        def _tbl(pv, title):
            L.append("")
            L.append("**%s**" % title)
            if not pv:
                L.append("")
                L.append("- (표본 없음)")
                return
            L.append("")
            L.append("| 후보 | 차단n | 발동률 | 차단평균pt | 통과평균pt | 분리도 | drop-worst | 차단승률 | 통과승률 |")
            L.append("|---|---|---|---|---|---|---|---|---|")
            _cur = _g46.get("cur_key")
            for k in sorted(pv, key=lambda x: (x.startswith("q"), x)):
                v = pv[k]
                L.append("| %s%s | %d | %.1f%% | %+.3f | %+.3f | **%+.3f** | %s | %.1f%% | %.1f%% |" % (
                    k, " ← 현행" if k == _cur else "", v["n_gated"], v["gate_rate"] * 100,
                    v["mean_gated_pt"], v["mean_passed_pt"], v["separation_pt"],
                    ("%+.3f" % v["separation_drop_worst"]) if v.get("separation_drop_worst") is not None else "—",
                    v["wr_gated"] * 100, v["wr_passed"] * 100))

        # ⚠ _tbl()이 title을 `**...**`로 감싸므로 title 안에 다시 `**`를 쓰면
        #   볼드가 중첩돼 마크다운이 깨진다.
        _tbl(_g46.get("per_variant"), "전체표본 — ⚠ in-sample, 판정 근거 아님")
        _tbl(_g46.get("per_variant_oos"),
             "OOS (%s 이후) — 판정 대상" % (_g46.get("oos_start") or "미설정"))
        L.append("")
        L.append("- **판정: %s** — %s" % (_g46.get("verdict"), _g46.get("reason")))
        # 판정보조 ② 일자단위(313차)
        _bd = _g46.get("by_day") or {}
        if _bd:
            _ks = sorted(_bd)[-10:]
            L.append("")
            L.append("**판정보조 ② 일자단위 (313차)** — 저hurst(<%.2f) 진입 비중 vs 그날 계약당 합pt"
                     % float(_g46.get("live_threshold", 0.45)))
            L.append("")
            L.append("| 일자 | 진입n | 저hurst 비중 | 합pt |")
            L.append("|---|---|---|---|")
            for k in _ks:
                v = _bd[k]
                L.append("| %s | %d | %.0f%% | %+.2f |" % (
                    k, v["n"], v["low_share"] * 100, v["pt"]))
    L.append("")
    L.append("> **⚠ 사전등록 정직성 고지**: 후보 목록은 2026-08-05 점검에서 **이미 1회**")
    L.append("> **스윕한 뒤에** 골랐다. 따라서 전체표본은 **가설을 세운 그 기간의 in-sample**")
    L.append("> 이며 그 자체로는 판정 근거가 아니다 — 사전등록 가치는 OOS에 있다([23]과 동일).")
    L.append("> ")
    L.append("> **⚠ 이미 반증된 방향 — 재시도 금지**: 추정량 **편향보정**(상수이동·선형")
    L.append("> de-shrinkage)은 317차가 60거래일 실측에서 **FalsePass 14.4%→30~33% 악화**로")
    L.append("> 폐기했다(`HURST_DESHRINK_TABLE`은 REFERENCE ONLY). 이 채널은 추정량을 고치지")
    L.append("> 않고 **임계 위치만** 묻는다. 317차가 손댄 N/max_lag와도 질문이 다르다 —")
    L.append("> 26주 WFA 재검증 항목을 앞당길 이유가 아니다.")
    L.append("> ")
    L.append("> **⚠ 372차 함정**: PSI 임계 재보정 시도가 이상치 2건이 만든 값으로 확인돼")
    L.append("> **기존값 유지**로 끝났다. 여기도 표본이 얇다 — `drop-worst`(차단구간 최악")
    L.append("> 1건 제거)와 위 일자단위를 **반드시 함께** 읽을 것. 분리도만 보면 같은 함정이다.")
    L.append("> ")
    L.append("> **⚠ 임계를 낮추면 노출이 는다.** 발동률이 줄어 사이징 축소가 덜 걸린다.")
    L.append("> CLAUDE.md ⑧ 미해제 상태에서는 그 자체가 리스크이므로 승격 시 총노출 병기 필수.")
    L.append("> ")
    L.append("> **⚠ [3-6] `hurst_gate_shadow`와 다른 질문이다** — 그건 \"차단된 신호가")
    L.append("> 벌었을까\"(모집단: 차단분), 이건 \"임계가 좋은/나쁜 신호를 가르는가\"")
    L.append("> (모집단: 실제 진입분)다. 두 verdict는 서로 무관하다(§9-4).")
    L.append("")
    L.append("---")
    L.append("")

    # ── [MW0602 489차 / D2] [56] CB② 복원 반사실 ────────────────────────────────
    L.append("## [56] CB② 복원 반사실 (489차 신설 · 0823 주간회의 D2)")
    L.append("")
    if cb2.get("error"):
        L.append("> ⚠ 스크립트 실행 실패: %s" % cb2["error"])
    else:
        L.append("- 라이브 `CB_CONSEC_STOP_LIMIT` = **%s** (%s)" % (
            cb2.get("live_limit"),
            "활성" if cb2.get("live_limit_active") else "**비활성** — 모의투자 한정 예외"))
        L.append("- 판정창 **%s~** : %s포지션 / %s거래일 (그 이전은 사후탐색 씨앗 — 판정 미반영)" % (
            cb2.get("start_date"), cb2.get("n_positions_judged"), cb2.get("n_days_judged")))
        L.append("")
        L.append("| 복원값 | 판정 | 정지일(유효) | 제거 포지션 | 제거 손익 | drop-worst |")
        L.append("|---|---|---|---|---|---|")
        for _lim, _d in sorted((cb2.get("per_limit") or {}).items()):
            _dw = _d.get("krw_removed_drop_worst")
            L.append("| %s | %s | %s (%s) | %s | %s | %s |" % (
                _lim, _fmt_verdict(_d.get("verdict", "")),
                _d.get("n_halt_days", 0), _d.get("n_effective_days", 0),
                _d.get("n_removed", 0),
                "{:+,.0f}원".format(_d.get("krw_removed") or 0.0),
                ("{:+,.0f}원".format(_dw) if _dw is not None else "—")))
        _seed = cb2.get("seed") or {}
        if _seed:
            L.append("")
            L.append("**사후탐색 씨앗 (%s 이전) — 🔴 판정 미반영, 표시 전용**" % cb2.get("start_date"))
            L.append("")
            L.append("| 복원값 | 정지일 | 제거 포지션 | 제거 손익 |")
            L.append("|---|---|---|---|")
            for _lim, _s in sorted(_seed.items()):
                L.append("| %s | %s | %s | %s |" % (
                    _lim, _s.get("n_halt_days", 0), _s.get("n_removed", 0),
                    "{:+,.0f}원".format(_s.get("krw_removed") or 0.0)))
    L.append("")
    L.append("> **왜 이 채널이 생겼나.** 절대원칙 §2의 CB②는 2026-07-05부터 `9999`")
    L.append("> (사실상 비활성)이고 복원 재검토 기한이 2026-08-29였는데, **그 기한은")
    L.append("> 2026-08-01에 이미 한 번 4주 연기된 것**이다. 날짜를 또 미루면")
    L.append("> CB③-P4·FP-CRITICAL이 걸어간 길과 같아진다. 0823 주간회의(D2)는 기한을")
    L.append("> **날짜가 아니라 사건**에 묶었다 — 복원 시점 = 실전 전환 기준 ⑧")
    L.append("> (실전 자본 재설정) 해제와 **동일 커밋**. ⑧이 열리는 순간이 노출이")
    L.append("> 커지는 순간이므로 선행조건이 되어 잊힐 수 없고, 이 채널이 그때 쓸")
    L.append("> 근거를 매주 쌓는다.")
    L.append("> ")
    L.append("> 🔴 **집계 단위는 포지션이다 — 레그가 아니다(470차 C1).**")
    L.append("> ⚠ **로그 `[CB] 연속 손절 N회`로 과거를 세지 말 것** — 2026-08-14 이전은")
    L.append("> 레그 단위 시절이라 과대계상된다(실측 대조 08-14: 로그 max=3 vs 포지션 2).")
    L.append("> 이 채널은 `trades.db`에서 **현행 규칙으로 재구성**한다.")
    L.append("> ")
    L.append("> ⚠ **진입 제거만 모형화한다.** 실제 HALT는 `emergency_exit`까지 부르므로")
    L.append("> 보유분 청산 시점도 바뀐다 — 2차 효과 미재현이라 **하한 추정**이고,")
    L.append("> 손익 예측이 아니라 **방향(부호) 판정용**이다.")
    L.append("> ")
    L.append("> ⚠ 단위는 **원(₩)**. `[1계약·TP1상한·미실현 시뮬]` 배지 채널과 더하지 말 것.")
    L.append("> ⚠ **CB②는 손익 장치가 아니라 실전 자본의 꼬리위험 장치다** —")
    L.append("> `RESTORE_COSTS`가 떠도 그것은 \"복원하지 말라\"가 아니라 **대가의 계량**이다.")
    L.append("")
    L.append("---")
    L.append("")

    # [MW0601 409차 / R3] A/B 채널 기준선 PC 대조 — **표시 전용, 판정 미반영**
    _me_pc = _pc_dir_name()
    _peers = _peer_ab_baselines(_me_pc)
    L.append("## A/B 채널 기준선 PC 대조 (표시 전용 — 판정 미반영)")
    L.append("")
    L.append("`[3-B]`·`[23-B]`·`[25]`의 FAIL 판정은 전부 `delta_vs_current`(대안 − 현행)로")
    L.append("내린다. 따라서 **기준선 `current` 자체의 부호가 PC간 반대면 같은 대안이 한 PC에서만**")
    L.append("**\"현행 초과\"로 등재된다** — 그 목록을 단일 PC 근거로 채택하면 안 된다.")
    L.append("")
    if not _peers:
        L.append("- 대조 가능한 다른 PC 리포트가 없다 (`docs/정기점검/금요일점검/<PC>/`에")
        L.append("  상대 PC 산출물이 있어야 한다 — 아직 pull하지 않았거나 단일 PC 운용 중).")
    else:
        _cols = [_me_pc] + sorted(_peers)
        L.append("| 채널 | %s |" % " | ".join(
            (c if c == _me_pc else "%s (%s)" % (c, _peers[c]["date"])) for c in _cols))
        L.append("|---%s|" % ("|---" * len(_cols)))
        _inverted = []
        for _tag, _key, _title in _AB_BASELINE_CHANNELS:
            _mine = ((off.get(_key) or {}).get("per_variant") or {}) \
                .get("current", {}).get("total_pt")
            _vals = [_mine] + [_peers[c]["vals"].get(_key) for c in sorted(_peers)]
            _known = [v for v in _vals if isinstance(v, (int, float))]
            _flip = len(_known) > 1 and min(_known) < 0 < max(_known)
            if _flip:
                _inverted.append(_tag)
            L.append("| %s %s%s | %s |" % (
                _tag, _title, " ⚠**부호 역전**" if _flip else "",
                " | ".join(("**%s**" % v) if isinstance(v, (int, float)) else "—"
                           for v in _vals)))
        L.append("")
        L.append("*단위 pt — 각 채널 `per_variant.current.total_pt`(현행 전략의 재생 손익).*")
        L.append("")
        if _inverted:
            L.append("> ⚠ **기준선 부호가 갈린 채널: %s** — 이 채널들의 \"현행 초과 대안\""
                     % ", ".join(_inverted))
            L.append("> 목록은 PC마다 다르게 나올 수밖에 없다. **양쪽에서 공통으로 살아남은**")
            L.append("> **대안만** 후보로 볼 것(0802 대조 §3: `stop_1.0`·`sym_1.0_1.0` 2개).")
        else:
            L.append("> 기준선 부호가 모든 PC에서 일치한다 — A/B 결과를 그대로 읽어도 된다.")
        L.append("> 상대 PC 날짜가 이번 주가 아니면 그 PC가 아직 리포트를 생성/커밋하지")
        L.append("> 않은 것이다. **날짜가 다른 두 리포트를 같은 주로 취급하지 말 것.**")
    L.append("")
    L.append("---")
    L.append("")

    # [404차 후속11] 확정 결정 레지스트리 — 판정과 결정을 분리해 보여준다
    L.append("## 확정 결정 레지스트리 (주간회의 수동 결정 이력)")
    L.append("")
    if not VALIDATION_CAMPAIGN_DECISIONS:
        L.append("- 등록된 결정 없음")
    else:
        for _k, _d in sorted(VALIDATION_CAMPAIGN_DECISIONS.items(),
                             key=lambda x: (x[1].get("date", ""), x[0])):
            L.append("### `%s` — %s *(%s)*" % (_k, _d["decision"], _d["date"]))
            L.append("")
            L.append("%s" % _d.get("note", ""))
            L.append("")
    L.append("> **판정(verdict)과 결정은 별개다.** 판정은 사전등록 기준으로 매주 자동")
    L.append("> 재계산되므로, 사람이 \"보고 나서 일부러 적용하지 않기로\" 한 채널도 FAIL이")
    L.append("> 계속 뜬다. 그 FAIL을 미조치로 오독하지 말 것 — 위 표에 결정이 있으면 이미")
    L.append("> 검토가 끝난 것이고, 뒤집으려면 새 근거가 필요하다.")
    L.append("> 반대 방향의 사고도 실제로 있었다: [6] Hurst 완화 권고는 2026-07-15에 이미")
    L.append("> 배포됐는데 리포트가 3주째 같은 권고를 찍어, 0801 결산 초안이 그것을 신규")
    L.append("> 승인 안건으로 잘못 올렸다(코드 확인 후 철회). 이 레지스트리가 그 재발 방지책이다.")
    L.append("> 출처: `config/settings.py:VALIDATION_CAMPAIGN_DECISIONS`. 결정 변경 시")
    L.append("> 그쪽을 갱신하고 `dev_memory/DECISION_LOG.md`에도 기록할 것(§9).")
    L.append("")
    L.append("---")
    L.append("")
    L.append("> 이 리포트는 권고만 출력한다. 정책 적용/롤백은 주간 회의에서 수동 결정하고")
    L.append("> `dev_memory/DECISION_LOG.md`에 기록할 것 (§2 사전등록 원칙, §9 계엄령).")

    return "\n".join(L), metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=28,
                        help="분석 창(일). 기본 28 — 캠페인 4주 전체")
    parser.add_argument("--out-dir", default=None,
                        help="출력 폴더 오버라이드. 기본 docs/정기점검/금요일점검/<PC명>/ "
                             "— 재현·검증용 임시 출력에만 쓸 것(주간 산출물은 기본 경로 유지). "
                             "지정 시 FIFO 보관정리는 하지 않는다")
    parser.add_argument("--keep", type=int, default=VALIDATION_REPORT_KEEP_WEEKS,
                        help="FIFO 보관 주차 수(기본 config/settings.py:"
                             "VALIDATION_REPORT_KEEP_WEEKS). 0 이하면 삭제 안 함")
    parser.add_argument("--no-prune", action="store_true",
                        help="이번 실행에서만 보관정리를 건너뛴다")
    args = parser.parse_args()

    report_md, metrics = build_report(args.days)

    # [MW0601 407차] 출력을 data/ 고정파일명 → docs/정기점검/금요일점검/<PC>/ 날짜본으로 이전.
    #
    # 왜 PC 폴더인가: data/는 gitignore 대상 PC 로컬 디렉터리라 **다른 PC에서 볼 방법이
    # 없었다.** 0802 MW0601×MW0602 항목별 대조에서 MW0602 리포트를 사용자가 수동
    # 복사해줄 때까지 31채널 대조가 막혀 있었다 — 리포트는 두 PC가 서로를 보는 유일한
    # 통로이므로 커밋되는 위치에 둔다("런타임 산출물 커밋 금지"의 의도적 예외).
    #
    # 왜 날짜본인가: 고정 파일명이 매주 덮어써서 **지난주 리포트가 남지 않았다.**
    # 2026-07-31 리포트가 08-01 재생성에 덮였고, 405차 세션 스크래치패드에 우연히
    # 백업이 남아 있지 않았으면 영영 잃었을 것이다. 날짜본은 그 유실을 원천 차단하고
    # 주차간 비교(지난주 vs 이번주)도 가능하게 한다.
    #
    # PC 식별은 405차 P0-5의 _pc_id()를 그대로 쓴다(호스트명에서 MW####).
    # 폴더 이름에 PC가 들어가므로 파일명에는 날짜만 넣는다.
    # [MW0601 408차] 폴더는 없으면 만든다 — 새 PC 첫 실행에서 그대로 동작한다.
    # PC 이름 자체가 규칙(MW####)에 안 맞으면 _pc_dir_name()이 경고를 찍는다.
    pc_name = _pc_dir_name()
    if args.out_dir:
        out_dir = os.path.abspath(args.out_dir)
    else:
        out_dir = os.path.join(BASE_DIR, "docs", "정기점검", "금요일점검", pc_name)
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.date.today().strftime("%Y%m%d")
    md_path = os.path.join(out_dir, "validation_campaign_report_%s.md" % stamp)
    json_path = os.path.join(out_dir, "validation_campaign_metrics_%s.json" % stamp)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2, default=str)

    print(report_md)
    print("\n저장: %s / %s" % (md_path, json_path))

    # [MW0601 408차] FIFO 보관 — 최근 N주만 남기고 오래된 자동생성물 삭제.
    # **쓰기가 끝난 뒤에만** 돈다(중간에 죽어도 이번 주 파일은 이미 디스크에 있다).
    # --out-dir는 임의 폴더라 절대 정리하지 않는다 — 남의 디렉터리를 지우면 안 된다.
    if args.out_dir:
        if args.keep > 0:
            print("보관정리: --out-dir 사용 중이라 건너뜀 (임의 폴더는 정리하지 않는다)")
    elif args.no_prune:
        print("보관정리: --no-prune")
    else:
        removed = _prune(pc_name, args.keep)
        if removed:
            print("보관정리: %d주 초과분 %d개 삭제 — %s"
                  % (args.keep, len(removed),
                     ", ".join(os.path.basename(p) for p in removed)))
        elif args.keep > 0:
            print("보관정리: 삭제 대상 없음 (보관 %d주)" % args.keep)


if __name__ == "__main__":
    main()

# backtest/param_optimizer.py — 전략 파라미터 최적화 프레임워크
"""
사용 흐름:
  1. 백테스트 그리드서치 → 상위 파라미터 후보 추출
  2. WalkForwardValidator로 교차검증 (26주 데이터)
  3. 통과 파라미터 → config/strategy_params.py PARAM_CURRENT 업데이트

실행 예시:
  python -m backtest.param_optimizer --groups A E --top-n 10
  python -m backtest.param_optimizer --groups A B C D E F I --full-wfa

주의:
  - 그리드 크기가 매우 커질 수 있음 → coupled_group 단위 실행 권장
  - WFA는 최소 26주 데이터 필요 (raw_data.db)
  - 병렬 처리 미지원 (Python 3.7 32-bit GIL 제한)
"""
import itertools
import logging
import math
import datetime
import json
import os
from typing import Any, Dict, List, Optional, Tuple

from config.strategy_params import (
    PARAM_SPACE, COUPLED_GROUPS, OPT_OBJECTIVES,
    generate_grid, validate_params, normalize_ensemble_weights,
    PARAM_HISTORY,
)
from backtest.walk_forward import WalkForwardValidator, AnchoredWalkForwardValidator
from backtest.performance_metrics import PerformanceMetrics
from config.settings import DB_DIR

logger = logging.getLogger(__name__)

# 최적화 결과 저장 경로
OPT_RESULT_DIR = os.path.join(DB_DIR, "param_opt")


def _extract_pareto_front(scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    (Sharpe, -MDD) 기준 Pareto 전선 추출.
    다른 후보에게 Sharpe·MDD 모두에서 지배당하지 않는 후보들을 반환.
    """
    pareto = []
    for cand in scored:
        s1 = cand["score"].get("sharpe", 0.0)
        m1 = abs(cand["score"].get("mdd_pct", 1.0))   # 절대값 (낮을수록 좋음)
        dominated = False
        for other in scored:
            if other is cand:
                continue
            s2 = other["score"].get("sharpe", 0.0)
            m2 = abs(other["score"].get("mdd_pct", 1.0))
            if s2 >= s1 and m2 <= m1 and (s2 > s1 or m2 < m1):
                dominated = True
                break
        if not dominated:
            pareto.append(cand)
    return pareto


class ParamOptimizer:
    """
    전략 파라미터 최적화기.

    단계:
      1. run_grid_search()  — 백테스트 그리드서치 (상위 후보 추출)
      2. run_wfa()          — WFA 교차검증 (최종 선정)
      3. apply_best()       — PARAM_CURRENT 업데이트 + 이력 저장

    사용:
        optimizer = ParamOptimizer(weekly_trades=weekly_trades_data)
        result    = optimizer.run(coupled_group="entry_quality", top_n=20)
        if result["passed"]:
            optimizer.apply_best(result["best_params"])
    """

    def __init__(
        self,
        weekly_trades: List[List[dict]],
        baseline_params: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            weekly_trades:   주차별 거래 데이터
                             [ [{"pnl_krw": float, "win": bool}, ...],  # 1주차
                               [...],                                     # 2주차 ...
                             ]
            baseline_params: 비교 기준 파라미터 (None이면 PARAM_CURRENT 사용)
        """
        self.weekly_trades = weekly_trades
        self.baseline      = baseline_params or {}
        self._wfa          = WalkForwardValidator()
        self._metrics      = PerformanceMetrics()

        os.makedirs(OPT_RESULT_DIR, exist_ok=True)

    # ── 메인 실행 ──────────────────────────────────────────────────────
    def run(
        self,
        coupled_group:  Optional[str] = None,
        param_names:    Optional[List[str]] = None,
        top_n:          int = 20,
        full_wfa:       bool = True,
    ) -> Dict[str, Any]:
        """
        파라미터 최적화 실행.

        Args:
            coupled_group: COUPLED_GROUPS 키 (예: "entry_quality")
            param_names:   직접 지정 파라미터 이름 리스트
            top_n:         그리드서치 상위 후보 수
            full_wfa:      True=WFA 교차검증 / False=단순 전체 백테스트

        Returns:
            {
              "passed":      bool,
              "best_params": dict,
              "wfa_result":  dict,
              "all_results": List[dict],  # top_n 결과
              "baseline_comparison": dict,
            }
        """
        # 파라미터 이름 결정
        if coupled_group and coupled_group in COUPLED_GROUPS:
            names = COUPLED_GROUPS[coupled_group]
        elif param_names:
            names = param_names
        else:
            raise ValueError("coupled_group 또는 param_names 중 하나 필요")

        logger.info("[Optimizer] 탐색 시작: %s (%d개 파라미터)", names, len(names))

        # ─ 1. 그리드 생성 ────────────────────────────────────────────
        grid = generate_grid(names)
        logger.info("[Optimizer] 그리드 포인트: %d개", len(grid))

        # ─ 2. 그리드서치 (전체 데이터 1회 백테스트) ─────────────────
        scored: List[Dict[str, Any]] = []
        for i, candidate in enumerate(grid):
            # 앙상블 가중치 정규화
            candidate = normalize_ensemble_weights(candidate)

            # 유효성 검사
            valid, errors = validate_params(candidate)
            if not valid:
                continue

            # 단순 전체 백테스트 점수 계산
            score = self._score_candidate(candidate)
            scored.append({"params": candidate, "score": score})

            if (i + 1) % 100 == 0:
                logger.info("[Optimizer] 진행: %d / %d", i + 1, len(grid))

        if not scored:
            return {"passed": False, "reason": "유효한 파라미터 후보 없음"}

        # 하드 제약 필터링
        filtered = [r for r in scored if self._check_hard_constraints(r["score"])]
        logger.info("[Optimizer] 하드 제약 통과: %d / %d", len(filtered), len(scored))

        if not filtered:
            # 제약 완화: 최상위 상위 20% 구제
            filtered = sorted(scored, key=lambda x: x["score"].get("sharpe", 0), reverse=True)
            filtered = filtered[:max(1, len(scored) // 5)]
            logger.warning("[Optimizer] 하드 제약 통과 없음 — 상위 20%% 구제 적용")

        # 복합 점수 정렬
        filtered.sort(key=lambda x: self._composite_score(x["score"]), reverse=True)
        top_candidates = filtered[:top_n]

        # ─ 3. WFA 교차검증 (§13: 데이터 주수에 따라 Rolling/AWFA/Combined 자동 선택) ─
        n_weeks = len(self.weekly_trades)
        _awfa   = AnchoredWalkForwardValidator()
        _wfa_mode = _awfa.recommend_mode(n_weeks)
        logger.info("[Optimizer] WFA 모드: %s (데이터 %d주)", _wfa_mode, n_weeks)

        best_result = None
        best_composite = -999.0

        for rank, cand in enumerate(top_candidates):
            if full_wfa:
                if _wfa_mode == "anchored_only":
                    wfa_result = _awfa.run(self.weekly_trades)
                elif _wfa_mode == "combined":
                    combined = _awfa.run_combined(self.weekly_trades)
                    wfa_result = combined.get("anchored_result", {})
                    wfa_result["passed"] = combined.get("passed", False)
                    if "avg_metrics" not in wfa_result:
                        wfa_result["avg_metrics"] = {"sharpe": combined.get("combined_sharpe", 0)}
                else:
                    wfa_result = self._wfa.run(self.weekly_trades)
            else:
                wfa_result = {"passed": True, "avg_metrics": cand["score"]}

            composite = self._composite_score(
                wfa_result.get("avg_metrics", cand["score"])
            )

            logger.info(
                "[Optimizer] WFA 순위%d: Sharpe=%.2f MDD=%.1f%% 승률=%.1f%% 복합=%.3f",
                rank + 1,
                wfa_result.get("avg_metrics", {}).get("sharpe", 0),
                abs(wfa_result.get("avg_metrics", {}).get("mdd_pct", 0)) * 100,
                wfa_result.get("avg_metrics", {}).get("win_rate", 0) * 100,
                composite,
            )

            if wfa_result.get("passed") and composite > best_composite:
                best_composite = composite
                best_result    = {
                    "params":     cand["params"],
                    "wfa_result": wfa_result,
                    "composite":  composite,
                }

        # ─ 4. 기준선 대비 비교 ───────────────────────────────────────
        baseline_comparison = self._compare_with_baseline(best_result)

        result = {
            "passed":               best_result is not None,
            "best_params":          best_result["params"] if best_result else {},
            "wfa_result":           best_result["wfa_result"] if best_result else {},
            "composite_score":      best_result["composite"] if best_result else 0.0,
            "all_results":          top_candidates,
            "baseline_comparison":  baseline_comparison,
            "searched_params":      names,
            "grid_size":            len(grid),
            "passed_hard_filter":   len(filtered),
            "timestamp":            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # 결과 저장
        self._save_result(result, coupled_group or "custom")

        return result

    # ── 현재 파라미터 적용 ─────────────────────────────────────────────
    def apply_best(
        self,
        best_params: Dict[str, Any],
        wfa_result:  Dict[str, Any],
        note:        str = "",
    ) -> None:
        """
        최적 파라미터를 PARAM_CURRENT에 반영하고 이력 저장.

        Args:
            best_params: apply할 파라미터 딕셔너리
            wfa_result:  WFA 결과 딕셔너리 (avg_metrics 포함)
            note:        변경 사유 메모
        """
        from config.strategy_params import PARAM_CURRENT

        changed = {}
        for k, v in best_params.items():
            old = PARAM_CURRENT.get(k)
            if old != v:
                changed[k] = {"from": old, "to": v}
                PARAM_CURRENT[k] = v

        if not changed:
            logger.info("[Optimizer] 변경 사항 없음 — 기존 파라미터 유지")
            return

        avg = wfa_result.get("avg_metrics", {})
        history_entry = {
            "date":    datetime.datetime.now().strftime("%Y-%m-%d"),
            "version": "v%d.%d" % (len(PARAM_HISTORY) + 1, 0),
            "changed": changed,
            "wfa_result": {
                "sharpe":   avg.get("sharpe"),
                "mdd_pct":  avg.get("mdd_pct"),
                "win_rate": avg.get("win_rate"),
            },
            "note": note or "param_optimizer.py 자동 최적화",
        }
        PARAM_HISTORY.append(history_entry)

        # [Phase2] StrategyRegistry에 버전 자동 등록
        try:
            from config.strategy_registry import get_registry as _get_registry
            _get_registry().register_version(
                version        = history_entry["version"],
                changed_params = changed,
                wfa_metrics    = history_entry["wfa_result"],
                note           = note or "param_optimizer.py 자동 최적화",
            )
            logger.info("[Optimizer] StrategyRegistry 등록 완료: %s", history_entry["version"])
        except Exception as _e:
            logger.warning("[Optimizer] registry 등록 실패 (스킵): %s", _e)

        logger.info(
            "[Optimizer] 파라미터 업데이트 완료 | 변경 %d개 | %s",
            len(changed),
            ", ".join("%s: %s→%s" % (k, v["from"], v["to"]) for k, v in changed.items()),
        )
        logger.info(
            "[Optimizer] WFA: Sharpe=%.2f MDD=%.1f%% 승률=%.1f%%",
            avg.get("sharpe", 0),
            abs(avg.get("mdd_pct", 0)) * 100,
            avg.get("win_rate", 0) * 100,
        )

        # [§19] RegimeFingerprint — 버전 교체 시 Live 버퍼 → 학습 기준 승격
        try:
            from strategy.regime_fingerprint import get_fingerprint as _get_fp
            _get_fp().reset_to_live_baseline()
        except Exception as _fp_e:
            logger.warning("[Optimizer] RegimeFingerprint 기준선 갱신 실패: %s", _fp_e)

    def propose_for_shadow(
        self,
        best_params: Dict[str, Any],
        wfa_result:  Dict[str, Any],
        note:        str = "",
    ) -> str:
        """
        최적 파라미터를 즉시 적용하지 않고 섀도우 후보로 보존.

        apply_best()와 달리 PARAM_CURRENT를 건드리지 않는다.
        trading loop(main.py)가 시작될 때 data/shadow_candidate.json을 읽어
        ShadowEvaluator를 초기화한다 (start_shadow_mode 참조).

        Returns:
            candidate_version 문자열
        """
        avg = wfa_result.get("avg_metrics", {})
        candidate_version = "v%d.%d-shadow" % (len(PARAM_HISTORY) + 1, 0)

        candidate = {
            "candidate_version": candidate_version,
            "candidate_params":  best_params,
            "wfa_sharpe":        float(avg.get("sharpe", 0.0)),
            "wfa_metrics":       avg,
            "proposed_at":       datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note":              note or "param_optimizer.py 섀도우 제안",
        }

        _path = os.path.join(OPT_RESULT_DIR, "..", "..", "shadow_candidate.json")
        _path = os.path.normpath(_path)
        try:
            os.makedirs(os.path.dirname(_path), exist_ok=True)
            with open(_path, "w", encoding="utf-8") as f:
                json.dump(candidate, f, ensure_ascii=False, indent=2)
            logger.info("[Optimizer] 섀도우 후보 저장: %s → %s", candidate_version, _path)
        except Exception as _e:
            logger.warning("[Optimizer] shadow_candidate.json 저장 실패: %s", _e)

        # 이벤트 로그
        try:
            from config.strategy_registry import get_registry as _get_reg
            _get_reg().log_event(
                event_type = "SHADOW_START",
                message    = "WFA Sharpe=%.2f — 섀도우 대기 시작 (%s)" % (
                    avg.get("sharpe", 0.0), note or ""),
                version    = candidate_version,
            )
        except Exception as _le:
            logger.warning("[Optimizer] registry log_event 실패: %s", _le)

        return candidate_version

    # ── 내부 헬퍼 ─────────────────────────────────────────────────────
    def _score_candidate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        파라미터 후보를 전체 데이터로 1회 백테스트.
        실제 구현에서는 파라미터를 시뮬레이션 엔진에 주입해야 함.
        현재는 weekly_trades 집계 지표를 반환 (파라미터 주입 자리).
        """
        all_trades: List[dict] = []
        for week in self.weekly_trades:
            all_trades.extend(week)
        return self._metrics.compute(all_trades)

    def _check_hard_constraints(self, score: Dict[str, Any]) -> bool:
        """OPT_OBJECTIVES 하드 제약 검사."""
        constraints = OPT_OBJECTIVES["hard_constraints"]
        for metric, (op, threshold) in constraints.items():
            val = score.get(metric, 0)
            if op == ">=" and val < threshold:
                return False
            if op == "<=" and abs(val) > threshold:
                return False
        return True

    def _composite_score(self, score: Dict[str, Any]) -> float:
        """복합 점수 계산 (OPT_OBJECTIVES.composite_score 가중합)."""
        weights = OPT_OBJECTIVES["composite_score"]
        total   = 0.0
        for metric, w in weights.items():
            val = score.get(metric, 0.0)
            if metric == "win_rate":
                val *= 100   # 0.54 → 54 스케일 통일
            total += val * w
        return total

    def _compare_with_baseline(
        self, best_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """기준선 대비 성과 개선량 계산."""
        if not best_result:
            return {}

        all_trades: List[dict] = []
        for week in self.weekly_trades:
            all_trades.extend(week)
        baseline_score = self._metrics.compute(all_trades)

        new_score = best_result["wfa_result"].get("avg_metrics", {})

        return {
            "sharpe_delta":    round(new_score.get("sharpe", 0) - baseline_score.get("sharpe", 0), 3),
            "mdd_pct_delta":   round(abs(new_score.get("mdd_pct", 0)) - abs(baseline_score.get("mdd_pct", 0)), 4),
            "win_rate_delta":  round(new_score.get("win_rate", 0) - baseline_score.get("win_rate", 0), 4),
            "pf_delta":        round(new_score.get("profit_factor", 0) - baseline_score.get("profit_factor", 0), 3),
        }

    # ── Pareto 최적 파라미터 선정 (§18) ───────────────────────────────────
    def run_pareto(
        self,
        coupled_group:  Optional[str]  = None,
        param_names:    Optional[List[str]] = None,
        stability_min:  float = 2.0,
    ) -> Dict[str, Any]:
        """
        Pareto-Front 기반 파라미터 선정 (§18).

        1. 전체 그리드에서 (Sharpe, -MDD) Pareto-optimal 집합 추출
        2. 각 후보의 neighborhood stability_score 계산
        3. stability_score 최대 & >= stability_min 파라미터 반환

        Args:
            coupled_group : COUPLED_GROUPS 키
            param_names   : 직접 지정 파라미터 이름 리스트
            stability_min : 통과 기준 stability_score (기본 2.0)

        Returns:
            {
              "passed":           bool,
              "best_params":      dict,
              "stability_score":  float,
              "pareto_count":     int,
              "reason":           str (실패시),
              "pareto_candidates": list (성공시),
            }
        """
        if coupled_group and coupled_group in COUPLED_GROUPS:
            names = COUPLED_GROUPS[coupled_group]
        elif param_names:
            names = param_names
        else:
            raise ValueError("coupled_group 또는 param_names 중 하나 필요")

        logger.info("[Pareto] 탐색 시작: %s", names)

        # ─ 1. 축 생성 & 전체 그리드 점수 계산 ────────────────────────────
        axes: Dict[str, List] = {}
        for name in names:
            spec = PARAM_SPACE[name]
            pts: list = []
            v = spec["low"]
            while v <= spec["high"] + 1e-9:
                pts.append(int(round(v)) if spec["dtype"] == "int" else round(float(v), 6))
                v += spec["step"]
            axes[name] = pts

        keys   = list(axes.keys())
        combos = list(itertools.product(*[axes[k] for k in keys]))

        all_scored:   List[Dict[str, Any]]       = []
        score_lookup: Dict[tuple, Dict[str, Any]] = {}

        for combo in combos:
            candidate = dict(zip(keys, combo))
            candidate = normalize_ensemble_weights(candidate)
            valid, _  = validate_params(candidate)
            if not valid:
                continue
            score = self._score_candidate(candidate)
            key   = tuple(candidate[k] for k in keys)
            score_lookup[key] = score
            all_scored.append({"params": candidate, "score": score, "key": key})

        if not all_scored:
            return {"passed": False, "reason": "유효한 파라미터 없음", "pareto_count": 0}

        logger.info("[Pareto] 그리드 점수 계산: %d개", len(all_scored))

        # ─ 2. Pareto 전선 추출 (Sharpe 최대, MDD 최소) ──────────────────
        pareto = _extract_pareto_front(all_scored)
        logger.info("[Pareto] Pareto 전선: %d개 / %d개", len(pareto), len(all_scored))

        # ─ 3. stability_score 계산 & 최고 후보 선택 ─────────────────────
        best_params    = None
        best_stability = -1.0

        for cand in pareto:
            stab = self._compute_stability_score(
                cand["key"], axes, keys, score_lookup
            )
            cand["stability_score"] = stab
            if stab > best_stability:
                best_stability = stab
                best_params    = cand["params"]

        logger.info("[Pareto] 최고 stability_score=%.3f (threshold=%.1f)", best_stability, stability_min)

        if best_stability < stability_min:
            return {
                "passed":          False,
                "reason":          "stability_score=%.3f < %.1f — 핀스냅 과최적화 탈락" % (best_stability, stability_min),
                "stability_score": best_stability,
                "pareto_count":    len(pareto),
                "best_params":     best_params or {},
            }

        return {
            "passed":            True,
            "best_params":       best_params,
            "stability_score":   best_stability,
            "pareto_count":      len(pareto),
            "pareto_candidates": pareto,
        }

    def _compute_stability_score(
        self,
        key:          tuple,
        axes:         Dict[str, List],
        param_keys:   List[str],
        score_lookup: Dict[tuple, Dict[str, Any]],
    ) -> float:
        """
        stability_score = 1 / std(Sharpe of ±1-step neighborhood)
        각 파라미터 차원에서 ±1 스텝 이웃들의 Sharpe 표준편차의 역수.
        """
        neighbor_sharpes: List[float] = []

        for i, pk in enumerate(param_keys):
            axis    = axes[pk]
            cur_idx = None
            for j, v in enumerate(axis):
                if abs(v - key[i]) < 1e-9:
                    cur_idx = j
                    break
            if cur_idx is None:
                continue

            for delta in (-1, +1):
                nbr_idx = cur_idx + delta
                if 0 <= nbr_idx < len(axis):
                    nbr_key_list    = list(key)
                    nbr_key_list[i] = axis[nbr_idx]
                    nbr_score = score_lookup.get(tuple(nbr_key_list))
                    if nbr_score is not None:
                        neighbor_sharpes.append(nbr_score.get("sharpe", 0.0))

        if len(neighbor_sharpes) < 2:
            return 0.0

        mean = sum(neighbor_sharpes) / len(neighbor_sharpes)
        var  = sum((s - mean) ** 2 for s in neighbor_sharpes) / max(len(neighbor_sharpes) - 1, 1)
        std  = math.sqrt(var) if var > 0 else 0.0
        return 1.0 / max(std, 1e-6)

    def _save_result(self, result: Dict[str, Any], group_name: str) -> None:
        """최적화 결과 JSON 저장."""
        ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(OPT_RESULT_DIR, "%s_%s.json" % (group_name, ts))
        try:
            with open(path, "w", encoding="utf-8") as f:
                # numpy 타입 직렬화 처리
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            logger.info("[Optimizer] 결과 저장: %s", path)
        except Exception as e:
            logger.warning("[Optimizer] 결과 저장 실패: %s", e)


# ---------------------------------------------------------------------------
# CLI 실행 지원
# ---------------------------------------------------------------------------
def _parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="미륵이 전략 파라미터 최적화")
    parser.add_argument(
        "--group", type=str, default=None,
        choices=list(COUPLED_GROUPS.keys()),
        help="최적화할 coupled group 이름",
    )
    parser.add_argument(
        "--top-n", type=int, default=20,
        help="WFA 검증할 상위 후보 수 (기본: 20)",
    )
    parser.add_argument(
        "--no-wfa", action="store_true",
        help="WFA 생략 (단순 그리드서치만)",
    )
    parser.add_argument(
        "--list-groups", action="store_true",
        help="사용 가능한 coupled group 목록 출력",
    )
    parser.add_argument(
        "--list-params", action="store_true",
        help="전체 파라미터 명세 출력",
    )
    return parser.parse_args()


def _print_param_table() -> None:
    """파라미터 명세 테이블 출력."""
    header = "%-35s %-7s %-7s %-7s %-7s %-5s %-8s  %s" % (
        "파라미터", "현재값", "하한", "상한", "스텝", "그룹", "검토주기", "설명"
    )
    print(header)
    print("-" * len(header))
    for name, spec in PARAM_SPACE.items():
        print("%-35s %-7s %-7s %-7s %-7s %-5s %-8s  %s" % (
            name,
            spec["current"], spec["low"], spec["high"], spec["step"],
            spec["group"], spec["review"],
            spec["note"][:60],
        ))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    args = _parse_args()

    if args.list_groups:
        print("\n=== Coupled Groups ===")
        for g, params in COUPLED_GROUPS.items():
            print("  %-20s: %s" % (g, ", ".join(params)))
        print()
        raise SystemExit(0)

    if args.list_params:
        _print_param_table()
        raise SystemExit(0)

    if not args.group:
        print("--group 또는 --list-groups 옵션 필요")
        raise SystemExit(1)

    # 실제 실행: weekly_trades는 DB에서 로드해야 함
    # 아래는 더미 데이터로 동작 확인용
    print("[ParamOptimizer] 주의: weekly_trades를 DB에서 로드해야 합니다.")
    print("[ParamOptimizer] 실제 백테스트 연동은 main.py 또는 별도 스크립트에서 수행하세요.")
    print()
    _print_param_table()

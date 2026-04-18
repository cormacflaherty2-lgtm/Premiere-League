from __future__ import annotations

import itertools
from typing import Any

from config import (
    MAX_LEGS_SAME_GAME,
    MAX_LEGS_SAME_TEAM,
    MIN_EDGE_PCT,
    MIN_HIT_PROB,
    PRIZEPICKS_PAYOUTS,
    SAME_GAME_CORR_PENALTY,
    SAME_TEAM_CORR_PENALTY,
    TIER_THRESHOLDS,
)


def compute_ev_multiplier(hit_prob: float, payout_mult: float) -> float:
    return round(hit_prob * payout_mult - 1.0, 3)


def should_bet(
    hit_prob: float,
    edge: float,
    min_hit_prob: float = MIN_HIT_PROB,
    min_edge: float = MIN_EDGE_PCT,
) -> bool:
    return hit_prob >= min_hit_prob and edge >= min_edge


def classify_bet_direction(
    exp_value: float,
    prop_line: float,
    hit_prob_over: float,
    hit_prob_under: float,
) -> tuple[str, float]:
    if hit_prob_over >= hit_prob_under:
        return ("OVER", hit_prob_over)
    return ("UNDER", hit_prob_under)


def tier_label(hit_prob: float) -> str:
    for threshold, label in TIER_THRESHOLDS:
        if hit_prob >= threshold:
            return label
    return "D"


def build_optimal_parlays(
    props: list[dict[str, Any]],
    sizes: list[int] | None = None,
) -> dict[int, dict[str, Any]]:
    if sizes is None:
        sizes = [2, 3, 4, 5, 6]

    pool = [p for p in props if p["hit_prob"] >= 0.60]
    best: dict[int, dict[str, Any]] = {}

    for size in sizes:
        if len(pool) < size:
            continue

        best_ev = -float("inf")
        best_combo: list[dict[str, Any]] = []

        for combo in itertools.combinations(pool, size):
            # No duplicate (player, prop_type) pair
            player_prop_pairs = [(c["player_id"], c["prop_type"]) for c in combo]
            if len(set(player_prop_pairs)) < len(player_prop_pairs):
                continue

            # Count legs per (match_key, prop_type)
            game_type_counts: dict[tuple[str, str], int] = {}
            team_counts: dict[str, int] = {}
            for c in combo:
                gt_key = (str(c["match_id"]), c["prop_type"])
                game_type_counts[gt_key] = game_type_counts.get(gt_key, 0) + 1
                team_counts[c["team"]] = team_counts.get(c["team"], 0) + 1

            if any(v > MAX_LEGS_SAME_GAME for v in game_type_counts.values()):
                continue
            if any(v > MAX_LEGS_SAME_TEAM for v in team_counts.values()):
                continue

            combined_prob = 1.0
            for c in combo:
                combined_prob *= c["hit_prob"]

            # Correlation penalties
            for (_, _), count in game_type_counts.items():
                if count > 1:
                    combined_prob *= SAME_GAME_CORR_PENALTY ** (count - 1)
            for _, count in team_counts.items():
                if count > 1:
                    combined_prob *= SAME_TEAM_CORR_PENALTY ** (count - 1)

            payout = PRIZEPICKS_PAYOUTS[size]
            ev = combined_prob * payout

            if ev > best_ev:
                best_ev = ev
                best_combo = list(combo)

        if best_combo:
            combined_prob = 1.0
            for c in best_combo:
                combined_prob *= c["hit_prob"]

            game_type_counts2: dict[tuple[str, str], int] = {}
            team_counts2: dict[str, int] = {}
            for c in best_combo:
                gt_key = (str(c["match_id"]), c["prop_type"])
                game_type_counts2[gt_key] = game_type_counts2.get(gt_key, 0) + 1
                team_counts2[c["team"]] = team_counts2.get(c["team"], 0) + 1
            for _, count in game_type_counts2.items():
                if count > 1:
                    combined_prob *= SAME_GAME_CORR_PENALTY ** (count - 1)
            for _, count in team_counts2.items():
                if count > 1:
                    combined_prob *= SAME_TEAM_CORR_PENALTY ** (count - 1)

            payout = PRIZEPICKS_PAYOUTS[size]
            best[size] = {
                "legs": best_combo,
                "combined_hit_prob": round(combined_prob, 4),
                "payout_mult": payout,
                "ev_multiplier": compute_ev_multiplier(combined_prob, payout),
            }

    return best

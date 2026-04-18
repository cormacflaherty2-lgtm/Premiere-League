from __future__ import annotations

import argparse
import os
from typing import Any

from scipy.stats import nbinom, poisson

from config import (
    FORM_WEIGHT,
    MODEL_WEIGHT,
    NB_VARIANCE_FACTOR,
    PRIZEPICKS_PAYOUTS,
    ROLE_CONFIG,
    URGENCY_MULT,
    VENUE_BLEND,
)
from data_loader import load_all, load_referees
from features import (
    build_player_form,
    build_referee_features,
    build_schedule_features,
    build_team_context,
    build_venue_features,
    minutes_adj,
    non_starter_override,
    resolve_role,
)
from output import export_csv, export_parlays, print_rich_table
from prizetiers import (
    build_optimal_parlays,
    classify_bet_direction,
    compute_ev_multiplier,
    should_bet,
    tier_label,
)


def fit_nb_params(
    mean: float, variance: float | None = None
) -> tuple[float | None, float | None]:
    if variance is None:
        variance = mean * NB_VARIANCE_FACTOR
    if variance <= mean:
        return (None, None)
    r = mean**2 / (variance - mean)
    p = r / (r + mean)
    return (r, p)


def p_over(mean: float, line: float, use_nb: bool = True) -> float:
    if mean <= 0:
        return 0.001
    threshold = int(line + 0.5)
    if use_nb:
        r, p = fit_nb_params(mean)
        if r is not None and p is not None:
            return float(1.0 - nbinom.cdf(threshold - 1, r, p))
    return float(1.0 - poisson.cdf(threshold - 1, mean))


def p_under(mean: float, line: float, use_nb: bool = True) -> float:
    return 1.0 - p_over(mean, line, use_nb)


def edge_pct(exp: float, line: float) -> float:
    if line == 0:
        return 0.0
    return round((exp - line) / line * 100, 2)


def compute_expected_shots_sot(
    player: dict[str, Any],
    lineup: dict[str, Any],
    team_ctx: dict[str, float],
    schedule: dict[str, float],
    ref_ctx: dict[str, float],
    is_home: bool,
) -> tuple[float, float, str]:
    is_starter = bool(lineup.get("is_confirmed_starter", True))
    if not is_starter:
        return (0.0, 0.0, "NON_STARTER")

    tactical_note = lineup.get("tactical_role_override") or lineup.get("playing_position_today")
    player_role = str(player["role"])
    resolved_role = resolve_role(player_role, str(tactical_note) if tactical_note else None)
    if resolved_role not in ROLE_CONFIG:
        resolved_role = player_role
    role_share, role_sot_rate, _ = ROLE_CONFIG[resolved_role]

    form = build_player_form(player)
    venue = build_venue_features(player, is_home)

    player_baseline_shots = form["exp_weighted_shots"]
    player_baseline_sot = form["exp_weighted_sot"]

    urgency_key = str(lineup.get("urgency_context", "neutral"))
    if urgency_key not in URGENCY_MULT:
        urgency_key = "neutral"
    urgency_m = URGENCY_MULT[urgency_key]

    model_exp_shots = (
        team_ctx["team_shots_base"]
        * team_ctx["team_context_mult"]
        * urgency_m
        * schedule["rest_mult"]
        * ref_ctx["set_piece_bonus_mult"]
        * role_share
    )

    blended_shots = FORM_WEIGHT * player_baseline_shots + MODEL_WEIGHT * model_exp_shots
    blended_shots = (1 - VENUE_BLEND) * blended_shots + VENUE_BLEND * venue["venue_adj_shots"]

    if player_baseline_sot > 0 and player_baseline_shots > 0:
        player_sot_rate = player_baseline_sot / player_baseline_shots
        blended_sot_rate = 0.60 * player_sot_rate + 0.40 * role_sot_rate
    else:
        blended_sot_rate = role_sot_rate

    blended_sot = blended_shots * blended_sot_rate
    blended_sot = (1 - VENUE_BLEND) * blended_sot + VENUE_BLEND * venue["venue_adj_sot"]

    expected_minutes = float(lineup.get("expected_minutes", 90))
    blended_shots = minutes_adj(blended_shots, expected_minutes)
    blended_sot = minutes_adj(blended_sot, expected_minutes)

    blended_sot = min(blended_sot, blended_shots)
    blended_shots = max(0.0, blended_shots)
    blended_sot = max(0.0, blended_sot)

    return (round(blended_shots, 3), round(blended_sot, 3), "STARTER")


def run_predictions(
    players_csv: str,
    matches_csv: str,
    lineups_csv: str,
    team_stats_csv: str,
    prop_lines_input: str,
    output_dir: str,
    min_tier: str | None = None,
    parlays_only: bool = False,
    verbose: bool = False,
) -> None:
    players, matches, lineups, team_stats, prop_lines = load_all(
        players_csv, matches_csv, lineups_csv, team_stats_csv, prop_lines_input
    )
    data_dir = os.path.dirname(prop_lines_input)
    ref_db = load_referees(data_dir if data_dir else "data")

    prop_map: dict[str, list[dict[str, Any]]] = {}
    for prop in prop_lines:
        pid = str(prop["player_id"])
        prop_map.setdefault(pid, []).append(prop)

    results: list[dict[str, Any]] = []

    for lineup in lineups:
        pid = str(lineup["player_id"])
        mid = str(lineup["match_id"])

        player = players.get(pid)
        match = matches.get(mid)
        if player is None or match is None:
            continue

        home_team = str(match["home_team"])
        away_team = str(match["away_team"])
        player_team = str(lineup["team"])
        is_home = player_team == home_team
        opp_team = away_team if is_home else home_team

        my_stats = team_stats.get(player_team)
        opp_stats = team_stats.get(opp_team)
        if my_stats is None or opp_stats is None:
            continue

        poss_key = "home_possession_pct" if is_home else "away_possession_pct"
        possession_pct = float(match[poss_key])

        team_ctx = build_team_context(my_stats, opp_stats, is_home, possession_pct)

        rest_key = "home_rest_days" if is_home else "away_rest_days"
        rest_days = int(match.get(rest_key, 4))
        schedule = build_schedule_features(rest_days)

        referee_id = str(match.get("referee_id", "unknown"))
        ref_ctx = build_referee_features(referee_id, ref_db)

        urgency_key = (
            "match_importance_home" if is_home else "match_importance_away"
        )
        lineup["urgency_context"] = str(match.get(urgency_key, "neutral"))

        exp_shots, exp_sot, status = compute_expected_shots_sot(
            player, lineup, team_ctx, schedule, ref_ctx, is_home
        )

        if verbose:
            form = build_player_form(player)
            venue = build_venue_features(player, is_home)
            print(f"\n[VERBOSE] {player['player_name']} ({pid})")
            print(f"  form={form}")
            print(f"  venue={venue}")
            print(f"  team_ctx={team_ctx}")
            print(f"  schedule={schedule}")
            print(f"  ref_ctx={ref_ctx}")
            print(f"  status={status} exp_shots={exp_shots} exp_sot={exp_sot}")

        tactical_note = lineup.get("tactical_role_override") or lineup.get("playing_position_today")
        resolved_role = resolve_role(
            str(player["role"]), str(tactical_note) if tactical_note else None
        )

        player_props = prop_map.get(pid, [])
        for prop in player_props:
            prop_type = str(prop["prop_type"])
            line = float(prop["line"])

            if prop_type == "Shots":
                exp = exp_shots
            elif prop_type == "SOT":
                exp = exp_sot
            else:
                continue

            prob_over = p_over(exp, line)
            prob_under = p_under(exp, line)
            direction, hit_prob = classify_bet_direction(exp, line, prob_over, prob_under)

            if direction == "OVER":
                edge = edge_pct(exp, line)
            else:
                edge = edge_pct(line, exp)

            t = tier_label(hit_prob)
            ev_2 = compute_ev_multiplier(hit_prob, PRIZEPICKS_PAYOUTS[2])
            ev_3 = compute_ev_multiplier(hit_prob, PRIZEPICKS_PAYOUTS[3])

            results.append(
                {
                    "player_id": pid,
                    "player_name": player["player_name"],
                    "team": player_team,
                    "opponent": opp_team,
                    "is_home": is_home,
                    "match_id": mid,
                    "role": resolved_role,
                    "prop_type": prop_type,
                    "direction": direction,
                    "exp_value": exp,
                    "prop_line": line,
                    "edge_pct": edge,
                    "hit_prob": hit_prob,
                    "tier": t,
                    "status": status,
                    "ev_2leg": ev_2,
                    "ev_3leg": ev_3,
                }
            )

    results.sort(key=lambda r: r["hit_prob"], reverse=True)

    parlays = build_optimal_parlays(results)

    os.makedirs(output_dir, exist_ok=True)
    predictions_path = os.path.join(output_dir, "predictions.csv")
    parlays_path = os.path.join(output_dir, "parlays.csv")

    export_csv(results, predictions_path)
    export_parlays(parlays, parlays_path)

    tier_order = {"S+": 0, "S": 1, "A": 2, "B": 3, "C": 4, "D": 5}

    filtered = results
    if min_tier:
        min_rank = tier_order.get(min_tier, 5)
        filtered = [r for r in results if tier_order.get(r["tier"], 5) <= min_rank]

    if not parlays_only:
        print_rich_table(filtered, parlays)
    else:
        print_rich_table([], parlays)


def main() -> None:
    parser = argparse.ArgumentParser(description="Premier League Shots & SOT Prop Model")
    parser.add_argument("--players", required=True)
    parser.add_argument("--matches", required=True)
    parser.add_argument("--lineups", required=True)
    parser.add_argument("--team-stats", required=True, dest="team_stats")
    parser.add_argument("--lines", required=True)
    parser.add_argument("--output", default="output/")
    parser.add_argument(
        "--min-tier",
        choices=["S+", "S", "A", "B", "C", "D"],
        default=None,
        dest="min_tier",
    )
    parser.add_argument("--parlays-only", action="store_true", dest="parlays_only")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    run_predictions(
        players_csv=args.players,
        matches_csv=args.matches,
        lineups_csv=args.lineups,
        team_stats_csv=args.team_stats,
        prop_lines_input=args.lines,
        output_dir=args.output,
        min_tier=args.min_tier,
        parlays_only=args.parlays_only,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()

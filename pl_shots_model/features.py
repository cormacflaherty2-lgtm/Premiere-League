from __future__ import annotations

from typing import Any

from config import (
    L3_WEIGHT,
    L5_WEIGHT,
    L10_WEIGHT,
    PL_LEAGUE_AVG_SHOTS_CONCEDED,
    ROLE_CONFIG,
    ROLE_OVERRIDE_MAP,
    STARTER_MIN_THRESHOLD,
    URGENCY_MULT,
)

REF_DB: dict[str, Any] = {}


def compute_exp_weighted_avg(values: list[float], weights: list[float]) -> float:
    assert abs(sum(weights) - 1.0) < 1e-6, "weights must sum to 1.0"
    return sum(v * w for v, w in zip(values, weights))


def safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def build_player_form(player: dict[str, Any]) -> dict[str, float]:
    l3s = float(player["l3_avg_shots"])
    l5s = float(player["l5_avg_shots"])
    l10s = float(player["l10_avg_shots"])
    l3t = float(player["l3_avg_sot"])
    l5t = float(player["l5_avg_sot"])
    l10t = float(player["l10_avg_sot"])

    exp_weighted_shots = compute_exp_weighted_avg(
        [l3s, l5s, l10s], [L3_WEIGHT, L5_WEIGHT, L10_WEIGHT]
    )
    exp_weighted_sot = compute_exp_weighted_avg(
        [l3t, l5t, l10t], [L3_WEIGHT, L5_WEIGHT, L10_WEIGHT]
    )

    shots_trend = l3s - l10s
    sot_trend = l3t - l10t

    season_shots = float(player["season_avg_shots"])
    season_sot = float(player["season_avg_sot"])

    recent_vals = [l3s, l5s, l10s]
    mean_recent = exp_weighted_shots
    variance_recent = compute_exp_weighted_avg(
        [(v - mean_recent) ** 2 for v in recent_vals], [L3_WEIGHT, L5_WEIGHT, L10_WEIGHT]
    )
    shots_consistency = 1.0 / (1.0 + variance_recent**0.5) if variance_recent >= 0 else 1.0

    sot_conversion_rate = safe_div(season_sot, season_shots)
    npxg_per_shot = float(player.get("npxg_per_shot", 0.10))
    touches_in_box = float(player.get("touches_in_box_pg", 2.0))
    big_chances_pg = float(player.get("big_chances_pg", 0.20))

    return {
        "exp_weighted_shots": exp_weighted_shots,
        "exp_weighted_sot": exp_weighted_sot,
        "shots_trend": shots_trend,
        "sot_trend": sot_trend,
        "shots_consistency": shots_consistency,
        "sot_conversion_rate": sot_conversion_rate,
        "npxg_per_shot": npxg_per_shot,
        "touches_in_box": touches_in_box,
        "big_chances_pg": big_chances_pg,
    }


def build_venue_features(
    player: dict[str, Any], is_home: bool
) -> dict[str, float]:
    home_shots = float(player["home_avg_shots"])
    away_shots = float(player["away_avg_shots"])
    home_sot = float(player["home_avg_sot"])
    away_sot = float(player["away_avg_sot"])

    if is_home:
        venue_adj_shots = home_shots
        venue_adj_sot = home_sot
    else:
        venue_adj_shots = away_shots
        venue_adj_sot = away_sot

    venue_shot_diff = home_shots - away_shots

    return {
        "venue_adj_shots": venue_adj_shots,
        "venue_adj_sot": venue_adj_sot,
        "venue_shot_diff": venue_shot_diff,
    }


def resolve_role(player_role: str, tactical_note: str | None) -> str:
    if tactical_note:
        note_lower = tactical_note.lower()
        for keyword, override_role in ROLE_OVERRIDE_MAP.items():
            if keyword in note_lower:
                return override_role
    return player_role


def build_team_context(
    team_stats: dict[str, Any],
    opponent_stats: dict[str, Any],
    is_home: bool,
    possession_pct: float,
) -> dict[str, float]:
    team_shots_base: float = (
        float(team_stats["home_shots_pg"]) if is_home else float(team_stats["away_shots_pg"])
    )

    # opponent's concession stats — from the opponent's perspective when defending at home/away
    if is_home:
        # team is at home, opponent is away — opponent defends as away team
        opp_conceded = float(opponent_stats["away_shots_conceded_pg"])
        opp_sot_conceded_pg = float(opponent_stats["away_sot_conceded_pg"])
    else:
        # team is away, opponent is at home — opponent defends as home team
        opp_conceded = float(opponent_stats["home_shots_conceded_pg"])
        opp_sot_conceded_pg = float(opponent_stats["home_sot_conceded_pg"])

    opp_adj = _clamp(opp_conceded / PL_LEAGUE_AVG_SHOTS_CONCEDED, 0.75, 1.30)
    poss_mult = _clamp(1.0 + (possession_pct - 50.0) * 0.018, 0.80, 1.25)
    home_mult = 1.13 if is_home else 0.87

    ppda = float(team_stats.get("press_intensity_ppda", 10.0))
    press_mult = _clamp(1.0 + (10.0 - ppda) * 0.008, 0.95, 1.08)

    team_context_mult = opp_adj * poss_mult * home_mult * press_mult

    return {
        "team_shots_base": team_shots_base,
        "opp_adj": opp_adj,
        "poss_mult": poss_mult,
        "home_mult": home_mult,
        "press_mult": press_mult,
        "team_context_mult": team_context_mult,
        "opp_sot_conceded_pg": opp_sot_conceded_pg,
    }


def build_schedule_features(rest_days: int) -> dict[str, float]:
    if rest_days <= 2:
        rest_mult = 0.88
    elif rest_days == 3:
        rest_mult = 0.94
    elif rest_days >= 7:
        rest_mult = 1.04
    else:
        rest_mult = 1.00
    return {"rest_days": float(rest_days), "rest_mult": rest_mult}


def build_referee_features(
    referee_id: str, ref_db: dict[str, Any] | None = None
) -> dict[str, float]:
    if ref_db is None:
        ref_db = REF_DB
    ref_data = ref_db.get(str(referee_id), {})
    ref_fouls_pg = float(ref_data.get("avg_fouls_per_game", 22.0))
    ref_cards_pg = float(ref_data.get("avg_cards_per_game", 3.5))
    set_piece_bonus_mult = _clamp(1.0 + (ref_fouls_pg - 22.0) * 0.003, 0.97, 1.06)
    return {
        "referee_id": float(hash(referee_id) % 10000),
        "ref_fouls_pg": ref_fouls_pg,
        "ref_cards_pg": ref_cards_pg,
        "set_piece_bonus_mult": set_piece_bonus_mult,
    }


def minutes_adj(base_exp: float, expected_minutes: float) -> float:
    return base_exp * (expected_minutes / 90.0)


def non_starter_override(
    is_confirmed_starter: bool,
    expected_minutes: float,
    exp_shots: float,
    exp_sot: float,
) -> tuple[float, float, str]:
    if not is_confirmed_starter:
        return (0.0, 0.0, "NON_STARTER")
    if expected_minutes < STARTER_MIN_THRESHOLD:
        scale = expected_minutes / 90.0
        return (exp_shots * scale, exp_sot * scale, "LIMITED_MINUTES")
    return (exp_shots, exp_sot, "STARTER")

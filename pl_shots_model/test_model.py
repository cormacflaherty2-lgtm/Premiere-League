from __future__ import annotations

import pytest

from config import (
    FORM_WEIGHT,
    MODEL_WEIGHT,
    ROLE_CONFIG,
    URGENCY_MULT,
)
from features import (
    build_schedule_features,
    build_team_context,
    minutes_adj,
    resolve_role,
)
from model import (
    compute_expected_shots_sot,
    edge_pct,
    fit_nb_params,
    p_over,
)
from prizetiers import build_optimal_parlays, tier_label


def _make_player(role: str = "CF", shots: float = 4.0, sot: float = 1.5) -> dict:
    return {
        "player_id": "P_TEST",
        "player_name": "Test Player",
        "team": "TestFC",
        "role": role,
        "season_avg_shots": shots,
        "season_avg_sot": sot,
        "season_avg_xg": 0.5,
        "l3_avg_shots": shots * 1.1,
        "l3_avg_sot": sot * 1.1,
        "l5_avg_shots": shots,
        "l5_avg_sot": sot,
        "l10_avg_shots": shots * 0.9,
        "l10_avg_sot": sot * 0.9,
        "home_avg_shots": shots * 1.1,
        "home_avg_sot": sot * 1.1,
        "away_avg_shots": shots * 0.9,
        "away_avg_sot": sot * 0.9,
        "shots_per_touch": 0.30,
        "touches_in_box_pg": 3.0,
        "npxg_per_shot": 0.12,
        "avg_minutes_played": 85,
        "big_chances_pg": 0.50,
        "penalty_kicks_pg": 0.02,
        "set_piece_shots_pg": 0.30,
        "open_play_shots_pg": shots * 0.85,
    }


def _make_lineup(
    is_starter: bool = True,
    minutes: float = 90.0,
    tactical: str | None = None,
) -> dict:
    return {
        "player_id": "P_TEST",
        "match_id": "M_TEST",
        "team": "TestFC",
        "is_confirmed_starter": is_starter,
        "expected_minutes": minutes,
        "tactical_role_override": tactical,
        "playing_position_today": None,
        "urgency_context": "neutral",
    }


def _make_team_stats(ppda: float = 10.0) -> dict:
    return {
        "team": "TestFC",
        "home_shots_pg": 14.0,
        "away_shots_pg": 11.0,
        "home_sot_pg": 5.0,
        "away_sot_pg": 4.0,
        "home_shots_conceded_pg": 11.0,
        "away_shots_conceded_pg": 13.0,
        "home_sot_conceded_pg": 3.8,
        "away_sot_conceded_pg": 4.4,
        "press_intensity_ppda": ppda,
    }


def _run_model(
    role: str = "CF",
    is_home: bool = True,
    is_starter: bool = True,
    minutes: float = 90.0,
    tactical: str | None = None,
    shots: float = 4.0,
    sot: float = 1.5,
) -> tuple[float, float, str]:
    player = _make_player(role, shots, sot)
    lineup = _make_lineup(is_starter, minutes, tactical)
    team_stats = _make_team_stats()
    opp_stats = _make_team_stats()
    from features import build_referee_features
    team_ctx = build_team_context(team_stats, opp_stats, is_home, 50.0)
    schedule = build_schedule_features(4)
    ref_ctx = build_referee_features("REF_TEST")
    return compute_expected_shots_sot(player, lineup, team_ctx, schedule, ref_ctx, is_home)


# --- Test cases ---

def test_non_starter_returns_zero() -> None:
    exp_shots, exp_sot, status = _run_model(is_starter=False)
    assert exp_shots == 0.0
    assert exp_sot == 0.0
    assert status == "NON_STARTER"


def test_non_starter_returns_zero_all_roles() -> None:
    for role in ROLE_CONFIG:
        shots, sot, status = _run_model(role=role, is_starter=False)
        assert shots == 0.0
        assert sot == 0.0
        assert status == "NON_STARTER"


def test_sot_never_exceeds_shots() -> None:
    roles = list(ROLE_CONFIG.keys())
    shot_levels = [1.0, 2.5, 4.0, 6.0]
    for role in roles:
        for base_shots in shot_levels:
            base_sot = base_shots * 0.4
            shots, sot, _ = _run_model(role=role, shots=base_shots, sot=base_sot)
            assert sot <= shots + 1e-9, f"role={role}: sot={sot} > shots={shots}"


def test_role_override_tactical_note() -> None:
    resolved = resolve_role("CF", "playing right back today")
    assert resolved == "FB_defensive"


def test_role_override_wingback() -> None:
    resolved = resolve_role("WF_wide", "deployed as a wingback on the left")
    assert resolved == "FB_attacking"


def test_poisson_fallback() -> None:
    r, p = fit_nb_params(mean=3.0, variance=2.0)
    assert r is None
    assert p is None
    prob = p_over(3.0, 2.5, use_nb=True)
    assert 0.0 < prob < 1.0


def test_possession_mult_clamped_low() -> None:
    from config import PL_LEAGUE_AVG_SHOTS_CONCEDED
    from features import build_team_context

    team = _make_team_stats()
    opp = _make_team_stats()
    ctx = build_team_context(team, opp, True, 10.0)
    expected_clamp = 0.80
    assert abs(ctx["poss_mult"] - expected_clamp) < 1e-9


def test_possession_mult_clamped_high() -> None:
    from features import build_team_context

    team = _make_team_stats()
    opp = _make_team_stats()
    ctx = build_team_context(team, opp, True, 90.0)
    expected_clamp = 1.25
    assert abs(ctx["poss_mult"] - expected_clamp) < 1e-9


def test_rest_mult_under_3_days() -> None:
    sched = build_schedule_features(2)
    assert abs(sched["rest_mult"] - 0.88) < 1e-9


def test_rest_mult_3_days() -> None:
    sched = build_schedule_features(3)
    assert abs(sched["rest_mult"] - 0.94) < 1e-9


def test_rest_mult_7_plus_days() -> None:
    sched = build_schedule_features(7)
    assert abs(sched["rest_mult"] - 1.04) < 1e-9


def test_rest_mult_normal() -> None:
    sched = build_schedule_features(5)
    assert abs(sched["rest_mult"] - 1.00) < 1e-9


def test_minutes_adj_sub() -> None:
    result = minutes_adj(3.0, 30.0)
    assert abs(result - 3.0 * (30.0 / 90.0)) < 1e-9


def test_blend_weights_sum_to_one() -> None:
    assert abs(FORM_WEIGHT + MODEL_WEIGHT - 1.0) < 1e-9


def test_tier_s_plus_above_92() -> None:
    assert tier_label(0.95) == "S+"
    assert tier_label(0.92) == "S+"


def test_tier_s_between_85_92() -> None:
    assert tier_label(0.88) == "S"
    assert tier_label(0.85) == "S"


def test_tier_a_between_75_85() -> None:
    assert tier_label(0.80) == "A"
    assert tier_label(0.75) == "A"


def test_tier_d_below_55() -> None:
    assert tier_label(0.40) == "D"


def test_parlay_no_duplicate_player_prop() -> None:
    props = [
        {
            "player_id": "P1",
            "player_name": "Alpha",
            "team": "TeamA",
            "match_id": "M1",
            "prop_type": "Shots",
            "direction": "OVER",
            "prop_line": 2.5,
            "hit_prob": 0.80,
        },
        {
            "player_id": "P1",
            "player_name": "Alpha",
            "team": "TeamA",
            "match_id": "M1",
            "prop_type": "Shots",
            "direction": "OVER",
            "prop_line": 2.5,
            "hit_prob": 0.78,
        },
        {
            "player_id": "P2",
            "player_name": "Beta",
            "team": "TeamB",
            "match_id": "M1",
            "prop_type": "SOT",
            "direction": "OVER",
            "prop_line": 1.5,
            "hit_prob": 0.75,
        },
    ]
    parlays = build_optimal_parlays(props, sizes=[2])
    if 2 in parlays:
        legs = parlays[2]["legs"]
        pairs = [(l["player_id"], l["prop_type"]) for l in legs]
        assert len(pairs) == len(set(pairs)), "Duplicate (player, prop_type) found in parlay"


def test_parlay_max_2_same_game() -> None:
    # Three props same match_id and same prop_type — no 3-leg parlay should form
    props = [
        {
            "player_id": f"P{i}",
            "player_name": f"Player{i}",
            "team": "TeamA",
            "match_id": "M1",
            "prop_type": "Shots",
            "direction": "OVER",
            "prop_line": 2.5,
            "hit_prob": 0.80,
        }
        for i in range(1, 4)
    ]
    parlays = build_optimal_parlays(props, sizes=[3])
    if 3 in parlays:
        legs = parlays[3]["legs"]
        game_type_counts: dict[tuple[str, str], int] = {}
        for leg in legs:
            key = (str(leg["match_id"]), leg["prop_type"])
            game_type_counts[key] = game_type_counts.get(key, 0) + 1
        for key, count in game_type_counts.items():
            assert count <= 2, f"More than 2 legs from same (match, prop_type): {key} count={count}"


def test_edge_pct_over_positive() -> None:
    result = edge_pct(4.0, 3.0)
    assert abs(result - 33.33) < 0.01


def test_edge_pct_zero_line() -> None:
    assert edge_pct(4.0, 0.0) == 0.0


def test_synthetic_line_all_roles_covered() -> None:
    expected_roles = {
        "CF", "SS", "WF_inside", "WF_wide", "AM",
        "CM_box", "CM_deep", "DM", "FB_attacking", "FB_defensive",
        "CB_aerial", "CB_defensive", "GK",
    }
    assert set(ROLE_CONFIG.keys()) == expected_roles


def test_limited_minutes_scales_output() -> None:
    shots_90, sot_90, _ = _run_model(minutes=90.0)
    shots_45, sot_45, status = _run_model(minutes=45.0)
    assert status == "STARTER"
    assert abs(shots_45 / shots_90 - 0.5) < 0.05


def test_nb_params_valid() -> None:
    r, p = fit_nb_params(3.0)
    assert r is not None and p is not None
    assert r > 0 and 0 < p < 1


def test_p_over_zero_mean() -> None:
    assert p_over(0.0, 2.5) == 0.001


def test_urgency_mult_all_keys_present() -> None:
    required = {
        "neutral", "must_win_title", "must_win_top4", "must_win_europe",
        "must_win_relegation", "dead_rubber", "nothing_to_play_for",
        "revenge_derby", "cup_final",
    }
    assert required.issubset(set(URGENCY_MULT.keys()))

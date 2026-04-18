"""One-time script to produce synthetic historical data for backtest/data/."""
from __future__ import annotations

import json
import os
from typing import Any

import pandas as pd

BASE_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(BASE_DIR, exist_ok=True)

# ── Team stats ──────────────────────────────────────────────────────────────
TEAM_STATS: dict[str, dict[str, Any]] = {
    "TeamA": {
        "season": "2023-24",
        "home_shots_pg": 16.5, "away_shots_pg": 14.0,
        "home_sot_pg": 6.0,    "away_sot_pg": 5.2,
        "home_shots_conceded_pg": 9.5,  "away_shots_conceded_pg": 11.5,
        "home_sot_conceded_pg": 3.4,    "away_sot_conceded_pg": 4.0,
        "avg_possession_home": 62, "avg_possession_away": 55,
        "press_intensity_ppda": 7.8, "transition_attacks_pg": 4.5,
        "set_piece_goals_pct": 0.22, "xg_overperformance": 0.28,
    },
    "TeamB": {
        "season": "2023-24",
        "home_shots_pg": 16.0, "away_shots_pg": 13.5,
        "home_sot_pg": 5.8,    "away_sot_pg": 5.0,
        "home_shots_conceded_pg": 10.0, "away_shots_conceded_pg": 12.5,
        "home_sot_conceded_pg": 3.6,    "away_sot_conceded_pg": 4.2,
        "avg_possession_home": 58, "avg_possession_away": 52,
        "press_intensity_ppda": 8.2, "transition_attacks_pg": 4.2,
        "set_piece_goals_pct": 0.20, "xg_overperformance": 0.22,
    },
    "TeamC": {
        "season": "2023-24",
        "home_shots_pg": 13.5, "away_shots_pg": 11.5,
        "home_sot_pg": 4.8,    "away_sot_pg": 4.2,
        "home_shots_conceded_pg": 11.5, "away_shots_conceded_pg": 13.0,
        "home_sot_conceded_pg": 4.0,    "away_sot_conceded_pg": 4.6,
        "avg_possession_home": 54, "avg_possession_away": 48,
        "press_intensity_ppda": 10.2, "transition_attacks_pg": 5.2,
        "set_piece_goals_pct": 0.16, "xg_overperformance": 0.08,
    },
    "TeamD": {
        "season": "2023-24",
        "home_shots_pg": 11.0, "away_shots_pg": 9.5,
        "home_sot_pg": 4.0,    "away_sot_pg": 3.5,
        "home_shots_conceded_pg": 14.5, "away_shots_conceded_pg": 16.0,
        "home_sot_conceded_pg": 5.0,    "away_sot_conceded_pg": 5.5,
        "avg_possession_home": 46, "avg_possession_away": 42,
        "press_intensity_ppda": 13.5, "transition_attacks_pg": 2.8,
        "set_piece_goals_pct": 0.14, "xg_overperformance": -0.18,
    },
}

# ── Players ──────────────────────────────────────────────────────────────────
PLAYER_DEFS: dict[str, dict[str, Any]] = {
    "P_BT1": {
        "player_name": "Harry Kane",   "team": "TeamA", "role": "CF",
        "season_avg_shots": 4.9, "season_avg_sot": 1.8,
        "home_avg_shots": 5.3, "home_avg_sot": 1.9,
        "away_avg_shots": 4.5, "away_avg_sot": 1.6,
        "season_avg_xg": 0.72, "shots_per_touch": 0.40,
        "touches_in_box_pg": 5.2, "npxg_per_shot": 0.16,
        "avg_minutes_played": 87, "big_chances_pg": 0.80,
        "penalty_kicks_pg": 0.04, "set_piece_shots_pg": 0.35,
        "open_play_shots_pg": 4.55,
    },
    "P_BT2": {
        "player_name": "Mo Salah",     "team": "TeamA", "role": "WF_inside",
        "season_avg_shots": 3.6, "season_avg_sot": 1.5,
        "home_avg_shots": 3.8, "home_avg_sot": 1.6,
        "away_avg_shots": 3.4, "away_avg_sot": 1.4,
        "season_avg_xg": 0.52, "shots_per_touch": 0.32,
        "touches_in_box_pg": 4.5, "npxg_per_shot": 0.14,
        "avg_minutes_played": 85, "big_chances_pg": 0.60,
        "penalty_kicks_pg": 0.03, "set_piece_shots_pg": 0.28,
        "open_play_shots_pg": 3.32,
    },
    "P_BT3": {
        "player_name": "Erling Haaland", "team": "TeamB", "role": "CF",
        "season_avg_shots": 5.9, "season_avg_sot": 2.7,
        "home_avg_shots": 6.3, "home_avg_sot": 2.9,
        "away_avg_shots": 5.5, "away_avg_sot": 2.5,
        "season_avg_xg": 0.88, "shots_per_touch": 0.45,
        "touches_in_box_pg": 6.0, "npxg_per_shot": 0.18,
        "avg_minutes_played": 86, "big_chances_pg": 1.00,
        "penalty_kicks_pg": 0.05, "set_piece_shots_pg": 0.45,
        "open_play_shots_pg": 5.45,
    },
    "P_BT4": {
        "player_name": "Kevin De Bruyne", "team": "TeamB", "role": "CM_box",
        "season_avg_shots": 1.9, "season_avg_sot": 0.7,
        "home_avg_shots": 2.1, "home_avg_sot": 0.8,
        "away_avg_shots": 1.7, "away_avg_sot": 0.6,
        "season_avg_xg": 0.22, "shots_per_touch": 0.16,
        "touches_in_box_pg": 2.8, "npxg_per_shot": 0.09,
        "avg_minutes_played": 82, "big_chances_pg": 0.28,
        "penalty_kicks_pg": 0.01, "set_piece_shots_pg": 0.42,
        "open_play_shots_pg": 1.48,
    },
    "P_BT5": {
        "player_name": "Son Heung-min", "team": "TeamC", "role": "SS",
        "season_avg_shots": 3.7, "season_avg_sot": 1.6,
        "home_avg_shots": 4.0, "home_avg_sot": 1.7,
        "away_avg_shots": 3.4, "away_avg_sot": 1.5,
        "season_avg_xg": 0.50, "shots_per_touch": 0.33,
        "touches_in_box_pg": 4.2, "npxg_per_shot": 0.13,
        "avg_minutes_played": 84, "big_chances_pg": 0.62,
        "penalty_kicks_pg": 0.03, "set_piece_shots_pg": 0.30,
        "open_play_shots_pg": 3.40,
    },
    "P_BT6": {
        "player_name": "Bukayo Saka",   "team": "TeamC", "role": "WF_inside",
        "season_avg_shots": 2.9, "season_avg_sot": 1.2,
        "home_avg_shots": 3.1, "home_avg_sot": 1.3,
        "away_avg_shots": 2.7, "away_avg_sot": 1.1,
        "season_avg_xg": 0.38, "shots_per_touch": 0.26,
        "touches_in_box_pg": 3.5, "npxg_per_shot": 0.11,
        "avg_minutes_played": 83, "big_chances_pg": 0.48,
        "penalty_kicks_pg": 0.02, "set_piece_shots_pg": 0.25,
        "open_play_shots_pg": 2.65,
    },
    "P_BT7": {
        "player_name": "James Tarkowski", "team": "TeamD", "role": "CB_defensive",
        "season_avg_shots": 0.5, "season_avg_sot": 0.1,
        "home_avg_shots": 0.6, "home_avg_sot": 0.1,
        "away_avg_shots": 0.4, "away_avg_sot": 0.1,
        "season_avg_xg": 0.05, "shots_per_touch": 0.04,
        "touches_in_box_pg": 0.8, "npxg_per_shot": 0.05,
        "avg_minutes_played": 88, "big_chances_pg": 0.08,
        "penalty_kicks_pg": 0.00, "set_piece_shots_pg": 0.22,
        "open_play_shots_pg": 0.28,
    },
    "P_BT8": {
        "player_name": "Declan Rice",   "team": "TeamD", "role": "CM_box",
        "season_avg_shots": 1.5, "season_avg_sot": 0.5,
        "home_avg_shots": 1.7, "home_avg_sot": 0.6,
        "away_avg_shots": 1.3, "away_avg_sot": 0.4,
        "season_avg_xg": 0.14, "shots_per_touch": 0.12,
        "touches_in_box_pg": 1.8, "npxg_per_shot": 0.07,
        "avg_minutes_played": 86, "big_chances_pg": 0.22,
        "penalty_kicks_pg": 0.00, "set_piece_shots_pg": 0.35,
        "open_play_shots_pg": 1.15,
    },
}

# Actual per-matchweek shots/SOT (index 0 = MW1, index 9 = MW10)
# P_BT7 MW3(idx2), MW6(idx5): non-starter => 0/0
# P_BT8 MW4(idx3), MW8(idx7): non-starter => 0/0
# P_BT5 MW5(idx4): limited minutes (30) => reduced shots
ACTUALS: dict[str, dict[str, list[int]]] = {
    "P_BT1": {"shots": [5, 4, 6, 3, 5, 4, 7, 5, 4, 6],
              "sot":   [2, 1, 3, 1, 2, 2, 3, 2, 2, 3]},
    "P_BT2": {"shots": [3, 4, 3, 5, 2, 4, 3, 4, 5, 3],
              "sot":   [1, 2, 1, 2, 1, 2, 1, 2, 2, 1]},
    "P_BT3": {"shots": [6, 5, 7, 4, 6, 8, 5, 6, 7, 5],
              "sot":   [3, 2, 3, 2, 3, 4, 2, 3, 3, 2]},
    "P_BT4": {"shots": [2, 1, 3, 2, 2, 1, 3, 2, 1, 2],
              "sot":   [1, 0, 1, 1, 1, 0, 1, 1, 0, 1]},
    "P_BT5": {"shots": [4, 3, 5, 2, 1, 3, 5, 4, 3, 4],  # MW5 limited mins
              "sot":   [2, 1, 2, 1, 0, 1, 2, 2, 1, 2]},
    "P_BT6": {"shots": [3, 2, 4, 3, 3, 2, 3, 4, 2, 3],
              "sot":   [1, 1, 2, 1, 1, 1, 1, 2, 1, 1]},
    "P_BT7": {"shots": [1, 0, 0, 0, 1, 0, 0, 1, 0, 1],  # MW3,MW6: non-starter (0)
              "sot":   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
    "P_BT8": {"shots": [2, 1, 2, 0, 2, 1, 2, 0, 1, 2],  # MW4,MW8: non-starter (0)
              "sot":   [1, 0, 1, 0, 1, 0, 1, 0, 0, 1]},
}

# Non-starter matchweeks (1-indexed)
NON_STARTERS: dict[str, list[int]] = {
    "P_BT7": [3, 6],
    "P_BT8": [4, 8],
}
# Limited minutes {player_id: {mw: minutes}}
LIMITED_MINUTES: dict[str, dict[int, int]] = {
    "P_BT5": {5: 30},
}
# Tactical role overrides {player_id: {mw: tactical_note}}
ROLE_OVERRIDES: dict[str, dict[int, str]] = {
    "P_BT6": {6: "wide", 7: "wide", 8: "wide", 9: "wide", 10: "wide"},
}

# Match schedule: mw -> [(home, away, poss_home, poss_away, imp_home, imp_away, rest_h, rest_a)]
MATCH_SCHEDULE: dict[int, list[tuple[str, str, int, int, str, str, int, int]]] = {
    1:  [("TeamA","TeamB",58,42,"neutral","neutral",7,7),
         ("TeamC","TeamD",54,46,"neutral","neutral",7,7)],
    2:  [("TeamB","TeamA",53,47,"neutral","neutral",7,7),
         ("TeamD","TeamC",44,56,"neutral","neutral",7,7)],
    3:  [("TeamA","TeamC",60,40,"must_win_top4","neutral",7,4),
         ("TeamB","TeamD",60,40,"neutral","neutral",7,7)],
    4:  [("TeamC","TeamA",46,54,"neutral","must_win_top4",4,7),
         ("TeamD","TeamB",41,59,"neutral","must_win_relegation",4,7)],
    5:  [("TeamA","TeamD",62,38,"must_win_title","neutral",7,7),
         ("TeamC","TeamB",49,51,"neutral","must_win_top4",7,3)],
    6:  [("TeamD","TeamA",40,60,"neutral","must_win_title",7,3),
         ("TeamB","TeamC",57,43,"must_win_top4","neutral",7,7)],
    7:  [("TeamA","TeamB",59,41,"neutral","neutral",7,7),
         ("TeamC","TeamD",53,47,"neutral","neutral",7,7)],
    8:  [("TeamB","TeamA",55,45,"neutral","neutral",7,3),
         ("TeamD","TeamC",42,58,"dead_rubber","neutral",7,7)],
    9:  [("TeamA","TeamC",61,39,"must_win_title","neutral",7,7),
         ("TeamB","TeamD",58,42,"neutral","neutral",4,7)],
    10: [("TeamC","TeamA",47,53,"neutral","must_win_title",7,4),
         ("TeamD","TeamB",43,57,"neutral","neutral",7,7)],
}

TEAM_TO_PLAYERS: dict[str, list[str]] = {
    "TeamA": ["P_BT1", "P_BT2"],
    "TeamB": ["P_BT3", "P_BT4"],
    "TeamC": ["P_BT5", "P_BT6"],
    "TeamD": ["P_BT7", "P_BT8"],
}

# Prop lines per matchweek: list of (player_id, prop_type, line)
# Designed to span all 8 calibration bins
PROP_LINE_TEMPLATES: list[tuple[str, str, float]] = [
    # High probability OVER (S+/S range 0.90-1.00)
    ("P_BT3", "Shots", 2.5),   # Haaland, expected ~5+ shots
    ("P_BT7", "Shots", 1.5),   # Tarkowski, expected ~0.4 shots → high UNDER
    # High probability (S/A range 0.85-0.93)
    ("P_BT1", "Shots", 2.5),   # Kane, expected ~4.5 shots
    ("P_BT3", "SOT",   1.5),   # Haaland SOT, expected ~2.5
    # Medium-high (A/B range 0.75-0.85)
    ("P_BT1", "Shots", 3.5),   # Kane - tighter line
    ("P_BT5", "Shots", 2.5),   # Son, expected ~3.5
    # Medium (B range 0.65-0.75)
    ("P_BT2", "SOT",   1.5),   # Salah SOT, expected ~1.5 - borderline
    ("P_BT4", "Shots", 1.5),   # KDB, expected ~1.9 - lower prob
]


def _make_match_id(mw: int, idx: int) -> str:
    return f"BT_M{mw:02d}_{idx+1}"


def build_historical_players() -> None:
    rows = []
    for pid, p in PLAYER_DEFS.items():
        rows.append({
            "player_id": pid,
            "player_name": p["player_name"],
            "team": p["team"],
            "role": p["role"],
            "season_avg_shots": p["season_avg_shots"],
            "season_avg_sot": p["season_avg_sot"],
            "season_avg_xg": p["season_avg_xg"],
            "l3_avg_shots": p["season_avg_shots"],
            "l3_avg_sot": p["season_avg_sot"],
            "l5_avg_shots": p["season_avg_shots"],
            "l5_avg_sot": p["season_avg_sot"],
            "l10_avg_shots": p["season_avg_shots"],
            "l10_avg_sot": p["season_avg_sot"],
            "home_avg_shots": p["home_avg_shots"],
            "home_avg_sot": p["home_avg_sot"],
            "away_avg_shots": p["away_avg_shots"],
            "away_avg_sot": p["away_avg_sot"],
            "shots_per_touch": p["shots_per_touch"],
            "touches_in_box_pg": p["touches_in_box_pg"],
            "npxg_per_shot": p["npxg_per_shot"],
            "avg_minutes_played": p["avg_minutes_played"],
            "big_chances_pg": p["big_chances_pg"],
            "penalty_kicks_pg": p["penalty_kicks_pg"],
            "set_piece_shots_pg": p["set_piece_shots_pg"],
            "open_play_shots_pg": p["open_play_shots_pg"],
        })
    pd.DataFrame(rows).to_csv(
        os.path.join(BASE_DIR, "historical_players.csv"), index=False
    )


def build_historical_matches() -> None:
    rows = []
    for mw, matches in MATCH_SCHEDULE.items():
        date_base = f"2023-{8 + (mw - 1) // 4:02d}-{5 + ((mw - 1) % 4) * 7:02d}"
        for idx, (home, away, ph, pa, ih, ia, rh, ra) in enumerate(matches):
            mid = _make_match_id(mw, idx)
            ht = TEAM_STATS[home]
            at = TEAM_STATS[away]
            rows.append({
                "match_id": mid, "date": date_base, "matchweek": mw,
                "home_team": home, "away_team": away,
                "home_possession_pct": ph, "away_possession_pct": pa,
                "home_team_xg_for_season": ht["xg_overperformance"] + 1.5,
                "away_team_xg_for_season": at["xg_overperformance"] + 1.2,
                "home_team_shots_pg": ht["home_shots_pg"],
                "away_team_shots_pg": at["away_shots_pg"],
                "home_team_shots_conceded_pg": ht["home_shots_conceded_pg"],
                "away_team_shots_conceded_pg": at["away_shots_conceded_pg"],
                "home_team_sot_conceded_pg": ht["home_sot_conceded_pg"],
                "away_team_sot_conceded_pg": at["away_sot_conceded_pg"],
                "home_team_deep_completions_pg": 9.0,
                "away_team_deep_completions_pg": 7.0,
                "match_importance_home": ih,
                "match_importance_away": ia,
                "home_goals_needed_aggregate": 0,
                "away_goals_needed_aggregate": 0,
                "game_state_context": "open",
                "weather_condition": "clear",
                "pitch_quality": "good",
                "referee_id": f"REF{(mw % 4) + 1:02d}",
                "avg_fouls_this_ref": 21.0 + (mw % 5),
                "home_rest_days": rh,
                "away_rest_days": ra,
            })
    pd.DataFrame(rows).to_csv(
        os.path.join(BASE_DIR, "historical_matches.csv"), index=False
    )


def build_historical_lineups() -> None:
    rows = []
    for mw, matches in MATCH_SCHEDULE.items():
        for idx, (home, away, *_) in enumerate(matches):
            mid = _make_match_id(mw, idx)
            for team in (home, away):
                for pid in TEAM_TO_PLAYERS[team]:
                    is_starter = mw not in NON_STARTERS.get(pid, [])
                    lim = LIMITED_MINUTES.get(pid, {}).get(mw, 90)
                    tactical = ROLE_OVERRIDES.get(pid, {}).get(mw)
                    rows.append({
                        "match_id": mid, "matchweek": mw,
                        "player_id": pid,
                        "player_name": PLAYER_DEFS[pid]["player_name"],
                        "team": team,
                        "is_confirmed_starter": is_starter,
                        "expected_minutes": lim if is_starter else 0,
                        "tactical_role_override": tactical if tactical else "",
                        "playing_position_today": PLAYER_DEFS[pid]["role"],
                    })
    pd.DataFrame(rows).to_csv(
        os.path.join(BASE_DIR, "historical_lineups.csv"), index=False
    )


def build_historical_actuals() -> None:
    rows = []
    for mw, matches in MATCH_SCHEDULE.items():
        mw_idx = mw - 1
        for idx, (home, away, *_) in enumerate(matches):
            mid = _make_match_id(mw, idx)
            for team in (home, away):
                for pid in TEAM_TO_PLAYERS[team]:
                    is_ns = mw in NON_STARTERS.get(pid, [])
                    did_start = not is_ns
                    shots = ACTUALS[pid]["shots"][mw_idx]
                    sot = ACTUALS[pid]["sot"][mw_idx]
                    mins = 0 if is_ns else LIMITED_MINUTES.get(pid, {}).get(mw, 90)
                    rows.append({
                        "match_id": mid, "matchweek": mw,
                        "player_id": pid,
                        "player_name": PLAYER_DEFS[pid]["player_name"],
                        "team": team,
                        "actual_shots": shots,
                        "actual_sot": sot,
                        "minutes_played": mins,
                        "did_start": did_start,
                    })
    pd.DataFrame(rows).to_csv(
        os.path.join(BASE_DIR, "historical_actuals.csv"), index=False
    )


def build_historical_prop_lines() -> None:
    lines: list[dict[str, Any]] = []
    for mw, matches in MATCH_SCHEDULE.items():
        for pid, prop_type, line in PROP_LINE_TEMPLATES:
            team = PLAYER_DEFS[pid]["team"]
            # Find match_id for this player's team in this matchweek
            mid = None
            for idx, (home, away, *_) in enumerate(matches):
                if team in (home, away):
                    mid = _make_match_id(mw, idx)
                    break
            if mid is None:
                continue
            lines.append({
                "matchweek": mw,
                "match_id": mid,
                "player_id": pid,
                "prop_type": prop_type,
                "line": line,
            })
    with open(os.path.join(BASE_DIR, "historical_prop_lines.json"), "w") as fh:
        json.dump(lines, fh, indent=2)


def build_historical_team_stats() -> None:
    rows = []
    for team, stats in TEAM_STATS.items():
        rows.append({"team": team, **stats})
    pd.DataFrame(rows).to_csv(
        os.path.join(BASE_DIR, "historical_team_stats.csv"), index=False
    )


if __name__ == "__main__":
    build_historical_players()
    build_historical_matches()
    build_historical_lineups()
    build_historical_actuals()
    build_historical_prop_lines()
    build_historical_team_stats()
    print(f"Synthetic data written to {BASE_DIR}")

from __future__ import annotations

import json
import os
from typing import Any

import pandas as pd

from config import ROLE_CONFIG, URGENCY_MULT


def _load_players(path: str) -> dict[str, dict[str, Any]]:
    df = pd.read_csv(path)
    players: dict[str, dict[str, Any]] = {}
    for _, row in df.iterrows():
        pid = str(row["player_id"])
        d = row.to_dict()
        _validate_player(d)
        players[pid] = d
    return players


def _validate_player(d: dict[str, Any]) -> None:
    shots = float(d["season_avg_shots"])
    sot = float(d["season_avg_sot"])
    role = str(d["role"])
    if not (0 < shots < 15):
        raise ValueError(f"player {d['player_id']}: season_avg_shots={shots} out of range (0, 15)")
    if not (0 <= sot <= shots):
        raise ValueError(f"player {d['player_id']}: season_avg_sot={sot} must be in [0, {shots}]")
    if role not in ROLE_CONFIG:
        raise ValueError(f"player {d['player_id']}: unknown role '{role}'")


def _load_matches(path: str) -> dict[str, dict[str, Any]]:
    df = pd.read_csv(path)
    matches: dict[str, dict[str, Any]] = {}
    for _, row in df.iterrows():
        mid = str(row["match_id"])
        d = row.to_dict()
        _validate_match(d)
        matches[mid] = d
    return matches


def _validate_match(d: dict[str, Any]) -> None:
    for side in ("home", "away"):
        poss = float(d[f"{side}_possession_pct"])
        if not (20 <= poss <= 80):
            raise ValueError(
                f"match {d['match_id']}: {side}_possession_pct={poss} out of range [20, 80]"
            )
    urgency_home = str(d.get("match_importance_home", "neutral"))
    urgency_away = str(d.get("match_importance_away", "neutral"))
    for urgency in (urgency_home, urgency_away):
        if urgency not in URGENCY_MULT:
            raise ValueError(
                f"match {d['match_id']}: urgency context '{urgency}' not in URGENCY_MULT"
            )


def _load_lineups(path: str) -> list[dict[str, Any]]:
    df = pd.read_csv(path)
    lineups: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        d = row.to_dict()
        exp_min = float(d.get("expected_minutes", 90))
        if exp_min > 90:
            raise ValueError(
                f"lineup player {d.get('player_id')}: expected_minutes={exp_min} > 90"
            )
        lineups.append(d)
    return lineups


def _load_team_stats(path: str) -> dict[str, dict[str, Any]]:
    df = pd.read_csv(path)
    teams: dict[str, dict[str, Any]] = {}
    for _, row in df.iterrows():
        team = str(row["team"])
        d = row.to_dict()
        teams[team] = d
    return teams


def _load_prop_lines(path: str) -> list[dict[str, Any]]:
    with open(path, "r") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("prop_lines.json must be a JSON array")
    return data


def load_all(
    players_csv: str,
    matches_csv: str,
    lineups_csv: str,
    team_stats_csv: str,
    prop_lines_json: str,
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    list[dict[str, Any]],
    dict[str, dict[str, Any]],
    list[dict[str, Any]],
]:
    players = _load_players(players_csv)
    matches = _load_matches(matches_csv)
    lineups = _load_lineups(lineups_csv)
    team_stats = _load_team_stats(team_stats_csv)
    prop_lines = _load_prop_lines(prop_lines_json)
    return players, matches, lineups, team_stats, prop_lines


def load_referees(data_dir: str = "data") -> dict[str, Any]:
    path = os.path.join(data_dir, "referees.json")
    if os.path.exists(path):
        with open(path, "r") as fh:
            return json.load(fh)
    return {}

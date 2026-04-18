"""Generate all data/ files for Chelsea vs Man Utd (MW34)."""
from __future__ import annotations
import json, os
import pandas as pd

DATA = "data"
MATCH_ID = "che_mun_mw34"

# ── Role-level stat templates ─────────────────────────────────────────────────
# (season_shots, season_sot, shots_per_touch, touches_box, npxg_shot, big_chances, set_pcs)
ROLE_T: dict[str, tuple] = {
    "CF":           (3.10, 1.22, 0.38, 4.8, 0.155, 0.78, 0.42),
    "SS":           (2.60, 1.02, 0.32, 4.1, 0.135, 0.62, 0.34),
    "AM":           (2.45, 0.97, 0.28, 3.6, 0.125, 0.55, 0.38),
    "WF_inside":    (2.25, 0.88, 0.30, 3.8, 0.120, 0.50, 0.30),
    "WF_wide":      (1.60, 0.60, 0.22, 2.8, 0.100, 0.32, 0.24),
    "CM_box":       (1.10, 0.38, 0.16, 2.2, 0.090, 0.24, 0.36),
    "CM_deep":      (0.55, 0.16, 0.10, 1.2, 0.075, 0.10, 0.22),
    "DM":           (0.50, 0.14, 0.09, 1.0, 0.070, 0.08, 0.20),
    "FB_attacking": (0.88, 0.25, 0.12, 1.6, 0.080, 0.16, 0.28),
    "FB_defensive": (0.36, 0.10, 0.07, 0.8, 0.065, 0.06, 0.18),
    "CB_defensive": (0.34, 0.10, 0.06, 0.7, 0.060, 0.05, 0.16),
    "CB_aerial":    (0.52, 0.19, 0.08, 1.0, 0.075, 0.08, 0.26),
}

def _p(pid, name, team, role, s, sot, l3m=1.10, l5m=1.03, l10m=0.97,
       hm=1.14, am=0.87, pens=0.01):
    """Build a full player row dict."""
    t = ROLE_T[role]
    base_s = round(s, 2)
    base_sot = round(sot, 3)
    set_pcs = round(t[6] * (s / t[0]), 2)
    return {
        "player_id": pid, "player_name": name, "team": team, "role": role,
        "season_avg_shots": base_s, "season_avg_sot": base_sot,
        "season_avg_xg": round(s * t[4], 3),
        "l3_avg_shots": round(s * l3m, 2), "l3_avg_sot": round(sot * l3m, 3),
        "l5_avg_shots": round(s * l5m, 2), "l5_avg_sot": round(sot * l5m, 3),
        "l10_avg_shots": round(s * l10m, 2), "l10_avg_sot": round(sot * l10m, 3),
        "home_avg_shots": round(s * hm, 2), "home_avg_sot": round(sot * hm, 3),
        "away_avg_shots": round(s * am, 2), "away_avg_sot": round(sot * am, 3),
        "shots_per_touch": round(t[1], 3),
        "touches_in_box_pg": round(t[2] * (s / t[0]), 2),
        "npxg_per_shot": t[4],
        "avg_minutes_played": 86,
        "big_chances_pg": round(t[5] * (s / t[0]), 3),
        "penalty_kicks_pg": pens,
        "set_piece_shots_pg": set_pcs,
        "open_play_shots_pg": round(max(0.01, s - set_pcs), 2),
    }

# ── Chelsea (home) ────────────────────────────────────────────────────────────
CHE = [
    _p("joao_pedro",        "Joao Pedro",          "Chelsea", "CF",           2.85, 1.12, 1.12, 1.04, 0.97, pens=0.03),
    _p("cole_palmer",       "Cole Palmer",          "Chelsea", "AM",           2.80, 1.10, 1.18, 1.06, 0.98, pens=0.04),
    _p("pedro_neto",        "Pedro Neto",           "Chelsea", "WF_inside",    2.25, 0.88, 1.14, 1.05, 0.97),
    _p("estevao",           "Estevao",              "Chelsea", "WF_inside",    1.98, 0.78, 1.10, 1.03, 0.96),
    _p("liam_delap",        "Liam Delap",           "Chelsea", "CF",           3.15, 1.24, 1.15, 1.06, 0.97, pens=0.02),
    _p("marc_guiu",         "Marc Guiu",            "Chelsea", "CF",           2.65, 1.04, 1.08, 1.02, 0.97),
    _p("alejandro_garnacho","Alejandro Garnacho",   "Chelsea", "WF_wide",      1.68, 0.62, 1.12, 1.04, 0.97),
    _p("enzo_fernandez",    "Enzo Fernandez",       "Chelsea", "CM_box",       1.22, 0.42, 1.10, 1.03, 0.97),
    _p("andrey_santos",     "Andrey Santos",        "Chelsea", "CM_deep",      0.58, 0.18, 1.06, 1.02, 0.97),
    _p("dario_essugo",      "Dario Essugo",         "Chelsea", "CM_deep",      0.50, 0.14, 1.04, 1.01, 0.98),
    _p("moises_caicedo",    "Moises Caicedo",       "Chelsea", "DM",           0.62, 0.20, 1.06, 1.02, 0.97),
    _p("romeo_lavia",       "Romeo Lavia",          "Chelsea", "CM_deep",      0.52, 0.16, 1.04, 1.01, 0.98),
    _p("reece_james",       "Reece James",          "Chelsea", "FB_attacking", 0.95, 0.28, 1.12, 1.04, 0.97),
    _p("malo_gusto",        "Malo Gusto",           "Chelsea", "FB_attacking", 0.82, 0.22, 1.10, 1.03, 0.97),
    _p("marc_cucurella",    "Marc Cucurella",       "Chelsea", "FB_defensive", 0.42, 0.12, 1.08, 1.02, 0.97),
    _p("jorrel_hato",       "Jorrel Hato",          "Chelsea", "FB_defensive", 0.32, 0.10, 1.06, 1.01, 0.98),
    _p("wesley_fofana",     "Wesley Fofana",        "Chelsea", "CB_defensive", 0.35, 0.10, 1.06, 1.01, 0.97),
    _p("tosin_adarabioyo",  "Tosin Adarabioyo",     "Chelsea", "CB_defensive", 0.38, 0.12, 1.06, 1.01, 0.97),
    _p("josh_acheampong",   "Josh Acheampong",      "Chelsea", "FB_attacking", 0.72, 0.20, 1.08, 1.02, 0.97),
    _p("mamadou_sarr",      "Mamadou Sarr",         "Chelsea", "CB_defensive", 0.30, 0.09, 1.04, 1.01, 0.98),
    _p("benoit_badiashile", "Benoit Badiashile",    "Chelsea", "CB_defensive", 0.38, 0.10, 1.06, 1.01, 0.97),
    _p("trevoh_chalobah",   "Trevoh Chalobah",      "Chelsea", "CB_defensive", 0.32, 0.09, 1.04, 1.01, 0.98),
]

# ── Man Utd (away) ────────────────────────────────────────────────────────────
MAN = [
    _p("bryan_mbeumo",      "Bryan Mbeumo",         "Man Utd", "WF_inside",    2.45, 0.94, 1.14, 1.05, 0.97),
    _p("matheus_cunha",     "Matheus Cunha",        "Man Utd", "SS",           2.62, 1.02, 1.12, 1.04, 0.97),
    _p("benjamin_sesko",    "Benjamin Sesko",       "Man Utd", "CF",           3.05, 1.20, 1.10, 1.03, 0.97, pens=0.02),
    _p("bruno_fernandes",   "Bruno Fernandes",      "Man Utd", "AM",           2.52, 0.98, 1.08, 1.02, 0.97, pens=0.03),
    _p("kobbie_mainoo",     "Kobbie Mainoo",        "Man Utd", "CM_box",       1.05, 0.36, 1.08, 1.02, 0.97),
    _p("harry_maguire",     "Harry Maguire",        "Man Utd", "CB_aerial",    0.52, 0.19, 1.06, 1.01, 0.97),
    _p("amad_diallo",       "Amad Diallo",          "Man Utd", "WF_inside",    2.25, 0.86, 1.15, 1.05, 0.97),
    _p("casemiro",          "Casemiro",             "Man Utd", "DM",           0.48, 0.14, 1.04, 1.01, 0.98),
    _p("joshua_zirkzee",    "Joshua Zirkzee",       "Man Utd", "SS",           2.38, 0.96, 1.10, 1.03, 0.97),
    _p("mason_mount",       "Mason Mount",          "Man Utd", "AM",           1.82, 0.72, 0.92, 0.96, 0.98),  # poor form
    _p("shea_lacey",        "Shea Lacey",           "Man Utd", "WF_wide",      1.52, 0.56, 1.08, 1.02, 0.97),
    _p("diogo_dalot",       "Diogo Dalot",          "Man Utd", "FB_attacking", 0.88, 0.28, 1.08, 1.02, 0.97),
    _p("manuel_ugarte",     "Manuel Ugarte",        "Man Utd", "DM",           0.42, 0.12, 1.04, 1.01, 0.98),
    _p("tyrell_malacia",    "Tyrell Malacia",       "Man Utd", "FB_defensive", 0.32, 0.10, 1.04, 1.01, 0.98),
    _p("luke_shaw",         "Luke Shaw",            "Man Utd", "FB_attacking", 0.78, 0.22, 1.06, 1.02, 0.97),
    _p("ayden_heaven",      "Ayden Heaven",         "Man Utd", "CB_defensive", 0.28, 0.08, 1.04, 1.01, 0.98),
    _p("tyler_fredricson",  "Tyler Fredricson",     "Man Utd", "CB_defensive", 0.22, 0.08, 1.04, 1.01, 0.98),
    _p("noussair_mazraoui", "Noussair Mazraoui",    "Man Utd", "FB_attacking", 0.82, 0.24, 1.08, 1.02, 0.97),
    _p("leny_yoro",         "Leny Yoro",            "Man Utd", "CB_defensive", 0.32, 0.10, 1.06, 1.01, 0.97),
]

PLAYERS = CHE + MAN

# ── Prop lines (all 79 as specified) ─────────────────────────────────────────
PROP_LINES = [
    {"player_id": "joao_pedro",         "prop_type": "Shots", "line": 2.5},
    {"player_id": "cole_palmer",        "prop_type": "Shots", "line": 1.5},
    {"player_id": "bryan_mbeumo",       "prop_type": "Shots", "line": 2.0},
    {"player_id": "matheus_cunha",      "prop_type": "Shots", "line": 2.0},
    {"player_id": "benjamin_sesko",     "prop_type": "Shots", "line": 2.0},
    {"player_id": "bruno_fernandes",    "prop_type": "Shots", "line": 2.0},
    {"player_id": "pedro_neto",         "prop_type": "Shots", "line": 1.5},
    {"player_id": "kobbie_mainoo",      "prop_type": "Shots", "line": 0.5},
    {"player_id": "harry_maguire",      "prop_type": "Shots", "line": 0.5},
    {"player_id": "estevao",            "prop_type": "Shots", "line": 1.5},
    {"player_id": "liam_delap",         "prop_type": "Shots", "line": 1.5},
    {"player_id": "marc_guiu",          "prop_type": "Shots", "line": 1.5},
    {"player_id": "alejandro_garnacho", "prop_type": "Shots", "line": 1.5},
    {"player_id": "amad_diallo",        "prop_type": "Shots", "line": 0.5},
    {"player_id": "casemiro",           "prop_type": "Shots", "line": 0.5},
    {"player_id": "enzo_fernandez",     "prop_type": "Shots", "line": 1.5},
    {"player_id": "joshua_zirkzee",     "prop_type": "Shots", "line": 1.5},
    {"player_id": "mason_mount",        "prop_type": "Shots", "line": 0.5},
    {"player_id": "andrey_santos",      "prop_type": "Shots", "line": 0.5},
    {"player_id": "dario_essugo",       "prop_type": "Shots", "line": 0.5},
    {"player_id": "shea_lacey",         "prop_type": "Shots", "line": 1.5},
    {"player_id": "jorrel_hato",        "prop_type": "Shots", "line": 1.5},
    {"player_id": "diogo_dalot",        "prop_type": "Shots", "line": 1.5},
    {"player_id": "malo_gusto",         "prop_type": "Shots", "line": 1.5},
    {"player_id": "manuel_ugarte",      "prop_type": "Shots", "line": 1.5},
    {"player_id": "marc_cucurella",     "prop_type": "Shots", "line": 1.5},
    {"player_id": "moises_caicedo",     "prop_type": "Shots", "line": 0.5},
    {"player_id": "romeo_lavia",        "prop_type": "Shots", "line": 1.5},
    {"player_id": "wesley_fofana",      "prop_type": "Shots", "line": 0.5},
    {"player_id": "tosin_adarabioyo",   "prop_type": "Shots", "line": 0.5},
    {"player_id": "josh_acheampong",    "prop_type": "Shots", "line": 0.5},
    {"player_id": "mamadou_sarr",       "prop_type": "Shots", "line": 0.5},
    {"player_id": "reece_james",        "prop_type": "Shots", "line": 1.5},
    {"player_id": "tyrell_malacia",     "prop_type": "Shots", "line": 1.5},
    {"player_id": "luke_shaw",          "prop_type": "Shots", "line": 1.5},
    {"player_id": "ayden_heaven",       "prop_type": "Shots", "line": 1.5},
    {"player_id": "tyler_fredricson",   "prop_type": "Shots", "line": 0.5},
    {"player_id": "noussair_mazraoui",  "prop_type": "Shots", "line": 0.5},
    {"player_id": "leny_yoro",          "prop_type": "Shots", "line": 0.5},
    {"player_id": "benoit_badiashile",  "prop_type": "Shots", "line": 0.5},
    {"player_id": "pedro_neto",         "prop_type": "SOT",   "line": 0.5},
    {"player_id": "bryan_mbeumo",       "prop_type": "SOT",   "line": 0.5},
    {"player_id": "joao_pedro",         "prop_type": "SOT",   "line": 0.5},
    {"player_id": "bruno_fernandes",    "prop_type": "SOT",   "line": 1.5},
    {"player_id": "cole_palmer",        "prop_type": "SOT",   "line": 0.5},
    {"player_id": "benjamin_sesko",     "prop_type": "SOT",   "line": 0.5},
    {"player_id": "joshua_zirkzee",     "prop_type": "SOT",   "line": 0.5},
    {"player_id": "liam_delap",         "prop_type": "SOT",   "line": 0.5},
    {"player_id": "matheus_cunha",      "prop_type": "SOT",   "line": 0.5},
    {"player_id": "amad_diallo",        "prop_type": "SOT",   "line": 1.5},
    {"player_id": "enzo_fernandez",     "prop_type": "SOT",   "line": 1.5},
    {"player_id": "alejandro_garnacho", "prop_type": "SOT",   "line": 1.5},
    {"player_id": "casemiro",           "prop_type": "SOT",   "line": 1.5},
    {"player_id": "estevao",            "prop_type": "SOT",   "line": 0.5},
    {"player_id": "marc_guiu",          "prop_type": "SOT",   "line": 0.5},
    {"player_id": "mason_mount",        "prop_type": "SOT",   "line": 1.5},
    {"player_id": "andrey_santos",      "prop_type": "SOT",   "line": 0.5},
    {"player_id": "shea_lacey",         "prop_type": "SOT",   "line": 1.5},
    {"player_id": "tosin_adarabioyo",   "prop_type": "SOT",   "line": 0.5},
    {"player_id": "ayden_heaven",       "prop_type": "SOT",   "line": 0.5},
    {"player_id": "jorrel_hato",        "prop_type": "SOT",   "line": 0.5},
    {"player_id": "josh_acheampong",    "prop_type": "SOT",   "line": 0.5},
    {"player_id": "diogo_dalot",        "prop_type": "SOT",   "line": 0.5},
    {"player_id": "kobbie_mainoo",      "prop_type": "SOT",   "line": 0.5},
    {"player_id": "leny_yoro",          "prop_type": "SOT",   "line": 0.5},
    {"player_id": "luke_shaw",          "prop_type": "SOT",   "line": 0.5},
    {"player_id": "malo_gusto",         "prop_type": "SOT",   "line": 0.5},
    {"player_id": "marc_cucurella",     "prop_type": "SOT",   "line": 0.5},
    {"player_id": "moises_caicedo",     "prop_type": "SOT",   "line": 0.5},
    {"player_id": "noussair_mazraoui",  "prop_type": "SOT",   "line": 0.5},
    {"player_id": "reece_james",        "prop_type": "SOT",   "line": 0.5},
    {"player_id": "romeo_lavia",        "prop_type": "SOT",   "line": 0.5},
    {"player_id": "trevoh_chalobah",    "prop_type": "SOT",   "line": 0.5},
    {"player_id": "wesley_fofana",      "prop_type": "SOT",   "line": 0.5},
    {"player_id": "manuel_ugarte",      "prop_type": "SOT",   "line": 0.5},
    {"player_id": "benoit_badiashile",  "prop_type": "SOT",   "line": 0.5},
    {"player_id": "dario_essugo",       "prop_type": "SOT",   "line": 0.5},
    {"player_id": "mamadou_sarr",       "prop_type": "SOT",   "line": 0.5},
    {"player_id": "tyler_fredricson",   "prop_type": "SOT",   "line": 0.5},
    {"player_id": "tyrell_malacia",     "prop_type": "SOT",   "line": 0.5},
]

# ── Matches ───────────────────────────────────────────────────────────────────
MATCHES = [{
    "match_id": MATCH_ID, "date": "2025-04-19",
    "home_team": "Chelsea", "away_team": "Man Utd",
    "home_possession_pct": 57, "away_possession_pct": 43,
    "home_team_xg_for_season": 68.4, "away_team_xg_for_season": 42.1,
    "home_team_shots_pg": 15.2, "away_team_shots_pg": 11.8,
    "home_team_shots_conceded_pg": 9.8, "away_team_shots_conceded_pg": 13.1,
    "home_team_sot_conceded_pg": 3.4, "away_team_sot_conceded_pg": 4.6,
    "home_team_deep_completions_pg": 12.1, "away_team_deep_completions_pg": 8.3,
    "match_importance_home": "must_win_top4",
    "match_importance_away": "must_win_europe",
    "home_goals_needed_aggregate": 0, "away_goals_needed_aggregate": 0,
    "game_state_context": "neutral",
    "weather_condition": "clear", "pitch_quality": "good",
    "referee_id": "ref_default", "avg_fouls_this_ref": 22.0,
    "home_rest_days": 6, "away_rest_days": 6,
}]

# ── Team stats ────────────────────────────────────────────────────────────────
TEAM_STATS = [
    {
        "team": "Chelsea", "season": "2024-25",
        "home_shots_pg": 15.2, "away_shots_pg": 13.1,
        "home_sot_pg": 5.4,    "away_sot_pg": 4.7,
        "home_shots_conceded_pg": 9.8,  "away_shots_conceded_pg": 11.2,
        "home_sot_conceded_pg": 3.4,    "away_sot_conceded_pg": 4.1,
        "avg_possession_home": 58, "avg_possession_away": 54,
        "press_intensity_ppda": 8.2,
        "transition_attacks_pg": 4.1,
        "set_piece_goals_pct": 0.28,
        "xg_overperformance": 0.14,
    },
    {
        "team": "Man Utd", "season": "2024-25",
        "home_shots_pg": 12.4, "away_shots_pg": 11.8,
        "home_sot_pg": 4.2,    "away_sot_pg": 3.9,
        "home_shots_conceded_pg": 12.1, "away_shots_conceded_pg": 13.1,
        "home_sot_conceded_pg": 4.3,    "away_sot_conceded_pg": 4.6,
        "avg_possession_home": 51, "avg_possession_away": 43,
        "press_intensity_ppda": 11.4,
        "transition_attacks_pg": 3.2,
        "set_piece_goals_pct": 0.31,
        "xg_overperformance": -0.22,
    },
]

# ── Lineups ───────────────────────────────────────────────────────────────────
ROLE_MAP = {p["player_id"]: p["role"] for p in PLAYERS}
TEAM_MAP = {p["player_id"]: p["team"] for p in PLAYERS}
NAME_MAP = {p["player_id"]: p["player_name"] for p in PLAYERS}

# trevoh_chalobah is SOT-only; still needs a lineup row
LINEUP_PIDS = sorted({pl["player_id"] for pl in PROP_LINES})

LINEUPS = [
    {
        "match_id": MATCH_ID,
        "player_id": pid,
        "player_name": NAME_MAP[pid],
        "team": TEAM_MAP[pid],
        "is_confirmed_starter": True,
        "expected_minutes": 90,
        "tactical_role_override": "",
        "playing_position_today": ROLE_MAP[pid],
    }
    for pid in LINEUP_PIDS
]

# ── Write ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(DATA, exist_ok=True)

    pd.DataFrame(PLAYERS).to_csv(f"{DATA}/players.csv", index=False)
    print(f"players.csv       — {len(PLAYERS)} rows")

    pd.DataFrame(MATCHES).to_csv(f"{DATA}/matches.csv", index=False)
    print(f"matches.csv       — {len(MATCHES)} rows")

    pd.DataFrame(TEAM_STATS).to_csv(f"{DATA}/team_stats.csv", index=False)
    print(f"team_stats.csv    — {len(TEAM_STATS)} rows")

    pd.DataFrame(LINEUPS).to_csv(f"{DATA}/lineups.csv", index=False)
    print(f"lineups.csv       — {len(LINEUPS)} rows")

    with open(f"{DATA}/prop_lines.json", "w") as fh:
        json.dump(PROP_LINES, fh, indent=2)
    print(f"prop_lines.json   — {len(PROP_LINES)} entries, "
          f"{len({p['player_id'] for p in PROP_LINES})} unique players")

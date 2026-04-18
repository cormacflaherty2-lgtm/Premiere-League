from __future__ import annotations

# Blend weights
FORM_WEIGHT: float = 0.55
MODEL_WEIGHT: float = 0.45
VENUE_BLEND: float = 0.30

# Form recency weights
L3_WEIGHT: float = 0.50
L5_WEIGHT: float = 0.30
L10_WEIGHT: float = 0.20

# Negative-binomial variance inflation
NB_VARIANCE_FACTOR: float = 1.40

# Bet-quality thresholds
MIN_HIT_PROB: float = 0.65
MIN_EDGE_PCT: float = 10.0

# Parlay correlation rules
MAX_LEGS_SAME_GAME: int = 2
MAX_LEGS_SAME_TEAM: int = 2
SAME_GAME_CORR_PENALTY: float = 0.95
SAME_TEAM_CORR_PENALTY: float = 0.97

# Lineup thresholds
STARTER_MIN_THRESHOLD: int = 45
NON_STARTER_SHOTS: float = 0.0

# League averages
PL_LEAGUE_AVG_SHOTS_CONCEDED: float = 12.2
PL_LEAGUE_AVG_SOT_CONCEDED: float = 4.1

# role -> (shot_share, sot_rate, touches_in_box_mult)
ROLE_CONFIG: dict[str, tuple[float, float, float]] = {
    "CF":           (0.220, 0.44, 1.30),
    "SS":           (0.165, 0.41, 1.15),
    "WF_inside":    (0.190, 0.42, 1.20),
    "WF_wide":      (0.140, 0.35, 0.90),
    "AM":           (0.125, 0.37, 1.05),
    "CM_box":       (0.085, 0.30, 0.85),
    "CM_deep":      (0.050, 0.24, 0.60),
    "DM":           (0.035, 0.22, 0.50),
    "FB_attacking": (0.045, 0.20, 0.70),
    "FB_defensive": (0.025, 0.16, 0.40),
    "CB_aerial":    (0.030, 0.18, 0.55),
    "CB_defensive": (0.015, 0.12, 0.30),
    "GK":           (0.000, 0.00, 0.00),
}

# keyword (lowercase) -> role
ROLE_OVERRIDE_MAP: dict[str, str] = {
    "false 9":          "SS",
    "no.10":            "AM",
    "number 10":        "AM",
    "inverted winger":  "WF_inside",
    "inside forward":   "WF_inside",
    "wide":             "WF_wide",
    "traditional winger": "WF_wide",
    "right back":       "FB_defensive",
    "left back":        "FB_defensive",
    "rb":               "FB_defensive",
    "lb":               "FB_defensive",
    "wingback":         "FB_attacking",
    "wing back":        "FB_attacking",
    "iwb":              "FB_attacking",
    "inverted fullback": "FB_attacking",
    "defensive mid":    "DM",
    "holding":          "DM",
    "pivot":            "CM_deep",
    "box to box":       "CM_box",
    "b2b":              "CM_box",
    "center back":      "CB_aerial",
    "cb":               "CB_defensive",
}

URGENCY_MULT: dict[str, float] = {
    "neutral":               1.00,
    "must_win_title":        1.12,
    "must_win_top4":         1.10,
    "must_win_europe":       1.07,
    "must_win_relegation":   1.08,
    "dead_rubber":           0.82,
    "nothing_to_play_for":   0.88,
    "revenge_derby":         1.05,
    "cup_final":             1.06,
}

AGGREGATE_MULT: dict[str, float] = {
    "must_score_3_plus":     1.22,
    "must_score_2":          1.12,
    "must_score_1":          1.05,
    "protect_2_goal_lead":   0.85,
    "protect_1_goal_lead":   0.92,
    "neutral":               1.00,
}

# legs -> payout multiplier
PRIZEPICKS_PAYOUTS: dict[int, float] = {
    2: 3.0,
    3: 5.0,
    4: 10.0,
    5: 20.0,
    6: 40.0,
}

# hit_prob thresholds -> tier label
TIER_THRESHOLDS: list[tuple[float, str]] = [
    (0.92, "S+"),
    (0.85, "S"),
    (0.75, "A"),
    (0.65, "B"),
    (0.55, "C"),
    (0.00, "D"),
]

# rich style per tier
TIER_STYLE: dict[str, str] = {
    "S+": "bold bright_green",
    "S":  "bold green",
    "A":  "green",
    "B":  "yellow",
    "C":  "yellow",
    "D":  "red",
}

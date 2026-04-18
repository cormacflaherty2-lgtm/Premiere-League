from __future__ import annotations

from typing import Any

import pandas as pd
from rich import box
from rich.console import Console
from rich.table import Table

from config import TIER_STYLE

console = Console()


def print_rich_table(
    results: list[dict[str, Any]],
    parlays: dict[int, dict[str, Any]],
) -> None:
    table = Table(
        title="Premier League Shots & SOT Props",
        box=box.ROUNDED,
        show_lines=False,
    )

    columns = [
        ("TIER", "center"),
        ("PLAYER", "left"),
        ("TEAM", "left"),
        ("PROP", "center"),
        ("DIR", "center"),
        ("EXP", "right"),
        ("LINE", "right"),
        ("EDGE%", "right"),
        ("HIT%", "right"),
        ("EV 3-LEG", "right"),
    ]
    for col_name, justify in columns:
        table.add_column(col_name, justify=justify)

    for r in results:
        if r["tier"] == "D":
            continue
        style = TIER_STYLE.get(r["tier"], "")
        table.add_row(
            r["tier"],
            str(r["player_name"]),
            str(r["team"]),
            str(r["prop_type"]),
            str(r["direction"]),
            f"{r['exp_value']:.2f}",
            f"{r['prop_line']:.1f}",
            f"{r['edge_pct']:+.1f}",
            f"{r['hit_prob']*100:.1f}%",
            f"{r['ev_3leg']:+.3f}×",
            style=style,
        )

    console.print(table)

    if not parlays:
        return

    console.print("\n[bold]OPTIMAL PARLAYS[/bold]")
    for size, data in sorted(parlays.items()):
        legs = data["legs"]
        payout = data["payout_mult"]
        combined = data["combined_hit_prob"]
        ev = data["ev_multiplier"]

        leg_strs = [
            f"{l['player_name']} {l['prop_type']} {l['direction']}" for l in legs
        ]
        legs_display = " + ".join(leg_strs)
        console.print(
            f"[bold]{size}-LEG ({payout}×):[/bold] {legs_display} "
            f"→ Hit: {combined*100:.1f}% | EV: {ev:+.2f}×"
        )


def export_csv(results: list[dict[str, Any]], path: str) -> None:
    df = pd.DataFrame(results)
    df.to_csv(path, index=False)


def export_parlays(
    parlays: dict[int, dict[str, Any]], path: str
) -> None:
    rows: list[dict[str, Any]] = []
    for size, data in sorted(parlays.items()):
        for i, leg in enumerate(data["legs"], 1):
            rows.append(
                {
                    "parlay_size": size,
                    "leg": i,
                    "player_name": leg["player_name"],
                    "team": leg["team"],
                    "prop_type": leg["prop_type"],
                    "direction": leg["direction"],
                    "prop_line": leg["prop_line"],
                    "hit_prob": leg["hit_prob"],
                    "combined_hit_prob": data["combined_hit_prob"],
                    "payout_mult": data["payout_mult"],
                    "ev_multiplier": data["ev_multiplier"],
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)

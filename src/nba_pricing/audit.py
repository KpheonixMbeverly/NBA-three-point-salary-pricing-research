"""Machine-readable audit focused on known coverage/measurement vulnerabilities."""
from __future__ import annotations
from pathlib import Path
import hashlib
import pandas as pd
from .preprocessing import load_player_data, prepare


def audit(input_file: str | Path) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    d = load_player_data(input_file)
    full = d.groupby("Year").agg(raw_rows=("Player", "size"),
                                 unique_players=("Player", "nunique"),
                                 unique_teams=("Team", "nunique"),
                                 nonmissing_3p_pct=("3P%", "count")).reset_index()
    full["share_missing_3p_pct"] = 1 - full["nonmissing_3p_pct"] / full["raw_rows"]
    panel = prepare(input_file)
    filtered = panel.groupby("Year").size().rename("post_capshare_rows").reset_index()
    full = full.merge(filtered, on="Year", how="left")
    duplicate = d[d.duplicated(["Player", "Year"], keep=False)].sort_values(["Player", "Year"])
    digest = hashlib.sha256(Path(input_file).read_bytes()).hexdigest()
    meta = {
        "file_sha256": digest,
        "raw_rows": int(len(d)),
        "player_year_duplicated_rows": int(duplicate.shape[0]),
        "player_year_duplicated_pairs": int(duplicate[["Player", "Year"]].drop_duplicates().shape[0]),
        "note": "Rows in early seasons may be incomplete; raw file provider provenance not verified."
    }
    return full, duplicate, meta

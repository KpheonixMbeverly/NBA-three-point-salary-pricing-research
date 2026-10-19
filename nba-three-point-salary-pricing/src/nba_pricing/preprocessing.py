"""Replicate the historical poster construction (including known limitations).

IMPORTANT: The processing order follows the earlier models for numerical
comparability; it should not be interpreted as the ideal econometric design.
See docs/METHODOLOGY_AND_LIMITATIONS.md before making causal claims.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

from .constants import CAP_BY_SEASON_END, PERIODS

NUMERIC = ["Age", "G", "MP", "3P", "3PA", "3P%", "2P", "2PA", "2P%",
           "FT", "FTA", "FT%", "TRB", "AST", "STL", "BLK"]
REQUIRED = ["Player", "Year", "Salary", "Team", "Pos", "3P", "3P%", "2P", "2P%",
            "FT", "FT%", "TRB", "AST", "STL", "BLK", "Age"]


def position_group(raw_position: str) -> str:
    """Legacy coding: guard-only strings -> G; center-only -> C; else F.

    This assigns multi-position labels such as 'SG-PF' to Forward.
    """
    p = str(raw_position)
    if "G" in p and "F" not in p:
        return "Guard"
    if "C" in p and "F" not in p and "G" not in p:
        return "Center"
    return "Forward"


def period_for_year(y: int) -> str | None:
    if 2000 <= y <= 2010:
        return PERIODS[0]
    if 2011 <= y <= 2015:
        return PERIODS[1]
    if 2016 <= y <= 2020:
        return PERIODS[2]
    if 2021 <= y <= 2025:
        return PERIODS[3]
    return None


def zscore_by_year(d: pd.DataFrame, column: str) -> pd.Series:
    """Within-year z-scores (ddof=0), computed AFTER salary filtering."""
    return d.groupby("Year")[column].transform(
        lambda s: (s - s.mean()) / s.std(ddof=0)
        if pd.notna(s.std(ddof=0)) and s.std(ddof=0) > 0
        else pd.Series(0.0, index=s.index)
    )


def load_player_data(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError(f"Missing input columns: {missing}")
    df = df.copy()
    for c in ["Salary", "Year"] + NUMERIC:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["Salary", "Player", "Year", "Team", "Pos"])
    df = df[df["Salary"] > 0].copy()
    df["Year"] = df["Year"].astype(int)
    return df


def attach_playoff_tiers(d: pd.DataFrame, csv_path: str | Path) -> pd.DataFrame:
    """Validated team-year left join; never substitute missing tiers with zero.

    Required columns: Year (playoff season-ending year), Team, PlayoffTier.
    PlayoffTier 0 is only valid when the source explicitly records no playoffs.
    For poster's *legacy* treatment, the t salary uses current team's t-1 outcome.
    It does not track each player's previous team, and may misattribute movers.
    """
    teams = pd.read_csv(csv_path)
    required = {"Year", "Team", "PlayoffTier"}
    if not required.issubset(teams.columns):
        raise ValueError(f"Playoff table requires {sorted(required)}")
    teams = teams[list(required)].copy()
    teams["Year"] = pd.to_numeric(teams["Year"], errors="raise").astype(int)
    teams["PlayoffTier"] = pd.to_numeric(teams["PlayoffTier"], errors="raise")
    if teams.duplicated(["Year", "Team"]).any():
        raise ValueError("Duplicate (Year, Team) in playoff tiers")
    if teams["PlayoffTier"].isna().any() or not teams["PlayoffTier"].isin([0, 1, 2, 3, 4]).all():
        raise ValueError("PlayoffTier must be an observed integer in 0..4")
    df = d.copy()
    df["LagSeason"] = df["Year"] - 1
    df = df.merge(teams.rename(columns={"Year": "LagSeason", "PlayoffTier": "PlayoffTierLag"}),
                  on=["LagSeason", "Team"], how="left", validate="many_to_one")
    if df["PlayoffTierLag"].isna().any():
        missing = (df[df["PlayoffTierLag"].isna()][["LagSeason", "Team"]]
                   .drop_duplicates().head(12).to_dict("records"))
        raise ValueError(f"Unmatched historical playoff team-years: {missing}. "
                         "Do not turn missing matches into playoff tier 0.")
    return df.drop(columns="LagSeason")


def prepare(path: str | Path, playoff_tiers_path: str | Path | None = None) -> pd.DataFrame:
    """Reconstruct the poster's 1.5%-filtered panel and 3-season *record* rolling means.

    Important: rolling means use up to 3 previous INCLUDED records per player,
    not necessarily 3 consecutive calendar seasons. See methodology note.
    """
    df = load_player_data(path)
    df["Position"] = df["Pos"].map(position_group)
    df["SalaryCap"] = df["Year"].map(CAP_BY_SEASON_END)
    if df["SalaryCap"].isna().any():
        raise ValueError("Missing salary-cap mapping for a year")
    df["CapShare"] = df["Salary"] / df["SalaryCap"]
    df = df[df["CapShare"] >= 0.015].copy()
    if not len(df):
        raise ValueError("No rows pass 1.5% filter")

    # Matches poster legacy code. This is the mean of the retained salary sample,
    # not necessarily the entire league's average salary.
    year_avg = df.groupby("Year")["Salary"].mean().rename("AvgSalary")
    df = df.merge(year_avg, on="Year", how="left")
    df["ln_Norm_Salary"] = np.log(df["Salary"] / df["AvgSalary"])

    # Legacy TeamPressure is a payroll SUM OF OBSERVED, FILTERED ROWS, and
    # therefore not an audited, complete NBA team payroll total.
    tp = df.groupby(["Year", "Team"], as_index=False)["Salary"].sum()
    tp["TeamPressure"] = tp["Salary"] / tp["Year"].map(CAP_BY_SEASON_END)
    df = df.merge(tp[["Year", "Team", "TeamPressure"]],
                  on=["Year", "Team"], how="left", validate="many_to_one")
    df["NearMax25"] = (df["CapShare"] >= 0.25).astype(int)

    if playoff_tiers_path is not None:
        df = attach_playoff_tiers(df, playoff_tiers_path)

    for new, orig in [("Z_3P_made", "3P"), ("Z_3P_pct", "3P%"),
                      ("Z_FT_made", "FT"), ("Z_FT_pct", "FT%"),
                      ("Z_2P_made", "2P"), ("Z_2P_pct", "2P%")]:
        df[new] = zscore_by_year(df, orig)
    df["Skill_3P"] = df["Z_3P_made"] + df["Z_3P_pct"]
    df["Skill_FT"] = df["Z_FT_made"] + df["Z_FT_pct"]

    df = df.sort_values(["Player", "Year"]).copy()
    df["Age_c"] = df["Age"] - df["Age"].mean()
    roll = ["Skill_3P", "Skill_FT", "Z_2P_made", "Z_2P_pct", "TRB", "AST",
            "STL", "BLK", "Age_c", "TeamPressure"]
    if playoff_tiers_path is not None:
        roll.append("PlayoffTierLag")
    for col in roll:
        df[f"{col}_roll3"] = df.groupby("Player")[col].transform(
            lambda s: s.rolling(window=3, min_periods=1).mean()
        )
    df["Age_c_sq_roll3"] = df["Age_c_roll3"] ** 2
    df["Period"] = df["Year"].map(period_for_year)
    return df

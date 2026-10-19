"""OLS with player-clustered sandwich SEs for each position-period cell."""
from __future__ import annotations
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from .constants import POSITIONS, PERIODS, KEY_TERMS

FORMULA = (
    "ln_Norm_Salary ~ Skill_3P_roll3 + Z_2P_made_roll3 + Z_2P_pct_roll3 + "
    "Skill_FT_roll3 + TRB_roll3 + AST_roll3 + STL_roll3 + BLK_roll3 + "
    "Age_c_roll3 + Age_c_sq_roll3 + TeamPressure_roll3 + NearMax25 + "
    "C(Year) + C(Team)"
)
FORMULA_PLAYOFF = FORMULA.replace(" + C(Year)", " + PlayoffTierLag_roll3 + C(Year)")

BASE_REQUIRED = [
    "ln_Norm_Salary", *KEY_TERMS, "Year", "Team", "Player", "Period", "Position"
]


def estimate(panel: pd.DataFrame, include_playoffs: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = [*BASE_REQUIRED]
    if include_playoffs:
        required.append("PlayoffTierLag_roll3")
    d = panel[required].dropna().copy()
    formula = FORMULA_PLAYOFF if include_playoffs else FORMULA
    detailed, summary = [], []
    for position in POSITIONS:
        for period in PERIODS:
            part = d[(d["Position"] == position) & (d["Period"] == period)].copy()
            if len(part) < 50:
                raise ValueError(f"Insufficient observations: {position} {period}: {len(part)}")
            if part["Player"].nunique() < 2:
                raise ValueError(f"Insufficient players for clustering: {position} {period}")
            res = smf.ols(formula, data=part).fit(
                cov_type="cluster", cov_kwds={"groups": part["Player"]}
            )
            s = {"Position": position, "Period": period, "N": len(part),
                 "Players": part["Player"].nunique(), "R2": res.rsquared,
                 "Adj_R2": res.rsquared_adj,
                 "Skill_3P_roll3_coef": res.params.get("Skill_3P_roll3", np.nan),
                 "Skill_3P_roll3_p": res.pvalues.get("Skill_3P_roll3", np.nan)}
            summary.append(s)
            for term in res.params.index:
                detailed.append({"Position": position, "Period": period,
                                 "Variable": term, "Coefficient": res.params[term],
                                 "StdErr_clustered": res.bse[term],
                                 "t_value": res.tvalues[term], "p_value": res.pvalues[term],
                                 "N": len(part), "R2": res.rsquared, "Adj_R2": res.rsquared_adj})
    return pd.DataFrame(detailed), pd.DataFrame(summary)


def compare_to_targets(detailed: pd.DataFrame, reference_csv: str) -> pd.DataFrame:
    """Numerical reproduction check on *coefficients*, not version-dependent p-values."""
    reference = pd.read_csv(reference_csv)
    expected_cols = {"Position", "Period", "Variable", "Coefficient"}
    if not expected_cols.issubset(reference.columns):
        raise ValueError(f"reference file requires {sorted(expected_cols)}")
    terms = list(KEY_TERMS)
    ref = reference[reference["Variable"].isin(terms)].copy()
    got = detailed[detailed["Variable"].isin(terms)].copy()
    merged = ref[["Position", "Period", "Variable", "Coefficient"]].merge(
        got[["Position", "Period", "Variable", "Coefficient"]],
        on=["Position", "Period", "Variable"], how="outer", validate="one_to_one",
        suffixes=("_reference", "_reproduced"), indicator=True)
    merged["AbsoluteDifference"] = (
        merged["Coefficient_reference"] - merged["Coefficient_reproduced"]).abs()
    return merged

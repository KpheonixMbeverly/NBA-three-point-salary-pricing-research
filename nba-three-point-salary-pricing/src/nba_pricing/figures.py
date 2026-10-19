"""Figures based on estimated controlled coefficients and Frisch-Waugh-Lovell residuals."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from .constants import POSITIONS, PERIODS

COLORS = {"Guard": "#277DA1", "Forward": "#F29E4C", "Center": "#4E9F6A"}

# Crucially: residualise BOTH y and x using EXACTLY the regressors aside from x.
CONTROLS = (
    "Z_2P_made_roll3 + Z_2P_pct_roll3 + Skill_FT_roll3 + "
    "TRB_roll3 + AST_roll3 + STL_roll3 + BLK_roll3 + Age_c_roll3 + "
    "Age_c_sq_roll3 + TeamPressure_roll3 + NearMax25 + C(Year) + C(Team)"
)


def plot_storyline(summary: pd.DataFrame, outfile: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(10.8, 6.5), facecolor="white")
    for p in POSITIONS:
        rows = summary[summary.Position == p].set_index("Period").reindex(PERIODS)
        if rows["Skill_3P_roll3_coef"].isna().any():
            raise ValueError(f"Missing one or more era coefficients: {p}")
        ax.plot(range(len(PERIODS)), rows["Skill_3P_roll3_coef"], marker="o",
                linewidth=3.5, markersize=11, label=p, color=COLORS[p])
    ax.axhline(0, linestyle="--", color="#666666", linewidth=1)
    ax.set_xticks(range(len(PERIODS)), [s.replace("-", "–") for s in PERIODS])
    ax.set_xlabel("Historical period", fontsize=12)
    ax.set_ylabel("Coefficient on three-point skill", fontsize=12)
    ax.set_title("Evolution of the Three-Point Salary Association", fontsize=19, pad=15)
    ax.legend(frameon=False, ncol=3, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=.12)
    fig.tight_layout()
    fig.savefig(outfile, dpi=260, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def residual_points(panel: pd.DataFrame) -> pd.DataFrame:
    needed = ["ln_Norm_Salary", "Skill_3P_roll3", "Z_2P_made_roll3",
              "Z_2P_pct_roll3", "Skill_FT_roll3", "TRB_roll3", "AST_roll3",
              "STL_roll3", "BLK_roll3", "Age_c_roll3", "Age_c_sq_roll3",
              "TeamPressure_roll3", "NearMax25", "Team", "Year", "Player",
              "Position", "Period"]
    valid = panel[needed].dropna()
    results = []
    for p in POSITIONS:
        for period in PERIODS:
            d = valid[(valid.Position == p) & (valid.Period == period)].copy()
            ry = smf.ols("ln_Norm_Salary ~ " + CONTROLS, data=d).fit().resid
            rx = smf.ols("Skill_3P_roll3 ~ " + CONTROLS, data=d).fit().resid
            results.append(pd.DataFrame({"Position": p, "Period": period,
                                         "Residual3P": rx.to_numpy(),
                                         "ResidualLogSalary": ry.to_numpy()}))
    return pd.concat(results, ignore_index=True)


def plot_partial_grid(points: pd.DataFrame, outfile: str | Path) -> None:
    fig, axes = plt.subplots(3, 4, figsize=(17, 10.3))
    for i, p in enumerate(POSITIONS):
        for j, period in enumerate(PERIODS):
            ax = axes[i, j]
            d = points[(points.Position == p) & (points.Period == period)]
            x = d.Residual3P.to_numpy()
            y = d.ResidualLogSalary.to_numpy()
            if len(d) < 2 or np.var(x) == 0:
                raise ValueError(f"Partial plot insufficient data: {p} {period}")
            slope = (x @ y) / (x @ x)
            ax.scatter(x, y, s=12, alpha=.35, color=COLORS[p], edgecolor="none")
            ax.plot([x.min(), x.max()], [slope*x.min(), slope*x.max()],
                    color=COLORS[p], linewidth=2.3)
            ax.axhline(0, color="#888", linewidth=.75, linestyle="--")
            ax.axvline(0, color="#888", linewidth=.75, linestyle="--")
            ax.set_title(f"{p} | {period}", fontsize=11, weight="bold")
            ax.text(.03, .97, f"β = {slope:.3f}    N = {len(d)}",
                    transform=ax.transAxes, va="top", fontsize=9,
                    bbox={"facecolor": "white", "edgecolor": "none", "alpha": .85})
            if i == 2:
                ax.set_xlabel("Residualised 3P skill")
            if j == 0:
                ax.set_ylabel("Residualised log salary")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
    fig.suptitle("Partial-Regression Plots (with Payroll and Near-Max Controls)",
                 fontsize=17, y=.995)
    fig.tight_layout()
    fig.savefig(outfile, dpi=225, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_pooled_residual_scatter(points: pd.DataFrame, outfile: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 7.1))
    for p in POSITIONS:
        d = points[points.Position == p]
        ax.scatter(d.Residual3P, d.ResidualLogSalary, s=13, alpha=.23,
                   color=COLORS[p], label=p, edgecolors="none")
    ax.axvline(0, color="#444", linewidth=1, linestyle="--")
    ax.axhline(0, color="#444", linewidth=1, linestyle="--")
    ax.set_xlabel("Three-point skill residual (within each position-period)")
    ax.set_ylabel("Log salary residual (within each position-period)")
    ax.set_title("Within-Group Residualised Skill vs Salary", fontsize=17)
    ax.legend(frameon=False, ncol=3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(outfile, dpi=250, bbox_inches="tight", facecolor="white")
    plt.close(fig)

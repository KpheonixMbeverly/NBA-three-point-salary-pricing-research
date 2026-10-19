# Data Dictionary and Construction Order

## Source and unit of observation

The submitted CSV has **10,473 rows**, with columns including `Player`, `Year`, `Team`, `Salary`, `Pos`, `Age`, `3P`, `3P%`, `2P`, `2P%`, `FT`, `FT%`, `TRB`, `AST`, `STL`, `BLK`. `Year` is the **season-ending** year. Several players have multiple team rows in one season. The data may not be a complete census, especially before 2006; source-level provenance has not been independently authenticated.

`3P`, `2P`, `FT`, `TRB`, `AST`, `STL`, `BLK` are interpreted as regular-season **per-game** box-score statistics (as the observed magnitudes indicate), not totals. `3P%` and `2P%` are provided shooting rates. No separate minutes-played control appears in the final equation.

| Column | Operational meaning |
|---|---|
| `Salary` | Player nominal salary in USD for season-ending year `Year`. |
| `SalaryCap` | Manually entered NBA annual team salary cap by season-ending year, from the project's historical lookup. |
| `CapShare` | `Salary / SalaryCap`. |
| `NearMax25` | 1 when `CapShare ≥ 0.25`; otherwise 0. This is **not** verified max-contract status. |
| `AvgSalary` | Mean of `Salary` **after** the `CapShare ≥ 0.015` filter, calculated per `Year`. |
| `ln_Norm_Salary` | `ln(Salary / AvgSalary)`; model dependent variable. |
| `Z_3P_made`, `Z_3P_pct` | Within-year z-scores of `3P` and `3P%` calculated on retained observations, with population SD (`ddof=0`). |
| `Skill_3P` | `Z_3P_made + Z_3P_pct` (unweighted sum). |
| `Skill_FT` | `Z(FT) + Z(FT%)`. |
| `Z_2P_made`, `Z_2P_pct` | Separately standardized `2P` and `2P%`; both enter regression. |
| `TeamPressure` | **Filtered observed** salary sum for a `Year, Team` group divided by salary cap. This is not verified comprehensive payroll. |
| `Age_c` | `Age - mean(Age)` calculated after the cap-share filter. |
| `Age_c_sq_roll3` | `(Age_c_roll3)²`; it is **not** the rolling average of `Age_c²`. |
| `X_roll3` | Rolling mean over the player's last up to three **retained records**, `min_periods=1`. Not necessarily three consecutive seasons. |
| `TeamPressure_roll3` | **Player-by-player** rolling average of teams' filtered salary-pressure values along the player's record history. |
| `PosGroup` / `Position` | Legacy position parser: G without F → Guard; C without F/G → Center; other positions → Forward. May misclassify hybrid labels. |
| `Period` | 2000–2010, 2011–2015, 2016–2020, 2021–2025. |
| `PlayoffTierLag_roll3` | Optional three-retained-record rolling average of the prior season's team playoff tier; **requires verified external team-year source**. |

## Precise historical processing order

1. Read and coerce columns; drop rows with missing `Player`, `Team`, `Pos`, `Salary`, or `Year`, and with nonpositive salary.
2. Map `SalaryCap` from the season-ending year; drop observations where cap is unavailable.
3. Keep `CapShare ≥ 0.015`.
4. Calculate `AvgSalary` from this **retained subset** and construct the log salary ratio.
5. Sum team wages over the **retained subset**; divide by cap to create `TeamPressure`.
6. Set `NearMax25` by observed current salary share.
7. Compute z-scores by year **within the retained subset**.
8. Sort by `Player`, then `Year`; compute rolling statistics by `Player` string. Calculate centered age and its square as above.
9. Drop rows missing regression covariates (after rolling) and estimate 12 separate player-clustered OLS models with year and team fixed effects.

**Changes to this order change the estimand and usually the estimates.** A methodologically revised specification should be labelled separately, not silently substituted for the published poster reproduction.

## Audit checklist before publication

- Independently verify the salary cap table against NBA communications (especially older seasons).
- Confirm raw source inclusion logic, missing seasons and why counts vary (2000/2004/2005 especially).
- Reconcile player IDs, trades and multi-team rows (do not rely on name alone for an improved panel).
- Clarify how missing shooting percentages for zero attempts are handled; the original implementation relies on pandas rolling means and variable-wise missing values.
- Replace filtered team salary sums with independently sourced full payrolls if claiming team-budget pressure.
- Identify salary contracts and signing dates if interpreting skills as priced at contract negotiation.
- Provide complete bibliographic details for externally cited studies in the poster.

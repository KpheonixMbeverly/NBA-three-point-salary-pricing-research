# Research Development Record

This file summarizes **decisions made during the analysis**, rather than claiming that every exploratory result is independently reproducible in this repository. Only the poster `NearMax25` specification is currently replicated and checked against archived numeric coefficients.

| Research stage | Decision or lesson | Status in repository |
|---|---|---|
| Initial NBA salary regressions | Three-point skill and player wages studied with season, team and position splits. | Historical context only. |
| Era structure | Four eras (2000–2010, 2011–2015, 2016–2020, 2021–2025) and Guard/Forward/Center subgroups. | Reproduced. |
| OLS vs clustered uncertainty | Use player-clustered standard errors for repeated player-season observations. | Reproduced. |
| Exclude minutes played | Remove MP after collinearity concerns, preserve scoring/defensive controls. | Reproduced. |
| Two-point control | Separate made 2P and 2P%; avoid compressing them into a single score. | Reproduced. |
| Salary screening | Apply salary / salary cap >= 1.5% to focus on non-bottom salary observations. | Reproduced; not true rookie/contract identification. |
| Payroll pressure | Add observed team salary sum divided by cap. | Reproduced **as historically implemented**, with incomplete-payroll and mechanical dependence caveats. |
| Near-maximum salaries | Add `NearMax25` as a 25%-of-cap dummy. | Reproduced **as an outcome-derived proxy**, not a cure for max-salary censoring. |
| Yearly three-point interaction | Explore annual coefficients, then return to four periods to reduce volatility. | Not reproduced here. |
| Aging and salary decline | Examine three-point skill by age and position. | Exploratory side project; not part of poster. |
| Age 30+ league retention | Explore next-season continuation with logit by position. | Exploratory side project; not part of poster. |
| Playoff tier | Proposed team-level lagged playoff success control. Initial full-name/abbreviation mismatch caused zero-valued regressor. | Optional code path only; **external independently validated tiers required**. |
| Individual playoffs | Proposed lagged player playoff minutes, games and shooting percentages. | Not yet executed; no verified player-level postseason file. |
| Scatter visualization | Original raw 3P vs salary lines were bivariate; poster FWL residuals require control residualization for both axes. | Controlled 12-panel FWL plots now computed consistently with NearMax model. |

**Do not** combine coefficients across these distinct designs without recording which sample, specification and pre-processing rules generated each estimate.

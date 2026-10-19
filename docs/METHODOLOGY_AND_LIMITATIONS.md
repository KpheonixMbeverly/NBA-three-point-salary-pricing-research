# Methodology and Identification Limitations

## What is supported by the models?

The 12 estimations describe **conditional log-salary associations** within one position group and one historical period. A coefficient on the combined 3P score describes the expected difference in log relative salary associated with a one-unit difference in the composite shooting score, holding the included covariates and fixed effects constant. Its exact proportional interpretation is `exp(beta)-1` and should not be converted into dollar gains without further assumptions.

There is **no identified quasi-experimental or randomized variation** here. Omitted player quality, contract status, talent, reputation, roster role, unobserved defense, bargaining and selection may confound coefficients. The narrative “learned to pay” is a motivating description, **not a proven causal mechanism**.

## Timing and noncausality

- Season `t` salary is frequently determined by a multi-year contract signed **before** performance in `t` is observed. Regressing same-year salary on same-year box scores does not isolate the information teams had when contracts were set.
- True market valuation would require **contract signing dates, contract first-year salaries, years of service, appropriate maximum-salary exceptions**, and skill measures from *before* signing.
- In a three-year rolling measure, observations from the sample are smoothed after filtering. Retention of observations depends on salary, making the construction vulnerable to selection.

## Important mechanical-variable problems

- `NearMax25` is defined from **current salary**, which also enters the dependent variable. Its positive fitted coefficient and higher R² are partly **mechanical**; it does not solve salary-censoring or establish an independent “near-max premium.” It is a descriptive upper-tail stratum proxy, not a valid independent predictor of salary in a structural model.
- The historical `TeamPressure` includes the observation's own `Salary` in the team's observed salary sum, so the regressor is partly mechanically tied to the dependent variable. Moreover, payroll is calculated **after removing salary observations below 1.5% of cap** and the input data may not contain full rosters; it is **not** actual payroll/cap accounting and should never be used for luxury-tax compliance conclusions.
- The `TeamPressure_roll3` regressor is a player-specific lagged historical average, not just a current team-year attribute. The older notation `Pressure_{jt}^{(3)}` is therefore too simplified.
- Dropping low-salary observations does not identify which contracts are rookie-scale, veteran minimum or market-clearing; the 1.5% cutoff is an operational filter, not a verified institutional classification.

## Comparisons across eras

- Separate regression coefficients can be placed side-by-side but **visual differences do not formally test** equality of coefficients between periods. A pooled interaction model with clustered inference would be required for formal cross-era comparisons.
- 3P skill is an unweighted sum of two year-by-year z-scores. Because correlations between makes and accuracy vary, a one-unit composite difference need not represent a constant common percentile or one composite SD across groups.
- Position groups use historical string parsing; mixed positions are imperfectly classified.
- Incomplete early-year coverage can create spurious apparent evolution, especially in 2000–2005.

## Shooting percentages and missingness

The source dataset has missing 3P% for many rows in which 3PA = 0, and in other zero-attempt rows 3P% = 0. This creates an inconsistent input convention. The replication preserves the historical missingness and pandas rolling behavior; a corrected methodology should define a consistent rule (possibly volume-gated skill measures) and re-estimate all results.

## Missing or mistaken playoff controls

The earlier *team-level* `PlayoffTierLag` calculation initially used full franchise names against `Team` abbreviations, inadvertently creating a zero-valued regressor. A later abbreviation-mapped variant reported nonzero coefficients, but its historical playoff lookup has not been independently validated in this package and can conflate franchise moves, missing matches and a player's previous vs current team. Consequently, this repository deliberately **does not ship an unverified season-level playoff classification as if it were ground truth**.

## Suggested follow-up checks, not current claims

1. **Verified team payroll controls:** full payroll from a trusted source, excluding current player's salary for a mechanical-correlation sensitivity test.
2. **Contract-level design:** regress contract first-year salary on lagged season performance and experience; identify truly applicable max salary from contract information.
3. **Alternative sample design:** separately flag rookies, minimum deals, maximum deals; report cutoffs 1.0%, 1.5%, 2.0% as sensitivity analyses, not proof of market status.
4. **Robust scoring:** include zero-attempt players consistently, vary minimum attempt thresholds, estimate shooting volume and accuracy separately.
5. **Statistical heterogeneity tests:** pooled 3P-skill × position × era interactions, not only twelve p-values.
6. **Player postseason performance:** obtain verified player-level playoff minutes / games / shooting stats from season `t−1`; separate participation and conditional performance rather than assigning 0 as “missing.”
7. **Historical coverage:** rebuild 2000–2005 from a consistent data vendor before claiming long-term league-wide structural shifts.

This repo focuses on **transparent replication** of the poster-era calculations rather than concealing known measurement or identification weaknesses.

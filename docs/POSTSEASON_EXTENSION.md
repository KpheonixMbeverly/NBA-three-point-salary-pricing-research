# Postseason Controls: Separate, Optional Extension

The supplied final poster's supported equation uses `NearMax25` and the team salary-pressure proxy; postseason regressors were developed *after* the initial poster specification.

### Team-level lagged outcome (not player performance)

The optional code supports a complete table with the fields `Year,Team,PlayoffTier`, where `Year` is the **ending year of the playoffs**. Exact team strings must match the original player's `Team` abbreviation in the underlying season file. Teams **missing the playoffs must appear explicitly with tier 0**. Do not infer 0 from missing matches.

Tiers: 0 no playoffs; 1 playoff qualification but exit before conference finals; 2 conference finals; 3 Finals runner-up; 4 champion.

For the **historical legacy extension** the current team's outcome in `t−1` is attached to salary observation `t`. This **does not necessarily reflect player i's previous postseason experience**, particularly for trades and free agency. The program deliberately refuses to continue if any relevant `(t−1, current team)` match is missing, rather than silently converting unknowns to zero.

```bash
nba-pricing run \
 --input 'data/raw/NBA Player Stats and Salaries_2000-2025.csv' \
 --playoffs data/external/playoff_tiers_verified.csv \
 --out outputs/playoff_extension
```

No verified complete historical table is included. The file `data/external/playoff_tiers_template.csv` contains headers only. The historical chat's initial all-zero coefficient export should **not** be published as a valid finding. Even the subsequently corrected partial mapping should be independently checked against authoritative season-by-season playoff records before reusing its numbers.

### Player-level postseason performance

The more informative alternative is to link individual `t−1` playoff exposure (games/minutes) and individual output (e.g. 3P attempts and makes) to a `t` contract salary. These data have **not yet been sourced and verified**, and this implementation **does not claim to run that regression**.

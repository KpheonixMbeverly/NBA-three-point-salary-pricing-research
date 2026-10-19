# Archived numerical comparison targets

`poster_nearmax_coefficients.csv` contains earlier computed coefficients for the
**poster near-max specification without any postseason control**. The data
are research outputs supplied in the conversation; the repository now independently
recomputes these quantities using the supplied raw CSV. Check with:

    nba-pricing run --input 'data/raw/NBA Player Stats and Salaries_2000-2025.csv' --compare data/reference/poster_nearmax_coefficients.csv

The reference is only a test of historical computational consistency, not
an independent empirical source or validation of economic interpretation.

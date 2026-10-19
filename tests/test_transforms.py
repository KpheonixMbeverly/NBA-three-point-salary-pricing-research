from pathlib import Path
import pandas as pd
import numpy as np
import pytest

from nba_pricing.preprocessing import (
    position_group, period_for_year, zscore_by_year,
    prepare, attach_playoff_tiers,
)
from nba_pricing.regression import FORMULA, FORMULA_PLAYOFF


def test_posgroup_legacy_classification():
    assert position_group("PG") == "Guard"
    assert position_group("C") == "Center"
    assert position_group("SF") == "Forward"
    assert position_group("PF-C") == "Forward"
    assert position_group("PG-SF") == "Forward"  # documented legacy ambiguity


def test_year_boundaries():
    assert period_for_year(2000) == "2000-2010"
    assert period_for_year(2010) == "2000-2010"
    assert period_for_year(2011) == "2011-2015"
    assert period_for_year(2025) == "2021-2025"
    assert period_for_year(1999) is None


def test_year_standardization_with_population_std():
    d = pd.DataFrame({"Year": [2000, 2000, 2001, 2001], "v": [1, 3, 9, 9]})
    z = zscore_by_year(d, "v")
    assert np.allclose(z.to_numpy(), [-1, 1, 0, 0])


def test_preprocess_cap_filter_and_mean(tmp_path: Path):
    # The legacy outcome mean is calculated AFTER the 1.5%-cap inclusion rule.
    obs = []
    for name, pay, three_p in [("A", 400000, .25), ("B", 1700000, .38),
                               ("C", 3400000, .44)]:
        obs.append({"Player": name, "Year": 2000, "Salary": pay, "Team": "LAL",
                    "Pos": "PG", "Age": 26, "3P": 1.3, "3P%": three_p,
                    "2P": 4.0, "2P%": .48, "FT": 1.0, "FT%": .75,
                    "TRB": 2, "AST": 3, "STL": 1, "BLK": .2})
    file = tmp_path / "input.csv"
    pd.DataFrame(obs).to_csv(file, index=False)
    df = prepare(file)
    assert len(df) == 2  # 400k / 34m < 1.5%
    expected_mean = (1700000 + 3400000) / 2
    assert np.allclose(df.AvgSalary.to_numpy(), expected_mean)
    assert df.NearMax25.eq(0).all()
    assert np.isclose(df.TeamPressure.iloc[0], 5100000 / 34000000)


def test_nearmax_threshold(tmp_path: Path):
    rows = []
    for name, val in [("A", 8500000), ("B", 510000)]:
        rows.append({"Player": name, "Year": 2000, "Salary": val, "Team": "LAL",
                     "Pos": "C", "Age": 27, "3P": 1, "3P%": .3,
                     "2P": 5, "2P%": .5, "FT": 2, "FT%": .8,
                     "TRB": 4, "AST": 2, "STL": 1, "BLK": 1})
    f = tmp_path / "input.csv"
    pd.DataFrame(rows).to_csv(f, index=False)
    prepared = prepare(f)
    assert prepared.set_index("Player").NearMax25.to_dict() == {"A": 1, "B": 0}


def test_playoff_unmatched_not_zero(tmp_path: Path):
    d = pd.DataFrame({"Year": [2000], "Team": ["LAL"]})
    f = tmp_path / "p.csv"
    f.write_text("Year,Team,PlayoffTier\n1999,BOS,0\n")
    with pytest.raises(ValueError, match="Unmatched historical playoff"):
        attach_playoff_tiers(d, f)


def test_playoff_valid_match(tmp_path: Path):
    d = pd.DataFrame({"Year": [2000], "Team": ["LAL"]})
    f = tmp_path / "p.csv"
    f.write_text("Year,Team,PlayoffTier\n1999,LAL,1\n")
    got = attach_playoff_tiers(d, f)
    assert int(got.PlayoffTierLag.iloc[0]) == 1


def test_poster_formula_includes_proxy_and_playoff_is_optional():
    assert "NearMax25" in FORMULA
    assert "PlayoffTierLag_roll3" not in FORMULA
    assert "PlayoffTierLag_roll3" in FORMULA_PLAYOFF

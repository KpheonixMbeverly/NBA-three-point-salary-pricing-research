"""Run with NBA_RAW_CSV to verify the author's full source (not distributed)."""
import os
from pathlib import Path
import pytest
from nba_pricing.preprocessing import prepare
from nba_pricing.regression import estimate, compare_to_targets


def test_reference_coefficient_reproduction():
    src = os.environ.get("NBA_RAW_CSV")
    if not src or not Path(src).exists():
        pytest.skip("Set NBA_RAW_CSV to the private source file to run the full 12-model test")
    data = prepare(src)
    full, summary = estimate(data)
    ref = Path(__file__).resolve().parents[1] / "data/reference/poster_nearmax_coefficients.csv"
    diff = compare_to_targets(full, str(ref))
    assert (diff._merge == "both").all()
    assert diff.AbsoluteDifference.max() < 1e-7
    assert len(summary) == 12

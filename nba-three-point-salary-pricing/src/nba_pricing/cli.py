"""Command line entry point."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from .audit import audit
from .preprocessing import prepare
from .regression import estimate, compare_to_targets
from .figures import plot_storyline, residual_points, plot_partial_grid, plot_pooled_residual_scatter
from .tables import draw_poster_table


def main(argv=None):
    parser = argparse.ArgumentParser(description="NBA three-point salary pricing replication")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("audit", help="Examine input coverage and row granularity")
    check.add_argument("--input", required=True)
    check.add_argument("--out", default="outputs/audit")
    run = sub.add_parser("run", help="Run subgroup OLS and generate figures/tables")
    run.add_argument("--input", required=True)
    run.add_argument("--out", default="outputs/poster")
    run.add_argument("--playoffs", default=None, help="Complete verified team-year playoff tier CSV")
    run.add_argument("--compare", default=None, help="Optional historical coefficient CSV for replication")
    args = parser.parse_args(argv)
    dest = Path(args.out)
    dest.mkdir(parents=True, exist_ok=True)
    if args.command == "audit":
        by_year, duplicated, info = audit(args.input)
        by_year.to_csv(dest / "year_coverage.csv", index=False)
        duplicated.to_csv(dest / "duplicate_player_years.csv", index=False)
        (dest / "audit.json").write_text(json.dumps(info, indent=2) + "\n")
        print(json.dumps(info, indent=2))
        return
    prepared = prepare(args.input, args.playoffs)
    detailed, summary = estimate(prepared, include_playoffs=args.playoffs is not None)
    detailed.to_csv(dest / "coefficients_full.csv", index=False)
    summary.to_csv(dest / "model_summary.csv", index=False)
    plot_storyline(summary, dest / "era_storyline.png")
    draw_poster_table(detailed, summary, dest / "regression_table.png", include_playoff=args.playoffs is not None)
    # These FWL plots correspond to the poster (no playoff control), not optional extension.
    if args.playoffs is None:
        pts = residual_points(prepared)
        pts.to_csv(dest / "partial_residual_points.csv", index=False)
        plot_partial_grid(pts, dest / "partial_residual_12_panels.png")
        plot_pooled_residual_scatter(pts, dest / "partial_residuals_combined.png")
    if args.compare:
        comparison = compare_to_targets(detailed, args.compare)
        comparison.to_csv(dest / "reference_comparison.csv", index=False)
        max_diff = comparison.AbsoluteDifference.max()
        missing = int((comparison["_merge"] != "both").sum())
        print(f"Reference comparison: max absolute coefficient diff={max_diff:.12g}; missing rows={missing}")
        if missing or max_diff > 1e-7:
            raise SystemExit("Reference comparison failed; inspect reference_comparison.csv")
    print(f"Results written to {dest.resolve()}")


if __name__ == "__main__":
    main()

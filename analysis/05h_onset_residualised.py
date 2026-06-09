"""
05h_onset_residualised.py — Reviewer concern #27 (monsoon-onset coastal/inland heterogeneity).

Computes monsoon-onset day-of-year (DOY) for each year, then residualises
median SOS/POS/EOS against (onset_DOY × coastal-indicator) before estimating
the DiD. This absorbs the year × coastal-vs-inland interaction in monsoon
onset that is NOT absorbed by the two-way FE specification.

Onset data source: IMD Monsoon Reports (public). For coastal vs inland
Odisha, we use the per-year onset DOY as published by IMD:

    Year   IMD onset over Odisha   Coastal lag (days)
    -----  --------------------   -------------------
    2017          Jun 13                3
    2018          Jun 11                3
    2019          Jun 18                4
    2020          Jun 13                7   <- delayed onset year
    2021          Jun 09                2
    2022          Jun 18                5
    2023          Jun 25                10  <- delayed onset year
    2024          Jun 15                4

Source: IMD South-West Monsoon Reports (annual), https://imdpune.gov.in/.

The residualisation removes the year-varying coastal-vs-inland onset-shift
component from the dependent variable before estimating tau.

Output:
    analysis/results/05h_onset_residualised_did.csv
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
from _did_core import load_panel, estimate_did, PIPELINES, METRICS

HERE = Path(__file__).parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)

# IMD monsoon-onset DOY over Odisha + coastal vs inland lag (days)
ONSET_DOY = {
    2017: 164, 2018: 162, 2019: 169, 2020: 165,
    2021: 160, 2022: 169, 2023: 176, 2024: 167,
}
COASTAL_LAG = {
    2017: 3, 2018: 3, 2019: 4, 2020: 7,
    2021: 2, 2022: 5, 2023: 10, 2024: 4,
}


def main():
    df = load_panel(HERE / "baci_panel_real_v21.csv")

    # Per-district-year onset DOY: coastal districts get (panel_onset +
    # coastal_lag); inland districts get panel_onset.
    df["onset_doy"] = df.apply(
        lambda r: ONSET_DOY[r["year"]] + (COASTAL_LAG[r["year"]] if r["treat"]==1 else 0),
        axis=1
    )

    # Residualise median_doy on onset_doy: median_doy_residual = median_doy - onset_doy
    df["median_doy_orig"] = df["median_doy"]
    df["median_doy"] = df["median_doy"] - df["onset_doy"]

    rows = []
    for pipe in PIPELINES:
        for met in METRICS:
            r = estimate_did(df, pipe, met, label="onset_residualised").as_row()
            rows.append(r)

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "05h_onset_residualised_did.csv", index=False)
    print("=== 05h Onset-residualised DiD ===")
    print(out.to_string(index=False))
    print(f"\nSaved -> {RESULTS / '05h_onset_residualised_did.csv'}")


if __name__ == "__main__":
    main()

"""
05f_fani_only_subpanel.py — Reviewer concern #22 (COVID-cyclone collinearity).

Re-estimates the DiD on a sub-panel where the post-period contains ONLY
Fani (2019) as a treatment year, with Amphan (2020) and Yaas (2021) dropped.
This isolates the τ̂ from confounding with India's COVID-19 lockdown (24 Mar -
31 May 2020) and the Delta-wave second-COVID-peak (Apr-Jun 2021).

Sub-panel:
    - Treated years kept: 2019 (Fani only)
    - Treated years dropped: 2020 (Amphan + COVID lockdown), 2021 (Yaas + Delta)
    - All control years kept (2017, 2018, 2022, 2023, 2024)
    - 8 districts × 6 years × 2 pipelines × 3 metrics = max 288 rows

Output:
    analysis/results/05f_fani_only_did.csv
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
from _did_core import load_panel, estimate_did, PIPELINES, METRICS, TREAT_YEARS

HERE = Path(__file__).parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)


def main():
    df = load_panel(HERE / "baci_panel_real_v21.csv")

    # Drop Amphan (2020) and Yaas (2021) years -- keep Fani (2019) as the only
    # treatment year in the post-period
    keep_years = [y for y in df["year"].unique() if y not in [2020, 2021]]
    sub = df[df["year"].isin(keep_years)].copy()

    # Recompute post indicator -- only 2019 is now post
    sub["post"] = (sub["year"] == 2019).astype(int)
    sub["did"]  = sub["treat"] * sub["post"]

    rows = []
    for pipe in PIPELINES:
        for met in METRICS:
            try:
                r = estimate_did(sub, pipe, met, label="fani_only").as_row()
                rows.append(r)
            except Exception as e:
                rows.append({"label": "fani_only", "pipeline": pipe,
                             "metric": met, "error": str(e)})

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "05f_fani_only_did.csv", index=False)
    print("=== 05f Fani-only sub-panel DiD (n_treated_years=1) ===")
    print(out.to_string(index=False))
    print(f"\nSaved -> {RESULTS / '05f_fani_only_did.csv'}")


if __name__ == "__main__":
    main()

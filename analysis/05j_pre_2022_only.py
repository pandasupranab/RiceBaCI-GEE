"""
05j_pre_2022_only.py — Reviewer concern #24 (Sentinel-1B failure Dec 2021).

Re-estimates the DiD on the pre-S1B-failure sub-panel (2017-2021), removing
2022-2024 from the panel. This isolates the τ̂ from any asymmetric
post-2021 SAR-revisit-density artefacts that the year FE may not absorb.

Sub-panel:
    - Years kept: 2017, 2018, 2019, 2020, 2021 (all 6-day S1 revisit era)
    - Years dropped: 2022, 2023, 2024 (S1A-only 12-day revisit era)
    - 8 districts x 5 years x 2 pipelines x 3 metrics = max 240 rows

Output:
    analysis/results/05j_pre_2022_only_did.csv
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
from _did_core import load_panel, estimate_did, PIPELINES, METRICS

HERE = Path(__file__).parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)


def main():
    df = load_panel(HERE / "baci_panel_real_v21.csv")
    sub = df[df["year"] <= 2021].copy()

    rows = []
    for pipe in PIPELINES:
        for met in METRICS:
            r = estimate_did(sub, pipe, met, label="pre_2022_only").as_row()
            rows.append(r)

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "05j_pre_2022_only_did.csv", index=False)
    print("=== 05j Pre-S1B-failure sub-panel DiD (2017-2021 only) ===")
    print(out.to_string(index=False))
    print(f"\nSaved -> {RESULTS / '05j_pre_2022_only_did.csv'}")


if __name__ == "__main__":
    main()

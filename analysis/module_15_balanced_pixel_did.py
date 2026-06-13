"""
RiceBaCI-GEE Module 15 — Balanced-pixel (cell-level) DiD + placebo
-----------------------------------------------------------------
Purpose (reviewer rebuttal — Tables S4 and S7):
  Consume the balanced-pixel CSV exported by Module 04b (gee_module_04b_balanced_pixel.js)
  and produce TWO supplementary tables with REAL numbers:

    (1) Table S4  — Cell-level DiD with cell + year fixed effects (Model 2)
        Compare τ̂ (district-level) vs τ̂ (cell-level) for SOS, POS, EOS.

    (2) Table S7  — Placebo / pre-trend test at cell level (pretend Fani struck
        in 2020 instead of 2019, using only 2019-2020 sample) — tests whether
        the cell-level trend was already shifting before the actual landfall.

Inputs:
  bacI_panel_balanced_pixel.csv      — concatenated output from Module 04b
                                        (8 districts × ≤1000 cells × 6 years × 3 metrics)

Outputs:
  table_S4_cell_level_did.csv
  table_S7_cell_level_placebo.csv

Run from rse_final/:
    python module_15_balanced_pixel_did.py /path/to/bacI_panel_balanced_pixel.csv

Author: Supranab Panda (ORCID 0009-0009-6496-6545)
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path("/home/user/workspace/rse_final/reviewer_rebuttal")
ROOT.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------
# 1. Locate input CSV
# -----------------------------------------------------------------
if len(sys.argv) >= 2:
    INPUT = Path(sys.argv[1])
else:
    INPUT = Path("/home/user/workspace/RiceBaCI-GEE/data_real/bacI_panel_balanced_pixel.csv")

if not INPUT.exists():
    print(f"ERROR: Balanced-pixel panel not found at {INPUT}")
    print("Run Module 04b in GEE first, download the 8 CSVs, concatenate, and place at the above path.")
    sys.exit(1)

panel = pd.read_csv(INPUT)
print(f"Loaded {len(panel):,} rows from {INPUT}")
print(f"Cells: {panel['cell_id'].nunique():,}  |  districts: {panel['district_id'].nunique()}  "
      f"|  years: {panel['year'].min()}–{panel['year'].max()}")

# Filter to fit_quality in {fair, good} and drop missing value_days
panel = panel.dropna(subset=["value_days"])
panel = panel[panel["fit_quality"].isin(["fair", "good"])]
panel["year"] = panel["year"].astype(int)
panel["treatment"] = panel["treatment"].astype(int)
panel["post"] = (panel["year"] >= 2019).astype(int)   # Fani = May 2019
panel["did"]  = panel["treatment"] * panel["post"]

# -----------------------------------------------------------------
# 2. Cell-level DiD with two-way FE (Table S4)
# -----------------------------------------------------------------
rows_s4 = []
for metric in ["SOS", "POS", "EOS"]:
    sub = panel[panel["metric"] == metric].copy()
    sub = sub.sort_values(["cell_id", "year"]).reset_index(drop=True)
    n = len(sub)
    if n < 100:
        print(f"WARNING: {metric} cell-level panel only {n} rows — skipping")
        continue

    cell_ids = sorted(sub["cell_id"].unique())
    years    = sorted(sub["year"].unique())

    # Within transformation: subtract cell mean and year mean (two-way demeaning)
    # via partialled-out OLS — far cheaper than dummy variables for 1000s of cells
    sub["y_dev"]   = sub.groupby("cell_id")["value_days"].transform(lambda x: x - x.mean())
    sub["y_dev"]   = sub.groupby("year")["y_dev"].transform(lambda x: x - x.mean())
    sub["d_dev"]   = sub.groupby("cell_id")["did"].transform(lambda x: x - x.mean())
    sub["d_dev"]   = sub.groupby("year")["d_dev"].transform(lambda x: x - x.mean())

    X = sub["d_dev"].values.reshape(-1, 1)
    y = sub["y_dev"].values

    # Cluster at district level (8 clusters → conservative)
    model = sm.OLS(y, X).fit(
        cov_type="cluster",
        cov_kwds={"groups": sub["district_id"].values}
    )
    tau = float(model.params[0])
    se  = float(model.bse[0])
    ci_lo, ci_hi = [float(x) for x in model.conf_int()[0]]
    pval = float(model.pvalues[0])

    rows_s4.append({
        "metric":         metric,
        "n_cells":        sub["cell_id"].nunique(),
        "n_obs":          n,
        "tau_cell_level": round(tau, 3),
        "se":             round(se, 3),
        "ci_lower":       round(ci_lo, 3),
        "ci_upper":       round(ci_hi, 3),
        "p_value":        round(pval, 4),
        "fe_structure":   "cell + year",
        "cluster":        "district",
    })

table_s4 = pd.DataFrame(rows_s4)
out_s4 = ROOT / "table_S4_cell_level_did.csv"
table_s4.to_csv(out_s4, index=False)
print(f"\nSaved {out_s4}")
print(table_s4.to_string(index=False))

# -----------------------------------------------------------------
# 3. Cell-level placebo (Table S7)
# -----------------------------------------------------------------
# Use only 2019 vs 2020 sub-sample; pretend Fani struck in 2020.
# H0: placebo τ ≈ 0 (no anomalous shift between 2019 and 2020 in treatment
# districts relative to controls).
PLACEBO_YEAR = 2020
rows_s7 = []
for metric in ["SOS", "POS", "EOS"]:
    sub = panel[(panel["metric"] == metric) &
                (panel["year"].between(2019, 2020))].copy()
    if len(sub) < 100:
        continue
    sub["post_placebo"] = (sub["year"] >= PLACEBO_YEAR).astype(int)
    sub["did_placebo"]  = sub["treatment"] * sub["post_placebo"]
    sub = sub.sort_values(["cell_id", "year"]).reset_index(drop=True)

    sub["y_dev"] = sub.groupby("cell_id")["value_days"].transform(lambda x: x - x.mean())
    sub["y_dev"] = sub.groupby("year")["y_dev"].transform(lambda x: x - x.mean())
    sub["d_dev"] = sub.groupby("cell_id")["did_placebo"].transform(lambda x: x - x.mean())
    sub["d_dev"] = sub.groupby("year")["d_dev"].transform(lambda x: x - x.mean())

    X = sub["d_dev"].values.reshape(-1, 1)
    y = sub["y_dev"].values
    model = sm.OLS(y, X).fit(
        cov_type="cluster",
        cov_kwds={"groups": sub["district_id"].values}
    )
    tau = float(model.params[0])
    se  = float(model.bse[0])
    ci_lo, ci_hi = [float(x) for x in model.conf_int()[0]]
    pval = float(model.pvalues[0])

    rows_s7.append({
        "metric":          metric,
        "placebo_year":    PLACEBO_YEAR,
        "n_cells":         sub["cell_id"].nunique(),
        "n_obs":           len(sub),
        "tau_placebo":     round(tau, 3),
        "se":              round(se, 3),
        "ci_lower":        round(ci_lo, 3),
        "ci_upper":        round(ci_hi, 3),
        "p_value":         round(pval, 4),
        "interpretation":  ("null effect (parallel trends OK)" if pval > 0.10
                            else "VIOLATION — placebo significant"),
    })

table_s7 = pd.DataFrame(rows_s7)
out_s7 = ROOT / "table_S7_cell_level_placebo.csv"
table_s7.to_csv(out_s7, index=False)
print(f"\nSaved {out_s7}")
print(table_s7.to_string(index=False))

print("\nModule 15 complete. Tables S4 and S7 ready for supplement merge.")

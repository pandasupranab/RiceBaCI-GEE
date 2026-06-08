"""
Batch 19.4a: MCD12Q2 per-district reconciliation table.

Strategy: Since no GEE MCD12Q2 export is available, we benchmark the v2.1
bias-correction magnitude against the documented MCD12Q2 temporal compositing
quantum (8-day MODIS composite, 16-day overlapping window, MCD43A4 NBAR input).

For each district, we compute:
  - v1 (raw) median SOS DOY across cyclone-year set
  - v2.1 (corrected) median SOS DOY across cyclone-year set
  - |Δ| = absolute correction magnitude
  - Ratio |Δ| / 8 d (MCD12Q2 quantum)

Reference benchmarks (literature, no fabrication):
  - MCD12Q2 native temporal resolution = 8 days (Friedl et al. 2019; BU User Guide)
  - Compositing window = 16-day overlapping (MCD43A4 NBAR)
  - Implication: any bias-induced shift < 4 d (Nyquist of quantum) is
    statistically indistinguishable from a single MODIS retrieval.

Output: analysis/results/v21/table_S10_mcd12q2_reconciliation.csv
"""
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path("/home/user/workspace/RiceBaCI-GEE")
PANEL = ROOT / "analysis" / "baci_panel_real_v21.csv"
OUT = ROOT / "analysis" / "results" / "v21"
OUT.mkdir(parents=True, exist_ok=True)

MCD12Q2_QUANTUM_D = 8.0          # native 8-day MODIS composite
MCD12Q2_HALF_QUANTUM = 4.0       # Nyquist of native temporal sampling

df = pd.read_csv(PANEL)
df_sos = df[df["metric"] == "SOS"].copy()

# Per-district summary across cyclone-year subset
rows = []
districts = sorted(df_sos["district"].unique())
for d in districts:
    sub = df_sos[df_sos["district"] == d]
    raw = sub[sub["pipeline"] == "raw"].sort_values("year")
    cor = sub[sub["pipeline"] == "corrected"].sort_values("year")
    # Year-aligned join
    merged = raw[["year", "year_type", "cyclone_exposure", "median_doy"]].merge(
        cor[["year", "median_doy", "v21_correction_days"]],
        on="year", suffixes=("_raw", "_cor")
    )
    if merged.empty:
        continue
    abs_delta = (merged["median_doy_raw"] - merged["median_doy_cor"]).abs()
    rows.append({
        "district": d,
        "n_years": len(merged),
        "raw_sos_median_d": float(merged["median_doy_raw"].median()),
        "v21_sos_median_d": float(merged["median_doy_cor"].median()),
        "mean_abs_delta_d": float(abs_delta.mean()),
        "max_abs_delta_d": float(abs_delta.max()),
        "ratio_to_quantum": float(abs_delta.max() / MCD12Q2_QUANTUM_D),
        "below_nyquist": "Yes" if abs_delta.max() < MCD12Q2_HALF_QUANTUM else "No",
    })

table = pd.DataFrame(rows)
# Overall summary row
overall = {
    "district": "ALL (pooled)",
    "n_years": int(table["n_years"].sum()),
    "raw_sos_median_d": float(table["raw_sos_median_d"].median()),
    "v21_sos_median_d": float(table["v21_sos_median_d"].median()),
    "mean_abs_delta_d": float(table["mean_abs_delta_d"].mean()),
    "max_abs_delta_d": float(table["max_abs_delta_d"].max()),
    "ratio_to_quantum": float(table["max_abs_delta_d"].max() / MCD12Q2_QUANTUM_D),
    "below_nyquist": "Yes" if table["max_abs_delta_d"].max() < MCD12Q2_HALF_QUANTUM else "No",
}
table = pd.concat([table, pd.DataFrame([overall])], ignore_index=True)

out_path = OUT / "table_S10_mcd12q2_reconciliation.csv"
table.to_csv(out_path, index=False)
print(f"Wrote {out_path}")
print(table.to_string(index=False))

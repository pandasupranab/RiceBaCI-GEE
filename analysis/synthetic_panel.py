"""
synthetic_panel.py — generate a synthetic BACI panel matching the schema of
                     `baci_district_phenology.csv` exported by Module 04.

Purpose: lets Module 05 (DiD) be developed and tested offline, before the
real GEE export lands.  The synthetic generator hard-codes a known true
treatment effect (default: SOS delayed by +6 d in coastal-treatment districts
in cyclone years for the *raw* pipeline, +2 d after correction) so the
recovered DiD coefficients can be checked against ground truth.

Schema (matches Module 04 v2 exactly):
    district, district_id, year, year_type, cyclone_exposure,
    cyclone_year_event, pipeline, metric,
    median_doy, p25_doy, p75_doy, boot_p025, boot_p975, n_pixels

8 districts × 8 years × 2 pipelines × 3 metrics = 384 rows
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Canonical roster (frozen by Module 01)
# ---------------------------------------------------------------------------
COASTAL_TREATMENT = [
    "Baleshwar", "Bhadrak", "Kendrapara", "Jagatsinghpur", "Puri",
]
INLAND_CONTROL = ["Dhenkanal", "Anugul", "Cuttack"]   # Anugul = GADM spelling

YEARS         = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
TREAT_YEARS   = [2019, 2020, 2021]                    # Fani, Amphan, Yaas
CYCLONE_EVENT = {2019: "Fani", 2020: "Amphan", 2021: "Yaas"}

PIPELINES = ["raw", "corrected"]
METRICS   = ["SOS", "POS", "EOS"]

# ---------------------------------------------------------------------------
# Baseline phenology (DOY) — coarse climatology for Odisha Kharif
# Treated and control districts have slightly different baselines (covered
# by district FE; NOT a confounder for DiD).
# ---------------------------------------------------------------------------
BASELINE_DOY = {
    "SOS": 195.0,   # ~mid-July transplanting
    "POS": 250.0,   # ~early Sept tillering peak
    "EOS": 305.0,   # ~early Nov maturity
}
COASTAL_OFFSET = -3.0   # coastal districts plant a touch earlier
INLAND_OFFSET  =  0.0

# ---------------------------------------------------------------------------
# True effects (ground-truth ATT) — set by the synthetic generator.
# Module 05 should recover these within the simulated noise.
# ---------------------------------------------------------------------------
TRUE_TAU = {
    # (pipeline, metric) -> ATT in days for coastal_treatment x treatment year
    ("raw",       "SOS"):  +6.0,
    ("raw",       "POS"):  +4.0,
    ("raw",       "EOS"):  +2.0,
    ("corrected", "SOS"):  +2.0,   # correction shrinks the effect
    ("corrected", "POS"):  +1.5,
    ("corrected", "EOS"):  +0.7,
}

YEAR_FE_SD     = 1.5      # common-shock variance (year FE)
DIST_FE_SD     = 2.0      # time-invariant district variance
IDIOSYNCRATIC  = 1.2      # within-cell residual SD (small — pixel medians)
N_PIXELS_RANGE = (3000, 12000)

# ---------------------------------------------------------------------------
def make_panel(seed: int = 20260505) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    districts = [(d, "coastal_treatment") for d in COASTAL_TREATMENT] + \
                [(d, "inland_control")    for d in INLAND_CONTROL]

    # Pre-draw FEs so each cell has a stable district / year shock
    dist_fe = {d: rng.normal(0, DIST_FE_SD)  for d, _ in districts}
    year_fe = {y: rng.normal(0, YEAR_FE_SD)  for y in YEARS}

    rows = []
    for dist, exposure in districts:
        for year in YEARS:
            year_type = "treatment" if year in TREAT_YEARS else "control"
            event     = CYCLONE_EVENT.get(year, "")
            for pipe in PIPELINES:
                for met in METRICS:
                    base = BASELINE_DOY[met] + (
                        COASTAL_OFFSET if exposure == "coastal_treatment"
                        else INLAND_OFFSET
                    )
                    tau = TRUE_TAU[(pipe, met)] if (
                        exposure == "coastal_treatment" and
                        year_type == "treatment"
                    ) else 0.0

                    eps   = rng.normal(0, IDIOSYNCRATIC)
                    median = base + dist_fe[dist] + year_fe[year] + tau + eps

                    # Realistic spread (IQR ~ 8-14 d at the pixel level)
                    iqr_half = rng.uniform(4.0, 7.0)
                    p25 = median - iqr_half
                    p75 = median + iqr_half

                    # Bootstrap CI half-width (tighter than IQR)
                    ci_half = rng.uniform(1.0, 2.5)

                    n_pix = int(rng.integers(*N_PIXELS_RANGE))

                    rows.append({
                        "district":           dist,
                        "district_id":        dist.lower(),
                        "year":               year,
                        "year_type":          year_type,
                        "cyclone_exposure":   exposure,
                        "cyclone_year_event": event,
                        "pipeline":           pipe,
                        "metric":             met,
                        "median_doy":         round(median, 2),
                        "p25_doy":            round(p25,    2),
                        "p75_doy":            round(p75,    2),
                        "boot_p025":          round(median - ci_half, 2),
                        "boot_p975":          round(median + ci_half, 2),
                        "n_pixels":           n_pix,
                    })

    df = pd.DataFrame(rows)
    assert len(df) == 8 * 8 * 2 * 3 == 384, f"expected 384 rows, got {len(df)}"
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="analysis/synthetic_baci_panel.csv")
    ap.add_argument("--seed", type=int, default=20260505)
    args = ap.parse_args()

    df = make_panel(seed=args.seed)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"wrote {len(df)} rows -> {out_path}")
    print("\nTrue ATT (days) — these should be recovered by Module 05:")
    for (p, m), t in TRUE_TAU.items():
        print(f"  pipeline={p:10s}  metric={m}  tau={t:+.2f}")


if __name__ == "__main__":
    main()

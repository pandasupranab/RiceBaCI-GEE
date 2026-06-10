#!/usr/bin/env python3
"""
RiceBaCI v2.0 — Build the district-year panel from cell-level Stage B fits.

INPUT : analysis/v22/fits/<DCODE>_fits.parquet      (8 files)
OUTPUT: analysis/baci_panel_real_v22.csv            (consumed by Modules 05/06/09)
        analysis/v22/panel/qc_v22.csv               (Gate-A acceptance summary)

DESIGN — REFRAME 2019–2024 (decided 11 Jun 2026 after Gate A v2.2 diag)
======================================================================
The v2.0 panel covers **2019–2024 only** (6 years × 8 districts = 48 rows).

Rationale for dropping 2017–2018:
  1. RICE_MASK uses ESA WorldCover v200 (2021 epoch). Applied uniformly
     to 2017–2024, this overstates rice extent in 2017–2018 because
     several flagged cells were fallow / non-rice in those years
     (cropping pattern drift). Stage B fits on those cells produce
     SOS pinned at the window edge (DOY ~122, May 2) with POS in
     late July — a non-kharif phenology that Stage B's QC correctly
     rejects (qc_sos_outside_kharif).
  2. Sentinel-2 coverage over India in 2017 is S2A-only (10-day
     nominal revisit, often >20 d after cloud filtering). The 5-day
     S2A+S2B revisit only stabilised mid-2018. Cell-level dekadal
     composites in 2017–2018 have too many NaN dekads for reliable
     Beck fitting.
  3. Empirical result of the first v2.2 run: 0–14 ok cells per
     district-year in 2017–2018, vs 5–222 in 2019–2024.

Identification (without 2017–2018 pre-trends):
  • Treatment = 5 coastal districts (BLS, BHA, KDP, JGS, PUR)
  • Controls  = 3 inland   districts (ANG, DHK, CTK)
  • Event-time k = year − 2019 (Fani is the first observable shock to
    all 5 coastal districts simultaneously, k=0 in 2019).
  • TWFE absorbs district + year FEs; identification rests on inland
    controls absorbing year-specific shocks while coastal districts
    carry the cyclone exposure.
  • Recovery dynamics readable from k = 1..5 (2020 Amphan, 2021 Yaas,
    2022, 2023, 2024). No pre-treatment parallel-trends test (k<0
    not observable) — see Methods rewrite.

For each (district, year):
    - median SOS, POS, EOS over fit_ok cells
    - p25/p75 over cells (NOT per-cell bootstrap CIs)
    - n_cells, n_ok_cells, fit_fail_rate
    - treatment indicator
    - cyclone-year event flag (Fani 2019 / Amphan 2020 / Yaas 2021)
    - event_time k = year − 2019 (treatment districts only)

Gate A acceptance criteria (all must pass) — UPDATED FOR 6-YEAR PANEL:
    - All 48 district-year cells present (no missing)
    - Every district-year retains >= 5 valid cells (n_ok >= 5)
    - >=20 unique POS DOY across 48 rows (was 30 for 8 yr panel)
    - >=25 unique EOS DOY across 48 rows (was 30 for 8 yr panel)
    - POS / EOS mode share <= 20% (tightened from 40% — the
      extended-window fix should give us this slack)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
FITS_DIR = ROOT / "analysis" / "v22" / "fits"
PANEL_DIR = ROOT / "analysis" / "v22" / "panel"
PANEL_DIR.mkdir(parents=True, exist_ok=True)
OUT_PANEL = ROOT / "analysis" / "baci_panel_real_v22.csv"
QC_PATH = PANEL_DIR / "qc_v22.csv"

# Panel window (inclusive)
PANEL_YEARS = list(range(2019, 2025))   # 2019..2024
N_DISTRICTS = 8
N_PANEL_ROWS = len(PANEL_YEARS) * N_DISTRICTS   # 48

# Cyclone-year mapping (treatment districts only)
CYCLONE_BY_YEAR = {2019: "Fani", 2020: "Amphan", 2021: "Yaas"}

# Event-time anchor: first observable shock (Fani 2019)
EVENT_ANCHOR_YEAR = 2019


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    """Per district-year aggregation, restricted to PANEL_YEARS."""
    df = df[df["year"].isin(PANEL_YEARS)].copy()
    rows = []
    for (district, dcode, year, treat), grp in df.groupby(
            ["district", "district_code", "year", "treatment"]):
        ok = grp[grp["fit_ok"]].copy()
        n_cells = len(grp)
        n_ok = len(ok)
        row = {
            "district": district,
            "district_code": dcode,
            "year": int(year),
            "treatment": int(treat),
            "n_cells": int(n_cells),
            "n_ok": int(n_ok),
            "fit_fail_rate": round(1 - n_ok / max(n_cells, 1), 4),
        }
        for col in ("sos", "pos", "eos"):
            if n_ok > 0:
                row[f"{col}_median"] = float(ok[col].median())
                row[f"{col}_p25"]    = float(ok[col].quantile(0.25))
                row[f"{col}_p75"]    = float(ok[col].quantile(0.75))
                row[f"{col}_mean"]   = float(ok[col].mean())
                row[f"{col}_std"]    = float(ok[col].std(ddof=1)) if n_ok > 1 else np.nan
            else:
                for stat in ("median", "p25", "p75", "mean", "std"):
                    row[f"{col}_{stat}"] = np.nan
        # Cyclone exposure tags
        cyc = CYCLONE_BY_YEAR.get(int(year), "none")
        row["cyclone_year_event"] = cyc if treat == 1 else "none"
        row["cyclone_exposure"]   = int(cyc != "none" and treat == 1)
        # Event-time (treatment districts only; controls get NaN to
        # absorb only year FEs in the event-study)
        row["event_time"] = (int(year) - EVENT_ANCHOR_YEAR) if treat == 1 else np.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["district", "year"]).reset_index(drop=True)


def gate_a_check(panel: pd.DataFrame) -> dict:
    """Acceptance verdict for the 6-year (2019–2024) panel."""
    unique_pos = int(panel["pos_median"].round(0).nunique(dropna=True))
    unique_eos = int(panel["eos_median"].round(0).nunique(dropna=True))
    unique_sos = int(panel["sos_median"].round(0).nunique(dropna=True))
    mean_fail  = float(panel["fit_fail_rate"].mean())
    pos_mode_share = float(panel["pos_median"].round(0).value_counts(normalize=True).iloc[0]) \
        if panel["pos_median"].notna().any() else 1.0
    eos_mode_share = float(panel["eos_median"].round(0).value_counts(normalize=True).iloc[0]) \
        if panel["eos_median"].notna().any() else 1.0

    n_rows = len(panel)
    min_n_ok = int(panel["n_ok"].min()) if len(panel) else 0

    checks = {
        "n_rows": n_rows,
        "min_n_ok_per_dy": min_n_ok,
        "unique_sos": unique_sos,
        "unique_pos": unique_pos,
        "unique_eos": unique_eos,
        "mean_fit_fail_rate": round(mean_fail, 4),
        "pos_mode_share": round(pos_mode_share, 4),
        "eos_mode_share": round(eos_mode_share, 4),
        "pass_panel_complete": n_rows == N_PANEL_ROWS,
        "pass_min_n_ok":       min_n_ok >= 5,
        "pass_unique_pos":     unique_pos >= 20,
        "pass_unique_eos":     unique_eos >= 25,
        "pass_pos_mode":       pos_mode_share <= 0.20,
        "pass_eos_mode":       eos_mode_share <= 0.20,
    }
    checks["GATE_A_PASS"] = all(v for k, v in checks.items() if k.startswith("pass_"))
    return checks


def main():
    parquets = sorted(FITS_DIR.glob("*_fits.parquet"))
    if not parquets:
        print(f"[FATAL] No fit parquets in {FITS_DIR}. "
              "Run stage_b_whittaker_beck.py first.")
        sys.exit(2)

    all_cells = pd.concat([pd.read_parquet(p) for p in parquets], ignore_index=True)
    print(f"[panel] Loaded {len(all_cells):,} cell-year rows "
          f"from {len(parquets)} districts (all years).")

    panel = aggregate(all_cells)
    panel.to_csv(OUT_PANEL, index=False)
    print(f"[panel] Wrote {len(panel)} district-year rows "
          f"({PANEL_YEARS[0]}–{PANEL_YEARS[-1]}) -> {OUT_PANEL.relative_to(ROOT)}")

    gate = gate_a_check(panel)
    pd.DataFrame([gate]).to_csv(QC_PATH, index=False)
    print(f"[panel] QC: {json.dumps(gate, indent=2)}")
    if gate["GATE_A_PASS"]:
        print("[panel] GATE A: PASS — proceed to Phase 3 (DiD re-estimation).")
    else:
        print("[panel] GATE A: FAIL — diagnose before Phase 3.")
        failed = [k for k, v in gate.items()
                  if k.startswith("pass_") and not v]
        print(f"[panel]  Failed checks: {failed}")


if __name__ == "__main__":
    main()

# RiceBaCI v2.0 — analysis/v22

Refit pipeline that replaces Module 04 (phenology extraction).

## Why this exists

`gee/04_phenology_extract.js` (v1.0.2) computed monthly NDVI means and applied
a 0.4 threshold — not the Whittaker + Beck double-logistic method the
manuscript describes. This directory holds the v2.0 refit that matches the
manuscript text.

## Pipeline

```
Stage A — GEE  (gee/04_v2_dekadal_export.js)
   |
   |  exports 8 CSVs, one per district, each holding
   |  per-cell (10 km grid) dekadal NDVI + VH + VV + CR + n_pixels
   |  for years 2017–2024
   |
   v
analysis/v22/raw_dekadal/<DISTRICT>_dekadal.csv

Stage B — Python
   |
   |  python -m analysis.v22.stage_b_whittaker_beck
   |    1. Whittaker smoother (Eilers 2003), λ per cell via GCV
   |    2. Beck et al. (2006) double-logistic fit
   |       (scipy.optimize.curve_fit, bounded parameters)
   |    3. Half-amplitude SOS / EOS extraction; POS = curve maximum
   |    4. 1000-iter bootstrap on dekadal composites
   |    5. Fit-failed cells DROPPED (not snapped)
   |
   v
analysis/v22/fits/<DISTRICT>_<YEAR>_fits.parquet
analysis/v22/smoothed/<DISTRICT>_<YEAR>_smoothed.parquet

Stage C — Panel build
   |
   |  python -m analysis.v22.build_v22_panel
   |  Aggregates per-cell SOS/EOS/POS to district-year medians
   |  with bootstrap p25/p75 and CR1 SE inputs.
   |
   v
analysis/baci_panel_real_v22.csv      <- consumed by Modules 05/05a/05d/05e/06/09
```

## Folders

| Path                            | Contents                                              |
|---------------------------------|-------------------------------------------------------|
| `analysis/v22/raw_dekadal/`     | Stage A outputs (CSV from Drive)                       |
| `analysis/v22/smoothed/`        | Stage B Whittaker outputs (parquet, one per district-year) |
| `analysis/v22/fits/`            | Stage B fit parameters + SOS/EOS/POS per cell          |
| `analysis/v22/panel/`           | Intermediate panel artefacts; final → `analysis/baci_panel_real_v22.csv` |
| `analysis/v22/logs/`            | Per-run stdout/stderr + GCV diagnostic plots           |

## Acceptance gate (Gate A — end of Phase 2)

The new panel must satisfy:

- ≥30 unique POS values across the 64 district-year cells
- ≥30 unique EOS values across the 64 district-year cells
- ≤5% fit-failure rate per district
- No DOY snapping artefacts (raw_eos histogram does not concentrate at 349/350)

If any of these fail, Phase 2 is not done and we diagnose before moving to
Phase 3.

## OSF pre-registration

This implementation aligns with OSF c4mp8 §3.4. The earlier monthly-threshold
implementation will be disclosed as a deviation in the Phase 5 amendment.

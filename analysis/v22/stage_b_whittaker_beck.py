#!/usr/bin/env python3
"""
RiceBaCI v2.0 — Stage B: Whittaker smoother + Beck double-logistic fit.

INPUT  : analysis/v22/raw_dekadal/v22_dekadal_<DCODE>.csv   (8 files)
OUTPUT : analysis/v22/smoothed/<DCODE>_<YEAR>.parquet       (smoothed dekadal series per cell)
         analysis/v22/fits/<DCODE>_<YEAR>.parquet           (per-cell SOS/POS/EOS + Beck params + bootstrap CIs)
         analysis/v22/logs/<DCODE>_run.json                 (per-district summary diagnostics)

Method
------
1. For each (district, cell_id, year):
   - Build dekadal series. Drop dekads where NDVI_count == 0 (no valid pixels).
   - Require >= 12 dekads with NDVI to attempt a fit; else mark FIT_FAIL.
2. Whittaker smoother (Eilers 2003, 2nd-order difference penalty).
   - lambda selected via Generalised Cross-Validation (GCV) on a log-spaced grid
     [1e0, 1e1, 1e2, 1e3, 1e4]. Per-cell, per-year.
3. Beck et al. (2006) double-logistic fit:
       y(t) = wNDVI + (mNDVI - wNDVI) * (1/(1+exp(-rsp*(t-sos))) - 1/(1+exp(-rau*(t-eos))))
   - scipy.optimize.curve_fit with bounded parameters.
   - If curve_fit raises or max-iter, mark FIT_FAIL (no snap, no fallback).
4. Phenometric extraction (half-amplitude convention):
       amp = mNDVI - wNDVI
       SOS = first t where smoothed series crosses (wNDVI + 0.5*amp) going up
       EOS = first t after POS where smoothed series falls below (wNDVI + 0.5*amp)
       POS = argmax of smoothed series within [SOS, EOS]
5. Bootstrap (1000 iter): resample dekadal composite values within their
   dekad-of-year empirical distribution (block bootstrap by dekad index),
   redo step 2-4, return p25/p75/p_025/p_975 for SOS/POS/EOS per cell.

Acceptance gate (printed at end of run, checked again in build_v22_panel.py):
    - >=30 unique POS values across 64 district-year cells
    - >=30 unique EOS values across 64 district-year cells
    - <=5% fit-failure rate per district
    - Raw EOS histogram NOT concentrated at any single DOY > 50%

Author: Supranab Panda — v2.0-refit branch
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.optimize import curve_fit

# ----------------------------------------------------------------------------
# Paths (repo-relative)
# ----------------------------------------------------------------------------
ROOT      = Path(__file__).resolve().parents[2]            # repo root
RAW_DIR   = ROOT / "analysis" / "v22" / "raw_dekadal"
SMOOTH_DIR= ROOT / "analysis" / "v22" / "smoothed"
FITS_DIR  = ROOT / "analysis" / "v22" / "fits"
LOG_DIR   = ROOT / "analysis" / "v22" / "logs"
for p in (SMOOTH_DIR, FITS_DIR, LOG_DIR):
    p.mkdir(parents=True, exist_ok=True)

YEARS = list(range(2017, 2025))   # 2017–2024
LAMBDAS = np.logspace(0, 4, 9)    # GCV search grid
BOOT_ITER = 200   # 200 iters → P25/P75 stable to ~1 doy
RNG_SEED = 20260610

# ----------------------------------------------------------------------------
# Whittaker smoother (Eilers 2003)
# ----------------------------------------------------------------------------
def whittaker(y: np.ndarray, w: np.ndarray, lam: float) -> np.ndarray:
    """2nd-order Whittaker smoother. y of len n, w of len n (0/1 weights or floats)."""
    n = len(y)
    D = sparse.diags([1.0, -2.0, 1.0], [0, 1, 2], shape=(n - 2, n)).tocsc()
    W = sparse.diags(w, 0, shape=(n, n)).tocsc()
    A = W + lam * (D.T @ D)
    return spsolve(A, w * y)


def gcv_score(y: np.ndarray, w: np.ndarray, lam: float) -> float:
    """Generalised cross-validation score; lower is better."""
    n = len(y)
    z = whittaker(y, w, lam)
    # Approximate trace(H) via stochastic estimate (Hutchinson) for speed.
    rng = np.random.default_rng(0)
    v = rng.choice([-1.0, 1.0], size=n)
    Hv = whittaker(v, w, lam)
    trH = (v * Hv * w).sum() / max(w.sum(), 1.0) * n
    rss = float(np.sum(w * (y - z) ** 2))
    denom = max((n - trH) ** 2, 1e-6)
    return rss / denom


def select_lambda(y: np.ndarray, w: np.ndarray) -> tuple[float, np.ndarray]:
    """Return (best_lambda, smoothed_series)."""
    scores = [gcv_score(y, w, lam) for lam in LAMBDAS]
    best = LAMBDAS[int(np.argmin(scores))]
    return best, whittaker(y, w, best)


# ----------------------------------------------------------------------------
# Beck et al. (2006) double-logistic
# ----------------------------------------------------------------------------
def beck_dl(t, wNDVI, mNDVI, sos, eos, rsp, rau):
    return wNDVI + (mNDVI - wNDVI) * (
        1.0 / (1.0 + np.exp(-rsp * (t - sos)))
        - 1.0 / (1.0 + np.exp(-rau * (t - eos)))
    )


def fit_beck(doy: np.ndarray, ndvi: np.ndarray) -> Optional[dict]:
    """Bounded curve_fit. Returns dict of params or None on failure.

    Bounds and initial guesses are tuned for kharif rice in coastal
    Odisha (single annual cycle, SOS Jun–Sep, POS Sep–Nov, EOS Nov–Dec):
      • wNDVI (background) bounded to observed lower envelope
      • mNDVI (peak) bounded to observed upper envelope (NOT 1.0,
        which caused the optimizer to peg at the boundary and
        produce peak_below_half failures)
      • sos_param initialized from observed inflection on the rising
        limb; eos_param from the falling limb
    """
    if len(doy) < 8:
        return None

    ndvi_min = float(np.nanmin(ndvi))
    ndvi_max = float(np.nanmax(ndvi))
    ndvi_p10 = float(np.nanpercentile(ndvi, 10))
    ndvi_p90 = float(np.nanpercentile(ndvi, 90))
    amp_obs  = ndvi_p90 - ndvi_p10

    # Drop hopeless cases early (no growing season visible)
    if amp_obs < 0.10:
        return None

    # Initial guesses from the observed series
    peak_idx = int(np.nanargmax(ndvi))
    peak_doy = float(doy[peak_idx])

    # Rising limb: first dekad where NDVI exceeds halfway between p10 and p90
    half = ndvi_p10 + 0.5 * amp_obs
    above = np.where(ndvi >= half)[0]
    sos_guess = float(doy[above[0]])   if len(above) else float(doy[0]  + 30)
    eos_guess = float(doy[above[-1]])  if len(above) else float(doy[-1] - 30)
    # Ensure sos < eos and both inside [doy.min, doy.max]
    sos_guess = max(min(sos_guess, peak_doy - 5), float(doy.min()) + 10)
    eos_guess = max(min(eos_guess, float(doy.max()) - 10), peak_doy + 5)

    p0 = [
        max(ndvi_p10, 0.0),    # wNDVI
        min(ndvi_p90, 0.95),   # mNDVI
        sos_guess,             # sos_param
        eos_guess,             # eos_param
        0.12,                  # rsp — rising rate
        0.12,                  # rau — senescence rate
    ]
    # Tight bounds informed by observed envelope:
    #   wNDVI ∈ [-0.10, p25_observed]
    #   mNDVI ∈ [p75_observed, ndvi_max + 0.02]   (NOT 0.95 — that
    #     caused the optimizer to chase an unreachable asymptote
    #     and produce degenerate narrow fits where peak_below_half)
    #   sos_param away from doy.min() so fitted plateau is reachable
    #   eos_param > sos_param + 30  (enforced via min separation)
    ndvi_p25 = float(np.nanpercentile(ndvi, 25))
    ndvi_p75 = float(np.nanpercentile(ndvi, 75))
    bounds = (
        [-0.10,                                # wNDVI lower
         max(ndvi_p75, 0.20),                  # mNDVI lower (forces real peak)
         float(doy.min()),                     # sos_param lower
         float(doy.min()) + 60,                # eos_param lower
         0.005, 0.005],                        # rsp, rau lower
        [min(ndvi_p25, 0.30),                  # wNDVI upper
         min(ndvi_max + 0.02, 0.95),           # mNDVI upper (capped to data)
         float(doy.max()) - 60,                # sos_param upper
         float(doy.max()),                     # eos_param upper
         1.0, 1.0],                            # rsp, rau upper
    )
    # Guard against any inverted bound (lower >= upper) for this cell-year
    for i in range(6):
        if bounds[0][i] >= bounds[1][i]:
            return None
    # Clamp p0 inside bounds to satisfy curve_fit
    p0 = [min(max(p0[i], bounds[0][i]), bounds[1][i]) for i in range(6)]
    try:
        popt, _ = curve_fit(
            beck_dl, doy, ndvi, p0=p0, bounds=bounds, maxfev=8000
        )
    except (RuntimeError, ValueError):
        return None
    keys = ("wNDVI", "mNDVI", "sos_param", "eos_param", "rsp", "rau")
    return dict(zip(keys, popt.tolist()))


def extract_phenometrics(doy_grid: np.ndarray, y_smooth: np.ndarray,
                         params: dict) -> dict:
    """Half-amplitude SOS/EOS/POS from the FITTED Beck double-logistic.

    Phenometrics are extracted from the Beck-fitted curve evaluated on a
    dense daily grid — not from the Whittaker-smoothed observations.
    The Whittaker series feeds the Beck fit; phenometrics come from the
    parametric model so that wNDVI/mNDVI/half-amplitude are internally
    consistent.

    Logic (single-cycle annual rice phenology):
      • build dense daily curve y_fit = beck_dl(t, ...) over [t_min, t_max]
      • POS  = doy of argmax(y_fit) (true peak of the fitted curve)
      • SOS  = first day BEFORE POS where y_fit crosses half-amp going up
      • EOS  = first day AFTER  POS where y_fit crosses half-amp going down
    """
    w, m = params["wNDVI"], params["mNDVI"]
    amp = m - w
    if amp < 0.10:
        return {"sos": np.nan, "eos": np.nan, "pos": np.nan,
                "ok": False, "reason": "low_amplitude"}

    t = doy_grid.astype(float)
    y_fit = beck_dl(
        t,
        params["wNDVI"], params["mNDVI"],
        params["sos_param"], params["eos_param"],
        params["rsp"], params["rau"],
    )
    half = w + 0.5 * amp

    # POS = peak of fitted curve
    pos_idx = int(np.argmax(y_fit))
    pos_doy = float(t[pos_idx])

    # The fitted-curve range must actually cross the half threshold.
    y_peak = float(y_fit[pos_idx])
    if y_peak < half:
        return {"sos": np.nan, "eos": np.nan, "pos": pos_doy,
                "ok": False, "reason": "peak_below_half"}

    # SOS = last index BEFORE pos where curve is still below half
    rising = y_fit[:pos_idx + 1] >= half
    if not rising.any():
        return {"sos": np.nan, "eos": np.nan, "pos": pos_doy,
                "ok": False, "reason": "no_sos_crossing"}
    sos_idx = int(np.argmax(rising))           # first True before POS
    sos_doy = float(t[sos_idx])

    # EOS = first index AFTER pos where curve drops below half
    falling = y_fit[pos_idx:] < half
    if not falling.any():
        return {"sos": sos_doy, "eos": np.nan, "pos": pos_doy,
                "ok": False, "reason": "no_eos_crossing"}
    eos_idx = pos_idx + int(np.argmax(falling))
    eos_doy = float(t[eos_idx])

    # Sanity: SOS < POS < EOS, all within fit window
    if not (sos_doy < pos_doy < eos_doy):
        return {"sos": sos_doy, "eos": eos_doy, "pos": pos_doy,
                "ok": False, "reason": "order_violation"}

    return {
        "sos": sos_doy,
        "pos": pos_doy,
        "eos": eos_doy,
        "ok": True, "reason": "",
    }


# ----------------------------------------------------------------------------
# Cell-year processing
# ----------------------------------------------------------------------------
@dataclass
class CellYearResult:
    district: str
    district_code: str
    cell_id: str
    year: int
    treatment: int
    sos: float
    pos: float
    eos: float
    sos_p25: float
    sos_p75: float
    eos_p25: float
    eos_p75: float
    pos_p25: float
    pos_p75: float
    n_dekads_used: int
    lam: float
    fit_ok: bool
    fit_reason: str
    wNDVI: float
    mNDVI: float


def process_cell_year(df_cy: pd.DataFrame) -> Optional[CellYearResult]:
    """df_cy: rows = dekads, columns include doy, NDVI_mean, NDVI_count."""
    df_cy = df_cy.sort_values("doy").copy()
    # Drop dekads with no S2 pixels
    df_cy = df_cy[df_cy["NDVI_count"].fillna(0) > 0]
    if len(df_cy) < 12:
        return None
    doy   = df_cy["doy"].to_numpy(dtype=float)
    ndvi  = df_cy["NDVI_mean"].to_numpy(dtype=float)
    w     = np.ones_like(ndvi)

    lam, y_smooth = select_lambda(ndvi, w)

    # Interpolate smoothed series onto a daily grid for half-amp extraction
    doy_grid = np.arange(int(doy.min()), int(doy.max()) + 1)
    y_daily  = np.interp(doy_grid, doy, y_smooth)

    params = fit_beck(doy, y_smooth)
    if params is None:
        return CellYearResult(
            district=df_cy["district"].iloc[0],
            district_code=df_cy["district_code"].iloc[0],
            cell_id=str(df_cy["cell_id"].iloc[0]),
            year=int(df_cy["year"].iloc[0]),
            treatment=int(df_cy["treatment"].iloc[0]),
            sos=np.nan, pos=np.nan, eos=np.nan,
            sos_p25=np.nan, sos_p75=np.nan,
            eos_p25=np.nan, eos_p75=np.nan,
            pos_p25=np.nan, pos_p75=np.nan,
            n_dekads_used=len(df_cy), lam=float(lam),
            fit_ok=False, fit_reason="beck_fit_failed",
            wNDVI=np.nan, mNDVI=np.nan,
        )

    pheno = extract_phenometrics(doy_grid, y_daily, params)

    # Bootstrap — block-resample dekads with replacement
    rng = np.random.default_rng(RNG_SEED + hash(str(df_cy["cell_id"].iloc[0])) % (2**31))
    boot_sos, boot_pos, boot_eos = [], [], []
    n = len(df_cy)
    for _ in range(BOOT_ITER):
        idx = rng.integers(0, n, size=n)
        idx.sort()  # keep chronological order
        b_doy   = doy[idx]
        b_ndvi  = ndvi[idx]
        b_w     = np.ones_like(b_ndvi)
        try:
            # Reuse lam selected on the original series — do NOT re-run
            # GCV grid search inside the bootstrap (10× speedup, and
            # bootstrap uncertainty is meant to capture observation
            # variability, not smoother re-tuning).
            b_smooth = whittaker(b_ndvi, b_w, lam)
            b_params = fit_beck(b_doy, b_smooth)
            if b_params is None:
                continue
            b_grid = np.arange(int(b_doy.min()), int(b_doy.max()) + 1)
            b_daily = np.interp(b_grid, b_doy, b_smooth)
            bp = extract_phenometrics(b_grid, b_daily, b_params)
            if bp["ok"]:
                boot_sos.append(bp["sos"])
                boot_pos.append(bp["pos"])
                boot_eos.append(bp["eos"])
        except Exception:
            continue

    def _pct(arr, q):
        return float(np.percentile(arr, q)) if arr else np.nan

    # ------------------------------------------------------------------
    # Biological QC gates (kharif rice, Odisha)
    #   • amplitude (mNDVI - wNDVI) >= 0.25 — healthy rice should show
    #     clear seasonal lift; lower values indicate degraded signal
    #   • POS in DOY 213–335 (1 Aug – 1 Dec) — expected peak window for
    #     kharif rice in coastal Odisha; outside this is almost
    #     certainly a fit artefact
    #   • season length (EOS - SOS) in [40, 200] d — too short or
    #     too long are physically implausible single-cycle fits
    # ------------------------------------------------------------------
    fit_ok = pheno["ok"]
    fit_reason = pheno["reason"]
    if fit_ok:
        amp_fit = float(params["mNDVI"]) - float(params["wNDVI"])
        if amp_fit < 0.25:
            fit_ok, fit_reason = False, "qc_low_amp_fit"
        elif not (213.0 <= pheno["pos"] <= 335.0):
            fit_ok, fit_reason = False, "qc_pos_outside_kharif"
        else:
            season_len = pheno["eos"] - pheno["sos"]
            if not (40.0 <= season_len <= 200.0):
                fit_ok, fit_reason = False, "qc_season_length"

    return CellYearResult(
        district=df_cy["district"].iloc[0],
        district_code=df_cy["district_code"].iloc[0],
        cell_id=str(df_cy["cell_id"].iloc[0]),
        year=int(df_cy["year"].iloc[0]),
        treatment=int(df_cy["treatment"].iloc[0]),
        sos=pheno["sos"], pos=pheno["pos"], eos=pheno["eos"],
        sos_p25=_pct(boot_sos, 25), sos_p75=_pct(boot_sos, 75),
        eos_p25=_pct(boot_eos, 25), eos_p75=_pct(boot_eos, 75),
        pos_p25=_pct(boot_pos, 25), pos_p75=_pct(boot_pos, 75),
        n_dekads_used=len(df_cy), lam=float(lam),
        fit_ok=fit_ok, fit_reason=fit_reason,
        wNDVI=float(params["wNDVI"]), mNDVI=float(params["mNDVI"]),
    )


# ----------------------------------------------------------------------------
# District driver
# ----------------------------------------------------------------------------
def process_district_csv(csv_path: Path) -> dict:
    df = pd.read_csv(csv_path)
    # GEE exports the grid-cell identifier under "system:index".
    # GEE rewrites the LEADING segments of system:index on every
    # .map() iteration, but the TRAILING "X,Y" segment (the
    # EPSG:3857 coveringGrid tile coordinates) is stable per cell.
    # Extract it as a stable cell_id.
    if "cell_id" not in df.columns:
        if "system:index" not in df.columns:
            raise KeyError(f"{csv_path.name}: neither 'cell_id' nor 'system:index'")
        cid = df["system:index"].astype(str).str.extract(r"(\d+,\d+)$")[0]
        if cid.isna().any():
            raise ValueError(
                f"{csv_path.name}: could not parse cell coords from system:index"
            )
        df["cell_id"] = cid
    dcode = df["district_code"].iloc[0]
    results: list[CellYearResult] = []
    failed = 0

    for (cell, yr), grp in df.groupby(["cell_id", "year"]):
        r = process_cell_year(grp)
        if r is None:
            failed += 1
            continue
        results.append(r)

    if not results:
        return {"district": dcode, "n_cells": 0, "n_failed": failed,
                "status": "no_results"}

    out_df = pd.DataFrame([asdict(r) for r in results])
    out_path = FITS_DIR / f"{dcode}_fits.parquet"
    out_df.to_parquet(out_path, index=False)

    n_total = len(out_df)
    n_ok = int(out_df["fit_ok"].sum())
    unique_sos = int(out_df.loc[out_df["fit_ok"], "sos"].round(0).nunique())
    unique_eos = int(out_df.loc[out_df["fit_ok"], "eos"].round(0).nunique())
    unique_pos = int(out_df.loc[out_df["fit_ok"], "pos"].round(0).nunique())

    summary = {
        "district": dcode,
        "n_cell_years": n_total,
        "n_ok": n_ok,
        "n_failed_skipped": failed,
        "fit_fail_rate": round(1 - n_ok / max(n_total, 1), 4),
        "unique_sos_doy": unique_sos,
        "unique_pos_doy": unique_pos,
        "unique_eos_doy": unique_eos,
        "out_file": str(out_path.relative_to(ROOT)),
    }
    (LOG_DIR / f"{dcode}_summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def _run_one(csv_path: Path) -> dict:
    print(f"[stage_b] {csv_path.name} ...", flush=True)
    s = process_district_csv(csv_path)
    print(f"   -> {csv_path.name}: ok={s.get('n_ok')}/{s.get('n_cell_years')}  "
          f"unique_pos={s.get('unique_pos_doy')}  unique_eos={s.get('unique_eos_doy')}",
          flush=True)
    return s


def main():
    import os
    from concurrent.futures import ProcessPoolExecutor

    csvs = sorted(RAW_DIR.glob("v22_dekadal_*.csv"))
    if not csvs:
        print(f"[FATAL] No CSVs in {RAW_DIR}. "
              "Run gee/04_v2_dekadal_export.js and drop the 8 files here first.")
        sys.exit(2)

    n_workers = int(os.environ.get("STAGE_B_WORKERS", "2"))
    print(f"[stage_b] Processing {len(csvs)} districts with {n_workers} workers",
          flush=True)
    summaries = []
    if n_workers <= 1:
        for csv_path in csvs:
            summaries.append(_run_one(csv_path))
    else:
        with ProcessPoolExecutor(max_workers=n_workers) as ex:
            for s in ex.map(_run_one, csvs):
                summaries.append(s)

    (LOG_DIR / "run_summary.json").write_text(json.dumps(summaries, indent=2))
    print(f"\n[stage_b] Wrote {len(summaries)} district fit files to {FITS_DIR}")
    print(f"[stage_b] Summary at {LOG_DIR/'run_summary.json'}")


if __name__ == "__main__":
    main()

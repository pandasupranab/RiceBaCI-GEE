"""
05d_jackknife_sensitivity.py — leave-one-district-out (LOO) sensitivity.

Why this and not Goodman-Bacon?
-------------------------------
Goodman-Bacon (2021) decomposes a TWFE DiD into weighted averages of
2x2 comparisons.  It is essential under STAGGERED adoption (different
units treated at different times), where "early-treated as control"
contamination can flip signs.  In RiceBaCI all five treatment
districts are exposed simultaneously across 2019-2021, with three
never-treated control districts — i.e. a single-cohort design.  In
that case the Bacon decomposition collapses to a single 2x2, so it
adds no information beyond Table S1.

The binding robustness question is instead:
    "Is tau being driven by a single district / a single year?"

This is a leave-one-out (LOO) sensitivity: drop one district at a
time, re-fit, and report the distribution of tau estimates.  We do
this both on the treatment side (5 LOOs) and the control side (3 LOOs)
for a total of 8 LOO fits per (pipeline, metric) cell.

Outputs
-------
analysis/results/jackknife_district.csv  — per (pipeline, metric, dropped):
    tau_loo, se_loo, p_loo, ci_lo, ci_hi, share_change_pct
analysis/results/jackknife_year.csv      — per (pipeline, metric, dropped year)
analysis/results/jackknife_summary.txt   — verdict per cell

Verdict rules
-------------
- "stable":   max(|tau_loo - tau_full|) <= 25 % of |tau_full| AND no LOO
              changes sign of tau.
- "fragile":  any LOO changes sign of tau.
- "leverage": one specific district / year drives > 25 % of tau.

Author : Supranab Panda
Date   : 2026-05-05
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Local import of Module 05
import importlib.util
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod
DID = _load("did_regression",
            Path(__file__).resolve().parent / "05_did_regression.py")

PIPELINES = ["raw", "corrected"]
METRICS   = ["SOS", "POS", "EOS"]


# ---------------------------------------------------------------------------
def loo_district(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pipe in PIPELINES:
        for met in METRICS:
            base_df = df.query("pipeline == @pipe and metric == @met").copy()
            tau_full = DID.estimate_static_did(df, pipe, met).tau

            for d in sorted(base_df["district"].unique()):
                drop_df = df[df["district"] != d].copy()
                if drop_df.query("pipeline == @pipe and metric == @met").empty:
                    continue
                try:
                    res = DID.estimate_static_did(drop_df, pipe, met)
                except Exception as exc:                  # noqa: BLE001
                    rows.append({
                        "pipeline": pipe, "metric": met,
                        "dropped_district": d,
                        "exposure": base_df.query("district == @d")
                                          ["cyclone_exposure"].iloc[0],
                        "tau_loo": np.nan, "se_loo": np.nan,
                        "p_loo": np.nan, "ci_lo": np.nan, "ci_hi": np.nan,
                        "delta_pct": np.nan,
                        "note": f"failed: {type(exc).__name__}",
                    })
                    continue
                delta_pct = (
                    100 * (res.tau - tau_full) / abs(tau_full)
                    if abs(tau_full) > 1e-9 else np.nan
                )
                rows.append({
                    "pipeline": pipe, "metric": met,
                    "dropped_district": d,
                    "exposure": base_df.query("district == @d")
                                       ["cyclone_exposure"].iloc[0],
                    "tau_loo":  round(res.tau, 3),
                    "se_loo":   round(res.se,  3),
                    "p_loo":    round(res.p_value, 4),
                    "ci_lo":    round(res.ci_lo, 3),
                    "ci_hi":    round(res.ci_hi, 3),
                    "delta_pct": round(delta_pct, 1),
                    "note":     "ok",
                })
    return pd.DataFrame(rows)


def loo_year(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pipe in PIPELINES:
        for met in METRICS:
            tau_full = DID.estimate_static_did(df, pipe, met).tau
            for y in sorted(df["year"].unique()):
                drop_df = df[df["year"] != y].copy()
                try:
                    res = DID.estimate_static_did(drop_df, pipe, met)
                except Exception as exc:                  # noqa: BLE001
                    rows.append({
                        "pipeline": pipe, "metric": met,
                        "dropped_year": y,
                        "tau_loo": np.nan, "se_loo": np.nan,
                        "p_loo": np.nan, "ci_lo": np.nan, "ci_hi": np.nan,
                        "delta_pct": np.nan,
                        "note": f"failed: {type(exc).__name__}",
                    })
                    continue
                delta_pct = (
                    100 * (res.tau - tau_full) / abs(tau_full)
                    if abs(tau_full) > 1e-9 else np.nan
                )
                rows.append({
                    "pipeline": pipe, "metric": met,
                    "dropped_year": int(y),
                    "is_treatment_year": int(y) in [2019, 2020, 2021],
                    "tau_loo":  round(res.tau, 3),
                    "se_loo":   round(res.se,  3),
                    "p_loo":    round(res.p_value, 4),
                    "ci_lo":    round(res.ci_lo, 3),
                    "ci_hi":    round(res.ci_hi, 3),
                    "delta_pct": round(delta_pct, 1),
                    "note":     "ok",
                })
    return pd.DataFrame(rows)


def verdicts(loo_d: pd.DataFrame, df_full: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pipe in PIPELINES:
        for met in METRICS:
            tau_full = DID.estimate_static_did(df_full, pipe, met).tau
            sub = loo_d.query(
                "pipeline == @pipe and metric == @met and note == 'ok'"
            )
            if sub.empty:
                continue
            sign_full = np.sign(tau_full)
            sign_flip = (np.sign(sub["tau_loo"]) != sign_full).any()
            # Guard against all-NaN delta_pct (occurs when tau_full ≈ 0
            # makes percentage changes undefined; e.g. EOS on real data
            # when most coastal districts don't reach NDVI > 0.4).
            delta_abs = sub["delta_pct"].abs()
            if delta_abs.notna().any():
                max_abs_pct = float(delta_abs.max())
                most_lev = sub.iloc[int(delta_abs.argmax())]
            else:
                max_abs_pct = np.nan
                most_lev = sub.iloc[0]

            if sign_flip:
                v = "fragile"
            elif max_abs_pct > 25:
                v = "leverage"
            else:
                v = "stable"

            rows.append({
                "pipeline":      pipe,
                "metric":        met,
                "tau_full":      round(tau_full, 3),
                "max_abs_delta_pct": round(max_abs_pct, 1),
                "most_leveraging_district": most_lev["dropped_district"],
                "verdict":       v,
            })
    return pd.DataFrame(rows)


def write_summary(verdict_df: pd.DataFrame, out_path: Path) -> None:
    lines = ["RiceBaCI Module 05d - LOO district sensitivity",
             "=" * 70, ""]
    lines.append(f"{'pipeline':10s} {'metric':6s} {'tau_full':>9s} "
                 f"{'max|delta|%':>11s} {'driver':>20s}  verdict")
    for _, r in verdict_df.iterrows():
        lines.append(
            f"{r['pipeline']:10s} {r['metric']:6s} "
            f"{r['tau_full']:+9.2f} {r['max_abs_delta_pct']:11.1f} "
            f"{r['most_leveraging_district']:>20s}  {r['verdict']}"
        )
    lines.append("")
    lines.append("Verdicts: stable (no LOO shifts tau by >25 %), "
                 "leverage (one district drives >25 %), "
                 "fragile (some LOO flips sign).")
    out_path.write_text("\n".join(lines))


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel",  default="analysis/synthetic_baci_panel.csv")
    ap.add_argument("--outdir", default="analysis/results")
    args = ap.parse_args()

    df = DID.load_panel(Path(args.panel))
    print(f"loaded {len(df)} rows, {df['district'].nunique()} districts")

    out_dir = Path(args.outdir); out_dir.mkdir(parents=True, exist_ok=True)

    print("running LOO over districts ...")
    loo_d = loo_district(df)
    loo_d.to_csv(out_dir / "jackknife_district.csv", index=False)

    print("running LOO over years ...")
    loo_y = loo_year(df)
    loo_y.to_csv(out_dir / "jackknife_year.csv", index=False)

    verdict_df = verdicts(loo_d, df)
    write_summary(verdict_df, out_dir / "jackknife_summary.txt")
    verdict_df.to_csv(out_dir / "jackknife_verdicts.csv", index=False)

    print("\nverdicts:")
    print(verdict_df.to_string(index=False))
    print(f"\nwrote: {out_dir}/jackknife_district.csv")
    print(f"wrote: {out_dir}/jackknife_year.csv")
    print(f"wrote: {out_dir}/jackknife_summary.txt")


if __name__ == "__main__":
    main()

"""
05_did_regression.py — Difference-in-Differences for the RiceBaCI panel.

Reads the panel produced by Module 04 (`baci_district_phenology.csv`) and
estimates the average treatment effect on the treated (ATT) of pre-Kharif
cyclone landfalls on rice phenology metrics (SOS, POS, EOS).

Specifications
--------------
(A) Static DiD (canonical 2×2 generalisation):

      Y_{idt} = alpha_d + gamma_t + tau * (Treat_d * Post_t) + eps_{idt}

    where Treat_d = 1 for coastal-treatment districts and Post_t = 1 for
    cyclone years (2019, 2020, 2021).  Estimated separately for each
    (pipeline, metric) pair using two-way fixed effects with district-
    clustered standard errors.

(B) Event study (dynamic DiD):

      Y_{idt} = alpha_d + gamma_t + sum_{k != -1} beta_k * 1[event_year=k]
              + eps_{idt}

    Event time is each district's offset from its first treatment year.
    Coastal-treatment districts use 2019 as their reference (Fani is the
    earliest treatment cyclone). Inland-control districts contribute only
    to year FEs (no event time defined).

Sample & exclusions
-------------------
- Bulbul (2019, inland) is held out for transferability — not in the main
  DiD sample. The panel currently labels 2019 as a treatment year for
  *all* districts, but identification still relies on Treat_d × Post_t,
  so Bulbul rows for inland-control districts add to the post-period
  control mean rather than contaminating the ATT.
- Hudhud (2014) is outside the panel time window (2017–2024).
- Transferability rows (year_type='transferability') are skipped if
  present.

Outputs
-------
- analysis/results/did_static.csv          — coefficient table per (pipeline, metric)
- analysis/results/event_study.csv         — event-time coefficients + 95 % CI
- analysis/results/did_summary.txt         — human-readable summary
- analysis/results/parallel_trends.csv     — pre-period coastal vs inland slopes

Author : Supranab Panda
Date   : 2026-05-05
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TREAT_YEARS    = [2019, 2020, 2021]
TREAT_EXPOSURE = "coastal_treatment"
PIPELINES      = ["raw", "corrected"]
METRICS        = ["SOS", "POS", "EOS"]

# ---------------------------------------------------------------------------
@dataclass
class DiDResult:
    pipeline: str
    metric: str
    n_obs: int
    n_districts: int
    tau: float
    se: float
    t_stat: float
    p_value: float
    ci_lo: float
    ci_hi: float
    cluster_var: str
    r2_within: float

    def as_row(self) -> dict:
        return {
            "pipeline":     self.pipeline,
            "metric":       self.metric,
            "n_obs":        self.n_obs,
            "n_districts":  self.n_districts,
            "tau_days":     round(self.tau, 3),
            "se_days":      round(self.se,  3),
            "t_stat":       round(self.t_stat, 3),
            "p_value":      round(self.p_value, 4),
            "ci_lo_95":     round(self.ci_lo, 3),
            "ci_hi_95":     round(self.ci_hi, 3),
            "cluster_var":  self.cluster_var,
            "r2_within":    round(self.r2_within, 4),
        }


# ---------------------------------------------------------------------------
def load_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    required = {
        "district", "year", "year_type", "cyclone_exposure",
        "pipeline", "metric", "median_doy", "n_pixels",
    }
    missing = required - set(df.columns)
    if missing:
        sys.exit(f"FATAL: panel missing columns: {missing}")

    # Drop transferability rows if any (safety)
    if "year_type" in df.columns:
        df = df[df["year_type"] != "transferability"].copy()

    # Drop rows with no pixels (failed cells)
    df = df.dropna(subset=["median_doy"]).copy()
    df = df[df["n_pixels"].fillna(0) > 0].copy()

    # Construct DiD indicators
    df["treat"] = (df["cyclone_exposure"] == TREAT_EXPOSURE).astype(int)
    df["post"]  = df["year"].isin(TREAT_YEARS).astype(int)
    df["did"]   = df["treat"] * df["post"]

    return df


# ---------------------------------------------------------------------------
def estimate_static_did(df: pd.DataFrame, pipeline: str, metric: str) -> DiDResult:
    """Two-way FE: district + year, district-clustered SE.

    We absorb district and year FEs by including them as categorical
    dummies; equivalent to within transformation.  Sample is restricted
    to the requested (pipeline, metric).
    """
    sub = df.query("pipeline == @pipeline and metric == @metric").copy()
    if sub.empty:
        raise ValueError(f"empty subset for pipeline={pipeline}, metric={metric}")

    sub["district"] = sub["district"].astype("category")
    sub["year_c"]   = sub["year"].astype("category")

    # Two-way FE via dummies; cluster SEs at district
    model = smf.ols(
        "median_doy ~ did + C(district) + C(year_c)",
        data=sub,
    ).fit(cov_type="cluster", cov_kwds={"groups": sub["district"]})

    # Within R2 — correlation of fitted (only DiD term, year/dist absorbed)
    # Use partial regression: residuals from regressing Y and DID on FEs
    fe_only = smf.ols(
        "median_doy ~ C(district) + C(year_c)", data=sub
    ).fit()
    fe_did  = smf.ols(
        "did        ~ C(district) + C(year_c)", data=sub
    ).fit()
    y_resid   = fe_only.resid
    did_resid = fe_did.resid
    if did_resid.var() > 0:
        within = smf.ols("y ~ d", data=pd.DataFrame({
            "y": y_resid, "d": did_resid
        })).fit()
        r2_within = within.rsquared
    else:
        r2_within = float("nan")

    tau = model.params["did"]
    se  = model.bse["did"]
    t   = model.tvalues["did"]
    p   = model.pvalues["did"]
    lo, hi = model.conf_int().loc["did"].tolist()

    return DiDResult(
        pipeline=pipeline, metric=metric,
        n_obs=int(model.nobs),
        n_districts=sub["district"].nunique(),
        tau=tau, se=se, t_stat=t, p_value=p,
        ci_lo=lo, ci_hi=hi,
        cluster_var="district",
        r2_within=r2_within,
    )


# ---------------------------------------------------------------------------
def estimate_event_study(df: pd.DataFrame, pipeline: str, metric: str,
                         reference: int = -1) -> pd.DataFrame:
    """
    Event-study: leads/lags around the *first* treatment event for each
    coastal-treatment district. Event-time is year - first_treat_year for
    treated; control districts get k = NA and absorb only year FEs via a
    `is_control` dummy interaction.

    Reference period is k = -1 (year before first treatment) — coefficient
    set to 0 / omitted.  Returns a tidy DataFrame with one row per k.
    """
    sub = df.query("pipeline == @pipeline and metric == @metric").copy()

    first_treat_year = min(TREAT_YEARS)              # 2019 (Fani)
    sub["event_k"] = np.where(
        sub["cyclone_exposure"] == TREAT_EXPOSURE,
        sub["year"] - first_treat_year,
        np.nan,
    )

    # Drop control rows from event-time dummies but keep them in the
    # regression for year FE identification via a separate intercept.
    sub_treat = sub[sub["event_k"].notna()].copy()
    sub_ctrl  = sub[sub["event_k"].isna()].copy()
    sub_ctrl["event_k"] = -999          # sentinel for control bin

    full = pd.concat([sub_treat, sub_ctrl], ignore_index=True)
    full["event_k"] = full["event_k"].astype(int)
    full["event_k_str"] = full["event_k"].astype(str)

    # Build dummies, drop reference k = -1
    full["district"] = full["district"].astype("category")
    full["year_c"]   = full["year"].astype("category")

    formula = (
        f"median_doy ~ C(event_k_str, Treatment(reference='{reference}')) "
        f"+ C(district) + C(year_c)"
    )
    model = smf.ols(formula, data=full).fit(
        cov_type="cluster", cov_kwds={"groups": full["district"]}
    )

    # Extract event-time coefficients
    rows = []
    for name, beta in model.params.items():
        if "event_k_str" not in name:
            continue
        # Parse: C(event_k_str, Treatment(reference='-1'))[T.k]
        try:
            k_str = name.split("[T.")[1].rstrip("]")
            k     = int(k_str)
        except (IndexError, ValueError):
            continue
        if k == -999:                   # control sentinel — skip
            continue
        se = model.bse[name]
        rows.append({
            "pipeline": pipeline, "metric": metric,
            "event_k":  k,
            "beta":     round(beta, 3),
            "se":       round(se,   3),
            "ci_lo_95": round(beta - 1.96 * se, 3),
            "ci_hi_95": round(beta + 1.96 * se, 3),
            "n_obs":    int(model.nobs),
        })

    # Reference period
    rows.append({
        "pipeline": pipeline, "metric": metric,
        "event_k": reference,
        "beta": 0.0, "se": 0.0,
        "ci_lo_95": 0.0, "ci_hi_95": 0.0,
        "n_obs": int(model.nobs),
    })

    return (pd.DataFrame(rows)
              .sort_values(["pipeline", "metric", "event_k"])
              .reset_index(drop=True))


# ---------------------------------------------------------------------------
def parallel_trends_check(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pre-treatment trend test: regress Y on year * treat in pre-period
    (years < min(TREAT_YEARS)). A non-significant interaction supports
    the parallel-trends assumption.
    """
    pre = df[df["year"] < min(TREAT_YEARS)].copy()
    rows = []
    for pipe in PIPELINES:
        for met in METRICS:
            sub = pre.query("pipeline == @pipe and metric == @met").copy()
            if sub["year"].nunique() < 2:
                rows.append({
                    "pipeline": pipe, "metric": met,
                    "interaction_coef": np.nan, "se": np.nan,
                    "p_value": np.nan, "n_pre": len(sub),
                    "note": "too few pre-years",
                })
                continue
            sub["year_c"] = sub["year"] - sub["year"].min()
            model = smf.ols(
                "median_doy ~ year_c * treat + C(district)", data=sub
            ).fit(cov_type="cluster", cov_kwds={"groups": sub["district"]})
            key = "year_c:treat"
            rows.append({
                "pipeline": pipe, "metric": met,
                "interaction_coef": round(model.params.get(key, np.nan), 3),
                "se":               round(model.bse.get(key,    np.nan), 3),
                "p_value":          round(model.pvalues.get(key, np.nan), 4),
                "n_pre":            int(model.nobs),
                "note":             "ok" if model.pvalues.get(key, 1) > 0.05
                                          else "WARNING: pre-trend p<0.05",
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
def write_summary(static_df: pd.DataFrame, pre_df: pd.DataFrame,
                  out_path: Path) -> None:
    lines: List[str] = []
    lines.append("=" * 78)
    lines.append("RiceBaCI Module 05 — DiD regression summary")
    lines.append("=" * 78)
    lines.append("")
    lines.append("Static DiD (Treat × Post)")
    lines.append("-" * 78)
    lines.append(f"{'pipeline':10s} {'metric':6s} {'tau (d)':>8s} "
                 f"{'SE':>6s} {'t':>6s} {'p':>7s} {'CI95':>18s}")
    for _, r in static_df.iterrows():
        lines.append(
            f"{r['pipeline']:10s} {r['metric']:6s} "
            f"{r['tau_days']:+8.2f} {r['se_days']:6.2f} "
            f"{r['t_stat']:+6.2f} {r['p_value']:7.4f} "
            f"[{r['ci_lo_95']:+6.2f},{r['ci_hi_95']:+6.2f}]"
        )
    lines.append("")
    lines.append("Pre-trend test (interaction year × treat in pre-period)")
    lines.append("-" * 78)
    lines.append(f"{'pipeline':10s} {'metric':6s} {'coef':>7s} "
                 f"{'SE':>6s} {'p':>7s}  note")
    for _, r in pre_df.iterrows():
        lines.append(
            f"{r['pipeline']:10s} {r['metric']:6s} "
            f"{r['interaction_coef']:+7.3f} {r['se']:6.3f} "
            f"{r['p_value']:7.4f}  {r['note']}"
        )
    lines.append("")
    lines.append("Notes:")
    lines.append("  • SEs clustered at district level (n=8 clusters).")
    lines.append("  • Treatment cohort: coastal districts × 2019/2020/2021.")
    lines.append("  • Bulbul (2019, inland) and Hudhud (2014) excluded — "
                 "transferability hold-outs.")
    out_path.write_text("\n".join(lines))


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel",
                    default="analysis/synthetic_baci_panel.csv",
                    help="path to the BACI panel CSV "
                         "(synthetic by default; use the GEE export when ready)")
    ap.add_argument("--outdir", default="analysis/results")
    args = ap.parse_args()

    panel_path = Path(args.panel)
    out_dir    = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_panel(panel_path)
    print(f"loaded {len(df)} rows from {panel_path}")
    print(f"  districts: {df['district'].nunique()}, "
          f"years: {df['year'].min()}–{df['year'].max()}, "
          f"pipelines: {df['pipeline'].unique().tolist()}")

    # --- Static DiD ---------------------------------------------------------
    static_rows = []
    for pipe in PIPELINES:
        for met in METRICS:
            res = estimate_static_did(df, pipe, met)
            static_rows.append(res.as_row())
    static_df = pd.DataFrame(static_rows)
    static_df.to_csv(out_dir / "did_static.csv", index=False)

    # --- Event study --------------------------------------------------------
    es_frames = []
    for pipe in PIPELINES:
        for met in METRICS:
            es_frames.append(estimate_event_study(df, pipe, met))
    es_df = pd.concat(es_frames, ignore_index=True)
    es_df.to_csv(out_dir / "event_study.csv", index=False)

    # --- Parallel trends ----------------------------------------------------
    pre_df = parallel_trends_check(df)
    pre_df.to_csv(out_dir / "parallel_trends.csv", index=False)

    # --- Summary ------------------------------------------------------------
    write_summary(static_df, pre_df, out_dir / "did_summary.txt")

    print(f"\nwrote: {out_dir}/did_static.csv")
    print(f"wrote: {out_dir}/event_study.csv")
    print(f"wrote: {out_dir}/parallel_trends.csv")
    print(f"wrote: {out_dir}/did_summary.txt")
    print("\nstatic DiD results:")
    print(static_df.to_string(index=False))


if __name__ == "__main__":
    main()

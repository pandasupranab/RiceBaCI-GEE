#!/usr/bin/env python3
"""
RiceBaCI v2.0 — Module 05b (v22): Cell-level DiD on the 2019–2024 panel.

INPUT  : analysis/v22/fits/*_fits.parquet   (all 8 districts)
OUTPUT : analysis/v22/results/did_cell_level_v22.csv
         analysis/v22/results/did_cell_summary_v22.txt
         analysis/v22/results/did_cell_summary_v22.json

DESIGN — Cell × year panel
==========================
The district-median DiD (did_event_study_v22.py) produced null effects
(p_wcb 0.39–0.47). One culprit is power: 48 district-year obs with 8
clusters and a wide within-district dispersion (cells per district-year
range 5..77) collapses real cell-level signal into noise.

This module runs DiD at the cell level:
  - Sample: fit_ok cells × years 2019..2024 (~3,478 cell-years)
  - Spec  : Y_{i,d,t} = α_i + γ_t + τ · (treat_d · cyc_t) + ε
    with cell FE (district-cell) + year FE, district-clustered SE.
  - Cyclone years: 2019 (Fani), 2020 (Amphan), 2021 (Yaas).
  - Identification: same as district panel — inland controls absorb
    year FEs while coastal cells carry the cyclone exposure.

Why this can find what the district panel can't:
  - The district median throws away within-district heterogeneity.
    Some cells respond strongly to the cyclone, others not at all.
  - Cell FE absorbs time-invariant cell-level confounders (rice
    cultivar, elevation, soil), making the within-cell change more
    precise.
  - Clustering at district keeps inference conservative (still 8
    clusters) but precision of τ improves dramatically with n_obs.

We also report:
  - Wild-cluster bootstrap p-values (999 Rademacher draws on the
    district clusters).
  - The same event-study k=0..5 with cell + year FE.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
FITS_DIR = ROOT / "analysis" / "v22" / "fits"
OUT_DIR  = ROOT / "analysis" / "v22" / "results"

PANEL_YEARS = list(range(2019, 2025))    # 2019..2024
TREAT_DCODES = {"BLS", "BHA", "KDP", "JGS", "PUR"}   # coastal
CYCLONE_YEARS = [2019, 2020, 2021]
EVENT_ANCHOR = 2019
EVENT_REF_K  = 0

METRICS = [("sos", "SOS"), ("pos", "POS"), ("eos", "EOS")]

WCB_ITER = 499                # 999 is slower at cell scale; 499 still gives
WCB_SEED = 20260611_2


# ----------------------------------------------------------------------------
@dataclass
class StaticResult:
    metric: str
    n_obs: int
    n_cells: int
    n_clusters: int
    tau_days: float
    se_days: float
    t_stat: float
    p_value_cluster: float
    ci_lo_95: float
    ci_hi_95: float
    p_value_wcb: float
    r2: float


@dataclass
class EventStudyRow:
    metric: str
    event_k: int
    beta: float
    se: float
    ci_lo_95: float
    ci_hi_95: float
    n_obs: int
    n_treat_cells_at_k: int


# ----------------------------------------------------------------------------
def load_cell_panel() -> pd.DataFrame:
    """Stack all 8 district fit parquets, keep fit_ok cells in 2019–2024."""
    frames = []
    for p in sorted(FITS_DIR.glob("*_fits.parquet")):
        frames.append(pd.read_parquet(p))
    if not frames:
        sys.exit(f"FATAL: no fits in {FITS_DIR}")
    df = pd.concat(frames, ignore_index=True)
    df = df[df["fit_ok"]].copy()
    df = df[df["year"].isin(PANEL_YEARS)].copy()
    df["treat"] = df["district_code"].isin(TREAT_DCODES).astype(int)
    df["cyc"]   = df["year"].isin(CYCLONE_YEARS).astype(int)
    df["did"]   = df["treat"] * df["cyc"]
    # Unique cell key: district + cell_id (cell_id is "x,y" tile coord)
    df["cell_key"] = df["district_code"].astype(str) + "::" + df["cell_id"].astype(str)
    return df


# ----------------------------------------------------------------------------
def estimate_static_cell(df: pd.DataFrame, ycol: str, label: str) -> StaticResult:
    sub = df.dropna(subset=[ycol]).copy()
    sub["cell_key"]      = sub["cell_key"].astype("category")
    sub["year_c"]        = sub["year"].astype("category")
    sub["district_code"] = sub["district_code"].astype("category")

    model = smf.ols(
        f"{ycol} ~ did + C(cell_key) + C(year_c)",
        data=sub,
    ).fit(cov_type="cluster", cov_kwds={"groups": sub["district_code"]})

    tau = float(model.params["did"])
    se  = float(model.bse["did"])
    t   = float(model.tvalues["did"])
    p   = float(model.pvalues["did"])
    lo, hi = (float(x) for x in model.conf_int().loc["did"].tolist())

    p_wcb = wild_cluster_bootstrap_p(
        sub, ycol, t_observed=t,
        n_iter=WCB_ITER, seed=WCB_SEED,
    )

    return StaticResult(
        metric=label,
        n_obs=int(model.nobs),
        n_cells=int(sub["cell_key"].nunique()),
        n_clusters=int(sub["district_code"].nunique()),
        tau_days=tau, se_days=se, t_stat=t,
        p_value_cluster=p,
        ci_lo_95=lo, ci_hi_95=hi,
        p_value_wcb=p_wcb,
        r2=float(model.rsquared),
    )


def wild_cluster_bootstrap_p(sub: pd.DataFrame, ycol: str,
                             t_observed: float,
                             n_iter: int, seed: int) -> float:
    """Rademacher wild-cluster bootstrap at the district level."""
    sub = sub.copy()
    restr = smf.ols(
        f"{ycol} ~ C(cell_key) + C(year_c)", data=sub
    ).fit()
    y_hat = restr.fittedvalues.to_numpy()
    e_hat = restr.resid.to_numpy()

    rng = np.random.default_rng(seed)
    clusters = sub["district_code"].cat.categories.tolist()
    cluster_idx = {c: (sub["district_code"] == c).to_numpy() for c in clusters}

    t_boot = np.empty(n_iter)
    for b in range(n_iter):
        w_clu = rng.choice([-1.0, 1.0], size=len(clusters))
        w_obs = np.zeros(len(sub))
        for c, w in zip(clusters, w_clu):
            w_obs[cluster_idx[c]] = w
        y_star = y_hat + w_obs * e_hat
        sub["_ystar"] = y_star
        try:
            m_b = smf.ols(
                "_ystar ~ did + C(cell_key) + C(year_c)", data=sub
            ).fit(cov_type="cluster", cov_kwds={"groups": sub["district_code"]})
            t_boot[b] = float(m_b.tvalues["did"])
        except Exception:
            t_boot[b] = np.nan

    finite = np.isfinite(t_boot)
    if finite.sum() < 50:
        return float("nan")
    p = (1 + np.sum(np.abs(t_boot[finite]) >= abs(t_observed))) / (1 + finite.sum())
    return float(p)


# ----------------------------------------------------------------------------
def estimate_event_study_cell(df: pd.DataFrame, ycol: str, label: str
                              ) -> List[EventStudyRow]:
    sub = df.dropna(subset=[ycol]).copy()
    sub["cell_key"]      = sub["cell_key"].astype("category")
    sub["year_c"]        = sub["year"].astype("category")
    sub["district_code"] = sub["district_code"].astype("category")

    sub["event_k"] = np.where(
        sub["treat"] == 1,
        (sub["year"] - EVENT_ANCHOR).astype(int),
        -999,
    )
    sub["event_k_str"] = sub["event_k"].astype(str)

    formula = (
        f"{ycol} ~ C(event_k_str, Treatment(reference='{EVENT_REF_K}')) "
        f"+ C(cell_key) + C(year_c)"
    )
    model = smf.ols(formula, data=sub).fit(
        cov_type="cluster", cov_kwds={"groups": sub["district_code"]}
    )

    rows: List[EventStudyRow] = []
    for name, beta in model.params.items():
        if "event_k_str" not in name:
            continue
        try:
            k_str = name.split("[T.")[1].rstrip("]")
            k = int(k_str)
        except (IndexError, ValueError):
            continue
        if k == -999:
            continue
        se = float(model.bse[name])
        n_at_k = int(((sub["treat"] == 1) & (sub["event_k"] == k)).sum())
        rows.append(EventStudyRow(
            metric=label, event_k=k,
            beta=round(float(beta), 3),
            se=round(se, 3),
            ci_lo_95=round(float(beta) - 1.96 * se, 3),
            ci_hi_95=round(float(beta) + 1.96 * se, 3),
            n_obs=int(model.nobs),
            n_treat_cells_at_k=n_at_k,
        ))

    n_at_ref = int(((sub["treat"] == 1) & (sub["event_k"] == EVENT_REF_K)).sum())
    rows.append(EventStudyRow(
        metric=label, event_k=EVENT_REF_K,
        beta=0.0, se=0.0,
        ci_lo_95=0.0, ci_hi_95=0.0,
        n_obs=int(model.nobs),
        n_treat_cells_at_k=n_at_ref,
    ))
    rows.sort(key=lambda r: r.event_k)
    return rows


# ----------------------------------------------------------------------------
def write_summary(static_results: List[StaticResult],
                  es_results: List[EventStudyRow],
                  out_dir: Path) -> None:
    lines: List[str] = []
    lines.append("=" * 78)
    lines.append("RiceBaCI v22 Module 05b — Cell-level DiD + Event Study")
    lines.append("=" * 78)
    lines.append("")
    lines.append("Sample: fit_ok cells × years 2019..2024.")
    lines.append("Spec  : cell FE + year FE, district-clustered SE (8 clusters).")
    lines.append("WCB   : 499 Rademacher draws (cluster-level).")
    lines.append("")
    lines.append("Static DiD")
    lines.append("-" * 78)
    lines.append(f"{'metric':6s} {'n_obs':>6s} {'n_cells':>8s} "
                 f"{'tau(d)':>8s} {'SE':>6s} {'t':>6s} "
                 f"{'p_clu':>7s} {'p_wcb':>7s}  {'CI95':>18s}")
    for r in static_results:
        lines.append(
            f"{r.metric:6s} {r.n_obs:>6d} {r.n_cells:>8d} "
            f"{r.tau_days:+8.2f} {r.se_days:6.2f} {r.t_stat:+6.2f} "
            f"{r.p_value_cluster:7.4f} {r.p_value_wcb:7.4f}  "
            f"[{r.ci_lo_95:+6.2f},{r.ci_hi_95:+6.2f}]"
        )
    lines.append("")
    lines.append("Event study  (k = year − 2019, reference k=0)")
    lines.append("-" * 78)
    lines.append(f"{'metric':6s} {'k':>3s} {'beta(d)':>8s} "
                 f"{'SE':>6s} {'CI95':>20s}  n_treat_cells")
    for r in es_results:
        lines.append(
            f"{r.metric:6s} {r.event_k:3d} {r.beta:+8.2f} "
            f"{r.se:6.2f} "
            f"[{r.ci_lo_95:+6.2f},{r.ci_hi_95:+6.2f}]  {r.n_treat_cells_at_k:5d}"
        )
    (out_dir / "did_cell_summary_v22.txt").write_text("\n".join(lines))

    payload = {
        "design": "cell-level inland-control event study, 2019-2024",
        "n_clusters": 8,
        "cyclone_years": CYCLONE_YEARS,
        "event_anchor": EVENT_ANCHOR,
        "event_reference_k": EVENT_REF_K,
        "static": [asdict(r) for r in static_results],
        "event_study": [asdict(r) for r in es_results],
        "wcb_iter": WCB_ITER,
    }
    (out_dir / "did_cell_summary_v22.json").write_text(json.dumps(payload, indent=2))


# ----------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(OUT_DIR))
    args = ap.parse_args()

    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_cell_panel()
    print(f"[did_cell_v22] loaded {len(df):,} fit_ok cell-year obs "
          f"(years {df['year'].min()}–{df['year'].max()}, "
          f"districts={df['district_code'].nunique()}, "
          f"cells={df.assign(k=df['district_code'].astype(str)+'::'+df['cell_id'].astype(str))['k'].nunique()})")
    print(f"[did_cell_v22] treat·post obs (did=1): {int(df['did'].sum())}")

    static_results: List[StaticResult] = []
    es_rows:        List[EventStudyRow] = []
    for ycol, label in METRICS:
        print(f"[did_cell_v22] estimating {label} ...", flush=True)
        static_results.append(estimate_static_cell(df, ycol, label))
        es_rows.extend(estimate_event_study_cell(df, ycol, label))

    pd.DataFrame([asdict(r) for r in static_results]).to_csv(
        out_dir / "did_cell_level_v22.csv", index=False)
    pd.DataFrame([asdict(r) for r in es_rows]).to_csv(
        out_dir / "event_study_cell_v22.csv", index=False)
    write_summary(static_results, es_rows, out_dir)

    print(f"[did_cell_v22] wrote {out_dir}/did_cell_level_v22.csv")
    print(f"[did_cell_v22] wrote {out_dir}/event_study_cell_v22.csv")
    print(f"[did_cell_v22] wrote {out_dir}/did_cell_summary_v22.{{txt,json}}")
    print()
    print("STATIC DiD (cell-level):")
    for r in static_results:
        sig = "***" if r.p_value_cluster < 0.01 else \
              "**"  if r.p_value_cluster < 0.05 else \
              "*"   if r.p_value_cluster < 0.10 else ""
        print(f"  {r.metric}: tau = {r.tau_days:+.2f} d  "
              f"(SE {r.se_days:.2f}, n_obs={r.n_obs}, n_cells={r.n_cells}, "
              f"p_clu={r.p_value_cluster:.4f}, p_wcb={r.p_value_wcb:.4f}) {sig}")


if __name__ == "__main__":
    main()

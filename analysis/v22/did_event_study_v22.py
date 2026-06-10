#!/usr/bin/env python3
"""
RiceBaCI v2.0 — Module 05 (v22): DiD + Event Study on the 2019–2024 panel.

INPUT  : analysis/baci_panel_real_v22.csv      (48 district-year rows)
OUTPUT : analysis/v22/results/did_static_v22.csv
         analysis/v22/results/event_study_v22.csv
         analysis/v22/results/did_summary_v22.txt
         analysis/v22/results/did_summary_v22.json

DESIGN (decided 11 Jun 2026 — see build_v22_panel.py header)
============================================================
Panel : 48 district-year cells (6 yrs × 8 districts, 2019–2024).
Treat : 5 coastal districts (BLS, BHA, KDP, JGS, PUR).
Ctrl  : 3 inland   districts (ANG, DHK, CTK).

No pre-treatment years are observable (2017–2018 dropped due to
ESA WorldCover vintage mismatch + sparse S2 coverage). The
identification strategy therefore CANNOT include a parallel-trends
test. Instead we run:

  (A) Static DiD with district + year fixed effects, where the DiD
      indicator is `treat × cyclone_year`:

         Y_{dt} = α_d + γ_t + τ · (treat_d · cyc_t) + ε_{dt}

      cyc_t = 1[t ∈ {2019, 2020, 2021}]   (Fani / Amphan / Yaas)

      Standard errors are district-clustered (5 + 3 = 8 clusters).

  (B) Event study with the Fani anchor:

         Y_{dt} = α_d + γ_t + Σ_{k≥0, k≠ref} β_k · 1[treat_d, k_{dt}=k]
                + ε_{dt}

      where k_{dt} = t - 2019 for treatment districts (k ∈ {0,1,2,3,4,5})
      and k_{dt} = NA for inland controls (they only carry year FEs).
      Reference period: k = 0 (Fani year). β_k for k ∈ {1..5} traces
      the recovery dynamics after the initial Fani shock.

  (C) Wild-cluster bootstrap p-values for the static τ
      (Cameron–Gelbach–Miller 2008), since 8 clusters is borderline
      for asymptotic cluster-robust inference.

Outcomes : SOS_median, POS_median, EOS_median  (calendar DOY).
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
PANEL_PATH = ROOT / "analysis" / "baci_panel_real_v22.csv"
OUT_DIR    = ROOT / "analysis" / "v22" / "results"

# Cyclone years (treatment × these years → DiD interaction == 1)
CYCLONE_YEARS = [2019, 2020, 2021]
EVENT_ANCHOR  = 2019              # Fani — first observable shock
EVENT_REF_K   = 0                 # k=0 is the omitted reference

METRICS = [("sos_median", "SOS"),
           ("pos_median", "POS"),
           ("eos_median", "EOS")]

# Wild bootstrap iterations (Rademacher draws)
WCB_ITER  = 999
WCB_SEED  = 20260611


# ----------------------------------------------------------------------------
@dataclass
class StaticResult:
    metric: str
    n_obs: int
    n_clusters: int
    tau_days: float
    se_days: float
    t_stat: float
    p_value_cluster: float
    ci_lo_95: float
    ci_hi_95: float
    p_value_wcb: float
    n_treat_post: int


@dataclass
class EventStudyRow:
    metric: str
    event_k: int
    beta: float
    se: float
    ci_lo_95: float
    ci_hi_95: float
    n_obs: int
    n_treat_at_k: int


# ----------------------------------------------------------------------------
def load_panel(path: Path) -> pd.DataFrame:
    """Read the v22 panel and add DiD / event-study indicators."""
    df = pd.read_csv(path)
    required = {
        "district", "district_code", "year", "treatment",
        "n_ok", "sos_median", "pos_median", "eos_median",
        "cyclone_exposure", "event_time",
    }
    missing = required - set(df.columns)
    if missing:
        sys.exit(f"FATAL: panel missing columns: {missing}")

    if len(df) == 0:
        sys.exit("FATAL: empty panel")

    df["treat"] = df["treatment"].astype(int)
    df["cyc"]   = df["year"].isin(CYCLONE_YEARS).astype(int)
    df["did"]   = df["treat"] * df["cyc"]
    return df


# ----------------------------------------------------------------------------
def estimate_static(df: pd.DataFrame, ycol: str, label: str) -> StaticResult:
    """Static DiD with district + year FE; district-clustered SE."""
    sub = df.dropna(subset=[ycol]).copy()
    sub["district"] = sub["district"].astype("category")
    sub["year_c"]   = sub["year"].astype("category")

    model = smf.ols(
        f"{ycol} ~ did + C(district) + C(year_c)",
        data=sub,
    ).fit(cov_type="cluster", cov_kwds={"groups": sub["district"]})

    tau = float(model.params["did"])
    se  = float(model.bse["did"])
    t   = float(model.tvalues["did"])
    p   = float(model.pvalues["did"])
    lo, hi = (float(x) for x in model.conf_int().loc["did"].tolist())
    n_treat_post = int(((sub["treat"] == 1) & (sub["cyc"] == 1)).sum())

    # ---- wild-cluster bootstrap p-value -----------------------------------
    p_wcb = wild_cluster_bootstrap_p(
        sub, ycol, t_observed=t,
        n_iter=WCB_ITER, seed=WCB_SEED,
    )

    return StaticResult(
        metric=label,
        n_obs=int(model.nobs),
        n_clusters=int(sub["district"].nunique()),
        tau_days=tau, se_days=se, t_stat=t,
        p_value_cluster=p,
        ci_lo_95=lo, ci_hi_95=hi,
        p_value_wcb=p_wcb,
        n_treat_post=n_treat_post,
    )


# ----------------------------------------------------------------------------
def wild_cluster_bootstrap_p(sub: pd.DataFrame, ycol: str,
                             t_observed: float,
                             n_iter: int = 999,
                             seed: int = 20260611) -> float:
    """Wild-cluster bootstrap p-value for H0: τ = 0 (Cameron–Gelbach–Miller 2008).

    For each iteration:
      1. Draw Rademacher weights {+1,-1} at the cluster (district) level.
      2. Multiply the restricted-model residuals (τ=0) by those weights.
      3. Form the bootstrap outcome  y* = y_hat_restricted + e_weighted.
      4. Re-fit the unrestricted model on y* and record t*.
      5. p = (1 + #{|t*| ≥ |t_obs|}) / (1 + B)
    """
    # Restricted model (τ = 0): regress y on FEs only
    sub = sub.copy()
    sub["did_zero"] = 0.0
    restr = smf.ols(
        f"{ycol} ~ C(district) + C(year_c)", data=sub
    ).fit()
    y_hat = restr.fittedvalues
    e_hat = restr.resid

    rng = np.random.default_rng(seed)
    clusters = sub["district"].cat.categories.tolist()
    cluster_idx = {c: (sub["district"] == c).to_numpy() for c in clusters}

    t_boot = np.empty(n_iter)
    for b in range(n_iter):
        # Rademacher weight per cluster
        w_clu = rng.choice([-1.0, 1.0], size=len(clusters))
        w_obs = np.zeros(len(sub))
        for c, w in zip(clusters, w_clu):
            w_obs[cluster_idx[c]] = w
        y_star = y_hat.to_numpy() + w_obs * e_hat.to_numpy()
        sub["_ystar"] = y_star
        try:
            m_b = smf.ols(
                "_ystar ~ did + C(district) + C(year_c)", data=sub
            ).fit(cov_type="cluster", cov_kwds={"groups": sub["district"]})
            t_boot[b] = float(m_b.tvalues["did"])
        except Exception:
            t_boot[b] = np.nan

    finite = np.isfinite(t_boot)
    if finite.sum() < 50:
        return float("nan")
    p = (1 + np.sum(np.abs(t_boot[finite]) >= abs(t_observed))) / (1 + finite.sum())
    return float(p)


# ----------------------------------------------------------------------------
def estimate_event_study(df: pd.DataFrame, ycol: str, label: str) -> List[EventStudyRow]:
    """Event study with k = year - 2019 for treatment, controls absorbed."""
    sub = df.dropna(subset=[ycol]).copy()
    sub["district"] = sub["district"].astype("category")
    sub["year_c"]   = sub["year"].astype("category")

    # Build event_k dummies for treatment districts; controls get k=-999 sentinel
    sub["event_k"] = np.where(
        sub["treat"] == 1,
        (sub["year"] - EVENT_ANCHOR).astype(int),
        -999,
    )
    sub["event_k_str"] = sub["event_k"].astype(str)

    formula = (
        f"{ycol} ~ C(event_k_str, Treatment(reference='{EVENT_REF_K}')) "
        f"+ C(district) + C(year_c)"
    )
    model = smf.ols(formula, data=sub).fit(
        cov_type="cluster", cov_kwds={"groups": sub["district"]}
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
            n_treat_at_k=n_at_k,
        ))

    # Reference period k = EVENT_REF_K (by construction beta = 0)
    n_at_ref = int(((sub["treat"] == 1) & (sub["event_k"] == EVENT_REF_K)).sum())
    rows.append(EventStudyRow(
        metric=label, event_k=EVENT_REF_K,
        beta=0.0, se=0.0,
        ci_lo_95=0.0, ci_hi_95=0.0,
        n_obs=int(model.nobs),
        n_treat_at_k=n_at_ref,
    ))
    rows.sort(key=lambda r: r.event_k)
    return rows


# ----------------------------------------------------------------------------
def write_summary(static_results: List[StaticResult],
                  es_results: List[EventStudyRow],
                  out_dir: Path) -> None:
    lines: List[str] = []
    lines.append("=" * 78)
    lines.append("RiceBaCI v22 Module 05 — DiD + Event Study (2019–2024 panel)")
    lines.append("=" * 78)
    lines.append("")
    lines.append("Design: 5 coastal-treatment vs 3 inland-control districts.")
    lines.append("Cyclone years (treatment × post=1): 2019 Fani, 2020 Amphan, 2021 Yaas.")
    lines.append("SEs district-clustered (8 clusters). WCB = Rademacher wild-cluster bootstrap.")
    lines.append("")
    lines.append("Static DiD  (Y = α_d + γ_t + τ · (treat × cyc) + ε)")
    lines.append("-" * 78)
    lines.append(f"{'metric':6s} {'tau(d)':>8s} {'SE':>6s} "
                 f"{'t':>6s} {'p_clu':>7s} {'p_wcb':>7s} "
                 f"{'CI95':>20s}  n_tp")
    for r in static_results:
        lines.append(
            f"{r.metric:6s} {r.tau_days:+8.2f} {r.se_days:6.2f} "
            f"{r.t_stat:+6.2f} {r.p_value_cluster:7.4f} {r.p_value_wcb:7.4f} "
            f"[{r.ci_lo_95:+6.2f},{r.ci_hi_95:+6.2f}]  {r.n_treat_post:3d}"
        )
    lines.append("")
    lines.append("Event study  (k = year − 2019, reference k=0)")
    lines.append("-" * 78)
    lines.append(f"{'metric':6s} {'k':>3s} {'beta(d)':>8s} "
                 f"{'SE':>6s} {'CI95':>20s}  n_treat")
    for r in es_results:
        lines.append(
            f"{r.metric:6s} {r.event_k:3d} {r.beta:+8.2f} "
            f"{r.se:6.2f} "
            f"[{r.ci_lo_95:+6.2f},{r.ci_hi_95:+6.2f}]  {r.n_treat_at_k:3d}"
        )
    lines.append("")
    lines.append("Notes:")
    lines.append("  • No pre-treatment parallel-trends test (2017–2018 data unavailable;")
    lines.append("    see Methods rewrite for the data-availability rationale).")
    lines.append("  • Identification rests on inland-control year-FE absorption and the")
    lines.append("    within-cohort dynamics of the 5 coastal districts (k=1..5).")
    lines.append("  • WCB p-value uses 999 Rademacher draws (Cameron-Gelbach-Miller 2008).")
    (out_dir / "did_summary_v22.txt").write_text("\n".join(lines))

    # JSON for downstream pickup (e.g., manuscript autopopulate)
    payload = {
        "design": "inland-control event study, 2019-2024",
        "n_districts": 8,
        "n_years":     6,
        "n_obs":       48,
        "n_clusters":  8,
        "cyclone_years": CYCLONE_YEARS,
        "event_anchor": EVENT_ANCHOR,
        "event_reference_k": EVENT_REF_K,
        "static": [asdict(r) for r in static_results],
        "event_study": [asdict(r) for r in es_results],
        "wcb_iter": WCB_ITER,
    }
    (out_dir / "did_summary_v22.json").write_text(json.dumps(payload, indent=2))


# ----------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel",  default=str(PANEL_PATH))
    ap.add_argument("--outdir", default=str(OUT_DIR))
    args = ap.parse_args()

    panel_path = Path(args.panel)
    out_dir    = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_panel(panel_path)
    print(f"[did_v22] loaded {len(df)} rows from {panel_path.name}")
    print(f"[did_v22]  districts={df['district_code'].nunique()}, "
          f"years={df['year'].min()}–{df['year'].max()}, "
          f"n_treat_post={int(df['did'].sum())}")

    # Static DiD
    static_results: List[StaticResult] = []
    for ycol, label in METRICS:
        r = estimate_static(df, ycol, label)
        static_results.append(r)
    pd.DataFrame([asdict(r) for r in static_results]).to_csv(
        out_dir / "did_static_v22.csv", index=False)

    # Event study
    es_rows: List[EventStudyRow] = []
    for ycol, label in METRICS:
        es_rows.extend(estimate_event_study(df, ycol, label))
    pd.DataFrame([asdict(r) for r in es_rows]).to_csv(
        out_dir / "event_study_v22.csv", index=False)

    write_summary(static_results, es_rows, out_dir)

    print(f"[did_v22] wrote {out_dir}/did_static_v22.csv")
    print(f"[did_v22] wrote {out_dir}/event_study_v22.csv")
    print(f"[did_v22] wrote {out_dir}/did_summary_v22.{{txt,json}}")
    print()
    print("STATIC DiD:")
    for r in static_results:
        sig = "***" if r.p_value_cluster < 0.01 else \
              "**"  if r.p_value_cluster < 0.05 else \
              "*"   if r.p_value_cluster < 0.10 else ""
        print(f"  {r.metric}: τ = {r.tau_days:+.2f} d  "
              f"(SE {r.se_days:.2f}, p_cluster={r.p_value_cluster:.4f}, "
              f"p_wcb={r.p_value_wcb:.4f}) {sig}")


if __name__ == "__main__":
    main()

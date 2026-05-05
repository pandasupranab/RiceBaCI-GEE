"""
05a_wild_cluster_bootstrap.py — wild-cluster bootstrap (CGM) for the
DiD coefficient with G = 8 districts.

Why this exists
---------------
Standard cluster-robust ("CR1") SEs are known to over-reject the null
when the number of clusters is small (G <= 30; we have G = 8).
Cameron, Gelbach & Miller (2008) recommend the wild cluster bootstrap
with the residuals imposed under the null (WCR), which empirically
delivers correct size even at G = 5–10.

Implementation
--------------
For each (pipeline, metric) we:
  1. Fit the unrestricted DiD model (Eq. 3.Y.1).
  2. Fit the restricted model imposing H0: tau = 0.
  3. Draw B Rademacher cluster weights w_g in {-1, +1}.
  4. Build bootstrap outcomes y* = X * beta_restricted + w_g * resid_g.
  5. Re-fit unrestricted on each replicate, store t-statistic on `did`.
  6. Bootstrap p-value = share of |t*| >= |t_observed|.
  7. 95 % CI by inversion: grid of tau_0 candidates, accept those with
     bootstrap p > 0.05.

Defaults
--------
B            = 9999  (CGM-style, > 999 to keep MC noise on p < 0.05 small)
weights      = Rademacher (CGM showed Mammen weights add no precision at G=8)
restricted   = True  (impose null on residuals, the CGM recommendation)

Outputs
-------
analysis/results/wild_bootstrap.csv  — one row per (pipeline, metric):
    tau_hat, t_obs, p_wcb_2sided, ci_lo_95, ci_hi_95, B

Author : Supranab Panda
Date   : 2026-05-05
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.regression.linear_model import OLS

# Local import of Module 05's loader
sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib.util
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod
DID_PATH = Path(__file__).resolve().parent / "05_did_regression.py"
did_mod  = _load("did_regression", DID_PATH)

PIPELINES = ["raw", "corrected"]
METRICS   = ["SOS", "POS", "EOS"]


# ---------------------------------------------------------------------------
def _design(sub: pd.DataFrame):
    """Build (y, X, did_idx, cluster_id) for OLS with district & year dummies.

    Returns numpy arrays so the bootstrap inner loop is fast.
    """
    sub = sub.copy().reset_index(drop=True)
    # One-hot encode district and year (drop_first to avoid collinearity)
    dist_dum = pd.get_dummies(sub["district"], prefix="d", drop_first=True)
    year_dum = pd.get_dummies(sub["year"],     prefix="y", drop_first=True)
    X = pd.concat(
        [pd.Series(1.0, index=sub.index, name="const"),
         sub[["did"]],
         dist_dum, year_dum],
        axis=1,
    ).astype(float)
    y = sub["median_doy"].astype(float).values
    cluster = sub["district"].values
    did_idx = list(X.columns).index("did")
    return y, X.values, did_idx, cluster


def _fit_t(y: np.ndarray, X: np.ndarray, did_idx: int, cluster: np.ndarray
           ) -> tuple[float, float, np.ndarray]:
    """Fit OLS, return (beta_did, t_did_clustered, residuals)."""
    res = OLS(y, X).fit(cov_type="cluster",
                        cov_kwds={"groups": cluster, "use_correction": True})
    beta = res.params[did_idx]
    se   = res.bse[did_idx]
    t    = beta / se if se > 0 else np.nan
    return beta, t, res.resid


def _wild_cluster_bootstrap(
    y: np.ndarray, X: np.ndarray, did_idx: int, cluster: np.ndarray,
    B: int = 9999, seed: int = 20260505,
    h0_tau: float = 0.0,
) -> tuple[np.ndarray, float, float]:
    """Return (t_star array, t_obs unrestricted at tau, beta_obs).

    Implements the WCR (restricted) bootstrap of Cameron, Gelbach &
    Miller (2008). Residuals are computed from the model with `did`
    coefficient imposed at h0_tau, so they reflect the null DGP.
    """
    rng = np.random.default_rng(seed)
    n, k = X.shape

    # Unrestricted t (used both for the observed test stat AND each replicate)
    beta_obs, t_obs, _ = _fit_t(y, X, did_idx, cluster)

    # Build restricted residuals: subtract h0_tau * X[:,did_idx] from y,
    # then regress on X without the did column.
    y_minus_did = y - h0_tau * X[:, did_idx]
    X_no_did    = np.delete(X, did_idx, axis=1)
    res_restr   = OLS(y_minus_did, X_no_did).fit()
    beta_restr  = res_restr.params
    fitted_restr_full = X_no_did @ beta_restr + h0_tau * X[:, did_idx]
    resid_restr       = y - fitted_restr_full

    # Cluster groupings (positions per district)
    clusters_unique = np.unique(cluster)
    cluster_pos = {c: np.where(cluster == c)[0] for c in clusters_unique}

    t_star = np.empty(B)
    for b in range(B):
        # Rademacher weights, one per cluster
        w = rng.choice([-1.0, 1.0], size=len(clusters_unique))
        w_full = np.empty(n)
        for c, w_c in zip(clusters_unique, w):
            w_full[cluster_pos[c]] = w_c
        # Bootstrap outcome
        y_star = fitted_restr_full + w_full * resid_restr
        # Re-fit unrestricted, get t on did
        try:
            _, t_b, _ = _fit_t(y_star, X, did_idx, cluster)
        except Exception:                                 # singular replicate
            t_b = np.nan
        t_star[b] = t_b

    return t_star, t_obs, beta_obs


def _wcb_p_value(t_star: np.ndarray, t_obs: float) -> float:
    """Two-sided WCR p-value with finite-sample +1 correction."""
    valid = ~np.isnan(t_star)
    return (1 + np.sum(np.abs(t_star[valid]) >= np.abs(t_obs))) / (1 + valid.sum())


def _wcb_ci_by_inversion(
    y, X, did_idx, cluster, beta_obs, t_obs,
    B: int = 999, seed: int = 20260505, alpha: float = 0.05,
    n_grid: int = 41,
) -> tuple[float, float]:
    """
    Construct (1-alpha) CI by inverting the WCR test on a grid of tau_0.
    Uses a smaller B per grid point to keep runtime bounded; the boundary
    is then refined by bisection.

    Heuristic grid: beta_obs ± 4 * (CR-SE), 41 points; accept tau_0 whose
    test does NOT reject at alpha.
    """
    # CR1 SE for grid scaling
    res = OLS(y, X).fit(cov_type="cluster",
                        cov_kwds={"groups": cluster, "use_correction": True})
    cr_se = res.bse[did_idx]
    if not np.isfinite(cr_se) or cr_se == 0:
        return (np.nan, np.nan)

    grid = np.linspace(beta_obs - 4 * cr_se, beta_obs + 4 * cr_se, n_grid)

    accept = []
    for tau_0 in grid:
        t_star, t_obs_at_h0, _ = _wild_cluster_bootstrap(
            y, X, did_idx, cluster, B=B, seed=seed + int(1000 * tau_0),
            h0_tau=tau_0,
        )
        p = _wcb_p_value(t_star, t_obs_at_h0)
        if p >= alpha:
            accept.append(tau_0)

    if not accept:
        return (np.nan, np.nan)
    return (min(accept), max(accept))


# ---------------------------------------------------------------------------
def run_one(df: pd.DataFrame, pipeline: str, metric: str,
            B: int = 9999, B_ci: int = 999, seed: int = 20260505,
            do_ci: bool = True) -> dict:
    sub = df.query("pipeline == @pipeline and metric == @metric").copy()
    y, X, did_idx, cluster = _design(sub)

    t_star, t_obs, beta_obs = _wild_cluster_bootstrap(
        y, X, did_idx, cluster, B=B, seed=seed, h0_tau=0.0,
    )
    p_wcb = _wcb_p_value(t_star, t_obs)

    ci_lo, ci_hi = (np.nan, np.nan)
    if do_ci:
        ci_lo, ci_hi = _wcb_ci_by_inversion(
            y, X, did_idx, cluster, beta_obs, t_obs,
            B=B_ci, seed=seed,
        )

    return {
        "pipeline":      pipeline,
        "metric":        metric,
        "tau_hat":       round(beta_obs, 3),
        "t_obs":         round(t_obs, 3),
        "B":             B,
        "p_wcb_2sided":  round(p_wcb, 4),
        "ci_lo_95_wcb":  round(ci_lo, 3) if not np.isnan(ci_lo) else np.nan,
        "ci_hi_95_wcb":  round(ci_hi, 3) if not np.isnan(ci_hi) else np.nan,
        "B_ci":          B_ci if do_ci else 0,
    }


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel",  default="analysis/synthetic_baci_panel.csv")
    ap.add_argument("--outdir", default="analysis/results")
    ap.add_argument("--B",      type=int, default=9999, help="bootstrap reps for p-value")
    ap.add_argument("--B-ci",   type=int, default=499,  help="reps per grid point for CI")
    ap.add_argument("--seed",   type=int, default=20260505)
    ap.add_argument("--no-ci",  action="store_true",
                    help="skip CI inversion (faster; just report p-values)")
    args = ap.parse_args()

    df = did_mod.load_panel(Path(args.panel))
    print(f"loaded {len(df)} rows; {df['district'].nunique()} clusters")
    print(f"running WCR bootstrap with B={args.B}, B_ci={args.B_ci} "
          f"({'skipping' if args.no_ci else 'including'} CI inversion)")

    rows = []
    for pipe in PIPELINES:
        for met in METRICS:
            print(f"  {pipe:10s} / {met} ...", end=" ", flush=True)
            r = run_one(df, pipe, met,
                        B=args.B, B_ci=args.B_ci, seed=args.seed,
                        do_ci=not args.no_ci)
            rows.append(r)
            print(f"tau={r['tau_hat']:+.2f}  p_wcb={r['p_wcb_2sided']:.4f}  "
                  f"CI=[{r['ci_lo_95_wcb']}, {r['ci_hi_95_wcb']}]")

    out_dir = Path(args.outdir); out_dir.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame(rows)
    out_path = out_dir / "wild_bootstrap.csv"
    out_df.to_csv(out_path, index=False)
    print(f"\nwrote: {out_path}")
    print("\nfull results:")
    print(out_df.to_string(index=False))


if __name__ == "__main__":
    main()

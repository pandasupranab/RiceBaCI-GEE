"""17_estimate_panel_variance_components.py — empirical variance components
for Module 09 power simulator.

Estimates sigma_u (district FE noise), sigma_t (year FE noise), and
sigma_e (idiosyncratic noise) directly from the v2.1 BACI panel SOS
residuals via the two-way fixed-effects (TWFE) decomposition

    y_{it} = mu + alpha_i + delta_t + epsilon_{it}

with alpha_i ~ N(0, sigma_u^2), delta_t ~ N(0, sigma_t^2), epsilon_{it}
~ N(0, sigma_e^2).

Method (within-estimator + ANOVA-style moment estimator):

  1. Demean by district to get alpha_i hat (district FE).
  2. Demean by year to get delta_t hat (year FE).
  3. Residual epsilon_{it} = y_{it} - mu_hat - alpha_i - delta_t.
  4. sigma_u_hat^2 = var(alpha_i_hat)
  5. sigma_t_hat^2 = var(delta_t_hat)
  6. sigma_e_hat^2 = var(epsilon_{it})

Writes:
  analysis/results/real_v21/variance_components_sos.csv
  analysis/results/real_v21/variance_components_pos.csv
  analysis/results/real_v21/variance_components_eos.csv
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "analysis" / "baci_panel_real_v21.csv"
OUT = ROOT / "analysis" / "results" / "real_v21"
OUT.mkdir(parents=True, exist_ok=True)


def decompose(df: pd.DataFrame, metric: str) -> dict:
    """Two-way FE variance decomposition on the RAW pipeline series."""
    sub = df[(df.metric == metric) & (df.pipeline == "raw")].copy()
    pivot = sub.pivot(index="district", columns="year", values="median_doy")
    if pivot.isna().any().any():
        # EOS has right-censoring; drop incomplete rows for variance estimation
        pivot = pivot.dropna(axis=0, how="any")
    y = pivot.values.astype(float)
    G, T = y.shape
    mu = y.mean()
    alpha = y.mean(axis=1) - mu  # district FEs (length G)
    delta = y.mean(axis=0) - mu  # year FEs (length T)
    eps = y - mu - alpha[:, None] - delta[None, :]
    return {
        "metric": metric,
        "n_districts": int(G),
        "n_years": int(T),
        "n_cells": int(G * T),
        "mu_hat": float(mu),
        "sigma_u_hat": float(np.std(alpha, ddof=1)),
        "sigma_t_hat": float(np.std(delta, ddof=1)),
        "sigma_e_hat": float(np.std(eps, ddof=1)),
        "var_alpha": float(np.var(alpha, ddof=1)),
        "var_delta": float(np.var(delta, ddof=1)),
        "var_eps": float(np.var(eps, ddof=1)),
        "var_total": float(np.var(y, ddof=1)),
    }


def main():
    df = pd.read_csv(PANEL)
    rows = []
    for m in ("SOS", "POS", "EOS"):
        comp = decompose(df, m)
        print(f"\n=== {m} ===")
        for k, v in comp.items():
            print(f"  {k} = {v}")
        rows.append(comp)
    out_df = pd.DataFrame(rows)
    out_path = OUT / "variance_components_real_v21.csv"
    out_df.to_csv(out_path, index=False)
    print(f"\n[OK] wrote {out_path}")
    return out_df


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Module 09 — Post-hoc power analysis (Methods §3.Y.4)
=====================================================

Reviewers of small-G DiD studies routinely ask:

    "With G=8 districts, what minimum effect size could you have
     reliably detected, and what is your power for the effect you
     observed?"

This module answers both, parametrically and via Monte-Carlo on the
fitted variance structure of the Module-05 panel.

Two outputs:

  (1) Minimum Detectable Effect (MDE) at α=0.05, power=0.80,
      one-sided and two-sided, computed analytically from the
      cluster-robust SE recovered in Module 05a (WCR).

  (2) Power curves: simulated rejection rates for τ ∈ {0,…,8} days
      at G=8 (current design) and G∈{4,6,8,12} (sensitivity to
      district roster), holding within-cluster autocorrelation and
      year FE structure constant. 999 reps per grid point.

Outputs:
  analysis/results/power_mde.csv          — MDE table (4 rows)
  analysis/results/power_curves.csv       — long-format curves (4×9 = 36 rows)
  figures/fig5_power_curves.pdf|png       — power curves + MDE markers

The power-curves figure also lands in the manuscript supplement as
Figure S1 (referenced by Methods §3.Y.4).

Conservative posture: this is *post-hoc* power, reported transparently
because the panel size is fixed by geography (8 coastal+inland districts).
We do NOT use it to recompute p-values — those come from WCR.
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# Reuse Module 05's static-DiD point estimator so the simulator and
# the actual analysis use the same regression specification.
import importlib.util
import sys

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "did_mod", ROOT / "analysis" / "05_did_regression.py")
DID_MOD = importlib.util.module_from_spec(SPEC)
sys.modules["did_mod"] = DID_MOD
SPEC.loader.exec_module(DID_MOD)

# ---------- Okabe-Ito (consistent with Fig 2/3/4) ----------
OK_BLUE   = "#0072B2"
OK_ORANGE = "#E69F00"
OK_GREEN  = "#009E73"
OK_RED    = "#D55E00"


# ============================================================
# 1. MDE — analytical, from the WCR-derived SE
# ============================================================
def mde_analytical(se: float,
                   alpha: float = 0.05,
                   power: float = 0.80,
                   df: int = 7,            # G-1 with G=8 clusters
                   sided: str = "two") -> float:
    """
    Minimum detectable effect at given (α, power, df).

    Uses the t-distribution with cluster df = G-1 (Donald & Lang
    small-cluster correction), not the normal approximation. This
    is the binding constraint at G=8.

    MDE = (t_{α/2 or α, df} + t_{1-power, df}) × SE
    """
    if sided == "two":
        t_alpha = stats.t.ppf(1 - alpha / 2, df)
    else:
        t_alpha = stats.t.ppf(1 - alpha, df)
    t_power = stats.t.ppf(power, df)
    return (t_alpha + t_power) * se


def build_mde_table(did_static_csv: Path,
                    wcr_csv: Path) -> pd.DataFrame:
    """
    For the 6 (pipeline × metric) cells, report:
      observed τ̂, SE (cluster-robust from Module 05),
      MDE_80 two-sided, MDE_80 one-sided,
      ratio τ̂/MDE_80 (≥1 means the observed effect was detectable).
    """
    did = pd.read_csv(did_static_csv)
    wcr = pd.read_csv(wcr_csv)
    rows = []
    for _, r in did.iterrows():
        se = float(r["se_days"])
        tau = float(r["tau_days"])
        m2 = mde_analytical(se, sided="two")
        m1 = mde_analytical(se, sided="one")
        rows.append({
            "pipeline":      r["pipeline"],
            "metric":        r["metric"],
            "tau_hat_d":     round(tau, 3),
            "se_d":          round(se, 3),
            "df_clusters":   7,                # G=8, G-1=7
            "alpha":         0.05,
            "power_target":  0.80,
            "MDE_2sided_d":  round(m2, 3),
            "MDE_1sided_d":  round(m1, 3),
            "tau_over_MDE":  round(abs(tau) / m2, 2),
            "detectable":    "yes" if abs(tau) >= m2 else "no",
        })
    return pd.DataFrame(rows)


# ============================================================
# 2. Monte-Carlo power curves
# ============================================================
def simulate_power(true_tau: float,
                   G: int,
                   T: int = 8,
                   sigma_u: float = 13.06,      # district FE noise (real v2.1 SOS panel)
                   sigma_t: float = 41.75,      # year FE noise (real v2.1 SOS panel)
                   sigma_e: float = 31.28,      # idio noise (real v2.1 SOS panel; days)
                   alpha: float = 0.05,
                   reps: int = 999,
                   seed: int = 20260605) -> float:
    """
    Empirical rejection rate of H0: τ=0 under DGP

        y_{it} = α_i + δ_t + τ·D_{it} + ε_{it}

    where D_{it}=1 for treated districts in post-period (t ≥ 4),
    α_i ~ N(0, σ_u²),  δ_t ~ N(0, σ_t²),  ε_{it} ~ N(0, σ_e²).

    Defaults are EMPIRICAL variance components estimated from the real v2.1
    BACI panel SOS series (analysis/baci_panel_real_v21.csv) via two-way FE
    decomposition; see analysis/17_estimate_panel_variance_components.py and
    analysis/results/real_v21/variance_components_real_v21.csv.

    Test = OLS τ̂ with cluster-robust SE (G clusters), t-test on
    df = G-1 (matches Donald-Lang and our WCR posture).

    Returns power = Pr(reject H0 | true_tau).
    """
    rng = np.random.default_rng(seed)
    G_treat = G // 2 if G > 1 else 1
    treat = np.array([1] * G_treat + [0] * (G - G_treat))
    post = np.arange(T) >= (T // 2)

    # design matrix columns we'll Pr-regress on
    rejects = 0
    df = G - 1
    t_crit = stats.t.ppf(1 - alpha / 2, df)

    for _ in range(reps):
        a_i = rng.normal(0, sigma_u, size=G)
        d_t = rng.normal(0, sigma_t, size=T)
        e_it = rng.normal(0, sigma_e, size=(G, T))
        y = (a_i[:, None] + d_t[None, :]
             + true_tau * (treat[:, None] * post[None, :])
             + e_it)

        # Regress y on dummies for district + year + treat*post (DiD spec).
        # Implement via partial-out trick to keep it fast.
        y_d = y - y.mean(axis=1, keepdims=True)         # demean district
        y_dt = y_d - y_d.mean(axis=0, keepdims=True)    # demean year
        D = (treat[:, None] * post[None, :]).astype(float)
        D_d = D - D.mean(axis=1, keepdims=True)
        D_dt = D_d - D_d.mean(axis=0, keepdims=True)

        x = D_dt.ravel()
        yflat = y_dt.ravel()
        denom = (x ** 2).sum()
        if denom < 1e-10:
            continue
        beta = (x * yflat).sum() / denom
        resid = yflat - beta * x

        # CR1 cluster-robust SE on G clusters (rows of original matrix)
        resid_mat = resid.reshape(G, T)
        x_mat = x.reshape(G, T)
        S = np.array([(x_mat[g] * resid_mat[g]).sum() for g in range(G)])
        meat = (S ** 2).sum()
        cr_var = meat / (denom ** 2)
        # small-sample CR1 correction
        cr_var *= G / (G - 1)
        se = np.sqrt(cr_var)
        if se < 1e-10:
            continue
        t_stat = beta / se
        if abs(t_stat) > t_crit:
            rejects += 1
    return rejects / reps


def build_power_curves(taus=(0, 5, 10, 15, 20, 30, 40, 60, 80, 100),
                       Gs=(4, 6, 8, 12),
                       reps: int = 999) -> pd.DataFrame:
    rows = []
    for G in Gs:
        for tau in taus:
            p = simulate_power(true_tau=tau, G=G, reps=reps)
            rows.append({"G": G, "true_tau_d": tau, "power": round(p, 3)})
            print(f"  G={G:2d}  τ={tau:>4.1f}d  power={p:.3f}")
    return pd.DataFrame(rows)


# ============================================================
# 3. Figure 5 — power curves
# ============================================================
def make_figure(curves: pd.DataFrame,
                mde: pd.DataFrame,
                outdir: Path) -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.6,
    })

    fig, ax = plt.subplots(figsize=(5.2, 3.6))

    color_map = {4: OK_RED, 6: OK_ORANGE, 8: OK_BLUE, 12: OK_GREEN}
    for G, sub in curves.groupby("G"):
        sub = sub.sort_values("true_tau_d")
        lw = 2.0 if G == 8 else 1.0
        ls = "-" if G == 8 else "--"
        ax.plot(sub["true_tau_d"], sub["power"],
                marker="o", ms=3.5, lw=lw, ls=ls,
                color=color_map[G],
                label=f"G={G}" + (" (this study)" if G == 8 else ""))

    # 0.80 power reference
    ax.axhline(0.80, color="0.4", lw=0.6, ls=":", zorder=0)
    tau_max = float(curves["true_tau_d"].max())
    ax.text(tau_max * 0.99, 0.81, "power = 0.80", fontsize=7.5,
            color="0.3", ha="right", va="bottom")

    # MDE markers — observed |τ| for non-degenerate cells
    # (skip rows where SE==0 or tau_hat==0, which collapse to spurious
    #  "detectable" status because MDE_2sided_d resolves to 0).
    strong_all = mde[mde["detectable"] == "yes"].copy()
    strong = strong_all[
        (strong_all["se_d"].astype(float) > 0)
        & (strong_all["tau_hat_d"].astype(float).abs() > 0)
    ].copy()
    if not strong.empty:
        for _, r in strong.iterrows():
            ax.axvline(abs(float(r["tau_hat_d"])),
                       color="0.7", lw=0.4, alpha=0.5)
        annot = (
            "Observed |tau-hat| (detectable cells, non-degenerate): "
            f"{abs(strong['tau_hat_d']).min():.1f}-"
            f"{abs(strong['tau_hat_d']).max():.1f} d"
        )
    else:
        # All cells under-powered; report the observed |tau-hat| range across
        # all non-degenerate rows so the reader still sees the effect-size
        # universe relative to the curves.
        nondeg = mde[
            (mde["se_d"].astype(float) > 0)
            & (mde["tau_hat_d"].astype(float).abs() > 0)
        ]
        if not nondeg.empty:
            annot = (
                "All non-degenerate cells under-powered at 0.80 "
                f"(observed |tau-hat|: {abs(nondeg['tau_hat_d']).min():.1f}-"
                f"{abs(nondeg['tau_hat_d']).max():.1f} d)"
            )
        else:
            annot = "No non-degenerate cells available."
    ax.text(0.02, 0.97, annot,
            transform=ax.transAxes, fontsize=7.5, color="0.3",
            ha="left", va="top",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, pad=2))

    ax.set_xlabel("True tau (days)")
    ax.set_ylabel("Power (Pr reject H0 | tau)")
    # Top title removed (caption supplied below figure in DOCX/manuscript).
    ax.set_title("",
                 fontsize=10, loc="left")
    # Extend x-axis to cover the full simulated tau grid so the 0.80-power
    # crossing is visible.
    ax.set_xlim(-1.0, tau_max + 2.0)
    ax.set_ylim(0, 1.02)
    xtick_step = 10 if tau_max <= 100 else 20
    ax.set_xticks(range(0, int(tau_max) + 1, xtick_step))
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    ax.grid(axis="y", lw=0.3, alpha=0.5)

    fig.tight_layout()
    outdir.mkdir(parents=True, exist_ok=True)
    fig.savefig(outdir / "fig5_power_curves.pdf",
                bbox_inches="tight", pad_inches=0.05)
    fig.savefig(outdir / "fig5_power_curves.png",
                bbox_inches="tight", pad_inches=0.05, dpi=300)
    plt.close(fig)
    print(f"wrote {outdir}/fig5_power_curves.pdf, .png")


# ============================================================
# 4. Driver
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--did-static",
                    default="analysis/results/did_static.csv")
    ap.add_argument("--wcr",
                    default="analysis/results/wild_bootstrap.csv")
    ap.add_argument("--outdir",
                    default="analysis/results")
    ap.add_argument("--figdir",
                    default="figures")
    ap.add_argument("--reps", type=int, default=999,
                    help="Monte-Carlo reps per grid point")
    args = ap.parse_args()

    out = Path(args.outdir)
    fig = Path(args.figdir)
    out.mkdir(parents=True, exist_ok=True)

    print("=== MDE (analytical, t-distribution, df=G-1=7) ===")
    mde = build_mde_table(Path(args.did_static), Path(args.wcr))
    print(mde.to_string(index=False))
    mde.to_csv(out / "power_mde.csv", index=False)
    print(f"wrote {out}/power_mde.csv")

    print("\n=== Power curves (Monte-Carlo, %d reps) ===" % args.reps)
    curves = build_power_curves(reps=args.reps)
    curves.to_csv(out / "power_curves.csv", index=False)
    print(f"wrote {out}/power_curves.csv")

    print("\n=== Figure 5 ===")
    make_figure(curves, mde, fig)

    # JSON summary for §3.Y.4 narrative
    g8 = curves[curves["G"] == 8].copy()
    # find smallest tau where power >= 0.80 at G=8
    g8_sorted = g8.sort_values("true_tau_d")
    above = g8_sorted[g8_sorted["power"] >= 0.80]
    tau80 = float(above["true_tau_d"].iloc[0]) if len(above) else None

    summary = {
        "G": 8,
        "df_clusters": 7,
        "alpha": 0.05,
        "MDE_80_2sided_range_d": [
            float(mde["MDE_2sided_d"].min()),
            float(mde["MDE_2sided_d"].max()),
        ],
        "tau_for_power_0_80_at_G8_d": tau80,
        "n_detectable_cells": int((mde["detectable"] == "yes").sum()),
        "n_total_cells":      int(len(mde)),
    }
    with open(out / "power_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nSummary:", json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

"""
06_figures.py — publication figures for the RiceBaCI manuscript.

Generates:
    figures/fig2_did_coefplot.{png,pdf}      — static DiD coefficients across
                                              (pipeline × metric) with 95 % CIs
    figures/fig3_event_study.{png,pdf}       — event-study leads/lags for SOS
                                              (raw vs corrected, faceted)
    figures/fig4_district_sos_panel.{png,pdf} — per-district SOS time series,
                                              treatment vs control, with
                                              cyclone-year vertical lines

Inputs:
    analysis/results/did_static.csv   (from Module 05)
    analysis/results/event_study.csv  (from Module 05)
    analysis/synthetic_baci_panel.csv (or real GEE export — pass via --panel)

Style:
    Publication-friendly: Helvetica/Arial fallback, 8 pt minor / 10 pt
    body / 12 pt title; vector PDFs for journal upload; PNG @ 300 dpi for
    review.  Colour-blind safe palette (Okabe-Ito).

Author: Supranab Panda
Date  : 2026-05-05
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# ---------------------------------------------------------------------------
# Style — Okabe-Ito + journal-friendly defaults
# ---------------------------------------------------------------------------
rcParams.update({
    "font.family":      ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size":        10,
    "axes.titlesize":   12,
    "axes.labelsize":   10,
    "xtick.labelsize":  9,
    "ytick.labelsize":  9,
    "legend.fontsize":  9,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.linewidth":    0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "savefig.dpi":       300,
    "savefig.bbox":      "tight",
    "pdf.fonttype":      42,    # editable text in PDF
    "ps.fonttype":       42,
})

OKABE_ITO = {
    "raw":         "#E69F00",   # orange
    "corrected":   "#0072B2",   # blue
    "treatment":   "#D55E00",   # vermilion
    "control":     "#009E73",   # green
    "neutral":     "#666666",
}


# ---------------------------------------------------------------------------
# Figure 2 — DiD coefficient plot
# ---------------------------------------------------------------------------
def fig_did_coefplot(static_df: pd.DataFrame, out_dir: Path) -> None:
    metrics = ["SOS", "POS", "EOS"]
    pipelines = ["raw", "corrected"]

    fig, ax = plt.subplots(figsize=(6.5, 3.8))

    y_pos = []
    y_lab = []
    yi = 0
    for met in metrics:
        for pipe in pipelines:
            row = static_df.query("pipeline == @pipe and metric == @met")
            if row.empty:
                continue
            r = row.iloc[0]
            err_lo = r["tau_days"] - r["ci_lo_95"]
            err_hi = r["ci_hi_95"] - r["tau_days"]
            ax.errorbar(
                r["tau_days"], yi,
                xerr=[[err_lo], [err_hi]],
                fmt="o", color=OKABE_ITO[pipe],
                ecolor=OKABE_ITO[pipe],
                capsize=3, markersize=6, lw=1.4,
                label=pipe if yi < 2 else None,
            )
            # Annotate p-value
            star = ""
            if r["p_value"] < 0.001:    star = "***"
            elif r["p_value"] < 0.01:   star = "**"
            elif r["p_value"] < 0.05:   star = "*"
            ax.text(r["ci_hi_95"] + 0.3, yi,
                    f"{r['tau_days']:+.2f} {star}",
                    va="center", fontsize=8.5, color=OKABE_ITO[pipe])
            y_pos.append(yi)
            y_lab.append(f"{met} ({pipe})")
            yi += 1
        yi += 0.4   # gap between metric groups

    ax.axvline(0, color="black", lw=0.6, ls=":")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_lab)
    ax.invert_yaxis()
    ax.set_xlabel("DiD coefficient τ (days)")
    ax.set_title("Treatment effect of pre-Kharif cyclones on rice phenology",
                 loc="left")
    ax.legend(title="Pipeline", loc="lower right", frameon=False)
    ax.grid(axis="x", alpha=0.25, lw=0.4)

    fig.text(0.01, -0.03,
             "*** p<0.001 · ** p<0.01 · * p<0.05.  "
             "Whiskers: 95 % CI, district-clustered SEs (n=8).",
             fontsize=8, color="#444")

    for ext in ("png", "pdf"):
        fig.savefig(out_dir / f"fig2_did_coefplot.{ext}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 3 — Event study (SOS only, raw vs corrected as facets)
# ---------------------------------------------------------------------------
def fig_event_study(es_df: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(8.5, 4.0), sharey=True)
    fig.subplots_adjust(top=0.82, bottom=0.18)

    for ax, pipe in zip(axes, ["raw", "corrected"]):
        sub = (es_df.query("pipeline == @pipe and metric == 'SOS'")
                    .sort_values("event_k"))
        if sub.empty:
            continue
        ax.errorbar(
            sub["event_k"], sub["beta"],
            yerr=[sub["beta"] - sub["ci_lo_95"], sub["ci_hi_95"] - sub["beta"]],
            fmt="o-", color=OKABE_ITO[pipe],
            capsize=3, lw=1.2, markersize=5,
        )
        ax.axhline(0, color="black", lw=0.6, ls=":")
        ax.axvline(-0.5, color=OKABE_ITO["treatment"], lw=0.8, ls="--",
                   alpha=0.6)
        ax.set_xlabel("Event time (years from first treatment)")
        ax.set_title(f"SOS — {pipe}", loc="left", pad=8)
        ax.grid(axis="y", alpha=0.25, lw=0.4)

    axes[0].set_ylabel("β (days, vs k = −1)")
    fig.suptitle("Dynamic treatment effects on Start-of-Season",
                 x=0.02, y=0.97, ha="left", fontsize=12)

    fig.text(0.01, 0.02,
             "Reference period k = −1 (year before first treatment landfall, 2018). "
             "Whiskers: 95 % CI.",
             fontsize=8, color="#444")

    for ext in ("png", "pdf"):
        fig.savefig(out_dir / f"fig3_event_study.{ext}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 4 — Per-district SOS time series, treatment vs control
# ---------------------------------------------------------------------------
TREAT_LANDFALL = {2019: "Fani", 2020: "Amphan", 2021: "Yaas"}


def fig_district_panel(panel_df: pd.DataFrame, out_dir: Path,
                        pipeline: str = "corrected", metric: str = "SOS") -> None:
    sub = panel_df.query(
        "pipeline == @pipeline and metric == @metric"
    ).copy()

    treat_d = sorted(sub.query("cyclone_exposure == 'coastal_treatment'")
                        ["district"].unique())
    ctrl_d  = sorted(sub.query("cyclone_exposure == 'inland_control'")
                        ["district"].unique())

    fig, axes = plt.subplots(2, 1, figsize=(7.2, 5.2), sharex=True, sharey=True)

    for ax, dlist, title, colour in [
        (axes[0], treat_d, "Coastal treatment districts", OKABE_ITO["treatment"]),
        (axes[1], ctrl_d,  "Inland control districts",     OKABE_ITO["control"]),
    ]:
        for d in dlist:
            ddf = sub[sub["district"] == d].sort_values("year")
            ax.plot(ddf["year"], ddf["median_doy"],
                    "-o", color=colour, alpha=0.55, markersize=3.5,
                    lw=1.0, label=d)

        # Mean line per group
        grp = (sub[sub["district"].isin(dlist)]
                  .groupby("year")["median_doy"].mean())
        ax.plot(grp.index, grp.values, "-",
                color=colour, lw=2.4, alpha=0.95)

        for y, name in TREAT_LANDFALL.items():
            ax.axvline(y, color="#888", lw=0.6, ls=":")
            ax.text(y, ax.get_ylim()[1] if False else 0,
                    "", color="#888")

        ax.set_title(title, loc="left", fontsize=10.5)
        ax.set_ylabel(f"{metric} (DOY)")
        ax.grid(axis="y", alpha=0.25, lw=0.4)
        ax.legend(ncol=3, fontsize=7.5, loc="lower right",
                  frameon=False, handlelength=1.2)

    # Annotate cyclone landfalls on top axis
    ax_top = axes[0].twiny() if False else axes[0]
    for y, name in TREAT_LANDFALL.items():
        ax_top.text(y, ax_top.get_ylim()[1],
                    name, color="#555",
                    ha="center", va="bottom", fontsize=8)

    axes[1].set_xlabel("Year")
    fig.suptitle(f"District-level {metric} — {pipeline} pipeline",
                 x=0.02, ha="left", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    for ext in ("png", "pdf"):
        fig.savefig(out_dir / f"fig4_district_{metric.lower()}_panel.{ext}")
    plt.close(fig)


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel",   default="analysis/synthetic_baci_panel.csv")
    ap.add_argument("--results", default="analysis/results")
    ap.add_argument("--outdir",  default="figures")
    args = ap.parse_args()

    panel_path = Path(args.panel)
    res_dir    = Path(args.results)
    out_dir    = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    panel_df  = pd.read_csv(panel_path)
    static_df = pd.read_csv(res_dir / "did_static.csv")
    es_df     = pd.read_csv(res_dir / "event_study.csv")

    fig_did_coefplot(static_df, out_dir)
    fig_event_study(es_df, out_dir)
    fig_district_panel(panel_df, out_dir, pipeline="corrected", metric="SOS")
    fig_district_panel(panel_df, out_dir, pipeline="raw",       metric="SOS")

    print(f"wrote figures to {out_dir}/")
    for p in sorted(out_dir.glob("fig[2-4]*")):
        print(f"  {p}")


if __name__ == "__main__":
    main()

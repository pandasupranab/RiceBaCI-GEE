"""
Build Figure 5 — Event study (k = 0..5, reference k=0 = 2019/Cyclone Fani).

Pattern matches Figures 2 and 3:
- Bigger fonts (font.size=18, axes labels=22)
- NO title (caption carries it)
- 1000 dpi JPG (embedded) + PDF vector archive + PNG legacy

Inputs (read verbatim, never re-derived):
  analysis/v22/results/event_study_v22.csv

Outputs:
  figures/fig6_event_study.jpg  (1000 dpi, embedded in manuscript)
  figures/fig6_event_study.pdf  (vector archive)
  figures/fig6_event_study.png  (legacy 300 dpi)
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

ROOT = Path("/tmp/RiceBaCI-fresh")
OUT  = Path("/home/user/workspace/rse_final/figures")
OUT.mkdir(parents=True, exist_ok=True)

# Bigger-font rc — matched to Figures 2 and 3
mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 18,
    "axes.titlesize": 24,
    "axes.labelsize": 22,
    "xtick.labelsize": 18,
    "ytick.labelsize": 18,
    "legend.fontsize": 22,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 1.2,
    "xtick.major.width": 1.2,
    "ytick.major.width": 1.2,
})

C_POST = "#1f77b4"   # blue — post-QC (matched to Figures 2 and 3 v2.0 colour)
C_ZERO = "#444444"
C_TREAT_BAND = "#fff2e6"  # very light orange to mark cyclone treatment years (k=1,2)

# Year mapping: k = 0..5 corresponds to 2019..2024
YEAR_OF_K = {0: 2019, 1: 2020, 2: 2021, 3: 2022, 4: 2023, 5: 2024}
TREAT_KS = {1, 2}  # 2020 Amphan, 2021 Yaas (k=0 2019 Fani is reference)

# ---- Load canonical event-study results -----------------------------------
es = pd.read_csv(ROOT / "analysis" / "v22" / "results" / "event_study_v22.csv")
print(es)

# ---- Plot: 3-panel horizontal (SOS | POS | EOS) ---------------------------
fig, axes = plt.subplots(1, 3, figsize=(20, 8), sharey=True)
metrics = ["SOS", "POS", "EOS"]

for ax, metric in zip(axes, metrics):
    sub = es[es["metric"] == metric].sort_values("event_k").reset_index(drop=True)

    # Light treatment-year bands (k=1, k=2)
    for k in TREAT_KS:
        ax.axvspan(k - 0.4, k + 0.4, color=C_TREAT_BAND, alpha=0.7, zorder=0)

    # Zero reference line
    ax.axhline(0, color=C_ZERO, linestyle="--", linewidth=1.2, alpha=0.7, zorder=1)

    # Connect points with line; errorbars for CI
    ax.errorbar(
        sub["event_k"], sub["beta"],
        yerr=[sub["beta"] - sub["ci_lo_95"], sub["ci_hi_95"] - sub["beta"]],
        fmt="o-", color=C_POST, ecolor=C_POST, capsize=8, capthick=2.0,
        markersize=14, markeredgecolor="white", markeredgewidth=1.5,
        linewidth=2.0, elinewidth=2.2, zorder=3,
    )

    # Title (panel label only — no figure-level title)
    ax.set_title(metric, fontweight="bold", color=C_POST, pad=12)

    # X-axis: event time k with year subscripts
    ax.set_xticks(range(0, 6))
    ax.set_xticklabels([f"{k}\n({YEAR_OF_K[k]})" for k in range(0, 6)])
    ax.set_xlabel("Event time k (year)", fontweight="bold", labelpad=8)
    ax.set_xlim(-0.5, 5.5)
    ax.grid(axis="y", linestyle=":", alpha=0.4)

# Shared y-axis label on leftmost panel only
axes[0].set_ylabel(r"$\hat\beta_k$ (days, reference $k=0$)", fontweight="bold")

# Custom legend — single, top-right of figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
legend_handles = [
    Line2D([0], [0], color=C_POST, marker="o", markersize=12, markeredgecolor="white",
           markeredgewidth=1.5, linewidth=2.0,
           label=r"$\hat\beta_k$ ± 95% cluster-robust CI"),
    Patch(facecolor=C_TREAT_BAND, edgecolor="none",
          label="Cyclone treatment year (k = 1, 2)"),
    Line2D([0], [0], color=C_ZERO, linestyle="--", linewidth=1.2,
           label=r"$\beta = 0$ (null effect)"),
]
leg = fig.legend(
    handles=legend_handles, loc="lower center", ncol=3,
    bbox_to_anchor=(0.5, -0.04), frameon=True, framealpha=0.95,
    edgecolor="#cccccc", fontsize=22, handlelength=2.8,
    handletextpad=0.9, columnspacing=2.2, borderpad=0.9,
)
for h in leg.legend_handles:
    if hasattr(h, "set_markersize"):
        h.set_markersize(18)

plt.tight_layout(rect=[0, 0.09, 1, 1])

# Outputs — JPG (embedded), PDF (vector), PNG (legacy 300 dpi)
fig.savefig(OUT / "fig6_event_study.jpg", dpi=1000,
            pil_kwargs={"quality": 95}, bbox_inches="tight")
fig.savefig(OUT / "fig6_event_study.pdf", bbox_inches="tight")
fig.savefig(OUT / "fig6_event_study.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"Saved Fig 4 → {OUT}/fig6_event_study.{{jpg,pdf,png}}")

"""
Build Figure 4 — Static DiD coefficient plot (Model 1, v2.0 QC-passing panel).

Pattern matches Figure 4 (build_fig4_qc_distributions.py):
- Bigger fonts (font.size=18, axes labels=22)
- NO title (caption carries that information)
- 1000 dpi raster outputs: JPG (embedded) + PDF (vector archive) + PNG (legacy)

Inputs (read verbatim, never re-derived):
  analysis/v22/results/did_static_v22.csv

Outputs:
  figures/fig5_did_coefplot.jpg  (1000 dpi, embedded in manuscript)
  figures/fig5_did_coefplot.pdf  (vector archive)
  figures/fig5_did_coefplot.png  (legacy 300 dpi)
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

ROOT = Path("/tmp/RiceBaCI-fresh")
OUT  = Path("/home/user/workspace/rse_final/figures")
OUT.mkdir(parents=True, exist_ok=True)

# Bigger-font rc — matched to Figure 2 treatment
mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 18,
    "axes.titlesize": 22,
    "axes.labelsize": 22,
    "xtick.labelsize": 18,
    "ytick.labelsize": 20,
    "legend.fontsize": 16,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 1.2,
    "xtick.major.width": 1.2,
    "ytick.major.width": 1.2,
})

C_POST = "#1f77b4"   # blue — post-QC (matched to Figure 2 v2.0 colour)
C_ZERO = "#444444"

# ---- Load canonical static DiD results ------------------------------------
did = pd.read_csv(ROOT / "analysis" / "v22" / "results" / "did_static_v22.csv")
# Enforce expected metric order
did["metric"] = pd.Categorical(did["metric"], categories=["SOS", "POS", "EOS"], ordered=True)
did = did.sort_values("metric").reset_index(drop=True)
print(did[["metric", "tau_days", "ci_lo_95", "ci_hi_95", "p_value_wcb"]])

# ---- Plot -----------------------------------------------------------------
fig, ax = plt.subplots(figsize=(14, 8))
y_pos = np.arange(len(did))

ax.errorbar(
    did["tau_days"], y_pos,
    xerr=[did["tau_days"] - did["ci_lo_95"], did["ci_hi_95"] - did["tau_days"]],
    fmt="o", color=C_POST, ecolor=C_POST, capsize=10, capthick=2.0,
    markersize=18, markeredgecolor="white", markeredgewidth=1.5,
    elinewidth=3.0, label=r"$\hat\tau$ ± 95% wild-cluster bootstrap CI",
)

ax.axvline(0, color=C_ZERO, linestyle="--", linewidth=1.2, alpha=0.8)

ax.set_yticks(y_pos)
ax.set_yticklabels(did["metric"], fontweight="bold")
ax.invert_yaxis()
ax.set_xlabel(r"DiD coefficient $\hat\tau$ (days)", fontweight="bold")

# Annotate point estimates + p_wcb to the right of each CI
xmin = did["ci_lo_95"].min()
xmax = did["ci_hi_95"].max()
xpad_right = 18.0
for i, row in did.iterrows():
    ax.text(
        row["ci_hi_95"] + 1.5, i - 0.18,
        f"$\\hat\\tau$ = {row['tau_days']:+.2f} d",
        va="center", ha="left", fontsize=18, fontweight="bold", color=C_POST,
    )
    ax.text(
        row["ci_hi_95"] + 1.5, i + 0.18,
        f"$p_{{\\mathrm{{WCB}}}}$ = {row['p_value_wcb']:.3f}",
        va="center", ha="left", fontsize=16, color="#333333",
    )

# Annotate CI bounds at endpoints
for i, row in did.iterrows():
    ax.text(row["ci_lo_95"], i - 0.42, f"{row['ci_lo_95']:+.1f}",
            ha="center", va="bottom", fontsize=14, color="#555555")
    ax.text(row["ci_hi_95"], i - 0.42, f"{row['ci_hi_95']:+.1f}",
            ha="center", va="bottom", fontsize=14, color="#555555")

# Zero-reference label
ax.text(0, -0.55, r"$\tau = 0$", ha="center", va="bottom",
        fontsize=15, color=C_ZERO, fontweight="bold")

ax.set_xlim(xmin - 6, xmax + xpad_right)
ax.set_ylim(len(did) - 0.5, -0.85)
ax.grid(axis="x", linestyle=":", alpha=0.4)
ax.legend(loc="lower right", framealpha=0.95, edgecolor="#cccccc")

plt.tight_layout()

# Outputs — JPG (embedded in manuscript), PDF (vector archive), PNG (legacy)
fig.savefig(OUT / "fig5_did_coefplot.jpg", dpi=1000, pil_kwargs={"quality": 95}, bbox_inches="tight")
fig.savefig(OUT / "fig5_did_coefplot.pdf", bbox_inches="tight")
fig.savefig(OUT / "fig5_did_coefplot.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"Saved Fig 3 → {OUT}/fig5_did_coefplot.{{jpg,pdf,png}}")

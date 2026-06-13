"""Rebuild Figure 2 with much larger text and 1000 dpi PNG output."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# Bump base font sizes globally (much larger)
mpl.rcParams.update({
    "font.size": 18,
    "axes.titlesize": 22,
    "axes.labelsize": 18,
    "xtick.labelsize": 15,
    "ytick.labelsize": 15,
    "legend.fontsize": 16,
    "figure.titlesize": 24,
})

C_PRE = "#c44e52"   # red
C_POST = "#4c72b0"  # blue

ROOT = Path("/tmp/RiceBaCI-fresh")
OUT = ROOT / "rse_v2" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# --- Pre-QC (v1.0.2 raw) district-year values ---
v1 = pd.read_csv(ROOT / "analysis" / "baci_panel_real_v1.csv")
v1r = v1[v1["pipeline"] == "raw"].copy()
v102_sos_vals = v1r[v1r["metric"] == "SOS"]["median_doy"].dropna().to_numpy()
v102_pos_vals = v1r[v1r["metric"] == "POS"]["median_doy"].dropna().to_numpy()
v102_eos_vals = v1r[v1r["metric"] == "EOS"]["median_doy"].dropna().to_numpy()

def mode_share(arr):
    s = pd.Series(np.round(arr).astype(int)).value_counts(normalize=True)
    return float(s.iloc[0])

ms_pre_sos = mode_share(v102_sos_vals)
ms_pre_pos = mode_share(v102_pos_vals)
ms_pre_eos = mode_share(v102_eos_vals)
mode_doy_pre_eos = pd.Series(np.round(v102_eos_vals).astype(int)).value_counts().index[0]

# --- Post-QC (v2.0) cell-level fits ---
import glob
fits = pd.concat([pd.read_parquet(p) for p in glob.glob(str(ROOT/"analysis/v22/fits/*.parquet"))],
                 ignore_index=True)
# Apply same QC filter as DiD-cell pipeline (years 2019-2024 + fit_reason empty)
import sys
sys.path.insert(0, str(ROOT/"analysis/v22"))
from did_cell_level_v22 import load_cell_panel
cell = load_cell_panel()
v22_sos = cell["sos"].dropna().to_numpy()
v22_pos = cell["pos"].dropna().to_numpy()
v22_eos = cell["eos"].dropna().to_numpy()

ms_post_sos = mode_share(v22_sos)
ms_post_pos = mode_share(v22_pos)
ms_post_eos = mode_share(v22_eos)

print(f"v1 mode-shares: SOS {ms_pre_sos:.3f}, POS {ms_pre_pos:.3f}, EOS {ms_pre_eos:.3f}")
print(f"v22 cell mode-shares: SOS {ms_post_sos:.3f}, POS {ms_post_pos:.3f}, EOS {ms_post_eos:.3f}")

# ============================================================================
# FIGURE 2 — bigger fonts, larger canvas, 1000 dpi PNG
# ============================================================================
fig, axes = plt.subplots(2, 3, figsize=(16, 10), sharey=False)

metrics = [
    ("SOS", v102_sos_vals, v22_sos, ms_pre_sos, ms_post_sos, (100, 280)),
    ("POS", v102_pos_vals, v22_pos, ms_pre_pos, ms_post_pos, (180, 340)),
    ("EOS", v102_eos_vals, v22_eos, ms_pre_eos, ms_post_eos, (260, 380)),
]

for col, (name, pre_vals, post_vals, ms_pre, ms_post, xlim) in enumerate(metrics):
    ax_top = axes[0, col]
    ax_bot = axes[1, col]
    bins = np.arange(xlim[0], xlim[1] + 5, 5)

    ax_top.hist(pre_vals, bins=bins, color=C_PRE, alpha=0.85, edgecolor="white", linewidth=0.6)
    ax_top.set_xlim(xlim)
    ax_top.set_ylabel("Pre-QC count" if col == 0 else "", fontweight="bold")
    ax_top.set_title(f"{name}", fontweight="bold")
    ax_top.text(0.5, 0.5,
                f"mode share = {ms_pre:.1%}\nn = {len(pre_vals)}",
                transform=ax_top.transAxes, ha="center", va="center",
                fontsize=16, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=C_PRE, lw=1.4))
    if name == "EOS":
        ax_top.axvline(mode_doy_pre_eos, color="black", linestyle="--", linewidth=1.5, alpha=0.7)
        # Arrow points to the top of the DOY 349 spike (data coordinates)
        spike_top_y = ax_top.get_ylim()[1] * 0.95
        ax_top.annotate(f"DOY {int(mode_doy_pre_eos)} spike\n(fitting-window\nboundary)",
                        xy=(mode_doy_pre_eos, spike_top_y), xycoords="data",
                        xytext=(0.05, 0.22), textcoords="axes fraction",
                        fontsize=12, ha="left", va="center", fontweight="bold",
                        arrowprops=dict(arrowstyle="->", color="black", lw=1.2,
                                        connectionstyle="arc3,rad=-0.2"))

    ax_bot.hist(post_vals, bins=bins, color=C_POST, alpha=0.85, edgecolor="white", linewidth=0.6)
    ax_bot.set_xlim(xlim)
    ax_bot.set_xlabel("Day of Year (DOY)", fontweight="bold")
    ax_bot.set_ylabel("Post-QC count" if col == 0 else "", fontweight="bold")
    ax_bot.text(0.5, 0.5,
                f"mode share = {ms_post:.1%}\nn = {len(post_vals)}",
                transform=ax_bot.transAxes, ha="center", va="center",
                fontsize=16, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=C_POST, lw=1.4))

plt.tight_layout(rect=[0.07, 0, 1, 1])

# Place row labels AFTER tight_layout. Use the y-axis-label position of axes[0,0] / axes[1,0]
# to set x — this guarantees the row labels sit immediately left of the y-axis labels.
fig.canvas.draw()
top_pos = axes[0, 0].get_position()
bot_pos = axes[1, 0].get_position()
top_y = (top_pos.y0 + top_pos.y1) / 2
bot_y = (bot_pos.y0 + bot_pos.y1) / 2
# Shifted closer to the 0.07 tight_layout boundary
label_x = 0.045
fig.text(label_x, top_y, "Pre-QC (v1.0.2)\ndistrict aggregates", ha="center", va="center",
         fontsize=17, fontweight="bold", color=C_PRE, rotation=90)
fig.text(label_x, bot_y, "Post-QC (v2.0)\ncell-level fits", ha="center", va="center",
         fontsize=17, fontweight="bold", color=C_POST, rotation=90)
fig.savefig(OUT / "fig4_qc_distributions.pdf")
fig.savefig(OUT / "fig4_qc_distributions.png", dpi=1000)
plt.close(fig)
print(f"Saved Fig 2 PNG (1000 dpi) and PDF to {OUT}")

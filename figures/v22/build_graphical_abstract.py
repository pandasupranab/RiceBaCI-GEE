"""
Graphical Abstract — RiceBaCI v2.0
Layout follows Elsevier's standard 3-panel template:
  Title bar | Take-home message | Point1 (context) | Point2 (method) | Point3 (outcome)
1000 dpi PDF + JPG.
All numbers verified against:
  /tmp/RiceBaCI-fresh/analysis/baci_panel_real_v1.csv   (pre-QC)
  /tmp/RiceBaCI-fresh/analysis/baci_panel_real_v22.csv  (post-QC)
  /tmp/RiceBaCI-fresh/analysis/v22/results/did_static_v22.csv
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd

# ---------- Design tokens ----------
ACCENT  = "#01696F"   # Hydra Teal (project accent)
ACCENT2 = "#A84B2F"   # Terra/rust for "fail" / pre-QC
INK     = "#28251D"
MUTED   = "#7A7974"
PAPER   = "#FFFFFF"
SUR_OK  = "#E6F1F2"   # very light teal tint for "pass"
SUR_BAD = "#F6E4DE"   # very light terra tint for "fail"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size":   9,
    "axes.edgecolor": INK,
    "axes.linewidth": 0.8,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "pdf.fonttype": 42,    # editable text in vector
    "ps.fonttype":  42,
})

# ---------- Verified data ----------
df_v1  = pd.read_csv("/tmp/RiceBaCI-fresh/analysis/baci_panel_real_v1.csv")
df_v22 = pd.read_csv("/tmp/RiceBaCI-fresh/analysis/baci_panel_real_v22.csv")
df_did = pd.read_csv("/tmp/RiceBaCI-fresh/analysis/v22/results/did_static_v22.csv")

# Pre-QC EOS distribution (most visually striking, 72.7% spike at DOY 349)
preqc_eos = (
    df_v1.query("pipeline == 'raw' and metric == 'EOS'")
         .groupby(["district", "year"], as_index=False)["median_doy"].first()["median_doy"]
)
# Post-QC EOS distribution
postqc_eos = df_v22["eos_median"].dropna()

did_lookup = {row.metric: row for row in df_did.itertuples()}

# ---------- Figure ----------
# Standard Elsevier graphical-abstract aspect ratio is ~ 5:3 (1328 × 531 px min, but
# higher is fine). We render at 1000 dpi so vector + raster both clean.
FIG_W, FIG_H = 13.3, 7.5                # inches
fig = plt.figure(figsize=(FIG_W, FIG_H), facecolor=PAPER, dpi=200)

# Master grid (height ratios mirror the template: title / takeaway / panels / footer)
gs = gridspec.GridSpec(
    nrows=4, ncols=3,
    height_ratios=[0.85, 0.55, 4.8, 0.55],
    width_ratios=[1, 1, 1],
    hspace=0.30, wspace=0.18,
    left=0.025, right=0.975, top=0.96, bottom=0.04,
)

# =====================================================================
# Title bar (row 0, spans all cols)
# =====================================================================
ax_title = fig.add_subplot(gs[0, :])
ax_title.set_axis_off()
ax_title.add_patch(FancyBboxPatch(
    (0.005, 0.05), 0.99, 0.90,
    boxstyle="round,pad=0.005,rounding_size=0.012",
    linewidth=1.6, edgecolor=ACCENT, facecolor=PAPER,
    transform=ax_title.transAxes, clip_on=False,
))
ax_title.text(
    0.5, 0.52,
    "Quantisation artefacts in Sentinel-2 rice phenology:",
    ha="center", va="center", transform=ax_title.transAxes,
    fontsize=18, fontweight="bold", color=INK,
)
ax_title.text(
    0.5, 0.18,
    "a reproducible QC framework for cyclone-impact studies",
    ha="center", va="center", transform=ax_title.transAxes,
    fontsize=13, color=INK,
)

# =====================================================================
# Take-home message (row 1, spans all cols)
# =====================================================================
ax_take = fig.add_subplot(gs[1, :])
ax_take.set_axis_off()
ax_take.add_patch(FancyBboxPatch(
    (0.005, 0.05), 0.99, 0.90,
    boxstyle="round,pad=0.005,rounding_size=0.012",
    linewidth=0.8, edgecolor=MUTED, facecolor=PAPER,
    linestyle=(0, (4, 3)),
    transform=ax_take.transAxes, clip_on=False,
))
ax_take.text(
    0.5, 0.5,
    "A three-gate QC framework collapses boundary spikes from 72.7% → 8.3% "
    "and turns false-positive cyclone effects into a robust null DiD.",
    ha="center", va="center", transform=ax_take.transAxes,
    fontsize=13, color=ACCENT, fontweight="medium", style="italic",
)

# =====================================================================
# Panel helper
# =====================================================================
def panel_frame(ax, title_text, tint=PAPER):
    ax.set_axis_off()
    ax.add_patch(FancyBboxPatch(
        (0.005, 0.005), 0.99, 0.99,
        boxstyle="round,pad=0.005,rounding_size=0.018",
        linewidth=1.6, edgecolor=ACCENT, facecolor=tint,
        transform=ax.transAxes, clip_on=False,
    ))
    ax.text(
        0.5, 0.955, title_text,
        ha="center", va="top", transform=ax.transAxes,
        fontsize=15, fontweight="bold", color=INK,
    )

# =====================================================================
# Panel 1 — CONTEXT: pre-QC artefact (row 2, col 0)
# =====================================================================
ax1_outer = fig.add_subplot(gs[2, 0])
panel_frame(ax1_outer, "1.  The problem", tint=SUR_BAD)

# Inset axes for the histogram — positioned in upper half of panel
bb = ax1_outer.get_position()
inset_w = 0.74 * bb.width
inset_h = 0.40 * bb.height
inset_x = bb.x0 + (bb.width - inset_w) / 2
inset_y = bb.y0 + 0.42 * bb.height
ax1 = fig.add_axes([inset_x, inset_y, inset_w, inset_h])
bins = np.arange(260, 366, 5)
ax1.hist(preqc_eos, bins=bins, color=ACCENT2, edgecolor="white", linewidth=0.6, alpha=0.9)
ax1.axvline(349, color=INK, linewidth=0.8, linestyle=":")
ax1.set_xlabel("EOS day-of-year (pre-QC v1.0.2)", fontsize=8.5, labelpad=2)
ax1.set_ylabel("count", fontsize=8.5, labelpad=2)
ax1.tick_params(labelsize=7.5)
ax1.set_xlim(255, 365)
ax1.annotate(
    "72.7% spike\nat DOY 349",
    xy=(349, ax1.get_ylim()[1]*0.85), xytext=(295, ax1.get_ylim()[1]*0.85),
    fontsize=8.5, color=ACCENT2, fontweight="bold",
    ha="center", va="center",
    arrowprops=dict(arrowstyle="->", color=ACCENT2, lw=1.0),
)

# Caption text under the chart (below the histogram x-label)
ax1_outer.text(
    0.5, 0.17,
    "Standard double-logistic fits concentrate\n"
    "72.7% of EOS and 65.6% of POS estimates\n"
    "on single boundary DOYs — artefacts that\n"
    "mimic genuine cyclone signals.",
    ha="center", va="center", transform=ax1_outer.transAxes,
    fontsize=11.5, color=INK,
)

# =====================================================================
# Panel 2 — METHOD: three-gate QC (row 2, col 1)
# =====================================================================
ax2 = fig.add_subplot(gs[2, 1])
panel_frame(ax2, "2.  Three-gate QC", tint=SUR_OK)

# Gate cards — bigger boxes, tighter spacing
gate_specs = [
    ("Gate A",    "Mode-share ≤ 0.20",                "Boundary-spike test"),
    ("Gate B",    "Biological plausibility",          "DOY within agronomic range"),
    ("Gate C",    "Fit quality",                      "R² ≥ 0.70, RMSE ≤ 0.10"),
]
n = len(gate_specs)
card_top  = 0.82
card_h    = 0.20
card_gap  = 0.015
card_x    = 0.06
card_w    = 0.88

for i, (g, headline, sub) in enumerate(gate_specs):
    y = card_top - i * (card_h + card_gap)
    ax2.add_patch(FancyBboxPatch(
        (card_x, y - card_h), card_w, card_h,
        boxstyle="round,pad=0.005,rounding_size=0.015",
        linewidth=1.2, edgecolor=ACCENT, facecolor=PAPER,
        transform=ax2.transAxes, clip_on=False,
    ))
    ax2.text(card_x + 0.04, y - card_h*0.32, g,
             transform=ax2.transAxes, fontsize=13.5,
             fontweight="bold", color=ACCENT, va="center")
    ax2.text(card_x + 0.28, y - card_h*0.32, headline,
             transform=ax2.transAxes, fontsize=12, color=INK, va="center")
    ax2.text(card_x + 0.28, y - card_h*0.70, sub,
             transform=ax2.transAxes, fontsize=10, color=MUTED, va="center",
             style="italic")

ax2.text(
    0.5, 0.13,
    "Each panel observation must pass all three\n"
    "gates before entering the causal panel.",
    ha="center", va="center", transform=ax2.transAxes,
    fontsize=11.5, color=INK,
)

# =====================================================================
# Panel 3 — OUTCOME: post-QC null DiD (row 2, col 2)
# =====================================================================
ax3_outer = fig.add_subplot(gs[2, 2])
panel_frame(ax3_outer, "3.  Robust null", tint=SUR_OK)

bb = ax3_outer.get_position()
inset_w = 0.80 * bb.width
inset_h = 0.40 * bb.height
inset_x = bb.x0 + (bb.width - inset_w) / 2
inset_y = bb.y0 + 0.42 * bb.height
ax3 = fig.add_axes([inset_x, inset_y, inset_w, inset_h])

metrics = ["SOS", "POS", "EOS"]
taus = [did_lookup[m].tau_days for m in metrics]
lo   = [did_lookup[m].ci_lo_95 for m in metrics]
hi   = [did_lookup[m].ci_hi_95 for m in metrics]
errs = np.array([[t - l for t, l in zip(taus, lo)],
                 [h - t for t, h in zip(taus, hi)]])
y_pos = np.arange(len(metrics))

ax3.errorbar(
    taus, y_pos, xerr=errs, fmt="o",
    color=ACCENT, ecolor=ACCENT, elinewidth=1.4,
    markersize=7, capsize=3, markeredgecolor="white", markeredgewidth=0.8,
)
ax3.axvline(0, color=INK, linewidth=0.8, linestyle="--", alpha=0.6)
ax3.set_yticks(y_pos)
ax3.set_yticklabels(metrics, fontsize=9)
ax3.invert_yaxis()
ax3.set_xlabel("DiD effect τ (days)  •  95% CI", fontsize=8.5, labelpad=2)
ax3.tick_params(labelsize=7.5)
# Expand x-range so p-value labels fit fully inside the plot box
ax3.set_xlim(-28, 70)
# WCB p-value labels — placed to the right of each error bar, fully inside axes
for yi, m in zip(y_pos, metrics):
    p_wcb = did_lookup[m].p_value_wcb
    tau   = did_lookup[m].tau_days
    hi_v  = did_lookup[m].ci_hi_95
    ax3.text(
        hi_v + 2, yi,
        f"τ = {tau:+.1f} d   p$_{{WCB}}$ = {p_wcb:.2f}",
        ha="left", va="center", fontsize=7.8, color=INK,
    )

ax3_outer.text(
    0.5, 0.17,
    "After QC, all three phenometrics return null\n"
    "(p$_{WCB}$ > 0.38).  The QC framework eliminates\n"
    "the false positives the artefact created.",
    ha="center", va="center", transform=ax3_outer.transAxes,
    fontsize=11.5, color=INK,
)

# =====================================================================
# Footer (row 3, spans all cols) — minimal: authors + repo handles
# =====================================================================
ax_foot = fig.add_subplot(gs[3, :])
ax_foot.set_axis_off()
ax_foot.add_patch(Rectangle(
    (0.005, 0.05), 0.99, 0.90,
    linewidth=0.6, edgecolor=MUTED, facecolor=PAPER, linestyle=(0, (2, 2)),
    transform=ax_foot.transAxes, clip_on=False,
))
ax_foot.text(
    0.012, 0.5, "Panda S. et al.  •  RiceBaCI-GEE v2.0",
    ha="left", va="center", transform=ax_foot.transAxes,
    fontsize=9, color=INK, fontweight="bold",
)
ax_foot.text(
    0.5, 0.5,
    "Sentinel-2  •  8 districts × 6 years  •  Coastal Odisha, India",
    ha="center", va="center", transform=ax_foot.transAxes,
    fontsize=9, color=MUTED,
)
ax_foot.text(
    0.988, 0.5,
    "Zenodo: 10.5281/zenodo.20587316  •  OSF: 10.17605/OSF.IO/C4MP8",
    ha="right", va="center", transform=ax_foot.transAxes,
    fontsize=8.5, color=MUTED,
)

# ---------- Save ----------
out_pdf = "/home/user/workspace/rse_final/Graphical_Abstract.pdf"
out_jpg = "/home/user/workspace/rse_final/Graphical_Abstract.jpg"
fig.savefig(out_pdf, dpi=1000, bbox_inches="tight", facecolor=PAPER)
fig.savefig(out_jpg, dpi=1000, bbox_inches="tight", facecolor=PAPER)
print("Saved:", out_pdf)
print("Saved:", out_jpg)

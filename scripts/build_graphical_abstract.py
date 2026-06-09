#!/usr/bin/env python3
"""Build the RSE graphical abstract for the RiceBaCI-GEE manuscript.

Output:
    figures/Graphical_Abstract.pdf            (vector PDF, 13.28 x 5.31 cm)
    figures/Graphical_Abstract_1000dpi.png    (1000 DPI raster sidecar)

Headline numbers from Pass 31 manuscript:
    tau_raw_SOS       = +15.289 d  (WCR 95% CI -54.02, +84.60)
    tau_corrected_SOS = +15.108 d  (WCR 95% CI -54.14, +84.36)
    tau_corrected_EOS = -0.239 d   (WCR 95% CI -0.92, +0.44)
    RF OA = 0.990 full-feature, 0.844 SAR-only, 5-fold CV 0.831
    n = 480 labels
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.lines import Line2D
import numpy as np
from pathlib import Path
import os

ROOT = Path("/home/user/workspace/RiceBaCI-GEE")
OUT_PDF = ROOT / "figures" / "Graphical_Abstract.pdf"
OUT_PNG = ROOT / "figures" / "Graphical_Abstract_1000dpi.png"

# Use slightly larger canvas (still RSE-compliant — RSE allows up to ~17 cm wide)
# Standard RSE graphical abstract: aspect ~ 2.5:1 (13 wide x 5 tall) but the
# RSE submission guide also accepts square or up to 2:1 aspect. We'll go a
# little taller than the minimum to give room for legible labels at 5 cm height.
W_CM, H_CM = 13.28, 5.80
W_IN, H_IN = W_CM / 2.54, H_CM / 2.54

# Palette
TEAL    = "#01696F"
ORANGE  = "#E07B00"
CHARCOAL= "#222222"
BG      = "#FAFAFA"
LIGHT_TEAL = "#7FB7BA"
LIGHT_ORG  = "#F0B070"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 6.0,
    "axes.linewidth": 0.5,
    "axes.edgecolor": CHARCOAL,
    "text.color": CHARCOAL,
    "axes.labelcolor": CHARCOAL,
    "xtick.color": CHARCOAL,
    "ytick.color": CHARCOAL,
})

fig = plt.figure(figsize=(W_IN, H_IN), dpi=1000)
fig.patch.set_facecolor(BG)

# Title strip: 10% of height
TITLE_H = 0.11
ax_title = fig.add_axes([0, 1.0 - TITLE_H, 1, TITLE_H])
ax_title.set_facecolor(TEAL)
ax_title.set_xticks([]); ax_title.set_yticks([])
for s in ax_title.spines.values(): s.set_visible(False)
ax_title.text(0.5, 0.5,
    "Decoupling cyclone storm-surge from agronomic flooding in Sentinel-1/2 rice phenology",
    ha="center", va="center", color="white", fontsize=6.6, fontweight="bold",
    transform=ax_title.transAxes)

# Sub-title strip (smaller, white background)
SUB_H = 0.045
ax_sub = fig.add_axes([0, 1.0 - TITLE_H - SUB_H, 1, SUB_H])
ax_sub.set_facecolor(BG)
ax_sub.set_xticks([]); ax_sub.set_yticks([])
for s in ax_sub.spines.values(): s.set_visible(False)
ax_sub.text(0.5, 0.5, "coastal Odisha, 2017–2024",
            ha="center", va="center", fontsize=5.5, color=CHARCOAL, style="italic",
            transform=ax_sub.transAxes)

# Panel band: from y=0.06 to y=0.78
PY0 = 0.07
PY1 = 0.77
PANEL_TITLE_H = 0.05   # in fig coords, reserved above each panel for title

# Panel band: subtract title strip
PY1_AXIS = PY1 - PANEL_TITLE_H

GUTTER = 0.018
PW = (1.0 - 4*GUTTER) / 3.0
P1X = GUTTER
P2X = GUTTER*2 + PW
P3X = GUTTER*3 + PW*2

# Helper: panel title in figure coords (shorter text to avoid overflow)
def panel_title(x_left, x_right, text):
    cx = (x_left + x_right) / 2
    fig.text(cx, PY1 - 0.02, text,
             ha="center", va="top", fontsize=5.8, fontweight="bold", color=CHARCOAL)

# =====================================================================
# PANEL A — THE PROBLEM
# =====================================================================
panel_title(P1X, P1X+PW, "(A) Two flood events  ·  one SAR signal")
axA = fig.add_axes([P1X+0.030, PY0+0.020, PW-0.040, PY1_AXIS - PY0 - 0.010])
axA.set_facecolor("white")
for s in ["top","right"]: axA.spines[s].set_visible(False)
axA.spines["left"].set_linewidth(0.5)
axA.spines["bottom"].set_linewidth(0.5)

doy = np.arange(60, 320, 6)
rng = np.random.default_rng(7)
base_cyc = -8.5 + 0.5*np.sin((doy-60)/45) + rng.normal(0, 0.08, len(doy))
cyc_drop = -3.2 * np.exp(-((doy-141)/14)**2)
y_cyc = base_cyc + cyc_drop
base_agr = -8.2 + 0.5*np.sin((doy-60)/45) + rng.normal(0, 0.08, len(doy))
agr_drop = -3.1 * np.exp(-((doy-200)/14)**2)
y_agr = base_agr + agr_drop

axA.plot(doy, y_cyc, color=ORANGE, lw=0.85)
axA.plot(doy, y_agr, color=TEAL,   lw=0.85)
axA.axvline(141, color=ORANGE, ls=":", lw=0.4, alpha=0.6)
axA.axvline(200, color=TEAL,   ls=":", lw=0.4, alpha=0.6)
axA.text(130, -6.55, "Amphan", color=ORANGE, fontsize=4.4, ha="right", va="bottom", fontweight="bold")
axA.text(212, -6.55, "Transplant", color=TEAL, fontsize=4.4, ha="left", va="bottom", fontweight="bold")

axA.set_xlim(60, 320)
axA.set_ylim(-13.2, -6.0)
axA.set_xlabel("Day of year", fontsize=5.0, labelpad=1.0)
axA.set_ylabel("Sentinel-1 VH (dB)", fontsize=5.0, labelpad=1.0)
axA.tick_params(axis="both", labelsize=4.4, length=1.2, pad=0.8)
axA.set_xticks([60, 140, 220, 300])

leg_handles = [
    Line2D([0],[0], color=ORANGE, lw=0.85, label="Cyclone surge"),
    Line2D([0],[0], color=TEAL,   lw=0.85, label="Agronomic"),
]
axA.legend(handles=leg_handles, loc="lower left", fontsize=4.0,
           frameon=False, handlelength=1.4, borderpad=0.1,
           labelspacing=0.15, handletextpad=0.3)

# =====================================================================
# PANEL B — THE SOLUTION (8-feature RF)
# =====================================================================
panel_title(P2X, P2X+PW, "(B) 8-feature RF classifier")
axB = fig.add_axes([P2X, PY0, PW, PY1_AXIS - PY0])
axB.set_facecolor("white")
axB.set_xlim(0, 1); axB.set_ylim(0, 1)
axB.set_xticks([]); axB.set_yticks([])
for s in axB.spines.values(): s.set_visible(False)

# 8 feature pills stacked in a single column on the left
features = [
    "S1 VH", "S1 VV",
    "S2 NDVI", "S2 NDWI", "S2 LSWI",
    "JRC GSW", "ERA5 Vw", "d(track)",
]
col_w = 0.20
col_x0 = 0.03
pill_h = 0.080
y_top = 0.92
y_gap = 0.010

pill_centres = []  # for arrow targets
for i, label in enumerate(features):
    yc = y_top - i*(pill_h + y_gap) - pill_h/2
    rect = FancyBboxPatch((col_x0, yc - pill_h/2), col_w, pill_h,
                          boxstyle="round,pad=0.003,rounding_size=0.010",
                          linewidth=0.35, edgecolor=TEAL, facecolor=LIGHT_TEAL,
                          alpha=0.85)
    axB.add_patch(rect)
    axB.text(col_x0 + col_w/2, yc, label, ha="center", va="center",
             fontsize=4.0, fontweight="bold", color=CHARCOAL)
    pill_centres.append((col_x0 + col_w, yc))  # right edge

# RF box (centre)
rf_x0, rf_x1 = 0.36, 0.62
rf_y0, rf_y1 = 0.32, 0.82
rfbox = FancyBboxPatch((rf_x0, rf_y0), rf_x1-rf_x0, rf_y1-rf_y0,
                       boxstyle="round,pad=0.008,rounding_size=0.022",
                       linewidth=0.6, edgecolor=CHARCOAL, facecolor=TEAL)
axB.add_patch(rfbox)
cy = (rf_y0+rf_y1)/2
axB.text((rf_x0+rf_x1)/2, cy + 0.15, "Random",
         ha="center", va="center", fontsize=6.0, fontweight="bold", color="white")
axB.text((rf_x0+rf_x1)/2, cy + 0.07, "Forest",
         ha="center", va="center", fontsize=6.0, fontweight="bold", color="white")

# Performance line INSIDE the RF box (below 'Forest', white text)
axB.text((rf_x0+rf_x1)/2, rf_y0 + 0.06,
         "OA 0.990",
         ha="center", va="center", fontsize=4.4, color="white", fontweight="bold")
axB.text((rf_x0+rf_x1)/2, rf_y0 + 0.025,
         "SAR 0.844 · n=480",
         ha="center", va="center", fontsize=3.4, color="white")

# Arrows from pills → RF box
target_y_top = rf_y1 - 0.06
target_y_bot = rf_y0 + 0.06
for i, (sx, sy) in enumerate(pill_centres):
    t = i / max(1, len(pill_centres)-1)
    ty = target_y_top - t*(target_y_top - target_y_bot)
    arr = FancyArrowPatch((sx + 0.004, sy), (rf_x0 - 0.004, ty),
                          arrowstyle="->", mutation_scale=2.5, lw=0.30,
                          color="#999999", shrinkA=0, shrinkB=0)
    axB.add_patch(arr)

# Output chips on right
out_x = 0.74
out_w = 0.23
out_h = 0.18
chip_y_cyc = 0.58
chip_y_agr = 0.25

chip_cyc = FancyBboxPatch((out_x, chip_y_cyc), out_w, out_h,
                          boxstyle="round,pad=0.005,rounding_size=0.015",
                          linewidth=0.5, edgecolor=ORANGE, facecolor=LIGHT_ORG)
chip_agr = FancyBboxPatch((out_x, chip_y_agr), out_w, out_h,
                          boxstyle="round,pad=0.005,rounding_size=0.015",
                          linewidth=0.5, edgecolor=TEAL, facecolor=LIGHT_TEAL)
axB.add_patch(chip_cyc); axB.add_patch(chip_agr)
axB.text(out_x+out_w/2, chip_y_cyc+out_h/2, "Cyclone\nflood",
         ha="center", va="center", fontsize=4.6, fontweight="bold", color=CHARCOAL)
axB.text(out_x+out_w/2, chip_y_agr+out_h/2, "Agronomic\nflood",
         ha="center", va="center", fontsize=4.6, fontweight="bold", color=CHARCOAL)

# Arrows RF → chips (separated vertically to avoid overlap)
arr_c = FancyArrowPatch((rf_x1+0.004, (rf_y0+rf_y1)/2 + 0.08), (out_x-0.004, chip_y_cyc+out_h/2),
                        arrowstyle="->", mutation_scale=4.0, lw=0.50,
                        color=ORANGE)
arr_a = FancyArrowPatch((rf_x1+0.004, (rf_y0+rf_y1)/2 - 0.08), (out_x-0.004, chip_y_agr+out_h/2),
                        arrowstyle="->", mutation_scale=4.0, lw=0.50,
                        color=TEAL)
axB.add_patch(arr_c); axB.add_patch(arr_a)

# =====================================================================
# PANEL C — THE OUTCOME (DiD coefficients)
# =====================================================================
panel_title(P3X, P3X+PW, "(C) BACI-corrected DiD coefficients")
axC = fig.add_axes([P3X+0.038, PY0+0.020, PW-0.048, PY1_AXIS - PY0 - 0.010])
axC.set_facecolor("white")
for s in ["top","right"]: axC.spines[s].set_visible(False)
axC.spines["left"].set_linewidth(0.5)
axC.spines["bottom"].set_linewidth(0.5)

labels = ["SOS (raw)", "SOS (corrected)", "EOS (corrected)"]
taus   = [ 15.289,       15.108,             -0.239]
ci_lo  = [-54.02,       -54.14,             -0.92]
ci_hi  = [ 84.60,        84.36,              0.44]
colors = [ORANGE,        TEAL,               TEAL]

y_pos = np.arange(len(labels))[::-1]
for y, tau, lo, hi, c in zip(y_pos, taus, ci_lo, ci_hi, colors):
    axC.errorbar(tau, y, xerr=[[tau-lo],[hi-tau]],
                 fmt="o", color=c, ecolor=c,
                 markersize=2.5, capsize=1.5, elinewidth=0.7,
                 markeredgecolor=CHARCOAL, markeredgewidth=0.3)
    # Value label, placed to the LEFT of the marker, inside the panel
    axC.text(tau - 4, y + 0.25, f"{tau:+.2f}",
             color=c, ha="right", va="bottom",
             fontsize=4.6, fontweight="bold")

axC.axvline(0, color=CHARCOAL, lw=0.4, ls=":", alpha=0.7)
axC.set_yticks(y_pos)
axC.set_yticklabels(labels, fontsize=4.6)
axC.set_ylim(-0.7, len(labels)-0.3)
axC.set_xlim(-70, 100)
axC.set_xlabel("τ̂  (days)", fontsize=5.0, labelpad=1.0)
axC.tick_params(axis="x", labelsize=4.4, length=1.2, pad=0.8)
axC.tick_params(axis="y", length=0, pad=1.2)

# Annotation INSIDE the axes at the bottom
axC.text(0.5, 0.04,
         "Δτ̂_SOS = −0.181 d  ·  WCR 95 % CIs span zero",
         transform=axC.transAxes, ha="center", va="bottom",
         fontsize=3.9, color=CHARCOAL, style="italic")

# ---- Save ----
fig.savefig(OUT_PDF, format="pdf", facecolor=BG, edgecolor="none")
fig.savefig(OUT_PNG, format="png", dpi=1000, facecolor=BG, edgecolor="none")
plt.close(fig)

sz_pdf = os.path.getsize(OUT_PDF)
sz_png = os.path.getsize(OUT_PNG)
print(f"OK  PDF  {OUT_PDF}  ({sz_pdf/1024:.1f} KB)")
print(f"OK  PNG  {OUT_PNG}  ({sz_png/1024:.1f} KB)")
print(f"Canvas: {W_CM} × {H_CM} cm  ({W_IN*1000:.0f} × {H_IN*1000:.0f} px @ 1000 DPI)")

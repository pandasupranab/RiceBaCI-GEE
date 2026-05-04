"""
render_figures.py
=================
RiceBaCI-GEE — Publication-quality figure rendering pipeline.

Produces all 10 manuscript figures as 300-DPI PNG files saved to
the same directory as this script.

All figures use clearly labelled ILLUSTRATIVE / SYNTHETIC data
(watermark on every panel).  Swap the synthetic data sections for
real data exports before journal submission.

Dependencies (standard scientific Python stack):
  matplotlib, numpy, pandas, scipy
  geopandas / cartopy / shapely are NOT required — Fig 1 uses
  matplotlib patches as a fallback.

Usage:
  python render_figures.py

Seed: 2026 (reproducible)
"""

import os
import sys
import warnings
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patches as mpatch
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle, Arc
from matplotlib.collections import PatchCollection, LineCollection
from matplotlib.colors import Normalize, TwoSlopeNorm
import matplotlib.cm as cm
import matplotlib.gridspec as gridspec
from scipy.ndimage import gaussian_filter

warnings.filterwarnings("ignore")

# ── global settings ──────────────────────────────────────────────────────────
RNG = np.random.default_rng(2026)
OUT_DIR = Path(__file__).parent          # save next to script
DPI = 300
WATERMARK = "ILLUSTRATIVE — REPLACE WITH REAL DATA"

# colour palette (consistent across all figures)
C_VIRIDIS  = "viridis"
C_PLASMA   = "plasma"
C_RDBU     = "RdBu"
C_TAB10    = plt.get_cmap("tab10")

# brand colours
COL_COASTAL = "#1a6faf"   # coastal/treatment
COL_INLAND  = "#d46a2a"   # inland/control
COL_RAW     = "#c0392b"   # raw pipeline
COL_CORR    = "#27ae60"   # corrected pipeline
COL_FANI    = "#e74c3c"
COL_AMPHAN  = "#8e44ad"
COL_YAAS    = "#e67e22"
COL_GREY    = "#7f8c8d"

FONT_TITLE  = dict(fontsize=11, fontweight="bold")
FONT_LABEL  = dict(fontsize=9)
FONT_TICK   = dict(labelsize=8)

# ── helpers ──────────────────────────────────────────────────────────────────

def add_watermark(ax, text=WATERMARK, fontsize=6.5, alpha=0.55):
    """Place italic watermark in lower-right corner of axes."""
    ax.text(
        0.99, 0.01, text,
        transform=ax.transAxes,
        ha="right", va="bottom",
        fontsize=fontsize, style="italic",
        color="#c0392b", alpha=alpha,
        zorder=99,
    )

def add_panel_label(ax, label, x=-0.12, y=1.02):
    ax.text(x, y, label, transform=ax.transAxes,
            fontsize=11, fontweight="bold", va="bottom")

def savefig(fig, fname):
    fpath = OUT_DIR / fname
    fig.savefig(fpath, dpi=DPI, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: {fname}")

# ═════════════════════════════════════════════════════════════════════════════
# Fig 01 — Study area + cyclone tracks
# ═════════════════════════════════════════════════════════════════════════════
def fig01_study_area():
    """
    Matplotlib-polygon approximation of Odisha coastal & inland districts
    plus synthetic IBTrACS cyclone tracks for Fani, Amphan, Yaas.
    No geopandas / cartopy required.
    """
    fig, ax = plt.subplots(figsize=(8, 7), facecolor="white")

    # ── basemap: Bay of Bengal water colour ──────────────────────────────
    ocean_rect = Rectangle((78, 16), 12, 9.5, linewidth=0,
                            facecolor="#cce5f5", zorder=0)
    land_rect  = Rectangle((78, 16), 12, 9.5, linewidth=0,
                            facecolor="#e8e0d0", zorder=1)
    ax.add_patch(land_rect)
    ax.add_patch(ocean_rect)   # will be partially covered by land

    # rough India land mask east coast (synthetic polygon)
    india_east = np.array([
        [80.0, 22.5], [81.0, 22.0], [82.5, 21.5], [83.5, 20.5],
        [84.5, 20.0], [85.5, 19.5], [86.5, 19.0], [87.5, 18.5],
        [87.5, 16.0], [78.0, 16.0], [78.0, 22.5],
    ])
    land_poly = Polygon(india_east, closed=True,
                        facecolor="#e8e0d0", edgecolor="#aaaaaa",
                        linewidth=0.8, zorder=2)
    ax.add_patch(land_poly)

    # ── synthetic district approximate polygons ───────────────────────────
    # (lon_min, lat_min, width, height) as rough rectangles
    coastal_districts = {
        "Balasore":        (86.3, 21.3, 1.0, 0.8),
        "Bhadrak":         (85.8, 20.7, 0.9, 0.7),
        "Kendrapara":      (86.2, 20.3, 0.8, 0.6),
        "Jagatsinghapur":  (86.0, 19.9, 0.6, 0.5),
        "Puri":            (85.5, 19.6, 0.8, 0.5),
    }
    inland_districts = {
        "Sambalpur":  (83.8, 21.2, 1.2, 1.0),
        "Bargarh":    (83.0, 21.1, 1.1, 0.9),
        "Sundargarh": (84.0, 22.0, 1.1, 1.0),
    }

    for name, (x, y, w, h) in coastal_districts.items():
        r = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04",
                           linewidth=1.2, edgecolor=COL_COASTAL,
                           facecolor="#aad4f5", alpha=0.75, zorder=4)
        ax.add_patch(r)
        ax.text(x + w/2, y + h/2, name, ha="center", va="center",
                fontsize=7, fontweight="bold", color="#003366", zorder=5)

    for name, (x, y, w, h) in inland_districts.items():
        r = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04",
                           linewidth=1.2, edgecolor=COL_INLAND,
                           facecolor="#f5d4aa", alpha=0.75, zorder=4)
        ax.add_patch(r)
        ax.text(x + w/2, y + h/2, name, ha="center", va="center",
                fontsize=7, fontweight="bold", color="#7a3800", zorder=5)

    # ── synthetic cyclone tracks ──────────────────────────────────────────
    def track_lons_lats(origin_lon, origin_lat, landfall_lon, landfall_lat, n=30):
        lons = np.linspace(origin_lon, landfall_lon, n) + \
               0.2 * np.sin(np.linspace(0, np.pi, n))
        lats = np.linspace(origin_lat, landfall_lat, n)
        return lons, lats

    cyclones = [
        ("Fani 2019",  COL_FANI,   (88.0, 17.5), (85.8, 19.8)),
        ("Amphan 2020", COL_AMPHAN, (90.0, 16.0), (86.8, 21.6)),
        ("Yaas 2021",  COL_YAAS,   (89.5, 16.5), (87.0, 21.0)),
    ]

    lf_handles = []
    for name, col, (olon, olat), (llon, llat) in cyclones:
        lons, lats = track_lons_lats(olon, olat, llon, llat)
        ax.plot(lons, lats, color=col, linewidth=1.8, zorder=6,
                linestyle="--", alpha=0.85)
        ax.scatter(llon, llat, marker="*", s=180, color=col,
                   edgecolors="white", linewidth=0.6, zorder=7)
        lf_handles.append(mpatches.Patch(color=col, label=f"{name} track"))

    # ── legend & decorations ──────────────────────────────────────────────
    coastal_patch = mpatches.Patch(facecolor="#aad4f5", edgecolor=COL_COASTAL,
                                   label="Coastal treatment districts (n=5)")
    inland_patch  = mpatches.Patch(facecolor="#f5d4aa", edgecolor=COL_INLAND,
                                   label="Inland control districts (n=3)")
    star_handle   = plt.scatter([], [], marker="*", s=100, color="k",
                                label="Cyclone landfall")
    ax.legend(handles=[coastal_patch, inland_patch, star_handle] + lf_handles,
              loc="lower left", fontsize=7.5, framealpha=0.9)

    ax.set_xlim(81, 91)
    ax.set_ylim(17.5, 23)
    ax.set_xlabel("Longitude (°E)", **FONT_LABEL)
    ax.set_ylabel("Latitude (°N)", **FONT_LABEL)
    ax.tick_params(**FONT_TICK)
    ax.set_title("Fig 1 — Study Area: Odisha Districts and Cyclone Tracks (Bay of Bengal)",
                 **FONT_TITLE)
    ax.set_facecolor("#cce5f5")

    # compass rose
    ax.annotate("N", xy=(0.96, 0.88), xycoords="axes fraction",
                ha="center", fontsize=10, fontweight="bold")
    ax.annotate("▲", xy=(0.96, 0.85), xycoords="axes fraction",
                ha="center", fontsize=9)

    add_watermark(ax)
    savefig(fig, "Fig01_study_area.png")


# ═════════════════════════════════════════════════════════════════════════════
# Fig 02 — Conceptual workflow diagram
# ═════════════════════════════════════════════════════════════════════════════
def fig02_workflow():
    fig, ax = plt.subplots(figsize=(12, 7), facecolor="white")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("Fig 2 — RiceBaCI-GEE Methodological Workflow",
                 **FONT_TITLE, pad=12)

    def box(ax, x, y, w, h, label, color="#d5e8f5", fontsize=8.5,
            edgecolor="#2980b9", wrap=True):
        r = FancyBboxPatch((x - w/2, y - h/2), w, h,
                           boxstyle="round,pad=0.12",
                           facecolor=color, edgecolor=edgecolor,
                           linewidth=1.4, zorder=3)
        ax.add_patch(r)
        if wrap:
            label = "\n".join(textwrap.wrap(label, 14))
        ax.text(x, y, label, ha="center", va="center",
                fontsize=fontsize, zorder=4,
                multialignment="center")

    def arrow(ax, x1, y1, x2, y2, color="#555555"):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color,
                                   lw=1.5, connectionstyle="arc3,rad=0.0"),
                    zorder=5)

    # ── input data sources ────────────────────────────────────────────────
    inputs = [
        (1.0, 5.0, "Sentinel-1\nGRD (VH+VV)", "#d0e8d0"),
        (2.5, 5.0, "Sentinel-2\nL2A (NDWI,\nLSWI)", "#d0e8d0"),
        (4.0, 5.0, "JRC Surface\nWater", "#d0e8d0"),
        (5.5, 5.0, "ERA5-Land\nWind Speed", "#d0e8d0"),
        (7.0, 5.0, "IBTrACS\nCyclone Tracks", "#d0e8d0"),
    ]
    for xc, yc, lbl, col in inputs:
        box(ax, xc, yc, 1.35, 0.9, lbl, color=col, fontsize=7.8,
            edgecolor="#27ae60", wrap=False)

    # Feature stack
    box(ax, 4.0, 3.8, 5.5, 0.75, "8-Feature Stack", color="#fff2cc",
        edgecolor="#d4a017", fontsize=9, wrap=False)
    for xc, yc, _, _ in inputs:
        arrow(ax, xc, yc - 0.45, xc if xc < 4.0 else xc, 3.8 + 0.375)

    # RF classifier
    box(ax, 4.0, 2.7, 3.2, 0.75,
        "Random Forest Saline-Flood\nClassifier (8 features)",
        color="#fce4d6", edgecolor="#c0392b", fontsize=8.2, wrap=False)
    arrow(ax, 4.0, 3.8 - 0.375, 4.0, 2.7 + 0.375)

    # Pixel relabelling
    box(ax, 4.0, 1.7, 2.8, 0.65, "Pixel Relabelling\n(saline-flood → mask)",
        color="#ead1dc", edgecolor="#8e44ad", fontsize=8.0, wrap=False)
    arrow(ax, 4.0, 2.7 - 0.375, 4.0, 1.7 + 0.325)

    # Two phenology branches
    box(ax, 2.0, 0.75, 2.5, 0.65,
        "Whittaker + Double-Logistic\nRAW pipeline",
        color="#ffd7d7", edgecolor=COL_RAW, fontsize=7.8, wrap=False)
    box(ax, 6.5, 0.75, 2.9, 0.65,
        "Whittaker + Double-Logistic\nCORRECTED pipeline",
        color="#d7ffd7", edgecolor=COL_CORR, fontsize=7.8, wrap=False)
    arrow(ax, 3.3, 1.7 - 0.325, 2.0, 0.75 + 0.325)
    arrow(ax, 4.7, 1.7 - 0.325, 6.5, 0.75 + 0.325)

    # SOS/POS/EOS
    box(ax, 9.5, 2.5, 2.0, 0.65,
        "SOS / POS / EOS\nrasters + bootstrap CIs",
        color="#dae8fc", edgecolor="#2980b9", fontsize=8.0, wrap=False)
    arrow(ax, 7.0 + 1.45/2, 0.75, 9.5, 2.5 - 0.325)

    # BACI model
    box(ax, 9.5, 1.3, 2.0, 0.65,
        "BACI Mixed-Effects\nModel (lme4, R)",
        color="#e1d5e7", edgecolor="#6c3483", fontsize=8.0, wrap=False)
    arrow(ax, 9.5, 2.5 - 0.325, 9.5, 1.3 + 0.325)

    # validation side box
    box(ax, 11.5, 3.5, 1.2, 0.55,
        "MCD12Q2 +\nVDSA Validation",
        color="#fff2cc", edgecolor="#d4a017", fontsize=7.5, wrap=False)
    arrow(ax, 11.5, 3.5 - 0.275, 10.5, 2.5)

    # legend arrows
    ax.plot([], [], "--", color=COL_RAW, label="Raw pipeline")
    ax.plot([], [], "-", color=COL_CORR, label="Corrected pipeline")
    ax.legend(loc="lower left", fontsize=8, framealpha=0.9)

    add_watermark(ax)
    savefig(fig, "Fig02_workflow.png")


# ═════════════════════════════════════════════════════════════════════════════
# Fig 03 — Backscatter signature comparison
# ═════════════════════════════════════════════════════════════════════════════
def fig03_backscatter():
    """4-panel: VH and VV time series for cyclone-flood vs agronomic-flood pixel"""
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), facecolor="white",
                             sharey="row", sharex=True)
    fig.suptitle("Fig 3 — SAR Backscatter Time Series: Cyclone-Flood vs Agronomic-Flood Pixels (2020)",
                 **FONT_TITLE)

    # synthetic dates: June–November 2020, every 6 days
    doy = np.arange(152, 335, 6)   # day of year
    n = len(doy)

    def smooth_ts(base, dip_center, dip_width, dip_depth, growth_center,
                  growth_width, growth_height):
        ts = np.full(n, base)
        # dip (flooding event)
        for i, d in enumerate(doy):
            ts[i] += dip_depth  * np.exp(-0.5 * ((d - dip_center)/dip_width)**2)
            ts[i] += growth_height * np.exp(-0.5 * ((d - growth_center)/growth_width)**2)
        noise = RNG.normal(0, 0.6, n)
        return ts + noise

    # ── synthetic time series ─────────────────────────────────────────────
    # Cyclone-flood pixel: steep dip mid-May (DoY≈141), corrected to DoY~145
    # Inside plot window Jun-Nov: Amphan landfall DoY=141 (before window),
    # show it as early Jun artefact; second dip for agronomic Jul
    vh_cyc = smooth_ts(-14, 155, 12, -9, 230, 30, 6)   # early steep dip
    vv_cyc = smooth_ts(-10, 155, 12, -7, 230, 30, 5)

    # Agronomic-flood pixel: dip late July (DoY~200)
    vh_agr = smooth_ts(-14, 200, 15, -9, 245, 30, 6)
    vv_agr = smooth_ts(-10, 200, 15, -7, 245, 30, 5)

    amphan_doy = 141   # outside window — mark where series starts
    transplant_start = 175
    transplant_end   = 215

    titles_row = ["VH (dB)", "VV (dB)"]
    titles_col = ["Cyclone-flood pixel", "Agronomic-flood pixel"]
    data_sets  = [(vh_cyc, vv_cyc), (vh_agr, vv_agr)]
    colors     = [COL_FANI, COL_COASTAL]   # one per column

    panel_labels = [("a", "b"), ("c", "d")]

    for row in range(2):
        for col in range(2):
            ax = axes[row, col]
            ts = data_sets[col][row]
            ax.plot(doy, ts, color=colors[col], linewidth=1.8, zorder=4)

            # transplanting window shading
            ax.axvspan(transplant_start, transplant_end,
                       color="grey", alpha=0.15, label="Transplanting window")

            # Amphan landfall line (only first column; at window start)
            if col == 0:
                ax.axvline(doy[0], color="red", linewidth=1.5,
                           linestyle="--", label="Amphan landfall (≈DoY 141)")
                ax.text(doy[0] + 2, ts.min() + 0.5,
                        "Amphan\n(DoY≈141)", color="red", fontsize=6.5)

            ax.set_ylabel(titles_row[row] if col == 0 else "",
                          **FONT_LABEL)
            ax.tick_params(**FONT_TICK)
            ax.set_ylim(-28, 2)

            if row == 0:
                ax.set_title(f"({panel_labels[row][col]}) {titles_col[col]}",
                             **FONT_LABEL, loc="left")

            if row == 1:
                ax.set_xlabel("Day of year (2020)", **FONT_LABEL)

            if row == 0 and col == 0:
                ax.legend(fontsize=6.5, loc="lower right")

            add_watermark(ax)

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    savefig(fig, "Fig03_backscatter.png")


# ═════════════════════════════════════════════════════════════════════════════
# Fig 04 — Random forest feature importance
# ═════════════════════════════════════════════════════════════════════════════
def fig04_feature_importance():
    fig, ax = plt.subplots(figsize=(7, 5), facecolor="white")
    ax.set_title("Fig 4 — Random Forest Feature Importances\n(Saline-Flood Classifier)",
                 **FONT_TITLE)

    features = [
        "VH min (dB)",
        "VV min (dB)",
        "VH/VV ratio",
        "NDWI",
        "LSWI",
        "JRC permanence (%)",
        "ERA5 wind speed (m s⁻¹)",
        "Days since storm",
    ]
    importances = [0.22, 0.18, 0.14, 0.11, 0.10, 0.09, 0.10, 0.06]
    assert abs(sum(importances) - 1.0) < 1e-9, "Importances must sum to 1"

    # sort ascending for horizontal bar chart
    idx = np.argsort(importances)
    feats_sorted = [features[i] for i in idx]
    imps_sorted  = [importances[i] for i in idx]

    cmap = cm.get_cmap(C_VIRIDIS)
    colors = [cmap(v / max(importances)) for v in imps_sorted]

    bars = ax.barh(feats_sorted, imps_sorted, color=colors,
                   edgecolor="white", linewidth=0.5, height=0.65)

    for bar, val in zip(bars, imps_sorted):
        ax.text(bar.get_width() + 0.003, bar.get_y() + bar.get_height()/2,
                f"{val:.2f}", va="center", ha="left", fontsize=8)

    ax.set_xlabel("Mean Decrease Impurity (normalised)", **FONT_LABEL)
    ax.tick_params(**FONT_TICK)
    ax.set_xlim(0, 0.28)
    ax.spines[["top", "right"]].set_visible(False)

    sm = plt.cm.ScalarMappable(cmap=cmap,
                               norm=Normalize(vmin=0, vmax=max(importances)))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation="vertical",
                        fraction=0.04, pad=0.03)
    cbar.set_label("Relative importance", fontsize=8)

    add_watermark(ax)
    fig.tight_layout()
    savefig(fig, "Fig04_feature_importance.png")


# ═════════════════════════════════════════════════════════════════════════════
# Fig 05 — SOS/POS/EOS maps raw vs corrected (2020)
# ═════════════════════════════════════════════════════════════════════════════
def fig05_phenology_maps():
    """6-panel map using synthetic rasters + district polygon overlays."""
    fig, axes = plt.subplots(2, 3, figsize=(13, 8), facecolor="white")
    fig.suptitle(
        "Fig 5 — Kharif 2020 Phenological Date Maps: Raw vs. Corrected Pipeline\n"
        "(Amphan year — SOS, POS, EOS; day-of-year from 1 Jun)",
        **FONT_TITLE)

    metrics  = ["SOS (DoY)", "POS (DoY)", "EOS (DoY)"]
    # approximate DoY range per metric (Kharif day-of-year from June 1)
    doy_ranges = [(10, 60), (80, 130), (150, 190)]

    # synthetic 100×100 rasters (lon: 85.5-87.5, lat: 19.5-22.0)
    nx, ny = 100, 100
    xx = np.linspace(85.5, 87.5, nx)
    yy = np.linspace(19.5, 22.0, ny)
    XX, YY = np.meshgrid(xx, yy)

    def make_raster(doy_min, doy_max, delay_zone=True):
        base = RNG.normal(0, 1, (ny, nx))
        raster = gaussian_filter(base, sigma=6)
        raster = (raster - raster.min()) / (raster.max() - raster.min())
        raster = doy_min + raster * (doy_max - doy_min)
        if delay_zone:
            # Bhadrak-like zone ~ lat 20.7-21.4, lon 85.8-86.7 → +10 day delay
            mask = (YY > 20.7) & (YY < 21.4) & (XX > 85.8) & (XX < 86.7)
            raster[mask] += 10
        return raster

    row_labels = ["RAW", "CORRECTED"]

    for col, (metric, (dmin, dmax)) in enumerate(zip(metrics, doy_ranges)):
        raster_raw  = make_raster(dmin, dmax, delay_zone=False)
        raster_corr = make_raster(dmin, dmax, delay_zone=True)

        for row, (raster, rlabel) in enumerate(
                zip([raster_raw, raster_corr], row_labels)):
            ax = axes[row, col]
            im = ax.imshow(raster, extent=[85.5, 87.5, 19.5, 22.0],
                           origin="lower", cmap=C_VIRIDIS,
                           vmin=dmin, vmax=dmax + 12, aspect="auto", zorder=2)

            # district outlines (simplified rectangles)
            for x0, y0, w, h, name in [
                (86.3, 21.3, 1.0, 0.8, "Balasore"),
                (85.8, 20.7, 0.9, 0.7, "Bhadrak"),
                (86.2, 20.3, 0.8, 0.6, "Kendrapara"),
                (86.0, 19.9, 0.6, 0.5, "Jagatsinghapur"),
                (85.5, 19.6, 0.8, 0.5, "Puri"),
            ]:
                rect = Rectangle((x0, y0), w, h, linewidth=1.0,
                                  edgecolor="white", facecolor="none", zorder=5)
                ax.add_patch(rect)
                if col == 0:
                    ax.text(x0 + w/2, y0 + h/2, name[:4],
                            ha="center", va="center", fontsize=5.5,
                            color="white", fontweight="bold", zorder=6)

            cbar = fig.colorbar(im, ax=ax, orientation="vertical",
                                fraction=0.046, pad=0.04)
            cbar.set_label("DoY", fontsize=7)
            cbar.ax.tick_params(labelsize=7)

            ax.set_title(f"({chr(97 + row*3 + col)}) {rlabel} — {metric}",
                         fontsize=8, loc="left")
            ax.tick_params(**FONT_TICK)
            ax.set_xlabel("Lon °E" if row == 1 else "", fontsize=7)
            ax.set_ylabel("Lat °N" if col == 0 else "", fontsize=7)

            add_watermark(ax, fontsize=5.5)

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    savefig(fig, "Fig05_phenology_maps.png")


# ═════════════════════════════════════════════════════════════════════════════
# Fig 06 — BACI mixed-effects results
# ═════════════════════════════════════════════════════════════════════════════
def fig06_baci():
    fig, ax = plt.subplots(figsize=(8, 6), facecolor="white")
    ax.set_title("Fig 6 — BACI Mixed-Effects Estimates: Raw vs. Corrected Pipeline\n"
                 "(BACI shift = cyclone-year − control-year difference, days)",
                 **FONT_TITLE)

    metrics = ["SOS", "POS", "EOS"]
    # synthetic BACI effects (days)
    raw_effects  = [-18.5, -6.2, -11.3]
    raw_ci       = [  3.8,  2.5,   3.1]
    corr_effects = [ -4.2, -2.0,  -3.5]
    corr_ci      = [  3.0,  2.1,   2.8]

    x = np.arange(len(metrics))
    w = 0.32

    bars_r = ax.bar(x - w/2, raw_effects,  width=w, color=COL_RAW,
                    alpha=0.85, label="Raw pipeline",       zorder=3)
    bars_c = ax.bar(x + w/2, corr_effects, width=w, color=COL_CORR,
                    alpha=0.85, label="Corrected pipeline", zorder=3)

    # 95 % CI error bars
    ax.errorbar(x - w/2, raw_effects, yerr=[1.96*ci for ci in raw_ci],
                fmt="none", color="black", capsize=5, linewidth=1.4, zorder=4)
    ax.errorbar(x + w/2, corr_effects, yerr=[1.96*ci for ci in corr_ci],
                fmt="none", color="black", capsize=5, linewidth=1.4, zorder=4)

    ax.axhline(0, color="k", linewidth=1.0, linestyle="--", zorder=2)

    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=10)
    ax.set_ylabel("BACI phenological shift (days)", **FONT_LABEL)
    ax.set_xlabel("Phenological metric", **FONT_LABEL)
    ax.tick_params(**FONT_TICK)
    ax.legend(fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)

    # annotate significance
    for i, (re, ce) in enumerate(zip(raw_effects, corr_effects)):
        ax.text(i - w/2, re - 1.2, "*", ha="center", va="top",
                fontsize=12, color=COL_RAW)
        ns = "n.s." if abs(ce) < 4 else "*"
        ax.text(i + w/2, ce - 1.2, ns, ha="center", va="top",
                fontsize=9, color=COL_CORR)

    ax.text(0.5, -0.13,
            "[ILLUSTRATIVE] * p < 0.05 (parametric bootstrap); n.s. = not significant",
            transform=ax.transAxes, ha="center", fontsize=7,
            style="italic", color=COL_RAW)

    add_watermark(ax)
    fig.tight_layout()
    savefig(fig, "Fig06_baci_results.png")


# ═════════════════════════════════════════════════════════════════════════════
# Fig 07 — Validation scatter vs MODIS MCD12Q2 + ICRISAT VDSA
# ═════════════════════════════════════════════════════════════════════════════
def fig07_validation():
    fig, axes = plt.subplots(1, 3, figsize=(13, 5), facecolor="white")
    fig.suptitle(
        "Fig 7 — Validation: Extracted vs. MODIS MCD12Q2 + ICRISAT VDSA Phenological Dates\n"
        "(Day-of-year; n=72 station-year observations [ILLUSTRATIVE])",
        **FONT_TITLE)

    metrics = ["SOS", "POS", "EOS"]
    centres = [40, 105, 175]   # approximate true DoY centres

    for col, (metric, centre) in enumerate(zip(metrics, centres)):
        ax = axes[col]

        # synthetic "true" reference dates (MCD12Q2 + VDSA)
        n_pts = 24
        true_doys = RNG.normal(centre, 8, n_pts)

        # corrected pipeline: within ±7 days
        corr_pred = true_doys + RNG.normal(0, 4, n_pts)
        # raw pipeline: scattered up to 25 days
        raw_pred  = true_doys + RNG.normal(-8, 9, n_pts)

        ax.scatter(true_doys, raw_pred, color=COL_RAW, alpha=0.7,
                   s=45, label="Raw pipeline", zorder=4)
        ax.scatter(true_doys, corr_pred, color=COL_CORR, alpha=0.85,
                   s=45, marker="D", label="Corrected pipeline", zorder=5)

        # 1:1 line
        lo = centre - 30; hi = centre + 30
        ax.plot([lo, hi], [lo, hi], "k-", linewidth=1.2,
                label="1:1 line", zorder=3)
        # ±10-day envelope
        ax.fill_between([lo, hi], [lo-10, hi-10], [lo+10, hi+10],
                        alpha=0.1, color="grey", label="±10-day envelope")

        mae_raw  = np.mean(np.abs(raw_pred  - true_doys))
        mae_corr = np.mean(np.abs(corr_pred - true_doys))

        ax.text(0.04, 0.96,
                f"MAE raw  = {mae_raw:.1f} d [ILLUSTRATIVE]\n"
                f"MAE corr = {mae_corr:.1f} d [ILLUSTRATIVE]",
                transform=ax.transAxes, va="top", fontsize=7.5,
                bbox=dict(facecolor="white", alpha=0.7, edgecolor="grey",
                          boxstyle="round,pad=0.3"))

        ax.set_title(f"({chr(97+col)}) {metric}", fontsize=9, loc="left")
        ax.set_xlabel("Reference DoY (MCD12Q2 / VDSA)", **FONT_LABEL)
        if col == 0:
            ax.set_ylabel("Extracted DoY", **FONT_LABEL)
        ax.tick_params(**FONT_TICK)

        if col == 2:
            ax.legend(fontsize=7.5, loc="upper left")

        add_watermark(ax, fontsize=5.5)

    fig.tight_layout(rect=[0, 0, 1, 0.92])
    savefig(fig, "Fig07_validation.png")


# ═════════════════════════════════════════════════════════════════════════════
# Fig 08 — Transferability: Andhra Pradesh (Hudhud 2014)
# ═════════════════════════════════════════════════════════════════════════════
def fig08_transferability():
    fig = plt.figure(figsize=(13, 6), facecolor="white")
    fig.suptitle(
        "Fig 8 — Transferability to Andhra Pradesh: Cyclone Hudhud 2014",
        **FONT_TITLE)

    gs = gridspec.GridSpec(1, 3, width_ratios=[2, 2, 1.4], wspace=0.3)

    # ── Map panels ────────────────────────────────────────────────────────
    map_defs = [
        ("(a) Odisha: Amphan 2020",  (84.5, 87.5, 18.5, 22.5), (85.5, 87.5)),
        ("(b) Andhra Pradesh: Hudhud 2014", (79.0, 84.0, 14.0, 19.5), (80.0, 83.0)),
    ]

    for i, (title, (xmin, xmax, ymin, ymax), prob_zone) in enumerate(map_defs):
        ax = fig.add_subplot(gs[i])
        # background land colour
        ax.set_facecolor("#e8e0d0")
        ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax)

        # synthetic cyclone-flood probability raster
        nx, ny = 80, 80
        xx = np.linspace(xmin, xmax, nx)
        yy = np.linspace(ymin, ymax, ny)
        XX, YY = np.meshgrid(xx, yy)
        proba = RNG.random((ny, nx))
        proba = gaussian_filter(proba, sigma=5)
        # higher probability near coast (eastern edge)
        coast_grad = (XX - xmin) / (xmax - xmin)
        proba = 0.4 * proba + 0.6 * coast_grad
        # clip to [0,1]
        proba = np.clip(proba, 0, 1)

        im = ax.imshow(proba, extent=[xmin, xmax, ymin, ymax],
                       origin="lower", cmap=C_PLASMA, vmin=0, vmax=1,
                       aspect="auto", alpha=0.75, zorder=2)
        cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.03)
        cbar.set_label("Cyclone-flood\nprobability", fontsize=7)
        cbar.ax.tick_params(labelsize=7)

        ax.set_title(title, fontsize=8.5, loc="left")
        ax.set_xlabel("Lon °E", fontsize=8)
        ax.set_ylabel("Lat °N" if i == 0 else "", fontsize=8)
        ax.tick_params(**FONT_TICK)
        add_watermark(ax, fontsize=5.5)

    # ── Bar chart inset ───────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[2])
    regions = ["Odisha\n(training)", "Andhra\n(transfer)"]
    oa_vals = [0.91, 0.85]
    colors  = [COL_COASTAL, COL_INLAND]
    ax3.bar(regions, oa_vals, color=colors, width=0.45,
            edgecolor="white", linewidth=1.0, zorder=3)
    ax3.set_ylim(0.70, 1.0)
    ax3.set_ylabel("Overall Accuracy", **FONT_LABEL)
    ax3.set_title("(c) Classifier OA\n[ILLUSTRATIVE]", fontsize=8.5, loc="left")
    ax3.tick_params(**FONT_TICK)
    ax3.spines[["top", "right"]].set_visible(False)
    ax3.axhline(0.88, color="grey", linewidth=1.0, linestyle="--",
                label="Pre-registered threshold (0.88)")
    for i, v in enumerate(oa_vals):
        ax3.text(i, v + 0.003, f"{v:.2f}", ha="center",
                 fontsize=9, fontweight="bold")
    ax3.legend(fontsize=7)
    add_watermark(ax3, fontsize=5.5)

    savefig(fig, "Fig08_transferability.png")


# ═════════════════════════════════════════════════════════════════════════════
# Fig 09 — Pixel-level uncertainty maps
# ═════════════════════════════════════════════════════════════════════════════
def fig09_uncertainty():
    fig, axes = plt.subplots(1, 3, figsize=(13, 5), facecolor="white")
    fig.suptitle(
        "Fig 9 — Phenological Date Uncertainty Maps: Bootstrap 95% CI Half-Width (days)\n"
        "(Kharif 2020; highest uncertainty along coastline and fragmented fields)",
        **FONT_TITLE)

    metrics = ["SOS", "POS", "EOS"]
    for col, metric in enumerate(metrics):
        ax = axes[col]
        nx, ny = 100, 100
        xx = np.linspace(85.5, 87.5, nx)
        yy = np.linspace(19.5, 22.0, ny)
        XX, YY = np.meshgrid(xx, yy)

        # synthetic uncertainty: higher near coast (east), lower inland
        base = RNG.random((ny, nx))
        base = gaussian_filter(base, sigma=5)
        # coastal gradient: east = high uncertainty
        coast_unc = (XX - 85.5) / (87.5 - 85.5) * 12
        # fragmented-field noise band
        frag_noise = np.where(
            (YY > 20.0) & (YY < 20.8) & (XX > 86.0) & (XX < 87.0),
            RNG.uniform(4, 14, (ny, nx)), 0)
        unc = 2 + coast_unc + 3 * base + frag_noise
        unc = gaussian_filter(unc, sigma=3)

        im = ax.imshow(unc, extent=[85.5, 87.5, 19.5, 22.0],
                       origin="lower", cmap=C_PLASMA, vmin=0, vmax=20,
                       aspect="auto", zorder=2)

        # district outlines
        for x0, y0, w, h in [
            (86.3, 21.3, 1.0, 0.8), (85.8, 20.7, 0.9, 0.7),
            (86.2, 20.3, 0.8, 0.6), (86.0, 19.9, 0.6, 0.5),
            (85.5, 19.6, 0.8, 0.5),
        ]:
            rect = Rectangle((x0, y0), w, h, linewidth=0.8,
                              edgecolor="white", facecolor="none", zorder=4)
            ax.add_patch(rect)

        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label("CI half-width (days)", fontsize=7)
        cbar.ax.tick_params(labelsize=7)

        ax.set_title(f"({chr(97+col)}) {metric} uncertainty",
                     fontsize=8.5, loc="left")
        ax.set_xlabel("Lon °E", fontsize=8)
        if col == 0:
            ax.set_ylabel("Lat °N", fontsize=8)
        ax.tick_params(**FONT_TICK)
        add_watermark(ax, fontsize=5.5)

    fig.tight_layout(rect=[0, 0, 1, 0.90])
    savefig(fig, "Fig09_uncertainty.png")


# ═════════════════════════════════════════════════════════════════════════════
# Fig 10 — Inter-product comparison
# ═════════════════════════════════════════════════════════════════════════════
def fig10_intercomparison():
    fig = plt.figure(figsize=(13, 7), facecolor="white")
    fig.suptitle(
        "Fig 10 — Inter-Product Rice-Area Comparison\n"
        "(RiceBaCI-GEE corrected vs. Mondal 2022 RSE&C vs. Singha 2019 South-Asia)",
        **FONT_TITLE)

    gs = gridspec.GridSpec(1, 2, width_ratios=[1.5, 1], wspace=0.35)

    districts = ["Balasore", "Bhadrak", "Kendrapara",
                 "Jagatsinghapur", "Puri"]
    n = len(districts)

    # synthetic rice area (×1000 ha) — realistic Odisha district magnitudes
    area_ricebaCI = RNG.normal([142, 118, 135, 97, 161], 5, (1, n)).flatten()
    area_mondal   = RNG.normal([138, 122, 130, 101, 156], 8, (1, n)).flatten()
    area_singha   = RNG.normal([148, 112, 140, 93,  170], 11,(1, n)).flatten()

    # ── Grouped bar chart ─────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0])
    x = np.arange(n)
    w = 0.26
    ax1.bar(x - w,   area_ricebaCI, width=w, color=COL_CORR,
            label="RiceBaCI-GEE (corrected)", edgecolor="white")
    ax1.bar(x,       area_mondal,   width=w, color=COL_COASTAL,
            label="Mondal 2022 (RSE&C)", edgecolor="white")
    ax1.bar(x + w,   area_singha,   width=w, color=COL_INLAND,
            label="Singha 2019 (South-Asia)", edgecolor="white")

    ax1.set_xticks(x)
    ax1.set_xticklabels(districts, rotation=20, ha="right", fontsize=8)
    ax1.set_ylabel("Rice area (×1000 ha)", **FONT_LABEL)
    ax1.set_title("(a) Total Kharif rice area per district", fontsize=9, loc="left")
    ax1.legend(fontsize=7.5)
    ax1.tick_params(**FONT_TICK)
    ax1.spines[["top", "right"]].set_visible(False)
    add_watermark(ax1, fontsize=5.5)

    # ── Agreement statistics table + dot plot ─────────────────────────────
    ax2 = fig.add_subplot(gs[1])
    ax2.axis("off")

    kappa_data = {
        "Comparison pair": [
            "RiceBaCI vs. Mondal 2022",
            "RiceBaCI vs. Singha 2019",
            "Mondal 2022 vs. Singha 2019",
        ],
        "Cohen's κ\n[ILLUSTRATIVE]": ["0.82", "0.74", "0.77"],
        "Area bias\n(×1000 ha)": ["+3.8", "−4.2", "−8.0"],
        "Pearson r": ["0.97", "0.93", "0.91"],
    }
    df = pd.DataFrame(kappa_data)

    col_labels = list(df.columns)
    cell_text  = df.values.tolist()

    tbl = ax2.table(
        cellText=cell_text,
        colLabels=col_labels,
        loc="center",
        cellLoc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.scale(1, 2.2)

    # style header row
    for j in range(len(col_labels)):
        tbl[0, j].set_facecolor("#2c3e50")
        tbl[0, j].set_text_props(color="white", fontweight="bold")

    ax2.set_title("(b) Agreement statistics [ILLUSTRATIVE]",
                  fontsize=9, loc="left", y=0.92)
    add_watermark(ax2, fontsize=5.5)

    fig.tight_layout(rect=[0, 0, 1, 0.91])
    savefig(fig, "Fig10_intercomparison.png")


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("RiceBaCI-GEE Figure Rendering Pipeline")
    print(f"Output directory : {OUT_DIR}")
    print(f"DPI              : {DPI}")
    print(f"Random seed      : 2026")
    print("=" * 60)

    # Library availability report
    unavailable = []
    try:
        import geopandas   # noqa: F401
    except ImportError:
        unavailable.append("geopandas → fallback: matplotlib polygon patches")
    try:
        import cartopy     # noqa: F401
    except ImportError:
        unavailable.append("cartopy  → fallback: matplotlib imshow + manual coastline polygon")
    try:
        import shapely     # noqa: F401
    except ImportError:
        unavailable.append("shapely  → not needed (matplotlib patches used)")

    if unavailable:
        print("\nLibraries unavailable (graceful fallbacks used):")
        for u in unavailable:
            print(f"  ✗  {u}")
    print()

    funcs = [
        fig01_study_area,
        fig02_workflow,
        fig03_backscatter,
        fig04_feature_importance,
        fig05_phenology_maps,
        fig06_baci,
        fig07_validation,
        fig08_transferability,
        fig09_uncertainty,
        fig10_intercomparison,
    ]

    for f in funcs:
        f()

    # Summary
    pngs = sorted(OUT_DIR.glob("Fig*.png"))
    print()
    print(f"Generated {len(pngs)} PNG files:")
    total_bytes = 0
    for p in pngs:
        size = p.stat().st_size
        total_bytes += size
        print(f"  {p.name:45s}  {size/1024:7.1f} KB")
    print(f"\nTotal output size: {total_bytes/1024/1024:.2f} MB")
    print("Done.")


if __name__ == "__main__":
    main()

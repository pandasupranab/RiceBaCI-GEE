#!/usr/bin/env python3
"""
Module 10 - Identification DAG (Fig 1B)
========================================

Pearl-style causal diagram for the RiceBaCI-GEE design.

Two stacked panels:

  (a) NAIVE PIPELINE — saline storm-surge inundation creates a
      backscatter trough that is mis-read as transplanting flooding,
      biasing SOS by +5-6 days. The cyclone-induced confound is in
      red.

  (b) CORRECTED PIPELINE — the saline-flood classifier (Module 02)
      breaks the cyclone -> backscatter trough arrow, leaving only
      the legitimate transplanting -> trough arrow. SOS bias collapses
      from +5.66 d to +1.96 d.

Output:
  figures/fig1b_identification_dag.{pdf,png}

Conventions:
  - boxes: observed variables (rectangles)
  - dashed boxes: latent / unobserved variables
  - solid arrows: identified causal effects
  - red dashed arrows: confounding pathways
  - red X: pathway broken by the correction step
"""

from __future__ import annotations
from pathlib import Path
import argparse

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Okabe-Ito (consistent with Fig 2/3/4/5/6)
OK_BLUE   = "#0072B2"
OK_ORANGE = "#E69F00"
OK_RED    = "#D55E00"
OK_GREEN  = "#009E73"
INK       = "#222222"


def _box(ax, x, y, w, h, text, *,
         dashed=False, fc="white", ec=INK, fontsize=8.5, weight="normal"):
    style = "round,pad=0.02,rounding_size=0.06"
    ls = (0, (4, 2)) if dashed else "-"
    p = FancyBboxPatch((x - w/2, y - h/2), w, h,
                       boxstyle=style,
                       linewidth=1.0, linestyle=ls,
                       facecolor=fc, edgecolor=ec, zorder=2)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center",
            fontsize=fontsize, weight=weight, color=INK, zorder=3)
    return (x, y, w, h)


def _arrow(ax, src, dst, *,
           color=INK, lw=1.1, ls="-", curve=0.0,
           label=None, label_offset=(0, 0.06), label_color=None):
    sx, sy, sw, sh = src
    dx, dy, dw, dh = dst
    # connect from edge of source toward dst
    style = f"arc3,rad={curve}"
    a = FancyArrowPatch(
        (sx, sy), (dx, dy),
        arrowstyle="-|>", mutation_scale=12,
        linewidth=lw, linestyle=ls,
        color=color, zorder=4,
        connectionstyle=style,
        shrinkA=42, shrinkB=42,
    )
    ax.add_patch(a)
    if label:
        mx, my = (sx + dx) / 2 + label_offset[0], (sy + dy) / 2 + label_offset[1]
        ax.text(mx, my, label,
                fontsize=7.5, color=label_color or color,
                ha="center", va="center", style="italic", zorder=5)


def _x_marker(ax, x, y, color=OK_RED, size=0.06):
    ax.plot([x - size, x + size], [y - size, y + size],
            color=color, lw=2.6, solid_capstyle="round", zorder=6)
    ax.plot([x - size, x + size], [y + size, y - size],
            color=color, lw=2.6, solid_capstyle="round", zorder=6)


def draw_panel_a_naive(ax):
    """Naive pipeline: saline-surge confound is identified but uncorrected."""
    ax.set_xlim(0, 11)
    ax.set_ylim(-0.2, 4.0)
    ax.set_aspect("equal")
    ax.axis("off")

    # Title (above the working area)
    ax.text(0.15, 3.85,
            "(a) Naive pipeline (every prior cyclone-affected SAR rice study)",
            fontsize=10.5, weight="bold", ha="left", color=INK)
    ax.text(0.15, 3.50,
            "saline storm-surge inundation is mis-read as transplanting "
            "flooding, biasing SOS",
            fontsize=8.2, ha="left", color="#555555", style="italic")

    # Nodes
    cyclone     = _box(ax, 1.4, 2.4, 1.7, 0.85,
                       "Cyclone\nlandfall",
                       fc="#FFE3D6", ec=OK_RED, weight="bold")
    transplant  = _box(ax, 1.4, 0.6, 1.7, 0.85,
                       "Real\ntransplanting",
                       fc="#FFFFFF", ec=INK)
    surge       = _box(ax, 4.7, 2.4, 1.9, 1.0,
                       "Saline\nstorm-surge\ninundation",
                       fc="#FFC9B0", ec=OK_RED, weight="bold",
                       dashed=True, fontsize=7.6)
    flood       = _box(ax, 4.7, 0.6, 1.9, 0.85,
                       "Agronomic\nflooding",
                       fc="#FFFFFF", ec=INK)
    trough      = _box(ax, 8.0, 1.5, 2.0, 1.05,
                       "SAR backscatter\ntrough\n(VV/VH minimum)",
                       fc="#E6F0F7", ec=OK_BLUE, fontsize=7.8)
    sos         = _box(ax, 10.3, 1.5, 1.4, 1.05,
                       "Estimated\nSOS",
                       fc="#FFFFFF", ec=INK)

    # Causal arrows
    _arrow(ax, cyclone,    surge,      color=OK_RED, lw=1.4,
           label="storm-surge\n(unobserved)", label_offset=(0, 0.30),
           label_color=OK_RED)
    _arrow(ax, cyclone,    transplant, color=INK, ls=(0, (3, 3)),
           lw=0.9, label="delays\nplanting", label_offset=(0.32, 0.0))
    _arrow(ax, transplant, flood,      color=INK)
    _arrow(ax, flood,      trough,     color=INK,
           label="legitimate", label_offset=(0.0, 0.20))
    _arrow(ax, surge,      trough,     color=OK_RED, lw=1.6,
           ls=(0, (5, 2)),
           label="CONFOUND", label_offset=(0.0, 0.20),
           label_color=OK_RED)
    _arrow(ax, trough,     sos,        color=INK)

    # Legend / verdict
    ax.text(5.5, -0.15,
            "SOS bias from saline-surge confound: +5.66 d "
            "(synthetic-panel verification, p_perm = 0.018)",
            fontsize=8.0, ha="center", color=OK_RED, weight="bold")


def draw_panel_b_corrected(ax):
    """Corrected pipeline: saline-surge arrow broken by Module 02."""
    ax.set_xlim(0, 11)
    ax.set_ylim(-0.2, 4.5)
    ax.set_aspect("equal")
    ax.axis("off")

    # Title (above the classifier band, above the nodes)
    ax.text(0.15, 4.35,
            "(b) Corrected pipeline (this study)",
            fontsize=10.5, weight="bold", ha="left", color=INK)
    ax.text(0.15, 4.05,
            "the saline-flood classifier (Module 02) breaks the "
            "storm-surge \u2192 trough arrow, restoring identification",
            fontsize=8.2, ha="left", color="#555555", style="italic")

    # Classifier band sits at the very top — well clear of subtitle
    classifier  = _box(ax, 4.7, 3.55, 3.0, 0.45,
                       "Module 02 saline-flood classifier",
                       fc="#D6F0E2", ec=OK_GREEN, fontsize=7.8,
                       weight="bold")

    cyclone     = _box(ax, 1.4, 2.4, 1.7, 0.85,
                       "Cyclone\nlandfall",
                       fc="#FFE3D6", ec=OK_RED, weight="bold")
    transplant  = _box(ax, 1.4, 0.6, 1.7, 0.85,
                       "Real\ntransplanting",
                       fc="#FFFFFF", ec=INK)
    surge       = _box(ax, 4.7, 2.4, 1.9, 1.0,
                       "Saline\nstorm-surge\ninundation",
                       fc="#FFC9B0", ec=OK_RED, weight="bold",
                       dashed=True, fontsize=7.6)
    flood       = _box(ax, 4.7, 0.6, 1.9, 0.85,
                       "Agronomic\nflooding",
                       fc="#FFFFFF", ec=INK)
    trough      = _box(ax, 8.0, 1.5, 2.0, 1.05,
                       "SAR backscatter\ntrough\n(VV/VH minimum)",
                       fc="#E6F0F7", ec=OK_BLUE, fontsize=7.8)
    sos         = _box(ax, 10.3, 1.5, 1.4, 1.05,
                       "Estimated\nSOS",
                       fc="#FFFFFF", ec=INK)

    _arrow(ax, cyclone,    surge,      color=OK_RED, lw=1.2,
           label="(detected)", label_offset=(0, 0.30),
           label_color=OK_RED)
    _arrow(ax, cyclone,    transplant, color=INK, ls=(0, (3, 3)),
           lw=0.9, label="delays\nplanting", label_offset=(0.32, 0.0))
    _arrow(ax, transplant, flood,      color=INK)
    _arrow(ax, flood,      trough,     color=INK,
           label="legitimate", label_offset=(0.0, 0.20))

    # Module 02 intercepts the surge -> trough arrow
    _arrow(ax, classifier, surge, color=OK_GREEN, lw=1.4,
           label="masks", label_offset=(0.55, 0.0),
           label_color=OK_GREEN)

    # The broken arrow: surge -> trough is now crossed out
    midx = (surge[0] + trough[0]) / 2
    midy = (surge[1] + trough[1]) / 2
    _arrow(ax, surge, trough, color="0.7", lw=1.0,
           ls=(0, (3, 3)))
    _x_marker(ax, midx, midy, color=OK_RED, size=0.20)

    _arrow(ax, trough, sos, color=INK)

    # Verdict
    ax.text(5.5, -0.15,
            "Residual SOS bias after correction: +1.96 d "
            "(p_perm = 0.054; corrected/EOS null at p = 0.27 \u2014 "
            "mechanism-specific)",
            fontsize=8.0, ha="center", color=OK_GREEN, weight="bold")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="figures")
    args = ap.parse_args()

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 9,
    })

    fig, (ax_a, ax_b) = plt.subplots(2, 1, figsize=(9.5, 8.0),
                                      gridspec_kw={"height_ratios": [4.2, 4.7]})
    draw_panel_a_naive(ax_a)
    draw_panel_b_corrected(ax_b)

    fig.subplots_adjust(hspace=0.18, top=0.97, bottom=0.03,
                        left=0.02, right=0.98)

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "fig1b_identification_dag.pdf",
                bbox_inches="tight", pad_inches=0.05)
    fig.savefig(out / "fig1b_identification_dag.png",
                bbox_inches="tight", pad_inches=0.05, dpi=300)
    plt.close(fig)
    print(f"wrote {out}/fig1b_identification_dag.pdf, .png")


if __name__ == "__main__":
    main()

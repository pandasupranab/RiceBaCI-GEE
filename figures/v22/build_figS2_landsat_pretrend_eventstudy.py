"""
Build Figure S2: Landsat-5/7/8 + Sentinel-2 combined event-study (2014-2024, ref=2018).
Layout: 3 rows × 1 column, full-width — (a) SOS top, (b) POS middle, (c) EOS bottom.
Only "(a)", "(b)", "(c)" labels — no subplot titles and no figure suptitle.
Legend overlaid inside panel (a).
Output: 1000 dpi JPG + PDF vector archive.
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

CSV = Path("/home/user/workspace/rse_final/reviewer_rebuttal/table_S10_pretrend_event_study.csv")
OUT_DIR = Path("/tmp/RiceBaCI-fresh/rse_v2/figures")
OUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(CSV)
df = df.sort_values(["metric", "year"]).reset_index(drop=True)

# Detect EOS degeneracy: SE collapsed near zero AND/OR coef NaN
eos = df[df["metric"] == "EOS"].copy()
eos_degenerate = (eos["se"].fillna(0).max() < 1e-6) or (
    eos["se"].isna().any() or eos["coef"].isna().any()
)

# 3 rows x 1 col, taller aspect — each panel ~6 inches tall + legend strip on top
fig, axes = plt.subplots(3, 1, figsize=(14, 23))
ax_sos, ax_pos, ax_eos = axes[0], axes[1], axes[2]

panel_map = [("SOS", ax_sos, "(a)"), ("POS", ax_pos, "(b)"), ("EOS", ax_eos, "(c)")]

REF_YEAR = 2018
PRE_COLOR = "#2ca02c"   # green for pre-period
POST_COLOR = "#9467bd"  # purple for post-period

for m, ax, label in panel_map:
    sub = df[df["metric"] == m].copy()

    if m == "EOS" and eos_degenerate:
        ax.set_xlim(2013.5, 2024.5)
        ax.set_ylim(-1, 1)
        ax.axhline(0, color="black", lw=0.8, linestyle="--", alpha=0.6)
        ax.text(
            2019, 0.0,
            "Not estimable\n\nLandsat-7 SLC-off + late-monsoon cloud cover\n"
            "collapse EOS to boundary DOY 349–350.\n"
            "After FE demeaning: σ → 0, χ² → ∞, SE → 0.\n"
            "(See Table S4b caveat.)",
            ha="center", va="center", fontsize=18,
            bbox=dict(boxstyle="round,pad=0.9", facecolor="#fff3cd",
                      edgecolor="#856404", lw=1.8),
        )
        ax.set_xticks(range(2014, 2025, 1))
        ax.set_xlabel("Year", fontsize=18)
        ax.set_ylabel("Event-study coefficient β (days)", fontsize=22)
        ax.tick_params(axis="both", labelsize=15)
        ax.text(-0.06, 1.02, label, transform=ax.transAxes,
                fontsize=22, weight="bold", va="bottom", ha="left")
        ax.grid(True, alpha=0.3)
        continue

    sub = sub.sort_values("year").reset_index(drop=True)
    years = sub["year"].values
    coefs = sub["coef"].values
    ci_lo = sub["ci_lower"].values
    ci_hi = sub["ci_upper"].values
    periods = sub["period"].values

    for y, c, lo, hi, p in zip(years, coefs, ci_lo, ci_hi, periods):
        color = PRE_COLOR if p == "pre" else POST_COLOR
        ax.errorbar(
            y, c,
            yerr=[[c - lo], [hi - c]],
            fmt="o", color=color,
            markersize=13, capsize=7, capthick=2.2, lw=2.4,
            markeredgecolor="black", markeredgewidth=1.0,
        )

    # Reference year marker
    ax.scatter([REF_YEAR], [0], marker="s", s=160, color="white",
               edgecolor="black", lw=1.8, zorder=5)

    ax.axhline(0, color="black", lw=0.8, linestyle="--", alpha=0.6)
    ax.axvspan(2013.5, 2018.5, alpha=0.07, color=PRE_COLOR)
    ax.axvspan(2018.5, 2024.5, alpha=0.07, color=POST_COLOR)

    for cy in (2019, 2020, 2021):
        ax.axvline(cy, color="orange", alpha=0.35, lw=2, linestyle=":")

    ax.set_xlim(2013.5, 2024.5)
    ax.set_xticks(range(2014, 2025, 1))
    ax.set_xlabel("Year", fontsize=18)
    ax.set_ylabel("Event-study coefficient β (days)", fontsize=22)
    ax.tick_params(axis="both", labelsize=15)
    ax.text(-0.06, 1.02, label, transform=ax.transAxes,
            fontsize=22, weight="bold", va="bottom", ha="left")
    ax.grid(True, alpha=0.3)

    if m == "POS":
        pos_2016 = sub[sub["year"] == 2016]
        if len(pos_2016):
            c = pos_2016["coef"].values[0]
            ax.annotate(
                f"2016 lead: β=+{c:.1f} d, p=0.024",
                xy=(2016, c), xytext=(2014.6, c + 13),
                fontsize=19, ha="left", weight="bold",
                arrowprops=dict(arrowstyle="->", color="black", lw=1.4),
                bbox=dict(boxstyle="round,pad=0.55", facecolor="#ffe5e5",
                          edgecolor="#d62728", lw=1.4),
            )

# Shared legend inside the SOS panel (top-right, away from data)
pre_patch = mpatches.Patch(color=PRE_COLOR, alpha=0.5,
                            label="Pre-period (Landsat 2014–2017)")
post_patch = mpatches.Patch(color=POST_COLOR, alpha=0.5,
                             label="Post-period (Sentinel-2 2019–2024)")
ref_marker = plt.Line2D([0], [0], marker="s", color="w",
                         markerfacecolor="white", markeredgecolor="black",
                         markersize=14, label="Reference year 2018 (β=0)")
cyc_line = plt.Line2D([0], [0], color="orange", alpha=0.6, lw=2.5, linestyle=":",
                       label="Cyclone year (Fani 2019, Amphan 2020, Yaas 2021)")
# Place legend above the figure (anchored to the top of the SOS panel, outside)
ax_sos.legend(
    handles=[pre_patch, post_patch, ref_marker, cyc_line],
    loc="lower center", bbox_to_anchor=(0.5, 1.08),
    fontsize=18, framealpha=0.95, ncol=2,
)

plt.tight_layout(rect=[0, 0, 1, 0.96])

jpg_path = OUT_DIR / "figS2_landsat_pretrend_eventstudy.jpg"
pdf_path = OUT_DIR / "figS2_landsat_pretrend_eventstudy.pdf"
png_path = OUT_DIR / "figS2_landsat_pretrend_eventstudy.png"

fig.savefig(jpg_path, dpi=1000, format="jpg", bbox_inches="tight",
            facecolor="white")
fig.savefig(pdf_path, format="pdf", bbox_inches="tight",
            facecolor="white")
fig.savefig(png_path, dpi=300, format="png", bbox_inches="tight",
            facecolor="white")
plt.close()

print(f"OK {jpg_path}  {jpg_path.stat().st_size}")
print(f"OK {pdf_path}  {pdf_path.stat().st_size}")
print(f"OK {png_path}  {png_path.stat().st_size}")

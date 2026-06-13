"""
Figure 3 - Parallel-trends event study with 2018 as reference year.
2017 enters as pre-period lead; 2019-2024 as post-period lags.
SOS and POS only (EOS omitted - residual 2-value distribution outside 2019-2024).

Pattern matches Figure 6 (build_fig6_event_study.py):
  - font.size=18, axes labels 22pt
  - no figure-level title (caption carries it)
  - 1000 dpi JPG + PDF vector + 300 dpi PNG
  - Two panels (SOS | POS) side-by-side sharing y-axis
  - Pale-orange band marks the 2017 pre-period lead
  - Dashed vertical line at 2018 reference year (k=0)
  - Pre-period coefficients in red, post-period in blue, reference at zero

Data source: /home/user/workspace/rse_final/reviewer_rebuttal/table_S10_event_study.csv
Numbers verified verbatim from CSV at build time - never hardcoded.
"""
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import pandas as pd
import numpy as np

# --- style ---------------------------------------------------------------
mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 18,
    "axes.titlesize": 22,
    "axes.labelsize": 22,
    "xtick.labelsize": 18,
    "ytick.labelsize": 20,
    "legend.fontsize": 18,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

C_PRE = "#d62728"    # red for pre-period lead
C_POST = "#1f77b4"   # blue for post-period lags
C_BAND_PRE = "#fcd5b4"   # pale orange for pre-period band
C_BAND_POST = "#ffe5cc"  # pale orange for cyclone-year bands

# --- data ----------------------------------------------------------------
CSV = Path("/home/user/workspace/rse_final/reviewer_rebuttal/table_S10_event_study.csv")
df = pd.read_csv(CSV)
print("CSV loaded:")
print(df[["metric", "year", "period", "coef", "ci_lower", "ci_upper", "p_value"]])

OUT = Path("/home/user/workspace/rse_final/figures")
OUT.mkdir(parents=True, exist_ok=True)

# --- helper to draw one panel -------------------------------------------
def draw_panel(ax, sub, metric_label, ylim):
    years = sorted(sub.year.unique())
    # cyclone year shading (treatment events)
    for yr in [2019, 2020, 2021]:
        ax.axvspan(yr - 0.35, yr + 0.35, color=C_BAND_POST, alpha=0.55, zorder=0)
    # pre-period band (2017)
    ax.axvspan(2017 - 0.35, 2017 + 0.35, color=C_BAND_PRE, alpha=0.75, zorder=0)

    # reference year line at 2018
    ax.axvline(2018, color="#222", linestyle="--", linewidth=1.6, alpha=0.55, zorder=1)
    # zero line
    ax.axhline(0, color="#222", linestyle=":", linewidth=1.4, alpha=0.7, zorder=1)

    # plot coefficients
    for _, row in sub.iterrows():
        if pd.isna(row["coef"]):
            continue
        col = C_PRE if row["period"] == "pre" else C_POST
        # CI bar
        ax.plot([row["year"], row["year"]], [row["ci_lower"], row["ci_upper"]],
                color=col, linewidth=2.4, alpha=0.85, zorder=3)
        # caps
        cap_w = 0.12
        for y in (row["ci_lower"], row["ci_upper"]):
            ax.plot([row["year"] - cap_w, row["year"] + cap_w], [y, y],
                    color=col, linewidth=2.4, alpha=0.85, zorder=3)
        # point estimate
        ax.plot(row["year"], row["coef"], marker="o", markersize=18,
                markerfacecolor=col, markeredgecolor="black",
                markeredgewidth=1.2, zorder=5)

    # annotate the reference year (2018) at zero
    ax.plot(2018, 0, marker="o", markersize=14, markerfacecolor="white",
            markeredgecolor="#222", markeredgewidth=1.6, zorder=6)

    # axis cosmetics
    ax.set_xlim(2016.5, 2024.5)
    ax.set_xticks([2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024])
    # rotate xtick labels for clarity
    for lbl in ax.get_xticklabels():
        lbl.set_rotation(0)
    ax.set_ylim(ylim)
    ax.set_xlabel("Year")
    ax.grid(True, axis="y", alpha=0.3, linestyle=":")
    ax.set_title(metric_label, loc="left", fontweight="bold", pad=12)

# --- build figure -------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(18, 9), sharey=False)

# SOS panel
sub_sos = df[df.metric == "SOS"].copy().sort_values("year").reset_index(drop=True)
y_sos_lo = min(sub_sos.ci_lower.min(skipna=True), -40)
y_sos_hi = max(sub_sos.ci_upper.max(skipna=True), 240)
draw_panel(axes[0], sub_sos, "SOS (start of season)", (y_sos_lo - 10, y_sos_hi + 10))
axes[0].set_ylabel(r"$\hat{\beta}_k$ (days)")

# POS panel
sub_pos = df[df.metric == "POS"].copy().sort_values("year").reset_index(drop=True)
y_pos_lo = min(sub_pos.ci_lower.min(skipna=True), -40)
y_pos_hi = max(sub_pos.ci_upper.max(skipna=True), 40)
draw_panel(axes[1], sub_pos, "POS (peak of season)", (y_pos_lo - 5, y_pos_hi + 5))

# Legend (shared, placed in figure)
legend_handles = [
    Line2D([0], [0], marker="o", color="white", markerfacecolor=C_PRE,
           markeredgecolor="black", markeredgewidth=1.2, markersize=16,
           linewidth=0, label="Pre-period lead (2017)"),
    Line2D([0], [0], marker="o", color="white", markerfacecolor=C_POST,
           markeredgecolor="black", markeredgewidth=1.2, markersize=16,
           linewidth=0, label="Post-period lag"),
    Line2D([0], [0], marker="o", color="white", markerfacecolor="white",
           markeredgecolor="#222", markeredgewidth=1.6, markersize=14,
           linewidth=0, label="Reference year (2018)"),
    Patch(facecolor=C_BAND_POST, alpha=0.55, edgecolor="none",
          label="Cyclone treatment year"),
]
fig.legend(handles=legend_handles, loc="upper center", ncol=4,
           fontsize=18, frameon=True, framealpha=0.95,
           bbox_to_anchor=(0.5, 1.02), handletextpad=0.6)

# Annotate key coefficient values directly on each panel
# SOS 2017 pre-period
row = sub_sos[sub_sos.year == 2017].iloc[0]
axes[0].annotate(
    f"$\\hat{{\\beta}}_{{2017}}$ = +{row.coef:.1f} d\n95% CI [{row.ci_lower:.1f}, {row.ci_upper:.1f}]\np = {row.p_value:.2f}",
    xy=(2017, row.coef), xytext=(2017.3, row.coef + 35),
    fontsize=15, color=C_PRE,
    arrowprops=dict(arrowstyle="-", color=C_PRE, alpha=0.4, lw=1.1))

# POS 2017 pre-period
row = sub_pos[sub_pos.year == 2017].iloc[0]
axes[1].annotate(
    f"$\\hat{{\\beta}}_{{2017}}$ = +{row.coef:.1f} d\n95% CI [{row.ci_lower:.1f}, {row.ci_upper:.1f}]\np = {row.p_value:.2f}",
    xy=(2017, row.coef), xytext=(2017.3, row.coef + 12),
    fontsize=15, color=C_PRE,
    arrowprops=dict(arrowstyle="-", color=C_PRE, alpha=0.4, lw=1.1))

fig.tight_layout(rect=(0, 0, 1, 0.94))

# --- save ----------------------------------------------------------------
base = OUT / "fig3_parallel_trends"
fig.savefig(str(base) + ".jpg", dpi=1000, pil_kwargs={"quality": 95}, bbox_inches="tight")
fig.savefig(str(base) + ".pdf", bbox_inches="tight")
fig.savefig(str(base) + ".png", dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"\nSaved Figure 3 at {base}.{{jpg,pdf,png}}")

# Copy to pandoc build dir
import shutil
PANDOC_FIG = Path("/tmp/RiceBaCI-fresh/rse_v2/figures")
for ext in ("jpg", "pdf", "png"):
    src = str(base) + "." + ext
    dst = PANDOC_FIG / ("fig3_parallel_trends." + ext)
    shutil.copy2(src, dst)
print("Copied to pandoc build dir.")

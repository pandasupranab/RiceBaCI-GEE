"""
Figure 7 - District-year median SOS panel, 2019-2024, coastal vs inland.

Pattern matches Figure 6 (build_fig6_event_study.py):
  - font.size=18, axes labels 22pt
  - no figure-level title (caption carries it)
  - legend.fontsize=22 (user requested big legend on Figure 6)
  - 1000 dpi JPG + PDF vector + 300 dpi PNG

Data source: /tmp/RiceBaCI-fresh/analysis/baci_panel_real_v22.csv (v2.0 QC-passing panel)
Numbers verified from CSV at build time - never hardcoded.
"""
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import pandas as pd

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

C_TREAT = "#1f77b4"  # blue for coastal treatment
C_CTRL = "#d62728"   # red for inland control
C_BAND = "#fdd49e"   # pale orange for cyclone-year bands

# --- data ---------------------------------------------------------------
ROOT = Path("/tmp/RiceBaCI-fresh")
OUT = Path("/home/user/workspace/rse_final/figures")
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(ROOT / "analysis" / "baci_panel_real_v22.csv")
df = df[df["year"].between(2019, 2024)].copy()

treat_districts = ["Baleshwar", "Bhadrak", "Kendrapara", "Jagatsinghpur", "Puri"]
ctrl_districts = ["Angul", "Cuttack", "Dhenkanal"]

# --- figure -------------------------------------------------------------
fig, axes = plt.subplots(2, 1, figsize=(13, 11), sharex=True, sharey=True)

# Cyclone-year bands (k=0 Fani 2019; k=1 Amphan 2020; k=2 Yaas 2021)
cyclone_years = {2019: "Fani", 2020: "Amphan", 2021: "Yaas"}

# ---------------- Coastal (treatment) panel ----------------
ax = axes[0]
for yr, name in cyclone_years.items():
    ax.axvspan(yr - 0.35, yr + 0.35, color=C_BAND, alpha=0.55, zorder=0)

for d in treat_districts:
    sub = df[df["district"] == d].sort_values("year")
    ax.plot(sub["year"], sub["sos_median"], marker="o", linewidth=1.5,
            color=C_TREAT, alpha=0.45, markersize=9, label=d)

grp_t = df[df["district"].isin(treat_districts)].groupby("year")["sos_median"].mean().reset_index()
ax.plot(grp_t["year"], grp_t["sos_median"], marker="o", linewidth=4, color=C_TREAT,
        markersize=16, markeredgecolor="black", markeredgewidth=1.0, label="Coastal mean", zorder=5)

# annotate cyclone names at top of axis
ymin, ymax = 160, 250
for yr, name in cyclone_years.items():
    ax.text(yr, ymax - 4, name, ha="center", va="top", fontsize=16,
            style="italic", color="#9a3412", fontweight="bold")

ax.set_ylim(ymin, ymax)
ax.set_ylabel("SOS (DOY)")
ax.set_title("Coastal treatment districts (n = 5)", loc="left", fontweight="bold", pad=12)
ax.grid(True, alpha=0.3, linestyle=":")

# Two-column legend for coastal districts + mean
coastal_handles = [Line2D([0], [0], marker="o", color=C_TREAT, alpha=0.45,
                          markersize=10, linewidth=1.5, label=d) for d in treat_districts]
coastal_handles.append(Line2D([0], [0], marker="o", color=C_TREAT, markersize=14,
                              markeredgecolor="black", markeredgewidth=1.0,
                              linewidth=4, label="Coastal mean"))
ax.legend(handles=coastal_handles, ncol=3, fontsize=16, loc="lower right",
          framealpha=0.92, handlelength=2.2, columnspacing=1.6)

# ---------------- Inland (control) panel ----------------
ax = axes[1]
for yr, name in cyclone_years.items():
    ax.axvspan(yr - 0.35, yr + 0.35, color=C_BAND, alpha=0.55, zorder=0)

for d in ctrl_districts:
    sub = df[df["district"] == d].sort_values("year")
    ax.plot(sub["year"], sub["sos_median"], marker="s", linewidth=1.5,
            color=C_CTRL, alpha=0.45, markersize=9, linestyle="--", label=d)

grp_c = df[df["district"].isin(ctrl_districts)].groupby("year")["sos_median"].mean().reset_index()
ax.plot(grp_c["year"], grp_c["sos_median"], marker="s", linewidth=4, color=C_CTRL,
        markersize=16, markeredgecolor="black", markeredgewidth=1.0,
        linestyle="--", label="Inland mean", zorder=5)

ax.set_ylim(ymin, ymax)
ax.set_ylabel("SOS (DOY)")
ax.set_xlabel("Kharif year")
ax.set_title("Inland control districts (n = 3)", loc="left", fontweight="bold", pad=12)
ax.grid(True, alpha=0.3, linestyle=":")

inland_handles = [Line2D([0], [0], marker="s", color=C_CTRL, alpha=0.45,
                         markersize=10, linewidth=1.5, linestyle="--", label=d) for d in ctrl_districts]
inland_handles.append(Line2D([0], [0], marker="s", color=C_CTRL, markersize=14,
                             markeredgecolor="black", markeredgewidth=1.0,
                             linewidth=4, linestyle="--", label="Inland mean"))
# pale-orange cyclone band as legend entry
inland_handles.append(Patch(facecolor=C_BAND, alpha=0.55, edgecolor="none",
                            label="Cyclone year"))
ax.legend(handles=inland_handles, ncol=3, fontsize=16, loc="lower right",
          framealpha=0.92, handlelength=2.2, columnspacing=1.6)

# --- x-axis -------------------------------------------------------------
for ax in axes:
    ax.set_xlim(2018.55, 2024.45)
    ax.set_xticks([2019, 2020, 2021, 2022, 2023, 2024])

fig.tight_layout()

# --- save ---------------------------------------------------------------
base = OUT / "fig7_district_sos_panel"
fig.savefig(str(base) + ".jpg", dpi=1000, pil_kwargs={"quality": 95}, bbox_inches="tight")
fig.savefig(str(base) + ".pdf", bbox_inches="tight")
fig.savefig(str(base) + ".png", dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"Saved Figure 7 at {base}.{{jpg,pdf,png}}")

# Also copy to pandoc build dir
import shutil
PANDOC_FIG = Path("/tmp/RiceBaCI-fresh/rse_v2/figures")
for ext in ("jpg", "pdf", "png"):
    src = str(base) + "." + ext
    dst = PANDOC_FIG / ("fig7_district_sos_panel." + ext)
    shutil.copy2(src, dst)
print("Copied to pandoc build dir.")

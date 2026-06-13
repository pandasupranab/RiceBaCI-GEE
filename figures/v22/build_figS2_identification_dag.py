"""
Figure S2 — Identification DAG: boundary-quantisation artefact and the QC intercept.

Standardised build:
- No figure-level title (caption carries it)
- Larger figsize and font sizes consistent with Fig S1
- Outputs to BOTH /home/user/workspace/rse_final/figures/ AND
  /tmp/RiceBaCI-fresh/rse_v2/figures/ at 1000 DPI (JPG), vector PDF, 300 DPI PNG
"""
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 20,
    "axes.titlesize": 28,
    "axes.labelsize": 22,
    "xtick.labelsize": 18,
    "ytick.labelsize": 18,
    "legend.fontsize": 18,
})

OUT_FINAL = Path("/home/user/workspace/rse_final/figures")
OUT_REPO  = Path("/tmp/RiceBaCI-fresh/rse_v2/figures")
OUT_FINAL.mkdir(parents=True, exist_ok=True)
OUT_REPO.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(20, 12))
ax.set_xlim(-3, 105)
ax.set_ylim(-2, 95)
ax.axis("off")

# Box sizes (bigger so larger text fits without wrap)
def dag_node(x, y, w, h, text, fc, fs=22, fw="normal"):
    p = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                       boxstyle="round,pad=0.45,rounding_size=1.5",
                       facecolor=fc, edgecolor="black", lw=1.6, zorder=2)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center",
            fontsize=fs, fontweight=fw, zorder=3, wrap=True)

def dag_arrow(x1, y1, x2, y2, label="", color="black", style="-|>", lw=2.2,
              labx=None, laby=None, linestyle="-"):
    ar = FancyArrowPatch((x1, y1), (x2, y2),
                         arrowstyle=style, mutation_scale=24,
                         color=color, lw=lw, linestyle=linestyle, zorder=1)
    ax.add_patch(ar)
    if label:
        if labx is None: labx = (x1 + x2) / 2
        if laby is None: laby = (y1 + y2) / 2 + 1.5
        ax.text(labx, laby, label, ha="center", va="center",
                fontsize=18, style="italic", color="#444",
                bbox=dict(facecolor="white", edgecolor="none", pad=1.5))

# Common source (left) — shifted right so left border is not clipped
dag_node(10, 50, 16, 10, "Cyclone\nlandfall", fc="#FFCDD2", fs=24, fw="bold")

# --------------------- Top pathway (agronomic, real) --------------------------
dag_node(30, 80, 24, 11, "Storm-surge inundation\n& rainfall anomaly", fc="#D6EAF8", fs=20)
dag_node(56, 80, 22, 11, "Transplanting /\nharvest delay", fc="#D6EAF8", fs=20)
dag_node(78, 80, 20, 11, "Real phenometric\nshift", fc="#D6EAF8", fs=20)
dag_node(96, 80, 13, 11, "DiD\ncoefficient", fc="#AED6F1", fs=22, fw="bold")

dag_arrow(17, 54, 23, 75)
dag_arrow(42, 80, 45, 80)
dag_arrow(67, 80, 68, 80)
dag_arrow(88, 80, 89.5, 80)

# --------------------- Bottom pathway (artefact) ------------------------------
dag_node(28, 22, 28, 11, "Late-senescence pixels\n(coastal-correlated)", fc="#FADBD8", fs=20)
dag_node(58, 22, 28, 11, "Fitting window truncates\nNDVI descending limb", fc="#FADBD8", fs=20)
dag_node(88, 22, 28, 11, "Optimiser assigns\nboundary DOY (349 / 288)", fc="#FADBD8", fs=20)

# QC operator banner
ax.add_patch(FancyBboxPatch((4, 0.5), 92, 9,
                            boxstyle="round,pad=0.5,rounding_size=1.8",
                            facecolor="#D5F5E3", edgecolor="#1E8449",
                            lw=2.0, zorder=2))
ax.text(50, 5, "QC framework intercepts the artefact arm:\n"
               "Gate A (mode-share ≤ 0.20) + Gate C (RMSR ≤ 0.15) → contaminated cells removed before DiD",
        ha="center", va="center", fontsize=20, fontweight="bold",
        color="#155724", zorder=3)

# Vertical green arrow from QC banner up to artefact-pathway middle node
dag_arrow(58, 9.5, 58, 16.5, color="#1E8449", lw=3.0, style="-|>")

# Arrows in artefact pathway
dag_arrow(17, 46, 22, 27)
dag_arrow(42, 22, 44, 22)
dag_arrow(72, 22, 74, 22)

# Spurious DiD arrow (would-be) — from artefact end node up to DiD coefficient
dag_arrow(96, 27.5, 96, 74.5,
          color="#943126", style="-|>", lw=2.4, linestyle="--")

# X marker overlay (block)
ax.add_patch(FancyBboxPatch((93.5, 47), 5, 7,
                            boxstyle="round,pad=0.3",
                            facecolor="white", edgecolor="none", zorder=4))
ax.text(96, 51, "✗", fontsize=52, color="#943126", fontweight="bold",
        ha="center", va="center", zorder=5)
ax.text(96, 41.5, "blocked\nby QC", fontsize=18, color="#943126",
        ha="center", va="top", style="italic", zorder=5)

ax.text(85, 60, "would-be\nspurious DiD", fontsize=18, color="#943126",
        ha="center", style="italic", zorder=5,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                  edgecolor="#943126", lw=1.2))

# District / year FEs annotation (centre, between pathways)
ax.text(50, 58, "District and year fixed effects do not break the artefact arm:\n"
                "boundary contamination is systematically more prevalent in\n"
                "coastal (treatment) districts than in inland controls.",
        ha="center", fontsize=22, style="italic", color="#444",
        bbox=dict(boxstyle="round,pad=0.9", facecolor="#FFFDF5",
                  edgecolor="#E5D9A8", lw=1.4))

fig.tight_layout()

# Save outputs to both destinations (filename retained as figS3_* to match supplement.md)
for OUT in [OUT_FINAL, OUT_REPO]:
    fig.savefig(OUT / "figS3_identification_dag.jpg",
                dpi=1000, pil_kwargs={"quality": 95}, bbox_inches="tight")
    fig.savefig(OUT / "figS3_identification_dag.pdf", bbox_inches="tight")
    fig.savefig(OUT / "figS3_identification_dag.png",
                dpi=300, bbox_inches="tight")
plt.close(fig)
print("Saved Fig S3 to:")
print(f"  {OUT_FINAL}")
print(f"  {OUT_REPO}")

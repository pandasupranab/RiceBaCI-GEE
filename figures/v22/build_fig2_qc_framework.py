"""
Build Figure 6 — QC framework flowchart (three-gate sequential pipeline).

Pattern matches Figures 2, 3, and 4:
- Bigger fonts (font.size=18, axes labels=22)
- NO title (caption carries it)
- 1000 dpi JPG (embedded) + PDF vector archive + PNG legacy

This is a schematic / flowchart, not a data plot — but all annotated
empirical numbers are read VERBATIM from the canonical Table 2 values
in §3.4 of the manuscript:

  v1.0.2 → v2.0 mode-shares:
    SOS: 0.203 → 0.125   (Gate A: pass → pass; closer to threshold pre-QC)
    POS: 0.656 → 0.083   (Gate A: fail → pass)
    EOS: 0.727 → 0.083   (Gate A: fail → pass)

  v1.0.2 → v2.0 unique-DOY counts:
    SOS: 11 → 36
    POS:  5 → 33
    EOS:  2 → 38

Outputs:
  figures/fig2_qc_framework.jpg  (1000 dpi, embedded)
  figures/fig2_qc_framework.pdf  (vector archive)
  figures/fig2_qc_framework.png  (legacy 300 dpi)
"""
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path("/home/user/workspace/rse_final/figures")
OUT.mkdir(parents=True, exist_ok=True)

# Bigger-font rc — matched to other figures
mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 16,
    "axes.titlesize": 22,
})

# Palette
C_INPUT   = "#e8e8e8"  # neutral grey for input
C_STAGE   = "#cfe2f3"  # light blue for processing stages
C_GATE_BG = "#fff2cc"  # light gold for the QC gate container
C_GATE_BD = "#bf9000"  # dark gold border for QC gates
C_PASS    = "#d5e8d4"  # light green for PASS
C_PASS_BD = "#6aa84f"  # green border
C_FAIL    = "#f8cecc"  # light red for FAIL
C_FAIL_BD = "#b85450"  # red border
C_VALID   = "#e8f0ff"  # very light blue for validation strip
C_VALID_BD = "#1f77b4"

fig, ax = plt.subplots(figsize=(20, 14))
ax.set_xlim(0, 20)
ax.set_ylim(0, 14)
ax.set_aspect("equal")
ax.axis("off")


def box(x, y, w, h, text, fc, ec="black", fontweight="normal", fontsize=15,
        text_color="black", lw=1.5):
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.12",
        fc=fc, ec=ec, lw=lw,
    )
    ax.add_patch(rect)
    if text:
        ax.text(x + w / 2, y + h / 2, text,
                ha="center", va="center",
                fontsize=fontsize, fontweight=fontweight,
                color=text_color)


def arrow(x1, y1, x2, y2, label="", lw=2.0, label_fontsize=14,
          label_color="#333", label_dx=0.25, label_dy=0):
    a = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=22,
        color="black", lw=lw,
    )
    ax.add_patch(a)
    if label:
        ax.text((x1 + x2) / 2 + label_dx, (y1 + y2) / 2 + label_dy, label,
                fontsize=label_fontsize, color=label_color, fontweight="bold")


# ============================================================================
# TOP: Input
# ============================================================================
box(7.0, 12.6, 6.0, 1.0,
    "Sentinel-2 L2A NDVI time series\n(cell-level, Kharif window 2019–2024)",
    fc=C_INPUT, fontweight="bold", fontsize=15)


# ============================================================================
# Stage A and Stage B (preprocessing)
# ============================================================================
box(1.5, 10.7, 7.5, 1.2,
    "Stage A — Dekadal NDVI compositing\n(10-day max-NDVI; ESA WorldCover crop mask;\nSentinel-2 SCL cloud screening)",
    fc=C_STAGE, fontweight="bold", fontsize=14)
box(11.0, 10.7, 7.5, 1.2,
    "Stage B — Double-logistic phenometric extraction\n(Whittaker smoother → 6-parameter fit;\nSOS / POS / EOS retrieval)",
    fc=C_STAGE, fontweight="bold", fontsize=14)

# Arrows from input down to Stage A and Stage B
arrow(9.0, 12.55, 5.25, 11.95, lw=2.0)
arrow(11.0, 12.55, 14.75, 11.95, lw=2.0)
# Horizontal arrow from Stage A → Stage B
arrow(9.05, 11.3, 10.95, 11.3, lw=2.0)


# ============================================================================
# QC FRAMEWORK container (the paper's contribution)
# ============================================================================
# Outer container
ax.add_patch(FancyBboxPatch(
    (0.5, 5.4), 19.0, 4.5,
    boxstyle="round,pad=0.18",
    fc=C_GATE_BG, ec=C_GATE_BD, lw=2.2,
))
ax.text(10.0, 9.45, "QC FRAMEWORK   (the primary contribution of this paper)",
        ha="center", va="center", fontsize=20, fontweight="bold",
        color=C_GATE_BD)

# Three gates as parallel columns
# Gate A: mode-share threshold
ax.text(3.7, 8.85, "GATE A", ha="center", va="center",
        fontsize=18, fontweight="bold")
ax.text(3.7, 8.35, "Mode-share threshold", ha="center", va="center",
        fontsize=15, fontstyle="italic", color="#555")
ax.text(3.7, 7.45,
        "Panel-wide mode-share\n(fraction at single DOY)\n≤ 0.20  for SOS, POS, EOS",
        ha="center", va="center", fontsize=14)
ax.text(3.7, 6.20,
        "v1.0.2 (raw):\nSOS 0.203 • POS 0.656 • EOS 0.727",
        ha="center", va="center", fontsize=12.5, color=C_FAIL_BD,
        fontweight="bold")
ax.text(3.7, 5.75,
        "v2.0 (refit):\nSOS 0.125 • POS 0.083 • EOS 0.083",
        ha="center", va="center", fontsize=12.5, color=C_PASS_BD,
        fontweight="bold")

# Gate B: biological plausibility
ax.text(10.0, 8.85, "GATE B", ha="center", va="center",
        fontsize=18, fontweight="bold")
ax.text(10.0, 8.35, "Biological plausibility", ha="center", va="center",
        fontsize=15, fontstyle="italic", color="#555")
ax.text(10.0, 7.45,
        "Median DOY within Kharif rice\nagronomic windows:\n"
        "SOS  ∈  [155, 240]\nPOS  ∈  [240, 320]\nEOS  ∈  [280, 380]",
        ha="center", va="center", fontsize=14)
ax.text(10.0, 5.95,
        "v2.0 observed ranges:\n"
        "SOS 168–241 • POS 256–304 • EOS 320–374",
        ha="center", va="center", fontsize=12.5, color=C_PASS_BD,
        fontweight="bold")

# Gate C: fit-quality screening
ax.text(16.3, 8.85, "GATE C", ha="center", va="center",
        fontsize=18, fontweight="bold")
ax.text(16.3, 8.35, "Fit-quality screening", ha="center", va="center",
        fontsize=15, fontstyle="italic", color="#555")
ax.text(16.3, 7.45,
        "Per-pixel RMSR  ≤  0.15 NDVI units\n"
        "Cell excluded if  > 30%  of pixels\nflagged as poor-fit",
        ha="center", va="center", fontsize=14)
ax.text(16.3, 6.05,
        "v2.0 panel-avg fit-fail rate:\n0.61  (no cell  >  30%)",
        ha="center", va="center", fontsize=12.5, color=C_PASS_BD,
        fontweight="bold")

# Vertical dividers between gates
ax.plot([6.85, 6.85], [5.8, 9.2], color=C_GATE_BD, lw=1.0, alpha=0.6)
ax.plot([13.15, 13.15], [5.8, 9.2], color=C_GATE_BD, lw=1.0, alpha=0.6)

# Arrows from Stage A/B down into the QC container
arrow(5.25, 10.65, 5.25, 9.95, lw=2.0)
arrow(14.75, 10.65, 14.75, 9.95, lw=2.0)


# ============================================================================
# Decision diamond (rendered as rounded box for simplicity)
# ============================================================================
box(7.5, 3.7, 5.0, 1.1,
    "All three gates passed?",
    fc="#ffe6cc", ec=C_GATE_BD, fontweight="bold", fontsize=16, lw=2.0)

# Arrow from QC container down into decision
arrow(10.0, 5.35, 10.0, 4.85, lw=2.0)


# ============================================================================
# PASS / FAIL outcomes
# ============================================================================
box(1.5, 1.8, 7.0, 1.4,
    "PASS\n→ District-year cell enters\nDiD estimation panel\n(n = 48; Models 1 and 2)",
    fc=C_PASS, ec=C_PASS_BD, fontweight="bold", fontsize=14, lw=2.0)
box(11.5, 1.8, 7.0, 1.4,
    "FAIL\n→ Cell flagged and excluded\nfrom DiD panel\n(reason code logged)",
    fc=C_FAIL, ec=C_FAIL_BD, fontweight="bold", fontsize=14, lw=2.0)

# Decision branches
arrow(8.5, 3.7, 5.0, 3.25, lw=2.0)
arrow(11.5, 3.7, 15.0, 3.25, lw=2.0)
ax.text(6.4, 3.55, "yes", fontsize=15, fontweight="bold", color=C_PASS_BD)
ax.text(13.3, 3.55, "no", fontsize=15, fontweight="bold", color=C_FAIL_BD)


# ============================================================================
# Empirical-validation strip at the bottom
# ============================================================================
ax.add_patch(FancyBboxPatch(
    (0.5, 0.15), 19.0, 1.25,
    boxstyle="round,pad=0.10",
    fc=C_VALID, ec=C_VALID_BD, lw=2.0,
))
ax.text(10.0, 1.20,
        "EMPIRICAL VALIDATION — Odisha panel, 2019–2024, 8 districts × 6 years",
        ha="center", va="center", fontsize=15, fontweight="bold",
        color=C_VALID_BD)
# Three validation columns
ax.text(3.7, 0.55,
        "EOS mode-share\n0.727  →  0.083",
        ha="center", va="center", fontsize=13)
ax.text(10.0, 0.55,
        "POS mode-share\n0.656  →  0.083",
        ha="center", va="center", fontsize=13)
ax.text(16.3, 0.55,
        "Unique EOS DOY values\n2  →  38",
        ha="center", va="center", fontsize=13)

# Vertical dividers in the validation strip
ax.plot([6.85, 6.85], [0.25, 1.0], color=C_VALID_BD, lw=0.8, alpha=0.5)
ax.plot([13.15, 13.15], [0.25, 1.0], color=C_VALID_BD, lw=0.8, alpha=0.5)


# ============================================================================
# Outputs — JPG (embedded), PDF (vector), PNG (legacy 300 dpi)
# ============================================================================
fig.savefig(OUT / "fig2_qc_framework.jpg", dpi=1000,
            pil_kwargs={"quality": 95}, bbox_inches="tight")
fig.savefig(OUT / "fig2_qc_framework.pdf", bbox_inches="tight")
fig.savefig(OUT / "fig2_qc_framework.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"Saved Fig 5 → {OUT}/fig2_qc_framework.{{jpg,pdf,png}}")

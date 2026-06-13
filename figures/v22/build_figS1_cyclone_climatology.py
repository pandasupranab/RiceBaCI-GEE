"""
Figure S1 - Bay of Bengal pre-Kharif cyclone climatology 1990-2024.

Two panels:
  (A) Bay of Bengal coastline map with all pre-Kharif landfall sites
      (DOY 90-180) for 1990-2024, sized by WMO peak intensity,
      with Fani/Amphan/Yaas treatment events highlighted as stars.
  (B) Pre-Kharif landfall intensity vs day-of-year scatter,
      with Saffir-Simpson equivalent intensity bands.

Pattern matches main-text figures (build_fig*.py):
  - font.size=18, axes labels 22pt
  - no figure-level title (caption carries it)
  - 1000 dpi JPG + PDF vector + 300 dpi PNG

Data source: /tmp/RiceBaCI-fresh/rse_v2/data_fig1/ibtracs.NI.list.v04r01.csv
Filter: SUBBASIN=BB, LANDFALL==0 (landfall observation), LAT 18-23, LON 82-92,
        DOY 90-180 (pre-Kharif Apr-Jun), SEASON 1990-2024.
"""
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature

mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 24,
    "axes.titlesize": 30,
    "axes.labelsize": 28,
    "xtick.labelsize": 24,
    "ytick.labelsize": 24,
    "legend.fontsize": 22,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# ---- load and filter ---------------------------------------------------
SRC = Path("/tmp/RiceBaCI-fresh/rse_v2/data_fig1/ibtracs.NI.list.v04r01.csv")
OUT = Path("/home/user/workspace/rse_final/figures")
OUT.mkdir(parents=True, exist_ok=True)

src = pd.read_csv(SRC, skiprows=[1], low_memory=False)
src["WMO_WIND"] = pd.to_numeric(src["WMO_WIND"], errors="coerce")
src["LAT"] = pd.to_numeric(src["LAT"], errors="coerce")
src["LON"] = pd.to_numeric(src["LON"], errors="coerce")
src["LANDFALL"] = pd.to_numeric(src["LANDFALL"], errors="coerce")
src["ISO_TIME"] = pd.to_datetime(src["ISO_TIME"], errors="coerce")
src["DOY"] = src["ISO_TIME"].dt.dayofyear

lf = src[src["LANDFALL"] == 0].sort_values(["SID", "ISO_TIME"]).groupby("SID").first().reset_index()

bb = lf[(lf["SUBBASIN"] == "BB") &
        (lf["LAT"].between(18, 23)) &
        (lf["LON"].between(82, 92)) &
        (lf["DOY"].between(90, 180)) &
        (lf["SEASON"] >= 1990) &
        (lf["SEASON"] <= 2024)].copy()
wmo_peak = src.groupby("SID")["WMO_WIND"].max().reset_index().rename(columns={"WMO_WIND": "wmo_peak"})
bb = bb.merge(wmo_peak, on="SID")
print(f"Pre-Kharif Odisha-Bengal landfalls 1990-2024: n={len(bb)}")

TREATMENT = {"FANI": "#0E7C7B", "AMPHAN": "#C2185B", "YAAS": "#F57C00"}
bb["is_treatment"] = bb["NAME"].isin(TREATMENT.keys())
others = bb[~bb["is_treatment"]].copy()
treat = bb[bb["is_treatment"]].copy()

# ---- figure ------------------------------------------------------------
fig = plt.figure(figsize=(16, 22))
gs = fig.add_gridspec(2, 1, height_ratios=[1, 1])

# ========== Panel A: spatial landfall map (cartopy) ==========
axA = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
axA.set_extent([81.5, 92.3, 17, 24], crs=ccrs.PlateCarree())
# Real Natural Earth coastline / land
axA.add_feature(cfeature.LAND.with_scale("10m"), facecolor="#E8E2D4", edgecolor="#888", linewidth=0.8, zorder=1)
axA.add_feature(cfeature.OCEAN.with_scale("10m"), facecolor="#D6E4F0", zorder=0)
axA.add_feature(cfeature.COASTLINE.with_scale("10m"), edgecolor="#666", linewidth=0.8, zorder=2)

# Non-treatment landfalls: scaled circles by WMO peak (NaN -> small fixed size)
sizes_other = others["wmo_peak"].fillna(25).clip(lower=20) * 1.8
axA.scatter(others["LON"], others["LAT"], s=sizes_other,
            facecolor="#888", edgecolor="#333", linewidth=0.6, alpha=0.55,
            zorder=3, label="Other pre-Kharif landfalls")

# Snap each treatment landfall to the nearest land point.
# IBTrACS records the landfall fix at a 3-hourly timestamp, which can
# fall a few km offshore depending on subgrid track timing. Visually
# snapping the marker to the nearest Natural Earth land vertex keeps
# the figure faithful to the event while avoiding the "star in the water"
# artefact.
from shapely.geometry import Point
from shapely.ops import nearest_points, unary_union
import cartopy.io.shapereader as shpreader

from shapely.geometry import box as shp_box
_land_reader = shpreader.Reader(shpreader.natural_earth(resolution="10m", category="physical", name="land"))
_clip = shp_box(80, 15, 95, 26)
_local_land = unary_union([g.intersection(_clip) for g in _land_reader.geometries() if g.intersects(_clip)])

def snap_to_land(lon, lat):
    p = Point(lon, lat)
    if _local_land.contains(p):
        return lon, lat
    nearest = nearest_points(_local_land, p)[0]
    # Nudge a touch further inland (0.05 deg ~5 km) along the same direction
    dx, dy = nearest.x - lon, nearest.y - lat
    norm = (dx*dx + dy*dy) ** 0.5
    if norm > 0:
        nx, ny = nearest.x + 0.05 * dx/norm, nearest.y + 0.05 * dy/norm
    else:
        nx, ny = nearest.x, nearest.y
    return nx, ny

# Treatment cyclones: large coloured stars (snapped to land)
for _, row in treat.iterrows():
    col = TREATMENT[row["NAME"]]
    snap_lon, snap_lat = snap_to_land(row["LON"], row["LAT"])
    axA.scatter(snap_lon, snap_lat, marker="*", s=900,
                facecolor=col, edgecolor="black", linewidth=1.4, zorder=6)
    # name label
    axA.text(snap_lon - 0.2, snap_lat + 0.35, row["NAME"].title(),
             fontsize=24, fontweight="bold", color=col,
             ha="center", va="bottom", zorder=7)

# Bay of Bengal label
axA.text(86, 18.0, "Bay of Bengal", fontsize=22, color="#3A6A8A",
         style="italic", ha="center", va="center", zorder=2)
axA.text(85.0, 22.5, "Odisha\n(study area)", fontsize=20, color="#444",
         ha="center", va="center", zorder=2)
axA.text(89.5, 23.3, "Bangladesh", fontsize=20, color="#555",
         ha="center", va="center", zorder=2)

axA.set_xlabel("Longitude (°E)")
axA.set_ylabel("Latitude (°N)")
axA.set_title("(A)", loc="left", fontweight="bold", pad=10)
# Gridlines with labels on left + bottom only
gl = axA.gridlines(draw_labels=True, alpha=0.25, linestyle=":", color="#888")
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {"size": 24}
gl.ylabel_style = {"size": 24}

# Compass arrow
axA.annotate("N", xy=(82.5, 23.5), xytext=(82.5, 23.0),
             arrowprops=dict(arrowstyle="-|>", color="black", lw=2.0),
             fontsize=22, fontweight="bold", ha="center")

# Panel A legend
legA = [
    Line2D([0], [0], marker="o", color="white", markerfacecolor="#888",
           markeredgecolor="#333", markersize=12, linewidth=0,
           label=f"IBTrACS 1990\u20132024 (n={len(others)})"),
    Line2D([0], [0], marker="*", color="white", markerfacecolor=TREATMENT["FANI"],
           markeredgecolor="black", markersize=20, linewidth=0,
           label="Fani (2019)"),
    Line2D([0], [0], marker="*", color="white", markerfacecolor=TREATMENT["AMPHAN"],
           markeredgecolor="black", markersize=20, linewidth=0,
           label="Amphan (2020)"),
    Line2D([0], [0], marker="*", color="white", markerfacecolor=TREATMENT["YAAS"],
           markeredgecolor="black", markersize=20, linewidth=0,
           label="Yaas (2021)"),
]
axA.legend(handles=legA, loc="lower right", framealpha=0.92, fontsize=20)

# ========== Panel B: intensity vs DOY ==========
axB = fig.add_subplot(gs[1, 0])
# Saffir-Simpson equivalent bands (intensity in kt)
# Cat 1: 64-82, Cat 2: 83-95, Cat 3: 96-112, Cat 4: 113-136, Cat 5: 137+
ss_bands = [
    (33, 63, "TS / Cyclonic Storm", "#FFFEF0"),
    (64, 82, "Cat 1", "#FFF2CC"),
    (83, 95, "Cat 2", "#FFE0A8"),
    (96, 112, "Cat 3", "#FFC078"),
    (113, 136, "Cat 4", "#FF8888"),
    (137, 180, "Cat 5", "#D85E5E"),
]
for lo, hi, lab, col in ss_bands:
    axB.axhspan(lo, hi, color=col, alpha=0.6, zorder=0)
    axB.text(180, (lo + hi) / 2, lab, fontsize=18, ha="right",
             va="center", color="#444", alpha=0.8, zorder=1)

# Other landfalls
axB.scatter(others["DOY"], others["wmo_peak"], s=110,
            facecolor="#666", edgecolor="black", linewidth=0.6, alpha=0.75,
            zorder=3, label=f"IBTrACS 1990\u20132024 (n={others.wmo_peak.notna().sum()})")

# Treatment cyclones
for _, row in treat.iterrows():
    col = TREATMENT[row["NAME"]]
    axB.scatter(row["DOY"], row["wmo_peak"], marker="*", s=550,
                facecolor=col, edgecolor="black", linewidth=1.4, zorder=6)
    # annotate name with peak wind and DOY
    axB.annotate(f"{row['NAME'].title()}\n{int(row['wmo_peak'])} kt, DOY {row['DOY']}",
                 xy=(row["DOY"], row["wmo_peak"]),
                 xytext=(row["DOY"] + 4, row["wmo_peak"] + 6),
                 fontsize=20, color=col, fontweight="bold",
                 arrowprops=dict(arrowstyle="-", color=col, alpha=0.5, lw=1.3))

axB.set_xlim(88, 181)
axB.set_ylim(20, 175)
axB.set_xlabel("Landfall day-of-year (DOY)")
axB.set_ylabel("WMO peak 1-min sustained wind (kt)")
axB.set_title("(B)", loc="left", fontweight="bold", pad=10)
axB.grid(True, alpha=0.25, linestyle=":")

# Panel B legend (top-left)
legB = [
    Line2D([0], [0], marker="o", color="white", markerfacecolor="#666",
           markeredgecolor="black", markersize=11, linewidth=0,
           label=f"IBTrACS 1990\u20132024 (n={others.wmo_peak.notna().sum()})"),
    Line2D([0], [0], marker="*", color="white", markerfacecolor=TREATMENT["FANI"],
           markeredgecolor="black", markersize=18, linewidth=0,
           label="Fani 2019"),
    Line2D([0], [0], marker="*", color="white", markerfacecolor=TREATMENT["AMPHAN"],
           markeredgecolor="black", markersize=18, linewidth=0,
           label="Amphan 2020"),
    Line2D([0], [0], marker="*", color="white", markerfacecolor=TREATMENT["YAAS"],
           markeredgecolor="black", markersize=18, linewidth=0,
           label="Yaas 2021"),
]
axB.legend(handles=legB, loc="upper left", framealpha=0.95, fontsize=20)

fig.tight_layout()

# ---- save -------------------------------------------------------------
base = OUT / "figS1_cyclone_climatology"
fig.savefig(str(base) + ".jpg", dpi=1000, pil_kwargs={"quality": 95}, bbox_inches="tight")
fig.savefig(str(base) + ".pdf", bbox_inches="tight")
fig.savefig(str(base) + ".png", dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"Saved Figure S1 at {base}.{{jpg,pdf,png}}")

# Copy to pandoc build dir
import shutil
PANDOC_FIG = Path("/tmp/RiceBaCI-fresh/rse_v2/figures")
for ext in ("jpg", "pdf", "png"):
    src = str(base) + "." + ext
    dst = PANDOC_FIG / ("figS1_cyclone_climatology." + ext)
    shutil.copy2(src, dst)
print("Copied to pandoc build dir.")

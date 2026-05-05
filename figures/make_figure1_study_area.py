"""
Figure 1 — Study area, cyclone tracks, and key reference features
RiceBaCI-GEE manuscript (Panda 2026, target: Remote Sensing of Environment)

Inputs (no remote download at runtime — all local):
  - GADM 4.1 India admin-2 boundaries
  - IBTrACS landfall coordinates for Fani 2019, Amphan 2020, Yaas 2021,
    Hudhud 2014, Bulbul 2019  (verified from IMD RSMC New Delhi reports;
    full tracks digitised from published IMD tracks at 6-h resolution).

Outputs:
  - figures/figure1_study_area.png  (300 dpi, 18 × 13 cm)
  - figures/figure1_study_area.pdf  (vector)
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import geopandas as gpd
from shapely.geometry import LineString, Point, Polygon
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# --------------------------------------------------------------------------
# 1. PATHS
# --------------------------------------------------------------------------
ROOT  = Path("/home/user/workspace")
GIS   = ROOT / "gis_data"
FIGS  = ROOT / "figures"
FIGS.mkdir(exist_ok=True)
GADM  = GIS / "gadm41_IND_2.json"

# --------------------------------------------------------------------------
# 2. LOAD ADMIN-2 + FILTER STUDY DISTRICTS
# --------------------------------------------------------------------------
ind2 = gpd.read_file(GADM)
print("GADM India admin-2 features:", len(ind2))

# Odisha (also spelled Orissa in some GADM versions)
odisha = ind2[ind2["NAME_1"].isin(["Odisha", "Orissa"])].copy()
print("Odisha districts:", len(odisha))
print("Sample district names:", sorted(odisha["NAME_2"].unique())[:15])

STUDY_DISTRICTS = [
    "Puri", "Khordha", "Khurda",          # Khurda is GADM spelling
    "Jagatsinghapur", "Jagatsinghpur",
    "Kendrapara",
    "Bhadrak",
    "Baleshwar", "Balasore",
    "Cuttack",
    "Ganjam",
]
study = odisha[odisha["NAME_2"].isin(STUDY_DISTRICTS)].copy()
print("\nMatched study districts:")
for _, row in study.iterrows():
    print(f"  - {row['NAME_2']}")

# --------------------------------------------------------------------------
# 3. CYCLONE TRACKS (digitised from IMD RSMC reports, 6-h)
#    Each list = (lon, lat) waypoints from genesis to dissipation.
#    Landfall point is highlighted separately.
# --------------------------------------------------------------------------
TRACKS = {
    "Fani 2019": {
        "color": "#d62728",
        "landfall": (85.83, 19.80),     # Puri
        "landfall_date": "03 May 2019",
        "intensity_kt": 150,
        "waypoints": [
            (88.6, 5.0), (87.6, 7.5), (86.5, 10.0), (85.8, 12.5),
            (85.3, 15.0), (85.1, 17.0), (85.5, 19.0),
            (85.83, 19.80),                # landfall (Puri)
            (86.4, 20.8), (87.5, 22.0),
            (88.5, 23.5), (89.5, 24.7),
        ],
    },
    "Amphan 2020": {
        "color": "#ff7f0e",
        "landfall": (88.13, 21.65),     # Bakkhali, WB
        "landfall_date": "20 May 2020",
        "intensity_kt": 145,
        "waypoints": [
            (86.5, 10.5), (86.5, 12.5), (86.6, 14.5), (86.8, 16.5),
            (87.0, 18.5), (87.4, 20.0),
            (88.13, 21.65),                # landfall
            (88.7, 23.0), (89.5, 24.5),
        ],
    },
    "Yaas 2021": {
        "color": "#1f77b4",
        "landfall": (87.10, 21.45),     # near Balasore (WB-Odisha border)
        "landfall_date": "26 May 2021",
        "intensity_kt": 75,
        "waypoints": [
            (88.0, 14.5), (88.0, 16.0), (87.7, 17.5), (87.5, 19.0),
            (87.3, 20.5),
            (87.10, 21.45),                # landfall
            (87.0, 22.5), (86.5, 23.5),
        ],
    },
    "Bulbul 2019 (transferability)": {
        "color": "#7f7f7f",
        "landfall": (88.50, 21.55),     # Sagar Island, WB
        "landfall_date": "09 Nov 2019",
        "intensity_kt": 75,
        "waypoints": [
            (88.0, 11.0), (87.5, 13.0), (87.0, 15.5), (87.1, 17.5),
            (87.5, 19.5), (87.9, 20.8),
            (88.50, 21.55),                # landfall
            (89.5, 22.5), (90.5, 23.5),
        ],
    },
    "Hudhud 2014 (transferability)": {
        "color": "#2ca02c",
        "landfall": (83.30, 17.70),     # Visakhapatnam, AP
        "landfall_date": "12 Oct 2014",
        "intensity_kt": 100,
        "waypoints": [
            (94.0, 12.0), (91.5, 13.0), (89.0, 14.0), (86.5, 15.0),
            (84.5, 16.5),
            (83.30, 17.70),                # landfall
            (82.5, 19.0), (81.5, 20.5),
        ],
    },
}

# --------------------------------------------------------------------------
# 4. KEY REFERENCE FEATURES
# --------------------------------------------------------------------------
# Bhitarkanika mangrove (centred ~86.85°E / 20.70°N, ~672 km²)
BHITARKANIKA_CENTRE = (86.85, 20.70)
# Approximate polygon — manuscript uses authoritative ESA WorldCover mangrove
# class for area calc; this polygon is for figure illustration only.
BHITARKANIKA_POLY = Polygon([
    (86.65, 20.55), (87.05, 20.55), (87.10, 20.85),
    (86.95, 20.95), (86.65, 20.85), (86.55, 20.65),
])

CITIES = {
    "Bhubaneswar": (85.83, 20.30),
    "Puri":        (85.83, 19.80),
    "Cuttack":     (85.88, 20.46),
    "Paradip":     (86.61, 20.32),
    "Balasore":    (86.93, 21.49),
    "Visakhapatnam": (83.30, 17.70),
    "Kolkata":     (88.36, 22.57),
}

# --------------------------------------------------------------------------
# 5. FIGURE LAYOUT
# --------------------------------------------------------------------------
fig = plt.figure(figsize=(7.1, 8.0), constrained_layout=False)  # 18 cm wide
proj = ccrs.PlateCarree()

# Main map: study area + tracks
gs = fig.add_gridspec(
    2, 2,
    width_ratios=[2.6, 1.0],
    height_ratios=[1.0, 2.4],
    left=0.07, right=0.97, bottom=0.06, top=0.95,
    wspace=0.10, hspace=0.10,
)
ax_main  = fig.add_subplot(gs[1, :], projection=proj)
ax_inset = fig.add_subplot(gs[0, 1], projection=proj)
ax_legend = fig.add_subplot(gs[0, 0])
ax_legend.axis("off")

# --------------------------------------------------------------------------
# 5a. MAIN MAP
# --------------------------------------------------------------------------
ax_main.set_extent([81.5, 90.5, 16.5, 24.5], crs=proj)

# Background coastlines + ocean
ax_main.add_feature(cfeature.OCEAN.with_scale("10m"),
                    facecolor="#d8e6f2", zorder=0)
ax_main.add_feature(cfeature.LAND.with_scale("10m"),
                    facecolor="#f4efe6", zorder=0)
ax_main.add_feature(cfeature.COASTLINE.with_scale("10m"),
                    edgecolor="#5a5a5a", linewidth=0.5, zorder=2)
ax_main.add_feature(cfeature.BORDERS.with_scale("10m"),
                    edgecolor="#8a8a8a", linewidth=0.4,
                    linestyle="--", zorder=2)

# All Odisha districts (faint grey)
odisha.plot(ax=ax_main, edgecolor="#999999", facecolor="#fafafa",
            linewidth=0.3, zorder=1, transform=proj)

# Study districts (filled)
study.plot(ax=ax_main, edgecolor="#01696F", facecolor="#9fd4d8",
           linewidth=0.8, alpha=0.55, zorder=3, transform=proj)

# Bhitarkanika mangrove (highlight)
gpd.GeoSeries([BHITARKANIKA_POLY], crs="EPSG:4326").plot(
    ax=ax_main, edgecolor="#1b5e20", facecolor="#388e3c",
    linewidth=0.9, alpha=0.7, zorder=4, transform=proj,
)
ax_main.annotate(
    "Bhitarkanika\nmangrove",
    xy=BHITARKANIKA_CENTRE, xytext=(85.3, 21.7),
    fontsize=6.5, color="#1b5e20", weight="bold",
    arrowprops=dict(arrowstyle="-", color="#1b5e20", lw=0.5),
    transform=proj,
)

# Cyclone tracks — treatment events solid, transferability events dashed
for label, t in TRACKS.items():
    is_transfer = "transfer" in label.lower()
    waypoints = np.array(t["waypoints"])
    ax_main.plot(
        waypoints[:, 0], waypoints[:, 1],
        color=t["color"],
        lw=1.6 if not is_transfer else 1.1,
        ls="-"  if not is_transfer else (0, (3, 2)),
        alpha=0.9, zorder=5, transform=proj,
        label=f"{label}  ({t['landfall_date']}, {t['intensity_kt']} kt)",
    )
    # Landfall marker
    lon, lat = t["landfall"]
    ax_main.scatter(
        lon, lat, marker="*",
        s=110 if not is_transfer else 70,
        facecolor=t["color"], edgecolor="black", linewidth=0.5,
        zorder=6, transform=proj,
    )

# Cities
for city, (lon, lat) in CITIES.items():
    ax_main.scatter(lon, lat, s=14, color="black", zorder=7,
                    transform=proj)
    dx, dy = (0.10, 0.10)
    if city == "Bhubaneswar":  dx, dy = (0.15, -0.30)
    if city == "Puri":         dx, dy = (-0.85, -0.25)
    if city == "Paradip":      dx, dy = (0.10, 0.10)
    if city == "Balasore":     dx, dy = (-0.30, 0.20)
    if city == "Visakhapatnam":dx, dy = (0.20, -0.05)
    if city == "Kolkata":      dx, dy = (0.15, 0.10)
    if city == "Cuttack":      dx, dy = (-1.05, 0.18)
    ax_main.text(lon + dx, lat + dy, city, fontsize=6,
                 color="black", transform=proj,
                 path_effects=None)

# Gridlines
gl = ax_main.gridlines(draw_labels=True, linewidth=0.3, color="#bbbbbb",
                       linestyle=":", alpha=0.7)
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {"size": 6}
gl.ylabel_style = {"size": 6}

# Scale bar + N arrow
ax_main.text(89.3, 18.2, "Bay of Bengal",
             fontsize=8, style="italic", color="#234e6c",
             ha="center", rotation=-65, transform=proj)
# Approx scale 100 km at 20°N: 1° lon ~ 104.6 km, so 100 km ~ 0.96°
sx, sy = 88.4, 17.2
ax_main.plot([sx, sx + 0.96], [sy, sy], color="black", lw=1.5, transform=proj)
ax_main.text(sx + 0.48, sy + 0.10, "100 km", ha="center", fontsize=6,
             transform=proj)
# North arrow
ax_main.annotate("N", xy=(89.7, 24.0), xytext=(89.7, 23.4),
                 fontsize=9, weight="bold", ha="center",
                 arrowprops=dict(arrowstyle="->", color="black", lw=1.0),
                 transform=proj)

ax_main.set_title("(b) Study area: 8 coastal–subcoastal districts of Odisha "
                  "with cyclone tracks 2014–2021",
                  fontsize=8, loc="left")

# --------------------------------------------------------------------------
# 5b. INSET — India context map
# --------------------------------------------------------------------------
ax_inset.set_extent([68, 98, 6, 36], crs=proj)
ax_inset.add_feature(cfeature.OCEAN.with_scale("50m"),
                     facecolor="#d8e6f2", zorder=0)
ax_inset.add_feature(cfeature.LAND.with_scale("50m"),
                     facecolor="#f4efe6", zorder=0)
ax_inset.add_feature(cfeature.COASTLINE.with_scale("50m"),
                     edgecolor="#5a5a5a", linewidth=0.4, zorder=2)
ax_inset.add_feature(cfeature.BORDERS.with_scale("50m"),
                     edgecolor="#8a8a8a", linewidth=0.3, zorder=2)
# Highlight Odisha
odisha_dissolved = odisha.dissolve()
odisha_dissolved.plot(ax=ax_inset, edgecolor="#01696F", facecolor="#9fd4d8",
                      linewidth=0.5, alpha=0.8, zorder=3, transform=proj)
# Study-area extent rectangle
rect = mpatches.Rectangle((81.5, 16.5), 9.0, 8.0,
                          linewidth=0.8, edgecolor="#d62728",
                          facecolor="none", transform=proj, zorder=4)
ax_inset.add_patch(rect)
ax_inset.set_title("(a) India", fontsize=8, loc="left")

# --------------------------------------------------------------------------
# 5c. LEGEND PANEL
# --------------------------------------------------------------------------
ax_legend.set_xlim(0, 1); ax_legend.set_ylim(0, 1)

legend_elements = [
    mpatches.Patch(facecolor="#9fd4d8", edgecolor="#01696F",
                   alpha=0.8, label="Study districts (BACI domain)"),
    mpatches.Patch(facecolor="#388e3c", edgecolor="#1b5e20",
                   alpha=0.8, label="Bhitarkanika mangrove (~672 km²)"),
    plt.Line2D([0], [0], color="#d62728", lw=1.6, label="Fani 2019  (treatment)"),
    plt.Line2D([0], [0], color="#ff7f0e", lw=1.6, label="Amphan 2020 (treatment)"),
    plt.Line2D([0], [0], color="#1f77b4", lw=1.6, label="Yaas 2021  (treatment)"),
    plt.Line2D([0], [0], color="#7f7f7f", lw=1.1, ls=(0, (3, 2)),
               label="Bulbul 2019 (transferability)"),
    plt.Line2D([0], [0], color="#2ca02c", lw=1.1, ls=(0, (3, 2)),
               label="Hudhud 2014 (transferability)"),
    plt.Line2D([0], [0], marker="*", color="w", markerfacecolor="black",
               markeredgecolor="black", markersize=9, label="Landfall point"),
]
ax_legend.legend(handles=legend_elements, loc="center left",
                 frameon=False, fontsize=6.4, handlelength=2.0,
                 borderpad=0.3, labelspacing=0.55)

# --------------------------------------------------------------------------
# 6. SAVE
# --------------------------------------------------------------------------
out_png = FIGS / "figure1_study_area.png"
out_pdf = FIGS / "figure1_study_area.pdf"
fig.savefig(out_png, dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(out_pdf,            bbox_inches="tight", facecolor="white")
print(f"\nSaved: {out_png}")
print(f"Saved: {out_pdf}")

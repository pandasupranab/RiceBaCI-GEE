import os
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader

# ---------- 1. Setup & Output Directory ----------
OUT = Path("/home/user/workspace/rse_final/figures")
OUT.mkdir(parents=True, exist_ok=True)

# ---------- 2. Style Palette ----------
C_TREAT  = "#E27D24"
C_CTRL   = "#1F77B4"
C_FANI   = "#D62728"
C_AMPHAN = "#9467BD"
C_YAAS   = "#2CA02C"
C_LAND   = "#F5EFD9"
C_OCEAN  = "#D7E8F2"
C_BORDER = "#8A8A8A"

# ---------- 3. Fetch Real District Borders ----------
print("Downloading official India district borders...")
GEO_URL = "https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/IND/ADM2/geoBoundaries-IND-ADM2.geojson"
all_districts = gpd.read_file(GEO_URL)

TREATMENT_DB = ["Baleshwar", "Bhadrak", "Kendrapara", "Jagatsinghapur", "Puri"]
CONTROL_DB = ["Anugul", "Dhenkanal", "Cuttack"]
STUDY_DISTRICTS = TREATMENT_DB + CONTROL_DB

districts = all_districts[all_districts["shapeName"].isin(STUDY_DISTRICTS)].copy()
name_mapping = {"Jagatsinghapur": "Jagatsinghpur", "Anugul": "Angul"}
districts["display_name"] = districts["shapeName"].replace(name_mapping)
districts["group"] = districts["display_name"].apply(
    lambda n: "treatment" if n in ["Baleshwar", "Bhadrak", "Kendrapara", "Jagatsinghpur", "Puri"] else "control"
)
print(f"Successfully loaded {len(districts)} study districts!")

# ---------- 4. Fetch Live Cyclone Data ----------
print("Downloading North Indian basin data from NOAA...")
NOAA_URL = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.NI.list.v04r01.csv"
ibtracs = pd.read_csv(NOAA_URL, skiprows=[1], low_memory=False)

def get_cyclone(name, year):
    df = ibtracs[(ibtracs["NAME"] == name.upper()) & (ibtracs["SEASON"] == year)].copy()
    df["LAT"] = pd.to_numeric(df["LAT"], errors="coerce")
    df["LON"] = pd.to_numeric(df["LON"], errors="coerce")
    df["ISO_TIME"] = pd.to_datetime(df["ISO_TIME"])
    df = df.dropna(subset=["LAT", "LON"]).sort_values("ISO_TIME")
    return df

TRACKS = {
    "Fani 2019":   {"df": get_cyclone("FANI", 2019),   "color": C_FANI,   "label": "Cyclone Fani (3 May 2019, ESCS)"},
    "Amphan 2020": {"df": get_cyclone("AMPHAN", 2020), "color": C_AMPHAN, "label": "Cyclone Amphan (20 May 2020, SuCS)"},
    "Yaas 2021":   {"df": get_cyclone("YAAS", 2021),   "color": C_YAAS,   "label": "Cyclone Yaas (26 May 2021, VSCS)"},
}

IMD_LANDFALLS = {
    "Fani 2019":   (85.83, 19.80),
    "Amphan 2020": (88.25, 21.60),
    "Yaas 2021":   (86.94, 21.42),
}

# ---------- 5. Building the Canvas ----------
print("Drawing the map...")
proj = ccrs.PlateCarree()
fig = plt.figure(figsize=(20, 14), facecolor="white")
ax_inset = fig.add_axes([0.01, 0.33, 0.20, 0.65], projection=proj)
ax_main = fig.add_axes([0.29, 0.33, 0.70, 0.65], projection=proj)
ax_legend = fig.add_axes([0.015, 0.04, 0.97, 0.26])

# --- Main Map ---
ax_main.set_extent([81.5, 90.5, 18.3, 23.3], crs=proj)
ax_main.add_feature(cfeature.OCEAN.with_scale("10m"), facecolor=C_OCEAN, zorder=0)
ax_main.add_feature(cfeature.LAND.with_scale("10m"),  facecolor=C_LAND,  zorder=1)
ax_main.add_feature(cfeature.COASTLINE.with_scale("10m"), edgecolor="#5A6E7A", lw=0.7, zorder=2)
ax_main.add_feature(cfeature.BORDERS.with_scale("10m"), edgecolor=C_BORDER, lw=0.5, linestyle="--", zorder=2)

states_reader = shpreader.Reader(shpreader.natural_earth(resolution="10m", category="cultural", name="admin_1_states_provinces"))
for s in states_reader.records():
    if s.attributes.get("name", "") == "Odisha":
        ax_main.add_geometries([s.geometry], crs=proj, facecolor="none", edgecolor="#B07535", lw=1.1, zorder=2.5)

for _, row in districts.iterrows():
    color = C_TREAT if row["group"] == "treatment" else C_CTRL
    ax_main.add_geometries([row.geometry], crs=proj, facecolor=color, edgecolor="black", lw=0.7, alpha=0.62, zorder=3)

for name, cyc in TRACKS.items():
    track = cyc["df"]
    imd_lon, imd_lat = IMD_LANDFALLS[name]
    track = track[track["LAT"] >= 8].copy()
    d2 = (track["LON"] - imd_lon)**2 + (track["LAT"] - imd_lat)**2
    if not track.empty:
        nearest_idx = d2.idxmin()
        track.loc[nearest_idx, "LON"] = imd_lon
        track.loc[nearest_idx, "LAT"] = imd_lat
        lf_time = track.loc[nearest_idx, "ISO_TIME"]
        track = track[track["ISO_TIME"] <= lf_time + pd.Timedelta(hours=12)]
    ax_main.plot(track["LON"], track["LAT"], color=cyc["color"], lw=2.3, alpha=0.92, zorder=5, transform=proj)
    ax_main.plot(imd_lon, imd_lat, marker="*", color=cyc["color"], markersize=22, markeredgecolor="black", markeredgewidth=0.9, zorder=8, transform=proj)
    pt = gpd.GeoSeries.from_xy([imd_lon], [imd_lat], crs="EPSG:4326").to_crs("EPSG:7755")
    buf = pt.buffer(50_000).to_crs("EPSG:4326").iloc[0]
    ax_main.add_geometries([buf], crs=proj, facecolor="none", edgecolor=cyc["color"], linestyle=":", lw=1.3, zorder=6)

LABEL_POSITIONS = {
    "Baleshwar": (86.95, 21.60), "Bhadrak": (86.75, 21.05), "Kendrapara": (86.75, 20.55),
    "Jagatsinghpur": (86.40, 20.15), "Puri": (84.80, 19.30), "Angul": (85.05, 20.95),
    "Dhenkanal": (85.55, 20.70), "Cuttack": (85.90, 20.40)
}

for _, row in districts.iterrows():
    name = row["display_name"]
    cent = row.geometry.centroid
    label_lon, label_lat = LABEL_POSITIONS.get(name, (cent.x, cent.y))
    needs_arrow = name == "Puri"
    ax_main.annotate(name, xy=(cent.x, cent.y), xytext=(label_lon, label_lat),
                     fontsize=14, ha="center", va="center", zorder=10, fontweight="bold",
                     bbox=dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor="#888888", lw=0.5, alpha=0.92),
                     arrowprops=dict(arrowstyle="-", color="#555555", lw=0.7) if needs_arrow else None,
                     transform=proj)

ax_main.text(84.0, 22.6, "Odisha", fontsize=36, style="italic", color="#B07535", ha="center", weight="bold", zorder=4, transform=proj)
ax_main.text(88.55, 22.40, "West Bengal", fontsize=22, style="italic", color="#4D4D4D", ha="center", weight="bold", zorder=4, transform=proj)
ax_main.text(87.5, 19.5, "Bay of Bengal", fontsize=30, style="italic", color="#3A6480", ha="center", zorder=4, transform=proj)

gl = ax_main.gridlines(draw_labels=True, linewidth=0.4, color="#888888", alpha=0.5, linestyle=":")
gl.top_labels = False; gl.right_labels = False
gl.xlabel_style = {"size": 20}; gl.ylabel_style = {"size": 20}

ax_main.annotate("", xy=(89.15, 19.30), xytext=(89.15, 18.75), arrowprops=dict(arrowstyle="-|>", color="black", lw=1.8), zorder=11)
ax_main.text(89.15, 19.45, "N", fontsize=30, fontweight="bold", ha="center", zorder=11, transform=proj)

sb_lon0, sb_lat = 87.7, 18.75
sb_dlon = 100.0 / (111.0 * np.cos(np.radians(sb_lat)))
ax_main.plot([sb_lon0, sb_lon0 + sb_dlon], [sb_lat, sb_lat], color="black", lw=3, zorder=11, transform=proj)
ax_main.text(sb_lon0 + sb_dlon/2, sb_lat + 0.10, "100 km", fontsize=20, ha="center", fontweight="bold", zorder=11, transform=proj)

# --- India Inset ---
ax_inset.set_extent([68, 97, -8, 45], crs=proj)
ax_inset.add_feature(cfeature.OCEAN.with_scale("50m"), facecolor=C_OCEAN, zorder=0)
ax_inset.add_feature(cfeature.LAND.with_scale("50m"), facecolor=C_LAND, zorder=1)
ax_inset.add_feature(cfeature.COASTLINE.with_scale("50m"), edgecolor="#5A6E7A", lw=0.4, zorder=2)
ax_inset.add_feature(cfeature.BORDERS.with_scale("50m"), edgecolor=C_BORDER, lw=0.4, linestyle="--", zorder=2)

print("Applying Survey of India official J&K/Ladakh boundaries...")
INDIA_GEO_URL = "https://raw.githubusercontent.com/datameet/maps/master/Country/india-composite.geojson"
india_official = gpd.read_file(INDIA_GEO_URL)
ax_inset.add_geometries(india_official.geometry, crs=proj,
                        facecolor=C_LAND, edgecolor=C_BORDER,
                        lw=0.8, zorder=3)

for s in shpreader.Reader(shpreader.natural_earth(resolution="50m", category="cultural", name="admin_1_states_provinces")).records():
    if s.attributes.get("name", "") == "Odisha":
        ax_inset.add_geometries([s.geometry], crs=proj, facecolor="#E27D24", edgecolor="#8C4A14", lw=0.8, alpha=0.85, zorder=4)

study_bbox = districts.unary_union.bounds
ax_inset.add_patch(Rectangle((study_bbox[0]-0.2, study_bbox[1]-0.2), study_bbox[2]-study_bbox[0]+0.4, study_bbox[3]-study_bbox[1]+0.4,
                             fill=False, edgecolor="red", lw=1.5, transform=proj, zorder=5))

ax_inset.set_title("(a)", loc="left", fontsize=28, fontweight="bold", pad=12)
ax_main.set_title("(b)", loc="left", fontsize=28, fontweight="bold", pad=12)
for spine in ax_inset.spines.values():
    spine.set_visible(True); spine.set_edgecolor("#999999"); spine.set_linewidth(0.6)

# --- Legend ---
ax_legend.axis("off")
legend_elems = [
    Line2D([0],[0], marker="s", color="w", markerfacecolor=C_TREAT, markeredgecolor="black", markersize=24, label="Coastal treatment district (n=5)"),
    Line2D([0],[0], marker="s", color="w", markerfacecolor=C_CTRL, markeredgecolor="black", markersize=24, label="Inland control district (n=3)"),
    Line2D([0],[0], color=C_FANI, lw=4.0, label=TRACKS["Fani 2019"]["label"]),
    Line2D([0],[0], color=C_AMPHAN, lw=4.0, label=TRACKS["Amphan 2020"]["label"]),
    Line2D([0],[0], color=C_YAAS, lw=4.0, label=TRACKS["Yaas 2021"]["label"]),
    Line2D([0],[0], marker="*", color="w", markerfacecolor="black", markeredgecolor="black", markersize=28, label="IMD-documented landfall site"),
    Line2D([0],[0], color="black", lw=2.5, linestyle=":", label="50-km landfall buffer"),
]
ax_legend.legend(handles=legend_elems, loc="center", fontsize=26, frameon=True, framealpha=0.97, edgecolor="#BBBBBB",
                 borderpad=1.2, labelspacing=1.0, columnspacing=2.5, handlelength=2.5, handletextpad=0.9, ncol=2, title="Legend", title_fontsize=32)

# ---------- 6. Export ----------
print("Saving Figure 1 at 1000 dpi...")
fig.savefig(OUT / "fig1_study_area.jpg", dpi=1000, facecolor="white", format="jpg", pil_kwargs={"quality": 95})
plt.close(fig)
print(f"Success! Saved to: {OUT / 'fig1_study_area.jpg'}")

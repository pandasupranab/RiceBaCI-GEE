"""Convert IBTrACS GeoJSON to a zipped Shapefile for GEE upload.

GEE's Code Editor 'Table upload' UI accepts Shapefile (zip) and CSV but not
GeoJSON, so we convert. Field names are truncated to 10 chars to satisfy
the Shapefile DBF spec.
"""
from pathlib import Path
import zipfile
import geopandas as gpd

ROOT   = Path(__file__).resolve().parents[1]
SRC    = ROOT / "data" / "processed" / "ibtracs_NI_2014_2024.geojson"
OUTDIR = ROOT / "data" / "processed" / "ibtracs_shp"
ZIPOUT = ROOT / "data" / "processed" / "ibtracs_NI_2014_2024.zip"

OUTDIR.mkdir(parents=True, exist_ok=True)

gdf = gpd.read_file(SRC)
print(f"Loaded {len(gdf)} features. Columns: {list(gdf.columns)}")

# Shapefile field names are limited to 10 chars - rename safely
gdf = gdf.rename(columns={
    "min_dist_km": "min_dist",
    "max_wind_kt": "max_wind",
    "start_time":  "start_t",
    "end_time":    "end_t",
})

shp_path = OUTDIR / "ibtracs_NI_2014_2024.shp"
gdf.to_file(shp_path, driver="ESRI Shapefile", encoding="utf-8")

# Zip the four sidecar files (.shp .shx .dbf .prj) for GEE upload
with zipfile.ZipFile(ZIPOUT, "w", zipfile.ZIP_DEFLATED) as zf:
    for ext in (".shp", ".shx", ".dbf", ".prj"):
        f = OUTDIR / f"ibtracs_NI_2014_2024{ext}"
        if f.exists():
            zf.write(f, arcname=f.name)
            print(f"  added {f.name}")

print(f"\nDone: {ZIPOUT}")

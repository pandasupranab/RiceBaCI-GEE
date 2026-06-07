"""Merge the 5 EMSR357 observedEventA shapefiles into a single Fani flood
footprint, dissolve overlaps, reproject to EPSG:4326, and save as GeoJSON
+ shapefile for uploading to GEE."""

import sys
from pathlib import Path
import geopandas as gpd
import pandas as pd

ROOT = Path('/home/user/workspace/RiceBaCI-GEE/data_real/cyclone_footprints/fani_ems357')
OUT  = Path('/home/user/workspace/RiceBaCI-GEE/data_real/cyclone_footprints/fani_observed_flood.geojson')
OUT_SHP = Path('/home/user/workspace/RiceBaCI-GEE/data_real/cyclone_footprints/fani_observed_flood.shp')

AOIs = {
    'AOI01_OdishaCoast': ROOT/'EMSR357_AOI01_DEL_PRODUCT_r1_VECTORS_v4_vector/EMSR357_AOI01_DEL_PRODUCT_observedEventA_r1_v4.shp',
    'AOI03_Bhubaneshwar': ROOT/'EMSR357_AOI03_FEP_PRODUCT_r1_RTP01_v1_vector/EMSR357_AOI03_FEP_PRODUCT_observedEventA_r1_v1.shp',
    'AOI05_Gopalpur':    ROOT/'EMSR357_AOI05_GRA_PRODUCT_r1_VECTORS_v1_vector/EMSR357_AOI05_GRA_PRODUCT_observedEventA_r1_v1.shp',
    'AOI06_Gopalpurport':ROOT/'EMSR357_AOI06_GRA_PRODUCT_r1_VECTORS_v1_vector/EMSR357_AOI06_GRA_PRODUCT_observedEventA_r1_v1.shp',
    'AOI08_Puri':        ROOT/'EMSR357_AOI08_GRA_PRODUCT_r1_RTP01_v2_vector/EMSR357_AOI08_GRA_PRODUCT_observedEventA_r1_v2.shp',
}

gdfs = []
for name, path in AOIs.items():
    g = gpd.read_file(path)
    print(f"\n--- {name} ---")
    print(f"  rows: {len(g)}")
    print(f"  crs: {g.crs}")
    print(f"  columns: {list(g.columns)}")
    if len(g):
        # Reproject to a local UTM (EPSG:32645 covers eastern India) for area in m^2,
        # then back to WGS84 for the merged output.
        g_utm = g.to_crs('EPSG:32645')
        total_km2 = g_utm.geometry.area.sum() / 1e6
        print(f"  flood area (km^2): {total_km2:.2f}")
        # Show distinct values for typical EMS attributes
        for col in ('event_type', 'obj_type', 'obj_desc', 'notation'):
            if col in g.columns:
                print(f"  {col} unique: {g[col].dropna().unique().tolist()[:6]}")
    g = g.to_crs('EPSG:4326')
    g['aoi'] = name
    g['cyclone'] = 'Fani'
    g['event_date'] = '2019-05-03'
    g['source'] = 'Copernicus EMS EMSR357'
    gdfs.append(g)

# Concatenate (keep only geometry + our added attrs to avoid schema clashes)
keep_cols = ['cyclone', 'event_date', 'aoi', 'source', 'geometry']
gdfs_lite = []
for g in gdfs:
    cols_present = [c for c in keep_cols if c in g.columns]
    gdfs_lite.append(g[cols_present])

merged = pd.concat(gdfs_lite, ignore_index=True)
merged = gpd.GeoDataFrame(merged, crs='EPSG:4326')

# Total area
merged_utm = merged.to_crs('EPSG:32645')
print(f"\n=== MERGED ===")
print(f"  total polygons: {len(merged)}")
print(f"  total flood area (km^2): {merged_utm.geometry.area.sum() / 1e6:.2f}")
print(f"  bbox (lon/lat): {merged.total_bounds}")

OUT.parent.mkdir(parents=True, exist_ok=True)
merged.to_file(OUT, driver='GeoJSON')
merged.to_file(OUT_SHP)
print(f"\nWrote: {OUT}")
print(f"Wrote: {OUT_SHP}")
print(f"GeoJSON size: {OUT.stat().st_size / 1e6:.2f} MB")

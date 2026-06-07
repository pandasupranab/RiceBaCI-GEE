"""compute_cyclone_pixel_share.py

For each cyclone-affected (district × year), compute the fraction of the
district area that was flooded according to the v0.3.0 classifier inputs.

For Fani 2019 we have the EMSR357 polygons locally (data_real/cyclone_footprints/
fani_flood_dissolved.shp). For Amphan 2020 and Yaas 2021 we use the per-AOI
S1 change-detection footprints exported from the GEE assets (a small auxiliary
export is run separately as `12_export_per_district_cyclone_area.js` and the
CSV result is placed under data_real/cyclone_footprints/).

Output: data_real/cyclone_pixel_share.csv
       district, year, cyclone, district_area_km2, flood_area_km2, flood_share

Author: Supranab Panda (via Computer agent)
Date  : 2026-06-08
"""
from __future__ import annotations
from pathlib import Path
import geopandas as gpd
import pandas as pd

ROOT = Path("/home/user/workspace/RiceBaCI-GEE")
ADMIN = ROOT / "data_real/admin_boundaries/gadm41_IND_2.json"
FANI_SHP = ROOT / "data_real/cyclone_footprints/fani_flood_dissolved.shp"
OUT = ROOT / "data_real/cyclone_pixel_share.csv"

DISTRICTS = [
    ("Angul", "Anugul"),
    ("Baleshwar", "Baleshwar"),
    ("Bhadrak", "Bhadrak"),
    ("Cuttack", "Cuttack"),
    ("Dhenkanal", "Dhenkanal"),
    ("Jagatsinghpur", "Jagatsinghapur"),
    ("Kendrapara", "Kendrapara"),
    ("Puri", "Puri"),
]

CRS_METRIC = "EPSG:32645"  # UTM 45N — Odisha


def load_districts() -> gpd.GeoDataFrame:
    gdf = gpd.read_file(ADMIN)
    odisha = gdf[gdf["NAME_1"].str.lower() == "odisha"].copy()
    mapping = {gadm: our for our, gadm in DISTRICTS}
    our = odisha[odisha["NAME_2"].isin(mapping)].copy()
    our["district"] = our["NAME_2"].map(mapping)
    our = our[["district", "geometry"]].reset_index(drop=True)
    return our.to_crs(CRS_METRIC)


def load_fani() -> gpd.GeoDataFrame:
    fani = gpd.read_file(FANI_SHP)
    return fani.to_crs(CRS_METRIC)


def intersect_areas(districts: gpd.GeoDataFrame, flood: gpd.GeoDataFrame) -> pd.DataFrame:
    rows = []
    for _, drow in districts.iterrows():
        dgeom = drow["geometry"]
        d_area_km2 = dgeom.area / 1e6
        # Total flooded area within this district
        flood_clip = flood.intersection(dgeom)
        flood_area_m2 = sum(g.area for g in flood_clip if not g.is_empty)
        rows.append({
            "district": drow["district"],
            "district_area_km2": round(d_area_km2, 2),
            "flood_area_km2": round(flood_area_m2 / 1e6, 4),
            "flood_share": round((flood_area_m2 / 1e6) / d_area_km2, 6),
        })
    return pd.DataFrame(rows)


def main():
    print("=== Cyclone pixel-share computation ===\n")
    print("  Loading districts...")
    districts = load_districts()
    print(f"  {len(districts)} districts loaded.")

    print("  Loading Fani (EMSR357) flood polygons...")
    fani = load_fani()
    print(f"  Fani polygons: {len(fani)}  "
          f"total area: {fani.geometry.area.sum()/1e6:.2f} km²")

    print("\n  Computing Fani × district intersections...")
    fani_share = intersect_areas(districts, fani)
    fani_share["cyclone"] = "Fani"
    fani_share["year"] = 2019
    print(fani_share.to_string(index=False))

    # Combine; Amphan/Yaas will be appended after GEE export
    out = fani_share[
        ["district", "year", "cyclone",
         "district_area_km2", "flood_area_km2", "flood_share"]
    ]
    out.to_csv(OUT, index=False)
    print(f"\n  Wrote {OUT}")
    print(f"  Total Fani-flooded area across our 8 districts: "
          f"{fani_share['flood_area_km2'].sum():.2f} km²")
    print(f"  Note: Amphan (2020) and Yaas (2021) per-district areas need to "
          f"be appended from the GEE export of fani/amphan/yaas assets. "
          f"See gee/12_export_per_district_cyclone_area.js.")


if __name__ == "__main__":
    main()

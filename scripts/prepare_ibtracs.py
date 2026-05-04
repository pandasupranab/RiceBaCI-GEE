"""
prepare_ibtracs.py - Filter IBTrACS NI basin to 2014-2024 and to tracks
within 500 km of the RiceBaCI study area, then export as GeoJSON.

Workflow:
  1. Download CSV from
     https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.NI.list.v04r01.csv
     and save to data/raw/
  2. python scripts/prepare_ibtracs.py
  3. python scripts/geojson_to_shapefile.py
  4. Upload data/processed/ibtracs_NI_2014_2024.zip to GEE as Shapefile
     at asset ID: projects/durable-pulsar-486209-b5/assets/ibtracs_NI_2014_2024
"""

import json
import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC  = ROOT / "data" / "raw" / "ibtracs.NI.list.v04r01.csv"
OUT  = ROOT / "data" / "processed" / "ibtracs_NI_2014_2024.geojson"

# Study-area centroid (approx centre of 8 districts, Odisha coast)
STUDY_LAT, STUDY_LON = 20.6, 86.0
BUFFER_KM = 500.0
YEAR_MIN, YEAR_MAX = 2014, 2024


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def main():
    print(f"Reading {SRC.name} ...")
    df = pd.read_csv(SRC, low_memory=False, skiprows=[1], na_values=[" ", ""])

    cols = ["SID", "SEASON", "NAME", "ISO_TIME", "LAT", "LON",
            "WMO_WIND", "USA_WIND", "NATURE"]
    df = df[[c for c in cols if c in df.columns]].copy()

    df["SEASON"] = pd.to_numeric(df["SEASON"], errors="coerce")
    df["LAT"]    = pd.to_numeric(df["LAT"],    errors="coerce")
    df["LON"]    = pd.to_numeric(df["LON"],    errors="coerce")
    df = df.dropna(subset=["SEASON", "LAT", "LON", "ISO_TIME"])
    df = df[(df["SEASON"] >= YEAR_MIN) & (df["SEASON"] <= YEAR_MAX)]

    print(f"Storms in {YEAR_MIN}-{YEAR_MAX} (raw fixes): {len(df)}")

    features = []
    kept_storms = []

    for sid, g in df.groupby("SID", sort=False):
        g = g.sort_values("ISO_TIME")
        dists = g.apply(
            lambda r: haversine_km(r["LAT"], r["LON"], STUDY_LAT, STUDY_LON),
            axis=1,
        )
        min_d = float(dists.min())
        if min_d > BUFFER_KM:
            continue

        coords = [[float(r["LON"]), float(r["LAT"])] for _, r in g.iterrows()]
        if len(coords) < 2:
            continue

        name = str(g["NAME"].iloc[0]).strip().title()
        if name in ("", "Nan", "Not_Named"):
            name = f"Unnamed_{int(g['SEASON'].iloc[0])}"

        wind_col = "USA_WIND" if "USA_WIND" in g.columns else "WMO_WIND"
        max_wind = pd.to_numeric(g[wind_col], errors="coerce").max()

        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "sid":         sid,
                "name":        name,
                "season":      int(g["SEASON"].iloc[0]),
                "start_time":  str(g["ISO_TIME"].iloc[0]),
                "end_time":    str(g["ISO_TIME"].iloc[-1]),
                "min_dist_km": round(min_d, 1),
                "max_wind_kt": (None if pd.isna(max_wind) else float(max_wind)),
                "n_fixes":     len(coords),
            },
        })
        kept_storms.append(
            (int(g["SEASON"].iloc[0]), name, round(min_d, 1),
             None if pd.isna(max_wind) else float(max_wind))
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": features}, f)

    print(f"\nKept {len(features)} storms within {BUFFER_KM:.0f} km of "
          f"({STUDY_LAT}, {STUDY_LON}):")
    print(f"{'Year':<6}{'Name':<22}{'min_dist_km':>12}{'max_wind_kt':>14}")
    for season, name, d, w in sorted(kept_storms):
        wstr = "-" if w is None else f"{w:.0f}"
        print(f"{season:<6}{name:<22}{d:>12.1f}{wstr:>14}")

    print(f"\nWritten: {OUT}")


if __name__ == "__main__":
    main()

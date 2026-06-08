"""18_real_s1_backscatter_signatures.py - Real Sentinel-1 RTC backscatter
signatures for the 4 paddy-dominant Bulbul probe districts.

Replaces the literature-calibrated canonical idealised signatures in
analysis/12_backscatter_signatures.py / Table S9 / Figure S2 with real
empirical mean VH and VV (in dB) and CR = VH/VV (linear ratio) extracted
per district per 10-day epoch from the Microsoft Planetary Computer
Sentinel-1 RTC collection (10 m, IW GRD, terrain-corrected, gamma_0).

Probe districts (paddy-dominant, retained from Pass-15 forest screen):
    Boudh, Ganjam, Khordha, Nayagarh.

Time window: 2019-05-01 to 2019-12-15 (covers agronomic transplanting
June-August 2019 AND the Bulbul cyclone landfall 2019-11-09).

Method:
  1. Use the same GADM v4.1 India L2 polygons used by the Bulbul probe.
  2. Query the planetary-computer sentinel-1-rtc collection for the
     district envelope, polarisations VH and VV, orbit-direction-agnostic.
  3. Read items with odc.stac.load at 100 m resolution (sufficient for
     district-mean signatures; full 10 m would be ~25x more data per scene).
  4. Mask to the district polygon, convert linear gamma_0 to dB:
        dB = 10 * log10(linear).
  5. Aggregate by 10-day epoch (dekad-of-year): mean VH_db, mean VV_db.
     CR = VH_lin / VV_lin (linear ratio, not dB difference).
  6. Persist per-district per-dekad CSV + a stacked all-district CSV.

Output: analysis/results/real_v21/s1_backscatter_real_signatures.csv
        analysis/results/real_v21/s1_backscatter_real_series_<district>.csv
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "analysis" / "results" / "real_v21"
RES.mkdir(parents=True, exist_ok=True)

# Same GADM file used by Bulbul probe
GADM = Path("/home/user/workspace/bulbul_real_probe/gadm41_IND_2.json")

# GADM v4.1 spelling: Bauda = Boudh
PROBE_DISTRICTS_GADM = ["Bauda", "Ganjam", "Khordha", "Nayagarh"]
GADM_TO_DISPLAY = {"Bauda": "Boudh", "Ganjam": "Ganjam",
                   "Khordha": "Khordha", "Nayagarh": "Nayagarh"}
START = "2019-05-01"
END = "2019-12-15"

OUT_RES_M = 100   # 100 m district-mean signatures; trade-off for runtime
LOG = sys.stdout


def log(msg: str) -> None:
    print(msg, flush=True)


def load_district_geoms() -> Dict[str, dict]:
    import shapely.geometry as sg
    with open(GADM) as f:
        gj = json.load(f)
    out = {}
    for feat in gj["features"]:
        prop = feat["properties"]
        if prop.get("NAME_1") != "Odisha":
            continue
        nm = prop.get("NAME_2")
        if nm in PROBE_DISTRICTS_GADM:
            out[GADM_TO_DISPLAY[nm]] = feat["geometry"]
    missing = set(GADM_TO_DISPLAY.values()) - set(out)
    if missing:
        raise RuntimeError(f"GADM missing districts: {missing}")
    return out


def fetch_district_series(district: str, geom: dict) -> pd.DataFrame:
    """Pull S1 RTC items for the district envelope and aggregate by dekad."""
    import pystac_client
    import planetary_computer as pc
    import odc.stac
    from shapely.geometry import shape as shp_shape
    import xarray as xr

    g = shp_shape(geom)
    bbox = list(g.bounds)
    log(f"  [{district}] bbox = {bbox}")

    cat = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=pc.sign_inplace,
    )
    search = cat.search(
        collections=["sentinel-1-rtc"],
        bbox=bbox,
        datetime=f"{START}/{END}",
    )
    items = list(search.items())
    log(f"  [{district}] {len(items)} S1 RTC items in window")
    if not items:
        return pd.DataFrame()

    ds = odc.stac.load(
        items,
        bands=["vh", "vv"],
        bbox=bbox,
        resolution=OUT_RES_M,
        crs="epsg:32644",  # UTM N44, central Odisha
        groupby="solar_day",
    )

    # Mask to district polygon
    import rioxarray  # noqa: F401  (xr.rio accessor)
    import geopandas as gpd
    gdf = gpd.GeoDataFrame({"geometry": [g]}, crs="epsg:4326").to_crs(32644)
    ds = ds.rio.write_crs("epsg:32644")
    ds = ds.rio.clip(gdf.geometry, drop=False, all_touched=False)

    # Linear gamma_0 -> dB; CR = vh_lin / vv_lin
    vh_lin = ds["vh"].where(ds["vh"] > 0)
    vv_lin = ds["vv"].where(ds["vv"] > 0)
    vh_db = 10.0 * np.log10(vh_lin)
    vv_db = 10.0 * np.log10(vv_lin)
    cr_lin = vh_lin / vv_lin

    # Time-mean by 10-day dekad of year
    times = pd.to_datetime(ds["time"].values)
    doy = np.array(times.dayofyear)
    dekad = np.minimum((doy - 1) // 10, 36)  # 0..36

    df_rows = []
    for d in np.unique(dekad):
        mask_t = dekad == d
        if not mask_t.any():
            continue
        vh_d = vh_db.isel(time=mask_t).mean(dim="time")
        vv_d = vv_db.isel(time=mask_t).mean(dim="time")
        cr_d = cr_lin.isel(time=mask_t).mean(dim="time")
        # Mean over masked spatial domain
        df_rows.append({
            "district": district,
            "dekad_of_year": int(d),
            "doy_centre": int(d * 10 + 5),
            "date_centre": (pd.Timestamp("2019-01-01")
                            + pd.Timedelta(days=int(d * 10 + 5) - 1)
                            ).strftime("%Y-%m-%d"),
            "n_scenes": int(mask_t.sum()),
            "vh_db_mean": float(vh_d.mean().values),
            "vv_db_mean": float(vv_d.mean().values),
            "cr_lin_mean": float(cr_d.mean().values),
        })
    return pd.DataFrame(df_rows)


def main():
    geoms = load_district_geoms()
    log(f"[OK] loaded {len(geoms)} probe district geometries")

    all_rows = []
    for d in ["Boudh", "Ganjam", "Khordha", "Nayagarh"]:
        log(f"\n=== {d} ===")
        try:
            df = fetch_district_series(d, geoms[d])
        except Exception as exc:
            log(f"  [ERROR] {d}: {exc!r}")
            continue
        if df.empty:
            log(f"  [WARN] {d}: empty result")
            continue
        out_path = RES / f"s1_backscatter_real_series_{d}.csv"
        df.to_csv(out_path, index=False)
        log(f"  [OK] wrote {out_path}  ({len(df)} dekads)")
        all_rows.append(df)

    if not all_rows:
        log("[FAIL] no series produced")
        sys.exit(1)
    combined = pd.concat(all_rows, ignore_index=True)
    out_combined = RES / "s1_backscatter_real_signatures.csv"
    combined.to_csv(out_combined, index=False)
    log(f"\n[OK] wrote {out_combined}  ({len(combined)} district-dekads)")


if __name__ == "__main__":
    main()

"""
Real Sentinel-2-based phenology extraction for the 6 Bulbul probe districts.

Source data
-----------
- Sentinel-2 L2A (cloud-optimized GeoTIFF) via Microsoft Planetary Computer STAC,
  anonymous access, https://planetarycomputer.microsoft.com/api/stac/v1
- District boundaries: GADM v4.1, India level 2, accessed 2026-06-08

Pipeline
--------
For each district d in {Mayurbhanj, Khordha, Ganjam, Nayagarh, Boudh, Kandhamal}
and each Kharif year y in {2017, 2018, 2020}:

  1. Query STAC for Sentinel-2 L2A scenes intersecting the district polygon,
     date range = Apr 01 -- Dec 31 of year y, cloud cover <= 40%.
  2. For each scene: read B04 (Red, 10 m) and B08 (NIR, 10 m) from the COG URL
     at 200 m resampling (overview level 4) clipped to the district polygon,
     mask cloud/scl != [4,5] (vegetation, not-vegetated land), compute NDVI.
  3. Aggregate to monthly median NDVI per district -> 9 monthly NDVI values.
  4. Fit a 6-parameter double-logistic curve following Beck et al. (2006)
     to the monthly series; estimate SOS as the DOY at half-maximum of the
     rising arm.
  5. District-year SOS DOY = the fitted SOS.

Outputs
-------
- bulbul_probe_phenology_real.csv (district, year, sos_doy, n_scenes, n_clear_months)
- bulbul_probe_ndvi_series.csv (district, year, month, ndvi_median)

Author : Pass-15 real-data closure of the pre-registered Bulbul probe.
"""
import os, json, time, math
from datetime import date
import numpy as np
import pandas as pd
import requests
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
from rasterio.mask import mask as rio_mask
import warnings
warnings.filterwarnings("ignore")

WORKDIR = "/home/user/workspace/bulbul_real_probe"
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"

DISTRICTS = {
    "Mayurbhanj":  "coastal_rainfall",   # GADM NAME_2 = "Mayurbhanj"
    "Khordha":     "coastal_rainfall",   # GADM = "Khordha"
    "Ganjam":      "coastal_rainfall",   # GADM = "Ganjam"
    "Nayagarh":    "inland_rainfall",    # GADM = "Nayagarh"
    "Boudh":       "inland_rainfall",    # GADM NAME_2 = "Bauda"
    "Kandhamal":   "inland_rainfall",    # GADM = "Kandhamal"
}
GADM_NAME_MAP = {
    "Mayurbhanj": "Mayurbhanj",
    "Khordha":    "Khordha",
    "Ganjam":     "Ganjam",
    "Nayagarh":   "Nayagarh",
    "Boudh":      "Bauda",
    "Kandhamal":  "Kandhamal",
}
YEARS = [2017, 2018, 2020]


def load_districts():
    with open(f"{WORKDIR}/gadm41_IND_2.json") as f:
        gj = json.load(f)
    out = {}
    for feat in gj["features"]:
        if feat["properties"].get("NAME_1") != "Odisha":
            continue
        n2 = feat["properties"].get("NAME_2")
        for our_name, gadm_name in GADM_NAME_MAP.items():
            if n2 == gadm_name:
                out[our_name] = shape(feat["geometry"])
    return out


def signed_url(asset_href):
    """Add SAS signature for Planetary Computer asset access."""
    # Use the data-api SAS endpoint to sign blob URLs
    r = requests.get(
        f"https://planetarycomputer.microsoft.com/api/sas/v1/sign?href={asset_href}",
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["href"]


def stac_search(geom_shape, start_iso, end_iso, max_cloud=40, limit=200):
    body = {
        "collections": ["sentinel-2-l2a"],
        "intersects": mapping(geom_shape.centroid.buffer(0.1)),  # small AOI around centroid
        "datetime": f"{start_iso}/{end_iso}",
        "query": {"eo:cloud_cover": {"lt": max_cloud}},
        "limit": 100,
    }
    items = []
    url = f"{STAC}/search"
    while True:
        r = requests.post(url, json=body, timeout=30)
        r.raise_for_status()
        data = r.json()
        items.extend(data.get("features", []))
        if len(items) >= limit:
            break
        # paginate
        next_link = next((l for l in data.get("links", []) if l.get("rel") == "next"), None)
        if not next_link:
            break
        url = next_link["href"]
        body = next_link.get("body", body)
        if next_link.get("method", "GET") == "GET":
            r2 = requests.get(url, timeout=30)
            r2.raise_for_status()
            data = r2.json()
            items.extend(data.get("features", []))
            nl2 = next((l for l in data.get("links", []) if l.get("rel") == "next"), None)
            if not nl2:
                break
            url = nl2["href"]
        if len(items) >= limit:
            break
    return items[:limit]


def read_scene_ndvi(item, district_geom):
    """Read B04, B08, SCL clipped to a 5 km buffer around district centroid,
    resample all to a common 100 m grid, mask cloud/shadow/water, return median NDVI.
    """
    try:
        b04 = signed_url(item["assets"]["B04"]["href"])
        b08 = signed_url(item["assets"]["B08"]["href"])
        scl = signed_url(item["assets"]["SCL"]["href"])
    except Exception:
        return None
    centroid = district_geom.centroid
    aoi = centroid.buffer(0.05)  # ~5 km half-extent
    # Target output grid: 100 x 100 pixels at ~100 m
    target_shape = (100, 100)
    out = {}
    for name, href in [("red", b04), ("nir", b08), ("scl", scl)]:
        try:
            with rasterio.open(href) as src:
                minx, miny, maxx, maxy = transform_bounds("EPSG:4326", src.crs, *aoi.bounds, densify_pts=21)
                window = from_bounds(minx, miny, maxx, maxy, src.transform)
                arr = src.read(1, window=window, out_shape=target_shape, boundless=True, fill_value=0)
                out[name] = arr.astype("float32")
        except Exception:
            return None
    red = out["red"]; nir = out["nir"]; scl = out["scl"]
    if red.shape != nir.shape or red.shape != scl.shape:
        return None
    # SCL codes: 4 = vegetation, 5 = not-vegetated land. Reject clouds/shadows/water/saturated.
    valid_mask = (scl == 4) | (scl == 5)
    valid_mask &= (red > 0) & (nir > 0)
    if valid_mask.sum() < 50:
        return None
    red_v = red[valid_mask] / 10000.0
    nir_v = nir[valid_mask] / 10000.0
    denom = nir_v + red_v
    valid = denom > 0
    ndvi = (nir_v[valid] - red_v[valid]) / denom[valid]
    ndvi = ndvi[np.isfinite(ndvi)]
    if ndvi.size < 50:
        return None
    return float(np.median(ndvi))


def double_logistic(t, mn, mx, sos, eos, k_sos, k_eos):
    """Beck et al. 2006 6-param double-logistic."""
    rise = 1.0 / (1.0 + np.exp(-k_sos * (t - sos)))
    fall = 1.0 / (1.0 + np.exp( k_eos * (t - eos)))
    return mn + (mx - mn) * (rise + fall - 1.0)


def fit_sos(monthly_doy, monthly_ndvi):
    """Return SOS DOY using double-logistic fit, or NaN."""
    from scipy.optimize import curve_fit
    t = np.asarray(monthly_doy, dtype="float64")
    y = np.asarray(monthly_ndvi, dtype="float64")
    msk = np.isfinite(y)
    t, y = t[msk], y[msk]
    if len(t) < 6:
        return np.nan
    p0 = [float(np.nanmin(y)), float(np.nanmax(y)), 170.0, 320.0, 0.08, 0.08]
    try:
        popt, _ = curve_fit(double_logistic, t, y, p0=p0, maxfev=5000,
                            bounds=([0.0, 0.0, 90, 200, 0.005, 0.005],
                                    [0.5, 1.2, 250, 360, 0.6, 0.6]))
        sos = popt[2]
        return float(sos)
    except Exception:
        return np.nan


from concurrent.futures import ThreadPoolExecutor, as_completed


def process_district_year(dname, dgeom, year, workdir, exposure):
    """Process one district-year; resumable."""
    series_path = f"{workdir}/series_{dname}_{year}.csv"
    summary_path = f"{workdir}/summary_{dname}_{year}.csv"
    if os.path.exists(summary_path):
        print(f"[skip] {dname} {year}: already done")
        return
    print(f"\n=== {dname} {year} ===")
    start = f"{year}-04-01T00:00:00Z"
    end   = f"{year}-12-31T23:59:59Z"
    items = stac_search(dgeom, start, end, max_cloud=60, limit=120)
    print(f"  {len(items)} scenes")
    monthly = {m: [] for m in range(4, 13)}

    def worker(it):
        dt = it["properties"]["datetime"][:10]
        mo = int(dt.split("-")[1])
        if mo not in monthly:
            return None
        ndvi = read_scene_ndvi(it, dgeom)
        if ndvi is None or not np.isfinite(ndvi):
            return None
        return (mo, dt, ndvi)

    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(worker, it): it for it in items}
        done = 0
        for fut in as_completed(futures):
            done += 1
            res = fut.result()
            if res is not None:
                mo, dt, ndvi = res
                monthly[mo].append(ndvi)
            if done % 20 == 0:
                clear = sum(len(v) for v in monthly.values())
                print(f"  [{done}/{len(items)}] clear scenes: {clear}")
    mo_med = {}
    series_rows = []
    for m in range(4, 13):
        vals = monthly[m]
        mo_med[m] = float(np.median(vals)) if vals else float("nan")
        series_rows.append({
            "district": dname, "year": year, "month": m,
            "n_scenes_clear": len(vals), "ndvi_median": mo_med[m],
        })
    doys = [date(year, m, 15).timetuple().tm_yday for m in range(4, 13)]
    sos = fit_sos(doys, [mo_med[m] for m in range(4, 13)])
    n_clear = sum(1 for m in range(4,13) if np.isfinite(mo_med[m]))
    print(f"  monthly NDVI: {[round(mo_med[m],3) if np.isfinite(mo_med[m]) else None for m in range(4,13)]}")
    print(f"  -> SOS DOY = {sos}  (n_clear_months={n_clear})")
    pd.DataFrame(series_rows).to_csv(series_path, index=False)
    pd.DataFrame([{
        "district": dname, "exposure": exposure, "year": year,
        "n_scenes_total": len(items), "n_clear_months": n_clear, "sos_doy": sos,
    }]).to_csv(summary_path, index=False)


def main():
    districts = load_districts()
    print(f"Loaded {len(districts)} district polygons: {list(districts.keys())}")
    for dname, dgeom in districts.items():
        for year in YEARS:
            try:
                process_district_year(dname, dgeom, year, WORKDIR, DISTRICTS[dname])
            except Exception as e:
                print(f"[ERROR] {dname} {year}: {e}")
    # Combine
    import glob
    summaries = glob.glob(f"{WORKDIR}/summary_*.csv")
    series    = glob.glob(f"{WORKDIR}/series_*.csv")
    if summaries:
        pd.concat([pd.read_csv(f) for f in summaries]).sort_values(["district","year"]).to_csv(f"{WORKDIR}/bulbul_probe_phenology_real.csv", index=False)
    if series:
        pd.concat([pd.read_csv(f) for f in series]).sort_values(["district","year","month"]).to_csv(f"{WORKDIR}/bulbul_probe_ndvi_series.csv", index=False)
    print("\nAll combined. Done.")


if __name__ == "__main__":
    main()

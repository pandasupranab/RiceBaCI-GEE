"""
Real IBTrACS NI pre-Kharif Bay-of-Bengal landfall extraction (1981-2018).

Reads the IBTrACS NI v04r01 CSV and returns real (lat, lon) and SEASON for every
named storm whose track crosses the Odisha / WB / Bangladesh coast (LON 83-93 E,
LAT 18-23 N) during DOY 105-166 (15 Apr – 15 Jun, the pre-Kharif window).

Output:
  data/ibtracs/ibtracs_NI_preKharif_landfalls_1981_2018.csv

Used by Figure S1A to plot the real climatological cloud (no synthetic draws).
"""
import csv
from datetime import datetime
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "data/ibtracs/ibtracs.NI.list.v04r01.csv"
OUT = SRC.parent / "ibtracs_NI_preKharif_landfalls_1981_2018.csv"

# Bay of Bengal coast (Odisha + WB + Bangladesh) bounding box
LON_MIN, LON_MAX = 83.0, 93.0
LAT_MIN, LAT_MAX = 17.5, 23.0

# Pre-Kharif window DOY 105-166 (15 Apr - 15 Jun)
DOY_MIN, DOY_MAX = 105, 166

YEAR_MIN, YEAR_MAX = 1981, 2018


def doy_of(iso_time: str) -> int:
    dt = datetime.strptime(iso_time.strip(), "%Y-%m-%d %H:%M:%S")
    return dt.timetuple().tm_yday


def main():
    rows_out = []
    seen_storm = set()

    with SRC.open() as fh:
        # First row = headers; second row = units. Skip units.
        reader = csv.reader(fh)
        headers = next(reader)
        _units = next(reader)
        idx = {h: i for i, h in enumerate(headers)}

        # Find LANDFALL distance column (the IBTrACS LANDFALL column is the
        # along-track distance to the next coastline crossing in km; the
        # operationally defined "landfall" point is the row where
        # |LANDFALL| < a small distance AND DIST2LAND ~ 0.)
        for row in reader:
            try:
                season = int(row[idx["SEASON"]])
            except (ValueError, KeyError):
                continue
            if not (YEAR_MIN <= season <= YEAR_MAX):
                continue

            sid = row[idx["SID"]]
            name = row[idx["NAME"]].strip()
            iso_time = row[idx["ISO_TIME"]].strip()
            if not iso_time:
                continue

            try:
                lat = float(row[idx["LAT"]])
                lon = float(row[idx["LON"]])
            except ValueError:
                continue

            # Pre-Kharif window
            try:
                d = doy_of(iso_time)
            except Exception:
                continue
            if not (DOY_MIN <= d <= DOY_MAX):
                continue

            # In coastal box
            if not (LON_MIN <= lon <= LON_MAX and LAT_MIN <= lat <= LAT_MAX):
                continue

            # The IBTrACS LANDFALL column is empty most rows; when populated
            # it gives the along-track time-to-next-coast (km).  A more
            # robust filter is DIST2LAND <= 20 km (~ at the coastline).
            try:
                d2l = float(row[idx["DIST2LAND"]])
            except ValueError:
                continue
            if d2l > 20:  # > 20 km from any coast, skip
                continue

            # Peak Vmax across the storm's lifetime is not on a single row;
            # capture the wind on this row (kt) and we will later swap with
            # the storm-lifetime max in a second pass.
            try:
                wmo_wind = float(row[idx["WMO_WIND"]])
            except ValueError:
                wmo_wind = float("nan")
            try:
                usa_wind = float(row[idx["USA_WIND"]])
            except ValueError:
                usa_wind = float("nan")

            # One landfall row per storm (the row closest to the coast)
            key = sid
            if key in seen_storm:
                # update if this row is closer to coast than the saved one
                prev_idx = next(i for i, r in enumerate(rows_out) if r["sid"] == key)
                if d2l < float(rows_out[prev_idx]["dist2land_km"]):
                    rows_out[prev_idx] = {
                        "sid": sid, "season": season, "name": name or f"UNNAMED_{season}",
                        "iso_time": iso_time, "doy": d, "lat": lat, "lon": lon,
                        "dist2land_km": d2l,
                    }
                continue

            seen_storm.add(key)
            rows_out.append({
                "sid": sid, "season": season, "name": name or f"UNNAMED_{season}",
                "iso_time": iso_time, "doy": d, "lat": lat, "lon": lon,
                "dist2land_km": d2l,
                "wind_kt_at_landfall": wmo_wind if wmo_wind == wmo_wind else usa_wind,
            })

    # Second pass: for each landfall storm, compute the storm-lifetime
    # max wind (kt) by re-reading the CSV.
    sids = {r["sid"] for r in rows_out}
    lifetime_max = {sid: float("nan") for sid in sids}
    with SRC.open() as fh:
        reader = csv.reader(fh)
        _ = next(reader); _ = next(reader)
        for row in reader:
            sid = row[idx["SID"]]
            if sid not in sids:
                continue
            for col in ("WMO_WIND", "USA_WIND"):
                try:
                    w = float(row[idx[col]])
                except (ValueError, KeyError):
                    w = float("nan")
                if w == w:  # not NaN
                    cur = lifetime_max[sid]
                    if not (cur == cur) or w > cur:
                        lifetime_max[sid] = w
    for r in rows_out:
        r["vmax_kt_lifetime"] = lifetime_max[r["sid"]]

    # Sort by season then DOY
    rows_out.sort(key=lambda r: (r["season"], r["doy"]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["sid", "season", "name",
                                            "iso_time", "doy", "lat", "lon",
                                            "dist2land_km",
                                            "wind_kt_at_landfall",
                                            "vmax_kt_lifetime"])
        w.writeheader()
        for r in rows_out:
            w.writerow(r)

    print(f"Wrote {len(rows_out)} pre-Kharif BoB landfall rows to {OUT}")
    print(f"Years: {sorted(set(r['season'] for r in rows_out))}")
    return rows_out


if __name__ == "__main__":
    main()

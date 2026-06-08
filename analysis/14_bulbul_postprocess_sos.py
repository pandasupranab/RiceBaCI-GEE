"""
Post-process Bulbul probe phenology with a robust SOS estimator.

Strategy:
  Primary  — Beck 2006 6-parameter double-logistic fit (already attempted).
  Fallback — Threshold-based SOS (TIMESAT-style): SOS = DOY at which the
             monthly NDVI series first crosses min + 0.30 * (max - min)
             during the rising leg.  This works on as few as 4 monthly
             points and produces a defensible Kharif-window estimate.

Output: bulbul_probe_phenology_robust.csv with three SOS columns:
  sos_dl    (double-logistic, may be NaN)
  sos_thr   (threshold, robust)
  sos_used  (sos_dl if finite, else sos_thr)
"""
import glob
from pathlib import Path
import numpy as np
import pandas as pd

WORKDIR = Path(__file__).resolve().parent
THRESHOLD = 0.30   # fraction of amplitude
# Kharif window: SOS is searched within DOY 90 - 250 (1 Apr - 7 Sep)
DOY_LO, DOY_HI = 90, 250

# Map month -> mid-month DOY
MONTH_DOY = {4: 105, 5: 135, 6: 166, 7: 196, 8: 227, 9: 258, 10: 288,
             11: 319, 12: 349}


def threshold_sos(months, ndvi):
    """Linear interpolation of SOS at 30% of amplitude (rising leg only).

    `months` is the list of months 4..12 in order, `ndvi` the corresponding
    monthly median (may contain NaN). Returns a DOY or NaN.
    """
    a = np.array([(MONTH_DOY[m], v) for m, v in zip(months, ndvi)
                  if v is not None and np.isfinite(v)],
                 dtype="float64")
    if len(a) < 4:
        return np.nan
    doy = a[:, 0]
    y = a[:, 1]

    y_min = float(np.min(y))
    y_max = float(np.max(y))
    if y_max - y_min < 0.05:
        return np.nan
    thr = y_min + THRESHOLD * (y_max - y_min)

    # peak index = position of max
    pk = int(np.argmax(y))
    if pk == 0:
        # series already peaked at first month; no rising leg observed
        return np.nan

    # walk left from peak looking for crossing
    for i in range(pk - 1, -1, -1):
        y_lo, y_hi = y[i], y[i + 1]
        d_lo, d_hi = doy[i], doy[i + 1]
        if y_lo <= thr <= y_hi:
            # linear interp
            if y_hi == y_lo:
                sos = d_lo
            else:
                sos = d_lo + (thr - y_lo) * (d_hi - d_lo) / (y_hi - y_lo)
            if DOY_LO <= sos <= DOY_HI:
                return float(sos)
    # if we never crossed, fallback: first month where y > thr
    for i in range(len(y)):
        if y[i] >= thr:
            return float(doy[i])
    return np.nan


def main():
    summaries = sorted(glob.glob(str(WORKDIR / "summary_*.csv")))
    series_files = sorted(glob.glob(str(WORKDIR / "series_*.csv")))
    if not summaries:
        print("No summaries found.")
        return

    # Load series into a dict keyed by (district, year) -> {month: ndvi}
    series_lookup = {}
    for sf in series_files:
        df = pd.read_csv(sf)
        if df.empty:
            continue
        d = df["district"].iloc[0]
        y = int(df["year"].iloc[0])
        m2v = {}
        for _, r in df.iterrows():
            m2v[int(r["month"])] = (float(r["ndvi_median"])
                                    if r["ndvi_median"] == r["ndvi_median"]
                                    else None)
        series_lookup[(d, y)] = m2v

    rows = []
    for sf in summaries:
        df = pd.read_csv(sf)
        for _, r in df.iterrows():
            d, y = r["district"], int(r["year"])
            m2v = series_lookup.get((d, y), {})
            months = sorted(m2v.keys())
            ndvi = [m2v[m] for m in months]
            sos_dl = float(r["sos_doy"]) if r["sos_doy"] == r["sos_doy"] else np.nan
            sos_thr = threshold_sos(months, ndvi)
            sos_used = sos_dl if np.isfinite(sos_dl) else sos_thr
            rows.append({
                "district": d, "exposure": r["exposure"], "year": y,
                "n_scenes_total": int(r["n_scenes_total"]),
                "n_clear_months": int(r["n_clear_months"]),
                "sos_dl": round(sos_dl, 1) if np.isfinite(sos_dl) else np.nan,
                "sos_thr": round(sos_thr, 1) if np.isfinite(sos_thr) else np.nan,
                "sos_used": round(sos_used, 1) if np.isfinite(sos_used) else np.nan,
            })

    out = pd.DataFrame(rows).sort_values(["district", "year"])
    out_path = WORKDIR / "bulbul_probe_phenology_robust.csv"
    out.to_csv(out_path, index=False)
    print(f"Wrote {len(out)} rows to {out_path}")
    print(out.to_string(index=False))

    # Per-district baseline / shock
    print("\n=== Per-district Δ_obs = SOS_2020 − mean(SOS_2017, SOS_2018) ===\n")
    deltas = []
    for d in sorted(out["district"].unique()):
        sub = out[out["district"] == d].set_index("year")
        sos_2017 = sub.loc[2017, "sos_used"] if 2017 in sub.index else np.nan
        sos_2018 = sub.loc[2018, "sos_used"] if 2018 in sub.index else np.nan
        sos_2020 = sub.loc[2020, "sos_used"] if 2020 in sub.index else np.nan
        baseline = np.nanmean([sos_2017, sos_2018])
        delta = sos_2020 - baseline if (np.isfinite(sos_2020)
                                         and np.isfinite(baseline)) else np.nan
        exposure = sub["exposure"].iloc[0]
        deltas.append({
            "district": d, "exposure": exposure,
            "sos_2017": sos_2017, "sos_2018": sos_2018,
            "sos_baseline": round(baseline, 1) if np.isfinite(baseline) else np.nan,
            "sos_2020": sos_2020,
            "delta_obs_d": round(delta, 1) if np.isfinite(delta) else np.nan,
        })
    deltas_df = pd.DataFrame(deltas)
    print(deltas_df.to_string(index=False))
    deltas_df.to_csv(WORKDIR / "bulbul_probe_deltas.csv", index=False)
    print(f"\nWrote per-district deltas to bulbul_probe_deltas.csv")


if __name__ == "__main__":
    main()

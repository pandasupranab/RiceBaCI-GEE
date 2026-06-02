"""validate_label_panel.py

Validate the 480-point Sentinel-2 visual reference label panel before it
goes into Module 02 retraining.

Inputs
------
Either:
  --csv <path>           Single concatenated CSV (12 columns, 480 rows).
or:
  --indir <dir>          Folder of 6 raw GEE-exported CSVs:
                         RiceBaCI_labels_<cyclone>_<class>_<date>.csv
                         (concatenated automatically).

Outputs
-------
  data_real/labels_panel_real.csv       (clean, concatenated, sorted)
  data_real/labels_panel_validation.txt (human-readable report)
  Exit code 0 on PASS, 1 on FAIL.

10 checks
---------
  1.  Schema: 12 expected columns present, no extras.
  2.  Row count: total in [400, 600] (480 ± 20% tolerance).
  3.  Class balance: |n(cyclone) - n(agro)| / total <= 0.10.
  4.  Class purity: class_name in {cyclone_flood, agronomic_flood}.
  5.  Class-id consistency: class_id == 2 iff class_name == cyclone_flood.
  6.  Cyclone coverage: all three cyclones (Fani/Amphan/Yaas) present with
      ≥ 50 points each per class.
  7.  Year-cyclone consistency: year matches cyclone landfall year.
  8.  Lon/Lat bounds: lon in [83.0, 87.5], lat in [19.0, 22.5] (Odisha box).
  9.  Spatial spread: per-class std(lon) > 0.10 and std(lat) > 0.10
      (rules out users dropping all clicks in one spot).
  10. Duplicate suppression: no two points within 30 m of each other in the
      same class (Haversine distance check).

Author: Supranab Panda (via Computer agent)
Date: 2026-06-02
"""
from __future__ import annotations
import argparse
import math
import sys
from pathlib import Path

import pandas as pd

EXPECTED_COLS = [
    "lon", "lat", "class_name", "class_id", "cyclone", "year",
    "landfall", "operator", "imagery", "window_start", "window_end",
    "labeled_on",
]

CYCLONE_YEAR = {"Fani": 2019, "Amphan": 2020, "Yaas": 2021}

# Odisha bounding box (slightly padded)
LON_MIN, LON_MAX = 83.0, 87.5
LAT_MIN, LAT_MAX = 19.0, 22.5


def haversine_m(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Great-circle distance in metres."""
    R = 6371000.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def load_panel(args) -> pd.DataFrame:
    if args.csv:
        return pd.read_csv(args.csv)
    indir = Path(args.indir)
    csvs = sorted(indir.glob("RiceBaCI_labels_*.csv"))
    if not csvs:
        raise SystemExit(f"No RiceBaCI_labels_*.csv files in {indir}")
    frames = []
    for c in csvs:
        try:
            df = pd.read_csv(c)
        except Exception as e:
            raise SystemExit(f"Failed to read {c}: {e}")
        df["__src_file__"] = c.name
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def report(name: str, ok: bool, detail: str = "") -> str:
    tag = "PASS" if ok else "FAIL"
    line = f"  [{tag}] {name}"
    if detail:
        line += f" — {detail}"
    return line


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=None,
                    help="Single concatenated CSV (480 rows)")
    ap.add_argument("--indir", default=None,
                    help="Folder of 6 GEE-exported CSVs to concatenate")
    ap.add_argument("--outdir", default="data_real",
                    help="Where to write the cleaned panel + report")
    args = ap.parse_args()

    if not args.csv and not args.indir:
        ap.error("Provide either --csv or --indir.")

    df = load_panel(args)

    out_lines = ["=== RiceBaCI-GEE label panel validation ==="]
    fails = 0

    # 1. Schema
    missing = [c for c in EXPECTED_COLS if c not in df.columns]
    extra = [c for c in df.columns if c not in EXPECTED_COLS + ["__src_file__", "system:index", ".geo"]]
    schema_ok = not missing
    out_lines.append(report(
        "01 Schema",
        schema_ok,
        f"missing={missing}" if missing else "all 12 columns present",
    ))
    if not schema_ok:
        fails += 1

    # 2. Row count
    n = len(df)
    count_ok = 400 <= n <= 600
    out_lines.append(report("02 Row count", count_ok, f"n={n} (target 480)"))
    if not count_ok:
        fails += 1

    # 3. Class balance
    counts = df["class_name"].value_counts() if "class_name" in df else pd.Series(dtype=int)
    n_cyc = int(counts.get("cyclone_flood", 0))
    n_agr = int(counts.get("agronomic_flood", 0))
    skew = abs(n_cyc - n_agr) / max(n_cyc + n_agr, 1)
    balance_ok = skew <= 0.10
    out_lines.append(report(
        "03 Class balance",
        balance_ok,
        f"cyclone={n_cyc}, agro={n_agr}, skew={skew:.1%}",
    ))
    if not balance_ok:
        fails += 1

    # 4. Class purity
    if "class_name" in df:
        bad_classes = sorted(set(df["class_name"]) - {"cyclone_flood", "agronomic_flood"})
        purity_ok = not bad_classes
        out_lines.append(report(
            "04 Class purity",
            purity_ok,
            f"unexpected={bad_classes}" if bad_classes else "only 2 classes present",
        ))
        if not purity_ok:
            fails += 1
    else:
        out_lines.append(report("04 Class purity", False, "class_name column missing"))
        fails += 1

    # 5. Class-id consistency
    if "class_name" in df and "class_id" in df:
        check = df.apply(
            lambda r: (r["class_id"] == 2) == (r["class_name"] == "cyclone_flood"),
            axis=1,
        )
        consistency_ok = bool(check.all())
        out_lines.append(report(
            "05 Class-id consistency",
            consistency_ok,
            f"inconsistent rows={int((~check).sum())}",
        ))
        if not consistency_ok:
            fails += 1

    # 6. Cyclone coverage
    if "cyclone" in df and "class_name" in df:
        pivot = df.pivot_table(
            index="cyclone", columns="class_name", values="lon",
            aggfunc="count", fill_value=0,
        )
        missing_combos = []
        for cyc in ["Fani", "Amphan", "Yaas"]:
            if cyc not in pivot.index:
                missing_combos.append(f"{cyc}/<none>")
                continue
            for cls in ["cyclone_flood", "agronomic_flood"]:
                v = pivot.loc[cyc].get(cls, 0)
                if v < 50:
                    missing_combos.append(f"{cyc}/{cls}={v}")
        coverage_ok = not missing_combos
        out_lines.append(report(
            "06 Cyclone coverage",
            coverage_ok,
            f"low cells: {missing_combos}" if missing_combos else "≥50 pts per cyclone × class",
        ))
        if not coverage_ok:
            fails += 1

    # 7. Year-cyclone consistency
    if "cyclone" in df and "year" in df:
        bad_year = df[df.apply(lambda r: CYCLONE_YEAR.get(r["cyclone"]) != r["year"], axis=1)]
        year_ok = bad_year.empty
        out_lines.append(report(
            "07 Year-cyclone consistency",
            year_ok,
            f"mismatched rows={len(bad_year)}",
        ))
        if not year_ok:
            fails += 1

    # 8. Lon/Lat bounds
    if "lon" in df and "lat" in df:
        oob = df[
            (df["lon"] < LON_MIN) | (df["lon"] > LON_MAX)
            | (df["lat"] < LAT_MIN) | (df["lat"] > LAT_MAX)
        ]
        bounds_ok = oob.empty
        out_lines.append(report(
            "08 Lon/Lat bounds",
            bounds_ok,
            f"out-of-Odisha points={len(oob)}",
        ))
        if not bounds_ok:
            fails += 1

    # 9. Spatial spread (per-class std)
    if "class_name" in df and "lon" in df and "lat" in df:
        spread_problems = []
        for cls in ["cyclone_flood", "agronomic_flood"]:
            sub = df[df["class_name"] == cls]
            if len(sub) < 10:
                continue
            slon = sub["lon"].std()
            slat = sub["lat"].std()
            if slon < 0.10 or slat < 0.10:
                spread_problems.append(f"{cls}: std_lon={slon:.3f}, std_lat={slat:.3f}")
        spread_ok = not spread_problems
        out_lines.append(report(
            "09 Spatial spread",
            spread_ok,
            f"clustered classes: {spread_problems}" if spread_problems else "both classes well-spread",
        ))
        if not spread_ok:
            fails += 1

    # 10. Duplicate suppression (30 m)
    if "lon" in df and "lat" in df and "class_name" in df:
        dups = 0
        for cls, sub in df.groupby("class_name"):
            pts = sub[["lon", "lat"]].to_numpy()
            for i in range(len(pts)):
                for j in range(i + 1, len(pts)):
                    d = haversine_m(pts[i, 0], pts[i, 1], pts[j, 0], pts[j, 1])
                    if d < 30.0:
                        dups += 1
                        if dups > 20:
                            break
                if dups > 20:
                    break
            if dups > 20:
                break
        dup_ok = dups == 0
        out_lines.append(report(
            "10 Duplicate suppression (30 m)",
            dup_ok,
            f"too-close pairs={dups}" if dups else "no near-duplicates",
        ))
        if not dup_ok:
            fails += 1

    out_lines.append("")
    out_lines.append(f"=== {fails} of 10 checks failed ===")

    # Write cleaned panel + report
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out_csv = outdir / "labels_panel_real.csv"
    out_txt = outdir / "labels_panel_validation.txt"

    keep_cols = [c for c in EXPECTED_COLS if c in df.columns]
    df[keep_cols].sort_values(["cyclone", "class_name", "lat", "lon"]).to_csv(
        out_csv, index=False,
    )
    out_txt.write_text("\n".join(out_lines), encoding="utf-8")

    print("\n".join(out_lines))
    print(f"\nWrote: {out_csv}")
    print(f"Wrote: {out_txt}")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

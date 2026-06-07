"""refresh_v21_from_module12.py

End-to-end refresh of the v2.1 pipeline once the Module 12 GEE export
(cyclone_pixel_share_v21.csv) lands. Replaces the provisional Amphan + Yaas
rows in data_real/cyclone_pixel_share.csv with the exact polygon-intersection
numbers, then re-runs the bounded-shift correction, DiD, WCB, jackknife,
placebo, figures, supplement tables, manuscript sweep, and DOCX rebuilds.

Usage:
    # Drop the Module 12 export at downloads/cyclone_pixel_share_v21.csv
    # (Drive → RiceBaCI_labels/cyclone_pixel_share_v21.csv)
    python scripts/refresh_v21_from_module12.py [--module12-csv PATH]

This is idempotent — safe to re-run after any further Module 12 refinement.

Author: Supranab Panda (via Computer agent)
Date  : 2026-06-08
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path("/home/user/workspace/RiceBaCI-GEE")
WS   = Path("/home/user/workspace")

DEFAULT_M12 = WS / "downloads" / "cyclone_pixel_share_v21.csv"
PIXEL_SHARE = ROOT / "data_real" / "cyclone_pixel_share.csv"
PIXEL_SHARE_BAK = ROOT / "data_real" / "cyclone_pixel_share.pre_module12.csv"

STUDY_DISTRICTS = [
    "Angul", "Baleshwar", "Bhadrak", "Cuttack", "Dhenkanal",
    "Jagatsinghpur", "Kendrapara", "Puri",
]
# GADM admin-2 sometimes spells "Baleshwar" as "Balasore"; normalise.
DISTRICT_ALIASES = {
    "Balasore": "Baleshwar",
    "Baleswar": "Baleshwar",
    "Khordha":  "Khordha",  # not in study; will be dropped
}


def run(cmd, cwd=ROOT):
    print(f"\n$ {' '.join(str(c) for c in cmd)}")
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"STDERR: {r.stderr[:1000]}")
        raise SystemExit(f"command failed: {cmd}")
    print(r.stdout[-800:] if r.stdout else "")
    return r


def refresh_pixel_share(module12_csv: Path):
    """Merge Module 12 exact Amphan + Yaas numbers into pixel_share.csv.

    Fani 2019 rows are KEPT (already exact via EMSR357 geopandas);
    Amphan 2020 and Yaas 2021 rows are REPLACED.
    """
    if not module12_csv.exists():
        raise SystemExit(
            f"Module 12 CSV not found at {module12_csv}.\n"
            f"Drop the GEE export there (Drive → RiceBaCI_labels → cyclone_pixel_share_v21.csv)\n"
            f"or pass --module12-csv PATH."
        )

    print(f"[1/9] Loading Module 12 export from {module12_csv}")
    m12 = pd.read_csv(module12_csv)
    print(f"      rows: {len(m12)}; cols: {list(m12.columns)}")

    # Backup current
    shutil.copy(PIXEL_SHARE, PIXEL_SHARE_BAK)
    print(f"      backup → {PIXEL_SHARE_BAK}")

    cur = pd.read_csv(PIXEL_SHARE)
    print(f"      current pixel-share rows: {len(cur)}")

    # Normalise district names in Module 12
    m12["district"] = m12["district"].replace(DISTRICT_ALIASES)
    m12 = m12[m12["district"].isin(STUDY_DISTRICTS)].copy()

    # Mark source as exact
    m12["source"] = "Module12_GEE_polygon_intersection"
    keep = ["district", "year", "cyclone", "district_area_km2",
            "flood_area_km2", "flood_share", "source"]
    m12 = m12[keep]
    print(f"      Module 12 rows after district filter: {len(m12)}")

    # Drop Amphan 2020 and Yaas 2021 from current; append Module 12
    new = pd.concat([
        cur[~cur["cyclone"].isin(["Amphan", "Yaas"])],
        m12[m12["cyclone"].isin(["Amphan", "Yaas"])],
    ], ignore_index=True)
    new = new.sort_values(["year", "cyclone", "district"]).reset_index(drop=True)
    new.to_csv(PIXEL_SHARE, index=False)

    print(f"      → wrote {PIXEL_SHARE} ({len(new)} rows)")
    print("      Per-cyclone totals (km²):")
    for cyc in ["Fani", "Amphan", "Yaas"]:
        sub = new[new["cyclone"] == cyc]
        tot = sub["flood_area_km2"].sum()
        nz = (sub["flood_area_km2"] > 0).sum()
        src = sub["source"].iloc[0] if len(sub) else "?"
        print(f"        {cyc:7s}  total {tot:7.2f} km²  ({nz} districts > 0)  [{src}]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--module12-csv", type=Path, default=DEFAULT_M12,
                    help=f"Path to Module 12 GEE export (default: {DEFAULT_M12})")
    ap.add_argument("--skip-push", action="store_true",
                    help="Skip the final GitHub push (default: push)")
    args = ap.parse_args()

    refresh_pixel_share(args.module12_csv)

    print("\n[2/9] Re-running v2.1 bounded-shift correction")
    run([sys.executable, "analysis/03b_apply_v21_correction.py"])

    print("\n[3/9] Re-running DiD on corrected panel")
    run([sys.executable, "analysis/05_did_regression.py",
         "--panel", "analysis/baci_panel_real_v21.csv",
         "--outdir", "analysis/results/real_v21"])

    print("\n[4/9] Re-running WCR bootstrap (B=9999)")
    run([sys.executable, "analysis/05a_wild_cluster_bootstrap.py",
         "--panel", "analysis/baci_panel_real_v21.csv",
         "--outdir", "analysis/results/real_v21",
         "--B", "9999", "--no-ci"])

    print("\n[5/9] Re-running jackknife + placebo")
    run([sys.executable, "analysis/05d_jackknife_sensitivity.py",
         "--panel", "analysis/baci_panel_real_v21.csv",
         "--outdir", "analysis/results/real_v21"])
    run([sys.executable, "analysis/05e_placebo_tests.py",
         "--panel", "analysis/baci_panel_real_v21.csv",
         "--outdir", "analysis/results/real_v21"])

    print("\n[6/9] Rebuilding figures (fig2 / fig3 / fig4)")
    run([sys.executable, "analysis/06_figures.py",
         "--panel", "analysis/baci_panel_real_v21.csv",
         "--outdir", "figures/real_v21"])

    print("\n[7/9] Rebuilding supplement tables S1, S2, S4, S5")
    run([sys.executable, "analysis/07_supplement_tables.py",
         "--results", "analysis/results/real_v21",
         "--outdir", "manuscript/supplement/real_v21"])
    # Promote v2.1 tables to supplement root for the combined bundle
    for tbl in ["Table_S1_did_static.docx", "Table_S2_pretrends.docx",
                "Table_S4_wild_bootstrap.docx", "Table_S5_jackknife.docx"]:
        src = ROOT / "manuscript" / "supplement" / "real_v21" / tbl
        dst = ROOT / "manuscript" / "supplement" / tbl
        if src.exists():
            shutil.copy(src, dst)
            print(f"      promoted {tbl}")

    print("\n[8/9] Sweeping manuscript and rebuilding DOCX")
    # The sweep is idempotent on a freshly-built MS — first restore from pre_b19
    # backup so we sweep a clean baseline, then re-sweep with new numbers.
    pre_b19 = ROOT / "manuscript" / "manuscript_text.pre_b19.md"
    ms = ROOT / "manuscript" / "manuscript_text.md"
    if pre_b19.exists():
        shutil.copy(pre_b19, ms)
        print(f"      restored {ms} from pre_b19 baseline")
    run([sys.executable, "scripts/sweep_v21_classifier_corrected.py"])
    run([sys.executable, str(WS / "build_manuscript_docx.py")])
    run([sys.executable, str(WS / "build_supplement_bundle.py")])
    # Copy combined supplement to canonical name
    src = ROOT / "manuscript" / "supplement" / "Supplement_v0.3.0.docx"
    dst = ROOT / "manuscript" / "Supplement_Combined.docx"
    shutil.copy(src, dst)
    print(f"      → {dst}")

    if args.skip_push:
        print("\n[9/9] Skipping push (--skip-push)")
    else:
        print("\n[9/9] Pushing refreshed artefacts to GitHub")
        run([sys.executable, "scripts/_push_b19.py"])

    print("\n=== Refresh complete ===")
    print("    Manuscript.docx, Supplement_Combined.docx now reflect exact")
    print("    Module 12 Amphan + Yaas pixel-share numbers.")
    print("    If push succeeded, tag the refreshed commit with:")
    print("        v1.0.0-rc3.1-module12-refresh  (or v1.0.0-submission)")


if __name__ == "__main__":
    main()

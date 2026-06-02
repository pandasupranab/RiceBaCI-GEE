#!/usr/bin/env python3
"""
Validator for bacI_panel_real.csv before sending to the agent.

Usage:
    python3 validate_real_panel.py /path/to/bacI_panel_real.csv

Exit code 0 = OK ready for ingestion.
Exit code 1 = problems printed; fix and re-run.

Requires: pandas only.
"""
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas not installed. Run:  pip install pandas")
    sys.exit(1)

EXPECTED_COLS = [
    "district_id", "district_name", "year", "treatment", "event",
    "metric", "value_days", "n_pixels", "qa_flag",
]
EXPECTED_DISTRICT_IDS = {"BLS", "BHA", "KDP", "JGS", "PUR", "DHK", "ANG", "CTK"}
EXPECTED_YEARS = set(range(2017, 2025))
EXPECTED_METRICS = {"SOS", "POS", "EOS"}
EXPECTED_EVENTS = {"Fani", "Amphan", "Yaas", "Bulbul", "none"}
EXPECTED_QA = {"OK", "gap-filled", "excluded"}


def fail(msg):
    print(f"  ✗ {msg}")


def ok(msg):
    print(f"  ✓ {msg}")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    path = Path(sys.argv[1]).expanduser()
    if not path.exists():
        print(f"ERROR: {path} not found")
        sys.exit(1)

    print(f"\nValidating {path.name}\n" + "─" * 60)
    df = pd.read_csv(path)
    issues = 0

    # 1. Columns
    print("\n[1] Columns")
    missing = [c for c in EXPECTED_COLS if c not in df.columns]
    extra = [c for c in df.columns if c not in EXPECTED_COLS]
    if missing:
        fail(f"missing columns: {missing}")
        issues += 1
    if extra:
        fail(f"unexpected extra columns: {extra}")
        issues += 1
    if not missing and not extra:
        ok("9 expected columns present, none extra")

    if missing:
        print("\nFIX: rename your columns to match exactly:")
        print("  " + ",".join(EXPECTED_COLS))
        sys.exit(1)

    # 2. Row count
    print("\n[2] Row count")
    if len(df) == 192:
        ok(f"192 rows as expected (8 districts × 8 years × 3 metrics)")
    else:
        fail(f"got {len(df)} rows, expected 192. Most likely a missing "
             f"district-year-metric combination or duplicates.")
        issues += 1

    # 3. District IDs
    print("\n[3] district_id values")
    actual = set(df["district_id"].unique())
    if actual == EXPECTED_DISTRICT_IDS:
        ok("all 8 expected codes present")
    else:
        fail(f"unexpected codes: got {actual}, expected {EXPECTED_DISTRICT_IDS}")
        issues += 1

    # 4. Years
    print("\n[4] year values")
    yrs = set(df["year"].astype(int).unique())
    if yrs == EXPECTED_YEARS:
        ok("all 8 years 2017–2024 present")
    else:
        fail(f"got years {sorted(yrs)}, expected {sorted(EXPECTED_YEARS)}")
        issues += 1

    # 5. Treatment binary
    print("\n[5] treatment column (must be 0/1)")
    if set(df["treatment"].unique()).issubset({0, 1}):
        # cross-check: coastal must be 1
        coast = df[df["district_id"].isin(
            {"BLS", "BHA", "KDP", "JGS", "PUR"})]["treatment"].unique()
        inland = df[df["district_id"].isin(
            {"DHK", "ANG", "CTK"})]["treatment"].unique()
        if list(coast) == [1] and list(inland) == [0]:
            ok("treatment correctly assigned (coastal=1, inland=0)")
        else:
            fail(f"treatment mis-assigned: coastal got {coast}, "
                 f"inland got {inland}")
            issues += 1
    else:
        fail(f"unexpected treatment values: {df['treatment'].unique()}")
        issues += 1

    # 6. Events
    print("\n[6] event column")
    evts = set(df["event"].dropna().unique())
    bad = evts - EXPECTED_EVENTS
    if not bad:
        ok(f"all events recognised ({evts})")
    else:
        fail(f"unknown event labels: {bad}; allowed: {EXPECTED_EVENTS}")
        issues += 1

    # 7. Metrics
    print("\n[7] metric column")
    if set(df["metric"].unique()) == EXPECTED_METRICS:
        ok("SOS / POS / EOS all present")
    else:
        fail(f"got metrics {df['metric'].unique()}, expected {EXPECTED_METRICS}")
        issues += 1

    # 8. value_days range
    print("\n[8] value_days range (1–366 or empty)")
    nonnull = df["value_days"].dropna()
    bad_rows = nonnull[(nonnull < 1) | (nonnull > 366)]
    if len(bad_rows) == 0:
        ok(f"{len(nonnull)} non-null values, all within DOY 1–366; "
           f"{len(df) - len(nonnull)} legitimate nulls")
    else:
        fail(f"{len(bad_rows)} values outside 1–366: {bad_rows.tolist()}")
        issues += 1

    # 9. n_pixels positive
    print("\n[9] n_pixels positive")
    if (df["n_pixels"] >= 0).all():
        ok(f"all n_pixels ≥ 0 (median {int(df['n_pixels'].median())})")
    else:
        fail("negative n_pixels found")
        issues += 1

    # 10. qa_flag values
    print("\n[10] qa_flag values")
    qas = set(df["qa_flag"].unique())
    if qas.issubset(EXPECTED_QA):
        ok(f"qa_flag values valid: {qas}")
    else:
        fail(f"unexpected qa_flag values: {qas - EXPECTED_QA}")
        issues += 1

    # Summary
    print("\n" + "─" * 60)
    if issues == 0:
        print("OK — panel ready for ingestion.\n")
        print("Next: drop bacI_panel_real.csv into your Google Drive folder")
        print("      RiceBaCI_real_data and share the link in the chat.")
        sys.exit(0)
    else:
        print(f"FAIL — {issues} issue(s) found. Fix and re-run.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

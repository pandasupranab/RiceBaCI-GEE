"""
Self-iterating audit loop.

Each pass:
  1. Runs scripts/audit_manuscript.py
  2. Writes the report to audit_pass_<N>.json
  3. Stops when two consecutive passes both find zero issues
     OR when issues are unchanged between passes (=> we cannot fix them automatically)
     OR after a hard cap of MAX_PASSES.

The loop only RUNS the auditor. Fixes between passes are applied by the
agent driving the loop (because some fixes are semantic and need
judgement).  The agent re-invokes this script after each fix.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/user/workspace/RiceBaCI-GEE")
MAX_PASSES = 20


def find_pass_files():
    return sorted(ROOT.glob("audit_pass_*.json"),
                  key=lambda p: int(p.stem.split("_")[-1]))


def next_pass_number():
    existing = find_pass_files()
    if not existing:
        return 1
    return int(existing[-1].stem.split("_")[-1]) + 1


def run_one_pass(n):
    out_path = ROOT / f"audit_pass_{n:02d}.json"
    rc = subprocess.call(
        ["python3", "scripts/audit_manuscript.py",
         "--brief", "--out", str(out_path)],
        cwd=str(ROOT),
    )
    return out_path, rc


def summarise(report_path):
    r = json.loads(report_path.read_text())
    s = {"total": r["total_issues"]}
    for k, v in r["categories"].items():
        s[k] = v["count"]
    return s


def diff_signatures(prev, curr):
    """Return list of issues present in curr but not prev (by structural key)."""
    def key(i):
        return json.dumps({k: i.get(k) for k in ["file", "line", "match",
                                                 "check", "missing"]},
                          sort_keys=True)
    prev_keys = {key(i) for blk in prev["categories"].values() for i in blk["issues"]}
    curr_keys = {key(i) for blk in curr["categories"].values() for i in blk["issues"]}
    return {"new": list(curr_keys - prev_keys),
            "fixed": list(prev_keys - curr_keys),
            "carried": list(prev_keys & curr_keys)}


def main():
    n = next_pass_number()
    print(f"=== Audit pass {n:02d} ===")
    out, rc = run_one_pass(n)
    summary = summarise(out)
    print(f"  total_issues: {summary['total']}")
    for k, v in summary.items():
        if k == "total":
            continue
        print(f"    {k}: {v}")

    # if a previous pass exists, show the diff
    prevs = [p for p in find_pass_files() if p != out]
    if prevs:
        prev = json.loads(prevs[-1].read_text())
        curr = json.loads(out.read_text())
        d = diff_signatures(prev, curr)
        print(f"\n  vs previous pass ({prevs[-1].name}):")
        print(f"    fixed: {len(d['fixed'])}  carried: {len(d['carried'])}  new: {len(d['new'])}")

    print(f"\nReport: {out}")
    return 0 if summary["total"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

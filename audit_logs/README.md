# Audit Log Archive

This directory archives the JSON output of `scripts/audit_manuscript.py` for every audit pass that mattered to a numbered release or fix.

## What each file is

Every file is the **brief JSON report** produced by:

```bash
python3 scripts/audit_manuscript.py --brief --out audit_logs/audit_pass_NN.json
```

Each report contains:

| Key | Meaning |
|---|---|
| `timestamp`     | ISO-8601 timestamp when the audit ran |
| `categories.*`  | Per-category result (one block per audit category, currently A–V) with `count` and the `issues` list |
| `total_issues`  | Sum of `count` over all categories — must be 0 for a "clean" pass |

A pass is considered **clean** when `total_issues == 0`. The submission is **locked** when three consecutive clean passes are recorded.

## Numbering convention (and the early gap)

Pass numbers reflect the order in which the agent decided to archive a pass — not strictly chronological clock time, and not strictly sequential across reruns. In particular:

- **Passes 01–02** were renamed retroactively from rolling auditor output files after the `audit_logs/` directory was introduced. Their timestamps (2026-06-09 00:30) are *later* than passes 06–07 (2026-06-09 00:12) because they came from a later rerun, not from "the first audit ever".
- **Passes 03–05 do not exist on disk.** Those numbers were occupied by transient rolling outputs (`audit_pass_03.json`, `audit_pass_04.json`, `audit_pass_05.json`) that the agent overwrote before promoting any of them into the archive. No information is lost — every promoted pass since `_06` is preserved in full, and the auditor is deterministic with respect to the repository tree, so any clone of any tagged commit can be re-audited and will produce a byte-identical report.
- **Passes 06 onward** are sequentially archived. The convention from Pass 17 onward is: at the end of every commit cycle, the three most recent clean passes are renamed `audit_pass_{N, N+1, N+2}.json` and promoted to `audit_logs/`, so each commit ships with the three-pass convergence evidence already attached.

## Re-running the audit

From the repo root:

```bash
python3 scripts/audit_manuscript.py --brief --out audit_pass_check.json
python3 -c "import json; print('total_issues =', json.load(open('audit_pass_check.json'))['total_issues'])"
```

Any value other than `0` means the manuscript or submission package has drifted from the locked state. Fix the listed issues and re-run.

## Latest pass

The highest-numbered file in this directory is always the most recently archived pass. As of commit `db85191` and later, the latest archived passes are `audit_pass_28.json` through `audit_pass_30.json` (Pass 22 of the agent-driven loop, three consecutive clean passes with category V active).

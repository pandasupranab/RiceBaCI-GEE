"""Cross-reference audit: manuscript_text.md ↔ Supplement_v0.3.0.docx.

For each supplement target (Notes S1-S3, Tables S1-S9, Figures S1-S2, Fig 1B),
check that the manuscript references it at least once. Conversely, for every
"Sx" / "Table Sx" / "Figure Sx" reference in the manuscript, check it resolves
to an actual supplement section.

Outputs:
  manuscript/audit/xref_audit.md   — human-readable report
  manuscript/audit/xref_audit.csv  — machine-readable matrix
"""
from __future__ import annotations
import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path("/home/user/workspace/RiceBaCI-GEE")
MS_PATH = ROOT / "manuscript/manuscript_text.md"
AUDIT_DIR = ROOT / "manuscript/audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

# Targets that exist in the supplement
SUPPL_TARGETS = [
    # (canonical_id, label, kind)
    ("S1",      "Note S1 — Bulbul transferability",        "note"),
    ("S2",      "Note S2 — Cyclone climatology",           "note"),
    ("S3",      "Note S3 — Backscatter signatures",        "note"),
    ("Table S1", "Static TWFE-DiD",                        "table"),
    ("Table S2", "Pre-trends",                             "table"),
    ("Table S3", "Bulbul transferability residuals",       "table"),
    ("Table S4", "Wild-cluster bootstrap",                 "table"),
    ("Table S5", "Jackknife LOO",                          "table"),
    ("Table S6", "MDE / power",                            "table"),
    ("Table S7", "Placebo / falsification",                "table"),
    ("Table S8", "Cyclone climatology",                    "table"),
    ("Table S9", "Backscatter features",                   "table"),
    ("Figure S1", "Cyclone climatology fig",               "figure"),
    ("Figure S2", "Backscatter signatures fig",            "figure"),
    ("Figure 1B", "Identification DAG (panel B)",          "figure"),
]

# Compile flexible matching patterns (case-insensitive, allow "Fig.", "Fig", "Figure")
def make_patterns(canonical: str):
    """Generate regex patterns that catch realistic citation forms."""
    if canonical.startswith("Note "):
        # "Note Sx", "see Note Sx", "Supplementary Note Sx"
        sid = canonical.replace("Note ", "")
        return [
            rf"\b(?:Supplementary\s+)?Note\s+{sid}\b",
            rf"\bSI\s+Note\s+{sid}\b",
        ]
    if canonical.startswith("Table "):
        sid = canonical.replace("Table ", "")
        return [
            rf"\bTable\s+{sid}\b",
            rf"\bTab\.\s*{sid}\b",
            rf"\bSupplementary\s+Table\s+{sid}\b",
        ]
    if canonical.startswith("Figure "):
        sid = canonical.replace("Figure ", "")
        return [
            rf"\bFigure\s+{sid}\b",
            rf"\bFig\.\s*{sid}\b",
            rf"\bFig\s+{sid}\b",
            rf"\bSupplementary\s+Figure\s+{sid}\b",
        ]
    # bare "Sx" mentions (e.g. "see S1") — only match Notes
    if re.fullmatch(r"S\d+", canonical):
        return [rf"\b{canonical}\b"]
    return [rf"\b{re.escape(canonical)}\b"]


# --- read manuscript ---
text = MS_PATH.read_text(encoding="utf-8")
n_words = len(text.split())
print(f"[audit] manuscript_text.md: {len(text):,} chars, {n_words:,} words")

# --- forward audit: each supplement target → count mentions ---
forward = []
for canonical, label, kind in SUPPL_TARGETS:
    if kind == "note":
        target_lookup = f"Note {canonical}"
    else:
        target_lookup = canonical
    patterns = make_patterns(target_lookup)
    matches = []
    for pat in patterns:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            matches.append((m.start(), m.group(0)))
    matches = sorted(set(matches))
    forward.append({
        "id": canonical,
        "kind": kind,
        "label": label,
        "n_mentions": len(matches),
        "first_offset": matches[0][0] if matches else None,
        "first_match": matches[0][1] if matches else None,
    })

# --- reverse audit: every "Table Sx" / "Figure Sx" / "Note Sx" / "Fig Sx" in
# manuscript → does it resolve to a real supplement section? ---
ms_refs = []
ref_patterns = [
    (r"\bSupplementary\s+Note\s+(S\d+)\b", "note"),
    (r"\bNote\s+(S\d+)\b",                  "note"),
    (r"\bSupplementary\s+Table\s+(S\d+)\b", "table"),
    (r"\bTable\s+(S\d+)\b",                 "table"),
    (r"\bSupplementary\s+Figure\s+(S\d+)\b", "figure"),
    (r"\bFigure\s+(S\d+)\b",                "figure"),
    (r"\bFig\.\s*(S\d+)\b",                 "figure"),
    (r"\bFig\s+(S\d+)\b",                   "figure"),
]
seen = set()
for pat, kind in ref_patterns:
    for m in re.finditer(pat, text, flags=re.IGNORECASE):
        sid = m.group(1).upper()
        key = (kind, sid, m.start())
        if key in seen:
            continue
        seen.add(key)
        ms_refs.append({
            "kind": kind,
            "id": sid,
            "offset": m.start(),
            "match": m.group(0),
        })

# Build lookup of valid supplement IDs
valid = {("note", t[0]) for t in SUPPL_TARGETS if t[2] == "note"}
valid |= {("table", t[0].replace("Table ", "")) for t in SUPPL_TARGETS if t[2] == "table"}
valid |= {("figure", t[0].replace("Figure ", "")) for t in SUPPL_TARGETS if t[2] == "figure"}

unresolved = []
for r in ms_refs:
    if (r["kind"], r["id"]) not in valid:
        unresolved.append(r)

# --- write CSV ---
csv_path = AUDIT_DIR / "xref_audit.csv"
with csv_path.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["target_id", "kind", "label", "n_mentions",
                "first_offset", "first_match", "status"])
    for row in forward:
        status = "ok" if row["n_mentions"] >= 1 else "MISSING"
        w.writerow([row["id"], row["kind"], row["label"],
                    row["n_mentions"], row["first_offset"] or "",
                    row["first_match"] or "", status])

# --- write Markdown report ---
md_path = AUDIT_DIR / "xref_audit.md"
lines = []
lines.append("# Manuscript ↔ supplement cross-reference audit")
lines.append("")
lines.append(f"- Manuscript: `manuscript/manuscript_text.md`")
lines.append(f"- Supplement: `manuscript/supplement/Supplement_v0.3.0.docx`")
lines.append(f"- Manuscript size: **{n_words:,} words** ({len(text):,} chars)")
lines.append(f"- Supplement targets audited: **{len(SUPPL_TARGETS)}**")
lines.append("")

# Forward section
n_ok = sum(1 for r in forward if r["n_mentions"] >= 1)
n_missing = sum(1 for r in forward if r["n_mentions"] == 0)
lines.append("## 1. Forward audit — every supplement target referenced in manuscript?")
lines.append("")
lines.append(f"**{n_ok}/{len(forward)}** supplement targets are referenced.")
lines.append(f"**{n_missing}** missing.")
lines.append("")
lines.append("| Target | Kind | Mentions | Status | First match |")
lines.append("|--------|------|---------:|--------|-------------|")
for row in forward:
    status = "✅" if row["n_mentions"] >= 1 else "❌ MISSING"
    fm = (row["first_match"] or "—").replace("|", "\\|")
    lines.append(f"| {row['id']} | {row['kind']} | {row['n_mentions']} | {status} | {fm} |")
lines.append("")

# Missing detail
if n_missing:
    lines.append("### Missing references")
    lines.append("")
    for row in forward:
        if row["n_mentions"] == 0:
            lines.append(f"- **{row['id']}** ({row['label']}) — not cited anywhere in manuscript_text.md")
    lines.append("")

# Reverse section
lines.append("## 2. Reverse audit — every manuscript reference resolves?")
lines.append("")
lines.append(f"**{len(ms_refs)}** total Sx-style references found in manuscript.")
lines.append(f"**{len(unresolved)}** unresolved (target does not exist in supplement).")
lines.append("")
if unresolved:
    lines.append("### Unresolved references")
    lines.append("")
    lines.append("| Match | Kind | ID | Offset |")
    lines.append("|-------|------|----|--------|")
    for r in unresolved:
        lines.append(f"| `{r['match']}` | {r['kind']} | {r['id']} | {r['offset']} |")
else:
    lines.append("All manuscript references resolve to a real supplement section.")
lines.append("")

# Density distribution
lines.append("## 3. Reference density")
lines.append("")
lines.append("Distribution of mentions per target (helps spot under-cited material):")
lines.append("")
buckets = defaultdict(list)
for row in forward:
    bucket = (
        "0 (missing)" if row["n_mentions"] == 0
        else "1 (minimum)" if row["n_mentions"] == 1
        else "2-3" if row["n_mentions"] <= 3
        else "4+"
    )
    buckets[bucket].append(row["id"])
for k in ["0 (missing)", "1 (minimum)", "2-3", "4+"]:
    items = buckets.get(k, [])
    lines.append(f"- **{k}**: {len(items)} target(s)" + (f" — {', '.join(items)}" if items else ""))
lines.append("")

lines.append("## 4. Verdict")
lines.append("")
if n_missing == 0 and not unresolved:
    lines.append("**PASS.** Every supplement target is referenced; every manuscript reference resolves.")
else:
    issues = []
    if n_missing:
        issues.append(f"{n_missing} supplement target(s) un-cited")
    if unresolved:
        issues.append(f"{len(unresolved)} dangling reference(s)")
    lines.append(f"**ATTENTION REQUIRED:** {' and '.join(issues)}.")
lines.append("")

md_path.write_text("\n".join(lines), encoding="utf-8")

# --- print summary to stdout ---
print(f"\n=== forward audit ===")
print(f"  {n_ok}/{len(forward)} targets referenced")
if n_missing:
    print(f"  MISSING:")
    for row in forward:
        if row["n_mentions"] == 0:
            print(f"    - {row['id']}: {row['label']}")
print(f"\n=== reverse audit ===")
print(f"  {len(ms_refs)} manuscript refs found")
print(f"  {len(unresolved)} unresolved")
if unresolved:
    for r in unresolved:
        print(f"    - {r['match']} (offset {r['offset']})")
print(f"\nWrote:")
print(f"  {md_path}")
print(f"  {csv_path}")

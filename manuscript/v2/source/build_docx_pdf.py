"""
Build Manuscript.docx + .pdf, Supplement_Combined.docx, Cover_Letter.docx,
Declarations.docx, Highlights.docx, and Figures_Bundle.pdf from current
MD/figure sources.

Assumes pandoc + soffice are on PATH.
"""
from __future__ import annotations
import os
import subprocess
import shutil
from pathlib import Path

ROOT = Path("/tmp/RiceBaCI-fresh/rse_v2")
OUT = ROOT / "docx"
OUT.mkdir(exist_ok=True)
FIGURES = ROOT / "figures"


def run(cmd, cwd=None):
    print(">>", " ".join(str(c) for c in cmd))
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        print("STDOUT:", r.stdout[-1000:])
        print("STDERR:", r.stderr[-1500:])
        raise RuntimeError(f"command failed: {cmd}")
    return r


# ---------------------------------------------------------------------------
# 1. Build Manuscript.md (concatenate text + table captions + figure captions + references)
# ---------------------------------------------------------------------------
manuscript_parts = [
    ROOT / "manuscript_text.md",
    ROOT / "table_captions.md",
    ROOT / "figure_captions.md",
    ROOT / "references.md",
]
combined_ms = ROOT / "_combined_manuscript.md"
with combined_ms.open("w", encoding="utf-8") as out:
    for p in manuscript_parts:
        out.write(p.read_text(encoding="utf-8"))
        out.write("\n\n---\n\n")

# Manuscript DOCX
run(["pandoc", str(combined_ms), "-o", str(OUT / "Manuscript.docx"),
     "--standalone", "--reference-links",
     "-V", "geometry:margin=1in", "-V", "fontsize=11pt",
     "-V", "linestretch=1.5"])

# Manuscript PDF (LibreOffice from DOCX)
run(["soffice", "--headless", "--convert-to", "pdf",
     "--outdir", str(OUT), str(OUT / "Manuscript.docx")])

# ---------------------------------------------------------------------------
# 2. Supplement_Combined
# ---------------------------------------------------------------------------
run(["pandoc", str(ROOT / "supplement.md"), "-o", str(OUT / "Supplement_Combined.docx"),
     "--standalone", "-V", "geometry:margin=1in"])
run(["soffice", "--headless", "--convert-to", "pdf",
     "--outdir", str(OUT), str(OUT / "Supplement_Combined.docx")])

# ---------------------------------------------------------------------------
# 3. Cover_Letter
# ---------------------------------------------------------------------------
run(["pandoc", str(ROOT / "cover_letter.md"), "-o", str(OUT / "Cover_Letter.docx"),
     "--standalone", "-V", "geometry:margin=1in"])
run(["soffice", "--headless", "--convert-to", "pdf",
     "--outdir", str(OUT), str(OUT / "Cover_Letter.docx")])

# ---------------------------------------------------------------------------
# 4. Declarations
# ---------------------------------------------------------------------------
run(["pandoc", str(ROOT / "declarations.md"), "-o", str(OUT / "Declarations.docx"),
     "--standalone", "-V", "geometry:margin=1in"])

# ---------------------------------------------------------------------------
# 5. Highlights
# ---------------------------------------------------------------------------
run(["pandoc", str(ROOT / "highlights.md"), "-o", str(OUT / "Highlights.docx"),
     "--standalone", "-V", "geometry:margin=1in"])
run(["soffice", "--headless", "--convert-to", "pdf",
     "--outdir", str(OUT), str(OUT / "Highlights.docx")])

# ---------------------------------------------------------------------------
# 6. Figures_Bundle.pdf (merge all figure PDFs)
# ---------------------------------------------------------------------------
from pypdf import PdfWriter, PdfReader

fig_order = [
    "fig1_study_area.pdf",
    "fig2_qc_distributions.pdf",
    "fig3_did_coefplot.pdf",
    "fig4_event_study.pdf",
    "fig5_qc_framework.pdf",
    "fig6_district_sos_panel.pdf",
    "fig7_event_study.pdf",
    "figS1_cyclone_climatology.pdf",
    "figS2_identification_dag.pdf",
]
writer = PdfWriter()
for name in fig_order:
    path = FIGURES / name
    if not path.exists():
        print(f"WARN: missing figure {path}")
        continue
    reader = PdfReader(str(path))
    for page in reader.pages:
        writer.add_page(page)
writer.add_metadata({
    "/Title": "Figures bundle — RSE QC-framework manuscript",
    "/Author": "Perplexity Computer",
})
with (OUT / "Figures_Bundle.pdf").open("wb") as f:
    writer.write(f)
print(f"Wrote {OUT / 'Figures_Bundle.pdf'}  ({len(writer.pages)} pages)")

print("\nAll DOCX/PDF artefacts built.")

"""Build Cover_Letter.docx + Cover_Letter.pdf from 00_cover_letter.md.

Same styling as Manuscript.docx: Arial Pt(10) body, A4, 2.5cm margins.
"""
import subprocess
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_LINE_SPACING

ROOT = Path("/home/user/workspace/RiceBaCI-GEE/manuscript")
MD = ROOT / "00_cover_letter.md"
DOCX = ROOT / "Cover_Letter.docx"
PDF = ROOT / "Cover_Letter.pdf"

# 1. md -> docx via pandoc
subprocess.check_call([
    "pandoc", str(MD),
    "-f", "markdown+pipe_tables",
    "-t", "docx",
    "-o", str(DOCX),
])

# 2. Patch fonts + spacing
doc = Document(str(DOCX))

for section in doc.sections:
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = section.right_margin = Cm(2.5)
    section.top_margin = section.bottom_margin = Cm(2.5)

styles = doc.styles
normal = styles['Normal']
normal.font.name = 'Arial'
normal.font.size = Pt(10)
normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
normal.paragraph_format.space_after = Pt(6)

for style_name in ['Heading 1', 'Heading 2', 'Heading 3']:
    try:
        s = styles[style_name]
        s.font.name = 'Arial'
        s.font.size = Pt(11)
        s.font.bold = True
    except KeyError:
        pass

# Force Arial on every run
for para in doc.paragraphs:
    for run in para.runs:
        run.font.name = 'Arial'
        if not run.font.size:
            run.font.size = Pt(10)

doc.save(str(DOCX))
print(f"Wrote {DOCX} ({DOCX.stat().st_size} bytes)")

# 3. docx -> pdf via libreoffice
subprocess.check_call([
    "libreoffice", "--headless", "--convert-to", "pdf",
    "--outdir", str(ROOT), str(DOCX)
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"Wrote {PDF} ({PDF.stat().st_size} bytes)")

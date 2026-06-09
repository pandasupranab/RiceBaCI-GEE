#!/usr/bin/env python3
"""Embed figure PNGs into manuscript/Manuscript.docx inline at their textual callouts.

Pandoc renders the source manuscript_text.md without embedding figures because
the source has no Markdown ![](path) image syntax — figures are referenced by
caption text only ("Figure 1", "Figure 2", ...). This script post-processes
the pandoc output so every figure appears inline in the rendered DOCX.

Strategy:
  - For each figure file in figures/, locate the first paragraph whose text
    contains the matching callout (e.g. "Figure 1.", "Figure 2.").
  - Insert a new paragraph with the image AFTER the callout-bearing paragraph.
  - Image width = 6.0 in (RSE standard one-column width).

Usage:
    python3 scripts/embed_manuscript_figures.py
"""
from pathlib import Path
import re
import sys

from docx import Document
from docx.shared import Inches, Pt
from docx.oxml.ns import qn
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "manuscript" / "Manuscript.docx"
FIGDIR = ROOT / "figures"

# Single source of truth for figure captions: import the FIGURES list that
# scripts/build_figures_bundle.py uses for Figures_Bundle.docx. This guarantees
# the inline manuscript figures and the stand-alone Figures Bundle carry
# identical labels and caption text, and that any Pass 21-style caption fix
# automatically propagates to both outputs.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_figures_bundle import FIGURES as BUNDLE_FIGURES  # noqa: E402

_BUNDLE_CAPTIONS = {fname: (label, caption)
                    for label, fname, caption in BUNDLE_FIGURES}

# Map of figure number → (file, search regex for callout sentence)
# Each entry: figure-name, file, callout regex.
# Regex picks the *first* paragraph containing this callout in normal manuscript prose;
# Figure 1 is the umbrella callout (Figure 1) and 1A/1B are matched by their explicit subletters.
FIGURES = [
    ("Figure 1",   FIGDIR / "figure1_study_area.png",
     re.compile(r"\(Figure\s+1\)")),
    ("Figure 1B",  FIGDIR / "fig1b_identification_dag.png",
     re.compile(r"Figure\s+1B")),
    ("Figure 2",   FIGDIR / "fig2_did_coefplot.png",
     re.compile(r"\(Figure\s+2\)")),
    ("Figure 3",   FIGDIR / "fig3_event_study.png",
     re.compile(r"in\s+Figure\s+3\b")),
    ("Figure 4",   FIGDIR / "fig4_district_sos_panel.png",
     re.compile(r"plotted\s+in\s+Figure\s+4\b")),
    ("Figure 5",   FIGDIR / "fig5_power_curves.png",
     re.compile(r"reported\s+in\s+Figure\s+5\b")),
    ("Figure 6",   FIGDIR / "fig6_placebo_distribution.png",
     re.compile(r"Table\s+S7,\s+Figure\s+6")),
]


def insert_paragraph_after(paragraph, doc):
    """Create a new empty paragraph immediately after `paragraph` and return it."""
    new_p = deepcopy(paragraph._p)  # clone for namespacing
    # strip its content
    for child in list(new_p):
        new_p.remove(child)
    paragraph._p.addnext(new_p)
    # wrap in python-docx Paragraph
    from docx.text.paragraph import Paragraph
    return Paragraph(new_p, paragraph._parent)


def main():
    if not DOCX.exists():
        print(f"FAIL: {DOCX} does not exist")
        raise SystemExit(1)

    doc = Document(str(DOCX))

    embedded = []
    missing = []

    # snapshot paragraphs since we'll mutate
    paragraphs = list(doc.paragraphs)

    for fig_name, fig_path, callout_re in FIGURES:
        if not fig_path.exists():
            missing.append((fig_name, fig_path))
            continue
        # find first paragraph whose text matches the callout
        target_idx = None
        for i, p in enumerate(paragraphs):
            if callout_re.search(p.text):
                target_idx = i
                break
        if target_idx is None:
            missing.append((fig_name, fig_path, "callout sentence not found in manuscript"))
            continue
        # Re-locate by traversing current doc paragraphs (paragraphs list may be stale after inserts)
        live_paragraphs = list(doc.paragraphs)
        live_target = None
        match_count = 0
        for p in live_paragraphs:
            if callout_re.search(p.text):
                match_count += 1
                if match_count == 1:  # first occurrence
                    live_target = p
                    break
        if live_target is None:
            missing.append((fig_name, fig_path, "callout sentence vanished after edits"))
            continue
        # create new paragraph after the callout and add image
        img_p = insert_paragraph_after(live_target, doc)
        run = img_p.add_run()
        run.add_picture(str(fig_path), width=Inches(6.0))
        img_p.alignment = 1  # WD_ALIGN_PARAGRAPH.CENTER

        # Insert caption paragraph immediately after the image so the reader
        # sees "Figure N. <caption text>" below every embedded figure. Pull
        # the caption from the bundle builder's FIGURES table so the inline
        # manuscript caption is identical to the Figures Bundle caption.
        label_caption = _BUNDLE_CAPTIONS.get(fig_path.name)
        if label_caption is not None:
            label, caption_text = label_caption
            cap_p = insert_paragraph_after(img_p, doc)
            cap_p.alignment = 0  # WD_ALIGN_PARAGRAPH.LEFT
            label_run = cap_p.add_run(f"{label}. ")
            label_run.bold = True
            label_run.font.size = Pt(10)
            text_run = cap_p.add_run(caption_text)
            text_run.font.size = Pt(10)
        else:
            print(f"  WARN: no bundle caption found for {fig_path.name} "
                  f"(figure embedded without caption)")

        embedded.append(fig_name)
        print(f"  OK: embedded {fig_name} ({fig_path.name}) after first callout")

    doc.save(str(DOCX))
    print()
    print(f"Embedded {len(embedded)} figures in {DOCX.relative_to(ROOT)}")
    if missing:
        print(f"WARNING: {len(missing)} figures NOT embedded:")
        for m in missing:
            print(f"   {m}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()

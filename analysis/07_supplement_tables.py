"""
07_supplement_tables.py — generate journal-ready supplementary tables.

Outputs (manuscript/supplement/):
    Table_S1_did_static.docx        — full coefficient table (DiD ATT)
    Table_S2_pretrends.docx         — pre-period interaction tests
    Table_S3_bulbul_transferability.docx — Bulbul transferability probe stub
    Table_S1_S3_combined.csv        — machine-readable consolidation

The DOCX path is intentional — Elsevier and Frontiers both accept it
directly without conversion.

Author: Supranab Panda
Date  : 2026-05-05
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


# ---------------------------------------------------------------------------
def _set_table_style(table, font_size: int = 10):
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(font_size)
                    run.font.name = "Arial"


def _style_header(row):
    for cell in row.cells:
        for p in cell.paragraphs:
            for run in p.runs:
                run.bold = True


def _add_caption(doc: Document, text: str):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(10)
    run.font.name = "Arial"


# ---------------------------------------------------------------------------
def table_s1_did_static(static_df: pd.DataFrame, out_path: Path) -> None:
    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Arial"
    style.font.size = Pt(10)

    _add_caption(doc,
                 "Table S1.  Static difference-in-differences estimates of "
                 "pre-Kharif cyclone effect on rice phenology (8 districts × "
                 "8 years; SEs clustered at the district level).")

    cols = ["pipeline", "metric", "n_obs", "n_districts",
            "tau_days", "se_days", "t_stat", "p_value",
            "ci_lo_95", "ci_hi_95", "r2_within"]

    table = doc.add_table(rows=1, cols=len(cols))
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    for i, c in enumerate(cols):
        hdr[i].text = {
            "pipeline":    "Pipeline",
            "metric":      "Metric",
            "n_obs":       "N obs",
            "n_districts": "N dist.",
            "tau_days":    "τ (d)",
            "se_days":     "SE",
            "t_stat":      "t",
            "p_value":     "p",
            "ci_lo_95":    "CI₂.₅",
            "ci_hi_95":    "CI₉₇.₅",
            "r2_within":   "R²ᵥᵥ",
        }[c]
    _style_header(table.rows[0])

    for _, r in static_df.iterrows():
        row = table.add_row().cells
        for i, c in enumerate(cols):
            v = r[c]
            if isinstance(v, float):
                row[i].text = f"{v:+.3f}" if c == "tau_days" else f"{v:.3f}"
            else:
                row[i].text = str(v)
    _set_table_style(table)

    doc.add_paragraph()
    note = doc.add_paragraph()
    note.add_run(
        "Notes. τ is the average treatment effect on the treated, in days "
        "of phenology shift. *** p<0.001; ** p<0.01; * p<0.05. "
        "R²ᵥᵥ is the partial within-R² of the DiD term after absorbing "
        "district and year fixed effects. Treatment cohort: coastal-treatment "
        "districts (Baleshwar, Bhadrak, Kendrapara, Jagatsinghpur, Puri) × "
        "cyclone years 2019, 2020, 2021. Bulbul (2019, post-monsoon, "
        "outside the study area) and Hudhud (2014) are excluded as "
        "transferability hold-outs."
    ).font.size = Pt(9)

    doc.save(out_path)


# ---------------------------------------------------------------------------
def table_s2_pretrends(pre_df: pd.DataFrame, out_path: Path) -> None:
    doc = Document()
    style = doc.styles["Normal"]; style.font.name = "Arial"; style.font.size = Pt(10)

    _add_caption(doc,
                 "Table S2.  Parallel-trends test: regression of phenology "
                 "metric on year × treat interaction in pre-treatment period "
                 "(years < 2019). A non-significant coefficient supports the "
                 "DiD identifying assumption.")

    cols = ["pipeline", "metric", "interaction_coef", "se", "p_value",
            "n_pre", "note"]
    table = doc.add_table(rows=1, cols=len(cols))
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    labels = ["Pipeline", "Metric", "β (year×treat)", "SE", "p",
              "N pre", "Verdict"]
    for i, lab in enumerate(labels):
        hdr[i].text = lab
    _style_header(table.rows[0])

    for _, r in pre_df.iterrows():
        row = table.add_row().cells
        row[0].text = str(r["pipeline"])
        row[1].text = str(r["metric"])
        row[2].text = f"{r['interaction_coef']:+.3f}"
        row[3].text = f"{r['se']:.3f}"
        row[4].text = f"{r['p_value']:.4f}"
        row[5].text = str(int(r["n_pre"]))
        row[6].text = str(r["note"])
    _set_table_style(table)

    doc.save(out_path)


# ---------------------------------------------------------------------------
def table_s3_bulbul_stub(out_path: Path) -> None:
    """Stub table — populated after Module 05b transferability run."""
    doc = Document()
    style = doc.styles["Normal"]; style.font.name = "Arial"; style.font.size = Pt(10)

    _add_caption(doc,
                 "Table S3.  Bulbul (Nov 2019) transferability probe: "
                 "out-of-sample prediction of inland Bulbul-affected districts' "
                 "SOS using coefficients trained on Fani / Amphan / Yaas. "
                 "[Populated by Module 05b after main DiD is locked.]")

    cols = ["district", "predicted_SOS_shift_d", "observed_SOS_shift_d",
            "residual_d", "within_95pct_PI"]
    table = doc.add_table(rows=1, cols=len(cols))
    table.style = "Light Grid Accent 1"
    hdr_labels = ["District", "Predicted ΔSOS (d)", "Observed ΔSOS (d)",
                  "Residual (d)", "Inside 95% PI?"]
    for i, lab in enumerate(hdr_labels):
        table.rows[0].cells[i].text = lab
    _style_header(table.rows[0])

    # Placeholder rows for the 8 districts so reviewers see the shape
    placeholders = [
        ("Baleshwar",     "—", "—", "—", "—"),
        ("Bhadrak",       "—", "—", "—", "—"),
        ("Kendrapara",    "—", "—", "—", "—"),
        ("Jagatsinghpur", "—", "—", "—", "—"),
        ("Puri",          "—", "—", "—", "—"),
        ("Dhenkanal",     "—", "—", "—", "—"),
        ("Anugul",        "—", "—", "—", "—"),
        ("Cuttack",       "—", "—", "—", "—"),
    ]
    for vals in placeholders:
        row = table.add_row().cells
        for i, v in enumerate(vals):
            row[i].text = v
    _set_table_style(table)

    doc.add_paragraph()
    note = doc.add_paragraph()
    note.add_run(
        "Notes. Awaiting Module 05b (transferability) execution. "
        "Prediction uses the corrected-pipeline DiD coefficients from "
        "Table S1 to forecast Bulbul-induced SOS shift; observed shift "
        "is computed from the corrected phenology pipeline applied to "
        "Bulbul (Nov 2019). Residuals centred near zero (and within the "
        "95% prediction interval) indicate the trained model generalises "
        "to a different cyclone class (post-monsoon, rainfall-dominant) "
        "outside the study area."
    ).font.size = Pt(9)

    doc.save(out_path)


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="analysis/results")
    ap.add_argument("--outdir",  default="manuscript/supplement")
    args = ap.parse_args()

    res_dir = Path(args.results)
    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    static_df = pd.read_csv(res_dir / "did_static.csv")
    pre_df    = pd.read_csv(res_dir / "parallel_trends.csv")

    table_s1_did_static(static_df, out_dir / "Table_S1_did_static.docx")
    table_s2_pretrends (pre_df,    out_dir / "Table_S2_pretrends.docx")
    table_s3_bulbul_stub(           out_dir / "Table_S3_bulbul_transferability.docx")

    # Also write a consolidated CSV for the GitHub release attachment
    static_df.assign(table="S1").to_csv(
        out_dir / "Table_S1_did_static.csv", index=False
    )
    pre_df.assign(table="S2").to_csv(
        out_dir / "Table_S2_pretrends.csv", index=False
    )

    print(f"wrote: {out_dir}/Table_S1_did_static.docx")
    print(f"wrote: {out_dir}/Table_S2_pretrends.docx")
    print(f"wrote: {out_dir}/Table_S3_bulbul_transferability.docx")
    print(f"wrote: {out_dir}/Table_S1_did_static.csv")
    print(f"wrote: {out_dir}/Table_S2_pretrends.csv")


if __name__ == "__main__":
    main()

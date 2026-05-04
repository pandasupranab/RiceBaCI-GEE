# RiceBaCI-GEE — Submission Package

**Target journal:** Remote Sensing of Environment (Elsevier)
**Manuscript title:** Decoupling Cyclone-Induced Saline Inundation from Agronomic Flooding in Sentinel-1/2 Rice Phenology Retrieval: A Multi-Year Bay-of-Bengal Coastal Framework (2017–2024)
**Corresponding author:** Subranab Panda (pandasupranab@gmail.com)

---

## What is in this package

### 1. Manuscript files (upload to Editorial Manager in this order)
| File | Editorial-Manager item type |
|---|---|
| `manuscript/Cover_Letter.pdf` | Cover Letter |
| `manuscript/Highlights.docx` | Highlights |
| `manuscript/Manuscript.docx` | Manuscript |
| `manuscript/Graphical_Abstract_Concept.docx` | Graphical Abstract (concept brief) |
| `manuscript/Declarations.docx` | Declarations (CRediT, GenAI, conflicts, funding) |
| `assets/Fig01_*.png` … `Fig10_*.png` | Figures (one per upload) |

### 2. Reproducibility code
| Folder | Contents |
|---|---|
| `gee/` | 4 Google Earth Engine modules (JavaScript) |
| `analysis/` | R script for BACI mixed-effects model |
| `assets/render_figures.py` | Python figure rendering pipeline |

### 3. Supplementary documentation
| File | Purpose |
|---|---|
| `docs/Data_Sources_Manifest.md` | Complete manifest of every open dataset with download URLs |
| `docs/02_OSF_Pre_Registration.md` | Pre-registered hypotheses (deposit on OSF before running pipeline) |
| `docs/03_Access_Setup_Guide.md` | Account setup walkthrough (GEE, NICFI, IBTrACS, OSF, Mendeley Data) |
| `docs/04_Week_1_Action_Plan.md` | Mon–Sun execution checklist |
| `manuscript/03_submission_checklist.md` | Editorial Manager step-by-step submission guide |

---

## Critical: items the user must complete BEFORE submission

### A. Replace placeholders in source files
Search the project for `[PLACEHOLDER:`, `pandasupranab`, `[Co-author`, `[Supervisor`, `[Institution]`, `[Mendeley Data DOI: pending]`, `[your ORCID]`, `[ORCID placeholder]`, `[Affiliation placeholder]` and complete each.

### B. Run the GEE pipeline to obtain real numbers
1. Sign up for Google Earth Engine (https://earthengine.google.com/signup)
2. Upload IBTrACS cyclone tracks as a GEE asset, then update `users/PLACEHOLDER/ibtracs_NI_2017_2024` in modules 02 and 04
3. Execute modules 01 → 02 → 03 → 04 in order
4. Download exported CSVs to `data/`
5. Run `analysis/baci_mixed_effects.R` in RStudio
6. Replace every `[PLACEHOLDER: ...]` marker in `manuscript/manuscript_text.md` with the real values
7. Re-run `pandoc manuscript_text.md -t docx --reference-doc=... -o Manuscript.docx`

### C. Replace illustrative figures with real renderings
The current PNGs in `assets/` are produced by `render_figures.py` from synthetic data and carry an "ILLUSTRATIVE — REPLACE WITH REAL DATA" watermark. Re-run `render_figures.py` after the GEE+R pipeline completes, feeding it real outputs.

### D. Pre-register on OSF
Deposit `docs/02_OSF_Pre_Registration.md` on https://osf.io BEFORE running the full pipeline. This is a non-negotiable scientific integrity step — pre-registration must precede analysis.

### E. Deposit data on Mendeley Data
After pipeline completion, deposit the BACI export CSV on https://data.mendeley.com and substitute the resulting DOI everywhere `[Mendeley Data DOI: pending]` appears.

---

## Manuscript stats

| Metric | Value |
|---|---|
| Word count (manuscript body) | ~11,100 words |
| Sections | 17 (incl. Title Page, Abstract, Highlights, 1–6, References, Appendices) |
| Tables | 6 |
| Figures | 10 |
| References | 43 (Elsevier Harvard style) |
| `[PLACEHOLDER: ...]` markers remaining (all empirical, fill after GEE pipeline run) | 67 |

---

## Honest disclosure

This package was built as a **research scaffold** — every line of code is real and runnable, but Results and validation numbers are placeholders. Real numbers must come from running the GEE pipeline on the user's own GEE account; no legitimate journal will accept fabricated results, and none have been generated.

The illustrative figures should be regenerated from real data before submission. The manuscript text — Introduction, Methods, Discussion structure, references — is publication-ready and required only the actual measurement values to substitute into the placeholder markers.

---

## License

MIT (see `LICENSE`). Citations welcome via `CITATION.cff`.

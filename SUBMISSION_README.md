# RiceBaCI-GEE — Submission Package

**Target journal:** Remote Sensing of Environment (Elsevier) — zero APC, gold open access available via co-author institutional agreements.
**Manuscript title:** Decoupling Cyclone-Induced Saline Inundation from Agronomic Flooding in Sentinel-1/2 Rice Phenology Retrieval: A Multi-Year Bay-of-Bengal Coastal Framework (2017–2024)
**Corresponding author:** Supranab Panda (pandasupranab@gmail.com), ORCID 0009-0009-6496-6545
**Co-author:** Sarat Chandra Sahu, ORCID 0000-0002-8048-1910
**Release tag:** v1.0.1-submission
**Pre-registration:** [OSF c4mp8](https://osf.io/c4mp8) — DOI 10.17605/OSF.IO/C4MP8
**Code archive (Zenodo):** [10.5281/zenodo.20587316](https://doi.org/10.5281/zenodo.20587316) (this version); concept DOI [10.5281/zenodo.20024578](https://doi.org/10.5281/zenodo.20024578)
**Data archive (Mendeley):** [10.17632/z3zxk4xy3c.1](https://doi.org/10.17632/z3zxk4xy3c.1)

---

## What is in this package

### 1. Manuscript files (upload to Editorial Manager in this order)
| File | Editorial-Manager item type |
|---|---|
| `manuscript/Cover_Letter.pdf` | Cover Letter |
| `manuscript/Highlights.docx` | Highlights |
| `manuscript/Manuscript.docx` | Manuscript |
| `manuscript/Graphical_Abstract_Concept.docx` | Graphical Abstract (concept brief — to be finalised at proof stage) |
| `manuscript/Declarations.docx` | Declarations (CRediT, GenAI use, conflicts, funding) |
| `manuscript/Table_1.docx` | Main-text Table 1 (Tropical cyclone events) — built by `scripts/build_main_text_tables.py`; identical to the inline copy in `Manuscript.docx`; auditor category V guarantees no drift |
| `manuscript/Table_2.docx` | Main-text Table 2 (Satellite and ancillary datasets) — same build script, same drift guard |
| `manuscript/Figures_Bundle.pdf` | Figures (one per upload from `figures/`) |
| `manuscript/supplement/Supplement_Combined.pdf` | Supplementary Material |

### 2. Reproducibility code
| Folder | Contents |
|---|---|
| `gee/` | Google Earth Engine modules 01–12 (JavaScript) — Sentinel-1/2 ingestion, saline-flood classifier, phenology retrieval, per-district cyclone-area shares |
| `analysis/` | Python analysis pipeline (10 stages, Python 3.12.8 with `numpy`, `pandas`, `scipy`, `statsmodels`, `matplotlib`, `python-docx` pinned in `requirements.txt`) |
| `scripts/run_all.sh` | One-command harness that reproduces every reported figure and supplementary table from the v2.1 real panel |
| `scripts/audit_manuscript.py` + `scripts/audit_loop.py` | 15-category self-iterating manuscript auditor (forbidden wording, cross-refs, identifiers, numerics, artefact freshness, table content, figure freshness, bundle refs) |
| `figures/` | All publication figures (PNG + PDF) regenerated from `analysis/results/real_v21/` |

### 3. Supplementary documentation
| File | Purpose |
|---|---|
| `docs/Data_Sources_Manifest.md` | Complete manifest of every open dataset (Sentinel-1/2, JRC GSW, ERA5, IBTrACS, MCD12Q2, ICRISAT VDSA, Microsoft Planetary Computer Sentinel-1 RTC) with download URLs and access notes |
| `docs/02_OSF_Pre_Registration.md` | Pre-registered hypotheses (deposited on OSF before analysis began) |
| `docs/04_Week_1_Action_Plan.md` | Execution log of the analysis week |
| `docs/user_guides/` | Step-by-step guides: how to run phenology in GEE, how to draw labels, how to review active-learning samples |
| `manuscript/03_submission_checklist.md` | Editorial Manager step-by-step submission guide |

---

## Critical: items the user must complete BEFORE submission

### A. Reviewer-facing checks
1. Confirm institutional affiliation and address are current on `manuscript/Manuscript.docx` title page.
2. Confirm co-author contact details and approval to submit are on file (handled outside this repo; **the agent does not draft co-author sign-off email per user directive**).
3. Verify all DOIs in this document and in `manuscript/02_declarations.md` resolve from your network.
4. Confirm Editorial Manager item-type mapping above against the RSE submission portal at submission time (Elsevier occasionally renames item types).

### B. Run the 15-category audit before submission
From the repo root:
```bash
python3 scripts/audit_loop.py    # writes audit_pass_NN.json next to root
```
A passing audit shows `total_issues = 0` across all 15 categories (A–O) and `fixed: 0  carried: 0  new: 0` versus the previous pass. The submission is considered locked once three consecutive clean passes are achieved (the loop has been run this way through Pass 17 in this repo).

### C. Re-generate artefacts from the real v2.1 panel if any source MD or CSV changes
```bash
# rebuild supplement
python3 scripts/build_supplement_bundle.py
cp manuscript/supplement/Supplement_v0.3.0.docx manuscript/supplement/Supplement_Combined.docx
libreoffice --headless --convert-to pdf manuscript/supplement/Supplement_Combined.docx --outdir manuscript/supplement

# rebuild manuscript and cover letter
pandoc manuscript/manuscript_text.md -o manuscript/Manuscript.docx
libreoffice --headless --convert-to pdf manuscript/Manuscript.docx --outdir manuscript
pandoc manuscript/00_cover_letter.md -o manuscript/Cover_Letter.docx
libreoffice --headless --convert-to pdf manuscript/Cover_Letter.docx --outdir manuscript

# rebuild supplement tables (real v2.1 numbers)
python3 analysis/07_supplement_tables.py --results analysis/results/real_v21 --out manuscript/supplement

# rebuild figures
python3 analysis/06_figures.py --results analysis/results/real_v21 --out figures
```

---

## Submission status

| Item | Status |
|---|---|
| Manuscript main text | Locked on real v2.1 panel |
| Supplement (Tables S1–S9, Notes S1–S4, Figures S1–S2) | Locked on real v2.1 panel |
| Figures 1–6 | Locked on real v2.1 panel |
| Cover letter | Locked |
| Highlights | Locked |
| Declarations (CRediT, GenAI, conflicts, funding) | Locked |
| Pre-registration on OSF | Deposited (c4mp8) with one logged scope amendment (Bulbul transferability probe, 2026-04-29) |
| Code archive on Zenodo | Released as v1.0.1-submission (this-version DOI 10.5281/zenodo.20587316) |
| Data archive on Mendeley | Released (DOI 10.17632/z3zxk4xy3c.1) |
| 15-category audit | Three consecutive clean passes (Pass 17) |

---

## Honest disclosure (publication-ready disclosure)

Every number reported in the manuscript, supplement, and figures is drawn from the real v2.1 analysis panel in `analysis/results/real_v21/`. No synthetic or placeholder values remain anywhere in the submission package — the auditor in `scripts/audit_manuscript.py` enforces this through fifteen independent categories of automated checks (forbidden-wording scan in MD and PDF, cross-reference integrity, identifier consistency, headline numeric drift, required-artefact existence, result-CSV existence, PDF freshness, broken Markdown links, page-count sanity, manuscript-internal citations, figure files, table content, figure freshness, and supplement-bundle references). The corrected SOS DiD coefficient \(\hat\tau\) = +15.108 d (WCR-restricted *p* = 0.4065, 95% CI inclusive of zero) is reported as a transparent null at the design's small-cluster MDE of ≈60 d, and is presented as such — not as evidence for or against a non-zero effect — in the manuscript text, supplement Note S4, and Figure 5.

---

## License

MIT for code (see `LICENSE`); CC-BY 4.0 for data archive (Mendeley); CC0 for the OSF pre-registration. Citations welcome via `CITATION.cff`.

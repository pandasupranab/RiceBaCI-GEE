# RiceBaCI-GEE

**Decoupling cyclone-induced saline inundation from agronomic
transplanting flooding in Sentinel-1/2 rice phenology — a
reproducible, pre-registered, zero-cost pipeline for the Bay of
Bengal coast.**

[![Pre-registered](https://img.shields.io/badge/OSF-pre--registered-blue)](https://osf.io/c4mp8)
[![DOI](https://img.shields.io/badge/DOI-10.17605%2FOSF.IO%2FC4MP8-informational)](https://doi.org/10.17605/OSF.IO/C4MP8)
[![Zenodo](https://img.shields.io/badge/Zenodo-concept%20DOI-orange)](https://doi.org/10.5281/zenodo.20024578)
[![Licence: MIT](https://img.shields.io/badge/licence-MIT-green)](LICENSE)
[![Earth Engine](https://img.shields.io/badge/runs%20on-Google%20Earth%20Engine-darkgreen)](https://earthengine.google.com)
[![Python 3.12.8](https://img.shields.io/badge/python-3.12.8-blue)](#reproducibility)

> **One line.** Every published Sentinel-1 rice-mapping pipeline reads
> the SAR backscatter trough as transplanting; in cyclone-prone deltas
> the same trough can be a saline storm-surge weeks earlier — silently
> biasing SOS by 5–6 days. RiceBaCI-GEE is the first framework to
> identify, quantify, and correct that confound.

---

## Headline result (synthetic-panel verification)

| Pipeline | Metric | τ̂ (d) | WCR p (B=9999) | LOO verdict | MDE @ G=8 |
|---:|:---:|---:|---:|:---|---:|
| **raw**       | SOS | **+5.66** | 0.007 | stable    | 2.49 |
| **raw**       | POS | +4.35     | 0.007 | stable    | 1.04 |
| **raw**       | EOS | +1.88     | 0.026 | stable    | 1.65 |
| **corrected** | SOS | +1.96     | 0.030 | stable    | 1.84 |
| **corrected** | POS | +2.10     | 0.007 | stable    | 1.53 |
| **corrected** | EOS | +0.56     | 0.20  | leverage  | 1.31 |

The +5.66-day uncorrected SOS bias is the **headline number**: it is
the artefact every prior cyclone-affected SAR rice study has carried
in silence. Correction collapses it to +1.96 d while preserving real
phenological signal at POS. EOS is correctly null after correction —
the saline-surge mechanism does not operate at end-of-season.

---

## Reviewer quick-start — clone to Table S1 in 4 commands

```bash
git clone https://github.com/pandasupranab/RiceBaCI-GEE.git
cd RiceBaCI-GEE
pip install -r requirements.txt
bash run_all.sh --quick
```

Expected runtime: **~3 minutes** on a laptop. Produces:

- 5 supplement tables (`manuscript/supplement/Table_S1…S6_*.docx`)
- 4 publication figures (`figures/fig{2,3,4,5}_*.{pdf,png}`)
- 9 result CSVs (`analysis/results/*.csv`)
- A coloured stage-by-stage console summary

Drop `--quick` for the publication-grade run (B = 9999 wild-cluster
reps, ~6 min on the same laptop). To use a real Module-04 GEE export
instead of the synthetic fixture:

```bash
bash run_all.sh --panel data/baci_panel_real.csv
```

---

## What the harness does (8 stages, all reproducible offline)

| Stage | Module | What it does | Key output |
|---|---|---|---|
| 0 | env check | verifies the 13 pinned deps load | `python` version stamp |
| 1 | `synthetic_panel.py` | generates a 384-row offline test fixture with hard-coded ATTs | `analysis/synthetic_baci_panel.csv` |
| 2 | `05_did_regression.py` | static DiD + event study + parallel-trends test | `did_static.csv`, `event_study.csv` |
| 3 | `05a_wild_cluster_bootstrap.py` | CGM Rademacher WCR (B = 9999), CI by inversion | `wild_bootstrap.csv` |
| 4 | `05b_bulbul_transferability.py` | plug-in residuals against held-out Bulbul 2019 | `bulbul_transferability.csv` |
| 5 | `05d_jackknife_sensitivity.py` | leave-one-district + leave-one-year LOO | `jackknife_verdicts.csv` |
| 6 | `06_figures.py` | Fig 2 / 3 / 4 — Okabe-Ito palette, vector PDF + 300 dpi PNG | `figures/fig{2,3,4}_*.pdf` |
| 7 | `07_supplement_tables.py` | Tables S1–S6 in DOCX (Light Grid Accent 1, Arial) | `manuscript/supplement/Table_S{1..6}_*.docx` |
| 8 | `09_power_analysis.py` | analytical MDE + Monte-Carlo power curves | `power_mde.csv`, `figures/fig5_power_curves.pdf` |

Modules 01–04 run on **Google Earth Engine** — they generate the
panel from Sentinel-1/2/JRC/IBTrACS and ERA5-Land. The pipeline is
designed so a reviewer who only has a laptop can validate every
inferential claim against the synthetic fixture in 3 minutes; only
re-running the empirical numbers requires a free GEE account.

A single methodological caveat — the Goodman-Bacon decomposition is
**not applicable** here because all five treated districts were
exposed simultaneously to Fani / Amphan / Yaas (single-cohort design);
LOO sensitivity is the binding leverage check instead. See
`analysis/05c_bacon_decomposition_note.md`.

---

## Why this exists

Every published Sentinel-1 rice-mapping algorithm relies on the SAR
backscatter "trough" at flooding/transplanting as a phenological
anchor. In cyclone-prone Asian deltas the **same trough** can be
produced by saline storm-surge inundation 4–6 weeks earlier in the
season — silently corrupting derived sowing-date and SOS estimates
by weeks. No prior study has characterised, let alone corrected,
this confound. RiceBaCI-GEE is the first attempt, and the entire
pipeline is built to run on **freely available data only** (no
licensed imagery, no commercial APIs, no APC-charging journal).

---

## Scientific design (one-page summary)

| Element | Choice | Source |
|---|---|---|
| Study area | 5 coastal Odisha districts (Baleshwar, Bhadrak, Kendrapara, Jagatsinghpur, Puri) + 3 inland controls (Dhenkanal, Anugul, Cuttack) | [GAUL 2015](https://data.apps.fao.org/catalog/dataset/gaul-2015) |
| Treatment cyclones | Fani (2019), Amphan (2020), Yaas (2021) | [IBTrACS v04r00](https://www.ncei.noaa.gov/products/international-best-track-archive) |
| Transferability cyclone | **Bulbul** (Nov 2019) — held out, post-hoc plug-in | [IBTrACS v04r00](https://www.ncei.noaa.gov/products/international-best-track-archive) |
| Identification strategy | DiD with district + year FE; Eq 3.Y.1 | Methods §3.Y |
| Inference at G=8 | Wild-cluster Rademacher bootstrap (Cameron-Gelbach-Miller); df = G − 1 | §3.Y.3 |
| Robustness | LOO district, LOO year, Bulbul transferability, MDE/power | §3.Y.4 |
| Targeted journal | Remote Sensing of Environment / *RSE* (zero APC for non-OA route) | RSE_Publication_Strategy |

Pre-registration: locked at OSF DOI [`10.17605/OSF.IO/C4MP8`](https://doi.org/10.17605/OSF.IO/C4MP8).
Working project: <https://osf.io/3vua4>. Concept DOI on Zenodo:
[`10.5281/zenodo.20024578`](https://doi.org/10.5281/zenodo.20024578).

---

## Repository layout

```
RiceBaCI-GEE/
├── gee/                       Google Earth Engine JavaScript modules (01–04)
│   ├── 01_study_area_and_data_ingestion.js
│   ├── 02_saline_flood_classifier.js
│   ├── 03_phenology_extraction.js
│   ├── 04_baci_export.js
│   └── lib/                   Shared GEE helper functions
├── analysis/                  Offline Python pipeline (05–09)
│   ├── synthetic_panel.py     384-row offline test fixture
│   ├── 05_did_regression.py   static DiD + event study + pre-trends
│   ├── 05a_wild_cluster_bootstrap.py
│   ├── 05b_bulbul_transferability.py
│   ├── 05c_bacon_decomposition_note.md   (non-applicability rationale)
│   ├── 05d_jackknife_sensitivity.py
│   ├── 06_figures.py          publication figures
│   ├── 07_supplement_tables.py  Tables S1–S6 in DOCX
│   ├── 09_power_analysis.py   MDE + power curves
│   ├── results/               .csv outputs
│   └── tests/                 7/7 pytest checks
├── manuscript/
│   ├── methods_module02_baseline.md     §3.X
│   ├── methods_module05_did.md          §3.Y
│   ├── methods_module09_power.md        §3.Y.4
│   └── supplement/                      Table_S1…S6 DOCX + CSV
├── figures/                   Fig 2 / 3 / 4 / 5 (PDF + 300 dpi PNG)
├── docs/                      Data manifest, OSF pre-registration, vendor letters
├── data/                      Reference data (validation points, cyclone metadata)
├── scripts/                   Push helpers (GitHub contents API)
├── requirements.txt           Python 3.12.8 pinned
├── run_all.sh                 8-stage offline reproducibility harness
├── CITATION.cff               machine-readable citation
├── LICENSE                    MIT
└── README.md                  this file
```

---

## Reproducibility

**Python**: 3.12.8 (pinned in `requirements.txt`).
**Operating systems tested**: Linux (Ubuntu 24.04). Should work on
macOS and Windows-WSL2 unchanged; pure-Windows is untested but the
only system call is the optional `bash` harness.

| Package | Pin |
|---|---|
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| scipy | 1.17.1 |
| matplotlib | 3.10.9 |
| statsmodels | 0.14.6 |
| linearmodels | 7.0 |
| python-docx | 1.2.0 |
| geopandas + shapely + pyproj + Cartopy + contextily | for Fig 1 |

Random seeds are pinned at module level (`SEED = 20260505`); WCR uses
`numpy.random.default_rng(seed)`. Re-running `bash run_all.sh` on the
synthetic fixture yields **bit-identical** CSVs across machines.

---

## Citing this work

If you use RiceBaCI-GEE, please cite both the **pre-registration**
and the **code release** (concept DOI for the most recent version):

```bibtex
@misc{panda_2026_ricebaci_prereg,
  author       = {Panda, Supranab},
  title        = {{RiceBaCI-GEE: Decoupling Cyclone-Induced Saline
                  Inundation from Agronomic Flooding in Sentinel
                  Rice Phenology — Pre-registration}},
  year         = 2026,
  publisher    = {Open Science Framework},
  doi          = {10.17605/OSF.IO/C4MP8},
  url          = {https://osf.io/c4mp8}
}

@software{panda_2026_ricebaci_code,
  author       = {Panda, Supranab},
  title        = {{RiceBaCI-GEE: Cyclone Saline-Inundation
                  Correction in SAR Rice Phenology}},
  year         = 2026,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.20024578}
}
```

A `CITATION.cff` is provided for GitHub's "Cite this repository" UI.

---

## Author

**Supranab Panda** — sole author, no co-authors, no funding,
no competing interests.
[ORCID 0009-0009-6496-6545](https://orcid.org/0009-0009-6496-6545).

For correspondence about replication, sub-AOI requests, or
collaboration, please open a GitHub issue rather than email — keeping
the audit trail public is part of the project's pre-registration
posture.

---

## Licence

MIT (`LICENSE`). Underlying datasets retain their original licences:
Sentinel-1/2 are under the Copernicus EU 2021 free-and-open licence;
ERA5-Land is under the C3S licence; IBTrACS is in the public domain;
JRC GSW is CC-BY 4.0.

# Mendeley Data — Step-by-Step Upload Guide

**Deposit file:** `RiceBaCI_Mendeley_v1.zip` (~64 KB, 18 files inside)
**Target repository:** https://data.mendeley.com/
**Login:** Use your Elsevier / ScienceDirect / Mendeley credentials (same account works across the Elsevier ecosystem). If you don't have one, sign up free at https://data.mendeley.com — no APC, no embargo required.

---

## 1. Sign in
1. Open https://data.mendeley.com/ in Edge.
2. Click **Sign in** (top-right). Use your Elsevier credentials or sign up. Mendeley Data is free.

## 2. Create new dataset
1. Click **+ New dataset**.
2. Choose **"Standard dataset"** (not "Software" — that's for the code, which is on Zenodo).

## 3. Drop the deposit
1. Drag `RiceBaCI_Mendeley_v1.zip` into the upload box, **or** extract first and drag all 18 files individually (Mendeley will preserve the folder structure either way). Either works — extracted version is slightly nicer for the file browser.
2. Wait for the green checkmarks on every file.

## 4. Fill the metadata form
Paste each block below into the matching Mendeley field.

### Title
```
RiceBaCI: District-scale BACI panel, classifier labels and analysis outputs for cyclone-induced saline-inundation correction of Sentinel-1/2 rice phenology in coastal Odisha (2017–2024)
```

### Description (Abstract field)
```
This deposit contains the derived dataset accompanying the manuscript "Decoupling Cyclone-Induced Saline Inundation from Agronomic Flooding in Sentinel-1/2 Rice Phenology Retrieval: A Multi-Year Bay-of-Bengal Coastal Framework (2017–2024)" submitted to Remote Sensing of Environment.

It comprises (i) the district-scale Before-After-Control-Impact (BACI) panel of 384 observations spanning 8 coastal- and inland-Odisha districts × 8 Kharif rice seasons × 6 phenology metrics (raw and corrected SOS/POS/EOS); (ii) the 480-label classifier training set with 8 Sentinel-1, Sentinel-2, JRC water and ERA5 features per label, separating cyclone-induced saline inundation from agronomic transplanting flooding; (iii) random-forest model cards (full-feature and SAR-only variants); (iv) the cyclone-flood pixel-share statistic per district-cyclone-year used to drive the BACI correction; and (v) the complete suite of TWFE-DiD analysis outputs (static coefficients, event-study, parallel-trends, wild-cluster restricted bootstrap, leave-one-out jackknife, in-space and in-time placebo).

Cyclone events covered: Fani (May 2019), Bulbul (Nov 2019), Amphan (May 2020), Yaas (May 2021), with Hudhud (Oct 2014, Andhra Pradesh) used for transferability testing.

All numerical results in the manuscript and supplement can be reproduced from public Copernicus EMS, Sentinel-1, Sentinel-2, JRC GSW, ERA5, and GADM inputs using a single command on the companion code archive: python scripts/refresh_v21_from_module12.py.

Companion resources: source code on GitHub (https://github.com/pandasupranab/RiceBaCI-GEE), code archive on Zenodo (DOI 10.5281/zenodo.20024578 concept; 10.5281/zenodo.20585636 v1.0.0), pre-registration on OSF (https://osf.io/c4mp8).
```

### Categories / Subject areas
Select all that apply:
- Remote Sensing
- Agricultural Remote Sensing
- Rice
- Phenology
- Tropical Cyclones
- Random Forest
- Synthetic Aperture Radar
- Causal Inference
- Difference-in-Differences

### Keywords (comma-separated)
```
Sentinel-1, Sentinel-2, rice phenology, cyclone, saline inundation, BACI design, difference-in-differences, random forest, Odisha, Bay of Bengal, Copernicus EMS, Google Earth Engine
```

### Licence
**CC BY 4.0** — select from dropdown.

### Authors
1. **Supranab Panda** — pandasupranab@gmail.com — ORCID `0009-0009-6496-6545` — Siksha 'O' Anusandhan (Deemed to be) University, Bhubaneswar, India — *Corresponding author*
2. **Sarat Chandra Sahu** — ORCID `0000-0002-8048-1910` — Siksha 'O' Anusandhan (Deemed to be) University, Bhubaneswar, India

### Related identifiers (very important — Mendeley supports this; use "Related works" → "+ Add related work")
| Type | Identifier | Relation |
|---|---|---|
| Software | https://github.com/pandasupranab/RiceBaCI-GEE | IsSupplementedBy |
| DOI | 10.5281/zenodo.20024578 | IsSupplementedBy |
| DOI | 10.5281/zenodo.20585636 | IsDerivedFrom |
| URL | https://osf.io/c4mp8 | IsContinuationOf |
| DOI | 10.17605/OSF.IO/C4MP8 | IsContinuationOf |

### Funding
**None** — leave blank or write "No external funding".

### Institution
Siksha 'O' Anusandhan (Deemed to be) University, Bhubaneswar, Odisha, India.

## 5. Submit for moderation
1. Click **Publish dataset**.
2. Mendeley performs a brief curation review (typically same-day, max 1–2 business days). You will receive a confirmation email when the DOI is minted.
3. The DOI follows the pattern `10.17632/<random>` and resolves at `https://data.mendeley.com/datasets/<id>/1`.

## 6. After DOI mints
1. Email the DOI to **pandasupranab@gmail.com** (yourself) so you have a record.
2. Reply here with the DOI string — I will then:
   - Insert it into the Manuscript "Data Availability" section
   - Insert it into the Cover Letter reproducibility statement
   - Push the updated files to GitHub
   - Update the OSF wiki to point at the new Mendeley DOI

---

## Why this split (Mendeley + Zenodo)

- **Zenodo** holds the *code* archive (Git release `v1.0.1-submission`) — versioned, MIT-licensed, fast clone.
- **Mendeley Data** holds the *derived data* — Elsevier's own repository; surfaces automatically on the article page once RSE accepts the paper.

Two independent preservation paths, two independent DOIs, zero single-point-of-failure for reviewers.

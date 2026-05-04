# OSF Pre-Registration

> **Use:** Copy each section below into the corresponding field of the OSF "OSF Standard Pre-Data Collection Registration" form (`https://osf.io/registries`). Pre-registering before fetching the validation data strengthens reviewer trust and is increasingly cited in RSE reviews.
>
> **Recommended template on OSF:** *OSF Pre-Registration* (general purpose) — not the clinical-trials template.
>
> **Approximate completion time:** 45 minutes.

---

## Title

Decoupling Cyclone-Induced Saline Inundation from Agronomic Flooding in Sentinel-1/2 Rice Phenology Retrieval: A Multi-Year Bay-of-Bengal Coastal Framework (2017–2024)

## Authors

Supranab Panda (PhD candidate, Agricultural Meteorology, ORCID 0009-0009-6496-6545), Dr. Sarat Chandra Sahu (Director, Center for Environment and Climate, Siksha 'O' Anusandhan University, ORCID 0000-0002-8048-1910).

## Date of pre-registration

[Auto-filled by OSF on submission.]

---

## A. Study information

### A1. Hypotheses

We pre-register three primary hypotheses and one falsifiable null:

- **H1.** A multi-feature classifier combining Sentinel-1 backscatter (VH, VV, VH/VV), Sentinel-2 indices (NDWI, LSWI), JRC water permanence, and ERA5 wind speed can discriminate cyclone-induced saline inundation from agronomic transplanting flooding in coastal Odisha rice pixels with overall accuracy ≥ 88 % and F1 ≥ 0.85 against PlanetScope-NICFI visual reference.

- **H2.** When the cyclone-flood confound is corrected, the detected start-of-season (SOS), peak-of-season (POS) and end-of-season (EOS) dates differ from uncorrected estimates by a mean absolute error of ≥ 7 days during cyclone-impacted Kharif seasons (2019, 2020, 2021), but by < 2 days during control Kharif seasons (2017, 2018, 2022, 2023, 2024).

- **H3.** A Before-After-Control-Impact (BACI) mixed-effects model with year-type as fixed effect and district as random effect will show a statistically significant year-type × cyclone-exposure interaction term (α = 0.05) for SOS and EOS dates in the uncorrected series; the interaction will weaken or disappear in the corrected series.

- **H0 (null).** No combination of the eight features can separate cyclone-flood from agronomic-flood pixels above chance, and BACI shifts in phenological dates are not distinguishable from inter-annual noise. If H0 cannot be rejected, the manuscript will be reframed as a *characterization* of the limits of SAR-optical phenology retrieval under cyclone disruption — still publishable in RSE-tier journals as a methodological constraint paper.

---

## B. Design plan

### B1. Study type

Quasi-experimental, observational, multi-year remote-sensing time-series analysis with a Before-After-Control-Impact (BACI) design.

### B2. Blinding

Not applicable — the analyst (S. Panda) performs all steps. However, the random-forest training/test split is performed on stratified random sampling with a fixed `seed = 2026` documented in code.

### B3. Study design

- **Treatment units:** Sentinel-1/2 pixels (10 m) over the 5 coastal Odisha districts.
- **Treatment condition:** Kharif seasons impacted by cyclones with landfall ≤ 200 km of district centroid in the preceding 60 days (Fani 2019, Amphan 2020, Yaas 2021).
- **Control condition:** Kharif seasons 2017, 2018, 2022, 2023, 2024 in the same districts, plus 3 inland Odisha districts (Sambalpur, Bargarh, Sundargarh) for all 8 years as spatial controls.
- **BACI structure:** 2 × 2 × 5 design (treatment vs. control year × treatment vs. control district × 5 phenological metrics).

### B4. Randomization

- Validation reference points: 60 sites stratified by 3 strata (cyclone-impacted, control, non-rice), randomly drawn within each stratum using `ee.FeatureCollection.randomPoints(seed = 2026)`.
- Random-forest training/test split: 70/30 stratified random.
- Cross-validation: 5-fold spatial block CV with 50 km blocks to avoid spatial autocorrelation.

---

## C. Sampling plan

### C1. Existing data

Sentinel-1, Sentinel-2, JRC, ERA5, ESA WorldCover, IBTrACS, and PlanetScope archives all exist prior to pre-registration. No data has been analysed yet beyond visual inspection of the study area extent in Google Earth Engine.

### C2. Data collection procedures

All datasets used in this study are openly available without permission, application, or institutional gatekeeping. Satellite data are accessed via Google Earth Engine. The MODIS MCD12Q2 Land Surface Phenology product is distributed by NASA LP DAAC and accessed through GEE. PlanetScope NICFI is accessed via the NICFI Basemaps programme, which is freely available to academic users worldwide (`https://www.planet.com/nicfi/`). Cyclone tracks are downloaded from NOAA IBTrACS v04r00. ICRISAT Village Dynamics in South Asia (VDSA) microdata are downloaded from `http://vdsa.icrisat.org`. District-level Kharif rice yield records are downloaded from the Government of India Open Data Platform (`https://data.gov.in`). A complete data manifest is maintained at `docs/Data_Sources_Manifest.md`.

### C3. Sample size

- **Pixels:** ~ 6.2 million 10-m pixels in 5 coastal districts × 8 years = ~ 50 million pixel-years (full population, no sampling).
- **Validation reference:** 60 stratified PlanetScope visual-inspection sites × 8 years = 480 reference observations for the saline-flood classifier.
- **Phenological reference (primary):** MODIS MCD12Q2 greenup, peak, and dormancy dates for all rice pixels intersecting MCD12Q2 cropland classes across eight Kharif seasons (2017–2024), aggregated to district–year level. **Secondary:** ICRISAT VDSA Bhadrak panel transplanting and harvest dates aggregated to village centroids (≈240 households × multi-year). **Tertiary:** FAO–GIEWS / IRRI Rice Knowledge Bank Odisha Kharif crop calendars and district yield-anomaly cross-correlation.

### C4. Sample size rationale

Power analysis for the saline-flood classifier: with n = 480 binary reference observations balanced across classes, a McNemar's test has > 99 % power to detect an OA difference of 5 percentage points between corrected and uncorrected pipelines (α = 0.05). For the BACI mixed-effects model, n = 8 districts × 8 years = 64 district-year observations — adequate for a fixed-effects test with 2 levels and 1 random effect by the rule-of-thumb of ≥ 30 observations per parameter.

### C5. Stopping rule

Data collection ends 31 December 2026. All validation datasets are pre-committed open-data sources guaranteed to be accessible (MCD12Q2, VDSA, FAO–GIEWS, data.gov.in, PlanetScope NICFI), so no fallback strategy is required.

---

## D. Variables

### D1. Manipulated variables

None — observational study.

### D2. Measured variables

| Variable | Source | Unit |
|---|---|---|
| VH backscatter | Sentinel-1 GRD | dB |
| VV backscatter | Sentinel-1 GRD | dB |
| NDVI, LSWI, NDWI, CIre | Sentinel-2 L2A | unitless |
| Surface water permanence | JRC GSW Monthly | % of months |
| 10-m wind speed (max) | ERA5-Land Daily | m s⁻¹ |
| Total precipitation | ERA5-Land Daily | mm |
| Cyclone landfall date and distance | IBTrACS NI basin | km, day |
| Phenological stage date (validation, primary) | MODIS MCD12Q2 (greenup / peak / dormancy) | day-of-year |
| Phenological stage date (validation, secondary) | ICRISAT VDSA Bhadrak (transplanting / harvest) | day-of-year |
| Yield anomaly (validation, tertiary) | data.gov.in district Kharif rice yield | t/ha, detrended anomaly |
| Saline-flood vs. agronomic-flood label (validation) | PlanetScope visual | binary |

### D3. Indices

- Saline-flood probability per pixel (random forest output, 0–1).
- Corrected SOS/POS/EOS day-of-year per pixel (TIMESAT double-logistic).
- BACI shift = (treatment-year − control-year) phenological date difference, in days.

---

## E. Analysis plan

### E1. Statistical models

1. **Saline-flood classifier:** Random-forest binary classification with 8 features, evaluated by overall accuracy, user's & producer's accuracy, F1, and confusion matrix on a held-out 30 % test set.
2. **Phenology extraction:** TIMESAT v3.3 / `phenex` double-logistic curve fitting on cleaned VH and NDVI series; SOS/POS/EOS thresholds at 20 %, peak, and 80 % amplitude respectively.
3. **BACI:** Linear mixed-effects model
   `phenology_date ~ year_type * cyclone_exposure + (1 | district) + (1 | year)`
   fit with `lme4::lmer` in R, fixed-effect significance via parametric bootstrap (`pbkrtest`).
4. **Raw vs. corrected comparison:** Paired McNemar's test on classification labels and paired t-test on phenological dates, with Bonferroni correction across 5 metrics.

### E2. Transformations

- SAR backscatter converted to dB (10·log₁₀).
- Time series gap-filled with Whittaker smoother (λ chosen by generalised cross-validation).
- All dates expressed as Kharif day-of-year (days since 1 June).

### E3. Inference criteria

- Saline-flood classifier accepted if test-set OA ≥ 0.88 and F1 ≥ 0.85 (pre-registered thresholds).
- BACI interaction accepted as significant if 95 % bootstrap CI excludes zero.
- Effect size reported as Cohen's *d* in addition to *p*-values.

### E4. Data exclusion

Pixel-years are excluded if:

- Cloud cover > 95 % during the Kharif window (no S2 observations to support fusion).
- WorldCover cropland mask is < 0.5 fraction within the 10-m pixel (sub-pixel non-cropland contamination).
- Within 50 m of a known coastal aquaculture pond (false saline-flood positives).

These exclusion rules are fixed before analysis and applied identically to treatment and control groups.

### E5. Missing data

Whittaker-smoother gap-filling with bootstrap uncertainty intervals (1000 bootstrap samples). Pixels with > 50 % missing observations in a Kharif season are flagged and reported separately rather than gap-filled.

### E6. Exploratory analyses

Any analysis not listed above will be reported as exploratory and clearly flagged in the manuscript. Specifically: panicle-initiation date detection using S2 red-edge CIre is exploratory and will not be claimed as confirmatory.

---

## F. Data and code availability

- **Code (live development):** `https://github.com/pandasupranab/RiceBaCI-GEE` (MIT licence).
- **Code (permanent archive):** Zenodo, via the GitHub–Zenodo integration. A frozen DOI is minted automatically for every tagged GitHub release. Tags planned: `v0.1.0-prereg` (Week 1, paired with this OSF registration), `v1.0.0-submission` (at manuscript submission to RSE), `v1.0.0-final` (at acceptance). Concept DOI: `[pending — assigned on first release]`.
- **Processed datasets:** Mendeley Data — corrected SOS/POS/EOS rasters, BACI tables, validation reference points (coordinates + labels + PlanetScope scene URLs only, not the imagery itself, owing to NICFI re-distribution restrictions). Reserved DOI: `[pending — minted Week 1 Thu]`.
- **Statistical analysis scripts (R):** same GitHub repository under `/analysis/` and included in the Zenodo archive.
- **Both repositories use username `supranab` and email `pandasupranab@gmail.com`.**

---

## G. Other

### G1. Conflicts of interest

None.

### G2. Funding

[Insert funding source if any; otherwise: "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors."]

### G3. Ethical approval

Not applicable — observational satellite study, no human/animal subjects.

### G4. Generative-AI use

The analyst used Perplexity Computer (an AI research and writing assistant) to support literature review, study design and manuscript drafting. All AI-generated text and code were reviewed and edited by the human author, who takes full responsibility for the content. A Declaration of Generative AI Use will be included in the submitted manuscript per Elsevier policy.

---

*End of pre-registration.*

# OSF Pre-Registration — Ready-to-Paste Content

> **How to use this file:**
> 1. Go to https://osf.io and sign in
> 2. Click "Create new project" → name it: `RiceBaCI-GEE: Cyclone-Saline Inundation Correction in SAR Rice Phenology`
> 3. Inside the project, click "Registrations" → "New Registration"
> 4. Choose template: **OSF Preregistration**
> 5. Copy each section below into the corresponding form field
> 6. Save as draft, review, then click "Register" to make it public and time-stamped

---

## STUDY INFORMATION

### Title
Decoupling Cyclone-Induced Saline Inundation from Agronomic Flooding in Sentinel-1/2 Rice Phenology Retrieval: A Multi-Year Bay-of-Bengal Coastal Framework (2017–2024)

### Authors
Supranab Panda (PhD candidate, Agricultural Meteorology, ORCID 0009-0009-6496-6545); Dr. Sarat Chandra Sahu (Director, Center for Environment and Climate, Siksha 'O' Anusandhan University, ORCID 0000-0002-8048-1910).

### Description
Tropical cyclones increasingly disrupt Kharif rice cultivation along the Bay of Bengal coast. The C-band SAR backscatter trough that anchors Start-of-Season (SOS) detection in published Sentinel-1 rice phenology algorithms can be confounded with cyclone-induced saline storm-surge inundation occurring weeks earlier — silently corrupting derived phenological dates. This study (i) develops an open-source random-forest classifier that separates cyclone-induced saline flooding from agronomic transplanting flooding using Sentinel-1, Sentinel-2, JRC water permanence, and ERA5 wind features; (ii) propagates classifier output into a parallel raw-vs-corrected Whittaker-smoothed double-logistic phenology pipeline; (iii) quantifies the resulting bias using a Before-After-Control-Impact (BACI) mixed-effects model. Five coastal Odisha districts (Balasore, Bhadrak, Kendrapara, Jagatsinghapur, Puri) and three inland controls (Dhenkanal, Angul, Cuttack) are analysed across eight Kharif seasons (2017–2024) covering Cyclones Fani (May 2019), Bulbul (Nov 2019), Amphan (May 2020), and Yaas (May 2021).

---

## DESIGN PLAN

### Study type
Observational, retrospective natural-experiment design using a Before-After-Control-Impact (BACI) framework. Cyclone landfalls during the 2017–2024 period are used as natural treatment events; spatially separated inland districts serve as controls.

### Blinding
Not applicable — analysis uses publicly archived satellite data and pre-existing cyclone track data. To minimise circularity, the saline-flood classifier is trained on labels derived from PlanetScope NICFI visual interpretation **before** any phenological analysis is performed; the analyst assigning labels does not view the SAR backscatter time series during labelling.

### Study design
- **Treatment units:** Five coastal Odisha districts (Balasore, Bhadrak, Kendrapara, Jagatsinghapur, Puri).
- **Control units:** Three inland Odisha districts (Dhenkanal, Angul, Cuttack), >120 km from coast, in the Mahanadi basin with similar rice cropping calendars.
- **Treatment years:** 2019, 2020, 2021 (cyclones Fani, Bulbul, Amphan, Yaas made landfall).
- **Control years:** 2017, 2018, 2022, 2023, 2024.
- **Pixel resolution:** 10 m (Sentinel-1 native).
- **Outcome variables:** SOS, POS, EOS dates (day-of-year) per pixel per Kharif season; raw and corrected.

### Randomization
Not applicable — observational design.

---

## SAMPLING PLAN

### Existing data
All datasets exist prior to this pre-registration. We have not yet accessed or analysed any data with respect to the hypotheses below.

### Explanation of existing data
- Sentinel-1 GRD (2014–present, ESA Copernicus): C-band SAR, openly available via Google Earth Engine (`COPERNICUS/S1_GRD`).
- Sentinel-2 SR (2017–present, ESA Copernicus): Multispectral 10–60 m, openly available via GEE (`COPERNICUS/S2_SR_HARMONIZED`).
- MODIS MCD12Q2 v6.1 Land Surface Phenology (NASA, 2001–present): openly available via GEE.
- ERA5-Land hourly reanalysis (2017–present, ECMWF): openly available via GEE.
- IBTrACS North Indian Ocean cyclone tracks v04r00 (NOAA): openly available at https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/csv/.
- ESA WorldCover 10 m 2021 v200: openly available via GEE.
- JRC Global Surface Water v1.4: openly available via GEE.
- ICRISAT VDSA Bhadrak panel: openly available at http://vdsa.icrisat.org.
- PlanetScope NICFI 2017–2024 quarterly basemaps: free academic access at https://www.planet.com/nicfi/.
- District-level Kharif rice yield records: openly available at https://data.gov.in.
- FAO-GIEWS / IRRI Rice Knowledge Bank crop calendars: openly available.

### Data collection procedures
All data are accessed programmatically via Google Earth Engine JavaScript API or HTTP download from the listed sources. Code modules for ingestion are version-controlled at https://github.com/pandasupranab/RiceBaCI-GEE.

### Sample size
Approximately 1,200,000 Kharif rice pixels per year per district (after applying ESA WorldCover crop mask + Singha 2019 paddy rice mask intersection). For BACI inference: 8 districts × 8 years = 64 district-years. For classifier validation: 480 PlanetScope visual reference labels stratified across 5 coastal districts × 3 treatment years × 32 sites per cell.

### Stopping rule
Analysis covers the full 2017–2024 Kharif window. No interim analysis or sequential testing.

---

## VARIABLES

### Manipulated variables
None — observational study.

### Measured variables

**Primary outcomes:**
- SOS, POS, EOS dates per pixel per Kharif season (raw and corrected pipelines), in day-of-year.

**Secondary outcomes:**
- Saline-flood classifier accuracy (Overall Accuracy, F1 score, User's accuracy, Producer's accuracy).
- Mean Absolute Error (MAE) and Root Mean Square Error (RMSE) of corrected SOS/POS/EOS against MCD12Q2 reference.
- BACI interaction coefficient (β, days) and 95% bootstrap confidence interval.
- Pearson correlation between corrected SOS shift and district yield anomaly.

**Predictor variables (classifier features):**
- Sentinel-1: VH backscatter (dB), VV backscatter (dB), VH/VV cross-ratio.
- Sentinel-2: NDWI, LSWI.
- JRC Global Surface Water: occurrence permanence (%).
- ERA5: Maximum 10-m wind speed during the May–June pre-monsoon window (m/s).
- IBTrACS-derived: Distance to nearest cyclone track (km), days since cyclone landfall.

### Indices
- **NDWI** = (Green − NIR) / (Green + NIR), Sentinel-2 bands B3, B8.
- **LSWI** = (NIR − SWIR1) / (NIR + SWIR1), Sentinel-2 bands B8, B11.
- **VH/VV cross-ratio** = VH backscatter (dB) − VV backscatter (dB).

---

## ANALYSIS PLAN

### Statistical models

**Saline-flood classifier:** Random Forest (500 trees, default Gini split, min leaf size 5) trained on 70 % of the 480 PlanetScope visual reference labels. Performance evaluated on held-out 30 %, stratified by district and year. Spatial block cross-validation (50 km blocks, 5 folds) reported alongside random-split accuracy to detect spatial autocorrelation inflation.

**Phenology extraction:**
- VH time series gap-filled by Whittaker smoother (λ = 1600).
- NDVI time series fitted to double-logistic curve following Beck et al. 2006 parameterisation.
- SOS = first-derivative maximum of ascending limb; POS = curve maximum; EOS = first-derivative maximum of descending limb.
- For corrected pipeline: pixels classified as cyclone-flood are masked from the SOS detection step and treated as gap-fill values for the Whittaker smoother.

**BACI mixed-effects model:**
```
SOS_pixel ~ year_type * coastal_indicator + (1|district) + (1|year)
```
where `year_type ∈ {treatment, control}` and `coastal_indicator ∈ {coastal, inland}`. Implemented in R using `lme4::lmer`. Fixed-effect interaction coefficient β is the primary BACI estimand. Inference via parametric bootstrap (10,000 iterations) with `pbkrtest::PBmodcomp`. Repeated for POS and EOS.

### Hypotheses

**H1 (Classifier accuracy):** The saline-flood classifier achieves Overall Accuracy ≥ 0.88 and F1 ≥ 0.85 on the held-out test set, against PlanetScope visual reference labels.

**H2 (Control-year fidelity):** In control years (2017, 2018, 2022, 2023, 2024), the corrected and raw pipelines agree to within MAE ≤ 2 days for SOS, POS, EOS — confirming the correction does not introduce spurious shifts when no cyclone surge occurred.

**H3 (BACI suppression):** The BACI interaction coefficient β for SOS in the corrected pipeline is statistically smaller (p < 0.05) than in the raw pipeline. After correction, |β_corrected| < |β_raw| × 0.5 (i.e., correction removes at least half of the apparent BACI effect).

**H4 (Validation accuracy):** Corrected SOS/POS/EOS dates achieve MAE ≤ 10 days against MCD12Q2 reference across all district-years.

**H5 (Yield coupling):** The corrected SOS shift in cyclone years correlates more strongly with district Kharif yield anomalies than the uncorrected series (|r_corrected| > |r_raw|, p < 0.05 for the difference).

### Inference criteria
- Hypotheses tested at α = 0.05.
- 95% confidence intervals via parametric bootstrap (10,000 iterations).
- Multiple-comparison correction: Holm–Bonferroni across the 5 hypotheses.

### Data exclusion
Pixels excluded if:
- Outside the ESA WorldCover 2021 cropland class.
- Not flagged as paddy rice in the Singha et al. 2019 South Asia rice mask.
- Sentinel-1 incidence angle outside 30°–45° to control geometric variability.
- Fewer than 12 valid Sentinel-1 observations in a Kharif season.
- District boundary buffer of 1 km to remove edge pixels.

### Missing data
Cloud-affected Sentinel-2 observations are gap-filled by the harmonic Sentinel-2 LST interpolation. SAR observations missing due to acquisition gaps are gap-filled by Whittaker smoother. No imputation of phenological dates: pixels with insufficient observations (< 12 SAR scenes) are excluded entirely.

### Exploratory analyses
- Andhra Pradesh transferability test (Cyclone Hudhud 2014–2016): Treated as exploratory — not part of confirmatory hypotheses.
- Panicle initiation (PI) detection from Sentinel-2 red-edge bands (B5/B7): Treated as exploratory.
- Rice variety effects: Treated as exploratory pending field-survey integration.

---

## OTHER

### Code and data sharing
All Earth Engine JavaScript modules and R analysis scripts are publicly developed at https://github.com/pandasupranab/RiceBaCI-GEE (MIT licence) and permanently archived at Zenodo via the GitHub–Zenodo integration, which mints a DOI for every tagged release (v0.1.0-prereg paired with this OSF registration; v1.0.0-submission at manuscript submission; v1.0.0-final at acceptance). Processed corrected SOS/POS/EOS rasters, BACI tables and validation reference points are deposited at Mendeley Data with a DOI reserved before submission and the deposit finalised at acceptance. PlanetScope NICFI imagery cannot be redistributed under NICFI programme terms; the derived validation reference point coordinates and labels (not the imagery) are deposited in the Mendeley Data record. Both repositories use username `supranab` and email pandasupranab@gmail.com.

### Conflict of interest
The authors declare no conflict of interest.

### Funding
This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

### AI-assisted writing disclosure
During preparation of this study and pre-registration document, the authors used Perplexity Computer (Anthropic Claude Sonnet 4.6 large language model) for supplementary literature review, code drafting, and document structuring. The authors reviewed and edited all content and take full responsibility for the work.

---

> **Final step:** After registering on OSF, copy the resulting OSF URL (e.g., https://osf.io/abc12/) and paste it into:
> - `manuscript/manuscript_text.md` (search for "https://osf.io/c4mp8")
> - `manuscript/00_cover_letter.md`
> - `README.md`

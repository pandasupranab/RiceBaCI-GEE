# Mendeley Data — "Steps to reproduce" field

Paste the block below into the **Steps to reproduce** field on the Mendeley Data submission form.

---

## STEPS TO REPRODUCE (paste verbatim)

Every numerical result and CSV in this deposit can be regenerated end-to-end from public Copernicus, NASA, JRC, ECMWF and GADM inputs using the openly-licensed RiceBaCI-GEE pipeline. No proprietary data, no paid API, no institutional sign-in is required at any step.

### 1. Software environment
- **Google Earth Engine** JavaScript Code Editor (web-based, free Earth Engine account at https://code.earthengine.google.com — sign-in with any Google account).
- **Python 3.11** with packages pinned in `requirements.txt` on the companion repository. Key libraries: `geopandas` 0.14, `rasterio` 1.3, `scikit-learn` 1.4, `statsmodels` 0.14, `linearmodels` 5.4 (TWFE two-way fixed-effects), `wildboottest` 0.2 (wild-cluster restricted bootstrap), `xarray` 2024.2, `numpy` 1.26, `pandas` 2.2.
- **Operating system:** tested on Ubuntu 22.04 LTS and macOS 14; no platform-specific dependencies.
- **Source code:** https://github.com/pandasupranab/RiceBaCI-GEE — pinned release tag `v1.0.1-submission`, archived on Zenodo at DOI 10.5281/zenodo.20587316 (concept DOI 10.5281/zenodo.20024578).

### 2. Input data (all public, no permission required)
| Layer | Source | Asset / endpoint | Resolution / cadence |
|---|---|---|---|
| Sentinel-1 GRD (VV+VH, IW mode) | ESA Copernicus | `COPERNICUS/S1_GRD` (Google Earth Engine catalogue) | 10 m, 6–12 day revisit |
| Sentinel-2 L2A (SR) | ESA Copernicus | `COPERNICUS/S2_SR_HARMONIZED` | 10–20 m, 5 day revisit |
| JRC Global Surface Water | EC Joint Research Centre | `JRC/GSW1_4/GlobalSurfaceWater` | 30 m, monthly history |
| ERA5 hourly single-levels | ECMWF | `ECMWF/ERA5_LAND/HOURLY` | 0.1°, hourly |
| MODIS Land-Surface Phenology | NASA LP DAAC | `MODIS/061/MCD12Q2` | 500 m, annual |
| Cyclone Fani EMSR357 flood footprint | Copernicus Emergency Management Service | https://emergency.copernicus.eu/mapping/list-of-components/EMSR357 (vector shapefile, freely downloadable) | Vector |
| Administrative boundaries | GADM v4.1 | https://gadm.org/download_country.html (India, level 2) | Vector |
| Cyclone tracks and intensity | IMD RSMC New Delhi annual reports | https://rsmcnewdelhi.imd.gov.in/ (PDF, freely downloadable) | Point-time-series |

### 3. End-to-end pipeline (twelve modules)

The pipeline runs as twelve numbered modules. Modules 1–10 execute in Google Earth Engine (JavaScript); modules 11–12 and the statistical analysis execute in Python.

1. **Module 01 — Study-area definition.** Load GADM Odisha district boundaries; tag five coastal districts (Balasore, Bhadrak, Kendrapara, Jagatsinghpur, Puri) as treated and three inland districts (Dhenkanal, Angul, Cuttack) as controls. Optionally add Andhra Pradesh districts (Srikakulam, Vizianagaram, Visakhapatnam) for the Hudhud transferability test.
2. **Module 02 — Saline-flood classifier training.** Ingest the n=480 stratified label set (240 cyclone-induced saline-inundation labels sampled from the Copernicus EMS EMSR357 Fani master delineation, Amphan and Yaas Sentinel-1 pre/post change detections at ≥3 dB drop; 240 agronomic-transplanting-flood labels sampled from Sentinel-1 VH −22 to −17 dB ∩ ESA WorldCover cropland ∩ JRC GSW seasonal water 1–5 months/year during non-cyclone windows). Extract eight features per label point: ΔVH (dB), ΔCR (cross-ratio dB), VV minimum in event window, ERA5 3-day maximum wind speed, LSWI minimum in event window, JRC water-permanence, NDWI maximum in event window, and the 10 m Sentinel-2 NDVI baseline. Train a `RandomForestClassifier` (n_estimators=500, max_depth=12, class_weight='balanced', random_state=17) with stratified 80/20 hold-out and 5-fold stratified cross-validation. Output: `rf_model_card_v0.3.0_full.json` (OA = 0.990, 5-fold CV OA = 0.996). Repeat without optical features to produce the SAR-only robustness variant `rf_model_card_v0.3.0_sar_only.json` (OA = 0.844, CV OA = 0.831).
3. **Module 03 — Sentinel-1 backscatter time series.** For each district × Kharif season (1 June – 30 November, 2017–2024), build a 6-day median composite of Sentinel-1 VV and VH backscatter restricted to a 10-m rice mask (ESA WorldCover 2021 cropland ∩ Mondal et al. 2022 rice mask ∩ Singha et al. 2019 paddy-rice mask).
4. **Module 04 — Sentinel-2 NDVI/EVI/LSWI time series.** Cloud-mask using QA60 and SCL, build 10-day median composites of NDVI, EVI and LSWI on the same rice mask.
5. **Module 05 — Whittaker smoothing + double-logistic curve fit.** Smooth each 10-m pixel's NDVI time series with a Whittaker smoother (λ = 1000) and fit a four-parameter double-logistic curve to extract Start-of-Season (SOS), Peak-of-Season (POS) and End-of-Season (EOS) dates per pixel.
6. **Module 06 — District aggregation (raw pipeline).** Aggregate per-pixel SOS/POS/EOS to district medians; export as `district_panel_n384_BACI.csv` rows with `pipeline = raw`.
7. **Module 07 — Cyclone-flood mask application.** Apply the trained classifier from Module 02 to the cyclone-window Sentinel-1+2+ERA5 feature stack; emit a binary 10-m cyclone-saline-flood mask per cyclone event.
8. **Module 08 — Per-district cyclone-flood pixel-share.** Intersect the cyclone-flood mask with each district polygon to compute `flood_share = flood_area_km2 / district_area_km2` — exported as `cyclone_pixel_share_per_district_year.csv`.
9. **Module 09 — Corrected phenology extraction.** Re-run Modules 03–05 on pixels filtered to exclude cyclone-saline-flood-classified pixels; district-aggregate to produce the corrected panel rows (`pipeline = corrected`).
10. **Module 10 — Identification DAG validation.** Verify the assumed identifying restrictions: no spillovers (inland controls have flood_share ≈ 0), exclusion (cyclone affects phenology only via the saline-inundation pathway), monotonicity (SOS bias is non-negative under saline inundation).
11. **Module 11 — Cyclone climatology.** Compile the cyclone-event climatology table from IMD RSMC New Delhi annual reports (ESCS/VSCS classification, peak wind, landfall date/location).
12. **Module 12 — Backscatter signature characterisation.** Compute the mean ΔVH/ΔCR signature per cyclone event from the labelled set, exported as the supplementary backscatter table.

### 4. Statistical analysis (single-command refresh)

After the GEE modules have populated `data_real/bacI_panel_real.csv`, the entire downstream statistical layer regenerates with one command:

```bash
git clone https://github.com/pandasupranab/RiceBaCI-GEE.git
cd RiceBaCI-GEE
git checkout v1.0.1-submission
pip install -r requirements.txt
python scripts/refresh_v21_from_module12.py
```

This script executes, in order:
1. **Two-way fixed-effects difference-in-differences** (`linearmodels.PanelOLS`, district + year fixed effects, district-clustered standard errors) — outputs `v21_did_static.csv`.
2. **Event-study leads-and-lags** (k = −3 … +3 around treatment) — outputs `v21_event_study.csv`.
3. **Pre-treatment parallel-trends test** — outputs `v21_parallel_trends.csv`.
4. **Wild-cluster restricted bootstrap** (`wildboottest`, B = 9,999, restricted null H₀: τ = 0) — outputs `v21_wild_bootstrap.csv`. Required because J = 8 clusters is below the asymptotic threshold for standard inference.
5. **Leave-one-out jackknife** at the district level and the year level — outputs `v21_jackknife_district.csv` and `v21_jackknife_year.csv`.
6. **In-space placebo** (1,000 random reassignments of treatment status across districts) — outputs `v21_placebo_in_space.csv` and `v21_placebo_summary.csv`.
7. **In-time placebo** (treatment shifted to non-cyclone years) — outputs `v21_placebo_in_time.csv`.

Runtime: ~6 minutes on a 2024 laptop (8-core, 16 GB RAM). No GPU required.

### 5. Validation strategy
Five mutually independent reference sources are used to validate the corrected phenology and the classifier:
1. **NASA MODIS MCD12Q2** Land Surface Phenology — methodologically independent (different sensor, different algorithm).
2. **ICRISAT VDSA microdata** — Bhadrak benchmark site, ground-survey transplanting dates.
3. **District-level Kharif rice yield records** from data.gov.in — outcome-side concordance.
4. **Sentinel-2 high-resolution visual interpretation** at 60 stratified sites (the openly-redistributable fallback to PlanetScope NICFI, activated under the pre-registered §E5 path after the Tropical Forest Observatory programme restricted eligibility to forest-domain users).
5. **Two existing rice-mask products** — Mondal et al. 2022 (Odisha rice-fallow Sentinel-1) and Singha et al. 2019 (South Asia Sentinel-1 paddy rice). Transferability is additionally tested on the Andhra Pradesh coast under Cyclone Hudhud (October 2014).

### 6. Pre-registration and identifiers
- Pre-registration: https://osf.io/c4mp8 (DOI 10.17605/OSF.IO/C4MP8) — all hypotheses, analysis decisions, and inference criteria registered prior to data analysis.
- Code archive (this version): Zenodo DOI 10.5281/zenodo.20587316 (v1.0.1-submission).
- Concept (always-latest) DOI: 10.5281/zenodo.20024578.
- Author ORCIDs: Supranab Panda 0009-0009-6496-6545; Sarat Chandra Sahu 0000-0002-8048-1910.

### 7. Expected reproduction outcome
Running the single-command refresh on the inputs above will exactly reproduce:
- τ̂_SOS raw = +15.289 d → corrected = +15.108 d
- τ̂_EOS corrected = −0.239 d
- Maximum absolute correction |Δ| = 1.510 d, mean |Δ| = 0.223 d
- Random-forest overall accuracy 0.990 (full feature set), 0.844 (SAR-only)

These are the headline numbers reported in the manuscript abstract.

---

**Length check:** ~5,800 characters. Mendeley Data accepts long entries here; if your form imposes a hard cap, the most important blocks to keep are sections 1, 2, 3 (numbered list of modules) and 4 (the single-command refresh). Section 5 can move to the README description if needed.

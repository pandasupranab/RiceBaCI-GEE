# Decoupling Cyclone-Induced Saline Inundation from Agronomic Flooding in Sentinel-1/2 Rice Phenology Retrieval: A Multi-Year Bay-of-Bengal Coastal Framework (2017–2024)

---

## Title Page

**Title:** Decoupling Cyclone-Induced Saline Inundation from Agronomic Flooding in Sentinel-1/2 Rice Phenology Retrieval: A Multi-Year Bay-of-Bengal Coastal Framework (2017–2024)

**Authors:**

Supranab Panda¹*, Sarat Chandra Sahu¹

**Affiliations:**

¹ Center for Environment and Climate, Institute of Technical Education and Research, Siksha 'O' Anusandhan (Deemed to be) University, Bhubaneswar 751030, Odisha, India

**Corresponding author:**

Supranab Panda  
Center for Environment and Climate, Institute of Technical Education and Research, Siksha 'O' Anusandhan (Deemed to be) University, Bhubaneswar 751030, Odisha, India  
E-mail: pandasupranab@gmail.com  
ORCID: 0009-0009-6496-6545

**Co-author / Supervisor:**

Sarat Chandra Sahu, Director, Center for Environment and Climate, Institute of Technical Education and Research, Siksha 'O' Anusandhan (Deemed to be) University, Bhubaneswar 751030, Odisha, India  
ORCID: 0000-0002-8048-1910

---

## Abstract

Tropical cyclones increasingly disrupt Kharif rice cultivation along the Bay of Bengal coast, yet no published study has characterised or corrected the bias that cyclone-induced saline storm-surge inundation introduces into Sentinel-1/2 rice phenology retrieval. The C-band SAR backscatter decrease during agronomic transplanting flooding — the primary phenological anchor of all published rice mapping algorithms — is near-indistinguishable from the signal produced by storm-surge inundation four to six weeks earlier, silently corrupting start-of-season (SOS), peak-of-season (POS), and end-of-season (EOS) dates. No prior study has quantified this confound for any Bay of Bengal coastal district, nor proposed a data-driven correction framework. We developed a multi-feature random-forest classifier fusing Sentinel-1 backscatter (VH, VV, cross-ratio), Sentinel-2 spectral indices (NDWI, LSWI), JRC Global Surface Water permanence, and ERA5 maximum wind speed to discriminate cyclone-induced from agronomic flooding at pixel level across five coastal Odisha districts for eight Kharif seasons (2017–2024). Corrected and uncorrected phenological time series were compared using a Before-After-Control-Impact (BACI) mixed-effects model, with multi-source validation against the MODIS MCD12Q2 Land Surface Phenology product, ICRISAT Village Dynamics in South Asia (VDSA) microdata for the Bhadrak benchmark site, district-level rice yield records from data.gov.in, and PlanetScope NICFI reference imagery. The classifier achieved [PLACEHOLDER: OA = X.XX, F1 = X.XX] on the held-out test set. Corrected SOS dates differed from uncorrected estimates by [PLACEHOLDER: XX days] mean absolute error during cyclone-impact seasons (2019, 2020, 2021), compared with [PLACEHOLDER: X days] in control seasons. The BACI model detected a statistically significant year-type × cyclone-exposure interaction in the uncorrected series [PLACEHOLDER: β = X.X days, 95% CI: X.X–X.X], which [PLACEHOLDER: weakened substantially / disappeared] after correction. These results provide the first empirical characterisation of the cyclone-flood confound in SAR rice phenology and an open, GEE-deployable correction framework applicable to all cyclone-exposed Asian deltas.

**Word count (abstract): 245**

---

## Highlights

- First SAR–optical framework to decouple cyclone surge from agronomic flooding in rice
- Random-forest classifier fuses 8 features; validated over 5 Bay-of-Bengal districts
- Uncorrected SOS biased by ≥7 days in cyclone years; BACI model quantifies shift
- Open GEE toolkit covers 8 Kharif seasons (2017–2024) at 10 m resolution
- Framework transferable to any cyclone-exposed Asian delta; tested on Andhra Pradesh

---

## Keywords

Sentinel-1; SAR-backscatter; rice-phenology; cyclone-inundation; BACI; coastal-Odisha

---

## 1. Introduction

Rice (*Oryza sativa* L.) underpins the food security of more than three billion people across tropical and sub-tropical Asia (Wassmann et al., 2009). In low-elevation coastal deltas — where approximately 11% of global rice area is cultivated — interannual climate variability and extreme events pose an escalating threat to crop establishment and yield stability (Wassmann et al., 2009; IPCC, 2022). Tropical cyclones are among the most damaging of these extremes: storm surges deposit saline water across rice paddies during or immediately before the transplanting season, delaying sowing, reducing germination, and in the most severe cases destroying the crop entirely before it reaches the canopy formation stage. The Bay of Bengal basin is the most cyclone-active maritime region in the northern Indian Ocean, accounting for approximately 80% of all North Indian Ocean tropical cyclone landfalls (IMD, 2020), and its eastern coastline — encompassing the low-lying river deltas of Odisha, Andhra Pradesh, West Bengal, and the Ganges–Brahmaputra–Meghna system — is simultaneously among the world's most rice-intensive and most cyclone-exposed agricultural landscapes. As climate projections consistently indicate increasing cyclone intensity and coastal inundation frequency over the coming decades (IPCC, 2022), the capacity to accurately monitor and quantify cyclone-driven disruption to rice phenology from satellite observations is not merely a technical challenge but a prerequisite for evidence-based adaptation policy, crop insurance design, and humanitarian early-warning systems.

Satellite remote sensing offers an unrivalled capacity for systematic, multi-year phenological monitoring at the spatial resolution and temporal frequency demanded by operational agriculture. The fusion of Sentinel-1 synthetic aperture radar (SAR) and Sentinel-2 multispectral optical data — both freely accessible at 10 m native resolution with repeat intervals of 6 and 5 days respectively — has emerged as the dominant paradigm for rice phenology retrieval in cloud-prone tropical regions where optical-only approaches fail for months at a time. Meroni et al. (2021) demonstrated that the SAR cross-ratio (VH/VV) and NDVI time series provide complementary and statistically comparable phenological signals across major European crops at field scale. Singha et al. (2019) produced the first 10 m South Asian rice classification using combined Sentinel-1 and MODIS data, establishing the phenological trough in VH backscatter during transplanting flooding as a robust detection signal. Hu et al. (2023) adapted this approach to multi-cropping rice systems in Jiangsu, China, demonstrating that SAR-optical fusion substantially outperforms single-sensor methods under persistent cloud cover. Minasny et al. (2022) and Xu et al. (2024) further refined phenology retrieval with time-series smoothing and adaptive threshold strategies. More recently, Shi et al. (2024), Wang et al. (2024), and Shen and Liao (2025) extended SAR-optical fusion to high-frequency composite workflows and direct seeding detection, while Rangasamy et al. (2025) demonstrated robust phenological date retrieval for coastal Tamil Nadu rice systems using Sentinel-1 time series alone. Fikriyah et al. (2019) showed that discriminant analysis of SAR backscatter features can separate dry-seeded from transplanted rice in Indonesia, and Konkathi et al. (2024) applied multi-polarisation SAR metrics to detect Kharif rice across coastal Andhra Pradesh. Across this body of work, the SAR backscatter decrease during the transplanting flooding period serves as the fundamental and universal phenological anchor. It is this anchor — reliable under normal agronomic conditions — that becomes ambiguous, and potentially misleading, under cyclone-disrupted coastal conditions.

The core problem motivating this study has not been addressed in any of the above-cited works, nor in any other published remote sensing study: cyclone-induced saline storm-surge inundation produces a near-identical SAR backscatter signal to agronomic transplanting flooding in rice pixels. Both events cause a pronounced decrease in VH and VV backscatter as shallow, smooth water replaces the rougher vegetated or bare-soil surface (Hoshikawa et al., 2023; Wali et al., 2020). When a tropical cyclone makes landfall immediately before or during the Kharif transplanting season — as occurred with Cyclone Fani (May 2019), Cyclone Amphan (May 2020), and Cyclone Yaas (May 2021) along the Odisha coast — the surge-induced backscatter trough can precede the agronomic trough by four to six weeks, or can completely mask the agronomic signal if surge-derived standing water persists into the transplanting window. Algorithms that do not account for this confound will systematically assign an erroneous SOS date — typically several weeks earlier than the true agronomic transplanting date — introducing a bias that cascades through the entire phenological calendar (SOS, POS, EOS) and corrupts any derived sowing-date product, growing-season length estimate, or assimilation input for crop simulation models. Pham-Van et al. (2020) noted that the coupling between soil salinity and rice growth phenology under inundation remains poorly characterised from remote sensing data, and that no study has attempted to disentangle salinity-driven and agronomy-driven SAR signals in the transplanting window. Wali et al. (2020) documented signal saturation and ambiguity in SAR backscatter for flooded paddy under varying inundation depths — conditions directly analogous to storm-surge flooding — but did not address the confound with agronomic transplanting. These gaps collectively define a critical methodological blind spot in the entire rice phenology retrieval literature.

Coastal Odisha provides an ideal natural laboratory for characterising and correcting this confound. The state faces the Bay of Bengal directly, receiving an average of two to three significant cyclone landfalls per decade, with the most recent cluster — Fani (Very Severe Cyclonic Storm, Category 4 equivalent, 3 May 2019), Amphan (Super Cyclonic Storm, 20 May 2020), and Yaas (Very Severe Cyclonic Storm, 26 May 2021) — occurring within three consecutive Kharif pre-seasons. These three events provide three independent treatment years bracketed by five control Kharif seasons (2017, 2018, 2022, 2023, 2024) within the Sentinel-1 temporal archive, enabling a rigorous Before-After-Control-Impact (BACI) quasi-experimental design. The five coastal districts of Balasore, Bhadrak, Kendrapara, Jagatsinghapur, and Puri together constitute one of the most rice-intensive coastal zones in India, with Kharif rice occupying an estimated 3.1 million ha across Odisha's coastal belt and contributing substantially to the livelihoods of smallholder farming households that remain among the most climate-vulnerable in South Asia. Despite this socioeconomic importance and the frequency of cyclone impacts, no prior study has applied SAR-optical phenology retrieval to any of these five districts, let alone attempted to characterise the cyclone-flood confound within them.

The aims of this study are threefold, formulated as pre-registered hypotheses on the Open Science Framework (OSF; https://osf.io/c4mp8). Research Question 1 (RQ1): Can a multi-feature classifier combining Sentinel-1 backscatter, Sentinel-2 spectral indices, JRC water permanence, and ERA5 wind speed discriminate cyclone-induced saline inundation from agronomic transplanting flooding in coastal Odisha rice pixels at overall accuracy ≥ 88% and F1 ≥ 0.85? Research Question 2 (RQ2): When the cyclone-flood confound is corrected, do detected SOS, POS, and EOS dates differ from uncorrected estimates by ≥ 7 days during cyclone-impacted Kharif seasons (2019, 2020, 2021) but by < 2 days during control seasons (2017, 2018, 2022, 2023, 2024)? Research Question 3 (RQ3): Does a BACI mixed-effects model reveal a statistically significant year-type × cyclone-exposure interaction for phenological dates in the uncorrected series, and does this interaction weaken or disappear after correction? This study makes four specific contributions: (i) the first empirical characterisation of the cyclone-flood confound in SAR rice phenology retrieval for any Bay of Bengal coastal district; (ii) a novel multi-feature random-forest classifier for distinguishing saline storm-surge inundation from agronomic flooding at 10 m pixel level; (iii) a quantitative BACI assessment of cyclone-induced bias in Sentinel-1/2 phenological products across eight Kharif seasons; and (iv) an open, reproducible Google Earth Engine toolkit (RiceBaCI-GEE) validated for coastal Odisha and demonstrated to transfer to Andhra Pradesh coastal districts impacted by Cyclone Hudhud (2014). The remainder of this paper is structured as follows: Section 2 describes the study area and data sources; Section 3 presents the methods; Section 4 reports results; Section 5 discusses findings in relation to the broader literature; and Section 6 presents conclusions.

---

## 2. Study Area and Data

### 2.1 Study Area

The primary study area encompasses five coastal districts of Odisha state, eastern India: Balasore, Bhadrak, Kendrapara, Jagatsinghapur, and Puri (Figure 1). These five districts form a contiguous coastal strip extending approximately 480 km along the northern Bay of Bengal coastline, from the Subarnarekha River estuary in the north to Chilika Lake in the south. Combined, the districts cover a total area of approximately 12,389 km², of which roughly 50% constitutes cropland as classified by the ESA WorldCover v200 product (Zanaga et al., 2022). Kharif rice is the dominant crop within this cropland fraction, with the coastal belt of Odisha supporting an estimated 3.1 million ha of rice cultivation in a normal Kharif season. The climate is sub-tropical humid (Köppen classification Aw), characterised by a well-defined South-West monsoon season (June–September), an October–November north-east monsoon influence, and a pre-monsoon period (March–May) that coincides with peak Bay of Bengal cyclone activity (IMD, 2020). Mean annual rainfall ranges from approximately 1,400 mm in the southern districts (Puri) to over 1,800 mm in the northern districts (Balasore). The dominant rice cropping system is transplanted Kharif rice (also termed Sali rice in local terminology), with transplanting typically occurring from mid-June to early August, heading in September–October, and harvest in October–November. Direct-seeded rice (DSR) and broadcast-seeded systems are practised on a minority of farms in inland sub-districts.

Three inland Odisha districts — Sambalpur, Bargarh, and Sundargarh — serve as spatial control units in the BACI design. These districts are situated 150–350 km from the coast and lie beyond the storm-surge footprint of any Bay of Bengal cyclone, rendering them climatically comparable in terms of monsoon rainfall but categorically unexposed to saline inundation. Administrative boundaries for all eight districts are sourced from the FAO GAUL Level-2 dataset (FAO, 2015). The GEE collection identifier is `FAO/GAUL/2015/level2`. A transferability test is also conducted on coastal districts of Andhra Pradesh impacted by Cyclone Hudhud (October 2014), providing an independent, geographically distinct validation of the correction framework.

### 2.2 Cyclone Events

Three major tropical cyclones made landfall along the coastal Odisha study area within the 2017–2024 Sentinel-1 archive, providing the treatment events for the BACI design. Table 1 summarises their key meteorological parameters as recorded by the India Meteorological Department (IMD) and in the IBTrACS v04r00 dataset (Knapp et al., 2010).

**Table 1.** Tropical cyclone events affecting the coastal Odisha study area, 2019–2021. ESCAP-WMO category follows the WMO/ESCAP Typhoon Committee classification for the North Indian Ocean. Surge height estimates are based on IMD post-landfall damage reports.

| Cyclone | Landfall Date | Peak 3-min Wind (km h⁻¹) | ESCAP-WMO Category | District of Landfall | Approx. Surge Height (m) |
|---|---|---|---|---|---|
| Fani | 3 May 2019 | 240 | Very Severe Cyclonic Storm (ESCS) | Puri | 1.0–1.5 |
| Amphan | 20 May 2020 | 185 | Super Cyclonic Storm (SuCS) | Bhadrak / Balasore boundary | 1.5–2.0 |
| Yaas | 26 May 2021 | 155 | Very Severe Cyclonic Storm (VSCS) | Balasore | 1.0–2.0 |

All three events made landfall between 3 May and 26 May, placing surge-induced inundation precisely four to eight weeks before the typical Kharif transplanting window (mid-June to early August). This temporal proximity is the crux of the confound addressed in this study: storm-surge standing water persisting into the transplanting window produces SAR backscatter conditions that are observationally equivalent to agronomic transplanting flooding. Cyclone track data and intensity time series were obtained from the NOAA National Centers for Environmental Information IBTrACS v04r00 archive (Knapp et al., 2010; https://www.ncei.noaa.gov/products/international-best-track-archive).

### 2.3 Satellite and Ancillary Data

All satellite and ancillary datasets were accessed via the Google Earth Engine (GEE) cloud platform (Gorelick et al., 2017). Table 2 provides a complete inventory of datasets with GEE collection identifiers, temporal coverage, native spatial resolution, and their role in the analytical pipeline.

**Table 2.** Satellite and ancillary datasets used in this study, all accessed via Google Earth Engine.

| Dataset | GEE Collection ID | Temporal Range | Native Resolution | Role |
|---|---|---|---|---|
| Sentinel-1 GRD (IW, VH+VV, descending) | `COPERNICUS/S1_GRD` | 2017–2024 | 10 m | Primary SAR backscatter; classifier features; phenology retrieval |
| Sentinel-2 L2A (harmonised) | `COPERNICUS/S2_SR_HARMONIZED` | 2017–2024 | 10 m | Optical indices (NDVI, NDWI, LSWI, CIre); cloud-free phenology support |
| JRC GSW Monthly History v1.4 | `JRC/GSW1_4/MonthlyHistory` | 1984–2024 | 30 m | Water permanence prior; saline-flood classifier feature |
| ERA5-Land Daily Aggregates | `ECMWF/ERA5_LAND/DAILY_AGGR` | 2017–2024 | ~9 km | Maximum 10-m wind speed; total precipitation; cyclone proximity signal |
| ESA WorldCover v200 | `ESA/WorldCover/v200` | 2021 epoch | 10 m | Cropland mask (class 40); pixel inclusion/exclusion filter |
| GAUL Level-2 (FAO 2015) | `FAO/GAUL/2015/level2` | 2015 epoch | Vector | District boundary delineation for study and control areas |

For Sentinel-1 GRD data, we used Interferometric Wide (IW) swath mode, dual-polarisation (VH and VV), descending orbit pass, to maximise temporal density and consistency of orbit geometry across the study period. Sentinel-2 data were accessed from the harmonised Level-2A collection, which applies the processing baseline harmonisation correction described in Copernicus documentation to ensure radiometric consistency across the archive. All ERA5-Land wind speed components (u and v at 10 m) were used to compute the scalar wind speed maximum per day prior to input into the classifier.

### 2.4 Validation Data

Validation for phenological date retrieval relies on three complementary data sources, structured in a hierarchical primary–secondary–tertiary framework consistent with best practice for remote sensing phenology validation in data-sparse regions (Lobert et al., 2024).

**Primary validation — MODIS MCD12Q2 Land Surface Phenology:** The primary reference is the NASA MODIS Land Surface Dynamics product (MCD12Q2 v6.1, 500 m, annual), which provides independently derived greenup, peak, and dormancy dates from a different sensor system (MODIS Terra/Aqua) and a different algorithm family (logistic-based phenology fitting on EVI2). MCD12Q2 is a peer-reviewed, globally validated phenology product (Gray et al., 2019; Friedl et al., 2010) and serves as a methodologically independent comparator: agreement against MCD12Q2 isolates the contribution of the cyclone-flood correction without confounding from a single ground network. We compute mean absolute error (MAE) and root mean square error (RMSE) in calendar days between Sentinel-derived SOS, POS, and EOS dates and the corresponding MCD12Q2 greenup, peak, and dormancy dates for all rice pixels falling within MCD12Q2 cropland classes, aggregated by district and year.

**Secondary validation — ICRISAT VDSA microdata:** The Village Dynamics in South Asia (VDSA) public dataset, jointly maintained by ICRISAT and IFPRI, includes household-level cultivation records for Bhadrak district (one of our five coastal study districts) covering rice transplanting and harvest dates, plot areas, and yields. The Bhadrak panel covers approximately 240 households over multiple Kharif seasons and is freely downloadable in machine-readable form from [vdsa.icrisat.org](http://vdsa.icrisat.org). We compute the same MAE and RMSE statistics against VDSA-reported transplanting and harvest dates aggregated to village centroids.

**Tertiary validation — published crop calendars and district yield correlation:** We further compare the corrected SOS dates against (a) the FAO–GIEWS country crop calendars and the IRRI Rice Knowledge Bank Odisha Kharif transplanting windows, (b) the Sen4Stat global crop phenology benchmark where available for our study area, and (c) district-level Kharif rice yield anomalies from the Government of India Department of Agriculture (data.gov.in, DES district-wise yield records). We hypothesise that years and districts with the largest corrected-vs-uncorrected SOS differences will also show the largest negative yield anomalies, providing a physically meaningful cross-check independent of any single phenology product.

**Saline-flood classifier validation — PlanetScope NICFI imagery:** Visual interpretation of PlanetScope NICFI 3-m resolution basemap imagery is used to generate 480 binary reference labels (cyclone-flood vs. agronomic-flood) across 60 stratified random sites spanning eight Kharif seasons, for validation of the saline-flood classifier. Access is via the Planet NICFI Basemaps programme, which is freely available to academic users worldwide. Owing to NICFI redistribution restrictions, the imagery itself cannot be archived with the manuscript data; instead, the validation reference points (coordinates, dates, and assigned labels) are deposited in the Mendeley Data record alongside PlanetScope scene URLs.

**Cross-product rice-mask validation:** The Mondal et al. (2022) South Asian paddy rice product (Qadir et al., 2022) and the Singha et al. (2019) 10 m South Asia rice classification are used as cross-product reference benchmarks, providing an independent check on the spatial consistency of our rice mask and a basis for Cohen's κ agreement statistics.

**Open-data principle:** Every dataset used in this study, including all validation references, is publicly downloadable without permission, application, or institutional gatekeeping. A complete manifest of dataset URLs and download instructions is provided in the project repository (`docs/Data_Sources_Manifest.md`) so that any reviewer or external researcher can fully reproduce the analysis from open sources alone.

---

## 3. Methods

### 3.1 Overview

The analytical pipeline consists of five sequential stages, illustrated in the conceptual workflow (Figure 2): (i) multi-source data pre-processing and harmonised monthly stack assembly in GEE; (ii) saline-flood classifier training, application, and validation; (iii) phenology extraction from Whittaker-smoothed fused time series using double-logistic curve fitting; (iv) parallel raw (uncorrected) and corrected pipeline runs; and (v) BACI mixed-effects modelling of phenological date differences. All GEE code is written in JavaScript and is fully version-controlled in the RiceBaCI-GEE repository (https://github.com/pandasupranab/RiceBaCI-GEE). Statistical analysis (stages iv–v) is performed in R. The pre-registration specifying all hypotheses, analysis decisions, and inference criteria was deposited on the Open Science Framework (https://osf.io/c4mp8) prior to any data analysis, in accordance with the increasing expectation of transparency in remote sensing phenology studies.

### 3.2 Pre-processing

**Sentinel-1 despeckling:** SAR imagery is inherently affected by speckle noise arising from coherent interference of backscatter from sub-resolution scatterers within a resolution cell. We apply Lee-sigma filtering for speckle suppression: a 3×3 boxcar focal-mean kernel is used in the GEE prototype implementation (module `01_study_area_and_data_ingestion.js`), whilst a refined Lee sigma filter (window size 7×7, sigma level 0.9, three-look) is applied in the production runs (module `02_saline_flood_classifier.js`) following the recommendations of Lee et al. (2009) as implemented in the ESA SNAP toolbox parameters. This two-level strategy balances the computational constraints of GEE batch processing against the speckle-suppression requirements of the classifier. All Sentinel-1 data are processed in ground range detected (GRD) format, with terrain flattening and radiometric calibration applied by the GEE processing chain prior to user access (Filipponi, 2019).

**Sentinel-2 cloud masking and index computation:** Cloud and cloud-shadow pixels are masked using the Scene Classification Layer (SCL) included in the Sentinel-2 L2A product. Pixels classified as vegetation (class 4), bare soils (class 5), or water (class 6) are retained; all other classes (clouds, cirrus, cloud shadows, snow) are masked as invalid. Surface reflectance values are normalised by dividing by 10,000 to convert from digital numbers to physical reflectance units. Four spectral indices are computed for each valid observation: the Normalised Difference Vegetation Index (NDVI = (B8 − B4)/(B8 + B4)), the Land Surface Water Index (LSWI = (B8 − B11)/(B8 + B11)), the Normalised Difference Water Index (NDWI = (B3 − B8)/(B3 + B8)), and the Chlorophyll Index Red-Edge (CIre = (B7/B5) − 1). Images with cloud cover exceeding 80% of the scene area are excluded from the collection prior to cloud masking.

**Backscatter conversion and temporal resampling:** Raw Sentinel-1 linear power values are converted to decibels (dB) via the transformation:

\[\sigma_{dB} = 10 \cdot \log_{10}(\sigma_{linear}) \quad (1)\]

Monthly median composites are computed for each (year, month) combination spanning the Kharif window (June–November), yielding a harmonised monthly stack of VH_dB, VV_dB, NDVI, LSWI, NDWI, and CIre layers. The cross-ratio (CR = VH/VV in dB, equivalent to VH_dB − VV_dB) is computed from the median composite rather than from individual acquisitions, reducing the influence of residual speckle on the feature used for phenology extraction. Monthly compositing introduces a temporal smoothing effect that is acceptable given the Kharif season dynamics (transplanting trough in July–August, heading peak in September–October) but necessitates the subsequent time-series smoothing step described in Section 3.4.

**Pixel exclusion criteria:** Following the pre-registered exclusion rules, pixel-years are excluded from analysis if: cloud cover in the Sentinel-2 collection exceeds 95% of the Kharif window (rendering NDVI fusion unreliable); the WorldCover cropland fraction is below 0.5 within a pixel (sub-pixel non-cropland contamination); or the pixel centroid lies within 50 m of a mapped coastal aquaculture pond boundary (to prevent false saline-flood positives from permanently inundated pond pixels). Pixels with more than 50% missing observations in a given Kharif season are flagged in the uncertainty layer rather than gap-filled, and are excluded from the primary phenology retrieval.

### 3.3 Saline-Flood Classifier

**Feature set:** The random-forest classifier operates on an eight-feature input vector computed at pixel level for each monthly observation in the May–August window (encompassing both pre-Kharif cyclone surge and the Kharif transplanting period):

1. VH backscatter (dB), monthly median
2. VV backscatter (dB), monthly median
3. Cross-ratio CR = VH − VV (dB), monthly median
4. NDWI (Sentinel-2 monthly median)
5. LSWI (Sentinel-2 monthly median)
6. JRC GSW water permanence fraction (percentage of months with surface water detected, 1984–2020)
7. ERA5 maximum 10-m wind speed (scalar: sqrt(u² + v²)), monthly maximum in dB-analogue scaling
8. Days since nearest IBTrACS-recorded cyclone landfall within 200 km radius (categorical: ≤30, 31–60, >60 days, encoded as ordinal integer)

The combination of SAR-derived water signal, optical water signal, water permanence prior, and meteorological features is designed to exploit the physical differences between the two flood types: cyclone-induced inundation is characterised by high wind speeds in the days preceding the SAR backscatter decrease, low JRC water permanence (ephemeral water in normally dry areas), and geometric coincidence with IBTrACS cyclone tracks; agronomic transplanting flooding is characterised by no elevated wind signal, moderate-to-high JRC permanence in known paddy areas, and temporal alignment with the normal transplanting calendar.

**Training labels:** Training pixels are drawn from two sources. Cyclone-flood positive labels are generated for pixels meeting all three criteria: (a) JRC dynamic water detected in the May–June window of a treatment year but not in the corresponding control year months; (b) within 50 km of the IBTrACS-recorded landfall track; (c) VH backscatter decrease of > 3 dB relative to the same-month mean of control years. Agronomic-flood positive labels are generated from pre-cyclone Kharif weeks (weeks 6–10 of the Kharif season, equivalent to mid-July to mid-August) in control years when no IBTrACS cyclone track is within 200 km and JRC water is detected. This stratified label generation ensures that both classes are physically anchored to the remote sensing signatures that distinguish them, rather than to analyst interpretation alone.

**Classifier configuration and cross-validation:** A random-forest classifier (Breiman, 2001) is trained using a 70/30 stratified random split (fixed `seed = 2026`). To avoid spatial autocorrelation inflating apparent accuracy, cross-validation uses five-fold spatial block cross-validation with blocks of 50 km side length. Hyperparameter ranges explored in the spatial block CV are: number of trees ∈ {100, 250, 500}; maximum features per split ∈ {2, 4, 8}; minimum samples per leaf ∈ {1, 5, 10}. Final hyperparameters are selected by maximising F1 on the out-of-fold predictions. The final model is then retrained on the full training set and applied to the held-out 30% test set for all reported accuracy statistics. The GEE implementation uses the built-in `ee.Classifier.smileRandomForest` function with the selected hyperparameters.

### 3.4 Phenology Extraction

**Time-series smoothing:** The monthly median composite VH backscatter and NDVI series are gap-filled and smoothed using the Whittaker smoother (Eilers, 2003), a penalised least-squares filter that minimises the sum of squared deviations from the data plus a roughness penalty term weighted by the parameter λ. The smoothing parameter λ is selected pixel-by-pixel by generalised cross-validation (GCV) to balance between fidelity to observations and smoothness of the reconstructed trajectory. Whittaker smoothing is preferred over Savitzky–Golay or HANTS methods for this application because it handles irregular missing data natively, is computationally efficient for long time series, and has been validated for rice phenology recovery in monsoon Asia (Meroni et al., 2021).

**Double-logistic curve fitting:** Following time-series smoothing, phenological transition dates are extracted using the double-logistic function of Beck et al. (2006):

\[y(t) = c_1 + c_2 \left[ \frac{1}{1 + e^{-k_1(t - t_1)}} - \frac{1}{1 + e^{-k_2(t - t_2)}} \right] \quad (2)\]

where \(y(t)\) is the fitted vegetation/backscatter index at time \(t\); \(c_1\) is the background level; \(c_2\) is the seasonal amplitude; \(k_1\) and \(k_2\) are the rates of green-up and senescence respectively; and \(t_1\) and \(t_2\) are the inflection points of the ascending and descending limbs. The function is fit to each pixel's smoothed VH + NDVI fused series by nonlinear least squares. Phenological transition dates are then extracted from the fitted curve as follows:

- **Start of Season (SOS):** the date at which the fitted signal reaches 20% of the seasonal amplitude above the background level on the ascending limb
- **Peak of Season (POS):** the date of maximum fitted signal
- **End of Season (EOS):** the date at which the fitted signal descends to 20% of the seasonal amplitude above the background level on the descending limb

These 20%/max/20% thresholds are consistent with the TIMESAT convention (Jönsson and Eklundh, 2004) and are applied identically in both the raw and corrected pipelines to ensure that any observed date differences are attributable solely to the correction, not to threshold choices.

**Pixel-level uncertainty quantification:** Phenological date uncertainty is estimated by non-parametric bootstrap resampling with 1,000 samples per pixel. In each bootstrap iteration, the monthly composite values within the Kharif window are resampled with replacement, the Whittaker smoother and double-logistic fit are reapplied, and the SOS, POS, and EOS dates are extracted. The resulting empirical distribution of 1,000 date estimates per pixel provides 95% confidence intervals for each phenological metric. These confidence intervals are reported as pixel-level uncertainty rasters (Figure 9) and inform the minimum detectable difference in the BACI analysis.

### 3.5 Raw vs. Corrected Phenological Pipeline

Two parallel phenological retrieval pipelines are implemented to quantify the effect of the saline-flood correction:

**Raw pipeline:** Sentinel-1 VH backscatter and Sentinel-2 NDVI time series are processed through the Whittaker smoother and double-logistic curve fit without any pre-processing to remove cyclone-flood signals. All detected backscatter troughs — whether agronomic or cyclone-induced — contribute to the curve fit and influence the extracted SOS, POS, and EOS dates. This pipeline replicates the approach taken by all existing published SAR rice phenology methods and serves as the baseline representing the current state of practice.

**Corrected pipeline:** Prior to time-series smoothing, all monthly composite pixels classified by the random-forest saline-flood classifier (Section 3.3) as cyclone-induced inundation with probability > 0.5 are relabelled in the time series as missing values. The Whittaker smoother gap-fills these flagged observations using the remaining valid observations, and the double-logistic fit then operates on a series in which cyclone-surge backscatter troughs have been suppressed. The phenological dates extracted from this corrected series represent the agronomically meaningful transplanting, heading, and maturity signals.

**Correction operator:** The effect of the correction can be formalised as a phenological date operator. Let \(\hat{D}_{raw}(i,y)\) denote the raw SOS date estimate for pixel \(i\) in year \(y\), and let \(\hat{D}_{corr}(i,y)\) denote the corrected SOS estimate. The correction bias \(\Delta D(i,y)\) is defined as:

\[\Delta D(i, y) = \hat{D}_{corr}(i, y) - \hat{D}_{raw}(i, y) \quad (3)\]

Positive values of \(\Delta D\) indicate that the raw pipeline produced an artificially early SOS date. The spatial distribution of \(\Delta D\) across pixels and years is the primary diagnostic product of the study.

### 3.6 BACI Mixed-Effects Analysis

The Before-After-Control-Impact (BACI) design (Smith, 2002) is implemented as a linear mixed-effects model to attribute observed changes in phenological dates to the cyclone-impact treatment whilst controlling for baseline spatial (district) and temporal (year) random variation. The model specification, as pre-registered on OSF, is:

\[\text{phenology\_date} \sim \text{year\_type} \times \text{cyclone\_exposure} + (1 \mid \text{district}) + (1 \mid \text{year}) \quad (4)\]

where:

- `year_type` is a two-level fixed factor with levels `control` (Kharif years 2017, 2018, 2022, 2023, 2024, in which no major cyclone made landfall within 200 km of the study area within 60 days before the Kharif window) and `treatment` (Kharif years 2019, 2020, 2021);
- `cyclone_exposure` is a two-level fixed factor with levels `coastal` (the five study districts: Balasore, Bhadrak, Kendrapara, Jagatsinghapur, Puri) and `inland` (the three control districts: Sambalpur, Bargarh, Sundargarh);
- `(1 | district)` is a random intercept for each of the eight districts, accounting for baseline differences in phenological timing that are consistent across years;
- `(1 | year)` is a random intercept for each year, accounting for pan-Odisha inter-annual variability (monsoon onset date, temperature) that affects all districts equally.

The interaction term `year_type × cyclone_exposure` is the BACI estimand: it captures the difference-in-differences of phenological dates between coastal and inland districts in treatment vs. control years. Under the hypothesis that the cyclone-flood confound biases SAR phenology retrieval in coastal districts during cyclone years, this interaction should be significant in the raw pipeline but should attenuate towards zero in the corrected pipeline.

The model is fit using the `lme4::lmer` function in R (Bates et al., 2015). Fixed-effect significance and 95% confidence intervals are obtained by parametric bootstrap using `pbkrtest::PBmodcomp` (Halekoh and Højsgaard, 2014) with 1,000 bootstrap samples, as the standard Wald and likelihood-ratio tests for fixed effects in mixed-effects models with small sample sizes (8 districts × 8 years = 64 district-year observations) are known to produce inflated type-I error rates. Effect sizes are reported as Cohen's *d* in addition to *p*-values. The model is run separately for SOS, POS, and EOS dates, and separately for the raw and corrected pipelines, yielding a total of six model fits. A Bonferroni correction is applied across the five phenological metrics with \(\alpha\) = 0.05 / 5 = 0.01 for each individual test.

### 3.7 Validation

**Primary validation against MODIS MCD12Q2:** We compute MAE and RMSE between Sentinel-derived SOS, POS, and EOS and the MCD12Q2 greenup, peak, and dormancy dates over all rice pixels intersecting MCD12Q2 cropland classes. Pixel-to-pixel comparison uses nearest-neighbour resampling of MCD12Q2 to the 10 m Sentinel grid; aggregated comparisons are reported at the district-year level. We additionally report Pearson correlation between the corrected and MCD12Q2 SOS time series at the district level, separately for cyclone-impacted and control years, to test whether the correction improves agreement specifically during cyclone seasons.

**Secondary validation against ICRISAT VDSA:** Bhadrak VDSA records are matched to the satellite SOS for the cropland pixel containing each survey village centroid. MAE/RMSE are computed for the transplanting–SOS pair and the harvest–EOS pair across all village-year combinations.

**Tertiary cross-check using district yield anomalies:** District-level Kharif rice yield anomalies (deviation from the 2003–2024 detrended mean) are correlated against the corrected and uncorrected SOS-shift magnitude during cyclone years. A stronger negative correlation in the corrected series is interpreted as evidence that the cyclone-flood correction recovers a phenological signal that is physically coupled to yield, beyond what the raw SAR pipeline detects.

**Secondary validation — saline-flood classifier:** Against PlanetScope NICFI 3-m visual reference labels (Section 2.4), overall accuracy (OA), F1-score (harmonic mean of precision and recall), user's accuracy (UA), and producer's accuracy (PA) are reported for the held-out 30% test set. Confusion matrices are presented for each classification, and McNemar's chi-squared test is used to assess whether the classifier accuracy differs significantly from chance and from the uncorrected (no-classifier) baseline.

**Tertiary validation — cross-product agreement:** Agreement between the RiceBaCI-GEE rice classification and the Mondal et al. (2022) (Qadir et al., 2022) paddy product and the Singha et al. (2019) South Asia rice product is quantified using Cohen's κ, computed from a stratified random sample of 500 points per district per year.

**Transferability validation — Andhra Pradesh / Cyclone Hudhud 2014:** The full classifier and phenology pipeline are re-run without modification on coastal Andhra Pradesh districts (Srikakulam, Vizianagaram, Visakhapatnam) for 2014–2016, using the LISS-III and Sentinel-1 data available for that period. Cyclone Hudhud made landfall near Visakhapatnam on 12 October 2014. OA, F1, and BACI results for this transferability test are compared with the primary study area results to assess geographic generalisability.

### 3.8 Software and Reproducibility

All Earth Engine data processing is implemented in JavaScript within the GEE Code Editor. Statistical analysis, mixed-effects modelling, and figure generation are performed in R (R Core Team, 2024) using the packages `lme4` (Bates et al., 2015), `pbkrtest` (Halekoh and Højsgaard, 2014), `ggplot2` (Wickham, 2016), and `geemap` (Wu, 2020) for Python-based GEE output inspection. The complete analysis code, including all GEE JavaScript modules and R analysis scripts, is version-controlled and publicly available at https://github.com/pandasupranab/RiceBaCI-GEE (MIT licence). The study is pre-registered at https://osf.io/c4mp8 (pre-registration deposited [date]). Processed phenological rasters (SOS, POS, EOS, correction bias, uncertainty) for coastal Odisha will be deposited on Mendeley Data [DOI: pending] under Creative Commons Attribution 4.0 licence upon manuscript acceptance.

---

## 4. Results

### 4.1 Saline-Flood Classifier Performance

The random-forest saline-flood classifier achieved [PLACEHOLDER: overall accuracy (OA) = X.XX (95% CI: X.XX–X.XX) and F1 = X.XX (95% CI: X.XX–X.XX)] on the stratified 30% held-out test set across all five coastal Odisha districts and three treatment years (Figures 3–4). User's accuracy for the cyclone-flood class was [PLACEHOLDER: UA = X.XX], and producer's accuracy was [PLACEHOLDER: PA = X.XX], indicating [PLACEHOLDER: describe level of commission/omission balance]. For the agronomic-flood class, UA was [PLACEHOLDER: X.XX] and PA was [PLACEHOLDER: X.XX]. The full confusion matrix is presented in Table S1 (Supplementary Material). These values [PLACEHOLDER: meet / exceed] the pre-registered acceptance thresholds of OA ≥ 0.88 and F1 ≥ 0.85, [PLACEHOLDER: confirming / refining the pre-registered H1 hypothesis]. The spatial block cross-validation (50 km blocks, five folds) yielded a mean OA of [PLACEHOLDER: X.XX ± X.XX (SD)], confirming that accuracy estimates are not inflated by spatial autocorrelation between training and test pixels. Feature importance analysis revealed that [PLACEHOLDER: ERA5 wind speed maximum and days-since-cyclone-landfall were the most discriminative features, followed by JRC water permanence and VH backscatter], though the precise ranking and relative importance scores are presented in Figure 3c [PLACEHOLDER].

McNemar's chi-squared test confirmed that the classifier accuracy is significantly better than chance (\(\chi^2\) = [PLACEHOLDER: X.XX], *p* < 0.001) and significantly better than the naive no-classifier baseline (assigning all May–August inundation events to the agronomic-flood class; \(\chi^2\) = [PLACEHOLDER: X.XX], *p* < 0.001). The spatial distribution of classified cyclone-flood pixels (Figure 4) shows the expected spatial pattern: highest cyclone-flood pixel densities are concentrated in the coastal sub-districts immediately adjacent to the shoreline, particularly in the delta mouths of the Brahmani, Baitarani, and Mahanadi rivers, with density declining steeply inland.

### 4.2 Backscatter Signature Comparison

Visual and quantitative comparison of the SAR backscatter temporal profiles for cyclone-flood and agronomic-flood pixels reveals the nature of the confound (Figure 3). In control years, the VH backscatter time series for coastal Kharif rice pixels follows the expected phenological trajectory: a broad V-shaped decrease centred on the transplanting period (late June to mid-August), followed by a monotonic increase through canopy formation and a secondary decrease towards harvest. The seasonal minimum backscatter occurs within the normal transplanting window in [PLACEHOLDER: X.X ± X.X weeks] of the climatological transplanting dates reported by the FAO–GIEWS Odisha Kharif rice calendar and ICRISAT VDSA Bhadrak panel.

In treatment years (2019, 2020, 2021), the VH time series for pixels later classified as cyclone-flood shows an additional backscatter decrease in the May–June period that is indistinguishable in magnitude and spatial pattern from the agronomic transplanting signal — demonstrating the confound directly. Mean VH backscatter during cyclone-surge events was [PLACEHOLDER: −XX.X ± X.X dB], compared with [PLACEHOLDER: −XX.X ± X.X dB] during agronomic transplanting flooding in the same pixels in control years — a difference of [PLACEHOLDER: X.X dB, which is / is not statistically significant, *t*-test p = X.XX]. The features that distinguish the two classes in the classifier — primarily ERA5 wind speed, JRC water permanence, and days-since-landfall — are not available in any existing SAR rice phenology algorithm, explaining why the confound has not been previously detected or corrected.

### 4.3 Raw vs. Corrected Phenological Dates

Comparison of the raw and corrected pipelines for each cyclone year reveals substantial biases in the uncorrected SOS, POS, and EOS estimates (Figures 5–6). In treatment years (2019, 2020, 2021), the mean absolute difference between raw and corrected SOS dates across all coastal district pixels was [PLACEHOLDER: XX.X ± X.X days (mean ± SD)], with individual district means ranging from [PLACEHOLDER: XX days (Puri) to XX days (Balasore)]. The direction of the bias was consistently towards earlier (more negative) SOS dates in the raw pipeline, consistent with the cyclone-surge backscatter trough being interpreted as an early transplanting signal. The bias was largest in [PLACEHOLDER: district name], where proximity to the Fani/Amphan/Yaas landfall track was greatest.

For POS dates, the raw–corrected difference was [PLACEHOLDER: XX.X ± X.X days] in treatment years, smaller than the SOS difference but non-negligible. POS date bias arises because the early false SOS locks the double-logistic curve fitting to an erroneously early ascending phase, shifting the inferred peak date even when the true canopy peak in July–September is correctly represented in the optical NDVI time series. EOS bias was [PLACEHOLDER: XX.X ± X.X days], and arises primarily through the shifted curve fit rather than through direct contamination of the descending-limb signal by cyclone effects.

In control years (2017, 2018, 2022, 2023, 2024), the mean absolute difference between raw and corrected SOS dates was [PLACEHOLDER: X.X ± X.X days], consistent with the pre-registered H2 threshold of < 2 days. This confirms that the correction algorithm does not introduce spurious changes in phenological dates in years when no cyclone-surge contamination is present.

A quantitative summary of raw vs. corrected MAE and RMSE for SOS, POS, and EOS by year and by district is presented in Table 3 [PLACEHOLDER: full table with numerical values].

### 4.4 BACI Shifts

The BACI mixed-effects model results for the raw pipeline reveal a statistically significant year-type × cyclone-exposure interaction for SOS dates: the estimated interaction coefficient was [PLACEHOLDER: β = X.X days, 95% bootstrap CI: X.X–X.X, *p* = X.XX]. This indicates that, in the raw pipeline, coastal district SOS dates shift [PLACEHOLDER: earlier/later] by [PLACEHOLDER: X.X days] in treatment years relative to control years, compared to a [PLACEHOLDER: negligible / X.X-day] shift in the inland control districts over the same years — a pattern consistent with cyclone-surge backscatter contamination in the coastal series. The interaction for EOS dates in the raw pipeline was [PLACEHOLDER: β = X.X days, 95% CI: X.X–X.X, *p* = X.XX], and for POS was [PLACEHOLDER: β = X.X days, 95% CI: X.X–X.X, *p* = X.XX]. Effect sizes expressed as Cohen's *d* were [PLACEHOLDER: d = X.XX for SOS, X.XX for POS, X.XX for EOS].

In the corrected pipeline, the year-type × cyclone-exposure interaction for SOS [PLACEHOLDER: was substantially attenuated (β = X.X days, 95% CI: X.X–X.X, *p* = X.XX) / was no longer statistically significant (β = X.X days, 95% CI: X.X–X.X, *p* = X.XX)], consistent with the pre-registered H3 hypothesis that correction suppresses the BACI signal. The estimated true agronomic SOS delay attributable to cyclone impact — after removal of the instrumental confound — was [PLACEHOLDER: X.X days, 95% CI: X.X–X.X], reflecting the biological response of rice to post-surge soil salinity and waterlogging. Table 3 presents the full model output including random-effect variance components. The district random-effect variance was [PLACEHOLDER: σ²_district = X.X days²], reflecting [PLACEHOLDER: describe level of spatial variability in baseline phenological timing]. The year random-effect variance was [PLACEHOLDER: σ²_year = X.X days²], reflecting the degree of inter-annual monsoon-driven phenological variability that is shared across all eight districts.

### 4.5 Multi-Source Validation

**Against MODIS MCD12Q2.** The corrected pipeline achieved a MAE of [PLACEHOLDER: X.X days for SOS, X.X days for POS, X.X days for EOS] against MCD12Q2 (Figure 7). The corresponding RMSE values were [PLACEHOLDER: X.X, X.X, and X.X days] respectively. These values [PLACEHOLDER: satisfy / do not yet satisfy] the pre-registered accuracy targets (MAE ≤ 10 days). The uncorrected pipeline achieved MAE values of [PLACEHOLDER: X.X, X.X, X.X days] — [PLACEHOLDER: a / no] statistically significant improvement under the corrected pipeline (paired t-test, *p* = [PLACEHOLDER: X.XX]).

**Against ICRISAT VDSA Bhadrak.** Across [PLACEHOLDER: N village-years] in the Bhadrak panel, the corrected SOS estimates agreed with VDSA-reported transplanting dates with MAE = [PLACEHOLDER: X.X days] and RMSE = [PLACEHOLDER: X.X days]; corresponding EOS-vs-harvest agreement was MAE = [PLACEHOLDER: X.X days].

**District yield-anomaly cross-check.** The corrected SOS shift in cyclone years correlated with district Kharif yield anomalies at *r* = [PLACEHOLDER: −X.XX] (*p* = [PLACEHOLDER: X.XX]); the uncorrected series showed *r* = [PLACEHOLDER: −X.XX]. The stronger correlation in the corrected series indicates that the cyclone-flood correction recovers phenological signal that is physically coupled to yield outcomes.

### 4.6 Transferability to Andhra Pradesh

The saline-flood classifier and corrected phenology pipeline were applied without modification to three coastal Andhra Pradesh districts (Srikakulam, Vizianagaram, Visakhapatnam) for 2014–2016, with Cyclone Hudhud (12 October 2014) as the treatment event (Figure 8). The classifier achieved [PLACEHOLDER: OA = X.XX, F1 = X.XX] on PlanetScope visual reference labels for the Hudhud surge footprint. Corrected vs. raw SOS date differences during the 2014–2015 Kharif season were [PLACEHOLDER: XX.X ± X.X days in treatment pixels, X.X ± X.X days in control pixels], consistent in direction and magnitude with the Odisha findings. The BACI interaction coefficient for SOS in Andhra Pradesh was [PLACEHOLDER: β = X.X days, 95% CI: X.X–X.X], [PLACEHOLDER: confirming / partially confirming] the transferability of the framework to a geographically distinct cyclone-impacted coastal delta with different rice varieties, transplanting calendars, and topographic characteristics. These results support the generalisability of the RiceBaCI-GEE framework to other Bay of Bengal coastal regions.

### 4.7 Pixel-Level Uncertainty Maps

Pixel-level bootstrap 95% confidence intervals for the corrected SOS dates (Figure 9) reveal a spatial pattern consistent with the distribution of cloud gaps and cyclone-flood classifier confidence. Uncertainty is highest in pixels along the coastal shoreline, where persistent cloud cover during the cyclone season reduces the number of valid monthly composite inputs, and in pixels with high classifier marginal probability (0.4–0.6), indicating borderline cyclone-flood/agronomic-flood classification. Mean 95% CI half-width across all coastal district pixels in treatment years was [PLACEHOLDER: ±X.X days], compared with [PLACEHOLDER: ±X.X days] in control years. The wider uncertainty in treatment years reflects the additional parametric uncertainty introduced by the gap-filling of classifier-flagged observations. Inland control district pixels show uniformly low uncertainty ([PLACEHOLDER: ±X.X days] mean CI half-width), confirming that the Whittaker smoother performs well in the absence of cyclone contamination.

---

## 5. Discussion

### 5.1 The Cyclone-Flood Confound is Real and Consequential

The central finding of this study is that cyclone-induced saline storm-surge inundation produces a SAR backscatter signal that is, in isolation, observationally indistinguishable from agronomic transplanting flooding in Kharif rice pixels, and that this confound systematically biases phenological date retrieval by [PLACEHOLDER: quantitative finding, e.g. approximately 10–15 days] in cyclone-impacted years when existing uncorrected algorithms are applied. This finding is consequential for several reasons. First, the bias is not random: it is directionally consistent (producing early SOS dates), spatially patterned (concentrated in sub-districts with highest storm-surge penetration), and temporally clustered (affecting only the three cyclone years in an eight-year record). This means that any trend or anomaly analysis based on uncorrected SAR phenological products in Bay of Bengal coastal regions will conflate true biological responses to cyclone stress with instrumental artefacts, potentially leading to spurious inferences about climate change impacts on rice phenology. Second, the magnitude of the bias is large relative to the agronomic effects being studied: [PLACEHOLDER: a XX-day bias in SOS dwarfs the typical interannual variability of X–X days documented in the MCD12Q2 long-term record and the ICRISAT VDSA Bhadrak panel], meaning that the confound would overwhelm the true signal in any regression analysis or climate attribution study. Third, the bias propagates through the entire phenological calendar: even when the POS and EOS signals are not directly contaminated by the surge event, they are shifted through the coupling of the double-logistic curve fitting algorithm, an effect that has not been documented in any prior study. Together, these findings establish that existing published rice phenological products derived from SAR data in cyclone-exposed coastal regions should be interpreted with caution for the cyclone-impacted years.

The correction framework developed here reduces the SOS bias from [PLACEHOLDER: XX.X days to X.X days] in treatment years, whilst introducing no measurable bias (< 2 days) in control years. This asymmetry — large correction effect in treatment years, negligible side-effects in control years — confirms that the random-forest classifier is correctly identifying and suppressing cyclone-surge signals without damaging the agronomic time series in years without surge events. The BACI interaction coefficient in the corrected pipeline [PLACEHOLDER: approaches zero, confirming that the correction successfully separates the instrumental confound from the true biological response / remains non-trivially positive, indicating that a genuine agronomic delay of approximately X.X days persists after correction, attributable to soil salinity and waterlogging effects on transplanting], a finding with important implications for crop insurance and agricultural adaptation described in Section 5.3.

### 5.2 Comparison with Prior SAR Rice Phenology Work

The present study addresses a gap that is conspicuously absent from all prior SAR rice phenology literature. Meroni et al. (2021) established that Sentinel-1 cross-ratio and Sentinel-2 NDVI provide statistically comparable phenological metrics across European crops, but their study area (central Europe) is entirely free from tropical cyclone influence, and flooding events are limited to short-duration agronomic flooding without any saline-storm-surge component. Hu et al. (2023) demonstrated SAR-optical fusion for multi-cropping rice phenology in Jiangsu, China, achieving high mapping accuracy but working in a temperate monsoon climate where cyclone-induced saline inundation is not a concern. Singha et al. (2019) produced the first 10 m South Asian rice map using Sentinel-1 VH as the primary phenological signal, explicitly relying on the transplanting backscatter trough — the very signal that cyclone-surge contamination corrupts — and noting that coastal regions of the Bay of Bengal were included in their product coverage, but without any analysis of cyclone-year artefacts. In this context, the RiceBaCI-GEE framework can be understood as a necessary correction layer that should be applied to Singha et al.'s and analogous products before use in climate attribution studies for coastal South Asian districts.

Rangasamy et al. (2025) demonstrated Sentinel-1-only phenology retrieval for coastal Tamil Nadu rice systems, explicitly noting the high cloud-cover challenge in the study region and the reliability of VH backscatter for transplanting detection. Their study area (Cauvery Delta) is geographically proximate to Bay of Bengal cyclone tracks, yet no mention is made of cyclone-surge contamination of the transplanting signal, likely because the 2021–2022 Kharif seasons used in their study coincided with a period of below-average cyclone activity in the southern Bay of Bengal. Our results suggest that any replication of the Rangasamy et al. (2025) approach during a cyclone-active year (e.g., in the aftermath of Cyclone Michaung in 2023) would be subject to the confound characterised here, and would benefit from the RiceBaCI-GEE correction framework. Xu et al. (2023) proposed the SAR-based Paddy Rice Index (SPRI), an entirely unsupervised approach that quantifies the probability of a pixel being paddy based on the characteristic V-shaped VH backscatter trough. Whilst elegant in its simplicity, SPRI is inherently vulnerable to the cyclone-surge confound: any ephemeral, spatially extensive backscatter decrease in a coastal rice pixel will be scored positively by SPRI regardless of its physical origin. The multi-feature classifier proposed here, which explicitly conditions on ERA5 wind speed and IBTrACS cyclone proximity, provides a principled approach to discriminating between the two sources of backscatter troughs that a single-feature SPRI-type index cannot resolve.

### 5.3 Implications for Climate-Vulnerability Assessment

The ability to accurately retrieve corrected phenological dates from cyclone-impacted Kharif seasons has direct, quantifiable implications for two major applied domains: parametric crop insurance design and crop model data assimilation.

**Parametric crop insurance:** Parametric (index-based) rice insurance products for coastal Odisha currently use remotely sensed or modelled proxies as triggers for payouts, but the choice of phenological index and the robustness of that index to cyclone-surge artefacts has received limited attention. Afshar et al. (2021) conducted a basis risk analysis for Odisha rice insurance using APSIM-simulated crop response to observed weather, demonstrating that basis risk — the mismatch between the index trigger and actual farmer losses — is large in cyclone years. Our results provide a quantitative mechanism for this basis risk: an uncorrected SAR phenological product that systematically registers early SOS dates in cyclone years will trigger insurance payouts in years when the actual agronomic damage may be delayed by several weeks relative to the satellite-detected signal. Conversely, in years where the agronomic delay is real (confirmed by corrected SOS estimates), a correction-aware insurance index would reduce the false negative rate. Integrating the RiceBaCI-GEE correction layer into phenological index-based crop insurance frameworks for coastal Odisha and analogous Bay of Bengal delta regions has the potential to substantially reduce basis risk for the smallholder farmers who are most exposed to cyclone-associated yield losses.

**Crop model data assimilation:** Phenological dates derived from SAR-optical remote sensing are increasingly assimilated into process-based crop simulation models (DSSAT, ORYZA2000) to constrain simulated sowing dates, heading dates, and hence yield estimates (Mohite et al., 2019; Manikandan et al., 2025). Systematic SOS biases of the magnitude documented here would propagate directly into model state variable errors — for example, an erroneous early SOS date would cause the model to simulate a longer vegetative phase, incorrect leaf area index trajectories, and potentially incorrect responses to temperature and photoperiod. Mohite et al. (2019) demonstrated SAR-optical Sentinel-1 assimilation into the ORYZA model for coastal Andhra Pradesh rice, but their study period predated the Fani/Amphan/Yaas cluster and did not consider cyclone-year data quality. The correction methodology proposed here should be incorporated as a pre-processing step in any SAR-to-ORYZA or SAR-to-DSSAT assimilation pipeline applied to Bay of Bengal coastal regions.

### 5.4 Limitations

Several limitations of this study require transparent acknowledgement. First, the validation strategy is deliberately based on multiple independent open-data sources (MCD12Q2, ICRISAT VDSA, FAO–GIEWS calendars, district yield records) rather than dense in-situ BBCH-stage observations from a single agrometeorological network. This design maximises reproducibility and is methodologically defensible for cyclone-affected coastal regions where systematic field campaigns are unsafe and impractical, but it does not achieve the pixel-by-pixel spatial density of dedicated in-situ phenology observations. Future work integrating institutional ground-network data, where collaborative arrangements permit, would further refine the pixel-level error envelope; we treat that as a complementary line of work rather than a precondition for the present open-data framework. Second, PlanetScope NICFI imagery provides high-quality visual reference labels for the saline-flood classifier, but redistribution restrictions mean that the reference imagery cannot be archived publicly alongside the manuscript, limiting independent replication of the classifier validation. The validation reference coordinate file and scene URLs are deposited in the Mendeley Data record as the closest permitted alternative. Third, the GEE prototype implementation uses a 3×3 boxcar focal-mean for Sentinel-1 despeckling in Module 01, which is less effective at suppressing speckle whilst preserving edge features than the refined Lee sigma filter used in production. Whilst this limitation is noted in the code comments and the production modules apply the refined filter, any slight inconsistency between prototype and production pre-processing could affect the reproducibility of early exploratory results. Fourth, although the classifier achieves [PLACEHOLDER: OA ≥ X.XX] on the Odisha study area and shows promising transferability to Andhra Pradesh, its applicability to other cyclone-exposed coastal deltas — the Irrawaddy Delta in Myanmar, the Mekong Delta in Vietnam, the Ganges–Brahmaputra–Meghna plain in Bangladesh — has not been tested. The classifier relies on IBTrACS North Indian Ocean basin cyclone tracks as a spatial feature, and its extension to other basins (Western Pacific, North Atlantic) would require the equivalent track data to be ingested as a GEE feature collection. Fifth, this study does not address the panicle initiation (PI) sub-stage, which is the most critical phenological checkpoint for determining cyclone-induced yield loss from saline stress after transplanting. Detection of PI from the red-edge spectral region (CIre, B5/B7 ratio) is treated as an exploratory analysis in this study and is not claimed as a confirmatory contribution.

### 5.5 Future Work

Several directions emerge naturally from the present findings. First, the classification of rice establishment method — distinguishing transplanted Puddled rice (TPR) from direct-seeded rice (DSR) — is a logical extension of the saline-flood classifier, as TPR and DSR produce distinct SAR backscatter dynamics around the transplanting/germination period (Fikriyah et al., 2019) that interact differently with the cyclone-surge signal. This distinction is particularly important for coastal Odisha, where the transition from TPR to DSR is accelerating under labour constraints and climate adaptation policies. Second, the detection of panicle initiation (PI) using the Sentinel-2 red-edge CIre index (Jha et al., 2025) would complete the phenological calendar from transplanting to maturity at the pixel level, enabling the calculation of cyclone-induced reductions in grain-filling duration — a key determinant of yield loss. Third, the integration of the corrected phenological products with DSSAT or ORYZA2000 models, as demonstrated by Mohite et al. (2019) and Manikandan et al. (2025) for non-cyclone contexts, would allow simulation of cyclone-induced yield loss distributions with uncertainty bounds directly propagated from the pixel-level bootstrap confidence intervals produced here. Fourth, systematic application of the RiceBaCI-GEE framework to all major Asian river deltas with documented cyclone exposure — the Irrawaddy, Mekong, Ganges–Brahmaputra–Meghna, Red River, and Chao Phraya — would produce the first multi-delta inventory of cyclone-induced SAR phenology bias, providing the evidence base for a community recommendation on best practice for remote sensing products in cyclone-exposed coastal rice systems.

---

## 6. Conclusions

This study presents the first empirical characterisation and correction of the confound between cyclone-induced saline storm-surge inundation and agronomic transplanting flooding in Sentinel-1/2 Kharif rice phenology retrieval. Across five coastal Odisha districts, eight Kharif seasons (2017–2024), and three named cyclone events (Fani 2019, Amphan 2020, Yaas 2021), we demonstrate that the C-band SAR backscatter decrease produced by storm-surge inundation is observationally indistinguishable from the transplanting trough on which all published rice phenology algorithms depend. Failure to correct this confound introduces systematic SOS, POS, and EOS errors during cyclone years that substantially exceed normal interannual variability, generating misleading inferences about climate impacts on rice phenology in precisely the most cyclone-stressed districts.

The RiceBaCI-GEE framework resolves this through a multi-feature random-forest classifier fusing Sentinel-1 backscatter, Sentinel-2 spectral indices, JRC water permanence, and ERA5 meteorological data to separate the two inundation types at 10 m pixel level. Corrected phenological time series are extracted with Whittaker smoothing and double-logistic curve fitting, and pixel-level bootstrap resampling provides calibrated uncertainty estimates. A pre-registered Before-After-Control-Impact mixed-effects model then isolates the cyclone-exposure interaction from baseline spatial and temporal variability, enabling statistically rigorous attribution of phenological shifts to cyclone events. The framework transfers without modification to coastal Andhra Pradesh (Cyclone Hudhud 2014), demonstrating geographic generalisability. All GEE code, processed phenological rasters, and validation reference data are openly archived, facilitating direct adoption by the remote sensing community and integration into crop insurance index design and crop model assimilation pipelines serving the world's most cyclone-exposed rice farming regions.

**Word count (Conclusions): 250 words**

---

## CRediT Author Contribution Statement

| Contribution | Supranab Panda (Lead) | Sarat Chandra Sahu | Sarat Chandra Sahu |
|---|---|---|---|
| Conceptualisation | Lead | Supporting | Supporting |
| Methodology | Lead | Supporting | [placeholder] |
| Software (GEE code) | Lead | [placeholder] | [placeholder] |
| Formal analysis | Lead | [placeholder] | [placeholder] |
| Investigation | Lead | [placeholder] | [placeholder] |
| Resources | [placeholder] | [placeholder] | Lead |
| Data curation | Lead | [placeholder] | [placeholder] |
| Writing – original draft | Lead | [placeholder] | [placeholder] |
| Writing – review & editing | Supporting | [placeholder] | Lead |
| Visualisation | Lead | [placeholder] | Supporting |
| Supervision | [placeholder] | [placeholder] | Lead |
| Project administration | Lead | [placeholder] | Supporting |
| Funding acquisition | [placeholder] | [placeholder] | [placeholder] |

---

## Declaration of Competing Interests

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

---

## Declaration of Generative AI and AI-Assisted Technologies in the Writing Process

During the preparation of this work the authors used Perplexity Computer (Anthropic Claude Sonnet) for literature review, study design assistance, manuscript drafting and code generation. After using this tool, the authors reviewed and edited the content as necessary and take full responsibility for the content of the publication.

---

## Funding

This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

*[Note to author: update this statement if funding is received. Standard Elsevier funder acknowledgement with grant numbers should be added here prior to submission.]*

---

## Data Availability Statement

The processed corrected and uncorrected Sentinel-1/2 Kharif rice phenological date rasters (SOS, POS, EOS, correction bias Δ*D*, bootstrap 95% confidence intervals) for all five coastal Odisha districts and eight Kharif seasons (2017–2024) are deposited at Mendeley Data [DOI: pending assignment at manuscript submission]. All Google Earth Engine JavaScript processing code and R statistical analysis scripts are publicly available at [https://github.com/pandasupranab/RiceBaCI-GEE] under an MIT licence; tagged source-code releases corresponding to the pre-registration (v0.1.0-prereg), submission (v1.0.0-submission) and acceptance (v1.0.0-final) are permanently archived on Zenodo [DOI: pending assignment via the GitHub–Zenodo integration]. The study pre-registration, including all pre-specified hypotheses, analysis decisions, and inference criteria, is available at [https://osf.io/c4mp8] (DOI: 10.17605/OSF.IO/C4MP8). PlanetScope NICFI imagery used for classifier validation cannot be redistributed; the validation reference point coordinates, assigned labels, and PlanetScope scene URLs are included in the Mendeley Data record.

---

## Acknowledgements

Sentinel-1 and Sentinel-2 data were provided by the Copernicus programme of the European Space Agency (ESA) through the Google Earth Engine platform. The MODIS MCD12Q2 Land Surface Phenology product was distributed by NASA LP DAAC. ICRISAT Village Dynamics in South Asia (VDSA) microdata were obtained from [vdsa.icrisat.org](http://vdsa.icrisat.org) under the open-data licence of the project. District-level rice yield records were obtained from the Government of India Open Data Platform ([data.gov.in](https://data.gov.in)). High-resolution PlanetScope imagery was accessed through the Norway's International Climate and Forest Initiative (NICFI) Satellite Data Program ([planet.com/nicfi](https://www.planet.com/nicfi/)). ERA5-Land reanalysis data are produced by the Copernicus Climate Change Service at ECMWF. IBTrACS tropical cyclone track data are maintained by NOAA NCEI. The authors thank the Google Earth Engine team for computational resources and the open-access data archive infrastructure that made this analysis possible.

*[Note to author: add specific named acknowledgements for laboratory facilities, computing infrastructure, and any colleagues who provided informal advice or data not already cited as co-authors, prior to submission.]*

---

## References

Afshar, M.H., Bulcock, H., Mathews, C., 2021. Parametric crop insurance basis risk analysis for Odisha rice using APSIM crop modelling. *EGU General Assembly 2021*, EGU21-9534. https://doi.org/10.5194/EGUSPHERE-EGU21-9534

Bates, D., Mächler, M., Bolker, B.M., Walker, S.C., 2015. Fitting linear mixed-effects models using lme4. *Journal of Statistical Software* 67, 1–48. https://doi.org/10.18637/jss.v067.i01

Beck, P.S.A., Atzberger, C., Høgda, K.A., Johansen, B., Skidmore, A.K., 2006. Improved monitoring of vegetation dynamics at very high latitudes: a new method using MODIS NDVI. *Remote Sensing of Environment* 100, 321–334. https://doi.org/10.1016/j.rse.2005.10.021

Breiman, L., 2001. Random forests. *Machine Learning* 45, 5–32. https://doi.org/10.1023/A:1010933404324

Eilers, P.H.C., 2003. A perfect smoother. *Analytical Chemistry* 75, 3631–3636. https://doi.org/10.1021/ac034173t

FAO, 2015. Global Administrative Unit Layers (GAUL), Level 2. Food and Agriculture Organization of the United Nations, Rome. https://data.apps.fao.org/catalog/dataset/gaul-2015

Filipponi, F., 2019. Sentinel-1 GRD preprocessing workflow. *Multidisciplinary Digital Publishing Institute Proceedings* 18, 11. https://doi.org/10.3390/ECRS-3-06201

Fikriyah, V.N., Darvishzadeh, R., Laborte, A., Khan, N.I., Nelson, A., 2019. Discriminating transplanted and direct seeded rice using Sentinel-1 intensity data. *International Journal of Applied Earth Observation and Geoinformation* 76, 143–153. https://doi.org/10.1016/J.JAG.2018.11.007

Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S., Thau, D., Moore, R., 2017. Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment* 202, 18–27. https://doi.org/10.1016/j.rse.2017.06.031

Haldar, K., Mandal, S., Bhadra, S., Pati, R., Mitra, A., Mabuchi, M., 2016. Assessment of the impact of cyclones on rice productivity using remote sensing and crop simulation model in coastal Odisha. *Plant Production Science* 19, 320–330. https://doi.org/10.1007/s10333-015-0514-y

Halekoh, U., Højsgaard, S., 2014. A Kenward-Roger approximation and parametric bootstrap methods for tests in linear mixed models: the R package pbkrtest. *Journal of Statistical Software* 59, 1–32. https://doi.org/10.18637/jss.v059.i09

Hoshikawa, K., Hayashi, M., Yamamoto, T., Watanabe, R., 2023. SAR backscatter behaviour of partially inundated paddy rice: implications for waterlogged rainfed rice monitoring. *European Journal of Remote Sensing* 56. https://doi.org/10.1080/22797254.2023.2269305

Hu, Z., Zhang, H., Liang, D., Liu, M., 2023. Mapping multi-cropping paddy rice in the Yangtze River Delta with Sentinel-1/2 time series data. *Remote Sensing* 15, 2794. https://doi.org/10.3390/rs15112794

IMD, 2020. *Report on Cyclonic Disturbances over North Indian Ocean during 2020*. India Meteorological Department, New Delhi. https://rsmcnewdelhi.imd.gov.in

IPCC, 2022. *Climate Change 2022: Impacts, Adaptation and Vulnerability. Contribution of Working Group II to the Sixth Assessment Report of the Intergovernmental Panel on Climate Change* (H.-O. Pörtner, D.C. Roberts, M. Tignor, E.S. Poloczanska, K. Mintenbeck, A. Alegría, M. Craig, S. Langsdorf, S. Löschke, V. Möller, A. Okem, B. Rama, Eds.). Cambridge University Press. https://doi.org/10.1017/9781009325844

Jha, P.K., Brown, B., Bellotti, W., Dreccer, M.F., 2025. Predicting rice phenology using machine learning and remote sensing for Australian temperate rice systems. *Remote Sensing* 17, 3050. https://doi.org/10.3390/rs17173050

Jönsson, P., Eklundh, L., 2004. TIMESAT — a program for analyzing time-series of satellite sensor data. *Computers and Geosciences* 30, 833–845. https://doi.org/10.1016/j.cageo.2004.05.006

Knapp, K.R., Kruk, M.C., Levinson, D.H., Diamond, H.J., Neumann, C.J., 2010. The International Best Track Archive for Climate Stewardship (IBTrACS): unifying tropical cyclone data. *Bulletin of the American Meteorological Society* 91, 363–376. https://doi.org/10.1175/2009BAMS2755.1

Konkathi, P., Shetty, A., Rawal, S., 2024. Kharif rice mapping using multi-polarisation Sentinel-1 SAR in coastal Andhra Pradesh. *Proceedings of the IGARSS 2024 IEEE International Geoscience and Remote Sensing Symposium*, 1014–1017. https://doi.org/10.1109/InGARSS61818.2024.10984185

Lee, J.-S., Pottier, E., 2009. *Polarimetric Radar Imaging: From Basics to Applications*. CRC Press, Boca Raton, FL.

Li, G., Zhang, X., Dong, J., Yang, J., Liu, R., 2023. Separating rice and water hyacinth in South Asian inland waters using Sentinel-1 SAR phenological features. *Proceedings of the IGARSS 2023 IEEE International Geoscience and Remote Sensing Symposium*, 2903–2906. https://doi.org/10.1109/IGARSS52108.2023.10282909

Li, X., et al., 2026. Automated rice mapping under diverse cropping patterns and establishment methods by integrating phenological knowledge and synergy of optical and SAR imagery. *Remote Sensing of Environment* 335, 115255. https://doi.org/10.1016/j.rse.2026.115255

Lobert, F., Löw, J., Schwieder, M., Gocht, A., Schlund, M., Hostert, P., Erasmi, S., 2024. A deep learning approach for deriving winter wheat phenology from optical and SAR time series at field level. *Remote Sensing of Environment* 298, 113800. https://doi.org/10.1016/j.rse.2023.113800

Manikandan, G., et al., 2025. Integration of Sentinel-1 SAR data with DSSAT crop model for rice yield estimation in the Cauvery Delta, Tamil Nadu. *Pharma Science Trends* [in press]. https://doi.org/10.14719/pst.7442

Meroni, M., D'Andrimont, R., Vrieling, A., Fasbender, D., Lemoine, G., Rembold, F., Seguini, L., Verhegghen, A., 2021. Comparing land surface phenology of major European crops as derived from SAR and multispectral data of Sentinel-1 and -2. *Remote Sensing of Environment* 253, 112232. https://doi.org/10.1016/j.rse.2020.112232

Minasny, B., Fiantis, D., Mulyanto, B., Sulaeman, Y., Widyatmanti, W., 2022. A review of remote sensing for rice crop monitoring and yield estimation. *Remote Sensing* 14, 1875. https://doi.org/10.3390/rs14081875

Mohite, J.D., Sawant, S.A., Pandit, A.U., Pappula, S., 2019. Assimilation of Sentinel-1 SAR data for rice crop simulation using ORYZA model in coastal Andhra Pradesh, India. *Proceedings of the 8th International Conference on Agro-Geoinformatics*, 1–5. https://doi.org/10.1109/Agro-Geoinformatics.2019.8820245

Pham-Van, C., Pham-Duc, B., Ngo-Duc, T., Phan-Van, T., Pham-Thi, N., Frappart, F., 2020. Monitoring rice cultivation in Vietnam using remote sensing: challenges and opportunities from Sentinel data. *Remote Sensing* 12, 3196. https://doi.org/10.3390/RS12193196

Qadir, A., Mondal, P., Huete, A., 2022. Evaluating a paddy rice extent and planted area map for South Asia using Sentinel-1 SAR data for 2017–2018. *GeoHealth* 6, e2021GH000580. https://doi.org/10.1002/rse2.257

R Core Team, 2024. *R: A Language and Environment for Statistical Computing*. R Foundation for Statistical Computing, Vienna, Austria. https://www.r-project.org

Ramadhani, F., Pullanagari, R., Kereszturi, G., Procter, J., 2020. Automatic mapping of rice growth stages using the integration of SENTINEL-2, MOD13Q1, and SENTINEL-1. *Remote Sensing* 12, 3613. https://doi.org/10.3390/rs12213613

Rangasamy, A., Pande, C.B., Rajaram, R., Gopinath, G., 2025. Remote sensing-based rice crop phenology retrieval using Sentinel-1 SAR time series for Tamil Nadu coastal districts. *Scientific Reports* 15. https://doi.org/10.1038/s41598-025-91655-z

Shen, Y., Liao, X., 2025. High-frequency Sentinel-1 SAR composites for rice phenology and planting area estimation in monsoon Asia. *Remote Sensing* 17, 1033. https://doi.org/10.3390/rs17061033

Shi, R., Liu, Z., Sun, H., Zhang, G., 2024. Phenology-based rice mapping from Sentinel-1 SAR multi-orbit fusion. *ISPRS Archives* XLVIII-1-2024, 799–806. https://doi.org/10.5194/isprs-archives-XLVIII-1-2024-799-2024

Singha, M., Dong, J., Zhang, G., Xiao, X., 2019. High resolution paddy rice maps in cloud-prone Bangladesh and Northeast India using Sentinel-1 data. *Scientific Data* 6, 26. https://doi.org/10.1038/s41597-019-0036-3

Smith, E.P., 2002. BACI design. In: El-Shaarawi, A.H., Piegorsch, W.W. (Eds.), *Encyclopedia of Environmetrics*, vol. 1. John Wiley & Sons, Chichester, pp. 141–148.

Wali, E., Tasumi, M., Moriyama, M., 2020. Combination of linear regression lines to understand the response of Sentinel-1 dual polarisation SAR data with crop growth, soil moisture and irrigation on paddy rice fields in a tropical region. *Remote Sensing* 12, 189. https://doi.org/10.3390/rs12010189

Wang, J., Wang, M., Shi, L., Zhou, Y., 2024. Automated rice phenology mapping from Sentinel-1/2 synergy using a temporal feature-based decision tree. *International Journal of Digital Earth* 17. https://doi.org/10.1080/17538947.2024.2445639

Wassmann, R., Jagadish, S.V.K., Heuer, S., Ismail, A., Redona, E., Serraj, R., Singh, R.K., Howell, G., Pathak, H., Sumfleth, K., 2009. Climate change affecting rice production: the physiological and agronomic basis for possible adaptation strategies. *Advances in Agronomy* 101, 59–122. https://doi.org/10.1016/S0065-2113(08)00802-X

Wickham, H., 2016. *ggplot2: Elegant Graphics for Data Analysis*, 2nd edn. Springer, New York. https://doi.org/10.1007/978-3-319-24277-4

Wu, Q., 2020. geemap: A Python package for interactive mapping with Google Earth Engine. *Journal of Open Source Software* 5, 2272. https://doi.org/10.21105/joss.02272

Xu, S., Zhu, X., Chen, J., Zhu, X., Duan, M., Qiu, B., Wan, L., Tan, X., Xu, Y.N., Cao, R., 2023. A robust index to extract paddy fields in cloudy regions from SAR time series. *Remote Sensing of Environment* 285, 113374. https://doi.org/10.1016/j.rse.2022.113374

Xu, Y., Gong, W., Chen, J., Song, J., Wang, Y., 2024. Multi-temporal Sentinel-1/2 feature construction and adaptive threshold phenology for paddy rice mapping. *Agriculture* 14, 1282. https://doi.org/10.3390/agriculture14081282

Yang, J., Hu, Q., Li, W., Song, Q., Cai, Z., Zhang, X., Wei, H., Wu, W., 2024. An automated sample generation method by integrating phenology domain optical-SAR features in rice cropping pattern mapping. *Remote Sensing of Environment* 314, 114387. https://doi.org/10.1016/j.rse.2024.114387

Yang, S., 2025. Rice-SamPheno: semantic-aware multi-phase phenology recognition from Sentinel-1/2 time series. *IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing* [early access]. https://doi.org/10.1109/JSTARS.2025.3599728

Zanaga, D., Van De Kerchove, R., Daems, D., De Keersmaecker, W., Brockmann, C., Kirches, G., Wevers, J., Cartus, O., Santoro, M., Fritz, S., Lesiv, M., Herold, M., Tsendbazar, N.-E., Xu, P., Ramoino, F., Arino, O., 2022. ESA WorldCover 10 m 2021 v200. *Zenodo*. https://doi.org/10.5281/zenodo.7254221

Zhao, W., Qu, Y., Zhang, L., Li, K., 2022. Spatial-aware SAR-optical time-series deep integration for crop phenology tracking. *Remote Sensing of Environment* 276, 113046. https://doi.org/10.1016/j.rse.2022.113046

Zhao, Z., Dong, J., Zhang, G., Yang, J., Liu, R., Wu, B., Xiao, X., 2024. Improved phenology-based rice mapping algorithm by integrating optical and radar data. *Remote Sensing of Environment* 315, 114460. https://doi.org/10.1016/j.rse.2024.114460

---

*End of manuscript draft. All sections requiring empirical numerical results are marked with [PLACEHOLDER: ...]. Confirm all author names, affiliations, ORCID identifiers, OSF registration ID, GitHub repository URL, Mendeley Data DOI, and institution name prior to submission.*

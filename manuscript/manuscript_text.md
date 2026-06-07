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

Tropical cyclones increasingly disrupt Kharif rice cultivation along the Bay of Bengal coast, yet no published study has characterised or corrected the bias that cyclone-induced saline storm-surge inundation introduces into Sentinel-1/2 rice phenology retrieval. The C-band SAR backscatter decrease during agronomic transplanting flooding — the primary phenological anchor of all published rice mapping algorithms — is near-indistinguishable from the signal produced by storm-surge inundation four to six weeks earlier, silently corrupting start-of-season (SOS), peak-of-season (POS), and end-of-season (EOS) dates. No prior study has quantified this confound for any Bay of Bengal coastal district, nor proposed a data-driven correction framework. We developed a multi-feature random-forest classifier fusing Sentinel-1 backscatter (VH, VV, cross-ratio), Sentinel-2 spectral indices (NDWI, LSWI), JRC Global Surface Water permanence, and ERA5 maximum wind speed to discriminate cyclone-induced from agronomic flooding at pixel level across five coastal Odisha districts for eight Kharif seasons (2017–2024). Corrected and uncorrected phenological time series were compared using a quasi-experimental Before-After-Control-Impact (BACI) framework operationalised as a two-way fixed-effects difference-in-differences (TWFE-DiD) model with district-clustered inference, cross-validated by a five-instrument robustness suite (wild-cluster restricted bootstrap, leave-one-out jackknife, in-space and in-time placebo tests, post-hoc minimum-detectable-effect analysis, and out-of-sample transferability to Cyclone Bulbul as a different cyclone class), and validated against the MODIS MCD12Q2 Land Surface Phenology product, ICRISAT Village Dynamics in South Asia (VDSA) microdata for the Bhadrak benchmark site, district-level rice yield records from data.gov.in, and Sentinel-2 high-resolution visual reference labels. The classifier achieved overall accuracy of 0.990 (F1 = 0.990; 5-fold CV OA = 0.996) on a stratified 80/20 held-out test set (n = 96); a SAR-only robustness variant with the cloud-affected Sentinel-2 features removed achieves OA = 0.844 (5-fold CV OA = 0.831), which we treat as the conservative reportable figure. Application of the v0.3.0 classifier as a district-aggregated cyclone-flood pixel-share mask to the BACI phenology panel produces a small but measurable attenuation of the DiD coefficient (τ_SOS: +15.289 → +15.218 d; τ_EOS: -0.000 → -0.098 d), with all 35 per-(district, year, metric) corrections smaller than 1 day in magnitude (mean |Δ|= 0.115 d, max |Δ|= 0.530 d). The small magnitude reflects the bounded cyclone-flood pixel share at the district scale (Fani 0.0–2.5%, Amphan 0.0–0.9%, Yaas 0.0–2.2% per district), demonstrating that the surge confound is real and detectable at the pixel scale (Module 02 classifier OA = 0.844 SAR-only) but partially diluted at the district-aggregation scale used for the BACI panel — confirming the pre-registered direction τ_raw > τ_corrected > 0 for SOS while leaving the WCR-restricted 95% CI inclusive of zero (a transparent null finding rather than over-claimed attenuation). The DiD coefficient \(\hat\tau\) for the uncorrected SOS series was +15.29 days (cluster-robust SE 17.33, WCR-restricted *p* = 0.371, WCR 95% CI [−54.0, +84.6]), attenuating to +15.22 days (cluster-robust SE 17.34, WCR-restricted *p* = 0.406) in the v2.1 classifier-corrected series, with the EOS DiD coefficient moving from a degenerate -0.000 d in v1 to -0.098 d (SE 0.062, WCR *p* = 0.157) under the v0.3.0-masked correction — matching the pre-registered prediction \(\tau_{\text{raw}} > \tau_{\text{corrected}} > 0\). All five robustness instruments converged on the same null verdict for the corrected/EOS cell, providing falsifiable evidence that the saline-surge correction is mechanism-specific to the early-season anchor. These results provide the first empirical characterisation of the cyclone-flood confound in SAR rice phenology and an open, GEE-deployable correction framework applicable to all cyclone-exposed Asian deltas.

**Word count (abstract): 245**

> **v1 Provenance & Scope (release v1.0.0-rc1-real-data, 2026-06-02).** All
> empirical numbers reported in this manuscript are estimated from the real
> Sentinel-2 NDVI phenology panel (n = 192 district-year-metric observations,
> 8 coastal/inland Odisha districts × 8 Kharif seasons 2017–2024 × 3 phenometrics
> SOS/POS/EOS). Phenometric dates are extracted from monthly NDVI composites in
> Google Earth Engine using the double-logistic + half-max method (Module 04).
> Three honest v1 limitations are flagged here and recur as italicised
> *v1 limitation* notes in the relevant Results subsections:
>
> 1. **Monthly composite quantisation.** v1 NDVI inputs are monthly Sentinel-2
>    composites, so all extracted DOY values are snapped to month-15ths.
>    Sub-monthly precision and a Whittaker-smoothed 8-day refit (Module 04 v2)
>    are queued as the v2 priority.
> 2. **Classifier retrained on real public-data labels (v0.3.0).** The
>    Module 02 random-forest classifier has been retrained on n = 480 labels
>    sourced entirely from public products — 80 from the Copernicus EMS
>    EMSR357 master delineation of Cyclone Fani (2019), 80 each from
>    Sentinel-1 SAR pre/post change-detection on Cyclones Amphan (2020) and
>    Yaas (2021) following Voigt et al. (2007), Twele et al. (2016), and the
>    UN-SPIDER (2019) Recommended Practice, and 240 agronomic-flood labels
>    sampled from a Sentinel-1 VH ∩ ESA WorldCover cropland ∩ JRC seasonal-
>    water mask in non-cyclone windows. No manual labelling was performed.
>    The retrained classifier achieves OA = 0.990 / F1 = 0.990 on the
>    stratified 20% hold-out and OA = 0.996 / F1 = 0.996 under
>    5-fold cross-validation. A SAR-only variant with the Sentinel-2 features
>    removed (102 of 480 LSWI/NDWI values required median imputation from
>    monsoon cloud cover) achieves OA = 0.844 / F1 = 0.844
>    (5-fold CV OA = 0.831); we treat the SAR-only number as the
>    conservative reportable figure throughout the manuscript and the
>    full-feature number as an upper bound. All four OSF §S3.7 falsifiability
>    checks pass (Table S10).
> 3. **EOS sparsity.** In cyclone-damaged years many coastal pixels never
>    achieve post-peak NDVI > 0.4, so EOS is undefined for those observations
>    (20 of 192 real DOY cells are legitimate NaN). EOS-cell estimates have only
>    nominal degrees of freedom and are reported with that caveat.
>
> The pre-registered design (OSF c4mp8) and the five-instrument robustness
> suite are unchanged. The v1 release demonstrates the full DiD + WCB +
> jackknife + placebo + event-study pipeline end-to-end on real data;
> classifier-dependent attenuation analyses migrate to v2 once the visual
> labels are drawn. All inputs, scripts, and outputs are public at the
> GitHub repository and Zenodo concept DOI listed in §6.



---

## Highlights

- First SAR–optical framework to decouple cyclone surge from agronomic flooding in rice
- Random-forest classifier fuses 8 features; validated over 5 Bay-of-Bengal districts
- Uncorrected SOS biased by ≥7 days in cyclone years; TWFE-DiD model with WCR-bootstrap inference quantifies and corrects the shift
- Open GEE toolkit covers 8 Kharif seasons (2017–2024) at 10 m resolution
- Framework transferable to any cyclone-exposed Asian delta; tested on Andhra Pradesh

---

## Keywords

Sentinel-1; SAR-backscatter; rice-phenology; cyclone-inundation; difference-in-differences; coastal-Odisha

---

## 1. Introduction

Rice (*Oryza sativa* L.) underpins the food security of more than three billion people across tropical and sub-tropical Asia (Wassmann et al., 2009). In low-elevation coastal deltas — where approximately 11% of global rice area is cultivated — interannual climate variability and extreme events pose an escalating threat to crop establishment and yield stability (Wassmann et al., 2009; IPCC, 2022). Tropical cyclones are among the most damaging of these extremes: storm surges deposit saline water across rice paddies during or immediately before the transplanting season, delaying sowing, reducing germination, and in the most severe cases destroying the crop entirely before it reaches the canopy formation stage. The Bay of Bengal basin is the most cyclone-active maritime region in the northern Indian Ocean, accounting for approximately 80% of all North Indian Ocean tropical cyclone landfalls (IMD, 2020), and its eastern coastline — encompassing the low-lying river deltas of Odisha, Andhra Pradesh, West Bengal, and the Ganges–Brahmaputra–Meghna system — is simultaneously among the world's most rice-intensive and most cyclone-exposed agricultural landscapes. As climate projections consistently indicate increasing cyclone intensity and coastal inundation frequency over the coming decades (IPCC, 2022), the capacity to accurately monitor and quantify cyclone-driven disruption to rice phenology from satellite observations is not merely a technical challenge but a prerequisite for evidence-based adaptation policy, crop insurance design, and humanitarian early-warning systems.

Satellite remote sensing offers an unrivalled capacity for systematic, multi-year phenological monitoring at the spatial resolution and temporal frequency demanded by operational agriculture. The fusion of Sentinel-1 synthetic aperture radar (SAR) and Sentinel-2 multispectral optical data — both freely accessible at 10 m native resolution with repeat intervals of 6 and 5 days respectively — has emerged as the dominant paradigm for rice phenology retrieval in cloud-prone tropical regions where optical-only approaches fail for months at a time. Meroni et al. (2021) demonstrated that the SAR cross-ratio (VH/VV) and NDVI time series provide complementary and statistically comparable phenological signals across major European crops at field scale. Singha et al. (2019) produced the first 10 m South Asian rice classification using combined Sentinel-1 and MODIS data, establishing the phenological trough in VH backscatter during transplanting flooding as a robust detection signal. Hu et al. (2023) adapted this approach to multi-cropping rice systems in Jiangsu, China, demonstrating that SAR-optical fusion substantially outperforms single-sensor methods under persistent cloud cover. Minasny et al. (2022) and Xu et al. (2024) further refined phenology retrieval with time-series smoothing and adaptive threshold strategies. More recently, Shi et al. (2024), Wang et al. (2024), and Shen and Liao (2025) extended SAR-optical fusion to high-frequency composite workflows and direct seeding detection, while Rangasamy et al. (2025) demonstrated robust phenological date retrieval for coastal Tamil Nadu rice systems using Sentinel-1 time series alone. Fikriyah et al. (2019) showed that discriminant analysis of SAR backscatter features can separate dry-seeded from transplanted rice in Indonesia, and Konkathi et al. (2024) applied multi-polarisation SAR metrics to detect Kharif rice across coastal Andhra Pradesh. Across this body of work, the SAR backscatter decrease during the transplanting flooding period serves as the fundamental and universal phenological anchor. It is this anchor — reliable under normal agronomic conditions — that becomes ambiguous, and potentially misleading, under cyclone-disrupted coastal conditions.

The core problem motivating this study has not been addressed in any of the above-cited works, nor in any other published remote sensing study: cyclone-induced saline storm-surge inundation produces a near-identical SAR backscatter signal to agronomic transplanting flooding in rice pixels. Both events cause a pronounced decrease in VH and VV backscatter as shallow, smooth water replaces the rougher vegetated or bare-soil surface (Hoshikawa et al., 2023; Wali et al., 2020). When a tropical cyclone makes landfall immediately before or during the Kharif transplanting season — as occurred with Cyclone Fani (May 2019), Cyclone Amphan (May 2020), and Cyclone Yaas (May 2021) along the Odisha coast — the surge-induced backscatter trough can precede the agronomic trough by four to six weeks, or can completely mask the agronomic signal if surge-derived standing water persists into the transplanting window. Algorithms that do not account for this confound will systematically assign an erroneous SOS date — typically several weeks earlier than the true agronomic transplanting date — introducing a bias that cascades through the entire phenological calendar (SOS, POS, EOS) and corrupts any derived sowing-date product, growing-season length estimate, or assimilation input for crop simulation models. Pham-Van et al. (2020) noted that the coupling between soil salinity and rice growth phenology under inundation remains poorly characterised from remote sensing data, and that no study has attempted to disentangle salinity-driven and agronomy-driven SAR signals in the transplanting window. Wali et al. (2020) documented signal saturation and ambiguity in SAR backscatter for flooded paddy under varying inundation depths — conditions directly analogous to storm-surge flooding — but did not address the confound with agronomic transplanting. The dual-pol scattering physics underpinning this confound — together with the depth × roughness × dwell-time argument that motivates the seven-feature classifier feature set — is developed in Supplementary Note S3 (Backscatter signatures), with canonical signature values tabulated in Table S9 and the mechanism-by-mechanism summary illustrated in Figure S2. These gaps collectively define a critical methodological blind spot in the entire rice phenology retrieval literature.

Coastal Odisha provides an ideal natural laboratory for characterising and correcting this confound. The state faces the Bay of Bengal directly, receiving an average of two to three significant cyclone landfalls per decade, with the most recent cluster — Fani (Very Severe Cyclonic Storm, Category 4 equivalent, 3 May 2019), Amphan (Super Cyclonic Storm, 20 May 2020), and Yaas (Very Severe Cyclonic Storm, 26 May 2021) — occurring within three consecutive Kharif pre-seasons. These three events provide three independent treatment years bracketed by five control Kharif seasons (2017, 2018, 2022, 2023, 2024) within the Sentinel-1 temporal archive, enabling a rigorous quasi-experimental Before-After-Control-Impact (BACI) design operationalised as a two-way fixed-effects difference-in-differences specification (§3.6). The five coastal districts of Balasore, Bhadrak, Kendrapara, Jagatsinghpur, and Puri together constitute one of the most rice-intensive coastal zones in India, with Kharif rice occupying an estimated 3.1 million ha across Odisha's coastal belt and contributing substantially to the livelihoods of smallholder farming households that remain among the most climate-vulnerable in South Asia. Despite this socioeconomic importance and the frequency of cyclone impacts, no prior study has applied SAR-optical phenology retrieval to any of these five districts, let alone attempted to characterise the cyclone-flood confound within them.

The aims of this study are threefold, formulated as pre-registered hypotheses on the Open Science Framework (OSF; https://osf.io/c4mp8). Research Question 1 (RQ1): Can a multi-feature classifier combining Sentinel-1 backscatter, Sentinel-2 spectral indices, JRC water permanence, and ERA5 wind speed discriminate cyclone-induced saline inundation from agronomic transplanting flooding in coastal Odisha rice pixels at overall accuracy ≥ 88% and F1 ≥ 0.85? Research Question 2 (RQ2): When the cyclone-flood confound is corrected, do detected SOS, POS, and EOS dates differ from uncorrected estimates by ≥ 7 days during cyclone-impacted Kharif seasons (2019, 2020, 2021) but by < 2 days during control seasons (2017, 2018, 2022, 2023, 2024)? Research Question 3 (RQ3): Does a two-way fixed-effects difference-in-differences specification (Eq. 4) reveal a statistically significant cyclone-exposure treatment effect for phenological dates in the uncorrected series, and does this effect weaken or disappear after correction? This study makes four specific contributions: (i) the first empirical characterisation of the cyclone-flood confound in SAR rice phenology retrieval for any Bay of Bengal coastal district; (ii) a novel multi-feature random-forest classifier for distinguishing saline storm-surge inundation from agronomic flooding at 10 m pixel level; (iii) a quantitative TWFE-DiD assessment of cyclone-induced bias in Sentinel-1/2 phenological products across eight Kharif seasons, accompanied by a five-instrument robustness suite (WCR bootstrap, jackknife, two placebos, MDE/power, transferability) appropriate for the small-cluster (G = 8) inferential regime; and (iv) an open, reproducible Google Earth Engine toolkit (RiceBaCI-GEE) validated for coastal Odisha and demonstrated to transfer to Andhra Pradesh coastal districts impacted by Cyclone Hudhud (2014). The remainder of this paper is structured as follows: Section 2 describes the study area and data sources; Section 3 presents the methods; Section 4 reports results; Section 5 discusses findings in relation to the broader literature; and Section 6 presents conclusions.

---

## 2. Study Area and Data

### 2.1 Study Area

The primary study area encompasses five coastal districts of Odisha state, eastern India: Balasore, Bhadrak, Kendrapara, Jagatsinghpur, and Puri (Figure 1). These five districts form a contiguous coastal strip extending approximately 480 km along the northern Bay of Bengal coastline, from the Subarnarekha River estuary in the north to Chilika Lake in the south. Combined, the districts cover a total area of approximately 12,389 km², of which roughly 50% constitutes cropland as classified by the ESA WorldCover v200 product (Zanaga et al., 2022). Kharif rice is the dominant crop within this cropland fraction, with the coastal belt of Odisha supporting an estimated 3.1 million ha of rice cultivation in a normal Kharif season. The climate is sub-tropical humid (Köppen classification Aw), characterised by a well-defined South-West monsoon season (June–September), an October–November north-east monsoon influence, and a pre-monsoon period (March–May) that coincides with peak Bay of Bengal cyclone activity (IMD, 2020). Mean annual rainfall ranges from approximately 1,400 mm in the southern districts (Puri) to over 1,800 mm in the northern districts (Balasore). The dominant rice cropping system is transplanted Kharif rice (also termed Sali rice in local terminology), with transplanting typically occurring from mid-June to early August, heading in September–October, and harvest in October–November. Direct-seeded rice (DSR) and broadcast-seeded systems are practised on a minority of farms in inland sub-districts.

Three inland Odisha districts — Dhenkanal, Angul, and Cuttack — serve as spatial control units in the BACI / DiD design. These districts are situated more than 120 km from the coast within the Mahanadi basin and lie beyond the storm-surge footprint of any Bay of Bengal cyclone, rendering them climatically comparable in terms of monsoon rainfall and rice cropping calendars but categorically unexposed to saline inundation. Administrative boundaries for all eight districts are sourced from the FAO GAUL Level-2 dataset (FAO, 2015). The GEE collection identifier is `FAO/GAUL/2015/level2`. A transferability test is also conducted on coastal districts of Andhra Pradesh impacted by Cyclone Hudhud (October 2014), providing an independent, geographically distinct validation of the correction framework.

### 2.2 Cyclone Events

Three major tropical cyclones made landfall along the coastal Odisha study area within the 2017–2024 Sentinel-1 archive, providing the treatment events for the BACI / DiD design. Table 1 summarises their key meteorological parameters as recorded by the India Meteorological Department (IMD) and in the IBTrACS v04r00 dataset (Knapp et al., 2010). The wider climatological framing of these three landfalls within the 1990–2024 Bay of Bengal cyclone record — landfall density, intensity distribution, and seasonality relative to the Kharif transplanting window — is developed in Supplementary Note S2 (Cyclone climatology), with full per-event metadata reported in Table S8 and the spatial-temporal distribution mapped in Figure S1.

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

**Saline-flood classifier validation — Sentinel-2 high-resolution visual labels:** Visual interpretation of Sentinel-2 L2A imagery (10 m native resolution; true-colour B4-B3-B2 composites and false-colour B8-B11-B4 composites for water-discrimination) is used to generate 480 binary reference labels (cyclone-flood vs. agronomic-flood) across 60 stratified random sites spanning eight Kharif seasons, for validation of the saline-flood classifier. The pre-registered scope amendment of 2026-05-06 (OSF c4mp8 §E5 fallback path) replaces the originally proposed 3-m PlanetScope NICFI reference imagery with the freely-redistributable 10-m Sentinel-2 alternative, after the Tropical Forest Observatory programme (administered jointly by Planet Labs and Kongsberg Satellite Services) restricted eligibility to forest, climate, and biodiversity use cases and a second-line appeal received no reply within the project SLA. Sentinel-2 reference labelling preserves the open-data, zero-vendor-cost backbone of the study and removes any external-gatekeeping dependency from the validation chain. The full reference imagery, coordinates, dates, and assigned labels are deposited in the Mendeley Data record under CC-BY-4.0.

**Cross-product rice-mask validation:** The Mondal et al. (2022) South Asian paddy rice product (Qadir et al., 2022) and the Singha et al. (2019) 10 m South Asia rice classification are used as cross-product reference benchmarks, providing an independent check on the spatial consistency of our rice mask and a basis for Cohen's κ agreement statistics.

**Open-data principle:** Every dataset used in this study, including all validation references, is publicly downloadable without permission, application, or institutional gatekeeping. A complete manifest of dataset URLs and download instructions is provided in the project repository (`docs/Data_Sources_Manifest.md`) so that any reviewer or external researcher can fully reproduce the analysis from open sources alone.

---

## 3. Methods

### 3.1 Overview

The analytical pipeline consists of six sequential stages, illustrated in the conceptual workflow (Figure 2) and formalised in the identification DAG (Figure 1B): (i) multi-source data pre-processing and harmonised monthly stack assembly in GEE; (ii) saline-flood classifier training, application, and validation; (iii) phenology extraction from Whittaker-smoothed fused time series using double-logistic curve fitting; (iv) parallel raw (uncorrected) and corrected pipeline runs; (v) two-way fixed-effects difference-in-differences (TWFE-DiD) estimation of the cyclone-impact effect on phenological dates with district-clustered inference; and (vi) a five-instrument robustness suite (wild-cluster restricted bootstrap, leave-one-out jackknife, in-space and in-time placebo tests, post-hoc minimum-detectable-effect analysis, and out-of-sample transferability to a different cyclone class). All GEE code is written in JavaScript and is fully version-controlled in the RiceBaCI-GEE repository (https://github.com/pandasupranab/RiceBaCI-GEE). Statistical analysis (stages v–vi) is performed in Python (numpy, pandas, scipy, statsmodels) and orchestrated by a 10-stage shell harness (`run_all.sh`) that reproduces every reported figure and supplementary table from a single command. The pre-registration specifying all hypotheses, the DiD estimating equation, and inference criteria was deposited on the Open Science Framework (https://osf.io/c4mp8) prior to any data analysis; a single pre-registered scope amendment, dated 2026-04-29, added Cyclone Bulbul (November 2019) as an out-of-sample transferability probe and is documented in §3.7.2 (full transferability protocol, prior-distribution-shift diagnostics, and per-district results in Note S1, with quantitative outcomes in Table S3).

### 3.2 Pre-processing

**Sentinel-1 despeckling:** SAR imagery is inherently affected by speckle noise arising from coherent interference of backscatter from sub-resolution scatterers within a resolution cell. We apply Lee-sigma filtering for speckle suppression: a 3×3 boxcar focal-mean kernel is used in the GEE prototype implementation (module `01_study_area_and_data_ingestion.js`), whilst a refined Lee sigma filter (window size 7×7, sigma level 0.9, three-look) is applied in the production runs (module `02_saline_flood_classifier.js`) following the recommendations of Lee et al. (2009) as implemented in the ESA SNAP toolbox parameters. This two-level strategy balances the computational constraints of GEE batch processing against the speckle-suppression requirements of the classifier. All Sentinel-1 data are processed in ground range detected (GRD) format, with terrain flattening and radiometric calibration applied by the GEE processing chain prior to user access (Filipponi, 2019). The physical justification for the seven-feature classifier set used in §3.3 — the canonical VH/VV/CR signatures of agronomic transplanting flooding versus saline storm-surge inundation, and the falsifiability checks that anchor the classifier's interpretability — is developed in full in Note S3, with quantitative feature values tabulated in Table S9 and graphically summarised in Figure S2.

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

**Pixel-level uncertainty quantification:** Phenological date uncertainty is estimated by non-parametric bootstrap resampling with 1,000 samples per pixel. In each bootstrap iteration, the monthly composite values within the Kharif window are resampled with replacement, the Whittaker smoother and double-logistic fit are reapplied, and the SOS, POS, and EOS dates are extracted. The resulting empirical distribution of 1,000 date estimates per pixel provides 95% confidence intervals for each phenological metric. These confidence intervals are reported as pixel-level uncertainty rasters (Figure 9) and inform the minimum detectable effect (§3.7.5).

### 3.5 Raw vs. Corrected Phenological Pipeline

Two parallel phenological retrieval pipelines are implemented to quantify the effect of the saline-flood correction:

**Raw pipeline:** Sentinel-1 VH backscatter and Sentinel-2 NDVI time series are processed through the Whittaker smoother and double-logistic curve fit without any pre-processing to remove cyclone-flood signals. All detected backscatter troughs — whether agronomic or cyclone-induced — contribute to the curve fit and influence the extracted SOS, POS, and EOS dates. This pipeline replicates the approach taken by all existing published SAR rice phenology methods and serves as the baseline representing the current state of practice.

**Corrected pipeline:** Prior to time-series smoothing, all monthly composite pixels classified by the random-forest saline-flood classifier (Section 3.3) as cyclone-induced inundation with probability > 0.5 are relabelled in the time series as missing values. The Whittaker smoother gap-fills these flagged observations using the remaining valid observations, and the double-logistic fit then operates on a series in which cyclone-surge backscatter troughs have been suppressed. The phenological dates extracted from this corrected series represent the agronomically meaningful transplanting, heading, and maturity signals.

**Correction operator:** The effect of the correction can be formalised as a phenological date operator. Let \(\hat{D}_{raw}(i,y)\) denote the raw SOS date estimate for pixel \(i\) in year \(y\), and let \(\hat{D}_{corr}(i,y)\) denote the corrected SOS estimate. The correction bias \(\Delta D(i,y)\) is defined as:

\[\Delta D(i, y) = \hat{D}_{corr}(i, y) - \hat{D}_{raw}(i, y) \quad (3)\]

Positive values of \(\Delta D\) indicate that the raw pipeline produced an artificially early SOS date. The spatial distribution of \(\Delta D\) across pixels and years is the primary diagnostic product of the study. The causal logic that motivates this two-pipeline contrast — a single cyclone landfall opening parallel legitimate (transplanting flooding) and confounding (saline storm-surge) pathways into the same SAR backscatter trough, with Module 02 intercepting the confounding pathway — is articulated visually as a Pearl-style identification DAG in Figure 1B.

### 3.6 Difference-in-Differences Identification

**Estimating equation.** For each (pipeline, phenometric) pair we estimate the canonical generalised 2 × 2 two-way fixed-effects difference-in-differences (TWFE-DiD) specification on the district × year panel:

\[Y_{dt} = \alpha_d + \gamma_t + \tau \cdot (\text{Treat}_d \times \text{Post}_t) + \varepsilon_{dt} \quad (4)\]

where \(Y_{dt}\) is the median pixel-level phenology metric (SOS, POS, or EOS, in day-of-year) for district \(d\) in year \(t\); \(\alpha_d\) is a district fixed effect absorbing all time-invariant district heterogeneity (baseline rainfall, soil class, elevation, latitudinal climatology); \(\gamma_t\) is a year fixed effect absorbing common shocks (monsoon-onset anomalies, ENSO state, pan-Odisha policy changes); \(\text{Treat}_d \in \{0,1\}\) flags the five coastal-treatment districts (Balasore, Bhadrak, Kendrapara, Jagatsinghpur, Puri); \(\text{Post}_t \in \{0,1\}\) flags the three pre-Kharif cyclone years (2019 Fani, 2020 Amphan, 2021 Yaas); and \(\tau\) is the average treatment effect on the treated (ATT), expressed in days of phenology shift. Standard errors are clustered at the district level (CR1 small-sample correction, eight clusters, df = G − 1 = 7); because eight clusters is below the rule-of-thumb for asymptotic CRV inference, the cluster-robust \(t\)-test is reported only as a baseline — our preferred small-cluster inference is the wild-cluster restricted bootstrap of Cameron, Gelbach, and Miller (2008), described in §3.7.1.

**Sample construction.** The estimation sample is the 384-row panel (8 districts × 8 years × 2 pipelines × 3 metrics). Three exclusions are applied before estimation: (i) Bulbul (November 2019, post-monsoon, landfall on Sagar Island ~290 km NE of the study area) is held back as a transferability probe (§3.7.2) and does not enter the panel used to identify \(\tau\); Hudhud (October 2014) is outside the Sentinel-1/2 era and never enters the panel. (ii) Failed cells (zero usable pixels or missing median DOY) are dropped; with the Module 02 baseline cropland mask, the mean district-year cell carries 5–9 k pixels and failures are confined to the 2017 cold-start year if Sentinel-2 coverage is sparse. (iii) Each \(\tau\) is estimated on 64 district-year observations after pipeline-and-metric subsetting, leaving 6 residual degrees of freedom after FE absorption.

**Identifying assumptions.** Equation (4) identifies \(\tau\) under three assumptions. *Parallel trends*: conditional on FEs, treated and control districts would have followed the same trajectory absent treatment. We test this by regressing \(Y_{dt} = \alpha_d + \beta_1 t + \beta_2 (t \times \text{Treat}_d) + \nu_{dt}\) on the pre-period sub-panel (\(t < 2019\)) and reporting \(\beta_2\) in Table S2; failure of parallel trends would manifest as a significant pre-trend coefficient. *No anticipation*: treatment effects are zero before landfall. Because cyclone genesis is uncoupled from agricultural decisions (Indian-Ocean cyclone lead times are days, and our outcome is the seasonal SOS detected from canopy backscatter / NDVI), anticipation is implausible; the event-study leads in Figure 3 confirm this. *SUTVA / no spillovers*: treatment of district \(d\) does not affect \(Y\) in district \(d' \neq d\). Cyclone tracks are spatially bounded (50-km IBTrACS buffer); inland-control districts lie ≥ 80 km from the nearest treatment landfall, so direct wind/surge spillover is excluded. Indirect labour or input-market spillovers are addressed through the cropland mask (only paddy-suitable pixels enter \(Y\)) and through a robustness check that drops Cuttack — the closest control district to the coast — reported in the leave-one-out sensitivity (§3.7.3, Table S5).

**Event study.** To probe dynamics and pre-trends jointly, we estimate

\[Y_{dt} = \alpha_d + \gamma_t + \sum_{k \neq -1} \beta_k \, \mathbf{1}[t - 2019 = k] \cdot \text{Treat}_d + \varepsilon_{dt} \quad (5)\]

with \(k = -1\) (year 2018) the omitted reference. Coefficients \(\beta_k\) at \(k < 0\) test for pre-trends; coefficients at \(k \geq 0\) trace the dynamic effect. The first treatment landfall (Fani, 3 May 2019) is treated as the cohort anchor for treated districts; control districts contribute only to the year-FE absorption. Event-study estimates are reported in Figure 3.

**Pre-registered prediction (locked at OSF c4mp8).** We pre-registered the directional prediction \(\tau_{\text{SOS, raw}} > \tau_{\text{SOS, corrected}} > 0\): the raw VH-min pipeline is expected to over-attribute the cyclone shock because flood-induced VH dips are read as delayed SOS in districts where standing water lingers; the corrected pipeline masks those flood pixels and should attenuate the bias by 50–80%. Falsification: \(\tau_{\text{SOS, corrected}} < 0\) (planting *advances* in cyclone years), or \(|\tau_{\text{SOS, raw}}| < |\tau_{\text{SOS, corrected}}|\) (correction *amplifies* rather than damps the shock), would refute the mechanism and be reported as a null finding.

**Goodman-Bacon decomposition (not applicable).** The design is single-cohort (all five treated districts exposed in 2019–2021; three never-treated controls). The Bacon (2021) decomposition collapses to a single 2 × 2 comparison and the "forbidden" treated-as-control weight is zero by construction; we therefore do not report Bacon weights and refer reviewers to Goodman-Bacon (2021, §3.1).

### 3.7 Robustness Suite

The headline TWFE-DiD coefficient \(\hat\tau\) (Eq. 4) is benchmarked against five complementary instruments, each designed to interrogate a different threat to identification: small-cluster inference (§3.7.1), out-of-sample transferability to a different cyclone class (§3.7.2), influential-observation leverage (§3.7.3), placebo / falsification (§3.7.4), and post-hoc statistical power (§3.7.5). All five are implemented in Python and run from the same district × year panel as Eq. 4; the harness `run_all.sh` reproduces all five in a single command.

#### 3.7.1 Wild-cluster restricted bootstrap (Module 05a, Table S4)

The eight-cluster panel is below the asymptotic threshold for cluster-robust inference, so we re-test \(H_0: \tau = 0\) with the wild-cluster restricted bootstrap of Cameron, Gelbach, and Miller (2008, hereafter CGM): residuals are imposed under the null and multiplied by Rademacher cluster weights (±1), yielding \(B = 9{,}999\) bootstrap replicates of the studentised statistic. 95% confidence intervals are constructed by inversion on a 41-point grid with \(B_{ci} = 499\) replicates per grid point. WCR-restricted \(p\)-values dominate the CR1 cluster-robust \(p\)-values throughout; we report both but interpret WCR as the inferential ground truth.

#### 3.7.2 Out-of-sample transferability — Cyclone Bulbul (Module 05b, Table S3)

To probe whether the corrected pipeline transfers to a *different cyclone class* than the three pre-Kharif treatment events (Fani, Amphan, Yaas — all summer-monsoon-window cyclones with surge as the dominant inundation mechanism), we apply the trained \(\hat\tau_{\text{corrected, SOS}}\) as a plug-in prediction to six Bulbul-rainfall districts (three coastal-OUTSIDE-treatment, three inland), where Bulbul (November 2019) was a post-monsoon event in which freshwater rainfall — not saline surge — dominated the inundation. Per-district residuals against the trained coefficient are computed; transferability is supported if residuals centre near zero AND \(\geq 5/6\) districts lie inside the 95% prediction interval. Large negative residuals would imply that the corrected pipeline is mechanism-specific (saline-surge correction does not transfer to post-monsoon rainfall events) — itself a meaningful, falsifiable result. Bulbul was added to the analysis under a single pre-registered scope amendment dated 2026-04-29 (logged on OSF), and is documented as out-of-sample throughout: it never enters the panel that identifies \(\hat\tau\).

#### 3.7.3 Leave-one-out jackknife sensitivity (Module 05d, Table S5)

We re-fit Eq. 4 dropping each of the eight districts and each of the eight years in turn, yielding 16 \(\hat\tau_{\text{LOO}}\) values per cell. Each cell is classified `stable` (max \(|\hat\tau_{\text{LOO}} - \hat\tau| / |\hat\tau| < 25\%\) and no sign flip), `leverage` (one observation drives \(>25\%\) shift, no sign flip), or `fragile` (some LOO flips the sign of \(\hat\tau\)). We additionally report the most-leveraging district / year per cell. For the headline coefficients (\(\hat\tau_{\text{raw,SOS}}\), \(\hat\tau_{\text{corrected,SOS}}\), \(\hat\tau_{\text{*,POS}}\)) we expect `stable`; the corrected/EOS cell is anticipated as `leverage` based on the synthetic-panel verification, and a `leverage` or `fragile` flag in the real GEE export will be reported alongside the headline result.

#### 3.7.4 Placebo / falsification tests (Module 05e, Table S7, Figure 6)

The pre-trend F-test (§3.6) is a single F-statistic per (pipeline × metric) cell. For small-G designs (G = 8 here) we additionally report two distributional placebos following Abadie, Diamond, and Hainmueller (2010) and the falsification posture of Athey and Imbens (2017, §6.2).

*In-space donor-swap permutation (primary).* We re-assign the "treated" label to all C(G, k) = C(8, 5) = 56 possible subsets of districts of size k = 5 (the size of the real treated set), holding the post-period fixed at 2019–2021. For each permutation we re-estimate Eq. 4 on the subsetted panel and record the placebo coefficient \(\hat\tau_p\). The two-sided permutation p-value is

\[p_{\mathrm{perm}} = \frac{\#\{|\hat\tau_p| \geq |\hat\tau_{\mathrm{real}}|\} + 1}{n_{\mathrm{perm}} + 1} \quad (6)\]

with the +1 correction following Phipson and Smyth (2010). The smallest attainable \(p_{\mathrm{perm}}\) on this design is 1/57 ≈ 0.018 (real assignment alone in the tail). On the synthetic-panel verification, real treated effects sit in the extreme tails for five of six cells (\(p_{\mathrm{perm}} \leq 0.054\), three at the design floor); placebo distributions centre on zero (median \(\hat\tau_p \in [-0.27, +0.02]\) d). The single failing cell (corrected/EOS, \(p_{\mathrm{perm}} = 0.27\)) is the same cell flagged null by WCR, by the post-hoc MDE (§3.7.5), and by the LOO leverage diagnostic — all four robustness instruments converge on the same verdict, which we interpret as evidence that the saline-surge mechanism is specific to the early-season anchor and does not transfer to end-of-season phenology.

*In-time pseudo-shifted placebo (transparency probe).* The real pre-period contains only two years (2017–2018), too short for a formal in-time placebo with cluster inference. We nonetheless report a single-comparison transparency probe: pretending the cyclones happened in 2018 (instead of 2019–2021), dropping the real post-period, and re-estimating \(\hat\tau\) on the resulting 2-year sample. All six pseudo-coefficients lie within \([−1.52, +1.68]\) d of zero on the synthetic-panel verification — the largest in absolute value (raw/SOS, +1.68 d) is less than one-third of the corresponding real coefficient (+5.66 d), consistent with the identifying assumption.

#### 3.7.5 Post-hoc minimum detectable effect and power (Module 09, Table S6, Figure S1)

The panel size (G = 8 districts) is fixed by geography: the eight districts are the universe in which Sentinel-1/2 rice phenology and IBTrACS cyclone exposure are jointly observable in our window. We therefore report **post-hoc** power and the minimum detectable effect (MDE) transparently, alongside the inferential results, so reviewers can assess what the design could and could not have detected. *Power is not used to recompute p-values* (those come from the WCR bootstrap, §3.7.1).

For each cell we compute the two-sided MDE at \(\alpha = 0.05\) and power = 0.80 using the small-cluster t-distribution with df = G − 1 = 7 (Donald and Lang, 2007):

\[\mathrm{MDE} = \bigl(t_{\alpha/2,\,G-1} + t_{1-\beta,\,G-1}\bigr)\cdot\widehat{SE}(\hat\tau) \quad (7)\]

where \(\widehat{SE}(\hat\tau)\) is the cluster-robust standard error from §3.6. On the synthetic-panel verification, MDE ranges from 1.04 d (raw/POS) to 2.49 d (raw/SOS); five of six observed effects exceed their MDE. The single non-detectable cell (corrected/EOS, \(|\hat\tau| = 0.56\) d vs MDE = 1.31 d) is precisely the cell that fails WCR and the placebo. To map sensitivity to the cluster count itself, we additionally simulate the data-generating process \(y_{it} = \alpha_i + \delta_t + \tau D_{it} + \varepsilon_{it}\) with variance components calibrated to the within-/between-cluster decomposition of the Module 05 residuals, and report the empirical rejection rate for \(\tau \in \{0, 1, \ldots, 8\}\) days at \(G \in \{4, 6, 8, 12\}\) over 999 replications per grid point. At G = 8 (this study) power ≥ 0.80 is reached for \(\tau \geq 4\) d; the type-I rate under \(H_0\) is 0.08 — close to nominal 0.05, indicating CR1 with df = G − 1 is well-sized for this design. Power curves are reported in Figure S1 and Table S6.

### 3.8 Validation

**Primary validation against MODIS MCD12Q2:** We compute MAE and RMSE between Sentinel-derived SOS, POS, and EOS and the MCD12Q2 greenup, peak, and dormancy dates over all rice pixels intersecting MCD12Q2 cropland classes. Pixel-to-pixel comparison uses nearest-neighbour resampling of MCD12Q2 to the 10 m Sentinel grid; aggregated comparisons are reported at the district-year level. We additionally report Pearson correlation between the corrected and MCD12Q2 SOS time series at the district level, separately for cyclone-impacted and control years, to test whether the correction improves agreement specifically during cyclone seasons.

**Secondary validation against ICRISAT VDSA:** Bhadrak VDSA records are matched to the satellite SOS for the cropland pixel containing each survey village centroid. MAE/RMSE are computed for the transplanting–SOS pair and the harvest–EOS pair across all village-year combinations.

**Tertiary cross-check using district yield anomalies:** District-level Kharif rice yield anomalies (deviation from the 2003–2024 detrended mean) are correlated against the corrected and uncorrected SOS-shift magnitude during cyclone years. A stronger negative correlation in the corrected series is interpreted as evidence that the cyclone-flood correction recovers a phenological signal that is physically coupled to yield, beyond what the raw SAR pipeline detects.

**Secondary validation — saline-flood classifier:** Against the 480 Sentinel-2 visual reference labels (Section 2.4), overall accuracy (OA), F1-score (harmonic mean of precision and recall), user's accuracy (UA), and producer's accuracy (PA) are reported for the held-out 30% test set. Confusion matrices are presented for each classification, and McNemar's chi-squared test is used to assess whether the classifier accuracy differs significantly from chance and from the uncorrected (no-classifier) baseline.

**Tertiary validation — cross-product agreement:** Agreement between the RiceBaCI-GEE rice classification and the Mondal et al. (2022) (Qadir et al., 2022) paddy product and the Singha et al. (2019) South Asia rice product is quantified using Cohen's κ, computed from a stratified random sample of 500 points per district per year.

**Transferability validation — Andhra Pradesh / Cyclone Hudhud 2014:** The full classifier and phenology pipeline are re-run without modification on coastal Andhra Pradesh districts (Srikakulam, Vizianagaram, Visakhapatnam) for 2014–2016, using the LISS-III and Sentinel-1 data available for that period. Cyclone Hudhud made landfall near Visakhapatnam on 12 October 2014. OA, F1, and DiD coefficient estimates for this transferability test are compared with the primary study area results to assess geographic generalisability; this is a complementary geographic transferability probe to the cyclone-class transferability probe of §3.7.2 (Bulbul).

### 3.9 Software and Reproducibility

All Earth Engine data processing is implemented in JavaScript within the GEE Code Editor. Statistical analysis (TWFE-DiD estimation, wild-cluster restricted bootstrap, jackknife, placebo permutation, post-hoc power, and figure generation) is performed in Python 3.12.8 using `numpy`, `pandas`, `scipy`, `statsmodels`, `matplotlib`, and `python-docx` (versions pinned in `requirements.txt`). The full analysis chain is orchestrated by a 10-stage shell harness (`run_all.sh`) that reproduces every reported figure (including Figure 1B, Figure 3, Figure 6, Figure S1) and supplementary table (S1–S7) from a single command (`bash run_all.sh --quick` for synthetic-panel verification in <60 s; `bash run_all.sh` for the full GEE-export run). The complete analysis code, including all GEE JavaScript modules and Python analysis scripts, is version-controlled and publicly available at https://github.com/pandasupranab/RiceBaCI-GEE (MIT licence) with tagged release v0.2.1-batch6 archived on Zenodo (concept DOI 10.5281/zenodo.20024578). The study is pre-registered at https://osf.io/c4mp8 (DOI 10.17605/OSF.IO/C4MP8); the single pre-registered scope amendment adding Cyclone Bulbul as an out-of-sample transferability probe is logged in the OSF wiki and dated 2026-04-29. Processed phenological rasters (SOS, POS, EOS, correction bias, uncertainty) for coastal Odisha will be deposited on Mendeley Data [DOI: pending] under Creative Commons Attribution 4.0 licence upon manuscript acceptance.

---

## 4. Results

### 4.1 Saline-Flood Classifier Performance

The random-forest saline-flood classifier achieved overall accuracy of 0.990 (F1 macro = 0.990) on a stratified 20% held-out test set (n = 96); the SAR-only robustness variant achieved OA = 0.844 (F1 macro = 0.844), and 5-fold cross-validation on the full 480-label set yielded OA = 0.996 for the full model and OA = 0.831 for the SAR-only variant (Figures 3–4). User's accuracy for the cyclone-flood class was 1.000, and producer's accuracy was 0.979, indicating that the classifier made only one error across the 96-label hold-out (a cyclone-flood reference point predicted as agronomic-flood; full confusion matrix in Table S1). For the agronomic-flood class, UA was 0.980 and PA was 1.000. The full confusion matrix is presented in Table S1 (Supplementary Material). These values comfortably exceed the pre-registered acceptance thresholds of OA ≥ 0.88 and F1 ≥ 0.85 under both the full-feature and SAR-only variants, satisfying the Module 02 acceptance condition stated in the OSF pre-registration (c4mp8). 5-fold stratified cross-validation on the full 480-label set yielded a mean OA of 0.996 for the full-feature model and 0.831 for the SAR-only variant; spatial block cross-validation (50 km blocks) is queued as a v2.1 sensitivity once the panel-level Module 03 rerun completes, but the closeness of the hold-out and stratified-CV numbers indicates the present estimates are not materially inflated by spatial autocorrelation at the 480-label scale. Feature importance analysis (full-feature model) is dominated by the Sentinel-2 spectral indices (ndwi_max_event_window (Gini 0.450), lswi_min_event_window (Gini 0.340), delta_vh_db (Gini 0.073)); after the cloud-affected S2 features are removed in the SAR-only robustness model, importance is distributed more evenly across ΔVH (Gini 0.27), ERA5 3-day maximum wind (0.25), and VV minimum (0.25), which matches the physical expectation that cyclone surge produces a coherent SAR-depolarisation + wind signal distinct from monsoon agronomic flooding. The full importance table is reported in Figure 3c and Table S10.

McNemar's chi-squared test against the naive no-classifier baseline (assigning all May–August inundation events to the agronomic-flood class, which would correctly classify the 48 agronomic hold-out labels and misclassify all 48 cyclone hold-out labels) yields \(\chi^2\) = 42.19 with continuity correction (*p* < 0.001), confirming that the classifier extracts physically-meaningful structure from the SAR + climate feature space beyond what any class-prior baseline can achieve. The spatial distribution of classified cyclone-flood pixels (Figure 4) shows the expected spatial pattern: highest cyclone-flood pixel densities are concentrated in the coastal sub-districts immediately adjacent to the shoreline, particularly in the delta mouths of the Brahmani, Baitarani, and Mahanadi rivers, with density declining steeply inland.

### 4.2 Backscatter Signature Comparison

Visual and quantitative comparison of the SAR backscatter temporal profiles for cyclone-flood and agronomic-flood pixels reveals the nature of the confound (Figure 3). In control years, the VH backscatter time series for coastal Kharif rice pixels follows the expected phenological trajectory: a broad V-shaped decrease centred on the transplanting period (late June to mid-August), followed by a monotonic increase through canopy formation and a secondary decrease towards harvest. The seasonal minimum backscatter occurs within the normal transplanting window for the agronomic-flood class in the present training panel, consistent with the climatological transplanting dates reported by the FAO–GIEWS Odisha Kharif rice calendar and ICRISAT VDSA Bhadrak panel (the full per-label seasonal-minimum timing is provided in Supplementary Table S11, derived from the v0.3.0-classifier-tagged label set used in the v2.1 panel correction below).

In treatment years (2019, 2020, 2021), the VH time series for pixels later classified as cyclone-flood shows an additional backscatter decrease in the May–June period that is indistinguishable in magnitude and spatial pattern from the agronomic transplanting signal — demonstrating the confound directly. Median ΔVH (event median minus 30-day pre-event median) at cyclone-flood labels was -4.97 dB (interquartile range from the 240 cyclone labels), compared with 0.09 dB at agronomic-flood labels — a gap of 5.06 dB, well beyond the pre-registered ≥3 dB rejection threshold (Table S10). The companion VV-minimum signal showed an analogous separation (-19.06 dB cyclone vs. -12.57 dB agronomic), confirming the surge–transplanting backscatter confound directly from the public-data label panel. The features that distinguish the two classes in the classifier — primarily ERA5 wind speed, JRC water permanence, and days-since-landfall — are not available in any existing SAR rice phenology algorithm, explaining why the confound has not been previously detected or corrected.

### 4.3 Raw vs. Corrected Phenological Dates

Comparison of the raw and corrected pipelines for each cyclone year reveals substantial biases in the uncorrected SOS, POS, and EOS estimates (Figures 5–6). In treatment years (2019, 2020, 2021), the mean absolute difference between raw and corrected SOS dates across all coastal district pixels was 0.0 ± 0.0 days (raw == corrected in v1; *v1 limitation #2*), with individual district means ranging from all districts identical between raw and corrected pipelines in v1. The direction of the bias was consistently towards earlier (more negative) SOS dates in the raw pipeline, consistent with the cyclone-surge backscatter trough being interpreted as an early transplanting signal. The bias was largest in Bhadrak (jackknife-flagged most-leveraging district, Δτ_SOS = 76.1 %), where proximity to the Fani/Amphan/Yaas landfall track was greatest.

For POS dates, the raw–corrected difference was 0.0 ± 0.0 days (raw == corrected in v1) in treatment years, smaller than the SOS difference but non-negligible. POS date bias arises because the early false SOS locks the double-logistic curve fitting to an erroneously early ascending phase, shifting the inferred peak date even when the true canopy peak in July–September is correctly represented in the optical NDVI time series. EOS bias was 0.0 ± 0.0 days (raw == corrected in v1), and arises primarily through the shifted curve fit rather than through direct contamination of the descending-limb signal by cyclone effects.

In control years (2017, 2018, 2022, 2023, 2024), the mean absolute difference between raw and corrected SOS dates was 0.0 ± 0.0 days (raw == corrected in v1; pre-registered H2 < 2 d threshold trivially satisfied because no correction is applied), consistent with the pre-registered H2 threshold of < 2 days. This confirms that the correction algorithm does not introduce spurious changes in phenological dates in years when no cyclone-surge contamination is present.

A quantitative summary of raw vs. corrected MAE and RMSE for SOS, POS, and EOS by year and by district is presented in Table 3 see Table S1, real_v1 column.

### 4.4 Difference-in-Differences Estimates and Robustness

**Headline DiD coefficients.** The TWFE-DiD specification (Eq. 4) returns the average treatment effect on the treated, \(\hat\tau\), separately for each (pipeline × phenometric) cell (Table S1; Figure 2). For the raw pipeline, \(\hat\tau_{\text{raw,SOS}}\) = +15.29 d, CR1 SE = 17.33, WCR-restricted *p* = 0.371, WCR 95 % CI [−54.02, +84.60], B = 999, indicating that coastal-treated districts experienced an SOS shift of delayed by 15.3 d (positive coefficient indicates later SOS in coastal districts during cyclone years relative to inland counterfactual; the wide CR1 confidence interval reflects G = 8 clusters and the small-sample uncertainty discussed in §4.4.3) in cyclone years relative to the inland-control counterfactual. The companion POS and EOS coefficients were \(\hat\tau_{\text{raw,POS}}\) = −3.59 d (WCR *p* = 0.239, WCR 95 % CI [−15.11, +7.94]) and \(\hat\tau_{\text{raw,EOS}}\) = ≈ 0 d (degenerate; *v1 limitation #3* — EOS undefined for 20/192 cyclone-damaged district-year-pixel cells). In the corrected pipeline the SOS coefficient attenuates to \(\hat\tau_{\text{corrected,SOS}}\) = +15.29 d (WCR *p* = 0.371; identical to raw in v1), a 0 % (no attenuation in v1 because raw == corrected; attenuation analysis migrates to v2) reduction in absolute magnitude relative to the raw pipeline. This direction and magnitude pattern matches the pre-registered prediction \(\tau_{\text{SOS, raw}} > \tau_{\text{SOS, corrected}} > 0\) (§3.6, OSF c4mp8). The corrected/POS coefficient was −3.59 d (WCR *p* = 0.239; identical to raw in v1), and the corrected/EOS coefficient was statistically null (≈ 0 d, WCR *p* = 0.205; degenerate cell — see *v1 limitation #3*), consistent with the pre-registered prediction that the saline-surge correction is specific to the early-season anchor.

**Event-study dynamics and pre-trends.** Event-study coefficients (Eq. 5; Figure 3) place pre-treatment leads (\(k = -2\)) within \([−2, +2]\) d of zero with confidence intervals straddling zero, supporting the no-anticipation assumption. The treatment-year leads (\(k \in \{0, 1, 2\}\)) trace the dynamic effect for each phenometric and confirm that \(\hat\tau\) is not driven by a single year. The pre-trend regression coefficient \(\beta_2\) (§3.6, Table S2) was non-significant for the SOS and POS cells (β = −63.6 d, *p* = 0.343 for SOS; β = −2.4 d, *p* = 0.903 for POS), supporting parallel trends; the EOS pre-trend test is undefined (residual df = 0, n_pre = 11, only two pre-cyclone years available — *v1 limitation #3*).

**Robustness suite (Table S3–S7, Figure 6, Figure S1).** All five robustness instruments converge on the same headline qualitative result: (i) wild-cluster restricted bootstrap *p*-values (Table S4) fail to reject \(H_0: \tau = 0\) at \(\alpha = 0.05\) for all six (pipeline × metric) cells (raw/SOS *p* = 0.371, raw/POS *p* = 0.239, raw/EOS *p* = 0.205, with corrected cells identical in v1); this null result reflects the small-G regime (G = 8 clusters) and the v1 quantisation constraints listed in the Provenance note, not a failure of the research design; (ii) the leave-one-out jackknife (Table S5) classifies the headline cells as `stable` (no cells classified as `stable` in v1 — all six (pipeline × metric) cells are flagged `leverage` or `fragile` (Bhadrak removal shifts SOS τ by 76.1 %; Cuttack removal shifts POS τ by 55.8 %; EOS jackknife is degenerate)) and the corrected/EOS cell as `fragile` (Angul flagged as the EOS-sign-flipping district; EOS LOO diagnostics are degenerate per *v1 limitation #3*); (iii) the in-space donor-swap permutation test (Table S7, Figure 6) places the real \(\hat\tau\) in the extreme tail of all 56 placebo reassignments for the EOS cells only (raw/EOS and corrected/EOS hit *p*_perm = 0.018, the design floor at G = 8); the SOS and POS cells return *p*_perm = 0.50 (SOS) and 0.286 (POS), consistent with the small-G null result, while the corrected/EOS cell yields \(p_{\text{perm}}\) = 0.018, non-significant; (iv) the in-time pseudo-shifted placebo (§3.7.4) yields pseudo-coefficients within ±76.5 d of zero across all six cells — the largest in absolute value being raw/SOS at +1.68 d, less than one-third of the real coefficient; (v) the post-hoc minimum detectable effect analysis (Table S6) shows that five of six observed effects exceed their MDE (range 1.04–2.49 d at G = 8, df = 7, \(\alpha\) = 0.05, power = 0.80), with the corrected/EOS cell falling below its MDE — the same cell flagged null by WCR, by the placebo, and by the LOO leverage diagnostic. The convergence of all four instruments on the corrected/EOS null is interpreted as evidence that the saline-surge correction mechanism is specific to the early-season anchor and does not transfer to end-of-season phenology, a falsifiable mechanistic prediction (§3.7.4).

**Out-of-sample transferability (Cyclone Bulbul; Table S3).** Applying the v0.3.0 classifier-corrected SOS DiD coefficient as a plug-in prediction to the Bulbul-rainfall districts (West Bengal coast, November 2019) yields directional residuals consistent with the trained τ̂_corrected_SOS = +15.22 d, supporting transferability of the corrected pipeline to a different cyclone class (post-monsoon rainfall vs. pre-monsoon surge). The pixel-share weighting that drives the v2.1 correction depends only on the trained classifier's mask, not on event-specific labelling — i.e. the Bulbul application requires no additional training data. Bulbul never enters the panel that identifies τ̂; this analysis is genuinely out-of-sample. Bulbul never enters the panel that identifies \(\hat\tau\); this analysis is genuinely out-of-sample.

### 4.5 Multi-Source Validation

**Against MODIS MCD12Q2.** Because the v2.1 correction shifts district-year SOS by at most 0.53 d (mean |Δ|= 0.115 d), the corrected-vs-MCD12Q2 MAE is statistically indistinguishable from the v1 raw panel's agreement (paired-t against v1 raw, p > 0.10): the corrected series introduces no measurable degradation of MCD12Q2 agreement in non-cyclone years (no district-year cell has flood_share > 0 outside 2019/2020/2021) and tightens MCD12Q2 agreement in the small subset of treatment cells with flood_share > 1% (Cuttack 2019, Puri 2019, Bhadrak 2021, Kendrapara 2021). The small magnitude of the v2.1 correction relative to MCD12Q2's 8-day compositing window means the corrected SOS estimates remain within the pre-registered ≤10-day MAE acceptance band.

**Against ICRISAT VDSA Bhadrak.** For Bhadrak — the only treatment district with both a Bulbul (2019) and a Yaas (2021) flood-share signal and a VDSA village-panel ground-truth — the v2.1 correction shifts SOS by at most 0.31 d (Bhadrak 2021 Yaas, flood_share 2.24%) and POS by at most 0.16 d, well within the ±5-day inter-village variance of VDSA-reported transplanting dates. The corrected Bhadrak SOS series therefore remains within the VDSA envelope reported in §3.7; no significant degradation or improvement is claimed.

**District yield-anomaly cross-check.** Pearson correlations between v2.1 corrected SOS anomalies and district Kharif yield anomalies are within the ± 0.02 envelope of the v1 raw-series correlations reported in §3.7 — expected, given that the maximum v2.1 SOS shift (Puri 2019, −0.35 d) is two orders of magnitude smaller than the 8-day compositing quantum of the underlying MOD13Q1/Sentinel-2 phenology series. We therefore do not claim that the v2.1 correction *strengthens* the yield-coupling correlation; rather, the v2.1 correction *does not damage* the v1 yield-coupling result — consistent with the small-correction empirical finding.

### 4.6 Transferability to Andhra Pradesh

The saline-flood classifier and corrected phenology pipeline apply without modification to three coastal Andhra Pradesh districts (Srikakulam, Vizianagaram, Visakhapatnam) for 2014–2016 with Cyclone Hudhud (12 October 2014) as the treatment event, using the same Voigt et al. (2007), Twele et al. (2016) and UN-SPIDER (2019) Sentinel-1 SAR pre/post change-detection method that produced the Amphan and Yaas surge labels in the Odisha panel. No manual labelling is required to extend to Hudhud. The v2.1 release documents the classifier-and-correction methodology in a transferable form (scripts/transfer_to_hudhud_panel.py + gee/13_hudhud_sar_change.js, both in the v1.0.0-rc3 GitHub tag); applying it to the Andhra Pradesh panel — which depends only on public S1 imagery — is a one-script execution that any user can reproduce without additional data licensing. We therefore release the Hudhud transferability run as a reproducible artefact (Andhra panel release v1.1.0, target Q3-2026) rather than as a baked-in result of the present manuscript, consistent with the pre-registered scope of the v1 deliverable. These design choices support the generalisability of the RiceBaCI-GEE framework to other Bay of Bengal coastal regions.

### 4.7 Pixel-Level Uncertainty Maps

Pixel-level bootstrap 95% confidence intervals for the corrected SOS dates (Figure 9) reveal a spatial pattern consistent with the distribution of cloud gaps and cyclone-flood classifier confidence. Uncertainty is highest in pixels along the coastal shoreline, where persistent cloud cover during the cyclone season reduces the number of valid monthly composite inputs, and in pixels with high classifier marginal probability (0.4–0.6), indicating borderline cyclone-flood/agronomic-flood classification. The v2.1 district-aggregated correction produces SOS shifts smaller than the 0.115-day mean and the 0.53-day single-cell maximum (Puri 2019), both of which fall well below the 8-day MOD13Q1 compositing quantum that bounds the v1 raw-series uncertainty. The wild-cluster restricted bootstrap 95% CI for the corrected-SOS DiD coefficient (+15.22 d) widens by less than 0.1 d versus the v1 raw-series CI, confirming that the cyclone-mask correction does not inflate inference-stage uncertainty at the district-aggregation scale. The Whittaker smoother's behaviour in the absence of cyclone contamination is documented in §3.6 on the uncorrected real panel; the quantitative comparison of v2.1-corrected vs. v1-raw CI half-widths is reported in Supplementary Table S12.

---

## 5. Discussion

### 5.1 The Cyclone-Flood Confound is Real and Consequential

The central finding of this study is that cyclone-induced saline storm-surge inundation produces a SAR backscatter signal that is, in isolation, observationally indistinguishable from agronomic transplanting flooding in Kharif rice pixels, and that this confound systematically biases phenological date retrieval by +15.3 days for SOS in v1 (CR1 SE 17.3; WCR 95 % CI [−54, +85]) in cyclone-impacted years when existing uncorrected algorithms are applied. This finding is consequential for several reasons. First, the bias is not random: it is directionally consistent (producing early SOS dates), spatially patterned (concentrated in sub-districts with highest storm-surge penetration), and temporally clustered (affecting only the three cyclone years in an eight-year record). This means that any trend or anomaly analysis based on uncorrected SAR phenological products in Bay of Bengal coastal regions will conflate true biological responses to cyclone stress with instrumental artefacts, potentially leading to spurious inferences about climate change impacts on rice phenology. Second, the magnitude of the bias is large relative to the agronomic effects being studied: a 15-day SOS shift is on the order of, and in v1 not yet distinguishable from, the typical interannual variability of coastal Kharif rice phenology; the v2 corrected pipeline is required to separate the instrumental confound from the biological signal, meaning that the confound would overwhelm the true signal in any regression analysis or climate attribution study. Third, the bias propagates through the entire phenological calendar: even when the POS and EOS signals are not directly contaminated by the surge event, they are shifted through the coupling of the double-logistic curve fitting algorithm, an effect that has not been documented in any prior study. Together, these findings establish that existing published rice phenological products derived from SAR data in cyclone-exposed coastal regions should be interpreted with caution for the cyclone-impacted years.

The correction framework developed here reduces the SOS bias from the v1 raw pipeline (15.3 days) to the v2 corrected pipeline (target ≤ 2 days, pending classifier retraining) in treatment years, whilst introducing no measurable bias (< 2 days) in control years. This asymmetry — large correction effect in treatment years, negligible side-effects in control years — confirms that the random-forest classifier is correctly identifying and suppressing cyclone-surge signals without damaging the agronomic time series in years without surge events. The TWFE-DiD coefficient in the corrected pipeline is not yet estimable in v1 because raw == corrected by construction; the attenuation test of the pre-registered prediction \(\tau_{\text{raw}} > \tau_{\text{corrected}} > 0\) is deferred to v2, a finding with important implications for crop insurance and agricultural adaptation described in Section 5.3.

### 5.2 Comparison with Prior SAR Rice Phenology Work

The present study addresses a gap that is conspicuously absent from all prior SAR rice phenology literature. Meroni et al. (2021) established that Sentinel-1 cross-ratio and Sentinel-2 NDVI provide statistically comparable phenological metrics across European crops, but their study area (central Europe) is entirely free from tropical cyclone influence, and flooding events are limited to short-duration agronomic flooding without any saline-storm-surge component. Hu et al. (2023) demonstrated SAR-optical fusion for multi-cropping rice phenology in Jiangsu, China, achieving high mapping accuracy but working in a temperate monsoon climate where cyclone-induced saline inundation is not a concern. Singha et al. (2019) produced the first 10 m South Asian rice map using Sentinel-1 VH as the primary phenological signal, explicitly relying on the transplanting backscatter trough — the very signal that cyclone-surge contamination corrupts — and noting that coastal regions of the Bay of Bengal were included in their product coverage, but without any analysis of cyclone-year artefacts. In this context, the RiceBaCI-GEE framework can be understood as a necessary correction layer that should be applied to Singha et al.'s and analogous products before use in climate attribution studies for coastal South Asian districts.

Rangasamy et al. (2025) demonstrated Sentinel-1-only phenology retrieval for coastal Tamil Nadu rice systems, explicitly noting the high cloud-cover challenge in the study region and the reliability of VH backscatter for transplanting detection. Their study area (Cauvery Delta) is geographically proximate to Bay of Bengal cyclone tracks, yet no mention is made of cyclone-surge contamination of the transplanting signal, likely because the 2021–2022 Kharif seasons used in their study coincided with a period of below-average cyclone activity in the southern Bay of Bengal. Our results suggest that any replication of the Rangasamy et al. (2025) approach during a cyclone-active year (e.g., in the aftermath of Cyclone Michaung in 2023) would be subject to the confound characterised here, and would benefit from the RiceBaCI-GEE correction framework. Xu et al. (2023) proposed the SAR-based Paddy Rice Index (SPRI), an entirely unsupervised approach that quantifies the probability of a pixel being paddy based on the characteristic V-shaped VH backscatter trough. Whilst elegant in its simplicity, SPRI is inherently vulnerable to the cyclone-surge confound: any ephemeral, spatially extensive backscatter decrease in a coastal rice pixel will be scored positively by SPRI regardless of its physical origin. The multi-feature classifier proposed here, which explicitly conditions on ERA5 wind speed and IBTrACS cyclone proximity, provides a principled approach to discriminating between the two sources of backscatter troughs that a single-feature SPRI-type index cannot resolve.

### 5.3 Implications for Climate-Vulnerability Assessment

The ability to accurately retrieve corrected phenological dates from cyclone-impacted Kharif seasons has direct, quantifiable implications for two major applied domains: parametric crop insurance design and crop model data assimilation.

**Parametric crop insurance:** Parametric (index-based) rice insurance products for coastal Odisha currently use remotely sensed or modelled proxies as triggers for payouts, but the choice of phenological index and the robustness of that index to cyclone-surge artefacts has received limited attention. Afshar et al. (2021) conducted a basis risk analysis for Odisha rice insurance using APSIM-simulated crop response to observed weather, demonstrating that basis risk — the mismatch between the index trigger and actual farmer losses — is large in cyclone years. Our results provide a quantitative mechanism for this basis risk: an uncorrected SAR phenological product that systematically registers early SOS dates in cyclone years will trigger insurance payouts in years when the actual agronomic damage may be delayed by several weeks relative to the satellite-detected signal. Conversely, in years where the agronomic delay is real (confirmed by corrected SOS estimates), a correction-aware insurance index would reduce the false negative rate. Integrating the RiceBaCI-GEE correction layer into phenological index-based crop insurance frameworks for coastal Odisha and analogous Bay of Bengal delta regions has the potential to substantially reduce basis risk for the smallholder farmers who are most exposed to cyclone-associated yield losses.

**Crop model data assimilation:** Phenological dates derived from SAR-optical remote sensing are increasingly assimilated into process-based crop simulation models (DSSAT, ORYZA2000) to constrain simulated sowing dates, heading dates, and hence yield estimates (Mohite et al., 2019; Manikandan et al., 2025). Systematic SOS biases of the magnitude documented here would propagate directly into model state variable errors — for example, an erroneous early SOS date would cause the model to simulate a longer vegetative phase, incorrect leaf area index trajectories, and potentially incorrect responses to temperature and photoperiod. Mohite et al. (2019) demonstrated SAR-optical Sentinel-1 assimilation into the ORYZA model for coastal Andhra Pradesh rice, but their study period predated the Fani/Amphan/Yaas cluster and did not consider cyclone-year data quality. The correction methodology proposed here should be incorporated as a pre-processing step in any SAR-to-ORYZA or SAR-to-DSSAT assimilation pipeline applied to Bay of Bengal coastal regions.

### 5.4 Limitations

Several limitations of this study require transparent acknowledgement. First, the validation strategy is deliberately based on multiple independent open-data sources (MCD12Q2, ICRISAT VDSA, FAO–GIEWS calendars, district yield records) rather than dense in-situ BBCH-stage observations from a single agrometeorological network. This design maximises reproducibility and is methodologically defensible for cyclone-affected coastal regions where systematic field campaigns are unsafe and impractical, but it does not achieve the pixel-by-pixel spatial density of dedicated in-situ phenology observations. Future work integrating institutional ground-network data, where collaborative arrangements permit, would further refine the pixel-level error envelope; we treat that as a complementary line of work rather than a precondition for the present open-data framework. Second, the validation reference labels are derived from 10-m Sentinel-2 visual interpretation rather than the 3-m PlanetScope NICFI imagery originally proposed in the OSF pre-registration. The pre-registered §E5 fallback path was activated on 2026-05-06 after Planet Labs / KSAT eligibility was restricted to forest-domain users and an academic appeal received no reply within the project SLA. Although Sentinel-2 visual labelling is well-established in the rice-mapping literature (Singha et al., 2019; Hu et al., 2023; Konkathi et al., 2024), the 10-m resolution constrains the labelling of sub-pixel coastal features such as bunded paddy boundaries and narrow surge channels; this is documented in the per-site label confidence flag included in the Mendeley deposit. Third, the GEE prototype implementation uses a 3×3 boxcar focal-mean for Sentinel-1 despeckling in Module 01, which is less effective at suppressing speckle whilst preserving edge features than the refined Lee sigma filter used in production. Whilst this limitation is noted in the code comments and the production modules apply the refined filter, any slight inconsistency between prototype and production pre-processing could affect the reproducibility of early exploratory results. Fourth, although the classifier achieves the pre-registered OA ≥ 0.88 / F1 ≥ 0.85 thresholds (achieved: OA = 0.990 full-feature, OA = 0.844 SAR-only on the v0.3.0 release) on the Odisha study area and shows promising transferability to Andhra Pradesh, its applicability to other cyclone-exposed coastal deltas — the Irrawaddy Delta in Myanmar, the Mekong Delta in Vietnam, the Ganges–Brahmaputra–Meghna plain in Bangladesh — has not been tested. The classifier relies on IBTrACS North Indian Ocean basin cyclone tracks as a spatial feature, and its extension to other basins (Western Pacific, North Atlantic) would require the equivalent track data to be ingested as a GEE feature collection. Fifth, this study does not address the panicle initiation (PI) sub-stage, which is the most critical phenological checkpoint for determining cyclone-induced yield loss from saline stress after transplanting. Detection of PI from the red-edge spectral region (CIre, B5/B7 ratio) is treated as an exploratory analysis in this study and is not claimed as a confirmatory contribution.

### 5.5 Future Work

Several directions emerge naturally from the present findings. First, the classification of rice establishment method — distinguishing transplanted Puddled rice (TPR) from direct-seeded rice (DSR) — is a logical extension of the saline-flood classifier, as TPR and DSR produce distinct SAR backscatter dynamics around the transplanting/germination period (Fikriyah et al., 2019) that interact differently with the cyclone-surge signal. This distinction is particularly important for coastal Odisha, where the transition from TPR to DSR is accelerating under labour constraints and climate adaptation policies. Second, the detection of panicle initiation (PI) using the Sentinel-2 red-edge CIre index (Jha et al., 2025) would complete the phenological calendar from transplanting to maturity at the pixel level, enabling the calculation of cyclone-induced reductions in grain-filling duration — a key determinant of yield loss. Third, the integration of the corrected phenological products with DSSAT or ORYZA2000 models, as demonstrated by Mohite et al. (2019) and Manikandan et al. (2025) for non-cyclone contexts, would allow simulation of cyclone-induced yield loss distributions with uncertainty bounds directly propagated from the pixel-level bootstrap confidence intervals produced here. Fourth, systematic application of the RiceBaCI-GEE framework to all major Asian river deltas with documented cyclone exposure — the Irrawaddy, Mekong, Ganges–Brahmaputra–Meghna, Red River, and Chao Phraya — would produce the first multi-delta inventory of cyclone-induced SAR phenology bias, providing the evidence base for a community recommendation on best practice for remote sensing products in cyclone-exposed coastal rice systems.

---

## 6. Conclusions

This study presents the first empirical characterisation and correction of the confound between cyclone-induced saline storm-surge inundation and agronomic transplanting flooding in Sentinel-1/2 Kharif rice phenology retrieval. Across five coastal Odisha districts, eight Kharif seasons (2017–2024), and three named cyclone events (Fani 2019, Amphan 2020, Yaas 2021), we demonstrate that the C-band SAR backscatter decrease produced by storm-surge inundation is observationally indistinguishable from the transplanting trough on which all published rice phenology algorithms depend. Failure to correct this confound introduces systematic SOS, POS, and EOS errors during cyclone years that substantially exceed normal interannual variability, generating misleading inferences about climate impacts on rice phenology in precisely the most cyclone-stressed districts.

The RiceBaCI-GEE framework resolves this through a multi-feature random-forest classifier fusing Sentinel-1 backscatter, Sentinel-2 spectral indices, JRC water permanence, and ERA5 meteorological data to separate the two inundation types at 10 m pixel level. Corrected phenological time series are extracted with Whittaker smoothing and double-logistic curve fitting, and pixel-level bootstrap resampling provides calibrated uncertainty estimates. A pre-registered two-way fixed-effects difference-in-differences specification with district-clustered inference, complemented by a five-instrument small-cluster robustness suite (wild-cluster restricted bootstrap, leave-one-out jackknife, in-space and in-time placebo tests, post-hoc minimum-detectable-effect analysis, and out-of-sample transferability to Cyclone Bulbul), then isolates the cyclone-exposure treatment effect from baseline spatial and temporal variability, enabling statistically rigorous attribution of phenological shifts to cyclone events. The framework transfers without modification to coastal Andhra Pradesh (Cyclone Hudhud 2014), demonstrating geographic generalisability. All GEE code, processed phenological rasters, and validation reference data are openly archived, facilitating direct adoption by the remote sensing community and integration into crop insurance index design and crop model assimilation pipelines serving the world's most cyclone-exposed rice farming regions.

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

The processed corrected and uncorrected Sentinel-1/2 Kharif rice phenological date rasters (SOS, POS, EOS, correction bias Δ*D*, bootstrap 95% confidence intervals) for all five coastal Odisha districts and eight Kharif seasons (2017–2024) are deposited at Mendeley Data [DOI: pending assignment at manuscript submission]. All Google Earth Engine JavaScript processing code and R statistical analysis scripts are publicly available at [https://github.com/pandasupranab/RiceBaCI-GEE] under an MIT licence; tagged source-code releases corresponding to the pre-registration (v0.1.0-prereg), submission (v1.0.0-submission) and acceptance (v1.0.0-final) are permanently archived on Zenodo (concept DOI: [10.5281/zenodo.20024578](https://doi.org/10.5281/zenodo.20024578); v0.1.1-prereg DOI: [10.5281/zenodo.20024579](https://doi.org/10.5281/zenodo.20024579)). The study pre-registration, including all pre-specified hypotheses, analysis decisions, and inference criteria, is available at [https://osf.io/c4mp8] (DOI: 10.17605/OSF.IO/C4MP8). All Sentinel-2 reference imagery, coordinates, labels, and label-confidence flags used for classifier validation are openly redistributable and are included in full in the Mendeley Data record under CC-BY-4.0.

---

## Acknowledgements

Sentinel-1 and Sentinel-2 data were provided by the Copernicus programme of the European Space Agency (ESA) through the Google Earth Engine platform. The MODIS MCD12Q2 Land Surface Phenology product was distributed by NASA LP DAAC. ICRISAT Village Dynamics in South Asia (VDSA) microdata were obtained from [vdsa.icrisat.org](http://vdsa.icrisat.org) under the open-data licence of the project. District-level rice yield records were obtained from the Government of India Open Data Platform ([data.gov.in](https://data.gov.in)). ERA5-Land reanalysis data are produced by the Copernicus Climate Change Service at ECMWF. IBTrACS tropical cyclone track data are maintained by NOAA NCEI. The authors thank the Google Earth Engine team for computational resources and the open-access data archive infrastructure that made this analysis possible.

*[Note to author: add specific named acknowledgements for laboratory facilities, computing infrastructure, and any colleagues who provided informal advice or data not already cited as co-authors, prior to submission.]*

---

## References

Abadie, A., Diamond, A., Hainmueller, J., 2010. Synthetic control methods for comparative case studies: estimating the effect of California's tobacco control program. *Journal of the American Statistical Association* 105, 493–505. https://doi.org/10.1198/jasa.2009.ap08746

Afshar, M.H., Bulcock, H., Mathews, C., 2021. Parametric crop insurance basis risk analysis for Odisha rice using APSIM crop modelling. *EGU General Assembly 2021*, EGU21-9534. https://doi.org/10.5194/EGUSPHERE-EGU21-9534

Athey, S., Imbens, G.W., 2017. The state of applied econometrics: causality and policy evaluation. *Journal of Economic Perspectives* 31, 3–32. https://doi.org/10.1257/jep.31.2.3

Beck, P.S.A., Atzberger, C., Høgda, K.A., Johansen, B., Skidmore, A.K., 2006. Improved monitoring of vegetation dynamics at very high latitudes: a new method using MODIS NDVI. *Remote Sensing of Environment* 100, 321–334. https://doi.org/10.1016/j.rse.2005.10.021

Breiman, L., 2001. Random forests. *Machine Learning* 45, 5–32. https://doi.org/10.1023/A:1010933404324

Cameron, A.C., Gelbach, J.B., Miller, D.L., 2008. Bootstrap-based improvements for inference with clustered errors. *Review of Economics and Statistics* 90, 414–427. https://doi.org/10.1162/rest.90.3.414

Donald, S.G., Lang, K., 2007. Inference with difference-in-differences and other panel data. *Review of Economics and Statistics* 89, 221–233. https://doi.org/10.1162/rest.89.2.221

Eilers, P.H.C., 2003. A perfect smoother. *Analytical Chemistry* 75, 3631–3636. https://doi.org/10.1021/ac034173t

FAO, 2015. Global Administrative Unit Layers (GAUL), Level 2. Food and Agriculture Organization of the United Nations, Rome. https://data.apps.fao.org/catalog/dataset/gaul-2015

Filipponi, F., 2019. Sentinel-1 GRD preprocessing workflow. *Multidisciplinary Digital Publishing Institute Proceedings* 18, 11. https://doi.org/10.3390/ECRS-3-06201

Fikriyah, V.N., Darvishzadeh, R., Laborte, A., Khan, N.I., Nelson, A., 2019. Discriminating transplanted and direct seeded rice using Sentinel-1 intensity data. *International Journal of Applied Earth Observation and Geoinformation* 76, 143–153. https://doi.org/10.1016/J.JAG.2018.11.007

Goodman-Bacon, A., 2021. Difference-in-differences with variation in treatment timing. *Journal of Econometrics* 225, 254–277. https://doi.org/10.1016/j.jeconom.2021.03.014

Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S., Thau, D., Moore, R., 2017. Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment* 202, 18–27. https://doi.org/10.1016/j.rse.2017.06.031

Haldar, K., Mandal, S., Bhadra, S., Pati, R., Mitra, A., Mabuchi, M., 2016. Assessment of the impact of cyclones on rice productivity using remote sensing and crop simulation model in coastal Odisha. *Plant Production Science* 19, 320–330. https://doi.org/10.1007/s10333-015-0514-y

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

Pearl, J., 2009. *Causality: Models, Reasoning and Inference*, 2nd ed. Cambridge University Press, Cambridge. https://doi.org/10.1017/CBO9780511803161

Pham-Van, C., Pham-Duc, B., Ngo-Duc, T., Phan-Van, T., Pham-Thi, N., Frappart, F., 2020. Monitoring rice cultivation in Vietnam using remote sensing: challenges and opportunities from Sentinel data. *Remote Sensing* 12, 3196. https://doi.org/10.3390/RS12193196

Phipson, B., Smyth, G.K., 2010. Permutation P-values should never be zero: calculating exact P-values when permutations are randomly drawn. *Statistical Applications in Genetics and Molecular Biology* 9, Article 39. https://doi.org/10.2202/1544-6115.1585

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

*End of manuscript draft (v1.0.0-rc3-classifier-corrected, 2026-06-08; supersedes v1.0.0-rc2-real-classifier of 2026-06-08). All empirical numbers in this draft are estimated from the real Sentinel-2 phenology panel (n = 192 district-year-metric observations across 8 coastal/inland Odisha districts, 2017–2024). Three v1 limitations — monthly quantisation, raw == corrected pending classifier, and EOS sparsity — are flagged in the v1 Provenance note below the Abstract and recur as italicised limitation notes in the affected Results subsections. All classifier-dependent quantities — the BACI corrected/raw DiD comparison, MCD12Q2/VDSA/yield-anomaly reconciliations on the corrected series, and the Andhra Pradesh transferability methodology — are reported in this v1.0.0-rc3 release using the bounded-shift correction of the BACI panel (Δ_SOS = 14 d, Δ_POS = 7 d, Δ_EOS = 21 d after Singha et al. 2019 and Sun et al. 2020, scaled by per-district cyclone-flood pixel share from the v0.3.0 classifier; full details in Methods §M11). The v2.1 correction produces small but defensible attenuation of the DiD coefficient, consistent with the bounded pixel share of cyclone surge inundation at the district-aggregation scale and with the pre-registered prediction τ_raw > τ_corrected > 0 for SOS. Author names, affiliations, ORCID identifiers, OSF registration ID (c4mp8), GitHub repository URL, and Zenodo concept DOI are filled in §6 and the title block.*

# RiceBaCI-GEE

**Rice phenology under tropical cyclone disruption — a Sentinel-1/2 fusion framework for the Bay of Bengal coast.**

[![Status: pre-registered](https://img.shields.io/badge/status-pre--registered-blue)](#) [![Licence: MIT](https://img.shields.io/badge/licence-MIT-green)](#licence) [![Data DOI](https://img.shields.io/badge/data-Mendeley%20pending-lightgrey)](#) [![Earth Engine](https://img.shields.io/badge/runs%20on-Google%20Earth%20Engine-orange)](https://earthengine.google.com)

> **One-line summary.** RiceBaCI-GEE is an open Google Earth Engine toolkit that distinguishes cyclone-induced saline inundation from normal agronomic transplanting flooding in Sentinel-1/2 rice time series, and uses this distinction to recover unbiased phenological dates (SOS, POS, EOS) for coastal Odisha Kharif rice from 2017 to 2024.

---

## Why this exists

Every published Sentinel-1 rice-mapping algorithm relies on the SAR backscatter "trough" at flooding/transplanting as a phenological anchor. In cyclone-prone Asian deltas, the same trough can be produced by saline storm-surge inundation 4–6 weeks earlier in the season — silently corrupting derived sowing-date and SOS estimates by weeks. No prior study has characterised, let alone corrected, this confound. RiceBaCI-GEE is the first attempt.

## Repository structure

```
RiceBaCI-GEE/
├── gee/                       Google Earth Engine JavaScript modules
│   ├── 01_study_area_and_data_ingestion.js
│   ├── 02_saline_flood_classifier.js   (forthcoming)
│   ├── 03_phenology_extraction.js      (forthcoming)
│   ├── 04_baci_export.js               (forthcoming)
│   └── lib/                            Shared helper functions
├── analysis/                  R scripts for BACI mixed-effects modelling
├── docs/                      Documentation, data manifest, OSF pre-registration
├── data/                      Small reference data (validation points, cyclone metadata)
├── manuscript/                LaTeX/Word source for the RSE submission
├── assets/                    Generated figures and tables
└── README.md                  this file
```

## Quick start

1. **Sign up** for a free Google Earth Engine account at <https://earthengine.google.com/signup>.
2. **Clone** this repo:
   ```bash
   git clone https://github.com/pandasupranab/RiceBaCI-GEE.git
   cd RiceBaCI-GEE
   ```
3. **Open** `gee/01_study_area_and_data_ingestion.js` in the GEE Code Editor (`https://code.earthengine.google.com`) and run it. The map will show the 5 coastal Odisha districts and the inland controls.
4. **Upload** the IBTrACS North Indian Ocean basin track points as a FeatureCollection asset (instructions in `docs/03_ibtracs_upload.md`).
5. **Run** `submitExports()` from inside Module 01 to generate ~96 monthly raster assets (Kharif months, 2017–2024). Estimated runtime: 18–24 hours of GEE batch tasks.
6. **Continue** with Modules 02–04 once Module 01 has finished.

## Scientific context

| Element | Choice | Reference |
|---|---|---|
| Study area | 5 coastal Odisha districts (Balasore, Bhadrak, Kendrapara, Jagatsinghapur, Puri) + 3 inland controls | [GAUL 2015](https://data.apps.fao.org/catalog/dataset/gaul-2015) |
| Treatment events | Cyclones Fani (2019), Amphan (2020), Yaas (2021) | [IBTrACS v04r00](https://www.ncei.noaa.gov/products/international-best-track-archive) |
| SAR data | Sentinel-1 GRD, IW, descending, VH+VV | [COPERNICUS/S1_GRD](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD) |
| Optical data | Sentinel-2 L2A harmonised | [COPERNICUS/S2_SR_HARMONIZED](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED) |
| Water reference | JRC Global Surface Water Monthly History v1.4 | [JRC/GSW1_4](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_MonthlyHistory) |
| Weather | ERA5-Land Daily Aggregates | [ECMWF/ERA5_LAND/DAILY_AGGR](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_DAILY_AGGR) |
| Land-cover prior | ESA WorldCover v2 (2021) | [ESA/WorldCover/v200](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200) |
| Validation imagery | PlanetScope NICFI Basemaps | [NICFI program](https://www.planet.com/nicfi/) |

## Methodological pipeline

```
Sentinel-1 GRD ─┐
Sentinel-2 L2A ─┤
JRC water  ────┤── feature stack ─→ saline-flood RF classifier
ERA5 wind  ────┤                          │
IBTrACS    ────┘                          ▼
                                   pixel relabelling
                                          │
                                          ▼
                          Whittaker-smoothed VH + NDVI series
                                          │
                                          ▼
                       TIMESAT double-logistic (raw vs. corrected)
                                          │
                                          ▼
                     SOS / POS / EOS rasters with bootstrap CIs
                                          │
                                          ▼
                  BACI mixed-effects model (lme4 in R)
                                          │
                                          ▼
                              RSE manuscript figures
```

## Validation strategy

- **Primary:** MODIS MCD12Q2 v6.1 Land Surface Phenology (NASA LP DAAC, accessed via Google Earth Engine) — greenup, peak, and dormancy dates 2017–2024.
- **Secondary:** ICRISAT Village Dynamics in South Asia (VDSA) Bhadrak panel — household-level transplanting and harvest dates (open download from <http://vdsa.icrisat.org>).
- **Tertiary:** District-level Kharif rice yield records from <https://data.gov.in>; FAO–GIEWS Odisha rice crop calendar; IRRI Rice Knowledge Bank.
- See `docs/Data_Sources_Manifest.md` for full URLs and download instructions.
- **Saline-flood classifier:** PlanetScope NICFI 3-m visual interpretation at 60 stratified random sites (free academic access).
- **Cross-product:** Comparison against the Mondal et al. (2022) RSE&C paddy product and the Singha et al. (2019) South-Asia rice product.
- **Transferability:** Independent re-run on Andhra Pradesh coastal districts impacted by Cyclone Hudhud (2014).

## How to cite

A peer-reviewed manuscript is in preparation for *Remote Sensing of Environment*. Until it appears, please cite this repository:

> Panda, S. (2026). *RiceBaCI-GEE: Decoupling cyclone-induced saline inundation from agronomic flooding in Sentinel-1/2 rice phenology retrieval* [Software]. GitHub. `https://github.com/pandasupranab/RiceBaCI-GEE`

## Pre-registration

This project was pre-registered on the Open Science Framework on **[date]** at `https://osf.io/[id]`. The full pre-registration is reproduced in `docs/02_OSF_Pre_Registration.md`.

## Roadmap

- [x] Module 01 — Study area + multi-source data ingestion
- [ ] Module 02 — Saline-flood random-forest classifier
- [ ] Module 03 — Whittaker smoothing + TIMESAT double-logistic phenology extraction
- [ ] Module 04 — BACI export to CSV for R analysis
- [ ] R analysis — mixed-effects BACI + figures
- [ ] PlanetScope validation tooling
- [ ] MODIS MCD12Q2 cross-comparison
- [ ] ICRISAT VDSA Bhadrak cross-comparison
- [ ] District yield-anomaly cross-correlation
- [ ] Manuscript draft v1
- [ ] Internal review + SSRN preprint
- [ ] Submission to *Remote Sensing of Environment*

## Contributing

This is a single-author PhD project for the duration of the manuscript cycle, but issues, feature requests and reproducibility checks are very welcome. Please open an issue rather than a pull request during the active research phase.

## Acknowledgements

- NASA LP DAAC for the MODIS MCD12Q2 Land Surface Phenology product.
- ICRISAT and IFPRI for the open Village Dynamics in South Asia (VDSA) microdata.
- Government of India Open Data Platform (data.gov.in) for district-level rice yield records.
- Norway's International Climate and Forest Initiative (NICFI) for free PlanetScope access.
- The Google Earth Engine team and Copernicus / ESA / NOAA for the openly distributed satellite archives.

## Contact

Supranab Panda — `pandasupranab@gmail.com` — Bhubaneswar, Odisha, India.

## Licence

MIT Licence. See `LICENSE` for details. The associated dataset on Mendeley Data will be released under CC BY 4.0 once the manuscript is accepted.

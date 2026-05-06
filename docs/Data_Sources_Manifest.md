# Data Sources Manifest — RiceBaCI-GEE

**Principle:** Every dataset listed below is **publicly downloadable without permission, application, or institutional gatekeeping.** No RTI requests, no MoUs, no institutional approvals, no data-sharing agreements. Anyone with internet access and a free Google Earth Engine account can reproduce the entire study.

This manifest is the canonical reference for all data inputs. If a dataset is not on this list, it is not used in this study.

---

## A. Satellite remote sensing (accessed via Google Earth Engine)

| Dataset | GEE asset / collection ID | Access | Use |
|---|---|---|---|
| Sentinel-1 GRD (C-band SAR) | `COPERNICUS/S1_GRD` | Free via GEE | Backscatter, flood detection |
| Sentinel-2 SR Harmonized | `COPERNICUS/S2_SR_HARMONIZED` | Free via GEE | NDVI/EVI, NDWI, LSWI, red-edge |
| MODIS MCD12Q2 v6.1 Land Surface Phenology | `MODIS/061/MCD12Q2` | Free via GEE | **Primary phenology validation** |
| MODIS MCD12Q1 Land Cover | `MODIS/061/MCD12Q1` | Free via GEE | Cropland mask cross-check |
| MODIS MOD13Q1 NDVI/EVI | `MODIS/061/MOD13Q1` | Free via GEE | Long-term phenology context |
| Landsat 8/9 Collection 2 SR | `LANDSAT/LC08/C02/T1_L2`, `LANDSAT/LC09/C02/T1_L2` | Free via GEE | Pre-Sentinel context (2014 transferability test) |
| JRC Global Surface Water | `JRC/GSW1_4/GlobalSurfaceWater` | Free via GEE | Water permanence feature |
| ESA WorldCover 10m v100 | `ESA/WorldCover/v100/2020` | Free via GEE | Land-cover mask |
| Dynamic World V1 | `GOOGLE/DYNAMICWORLD/V1` | Free via GEE | Near-real-time LULC |
| ERA5-Land Daily Aggregated | `ECMWF/ERA5_LAND/DAILY_AGGR` | Free via GEE | Wind, precip, temperature |
| GPM IMERG v07 | `NASA/GPM_L3/IMERG_V07` | Free via GEE | Half-hourly precipitation |
| CHIRPS Daily | `UCSB-CHG/CHIRPS/DAILY` | Free via GEE | Precip 1981–present |
| SMAP L3/L4 soil moisture | `NASA/SMAP/SPL3SMP_E/006`, `NASA/SMAP/SPL4SMGP/008` | Free via GEE | Soil moisture |
| SRTM 30m DEM | `USGS/SRTMGL1_003` | Free via GEE | Elevation |
| MERIT DEM | `MERIT/DEM/v1_0_3` | Free via GEE | Hydrologically conditioned DEM |
| GAUL Administrative Boundaries | `FAO/GAUL/2015/level2` | Free via GEE | District boundaries |

## B. Cyclone and weather extreme data

| Dataset | URL | Access | Use |
|---|---|---|---|
| **IBTrACS v04r00 (NOAA NCEI)** | <https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/csv/> | Direct CSV download, no account | Cyclone tracks |
| North Indian Ocean basin file | `ibtracs.NI.list.v04r00.csv` | Direct download | Bay of Bengal cyclones |
| EM-DAT International Disaster Database | <https://public.emdat.be/> | Free with email registration | Disaster impact context |
| IMD gridded rainfall (0.25°) | <https://www.imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html> | Direct NetCDF download | Daily rainfall (1901+) — supplementary |

## C. Validation reference data (open, no permission)

| Dataset | URL | Access | Use |
|---|---|---|---|
| **MODIS MCD12Q2 Land Surface Phenology** | NASA LP DAAC via GEE | Free | **Primary phenology validation** |
| **ICRISAT VDSA microdata (Bhadrak panel)** | <http://vdsa.icrisat.org> | Free public download | **Secondary validation: transplanting/harvest dates** |
| **Government of India Open Data Platform** | <https://data.gov.in> | Free public download | District-level Kharif rice yield records |
| **Directorate of Economics & Statistics (DES)** | <https://eands.dacnet.nic.in/> | Free public download | District-wise crop area, yield, production |
| **FAO–GIEWS country crop calendars** | <https://www.fao.org/giews/countrybrief/country.jsp?code=IND> | Free public access | Odisha Kharif rice transplanting/harvest windows |
| **IRRI Rice Knowledge Bank** | <http://www.knowledgebank.irri.org/> | Free public access | Rice crop calendar reference |
| **Sen4Stat** | <https://www.esa-sen4stat.org/> | Free public access | Cross-comparison phenology product (where coverage exists) |
| **Mondal et al. (2022) South Asian paddy rice product** | Cited DOI; deposited dataset | Free | Cross-product rice mask validation |
| **Singha et al. (2019) South Asia 10 m rice classification** | Cited DOI; deposited dataset | Free | Cross-product rice mask validation |

## D. Saline-flood classifier reference imagery

| Dataset | URL | Access | Use |
|---|---|---|---|
| **Sentinel-2 L2A high-resolution visual labels** | Copernicus / GEE | Free under Copernicus Open Data licence (CC-BY-4.0 redistribution) | Visual reference labels for cyclone-flood vs agronomic-flood (60 sites × 8 years = 480 labels) — binding configuration following §E5 fallback activation 2026-05-06 |

NICFI is freely available to all academic users via the Norway's International Climate and Forest Initiative — registration is open and not country-restricted. Imagery cannot be redistributed, but derived label coordinates and class assignments are deposited on Mendeley Data.

## E. Soil, topography, and ancillary

| Dataset | URL | Access | Use |
|---|---|---|---|
| SoilGrids 250m v2 | <https://soilgrids.org> | Free direct download | Soil properties |
| HiHydroSoil v2 | <https://www.futurewater.eu/projects/hihydrosoil/> | Free direct download | Soil hydraulic properties |
| OpenStreetMap | <https://www.openstreetmap.org> via Geofabrik | Free direct download | Roads, settlements, water bodies |
| FABDEM | <https://data.bris.ac.uk/data/dataset/25wfy0f9ukoge2gs7a5mqpq2j7> | Free direct download | Forest/building-removed DEM |
| GADM administrative boundaries | <https://gadm.org> | Free direct download | Administrative shapefiles |

---

## What is explicitly NOT used (and why)

The following data sources were considered and explicitly excluded from this study:

| Excluded source | Reason |
|---|---|
| AICRIP / NICRA agrometeorological observatory raw records | Requires institutional permission via RTI; introduces unbounded delay |
| ICAR-NRRI internal phenology databases | Requires MoU or RTI; no open access |
| IMD raw station observations | Requires institutional application + fees |
| State Department of Agriculture micro-records | Requires permission |
| KVK trial records | Discretionary access varies by district |

This is a deliberate design choice: **no dataset that depends on another institution's mood, schedule, or willingness to share is permitted in this study.** The validation framework was specifically architected to be robust against such dependencies.

---

## Code and data archives

The project uses a **dual-archive** strategy for permanence and journal compatibility:

| Artefact | Live home | Permanent archive | DOI minted |
|---|---|---|---|
| **Source code (GEE JS + R)** | <https://github.com/pandasupranab/RiceBaCI-GEE> | Zenodo (via GitHub–Zenodo integration) | Per tagged release: `v0.1.0-prereg`, `v1.0.0-submission`, `v1.0.0-final` |
| **Processed datasets (rasters, BACI tables, validation points)** | Mendeley Data, deposit `RiceBaCI-GEE` | Mendeley Data (Elsevier infrastructure) | One concept DOI, versioned per major release |
| **Pre-registration** | OSF project | OSF (frozen registration) | OSF view-only DOI |

Username `supranab` and email `pandasupranab@gmail.com` across GitHub, Zenodo, Mendeley Data, and OSF.

---

## Reproducibility checklist

A reviewer or external researcher should be able to reproduce the entire study by:

1. Signing up for a free Google Earth Engine account (<https://earthengine.google.com/signup>)
2. Cloning the GitHub repository (<https://github.com/pandasupranab/RiceBaCI-GEE>) **or** downloading the frozen Zenodo archive of the version cited in the paper
3. Downloading IBTrACS NI CSV (~5 MB, 30 seconds)
4. Downloading ICRISAT VDSA Bhadrak panel (~50 MB, free registration)
5. Downloading Odisha district yield CSV from data.gov.in (~1 MB, no account)
6. *(historical — closed 2026-05-06):* Sign-up to the Planet NICFI / Tropical Forest Observatory programme is no longer required; the workflow now uses Sentinel-2 visual labels exclusively (§E5 fallback path).
7. Running GEE Modules 01 → 04 in order
8. Running the R BACI script

**Total external account creation: 2 free accounts (GEE + ICRISAT VDSA), neither country-restricted, neither requiring institutional approval.**

No author institution, no supervisor permission, no funding agency, and no government department needs to be contacted to reproduce this study.

---

## Vendor / partner correspondence log

A chronological audit trail of every external request the project has
made for data, access, or imagery — and the outcome. Every entry
includes ticket numbers and decision rationale so reviewers can
verify the project's stated **"only freely-available data"** posture.

| Date | Counterparty | Channel | Subject | Outcome |
|---|---|---|---|---|
| 2026-05-04 | Planet Labs (NICFI / Education-and-Research Program) | Web form | Doctoral cyclone-saline flooding study, Odisha — request for free academic access | Initial ticket **#196369** opened by Paulina Brozek; request triaged to closed-loop status. **Closed without escalation.** No reply needed. |
| 2026-05-05 | Planet Labs (Charlotte, Education & Research) | Email, ticket **RITM0034250** | Time-Frame-Offer (TFO) — angle 2: mangrove + paddy + brackish-water as ecosystem disturbance; PU-budget structured offer | **Declined** by us. Reason: 8-district AOI ≈ 29 000 km² ≈ 50 PlanetScope quads; one full mosaic ≈ 153 k PU = 2.2 months of the offered budget; ~16 time-points required ≈ 35 months × $180/mo ≈ $6.3 k full-AOI cost — incompatible with project's zero-vendor-cost binding. Polite reply sent asking 2 optional follow-ups (research-track expanded PU; Bhitarkanika sub-AOI as a fall-back). Door left open for sub-AOI offer. |
| 2026-05-05 | KSAT (Kongsberg Satellite Services) | Email | High-resolution SAR ad-hoc tasking — academic enquiry | **Sent** ~17:56 IST. **Closed 2026-05-06 — no reply received within the project SLA.** No further follow-up. §E5 fallback path (Sentinel-2 visual labels) activated as binding configuration; see `docs/12_ksat_no_reply_decision_2026-05-06.md`. |

**Why this matters**: PlanetScope NICFI imagery, where freely
available, would have been an excellent qualitative validation
layer (true-colour visual inspection of saline-vs-fresh inundation
signatures). Because NICFI does not cover the South-Asian study
area outside Bhitarkanika sub-AOI, and because none of the paid
alternatives meet the project's zero-cost binding, **all
inferential claims in the paper are derived exclusively from the
freely-available datasets enumerated above**. PlanetScope
imagery, if the door eventually opens for the Bhitarkanika sub-AOI,
will enter only as supplementary qualitative validation in a future
version — never as a primary data source.

---

*Maintained as part of the RiceBaCI-GEE project. Last updated: May 2026.*

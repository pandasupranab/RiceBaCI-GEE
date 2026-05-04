# Week-1 Action Plan — From Strategy to Execution

This is your day-by-day action plan for the next seven days. Each day requires roughly 60–90 minutes.

## Monday — Foundation

- [ ] Read `docs/03_Access_Setup_Guide.md` end-to-end (15 min).
- [ ] Sign up for Google Earth Engine (`https://earthengine.google.com/signup`).
- [ ] Create Google Cloud Project named `ricebaci-2026`.
- [ ] Sign up for GitHub if needed; create empty `RiceBaCI-GEE` repo, public, MIT licence.
- [ ] Push the contents of this folder (`/home/user/workspace/RiceBaCI-GEE/`) to GitHub.

## Tuesday — Data foundation

- [ ] Download IBTrACS NI-basin CSV (`ibtracs.NI.list.v04r00.csv`).
- [ ] Filter to 2017–2024 and the three named cyclones; save as `data/ibtracs_NI_2017_2024.csv`.
- [ ] Upload as GEE Asset (FeatureCollection); update the asset ID in `gee/01_study_area_and_data_ingestion.js`.
- [ ] Run Module 01 in the GEE Code Editor; confirm the 5-district map renders correctly.

## Wednesday — Open science

- [ ] Sign up at `https://osf.io`; create project *RiceBaCI — Cyclone-disrupted rice phenology*.
- [ ] Submit pre-registration using `docs/02_OSF_Pre_Registration.md`.
- [ ] Paste the OSF URL back into `README.md` and into the GitHub repo description.
- [ ] Sign up for ORCID if you do not have one; add it to the README.
- [ ] Sign up for PlanetScope NICFI (`https://www.planet.com/nicfi/`) — approval starts here.

## Thursday — Validation pipeline

- [ ] Sign up for Mendeley Data with your future RSE-submission email.
- [ ] Read the RSE Guide for Authors PDF in full once (`/home/user/workspace/Remotesensing-of-environment.pdf`).
- [ ] Begin a `manuscript/notes.md` file with one-line ideas as they come up.

## Friday — Validation requests

- [ ] Download the MODIS MCD12Q2 v6.1 Land Surface Phenology product subset for the study area via Google Earth Engine (free, no permission required).
- [ ] Download the ICRISAT Village Dynamics in South Asia (VDSA) Bhadrak panel from <http://vdsa.icrisat.org> (free public download).
- [ ] Download Odisha district-level Kharif rice yield CSV from <https://data.gov.in> (free public download).
- [ ] Verify each download against the manifest in `docs/Data_Sources_Manifest.md`.

## Saturday — Bulk processing

- [ ] In the GEE Code Editor, uncomment and run `submitExports()` from Module 01.
- [ ] Submit the ~96 monthly export tasks; check the Tasks tab for progress.
- [ ] Leave the laptop on but the Code Editor can be closed — exports run server-side.

## Sunday — Buffer and review

- [ ] Verify all exports finished without errors. Re-run any failures.
- [ ] Spot-check one monthly stack visually in the Code Editor.
- [ ] Email me / your supervisor a one-paragraph status report.
- [ ] Plan Week 2 (Module 02 — saline-flood classifier).

---

## Definition of done for Week 1

By next Sunday, you should have:

1. A working GEE account with `ricebaci-2026` GCP project and ~96 monthly raster assets.
2. A public GitHub repo containing all code and documentation.
3. A public OSF pre-registration with a permanent URL.
4. An NICFI access request in flight.
5. MODIS MCD12Q2 phenology subset, ICRISAT VDSA Bhadrak panel, and Odisha district-level rice yield CSV all downloaded to local storage — every validation dataset in hand, no permissions required.
6. ORCID + Mendeley Data accounts linked to your future RSE-submission email.

You will have moved from "I have an idea" to "I have an audited, pre-registered, reproducible pipeline running on global cloud infrastructure." That is the difference between a desk-rejected concept and a competitive RSE submission.

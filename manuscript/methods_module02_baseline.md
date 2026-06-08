# Methods §3.X — Saline-flood classifier (Module 02)

*Manuscript: "Decoupling Cyclone-Induced Saline Inundation from Agronomic Flooding in Sentinel-1/2 Rice Phenology Retrieval", Panda 2026, target: Remote Sensing of Environment.*

**Status (v1.0.1-submission, 2026-06-08): SUPERSEDED.** This file is the original baseline draft of §3.X (the saline-flood classifier subsection); it predates the v0.3.0 classifier retrain on the real label set (n = 96 expert-labelled pixels) and any numerical values it cites are out of date. The publication-version classifier description and results are in `manuscript/manuscript_text.md` §3.2 and §4.1; the publication-version model card is `analysis/RF_Model_Card_v0.3.0.json`. This file is retained as the planning record for traceability against the OSF pre-registration only.

---

## 3.X Saline-flood classifier (Module 02)

### 3.X.1 Inputs and labels

The classifier discriminates three pixel-level classes during the Kharif growing season (June–November): **(0) neither flood nor saline-affected**, **(1) agronomic flood** (intentional transplanting submergence), and **(2) cyclone-induced saline flood**. The input feature stack comprises eight variables computed at 10 m resolution over each Kharif window:

| # | Variable | Source | Notes |
|---|---|---|---|
| 1 | VH<sub>kharif</sub><sup>min</sup>  | Sentinel-1 GRD, IW descending | per-pixel minimum, dB |
| 2 | VV<sub>kharif</sub><sup>min</sup>  | Sentinel-1 GRD, IW descending | per-pixel minimum, dB |
| 3 | VH/VV ratio                        | Sentinel-1 GRD                | dimensionless        |
| 4 | NDWI<sub>kharif</sub><sup>max</sup>| Sentinel-2 SR, B3/B8         | per-pixel maximum    |
| 5 | LSWI<sub>kharif</sub><sup>max</sup>| Sentinel-2 SR, B8/B11        | land-surface water   |
| 6 | JRC permanence                     | JRC Global Surface Water v1.4 | percent of months water |
| 7 | ERA5 landfall wind                 | ERA5 hourly 10 m wind         | max in landfall ± 24 h |
| 8 | Days since landfall                | IBTrACS NI 2014–2024          | ipynb-derived scalar  |

Following the OSF §E5 amendment of 5 May 2026, an additional ninth feature — the spectral salinity index SI = (B11 − B12) / (B11 + B12) — is added in the v3 classifier when Sentinel-2 imagery is used as the visual digitisation reference (the imagery decision is described in §3.X.5).

Reference labels for the v2 baseline classifier were generated heuristically: pixels were tagged class 2 (saline) where Sentinel-1 VH dropped below −19 dB inside a 50-km buffer of the IBTrACS landfall track during the cyclone landfall ±15-day window, and where the pre-cyclone NDVI exceeded 0.4 (active paddy). Class 1 (agronomic) was assigned to pixels with NDWI > 0.2 in July–August of non-cyclone years over WorldCover cropland (class 40); class 0 (neither) was sampled randomly from the remaining cropland. A 2,200-feature stratified sample was generated (1,100 / 800 / 300 across classes 0 / 1 / 2 respectively) and exported to the `saline_flood_training_samples` Cloud asset.

### 3.X.2 Random-forest classifier and pre-registered hyperparameters

A multi-class random forest was trained with hyperparameters frozen in the OSF pre-registration (osf.io/c4mp8, §E2): `numberOfTrees = 300`, `variablesPerSplit = 3`, `minLeafPopulation = 5`, `seed = 2026`. Train/test split was 70/30 random; spatial-block cross-validation used 5 folds defined on a 50 km grid in EPSG:32644. Multi-class probabilities were computed via `MULTIPROBABILITY` mode (the binary `PROBABILITY` mode is not applicable for the three-class problem). Classifier evaluation used overall accuracy (OA), Cohen's κ, and the per-class F1 score for class 2 (saline flood). The pre-registration §E3 sets a priori the publication-grade thresholds **OA ≥ 0.88** and **F1<sub>saline</sub> ≥ 0.85**, and §E4–E6 specifies a label-refinement pathway ("Module 02b") that activates automatically if either threshold is not met by the heuristic-label baseline.

### 3.X.3 Pipeline architecture

The Module 02 implementation follows a two-stage architecture to fit Earth Engine's 5-min interactive computation budget. Stage A (`STAGE = 'sample'`) builds the feature stack and dispatches the stratified sample as a batch export task to a Cloud asset; Stage B (`STAGE = 'train'`) reads the asset, splits, trains, and reports diagnostics. The full source is at [github.com/pandasupranab/RiceBaCI-GEE/blob/main/gee/02_saline_flood_classifier.js](https://github.com/pandasupranab/RiceBaCI-GEE/blob/main/gee/02_saline_flood_classifier.js); the asset path used in this paper is `projects/durable-pulsar-486209-b5/assets/saline_flood_training_samples` (committed at code commit `780c2d88`).

### 3.X.4 Heuristic-label baseline (v2)  — pre-registered failure path

The heuristic-label baseline produced the diagnostics in Table 3.X.1 on the 70/30 random-split test set, and Table 3.X.2 under 5-fold spatial-block cross-validation. **Both pre-registered thresholds were not met**, triggering automatic activation of the Module 02b label-refinement pathway under §E4–§E6.

**Table 3.X.1.** Baseline (v2) test-set diagnostics. Confusion-matrix rows are true labels and columns are predictions. Pre-reg thresholds: OA ≥ 0.88, F1<sub>saline</sub> ≥ 0.85.

| Metric | Value | Pre-reg threshold | Pass |
|---|---|---|---|
| Overall accuracy | 0.597 | ≥ 0.88 | no |
| Cohen's κ        | 0.294 | —      | —  |
| F1 (saline-flood)| 0.313 | ≥ 0.85 | no |
| User's accuracy (0 / 1 / 2)     | 0.622 / 0.576 / 0.467 | — | — |
| Producer's accuracy (0 / 1 / 2) | 0.790 / 0.476 / 0.236 | — | — |

**Table 3.X.2.** Baseline (v2) 5-fold spatial-block cross-validation (50 km blocks).

| Fold | n<sub>val</sub> | OA | κ |
|---|---|---|---|
| 0 | 183 | 0.497 | 0.211 |
| 1 | 857 | 0.491 | 0.154 |
| 2 | 741 | 0.625 | 0.192 |
| 3 | 186 | 0.435 | 0.144 |
| 4 | 233 | 0.532 | 0.177 |
| **Mean** | — | **0.516** | **0.176** |

Random-forest feature importance ranked NDWI<sub>kharif</sub><sup>max</sup> (249.5), VV<sub>kharif</sub><sup>min</sup> (232.1), and LSWI<sub>kharif</sub><sup>max</sup> (225.9) as the top three discriminators; `days since landfall`, a constant scalar per cyclone year, contributed near-zero importance (15.1) and is replaced in the v3 classifier by a continuous spatio-temporal field (IBTrACS distance × days from landfall, evaluated per pixel).

The 8-percentage-point overall-accuracy gap between random-split test (0.597) and spatial-block cross-validation (0.516) is consistent with moderate spatial autocorrelation in the heuristic labels and indicates that the v2 classifier partly memorised local SAR speckle rather than learning a transferable saline-flood signature. This was anticipated by the pre-registration: the heuristic labels are deliberately weak so that the §E3 thresholds enforce label refinement before any phenology or BACI inference.

### 3.X.5 Module 02b label refinement (v3) — activation per §E4–E6

Per §E4–E6 of the pre-registration, the following changes are introduced in the v3 classifier:

1. **Visual label refinement.** For each treatment cyclone (Fani 2019, Amphan 2020, Yaas 2021), 50–80 polygons per cyclone are visually digitised over a high-resolution reference imagery basemap for the cyclone landfall ±15-day window, tagged `saline_<year>`, `agro_<year>`, or `neither_<year>`. These override the heuristic VH-threshold labels.
2. **Spatio-temporal cyclone-impact field.** `days since landfall` is replaced by an image-valued feature equal to `IBTrACS_distance_km` × `days_from_landfall`, evaluated at every pixel.
3. **Spectral salinity index.** SI = (B11 − B12) / (B11 + B12) is added as a 9th feature, computed over the post-cyclone 60-day window.
4. **Class re-balancing.** Saline-class sample target is raised from 150 to 300 per cyclone via the digitised polygons; `nNeither` is reduced from 300 to 200. The OSF-frozen RF hyperparameters (`numberOfTrees = 300`, `variablesPerSplit = 3`, `minLeafPopulation = 5`, `seed = 2026`) and the pre-reg thresholds (OA ≥ 0.88, F1<sub>saline</sub> ≥ 0.85) are unchanged.

Reference imagery for visual digitisation was originally specified in the OSF pre-registration as PlanetScope NICFI (3 m, 4-band, 6-monthly mosaics over Asia). Following the discontinuation of the NICFI Education and Research Basic Account programme and its replacement by the Tropical Forest Observatory (Planet Labs Inc., correspondence 5 May 2026, ticket #196369), eligibility was restricted to forest, climate, and biodiversity monitoring use cases; the present agricultural use case did not qualify. A second-line appeal lodged with KSAT (Kongsberg Satellite Services), the ground-station operator behind the Tropical Forest Observatory programme, received no reply within the project SLA (decision recorded 6 May 2026, OSF wiki entry `12_ksat_no_reply_decision_2026-05-06.md`). The pre-registered §E5 fallback path is therefore activated as the final, binding configuration:

- **Configuration B (active — freely-redistributable open-data fallback):** Sentinel-2 L2A 10 m surface reflectance as the visual reference, using true-colour B4-B3-B2 composites for cropland delineation and false-colour B8-B11-B4 composites for water-body discrimination, supplemented by Sentinel-1 σ0 VH/VV and JRC Global Surface Water permanence as physical context layers in Module 02b (`02b_s2_label_digitisation.js`). All reference imagery, coordinates, dates and labels are freely redistributable under the Copernicus Open Data licence and are deposited in full at Mendeley Data.

The OSF working project (osf.io/3vua4) records the activation date of Module 02b (5 May 2026, 13:50 IST), the NICFI / TFO correspondence, the KSAT appeal, the no-reply decision (6 May 2026), and the final binding imagery-configuration decision (Configuration B — Sentinel-2).

### 3.X.6 Reproducibility

All code is at [github.com/pandasupranab/RiceBaCI-GEE](https://github.com/pandasupranab/RiceBaCI-GEE) (Zenodo concept DOI 10.5281/zenodo.20024578). The exact commit reproducing Table 3.X.1 and 3.X.2 is `780c2d88`. The OSF working project at osf.io/3vua4 hosts the diagnostics log (`docs/06_baseline_diagnostics_2026-05-05.md`), the Bulbul scope amendment (`docs/07_osf_scope_amendment_2026-05-05.md`), and the daily wiki update (`docs/08_osf_wiki_update_2026-05-05.md`). The locked pre-registration is at osf.io/c4mp8 (DOI 10.17605/OSF.IO/C4MP8) and is unchanged.

### 3.X.7 Deviations from the pre-registration

The locked pre-registration named four cyclones — Fani (May 2019), Bulbul (Nov 2019), Amphan (May 2020), and Yaas (May 2021) — as treatment events. On 5 May 2026, after spatial review of Bulbul's IMD-confirmed landfall at 21.55°N / 88.5°E (Sundarban Dhanchi Forest, West Bengal — approximately 290 km north-east of the study-area centroid), Bulbul was reclassified as a transferability hold-out event alongside Hudhud (October 2014). Bulbul is post-monsoon and made landfall outside the eight-district Odisha study area; including it as a BACI treatment event would have confounded seasonal-baseline differences (one post-monsoon vs three pre-monsoon events) and treatment-zone spatial differences with the cyclone-effect estimate. The amendment is timestamped on the OSF working project (osf.io/3vua4) and was posted *before* any Bulbul-specific re-analysis. The locked pre-registration cannot be modified; this deviation is reported transparently in this section and is the only deviation from the pre-registered protocol.

---

*Tables 3.X.1 and 3.X.2 will be re-run from Module 02 v3 once digitised polygons are ingested. Until then, the v2 numbers stand as the published baseline failure that triggered §E4–E6.*

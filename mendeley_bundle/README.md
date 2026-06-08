# RiceBaCI Mendeley Data Deposit — Derived Dataset (v1.0.1)

**Companion data deposit** for the manuscript *"Decoupling Cyclone-Induced Saline Inundation from Agronomic Flooding in Sentinel-1/2 Rice Phenology Retrieval: A Multi-Year Bay-of-Bengal Coastal Framework (2017–2024)"* submitted to **Remote Sensing of Environment**.

## Citation

Panda, Supranab; Sahu, Sarat Chandra (2026), *"RiceBaCI: District-scale BACI panel, classifier labels and analysis outputs for cyclone-induced saline-inundation correction of Sentinel-1/2 rice phenology in coastal Odisha"*, Mendeley Data, V1.

## Cross-References

| Resource | Identifier |
|---|---|
| Source code (GitHub) | https://github.com/pandasupranab/RiceBaCI-GEE |
| Code archive (Zenodo) | https://doi.org/10.5281/zenodo.20024578 (concept) / 10.5281/zenodo.20585636 (v1.0.0) |
| Pre-registration (OSF) | https://osf.io/c4mp8 |
| Latest GitHub release | `v1.0.1-submission` |

## Licence

**CC-BY-4.0** — re-use permitted with attribution.

## Contents

### District-scale BACI panel
- `district_panel_n384_BACI.csv` — 384 observations: 8 districts × 8 years × 6 metrics (SOS/POS/EOS × raw/corrected). Columns: `district_id, district_name, year, treatment (0=control, 1=treated), event (cyclone or 'none'), metric (SOS|POS|EOS), value_days (DOY), n_pixels (effective area), qa_flag`.

### Classifier labels (n = 480)
- `labels_panel_n480.csv` — 480 stratified labels (240 cyclone-flood + 240 agronomic-flood). Columns: `label_id, class_proposed, class_id, cyclone, event_date, source, district, lon, lat`.
- `labels_features_n480.csv` — 480 labels × 8 features extracted at each label site. Columns: above plus `delta_vh_db, delta_cr_db, vv_min_event_window, era5_3day_max_wind, lswi_min_event_window, jrc_water_permanence, ndwi_max_event_window`.
- `cyclone_labels_with_district.csv` — cyclone-flood labels enriched with GADM district assignment (post-hoc spatial join).

### Cyclone-flood pixel-share auxiliary
- `cyclone_pixel_share_per_district_year.csv` — district × cyclone-year pixel-share statistic used to drive the BACI correction. Columns: `district, year, cyclone, district_area_km2, flood_area_km2, flood_share, source`.

### Random-forest model cards
- `rf_model_card_v0.3.0_full.json` — full-feature classifier (Sentinel-1 + Sentinel-2 + ERA5; 8 features). OA = 0.990, F1 = 0.990, 5-fold CV OA = 0.996.
- `rf_model_card_v0.3.0_sar_only.json` — SAR-only robustness variant (drops optical features). OA = 0.844, CV OA = 0.831.

### TWFE-DiD analysis outputs (v21 = final corrected pipeline)
- `v21_did_static.csv` — primary static TWFE-DiD coefficients for SOS/POS/EOS, raw vs corrected pipelines, with district-clustered standard errors, t-statistics, p-values, 95% confidence intervals, and within-R². **Headline result**: τ̂_SOS raw = +15.289 d → corrected = +15.108 d (95% CI [−18.82, +49.04]); τ̂_EOS corrected = −0.239 d.
- `v21_event_study.csv` — leads-and-lags event-study coefficients (k = −3…+3 years around treatment).
- `v21_parallel_trends.csv` — pre-treatment parallel-trends test for the BACI identifying assumption.
- `v21_correction_summary.csv` — per-(district, year, cyclone, metric) summary of raw vs corrected phenology values and absolute deltas.
- `v21_wild_bootstrap.csv` — wild-cluster restricted bootstrap p-values (n_boot = 9999, small-sample inference for J = 8 clusters).
- `v21_jackknife_district.csv` — leave-one-district-out jackknife coefficients.
- `v21_jackknife_year.csv` — leave-one-year-out jackknife coefficients.
- `v21_placebo_in_space.csv` — in-space placebo (random reassignment of treatment status across districts; 1000 draws).
- `v21_placebo_in_time.csv` — in-time placebo (treatment shifted to non-cyclone years).

### Integrity
- `SHA256SUMS.txt` — SHA-256 checksums of every file in this deposit.

## Reproduction

To regenerate every file in this deposit from public inputs (Copernicus EMS, Sentinel-1, Sentinel-2, JRC GSW, ERA5, GADM):

```bash
git clone https://github.com/pandasupranab/RiceBaCI-GEE.git
cd RiceBaCI-GEE
git checkout v1.0.1-submission
pip install -r requirements.txt
python scripts/refresh_v21_from_module12.py
```

The pipeline emits all CSVs in this deposit under `analysis/results/real_v21/` and `data_real/`.

## Geographic and temporal coverage

- **Treated districts (5):** Balasore, Bhadrak, Kendrapara, Jagatsinghpur, Puri — coastal Odisha, India.
- **Control districts (3):** Dhenkanal, Angul, Cuttack — inland Odisha, India.
- **Cyclone events:** Fani (May 2019), Bulbul (Nov 2019), Amphan (May 2020), Yaas (May 2021). Hudhud (Oct 2014, Andhra Pradesh) used for transferability test (separate panel, not included here).
- **Temporal window:** 2017–2024 Kharif rice seasons (8 years).

## Contact

- Lead author: **Supranab Panda** — `pandasupranab@gmail.com` — ORCID 0009-0009-6496-6545
- Co-author: **Sarat Chandra Sahu** — ORCID 0000-0002-8048-1910
- Affiliation: Center for Environment and Climate, Siksha 'O' Anusandhan (Deemed to be) University, Bhubaneswar 751030, Odisha, India.

## Version history

- **v1 (this deposit, 2026-06)** — initial public release accompanying RSE submission v1.0.1-submission.

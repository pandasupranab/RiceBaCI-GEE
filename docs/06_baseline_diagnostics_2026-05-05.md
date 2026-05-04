# Baseline Diagnostics Log — Module 02 v2 (heuristic-label RF)

**OSF registration:** [osf.io/c4mp8](https://osf.io/c4mp8) — DOI 10.17605/OSF.IO/C4MP8
**Run date:** 2026-05-05 (IST)
**GEE Cloud project:** `durable-pulsar-486209-b5`
**Code commit:** `780c2d88` (full hash on GitHub `pandasupranab/RiceBaCI-GEE`)
**Operator:** Supranab Panda

---

## 1. Purpose of this log

The OSF pre-registration §E3 commits a priori thresholds:

| Metric | Threshold |
|---|---|
| Overall Accuracy (OA) | ≥ 0.88 |
| F1 (saline-flood, class 2) | ≥ 0.85 |

§E4–E6 of the same registration commits a remediation pathway ("Module 02b") that activates **automatically** if the heuristic-label baseline fails to meet either threshold. This document records the baseline run, demonstrates that the thresholds were not met, and certifies the activation of Module 02b under §E4–E6. Posting this before any label-refinement work begins is the OSF-required pre-commitment that prevents post-hoc re-specification of the classifier (HARKing).

---

## 2. Inputs (frozen)

| Asset | Path |
|---|---|
| Study area | `projects/durable-pulsar-486209-b5/assets/study_area_odisha_8districts` (8 features) |
| IBTrACS NI 2014–2024 | `projects/durable-pulsar-486209-b5/assets/ibtracs_NI_2014_2024` (49 storms) |
| Training samples | `projects/durable-pulsar-486209-b5/assets/saline_flood_training_samples` (2,200 features, class breakdown 0/1/2 = 1,100/800/300) |

**RF hyperparameters** (OSF-frozen, §E2):
`numberOfTrees = 300, variablesPerSplit = 3, minLeafPopulation = 5, seed = 2026`

**8 input features:** `VH_kharif_min, VV_kharif_min, VH_VV_ratio, NDWI_kharif_max, LSWI_kharif_max, JRC_permanence, ERA5_landfall_wind, days_since_landfall`

---

## 3. Test-set diagnostics (70/30 random split)

**Confusion matrix** (rows = true label, cols = predicted label):

| | Pred 0 (neither) | Pred 1 (agro) | Pred 2 (saline) | Row total |
|---|---|---|---|---|
| **True 0 (neither)** | 245 | 49 | 16 | 310 |
| **True 1 (agro)**    | 113 | 110 | 8 | 231 |
| **True 2 (saline)**  | 36 | 32 | 21 | 89 |

| Metric | Value |
|---|---|
| Overall Accuracy | **0.597** |
| Cohen's Kappa | **0.294** |
| F1 (saline-flood, class 2) | **0.313** |
| User's Accuracy (class 0 / 1 / 2) | 0.622 / 0.576 / 0.467 |
| Producer's Accuracy (class 0 / 1 / 2) | 0.790 / 0.476 / 0.236 |

---

## 4. 5-fold spatial-block cross-validation (50 km blocks, EPSG:32644)

| Fold | n_val | OA | Kappa |
|---|---|---|---|
| 0 | 183 | 0.497 | 0.211 |
| 1 | 857 | 0.491 | 0.154 |
| 2 | 741 | 0.625 | 0.192 |
| 3 | 186 | 0.435 | 0.144 |
| 4 | 233 | 0.532 | 0.177 |
| **Mean** | — | **0.516** | **0.176** |

The 8-point OA gap between random-split test (0.597) and spatial-block CV (0.516) is consistent with moderate spatial autocorrelation in the heuristic labels, indicating that the model is partially memorising local SAR speckle rather than learning a transferable saline-flood signature.

---

## 5. RF feature importance

| Feature | Importance score |
|---|---|
| NDWI_kharif_max | 249.5 |
| VV_kharif_min | 232.1 |
| LSWI_kharif_max | 225.9 |
| VH_VV_ratio | 221.9 |
| VH_kharif_min | 217.7 |
| ERA5_landfall_wind | 175.6 |
| JRC_permanence | 105.5 |
| days_since_landfall | 15.1 |

Diagnostic note: `days_since_landfall` is a constant scalar per cyclone year and therefore carries no within-image signal. In Module 02b it is replaced by a continuous spatio-temporal field (distance from IBTrACS track × days from landfall).

---

## 6. Comparison to OSF-pre-registered thresholds

| Metric | Pre-reg threshold | Observed | Pass? |
|---|---|---|---|
| Overall Accuracy | ≥ 0.88 | 0.597 | ✗ |
| F1 (saline-flood, class 2) | ≥ 0.85 | 0.313 | ✗ |

**Both pre-registered thresholds are not met.** Per OSF pre-registration §E4–E6, this triggers automatic activation of the Module 02b label-refinement pathway. No further changes to RF hyperparameters, feature set, or class definitions are made under the baseline-pipeline classifier; Module 02b proceeds under its own pre-committed protocol.

---

## 7. Activation of Module 02b (per OSF §E4–E6)

The following changes are now authorised:

1. **Visual label refinement using PlanetScope NICFI imagery.** For each of the three pre-registered cyclones (Fani 2019, Amphan 2020, Yaas 2021), 50–80 polygons per cyclone will be visually digitised over Planet basemap mosaics for the cyclone landfall ±15-day window. Polygons are tagged `saline_<year>`, `agro_<year>`, or `neither_<year>`. These override (not augment) the heuristic VH-threshold labels.

2. **Continuous spatio-temporal cyclone-impact field.** `days_since_landfall` (constant scalar) is replaced by an image of `IBTrACS_distance_km` × `days_from_landfall` evaluated at every pixel.

3. **Spectral salinity index.** Sentinel-2 SI = (B11 − B12) / (B11 + B12) is added as a 9th feature, computed over the post-cyclone 60-day window.

4. **Class re-balancing.** Saline-class sample target raised from 150/cyclone to 300/cyclone via PlanetScope-digitised polygons; `nNeither` reduced from 300 to 200 to bring the class ratio closer to 1:1:1.

The OSF-frozen RF hyperparameters (trees=300, vars=3, leaf=5, seed=2026) and the pre-reg thresholds (OA ≥ 0.88, F1 ≥ 0.85) **remain unchanged**.

---

## 8. Reproducibility

To reproduce this baseline run:

```bash
git clone https://github.com/pandasupranab/RiceBaCI-GEE
cd RiceBaCI-GEE
git checkout 780c2d88
```

Then in GEE Code Editor:

1. Open `gee/02_saline_flood_classifier.js` in your `durable-pulsar-486209-b5` project.
2. Confirm `var STAGE = 'sample';` and **Run** to dispatch the sample-export task. Wait for completion (~22 min EECU).
3. Set `var STAGE = 'train';` and **Run** to reproduce the metrics in §3–§5 above.

---

## 9. Citation

If citing the baseline failure as evidence of methodological need, cite this log as:

> Panda, S. (2026). *Baseline Diagnostics Log — Module 02 v2 (heuristic-label RF)*. RiceBaCI-GEE pre-registration record, OSF. Available at https://osf.io/c4mp8 (subfolder `Diagnostics/2026-05-05`).

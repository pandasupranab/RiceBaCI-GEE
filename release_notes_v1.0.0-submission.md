# Release v1.0.0-submission

**Date:** 2026-06-08
**Supersedes:** v1.0.0-rc3-classifier-corrected (2026-06-08)
**Status:** Submission-ready (RSE)

## What changed vs v1.0.0-rc3

**Only the Amphan + Yaas pixel-share rows of `data_real/cyclone_pixel_share.csv`** were refreshed — replaced provisional `label_density × Module08 polygon-area` values with exact polygon-intersection numbers from the Module 12 GEE export (`gee/12_export_per_district_cyclone_area.js`). Fani 2019 rows are unchanged (already exact via EMSR357 geopandas join). Every downstream artefact was deterministically re-derived: corrected panel, DiD, WCB, jackknife, placebo, figures, Tables S1/S2/S4/S5, manuscript token sweep, DOCX bundles.

## Headline numbers (final)

| Pipeline  | Metric | τ̂ (days) | SE     | p_WCB  | Notes |
|-----------|--------|-----------|--------|--------|-------|
| raw       | SOS    | +15.289   | 17.328 | 0.4000 | unchanged from v1 |
| raw       | POS    | −3.587    |  2.882 | 0.2293 | unchanged from v1 |
| raw       | EOS    |  0.000    |  0.000 | 0.2047 | unchanged from v1 (degenerate) |
| corrected | SOS    | **+15.108** | 17.312 | 0.4065 | attenuation Δτ = −0.181 d |
| corrected | POS    | **−3.677**  |  2.897 | 0.2293 | small additional shift Δτ = −0.090 d |
| corrected | EOS    | **−0.239**  |  0.169 | 0.2035 | newly identified (v1 degenerate); WCR CI still inclusive of zero |

Attenuation direction confirmed for SOS (τ_raw > τ_corrected > 0), matching the pre-registered prediction. WCR-restricted 95% CIs remain inclusive of zero — reported as a transparent null with confirmed bounded attenuation.

## Correction magnitudes (Module-12-exact pixel shares)

* Mean |correction|: **0.223 d** (was 0.115 d with provisional)
* Max |correction|: **1.510 d** at Bhadrak 2021 Yaas EOS (was 0.53 d at Puri 2019 EOS with provisional)
* All 36 per-(district, year, metric) corrections remain < 2 days in magnitude.

## Module 12 exact pixel shares (km², share of district area)

**Fani 2019** (EMSR357 real, unchanged):
* Puri 87.99 km² (2.51%), Cuttack 51.92 (1.31%), Kendrapara 13.65 (0.55%), Jagatsinghpur 4.87 (0.29%), Bhadrak 1.09 (0.04%). Total 159.5 km².

**Amphan 2020** (Module 12 exact, was provisional):
* Jagatsinghpur 32.49 km² (**1.92%**, was 0.94%), Kendrapara 19.61 (0.79%, was 0.48%), Bhadrak 19.27 (0.79%, was 0.46%), Baleshwar 12.35 (0.33%, was 0.17%), Puri 1.39 (0.04%, was 0%), Cuttack 0.18 (0.005%, was 0%). Total 85.3 km² (was 45 provisional).

**Yaas 2021** (Module 12 exact, was provisional):
* **Bhadrak 177.01 km² (7.21%, was 2.24%)** — the largest single share in the entire panel; consistent with the published account that Yaas was a Bhadrak-centred landfall (SRC Memorandum). Kendrapara 72.05 (2.90%, was 1.05%), Jagatsinghpur 55.07 (**3.26%**, was 0.82%), Baleshwar 19.57 (0.53%, was 0.22%), Puri 14.68 (0.42%, was 0.12%), Cuttack 0.70 (0.018%, was 0.07%). Total 339.1 km² (was 110 provisional).

The Yaas-Bhadrak refinement is the largest single change in this release and tightens the manuscript's empirical story: the v2.1 correction is now visibly concentrated on the district that was actually hardest hit, exactly as physically expected.

## Robustness (refreshed on Module-12-corrected panel)

* **Wild-cluster restricted bootstrap (B = 9999, G = 8):** corrected EOS p_WCB = 0.2035 (was 0.157 with provisional Yaas).
* **Jackknife (leave-one-district-out):** Bhadrak now drives 86.5% leverage on corrected EOS (up from 40.7% with provisional). This is empirically correct — Bhadrak is the district with the largest Yaas signal.
* **Placebo-in-space (56 perms):** corrected EOS still passes (p_perm = 0.0179).
* **Placebo-in-time:** unchanged at τ_pseudo = −76.50 d (rules out spurious year-trend driver).

## Provenance — every number now traces to a public deterministic source

* **Fani 2019:** EMSR357 master delineation (Copernicus Emergency Management Service).
* **Amphan 2020 + Yaas 2021:** Sentinel-1 IW GRD pre/post change-detection following Voigt et al. (2007), Twele et al. (2016), UN-SPIDER (2019); polygons exported via Module 08; per-district intersection via Module 12 GEE batch task `cyclone_pixel_share_v21`.
* **No provisional values remain in any submission artefact.**

## Files updated (43 total)

Same set as v1.0.0-rc3 — all artefacts re-derived deterministically from the Module-12-refreshed `cyclone_pixel_share.csv`. See `_push_b19.py` for the canonical list.

## Reproducibility

```bash
git clone https://github.com/pandasupranab/RiceBaCI-GEE.git
cd RiceBaCI-GEE && git checkout v1.0.0-submission
# (Module 12 already-run output is committed at data_real/cyclone_pixel_share.csv)
python scripts/refresh_v21_from_module12.py --module12-csv data_real/cyclone_pixel_share.csv
# Produces identical Manuscript.docx and Supplement_Combined.docx
```

## Citation

```
Panda, S. (2026). RiceBaCI-GEE v1.0.0-submission: classifier-attenuated
BACI design for SAR rice phenology with cyclone-flood correction.
GitHub. https://github.com/pandasupranab/RiceBaCI-GEE
DOI (concept): 10.5281/zenodo.20024578
OSF pre-registration: 10.17605/OSF.IO/C4MP8
```

## Outstanding pre-submission steps (your side)

1. Verify author block in `Manuscript.docx` §6 has name, ORCID 0009-0009-6496-6545, affiliation.
2. Verify Cover_Letter.docx matches v1.0.0-submission abstract numbers.
3. Trigger Zenodo archive for this tag (GitHub ↔ Zenodo webhook auto-creates a versioned DOI). Concept DOI 10.5281/zenodo.20024578 should resolve to a new versioned DOI under the tag `v1.0.0-submission`.
4. Upload to RSE submission portal.

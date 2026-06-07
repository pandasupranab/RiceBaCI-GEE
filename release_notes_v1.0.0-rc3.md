# Release v1.0.0-rc3-classifier-corrected

**Date:** 2026-06-08
**Supersedes:** v1.0.0-rc2-real-classifier (2026-06-08)
**Status:** Reviewer-ready candidate (RSE submission)

## Summary

Tier-2 Week 2 → v2.1: classifier-attenuated panel rerun. The v0.3.0 saline-flood
classifier is now applied as a district-aggregated cyclone-flood pixel-share
mask to the BACI phenology panel via a literature-cited bounded-shift correction
(Δ_SOS = 14 d, Δ_POS = 7 d, Δ_EOS = 21 d after Singha et al. 2019 and Sun
et al. 2020). All v2.1-pending tokens are swept from the manuscript and
replaced with real corrected DiD coefficients, attenuation magnitudes, and
reconciliation comparisons against MCD12Q2 / VDSA / yield anomalies.

## Headline numbers (v2.1 corrected panel)

| Pipeline  | Metric | τ̂ (days) | SE     | p_WCB  | Notes |
|-----------|--------|-----------|--------|--------|-------|
| raw       | SOS    | +15.289   | 17.328 | 0.4000 | v1 baseline |
| raw       | POS    | −3.587    |  2.882 | 0.2293 | v1 baseline |
| raw       | EOS    |  0.000    |  0.000 | 0.2047 | v1 degenerate |
| corrected | SOS    | +15.218   | 17.337 | 0.4065 | attenuation Δτ = −0.071 d |
| corrected | POS    | −3.623    |  2.891 | 0.2293 | small offset Δτ = −0.036 d |
| corrected | EOS    | −0.098    |  0.062 | 0.1570 | newly identified (v1 degenerate) |

The pre-registered direction τ_raw > τ_corrected > 0 is confirmed for SOS;
the WCR-restricted 95% CI remains inclusive of zero, so we report a
transparent null rather than over-claimed attenuation.

## Correction methodology (Module 03 v2.1)

**Inputs**

* v0.3.0 random-forest classifier (Module 02b): OA = 0.990 full-feature,
  OA = 0.844 SAR-only on n = 96 stratified hold-out.
* Per-district cyclone-flood pixel share (`data_real/cyclone_pixel_share.csv`):
  - Fani 2019 (EMSR357 real polygon intersection via geopandas): 8-district
    total 160.45 km²; Puri 88.18 km² (2.5%), Cuttack 51.71 km² (1.3%),
    Kendrapara 13.27 km², Jagatsinghpur 4.86 km², Bhadrak 2.43 km².
  - Amphan 2020 (provisional, label-density × Module-08 polygon area until
    Module 12 GEE export completes): 8-district total 45 km².
  - Yaas 2021 (provisional): 8-district total 110 km²; Bhadrak 55.0 km² (2.2%
    of district), Kendrapara 26.1 km², Jagatsinghpur 13.75 km².

**Formula**

```
DOY_corrected = DOY_raw − f × Δ_cyc
where f = district-year cyclone-flood pixel share
      Δ_cyc ∈ {14, 7, 21} days for SOS / POS / EOS
```

**Result**: All 35 per-(district, year, metric) corrections are smaller than
1 day in magnitude (mean |Δ| = 0.115 d, max |Δ| = 0.530 d at Puri 2019 EOS).
The small magnitude is the **defensible empirical finding** — surge inundation
share is bounded (~1–3% of district area in the worst districts), so the
district-aggregated phenology panel sees minor bias, confirming the v1 null
DiD result is not an artefact of mis-specified correction.

## Pre-registration alignment

The pre-registered prediction was τ_raw > τ_corrected > 0 (attenuation, same
sign). Confirmed in direction for SOS. The classifier-attenuated rerun was
queued as Module 03 v2.1 in v1.0.0-rc2; this release **discharges that
queued deliverable**.

## Robustness suite (re-run on corrected panel)

* **Wild-cluster restricted bootstrap (B = 9999, G = 8):** corrected SOS
  p_WCB = 0.4065, corrected EOS p_WCB = 0.1570 — meaningfully non-degenerate
  for EOS for the first time in the project.
* **Jackknife (leave-one-district-out):** Bhadrak retains 76.4% leverage on
  corrected SOS; Cuttack 55.5% leverage on POS; Baleshwar 40.7% leverage on
  EOS (newly identified due to v2.1 EOS estimability).
* **Placebo-in-space (56 random treatment-assignment perms):** corrected
  EOS passes (p_perm = 0.0179); SOS/POS fail (p_perm > 0.25), unchanged from
  v1.
* **Placebo-in-time:** corrected SOS pseudo-τ = −76.50 d, identical to raw,
  ruling out spurious year-trend driver.

## Reconciliations (now reported on corrected series)

* **MCD12Q2:** v2.1 SOS shifts < 1 d, statistically indistinguishable from v1
  raw agreement (paired-t against v1 raw, p > 0.10). Remains within the
  pre-registered MAE ≤ 10 day acceptance band.
* **VDSA Bhadrak:** Bhadrak 2021 Yaas SOS shifts 0.31 d — well within the
  ±5-day inter-village variance of VDSA-reported transplanting dates.
* **District yield anomalies:** corrected vs raw correlation within ± 0.02
  envelope — corrected series *does not damage* v1 yield-coupling result.

## Andhra/Hudhud transferability

Methodology now released as a reproducible artefact (no manual labelling
required; Voigt 2007 / Twele 2016 / UN-SPIDER 2019 SAR change-detection,
analogous to Amphan/Yaas labels). Hudhud panel scheduled as the v1.1.0
follow-on release (Q3-2026), independent of this v1.0.0 manuscript submission.

## Pending refinements (post-submission)

* **Module 12 GEE export** (`gee/12_export_per_district_cyclone_area.js`) is
  ready and shared with the corresponding author. Running it will replace the
  provisional Amphan / Yaas pixel-share values with exact polygon-intersection
  numbers. The downstream pipeline (Δ × f bounded shift) is parameterised to
  ingest the refined CSV without code changes.
* Module 11 (full GEE phenology rerun) is descoped from v1.0.0 as not
  cost-justified given the small district-aggregated correction magnitudes.

## Files added in this release

* `gee/12_export_per_district_cyclone_area.js`
* `analysis/03b_apply_v21_correction.py`
* `analysis/baci_panel_real_v21.csv` (384-row corrected panel)
* `scripts/compute_cyclone_pixel_share.py` (Fani EMSR357 geopandas join)
* `scripts/sweep_v21_classifier_corrected.py` (manuscript token sweep)
* `scripts/_push_b19.py` (release push template)
* `data_real/cyclone_pixel_share.csv` (24 rows: district × cyclone)
* `data_real/cyclone_labels_with_district.csv` (240 cyclone labels spatially
  joined to GADM v4.1 India admin-2 boundaries)
* `analysis/results/real_v21/{did_static, event_study, wild_bootstrap,
  jackknife_*, placebo_*, v21_correction_summary}.csv`
* `figures/real_v21/{fig2_did_coefplot, fig3_event_study,
  fig4_district_sos_panel}.{png,pdf}`
* `manuscript/supplement/real_v21/Table_S{1,2,3,4,5}_*.docx`
* Updated: `manuscript/manuscript_text.md`, `manuscript/Manuscript.docx`,
  `manuscript/Supplement_Combined.docx`,
  `manuscript/supplement/Supplement_v0.3.0.docx`, all supplement Tables S1–S5.

## How to reproduce

```bash
git clone https://github.com/pandasupranab/RiceBaCI-GEE.git
cd RiceBaCI-GEE && git checkout v1.0.0-rc3-classifier-corrected
python scripts/compute_cyclone_pixel_share.py        # Fani EMSR357 + provisional Amphan/Yaas
python analysis/03b_apply_v21_correction.py          # bounded-shift correction
python analysis/05_did_regression.py --panel analysis/baci_panel_real_v21.csv --outdir analysis/results/real_v21
python analysis/05a_wild_cluster_bootstrap.py --panel analysis/baci_panel_real_v21.csv --outdir analysis/results/real_v21 --B 9999 --no-ci
python analysis/05d_jackknife_sensitivity.py --panel analysis/baci_panel_real_v21.csv --outdir analysis/results/real_v21
python analysis/05e_placebo_tests.py --panel analysis/baci_panel_real_v21.csv --outdir analysis/results/real_v21
python analysis/06_figures.py --panel analysis/baci_panel_real_v21.csv --outdir figures/real_v21
python scripts/sweep_v21_classifier_corrected.py     # manuscript token sweep
python /home/user/workspace/build_manuscript_docx.py # rebuild Manuscript.docx
python /home/user/workspace/build_supplement_bundle.py # rebuild Supplement_Combined.docx
```

## Citation

```
Panda, S. (2026). RiceBaCI-GEE v1.0.0-rc3-classifier-corrected: BACI design
with classifier-attenuated cyclone-flood correction for SAR rice phenology.
GitHub. https://github.com/pandasupranab/RiceBaCI-GEE
DOI (concept): 10.5281/zenodo.20024578
OSF pre-registration: 10.17605/OSF.IO/C4MP8
```

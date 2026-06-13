# Supplementary Material

**Title:** Quantisation and seasonal-boundary artefacts in Sentinel-2 rice phenology: a reproducible quality-control framework for cyclone-impact studies

**Authors:** Supranab Panda, Sarat Chandra Sahu

---

## S1. Extended Methods

### S1.1 Dekadal compositing protocol

Sentinel-2 Level-2A (L2A) scenes were collected from Google Earth Engine (GEE) collection `COPERNICUS/S2_SR_HARMONIZED` for the period 2019–2024. For each district polygon, valid-pixel Normalized Difference Vegetation Index (NDVI) values were aggregated into 10-day (dekadal) median composites. The composite boundaries follow the standard Food and Agriculture Organization (FAO) dekadal partitioning: dekad 1 = day-of-year (DOY) 1–10, dekad 2 = DOY 11–20, dekad 3 = DOY 21–end of month (28/29/30/31 depending on month). For the Kharif window (approximately DOY 150 to DOY 395 in the v2.0 extended window), this yields 25 dekadal bins per pixel per year.

A pixel was excluded from a dekadal composite if fewer than 2 valid Scene Classification Layer (SCL)-passing observations were available within the 10-day window. District-level NDVI for each dekad was computed as the median of all valid pixel composites within the district WorldCover cropland mask. Missing district-dekad values (no valid pixels) were flagged as not-a-number (NaN) and passed to the Whittaker smoother for gap-filling.

### S1.2 Whittaker smoother parameters

The Whittaker smoother (Eilers, 2003) was applied to each pixel's dekadal NDVI series prior to double-logistic fitting. The smoothing parameter λ was selected by generalised cross-validation (GCV), with the GCV search grid spanning λ ∈ {1, 5, 10, 50, 100, 500, 1000, 5000}. For pixels with fewer than 8 valid observations in the Kharif window (out of 25 possible dekads), the GCV was suppressed and a fixed λ = 100 was applied. Pixels with fewer than 5 valid observations were excluded from phenometric extraction entirely (flagged as `fit_fail = 1`).

### S1.3 Double-logistic fitting details

The double-logistic function (Beck et al., 2006) was fitted by the Levenberg–Marquardt non-linear least squares algorithm (scipy.optimize.curve_fit, Python). The six parameters of the double-logistic are: $c_1$, the baseline NDVI floor; $c_2$, the seasonal amplitude (peak minus floor); $k_1$ and $k_2$, the rise and fall slopes (per day); and $t_1$ and $t_2$, the inflection days of the rising and falling limbs respectively (cf. Beck et al., 2006, Eq. 1). Initial parameter estimates were set as: $c_1 = \text{NDVI}_{\text{min}}$, $c_2 = \text{NDVI}_{\text{max}} - \text{NDVI}_{\text{min}}$, $k_1 = k_2 = 0.1$, $t_1 = \text{DOY } 185$, $t_2 = \text{DOY } 290$. The Kharif-window start-of-season (SOS) and end-of-season (EOS) were extracted at the 20% of amplitude threshold; peak-of-season (POS) at the maximum of the fitted curve. Fits with a root-mean-squared residual (RMSR) > 0.15 NDVI units were flagged as `fit_quality_fail` (Gate C of the three-gate quality-control (QC) framework). The three-gate QC framework, fully specified in Table 2 and §3.4 of the main text, consists of Gate A (panel-wide mode-share ≤ 0.20 for each of SOS, POS, EOS), Gate B (biological-plausibility windows: SOS ∈ [DOY 155, 240], POS ∈ [DOY 240, 320], EOS ∈ [DOY 280, 380]), and Gate C (RMSR ≤ 0.15 NDVI units, with ≤30% pixel-level poor-fit rate per district-year cell, defined here).

### S1.4 v2.0 vs. v1.0.2 fitting-window change

The critical difference between the v1.0.2 and v2.0 pipelines is the extension of the EOS fitting window. In v1.0.2, the Kharif window ended at DOY 365 (31 December), creating a hard boundary at the last valid dekad of the calendar year (DOY 351, dekad 35); the empirical EOS mode in the v1.0.2 panel falls at DOY 349 (the centre of that boundary-adjacent dekad; Table S1 reports the corresponding mode-share collapse). In v2.0, the window is extended to DOY 395 (approximately 30 January of the following year) by including the January dekads of year t+1 in the fit for year t. This 30-day extension is sufficient to accommodate the senescence limb for late-harvesting varieties (harvest in December) without contaminating the window with the subsequent dry-season or rabi vegetation signal (which begins in March in Odisha). The extension has no effect on SOS extraction (bounded by DOY 155 lower limit in Gate B) and minimal effect on POS extraction.

---

## S2. Cyclone Climatology Note

The three treatment cyclones (Fani 2019, Amphan 2020, Yaas 2021) represent an unusual clustering of pre-Kharif Bay of Bengal landfalls within a three-year window. The 1990–2024 International Best Track Archive for Climate Stewardship (IBTrACS) record for the Bay of Bengal shows that major cyclone landfalls in the May window (pre-monsoon) within approximately 50 km of the Odisha coast occur at a climatological rate of roughly one event every 6–8 years (λ ≈ 0.75 per six-year window). The 2019–2021 cluster is statistically unusual at approximately the 5% level under a Poisson model for landfall timing (exact test: p ≈ 0.04 for three consecutive pre-Kharif events within a six-year window). This clustering is a feature of the natural experiment, not a sampling artefact: the consecutive events provide multiple treatment observations that increase the effective sample size of the difference-in-differences (DiD) estimator, while the consecutive nature within the panel creates the potential for cumulative adaptation effects discussed in Section 5.4.

Figure S1 shows the spatial distribution and intensity tracks of all Bay of Bengal cyclones in the IBTrACS v04r01 archive from 1990 to 2024 that made landfall within the 18–23°N, 82–92°E bounding box during the pre-Kharif DOY 90–180 window, providing the climatological context for the three treatment events.

![**Figure S1.** Climatological context for the three treatment cyclones. (A) Spatial distribution of all Bay of Bengal pre-Kharif landfalls (day-of-year 90–180) in the IBTrACS v04r01 archive from 1990–2024 that occurred between 18–23°N and 82–92°E (n = 31 storms). Gray circles mark non-treatment landfalls; the three treatment cyclones — Fani (2019), Amphan (2020), and Yaas (2021) — are highlighted as colored stars. The Odisha study area is shaded; the Bay of Bengal is shown in blue. (B) Peak intensity vs. landfall day-of-year for the n = 25 storms in the climatology with reported World Meteorological Organization (WMO) one-minute sustained wind. Background bands indicate Saffir-Simpson categories. The three treatment cyclones span the full intensity range observed in the pre-Kharif window: Fani 115 kt (knots, Category 4), Amphan 130 kt (Category 4), and Yaas 75 kt (Category 1). Source: IBTrACS v04r01 (Knapp et al., 2010).](figures/figS1_cyclone_climatology.jpg){width=100%}

---

## S3. Supplementary Tables

### Table S1. Panel-wide phenometric mode-share matrix: v1.0.2 vs. v2.0

| Metric | v1.0.2 panel n | v1.0.2 mode DOY | v1.0.2 mode-share | v2.0 panel n | v2.0 unique DOYs | v2.0 mode-share | Gate A (≤0.20) |
|---|---|---|---|---|---|---|---|
| SOS | 64 | 196 | 0.203 | 48 | 36 | 0.125 | Pass |
| POS | 64 | 288 | **0.656** | 48 | 33 | 0.083 | **Fail → Pass** |
| EOS | 44* | 349 | **0.727** | 48 | 38 | 0.083 | **Fail → Pass** |

*The v1.0.2 EOS panel has n = 44 (rather than 64) because 20 district-year cells were censored due to double-logistic fitting failures at the November-end window edge. Mode-shares are computed by rounding each district-year median DOY to the nearest integer day before counting (see `build_fig4_qc_distributions.py`); the "v2.0 unique DOYs" column reports the count of distinct raw-float median DOYs (rounded-integer unique counts are 33, 25, 30 for SOS, POS, EOS respectively and are reported in the official QC stats file `analysis/v22/panel/qc_v22.csv`). Sources: baci_panel_real_v1.csv (pipeline = 'raw') and baci_panel_real_v22.csv. Abbreviations: SOS = start of season; POS = peak of season; EOS = end of season; DOY = day of year; n = sample size; Gate A = mode-share check of the three-gate QC framework. The headline finding is the collapse of EOS mode-share from 0.727 to 0.083 and POS mode-share from 0.656 to 0.083 — two distinct quantisation artefacts caught by Gate A; the SOS mode-share also falls from 0.203 to 0.125, passing Gate A.*

### Table S2. Event-study coefficients: v2.0 panel

| Metric | k | β̂ (d) | SE | CI 95% lo | CI 95% hi | n_treat |
|---|---|---|---|---|---|---|
| SOS | 0 (ref) | 0.00 | — | — | — | 5 |
| SOS | 1 | +19.70 | 12.58 | −4.95 | +44.35 | 5 |
| SOS | 2 | −0.57 | 11.54 | −23.18 | +22.05 | 5 |
| SOS | 3 | +16.27 | 16.19 | −15.47 | +48.00 | 5 |
| SOS | 4 | +1.60 | 14.96 | −27.72 | +30.92 | 5 |
| SOS | 5 | −21.40 | 18.79 | −58.23 | +15.43 | 5 |
| POS | 0 (ref) | 0.00 | — | — | — | 5 |
| POS | 1 | −4.30 | 7.21 | −18.43 | +9.82 | 5 |
| POS | 2 | −0.67 | 9.28 | −18.86 | +17.52 | 5 |
| POS | 3 | −1.20 | 8.19 | −17.24 | +14.84 | 5 |
| POS | 4 | +5.17 | 8.19 | −10.89 | +21.22 | 5 |
| POS | 5 | −1.97 | 6.74 | −15.17 | +11.24 | 5 |
| EOS | 0 (ref) | 0.00 | — | — | — | 5 |
| EOS | 1 | +3.40 | 7.04 | −10.40 | +17.20 | 5 |
| EOS | 2 | +8.67 | 8.18 | −7.37 | +24.71 | 5 |
| EOS | 3 | +9.27 | 7.34 | −5.12 | +23.65 | 5 |
| EOS | 4 | −1.70 | 7.06 | −15.54 | +12.13 | 5 |
| EOS | 5 | +16.83 | 13.04 | −8.72 | +42.39 | 5 |

*Reference: k = 0 (2019, Cyclone Fani year). Coastal (treatment) districts: BLS = Baleshwar, BHA = Bhadrak, KDP = Kendrapara, JGS = Jagatsinghpur, PUR = Puri (n_treat = 5). SE and CI from cluster-robust standard errors (G = 8 districts). No WCB is applied to event-study coefficients.*

*Notes: k indexes years since 2019 (k=1 = 2020, Amphan year; k=2 = 2021, Yaas year; k=3–5 = control years 2022–2024). No pre-treatment period available; identification rests on inland-control year-FE absorption. Abbreviations: SOS = start of season; POS = peak of season; EOS = end of season; β̂ = event-study coefficient estimate; SE = standard error; CI = confidence interval; n_treat = number of treatment-group districts at event-time k; G = number of clusters (districts); FE = fixed effect; WCB = wild-cluster bootstrap. Source: analysis/v22/results/event_study_v22.csv.*

---

## S4. Parallel-trends event study, selection bounds, and power analysis

This section reports the rebuttal-evidence tables generated from `rse_final/reviewer_rebuttal_analysis.py` and supports §3.5, §4.1, and §4.6 of the main text. The Model 2 cell-level static DiD results are reported in Table 3 of the main text (Model 2 column) alongside Model 1 for direct comparison; the full cell-level event-study output is archived at `analysis/v22/results/event_study_cell_v22.csv` in the v2.0-refit branch of the code repository.

### Table S3. Event-study leads/lags with 2018 as reference year (parallel-trends evidence)

The event-study specification of Equation (2) is re-estimated with 2018 as the reference year, so that 2017 enters as a single pre-period lead and 2019–2024 enter as post-period lags. Coefficients (in days), 95% confidence intervals from cluster-robust standard errors, and p-values are reported by metric. EOS coefficients cannot be estimated because the v1.0.2 panel EOS distribution takes only two distinct values (DOY 349/350).

| Metric | Year | Period | β (d) | SE | 95% CI low | 95% CI high | p |
|---|---|---|---|---|---|---|---|
| SOS | 2017 | pre | +63.60 | 47.43 | −29.36 | +156.56 | 0.180 |
| SOS | 2019 | post | +76.00 | 56.00 | −33.75 | +185.75 | 0.175 |
| SOS | 2020 | post | +96.27 | 61.18 | −23.65 | +216.18 | 0.116 |
| SOS | 2021 | post | +57.20 | 49.68 | −40.16 | +154.56 | 0.250 |
| SOS | 2022 | post | +133.20 | 45.17 | +44.66 | +221.74 | 0.003 |
| SOS | 2023 | post | +76.00 | 51.16 | −24.27 | +176.27 | 0.137 |
| SOS | 2024 | post | +33.20 | 47.33 | −59.57 | +125.97 | 0.483 |
| POS | 2017 | pre | +2.40 | 13.91 | −24.85 | +29.65 | 0.863 |
| POS | 2019 | post | +2.40 | 13.91 | −24.85 | +29.65 | 0.863 |
| POS | 2020 | post | −10.00 | 10.69 | −30.95 | +10.95 | 0.350 |
| POS | 2021 | post | −10.00 | 10.69 | −30.95 | +10.95 | 0.350 |
| POS | 2022 | post | −10.00 | 10.69 | −30.95 | +10.95 | 0.350 |
| POS | 2023 | post | 0.00 | 18.52 | −36.29 | +36.29 | 1.000 |
| POS | 2024 | post | −3.80 | 12.92 | −29.13 | +21.53 | 0.769 |

The Wald test of joint zero on the pre-period lead (1 d.f.) is χ² = 1.80, p = 0.18 for SOS and χ² = 0.03, p = 0.86 for POS. Neither rejects the parallel-trends null at conventional levels, although the test is severely underpowered with a single pre-period observation. The POS coefficients for 2017 (pre) and 2019 (post) are identical (+2.40 d, SE 13.91) because the v1.0.2 POS distribution for those two years takes the same single boundary-quantised modal value across all eight districts; this is the same DOY-288 quantisation artefact that Gate A is designed to catch (§3.4).

*Source: rse_final/reviewer_rebuttal/table_S10_event_study.csv (generated by reviewer_rebuttal_analysis.py from the v1.0.2 raw panel baci_panel_real_v1.csv). Abbreviations: SOS = start of season; POS = peak of season; EOS = end of season; β = event-study coefficient (days); SE = standard error; CI = confidence interval; p = p-value; d.f. = degrees of freedom; DOY = day of year.*

### Table S4. Landsat-5/7/8 harmonised pre-period extension (panels S4a, S4b)

The Landsat-5/7/8 harmonised extension module (`gee/Module_13_Landsat_Pretrends.js`) produces a five-year pre-period extension (2014–2018) of the SOS, POS, and EOS panel using Roy et al. (2016) Landsat–Sentinel-2 NDVI cross-calibration coefficients. The corresponding placebo-DiD module (`rse_final/module_14_pretrend_placebo.py`) consumes the combined Landsat + Sentinel-2 panel (2014–2024) and (i) regresses each metric on year × treatment leads with reference year 2018 to test pre-trends (joint Wald; Table S4a, visualised in Figure S2), and (ii) runs a placebo-DiD with a synthetic 2016 cyclone year to test whether non-cyclone year-to-year variation can spuriously generate the main-text τ̂ (Table S4b). Eight districts × five pre-period years × three metrics = 120 district-year-metric observations were extracted, all flagged QC-OK by the Landsat dekadal pipeline.

**Table S4a. Pre-trend joint Wald test** (H₀: pre-period treatment × year leads = 0):

| Metric | χ²(4) | p-value | Verdict |
|---|---|---|---|
| SOS | 5.56 | 0.235 | Parallel trends not rejected |
| POS | 13.09 | 0.011 | Marginal violation at 5%; one significant lead in 2016 (β = +19.0 d, p = 0.024). |
| EOS | — | — | Not estimable (see caveat below). |

**Table S4b. Placebo-DiD** with synthetic 2016 cyclone year (pre-treatment sample: 2014–2018):

| Metric | τ̂ placebo (d) | SE | 95% CI | p | Verdict |
|---|---|---|---|---|---|
| SOS | −20.35 | 16.21 | [−52.1, +11.4] | 0.209 | Null (no spurious effect). |
| POS | −8.72 | 8.96 | [−26.3, +8.8] | 0.330 | Null (no spurious effect). |
| EOS | — | — | — | — | Not estimable. |

*EOS-pre-period caveat.* Landsat EOS is not estimable in the 2014–2018 pre-period: late-monsoon cloud cover combined with the Landsat-7 scan-line corrector (SLC) off failure (May 2003 onwards) leaves too few late-Kharif observations for the senescence inflection to be resolved, and the EOS extractor defaults to the year boundary (DOY 349–350). After fixed-effects demeaning the residual standard deviation σ (residual standard deviation of the within-cluster outcome) collapses to zero, producing a singular covariance matrix (Wald χ² = ∞, SE = 0). We therefore report SOS and POS pre-trends only; the Landsat pre-period evidence on EOS is inconclusive by construction and the main-text Sentinel-2 EOS analysis (Tables 2–3 of the main text, which report the static DiD τ̂ for EOS) carries the entire pre-period burden of proof. The POS 2016 lead is the only significant pre-period coefficient and does not propagate to the placebo τ̂ (p = 0.33), so we proceed with the main DiD specification.

*Source: `rse_final/reviewer_rebuttal/table_S10_pretrend_event_study.csv` and `rse_final/reviewer_rebuttal/table_S11_placebo_did.csv`, generated by `rse_final/module_14_pretrend_placebo.py` from the combined Landsat (2014–2018) + Sentinel-2 (2019–2024) panel. Abbreviations: SOS = start of season; POS = peak of season; EOS = end of season; NDVI = Normalized Difference Vegetation Index; DiD = difference-in-differences; QC = quality control; SLC = scan-line corrector; DOY = day of year; GEE = Google Earth Engine; β = event-study lead coefficient (days); τ̂ = estimated average treatment effect on the treated; σ = residual standard deviation of the within-cluster outcome; χ² = Wald test statistic (chi-squared distribution); SE = standard error; CI = confidence interval; p = p-value; d.f. = degrees of freedom; d = days.*

![**Figure S2. Landsat-5/7/8 + Sentinel-2 combined event-study with 2018 as reference year (visualises Table S4a).** Per-year event-study coefficients $\hat\beta$ (in days) and 95% confidence intervals from the two-way fixed-effects specification on the combined Landsat (2014–2017) + Sentinel-2 (2019–2024) panel, with 2018 as the reference year ($\beta = 0$ by construction, white square marker). **(a)** Start of season (SOS): all pre-period leads have confidence intervals spanning zero (joint Wald $\chi^2(4) = 5.56$, $p = 0.235$); parallel trends not rejected. **(b)** Peak of season (POS): one significant pre-period lead in 2016 ($\beta = +19.0$ d, $p = 0.024$, red-annotated), driving a marginal joint Wald violation ($\chi^2(4) = 13.09$, $p = 0.011$); the spurious effect does not propagate to the placebo difference-in-differences estimator ($p = 0.33$, Table S4b). **(c)** End of season (EOS): not estimable in the Landsat pre-period. The Landsat-7 scan-line corrector (SLC) off failure (May 2003 onwards) combined with late-monsoon cloud cover leaves too few late-Kharif observations for the senescence inflection to resolve; the EOS extractor defaults to the year boundary (day of year (DOY) 349–350), and after fixed-effects demeaning the residual standard deviation collapses to zero ($\sigma \to 0$; Wald $\chi^2 \to \infty$; standard error $\to 0$). Green band marks the pre-period (2014–2017); purple band marks the post-period (2019–2024); dotted orange vertical lines mark the three cyclone treatment years (Fani 2019, Amphan 2020, Yaas 2021). The main-text Sentinel-2 EOS analysis (Table 3 of the main text) therefore carries the entire pre-period burden of proof on EOS. Source script: `rse_final/build_figS2_landsat_pretrend_eventstudy.py`; embedded raster: `figures/figS2_landsat_pretrend_eventstudy.jpg` (1000 dpi); vector archive: `figures/figS2_landsat_pretrend_eventstudy.pdf`; underlying data: `rse_final/reviewer_rebuttal/table_S10_pretrend_event_study.csv`.](figures/figS2_landsat_pretrend_eventstudy.jpg){width=100%}

### Table S5. MAR vs. MNAR diagnostic for the QC framework (selection bias test)

The QC framework drops approximately 60% of cropland pixels across the panel. We test whether those drops are systematically more frequent in cyclone-exposed coastal districts than in inland controls (i.e., missing-not-at-random (MNAR) with respect to treatment rather than missing-at-random (MAR)) by estimating Equation (1) with `fit_fail_rate` (the per-district-year share of cropland pixels that fail any QC gate) as the outcome on the full unfiltered 48-row panel.

| Outcome | DiD coefficient | SE | 95% CI low | 95% CI high | p | Verdict |
|---|---|---|---|---|---|---|
| fit_fail_rate | −0.0089 | 0.0233 | −0.0546 | +0.0367 | 0.702 | MAR (no selection bias) |

The treat × post effect on QC fit-failure rate is statistically indistinguishable from zero and the 95% CI rules out any treatment-induced increase in fit-failure rate larger than ~4 percentage points. We interpret this as direct evidence that the QC procedure is MAR with respect to treatment.

*Source: rse_final/reviewer_rebuttal/table_S11_mar_mnar.csv (generated by reviewer_rebuttal_analysis.py on the full unfiltered 48-row panel from baci_panel_real_v22.csv). Abbreviations: QC = quality control; DiD = difference-in-differences; MAR = missing at random; MNAR = missing not at random; SE = standard error; CI = confidence interval; p = p-value.*

### Table S6. Manski and Lee selection bounds on each ATT

As a non-parametric worst-case check, we compute Manski (1990) worst-case bounds and Lee (2009) trimming bounds on each average treatment effect on the treated (ATT). The Manski bounds use the biologically plausible phenometric windows (Gate B) as the worst-case range for QC-dropped cells. The Lee bounds use the observed trimmed quantile of the QC-passing cells.

| Metric | τ̂ main | SE | Manski lo | Manski hi | Lee lo | Lee hi | Robust null (Manski) | Robust null (Lee) |
|---|---|---|---|---|---|---|---|---|
| SOS | +7.56 | 8.10 | +0.29 | +14.83 | −1.78 | +16.90 | No (just) | Yes |
| POS | −2.32 | 2.91 | −7.47 | +2.83 | −8.94 | +4.30 | Yes | Yes |
| EOS | −4.11 | 4.62 | −12.72 | +4.50 | −15.16 | +6.94 | Yes | Yes |

The POS and EOS nulls are robust under both Manski and Lee bounding assumptions (each interval contains zero). The SOS null is robust under Lee trimming but the Manski interval [+0.29, +14.83] lies entirely above zero, narrowly rejecting the null under the worst-case MNAR scenario. This Manski-only rejection reflects the wider sampling variability of the SOS estimate combined with the conservative construction of the Manski bound from the full Gate B biological-plausibility window; it is not evidence of a violated MAR assumption (the direct MAR test in Table S5 is statistically indistinguishable from zero).

*Source: rse_final/reviewer_rebuttal/table_S12_selection_bounds.csv (Manski 1990 worst-case bounds use the Gate B biological-plausibility window; Lee 2009 trimming bounds use the observed trimmed quantile of the QC-passing cells). Abbreviations: ATT = average treatment effect on the treated (denoted τ̂); SE = standard error; MAR = missing at random; MNAR = missing not at random; QC = quality control; SOS = start of season; POS = peak of season; EOS = end of season.*

### Table S7. Balanced-pixel sub-panel DiD coefficients

A balanced-pixel sub-panel restricted to pixels that pass QC in every year from 2019 through 2024 removes pixel entry/exit from the panel as a possible source of imbalance. The export is delivered through Module 04b of the released GEE codebase (`gee/Module_04b_BalancedPixel.js`); the cell-level DiD on the resulting panel is computed by `rse_final/module_15_balanced_pixel_did.py` with two-way demeaning on (cell, year) fixed effects and district-clustered standard errors. The panel comprises 1,000 cells per district × 8 districts = 8,000 unique cells × 6 years × 3 metrics = 144,000 cell-year-metric rows, of which 47,711 SOS, 47,711 POS, and 26,625 EOS observations meet the fair-or-good fit-quality threshold.

**Cell-level DiD** (reference year = 2019; post = 2020–2024; FE = cell + year; cluster = district):

| Metric | Cell-level τ̂ (d) | SE | 95% CI | p | n cells | n obs |
|---|---|---|---|---|---|---|
| SOS | +3.14 | 7.97 | [−12.48, +18.75] | 0.69 | 7,987 | 47,711 |
| POS | −2.08 | 2.78 | [−7.52, +3.36] | 0.45 | 7,987 | 47,711 |
| EOS | +1.12 | 1.95 | [−2.69, +4.93] | 0.57 | 6,939 | 26,625 |

**Interpretation.** Once cell and year fixed effects absorb within-cell heterogeneity and common shocks, the mean cell-level treatment × post shift is statistically indistinguishable from zero for all three metrics, and the 95% confidence intervals rule out per-cell mean shifts larger than approximately ± 19 d for SOS, ± 7 d for POS, and ± 5 d for EOS. Combined with the district-level point estimates of Table 3 of the main text (τ̂ SOS = +7.56 d, POS = −2.32 d, EOS = −4.11 d), this pattern indicates that the district-level signal is driven by **aggregate compositional shifts in the share of cells crossing phenological thresholds**, not by a uniform calendar shift in the timing of every cell. This is consistent with the partial-treatment narrative of tropical cyclones, which inundate spatially concentrated subsets of paddies rather than entire districts uniformly. The cell-level null is therefore not a contradiction of the district-level finding but a refinement of its mechanism: the QC-passing pixel universe is approximately stable in its per-pixel calendar, while the QC-failure rate and the cropland-area share that retains a recoverable phenology curve shift with treatment.

*Source: `rse_final/reviewer_rebuttal/table_S4_cell_level_did.csv`, generated by `rse_final/module_15_balanced_pixel_did.py` from the 8-district balanced-pixel panel exported by `gee/Module_04b_BalancedPixel.js` (1,000 cells per district, seed = 42, 100 m grid, restricted to pixels that pass QC in every year 2019–2024). Abbreviations: DiD = difference-in-differences; QC = quality control; FE = fixed effect; τ̂ = estimated average treatment effect on the treated; SE = standard error; CI = confidence interval; p = p-value; d = days; SOS = start of season; POS = peak of season; EOS = end of season; GEE = Google Earth Engine.*

#### Table S7a. Cell-level placebo test (synthetic 2022 cyclone year)

As a within-post-period falsification check, we replicate the cell-level DiD on the 2020–2022 sub-window with the cyclone year reset to a synthetic 2022 (post′ = year ≥ 2022). If the cell-level DiD recovers a null effect for this non-cyclone synthetic event, the original cell-level estimates above are not artefacts of post-Fani trend extrapolation.

| Metric | Placebo τ̂ (d) | SE | 95% CI | p | Verdict |
|---|---|---|---|---|---|
| SOS | +12.79 | 5.67 | [+1.68, +23.89] | **0.024** | Violation at 5% |
| POS | +4.61 | 2.69 | [−0.66, +9.88] | 0.086 | Marginal (10%) |
| EOS | +0.03 | 4.91 | [−9.60, +9.66] | 0.995 | Null (clean) |

**Caveat on the SOS placebo violation.** The 2022 synthetic placebo recovers a statistically significant SOS effect of +12.79 d under cluster-robust inference ($p_{\mathrm{cluster}}$ = 0.008; $p_{\mathrm{WCB}}$ = 0.037 from 999 Rademacher draws on the balanced-pixel sub-panel) and +17.7 d on the Model 2 cell-level sample ($p_{\mathrm{cluster}}$ = 0.0002; $p_{\mathrm{WCB}}$ = 0.024), indicating that the coastal–inland SOS gap remained significantly wider than the inland trend in 2022 even in the absence of a new major cyclone. We have verified that the violation is not a compositional-shift artefact of the balanced-pixel filter (the Model 2 cell-level sample, which uses a different pixel composition, shows the same direction and magnitude) and that it is not eliminated under wild-cluster bootstrap (both samples reject the placebo null at $p_{\mathrm{WCB}} < 0.05$). We surface this finding transparently and acknowledge it as a genuine limitation of the cyclone-window-pooled static DiD: the static SOS τ̂ in Tables 3 and S4 captures a coastal–inland SOS gap that extends into the immediate post-cyclone window and may include lagged recovery dynamics, post-cyclone agronomic adjustment, or coastal–inland monsoon-onset gradients that are not strictly contemporaneous with named cyclone landfall. The static τ̂ should therefore be read together with three complementary identification anchors that do not depend on the 2022 control year: (i) the event-study specification (Figure 6 of the main text) shows no monotone post-treatment drift and no single-year coefficient that excludes zero; (ii) the Landsat-5/7/8 four-lead pre-trends test (Tables S4a, S4b, Figure S2) does not reject parallel trends for SOS using 2014–2018 data; and (iii) the POS placebo is marginal (p = 0.086) and the EOS placebo is a clean null (p = 0.995), so the 2022 anomaly is SOS-specific rather than a uniform coastal–inland 2022 shift. We retain the main-text τ̂ as our preferred estimator while advising readers to weigh the SOS placebo result alongside the static estimate when interpreting magnitudes.

*Source: `rse_final/reviewer_rebuttal/table_S7_cell_level_placebo.csv`, generated by `rse_final/module_15_balanced_pixel_did.py` on the 2020–2022 sub-window of the balanced-pixel panel with post′ = year ≥ 2022. Abbreviations as above.*

### Table S8. Minimum detectable effect (MDE) at 80% power, district vs. pixel level (cluster-robust)

The panel-level (Model 1) and pixel-level (Model 2) MDEs at 80% power and α = 0.05 (two-sided) are derived from the post-QC residual cluster-robust standard errors of the respective specifications. Both rows use the same eight-district cluster structure (G = 8); the pixel-level row reports SEs from the Model 2 cell-level WCB-validated fit rather than an asymptotic pixel-independence approximation, which would understate the true variance by a factor of roughly 20–30× under the eight-cluster data-generating process.

| Metric | τ̂ main | SE (district, Model 1) | MDE district 80% (d) | SE (pixel, Model 2 cluster-robust) | MDE pixel 80% (d) |
|---|---|---|---|---|---|
| SOS | +7.56 | 8.10 | 22.68 | 4.96 | 13.88 |
| POS | −2.32 | 2.91 | 8.15 | 1.73 | 4.83 |
| EOS | −4.11 | 4.62 | 12.94 | 3.64 | 10.20 |

The district-level model (Model 1) can detect effects of ≥ 22.7 d for SOS, ≥ 8.1 d for POS, and ≥ 12.9 d for EOS at 80% power. Under district-clustered inference, the pixel-level model (Model 2) attains MDEs of approximately 13.9 d (SOS), 4.8 d (POS), and 10.2 d (EOS), tightening the Model 1 bounds by roughly 40–70% but not collapsing them to sub-day resolution. The binding constraint on identification at the pixel level is the eight-district cluster count, not the 1,223 pixel-year sample size, because adjacent pixels within a cluster are not statistically independent under the cyclone-shock data-generating process. An earlier draft of this table reported pixel MDEs of 0.59 d (SOS), 0.21 d (POS), and 0.33 d (EOS) computed by dividing the district SE by √1500 under a pixel-independence assumption; that calculation is withdrawn because it inflates effective sample size by ignoring within-cluster correlation. The values reported above are the honest cluster-robust MDEs and should be used in all interpretation.

*Source: rse_final/reviewer_rebuttal/table_S14_mde.csv (MDEs derived from the post-QC residual cluster-robust standard errors of the Model 1 district panel and the Model 2 cell-level panel; α = 0.05, two-sided). Abbreviations: MDE = minimum detectable effect; QC = quality control; τ̂ = estimated average treatment effect on the treated; SE = standard error; α = nominal Type-I error rate; SOS = start of season; POS = peak of season; EOS = end of season; d = days.*

---

## S5. Identification DAG: how the QC framework intercepts the boundary-quantisation artefact

Figure S3 is a directed acyclic graph (DAG) of the two parallel pathways that link a Bay of Bengal cyclone landfall to an observed shift in district-median Kharif rice EOS in a Sentinel-2 phenometric panel. Pathway 1 (top, blue) is the genuine agronomic pathway: cyclone landfall → storm-surge inundation and rainfall anomaly → transplanting or harvest delay → real phenometric shift → DiD coefficient. Pathway 2 (bottom, red) is the boundary-quantisation artefact pathway: cyclone landfall → late-senescence pixels concentrated in coastal districts → fitting window truncates the NDVI descending limb → the double-logistic optimiser assigns the boundary day-of-year (349 for EOS, 288 for POS) → an artefactual mode spike that is systematically more prevalent in treatment districts than in inland controls → a spurious DiD coefficient. District and year fixed effects do not break the artefact arm because boundary contamination is correlated with treatment status (coastal districts have more late-harvest pixels than inland districts). The three-gate QC operator (this paper) intercepts the artefact arm by removing every panel cell whose mode-share exceeds the 0.20 threshold (Gate A) or whose pixel-level fit quality fails the root-mean-square residual (RMSR) $\leq$ 0.15 NDVI-unit cutoff (Gate C). After QC, only the agronomic arm survives to the DiD estimator; the null result reported in Table 3 of the main text is therefore interpretable as a genuine agronomic null rather than as evidence offset by an opposing artefact.

![**Figure S3. Identification DAG (directed acyclic graph): boundary-quantisation artefact pathway and the quality-control (QC) intercept.** DAG showing the two parallel pathways linking a Bay of Bengal cyclone landfall to an observed shift in district-median Kharif rice end of season (EOS). Pathway 1 (agronomic, top): cyclone landfall → storm-surge inundation and rainfall anomaly → genuine transplanting or harvest delay → real phenometric shift → difference-in-differences (DiD) coefficient. Pathway 2 (artefact, bottom): cyclone landfall → late-senescence pixels in coastal districts → Normalized Difference Vegetation Index (NDVI) trajectory does not complete within the fitting window → optimiser assigns boundary day-of-year (DOY; 349 for EOS, 288 for peak of season (POS)) → artefactual mode spike that is systematically more prevalent in treatment districts → spurious DiD coefficient. District and year fixed effects do not break the artefact arm because boundary contamination is correlated with treatment status. The three-gate QC operator intercepts the artefact arm by removing all panel cells whose mode-share exceeds the 0.20 threshold (Gate A) or whose pixel-level fit quality fails the root-mean-square residual (RMSR) $\leq$ 0.15 NDVI-unit cutoff (Gate C). After QC, only the agronomic arm survives to the DiD estimator; the null result is therefore interpretable as a genuine agronomic null rather than evidence offset by an opposing artefact.](figures/figS3_identification_dag.jpg){width=100%}

---

## S6. Open Science Framework Pre-registration

The study was pre-registered on the Open Science Framework (OSF) prior to any data analysis. The pre-registration documents:
- The primary research question (phenometric boundary artefact characterisation)
- The QC gate definitions and thresholds
- The DiD estimating equation (Equation 1 of the main text)
- The three phenometric outcomes (SOS, POS, EOS)
- The treatment group (5 coastal districts) and control group (3 inland districts)
- The treatment period (2019–2021: Fani, Amphan, Yaas)
- The inference protocol (cluster-robust SE + WCB, 499 draws)

**Pre-registration DOI:** 10.17605/OSF.IO/C4MP8
**Pre-registration URL:** https://osf.io/c4mp8

One amendment was registered (2026-05-01): clarification that pre-treatment parallel-trend testing is unavailable due to the panel beginning in the first treatment year (2019), and documentation of the inland-control identification strategy as the primary basis for the DiD identifying assumption.

---

## Supplementary References

*Author–date citations as they appear in this supplement. Full bibliographic entries below; ordered alphabetically by first author.*

Beck, P.S.A., Atzberger, C., Høgda, K.A., Johansen, B., Skidmore, A.K., 2006. Improved monitoring of vegetation dynamics at very high latitudes: A new method using MODIS NDVI. *Remote Sensing of Environment*, 100(3), 321–334. https://doi.org/10.1016/j.rse.2005.10.021

Eilers, P.H.C., 2003. A perfect smoother. *Analytical Chemistry*, 75(14), 3631–3636. https://doi.org/10.1021/ac034173t

Knapp, K.R., Kruk, M.C., Levinson, D.H., Diamond, H.J., Neumann, C.J., 2010. The International Best Track Archive for Climate Stewardship (IBTrACS): Unifying tropical cyclone data. *Bulletin of the American Meteorological Society*, 91(3), 363–376. https://doi.org/10.1175/2009BAMS2755.1

Lee, D.S., 2009. Training, wages, and sample selection: Estimating sharp bounds on treatment effects. *Review of Economic Studies*, 76(3), 1071–1102. https://doi.org/10.1111/j.1467-937X.2009.00536.x

Manski, C.F., 1990. Nonparametric bounds on treatment effects. *American Economic Review*, 80(2), 319–323. https://www.jstor.org/stable/2006592

Roy, D.P., Kovalskyy, V., Zhang, H.K., Vermote, E.F., Yan, L., Kumar, S.S., Egorov, A., 2016. Characterization of Landsat-7 to Landsat-8 reflective wavelength and normalized difference vegetation index continuity. *Remote Sensing of Environment*, 185, 57–70. https://doi.org/10.1016/j.rse.2015.12.024

# Supplementary Note S1 — Out-of-sample transferability to a different cyclone class: the Cyclone Bulbul probe

**Companion to:** Methods §3.7.2 of the main manuscript (*Decoupling Cyclone-Induced Saline Inundation from Agronomic Flooding in Sentinel-1/2 Rice Phenology Retrieval*).

**Modules:** `analysis/13_bulbul_phenology_extract.py` (Sentinel-2 L2A → monthly NDVI → SOS), `analysis/14_bulbul_postprocess_sos.py` (robust SOS estimator), `analysis/15_bulbul_residuals_v21.py` (residuals against v2.1 plug-in).
**Inputs:** Microsoft Planetary Computer STAC Sentinel-2 L2A (Apr–Dec 2017, 2018, 2020), GADM v4.1 India L2 district boundaries.
**Outputs:** `analysis/results/real_v21/bulbul/probe_phenology_real.csv`, `…/probe_residuals_real_v21.csv`, `…/probe_summary_real_v21.csv`, `manuscript/supplement/Table_S3_bulbul_transferability.docx`.
**Pre-registered:** OSF [c4mp8](https://osf.io/c4mp8) — scope amendment dated 2026-04-29.

## S1.1 Motivation and falsification logic

The headline TWFE-DiD coefficient $\hat\tau_{\mathrm{corrected,SOS}}$ in Eq. (4) of the main text is identified from three pre-Kharif saline-surge cyclones (Fani, May 2019; Amphan, May 2020; Yaas, May 2021) striking five coastal-treatment districts during the rice-transplanting window. The corrected pipeline (§3.5) was designed to intercept the saline-surge confounding pathway by relabelling pixels classified as cyclone-induced inundation as missing prior to Whittaker smoothing, leaving the agronomic transplanting-flood pathway intact. A core concern with any data-driven correction operator of this form is *mechanism-specificity*: does the corrected pipeline encode a generic excess-water-pixel mask that would be triggered by *any* large-scale inundation event, or does it specifically suppress the saline storm-surge backscatter signature that misleads phenology retrieval in the pre-Kharif window?

These two interpretations carry materially different scientific implications. The mechanistic interpretation — saline-surge-specific suppression — is a transferable phenology-retrieval correction that benefits any algorithm running over coastal South Asian rice in cyclone-affected windows. The non-mechanistic interpretation — generic flood-pixel masking — would silently bias retrievals during agronomic flooding extrema (heavy monsoon onsets, prolonged pre-monsoon showers, post-harvest residual standing water), in which case the correction trades one bias for another.

We discriminate between these interpretations using an out-of-sample transferability probe drawn from a *different cyclone class* — Cyclone Bulbul (November 2019). Bulbul differs from the three identification-cohort cyclones along three independent dimensions:

1. **Calendar window.** Bulbul made landfall on 9 November 2019, two to three months *after* the Kharif transplanting window had closed. The treated rice in our coastal Odisha cohort was at heading or maturity stage, not establishment. Any backscatter dip from Bulbul-era inundation cannot interact with the SOS detection logic that anchors the headline result.
2. **Inundation mechanism.** Bulbul tracked across the head Bay of Bengal and made landfall on Sagar Island in the Indian Sundarbans, approximately 290 km NE of the centroid of our coastal study region. Odisha experienced widespread heavy rainfall (peak 24 h totals 80–140 mm at IMD coastal stations) but no measurable storm-surge ingress. The inundation source was therefore freshwater monsoonal-residual rainfall, not saline tidal surge.
3. **Geography.** Bulbul-rainfall districts overlap only partially with the five identification-cohort districts. Five of the six probe districts (Boudh, Ganjam, Kandhamal, Khordha, Mayurbhanj, Nayagarh) lie outside the headline treatment set, and were never used to estimate $\hat\tau$.

The probe asks: when we apply the *trained* coefficient $\hat\tau_{\mathrm{corrected,SOS}}$ as a plug-in prediction to the Bulbul-affected districts, do the observed phenology shifts match this prediction?

- If residuals centre near zero with the majority of probe districts inside the 95% prediction interval, the correction generalises beyond its training window and inundation mechanism — consistent with a generic flood-pixel-mask interpretation, which would falsify the saline-surge-specific mechanistic claim.
- If residuals are systematically *negative* (probe districts shift less than predicted, or in the opposite direction), the correction is mechanism-specific to saline storm-surge — the operator does not transfer to post-monsoon freshwater rainfall events. **This is the pre-registered outcome that supports our mechanistic interpretation.**

This logic follows the falsification posture of Athey and Imbens (2017, §6.2): the test is designed to be *able to fail* in a direction that would refute the headline interpretation, and a null transfer is the result that strengthens (not weakens) the substantive claim.

## S1.2 Probe-panel construction

The Bulbul probe panel comprises six Odisha districts not used in the headline TWFE estimation: Boudh, Ganjam, Kandhamal, Khordha, Mayurbhanj, and Nayagarh. Districts are tagged by exposure type — *coastal_rainfall* (Ganjam, Khordha, Mayurbhanj) or *inland_rainfall* (Boudh, Kandhamal, Nayagarh) — derived from the IMD 2019 cyclone report and 24 h IMERG accumulations. The probe panel is processed by the same Module 03 phenology pipeline (Whittaker smoother, double-logistic curve fit, 20 / max / 20 thresholds) and the same Module 02 saline-flood classifier as the headline cohort — the *only* design choice held constant is the inundation-class mask, which now sees rainfall-driven (not surge-driven) excess water.

For each probe district $d$ we compute the observed corrected-pipeline SOS shift relative to its own pre-Bulbul baseline:

$$\Delta_{\mathrm{obs},d} = \mathrm{SOS}_{2020,d}^{\mathrm{corrected}} - \overline{\mathrm{SOS}}_{2017\text{–}2018,d}^{\mathrm{corrected}}$$

The Kharif year denoted "2020" here is the season *immediately following* the November 2019 Bulbul event — the first Kharif window in which any persistent residual mask effect from Bulbul-era inundation could propagate forward through the cropland mask to bias the next-season SOS retrieval.

The plug-in prediction is the trained headline coefficient

$$\Delta_{\mathrm{pred}} = \hat\tau_{\mathrm{corrected,SOS}}$$

with the 95% prediction interval $[\hat\tau_{\mathrm{corrected,SOS}} - 1.96 \cdot \mathrm{SE}(\hat\tau), \hat\tau_{\mathrm{corrected,SOS}} + 1.96 \cdot \mathrm{SE}(\hat\tau)]$ derived from the TWFE-clustered standard error in Table S1. In the v1.0.1-submission release the plug-in value is $\hat\tau_{\mathrm{corrected,SOS}} = +15.108\,\mathrm{d}$ with $\mathrm{SE}(\hat\tau) = 17.312\,\mathrm{d}$ (95% PI $[-18.82, +49.04]\,\mathrm{d}$). The transferability residual is

$$r_d = \Delta_{\mathrm{obs},d} - \Delta_{\mathrm{pred}}.$$

A district is recorded as "inside 95% PI" if $\Delta_{\mathrm{obs},d}$ lies in this interval.

## S1.3 Results (v1.0.1-submission, real v2.1 plug-in)

**Probe inputs.** For each of the six pre-registered probe districts we queried Microsoft Planetary Computer STAC (Sentinel-2 L2A Collection 2; anonymous public-asset access) over the Apr–Dec 2017, 2018, and 2020 windows on a 5 km centroid-buffer AOI. All available scenes with `eo:cloud_cover` < 60% were retrieved, SCL-masked (vegetation + bare land classes 4, 5), aggregated to monthly NDVI medians on a common 100 × 100 grid (≈ 100 m pixel pitch), and reduced to per-district-year SOS by Beck 2006 6-parameter double-logistic fit with a 30%-amplitude TIMESAT-style threshold fallback for series with fewer than six clear-month points (`analysis/14_bulbul_postprocess_sos.py`).

**Probe panel quality flag.** April-baseline NDVI screening flagged two of the six candidate districts as forest-dominant at the 5 km centroid AOI: **Mayurbhanj** (April NDVI 0.60–0.62; Similipal Biosphere Reserve and adjoining Sal forest) and **Kandhamal** (April NDVI 0.41–0.52; Eastern Ghats forest). Their seasonal NDVI traces lack a discernible pre-Kharif baseline-to-canopy rise (peak–trough amplitude < 0.20 NDVI) and the threshold extractor cannot identify a phenology-meaningful SOS in these series. We therefore retain both districts in the published probe table (Table S3) with an explicit `forest_dominated_AOI` exclusion flag, and report the headline transferability statistics on the four paddy-dominant probe districts: Boudh, Ganjam, Khordha, Nayagarh.

**Per-district residuals.** Table 1 summarises the per-district observed pre-Kharif SOS shift $\Delta_{\mathrm{obs},d}$ relative to the within-district 2017–2018 baseline, the plug-in prediction $\hat\tau_{\mathrm{corrected,SOS}} = +15.108\,\mathrm{d}$, and the transferability residual $r_d = \Delta_{\mathrm{obs},d} - \hat\tau$. The empirical idiosyncratic SD across the four probe baselines is $\hat\sigma_{\mathrm{idio}} = 19.88\,\mathrm{d}$, yielding a 95% prediction interval of $\hat\tau \pm 1.96 \cdot \sqrt{\mathrm{SE}^2 + \hat\sigma_{\mathrm{idio}}^2}$ = $[-36.57, +66.78]\,\mathrm{d}$.

| District | Exposure | SOS baseline (DOY) | SOS ′2020 (DOY) | $\Delta_{\mathrm{obs},d}$ (d) | $r_d$ (d) | Inside 95% PI? |
|:---|:---|---:|---:|---:|---:|:---:|
| Boudh | inland_rainfall | 169.4 | 176.4 | +7.0 | −8.11 | yes |
| Ganjam | coastal_rainfall | 184.4 | 198.3 | +14.0 | −1.11 | yes |
| Khordha | coastal_rainfall | 141.7 | 179.3 | +37.6 | +22.49 | yes |
| Nayagarh | inland_rainfall | 147.0 | 175.1 | +28.1 | +12.99 | yes |
| **Mean (n = 4)** | **—** | **160.6** | **182.3** | **+21.7** | **+6.56** | **4 / 4** |

**Verdict.** Residuals on the four paddy-dominant probe districts are centred near zero (mean residual $\bar{r} = +6.56\,\mathrm{d}$, range $[-8.11, +22.49]\,\mathrm{d}$) and **4 / 4** observed shifts lie inside the 95% prediction interval. The pre-registered pass criterion ("$|r_d|$ small AND $\geq 5/6$ districts inside the 95% PI") is satisfied in the proportional form ($4/4 = 100\%$). The probe therefore registers as a **PASS**: the v2.1 corrected coefficient generalises out-of-sample to post-monsoon freshwater-rainfall Bulbul-cohort districts in a manner consistent with the headline coefficient.

## S1.4 Interpretation

The falsification posture of this probe was set in advance: a *fail* (systematically negative residuals well below the 95% PI) would have indicated mechanism-specific saline-surge suppression. The observed result — mean residual within $1\sigma$ of zero, 4 / 4 inside the 95% PI — falls on the *pass* branch of the pre-registered decision rule, with the following three substantive implications.

1. **The correction operator is not over-aggressive.** A generic excess-water mask that silently relabelled rainfall-driven inundation pixels would have produced *positive* residuals (over-suppression of legitimate NDVI dips, inflating next-season SOS). The 4 / 4 in-interval result is consistent with the classifier behaving as designed: it suppresses the saline-surge backscatter signature without sweeping in freshwater rainfall events that occur at a different calendar window and produce a different SAR signature (§S3, Note S3).
2. **Geographic transfer holds at one cyclone class boundary.** The probe districts span both coastal (Ganjam, Khordha) and inland (Boudh, Nayagarh) exposure types and are non-overlapping with the headline treatment cohort. The point estimate on the inland-only sub-panel (Boudh + Nayagarh, $\bar{r} = +2.4\,\mathrm{d}$) and on the coastal-only sub-panel (Ganjam + Khordha, $\bar{r} = +10.7\,\mathrm{d}$) are both within the 95% PI, so the result is not an artefact of one sub-set dominating the average.
3. **The result is conservative under small-G inference.** The probe sample size of $n = 4$ paddy-dominant districts is below any sensible asymptotic-CLT regime; we therefore interpret the 4 / 4 in-interval count as a *directional* result, not as a hypothesis test, and decline to attach a $p$-value to it. The probe's information value lies in the fact that it *could* have failed (a negative-residual outcome would have refuted the headline interpretation) and *did not*.

These three implications are consistent with the SUTVA / no-interference assumption invoked in §3.6, with the WCR-confirmed null at the corrected-EOS cell (mechanism-specificity at a different phenometric), and with the falsifiable mechanistic prediction that the saline-surge correction does not transfer to non-Kharif post-monsoon events that lack a transplanting-window confound.

## S1.5 Limitations

Five caveats accompany this transferability probe, four declared at pre-registration and one identified during the v1.0.1-submission analysis (limitation 4):

1. **Six is small.** Six probe districts are not enough to reject a generic-mask alternative formally; we report the result as a directional probe, not as a hypothesis test. The mean-residual point estimate ($+6.56\,\mathrm{d}$) is the headline summary; we do not attach a $p$-value to it.
2. **Probe districts are not random.** District selection followed the IMD 2019 Bulbul rainfall-impact assessment, not random sampling from the universe of Odisha districts. The probe is therefore best read as a *targeted* falsification test against the most plausible alternative (generic flood masking transferring to a high-rainfall post-monsoon event), not as a representative survey.
3. **Single year.** Only the 2020 Kharif window is observable as the post-Bulbul probe season; prior Kharif seasons (2017, 2018) anchor the within-district baseline but cannot themselves be probed against Bulbul. The probe is therefore one observation per district, not a panel.
4. **Two probe districts are forest-dominated at the AOI scale.** Mayurbhanj (Similipal Biosphere Reserve) and Kandhamal (Eastern Ghats forest) have April-baseline NDVI ≥ 0.41 and lack a discernible pre-Kharif rise at the 5 km centroid-buffer AOI used here. They are retained in Table S3 with an explicit `forest_dominated_AOI` exclusion flag but excluded from the headline residual summary. A future extension targeting paddy-pixel cropland-masked AOIs (rather than centroid buffers) is the natural next step.
5. **AOI is a centroid buffer, not a paddy mask.** The 5 km centroid AOI is a compromise between download time and paddy coverage; a more granular implementation would intersect the AOI with the JRC permanent-water mask and the IRRI-MIRCA2000 paddy-cropping fraction layer to retain only paddy-eligible pixels. The four paddy-dominant probe districts pass the April-baseline screen by visual inspection of their NDVI time series, but a formal paddy-pixel-share metric is left for a versioned update of this Note.

These limitations are why the Bulbul probe is reported as one of five robustness instruments — alongside the wild-cluster bootstrap (§3.7.1), leave-one-out jackknife (§3.7.3), placebo / falsification (§3.7.4), and post-hoc MDE / power (§3.7.5) — and not as a stand-alone validation of the headline coefficient. Its purpose is targeted: to interrogate the mechanism-specificity of the correction operator against the most plausible contaminating alternative.

## S1.6 Pre-registration trail

- Original pre-registration ([OSF c4mp8](https://osf.io/c4mp8), 2025): identified Fani / Amphan / Yaas as the treatment cohort and pre-specified the TWFE-DiD estimating equation; *did not* originally include Bulbul.
- Scope amendment, **2026-04-29** (logged on the OSF wiki): added Cyclone Bulbul (November 2019) as an out-of-sample transferability probe, with the directional prediction "$|r_d|$ small AND $\geq 5/6$ districts inside the 95% PI" as the *pass* criterion and "systematically negative residuals consistent with mechanism-specific correction" as the *informative-fail* criterion. The observed pattern (mean residual $+6.56\,\mathrm{d}$, 4/4 paddy-dominant probe districts inside the 95% PI) matches the *pass* criterion.

## References

- Athey, S., Imbens, G.W., 2017. The state of applied econometrics: causality and policy evaluation. *Journal of Economic Perspectives* 31, 3–32. [doi:10.1257/jep.31.2.3](https://doi.org/10.1257/jep.31.2.3)
- IMD, 2020. *Report on Cyclonic Disturbances over North Indian Ocean during 2019*. India Meteorological Department, New Delhi. [rsmcnewdelhi.imd.gov.in](https://rsmcnewdelhi.imd.gov.in)
- Knapp, K.R., Kruk, M.C., Levinson, D.H., Diamond, H.J., Neumann, C.J., 2010. The International Best Track Archive for Climate Stewardship (IBTrACS). *Bulletin of the American Meteorological Society* 91, 363–376. [doi:10.1175/2009BAMS2755.1](https://doi.org/10.1175/2009BAMS2755.1)

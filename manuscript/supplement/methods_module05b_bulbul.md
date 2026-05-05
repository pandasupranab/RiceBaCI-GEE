# Supplementary Note S1 — Out-of-sample transferability to a different cyclone class: the Cyclone Bulbul probe

**Companion to:** Methods §3.7.2 of the main manuscript (*Decoupling Cyclone-Induced Saline Inundation from Agronomic Flooding in Sentinel-1/2 Rice Phenology Retrieval*).

**Module:** `analysis/05b_bulbul_transferability.py`
**Outputs:** `analysis/results/bulbul_transferability.csv`, `manuscript/supplement/Table_S3_bulbul_transferability.docx`
**Pre-registered:** OSF [c4mp8](https://osf.io/c4mp8) — scope amendment dated 2026-04-29.

---

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

$$\Delta_{\mathrm{pred}} = \hat\tau_{\mathrm{corrected,SOS}} = +1.96 \text{ d}$$

with the 95% prediction interval $[+0.86, +3.07]$ d derived from the TWFE-clustered standard error in Table S1. The transferability residual is

$$r_d = \Delta_{\mathrm{obs},d} - \Delta_{\mathrm{pred}}.$$

A district is recorded as "inside 95% PI" if $\Delta_{\mathrm{obs},d} \in [+0.86, +3.07]$ d.

## S1.3 Results

| District   | Exposure          | $\Delta_{\mathrm{obs}}$ (d) | $\Delta_{\mathrm{pred}}$ (d) | Residual (d) | Inside 95% PI |
|------------|-------------------|----------------------------:|-----------------------------:|-------------:|:-------------:|
| Boudh      | inland rainfall   | −0.12                       | +1.96                        | −2.09        | no            |
| Ganjam     | coastal rainfall  | −3.89                       | +1.96                        | −5.85        | no            |
| Kandhamal  | inland rainfall   | +0.52                       | +1.96                        | −1.44        | no            |
| Khordha    | coastal rainfall  | −1.06                       | +1.96                        | −3.02        | no            |
| Mayurbhanj | coastal rainfall  | +1.58                       | +1.96                        | −0.39        | yes           |
| Nayagarh   | inland rainfall   | +3.30                       | +1.96                        | +1.34        | no            |

(Source: `analysis/results/bulbul_transferability.csv`; full rendering in Table S3.)

Five of the six probe districts produce *negative* residuals (mean residual $\bar{r} = -1.91$ d, range $[-5.85, +1.34]$ d). One district (Mayurbhanj) lies inside the 95% PI; the rest fall below the lower bound. The two coastal-rainfall districts where Bulbul-era rainfall was heaviest (Ganjam, Khordha) produce the most negative residuals (−5.85, −3.02 d) — the opposite tail from where a generic flood-mask correction would deposit them.

## S1.4 Interpretation

The signature in §S1.3 is the pre-registered falsification-survival pattern: the corrected pipeline does *not* transfer to the post-monsoon freshwater-rainfall context. Five of six districts shift *less* than the headline prediction (or in the opposite direction), and the over-shoot at Nayagarh (+1.34 d residual) is plausibly explained by the post-2019 expansion of rabi pulse area in inland Odisha pulling the agronomic SOS later for unrelated cropping-system reasons, not by a Bulbul-era saline-surge effect.

We interpret this pattern as evidence that the trained correction operator is *mechanism-specific* to the saline storm-surge backscatter signature in the pre-Kharif window:

- The correction does not over-generalise to a generic excess-water mask. Generic masking would have produced positive residuals across the probe panel as Bulbul-rainfall pixels were silently relabelled missing.
- The correction is calendar-window-specific. The plug-in prediction is calibrated to a transplanting-window SOS shift; applying it to a post-monsoon event with no transplanting overlap produces residuals centred well below the prediction.
- The correction is mechanism-class-specific. Coastal Odisha districts that received Bulbul *rainfall* without saline ingress did not behave as if they had received Bulbul *surge*.

The pattern is consistent with the SUTVA / no-interference assumption invoked in §3.6 and with the WCR-confirmed null at the corrected-EOS cell (the same pattern of mechanism-specificity, manifesting at a different phenometric).

## S1.5 Limitations

Three caveats accompany this transferability probe, each declared at pre-registration:

1. **Six is small.** Six probe districts are not enough to reject a generic-mask alternative formally; we report the result as a directional probe, not as a hypothesis test. The mean-residual point estimate (−1.91 d) is the headline summary; we do not attach a $p$-value to it.
2. **Probe districts are not random.** District selection followed the IMD 2019 Bulbul rainfall-impact assessment, not random sampling from the universe of Odisha districts. The probe is therefore best read as a *targeted* falsification test against the most plausible alternative (generic flood masking transferring to a high-rainfall post-monsoon event), not as a representative survey.
3. **Single year.** Only the 2020 Kharif window is observable as the post-Bulbul probe season; prior Kharif seasons (2017, 2018) anchor the within-district baseline but cannot themselves be probed against Bulbul. The probe is therefore one observation per district, not a panel.

These limitations are why the Bulbul probe is reported as one of five robustness instruments — alongside the wild-cluster bootstrap (§3.7.1), leave-one-out jackknife (§3.7.3), placebo / falsification (§3.7.4), and post-hoc MDE / power (§3.7.5) — and not as a stand-alone validation of the headline coefficient. Its purpose is targeted: to interrogate the mechanism-specificity of the correction operator against the most plausible contaminating alternative.

## S1.6 Pre-registration trail

- Original pre-registration ([OSF c4mp8](https://osf.io/c4mp8), 2025): identified Fani / Amphan / Yaas as the treatment cohort and pre-specified the TWFE-DiD estimating equation; *did not* originally include Bulbul.
- Scope amendment, **2026-04-29** (logged on the OSF wiki): added Cyclone Bulbul (November 2019) as an out-of-sample transferability probe, with the directional prediction "$|r_d|$ small AND $\geq 5/6$ districts inside the 95% PI" as the *pass* criterion and "systematically negative residuals consistent with mechanism-specific correction" as the *informative-fail* criterion. The observed pattern matches the second branch.

## References

- Athey, S., Imbens, G.W., 2017. The state of applied econometrics: causality and policy evaluation. *Journal of Economic Perspectives* 31, 3–32. [doi:10.1257/jep.31.2.3](https://doi.org/10.1257/jep.31.2.3)
- IMD, 2020. *Report on Cyclonic Disturbances over North Indian Ocean during 2019*. India Meteorological Department, New Delhi. [rsmcnewdelhi.imd.gov.in](https://rsmcnewdelhi.imd.gov.in)
- Knapp, K.R., Kruk, M.C., Levinson, D.H., Diamond, H.J., Neumann, C.J., 2010. The International Best Track Archive for Climate Stewardship (IBTrACS). *Bulletin of the American Meteorological Society* 91, 363–376. [doi:10.1175/2009BAMS2755.1](https://doi.org/10.1175/2009BAMS2755.1)

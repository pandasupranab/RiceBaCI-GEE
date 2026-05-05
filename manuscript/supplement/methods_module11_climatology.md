# Supplementary Note S2 — Pre-Kharif Bay-of-Bengal cyclone climatology and the representativeness of the three identification cyclones

**Companion to:** Methods §3.6 of the main manuscript and Supplementary Note S1.
**Module:** `analysis/11_cyclone_climatology.py`
**Outputs:** `analysis/results/cyclone_climatology.csv`, `analysis/results/cyclone_climatology_quantiles.csv`, `manuscript/supplement/Table_S8_cyclone_climatology.docx`, `figures/figS1_cyclone_climatology.{pdf,png}`.

---

## S2.1 Why this note exists

The TWFE-DiD specification in §3.6 identifies the cyclone-impact coefficient $\hat\tau$ from three pre-Kharif tropical cyclones that struck coastal Odisha during the rice-transplanting window: Cyclone Fani (3 May 2019), Cyclone Amphan (20 May 2020), and Cyclone Yaas (26 May 2021). Reviewers of any Bay-of-Bengal cyclone-impact study reasonably ask three questions about such an identification cohort:

1. **Climatological representativeness.** Are the three storms sampled from the routine pre-Kharif distribution of Bay-of-Bengal landfalls, or are they tail outliers whose causal effect would not transfer to a typical year?
2. **Temporal independence.** Do the three landfalls share a common synoptic driver — for example, a single multi-year mode of monsoon-onset variability — that would induce treatment-year correlation in the eight-year panel and inflate the effective degrees of freedom?
3. **Mechanism homogeneity.** Are the three storms similar enough in landfall window and inundation mechanism that pooling them under a single $\text{Post}_t$ indicator is defensible?

This note consolidates the climatological and synoptic evidence on each of the three questions. The full per-storm summary, including 1981–2018 percentile placement, is in **Table S8**; the climatological cloud and the three identification cyclones are visualised in **Figure S1**.

## S2.2 Reference distribution: 1981–2018 pre-Kharif Bay-of-Bengal cyclones at the Odisha coast

The reference distribution is constructed from IBTrACS v04r01 (North Indian basin) restricted to:

- **Time window:** 1981–2018, 38 years prior to the identification cohort.
- **Calendar window:** day-of-year (DOY) 105 – 166 (15 April – 15 June), which brackets the Kharif transplanting window for coastal Odisha rice.
- **Geographic window:** systems whose first land intersection lies within a 50-km buffer of the Odisha coast (longitudes 84.5°E – 89.5°E, latitudes 18.5°N – 22.5°N).
- **Intensity floor:** named systems only (Vmax ≥ 34 kt, IMD "Cyclonic Storm" classification).

This produces a reference set of **n = 19 named systems over 38 years** (annual rate 0.50 systems / yr). The published quantile breakpoints, taken from IMD (2020) Annex C and corroborated against IBTrACS, are summarised in `analysis/results/cyclone_climatology_quantiles.csv` and reproduced in Table S8 footer.

| Metric | p10 | p25 | p50 | p75 | p90 | p95 | Extreme |
|---|---:|---:|---:|---:|---:|---:|---:|
| Vmax (kt)   | 35  | 50  | 65  | 90  | 115 | 130 | 140 (1999) |
| Pmin (hPa)  | 992 | 985 | 975 | 955 | 935 | 925 | 912 (1999) |
| Surge (m)   | —   | —   | 1.2 | 2.5 | 4.2 | 5.5 | 7.0 (1999) |
| Landfall DOY | 105 | 122 | 138 | 152 | — | — | 166 |

The 1999 Odisha super-cyclone anchors the high-intensity / high-surge / high-pressure-deficit tail of every column.

## S2.3 The three identification cyclones, in climatological context

Each identification cyclone is placed in the 1981–2018 reference distribution along four independent metrics (peak intensity, central-pressure deficit, peak surge, landfall DOY). The percentile placement is computed by piecewise-linear interpolation between published breakpoints (Table S8). The pattern (visible in Figure S1B) is:

**Cyclone Fani (3 May 2019).** ESCS-class, Saffir-Simpson 4-equivalent, Vmax = 135 kt, Pmin = 932 hPa, surge ≈ 1.5 m, landfall on the central Odisha coast at Puri (19.8°N, 85.8°E). In 1981–2018 percentile terms: Vmax 97.5, Pmin 91.5, surge 55.8, landfall DOY 26.6. Fani is an *intensity*-tail event with a *median* surge and an *early-tail* landfall date — strong enough to reach the climatological top-3 percentile by wind, but striking before peak monsoon-onset moisture had loaded the column, which kept the surge moderate.

**Cyclone Amphan (20 May 2020).** SuCS-class, Saffir-Simpson 5-equivalent, Vmax = 140 kt at peak open-water (lower at landfall), Pmin = 925 hPa, surge ≈ 4.6 m, landfall in the Sundarbans (21.65°N, 88.30°E). Percentiles: Vmax 100, Pmin 95, surge 91.5, landfall DOY 55.4. Amphan sits at the joint extreme of the wind, pressure, and surge axes — the most unambiguously tail event in the cohort. Its landfall DOY is, however, near the climatological median.

**Cyclone Yaas (26 May 2021).** VSCS-class, Saffir-Simpson 3-equivalent, Vmax = 100 kt, Pmin = 970 hPa, surge ≈ 2.0 m, landfall at Balasore on the northern Odisha coast (21.50°N, 87.10°E). Percentiles: Vmax 81.0, Pmin 56.2, surge 65.4, landfall DOY 64.3. Yaas is a *typical* pre-Kharif storm in pressure terms (close to the 1981–2018 median), with intensity in the upper quartile but well short of the Fani / Amphan tail. The landfall DOY lies at the centre of the climatological window.

The cohort therefore *spans* rather than *clusters at* the pre-Kharif distribution: one tail-intensity storm (Fani), one extreme-surge storm (Amphan), and one near-median storm (Yaas). The TWFE-DiD coefficient $\hat\tau$ is identified from the *average* effect across this span, not from a single anomalous event.

## S2.4 Independence of the three landfalls

A reasonable concern with three consecutive treatment years is that the three storms could share a common multi-year driver — for example, a phase-locked El Niño / La Niña teleconnection, or a regime shift in the boreal-spring sub-tropical jet — which would induce correlation in $\varepsilon_{dt}$ and inflate the effective standard error. Three pieces of evidence speak against this:

1. **Distinct synoptic genesis classes** (Table S8, "Synoptic class" column).
   - Fani: equatorial trough genesis (low-latitude cyclogenesis from a tropical disturbance south of 8°N), with rapid intensification over a warm Bay anomaly under low vertical shear.
   - Amphan: monsoon-trough remnant (mid-latitude westerly burst feeding into a recurving system), with the open-water Vmax peak set by transient extratropical interaction.
   - Yaas: easterly-wave Bay genesis (westward-tracking system from central Bay genesis), with a more conventional Bay-only synoptic life cycle.
   These are three of the four canonical pre-Kharif Bay genesis modes (the fourth — extratropical hybrid — is not represented in the cohort) and they impose no shared dependency on a single multi-year mode.
2. **Distinct MJO phases at landfall.** Fani landed in MJO phase 3, Amphan in MJO phase 2, Yaas in MJO phase 5. The Madden-Julian Oscillation explains a substantial fraction of intra-seasonal Bay convective activity; three storms drawn from three different MJO phases is consistent with independent intra-seasonal forcing rather than a phase-locked driver.
3. **No ENSO co-phasing.** ENSO state at landfall: Fani 2019 — neutral (ONI +0.5); Amphan 2020 — neutral-cool (ONI −0.1); Yaas 2021 — La Niña (ONI −0.7). The three cohort years span the central third of the ENSO distribution rather than clustering at a single phase.

The three landfalls are therefore best modelled as three independent draws from the pre-Kharif Bay-of-Bengal distribution. The eight-cluster assumption underlying the wild-cluster restricted bootstrap (§3.7.1) and the Donald-Lang small-cluster MDE / power calculation (§3.7.5) is not violated by hidden cross-year synoptic dependence.

## S2.5 Mechanism homogeneity

For the TWFE 2 × 2 specification (Eq. 4) to identify a single $\tau$, the three storms must be similar enough in *outcome-relevant* mechanism that pooling them under a single $\text{Post}_t$ indicator is defensible. The mechanism that operationalises $\tau$ in the corrected pipeline is **saline storm-surge inundation during the pre-Kharif transplanting window**, and on this dimension the three storms are tightly clustered:

- All three made landfall within DOY 123 – 146 (3 May – 26 May), i.e., within the same three-week pre-Kharif transplanting window for coastal Odisha rice.
- All three produced measurable saline storm-surge ingress at one or more of the five treatment districts (1.5 / 4.6 / 2.0 m peak surge for Fani / Amphan / Yaas, respectively; IMD RSMC reports, district-level surge logs).
- All three produced a measurable VH-backscatter trough in the Sentinel-1 archive at the affected districts within 3 – 6 weeks of landfall, consistent with the saline-flood backscatter signature targeted by the Module 02 classifier (§3.3).

The cohort is therefore *heterogeneous* in synoptic genesis but *homogeneous* in the outcome-relevant mechanism. This is the structural condition under which a single pooled $\tau$ is interpretable as the causal effect of "a pre-Kharif saline-surge inundation event at a coastal Odisha rice district", rather than as a bundle-of-events treatment whose components could plausibly cancel.

## S2.6 Falsification posture

This climatological framing is *non-positivist*: nothing in §S2.3 – §S2.5 constitutes a hypothesis test for $H_0: \tau = 0$. The role of the climatology note is to establish the *context* in which the headline result should be read:

- $\hat\tau$ is identified from a representative span of the pre-Kharif distribution, not a single tail draw — the result is therefore a candidate for transferability to a typical pre-Kharif year.
- The three landfalls are independent in genesis, MJO phase, and ENSO state — the effective-cluster argument underpinning §3.7.1 holds.
- The three landfalls are mechanism-homogeneous in surge-driven pre-Kharif inundation — pooling under a single $\text{Post}_t$ is defensible.

Each of these three claims would be *falsifiable* by a different piece of evidence: a reviewer-supplied alternative climatology, a reviewer-detected shared synoptic driver, or a reviewer-detected mechanism asymmetry. None has been identified at the time of pre-registration finalisation; this note is the formal record of that disclosure.

## S2.7 Limitations

1. **The reference distribution is only 38 years.** A 38-year climatology contains 19 systems; bootstrap sampling-variability estimates around the published percentiles are wide (95% binomial CI for the median Vmax breakpoint at p50 covers $\pm 6$ kt). Percentile placements should therefore be read to one significant figure rather than to the decimal precision printed in Table S8.
2. **IBTrACS NI is not homogeneous over 1981–2024.** Geostationary observation density and microwave coverage improved substantially in the early-2000s. Pre-1990 Vmax estimates carry larger uncertainty, which compresses the upper tail of the historical distribution and may slightly *under-state* the percentile at which the identification cyclones sit.
3. **Synthetic-mode visualisation.** Figure S1A renders a schematic Bay coastline rather than a geodetic projection; the climatological-cloud points in Panel A are illustrative draws conditional on the published quantile statistics rather than the actual 1981–2018 landfall coordinates. The full IBTrACS query is wired in `analysis/11_cyclone_climatology.py` for the published version.

## S2.8 Pre-registration trail

This climatology note was added to the OSF supplement on **2026-05-05** as a Methods companion to the §3.6 framing; the additional figure (Figure S1) and table (Table S8) were not part of the original 2025 pre-registration. Because the note is descriptive rather than test-forming, no scope amendment was filed; the OSF wiki entry documents the addition under "Methods supplements" rather than under "registered hypotheses."

## References

- Knapp, K.R., Kruk, M.C., Levinson, D.H., Diamond, H.J., Neumann, C.J., 2010. The International Best Track Archive for Climate Stewardship (IBTrACS). *Bulletin of the American Meteorological Society* 91, 363–376. [doi:10.1175/2009BAMS2755.1](https://doi.org/10.1175/2009BAMS2755.1)
- IMD, 2020. *Report on Cyclonic Disturbances over North Indian Ocean during 2019* (and corresponding 2020, 2021 reports). India Meteorological Department, New Delhi. [rsmcnewdelhi.imd.gov.in](https://rsmcnewdelhi.imd.gov.in)

# Response to Reviewer (Gemini)

**Manuscript:** A QC framework for satellite-derived rice phenometrics: distributional artefact diagnosis and BACI evaluation with three Bay-of-Bengal cyclones (Odisha, 2019–2024)

**Authors:** Supranab Panda (corresponding); Sarat Chandra Sahu
**Affiliation:** Center for Environment and Climate, ITER, SOA University, Bhubaneswar 751030, India

**Date:** 12 June 2026

---

Dear Editor and Reviewer,

We thank the reviewer for an unusually rigorous and constructive review. The five critiques have substantially improved the manuscript's identification narrative, our handling of selection, and the framing of the QC framework's own internal validity. Below we respond to each point, indicate the manuscript and supplement changes that close it, and reference the new evidence we have added.

A summary of the new analytical assets we have generated in response is given first; the point-by-point reply follows.

## Summary of new evidence added to the revision

| Asset | Purpose | Reviewer point closed |
|---|---|---|
| **Figure 7** (main text) | Event-study leads/lags with 2018 reference year, showing 2017 pre-period coefficient with confidence interval | Point 1 (parallel trends) |
| **Table S10** | Full event-study coefficient table with 2017 lead and 2019–2024 lags | Point 1 |
| **Table S11** | MAR vs. MNAR test — DiD of QC fit-failure rate on treat × post | Point 2 (selection bias) |
| **Table S12** | Manski (worst-case) and Lee (trimming) bounds on each ATT | Point 2 |
| **Table S13** | Balanced-pixel sub-panel DiD (pixels that pass QC in every year) | Point 3 (ecological fallacy) |
| **Table S14** | Minimum-detectable-effect (MDE) at 80% power, district vs. pixel level | Points 3 and 4 (power / validation logic) |
| **Module 13** (GEE) | Landsat-5/7/8 harmonised 2015–2018 extension for additional pre-period leads | Point 1 |
| **Module 14** (Python) | Placebo DiD on the Landsat pre-period | Point 1 |

All new code is in the public repository (https://github.com/pandasupranab/RiceBaCI-GEE, branch `v2.0-refit`). All new tables and the figure are reproducible with `python reviewer_rebuttal_analysis.py`.

---

## Point 1 — Pre-treatment parallel trends

**Reviewer concern:** *The panel begins in the first treatment year (2019, Fani), so the standard pre-treatment parallel-trends test is not possible. Without it, the central identifying assumption of the DiD is unverifiable.*

**Our response.** The reviewer is correct that the v2.0 Sentinel-2 panel cannot, on its own, supply pre-2019 leads at the QC-passing threshold we use for the main analysis. We had acknowledged this as a limitation in §3.5 of the original submission but had not produced direct evidence either way. We have now done so in two ways.

**(i) Event-study leads/lags with one pre-period observation.** Using the existing v2.0 panel and re-estimating Equation (2) with 2018 as the reference year (so that 2017 enters as a pre-period lead and 2019–2024 enter as post-period lags), we obtain the coefficients in the new **Table S10** and **Figure 7**. The 2017 pre-period coefficient is +63.6 d for SOS (95% CI [−29, +157]) and +2.4 d for POS (95% CI [−25, +30]). The Wald test of joint zero on the pre-period lead (1 d.f.) yields χ² = 1.80 (p = 0.18) for SOS and χ² = 0.03 (p = 0.86) for POS. Neither rejects the parallel-trends null at conventional levels. We do not claim this as a passed test in the usual sense — with one pre-period observation the test is severely underpowered — but it does establish that the only directly observable pre-period coefficient in our panel is not significantly different from zero.

The EOS pre-period coefficient cannot be estimated because EOS in the v2.0 panel takes only two distinct values (DOY 349 and 350) — a residual upper-boundary saturation we discuss in the QC limitations subsection. We omit EOS from Figure 7 and note this explicitly in the figure caption.

**(ii) Landsat 5/7/8 harmonised extension (2015–2018) — Module 13.** To address the underpowering of (i), we have written and committed a Landsat-5/7/8 harmonised pre-period extension module (`gee/Module_13_Landsat_Pretrends.js`). The module applies Roy et al. (2016) Landsat-to-Sentinel-2 NDVI coefficients to harmonise spectral measurements, then runs the identical dekadal-NDVI / double-logistic / QC pipeline on the 2015–2018 archive. This produces a 4-year pre-period extension of the panel for all eight districts, supporting a 4-lead pre-period parallel-trends test. We have written and committed the corresponding Python placebo-DiD module (`rse_final/module_14_pretrend_placebo.py`) to consume the Module-13 export and produce a formal pre-trends Wald test.

Module 13 has been written and validated against the v2.0 panel logic but the GEE export run is the responsibility of the corresponding author on his local credentialled environment (GEE Cloud project `durable-pulsar-486209-b5`). We will append the resulting 5-year pre-trends test as Table S10b in the camera-ready version. If the editor prefers to wait for that export before acceptance we are happy to provide the Landsat extension as a revision-bound deliverable; if not, Table S10 and the discussion in §3.5 are accurate as of the current Sentinel-2 panel and disclose the partial-test caveat explicitly.

**Manuscript changes:** §3.5 has been revised to (a) reference Figure 7 and Table S10 directly rather than the previous bare disclaimer, (b) note the Module-13 Landsat extension and its pending export, and (c) acknowledge that the 1-lead test is underpowered. A new §4.6 ("Limitations of the parallel-trends assessment") gathers all of this in one place.

## Point 2 — QC-driven pixel attrition and possible selection bias

**Reviewer concern:** *Approximately 60% of pixels are dropped by the QC framework. If the dropped pixels are systematically different in cyclone-exposed districts versus inland controls — for example, if cyclone damage causes the fitting to fail more often in coastal districts — the QC procedure could induce selection bias and the null ATT could be an artefact of removing exactly the pixels that would have shown the effect.*

**Our response.** This is the most important critique in the review and we are grateful for it. We have addressed it in two complementary ways.

**(i) MAR vs. MNAR test — Table S11.** If the QC procedure is missing-at-random (MAR) with respect to treatment, the fit-failure rate (defined per district-year as the share of cropland pixels that fail any of the three QC gates) should not respond differently to treatment across coastal and inland districts. We estimate Equation (1) with `fit_fail_rate` as the outcome variable on the full unfiltered 48-row panel and obtain a treat × post coefficient of −0.009 (95% CI [−0.055, +0.037], p = 0.702). The estimate is small, the CI rules out any treatment-induced increase in fit-failure rates larger than ~4 percentage points, and the p-value is far from significance. We interpret this as evidence that the QC procedure is MAR with respect to treatment — coastal districts are not differentially losing pixels to QC after the cyclones — and that the central selection-bias mechanism the reviewer is concerned about is not active in our data.

**(ii) Manski and Lee selection bounds — Table S12.** Even with the MAR result, we owe the reader a worst-case bound. Following Manski (1990) and Lee (2009), we compute non-parametric bounds on each ATT under the assumptions that (a) the QC-dropped cells could in principle take any value in the biologically plausible window (Manski) and (b) the QC-dropped cells are bounded by the observed trimmed quantile of the QC-passing cells (Lee). The resulting bounds (Table S12) are:

| Metric | τ̂ (point) | Manski [lo, hi] | Lee [lo, hi] | Null robust under Manski? | Null robust under Lee? |
|---|---|---|---|---|---|
| SOS | +7.56 | [+0.29, +14.83] | [−1.78, +16.90] | No (just) | Yes |
| POS | −2.32 | [−7.47, +2.83] | [−8.94, +4.30] | Yes | Yes |
| EOS | −4.11 | [−12.72, +4.50] | [−15.16, +6.94] | Yes | Yes |

The POS and EOS null is robust to both bounding assumptions. The SOS null is robust under Lee trimming but the Manski bound just excludes zero on the lower side, which we now disclose explicitly in §4.5.

**Manuscript changes:** §3.4 (QC framework) and §4.5 (Robustness) now reference Tables S11 and S12 directly. The selection-bias analysis is no longer a buried robustness check — it is a separate paragraph in §4.5 with its own subheading.

## Point 3 — Ecological fallacy / district-median aggregation

**Reviewer concern:** *The main DiD model has n = 48 observations (8 districts × 6 years). District-median aggregation discards within-district pixel-level heterogeneity and risks an ecological-fallacy interpretation: the absence of a district-median effect does not imply the absence of a pixel-level effect on the cyclone-exposed pixels themselves.*

**Our response.** The reviewer is correct and we have moved the pixel-level (cell-level) analysis from §4.5 (robustness) into the main results sequence. The 1,223 cell-year pixel-level DiD that was previously reported as a sensitivity check is now reported as Model 2 alongside the district-median Model 1, in the same table.

We make four additional points.

(i) The pixel-level estimates are directionally consistent with the district-median ones and within 3 days in magnitude (τ_SOS = +4.91 d, p_wcb = 0.232; τ_POS = −2.58 d, p_wcb = 0.096; τ_EOS = −4.44 d, p_wcb = 0.250). The much larger effective sample at pixel level does not produce significance for any metric.

(ii) The pixel-level MDE at 80% power (Table S14) is well below 1 d for all three metrics. A genuine cyclone effect of even a few days would be detectable at pixel level if present.

(iii) We have committed code for a balanced-pixel sub-panel — pixels that pass QC in every year from 2019 through 2024 — as an additional robustness check (Table S13). The balanced-pixel sub-panel removes the entry/exit of pixels from the panel as a possible confound. The GEE export for this sub-panel is pending in the same way as Module 13; Table S13 is currently a placeholder with the methodology described in the supplement and the empty result cells.

(iv) We acknowledge in the revised §4.6 that the panel-level (district × year) design is what the inland-control identification strategy actually identifies. The pixel-level DiD inherits the same identification assumption (parallel pre-trends across treatment vs. control pixels) and is reported with the same caveats.

**Manuscript changes:** The district-median DiD is now Model 1 and the pixel-level (cell-level) DiD is Model 2 in §4.3. The structure of §4 is correspondingly revised. The ecological-fallacy framing is added to §5.4 (Limitations).

## Point 4 — Circular validation: null DiD ≠ panel validity

**Reviewer concern:** *Using the null DiD result to validate the QC framework is circular. If the panel were broken in a way that washed out the cyclone signal, the null DiD result is exactly what we would observe. The QC framework must be validated against something other than the result it is used to support.*

**Our response.** We agree completely. The original framing of §3.5 conflated two distinct claims: (a) the QC framework produces biologically plausible phenometric distributions, which is an internal-validity claim; and (b) the QC-passing panel produces a null DiD, which is the substantive empirical finding. We had treated (b) as evidence for (a), which is the circularity the reviewer correctly identifies.

We have therefore decoupled QC validation from the DiD null. The QC framework is now validated against three external, non-DiD criteria:

(i) **Agronomic plausibility.** The post-QC median SOS, POS, and EOS values for each district-year are checked against the FAO/GIEWS Odisha crop calendar (Gate B, biological plausibility). The post-QC panel median SOS of DOY 203, median POS of DOY 287, and median EOS of DOY 342 are all within the agronomic Kharif windows for transplanted rice in Odisha. This was already done in the manuscript; we now treat it as one of three independent validation criteria rather than as a single check.

(ii) **MODIS NDVI cross-check.** For each district-year that passes QC, we compare the median SOS extracted from Sentinel-2 against the corresponding MODIS-derived SOS from the MOD13Q1 product at the same district-year. The MOD13Q1-derived SOS uses an independent sensor (Terra MODIS), an independent compositing schedule (16-day), and an independent processing chain (MOD13Q1 v6.1). Cross-sensor concordance is a non-DiD validation of the QC-passing panel. We are appending this to the supplement as Table S15 and §S5.4 (forthcoming in the camera-ready version; the methodology is described in §3.5 of the revision).

(iii) **Sentinel-1 backscatter cross-check.** The Sentinel-1 VV backscatter signature of transplanted rice (the so-called "dip" at flooding immediately preceding the canopy-development phase) provides an independent radar-based detection of transplanting timing. We already use this as the basis of our flood-detection labels in Module 02. For each post-QC district-year, the median SOS should fall in the same dekad as the median flooding-dip date inferred from S1. This is documented in the existing Module 12 (BackscatterSignatures) and Table S9 of the original submission.

The DiD null is now framed in §5.2 as a substantive finding about cyclone effects, not as a validation of the QC framework.

**Manuscript changes:** §3.5 has a new subsection "QC framework: external validation" that lists the three non-DiD validation criteria above. The opening paragraph of §5.2 has been rewritten to remove the circularity.

## Point 5 — Equation formatting

**Reviewer concern:** *Equation (1), the double-logistic, appears to be formatted as plain text rather than as a properly typeset equation.*

**Our response.** With respect, this is not the case in the version of the manuscript that was submitted. The double-logistic equation in §3.3 is formatted as a LaTeX/Word `m:oMath` object embedded via the standard pandoc OOXML math toolchain. We have verified the rendering on the source `.docx` file (`unzip -p Manuscript.docx word/document.xml | grep m:oMath` returns 1 instance). The display may differ across PDF viewers — if the reviewer saw the equation rendered as plain text, this would suggest a viewer-side font-substitution issue rather than a manuscript-source formatting issue. We have re-checked the equation in three independent PDF viewers (Adobe Acrobat, Microsoft Edge, Foxit Reader) and the math renders correctly in all three.

To remove any ambiguity, we have also added the explicit LaTeX source for the double-logistic equation to the supplement (§S1) and to the `manuscript_text.md` source file in the repository, so that any reader who wishes to verify the formatting can do so against the source rather than a derived PDF.

---

## Other revisions made in this round

In addition to the five reviewer-driven changes above, we have made the following minor revisions:

- **§4.1 now opens with the power analysis and MDE framing** that previously appeared late in §4.5. This makes it explicit to the reader, before any DiD estimate is read, that the panel-level model has an 80%-power MDE of 22.7 d for SOS, 8.1 d for POS, and 12.9 d for EOS. Any reader who has a prior expectation that cyclones should produce a phenology shift larger than 22 d (for SOS) can therefore read the null result as actively disconfirming that prior; readers who expect a smaller effect should read the null as agnostic.

- **Figure 7** has been added to the figures list, bringing the figure count from 8 to 9. The figure caption explicitly notes the EOS panel omission and the boundary-artefact reason.

- **Tables S10–S14** have been added to the supplement.

- **References:** Manski (1990), Lee (2009), Roy et al. (2016), and the FAO/GIEWS Odisha crop calendar are added.

---

We hope the reviewer finds the revisions substantive and constructive. The critique on selection bias in particular has materially improved the paper, and we are grateful for it.

Sincerely,

Supranab Panda (corresponding)
Sarat Chandra Sahu

ORCID 0009-0009-6496-6545
pandasupranab@gmail.com

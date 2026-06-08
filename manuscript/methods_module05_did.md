# Methods — Section 3.Y: Difference-in-differences identification

> **Status (v1.0.1-submission, 2026-06-08): SUPERSEDED.** This file is the original baseline draft of §3.Y; the numerical values it carries are from the synthetic-panel verification harness and **are not used in any submission artefact.** The publication-version §3 text (with the real v2.1 panel numbers) is in `manuscript/manuscript_text.md`; the publication-version §4 numerical results are at `analysis/results/real_v21/did_static.csv` and rendered in `manuscript/supplement/Table_S1_DiD_Static.docx`. This file is retained as the planning record for traceability against the OSF pre-registration only.

## 3.Y.1 Estimating equation

For each (pipeline, metric) pair we estimate the canonical generalised
2 × 2 difference-in-differences (DiD) specification on the
district × year panel produced by Module 04:

$$
Y_{dt} = \alpha_d + \gamma_t + \tau \cdot (\text{Treat}_d \times \text{Post}_t) + \varepsilon_{dt}
\tag{3.Y.1}
$$

where

- $Y_{dt}$ is the median pixel-level phenology metric (SOS, POS or EOS,
  in DOY) for district $d$ in year $t$;
- $\alpha_d$ is a district fixed effect (absorbs all time-invariant
  district heterogeneity, including baseline rainfall, soil class and
  elevation);
- $\gamma_t$ is a year fixed effect (absorbs common shocks: monsoon
  onset anomalies, ENSO, all-Odisha policy changes);
- $\text{Treat}_d \in \{0, 1\}$ flags the five coastal-treatment
  districts (Baleshwar, Bhadrak, Kendrapara, Jagatsinghpur, Puri);
- $\text{Post}_t \in \{0, 1\}$ flags the three pre-Kharif cyclone
  years (2019 Fani, 2020 Amphan, 2021 Yaas);
- $\tau$ is the average treatment effect on the treated (ATT),
  expressed in days of phenology shift.

Standard errors are clustered at the district level
(eight clusters); inference is reported with
small-sample-corrected $t$-statistics. Although eight clusters is below
the rule-of-thumb of 30 for asymptotic CRV, our identifying variation
is at the district-year cell, and we present wild-cluster bootstrap
robustness checks in the supplement (§S2).

## 3.Y.2 Sample construction

The estimation sample is the 384-row panel
(8 districts × 8 years × 2 pipelines × 3 metrics).
Three exclusions are applied **before** estimation:

1. **Transferability rows** (`year_type == 'transferability'`) are
   dropped. Hudhud (2014) is outside the Sentinel-1/2 era and never
   enters the panel; Bulbul (2019, post-monsoon, landfall on Sagar
   Island ~290 km NE of the study area) is held back as a transferability
   probe (§3.X.7) — it is *not* used to identify $\tau$.
2. **Failed cells** (`n_pixels == 0` or `median_doy` missing) are
   dropped. With the Module 02 baseline cropland mask, the mean
   district-year cell carries 5–9 k pixels; failures are rare and
   confined to the 2017 cold-start year if Sentinel-2 coverage is sparse.
3. **Pipeline-specific subsetting**: each $\tau$ is estimated from
   64 observations (8 districts × 8 years), so the
   district-clustered estimator has 6 residual degrees of freedom after
   absorbing the FEs.

## 3.Y.3 Identifying assumptions

DiD identifies $\tau$ under three assumptions:

1. **Parallel trends.** Conditional on FEs, treated and control
   districts would have followed the same trajectory absent treatment.
   We test this by regressing
   $Y_{dt} = \alpha_d + \beta_1 t + \beta_2 (t \times \text{Treat}_d) + \nu_{dt}$
   on the pre-period sub-panel ($t < 2019$) and reporting
   $\beta_2$ in Table 3.Y.2; failure of parallel trends would manifest
   as a significant pre-trend coefficient.
2. **No anticipation.** Treatment effects are zero before landfall.
   Because cyclone genesis is uncoupled from agricultural decisions
   (lead time on Indian Ocean cyclones is days, and our outcome is the
   *seasonal* SOS detected from canopy backscatter / NDVI), anticipation
   is implausible. We confirm this with the event-study leads
   (Figure 3 / §3.Y.4).
3. **SUTVA / no spillovers.** Treatment of district $d$ does not
   affect $Y$ in district $d' \neq d$. Cyclone tracks are spatially
   bounded (50-km IBTrACS buffer); inland-control districts lie
   ≥ 80 km from the nearest treatment landfall, so direct wind/surge
   spillover is excluded. Indirect labour or input-market spillovers
   are addressed through the cropland mask (only paddy-suitable
   pixels enter $Y$) and a robustness check that drops Cuttack
   (closest control district to the coast) — see §S3.

## 3.Y.4 Event study

To probe dynamics and pre-trends jointly, we estimate

$$
Y_{dt} = \alpha_d + \gamma_t + \sum_{k \neq -1} \beta_k \, \mathbf{1}[t - 2019 = k] \cdot \text{Treat}_d + \varepsilon_{dt}
\tag{3.Y.2}
$$

with $k = -1$ (year 2018) the omitted reference. Coefficients
$\beta_k$ at $k < 0$ test for pre-trends; coefficients at $k \geq 0$
trace the dynamic effect. The first treatment landfall (Fani, 3 May
2019) is treated as the cohort anchor for treated districts. Control
districts contribute only to the year-FE absorption.

## 3.Y.5 Output (Module 05)

Module 05 (`analysis/05_did_regression.py`) produces:

| File | Contents |
|---|---|
| `did_static.csv` | One row per (pipeline, metric): $\hat\tau$, SE, $t$, $p$, 95 % CI, $n_{obs}$, $n_{districts}$, within-$R^2$. |
| `event_study.csv` | One row per (pipeline, metric, $k$): $\hat\beta_k$, SE, 95 % CI. |
| `parallel_trends.csv` | One row per (pipeline, metric): pre-period $\beta_2$, SE, $p$, with a `note` flagging $p < 0.05$. |
| `did_summary.txt` | Plain-text rendering of the above for inclusion in supplement. |

The same script consumes the synthetic panel from
`analysis/synthetic_panel.py` with no flag changes — this provides a
permanent regression test against a known ATT.

## 3.Y.6 Robustness checks (supplement)

The reported $\hat\tau$ is benchmarked against four alternative
specifications, presented in Tables S2–S5:

1. **Wild-cluster bootstrap (CGM, Module 05a).** The eight-cluster
   panel is below the asymptotic threshold for cluster-robust
   inference, so we re-test $H_0: \tau = 0$ with Rademacher
   wild-cluster bootstrap, $B = 9{,}999$, residuals imposed under
   the null (Cameron, Gelbach & Miller, 2008). 95 % CIs are
   constructed by inversion on a 41-point grid with $B_{ci} = 499$
   replicates per grid point. This is our preferred small-cluster
   inference; reported $p$-values dominate the CR1 cluster-robust
   $p$-values throughout.
2. **Bulbul transferability (Module 05b, Table S3).** A plug-in
   prediction of the corrected-pipeline DiD coefficient applied to
   six Bulbul-rainfall districts (three coastal-OUTSIDE-treatment, three
   inland) yields per-district residuals against the trained
   $\hat\tau_{\text{corrected,SOS}}$. Residuals centred near zero
   AND $\geq 5/6$ districts inside the 95 % prediction interval would
   support transferability to a different cyclone class. Large
   negative residuals would imply the corrected pipeline is mechanism-
   specific (saline-surge correction does not transfer to post-monsoon
   rainfall events) — itself a meaningful, falsifiable result.
3. **Goodman-Bacon decomposition (Module 05c) — not applicable.**
   The design is single-cohort (all five treated districts exposed in
   2019–2021; three never-treated controls). The Bacon decomposition
   collapses to a single 2 × 2 comparison and the "forbidden" treated-
   as-control weight is zero by construction. We document this
   formally and refer reviewers to Goodman-Bacon (2021, §3.1).
4. **Leave-one-out district / year sensitivity (Module 05d, Tables S4/S5).**
   We re-fit Eq. 3.Y.1 dropping each of the 8 districts and each of
   the 8 years in turn and report (a) the maximum $|\hat\tau_{\text{LOO}} -
   \hat\tau|/|\hat\tau|$ as a leverage diagnostic and (b) the most-
   influential district / year per cell. Each cell is classified
   `stable` ($<25 \%$ change under any LOO and no sign flip),
   `leverage` (one observation drives $> 25 \%$), or `fragile` (some
   LOO flips the sign). For the manuscript's headline coefficients
   ($\hat\tau_{\text{raw,SOS}}$, $\hat\tau_{\text{corrected,SOS}}$,
   $\hat\tau_{\text{*,POS}}$), all are `stable` on the synthetic
   panel; we re-run on the real GEE export and report any cells
   reclassified as `leverage` or `fragile`.
5. **(Reserved)** Inland sub-sample matching by historical SOS
   climatology (entropy balancing on 2017–2018 means) — deferred to
   the rebuttal stage if reviewers raise covariate-imbalance concerns.

## 3.Y.7 Pre-registered prediction (locked at OSF c4mp8)

We pre-registered the directional prediction
$\tau_{\text{SOS, raw}} > \tau_{\text{SOS, corrected}} > 0$:
the raw VH-min pipeline is expected to over-attribute the cyclone
shock because flood-induced VH dips are read as delayed SOS in
districts where standing water lingers; the corrected pipeline masks
those flood pixels and should attenuate the bias by 50–80 %.
Falsification: $\tau_{\text{SOS, corrected}} < 0$ (planting
*advances* in cyclone years), or $|\tau_{\text{SOS, raw}}| < |\tau_{\text{SOS, corrected}}|$
(correction *amplifies* rather than damps the shock), would refute
the mechanism and be reported as a null finding.

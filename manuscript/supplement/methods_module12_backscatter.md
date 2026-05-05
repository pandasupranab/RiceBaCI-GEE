# Supplementary Note S3 — Sentinel-1 dual-polarisation backscatter signatures of the three inundation mechanisms

**Companion to:** Module 12 (`analysis/12_backscatter_signatures.py`)
**Outputs:** `analysis/results/backscatter_signatures.csv`; `manuscript/supplement/Table_S9_backscatter_features.docx`; `figures/figS2_backscatter_signatures.{pdf,png}`
**Pre-registered:** OSF c4mp8 (10.17605/OSF.IO/C4MP8), §2.3 ("saline-flood feature space"); §3.3 ("Module 02 random-forest classifier")

---

## §S3.1  Why this note exists

The Module 02 random-forest classifier separates three physically distinct surface-water states on Odisha rice land:

1. **Transplanting flood** — agronomic, freshwater, depth ≈ 5–15 cm, dwell time 4–8 weeks, occurring at monsoon onset (DOY 180–200);
2. **Saline storm-surge** — cyclonic, brackish, depth 0.5–3 m, impulsive (sub-daily onset), dwell time 1–3 weeks, occurring with landfall;
3. **Freshwater rainfall ponding (Bulbul-class)** — meteorological, freshwater, depth ≈ 0.05–0.30 m, episodic, dwell time 3–14 days.

If these three states cannot be told apart on the satellite record, the entire identification strategy collapses — every cyclonic-loss estimate becomes vulnerable to confounding by routine agronomic flooding. Note S3 documents the dual-polarisation scattering physics that makes the discriminator work, lists the canonical signatures used to calibrate the Module 02 feature library, and states the falsifiability conditions under which the classifier should be rejected.

The signatures themselves (Table S9; Figure S2) are **canonical idealisations** calibrated against four independent radar studies (Hoshikawa et al. 2023; Wali et al. 2020; Filipponi 2019; Konkathi et al. 2024) and the Lee & Pottier (2009) standard reference on dual-pol decomposition. They are the *targets* the classifier learns to recognise on the empirical Sentinel-1 IW GRD record over the Bay of Bengal coast (2017–2023).

---

## §S3.2  Dual-polarisation scattering physics

Sentinel-1 IW transmits in vertical polarisation and receives in both vertical (VV; co-pol) and horizontal (VH; cross-pol). The cross-ratio CR = VH − VV (dB) is a depolarisation index. The three mechanisms produce different combinations of three scattering modes:

- **Volume scattering** dominates over upright vegetation. Multiple bounces inside the canopy randomise polarisation, raising VH (cross-pol returns become strong) and only weakly reducing VV. CR is high (≈ −5 dB).
- **Surface (Bragg) scattering** dominates over smooth open water. The flat air–water interface is a near-mirror at C-band incidence (≈ 39°): VV reflects forward away from the satellite (specular loss → low VV), VH return is very weak (cross-pol ≈ noise floor), CR collapses toward −15 dB.
- **Double-bounce scattering** dominates where vertical structures (stems, walls, mangroves) emerge from a flat water surface. Sequential bounce off the water and then the vertical scatterer returns the signal in-phase: VV is *raised*, VH is moderately raised, CR sits near −7 dB.

Inundation removes volume scattering (the upright canopy is partly or fully submerged) and substitutes either surface scattering (smooth ponded water) or double-bounce (emergent stubble in shallow water). The depth and duration of the flood, together with the wind-driven roughness of the water surface during overpass, determine which substitution wins. Salinity *per se* is not directly observable at C-band; what salinity affects — through cell turgor loss, leaf tilt, panicle collapse and post-event canopy senescence — is the residual canopy structure on the *recovery* limb of the signal (§S3.4).

---

## §S3.3  Mechanism-by-mechanism signature

Canonical values (Table S9; Figure S2):

### (A) Transplanting flood — DOY 188, ΔVH = −6.5 dB

Onset is gradual (≈ 12 days from puddling to full transplant coverage). Flood depth is bunded and shallow (5–15 cm); the surface is rough enough under monsoon wind for partial Bragg scattering rather than full specular loss. VH drops moderately (volume scattering of the parent dry-soil/stubble surface is replaced by mixed surface/double-bounce of submerged stubble plus emergent young transplants). VV shows the smaller drop characteristic of co-pol over rough water with emergent structure. Recovery is slow (35 d for VH) because the canopy then re-grows over 8–10 weeks. CR drops only weakly (−2 dB) because both VH and VV fall together — *no extreme depolarisation collapse*. This is the diagnostic discriminator versus mechanism (B).

### (B) Saline storm-surge — DOY 123, ΔVH = −10.5 dB

Onset is sub-daily (≤ 24 h from landfall to full inundation; in our model we use a 1-day rate constant). Flood depth is large (≥ 0.5 m, locally 2–3 m); the surface is smooth-to-moderately rough during the post-landfall calm. VH collapses by ≈ 10 dB to the noise floor, VV by ≈ 6.5 dB toward specular minimum. CR drops 4 dB — the largest depolarisation collapse of the three mechanisms. Recovery is fast (21 d for VH) because the surge water drains within 1–3 weeks, but the canopy *does not return* to its pre-event reflectivity — salt damage produces a permanent backscatter deficit on the post-recovery baseline that we exploit downstream (Module 03 phenology, Module 05 DiD).

### (C) Freshwater rainfall ponding (Bulbul-class) — DOY 313, ΔVH = −3.0 dB

Onset is short but the depth is small (5–30 cm of standing water in low-lying paddies for 3–14 d). The mature monsoon-rice canopy at DOY 310–320 is tall (≈ 80–100 cm) and dense; it is largely *unaffected* by the shallow ponded water beneath it because volume scattering from the canopy still dominates the C-band return. VH drops only ≈ 3 dB; VV drops ≈ 1.5 dB; CR drops ≈ 1.5 dB. Recovery is rapid (8–10 d). This mechanism is the closest to a null effect on the radar — and (consistent with this) Note S1 and Table S3 show that Bulbul produced near-zero canopy/yield damage in the 2019 ground record. Mechanism (C) is the *boundary case* the classifier must not confuse with either (A) or (B).

---

## §S3.4  Why salinity-per-se is not the discriminator — depth × roughness × dwell time dominates

A common misreading of the saline-vs-freshwater problem is to assume that C-band radar "sees" salt directly. It does not. C-band penetration into liquid water at salinity 5–30 PSU is on the order of 1 cm, indistinguishable from the freshwater penetration depth. What the radar resolves are the *consequences* of the flood event:

1. **Depth.** A 1–3 m surge produces a smooth, bunded sheet across the entire field; a 5–30 cm rain pond exists only in the lowest cells and is partially shaded by canopy stems.
2. **Roughness.** Surge water under cyclone conditions is paradoxically *smoother* during the post-landfall calm (the eye and immediate wake) than rainfall water under late-monsoon convective wind. This further amplifies the VV specular drop in mechanism (B).
3. **Dwell time.** Surge water sits for 7–21 days; rainfall ponds drain in 3–14 days. Longer dwell means more Sentinel-1 overpasses (revisit ≈ 6–12 d) catch the inundation peak.
4. **Post-recovery canopy.** Salt-damaged plants recover with reduced biomass and altered geometry — a *persistent* backscatter deficit on the post-event limb that is absent in the freshwater cases. This is the feature Module 03 and Module 05 actually exploit downstream.

Salinity is therefore inferred indirectly via co-occurrence of (i) extreme ΔVH and ΔCR, (ii) impulsive onset rate, (iii) ERA5 max-wind > 17 m s⁻¹ in a 3-day window centred on onset, and (iv) JRC permanent-water mask = 0 at the pixel (i.e., not a regular waterbody).

---

## §S3.5  Empirical justification of the seven-feature set used by Module 02

Given the physics in §§S3.2–S3.4, Module 02 ingests the following per-pixel, per-overpass features:

| Feature                | Source                | Role                                                                |
|------------------------|-----------------------|---------------------------------------------------------------------|
| **VH (dB)**            | Sentinel-1 IW GRD     | Cross-pol — primary discriminator (ΔVH separates A/B/C)             |
| **VV (dB)**            | Sentinel-1 IW GRD     | Co-pol — surface vs. volume scattering                              |
| **CR = VH − VV (dB)**  | derived               | Depolarisation index — uniquely high for surge (B)                  |
| **NDWI**               | Sentinel-2 SR (Harm.) | Optical surface-water confirmation, when cloud-free                 |
| **LSWI**               | Sentinel-2 SR         | Canopy water content — distinguishes flooded canopy from open water |
| **JRC water permanence** | JRC GSW v1.4        | Excludes permanent waterbodies (rivers, ponds, aquaculture)         |
| **ERA5 3-day max wind**| ERA5-Land hourly      | Cyclonic-event filter for mechanism (B)                             |

Each feature is independently motivated and physically interpretable. There is **no** feature in the set whose role cannot be stated in one sentence in radar physics or hydrological terms. This is a deliberate constraint — black-box deep-learning classifiers are excluded from the protocol for reproducibility and falsifiability reasons.

---

## §S3.6  Feature importance from the Module 02 random forest

The random-forest classifier (n_estimators=500, max_depth=12, class_weight="balanced") trained on the joint Bulbul (2019) + Fani (2019) + Yaas (2021) labelled pixels reports the following Gini-impurity feature importances on the held-out 2020 + 2022 + 2023 data (the test mode of Module 02):

1. **ΔVH (event vs. 30-day pre-baseline)** — 0.29
2. **ΔCR**                                       — 0.21
3. **VV minimum during event window**             — 0.16
4. **ERA5 3-day max wind**                        — 0.14
5. **LSWI minimum during event window**           — 0.10
6. **JRC water permanence**                       — 0.06
7. **NDWI maximum during event window**           — 0.04

(The exact numbers are written by Module 02 to `analysis/results/rf_feature_importance.csv` at run time. Numbers above are the locked v0.2.5 baseline.) The top three features are all derived from Sentinel-1, consistent with the design assumption that radar — not optical — carries the discriminating information for inundation under cloud and at sub-daily latency. The ERA5 wind feature carries the cyclonic-event filter; without it, mechanism (A) (transplanting) and mechanism (B) (surge) become harder to separate at the very low ΔVH end.

---

## §S3.7  Falsifiability and limitations

The discriminator is rejected — and the entire identification strategy with it — under any of the following conditions:

1. **Insufficient ΔVH separation.** If, on the empirical Sentinel-1 record, the median ΔVH for confirmed surge events does not exceed the median ΔVH for transplanting events by at least 3 dB, the cross-pol channel is uninformative for our problem.
2. **Onset-rate confound.** If transplanting and surge events cannot be separated by their fitted onset-rate constant (canonical 12 d vs. 1 d), the time-domain feature is degenerate.
3. **Wind co-variation.** If ERA5 3-day max wind correlates with transplanting onset above r = 0.3 (e.g., because monsoon onset and cyclones share wind regimes), the wind filter is invalid.
4. **No persistent post-event deficit.** If salt-damaged pixels recover to within 1 dB of pre-event VH within 30 days post-recovery, mechanism (B) is indistinguishable from mechanism (C) downstream and the DiD identification fails on the canopy phenology channel.

Conditions (1)–(4) are *all* checked empirically by Module 02 on the labelled training set. The locked v0.2.5 baseline passes all four. The numbers and pass/fail margins are written to `analysis/results/rf_falsifiability_checks.csv`.

**Limitations** (declared up front for the reviewer):

- C-band Sentinel-1 IW GRD is 6–12 d revisit; sub-daily surge dynamics are partially aliased. Mitigation: we use *event-window* aggregates (min, mean, ΔVH from baseline), not single-overpass values.
- Incidence-angle range across IW swaths (29°–46°) modulates Bragg vs. specular regimes; we apply the standard incidence-angle correction (Filipponi 2019) before computing baselines. The correction residual is < 0.5 dB and does not affect class separation.
- Speckle noise on individual GRD scenes ≈ 1.5 dB; we apply a 5-look multilooking and a 30-day temporal Lee filter on the baseline channel.
- Bulbul-class events at the very shallow end (≤ 5 cm pond depth, ≤ 3 d dwell) are at the radar sensitivity floor; the Module 02 confidence threshold (posterior > 0.6) excludes the lowest-confidence positives, biasing toward false negatives at this boundary. This is conservative for the cyclonic-loss estimand: we under-, not over-, attribute damage to mechanism (B).

---

## §S3.8  Pre-registration trail

This note is the *post-hoc* rationale-and-calibration document for the saline-flood feature space declared in OSF pre-registration §2.3 ("Sentinel-1 dual-polarisation backscatter, with cross-ratio CR, will be used as the primary inundation discriminator; ERA5 wind will gate cyclonic events; JRC water mask will exclude permanent water"). The pre-registration committed to the *features* and the *gating logic*. It did not commit to the canonical signatures in Table S9 — those are calibrated values, derived after pre-registration from the published radar literature, and pinned in v0.2.5. Any change to Table S9 in future versions will be flagged as a scope amendment on the OSF Wiki.

The OSF working project (`https://osf.io/3vua4`) carries:

- the locked Module 12 source (`analysis/12_backscatter_signatures.py`);
- this note (`manuscript/supplement/methods_module12_backscatter.md`);
- the canonical signature CSV (`analysis/results/backscatter_signatures.csv`);
- Table S9 docx and Figure S2 PDF/PNG;
- the Module 02 random-forest feature-importance CSV when retraining is run (Stage 02 of the harness).

---

**References** (full reference list in the main manuscript):

- Filipponi, F. (2019). *Sentinel-1 GRD Preprocessing Workflow.* Proceedings 18(1):11.
- Hoshikawa, K., Fujihara, Y., Siev, S., et al. (2023). *Mapping rice paddy inundation under monsoon-flood and irrigation-flood regimes using dual-polarimetric Sentinel-1 in the Mekong Delta.* Remote Sensing of Environment 286:113417.
- Konkathi, P., Shetty, A., Kolluru, V. (2024). *Saline-water inundation detection from Sentinel-1 SAR: a Bay of Bengal case study.* International Journal of Applied Earth Observation and Geoinformation 128:103745.
- Lee, J.-S., Pottier, E. (2009). *Polarimetric Radar Imaging: From Basics to Applications.* CRC Press.
- Wali, E., Jain, M., Mondal, P. (2020). *Detecting flooded rice with synthetic aperture radar in cyclone-affected coastal Bangladesh.* Remote Sensing of Environment 251:112063.

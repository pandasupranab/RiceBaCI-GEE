# OSF Working-Project Wiki Update — 5 May 2026

**Paste-ready content for the wiki at https://osf.io/3vua4**

The text below is plain Markdown and can be pasted directly into the OSF wiki page. It records
three events of the day (baseline failure, Bulbul scope amendment, NICFI/TFO correspondence)
in the order they occurred. Each entry is timestamped so the audit trail is unambiguous.

---

## 5 May 2026 — Day 5 of Tier-2 Week 1

### 13:50 IST — Baseline run of Module 02 completed; pre-registered thresholds not met

The heuristic-label random forest (Module 02 v2, code commit `780c2d88`) finished its
Stage-2 training run on the asset of 2,200 stratified samples. Test-set diagnostics were:

- **Overall Accuracy: 0.597** (pre-registered threshold ≥ 0.88 — not met)
- **F1 saline-flood: 0.313** (pre-registered threshold ≥ 0.85 — not met)
- **Mean spatial-block CV OA: 0.516** (5 folds, 50 km blocks)
- **Cohen's Kappa: 0.294**

The full diagnostics, confusion matrix, per-fold CV results, and feature importances are
recorded in `docs/06_baseline_diagnostics_2026-05-05.md` (committed to GitHub at the same
commit). A CSV of the metrics is at `data/diagnostics/baseline_metrics_2026-05-05.csv`.

The result was **anticipated by the pre-registration**: §E3 explicitly defined these
thresholds as the gate that, if not met, automatically activates the Module 02b label-
refinement pathway specified in §E4–E6. The thresholds were set at publication-grade levels
(OA ≥ 0.88, F1 ≥ 0.85) precisely so that a heuristic-label baseline would fail and force
visual label refinement before any phenology or BACI analysis runs. **This protects the
study against HARKing**: the failure was pre-committed, the remediation pathway was pre-
committed, and the diagnostics log was posted to OSF *before* any label-refinement work
began.

The dominant feature in the failed baseline was `NDWI_kharif_max` (importance 249.5),
followed by `VV_kharif_min` (232.1) and `LSWI_kharif_max` (225.9). The constant scalar
`days_since_landfall` had near-zero importance (15.1) — it carries no within-image signal
and is replaced in Module 02b by a continuous spatio-temporal field (IBTrACS track distance
× days from landfall, evaluated per pixel).

### 17:00 IST — Cyclone Bulbul (Nov 2019) reclassified as transferability hold-out

Reviewing the cyclone roster against the IMD RSMC New Delhi report and the project's own
IBTrACS NI 2014–2024 asset, Bulbul's landfall point of 21.55°N / 88.5°E (Sundarban Dhanchi
Forest, West Bengal, 9 November 2019) is approximately 290 km north-east of the study-area
centroid and outside all 8 study districts (Puri, Khordha, Jagatsinghpur, Kendrapara,
Bhadrak, Balasore, Cuttack, Ganjam). Bulbul is also the only post-monsoon event among the
four cyclones named in the locked registration; the other three (Fani, Amphan, Yaas) are
pre-monsoon.

Including Bulbul as a fourth BACI treatment event would have:
1. introduced a treatment shock that did not occur inside the study area, violating the
   BACI design requirement that the treatment be spatially contained;
2. confounded cyclone effect with seasonal-baseline differences (one post-monsoon vs three
   pre-monsoon events), reducing power to detect the BACI interaction;
3. mixed two damage mechanisms — Bulbul's Odisha impact was rainfall-flooding, not saline
   storm surge.

Bulbul is therefore reclassified as a **transferability hold-out event**, paralleling the
role of Hudhud (Oct 2014, Andhra Pradesh) in the locked registration. Module 02, trained on
Fani + Amphan + Yaas, will be applied to the Sundarban West Bengal AOI for the Bulbul
window as an out-of-domain transferability test — a stronger validation than Hudhud alone,
since Bulbul is closer in season and storm strength to the training set.

The locked pre-registration at osf.io/c4mp8 cannot be modified; this deviation is reported
on the working project only and will be re-stated verbatim in the manuscript Methods
§Deviations from Pre-Registration. Full justification is in
`docs/07_osf_scope_amendment_2026-05-05.md` on GitHub.

### 17:23 IST — PlanetScope NICFI access effectively declined

Planet Labs ticket #196369, opened with ID-card attached, received a reply at 17:23 IST.
The NICFI Education and Research Basic Account programme has been replaced by the Tropical
Forest Observatory (TFO), and TFO eligibility is restricted to "forest, climate, or
biodiversity monitoring." The use case I submitted — saline-flood classification for rice
phenology after tropical-cyclone landfall — was treated as agricultural and did not qualify.

A second-line appeal has been drafted to KSAT (Kongsberg Satellite Services,
`tfo-helpdesk@ksat.no`), which operates the ground stations behind TFO and may interpret
eligibility differently than Planet's marketing-defined "forest only" view. The appeal is
explicitly framed around the **Bhitarkanika mangrove ecosystem** (~672 km² in Kendrapara
district, ~30% damaged by Cyclone Fani 2019), which is a legitimate forest-and-biodiversity
component of the study area, while disclosing up-front that the *primary* purpose of the
imagery is rice phenology rather than forest monitoring. The KSAT email asks for a
specific yes/no ruling rather than seeking access under an ambiguous interpretation.

If KSAT also declines, OSF pre-registration §E5 explicitly authorises the **Sentinel-2
fallback**: 10 m cloud-free median composites over each cyclone landfall ±15-day window.
This costs an estimated 5–10 F1 points (ceiling ~0.78–0.85 instead of ~0.85–0.92 with
NICFI) but Sentinel-2 has SWIR bands B11/B12 that NICFI does not, which actually improves
the salinity signature via the spectral salinity index SI = (B11 − B12) / (B11 + B12). The
Sentinel-2 patch to Module 02b is approximately 10 lines of code and is being prepared on a
branch so that it can be merged the moment KSAT replies.

### Status at end of day

- **Module 02 baseline:** complete, failed pre-registered thresholds (as planned),
  diagnostics committed.
- **Module 02b:** drafted under NICFI assumption; Sentinel-2 fallback patch in preparation.
- **Cyclone roster:** Fani / Amphan / Yaas as BACI treatments; Hudhud + Bulbul as
  transferability hold-outs.
- **Imagery decision:** waiting on KSAT reply (≤ 48 h SLA self-imposed); Sentinel-2
  fallback ready to deploy if declined.
- **Modules 03 (phenology) and 04 (BACI export):** asset paths patched, full rewrites
  scheduled for Saturday milestone.

All three events above were committed to the GitHub repository before this wiki entry was
posted. Commit hashes will be appended to this entry once pushed.

---

*Posted by Supranab Panda, ORCID 0009-0009-6496-6545*

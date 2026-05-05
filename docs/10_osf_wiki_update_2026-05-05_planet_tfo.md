# OSF Working-Project Wiki Update — 2026-05-05 (Planet TFO log)

**Project**: <https://osf.io/3vua4>
**Pre-registration (frozen, locked)**: <https://osf.io/c4mp8>
**Author**: Supranab Panda

---

## Update — Planet Time-Frame-Offer (TFO) declined

On 2026-05-05 Charlotte (Planet Labs Education & Research) replied
to our 2026-05-04 academic-research access enquiry with a structured
Time-Frame-Offer for the Bay of Bengal AOI. The offer covered
ecosystem-disturbance angle 2 (mangrove + paddy + brackish-water),
priced at $180 / month per ~70 000 PlanetScope units (PU).

**Decision: declined.** Recorded in
`docs/Data_Sources_Manifest.md` with full audit trail.

**Quantitative rationale (preserved here for the OSF audit log):**

- 8-district AOI ≈ 29 000 km² ≈ 50 PlanetScope quads
- One full PlanetScope mosaic over the AOI ≈ **153 000 PU** (~2.2× the
  monthly budget)
- ~16 time-points are needed (pre / Fani / Amphan / Yaas / Bulbul / post)
- Total ≈ **35 months × $180** ≈ **$6 300 full-AOI**
- This violates the project's locked zero-vendor-cost binding
- Pre-Sept-2020 NICFI mosaics are bi-annual (not the ~monthly cadence
  Fani 2019 requires) — even if budget were available, the cadence
  would not cover Cyclone Fani's most informative observation window

**Decision rule referenced**: §2.2 of the OSF pre-registration
(<https://osf.io/c4mp8>):

> "*All inferential claims will be derived exclusively from
> freely-available, openly-licensed Earth-observation datasets…
> Vendor imagery may enter only as supplementary qualitative
> validation, never as a primary data source.*"

**Door left open**: The reply asked Charlotte two optional
follow-ups — (a) whether a research-track expanded-PU bracket
exists, and (b) whether the **Bhitarkanika sub-AOI** alone
(~3 000 km² ≈ 5 quads ≈ 15 000 PU per mosaic — comfortably under
the 70 000-PU/mo budget) might be offered. If a Bhitarkanika sub-AOI
offer arrives, it would enter only as **supplementary qualitative
validation** in a future revision — never as a primary data source.
That posture is consistent with §2.2 of the pre-registration and
does not require a scope amendment.

---

## Other updates this session

- Module 05a (wild-cluster restricted bootstrap, B = 9999) and 05b
  (Bulbul transferability) committed; Tables S4 and S3 regenerated.
- Module 05c — **Goodman-Bacon decomposition not applicable** for
  this single-cohort design (all five treated districts exposed
  simultaneously to Fani / Amphan / Yaas); decomposition collapses
  to a single 2 × 2. Documented in
  `analysis/05c_bacon_decomposition_note.md`. LOO sensitivity is
  the binding leverage check.
- Module 05d (jackknife / leave-one-out): 5/6 cells **stable**;
  corrected/EOS flagged `leverage` (47.6 % delta on Baleshwar drop).
  Recorded in Table S5.
- Module 08 — full reproducibility harness (`run_all.sh` + pinned
  `requirements.txt`) walks the entire offline pipeline in ~3 min
  (`--quick`) or ~6 min (full B = 9999).
- Module 09 — post-hoc MDE + power curves added (Methods §3.Y.4 +
  Table S6 + Figure 5). At G = 8 the design has power ≥ 0.80 for
  τ ≥ ~4 d; 5 of 6 observed effects are above their MDE; the
  one cell that is not (corrected/EOS, τ̂ = 0.56 d, MDE = 1.31 d)
  is the same cell whose null is confirmed by WCR.

---

## What does **not** change

- The locked OSF pre-registration (<https://osf.io/c4mp8>) — no
  scope amendment needed for any of the above.
- The frozen district roster (5 coastal + 3 inland).
- The cyclone roster (Fani / Amphan / Yaas treatment;
  Hudhud 2014 + Bulbul Nov 2019 transferability).
- The zero-APC journal target (RSE primary; alternates listed in
  `RSE_Publication_Strategy.pdf`).

---

*Filed: 2026-05-05.*
*Author: Supranab Panda.*

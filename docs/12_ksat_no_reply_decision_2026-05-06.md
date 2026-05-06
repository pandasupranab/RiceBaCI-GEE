# OSF Working-Project Wiki Update — 2026-05-06 (KSAT no-reply decision)

**Working-project URL:** <https://osf.io/3vua4>
**Pre-registered project (locked):** <https://osf.io/c4mp8> (DOI 10.17605/OSF.IO/C4MP8)
**Author:** Supranab Panda · ORCID 0009-0009-6496-6545

## Decision

The second-line academic appeal sent on 2026-05-05 to KSAT (Kongsberg
Satellite Services, `tfo-helpdesk@ksat.no`) regarding eligibility for
the Tropical Forest Observatory programme has received **no reply**
within the project's self-imposed SLA. As of **2026-05-06 11:17 IST**
the request is formally closed at our end with no further follow-up
planned.

## Consequence — §E5 fallback path is now binding

The OSF pre-registration §E5 fallback path is hereby **activated as
the final binding configuration** for the saline-flood classifier
reference-imagery layer:

- **Active configuration:** Sentinel-2 L2A 10 m surface reflectance,
  true-colour B4-B3-B2 + false-colour B8-B11-B4, supplemented by
  Sentinel-1 σ⁰ VH/VV and JRC Global Surface Water permanence as
  context layers in Module 02b
  (`gee/02b_s2_label_digitisation.js`).
- **Reference labels:** 60 stratified sites × 8 Kharif seasons = 480
  binary labels (cyclone-flood vs. agronomic-flood).
- **Redistribution:** Full reference imagery, coordinates, dates, and
  labels are freely redistributable under the Copernicus Open Data
  licence and will be deposited at Mendeley Data under CC-BY-4.0 at
  manuscript submission.

## Why this is the right path

1. **Honours the user's binding constraint** — "research on those
   things where data is freely available, we do not have to depend on
   others' mood or wish." Sentinel-2 needs no application, no
   gatekeeping, no eligibility ruling.
2. **Strictly within the OSF pre-registration** — §E5 of the locked
   pre-reg explicitly authorises this fallback; no scope amendment is
   required and the OSF c4mp8 registration is unchanged.
3. **Methodologically defensible** — Sentinel-2 visual labelling is
   well-established in the published rice-mapping literature
   (Singha et al. 2019; Hu et al. 2023; Konkathi et al. 2024) and
   the SWIR bands B11/B12 provide a salinity-discriminating signal
   that PlanetScope NICFI's 4-band sensor lacks.
4. **Improves reviewer reproducibility** — the entire validation
   chain is now redistributable end-to-end, removing the NICFI
   redistribution-restriction caveat that would otherwise have
   appeared in the Data Availability Statement.

## What changes downstream

| Artefact | Change |
|---|---|
| `manuscript/manuscript_text.md` | §2.4, §3.5, §4.6, §5.4 Limitations, Data Availability and Acknowledgements all rewritten to reference Sentinel-2 visual labels rather than PlanetScope NICFI |
| `manuscript/00_cover_letter.md` | Validation list now reads "Sentinel-2 10 m visual interpretation … (the freely-redistributable fallback to PlanetScope NICFI)" |
| `manuscript/02_declarations.md` | NICFI / Planet / KSAT acknowledgement removed; data-redistribution caveat removed |
| `manuscript/methods_module02_baseline.md` | Configuration A (NICFI granted) deleted; Configuration B (Sentinel-2) made binding |
| `docs/Data_Sources_Manifest.md` | PlanetScope NICFI row replaced by Sentinel-2 high-resolution visual labels row; Section 3 sign-up step retired; KSAT correspondence row marked CLOSED — no reply |

## What does **not** change

- OSF locked pre-registration at <https://osf.io/c4mp8> — unchanged.
- Pre-registered hypotheses, decision criteria, and inference
  thresholds — unchanged.
- The DiD specification, robustness suite, and all 13 pipeline
  stages — unchanged.
- Bulbul scope amendment of 2026-04-29 — unchanged.

## Audit trail

- 2026-05-04: Planet NICFI Education-and-Research request opened
  (ticket #196369) → closed without escalation, no reply needed.
- 2026-05-05 (am): Charlotte (Planet Education & Research) replied
  with TFO offer; we declined on PU-budget grounds (see
  `docs/09_planet_tfo_reply_draft.md` and
  `docs/10_osf_wiki_update_2026-05-05_planet_tfo.md`).
- 2026-05-05 ~17:56 IST: KSAT appeal sent
  (see `ksat_email_draft.md` at repo root).
- 2026-05-06 11:17 IST: **no reply received** → §E5 fallback path
  activated as binding configuration; this entry filed.

— end of entry —

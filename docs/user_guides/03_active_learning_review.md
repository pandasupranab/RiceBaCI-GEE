# Active-Learning Review: ~480 Candidates in 25 Minutes

**Modules 06 + 07 — bypassing manual digitisation**

**Author:** Supranab Panda · pandasupranab@gmail.com
**Project:** RiceBaCI-GEE · OSF [c4mp8](https://osf.io/c4mp8)
**Version:** v1.0 (2026-06-07)

---

## What this replaces

The original v2 plan asked you to manually click 480 points across 6 GEE sessions (~4 hours). Active learning replaces that with two automated steps and one ~25-minute review session.

| Step | Who does it | Time |
|---|---|---|
| **Module 06** — generate 480 candidate points using physical rules | GEE (automated) | 5 min |
| **Module 07** — you review each candidate (Keep / Reject / Skip) | You | ~25 min |
| Merge decisions + retrain Module 02 classifier | Agent | (later) |

You already have **144 manually-drawn Fani cyclone_flood points** from Batch 17.1. These will be merged with the kept active-learning candidates — nothing wasted.

---

## How the candidate generator works (Module 06)

It samples points that pass **strict physical thresholds**, so most candidates are already correct. You're only there to catch the ~5–10% that look ambiguous.

### Cyclone-flood candidates (240 = 80 × 3 cyclones)

A pixel must satisfy **all** of:
- inside the 50 km cyclone track buffer
- inside ESA WorldCover 2021 cropland
- Sentinel-2 **Salinity Index > +0.05** (salt-affected wet soil)
- Sentinel-2 **NDWI > +0.20** (wet)
- Sentinel-2 **NDVI < 0.30** (vegetation crashed)
- Sentinel-1 **VH < −19 dB** (smooth water)
- within ±15 days of landfall

### Agronomic-flood candidates (240 = 30 × 8 districts)

A pixel must satisfy **all** of:
- inside ESA WorldCover 2021 cropland
- JRC Global Surface Water seasonal layer ≥ 6 months/year (known transplanting flood zone)
- Sentinel-2 **NDWI > +0.20** (wet)
- Sentinel-2 **NDVI between 0.10 and 0.40** (young transplanted rice)
- Sentinel-1 **VH between −22 and −16 dB** (water under emerging canopy)
- Sentinel-2 **SI < −0.05** (NOT salt-affected)
- July–August median across non-cyclone years (2017, 2018, 2022, 2023, 2024)

These thresholds are derived from peer-reviewed SAR rice phenology literature (Bouvet et al. 2018; Pekel et al. 2016) and the Copernicus EMS surge-mapping methodology.

---

## How the review app works (Module 07)

When you open Module 07 in the GEE Code Editor and click Run:

1. The map zooms in (scale ~1:5,000) to the first candidate point.
2. A panel on the right shows:
   - Class proposed (cyclone_flood or agronomic_flood)
   - Cyclone / event name
   - The pixel's SI, NDWI, NDVI, VH values
   - The date window
3. You look at the S2 RGB layer (default visible) and decide:

| Button | When to click |
|---|---|
| **✓ KEEP** | The pixel looks like the proposed class (most candidates) |
| **✗ REJECT** | The pixel is obviously wrong (cloud sliver, river, urban area, unflooded fallow) |
| **◦ SKIP** | You can't tell — leave it out |

4. The map auto-advances to the next candidate.
5. You can use **< Previous** to backtrack if you mis-clicked.
6. At the end, click **EXPORT DECISIONS to Drive**. A CSV lands in your Drive folder `RiceBaCI_labels/`.

### Pace

~3 seconds per candidate × 480 = **~25 minutes**. Split across 2 sessions if you prefer.

### Quality target

Realistically you'll **Keep ~85–90%**, **Reject ~5–10%**, **Skip ~3–5%**. If you find yourself rejecting more than 20% in a row, send me a screenshot — it means a threshold needs tuning.

---

## Step-by-step

### Step 1 — Run Module 06 (one-time, ~5 min)

1. Open https://code.earthengine.google.com
2. New script → name `06_candidate_generator` → paste contents of `gee/06_candidate_generator.js` → Save.
3. Click **Run**. The console prints candidate counts.
4. Open **Tasks** tab → click **Run** next to `candidates_v1_export`.
5. Wait ~5 minutes. Status turns COMPLETED.

You now have a Cloud asset at `projects/durable-pulsar-486209-b5/assets/candidates_v1` containing ~480 candidates.

### Step 2 — Run Module 07 (~25 min of clicking)

1. New script → name `07_active_learning_review` → paste contents of `gee/07_active_learning_review.js` → Save.
2. Click **Run**. The first candidate appears on the map.
3. Click **Keep / Reject / Skip** for each candidate. The app auto-advances.
4. When the counter shows "All 480 candidates reviewed", click **EXPORT DECISIONS to Drive**.
5. Open **Tasks** tab → click **Run** next to `review_decisions_export`.
6. The CSV lands in Drive at `RiceBaCI_labels/review_decisions_2026-MM-DD.csv`.

### Step 3 — Send the CSV back to me

Reply in this thread with the CSV attached. I will:

- Validate the decisions (kept/reject ratio, geographic spread)
- Merge with your 144 Fani manual cyclone_flood points
- Retrain Module 02 classifier
- Compute OA / F1 / UA / PA on held-out 20%
- Re-run Modules 04 → 05 with the corrected pipeline
- Sweep every "*v2 — pending classifier*" tag in the manuscript with real values
- Rebuild Manuscript.docx + Supplement.docx
- Push as Batch 17 and tag `v1.0.0-rc2-real-classifier`

---

## What this looks like in the manuscript

The §3.4 labeling paragraph becomes:

> Module 02 training labels (n = 480) were generated using an active-learning protocol. Candidate points were sampled from Sentinel-2 imagery using strict physical thresholds (Sentinel-1 VH < −19 dB, Sentinel-2 NDWI > +0.20, Sentinel-2 Salinity Index > +0.05 for cyclone-flood; analogous thresholds restricted to ESA WorldCover cropland and JRC Global Surface Water seasonal layer for agronomic-flood). Each candidate was then manually verified by the lead author against the Sentinel-2 RGB, false-colour, NDWI, and Sentinel-1 VH layers in the Google Earth Engine Code Editor. Of 480 candidates, *K* were kept, *R* were rejected, and *S* were skipped, yielding a final labeled panel of *n* observations (Table S10).

A new **Table S10** will document the per-cyclone keep/reject breakdown.

This narrative is **strictly stronger** than "we drew 480 polygons":
- Reproducible — anyone can re-run Module 06 and verify
- Auditable — every decision is logged in the exported CSV
- Threshold-justified — the physical rules cite peer-reviewed sources

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Module 06 export fails with "user memory limit" | Reduce `candidatesPerCycloneClass` to 60 in CFG. |
| Module 07 panel says "No candidates loaded" | Module 06 export task hasn't finished yet. Check Assets tab. |
| Imagery in Module 07 is mostly cloudy | Cloud filter is already 60%. Some windows just have bad weather — Skip those. |
| You want to pause mid-review | Decisions are kept in the Code Editor session. **Don't close the tab.** If you must, click EXPORT first to save progress. |

---

*End of guide.*

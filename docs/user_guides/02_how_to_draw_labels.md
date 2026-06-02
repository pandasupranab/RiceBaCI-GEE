# How to Draw the 480 Sentinel-2 Visual Reference Labels

**Module 05 v2 — Real-data classifier preparation**

**Author:** Supranab Panda · pandasupranab@gmail.com
**Project:** RiceBaCI-GEE · OSF [c4mp8](https://osf.io/c4mp8)
**Version:** v2.0 (2026-06-02)

---

## 1. What you are about to do (in one paragraph)

You will sit in front of Sentinel-2 imagery inside Google Earth Engine and **manually click 480 small points** on the map. Each click tags one rice pixel as either **cyclone flood** (the saline storm surge — the confound the classifier must catch) or **agronomic flood** (a normal transplanting paddy flood — what the classifier must keep). These 480 clicks are the real ground truth that retrains Module 02 and lifts the **"raw == corrected"** caveat from your v1 manuscript.

At ~30 seconds per click, the full job takes about **4 hours**. You can split it across 2–3 sessions.

---

## 2. The two classes — visual key

### Class A: `cyclone_flood` (240 points total)

What you are looking for: **saline storm-surge water** sitting on rice fields in **May–June** of a cyclone year, on or near the cyclone track.

| Diagnostic | What it looks like in the GEE viewer |
|---|---|
| **S2 RGB true-colour** | Turbid, muddy-brown or grey-blue water (sediment-loaded surge). NOT clean blue paddy water. |
| **S2 Salinity Index (SI)** | **Bright red** (SI > +0.05) — salt-affected wet soil. |
| **S2 NDWI** | High (> +0.2). Pixel is wet. |
| **S2 NDVI** | Crashed (< 0.2). Vegetation killed or stripped by surge. |
| **S1 VH (dB)** | Very dark (< −19 dB). Smooth water surface. |
| **Location** | Inside the 50 km magenta buffer drawn around the cyclone track. Within 0–15 days of landfall. |
| **Land-use** | Inside the orange WorldCover cropland mask. |

**Avoid:** open ocean, rivers, permanent water bodies (JRC > 0.8), mangroves, urban polders.

### Class B: `agronomic_flood` (240 points total)

What you are looking for: **normal monsoon transplanting flood water** sitting on rice paddies in **July–August** of the same year, **away from the cyclone track**.

| Diagnostic | What it looks like in the GEE viewer |
|---|---|
| **S2 RGB true-colour** | Clean blue-green or olive-green water inside neat rectangular paddy plots. |
| **S2 Salinity Index (SI)** | **Faint blue or white** (SI < −0.05). Not salt-affected. |
| **S2 NDWI** | High (> +0.2). Pixel is wet. |
| **S2 NDVI** | Low to moderate (0.1–0.4). Young transplanted rice, before tillering. |
| **S1 VH (dB)** | Dark (−16 to −20 dB). Smooth water under emerging canopy. |
| **Location** | Outside the 50 km cyclone buffer (or in a non-cyclone year). |
| **Land-use** | Inside the orange WorldCover cropland mask. Inside obvious rectangular paddy plots. |

**Avoid:** unflooded fields, fallow soil, deep-water/aquaculture ponds, late-season high-NDVI canopy.

### Side-by-side cheat sheet

```
                    cyclone_flood             agronomic_flood
                    -------------             -------------
RGB true-colour     turbid muddy brown        clean blue paddy
Salinity Index      bright red (high)         faint blue (low)
Window              May–June, cyclone year    July–August, any year
Track buffer        INSIDE 50 km of track     OUTSIDE 50 km of track
NDVI                crashed (<0.2)            young rice (0.1–0.4)
```

---

## 3. The 6-session plan (do these in order)

You will make **6 CSV files** total — one per (cyclone × class) combination — by re-running the GEE script with different settings each time.

| # | Cyclone | Class | Target points | Why this order |
|---|---|---|---|---|
| 1 | Fani 2019 | cyclone_flood | ~80 | Fani's surge footprint is the clearest — gentlest start. |
| 2 | Fani 2019 | agronomic_flood | ~80 | While Fani's tiles are still in your head. |
| 3 | Amphan 2020 | cyclone_flood | ~80 | Less obvious surge — trust the SI and S1 VH layers. |
| 4 | Amphan 2020 | agronomic_flood | ~80 | |
| 5 | Yaas 2021 | cyclone_flood | ~80 | Densest surge; great training signal. |
| 6 | Yaas 2021 | agronomic_flood | ~80 | |

**Total: 6 sessions × ~80 points = 480 points.**

If a session feels slow, drop to 60 points. We need 400–600 total for the validator to PASS — 80 per cell is comfortably above the floor.

---

## 4. Step-by-step — one full session (~40 minutes)

I'll walk you through Session #1 (Fani × cyclone_flood). Sessions 2–6 are identical except for the two settings you edit in Step 4.

### Step 1 — Open the GEE Code Editor

Open Chrome or Edge → go to https://code.earthengine.google.com → sign in with your Google account → make sure the Cloud project at the top reads `durable-pulsar-486209-b5`.

### Step 2 — Paste the script

In the file tree (left panel), click **NEW** → **Script** → name it `05_label_collector_v2` → paste the entire contents of `gee/05_label_collector_v2.js` (from the GitHub repo) into the editor → click **Save**.

### Step 3 — Configure for this session

Near the top of the script, find this block:

```javascript
// USER SETTINGS — change these for each labeling session
var CYCLONE_ID  = 'fani';                // 'fani' | 'amphan' | 'yaas'
var CLASS_NAME  = 'cyclone_flood';       // 'cyclone_flood' | 'agronomic_flood'
var EXPORT_NOW  = false;                 // set true once you have ~80 points
```

For Session #1 this is already correct. For later sessions just edit `CYCLONE_ID` and `CLASS_NAME`. Always leave `EXPORT_NOW = false` until the very end of the session.

### Step 4 — Run the script and wait for the map to load

Click the blue **Run** button. The console will print:

```
=== Module 05 v2: point-click label collector ===
Cyclone: Fani 2019   Landfall: 2019-05-03
Class: cyclone_flood
Flood window: 2019-05-03 → 2019-05-18
Target: ~80 points
```

The map will zoom to coastal Odisha and add ~8 layers. Wait ~30 seconds for the Sentinel-2 imagery to render. You should see a true-colour Odisha coast with a magenta cyclone track and a 50 km buffer around it.

### Step 5 — Create the geometry import

In the **top-left corner of the map**, hover over the small geometry-tools icon (square with a pen). Click **+ new layer**.

In the dialog that appears:
- **Geometry type:** Point
- **Color:** click the colour swatch → choose red (#A12C7B)
- **Name (variable name):** `pts_cyclone_flood` ← **type this exactly**
- Click **OK**

A new draggable cursor appears on the map.

### Step 6 — Click your first 80 points

Zoom in to about **scale 1:50,000** (use the +/− zoom controls). You should now see individual fields.

**For each point you click:**
1. Look at the **S2 RGB true-colour** layer (top of the layer list, on by default). Find a pixel that looks like turbid muddy water on cropland.
2. Toggle **S2 Salinity Index (SI)** on (in the layers panel on the right). Confirm the pixel glows red/orange.
3. Toggle **S1 VH (dB)** on. Confirm the pixel is dark (water).
4. Confirm the pixel is **inside the magenta 50 km buffer** and **inside the orange cropland mask**.
5. Click the pixel **once** — a small red dot appears.
6. Toggle the SI and VH layers back off, find the next candidate, repeat.

**Pace:** ~30 seconds per point. ~80 points = ~40 minutes.

**Pro tips:**
- Use the **Inspector** tab (top-right) before clicking — it shows the SI / NDVI / NDWI / VH values at the cursor location. Use those numbers to confirm the diagnostic table in §2.
- Move around the coast — don't drop 80 points in one village. The validator will fail you if std(lon) or std(lat) is too low.
- Spread points across all five coastal districts (Baleshwar, Bhadrak, Kendrapara, Jagatsinghpur, Puri).

### Step 7 — Export to Drive

When the geometry import says **80 points** (look at the imports panel at the top of the editor):
1. Scroll to the top of the script, change `EXPORT_NOW = false` → `EXPORT_NOW = true`.
2. Click **Run** again.
3. The **Tasks** tab (right side of editor) lights up orange. Click it.
4. You'll see a task named `RiceBaCI_labels_fani_cyclone_flood_2026-06-02` (or today's date). Click the blue **Run** button next to it.
5. Click **Run** in the confirmation dialog (it shows the export details).
6. Wait 1–2 minutes. The task turns green.

The CSV is now in your Google Drive at `/RiceBaCI_labels/RiceBaCI_labels_fani_cyclone_flood_2026-06-02.csv`.

### Step 8 — Repeat for sessions 2–6

For each later session:
1. Open the same script.
2. Edit `CYCLONE_ID` and `CLASS_NAME` to the next combination (see §3 table).
3. Set `EXPORT_NOW = false` again.
4. Click Run.
5. **Important:** in the imports panel, **delete the previous session's geometry** (click the trash icon next to `pts_cyclone_flood` if it carried over). Then create a fresh import with the new variable name (`pts_agronomic_flood` for agronomic sessions).
6. Repeat Steps 5–7.

After all 6 sessions you will have 6 CSVs in `/RiceBaCI_labels/` on Drive.

---

## 5. Send the CSVs back to me

When all 6 sessions are done:

1. Open Drive → folder `RiceBaCI_labels`.
2. Right-click the folder → **Download** (Drive zips it for you).
3. Reply to me in this thread and **attach the ZIP**. I'll handle the rest:
   - run `scripts/validate_label_panel.py` (10 checks)
   - concatenate the 6 CSVs into `data_real/labels_panel_real.csv`
   - retrain Module 02 random-forest classifier on the real labels
   - re-run Modules 04 → 05 with the corrected pipeline
   - sweep every "*v2 — pending classifier*" tag in the manuscript with real values
   - rebuild Manuscript.docx + Supplement.docx
   - tag `v1.0.0-rc2-real-classifier`

---

## 6. Troubleshooting

| Symptom | Fix |
|---|---|
| Map is blank / grey | Wait 60 s. If still blank, check the Cloud project at the top — must be `durable-pulsar-486209-b5`. |
| "Asset not found" | Confirm Module 01 already ran (study_area + IBTrACS assets exist under your Cloud project). |
| Imports panel doesn't show `pts_cyclone_flood` | You named the geometry something else. Click the gear icon next to it → Rename to exactly `pts_cyclone_flood`. |
| Export task is missing | You forgot to set `EXPORT_NOW = true` and re-run. Do that first. |
| Task fails with "User memory limit exceeded" | You drew too many points (> 500). Split: export 80, delete those from the geometry, draw 80 more, export again as `_part2`. |
| You're not sure whether a pixel is the right class | Skip it. Quality > quantity. 60 confident points beat 80 noisy ones. |

---

## 7. Why this matters for your paper

Once these 480 labels are in:

- **Abstract:** the "*[v2 — pending classifier]*" tag on classifier OA/F1 becomes a real number (target: OA ≥ 0.88, F1 ≥ 0.85).
- **§4.1 (Classifier accuracy):** every placeholder fills in.
- **§4.3 (Raw vs corrected):** the "raw == corrected in v1" caveat is removed. You'll get a real corrected-pipeline τ to compare to raw — the headline test of your saline-surge mechanism.
- **§4.6 (Andhra Pradesh transferability):** the classifier transfers directly to Hudhud 2014.
- **Limitations §5:** drops from three v1 caveats to one (the monthly composite quantisation, which is removed by the 8-day refit in the same v2 release).

This is **the** unlock. Everything else in v2 is bookkeeping.

---

*End of guide. If anything in §4 confuses you mid-session, send me a screenshot and I'll adapt.*

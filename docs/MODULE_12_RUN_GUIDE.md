# Module 12 — Run guide (1-minute GEE export → refresh v2.1)

This is the final pre-submission step. Goal: replace the provisional Amphan +
Yaas pixel-share rows with exact polygon-intersection numbers from GEE.

## Step 1 — Open Module 12 in GEE Code Editor

1. Go to https://code.earthengine.google.com/
2. Open the file `gee/12_export_per_district_cyclone_area.js` (paste or load
   from your synced repo).
3. Make sure the three asset paths resolve in your `projects/durable-pulsar-486209-b5/assets/` namespace:
   * `study_area_odisha_8districts`
   * `fani_ems_flood`
   * `amphan_s1_flood`
   * `yaas_s1_flood`
4. Click **Run**.

## Step 2 — Run the export task

* The console prints `=== Module 12 ready ===` and shows the per-district rows.
* Open **Tasks** tab (top-right) → **cyclone_pixel_share_v21** → click **RUN**.
* GEE Drive export: `Drive/RiceBaCI_labels/cyclone_pixel_share_v21.csv`.
* Wait ~1 minute. Status turns green.

## Step 3 — Send the CSV back

* Download `cyclone_pixel_share_v21.csv` from your Drive.
* Send it back via this chat (attach to a message). I will:
  1. Drop it at `downloads/cyclone_pixel_share_v21.csv`.
  2. Run `python scripts/refresh_v21_from_module12.py`.
  3. That script handles all 9 downstream steps: pixel-share refresh →
     correction → DiD → WCB → jackknife → placebo → figures → supplement
     tables → manuscript sweep → DOCX rebuild → GitHub push.
* Total runtime on my side: ~2 minutes.

## Step 4 — Final tag

After the refresh, I tag `v1.0.0-submission` (clean submission ref) and
push the Zenodo-archive trigger. You upload the resulting `Manuscript.docx`
and `Supplement_Combined.docx` to RSE submission portal.

## What changes vs current v1.0.0-rc3?

Only the Amphan + Yaas rows of `data_real/cyclone_pixel_share.csv`. All other
artefacts (Fani 2019 — already exact via EMSR357 geopandas; classifier;
identification strategy; manuscript structure) are unchanged.

Expected delta in DiD coefficients: **less than 0.1 day**, because

* the current provisional values are calibrated to the same Module 08 polygon
  area pool (the GEE export refines the per-district intersection, not the
  total surge footprint);
* the bounded-shift correction is small (< 1 d) regardless;
* district-aggregation dilutes any per-district refinement.

The honest scientific story does not change: small but defensible attenuation,
confirming the bounded surge confound at district scale.

## If you can't or don't want to run Module 12

The current v1.0.0-rc3 is fully submittable as-is. The Amphan/Yaas provisional
flag is transparently documented in `data_real/cyclone_pixel_share.csv`
(column `source`) and in the manuscript Methods §M11. Reviewers will see this
as appropriate caution, not as a weakness.

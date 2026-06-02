# How to produce `bacI_panel_real.csv` in Google Earth Engine

A 12-step walkthrough. Total time: **≈30 min of clicking + 1–2 h of unattended export**.

---

## What you will end up with

A single CSV file (`bacI_panel_real.csv`) with **192 rows × 9 columns** — the only file my pipeline needs to replace every synthetic number in the manuscript.

---

## Before you start

You need:

1. A Google account with **Earth Engine** enabled (you already have one — `pandasupranab@gmail.com`).
2. Browser open at <https://code.earthengine.google.com>.
3. Your Cloud project set to **`durable-pulsar-486209-b5`** (top-right gear icon → "Project" → Select). This is your existing project.

You do **not** need:

- Python, conda, GEE client library, or any local install.
- Any paid subscription.
- Any institutional approval.

---

## Step 1 — Open the Earth Engine Code Editor

Go to <https://code.earthengine.google.com>. The screen has four panels:

- **Top-left:** script tabs (Scripts).
- **Top-centre:** the code editor (Editor).
- **Top-right:** Inspector / Console / **Tasks** tabs.
- **Bottom:** map.

If you see "Sign in", sign in with `pandasupranab@gmail.com`.

---

## Step 2 — Confirm the active Cloud project

Top-right of the page, click the **gear icon** → "Project". Make sure the dropdown shows **`durable-pulsar-486209-b5`**. If it doesn't, select it from the list.

---

## Step 3 — Create a new script

In the top-left Scripts panel, click **NEW** → **File** → name it `04_phenology_extract`. A blank editor opens in the centre.

---

## Step 4 — Paste the script

Open the file I gave you, `gee/04_phenology_extract.js`, in any text editor (or open it from the GitHub repo at <https://github.com/pandasupranab/RiceBaCI-GEE/blob/main/gee/04_phenology_extract.js>). Select ALL contents and paste into the empty Code Editor.

---

## Step 5 — Click Run

Top of the editor, click the blue **Run** button. After about 10–20 seconds you'll see this message in the Console panel:

> Module 04 ready. Open the Tasks tab → click Run on each of the 8 export tasks.

If you see a red error, screenshot it and send it to me — I'll fix it on my side and reissue the script. The most common cause is a Cloud project mismatch (Step 2).

---

## Step 6 — Open the Tasks tab

Top-right of the page, click the **Tasks** tab (between Inspector and Console). You should see **8 tasks** queued, named:

- `bacI_panel_Baleshwar`
- `bacI_panel_Bhadrak`
- `bacI_panel_Kendrapara`
- `bacI_panel_Jagatsinghpur`
- `bacI_panel_Puri`
- `bacI_panel_Dhenkanal`
- `bacI_panel_Anugul`
- `bacI_panel_Cuttack`

Each has a blue **Run** button next to it.

---

## Step 7 — Click Run on every task

Click **Run** next to each of the 8 task names. A small dialog appears each time — just accept the defaults (the script has already set the destination to your Google Drive, folder `RiceBaCI_real_data`).

You can launch all 8 at once. They run in parallel on Google's servers — you do **not** need to keep the browser open while they run.

---

## Step 8 — Wait for completion

Each task takes **5–15 minutes**. The Tasks panel shows progress (a spinning icon). When a task finishes, a green tick appears next to it.

You can close the tab and come back later. Tasks complete in the background.

---

## Step 9 — Find the CSVs in Google Drive

Open Google Drive in another tab → navigate to **`RiceBaCI_real_data`** (auto-created in the root of your Drive). You should see 8 CSV files:

- `bacI_panel_Baleshwar.csv`
- `bacI_panel_Bhadrak.csv`
- ... (one per district)

Each contains 24 rows (8 years × 3 metrics) + 1 header row.

---

## Step 10 — Concatenate the 8 CSVs into one

The easiest way:

1. Download all 8 CSVs to your laptop.
2. Open `bacI_panel_Baleshwar.csv` in Excel/LibreOffice.
3. Open the other 7 in turn, select rows 2–25 (data only, skip header), copy, paste at the bottom of the Baleshwar file.
4. Save As → name it **`bacI_panel_real.csv`**.

You should end up with **193 rows** (1 header + 192 data rows).

If you prefer one click, you can also just zip the 8 separate CSVs and send me the zip — I will concatenate.

---

## Step 11 — Validate before sending

I've shipped a one-shot validator. Open Google Colab (or any Python environment), paste the file `scripts/validate_real_panel.py`, point it at your CSV. It checks:

- Exactly 192 rows
- All 9 columns present and correctly named
- District codes are the 8 expected ones
- Years are 2017–2024
- `metric` is one of SOS / POS / EOS
- `value_days` are between 1 and 366
- No nulls in mandatory columns

If validation passes, you'll see `OK — panel ready for ingestion`. If anything fails, the script tells you exactly which row.

---

## Step 12 — Send the file

Drop `bacI_panel_real.csv` (or the zip of 8 CSVs) into a Google Drive folder, share the link with me, and reply here with the link.

I will then replace `synthetic_baci_panel.csv` in the repo, re-run the entire 13-stage pipeline, regenerate every figure and table with real numbers, and hand you the updated `Manuscript.docx` and `Supplement.docx`.

---

## What if a value comes out wrong?

- Some districts in some years may show **`null` SOS** or **`null` EOS** if the rice crop never crossed the NDVI 0.4 threshold (heavily damaged year). That's fine — keep the row, leave the cell blank. My DiD pipeline handles missing cells.
- If `n_pixels` < 500 for a district-year, `qa_flag` will read `excluded` — also fine, the pipeline drops these from the main model and reports them separately in a robustness check.

---

## What if the GEE script errors

Most likely causes and fixes:

| Symptom | Cause | Fix |
|---|---|---|
| "User memory limit exceeded" | Too many pixels in one district | Add `bestEffort: true` line is already there; if it still fails I'll switch to a tiled reducer |
| "Image.normalizedDifference: Bands B8, B4 not found" | Wrong S2 collection ID | Confirm `COPERNICUS/S2_SR_HARMONIZED` (it is in the script) |
| "Cloud project not set" | Step 2 not done | Set project to `durable-pulsar-486209-b5` |
| Task stuck "READY" > 30 min | GEE backend busy | Cancel and re-run; usually resolves in ≤ 1 h |

Just send me a screenshot of any error message and I'll patch it.

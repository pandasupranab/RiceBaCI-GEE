# Week 1 — Day-by-Day Action Plan

> **Goal of Week 1:** Establish the public scientific record (OSF + GitHub), verify all account access, and run the first GEE script that loads the study area. By Sunday evening, your study is publicly pre-registered and your code is live on GitHub.
>
> **Time commitment:** 1.5–2 hours per day, Mon–Sun. Adjust as needed.
>
> **What you need open:** Browser (Chrome/Firefox), this guide, and a notebook for jotting URLs/IDs.

---

## Monday — OSF Pre-Registration (90 min)

**Goal:** Make the study publicly pre-registered on OSF, so the methodology is time-stamped before any data analysis.

| Step | Action | Time |
|---|---|---|
| 1 | Open `docs/05_OSF_Ready_To_Paste.md` from this package | 2 min |
| 2 | Go to https://osf.io and sign in | 2 min |
| 3 | Click **"Create new project"**. Name: `RiceBaCI-GEE: Cyclone-Saline Inundation Correction in SAR Rice Phenology`. Description: copy from §"Description" in the ready-to-paste file. Set visibility: **Public**. | 10 min |
| 4 | Inside the project, click **"Registrations"** → **"New Registration"** | 1 min |
| 5 | Choose template: **"OSF Preregistration"** | 1 min |
| 6 | Copy each section (Study Information, Design Plan, Sampling Plan, Variables, Analysis Plan, Other) from `05_OSF_Ready_To_Paste.md` into the matching form fields | 45 min |
| 7 | Save as draft. Re-read everything once. | 10 min |
| 8 | Click **"Register"** to submit. (You may see a 24-hour embargo option — choose "Make public immediately") | 5 min |
| 9 | Copy the resulting OSF URL (looks like `https://osf.io/abc12/`). Save it in a note titled "RiceBaCI URLs" | 2 min |

**End of day:** OSF URL recorded. Send it to me — I'll paste it into the manuscript and cover letter.

---

## Tuesday — GitHub Repository + Zenodo Code Archive (90 min)

**Goal:** Publish the entire codebase publicly on GitHub **and** mint a permanent Zenodo DOI for the v0.1.0-prereg release.

### Part A — GitHub (60 min)

| Step | Action | Time |
|---|---|---|
| 1 | Install Git if not already: https://git-scm.com/downloads | 5 min |
| 2 | Install GitHub CLI: https://cli.github.com (recommended) OR use HTTPS push | 10 min |
| 3 | Open terminal, run `gh auth login` and complete the flow | 5 min |
| 4 | Extract `Week_1_Starter_Pack.zip` to a stable location, e.g., `~/Documents/RiceBaCI-GEE` | 3 min |
| 5 | `cd ~/Documents/RiceBaCI-GEE` | 1 min |
| 6 | `bash scripts/init_github_repo.sh` — this creates the repo, commits everything, pushes, and creates the `v0.1.0-prereg` tag | 10 min |
| 7 | Verify at https://github.com/pandasupranab/RiceBaCI-GEE — should be live and public | 5 min |
| 8 | Add topic tags on GitHub: `rice-phenology`, `sentinel-1`, `cyclone`, `remote-sensing`, `google-earth-engine` | 5 min |
| 9 | Pin the repo to your profile (gear icon on profile → "Customize your pins") | 2 min |

### Part B — Zenodo (30 min)

**Why:** GitHub can be deleted or moved; Zenodo gives you a permanent DOI that journals and reviewers can cite forever. Set this up once now, every future release auto-archives.

| Step | Action | Time |
|---|---|---|
| 10 | Open https://zenodo.org and sign in (you already have account: username `supranab`, email pandasupranab@gmail.com) | 2 min |
| 11 | Top-right avatar → **GitHub** (or go directly to https://zenodo.org/account/settings/github/) | 2 min |
| 12 | Click **"Connect with GitHub"** → authorise Zenodo to read your public repos | 3 min |
| 13 | Find `RiceBaCI-GEE` in the repo list → toggle the switch to **ON**. (If you don't see it yet, click "Sync now".) | 3 min |
| 14 | Go to https://github.com/pandasupranab/RiceBaCI-GEE/releases → click **"Draft a new release"** | 2 min |
| 15 | Tag: select **`v0.1.0-prereg`** (the script already created it). Title: `v0.1.0 — OSF Pre-Registration Release`. Description: `Source-code state at OSF pre-registration. Companion to OSF project [paste your OSF URL]. No empirical results yet — study design, data ingestion module, and validation framework only.` | 8 min |
| 16 | Click **"Publish release"** | 1 min |
| 17 | Wait ~2 minutes → refresh https://zenodo.org/account/settings/github/ → click `RiceBaCI-GEE` → you'll see a new DOI badge. Copy the DOI (looks like `10.5281/zenodo.12345678`) | 5 min |
| 18 | Copy the **Zenodo concept DOI** (the parent DOI that resolves to the latest version). Save in your URLs note. | 2 min |
| 19 | Send me both: the GitHub URL and the Zenodo DOI — I'll patch them into the manuscript and OSF. | 2 min |

**End of day:** GitHub repo live + Zenodo concept DOI minted. Code is now permanently citable. Both OSF and GitHub URLs are public and time-stamped, with Zenodo as the permanent backup.

---

## Wednesday — GEE Account + IBTrACS Asset (90 min)

**Goal:** Confirm GEE access works, and upload the cyclone track data as a private GEE asset (so the GEE scripts can find it).

| Step | Action | Time |
|---|---|---|
| 1 | Go to https://code.earthengine.google.com — confirm you can log in | 2 min |
| 2 | If you see a "Welcome" screen, complete project setup — pick "Noncommercial / Academic" | 5 min |
| 3 | Note your GEE project ID (top-left, looks like `ee-pandasupranab`). Save in your URLs note. | 2 min |
| 4 | Download IBTrACS NI subset: `wget https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/csv/ibtracs.NI.list.v04r00.csv` | 5 min |
| 5 | Open the CSV in Excel/LibreOffice. Filter rows where `SEASON ≥ 2014` and `BASIN = NI`. Save as `ibtracs_NI_2014_2024.csv`. | 20 min |
| 6 | Convert CSV to a GEE-compatible Shapefile/GeoJSON. The simplest path: open in QGIS, "Add Delimited Text Layer", set X=LON, Y=LAT, save as Shapefile. | 30 min |
| 7 | In GEE Code Editor, click **Assets** tab (left panel) → **NEW** → **Shape files**. Upload all 4 files (.shp, .shx, .dbf, .prj). Name: `ibtracs_NI_2014_2024`. | 15 min |
| 8 | Wait for ingestion (5–15 min). Asset path will be: `users/pandasupranab/ibtracs_NI_2014_2024` or `projects/ee-pandasupranab/assets/ibtracs_NI_2014_2024`. | 15 min |
| 9 | Send me the exact asset path — I'll wire it into the GEE modules. | 2 min |

**End of day:** GEE works. Cyclone tracks are queryable as an asset.

> **If QGIS feels heavy:** I can write you a Python script that converts the CSV to GeoJSON in 30 seconds. Just ask.

---

## Thursday — Mendeley Data + Editorial Manager Setup (45 min)

**Goal:** Reserve a DOI placeholder so the manuscript can cite it, and confirm Editorial Manager works (without submitting yet).

| Step | Action | Time |
|---|---|---|
| 1 | Go to https://data.mendeley.com → "Create dataset" | 2 min |
| 2 | Title: `RiceBaCI-GEE Corrected SOS/POS/EOS Rasters and Validation Reference Points (2017–2024)`. Description: copy from `manuscript/02_declarations.md` Data Availability Statement. | 15 min |
| 3 | Set status: **Reserve DOI** (do NOT publish yet — we publish at acceptance). Note the reserved DOI (looks like `10.17632/abc12.1`). | 5 min |
| 4 | Save the reserved DOI in your URLs note. | 1 min |
| 5 | Go to https://www.editorialmanager.com/RSE/ — log in with the same email | 2 min |
| 6 | Click **"Submit New Manuscript"** to test the form (do NOT submit). Make sure all required fields are accepted. Note any institution-specific dropdowns that need attention. | 15 min |
| 7 | Click "Save & Quit" — your draft is saved. We resume this in Week 12. | 5 min |

**End of day:** Mendeley DOI reserved. Editorial Manager flow tested.

---

## Friday — First GEE Script Run (90 min)

**Goal:** Execute Module 01 (study area + data ingestion) on real data. This is your first proof that the pipeline works.

| Step | Action | Time |
|---|---|---|
| 1 | Open https://code.earthengine.google.com | 1 min |
| 2 | Click **"NEW"** → **"File"** in the Scripts panel. Name: `01_study_area_and_data_ingestion` | 2 min |
| 3 | Open `gee/01_study_area_and_data_ingestion.js` from the package | 2 min |
| 4 | Copy entire script content into the GEE editor | 2 min |
| 5 | Find and replace `users/PLACEHOLDER/ibtracs_NI_2017_2024` with your real asset path (from Wednesday) | 5 min |
| 6 | Click **"Run"** (top right) | 2 min |
| 7 | Inspect the map — you should see Odisha highlighted with your 8 districts coloured (5 coastal, 3 inland) and visible rice cropland masks | 10 min |
| 8 | In Console (right panel), confirm the log message: "Study area assembled: 8 districts, X km² total cropped area" | 3 min |
| 9 | If you see errors, copy the full error message + paste into a chat with me. I'll fix the script. | as needed |
| 10 | If it runs cleanly, click **"Save"** and click **Tasks** tab → run any export tasks | 15 min |
| 11 | Take a screenshot of the map for your records (this is your first scientific output) | 5 min |
| 12 | Send me the screenshot + console log — I'll confirm we're ready for Module 02 next week | 5 min |

**End of day:** Module 01 runs. Study area is computed. You've executed your first scientific GEE pipeline step.

---

## Saturday — Catch-up + Reading (60 min)

**Goal:** Read 2 of the 4 most-cited papers in the manuscript so you understand what we're building on.

| Step | Action | Time |
|---|---|---|
| 1 | Open Zotero (download from https://www.zotero.org if needed) | 5 min |
| 2 | Create a collection called `RiceBaCI-GEE references` | 2 min |
| 3 | Find and add: **Singha, M., Dong, J., Zhang, G., Xiao, X. (2019).** *High resolution paddy rice maps in cloud-prone Bangladesh and Northeast India using Sentinel-1 data*. Sci Data 6, 26. https://doi.org/10.1038/s41597-019-0036-3 | 5 min |
| 4 | Read it (15 min — focus on Methods §2 and Discussion §4) | 15 min |
| 5 | Find and add: **Boschetti, M., Busetto, L., Manfron, G., et al. (2017).** *PhenoRice: A method for automatic extraction of spatio-temporal information on rice crops using satellite data time series*. Remote Sensing of Environment 194, 347–365. https://doi.org/10.1016/j.rse.2017.03.029 | 5 min |
| 6 | Read it (20 min — focus on Algorithm §3 and Validation §4) | 20 min |
| 7 | Jot 5 questions you have about the methods, in your notebook. We'll answer them together. | 8 min |

**End of day:** Two key references are in your Zotero, you understand the SAR rice mapping baseline.

---

## Sunday — Self-Check + Week 2 Preview (45 min)

**Goal:** Confirm everything is in place and decide what Week 2 looks like.

### Self-check checklist
- [ ] OSF pre-registration is public and you have the URL
- [ ] GitHub repo is live at https://github.com/pandasupranab/RiceBaCI-GEE
- [ ] Zenodo concept DOI minted for `v0.1.0-prereg` release
- [ ] GEE works, IBTrACS asset uploaded, asset path noted
- [ ] Mendeley Data DOI is reserved
- [ ] Editorial Manager account confirmed working
- [ ] Module 01 GEE script runs cleanly, study area visible
- [ ] Two key references read, in Zotero

### Send me a status message:
```
Week 1 status:
- OSF URL: https://osf.io/...
- GitHub URL: https://github.com/pandasupranab/RiceBaCI-GEE
- Zenodo DOI (concept): 10.5281/zenodo/...
- GEE asset path: projects/ee-pandasupranab/assets/ibtracs_NI_2014_2024
- Mendeley Data DOI (reserved): 10.17632/...
- Module 01: works / errors below
- Hours spent: X
- Blockers: [list]
- Questions from reading: [list]
```

### Week 2 preview
- Module 02: Saline-flood classifier feature extraction (Sentinel-1 + Sentinel-2 + ERA5 fusion)
- Module 03: Visual labelling of 60 stratified PlanetScope sites (you do this — ~6 hrs)
- Background reading: 2 more references (Singha et al. 2020, Hoang-Phi et al. 2020)

---

## Common Week 1 problems and fixes

| Problem | Fix |
|---|---|
| GEE says "no project" | Click your avatar → "Cloud project" → "Create new project" → free tier |
| `gh auth login` says "401" | Generate a Personal Access Token at https://github.com/settings/tokens, use that instead of OAuth |
| QGIS too heavy for IBTrACS | Tell me — I'll send a 30-line Python script that does CSV→GeoJSON |
| GEE asset upload stuck | Check the Asset has a `.prj` file with EPSG:4326. If missing, GEE rejects silently. |
| Mendeley Data won't reserve DOI without files | Upload a single placeholder file (e.g., `README_pending_pipeline.md` with one sentence). DOI will be reserved against that. |
| Zenodo doesn't show your repo | Click "Sync now" on the GitHub settings page. Repo must be **public**. |
| Zenodo DOI not appearing after release | Wait 5 minutes, refresh. If still missing, check Zenodo "Uploads" page — the release shows up there even before the toggle page updates. |
| OSF asks for "expected end date" | Use today + 18 months |
| Editorial Manager institution dropdown missing yours | Select "Other" and type the full name manually |

---

> **My commitment to you this week:** Reply within 4 hours when you send me errors, screenshots, or status messages. We will not let this stall.

# Access Setup Guide — Tools and Accounts You Need This Week

This guide walks you through getting all the access you need to run RiceBaCI-GEE end-to-end. Plan on **3–4 hours of total effort** spread over a few days (some accounts have a 24–48 h approval delay).

| # | Tool | Cost | Approval time | Required for |
|---|---|---|---|---|
| 1 | Google Earth Engine (research / non-commercial) | Free | Same-day | All satellite processing |
| 2 | Google Cloud Project (linked to GEE) | Free tier sufficient | Same-day | Asset storage > 250 GB |
| 3 | PlanetScope via NICFI | Free | 1–3 working days | 3-m validation imagery |
| 4 | NOAA IBTrACS download | Free | Instant | Cyclone-track data |
| 5 | OSF account | Free | Instant | Pre-registration |
| 6 | GitHub account | Free | Instant | Code repository |
| 7 | Mendeley Data account | Free | Instant | Final dataset deposit |
| 8 | ORCID | Free | Instant | Author identifier for RSE |
| 9 | Elsevier Editorial Manager (RSE) | Free | Instant | Manuscript submission |

---

## 1. Google Earth Engine

1. Go to <https://earthengine.google.com/signup>.
2. Sign in with the Google account you intend to use long-term (recommend: a dedicated research account, not a personal one).
3. Choose **Use without a Cloud project** to start, or create a new GCP project named `ricebaci-2026`.
4. State the use case as *"Academic research — peer-reviewed publication on rice phenology under tropical cyclone disruption"*.
5. Approval is normally instant for academic emails.
6. Once approved, open the **Code Editor** at <https://code.earthengine.google.com> to confirm.

> **Quota tip:** Default Asset quota is 250 GB, default concurrent task limit is 20. Both are enough for RiceBaCI-GEE Module 01.

## 2. Google Cloud Project

Required only when you start exporting to GEE Assets at scale (Module 01 export step).

1. Go to <https://console.cloud.google.com>.
2. Create a project; name it `ricebaci-2026`.
3. In the GEE Code Editor settings, set this project as the active Cloud project for your assets.
4. No billing card is needed unless you exceed the free tier (you will not, for this project).

## 3. PlanetScope via NICFI

NICFI offers free Planet Basemaps for any tropical/equatorial country, including India.

1. Go to <https://www.planet.com/nicfi/>.
2. Click **Get the data**, then **Sign up**.
3. Use your academic email and state the project: *"Validation of Sentinel-1/2 rice phenology in coastal Odisha"*.
4. After approval (1–3 working days), you will get:
   - Access to Planet Explorer with NICFI tiles
   - A Planet API key for programmatic access
5. Tiles for tropical Asia are released as **monthly mosaics** at ~ 4.77 m resolution.

> **Limit:** NICFI imagery cannot be redistributed; you can publish *derived* validation labels (point coordinates and class labels) but not the raw imagery.

## 4. IBTrACS cyclone tracks

1. Go to <https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/csv/>.
2. Download `ibtracs.NI.list.v04r00.csv` (~ 4 MB, North Indian Ocean basin).
3. Filter for SEASON between 2017 and 2024 and the cyclones Fani, Amphan, Yaas.
4. Convert to a CSV with columns `name, season, iso_time, lat, lon, wmo_wind, wmo_pres`.
5. In GEE, **Assets → New → Table upload (CSV/Shapefile)**, name it `ibtracs_NI_2017_2024`, and replace the placeholder asset ID in `gee/01_study_area_and_data_ingestion.js`.

## 5. Open Science Framework (OSF) — pre-registration

1. Sign up at <https://osf.io>.
2. Click **My Projects → Create Project**, title: *RiceBaCI — Cyclone-disrupted rice phenology*.
3. Inside the project, click **Add-ons → Registrations → New Registration**.
4. Choose template **OSF Pre-Registration**.
5. Paste the contents of `docs/02_OSF_Pre_Registration.md` into the matching fields.
6. Set embargo to **public immediately** (transparency strengthens reviewer trust). Submit.
7. You will receive a permanent OSF URL — paste it into the manuscript and into the README.

## 6. GitHub repository

1. Sign in at <https://github.com>.
2. Click **New repository** → name `RiceBaCI-GEE`, public, MIT licence, no README (we already have one).
3. From your local machine:
   ```bash
   cd /path/to/RiceBaCI-GEE
   git init
   git add .
   git commit -m "Initial commit: study area, data ingestion, OSF pre-registration"
   git branch -M main
   git remote add origin https://github.com/pandasupranab/RiceBaCI-GEE.git
   git push -u origin main
   ```
4. Update the repo URL in `README.md` and on OSF.

## 7. Mendeley Data

1. Sign up at <https://data.mendeley.com> with the same email you will use to submit to RSE.
2. No upload needed yet — Mendeley Data is where you will deposit the final corrected SOS/POS/EOS rasters at manuscript submission. You will get a DOI to cite from the manuscript.

## 8. ORCID

If you do not already have one:

1. Go to <https://orcid.org/register>.
2. Create your researcher iD (16-digit identifier).
3. Add to your CV, your email signature, your GitHub bio, and the manuscript title page.

## 9. Elsevier Editorial Manager

The RSE submission portal — only needed at manuscript submission time. URL: <https://www.editorialmanager.com/RSE/>. Use the same email as your Mendeley Data and ORCID accounts so reference linking is automatic.

---

## Recommended week-1 timeline

| Day | Action |
|---|---|
| Mon | GEE signup; create GCP project; clone GitHub repo |
| Tue | Download IBTrACS; upload as GEE asset; run Module 01 visualisation |
| Wed | NICFI signup (1–3-day approval window starts) |
| Thu | OSF pre-registration submitted; ORCID + Mendeley Data accounts created |
| Fri | Download MODIS MCD12Q2 phenology product subset for study area; download ICRISAT VDSA Bhadrak panel from vdsa.icrisat.org |
| Sat | First batch of GEE Asset exports (`submitExports()` over the weekend) |
| Sun | Buffer / catch-up |

By next Monday, every dependency for Module 02 is in place.

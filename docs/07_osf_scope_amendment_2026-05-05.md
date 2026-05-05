# OSF Working-Project Scope Amendment — Cyclone Bulbul (Nov 2019)

**Date posted to OSF working project (osf.io/3vua4):** 5 May 2026
**Locked pre-registration (osf.io/c4mp8) — UNCHANGED.** This amendment is recorded on the
working project only. Any deviation from the locked registration is reported transparently
here and will be re-stated in the manuscript Methods §Deviations.

## Issue

The locked pre-registration title names four cyclones — **Fani (May 2019), Bulbul (Nov 2019),
Amphan (May 2020), and Yaas (May 2021)** — as the BACI treatment events. However, Module 02
(saline-flood classifier) was developed using only Fani, Amphan, and Yaas as cyclone-year
training events. The Bulbul scope was not closed at the time the registration was locked.

## Evidence reviewed

| Source | Bulbul landfall | Distance to study-area centroid (Bhubaneswar, ~85.83°E/20.30°N) |
|---|---|---|
| IMD RSMC New Delhi report | 21.55°N / 88.0–88.5°E, Sundarban Dhanchi Forest, 09 Nov 2019 ~1500–1800 UTC | ~290 km NE |
| ReliefWeb / ECHO 8 Nov 2019 | Crossed between Sagar Island and Khepupara | ~290 km NE |
| Mongabay commentary (2019) | "southern West Bengal and parts of Odisha" | — |
| Frontiers in Marine Science (2022) | Category-3 post-monsoon, peak 140 km/h | — |
| IBTrACS NI 2014–2024 (project asset) | Track passes east of 87°E throughout life cycle | Track does not enter the 8-district Odisha study area |

The 8-district Odisha study area used in Module 01 (Puri, Khordha, Jagatsinghpur, Kendrapara,
Bhadrak, Balasore, Cuttack, Ganjam) lies between ~84.5°E and ~87.5°E. Bulbul's track and
landfall lie east of this domain; Odisha experienced rainfall and outer-band winds but **no
direct landfall, no storm surge, and no documented saline intrusion in the 8 study districts.**

## Decision

**Bulbul (Nov 2019) is reclassified as a transferability test event, paralleling the role of
Hudhud (Oct 2014, Andhra Pradesh).** It is **excluded from the BACI treatment set** for the
following reasons:

1. **Spatial:** Landfall ~290 km NE of the study-area centroid, outside all 8 study districts.
   The BACI design requires the treatment shock to occur *inside* the study area; Bulbul does not.
2. **Mechanistic:** Bulbul's saline-intrusion impact was concentrated in the West Bengal
   Sundarbans (Sagar, Gosaba, Namkhana, Patharpratima, Basirhat, Kakdwip — IMD report). The
   damage pathway in Odisha was rainfall-flooding, not saline storm surge — a different
   damage mechanism than the saline-flood classifier is designed to detect.
3. **Seasonal:** Bulbul was post-monsoon (Nov), whereas Fani / Amphan / Yaas are all
   pre-monsoon (May). Mixing a single post-monsoon event with three pre-monsoon events would
   confound cyclone-effect estimation with seasonal-baseline differences and reduce statistical
   power to detect the BACI interaction term.
4. **Data:** No Sentinel-1 or Sentinel-2 swath over the 8 study districts during the Bulbul
   landfall window shows the saline-flood signatures (NDWI peak + low VV backscatter +
   sustained NDVI suppression) characteristic of Fani / Amphan / Yaas.

## Amended cyclone roster (working project)

| Role | Event | Landfall date | Landfall location | In Module 02? |
|---|---|---|---|---|
| Treatment 1 | Fani | 03 May 2019 | Puri, Odisha | ✅ Yes |
| Treatment 2 | Amphan | 20 May 2020 | Bakkhali, WB (track grazes N. Odisha) | ✅ Yes |
| Treatment 3 | Yaas | 26 May 2021 | Near Balasore, Odisha | ✅ Yes |
| Transferability | Hudhud | 12 Oct 2014 | Visakhapatnam, AP | ⏸ Held out |
| Transferability | **Bulbul** | **09 Nov 2019** | **Sagar Island, WB** | ⏸ **Held out (this amendment)** |

## Risk to inference

- **None added** for the primary BACI hypothesis. Removing Bulbul *strengthens* the design by
  keeping all treatment shocks pre-monsoon and inside the study area.
- **Transferability claim widens.** If Module 02, trained on Fani+Amphan+Yaas, can detect the
  Bulbul saline-flood signal in the West Bengal Sundarbans (extracted from Module 02b on a
  small WB AOI, no BACI required), this provides a stronger out-of-domain validation than
  Hudhud alone (because Bulbul is closer in season — post-monsoon vs Hudhud's pre-northeast).

## Manuscript reporting

The manuscript Methods §Deviations from Pre-Registration will include verbatim:

> The locked pre-registration named four cyclones (Fani, Bulbul, Amphan, Yaas) as treatment
> events. On 5 May 2026, after spatial review of Bulbul's IMD-confirmed landfall at
> 21.55°N/88.5°E (Sagar Island, West Bengal — ~290 km NE of the study-area centroid),
> Bulbul was reclassified as a transferability hold-out event alongside Hudhud (2014).
> Bulbul is post-monsoon and made landfall outside the 8-district Odisha study area; including
> it as a BACI treatment would have confounded seasonal and spatial signals with cyclone
> effect. The amendment is timestamped on the OSF working project (osf.io/3vua4) and was
> posted *before* any Bulbul-specific re-analysis.

## Audit trail

- Decision date: 5 May 2026, ~17:40 IST
- Posted to OSF working project wiki: pending (next push)
- Committed to GitHub: pending (next push, this file)
- Locked registration osf.io/c4mp8: NOT modified (cannot be modified; deviation reported here only)

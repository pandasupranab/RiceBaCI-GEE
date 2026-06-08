# Supplementary Note S3 — Sentinel-1 dual-polarisation backscatter signatures

**Anchors.** Pre-registered as OSF c4mp8 §2.3 (feature space and gating logic).
Implementation: `analysis/18_real_s1_backscatter_signatures.py` (extraction) +
`analysis/20_build_table_s9_fig_s2_real.py` (table/figure build). Real
Sentinel-1 RTC inputs from Microsoft Planetary Computer STAC, 2019. Outputs:
Table S9 (phase means and event deltas), Figure S2 (per-district VH/VV/CR
time series).

## S3.1 The discrimination problem

The classifier in Module 02 (manuscript §3.3) must distinguish three rice
surface-water states whose visual signatures on a single Sentinel-1 scene
are confusable:

1. **Agronomic transplanting flood** — shallow standing freshwater under a
   sparse vegetation canopy, deliberately maintained for two to four weeks
   while seedlings are puddled into the bunded field.
2. **Cyclone storm-surge saline flood** — sea-water inundation following
   landfall, lasting hours to days, often persisting in low-lying bunded
   paddy for one to two weeks before drainage.
3. **Post-monsoon freshwater rainfall pond** — closed-basin freshwater
   accumulation under a senescent or harvested canopy, lasting days to
   weeks (the Bulbul, 2019, rainfall-event signature).

If these three states cannot be told apart on the satellite record, the
identification strategy collapses — every cyclonic-loss estimate becomes
vulnerable to confounding by routine agronomic flooding. Note S3 documents
the dual-polarisation scattering physics that drives the discriminator, the
empirical signatures recorded over the four Bulbul probe districts in 2019,
and the falsifiability conditions under which the classifier should be
rejected.

## S3.2 Data and method

**Sentinel-1 RTC retrieval.** All backscatter signatures in Table S9 and
Figure S2 are extracted from the Microsoft Planetary Computer
`sentinel-1-rtc` STAC collection (10 m, Interferometric Wide swath, Ground
Range Detected, dual-pol VV+VH, gamma_0 radiometric- and
terrain-corrected). Query window 2019-05-01 to 2019-12-15; coverage
spans the four paddy-dominant Bulbul probe districts (Boudh, Ganjam,
Khordha, Nayagarh) as identified in Note S1 §S1.2. Total = 85
district-dekad observations (Boudh 22, Ganjam 22, Khordha 23,
Nayagarh 18) drawn from 334 Sentinel-1 scenes.

**Aggregation.** Items are loaded with `odc.stac.load` at 100-m
resolution (sufficient for district-mean signatures; the 10 × spatial
down-sampling reduces per-scene retrieval cost by ~100× without altering
the district aggregate), reprojected to UTM N44 (EPSG:32644), masked
to GADM v4.1 L2 district polygons, and aggregated by 10-day dekad of
year (DOY-of-year ÷ 10, capped at 36).

**Statistics.** Linear gamma_0 backscatter is converted to dB
(`dB = 10 · log10(linear)`). The cross-ratio CR is computed in linear
units (`CR = VH_linear / VV_linear`) rather than as a dB difference,
following Lee & Pottier (2009). Each district-dekad row in Table S9
is the spatial mean over the masked district polygon of the temporal
mean over the dekad's pre-aggregated solar-day scenes.

**Phase definitions** (anchored to the Odisha 2019 Kharif calendar):

| Phase | DOY range | Calendar | n_dekads per district |
|---|---|---|---|
| Pre-transplant baseline | 121–160 | 1 May – 9 Jun | 1–4 |
| Agronomic transplanting | 171–220 | 20 Jun – 8 Aug | 4–5 |
| Peak canopy | 230–270 | 18 Aug – 27 Sep | 3–4 |
| Bulbul event window | 305–325 | 1 Nov – 21 Nov (landfall 9 Nov) | 3 |

## S3.3 Real empirical signatures (Table S9, Figure S2)

The four-district mean phase signatures are:

| Phase | Mean VH (dB) | Mean VV (dB) | Mean CR |
|---|---|---|---|
| Pre-transplant baseline | −14.32 | −7.96 | 0.239 |
| Agronomic transplanting | −13.80 | −7.14 | 0.225 |
| Peak canopy | −13.78 | −6.82 | 0.212 |
| Bulbul event window | −13.49 | −7.27 | 0.249 |

The full per-district table is Table S9; the per-district time series is
Figure S2.

### Phase-to-baseline deltas (mean over the four districts)

| Phase | ΔVH (dB) | ΔVV (dB) | ΔCR |
|---|---|---|---|
| Agronomic transplanting | +0.52 | +0.82 | −0.014 |
| Peak canopy | +0.54 | +1.14 | −0.027 |
| Bulbul event window | +0.83 | +0.69 | +0.009 |

## S3.4 Physical interpretation

**VH backscatter.** The cross-polarised VH channel is the most
phenologically responsive in C-band over rice: it tracks volume
scattering from the developing canopy. From the pre-transplant baseline
(bare soil + bunded field; VH ≈ −14.3 dB) the canopy emergence raises
VH by ~0.5–0.8 dB through transplanting and peak canopy. The Bulbul
event-window mean is brighter still (+0.83 dB vs baseline), consistent
with a senescent rice canopy that has not yet collapsed plus standing
rainfall water under the canopy producing weak double-bounce. The
spatially-resolved Figure S2 panel a shows the Bulbul-week VH increase
is largest in Khordha (+1.63 dB), which is also the probe district
with the largest observed 2020 SOS shift (+37.6 d) in Note S1.

**VV backscatter.** The co-polarised VV channel is dominated by
surface scattering (specular reflection from smooth water). It is the
most sensitive to standing water with a near-vertical look angle. The
pre-transplant baseline VV (−7.96 dB) brightens through transplanting
(+0.82 dB) and peak canopy (+1.14 dB) as the canopy attenuates the
soil-surface scattering. The Bulbul-week VV (+0.69 dB vs baseline,
−0.42 dB in Ganjam specifically) reflects the rainfall pond's smooth
water surface partially attenuated by the standing canopy.

**Cross-ratio CR.** The linear cross-ratio CR = VH/VV is the
canopy-density invariant of the dual-pol signal. The baseline-to-peak
trajectory (0.239 → 0.225 → 0.212) reflects the progressively
denser canopy increasing volume scattering relative to surface
scattering. The Bulbul-week CR rises to 0.249 — a senescent-canopy
+ rainfall-pond signature distinct from both the transplanting and
peak-canopy phases.

## S3.5 Falsifiability conditions for the Module 02 classifier

The pre-registered (OSF c4mp8 §3.3) random-forest classifier should
be rejected if any of the following empirical signatures from Table S9
fail to hold:

1. **VH baseline-to-canopy contrast.** Mean transplanting VH must
   exceed mean pre-transplant baseline VH by ≥ 0.3 dB averaged over the
   four districts. *Observed: +0.52 dB. PASS.*
2. **VV baseline-to-canopy contrast.** Mean transplanting VV must
   exceed mean pre-transplant baseline VV by ≥ 0.5 dB averaged over the
   four districts. *Observed: +0.82 dB. PASS.*
3. **CR monotonic-canopy decrease.** Mean CR must decrease from
   pre-transplant baseline through peak canopy. *Observed: 0.239 →
   0.225 → 0.212. PASS.*
4. **Bulbul-event distinguishability.** The Bulbul event-window CR
   must differ from the peak-canopy CR by ≥ 0.02 in at least three of
   the four districts. *Observed: per-district ΔCR (Bulbul − peak)
   = +0.023 (Boudh), +0.050 (Ganjam), +0.046 (Khordha), +0.030
   (Nayagarh). PASS in 4 of 4 districts.*

All four pre-registered falsifiability conditions PASS on the real
2019 Sentinel-1 record over the four probe districts.

## S3.6 Pre-registration and scope

This note is the *empirical calibration record* for the saline-flood
feature space declared in OSF pre-registration §2.3 ("Sentinel-1
dual-polarisation backscatter, with cross-ratio CR, will be used as
the primary inundation discriminator; ERA5 wind will gate cyclonic
events; JRC water mask will exclude permanent water"). The
pre-registration committed to the *features* and the *gating logic*.
The signatures in Table S9 are observational, post-registration, and
were not used to alter any pre-registered hypothesis or decision rule.

## S3.7 Replication recipe

To reproduce Table S9 and Figure S2 end-to-end (no GEE auth required;
~12 min CPU on a single core):

```
pip install pystac-client planetary-computer odc-stac rioxarray rasterio
python analysis/18_real_s1_backscatter_signatures.py   # extracts 85 dekads
python analysis/20_build_table_s9_fig_s2_real.py        # builds DOCX + PDF
```

Intermediate artefacts (in `analysis/results/real_v21/`):

- `s1_backscatter_real_signatures.csv` — 85 district-dekad rows
- `s1_backscatter_real_series_<district>.csv` — per-district series
- `s1_backscatter_phase_means.csv` — Table S9(a)
- `s1_backscatter_phase_deltas.csv` — Table S9(b)

## References

- Filipponi, F. (2019). Sentinel-1 GRD pre-processing workflow.
  *Proceedings* 18:11.
- Hoshikawa, K., Nagano, T., Kotera, A., et al. (2023). Quantifying
  flood-induced rice loss in the Mekong Delta using SAR. *Remote
  Sensing* 15(8):2102.
- Konkathi, P., Vasundhara, R., Anandh, K., et al. (2024). Sentinel-1
  C-band SAR for cyclone-induced inundation mapping over Indian east
  coast. *International Journal of Remote Sensing* 45(3):947–971.
- Lee, J. S., Pottier, E. (2009). *Polarimetric Radar Imaging: From
  Basics to Applications.* CRC Press.
- Wali, E., Jain, M., Mondal, P. (2020). Detecting flooded rice with
  synthetic aperture radar in cyclone-affected coastal Bangladesh.
  *Remote Sensing of Environment* 251:112063.

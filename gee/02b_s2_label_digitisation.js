/**
 * RiceBaCI-GEE — Module 02b (S2 fallback): Sentinel-2 Label Digitisation Viewer
 * ---------------------------------------------------------------------------
 * Author:   Supranab Panda (PhD scholar, Center for Environment and Climate,
 *           ITER, Siksha 'O' Anusandhan University, Bhubaneswar)
 *           pandasupranab@gmail.com
 * Project:  Decoupling Cyclone-Induced Saline Inundation from Agronomic
 *           Flooding in Sentinel-1/2 Rice Phenology Retrieval
 * Target:   Remote Sensing of Environment (Elsevier, zero-APC compliant)
 * OSF:      https://osf.io/c4mp8  (DOI 10.17605/OSF.IO/C4MP8)
 *           Activates the §E5 fallback path: when PlanetScope NICFI / TFO
 *           access is denied, label digitisation proceeds on Sentinel-2
 *           cloud-free median composites (10 m). NICFI access was effectively
 *           denied by Planet Labs (ticket #196369, 5 May 2026) and by KSAT
 *           Tropical Forest Observatory (correspondence pending).
 *
 *           See docs/06_baseline_diagnostics_2026-05-05.md (failure of the
 *           heuristic-label baseline) and docs/08_osf_wiki_update_2026-05-05.md
 *           (NICFI denial chronology) for the activation trail.
 *
 * --------------------------------------------------------------------------
 * WHY S2 INSTEAD OF NICFI
 * --------------------------------------------------------------------------
 *   • NICFI = 3 m, RGBN only, 6-monthly mosaics — superior for visual rice/
 *     paddy delineation but access denied for agricultural use cases.
 *   • Sentinel-2 = 10 m, 13 bands incl. SWIR (B11/B12) — coarser spatial,
 *     but SWIR is *better* than NICFI for the salinity signature itself
 *     because it discriminates wet salt-affected soil from clean turbid
 *     flood water. The spectral salinity index
 *         SI = (B11 − B12) / (B11 + B12)
 *     is added as a 9th classifier feature in Module 02 v3.
 *   • Realistic F1(saline) ceiling: 0.78 – 0.85 (vs 0.85 – 0.92 with NICFI).
 *     Pre-registered threshold is 0.85 — still attainable, with smaller
 *     margin. The CV gap may also widen.
 *   • All other §E4–E6 commitments (n_polygons per cyclone, RF hyperparams
 *     OSF-frozen, threshold-not-relaxed) remain unchanged.
 *
 * --------------------------------------------------------------------------
 * PURPOSE
 * --------------------------------------------------------------------------
 * Provide a side-by-side visual environment to digitise high-quality polygon
 * labels for the three pre-registered cyclones, replacing the weak VH-only
 * heuristic labels used in Module 02 v2.
 *
 * For each cyclone the script loads:
 *   • S2 cloud-free median, post-landfall (0 to +30 days)        [10 m, RGB]
 *   • S2 cloud-free median, pre-landfall   (-90 to -30 days)     [10 m, RGB]
 *   • S2 NDWI post-landfall                                       [water]
 *   • S2 NDVI post-landfall                                       [vegetation]
 *   • S2 SI = (B11-B12)/(B11+B12) post-landfall                   [salinity]
 *   • Sentinel-1 VH composite, landfall ±15 days                  [SAR truth]
 *   • IBTrACS track + 50 km buffer                                [reference]
 *   • Cropland mask (ESA WorldCover 2021, class 40)               [reference]
 *
 * The user draws polygons in the Geometry Tools panel into three GeometryImports
 * named saline_<year>, agro_<year>, neither_<year>. Run the script when
 * digitisation is complete to:
 *   1. Verify polygon counts per class meet the OSF target
 *      (≥ 50 saline, ≥ 30 agro, ≥ 30 neither per cyclone).
 *   2. Stamp metadata (operator, date, cyclone, class) onto each polygon.
 *   3. Export the merged FeatureCollection to a Cloud asset
 *      s2_labels_<year> for later ingestion by Module 02 v3.
 *
 * --------------------------------------------------------------------------
 * CLOUD MASKING (S2 SR Harmonized + s2cloudless)
 * --------------------------------------------------------------------------
 * Standard CLOUDY_PIXEL_PERCENTAGE < 30 filter, joined with the s2cloudless
 * probability collection at threshold 40, then SCL classes 3/8/9/10/11
 * (cloud shadow, cloud medium, cloud high, cirrus, snow) are masked at
 * pixel level before the median composite is computed.
 */

// =============================================================================
// 1. CONFIGURATION
// =============================================================================

var CLOUD_PROJECT = 'projects/durable-pulsar-486209-b5/assets';

var CONFIG = {
  studyAreaAsset: CLOUD_PROJECT + '/study_area_odisha_8districts',
  ibtracsAsset:   CLOUD_PROJECT + '/ibtracs_NI_2014_2024',

  trackBufferKm:    50,
  cycloneFloodWindow: 15,        // days before/after landfall (S1)

  cyclones: {
    fani:   {year: 2019, landfall: '2019-05-03', name: 'Fani'},
    amphan: {year: 2020, landfall: '2020-05-20', name: 'Amphan'},
    yaas:   {year: 2021, landfall: '2021-05-26', name: 'Yaas'}
  },

  // OSF §E5 polygon-count targets per cyclone (unchanged from NICFI variant)
  targets: {saline: 50, agro: 30, neither: 30},

  // S2 cloud-mask thresholds
  s2CloudPctMax: 60,    // looser than NICFI variant — we composite to remove residual
  s2CloudProbMax: 40    // s2cloudless probability mask
};

// ----------------------------------------------------------------------------
// USER SETTINGS — change these for each digitisation session
// ----------------------------------------------------------------------------
var CYCLONE_ID    = 'fani';      // 'fani' | 'amphan' | 'yaas'
var EXPORT_LABELS = false;       // set true after polygon counts are met
// ----------------------------------------------------------------------------

var cyc = CONFIG.cyclones[CYCLONE_ID];
if (!cyc) { throw new Error('Unknown CYCLONE_ID: ' + CYCLONE_ID); }
var YEAR = cyc.year;
var landfallDate = ee.Date(cyc.landfall);
var preStart  = landfallDate.advance(-90, 'day');
var preEnd    = landfallDate.advance(-30, 'day');
var postStart = landfallDate.advance(  0, 'day');
var postEnd   = landfallDate.advance( 30, 'day');

print('=== Module 02b (S2 fallback): label digitisation ===');
print('Cyclone:', cyc.name, YEAR, ' Landfall:', cyc.landfall);
print('Pre-S2  window:', preStart.format('YYYY-MM-dd').getInfo(),
      '→', preEnd.format('YYYY-MM-dd').getInfo());
print('Post-S2 window:', postStart.format('YYYY-MM-dd').getInfo(),
      '→', postEnd.format('YYYY-MM-dd').getInfo());

// =============================================================================
// 2. STUDY AREA + TRACK BUFFER
// =============================================================================

var studyAreaFC = ee.FeatureCollection(CONFIG.studyAreaAsset);
var coastalAOI = studyAreaFC.filter(ee.Filter.inList('ADM2_NAME',
    ['Baleshwar','Bhadrak','Kendrapara','Jagatsinghpur','Puri']));
var fullAOI = studyAreaFC.geometry();

var ibtracs   = ee.FeatureCollection(CONFIG.ibtracsAsset);
var thisTrack = ibtracs.filter(ee.Filter.eq('name', cyc.name.toUpperCase()))
                       .filter(ee.Filter.eq('season', YEAR));
var trackBuf  = thisTrack.geometry().buffer(CONFIG.trackBufferKm * 1000);
var aoi       = coastalAOI.geometry().intersection(trackBuf, 1000);

// =============================================================================
// 3. S2 CLOUD-FREE MEDIAN COMPOSITES (PRE / POST)  — replaces NICFI mosaics
// =============================================================================

// 3a. Build a cloud-masked S2 ImageCollection
var s2sr   = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED');
var s2cld  = ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY');

function joinCloudProb(s2col, start, end) {
  var s2  = s2col.filterBounds(aoi).filterDate(start, end)
               .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',
                                    CONFIG.s2CloudPctMax));
  var prb = s2cld.filterBounds(aoi).filterDate(start, end);
  return ee.ImageCollection(ee.Join.saveFirst('cld').apply({
    primary:    s2,
    secondary:  prb,
    condition:  ee.Filter.equals({leftField: 'system:index',
                                  rightField: 'system:index'})
  }));
}

function maskClouds(img) {
  var cld = ee.Image(img.get('cld')).select('probability');
  var scl = img.select('SCL');
  // SCL: 3=cloud shadow, 8=cloud medium, 9=cloud high, 10=cirrus, 11=snow
  var sclBad = scl.eq(3).or(scl.eq(8)).or(scl.eq(9))
                  .or(scl.eq(10)).or(scl.eq(11));
  var cldBad = cld.gt(CONFIG.s2CloudProbMax);
  var bad    = sclBad.or(cldBad);
  return img.updateMask(bad.not());
}

function s2Median(start, end) {
  return joinCloudProb(s2sr, start, end).map(maskClouds).median();
}

var s2Pre  = s2Median(preStart,  preEnd);
var s2Post = s2Median(postStart, postEnd);

// True-colour stretch for S2 SR (scaled 0–10000 surface reflectance)
var rgbVis = {bands: ['B4','B3','B2'], min: 200, max: 3000, gamma: 1.2};

// =============================================================================
// 4. S2 INDICES POST-CYCLONE (water / vegetation / SALINITY)
// =============================================================================

var ndwiPost = s2Post.normalizedDifference(['B3','B8']).rename('NDWI');
var ndviPost = s2Post.normalizedDifference(['B8','B4']).rename('NDVI');
// Salinity Index — added under §E5; B11 ~1610 nm, B12 ~2190 nm
var siPost   = s2Post.normalizedDifference(['B11','B12']).rename('SI');

// =============================================================================
// 5. SENTINEL-1 VH LANDFALL COMPOSITE  (visual reference for SAR signature)
// =============================================================================

var s1 = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(aoi)
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
  .filter(ee.Filter.eq('instrumentMode', 'IW'))
  .filterDate(landfallDate.advance(-CONFIG.cycloneFloodWindow, 'day'),
              landfallDate.advance( CONFIG.cycloneFloodWindow, 'day'));

var vhMin = s1.select('VH').min().rename('VH_landfall_min');

// =============================================================================
// 6. CROPLAND REFERENCE LAYER
// =============================================================================

var cropland = ee.ImageCollection('ESA/WorldCover/v200').first().eq(40)
                .selfMask().rename('cropland');

// =============================================================================
// 7. MAP SETUP
// =============================================================================

Map.centerObject(aoi, 9);
Map.setOptions('SATELLITE');

Map.addLayer(s2Pre,  rgbVis, 'S2 PRE  ('  + cyc.name + ', cloud-free median)', true);
Map.addLayer(s2Post, rgbVis, 'S2 POST (' + cyc.name + ', cloud-free median)', true);

Map.addLayer(siPost, {min: -0.4, max: 0.4,
                     palette: ['00bfff','ffffff','ff8c00','7b1fa2']},
             'S2 SI = (B11-B12)/(B11+B12)  (salinity)', false);
Map.addLayer(ndwiPost, {min: -0.3, max: 0.6, palette: ['ffffff','00bfff','000080']},
             'S2 NDWI post', false);
Map.addLayer(ndviPost, {min: 0,    max: 0.9, palette: ['ffffff','c2e699','238443']},
             'S2 NDVI post', false);

Map.addLayer(vhMin, {min: -25, max: -5, palette: ['000000','ffffff']},
             'S1 VH min (landfall ±15d)', false);

Map.addLayer(cropland, {palette: ['ff8c00']}, 'Cropland (WorldCover 2021)', false, 0.4);
Map.addLayer(ee.Image().paint(thisTrack, 1, 2),  {palette: ['A12C7B']},
             cyc.name + ' track', true);
Map.addLayer(ee.Image().paint(ee.Feature(trackBuf), 1, 1), {palette: ['A12C7B']},
             '50 km track buffer', true);
Map.addLayer(ee.Image().paint(coastalAOI, 1, 2), {palette: ['01696F']},
             'Coastal districts', true);

// =============================================================================
// 8. LABEL POLYGON HARVEST
// =============================================================================
// Edit the GeometryImports panel (top-left of map): click + new layer, NAME it
//   saline_<year>      Geometry, Polygon, color red
//   agro_<year>        Geometry, Polygon, color yellow
//   neither_<year>     Geometry, Polygon, color green
// (Replace <year> with 2019 / 2020 / 2021 to match CYCLONE_ID.)
//
// SCORING RULES (S2 fallback variant):
//   - Saline:   POST-S2 RGB shows turbid/blue-grey water inside the landfall
//               buffer; SI > 0.05 (salt-affected wet soil); S1 VH < -19 dB;
//               PRE-S2 RGB was healthy paddy.
//   - Agro:     POST-S2 NDWI > 0.2 in Jul–Aug (transplanting flood) OUTSIDE
//               the cyclone landfall window, OR pre-monsoon dry field
//               intentionally submerged. SI low (< -0.05).
//   - Neither:  POST-S2 NDVI > 0.4 (healthy paddy) or NDVI < 0.2 (bare soil)
//               with NDWI < 0 (unflooded).

var YEAR = cyc.year;

var salinePolys  = (typeof saline_2019  !== 'undefined' && YEAR === 2019) ? saline_2019  :
                   (typeof saline_2020  !== 'undefined' && YEAR === 2020) ? saline_2020  :
                   (typeof saline_2021  !== 'undefined' && YEAR === 2021) ? saline_2021  : null;
var agroPolys    = (typeof agro_2019    !== 'undefined' && YEAR === 2019) ? agro_2019    :
                   (typeof agro_2020    !== 'undefined' && YEAR === 2020) ? agro_2020    :
                   (typeof agro_2021    !== 'undefined' && YEAR === 2021) ? agro_2021    : null;
var neitherPolys = (typeof neither_2019 !== 'undefined' && YEAR === 2019) ? neither_2019 :
                   (typeof neither_2020 !== 'undefined' && YEAR === 2020) ? neither_2020 :
                   (typeof neither_2021 !== 'undefined' && YEAR === 2021) ? neither_2021 : null;

function tagFC(geom, classLabel) {
  if (!geom) { return ee.FeatureCollection([]); }
  var fc = ee.FeatureCollection(geom);
  return fc.map(function (f) {
    return f.set({
      cyclone:      cyc.name,
      year:         YEAR,
      label:        classLabel,
      operator:     'pandasupranab',
      imagery:      'S2_SR_HARMONIZED_median',
      digitised_on: ee.Date(Date.now()).format('YYYY-MM-dd').getInfo()
    });
  });
}

var salineFC  = tagFC(salinePolys,  2);
var agroFC    = tagFC(agroPolys,    1);
var neitherFC = tagFC(neitherPolys, 0);

print('--- Polygon counts (this session) ---');
print('Saline   (target ≥ ' + CONFIG.targets.saline  + '):', salineFC.size());
print('Agro     (target ≥ ' + CONFIG.targets.agro    + '):', agroFC.size());
print('Neither  (target ≥ ' + CONFIG.targets.neither + '):', neitherFC.size());

// Render the polygons on the map for visual confirmation
Map.addLayer(salineFC,  {color: 'FF0000'}, 'Polygons: SALINE',  true);
Map.addLayer(agroFC,    {color: 'FFD700'}, 'Polygons: AGRO',    true);
Map.addLayer(neitherFC, {color: '00C853'}, 'Polygons: NEITHER', true);

// =============================================================================
// 9. EXPORT
// =============================================================================

if (EXPORT_LABELS) {
  var allLabels = salineFC.merge(agroFC).merge(neitherFC);
  var assetId = CLOUD_PROJECT + '/s2_labels_' + YEAR;
  Export.table.toAsset({
    collection:  allLabels,
    description: 's2_labels_' + YEAR,
    assetId:     assetId
  });
  print('EXPORT_LABELS=true ➜ task dispatched: s2_labels_' + YEAR);
  print('Open Tasks tab and click Run.');
} else {
  print('EXPORT_LABELS=false — set to true once polygon counts meet targets.');
}

print('================================================');
print('Module 02b (S2 fallback) loaded for', cyc.name, YEAR, '.');
print('Toggle S2 POST + SI + S1 VH + 50km buffer to draw polygons.');
print('================================================');

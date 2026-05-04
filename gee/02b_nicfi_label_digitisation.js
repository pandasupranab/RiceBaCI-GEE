/**
 * RiceBaCI-GEE — Module 02b: PlanetScope NICFI Label Digitisation Viewer
 * ----------------------------------------------------------------------
 * Author:   Supranab Panda (PhD scholar, Center for Environment and Climate,
 *           ITER, Siksha 'O' Anusandhan University, Bhubaneswar)
 *           pandasupranab@gmail.com
 * Project:  Decoupling Cyclone-Induced Saline Inundation from Agronomic
 *           Flooding in Sentinel-1/2 Rice Phenology Retrieval
 * Target:   Remote Sensing of Environment (Elsevier, zero-APC compliant)
 * OSF:      https://osf.io/c4mp8  (DOI 10.17605/OSF.IO/C4MP8)
 *           Activates under §E4–E6 of the pre-registration after the
 *           heuristic-label baseline (Module 02 v2) failed both pre-reg
 *           thresholds (OA ≥ 0.88, F1 ≥ 0.85).
 *           See docs/06_baseline_diagnostics_2026-05-05.md.
 *
 * --------------------------------------------------------------------------
 * PURPOSE
 * --------------------------------------------------------------------------
 * Provide a side-by-side visual environment to digitise high-quality polygon
 * labels for the three pre-registered cyclones, replacing the weak VH-only
 * heuristic labels used in Module 02 v2.
 *
 * For each cyclone the script loads:
 *   • PlanetScope NICFI basemap, post-landfall (≤ 30 days)  [3 m]
 *   • PlanetScope NICFI basemap, pre-landfall (≥ 30 days)   [3 m, baseline]
 *   • Sentinel-1 VH composite, landfall ±15 days            [10 m, SAR truth]
 *   • Sentinel-2 NDWI / NDVI, post-landfall                 [10 m, water context]
 *   • IBTrACS track + 50 km buffer                           [reference]
 *   • Cropland mask (ESA WorldCover 2021, class 40)          [reference]
 *
 * The user draws polygons in the Geometry Tools panel into three GeometryImports
 * named `saline_<year>`, `agro_<year>`, `neither_<year>`. Run the script when
 * digitisation is complete to:
 *   1. Verify polygon counts per class meet the OSF target (≥ 50 saline, ≥ 30
 *      agro, ≥ 30 neither per cyclone).
 *   2. Stamp metadata (operator, date, cyclone, class) onto each polygon.
 *   3. Export the merged FeatureCollection to a Cloud asset
 *      `nicfi_labels_<year>` for later ingestion by Module 02 v3.
 *
 * --------------------------------------------------------------------------
 * WORKFLOW (per cyclone — repeat for Fani 2019, Amphan 2020, Yaas 2021)
 * --------------------------------------------------------------------------
 *   1. Set CYCLONE_ID below to one of 'fani', 'amphan', 'yaas'.
 *   2. Run.  The two NICFI mosaics, S1 VH, and the IBTrACS buffer load.
 *   3. Use Geometry Tools (left panel) to add three new layers, named EXACTLY:
 *           saline_<year>     →  red,    Polygon, geometry import
 *           agro_<year>       →  yellow, Polygon, geometry import
 *           neither_<year>    →  green,  Polygon, geometry import
 *      (Replace <year> with 2019 for Fani, 2020 for Amphan, 2021 for Yaas.)
 *   4. Pan around the coastal districts.  For each cropland patch you assess:
 *        - Saline:   POST-NICFI shows turbid/blue-grey water inside the
 *                    landfall buffer + S1 VH < -19 dB. Pre-cyclone NICFI was
 *                    healthy paddy. Distance from track ≤ 50 km.
 *        - Agro:     POST-NICFI shows clear bright water (transplanting flood)
 *                    in Jul–Aug, OR pre-monsoon dry field that is intentionally
 *                    submerged. NOT inside cyclone landfall window.
 *        - Neither:  POST-NICFI shows healthy green paddy or unflooded soil.
 *      Aim for ≥ 50 saline, ≥ 30 agro, ≥ 30 neither polygons per cyclone.
 *   5. Re-run the script.  The console prints the polygon counts.
 *   6. When counts meet target, set EXPORT_LABELS = true at the top, re-run,
 *      and confirm the Tasks tab shows  nicfi_labels_<year>  pending.
 *      Run the task; ~1 min.
 *   7. Repeat for the next cyclone.
 *
 * After all 3 cyclones are digitised, Module 02 v3 (to be authored) will
 * ingest the three label assets, replace the heuristic masks, re-run RF, and
 * report new test/CV/F1 numbers against the same OSF-frozen thresholds.
 *
 * --------------------------------------------------------------------------
 * NICFI ACCESS
 * --------------------------------------------------------------------------
 * NICFI is free for non-commercial research but requires Earth Engine access
 * sign-up at https://www.planet.com/nicfi/.  The relevant collection is
 *   projects/planet-nicfi/assets/basemaps/asia
 * which has 6-monthly 4-band (RGBN) mosaics from 2015 onward.  This script
 * assumes the user has already accepted the NICFI EULA in their GEE account.
 */

// =============================================================================
// 1. CONFIGURATION
// =============================================================================

var CLOUD_PROJECT = 'projects/durable-pulsar-486209-b5/assets';

var CONFIG = {
  studyAreaAsset: CLOUD_PROJECT + '/study_area_odisha_8districts',
  ibtracsAsset:   CLOUD_PROJECT + '/ibtracs_NI_2014_2024',

  trackBufferKm:    50,
  cycloneFloodWindow: 15,        // days before/after landfall

  cyclones: {
    fani:   {year: 2019, landfall: '2019-05-03', name: 'Fani'},
    amphan: {year: 2020, landfall: '2020-05-20', name: 'Amphan'},
    yaas:   {year: 2021, landfall: '2021-05-26', name: 'Yaas'}
  },

  // OSF §E5 polygon-count targets per cyclone
  targets: {saline: 50, agro: 30, neither: 30},

  nicfiCollection: 'projects/planet-nicfi/assets/basemaps/asia'
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

print('=== Module 02b : NICFI label digitisation ===');
print('Cyclone:', cyc.name, YEAR, ' Landfall:', cyc.landfall);
print('Pre-NICFI window :', preStart.format('YYYY-MM-dd').getInfo(),
      '→', preEnd.format('YYYY-MM-dd').getInfo());
print('Post-NICFI window:', postStart.format('YYYY-MM-dd').getInfo(),
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
// 3. NICFI MOSAICS (PRE / POST)
// =============================================================================

var nicfi = ee.ImageCollection(CONFIG.nicfiCollection);

function nicfiMosaic(start, end) {
  return nicfi.filterDate(start, end).filterBounds(aoi).mosaic();
}

var nicfiPre  = nicfiMosaic(preStart,  preEnd);
var nicfiPost = nicfiMosaic(postStart, postEnd);

// NICFI true-colour stretch: B G R scaled 64-5454 -> 0-1
var rgbVis = {bands: ['R','G','B'], min: 64, max: 5454, gamma: 1.8};

// =============================================================================
// 4. SENTINEL-1 VH LANDFALL COMPOSITE  (visual reference for SAR signature)
// =============================================================================

var s1 = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(aoi)
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
  .filter(ee.Filter.eq('instrumentMode', 'IW'))
  .filterDate(landfallDate.advance(-CONFIG.cycloneFloodWindow, 'day'),
              landfallDate.advance( CONFIG.cycloneFloodWindow, 'day'));

var vhMin = s1.select('VH').min().rename('VH_landfall_min');

// =============================================================================
// 5. SENTINEL-2 NDWI/NDVI POST-CYCLONE (for water/vegetation context)
// =============================================================================

var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(aoi)
  .filterDate(postStart, postEnd)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30));

var s2Median = s2.median();
var ndwi = s2Median.normalizedDifference(['B3','B8']).rename('NDWI');
var ndvi = s2Median.normalizedDifference(['B8','B4']).rename('NDVI');

// =============================================================================
// 6. CROPLAND + IBTrACS REFERENCE LAYERS
// =============================================================================

var cropland = ee.ImageCollection('ESA/WorldCover/v200').first().eq(40)
                .selfMask().rename('cropland');

// =============================================================================
// 7. MAP SETUP
// =============================================================================

Map.centerObject(aoi, 9);
Map.setOptions('SATELLITE');

Map.addLayer(nicfiPre,  rgbVis, 'NICFI PRE  ('  + cyc.name + ')',  true);
Map.addLayer(nicfiPost, rgbVis, 'NICFI POST (' + cyc.name + ')',  true);
Map.addLayer(vhMin, {min: -25, max: -5, palette: ['000000','ffffff']},
             'S1 VH min (landfall ±15d)', false);
Map.addLayer(ndwi, {min: -0.3, max: 0.6, palette: ['ffffff','00bfff','000080']},
             'S2 NDWI post (cloud-free median)', false);
Map.addLayer(ndvi, {min: 0,    max: 0.9, palette: ['ffffff','c2e699','238443']},
             'S2 NDVI post (cloud-free median)', false);
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
// Each is created by clicking the import name + 'Geometry' in the panel.
// They become global vars with those exact names; the script reads them below.

var salineName  = 'saline_'  + YEAR;
var agroName    = 'agro_'    + YEAR;
var neitherName = 'neither_' + YEAR;

// Read from the global namespace via this(); polygons are added by the user.
function safeGet(name) {
  try {
    var g = this[name];        // bound at top-level scope by GeometryImport
    return ee.Algorithms.If(g, ee.FeatureCollection(g), ee.FeatureCollection([]));
  } catch (e) {
    return ee.FeatureCollection([]);
  }
}

// In the Code Editor, named GeometryImports become global symbols.
// We can't dynamically resolve them by string -> use the literal names below.
// If a polygon import does not yet exist, comment out its line (otherwise the
// script throws ReferenceError before any other code can run).
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
      cyclone:     cyc.name,
      year:        YEAR,
      label:       classLabel,
      operator:    'pandasupranab',
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
  var assetId = CLOUD_PROJECT + '/nicfi_labels_' + YEAR;
  Export.table.toAsset({
    collection:  allLabels,
    description: 'nicfi_labels_' + YEAR,
    assetId:     assetId
  });
  print('EXPORT_LABELS=true ➜ task dispatched: nicfi_labels_' + YEAR);
  print('Open Tasks tab and click Run.');
} else {
  print('EXPORT_LABELS=false — set to true once polygon counts meet targets.');
}

print('================================================');
print('Module 02b session loaded for', cyc.name, YEAR, '.');
print('Toggle NICFI POST + S1 VH + 50km buffer to draw polygons.');
print('================================================');

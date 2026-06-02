/**
 * RiceBaCI-GEE — Module 05 (v2 prep): Point-click label collector
 * ---------------------------------------------------------------------------
 * Author:   Supranab Panda (PhD scholar, Center for Environment and Climate,
 *           ITER, Siksha 'O' Anusandhan University, Bhubaneswar)
 *           pandasupranab@gmail.com
 * Project:  Decoupling Cyclone-Induced Saline Inundation from Agronomic
 *           Flooding in Sentinel-1/2 Rice Phenology Retrieval
 * Target:   Remote Sensing of Environment (Elsevier, zero-APC compliant)
 * OSF:      https://osf.io/c4mp8  (DOI 10.17605/OSF.IO/C4MP8)
 *           Implements the v2 transition: replace synthetic-label Module 02
 *           training data with 480 real Sentinel-2 visual reference labels
 *           drawn under the §E5 fallback path.
 *
 * ---------------------------------------------------------------------------
 * RELATIONSHIP TO MODULE 02b
 * ---------------------------------------------------------------------------
 * Module 02b (gee/02b_s2_label_digitisation.js) is the full polygon-based
 * digitiser with OSF polygon-count targets (saline ≥ 50, agro ≥ 30,
 * neither ≥ 30 per cyclone) and exports to a GEE Cloud asset.
 *
 * Module 05 (this script) is a streamlined POINT-CLICK companion that:
 *   - collects 480 single-pixel labels (240 cyclone_flood + 240 agronomic_flood)
 *   - exports a CSV to your Google Drive (much easier to hand back to me)
 *   - lets you label in three short sessions across the three cyclones
 *
 * BOTH WORKFLOWS ARE VALID. Polygons give the classifier more pixels per
 * label (better training); points are faster and easier for a first session.
 * If you have time for both, run 02b after 05 — the polygon labels will
 * augment the point labels and lift F1 further.
 *
 * ---------------------------------------------------------------------------
 * HOW TO USE — 6-STEP RECIPE
 * ---------------------------------------------------------------------------
 *  1. Open https://code.earthengine.google.com in Chrome/Edge.
 *  2. Paste this entire file into a new Code Editor script. Save it as
 *     "05_label_collector_v2" inside the RiceBaCI-GEE Cloud project.
 *  3. Edit the USER SETTINGS block below: set CYCLONE_ID to 'fani'
 *     (start with Fani 2019 because the surge footprint is clearest).
 *     Set CLASS_NAME to 'cyclone_flood'.
 *  4. Click Run. Wait ~30 s for tiles to load.
 *  5. Click ~80 points on the map where you see clear saline storm-surge
 *     water (see Visual Key PDF). Each click adds a Feature to the imports
 *     panel under the variable name pts_cyclone_flood (auto-created).
 *  6. When done with this class, set EXPORT_NOW = true and click Run.
 *     A task appears in the Tasks tab — click Run to send a CSV to your
 *     Drive folder named RiceBaCI_labels_<cyclone>_<class>_<YYYY-MM-DD>.csv.
 *
 * Repeat for the 5 remaining combinations (3 cyclones × 2 classes − the
 * one you just did = 5):
 *   fani   × agronomic_flood
 *   amphan × cyclone_flood
 *   amphan × agronomic_flood
 *   yaas   × cyclone_flood
 *   yaas   × agronomic_flood
 *
 * Aim for ~80 cyclone_flood points per cyclone × 3 cyclones = 240,
 * and ~80 agronomic_flood points per cyclone × 3 cyclones = 240.
 * Total = 480 points. ~30 sec/point → ~4 hours of focused work,
 * splittable across 2-3 sessions.
 *
 * After all 6 CSVs are in Drive, download them, ZIP them, and upload
 * the ZIP to me. I will run scripts/validate_label_panel.py and then
 * retrain Module 02.
 * ---------------------------------------------------------------------------
 */

// =============================================================================
// 1. CONFIGURATION
// =============================================================================

var CLOUD_PROJECT = 'projects/durable-pulsar-486209-b5/assets';

var CONFIG = {
  studyAreaAsset: CLOUD_PROJECT + '/study_area_odisha_8districts',
  ibtracsAsset:   CLOUD_PROJECT + '/ibtracs_NI_2014_2024',

  trackBufferKm:    50,
  cycloneFloodWindow: 15,

  cyclones: {
    fani:   {year: 2019, landfall: '2019-05-03', name: 'Fani'},
    amphan: {year: 2020, landfall: '2020-05-20', name: 'Amphan'},
    yaas:   {year: 2021, landfall: '2021-05-26', name: 'Yaas'}
  },

  // Per-class point target per cyclone
  targetsPerCycloneClass: 80,

  s2CloudPctMax:  60,
  s2CloudProbMax: 40
};

// ----------------------------------------------------------------------------
// USER SETTINGS — change these for each labeling session
// ----------------------------------------------------------------------------
var CYCLONE_ID  = 'fani';                // 'fani' | 'amphan' | 'yaas'
var CLASS_NAME  = 'cyclone_flood';       // 'cyclone_flood' | 'agronomic_flood'
var EXPORT_NOW  = false;                 // set true once you have ~80 points
// ----------------------------------------------------------------------------

var cyc = CONFIG.cyclones[CYCLONE_ID];
if (!cyc) { throw new Error('Unknown CYCLONE_ID: ' + CYCLONE_ID); }
var YEAR = cyc.year;
var landfallDate = ee.Date(cyc.landfall);

// Cyclone-flood points come from POST-landfall window (landfall to +15 days).
// Agronomic-flood points come from the standard transplanting flood window
// (July 1 to August 31 of the SAME year, AWAY from the cyclone track).
var floodStart, floodEnd;
if (CLASS_NAME === 'cyclone_flood') {
  floodStart = landfallDate;
  floodEnd   = landfallDate.advance(15, 'day');
} else if (CLASS_NAME === 'agronomic_flood') {
  floodStart = ee.Date.fromYMD(YEAR, 7, 1);
  floodEnd   = ee.Date.fromYMD(YEAR, 8, 31);
} else {
  throw new Error('CLASS_NAME must be cyclone_flood or agronomic_flood');
}

print('=== Module 05 v2: point-click label collector ===');
print('Cyclone:', cyc.name, YEAR, '  Landfall:', cyc.landfall);
print('Class:', CLASS_NAME);
print('Flood window:', floodStart.format('YYYY-MM-dd').getInfo(),
      '→', floodEnd.format('YYYY-MM-dd').getInfo());
print('Target: ~' + CONFIG.targetsPerCycloneClass + ' points');

// =============================================================================
// 2. STUDY AREA + CYCLONE TRACK BUFFER
// =============================================================================

var studyAreaFC = ee.FeatureCollection(CONFIG.studyAreaAsset);
var fullAOI = studyAreaFC.geometry();
var coastalAOI = studyAreaFC.filter(ee.Filter.inList('ADM2_NAME',
    ['Baleshwar','Bhadrak','Kendrapara','Jagatsinghpur','Puri']));

var ibtracs = ee.FeatureCollection(CONFIG.ibtracsAsset);
var thisTrack = ibtracs.filter(ee.Filter.eq('SEASON', YEAR));
var trackBuf  = thisTrack.geometry().buffer(CONFIG.trackBufferKm * 1000);

// =============================================================================
// 3. SENTINEL-2 CLOUD-FREE COMPOSITE
// =============================================================================

function maskS2sr(image) {
  var scl = image.select('SCL');
  var cloudShadow = scl.eq(3);
  var cloudMed    = scl.eq(8);
  var cloudHigh   = scl.eq(9);
  var cirrus      = scl.eq(10);
  var snow        = scl.eq(11);
  var mask = cloudShadow.or(cloudMed).or(cloudHigh).or(cirrus).or(snow).not();
  return image.updateMask(mask).divide(10000);
}

var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(fullAOI)
  .filterDate(floodStart, floodEnd)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', CONFIG.s2CloudPctMax))
  .map(maskS2sr);

var s2Median = s2.median().clip(fullAOI);

// Salinity Index SI = (B11 − B12) / (B11 + B12)
var SI = s2Median.expression(
  '(B11 - B12) / (B11 + B12)',
  {B11: s2Median.select('B11'), B12: s2Median.select('B12')}
).rename('SI');

var NDWI = s2Median.normalizedDifference(['B3','B8']).rename('NDWI');
var NDVI = s2Median.normalizedDifference(['B8','B4']).rename('NDVI');

// =============================================================================
// 4. SENTINEL-1 VH BACKSCATTER (truth for water under cloud)
// =============================================================================

var s1 = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(fullAOI)
  .filterDate(floodStart, floodEnd)
  .filter(ee.Filter.eq('instrumentMode', 'IW'))
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
  .select('VH');

var s1Median = s1.median().clip(fullAOI);

// =============================================================================
// 5. CROPLAND MASK (ESA WorldCover 2021)
// =============================================================================

var worldCover = ee.ImageCollection('ESA/WorldCover/v200').first();
var cropland = worldCover.eq(40).selfMask();

// =============================================================================
// 6. MAP VISUALISATION
// =============================================================================

Map.centerObject(coastalAOI, 8);

// True-colour RGB (best for spotting flood water)
Map.addLayer(s2Median.select(['B4','B3','B2']),
  {min: 0, max: 0.30, gamma: 1.3},
  'S2 RGB true-colour ' + cyc.name, true);

// False-colour (SWIR/NIR/Red) — flood = dark blue, healthy crop = bright green
Map.addLayer(s2Median.select(['B11','B8','B4']),
  {min: 0, max: 0.45, gamma: 1.2},
  'S2 false-colour SWIR/NIR/Red ' + cyc.name, false);

// NDWI — water highlight
Map.addLayer(NDWI, {min: -0.3, max: 0.6, palette: ['440154','3b528b','21918c','5ec962','fde725']},
  'S2 NDWI', false);

// Salinity Index — bright = salt-affected
Map.addLayer(SI, {min: -0.2, max: 0.2, palette: ['2166ac','67a9cf','f7f7f7','ef8a62','b2182b']},
  'S2 Salinity Index (SI)', false);

// S1 VH backscatter — water is very dark
Map.addLayer(s1Median, {min: -25, max: -5, palette: ['000000','555555','ffffff']},
  'S1 VH (dB)', false);

// Cropland mask
Map.addLayer(cropland, {palette: ['ff8c00']}, 'Cropland (WorldCover 2021)', false, 0.4);

// Cyclone track + 50 km buffer (only useful for cyclone_flood class)
if (CLASS_NAME === 'cyclone_flood') {
  Map.addLayer(ee.Image().paint(thisTrack, 1, 2), {palette: ['A12C7B']},
    cyc.name + ' track', true);
  Map.addLayer(ee.Image().paint(ee.Feature(trackBuf), 1, 1), {palette: ['A12C7B']},
    '50 km track buffer', true);
}

Map.addLayer(ee.Image().paint(coastalAOI, 1, 2), {palette: ['01696F']},
  'Coastal districts', true);

// =============================================================================
// 7. POINT-CLICK INSTRUCTIONS (banner)
// =============================================================================

print('');
print('========= HOW TO DRAW POINTS =========');
print('1. In the top-left of the map, find the Geometry Tools icon (square+pen).');
print('2. Click "+ new layer".');
print('3. Set Geometry type = Point, Color = ' +
      (CLASS_NAME === 'cyclone_flood' ? 'red (#A12C7B)' : 'gold (#FFD700)') + '.');
print('4. Rename the import variable to: pts_' + CLASS_NAME);
print('5. Start clicking pixels that match the Visual Key for "' + CLASS_NAME + '".');
print('   Aim for ~' + CONFIG.targetsPerCycloneClass + ' points.');
print('======================================');
print('');

// =============================================================================
// 8. STAMP METADATA + EXPORT
// =============================================================================

// Try to read the auto-created geometry variable.
var pts = null;
try {
  if (CLASS_NAME === 'cyclone_flood' && typeof pts_cyclone_flood !== 'undefined') {
    pts = pts_cyclone_flood;
  } else if (CLASS_NAME === 'agronomic_flood' && typeof pts_agronomic_flood !== 'undefined') {
    pts = pts_agronomic_flood;
  }
} catch (e) {
  // first run before user has created the geometry — fine
}

if (pts) {
  var fc = ee.FeatureCollection(pts).map(function (f) {
    var coords = f.geometry().coordinates();
    return f.set({
      lon:          ee.Number(coords.get(0)),
      lat:          ee.Number(coords.get(1)),
      class_name:   CLASS_NAME,
      class_id:     CLASS_NAME === 'cyclone_flood' ? 2 : 1,
      cyclone:      cyc.name,
      year:         YEAR,
      landfall:     cyc.landfall,
      operator:     'pandasupranab',
      imagery:      'S2_SR_HARMONIZED_median',
      window_start: floodStart.format('YYYY-MM-dd'),
      window_end:   floodEnd.format('YYYY-MM-dd'),
      labeled_on:   ee.Date(Date.now()).format('YYYY-MM-dd')
    });
  });

  print('--- Points in this session (' + CLASS_NAME + ', ' + cyc.name + ') ---');
  print('Count:', fc.size(), '   target ≈', CONFIG.targetsPerCycloneClass);

  // Render the points on the map for confirmation
  Map.addLayer(fc,
    {color: CLASS_NAME === 'cyclone_flood' ? 'A12C7B' : 'FFD700'},
    'Points: ' + CLASS_NAME + ' (' + cyc.name + ')', true);

  if (EXPORT_NOW) {
    var fname = 'RiceBaCI_labels_' + CYCLONE_ID + '_' + CLASS_NAME + '_' +
                ee.Date(Date.now()).format('YYYY-MM-dd').getInfo();
    Export.table.toDrive({
      collection:    fc,
      description:   fname,
      folder:        'RiceBaCI_labels',
      fileNamePrefix: fname,
      fileFormat:    'CSV',
      selectors: ['lon','lat','class_name','class_id','cyclone','year',
                  'landfall','operator','imagery','window_start',
                  'window_end','labeled_on']
    });
    print('EXPORT_NOW=true ➜ task dispatched: ' + fname + '.csv');
    print('Open Tasks tab (right side) and click Run.');
    print('The CSV will land in your Drive at: /RiceBaCI_labels/' + fname + '.csv');
  } else {
    print('EXPORT_NOW=false — set to true once you have ~' +
          CONFIG.targetsPerCycloneClass + ' points.');
  }
} else {
  print('No points drawn yet for ' + CLASS_NAME + '.');
  print('Use Geometry Tools to create an import named: pts_' + CLASS_NAME);
}

print('================================================');
print('Module 05 v2 loaded for', cyc.name, YEAR, 'class=' + CLASS_NAME + '.');
print('================================================');

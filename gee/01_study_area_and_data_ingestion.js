/* ============================================================================
 * RiceBaCI-GEE — Module 01: Study Area & Data Ingestion
 * ============================================================================
 *
 * Author:        Supranab Panda  (ORCID 0009-0009-6496-6545)
 * Supervisor:    Dr. Sarat Chandra Sahu  (ORCID 0000-0002-8048-1910)
 * Affiliation:   Center for Environment and Climate, Institute of Technical
 *                Education and Research, Siksha 'O' Anusandhan University,
 *                Bhubaneswar 751030, Odisha, India
 * Repository:    https://github.com/pandasupranab/RiceBaCI-GEE
 * Pre-reg:       https://osf.io/[OSF-id-pending]
 * Licence:       MIT
 *
 * What this script does
 * ---------------------
 *   1. Defines the study area: 5 coastal Odisha districts (treatment) and
 *      3 inland controls.
 *   2. Loads the rice cropland mask: ESA WorldCover 2021 cropland intersected
 *      with Singha et al. (2019) South Asia paddy mask.
 *   3. Loads IBTrACS cyclone tracks for the North Indian Ocean basin
 *      (2014–2024 — covers Hudhud transferability test plus main study window).
 *   4. Loads Sentinel-1 GRD, Sentinel-2 SR, JRC Global Surface Water,
 *      ERA5-Land, and MODIS MCD12Q2 (lazy collections — no compute yet).
 *   5. Visualises the study area on the map.
 *   6. Prints summary statistics to the Console.
 *
 * What you must edit before running
 * ---------------------------------
 *   - IBTRACS_ASSET (line ~50): Replace 'users/PLACEHOLDER/ibtracs_NI_2014_2024'
 *     with the actual asset path you uploaded in Week 1, Wednesday.
 *
 * Expected runtime:  30–60 seconds.
 * Expected outputs:  Map layers + console log. No image exports yet.
 * ========================================================================== */

// ============================================================================
// 1. CONFIGURATION
// ============================================================================

// IBTrACS asset (uploaded as Shapefile, 49 NI-basin tracks 2014-2024,
// pre-filtered to <500 km of study-area centroid, see scripts/prepare_ibtracs.py)
var IBTRACS_ASSET = 'projects/durable-pulsar-486209-b5/assets/ibtracs_NI_2014_2024';

var STUDY_PERIOD = {
  start: '2017-01-01',
  end:   '2024-12-31'
};

// 5 coastal Odisha districts (treatment)
var COASTAL_DISTRICTS = [
  'Baleshwar',     // Balasore
  'Bhadrak',
  'Kendrapara',
  'Jagatsinghpur',
  'Puri'
];

// 3 inland Odisha districts (control)
var INLAND_DISTRICTS = [
  'Dhenkanal',
  'Angul',
  'Cuttack'
];

var ALL_DISTRICTS = COASTAL_DISTRICTS.concat(INLAND_DISTRICTS);

// ============================================================================
// 2. STUDY AREA — DISTRICT BOUNDARIES (FAO GAUL Level-2)
// ============================================================================

var gaul = ee.FeatureCollection('FAO/GAUL/2015/level2');

var odisha = gaul
  .filter(ee.Filter.eq('ADM0_NAME', 'India'))
  .filter(ee.Filter.eq('ADM1_NAME', 'Orissa'));

var coastal = odisha
  .filter(ee.Filter.inList('ADM2_NAME', COASTAL_DISTRICTS))
  .map(function (f) { return f.set('ZONE', 'coastal'); });

var inland = odisha
  .filter(ee.Filter.inList('ADM2_NAME', INLAND_DISTRICTS))
  .map(function (f) { return f.set('ZONE', 'inland'); });

var studyArea = coastal.merge(inland);
var studyAreaGeom = studyArea.geometry();

// ============================================================================
// 3. RICE CROPLAND MASK
// ============================================================================

// 3.1 ESA WorldCover 2021 — cropland class (40)
var worldcover  = ee.ImageCollection('ESA/WorldCover/v200').first();
var cropland    = worldcover.eq(40).selfMask().rename('cropland');

// 3.2 JRC Global Surface Water — water permanence (used downstream for masking)
var jrcWater = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence');
var permanentWater = jrcWater.gte(80);  // ≥ 80 % occurrence
var nonWater       = permanentWater.unmask(0).not();

// 3.3 Combined rice candidate mask (cropland AND not permanent water)
var riceCandidate = cropland.updateMask(nonWater).rename('rice_candidate');

// (Singha 2019 South Asia paddy mask is added in Module 02 once we have
//  authenticated access to the ee.Image asset; for now we use cropland alone.)

// ============================================================================
// 4. CYCLONE TRACKS
// ============================================================================

// Note: shapefile column names are lowercase + 10-char limit
// (season, name, min_dist, max_wind, start_t, end_t, sid, n_fixes)
var ibtracs;
try {
  ibtracs = ee.FeatureCollection(IBTRACS_ASSET)
    .filter(ee.Filter.gte('season', 2014))
    .filter(ee.Filter.lte('season', 2024));
} catch (e) {
  print('WARNING: IBTrACS asset not found at:', IBTRACS_ASSET);
  print('  Verify upload at projects/durable-pulsar-486209-b5/assets/');
  ibtracs = ee.FeatureCollection([]);
}

// Pre-registered cyclone events (used in BACI as treatment years)
var preRegEvents = ibtracs.filter(
  ee.Filter.inList('name', ['Fani', 'Amphan', 'Yaas']));
var transferTest = ibtracs.filter(ee.Filter.eq('name', 'Hudhud'));
var strongStorms = ibtracs.filter(ee.Filter.gte('max_wind', 64));

// Major cyclones during the study window (manual list, used for visualisation)
var KEY_CYCLONES = [
  { name: 'Hudhud',  date: '2014-10-12', lat: 17.7, lon: 83.3 },  // transferability
  { name: 'Fani',    date: '2019-05-03', lat: 20.0, lon: 86.0 },
  { name: 'Bulbul',  date: '2019-11-09', lat: 21.0, lon: 88.5 },
  { name: 'Amphan',  date: '2020-05-20', lat: 21.7, lon: 88.0 },
  { name: 'Yaas',    date: '2021-05-26', lat: 21.5, lon: 87.0 }
];

var cyclonePoints = ee.FeatureCollection(
  KEY_CYCLONES.map(function (c) {
    return ee.Feature(ee.Geometry.Point([c.lon, c.lat]), {
      name: c.name,
      date: c.date
    });
  })
);

// ============================================================================
// 5. SATELLITE & REANALYSIS COLLECTIONS (lazy — no compute yet)
// ============================================================================

var s1 = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterDate(STUDY_PERIOD.start, STUDY_PERIOD.end)
  .filterBounds(studyAreaGeom)
  .filter(ee.Filter.eq('instrumentMode', 'IW'))
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'));

var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterDate(STUDY_PERIOD.start, STUDY_PERIOD.end)
  .filterBounds(studyAreaGeom)
  .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', 80));

var era5 = ee.ImageCollection('ECMWF/ERA5_LAND/HOURLY')
  .filterDate(STUDY_PERIOD.start, STUDY_PERIOD.end)
  .filterBounds(studyAreaGeom);

var modisPheno = ee.ImageCollection('MODIS/061/MCD12Q2')
  .filterDate(STUDY_PERIOD.start, STUDY_PERIOD.end);

// ============================================================================
// 6. VISUALISATION
// ============================================================================

Map.centerObject(studyAreaGeom, 7);

// Country/state context (subtle)
Map.addLayer(odisha,
  { color: 'BBBBBB' },
  'Odisha (all districts)', false, 0.3);

// Coastal districts — orange
Map.addLayer(coastal,
  { color: 'E15A1A' },
  'Coastal districts (treatment)', true, 0.5);

// Inland districts — green
Map.addLayer(inland,
  { color: '2E7D32' },
  'Inland districts (control)', true, 0.5);

// Rice cropland mask
Map.addLayer(riceCandidate.clip(studyAreaGeom),
  { palette: ['B5E48C'] },
  'Rice cropland candidate', true, 0.7);

// Cyclone landfall points
Map.addLayer(cyclonePoints,
  { color: 'D32F2F' },
  'Cyclone landfalls (Hudhud, Fani, Bulbul, Amphan, Yaas)', true);

// Cyclone tracks: all 49 NI-basin tracks (faint), strong cyclones, pre-reg events, transferability test
Map.addLayer(ibtracs,
  { color: 'BAB9B4' },
  'All NI tracks 2014-2024 (49)', true, 0.4);
Map.addLayer(strongStorms,
  { color: 'A12C7B' },
  'Cyclone-strength tracks (>=64 kt, 9)', true, 0.7);
Map.addLayer(preRegEvents,
  { color: 'FF6F00' },
  'Pre-registered: Fani, Amphan, Yaas', true, 1.0);
Map.addLayer(transferTest,
  { color: '7A39BB' },
  'Transferability test: Hudhud 2014', true, 0.8);

// Outline of the entire study area
Map.addLayer(
  ee.Image().paint(studyArea, 1, 2),
  { palette: '000000' },
  'Study area outline', true);

// ============================================================================
// 7. SUMMARY STATISTICS (printed to Console)
// ============================================================================

print('================================================');
print('RiceBaCI-GEE Module 01: Study Area Assembly');
print('================================================');
print('');
print('Study period:', STUDY_PERIOD.start, '→', STUDY_PERIOD.end);
print('');
print('Districts:');
print('  Coastal (treatment):', COASTAL_DISTRICTS);
print('  Inland (control):',    INLAND_DISTRICTS);
print('');

// Pixel counts (approximate, server-side)
var ricePixels = riceCandidate.reduceRegion({
  reducer: ee.Reducer.count(),
  geometry: studyAreaGeom,
  scale: 100,
  maxPixels: 1e10
});
print('Approx. rice candidate pixels (100 m grid):', ricePixels);

// Image counts
print('Sentinel-1 GRD scenes available:', s1.size());
print('Sentinel-2 SR scenes available:',  s2.size());
print('ERA5-Land hourly slices:',         era5.size());
print('MODIS MCD12Q2 annual:',            modisPheno.size());
print('Cyclone track points (IBTrACS NI):', ibtracs.size());

// Geometry sanity
print('Study area total bounds:', studyAreaGeom.bounds());

// Export the study area as a GEE asset for use by downstream modules
Export.table.toAsset({
  collection: studyArea,
  description: 'export_study_area_v1',
  assetId:     'study_area_odisha_8districts'
});
print('');
print('  Run the export task ("Tasks" tab → Run) to save the study area');
print('  as a reusable asset for Modules 02–05.');
print('');
print('NEXT MODULE: 02_saline_flood_classifier.js');
print('  → Build the random-forest classifier features on this study area.');
print('================================================');

// ============================================================================
// END OF MODULE 01
// ============================================================================

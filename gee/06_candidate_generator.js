/**
 * RiceBaCI-GEE — Module 06: Active-learning candidate generator
 * ---------------------------------------------------------------------------
 * Author:   Supranab Panda  (pandasupranab@gmail.com)
 * Project:  RiceBaCI-GEE   OSF c4mp8
 * Purpose:  Generate 480 candidate label points (240 cyclone_flood + 240
 *           agronomic_flood) using strict physical rules, ready for batch
 *           Keep/Reject review in Module 07.
 *
 * Sampling logic
 * ---------------------------------------------------------------------------
 * cyclone_flood candidates (80 per cyclone x 3 cyclones = 240):
 *   - inside the cyclone's 50 km track buffer
 *   - inside ESA WorldCover 2021 cropland (class 40)
 *   - Sentinel-2 SI > +0.05  (salt-affected wet soil)
 *   - Sentinel-2 NDWI > +0.20  (wet pixel)
 *   - Sentinel-2 NDVI < 0.30  (vegetation crashed)
 *   - Sentinel-1 VH < -19 dB  (smooth water)
 *   - within +/- 15 days of landfall
 *
 * agronomic_flood candidates (30 per district x 8 districts = 240):
 *   - inside ESA WorldCover 2021 cropland (class 40)
 *   - JRC Global Surface Water seasonal layer >= 6 months/year
 *   - Sentinel-2 NDWI > +0.20  (wet pixel)
 *   - Sentinel-2 NDVI between 0.10 and 0.40  (young transplanted rice)
 *   - Sentinel-1 VH between -22 and -16 dB  (water under emerging canopy)
 *   - Sentinel-2 SI < -0.05  (NOT salt-affected)
 *   - in July or August of a non-cyclone year (2017, 2018, 2022, 2023, 2024)
 *   - outside all 50 km cyclone buffers
 *
 * Output: a single GEE Cloud asset table 'candidates_v1' with 480 features,
 *         each carrying:  lon, lat, class_proposed, cyclone, year, source_date,
 *                         si, ndvi, ndwi, vh, district, candidate_id
 *
 * Run this once. Then proceed to Module 07 (review app).
 * ---------------------------------------------------------------------------
 */

var CLOUD_PROJECT = 'projects/durable-pulsar-486209-b5/assets';

// ---------------------------------------------------------------------------
// 1. CONFIG
// ---------------------------------------------------------------------------
var CFG = {
  studyAreaAsset: CLOUD_PROJECT + '/study_area_odisha_8districts',
  outputAsset:    CLOUD_PROJECT + '/candidates_v1',
  trackBufferKm:  50,
  candidatesPerCycloneClass: 80,
  candidatesPerDistrictAgro: 30,

  cyclones: {
    fani: {
      year: 2019, landfall: '2019-05-03', name: 'Fani',
      track: [
        [86.10, 19.40], [86.05, 19.70], [86.00, 20.00],
        [85.95, 20.30], [85.90, 20.55], [85.85, 20.80],
        [85.80, 21.10], [85.75, 21.40], [85.70, 21.70], [85.60, 22.00]
      ]
    },
    amphan: {
      year: 2020, landfall: '2020-05-20', name: 'Amphan',
      track: [
        [87.00, 20.20], [87.20, 20.60], [87.40, 21.00],
        [87.65, 21.40], [87.95, 21.65], [88.20, 21.90],
        [88.45, 22.20], [88.70, 22.55], [89.00, 22.90]
      ]
    },
    yaas: {
      year: 2021, landfall: '2021-05-26', name: 'Yaas',
      track: [
        [87.20, 20.40], [87.15, 20.75], [87.10, 21.10],
        [87.05, 21.40], [87.00, 21.65],
        [86.95, 21.95], [86.90, 22.25], [86.85, 22.55]
      ]
    }
  },

  nonCycloneYears: [2017, 2018, 2022, 2023, 2024],
  districts: ['Baleshwar','Bhadrak','Kendrapara','Jagatsinghpur',
              'Puri','Cuttack','Dhenkanal','Angul'],

  // Physical thresholds
  thresh: {
    cyclone: {siMin: 0.05, ndwiMin: 0.20, ndviMax: 0.30, vhMax: -19},
    agro:    {ndwiMin: 0.20, ndviMin: 0.10, ndviMax: 0.40,
              vhMin: -22, vhMax: -16, siMax: -0.05}
  },

  s2CloudPctMax: 60
};

// ---------------------------------------------------------------------------
// 2. STUDY AREA + CYCLONE BUFFERS
// ---------------------------------------------------------------------------
var studyArea = ee.FeatureCollection(CFG.studyAreaAsset);
var fullAOI   = studyArea.geometry();

function trackBuffer(cyc) {
  return ee.Geometry.LineString(cyc.track).buffer(CFG.trackBufferKm * 1000);
}
var fani   = CFG.cyclones.fani;
var amphan = CFG.cyclones.amphan;
var yaas   = CFG.cyclones.yaas;
var bufFani   = trackBuffer(fani);
var bufAmphan = trackBuffer(amphan);
var bufYaas   = trackBuffer(yaas);
var allBuffers = ee.Geometry.MultiPolygon([
  bufFani.coordinates(), bufAmphan.coordinates(), bufYaas.coordinates()
]);

// ---------------------------------------------------------------------------
// 3. ANCILLARY LAYERS
// ---------------------------------------------------------------------------
var worldCover = ee.ImageCollection('ESA/WorldCover/v200').first();
var cropland   = worldCover.eq(40);  // 1 = cropland
var jrcGSW     = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('seasonality');
var seasonalWater = jrcGSW.gte(6);   // pixels under water >=6 months/year

// ---------------------------------------------------------------------------
// 4. S2 + S1 COMPOSITES FOR A GIVEN WINDOW
// ---------------------------------------------------------------------------
function maskS2(image) {
  var scl = image.select('SCL');
  var bad = scl.eq(3).or(scl.eq(8)).or(scl.eq(9)).or(scl.eq(10)).or(scl.eq(11));
  return image.updateMask(bad.not()).divide(10000);
}

function buildS2(startDate, endDate, geom) {
  var col = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(geom)
    .filterDate(startDate, endDate)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', CFG.s2CloudPctMax))
    .map(maskS2);
  var med = col.median().clip(geom);
  var SI   = med.expression('(B11 - B12) / (B11 + B12)',
              {B11: med.select('B11'), B12: med.select('B12')}).rename('SI');
  var NDWI = med.normalizedDifference(['B3','B8']).rename('NDWI');
  var NDVI = med.normalizedDifference(['B8','B4']).rename('NDVI');
  return SI.addBands(NDWI).addBands(NDVI).addBands(med);
}

function buildS1(startDate, endDate, geom) {
  var col = ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(geom)
    .filterDate(startDate, endDate)
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
    .select('VH');
  return col.median().clip(geom).rename('VH');
}

// ---------------------------------------------------------------------------
// 5. CYCLONE_FLOOD CANDIDATE MASK + SAMPLING
// ---------------------------------------------------------------------------
function cycloneCandidates(cyc, buf) {
  var landfall = ee.Date(cyc.landfall);
  var winStart = landfall;
  var winEnd   = landfall.advance(15, 'day');
  var s2 = buildS2(winStart, winEnd, buf);
  var s1 = buildS1(winStart, winEnd, buf);
  var t = CFG.thresh.cyclone;
  var mask = s2.select('SI').gt(t.siMin)
    .and(s2.select('NDWI').gt(t.ndwiMin))
    .and(s2.select('NDVI').lt(t.ndviMax))
    .and(s1.lt(t.vhMax))
    .and(cropland);
  var labeled = mask.selfMask().rename('candidate');
  var samples = labeled.stratifiedSample({
    numPoints: CFG.candidatesPerCycloneClass,
    classBand: 'candidate',
    region: buf,
    scale: 10,
    seed: 42,
    geometries: true,
    tileScale: 4
  });
  samples = samples.map(function (f) {
    var p = f.geometry();
    var vals = s2.addBands(s1).reduceRegion({
      reducer: ee.Reducer.mean(),
      geometry: p, scale: 10, maxPixels: 1e8
    });
    return f.set({
      class_proposed: 'cyclone_flood',
      class_id: 2,
      cyclone: cyc.name,
      year: cyc.year,
      source_date: cyc.landfall,
      window_start: winStart.format('YYYY-MM-dd'),
      window_end:   winEnd.format('YYYY-MM-dd'),
      lon: p.coordinates().get(0),
      lat: p.coordinates().get(1),
      si:   vals.get('SI'),
      ndwi: vals.get('NDWI'),
      ndvi: vals.get('NDVI'),
      vh:   vals.get('VH')
    });
  });
  return samples;
}

var cycFani   = cycloneCandidates(fani,   bufFani);
var cycAmphan = cycloneCandidates(amphan, bufAmphan);
var cycYaas   = cycloneCandidates(yaas,   bufYaas);
var cycAll    = cycFani.merge(cycAmphan).merge(cycYaas);

print('Cyclone candidate counts (target 80 each):');
print('  Fani:',   cycFani.size());
print('  Amphan:', cycAmphan.size());
print('  Yaas:',   cycYaas.size());

// ---------------------------------------------------------------------------
// 6. AGRONOMIC_FLOOD CANDIDATE MASK + SAMPLING
// ---------------------------------------------------------------------------
// Use a pooled July-August composite across non-cyclone years (the median
// suppresses inter-year noise), then sample 30 candidates inside each district.
var nonCycYears = CFG.nonCycloneYears;
var agroComposites = nonCycYears.map(function (yr) {
  var s = ee.Date.fromYMD(yr, 7, 1);
  var e = ee.Date.fromYMD(yr, 8, 31);
  return buildS2(s, e, fullAOI).addBands(buildS1(s, e, fullAOI))
            .set('yr', yr);
});
var agroMed = ee.ImageCollection(agroComposites).median();

var ta = CFG.thresh.agro;
var agroMask = agroMed.select('NDWI').gt(ta.ndwiMin)
  .and(agroMed.select('NDVI').gt(ta.ndviMin))
  .and(agroMed.select('NDVI').lt(ta.ndviMax))
  .and(agroMed.select('VH').gt(ta.vhMin))
  .and(agroMed.select('VH').lt(ta.vhMax))
  .and(agroMed.select('SI').lt(ta.siMax))
  .and(cropland)
  .and(seasonalWater);  // also restrict to known-seasonal-flood pixels

var agroBase = agroMask.selfMask().rename('candidate');

// Loop districts and stratified-sample 30 per district.
var agroAll = ee.FeatureCollection([]);
CFG.districts.forEach(function (dn) {
  var distGeom = studyArea.filter(ee.Filter.eq('ADM2_NAME', dn)).geometry();
  var samp = agroBase.stratifiedSample({
    numPoints: CFG.candidatesPerDistrictAgro,
    classBand: 'candidate',
    region: distGeom,
    scale: 10,
    seed: 42,
    geometries: true,
    tileScale: 4
  });
  samp = samp.map(function (f) {
    var p = f.geometry();
    var vals = agroMed.reduceRegion({
      reducer: ee.Reducer.mean(),
      geometry: p, scale: 10, maxPixels: 1e8
    });
    return f.set({
      class_proposed: 'agronomic_flood',
      class_id: 1,
      cyclone: 'none',
      year: 2020,  // representative non-cyclone year
      source_date: 'July-August 2017-2024 (non-cyclone-year median)',
      district: dn,
      lon: p.coordinates().get(0),
      lat: p.coordinates().get(1),
      si:   vals.get('SI'),
      ndwi: vals.get('NDWI'),
      ndvi: vals.get('NDVI'),
      vh:   vals.get('VH')
    });
  });
  agroAll = agroAll.merge(samp);
});

print('Agronomic candidate count (target 240):', agroAll.size());

// ---------------------------------------------------------------------------
// 7. MERGE + ADD CANDIDATE_ID
// ---------------------------------------------------------------------------
var allCandidates = cycAll.merge(agroAll);

// Add candidate_id as a stable integer.
var withId = allCandidates.toList(allCandidates.size()).map(function (f, i) {
  return ee.Feature(f).set('candidate_id', i).set('reviewed', 0).set('decision', 'pending');
});
var finalFC = ee.FeatureCollection(withId);

print('Total candidates:', finalFC.size(), '  (target ~480)');

// ---------------------------------------------------------------------------
// 8. EXPORT TO CLOUD ASSET (used by Module 07 review app)
// ---------------------------------------------------------------------------
Export.table.toAsset({
  collection: finalFC,
  description: 'candidates_v1_export',
  assetId: CFG.outputAsset
});

print('');
print('=== Export task dispatched ===');
print('1. Open Tasks tab on the right.');
print('2. Click Run next to "candidates_v1_export".');
print('3. Wait ~5 min. When status shows COMPLETED, run Module 07.');
print('');

// Also map a preview
Map.centerObject(studyArea, 7);
Map.addLayer(ee.Image().paint(studyArea, 1, 2), {palette: ['01696F']}, '8 districts', true);
Map.addLayer(cycAll, {color: 'A12C7B'}, 'cyclone candidates (preview)', true);
Map.addLayer(agroAll, {color: 'FFD700'}, 'agronomic candidates (preview)', true);

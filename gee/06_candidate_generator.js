/**
 * RiceBaCI-GEE — Module 06: Active-learning candidate generator
 * ---------------------------------------------------------------------------
 * Author:   Supranab Panda  (pandasupranab@gmail.com)
 * Project:  RiceBaCI-GEE   OSF c4mp8
 * Purpose:  Generate 480 candidate label points (240 cyclone_flood + 240
 *           agronomic_flood) using strict physical rules, ready for batch
 *           Keep/Reject review in Module 07.
 *
 * v2 patch (2026-06-07):
 *   - Empty-collection guard in buildS2 / buildS1 (returns dummy bands so
 *     downstream .normalizedDifference cannot crash).
 *   - Explicit .select() of B2/B3/B4/B8/B11/B12 before computing indices,
 *     so band metadata is preserved.
 *   - Agronomic composite now uses a SINGLE multi-year ImageCollection
 *     with ee.Filter.calendarRange(7, 8, 'month') and a year-list filter,
 *     so band metadata is never lost via JS-array reconstruction.
 *
 * Sampling logic (unchanged)
 * ---------------------------------------------------------------------------
 * cyclone_flood: 80 per cyclone x 3 = 240
 * agronomic_flood: 30 per district x 8 = 240
 * ---------------------------------------------------------------------------
 */

var CLOUD_PROJECT = 'projects/durable-pulsar-486209-b5/assets';

// ---------------------------------------------------------------------------
// 1. CONFIG
// ---------------------------------------------------------------------------
var CFG = {
  studyAreaAsset: CLOUD_PROJECT + '/study_area_odisha_8districts',
  outputAsset:    CLOUD_PROJECT + '/candidates_v3',  // v1/v2 = cyclone-only; v3 = S1-only agro + cyclone
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

  thresh: {
    cyclone: {siMin: 0.05, ndwiMin: 0.20, ndviMax: 0.30, vhMax: -19},
    // Agro v4: S1-ONLY mask. Diagnostic confirmed S2 is essentially absent
    // for coastal Odisha in July (0 scenes at CLOUD<60 in Jul 2018). Switch
    // to a radar-only definition of agronomic_flood:
    //   * inside ESA WorldCover cropland
    //   * S1 VH between -22 and -17 dB  (smooth shallow water under emerging
    //     canopy; below permanent open water and above dry land/canopy)
    //   * JRC seasonality in [1, 5] months/year (transient seasonal flooding,
    //     NOT permanent water bodies)
    agro:    {vhMin: -22, vhMax: -17, jrcMin: 1, jrcMax: 5}
  },

  s2CloudPctMax: 80  // raise from 60 to 80 to give cyclone S2 path more headroom
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

// ---------------------------------------------------------------------------
// 3. ANCILLARY LAYERS
// ---------------------------------------------------------------------------
var worldCover = ee.ImageCollection('ESA/WorldCover/v200').first();
var cropland   = worldCover.eq(40);  // 1 = cropland
var jrcGSW     = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('seasonality');
var seasonalWater = jrcGSW.gte(6);   // pixels under water >=6 months/year

// ---------------------------------------------------------------------------
// 4. S2 + S1 COMPOSITES — with empty-collection guards
// ---------------------------------------------------------------------------
// Bands we always want to be present, in this order, so .normalizedDifference
// cannot fail even when the input collection is empty.
var S2_BANDS = ['B2','B3','B4','B8','B11','B12'];

// A safe zero-image carrying the expected S2 bands. Used when a date window
// has zero usable scenes inside the AOI.
function dummyS2Image() {
  var z = ee.Image.constant(0).rename(S2_BANDS[0]);
  for (var i = 1; i < S2_BANDS.length; i++) {
    z = z.addBands(ee.Image.constant(0).rename(S2_BANDS[i]));
  }
  return z.toFloat();
}
function dummyS1Image() {
  return ee.Image.constant(-25).rename('VH').toFloat();  // very dry / no-data sentinel
}

function maskS2(image) {
  var scl = image.select('SCL');
  var bad = scl.eq(3).or(scl.eq(8)).or(scl.eq(9)).or(scl.eq(10)).or(scl.eq(11));
  return image.updateMask(bad.not()).divide(10000).select(S2_BANDS);
}

/**
 * Build a guarded S2 composite for the given window+geom.
 * Always returns an image with bands [SI, NDWI, NDVI, B2..B12], even when the
 * underlying ImageCollection is empty for that AOI/window.
 */
function buildS2(startDate, endDate, geom) {
  var col = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(geom)
    .filterDate(startDate, endDate)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', CFG.s2CloudPctMax))
    .map(maskS2);

  // Use ee.Algorithms.If so the guard runs server-side and band metadata is
  // preserved regardless of collection size.
  var med = ee.Image(ee.Algorithms.If(
    col.size().gt(0),
    col.median().select(S2_BANDS),
    dummyS2Image()
  ));

  var SI   = med.expression('(B11 - B12) / (B11 + B12 + 1e-6)',
              {B11: med.select('B11'), B12: med.select('B12')}).rename('SI');
  var NDWI = med.normalizedDifference(['B3','B8']).rename('NDWI');
  var NDVI = med.normalizedDifference(['B8','B4']).rename('NDVI');
  return SI.addBands(NDWI).addBands(NDVI).addBands(med).clip(geom);
}

function buildS1(startDate, endDate, geom) {
  var col = ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(geom)
    .filterDate(startDate, endDate)
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
    .select('VH');
  var med = ee.Image(ee.Algorithms.If(
    col.size().gt(0),
    col.median().rename('VH'),
    dummyS1Image()
  ));
  return med.clip(geom);
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
// 6. AGRONOMIC_FLOOD CANDIDATE — single multi-year July-Aug composite
// ---------------------------------------------------------------------------
// Build ONE ImageCollection that contains all July-August scenes from the
// non-cyclone years, then take its median. This avoids any JS array of
// per-year composites and preserves band metadata even if a single year is
// patchy.
var yearList = CFG.nonCycloneYears;
var yearStart = ee.Date.fromYMD(ee.Number(yearList[0]), 1, 1);
var yearEnd   = ee.Date.fromYMD(ee.Number(yearList[yearList.length - 1]), 12, 31);

// v4 strategy: S1-ONLY per-year July-August sampling.
//   Diagnostic showed July 2018 has ZERO S2 scenes <60% cloud in coastal
//   Odisha (the monsoon). S1 radar is unaffected by clouds. New mask:
//     inside cropland
//     + S1 VH in [-22, -17] dB  (smooth shallow water under emerging canopy)
//     + JRC seasonality in [1, 5] months  (transient, not permanent water)
//   For each non-cyclone year x district, sample 6 candidates.
//   Total = 5 yrs x 8 dists x 6 = 240.
var AGRO_SCALE = 30;
var ta = CFG.thresh.agro;
var agroAll = ee.FeatureCollection([]);
var PER_DISTRICT_PER_YEAR = 6;

// JRC seasonality soft-prior layer (1-5 months/year flooded = transient)
var jrcTransient = jrcGSW.gte(ta.jrcMin).and(jrcGSW.lte(ta.jrcMax));

CFG.nonCycloneYears.forEach(function (yr) {
  // July + August window (2 months of S1 scenes, more candidates)
  var winStart = ee.Date.fromYMD(yr, 7, 1);
  var winEnd   = ee.Date.fromYMD(yr, 8, 31);
  var s1 = buildS1(winStart, winEnd, fullAOI);

  // S1-only agronomic mask.
  var mask = s1.select('VH').gt(ta.vhMin)
    .and(s1.select('VH').lt(ta.vhMax))
    .and(cropland)
    .and(jrcTransient);

  var agroBase = mask.selfMask().rename('candidate');

  CFG.districts.forEach(function (dn) {
    var distGeom = studyArea.filter(ee.Filter.eq('ADM2_NAME', dn)).geometry();
    var samp = agroBase.stratifiedSample({
      numPoints: PER_DISTRICT_PER_YEAR,
      classBand: 'candidate',
      region: distGeom,
      scale: AGRO_SCALE,
      seed: 42 + yr,
      geometries: true,
      tileScale: 8
    });
    samp = samp.map(function (f) {
      var p = f.geometry();
      var vals = s1.reduceRegion({
        reducer: ee.Reducer.mean(),
        geometry: p, scale: AGRO_SCALE, maxPixels: 1e8
      });
      return f.set({
        class_proposed: 'agronomic_flood',
        class_id: 1,
        cyclone: 'none',
        year: yr,
        source_date: ee.String('Jul-Aug ').cat(ee.Number(yr).format('%d')),
        district: dn,
        lon: p.coordinates().get(0),
        lat: p.coordinates().get(1),
        si:   null,    // not computed (S2 unavailable in monsoon)
        ndwi: null,
        ndvi: null,
        vh:   vals.get('VH')
      });
    });
    agroAll = agroAll.merge(samp);
  });
});

print('Agronomic candidates (v4 S1-only): deferred to Export task (target 240).');

// ---------------------------------------------------------------------------
// 7. MERGE + ADD CANDIDATE_ID
// ---------------------------------------------------------------------------
var allCandidates = cycAll.merge(agroAll);

// Assign candidate_id 0..N-1 server-side.
// IMPORTANT: ee.List.map's callback MUST be single-argument (the index `i`
// parameter that some examples show is illegal and causes:
//   "List.map: A mapped algorithm must take one argument."
// So we zip a sequence of ids with the feature list and rebuild.
var featList = allCandidates.toList(allCandidates.size());
var idList   = ee.List.sequence(0, allCandidates.size().subtract(1));
var zipped   = idList.zip(featList);  // [[0, f0], [1, f1], ...]
var withId = zipped.map(function (pair) {
  pair = ee.List(pair);
  var id   = ee.Number(pair.get(0));
  var feat = ee.Feature(pair.get(1));
  return feat.set('candidate_id', id)
             .set('reviewed', 0)
             .set('decision', 'pending');
});
var finalFC = ee.FeatureCollection(withId);

// Skip eager .size() print for the same reason — the Export task will
// materialise all ~480 features.
print('Total candidates: deferred to Export task (target ~480).');

// ---------------------------------------------------------------------------
// 8. EXPORT TO CLOUD ASSET
// ---------------------------------------------------------------------------
Export.table.toAsset({
  collection: finalFC,
  description: 'candidates_v3_export',
  assetId: CFG.outputAsset
});

print('');
print('=== Export task dispatched ===');
print('1. Open Tasks tab on the right.');
print('2. Click Run next to "candidates_v3_export".');
print('3. Wait ~15 min. When status shows COMPLETED, run Module 07.');
print('');

// Preview — cyclone candidates only. The agronomic preview layer is omitted
// because rendering it would force the heavy pooled composite to compute
// interactively and hit the 5-min timeout. After Export completes, the
// `candidates_v1` asset itself can be added as a layer if you want a preview.
Map.centerObject(studyArea, 7);
Map.addLayer(ee.Image().paint(studyArea, 1, 2), {palette: ['01696F']}, '8 districts', true);
Map.addLayer(cycAll, {color: 'A12C7B'}, 'cyclone candidates (preview)', true);

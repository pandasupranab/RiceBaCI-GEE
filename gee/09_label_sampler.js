/**
 * RiceBaCI-GEE — Module 09: Final label panel sampler
 * ---------------------------------------------------------------------------
 * Author:   Supranab Panda  (pandasupranab@gmail.com)
 * Project:  RiceBaCI-GEE   OSF c4mp8
 * Purpose:  Produce the FINAL labels_panel_real.csv for Module 02 retraining.
 *           Combines three independent cyclone_flood sources + agronomic
 *           candidates from candidates_v3 into one ~480-row label panel.
 *
 * Inputs (must exist as Cloud assets first):
 *   projects/durable-pulsar-486209-b5/assets/fani_ems_flood   (5 multipolys,
 *      from Copernicus EMS EMSR357)
 *   projects/durable-pulsar-486209-b5/assets/amphan_s1_flood  (3,096 polys,
 *      auto-derived in Module 08)
 *   projects/durable-pulsar-486209-b5/assets/yaas_s1_flood    (7,779 polys,
 *      auto-derived in Module 08)
 *   projects/durable-pulsar-486209-b5/assets/candidates_v3    (480 candidates;
 *      we use only the 240 agronomic_flood rows)
 *   projects/durable-pulsar-486209-b5/assets/study_area_odisha_8districts
 *
 * Output:
 *   Drive CSV: labels_panel_real.csv
 *   Cloud asset: labels_panel_real
 *
 * Sampling design:
 *   cyclone_flood    : 80 per cyclone x 3 cyclones = 240 points (stratified
 *                      by Fani/Amphan/Yaas; sampled INSIDE flood polygons,
 *                      restricted to ESA cropland)
 *   agronomic_flood  : 240 points (taken directly from candidates_v3
 *                      where class_proposed == 'agronomic_flood')
 *   TOTAL            : 480 labels
 *
 * Each row has: lat, lon, class_proposed, class_id, cyclone, event_date,
 *               source, district, sampled at 10 m S2/S1 stack values.
 * ---------------------------------------------------------------------------
 */

var CLOUD_PROJECT = 'projects/durable-pulsar-486209-b5/assets';
var PER_CYCLONE_N = 80;  // 80 x 3 cyclones = 240 cyclone_flood points

// ---------------------------------------------------------------------------
// 1. INPUTS
// ---------------------------------------------------------------------------
var studyArea = ee.FeatureCollection(CLOUD_PROJECT + '/study_area_odisha_8districts');
var AOI       = studyArea.geometry();

var fani   = ee.FeatureCollection(CLOUD_PROJECT + '/fani_ems_flood');
var amphan = ee.FeatureCollection(CLOUD_PROJECT + '/amphan_s1_flood');
var yaas   = ee.FeatureCollection(CLOUD_PROJECT + '/yaas_s1_flood');

var candidatesV3 = ee.FeatureCollection(CLOUD_PROJECT + '/candidates_v3');

// Ancillary
var worldCover = ee.ImageCollection('ESA/WorldCover/v200').first();
var cropland   = worldCover.eq(40);

// ---------------------------------------------------------------------------
// 2. SAMPLE CYCLONE_FLOOD LABELS
// ---------------------------------------------------------------------------
function sampleCycloneLabels(footprint, cycloneLabel, eventDate, sourceLabel) {
  // Restrict the footprint to ESA cropland (we want rice flood, not urban flood)
  var floodMask = ee.Image.constant(1)
    .clip(footprint)
    .updateMask(cropland)
    .rename('flood');

  var samples = floodMask.stratifiedSample({
    numPoints: PER_CYCLONE_N,
    classBand: 'flood',
    region: AOI,
    scale: 30,
    seed: 42,
    geometries: true,
    tileScale: 8
  });

  samples = samples.map(function (f) {
    var p = f.geometry();
    return f.set({
      class_proposed: 'cyclone_flood',
      class_id: 2,
      cyclone: cycloneLabel,
      event_date: eventDate,
      source: sourceLabel,
      district: 'NA',
      lon: p.coordinates().get(0),
      lat: p.coordinates().get(1)
    });
  });
  return samples;
}

var fLabels = sampleCycloneLabels(fani,   'Fani',
  '2019-05-03', 'Copernicus EMS EMSR357');
var aLabels = sampleCycloneLabels(amphan, 'Amphan',
  '2020-05-20', 'Sentinel-1 SAR change detection (Module 08)');
var yLabels = sampleCycloneLabels(yaas,   'Yaas',
  '2021-05-26', 'Sentinel-1 SAR change detection (Module 08)');

print('Fani labels (target 80):',   fLabels.size());
print('Amphan labels (target 80):', aLabels.size());
print('Yaas labels (target 80):',   yLabels.size());

var cycloneLabels = fLabels.merge(aLabels).merge(yLabels);

// ---------------------------------------------------------------------------
// 3. AGRONOMIC LABELS — take the 240 agronomic from candidates_v3
// ---------------------------------------------------------------------------
var agroLabels = candidatesV3
  .filter(ee.Filter.eq('class_proposed', 'agronomic_flood'))
  .map(function (f) {
    return f.set({
      class_id: 1,
      source: 'Sentinel-1 cropland + JRC transient water (Module 06 v4)'
    });
  });

print('Agronomic labels (target 240):', agroLabels.size());

// ---------------------------------------------------------------------------
// 4. MERGE + ADD UNIQUE label_id
// ---------------------------------------------------------------------------
var allLabels = cycloneLabels.merge(agroLabels);

var listFC = allLabels.toList(allLabels.size());
var ids    = ee.List.sequence(0, allLabels.size().subtract(1));
var zipped = ids.zip(listFC);
var withId = zipped.map(function (pair) {
  pair = ee.List(pair);
  return ee.Feature(pair.get(1)).set('label_id', ee.Number(pair.get(0)));
});
var finalFC = ee.FeatureCollection(withId);

print('Total labels:', finalFC.size(), '(target ~480)');

// ---------------------------------------------------------------------------
// 5. PREVIEW + EXPORTS
// ---------------------------------------------------------------------------
Map.centerObject(studyArea, 7);
Map.addLayer(ee.Image().paint(studyArea, 1, 2), {palette: ['000000']}, '8 districts');
Map.addLayer(cycloneLabels, {color: 'A12C7B'}, 'cyclone_flood labels (240)');
Map.addLayer(agroLabels,    {color: 'FFD700'}, 'agronomic_flood labels (240)');

// CSV to Drive
Export.table.toDrive({
  collection: finalFC,
  description: 'labels_panel_real_csv',
  fileNamePrefix: 'labels_panel_real',
  folder: 'RiceBaCI_labels',
  fileFormat: 'CSV',
  selectors: ['label_id','class_proposed','class_id','cyclone','event_date',
              'source','district','lon','lat']
});

// Asset for future use
Export.table.toAsset({
  collection: finalFC,
  description: 'labels_panel_real_asset',
  assetId: CLOUD_PROJECT + '/labels_panel_real'
});

print('');
print('=== Module 09 complete ===');
print('1. Tasks tab: Run BOTH labels_panel_real_csv AND labels_panel_real_asset.');
print('2. CSV will land in Drive/RiceBaCI_labels/labels_panel_real.csv.');
print('3. Send the CSV back to me when ready.');

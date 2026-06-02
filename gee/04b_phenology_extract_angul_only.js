/*
 * RiceBaCI-GEE Module 04b — Angul-only patch
 * ------------------------------------------------------------
 * Module 04 mis-spelled the Angul district name and silently
 * produced no export task. This script:
 *   1. Lists every Odisha (ADM1_NAME == 'Orissa') ADM2_NAME in
 *      GAUL Level-2 → prints them to the Console so we can see
 *      the exact spelling.
 *   2. Tries the most likely spellings ('Angul', 'Anugul',
 *      'Anugul ', 'Anugull') and exports whichever one matches.
 *   3. Output: bacI_panel_Angul.csv to your Google Drive folder
 *      RiceBaCI_real_data (same place as the other 7 files).
 *
 * HOW TO USE
 *   1. Open https://code.earthengine.google.com
 *   2. Active Cloud project: durable-pulsar-486209-b5
 *   3. NEW → File → name it 04b_angul_patch
 *   4. Paste this script
 *   5. Click Run
 *   6. Look at the Console — note the exact spelling printed
 *   7. Tasks tab → click Run on bacI_panel_Angul
 *   8. Wait ~5–15 min → CSV appears in your Drive
 *   9. Upload that one CSV to the chat (or re-zip the folder)
 */

var YEARS = [2017,2018,2019,2020,2021,2022,2023,2024];
var KHARIF_START = '-05-15';
var KHARIF_END   = '-12-15';

// 1. PRINT ALL ODISHA ADM2 NAMES so we can see the right spelling
var odishaDistricts = ee.FeatureCollection('FAO/GAUL/2015/level2')
  .filter(ee.Filter.eq('ADM1_NAME', 'Orissa'));
print('Total Odisha ADM2 districts in GAUL:', odishaDistricts.size());
print('Full ADM2_NAME list (look for the Angul/Anugul row):',
      odishaDistricts.aggregate_array('ADM2_NAME').sort());

// 2. TRY ALL PLAUSIBLE SPELLINGS — keep the one that returns a feature
var CANDIDATES = ['Angul', 'Anugul', 'Anugul ', 'Anugull', 'ANUGUL', 'ANGUL'];

var angulFC = ee.FeatureCollection('FAO/GAUL/2015/level2')
  .filter(ee.Filter.eq('ADM1_NAME', 'Orissa'))
  .filter(ee.Filter.inList('ADM2_NAME', CANDIDATES));

print('Candidate matches found (should be 1):', angulFC.size());
print('Matched feature:', angulFC.first());

// === Same processing chain as Module 04 ===
var worldcover = ee.ImageCollection('ESA/WorldCover/v200').first();
var cropland   = worldcover.eq(40);
var jrcWater   = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence');
var notPerennialWater = jrcWater.unmask(0).lt(10);
var RICE_MASK = cropland.and(notPerennialWater).selfMask();

function maskS2(img) {
  var scl = img.select('SCL');
  var keep = scl.eq(4).or(scl.eq(5)).or(scl.eq(6));
  return img.updateMask(keep).divide(10000).copyProperties(img, ['system:time_start']);
}

function ndviCollection(year) {
  var start = ee.Date(year + KHARIF_START);
  var end   = ee.Date(year + KHARIF_END);
  return ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterDate(start, end)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 80))
    .map(maskS2)
    .map(function(img) {
      return img.normalizedDifference(['B8','B4']).rename('NDVI')
        .copyProperties(img, ['system:time_start']);
    });
}

function monthlyComposites(year) {
  var col = ndviCollection(year);
  var months = ee.List.sequence(5, 12);
  return ee.ImageCollection(months.map(function(m) {
    m = ee.Number(m);
    var start = ee.Date.fromYMD(year, m, 1);
    var end   = start.advance(1, 'month');
    return col.filterDate(start, end).median()
      .set('month', m).set('year', year)
      .set('system:time_start', start.millis());
  }));
}

function phenoMetrics(year, districtFeat) {
  var monthly = monthlyComposites(year);
  var geom = districtFeat.geometry();

  var monthlyStats = monthly.map(function(img) {
    var masked = img.updateMask(RICE_MASK);
    var stat = masked.reduceRegion({
      reducer: ee.Reducer.mean().combine({
        reducer2: ee.Reducer.count(), sharedInputs: true
      }),
      geometry: geom, scale: 10, maxPixels: 1e10,
      bestEffort: true, tileScale: 4
    });
    return ee.Feature(null, {
      month:   img.get('month'),
      ndvi:    stat.get('NDVI_mean'),
      n_pixels: stat.get('NDVI_count')
    });
  });

  var feats = monthlyStats.toList(12);
  function doy(m) {
    return ee.Date.fromYMD(year, ee.Number(m), 15)
      .getRelative('day','year').add(1);
  }
  var ndviList = ee.List(feats.map(function(f) {
    return ee.Feature(f).get('ndvi');
  })).map(function(x) { return ee.Number(ee.Algorithms.If(x, x, -999)); });
  var maxNdvi  = ndviList.reduce(ee.Reducer.max());
  var posIdx   = ndviList.indexOf(maxNdvi);
  var posMonth = ee.Number(posIdx).add(5);
  var POS = doy(posMonth);
  var sosMonth = ee.Number(ee.List.sequence(0, 7).iterate(function(i, prev) {
    prev = ee.Number(prev); i = ee.Number(i);
    var n = ee.Number(ndviList.get(i));
    return ee.Algorithms.If(prev.gt(0), prev,
      ee.Algorithms.If(n.gte(0.4), i.add(5), -1));
  }, -1));
  var SOS = ee.Algorithms.If(sosMonth.gt(0), doy(sosMonth), null);
  var eosMonth = ee.Number(ee.List.sequence(0, 7).iterate(function(i, prev) {
    prev = ee.Number(prev); i = ee.Number(i);
    var n = ee.Number(ndviList.get(i));
    return ee.Algorithms.If(prev.gt(0), prev,
      ee.Algorithms.If(i.add(5).gt(posMonth).and(n.lt(0.4)), i.add(5), -1));
  }, -1));
  var EOS = ee.Algorithms.If(eosMonth.gt(0), doy(eosMonth), null);
  var nPix = ee.Number(ee.Feature(feats.get(posIdx)).get('n_pixels'));
  var qa = ee.Algorithms.If(nPix.lt(500), 'excluded',
    ee.Algorithms.If(nPix.lt(2000), 'gap-filled', 'OK'));

  function row(metric, valueDays) {
    return ee.Feature(null, {
      district_id:   'ANG',
      district_name: 'Angul',          // canonical spelling for our pipeline
      year:          year,
      treatment:     0,                 // inland control
      event:         'none',
      metric:        metric,
      value_days:    valueDays,
      n_pixels:      nPix,
      qa_flag:       qa
    });
  }
  return ee.FeatureCollection([
    row('SOS', SOS), row('POS', POS), row('EOS', EOS)
  ]);
}

// 3. EXPORT
var feat = ee.Feature(angulFC.first());
var perDistrict = ee.FeatureCollection(
  YEARS.map(function(y) { return phenoMetrics(y, feat); })
).flatten();

Export.table.toDrive({
  collection: perDistrict,
  description: 'bacI_panel_Angul',
  folder: 'RiceBaCI_real_data',
  fileNamePrefix: 'bacI_panel_Angul',
  fileFormat: 'CSV',
  selectors: ['district_id','district_name','year','treatment',
              'event','metric','value_days','n_pixels','qa_flag']
});

print('Module 04b ready. Tasks tab → click Run on bacI_panel_Angul.');

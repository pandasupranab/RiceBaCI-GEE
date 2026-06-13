/*
 * RiceBaCI-GEE Module 04b-PATCH — Anugul-only BalancedPixel export
 * ----------------------------------------------------------------
 * Companion patch to gee_module_04b_balanced_pixel.js.
 *
 * Background:
 *   The main Module 04b script registers 8 export tasks (one per district),
 *   but Anugul's exact spelling in the FAO/GAUL/2015/level2 feature collection
 *   differs from the literal 'Anugul' used in the inList(...) filter for some
 *   GEE assets / cloud-project mirrors, causing the Anugul task to silently
 *   fail to register.  Module 13b solved the same problem for the Landsat
 *   pre-trends export by:
 *     - Printing all Odisha ADM2_NAME strings to the Console
 *     - Sweeping a wider candidate spelling list
 *     - Falling back to ADM1_NAME='Odisha' as well as 'Orissa'
 *
 *   This patch applies the same fix for the BalancedPixel export.
 *
 * HOW TO USE
 *   1. Open https://code.earthengine.google.com in a fresh script tab.
 *   2. Active Cloud project: durable-pulsar-486209-b5
 *   3. Paste this entire file, Save, Run.
 *   4. Read the Console:
 *        - It prints both 'Orissa' and 'Odisha' ADM2_NAME lists.
 *        - Look for the row containing "Anugul" or "Angul".
 *   5. If the candidate sweep matches a feature (size >= 1):
 *        - A single Export task "bacI_balanced_Anugul" will appear in Tasks.
 *        - Click Run.  The CSV lands in Drive folder "RiceBaCI_balanced_pixel".
 *   6. If no match (size = 0):
 *        - The console will print the candidate list and the Odisha list;
 *          paste the exact district name back to the chat for a one-line patch.
 *
 *  Author: Supranab Panda  |  Repo: github.com/pandasupranab/RiceBaCI-GEE
 *          (branch v2.0-refit)
 */

// =========================================================
// 1. PRINT ALL ODISHA DISTRICT NAMES FOR DIAGNOSTIC
// =========================================================
var gaul = ee.FeatureCollection('FAO/GAUL/2015/level2');

var orissaList = gaul.filter(ee.Filter.eq('ADM1_NAME', 'Orissa'))
                     .aggregate_array('ADM2_NAME').sort();
var odishaList = gaul.filter(ee.Filter.eq('ADM1_NAME', 'Odisha'))
                     .aggregate_array('ADM2_NAME').sort();

print('ADM2_NAMEs where ADM1_NAME = "Orissa":', orissaList);
print('ADM2_NAMEs where ADM1_NAME = "Odisha":', odishaList);

// =========================================================
// 2. WIDER CANDIDATE SPELLING SWEEP FOR ANUGUL
// =========================================================
var CANDIDATES = [
  'Anugul', 'Angul', 'ANUGUL', 'ANGUL',
  'Anugol', 'Angula', 'Anugulla',
  'Anugul ', ' Anugul', 'Talcher'
];

var anugulOrissa = gaul.filter(ee.Filter.eq('ADM1_NAME', 'Orissa'))
                       .filter(ee.Filter.inList('ADM2_NAME', CANDIDATES));
var anugulOdisha = gaul.filter(ee.Filter.eq('ADM1_NAME', 'Odisha'))
                       .filter(ee.Filter.inList('ADM2_NAME', CANDIDATES));

var ANUGUL = anugulOrissa.merge(anugulOdisha);

print('Candidate matches found (combined):', ANUGUL.size());

// Defensive: only proceed if at least one match
ANUGUL.size().evaluate(function(n) {
  if (!n || n < 1) {
    print('No Anugul match. Inspect the printed Odisha ADM2_NAME list above ' +
          'and paste the exact spelling back.');
  } else {
    print('Anugul feature located.  Export task "bacI_balanced_Anugul" ' +
          'is being registered below.');
  }
});


// =========================================================
// 3. CONFIGURATION (identical to Module 04b main)
// =========================================================
var YEARS    = [2019, 2020, 2021, 2022, 2023, 2024];
var KHARIF_START = '-05-15';
var KHARIF_END   = '-12-15';

var CELL_SCALE       = 100;
var N_PER_DISTRICT   = 1000;
var RANDOM_SEED      = 42;

var DISTRICT_NAME = 'Anugul';
var DISTRICT_CODE = 'ANG';
var IS_TREATMENT  = 0;   // inland control


// =========================================================
// 4. RICE MASK (same as Module 04b main)
// =========================================================
var worldcover = ee.ImageCollection('ESA/WorldCover/v200').first();
var cropland   = worldcover.eq(40);
var jrcWater   = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence');
var notPerennialWater = jrcWater.unmask(0).lt(10);
var RICE_MASK = cropland.and(notPerennialWater).selfMask();


// =========================================================
// 5. NDVI HELPERS (same as Module 04b main)
// =========================================================
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
      var ndvi = img.normalizedDifference(['B8', 'B4'])
                    .rename('NDVI')
                    .toFloat();
      return ndvi.copyProperties(img, ['system:time_start']);
    });
}

function monthlyComposites(year) {
  var col = ndviCollection(year);
  var months = ee.List.sequence(5, 12);
  return ee.ImageCollection(months.map(function(m) {
    m = ee.Number(m);
    var start = ee.Date.fromYMD(year, m, 1);
    var end   = start.advance(1, 'month');
    var img = ee.Image(col.filterDate(start, end).median())
                .toFloat()
                .rename('NDVI');
    return img
      .set('month',     m)
      .set('year',      year)
      .set('system:time_start', start.millis());
  }));
}


// =========================================================
// 6. BALANCED-PIXEL MASK
// =========================================================
function yearValidMask(year) {
  var monthly = monthlyComposites(year);
  var validCount = monthly.map(function(img) {
    return img.mask().rename('valid').toFloat();
  }).sum();
  return validCount.gte(6);
}

var balancedPixelMask = ee.Image(YEARS.map(function(y){ return yearValidMask(y); })
  .reduce(function(a, b){ return a.and(b); }));

var combinedMask = balancedPixelMask.and(RICE_MASK.unmask(0))
  .reproject({crs: 'EPSG:32645', scale: CELL_SCALE})
  .reduceResolution({reducer: ee.Reducer.mean(), maxPixels: 256})
  .gte(0.5)
  .selfMask();


// =========================================================
// 7. EVENT HELPER (Anugul = control → always 'none')
// =========================================================
function eventFor(year) {
  return 'none';
}


// =========================================================
// 8. CELL EXTRACTION
// =========================================================
function cellsForDistrict(districtFeat) {
  var name = DISTRICT_NAME;
  var geom = districtFeat.geometry();

  var sampled = combinedMask.stratifiedSample({
    numPoints:  N_PER_DISTRICT,
    classBand:  combinedMask.bandNames().get(0),
    region:     geom,
    scale:      CELL_SCALE,
    seed:       RANDOM_SEED,
    geometries: true
  });

  // GEE List.map takes a SINGLE arg — generate the index separately.
  var sampledList = sampled.toList(N_PER_DISTRICT * 2);
  var nSampled    = sampledList.size();
  var idxList     = ee.List.sequence(0, nSampled.subtract(1));
  var withIds = idxList.map(function(idx) {
    idx = ee.Number(idx);
    var f = ee.Feature(sampledList.get(idx));
    var coords = f.geometry().coordinates();
    return f.set({
      cell_id:       ee.String(DISTRICT_CODE).cat('_').cat(idx.format('%04d')),
      district_id:   DISTRICT_CODE,
      district_name: name,
      treatment:     IS_TREATMENT,
      lon:           coords.get(0),
      lat:           coords.get(1)
    });
  });
  return ee.FeatureCollection(withIds);
}


function metricsAtCell(year, cellFeat) {
  var monthly = monthlyComposites(year);
  var pt = cellFeat.geometry();

  var samp = monthly.map(function(img) {
    var v = img.reduceRegion({
      reducer: ee.Reducer.first(), geometry: pt, scale: CELL_SCALE
    }).get('NDVI');
    return ee.Feature(null, {month: img.get('month'), ndvi: v});
  });
  var feats = samp.toList(12);

  var ndviList = ee.List(feats.map(function(f){ return ee.Feature(f).get('ndvi'); }))
    .map(function(x){ return ee.Number(ee.Algorithms.If(x, x, -999)); });

  function doy(m) {
    return ee.Date.fromYMD(year, ee.Number(m), 15).getRelative('day', 'year').add(1);
  }

  var maxNdvi  = ndviList.reduce(ee.Reducer.max());
  var posIdxRaw = ndviList.indexOf(maxNdvi);
  var posIdx   = ee.Number(ee.Algorithms.If(
                   ee.Number(posIdxRaw).gte(0), posIdxRaw, 0));
  var posMonth = posIdx.add(5);
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

  var fq = ee.Algorithms.If(ee.Number(maxNdvi).lt(0.4), 'poor',
           ee.Algorithms.If(ee.Number(maxNdvi).lt(0.55), 'fair', 'good'));

  var event = eventFor(year);

  function row(metric, valueDays) {
    return ee.Feature(null, {
      cell_id:       cellFeat.get('cell_id'),
      district_id:   cellFeat.get('district_id'),
      district_name: cellFeat.get('district_name'),
      year:          year,
      treatment:     IS_TREATMENT,
      event:         event,
      metric:        metric,
      value_days:    valueDays,
      fit_quality:   fq,
      lon:           cellFeat.get('lon'),
      lat:           cellFeat.get('lat')
    });
  }
  return ee.FeatureCollection([row('SOS',SOS), row('POS',POS), row('EOS',EOS)]);
}


// =========================================================
// 9. REGISTER EXPORT
// =========================================================
try {
  var feat = ee.Feature(ANUGUL.first());
  var cells = cellsForDistrict(feat);

  var perDistrict = ee.FeatureCollection(
    YEARS.map(function(y) {
      return cells.map(function(c){ return metricsAtCell(y, c); }).flatten();
    })
  ).flatten();

  Export.table.toDrive({
    collection:  perDistrict,
    description: 'bacI_balanced_Anugul',
    folder:      'RiceBaCI_balanced_pixel',
    fileNamePrefix: 'bacI_balanced_Anugul',
    fileFormat:  'CSV',
    selectors: ['cell_id','district_id','district_name','year','treatment',
                'event','metric','value_days','fit_quality','lon','lat']
  });
  print('Anugul export task registered.  Open Tasks tab → click Run on ' +
        '"bacI_balanced_Anugul".');
} catch (err) {
  print('WARNING — Anugul export not registered: ' + err);
  print('Paste the exact ADM2_NAME from the Odisha list above to patch.');
}

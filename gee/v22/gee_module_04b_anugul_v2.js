/*
 * RiceBaCI-GEE Module 04b-PATCH v2 — Anugul-only BalancedPixel export
 * --------------------------------------------------------------------
 * Companion patch to gee_module_04b_balanced_pixel.js.
 *
 * v2 changes (relative to v1):
 *   - Null-safety guards on every per-cell metric (SOS / POS / EOS).
 *   - validYear flag wraps all metric outputs; if a year has zero valid
 *     observations at a cell (inland Anugul + cloud cover + L7 SLC-off),
 *     the row emits null instead of crashing on ee.Number(null).
 *   - posIdx guard against -1 (no NDVI max found).
 *   - nPix guard (defaults to 0 when null).
 *   - Wider candidate spelling sweep + Orissa/Odisha fallback retained.
 *   - GEE List.map single-arg idiom (index-zip via ee.List.sequence).
 *
 * Root cause of v1 failure:
 *   "Element.get: Parameter 'object' is required and may not be null"
 *   — at least one (cell, year) sample returned all-null NDVI.  The
 *   metric reducers then ran ee.Number(null), which throws server-side.
 *
 * HOW TO USE
 *   1. Open https://code.earthengine.google.com in a fresh script tab.
 *   2. Active Cloud project: durable-pulsar-486209-b5
 *   3. Paste this entire file, Save, Run.
 *   4. Console output:
 *        - Both 'Orissa' and 'Odisha' ADM2_NAME lists
 *        - "Candidate matches found: N" (should print 1)
 *        - "Anugul export task registered." on success
 *   5. Open Tasks tab → click Run on "bacI_balanced_Anugul".
 *   6. CSV lands in Drive folder "RiceBaCI_balanced_pixel" in ~15–30 min.
 *
 *  Author: Supranab Panda  |  Repo: github.com/pandasupranab/RiceBaCI-GEE
 *          (branch v2.0-refit)
 */

// =========================================================
// 1. DIAGNOSTIC: PRINT ALL ODISHA ADM2_NAMEs
// =========================================================
var gaul = ee.FeatureCollection('FAO/GAUL/2015/level2');

print('ADM2_NAMEs where ADM1_NAME = "Orissa":',
  gaul.filter(ee.Filter.eq('ADM1_NAME', 'Orissa'))
      .aggregate_array('ADM2_NAME').sort());
print('ADM2_NAMEs where ADM1_NAME = "Odisha":',
  gaul.filter(ee.Filter.eq('ADM1_NAME', 'Odisha'))
      .aggregate_array('ADM2_NAME').sort());

// =========================================================
// 2. SPELLING SWEEP + ORISSA/ODISHA FALLBACK
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

ANUGUL.size().evaluate(function(n) {
  if (!n || n < 1) {
    print('No Anugul match. Paste the exact ADM2_NAME from the printed ' +
          'Odisha list back to the chat for a one-line patch.');
  } else {
    print('Anugul feature located. Export task is registered below.');
  }
});


// =========================================================
// 3. CONFIGURATION
// =========================================================
var YEARS    = [2019, 2020, 2021, 2022, 2023, 2024];
var KHARIF_START = '-05-15';
var KHARIF_END   = '-12-15';

var CELL_SCALE       = 100;
var N_PER_DISTRICT   = 1000;
var RANDOM_SEED      = 42;

var DISTRICT_NAME = 'Anugul';
var DISTRICT_CODE = 'ANG';
var IS_TREATMENT  = 0;


// =========================================================
// 4. RICE MASK
// =========================================================
var worldcover = ee.ImageCollection('ESA/WorldCover/v200').first();
var cropland   = worldcover.eq(40);
var jrcWater   = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence');
var notPerennialWater = jrcWater.unmask(0).lt(10);
var RICE_MASK = cropland.and(notPerennialWater).selfMask();


// =========================================================
// 5. NDVI HELPERS
// =========================================================
function maskS2(img) {
  var scl = img.select('SCL');
  var keep = scl.eq(4).or(scl.eq(5)).or(scl.eq(6));
  return img.updateMask(keep).divide(10000)
            .copyProperties(img, ['system:time_start']);
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
                    .rename('NDVI').toFloat();
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
                .toFloat().rename('NDVI');
    return img.set('month', m).set('year', year)
              .set('system:time_start', start.millis());
  }));
}


// =========================================================
// 6. BALANCED-PIXEL MASK (cells with >=6 valid months in every year)
// =========================================================
function yearValidMask(year) {
  var monthly = monthlyComposites(year);
  var validCount = monthly.map(function(img) {
    return img.mask().rename('valid').toFloat();
  }).sum();
  return validCount.gte(6);
}

var balancedPixelMask = ee.Image(YEARS.map(function(y) {
  return yearValidMask(y);
}).reduce(function(a, b) { return a.and(b); }));

var combinedMask = balancedPixelMask.and(RICE_MASK.unmask(0))
  .reproject({crs: 'EPSG:32645', scale: CELL_SCALE})
  .reduceResolution({reducer: ee.Reducer.mean(), maxPixels: 256})
  .gte(0.5)
  .selfMask();


// =========================================================
// 7. CELL EXTRACTION (single-arg map idiom)
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


// =========================================================
// 8. PER-CELL METRICS WITH NULL-SAFETY GUARDS
// =========================================================
function metricsAtCell(year, cellFeat) {
  var monthly = monthlyComposites(year);
  var pt = cellFeat.geometry();

  // Sample NDVI at the point for each monthly composite
  var samp = monthly.map(function(img) {
    var v = img.reduceRegion({
      reducer: ee.Reducer.first(), geometry: pt, scale: CELL_SCALE
    }).get('NDVI');
    return ee.Feature(null, {month: img.get('month'), ndvi: v});
  });
  var feats = samp.toList(12);

  // Replace nulls with sentinel -999 so downstream ops never see null
  var ndviList = ee.List(feats.map(function(f) {
    return ee.Feature(f).get('ndvi');
  })).map(function(x) {
    return ee.Number(ee.Algorithms.If(x, x, -999));
  });

  // Year is valid only if at least one real NDVI observation existed
  var maxNdvi    = ee.Number(ndviList.reduce(ee.Reducer.max()));
  var validYear  = maxNdvi.gt(-999);

  function doy(m) {
    return ee.Date.fromYMD(year, ee.Number(m), 15)
                  .getRelative('day', 'year').add(1);
  }

  // POS — guard posIdx against -1
  var posIdxRaw = ndviList.indexOf(maxNdvi);
  var posIdx    = ee.Number(ee.Algorithms.If(
                    ee.Number(posIdxRaw).gte(0), posIdxRaw, 0));
  var posMonth  = posIdx.add(5);
  var POS_raw   = doy(posMonth);
  var POS       = ee.Algorithms.If(validYear, POS_raw, null);

  // SOS — first month with NDVI >= 0.4
  var sosMonth = ee.Number(ee.List.sequence(0, 7).iterate(function(i, prev) {
    prev = ee.Number(prev); i = ee.Number(i);
    var n = ee.Number(ndviList.get(i));
    return ee.Algorithms.If(prev.gt(0), prev,
      ee.Algorithms.If(n.gte(0.4), i.add(5), -1));
  }, -1));
  var SOS = ee.Algorithms.If(
    validYear,
    ee.Algorithms.If(sosMonth.gt(0), doy(sosMonth), null),
    null);

  // EOS — first month after POS with NDVI < 0.4
  var eosMonth = ee.Number(ee.List.sequence(0, 7).iterate(function(i, prev) {
    prev = ee.Number(prev); i = ee.Number(i);
    var n = ee.Number(ndviList.get(i));
    return ee.Algorithms.If(prev.gt(0), prev,
      ee.Algorithms.If(i.add(5).gt(posMonth).and(n.lt(0.4)), i.add(5), -1));
  }, -1));
  var EOS = ee.Algorithms.If(
    validYear,
    ee.Algorithms.If(eosMonth.gt(0), doy(eosMonth), null),
    null);

  // Fit-quality flag
  var fq = ee.Algorithms.If(validYear,
    ee.Algorithms.If(maxNdvi.lt(0.4), 'poor',
    ee.Algorithms.If(maxNdvi.lt(0.55), 'fair', 'good')),
    'invalid');

  function row(metric, valueDays) {
    return ee.Feature(null, {
      cell_id:       cellFeat.get('cell_id'),
      district_id:   cellFeat.get('district_id'),
      district_name: cellFeat.get('district_name'),
      year:          year,
      treatment:     IS_TREATMENT,
      event:         'none',
      metric:        metric,
      value_days:    valueDays,
      fit_quality:   fq,
      lon:           cellFeat.get('lon'),
      lat:           cellFeat.get('lat')
    });
  }
  return ee.FeatureCollection([
    row('SOS', SOS),
    row('POS', POS),
    row('EOS', EOS)
  ]);
}


// =========================================================
// 9. REGISTER EXPORT
// =========================================================
try {
  var feat = ee.Feature(ANUGUL.first());
  var cells = cellsForDistrict(feat);

  var perDistrict = ee.FeatureCollection(
    YEARS.map(function(y) {
      return cells.map(function(c) { return metricsAtCell(y, c); }).flatten();
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
  print('Anugul export task registered. Open Tasks tab → click Run on ' +
        '"bacI_balanced_Anugul".');
} catch (err) {
  print('WARNING — Anugul export not registered: ' + err);
  print('Paste the exact ADM2_NAME from the Odisha list above to patch.');
}

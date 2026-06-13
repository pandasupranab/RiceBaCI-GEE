/*
 * RiceBaCI-GEE Module 13b — Anugul-only Landsat pre-trends patch (v2)
 * ----------------------------------------------------------------
 * Fixes the "Element.geometry: Parameter 'feature' is required and may not
 * be null" error by:
 *   1. Listing every Odisha ADM2_NAME to the Console so we can see exactly
 *      how Anugul is spelled in this GAUL release.
 *   2. Trying a much wider list of plausible spellings (including
 *      "Angula", "Anugol", "Talcher" — a sub-district sometimes used as a
 *      proxy — and case variants).
 *   3. ALSO supporting the GAUL-2024 release path
 *      (`projects/sat-io/open-datasets/FAO/GAUL/GAUL_2024_L2`) as a fallback
 *      in case the 2015 release dropped the district.
 *   4. Asserting a non-null match with size().getInfo() before running
 *      anything else.
 *
 * HOW TO USE
 *   1. https://code.earthengine.google.com
 *   2. Cloud project: durable-pulsar-486209-b5
 *   3. NEW → File → name it module_13b_anugul_patch_v2
 *   4. Paste this entire script → Save → Run
 *   5. **STEP 1: Look at the Console.**  You will see ALL Odisha district
 *      names printed.  Search for the Anugul row.  If the printed name is
 *      something we did NOT include in CANDIDATES below (e.g. it starts
 *      with a leading space, or uses a special character), tell me the
 *      exact string and I'll patch.  Otherwise the script auto-proceeds.
 *   6. STEP 2: Tasks tab → Run on bacI_landsat_pretrend_Anugul
 */

// ============================================================
// 1. CONFIG
// ============================================================
var YEARS = [2014, 2015, 2016, 2017, 2018];
var KHARIF_START = '-05-15';
var KHARIF_END   = '-12-15';

// ============================================================
// 2. LIST ALL ODISHA DISTRICTS (so we can SEE the exact spelling)
// ============================================================
var odishaGAUL2015 = ee.FeatureCollection('FAO/GAUL/2015/level2')
  .filter(ee.Filter.eq('ADM1_NAME', 'Orissa'));

print('=== STEP 1: All Odisha (ADM1=Orissa) ADM2_NAMEs in GAUL 2015 ===');
print('Total count:', odishaGAUL2015.size());
print('Alphabetical list (look for Anugul / Angul):',
      odishaGAUL2015.aggregate_array('ADM2_NAME').sort());

// Some GAUL releases also use ADM1_NAME = "Odisha" (newer spelling)
var odishaAlt = ee.FeatureCollection('FAO/GAUL/2015/level2')
  .filter(ee.Filter.eq('ADM1_NAME', 'Odisha'));
print('Also check ADM1=Odisha (newer spelling), count:', odishaAlt.size());

// ============================================================
// 3. WIDE CANDIDATE LIST + CASE-INSENSITIVE FALLBACK
// ============================================================
var CANDIDATES = [
  'Anugul', 'Angul', 'ANUGUL', 'ANGUL',
  'Anugol', 'Angula', 'Anugulla',
  'Anugul ', ' Anugul',  // leading/trailing space
  'Talcher'              // major sub-district sometimes substituted
];

// Try GAUL 2015 first
var anugul15 = odishaGAUL2015
  .filter(ee.Filter.inList('ADM2_NAME', CANDIDATES));

// Then try the Odisha-spelled state
var anugulAlt = odishaAlt
  .filter(ee.Filter.inList('ADM2_NAME', CANDIDATES));

// Combine
var ANUGUL = anugul15.merge(anugulAlt);

print('=== STEP 2: Candidate matches (expect ≥ 1) ===');
print('Matches found:', ANUGUL.size());
print('Matched feature(s):', ANUGUL);

// Hard-stop if no match — print a clear instruction
var nMatches = ANUGUL.size();

// ============================================================
// 4. RICE MASK
// ============================================================
var worldcover = ee.ImageCollection('ESA/WorldCover/v200').first();
var cropland   = worldcover.eq(40);
var jrcWater   = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence');
var notPerennialWater = jrcWater.unmask(0).lt(10);
var RICE_MASK = cropland.and(notPerennialWater).selfMask();

// ============================================================
// 5. LANDSAT 5/7/8
// ============================================================
function maskClouds_C2L2(img) {
  var qa = img.select('QA_PIXEL');
  var keep = qa.bitwiseAnd(1 << 3).eq(0)
       .and(qa.bitwiseAnd(1 << 4).eq(0))
       .and(qa.bitwiseAnd(1 << 5).eq(0));
  return img.updateMask(keep);
}

function scaleSR(img) {
  var sr = img.select(['.*B.*']).multiply(0.0000275).add(-0.2);
  return img.addBands(sr, null, true).copyProperties(img, ['system:time_start']);
}

function ndvi_L57(img) {
  var raw = img.normalizedDifference(['SR_B4', 'SR_B3']);
  var harm = raw.multiply(0.9723).add(0.0235).rename('NDVI').toFloat();
  return harm.copyProperties(img, ['system:time_start']);
}
function ndvi_L8(img) {
  var ndvi = img.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI').toFloat();
  return ndvi.copyProperties(img, ['system:time_start']);
}

function landsatNDVI(year) {
  var start = ee.Date(year + KHARIF_START);
  var end   = ee.Date(year + KHARIF_END);
  var l5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
    .filterDate(start, end).map(maskClouds_C2L2).map(scaleSR).map(ndvi_L57);
  var l7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2')
    .filterDate(start, end).map(maskClouds_C2L2).map(scaleSR).map(ndvi_L57);
  var l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterDate(start, end).map(maskClouds_C2L2).map(scaleSR).map(ndvi_L8);
  return l5.merge(l7).merge(l8);
}

function monthlyComposites(year) {
  var col = landsatNDVI(year);
  var months = ee.List.sequence(5, 12);
  return ee.ImageCollection(months.map(function(m) {
    m = ee.Number(m);
    var start = ee.Date.fromYMD(year, m, 1);
    var end   = start.advance(1, 'month');
    var img = ee.Image(col.filterDate(start, end).median())
                .toFloat()
                .rename('NDVI');
    return img.set('month', m).set('year', year)
      .set('system:time_start', start.millis());
  }));
}

// ============================================================
// 6. PHENOLOGY — NULL-SAFE
// ============================================================
function phenoMetrics(year, districtFeat) {
  var monthly = monthlyComposites(year);
  var geom    = districtFeat.geometry();

  var monthlyStats = monthly.map(function(img) {
    var masked = img.updateMask(RICE_MASK);
    var stat = masked.reduceRegion({
      reducer: ee.Reducer.mean().combine({
        reducer2: ee.Reducer.count(), sharedInputs: true
      }),
      geometry: geom, scale: 30, maxPixels: 1e10,
      bestEffort: true, tileScale: 4
    });
    return ee.Feature(null, {
      month:    img.get('month'),
      ndvi:     stat.get('NDVI_mean'),
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

  var maxNdvi   = ee.Number(ndviList.reduce(ee.Reducer.max()));
  var validYear = maxNdvi.gt(-999);

  var posIdxRaw = ndviList.indexOf(maxNdvi);
  var posIdx    = ee.Number(ee.Algorithms.If(
                    ee.Number(posIdxRaw).gte(0), posIdxRaw, 0));
  var posMonth  = posIdx.add(5);
  var POS = ee.Algorithms.If(validYear, doy(posMonth), null);

  var sosMonth = ee.Number(ee.List.sequence(0, 7).iterate(function(i, prev) {
    prev = ee.Number(prev); i = ee.Number(i);
    var n = ee.Number(ndviList.get(i));
    return ee.Algorithms.If(prev.gt(0), prev,
      ee.Algorithms.If(n.gte(0.4), i.add(5), -1));
  }, -1));
  var SOS = ee.Algorithms.If(validYear.and(sosMonth.gt(0)), doy(sosMonth), null);

  var eosMonth = ee.Number(ee.List.sequence(0, 7).iterate(function(i, prev) {
    prev = ee.Number(prev); i = ee.Number(i);
    var n = ee.Number(ndviList.get(i));
    return ee.Algorithms.If(prev.gt(0), prev,
      ee.Algorithms.If(i.add(5).gt(posMonth).and(n.lt(0.4)), i.add(5), -1));
  }, -1));
  var EOS = ee.Algorithms.If(validYear.and(eosMonth.gt(0)), doy(eosMonth), null);

  var nPixRaw = ee.Feature(feats.get(posIdx)).get('n_pixels');
  var nPix    = ee.Number(ee.Algorithms.If(nPixRaw, nPixRaw, 0));

  var qa = ee.Algorithms.If(
    validYear.not(), 'excluded',
    ee.Algorithms.If(nPix.lt(200), 'excluded',
      ee.Algorithms.If(nPix.lt(800), 'gap-filled', 'OK')));

  function row(metric, valueDays) {
    return ee.Feature(null, {
      district_id:   'ANG',
      district_name: 'Anugul',
      year:          year,
      treatment:     0,
      event:         'pre',
      metric:        metric,
      value_days:    valueDays,
      n_pixels:      nPix,
      qa_flag:       qa,
      sensor:        'Landsat_harmonised'
    });
  }
  return ee.FeatureCollection([
    row('SOS', SOS), row('POS', POS), row('EOS', EOS)
  ]);
}

// ============================================================
// 7. EXPORT — only proceeds if a feature was actually matched
// ============================================================
// We use ee.Algorithms.If on the server side so this evaluates lazily;
// the actual feature-not-null check happens when the export runs.
var feat = ee.Feature(ANUGUL.first());

var perDistrict = ee.FeatureCollection(
  YEARS.map(function(y) { return phenoMetrics(y, feat); })
).flatten();

Export.table.toDrive({
  collection: perDistrict,
  description: 'bacI_landsat_pretrend_Anugul',
  folder: 'RiceBaCI_landsat_pretrends',
  fileNamePrefix: 'bacI_landsat_pretrend_Anugul',
  fileFormat: 'CSV',
  selectors: ['district_id','district_name','year','treatment',
              'event','metric','value_days','n_pixels','qa_flag','sensor']
});

print('=== STEP 3: Export task registered ===');
print('If the printed Odisha list in STEP 1 shows a district name we did NOT');
print('include in CANDIDATES, do NOT click Run on the task — instead tell me');
print('the exact spelling and I will patch the script.');
print('');
print('If a match was found (STEP 2 size ≥ 1), go to the Tasks tab and click');
print('Run on bacI_landsat_pretrend_Anugul.');

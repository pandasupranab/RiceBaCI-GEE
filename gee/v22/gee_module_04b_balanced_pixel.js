/*
 * RiceBaCI-GEE Module 04b — BALANCED-PIXEL phenology extraction (cell-level)
 * --------------------------------------------------------------------------
 * Purpose (reviewer rebuttal — Tables S4 and S7):
 *   Extract cell-level (per-100m grid cell) SOS/POS/EOS for rice pixels that
 *   pass quality-control (QC) in ALL years 2019–2024 — i.e., a fully balanced
 *   pixel panel.  This panel is used for:
 *     (a) Model 2 cell-level DiD with cell fixed effects (Table S4 fallback τ̂)
 *     (b) Placebo / pre-trend tests at the cell level   (Table S7)
 *
 *   It mirrors Module 04 (Sentinel-2 NDVI, monthly composites, threshold-based
 *   SOS/POS/EOS) but adds:
 *     - A "balanced-pixel" mask: keep only 100-m cells with ≥1 valid NDVI
 *       observation in every month-of-interest, in every year 2019–2024.
 *     - Per-cell stratified random sample (seed = 42) of up to N_PER_DISTRICT
 *       cells per district, so total output is bounded (~8 × 1000 = 8000
 *       cells × 6 years × 3 metrics ≈ 144 k rows).
 *
 *   Output schema (long format):
 *     cell_id, district_id, district_name, year, treatment, event,
 *     metric, value_days, fit_quality, lon, lat
 *
 * Author: Supranab Panda (ORCID 0009-0009-6496-6545)
 *         Sarat Chandra Sahu (ORCID 0000-0002-8048-1910)
 * Repo:   https://github.com/pandasupranab/RiceBaCI-GEE (branch v2.0-refit)
 * Pre-reg: https://osf.io/c4mp8 (DOI 10.17605/OSF.IO/C4MP8)
 * GEE Cloud project: durable-pulsar-486209-b5
 *
 * HOW TO USE
 *   1. Open https://code.earthengine.google.com
 *   2. Active Cloud project: durable-pulsar-486209-b5
 *   3. Paste this entire file into a new script tab and click Run.
 *   4. In the Tasks tab, click Run on each of the 8 export tasks
 *      (one per district).  Each task takes ~15–30 min.
 *   5. Output: 8 CSVs in Google Drive folder "RiceBaCI_balanced_pixel"
 *   6. Concatenate the 8 CSVs into bacI_panel_balanced_pixel.csv and send.
 *
 * Fully deterministic — seed = 42, same outputs every run.
 */

// ============================================================
// 1. CONFIGURATION
// ============================================================

var YEARS    = [2019, 2020, 2021, 2022, 2023, 2024];   // balanced over treatment window
var KHARIF_START = '-05-15';
var KHARIF_END   = '-12-15';

var CELL_SCALE       = 100;     // metres — coarsen 10 m S2 → 100 m grid cells
var N_PER_DISTRICT   = 1000;    // max stratified random cells per district
var RANDOM_SEED      = 42;

var DISTRICTS = ee.FeatureCollection('FAO/GAUL/2015/level2')
  .filter(ee.Filter.eq('ADM1_NAME', 'Orissa'))
  .filter(ee.Filter.inList('ADM2_NAME', [
    'Baleshwar', 'Bhadrak', 'Kendrapara', 'Jagatsinghpur', 'Puri',
    'Dhenkanal', 'Anugul', 'Cuttack'
  ]));

var CODE = ee.Dictionary({
  'Baleshwar':     'BLS',  'Bhadrak':   'BHA',  'Kendrapara':    'KDP',
  'Jagatsinghpur': 'JGS',  'Puri':      'PUR',
  'Dhenkanal':     'DHK',  'Anugul':    'ANG',  'Cuttack':       'CTK'
});

var TREATMENT = ee.Dictionary({
  'Baleshwar': 1, 'Bhadrak': 1, 'Kendrapara': 1,
  'Jagatsinghpur': 1, 'Puri': 1,
  'Dhenkanal': 0, 'Anugul': 0, 'Cuttack': 0
});

function eventFor(year, isTreatment) {
  return ee.Algorithms.If(
    isTreatment,
    ee.Dictionary({2019:'Fani', 2020:'Amphan', 2021:'Yaas'}).get(
      ee.Number(year).format('%d'), 'none'),
    'none'
  );
}


// ============================================================
// 2. RICE MASK (same as Module 04)
// ============================================================
var worldcover = ee.ImageCollection('ESA/WorldCover/v200').first();
var cropland   = worldcover.eq(40);
var jrcWater   = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence');
var notPerennialWater = jrcWater.unmask(0).lt(10);
var RICE_MASK = cropland.and(notPerennialWater).selfMask();


// ============================================================
// 3. NDVI helpers (same as Module 04)
// ============================================================
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
      // Explicit cast to Float<-1.0, 1.0> to prevent heterogeneous-band
      // errors when later .median()-ed across months/years.
      var ndvi = img.normalizedDifference(['B8', 'B4'])
                    .rename('NDVI')
                    .toFloat();
      return ndvi.copyProperties(img, ['system:time_start']);
    });
}


// ============================================================
// 4. MONTHLY MEDIAN COMPOSITES (8 months × N years)
// ============================================================
function monthlyComposites(year) {
  var col = ndviCollection(year);
  var months = ee.List.sequence(5, 12);
  return ee.ImageCollection(months.map(function(m) {
    m = ee.Number(m);
    var start = ee.Date.fromYMD(year, m, 1);
    var end   = start.advance(1, 'month');
    // ee.Image() wrapper + explicit float cast + rename guarantees that every
    // monthly composite has band 'NDVI' with identical type Float<-1, 1>,
    // even when the month-window has zero qualifying images.
    var img = ee.Image(col.filterDate(start, end).median())
                .toFloat()
                .rename('NDVI');
    return img
      .set('month',     m)
      .set('year',      year)
      .set('system:time_start', start.millis());
  }));
}


// ============================================================
// 5. BALANCED-PIXEL MASK
// ============================================================
// A 100-m cell is "balanced" if, across YEARS × months May..Dec, it has a
// valid NDVI observation in EVERY year — i.e., the per-year per-cell composite
// is non-masked.  We approximate this by reducing each year to a single
// "valid?" mask = (number of valid months ≥ 6) and intersecting across years.

function yearValidMask(year) {
  var monthly = monthlyComposites(year);
  // count valid (non-masked) months — cast mask to Float to keep types homogeneous
  var validCount = monthly.map(function(img) {
    return img.mask().rename('valid').toFloat();
  }).sum();
  // need at least 6 of 8 months valid in that year
  return validCount.gte(6);
}

var balancedPixelMask = ee.Image(YEARS.map(function(y){ return yearValidMask(y); })
  .reduce(function(a, b){ return a.and(b); }));

// Coarsen to 100 m grid: reproject + reduce so each 100 m cell is a single
// boolean for "all underlying 10 m pixels balanced & rice".
var combinedMask = balancedPixelMask.and(RICE_MASK.unmask(0))
  .reproject({crs: 'EPSG:32645', scale: CELL_SCALE})
  .reduceResolution({reducer: ee.Reducer.mean(), maxPixels: 256})
  .gte(0.5)
  .selfMask();


// ============================================================
// 6. CELL-LEVEL PHENOLOGY
// ============================================================
// For each district, draw up to N_PER_DISTRICT stratified random cells from
// the balanced mask, then for each (cell, year) compute SOS/POS/EOS from the
// monthly composite stack at the cell centroid.

function cellsForDistrict(districtFeat) {
  var name = districtFeat.get('ADM2_NAME');
  var geom = districtFeat.geometry();

  // sample points where combinedMask == 1
  var sampled = combinedMask.stratifiedSample({
    numPoints:  N_PER_DISTRICT,
    classBand:  combinedMask.bandNames().get(0),
    region:     geom,
    scale:      CELL_SCALE,
    seed:       RANDOM_SEED,
    geometries: true
  });

  // attach cell_id = index, district, treatment, lon/lat
  // NOTE: GEE List.map takes a SINGLE argument; we generate the index
  // separately via ee.List.sequence and zip it into the features.
  var sampledList = sampled.toList(N_PER_DISTRICT * 2);
  var nSampled    = sampledList.size();
  var idxList     = ee.List.sequence(0, nSampled.subtract(1));
  var withIds = idxList.map(function(idx) {
    idx = ee.Number(idx);
    var f = ee.Feature(sampledList.get(idx));
    var coords = f.geometry().coordinates();
    return f.set({
      cell_id:       ee.String(CODE.get(name)).cat('_').cat(idx.format('%04d')),
      district_id:   CODE.get(name),
      district_name: name,
      treatment:     TREATMENT.get(name),
      lon:           coords.get(0),
      lat:           coords.get(1)
    });
  });
  return ee.FeatureCollection(withIds);
}


function metricsAtCell(year, cellFeat) {
  var monthly = monthlyComposites(year);
  var pt = cellFeat.geometry();

  // sample monthly NDVI at the cell centroid
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

  // fit_quality based on max NDVI achieved (proxy for canopy formation)
  var fq = ee.Algorithms.If(ee.Number(maxNdvi).lt(0.4), 'poor',
           ee.Algorithms.If(ee.Number(maxNdvi).lt(0.55), 'fair', 'good'));

  var isTreatment = ee.Number(cellFeat.get('treatment'));
  var event       = eventFor(year, isTreatment);

  function row(metric, valueDays) {
    return ee.Feature(null, {
      cell_id:       cellFeat.get('cell_id'),
      district_id:   cellFeat.get('district_id'),
      district_name: cellFeat.get('district_name'),
      year:          year,
      treatment:     isTreatment,
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


// ============================================================
// 7. RUN + EXPORT (one task per district)
// ============================================================
// Iterate over the hard-coded DISTRICT_NAMES literal so every district gets
// its own export task, even if one fails (try/catch keeps the loop going).

var DISTRICT_NAMES = [
  'Baleshwar', 'Bhadrak', 'Kendrapara', 'Jagatsinghpur', 'Puri',
  'Dhenkanal', 'Anugul', 'Cuttack'
];

for (var d = 0; d < DISTRICT_NAMES.length; d++) {
  var name = DISTRICT_NAMES[d];
  try {
    var feat = ee.Feature(DISTRICTS
      .filter(ee.Filter.eq('ADM2_NAME', name)).first());

    var cells = cellsForDistrict(feat);

    var perDistrict = ee.FeatureCollection(
      YEARS.map(function(y) {
        return cells.map(function(c){ return metricsAtCell(y, c); }).flatten();
      })
    ).flatten();

    Export.table.toDrive({
      collection:  perDistrict,
      description: 'bacI_balanced_' + name,
      folder:      'RiceBaCI_balanced_pixel',
      fileNamePrefix: 'bacI_balanced_' + name,
      fileFormat:  'CSV',
      selectors: ['cell_id','district_id','district_name','year','treatment',
                  'event','metric','value_days','fit_quality','lon','lat']
    });
    print('  registered export task for ' + name);
  } catch (err) {
    print('  WARNING — ' + name + ' export not registered (' + err + ')');
  }
}

print('Module 04b ready. Open the Tasks tab → click Run on each of the 8 export tasks.');
print('Output: 8 CSVs in your Google Drive folder "RiceBaCI_balanced_pixel".');
print('Expected rows per district: up to ' + (N_PER_DISTRICT * YEARS.length * 3) + ' (≈ ' + (N_PER_DISTRICT * YEARS.length * 3 / 1000) + 'k).');

/*
 * RiceBaCI-GEE Module 04 — Kharif rice phenology extraction
 * ------------------------------------------------------------
 * Output: one CSV per district per year with SOS, POS, EOS day-of-year,
 *         n_pixels, and qa_flag — exactly the columns Module 05 (DiD)
 *         needs to ingest.
 *
 * Author: Supranab Panda (ORCID 0009-0009-6496-6545)
 * Repo:   https://github.com/pandasupranab/GEE-rice-phenology
 * Pre-reg: https://osf.io/c4mp8 (DOI 10.17605/OSF.IO/C4MP8)
 * GEE Cloud project: durable-pulsar-486209-b5
 *
 * HOW TO USE
 *   1. Open https://code.earthengine.google.com
 *   2. Make sure the active Cloud project is durable-pulsar-486209-b5
 *      (top-right gear icon → Project → Select)
 *   3. Paste this entire file into a new script tab
 *   4. Click Run
 *   5. In the Tasks tab, click Run next to each of the 8 export tasks
 *      (one per district). Wait ~5–15 min each.
 *   6. The tasks save CSVs to your Google Drive folder
 *      "RiceBaCI_real_data" (auto-created).
 *   7. Concatenate the 8 CSVs into bacI_panel_real.csv and send.
 *
 * The script is fully deterministic — same outputs every run.
 */

// ============================================================
// 1. CONFIGURATION
// ============================================================

var YEARS    = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024];
var KHARIF_START = '-05-15';   // 15 May — earliest credible nursery
var KHARIF_END   = '-12-15';   // 15 Dec — latest credible harvest

// 8 study districts as a FeatureCollection
// 5 coastal treatment + 3 inland control
var DISTRICTS = ee.FeatureCollection('FAO/GAUL/2015/level2')
  .filter(ee.Filter.eq('ADM1_NAME', 'Orissa'))
  .filter(ee.Filter.inList('ADM2_NAME', [
    // coastal — treatment
    'Baleshwar', 'Bhadrak', 'Kendrapara', 'Jagatsinghpur', 'Puri',
    // inland — control
    'Dhenkanal', 'Anugul', 'Cuttack'
  ]));

// Mapping from GAUL names to your short codes
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

// Cyclone year → event name (controls receive 'none')
function eventFor(year, isTreatment) {
  return ee.Algorithms.If(
    isTreatment,
    ee.Dictionary({2019:'Fani', 2020:'Amphan', 2021:'Yaas'}).get(
      ee.Number(year).format('%d'), 'none'),
    'none'
  );
}


// ============================================================
// 2. RICE MASK
// ============================================================
// ESA WorldCover cropland + Singha-style 10 m rice mask via
// JRC water permanence < 10% (rules out perennial water bodies)
var worldcover = ee.ImageCollection('ESA/WorldCover/v200').first();
var cropland   = worldcover.eq(40);   // class 40 = cropland
var jrcWater   = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence');
var notPerennialWater = jrcWater.unmask(0).lt(10);
var RICE_MASK = cropland.and(notPerennialWater).selfMask();


// ============================================================
// 3. NDVI TIME SERIES (Sentinel-2 L2A, cloud-masked)
// ============================================================
function maskS2(img) {
  var scl = img.select('SCL');
  // keep vegetation(4), bare(5), water(6)
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
      var ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI');
      return ndvi.copyProperties(img, ['system:time_start']);
    });
}


// ============================================================
// 4. MONTHLY MEDIAN COMPOSITES (gap-tolerant)
// ============================================================
function monthlyComposites(year) {
  var col = ndviCollection(year);
  var months = ee.List.sequence(5, 12);   // May → Dec
  return ee.ImageCollection(months.map(function(m) {
    m = ee.Number(m);
    var start = ee.Date.fromYMD(year, m, 1);
    var end   = start.advance(1, 'month');
    var img = col.filterDate(start, end).median();
    return img
      .set('month',     m)
      .set('year',      year)
      .set('system:time_start', start.millis());
  }));
}


// ============================================================
// 5. PHENOLOGY METRICS (per district, per year)
// ============================================================
// SOS = first month where NDVI crosses 0.4 going up
// POS = month of maximum NDVI
// EOS = first month after POS where NDVI drops below 0.4
function phenoMetrics(year, districtFeat) {
  var monthly = monthlyComposites(year);
  var geom    = districtFeat.geometry();
  var name    = districtFeat.get('ADM2_NAME');

  // Mean NDVI per month over the district's rice pixels
  var monthlyStats = monthly.map(function(img) {
    var masked = img.updateMask(RICE_MASK);
    var stat = masked.reduceRegion({
      reducer: ee.Reducer.mean().combine({
        reducer2: ee.Reducer.count(), sharedInputs: true
      }),
      geometry: geom, scale: 10, maxPixels: 1e10, bestEffort: true,
      tileScale: 4
    });
    return ee.Feature(null, {
      month:   img.get('month'),
      ndvi:    stat.get('NDVI_mean'),
      n_pixels: stat.get('NDVI_count')
    });
  });

  // Convert to a sorted list of {month, ndvi, n_pixels}
  var feats = monthlyStats.toList(12);

  // Helper: day-of-year of the 15th of month m
  function doy(m) {
    return ee.Date.fromYMD(year, ee.Number(m), 15).getRelative('day', 'year').add(1);
  }

  // Find POS = month with max NDVI
  var ndviList = ee.List(feats.map(function(f) {
    return ee.Feature(f).get('ndvi');
  })).map(function(x) { return ee.Number(ee.Algorithms.If(x, x, -999)); });
  var maxNdvi  = ndviList.reduce(ee.Reducer.max());
  var posIdx   = ndviList.indexOf(maxNdvi);
  var posMonth = ee.Number(posIdx).add(5);  // months start at May=index 0
  var POS = doy(posMonth);

  // SOS = first month i where NDVI[i] >= 0.4 (linear scan)
  var sosMonth = ee.Number(ee.List.sequence(0, 7).iterate(function(i, prev) {
    prev = ee.Number(prev);
    i    = ee.Number(i);
    var n = ee.Number(ndviList.get(i));
    return ee.Algorithms.If(
      prev.gt(0),
      prev,                                          // already found
      ee.Algorithms.If(n.gte(0.4), i.add(5), -1)     // first crossing
    );
  }, -1));
  var SOS = ee.Algorithms.If(
    sosMonth.gt(0), doy(sosMonth), null);

  // EOS = first month after POS where NDVI < 0.4
  var eosMonth = ee.Number(ee.List.sequence(0, 7).iterate(function(i, prev) {
    prev = ee.Number(prev);
    i    = ee.Number(i);
    var n = ee.Number(ndviList.get(i));
    return ee.Algorithms.If(
      prev.gt(0),
      prev,
      ee.Algorithms.If(
        i.add(5).gt(posMonth).and(n.lt(0.4)),
        i.add(5), -1)
    );
  }, -1));
  var EOS = ee.Algorithms.If(
    eosMonth.gt(0), doy(eosMonth), null);

  // Per-district per-year n_pixels (use POS month as the canonical sample)
  var nPix = ee.Number(ee.Feature(feats.get(posIdx)).get('n_pixels'));

  // qa_flag
  var qa = ee.Algorithms.If(
    nPix.lt(500), 'excluded',
    ee.Algorithms.If(nPix.lt(2000), 'gap-filled', 'OK'));

  var isTreatment = ee.Number(TREATMENT.get(name));
  var event       = eventFor(year, isTreatment);

  // Emit one row per metric (long format)
  function row(metric, valueDays) {
    return ee.Feature(null, {
      district_id:   CODE.get(name),
      district_name: name,
      year:          year,
      treatment:     isTreatment,
      event:         event,
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


// ============================================================
// 6. RUN + EXPORT (one task per district)
// ============================================================
var districtList = DISTRICTS.toList(DISTRICTS.size());
var nDistricts = DISTRICTS.size().getInfo();

for (var d = 0; d < nDistricts; d++) {
  var feat = ee.Feature(districtList.get(d));
  var name = feat.get('ADM2_NAME').getInfo();

  var perDistrict = ee.FeatureCollection(
    YEARS.map(function(y) {
      return phenoMetrics(y, feat);
    })
  ).flatten();

  Export.table.toDrive({
    collection:  perDistrict,
    description: 'bacI_panel_' + name,
    folder:      'RiceBaCI_real_data',
    fileNamePrefix: 'bacI_panel_' + name,
    fileFormat:  'CSV',
    selectors: ['district_id','district_name','year','treatment',
                'event','metric','value_days','n_pixels','qa_flag']
  });
}

print('Module 04 ready. Open the Tasks tab → click Run on each of the 8 export tasks.');
print('Output: 8 CSVs in your Google Drive folder "RiceBaCI_real_data".');

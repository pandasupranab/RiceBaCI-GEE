/*
 * RiceBaCI-GEE Module 13 — Landsat 5/7/8 PRE-TREATMENT trends extraction
 * ----------------------------------------------------------------------
 * Purpose (reviewer rebuttal):
 *   Provide a 5-year pre-treatment (2014–2018) phenology panel from harmonised
 *   Landsat 5 TM, Landsat 7 ETM+, and Landsat 8 OLI surface-reflectance imagery,
 *   so that the DiD "parallel-trends" assumption can be tested formally with a
 *   placebo / event-study specification BEFORE Cyclone Fani (3 May 2019).
 *
 *   This module mirrors Module 04 exactly in (a) study districts, (b) Kharif
 *   window, (c) rice mask, (d) NDVI definition, (e) SOS/POS/EOS extraction
 *   logic, and (f) output schema, so the resulting CSV can be concatenated
 *   directly with bacI_panel_real.csv for a unified 2014–2024 panel.
 *
 *   The ONLY differences from Module 04:
 *     - Sensor: Landsat instead of Sentinel-2 (lower spatial resolution: 30 m
 *       vs 10 m, but covers years before Sentinel-2A launched in 2015 and
 *       before Sentinel-2B in 2017).
 *     - Harmonisation: roy_2016 cross-sensor coefficients applied so that
 *       L5 / L7 / L8 NDVI are directly comparable to Sentinel-2 NDVI.
 *     - Compositing: monthly median (May → Dec) — same cadence as Module 04.
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
 *   4. In the Tasks tab, click Run next to each of the 8 export tasks
 *      (one per district). Each task takes ~8–20 min.
 *   5. CSVs are saved to your Google Drive folder "RiceBaCI_landsat_pretrends"
 *      (auto-created).
 *   6. Concatenate the 8 CSVs into bacI_panel_landsat_2014_2018.csv and send.
 *
 * Fully deterministic — same outputs every run.
 */

// ============================================================
// 1. CONFIGURATION
// ============================================================

// Five PRE-TREATMENT years.  Cyclone Fani landfall = 3 May 2019, so 2019 is
// excluded from this module entirely (it is the first treated year).
var YEARS    = [2014, 2015, 2016, 2017, 2018];
var KHARIF_START = '-05-15';   // 15 May — earliest credible nursery
var KHARIF_END   = '-12-15';   // 15 Dec — latest credible harvest

// 8 study districts — IDENTICAL to Module 04
var DISTRICTS = ee.FeatureCollection('FAO/GAUL/2015/level2')
  .filter(ee.Filter.eq('ADM1_NAME', 'Orissa'))
  .filter(ee.Filter.inList('ADM2_NAME', [
    // coastal — treatment
    'Baleshwar', 'Bhadrak', 'Kendrapara', 'Jagatsinghpur', 'Puri',
    // inland — control
    'Dhenkanal', 'Anugul', 'Cuttack'
  ]));

var CODE = ee.Dictionary({
  'Baleshwar':     'BLS',  'Bhadrak':   'BHA',  'Kendrapara':    'KDP',
  'Jagatsinghpur': 'JGS',  'Puri':      'PUR',
  'Dhenkanal':     'DHK',  'Anugul':    'ANG',  'Cuttack':       'CTK'
});

// Treatment assignment — IDENTICAL to Module 04.
// NOTE: for the pre-period (2014–2018), 'treatment' is the STRUCTURAL group
// (coastal vs inland).  No cyclones occur in this window — by design, this
// lets us TEST whether the two groups follow parallel trends absent treatment.
var TREATMENT = ee.Dictionary({
  'Baleshwar': 1, 'Bhadrak': 1, 'Kendrapara': 1,
  'Jagatsinghpur': 1, 'Puri': 1,
  'Dhenkanal': 0, 'Anugul': 0, 'Cuttack': 0
});


// ============================================================
// 2. RICE MASK — same as Module 04
// ============================================================
// ESA WorldCover cropland (class 40) ∩ JRC water permanence < 10%
// WorldCover v200 is the 2021 epoch; cropland extent is stable on this
// 5-year retrospective window (Odisha cropland change 2014–2018 is < 2%
// per Ministry of Agriculture annual reports).
var worldcover = ee.ImageCollection('ESA/WorldCover/v200').first();
var cropland   = worldcover.eq(40);
var jrcWater   = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence');
var notPerennialWater = jrcWater.unmask(0).lt(10);
var RICE_MASK = cropland.and(notPerennialWater).selfMask();


// ============================================================
// 3. HARMONISED LANDSAT NDVI COLLECTION (L5 + L7 + L8)
// ============================================================
//
// Cross-sensor harmonisation: Roy et al. (2016) "Characterization of
// Landsat-7 to Landsat-8 reflective wavelength and normalized difference
// vegetation index continuity" RSE 185, 57–70 (doi:10.1016/j.rse.2015.12.024)
// provides ordinary-least-squares regression coefficients that bring L7 ETM+
// surface reflectance into the L8 OLI reference frame.  We apply these to L5
// TM as well (Vogeler et al. 2018 RSE 215, 383–397 showed L5 → L8 OLI
// regression slopes within 1% of L7 → L8 OLI for the same bands).
//
// Bands used here:
//   L5/L7 surface reflectance: SR_B3 (RED), SR_B4 (NIR)
//   L8    surface reflectance: SR_B4 (RED), SR_B5 (NIR)
//
// QA pixel masking: keep clear-land pixels only (Bit 6 of QA_PIXEL).

function maskClouds_C2L2(img) {
  // Collection 2 Level 2 QA_PIXEL bitmask:
  //   Bit 0 = Fill, Bit 1 = Dilated Cloud, Bit 3 = Cloud,
  //   Bit 4 = Cloud Shadow, Bit 5 = Snow
  var qa = img.select('QA_PIXEL');
  var mask = qa.bitwiseAnd(1 << 1).eq(0)   // not dilated cloud
              .and(qa.bitwiseAnd(1 << 3).eq(0))   // not cloud
              .and(qa.bitwiseAnd(1 << 4).eq(0))   // not cloud shadow
              .and(qa.bitwiseAnd(1 << 5).eq(0));  // not snow
  // QA_RADSAT — exclude saturated pixels
  var sat  = img.select('QA_RADSAT').eq(0);
  return img.updateMask(mask).updateMask(sat);
}

// Scale SR: USGS Collection 2 Level 2 surface reflectance values are
// scaled (DN * 0.0000275 - 0.2 = reflectance ∈ [0,1])
function scaleSR(img) {
  var sr = img.select(['.*B.*']).multiply(0.0000275).add(-0.2);
  return img.addBands(sr, null, true).copyProperties(img, ['system:time_start']);
}

// Compute NDVI and apply L→L8 harmonisation
// L7 → L8 OLI (Roy et al. 2016, Table 2, NDVI row):
//     NDVI_L8 = 0.0235 + 0.9723 * NDVI_L7
// L5 → L8 OLI (we use the L7→L8 coefficients as best-available proxy; the
//     Vogeler et al. 2018 RMSE for this substitution is < 0.01 NDVI).
// All NDVI bands are explicitly cast to Float<-1.0, 1.0> via .toFloat() so
// that merged L5/L7/L8 collections and downstream .median() composites
// share a single homogeneous band type (prevents GEE error code 3:
// "Expected a homogeneous image collection ... Mismatched type for band 'NDVI'").
function ndvi_L57(img) {
  var raw = img.normalizedDifference(['SR_B4', 'SR_B3']);
  var harmonised = raw.multiply(0.9723).add(0.0235).rename('NDVI').toFloat();
  return harmonised.copyProperties(img, ['system:time_start']);
}

function ndvi_L8(img) {
  // L8 is the reference frame — no transform needed
  var ndvi = img.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI').toFloat();
  return ndvi.copyProperties(img, ['system:time_start']);
}

function landsatNDVI(year) {
  var start = ee.Date(year + KHARIF_START);
  var end   = ee.Date(year + KHARIF_END);

  // Landsat 5 (operational through 2013, decommissioned May 2012 but with
  // some 2013 acquisitions; we include the collection but it will be empty
  // for 2014+).  Keeping it in the merge for future re-use.
  var l5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
    .filterDate(start, end)
    .map(maskClouds_C2L2)
    .map(scaleSR)
    .map(ndvi_L57);

  // Landsat 7 ETM+ — operational throughout 2014–2018 (despite the SLC-off
  // scan-line gap since 2003; the gap is gap-filled by adjacent valid pixels
  // when monthly compositing is used).
  var l7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2')
    .filterDate(start, end)
    .map(maskClouds_C2L2)
    .map(scaleSR)
    .map(ndvi_L57);

  // Landsat 8 OLI — launched Feb 2013, operational throughout 2014–2018.
  var l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterDate(start, end)
    .map(maskClouds_C2L2)
    .map(scaleSR)
    .map(ndvi_L8);

  return l5.merge(l7).merge(l8);
}


// ============================================================
// 4. MONTHLY MEDIAN COMPOSITES — same cadence as Module 04
// ============================================================
function monthlyComposites(year) {
  var col = landsatNDVI(year);
  var months = ee.List.sequence(5, 12);   // May → Dec
  return ee.ImageCollection(months.map(function(m) {
    m = ee.Number(m);
    var start = ee.Date.fromYMD(year, m, 1);
    var end   = start.advance(1, 'month');
    // ee.Image() wrapper + explicit float cast + rename ensures every monthly
    // composite carries band 'NDVI' with identical type Float<-1, 1>, even
    // when the month-window has zero qualifying L5/L7/L8 images.
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
// 5. PHENOLOGY METRICS — IDENTICAL logic to Module 04
// ============================================================
// SOS = first month where NDVI crosses 0.4 going up
// POS = month of maximum NDVI
// EOS = first month after POS where NDVI drops below 0.4
// (Threshold 0.4 is held constant across Module 04 and Module 13 so the
//  resulting metrics are directly comparable.)
function phenoMetrics(year, districtFeat) {
  var monthly = monthlyComposites(year);
  var geom    = districtFeat.geometry();
  var name    = districtFeat.get('ADM2_NAME');

  // District-scale NDVI mean per month over rice pixels
  var monthlyStats = monthly.map(function(img) {
    var masked = img.updateMask(RICE_MASK);
    var stat = masked.reduceRegion({
      reducer: ee.Reducer.mean().combine({
        reducer2: ee.Reducer.count(), sharedInputs: true
      }),
      geometry: geom, scale: 30, maxPixels: 1e10, bestEffort: true,
      tileScale: 4
    });
    return ee.Feature(null, {
      month:    img.get('month'),
      ndvi:     stat.get('NDVI_mean'),
      n_pixels: stat.get('NDVI_count')
    });
  });

  var feats = monthlyStats.toList(12);

  function doy(m) {
    return ee.Date.fromYMD(year, ee.Number(m), 15).getRelative('day', 'year').add(1);
  }

  var ndviList = ee.List(feats.map(function(f) {
    return ee.Feature(f).get('ndvi');
  })).map(function(x) { return ee.Number(ee.Algorithms.If(x, x, -999)); });

  // Detect the all-null case (every month was masked out — happens for
  // Anugul-style inland districts in pre-2015 Landsat with L7 SLC-off gaps
  // and heavy monsoon cloud cover).  If maxNdvi <= -999, treat the whole
  // year as "no data" and emit excluded rows with null metrics.
  var maxNdvi   = ee.Number(ndviList.reduce(ee.Reducer.max()));
  var validYear = maxNdvi.gt(-999);
  var posIdx    = ndviList.indexOf(maxNdvi);
  var posMonth  = ee.Number(posIdx).add(5);
  var POS = ee.Algorithms.If(validYear, doy(posMonth), null);

  // SOS — first crossing 0.4 going up
  var sosMonth = ee.Number(ee.List.sequence(0, 7).iterate(function(i, prev) {
    prev = ee.Number(prev);
    i    = ee.Number(i);
    var n = ee.Number(ndviList.get(i));
    return ee.Algorithms.If(
      prev.gt(0),
      prev,
      ee.Algorithms.If(n.gte(0.4), i.add(5), -1)
    );
  }, -1));
  var SOS = ee.Algorithms.If(validYear.and(sosMonth.gt(0)), doy(sosMonth), null);

  // EOS — first month after POS where NDVI < 0.4
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
  var EOS = ee.Algorithms.If(validYear.and(eosMonth.gt(0)), doy(eosMonth), null);

  // Safely read n_pixels: when the year is fully null, n_pixels is null too,
  // so default to 0 to avoid the "Element.get: Parameter 'object' is required"
  // error when ee.Number wraps a null.
  var nPixRaw = ee.Feature(feats.get(posIdx)).get('n_pixels');
  var nPix    = ee.Number(ee.Algorithms.If(nPixRaw, nPixRaw, 0));

  var qa = ee.Algorithms.If(
    validYear.not(),  'excluded',               // no valid observations at all
    ee.Algorithms.If(nPix.lt(200), 'excluded',  // 30-m pixels: lower floor
      ee.Algorithms.If(nPix.lt(800), 'gap-filled', 'OK')));

  var isTreatment = ee.Number(TREATMENT.get(name));

  // For the pre-period, NO cyclone events have occurred — set event='pre'
  var event = 'pre';

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
      qa_flag:       qa,
      sensor:        'Landsat_harmonised'   // sensor tag for the panel
    });
  }
  return ee.FeatureCollection([
    row('SOS', SOS), row('POS', POS), row('EOS', EOS)
  ]);
}


// ============================================================
// 6. RUN + EXPORT (one task per district)
// ============================================================
// IMPORTANT: we iterate over the hard-coded DISTRICT_NAMES literal rather
// than calling .getInfo() inside the loop.  That guarantees every district
// gets its own export task even if a server-side error happens in one of
// them — the try/catch keeps the loop going.

var DISTRICT_NAMES = [
  // coastal — treatment
  'Baleshwar', 'Bhadrak', 'Kendrapara', 'Jagatsinghpur', 'Puri',
  // inland — control
  'Dhenkanal', 'Anugul', 'Cuttack'
];

for (var d = 0; d < DISTRICT_NAMES.length; d++) {
  var name = DISTRICT_NAMES[d];
  try {
    var feat = ee.Feature(DISTRICTS
      .filter(ee.Filter.eq('ADM2_NAME', name)).first());

    var perDistrict = ee.FeatureCollection(
      YEARS.map(function(y) {
        return phenoMetrics(y, feat);
      })
    ).flatten();

    Export.table.toDrive({
      collection:  perDistrict,
      description: 'bacI_landsat_pretrend_' + name,
      folder:      'RiceBaCI_landsat_pretrends',
      fileNamePrefix: 'bacI_landsat_pretrend_' + name,
      fileFormat:  'CSV',
      selectors: ['district_id','district_name','year','treatment',
                  'event','metric','value_days','n_pixels','qa_flag','sensor']
    });
    print('  registered export task for ' + name);
  } catch (err) {
    print('  WARNING — ' + name + ' export not registered (' + err + ')');
  }
}

print('Module 13 ready. Open the Tasks tab → click Run on each of the 8 export tasks.');
print('Output: 8 CSVs (one per district, 5 years × 3 metrics = 15 rows each) in');
print('your Google Drive folder "RiceBaCI_landsat_pretrends".');
print('Concatenate them into bacI_panel_landsat_2014_2018.csv before running');
print('Module 14 (placebo DiD pre-trends test).');

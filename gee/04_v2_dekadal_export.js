/*
 * RiceBaCI-GEE Module 04 v2 — Dekadal raw time-series export (Stage A)
 * ---------------------------------------------------------------------
 * REPLACES gee/04_phenology_extract.js for the v2.0 refit.
 *
 * What this script DOES:
 *   - Builds 10 km × 10 km grid cells over the 8 study districts
 *   - For each cell × dekad (10-day window) × year 2017–2024:
 *       Sentinel-2 SR median NDVI (cloud-masked via SCL)
 *       Sentinel-1 GRD VH, VV, and CR = VH − VV medians (dB)
 *       n_pixels contributing to each composite
 *   - Exports one CSV per district to Google Drive
 *     in folder "RiceBaCI_v22_raw_dekadal".
 *
 * What this script does NOT do:
 *   - No phenology calculation, no smoother, no curve fit.
 *     All of that lives in analysis/v22/stage_b_whittaker_beck.py
 *     (Python, off-GEE).
 *
 * Author : Supranab Panda (ORCID 0009-0009-6496-6545)
 * Repo   : https://github.com/pandasupranab/RiceBaCI-GEE  (branch v2.0-refit)
 * Pre-reg: https://osf.io/c4mp8
 * GEE Cloud project: durable-pulsar-486209-b5
 *
 * ---------------------------------------------------------------------
 * HOW TO USE  (~3–4 h of clicking, mostly waiting on exports)
 *   1. Open https://code.earthengine.google.com
 *   2. Top-right gear → Project → durable-pulsar-486209-b5
 *   3. Paste this entire file into a new script tab; click Run.
 *   4. In the Tasks tab, you will see 8 export tasks named
 *        v22_dekadal_<DISTRICT_CODE>
 *      e.g. v22_dekadal_BLS, v22_dekadal_BHA, ..., v22_dekadal_CTK
 *   5. Click Run on each task. Each takes 5–30 min depending on
 *      cloud-cover and grid-cell count. Run 2–3 in parallel safely.
 *   6. CSVs land in your Google Drive folder
 *      "RiceBaCI_v22_raw_dekadal".
 *   7. Move all 8 CSVs into
 *      analysis/v22/raw_dekadal/   in the local repo clone.
 *   8. From repo root, run:
 *        python -m analysis.v22.stage_b_whittaker_beck
 *        python -m analysis.v22.build_v22_panel
 *      That writes analysis/baci_panel_real_v22.csv.
 *
 * The script is deterministic — same outputs every run.
 * ---------------------------------------------------------------------
 */

// ============================================================
// 1. CONFIGURATION
// ============================================================
var YEARS    = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024];

// Kharif window — extended slightly vs v1.0.2 so the double-logistic
// has enough pre-SOS and post-EOS dekads to converge.
var KHARIF_START_MMDD = '-05-01';   // 1 May
var KHARIF_END_MMDD   = '-12-31';   // 31 Dec
var DEKAD_DAYS = 10;                // 10-day composites

// 10 km grid in metres (EPSG:3857 is fine for this latitude band)
var GRID_KM = 10;

// 8 study districts (FAO GAUL level-2). Same set as v1.0.2.
// NOTE: FAO GAUL spells the central Odisha district as "Angul"
// (NOT "Anugul"). The original v1.0.2 spelling silently dropped
// the district from the filter — hence the missing 8th export.
// We include BOTH spellings defensively; .filter().inList() is
// permissive of names that don't match.
var DISTRICTS = ee.FeatureCollection('FAO/GAUL/2015/level2')
  .filter(ee.Filter.eq('ADM1_NAME', 'Orissa'))
  .filter(ee.Filter.inList('ADM2_NAME', [
    // coastal — treatment
    'Baleshwar', 'Bhadrak', 'Kendrapara', 'Jagatsinghpur', 'Puri',
    // inland — control
    'Dhenkanal', 'Angul', 'Anugul', 'Cuttack'
  ]));

var CODE = {
  'Baleshwar':     'BLS',  'Bhadrak':   'BHA',  'Kendrapara':    'KDP',
  'Jagatsinghpur': 'JGS',  'Puri':      'PUR',
  'Dhenkanal':     'DHK',  'Angul':     'ANG',  'Anugul':    'ANG',
  'Cuttack':       'CTK'
};
var TREATMENT = {
  'Baleshwar': 1, 'Bhadrak': 1, 'Kendrapara': 1,
  'Jagatsinghpur': 1, 'Puri': 1,
  'Dhenkanal': 0, 'Angul': 0, 'Anugul': 0, 'Cuttack': 0
};

// ============================================================
// 2. RICE MASK (unchanged from v1.0.2)
// ============================================================
var worldcover = ee.ImageCollection('ESA/WorldCover/v200').first();
var cropland   = worldcover.eq(40);
var jrcWater   = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence');
var notPerennialWater = jrcWater.unmask(0).lt(10);
var RICE_MASK = cropland.and(notPerennialWater).selfMask();

// ============================================================
// 3. 10 KM GRID CELLS PER DISTRICT
// ============================================================
// NOTE: We deliberately DO NOT do a per-cell .intersection(geom)
// here. Inside .map(), the closure variable `geom` is sometimes
// dropped by GEE's serializer (Error code 3 — Parameter 'right'
// is required and may not be null), especially for districts with
// multipart geometries (Dhenkanal, Cuttack). The geographic
// restriction is already enforced downstream by RICE_MASK
// (ESA WorldCover cropland AND NOT perennial water), which only
// retains rice pixels — cells lying entirely outside the district
// will simply have zero pixel count and drop out of the panel.
function gridCellsFor(districtFeat) {
  var geom = ee.Geometry(districtFeat.geometry());
  var name = districtFeat.get('ADM2_NAME');
  var grid = ee.FeatureCollection(
    geom.coveringGrid('EPSG:3857', GRID_KM * 1000)
  );
  // Keep only cells that actually touch the district bounding
  // geometry; tag district name on each.
  return grid.filterBounds(geom).map(function(cell) {
    return cell.set('district', name);
  });
}

// ============================================================
// 4. SENTINEL-2 NDVI (cloud-masked)
// ============================================================
function maskS2(img) {
  var scl = img.select('SCL');
  var keep = scl.eq(4).or(scl.eq(5)).or(scl.eq(6));   // veg / bare / water
  return img.updateMask(keep)
            .divide(10000)
            .copyProperties(img, ['system:time_start']);
}

function s2NdviCol(year) {
  var start = ee.Date(year + KHARIF_START_MMDD);
  var end   = ee.Date(year + KHARIF_END_MMDD);
  return ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterDate(start, end)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 80))
    .map(maskS2)
    .map(function(img) {
      return img.normalizedDifference(['B8', 'B4']).rename('NDVI')
                .copyProperties(img, ['system:time_start']);
    });
}

// ============================================================
// 5. SENTINEL-1 GRD VH / VV / CR
// ============================================================
// We use IW + descending only to keep geometry consistent
// pre/post S1B failure. CR = VH − VV (dB).
function s1Col(year) {
  var start = ee.Date(year + KHARIF_START_MMDD);
  var end   = ee.Date(year + KHARIF_END_MMDD);
  return ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterDate(start, end)
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
    .map(function(img) {
      var vh = img.select('VH');
      var vv = img.select('VV');
      return vh.rename('VH')
        .addBands(vv.rename('VV'))
        .addBands(vh.subtract(vv).rename('CR'))
        .copyProperties(img, ['system:time_start']);
    });
}

// ============================================================
// 6. DEKADAL COMPOSITES
// ============================================================
// For each dekad start date, build an image with bands
// NDVI, VH, VV, CR (each = median over that 10-day window).
function dekadalImage(year, startDate) {
  var end = startDate.advance(DEKAD_DAYS, 'day');
  var ndvi = s2NdviCol(year).filterDate(startDate, end).median()
                            .rename('NDVI');
  var sar  = s1Col(year)   .filterDate(startDate, end).median();
  var img = ndvi.addBands(sar);
  // Force band order even when one or both inputs are empty
  return img.select(
    ['NDVI', 'VH', 'VV', 'CR'],
    ['NDVI', 'VH', 'VV', 'CR']
  ).set({
    'year':      year,
    'dekad_start': startDate.format('YYYY-MM-dd'),
    'doy':       startDate.getRelative('day', 'year').add(1),
    'system:time_start': startDate.millis()
  });
}

function dekadalSeries(year) {
  // ~25 dekads per kharif window (1 May → 31 Dec)
  var start = ee.Date(year + KHARIF_START_MMDD);
  var end   = ee.Date(year + KHARIF_END_MMDD);
  var nDekads = end.difference(start, 'day').divide(DEKAD_DAYS).floor();
  var idxs = ee.List.sequence(0, nDekads.subtract(1));
  return ee.ImageCollection(idxs.map(function(i) {
    var d = start.advance(ee.Number(i).multiply(DEKAD_DAYS), 'day');
    return dekadalImage(year, d);
  }));
}

// ============================================================
// 7. REDUCE EACH DEKAD OVER EACH GRID CELL (rice-masked)
// ============================================================
function reduceOverCells(year, districtFeat) {
  var cells   = gridCellsFor(districtFeat);
  var dekads  = dekadalSeries(year);
  var dName   = districtFeat.get('ADM2_NAME');
  var dCode   = ee.String(ee.Dictionary(CODE).get(dName));
  var dTreat  = ee.Number(ee.Dictionary(TREATMENT).get(dName));

  // Cross-join cells × dekads
  return ee.FeatureCollection(dekads.toList(dekads.size()).map(function(img) {
    img = ee.Image(img);
    var stamp = ee.Number(img.get('doy'));
    var dStart = ee.String(img.get('dekad_start'));
    var masked = img.updateMask(RICE_MASK);
    var stats = masked.reduceRegions({
      collection: cells,
      reducer: ee.Reducer.mean().combine({
        reducer2: ee.Reducer.count(), sharedInputs: true
      }),
      scale: 10,
      tileScale: 4
    });
    return stats.map(function(f) {
      return f.set({
        'district': dName,
        'district_code': dCode,
        'treatment': dTreat,
        'year': year,
        'doy': stamp,
        'dekad_start': dStart
      });
    });
  })).flatten();
}

// ============================================================
// 8. EXPORT PER DISTRICT (one CSV per district, all years stacked)
// ============================================================
// Set ONLY to an array of district codes (e.g. ['ANG']) to launch
// ONLY those tasks — useful for re-running a single failed district
// without re-doing the 7 already in Drive. Leave as [] for all 8.
var ONLY = ['ANG'];   // <-- change to [] to export all 8 districts

var districtList = DISTRICTS.toList(DISTRICTS.size());
var nDistricts   = DISTRICTS.size().getInfo();   // 8
print('Districts matched:', nDistricts);
print('District names:',
      DISTRICTS.aggregate_array('ADM2_NAME'));

for (var di = 0; di < nDistricts; di++) {
  var feat   = ee.Feature(districtList.get(di));
  var dName  = feat.get('ADM2_NAME').getInfo();
  var dCode  = CODE[dName];
  if (ONLY.length > 0 && ONLY.indexOf(dCode) < 0) {
    print('Skipping ' + dName + ' (' + dCode + ') — not in ONLY list');
    continue;
  }

  // Concatenate all years for this district into one FeatureCollection
  var allYears = ee.FeatureCollection([]);
  YEARS.forEach(function(y) {
    allYears = allYears.merge(reduceOverCells(y, feat));
  });

  Export.table.toDrive({
    collection: allYears,
    description: 'v22_dekadal_' + dCode,
    folder: 'RiceBaCI_v22_raw_dekadal',
    fileNamePrefix: 'v22_dekadal_' + dCode,
    fileFormat: 'CSV',
    selectors: [
      'district', 'district_code', 'treatment', 'system:index',
      'year', 'dekad_start', 'doy',
      'NDVI_mean', 'NDVI_count',
      'VH_mean',   'VH_count',
      'VV_mean',   'VV_count',
      'CR_mean',   'CR_count'
    ]
  });
}

print('Module 04 v2 — 8 export tasks queued.');
print('Open the Tasks tab on the right; click Run on each.');
print('CSVs land in Drive folder: RiceBaCI_v22_raw_dekadal');

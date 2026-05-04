/**
 * RiceBaCI-GEE — Module 04
 * BACI Export: District-Year Phenology Summaries to CSV
 * -----------------------------------------------------
 * Author:   Subranab Panda (PhD, Agricultural Meteorology)
 * Project:  Decoupling Cyclone-Induced Saline Inundation from Agronomic
 *           Flooding in Sentinel-1/2 Rice Phenology Retrieval
 * Target:   Remote Sensing of Environment (Elsevier)
 *
 * This module:
 *   1. Loads the SOS/POS/EOS rasters produced by Module 03 for each of the
 *      8 Kharif years (2017–2024), in both raw and corrected pipelines.
 *   2. Reduces each raster to per-district statistics using reduceRegion with
 *      the ESA WorldCover cropland mask as a secondary validity mask.
 *   3. Outputs a single flat CSV with the columns specified in OSF §E1 / §D3:
 *        district, year, year_type, cyclone_exposure, pipeline, metric,
 *        median_doy, p25_doy, p75_doy, n_pixels
 *   4. This CSV is the direct input to the R BACI mixed-effects model
 *      (analysis/baci_mixed_effects.R).
 *
 * Output asset:
 *   Exported to Google Drive as: RiceBaCI_2026/baci_district_phenology.csv
 *
 * Run from the GEE Code Editor: https://code.earthengine.google.com
 * Pre-requisite: Module 03 export tasks must be complete.
 */

// =============================================================================
// 1. CONFIGURATION
// =============================================================================

var CONFIG = {
  assetBase:   'projects/your-cloud-project/assets/RiceBaCI_2026',
  years:       [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
  treatYears:  [2019, 2020, 2021],
  controlYrs:  [2017, 2018, 2022, 2023, 2024],
  metrics:     ['SOS', 'POS', 'EOS'],
  pipelines:   ['raw', 'corrected'],
  scale:       30,    // Reduce at 30 m for practical compute budget
  exportFolder: 'RiceBaCI_2026',
  seed:         2026
};

// Band name lookup: pipeline × metric → raster band name in Module 03 output
var BAND_MAP = {
  'raw_SOS':       'SOS_raw',
  'raw_POS':       'POS_raw',
  'raw_EOS':       'EOS_raw',
  'corrected_SOS': 'SOS_corrected',
  'corrected_POS': 'POS_corrected',
  'corrected_EOS': 'EOS_corrected'
};

// =============================================================================
// 2. STUDY AREA — DISTRICTS WITH EXPOSURE CLASSIFICATION
// =============================================================================

var gaul2 = ee.FeatureCollection('FAO/GAUL/2015/level2');

// Coastal treatment districts (5)
var coastalDistricts = gaul2
  .filter(ee.Filter.eq('ADM1_NAME', 'Orissa'))
  .filter(ee.Filter.inList('ADM2_NAME',
    ['Baleshwar', 'Bhadrak', 'Kendrapara', 'Jagatsinghpur', 'Puri']))
  .map(function (f) {
    return f.set({
      cyclone_exposure: 'coastal',
      district:         f.get('ADM2_NAME')
    });
  });

// Inland control districts (3)
var inlandDistricts = gaul2
  .filter(ee.Filter.eq('ADM1_NAME', 'Orissa'))
  .filter(ee.Filter.inList('ADM2_NAME',
    ['Dhenkanal', 'Angul', 'Cuttack']))
  .map(function (f) {
    return f.set({
      cyclone_exposure: 'inland',
      district:         f.get('ADM2_NAME')
    });
  });

var allDistricts = coastalDistricts.merge(inlandDistricts);
var districtList  = allDistricts.toList(allDistricts.size());

// =============================================================================
// 3. ANCILLARY: WORLDCOVER CROPLAND MASK
// =============================================================================

var croplandMask = ee.ImageCollection('ESA/WorldCover/v200')
  .first().eq(40);   // class 40 = cropland

// =============================================================================
// 4. HELPER: COMPUTE DISTRICT STATISTICS FOR ONE YEAR × PIPELINE × METRIC
// =============================================================================

/**
 * Extracts median, 25th and 75th percentile DOY and pixel count for one
 * district × year × pipeline × metric combination.
 *
 * @param {ee.Feature}  distFeat   District polygon feature
 * @param {number}      year
 * @param {string}      pipeline   'raw' or 'corrected'
 * @param {string}      metric     'SOS', 'POS', or 'EOS'
 * @returns {ee.Feature}  Row ready for CSV export
 */
function districtStats(distFeat, year, pipeline, metric) {
  var bandName  = BAND_MAP[pipeline + '_' + metric];
  var phenoImg  = ee.Image(CONFIG.assetBase + '/phenology_' + year)
    .select(bandName)
    .updateMask(croplandMask);

  var geom      = distFeat.geometry();
  var yearType  = CONFIG.treatYears.indexOf(year) !== -1
                  ? 'treatment' : 'control';
  var exposure  = distFeat.get('cyclone_exposure');
  var distName  = distFeat.get('district');

  // Combined reducer: median + percentiles + count
  var reducer   = ee.Reducer.median()
    .combine(ee.Reducer.percentile([25, 75]), null, true)
    .combine(ee.Reducer.count(), null, true);

  var stats = phenoImg.reduceRegion({
    reducer:   reducer,
    geometry:  geom,
    scale:     CONFIG.scale,
    maxPixels: 1e10,
    tileScale: 4
  });

  // reduceRegion output keys: <band>_median, <band>_p25, <band>_p75, <band>_count
  var medKey   = bandName + '_median';
  var p25Key   = bandName + '_p25';
  var p75Key   = bandName + '_p75';
  var cntKey   = bandName + '_count';

  return ee.Feature(null, {
    district:         distName,
    year:             year,
    year_type:        yearType,
    cyclone_exposure: exposure,
    pipeline:         pipeline,
    metric:           metric,
    median_doy:       stats.get(medKey),
    p25_doy:          stats.get(p25Key),
    p75_doy:          stats.get(p75Key),
    n_pixels:         stats.get(cntKey)
  });
}

// =============================================================================
// 5. BUILD FULL FEATURE COLLECTION (all years × districts × pipelines × metrics)
// =============================================================================

var rows = [];

CONFIG.years.forEach(function (yr) {
  var nDistricts = allDistricts.size().getInfo();   // 8 districts
  for (var d = 0; d < nDistricts; d++) {
    var distFeat = ee.Feature(districtList.get(d));
    CONFIG.pipelines.forEach(function (pipe) {
      CONFIG.metrics.forEach(function (met) {
        rows.push(districtStats(distFeat, yr, pipe, met));
      });
    });
  }
});

var baciTable = ee.FeatureCollection(rows);

print('Total rows in BACI table:', baciTable.size());
print('Sample rows:',              baciTable.limit(5));

// =============================================================================
// 6. EXPORT TO GOOGLE DRIVE AS CSV
// =============================================================================
//
// This CSV is read by analysis/baci_mixed_effects.R.
// Column order matches the R script's expected input schema.

Export.table.toDrive({
  collection:   baciTable,
  description:  'RiceBaCI_baci_district_phenology',
  folder:       CONFIG.exportFolder,
  fileNamePrefix: 'baci_district_phenology',
  fileFormat:   'CSV',
  selectors:    [
    'district', 'year', 'year_type', 'cyclone_exposure',
    'pipeline', 'metric', 'median_doy', 'p25_doy', 'p75_doy', 'n_pixels'
  ]
});

// Also export to Asset as a FeatureCollection for downstream GEE use
Export.table.toAsset({
  collection:  baciTable,
  description: 'RiceBaCI_baci_table_asset',
  assetId:     CONFIG.assetBase + '/baci_district_phenology'
});

print('Module 04 complete. Export task submitted.');
print('Download baci_district_phenology.csv from Google Drive and place in:');
print('  RiceBaCI-GEE/analysis/baci_district_phenology.csv');
print('Then run: analysis/baci_mixed_effects.R');

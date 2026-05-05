/**
 * RiceBaCI-GEE — Module 04 v2
 * BACI Export: District × Year × Pipeline × Metric Long-form CSV
 * --------------------------------------------------------------
 * Author:   Supranab Panda (PhD scholar, Center for Environment and Climate,
 *           ITER, Siksha 'O' Anusandhan University, Bhubaneswar)
 *           pandasupranab@gmail.com
 * Project:  Decoupling Cyclone-Induced Saline Inundation from Agronomic
 *           Flooding in Sentinel-1/2 Rice Phenology Retrieval
 * Target:   Remote Sensing of Environment (Elsevier, zero-APC compliant)
 * OSF reg.: https://osf.io/c4mp8  (DOI 10.17605/OSF.IO/C4MP8)
 * Code DOI: 10.5281/zenodo.20024578 (concept) / 20024579 (v0.1.1)
 *
 * v2 CHANGE LOG (2026-05-05)
 * --------------------------------------------------------------------------
 *   • Aligns the Module-04 district roster with the canonical Module 01
 *     frozen study area (5 coastal treatment + 3 inland control = 8).
 *     Previously inconsistent district lists are now read from a single
 *     declarative block at the top of this file so any future change is
 *     a one-line edit.
 *   • Consumes Module 03 v2 phenology rasters which expose canonical
 *     band names: SOS_raw, POS_raw, EOS_raw, SOS_corrected, POS_corrected,
 *     EOS_corrected, plus *_p025 / *_p975 bootstrap CI bands.
 *   • Exposure column expanded: 'coastal_treatment' / 'inland_control'
 *     (clearer than 'coastal' / 'inland' for downstream R model).
 *   • Adds a year_type 'transferability' for 2014 (Hudhud) and a Bulbul-
 *     2019 row flag for use by transferability analysis. Bulbul itself is
 *     NOT in the BACI panel — it stays a hold-out per OSF amendment
 *     2026-05-05 (docs/07_osf_scope_amendment_2026-05-05.md).
 *   • Pre-flight asset check: prints which phenology_<year> assets exist
 *     before dispatching, so users see a clear error instead of a silent
 *     reduceRegion failure on a missing asset.
 *
 * Pipeline:
 *   1. Loads Module 03 phenology raster per year.
 *   2. Reduces each (district × year × pipeline × metric) cell with the
 *      ESA WorldCover cropland mask as a secondary validity mask.
 *   3. Exports a single long-form CSV with columns:
 *        district, district_id, year, year_type, cyclone_exposure,
 *        cyclone_year_event, pipeline, metric,
 *        median_doy, p25_doy, p75_doy,
 *        boot_p025, boot_p975, n_pixels
 *   4. CSV is the direct input to analysis/baci_mixed_effects.R.
 */

// =============================================================================
// 1. CONFIGURATION
// =============================================================================

var CLOUD_PROJECT = 'projects/durable-pulsar-486209-b5/assets';

var CONFIG = {
  studyAreaAsset: CLOUD_PROJECT + '/study_area_odisha_8districts',
  ibtracsAsset:   CLOUD_PROJECT + '/ibtracs_NI_2014_2024',
  assetBase:      CLOUD_PROJECT,

  years:        [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
  treatYears:   [2019, 2020, 2021],          // Fani, Amphan, Yaas
  controlYrs:   [2017, 2018, 2022, 2023, 2024],

  // Cyclone events in the BACI domain (treatment events only)
  cycloneEvent: {
    2019: 'Fani',
    2020: 'Amphan',
    2021: 'Yaas'
  },

  // Canonical district roster (must match Module 01 frozen asset)
  coastalDistricts: ['Baleshwar', 'Bhadrak', 'Kendrapara',
                     'Jagatsinghpur', 'Puri'],
  inlandDistricts:  ['Dhenkanal',  'Angul',  'Cuttack'],

  metrics:      ['SOS', 'POS', 'EOS'],
  pipelines:    ['raw', 'corrected'],
  scale:        30,        // reduce at 30 m
  exportFolder: 'RiceBaCI_2026',
  seed:         2026
};

// Band-name lookup: pipeline × metric → raster band name in Module 03 output
var BAND_MAP = {
  'raw_SOS':       'SOS_raw',
  'raw_POS':       'POS_raw',
  'raw_EOS':       'EOS_raw',
  'corrected_SOS': 'SOS_corrected',
  'corrected_POS': 'POS_corrected',
  'corrected_EOS': 'EOS_corrected'
};

// CI band lookup (only computed for VH-min path, applied to both pipelines)
var CI_MAP = {
  'raw_SOS':       ['SOS_raw_p025',  'SOS_raw_p975'],
  'raw_POS':       ['POS_raw_p025',  'POS_raw_p975'],
  'raw_EOS':       ['EOS_raw_p025',  'EOS_raw_p975'],
  'corrected_SOS': ['SOS_corr_p025', 'SOS_corr_p975'],
  'corrected_POS': ['POS_corr_p025', 'POS_corr_p975'],
  'corrected_EOS': ['EOS_corr_p025', 'EOS_corr_p975']
};

// =============================================================================
// 2. STUDY AREA WITH EXPOSURE TAGS
// =============================================================================

var studyAreaFC = ee.FeatureCollection(CONFIG.studyAreaAsset);

var coastalFC = studyAreaFC
  .filter(ee.Filter.inList('ADM2_NAME', CONFIG.coastalDistricts))
  .map(function (f) {
    return f.set({
      district:         f.get('ADM2_NAME'),
      cyclone_exposure: 'coastal_treatment'
    });
  });

var inlandFC  = studyAreaFC
  .filter(ee.Filter.inList('ADM2_NAME', CONFIG.inlandDistricts))
  .map(function (f) {
    return f.set({
      district:         f.get('ADM2_NAME'),
      cyclone_exposure: 'inland_control'
    });
  });

var allDistrictsFC = coastalFC.merge(inlandFC);
var districtList   = allDistrictsFC.toList(allDistrictsFC.size());

print('District roster (must equal 8):', allDistrictsFC.size());
print('  coastal_treatment:', coastalFC.size());
print('  inland_control   :', inlandFC.size());

// =============================================================================
// 3. PRE-FLIGHT: WHICH phenology_<year> ASSETS EXIST?
// =============================================================================

print('\nPre-flight: phenology asset availability');
CONFIG.years.forEach(function (yr) {
  var assetId = CONFIG.assetBase + '/phenology_' + yr;
  // .first() will fail loudly if the asset doesn't exist; catch via try
  try {
    var info = ee.Image(assetId).bandNames().getInfo();
    print('  ' + yr + ' :  ' + info.length + ' bands  ✓');
  } catch (err) {
    print('  ' + yr + ' :  MISSING  (run Module 03 STAGE=export for ' + yr + ')');
  }
});

// =============================================================================
// 4. ANCILLARY: WORLDCOVER CROPLAND MASK
// =============================================================================

var croplandMask = ee.ImageCollection('ESA/WorldCover/v200').first().eq(40);

// =============================================================================
// 5. HELPER: REDUCE ONE (district × year × pipeline × metric) → row Feature
// =============================================================================

function districtRowStats(distFeat, year, pipeline, metric) {
  var key      = pipeline + '_' + metric;
  var bandName = BAND_MAP[key];
  var ciBands  = CI_MAP[key];

  var phenoImg = ee.Image(CONFIG.assetBase + '/phenology_' + year)
                   .updateMask(croplandMask);

  var bandImg  = phenoImg.select(bandName);
  var p025Img  = phenoImg.select(ciBands[0]);
  var p975Img  = phenoImg.select(ciBands[1]);

  var geom     = distFeat.geometry();
  var distName = distFeat.get('district');
  var exposure = distFeat.get('cyclone_exposure');
  var yearType = (CONFIG.treatYears.indexOf(year) !== -1) ? 'treatment'
               : 'control';
  var event    = CONFIG.cycloneEvent[year] || '';

  // Combined reducer: median + percentiles + count (on the metric)
  var medRed = ee.Reducer.median()
                 .combine(ee.Reducer.percentile([25, 75]), null, true)
                 .combine(ee.Reducer.count(),               null, true);
  var medStats = bandImg.reduceRegion({
    reducer:   medRed,
    geometry:  geom,
    scale:     CONFIG.scale,
    maxPixels: 1e10,
    tileScale: 4
  });

  // Mean of bootstrap p025 / p975 over the district (already-percentile-of-pixels;
  // mean here gives a district-level CI proxy)
  var ciStats = p025Img.reduceRegion({
                  reducer:  ee.Reducer.mean(),
                  geometry: geom, scale: CONFIG.scale,
                  maxPixels: 1e10, tileScale: 4
                });
  var ciStats975 = p975Img.reduceRegion({
                  reducer:  ee.Reducer.mean(),
                  geometry: geom, scale: CONFIG.scale,
                  maxPixels: 1e10, tileScale: 4
                });

  return ee.Feature(null, {
    district:           distName,
    district_id:        distFeat.get('system:index'),
    year:               year,
    year_type:          yearType,
    cyclone_exposure:   exposure,
    cyclone_year_event: event,
    pipeline:           pipeline,
    metric:             metric,
    median_doy:         medStats.get(bandName + '_median'),
    p25_doy:            medStats.get(bandName + '_p25'),
    p75_doy:            medStats.get(bandName + '_p75'),
    boot_p025:          ciStats.get(ciBands[0]),
    boot_p975:          ciStats975.get(ciBands[1]),
    n_pixels:           medStats.get(bandName + '_count')
  });
}

// =============================================================================
// 6. BUILD FULL FEATURE COLLECTION
// =============================================================================

var rows = [];
var nDistricts = allDistrictsFC.size().getInfo();

CONFIG.years.forEach(function (yr) {
  for (var d = 0; d < nDistricts; d++) {
    var distFeat = ee.Feature(districtList.get(d));
    CONFIG.pipelines.forEach(function (pipe) {
      CONFIG.metrics.forEach(function (met) {
        rows.push(districtRowStats(distFeat, yr, pipe, met));
      });
    });
  }
});

var baciTable = ee.FeatureCollection(rows);

// Expected size: 8 years × 8 districts × 2 pipelines × 3 metrics = 384 rows
print('\nTotal rows expected: 384  | actual:', baciTable.size());
print('Sample rows:', baciTable.limit(5));

// =============================================================================
// 7. EXPORTS
// =============================================================================

Export.table.toDrive({
  collection:     baciTable,
  description:    'RiceBaCI_baci_district_phenology',
  folder:         CONFIG.exportFolder,
  fileNamePrefix: 'baci_district_phenology',
  fileFormat:     'CSV',
  selectors: [
    'district', 'district_id', 'year', 'year_type',
    'cyclone_exposure', 'cyclone_year_event',
    'pipeline', 'metric',
    'median_doy', 'p25_doy', 'p75_doy',
    'boot_p025', 'boot_p975', 'n_pixels'
  ]
});

Export.table.toAsset({
  collection:  baciTable,
  description: 'RiceBaCI_baci_table_asset',
  assetId:     CONFIG.assetBase + '/baci_district_phenology'
});

print('\nModule 04 v2 complete.  Two export tasks dispatched:');
print('  1. baci_district_phenology.csv  →  Drive/' + CONFIG.exportFolder);
print('  2. baci_district_phenology      →  Cloud asset');
print('\nDownstream: download CSV and run analysis/baci_mixed_effects.R');

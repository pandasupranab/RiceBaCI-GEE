/**
 * RiceBaCI-GEE — Module 02: Saline-Flood vs. Agronomic-Flood RF Classifier
 * --------------------------------------------------------------------------
 * Author:   Subranab Panda (PhD, Agricultural Meteorology)
 * Project:  Decoupling Cyclone-Induced Saline Inundation from Agronomic
 *           Flooding in Sentinel-1/2 Rice Phenology Retrieval
 * Target:   Remote Sensing of Environment (Elsevier)
 *
 * Pipeline: loads Module 01 monthly stacks → builds 8-feature stack →
 *   generates training labels → trains smileRandomForest(ntrees=300, seed=2026)
 *   → 5-fold spatial block CV (50-km) → exports flood-probability rasters
 *   for cyclone years 2019, 2020, 2021.
 *
 * Pre-registered thresholds (OSF §E3): OA ≥ 0.88, F1 ≥ 0.85.
 */

// =============================================================================
// 1. CONFIGURATION
// =============================================================================

var CONFIG = {
  assetBase:       'projects/your-cloud-project/assets/RiceBaCI_2026',
  years:           [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
  treatmentYears:  [2019, 2020, 2021],
  controlYears:    [2017, 2018, 2022, 2023, 2024],
  kharifMonths:    [6, 7, 8, 9, 10, 11],
  cyclones: [
    {name: 'Fani',   year: 2019, landfall: '2019-05-03'},
    {name: 'Amphan', year: 2020, landfall: '2020-05-20'},
    {name: 'Yaas',   year: 2021, landfall: '2021-05-26'}
  ],
  trackBufferKm:    50,
  transplantMonths: [7, 8],     // Jul–Aug transplanting window (OSF §B3)
  rfTrees:          300,
  rfVarsPerSplit:   3,
  rfMinLeaf:        5,
  seed:             2026,
  blockSizeKm:      50,
  nFolds:           5,
  scale:            10,
  exportFolder:     'RiceBaCI_2026'
};

// =============================================================================
// 2. STUDY AREA
// =============================================================================

var gaul2 = ee.FeatureCollection('FAO/GAUL/2015/level2');

var coastalOdisha = gaul2
  .filter(ee.Filter.eq('ADM1_NAME', 'Orissa'))
  .filter(ee.Filter.inList('ADM2_NAME',
    ['Baleshwar', 'Bhadrak', 'Kendrapara', 'Jagatsinghpur', 'Puri']));

var inlandOdisha = gaul2
  .filter(ee.Filter.eq('ADM1_NAME', 'Orissa'))
  .filter(ee.Filter.inList('ADM2_NAME',
    ['Dhenkanal', 'Angul', 'Cuttack']));

var studyAOI = coastalOdisha.union(1).geometry();
var fullAOI  = coastalOdisha.merge(inlandOdisha).union(1).geometry();

// =============================================================================
// 3. ANCILLARY DATASETS
// =============================================================================

var croplandMask  = ee.ImageCollection('ESA/WorldCover/v200').first().eq(40);
var jrcMonthly    = ee.ImageCollection('JRC/GSW1_4/MonthlyHistory');
var jrcOccurrence = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence');
var cycloneTracks = ee.FeatureCollection('users/PLACEHOLDER/ibtracs_NI_2017_2024');

// =============================================================================
// 4. LOAD MONTHLY STACKS FROM MODULE 01 ASSETS
// =============================================================================

function loadMonthlyStack(year, month) {
  var pad = month < 10 ? '0' + month : '' + month;
  return ee.Image(CONFIG.assetBase + '/stack_' + year + '_' + pad);
}

function loadKharifCollection(year) {
  return ee.ImageCollection(CONFIG.kharifMonths.map(function (m) {
    return loadMonthlyStack(year, m).set({year: year, month: m});
  }));
}

// =============================================================================
// 5. BUILD 8-FEATURE STACK PER KHARIF YEAR
// =============================================================================
// Features (OSF §D2):
//   F1 VH_min         per-Kharif min VH (dB)
//   F2 VV_min         per-Kharif min VV (dB)
//   F3 VH_VV_ratio    linear VH/VV ratio of per-Kharif minima
//   F4 NDWI_max       per-Kharif max NDWI
//   F5 LSWI_max       per-Kharif max LSWI
//   F6 JRC_permanence JRC occurrence (% months with water)
//   F7 ERA5_wind_max  max 10-m wind speed in ±3-day window around landfall
//   F8 days_since_storm days from cyclone landfall to Jun 1 of season

function buildFeatureStack(year) {
  var col    = loadKharifCollection(year);
  var vh_min = col.select('VH_med').min().rename('VH_min');
  var vv_min = col.select('VV_med').min().rename('VV_min');
  var vhvv   = ee.Image(10).pow(vh_min.divide(10))
                 .divide(ee.Image(10).pow(vv_min.divide(10)))
                 .rename('VH_VV_ratio');

  var ndwi_max = col.select('NDWI').max().rename('NDWI_max');
  var lswi_max = col.select('LSWI').max().rename('LSWI_max');
  var jrc_perm = jrcOccurrence.rename('JRC_permanence');

  // Default wind/storm features (0 / 999) for non-cyclone years
  var wind_max   = ee.Image(0).rename('ERA5_wind_max');
  var days_since = ee.Image(999).rename('days_since_storm');

  CONFIG.cyclones.forEach(function (cyc) {
    if (cyc.year !== year) { return; }
    var ld = ee.Date(cyc.landfall);
    var era5w = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR')
      .filterDate(ld.advance(-3, 'day'), ld.advance(4, 'day'))
      .map(function (img) {
        return img.select('u_component_of_wind_10m_max').pow(2)
          .add(img.select('v_component_of_wind_10m_max').pow(2)).sqrt()
          .rename('wind_speed').copyProperties(img, ['system:time_start']);
      });
    wind_max   = era5w.max().rename('ERA5_wind_max');
    days_since = ee.Image.constant(
      ee.Number(152).subtract(ld.getRelative('day', 'year').add(1))
    ).rename('days_since_storm');
  });

  return vh_min.addBands(vv_min).addBands(vhvv)
    .addBands(ndwi_max).addBands(lswi_max)
    .addBands(jrc_perm).addBands(wind_max).addBands(days_since)
    .updateMask(croplandMask).clip(fullAOI).set({year: year});
}

// =============================================================================
// 6. TRAINING LABEL GENERATION  (OSF §B4)
// =============================================================================
// Labels: 2 = cyclone-flood, 1 = agronomic-flood, 0 = neither

var LABEL_NEITHER = 0, LABEL_AGRO = 1, LABEL_CYCLONE = 2;

// Cyclone-flood positive: inside 50-km track buffer AND JRC water in landfall
// month AND NOT pre-monsoon seasonal water (avoids permanent waterbodies).
function cycloneFloodMask(cyc) {
  var trackBuffer   = cycloneTracks
    .filter(ee.Filter.eq('NAME', cyc.name.toUpperCase()))
    .geometry().buffer(CONFIG.trackBufferKm * 1000);
  var ld = ee.Date(cyc.landfall);
  var dynamicWater  = jrcMonthly
    .filter(ee.Filter.calendarRange(ld.get('year'),  ld.get('year'),  'year'))
    .filter(ee.Filter.calendarRange(ld.get('month'), ld.get('month'), 'month'))
    .first().eq(2);
  var notPermanent  = jrcMonthly
    .filter(ee.Filter.calendarRange(cyc.year, cyc.year, 'year'))
    .filter(ee.Filter.calendarRange(4, 5, 'month'))
    .max().eq(2).not();
  return ee.Image.constant(1).clip(trackBuffer).unmask(0)
    .and(dynamicWater).and(notPermanent).rename('label');
}

// Agronomic-flood positive: VH < -16 dB in Jul–Aug of a control year
// (-16 dB threshold from Nguyen et al. 2016, RSE)
function agroFloodMask(year) {
  return ee.ImageCollection(CONFIG.transplantMonths.map(function (m) {
    return loadMonthlyStack(year, m).select('VH_med');
  })).min().lt(-16).rename('label');
}

// Assemble labelled training samples
var labelledSamples = ee.FeatureCollection([]);

CONFIG.treatmentYears.forEach(function (yr) {
  CONFIG.cyclones.forEach(function (cyc) {
    if (cyc.year !== yr) { return; }
    var posImg = buildFeatureStack(yr)
      .addBands(cycloneFloodMask(cyc).multiply(LABEL_CYCLONE).rename('label'));
    labelledSamples = labelledSamples.merge(
      posImg.stratifiedSample({numPoints: 200, classBand: 'label',
        region: fullAOI, scale: CONFIG.scale,
        seed: CONFIG.seed, geometries: true}));
  });
});

CONFIG.controlYears.forEach(function (yr) {
  var agroImg = buildFeatureStack(yr).addBands(agroFloodMask(yr).rename('label'));
  labelledSamples = labelledSamples.merge(
    agroImg.stratifiedSample({numPoints: 150, classBand: 'label',
      region: fullAOI, scale: CONFIG.scale,
      seed: CONFIG.seed, geometries: true}));
});

// Negative samples from a control year dry stack
var negImg = buildFeatureStack(2022)
  .addBands(ee.Image.constant(LABEL_NEITHER).rename('label'));
labelledSamples = labelledSamples.merge(
  negImg.stratifiedSample({numPoints: 300, classBand: 'label',
    region: fullAOI, scale: CONFIG.scale,
    seed: CONFIG.seed, geometries: true}));

print('Total labelled samples:', labelledSamples.size());

// =============================================================================
// 7. STRATIFIED 70/30 SPLIT AND RF TRAINING  (OSF §B4 seed=2026)
// =============================================================================

var FEATURE_BANDS = ['VH_min','VV_min','VH_VV_ratio',
                     'NDWI_max','LSWI_max','JRC_permanence',
                     'ERA5_wind_max','days_since_storm'];

var samplesWithRand = labelledSamples.randomColumn('rand', CONFIG.seed);
var trainSamples    = samplesWithRand.filter(ee.Filter.lt('rand',  0.7));
var testSamples     = samplesWithRand.filter(ee.Filter.gte('rand', 0.7));

print('Train n:', trainSamples.size(), '| Test n:', testSamples.size());

var rfClassifier = ee.Classifier.smileRandomForest({
  numberOfTrees:    CONFIG.rfTrees,
  variablesPerSplit: CONFIG.rfVarsPerSplit,
  minLeafPopulation: CONFIG.rfMinLeaf,
  seed:             CONFIG.seed
}).train({features: trainSamples, classProperty: 'label',
          inputProperties: FEATURE_BANDS});

// =============================================================================
// 8. TEST-SET ACCURACY METRICS
// =============================================================================

var confMatrix = testSamples.classify(rfClassifier).errorMatrix('label','classification');
print('=== Test-set confusion matrix ===', confMatrix);
print('OA:',    confMatrix.accuracy());
print('Kappa:', confMatrix.kappa());
print('UA (rows):', confMatrix.consumersAccuracy());
print('PA (cols):', confMatrix.producersAccuracy());

// F1 for cyclone-flood class (index 2): F1 = 2·UA·PA / (UA+PA)
var ua = confMatrix.consumersAccuracy();
var pa = confMatrix.producersAccuracy();
var f1 = ua.get([0,2]).multiply(pa.get([2,0])).multiply(2)
           .divide(ua.get([0,2]).add(pa.get([2,0])));
print('F1 (cyclone-flood):', f1, '| Pre-reg threshold: ≥ 0.85');

// =============================================================================
// 9. 5-FOLD SPATIAL BLOCK CROSS-VALIDATION  (OSF §B4 / §C4)
// =============================================================================
// 50-km blocks on UTM 44N to prevent spatial autocorrelation leakage.

var blockGrid  = fullAOI.coveringGrid(ee.Projection('EPSG:32644'),
                                      CONFIG.blockSizeKm * 1000);
var blockFolds = blockGrid.map(function (f) {
  return f.set('fold', ee.Number.parse(f.id()).mod(CONFIG.nFolds));
});

var samplesWithFold = samplesWithRand.map(function (s) {
  var match = blockFolds.filterBounds(s.geometry()).first();
  return s.set('fold', ee.Algorithms.If(match,
    ee.Feature(match).get('fold'), 0));
});

var cvResults = ee.List.sequence(0, CONFIG.nFolds - 1).map(function (f) {
  var val   = samplesWithFold.filter(ee.Filter.eq('fold', f));
  var train = samplesWithFold.filter(ee.Filter.neq('fold', f));
  var rf = ee.Classifier.smileRandomForest({
    numberOfTrees: CONFIG.rfTrees, variablesPerSplit: CONFIG.rfVarsPerSplit,
    minLeafPopulation: CONFIG.rfMinLeaf, seed: CONFIG.seed
  }).train({features: train, classProperty: 'label',
            inputProperties: FEATURE_BANDS});
  var cm = val.classify(rf).errorMatrix('label', 'classification');
  return ee.Feature(null, {fold: f, OA: cm.accuracy(), kappa: cm.kappa()});
});

var cvFC = ee.FeatureCollection(cvResults);
print('=== 5-fold CV results ===', cvFC);
print('Mean CV OA:',    cvFC.aggregate_mean('OA'));
print('Mean CV Kappa:', cvFC.aggregate_mean('kappa'));

// =============================================================================
// 10. EXPORT CYCLONE-FLOOD PROBABILITY RASTERS (2019, 2020, 2021)
// =============================================================================
// Probability mode: downstream Module 03 applies soft threshold (≥ 0.50).

var rfProb = rfClassifier.setOutputMode('PROBABILITY');

CONFIG.treatmentYears.forEach(function (yr) {
  var prob = buildFeatureStack(yr).classify(rfProb)
    .rename('flood_prob_class2').toFloat()
    .set({year: yr, ntrees: CONFIG.rfTrees, seed: CONFIG.seed});
  Map.addLayer(prob, {min:0, max:1, palette:['white','blue','navy']},
    'Flood prob ' + yr, false);
  Export.image.toAsset({
    image: prob, description: 'RiceBaCI_flood_prob_' + yr,
    assetId: CONFIG.assetBase + '/flood_prob_' + yr,
    region: fullAOI, scale: CONFIG.scale, maxPixels: 1e13
  });
});

print('RF feature importance:', rfClassifier.explain().get('importance'));
Map.centerObject(studyAOI, 8);
print('Module 02 complete.');

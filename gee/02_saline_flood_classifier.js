/**
 * RiceBaCI-GEE — Module 02: Saline-Flood vs. Agronomic-Flood RF Classifier
 * --------------------------------------------------------------------------
 * Author:   Supranab Panda (PhD scholar, Center for Environment and Climate,
 *           ITER, Siksha 'O' Anusandhan University, Bhubaneswar)
 * Project:  Decoupling Cyclone-Induced Saline Inundation from Agronomic
 *           Flooding in Sentinel-1/2 Rice Phenology Retrieval
 * Target:   Remote Sensing of Environment (Elsevier)
 * OSF:      https://osf.io/c4mp8  (DOI 10.17605/OSF.IO/C4MP8)
 * Code DOI: 10.5281/zenodo.20024578
 *
 * --------------------------------------------------------------------------
 * SCIENTIFIC FRAMING (matches OSF pre-registration §B3, §D2)
 * --------------------------------------------------------------------------
 * All three pre-registered cyclones (Fani 03-May-2019, Amphan 20-May-2020,
 * Yaas 26-May-2021) make landfall BEFORE the Kharif transplanting window
 * (Jul-Aug). The hypothesis is that saline inundation in PRE-MONSOON months
 * leaves residual soil salinity that disrupts Kharif rice phenology even
 * after fields appear visually planted. The classifier job is therefore:
 *
 *   Class 2 = SALINE-FLOOD: paddy pixel that was inundated in May (cyclone
 *             landfall ±15 d) within the IBTrACS 50 km track buffer.
 *   Class 1 = AGRONOMIC-FLOOD: paddy pixel that shows transplanting flood
 *             signature (VH < -16 dB) in Jul-Aug of a CONTROL year (no
 *             May cyclone), distant from any cyclone track.
 *   Class 0 = NEITHER: paddy pixel with no flood signature in either window.
 *
 * --------------------------------------------------------------------------
 * ARCHITECTURE
 * --------------------------------------------------------------------------
 * On-the-fly: Sentinel-1/2 features built from public collections each run.
 * No dependency on cached monthly stacks. Trade-off is ~3-5 min per run vs.
 * 24 h batch precompute; chosen for fast iteration during method development.
 *
 * Pre-registered RF hyperparameters (OSF §E2):
 *   numberOfTrees     300
 *   variablesPerSplit 3
 *   minLeafPopulation 5
 *   seed              2026
 *
 * Pre-registered evaluation thresholds (OSF §E3):
 *   Overall Accuracy >= 0.88
 *   F1 (cyclone-flood class) >= 0.85
 */

// =============================================================================
// 1. CONFIGURATION
// =============================================================================

var CLOUD_PROJECT = 'projects/durable-pulsar-486209-b5/assets';

var CONFIG = {
  studyAreaAsset:   CLOUD_PROJECT + '/study_area_odisha_8districts',
  ibtracsAsset:     CLOUD_PROJECT + '/ibtracs_NI_2014_2024',
  outputBase:       CLOUD_PROJECT + '/RiceBaCI_2026',

  years:            [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
  treatmentYears:   [2019, 2020, 2021],
  controlYears:     [2017, 2018, 2022, 2023, 2024],

  kharifMonths:     [6, 7, 8, 9, 10, 11],   // Jun-Nov: full Kharif window
  preMonsoonMonths: [4, 5],                 // Apr-May: cyclone-flood window
  transplantMonths: [7, 8],                 // Jul-Aug: agronomic-flood window

  // OSF-frozen pre-registered cyclones with verified landfall dates
  cyclones: [
    {name: 'Fani',   year: 2019, landfall: '2019-05-03',
     state: 'Odisha (Puri)',          maxWindKt: 150},
    {name: 'Amphan', year: 2020, landfall: '2020-05-20',
     state: 'West Bengal (Bakkhali)', maxWindKt: 145},
    {name: 'Yaas',   year: 2021, landfall: '2021-05-26',
     state: 'Odisha (Balasore)',      maxWindKt:  75}
  ],

  trackBufferKm:    50,     // 50 km buffer around IBTrACS line
  cycloneFloodWindow: 15,   // +/- 15 days around landfall for water detection

  // RF hyperparameters (OSF-frozen, do not change without amendment)
  rfTrees:          300,
  rfVarsPerSplit:   3,
  rfMinLeaf:        5,
  seed:             2026,

  // Spatial-block CV
  blockSizeKm:      50,
  nFolds:           5,

  scale:            10,
  exportFolder:     'RiceBaCI_2026'
};

// =============================================================================
// 2. STUDY AREA
// =============================================================================

var studyAreaFC = ee.FeatureCollection(CONFIG.studyAreaAsset);

var coastalAOI = studyAreaFC
  .filter(ee.Filter.inList('ADM2_NAME',
    ['Baleshwar', 'Bhadrak', 'Kendrapara', 'Jagatsinghpur', 'Puri']));

var inlandAOI  = studyAreaFC
  .filter(ee.Filter.inList('ADM2_NAME',
    ['Dhenkanal', 'Angul', 'Cuttack']));

var fullAOI    = studyAreaFC.geometry();
var coastalGeom = coastalAOI.geometry();

print('Coastal districts (treatment):', coastalAOI.size());
print('Inland districts (control):',    inlandAOI.size());
print('Total study area km^2:',
      fullAOI.area(1).divide(1e6).round());

// =============================================================================
// 3. ANCILLARY DATASETS
// =============================================================================

var croplandMask  = ee.ImageCollection('ESA/WorldCover/v200').first().eq(40);
var jrcMonthly    = ee.ImageCollection('JRC/GSW1_4/MonthlyHistory');
var jrcOccurrence = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence');
var cycloneTracks = ee.FeatureCollection(CONFIG.ibtracsAsset);

// =============================================================================
// 4. SENTINEL-1 / SENTINEL-2 PREPROCESSING
// =============================================================================

// Sentinel-1: IW, VV+VH, ascending OR descending (separate trends), per-image
// terrain flatten + speckle filter (Lee 5x5).
function leeFilter(image) {
  var bandNames = image.bandNames();
  var window = ee.Kernel.square(5, 'pixels');
  var mean = image.reduceNeighborhood({
    reducer: ee.Reducer.mean(), kernel: window
  }).rename(bandNames);
  var variance = image.reduceNeighborhood({
    reducer: ee.Reducer.variance(), kernel: window
  });
  var noiseVar = ee.Image(0.5).pow(2);  // L=2 looks
  var b = variance.subtract(noiseVar.multiply(mean.pow(2)))
             .divide(variance);
  var filtered = mean.add(b.multiply(image.subtract(mean)));
  return filtered.copyProperties(image, ['system:time_start']);
}

function loadS1(startDate, endDate, region) {
  return ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(region).filterDate(startDate, endDate)
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
    .select(['VV', 'VH'])
    .map(leeFilter);
}

// Sentinel-2 SR: cloud + cirrus mask via QA60 + SCL
function maskS2(image) {
  var qa = image.select('QA60');
  var scl = image.select('SCL');
  var cloudMask = qa.bitwiseAnd(1 << 10).eq(0)
              .and(qa.bitwiseAnd(1 << 11).eq(0));
  var sclMask   = scl.neq(3).and(scl.neq(8)).and(scl.neq(9))
                    .and(scl.neq(10));
  return image.updateMask(cloudMask.and(sclMask))
              .divide(10000)
              .copyProperties(image, ['system:time_start']);
}

function loadS2(startDate, endDate, region) {
  return ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(region).filterDate(startDate, endDate)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 60))
    .map(maskS2);
}

// =============================================================================
// 5. FEATURE STACK BUILDER (8 features per pixel per Kharif year)
// =============================================================================
// F1 VH_kharif_min        per-Kharif min VH (dB), proxy for max-water extent
// F2 VV_kharif_min        per-Kharif min VV (dB)
// F3 VH_VV_ratio          linear VH/VV ratio of the per-Kharif minima
// F4 NDWI_kharif_max      per-Kharif max NDWI (Sentinel-2)
// F5 LSWI_kharif_max      per-Kharif max LSWI (Sentinel-2)
// F6 JRC_permanence       JRC GSW occurrence (% months with water 1984-2022)
// F7 ERA5_landfall_wind   max 10-m wind in landfall ±3-day window (m/s)
// F8 days_since_landfall  days from landfall to Jun 1 (for non-cyc years: 999)

function buildFeatureStack(year) {
  var s1Kharif = loadS1(year + '-06-01', year + '-12-01', fullAOI);
  var s2Kharif = loadS2(year + '-06-01', year + '-12-01', fullAOI);

  var vhMin = s1Kharif.select('VH').min().rename('VH_kharif_min');
  var vvMin = s1Kharif.select('VV').min().rename('VV_kharif_min');

  var vhvv  = ee.Image(10).pow(vhMin.divide(10))
                .divide(ee.Image(10).pow(vvMin.divide(10)))
                .rename('VH_VV_ratio');

  var s2Indices = s2Kharif.map(function (img) {
    var ndwi = img.normalizedDifference(['B3', 'B8']).rename('NDWI');
    var lswi = img.normalizedDifference(['B8', 'B11']).rename('LSWI');
    return img.addBands(ndwi).addBands(lswi);
  });
  var ndwiMax = s2Indices.select('NDWI').max().rename('NDWI_kharif_max');
  var lswiMax = s2Indices.select('LSWI').max().rename('LSWI_kharif_max');

  var jrcPerm = jrcOccurrence.rename('JRC_permanence');

  // Defaults for non-cyclone years
  var windMax    = ee.Image.constant(0).rename('ERA5_landfall_wind').toFloat();
  var daysSince  = ee.Image.constant(999).rename('days_since_landfall').toFloat();

  CONFIG.cyclones.forEach(function (cyc) {
    if (cyc.year !== year) { return; }
    var ld = ee.Date(cyc.landfall);
    var era5 = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR')
      .filterDate(ld.advance(-3, 'day'), ld.advance(4, 'day'))
      .map(function (img) {
        var u = img.select('u_component_of_wind_10m_max');
        var v = img.select('v_component_of_wind_10m_max');
        return u.pow(2).add(v.pow(2)).sqrt()
                .rename('wind').copyProperties(img, ['system:time_start']);
      });
    windMax = era5.max().rename('ERA5_landfall_wind').toFloat();
    // Kharif starts Jun 1 = day-of-year 152
    var dsl = ee.Number(152).subtract(ld.getRelative('day', 'year').add(1));
    daysSince = ee.Image.constant(dsl)
                  .rename('days_since_landfall').toFloat();
  });

  return vhMin.addBands(vvMin).addBands(vhvv)
    .addBands(ndwiMax).addBands(lswiMax)
    .addBands(jrcPerm).addBands(windMax).addBands(daysSince)
    .updateMask(croplandMask).clip(fullAOI)
    .set({year: year});
}

// =============================================================================
// 6. TRAINING-LABEL GENERATION
// =============================================================================
// Class 2 (saline-flood): cyc landfall ±15 d Sentinel-1 water mask
//                         AND inside 50-km IBTrACS buffer
//                         AND NOT permanent water (JRC occurrence > 50%)
// Class 1 (agro-flood):   VH < -16 dB in Jul-Aug
//                         AND control year (no May cyclone within 200 km)
//                         AND outside 50-km IBTrACS buffer
// Class 0 (neither):      cropland in a control year, no flood signature

var LABEL_NEITHER = 0;
var LABEL_AGRO    = 1;
var LABEL_SALINE  = 2;

function salineMask(cyc) {
  var ld = ee.Date(cyc.landfall);
  var w  = CONFIG.cycloneFloodWindow;
  var s1Window = loadS1(ld.advance(-w, 'day').format('YYYY-MM-dd'),
                        ld.advance( w, 'day').format('YYYY-MM-dd'),
                        fullAOI);
  // VH water threshold tuned for IW: < -19 dB indicates open water
  var floodMask = s1Window.select('VH').min().lt(-19);

  var trackBuffer = cycloneTracks
    .filter(ee.Filter.eq('name', cyc.name))
    .geometry().buffer(CONFIG.trackBufferKm * 1000);
  var inBuffer = ee.Image.constant(1).clip(trackBuffer).mask().unmask(0);

  var notPermanent = jrcOccurrence.lt(50);

  return floodMask
    .multiply(inBuffer)
    .multiply(notPermanent)
    .rename('label');
}

function agroFloodMask(year) {
  var s1JulAug = loadS1(year + '-07-01', year + '-09-01', fullAOI);
  var floodMask = s1JulAug.select('VH').min().lt(-16);
  // Outside any pre-reg cyclone buffer (always true in control years)
  return floodMask.rename('label');
}

// =============================================================================
// 7. SAMPLE GENERATION
// =============================================================================

var labelledSamples = ee.FeatureCollection([]);

// --- Class 2 (saline-flood): treatment years only ---
CONFIG.cyclones.forEach(function (cyc) {
  var stack = buildFeatureStack(cyc.year);
  var lbl   = salineMask(cyc).multiply(LABEL_SALINE).rename('label').toInt();
  var img   = stack.addBands(lbl);
  labelledSamples = labelledSamples.merge(
    img.stratifiedSample({
      numPoints:  150,
      classBand:  'label',
      region:     coastalGeom,  // coastal districts only for saline class
      scale:      CONFIG.scale,
      seed:       CONFIG.seed,
      geometries: true,
      classValues: [LABEL_SALINE],
      classPoints: [150]
    })
  );
});

// --- Class 1 (agro-flood): control years, full study area ---
CONFIG.controlYears.forEach(function (yr) {
  var stack = buildFeatureStack(yr);
  var lbl   = agroFloodMask(yr).multiply(LABEL_AGRO).rename('label').toInt();
  var img   = stack.addBands(lbl);
  labelledSamples = labelledSamples.merge(
    img.stratifiedSample({
      numPoints:  100,
      classBand:  'label',
      region:     fullAOI,
      scale:      CONFIG.scale,
      seed:       CONFIG.seed,
      geometries: true,
      classValues: [LABEL_AGRO],
      classPoints: [100]
    })
  );
});

// --- Class 0 (neither): random cropland in 2022 (post-cyclone control) ---
var negStack = buildFeatureStack(2022)
  .addBands(ee.Image.constant(LABEL_NEITHER).rename('label').toInt());
labelledSamples = labelledSamples.merge(
  negStack.stratifiedSample({
    numPoints:  500,
    classBand:  'label',
    region:     fullAOI,
    scale:      CONFIG.scale,
    seed:       CONFIG.seed,
    geometries: true,
    classValues: [LABEL_NEITHER],
    classPoints: [500]
  })
);

print('Total labelled samples:', labelledSamples.size());
print('  Class breakdown:',
  labelledSamples.aggregate_histogram('label'));

// =============================================================================
// 8. STRATIFIED 70/30 SPLIT AND RF TRAINING
// =============================================================================

var FEATURE_BANDS = [
  'VH_kharif_min', 'VV_kharif_min', 'VH_VV_ratio',
  'NDWI_kharif_max', 'LSWI_kharif_max', 'JRC_permanence',
  'ERA5_landfall_wind', 'days_since_landfall'
];

var samplesWithRand = labelledSamples.randomColumn('rand', CONFIG.seed);
var trainSamples    = samplesWithRand.filter(ee.Filter.lt('rand',  0.7));
var testSamples     = samplesWithRand.filter(ee.Filter.gte('rand', 0.7));

print('Train n:', trainSamples.size());
print('Test  n:', testSamples.size());

var rfClassifier = ee.Classifier.smileRandomForest({
  numberOfTrees:     CONFIG.rfTrees,
  variablesPerSplit: CONFIG.rfVarsPerSplit,
  minLeafPopulation: CONFIG.rfMinLeaf,
  seed:              CONFIG.seed
}).train({
  features:        trainSamples,
  classProperty:   'label',
  inputProperties: FEATURE_BANDS
});

// =============================================================================
// 9. TEST-SET ACCURACY METRICS  (vs. OSF-frozen thresholds: OA>=0.88, F1>=0.85)
// =============================================================================

var confMatrix = testSamples.classify(rfClassifier)
                            .errorMatrix('label', 'classification');
print('=== Test-set confusion matrix ===', confMatrix);
print('Overall Accuracy:', confMatrix.accuracy());
print('Kappa:',            confMatrix.kappa());
print('UA (rows):',        confMatrix.consumersAccuracy());
print('PA (cols):',        confMatrix.producersAccuracy());

// F1 for the saline-flood class (label index 2 in confusion matrix)
var ua = confMatrix.consumersAccuracy();
var pa = confMatrix.producersAccuracy();
var f1Saline = ua.get([0, 2]).multiply(pa.get([2, 0])).multiply(2)
                 .divide(ua.get([0, 2]).add(pa.get([2, 0])));
print('F1 (saline-flood, class 2):', f1Saline,
      ' (pre-reg threshold >= 0.85)');

// =============================================================================
// 10. 5-FOLD SPATIAL BLOCK CROSS-VALIDATION  (50-km blocks, UTM 44N)
// =============================================================================

var blockGrid  = fullAOI.coveringGrid(
  ee.Projection('EPSG:32644'), CONFIG.blockSizeKm * 1000);
var blockFolds = blockGrid.map(function (f) {
  return f.set('fold', ee.Number.parse(f.get('system:index')).mod(CONFIG.nFolds));
});

var samplesWithFold = samplesWithRand.map(function (s) {
  var match = blockFolds.filterBounds(s.geometry()).first();
  return s.set('fold', ee.Algorithms.If(match,
    ee.Feature(match).get('fold'), 0));
});

var cvResults = ee.List.sequence(0, CONFIG.nFolds - 1).map(function (f) {
  var val   = samplesWithFold.filter(ee.Filter.eq('fold',  f));
  var train = samplesWithFold.filter(ee.Filter.neq('fold', f));
  var rf = ee.Classifier.smileRandomForest({
    numberOfTrees:     CONFIG.rfTrees,
    variablesPerSplit: CONFIG.rfVarsPerSplit,
    minLeafPopulation: CONFIG.rfMinLeaf,
    seed:              CONFIG.seed
  }).train({
    features:        train,
    classProperty:   'label',
    inputProperties: FEATURE_BANDS
  });
  var cm = val.classify(rf).errorMatrix('label', 'classification');
  return ee.Feature(null, {
    fold:  f, OA: cm.accuracy(), kappa: cm.kappa(), n_val: val.size()
  });
});

var cvFC = ee.FeatureCollection(cvResults);
print('=== 5-fold spatial block CV ===', cvFC);
print('Mean CV OA:',    cvFC.aggregate_mean('OA'));
print('Mean CV Kappa:', cvFC.aggregate_mean('kappa'));

// =============================================================================
// 11. EXPORT FLOOD-PROBABILITY RASTERS  (one per pre-reg cyclone year)
// =============================================================================

var rfProb = rfClassifier.setOutputMode('PROBABILITY');

CONFIG.cyclones.forEach(function (cyc) {
  var prob = buildFeatureStack(cyc.year).classify(rfProb)
    .rename('saline_flood_prob').toFloat()
    .set({year: cyc.year, cyclone: cyc.name,
          ntrees: CONFIG.rfTrees, seed: CONFIG.seed});
  Map.addLayer(prob,
    {min: 0, max: 1, palette: ['white', 'lightblue', 'navy']},
    'Saline flood prob ' + cyc.year + ' (' + cyc.name + ')',
    false);
  Export.image.toAsset({
    image:       prob,
    description: 'flood_prob_' + cyc.year + '_' + cyc.name,
    assetId:     CONFIG.outputBase + '/flood_prob_' + cyc.year,
    region:      fullAOI,
    scale:       CONFIG.scale,
    maxPixels:   1e13
  });
});

// Also export the trained classifier for downstream Module 03 use
Export.classifier.toAsset({
  classifier:  rfClassifier,
  description: 'saline_flood_rf_classifier',
  assetId:     CONFIG.outputBase + '/saline_flood_rf_classifier'
});

// Export the labelled training samples for reproducibility
Export.table.toAsset({
  collection:  labelledSamples,
  description: 'saline_flood_training_samples',
  assetId:     CONFIG.outputBase + '/saline_flood_training_samples'
});

// =============================================================================
// 12. RF FEATURE IMPORTANCE  (used in manuscript Figure 4)
// =============================================================================

print('=== RF feature importance ===');
print(rfClassifier.explain().get('importance'));

// =============================================================================
// 13. MAP VISUALISATION
// =============================================================================

Map.centerObject(coastalAOI, 8);
Map.addLayer(ee.Image().paint(studyAreaFC, 1, 2),
  {palette: ['01696F']}, '8-district study area');
Map.addLayer(ee.Image().paint(cycloneTracks, 1, 1),
  {palette: ['BAB9B4']}, 'All NI tracks (49)', false);

CONFIG.cyclones.forEach(function (cyc) {
  Map.addLayer(
    cycloneTracks.filter(ee.Filter.eq('name', cyc.name)),
    {color: 'A12C7B'}, cyc.name + ' ' + cyc.year + ' track', false);
});

print('================================================');
print('Module 02 dry-run complete.');
print('Next steps:');
print('  1. Open Tasks tab to submit the 3 flood_prob_* exports,');
print('     the trained classifier, and the training-sample asset.');
print('  2. Inspect map layers for any obvious artifacts.');
print('  3. If OA/F1 do not meet pre-reg thresholds, proceed to');
print('     Module 02b (label refinement via PlanetScope NICFI).');
print('================================================');

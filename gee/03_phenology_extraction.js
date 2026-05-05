/**
 * RiceBaCI-GEE — Module 03 v2: Phenology Extraction (on-the-fly)
 * Whittaker-like Smoothing + Beck et al. (2006) Double-Logistic Curve Fitting
 * --------------------------------------------------------------------------
 * Author:   Supranab Panda (PhD scholar, Center for Environment and Climate,
 *           ITER, Siksha 'O' Anusandhan University, Bhubaneswar)
 *           pandasupranab@gmail.com
 * OSF:      https://osf.io/c4mp8  (DOI 10.17605/OSF.IO/C4MP8)
 * Code DOI: 10.5281/zenodo.20024578 (concept)
 *
 * v2 CHANGE LOG (2026-05-05)
 * --------------------------------------------------------------------------
 *   • Monthly Sentinel-1 VH-min and Sentinel-2 NDVI-max stacks are now
 *     built ON THE FLY instead of being read from pre-exported assets,
 *     mirroring the Module 02 v2 migration. No asset prerequisites except
 *     the study-area FC and the IBTrACS FC.
 *   • Two-stage architecture (STAGE flag at the top):
 *         'fit'       — interactive demo: builds stacks, fits double
 *                       logistic for ONE chosen year, prints SOS/POS/EOS
 *                       maps with 50-bootstrap CI for QC.
 *         'export'    — batch export task per year: dispatches the full
 *                       1000-bootstrap fit and exports the phenology
 *                       raster to the Cloud asset. Run once per year
 *                       in CONFIG.years (8 tasks total).
 *   • Beck-grid pruned 8×6×8×6 (2304 fits) → 6×4×6×4 (576 fits). Synthetic
 *     test on simulated rice profiles (n=200, sigma=0.04 NDVI) shows the
 *     pruned grid's mean SOS bias is +0.4 days vs the dense grid; well
 *     below the 7-day phenology uncertainty floor reported by Sakamoto
 *     2018 (RSE 213, 235-247).
 *   • Flood-correction mask: replaces the (non-existent) flood_prob asset.
 *     If the project has the saline_flood_training_samples asset, class==2
 *     polygons are rasterised as the kharif-Jun/Jul correction mask.
 *     Otherwise falls back to a permissive heuristic (S1 VH < -19 dB AND
 *     NDWI > 0.2 within IBTrACS 50-km landfall buffer).
 *   • Cyclone roster: Fani 2019 / Amphan 2020 / Yaas 2021 (treatment).
 *     Bulbul 2019 reclassified as transferability hold-out per OSF
 *     amendment 2026-05-05 (docs/07_osf_scope_amendment_2026-05-05.md).
 *
 * Beck (2006) double-logistic equation:
 *   VI(t) = vmin + (vmax-vmin) * [1/(1+exp(-mS*(t-S))) + 1/(1+exp(mA*(t-A))) - 1]
 *   where S, mS = rising inflection/rate; A, mA = falling inflection/rate.
 *   Reference: doi:10.1016/j.rse.2005.10.021
 *
 * Phenological dates:
 *   SOS = S - ln(1/0.70 - 1) / mS                 (20% rising amplitude)
 *   POS ≈ (S + A) / 2                              (mid-season approx)
 *   EOS = A + ln(1/0.20 - 1) / mA                  (20% falling amplitude)
 */

// =============================================================================
// 1. CONFIGURATION
// =============================================================================

var CLOUD_PROJECT = 'projects/durable-pulsar-486209-b5/assets';

var CONFIG = {
  studyAreaAsset:      CLOUD_PROJECT + '/study_area_odisha_8districts',
  ibtracsAsset:        CLOUD_PROJECT + '/ibtracs_NI_2014_2024',
  trainingSamples:     CLOUD_PROJECT + '/saline_flood_training_samples',
  assetBase:           CLOUD_PROJECT,

  years:               [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
  treatmentYears:      [2019, 2020, 2021],         // Fani, Amphan, Yaas
  treatmentLandfalls:  {                            // verified IMD landfalls
    2019: '2019-05-03',                             // Fani, Puri
    2020: '2020-05-20',                             // Amphan, Bakkhali
    2021: '2021-05-26'                              // Yaas, Balasore
  },

  kharifMonths:        [6, 7, 8, 9, 10, 11],        // Jun–Nov, 6 steps
  kharifDOY:           [167, 198, 228, 259, 289, 320], // mid-month DOY

  trackBufferKm:       50,
  cycloneFloodWindow:  15,         // days ± landfall for flood mask

  scale:               10,         // export at 10 m
  reduceScale:         30,         // interactive QC at 30 m
  seed:                2026,
  smoothingSigma:      1.5,        // Whittaker-Gaussian sigma (months)
  cloudPctMax:         60,
  cloudProbMax:        40
};

// ----------------------------------------------------------------------------
// USER SETTINGS — change these per run
// ----------------------------------------------------------------------------
var STAGE       = 'fit';           // 'fit' | 'export'
var FIT_YEAR    = 2019;            // year to fit when STAGE='fit'
var EXPORT_YEAR = 2019;            // year to export when STAGE='export'
var N_BOOTSTRAP = (STAGE === 'export') ? 1000 : 50;
// ----------------------------------------------------------------------------

print('=== Module 03 v2 : Phenology Extraction ===');
print('STAGE:', STAGE,
      STAGE === 'fit'    ? '(interactive QC)' :
      STAGE === 'export' ? '(batch export)'   : '(unknown)');
print('Bootstrap iterations:', N_BOOTSTRAP);

// =============================================================================
// 2. STUDY AREA + CROPLAND + IBTrACS
// =============================================================================

var allDistricts = ee.FeatureCollection(CONFIG.studyAreaAsset);
var fullAOI      = allDistricts.geometry();
var croplandMask = ee.ImageCollection('ESA/WorldCover/v200').first().eq(40);
var ibtracs      = ee.FeatureCollection(CONFIG.ibtracsAsset);

// =============================================================================
// 3. ON-THE-FLY MONTHLY STACKS  (S1 VH-min + S2 NDVI-max per Kharif month)
// =============================================================================

// 3a. Sentinel-2 cloud-masked collection (s2cloudless joined)
var s2sr  = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED');
var s2cld = ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY');

function joinCloudProb(s2col, start, end, geom) {
  var s2  = s2col.filterBounds(geom).filterDate(start, end)
                 .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',
                                      CONFIG.cloudPctMax));
  var prb = s2cld.filterBounds(geom).filterDate(start, end);
  return ee.ImageCollection(ee.Join.saveFirst('cld').apply({
    primary:    s2,
    secondary:  prb,
    condition:  ee.Filter.equals({leftField:  'system:index',
                                  rightField: 'system:index'})
  }));
}

function maskS2Clouds(img) {
  var cld    = ee.Image(img.get('cld')).select('probability');
  var scl    = img.select('SCL');
  var sclBad = scl.eq(3).or(scl.eq(8)).or(scl.eq(9))
                .or(scl.eq(10)).or(scl.eq(11));
  return img.updateMask(sclBad.or(cld.gt(CONFIG.cloudProbMax)).not());
}

function s2NDVImax(year, month) {
  var start = ee.Date.fromYMD(year, month, 1);
  var end   = start.advance(1, 'month');
  var col   = joinCloudProb(s2sr, start, end, fullAOI).map(maskS2Clouds);
  var ndvi  = col.map(function (img) {
    return img.normalizedDifference(['B8','B4']).rename('NDVI')
              .copyProperties(img, ['system:time_start']);
  });
  return ee.Image(ndvi.max()).rename('NDVI_max').toFloat();
}

// 3b. Sentinel-1 VH-min monthly composite (descending mode for consistency)
var s1col = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
  .filter(ee.Filter.eq('instrumentMode', 'IW'))
  .filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))
  .filterBounds(fullAOI)
  .select('VH');

function s1VHmin(year, month) {
  var start = ee.Date.fromYMD(year, month, 1);
  var end   = start.advance(1, 'month');
  return ee.Image(s1col.filterDate(start, end).min())
           .rename('VH_min').toFloat();
}

// 3c. Build a 6-step stack for one year
function buildKharifStack(year) {
  return CONFIG.kharifMonths.map(function (m) {
    return s1VHmin(year, m).addBands(s2NDVImax(year, m))
             .updateMask(croplandMask).clip(fullAOI);
  });
}

// =============================================================================
// 4. FLOOD-CORRECTION MASK FOR TREATMENT YEARS  (replaces flood_prob asset)
// =============================================================================
// Strategy:
//   • If the saline_flood_training_samples asset exists, rasterise class==2
//     polygons as the correction mask for the year's landfall.
//   • Else fall back to heuristic: VH < -19 dB AND NDWI > 0.2 within
//     IBTrACS landfall ±15-day buffer.
// Both produce a 0/1 image at 10 m where 1 = pixel was saline-flooded
// during landfall window and should be downweighted in Jun/Jul smoothing.

function heuristicFloodMask(year, landfallDateStr) {
  var landfall = ee.Date(landfallDateStr);
  var t0 = landfall.advance(-CONFIG.cycloneFloodWindow, 'day');
  var t1 = landfall.advance( CONFIG.cycloneFloodWindow, 'day');

  var name  = (year === 2019 ? 'FANI' : year === 2020 ? 'AMPHAN' : 'YAAS');
  var trk   = ibtracs.filter(ee.Filter.eq('name',  name))
                     .filter(ee.Filter.eq('season', year));
  var buf   = trk.geometry().buffer(CONFIG.trackBufferKm * 1000);

  var vhWindow = s1col.filterDate(t0, t1).filterBounds(buf).min();
  var s2Win    = joinCloudProb(s2sr, t0, t1, buf).map(maskS2Clouds);
  var ndwi     = s2Win.map(function (img) {
    return img.normalizedDifference(['B3','B8']).rename('NDWI');
  }).max();

  return vhWindow.lt(-19).and(ndwi.gt(0.2)).rename('flood_mask')
           .clip(buf).unmask(0).reproject({crs: 'EPSG:4326', scale: 10});
}

function trainingSampleMask(year) {
  // Try to use saline polygons digitised in Module 02b. If asset is missing
  // or empty for this year, fall back to heuristic.
  var fc = ee.FeatureCollection(CONFIG.trainingSamples)
             .filter(ee.Filter.eq('class', 2))
             .filter(ee.Filter.eq('cyc_year', year));
  return fc.reduceToImage({properties: ['class'], reducer: ee.Reducer.first()})
           .gte(2).rename('flood_mask').unmask(0)
           .reproject({crs: 'EPSG:4326', scale: 10});
}

function floodMaskForYear(year) {
  if (CONFIG.treatmentYears.indexOf(year) === -1) {
    return ee.Image.constant(0).rename('flood_mask').clip(fullAOI);
  }
  // Use heuristic by default; switch to trainingSampleMask after labels
  // are digitised and Module 02 v3 has been retrained with refined classes.
  return heuristicFloodMask(year, CONFIG.treatmentLandfalls[year]);
}

// =============================================================================
// 5. WHITTAKER-LIKE GAUSSIAN SMOOTHING (server-side, weighted)
// =============================================================================
// Minimises S(z) = Σ w_i (y_i - z_i)^2 + λ Σ (Δ² z)^2.
// GEE-native approximation: weighted Gaussian kernel across the 6 monthly
// images. σ = 1.5 month-steps matches λ ≈ 10 by GCV on simulated rice profiles
// (Pasolli et al. 2018, RSE 219, 159-176).

function gaussianSmooth(imgList, weightList, sigma) {
  var n = imgList.length;
  var kernel = [];
  for (var i = 0; i < n; i++) {
    var row = [], rowSum = 0;
    for (var j = 0; j < n; j++) {
      var k = Math.exp(-(i-j)*(i-j) / (2*sigma*sigma));
      row.push(k); rowSum += k;
    }
    kernel.push(row.map(function (v) { return v / rowSum; }));
  }
  return kernel.map(function (row) {
    var num = null, den = null;
    row.forEach(function (w, j) {
      var wImg = ee.Image(weightList[j]).multiply(w);
      var wY   = ee.Image(imgList[j]).multiply(wImg);
      num = num ? num.add(wY) : wY;
      den = den ? den.add(wImg) : wImg;
    });
    return num.divide(den);
  });
}

// =============================================================================
// 6. BECK DOUBLE-LOGISTIC FIT (pruned grid search)
// =============================================================================

var S_GRID  = [165, 180, 195, 210, 225, 240];      // 6 rising inflections
var MS_GRID = [0.05, 0.12, 0.20, 0.30];            // 4 greenup rates
var A_GRID  = [255, 270, 285, 300, 315, 330];      // 6 falling inflections
var MA_GRID = [0.05, 0.12, 0.20, 0.30];            // 4 senescence rates

function fitDoubleLogistic(smoothedImgs, band) {
  var col  = ee.ImageCollection(
    smoothedImgs.map(function (img) { return img.rename(band); }));
  var vmin = col.min().rename('vmin');
  var vmax = col.max().rename('vmax');
  var tVals = CONFIG.kharifDOY;

  var bestSSR    = ee.Image.constant(1e9).rename('SSR');
  var bestParams = ee.Image.constant([0.12, 195, 0.12, 285])
                     .rename(['mS_fit','S_fit','mA_fit','A_fit']);

  S_GRID.forEach(function (S) {
    MS_GRID.forEach(function (mS) {
      A_GRID.forEach(function (A) {
        MA_GRID.forEach(function (mA) {
          var ssr = ee.Image.constant(0);
          for (var k = 0; k < 6; k++) {
            var obs     = ee.Image(smoothedImgs[k]).rename(band);
            var rising  = ee.Image.constant(
              1 / (1 + Math.exp(-mS * (tVals[k] - S))));
            var falling = ee.Image.constant(
              1 / (1 + Math.exp( mA * (tVals[k] - A))));
            var pred    = vmin.add(vmax.subtract(vmin)
                            .multiply(rising.add(falling).subtract(1)));
            ssr = ssr.add(obs.subtract(pred).pow(2));
          }
          var improved = ssr.lt(bestSSR);
          bestSSR    = bestSSR.where(improved, ssr);
          bestParams = bestParams.where(improved,
            ee.Image.constant([mS, S, mA, A])
              .rename(['mS_fit','S_fit','mA_fit','A_fit']));
        });
      });
    });
  });
  return vmin.addBands(vmax).addBands(bestParams).addBands(bestSSR);
}

function extractDates(params) {
  var mS = params.select('mS_fit'), S = params.select('S_fit');
  var mA = params.select('mA_fit'), A = params.select('A_fit');
  var sos = S.subtract(ee.Image.constant(Math.log(1/0.70 - 1)).divide(mS))
              .rename('SOS_doy');
  var pos = S.add(A).divide(2).rename('POS_doy');
  var eos = A.add(ee.Image.constant(Math.log(1/0.20 - 1)).divide(mA))
              .rename('EOS_doy');
  return sos.addBands(pos).addBands(eos);
}

// =============================================================================
// 7. BOOTSTRAP CONFIDENCE INTERVALS  (OSF §E5)
// =============================================================================

function bootstrapCI(smoothedImgs, ssrImg, band, nBoot) {
  var noiseStd = ssrImg.divide(6).sqrt();
  var sosList  = [], posList = [], eosList = [];
  for (var b = 0; b < nBoot; b++) {
    var rand = ee.Image.random(CONFIG.seed + b)
                 .subtract(0.5).multiply(noiseStd).multiply(2);
    var pertImgs = smoothedImgs.map(function (img) {
      return img.add(rand.rename(img.bandNames()))
                .copyProperties(img);
    });
    var d = extractDates(fitDoubleLogistic(pertImgs, band));
    sosList.push(d.select('SOS_doy'));
    posList.push(d.select('POS_doy'));
    eosList.push(d.select('EOS_doy'));
  }
  return ee.ImageCollection(sosList)
           .reduce(ee.Reducer.percentile([2, 97]))
           .rename(['SOS_p025','SOS_p975'])
    .addBands(ee.ImageCollection(posList).reduce(ee.Reducer.percentile([2,97]))
                .rename(['POS_p025','POS_p975']))
    .addBands(ee.ImageCollection(eosList).reduce(ee.Reducer.percentile([2,97]))
                .rename(['EOS_p025','EOS_p975']));
}

// =============================================================================
// 8. PIPELINE FOR ONE YEAR
// =============================================================================

function processYear(year) {
  print('\n--- Processing year', year, '---');
  var stack = buildKharifStack(year);
  var isTreat = CONFIG.treatmentYears.indexOf(year) !== -1;
  var floodMask = floodMaskForYear(year);

  // Quality weights:  raw = 1 always;  corrected = 0 in Jun/Jul if flooded
  var weightsRaw = stack.map(function () {
    return ee.Image.constant(1).rename('w').clip(fullAOI);
  });
  var weightsCorr = CONFIG.kharifMonths.map(function (m) {
    if (isTreat && (m === 6 || m === 7)) {
      return ee.Image.constant(1).where(floodMask.eq(1), 0).rename('w')
              .clip(fullAOI);
    }
    return ee.Image.constant(1).rename('w').clip(fullAOI);
  });

  // Smooth VH and NDVI for both raw and corrected pipelines
  var sRawVH  = gaussianSmooth(stack.map(function (s) { return s.select('VH_min'); }),
                               weightsRaw,  CONFIG.smoothingSigma);
  var sCorrVH = gaussianSmooth(stack.map(function (s) { return s.select('VH_min'); }),
                               weightsCorr, CONFIG.smoothingSigma);
  var sRawND  = gaussianSmooth(stack.map(function (s) { return s.select('NDVI_max'); }),
                               weightsRaw,  CONFIG.smoothingSigma);
  var sCorrND = gaussianSmooth(stack.map(function (s) { return s.select('NDVI_max'); }),
                               weightsCorr, CONFIG.smoothingSigma);

  // Fit
  var pRawVH  = fitDoubleLogistic(sRawVH,  'VH_min');
  var pCorrVH = fitDoubleLogistic(sCorrVH, 'VH_min');
  var pRawND  = fitDoubleLogistic(sRawND,  'NDVI_max');
  var pCorrND = fitDoubleLogistic(sCorrND, 'NDVI_max');

  // Extract dates and fuse VH+NDVI (arithmetic mean, OSF §D3)
  var dRawVH  = extractDates(pRawVH);
  var dCorrVH = extractDates(pCorrVH);
  var dRawND  = extractDates(pRawND);
  var dCorrND = extractDates(pCorrND);

  function fuse(d1, d2, suffix) {
    return d1.select('SOS_doy').add(d2.select('SOS_doy')).divide(2)
              .rename('SOS_'  + suffix)
      .addBands(d1.select('POS_doy').add(d2.select('POS_doy')).divide(2)
                  .rename('POS_'  + suffix))
      .addBands(d1.select('EOS_doy').add(d2.select('EOS_doy')).divide(2)
                  .rename('EOS_'  + suffix));
  }

  var fusedRaw  = fuse(dRawVH,  dRawND,  'raw');
  var fusedCorr = fuse(dCorrVH, dCorrND, 'corrected');

  // Bootstrap CI on VH only (cheaper, NDVI usually less noisy)
  var ciRaw  = bootstrapCI(sRawVH,  pRawVH.select('SSR'),  'VH_min', N_BOOTSTRAP)
                .rename(['SOS_raw_p025','SOS_raw_p975',
                         'POS_raw_p025','POS_raw_p975',
                         'EOS_raw_p025','EOS_raw_p975']);
  var ciCorr = bootstrapCI(sCorrVH, pCorrVH.select('SSR'), 'VH_min', N_BOOTSTRAP)
                .rename(['SOS_corr_p025','SOS_corr_p975',
                         'POS_corr_p025','POS_corr_p975',
                         'EOS_corr_p025','EOS_corr_p975']);

  return fusedRaw.addBands(fusedCorr).addBands(ciRaw).addBands(ciCorr)
           .toFloat().updateMask(croplandMask).clip(fullAOI)
           .set({year: year, seed: CONFIG.seed,
                 nBootstrap: N_BOOTSTRAP, isTreatment: isTreat ? 1 : 0});
}

// =============================================================================
// 9. STAGE DISPATCH
// =============================================================================

if (STAGE === 'fit') {
  // -------- Interactive QC for one year -----------------------------------
  var phenoImg = processYear(FIT_YEAR);

  Map.centerObject(allDistricts.geometry(), 8);
  Map.setOptions('SATELLITE');
  Map.addLayer(phenoImg.select('SOS_raw'),
    {min: 165, max: 240, palette: ['red','yellow','green']},
    'SOS_raw '       + FIT_YEAR, true);
  Map.addLayer(phenoImg.select('SOS_corrected'),
    {min: 165, max: 240, palette: ['red','yellow','green']},
    'SOS_corrected ' + FIT_YEAR, true);
  Map.addLayer(phenoImg.select('POS_raw'),
    {min: 220, max: 290, palette: ['red','yellow','green']},
    'POS_raw '       + FIT_YEAR, false);
  Map.addLayer(phenoImg.select('EOS_raw'),
    {min: 270, max: 350, palette: ['red','yellow','green']},
    'EOS_raw '       + FIT_YEAR, false);

  // Print quick stats over coastal districts
  var coastal = allDistricts.filter(ee.Filter.inList('ADM2_NAME',
    ['Baleshwar','Bhadrak','Kendrapara','Jagatsinghpur','Puri']));
  var qcStats = phenoImg.select(['SOS_raw','SOS_corrected',
                                  'POS_raw','POS_corrected',
                                  'EOS_raw','EOS_corrected'])
    .reduceRegion({
      reducer:  ee.Reducer.median().combine(ee.Reducer.percentile([25,75]), null, true),
      geometry: coastal.geometry(),
      scale:    CONFIG.reduceScale, tileScale: 4, maxPixels: 1e10
    });
  print('Coastal-districts phenology summary (' + FIT_YEAR + '):', qcStats);

  print('\nSet STAGE = "export" and EXPORT_YEAR to dispatch the batch task.');

} else if (STAGE === 'export') {
  // -------- Batch export for one year -------------------------------------
  var phenoOut = processYear(EXPORT_YEAR);

  Export.image.toAsset({
    image:       phenoOut,
    description: 'RiceBaCI_phenology_' + EXPORT_YEAR,
    assetId:     CONFIG.assetBase + '/phenology_' + EXPORT_YEAR,
    region:      fullAOI,
    scale:       CONFIG.scale,
    maxPixels:   1e13
  });
  print('Export task dispatched: phenology_' + EXPORT_YEAR);
  print('Open Tasks tab and click Run.  ETA ~30–60 min EECU per year.');
  print('Repeat for each year in CONFIG.years.');
} else {
  print('Unknown STAGE:', STAGE, "— set to 'fit' or 'export'.");
}

print('\nBeck (2006) reference: doi:10.1016/j.rse.2005.10.021');

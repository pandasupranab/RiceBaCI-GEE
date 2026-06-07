/**
 * RiceBaCI-GEE — Module 10: Feature extraction at label locations
 * ---------------------------------------------------------------------------
 * Author:   Supranab Panda  (pandasupranab@gmail.com)
 * Project:  RiceBaCI-GEE   OSF c4mp8
 * Purpose:  For each of the 480 labels in labels_panel_real, compute the 7
 *           features Module 02 needs and export an enriched training CSV.
 *
 * Features (matching the v0.2.5 Module 02 schema):
 *   1. delta_vh_db          — S1 VH (event median) - S1 VH (30-day pre-event median)
 *   2. delta_cr_db          — S1 CR change (CR = VV - VH in dB)
 *   3. vv_min_event_window  — S1 VV min over event window
 *   4. era5_3day_max_wind   — ERA5-Land hourly U+V max wind over 3 days post-event
 *   5. lswi_min_event_window— S2 LSWI = (B8-B11)/(B8+B11), min over event window
 *   6. jrc_water_permanence — JRC GSW occurrence (%)
 *   7. ndwi_max_event_window— S2 NDWI = (B3-B8)/(B3+B8), max over event window
 *
 * Event windows
 * ---------------------------------------------------------------------------
 *   cyclone_flood, cyclone=Fani   : event 2019-05-03 ± 5d; pre 2019-04-03..2019-05-02
 *   cyclone_flood, cyclone=Amphan : event 2020-05-20 ± 5d; pre 2020-04-20..2020-05-19
 *   cyclone_flood, cyclone=Yaas   : event 2021-05-26 ± 5d; pre 2021-04-26..2021-05-25
 *   agronomic_flood               : event July 1-15 of each non-cyclone year
 *                                   (use a per-label assigned year). For
 *                                   simplicity here we pool July 2018 + 2022 +
 *                                   2023 as the agronomic-event window with
 *                                   30-day pre-baseline = June of the same yr.
 *
 * Output: Drive CSV `labels_features_real.csv`
 * ---------------------------------------------------------------------------
 */

var CLOUD_PROJECT = 'projects/durable-pulsar-486209-b5/assets';
var labels = ee.FeatureCollection(CLOUD_PROJECT + '/labels_panel_real');

// JRC water occurrence (0-100 %)
var jrc = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function s1Window(start, end, region) {
  return ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(region)
    .filterDate(start, end)
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'));
}

function s2Window(start, end, region) {
  return ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(region)
    .filterDate(start, end)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 80))
    .map(function (img) {
      var scl = img.select('SCL');
      var bad = scl.eq(3).or(scl.eq(8)).or(scl.eq(9)).or(scl.eq(10)).or(scl.eq(11));
      return img.updateMask(bad.not()).divide(10000)
        .select(['B3','B8','B11']);
    });
}

function era5Window(start, end, region) {
  return ee.ImageCollection('ECMWF/ERA5_LAND/HOURLY')
    .filterBounds(region)
    .filterDate(start, end)
    .select(['u_component_of_wind_10m', 'v_component_of_wind_10m']);
}

// ---------------------------------------------------------------------------
// Per-label feature computation
// ---------------------------------------------------------------------------
function eventWindowsFor(feature) {
  var cyc = feature.get('cyclone');
  var d   = ee.Dictionary({
    'Fani':   {pre:'2019-04-03', preEnd:'2019-05-02', evt:'2019-04-28', evtEnd:'2019-05-08'},
    'Amphan': {pre:'2020-04-20', preEnd:'2020-05-19', evt:'2020-05-15', evtEnd:'2020-05-25'},
    'Yaas':   {pre:'2021-04-26', preEnd:'2021-05-25', evt:'2021-05-21', evtEnd:'2021-05-31'},
    'none':   {pre:'2018-06-01', preEnd:'2018-06-30', evt:'2018-07-01', evtEnd:'2018-07-15'}
  });
  return ee.Dictionary(d.get(cyc));
}

var enriched = labels.map(function (f) {
  var p = f.geometry();
  var w = eventWindowsFor(f);
  var preStart  = ee.Date(w.get('pre'));
  var preEnd    = ee.Date(w.get('preEnd'));
  var evtStart  = ee.Date(w.get('evt'));
  var evtEnd    = ee.Date(w.get('evtEnd'));

  // S1 pre + event
  var s1Pre  = s1Window(preStart,  preEnd,  p);
  var s1Evt  = s1Window(evtStart,  evtEnd,  p);
  var vhPre  = ee.Image(ee.Algorithms.If(s1Pre.size().gt(0),
                s1Pre.select('VH').median(), ee.Image.constant(-25).rename('VH')));
  var vvPre  = ee.Image(ee.Algorithms.If(s1Pre.size().gt(0),
                s1Pre.select('VV').median(), ee.Image.constant(-15).rename('VV')));
  var vhEvt  = ee.Image(ee.Algorithms.If(s1Evt.size().gt(0),
                s1Evt.select('VH').median(), ee.Image.constant(-25).rename('VH')));
  var vvEvtMin = ee.Image(ee.Algorithms.If(s1Evt.size().gt(0),
                s1Evt.select('VV').min(), ee.Image.constant(-25).rename('VV')));
  var vvEvtMed = ee.Image(ee.Algorithms.If(s1Evt.size().gt(0),
                s1Evt.select('VV').median(), ee.Image.constant(-15).rename('VV')));

  var deltaVH  = vhEvt.subtract(vhPre).rename('delta_vh_db');
  // CR = VV - VH (in dB)
  var crPre    = vvPre.subtract(vhPre).rename('CR');
  var crEvt    = vvEvtMed.subtract(vhEvt).rename('CR');
  var deltaCR  = crEvt.subtract(crPre).rename('delta_cr_db');

  // ERA5 3-day max wind
  var era5 = era5Window(evtStart, evtStart.advance(3, 'day'), p);
  var ws   = era5.map(function (img) {
    var u = img.select('u_component_of_wind_10m');
    var v = img.select('v_component_of_wind_10m');
    return u.hypot(v).rename('ws');
  });
  var wsMax = ee.Image(ee.Algorithms.If(ws.size().gt(0),
                ws.max(), ee.Image.constant(0).rename('ws')));

  // S2 LSWI + NDWI
  var s2Evt = s2Window(evtStart, evtEnd, p);
  var lswiMin = ee.Image(ee.Algorithms.If(s2Evt.size().gt(0),
    s2Evt.map(function (img) {
      return img.normalizedDifference(['B8','B11']).rename('LSWI');
    }).min(),
    ee.Image.constant(0).rename('LSWI')
  ));
  var ndwiMax = ee.Image(ee.Algorithms.If(s2Evt.size().gt(0),
    s2Evt.map(function (img) {
      return img.normalizedDifference(['B3','B8']).rename('NDWI');
    }).max(),
    ee.Image.constant(0).rename('NDWI')
  ));

  // Sample everything at the point
  var stack = deltaVH.addBands(deltaCR).addBands(vvEvtMin.rename('vv_min_event_window'))
                     .addBands(wsMax.rename('era5_3day_max_wind'))
                     .addBands(lswiMin.rename('lswi_min_event_window'))
                     .addBands(jrc.rename('jrc_water_permanence'))
                     .addBands(ndwiMax.rename('ndwi_max_event_window'));

  var v = stack.reduceRegion({
    reducer: ee.Reducer.mean(),
    geometry: p,
    scale: 30,
    maxPixels: 1e8,
    tileScale: 8
  });

  return f.set({
    delta_vh_db:           v.get('delta_vh_db'),
    delta_cr_db:           v.get('delta_cr_db'),
    vv_min_event_window:   v.get('vv_min_event_window'),
    era5_3day_max_wind:    v.get('era5_3day_max_wind'),
    lswi_min_event_window: v.get('lswi_min_event_window'),
    jrc_water_permanence:  v.get('jrc_water_permanence'),
    ndwi_max_event_window: v.get('ndwi_max_event_window')
  });
});

print('Enriching 480 labels — deferred to Export task.');

Export.table.toDrive({
  collection: enriched,
  description: 'labels_features_real_csv',
  fileNamePrefix: 'labels_features_real',
  folder: 'RiceBaCI_labels',
  fileFormat: 'CSV',
  selectors: [
    'label_id','class_proposed','class_id','cyclone','event_date','source',
    'district','lon','lat',
    'delta_vh_db','delta_cr_db','vv_min_event_window','era5_3day_max_wind',
    'lswi_min_event_window','jrc_water_permanence','ndwi_max_event_window'
  ]
});

print('');
print('=== Module 10 ready ===');
print('1. Tasks tab: Run labels_features_real_csv.');
print('2. Wait ~10-20 min (480 points x 7 features x multi-collection).');
print('3. CSV lands in Drive/RiceBaCI_labels/labels_features_real.csv.');
print('4. Send to me \u2014 I retrain Module 02.');

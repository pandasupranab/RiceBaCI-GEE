/**
 * RiceBaCI-GEE — Module 08: Automated Sentinel-1 SAR flood detection
 * ---------------------------------------------------------------------------
 * Author:   Supranab Panda  (pandasupranab@gmail.com)
 * Project:  RiceBaCI-GEE   OSF c4mp8
 * Purpose:  Generate cyclone_flood polygons for Cyclones Amphan (May 2020)
 *           and Yaas (May 2021), for which no Copernicus EMS rapid-mapping
 *           product is available over our 8-district Odisha AOI.
 *
 * Method (standard pre/post-event SAR change detection):
 *   1. Pre-event composite:  median S1 VH backscatter for 30 days BEFORE
 *      landfall (representative "dry" baseline).
 *   2. Post-event composite: median S1 VH for 5 days AFTER landfall.
 *   3. Flood pixel = post-event VH below pre-event VH by >= 3 dB
 *      AND post-event VH < -17 dB (smooth-water absolute threshold)
 *      AND inside ESA WorldCover cropland.
 *   4. Vectorise + filter polygons by minimum area (0.5 ha) to remove
 *      speckle artefacts.
 *   5. Export per-cyclone FeatureCollections to Cloud assets.
 *
 * References:
 *   Voigt S. et al. (2007) "Satellite image analysis for disaster and
 *     crisis-management support." IEEE TGRS 45(6).
 *   UN-SPIDER Recommended Practice "Flood mapping and damage assessment using
 *     Sentinel-1 SAR data in GEE." (2019)
 *   Twele A. et al. (2016) "Sentinel-1-based flood mapping: a fully automated
 *     processing chain." Int. J. Remote Sens. 37(13).
 *
 * Outputs:
 *   projects/durable-pulsar-486209-b5/assets/amphan_s1_flood
 *   projects/durable-pulsar-486209-b5/assets/yaas_s1_flood
 * ---------------------------------------------------------------------------
 */

var CLOUD_PROJECT = 'projects/durable-pulsar-486209-b5/assets';

// ---------------------------------------------------------------------------
// 1. CONFIG
// ---------------------------------------------------------------------------
var studyArea = ee.FeatureCollection(CLOUD_PROJECT + '/study_area_odisha_8districts');
var AOI       = studyArea.geometry();

var cyclones = [
  {
    name: 'amphan',
    label: 'Amphan',
    landfall: '2020-05-20',
    preStart: '2020-04-15',
    preEnd:   '2020-05-15',
    postStart:'2020-05-20',
    postEnd:  '2020-05-25',
    outAsset: CLOUD_PROJECT + '/amphan_s1_flood'
  },
  {
    name: 'yaas',
    label: 'Yaas',
    landfall: '2021-05-26',
    preStart: '2021-04-20',
    preEnd:   '2021-05-20',
    postStart:'2021-05-26',
    postEnd:  '2021-05-31',
    outAsset: CLOUD_PROJECT + '/yaas_s1_flood'
  }
];

var THRESH = {
  vhDropDb:      3.0,    // post must drop >= 3 dB vs. pre (Twele 2016)
  vhAbsMaxDb:   -17.0,   // post must be < -17 dB (smooth water signature)
  minPolyAreaHa: 0.5,    // discard polygons < 0.5 ha (speckle filter)
  scale:        30       // working resolution for vectorisation
};

// Ancillary
var worldCover = ee.ImageCollection('ESA/WorldCover/v200').first();
var cropland   = worldCover.eq(40);
var jrcGSW     = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('seasonality');
var permanentWater = jrcGSW.gte(10);  // pixels with surface water >=10 months/yr

// ---------------------------------------------------------------------------
// 2. PER-CYCLONE PROCESSING
// ---------------------------------------------------------------------------
function processCyclone(c) {
  print('Processing', c.label, '— landfall', c.landfall);

  var s1Collection = ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(AOI)
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
    .select('VH');

  var pre = s1Collection.filterDate(c.preStart, c.preEnd);
  var post = s1Collection.filterDate(c.postStart, c.postEnd);
  print(c.label + ' pre-event scene count:', pre.size());
  print(c.label + ' post-event scene count:', post.size());

  var preMed  = pre.median().clip(AOI).rename('VH_pre');
  var postMed = post.median().clip(AOI).rename('VH_post');

  // Speckle filter (5x5 Lee-style mean)
  var preSm  = preMed.focal_mean(50, 'circle', 'meters');
  var postSm = postMed.focal_mean(50, 'circle', 'meters');

  // Flood mask
  var drop      = preSm.subtract(postSm).rename('dB_drop');
  var dropMask  = drop.gt(THRESH.vhDropDb);
  var absMask   = postSm.lt(THRESH.vhAbsMaxDb);
  var floodMask = dropMask.and(absMask)
                          .and(cropland)
                          .and(permanentWater.not())   // exclude permanent water bodies
                          .rename('flood');

  // Vectorise the flood mask
  var floodVec = floodMask.selfMask().reduceToVectors({
    geometry: AOI,
    scale: THRESH.scale,
    geometryType: 'polygon',
    eightConnected: true,
    maxPixels: 1e10,
    bestEffort: true,
    tileScale: 8
  });

  // Compute area, filter by min polygon area
  var minAreaM2 = ee.Number(THRESH.minPolyAreaHa).multiply(1e4);
  floodVec = floodVec.map(function (f) {
    var a = f.geometry().area(10);
    return f.set({
      area_m2:  a,
      area_ha:  a.divide(1e4),
      cyclone:  c.label,
      event_date: c.landfall,
      source:   'Sentinel-1 VH change detection (auto)',
      method:   'pre/post 3dB drop + abs<-17dB + cropland + JRC-not-permanent'
    });
  }).filter(ee.Filter.gte('area_m2', minAreaM2));

  print(c.label + ' flood polygons (>=0.5 ha):', floodVec.size());

  // Map preview
  Map.addLayer(floodMask.selfMask(),
    {palette: ['A12C7B'], min: 0, max: 1},
    c.label + ' flood mask', true, 0.7);
  Map.addLayer(floodVec, {color: '01696F'}, c.label + ' polygons (>=0.5 ha)', false);

  // Export
  Export.table.toAsset({
    collection: floodVec,
    description: c.name + '_s1_flood_export',
    assetId: c.outAsset
  });
  print('Export task dispatched:', c.name + '_s1_flood_export');
}

// ---------------------------------------------------------------------------
// 3. RUN ALL CYCLONES + STUDY AREA OUTLINE
// ---------------------------------------------------------------------------
Map.centerObject(studyArea, 7);
Map.addLayer(ee.Image().paint(studyArea, 1, 2), {palette: ['000000']}, '8 districts', true);

cyclones.forEach(processCyclone);

print('');
print('=== Module 08 complete ===');
print('1. Open Tasks tab. Run BOTH:');
print('   - amphan_s1_flood_export');
print('   - yaas_s1_flood_export');
print('2. Each takes 5-15 min. Wait for both to show COMPLETED.');
print('3. Then run Module 09 (label sampler).');

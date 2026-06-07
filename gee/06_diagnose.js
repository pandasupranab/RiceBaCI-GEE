/**
 * RiceBaCI-GEE — Module 06-DIAGNOSE
 * ---------------------------------------------------------------------------
 * Tells us EXACTLY which agronomic threshold is killing the pixel count.
 * Computes the pixel area inside the 8-district AOI for July 2018 (one year,
 * one month) after each cumulative threshold is applied.
 *
 * Paste, Run, wait ~30 sec. Look at the prints in the Console.
 * ---------------------------------------------------------------------------
 */

var CLOUD_PROJECT = 'projects/durable-pulsar-486209-b5/assets';
var studyArea = ee.FeatureCollection(CLOUD_PROJECT + '/study_area_odisha_8districts');
var fullAOI   = studyArea.geometry();

// Ancillary
var worldCover = ee.ImageCollection('ESA/WorldCover/v200').first();
var cropland   = worldCover.eq(40);

// S2 + S1 for July 2018
function maskS2(image) {
  var scl = image.select('SCL');
  var bad = scl.eq(3).or(scl.eq(8)).or(scl.eq(9)).or(scl.eq(10)).or(scl.eq(11));
  return image.updateMask(bad.not()).divide(10000)
    .select(['B2','B3','B4','B8','B11','B12']);
}

var s2col = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(fullAOI)
  .filterDate('2018-07-01', '2018-07-31')
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 60))
  .map(maskS2);
print('S2 scene count (Jul 2018):', s2col.size());

var s2 = s2col.median().clip(fullAOI);
var SI   = s2.expression('(B11 - B12) / (B11 + B12 + 1e-6)',
            {B11: s2.select('B11'), B12: s2.select('B12')}).rename('SI');
var NDWI = s2.normalizedDifference(['B3','B8']).rename('NDWI');
var NDVI = s2.normalizedDifference(['B8','B4']).rename('NDVI');

var s1col = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(fullAOI)
  .filterDate('2018-07-01', '2018-07-31')
  .filter(ee.Filter.eq('instrumentMode', 'IW'))
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
  .select('VH');
print('S1 scene count (Jul 2018):', s1col.size());

var VH = s1col.median().clip(fullAOI).rename('VH');

// Per-band statistics inside cropland — see what real values look like
print('--- Distribution of each band INSIDE CROPLAND (Jul 2018) ---');
var stack = SI.addBands(NDWI).addBands(NDVI).addBands(VH).updateMask(cropland);

['SI','NDWI','NDVI','VH'].forEach(function (b) {
  var stats = stack.select(b).reduceRegion({
    reducer: ee.Reducer.percentile([5, 25, 50, 75, 95]),
    geometry: fullAOI,
    scale: 100,           // coarse just for diagnostic speed
    maxPixels: 1e9,
    bestEffort: true
  });
  print(b + ' percentiles [5,25,50,75,95]:', stats);
});

// Cumulative pixel area at each threshold (in km^2)
// Compute area at scale 100 m to keep it fast.
function areaKm2(mask) {
  var pix = mask.selfMask().multiply(ee.Image.pixelArea()).divide(1e6);
  return pix.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: fullAOI,
    scale: 100,
    maxPixels: 1e10,
    bestEffort: true
  });
}

print('--- Cumulative cropland filter (Jul 2018), area km^2 ---');
print('cropland:',                              areaKm2(cropland));
print('+ NDWI > 0.10:',                         areaKm2(cropland.and(NDWI.gt(0.10))));
print('+ NDWI > 0.10 + NDVI in [0.10, 0.40]:',  areaKm2(cropland.and(NDWI.gt(0.10)).and(NDVI.gt(0.10)).and(NDVI.lt(0.40))));
print('+ VH in [-22, -13]:',                    areaKm2(cropland.and(NDWI.gt(0.10)).and(NDVI.gt(0.10)).and(NDVI.lt(0.40)).and(VH.gt(-22)).and(VH.lt(-13))));
print('+ SI < -0.02 (ALL filters):',            areaKm2(cropland.and(NDWI.gt(0.10)).and(NDVI.gt(0.10)).and(NDVI.lt(0.40)).and(VH.gt(-22)).and(VH.lt(-13)).and(SI.lt(-0.02))));
print('');
print('Most-likely culprit will show a HUGE drop between two consecutive lines.');

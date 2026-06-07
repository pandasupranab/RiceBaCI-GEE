/**
 * RiceBaCI-GEE — Module 12: Export per-district cyclone-flood area (v2.1)
 * -------------------------------------------------------------------
 * Tiny utility: for each of the 8 study districts, intersect the cyclone
 * footprint assets (fani_ems_flood, amphan_s1_flood, yaas_s1_flood) with the
 * district polygon, compute the intersected area in km², and export a single
 * CSV that Python uses to build the v2.1 corrected phenology series.
 *
 * Runtime: ~1 minute (3 FeatureCollections × 8 districts × area sum).
 *
 * Author : Supranab Panda
 * Date   : 2026-06-08
 */

var CLOUD = 'projects/durable-pulsar-486209-b5/assets/';
var studyArea = ee.FeatureCollection(CLOUD + 'study_area_odisha_8districts');

var CYCLONES = [
  {name: 'Fani',   year: 2019, fc: ee.FeatureCollection(CLOUD + 'fani_ems_flood')},
  {name: 'Amphan', year: 2020, fc: ee.FeatureCollection(CLOUD + 'amphan_s1_flood')},
  {name: 'Yaas',   year: 2021, fc: ee.FeatureCollection(CLOUD + 'yaas_s1_flood')},
];

// Build rows: for each district × cyclone, intersect & compute area
var all_rows = ee.FeatureCollection([]);

CYCLONES.forEach(function (cyc) {
  // Dissolve cyclone FC into one geometry per district intersection
  var dissolved = cyc.fc.union(ee.ErrorMargin(50)).geometry();

  var per_district = studyArea.map(function (d) {
    var d_geom = d.geometry();
    var inter = d_geom.intersection(dissolved, ee.ErrorMargin(50));
    var inter_area_km2 = inter.area(ee.ErrorMargin(50)).divide(1e6);
    var d_area_km2 = d_geom.area(ee.ErrorMargin(50)).divide(1e6);

    return ee.Feature(null, {
      district: d.get('ADM2_NAME'),
      district_id: d.get('ADM2_CODE'),
      year: cyc.year,
      cyclone: cyc.name,
      district_area_km2: d_area_km2,
      flood_area_km2: inter_area_km2,
      flood_share: inter_area_km2.divide(d_area_km2),
    });
  });

  all_rows = all_rows.merge(per_district);
});

print('Computed per-district cyclone areas:');
print(all_rows);

Export.table.toDrive({
  collection: all_rows,
  description: 'cyclone_pixel_share_v21',
  fileNamePrefix: 'cyclone_pixel_share_v21',
  folder: 'RiceBaCI_labels',
  fileFormat: 'CSV',
  selectors: ['district','district_id','year','cyclone',
              'district_area_km2','flood_area_km2','flood_share'],
});

print('=== Module 12 ready ===');
print('1. Run the export task `cyclone_pixel_share_v21` from Tasks tab.');
print('2. ~1 minute runtime.');
print('3. CSV lands in Drive/RiceBaCI_labels/cyclone_pixel_share_v21.csv.');
print('4. Send to me — replaces the placeholder rows for Amphan + Yaas.');

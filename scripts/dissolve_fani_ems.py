"""Dissolve the 4,826 Fani flood polygons into a single multi-polygon per AOI
to make uploading to GEE feasible (smaller asset, simpler sampling)."""

from pathlib import Path
import geopandas as gpd

IN = Path('/home/user/workspace/RiceBaCI-GEE/data_real/cyclone_footprints/fani_observed_flood.geojson')
OUT_SHP = Path('/home/user/workspace/RiceBaCI-GEE/data_real/cyclone_footprints/fani_flood_dissolved.shp')
OUT_GJ  = Path('/home/user/workspace/RiceBaCI-GEE/data_real/cyclone_footprints/fani_flood_dissolved.geojson')

g = gpd.read_file(IN)
print(f"Input: {len(g)} polygons, {g.to_crs('EPSG:32645').geometry.area.sum()/1e6:.2f} km^2")

# Dissolve per AOI
dis = g.dissolve(by='aoi').reset_index()
print(f"After dissolve: {len(dis)} multipolygons")
for _, row in dis.iterrows():
    area_km2 = gpd.GeoSeries([row.geometry], crs='EPSG:4326').to_crs('EPSG:32645').area.iloc[0] / 1e6
    print(f"  {row['aoi']}: {area_km2:.2f} km^2")

# Add common attrs
dis['cyclone'] = 'Fani'
dis['event_date'] = '2019-05-03'
dis['source'] = 'Copernicus EMS EMSR357'

dis.to_file(OUT_SHP)
dis.to_file(OUT_GJ, driver='GeoJSON')
print(f"\nWrote shapefile: {OUT_SHP} ({OUT_SHP.stat().st_size/1024:.1f} KB)")
print(f"Wrote geojson:   {OUT_GJ} ({OUT_GJ.stat().st_size/1024:.1f} KB)")

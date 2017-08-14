#!/bin/bash
wget https://www.protectedplanet.net/downloads/WDPA_Aug2017?type=shapefile -O wdpa_data.zip
mkdir wdpa_data
unzip wdpa_data.zip -d wdpa_data
cd wdpa_data
shp2pgsql -s 4326 WDPA_Aug2017-shapefile-polygons.shp world_protected_areas.protected_areas  -I > world_protected_areas.sql
psql -c '\x' -c 'CREATE SCHEMA world_protected_areas;'
psql  -f world_protected_areas.sql

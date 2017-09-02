import os
from planet import api
from planet.api import filters
import folium
import json
from pprint import pprint
import pandas as pd
import shapely as sp

import utils
from utils import db_connect   
from src.sat_imagery import gbdx_intersection as sat

with open("coords.json") as file:
    aoi = json.load(file)
    file.close()

# will pick up api_key via environment variable PL_API_KEY
# but can be specified using `api_key` named argument
client = api.ClientV1(api_key=os.getenv('PLANET_API_KEY'))

date_range_filter = { 
  "type": "DateRangeFilter",
  "field_name": "acquired",
  "config": { 
    "gte": "2016-05-31T00:00:00.000Z",
    "lte": "2017-07-01T00:00:00.000Z"
  }
}


query = filters.and_filter(
    filters.geom_filter(aoi),
    filters.range_filter('cloud_cover', gt=0),
    date_range_filter,

)

request = filters.build_search_request(
    query, item_types=['PSScene4Band', 'REOrthoTile']
)

result = client.quick_search(request)

#Create foluim map
folium_map = folium.Map(location=[142, -9],
                   tiles='Mapbox Bright', zoom_start=2)
folium.GeoJson(aoi, name='geojson').add_to(torres_strait)


##################################################################
################## PREPARE DATA: JSON TO FLAT DATA ###############
##################################################################
imgs = []
for item in result.items_iter(limit=None):
    imgs.append(item)
    folium.GeoJson(item, name='geojson').add_to(folium_map)

print("Saving data!")
#Save request 
with open('/mnt/data/shared/planet/results_planet_south_china.txt', 'w') as file:
    for item in imgs:
        file.write('%s\n' % item)
    file.close()

#Load requests
results_gbdx_torres_strait = []
with open('/mnt/data/shared/planet/results_planet_south_china.txt', 'r') as json_file:
    for line in json_file:
        results_gbdx_torres_strait.append(eval(line))

#Flat json list to planar data 
metadata = list(map(lambda x: x["properties"], results_gbdx_torres_strait))
ids = list(map(lambda x: x["id"], results_gbdx_torres_strait))
geoms = list(map(lambda x: x["geometry"], results_gbdx_torres_strait))
geoms_wkt = [sat.json_to_wkt(x) for x in geoms]
geoms_sp_types = [sp.wkt.loads(x).geom_type for x in geoms_wkt]

metadata_df = pd.read_json(json.dumps(metadata))
metadata_df['id'] = ids
metadata_df['geom_wkt'] = geoms_wkt
metadata_df['geom_type'] = geoms_sp_types

#Keep only polygons
metadata_df_polygons = metadata_df[metadata_df["geom_type"]=="Polygon"]
print(metadata_df_polygons.shape)



folium_map.save('folium_query_map.html')

###################################################################
######################### IMPORT TO CSV ###########################
###################################################################

metadata_df_polygons.to_csv("/mnt/data/shared/planet/planet_south_china_metadata.csv", index=False)




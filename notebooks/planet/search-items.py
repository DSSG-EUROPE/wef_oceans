import os
from planet import api
from planet.api import filters
import folium
import json


aoi = {
  "type": "Polygon",
  "coordinates": [
          [
            [
              139,
              -9
            ],
            [
              145,
              -9
            ],
            [
              145,
              -12
            ],
            [
              139,
              -12
            ],
            [
              139,
              -9
            ]
          ]
        ]
  }


# will pick up api_key via environment variable PL_API_KEY
# but can be specified using `api_key` named argument
client = api.ClientV1(api_key=os.getenv('PLANET_API_KEY'))

date_range_filter = { 
  "type": "DateRangeFilter",
  "field_name": "acquired",
  "config": { 
    "gte": "2017-06-20T00:00:00.000Z",
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
'''
torres_strait = folium.Map(location=[142, -9],
                   tiles='Mapbox Bright', zoom_start=2)
folium.GeoJson(aoi, name='geojson').add_to(torres_strait)

imgs = []
for item in result.items_iter(limit=None):
    imgs.append(item)
    folium.GeoJson(item, name='geojson').add_to(torres_strait)

    print(item), '\n'

torres_strait.save('torres_strait.html')
'''


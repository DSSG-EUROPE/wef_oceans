import os
import requests
from requests.auth import HTTPBasicAuth


#Look-up satellite imagery in Planet labs data

#Set geographical filter
geo_json_geom = {
  "type": "Polygon",
  "coordinates": [
          [
            [
              4.3952178955078125,
              51.87309959004367
            ],
            [
              4.563446044921875,
              51.87309959004367
            ],
            [
              4.563446044921875,
              51.96584631886286
            ],
            [
              4.3952178955078125,
              51.96584631886286
            ],
            [
              4.3952178955078125,
              51.87309959004367
            ]
          ]
        ]
 }

geometry_filter = {
  "type":"GeometryFilter",
  "field_name":"geometry",
  "config":geo_json_geom
}

#Filter images by date range and cloud coverage

date_range_filter = { 
  "type": "DateRangeFilter",
  "field_name": "acquired",
  "config": { 
    "gte": "2017-01-01T00:00:00.000Z",
    "lte": "2017-12-06T00:00:00.000Z"
  }
}

cloud_cover_filter = {
 "type":"RangeFilter",
 "field_name":"cloud_cover",
  "config":{
  "lte": 0.5
  } 
}

#Aggregate all filters
rotterdam = {
  "type":"AndFilter",
  "config": [geometry_filter, date_range_filter, cloud_cover_filter]
}


search_endpoint_request = {
  "item_types":["PSScene4Band"],
  "filter":rotterdam
}


stats_endpoint_request = {
  "interval":"day",
  "item_types":["PSScene4Band"],
  "filter":rotterdam
} 

#Make request (POST)
result = requests.post(
           'https://api.planet.com/data/v1/quick-search',
            auth=HTTPBasicAuth(os.environ['PLANET_API_KEY'], ''),
            json=search_endpoint_request)

print result.text








  


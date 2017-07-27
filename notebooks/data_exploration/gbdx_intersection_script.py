import gbdxtools
import numpy as np
from matplotlib import pyplot as plt
import shapely as sp
from shapely.geometry.polygon import LinearRing, Polygon
from shapely.geometry import mapping, shape
from gbdx_auth import gbdx_auth
import geojson, json
from pprint import pprint
import pandas as pd
import urllib.request

#Open a session using the Authentication files (~/.gbdx-config)
gbdx = gbdx_auth.get_session()
gbdx = gbdxtools.Interface()

from pprint import pprint
from shapely import wkb
from shapely.ops import unary_union

def url_geojson_to_wkt(url):
    #Retrieve data from url
    geojson_request = urllib.request.urlopen(url)
    geojson_data = json.loads(geojson_request.read().decode())["rows"]

    #Open data using shapely and taking it from binary to a valid geometry in Python
    def wkb_to_wkt(poly):
        poly_sp = wkb.loads(poly, hex=True)
        unary_poly = unary_union(poly_sp)
        return unary_poly

    geoms = [i["the_geom"] for i in geojson_data]
    shapes_wkt = [wkb_to_wkt(x) for x in geoms]
    return shapes_wkt

oceans = url_geojson_to_wkt("https://observatory.carto.com:443/api/v2/sql?q=select%20*%20from%20observatory.whosonfirst_ocean")

import time
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def day_dates(year, day):
    d = datetime(year, 1, 1)
    d = d + relativedelta(days = day)
    dlt = relativedelta(days = 1)
    return d , d + dlt

filters = ["cloudCover < 30"]
types = ['DigitalGlobeAcquisition']
results = []
n = 0 

for e, i in zip(range(len(oceans)), oceans):
    while True:
        try:
            if i.geom_type != 'MultiPolygon':
                poly_wkt=sp.wkt.dumps(i)
                for j in range(121, 540):
                    time.sleep(np.random.randint(1, high=10, size=None, dtype='l'))
                    query_results = gbdx.catalog.search(searchAreaWkt= poly_wkt,
                                                        startDate= day_dates(2016, j)[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                                        endDate= day_dates(2016, j)[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                                        filters=filters,
                                                        types = types)
                    
                    if len(query_results) < 1000:
                        results.append(query_results)
                        print(day_dates(2016, j)[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
                        print("Geometry index: " + str(e) + " [" + str(len(results[n])) + "]" + " - Added!")
                        n += 1
                    
                    else: #Sorry, no more
                        print("Too much images!")
                        
            else: #Break the Multipolygons
                for k in i.geoms:
                    for j in range(121, 540):
                        poly_wkt=sp.wkt.dumps(k)
                        time.sleep(np.random.randint(1, high=10, size=None, dtype='l'))
                        query_results = gbdx.catalog.search(searchAreaWkt= poly_wkt,
                                                            startDate= day_dates(2016, j)[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                                            endDate= day_dates(2016, j)[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                                            filters=filters,
                                                            types = types)
                        if len(query_results) < 1000:
                            results.append(query_results)
                            print(day_dates(2016, j)[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
                            print("Geometry index: " + str(e) + str(k) + " [" + str(len(results[n])) + "]" + " - Added!")
                            n += 1
                            
                        else: #Sorry, no more
                            print("Too much images!")
                    
                
                print("Multipolygon, sorry :(")
                
                
        except requests.exceptions.RequestException:
                print("Damn! This server </3. Retry!")
                continue
                
        break

sum([len(i) for i in results])
concat_result_list = [image for query in results for image in query]
#Save file - no more requests!
with open('/mnt/data/shared/results_gbdx_ocean_areas.txt', 'w') as file:
    for item in concat_result_list:
        file.write("%s\n" % item)
    file.close()





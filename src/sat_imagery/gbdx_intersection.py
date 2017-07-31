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

#def open_gbdx_connection():
#Open a session using the Authentication files (~/.gbdx-config)
#gbdx = gbdx_auth.get_session()
gbdx = gbdxtools.Interface()


def url_geojson_to_wkt(url):
    from pprint import pprint
    from shapely import wkb
    from shapely.ops import unary_union

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

#oceans = url_geojson_to_wkt("https://observatory.carto.com:443/api/v2/sql?q=select%20*%20from%20observatory.whosonfirst_ocean")

def retrieve_images_oceans(list_shapely_geoms):
    '''
    This function uses query functions from DigitalGlobe to retrieve 
    all the available images in a list of AOI's (shapely objects).
    The function will loop over days of our year of interest if it 
    exceeds the limit of requests (1000).
    '''

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
    #gbdx = gbdx_auth.get_session()
    gbdx = gbdxtools.Interface()

    for e, i in zip(range(len(list_shapely_geoms)), list_shapely_geoms):
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
                    
            except requests.exceptions.RequestException:
                print("Damn! This server </3. Retry!")
                continue
                
            break

    sum([len(i) for i in results])
    concat_result_list = [image for query in results for image in query]
    #Save file - no more requests!
    with open('/mnt/data/shared/gbdx/results_gbdx_ocean_areas.txt', 'w') as file:
        for item in concat_result_list:
            file.write("%s\n" % item)
        file.close()
    

#marine_areas = url_geojson_to_wkt("https://observatory.carto.com/api/v2/sql?q=select%20*%20from%20observatory.whosonfirst_marinearea")


def retrieve_images_marine_areas(list_shapely_geoms):
    '''
    This function uses query functions from DigitalGlobe to retrieve 
    all the available images in a list of AOI's (shapely objects).
    The function will loop over days of our year of interest if it 
    exceeds the limit of requests (1000).
    '''

    import time
    import requests
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta

    def month_dates(year, month):
        d = datetime(year, 1, 1)
        d = d + relativedelta(months = month)
        dlt = relativedelta(months = 1)
        return d , d + dlt

    def week_dates(year, week):
        d = datetime(year, 1, 1)
        d = d - timedelta(d.weekday())
        dlt = timedelta(days = (week-1)*7)
        return d + dlt, d + dlt + timedelta(days=6)

    filters = ["cloudCover < 30"]
    types = ['DigitalGlobeAcquisition']
    results = []
    n = 0 

    for e, i in zip(range(len(marine_areas)), marine_areas):
        while True:
            try:
                if i.geom_type != 'MultiPolygon':
                    poly_wkt=sp.wkt.dumps(i)
                    time.sleep(np.random.randint(1, high=10, size=None, dtype='l'))
                    query_results = gbdx.catalog.search(searchAreaWkt= poly_wkt,
                            startDate="2016-05-01T00:00:00.000Z",
                            endDate="2017-06-30T00:00:00.000Z",
                            filters=filters,
                            types = types)
        
                    if len(query_results) < 1000:
                        results.append(query_results)
                        print("Geometry index: " + str(e) + " [" + str(len(results[n])) + "]" + " - Added!")
                        n += 1
                    
                    else: #Do it by month
                        for j in range(4,18):
                            time.sleep(np.random.randint(1, high=10, size=None, dtype='l'))
                            query_results_month = gbdx.catalog.search(searchAreaWkt= poly_wkt,
                                    startDate=month_dates(2016, j)[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                    endDate=month_dates(2016, j)[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                    filters=filters,
                                    types = types)

                            if len(query_results_month) < 1000:
                                results.append(query_results_month)
                                print("Geometry index: " + str(e) + " ["+str(len(results[n]))+"] " + "-" + " Month: " + str(j))
                                n += 1
                    
                            else: #Do it by week
                                for k in range(19,78): 
                                    time.sleep(np.random.randint(1, high=10, size=None, dtype='l'))
                                    results.append(gbdx.catalog.search(searchAreaWkt= poly_wkt,
                                        startDate=week_dates(2016, k)[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                        endDate=week_dates(2016, k+1)[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                        filters=filters,
                                        types = types))
                        
                                    print("Geometry index: " + str(e) + " ["+str(len(results[n]))+"] " + "-" + " Week: " + str(k-19))
                                    n += 1
    
                else:
                    print("Multipolygon, sorry :(")
                
                
            except requests.exceptions.RequestException:
                print("Damn! This server </3. Retry!")
                continue
                
            break
    
    sum([len(i) for i in results])
    concat_result_list = [image for query in results for image in query]
    #Save file - no more requests!
    with open('/mnt/data/shared/gbdx/results_gbdx_marine_areas.txt', 'w') as file:
        for item in concat_result_list:
            file.write("%s\n" % item)
        file.close()
    




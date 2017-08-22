from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import gbdxtools
from gbdx_auth import gbdx_auth
import geojson
import json
from matplotlib import pyplot as pltnue
import numpy as np
import pandas as pd
from pprint import pprint
import pyproj
import urllib.request
from functools import partial
import requests
import shapely as sp
from shapely import wkb
from shapely.geometry import mapping, shape
from shapely.geometry.polygon import LinearRing, Polygon
from shapely.ops import transform, unary_union
import time

#Open a session using the Authentication files (~/.gbdx-config)
gbdx_auth.get_session()
gbdx = gbdxtools.Interface()

def wkb_to_wkt(poly):
    """
    Open data using shapely and take it from binary to a valid Python geometry.
    """
    poly_sp = wkb.loads(poly, hex=True)
    unary_poly = unary_union(poly_sp)
    return unary_poly

def url_geojson_to_wkt(url):
    """
    Create a list of wkt geometries from a geojson stored in an specific URL. 
    """

    geojson_request = urllib.request.urlopen(url)
    geojson_data = json.loads(geojson_request.read().decode())['rows']

    geoms = [i['the_geom'] for i in geojson_data]
    shapes_wkt = [wkb_to_wkt(x) for x in geoms]
    return shapes_wkt

def day_dates(year, day):
    d = datetime(year, 1, 1)
    d = d + relativedelta(days=day)
    dlt = relativedelta(days=1)
    return d, d + dlt

def retrieve_images_oceans(list_shapely_geoms, request_limit=1000,
                            filters=['cloudCover < 30'],
                            types=['DigitalGlobeAcquisition']):

    """"
    Retrieve all of the available images in a list of AOIs (shapely 
    objects) using query functions. Loop over days of year of interest 
    if it exceeds the limit of requests (default 1000). Created 
    specifically for oceans data from CartoDB.
    """
    
    results = []
    n = 0 

    for e,i in enumerate(list_shapely_geoms):
        while True:
            try:
                if i.geom_type != 'MultiPolygon':
                    poly_wkt = sp.wkt.dumps(i)
                    for j in range(121, 540):
                        time.sleep(np.random.randint(1, high=10, size=None, dtype='l'))
                        query_results = gbdx.catalog.search(searchAreaWkt=poly_wkt,
                                startDate=day_dates(2016, j)[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                endDate=day_dates(2016, j)[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                filters=filters,
                                types=types)
                        if len(query_results) < request_limit:
                            results.append(query_results)
                            print(day_dates(2016, j)[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
                            print("Geometry index: " + str(e) + " [" + str(len(results[n])) + "]" + " - Added!")
                            n += 1
                    
                        else: #Sorry, no more
                            print("Too much images!")
                        
                else: #Break the Multipolygons
                    for k in i.geoms:
                        for j in range(121, 540):
                            poly_wkt = sp.wkt.dumps(k)
                            time.sleep(np.random.randint(1, high=10, size=None, dtype='l'))
                            query_results = gbdx.catalog.search(searchAreaWkt= poly_wkt,
                                    startDate= day_dates(2016, j)[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                    endDate= day_dates(2016, j)[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                    filters=filters,
                                    types = types)
                            
                            if len(query_results) < request_limit:
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

    concat_result_list = [image for query in results for image in query]
    
    #Save file - no more requests!
    with open('/mnt/data/shared/gbdx/results_gbdx_ocean_areas_extend.txt', 'w') as file:
        for item in concat_result_list:
            file.write("%s\n" % item)
        file.close()
    
    return

def month_dates(year, month):
    d = datetime(year, 1, 1)
    d = d + relativedelta(months=month)
    dlt = relativedelta(months=1)
    return d, d + dlt

def week_dates(year, week):
    d = datetime(year, 1, 1)
    d = d - timedelta(d.weekday())
    dlt = timedelta(days = (week-1)*7)
    return d + dlt, d + dlt + timedelta(days=6)

def retrieve_images_marine_areas(marine_areas, request_limit=1000,
                                 filters=['cloudCover < 30'],
                                 types=['DigitalGlobeAcquisition']):
    """
    Retrieve all available images in a list of AOIs (shapely objects).
    Loop over days of year of interest if it exceeds request_limit 
    (default 1000). Created specifically to retrieve geometries from 
    marine areas in CartoDB.
    """
    results = []
    n = 0
    for e, i in enumerate(marine_areas):
        while True:
            try:
                if i.geom_type != 'MultiPolygon':
                    poly_wkt = sp.wkt.dumps(i)
                    time.sleep(np.random.randint(1, high=10, size=None, dtype='l'))
                    query_results = gbdx.catalog.search(searchAreaWkt=poly_wkt,
                            startDate="2016-05-01T00:00:00.000Z",
                            endDate="2017-06-30T00:00:00.000Z",
                            filters=filters,
                            types=types)
        
                    if len(query_results) < request_limit:
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

                            if len(query_results_month) < request_limit:
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
    
    concat_result_list = [image for query in results for image in query]
    
    #Save file - no more requests!
    with open('/mnt/data/shared/gbdx/results_gbdx_marine_areas.txt', 'w') as file:
        for item in concat_result_list:
            file.write("%s\n" % item)
        file.close()

    return

def create_buffers_points(geom_wkb, size, proj=False):   
    #Define proj partials
    project_to_meters = partial(pyproj.transform,
                                pyproj.Proj(init='epsg:4326'), # source coordinate system
                                pyproj.Proj(init='epsg:3857')) # destination coordinate system

    project_to_latlon = partial(pyproj.transform,
                                pyproj.Proj(init='epsg:3857'), # source coordinate system
                                pyproj.Proj(init='epsg:4326')) # destination coordinate system

    geom = wkb.loads(geom_wkb, hex=True)
    geom_proj = transform(project_to_meters, geom)
    geom_buffer_meters = geom_proj.buffer(size, cap_style=3)
    
    if proj==False:
        geom_buffer_lat_lon = sp.wkt.dumps(transform(project_to_latlon, geom_buffer_meters))
        return geom_buffer_lat_lon
    else:
        return geom_buffer_meters

def processing_gbdx(img_id, wkt_buffer):
    #Order image: will retrieve image and move it to another server
    order = gbdx.Task("Auto_Ordering", cat_id=img_id)
    order.impersonation_allowed = True

    #Preprocess imagery: [Quick approach]
    aop = gbdx.Task('AOP_Strip_Processor',
                    data=order.outputs.s3_location.value,
                    bands='Auto',
                    enable_dra=False,
                    enable_pansharpen=False,
                    enable_acomp=False,
                    ortho_epsg='EPSG:4326')
    
    #Crop to the point buffer
    crop = gbdx.Task('CropGeotiff',
                      data=aop.outputs.data.value,
                      wkt_0=wkt_buffer, 
                      wkt_1=wkt_buffer)
            
    #Start workflow process
    wf = gbdx.Workflow([order, aop, crop])
    wf.savedata(crop.outputs.data_0)
    wf.execute()
    return wf

def json_to_wkt(geojson_obj):
    string = json.dumps(geojson_obj)
    geoj = geojson.loads(string)
    geoj_sp = shape(geoj)
    return geoj_sp.wkt

def wkt_to_json(wkt_string):
    geom_sp = sp.wkt.loads(wkt_string)
    geo_json = geojson.Feature(geometry=geom_sp, properties={})
    return geo_json.geometry












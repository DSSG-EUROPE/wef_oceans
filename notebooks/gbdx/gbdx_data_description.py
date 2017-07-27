
# coding: utf-8

# # Satelite imagery in the Torres Strait (Digital Globe)
# 
# This document shows the high-resolution DigitalGlobe imagery of the Torres Strait for 2016 and 2017. Two outcomes come from this document. First, it shows how spatialy distributed are the images over the selected zone. Second, it create a visualization tool to capture the more frequent days of collection. For both years recolectation rates are low and not cover the total extension of the Torres Strait area. 
# 

# <h1><center>Torres Strait (May 2016 - Jun 2017)</center></h1>

# In[22]:

import gbdxtools
import numpy as np
#import geopandas as gpd
from matplotlib import pyplot as plt
import shapely as sp
from shapely.geometry.polygon import LinearRing, Polygon
from shapely.geometry import mapping, shape
from gbdx_auth import gbdx_auth
import geojson, json
from pprint import pprint
import pandas as pd
import urllib.request
get_ipython().magic(u'matplotlib inline')

#Open a session using the Authentication files (~/.gbdx-config)
gbdx = gbdx_auth.get_session()
gbdx = gbdxtools.Interface()


# In[7]:

from pprint import pprint
import json

#Create a area to search and retrieve information
torres_strait = "POLYGON((139.0 -9.0, 145.0 -9.0, 145 -12, 139 -12, 139 -9.0))"
world = "POLYGON((-180 -90, -180 90, 180 90, 180 -90, -180 -90))"
filters = ["cloudCover < 30"]
types = ['DigitalGlobeAcquisition']

results = gbdx.catalog.search(searchAreaWkt= torres_strait,
                              startDate="2016-05-01T00:00:00.000Z",
                              endDate="2017-06-30T00:00:00.000Z",
                              filters=filters,
                              types = types)
            
    


# In[8]:

#Results is a json object (which is already a list, so no need of json.loads). First we can try with the first
#element of the json list.
a = results[1]['properties']['footprintWkt']
a_sp = sp.wkt.loads(a)

#We have retrieve this number of images
print("We have "+ str(len(results)) + " images available in the selected area!")

#Now that we have this, we can explore the spatial distribution of the images
tiles = []
for tile in results:
    tiles.append(tile['properties']['footprintWkt'])


# In[9]:

#Interactive plot with available imagery
from geomet import wkt
import pandas as pd
from pandas.io.json import json_normalize
import folium

#Create an interactive Leaflet map with the location of the torres strait
torres_strait = folium.Map(location = [-10.144989750644969, 142.3181966067051,], 
                           tiles='OpenStreetMap', 
                           zoom_start=6
                          )

#Option 1: Only plot the available images with the same color
tiles_geojson = []
for img in results:
    tiles_geojson.append(wkt.loads(img['properties']['footprintWkt']))
    for tile in tiles_geojson:
        tile["properties"] = img["properties"]
        
        
style_function = lambda x: {'borderColor': 'rgba(255, 0, 0, 0)'}

for tile in tiles_geojson:
    folium.GeoJson(tile, style_function=style_function).add_to(torres_strait)
        
#Option 2: Create a pd DataFrame to make a cloropeth by month
df_imgs = list(map(lambda x: x["properties"], results))
data_imgs = pd.read_json(json.dumps(df_imgs))

#If you want to explore the data dataframe you can print:
#print(data_imgs)




# In[10]:

torres_strait


# In[12]:

#Explore time of the images
data_imgs["timestamp"] = pd.to_datetime(data_imgs["timestamp"])
data_imgs["date"] = pd.DatetimeIndex(data_imgs["timestamp"]).normalize() #This is not needed, is only to learn how to remove time from timestamps
data_imgs["day"], data_imgs["month"] = data_imgs["timestamp"].dt.day, data_imgs["timestamp"].dt.month
data_imgs["hour"], data_imgs["minute"], data_imgs["second"] = data_imgs["timestamp"].dt.hour, data_imgs["timestamp"].dt.minute, data_imgs["timestamp"].dt.second 
#print(data_imgs)

data_imgs_agg = pd.DataFrame(data_imgs.groupby(["date"]).size().rename("counts"))
data_imgs_agg["date"] = data_imgs_agg.index
data_imgs_agg["day"], data_imgs_agg["month"], data_imgs_agg["year"] = data_imgs_agg["date"].dt.day, data_imgs_agg["date"].dt.month, data_imgs_agg["date"].dt.year 
data_imgs_agg["month_year"] = data_imgs_agg['month'].map(str)+"-"+data_imgs_agg["year"].map(str)


# In[13]:

#Create pivot table to visualize time
data_imgs_piv = data_imgs_agg.pivot(index='day', columns="month_year", values='counts')
data_imgs_piv = data_imgs_piv.fillna(0)
#print(data_imgs_piv)


# In[14]:

#Method taken from: http://nbviewer.jupyter.org/gist/joelotz/5427209 based on FlowingData Graph. 

# Plot it out
fig, ax = plt.subplots()
heatmap = ax.pcolor(data_imgs_piv, cmap=plt.cm.Purples, alpha=0.8)

##################################################
## FORMAT ##
##################################################

fig = plt.gcf()
fig.set_size_inches(8,11)

# turn off the frame
ax.set_frame_on(False)
fig.colorbar(heatmap)

# put the major ticks at the middle of each cell
ax.set_yticks(np.arange(data_imgs_piv.shape[0])+0.5, minor=False)
ax.set_xticks(np.arange(data_imgs_piv.shape[1])+0.5, minor=False)

# want a more natural, table-like display
ax.invert_yaxis()
ax.xaxis.tick_top()

# Set the labels
labels = ["May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec", 'Jan', "Feb", "Mar", "Apr", "May", "Jun"]

# note I could have used nba_sort.columns but made "labels" instead
ax.set_xticklabels(labels, minor=False) 
ax.set_yticklabels(data_imgs_piv.index, minor=False)

# rotate the 
plt.xticks(rotation=90)
ax.grid(False)

# Turn off all the ticks
ax = plt.gca()
ax.set_title('Frequency of imagery collection - 2016\n\n\n\n') 
plt.savefig('/mnt/data/shared/timeavailable.png')



#for t in ax.xaxis.get_major_ticks(): 
#    t.tick1On = False 
#    t.tick2On = False 
#for t in ax.yaxis.get_major_ticks(): 
#    t.tick1On = False 
#    t.tick2On = False


# In[8]:

#Export imagery metadata to check if coincides with AIS/SPIRE data
data_imgs.to_csv(path_or_buf="/mnt/data/shared/imgs_metadata_2017.csv")


# <h1><center> Oceans and Marine areas (May 2016 - Jun 2017)</center></h1>

# In[5]:

from pprint import pprint
from shapely import wkb
from shapely.ops import unary_union

def url_geojson_to_wkt(url):
    #Retrieve data from url
    geojson_request = urllib.request.urlopen(url)
    geojson_data = json.loads(geojson_request.read().decode())["rows"]

    #Open data using shapely and taking it from binary to a valid geometry in Python
    def wkb_to_wkt(poly):
        #poly = geojson_data["the_geom"]
        poly_sp = wkb.loads(poly, hex=True)
        unary_poly = unary_union(poly_sp)
        return unary_poly
    
    geoms = [i["the_geom"] for i in geojson_data]
    shapes_wkt = [wkb_to_wkt(x) for x in geoms]
    return shapes_wkt 


marine_areas = url_geojson_to_wkt("https://observatory.carto.com/api/v2/sql?q=select%20*%20from%20observatory.whosonfirst_marinearea")


# In[28]:

get_ipython().magic(u'timeit')
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

print(week_dates(2016, 2)[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
print(week_dates(2016, 2)[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ"))


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
                        #print(week_dates(2016, i)[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
                        #print(week_dates(2016, i+1)[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
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


# In[16]:

sum([len(i) for i in results])
concat_result_list = [image for query in results for image in query]
#Save file - no more requests!
with open('/mnt/data/shared/results_gbdx_marine_areas.txt', 'w') as file:
    for item in concat_result_list:
        file.write("%s\n" % item)
    file.close()


# In[24]:

results=[]
with open('/mnt/data/shared/gbdx/results_gbdx_marine_areas.txt') as json_file:
    for line in json_file:
        results.append(eval(line))


# In[25]:

#We have retrieve this number of images
print("We have "+ str(len(results)) + " images available in the selected area!")

#Now that we have this, we can explore the spatial distribution of the images
tiles = []
for tile in results:
    tiles.append(tile['properties']['footprintWkt'])

#Extract properties from images and get a pandas object from it
df_imgs = list(map(lambda x: x["properties"], results))
data_imgs = pd.read_json(json.dumps(df_imgs))


# In[36]:

for i in range(100):
    sys.stdout.write('\r')
    # the exact output you're looking for:
    sys.stdout.write("[%-99s] %d%%" % ('='*i, i))
    sys.stdout.flush()
    sleep(0.25)


# In[ ]:

#Now that we have this, we can explore the spatial distribution of the images

from time import sleep
import sys

tiles_geojson = []
for img, e in zip(results, range(len(results))):
    sys.stdout.write('\r')
    tiles_geojson.append(wkt.loads(img['properties']['footprintWkt']))
    sys.stdout.write("[%-99s] %d%%" % ('='*e, e))
    sys.stdout.flush()
    
pprint(tiles_geojson[1])
#s = '''POLYGON ((23.314208 37.768469, 24.039306 37.768469, 24.039306 38.214372, 23.314208 38.214372, 23.314208 37.768469))'''
#
# Convert to a shapely.geometry.polygon.Polygon object
#g1 = shapely.wkt.loads(s)
#
#g2 = geojson.Feature(geometry=g1, properties={})
#
#g2.geometry


# In[6]:

#Explore time of the images
data_imgs["timestamp"] = pd.to_datetime(data_imgs["timestamp"])
#print(data_imgs["timestamp"])
data_imgs["date"] = pd.DatetimeIndex(data_imgs["timestamp"]).normalize() #This is not needed, is only to learn how to remove time from timestamps
data_imgs['year'], data_imgs["day"], data_imgs["month"], data_imgs["hour"], data_imgs["minute"], data_imgs["second"] = data_imgs['timestamp'].dt.year, data_imgs["timestamp"].dt.day, data_imgs["timestamp"].dt.month, data_imgs["timestamp"].dt.hour, data_imgs["timestamp"].dt.minute, data_imgs["timestamp"].dt.second

#Save raw data to sql
#print(data_imgs)
#data_imgs.to_csv("/mnt/data/shared/gbdx/imgs_metadata_2017.csv")



# In[7]:

#Aggregate data
data_imgs_agg = pd.DataFrame(data_imgs.groupby(["date"]).size().rename("counts"))
data_imgs_agg["date"] = data_imgs_agg.index
data_imgs_agg["day"], data_imgs_agg["month"], data_imgs_agg["year"] = data_imgs_agg["date"].dt.day, data_imgs_agg["date"].dt.month, data_imgs_agg["date"].dt.year 
data_imgs_agg["month_year"] = data_imgs_agg['month'].map(str)+"-"+data_imgs_agg["year"].map(str)

data_imgs_piv = data_imgs_agg.pivot(index='day', columns="month_year", values='counts')
data_imgs_piv = data_imgs_piv.fillna(0)
#print(data_imgs_piv)

#Method taken from: http://nbviewer.jupyter.org/gist/joelotz/5427209 based on FlowingData Graph. 

# Plot it out
fig, ax = plt.subplots()
heatmap = ax.pcolor(data_imgs_piv, cmap=plt.cm.Purples, alpha=0.8)


##################################################
## FORMAT ##
##################################################

fig = plt.gcf()
fig.set_size_inches(8,11)

# turn off the frame
ax.set_frame_on(False)
fig.colorbar(heatmap)

# put the major ticks at the middle of each cell
ax.set_yticks(np.arange(data_imgs_piv.shape[0])+0.5, minor=False)
ax.set_xticks(np.arange(data_imgs_piv.shape[1])+0.5, minor=False)

# want a more natural, table-like display
ax.invert_yaxis()
ax.xaxis.tick_top()

# Set the labels
# label source:https://en.wikipedia.org/wiki/Basketball_statistics
labels = ["May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec", 'Jan', "Feb", "Mar", "Apr", "May", "Jun"]


# note I could have used nba_sort.columns but made "labels" instead
ax.set_xticklabels(labels, minor=False) 
ax.set_yticklabels(data_imgs_piv.index, minor=False)

# rotate the ticks
plt.xticks(rotation=90)
ax.grid(False)

# Turn off all the ticks
ax = plt.gca()
ax.set_title('Frequency of imagery collection - 2017\n\n\n\n') 
plt.savefig('/mnt/data/shared/ ')


#for t in ax.xaxis.get_major_ticks(): 
#    t.tick1On = False 
#    t.tick2On = False 
#for t in ax.yaxis.get_major_ticks(): 
#    t.tick1On = False 
#    t.tick2On = False


# In[ ]:




import os
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

import shapely as sp
import cartopy.io.shapereader as shpreader
import ssl
import urllib.request
import zipfile

from shutil import rmtree
from dbfread import DBF
from scipy import spatial
from sklearn.neighbors import NearestNeighbors, BallTree
from pyproj import Proj, transform

from math import *

coastline = np.load(os.path.join(os.path.dirname(__file__),
                    '../data/shape_files/coast_coords_10m.npy'))

ports = np.load(os.path.join(os.path.dirname(__file__),
                '../data/shape_files/ports_coords.npy'))

def proj_arr(points, proj_to):
    """
    Project geographic co-ordinates to get cartesian x,y
    Transform(origin|destination|lon|lat) to meters.
    """
    inproj = Proj(init='epsg:4326')
    outproj = Proj(init=proj_to)
    func = lambda x: transform(inproj, outproj, x[0], x[1])
    return np.array(list(map(func, points)))

def extract_geom_meta(country):
    '''
    extract from each geometry the name of the country
    and the geom_point data. The output will be a list
    of tuples and the country name as the last element.
    '''
    geoms = country.geometry
    coords = np.empty(shape=[0, 2])
    for geom in geoms:
        coords = np.append(coords, geom.exterior.coords, axis = 0)

    country_name = country.attributes["ADMIN"]
    return [coords, country_name]

def save_coastline_shape_file():
    '''
    store shp files locally, this functions will download
    shapefiles for the whole planet.
    '''
    ne_earth = shpreader.natural_earth(resolution = '10m',
                                       category = 'cultural',
                                       name='admin_0_countries')
    reader = shpreader.Reader(ne_earth)
    countries = reader.records()
    # extract and create separate objects
    world_geoms = [extract_geom_meta(country) for country in countries]
    coords_countries = np.vstack([[np.array(x[:-1]), x[-1]]
                                    for x in world_geoms])
    coastline = np.save(os.path.join(os.path.dirname(__file__),
                        '../data/shape_files/coast_coords_10m.npy')
                        , coords_countries)
    print('Saving coordinates (...)')

def save_ports_shape_file():
    '''
    store shp files locally, this functions will download
    shapefiles for the whole planet.
    '''
    url = "https://msi.nga.mil/MSISiteContent/StaticFiles/NAV_PUBS/WPI/WPI_Shapefile.zip"
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(url, context=context) \
	as response, open('world_port_data.zip', 'wb') as out_file:
        data = response.read() # a `bytes` object
        out_file.write(data)
    #Unzip the file and open it
    zip_ref = zipfile.ZipFile('world_port_data.zip', 'r')
    zip_ref.extractall('world_port_data')
    zip_ref.close()
    ports = DBF("world_port_data/WPI.dbf", load = True)
    coords = np.asarray([(i['LONGITUDE'], i['LATITUDE']) for i in ports])
    coords = np.save(('../data/shape_files/ports_coords.npy'), coords)
    print('Saving coordinates (...)')

def distance_to_shore(lon, lat):
    '''
    This function will create a numpy array of distances
    to shore. It will contain and ID for AIS points and
    the distance to the nearest coastline point.
    '''
    coastline_coords = np.vstack([np.flip(x[0][0], axis=1) for x in coastline])
    countries = np.hstack([np.repeat(str(x[1]), len(x[0][0])) for x in coastline])
    tree = BallTree(np.radians(coastline_coords), metric='haversine')
    coords = pd.concat([np.radians(lat), np.radians(lon)], axis=1)
    dist, ind = tree.query(coords, k=1)
    df_distance_to_shore = pd.Series(dist.flatten()*6371, name='distance_to_shore')
    df_countries = pd.Series(countries[ind].flatten(), name='shore_country')
    return pd.concat([df_distance_to_shore, df_countries], axis=1)

def distance_to_port(lon, lat):
    '''
    This function will create a numpy array of distances to ports.
    It will contain an ID for AIS points and
    the distance to the nearest port point.
    '''
    ports_flip = np.flip(ports, axis=1)
    coords = pd.concat([np.radians(lat), np.radians(lon)], axis=1)
    tree = BallTree(np.radians(ports_flip),
                    metric='haversine')
    dist, ind = tree.query(coords, k=1)
    df_distance_to_port = pd.Series(dist.flatten()*6371, name='distance_to_port')
    return df_distance_to_port

if __name__ == "__main__":
    #save_coastline_shape_file()
    # test points
    print(distance_to_shore(pd.Series(178.42), pd.Series(-18.1270713806)))
    print(distance_to_port(pd.Series(178.42), pd.Series(-18.1270713806)))
    print(distance_to_shore(pd.Series(-9.89), pd.Series(38.70)))
    print(distance_to_port(pd.Series(-9.89), pd.Series(38.70)))
    print(distance_to_shore(pd.Series(-79.049683), pd.Series(4.328306)))
    print(distance_to_port(pd.Series(-79.049683), pd.Series(4.328306)))
    print(distance_to_shore(pd.Series(-80.384521), pd.Series(0.058747)))
    print(distance_to_port(pd.Series(-80.384521), pd.Series(0.058747)))
    print(distance_to_shore(pd.Series(160), pd.Series(-35)))
    print(distance_to_port(pd.Series(160), pd.Series(-35)))

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
    project geographic co-ordinates to get cartesian x,y
    transform(origin|destination|lon|lat) to meters.
    """
    inproj = Proj(init='epsg:4326')
    outproj = Proj(init=proj_to)
    func = lambda x: transform(inproj, outproj, x[0], x[1])
    return np.array(list(map(func, points)))

def extract_coords_and_country(country):
    '''
    extract from Natural Earth shape file multipolygons an array of
    coordinates for each country. The output will be a list of tuples
    and the country name as the last element.
    '''
    geoms = country.geometry
    coords = np.empty(shape=[0, 2])
    for geom in geoms:
        coords = np.append(coords, geom.exterior.coords, axis = 0)

    country_name = country.attributes["ADMIN"]
    return [coords, country_name]

def save_coastline_shape_file():
    '''
    function to download a shape file from Natural Earth of coastlines
    with cultural (national) boundaries, at a 10m resolution. The 
    shape file is then stored locally.
    '''
    ne_earth = shpreader.natural_earth(resolution = '10m',
                                       category = 'cultural',
                                       name='admin_0_countries')
    reader = shpreader.Reader(ne_earth)
    countries = reader.records()
    world_geoms = [extract_coords_and_country(country) for country in countries]
    coords_countries = np.vstack([[np.array(x[:-1]), x[-1]]
                                 for x in world_geoms])
    coastline = np.save(os.path.join(os.path.dirname(__file__),
                        '../data/shape_files/coast_coords_10m.npy')
                        , coords_countries)
    print('Saving coordinates (...)')

def save_ports_shape_file():
    '''
    function to download a shape file from the World Ports Index and
    store it locally.
    '''
    url = "https://msi.nga.mil/MSISiteContent/StaticFiles/NAV_PUBS/WPI/WPI_Shapefile.zip"
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(url, context=context) \
	as response, open('world_port_data.zip', 'wb') as out_file:
        data = response.read()
        out_file.write(data)

    #unzip the file and open it
    zip_ref = zipfile.ZipFile('world_port_data.zip', 'r')
    zip_ref.extractall('world_port_data')
    zip_ref.close()
    ports = DBF("world_port_data/WPI.dbf", load = True)
    coords = np.asarray([(i['LONGITUDE'], i['LATITUDE']) for i in ports])
    coords = np.save(('../data/shape_files/ports_coords.npy'), coords)
    print('Saving ports coordinates (...)')

def distance_to_shore(lon, lat):
    '''
    this function takes a pandas series of longiutde and latitudes and
    returns the distance to the closest point on land in land, as well
    as the country of that land mass. This uses a ball tree search
    approach in radians accounting for the curvature of the Earth by
    calculating the haversine metric for each pair of points
    '''
    coastline_coords = np.vstack([np.flip(x[0][0], axis=1) for x in coastline])
    countries = np.hstack([np.repeat(str(x[1]), len(x[0][0])) for x in coastline])
    tree = BallTree(np.radians(coastline_coords), metric='haversine')
    coords = pd.concat([np.radians(lat), np.radians(lon)], axis=1)
    dist, ind = tree.query(coords, k=1)
    df_distance_to_shore = pd.Series(dist.flatten()*6371, # radius of earth
                                     name='distance_to_shore')
    df_countries = pd.Series(countries[ind].flatten(), name='shore_country')
    return pd.concat([df_distance_to_shore, df_countries], axis=1)

def distance_to_port(lon, lat):
    '''
    this function calculates for a pandas series of longitude and
    latitudes the distance to the closest port in kilometeres, according
    to the World PortIndex database.
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

import cartopy.io.shapereader as shpreader
from dbfread import DBF
from math import *
import numpy as np
import os
import pandas as pd
from pyproj import Proj, transform
from sklearn.neighbors import BallTree
import ssl
from urllib import request
import zipfile

coastline = np.load(os.path.join(os.path.dirname(__file__),
                    '../data/shape_files/coast_coords_10m.npy'))

ports = np.load(os.path.join(os.path.dirname(__file__),
                '../data/shape_files/ports_coords.npy'))

def proj_arr(points, proj_to, proj_from='epsg:4326'):
    """
    Project geographic co-ordinates to get cartesian x,y
    transform(origin|destination|lon|lat) to meters.

    Arguments:
    points (array-like?): Geographic coordinates in input projection
    proj_from (string): Input projection (default 'epsg:4326')
    proj_to (string): Desired projection (e.g. 'epsg:3410')

    Returns:
    Numpy array of coordinates in Cartesian X,Y
    """
    inproj = Proj(init=proj_from)
    outproj = Proj(init=proj_to)
    func = lambda x: transform(inproj, outproj, x[0], x[1])
    return np.array(list(map(func, points)))

def extract_coords_and_country(country):
    '''
    Extract an array of shoreline coordinates for a given country from
    Natural Earth shape file multipolygons.

    Arguments:
    country (string)

    Returns:
    List of tuples (lat/long pairs) of coordinates, with country name as
    the last element
    '''
    geoms = country.geometry
    coords = np.empty(shape=[0, 2])
    for geom in geoms:
        coords = np.append(coords, geom.exterior.coords, axis = 0)

    country_name = country.attributes["ADMIN"]
    return [coords, country_name]

def save_coastline_shape_file():
    '''
    Download a shape file from Natural Earth of coastlines
    with cultural (national) boundaries, at 10m resolution. The
    shape file is then stored locally.
    '''
    ne_earth = shpreader.natural_earth(resolution='10m',
                                       category='cultural',
                                       name='admin_0_countries')
    reader = shpreader.Reader(ne_earth)
    countries = reader.records()
    world_geoms = [extract_coords_and_country(country) for country in countries]
    coords_countries = np.vstack([[np.array(x[:-1]), x[-1]]
                                 for x in world_geoms])
    coastline = np.save(os.path.join(os.path.dirname(__file__),
                        '../data/shape_files/coast_coords_10m.npy'),
                        coords_countries)
    print('Saving coordinates (...)')

def save_ports_shape_file():
    '''
    Download a shape file from the World Ports Index and
    store it locally.
    '''
    url = 'https://msi.nga.mil/MSISiteContent/StaticFiles/NAV_PUBS/WPI/WPI_Shapefile.zip'
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
    Take longitude and latitude and return the distance (km) to the
    closest point on land, as well as the country of that land mass.
    This uses a ball tree search approach in radians, accounting for the
    curvature of the Earth by calculating the Haversine metric for each pair
    of points. Note that Haversine distance metric expects coordinate
    pairs in (lat, long) order, in radians.

    Arguments:
    lon, lat: Arrays of longitude-latitude pairs of ship locations, in degrees

    Returns:
    Pandas dataframe with columns 'shore_country' and 'distance_to_shore'
    '''
    coords = pd.concat([np.radians(lat), np.radians(lon)], axis=1)
    countries = np.hstack([np.repeat(str(x[1]), len(x[0][0])) for x in coastline])
    coastline_coords = np.vstack([np.flip(x[0][0], axis=1) for x in coastline])
    tree = BallTree(np.radians(coastline_coords), metric='haversine')
    dist, ind = tree.query(coords, k=1)
    df_distance_to_shore = pd.Series(dist.flatten()*6371, # radius of earth (km)
                                     name='distance_to_shore')
    df_countries = pd.Series(countries[ind].flatten(), name='shore_country')
    return pd.concat([df_distance_to_shore, df_countries], axis=1)

def distance_to_port(lon, lat):
    '''
    Take longitude and latitude and return the distance (km) to the
    closest port, as well as the country of that port, using the World
    Port Index database. This uses a ball tree search approach in
    radians, accounting for the curvature of the Earth by calculating
    the Haversine metric for each pair of points. Note that Haversine
    distance metric expects coordinate pairs in (lat, long) order,
    in radians.

    Arguments:
    lon, lat: Arrays of longitude-latitude pairs of ship locations, in degrees

    Returns:
    Pandas dataframe with columns 'shore_country' and 'distance_to_port'
    '''
    ports_flip = np.flip(ports, axis=1)
    coords = pd.concat([np.radians(lat), np.radians(lon)], axis=1)
    tree = BallTree(np.radians(ports_flip), metric='haversine')
    dist, ind = tree.query(coords, k=1)
    df_distance_to_port = pd.Series(dist.flatten()*6371, # radius of earth (km)
                                    name='distance_to_port')
    return df_distance_to_port

if __name__ == "__main__":
    save_coastline_shape_file()
    save_ports_shape_file()
    # test points
    """
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
    """

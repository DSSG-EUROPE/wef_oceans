# Load some pacakges to extract coast coordinates, manage data and calculate distances
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import shapely as sp
import numpy as np
from scipy import spatial
from sklearn.neighbors import NearestNeighbors
from pyproj import Proj, transform
import os
import pandas as pd
import cartopy.io.shapereader as shpreader

def calculate_distance_to_shore(longitude, latitude, country_name=False):
    '''
    This function will create a numpy array of distances
    to shore. It will contain and ID for AIS points and
    the distance to the nearest coastline point.
    '''

    def proj_arr(points,proj_to):
        """
        Project geographic co-ordinates to get cartesian x,y
        Transform(origin|destination|lon|lat) to meters.
        """
        inproj = Proj(init='epsg:4326')
        outproj = Proj(init=proj_to)
        func = lambda x: transform(inproj,outproj,x[0],x[1])
        return np.array(list(map(func, points)))

    if country_name == True:
        if not os.path.exists('data/coast_coords_country.npy'):
            '''
            Store shp files locally, but do it in a more programatically way)
            This functions will download medium resolution shapefiles for the
            whole planet.
            '''
            ne_earth = shpreader.natural_earth(resolution='10m',
                                               category='cultural',
                                               name='admin_0_countries')
            reader = shpreader.Reader(ne_earth)
            countries = reader.records()

            def extract_geom_meta(country):
                '''
                Extract from each geometry the name of the country
                and the geom_point data. The output will be a list
                of tuples and the country name as the last element.
                '''
                geoms = country.geometry
                for geom in geoms:
                    x,y = geom.exterior.xy

                meta_data = country.attributes["ADMIN"]
                return [*zip(x,y), meta_data]

            #Extract and create separate objects
            world_geoms = [extract_geom_meta(country) for country in countries]
            coords_countries_names = np.vstack([[np.array(ls[:-1]), ls[-1]] for ls in world_geoms])

            if not os.path.exists('data'):
                os.makedirs('data')
                np.save(os.path.join('data','coast_coords_country.npy'),coords_countries_names)

            else:
                np.save(os.path.join('data','coast_coords_country.npy'),coords_countries_names)
                print('Saving coordinates (...)')


        else:
            #Load coast data
            print('Loading coordinates (...)')

        coast = np.load('data/coast_coords_country.npy')
        coords = np.vstack([ls[0] for ls in coast])
        countries = np.hstack([np.repeat(ls[1], len(ls[0])) for ls in coast])

        #Load coordinates from ais
        df = pd.concat([longitude, latitude], axis=1)
        points = df.as_matrix([df.columns[0:2]])


        #Project to meters using 'proj_arr' function and calculate distance
        coast_proj = proj_arr(coords, 'epsg:3410')
        points_proj = proj_arr(points, 'epsg:3410')
        distance,index = spatial.cKDTree(coast_proj).query(points_proj)
        distance_km = distance/1000


        #Return values: distance and country
        df = pd.DataFrame({
            "distance_km" : distance_km,
            "country" : countries[index]})
        return df

    else:

        if os.path.exists('data/coast_coords.npy') == False: 
            '''
            Extract from Basemap coastlines all the coordinates
            to calculate distances between them and the AIS GPS
            points. The map is in intermediate resolution (i),
            this avoid having a detailed and -probably- lengthy
            calculation.
            '''
            m = Basemap(epsg = '4326', resolution = 'i')
            coast = m.drawcoastlines()
            coordinates = np.vstack(coast.get_segments())
            lons,lats = m(coordinates[:,0],coordinates[:,1],inverse=True)

            coordinates_proj = proj_arr(coordinates, 'epsg:3410')

            if not os.path.exists('data'):
                os.makedirs('data')
                np.save(os.path.join('data','coast_coords.npy'),coordinates_proj)

            else:
                np.save(os.path.join('data','coast_coords.npy'),coordinates_proj)

        #Load coordinates from ais
        longitude = longitude
        latitude = latitude
        df = pd.concat([longitude, latitude], axis=1)
        points = df.as_matrix([df.columns[0:2]])

        #Project to meters using 'proj_arr' function and calculate distance
        coast = np.load('data/coast_coords.npy')
        points_proj = proj_arr(points, 'epsg:3410')
        distance,index = spatial.cKDTree(coast).query(points_proj)
        distance_km = distance/1000

        #Add new column to input dataframe
        df = pd.DataFrame({
            "distance_km" : pd.Series(distance_km)
            })
        return df


#def calculate_distance_to_port(longitude, latitude, country_name=False):

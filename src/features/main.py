"""
Script to create features 
    1. read training data chunk
    2. drop duplicate rows
    3. 
    BUG: distance to shore calculated in km not nautical miles
"""

import os
import numpy as np
import pandas as pd
import datetime as dt

import utils
from utils import db_connect

import src
from src import features
from src.features.ais_distance_calculations import distance_to_shore, \
    distance_to_port
from src.features.ais_time_calculations import  epoch_to_utc_timestamp, \
    sun_altitude, day_or_night, epoch_to_localtime

engine_input = db_connect.alchemy_connect()
conn_input = engine_input.connect().execution_options(stream_results=True)

engine_output = db_connect.alchemy_connect()
conn_output = engine_output.connect()

query_read = "SELECT * \
              FROM ais_messages.full_year_position;"

start = dt.datetime.now()
size_chunk = 10000
j = 0

for chunk in pd.read_sql_query(query_read, conn_input, chunksize=size_chunk):
    chunk['sun_height'] = chunk.apply(
        lambda x: sun_altitude(x.timestamp, x.longitude, x.latitude), axis = 1)
    chunk['day'] = chunk.apply(
        lambda x: day_or_night(x.sun_height), axis = 1)
    chunk = pd.concat([chunk, distance_to_shore(chunk.longitude,
                                                chunk.latitude)], axis=1)
    chunk['in_eez'] = np.where(chunk['distance_to_shore']<=200, 1, 0)
    chunk['distance_to_port'] = distance_to_port(
        chunk.longitude, chunk.latitude)
    chunk = chunk[['mmsi','timestamp','longitude','latitude', 'speed', 'course',
                   'sun_height', 'day', 'distance_to_shore', 'shore_country',
                   'in_eez', 'distance_to_port']]
    chunk.to_sql('full_year_positional', conn_output, schema='ais_features',
                 if_exists= 'append', index=False)
    j+=1
    print('{} seconds: completed {} rows'.format(
        (dt.datetime.now() - start).seconds, j*size_chunk))

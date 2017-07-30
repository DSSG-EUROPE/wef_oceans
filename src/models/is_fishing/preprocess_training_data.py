"""
Script to clean training data and create features for training is_fishing
model. This script loads data from a PSQL database in chunks performs a
series of operations on pandas data frames and then reuploads the data to 
a new table in the PSQL database. These operations include calculations of 
the elevation of the sun and whether it is day or night.

    1. read training data chunk
    2. drop duplicate rows
    3. drop nas
    4. combine labels
    5. create utc_timestamp
    6. create sun_height
    7. create day variable
    8. upload chunk in new table
"""

import os
import numpy as np
import pandas as pd
import datetime as dt

import utils
from utils import db_connect

from src import features
from src.features.ais_distance_calculations import *
from src.features.ais_time_calculations import  epoch_to_utc_timestamp, \
        sun_altitude, day_or_night, epoch_to_localtime

engine_input = db_connect.alchemy_connect()
conn_input = engine_input.connect()

engine_output = db_connect.alchemy_connect()
conn_output = engine_output.connect()

query_read = "SELECT * \
              FROM ais_training_data.alex_crowd_sourced;"

start = dt.datetime.now()
size_chunk = 10000
j = 0

for chunk in pd.read_sql_query(query_read, conn_input, chunksize=size_chunk):
    chunk.dropna(how='any', inplace=True)
    chunk.drop_duplicates(inplace=True)
    chunk.replace({'is_fishing': {-1: 0}}, inplace=True)
    chunk['utc_timestamp'] = chunk.apply(
        lambda x: epoch_to_utc_timestamp(x.timestamp), axis = 1)
    chunk['sun_height'] = chunk.apply(
        lambda x: sun_altitude(x.timestamp, x.lon, x.lat, epoch=True), axis = 1)
    print("calculated sun_height")
    chunk['day'] = chunk.apply(lambda x: day_or_night(x.sun_height), axis = 1)
    chunk.to_sql('alex_crowd_sourced_features', conn_output,
                 schema='ais_training_data', if_exists= 'append', index=False)
    j+=1
    print('{} seconds: completed {} rows'.format(
        (dt.datetime.now() - start).seconds, j*size_chunk))

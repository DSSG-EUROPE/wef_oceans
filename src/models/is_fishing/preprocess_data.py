"""
Functions to perform data transformation on training and test data
for modelling. Uses the db_manipulate module to run these functions
in parallel.

Notes:
    EEZ is defined as 200 nautical miles or 370 km
    Day or night is defined by whether sun is above or below horizon

"""

import os
import numpy as np
import pandas as pd

from sklearn.preprocessing import LabelEncoder
from collections import defaultdict

from utils import db_manipulate
from src.features.ais_distance_calculations import distance_to_port, distance_to_shore
from src.features.ais_time_calculations import  epoch_to_utc_timestamp, sun_altitude, day_or_night, epoch_to_localtime

import config

def label_encode_data(df):
    d = defaultdict(LabelEncoder)
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    encode_cols = df.select_dtypes(exclude=numerics).columns
    try:
        df[encode_cols] = df[encode_cols].apply(
                                          lambda x: d[x.name].fit_transform(x))
        return encode_cols, df
    except ValueError:
        print("Columns are numeric, label encoding not required")

def preprocess_training_data(chunk):
    """
    Create features for modelling on training data from Kristina
    Boerder. Includes a distance_to_shore and distance_to_port
    calculation from ais_distance_calculations.

    Where is_fishing label is -1, i.e. conflict in labelling data has been
    removed from training.
    """
    chunk['utc_timestamp'] = chunk.apply(
        lambda x: epoch_to_utc_timestamp(x.timestamp), axis = 1)
    chunk['sun_height'] = chunk.apply(
        lambda x: sun_altitude(x.timestamp, x.lon, x.lat, epoch=True),
                               axis = 1)
    chunk['day_or_night'] = chunk.apply(lambda x: day_or_night(x.sun_height),
                                        axis = 1)
    df = distance_to_shore(chunk.lon, chunk.lat)
    chunk.reset_index(drop=True, inplace=True)
    df.reset_index(drop=True, inplace=True)
    chunk = pd.concat([chunk, df], axis=1)
    chunk['distance_to_port'] = distance_to_port(chunk.lon, chunk.lat)
    chunk['in_eez'] = np.where(chunk['distance_to_shore']<=370, 1, 0)
    chunk.dropna(how='any', inplace=True)
    chunk.drop_duplicates(inplace=True)
    chunk.drop(chunk[chunk['is_fishing'] == -1].index.tolist(), inplace=True)
    return chunk

def preprocess_test_data(chunk):
    """
    Create features for modelling on test data from Spire. Includes a
    distance_to_shore and distance_to_port calculation from
    ais_distance_calculations.

    Where is_fishing label is -1, i.e. conflict in labelling data has been
    removed from training.
    """
    chunk['sun_height'] = chunk.apply(
        lambda x: sun_altitude(x.timestamp, x.longitude, x.latitude), axis = 1)
    chunk['day_or_night'] = chunk.apply(
        lambda x: day_or_night(x.sun_height), axis = 1)
    df = distance_to_shore(chunk.longitude, chunk.latitude)
    chunk.reset_index(drop=True, inplace=True)
    chunk = pd.concat([chunk, df.reset_index(drop=True, inplace=True)], axis=1)
    chunk['distance_to_port'] = distance_to_port(
        chunk.longitude, chunk.latitude)
    chunk['in_eez'] = np.where(chunk['distance_to_shore']<=370, 1, 0)
    chunk = chunk[['mmsi','timestamp','longitude','latitude', 'speed', 'course',
                   'sun_height', 'day_or_night', 'distance_to_shore',
                   'shore_country', 'in_eez', 'distance_to_port']]
    return chunk

def main():
    features = list(itertools.chain.from_iterable(config.features.values()))

    #preprocess training
    table_read = "SELECT " + ", ".join(features) + " " + \
                 "FROM ais_is_fishing_model.training_data;"

    db_manipulate.loop_chunks(table_read,
                               preprocess_training_data,
                               'ais_is_fishing_model',
                               'training_data_features',
                               parallel=True)

    #preprocess test
    table_read = "SELECT " + ", ".join(features) + " " + \
                 "FROM ais_messages.full_year_position;"

    db_manipulate.loop_chunks(table_read,
                              preprocess_test_data,
                              'ais_is_fishing_model',
                              'test_data_features',
                              1000000,
                              parallel=True)

    # add time features in sql and rename columns
    add_time_features = os.path.join(os.path.dirname(__file__),
                                     '../../../sql_scripts/\
                                      is_fishing_model_time_features.sql',
                                      'r')
    db_connect.query(add_time_features)

if __name__ == '__main__':
    main()

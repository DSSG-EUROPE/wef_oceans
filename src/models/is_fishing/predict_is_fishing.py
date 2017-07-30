"""
"""

import os
import numpy as np
import pandas as pd
import datetime as dt

import sklearn
from sklearn.externals import joblib

import utils
from utils import db_connect

import src
import ml_config

engine_input = db_connect.alchemy_connect()
conn_input = engine_input.connect().execution_options(stream_results=True)

engine_output = db_connect.alchemy_connect()
conn_output = engine_output.connect()

model = joblib.load('../../../models/model_1.pkl')

features = ml_config.params['features']

query_read = "SELECT * \
              FROM ais_features.full_year_positional;"

start = dt.datetime.now()
size_chunk = 10000
j = 0

for chunk in pd.read_sql_query(query_read, conn_input, chunksize=size_chunk):
    chunk = chunk.rename(columns = {'distance_to_shore':'distance_from_shore', 'distance_to_port':'distance_from_port'})
    chunk_features = chunk[features]
    predictions = pd.Series(model.predict(chunk_features), name = 'is_fishing')
    chunk = pd.concat([chunk[['mmsi', 'timestamp']], predictions], axis=1)
    chunk.to_sql('ais_predictions', conn_output, schema='ais_modelling',
                 if_exists= 'append', index=False)
    j+=1
    print('{} seconds: completed {} rows'.format(
        (dt.datetime.now() - start).seconds, j*size_chunk))

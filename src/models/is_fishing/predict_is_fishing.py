"""
"""

import os
import numpy as np
import pandas as pd
import datetime as dt
import itertools

import sklearn
from sklearn.externals import joblib

import utils
from utils import db_connect, db_manipulate

import src
import config
import itertools
import preprocess_data

def predict_chunk(chunk):
    model = joblib.load(os.path.join(os.path.dirname(__file__),
                                     '../../../models/model_1.pkl'))
    predictions = pd.Series(model.predict_proba(chunk)[:,1],
                            name = 'is_fishing')
    chunk.reset_index(drop=True, inplace=True)
    predictions.reset_index(drop=True, inplace=True)
    chunk = pd.concat([chunk, predictions], axis=1)
    return chunk

def main():
    features = list(itertools.chain.from_iterable(config.features.values()))

    table_read = "SELECT " + ", ".join(features) + " " + \
                 "FROM ais_is_fishing_model.test_data_features;"

    db_manipulate.loop_chunks(table_read,
                               predict_chunk,
                               'ais_is_fishing_model',
                               'test_data_predictions',
                               1000,
                               parallel=True)

if __name__ == '__main__':
    main()

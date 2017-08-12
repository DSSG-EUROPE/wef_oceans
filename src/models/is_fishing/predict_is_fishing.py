"""
"""

import os
import numpy as np
import pandas as pd
import datetime as dt

import sklearn
from sklearn.externals import joblib

import utils
from utils import db_connect, db_manipulate

import src
import config
import itertools
import preprocess_data



table_read = "SELECT " + ", ".join(features) + " " + \
             "FROM ais_is_fishing_model.test_data_features;"

features = list(itertools.chain.from_iterable(config.features.values()))

def predict_chunk(chunk):
    predictions = pd.DataFrame(model.predict_proba(chunk),
                               columns=['is_fishing', 'is_not_fishing'])
    chunk.reset_index(drop=True, inplace=True)
    predictions.reset_index(drop=True, inplace=True)
    chunk = pd.concat([chunk, predictions], axis=1)
    return chunk


def main():
    model = joblib.load('../../../models/model_1.pkl')
    db_manipulate.loop_chunks(table_read,
                               predict_chunk,
                               'ais_is_fishing_model',
                               'predictions',
                               100000,
                               parallel=True)

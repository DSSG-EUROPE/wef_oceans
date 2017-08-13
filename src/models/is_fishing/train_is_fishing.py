""" models to predict whether a vessel is fishing or not for a given time point.
Labelled data was provided by Kristina Boerder at Dalhousie University.
The data has AIS messages and labels for whether the ship was fishing or not
and the type of fishing gear used.

[Global Fishing Watch](https://github.com/GlobalFishingWatch/training-data)
"""

import os
import numpy as np
import pandas as pd

import utils
from utils import db_connect

import sklearn

import itertools

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score
from sklearn.externals import joblib

import config

def get_training_data():
    features = list(itertools.chain.from_iterable(config.features.values()))
    table_read = "SELECT " + ", ".join(features) + ", is_fishing " + \
                 "FROM ais_is_fishing_model.training_data_features;"
    conn_input, conn_output = db_connect.alchemy_input_output_open()
    df = pd.read_sql_query(table_read, con=conn_input)
    db_connect.alchemy_input_output_close(conn_input, conn_output)
    df = pd.concat([df[features], df['is_fishing']], axis=1)
    return df


df = get_training_data(all_features)

X_train, X_test, y_train, y_test = train_test_split(
    df.drop('is_fishing', axis=1), # X
    df['is_fishing'], # y
    test_size=0.20,
    stratify=df.is_fishing)

model = RandomForestClassifier(n_estimators=450, n_jobs=-1)
model.fit(X_train, y_train)

predictions = pd.Series(model.predict_proba(X_test)[:,1],
                        name = 'is_fishing')

precision_score(y_test, predictions)
#0.99375462240118329 precision model_1

joblib.dump(model, '../../../models/model_1.pkl')

"""
models to predict whether a vessel is fishing or not for a given time point.
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
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score
from sklearn.externals import joblib

import ml_config

features = ml_config.params['features']

engine_input = db_connect.alchemy_connect()
conn_input = engine_input.connect().execution_options(stream_results=True)

engine_output = db_connect.alchemy_connect()
conn_output = engine_output.connect()


df = pd.read_sql_query('SELECT * \
                        FROM ais_training_data.alex_crowd_sourced_features;', con=conn_input)

training_data = pd.concat([df[features], df['is_fishing']], axis=1)

X_train, X_test, y_train, y_test = train_test_split(
    training_data.drop('is_fishing', axis=1), # X
    training_data['is_fishing'], # y
    test_size=0.20,
    stratify=training_data.is_fishing)

model = RandomForestClassifier(n_estimators=450, n_jobs=6)
model.fit(X_train, y_train)

predictions = pd.Series(model.predict(X_test))

precision_score(y_test, predictions)
#0.99375462240118329 precision model_1

joblib.dump(model, '../../../models/model_1.pkl')

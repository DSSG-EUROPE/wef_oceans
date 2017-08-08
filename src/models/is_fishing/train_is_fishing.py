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
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score
from sklearn.metrics import log_loss
from sklearn.externals import joblib

import ml_config

#features = ml_config.params['features']
features = ['distance_from_shore', 'distance_from_port' ,'speed', 'course']


df = db_connect.query('SELECT * FROM ais_training_data.alex_crowd_sourced \
                        where is_fishing != -1 order by timestamp asc;')


tscv = TimeSeriesSplit(n_splits=5)

X, y = df[features], df['is_fishing']


for train_index, test_index in tscv.split(X):
    
    model = RandomForestClassifier(n_estimators=2000, n_jobs=-1)
    
    print(train_index, test_index)
    X_train, X_test = X.ix[train_index], X.ix[test_index]
    y_train, y_test = y.ix[train_index], y.ix[test_index]
    
    model.fit(X_train, y_train)
    predictions = model.predict_proba(X_test)
    predictions_labels = model.predict(X_test)
    print(precision_score(y_test, predictions_labels))
    print(log_loss(y_test, predictions))

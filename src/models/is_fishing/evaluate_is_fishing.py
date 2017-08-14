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
import itertools

import matplotlib
matplotlib.use('agg')

import pylab as pl
import seaborn as sns

import utils
from utils import db_connect

import sklearn
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_recall_curve, precision_score, auc, log_loss
from sklearn.externals import joblib

import config

features = list(itertools.chain.from_iterable(config.features.values()))

model = joblib.load(os.path.join(os.path.dirname(__file__),
                                 '../../../models/model_1.pkl'))
model = joblib.load('../../../models/model_1.pkl')

df = db_connect.query('SELECT * \
                       FROM ais_is_fishing_model.training_data_features \
                       WHERE is_fishing != -1 \
                       ORDER BY timestamp ASC;')

tscv = TimeSeriesSplit(n_splits=3)

X, y = df[features], df['is_fishing']

for train_index, test_index in tscv.split(X):

    print(train_index, test_index)
    X_train, X_test = X.ix[train_index], X.ix[test_index]
    y_train, y_test = y.ix[train_index], y.ix[test_index]

    importances = pd.DataFrame({'feature':X_train.columns,'importance':np.round(model.feature_importances_,3)})
    importances = importances.sort_values('importance',ascending=False).set_index('feature')
    print(importances)

    predictions = model.predict_proba(X_test)
    predictions_labels = model.predict(X_test)
    print('precision_score', precision_score(y_test, predictions_labels))
    print('log_loss', log_loss(y_test, predictions))

    precision, recall, thresholds = precision_recall_curve(y_test, [i[1] for i in predictions])
    area = auc(recall, precision)
    print("Area Under Curve: %0.2f" % area)

    thresholds = np.append(thresholds, 1)

    pl.plot(thresholds, precision, color=sns.color_palette()[0])
    pl.plot(thresholds, recall, color=sns.color_palette()[1])

    leg = pl.legend(('precision', 'recall'), frameon=True)
    leg.get_frame().set_edgecolor('k')
    pl.xlabel('threshold')
    pl.ylabel('%')

    pl.savefig('./plots/precision_recall_threshold')

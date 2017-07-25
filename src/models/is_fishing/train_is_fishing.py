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

from src import features
from src.features import ais_distance_calculations
from src.features import ais_time_calculations
#import importlib
#reload(feature_generation)


from sklearn.model_selection import train_test_split

#from matplotlib import pyplot as plt

from sklearn.metrics import precision_score
from sklearn.metrics import roc_curve, auc

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import make_scorer
from sklearn.grid_search import GridSearchCV
from sklearn.model_selection import ShuffleSplit

from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression

def prepare_training_data(data,
                          drop_na=True,
                          combine_labels=True,
                          convert_time_to_local=False,
                          day_column=False):
    """prepare the training data for modelling by removing null values,
    combining unknown values with negatives,converting timestamps to local
    time, and creating a column for day or night"""
    if drop_na == True:
        prepared_data = data.dropna(how='any', inplace=False)
    if combine_labels == True:
        prepared_data = data.replace({'is_fishing': {-1: 0}}, inplace=False)
    if convert_time_to_local == True:
        prepared_data['timestamp'] = prepared_data['timestamp'].apply(
            lambda x: utc_timestamp_to_localtime(utc_timestamp, lon, lat))
    if day_column == True:
        prepared_data['day'] = prepared_data['timestamp'].apply(
            lambda x: x.hour > 12)
    return(prepared_data)

def accuracy_score(truth, pred):
    """ x accuracy score for input truth and predictions. """
    if len(truth) == len(pred):
        return (truth == pred).mean()*100
    else:
        return "Number of predictions does not match number of outcomes!"


def performance_metric(truth, pred):
    return precision_score(truth, pred)

def fit_model(X, y):
    cv_sets = ShuffleSplit(test_size = 0.20,
                           random_state = 0).get_n_splits(X)
    regressor = RandomForestClassifier()
    params = {'n_estimators': np.arange(50, 500, step=100)}
    scoring_fnc = make_scorer(accuracy_score)
    grid = GridSearchCV(regressor, params, scoring=scoring_fnc, cv=cv_sets)
    grid = grid.fit(X, y)
    return grid.best_estimator_

training_data = db_connect.query("SELECT * \
                                 FROM ais_training_data.alex_crowd_sourced;")


test_data = db_connect.query("SELECT * \
                             FROM ais_messages.full_year_position \
                             LIMIT 1000;")


list_of_features = ['distance_from_shore', 'speed', 'course', 'day']

training_data = prepare_training_data(training_data)

features = training_data[list_of_features]

distance_from_shore = ais_distance_calculations.distance_to_shore(
    test_data['longitude'], test_data['latitude'], country_name=True)

test_data['distance_from_shore'] = distance_from_shore['distance_km']
test_data.dropna(how='any', inplace=True)

X_train, X_test, y_train, y_test = train_test_split(
    features, training_data['is_fishing'],
    test_size=0.20,
    stratify=training_data.is_fishing)

regressor = RandomForestClassifier(n_estimators=100)
regressor.fit(X_train, y_train)


predictions = regressor.predict(test_data[['distance_from_shore',
                                           'speed',
                                           'course']])

test_data['is_fishing'] = predictions
test_data[test_data['is_fishing'] == 1]

print regressor.feature_importances_

importances = pd.DataFrame({'feature':X_train.columns,'feature importance':np.round(regressor.feature_importances_,3)})

importances = importances.sort_values('feature importance',ascending=False).set_index('feature')

print importances
importances.plot.bar()
plt.show()


print accuracy_score(y_test, predictions)


def main():
    plot_classification_report(
        classification_report(y_test,regressor.predict(X_test)))
    plt.savefig('test_plot_classif_report.png',
                dpi=200,
                format='png',
                bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    main()

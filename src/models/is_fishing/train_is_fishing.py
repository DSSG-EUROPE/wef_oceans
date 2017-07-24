"""
Models to predict whether vessels are fishing or not.
Labelled data was provided by Kristina Boerder at Dalhousie
University. The data has AIS messages and labels for weather the ship was
fishing or not and the type of fishing gear used.

[Global Fishing Watch](https://github.com/GlobalFishingWatch/training-data)
"""


import os
import numpy as np
import pandas as pd
import pytz
import utils
from utils import db_connect


import feature_generation
from feature_generation import ais_distance_calculations
#import importlib
#reload(feature_generation)

from datetime import datetime, timedelta

from sklearn.model_selection import train_test_split

from matplotlib import pyplot as plt

from sklearn.metrics import precision_score
from sklearn.metrics import roc_curve, auc

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import make_scorer
from sklearn.grid_search import GridSearchCV
from sklearn.model_selection import ShuffleSplit

from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression

def convert_epoch_to_datetime(timestamp):
    """ convert timestamps to Eastern Australian time-zone """
    utc_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    au_tz = pytz.timezone('Australia/Sydney')
    au_dt = au_tz.normalize(utc_dt.astimezone(au_tz))
    return au_dt


def prepare_training_data(data, drop_na=True, combine_labels=True,
                          convert_timestamp=True, day_column=True):
    """prepare the training data for modelling by removing null values,
    combining unknown values with negatives,converting timestamps to local
    time, and creating a column for day or night"""
    if drop_na == True:
        prepared_data = data.dropna(how='any', inplace=False)
    if combine_labels == True:
        prepared_data = data.replace({'is_fishing': {-1: 0}}, inplace=False)
    if convert_timestamp == True:
        prepared_data['timestamp'] = prepared_data['timestamp'].apply(
            lambda x: convert_epoch_to_datetime(x))
    if day_column == True:
        prepared_data['day'] = prepared_data['timestamp'].apply(
            lambda x: x.hour > 12)
    return(prepared_data)

def accuracy_score(truth, pred):
    """ Returns accuracy score for input truth and predictions. """
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

def show_values(pc, fmt="%.2f", **kw):
    '''
    Heatmap with text in each cell with matplotlib's pyplot
    Source: https://stackoverflow.com/a/25074150/395857
    '''
    from itertools import izip
    pc.update_scalarmappable()
    ax = pc.get_axes()
    for p, color, value in izip(pc.get_paths(), pc.get_facecolors(), pc.get_array()):
        x, y = p.vertices[:-2, :].mean(0)
        if np.all(color[:3] > 0.5):
            color = (0.0, 0.0, 0.0)
        else:
            color = (1.0, 1.0, 1.0)
        ax.text(x, y, fmt % value, ha="center", va="center", color=color, **kw)


def cm2inch(*tupl):
    '''
    Specify figure size in centimeter in matplotlib
    Source: https://stackoverflow.com/a/22787457/395857
    By gns-ank
    '''
    inch = 2.54
    if type(tupl[0]) == tuple:
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)


def heatmap(AUC, title, xlabel, ylabel, xticklabels, yticklabels, figure_width=40, figure_height=20, correct_orientation=False, cmap='RdBu'):
    '''
    Inspired by:
    - https://stackoverflow.com/a/16124677/395857
    - https://stackoverflow.com/a/25074150/395857
    '''

    # Plot it out
    fig, ax = plt.subplots()
    #c = ax.pcolor(AUC, edgecolors='k', linestyle= 'dashed', linewidths=0.2, cmap='RdBu', vmin=0.0, vmax=1.0)
    c = ax.pcolor(AUC, edgecolors='k', linestyle= 'dashed', linewidths=0.2, cmap=cmap)

    # put the major ticks at the middle of each cell
    ax.set_yticks(np.arange(AUC.shape[0]) + 0.5, minor=False)
    ax.set_xticks(np.arange(AUC.shape[1]) + 0.5, minor=False)

    # set tick labels
    #ax.set_xticklabels(np.arange(1,AUC.shape[1]+1), minor=False)
    ax.set_xticklabels(xticklabels, minor=False)
    ax.set_yticklabels(yticklabels, minor=False)

    # set title and x/y labels
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Remove last blank column
    plt.xlim( (0, AUC.shape[1]) )

    # Turn off all the ticks
    ax = plt.gca()
    for t in ax.xaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    for t in ax.yaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False

    # Add color bar
    plt.colorbar(c)

    # Add text in each cell
    show_values(c)

    # Proper orientation (origin at the top left instead of bottom left)
    if correct_orientation:
        ax.invert_yaxis()
        ax.xaxis.tick_top()

    # resize
    fig = plt.gcf()
    #fig.set_size_inches(cm2inch(40, 20))
    #fig.set_size_inches(cm2inch(40*4, 20*4))
    fig.set_size_inches(cm2inch(figure_width, figure_height))



def plot_classification_report(classification_report, title='Classification report ', cmap='RdBu'):
    '''
    Plot scikit-learn classification report.
    Extension based on https://stackoverflow.com/a/31689645/395857
    '''
    lines = classification_report.split('\n')

    classes = []
    plotMat = []
    support = []
    class_names = []
    for line in lines[2 : (len(lines) - 2)]:
        t = line.strip().split()
        if len(t) < 2: continue
        classes.append(t[0])
        v = [float(x) for x in t[1: len(t) - 1]]
        support.append(int(t[-1]))
        class_names.append(t[0])
        print(v)
        plotMat.append(v)

    print('plotMat: {0}'.format(plotMat))
    print('support: {0}'.format(support))

    xlabel = 'Metrics'
    ylabel = 'Classes'
    xticklabels = ['Precision', 'Recall', 'F1-score']
    yticklabels = ['{0} ({1})'.format(class_names[idx], sup) for idx, sup  in enumerate(support)]
    figure_width = 25
    figure_height = len(class_names) + 7
    correct_orientation = False
    heatmap(np.array(plotMat), title, xlabel, ylabel, xticklabels, yticklabels, figure_width, figure_height, correct_orientation, cmap=cmap)




training_data = db_connect.query("SELECT * \
                                 FROM ais_training_data.alex_crowd_sourced;")


test_data = db_connect.query("SELECT * \
                             FROM ais_messages.full_year_position \
                             LIMIT 1000;")


list_of_features = ['distance_from_shore', 'speed', 'course', 'day']

training_data = prepare_training_data(training_data)

features = training_data[list_of_features]

distance_from_shore = ais_distance_calculations.calculate_distance_to_shore(
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

import os
import pandas as pd
import numpy as np

from utils import db_connect

import matplotlib
matplotlib.use('agg')

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np


plt.figure(figsize=(12,6))


def plot_trajectory(mmsi):

    df = db_connect.query('select * from ais_messages.full_year_position where mmsi = {};'.format(mmsi))

    lons, lats = df['longitude'].tolist(), df['latitude'].tolist()

    m = Basemap(projection='robin', resolution = 'l', area_thresh = 1000.0,
              lat_0=0, lon_0=-130)


    m.bluemarble()
    m.drawmapboundary()

    m.fillcontinents()

    x, y = m(lons, lats)


    m.scatter(x, y, marker='.',color='red')


    plt.savefig('{}_trajectory.png'.format(mmsi))
    plt.clf()


plot_trajectory(316007840)

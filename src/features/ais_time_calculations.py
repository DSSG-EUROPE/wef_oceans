"""
functions to convert timestamps to local.
"""

import math
import ephem
import pytz
import datetime
#import tzwhere

import utils
from utils import db_connect

from timezonefinder import TimezoneFinder

from datetime import datetime, timedelta
#from tzwhere import tzwhere

tf = TimezoneFinder()

def epoch_to_utc_timestamp(epoch):
    """ convert timestamps to UTC timestamps """
    utc_timestamp = datetime.utcfromtimestamp(float(epoch)).replace(tzinfo=pytz.utc)
    return utc_timestamp

def epoch_to_australia_timestamp(epoch):
    """ convert timestamps to Eastern Australian time-zone """
    utc_timestamp = datetime.utcfromtimestamp(float(epoch)).replace(tzinfo=pytz.utc)
    au_timezone = pytz.timezone('Australia/Sydney')
    au_timestamp = au_timezone.normalize(utc_timestamp.astimezone(au_timezone))
    return au_timestamp

def lon_lat_to_timezone(lon, lat):
    """ find the timezone at a certain longitude and latitude """
    timezone_str = tf.timezone_at(lng=lon, lat=lat)
    return timezone_str

def utc_timestamp_to_localtime(utc_timestamp, lon, lat):
    """ convert from utc timestamp to a local timestamp provided the timzeon
    string, only available on land"""
    timezone_str = lon_lat_to_timezone(lon,lat)
    timezone = pytz.timezone(timezone_str)
    localtime = timezone.normalize(utc_timestamp.astimezone(timezone))
    return localtime

def epoch_to_localtime(epoch, lon, lat):
    """ convert from utc timestamp to a local timestamp provided the timezone
    string, only available onland"""
    utc_timestamp = epoch_to_utc_timestamp(epoch)
    timezone_str = lon_lat_to_timezone(lon,lat)
    timezone = pytz.timezone(timezone_str)
    localtime = timezone.normalize(utc_timestamp.astimezone(timezone))
    return localtime

def timestamp_day_or_night(utc_timestamp, lon, lat):
    """ convert timestamp to day or night 1 or 0 night if sun altitude < -6 
    [https://stackoverflow.com/questions/43299500/
    pandas-how-to-know-if-its-day-or-night-using-timestamp]
    """
    day = False
    observer = ephem.Observer()
    observer.lon, observer.lat, observer.elevation = str(lon), str(lat), 0
    observer.date = utc_timestamp
    sun = ephem.Sun()
    sun.compute(observer)
    sun_height = sun.alt*180/math.pi
    if sun_height > -12:
        day = True
    return utc_timestamp, day

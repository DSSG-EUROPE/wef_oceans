"""
functions to convert timestamps to local.
"""

import math
import ephem
import pytz
import datetime
import tzwhere

from datetime import datetime, timedelta
from tzwhere import tzwhere

def epoch_to_utc_timestamp(epoch):
    """ convert timestamps to UTC timestamps """
    utc_timestamp = datetime.utcfromtimestamp(epoch).replace(tzinfo=pytz.utc)
    return utc_timestamp

def epoch_to_australia_timestamp(epoch):
    """ convert timestamps to Eastern Australian time-zone """
    utc_timestamp = datetime.utcfromtimestamp(epoch).replace(tzinfo=pytz.utc)
    au_timezone = pytz.timezone('Australia/Sydney')
    au_timestamp = au_timezone.normalize(utc_timestamp.astimezone(au_timezone))
    return au_timestamp

def lon_lat_to_timezone(lon, lat):
    """ find the timezone at a certain longitude and latitude """
    tzwhere = tzwhere.tzwhere()
    timezone_str = tzwhere.tzNameAt(lon, lat)
    return timezone_str

def utc_timestamp_to_localtime(utc_timestamp, lon, lat):
    """ convert from utc timestamp to a local timestamp provided the timzeon
    string"""
    timezone_str = lon_lat_to_timezone(lon,lat)
    timezone = pytz.timezone(timezone_str)
    localtime = timezone.normalize(utc_timestamp.astimezone(timezone))
    return localtime

def timestamp_day_or_night(utc_timestamp, lon, lat):
    """ convert timestamp to day or night 1 or 0 night is sun altitude < 0
    [https://stackoverflow.com/questions/43299500/
    pandas-how-to-know-if-its-day-or-night-using-timestamp]
    """
    sun = ephem.Sun()
    observer = ephem.Observer()
    observer.lon, observer.lat, observer.elevation = lon, lat, 0
    observer.date = utc_timestamp
    sun.compute(observer)
    sun_alt = sun.alt
    if sun_alt > 0:
        day = 1
    else:
        day = 0
    return day

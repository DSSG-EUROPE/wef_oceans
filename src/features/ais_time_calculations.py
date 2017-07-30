"""
functions for time conversions, to find local timezones. Convert epochs
to timestamps and calculate day or night binary.
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
    """ convert epoch to utc_timestamp """
    epoch = float(epoch)
    utc_timestamp = datetime.utcfromtimestamp(epoch).replace(tzinfo=None)
    return utc_timestamp

def epoch_to_australia_timestamp(epoch):
    """ convert timestamps to Eastern Australian time-zone """
    epoch = float(epoch)
    utc_timestamp = datetime.utcfromtimestamp(epoch).replace(tzinfo=pytz.utc)
    au_timezone = pytz.timezone('Australia/Sydney')
    au_timestamp = au_timezone.normalize(utc_timestamp.astimezone(au_timezone))
    return au_timestamp

def lon_lat_to_timezone(lon, lat):
    """ find the timezone at a certain longitude and latitude """
    timezone_str = tf.timezone_at(lng=lon, lat=lat)
    return timezone_str

def utc_timestamp_to_localtime(utc_timestamp, lon, lat):
    """ convert from utc timestamp to a local timestamp provided the timezone
    string, only available on land"""
    timezone_str = lon_lat_to_timezone(lon,lat)
    timezone = pytz.timezone(timezone_str)
    localtime = timezone.normalize(utc_timestamp.astimezone(timezone))
    return localtime

def epoch_to_localtime(epoch, lon, lat):
    """ convert from utc timestamp to a local timestamp provided the timezone
    string, only available on land"""
    utc_timestamp = epoch_to_utc_timestamp(epoch)
    timezone_str = lon_lat_to_timezone(lon,lat)
    timezone = pytz.timezone(timezone_str)
    localtime = timezone.normalize(utc_timestamp.astimezone(timezone))
    return localtime

def sun_altitude(utc_time, lon, lat, epoch=False):
    """ calculate angle of the sun at a lon lat for a certain time
    [https://stackoverflow.com/questions/43299500/
    pandas-how-to-know-if-its-day-or-night-using-timestamp]
    assumes an elevation of 0 m or sea-level
    """
    if epoch == True:
        time = epoch_to_utc_timestamp(utc_time)
        time = time.strftime('%Y-%m-%d %H:%M:%S')
    else:
        time = utc_time
    observer = ephem.Observer()
    observer.lon, observer.lat, observer.elevation = str(lon), str(lat), 0
    observer.date = time
    sun = ephem.Sun()
    sun.compute(observer)
    sun_height = sun.alt*180/math.pi # calculate in degrees
    return sun_height

def day_or_night(sun_altitude):
    """ determines whether day or night for a certain sun altitude,
    uses the civil definition of dusk/dawn when the sun is < - 6 degrees
    below the horizon """
    day = 0
    if sun_altitude > -6:
        day = 1
    return day

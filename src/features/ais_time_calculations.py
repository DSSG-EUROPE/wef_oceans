"""
functions to convert timestamps to local.
"""

import datetime
from datetime import datetime, timedelta
import pytz
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

def utc_timestamp_to_localtime(utc_timestamp, timezone_str):
    """ convert from utc timestamp to a local timestamp provided the timzeon
    string"""
    local_timestamp = datetime.utcfromtimestamp(epoch).replace(tzinfo=pytz.utc)
    utc_timestamp = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    au_tz = pytz.timezone('Australia/Sydney')
    au_dt = au_tz.normalize(utc_dt.astimezone(au_tz))
    return localtime


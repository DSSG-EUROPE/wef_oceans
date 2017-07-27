"""
This module provides functions for accessing the postgres database of AIS
messages provided by SPIRE. Connection to the database requires a database.ini
file.
Documentation of AIS message fields is available here
https://spire.com/contact/developer-portal/
"""

import os
import sys
import psycopg2
import pandas as pd
from sqlalchemy import *
from geoalchemy2 import *
from sqlalchemy import func
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import *

from configparser import ConfigParser

database_config = os.path.join(os.path.dirname(__file__), '../auth/database.ini')

def alchemy_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**database.DATABASE))
 

def config(filename=database_config, section='postgresql'):
    """ Define parameters for PostgreSQL database connection """
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} not found in the {1} file'.format(section, filename))
    return db


def query(sql_query):
    """ Connect to the PostgreSQL database server and run query """
    conn = None
    try:
        params = config()
        #print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(sql_query)
        colnames = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        data = pd.DataFrame(rows, columns=colnames)
        return data
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            #print('Database connection closed.')


if __name__ == '__main__':
    data = query(sys.argv[1])
    print(data)

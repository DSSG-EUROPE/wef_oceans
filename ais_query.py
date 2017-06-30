"""
This module provides functions for accessing the postgres database of AIS
messages provided by SPIRE. Connection to the database requires a database.ini
file.
Documentation of AIS message fields is available here
https://spire.com/contact/developer-portal/
"""

import psycopg2
import pandas as pd
from configparser import ConfigParser

columns_static = ['msg_type',
		  'mmsi', 
		  'timestamp', 
		  'nmea',
		  'imo',
		  'name',
		  'ship_and_cargo_type',
		  'length',
		  'width',
		  'draught',
		  'eta_date',
		  'destination',
		  'call_sign']

columns_position = ['msg_type',
                    'mmsi',
                    'timestamp',
                    'nmea',
                    'status',
                    'rot',
                    'speed',
                    'accuracy',
                    'longitude',
                    'latitude',
                    'course',
                    'heading',
                    'manever',
                    'geom']


sql_query = """SELECT *
               FROM ais_messages.ais_static
               WHERE timestamp_ais
               BETWEEN '2017-01-02 03:45:29' and '2017-06-07 01:12:49'
               LIMIT 5
               """

def config(filename='database.ini', section='postgresql'):
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


def connect(sql_query):
    """ Connect to the PostgreSQL database server and run query """
    conn = None
    try:
        params = config()
        #print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(sql_query)
        rows = cur.fetchall()
        spire_ais = pd.DataFrame(rows)
        return spire_ais
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            #print('Database connection closed.')


if __name__ == '__main__':
    spire_ais = connect(sql_query) 
    print(spire_ais)

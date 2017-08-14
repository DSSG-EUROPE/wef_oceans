"""
Functions for accessing the PostgreSQL database for this project. In this way
AIS data, modelling features, and predictions can be accessed, along with
satellite image meta-data.

Database connections use either psycopg2 or sqlalchemy packages, and require
the following initialisation files:

/auth/database_alchemy.ini
/auth/database_psycopg2.ini

Documentation of AIS message fields is available here
https://spire.com/contact/developer-portal/
"""
from configparser import ConfigParser, SafeConfigParser
from geoalchemy2 import *
import os
import pandas as pd
import psycopg2
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import *
import sys

config_pscopg2 = os.path.join(os.path.dirname(__file__),
                              '../auth/database_psycopg2.ini')

config_alchemy = os.path.join(os.path.dirname(__file__),
                              '../auth/database_alchemy.ini')

parser = SafeConfigParser()
parser.read(config_alchemy)
url = parser.get('postgresql', 'url')

def config(filename=config_pscopg2, section='postgresql'):
    """ define parameters for PostgreSQL database connection """

    parser = ConfigParser()
    parser.read(filename)
    database = {}

    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            database[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} not found in the {1} file'.format(section, filename))

    return database

def query(sql_query):
    """ connect to PostgreSQL database server with psycopg2 and run query """

    conn = None

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(sql_query)
        colnames = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        data = pd.DataFrame(rows, columns=colnames)
        cur.close()
        return data
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def alchemy_connect():
    """
    connect to database with sqlalchemy url.
    """
    return create_engine(url)

def alchemy_input_output_open():
    """
    create input and output engines, to stream to and from the PostgreSQL
    database in parallel. Stream results for faster downstream connection.
    """
    engine_input = alchemy_connect()
    conn_input = engine_input.connect().execution_options(stream_results=True)

    engine_output = alchemy_connect()
    conn_output = engine_output.connect()
    return conn_input, conn_output

def alchemy_input_output_close(conn_input, conn_output):
    """
    close input and output connections from sqlalchemy.
    """
    conn_input.close()
    conn_output.close()

if __name__ == '__main__':

    # run queries from command line taking query as argument
    data = query(sys.argv[1])
    print(data)

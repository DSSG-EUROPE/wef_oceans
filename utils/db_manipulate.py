"""
Functions to manipulate data from PostgreSQL database includes a
parallelise dataframe that runs a function on a pandas data frame
in parallel, as well as a loop_chunks function. This reads a chunk
from the database performs an operation and uploads to a new
table in the database.
"""


import numpy as np
import pandas as pd
import time

from multiprocessing import Pool, cpu_count

from utils import db_connect

def parallelise_dataframe(df, func, num_cores=None):
    '''
    Perform function in parallel on pandas data frame where if the
    num_cores is not specified then use the number of available
    cores -1.

    Arguments:
    df (dataframe to manipulate)
    func (function to apply)
    num_cores (number of cores to parallelise)

    Returns:
    The data frame processed by function in parallel.
    '''
    if num_cores==None:
        num_cores = cpu_count() - 1
    df_split = np.array_split(df, num_cores)
    pool = Pool(num_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df

def loop_chunks(table_read, chunk_function, output_schema, output_table,
                size_chunk=1000000, parallel=True):
    '''
    Perform function on PostgreSQL database chunk. Read from the db
    perform operation either threaded or on a single core, then
    upload to the database.

    Arguments:
    table_read (a PSQL query that alchemy uses to read the table)
    chunk_function (the function to apply to that chunk)
    output_schema (schema for table output)
    output_table (table name to output data into, will create if not exists)
    size_chunk (the number of rows to process in 1 chunk)
    parallel (use the parallelise_dataframe function on chunk)
    '''

    conn_input, conn_output = db_connect.alchemy_input_output_open()
    start = round(time.time())
    j = 0
    for chunk in pd.read_sql_query(table_read, conn_input, chunksize=size_chunk):
        if parallel==True:
            chunk = parallelise_dataframe(chunk, chunk_function)
        else:
            chunk = chunk_function(chunk)
        chunk.to_sql(output_table, conn_output, schema=output_schema,
                     if_exists='append', index=False)
        j+=1
        print('{} seconds: completed {} rows'.format(
            (round(time.time()) - start), j*size_chunk))
    db_connect.alchemy_input_output_close(conn_input, conn_output)

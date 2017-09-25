#!/bin/python

"""Collection of functions for creating or appending SQLite (sql) or postgreSQL (pg)
databases with data from python lists or .csv tables.  All functions assume that data
is structured with a two-line header, the first containing column names and the second
data types, all in SQLite/postgreSQL-compatible format.  For particularly large files,
there is an optional argument to specify the number of lines to read and upload in a
single block, in order to limit the amount of data stored in memory and improve run
times.
"""

import sqlite3
import csv
from string import maketrans
import time
import os


def human_size(bytes):
    """http://stackoverflow.com/questions/14996453/python-libraries-to-calculate-human-readable-filesize-from-bytes
    """
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    sign = ''
    if bytes == 0:
        return '0 B'
    elif bytes < 0:
        sign = '-'
        bytes = abs(bytes)
    i = 0
    while bytes >= 1024 and i < len(suffixes)-1:
        bytes /= 1024.
        i += 1
    f = ('%.2f' % bytes).rstrip('0').rstrip('.')
    return '%s%s %s' % (sign, f, suffixes[i])


def human_time(seconds):
    """Modified from human_time() above
    """
    suffixes = ['s', 'min', 'h']
    sign = ''
    if seconds == 0:
        return '0 s'
    elif seconds < 0:
        sign = '-'
        seconds = abs(seconds)
    i = 0
    while seconds >= 60 and i < len(suffixes)-1:
        seconds /= 60.
        i += 1
    f = ('%.2f' % seconds).rstrip('0').rstrip('.')
    return '%s%s %s' % (sign, f, suffixes[i])


def sql_query_stats(cursor_object, query, db_fpath=''):
    """Structure to execute a query and return fetchall results, automatically printing out the execution time and
    change in file size.
    """

    print "   Executing query:"
    print "   ", query
    start_time = time.time()
    if db_fpath:
        initial_size = os.path.getsize(db_fpath)

    cursor_object.execute(query)
    results = cursor_object.fetchall()
    print "    Query executed in %s" % human_time(time.time()-start_time)

    if db_fpath:
        growth = os.path.getsize(db_fpath) - initial_size
        print "    Database file %s increased in size from %s by %s (%.1f %%)" % \
              (db_fpath, human_size(initial_size), human_size(growth), (float(growth)/initial_size)*100)

    print
    return results


def list_to_sql(data, db_fpath, db_table):
    """Copy contents of a python list into a table in an existing or new SQLite database
    file.  Assumes list has a standard two-row header:  column names, SQLite data types.
    Function will fail if file/table already exist.  
    Basic structure from http://zetcode.com/db/sqlitepythontutorial/
    Args-
        data (list): list of data to upload
        db_fpath (str): full path from root of database file
        db_table (str): name for new table
    """
    # clone input list into this function's stack frame so original is not changed
    my_list = data[:]

    # remove any illegal characters from column name
    trantab = maketrans(",.()-/$", "_______")
    for i in range(len(my_list[0])):
        my_list[0][i] = my_list[0][i].translate(trantab)

    # define SQLite command string to create new table with required columns names & data types
    entries = ""
    count = 0
    for e in range(len(my_list[0])):
        entries += "%s %s, " % (my_list[0][e], my_list[1][e])
        count +=1
    create_table = "CREATE TABLE %s (%s)" % (db_table, entries[:-2])
    
    # define SQLite command string for tabular data insertion
    values = count*"?, "
    insert_values = "INSERT INTO %s VALUES(%s)" % (db_table, values[:-2])
     
    # delete two header rows of list
    for i in range(2):
        del my_list[0]

    # establish database connection and execute the command strings
    con = sqlite3.connect(db_fpath)
    with con:
        cur = con.cursor()
        cur.execute(create_table)
        cur.executemany(insert_values, my_list)


def append_sql(data, db_fpath, db_table):
    """Append additional data to an existing SQLite database file/table.  Note that
    this function is intended for use with csv_to_sql() and has not yet been rigorously
    tested for stand-alone operation.  
    Basic structure from http://zetcode.com/db/sqlitepythontutorial/
    Args-
        data (list): list of data to upload
        db_fpath (str): full path from root of database file to append
        db_table (str): name of table to append
    """
    # clone input list into this function's stack frame so original is not changed
    my_list = data[:]
    
    # define SQLite command string for tabular data insertion
    values = len(my_list[0])*"?, "
    insert_values = "INSERT INTO %s VALUES(%s)" % (db_table, values[:-2])

    # establish database connection and execute the command string
    con = sqlite3.connect(db_fpath)
    with con:
        cur = con.cursor()
        cur.executemany(insert_values, my_list)


def csv_to_sql(csv_fpath, db_fpath, db_table, delim="c", line_block=0):
    """Copy contents of a .csv file into a table in an existing or new SQLite database
    file.  Assumes list has a standard two-row header:  column names, SQLite data types.
    Function will fail if file/table already exists.
    Args-
        csv_fpath (str): full path from root of csv file to upload
        db_fpath (str): full path from root of database file to create
        delim (str, optional): 'c'=comma (default) or 't'=tab
        line_block (int, optional): number of lines to read as a block (default is
            entire file)
    """
    # print operation description and start timer
    print "Copying %s to SQLite database %s..." % (csv_fpath, db_fpath)
    start = time.time()

    # copy .csv contents into a python list
    if delim == "t":
        lines = csv.reader(open(csv_fpath, 'rU'), delimiter="\t")
    else:
        lines = csv.reader(open(csv_fpath, 'rU'))
        
    # upload data in either a single or multiple blocks
    my_list = [[]]
    line_total = 0
    if line_block == 0:
        for line in lines:
            my_list.append(line)
            line_total += 1
        del my_list[0]
        list_to_sql(my_list, db_fpath, db_table)
    else:
        # create new database table from headers and first row of data
        for i in range(3):
            line = lines.next()
            my_list.append(line)
            line_total += 1
        del my_list[0]
        list_to_sql(my_list, db_fpath, db_table)

        # fill a list of data with the appropriate block size, and append to previously-created database
        data = [[]]
        bail = 0
        line_count = 1
        while True:
            while line_count <= line_block:
                try:
                    line = lines.next()
                    data.append(line)
                    line_count += 1
                    line_total += 1
                except:
                    bail = 1
                    break
            del data[0]
            if data:
                append_sql(data, db_fpath, db_table)
            data = [[]]
            line_count = 0
            if bail == 1:
                break

    # stop timer and report time elapsed
    print "    Total of %i data rows (%i columns each) uploaded in %s s" % \
          (line_total-2, len(my_list[0]), round(time.time()-start, 6))
    print


def query_to_csv(cursor_object, table, query, out_fpath, types=True):
    """Saves a standard-format csv table (including a two-line header of column names
    and data types) for the specified 'SELECT *'-type query statement.
        Note: to return a more restricted list of data columns, first save them as a
        new table or view and then execute this function.
    Args-
        cursor_object (object): previously-defined SQLite cursor object name
        table (str): table to be queries
        query (str): SQLite-formatted 'SELECT *'-type query
        out_fpath (str): full file path for output
    """
    cursor_object.execute(query)
    rows = cursor_object.fetchall()
    cursor_object.execute("PRAGMA table_info(%s)" % table)
    columns = cursor_object.fetchall()
    labels = []
    types = []
    for i in range(len(columns)):
        labels.append(columns[i][1])
        types.append(columns[i][2])
    rows.insert(0, labels)
    if types:
        rows.insert(1, types)
    c = csv.writer(open(out_fpath, "wb"))
    for row in rows:
        c.writerow(row)


def pg_to_sql(csv_fpath, delim="c"):
    """Function to convert postgreSQL-format data types in .csv headers to SQLite format.
    Args-
        csv_fpath (str): file path of .csv file to be converted
    """
    temp_csv_fpath = csv_fpath+".temp"
    if delim == "t":
        in_file = csv.reader(open(csv_fpath, 'rU'), delimiter="\t")
    else:
        in_file = csv.reader(open(csv_fpath, 'rU'))
    out_file = csv.writer(open(temp_csv_fpath, "w"))
    replacements = {"varchar":"TEXT", "float8":"REAL", "float4":"REAL", "int4":"INT", "int2":"INT"}

    for line in in_file:
        for i in range(len(line)):
            for src, target in replacements.iteritems():
                line[i] = line[i].replace(src, target)
        out_file.writerow(line)
    os.remove(csv_fpath)
    os.rename(temp_csv_fpath, csv_fpath)

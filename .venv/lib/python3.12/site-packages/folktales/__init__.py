"""
################################################################################
#                                                                              #
# folktales                                                                    #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program enables the creation, access and modification of SQL databases, #
# with an emphasis on storing dictionaries easily and accessing database       #
# tables as pandas DataFrames easily. It also provides template dictionaries   #
# suitable for logging.                                                        #
#                                                                              #
# copyright (C) 2018 William Breaden Madden                                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################
"""

import datetime
import logging
import os
import uuid

import dataset
import pandas as pd
import technicolor

name        = "folktales"
__version__ = "2018-05-03T0245Z"

log = logging.getLogger(name)
log.addHandler(technicolor.ColorisingStreamHandler())
log.setLevel(logging.DEBUG)

def create_database(
    filepath        = "database.db",
    command         = "sqlite3 {filepath} \"create table aTable(field1 int); drop table aTable;\"",
    path_expansions = True
    ):
    """
    Create a database at a specified filepath.
    """
    try:
        filepath = os.path.expanduser(os.path.expandvars(filepath)) if path_expansions else filepath
        log.debug("create database {filepath}".format(filepath = filepath))
        os.system(command.format(filepath = filepath))
        return filepath
    except:
        log.error("error creating database {filepath}".format(filepath = filepath))
        return False

def access_database(
    filepath        = "database.db",
    URL             = "sqlite:///",
    path_expansions = True,
    create          = True
    ):
    """
    Return a database object opened using a specified URL and filepath. If the
    database does not exist, it may be created first.
    """
    try:
        filepath = os.path.expanduser(os.path.expandvars(filepath)) if path_expansions else filepath
        if not os.path.isfile(filepath):
            log.debug("{filepath} not found".format(filepath = filepath))
            if create:
                create_database(filepath = filepath)
            else:
                return False
        log.debug("access {filepath}".format(filepath = filepath))
        return dataset.connect(URL + str(filepath))
    except:
        log.error("error accessing {filepath}".format(filepath = filepath))
        return False

def insert_dictionary_into_database_table(
    dictionary      = None,
    table           = None,
    table_name      = "data",
    database        = None,
    filepath        = "database.db",
    URL             = "sqlite:///",
    path_expansions = True,
    create          = True
    ):
    """
    Insert a specified dictionary into a table of a database. If a table object
    is not specified, then it can be accessed from a database. If a database
    object is not specified, then it can be accessed from a filepath. Return the
    inserted row primary key.
    """
    if not table:
        if not database:
            database = access_database(
                filepath        = filepath,
                URL             = URL,
                path_expansions = path_expansions,
                create          = create
            )
        try:
            table = database[table_name]
        except:
            log.error("error accessing table \"{table_name}\"".format(table_name = table_name))
            return False
    else:
        table_name = table.name
    try:
        log.debug("convert dictionary values to strings")
        dictionary = dict((k, str(v)) for k, v in list(dictionary.items()))
        log.debug("insert dictionary into table \"{table_name}\"".format(table_name = table_name))
        return table.insert(dictionary)
    except:
        log.error("error inserting dictionary into table \"{table_name}\"".format(table_name = table_name))
        return False

def template_state_dictionary():
    """
    Return a template state dictionary featuring a UUID4 identifier and a UTC
    datetime object.
    """
    return {
        "datetime": datetime.datetime.utcnow(),
        "UUID4"   : uuid.uuid4()
    }

def state_dictionary(
    entries = None
    ):
    """
    Return a state dictionary featuring a UUID4 identifier and a UTC datetime
    object, and updated with any other entries specified.
    """
    dictionary = template_state_dictionary()
    if entries:
        dictionary.update(entries)
    return dictionary

def insert_state_dictionary_into_database_table(
    entries         = None,
    table           = None,
    table_name      = "data",
    database        = None,
    filepath        = "database.db",
    URL             = "sqlite:///",
    path_expansions = True,
    create          = True
    ):
    """
    Insert a state dictionary into a table of a database.
    """
    return insert_dictionary_into_database_table(
        dictionary      = state_dictionary(entries = entries),
        table           = table,
        table_name      = table_name,
        database        = database,
        filepath        = filepath,
        URL             = URL,
        path_expansions = path_expansions,
        create          = create
    )

def DataFrame_of_database_table(
    table           = None,
    table_name      = "data",
    database        = None,
    filepath        = "database.db",
    URL             = "sqlite:///",
    path_expansions = True
    ):
    """
    Return a pandas DataFrame of a database table. If a table object is not
    specified, then it can be accessed from a database. If a database object is
    not specified, then it can be accessed from a filepath.
    """
    if not table:
        if not database:
            database = access_database(
                filepath        = filepath,
                URL             = URL,
                path_expansions = path_expansions
            )
        try:
            table = database[table_name]
        except:
            log.error("error accessing table \"{table_name}\"".format(table_name = table_name))
            return False  
    else:
        table_name = table.name
    try:
        df = pd.DataFrame(columns = table.columns)
        for entry in table:
            df = df.append(entry, ignore_index = True)
        return df
    except:
        log.error("error converting table \"{table_name}\" to pandas DataFrame".format(table_name = table_name))
        return False

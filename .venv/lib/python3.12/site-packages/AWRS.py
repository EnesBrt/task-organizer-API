# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# AWRS                                                                         #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program provides weather utilities.                                     #
#                                                                              #
# copyright (C) 2017 Will Breaden Madden, wbm@protonmail.ch                    #
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
import json
try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen

name    = 'AWRS'
version = '2019-08-14T1152Z'

def METAR(
    identifier = 'EGPF',
    URL        = 'https://avwx.rest/api/metar/'
    ):
    try:
        file_URL          = urlopen(URL + identifier)
        data_string       = file_URL.read().decode('utf-8')
        data_JSON         = json.loads(data_string)
        report            = {}
        report['raw']     = data_JSON
        report['METAR']   = data_JSON['raw']
    except:
        return None
    report['identifier']  = identifier
    report['dewpoint']    = int(data_JSON['dewpoint']['value'])
    report['QNH']         = data_JSON['altimeter']['value']
    report['temperature'] = int(data_JSON['temperature']['value'])
    report['visibility']  = int(data_JSON['visibility']['value'])
    try:
        report['wind_direction'] = int(data_JSON['wind_direction']['value'])
    except:
        report['wind_direction'] = None
    report['wind_speed']  = int(data_JSON['wind_speed']['value'])
    # datetime
    now                   = datetime.datetime.utcnow()
    tmp                   = datetime.datetime.strptime(
                                   data_JSON['time']['repr'],
                                   '%d%H%MZ'
                            )
    report['datetime']    = datetime.datetime(
                                now.year,
                                now.month,
                                tmp.day,
                                tmp.hour,
                                tmp.minute
                            )
    report['time_UTC']    = report['datetime'].strftime('%Y-%m-%dT%H%MZ')
    # rain
    if 'RA' in report['METAR']:
        report['rain'] = True
    else:
        report['rain'] = False
    return report

def TAF(
    identifier = 'EGPF',
    URL        = 'https://avwx.rest/api/taf/'
    ):
    try:
        file_URL          = urlopen(URL + identifier)
        data_string       = file_URL.read().decode('utf-8')
        data_JSON         = json.loads(data_string)
        report            = {}
        report['raw']     = data_JSON
        report['TAF']     = data_JSON['raw']
    except:
        return None
    report['identifier']         = identifier
    # list of tuples of start and stop TAF datetimes for rain predictions
    report['rain_TAF_datetimes'] = [
        (forecast['start_time']['repr'], forecast['end_time']['repr'])\
        for forecast in data_JSON['forecast'] if 'RA' in forecast['raw']
    ]
    # list of tuples of start and stop datetimes for rain predictions
    report['rain_datetimes'] = []
    now = datetime.datetime.utcnow()
    for datetimes in report['rain_TAF_datetimes']:
        start_datetime = TAF_datetime_to_datetime_object(
            datetime_string             = datetimes[0],
            datetime_for_year_and_month = now
        )
        stop_datetime = TAF_datetime_to_datetime_object(
            datetime_string             = datetimes[1],
            datetime_for_year_and_month = now
        )
        report['rain_datetimes'].append((start_datetime, stop_datetime))
    # list of human-readable time windows in style %Y-%m-%dT%H%MZ
    report['rain_human_readable_datetimes'] = []
    for datetimes in report['rain_datetimes']:
        report['rain_human_readable_datetimes'].append(
            datetimes[0].strftime('%Y-%m-%dT%H%MZ') +\
            '--'                                    +\
            datetimes[1].strftime('%Y-%m-%dT%H%MZ')
        )
    return report

def TAF_datetime_to_datetime_object(
    datetime_string             = None,
    datetime_for_year_and_month = None  # e.g. datetime.datetime.utcnow()
    ):
    """
    Preprocess datetimes to change hours from 24 to 00, incrementing the date
    as necessary.
    """
    if datetime_string.endswith('24'):
        datetime_string = datetime_string[:-2] + '00'
        tmp = datetime.datetime.strptime(datetime_string, '%d%H') +\
              datetime.timedelta(days = 1)
    else:
        tmp = datetime.datetime.strptime(datetime_string, '%d%H')
    return datetime.datetime(
        datetime_for_year_and_month.year,
        datetime_for_year_and_month.month,
        tmp.day,
        tmp.hour,
        tmp.minute
    )

def rain_datetimes(
    identifier = 'EGPF'
    ):
    report = TAF(identifier = identifier)
    return report['rain_datetimes']

def rain_human_readable_datetimes(
    identifier    = 'EGPF',
    return_list   = True,
    return_string = False
    ):
    report = TAF(identifier = identifier)
    if return_list:
        return report['rain_human_readable_datetimes']
    if return_string:
        return ', '.join(report['rain_human_readable_datetimes'])

def rain_soon(
    identifier = 'EGPF',
    minutes    = 30
    ):
    test_time = datetime.datetime.utcnow() +\
                datetime.timedelta(minutes = minutes)
    report    = TAF(identifier = identifier)
    if report['rain_datetimes']:
        for datetimes in report['rain_datetimes']:
            if datetimes[0] <= test_time <= datetimes[1]:
                return True
    return False

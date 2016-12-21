#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.parsers.common
@file cgsn_parsers/parsers/common.py
@author Christopher Wingard
@brief Provides common base classes, definitions and other utlities for all parsers.
'''
import argparse
import datetime
import re

from bunch import Bunch
from calendar import timegm
from pytz import timezone

# Regex strings for use with the majority of parsers
DCL_TIMESTAMP = r'(\d{4}/\d{2}/\d{2}\s\d{2}:\d{2}:\d{2}.\d{3})'
FLOAT = r'([+-]?\d+.\d+[Ee]?[+-]?\d*)'  # includes scientific notation
FLTNAN = r'([+-]?\d+.\d+[Ee]?[+-]?\d*|NaN)'
INTEGER = r'([+-]?[0-9]+)'
NEWLINE = r'(?:\r\n|\n)?'


class ParameterNames(object):
    '''
    Base class used to initialize the Bunch class dictionary object for holding
    parsed parameters. The class must be initialized with the parameter names
    when called by the individual parsers.
    '''
    # Initialize Parameter names with time as the only default parameter
    def __init__(self, parameters=[]):
        self.parameters = ['time'] + parameters

    # Create the initial dictionary object.
    def create_dict(self):
        '''
        Create a Bunch class object to store the parameter names for the data
        files.
        '''
        bunch = Bunch()

        for name in self.parameters:
            bunch[name] = []

        return bunch


class ParserCommon(object):
    '''
    A Parser class that begins the process of extracting data records from the
    DCL log files.

    An initialize method is used to initialize the Parser object, with two
    methods provided to read the data files in as buffered objects (using
    either readlines, if the file is ascii, or read if the file is a
    pure binary file).
    '''
    def initialize(self, infile, parameters):
        '''
        Initialize the Parser object with the input file and path and the data
        parameters
        '''
        # set the infile name and path
        self.infile = infile

        # initialize the data dictionary using the names defined above
        data = ParameterNames(parameters)
        self.data = data.create_dict()
        self.raw = None

    def load_ascii(self):
        '''
        Create a buffered data object by opening the data file and reading in
        the contents
        '''
        with open(self.infile, 'rb') as fid:
            self.raw = fid.readlines()

    def load_binary(self):
        '''
        Create a buffered data object by opening the data file and reading in
        the contents
        '''
        with open(self.infile, 'rb') as fid:
            self.raw = fid.read()


def dcl_to_epoch(time_string):
    '''
    Use the DCL formatted date and time string to calculate an epoch timestamp
    (seconds since 1970-01-01)
    '''
    # find and replace the incorrectly formatted cases where the seconds are
    # incorrectly set to 60.000 (seconds must be between 00 and 59).
    if re.match(r'(\d{4}/\d{2}/\d{2}\s\d{2}:\d{2}:60.\d{3})', time_string):
        time_string = re.sub('60.\d{3}', '00.000', time_string)
        tplus = 60.0
    else:
        tplus = 0.0

    # convert the date and time string into a datetime object
    dcl = datetime.datetime.strptime(time_string, '%Y/%m/%d %H:%M:%S.%f')
    utc = dcl.replace(tzinfo=timezone('UTC'))

    # calculate the epoch time as seconds since 1970-01-01 in UTC
    epts = timegm(utc.timetuple()) + (utc.microsecond / 1e6) + tplus
    return epts


def inputs():
    '''
    Sets the main input arguments for the parser that would be passed by the
    harvester. By default, these are just the input file (raw data file), the
    the output file, and an optional integer switch that can be used to set
    custom options for parsers if needed. File names should include pathnames,
    which can be relative to the harvester.
    '''
    # initialize arguement parser
    parser = argparse.ArgumentParser(description='''Parse data files from DCL
                                     formatted daily or hourly log files''',
                                     epilog='''Parses the data file''')

    # assign arguements for the infile and outfile and a generi switch that can
    # be used, if needed, to set different options (e.g. if switch == 1, do
    # this or that).
    parser.add_argument("-i", "--infile", dest="infile", type=str, required=True)
    parser.add_argument("-o", "--outfile", dest="outfile", type=str, required=True)
    parser.add_argument("-s", "--switch", dest="switch", type=int, default=0)

    # parse the input arguements and create a parser object
    args = parser.parse_args()

    return args

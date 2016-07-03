#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.parsers.parse_ctdbp
@file cgsn_parsers/parsers/parse_ctdbp.py
@author Christopher Wingard 
@brief Parses the 3 variants of CTDBP data.
'''
__author__ = 'Christopher Wingard'
__license__ = 'Apache 2.0'

import os
import re
import scipy.io as sio

# Import common utilites and base classes
from common import ParserCommon
from common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, INTEGER, NEWLINE

# Set regex strings to just find the CTD data (with options for DOSTA or FLORT).
DOSTA = FLOAT + r',\s+'
FLORT = INTEGER + r',\s+' + INTEGER + r',\s+' + INTEGER + r',\s+'
CTD_DATE = r'(\d{2}\s\w{3}\s\d{4}\s\d{2}:\d{2}:\d{2})'

BASE_PATTERN = (
    DCL_TIMESTAMP + r'\s+' +    # DCL Time-Stamp
    r'(?:\[\w*:\w*\]:|\#)*\s+' +   # DCL logger ID (may not be present)
    FLOAT + r',\s+' +           # temperature
    FLOAT + r',\s+' +           # conductivity
    FLOAT + r',\s+'             # pressure
)

CTDBP1 = BASE_PATTERN + CTD_DATE + NEWLINE
CTDBP2 = BASE_PATTERN + DOSTA + CTD_DATE + NEWLINE
CTDBP3 = BASE_PATTERN + FLORT + CTD_DATE + NEWLINE


def _get_parameter_names_ctdbp(ctd_type):
    parameter_names = [
        'dcl_date_time_string',
        'temperature',
        'conductivity',
        'pressure'
        ]

    if ctd_type == 1:
        parameter_names.extend([
            'ctd_date_time_string'
        ])

    if ctd_type == 2:
        parameter_names.extend([
            'oxygen_concentration',
            'ctd_date_time_string'
        ])

    if ctd_type == 3:
        parameter_names.extend([
            'raw_backscatter',
            'raw_chlorophyll',
            'raw_cdom',
            'ctd_date_time_string'
        ])

    return parameter_names


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the CTDBP specific
    methods to parse the data, and extracts the CTDBP data records from the DCL
    daily log files.
    """
    def __init__(self, infile, ctd_type):
        self.initialize(infile, _get_parameter_names_ctdbp(ctd_type))
        self.ctd_type = ctd_type

    def parse_data(self):
        '''
        Iterate through the record lines (defined via the regex expression
        above) in the data object, and parse the data into a pre-defined
        dictionary object created using the Bunch class.
        '''
        if self.ctd_type == 1:
            REGEX = re.compile(CTDBP1, re.DOTALL)

        if self.ctd_type == 2:
            REGEX = re.compile(CTDBP2, re.DOTALL)

        if self.ctd_type == 3:
            REGEX = re.compile(CTDBP3, re.DOTALL)

        for line in self.raw:
            match = REGEX.match(line)
            if match:
                self._build_parsed_values(match)

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # Use the date_time_string to calculate an epoch timestamp (seconds since
        # 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.time.append(epts)
        self.data.dcl_date_time_string.append(str(match.group(1)))

        # Assign the remaining MET data to the named parameters
        self.data.temperature.append(float(match.group(2)))
        self.data.conductivity.append(float(match.group(3)))
        self.data.pressure.append(float(match.group(4)))

        if self.ctd_type == 1:
            self.data.ctd_date_time_string.append(str(match.group(5)))

        if self.ctd_type == 2:
            self.data.oxygen_concentration.append(float(match.group(5)))
            self.data.ctd_date_time_string.append(str(match.group(6)))

        if self.ctd_type == 3:
            self.data.raw_backscatter.append(int(match.group(5)))
            self.data.raw_chlorophyll.append(int(match.group(6)))
            self.data.raw_cdom.append(int(match.group(7)))
            self.data.ctd_date_time_string.append(str(match.group(8)))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)
    ctd_type = args.switch

    # initialize the Parser object for CTDBP
    ctdbp = Parser(infile, ctd_type)

    # load the data into a buffered object and parse the data into a dictionary
    ctdbp.load_ascii()
    ctdbp.parse_data(ctd_type)

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, ctdbp.data.toDict())

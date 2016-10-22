#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.parsers.parse_flort
@file cgsn_parsers/parsers/parse_flort.py
@author Christopher Wingard
@brief Parses flort data logged by the custom built WHOI data loggers.
'''
import os
import re
import scipy.io as sio

# Import common utilites and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, INTEGER, NEWLINE

# Regex pattern for a line with a DCL time stamp, possible DCL status value and
# the 12 following met data values.
PATTERN = (
    DCL_TIMESTAMP + r'\s+' +                   # DCL Time-Stamp
    r'([0-9/]+[0-9]+\s+[0-9:]+[0-9]+)' + r'\s+' +          # FLORT Date and Time
    INTEGER + r'\s+' +                         # measurement_wavelength_beta
    INTEGER + r'\s+' +                         # raw_signal_beta
    INTEGER + r'\s+' +                         # measurement_wavelength_chl
    INTEGER + r'\s+' +                         # raw_signal_chl
    INTEGER + r'\s+' +                         # measurement_wavelength_cdom
    INTEGER + r'\s+' +                         # raw_signal_cdom
    INTEGER + r'\s*' +                         # raw_internal_temp
    NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_flort = [
        'dcl_date_time_string',
        'flort_date_time_string',
        'measurement_wavelength_beta',
        'raw_signal_beta',
        'measurement_wavelength_chl',
        'raw_signal_chl',
        'measurement_wavelength_cdom',
        'raw_signal_cdom',
        'raw_internal_temp'
    ]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the flort specific
    methods to parse the data, and extracts the flort data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_flort)

    def parse_data(self):
        '''
        Iterate through the record lines (defined via the regex expression
        above) in the data object, and parse the data into a pre-defined
        dictionary object created using the Bunch class.
        '''
        for line in self.raw:
            match = REGEX.match(line)
            if match:
                self._build_parsed_values(match)

    def _build_parsed_values(self, match):
        '''
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        '''
        # Use the date_time_string to calculate an epoch timestamp (seconds since
        # 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.time.append(epts)
        self.data.dcl_date_time_string.append(str(match.group(1)))

        # Assign the remaining MET data to the named parameters
        self.data.flort_date_time_string.append(re.sub('\t', ' ', str(match.group(2))))
        self.data.measurement_wavelength_beta.append(int(match.group(3)))
        self.data.raw_signal_beta.append(int(match.group(4)))
        self.data.measurement_wavelength_chl.append(int(match.group(4)))
        self.data.raw_signal_chl.append(int(match.group(5)))
        self.data.measurement_wavelength_cdom.append(int(match.group(6)))
        self.data.raw_signal_cdom.append(int(match.group(7)))
        self.data.raw_internal_temp.append(int(match.group(8)))

if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for flort
    flort = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    flort.load_ascii()
    flort.parse_data()

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, flort.data.toDict())

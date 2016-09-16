#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.parsers.parse_presf
@file cgsn_parsers/parsers/parse_presf.py
@author Christopher Wingard
@brief Parses PRESF data logged by the custom built WHOI data loggers.
'''
import os
import re
import scipy.io as sio

# Import common utilites and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, NEWLINE

# Regex pattern for a line with a DCL time stamp and the PRESF tide data.
presf_date = r'(\d{2}\s\w{3}\s\d{4}\s\d{2}:\d{2}:\d{2})'
PATTERN = (
    DCL_TIMESTAMP + r'\s+tide:\s+' +            # DCL Time-Stamp
    r'start time = ' + presf_date + r',\s+' +   # PRESF Time-Stamp
    r'p = ' + FLOAT + r',\s+' +                 # Absolute pressure (psia)
    r'pt = ' + FLOAT + r',\s+' +                # Pressure temperature (degC)
    r't = ' + FLOAT + NEWLINE                   # Seawater temperature (degC)
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_presf = [
        'dcl_date_time_string',
        'presf_date_time_string',
        'absolute_pressure',
        'pressure_temp',
        'seawater_temperature'
    ]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the PRESF specific
    methods to parse the data, and extracts the PRESF data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_presf)

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
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # Use the date_time_string to calculate an epoch timestamp (seconds
        # since 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.time.append(epts)
        self.data.dcl_date_time_string.append(str(match.group(1)))

        # Assign the remaining PRESF data to the named parameters
        self.data.presf_date_time_string.append(str(match.group(2)))
        self.data.absolute_pressure.append(float(match.group(3)))
        self.data.pressure_temp.append(float(match.group(4)))
        self.data.seawater_temperature.append(float(match.group(5)))

if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for PRESF
    presf = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    presf.load_ascii()
    presf.parse_data()

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, presf.data.toDict())

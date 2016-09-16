#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.parsers.parse_hydgn
@file cgsn_parsers/parsers/parse_hydgn.py
@author Christopher Wingard
@brief Parses hydrogen data logged by the custom built WHOI data loggers.
'''
import os
import re
import scipy.io as sio

# Import common utilites and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, NEWLINE

# Regex pattern for a line with a DCL time stamp and hydrogen data
PATTERN = (
    DCL_TIMESTAMP + r'\s+\*' +  # DCL Time-Stamp
    FLOAT + r'\s+' +            # hydrogen LEL percentage
    FLOAT + r'\s+' +            # hydrogen LEL ... printed again ... why?
    r'\%\s+' + NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_hydgn = [
        'dcl_date_time_string',
        'hydrogen_concentration'
    ]


class Parser(ParserCommon):
    '''
    A Parser subclass that calls the Parser base class, adds the METBK specific
    methods to parse the data, and extracts the METBK data records from the DCL
    daily log files.
    '''
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_hydgn)

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
        # Use the date_time_string to calculate an epoch timestamp (seconds since
        # 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.time.append(epts)
        self.data.dcl_date_time_string.append(str(match.group(1)))

        # Assign the remaining MET data to the named parameters
        self.data.hydrogen_concentration.append(float(match.group(2)))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for hydrogen
    hydrogen = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    hydrogen.load_ascii()
    hydrogen.parse_data()

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, hydrogen.data.toDict())

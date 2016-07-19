# -*- coding: utf-8 -*-
'''
@package parsers.parse_gps
@file parsers/parse_gps.py
@author Christopher Wingard
@brief Parses the GPS data logged by the custom built WHOI data loggers.
'''
__author__ = 'Christopher Wingard'
__license__ = 'Apache 2.0'

import os
import re
import scipy.io as sio

# Import common utilites and base classes
from common import ParameterNames, Parser
from common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, INTEGER, STRING, NEWLINE

# Regex pattern for the power system records
PATTERN = (
    DCL_TIMESTAMP + r'\sGPS\s' +
    FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    INTEGER + r'\s' + INTEGER + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    STRING + r'\s' + STRING + r'\s' +
    r'(\S+\s\w)' + r'\s' + r'(\S+\s\w)' + NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)


class ParameterNames(ParameterNames):
    '''
    Extend the parameter names with parameters for the PWRSYS (time is already
    declared in the base class).
    '''
    ParameterNames.parameters.extend([
        'dcl_date_time_string',
        'latitude',
        'longitude',
        'speed_over_ground',
        'course_over_ground',
        'fix_quality',
        'number_satellites',
        'horiz_dilution_precision',
        'altitude',
        'gps_date_string',
        'gps_time_string',
        'latitude_string',
        'longitude_string',
    ])


class Parser(Parser):
    """
    A Parser subclass that calls the Parser base class, adds the PWRSYS specific
    methods to parse the data, and extracts the PWRSYS data records from the DCL
    daily log files.
    """
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
        self.data.latitude.append(float(match.group(2)))
        self.data.longitude.append(float(match.group(3)))
        self.data.speed_over_ground.append(float(match.group(4)))
        self.data.course_over_ground.append(float(match.group(5)))
        self.data.fix_quality.append(int(match.group(6)))
        self.data.number_satellites.append(int(match.group(7)))
        self.data.horiz_dilution_precision.append(float(match.group(8)))
        self.data.altitude.append(float(match.group(9)))
        self.data.gps_date_string.append(str(match.group(10)))
        self.data.gps_time_string.append(str(match.group(11)))
        self.data.latitude_string.append(str(match.group(12)))
        self.data.longitude_string.append(str(match.group(13)))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for PWRSYS
    gps = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    gps.load_ascii()
    gps.parse_data()

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, gps.data.toDict())

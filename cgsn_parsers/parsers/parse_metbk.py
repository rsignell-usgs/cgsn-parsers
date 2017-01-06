#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.parsers.parse_metbk
@file cgsn_parsers/parsers/parse_metbk.py
@author Christopher Wingard
@brief Parses metbk data logged by the custom built WHOI data loggers.
'''
import os
import re

# Import common utilites and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLTNAN, NEWLINE

# Regex pattern for a line with a DCL time stamp, possible DCL status value and
# the 12 following met data values.
PATTERN = (
    DCL_TIMESTAMP + r'\s+' +   # DCL Time-Stamp
    r'(?:\[\w*:\w*\]:\s*)*' +  # DCL status string (usually not be present)
    FLTNAN + r'\s+' +           # barometric pressure
    FLTNAN + r'\s+' +           # relative humidity
    FLTNAN + r'\s+' +           # air temperature
    FLTNAN + r'\s+' +           # longwave irradiance
    FLTNAN + r'\s+' +           # precipitation level
    FLTNAN + r'\s+' +           # sea surface temperature
    FLTNAN + r'\s+' +           # sea surface conductivity
    FLTNAN + r'\s+' +           # shortwave irradiance
    FLTNAN + r'\s+' +           # eastward wind velocity
    FLTNAN + r'\s+' +           # northward wind velocity
    FLTNAN + r'\s+' +           # repeated sea surface conductivity
    FLTNAN + NEWLINE            # dummy field for ASIMET battery voltage
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_metbk = [
    'dcl_date_time_string',
    'barometric_pressure',
    'relative_humidity',
    'air_temperature',
    'longwave_irradiance',
    'precipitation_level',
    'sea_surface_temperature',
    'sea_surface_conductivity',
    'shortwave_irradiance',
    'eastward_wind_velocity',
    'northward_wind_velocity'
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the METBK specific
    methods to parse the data, and extracts the METBK data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_metbk)

    def parse_data(self):
        '''
        Iterate through the record lines (defined via the regex expression
        above) in the data object, and parse the data into a pre-defined
        dictionary object created using the Bunch class.
        '''
        for line in self.raw:
            # Some missing sensor data is represented as either a 'NaN', 'Na', 
            # or 'N'. While 'NaN' is fine and can be used to represent missing
            # data, 'Na' or 'N' needs to be set to a full 'NaN'.
            line = re.sub(r'\sN[aN]*\s', '\sNaN\s', line)
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
        self.data.barometric_pressure.append(float(match.group(2)))
        self.data.relative_humidity.append(float(match.group(3)))
        self.data.air_temperature.append(float(match.group(4)))
        self.data.longwave_irradiance.append(float(match.group(5)))
        self.data.precipitation_level.append(float(match.group(6)))
        self.data.sea_surface_temperature.append(float(match.group(7)))
        self.data.sea_surface_conductivity.append(float(match.group(8)))
        self.data.shortwave_irradiance.append(float(match.group(9)))
        self.data.eastward_wind_velocity.append(float(match.group(10)))
        self.data.northward_wind_velocity.append(float(match.group(11)))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for METBK
    metbk = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    metbk.load_ascii()
    metbk.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(metbk.data.toJSON())

# -*- coding: utf-8 -*-
'''
@package parsers.parse_metbk
@file parsers/parse_metbk.py
@author Christopher Wingard
@brief Parses metbk data logged by the custom built WHOI data loggers.
'''
__author__ = 'Christopher Wingard'
__license__ = 'Apache 2.0'

import os
import re
import scipy.io as sio

# Import common utilites and base classes
from common import ParameterNames, Parser
from common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, NEWLINE


# Regex pattern for a line with a DCL time stamp, possible DCL status value and
# the 12 following met data values.
PATTERN = (
    DCL_TIMESTAMP + r'\s+' +   # DCL Time-Stamp
    r'(?:\[\w*:\w*\]:\s*)*' +  # DCL status string (usually not be present) 
    FLOAT + r'\s+' +           # barometric pressure
    FLOAT + r'\s+' +           # relative humidity
    FLOAT + r'\s+' +           # air temperature
    FLOAT + r'\s+' +           # longwave irradiance
    FLOAT + r'\s+' +           # precipitation level
    FLOAT + r'\s+' +           # sea surface temperature
    FLOAT + r'\s+' +           # sea surface conductivity
    FLOAT + r'\s+' +           # shortwave irradiance
    FLOAT + r'\s+' +           # eastward wind velocity
    FLOAT + r'\s+' +           # northward wind velocity
    FLOAT + r'\s+' +           # repeated sea surface conductivity
    FLOAT + NEWLINE            # dummy field for ASIMET battery voltage
)
REGEX = re.compile(PATTERN, re.DOTALL)


class ParameterNames(ParameterNames):
    '''
    Extend the parameter names with parameters for the METBK (time is already
    declared in the base class).
    '''
    ParameterNames.parameters.extend([
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
    ])


class Parser(Parser):
    """
    A Parser subclass that calls the Parser base class, adds the METBK specific
    methods to parse the data, and extracts the METBK data records from the DCL
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

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, metbk.data.toDict())

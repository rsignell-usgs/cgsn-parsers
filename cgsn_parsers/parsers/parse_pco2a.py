#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.parsers.parse_pco2a
@file cgsn_parsers/parsers/parse_pco2a.py
@author Christopher Wingard
@brief Parses PCO2A data logged by the custom built WHOI data loggers.
'''
import os
import re

# Import common utilites and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, INTEGER, NEWLINE

# Regex pattern for a line with a DCL time stamp, possible DCL status value and
# the 12 following met data values.
PATTERN = (
    DCL_TIMESTAMP + r'\s+' +                   # DCL Time-Stamp
    r'#([0-9/]+\s[0-9:]+), M,\s*' +            # Pro-Oceanus Time Stamp
    INTEGER + r',\s*' +                        # zero_a2d
    INTEGER + r',\s*' +                        # current_a2d
    FLOAT + r',\s*' +                          # measured_co2
    FLOAT + r',\s*' +                          # avg_irga_temperature
    FLOAT + r',\s*' +                          # humidity
    FLOAT + r',\s*' +                          # humidity_temperature
    INTEGER + r',\s*' +                        # gas_stream_pressure
    FLOAT + r',\s*' +                          # irga_detector_temperature
    FLOAT + r',\s*' +                          # irga_source_temperature
    r'([AW]{1})' +                             # co2_source
    NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_pco2a = [
        'dcl_date_time_string',
        'co2_date_time_string',
        'zero_a2d',
        'current_a2d',
        'measured_water_co2',
        'avg_irga_temperature',
        'humidity',
        'humidity_temperature',
        'gas_stream_pressure',
        'irga_detector_temperature',
        'irga_source_temperature',
        'co2_source'
    ]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the PCO2A specific
    methods to parse the data, and extracts the PCO2A data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_pco2a)

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
        self.data.co2_date_time_string.append(str(match.group(2)))
        self.data.zero_a2d.append(int(match.group(3)))
        self.data.current_a2d.append(int(match.group(4)))
        self.data.measured_water_co2.append(float(match.group(5)))
        self.data.avg_irga_temperature.append(float(match.group(6)))
        self.data.humidity.append(float(match.group(7)))
        self.data.humidity_temperature.append(float(match.group(8)))
        self.data.gas_stream_pressure.append(int(match.group(9)))
        self.data.irga_detector_temperature.append(float(match.group(10)))
        self.data.irga_source_temperature.append(float(match.group(11)))
        self.data.co2_source.append(str(match.group(12)))

if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for PCO2A
    pco2a = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    pco2a.load_ascii()
    pco2a.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(pco2a.data.toJSON())

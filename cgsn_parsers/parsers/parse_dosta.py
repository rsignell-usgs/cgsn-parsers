#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.parsers.parse_dosta
@file cgsn_parsers/parsers/parse_dosta.py
@author Christopher Wingard
@brief Parses DOSTA data logged by the custom built WHOI data loggers.
'''
import os
import re

# Import common utilites and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, INTEGER, NEWLINE

# Regex pattern for a line with a DCL time stamp, possible DCL status value and
# the 12 following met data values.
PATTERN = (
    DCL_TIMESTAMP + r'\s+' +    # DCL Time-Stamp
    INTEGER + r'\s+' +          # Optode model number
    INTEGER + r'\s+' +          # Optode serial number
    FLOAT + r'\s+' +            # Oxygen Concentration (microMolar)
    FLOAT + r'\s+' +            # Relative Air Saturation (%)
    FLOAT + r'\s+' +            # Temperature (degC)
    FLOAT + r'\s+' +            # Calibrated Phase (deg)
    FLOAT + r'\s+' +            # Temperature compensated phase (deg)
    FLOAT + r'\s+' +            # Phase measurement with blue light (deg)
    FLOAT + r'\s+' +            # Phase measurement with red light (deg)
    FLOAT + r'\s+' +            # Amplitude measurement with blue light (mV)
    FLOAT + r'\s+' +            # Amplitude measurement with red light (mV)
    FLOAT + NEWLINE             # Voltage from thermistor bridge (mV)
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_dosta = [
        'date_time_string',
        'product_number',
        'serial_number',
        'estimated_oxygen_concentration',
        'estimated_oxygen_saturation',
        'optode_temperature',
        'calibrated_phase',
        'temp_compensated_phase',
        'blue_phase',
        'red_phase',
        'blue_amplitude',
        'red_amplitude',
        'raw_temperature'
    ]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the PCO2A specific
    methods to parse the data, and extracts the PCO2A data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_dosta)

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
        self.data.date_time_string.append(str(match.group(1)))

        # Assign the remaining DOSTA data to the named parameters
        self.data.product_number.append(int(match.group(2)))
        self.data.serial_number.append(int(match.group(3)))
        self.data.estimated_oxygen_concentration.append(float(match.group(4)))
        self.data.estimated_oxygen_saturation.append(float(match.group(5)))
        self.data.optode_temperature.append(float(match.group(6)))
        self.data.calibrated_phase.append(float(match.group(7)))
        self.data.temp_compensated_phase.append(float(match.group(8)))
        self.data.blue_phase.append(float(match.group(9)))
        self.data.red_phase.append(float(match.group(10)))
        self.data.blue_amplitude.append(float(match.group(11)))
        self.data.red_amplitude.append(float(match.group(12)))
        self.data.raw_temperature.append(float(match.group(13)))

if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for PCO2A
    dosta = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    dosta.load_ascii()
    dosta.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(dosta.data.toJSON())

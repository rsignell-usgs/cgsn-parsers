# -*- coding: utf-8 -*-
'''
@package parsers.parse_spkir
@file parsers/parse_spkir.py
@author Christopher Wingard
@brief Parses spkir data logged by the custom built WHOI data loggers.
'''
import os
import re
import scipy.io as sio

from struct import Struct

# Import common utilites and base classes
from common import ParameterNames, Parser
from common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, NEWLINE

# Regex pattern for a line with a DCL time stamp and the OCR-507 data sample
PATTERN = (
    DCL_TIMESTAMP + r'\s+' +     # DCL Time-Stamp
    r'SATDI7' + r'([\d]{4})' +   # Serial number
    FLOAT +                      # Timer (seconds)
    b'([\x00-\xFF]{38})' +       # binary data packet
    NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

# Set the format for the binary packet for later unpacking
SPKIR = Struct('<h7I3HBB')


class ParameterNames(ParameterNames):
    '''
    Extend the parameter names with parameters for the SPKIR (time is already
    declared in the base class).
    '''
    ParameterNames.parameters.extend([
        'date_time_string',
        'serial_number',
        'timer',
        'sample_delay',
        'raw_channels',
        'input_voltage',
        'analog_rail_voltage',
        'frame_counter',
        'internal_temperature'
    ])


class Parser(Parser):
    '''
    A Parser subclass that calls the Parser base class, adds the SPKIR specific
    methods to parse the data, and extracts the SPKIR data records from the DCL
    daily log files.
    '''
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

        self.data.date_time_string.append(str(match.group(1)))
        self.data.serial_number.append(int(match.group(2)))
        self.data.timer.append(float(match.group(3)))

        # Unpack the binary data packet
        (delay, ch1, ch2, ch3, ch4, ch5, ch6, ch7,
         Vin, Va, temp, count, check) = SPKIR.unpack(match.group(4))

        # Assign the remaining SPKIR data to the named parameters
        self.data.sample_delay.append(delay)
        self.data.raw_channels.append([ch1, ch2, ch3, ch4, ch5, ch6, ch7])
        self.data.input_voltage.append(Vin)
        self.data.analog_rail_voltage.append(Va)
        self.data.frame_counter.append(count)
        self.data.internal_temperature.append(temp)

if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for SPKIR
    spkir = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    spkir.load_ascii()
    spkir.parse_data()

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, spkir.data.toDict())

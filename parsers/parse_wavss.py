# -*- coding: utf-8 -*-
'''
@package parsers.parse_wavss
@file parsers/parse_wavss.py
@author Christopher Wingard
@brief Parses WAVSS data logged by the custom built WHOI data loggers.
'''
__author__ = 'Christopher Wingard'
__license__ = 'Apache 2.0'

import os
import re
import scipy.io as sio

# Import common utilites and base classes
from common import ParameterNames, ParserCommon
from common import dcl_to_epoch, inputs, DCL_TIMESTAMP, INTEGER, FLOAT, NEWLINE

# Regex pattern for a line with a DCL time stamp, possible DCL status value and
# the wave statistics summary line
PATTERN = (
    DCL_TIMESTAMP + r'\s+' +       # DCL Time-Stamp
    r'\$TSPWA,(\d{8}),' +          # NMEA sentence header and date
    r'(\d{6}),' +                  # time
    r'(\d{5}),buoyID,,,' +         # Tri-Axys unit serial number    
    INTEGER + r',' +               # Number of Zero Crossings
    FLOAT + r',' +                 # Average wave height (Havg)
    FLOAT + r',' +                 # Tz (Mean Spectral  Period)
    FLOAT + r',' +                 # Hmax (Maximum Wave Height)
    FLOAT + r',' +                 # Hsig (Significant Wave Height)
    FLOAT + r',' +                 # Tsig (Significant Period)
    FLOAT + r',' +                 # H10 (average height of highest 1/10 of waves)
    FLOAT + r',' +                 # T10 (average period of H10 waves)
    FLOAT + r',' +                 # Tavg (Mean Wave Period)
    FLOAT + r',' +                 # TP (Peak Period)
    FLOAT + r',' +                 # TP5
    FLOAT + r',' +                 # HMO
    FLOAT + r',' +                 # Mean Direction
    FLOAT +                        # Mean Spread
    r'\*[0-9a-fA-F]+' + NEWLINE    # checksum and <cr><lf>
)
REGEX = re.compile(PATTERN, re.DOTALL)


_parameter_names_wavss = [
    'dcl_date_time_string',
    'date_string',
    'time_string',
    'serial_number',
    'num_zero_crossings',
    'average_wave_height',
    'mean_spectral_period',
    'maximum_wave_height',
    'significant_wave_height',
    'significant_wave_period',
    'average_tenth_height',
    'average_tenth_period',
    'average_wave_period',
    'peak_period',
    'peak_period_read',
    'spectral_wave_height',
    'mean_wave_direction',
    'mean_directional_spread'
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the wavss specific
    methods to parse the data, and extracts the wavss data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_wavss)

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

        # Assign the remaining WAVSS data to the named parameters
        self.data.date_string.append(str(match.group(2)))
        self.data.time_string.append(str(match.group(3)))
        self.data.serial_number.append(str(match.group(4)))
        self.data.num_zero_crossings.append(int(match.group(5)))
        self.data.average_wave_height.append(float(match.group(6)))
        self.data.mean_spectral_period.append(float(match.group(7)))
        self.data.maximum_wave_height.append(float(match.group(8)))
        self.data.significant_wave_height.append(float(match.group(9)))
        self.data.significant_wave_period.append(float(match.group(10)))
        self.data.average_tenth_height.append(float(match.group(11)))
        self.data.average_tenth_period.append(float(match.group(12)))
        self.data.average_wave_period.append(float(match.group(13)))
        self.data.peak_period.append(float(match.group(14)))
        self.data.peak_period_read.append(float(match.group(15)))
        self.data.spectral_wave_height.append(float(match.group(16)))
        self.data.mean_wave_direction.append(float(match.group(17)))
        self.data.mean_directional_spread.append(float(match.group(18)))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for wavss
    wavss = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    wavss.load_ascii()
    wavss.parse_data()

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, wavss.data.toDict())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.parsers.parse_fdchp
@file cgsn_parsers/parsers/parse_fdchp.py
@author Christopher Wingard
@brief Parses FDCHP data logged by the custom built WHOI data loggers.
'''
import os
import re
import scipy.io as sio

# Import common utilites and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP

# Set regex string to just find the FDCHP data.
PATTERN = (
    DCL_TIMESTAMP + r'\s+' +         # DCL Time Stamp
    r'FLUXDATA\s+' +                 # FLUXDATA message leader
    r'(.+)\n'                        # rest of the data, comma separated
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_fdchp = [
        'dcl_date_time_string',
        'start_time',
        'processing_version',
        'status',
        'avg_wind_u',
        'avg_wind_v',
        'avg_wind_w',
        'speed_of_sound',
        'std_wind_u',
        'std_wind_v',
        'std_wind_w',
        'std_speed_of_sound',
        'max_wind_u',
        'max_wind_v',
        'max_wind_w',
        'max_speed_of_sound',
        'min_wind_u',
        'min_wind_v',
        'min_wind_w',
        'min_speed_of_sound',
        'acceleration_x',
        'acceleration_y',
        'acceleration_z',
        'std_acc_x',
        'std_acc_y',
        'std_acc_z',
        'max_acc_x',
        'max_acc_y',
        'max_acc_z',
        'min_acc_x',
        'min_acc_y',
        'min_acc_z',
        'rate_x',
        'rate_y',
        'rate_z',
        'std_rate_x',
        'std_rate_y',
        'std_rate_z',
        'max_rate_x',
        'max_rate_y',
        'max_rate_z',
        'min_rate_x',
        'min_rate_y',
        'min_rate_z',
        'heading',
        'pitch',
        'roll',
        'std_heading',
        'std_pitch',
        'std_roll',
        'max_heading',
        'max_pitch',
        'max_roll',
        'min_heading',
        'min_pitch',
        'min_roll',
        'u_corrected',
        'v_corrected',
        'w_corrected',
        'std_u_corrected',
        'std_v_corrected',
        'std_w_corrected',
        'wind_speed',
        'momentum_flux_uw',
        'momentum_flux_vw',
        'buoyancy_flux',
        'wave_motion'
        ]


class Parser(ParserCommon):
    '''
    A Parser subclass that calls the Parser base class, adds the FDCHP specific
    methods to parse the data, and extracts the FDCHP data records from the DCL
    daily log files.
    '''
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_fdchp)

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
        # Use the date_time_string to calculate an epoch timestamp (seconds
        # since 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.time.append(epts)
        self.data.dcl_date_time_string.append(str(match.group(1)))

        # Assign the remaining FDCHP data to the named parameters, where the
        # rest of the data is in a (mostly) comma separated string, so ... need
        # to use filter and a split that looks for both commas and spaces
        # (sloppy programming by the developer of the instrument).
        data = filter(None, re.split(r',|\s', match.group(2)))

        # index through the list of parameter names and assign the data
        cnt = 0
        for p in _parameter_names_fdchp[1:]:
            if cnt == 2:
                # the status parameter is a 6 character hex value ...
                self.data[p].append(str(data[cnt]))
            else:
                # all other values are floats
                self.data[p].append(float(data[cnt]))

            cnt += 1

if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for FDCHP
    fdchp = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    fdchp.load_ascii()
    fdchp.parse_data()

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, fdchp.data.toDict())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package parsers.parse_phsen
@file parsers/parse_phsen.py
@author Christopher Wingard
@brief Parses PHSEN data logged by the custom built WHOI data loggers.
'''
__author__ = 'Christopher Wingard'
__license__ = 'Apache 2.0'

import os
import re
import scipy.io as sio

# Import common utilites and base classes
from common import ParameterNames, Parser
from common import dcl_to_epoch, inputs, DCL_TIMESTAMP

# Regex pattern for a line with a DCL time stamp, the "*" character, 4 unknown 
# characters (2 for a 1 byte hash of the unit serial number and calibration, 
# and 2 for the length byte), and a '0A' (indicating a Type 10, or pH, data 
# record), all of which combine to denote the start of a sampling record.
PATTERN_START = (
    DCL_TIMESTAMP + r'\s+' +                # DCL Time-Stamp
    r'(\*[A-F0-9]{4}0A[A-F0-9]+)' + r'\s'   # Beginning of a pH sampling record
)
REGEX_START = re.compile(PATTERN_START, re.DOTALL)


class ParameterNames(ParameterNames):
    '''
    Extend the parameter names with parameters for the PHSEN (time is already
    declared in the base class).
    '''
    ParameterNames.parameters.extend([
        'dcl_date_time_string',
        'record_length',
        'record_type',
        'record_time',
        'thermistor_start',
        'reference_measurements',
        'light_measurements',
        'voltage_battery',
        'thermistor_end'
    ])


class Parser(Parser):
    """
    A Parser subclass that calls the Parser base class, adds the PHSEN specific
    methods to parse the data, and extracts the PHSEN data records from the DCL
    daily log files.
    """
    def parse_data(self):
        '''
        Iterate through the record markers (defined via the regex expression
        above) in the data object, and parse the data file into a pre-defined
        dictionary object created using the Bunch class.
        '''
        record_marker = [m.start() for m in REGEX_START.finditer(self.raw)]

        # if we have found record markers, work through the data
        while record_marker:
            # for each record marker, set the start and stop points of the sample
            start = record_marker[0]
            if len(record_marker) > 1:
                # stopping point is the next record marker
                stop = record_marker[1]
            else:
                # stopping point is the end of the file
                stop = len(self.raw)

            # now create the sample string
            sample = self.raw[start:stop]

            # pull out of the sample string the DCL timestamp
            timestamp = REGEX_START.match(sample).group(1)

            # clean up the rest of the extraneous strings in the sample string
            sample = re.sub(DCL_TIMESTAMP, '', sample)  # get rid of the extra time stamps
            sample = re.sub(r'\s+', '', sample)         # get rid of newlines and spaces
            sample = re.sub(r'\[\w+:\w+\]:.+', '', sample)  # get rid of the stop messages

            # if we have a complete sample, process it.
            if len(sample) == 465:
                # print '%s --- %s\n' % (timestamp, sample)
                self._build_parsed_values(timestamp, sample)

            # bump to the next marker
            record_marker.pop(0)

    def _build_parsed_values(self, timestamp, sample):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # Use the date_time_string to calculate an epoch timestamp (seconds since
        # 1970-01-01)
        epts = dcl_to_epoch(timestamp)
        self.data.time.append(epts)
        self.data.dcl_date_time_string.append(timestamp)

        self.data.record_length.append(int(sample[3:5], 16))
        self.data.record_type.append(int(sample[5:7], 16))
        self.data.record_time.append(int(sample[7:15], 16))
        self.data.thermistor_start.append(int(sample[15:19], 16))

        cnt = 19
        reference = []  # create empty list to hold the 16 reference measurements
        for i in range(0, 16):
            indx = (i * 4) + cnt
            reference.append(int(sample[indx:indx+4], 16))

        self.data.reference_measurements.append(reference)

        cnt = indx + 4  # reset the counter to start with the light measurements
        light = []  # create empty list to hold the 92 light measurements
        for i in range(0, 92):
            indx = (i * 4) + cnt
            light.append(int(sample[indx:indx+4], 16))

        self.data.light_measurements.append(light)
        
        cnt = indx + 8  # reset the counter for the final parameters
        self.data.voltage_battery.append(int(sample[cnt:cnt+4], 16))
        self.data.thermistor_end.append(int(sample[cnt+4:cnt+8], 16))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for PHSEN
    phsen = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    phsen.load_binary()     # not really binary, but this creates on object that is easy to parse
    phsen.parse_data()

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, phsen.data.toDict())

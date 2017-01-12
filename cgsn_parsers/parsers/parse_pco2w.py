#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.parsers.parse_pco2w
@file cgsn_parsers/parsers/parse_pco2w.py
@author Christopher Wingard
@brief Parses PCO2W data logged by the custom built WHOI data loggers.
'''
import os
import re

# Import common utilites and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP

# Regex pattern for a line with a DCL time stamp, the "*" character, 4 unknown
# characters (2 for a 1 byte hash of the unit serial number and calibration,
# and 2 for the length byte), and a '11' (indicating a Type 11, or Device 1,
# data record), all of which combine to denote the start of a sampling record.
PATTERN = (
    DCL_TIMESTAMP + r'\s+' +                  # DCL Time-Stamp
    r'(\*[A-F0-9]{4}11[A-F0-9]+)' + r'\s' +   # Device 1 (external pump) sample collection
    DCL_TIMESTAMP + r'\s+' +                  # DCL Time-Stamp
    r'(\*[A-F0-9]{4}04[A-F0-9]+)' + r'\s'     # Device 0 sample processing
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_pco2w = [
        'collect_date_time',
        'process_date_time',
        'unique_id',
        'record_length',
        'record_type',
        'record_time',
        'light_measurements',
        'voltage_battery',
        'thermistor_raw'
    ]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the pco2w specific
    methods to parse the data, and extracts the pco2w data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_pco2w)

    def parse_data(self):
        '''
        Iterate through the record markers (defined via the regex expression
        above) in the data object, and parse the data file into a pre-defined
        dictionary object created using the Bunch class.
        '''
        record_marker = [m.start() for m in REGEX.finditer(self.raw)]

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

            # now create the initial sample string
            sample = self.raw[start:stop]
            match = REGEX.match(sample)

            # pull out of the sample string the DCL timestamps and a cleaned sample string
            collect_time = match.group(1)
            process_time = match.group(3)
            sample = match.group(4)

            # if we have a complete sample, process it.
            if len(sample) == 81:
                # print '%s --- %s\n' % (timestamp, sample)
                self._build_parsed_values(collect_time, process_time, sample)

            # bump to the next marker
            record_marker.pop(0)

    def _build_parsed_values(self, collect_time, process_time, sample):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # Use the date_time_string from the collection time to calculate an
        # epoch timestamp (seconds since 1970-01-01), using that values as the
        # preferred time record for the data
        epts = dcl_to_epoch(collect_time)
        self.data.time.append(epts)
        self.data.collect_date_time.append(collect_time)
        self.data.process_date_time.append(process_time)

        self.data.unique_id.append(int(sample[1:3], 16))
        self.data.record_length.append(int(sample[3:5], 16))
        self.data.record_type.append(int(sample[5:7], 16))
        self.data.record_time.append(int(sample[7:15], 16))

        cnt = 15    # set the counter for the light measurements
        light = []  # create empty list to hold the 14 light measurements
        for i in range(0, 14):
            indx = (i * 4) + cnt
            light.append(int(sample[indx:indx+4], 16))

        self.data.light_measurements.append(light)

        cnt = indx + 4  # reset the counter for the final parameters
        self.data.voltage_battery.append(int(sample[cnt:cnt+4], 16))
        self.data.thermistor_raw.append(int(sample[cnt+4:cnt+8], 16))

if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for pco2w
    pco2w = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    pco2w.load_binary()     # not really binary, but this creates on object that is easy to parse
    pco2w.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(pco2w.data.toJSON())

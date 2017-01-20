#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.parsers.parse_nutnr
@file cgsn_parsers/parsers/parse_nutnr.py
@author Christopher Wingard
@brief Parses NUTNR data logged by the custom built WHOI data loggers.
'''
import os
import re

# Import common utilites and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, STRING, NEWLINE

# Set regex string to just find the NUTNR data.
PATTERN = (
    DCL_TIMESTAMP + r'\s+' +         # DCL Time-Stamp
    r'SATN(\w{2})' + r'(\d{4}),' +   # Measurement type and serial #
    STRING + NEWLINE                 # rest of the data, comma separated
)
REGEX = re.compile(PATTERN, re.DOTALL)


def _parameter_names_nutnr(spectra):
    '''
    Setup parameter names depending on the spectral output (full or condensed)
    '''
    parameter_names = [
            'date_time_string',
            'measurement_type',
            'serial_number',
            'date_string',
            'decimal_hours',
            'nitrate_concentration',
            'auxiliary_fit_1st',
            'auxiliary_fit_2nd',
            'auxiliary_fit_3rd',
            'rms_error'
        ]

    if spectra == 1:    # full spectra
        parameter_names.extend([
            'temperature_internal',
            'temperature_spectrometer',
            'temperature_lamp',
            'lamp_on_time',
            'humidity',
            'voltage_lamp',
            'voltage_analog',
            'voltage_main',
            'average_reference',
            'variance_reference',
            'seawater_dark',
            'spectal_average',
            'channel_measurements'
        ])
    
    return parameter_names


class Parser(ParserCommon):
    '''
    A Parser subclass that calls the Parser base class, adds the NUTNR specific
    methods to parse the data, and extracts the NUTNR data records from the DCL
    daily log files.
    '''
    def __init__(self, infile, spectra):
        self.initialize(infile, _parameter_names_nutnr(spectra))
        self.spectra = spectra

    def parse_data(self):
        '''
        Iterate through the record lines (defined via the regex expression
        above) in the data object, and parse the data into a pre-defined
        dictionary object created using the Bunch class.
        '''
        for line in self.raw:
            match = REGEX.match(line)
            if match:
                self._build_parsed_values(match, self.spectra)

    def _build_parsed_values(self, match, spectra):
        '''
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        '''
        # Use the date_time_string to calculate an epoch timestamp (seconds
        # since 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.time.append(epts)
        self.data.date_time_string.append(str(match.group(1)))

        # Assign the remaining NUTNR data to the named parameters
        self.data.measurement_type.append(str(match.group(2)))
        self.data.serial_number.append(int(match.group(3)))

        # the rest of the data is in a comma separated string, so...
        data = (match.group(4)).split(',')

        # data found in all frames
        self.data.date_string.append(str(data[0]))
        self.data.decimal_hours.append(float(data[1]))
        self.data.nitrate_concentration.append(float(data[2]))
        self.data.auxiliary_fit_1st.append(float(data[3]))
        self.data.auxiliary_fit_2nd.append(float(data[4]))
        self.data.auxiliary_fit_3rd.append(float(data[5]))
        self.data.rms_error.append(float(data[6]))

        # data found only in the full frames
        if self.spectra == 1:
            self.data.temperature_internal.append(float(data[7]))
            self.data.temperature_spectrometer.append(float(data[8]))
            self.data.temperature_lamp.append(float(data[9]))
            self.data.lamp_on_time.append(int(data[10]))
            self.data.humidity.append(float(data[11]))
            self.data.voltage_lamp.append(float(data[12]))
            self.data.voltage_analog.append(float(data[13]))
            self.data.voltage_main.append(float(data[14]))
            self.data.average_reference.append(float(data[15]))
            self.data.variance_reference.append(float(data[16]))
            self.data.seawater_dark.append(float(data[17]))
            self.data.spectal_average.append(float(data[18]))
            self.data.channel_measurements.append(map(int, data[19:]))

if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)
    spectra = args.switch

    # initialize the Parser object for NUTNR
    nutnr = Parser(infile, spectra)

    # load the data into a buffered object and parse the data into a dictionary
    nutnr.load_ascii()
    nutnr.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(nutnr.data.toJSON())

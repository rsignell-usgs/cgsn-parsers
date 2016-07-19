# -*- coding: utf-8 -*-
'''
@package parsers.parse_zplsc
@file parsers/parse_zplsc.py
@author Christopher Wingard
@brief Parses zplsc data logged by the custom built WHOI data loggers.
'''
import os
import re
import scipy.io as sio

# Import common utilites and base classes
from common import ParameterNames, Parser
from common import dcl_to_epoch, inputs, DCL_TIMESTAMP, STRING, NEWLINE

# Set regex string to just find the ZPLSC data.
PATTERN = (
    DCL_TIMESTAMP + r'\s+' +         # DCL Time Stamp
    r'@D(\d{14})!@P,' +              # transmission time stamp
    STRING +                         # rest of the data, comma separated
    r'!' + NEWLINE                   # end of the data sentence
)
REGEX = re.compile(PATTERN, re.DOTALL)


class ParameterNames(ParameterNames):
    '''
    Extend the parameter names with parameters for the ZPLSC (time is already
    declared in the base class).
    '''
    ParameterNames.parameters.extend([
        'dcl_date_time_string',
        'transmission_date_string',
        'serial_number',
        'phase',
        'burst_number',
        'number_bins',
        'minimum_values',
        'burst_date_string',
        'tilts',
        'battery_voltage',
        'temperature',
        'frequencies',
        'profiles_freq1',
        'profiles_freq2',
        'profiles_freq3',
        'profiles_freq4'
    ])


class Parser(Parser):
    '''
    A Parser subclass that calls the Parser base class, adds the ZPLSC specific
    methods to parse the data, and extracts the ZPLSC data records from the DCL
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
        # Use the date_time_string to calculate an epoch timestamp (seconds
        # since 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.time.append(epts)
        self.data.dcl_date_time_string.append(str(match.group(1)))

        # Assign the remaining ZPLSC data to the named parameters
        self.data.transmission_date_string.append(str(match.group(2)))

        # the rest of the data is in a comma separated string, so...
        data = (match.group(3)).split(',')

        # serial number, phase and burst number
        self.data.serial_number.append(int(data[0]))
        self.data.phase.append(int(data[1]))
        self.data.burst_number.append(int(data[2]))

        # number of frequencies and bins per profile
        nfreq = int(data[3])
        strt = 4
        stop = strt + nfreq
        nbins = map(int, data[strt:stop])
        self.data.number_bins.append(nbins)

        # minimum values per frequency
        strt = stop
        stop = strt + nfreq
        self.data.minimum_values.append(map(int, data[strt:stop]))

        # tilts, battery and temperature (no pressure sensor)
        strt = stop
        self.data.burst_date_string.append(str(data[strt]))
        self.data.tilts.append(map(float, data[strt+1:strt+3]))
        self.data.battery_voltage.append(float(data[strt+3]))
        self.data.temperature.append(float(data[strt+4]))

        # frequency #1
        strt += 7
        freq = [int(data[strt])]
        self.data.profiles_freq1.append(map(int, data[strt+1:strt+1+nbins[0]]))

        # frequency #2
        if nfreq >= 2:
            strt += 2 + nbins[0]
            freq.append(int(data[strt]))
            self.data.profiles_freq2.append(map(int, data[strt+1:strt+1+nbins[1]]))

        # frequency #3
        if nfreq >= 3:
            strt += 2 + nbins[1]
            freq.append(int(data[strt]))
            self.data.profiles_freq3.append(map(int, data[strt+1:strt+1+nbins[2]]))

        # frequency #4
        if nfreq == 4:
            strt += 2 + nbins[2]
            freq.append(int(data[strt]))
            self.data.profiles_freq4.append(map(int, data[strt+1:strt+1+nbins[3]]))

        self.data.frequencies.append(freq)

if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for ZPLSC
    zplsc = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    zplsc.load_ascii()
    zplsc.parse_data()

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, zplsc.data.toDict())

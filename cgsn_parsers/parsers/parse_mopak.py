#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package parsers.parse_mopak
@file parsers/parse_mopak.py
@author Christopher Wingard
@brief Parses MOPAK  data logged by the custom built WHOI data loggers.
'''
import os
import re
import scipy.io as sio

from struct import Struct

# Import common utilites and base classes
from common import ParameterNames, Parser
from common import logfilename_to_epoch, inputs, LOGFILENAME_TIMESTAMP

# Regex pattern for a binary MOPAK (Microstrain 3DM-GX3-25) data packet;
PATTERN = b'(\xCB)([\x00-\xff]{42})'
REGEX = re.compile(PATTERN, re.DOTALL)

# Struct class object for the MOPAK binary data byte streams
MOPAK = Struct('>B9fIH')


class ParameterNames(ParameterNames):
    '''
    Extend the parameter names with parameters for the mopak (time is already
    declared in the base class).
    '''
    ParameterNames.parameters.extend([
        'acceleration_x',
        'acceleration_y',
        'acceleration_z',
        'angular_rate_x',
        'angular_rate_y',
        'angular_rate_z',
        'magnetometer_x',
        'magnetometer_y',
        'magnetometer_z',
        'timer'
    ])


class Parser(Parser):
    '''
    A Parser subclass that calls the Parser base class, adds the mopak specific
    methods to parse the data, and extracts the mopak data records from the DCL
    daily log files.
    '''
    def parse_data(self):
        '''
        Iterate through packets to parse the data into a pre-defined
        dictionary object created using the Bunch class.
        '''
        # determine epoch start time from characters in the log file name; the
        # date_time in this filename marks when the file was created...that's
        # actually kind of a problem for the inshore surface moorings, but it
        # can be corrected elsewhere.
        dt_regex = re.compile(LOGFILENAME_TIMESTAMP, re.DOTALL)
        match = dt_regex.search(self.infile)
        epts = logfilename_to_epoch(match.group(1))

        # the wake time of the unit (time before first packet is output)
        # is a function of the filtering width. we use a width of 100, to
        # output 10 Hz data. adding the wake time to the file start time,
        # should provide a better measure of when the data was collected.
        twake = 0.053 + (2. * 100. / 1000.)
        epts = epts + twake

        # find all the mopak data packets
        record_marker = [m.start() for m in REGEX.finditer(self.raw)]

        # if we have mopak records, then parse them one-by-one
        while record_marker:
            # set the start and stop points of the packet
            start = record_marker[0]
            stop = start + 43

            # parse the packet
            self._build_parsed_values(self.raw[start:stop], epts)
            
            # grab the next packet
            record_marker.pop(0)

    def _build_parsed_values(self, packet, epts):
        '''
        Extract the data from the relevant byte groupings and assign to
        elements of the data dictionary.
        '''
        # unpack the packet
        (_, accx, accy, accz, angx, angy, angz,
         magx, magy, magz, timer, check) = MOPAK.unpack(packet)

        # Check the size
        if len(packet) != 43:
            print("Incorrect packet size")
            print("mopak data packet failed to parse")
            return False

        # Check the checksums
        if check != self._calc_checksum(packet[:-2]):
            print("Checksum mismatch")
            return False

        # assign the MOPAK header data to the named parameters
        self.data.time.append(epts + (timer / 62500.))
        self.data.acceleration_x.append(accx)
        self.data.acceleration_y.append(accy)
        self.data.acceleration_z.append(accz)
        self.data.angular_rate_x.append(angx)
        self.data.angular_rate_y.append(angy)
        self.data.angular_rate_z.append(angz)
        self.data.magnetometer_x.append(magx)
        self.data.magnetometer_y.append(magz)
        self.data.magnetometer_z.append(magz)
        self.data.timer.append(timer / 62500.)
        return True

    def _calc_checksum(self, packet):
        # add integer representations of the 1-byte characters
        checksum = 0
        for byte in packet:
            checksum += ord(byte)

        # reduce checksum to 2 significant bytes
        checksum = checksum & 65535
        return checksum

if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for vel3d
    mopak = Parser(infile)

    # load the data into a buffered object and parse the data into dictionaries
    mopak.load_binary()
    mopak.parse_data()

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, mopak.data.toDict())

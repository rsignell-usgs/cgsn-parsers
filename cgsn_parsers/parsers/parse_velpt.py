#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package parsers.parse_velpt
@file parsers/parse_velpt.py
@author Christopher Wingard
@brief Parses VELPT binary data files logged external to the unit.
'''
__author__ = 'Christopher Wingard'
__license__ = 'Apache 2.0'

import os
import re
import scipy.io as sio

from bunch import Bunch
from calendar import timegm
from datetime import datetime
from pytz import timezone
from struct import unpack

# Import common utilites and base classes
from common import Parser, inputs

# Regex pattern for a binary VELPT (ac-s) data packet;
# the number of wavelengths must be determined before the regex is compiled.
VELOCITY_REGEX = b'(\xa5\x01)([\x00-\xff]{40})'     # velocity data packets
VELOCITY_MATCHER = re.compile(VELOCITY_REGEX, re.DOTALL)
HEADER_REGEX = b'(\xa5\x06)([\x00-\xff]{34})'       # header data packets
HEADER_MATCHER = re.compile(HEADER_REGEX, re.DOTALL)
DIAGNOSTICS_REGEX = b'(\xa5\x80)([\x00-\xff]{40})'  # diagnostics data packets
DIAGNOSTICS_MATCHER = re.compile(DIAGNOSTICS_REGEX, re.DOTALL)


class ParameterNames(object):
    '''
    Nortek Aquadopp binary data file contents
    '''
    def __init__(self):
        # Diagnostics Header Data
        self._header = [
            'time',
            'records_to_follow',
            'cell_number',
            'noise_amplitudes',
            'processing_magnitudes',
            'beam_distances'
        ]

        # Velocity and Diagnostics Packet Data
        self._packet = [
            'time',
            'date_time_array',
            'error_code',
            'battery_voltage',
            'speed_of_sound',
            'heading',
            'pitch',
            'roll',
            'pressure',
            'status_code',
            'temperature',
            'velocity_east',
            'velocity_north',
            'velocity_vertical',
            'amplitude_beam1',
            'amplitude_beam2',
            'amplitude_beam3'
        ]

    # Create the initial dictionary object from the velocity, diagnostics and
    # diagnostics data header data types.
    def create_dict(self):
        '''
        Create a Bunch class object to store the parameter names for the Nortek
        Aquadopp (aka VELPT), with the data organized hierarchically by the
        data type.
        '''
        bunch = Bunch()
        bunch.header = Bunch()
        bunch.diagnostics = Bunch()
        bunch.velocity = Bunch()

        for name in self._header:
            bunch.header[name] = []

        for name in self._packet:
            bunch.diagnostics[name] = []
            bunch.velocity[name] = []

        return bunch


class Parser(Parser):
    """
    A Parser subclass that calls the Parser base class, adds the VELPT specific
    methods to parse the data, and extracts the VELPT data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        # set the infile name and path
        self.infile = infile

        # initialize the data dictionary using the names defined above
        data = ParameterNames()
        self.data = data.create_dict()
        self.raw = None

    def parse_velocity(self):
        '''
        Iterate through the record markers (defined via the regex expression
        above) in the data object, and parse the data file into a pre-defined
        dictionary object created using the Bunch class.
        '''
        # find all the velocity data packets
        record_marker = [m.start() for m in VELOCITY_MATCHER.finditer(self.raw)]

        # if we have velocity records, then parse them one-by-one
        while record_marker:
            # set the start and stop points of the velocity packet
            start = record_marker[0]
            stop = start + 42

            # parse the velocity packet
            self._build_parsed_velocity(self.raw[start:stop])

            # advance to the next record
            record_marker.pop(0)

    def parse_diagnostics(self):
        '''
        Iterate through the record markers (defined via the regex expression
        above) in the data object, and parse the data file into a pre-defined
        dictionary object created using the Bunch class.
        '''
        # find all the diagnostics data header packets
        header_marker = [m.start() for m in HEADER_MATCHER.finditer(self.raw)]
        diagnostics_marker = [m.start() for m in DIAGNOSTICS_MATCHER.finditer(self.raw)]

        # if we have header records, then parse them one-by-one
        while header_marker:
            # set the start and stop points of the header packet
            start = header_marker[0]
            stop = start + 36

            # determine if this is the last packet
            if len(header_marker) == 1:
                last = len(self.raw)
            else:
                last = header_marker[1]

            # parse the header packet and set the counter
            self._build_parsed_header(self.raw[start:stop])
            cnt = 0

            # the header packet precedes the diagnostic packets, starting with
            # the first header packet, find the first diagnostic packet...
            while diagnostics_marker:
                # make sure the first packet comes after the first header
                if diagnostics_marker[0] < start:
                    diagnostics_marker.pop(0)
                    continue
                # make sure we don't process past the next header.
                if diagnostics_marker[0] > last:
                    break

                # set the start and stop points and process the packet
                dstrt = diagnostics_marker[0]
                dstop = dstrt + 42
                self._build_parsed_diagnostics(self.raw[dstrt:dstop])

                # advance to the next diagnostics record
                diagnostics_marker.pop(0)

                # check the counter, if this is the first packet, use its time
                # record for the header.
                cnt += 1
                if cnt == 1:
                    self.data.header.time.append(self.data.diagnostics.time[-1])

            # advance to the next header record
            header_marker.pop(0)

    def _build_parsed_diagnostics(self, diagnostics):
        '''
        Extract the data from the relevant byte groupings and assign to
        elements of the data dictionary.
        '''
        # parse the diagnostics packet
        data = self._parse_aquadopp_packet(diagnostics)
        if not data:
            print "diagnostics data packet failed to parse"
            return

        # Assign the VELPT data to the named parameters
        self.data.diagnostics.time.append(data[0])
        self.data.diagnostics.date_time_array.append(data[1])
        self.data.diagnostics.error_code.append(data[2])
        self.data.diagnostics.battery_voltage.append(data[3] * 0.1)
        self.data.diagnostics.speed_of_sound.append(data[4] * 0.1)
        self.data.diagnostics.heading.append(data[5] * 0.1)
        self.data.diagnostics.pitch.append(data[6] * 0.1)
        self.data.diagnostics.roll.append(data[7] * 0.1)
        self.data.diagnostics.pressure.append(data[8])
        self.data.diagnostics.status_code.append(data[9])
        self.data.diagnostics.temperature.append(data[10] * 0.01)
        self.data.diagnostics.velocity_east.append(data[11])
        self.data.diagnostics.velocity_north.append(data[12])
        self.data.diagnostics.velocity_vertical.append(data[13])
        self.data.diagnostics.amplitude_beam1.append(data[14])
        self.data.diagnostics.amplitude_beam2.append(data[15])
        self.data.diagnostics.amplitude_beam3.append(data[16])

    def _build_parsed_header(self, header):
        '''
        Extract the data from the relevant byte groupings and assign to
        elements of the data dictionary.
        '''
        # unpack the velocity packet
        (_, _, size, records, cell, noise1, noise2, noise3, noise4,
         proc1, proc2, proc3, proc4, dist1, dist2, dist3, dist4,
         _, _, _, _, _, _, check) = unpack('<2B3H4B4H4H6bH', header)

        # Check the size, some packets report erroneous sizes for some reason.
        if size * 2 != 36:
            print "Incorrect packet size"
            print "header data packet failed to parse"
            return

        # Check the checksums...
        if check != self._calc_checksum(size * 2, header):
            print "Checksum mismatch"
            return

        self.data.header.records_to_follow.append(records)
        self.data.header.cell_number.append(cell)
        self.data.header.noise_amplitudes.append([noise1, noise2, noise3, noise4])
        self.data.header.processing_magnitudes.append([proc1, proc2, proc3, proc4])
        self.data.header.beam_distances.append([dist1, dist2, dist3, dist4])

    def _build_parsed_velocity(self, velocity):
        '''
        Extract the data from the relevant byte groupings and assign to
        elements of the data dictionary.
        '''
        # parse the velocity packet
        data = self._parse_aquadopp_packet(velocity)
        if not data:
            print "Velocity data packet failed to parse"
            return

        # Assign the VELPT data to the named parameters
        self.data.velocity.time.append(data[0])
        self.data.velocity.date_time_array.append(data[1])
        self.data.velocity.error_code.append(data[2])
        self.data.velocity.battery_voltage.append(data[3] * 0.1)
        self.data.velocity.speed_of_sound.append(data[4] * 0.1)
        self.data.velocity.heading.append(data[5] * 0.1)
        self.data.velocity.pitch.append(data[6] * 0.1)
        self.data.velocity.roll.append(data[7] * 0.1)
        self.data.velocity.pressure.append(data[8])
        self.data.velocity.status_code.append(data[9])
        self.data.velocity.temperature.append(data[10] * 0.01)
        self.data.velocity.velocity_east.append(data[11])
        self.data.velocity.velocity_north.append(data[12])
        self.data.velocity.velocity_vertical.append(data[13])
        self.data.velocity.amplitude_beam1.append(data[14])
        self.data.velocity.amplitude_beam2.append(data[15])
        self.data.velocity.amplitude_beam3.append(data[16])

    def _parse_aquadopp_packet(self, packet):
        '''
        Unpack the Aquadopp velocity data packet. Same structure is used for
        both the velocity (0xA501) and diagnostics (0xA580) packets.
        '''
        # unpack the velocity packet
        (_, _, size, minute, second, day, hour, year, month,
         error, _, battery, speed, heading, pitch, roll, pMSB,
         status, pLSW, temp, vel1, vel2, vel3, amp1, amp2, amp3, _,
         check) = unpack('<2BH6B2h2H3hBbHh3h3BbH', packet)

        # Check the size, some packets report erroneous sizes for some reason.
        if size * 2 != 42:
            print "Incorrect packet size"
            return []

        # Check the checksums...
        if check != self._calc_checksum(size * 2, packet):
            print "Checksum mismatch"
            return []

        # calculate an epoch timestamp from the time array, first converting
        # the binary coded decimal (BCD) date values to integers
        year = self._convert_bcd(year)
        if year >= 90:
            year += 1900
        else:
            year += 2000
        month = self._convert_bcd(month)
        day = self._convert_bcd(day)
        hour = self._convert_bcd(hour)
        minute = self._convert_bcd(minute)
        second = self._convert_bcd(second)
        utc = datetime(year, month, day, hour, minute, second, tzinfo=timezone('UTC'))
        epts = timegm(utc.timetuple())
        date_array = [year, month, day, hour, minute, second]

        # calculate pressure
        dbar = (65536 * pMSB + pLSW) * 0.001

        # return the results
        return [epts, date_array, error, battery, speed, heading,
                pitch, roll, dbar, status, temp, vel1, vel2, vel3,
                amp1, amp2, amp3]

    def _calc_checksum(self, length, record):
        """
        Calculate the checksum for the data record
        """
        # The base value of the checksum, given in the manual
        # base = int('0xb58c', 16) = 46476
        base = 46476

        # Add up the uint16 integers in the packet, minus the checksum
        for x in range(0, length-2, 2):
            base += unpack('<H', record[x:x+2])[0]

        # Modulo 65536 is applied to the checksum to keep it a 16 bit value
        checksum = base % 65536
        return checksum

    def _convert_bcd(self, cBCD):
        '''
        Convert the BCD values to integers

        From the Nortek System Integrator Manual, March 2014
        '''
        cBCD = min([cBCD, 0x99])
        c = (cBCD & 0x0f)
        c += 10 * (cBCD >> 4)
        return c

if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for velpt
    velpt = Parser(infile)

    # load the data into a buffered object and parse the data into dictionaries
    velpt.load_binary()
    velpt.parse_velocity()
    velpt.parse_diagnostics()

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, velpt.data.toDict())

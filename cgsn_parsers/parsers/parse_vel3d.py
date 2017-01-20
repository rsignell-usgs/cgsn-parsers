#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.parsers.parse_vel3d
@file cgsn_parsers/parsers/parse_vel3d.py
@author Christopher Wingard
@brief Parses VEL3D binary data files logged external to the unit.
'''
import os
import re

from munch import Munch as Bunch
from calendar import timegm
from datetime import datetime
from pytz import timezone
from struct import unpack

# Import common utilites and base classes
from cgsn_parsers.parsers.common import ParserCommon, inputs

# Regex pattern for a binary VEL3D data packet;
VELOCITY_REGEX = b'(\xa5\x10)([\x00-\xff]{22})'     # velocity data packets
VELOCITY_MATCHER = re.compile(VELOCITY_REGEX, re.DOTALL)
SYSTEM_REGEX = b'(\xa5\x11)([\x00-\xff]{26})'  # system data packets
SYSTEM_MATCHER = re.compile(SYSTEM_REGEX, re.DOTALL)
HEADER_REGEX = b'(\xa5\x12)([\x00-\xff]{40})'       # header data packets
HEADER_MATCHER = re.compile(HEADER_REGEX, re.DOTALL)


class ParameterNames(object):
    '''
    Nortek Vector binary data file contents
    '''
    def __init__(self):
        # Vector Velocity Data Header
        self._header = [
            'time',
            'date_time_array',
            'records_to_follow',
            'noise_amplitudes',
            'noise_correlations'
        ]

        # Vector System Data
        self._system = [
            'time',
            'date_time_array',
            'battery_voltage',
            'speed_of_sound',
            'heading',
            'pitch',
            'roll',
            'temperature',
            'error_code',
            'status_code'
        ]

        # Vector Velocity Data
        self._velocity = [
            'time',
            'ensemble_counter',
            'pressure',
            'velocity_east',
            'velocity_north',
            'velocity_vertical',
            'amplitudes',
            'correlations'
        ]

    # Create the initial dictionary object from the velocity, system and
    # header data types.
    def create_dict(self):
        '''
        Create a Bunch class object to store the parameter names for the Nortek
        Vector (aka VEL3D), with the data organized hierarchically by the
        data type.
        '''
        bunch = Bunch()
        bunch.header = Bunch()
        bunch.system = Bunch()
        bunch.velocity = Bunch()

        for name in self._header:
            bunch.header[name] = []

        for name in self._system:
            bunch.system[name] = []

        for name in self._velocity:
            bunch.velocity[name] = []

        return bunch


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the VEL3D specific
    methods to parse the data, and extracts the VEL3D data records from the DCL
    hourly log files.
    """
    def __init__(self, infile, sample_rate):
        # set the infile name and path
        self.infile = infile
        self.sample_rate = sample_rate

        # initialize the data dictionary using the names defined above
        data = ParameterNames()
        self.data = data.create_dict()
        self.raw = None

    def parse_header(self):
        '''
        Iterate through the record markers (defined via the regex expression
        above) in the data object, and parse the data file into a pre-defined
        dictionary object created using the Bunch class.
        '''
        # find all the header data packets
        record_marker = [m.start() for m in HEADER_MATCHER.finditer(self.raw)]

        # if we have header records, then parse them one-by-one
        while record_marker:
            # set the start and stop points of the header packet
            start = record_marker[0]
            stop = start + 42

            # parse the header packet
            self._build_parsed_header(self.raw[start:stop])

            # advance to the next record
            record_marker.pop(0)

    def parse_velocity(self):
        '''
        Iterate through the record markers (defined via the regex expression
        above) in the data object, and parse the data file into a pre-defined
        dictionary object created using the Bunch class.
        '''
        # find all the velocity and system data packets
        system_marker = [m.start() for m in SYSTEM_MATCHER.finditer(self.raw)]
        velocity_marker = [m.start() for m in VELOCITY_MATCHER.finditer(self.raw)]

        # if we have system records, then parse them one-by-one
        while system_marker:
            # set the start and stop points of the system packet
            start = system_marker[0]
            stop = start + 28

            # determine if this is the last system packet
            if len(system_marker) == 1:
                last = len(self.raw)
            else:
                last = system_marker[1]

            # parse the system packet and set the counter
            system = self._build_parsed_system(self.raw[start:stop])
            time = self.data.system['time'][-1]
            cnt = 0

            # the system packet precedes the velocity packets, starting with
            # the first successfully parsed system packet, find the
            # corresponding velocity packets
            if system:
                while velocity_marker:
                    # make sure the first velocity packet comes after the first
                    # system packet
                    if velocity_marker[0] < start:
                        velocity_marker.pop(0)
                        continue
                    # make sure we don't process past the next system.
                    if velocity_marker[0] > last:
                        break

                    # set the start and stop points and process the packet
                    vstrt = velocity_marker[0]
                    vstop = vstrt + 24
                    self._build_parsed_velocity(self.raw[vstrt:vstop])

                    # use the counter and the time of the system packet to
                    # generate a time record for the velocity packets.
                    vtime = float(time) + (float(cnt) * 1/self.sample_rate)
                    self.data.velocity.time.append(vtime)

                    # advance to the next velocity record
                    velocity_marker.pop(0)
                    cnt += 1

            # advance to the next system record
            system_marker.pop(0)

    def _build_parsed_header(self, header):
        '''
        Extract the data from the relevant byte groupings and assign to
        elements of the data dictionary.
        '''
        # unpack the header packet
        (_, _, size, minute, second, day, hour, year, month, records,
         noise1, noise2, noise3, _, corr1, corr2, corr3,
         _, _, check) = unpack('<2BH6BH4B4B20sH', header)

        # Check the size, some packets report erroneous sizes for some reason.
        if size * 2 != 42:
            print("Incorrect packet size")
            print("header data packet failed to parse")
            return False

        # Check the checksums.
        if check != self._calc_checksum(size * 2, header):
            print("Checksum mismatch")
            return False

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

        # assign the VEL3D header data to the named parameters
        self.data.header.time.append(epts)
        self.data.header.date_time_array.append(date_array)
        self.data.header.records_to_follow.append(records)
        self.data.header.noise_amplitudes.append([noise1, noise2, noise3])
        self.data.header.noise_correlations.append([corr1, corr2, corr3])
        return True

    def _build_parsed_system(self, system):
        '''
        Extract the data from the relevant byte groupings and assign to
        elements of the data dictionary.
        '''
        # unpack the system packet
        (_, _, size, minute, second, day, hour, year, month,
         battery, speed, heading, pitch, roll, temp, error, status,
         _, check) = unpack('<2BH6B2H4h2b2H', system)

        # Check the size, some packets report erroneous sizes for some reason.
        if size * 2 != 28:
            print("Incorrect packet size")
            return False

        # Check the checksums...
        if check != self._calc_checksum(size * 2, system):
            print("Checksum mismatch")
            return False

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

        # Assign the VEL3D system data to the named parameters
        self.data.system.time.append(epts)
        self.data.system.date_time_array.append(date_array)
        self.data.system.battery_voltage.append(battery * 0.1)
        self.data.system.speed_of_sound.append(speed * 0.1)
        self.data.system.heading.append(heading * 0.1)
        self.data.system.pitch.append(pitch * 0.1)
        self.data.system.roll.append(roll * 0.1)
        self.data.system.temperature.append(temp * 0.01)
        self.data.system.error_code.append(error)
        self.data.system.status_code.append(status)
        return True

    def _build_parsed_velocity(self, velocity):
        '''
        Extract the data from the relevant byte groupings and assign to
        elements of the data dictionary.
        '''
        # parse the velocity packet
        (_, _, _, count, pMSB, _, pLSW, _, vel1, vel2, vel3, amp1, amp2, amp3,
         cor1, cor2, cor3, check) = unpack('<6B2H3h6BH', velocity)

        # Check the size, some packets report erroneous sizes for some reason.
        size = len(velocity)
        if size != 24:
            print("Incorrect packet size")
            return False

        # Check the checksums...
        if check != self._calc_checksum(size, velocity):
            print("Checksum mismatch")
            return False

        # calculate the pressure value
        dbar = (65536 * pMSB + pLSW) * 0.001

        # Assign the VEL3D velocity data to the named parameters
        self.data.velocity.ensemble_counter.append(count)
        self.data.velocity.pressure.append(dbar)
        self.data.velocity.velocity_east.append(vel1)
        self.data.velocity.velocity_north.append(vel2)
        self.data.velocity.velocity_vertical.append(vel3)
        self.data.velocity.amplitudes.append([amp1, amp2, amp3])
        self.data.velocity.correlations.append([cor1, cor2, cor3])
        return True

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
    sample_rate = args.switch

    # initialize the Parser object for vel3d
    vel3d = Parser(infile, sample_rate)

    # load the data into a buffered object and parse the data into dictionaries
    vel3d.load_binary()
    vel3d.parse_header()
    vel3d.parse_velocity()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(vel3d.data.toJSON())

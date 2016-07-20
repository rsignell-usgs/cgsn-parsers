#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.parsers.parse_optaa
@file cgsn_parsers/parsers/parse_optaa.py
@author Russell Desiderio
@brief Parses OPTAA data logged by the custom built WHOI data loggers.
'''
import os
import re
import scipy.io as sio
from struct import unpack

# Import common utilites and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import logfilename_to_epoch, inputs, LOGFILENAME_TIMESTAMP

# Regex pattern for a binary OPTAA (ac-s) data packet;
# the number of wavelengths must be determined before the regex is compiled.
MARKER = b'(\xff\x00\xff\x00)'
#                               numbering reflects 'regex.findall' indexing;
#                               add 1 for 'regex.search' group indexing
PATTERN = (
    MARKER +                    # 00 registration bytes signaling start of packet
    '(..)' +                    # 01 record length of packet excluding checksum and pad
    '(.)' +                     # 02 packet type; 03 and above designates ac-s meter
    '(.)' +                     # 03 reserved; \x01
    '(.)' +                     # 04 meter type; 53 indicates ac-s
    '(.)' +                     # 05 1st byte of 3-byte serial number; always \x00
    '(..)' +                    # 06 serial number
    '(..)' +                    # 07 "a" reference dark counts
    '(..)' +                    # 08 pressure counts
    '(..)' +                    # 09 "a" signal dark counts
    '(..)' +                    # 10 raw external temperature counts
    '(..)' +                    # 11 raw internal temperature counts
    '(..)' +                    # 12 "c" reference dark counts
    '(..)' +                    # 13 "c" signal dark counts
    '(....)' +                  # 14 time in milliseconds since power up
    '(.)' +                     # 15 reserved; \x01
    '(.)' +                     # 16 number of wavelengths (nwave)
    '(.' + '{var}' + ')' +      # 17 'var' = str(2 [bytes] * 4 [channels] * nwave)
    '(..)' +                    # 18 checksum
    '(.)'                       # 19 pad byte; always \x00
)

_parameter_names_optaa = [
        'serial_number',
        'a_reference_dark_counts',
        'pressure_counts',
        'a_signal_dark_counts',
        'raw_external_temperature_counts',
        'raw_internal_temperature_counts',
        'c_reference_dark_counts',
        'c_signal_dark_counts',
        'time_msec_since_power_up',
        'number_of_wavelengths',
        'cref_raw_counts',
        'aref_raw_counts',
        'csig_raw_counts',
        'asig_raw_counts'
    ]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the optaa specific
    methods to parse the data, and extracts the optaa data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_optaa)

    def parse_data(self):
        # parse the first data packet to find the packet length and number of
        # output wavelengths for this particular optaa (ac-s). the first good
        # data packet is delimited by marker bytes.
        pattern0 = PATTERN + MARKER
        # change the regex pattern0 to match a variable number of bytes
        # in between the marker endpoints
        pattern0 = pattern0.replace('{var}', '*?')
        regex0 = re.compile(pattern0, re.DOTALL)
        packet0 = regex0.search(self.raw)

        # coarse check of the packet integrity
        #   the data packet consists of:
        #      record length = 32 bytes + 2 [bytes] * 4 [optical channels] * nwave
        #      (a checksum of 2 bytes plus a pad byte are not included in record length)
        record_length = unpack('>H', packet0.group(2))[0]
        nwave = unpack('B', packet0.group(17))[0]
        if nwave != (record_length - 32) / 8:
            raise Exception('optaa data packet: record length does not match nwave.')

        # determine epoch starttime from characters in inlogfilename; the date_time in
        # this filename marks when the file was created.
        dt_regex = re.compile(LOGFILENAME_TIMESTAMP, re.DOTALL)
        match = dt_regex.search(self.infile)
        epts = logfilename_to_epoch(match.group(1))

        # the time record in the ac-s binary data is time_msec_since_power_up; the utc time
        # for a given data packet is therefore constructed as (time at filename creation) +
        # (time_msec_since_power_up[given packet] - time_msec_since_power_up[0])/1000.0
        #
        # subtract first packet's acs timestamp from time at filename creation.
        time0 = epts - unpack('>I', packet0.group(15))[0]/1000.0

        # construct packet pattern for an optaa with nwave output wavelengths
        packet_pattern = PATTERN.replace('var', str(8 * nwave))
        regex_pp = re.compile(packet_pattern, re.DOTALL)
        packets = regex_pp.findall(self.raw)

        '''
        Iterate through packets to parse the data into a pre-defined
        dictionary object created using the Bunch class.
        '''
        for packet in packets:
            if self.acs_checksum_agreement(packet):
                self._build_parsed_values(packet, nwave, time0)

    def _build_parsed_values(self, match, nwave, time0):
        """
        Extract the data from the relevant byte groupings and assign to elements
        of the data dictionary.
        """
        # time0 is already an epoch timestamp (seconds since 1970-01-01) which
        # was calculated as the datetime parsed from the infilename minus the
        # time_msec_since_power_up value in seconds from the first ac-s data packet.
        time_msec_since_power_up = unpack('>I', match[14])[0]
        self.data.time.append(time0 + time_msec_since_power_up/1000.0)

        # parse the optical data from the 4 optical channels: the data ordering is
        #    cref, aref, csig, asig for wavelength 1;
        #    cref, aref, csig, asig for wavelength 2;
        #    ...   ...   ...   ...
        #    cref, aref, csig, asig for wavelength nwave.
        optical_data = unpack(('>' + 'H'*4*nwave), match[17])

        # Assign the OPTAA data to the named parameters
        self.data.serial_number.append(str(unpack('>H', match[6])[0]))
        self.data.a_reference_dark_counts.append(unpack('>H', match[7])[0])
        self.data.pressure_counts.append(unpack('>H', match[8])[0])
        self.data.a_signal_dark_counts.append(unpack('>H', match[9])[0])
        self.data.raw_external_temperature_counts.append(unpack('>H', match[10])[0])
        self.data.raw_internal_temperature_counts.append(unpack('>H', match[11])[0])
        self.data.c_reference_dark_counts.append(unpack('>H', match[12])[0])
        self.data.c_signal_dark_counts.append(unpack('>H', match[13])[0])
        self.data.time_msec_since_power_up.append(time_msec_since_power_up)
        self.data.number_of_wavelengths.append(unpack('B', match[16])[0])
        self.data.cref_raw_counts.append(optical_data[0::4])
        self.data.aref_raw_counts.append(optical_data[1::4])
        self.data.csig_raw_counts.append(optical_data[2::4])
        self.data.asig_raw_counts.append(optical_data[3::4])

    def acs_checksum_agreement(self, packet):
        # as currently coded, packet is a re object, not a string of bytes
        # reconstruct packet excluding 2 checksum bytes and 1 pad byte
        packet_lesslast3bytes = ''.join(packet[0:-2])
        # add integer representations of the 1-byte characters
        checksum = 0
        for byte in packet_lesslast3bytes:
            checksum += ord(byte)
        # reduce checksum to 2 significant bytes
        checksum = checksum & 65535  # or np.mod(checksum, 65536) could be used

        return checksum == unpack('>H', packet[-2])[0]

if __name__ == '__main__':

    # usage: parse_optaa.py -i INFILE -o OUTFILE

    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for optaa
    optaa = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    optaa.load_binary()
    optaa.parse_data()

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, optaa.data.toDict())

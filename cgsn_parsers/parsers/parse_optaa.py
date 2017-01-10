#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.parsers.parse_optaa
@file cgsn_parsers/parsers/parse_optaa.py
@author Russell Desiderio with edits from Christopher Wingard
@brief Parses OPTAA data logged by the custom built WHOI data loggers.
'''
import os
import re
from struct import unpack

# Import common utilites and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import logfilename_to_epoch, inputs, LOGFILENAME_TIMESTAMP

# Regex pattern for the start of a binary OPTAA (ac-s) data packet
PATTERN = b'(\xff\x00\xff\x00)'
REGEX = re.compile(PATTERN, re.DOTALL)

# Each optaa packet consists of: 
#    4 registration bytes signaling start of packet
#    2 bytes for packet record length (excludes 2 byte checksum and padding byte)
#    1 byte for packet type; 03 and above designates ac-s meter
#    1 byte reserved
#    1 byte for meter type; 53 indicates ac-s
#    3 bytes for the serial number
#    2 bytes for "a" reference dark counts
#    2 bytes for pressure counts
#    2 bytes for "a" signal dark counts
#    2 bytes for raw external temperature counts
#    2 bytes for raw internal temperature counts
#    2 bytes for "c" reference dark counts
#    2 bytes for "c" signal dark counts
#    4 bytes for time in milliseconds since power up
#    1 byte reserved
#    1 byte for the number of wavelengths
#    N bytes where there are 2 bytes * number of wavelengths * 4 optical channels
#       ordering of the optical channels is:
#           cref, aref, csig, asig for wavelength 1;
#           cref, aref, csig, asig for wavelength 2;
#           ...   ...   ...   ...
#           cref, aref, csig, asig for wavelength N.
#    2 bytes for the checksum
#    1 byte padding

_parameter_names_optaa = [
        'serial_number',
        'a_reference_dark',
        'pressure_raw',
        'a_signal_dark',
        'external_temp_raw',
        'internal_temp_raw',
        'c_reference_dark',
        'c_signal_dark',
        'elapsed_run_time',
        'num_wavelengths',
        'c_reference_raw',
        'a_reference_raw',
        'c_signal_raw',
        'a_signal_raw'
    ]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the optaa specific
    methods to parse the data, and extracts the optaa data records from the DCL
    hourly log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_optaa)

    def parse_data(self):
        # Determine epoch start time from characters in the log file name; the
        # date_time in this filename marks when the file was created. This is
        # actually kind of a problem, because it is not accurate (especially
        # for the inshore surface moorings), but it can be corrected elsewhere.
        dt_regex = re.compile(LOGFILENAME_TIMESTAMP, re.DOTALL)
        match = dt_regex.search(self.infile)
        epts = logfilename_to_epoch(match.group(1))
        
        # find all the optaa data packets
        record_marker = [m.start() for m in REGEX.finditer(self.raw)]
        record_length = 0   # default record length set to 0, updated with first packet
        
        # if we have optaa packets, then parse them one-by-one
        while record_marker:
            # set the start point of the packet
            start = record_marker[0]
            if record_length == 0:      # this is the first packet, set defaults
                # set the record length for the packets, as well as the number 
                # of wavelengths and time zero for the file.
                record_length = unpack('>H', self.raw[start+4:start+6])[0]
                nwave = unpack('>B', self.raw[start+31])[0]
                if nwave != (record_length - 32) / 8:
                    raise Exception('optaa data packet: record length does not match number of wavelengths.')

                # mark the first packet's elapsed_run_time 
                time_zero = unpack('>I', self.raw[start+26:start+30])[0]

            # now set the stop point of the packet
            stop = start + record_length + 3
            
            # parse the packet
            if self._acs_checksum_agreement(self.raw[start:stop]):
                self._build_parsed_values(self.raw[start:stop], nwave, epts, time_zero)

            # pop to the next packet
            record_marker.pop(0)

    def _build_parsed_values(self, packet, nwave, epts, time_zero):
        """
        Extract data from the relevant byte groupings and assign to elements
        of the data dictionary.
        """
        # Assign the optaa data to the named parameters
        self.data.serial_number.append(str(unpack('>I', '\x00' + packet[9:12])[0]))
        self.data.a_reference_dark.append(unpack('>H', packet[12:14])[0])
        self.data.pressure_raw.append(unpack('>H', packet[14:16])[0])
        self.data.a_signal_dark.append(unpack('>H', packet[16:18])[0])
        self.data.external_temp_raw.append(unpack('>H', packet[18:20])[0])
        self.data.internal_temp_raw.append(unpack('>H', packet[20:22])[0])
        self.data.c_reference_dark.append(unpack('>H', packet[22:24])[0])
        self.data.c_signal_dark.append(unpack('>H', packet[24:26])[0])
        elapsed_run_time = unpack('>I',packet[26:30])[0]
        self.data.elapsed_run_time.append(elapsed_run_time)
        time = epts + (elapsed_run_time - time_zero) / 1000.
        self.data.time.append(time)
        self.data.num_wavelengths.append(unpack('>B', packet[31])[0])
        optical_data = unpack(('>' +  str(4 * nwave) + 'H'), packet[32:32 + 2 * 4 * nwave])
        self.data.c_reference_raw.append(optical_data[0::4])
        self.data.a_reference_raw.append(optical_data[1::4])
        self.data.c_signal_raw.append(optical_data[2::4])
        self.data.a_signal_raw.append(optical_data[3::4])
        
        # Note, record time is a function of the "absolute" file start time 
        # noted in the file name, used to calculate the epoch_time, and the
        # relative time recorded in the data in the elapsed_run_time (msec) 
        # parameter. The first elapsed_run_time measurement is used to set 
        # time_zero, from there:
        #   time = epoch_time - time_zero + elapsed_run_time

    def _acs_checksum_agreement(self, packet):
        # sum integer representations of the 1-byte characters
        checksum = 0
        for byte in packet[:-3]:
            checksum += ord(byte)
            
        # reduce checksum to 2 significant bytes
        checksum = checksum & 65535  # or np.mod(checksum, 65536) could be used

        # compare the calculated and reported checksum values
        return checksum == unpack('>H', packet[-3:-1])[0]

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

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(optaa.data.toJSON())

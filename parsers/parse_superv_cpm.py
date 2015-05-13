# -*- coding: utf-8 -*-
'''
@package parsers.parse_metbk
@file parsers/parse_metbk.py
@author Christopher Wingard
@brief Parses metbk data logged by the custom built WHOI data loggers.
'''
__author__ = 'Christopher Wingard'
__license__ = 'Apache 2.0'

import os
import re
import scipy.io as sio

# Import common utilites and base classes
from common import ParameterNames, Parser
from common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, INTEGER, NEWLINE


# Regex pattern for a line with a DCL time stamp, possible DCL status value and
# the 12 following met data values.
PATTERN = (
    DCL_TIMESTAMP + r'\s+superv\s+cpm:\s+' +
    FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + r'([0-9a-f]{8})\s+' +
    r't\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    r'h\s+' + FLOAT + r'\s+'
    r'p\s+' + FLOAT + r'\s+'
    r'gf\s+([0-9a-f]{1})\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    r'ld\s+([0-9a-f]{1})\s+' + INTEGER + r'\s+' + INTEGER + r'\s+' +
    r'hb\s+([0-1]+)\s+' + INTEGER + r'\s+' + INTEGER + r'\s+' +
    r'wake\s+([0-9]{2})\s+' +
    r'ir\s+([+-]?[0-1]+)\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + r'([0-2])\s+' +
    r'fwwf\s+([+-]?[0-1]+)\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + r'([0-3])\s+' +
    r'gps\s+([0-1]+)\s+' +
    r'sbd\s+([0-1]+)\s+([0-1]+)\s+' +
    r'pps\s+([0-1]+)\s+' +
    r'dcl\s+([0-9a-f]{2})\s+' +
    r'wtc\s+' + FLOAT + r'\s+' +
    r'wpc\s+' + INTEGER + r'\s+' +
    r'esw\s+([0-3]+)\s+' +
    r'dsl\s+([0-1]+)\s+' +
    r'([0-9a-f]{4})' + NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)


class ParameterNames(ParameterNames):
    '''
    Extend the parameter names with parameters for the METBK (time is already
    declared in the base class).
    '''
    ParameterNames.parameters.extend([
        'dcl_date_time_string',
        'main_voltage',
        'main_current',
        'backup_battery_voltage',
        'backup_battery_current',
        'error_flags',
        'temperature1',
        'temperature2',
        'humidity',
        'pressure',
        'ground_fault_enable',
        'ground_fault_sbd',
        'ground_fault_gps',
        'ground_fault_main',
        'ground_fault_9522_fw',
        'leak_detect_enable',
        'leak_detect_voltage1',
        'leak_detect_voltage2',
        'heartbeat_enable',
        'heartbeat_delta',
        'heartbeat_threshold',
        'wake_code',
        'iridium_power_state',
        'iridium_voltage',
        'iridium_current',
        'iridium_error_flag',
        'fwwf_power_state',
        'fwwf_voltage',
        'fwwf_current',
        'fwwf_power_flag',
        'gps_power_state',
        'sbd_power_state',
        'sbd_message_pending',
        'pps_source',
        'dcl_power_state',
        'wake_time_count',
        'wake_power_count',
        'esw_power_state',
        'dsl_power_state'
    ])


class Parser(Parser):
    """
    A Parser subclass that calls the Parser base class, adds the METBK specific
    methods to parse the data, and extracts the METBK data records from the DCL
    daily log files.
    """
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
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # Use the date_time_string to calculate an epoch timestamp (seconds since
        # 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.time.append(epts)
        self.data.dcl_date_time_string.append(str(match.group(1)))

        # Assign the remaining MET data to the named parameters
        self.data.main_voltage.append(float(match.group(2)))
        self.data.main_current.append(float(match.group(3)))
        self.data.backup_battery_voltage.append(float(match.group(4)))
        self.data.backup_battery_current.append(float(match.group(5)))
        self.data.error_flags.append(int(match.group(6), 16))

        self.data.temperature1.append(float(match.group(7)))
        self.data.temperature2.append(float(match.group(8)))

        self.data.humidity.append(float(match.group(9)))
        self.data.pressure.append(float(match.group(10)))

        self.data.ground_fault_enable.append(int(match.group(11), 16))
        self.data.ground_fault_sbd.append(float(match.group(12)))
        self.data.ground_fault_gps.append(float(match.group(13)))
        self.data.ground_fault_main.append(float(match.group(14)))
        self.data.ground_fault_9522_fw.append(float(match.group(15)))

        self.data.leak_detect_enable.append(int(match.group(16), 16))
        self.data.leak_detect_voltage1.append(int(match.group(17)))
        self.data.leak_detect_voltage2.append(int(match.group(18)))

        self.data.heartbeat_enable.append(int(match.group(19)))
        self.data.heartbeat_delta.append(int(match.group(20)))
        self.data.heartbeat_threshold.append(int(match.group(21)))

        self.data.wake_code.append(int(match.group(22)))

        self.data.iridium_power_state.append(int(match.group(23)))
        self.data.iridium_voltage.append(float(match.group(24)))
        self.data.iridium_current.append(float(match.group(25)))
        self.data.iridium_error_flag.append(int(match.group(26)))

        self.data.fwwf_power_state.append(int(match.group(27), 16))
        self.data.fwwf_voltage.append(float(match.group(28)))
        self.data.fwwf_current.append(float(match.group(29)))
        self.data.fwwf_power_flag.append(int(match.group(30)))

        self.data.gps_power_state.append(float(match.group(31)))

        self.data.sbd_power_state.append(float(match.group(32)))
        self.data.sbd_message_pending.append(float(match.group(33)))

        self.data.pps_source.append(float(match.group(34)))

        #dcl_flags = int(match.group(35), 16)
        #self.data.dcl_power_state.append([(dcl_flags >> i) & 1 for i in xrange(7)])
        self.data.dcl_power_state.append(int(match.group(35), 16))

        self.data.wake_time_count.append(float(match.group(36)))
        self.data.wake_power_count.append(int(match.group(37)))

        self.data.esw_power_state.append(int(match.group(38), 16))

        self.data.dsl_power_state.append(int(match.group(39)))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for METBK
    superv = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    superv.load_ascii()
    superv.parse_data()

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, superv.data.toDict())

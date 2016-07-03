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
from common import ParameterNames, ParserCommon
from common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, INTEGER, NEWLINE


# Regex pattern for a DCL supervisor log
PATTERN = (
    DCL_TIMESTAMP + r'\s+superv\s+dcl:\s+' +
    FLOAT + r'\s+' + FLOAT + r'\s+' + r'([0-9a-f]{8})\s+' +
    r't\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    r'h\s+' + FLOAT + r'\s+'
    r'p\s+' + FLOAT + r'\s+'
    r'gf\s+([0-9a-f]{1})\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    r'ld\s+([0-9a-f]{1})\s+' + INTEGER + r'\s+' + INTEGER + r'\s+' +
    r'p1\s+([0-1]+)\s+' + FLOAT + r'\s+' + FLOAT + r'\s+([0-4]+)\s+' +
    r'p2\s+([0-1]+)\s+' + FLOAT + r'\s+' + FLOAT + r'\s+([0-4]+)\s+' +
    r'p3\s+([0-1]+)\s+' + FLOAT + r'\s+' + FLOAT + r'\s+([0-4]+)\s+' +
    r'p4\s+([0-1]+)\s+' + FLOAT + r'\s+' + FLOAT + r'\s+([0-4]+)\s+' +
    r'p5\s+([0-1]+)\s+' + FLOAT + r'\s+' + FLOAT + r'\s+([0-4]+)\s+' +
    r'p6\s+([0-1]+)\s+' + FLOAT + r'\s+' + FLOAT + r'\s+([0-4]+)\s+' +
    r'p7\s+([0-1]+)\s+' + FLOAT + r'\s+' + FLOAT + r'\s+([0-4]+)\s+' +
    r'p8\s+([0-1]+)\s+' + FLOAT + r'\s+' + FLOAT + r'\s+([0-4]+)\s+' +
    r'hb\s+([0-1]+)\s+' + INTEGER + r'\s+' + INTEGER + r'\s+' +
    r'wake\s+([0-9]+)\s+' +
    r'wtc\s+' + INTEGER + r'\s+' +
    r'wpc\s+' + INTEGER + r'\s+' +
    r'pwr\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
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
        'error_flags',
        'temperature1',
        'temperature2',
        'temperature3',
        'temperature4',
        'temperature5',
        'humidity',
        'pressure',
        'ground_fault_enable',
        'ground_fault_isov3',
        'ground_fault_main',
        'ground_fault_sensors',
        'leak_detect_enable',
        'leak_detect_voltage1',
        'leak_detect_voltage2',
        'port1_power_state',
        'port1_voltage',
        'port1_current',
        'port1_error_flag',
        'port2_power_state',
        'port2_voltage',
        'port2_current',
        'port2_error_flag',
        'port3_power_state',
        'port3_voltage',
        'port3_current',
        'port3_error_flag',
        'port4_power_state',
        'port4_voltage',
        'port4_current',
        'port4_error_flag',
        'port5_power_state',
        'port5_voltage',
        'port5_current',
        'port5_error_flag',
        'port6_power_state',
        'port6_voltage',
        'port6_current',
        'port6_error_flag',
        'port7_power_state',
        'port7_voltage',
        'port7_current',
        'port7_error_flag',
        'port8_power_state',
        'port8_voltage',
        'port8_current',
        'port8_error_flag',
        'heartbeat_enable',
        'heartbeat_delta',
        'heartbeat_threshold',
        'wake_code',
        'wake_time_count',
        'wake_power_count',
        'power_state',
        'power_board_mode',
        'power_voltage_select',
        'power_voltage_main',
        'power_current_main',
        'power_voltage_12',
        'power_current_12',
        'power_voltage_24',
        'power_current_24'
    ])


class Parser(ParserCommon):
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

        # Assign the remaining data to the named parameters
        self.data.main_voltage.append(float(match.group(2)))
        self.data.main_current.append(float(match.group(3)))
        self.data.error_flags.append(int(match.group(4), 16))

        self.data.temperature1.append(float(match.group(5)))
        self.data.temperature2.append(float(match.group(6)))
        self.data.temperature3.append(float(match.group(7)))
        self.data.temperature4.append(float(match.group(8)))
        self.data.temperature5.append(float(match.group(9)))

        self.data.humidity.append(float(match.group(10)))
        self.data.pressure.append(float(match.group(11)))

        self.data.ground_fault_enable.append(int(match.group(12), 16))
        self.data.ground_fault_isov3.append(float(match.group(13)))
        self.data.ground_fault_main.append(float(match.group(14)))
        self.data.ground_fault_sensors.append(float(match.group(15)))

        self.data.leak_detect_enable.append(int(match.group(16), 16))
        self.data.leak_detect_voltage1.append(int(match.group(17)))
        self.data.leak_detect_voltage2.append(int(match.group(18)))

        self.data.port1_power_state.append(int(match.group(19)))
        self.data.port1_voltage.append(float(match.group(20)))
        self.data.port1_current.append(float(match.group(21)))
        self.data.port1_error_flag.append(int(match.group(22)))

        self.data.port2_power_state.append(int(match.group(23)))
        self.data.port2_voltage.append(float(match.group(24)))
        self.data.port2_current.append(float(match.group(25)))
        self.data.port2_error_flag.append(int(match.group(26)))

        self.data.port3_power_state.append(int(match.group(27)))
        self.data.port3_voltage.append(float(match.group(28)))
        self.data.port3_current.append(float(match.group(29)))
        self.data.port3_error_flag.append(int(match.group(30)))

        self.data.port4_power_state.append(int(match.group(31)))
        self.data.port4_voltage.append(float(match.group(32)))
        self.data.port4_current.append(float(match.group(33)))
        self.data.port4_error_flag.append(int(match.group(34)))

        self.data.port5_power_state.append(int(match.group(35)))
        self.data.port5_voltage.append(float(match.group(36)))
        self.data.port5_current.append(float(match.group(37)))
        self.data.port5_error_flag.append(int(match.group(38)))

        self.data.port6_power_state.append(int(match.group(39)))
        self.data.port6_voltage.append(float(match.group(40)))
        self.data.port6_current.append(float(match.group(41)))
        self.data.port6_error_flag.append(int(match.group(42)))

        self.data.port7_power_state.append(int(match.group(43)))
        self.data.port7_voltage.append(float(match.group(44)))
        self.data.port7_current.append(float(match.group(45)))
        self.data.port7_error_flag.append(int(match.group(46)))

        self.data.port8_power_state.append(int(match.group(47)))
        self.data.port8_voltage.append(float(match.group(48)))
        self.data.port8_current.append(float(match.group(49)))
        self.data.port8_error_flag.append(int(match.group(50)))

        self.data.heartbeat_enable.append(int(match.group(51)))
        self.data.heartbeat_delta.append(int(match.group(52)))
        self.data.heartbeat_threshold.append(int(match.group(53)))

        self.data.wake_code.append(int(match.group(54)))
        self.data.wake_time_count.append(float(match.group(55)))
        self.data.wake_power_count.append(int(match.group(56)))

        self.data.power_state.append(int(match.group(57)))
        self.data.power_board_mode.append(int(match.group(58)))
        self.data.power_voltage_select.append(int(match.group(59)))
        self.data.power_voltage_main.append(float(match.group(60)))
        self.data.power_current_main.append(float(match.group(61)))
        self.data.power_voltage_12.append(float(match.group(62)))
        self.data.power_current_12.append(float(match.group(63)))
        self.data.power_voltage_24.append(float(match.group(64)))
        self.data.power_current_24.append(float(match.group(65)))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for METBK
    superv = ParserCommon(infile)

    # load the data into a buffered object and parse the data into a dictionary
    superv.load_ascii()
    superv.parse_data()

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, superv.data.toDict())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.parsers.parse_pwrsys
@file cgsn_parsers/parsers/parse_pwrsys.py
@author Christopher Wingard
@brief Parses the Power System data logged by the custom built WHOI data loggers.
'''
import os
import re
import scipy.io as sio

# Import common utilites and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, NEWLINE

# Regex pattern for the power system records
PATTERN = (
    DCL_TIMESTAMP + r'\sPwrSys\spsc:\s' +
    FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'([0-9a-f]{4})\s([0-9a-f]{8})\s([0-9a-f]{8})\s' +
    r'pv1\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'pv2\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'pv3\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'pv4\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'wt1\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'wt2\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'fc1\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'fc2\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'bt1\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'bt2\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'bt3\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'bt4\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'ext\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'int\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'fcl\s' + FLOAT + r'\s' +
    r'swg\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'cvt\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'([0-1]{1})\s' + FLOAT + r'\s([0-9a-f]{8})\s' +
    r'(?:No_FC_Data\s)?' +
    r'([0-9a-f]{4})' + NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_pwrsys = [
        'dcl_date_time_string',
        'main_voltage',
        'main_current',
        'percent_charge',
        'override_flag',
        'error_flag1',
        'error_flag2',
        'solar_panel1_state',
        'solar_panel1_voltage',
        'solar_panel1_current',
        'solar_panel2_state',
        'solar_panel2_voltage',
        'solar_panel2_current',
        'solar_panel3_state',
        'solar_panel3_voltage',
        'solar_panel3_current',
        'solar_panel4_state',
        'solar_panel4_voltage',
        'solar_panel4_current',
        'wind_turbine1_state',
        'wind_turbine1_voltage',
        'wind_turbine1_current',
        'wind_turbine2_state',
        'wind_turbine2_voltage',
        'wind_turbine2_current',
        'fuel_cell1_state',
        'fuel_cell1_voltage',
        'fuel_cell1_current',
        'fuel_cell2_state',
        'fuel_cell2_voltage',
        'fuel_cell2_current',
        'battery_bank1_temperature',
        'battery_bank1_voltage',
        'battery_bank1_current',
        'battery_bank2_temperature',
        'battery_bank2_voltage',
        'battery_bank2_current',
        'battery_bank3_temperature',
        'battery_bank3_voltage',
        'battery_bank3_current',
        'battery_bank4_temperature',
        'battery_bank4_voltage',
        'battery_bank4_current',
        'external_voltage',
        'external_current',
        'internal_voltage',
        'internal_current',
        'internal_temperature',
        'fuel_cell_volume',
        'seawater_ground_state',
        'seawater_ground_positve',
        'seawater_ground_negative',
        'cvt_state',
        'cvt_voltage',
        'cvt_current',
        'cvt_interlock',
        'cvt_temperature',
        'error_flag3'
    ]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the PWRSYS specific
    methods to parse the data, and extracts the PWRSYS data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_pwrsys)

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
        self.data.percent_charge.append(float(match.group(4)))
        self.data.override_flag.append(str(match.group(5)))
        self.data.error_flag1.append(str(match.group(6)))
        self.data.error_flag2.append(str(match.group(7)))
        self.data.solar_panel1_state.append(int(match.group(8)))
        self.data.solar_panel1_voltage.append(float(match.group(9)))
        self.data.solar_panel1_current.append(float(match.group(10)))
        self.data.solar_panel2_state.append(int(match.group(11)))
        self.data.solar_panel2_voltage.append(float(match.group(12)))
        self.data.solar_panel2_current.append(float(match.group(13)))
        self.data.solar_panel3_state.append(int(match.group(14)))
        self.data.solar_panel3_voltage.append(float(match.group(15)))
        self.data.solar_panel3_current.append(float(match.group(16)))
        self.data.solar_panel4_state.append(int(match.group(17)))
        self.data.solar_panel4_voltage.append(float(match.group(18)))
        self.data.solar_panel4_current.append(float(match.group(19)))
        self.data.wind_turbine1_state.append(int(match.group(20)))
        self.data.wind_turbine1_voltage.append(float(match.group(21)))
        self.data.wind_turbine1_current.append(float(match.group(22)))
        self.data.wind_turbine2_state.append(int(match.group(23)))
        self.data.wind_turbine2_voltage.append(float(match.group(24)))
        self.data.wind_turbine2_current.append(float(match.group(25)))
        self.data.fuel_cell1_state.append(int(match.group(26)))
        self.data.fuel_cell1_voltage.append(float(match.group(27)))
        self.data.fuel_cell1_current.append(float(match.group(28)))
        self.data.fuel_cell2_state.append(int(match.group(29)))
        self.data.fuel_cell2_voltage.append(float(match.group(30)))
        self.data.fuel_cell2_current.append(float(match.group(31)))
        self.data.battery_bank1_temperature.append(float(match.group(32)))
        self.data.battery_bank1_voltage.append(float(match.group(33)))
        self.data.battery_bank1_current.append(float(match.group(34)))
        self.data.battery_bank2_temperature.append(float(match.group(35)))
        self.data.battery_bank2_voltage.append(float(match.group(36)))
        self.data.battery_bank2_current.append(float(match.group(37)))
        self.data.battery_bank3_temperature.append(float(match.group(38)))
        self.data.battery_bank3_voltage.append(float(match.group(39)))
        self.data.battery_bank3_current.append(float(match.group(40)))
        self.data.battery_bank4_temperature.append(float(match.group(41)))
        self.data.battery_bank4_voltage.append(float(match.group(42)))
        self.data.battery_bank4_current.append(float(match.group(43)))
        self.data.external_voltage.append(float(match.group(44)))
        self.data.external_current.append(float(match.group(45)))
        self.data.internal_voltage.append(float(match.group(46)))
        self.data.internal_current.append(float(match.group(47)))
        self.data.internal_temperature.append(float(match.group(48)))
        self.data.fuel_cell_volume.append(float(match.group(49)))
        self.data.seawater_ground_state.append(int(match.group(50)))
        self.data.seawater_ground_positve.append(float(match.group(51)))
        self.data.seawater_ground_negative.append(float(match.group(52)))
        self.data.cvt_state.append(int(match.group(53)))
        self.data.cvt_voltage.append(float(match.group(54)))
        self.data.cvt_current.append(float(match.group(55)))
        self.data.cvt_interlock.append(int(match.group(56)))
        self.data.cvt_temperature.append(float(match.group(57)))
        self.data.error_flag3.append(str(match.group(58)))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for PWRSYS
    pwrsys = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    pwrsys.load_ascii()
    pwrsys.parse_data()

    # write the resulting Bunch object via the toDict method to a matlab
    # formatted structured array.
    sio.savemat(outfile, pwrsys.data.toDict())

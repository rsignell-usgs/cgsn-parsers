#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.parsers.parse_adcp
@file cgsn_parsers/parsers/parse_adcp.py
@author Christopher Wingard
@brief Parses Teledyne RDI WorkHorse ADCP data, reported as an ASCIIHEX string
    (in PD0 format) to the DCL with a DCL timestamp prepended to the record
    string.

Release notes:
    This code evolved from earlier work by Roger Unwin at the University of
    California, San Diego as part of the Ocean Observatories Initiative
    CyberInfrastructure team. See https://github.com/ooici/marine-integrations/blob/
    f9371e42341e1cb9363df84e8980ed063f0c0a95/mi/instrument/teledyne/particles.py
'''
import os
import re

from binascii import unhexlify
from munch import Munch as Bunch
from struct import unpack

# Import common utilites and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, NEWLINE

# Regex set to find the start of a PD0 packet (DCL timestamp and the first 6
# bytes of the header data). Using the first 6 bytes of the packet is a more
# explicit regex than just the 0x7f7f marker the manual specifies, eliminating
# false positive matches.
PATTERN = (
    DCL_TIMESTAMP + r'\s+' +
    r'(7F7F)([0-9A-F]{4})(00)(06|07)' +
    r'([0-9A-F]+)' + NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)


class ParameterNames(object):
    '''
    Teledyne RDI WorkHorse PD0 formatted data files
    '''
    def __init__(self):
        # Header Data
        self._header = [
            'num_bytes',
            'num_data_types'
        ]

        # Fixed Leader Data
        self._fixed = [
            'firmware_version',
            'firmware_revision',
            'sysconfig_frequency',
            'sysconfig_beam_pattern',
            'sysconfig_sensor_config',
            'sysconfig_head_attached',
            'sysconfig_vertical_orientation',
            'data_flag',
            'lag_length',
            'num_beams',
            'num_cells',
            'pings_per_ensemble',
            'depth_cell_length',
            'blank_after_transmit',
            'signal_processing_mode',
            'low_corr_threshold',
            'num_code_repetitions',
            'percent_good_min',
            'error_vel_threshold',
            'time_per_ping_minutes',
            'time_per_ping_seconds',
            'coord_transform_type',
            'coord_transform_tilts',
            'coord_transform_beams',
            'coord_transform_mapping',
            'heading_alignment',
            'heading_bias',
            'sensor_source_speed',
            'sensor_source_depth',
            'sensor_source_heading',
            'sensor_source_pitch',
            'sensor_source_roll',
            'sensor_source_conductivity',
            'sensor_source_temperature',
            'sensor_available_depth',
            'sensor_available_heading',
            'sensor_available_pitch',
            'sensor_available_roll',
            'sensor_available_conductivity',
            'sensor_available_temperature',
            'bin_1_distance',
            'transmit_pulse_length',
            'reference_layer_start',
            'reference_layer_stop',
            'false_target_threshold',
            'transmit_lag_distance',
            'system_bandwidth',
            'serial_number',
            'beam_angle'
        ]

        # Variable Leader Data
        self._variable = [
            'ensemble_number',
            'ensemble_number_increment',
            'real_time_clock1',
            'bit_result_demod_1',
            'bit_result_demod_2',
            'bit_result_timing',
            'speed_of_sound',
            'transducer_depth',
            'heading',
            'pitch',
            'roll',
            'salinity',
            'temperature',
            'mpt_minutes',
            'mpt_seconds',
            'heading_stdev',
            'pitch_stdev',
            'roll_stdev',
            'adc_transmit_current',
            'adc_transmit_voltage',
            'adc_ambient_temp',
            'adc_pressure_plus',
            'adc_pressure_minus',
            'adc_attitude_temp',
            'adc_attitude',
            'adc_contamination_sensor',
            'bus_error_exception',
            'address_error_exception',
            'illegal_instruction_exception',
            'zero_divide_instruction',
            'emulator_exception',
            'unassigned_exception',
            'watchdog_restart_occurred',
            'battery_saver_power',
            'pinging',
            'cold_wakeup_occurred',
            'unknown_wakeup_occurred',
            'clock_read_error',
            'unexpected_alarm',
            'clock_jump_forward',
            'clock_jump_backward',
            'power_fail',
            'spurious_dsp_interrupt',
            'spurious_uart_interrupt',
            'spurious_clock_interrupt',
            'level_7_interrupt',
            'pressure',
            'pressure_variance',
            'real_time_clock2'
        ]

        # Velocity Data
        self._velocity = [
            'eastward',
            'northward',
            'vertical',
            'error'
        ]

        # Correlation Magnitude Data
        self._correlation = [
            'magnitude_beam1',
            'magnitude_beam2',
            'magnitude_beam3',
            'magnitude_beam4'
        ]

        # Echo Intensity Data
        self._echo = [
            'intensity_beam1',
            'intensity_beam2',
            'intensity_beam3',
            'intensity_beam4'
        ]

        # Percent Good Data
        self._percent = [
            'good_3beam',
            'transforms_reject',
            'bad_beams',
            'good_4beam'
        ]

    # Create the initial dictionary object from the fixed, variable, velocity,
    # correlation magnitude, echo intensity and percent good data types. Note,
    # while it is possible that a pd0 data file may only contain the fixed and
    # variable data types, it really wouldn't make much sense. Thus, we can
    # assume that velocity, correlation, intensity and percent data is present
    # as the default.
    def create_dict(self):
        '''
        Create a Bunch class object to store the parameter names for the
        Workhorse ADCP pd0 data files, with the data organized hierarchically
        by the data type.
        '''
        bunch = Bunch()
        bunch.time = []
        bunch.header = Bunch()
        bunch.fixed = Bunch()
        bunch.variable = Bunch()
        bunch.velocity = Bunch()
        bunch.correlation = Bunch()
        bunch.echo = Bunch()
        bunch.percent = Bunch()

        for name in self._header:
            bunch.header[name] = []

        for name in self._fixed:
            bunch.fixed[name] = []

        for name in self._variable:
            bunch.variable[name] = []

        for name in self._velocity:
            bunch.velocity[name] = []

        for name in self._correlation:
            bunch.correlation[name] = []

        for name in self._echo:
            bunch.echo[name] = []

        for name in self._percent:
            bunch.percent[name] = []

        return bunch


class Parser(ParserCommon):
    """
    A Parser class that extracts the data records from a PD0 data packet
    formatted in ASCIIHEX produced by a Teledyne RDI Workhorse ADCP.
    """
    def __init__(self, infile):
        # set the infile name and path
        self.infile = infile

        # initialize the data dictionary using the names defined above
        data = ParameterNames()
        self.data = data.create_dict()
        self.raw = None

    def parse_data(self):
        '''
        Iterate through the record markers (defined via the regex expression
        above) in the data object, and parse the data file into a pre-defined
        dictionary object created using the Bunch class.
        '''
        for line in self.raw:
            match = REGEX.match(line)
            if match:
                self._build_parsed_values(match)

    # Parse the ADCP ensembles, building a full, parsed record
    def _build_parsed_values(self, match):
        """
        Start by parsing the beginning portion of the ensemble (Header Data)
        """
        # build the ensemble string from match.group(2) through to the end.
        length = unpack("<H", unhexlify(match.group(3)))[0]
        ensemble = unhexlify(''.join(match.groups()[1:]))

        # Calculate the checksum
        total = int(0)
        for i in range(0, length):
            total += int(ord(ensemble[i]))

        checksum = total & 65535    # bitwise and with 65535 or mod vs 65536
        if checksum != unpack("<H", ensemble[length: length+2])[0]:
            raise Exception("Checksum mismatch")

        (header_id, data_source_id, num_bytes, spare, num_data_types) = \
            unpack('<2BH2B', ensemble[0:6])

        self.data.time.append(dcl_to_epoch(match.group(1)))
        self.data.header.num_bytes.append(num_bytes)
        self.data.header.num_data_types.append(num_data_types)

        offsets = []    # create list for offsets
        strt = 6        # offsets start at byte 6 (using 0 indexing)
        nDT = 1         # counter for N data types
        while nDT <= num_data_types:
            value = unpack('<H', ensemble[strt:strt+2])[0]
            offsets.append(value)
            strt += 2
            nDT += 1

        for offset in offsets:
            # for each offset, using the starting byte, determine the data type
            # and then parse accordingly.
            data_type = unpack('<H', ensemble[offset:offset+2])[0]

            # fixed leader data (x00x00)
            if data_type == 0:
                chunk = ensemble[offset:offset+59]
                self._parse_fixed_chunk(chunk)
                iCells = self.num_depth_cells   # grab the # of depth cells

            # variable leader data (x80x00)
            if data_type == 128:
                chunk = ensemble[offset:offset+65]
                self._parse_variable_chunk(chunk)

            # velocity data (x00x01)
            if data_type == 256:
                # number of bytes is a function of the user selectable number
                # of depth cells (WN command), obtained above
                nBytes = 2 + 8 * iCells
                chunk = ensemble[offset:offset+nBytes]
                self._parse_velocity_chunk(chunk)

            # correlation magnitude data (x00x02)
            if data_type == 512:
                # number of bytes is a function of the user selectable number
                # of depth cells (WN command), obtained above
                nBytes = 2 + 4 * iCells
                chunk = ensemble[offset:offset+nBytes]
                self._parse_corelation_magnitude_chunk(chunk)

            # echo intensity data (x00x03)
            if data_type == 768:
                # number of bytes is a function of the user selectable number
                # of depth cells (WN command), obtained above
                nBytes = 2 + 4 * iCells
                chunk = ensemble[offset:offset+nBytes]
                self._parse_echo_intensity_chunk(chunk)

            # percent-good data (x00x04)
            if data_type == 1024:
                # number of bytes is a function of the user selectable number
                # of depth cells (WN command), obtained above
                nBytes = 2 + 4 * iCells
                chunk = ensemble[offset:offset+nBytes]
                self._parse_percent_good_chunk(chunk)

    def _parse_fixed_chunk(self, chunk):
        """
        Parse the fixed leader portion of the particle

        @throws Exception If there is a problem with sample creation
        """
        (fixed_leader_id, firmware_version, firmware_revision,
         sysconfig_frequency, data_flag, lag_length, num_beams, num_cells,
         pings_per_ensemble, depth_cell_length, blank_after_transmit,
         signal_processing_mode, low_corr_threshold, num_code_repetitions,
         percent_good_min, error_vel_threshold, time_per_ping_minutes,
         time_per_ping_seconds, time_per_ping_hundredths, coord_transform_type,
         heading_alignment, heading_bias, sensor_source, sensor_available,
         bin_1_distance, transmit_pulse_length, reference_layer_start,
         reference_layer_stop, false_target_threshold, SPARE1,
         transmit_lag_distance, SPARE2, system_bandwidth,
         SPARE3, SPARE4, serial_number, beam_angle) = \
            unpack('<H2BH4B3H4BH4B2h2B2H4BHQH2BIB', chunk)

        if 0 != fixed_leader_id:
            raise Exception("fixed_leader_id was not equal to 0")

        # store the number of depth cells for use elsewhere
        self.num_depth_cells = num_cells

        self.data.fixed.firmware_version.append(firmware_version)
        self.data.fixed.firmware_revision.append(firmware_revision)

        frequencies = [75, 150, 300, 600, 1200, 2400]

        self.data.fixed.sysconfig_frequency.append(frequencies[sysconfig_frequency & 0b00000111])
        self.data.fixed.sysconfig_beam_pattern.append(1 if sysconfig_frequency & 0b00001000 else 0)
        self.data.fixed.sysconfig_sensor_config.append(sysconfig_frequency & 0b00110000 >> 4)
        self.data.fixed.sysconfig_head_attached.append(1 if sysconfig_frequency & 0b01000000 else 0)
        self.data.fixed.sysconfig_vertical_orientation.append(1 if sysconfig_frequency & 0b10000000 else 0)

        if 0 != data_flag:
            raise Exception("data_flag was not equal to 0")

        self.data.fixed.data_flag.append(data_flag)
        self.data.fixed.lag_length.append(lag_length)
        self.data.fixed.num_beams.append(num_beams)
        self.data.fixed.num_cells.append(num_cells)
        self.data.fixed.pings_per_ensemble.append(pings_per_ensemble)
        self.data.fixed.depth_cell_length.append(depth_cell_length)
        self.data.fixed.blank_after_transmit.append(blank_after_transmit)

        if 1 != signal_processing_mode:
            raise Exception("signal_processing_mode was not equal to 1")

        self.data.fixed.signal_processing_mode.append(signal_processing_mode)
        self.data.fixed.low_corr_threshold.append(low_corr_threshold)
        self.data.fixed.num_code_repetitions.append(num_code_repetitions)
        self.data.fixed.percent_good_min.append(percent_good_min)
        self.data.fixed.error_vel_threshold.append(error_vel_threshold)
        self.data.fixed.time_per_ping_minutes.append(time_per_ping_minutes)

        tpp_float_seconds = float(time_per_ping_seconds + (time_per_ping_hundredths/100))
        self.data.fixed.time_per_ping_seconds.append(tpp_float_seconds)
        self.data.fixed.coord_transform_type.append(coord_transform_type & 0b00011000 >> 3)
        self.data.fixed.coord_transform_tilts.append(1 if coord_transform_type & 0b00000100 else 0)
        self.data.fixed.coord_transform_beams.append(1 if coord_transform_type & 0b0000000 else 0)
        self.data.fixed.coord_transform_mapping.append(1 if coord_transform_type & 0b00000001 else 0)

        # lame, but expedient - mask off un-needed bits
        self.coord_transform_type = (coord_transform_type & 0b00011000) >> 3

        self.data.fixed.heading_alignment.append(heading_alignment)
        self.data.fixed.heading_bias.append(heading_bias)
        self.data.fixed.sensor_source_speed.append(1 if sensor_source & 0b01000000 else 0)
        self.data.fixed.sensor_source_depth.append(1 if sensor_source & 0b00100000 else 0)
        self.data.fixed.sensor_source_heading.append(1 if sensor_source & 0b00010000 else 0)
        self.data.fixed.sensor_source_pitch.append(1 if sensor_source & 0b00001000 else 0)
        self.data.fixed.sensor_source_roll.append(1 if sensor_source & 0b00000100 else 0)
        self.data.fixed.sensor_source_conductivity.append(1 if sensor_source & 0b00000010 else 0)
        self.data.fixed.sensor_source_temperature.append(1 if sensor_source & 0b00000001 else 0)
        self.data.fixed.sensor_available_depth.append(1 if sensor_available & 0b00100000 else 0)
        self.data.fixed.sensor_available_heading.append(1 if sensor_available & 0b00010000 else 0)
        self.data.fixed.sensor_available_pitch.append(1 if sensor_available & 0b00001000 else 0)
        self.data.fixed.sensor_available_roll.append(1 if sensor_available & 0b00000100 else 0)
        self.data.fixed.sensor_available_conductivity.append(1 if sensor_available & 0b00000010 else 0)
        self.data.fixed.sensor_available_temperature.append(1 if sensor_available & 0b00000001 else 0)
        self.data.fixed.bin_1_distance.append(bin_1_distance)
        self.data.fixed.transmit_pulse_length.append(transmit_pulse_length)
        self.data.fixed.reference_layer_start.append(reference_layer_start)
        self.data.fixed.reference_layer_stop.append(reference_layer_stop)
        self.data.fixed.false_target_threshold.append(false_target_threshold)
        self.data.fixed.transmit_lag_distance.append(transmit_lag_distance)
        self.data.fixed.system_bandwidth.append(system_bandwidth)
        self.data.fixed.serial_number.append(serial_number)
        self.data.fixed.beam_angle.append(beam_angle)

    def _parse_variable_chunk(self, chunk):
        """
        Parse the variable leader portion of the particle

        @throws Exception If there is a problem with sample creation
        """
        rtc1 = {}
        rtc2 = {}
        (variable_leader_id, ensemble_number, rtc1['year'], rtc1['month'],
         rtc1['day'], rtc1['hour'], rtc1['minute'], rtc1['second'],
         rtc1['hundredths'], ensemble_number_increment, error_bit_field,
         reserved_error_bit_field, speed_of_sound, transducer_depth, heading,
         pitch, roll, salinity, temperature, mpt_minutes, mpt_seconds_component,
         mpt_hundredths_component, heading_stdev, pitch_stdev, roll_stdev,
         adc_transmit_current, adc_transmit_voltage, adc_ambient_temp,
         adc_pressure_plus, adc_pressure_minus, adc_attitude_temp,
         adc_attitiude, adc_contamination_sensor, error_status_word_1,
         error_status_word_2, error_status_word_3, error_status_word_4,
         SPARE1, pressure, pressure_variance, SPARE2, rtc2['century'],
         rtc2['year'], rtc2['month'], rtc2['day'], rtc2['hour'], rtc2['minute'],
         rtc2['second'], rtc2['hundredths']) = \
            unpack('<2H10B3H2hHh18BH2I9B', chunk)

        if 128 != variable_leader_id:
            raise Exception("variable_leader_id was not equal to 128")

        self.data.variable.ensemble_number.append(ensemble_number)
        self.data.variable.ensemble_number_increment.append(ensemble_number_increment)

        self.data.variable.real_time_clock1.append([rtc1['year'], rtc1['month'], rtc1['day'],
                                                    rtc1['hour'], rtc1['minute'], rtc1['second'],
                                                    rtc1['hundredths']])

        self.data.variable.bit_result_demod_1.append(1 if error_bit_field & 0b00001000 else 0)
        self.data.variable.bit_result_demod_2.append(1 if error_bit_field & 0b00010000 else 0)
        self.data.variable.bit_result_timing.append(1 if error_bit_field & 0b00000010 else 0)
        self.data.variable.speed_of_sound.append(speed_of_sound)
        self.data.variable.transducer_depth.append(transducer_depth)
        self.data.variable.heading.append(heading)
        self.data.variable.pitch.append(pitch)
        self.data.variable.roll.append(roll)
        self.data.variable.salinity.append(salinity)
        self.data.variable.temperature.append(temperature)
        self.data.variable.mpt_minutes.append(mpt_minutes)

        mpt_seconds = float(mpt_seconds_component + (mpt_hundredths_component/100))
        self.data.variable.mpt_seconds.append(mpt_seconds)
        self.data.variable.heading_stdev.append(heading_stdev)
        self.data.variable.pitch_stdev.append(pitch_stdev)
        self.data.variable.roll_stdev.append(roll_stdev)
        self.data.variable.adc_transmit_current.append(adc_transmit_current)
        self.data.variable.adc_transmit_voltage.append(adc_transmit_voltage)
        self.data.variable.adc_ambient_temp.append(adc_ambient_temp)
        self.data.variable.adc_pressure_plus.append(adc_pressure_plus)
        self.data.variable.adc_pressure_minus.append(adc_pressure_minus)
        self.data.variable.adc_attitude_temp.append(adc_attitude_temp)
        self.data.variable.adc_attitude.append(adc_attitiude)
        self.data.variable.adc_contamination_sensor.append(adc_contamination_sensor)
        self.data.variable.bus_error_exception.append(1 if error_status_word_1 & 0b00000001 else 0)
        self.data.variable.address_error_exception.append(1 if error_status_word_1 & 0b00000010 else 0)
        self.data.variable.illegal_instruction_exception.append(1 if error_status_word_1 & 0b00000100 else 0)
        self.data.variable.zero_divide_instruction.append(1 if error_status_word_1 & 0b00001000 else 0)
        self.data.variable.emulator_exception.append(1 if error_status_word_1 & 0b00010000 else 0)
        self.data.variable.unassigned_exception.append(1 if error_status_word_1 & 0b00100000 else 0)
        self.data.variable.watchdog_restart_occurred.append(1 if error_status_word_1 & 0b01000000 else 0)
        self.data.variable.battery_saver_power.append(1 if error_status_word_1 & 0b10000000 else 0)
        self.data.variable.pinging.append(1 if error_status_word_1 & 0b00000001 else 0)
        self.data.variable.cold_wakeup_occurred.append(1 if error_status_word_1 & 0b01000000 else 0)
        self.data.variable.unknown_wakeup_occurred.append(1 if error_status_word_1 & 0b10000000 else 0)
        self.data.variable.clock_read_error.append(1 if error_status_word_3 & 0b00000001 else 0)
        self.data.variable.unexpected_alarm.append(1 if error_status_word_3 & 0b00000010 else 0)
        self.data.variable.clock_jump_forward.append(1 if error_status_word_3 & 0b00000100 else 0)
        self.data.variable.clock_jump_backward.append(1 if error_status_word_3 & 0b00001000 else 0)
        self.data.variable.power_fail.append(1 if error_status_word_4 & 0b00001000 else 0)
        self.data.variable.spurious_dsp_interrupt.append(1 if error_status_word_4 & 0b00010000 else 0)
        self.data.variable.spurious_uart_interrupt.append(1 if error_status_word_4 & 0b00100000 else 0)
        self.data.variable.spurious_clock_interrupt.append(1 if error_status_word_4 & 0b01000000 else 0)
        self.data.variable.level_7_interrupt.append(1 if error_status_word_4 & 0b10000000 else 0)
        self.data.variable.pressure.append(pressure)
        self.data.variable.pressure_variance.append(pressure_variance)
        self.data.variable.real_time_clock2.append([rtc2['century'], rtc2['year'],
                                                    rtc2['month'], rtc2['day'],
                                                    rtc2['hour'], rtc2['minute'],
                                                    rtc2['second'], rtc2['hundredths']])

    def _parse_velocity_chunk(self, chunk):
        """
        Parse the velocity portion of the particle

        @throws Exception If there is a problem with sample creation
        """
        N = (len(chunk) - 2) / 2 / 4
        offset = 0

        velocity_data_id = unpack("<H", chunk[0:2])[0]
        if 256 != velocity_data_id:
            raise Exception("velocity_data_id was not equal to 256")

        beam1 = []
        beam2 = []
        beam3 = []
        beam4 = []
        for row in range(1, N):
            (a, b, c, d) = unpack('<4h', chunk[offset + 2: offset + 10])
            beam1.append(a)
            beam2.append(b)
            beam3.append(c)
            beam4.append(d)
            offset += 4 * 2

        self.data.velocity.eastward.append(beam1)
        self.data.velocity.northward.append(beam2)
        self.data.velocity.vertical.append(beam3)
        self.data.velocity.error.append(beam4)

    def _parse_corelation_magnitude_chunk(self, chunk):
        """
        Parse the corelation magnitude portion of the particle

        @throws Exception If there is a problem with sample creation
        """
        N = (len(chunk) - 2) / 4
        offset = 0

        correlation_magnitude_id = unpack("<H", chunk[0:2])[0]
        if 512 != correlation_magnitude_id:
            raise Exception("correlation_magnitude_id was not equal to 512")

        beam1 = []
        beam2 = []
        beam3 = []
        beam4 = []
        for row in range(1, N):
            (a, b, c, d) = unpack('<4B', chunk[offset + 2: offset + 6])
            beam1.append(a)
            beam2.append(b)
            beam3.append(c)
            beam4.append(d)
            offset += 4

        self.data.correlation.magnitude_beam1.append(beam1)
        self.data.correlation.magnitude_beam2.append(beam2)
        self.data.correlation.magnitude_beam3.append(beam3)
        self.data.correlation.magnitude_beam4.append(beam4)

    def _parse_echo_intensity_chunk(self, chunk):
        """
        Parse the echo intensity portion of the particle

        @throws Exception If there is a problem with sample creation
        """
        N = (len(chunk) - 2) / 4
        offset = 0

        echo_intensity_id = unpack("<H", chunk[0:2])[0]
        if 768 != echo_intensity_id:
            raise Exception("echo_intensity_id was not equal to 768")

        beam1 = []
        beam2 = []
        beam3 = []
        beam4 = []
        for row in range(1, N):
            (a, b, c, d) = unpack('<4B', chunk[offset + 2: offset + 6])
            beam1.append(a)
            beam2.append(b)
            beam3.append(c)
            beam4.append(d)
            offset += 4

        self.data.echo.intensity_beam1.append(beam1)
        self.data.echo.intensity_beam2.append(beam2)
        self.data.echo.intensity_beam3.append(beam3)
        self.data.echo.intensity_beam4.append(beam4)

    def _parse_percent_good_chunk(self, chunk):
        """
        Parse the percent good portion of the particle

        @throws Exception If there is a problem with sample creation
        """
        N = (len(chunk) - 2) / 4
        offset = 0

        percent_good_id = unpack("<H", chunk[0:2])[0]
        if 1024 != percent_good_id:
            raise Exception("percent_good_id was not equal to 1024")

        percent1 = []
        percent2 = []
        percent3 = []
        percent4 = []
        for row in range(1, N):
            (a, b, c, d) = unpack('<4B', chunk[offset + 2: offset + 6])
            percent1.append(a)
            percent2.append(b)
            percent3.append(c)
            percent4.append(d)
            offset += 4

        self.data.percent.good_3beam.append(percent1)
        self.data.percent.transforms_reject.append(percent2)
        self.data.percent.bad_beams.append(percent3)
        self.data.percent.good_4beam.append(percent4)


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for the ADCP
    adcp = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    adcp.load_ascii()
    adcp.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(adcp.data.toJSON())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_parse_optaa
@file cgsn_parsers/tests/test_parse_optaa.py
@author Christopher Wingard
@brief Unit tests for parsing the OPTAA data
"""
import numpy as np
import json
import unittest

from munch import Munch
from nose.plugins.attrib import attr
from os import path

from cgsn_parsers.parsers.parse_optaa import Parser

# data sources for testing the parser
RAWDATA = path.join(path.dirname(__file__), 'optaa/20150809_075841.optaa_cspp.log')
UCSPPDATA = path.join(path.dirname(__file__), 'optaa/ucspp_32213320_ACS_ACS.txt')

# data sources for testing the processing
PARSED = path.join(path.dirname(__file__), 'optaa/20150809_075841.optaa_cspp.json')
DEVFILE = path.join(path.dirname(__file__), 'optaa/acs138_cspp_20140703.dev')
COEFF_FILE = path.join(path.dirname(__file__), 'optaa/CGINS-OPTAAJ-00138_20150410.pkl')
CSV_URL = 'https://github.com/ooi-integration/asset-management/raw/master/calibration/OPTAAJ/CGINS-OPTAAJ-00138__20150410.csv'

@attr('parse')
class TestParsingUnit(unittest.TestCase):
    '''
    OOI Endurance, Pioneer and Global moorings use the WET Labs, Inc., Spectral
    Absorption and Attenuation Sensor (ac-s) for the OPTAA instrument. This 
    unit test will look at the parser output compared to the output from 
    independently developed code created by engineers at WET Labs, Inc.
    '''
    def setUp(self):
        '''
        Using the sample data, initialize the Parser object with parsed OPTAA
        data and set the expected output arrays.
        '''
        # initialize Parser objects for the CTDBP types defined above.
        self.optaa = Parser(RAWDATA)
        self.optaa.load_binary()
        self.optaa.parse_data()
        
        # set the expected output array for the OPTAA data. Data is from
        # the OPTAA on a uCSPP (source doesn't really matter as we are working
        # with binary data files). The uCSPP software extracts the binary data
        # into a tab-delimited ASCII file.
        self.expected = np.genfromtxt(UCSPPDATA, skip_header=6, dtype=np.int)       

    def test_parse_optaa(self):
        '''
        Test parsing of the OPTAA data file
        '''
        serial_num = np.array(self.optaa.data.serial_number)
        external_temp = np.array(self.optaa.data.external_temp_raw)
        internal_temp = np.array(self.optaa.data.internal_temp_raw)
        num_wvlngths = np.array(self.optaa.data.num_wavelengths)
        c_reference = np.array(self.optaa.data.c_reference_raw)
        ncols = num_wvlngths[0]

        np.testing.assert_array_equal(serial_num, self.expected[:, 3])
        np.testing.assert_array_equal(external_temp, self.expected[:, -3])
        np.testing.assert_array_equal(internal_temp, self.expected[:, -2])
        np.testing.assert_array_equal(num_wvlngths, self.expected[:, 5])
        np.testing.assert_array_equal(c_reference, self.expected[:, 7:7+ncols])


@attr('process')
class TestProcessingUnit(unittest.TestCase):
    '''
    OOI Endurance, Pioneer and Global moorings use the WET Labs, Inc., Spectral
    Absorption and Attenuation Sensor (ac-s) for the OPTAA instrument. This 
    unit test will look at the processing output compared to the output from 
    independently developed code created WET Labs and Russell Desiderio.
    '''
    def setUp(self):
        '''
        Using the sample data, initialize the Parser object and set the 
        expected output arrays.
        '''
        # load the parsed, json data file
        with open(PARSED, 'rb') as f:
            self.optaa = Munch(json.load(f))
            
    def test_process_load_dev(self):
        '''
        Load a factory device file and parse
        '''
        assert False
        
    def test_process_load_csv(self):
        '''
        Load calibration coefficients from GitHub
        '''
        assert False

    def test_process_load_pickle(self):
        '''
        Load the locally stored serialized calibrations object
        '''
        assert False

    def test_process_apply_dev(self):
        '''
        Apply the calibration data to the parsed data
        '''
        assert False

    def test_process_apply_tscorr(self):
        '''
        Apply the temperature and salinity corrections to the data
        '''
        assert False

    def test_process_apply_scatcorr(self):
        '''
        Apply the scatter correction to the data
        '''
        assert False

if __name__ == '__main__':       
    unittest.main()

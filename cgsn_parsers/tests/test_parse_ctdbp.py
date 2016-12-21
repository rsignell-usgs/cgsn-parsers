#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_parse_ctdbp
@file cgsn_parsers/tests/test_parse_ctdbp.py
@author Christopher Wingard
@brief Unit tests for parsing the 3 different types of CTDBP data
"""
import numpy as np
import unittest
from nose.plugins.attrib import attr
from os import path
from cgsn_parsers.parsers.parse_ctdbp import Parser


TESTDATA_CTDBP_TYPE1 = path.join(path.dirname(__file__), 'ctdbp/20161219.ctdbp1.log')
TESTDATA_CTDBP_TYPE2 = path.join(path.dirname(__file__), 'ctdbp/20161219.ctdbp2.log')
TESTDATA_CTDBP_TYPE3 = path.join(path.dirname(__file__), 'ctdbp/20161110.ctdbp3.log')


@attr('parse')
class TestParsingUnit(unittest.TestCase):
    '''
    OOI Endurance and Pioneer moorings use the Sea-Bird Electronics 16Plus V2
    CTDs, on the Buoy, NSIF and MFN instrument frames, configured in one of 3 
    ways. All units are set to report conductivity, temperature and pressure in
    engineering units.

    On the NSIF, for all the CSMs, the CTD is programmed to output measurements
    every 10 s for 3 minutes every 15 minutes. Pioneer moorings configure the
    CTD on the MFN in the same way. This is CTDBP Type 1.

    On the NSIF, for the Endurance ISSM, the CTD includes an Aanderaa Optode
    4831 measurement (reports O2 concentration in uMol/L). The units are
    programmed to autonomously record a 10 s averaged measurement every 15
    minutes in addition to being polled (via the TS command) every hour at the
    bottom of the hour. The 4 Endurance MFN units are programmed the same way.
    This is CTDBP Type 2.

    On the buoy instrument frame (approximately 1 m below the surface), for the
    Endurance ISSM only, the CTD includes a WET Labs ECO Triplet (FLORT) 
    fluorometer measuring chlorohyll and CDOM fluroescence and optical 
    backscatter (values are reported in counts). The units are programmed to 
    autonomously record a 10 s averaged measurement every 30 minutes in 
    addition to being polled (via the TS command) every hour at the bottom of 
    the hour. This is CTDBP Type 3.

    This test class will parse and compare the outputs from all three types of
    CTDBPs to confirm the parser functions as expected.
    '''
    def setUp(self):
        '''
        Using sample data files, initialize the Parser objects for each of the
        3 CTDBP types and set the expected output arrays.
        '''
        # initialize Parser objects for the CTDBP types defined above.
        self.ctdbp_type1 = Parser(TESTDATA_CTDBP_TYPE1, 1)
        self.ctdbp_type2 = Parser(TESTDATA_CTDBP_TYPE2, 2)
        self.ctdbp_type3 = Parser(TESTDATA_CTDBP_TYPE3, 3)
        
        # set the expected output arrays for the each of the CTDBP types using
        # the raw data minus the date/time strings (data copied directly from 
        # the raw files and reformatted into arrays). For CTDBP type 1 data, 
        # just using the first burst of data.
        self.type1_expected = np.array([
            [9.6259, 3.13279, 7.185],
            [9.6320, 3.13309, 6.602],
            [9.6247, 3.13116, 6.928],
            [9.6077, 3.12590, 6.848],
            [9.6053, 3.12557, 6.799],
            [9.6111, 3.12691, 6.620],
            [9.6179, 3.12995, 6.871],
            [9.6361, 3.13461, 6.995],
            [9.6171, 3.12810, 6.686],
            [9.6115, 3.12712, 7.048],
            [9.6207, 3.12971, 6.844],
            [9.6088, 3.12646, 6.706],
            [9.5946, 3.12296, 7.040],
            [9.6085, 3.12662, 6.986],
            [9.6163, 3.12836, 6.879],
            [9.6240, 3.13117, 7.009],
            [9.6002, 3.12410, 6.832],
            [9.6075, 3.12734, 6.937]])
            
        self.type2_expected = np.array([
            [10.1877,  3.66669,   88.598,  188.850],
            [10.1725,  3.66563,   88.409,  190.529],
            [10.1930,  3.66693,   87.201,  191.661],
            [10.2378,  3.66958,   86.939,  192.933],
            [10.3269,  3.67482,   86.919,  196.923],
            [10.3886,  3.67875,   86.325,  200.182],
            [10.3282,  3.67501,   86.636,  200.069],
            [10.2862,  3.67238,   86.788,  199.786],
            [10.2699,  3.67143,   87.148,  198.941],
            [10.2558,  3.67060,   87.750,  199.079],
            [10.2489,  3.67030,   88.829,  198.049],
            [10.2217,  3.66870,   88.843,  198.044],
            [10.1913,  3.66677,   89.261,  195.529],
            [10.2358,  3.66939,   88.737,  197.619],
            [10.3398,  3.67566,   88.690,  200.492],
            [10.4762,  3.68392,   88.398,  206.102],
            [10.6394,  3.69410,   87.023,  211.766],
            [10.5171,  3.68697,   87.849,  205.337],
            [10.4791,  3.68444,   87.438,  205.091],
            [10.4489,  3.68251,   88.031,  204.360],
            [10.4275,  3.68115,   88.320,  203.623],
            [10.3692,  3.67758,   88.174,  203.001],
            [10.3595,  3.67698,   88.965,  201.765]])

        self.type3_expected = np.array([
            [14.1337,  3.78478,    1.015, 2511, 117, 76],
            [14.0952,  3.79011,    1.002, 2413, 112, 76],
            [14.0918,  3.79235,    1.019, 2280, 112, 75],
            [14.0948,  3.78518,    0.967, 2619, 110, 77],
            [14.0626,  3.78539,    1.024, 2378, 108, 76],
            [14.0687,  3.78741,    0.998, 2462, 110, 75],
            [14.0668,  3.78794,    0.972, 2399, 109, 77],
            [14.0632,  3.78850,    0.985, 2351, 108, 76],
            [14.0486,  3.78639,    0.952, 2222, 107, 75],
            [14.0450,  3.78503,    0.945, 2178, 107, 76],
            [14.0531,  3.78831,    0.969, 2256, 106, 76],
            [14.0594,  3.78848,    0.925, 2346, 107, 76],
            [14.0736,  3.79004,    0.980, 2426, 108, 76],
            [14.0841,  3.79083,    0.994, 2416, 109, 76],
            [14.0268,  3.77012,    1.023, 1299, 101, 74],
            [14.0585,  3.76792,    0.969, 1210, 103, 74],
            [14.0394,  3.71497,    0.971, 1247, 109, 78],
            [14.0520,  3.75194,    1.038, 2130, 115, 76],
            [14.0908,  3.74778,    0.967, 2175, 117, 75],
            [14.0929,  3.73587,    0.988, 1837, 129, 74],
            [14.1403,  3.76612,    0.927, 2006, 125, 74],
            [14.1234,  3.78286,    0.943, 1720, 127, 73],
            [14.1231,  3.78034,    0.958, 1683, 129, 74],
            [14.1303,  3.78248,    0.969, 1897, 129, 75]])

    def test_parse_ctdbp_type1(self):
        '''
        Compare the data parsed from a data log file from a Type 1 CTD to a
        copy/paste/reformat array specified above.

        TODO: Add test for the epoch time stamp
        '''
        self.ctdbp_type1.load_ascii()
        self.ctdbp_type1.parse_data()
        parsed = self.ctdbp_type1.data.toDict()
        
        np.testing.assert_array_equal(parsed['temperature'][:18], self.type1_expected[:, 0])
        np.testing.assert_array_equal(parsed['conductivity'][:18], self.type1_expected[:, 1])
        np.testing.assert_array_equal(parsed['pressure'][:18], self.type1_expected[:, 2])

    def test_parse_ctdbp_type2(self):
        '''
        Compare the data parsed from a data log file from a Type 2 CTD to a
        copy/paste/reformat array specified above.

        TODO: Add test for the epoch time stamp
        '''
        self.ctdbp_type2.load_ascii()
        self.ctdbp_type2.parse_data()
        parsed = self.ctdbp_type2.data.toDict()

        np.testing.assert_array_equal(parsed['temperature'], self.type2_expected[:, 0])
        np.testing.assert_array_equal(parsed['conductivity'], self.type2_expected[:, 1])
        np.testing.assert_array_equal(parsed['pressure'], self.type2_expected[:, 2])
        np.testing.assert_array_equal(parsed['oxygen_concentration'], self.type2_expected[:, 3])

    def test_parse_ctdbp_type3(self):
        '''
        Compare the data parsed from a data log file from a Type 3 CTD to a
        copy/paste/reformat array specified above.

        TODO: Add test for the epoch time stamp
        '''
        self.ctdbp_type3.load_ascii()
        self.ctdbp_type3.parse_data()
        parsed = self.ctdbp_type3.data.toDict()

        np.testing.assert_array_equal(parsed['temperature'], self.type3_expected[:, 0])
        np.testing.assert_array_equal(parsed['conductivity'], self.type3_expected[:, 1])
        np.testing.assert_array_equal(parsed['pressure'], self.type3_expected[:, 2])
        np.testing.assert_array_equal(parsed['raw_backscatter'], self.type3_expected[:, 3])
        np.testing.assert_array_equal(parsed['raw_chlorophyll'], self.type3_expected[:, 4])
        np.testing.assert_array_equal(parsed['raw_cdom'], self.type3_expected[:, 5])


if __name__ == '__main__':       
    unittest.main()

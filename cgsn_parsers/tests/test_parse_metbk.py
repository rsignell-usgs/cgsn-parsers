#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_parse_metbk
@file cgsn_parsers/tests/test_parse_metbk.py
@author Christopher Wingard
@brief Unit tests for parsing the 3 different types of metbk data
"""
import numpy as np
import unittest
from nose.plugins.attrib import attr
from os import path
from cgsn_parsers.parsers.parse_metbk import Parser

# test data file created using chunks of data from various files with the
# different cases of data we might encounter.
TESTDATA = path.join(path.dirname(__file__), 'metbk/metbk.test.dat')


@attr('parse')
class TestParsingUnit(unittest.TestCase):
    '''
    '''
    def setUp(self):
        '''
        '''
        # initialize Parser objects for the metbk types defined above.
        self.metbk = Parser(TESTDATA)
        
        # set the expected output array minus the date/time strings
        self.expected = np.array([
            [1021.22, np.nan, np.nan, 298.2, 14.05, 9.444, 3.1416,   40.0, np.nan, np.nan],
            [1021.49, np.nan, np.nan, 299.8, 14.03, 9.439, 3.1409,   79.6, np.nan, np.nan],
            [1020.94, np.nan, np.nan, 301.1, 14.06, 9.422, 3.1384,   80.2, np.nan, np.nan],
            [1023.22, 62.072,  3.418, 244.3,  4.40, 8.965, 3.0188,    2.1,  -5.38,   2.03],
            [1023.15, 62.969,  3.485, 244.3,  4.29, 8.955, 3.0175,    2.3,  -5.47,   2.48],
            [1023.15, 60.724,  3.380, 245.6,  4.40, 8.955, 3.0161,    2.2,  -5.71,   1.31],
            [1020.12, np.nan, np.nan, 343.5, 14.03, 9.115, 3.0978, np.nan,  -3.23,   4.32],
            [1020.94, np.nan, np.nan, 341.6, 14.01, 9.131, 3.0997, np.nan,  -5.14,   4.22],
            [1020.94, np.nan, np.nan, 338.6, 13.97, 9.132, 3.0997, np.nan,  -4.57,   4.06]])
            
    def test_parse_metbk(self):
        '''
        '''
        self.metbk.load_ascii()
        self.metbk.parse_data()
        parsed = self.metbk.data.toDict()
        
        np.testing.assert_array_equal(parsed['barometric_pressure'], self.expected[:, 0])
        np.testing.assert_array_equal(parsed['relative_humidity'], self.expected[:, 1])
        np.testing.assert_array_equal(parsed['air_temperature'], self.expected[:, 2])
        np.testing.assert_array_equal(parsed['longwave_irradiance'], self.expected[:, 3])
        np.testing.assert_array_equal(parsed['precipitation_level'], self.expected[:, 4])
        np.testing.assert_array_equal(parsed['sea_surface_temperature'], self.expected[:, 5])
        np.testing.assert_array_equal(parsed['sea_surface_conductivity'], self.expected[:, 6])
        np.testing.assert_array_equal(parsed['shortwave_irradiance'], self.expected[:, 7])
        np.testing.assert_array_equal(parsed['eastward_wind_velocity'], self.expected[:, 8])
        np.testing.assert_array_equal(parsed['northward_wind_velocity'], self.expected[:, 9])


if __name__ == '__main__':       
    unittest.main()

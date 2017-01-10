#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_parse_optaa
@file cgsn_parsers/tests/test_parse_optaa.py
@author Christopher Wingard
@brief Unit tests for parsing the OPTAA data
"""
import numpy as np
import unittest
from nose.plugins.attrib import attr
from os import path
from cgsn_parsers.parsers.parse_optaa import Parser

TESTDATA = path.join(path.dirname(__file__), 'optaa/20161001_063017.optaa.log')

@attr('parse')
class TestParsingUnit(unittest.TestCase):
    '''
    OOI Endurance, Pioneer and Global moorings use the WET Labs, Inc., Spectral
    Absorption and Attenuation Sensor (ac-s) for the OPTAA instrument. This 
    unit test will look at the parser output compared to the output from 
    independently developed code created by Steve Lerner and Michael Eder at 
    WHOI.
    '''
    def setUp(self):
        '''
        Using the sample data, initialize the Parser object and set the 
        expected output arrays.
        '''
        # initialize Parser objects for the CTDBP types defined above.
        self.optaa = Parser(TESTDATA)
        
        # set the expected output array for the OPTAA data. Data is from
        # the OPTAA on the NSIF for CE04OSSM-00003, and is copied from the 
        # output for the first 20 packets (drops first packet for some reason).
        # data is further limited to just the initial parameters and the first 
        # 5 wavelengths . 
        self.expected = np.array([
            [0x000102, 0x921a, 0xc08d, 0x000028aa, 86, 1184, 1287, 939, 1252, 1332, 1445, 1087, 1439, 1492, 1618, 1257, 1639, 1667, 1803, 1440, 1854, 1845, 1996, 1640, 2086],
            [0x000102, 0x9219, 0xc08c, 0x000029a2, 86, 1186, 1284, 939, 1253, 1338, 1449, 1093, 1446, 1491, 1619, 1258, 1643, 1663, 1804, 1442, 1861, 1847, 1995, 1644, 2087],
            [0x000102, 0x9218, 0xc08e, 0x00002a9e, 86, 1189, 1284, 936, 1249, 1334, 1440, 1090, 1430, 1491, 1619, 1253, 1637, 1661, 1796, 1436, 1848, 1845, 1996, 1635, 2086],
            [0x000102, 0x9217, 0xc086, 0x00002b9a, 86, 1182, 1280, 933, 1248, 1334, 1446, 1087, 1440, 1495, 1616, 1259, 1640, 1660, 1797, 1435, 1855, 1844, 1997, 1637, 2089],
            [0x000102, 0x9219, 0xc08d, 0x00002c96, 86, 1186, 1284, 938, 1248, 1332, 1439, 1091, 1433, 1493, 1615, 1256, 1637, 1662, 1797, 1441, 1851, 1843, 1993, 1637, 2084],
            [0x000102, 0x9218, 0xc08e, 0x00002d8f, 86, 1182, 1283, 934, 1248, 1329, 1442, 1088, 1433, 1491, 1614, 1254, 1634, 1656, 1799, 1437, 1854, 1841, 1993, 1634, 2084],
            [0x000102, 0x9214, 0xc084, 0x00002e86, 86, 1184, 1284, 939, 1248, 1332, 1442, 1086, 1434, 1491, 1612, 1259, 1633, 1659, 1800, 1437, 1851, 1842, 1994, 1638, 2083],
            [0x000102, 0x9216, 0xc087, 0x00002f7e, 86, 1187, 1279, 938, 1245, 1335, 1445, 1089, 1435, 1492, 1617, 1255, 1637, 1663, 1799, 1440, 1853, 1844, 1990, 1638, 2079],
            [0x000102, 0x9218, 0xc08c, 0x0000307b, 86, 1183, 1287, 933, 1249, 1332, 1441, 1088, 1431, 1488, 1609, 1252, 1629, 1663, 1790, 1439, 1840, 1844, 1989, 1638, 2074],
            [0x000102, 0x9218, 0xc08b, 0x00003179, 86, 1182, 1279, 937, 1247, 1333, 1443, 1088, 1437, 1493, 1612, 1255, 1632, 1662, 1795, 1439, 1848, 1842, 1990, 1637, 2081],
            [0x000102, 0x9216, 0xc08f, 0x00003273, 86, 1183, 1279, 938, 1244, 1329, 1438, 1090, 1427, 1490, 1606, 1257, 1631, 1656, 1791, 1438, 1845, 1843, 1990, 1637, 2079],
            [0x000102, 0x9214, 0xc08e, 0x00003369, 86, 1185, 1282, 939, 1244, 1332, 1435, 1089, 1426, 1488, 1610, 1258, 1633, 1662, 1792, 1438, 1844, 1845, 1984, 1642, 2073],
            [0x000102, 0x9214, 0xc089, 0x00003460, 86, 1182, 1285, 939, 1244, 1334, 1437, 1088, 1428, 1492, 1613, 1258, 1633, 1658, 1799, 1442, 1849, 1839, 1989, 1636, 2077],
            [0x000102, 0x9214, 0xc08d, 0x0000355b, 86, 1183, 1284, 931, 1247, 1333, 1439, 1084, 1429, 1491, 1609, 1255, 1632, 1661, 1791, 1435, 1844, 1849, 1988, 1636, 2076],
            [0x000102, 0x9214, 0xc088, 0x00003657, 86, 1183, 1282, 934, 1247, 1329, 1434, 1081, 1425, 1494, 1606, 1249, 1625, 1662, 1787, 1434, 1841, 1842, 1988, 1628, 2077],
            [0x000102, 0x9216, 0xc08c, 0x00003753, 86, 1186, 1281, 938, 1244, 1331, 1437, 1089, 1429, 1489, 1607, 1255, 1627, 1659, 1788, 1441, 1840, 1842, 1988, 1634, 2074],
            [0x000102, 0x9214, 0xc08c, 0x0000384d, 86, 1183, 1277, 936, 1241, 1327, 1437, 1084, 1428, 1492, 1606, 1256, 1627, 1659, 1789, 1440, 1841, 1837, 1986, 1636, 2073],
            [0x000102, 0x9213, 0xc08c, 0x00003946, 86, 1182, 1278, 936, 1241, 1328, 1435, 1087, 1426, 1488, 1607, 1253, 1627, 1657, 1789, 1435, 1840, 1837, 1985, 1635, 2072],
            [0x000102, 0x9216, 0xc08e, 0x00003a3f, 86, 1185, 1277, 937, 1240, 1328, 1430, 1086, 1420, 1487, 1611, 1253, 1629, 1659, 1786, 1437, 1838, 1838, 1983, 1637, 2069],
            [0x000102, 0x9218, 0xc089, 0x00003b38, 86, 1182, 1278, 932, 1244, 1324, 1438, 1084, 1429, 1491, 1610, 1250, 1629, 1657, 1792, 1435, 1844, 1835, 1988, 1633, 2076]
        ])
        

    def test_parse_optaa(self):
        '''
        Compare the data parsed from a data log file from a Type 1 CTD to a
        copy/paste/reformat array specified above.

        TODO: Add test for the epoch time stamp
        '''
        self.optaa_type1.load_ascii()
        self.optaa_type1.parse_data()
        parsed = self.optaa_type1.data.toDict()
        
        np.testing.assert_array_equal(parsed['temperature'][:18], self.type1_expected[:, 0])
        np.testing.assert_array_equal(parsed['conductivity'][:18], self.type1_expected[:, 1])
        np.testing.assert_array_equal(parsed['pressure'][:18], self.type1_expected[:, 2])

if __name__ == '__main__':       
    unittest.main()

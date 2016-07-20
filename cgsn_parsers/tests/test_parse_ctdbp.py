#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_parse_ctdbp
@file cgsn_parsers/tests/test_parse_ctdbp.py
@author Christopher Wingard
@brief Sets up the unit tests for parsing the 3 different types of CTDBP data
"""
import numpy as np
from nose.plugins.attrib import attr
from cgsn_parsers.test.test_common import BaseUnitTestCase
from cgsn_parsers.parsers.parse_ctdbp import Parser


@attr('UNIT', group='func')
class TestParsingUnit(BaseUnitTestCase):
    '''
    OOI Endurance and Pioneer moorings use the Sea-Bird Electronics 16Plus V2
    CTDs on the NSIF and MFN frames configured in one of 3 ways. All units are
    set to report conductivity, temperature and pressure in engineering units.

    On the NSIF, for the CSMs, the CTD is programmed to output a measurement
    every 10 s for 3 minutes every 15 minutes. Pioneer moorings configure the
    CTD on the MFN in the same way. This is CTDBP Type 1.

    On the NSIF, for the Endurance ISSM, the CTD includes an Aanderaa Optode
    4831 measurement (reports O2 concentration in uMol/L). The units are
    programmed to autonomously record a 10 s averaged measurement every 15
    minutes in addition to being polled (via the TS command) every hour at the
    bottom of the hour. The 4 Endurance MFN units are programmed the same way.
    This is CTDBP Type 2.

    On the buoy instrument frame (approximately 1 m below the surface), for the
    Endurance ISSM, the CTD includes a WET Labs ECO Triplet (FLORT) fluorometer
    measuring chlorohyll and CDOM fluroescence and optical backscatter (values
    are reported in counts). The units are programmed to autonomously record a
    10 s averaged measurement every 30 minutes in addition to being polled (via
    the TS command) every hour at the bottom of the hour. This is CTDBP Type 3.

    This test class will parse and compare the outputs from all three types of
    CTDBPs to confirm the parser functions as expected.
    '''
    def setUp(self):
        '''
        '''
        pass

    def parse_ctdbp_type1(self):
        '''
        '''
        return False

    def parse_ctdbp_type2(self):
        '''
        '''
        return False

    def parse_ctdbp_type3(self):
        '''
        '''
        return False

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_common
@file cgsn_parsers/tests/test_common.py
@author Christopher Mueller
@brief Sets up the unit tests and provides basic common functions
"""
from unittest import TestCase


class BaseUnitTestCase(TestCase):
    # Prevent test docstring from printing - uses test name instead
    # see http://www.saltycrane.com/blog/2012/07/how-prevent-nose-unittest-using-docstring-when-verbosity-2/
    def shortDescription(self):
        return None

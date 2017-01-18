#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.process.proc_pco2w
@file cgsn_parsers/process/proc_pco2w.py
@author Christopher Wingard
@brief Calculate the pCO2 of water from the SAMI2-pCO2 (PCO2W) instrument
'''
import cPickle as pickle
import json
import numpy as np
import os
import pandas as pd

from datetime import datetime, timedelta
from munch import Munch
from pytz import timezone

from cgsn_parsers.parsers.common import dcl_to_epoch
from cgsn_parsers.process.common import Coefficients, inputs
from ion_functions.data.co2_functions import pco2_blank, pco2_pco2wat
from ion_functions.data.ph_functions import ph_thermistor, ph_battery

class Blanks(object):
    '''
    Serialized object used to store the PCO2W absorbance blanks used in the 
    calculations of the pCO2 of seawater from a Sunburst Sensors, SAMI2-pCO2
    '''
    def __init__(self, blnkfile, blank_434, blank_620):
        # initialize the information needed to define the blanks cPickle file
        # and the blanks        
        self.blnkfile = blnkfile;
        self.blank_434 = blank_434
        self.blank_620 = blank_620
    
    def load_blanks(self):
        # load the cPickled blanks dictionary
        with open(self.blnkfile, 'rb') as f:
            blank = pickle.load(f)

        # assign the blanks
        self.blank_434 = blank['434']
        self.blank_620 = blank['620']
        
    def save_blanks(self):
        # create the blanks dictionary        
        blank = {}
        blank['434'] = self.blank_434
        blank['620'] = self.blank_620
        
        # save the cPickled blanks dictionary
        with open(self.blnkfile, 'wb') as f:
            pickle.dump(blank, f)

            
class Calibrations(Coefficients):
    def __init__(self, coeff_file, csv_url=None):
        '''
        Loads the calibration coefficients for a unit. Values come from either
        a serialized object created per instrument and deployment (calibration 
        coefficients do not change in the middle of a deployment), or from 
        parsed CSV files maintained on GitHub by the OOI CI team.
        '''        
        # assign the inputs
        Coefficients.__init__(self, coeff_file)
        self.csv_url = csv_url

    def read_csv(self, csv_url):
        '''
        Reads the values from the CSV file already parsed and stored on Github.
        Note, the formatting of those files puts some constraints on this 
        process. If someone has a cleaner method, I'm all in favor...
        '''
        # create the device file dictionary and assign values
        coeffs = {}
        
        # read in the calibration data
        data = pd.read_csv(csv_url, usecols=[0,1,2])
        for idx, row in data.iterrows():
            if row[1] == 'CC_cala': coeffs['cala'] = np.float(row[2])
            if row[1] == 'CC_calb': coeffs['calb'] = np.float(row[2])
            if row[1] == 'CC_calc': coeffs['calc'] = np.float(row[2])
            if row[1] == 'CC_calt': coeffs['calt'] = np.float(row[2])

        # serial number, stripping off all but the numbers
        coeffs['serial_number'] = data.serial[0]

        # save the resulting dictionary
        self.coeffs = coeffs


if __name__ == '__main__':
    # load  the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)
    coeff_file = os.path.abspath(args.coeff_file)
    blnk_file = os.path.abspath(args.devfile)
        
    # check for the source of calibration coeffs and load accordingly
    dev = Calibrations(coeff_file)  # initialize calibration class
    if os.path.isfile(coeff_file):
        # we always want to use this file if it exists
        dev.load_coeffs()
    elif args.csvurl:
        # load from the CI hosted CSV files
        csv_url = args.csvurl
        dev.read_csv(csv_url)
        dev.save_coeffs()
    else:
        raise Exception('A source for the PCO2W calibration coefficients could not be found')

    # check for the source of instrument blanks and load accordingly
    blank = Blanks(blnk_file, 1.0, 1.0) # initialize the calibration class
    if os.path.isfile(blnk_file):
        blank.load_blanks()
    else:
        blank.save_blanks()
        
    # load the PCO2W data file
    with open(infile, 'rb') as f:
        pco2w = Munch(json.load(f))

    # convert the raw battery voltage and thermistor values from counts
    # to V and degC, respectively
    pco2w.thermistor = ph_thermistor(np.array(pco2w.thermistor_raw)).tolist()
    pco2w.voltage_battery = ph_battery(np.array(pco2w.voltage_battery)).tolist()

    # compare the instrument clock to the GPS based DCL time stamp
    # --> PCO2W uses the OSX date format of seconds since 1904-01-01
    mac = datetime.strptime("01-01-1904", "%m-%d-%Y")
    offset = []
    for i in range(len(pco2w.time)):
        rec = mac + timedelta(seconds=pco2w.record_time[i])
        rec.replace(tzinfo=timezone('UTC'))
        dcl = datetime.utcfromtimestamp(pco2w.time[i])
        
        # we use the sample collection time as the time record for the sample.
        # the record_time, however, is when the sample was processed. so the
        # true offset needs to include the difference between the collection
        # and processing times
        collect = dcl_to_epoch(pco2w.collect_date_time[i])
        process = dcl_to_epoch(pco2w.process_date_time[i])
        diff = process - collect
        if np.isnan(diff):
            diff = 300
        offset.append((rec - dcl).total_seconds() - diff)

    pco2w.time_offset = offset

    # set calibration inputs to pCO2 calculations
    ea434 = 19706.   # factory constants
    eb434 = 3073.    # factory constants
    ea620 = 34.      # factory constants
    eb620 = 44327.   # factory constants

    # calculate pCO2
    pCO2 = []
    blank434 = []
    blank620 = []

    for i in range(len(pco2w.record_type)):
        if pco2w.record_type[i] == 4:
            # this is a light measurement, calculate the pCO2
            pCO2.append(pco2_pco2wat(pco2w.record_type[i],
                                     pco2w.light_measurements[i],
                                     pco2w.thermistor[i],
                                     ea434, eb434, ea620, eb620,
                                     dev.coeffs['calt'], 
                                     dev.coeffs['cala'],
                                     dev.coeffs['calb'],
                                     dev.coeffs['calc'],
                                     blank.blank_434,
                                     blank.blank_620))

            # record the blanks used
            blank434.append(blank.blank_434)
            blank620.append(blank.blank_620)

        if pco2w.record_type[i] == 5:
            # this is a dark measurement, update and save the new blanks
            blank.blank_434 = pco2_blank(pco2w.light_measurements[i][6])
            blank.blank_620 = pco2_blank(pco2w.light_measurements[i][7])
            blank.save_blanks()

            blank434.append(blank.blank_434)
            blank620.append(blank.blank_620)


    # save the resulting data to a json formatted file
    pco2w.pCO2 = pCO2
    pco2w.blank434 = blank434
    pco2w.blank620 = blank620

    with open(outfile, 'w') as f:
        f.write(pco2w.toJSON())

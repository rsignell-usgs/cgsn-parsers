#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package level2.level2_pco2w
@file level2/level2_pco2w.py
@author Christopher Wingard
@brief Combines the PCO2W and co-located CTDBP data to calculate pH.
'''
import argparse
import cPickle as pickle
import numpy as np
import os
import scipy.io as sio

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from calendar import timegm
from datetime import datetime, timedelta
from pytz import timezone

from parsers.common import dcl_to_epoch
from ion_functions.data.co2_functions import pco2_blank, pco2_pco2wat
from ion_functions.data.ph_functions import ph_thermistor, ph_battery


class blanks(object):
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


class calibrations(object):
    def __init__(self, coeff_file, cal_sheet, serial_num):
        '''
        Loads the calibration coefficients for a unit based on its serial
        number. Values come from either the Google Spreadsheet, or a serialized
        object created per instrument and deployment (calibration coefficients
        do not change in the middle of a deployment).
        '''        
        # assign the inputs
        self.coeff_file = coeff_file
        self.cal_sheet = cal_sheet
        self.serial_num = serial_num

    def load_spread(self, record_date):
        '''
        Obtain the calibration data for this instrument from the Google Docs
        spreadsheet
        '''
        # register the credentials and create the google spread sheet object
        jcreds = os.path.join(os.getenv('HOME'), '.google/ooice_platforms-a4d38f09c7cc.json')
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(jcreds, scope)
        gc = gspread.authorize(credentials)

        # open the sheet and obtain all the values for this unit
        sheet = gc.open(self.cal_sheet).worksheet('Sheet1')
        rc = sheet.findall(self.serial_num)
        values = []
        for r in rc:
            values.append(sheet.row_values(r.row))

        # now that we have the values for this unit, we need to find the data
        # that occurs closest in time to before the start of a deployment.
        tdiff = []
        for r in values:
            # convert the calibration date to an epoch timestamp
            cal = datetime.strptime('%s 00:00' % r[1], '%Y-%m-%d %H:%M')
            cal.replace(tzinfo=timezone('UTC'))
            cal = timegm(cal.timetuple())
            
            # calculate the difference between the record time and the 
            # calibration date
            tdiff.append(round(cal - record_date))

        # create a dictionary with the coeffs
        coeffs = {}
        indx = np.min(np.where(np.array(tdiff) <= 0.0))
        coeffs['serial_num'] = values[indx][0]
        coeffs['cal_date'] = values[indx][1]
        coeffs['coeff_a'] = values[indx][2]
        coeffs['coeff_b'] = values[indx][3]
        coeffs['coeff_c'] = values[indx][4]
        coeffs['cal_t'] = values[indx][5]
        self.coeffs = coeffs

    def load_coeffs(self):
        '''
        Obtain the calibration data for this instrument from the Google Docs
        spreadsheet
        '''
        # load the cPickled blanks dictionary
        with open(self.coeff_file, 'rb') as f:
            coeffs = pickle.load(f)

        self.coeffs = coeffs

    def save_coeffs(self):
        '''
        Obtain the calibration data for this instrument from the Google Docs
        spreadsheet
        '''
        # save the cPickled blanks dictionary
        with open(self.coeff_file, 'wb') as f:
            pickle.dump(self.coeffs, f)

def inputs():
    '''
    Sets the main input arguments for the PCO2W L2 processor. File names should
    include pathnames (which can be relative). The key inputs are the PCO2W L1 
    dataset and the co-located CTDBP L1 dataset. If the CTDBP data file is not
    available, a default salinity value of 33 will be used.  
    '''
    # initialize arguement parser
    parser = argparse.ArgumentParser(description='''Calculate the pCO2 values
                                     for the current data file''',
                                     epilog='''Calculate pCO2''')

    # assign arguements for the infile and outfile and a switch that can be
    # used, if needed, to set different options (e.g. if switch == 1, do this
    # or that).
    parser.add_argument("-i", "--infile", dest="infile", type=str, required=True)
    parser.add_argument("-o", "--outfile", dest="outfile", type=str, required=True)
    parser.add_argument("-b", "--blnkfile", dest="blnkfile", type=str, required=True)
    parser.add_argument("-c", "--calfile", dest="calfile", type=str, required=True)
    parser.add_argument("-s", "--serial", dest="serial", type=str, required=True)

    # parse the input arguements and create a parser object
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    # load  the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)
    blnkfile = os.path.abspath(args.blnkfile)
    calfile = os.path.abspath(args.calfile)
    snum = args.serial
    
    # load the PCO2W data file
    pco2w = sio.loadmat(infile, struct_as_record=False, squeeze_me=True)

    # convert the raw battery voltage and thermistor values from counts
    # to V and degC, respectively
    pco2w['thermistor'] = ph_thermistor(pco2w['thermistor_raw'])
    pco2w['voltage_battery'] = ph_battery(pco2w['voltage_battery'])

    # compare the instrument clock to the GPS based DCL time stamp
    # --> PCO2W uses the OSX date format of seconds since 1904-01-01
    mac = datetime.strptime("01-01-1904", "%m-%d-%Y")
    offset = []
    for i in range(len(pco2w['time'])):
        rec = mac + timedelta(seconds=pco2w['record_time'][i])
        rec.replace(tzinfo=timezone('UTC'))
        dcl = datetime.utcfromtimestamp(pco2w['time'][i])
        
        # we use the sample collection time as the time record for the sample.
        # the record_time, however, is when the sample was processed. so the
        # true offset needs to include the difference between the collection
        # and processing times
        collect = dcl_to_epoch(pco2w['collect_date_time'][i])
        process = dcl_to_epoch(pco2w['process_date_time'][i])
        diff = process - collect
        if np.isnan(diff):
            diff = 300
        offset.append((rec - dcl).total_seconds() - diff)

    pco2w['time_offset'] = offset

    # clean up the dictionary, removing elements not used in further processing
    pco2w.pop("collect_date_time", None)
    pco2w.pop("process_date_time", None)
    pco2w.pop("thermistor_raw", None)
    pco2w.pop("record_length", None)
    pco2w.pop("unique_id", None)

    # initialize the blanks class and either load the blanks or assign default
    # values to the blanks
    blank = blanks(blnkfile, 1.0, 1.0)
    if os.path.exists(blnkfile):
        blank.load_blanks()
    else:
        blank.save_blanks()

    # load the calibration coefficients for this unit
    cals = calibrations(calfile, 'pco2w_calibration_records', snum)
    if os.path.exists(calfile):
        cals.load_coeffs()
    else:
        cals.load_spread(pco2w['time'][0])
        cals.save_coeffs()

    # set calibration inputs to pCO2 calculations
    ea434 = 19706.   # factory constants
    eb434 = 3073.    # factory constants
    ea620 = 34.      # factory constants
    eb620 = 44327.   # factory constants
    cala = float(cals.coeffs['coeff_a'])
    calb = float(cals.coeffs['coeff_b'])
    calc = float(cals.coeffs['coeff_c'])
    calt = float(cals.coeffs['cal_t'])
    
    # calculate pCO2
    pco2w['pCO2'] = []
    pco2w['blank434'] = []
    pco2w['blank620'] = []
    
    for i in range(len(pco2w['record_type'])):
        if pco2w['record_type'][i] == 4:
            # this is a light measurement, calculate the pCO2
            pco2w['pCO2'].append(pco2_pco2wat(pco2w['record_type'][i],
                                              pco2w['light_measurements'][i],
                                              pco2w['thermistor'][i],
                                              ea434, eb434, ea620, eb620,
                                              calt, cala, calb, calc,
                                              blank.blank_434,
                                              blank.blank_620))

            # record the blanks used
            pco2w['blank434'].append(blank.blank_434)
            pco2w['blank620'].append(blank.blank_620)

        if pco2w['record_type'][i] == 5:           
            # update and save the new blanks
            blank.blank_434 = pco2_blank(pco2w['light_measurements'][i][6])
            blank.blank_620 = pco2_blank(pco2w['light_measurements'][i][7])
            blank.save_blanks()

            pco2w['blank434'].append(blank.blank_434)
            pco2w['blank620'].append(blank.blank_620)

    pco2w['record_type']

    # save the resulting data file
    sio.savemat(outfile, pco2w)

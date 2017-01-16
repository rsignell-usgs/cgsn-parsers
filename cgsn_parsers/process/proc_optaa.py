#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.process.proc_optaa
@file cgsn_parsers/process/proc_optaa
@author Christopher Wingard with inspiration and guidance from Russell Desiderio
@brief Reads in the parsed OPTAA data and applies the calibration, temperature,
    salinity and scattering corrections to the data, saving the resulting data  
'''
import json
import numpy as np
import os
import pandas as pd
import re
import requests
import scipy.interpolate as sci
import scipy.io as sio

from cgsn_parsers.process.common import Coefficients, inputs
from ion_functions.data.opt_functions import opt_internal_temp, opt_external_temp
from ion_functions.data.opt_functions import opt_pressure, opt_pd_calc, opt_tempsal_corr


class Calibrations(Coefficients):
    def __init__(self, coeff_file, dev_file=None, hdr_url=None, tca_url=None, tcc_url=None):
        '''
        Loads the OPTAA factory calibration coefficients for a unit. Values 
        come from either a serialized object created per instrument and 
        deployment (calibration coefficients do not change in the middle of a
        deployment), from the factory supplied device file, or from parsed
        CSV files maintained on GitHub by the OOI CI team.
        '''        
        # assign the inputs
        Coefficients.__init__(self, coeff_file)
        self.dev_file = dev_file
        self.hdr_url = hdr_url
        self.tca_url = tca_url
        self.tcc_url = tcc_url

    def read_devfile(self, dev_file):
        '''
        Reads the values from an ac-s device file into a python dictionary.
        '''
        # read in the device file
        with open(dev_file, 'rb') as f:
            data = f.readlines()
    
        # create the coefficients dictionary and assign values
        coeffs = {}
        
        ### assign values from the header portion of the device file
        # serial number, assuming they never go above 4096...
        coeffs['serial_number'] = np.mod(np.int(data[1].split()[0], 16), 4096)
        # temperature of calibration water
        coeffs['temp_calibration'] = np.float(data[3].split()[1])
        # offset and slope pressure coefficients (0 if not present)
        coeffs['pressure_coeff'] = np.array(data[4].split()[0:2]).astype(np.float)
        # pathlength (always 0.25 m)
        coeffs['pathlength'] = np.float(data[6].split()[0])
        # number of wavelengths
        coeffs['num_wavelengths'] = np.int(data[7].split()[0])
        # number of internal temperature compensation bins
        nbin = np.int(data[8].split()[0])
        coeffs['num_temp_bins'] = nbin
        # array of the temperatures for the bins
        coeffs['temp_bins'] = np.array(data[9].split()[:-3]).astype(np.float)
    
        ### assign values from the array portion of the file
        awvl = []
        cwvl = []
        aoff = []
        coff = []
        ta_array = []
        tc_array = []
        for line in data[10:-1]:
            line = line.split()
            cwvl.append(np.float(re.sub('C', '', line[0])))
            awvl.append(np.float(re.sub('A', '', line[1])))
            coff.append(np.float(line[3]))
            aoff.append(np.float(line[4]))
            tc_array.append(np.array(line[5:5+nbin]).astype(np.float))
            ta_array.append(np.array(line[nbin+5:-12]).astype(np.float))
            
        # beam attenuation and absorption channel wavelengths
        coeffs['c_wavelengths'] = np.array(cwvl)
        coeffs['a_wavelengths'] = np.array(awvl)
        # beam attenuation and absorption channel clear water offsets
        coeffs['c_offsets'] = np.array(coff)
        coeffs['a_offsets'] = np.array(aoff)
        # temperature compensation values as f(wavelength, temperature) for the
        # beam attenuation and absorption channels
        coeffs['tc_array'] = np.array(tc_array)
        coeffs['ta_array'] = np.array(ta_array)
        
        # save the resulting dictionary
        self.coeffs = coeffs
    
    def read_devurls(self, hdr_url, tca_url, tcc_url):
        '''
        Reads the values from an ac-s device file already parsed and stored on
        Github as a set of 3 CSV files. Note, the formatting of those files 
        puts some constraints on this process. If someone has a cleaner method,
        I'm all in favor...
        '''
        # create the device file dictionary and assign values
        coeffs = {}
        
        # read in the mostly header portion of the calibration data
        hdr = pd.read_csv(hdr_url, usecols=[0,1,2])
        for idx, row in hdr.iterrows():
            # beam attenuation and absorption channel clear water offsets
            if row[1] == 'CC_acwo': coeffs['a_offsets'] = np.array(json.loads(row[2]))
            if row[1] == 'CC_ccwo': coeffs['c_offsets'] = np.array(json.loads(row[2]))
            # beam attenuation and absorption channel wavelengths
            if row[1] == 'CC_awlngth': coeffs['a_wavelengths'] = np.array(json.loads(row[2]))
            if row[1] == 'CC_cwlngth': coeffs['c_wavelengths'] = np.array(json.loads(row[2]))
            # internal temperature compensation values
            if row[1] == 'CC_tbins': coeffs['temp_bins'] = np.array(json.loads(row[2]))
            # temperature of calibration water
            if row[1] == 'CC_tcal': coeffs['temp_calibration'] = np.float(row[2])

        # serial number, stripping off all but the numbers
        coeffs['serial_number'] = np.int(re.sub('[^0-9]','', hdr.serial[0]))
        # number of wavelengths
        coeffs['num_wavelengths'] = len(coeffs['a_wavelengths'])
        # number of internal temperature compensation bins
        coeffs['num_temp_bins'] = len(coeffs['temp_bins'])
        # pressure coefficients, set to 0 since not included in the CI csv files
        coeffs['pressure_coeff'] = [0, 0]

        # temperature compensation values as f(wavelength, temperature) for the
        # beam attenuation and absorption channels
        ta_array = []
        tc_array = []

        tcc = requests.get(tcc_url)
        for line in tcc.content.splitlines():
            tc_array.append(np.array(line.split(',')).astype(np.float))

        tca = requests.get(tca_url)
        for line in tca.content.splitlines():
            ta_array.append(np.array(line.split(',')).astype(np.float))

        coeffs['tc_array'] = tc_array
        coeffs['ta_array'] = ta_array
        
        # save the resulting dictionary
        self.coeffs = coeffs
    
def apply_dev(optaa, coeffs):
    '''
    Processes the raw data contained in the optaa dictionary and applies the 
    factory calibration coefficents contained in the coeffs dictionary to
    convert the data into initial science units.
    '''
    # convert internal and external temperature sensors
    optaa['internal_temp'] = opt_internal_temp(optaa['internal_temp_raw'])
    optaa['external_temp'] = opt_external_temp(optaa['external_temp_raw'])

    # pressure
    if np.all(coeffs['pressure_coeff']==0):
        # do not use None, which will cause sio.savemat to croak.
        optaa['pressure'] = np.NaN * optaa['pressure_raw']
    else:
        offset = coeffs['pressure_coeff'][0]
        slope = coeffs['pressure_coeff'][1]
        optaa['pressure'] = opt_pressure(optaa['pressure_raw'], offset, slope)
    
    # calculate the L1 OPTAA data products (uncorrected beam attenuation and 
    # absorbance) for particulates and dissolved organic matter with clear
    # water removed.
    optaa['a_pd'] = opt_pd_calc(optaa['a_reference_raw'], optaa['a_signal_raw'],
        coeffs['a_offsets'], optaa['internal_temp'], coeffs['temp_bins'],
        coeffs['ta_array'])
    optaa['c_pd'] = opt_pd_calc(optaa['c_reference_raw'], optaa['c_signal_raw'],
        coeffs['c_offsets'], optaa['internal_temp'], coeffs['temp_bins'],
        coeffs['tc_array'])

    # add the beam attenuation and absorbance wavelengths to the data.
    optaa['c_wavelengths'] = coeffs['c_wavelengths']
    optaa['a_wavelengths'] = coeffs['a_wavelengths']

    # return the optaa dictionary with the factory calibrations applied
    return optaa

def apply_tscorr(optaa, coeffs, Temp=None, Salinity=None):
    '''
    Corrects the absorption and beam attenuation data for the absorption
    of seawater as a function of seawater temperature and salinity (the
    calibration blanking offsets are determined using pure water.)
    
    If inputs Temp or Salinity are not supplied as calling arguments, then the 
    following default values are used.
        
        Temp: temperature values recorded by the ac-s's external thermistor.
        Salinity: 33.0 psu

    Otherwise, each of the arguments for Temp and Salinity should be either a 
    scalar, or a 1D array or row or column vector with the same number of time
    points as 'a' and 'c'.
    '''
    # setup the temperature and salinity arrays
    if Temp is None:
        Temp = optaa['external_temp'][:, np.newaxis]
    else: 
        if np.array(Temp).size != 1:
            Temp = Temp.flatten()[:, np.newaxis]
    
    if Temp.size != optaa['time'].size:
        raise Exception("Mismatch: Temperature array != number of OPTAA measurements")

    if Salinity is None:
        Salinity = 33.0
    else:
        if np.array(Salinity).size != 1:
            Salinity = Salinity.flatten()[:, np.newaxis]
    
    if Salinity.size != optaa['time'].size:
        raise Exception("Mismatch: Salinity array != number of OPTAA measurements")

    optaa['a_pd_ts'] = opt_tempsal_corr('a', optaa['a_pd'], optaa['a_wavelengths'], 
        coeffs['temp_calibration'], Temp, Salinity)
    optaa['c_pd_ts'] = opt_tempsal_corr('c', optaa['c_pd'], optaa['c_wavelengths'], 
        coeffs['temp_calibration'], Temp, Salinity)
    
    return optaa

def apply_scatcorr(optaa, method=1):
    """
    Correct the absorbance data for scattering using Method 1 (the default),
    with 715 nm used as the scattering wavelength.
    """
    reference_wavelength = 715.0

    if method != 1:
        raise Exception('Only scatter method = 1 is coded for the time being.')

    a_interpolant = sci.interp1d(optaa['a_wavelengths'], optaa['a'])

    optaa['a_scatter_artifact'] = a_interpolant(reference_wavelength)
    optaa['a_pd_ts_s'] = optaa['a'] - optaa['a_scatter_artifact'][:, np.newaxis]

    return optaa

if __name__ == '__main__':
    # usage: l2_optaa.py -i INFILE -o OUTFILE -d DEVFILE
    # load  the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    devfile = os.path.abspath(args.devfile)

    # load L1 data
    optaa = sio.loadmat(infile, struct_as_record=False, squeeze_me=True)
    optaa['datafile'] = infile

    # read in the devfile info
    dev = read_acs_devfile(args.devfile)

    # compatibility checks
    if dev['serial_number'] != optaa0['serial_number'][0].astype(int):
        raise Exception('Serial Number mismatch between ac-s data and devfile.')
    if dev['number_of_wavelengths'] != optaa0['number_of_wavelengths'][0]:
        raise Exception('Number of wavelengths mismatch between ac-s data and devfile.')

    optaa1 = apply_acs_devfile_to_rawdata(optaa0, dev)
    optaa2 = apply_TS_corrections(optaa1, None, 33.0)
    optaa = apply_scatter_correction(optaa2, 1)

    # save the resulting data file
    sio.savemat(outfile, optaa)
    
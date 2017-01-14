#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.process.proc_optaa
@file cgsn_parsers/process/proc_optaa
@author Christopher Wingard with inspiration and guidance from Russell Desiderio
@brief Reads in the parsed OPTAA data and applies the calibration, temperature,
    salinity and scattering corrections to the data, saving the resulting data  
'''
import argparse
import csv
import numpy as np
import os
import re
import requests

from contextlib import closing

import scipy.interpolate as sci

from ion_functions.data.opt_functions_tscor import tscor

def read_devfile(dev_file):
    '''
    Reads the values from an ac-s device file into a python dictionary.
    '''
    # read in the device file
    with open(dev_file, 'rb') as f:
        data = f.readlines()

    # create the device file dictionary and assign values
    dev = {}
    
    ### assign values from the header portion of the device file
    # serial number, assuming they never go above 4096...
    dev['serial_number'] = np.mod(np.int(data[1].split()[0], 16), 4096)
    # temperature of calibration water
    dev['temp_calibration'] = np.float(data[3].split()[1])
    # offset and slope pressure coefficients (0 if not present)
    dev['pressure_coeff'] = np.array(data[4].split()[0:2]).astype(np.float)
    # pathlength (always 0.25 m)
    dev['pathlength'] = np.float(data[6].split()[0])
    # number of wavelengths
    dev['num_wavelengths'] = np.int(data[7].split()[0])
    # number of internal temperature compensation bins
    nbin = np.int(data[8].split()[0])
    dev['num_temp_bins'] = nbin
    # array of the temperatures for the bins
    dev['temp_bins'] = np.array(data[9].split()[:-3]).astype(np.float)

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
    dev['c_wavelengths'] = np.array(cwvl)
    dev['a_wavelengths'] = np.array(awvl)
    # beam attenuation and absorption channel offsets
    dev['c_offsets'] = np.array(coff)
    dev['a_offsets'] = np.array(aoff)
    # temperature compensation values as f(wavelength, temperature) for the
    # beam attenuation and absorption channels
    dev['tc_array'] = np.array(tc_array)
    dev['ta_array'] = np.array(ta_array)
    
    # return the resulting dictionary
    return dev

def read_devurl(dev_url):
    '''
    Reads the values from an ac-s device file already parsed and stored on
    Github as a set of 3 csv files.
    '''
    # read in the device file
    with closing(requests.get(dev_url, stream=True)) as r:
        reader = csv.reader(r.iter_lines(), delimiter=',', quotechar='"')
        for row in reader:
            # Handle each row here...
            print row   
    
    # create the device file dictionary and assign values
    dev = {}
    
    ### assign values from the header portion of the device file
    # serial number, assuming they never go above 4096...
    dev['serial_number'] = np.mod(np.int(data[1].split()[0], 16), 4096)
    # temperature of calibration water
    dev['temp_calibration'] = np.float(data[3].split()[1])
    # offset and slope pressure coefficients (0 if not present)
    dev['pressure_coeff'] = np.array(data[4].split()[0:2]).astype(np.float)
    # pathlength (always 0.25 m)
    dev['pathlength'] = np.float(data[6].split()[0])
    # number of wavelengths
    dev['num_wavelengths'] = np.int(data[7].split()[0])
    # number of internal temperature compensation bins
    nbin = np.int(data[8].split()[0])
    dev['num_temp_bins'] = nbin
    # array of the temperatures for the bins
    dev['temp_bins'] = np.array(data[9].split()[:-3]).astype(np.float)

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
    dev['c_wavelengths'] = np.array(cwvl)
    dev['a_wavelengths'] = np.array(awvl)
    # beam attenuation and absorption channel offsets
    dev['c_offsets'] = np.array(coff)
    dev['a_offsets'] = np.array(aoff)
    # temperature compensation values as f(wavelength, temperature) for the
    # beam attenuation and absorption channels
    dev['tc_array'] = np.array(tc_array)
    dev['ta_array'] = np.array(ta_array)
    
    # return the resulting dictionary
    return dev
    
    
    
def apply_acs_devfile_to_rawdata(optaa_in, devdata):
    """
    # processes raw acs data contained in the dictionary optaa and applies
    # the factory cal coeffs contained in the dictionary devdata to convert
    # the data into science units.
    """
    optaa = optaa_in.copy()
    # constants for processing acs thermistor data
    # internal temperature
    a_int = 0.00093135
    b_int = 0.000221631
    c_int = 0.000000125741
    # external temperature
    a_ext = -7.1023317e-13
    b_ext =  7.09341920e-8
    c_ext = -3.87065673e-3
    d_ext = 95.8241397
    # internal temperature for temperature compensation processing:
    inttemp_vlt = 5.0 * optaa['raw_internal_temperature_counts'] / 65535.0
    ln_inttemp_ohm = np.log(10000.0 * inttemp_vlt / (4.516 - inttemp_vlt))
    denominator = a_int + b_int * ln_inttemp_ohm + c_int * ln_inttemp_ohm**3
    inttemp = 1.0 / denominator - 273.15
    # external temperature (horner's method for calculating polynomials):
    x = optaa['raw_external_temperature_counts']
    exttemp = d_ext + x * (c_ext + x * (b_ext + x * a_ext))
    # pressure
    if np.all(devdata['pressure_sensor_coefficients']==0):
        # do not use None, which will cause sio.savemat to croak.
        acs_pressure = np.NaN * optaa['pressure_counts']
    else:
        offset = devdata['pressure_sensor_coefficients'][0]
        slope = devdata['pressure_sensor_coefficients'][1]
        acs_pressure = offset + optaa['pressure_counts'] * slope
    
    # figure internal temperature corrections for both optical channels.
    #
    # bin_temperatures.shape = (number_of_temperature_bins,)
    # c_temperature_compensation_array.shape = (number_of_wavelengths,
    #                                        number_of_temperature_bins)
    #
    # by default scipy interpolates along the last axis of the 2nd argument,
    # so that:
    #     delta_c.shape = (number_of_wavelengths, inttemp.size)
    #     where inttemp.size signifies the number of time points.
    c_interpolant = sci.interp1d(devdata['bin_temperatures'],
                                 devdata['c_temperature_compensation_array'])
    delta_c = c_interpolant(inttemp)
    a_interpolant = sci.interp1d(devdata['bin_temperatures'],
                                 devdata['a_temperature_compensation_array'])
    delta_a = a_interpolant(inttemp)
    # calculate abs and beam c values,
    # un-corrected for the temperature and salinity of the seawater.
    #     (a) the delta arrays must be transposed to match the dimensions
    #         of the counts variables (first dimension is time, second is
    #         wavelength).
    #     (b) python correctly broadcasts the values of the 1D variable
    #         Offsets into 2D to match the dimensions of the 2D variables. 
    #     (c) avoid a type integer divide which would result in log(0).    
    beamc = devdata['c_offsets'] - delta_c.T - (np.log(
                                  optaa['csig_raw_counts'].astype('float64')/
                                  optaa['cref_raw_counts']) / 0.25 )
    abs   = devdata['a_offsets'] - delta_a.T - (np.log(
                                  optaa['asig_raw_counts'].astype('float64')/
                                  optaa['aref_raw_counts']) / 0.25 )
    # populate the dictionary with the derived quantities and useful
    # information (like wavelength values).
    optaa['a_data_status'] = 'uncorrected for T,S,b'  # abs data uncorrected for T,S,scatter
    optaa['c_data_status'] = 'uncorrected for T,S'  # beam c data uncorrected for T,S
    optaa['serial_number'] = devdata['serial_number']  # scalar
    optaa['number_of_wavelengths'] = devdata['number_of_wavelengths']  # scalar
    optaa['c_wavelengths'] = devdata['c_wavelengths']
    optaa['a_wavelengths'] = devdata['a_wavelengths']
    optaa['c'] = beamc
    optaa['a'] = abs
    optaa['calibration_water_temperature'] = devdata['calibration_water_temperature']
    optaa['external_temperature'] = exttemp
    optaa['internal_temperature'] = inttemp  # needed for check values
    optaa['pressure'] = acs_pressure;
    # clean up the dictionary, removing elements not used in further processing
    del optaa['aref_raw_counts']
    del optaa['cref_raw_counts']
    del optaa['asig_raw_counts']
    del optaa['csig_raw_counts']
    del optaa['raw_external_temperature_counts']
    del optaa['raw_internal_temperature_counts']
    del optaa['pressure_counts']
    del optaa['time_msec_since_power_up']
    # may want to keep the following for future diagnostics;
    # each is only one integer per data packet.
    del optaa['a_signal_dark_counts']
    del optaa['c_signal_dark_counts']
    del optaa['a_reference_dark_counts']
    del optaa['c_reference_dark_counts']
    return optaa
def apply_TS_corrections(optaa_in, T=None, S=None):
    """
    DESCRIPTION:
    Corrects the absorption and beam attenuation data for the absorption
    of seawater as a function of ocean temperature and salinity (because
    the calibration blanking offsets are determined using pure water.)
    USAGE:
    If T or S is not supplied as a calling argument, then the following
    default values are used.
        T: temperature values recorded by the ac-s's external thermistor.
           note, this sensor's time constant > minutes, so that this should
           only be used for surface mooring data.
        S: S=33.0
    Else, each of the arguments T and S should be either:
        a scalar,
        or, 
        a 1D array or row or column vector with the same number of time points
        as 'a' and 'c'.
    Examples:
        optaa = apply_TS_corrections(optaa)
        optaa = apply_TS_corrections(optaa, None, 34.6)
        optaa = apply_TS_corrections(optaa, None, np.array([34.6]))
        optaa = apply_TS_corrections(optaa, None, S)
            These all use the external temperature values recorded by the ac-s.
        optaa = apply_TS_corrections(optaa, T)
        optaa = apply_TS_corrections(optaa, T, S)
        optaa = apply_TS_corrections(optaa, 12.0, 33.0)
    NOTES:
    Requires a dictonary containing the T,S corrections as a function of
    wavelength at 0.1 nm intervals. The dictionary created for ion_functions
    is copied here. Note that the keys are not strings but non-integer
    variables of format XXX.X, so that the wavelengths *must* be type float64
    else a keyword exception will be raised, because, for example, if a 500.1nm
    wavelength value is of type float32, it will be represented as 500.1000061
    instead of 500.1, which will result in a KeyError.
    """
    optaa = optaa_in.copy()
    dataStatus = 'TS-corrected'
    # set defaults.
    # condition non-scalar inputs to be column vectors for broadcasting.
    if T is None:
        T = optaa['external_temperature'][:, np.newaxis]
        tVarStat = ': T = ac-s'
    elif np.array(T).size != 1:
        T = T.flatten()[:, np.newaxis]
        if T.size != optaa['c'].shape[0]:
            raise Exception("Mismatch: T.size != optaa['c'].shape[0]")
        tVarStat = ': T = vector'
    else:
        tVarStat = ': T = ' + str(T)        
    if S is None:
        S = 33.0
        sVarStat = '; S = ' + str(S)
    elif np.array(S).size != 1:
        S = S.flatten()[:, np.newaxis]
        if S.size != optaa['c'].shape[0]:
            raise Exception("Mismatch: S.size != optaa['c'].shape[0]")
        sVarStat = '; S = vector'
    else:
        sVarStat = '; S = ' + str(S)        
    dataStatus = dataStatus + tVarStat + sVarStat
    # cals are done with pure water, so reference salinity is 0 and dS = S:
    dS = S - 0.0
    dT = T - optaa['calibration_water_temperature']
    # make sure that there won't be keyword problems as described in Notes.
    aWvl = np.around(optaa['a_wavelengths'].astype('float64'), decimals=1)
    cWvl = np.around(optaa['c_wavelengths'].astype('float64'), decimals=1)
    # apply the temperature and salinity corrections for each wavelength.
    # use a dictionary comprehension to read in only those values required
    # into an np array. Explicitly slice into the resultant np_tscor variable
    # to get a column vector, then transpose to a row vector, so that the 
    # wavelength dimension will correspond with that of optaa['a'] for 
    # correct broadcasting.
    np_tscor = np.array([tscor[ii] for ii in aWvl])
    optaa['a'] = optaa['a'] - dT * np_tscor[:, 0:1].T - dS * np_tscor[:, 2:].T
    np_tscor = np.array([tscor[ii] for ii in cWvl])
    optaa['c'] = optaa['c'] - dT * np_tscor[:, 0:1].T - dS * np_tscor[:, 1:2].T
    optaa['a_data_status'] = dataStatus
    optaa['c_data_status'] = dataStatus
    return optaa
def apply_scatter_correction(optaa_in, scatter_method=1):
    """
    scatter_method=1 (a715 subtract) is the most robust. 715nm was chosen
    historically because that was the reddest wavelength of an ac-9, the
    predecessor to the ac-s. A redder wavelength may be more appropriate
    when processing ac-s data.
    """
    optaa = optaa_in.copy()
    reference_wavelength = 715.0
    if scatter_method!=1:
        raise Exception('Only scatter method = 1 is coded.')
    a_interpolant = sci.interp1d(optaa['a_wavelengths'], optaa['a'])
    optaa['a_scatter_artifact'] = a_interpolant(reference_wavelength)
    optaa['a'] = optaa['a'] - optaa['a_scatter_artifact'][:, np.newaxis]
    # update
    aDataStatus = ( 'scatter_method=' + str(scatter_method) + 
        '; reference_wavelength=' + str(reference_wavelength) )
    optaa['a_data_status'] = aDataStatus
    return optaa
def inputs():
    '''
    Sets the main input arguments for the OPTAA L2 processor. File names should
    include pathnames. The key inputs are the OPTAA L1 dataset and the associated
    instrument device file. As of 2016-04-11 CTDBP data is not used. Rather, a
    default salinity value of 33 is used as is the temperature data recorded by
    the ac-s's external thermistor. Note that this sensor has an extremely long
    time constant (could be tens of minutes) and therefore its use would not be
    appropriate for profiling applications.
    '''
    # initialize argument parser
    parser = argparse.ArgumentParser(description='''Parse data files from DCL
                                     formatted daily data files''',
                                     epilog='''Parses the data file''')
    # assign arguments for the infile, outfile, and devfile.
    parser.add_argument("-i", "--infile", dest="infile", type=str, required=True)
    parser.add_argument("-d", "--devfile", dest="devfile", type=str, required=True)
    parser.add_argument("-o", "--outfile", dest="outfile", type=str, required=True)
    # parse the input arguments and create a parser object
    args = parser.parse_args()
    return args
if __name__ == '__main__':
    # usage: l2_optaa.py -i INFILE -o OUTFILE -d DEVFILE
    # load  the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    devfile = os.path.abspath(args.devfile)
    outfile = os.path.abspath(args.outfile)
    # load L1 data
    optaa0 = sio.loadmat(infile, struct_as_record=False, squeeze_me=True)
    optaa0['datafile'] = infile
    # read in the devfile info
    devdata = read_acs_devfile(args.devfile)
    # compatibility checks
    if devdata['serial_number'] != optaa0['serial_number'][0].astype(int):
        raise Exception('Serial Number mismatch between ac-s data and devfile.')
    if devdata['number_of_wavelengths'] != optaa0['number_of_wavelengths'][0]:
        raise Exception('Number of wavelengths mismatch between ac-s data and devfile.')
    optaa1 = apply_acs_devfile_to_rawdata(optaa0, devdata)
    optaa2 = apply_TS_corrections(optaa1, None, 33.0)
    optaa = apply_scatter_correction(optaa2, 1)
    # save the resulting data file
    sio.savemat(outfile, optaa)
    
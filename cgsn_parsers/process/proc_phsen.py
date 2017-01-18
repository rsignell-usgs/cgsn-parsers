#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package cgsn_parsers.process.proc_phsen
@file cgsn_parsers/process/proc_phsen.py
@author Christopher Wingard
@brief Combines the PHSEN and co-located CTDBP data (or a default value) to 
    calculate pH.
'''
import argparse
import gsw
import json
import numpy as np
import os
import scipy.interpolate as sci

from datetime import datetime, timedelta
from munch import Munch
from pytz import timezone

from ion_functions.data.ph_functions import ph_battery, ph_thermistor, ph_calc_phwater

def inputs():
    '''
    Sets the main input arguments for the PHSEN L2 processor. File names should
    include pathnames (which can be relative). The key inputs are the PHSEN L1 
    dataset and the co-located CTDBP L1 dataset. If the CTDBP data file is not
    available, a default salinity value of 33 will be used.  
    '''
    # initialize arguement parser
    parser = argparse.ArgumentParser(description='''Parse data files from DCL
                                     formatted daily data files''',
                                     epilog='''Parses the data file''')

    # assign arguements for the infile and outfile and a switch that can be
    # used, if needed, to set different options (e.g. if switch == 1, do this
    # or that).
    parser.add_argument("-i", "--infile", dest="infile", type=str, required=True)
    parser.add_argument("-o", "--outfile", dest="outfile", type=str, required=True)
    parser.add_argument("-s", "--salinity", dest="salinity", type=float, required=True, default=33.0)
    parser.add_argument("-c", "--ctdfile", dest="ctdbp", type=str, required=False, default=None)

    # parse the input arguements and create a parser object
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    # load  the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # load the parsed, json data file
    with open(infile, 'rb') as f:
        phsen = Munch(json.load(f))

    # convert the raw battery voltage and thermistor values from counts
    # to V and degC, respectively
    phsen.thermistor_start = ph_thermistor(np.array(phsen.thermistor_start)).tolist()
    therm = ph_thermistor(np.array(phsen.thermistor_end))
    phsen.thermistor_end = therm.tolist()
    phsen.voltage_battery = ph_battery(np.array(phsen.voltage_battery)).tolist()

    # compare the instrument clock to the GPS based DCL time stamp
    # --> PHSEN uses the OSX date format of seconds since 1904-01-01
    mac = datetime.strptime("01-01-1904", "%m-%d-%Y")
    offset = []
    for i in range(len(phsen.time)):
        rec = mac + timedelta(seconds=phsen.record_time[i])
        rec.replace(tzinfo=timezone('UTC'))
        dcl = datetime.utcfromtimestamp(phsen.time[i])
        offset.append((rec - dcl).total_seconds())

    phsen.time_offset = offset

    # set default calibration values (for now)
    nRec = len(phsen.thermistor_end)
    ea434 = np.ones(nRec) * 17533.
    eb434 = np.ones(nRec) * 2229.
    ea578 = np.ones(nRec) * 101.
    eb578 = np.ones(nRec) * 38502.
    slope = np.ones(nRec) * 0.9698
    offset = np.ones(nRec) * 0.2484

    # if available, load the co-located CTDBP data file corresponding to the
    # PHSEN data file
    if args.ctdfile:
        # load the ctd data
        ctdfile = os.path.abspath(args.ctdfile)
        with open(ctdfile, 'rb') as f:
            ctd = Munch(json.load(f))

        data = np.array([ctd.time, ctd.conductivity, ctd.temperature, ctd.pressure])

        # process the bursts, creating a median averaged dataset of the bursts,
        # yielding a 15 minute data record
        m = np.where(np.diff(data[0, :]) > 300)     # find beginning of each burst
        burst = []
        strt = 0
        # process the bursts ...
        for indx in m[0] + 1:
            time = np.atleast_1d(np.mean(data[0, strt:indx]))
            smpl = np.median(data[1:, strt:indx], axis=1)
            burst.append(np.hstack((time, smpl)))
            strt = indx

        # ... and the last burst
        time = np.atleast_1d(np.mean(data[0, strt:]))
        smpl = np.median(data[1:, strt:], axis=1)
        burst.append(np.hstack((time, smpl)))
        burst = np.atleast_1d(burst)

        # interpolate the ctd burst data records onto the phsen record
        interpf = sci.interp1d(burst[:, 0], burst[:, 1:], kind='linear', axis=0,
                               bounds_error=False)
        ctd = interpf(np.array(phsen.time))

        # calculate the salinity from the CTD data,
        psu = gsw.SP_from_C(ctd[:, 0], ctd[:, 1], ctd[:, 2]).reshape((ctd.shape[0], 1))
        ctd = np.hstack((ctd, psu))
    else:
        data = np.array((np.nan, np.nan, np.nan, args.salinity))
        ctd = np.tile(data, (len(phsen.time), 1))

    # calculate the pH
    refnc = np.array(phsen.reference_measurements)
    light = np.array(phsen.light_measurements)
    
    pH = ph_calc_phwater(refnc, light, therm, ea434, eb434, ea578, eb578,
                         slope, offset, ctd[:, 3])
    phsen.pH = pH.tolist()
    
    # save the resulting data to a json formatted file
    with open(outfile, 'w') as f:
        f.write(phsen.toJSON())

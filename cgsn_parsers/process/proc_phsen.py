#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@package level2.level2_phsen
@file level2/level2_phsen.py
@author Christopher Wingard
@brief Combines the PHSEN and co-located CTDBP data to calculate pH.
'''
__author__ = 'Christopher Wingard'
__license__ = 'Apache 2.0'

import argparse
import numpy as np
import os
import scipy.interpolate as sci
import scipy.io as sio

from datetime import datetime, timedelta
from pytz import timezone

from ion_functions.data.ph_functions import ph_battery, ph_thermistor, ph_calc_phwater
from ion_functions.data.ctd_functions import ctd_pracsal 


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
    parser.add_argument("-s", "--salinity", dest="salinity", type=float, required=True, default=35.0)
    parser.add_argument("-c", "--ctdfile", dest="ctdbp", type=str, required=False, default=None)

    # parse the input arguements and create a parser object
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    # load  the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for PHSEN
    phsen = sio.loadmat(infile, struct_as_record=False, squeeze_me=True)

    # clean up the dictionary, removing elements not used in further processing
    phsen.pop("dcl_date_time_string", None)
    phsen.pop("record_type", None)
    phsen.pop("record_length", None)

    # convert the raw battery voltage and thermistor values from counts
    # to V and degC, respectively
    phsen['thermistor_start'] = ph_thermistor(phsen['thermistor_start'])
    phsen['thermistor_end'] = ph_thermistor(phsen['thermistor_end'])
    phsen['voltage_battery'] = ph_battery(phsen['voltage_battery'])

    # compare the instrument clock to the GPS based DCL time stamp
    # --> PHSEN uses the OSX date format of seconds since 1904-01-01
    mac = datetime.strptime("01-01-1904", "%m-%d-%Y")
    offset = []
    for i in range(len(phsen['time'])):
        rec = mac + timedelta(seconds=phsen['record_time'][i])
        rec.replace(tzinfo=timezone('UTC'))
        dcl = datetime.utcfromtimestamp(phsen['time'][i])
        offset.append((rec - dcl).total_seconds())

    phsen['time_offset'] = offset

    # set default calibration values (for now)
    nRec = len(phsen['thermistor_end'])
    ea434 = np.ones(nRec) * 17533.
    eb434 = np.ones(nRec) * 2229.
    ea578 = np.ones(nRec) * 101.
    eb578 = np.ones(nRec) * 38502.
    slope = np.ones(nRec) * 0.9698
    offset = np.ones(nRec) * 0.2484

    # if available, load the co-located CTDBP data file corresponding to the
    # PHSEN data file.
    if args.ctdbp:
        # load the ctd data
        ctdfile = os.path.abspath(args.ctdbp)
        ctd = sio.loadmat(ctdfile, struct_as_record=False, squeeze_me=True)
        data = np.array([ctd['time'], ctd['conductivity'], ctd['temperature'], ctd['pressure']])

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
        ctd = interpf(phsen['time'])

        # calculate the salinity from the CTD data,
        psu = (ctd_pracsal(ctd[:, 0], ctd[:, 1], ctd[:, 2])).reshape((ctd.shape[0], 1))
        phsen['ctd'] = np.hstack((ctd, psu))
    else:
        data = np.array((np.nan, np.nan, np.nan, args.salinity))
        phsen['ctd'] = np.tile(data, (len(phsen['time']), 1))

    # calculate the pH
    phsen['pH'] = ph_calc_phwater(phsen['reference_measurements'],
                                  phsen['light_measurements'],
                                  phsen['thermistor_end'],
                                  ea434, eb434, ea578, eb578,
                                  slope, offset, phsen['ctd'][:, 3])

    # save the resulting data file
    sio.savemat(outfile, phsen)

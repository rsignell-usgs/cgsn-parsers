#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import cPickle as pickle


class Coefficients(object):
    '''
    A Coefficients class with two methods to load/save the serialized 
    calibration coefficients for an instrument.
    '''
    def __init__(self, coeff_file):
        '''
        Initialize the object with the path to coefficients file
        '''
        # set the infile name and path
        self.coeff_file = coeff_file

    def load_coeffs(self):
        '''
        Obtain the calibration data for this instrument from the serialized
        data object.
        '''
        # load the cPickled blanks dictionary
        with open(self.coeff_file, 'rb') as f:
            coeffs = pickle.load(f)

        self.coeffs = coeffs

    def save_coeffs(self):
        '''
        Save the calibration data for this instrument as a serialized data
        object.
        '''
        # save the cPickled blanks dictionary
        with open(self.coeff_file, 'wb') as f:
            pickle.dump(self.coeffs, f)

def inputs():
    '''
    Sets the main input arguments for the processor. At the least, the input
    and output files need to be specified. Optionally, you can specify the
    sources of the factory calibration data (either a stored serialized object,
    or a link (either file path for factory provided data file(s) or a URL to
    OOI CI maintained CSV files). File names should always include pathnames.
    Finally a simple integer switch is provided for cases where the processor
    needs to function differently depending on some set of basic conditions.
    '''
    # initialize arguement parser
    parser = argparse.ArgumentParser(description='''Process data files, converting
                                                 data from engineering units to
                                                 scientific units''',
                                     epilog='''Process the data files''')

    # assign arguements for the infile and outfile and a generi switch that can
    # be used, if needed, to set different options (e.g. if switch == 1, do
    # this or that).
    parser.add_argument("-i", "--infile", dest="infile", type=str, required=True)
    parser.add_argument("-o", "--outfile", dest="outfile", type=str, required=True)
    parser.add_argument("-c", "--coeffs", dest="coeffs", type=str, required=False)
    parser.add_argument("-f", "--factory", dest="factory", type=str, required=False)
    parser.add_argument("-s", "--switch", dest="switch", type=int, default=0)

    # parse the input arguements and create a parser object
    args = parser.parse_args()

    return args

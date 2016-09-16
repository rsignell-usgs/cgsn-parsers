#!/bin/bash
#
# Read the raw FLORT data files from the Endurance Coastal Surface Moorings and
# create parsed datasets available in Matlab formatted .mat files for further
# processing and review.
#
# C. Wingard  2016-02-19

# Parse the command line inputs
if [ $# -ne 4 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL"
    echo "number and the name of the file to process."
    echo "     example: $0 ce01issm D00001 dcl16 20150505.flort.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
FILE=`/bin/basename $4`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"
BIN="/home/ooiuser/bin/cgsn-parsers/parsers"
PYTHON="/opt/python2.7.11/bin/python"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/$DCL/flort/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/flort/${FILE%.log}.mat"

# Parse the file
if [ -e $IN ]; then
    $PYTHON $BIN/parse_flort.py -i $IN -o $OUT
fi

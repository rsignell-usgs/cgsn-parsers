#!/bin/bash
#
# Read the raw VELPT data files from the Endurance Coastal Surface Moorings and
# create parsed datasets available in Matlab formatted .mat files for further
# processing and review.
#
# C. Wingard  2016-02-23

# Parse the command line inputs
if [ $# -ne 5 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL"
    echo "number, the directory name and the name of the file to process."
    echo "     example: $0 ce01issm D00001 dcl16 velpt2 20150505.velpt2.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
VELPT=${4,,}
FILE=`/bin/basename $5`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"
BIN="/home/ooiuser/bin/cgsn-parsers/parsers"
PYTHON="/opt/python2.7.11/bin/python"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/$DCL/$VELPT/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$VELPT/${FILE%.log}.mat"

# Parse the file
if [ -e $IN ]; then
    $PYTHON $BIN/parse_velpt.py -i $IN -o $OUT
fi

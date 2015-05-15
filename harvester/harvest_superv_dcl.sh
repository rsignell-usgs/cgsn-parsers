#!/bin/bash
#
# Read the DCL Supervisor log files for the Endurance Coastal Surface Moorings
# and create parsed datasets available in Matlab formatted .MAT files for
# further processing and review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 4 ]; then
    echo "$0: required inputs are the platform and deployment names,"
    echo "the name of the DCL, and the name of the file to process."
    echo "     example: $0 ce01issm D00001 dcl11 20150505.superv.log"
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
PYTHON="/opt/python2.7.9/bin/python"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/$DCL/superv/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/superv/$DCL/${FILE%.log}.mat"

# Parse the file
[ -e $IN ] && $PYTHON $BIN/parse_superv_dcl.py -i $IN -o $OUT

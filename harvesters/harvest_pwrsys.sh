#!/bin/bash
#
# Read the raw Power System log files for the Endurance Coastal Surface
# Moorings and create parsed datasets available in Matlab formatted .MAT files
# for further processing and review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment names,"
    echo "in that order, and the name of the file to process."
    echo "     example: $0 ce01issm D00001 20150505.pwrsys.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
FILE=`/bin/basename $3`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"
BIN="/home/ooiuser/bin/cgsn-parsers/parsers"
PYTHON="/opt/python2.7.9/bin/python"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/pwrsys/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/pwrsys/${FILE%.log}.mat"

# Parse the file
[ -e $IN ] && $PYTHON $BIN/parse_pwrsys.py -i $IN -o $OUT

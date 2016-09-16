#!/bin/bash
#
# Read the CPM Supervisor log files for the Endurance Coastal Surface Moorings
# and create parsed datasets available in Matlab formatted .MAT files for
# further processing and review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 5 ]; then
    echo "$0: required inputs are the platform and deployment names,"
    echo "the name of the CPM, and the name of the file to process."
    echo "     example: $0 ce01issm D00001 cpm1 20150505.superv.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
CPM=${3,,}
BASE=$4
FILE=`/bin/basename $5`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"
BIN="/home/ooiuser/bin/cgsn-parsers/parsers"
PYTHON="/opt/python2.7.11/bin/python"

# Setup the input and output filenames as well as the absolute paths
if [ $BASE == 0 ]; then
    IN="$RAW/$PLATFORM/$DEPLOY/superv/$FILE"
else
    IN="$RAW/$PLATFORM/$DEPLOY/$CPM/superv/$FILE"
fi
OUT="$PARSED/$PLATFORM/$DEPLOY/superv/$CPM/${FILE%.log}.mat"

# Parse the file
if [ -e $IN ]; then
    $PYTHON $BIN/parse_superv_cpm.py -i $IN -o $OUT
fi

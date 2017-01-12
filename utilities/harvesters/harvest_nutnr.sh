#!/bin/bash
#
# Read the raw NUTNR data files for the Endurance Coastal Surface Moorings and
# create parsed datasets available in Matlab formatted .MAT files for further
# processing and review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 5 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL"
    echo "number, a switch to indicate what data is available (condensed or "
    echo "full) in the data files, and the name of the file to process."
    echo "     example: $0 ce01issm D00001 dcl16 0 20150505.nutnr.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
SWITCH=$4
FILE=`/bin/basename $5`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"
BIN="/home/ooiuser/bin/cgsn-parsers/parsers"
PYTHON="/opt/python2.7.11/bin/python"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/$DCL/nutnr/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/nutnr/${FILE%.log}.mat"

# Parse the file
if [ -e $IN ]; then
    $PYTHON $BIN/parse_nutnr.py -i $IN -o $OUT -s $SWITCH
fi

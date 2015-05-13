#!/bin/bash
#
# Read the raw hydrogen data files for the Endurance Coastal Surface Moorings
# and create parsed datasets available in Matlab formatted .MAT files for
# further processing and review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 5 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL"
    echo "name, the hydrogen sensor name and the name of the file to process."
    echo "     example: $0 ce01issm D00001 dcl11 hyd1 20150505.hyd1.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
HYD=${4,,}
FILE=`/bin/basename $5`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"
BIN="/home/ooiuser/bin/cgsn-parsers/parsers"
PYTHON="/opt/python2.7.9/bin/python"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/$DCL/$HYD/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$HYD/${FILE%.log}.mat"

# Parse the file
$PYTHON $BIN/parse_hydrogen.py -i $IN -o $OUT

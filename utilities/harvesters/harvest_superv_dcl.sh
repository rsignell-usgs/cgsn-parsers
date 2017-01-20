#!/bin/bash
#
# Read the DCL Supervisor log files for the Endurance Surface Moorings and
# create parsed datasets available in JSON formatted files for further
# processing and review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 4 ]; then
    echo "$0: required inputs are the platform and deployment names,"
    echo "the name of the DCL, and the name of the file to process."
    echo "     example: $0 ce02shsm D00001 dcl11 20150505.superv.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
FILE=`/bin/basename $4`

# Set the default directory paths
RAW="/webdata/cgsn/data/raw"
PARSED="/webdata/cgsn/data/proc"
BIN="/home/cgsnmo/dev/cgsn-parsers/cgsn_parsers/parsers"
PYTHON="/home/cgsnmo/anaconda3/envs/py27/bin/python"

# Setup the input and output filenames as well as the absolute paths
if [ $DCL = "dcl11" ] || [ $DCL = "dcl12" ] || [ $DCL = "dcl17" ]; then
    pltfrm="buoy"
elif [ $DCL = "dcl26" ] || [ $DCL = "dcl27" ] || [ $DCL = "dcl16" ]; then
    pltfrm="nsif"
else
    pltfrm="mfn"
fi
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/superv/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$pltfrm/superv/$DCL/${FILE%.log}.json"
if [ ! -d `/usr/bin/dirname $OUT` ]; then
    mkdir -p `/usr/bin/dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    $PYTHON -m $BIN/parse_superv_dcl -i $IN -o $OUT
fi

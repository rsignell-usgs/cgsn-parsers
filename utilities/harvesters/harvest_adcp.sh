#!/bin/bash
#
# Read the raw ADCP data files for the Endurance Surface Moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 5 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL"
    echo "number, the ADCP name and the name of the file to process."
    echo "     example: $0 ce01issm D00001 dcl35 adcpt 20150505.adcpt.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
ADCP=${4,,}
FILE=`/bin/basename $5`

# Set the default directory paths
RAW="/webdata/cgsn/data/raw"
PARSED="/webdata/cgsn/data/proc"
BIN="/home/cgsnmo/dev/cgsn-parsers/cgsn_parsers/parsers"
PYTHON="/home/cgsnmo/anaconda3/envs/py27/bin/python"

# Setup the input and output filenames as well as the absolute paths
if [ $DCL = "dcl26" ]; then
    pltfrm="nsif"
else
    pltfrm="mfn"
fi
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$ADCP/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$pltfrm/adcp/${FILE%.log}.json"
if [ ! -d `/usr/bin/dirname $OUT` ]; then
    mkdir -p `/usr/bin/dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    $PYTHON -m $BIN/parse_adcp -i $IN -o $OUT
fi

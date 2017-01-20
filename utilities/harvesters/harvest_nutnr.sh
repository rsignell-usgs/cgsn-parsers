#!/bin/bash
#
# Read the raw NUTNR data files for the Endurance Surface Moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
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
RAW="/webdata/cgsn/data/raw"
PARSED="/webdata/cgsn/data/proc"
BIN="/home/cgsnmo/dev/cgsn-parsers/cgsn_parsers/parsers"
PYTHON="/home/cgsnmo/anaconda3/envs/py27/bin/python"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/nutnr/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/nsif/nutnr/${FILE%.log}.json"
if [ ! -d `/usr/bin/dirname $OUT` ]; then
    mkdir -p `/usr/bin/dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    $PYTHON -m $BIN/parse_nutnr -i $IN -o $OUT -s $SWITCH
fi

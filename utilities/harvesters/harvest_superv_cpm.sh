#!/bin/bash
#
# Read the CPM Supervisor log files for the Endurance Coastal Surface Moorings
# and create parsed datasets available in JSON formatted files for further
# processing and review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 5 ]; then
    echo "$0: required inputs are the platform and deployment names,"
    echo "the name of the CPM, and the name of the file to process."
    echo "     example: $0 ce01issm D00001 cpm1 0 20150505.superv.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
CPM=${3,,}
BASE=$4
FILE=`/bin/basename $5`

# Set the default directory paths
RAW="/webdata/cgsn/data/raw"
PARSED="/webdata/cgsn/data/proc"
BIN="/home/cgsnmo/dev/cgsn-parsers/cgsn_parsers/parsers"
PYTHON="/home/cgsnmo/anaconda3/envs/py27/bin/python"

# Setup the input and output filenames as well as the absolute paths
if [ $CPM = "cpm1" ]; then
    pltfrm="buoy"
elif [ $CPM = "cpm2" ]; then
    pltfrm="nsif"
else
    pltfrm="mfn"
fi
if [ $BASE == 0 ]; then
    IN="$RAW/$PLATFORM/$DEPLOY/cg_data/superv/$FILE"
else
    IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$CPM/superv/$FILE"
fi
OUT="$PARSED/$PLATFORM/$DEPLOY/$pltfrm/superv/$CPM/${FILE%.log}.json"
if [ ! -d `/usr/bin/dirname $OUT` ]; then
    mkdir -p `/usr/bin/dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    $PYTHON -m $BIN/parse_superv_cpm -i $IN -o $OUT
fi

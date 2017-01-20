#!/bin/bash
#
# Read the raw VELPT data files from the Endurance Surface Moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
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
RAW="/webdata/cgsn/data/raw"
PARSED="/webdata/cgsn/data/proc"
BIN="/home/cgsnmo/dev/cgsn-parsers/cgsn_parsers/parsers"
PYTHON="/home/cgsnmo/anaconda3/envs/py27/bin/python"

# Setup the input and output filenames as well as the absolute paths
if [ $DCL = "dcl11" ] || [ $DCL = "dcl17" ]; then
    pltfrm="buoy"
else
    pltfrm="nsif"
fi
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$VELPT/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$pltfrm/velpt/${FILE%.log}.json"
if [ ! -d `/usr/bin/dirname $OUT` ]; then
    mkdir -p `/usr/bin/dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    $PYTHON -m $BIN/parse_velpt -i $IN -o $OUT
fi

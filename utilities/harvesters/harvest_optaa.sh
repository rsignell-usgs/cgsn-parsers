#!/bin/bash
#
# Read the raw OPTAA data files from the Endurance Surface Moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
#
# R. Desiderio. 2015-12-17

# Parse the command line inputs
if [ $# -ne 5 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL"
    echo "number, the OPTAA directory name and the name of the file to process."
    echo "     example: $0 ce01issm D00001 dcl16 optaa1 20150505_233000.optaa1.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
OPTAA=${4,,}
FILE=`/bin/basename $5`

# Set the default directory paths
RAW="/webdata/cgsn/data/raw"
PARSED="/webdata/cgsn/data/proc"
BIN="/home/cgsnmo/dev/cgsn-parsers/cgsn_parsers/parsers"
PYTHON="/home/cgsnmo/anaconda3/envs/py27/bin/python"

# Setup the input and output filenames as well as the absolute paths
if [ $DCL = "dcl37" ]; then
    pltfrm="mfn"
else
    pltfrm="nsif"
fi
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$OPTAA/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$pltfrm/optaa/${FILE%.log}.json"
if [ ! -d `/usr/bin/dirname $OUT` ]; then
    mkdir -p `/usr/bin/dirname $OUT`
fi

# Parse the file
if [ ! -e $OUT ]; then
    $PYTHON -m $BIN/parse_optaa -i $IN -o $OUT
fi

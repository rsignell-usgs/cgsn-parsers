#!/bin/bash
#
# Read the raw ZPLSC data files from the Endurance Surface Moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
#
# C. Wingard  2016-02-19

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment names and the"
    echo "name of the file to process."
    echo "     example: $0 ce07shsm D00001 20150505.zplsc.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
FILE=`/bin/basename $3`

# Set the default directory paths
RAW="/webdata/cgsn/data/raw"
PARSED="/webdata/cgsn/data/proc"
BIN="/home/cgsnmo/dev/cgsn-parsers/cgsn_parsers/parsers"
PYTHON="/home/cgsnmo/anaconda3/envs/py27/bin/python"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/dcl37/zplsc/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/mfn/zplsc/${FILE%.log}.json"
if [ ! -d `/usr/bin/dirname $OUT` ]; then
    mkdir -p `/usr/bin/dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    $PYTHON -m $BIN/parse_zplsc -i $IN -o $OUT
fi

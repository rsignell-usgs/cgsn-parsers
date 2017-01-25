#!/bin/bash
#
# Read the raw PCO2W data files from the Endurance Coastal Surface Moorings and
# create parsed datasets available in JSON formatted files for further
# processing and review.
#
# C. Wingard  2016-02-19

# Parse the command line inputs
if [ $# -ne 5 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL"
    echo "number, the pco2w directory name and the name of the file to process."
    echo "     example: $0 ce01issm D00001 dcl16 pco2w1 20150505.pco2w1.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
PCO2W=${4,,}
FILE=`/bin/basename $5`

# Set the default directory paths
RAW="/webdata/cgsn/data/raw"
PARSED="/webdata/cgsn/data/proc"
BIN="/home/cgsnmo/dev/cgsn-parsers/cgsn_parsers/parsers"
PYTHON="/home/cgsnmo/anaconda3/envs/py27/bin/python"

# Setup the input and output filenames as well as the absolute paths
if [ $DCL = "dcl35" ]; then
    pltfrm="mfn"
else
    pltfrm="nsif"
fi
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$PCO2W/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$pltfrm/pco2w/${FILE%.log}.json"
if [ ! -d `/usr/bin/dirname $OUT` ]; then
    mkdir -p `/usr/bin/dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    $PYTHON -m $BIN/parse_pco2w -i $IN -o $OUT
fi

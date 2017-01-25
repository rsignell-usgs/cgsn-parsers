#!/bin/bash
#
# Read the parsed PHSEN data files from the Endurance Surface Moorings and
# create processed datasets available in JSON formatted files for further
# processing and review.
#
# C. Wingard 2017-01-24

# Parse the command line inputs
if [ $# -ne 4 ]; then
    echo "$0: required inputs are the platform and deployment names, the PHSEN"
    echo "directory name, and the name of the file to process."
    echo ""
    echo "     example: $0 ce02shsm D00004 nsif/phsen 20161012.phsen.json"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
PHSEN=${3,,}
FILE=`/bin/basename $4`

# Set the default directory paths and input/output sources
BIN="/home/cgsnmo/dev/cgsn-parsers/cgsn_parsers/process"
PYTHON="/home/cgsnmo/anaconda3/envs/py27/bin/python"

PROC="/webdata/cgsn/data/proc"
IN="$PROC/$PLATFORM/$DEPLOY/$PHSEN/$FILE"
OUT="$PROC/$PLATFORM/$DEPLOY/$PHSEN/${FILE%.json}.proc.json"

# Process the file
if [ -e $IN ]; then
    $PYTHON -m $BIN/proc_phsen -i $IN -o $OUT
fi

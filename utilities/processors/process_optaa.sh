#!/bin/bash
#
# Read the parsed OPTAA data files from the Endurance Surface Moorings and create
# processed datasets available in JSON formatted files with the vendor factory
# calibration coefficients applied, rough temperature and salinity corrections
# (for now) and an initial scatter correction for further processing and review.
#
# C. Wingard 2017-01-23

# Parse the command line inputs
if [ $# -ne 5 ]; then
    echo "$0: required inputs are the platform and deployment names, the OPTAA"
    echo "directory name, the UID name of the stored factory calibration data,"
    echo "and the name of the file to process."
    echo ""
    echo "     example: $0 ce02shsm D00004 nsif/optaa OPTAAD/CGINS-OPTAAD-00208__20160921 20161012_233000.optaa.json"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
OPTAA=${3,,}
UID=${4^^}
CFILE=`/bin/basename $UID`
FILE=`/bin/basename $5`

# Set the default directory paths and input/output sources
BIN="/home/cgsnmo/dev/cgsn-parsers/cgsn_parsers/processors"
PYTHON="/home/cgsnmo/anaconda3/envs/py27/bin/python"

PROC="/webdata/cgsn/data/proc"
IN="$PROC/$PLATFORM/$DEPLOY/$OPTAA/$FILE"
OUT="$PROC/$PLATFORM/$DEPLOY/$OPTAA/${FILE%.json}.proc.json"

COEFF="$PROC/$PLATFORM/$DEPLOY/$OPTAA/$CFILE.coeff"
URL="https://github.com/ooi-integration/asset-management/raw/master/calibration/$UID.csv"

# Process the file (if it hasn't already been done)
if [ -e $IN ] && [ ! -e $OUT ]; then
    $PYTHON -m $BIN/proc_optaa -i $IN -o $OUT -c $COEFF -u $URL
fi

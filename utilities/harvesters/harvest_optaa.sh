#!/bin/bash
#
# Read the raw OPTAA data files from the Endurance Coastal Surface Moorings and
# create parsed datasets available in Matlab formatted .mat files for further
# processing and review.
#
# R. Desiderio. 2015-12-17; adapted from harvest_adcp.sh
#
# ce01issm:  nsif=dcl16 optaa1         mfn=dcl37 optaa2
# ce02shsm:  nsif=dcl27 optaa          no mfn
# ce04ossm:  nsif=dcl27 optaa          no mfn
# ce06issm:  nsif=dcl16 optaa1         mfn=dcl37 optaa2
# ce07shsm:  nsif=dcl27 optaa1         mfn=dcl37 optaa2
# ce09ossm:  nsif=dcl27 optaa1         mfn=dcl37 optaa2


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
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"
BIN="/home/ooiuser/bin/cgsn-parsers/parsers"
PYTHON="/opt/python2.7.11/bin/python"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/$DCL/$OPTAA/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$OPTAA/${FILE%.log}.mat"

# Parse the file
if [ ! -e $OUT ]; then
    $PYTHON $BIN/parse_optaa.py -i $IN -o $OUT
fi
